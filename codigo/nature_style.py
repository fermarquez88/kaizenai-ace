#!/usr/bin/env python3
"""Sistema de estilo tipo publicación (Nature-grade) para figuras Neuromentia.
Paleta validada (skill dataviz): categórica CVD-safe, divergente azul↔rojo, tinta/grilla recesivas.
Marcas finas, sin spines superior/derecho, grilla hairline en y, etiquetas directas, sin chartjunk.
Uso: from nature_style import set_style, C, forest, grouped_bars, heatmap, savefig
"""
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# --- Paleta validada (light mode) ---
C = dict(
    cat=["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7","#e34948"],
    blue="#2a78d6", red="#e34948", aqua="#1baf7a", orange="#eb6834",
    ink="#0b0b0b", ink2="#52514e", muted="#898781",
    grid="#e1e0d9", baseline="#c3c2b7", surface="#fcfcfb",
    good="#0ca30c", warn="#fab219", crit="#d03b3b",
    pos="#256abf",   # efecto protector/positivo (azul)
    neg="#d03b3b",   # efecto de riesgo/negativo (rojo)
)
SEQ_BLUE=["#cde2fb","#9ec5f4","#6da7ec","#3987e5","#256abf","#184f95","#104281"]

def set_style():
    mpl.rcParams.update({
        "font.family":"sans-serif",
        "font.sans-serif":["Helvetica Neue","Helvetica","Arial","DejaVu Sans"],
        "font.size":10, "axes.titlesize":12, "axes.labelsize":10.5,
        "axes.titleweight":"semibold", "axes.titlecolor":C["ink"],
        "axes.labelcolor":C["ink2"], "text.color":C["ink"],
        "figure.facecolor":C["surface"], "axes.facecolor":C["surface"],
        "savefig.facecolor":C["surface"],
        "axes.edgecolor":C["baseline"], "axes.linewidth":0.9,
        "axes.grid":True, "axes.axisbelow":True,
        "grid.color":C["grid"], "grid.linewidth":0.8, "grid.alpha":1.0,
        "xtick.color":C["muted"], "ytick.color":C["muted"],
        "xtick.labelcolor":C["ink2"], "ytick.labelcolor":C["ink2"],
        "xtick.major.size":0, "ytick.major.size":0,
        "legend.frameon":False, "legend.fontsize":9,
        "axes.spines.top":False, "axes.spines.right":False,
        "figure.dpi":170, "savefig.dpi":300,
    })

def _despine_left(ax):
    ax.spines["left"].set_visible(False); ax.grid(axis="y",visible=False)

def forest(ax, labels, beta, lo, hi, ref=0.0, xlabel="", diverging=True, color=None):
    """Forest plot horizontal: efecto (beta) con IC[lo,hi]. Color por dirección si diverging."""
    y=np.arange(len(labels))[::-1]
    for yi,b,l,h in zip(y,beta,lo,hi):
        col = color or (C["pos"] if b>=ref else C["neg"]) if diverging else (color or C["blue"])
        ax.plot([l,h],[yi,yi], color=col, lw=2.0, solid_capstyle="round", zorder=2)
        ax.plot(b,yi, "o", ms=7, color=col, mec=C["surface"], mew=1.5, zorder=3)
    ax.axvline(ref, color=C["baseline"], lw=1.0, ls=(0,(4,3)), zorder=1)
    ax.set_yticks(y); ax.set_yticklabels(labels, color=C["ink2"], fontsize=9.5)
    ax.set_xlabel(xlabel); ax.grid(axis="y",visible=False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y",length=0)
    ax.margins(y=0.08)
    return ax

def grouped_bars(ax, cats, values, err=None, colors=None, ylabel="", value_fmt="{:.2f}", labels_on=True):
    x=np.arange(len(cats)); w=min(0.6, 0.8)
    cols=colors or [C["blue"]]*len(cats)
    bars=ax.bar(x, values, width=w, color=cols, zorder=2,
                edgecolor=C["surface"], linewidth=1.2)
    if err is not None:
        ax.errorbar(x, values, yerr=err, fmt="none", ecolor=C["ink2"], elinewidth=1.2, capsize=3, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(cats, color=C["ink2"])
    ax.set_ylabel(ylabel); ax.grid(axis="x",visible=False)
    if labels_on:
        for xi,v in zip(x,values):
            ax.annotate(value_fmt.format(v),(xi,v),xytext=(0,4),textcoords="offset points",
                        ha="center",va="bottom",fontsize=9,color=C["ink"])
    return ax

def heatmap(ax, M, labels, title="", vmin=None, vmax=None):
    from matplotlib.colors import LinearSegmentedColormap
    cmap=LinearSegmentedColormap.from_list("seqblue",SEQ_BLUE)
    im=ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal")
    ax.set_xticks(range(len(labels))); ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8, color=C["ink2"])
    ax.set_yticklabels(labels, fontsize=8, color=C["ink2"])
    ax.grid(False); ax.set_title(title)
    for sp in ax.spines.values(): sp.set_visible(False)
    return im

def savefig(fig, path, w=None, h=None):
    if w and h: fig.set_size_inches(w,h)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=C["surface"], pil_kwargs={"quality":94})
    plt.close(fig)

def dotplot(ax, labels, values, err=None, color=None, xlabel="", sort=True, value_fmt="{:.2f}", ref=None):
    """Lollipop horizontal (magnitudes ordenadas). Alternativa a barras/forest."""
    idx=np.argsort(values) if sort else np.arange(len(values))
    labels=[labels[i] for i in idx]; values=[values[i] for i in idx]
    err=[err[i] for i in idx] if err is not None else None
    y=np.arange(len(labels)); col=color or C["blue"]
    if ref is not None: ax.axvline(ref,color=C["baseline"],lw=1.0,ls=(0,(4,3)),zorder=1)
    for yi,v in zip(y,values):
        ax.plot([ref if ref is not None else 0,v],[yi,yi],color=C["grid"],lw=1.4,zorder=1)
    if err is not None:
        ax.errorbar(values,y,xerr=err,fmt="none",ecolor=C["ink2"],elinewidth=1.1,capsize=2.5,zorder=2)
    ax.plot(values,y,"o",ms=8,color=col,mec=C["surface"],mew=1.5,zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=9.5,color=C["ink2"])
    ax.set_xlabel(xlabel); ax.grid(axis="y",visible=False); ax.spines["left"].set_visible(False); ax.tick_params(axis="y",length=0)
    for yi,v in zip(y,values): ax.annotate(value_fmt.format(v),(v,yi),xytext=(8,0),textcoords="offset points",va="center",fontsize=9,color=C["ink"])
    ax.margins(y=0.08); return ax

def dumbbell(ax, labels, v1, v2, lab1="", lab2="", xlabel="", c1=None, c2=None, fmt="{:.2f}"):
    """Dos estados por fila conectados (comparación de 2 grupos/momentos)."""
    y=np.arange(len(labels))[::-1]; c1=c1 or C["muted"]; c2=c2 or C["blue"]
    for yi,a,b in zip(y,v1,v2):
        ax.plot([a,b],[yi,yi],color=C["grid"],lw=3,zorder=1,solid_capstyle="round")
        ax.plot(a,yi,"o",ms=8,color=c1,mec=C["surface"],mew=1.5,zorder=2)
        ax.plot(b,yi,"o",ms=8,color=c2,mec=C["surface"],mew=1.5,zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=9.5,color=C["ink2"])
    ax.set_xlabel(xlabel); ax.grid(axis="y",visible=False); ax.spines["left"].set_visible(False); ax.tick_params(axis="y",length=0)
    from matplotlib.lines import Line2D
    ax.legend([Line2D([0],[0],marker="o",color="w",markerfacecolor=c1,ms=8),
               Line2D([0],[0],marker="o",color="w",markerfacecolor=c2,ms=8)],[lab1,lab2],loc="best")
    ax.margins(y=0.1); return ax

def scatter_fit(ax, x, y, xs=None, yhat=None, lo=None, hi=None, xlabel="", ylabel="", identity=False, pt_alpha=0.14):
    """Dispersión + línea ajustada con banda IC (relaciones continuas, calibración, spline)."""
    ax.scatter(x,y,s=9,alpha=pt_alpha,color=C["muted"],edgecolors="none",zorder=1)
    if identity:
        lim=[min(min(x),min(y)),max(max(x),max(y))]; ax.plot(lim,lim,color=C["baseline"],lw=1.0,ls=(0,(4,3)),zorder=2)
    if xs is not None and yhat is not None:
        if lo is not None and hi is not None:
            ax.fill_between(xs,lo,hi,color=C["blue"],alpha=0.14,lw=0,zorder=2)
        ax.plot(xs,yhat,color=C["blue"],lw=2.4,zorder=3)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); return ax

def waterfall(ax, labels, contribs, total_label="Total", ylabel="", fmt="{:+.2f}"):
    """Descomposición (p.ej. Oaxaca): contribuciones apiladas + total."""
    cum=0; x=np.arange(len(contribs)+1)
    for i,(lab,c) in enumerate(zip(labels,contribs)):
        col=C["pos"] if c>=0 else C["neg"]
        ax.bar(i,c,bottom=cum,width=0.62,color=col,edgecolor=C["surface"],linewidth=1.2,zorder=2)
        ax.annotate(fmt.format(c),(i,cum+c),xytext=(0,4 if c>=0 else -12),textcoords="offset points",ha="center",fontsize=8.5,color=C["ink"])
        cum+=c
    ax.bar(len(contribs),cum,width=0.62,color=C["ink2"],edgecolor=C["surface"],linewidth=1.2,zorder=2)
    ax.annotate(fmt.format(cum),(len(contribs),cum),xytext=(0,4),textcoords="offset points",ha="center",fontsize=8.5,color=C["ink"])
    ax.set_xticks(x); ax.set_xticklabels(list(labels)+[total_label],rotation=30,ha="right",fontsize=9,color=C["ink2"])
    ax.set_ylabel(ylabel); ax.axhline(0,color=C["baseline"],lw=1.0); ax.grid(axis="x",visible=False); return ax

if __name__=="__main__":
    set_style()
    fig,ax=plt.subplots(figsize=(6,3.2))
    forest(ax,["A","B","C"],[0.13,-0.21,0.07],[0.07,-0.28,-0.01],[0.19,-0.14,0.15],xlabel="β [IC95%]")
    ax.set_title("Test forest"); savefig(fig,"/tmp/_test_forest.jpg")
    print("estilo OK; helpers: forest,grouped_bars,heatmap,dotplot,dumbbell,scatter_fit,waterfall")
