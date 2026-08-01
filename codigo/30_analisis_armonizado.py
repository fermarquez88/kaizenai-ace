#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ANÁLISIS COMPLETO CON EL RECONOCIMIENTO ARMONIZADO.

ARMONIZACIÓN (declarada a priori). El ítem de reconocimiento de nombre y dirección
(`ACE_MReconocNyD`, máx 5) se puntuó con reglas distintas en las dos fuentes:
  · Clínica  — regla estándar del ACE-III: los elementos evocados libremente cuentan como
    reconocidos. Correlación evocación–reconocimiento +0,652.
  · Comunitaria — se puntuó SÓLO sobre los elementos no evocados. Correlación −0,180, y el
    máximo observado es exactamente 7−evocación en cada nivel de evocación (con la excepción
    de evocación 7/7, donde se asigna 5 por convención).
La regla comunitaria queda identificada en los propios datos, de modo que es reconstruible:
    reconocimiento_estándar = mín(5, reconocimiento_observado + evocados_del_bloque)
    y 5 si la evocación fue 7/7
Como la base sólo guarda totales de bloque (no el desglose de los 5 sub-ítems), los evocados del
bloque se aproximan por round(evocación × 5/7). Es la única aproximación del procedimiento y se
declara como limitación.

Todo el análisis se corre sobre el ACE-III armonizado, con el original como sensibilidad.

Salida: consola + out/30_armonizado.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from patsy import dmatrix, dmatrices
from scipy import stats

warnings.filterwarnings("ignore")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
ITEMS = ['ACE_AtOT','ACE_AtOE','ACE_AtRegistro','ACE_AtSubstr','ACE_MRecuerdo','ACE_MAnterogr',
         'ACE_MRetrogr','ACE_MRecuerdoNyD','ACE_MReconocNyD','ACE_FluVerbFPC','ACE_FluVerbSPC',
         'ACE_LComprensionLyH','ACE_LEscrit','ACE_LRepP','ACE_LRepProverb','ACE_LDenom',
         'ACE_LCompDibujo','ACE_LLectura','ACE_HabVisoDiagrama','ACE_HabVisoCubo',
         'ACE_HabPerPuntos','ACE_HabPerLetras','ACE_HabVisoReloj']
MARG = (3, 7, 12, 17)
R = {}


def lrt(m0, m1):
    c = 2 * (m1.llf - m0.llf); df = int(m1.df_model - m0.df_model)
    return {"chi2": round(float(c), 2), "df": df, "p": float(stats.chi2.sf(c, df))}


def armoniza(recuerdo, reconoc):
    """Lleva el reconocimiento de la regla comunitaria a la regla estándar del ACE-III."""
    evocados_bloque = np.minimum(5, np.round(recuerdo * 5 / 7))
    std = np.minimum(5, reconoc + evocados_bloque)
    return np.where(recuerdo == 7, 5, std)


# ================================================================ datos
sol = set(pd.read_csv(NM / "analisis/solape_dni.csv").dni.astype(str))
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
X = pd.DataFrame({k: pd.to_numeric(craw[k], errors="coerce") for k in ITEMS})
X["ACE_LLectura"] = X.ACE_LLectura.clip(upper=1)
mk = X.notna().all(axis=1).values
Xm = X[mk].reset_index(drop=True)
rec_std = armoniza(Xm.ACE_MRecuerdoNyD.values, Xm.ACE_MReconocNyD.values)
com = pd.DataFrame({
    "ACE": (Xm[ITEMS].sum(axis=1) - Xm.ACE_MReconocNyD + rec_std).values,   # armonizado
    "ACE_orig": Xm[ITEMS].sum(axis=1).values,
    "ACE_col": pd.to_numeric(craw["ACE_TOTAL"], errors="coerce")[mk].values,
    "Edad": pd.to_numeric(craw.Edad, errors="coerce")[mk].values,
    "edu": pd.to_numeric(craw.ed_anos_completos, errors="coerce").mask(lambda s: s > 30)[mk].values,
    "Sexo": craw.Sexo.astype(str)[mk].values,
    "ola": pd.to_datetime(craw["Fecha"], errors="coerce").dt.year[mk].values,
    "dni": craw["dni"].astype(str).str.replace(r"\D", "", regex=True)[mk].values,
}).dropna(subset=["ACE", "Edad", "edu", "Sexo"])
com_full = com.copy()
com = com[~com.dni.isin(sol)].assign(cohorte="comunitaria").reset_index(drop=True)

cli = pd.read_csv(NM / "analisis/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
cli = cli.dropna(subset=["ACE", "edu", "Edad", "Sexo"])
cli = cli[cli.edu.between(0, 30)].assign(cohorte="clinica", ACE_orig=lambda x: x.ACE).reset_index(drop=True)

print("=" * 100)
print(f"COMUNITARIA n={len(com)} (ACE-III armonizado)   |   CLÍNICA n={len(cli)}   |   total {len(com)+len(cli)}")
print(f"  efecto de la armonización en la comunitaria: {com.ACE_orig.mean():.2f} -> {com.ACE.mean():.2f} "
      f"(+{(com.ACE-com.ACE_orig).mean():.2f}; r={com.ACE.corr(com.ACE_orig):.4f})")
R["armonizacion"] = {"media_original": round(float(com.ACE_orig.mean()), 2),
                     "media_armonizada": round(float(com.ACE.mean()), 2),
                     "delta_medio": round(float((com.ACE - com.ACE_orig).mean()), 2),
                     "r": round(float(com.ACE.corr(com.ACE_orig)), 4),
                     "delta_por_tramo": {str(k): round(float(v), 2) for k, v in
                                         (com.ACE - com.ACE_orig).groupby(
                                             pd.cut(com.edu, [-1, 6.5, 11.5, 99],
                                                    labels=["<7", "7-11", "≥12"]), observed=True).mean().items()}}
print(f"  cambio por tramo educativo: {R['armonizacion']['delta_por_tramo']}")

COH = [("comunitaria", com), ("clínica", cli)]
TR = lambda d: pd.cut(d.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
D = pd.concat([com[["ACE", "edu", "Edad", "Sexo", "cohorte"]],
               cli[["ACE", "edu", "Edad", "Sexo", "cohorte"]]], ignore_index=True)

# ---- descriptivos
desc = D.groupby("cohorte").apply(lambda d: pd.Series({
    "n": len(d), "mujeres_%": round(100*(d.Sexo == "Mujer").mean(), 1),
    "edad_mediana": d.Edad.median(), "edad_Q1Q3": f"{d.Edad.quantile(.25):.0f}-{d.Edad.quantile(.75):.0f}",
    "edad_rango": f"{d.Edad.min():.0f}-{d.Edad.max():.0f}",
    "edu_mediana": d.edu.median(), "edu_Q1Q3": f"{d.edu.quantile(.25):.0f}-{d.edu.quantile(.75):.0f}",
    "n_lt7": int((d.edu < 7).sum()), "n_7a11": int(d.edu.between(7, 11).sum()),
    "n_ge12": int((d.edu >= 12).sum()),
    "ACE_media": round(d.ACE.mean(), 1), "ACE_sd": round(d.ACE.std(), 1),
    "ACE_mediana": d.ACE.median(), "ACE_Q1Q3": f"{d.ACE.quantile(.25):.0f}-{d.ACE.quantile(.75):.0f}",
    "pct_ge90": round(100*(d.ACE >= 90).mean(), 1), "pct_le40": round(100*(d.ACE <= 40).mean(), 1)}))
print("\n" + desc.T.to_string())
R["descriptivos"] = desc.reset_index().to_dict("records")


def perfil(d, lab):
    lin = smf.ols("ACE ~ edu + Edad + C(Sexo)", data=d).fit()
    qua = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    ml = smf.ols("ACE ~ edu + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    mq = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    nm = list(mq.params.index); i1, i2 = nm.index("edu"), nm.index("I(edu ** 2)")
    V = np.asarray(mq.cov_params()); b1, b2 = mq.params.iloc[i1], mq.params.iloc[i2]
    ci2 = mq.conf_int().loc["I(edu ** 2)"]
    o = {"n": int(len(d)),
         "lineal": {"b": round(float(ml.params["edu"]), 3),
                    "ic95": [round(x, 3) for x in ml.conf_int().loc["edu"].tolist()]},
         "b2": {"b": round(float(b2), 4), "ic95": [round(float(ci2[0]), 4), round(float(ci2[1]), 4)],
                "p": float(mq.pvalues["I(edu ** 2)"])},
         "AIC": {"lineal": round(lin.aic, 1), "cuadratica": round(qua.aic, 1)}, "marginal": {}}
    for e in MARG:
        v = np.zeros(len(nm)); v[i1] = 1; v[i2] = 2*e
        est = float(b1 + 2*b2*e); se = float(np.sqrt(v @ V @ v))
        o["marginal"][str(e)] = {"b": round(est, 2),
                                 "ic95": [round(est-1.96*se, 2), round(est+1.96*se, 2)]}
    m = "  ".join(f"{k}a:{x['b']}[{x['ic95'][0]},{x['ic95'][1]}]" for k, x in o["marginal"].items())
    print(f"  {lab:<22} n={o['n']:<5} lineal={o['lineal']['b']:<6} b2={o['b2']['b']} "
          f"{o['b2']['ic95']} p={o['b2']['p']:.2e}\n      {m}")
    return o


print("\n" + "=" * 100 + "\n1. FORMA FUNCIONAL POR COHORTE (ACE-III armonizado)")
R["comunitaria"] = perfil(com, "COMUNITARIA")
R["clinica"] = perfil(cli, "CLÍNICA")

# ---- heterogeneidad
F_full = "ACE ~ (edu + I(edu**2))*C(cohorte) + Edad + C(Sexo)"
F_lin = "ACE ~ edu*C(cohorte) + I(edu**2) + Edad + C(Sexo)"
F_com = "ACE ~ edu + I(edu**2) + C(cohorte) + Edad + C(Sexo)"
R["heterogeneidad"] = {"forma_completa": lrt(smf.ols(F_com, data=D).fit(), smf.ols(F_full, data=D).fit()),
                       "curvatura": lrt(smf.ols(F_lin, data=D).fit(), smf.ols(F_full, data=D).fit()),
                       "pendiente_lineal": lrt(smf.ols(F_com, data=D).fit(), smf.ols(F_lin, data=D).fit())}
mf = smf.ols(F_full, data=D).fit(cov_type="HC3")
k2 = [i for i in mf.params.index if i.startswith("I(edu ** 2):")][0]
R["contraste_curvatura"] = {"dif": round(float(mf.params[k2]), 4),
                            "ic95": [round(x, 4) for x in mf.conf_int().loc[k2].tolist()],
                            "p": float(mf.pvalues[k2])}
print("\n2. REPLICACIÓN ENTRE COHORTES")
for k, v in R["heterogeneidad"].items():
    print(f"  {k:<18} chi2={v['chi2']:<7} gl={v['df']:<3} p={v['p']:.4g}")
print(f"  contraste de curvatura: {R['contraste_curvatura']['dif']} "
      f"IC95 {R['contraste_curvatura']['ic95']} p={R['contraste_curvatura']['p']:.3f}")
lo_e, hi_e = max(com.Edad.min(), cli.Edad.min()), min(com.Edad.max(), cli.Edad.max())
Ds = D[D.Edad.between(lo_e, hi_e)]
mfs = smf.ols(F_full, data=Ds).fit(cov_type="HC3")
k2s = [i for i in mfs.params.index if i.startswith("I(edu ** 2):")][0]
R["soporte_comun"] = {"n": int(len(Ds)), "dif": round(float(mfs.params[k2s]), 4),
                      "p": float(mfs.pvalues[k2s])}
print(f"  en soporte etario común [{lo_e:.0f},{hi_e:.0f}] (n={len(Ds)}): "
      f"dif {R['soporte_comun']['dif']} p={R['soporte_comun']['p']:.3f}")

# ---- especificación
print("\n3. ESPECIFICACIÓN (spline cúbico natural vs cuadrática)")
R["especificacion"] = {}
for lab, d in COH:
    lin = smf.ols("ACE ~ edu + Edad + C(Sexo)", data=d).fit()
    qua = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    sp = dmatrix("cr(edu, df=4) - 1", d, return_type="dataframe")
    sp.columns = [f"s{i}" for i in range(sp.shape[1])]
    ss = pd.concat([d.reset_index(drop=True), sp.reset_index(drop=True)], axis=1)
    spl = smf.ols("ACE ~ " + " + ".join(sp.columns) + " + Edad + C(Sexo)", data=ss).fit()
    R["especificacion"][lab] = {"AIC": {"lin": round(lin.aic, 1), "cuad": round(qua.aic, 1),
                                        "spline": round(spl.aic, 1)},
                                "cuad_vs_lin": lrt(lin, qua), "spline_vs_cuad": lrt(qua, spl)}
    a = R["especificacion"][lab]["AIC"]
    print(f"  {lab:<13} AIC lin/cuad/spl {a['lin']}/{a['cuad']}/{a['spline']}  "
          f"cuad>lin p={R['especificacion'][lab]['cuad_vs_lin']['p']:.3g}  "
          f"spl>cuad p={R['especificacion'][lab]['spline_vs_cuad']['p']:.3g}")

# ---- políticas de corte
print("\n4. POLÍTICAS DE CORTE (P1 único 86 · P2 escalón 86/68 vigente · P3 continuo)")
R["politicas"] = {}; R["curva_corte"] = {}; R["dentro_banda"] = {}; R["reclasificacion"] = {}
GUARD = {}
for nom, d in COH:
    d = d.copy()
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    ref = d.loc[d.edu >= 12, "edu"].median()
    e_ref = float(m.predict(pd.DataFrame({"edu": [ref], "Edad": [d.Edad.mean()], "Sexo": ["Mujer"]})).iloc[0])
    pr = pd.DataFrame({"edu": d.edu, "Edad": d.Edad.mean(), "Sexo": "Mujer"})
    d["corte"] = 86 - (e_ref - m.predict(pr).values)
    d["P1"] = d.ACE < 86
    d["P2"] = np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68)
    d["P3"] = d.ACE < d.corte
    t = d.groupby(TR(d), observed=True).apply(lambda g: pd.Series({
        "n": len(g), "P1": round(100*g.P1.mean(), 1), "P2": round(100*g.P2.mean(), 1),
        "P3": round(100*g.P3.mean(), 1)}))
    print(f"  {nom.upper()}"); print(t.to_string())
    R["politicas"][nom] = t.reset_index().to_dict("records")
    g = pd.DataFrame({"edu": [2,4,7,9,11,12,14,17], "Edad": d.Edad.mean(), "Sexo": "Mujer"})
    corte = 86 - (e_ref - m.predict(g).values); esp = m.predict(g).values
    R["curva_corte"][nom] = {str(int(e)): round(float(c), 1) for e, c in zip(g.edu, corte)}
    R["curva_corte"][nom]["salto_11_12"] = round(float(np.interp(12, g.edu, corte) - np.interp(11, g.edu, corte)), 1)
    idx = [0,1,2,3,4]
    R["dentro_banda"][nom] = {"esperado": [round(float(esp[i]), 1) for i in idx],
                              "rango": round(float(esp[4] - esp[0]), 1)}
    dis = d.P2 != d.P3
    det = d.groupby(TR(d), observed=True).apply(lambda g2: pd.Series({
        "n": len(g2), "%cambia": round(100*(g2.P2 != g2.P3).mean(), 1),
        "→positivo": int(((~g2.P2) & g2.P3).sum()), "→negativo": int((g2.P2 & (~g2.P3)).sum())}))
    R["reclasificacion"][nom] = {"global": round(100*float(dis.mean()), 1), "n": int(len(d)),
                                 "detalle": det.reset_index().to_dict("records")}
    print(f"    corte continuo: " + " ".join(f"{int(e)}a:{c:.0f}" for e, c in zip(g.edu, corte)))
    print(f"    salto real 11→12: {R['curva_corte'][nom]['salto_11_12']} (la regla salta 18) | "
          f"rango dentro de <12: {R['dentro_banda'][nom]['rango']} pts")
    print(f"    reclasificación P2→P3: {R['reclasificacion'][nom]['global']}%"); print(det.to_string()); print()
    GUARD[nom] = d

# ---- supuestos y sensibilidades
y, Xd = dmatrices("ACE ~ edu + I(edu**2) + Edad + C(Sexo) + C(cohorte)", data=D, return_type="dataframe")
bp = het_breuschpagan(sm.OLS(y, Xd).fit().resid, Xd)
Xc = D.assign(edu_c=D.edu - D.edu.mean())
_, Xv = dmatrices("ACE ~ edu_c + I(edu_c**2) + Edad", data=Xc, return_type="dataframe")
R["supuestos"] = {"breusch_pagan_p": float(bp[1]),
                  "vif": {Xv.columns[i]: round(float(variance_inflation_factor(Xv.values, i)), 2)
                          for i in range(1, Xv.shape[1])}}
print("5. SUPUESTOS: Breusch-Pagan p=%.3g | VIF %s" % (bp[1], R["supuestos"]["vif"]))


def b2(d, y="ACE"):
    m = smf.ols(f"{y} ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    return {"n": int(len(d)), "b2": round(float(m.params["I(edu ** 2)"]), 4),
            "p": float(m.pvalues["I(edu ** 2)"])}


print("\n6. SENSIBILIDADES")
S = {"principal": {"comunitaria": b2(com), "clínica": b2(cli)},
     "ACE sin armonizar": {"comunitaria": b2(com, "ACE_orig")},
     "sin excluir solape": {"comunitaria": b2(com_full.assign(cohorte="c"))},
     "columna ACE_TOTAL": {"comunitaria": b2(com.dropna(subset=["ACE_col"]).assign(ACE=lambda x: x.ACE_col))},
     "ajuste por ola": {"comunitaria": {"b2": round(float(smf.ols(
         "ACE ~ edu + I(edu**2) + Edad + C(Sexo) + C(ola)", data=com).fit(cov_type="HC3")
         .params["I(edu ** 2)"]), 4)}},
     "sin techo (<95)": {"comunitaria": b2(com[com.ACE < 95]), "clínica": b2(cli[cli.ACE < 95])},
     "edad 46-85": {"comunitaria": b2(com[com.Edad.between(46, 85)]), "clínica": b2(cli[cli.Edad.between(46, 85)])},
     "educación ≤18": {"comunitaria": b2(com[com.edu <= 18]), "clínica": b2(cli[cli.edu <= 18])}}
if "estado" in cli.columns:
    S["sólo ítems validados"] = {"clínica": b2(cli[cli.estado == "items_validados"])}
for lab, v in S.items():
    print(f"  {lab:<24} " + "  ".join(f"{k}: b2={x['b2']}" + (f" (n={x['n']})" if "n" in x else "")
                                      for k, x in v.items()))
R["sensibilidades"] = S

(OUTD / "30_armonizado.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
com.to_csv(NM / "analisis/comunitaria_armonizada.csv", index=False)
print(f"\n-> analisis/comunitaria_armonizada.csv | {OUTD/'30_armonizado.json'}")
