#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Figuras del reencuadre: la falsación del escalón es el resultado principal."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL, savefig  # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
set_style()
OUT = NM / "posters_CAN2026/plataforma/12b_educacion_2cohortes"

com = pd.read_csv(NM / "analisis/comunitaria_armonizada.csv")
cli = (pd.read_csv(NM / "analisis/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
       .dropna(subset=["ACE", "edu", "Edad", "Sexo"]))
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
GR = [("Comunitaria", com, PAL["blue"]), ("Clínica", cli, PAL["red"])]

# ============================================ FIGURA 1 — la falsación
fig, ax = plt.subplots(1, 3, figsize=(15.6, 4.7))

# (a) positividad de la regla vigente año por año  <-- la figura del trabajo
for lab, d, col in GR:
    d = d.copy(); d["P2"] = np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68)
    t = d[d.edu.between(1, 18)].groupby("edu").P2.agg(["size", "mean"])
    t = t[t["size"] >= 10]
    x, y = t.index.values, 100 * t["mean"].values
    pre, post = x < 12, x >= 12
    ax[0].plot(x[pre], y[pre], "o-", color=col, lw=2.2, ms=5, label=f"{lab} (n={len(d)})")
    ax[0].plot(x[post], y[post], "o-", color=col, lw=2.2, ms=5)
    ax[0].plot([x[pre][-1], x[post][0]], [y[pre][-1], y[post][0]], ":", color=col, lw=1.4, alpha=0.7)
ax[0].axvline(11.5, color=PAL["ink"], lw=1.6, ls="--")
ax[0].text(11.35, 96, "cambia el corte\nde 68 a 86", ha="right", va="top", fontsize=8.6,
           color=PAL["ink"], fontweight="semibold", linespacing=1.3)
ax[0].annotate("", xy=(12, 52), xytext=(11, 6),
               arrowprops=dict(arrowstyle="->", color=PAL["crit"], lw=2))
ax[0].text(9.6, 32, "8,4×", fontsize=13, color=PAL["crit"], fontweight="bold", ha="right")
ax[0].set_xlabel("Años de educación"); ax[0].set_ylabel("% por debajo del corte vigente")
ax[0].set_title("a  El salto está en la regla, no en el rendimiento", loc="left", fontsize=11)
ax[0].legend(loc="upper right", fontsize=8.6); ax[0].set_ylim(-4, 104)

# (b) el rendimiento observado es continuo
for lab, d, col in GR:
    lo, hi = np.percentile(d.edu, [3, 97])
    g = np.linspace(max(1, lo), min(20, hi), 60)
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    ax[1].plot(g, m.predict(pd.DataFrame({"edu": g, "Edad": d.Edad.mean(), "Sexo": "Mujer"})),
               color=col, lw=2.4, label=f"{lab}: ACE-III esperado")
    med = d[d.edu.between(1, 18)].groupby("edu").agg(n=("ACE", "size"), m=("ACE", "median"))
    med = med[med.n >= 10]
    ax[1].plot(med.index, med.m, "o", color=col, ms=4.5, alpha=0.55)
ax[1].axvline(11.5, color=PAL["ink"], lw=1.6, ls="--")
ax[1].set_xlabel("Años de educación"); ax[1].set_ylabel("ACE-III total")
ax[1].set_title("b  Sin discontinuidad en el rendimiento\n(puntos: mediana observada por año)",
                loc="left", fontsize=11)
ax[1].legend(loc="lower right", fontsize=8.4)

# (c) el escalón estimado contra el que impone la regla
labs = ["Comunitaria\n(n=762)", "Clínica\n(n=2112)"]
est = [0.55, 0.13]; lo = [-2.09, -2.56]; hi = [3.20, 2.83]
cols = [PAL["blue"], PAL["red"]]
ys = np.arange(len(labs))[::-1]
for y, e, l, h, c in zip(ys, est, lo, hi, cols):
    ax[2].plot([l, h], [y, y], color=c, lw=3.2, solid_capstyle="round")
    ax[2].plot(e, y, "o", color=c, ms=9, mec="white", mew=1.4)
    ax[2].text(h + 0.7, y, f"{e:+.2f}\n[{l:+.2f}; {h:+.2f}]", va="center", fontsize=8.4,
               color=PAL["ink2"], linespacing=1.3)
ax[2].axvline(0, color=PAL["baseline"], lw=1.1, ls="--")
ax[2].axvline(18, color=PAL["crit"], lw=2.4)
ax[2].text(17.4, 1.42, "salto que\nimpone la regla:\n18 puntos", ha="right", va="top",
           fontsize=9, color=PAL["crit"], fontweight="semibold", linespacing=1.35)
ax[2].set_yticks(ys); ax[2].set_yticklabels(labs, fontsize=9.5)
ax[2].set_xlim(-4.5, 20.5); ax[2].set_ylim(-0.6, 1.75)
ax[2].set_xlabel("Escalón en 12 años de educación (puntos ACE-III, IC95%)")
ax[2].set_title("c  La discontinuidad estimada excluye la regla\npor un factor de seis",
                loc="left", fontsize=11)
ax[2].grid(axis="y", visible=False)
fig.tight_layout(); savefig(fig, str(OUT / "Figura1_falsacion_del_escalon.jpg")); plt.close(fig)

# ============================================ FIGURA 2 — consecuencia y forma
fig, ax = plt.subplots(1, 2, figsize=(11.8, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})

TR = ["<7", "7–11", "≥12"]
dat = {"Comunitaria · escalón vigente": ([55.6, 20.8, 40.6], PAL["ink"], "//"),
       "Comunitaria · corte continuo": ([41.2, 38.4, 34.7], PAL["blue"], None),
       "Clínica · escalón vigente": ([74.5, 55.3, 61.9], PAL["muted"], "//"),
       "Clínica · corte continuo": ([54.3, 61.9, 61.6], PAL["red"], None)}
w = 0.2
for j, (lab, (v, col, hatch)) in enumerate(dat.items()):
    ax[0].bar(np.arange(3) + (j - 1.5) * w, v, width=w, color=col, alpha=0.9,
              hatch=hatch, edgecolor="white", lw=0.6, label=lab)
ax[0].set_xticks(np.arange(3)); ax[0].set_xticklabels([f"{t} años" for t in TR])
ax[0].set_xlabel("Años de educación"); ax[0].set_ylabel("% marcado")
ax[0].set_title("a  A igual carga de derivación, la regla reparte\nde forma cinco veces más desigual",
                loc="left", fontsize=10.5)
ax[0].legend(loc="upper right", fontsize=7.6); ax[0].set_ylim(0, 92)
ax[0].text(0.02, 0.02, "rango entre tramos:  regla 34,8 y 19,2 pp   ·   continuo 6,6 y 7,5 pp",
           transform=ax[0].transAxes, fontsize=8, color=PAL["muted"])

for lab, d, col in GR:
    lo, hi = np.percentile(d.edu, [5, 95]); g = np.linspace(max(1, lo), min(20, hi), 60)
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    nm = list(m.params.index); i1, i2 = nm.index("edu"), nm.index("I(edu ** 2)")
    V = np.asarray(m.cov_params()); b1, b2 = m.params.iloc[i1], m.params.iloc[i2]
    est = b1 + 2 * b2 * g
    se = np.array([np.sqrt(np.r_[[1.0 if k == i1 else (2 * e if k == i2 else 0.0)
                                  for k in range(len(nm))]] @ V @
                           np.r_[[1.0 if k == i1 else (2 * e if k == i2 else 0.0)
                                  for k in range(len(nm))]]) for e in g])
    ci = m.conf_int().loc["I(edu ** 2)"]
    ax[1].fill_between(g, est - 1.96 * se, est + 1.96 * se, color=col, alpha=0.13, lw=0)
    ax[1].plot(g, est, color=col, lw=2.3,
               label=f"{lab}\nb₂={m.params.iloc[i2]:.3f} [{ci[0]:.3f}; {ci[1]:.3f}]")
ax[1].axhline(0, color=PAL["baseline"], lw=1, ls=":")
ax[1].set_xlabel("Años de educación"); ax[1].set_ylabel("Pendiente marginal\n(puntos ACE-III por año)")
ax[1].set_title("b  Misma curvatura en dos cohortes de\nselección opuesta (p=0,92)", loc="left", fontsize=10.5)
ax[1].legend(loc="upper right", fontsize=8, labelspacing=0.9)
fig.tight_layout(); savefig(fig, str(OUT / "Figura2_consecuencia_y_forma.jpg")); plt.close(fig)
print("figuras ->", OUT)
