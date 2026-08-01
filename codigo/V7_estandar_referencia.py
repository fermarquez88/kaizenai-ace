#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V7 — ANÁLISIS CONTRA ESTÁNDAR DE REFERENCIA.

Se dispone ahora de dos grupos definidos SIN usar el ACE-III:
  · Demencia            — juicio clínico narrativo (deterioro moderado, moderado-severo o severo)
  · DCL                 — juicio clínico narrativo (leve o leve-moderado)
  · Sin demencia        — cohorte comunitaria sin compromiso funcional en las subescalas del ADLQ
                          que son neutrales respecto de la escolaridad (básicas + hogar + dinero),
                          más los clínicos rotulados sin afectación.

  A. ¿Discrimina el ACE-III igual de bien en todos los tramos educativos? (área bajo la curva)
  B. La regla vigente frente a un corte único: sensibilidad, especificidad y equilibrio.
  C. El gradiente educativo de los falsos positivos bajo cada regla — la pregunta de equidad.
  D. Corte óptimo empírico por tramo educativo, y su contraste con 86/68.
  E. Forma funcional de la asociación escolaridad–ACE-III DENTRO de cada estrato diagnóstico.

Advertencia de diseño: los casos provienen de la cohorte clínica y los controles mayormente de la
comunitaria (diseño de dos puertas), lo que infla la exactitud absoluta. Por eso **no se reporta
exactitud absoluta como resultado**: todas las comparaciones son entre reglas sobre la misma
muestra, donde ese sesgo se cancela.

Salida: consola + resultados/V7_estandar_referencia.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
rng = np.random.default_rng(20260801)
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
R = {}

dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv")
ctrl = pd.read_csv(EST / "datos/controles_comunitarios.csv")

cas = dx3[dx3.dx3.isin(["DCL", "Demencia"])][["ACE", "edu", "Edad", "Sexo", "dx3"]].copy()
cas["origen"] = "clinica"
ctrl = ctrl.rename(columns={c: c[:-2] for c in ctrl.columns if c.endswith("_y") and c[:-2] in ("Edad","Sexo")})
for _c in ("Edad","Sexo"):
    if _c not in ctrl.columns:
        _alt=[x for x in ctrl.columns if x.lower().startswith(_c.lower())]
        ctrl[_c]=ctrl[_alt[0]]
con = ctrl[["ACE", "edu", "Edad", "Sexo"]].copy()
con["dx3"] = "Sin demencia"; con["origen"] = "comunitaria"
extra = dx3[dx3.dx3 == "Sin afectación"][["ACE", "edu", "Edad", "Sexo"]].copy()
extra["dx3"] = "Sin demencia"; extra["origen"] = "clinica"
D = pd.concat([cas, con, extra], ignore_index=True).dropna(subset=["ACE", "edu"])
D["tr"] = pd.cut(D.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
D["demencia"] = (D.dx3 == "Demencia").astype(int)
D["cualquier"] = (D.dx3 != "Sin demencia").astype(int)

print("MUESTRA CON ESTÁNDAR DE REFERENCIA")
print(pd.crosstab(D.dx3, D.tr, margins=True).to_string())
print(f"\ntotal = {len(D)}   |   controles de la comunidad {int((D.origen=='comunitaria').sum())}, "
      f"de la clínica {int(((D.origen=='clinica')&(D.dx3=='Sin demencia')).sum())}")
R["muestra"] = pd.crosstab(D.dx3, D.tr).to_dict()


def auc(pos, neg):
    """Área bajo la curva por el estadístico de Mann-Whitney (probabilidad de concordancia)."""
    if len(pos) < 5 or len(neg) < 5:
        return np.nan, (np.nan, np.nan)
    u = stats.mannwhitneyu(neg, pos, alternative="greater").statistic
    a = u / (len(pos) * len(neg))
    bs = [np.mean(rng.choice(neg, len(neg))[:, None] > rng.choice(pos, len(pos))[None, :])
          for _ in range(400)]
    return a, (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


# ══════════════════════════════════════════ A. ¿DISCRIMINA IGUAL EN TODOS LOS TRAMOS?
print("\n" + "=" * 94 + "\nA. CAPACIDAD DISCRIMINATIVA DEL ACE-III POR TRAMO EDUCATIVO")
print("   Si el área bajo la curva es similar entre tramos, el test funciona igual de bien en todos")
print("   y lo único que cambia es dónde debe situarse el umbral.\n")
R["auc"] = {}
print(f"{'tramo':<8}{'n casos':>9}{'n control':>11}{'AUC demencia':>15}{'IC 95%':>22}")
for tr in ["<7", "7-11", "≥12"]:
    s = D[D.tr == tr]
    p, n = s[s.demencia == 1].ACE.values, s[s.dx3 == "Sin demencia"].ACE.values
    a, ci = auc(p, n)
    R["auc"][tr] = {"n_casos": int(len(p)), "n_control": int(len(n)),
                    "auc": None if np.isnan(a) else round(float(a), 3),
                    "ic95": [round(ci[0], 3), round(ci[1], 3)] if not np.isnan(a) else None}
    print(f"{tr:<8}{len(p):>9}{len(n):>11}{a:>15.3f}{f'[{ci[0]:.3f}; {ci[1]:.3f}]':>22}")

# ══════════════════════════════════════════ B. REGLA VIGENTE VS CORTE ÚNICO
print("\n" + "=" * 94 + "\nB. LA REGLA VIGENTE FRENTE A UN CORTE ÚNICO")
REGLAS = {
    "vigente 86/68 (<12 años)": lambda d: np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68),
    "corte único 86": lambda d: d.ACE < 86,
    "corte único 82": lambda d: d.ACE < 82,
    "corte único 88": lambda d: d.ACE < 88,
}


def met(d, pos_col, flag):
    y, p = d[pos_col].values, np.asarray(flag).astype(int)
    tp, fn = int(((y == 1) & (p == 1)).sum()), int(((y == 1) & (p == 0)).sum())
    fp, tn = int(((y == 0) & (p == 1)).sum()), int(((y == 0) & (p == 0)).sum())
    se = tp / (tp + fn) if tp + fn else np.nan
    sp = tn / (tn + fp) if tn + fp else np.nan
    return se, sp, se + sp - 1, (se + sp) / 2


R["reglas"] = {}
print(f"\n  desenlace: DEMENCIA  (n={int(D.demencia.sum())} casos, "
      f"{int((D.dx3=='Sin demencia').sum())} sin demencia)")
print(f"  {'regla':<26}{'sensib.':>9}{'especif.':>10}{'Youden':>9}{'exact. equil.':>15}")
dd = D[D.dx3 != "DCL"]
for nm, f in REGLAS.items():
    se, sp, j, ba = met(dd, "demencia", f(dd))
    R["reglas"][nm] = {"sens": round(se, 3), "espec": round(sp, 3), "youden": round(j, 3),
                       "exactitud_equilibrada": round(ba, 3)}
    print(f"  {nm:<26}{se:>9.3f}{sp:>10.3f}{j:>9.3f}{ba:>15.3f}")

# ══════════════════════════════════════════ C. EQUIDAD: FALSOS POSITIVOS POR TRAMO
print("\n" + "=" * 94 + "\nC. GRADIENTE EDUCATIVO DE LOS FALSOS POSITIVOS (la pregunta de equidad)")
print("   Proporción de personas SIN demencia que cada regla señala, por tramo educativo.\n")
R["falsos_positivos"] = {}
print(f"  {'regla':<26}{'<7 años':>10}{'7-11':>9}{'≥12':>9}{'rango':>9}")
sd = D[D.dx3 == "Sin demencia"]
for nm, f in REGLAS.items():
    fl = pd.Series(np.asarray(f(sd)).astype(bool), index=sd.index)
    g = fl.groupby(sd.tr, observed=True).mean() * 100
    rango = float(g.max() - g.min())
    R["falsos_positivos"][nm] = {**{k: round(float(v), 1) for k, v in g.items()},
                                 "rango": round(rango, 1)}
    print(f"  {nm:<26}{g.get('<7',np.nan):>10.1f}{g.get('7-11',np.nan):>9.1f}"
          f"{g.get('≥12',np.nan):>9.1f}{rango:>9.1f}")
print("\n  (rango = diferencia entre el tramo más y el menos señalado; menor es más equitativo)")

# ══════════════════════════════════════════ D. CORTE ÓPTIMO EMPÍRICO POR TRAMO
print("\n" + "=" * 94 + "\nD. CORTE ÓPTIMO EMPÍRICO POR TRAMO EDUCATIVO (máximo índice de Youden)")
R["corte_optimo"] = {}
print(f"  {'tramo':<8}{'corte óptimo':>14}{'IC 95% bootstrap':>22}{'regla vigente':>15}{'diferencia':>12}")
for tr in ["<7", "7-11", "≥12"]:
    s = dd[dd.tr == tr]
    if s.demencia.sum() < 10:
        continue
    cs = np.arange(40, 96)
    j = [met(s, "demencia", s.ACE < c)[2] for c in cs]
    opt = int(cs[int(np.nanargmax(j))])
    bs = []
    for _ in range(300):
        ss = s.sample(len(s), replace=True, random_state=None)
        jj = [met(ss, "demencia", ss.ACE < c)[2] for c in cs]
        bs.append(cs[int(np.nanargmax(jj))])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    vig = 68 if tr != "≥12" else 86
    R["corte_optimo"][tr] = {"optimo": opt, "ic95": [int(lo), int(hi)], "vigente": vig,
                             "diferencia": opt - vig}
    print(f"  {tr:<8}{opt:>14}{f'[{lo:.0f}; {hi:.0f}]':>22}{vig:>15}{opt-vig:>+12}")

# ══════════════════════════════════════════ E. FORMA FUNCIONAL POR ESTRATO
print("\n" + "=" * 94 + "\nE. FORMA DE LA ASOCIACIÓN DENTRO DE CADA ESTRATO DIAGNÓSTICO")
print("   ¿Se comporta igual la escolaridad en personas sin demencia, con DCL y con demencia?\n")
R["forma_por_estrato"] = {}
print(f"  {'estrato':<16}{'n':>7}{'curvatura b2':>15}{'IC 95%':>24}{'p':>10}")
for k in ["Sin demencia", "DCL", "Demencia"]:
    s = D[D.dx3 == k].dropna(subset=["Edad", "Sexo"])
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
    b = float(m.params["I(edu ** 2)"]); ci = m.conf_int().loc["I(edu ** 2)"]
    R["forma_por_estrato"][k] = {"n": int(len(s)), "b2": round(b, 4),
                                 "ic95": [round(float(ci[0]), 4), round(float(ci[1]), 4)],
                                 "p": float(m.pvalues["I(edu ** 2)"])}
    print(f"  {k:<16}{len(s):>7}{b:>+15.4f}{f'[{ci[0]:+.4f}; {ci[1]:+.4f}]':>24}"
          f"{m.pvalues['I(edu ** 2)']:>10.4f}")
mi = smf.ols("ACE ~ edu*C(dx3) + I(edu**2)*C(dx3) + Edad + C(Sexo)",
             data=D.dropna(subset=["Edad", "Sexo"])).fit(cov_type="HC3")
ter = [t for t in mi.params.index if "I(edu ** 2):" in t]
w = mi.wald_test_terms(skip_single=False)
pint = float(mi.f_test(" = 0, ".join(ter) + " = 0").pvalue) if ter else np.nan
print(f"\n  prueba conjunta de interacción curvatura × estrato diagnóstico: p={pint:.3f}")
print("  -> " + ("la forma NO difiere entre estratos" if pint > 0.05 else
                 "la forma difiere entre estratos"))
R["interaccion_curvatura_estrato_p"] = pint

(EST / "resultados/V7_estandar_referencia.json").write_text(
    json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> resultados/V7_estandar_referencia.json")
