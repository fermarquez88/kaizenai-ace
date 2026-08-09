#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
F11 — Reconstruye de forma REPRODUCIBLE las dos figuras del manuscrito que no tenían script.

Motivo. La auditoría del repositorio encontró que `Figura4_desproporcion_y_discriminacion.jpg` y
`Figura3_equidad.jpg` existían como archivos pero ningún script del repositorio las generaba: se
habían producido en una sesión interactiva y quedaron huérfanas. En un trabajo que declara publicar
el código completo eso es un defecto de reproducibilidad, no un detalle de orden.

Aquí se regeneran ambas desde `resultados/CIFRAS_MAESTRAS.json` y los JSON de bloque, sin tocar los
datos individuales, y se incorpora el panel que faltaba:

  Figura 4 — Qué corrige la regla, qué no puede corregir y por qué la escala engaña
     (a) escala del sesgo de medición frente al error del instrumento y a la corrección aplicada
     (b) área bajo la curva por tramo educativo                                    [V7]
     (c) NUEVO — la dispersión se estrecha en el puntaje pero no en la habilidad   [V26 · V26b]

  Figura 5 — Reparto de los señalamientos por tramo, a igual tasa de positividad   [V13]

El panel (c) es la corrección de fondo del manuscrito: el estrechamiento de la dispersión que se
presentaba como propiedad de la distribución de habilidad es, en su mayor parte, un efecto de la
no linealidad de la escala del puntaje bruto cerca del techo. Las barras se normalizan al tramo de
menor escolaridad para que las dos métricas —puntos de ACE-III y unidades de θ, que no comparten
unidad— sean comparables en un único eje, en vez de en dos ejes gemelos que engañan a la vista.

Salida: figuras/Figura4_instrumento.{jpg,pdf} + figuras/Figura5_equidad.{jpg,pdf}
"""
import json, sys
from pathlib import Path
import numpy as np

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL                 # noqa: E402
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.ticker import FuncFormatter                  # noqa: E402

set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
FIG = EST / "figuras"
L = lambda n: json.loads((EST / "resultados" / n).read_text())
M = L("CIFRAS_MAESTRAS.json")
v7, v13 = L("V7_estandar_referencia.json"), L("V13_equidad_corregida.json")
BANDAS = ["<7", "7-11", ">=12"]
ETI = ["menos de 7", "7 a 11", "12 o más"]


def guarda(fig, nombre):
    for ext in ("jpg", "pdf"):
        fig.savefig(FIG / f"{nombre}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    print(f"  -> figuras/{nombre}.jpg + .pdf")


# ═══════════════════════════════════════════════════ FIGURA 4
fig, ax = plt.subplots(1, 3, figsize=(12.6, 3.7))

# ── (a) escala del sesgo
dtf = M["psicometria"]["dtf_total"]
eem = M["test_retest"]["eem_extrapolado"]
vals = [abs(dtf["comunitaria"]["dtf_baja_vs_alta"]), abs(dtf["clinica"]["dtf_baja_vs_alta"]),
        eem, 18.0]
etiq = ["Sesgo medido\ncomunitaria", "Sesgo medido\nclínica",
        "Error estándar\nde medición", "Corrección que\naplica la regla"]
cols = [PAL["blue"], PAL["blue"], PAL["muted"], PAL["crit"]]
b = ax[0].bar(range(4), vals, color=cols, width=0.62)
for r, v in zip(b, vals):
    txt = f"{v:.0f}" if float(v).is_integer() else f"{v:.2f}".replace(".", ",")
    ax[0].text(r.get_x() + r.get_width() / 2, v + 0.45, txt + " pts", ha="center", fontsize=8)
ax[0].annotate("", xy=(3, 19.2), xytext=(0.15, 19.2),
               arrowprops=dict(arrowstyle="<->", color=PAL["ink2"], lw=0.9))
ax[0].text(1.55, 19.7, "desproporción", ha="center", fontsize=8, color=PAL["ink2"])
ax[0].set_xticks(range(4)); ax[0].set_xticklabels(etiq, fontsize=7.4)
ax[0].set_ylabel("puntos de ACE-III"); ax[0].set_ylim(0, 21.5)
ax[0].yaxis.set_major_formatter(COMA)
ax[0].set_title("a · la regla corrige un sesgo 50 a 200 veces menor", loc="left", fontsize=9.5)

# ── (b) área bajo la curva por tramo
claves = ["<7", "7-11", "≥12"]
y = np.arange(3)[::-1]
for i, k in enumerate(claves):
    d = v7["auc"][k]
    c = PAL["crit"] if k == "<7" else PAL["blue"]
    ax[1].plot([d["ic95"][0], d["ic95"][1]], [y[i]] * 2, color=c, lw=2.6, solid_capstyle="round")
    ax[1].plot([d["auc"]], [y[i]], "o", ms=7, color=c)
    ax[1].text(d["ic95"][1] + 0.006, y[i], f"{d['auc']:.3f}".replace(".", ",") +
               f"  [{d['ic95'][0]:.3f}–{d['ic95'][1]:.3f}]".replace(".", ","),
               va="center", fontsize=7.6, color=c)
    ax[1].text(0.792, y[i] + 0.30, f"{d['n_casos']} casos · {d['n_control']} controles",
               fontsize=6.8, color=PAL["muted"])
ax[1].set_yticks(y); ax[1].set_yticklabels(ETI, fontsize=8.4)
ax[1].set_xlim(0.78, 1.03); ax[1].set_xlabel("área bajo la curva ROC (IC 95 %)")
ax[1].xaxis.set_major_formatter(COMA)
ax[1].set_title("b · lo que ningún corte iguala: discriminar", loc="left", fontsize=9.5)

# ── (c) dispersión: puntaje frente a habilidad, normalizadas al tramo de menor escolaridad
disp = M["dispersion"]
sd_bruto = np.array(disp["bruto"]["de_por_tramo"], float)
# desvío latente del GRM multigrupo (V26 corregido): no arrastra la contracción del EAP
sd_hab = np.array([disp["habilidad_multigrupo"][b]["de"] for b in BANDAS], float)
pend = [disp["dos_metricas"]["tcc"]["pendiente_local"][k] for k in BANDAS]
nb = sd_bruto / sd_bruto[0] * 100
nh = sd_hab / sd_hab[0] * 100
x = np.arange(3); w = 0.36
ax[2].bar(x - w / 2, nb, w, color=PAL["blue"], label="puntaje bruto")
ax[2].bar(x + w / 2, nh, w, color=PAL["aqua"], label="habilidad latente (multigrupo)")
for xi, (a_, b_) in enumerate(zip(nb, nh)):
    ax[2].text(xi - w / 2, a_ + 2, f"{a_:.0f}", ha="center", fontsize=7.6, color=PAL["blue"])
    ax[2].text(xi + w / 2, b_ + 2, f"{b_:.0f}", ha="center", fontsize=7.6, color=PAL["aqua"])
for xi, p_ in enumerate(pend):
    ax[2].text(xi, -12, f"{p_:.1f}".replace(".", ",") + " pts/θ", ha="center",
               fontsize=7, color=PAL["muted"])
ax[2].text(1, -20.5, "pendiente local del instrumento", ha="center", fontsize=7,
           color=PAL["muted"], style="italic")
ax[2].set_xticks(x); ax[2].set_xticklabels(ETI, fontsize=8.4)
ax[2].set_ylim(0, 118); ax[2].set_ylabel("dispersión, % del tramo de menor escolaridad")
ax[2].axhline(100, color=PAL["baseline"], lw=0.7, ls=":")
ax[2].legend(frameon=False, fontsize=7.4, loc="upper right")
ax[2].yaxis.set_major_formatter(COMA)
ax[2].set_title("c · el puntaje se estrecha más que la habilidad", loc="left", fontsize=9.5)

fig.tight_layout()
guarda(fig, "Figura4_instrumento"); plt.close(fig)

# ═══════════════════════════════════════════════════ FIGURA 5 (dos paneles)
# (a) reparto de señalamientos a igual positividad; (b) el gradiente a lo largo del punto de
# operación, que responde la objeción del punto único y muestra que la regla de dos cortes es peor
# que un corte único a la misma positividad.
v29 = L("V29_sensibilidad_y_operacion.json")
P = v13["principal"]
fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.0), gridspec_kw={"width_ratios": [1, 1.05]})

vig = [P["vigente"]["fp"][k] for k in claves]
con = [P["continua"]["fp"][k] for k in claves]
x = np.arange(3); w = 0.36
ax[0].bar(x - w / 2, vig, w, color=PAL["crit"], label="regla vigente (86 / 68)")
ax[0].bar(x + w / 2, con, w, color=PAL["blue"], label="corrección continua")
for xi, (a_, b_) in enumerate(zip(vig, con)):
    ax[0].text(xi - w / 2, a_ + 1.1, f"{a_:.1f} %".replace(".", ","), ha="center", fontsize=8)
    ax[0].text(xi + w / 2, b_ + 1.1, f"{b_:.1f} %".replace(".", ","), ha="center", fontsize=8)
gp = v29["gradiente_preespecificado"]
yb = max(vig) + 6.0
for xi in (0 - w / 2, 1 - w / 2):
    ax[0].plot([xi, xi], [vig[0 if xi < 0.5 else 1] + 1.8, yb], color=PAL["crit"], lw=0.8)
ax[0].plot([0 - w / 2, 1 - w / 2], [yb, yb], color=PAL["crit"], lw=0.8)
ax[0].text(0.5 - w / 2, yb + 1.4, f"{gp['vigente']['estimacion']:.1f}".replace(".", ",") +
           " p.p.\n[" + f"{gp['vigente']['ic95'][0]:.1f}".replace(".", ",") + "; " +
           f"{gp['vigente']['ic95'][1]:.1f}".replace(".", ",") + "]",
           ha="center", fontsize=7.6, color=PAL["crit"])
ax[0].set_xticks(x)
ax[0].set_xticklabels([f"{e}\n(n = {P['ctrl_por_tramo'][k]})" for e, k in zip(ETI, claves)], fontsize=8.5)
ax[0].set_xlabel("años de escolaridad"); ax[0].set_ylabel("personas sin deterioro señaladas, %")
ax[0].set_ylim(0, 76); ax[0].yaxis.set_major_formatter(COMA)
ax[0].legend(frameon=False, fontsize=7.6, loc="upper right")
ax[0].set_title("a · reparto a igual tasa de positividad", loc="left", fontsize=9.5)

bar = v29["barrido_operacion"]
pos = [f["positividad"] * 100 for f in bar]
gu = [f["gradiente_corte_unico"] for f in bar]
gc = [f["gradiente_continua"] for f in bar]
pv = P["positividad"]
ax[1].axhline(0, color=PAL["baseline"], lw=0.8)
ax[1].plot(pos, gu, "-o", ms=4, color=PAL["muted"], label="un corte único")
ax[1].plot(pos, gc, "-o", ms=4, color=PAL["blue"], label="corrección continua")
ax[1].plot([pv], [gp["vigente"]["estimacion"]], "D", ms=8, color=PAL["crit"],
           label="regla vigente (dos cortes)")
ax[1].annotate(f"{gp['vigente']['estimacion']:.1f}".replace(".", ",") + " p.p.",
               xy=(pv, gp["vigente"]["estimacion"]), xytext=(pv - 21, gp["vigente"]["estimacion"] + 3),
               fontsize=8, color=PAL["crit"],
               arrowprops=dict(arrowstyle="->", color=PAL["crit"], lw=0.8))
iv = min(range(len(pos)), key=lambda i: abs(pos[i] - pv))
ax[1].annotate(f"un corte único a la misma\npositividad: {gu[iv]:.1f}".replace(".", ",") + " p.p.",
               xy=(pos[iv], gu[iv]), xytext=(pos[iv] - 6, gu[iv] - 15), fontsize=7.6,
               color=PAL["ink2"], arrowprops=dict(arrowstyle="->", color=PAL["ink2"], lw=0.8))
ax[1].set_xlabel("tasa de positividad, %")
ax[1].set_ylabel("gradiente educativo, puntos porcentuales")
ax[1].xaxis.set_major_formatter(COMA); ax[1].yaxis.set_major_formatter(COMA)
ax[1].legend(frameon=False, fontsize=7.6, loc="upper right")
ax[1].set_title("b · el gradiente depende de dónde se opere", loc="left", fontsize=9.5)

fig.tight_layout()
guarda(fig, "Figura5_equidad"); plt.close(fig)

print("\nlisto — Figura 4 con el panel de dispersión y Figura 5 con el barrido del punto de operación")
