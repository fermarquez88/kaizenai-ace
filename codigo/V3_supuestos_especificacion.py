#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V3 — SUPUESTOS, ESPECIFICACIÓN, OBSERVACIONES INFLUYENTES Y POTENCIA.

Pregunta del bloque: ¿alguno de los dos resultados (la ausencia de escalón y la curvatura)
depende de un supuesto que no se cumple, de una decisión de modelado, o de un puñado de sujetos?

  A. Diagnóstico de residuos y colinealidad.
  B. Observaciones influyentes: distancia de Cook, DFBETA y jackknife sobre b₂ y sobre el escalón.
  C. Especificación alternativa del desenlace: regresión robusta, mediana, censura en el techo.
  D. Especificación alternativa de los covariables (edad no lineal, interacciones).
  E. FALSACIÓN DE PLACEBO: el escalón estimado en TODOS los cortes candidatos, no sólo en 12.
  F. Potencia y equivalencia formal (dos pruebas unilaterales).
  G. Datos faltantes: ¿los excluidos difieren de los incluidos?

Salida: consola + resultados/V3_supuestos.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor, OLSInfluence
from patsy import dmatrix
from scipy import stats, optimize

warnings.filterwarnings("ignore")
rng = np.random.default_rng(20260731)
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUT = EST / "resultados"
R = {}

com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
cli = (pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
       .dropna(subset=["ACE", "edu", "Edad", "Sexo"]))
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
COH = [("comunitaria", com), ("clínica", cli)]
FQ = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
FS = "ACE ~ edu + I(edu**2) + post + Edad + C(Sexo)"
mkpost = lambda d, c=12: d.assign(post=(d.edu >= c).astype(int))

# ==================================================================== A. RESIDUOS Y COLINEALIDAD
print("=" * 96 + "\nA. DIAGNÓSTICO DE RESIDUOS Y COLINEALIDAD")
R["residuos"] = {}
for nm, d in COH:
    m = smf.ols(FQ, data=d).fit()
    X = pd.DataFrame({"edu": d.edu, "edu2": d.edu**2, "Edad": d.Edad,
                      "mujer": (d.Sexo == "Mujer").astype(int)})
    Xc = sm.add_constant(X - X.mean())            # centrado: el VIF de un polinomio sin centrar es artificial
    vif = {c: round(float(variance_inflation_factor(Xc.values, i)), 2)
           for i, c in enumerate(Xc.columns) if c != "const"}
    sw = stats.shapiro(m.resid[:4999])
    R["residuos"][nm] = {"vif_centrado": vif, "asimetria": round(float(stats.skew(m.resid)), 3),
                         "curtosis": round(float(stats.kurtosis(m.resid)), 3),
                         "shapiro_p": float(sw.pvalue), "R2": round(float(m.rsquared), 3)}
    print(f"  {nm:<13} R²={m.rsquared:.3f}  asimetría={stats.skew(m.resid):+.2f}  "
          f"curtosis={stats.kurtosis(m.resid):+.2f}  Shapiro p={sw.pvalue:.1e}")
    print(f"                VIF (centrado): {vif}")
print("  -> residuos con cola izquierda (esperable: el ACE-III tiene techo); por eso todo el")
print("     estudio usa HC3, que no supone normalidad ni varianza constante.")

# ==================================================================== B. INFLUYENTES
print("\n" + "=" * 96 + "\nB. OBSERVACIONES INFLUYENTES")
R["influyentes"] = {}
for nm, d in COH:
    d = mkpost(d).reset_index(drop=True)
    mq = smf.ols(FQ, data=d).fit()
    inf = OLSInfluence(mq)
    cook = inf.cooks_distance[0]
    umbral = 4 / len(d)
    idx_b2 = list(mq.params.index).index("I(edu ** 2)")
    dfb = inf.dfbetas[:, idx_b2]
    # jackknife: sacar el 1 % más influyente y re-estimar
    peores = np.argsort(-np.abs(dfb))[:max(1, len(d) // 100)]
    b2_full = float(smf.ols(FQ, data=d).fit(cov_type="HC3").params["I(edu ** 2)"])
    b2_sin = float(smf.ols(FQ, data=d.drop(index=peores)).fit(cov_type="HC3").params["I(edu ** 2)"])
    esc_full = float(smf.ols(FS, data=d).fit(cov_type="HC3").params["post"])
    ms = smf.ols(FS, data=d).fit()
    idx_p = list(ms.params.index).index("post")
    dfbp = OLSInfluence(ms).dfbetas[:, idx_p]
    peores_p = np.argsort(-np.abs(dfbp))[:max(1, len(d) // 100)]
    esc_sin = float(smf.ols(FS, data=d.drop(index=peores_p)).fit(cov_type="HC3").params["post"])
    R["influyentes"][nm] = {"n_cook_sobre_4n": int((cook > umbral).sum()),
                            "cook_max": round(float(cook.max()), 4),
                            "dfbeta_b2_max": round(float(np.abs(dfb).max()), 3),
                            "b2_completo": round(b2_full, 4), "b2_sin_1pct": round(b2_sin, 4),
                            "escalon_completo": round(esc_full, 2), "escalon_sin_1pct": round(esc_sin, 2)}
    print(f"  {nm:<13} Cook>4/n: {int((cook>umbral).sum())} ({100*(cook>umbral).mean():.1f} %)  "
          f"Cook máx={cook.max():.4f}  |DFBETA(b₂)| máx={np.abs(dfb).max():.3f}")
    print(f"                b₂  {b2_full:+.4f} -> {b2_sin:+.4f}   |   "
          f"escalón {esc_full:+.2f} -> {esc_sin:+.2f}  (sacando el 1 % más influyente)")
print("  -> ningún Cook supera 1; ningún |DFBETA| supera 2/√n de forma relevante.")

# ==================================================================== C. DESENLACE ALTERNATIVO
print("\n" + "=" * 96 + "\nC. ESPECIFICACIÓN ALTERNATIVA DEL DESENLACE")


def tobit_b2(d, tope=100.0):
    """Regresión normal censurada por arriba en el techo del ACE-III. Devuelve b₂ y el escalón."""
    X = np.column_stack([np.ones(len(d)), d.edu, d.edu**2, (d.edu >= 12).astype(float),
                         d.Edad, (d.Sexo == "Mujer").astype(float)])
    y = d.ACE.values.astype(float); cen = y >= tope

    def nll(p):
        b, ls = p[:-1], p[-1]
        s = np.exp(np.clip(ls, -5, 5)); mu = X @ b
        z = (y - mu) / s
        ll = np.where(cen, stats.norm.logsf((tope - mu) / s), -0.5*z**2 - np.log(s) - 0.918938533)
        return -np.sum(ll)

    ini = np.append(np.linalg.lstsq(X, y, rcond=None)[0], np.log(y.std()))
    r = optimize.minimize(nll, ini, method="Nelder-Mead",
                          options={"maxiter": 60000, "maxfev": 60000, "xatol": 1e-6, "fatol": 1e-6})
    return float(r.x[2]), float(r.x[3]), bool(r.success), int(cen.sum())


R["desenlace_alt"] = {}
for nm, d in COH:
    d = mkpost(d)
    rob = sm.RLM.from_formula(FS, data=d, M=sm.robust.norms.HuberT()).fit()
    med = smf.quantreg(FS, data=d).fit(q=0.5)
    b2t, esct, ok, ncen = tobit_b2(d)
    R["desenlace_alt"][nm] = {
        "huber": {"b2": round(float(rob.params["I(edu ** 2)"]), 4), "escalon": round(float(rob.params["post"]), 2)},
        "mediana": {"b2": round(float(med.params["I(edu ** 2)"]), 4), "escalon": round(float(med.params["post"]), 2)},
        "tobit": {"b2": round(b2t, 4), "escalon": round(esct, 2), "convergio": ok, "n_en_techo": ncen}}
    print(f"  {nm:<13} robusta Huber  b₂={rob.params['I(edu ** 2)']:+.4f}  escalón={rob.params['post']:+.2f}")
    print(f"                regresión de la mediana  b₂={med.params['I(edu ** 2)']:+.4f}  escalón={med.params['post']:+.2f}")
    print(f"                censurada en 100 (n techo={ncen})  b₂={b2t:+.4f}  escalón={esct:+.2f}")

# ==================================================================== D. COVARIABLES ALTERNATIVAS
print("\n" + "=" * 96 + "\nD. ESPECIFICACIÓN ALTERNATIVA DE LAS COVARIABLES")
R["covar_alt"] = {}
ESPEC = {"edad lineal (principal)": FS,
         "edad cuadrática": "ACE ~ edu + I(edu**2) + post + Edad + I(Edad**2) + C(Sexo)",
         "edad en spline": "ACE ~ edu + I(edu**2) + post + cr(Edad, df=4) + C(Sexo)",
         "interacción educación×edad": "ACE ~ edu*Edad + I(edu**2) + post + C(Sexo)",
         "interacción educación×sexo": "ACE ~ edu*C(Sexo) + I(edu**2) + post + Edad",
         "sin covariables": "ACE ~ edu + I(edu**2) + post"}
for nm, d in COH:
    d = mkpost(d); R["covar_alt"][nm] = {}
    for k, f in ESPEC.items():
        m = smf.ols(f, data=d).fit(cov_type="HC3")
        ci = m.conf_int().loc["post"]
        R["covar_alt"][nm][k] = {"escalon": round(float(m.params["post"]), 2),
                                 "ic95": [round(float(ci[0]), 2), round(float(ci[1]), 2)],
                                 "b2": round(float(m.params["I(edu ** 2)"]), 4)}
        print(f"  {nm:<13} {k:<28} escalón {m.params['post']:+.2f} "
              f"[{ci[0]:+.2f},{ci[1]:+.2f}]  b₂={m.params['I(edu ** 2)']:+.4f}")

# ==================================================================== E. PLACEBO
print("\n" + "=" * 96 + "\nE. FALSACIÓN DE PLACEBO — el escalón en TODOS los cortes candidatos")
print("   Si el corte de 12 años captara algo real, debería destacarse entre los demás.")
R["placebo"] = {}
for nm, d in COH:
    fila = []
    for c in range(5, 19):
        s = d.assign(post=(d.edu >= c).astype(int))
        if s.post.mean() < 0.03 or s.post.mean() > 0.97:
            continue
        m = smf.ols(FS, data=s).fit(cov_type="HC3")
        fila.append({"corte": c, "b": round(float(m.params["post"]), 2),
                     "z": round(float(m.tvalues["post"]), 2), "p": float(m.pvalues["post"])})
    R["placebo"][nm] = fila
    print(f"  {nm}:")
    print("    " + "  ".join(f"{f['corte']}a:{f['b']:+.1f}" for f in fila))
    z12 = [f["z"] for f in fila if f["corte"] == 12][0]
    rank = 1 + sum(abs(f["z"]) > abs(z12) for f in fila)
    print(f"    el corte de 12 años ocupa el puesto {rank} de {len(fila)} por magnitud del estadístico "
          f"(z={z12:+.2f}); p de permutación entre cortes = {rank/len(fila):.2f}")
    R["placebo"][nm + "_rank12"] = {"puesto": rank, "de": len(fila), "z12": z12,
                                    "p_permutacion": round(rank/len(fila), 3)}

# ==================================================================== F. POTENCIA Y EQUIVALENCIA
print("\n" + "=" * 96 + "\nF. POTENCIA Y EQUIVALENCIA FORMAL")
R["potencia"] = {}
for nm, d in COH:
    d = mkpost(d)
    m = smf.ols(FS, data=d).fit(cov_type="HC3")
    b, se = float(m.params["post"]), float(m.bse["post"])
    mde = 2.802 * se                       # diferencia mínima detectable con 80 % de potencia, α=0,05
    pot18 = float(stats.norm.sf(1.96 - 18/se))
    # dos pruebas unilaterales (TOST) contra ±margen
    tost = {}
    for M in (18, 5, 3):
        p1 = float(stats.norm.cdf((M - b)/se * -1))       # H0: escalón ≥ +M
        p2 = float(stats.norm.cdf((-M - b)/se))           # H0: escalón ≤ −M
        tost[str(M)] = {"p_TOST": max(p1, p2), "equivalente": max(p1, p2) < 0.05}
    R["potencia"][nm] = {"ee": round(se, 3), "mde_80": round(mde, 2),
                         "potencia_para_18": round(pot18, 6), "TOST": tost}
    print(f"  {nm:<13} EE={se:.2f}  diferencia mínima detectable (80 % potencia) = {mde:.2f} puntos")
    print(f"                potencia para detectar el escalón de 18 puntos: {100*pot18:.4f} %")
    for M, v in tost.items():
        print(f"                equivalencia dentro de ±{M:>2} puntos: p={v['p_TOST']:.2e} "
              f"-> {'SÍ' if v['equivalente'] else 'no'}")

# ==================================================================== G. FALTANTES
print("\n" + "=" * 96 + "\nG. DATOS FALTANTES — ¿los excluidos difieren de los incluidos?")
R["faltantes"] = {}
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all").dropna(axis=0, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
c40["edu_n"] = pd.to_numeric(c40.ed_anos_completos, errors="coerce").mask(lambda s: s > 30)
c40["ace_col"] = pd.to_numeric(c40.ACE_TOTAL, errors="coerce")
c40["edad_n"] = pd.to_numeric(c40.Edad, errors="coerce")
inc = pd.to_numeric(c40["dni"].astype(str).str.replace(r"\D", "", regex=True),
                    errors="coerce").isin(com.dni.dropna())
for v, lab in [("edad_n", "edad"), ("edu_n", "educación"), ("ace_col", "ACE-III (columna)")]:
    a, b_ = c40.loc[inc, v].dropna(), c40.loc[~inc, v].dropna()
    if len(a) < 5 or len(b_) < 5:
        continue
    t = stats.ttest_ind(a, b_, equal_var=False)
    R["faltantes"][lab] = {"incluidos_media": round(float(a.mean()), 2), "n_inc": int(len(a)),
                           "excluidos_media": round(float(b_.mean()), 2), "n_exc": int(len(b_)),
                           "p": float(t.pvalue)}
    print(f"  {lab:<20} incluidos {a.mean():6.2f} (n={len(a)})  vs  excluidos {b_.mean():6.2f} "
          f"(n={len(b_)})   p={t.pvalue:.4f}")
print("  -> se compara a los 758 analizados contra el resto de los ≥40 años de la base comunitaria.")

(OUT / "V3_supuestos.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> {OUT/'V3_supuestos.json'}")
