#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Material para circular con el equipo.

  EQUIPO_tres_regimenes.{jpg,pdf}   figura de 3 paneles: curvas, % señalado y la TABLA
                                    alineada columna por columna con el eje de escolaridad
  EQUIPO_tabla_esperados.{jpg,pdf}  tabla de consulta: esperado (percentil 5)
                                    por año de escolaridad y franja etaria
  tablas/EQUIPO_*.csv / .md         las mismas tablas en texto
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
(EST / "tablas").mkdir(exist_ok=True)
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL          # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

# ── Corrección del sesgo de Harvey (1976) ───────────────────────────────────
# Estimar log(sigma^2) por MCO sobre log(residuo^2) subestima la varianza: si e ~ N(0, s^2),
# entonces E[log(e^2)] = log(s^2) + E[log(chi2_1)] = log(s^2) - 1,27036. Sin corregir, sigma
# queda multiplicado por exp(-1,27036/2) = 0,530, es decir 1,887 veces más chico de lo que es.
# Verificación empírica: sin corregir, el 19,0 % de los controles cae bajo el percentil 5
# nominal y los z tienen DE 1,906; corrigiendo, cae el 6,5 % y los z tienen DE 1,010.
SESGO_LOGCHI2 = 1.2703628454614782   # = -(digamma(1/2) + log 2)

set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))

craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
c40["doc"] = nd(c40["dni"]); c40["rec"] = pd.to_numeric(c40.LDR_Reconocimiento_A, errors="coerce")
c40["acv"] = pd.to_numeric(c40["APN_ACV"], errors="coerce")
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv").merge(
    c40[["doc", "rec", "acv"]].rename(columns={"doc": "dni"}), on="dni", how="left")
# Criterio de dos dominios: memoria de reconocimiento y ausencia de accidente cerebrovascular.
# Son los dos únicos criterios disponibles que no dependen del tramo educativo (V18, V20).
REF = com[(com.rec >= 10) & (com.acv == 0)].dropna(subset=["ACE", "edu", "Edad", "Sexo"])

FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
mu = smf.ols(FP, data=REF).fit()
t2 = REF.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()

# predicción marginal sobre la distribución de sexo de la muestra de referencia
PS = REF.Sexo.value_counts(normalize=True)
def esperado(edu, edad):
    edu, edad = np.asarray(edu, float), np.asarray(edad, float)
    out = np.zeros_like(edu, dtype=float)
    for s, w in PS.items():
        out += w * mu.predict(pd.DataFrame({"edu": edu, "Edad": edad, "Sexo": s})).values
    return out
def sigma(edu, edad):
    return np.sqrt(np.exp(SESGO_LOGCHI2 + sd.predict(pd.DataFrame(
        {"edu": np.asarray(edu, float), "Edad": np.asarray(edad, float)})).values))

E = np.arange(0, 21)
esp = esperado(E, np.full(21, 65.0))
sig = sigma(E, np.full(21, 65.0))
p5 = esp - 1.645*sig
corte = np.where(E >= 12, 86, 68)
señalado = 100*stats.norm.cdf((corte - esp)/sig)

# Los regímenes se derivan del modelo, no se escriben a mano: para cada año de escolaridad
# se mira dónde cae el corte vigente respecto del rendimiento esperado y del percentil 5.
def _reg(i):
    if corte[i] > esp[i]:  return "crit", "El corte supera al\nrendimiento esperado"
    if corte[i] > p5[i]:   return "warn", "El corte cae entre\nel esperado y el p5"
    return "blue", "El corte cae por\ndebajo del p5"

REG, _run = [], None
for i, e in enumerate(E):
    k, txt = _reg(i)
    if _run and _run[0] == k: _run[1] = e
    else:
        if _run: REG.append((_run[2], _run[1], _run[3], PAL[_run[0]]))
        _run = [k, e, e, txt]
if _run: REG.append((_run[2], _run[1], _run[3], PAL[_run[0]]))
def reg_col(x):
    for a, b, _, col in REG:
        if a <= x <= b: return col
    return PAL["ink"]

# ════════════════════════════════ FIGURA 1: curvas + tabla alineada
fig, ax = plt.subplots(3, 1, figsize=(12.4, 11.4), sharex=True,
                       gridspec_kw={"height_ratios": [1.15, 1, 0.42]})

for a, b, _, col in REG:
    ax[0].axvspan(a-0.5, b+0.5, color=col, alpha=0.07, lw=0)
    ax[1].axvspan(a-0.5, b+0.5, color=col, alpha=0.07, lw=0)
    ax[2].axvspan(a-0.5, b+0.5, color=col, alpha=0.07, lw=0)

ax[0].fill_between(E, p5, esp, color=PAL["blue"], alpha=0.16, lw=0,
                   label="rango entre el percentil 5 y el esperado")
ax[0].plot(E, esp, color=PAL["blue"], lw=3, zorder=4, label="rendimiento esperado sin deterioro")
ax[0].plot(E, p5, color=PAL["blue"], lw=1.6, ls=":", zorder=4, label="percentil 5")
ax[0].step(E, corte, where="mid", color=PAL["crit"], lw=3, zorder=5,
           label="corte vigente (68 / 86)")
ax[0].axvline(11.5, color=PAL["ink"], lw=1.3, ls="--", alpha=0.6)
for x, y, t, ha in [(1.2, 40, "el corte declara anormal\nal rendimiento medio", "left"),
                    (8.2, 44, "el corte queda muy por debajo\ndel rendimiento esperado", "center"),
                    (13.0, 96, "el salto aterriza por\nencima del esperado", "left")]:
    ax[0].annotate(t, xy=(x, y), fontsize=9.2, ha=ha, color=PAL["ink"],
                   linespacing=1.35, fontweight="semibold")
ax[0].set_ylabel("ACE-III (puntos)")
ax[0].set_title("a   Dónde cae el corte vigente respecto del rendimiento normal, a los 65 años",
                loc="left", fontsize=12)
ax[0].legend(loc="lower right", fontsize=9, frameon=True, framealpha=0.94, edgecolor="none")
ax[0].set_ylim(28, 104)

ax[1].plot(E[E < 12], señalado[E < 12], "o-", color=PAL["crit"], lw=2.6, ms=6)
ax[1].plot(E[E >= 12], señalado[E >= 12], "o-", color=PAL["crit"], lw=2.6, ms=6)
ax[1].plot([11, 12], [señalado[11], señalado[12]], ":", color=PAL["crit"], lw=1.6, alpha=0.7)
ax[1].axvline(11.5, color=PAL["ink"], lw=1.3, ls="--", alpha=0.6)
ax[1].axhline(5, color=PAL["baseline"], lw=1.2)
ax[1].text(-0.4, 8, "5 %", fontsize=8.6, color=PAL["ink2"], ha="left")
for x, dx, dy, ha in [(0, 0.6, -16, "left"), (11, -0.5, 9, "right"), (12, 0.7, 3, "left")]:
    ax[1].annotate(f"{señalado[x]:.0f} %".replace(".", ","), xy=(x, señalado[x]),
                   xytext=(x+dx, señalado[x]+dy), fontsize=10.5, ha=ha,
                   color=PAL["crit"], fontweight="bold")
ax[1].set_ylabel("% de personas SIN deterioro\nque la regla señala")
ax[1].set_title("b   Proporción de personas sin deterioro señaladas por la regla vigente",
                loc="left", fontsize=12)
ax[1].set_ylim(-3, 118); ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))
for a, b, txt, col in REG:
    ax[1].text((a+b)/2, 99, txt, ha="center", va="top", fontsize=8.4, color=col,
               fontweight="semibold", linespacing=1.3)

# ── panel c: la tabla, alineada con el eje de escolaridad
FILAS = [("Rendimiento esperado", esp, PAL["blue"], "bold"),
         ("Percentil 5", p5, PAL["blue"], "normal"),
         ("Corte vigente", corte.astype(float), PAL["crit"], "normal"),
         ("% sin deterioro señalado", señalado, PAL["crit"], "bold")]
ax[2].set_ylim(-0.6, len(FILAS)-0.3)
for i, (nom, val, col, peso) in enumerate(FILAS):
    y = len(FILAS)-1-i
    ax[2].text(-1.15, y, nom, ha="right", va="center", fontsize=9, color=PAL["ink"],
               fontweight="semibold")
    for x in E:
        c = reg_col(x) if nom.startswith("%") else col
        ax[2].text(x, y, f"{val[x]:.0f}", ha="center", va="center", fontsize=8.4,
                   color=c, fontweight=peso)
    if i < len(FILAS)-1:
        ax[2].axhline(y-0.5, color=PAL["baseline"], lw=0.6, alpha=0.5)
ax[2].axvline(11.5, color=PAL["ink"], lw=1.3, ls="--", alpha=0.6)
ax[2].set_yticks([]); ax[2].set_xlabel("Años de escolaridad completos")
ax[2].set_title("c   Los mismos valores en tabla   ·   ACE-III en puntos, a los 65 años",
                loc="left", fontsize=12)
for s in ("left", "right", "top"): ax[2].spines[s].set_visible(False)

for a_ in ax:
    a_.xaxis.set_major_formatter(COMA); a_.set_xlim(-0.7, 20.7)
for a_ in ax[:2]:
    a_.yaxis.set_major_formatter(COMA)

_s11, _s12 = señalado[11], señalado[12]
fig.suptitle(f"La regla vigente del ACE-III señala al {_s11:.0f} % de las personas sin deterioro con 11 "
             f"años de escolaridad y al {_s12:.0f} % con 12", fontsize=13.5, y=0.988, x=0.012,
             ha="left", fontweight="semibold")
fig.text(0.012, 0.004, f"Modelo estimado sobre {len(REF)} participantes comunitarios con memoria de "
         "reconocimiento normal (criterio independiente del ACE-III y sin gradiente educativo). "
         "La dispersión lleva la corrección de Harvey. Valores ilustrativos: no constituyen normas poblacionales.",
         fontsize=8.4, color=PAL["ink2"], ha="left")
fig.tight_layout(rect=[0.075, 0.018, 1, 0.968])
for ext in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
    fig.savefig(EST / f"figuras/EQUIPO_tres_regimenes.{ext}", dpi=300,
                bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)

# ════════════════════════════════ VERSIÓN PARA EL MANUSCRITO
# Sólo los paneles a y b: la tabla de esperados va como Tabla 3, y el reglamento del congreso
# exige que un mismo resultado no aparezca simultáneamente en tabla y en figura.
fm, am = plt.subplots(2, 1, figsize=(9.2, 7.4), sharex=True,
                      gridspec_kw={"height_ratios": [1.15, 1]})
for a, b, _, col in REG:
    am[0].axvspan(a-0.5, b+0.5, color=col, alpha=0.07, lw=0)
    am[1].axvspan(a-0.5, b+0.5, color=col, alpha=0.07, lw=0)
am[0].fill_between(E, p5, esp, color=PAL["blue"], alpha=0.16, lw=0,
                   label="rango entre el percentil 5 y el esperado")
am[0].plot(E, esp, color=PAL["blue"], lw=2.6, zorder=4, label="rendimiento esperado sin deterioro")
am[0].plot(E, p5, color=PAL["blue"], lw=1.5, ls=":", zorder=4, label="percentil 5")
am[0].step(E, corte, where="mid", color=PAL["crit"], lw=2.6, zorder=5, label="corte vigente (68 / 86)")
am[0].axvline(11.5, color=PAL["ink"], lw=1.2, ls="--", alpha=0.6)
am[0].set_ylabel("ACE-III (puntos)"); am[0].set_ylim(28, 104)
am[0].set_title("a   Posición del corte vigente respecto del rendimiento esperado, a los 65 años",
                loc="left", fontsize=11)
am[0].legend(loc="lower right", fontsize=8.4, frameon=True, framealpha=0.94, edgecolor="none")
am[1].plot(E[E < 12], señalado[E < 12], "o-", color=PAL["crit"], lw=2.3, ms=5)
am[1].plot(E[E >= 12], señalado[E >= 12], "o-", color=PAL["crit"], lw=2.3, ms=5)
am[1].plot([11, 12], [señalado[11], señalado[12]], ":", color=PAL["crit"], lw=1.5, alpha=0.7)
am[1].axvline(11.5, color=PAL["ink"], lw=1.2, ls="--", alpha=0.6)
am[1].axhline(5, color=PAL["baseline"], lw=1.1)
for x, dx, dy, ha in [(0, 0.5, -13, "left"), (11, -0.4, 8, "right"), (12, 0.6, 3, "left")]:
    am[1].annotate(f"{señalado[x]:.0f} %".replace(".", ","), xy=(x, señalado[x]),
                   xytext=(x+dx, señalado[x]+dy), fontsize=9.6, ha=ha,
                   color=PAL["crit"], fontweight="bold")
am[1].set_xlabel("Años de escolaridad completos")
am[1].set_ylabel("% de personas sin deterioro\nseñaladas por la regla")
am[1].set_title("b   Proporción de personas sin deterioro que la regla vigente señala",
                loc="left", fontsize=11)
am[1].set_ylim(-3, 108); am[1].xaxis.set_major_locator(MaxNLocator(integer=True))
for a_ in am:
    a_.xaxis.set_major_formatter(COMA); a_.yaxis.set_major_formatter(COMA); a_.set_xlim(-0.7, 20.7)
fm.tight_layout()
for ext in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
    fm.savefig(EST / f"figuras/Figura3_corte_y_dispersion.{ext}", dpi=300,
               bbox_inches="tight", facecolor="white", **kw)
plt.close(fm)

# ════════════════════════════════ FIGURA 2: tabla de consulta por escolaridad y edad
EDADES = [50, 55, 60, 65, 70, 75, 80]
M_esp = np.array([[esperado([e], [a])[0] for a in EDADES] for e in E])
M_p5 = np.array([[esperado([e], [a])[0] - 1.645*sigma([e], [a])[0] for a in EDADES] for e in E])

fh, fa = plt.subplots(figsize=(9.6, 11.2))
fa.set_xlim(-2.35, len(EDADES)); fa.set_ylim(-1.55, len(E)+0.1); fa.axis("off")
fa.text(-2.3, len(E)-0.35, "Años de\nescolaridad", ha="left", va="center", fontsize=9.2,
        fontweight="bold", color=PAL["ink"], linespacing=1.3)
fa.text(-1.05, len(E)-0.35, "Corte\nvigente", ha="center", va="center", fontsize=9.2,
        fontweight="bold", color=PAL["crit"], linespacing=1.3)
fa.text(len(EDADES)/2 - 0.5, len(E)+0.62, "Edad en años", ha="center", va="center",
        fontsize=9.6, fontweight="bold", color=PAL["ink"])
for j, a in enumerate(EDADES):
    fa.text(j, len(E)-0.35, f"{a}", ha="center", va="center", fontsize=9.6,
            fontweight="bold", color=PAL["ink"])
fa.plot([-2.35, len(EDADES)-0.5], [len(E)-0.85]*2, color=PAL["ink"], lw=1.1)
for i, e in enumerate(E):
    y = len(E)-1.55-i
    col = reg_col(e)
    fa.axhspan(y-0.5, y+0.5, xmin=0.0, xmax=1.0, color=col, alpha=0.07, lw=0)
    fa.text(-2.3, y, f"{e}", ha="left", va="center", fontsize=9.4, color=PAL["ink"],
            fontweight="semibold")
    fa.text(-1.05, y, f"{corte[i]}", ha="center", va="center", fontsize=9.2, color=PAL["crit"])
    for j in range(len(EDADES)):
        fa.text(j, y+0.10, f"{M_esp[i, j]:.0f}", ha="center", va="center", fontsize=9.6,
                color=PAL["ink"], fontweight="semibold")
        fa.text(j, y-0.24, f"({M_p5[i, j]:.0f})", ha="center", va="center", fontsize=7.8,
                color=PAL["ink2"])
fa.plot([-0.5, -0.5], [-1.05, len(E)-0.85], color=PAL["baseline"], lw=0.9)
fa.plot([-2.35, len(EDADES)-0.5], [len(E)-13.05]*2, color=PAL["ink"], lw=1.3, ls="--", alpha=0.6)

fh.suptitle("Rendimiento esperado en el ACE-III según escolaridad y edad",
            fontsize=13.5, y=0.988, x=0.02, ha="left", va="top", fontweight="semibold")
fh.text(0.02, 0.962, "Cada celda: el puntaje esperado en una persona sin deterioro y, entre "
        "paréntesis, el percentil 5.\nUn puntaje por debajo del percentil 5 se aparta de lo esperable "
        "para esa combinación de escolaridad y edad.", fontsize=9.6, color=PAL["ink"], ha="left",
        va="top", linespacing=1.5)
fh.text(0.02, 0.018, f"Modelo de media y dispersión estimado sobre {len(REF)} participantes "
        "comunitarios con memoria de reconocimiento normal, promediado sobre la distribución de sexo "
        "de la muestra.\nLa línea punteada marca el salto del corte vigente entre los 11 y los 12 "
        "años. Valores ilustrativos: no constituyen normas poblacionales.",
        fontsize=8.2, color=PAL["ink2"], ha="left", linespacing=1.4)
fh.tight_layout(rect=[0, 0.048, 1, 0.918])
for ext in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
    fh.savefig(EST / f"figuras/EQUIPO_tabla_esperados.{ext}", dpi=300,
               bbox_inches="tight", facecolor="white", **kw)
plt.close(fh)

# ════════════════════════════════ las mismas tablas en texto
t1 = pd.DataFrame({"anios_escolaridad": E, "esperado": esp.round(1), "percentil_5": p5.round(1),
                   "corte_vigente": corte, "pct_sin_deterioro_senalado": señalado.round(1)})
t1.to_csv(EST / "tablas/EQUIPO_tabla_65anios.csv", index=False)
t2b = pd.DataFrame(M_esp.round(1), index=E, columns=[f"esperado_{a}" for a in EDADES])
t2b = t2b.join(pd.DataFrame(M_p5.round(1), index=E, columns=[f"p5_{a}" for a in EDADES]))
t2b.index.name = "anios_escolaridad"
t2b.to_csv(EST / "tablas/EQUIPO_tabla_esperados_edad.csv")

md = ["# Tablas para el equipo\n",
      f"Modelo estimado sobre {len(REF)} participantes comunitarios con memoria de reconocimiento "
      "normal. Valores ilustrativos: no constituyen normas poblacionales.\n",
      "\n## Tabla 1. A los 65 años\n",
      "| Años de escolaridad | Esperado | Percentil 5 | Corte vigente | % sin deterioro señalado |",
      "|---|---|---|---|---|"]
for i, e in enumerate(E):
    md.append(f"| {e} | {esp[i]:.0f} | {p5[i]:.0f} | {corte[i]} | {señalado[i]:.0f} % |")
md += ["\n## Tabla 2. Esperado (percentil 5) por escolaridad y edad\n",
       "| Años de escolaridad | " + " | ".join(f"{a} años" for a in EDADES) + " | Corte vigente |",
       "|---|" + "---|"*(len(EDADES)+1)]
for i, e in enumerate(E):
    md.append(f"| {e} | " + " | ".join(f"{M_esp[i,j]:.0f} ({M_p5[i,j]:.0f})"
              for j in range(len(EDADES))) + f" | {corte[i]} |")
(EST / "tablas/EQUIPO_tablas.md").write_text("\n".join(md) + "\n")

print(f"n de referencia: {len(REF)}")
print(f"{'años':>5}{'esperado':>10}{'p5':>7}{'corte':>7}{'% señalado':>12}")
for x in E:
    print(f"{x:>5}{esp[x]:>10.0f}{p5[x]:>7.0f}{corte[x]:>7}{señalado[x]:>11.0f} %")
print("\n-> figuras/EQUIPO_tres_regimenes.{jpg,pdf}   (ahora con la tabla como panel c)")
print("-> figuras/Figura3_corte_y_dispersion.{jpg,pdf}   (versión del manuscrito, sin el panel c)")
print("-> figuras/EQUIPO_tabla_esperados.{jpg,pdf}")
print("-> tablas/EQUIPO_tabla_65anios.csv | EQUIPO_tabla_esperados_edad.csv | EQUIPO_tablas.md")
