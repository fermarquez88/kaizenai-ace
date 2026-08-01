#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
REENCUADRE — el entregable es la FALSACIÓN del escalón, no una propuesta de corte.

Motivo del cambio (auditoría): el corte continuo estaba anclado a 86 en la mediana educativa del
grupo ≥12 años, donde el ACE-III esperado es 86,3. El "corte" quedaba así a 0,3 puntos de la media
condicional (z≈0), de modo que aplanar la positividad es una propiedad mecánica del anclaje y no
evidencia de calibración. El anclaje es además un parámetro libre con mucha palanca.

Lo que sí es robusto y no depende de anclaje, punto de operación ni forma funcional: **no existe
discontinuidad en 12 años**. Este script produce el análisis principal nuevo y todas las
verificaciones que la auditoría exigió.

Salida: consola + out/31_falsacion.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from patsy import dmatrix

warnings.filterwarnings("ignore")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
R = {}
rng = np.random.default_rng(7)

com = pd.read_csv(NM / "analisis/comunitaria_armonizada.csv")
cli = (pd.read_csv(NM / "analisis/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
       .dropna(subset=["ACE", "edu", "Edad", "Sexo"]))
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
COH = [("comunitaria", com), ("clínica", cli)]
TR = lambda d: pd.cut(d.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])

# ==================================================================== 1. FALSACIÓN
print("=" * 96)
print("1. ¿EXISTE LA DISCONTINUIDAD QUE LA REGLA SUPONE? (análisis principal)")
R["discontinuidad"] = {}
for nm, d in COH:
    d = d.copy(); d["post"] = (d.edu >= 12).astype(int)
    m = smf.ols("ACE ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    ci = m.conf_int().loc["post"]
    R["discontinuidad"][nm] = {"escalon": round(float(m.params["post"]), 2),
                              "ic95": [round(float(ci[0]), 2), round(float(ci[1]), 2)],
                              "p": float(m.pvalues["post"])}
    print(f"  {nm:<13} escalón estimado {m.params['post']:+.2f}  IC95 [{ci[0]:+.2f}, {ci[1]:+.2f}]  "
          f"p={m.pvalues['post']:.3f}   (la regla salta 18)")
print("\n  regresión discontinua local (ventanas alrededor de 12):")
R["rd_local"] = {}
for w in [(10, 13), (9, 14), (8, 15)]:
    for nm, d in COH:
        s = d[d.edu.between(*w)].copy(); s["post"] = (s.edu >= 12).astype(int)
        m = smf.ols("ACE ~ edu + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
        ci = m.conf_int().loc["post"]
        R["rd_local"][f"{nm}_{w[0]}-{w[1]}"] = {"n": int(len(s)), "escalon": round(float(m.params["post"]), 2),
                                                "ic95": [round(float(ci[0]), 2), round(float(ci[1]), 2)],
                                                "p": float(m.pvalues["post"])}
        print(f"    {str(w):<9} {nm:<13} n={len(s):<5} {m.params['post']:+.2f} "
              f"[{ci[0]:+.2f},{ci[1]:+.2f}] p={m.pvalues['post']:.3f}")
print("\n  diferencia CRUDA 11 vs 12 años (sin modelo):")
R["crudo_11_12"] = {}
for nm, d in COH:
    a, b = d[d.edu == 11].ACE, d[d.edu == 12].ACE
    dif = b.mean() - a.mean()
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    R["crudo_11_12"][nm] = {"n11": int(len(a)), "n12": int(len(b)), "dif": round(float(dif), 2),
                            "ic95": [round(float(dif-1.96*se), 2), round(float(dif+1.96*se), 2)]}
    print(f"    {nm:<13} n(11)={len(a):<4} n(12)={len(b):<5} dif {dif:+.2f} "
          f"[{dif-1.96*se:+.2f}, {dif+1.96*se:+.2f}]")

# ---- efecto credencial en 7 y 12
print("\n  ¿hay efecto credencial (sheepskin) en 7 o en 12 años?")
R["credencial"] = {}
for nm, d in COH:
    d = d.copy(); d["c7"] = (d.edu >= 7).astype(int); d["c12"] = (d.edu >= 12).astype(int)
    m = smf.ols("ACE ~ edu + I(edu**2) + c7 + c12 + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    R["credencial"][nm] = {k: {"b": round(float(m.params[k]), 2), "p": float(m.pvalues[k])}
                           for k in ("c7", "c12")}
    print(f"    {nm:<13} primaria completa (≥7): {m.params['c7']:+.2f} p={m.pvalues['c7']:.3f} | "
          f"secundaria completa (≥12): {m.params['c12']:+.2f} p={m.pvalues['c12']:.3f}")

# ==================================================================== 2. POSITIVIDAD POR AÑO
print("\n" + "=" * 96)
print("2. POSITIVIDAD DE LA REGLA VIGENTE, AÑO POR AÑO (la figura principal)")
R["positividad_anual"] = {}
for nm, d in COH:
    d = d.copy(); d["P2"] = np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68)
    t = d[d.edu.between(0, 18)].groupby("edu").P2.agg(["size", "mean"])
    t = t[t["size"] >= 10]
    R["positividad_anual"][nm] = {int(k): {"n": int(v["size"]), "pct": round(100*float(v["mean"]), 1)}
                                  for k, v in t.iterrows()}
    print(f"  {nm}: " + " · ".join(f"{int(k)}a {100*v['mean']:.0f}%(n={int(v['size'])})"
                                   for k, v in t.iterrows()))
    a = R["positividad_anual"][nm].get(11); b = R["positividad_anual"][nm].get(12)
    if a and b:
        print(f"     salto 11→12: {a['pct']}% → {b['pct']}%  ({b['pct']/max(a['pct'],0.1):.1f}×)")
        R["positividad_anual"][nm]["salto_11_12_veces"] = round(b["pct"]/max(a["pct"], 0.1), 1)

# ==================================================================== 3. AUTOCRÍTICA DEL CORTE CONTINUO
print("\n" + "=" * 96)
print("3. LÍMITES DEL CORTE CONTINUO (autocrítica que hay que publicar)")


def corte_de(d, forma, ancla_edu=None):
    f = {"cuadrática": "ACE ~ edu + I(edu**2) + Edad + C(Sexo)",
         "lineal": "ACE ~ edu + Edad + C(Sexo)",
         "log": "ACE ~ np.log(edu+1) + Edad + C(Sexo)"}[forma]
    m = smf.ols(f, data=d).fit()
    ref = ancla_edu if ancla_edu is not None else d.loc[d.edu >= 12, "edu"].median()
    e_ref = float(m.predict(pd.DataFrame({"edu": [ref], "Edad": [d.Edad.mean()], "Sexo": ["Mujer"]})).iloc[0])
    pr = pd.DataFrame({"edu": d.edu, "Edad": d.Edad.mean(), "Sexo": "Mujer"})
    return 86 - (e_ref - m.predict(pr).values), e_ref, ref


print("\n  3a. El corte queda en la media condicional -> aplanar es mecánico")
R["ancla_z"] = {}
for nm, d in COH:
    corte, e_ref, ref = corte_de(d, "cuadrática")
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    sd = float(np.sqrt(m.mse_resid)); c = 86 - e_ref
    R["ancla_z"][nm] = {"ancla_edu": float(ref), "E_ACE_ancla": round(e_ref, 2),
                        "c": round(c, 2), "z": round(c/sd, 2)}
    print(f"    {nm:<13} ancla edu={ref:.0f}  E[ACE]={e_ref:.2f}  c={c:+.2f}  z={c/sd:+.2f}")

print("\n  3b. El aplanamiento no identifica la forma funcional")
R["formas"] = {}
for nm, d in COH:
    fila = {}
    for forma in ["cuadrática", "lineal", "log"]:
        corte, *_ = corte_de(d, forma)
        pos = d.assign(P=(d.ACE < corte)).groupby(TR(d), observed=True).P.mean()*100
        fila[forma] = round(float(pos.max()-pos.min()), 1)
    p2 = d.assign(P=np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68)).groupby(TR(d), observed=True).P.mean()*100
    fila["escalón vigente"] = round(float(p2.max()-p2.min()), 1)
    R["formas"][nm] = fila
    print(f"    {nm:<13} rango de positividad entre tramos (pp): {fila}")

print("\n  3c. El anclaje es un parámetro libre con mucha palanca")
R["anclaje"] = {}
for nm, d in COH:
    fila = {}
    for a in [12, 13.2, None, 17]:
        corte, e_ref, ref = corte_de(d, "cuadrática", a)
        fila[f"ancla={ref:.1f}"] = round(100*float((d.ACE < corte).mean()), 1)
    R["anclaje"][nm] = fila
    print(f"    {nm:<13} positividad global según anclaje: {fila}")

print("\n  3d. Validación cruzada 10-fold: NO hay sobreajuste")
R["vc"] = {}
for nm, d in COH:
    idx = rng.permutation(len(d)); folds = np.array_split(idx, 10)
    pred = np.zeros(len(d), dtype=bool)
    for f in folds:
        tr = d.drop(d.index[f]); te = d.iloc[f]
        m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=tr).fit()
        ref = tr.loc[tr.edu >= 12, "edu"].median()
        e_ref = float(m.predict(pd.DataFrame({"edu": [ref], "Edad": [tr.Edad.mean()], "Sexo": ["Mujer"]})).iloc[0])
        c = 86 - (e_ref - m.predict(pd.DataFrame({"edu": te.edu, "Edad": tr.Edad.mean(), "Sexo": "Mujer"})).values)
        pred[f] = (te.ACE.values < c)
    corte, *_ = corte_de(d, "cuadrática")
    dentro = (d.ACE < corte).values
    R["vc"][nm] = {"dentro_pct": round(100*float(dentro.mean()), 1),
                   "fuera_pct": round(100*float(pred.mean()), 1),
                   "discordancia_pct": round(100*float((dentro != pred).mean()), 2)}
    print(f"    {nm:<13} en muestra {100*dentro.mean():.1f}%  fuera de muestra {100*pred.mean():.1f}%  "
          f"discordancia individual {100*(dentro!=pred).mean():.2f}%")

print("\n  3e. La curva NO transfiere entre cohortes")
mc = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=com).fit()
ml = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=cli).fit()
g = np.array([0, 2, 4, 7, 9, 11, 12, 15, 17])
cc = 86 - (float(mc.predict(pd.DataFrame({"edu": [15], "Edad": [com.Edad.mean()], "Sexo": ["Mujer"]})).iloc[0])
           - mc.predict(pd.DataFrame({"edu": g, "Edad": com.Edad.mean(), "Sexo": "Mujer"})).values)
kl = 86 - (float(ml.predict(pd.DataFrame({"edu": [15], "Edad": [cli.Edad.mean()], "Sexo": ["Mujer"]})).iloc[0])
           - ml.predict(pd.DataFrame({"edu": g, "Edad": cli.Edad.mean(), "Sexo": "Mujer"})).values)
R["transferencia"] = {"edu": g.tolist(), "comunitaria": [round(float(x), 1) for x in cc],
                      "clinica": [round(float(x), 1) for x in kl],
                      "dif_max": round(float(np.abs(cc-kl).max()), 1)}
print("    edu :", "  ".join(f"{int(e):>5}" for e in g))
print("    comu:", "  ".join(f"{x:>5.1f}" for x in cc))
print("    clin:", "  ".join(f"{x:>5.1f}" for x in kl))
print("    dif :", "  ".join(f"{x:>+5.1f}" for x in cc-kl), f"  -> máx {np.abs(cc-kl).max():.1f} pts")

# ==================================================================== 4. COMPARACIÓN JUSTA
print("\n" + "=" * 96)
print("4. COMPARACIÓN A TASA GLOBAL IGUALADA (la única comparación justa)")
R["tasa_igualada"] = {}
for nm, d in COH:
    p2 = np.where(d.edu >= 12, d.ACE < 86, d.ACE < 68)
    tasa = p2.mean()
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    resid = d.ACE - m.predict(d)
    umbral = np.quantile(resid, tasa)
    p3 = (resid < umbral).values
    t2 = pd.Series(p2).groupby(TR(d).values, observed=True).mean()*100
    t3 = pd.Series(p3).groupby(TR(d).values, observed=True).mean()*100
    R["tasa_igualada"][nm] = {"tasa_global": round(100*float(tasa), 1),
                             "P2": {str(k): round(float(v), 1) for k, v in t2.items()},
                             "P3": {str(k): round(float(v), 1) for k, v in t3.items()},
                             "rango_P2": round(float(t2.max()-t2.min()), 1),
                             "rango_P3": round(float(t3.max()-t3.min()), 1),
                             "reclasificacion": round(100*float((p2 != p3).mean()), 1)}
    print(f"  {nm} (tasa global igualada en {100*tasa:.1f}%)")
    print(f"    escalón vigente : " + " · ".join(f"{k} {v:.1f}%" for k, v in t2.items()) +
          f"   -> rango {t2.max()-t2.min():.1f} pp")
    print(f"    corte continuo  : " + " · ".join(f"{k} {v:.1f}%" for k, v in t3.items()) +
          f"   -> rango {t3.max()-t3.min():.1f} pp")
    print(f"    reclasificación : {100*(p2!=p3).mean():.1f}%")

# ==================================================================== 5. ESCALA
print("\n" + "=" * 96)
print("5. LA VARIANZA TAMBIÉN DEPENDE DE LA EDUCACIÓN (corrección de localización-escala)")
R["escala"] = {}
for nm, d in COH:
    m = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    r = d.ACE - m.predict(d)
    ms = smf.ols("np.log(r2) ~ edu", data=d.assign(r2=np.maximum(r**2, 1e-6))).fit()
    sd = {int(e): round(float(np.exp(0.5*(ms.params["Intercept"] + ms.params["edu"]*e))), 1)
          for e in [2, 7, 12, 17]}
    porq = r.groupby(TR(d).values, observed=True).std().round(1).to_dict()
    R["escala"][nm] = {"sd_modelada": sd, "sd_por_tramo": {str(k): float(v) for k, v in porq.items()},
                       "p_edu": float(ms.pvalues["edu"])}
    print(f"  {nm:<13} DE residual modelada: {sd}  (p educación={ms.pvalues['edu']:.2g})")
    print(f"                DE por tramo observada: {porq}")

# ==================================================================== 6. ANCLA DE 86
print("\n" + "=" * 96)
print("6. ¿EL ANCLA DE 86 TRANSPORTA A ESTA POBLACIÓN?")
R["ancla86"] = {}
for nm, d in COH:
    a = 100*float((d[d.edu >= 12].ACE < 86).mean())
    b = 100*float((d[(d.edu >= 15) & (d.Edad <= 65)].ACE < 86).mean())
    R["ancla86"][nm] = {"pct_lt86_ge12": round(a, 1), "pct_lt86_ge15_le65": round(b, 1),
                        "n_ge15_le65": int(((d.edu >= 15) & (d.Edad <= 65)).sum())}
    print(f"  {nm:<13} % <86 entre ≥12 años: {a:.1f}%   |  entre ≥15 años y ≤65: {b:.1f}% "
          f"(n={int(((d.edu>=15)&(d.Edad<=65)).sum())})")
print("  Bruno reporta especificidad 82% -> ~18% de positivos esperados entre sanos.")

(OUTD / "31_falsacion.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> {OUTD/'31_falsacion.json'}")
