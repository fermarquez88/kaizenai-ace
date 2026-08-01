#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V2 — REPRODUCCIÓN INDEPENDIENTE DEL ANÁLISIS PRINCIPAL + VARIABILIDAD TEST-RETEST.

Se recalcula TODO desde los datasets analíticos corregidos en V1b, sin tomar ninguna cifra de
corridas anteriores. Cada resultado que va al manuscrito se produce acá.

Contenido:
  A. Descriptivos de ambas cohortes.
  B. ANÁLISIS PRINCIPAL — falsación del escalón en 12 años (indicador + regresión discontinua local
     + diferencia cruda) y prueba de equivalencia frente al salto de 18 puntos.
  C. Forma de la asociación y replicación entre cohortes (modelo único con interacciones).
  D. Consecuencia: positividad de la regla vigente, año por año.
  E. Variabilidad test-retest del ACE-III y error estándar de medición.
  F. Sensibilidades.

Salida: consola + resultados/V2_reproduccion.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from patsy import dmatrix, dmatrices
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUT = EST / "resultados"; OUT.mkdir(exist_ok=True)
R = {}

com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
cli = (pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
       .dropna(subset=["ACE", "edu", "Edad", "Sexo"]))
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
COH = [("comunitaria", com), ("clínica", cli)]
TR = lambda d: pd.cut(d.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
print(f"COMUNITARIA n={len(com)}   |   CLÍNICA n={len(cli)}   |   total {len(com)+len(cli)}")

# ==================================================================== A. DESCRIPTIVOS
D = pd.concat([com.assign(cohorte="comunitaria")[["ACE", "edu", "Edad", "Sexo", "cohorte"]],
               cli.assign(cohorte="clinica")[["ACE", "edu", "Edad", "Sexo", "cohorte"]]],
              ignore_index=True)
desc = D.groupby("cohorte").apply(lambda d: pd.Series({
    "n": len(d), "mujeres_pct": round(100*(d.Sexo == "Mujer").mean(), 1),
    "edad_med": d.Edad.median(), "edad_q1": d.Edad.quantile(.25), "edad_q3": d.Edad.quantile(.75),
    "edad_min": d.Edad.min(), "edad_max": d.Edad.max(),
    "edu_med": d.edu.median(), "edu_q1": d.edu.quantile(.25), "edu_q3": d.edu.quantile(.75),
    "n_lt7": int((d.edu < 7).sum()), "n_7a11": int(d.edu.between(7, 11).sum()),
    "n_ge12": int((d.edu >= 12).sum()),
    "ACE_media": round(d.ACE.mean(), 1), "ACE_de": round(d.ACE.std(), 1),
    "ACE_med": d.ACE.median(), "ACE_q1": d.ACE.quantile(.25), "ACE_q3": d.ACE.quantile(.75),
    "pct_ge90": round(100*(d.ACE >= 90).mean(), 1), "pct_le40": round(100*(d.ACE <= 40).mean(), 1)}))
print("\n" + desc.T.to_string())
R["descriptivos"] = desc.reset_index().to_dict("records")

# ==================================================================== B. FALSACIÓN
print("\n" + "=" * 96 + "\nB. ANÁLISIS PRINCIPAL — ¿existe la discontinuidad en 12 años?")
R["falsacion"] = {}
for nm, d in COH:
    d = d.copy(); d["post"] = (d.edu >= 12).astype(int)
    m = smf.ols("ACE ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    b, se = float(m.params["post"]), float(m.bse["post"])
    ci = m.conf_int().loc["post"]
    # equivalencia frente a 18: ¿podemos descartar un escalón ≥18? (test unilateral)
    z18 = (18 - b) / se
    p_eq18 = float(stats.norm.cdf(-z18))          # H0: escalón ≥18
    # y frente a un margen clínicamente trivial de 5 puntos
    z5 = (5 - b) / se
    p_eq5 = float(stats.norm.cdf(-z5))
    R["falsacion"][nm] = {"escalon": round(b, 2), "ee": round(se, 2),
                          "ic95": [round(float(ci[0]), 2), round(float(ci[1]), 2)],
                          "p": float(m.pvalues["post"]),
                          "p_equivalencia_vs_18": p_eq18, "p_equivalencia_vs_5": p_eq5}
    print(f"  {nm:<13} escalón {b:+.2f} (EE {se:.2f}) IC95 [{ci[0]:+.2f}, {ci[1]:+.2f}] p={m.pvalues['post']:.3f}")
    print(f"                se descarta un escalón ≥18: p={p_eq18:.2e}  |  ≥5 puntos: p={p_eq5:.4f}")

print("\n  regresión discontinua local:")
R["rd_local"] = {}
for w in [(10, 13), (9, 14), (8, 15)]:
    for nm, d in COH:
        s = d[d.edu.between(*w)].copy(); s["post"] = (s.edu >= 12).astype(int)
        m = smf.ols("ACE ~ edu + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
        ci = m.conf_int().loc["post"]
        R["rd_local"][f"{nm}_{w[0]}-{w[1]}"] = {"n": int(len(s)), "b": round(float(m.params["post"]), 2),
                                                "ic95": [round(float(ci[0]), 2), round(float(ci[1]), 2)],
                                                "p": float(m.pvalues["post"])}
        print(f"    {str(w):<9} {nm:<13} n={len(s):<5} {m.params['post']:+.2f} "
              f"[{ci[0]:+.2f},{ci[1]:+.2f}] p={m.pvalues['post']:.3f}")

print("\n  diferencia cruda 11 vs 12 años:")
R["crudo"] = {}
for nm, d in COH:
    a, b_ = d[d.edu == 11].ACE, d[d.edu == 12].ACE
    dif = b_.mean() - a.mean()
    se = np.sqrt(a.var(ddof=1)/len(a) + b_.var(ddof=1)/len(b_))
    R["crudo"][nm] = {"n11": int(len(a)), "n12": int(len(b_)), "dif": round(float(dif), 2),
                      "ic95": [round(float(dif-1.96*se), 2), round(float(dif+1.96*se), 2)]}
    print(f"    {nm:<13} n(11)={len(a):<4} n(12)={len(b_):<5} {dif:+.2f} [{dif-1.96*se:+.2f}, {dif+1.96*se:+.2f}]")

# ==================================================================== C. FORMA Y REPLICACIÓN
print("\n" + "=" * 96 + "\nC. FORMA DE LA ASOCIACIÓN Y REPLICACIÓN")
R["forma"] = {}
for nm, d in COH:
    lin = smf.ols("ACE ~ edu + Edad + C(Sexo)", data=d).fit()
    qua = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    mq = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    ml = smf.ols("ACE ~ edu + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    sp = dmatrix("cr(edu, df=4) - 1", d, return_type="dataframe")
    sp.columns = [f"s{i}" for i in range(sp.shape[1])]
    spl = smf.ols("ACE ~ " + " + ".join(sp.columns) + " + Edad + C(Sexo)",
                  data=pd.concat([d.reset_index(drop=True), sp.reset_index(drop=True)], axis=1)).fit()
    nmp = list(mq.params.index); i1, i2 = nmp.index("edu"), nmp.index("I(edu ** 2)")
    V = np.asarray(mq.cov_params()); b1, b2 = mq.params.iloc[i1], mq.params.iloc[i2]
    ci2 = mq.conf_int().loc["I(edu ** 2)"]
    marg = {}
    for e in (3, 7, 12, 17):
        v = np.zeros(len(nmp)); v[i1] = 1; v[i2] = 2*e
        est = float(b1 + 2*b2*e); se = float(np.sqrt(v @ V @ v))
        marg[str(e)] = {"b": round(est, 2), "ic95": [round(est-1.96*se, 2), round(est+1.96*se, 2)]}
    lr = lambda m0, m1: {"chi2": round(2*(m1.llf-m0.llf), 2), "df": int(m1.df_model-m0.df_model),
                         "p": float(stats.chi2.sf(2*(m1.llf-m0.llf), max(int(m1.df_model-m0.df_model), 1)))}
    R["forma"][nm] = {"n": int(len(d)),
                      "lineal": {"b": round(float(ml.params["edu"]), 3),
                                 "ic95": [round(x, 3) for x in ml.conf_int().loc["edu"].tolist()]},
                      "b2": {"b": round(float(b2), 4), "ic95": [round(float(ci2[0]), 4), round(float(ci2[1]), 4)],
                             "p": float(mq.pvalues["I(edu ** 2)"])},
                      "AIC": {"lin": round(lin.aic, 1), "cuad": round(qua.aic, 1), "spline": round(spl.aic, 1)},
                      "cuad_vs_lin": lr(lin, qua), "spline_vs_cuad": lr(qua, spl), "marginal": marg}
    f = R["forma"][nm]
    print(f"  {nm:<13} n={f['n']:<5} b2={f['b2']['b']} {f['b2']['ic95']} p={f['b2']['p']:.2e}")
    print(f"       marginal: " + "  ".join(f"{k}a:{v['b']}[{v['ic95'][0]},{v['ic95'][1]}]" for k, v in marg.items()))
    print(f"       AIC lin/cuad/spl {f['AIC']['lin']}/{f['AIC']['cuad']}/{f['AIC']['spline']}  "
          f"cuad>lin p={f['cuad_vs_lin']['p']:.2e}  spl>cuad p={f['spline_vs_cuad']['p']:.3f}")

F_full = "ACE ~ (edu + I(edu**2))*C(cohorte) + Edad + C(Sexo)"
F_lin = "ACE ~ edu*C(cohorte) + I(edu**2) + Edad + C(Sexo)"
F_com = "ACE ~ edu + I(edu**2) + C(cohorte) + Edad + C(Sexo)"
lrt = lambda m0, m1: {"chi2": round(2*(m1.llf-m0.llf), 2), "df": int(m1.df_model-m0.df_model),
                      "p": float(stats.chi2.sf(2*(m1.llf-m0.llf), max(int(m1.df_model-m0.df_model), 1)))}
mf = smf.ols(F_full, data=D).fit(cov_type="HC3")
k2 = [i for i in mf.params.index if i.startswith("I(edu ** 2):")][0]
R["replicacion"] = {"forma": lrt(smf.ols(F_com, data=D).fit(), smf.ols(F_full, data=D).fit()),
                    "curvatura": lrt(smf.ols(F_lin, data=D).fit(), smf.ols(F_full, data=D).fit()),
                    "lineal": lrt(smf.ols(F_com, data=D).fit(), smf.ols(F_lin, data=D).fit()),
                    "contraste_b2": {"dif": round(float(mf.params[k2]), 4),
                                     "ic95": [round(x, 4) for x in mf.conf_int().loc[k2].tolist()],
                                     "p": float(mf.pvalues[k2])}}
print(f"\n  replicación: forma p={R['replicacion']['forma']['p']:.2e} | "
      f"lineal p={R['replicacion']['lineal']['p']:.2e} | CURVATURA p={R['replicacion']['curvatura']['p']:.3f}")
print(f"  contraste de curvatura: {R['replicacion']['contraste_b2']['dif']} "
      f"{R['replicacion']['contraste_b2']['ic95']} p={R['replicacion']['contraste_b2']['p']:.3f}")

# ==================================================================== D. POSITIVIDAD
print("\n" + "=" * 96 + "\nD. POSITIVIDAD DE LA REGLA VIGENTE, AÑO POR AÑO")
R["positividad"] = {}
for nm, d in COH:
    d = d.copy(); d["P2"] = np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68)
    t = d[d.edu.between(0, 18)].groupby("edu").P2.agg(["size", "mean"])
    t = t[t["size"] >= 10]
    R["positividad"][nm] = {int(a): {"n": int(v["size"]), "pct": round(100*float(v["mean"]), 1)}
                            for a, v in t.iterrows()}
    print(f"  {nm}: " + " · ".join(f"{int(a)}a {100*v['mean']:.0f}%(n={int(v['size'])})" for a, v in t.iterrows()))
    p11 = R["positividad"][nm].get(11); p12 = R["positividad"][nm].get(12)
    if p11 and p12:
        R["positividad"][nm]["salto_veces"] = round(p12["pct"]/max(p11["pct"], .1), 1)
        print(f"     salto 11→12: {p11['pct']}% → {p12['pct']}%  ({R['positividad'][nm]['salto_veces']}×)")
    tt = d.groupby(TR(d), observed=True).P2.agg(["size", "mean"])
    R["positividad"][nm]["por_tramo"] = {str(a): round(100*float(v["mean"]), 1) for a, v in tt.iterrows()}
    print(f"     por tramo: {R['positividad'][nm]['por_tramo']}")

# ==================================================================== E. TEST-RETEST
print("\n" + "=" * 96 + "\nE. VARIABILIDAD TEST-RETEST DEL ACE-III (subgrupo clínico reevaluado)")
lon = pd.read_csv(NM / "analisis/ace_items_clinico_v2_longitudinal.csv")
lon["f"] = pd.to_datetime(lon.fecha_ev, errors="coerce", format="ISO8601")
lon = lon.dropna(subset=["f", "ACE_total"]).sort_values(["persona_id", "f"])
pares = []
for pid, g in lon.groupby("persona_id"):
    g = g.reset_index(drop=True)
    for i in range(len(g) - 1):
        dt = (g.f[i+1] - g.f[i]).days
        if dt > 0:
            pares.append({"persona_id": pid, "t1": g.ACE_total[i], "t2": g.ACE_total[i+1],
                          "dias": dt, "edu": g.ed_anos_completos[i] if "ed_anos_completos" in g else np.nan,
                          "Edad": g.Edad[i] if "Edad" in g else np.nan})
P = pd.DataFrame(pares)
print(f"  pares consecutivos: {len(P)}  de {P.persona_id.nunique()} personas")
print(f"  intervalo de retest: mediana {P.dias.median():.0f} días "
      f"[Q1–Q3 {P.dias.quantile(.25):.0f}–{P.dias.quantile(.75):.0f}; rango {P.dias.min():.0f}–{P.dias.max():.0f}]")
dif = P.t2 - P.t1
r_tt = float(P.t1.corr(P.t2))
# ICC(A,1) por componentes de varianza
gm = np.concatenate([P.t1.values, P.t2.values]).mean()
msb = 2*((P[["t1", "t2"]].mean(axis=1) - gm)**2).sum()/(len(P)-1)
msw = ((P.t1 - P[["t1", "t2"]].mean(axis=1))**2 + (P.t2 - P[["t1", "t2"]].mean(axis=1))**2).sum()/len(P)
icc = float((msb - msw)/(msb + msw))
sd_dif = float(dif.std(ddof=1))
sem = sd_dif/np.sqrt(2)                 # error estándar de medición
rci = 1.96*sd_dif                       # cambio mínimo detectable (95%)
print(f"  correlación test-retest r={r_tt:.3f}   |   coeficiente de correlación intraclase={icc:.3f}")
print(f"  cambio medio {dif.mean():+.2f} puntos (DE {sd_dif:.2f})")
print(f"  ERROR ESTÁNDAR DE MEDICIÓN = {sem:.2f} puntos")
print(f"  CAMBIO MÍNIMO DETECTABLE (95%) = ±{rci:.1f} puntos")
print(f"  -> el escalón de la regla (18 puntos) equivale a {18/sem:.1f} errores estándar de medición")
R["test_retest"] = {"n_pares": int(len(P)), "n_personas": int(P.persona_id.nunique()),
                    "dias_mediana": float(P.dias.median()),
                    "dias_q1": float(P.dias.quantile(.25)), "dias_q3": float(P.dias.quantile(.75)),
                    "r": round(r_tt, 3), "icc": round(icc, 3),
                    "cambio_medio": round(float(dif.mean()), 2), "de_cambio": round(sd_dif, 2),
                    "sem": round(float(sem), 2), "cambio_min_detectable": round(float(rci), 1),
                    "escalon_en_sem": round(18/float(sem), 1)}
if P.edu.notna().sum() > 50:
    P["tr"] = pd.cut(P.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
    t = P.groupby("tr", observed=True).apply(lambda g: pd.Series({
        "n": len(g), "DE_cambio": round(float((g.t2-g.t1).std(ddof=1)), 2),
        "EEM": round(float((g.t2-g.t1).std(ddof=1)/np.sqrt(2)), 2)}))
    print("\n  por tramo educativo:"); print(t.to_string())
    R["test_retest"]["por_tramo"] = t.reset_index().to_dict("records")

# ==================================================================== F. SENSIBILIDADES
print("\n" + "=" * 96 + "\nF. SENSIBILIDADES (curvatura b₂)")
def b2(d, y="ACE"):
    m = smf.ols(f"{y} ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    return {"n": int(len(d)), "b2": round(float(m.params["I(edu ** 2)"]), 4),
            "p": float(m.pvalues["I(edu ** 2)"])}
S = {"principal": {"comunitaria": b2(com), "clínica": b2(cli)},
     "sin armonizar": {"comunitaria": b2(com, "ACE_orig")},
     "columna del instrumento": {"comunitaria": b2(com.dropna(subset=["ACE_col"]).assign(ACE=lambda x: x.ACE_col))},
     "ajuste por ola": {"comunitaria": {"b2": round(float(smf.ols(
         "ACE ~ edu + I(edu**2) + Edad + C(Sexo) + C(ola)", data=com).fit(cov_type="HC3")
         .params["I(edu ** 2)"]), 4)}},
     "sin techo (<95)": {"comunitaria": b2(com[com.ACE < 95]), "clínica": b2(cli[cli.ACE < 95])},
     "edad 46-85": {"comunitaria": b2(com[com.Edad.between(46, 85)]), "clínica": b2(cli[cli.Edad.between(46, 85)])},
     "educación ≤18": {"comunitaria": b2(com[com.edu <= 18]), "clínica": b2(cli[cli.edu <= 18])}}
if "estado" in cli.columns:
    S["sólo ítems validados"] = {"clínica": b2(cli[cli.estado == "items_validados"])}
for lab, v in S.items():
    print(f"  {lab:<26} " + "  ".join(f"{k}: b2={x['b2']}" + (f" (n={x['n']})" if "n" in x else "")
                                      for k, x in v.items()))
R["sensibilidades"] = S
y, Xd = dmatrices("ACE ~ edu + I(edu**2) + Edad + C(Sexo) + C(cohorte)", data=D, return_type="dataframe")
bp = het_breuschpagan(sm.OLS(y, Xd).fit().resid, Xd)
R["breusch_pagan_p"] = float(bp[1])
print(f"  Breusch-Pagan p={bp[1]:.3g} (HC3 justificado)")

(OUT / "V2_reproduccion.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> {OUT/'V2_reproduccion.json'}")
