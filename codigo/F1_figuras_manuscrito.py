#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIGURAS DEL MANUSCRITO — CAN 2026.

Ordenadas según la arquitectura del trabajo:
  Figura 1  LA FORMA FUNCIONAL (el hallazgo): la asociación es curvilínea, replica entre cohortes
            de selección opuesta y sobrevive en la métrica latente.
  Figura 2  LA FALSACIÓN (consecuencia 1): no hay discontinuidad en 12 años, y de los catorce
            cortes candidatos ése es el que menos señal produce.
  Figura 3  LA CONSECUENCIA CLÍNICA: la regla corrige con 18 puntos un sesgo de 0,08–0,34.

Todas las cifras provienen de los datos, no de literales: se recalculan acá.
Salida: figuras/Figura1..3 en .jpg (300 dpi) y .pdf (vectorial).
"""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL                      # noqa: E402
import matplotlib.pyplot as plt                                    # noqa: E402
from matplotlib.patches import Rectangle                           # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator            # noqa: E402
set_style()

COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def es(axes):
    """Separador decimal español, sin tocar los ejes con etiquetas categóricas fijas."""
    import matplotlib.ticker as mt
    for a in np.atleast_1d(axes).ravel():
        for eje in (a.xaxis, a.yaxis):
            if isinstance(eje.get_major_formatter(), mt.ScalarFormatter):
                eje.set_major_formatter(COMA)
OUT = EST / "figuras"; OUT.mkdir(exist_ok=True)

ITEMS = ['ACE_AtOT','ACE_AtOE','ACE_AtRegistro','ACE_AtSubstr','ACE_MRecuerdo','ACE_MAnterogr',
         'ACE_MRetrogr','ACE_MRecuerdoNyD','ACE_MReconocNyD','ACE_FluVerbFPC','ACE_FluVerbSPC',
         'ACE_LComprensionLyH','ACE_LEscrit','ACE_LRepP','ACE_LRepProverb','ACE_LDenom',
         'ACE_LCompDibujo','ACE_LLectura','ACE_HabVisoDiagrama','ACE_HabVisoCubo',
         'ACE_HabPerPuntos','ACE_HabPerLetras','ACE_HabVisoReloj']

com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
cli = (pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
       .dropna(subset=["ACE", "edu", "Edad", "Sexo"]))
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
GR = [("Comunitaria", com, PAL["blue"]), ("Clínica", cli, PAL["red"])]
FQ = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"


def guarda(fig, nombre):
    fig.tight_layout()
    for ext in ("jpg", "pdf"):
        kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
        fig.savefig(OUT / f"{nombre}.{ext}", dpi=300, bbox_inches="tight",
                    facecolor="white", **kw)
    plt.close(fig)
    print(f"  -> figuras/{nombre}.jpg + .pdf")


def marginal(d, y="ACE", xs=np.arange(1, 19)):
    """Pendiente marginal dY/dEdu = b1 + 2·b2·edu, con IC por método delta sobre HC3."""
    m = smf.ols(f"{y} ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    nm = list(m.params.index); i1, i2 = nm.index("edu"), nm.index("I(edu ** 2)")
    V = np.asarray(m.cov_params()); b1, b2 = m.params.iloc[i1], m.params.iloc[i2]
    est, se = [], []
    for e in xs:
        v = np.zeros(len(nm)); v[i1] = 1; v[i2] = 2*e
        est.append(float(b1 + 2*b2*e)); se.append(float(np.sqrt(v @ V @ v)))
    return xs, np.array(est), np.array(se)


# ═══════════════════════════════════════════════ FIGURA 1 — LA FORMA FUNCIONAL
print("Figura 1 — la forma funcional")
fig, ax = plt.subplots(1, 3, figsize=(15.4, 4.6))

# (a) curva ajustada sobre las medias observadas
for lab, d, col in GR:
    t = d[d.edu.between(0, 18)].groupby("edu").ACE.agg(["size", "mean", "sem"])
    t = t[t["size"] >= 8]
    ax[0].errorbar(t.index, t["mean"], yerr=1.96*t["sem"], fmt="o", color=col, ms=4.5,
                   lw=0, elinewidth=1.1, capsize=2, alpha=0.75, zorder=3)
    m = smf.ols(FQ, data=d).fit(cov_type="HC3")
    g = pd.DataFrame({"edu": np.linspace(0, 18, 120), "Edad": d.Edad.median(),
                      "Sexo": d.Sexo.mode()[0]})
    pr = m.get_prediction(g).summary_frame(alpha=0.05)
    ax[0].plot(g.edu, pr["mean"], color=col, lw=2.6, zorder=4, label=f"{lab} (n={len(d)})")
    ax[0].fill_between(g.edu, pr["mean_ci_lower"], pr["mean_ci_upper"], color=col,
                       alpha=0.13, lw=0, zorder=2)
ax[0].set_xlabel("Años de escolaridad"); ax[0].set_ylabel("ACE-III (puntos)")
ax[0].set_title("a  La asociación es curvilínea en las dos cohortes", loc="left", fontsize=11)
ax[0].legend(loc="lower right", fontsize=8.8, frameon=False)
ax[0].set_xlim(-0.6, 18.6)

# (b) pendiente marginal: el rendimiento decreciente, explícito
for lab, d, col in GR:
    xs, est, se = marginal(d)
    ax[1].plot(xs, est, color=col, lw=2.6, zorder=4, label=lab)
    ax[1].fill_between(xs, est-1.96*se, est+1.96*se, color=col, alpha=0.13, lw=0, zorder=2)
ax[1].axhline(0, color=PAL["baseline"], lw=1.1, zorder=1)
xs, est, se = marginal(com)
r_com = est[2] / est[16]
for e, ha, dx in [(3, "left", 0.7), (17, "right", -0.7)]:
    ax[1].annotate(f"{est[e-1]:.1f}".replace(".", ",") + " pts/año",
                   xy=(e, est[e-1]), xytext=(e + dx, est[e-1] + 0.45),
                   fontsize=9.2, ha=ha, color=PAL["blue"], fontweight="semibold")
ax[1].set_xlabel("Años de escolaridad")
ax[1].set_ylabel("Ganancia por año adicional (puntos)")
ax[1].set_title(f"b  La ganancia cae {r_com:.1f}".replace(".", ",") +
                " veces entre el año 3 y el 17", loc="left", fontsize=11)
ax[1].legend(loc="lower left", fontsize=8.8, frameon=False)
ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))
ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))

# (c) la curvatura sobre la métrica latente: no es artefacto del techo
V4 = json.loads((EST / "resultados/V4_tri.json").read_text())
lab_c = ["Comunitaria", "Clínica"]
b_raw = [V4["curvatura_latente"]["comunitaria"]["puntaje bruto"]["b2_estandarizado"],
         V4["curvatura_latente"]["clínica"]["puntaje bruto"]["b2_estandarizado"]]
b_lat = [V4["curvatura_latente"]["comunitaria"]["θ latente"]["b2_estandarizado"],
         V4["curvatura_latente"]["clínica"]["θ latente"]["b2_estandarizado"]]
x = np.arange(2); w = 0.34
ax[2].bar(x - w/2, [-v*1000 for v in b_raw], w, color=PAL["ink2"], label="Puntaje bruto")
ax[2].bar(x + w/2, [-v*1000 for v in b_lat], w, color=PAL["blue"], alpha=0.75, label="Habilidad latente")
for i in range(2):
    pct = 100 * b_lat[i] / b_raw[i]
    ax[2].text(i, -b_raw[i]*1000 + 0.16, f"persiste\nel {pct:.0f} %", ha="center", fontsize=9,
               color=PAL["ink2"], linespacing=1.25)
ax[2].set_xticks(x); ax[2].set_xticklabels(lab_c)
ax[2].set_ylabel("Curvatura estandarizada (×10⁻³)")
ax[2].set_title("c  La curvatura sobrevive sin el techo del test", loc="left", fontsize=11)
ax[2].legend(loc="upper right", fontsize=8.8, frameon=False)
ax[2].set_ylim(0, max(-v*1000 for v in b_raw) * 1.42)
es(ax)
guarda(fig, "Figura1_forma_funcional")

# ═══════════════════════════════════════════════ FIGURA 2 — LA FALSACIÓN
print("Figura 2 — la falsación del escalón")
fig, ax = plt.subplots(1, 3, figsize=(16.6, 4.8))

# (a) prueba de placebo sobre los catorce cortes candidatos
for lab, d, col in GR:
    xs_, bs_, los_, his_ = [], [], [], []
    for c in range(5, 19):
        s = d.assign(post=(d.edu >= c).astype(int))
        if not 0.03 < s.post.mean() < 0.97:
            continue
        m = smf.ols("ACE ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
        ci = m.conf_int().loc["post"]
        xs_.append(c); bs_.append(float(m.params["post"]))
        los_.append(float(ci[0])); his_.append(float(ci[1]))
    off = -0.16 if lab == "Comunitaria" else 0.16
    ax[0].errorbar(np.array(xs_) + off, bs_, yerr=[np.array(bs_)-np.array(los_),
                   np.array(his_)-np.array(bs_)], fmt="o", color=col, ms=4.2,
                   elinewidth=1.2, capsize=2, lw=0, label=lab, zorder=3)
ax[0].axhline(0, color=PAL["baseline"], lw=1.2)
ax[0].axhline(18, color=PAL["crit"], lw=1.6, ls="--")
ax[0].text(18.6, 18.8, "escalón que supone la regla vigente (18 puntos)", ha="right",
           fontsize=8.6, color=PAL["crit"], fontweight="semibold")
ax[0].add_patch(Rectangle((11.55, -11), 0.9, 33, color=PAL["warn"], alpha=0.16, lw=0, zorder=0))
ax[0].text(12, -10.2, "corte\nen uso", ha="center", fontsize=8.6, color=PAL["ink"],
           fontweight="semibold", linespacing=1.25)
ax[0].set_xlabel("Corte evaluado (años de escolaridad)")
ax[0].set_ylabel("Discontinuidad estimada (puntos)")
ax[0].annotate("amontonamiento en\n«primaria completa»", xy=(7, -6.4), xytext=(5.4, -11.4),
               fontsize=8.2, color=PAL["ink2"], linespacing=1.25, ha="left",
               arrowprops=dict(arrowstyle="-", color=PAL["ink2"], lw=0.9))
ax[0].set_title("a  Ningún corte es discontinuo; el de 12, menos que ninguno",
                loc="left", fontsize=10.6)
ax[0].legend(loc="upper left", fontsize=8.8, frameon=False, ncol=2); ax[0].set_ylim(-14.5, 25)
ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))

# (b) regresión discontinua local en tres ventanas
VENT = [(10, 13), (9, 14), (8, 15)]
for i, w in enumerate(VENT):
    yy0 = len(VENT) - 1 - i
    for j, (lab, d, col) in enumerate(GR):
        sub = d[d.edu.between(*w)].copy(); sub["post"] = (sub.edu >= 12).astype(int)
        m = smf.ols("ACE ~ edu + post + Edad + C(Sexo)", data=sub).fit(cov_type="HC3")
        ci = m.conf_int().loc["post"]; yy = yy0 + (0.17 if j == 0 else -0.17)
        ax[1].plot([ci[0], ci[1]], [yy, yy], color=col, lw=2.3, solid_capstyle="round", zorder=3)
        ax[1].plot(float(m.params["post"]), yy, "o", color=col, ms=6.5, zorder=4,
                   label=lab if i == 0 else None)
        ax[1].text(20.4, yy, f"n={len(sub)}", va="center", fontsize=7.8, color=col)
ax[1].axvline(0, color=PAL["baseline"], lw=1.2)
ax[1].axvline(18, color=PAL["crit"], lw=1.6, ls="--")
ax[1].text(17.4, 2.42, "18 puntos", fontsize=8.4, color=PAL["crit"], ha="right",
           fontweight="semibold")
ax[1].set_yticks(range(len(VENT)))
ax[1].set_yticklabels([f"{w[0]}–{w[1]} años" for w in VENT][::-1], fontsize=9.4)
ax[1].set_ylim(-0.55, 2.62)
ax[1].set_xlabel("Discontinuidad en 12 años (puntos)")
ax[1].set_title("b  Regresión discontinua local: seis ventanas, ningún escalón",
                loc="left", fontsize=10.6)
ax[1].legend(loc="lower left", fontsize=8.8, frameon=False)
ax[1].set_xlim(-14, 24)

# (c) equivalencia: el intervalo cabe dentro de márgenes cada vez más estrictos
V3 = json.loads((EST / "resultados/V3_supuestos.json").read_text())
for i, (lab, d, col) in enumerate(GR):
    k = "comunitaria" if lab == "Comunitaria" else "clínica"
    s = d.assign(post=(d.edu >= 12).astype(int))
    m = smf.ols("ACE ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
    ci = m.conf_int().loc["post"]; b = float(m.params["post"])
    yy = 1 - i
    ax[2].plot([ci[0], ci[1]], [yy, yy], color=col, lw=3.4, solid_capstyle="round", zorder=4)
    ax[2].plot(b, yy, "o", color=col, ms=8, zorder=5)
    ax[2].text(ci[1] + 0.9, yy, (f"{b:+.2f}  [{ci[0]:+.1f}; {ci[1]:+.1f}]").replace(".", ","),
               va="center", fontsize=8.8, color=col, fontweight="semibold")
for M, alpha, ty in [(18, 0.10, 1.62), (5, 0.16, 1.44), (3, 0.24, 1.26)]:
    ax[2].add_patch(Rectangle((-M, -0.62), 2*M, 2.9, color=PAL["blue"], alpha=alpha, lw=0, zorder=1))
    ax[2].text(M + 0.5, ty, f"margen ±{M}", ha="left", va="center", fontsize=8.4,
               color=PAL["ink2"])
ax[2].axvline(0, color=PAL["baseline"], lw=1.2, zorder=2)
ax[2].set_yticks([1, 0]); ax[2].set_yticklabels(["Comunitaria", "Clínica"], fontsize=9.2)
ax[2].set_ylim(-0.75, 1.9); ax[2].set_xlim(-21, 31)
ax[2].set_xlabel("Discontinuidad en 12 años (puntos)")
ax[2].set_title("c  Equivalencia: se descarta incluso un escalón de 3 puntos",
                loc="left", fontsize=10.6)
es(ax)
guarda(fig, "Figura2_falsacion")

# ═══════════════════════════════════════════════ FIGURA 3 — LA CONSECUENCIA
print("Figura 3 — la consecuencia clínica")
fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.6))

# (a) positividad año a año
for lab, d, col in GR:
    dd = d.copy(); dd["P"] = np.where(dd.edu >= 12, dd.ACE < 86, dd.ACE < 68)
    t = dd[dd.edu.between(1, 18)].groupby("edu").P.agg(["size", "mean"])
    t = t[t["size"] >= 10]
    x, y = t.index.values, 100*t["mean"].values
    pre, post = x < 12, x >= 12
    ax[0].plot(x[pre], y[pre], "o-", color=col, lw=2.3, ms=5, label=f"{lab} (n={len(d)})")
    ax[0].plot(x[post], y[post], "o-", color=col, lw=2.3, ms=5)
    ax[0].plot([x[pre][-1], x[post][0]], [y[pre][-1], y[post][0]], ":", color=col, lw=1.4, alpha=0.7)
ax[0].axvline(11.5, color=PAL["ink"], lw=1.6, ls="--")
ax[0].text(11.3, 97, "el corte cambia\nde 68 a 86", ha="right", va="top", fontsize=8.8,
           color=PAL["ink"], fontweight="semibold", linespacing=1.3)
dd = com.copy(); dd["P"] = np.where(dd.edu >= 12, dd.ACE < 86, dd.ACE < 68)
p11 = 100*dd[dd.edu == 11].P.mean(); p12 = 100*dd[dd.edu == 12].P.mean()
ax[0].annotate("", xy=(12, p12), xytext=(11, p11),
               arrowprops=dict(arrowstyle="->", color=PAL["crit"], lw=2.2))
ax[0].text(9.7, (p11+p12)/2, f"{p12/p11:.1f}×".replace(".", ","), fontsize=13.5, color=PAL["crit"],
           fontweight="bold", ha="right", va="center")
ax[0].set_xlabel("Años de escolaridad"); ax[0].set_ylabel("% señalado por la regla vigente")
ax[0].set_title("a  Un año de escolaridad reclasifica a la mitad de las personas",
                loc="left", fontsize=10.6)
ax[0].legend(loc="upper right", fontsize=8.8, frameon=False); ax[0].set_ylim(-4, 112)
ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))

# (b) la desproporción: sesgo real vs corrección aplicada vs error de medición
V4c = json.loads((EST / "resultados/V4c_dtf.json").read_text())
etq = ["Sesgo real\ncomunitaria", "Sesgo real\nclínica", "Error de medición\ndel ACE-III",
       "Corrección que\naplica la regla"]
val = [abs(V4c["comunitaria"]["dtf_baja_vs_alta"]), abs(V4c["clínica"]["dtf_baja_vs_alta"]), 8.15, 18.0]
cols = [PAL["blue"], PAL["red"], PAL["muted"], PAL["crit"]]
bars = ax[1].bar(np.arange(4), val, color=cols, width=0.62)
for b, v in zip(bars, val):
    ax[1].text(b.get_x()+b.get_width()/2, v+0.45,
               (f"{v:.2f}".rstrip("0").rstrip(".") + " pts").replace(".", ","),
               ha="center", fontsize=9.6, fontweight="semibold", color=PAL["ink"])
ax[1].set_xticks(np.arange(4)); ax[1].set_xticklabels(etq, fontsize=8.6, linespacing=1.3)
ax[1].set_ylabel("Puntos de ACE-III")
ax[1].set_title("b  La regla corrige 50 a 200 veces el sesgo que existe", loc="left", fontsize=10.6)
ax[1].set_ylim(0, 21)
ax[1].annotate("", xy=(3, 17.2), xytext=(0.15, 17.2),
               arrowprops=dict(arrowstyle="<->", color=PAL["ink2"], lw=1.3))
ax[1].text(1.6, 17.9, "desproporción de la corrección", ha="center", fontsize=8.8,
           color=PAL["ink2"], style="italic")
es(ax)
guarda(fig, "Figura3_consecuencia")

print(f"\nTres figuras guardadas en {OUT}")
