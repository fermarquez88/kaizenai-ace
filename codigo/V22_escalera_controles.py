#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V22 — Escalera acumulativa de criterios de control.

Los criterios se agregan de a uno, ordenados por su neutralidad respecto de la escolaridad: primero
los que no dependen de la exposición, al final los que sí. La queja cognitiva subjetiva va última
porque es el criterio más graduado por escolaridad de todos los disponibles (22 % contra 51 % de
independencia entre los extremos), de modo que su efecto queda aislado en el último peldaño.

En cada peldaño se reportan las dos mitades del trabajo:
  · el modelo normativo, que sólo usa controles y sostiene la tabla de esperados
  · la comparación de reglas, que usa casos y controles y sostiene el gradiente

Un mensaje robusto es el que sobrevive a los siete peldaños.

Salida: resultados/V22_escalera_controles.json + manuscrito/TablaS_escalera.md
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, duckdb
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold
from scipy import stats as st

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
IN = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
BANDAS = ["<7", "7-11", "≥12"]
BIAS = 1.2703628454614782
FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"

craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"])
num = lambda c: pd.to_numeric(craw[c], errors="coerce")
AY = ["ayuda_vestir", "ayuda_medicam", "ayuda_dinero", "ayuda_tareas"]
CB = ["cambios_mem", "cambios_orient", "cambios_leng", "cambios_organ"]
AB = ["ADLQ_Alimentarse_(A)", "ADLQ_Vestido_(A)", "ADLQ_Baño_(A)", "ADLQ_Evacuación_(A)"]
GDS = [c for c in craw.columns if str(c).startswith("Escala_Yesavage")]

def cero(cols):
    M = pd.DataFrame({c: num(c) for c in cols}).replace(9, np.nan)
    return ((M.fillna(0) == 0).all(axis=1) & (M.notna().sum(axis=1) >= len(cols) - 1))

b = pd.DataFrame({"doc": craw["doc"],
                  "rec": num("LDR_Reconocimiento_A"), "acv": num("APN_ACV"),
                  "tec": num("APN_LesionesCabeza"),
                  "gds": pd.DataFrame({c: num(c) for c in GDS}).sum(axis=1, min_count=1),
                  "abvd": cero(AB).values, "ayuda": cero(AY).values, "queja": cero(CB).values})
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv").merge(
    b, left_on="dni", right_on="doc", how="left").dropna(subset=["ACE", "edu", "Edad", "Sexo"])
com["tr"] = TR(com.edu)

con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
cl = con.execute("select eval_id, bruto rec from resultados_v2 "
                 "where test='Lista de Rey' and subtest like 'Reconoc%'").fetchdf()
cl["rec"] = pd.to_numeric(cl.rec, errors="coerce")
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv").merge(
    cl.dropna(subset=["rec"]).drop_duplicates("eval_id"), on="eval_id", how="left")
CAS = dx3[dx3.dx3 == "Demencia"][["ACE", "edu", "Edad", "Sexo"]].assign(y=1)

# ── la escalera: de más neutral a menos, con la queja al final
PELDANOS = [
    ("1 · reconocimiento de lista ≥ 10",      lambda d: d.rec >= 10),
    ("2 · sin accidente cerebrovascular",     lambda d: d.acv == 0),
    ("3 · sin traumatismo de cráneo",         lambda d: d.tec == 0),
    ("4 · independiente en ABVD",             lambda d: d.abvd == True),
    ("5 · sin sintomatología depresiva",      lambda d: d.gds <= 5),
    ("6 · sin ayuda instrumental",            lambda d: d.ayuda == True),
    ("7 · sin queja cognitiva referida",      lambda d: d.queja == True),
]

def normativo(Q):
    mu = smf.ols(FP, data=Q).fit()
    t2 = Q.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
    sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
    PM = Q.Sexo.value_counts(normalize=True).get("Mujer", 0.83)
    def esp(e, a=65):
        d = lambda s: pd.DataFrame({"edu": [e], "Edad": [a], "Sexo": [s]})
        return float(mu.predict(d("Mujer"))[0]*PM + mu.predict(d("Hombre"))[0]*(1-PM))
    def sg(e, a=65):
        return float(np.sqrt(np.exp(BIAS + sd.predict(pd.DataFrame({"edu": [e], "Edad": [a]}))[0])))
    pc = lambda e: 100*st.norm.cdf(((86 if e >= 12 else 68) - esp(e))/sg(e))
    return {"esp0": esp(0), "esp11": esp(11), "esp12": esp(12), "esp20": esp(20),
            "sg0": sg(0), "sg20": sg(20), "pc0": pc(0), "pc11": pc(11), "pc12": pc(12),
            "pend_disp": float(sd.params["edu"]), "p_disp": float(sd.pvalues["edu"])}

def casos_controles(ctl):
    E = pd.concat([ctl[["ACE", "edu", "Edad", "Sexo"]].assign(y=0), CAS],
                  ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
    lo = max(E[E.y == 1].Edad.min(), E[E.y == 0].Edad.min())
    hi = min(E[E.y == 1].Edad.max(), E[E.y == 0].Edad.max())
    E = E[E.Edad.between(lo, hi)].copy()
    E["b"] = pd.cut(E.Edad, np.arange(np.floor(lo/5)*5, hi + 6, 5))
    P = [pd.concat([g[g.y == 1].sample(k, random_state=1), g[g.y == 0].sample(k, random_state=1)])
         for _, g in E.groupby("b", observed=True)
         if (k := min((g.y == 1).sum(), (g.y == 0).sum())) > 0]
    if not P: return None
    E = pd.concat(P, ignore_index=True); E["tr"] = TR(E.edu)
    if ((E.y == 0) & (E.tr == "<7")).sum() < 10: return None
    sen = E.ACE < np.where(E.edu >= 12, 86, 68)
    fp = {t: 100*sen[(E.y == 0) & (E.tr == t)].mean() for t in BANDAS}
    yv = sen[E.y == 1].mean() - sen[E.y == 0].mean()
    REF = E[E.y == 0].reset_index(drop=True)
    def nm(t_, a_):
        mu = smf.ols(FP, data=t_).fit()
        t2 = t_.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
        sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
        return (a_.ACE - mu.predict(a_))/np.sqrt(np.exp(BIAS + sd.predict(a_)))
    z = pd.Series(index=E.index, dtype=float); fold = np.zeros(len(REF), int)
    for k, (_, te) in enumerate(KFold(10, shuffle=True, random_state=1).split(REF)): fold[te] = k
    rp = E.index[E.y == 0].values
    for k in range(10):
        o = E.loc[rp[fold == k]]; z.loc[o.index] = nm(REF[fold != k], o).values
    cs = E.index[E.y == 1]; z.loc[cs] = nm(REF, E.loc[cs]).values
    cc = z < np.quantile(z, sen.mean())
    return {"n_casos": int((E.y == 1).sum()), "n_ctrl": int((E.y == 0).sum()),
            "ctrl_lt7": int(((E.y == 0) & (E.tr == "<7")).sum()),
            "fp": fp, "grad": max(fp.values()) - min(fp.values()), "youden": float(yv),
            "d_youden": float(cc[E.y == 1].mean() - cc[E.y == 0].mean() - yv),
            "inversion": bool(fp["7-11"] < min(fp["<7"], fp["≥12"]))}

R, acum, etiq = {"peldanos": []}, pd.Series(True, index=com.index), []
print("ESCALERA ACUMULATIVA DE CRITERIOS DE CONTROL\n")
print(f"{'criterios acumulados':<70}{'n':>5}{'<7':>5}{'pierde':>8}{'p edu':>8}"
      f"{'esp 0':>7}{'σ 0':>6}{'pc 11':>7}{'pc 12':>7}{'grad':>7}{'ΔYouden':>9}{'inv':>5}")
prev = None
for nom, f in PELDANOS:
    m = f(com)
    acum = acum & m.fillna(False)
    etiq.append(nom.split(" · ")[1])
    nom = (" + ".join(etiq) if len(etiq) > 1 else etiq[0])
    nom = f"{len(etiq)}. " + (nom if len(nom) <= 66 else nom[:63] + "…")
    Q = com[acum]
    if len(Q) < 80:
        print(f"{nom:<70}{len(Q):>5}   muestra insuficiente"); break
    nt = {t: int((Q.tr == t).sum()) for t in BANDAS}
    ev = com[m.notna()]
    tab = pd.crosstab(ev.tr, acum[m.notna()])
    p = st.chi2_contingency(tab)[1] if tab.shape == (3, 2) else np.nan
    nr = normativo(Q); cc = casos_controles(Q)
    pierde = "" if prev is None else f"−{prev - len(Q)}"
    g = f"{cc['grad']:.1f}" if cc else "—"
    dy = f"{cc['d_youden']:+.3f}" if cc else "—"
    iv = ("sí" if cc["inversion"] else "NO") if cc else "—"
    print(f"{nom:<70}{len(Q):>5}{nt['<7']:>5}{pierde:>8}{p:>8.3f}"
          f"{nr['esp0']:>7.0f}{nr['sg0']:>6.1f}{nr['pc11']:>6.0f}%{nr['pc12']:>6.0f}%{g:>7}{dy:>9}{iv:>5}")
    R["peldanos"].append({"criterio": nom, "n": len(Q), "n_por_tramo": nt,
                          "p_edu": round(float(p), 4),
                          "normativo": {k: round(v, 3) for k, v in nr.items()},
                          "casos_controles": ({k: (round(v, 3) if isinstance(v, float) else v)
                                               for k, v in cc.items()} if cc else None)})
    prev = len(Q)

print("\n  pc 11 / pc 12 = percentil que ocupa el corte vigente a los 11 y 12 años de escolaridad")
print("  grad = gradiente de la regla vigente, en puntos porcentuales")
print("  inv = el tramo de 7 a 11 años es el menos señalado")
Path(EST / "resultados/V22_escalera_controles.json").write_text(
    json.dumps(R, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"\n-> resultados/V22_escalera_controles.json")
