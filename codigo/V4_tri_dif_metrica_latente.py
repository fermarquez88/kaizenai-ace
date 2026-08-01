#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V4 — TEORÍA DE RESPUESTA AL ÍTEM, DIF Y CURVATURA SOBRE LA MÉTRICA LATENTE.

Pregunta central del bloque, que es la objeción psicométrica al resultado principal:
  ¿los rendimientos decrecientes de la educación son una propiedad de la cognición, o un artefacto
  del techo del puntaje bruto? El puntaje bruto es una función ojival de la habilidad latente, de
  modo que comprime en el extremo alto y podría FABRICAR curvatura donde no la hay.

Se responde reestimando todo sobre θ (habilidad latente del Graded Response Model), que es una
métrica de intervalo sin techo.

  A. Ajuste del GRM sobre la muestra combinada (métrica común a las dos cohortes).
  B. Estimación de θ por valor esperado a posteriori (EAP), implementada explícitamente.
  C. LA PRUEBA: curvatura y escalón sobre θ vs sobre el puntaje bruto.
  D. Funcionamiento diferencial del ítem (DIF) por educación, con purificación iterativa.
  E. Invarianza entre cohortes: ¿es lícito ponerlas en la misma métrica?

Salida: consola + resultados/V4_tri.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from girth import grm_mml
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUT = EST / "resultados"
R = {}

ITEMS = ['ACE_AtOT','ACE_AtOE','ACE_AtRegistro','ACE_AtSubstr','ACE_MRecuerdo','ACE_MAnterogr',
         'ACE_MRetrogr','ACE_MRecuerdoNyD','ACE_MReconocNyD','ACE_FluVerbFPC','ACE_FluVerbSPC',
         'ACE_LComprensionLyH','ACE_LEscrit','ACE_LRepP','ACE_LRepProverb','ACE_LDenom',
         'ACE_LCompDibujo','ACE_LLectura','ACE_HabVisoDiagrama','ACE_HabVisoCubo',
         'ACE_HabPerPuntos','ACE_HabPerLetras','ACE_HabVisoReloj']

# ------------------------------------------------------------------ datos con ítems completos
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all").dropna(axis=0, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
com_ok = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")          # los 758 analíticos
c40["doc"] = nd(c40["dni"])
X = pd.DataFrame({k: pd.to_numeric(c40[k], errors="coerce") for k in ITEMS})
X["ACE_LLectura"] = X.ACE_LLectura.clip(upper=1)
r_, k_ = X.ACE_MRecuerdoNyD, X.ACE_MReconocNyD
X["ACE_MReconocNyD"] = np.where(r_ == 7, 5, np.minimum(5, k_ + np.minimum(5, np.round(r_*5/7))))
com = pd.concat([X, c40[["doc"]], pd.DataFrame({
    "Edad": pd.to_numeric(c40.Edad, errors="coerce"),
    "edu": pd.to_numeric(c40.ed_anos_completos, errors="coerce").mask(lambda s: s > 30),
    "Sexo": c40.Sexo.astype(str)})], axis=1)
com = com[com.doc.isin(set(pd.to_numeric(com_ok.dni, errors="coerce").dropna()))]
com = com.dropna(subset=ITEMS + ["edu", "Edad", "Sexo"]).reset_index(drop=True)
com["ACE"] = com[ITEMS].sum(axis=1); com["cohorte"] = "comunitaria"

cli = pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
cli = cli.dropna(subset=ITEMS + ["edu", "Edad", "Sexo", "ACE"])
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True); cli["cohorte"] = "clínica"

D = pd.concat([com[ITEMS + ["ACE", "edu", "Edad", "Sexo", "cohorte"]],
               cli[ITEMS + ["ACE", "edu", "Edad", "Sexo", "cohorte"]]], ignore_index=True)
print(f"con los 23 ítems completos -> comunitaria {len(com)} | clínica {len(cli)} | combinada {len(D)}")
R["n"] = {"comunitaria": len(com), "clinica": len(cli), "combinada": len(D)}


def collapse_ordinal(s, min_cell=15):
    """Colapsa categorías adyacentes escasas preservando el orden. Devuelve códigos 0..K-1."""
    vals = sorted(pd.unique(s.dropna())); counts = s.value_counts()
    groups, cur = [], []
    for v in vals:
        cur.append(v)
        if sum(counts.get(x, 0) for x in cur) >= min_cell:
            groups.append(cur); cur = []
    if cur:
        groups[-1].extend(cur) if groups else groups.append(cur)
    mp = {v: gi for gi, g in enumerate(groups) for v in g}
    return s.map(mp).astype(int), len(groups)


# ==================================================================== A. GRM
print("\n" + "=" * 96 + "\nA. GRADED RESPONSE MODEL SOBRE LA MUESTRA COMBINADA (métrica común)")
Rc = pd.DataFrame({c: collapse_ordinal(D[c])[0] for c in ITEMS})
ncat = {c: int(Rc[c].max()) + 1 for c in ITEMS}
grm = grm_mml(Rc.values.T.astype(int))
a = np.asarray(grm["Discrimination"], dtype=float)
b = np.asarray(grm["Difficulty"], dtype=float)          # ítems × (K-1), NaN donde no hay umbral
print(f"  discriminación: mediana {np.median(a):.2f}  rango [{a.min():.2f}, {a.max():.2f}]")
top = sorted(zip(ITEMS, a), key=lambda t: -t[1])[:5]
print("  más discriminativos: " + " · ".join(f"{i.replace('ACE_','')} a={v:.2f}" for i, v in top))
R["grm"] = {"a_mediana": round(float(np.median(a)), 3),
            "a_rango": [round(float(a.min()), 3), round(float(a.max()), 3)],
            "items": {i: {"a": round(float(av), 3), "n_cat": ncat[i]} for i, av in zip(ITEMS, a)}}


# ==================================================================== B. θ POR EAP
def eap(Rmat, a, b, grid=np.linspace(-4, 4, 161)):
    """Valor esperado a posteriori de θ bajo el GRM de Samejima, con previa normal estándar."""
    n, J = Rmat.shape
    logL = np.zeros((n, len(grid)))
    for j in range(J):
        thr = b[j][~np.isnan(b[j])]
        # P(X >= k) para k = 1..K-1  ->  matriz (grid × K-1)
        cum = 1.0 / (1.0 + np.exp(-a[j] * (grid[:, None] - thr[None, :])))
        P = np.concatenate([np.ones((len(grid), 1)), cum, np.zeros((len(grid), 1))], axis=1)
        P = np.clip(P[:, :-1] - P[:, 1:], 1e-10, 1.0)          # grid × K
        logL += np.log(P.T)[Rmat[:, j], :]
    w = np.exp(logL - logL.max(axis=1, keepdims=True)) * stats.norm.pdf(grid)[None, :]
    w /= w.sum(axis=1, keepdims=True)
    th = w @ grid
    se = np.sqrt(w @ (grid**2) - th**2)
    return th, se


theta, se_th = eap(Rc.values.astype(int), a, b)
D["theta"] = theta; D["se_theta"] = se_th
print(f"\nB. θ estimado por EAP: media {theta.mean():+.3f}  DE {theta.std():.3f}  "
      f"error estándar medio {se_th.mean():.3f}")
print(f"   correlación θ con el puntaje bruto: r={np.corrcoef(theta, D.ACE)[0,1]:.3f} "
      f"(Spearman {stats.spearmanr(theta, D.ACE).statistic:.3f})")
R["theta"] = {"media": round(float(theta.mean()), 3), "de": round(float(theta.std()), 3),
              "se_medio": round(float(se_th.mean()), 3),
              "r_con_bruto": round(float(np.corrcoef(theta, D.ACE)[0, 1]), 3),
              "rho_con_bruto": round(float(stats.spearmanr(theta, D.ACE).statistic), 3)}

# ==================================================================== C. LA PRUEBA
print("\n" + "=" * 96 + "\nC. ¿LA CURVATURA SOBREVIVE EN LA MÉTRICA LATENTE?")
print("   Se reestima el mismo modelo con θ como desenlace. θ no tiene techo.")
R["curvatura_latente"] = {}
for coh in ["comunitaria", "clínica"]:
    d = D[D.cohorte == coh].copy()
    d["post"] = (d.edu >= 12).astype(int)
    print(f"\n  {coh} (n={len(d)}):")
    for lab, y, esc in [("puntaje bruto", "ACE", 1.0), ("θ latente", "theta", 1.0)]:
        mq = smf.ols(f"{y} ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
        lin = smf.ols(f"{y} ~ edu + Edad + C(Sexo)", data=d).fit()
        qua = smf.ols(f"{y} ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
        ms = smf.ols(f"{y} ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
        b2 = float(mq.params["I(edu ** 2)"]); ci2 = mq.conf_int().loc["I(edu ** 2)"]
        # curvatura relativa: b2 en unidades de la DE del desenlace, comparable entre escalas
        b2r = b2 / d[y].std()
        p_cl = float(stats.chi2.sf(2*(qua.llf - lin.llf), 1))
        ci_e = ms.conf_int().loc["post"]
        R["curvatura_latente"].setdefault(coh, {})[lab] = {
            "b2": round(b2, 4), "ic95": [round(float(ci2[0]), 4), round(float(ci2[1]), 4)],
            "p": float(mq.pvalues["I(edu ** 2)"]), "b2_estandarizado": round(float(b2r), 5),
            "p_cuad_vs_lin": p_cl, "escalon": round(float(ms.params["post"]), 3),
            "escalon_ic95": [round(float(ci_e[0]), 3), round(float(ci_e[1]), 3)],
            "escalon_p": float(ms.pvalues["post"])}
        print(f"    {lab:<15} b₂={b2:+.4f} [{ci2[0]:+.4f},{ci2[1]:+.4f}] p={mq.pvalues['I(edu ** 2)']:.2e}"
              f"   b₂/DE={b2r:+.5f}   cuad>lin p={p_cl:.2e}")
        print(f"    {'':<15} escalón en 12 años: {ms.params['post']:+.3f} "
              f"[{ci_e[0]:+.3f},{ci_e[1]:+.3f}] p={ms.pvalues['post']:.3f}")
    # pendientes marginales sobre θ
    d2 = D[D.cohorte == coh]
    mq = smf.ols("theta ~ edu + I(edu**2) + Edad + C(Sexo)", data=d2).fit(cov_type="HC3")
    nmp = list(mq.params.index); i1, i2 = nmp.index("edu"), nmp.index("I(edu ** 2)")
    V = np.asarray(mq.cov_params()); b1, b2 = mq.params.iloc[i1], mq.params.iloc[i2]
    mg = {}
    for e in (3, 7, 12, 17):
        v = np.zeros(len(nmp)); v[i1] = 1; v[i2] = 2*e
        est = float(b1 + 2*b2*e); s = float(np.sqrt(v @ V @ v))
        mg[str(e)] = {"b": round(est, 4), "ic95": [round(est-1.96*s, 4), round(est+1.96*s, 4)]}
    R["curvatura_latente"][coh]["marginal_theta"] = mg
    print("    pendiente marginal sobre θ (DE de habilidad por año): " +
          "  ".join(f"{e}a:{mg[e]['b']:+.3f}" for e in mg))
    print(f"    razón año 3 / año 17 = {mg['3']['b']/mg['17']['b']:.1f}×" if mg['17']['b'] > 0 else "")

# ==================================================================== D. DIF POR EDUCACIÓN
print("\n" + "=" * 96 + "\nD. FUNCIONAMIENTO DIFERENCIAL DEL ÍTEM POR EDUCACIÓN (con purificación)")
print("   Zumbo: se compara el ajuste de un modelo con y sin el grupo, condicionando en la habilidad.")


def dif_barrido(d, grupo, anchor_items):
    """DIF de Zumbo con anclaje: se condiciona en el puntaje de los ítems libres de DIF."""
    res = {}
    match = d[anchor_items].sum(axis=1)
    match = (match - match.mean()) / match.std()
    for c in ITEMS:
        y = collapse_ordinal(d[c])[0]
        if y.nunique() < 2:
            continue
        df = pd.DataFrame({"y": (y >= y.max()).astype(int), "m": match.values, "g": grupo.values})
        try:
            m0 = smf.logit("y ~ m", data=df).fit(disp=0)
            m1 = smf.logit("y ~ m + g", data=df).fit(disp=0)
            m2 = smf.logit("y ~ m * g", data=df).fit(disp=0)
        except Exception:
            continue
        nag = lambda mm: (1 - np.exp(2*(m0.llnull - mm.llf)/len(df))) / (1 - np.exp(2*m0.llnull/len(df)))
        dR2 = float(nag(m2) - nag(m0))
        p = float(stats.chi2.sf(2*(m2.llf - m0.llf), 2))
        res[c] = {"dR2": round(dR2, 4), "p": p, "beta_g": round(float(m1.params["g"]), 3),
                  "clase": "grande" if dR2 >= 0.070 else ("moderado" if dR2 >= 0.035 else "trivial")}
    return res


dcom = D[D.cohorte == "comunitaria"].reset_index(drop=True)
g_edu = (dcom.edu < 12).astype(int)
print(f"   grupo focal (baja escolaridad) n={int(g_edu.sum())} | referencia n={int((1-g_edu).sum())}")
anchor = list(ITEMS)
for it in range(4):                                   # purificación iterativa
    r = dif_barrido(dcom, g_edu, anchor)
    ps = pd.Series({k: v["p"] for k, v in r.items()}).sort_values()
    q = ps * len(ps) / np.arange(1, len(ps)+1)        # Benjamini-Hochberg
    q = q[::-1].cummin()[::-1].clip(upper=1)
    flag = [k for k in r if q.get(k, 1) < 0.05 and r[k]["dR2"] >= 0.035]
    nuevo = [c for c in ITEMS if c not in flag]
    if nuevo == anchor:
        break
    anchor = nuevo if len(nuevo) >= 10 else anchor
print(f"   purificación: {it+1} iteraciones; ancla final = {len(anchor)} ítems")
grandes = {k: v for k, v in r.items() if v["clase"] != "trivial"}
R["dif_educacion"] = {"n_focal": int(g_edu.sum()), "n_referencia": int((1-g_edu).sum()),
                      "anclaje_n": len(anchor), "items": r,
                      "n_no_trivial": len(grandes), "q_valores": {k: round(float(v), 4) for k, v in q.items()}}
if grandes:
    print("   ítems con DIF no trivial (ΔR² Nagelkerke ≥ 0,035 y q<0,05):")
    for k, v in sorted(grandes.items(), key=lambda t: -t[1]["dR2"]):
        sig = "a favor de baja escolaridad" if v["beta_g"] > 0 else "en contra de baja escolaridad"
        print(f"     {k.replace('ACE_',''):<22} ΔR²={v['dR2']:.3f} ({v['clase']}) q={q[k]:.4f}  {sig}")
else:
    print("   ningún ítem alcanza DIF no trivial")

# ==================================================================== E. INVARIANZA ENTRE COHORTES
print("\n" + "=" * 96 + "\nE. INVARIANZA ENTRE COHORTES — ¿es lícita la métrica común?")
g_coh = (D.cohorte == "clínica").astype(int).reset_index(drop=True)
rc = dif_barrido(D.reset_index(drop=True), g_coh, ITEMS)
nt = {k: v for k, v in rc.items() if v["dR2"] >= 0.035}
print(f"   ítems con ΔR² ≥ 0,035 entre cohortes: {len(nt)} de {len(rc)}")
for k, v in sorted(nt.items(), key=lambda t: -t[1]["dR2"])[:6]:
    print(f"     {k.replace('ACE_',''):<22} ΔR²={v['dR2']:.3f} ({v['clase']})")
R["invarianza_cohorte"] = {"n_no_trivial": len(nt), "items": rc}

(OUT / "V4_tri.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> {OUT/'V4_tri.json'}")
