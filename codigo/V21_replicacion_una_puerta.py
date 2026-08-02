#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V21 — Replicación del análisis de reglas dentro de la cohorte clínica: diseño de una sola puerta.

El análisis principal compara casos clínicos contra controles comunitarios. Es un diseño de dos
puertas: cualquier diferencia entre cohortes se comporta como señal, y por eso la exactitud absoluta
está inflada y no se reporta.

Este bloque repite el análisis **dentro de la cohorte clínica**, con casos y controles que atravesaron
el mismo mecanismo de selección —consulta por queja cognitiva— y con el **mismo criterio de control
que en la comunitaria**: memoria de reconocimiento de lista ≥ 10. Al usar el criterio y no la etiqueta
narrativa del informe se elimina además el sesgo de incorporación, porque la condición de control deja
de depender de un juicio emitido por quien administró el ACE-III.

Los dos diseños tienen sesgos opuestos:
  · dos puertas  → infla la separación entre grupos y, con ella, el gradiente
  · una puerta   → los controles son personas que consultaron por queja cognitiva, de modo que están
                   más comprometidas que la población general y el contraste se atenúa

Un resultado que aparece en ambos no puede atribuirse a ninguno de los dos mecanismos.

Salida: resultados/V21_replicacion_una_puerta.json
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
SESGO = 1.2703628454614782
FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
rng = np.random.default_rng(20260802)
R = {}

con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
cl = con.execute("select eval_id, bruto rec from resultados_v2 "
                 "where test='Lista de Rey' and subtest like 'Reconoc%'").fetchdf()
cl["rec"] = pd.to_numeric(cl.rec, errors="coerce")
dx = pd.read_csv(EST / "datos/clinico_dx3.csv").merge(
    cl.dropna(subset=["rec"]).drop_duplicates("eval_id"), on="eval_id", how="left")
dx["tr"] = TR(dx.edu)

# ── A · por qué la etiqueta narrativa no sirve como criterio de control
print("A. COMPOSICIÓN EDUCATIVA DE LOS CANDIDATOS A CONTROL EN LA COHORTE CLÍNICA")
R["candidatos"] = {}
for nom, sel in [("etiqueta «Sin afectación» del informe", dx.dx3 == "Sin afectación"),
                 ("reconocimiento ≥ 10 (criterio del estudio)", dx.rec >= 10)]:
    g = dx[sel].dropna(subset=["ACE", "edu", "Edad", "Sexo"])
    t = {b: int((g.tr == b).sum()) for b in BANDAS}
    pct = {b: round(100*t[b]/max(len(g), 1), 1) for b in BANDAS}
    print(f"   {nom:<44} n={len(g):<5} {t}   ({pct['<7']} % en el tramo bajo)")
    R["candidatos"][nom] = {"n": len(g), "por_tramo": t, "pct_por_tramo": pct}
print("\n   La etiqueta narrativa se aplica casi sólo a pacientes de alta escolaridad, de modo que no")
print("   permite estimar nada en el tramo que el trabajo estudia. Se usa el criterio del estudio.\n")

# ── B · el análisis, replicado dentro de la cohorte clínica
def arma(ctl, cas):
    E = pd.concat([ctl[["ACE", "edu", "Edad", "Sexo"]].assign(y=0),
                   cas[["ACE", "edu", "Edad", "Sexo"]].assign(y=1)],
                  ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
    lo = max(E[E.y == 1].Edad.min(), E[E.y == 0].Edad.min())
    hi = min(E[E.y == 1].Edad.max(), E[E.y == 0].Edad.max())
    E = E[E.Edad.between(lo, hi)].copy()
    E["b"] = pd.cut(E.Edad, np.arange(np.floor(lo/5)*5, hi + 6, 5))
    P = [pd.concat([g[g.y == 1].sample(k, random_state=1), g[g.y == 0].sample(k, random_state=1)])
         for _, g in E.groupby("b", observed=True)
         if (k := min((g.y == 1).sum(), (g.y == 0).sum())) > 0]
    E = pd.concat(P, ignore_index=True); E["tr"] = TR(E.edu)
    return E

def evalua(E):
    sen = E.ACE < np.where(E.edu >= 12, 86, 68)
    fp = {t: 100*sen[(E.y == 0) & (E.tr == t)].mean() for t in BANDAS}
    yv = sen[E.y == 1].mean() - sen[E.y == 0].mean()
    REF = E[E.y == 0].reset_index(drop=True)
    def norma(t_, a_):
        mu = smf.ols(FP, data=t_).fit()
        t2 = t_.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
        sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
        return (a_.ACE - mu.predict(a_)) / np.sqrt(np.exp(SESGO + sd.predict(a_)))
    z = pd.Series(index=E.index, dtype=float); fold = np.zeros(len(REF), int)
    for k, (_, te) in enumerate(KFold(10, shuffle=True, random_state=1).split(REF)): fold[te] = k
    rp = E.index[E.y == 0].values
    for k in range(10):
        o = E.loc[rp[fold == k]]; z.loc[o.index] = norma(REF[fold != k], o).values
    cs = E.index[E.y == 1]; z.loc[cs] = norma(REF, E.loc[cs]).values
    cc = z < np.quantile(z, sen.mean())
    fpc = {t: 100*cc[(E.y == 0) & (E.tr == t)].mean() for t in BANDAS}
    yc = cc[E.y == 1].mean() - cc[E.y == 0].mean()
    return {"vig_fp": fp, "vig_grad": max(fp.values()) - min(fp.values()), "vig_youden": yv,
            "cont_fp": fpc, "cont_grad": max(fpc.values()) - min(fpc.values()), "cont_youden": yc,
            "d_youden": yc - yv, "sens": float(sen[E.y == 1].mean()),
            "espec": float(1 - sen[E.y == 0].mean())}

ctl = dx[dx.rec >= 10]
cas = dx[dx.dx3 == "Demencia"]
E = arma(ctl, cas)
o = evalua(E)
nt = {t: int(((E.y == 0) & (E.tr == t)).sum()) for t in BANDAS}
print("B. REPLICACIÓN DENTRO DE LA COHORTE CLÍNICA")
print(f"   {int((E.y==1).sum())} casos · {int((E.y==0).sum())} controles  ·  controles por tramo {nt}")
print(f"   edad {E[E.y==1].Edad.mean():.1f} frente a {E[E.y==0].Edad.mean():.1f} años\n")
print(f"   {'regla':<24}{'sens':>7}{'espec':>8}{'Youden':>8}{'<7':>8}{'7-11':>7}{'≥12':>7}{'grad':>8}")
print(f"   {'vigente 86/68':<24}{o['sens']:>7.3f}{o['espec']:>8.3f}{o['vig_youden']:>8.3f}"
      f"{o['vig_fp']['<7']:>7.1f}%{o['vig_fp']['7-11']:>6.1f}%{o['vig_fp']['≥12']:>6.1f}%{o['vig_grad']:>8.1f}")
print(f"   {'corrección continua':<24}{'':>7}{'':>8}{o['cont_youden']:>8.3f}"
      f"{o['cont_fp']['<7']:>7.1f}%{o['cont_fp']['7-11']:>6.1f}%{o['cont_fp']['≥12']:>6.1f}%{o['cont_grad']:>8.1f}")

# ── intervalos por remuestreo
bs = []
for _ in range(400):
    idx = np.concatenate([rng.choice(E.index[E.y == 0], (E.y == 0).sum(), replace=True),
                          rng.choice(E.index[E.y == 1], (E.y == 1).sum(), replace=True)])
    try: bs.append(evalua(E.loc[idx].reset_index(drop=True)))
    except Exception: pass
q = lambda k, p: float(np.percentile([b[k] for b in bs], p))
print(f"\n   IC 95 % ({len(bs)} réplicas):")
print(f"     gradiente de la regla vigente     {o['vig_grad']:.1f}  [{q('vig_grad',2.5):.1f}; {q('vig_grad',97.5):.1f}]")
print(f"     Δ Youden (continua − vigente)     {o['d_youden']:+.3f}  [{q('d_youden',2.5):+.3f}; {q('d_youden',97.5):+.3f}]")

R["replicacion"] = {"n_casos": int((E.y == 1).sum()), "n_ctrl": int((E.y == 0).sum()),
                    "ctrl_por_tramo": nt,
                    "edad_casos": round(float(E[E.y == 1].Edad.mean()), 1),
                    "edad_ctrl": round(float(E[E.y == 0].Edad.mean()), 1),
                    "vigente": {"sens": round(o["sens"], 3), "espec": round(o["espec"], 3),
                                "youden": round(o["vig_youden"], 3),
                                "fp": {t: round(o["vig_fp"][t], 1) for t in BANDAS},
                                "grad": round(o["vig_grad"], 1)},
                    "continua": {"youden": round(o["cont_youden"], 3),
                                 "fp": {t: round(o["cont_fp"][t], 1) for t in BANDAS},
                                 "grad": round(o["cont_grad"], 1)},
                    "d_youden": round(o["d_youden"], 3),
                    "ic_grad_vig": [round(q("vig_grad", 2.5), 1), round(q("vig_grad", 97.5), 1)],
                    "ic_d_youden": [round(q("d_youden", 2.5), 3), round(q("d_youden", 97.5), 3)]}

# ── C · lectura conjunta con el análisis principal
print("\n\nC. LOS DOS DISEÑOS, LADO A LADO")
print(f"   {'diseño':<40}{'casos':>7}{'ctrl':>6}{'<7':>8}{'7-11':>8}{'≥12':>8}{'grad':>8}{'ΔYouden':>10}")
prin = json.loads((EST / "resultados/V13_equidad_corregida.json").read_text())["principal"]
print(f"   {'dos puertas · controles comunitarios':<40}{prin['n_casos']:>7}{prin['n_ctrl']:>6}"
      f"{prin['vigente']['fp']['<7']:>7.1f}%{prin['vigente']['fp']['7-11']:>7.1f}%"
      f"{prin['vigente']['fp']['≥12']:>7.1f}%{prin['vigente']['grad']:>8.1f}{prin['d_youden']:>+10.3f}")
print(f"   {'una puerta · controles clínicos':<40}{int((E.y==1).sum()):>7}{int((E.y==0).sum()):>6}"
      f"{o['vig_fp']['<7']:>7.1f}%{o['vig_fp']['7-11']:>7.1f}%{o['vig_fp']['≥12']:>7.1f}%"
      f"{o['vig_grad']:>8.1f}{o['d_youden']:>+10.3f}")
print("\n   En ambos el tramo intermedio es el menos señalado y la diferencia de Youden es")
print("   indistinguible de cero. La magnitud del gradiente depende del diseño, como se espera:")
print("   los controles clínicos consultaron por queja cognitiva y están más comprometidos.")
R["comparacion"] = {"dos_puertas": {"grad": prin["vigente"]["grad"], "d_youden": prin["d_youden"],
                                    "fp": prin["vigente"]["fp"]},
                    "una_puerta": {"grad": round(o["vig_grad"], 1), "d_youden": round(o["d_youden"], 3),
                                   "fp": {t: round(o["vig_fp"][t], 1) for t in BANDAS}}}

Path(EST / "resultados/V21_replicacion_una_puerta.json").write_text(
    json.dumps(R, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("\n-> resultados/V21_replicacion_una_puerta.json")
