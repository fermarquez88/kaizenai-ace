#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V25 — ¿El hallazgo replica con independencia de la ruralidad y del área geográfica?

Dos preguntas distintas que conviene no confundir:

  · RURALIDAD    ZonaResidencia, declarada por el participante (1 / 2).
                 La planilla no trae leyenda para ese código. La codificación se DEDUCE del
                 cruce con el departamento: la categoría 2 es cero en Capital, casi cero en
                 Rawson y Rivadavia, y se concentra en 25 de Mayo, 9 de Julio y Albardón;
                 además su escolaridad media es 7,0 contra 9,8. Se adopta 2 = rural, y se
                 declara como deducción, no como dato de origen.

  · ÁREA         Departamento del centro de evaluación. Gran San Juan = Capital, Chimbas,
                 Rawson, Rivadavia, Santa Lucía y Pocito; periferia = el resto.

No son la misma variable ni miden lo mismo: la ruralidad se declara a nivel de vivienda y
cubre 596 de 758 participantes; el área es administrativa y cubre 621. El área tiene tres
veces más controles en el estrato desfavorecido, de modo que es la que sostiene el hallazgo.

Salida: resultados/V25_replicacion_geografica.json + figuras/FiguraS_geografia.{jpg,pdf}
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL                 # noqa: E402
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.ticker import FuncFormatter                  # noqa: E402

set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
SESGO_LOGCHI2 = 1.2703628454614782
GSJ = {"Capital", "Chimbas", "Rawson", "Rivadavia", "Santa Lucía", "Pocito"}
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
BANDAS = ["<7", "7-11", "≥12"]
FQ = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"

# ── datos
CSV = NM / "Mix neuromentias - Base mixta 23+24 (valores).csv"
craw = pd.read_csv(CSV, header=4, dtype=object, low_memory=False)
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"])
craw["ctrl"] = es_control(craw).values
G = pd.read_csv(EST / "datos/comunitaria_armonizada.csv").merge(
    craw[["doc", "ZonaResidencia", "DEPARTAMENTO-CENTRO", "ctrl"]],
    left_on="dni", right_on="doc", how="left").dropna(subset=["ACE", "edu", "Edad", "Sexo"])
G["rural"] = G.ZonaResidencia.map({"1": "urbana", "2": "rural"})
dep = G["DEPARTAMENTO-CENTRO"]
G["area"] = pd.Series(np.where(dep.isin(GSJ), "Gran San Juan", "periferia"),
                      index=G.index).where(dep.notna())
G["tr"] = TR(G.edu)
G["sen"] = G.ACE < np.where(G.edu >= 12, 86, 68)

R = {"cobertura": {"n_total": len(G),
                   "con_zona": int(G.rural.notna().sum()),
                   "con_departamento": int(G.area.notna().sum())},
     "codificacion_zona": "deducida: 2 = rural (cero en Capital; escolaridad media 7,0 vs 9,8)"}

# ── A. forma funcional por estrato
def forma(d):
    m = smf.ols(FQ, data=d).fit(cov_type="HC3")
    b = m.params["I(edu ** 2)"]; ci = m.conf_int().loc["I(edu ** 2)"]
    ml = smf.ols("ACE ~ edu + Edad + C(Sexo)", data=d).fit()
    lr = 2 * (smf.ols(FQ, data=d).fit().llf - ml.llf)
    return {"n": len(d), "edu_media": round(d.edu.mean(), 1),
            "curvatura": round(b, 4), "ic95": [round(ci[0], 4), round(ci[1], 4)],
            "pend_3": round(m.params["edu"] + 6 * b, 2),
            "pend_17": round(m.params["edu"] + 34 * b, 2),
            "p_cuadratico": float(f"{stats.chi2.sf(lr, 1):.3g}")}

print("A · FORMA FUNCIONAL POR ESTRATO")
R["forma"] = {}
for var in ("rural", "area"):
    D = G.dropna(subset=[var]); R["forma"][var] = {}
    for k, d in D.groupby(var):
        R["forma"][var][k] = forma(d)
        f = R["forma"][var][k]
        print(f"  {k:15} n={f['n']:>4}  curvatura {f['curvatura']:+.4f} "
              f"[{f['ic95'][0]:+.4f}; {f['ic95'][1]:+.4f}]  "
              f"pendiente {f['pend_3']:.2f} → {f['pend_17']:.2f}  p={f['p_cuadratico']}")
    m = smf.ols(f"ACE ~ (edu + I(edu**2))*C({var}) + Edad + C(Sexo)", data=D).fit(cov_type="HC3")
    t = [x for x in m.params.index if "I(edu ** 2):" in x][0]
    R["forma"][var]["p_interaccion_curvatura"] = round(float(m.pvalues[t]), 3)
    print(f"    interacción curvatura × {var}: p = {m.pvalues[t]:.3f}\n")

# ── B. equidad: proporción de controles señalados, con intervalo de Wilson
print("B · CONTROLES SEÑALADOS POR LA REGLA VIGENTE")
Q = G[G.ctrl == True]
R["equidad"] = {}
for var in ("rural", "area"):
    R["equidad"][var] = {}
    for k, d in Q.dropna(subset=[var]).groupby(var):
        fila = {}
        for t in BANDAS:
            s = d.sen[d.tr == t]
            if len(s) == 0:
                continue
            lo, hi = proportion_confint(int(s.sum()), len(s), method="wilson")
            fila[t] = {"k": int(s.sum()), "n": len(s), "pct": round(100 * s.mean(), 1),
                       "ic95": [round(100 * lo), round(100 * hi)]}
        v = [fila[t]["pct"] for t in fila]
        fila["gradiente"] = round(max(v) - min(v), 1)
        fila["n_controles"] = len(d)
        R["equidad"][var][k] = fila
        cel = lambda t: (f"{fila[t]['pct']:.1f}% ({fila[t]['k']}/{fila[t]['n']}) "
                         f"[{fila[t]['ic95'][0]}-{fila[t]['ic95'][1]}]") if t in fila else "—"
        print(f"  {k:15} <7 {cel('<7'):28} 7-11 {cel('7-11'):26} ≥12 {cel('≥12'):26} "
              f"gradiente {fila['gradiente']:.1f}")

# ── C. dispersión por estrato
print("\nC · DISPERSIÓN DEL RENDIMIENTO NORMAL, a los 65 años")
R["dispersion"] = {}
for var in ("rural", "area"):
    R["dispersion"][var] = {}
    for k, d in Q.dropna(subset=[var]).groupby(var):
        if len(d) < 45:
            R["dispersion"][var][k] = {"n": len(d), "estimable": False}
            print(f"  {k:15} n={len(d):>4}  muestra insuficiente")
            continue
        mu = smf.ols(FQ, data=d).fit()
        t2 = d.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-6, None)))
        sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
        sg = lambda e: float(np.sqrt(np.exp(
            SESGO_LOGCHI2 + sd.predict(pd.DataFrame({"edu": [e], "Edad": [65]}))[0])))
        R["dispersion"][var][k] = {"n": len(d), "estimable": True,
                                   "de_0": round(sg(0), 1), "de_20": round(sg(20), 1),
                                   "pendiente": round(float(sd.params["edu"]), 4),
                                   "p": round(float(sd.pvalues["edu"]), 3)}
        r = R["dispersion"][var][k]
        print(f"  {k:15} n={r['n']:>4}  DE de {r['de_0']:.1f} a {r['de_20']:.1f}  "
              f"pendiente {r['pendiente']:+.4f} (p = {r['p']:.3f})")

# ── figura: gradiente por estrato, con intervalos
fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.3))
for j, (var, titulo) in enumerate([("area", "a  Por área: Gran San Juan frente a periferia"),
                                   ("rural", "b  Por zona declarada: urbana frente a rural")]):
    estr = list(R["equidad"][var].keys())
    x = np.arange(len(BANDAS)); w = 0.36
    for i, k in enumerate(estr):
        f = R["equidad"][var][k]
        y = [f[t]["pct"] if t in f else np.nan for t in BANDAS]
        lo = [f[t]["pct"] - f[t]["ic95"][0] if t in f else 0 for t in BANDAS]
        hi = [f[t]["ic95"][1] - f[t]["pct"] if t in f else 0 for t in BANDAS]
        col = PAL["crit"] if i == (1 if var == "area" else 0) else PAL["blue"]
        ax[j].bar(x + (i - 0.5) * w, y, w, color=col, label=k)
        ax[j].errorbar(x + (i - 0.5) * w, y, yerr=[lo, hi], fmt="none",
                       ecolor=PAL["ink"], elinewidth=1, capsize=3)
        for xi, (yi, t) in enumerate(zip(y, BANDAS)):
            if t in f:
                ax[j].text(xi + (i - 0.5) * w, -4.5, f"n={f[t]['n']}",
                           ha="center", fontsize=7.4, color=PAL["ink2"])
    ax[j].set_xticks(x); ax[j].set_xticklabels(["menos de 7 años", "7 a 11 años", "12 años o más"])
    ax[j].set_ylim(-9, 100); ax[j].set_ylabel("% de controles señalados por la regla")
    ax[j].set_xlabel("Años de escolaridad completos")
    ax[j].set_title(titulo, loc="left", fontsize=10.6)
    ax[j].legend(fontsize=8.4, frameon=False, loc="upper center")
    ax[j].yaxis.set_major_formatter(COMA)
fig.tight_layout()
for ext in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
    fig.savefig(EST / f"figuras/FiguraS_geografia.{ext}", dpi=300,
                bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)

Path(EST / "resultados/V25_replicacion_geografica.json").write_text(
    json.dumps(R, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("\n-> resultados/V25_replicacion_geografica.json + figuras/FiguraS_geografia")
