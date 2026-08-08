#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V26 — ¿EL ESTRECHAMIENTO DE LA DISPERSIÓN ES REAL O ES ARTEFACTO DE TECHO?

El manuscrito sostiene que la variabilidad del rendimiento NORMAL se estrecha al aumentar la
escolaridad (13,2 -> 5,8 puntos de ACE-III) y deriva de allí su afirmación más general: ningún
umbral fijo puede ocupar la misma posición relativa en todos los tramos. Ese argumento es el que
transporta a otros instrumentos, de modo que conviene atacarlo antes de invertir en extensiones.

La amenaza es la misma que V4 ya documentó para la CURVATURA: el ACE-III topa en 100. Los
controles de alta escolaridad se apilan contra el techo y su varianza se comprime por construcción.
V4 mostró que un tercio de la curvatura observada era techo. La dispersión nunca se testeó así.

Aquí se reestima el modelo de dispersión sobre θ (habilidad latente del GRM de Samejima), que no
tiene techo, y se compara contra el puntaje bruto. Tres capas:

  A. θ por EAP sobre la muestra combinada (misma métrica que V4, misma implementación).
  B. Dispersión de Harvey (1976) sobre controles comunitarios, en bruto y en θ.
  C. Corrección por error de medición: var(θ) observada = var verdadera + var del error. Como el
     error del EAP varía con el nivel, se descuenta E[SE²] por tramo. Sin esto, un estrechamiento
     de θ podría ser sólo mayor precisión de medición en un extremo de la escala.

  D. Diagnóstico de techo explícito: proporción en el techo y a <=3 puntos del techo, por tramo.

θ por EAP se contrae hacia la previa, lo que comprime varianza. Esa contracción juega EN CONTRA
del hallazgo (achata las diferencias entre tramos), de modo que un estrechamiento que sobreviva
en θ es conservador. Se declara y no se corrige.

Salida: consola + resultados/V26_dispersion_latente.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from girth import grm_mml
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402

OUT = EST / "resultados"
SESGO_LOGCHI2 = 1.2703628454614782      # -(digamma(1/2) + log 2); Harvey 1976
EDAD_REF = 65.0
BANDAS = ["<7", "7-11", ">=12"]
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=BANDAS)
rng = np.random.default_rng(26)
R = {}

ITEMS = ['ACE_AtOT', 'ACE_AtOE', 'ACE_AtRegistro', 'ACE_AtSubstr', 'ACE_MRecuerdo', 'ACE_MAnterogr',
         'ACE_MRetrogr', 'ACE_MRecuerdoNyD', 'ACE_MReconocNyD', 'ACE_FluVerbFPC', 'ACE_FluVerbSPC',
         'ACE_LComprensionLyH', 'ACE_LEscrit', 'ACE_LRepP', 'ACE_LRepProverb', 'ACE_LDenom',
         'ACE_LCompDibujo', 'ACE_LLectura', 'ACE_HabVisoDiagrama', 'ACE_HabVisoCubo',
         'ACE_HabPerPuntos', 'ACE_HabPerLetras', 'ACE_HabVisoReloj']

# ============================================================ datos (idéntico a V4 + control)
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all").dropna(axis=0, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
com_ok = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
c40["doc"] = nd(c40["dni"])
c40["ctrl"] = es_control(c40).values

X = pd.DataFrame({k: pd.to_numeric(c40[k], errors="coerce") for k in ITEMS})
X["ACE_LLectura"] = X.ACE_LLectura.clip(upper=1)
r_, k_ = X.ACE_MRecuerdoNyD, X.ACE_MReconocNyD
X["ACE_MReconocNyD"] = np.where(r_ == 7, 5, np.minimum(5, k_ + np.minimum(5, np.round(r_ * 5 / 7))))
com = pd.concat([X, c40[["doc", "ctrl"]], pd.DataFrame({
    "Edad": pd.to_numeric(c40.Edad, errors="coerce"),
    "edu": pd.to_numeric(c40.ed_anos_completos, errors="coerce").mask(lambda s: s > 30),
    "Sexo": c40.Sexo.astype(str)})], axis=1)
com = com[com.doc.isin(set(pd.to_numeric(com_ok.dni, errors="coerce").dropna()))]
com = com.dropna(subset=ITEMS + ["edu", "Edad", "Sexo"]).reset_index(drop=True)
com["ACE"] = com[ITEMS].sum(axis=1)
com["cohorte"] = "comunitaria"

cli = pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
cli = cli.dropna(subset=ITEMS + ["edu", "Edad", "Sexo", "ACE"])
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
cli["cohorte"] = "clínica"; cli["ctrl"] = False

COLS = ITEMS + ["ACE", "edu", "Edad", "Sexo", "cohorte", "ctrl"]
D = pd.concat([com[COLS], cli[COLS]], ignore_index=True)
print("=" * 96)
print(f"muestra con los 23 ítems completos — comunitaria {len(com)} | clínica {len(cli)} | "
      f"combinada {len(D)} | controles comunitarios {int(com.ctrl.sum())}")
R["n"] = {"comunitaria": len(com), "clinica": len(cli), "combinada": len(D),
          "controles": int(com.ctrl.sum())}


# ============================================================ A. GRM + θ (igual que V4)
def collapse_ordinal(s, min_cell=15):
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


def eap(Rmat, a, b, grid=np.linspace(-4, 4, 161)):
    n, J = Rmat.shape
    logL = np.zeros((n, len(grid)))
    for j in range(J):
        thr = b[j][~np.isnan(b[j])]
        cum = 1.0 / (1.0 + np.exp(-a[j] * (grid[:, None] - thr[None, :])))
        P = np.concatenate([np.ones((len(grid), 1)), cum, np.zeros((len(grid), 1))], axis=1)
        P = np.clip(P[:, :-1] - P[:, 1:], 1e-10, 1.0)
        logL += np.log(P.T)[Rmat[:, j], :]
    w = np.exp(logL - logL.max(axis=1, keepdims=True)) * stats.norm.pdf(grid)[None, :]
    w /= w.sum(axis=1, keepdims=True)
    th = w @ grid
    se = np.sqrt(np.clip(w @ (grid ** 2) - th ** 2, 0, None))
    return th, se


print("\nA. GRADED RESPONSE MODEL sobre la muestra combinada (métrica común a las dos cohortes)")
Rc = pd.DataFrame({c: collapse_ordinal(D[c])[0] for c in ITEMS})
grm = grm_mml(Rc.values.T.astype(int))
a = np.asarray(grm["Discrimination"], dtype=float)
b = np.asarray(grm["Difficulty"], dtype=float)
theta, se_th = eap(Rc.values.astype(int), a, b)
D["theta"], D["se_theta"] = theta, se_th
print(f"   θ: media {theta.mean():+.3f} DE {theta.std():.3f} · error estándar medio {se_th.mean():.3f} "
      f"· r con el bruto {np.corrcoef(theta, D.ACE)[0, 1]:.3f}")
R["grm"] = {"a_mediana": round(float(np.median(a)), 3),
            "theta_de": round(float(theta.std()), 3), "se_medio": round(float(se_th.mean()), 3),
            "r_theta_bruto": round(float(np.corrcoef(theta, D.ACE)[0, 1]), 3)}

CTL = D[(D.cohorte == "comunitaria") & (D.ctrl)].copy().reset_index(drop=True)
CTL["tr"] = TR(CTL.edu)
print(f"\n   controles comunitarios con ítems completos: n = {len(CTL)}  "
      f"({' · '.join(f'{b_}={int((CTL.tr==b_).sum())}' for b_ in BANDAS)})")
R["n"]["controles_items_completos"] = len(CTL)
R["n"]["controles_por_tramo"] = {b_: int((CTL.tr == b_).sum()) for b_ in BANDAS}


# ============================================================ D. diagnóstico de techo
print("\n" + "=" * 96)
print("D. DIAGNÓSTICO DE TECHO EN LOS CONTROLES (la amenaza que se quiere descartar)")
R["techo"] = {}
for b_ in BANDAS:
    s = CTL[CTL.tr == b_]
    if not len(s):
        continue
    d = {"n": int(len(s)), "media_ACE": round(float(s.ACE.mean()), 2),
         "en_100": round(float((s.ACE >= 100).mean()) * 100, 1),
         "a_3_del_techo": round(float((s.ACE >= 97).mean()) * 100, 1),
         "a_10_del_techo": round(float((s.ACE >= 90).mean()) * 100, 1),
         "de_ACE": round(float(s.ACE.std(ddof=1)), 2),
         "de_theta": round(float(s.theta.std(ddof=1)), 3),
         "se_theta_medio": round(float(s.se_theta.mean()), 3)}
    R["techo"][b_] = d
    print(f"   {b_:>5}  n={d['n']:<4} ACE media {d['media_ACE']:>5} · DE {d['de_ACE']:>5} | "
          f"=100: {d['en_100']:>4}%  >=97: {d['a_3_del_techo']:>4}%  >=90: {d['a_10_del_techo']:>5}% | "
          f"θ DE {d['de_theta']:.3f} · SE(θ) {d['se_theta_medio']:.3f}")


# ============================================================ B. dispersión de Harvey
def harvey(df, y, formula_mu, formula_sd="lr2 ~ edu + Edad"):
    """Modelo de posición + modelo de log-varianza con la corrección de sesgo de Harvey."""
    mu = smf.ols(f"{y} ~ {formula_mu}", data=df).fit(cov_type="HC3")
    t2 = df.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-10, None)))
    sd = smf.ols(formula_sd, data=t2).fit(cov_type="HC3")
    return mu, sd


def sigma_en(sd_model, edu, edad=EDAD_REF):
    g = pd.DataFrame({"edu": np.atleast_1d(edu), "Edad": edad})
    return np.sqrt(np.exp(SESGO_LOGCHI2 + sd_model.predict(g).values))


print("\n" + "=" * 96)
print("B. MODELO DE DISPERSIÓN SOBRE LOS CONTROLES — puntaje bruto frente a métrica latente")
FMU = "edu + I(edu**2) + Edad + C(Sexo)"
R["dispersion"] = {}
modelos = {}
for lab, y in [("ACE bruto", "ACE"), ("θ latente", "theta")]:
    mu, sd = harvey(CTL, y, FMU)
    modelos[lab] = (mu, sd)
    coef = float(sd.params["edu"]); ci = sd.conf_int().loc["edu"]
    s0, s20 = sigma_en(sd, 0.0)[0], sigma_en(sd, 20.0)[0]
    R["dispersion"][lab] = {
        "pendiente_log_var_por_anio": round(coef, 4),
        "ic95": [round(float(ci[0]), 4), round(float(ci[1]), 4)],
        "p": float(sd.pvalues["edu"]),
        "sigma_edu0": round(float(s0), 4), "sigma_edu20": round(float(s20), 4),
        "razon_sigma_0_20": round(float(s0 / s20), 3)}
    print(f"\n   {lab:<11} pendiente de log-varianza por año  {coef:+.4f}  "
          f"IC95 [{ci[0]:+.4f}, {ci[1]:+.4f}]  p={sd.pvalues['edu']:.2e}")
    print(f"   {'':<11} sigma a los {EDAD_REF:.0f} años:  0 años de escuela {s0:.3f}  ->  "
          f"20 años {s20:.3f}   (razón {s0/s20:.2f}×)")

# Levene por tramo, en las dos métricas
print("\n   homogeneidad de varianzas entre tramos (Levene):")
R["levene"] = {}
for lab, y in [("ACE bruto", "ACE"), ("θ latente", "theta")]:
    grupos = [CTL.loc[CTL.tr == b_, y].values for b_ in BANDAS if (CTL.tr == b_).sum() > 2]
    st, p = stats.levene(*grupos, center="median")
    des = [round(float(np.std(g, ddof=1)), 3) for g in grupos]
    R["levene"][lab] = {"W": round(float(st), 3), "p": float(p), "de_por_tramo": des}
    print(f"     {lab:<11} W={st:6.3f}  p={p:.2e}   DE por tramo: " +
          "  ".join(f"{b_}={d}" for b_, d in zip(BANDAS, des)))


# ============================================================ C. corrección por error de medición
print("\n" + "=" * 96)
print("C. ¿ES VARIANZA VERDADERA O ES PRECISIÓN DE MEDICIÓN?")
print("   var(θ observada) = var(θ verdadera) + E[SE(θ)²].  Se descuenta el error por tramo.")
R["var_verdadera"] = {}
for b_ in BANDAS:
    s = CTL[CTL.tr == b_]
    if len(s) < 3:
        continue
    v_obs = float(s.theta.var(ddof=1))
    v_err = float((s.se_theta ** 2).mean())
    v_true = max(v_obs - v_err, 0.0)
    R["var_verdadera"][b_] = {"n": int(len(s)), "var_observada": round(v_obs, 4),
                              "var_error": round(v_err, 4), "var_verdadera": round(v_true, 4),
                              "de_verdadera": round(float(np.sqrt(v_true)), 3),
                              "fiabilidad": round(1 - v_err / v_obs, 3) if v_obs > 0 else None}
    print(f"   {b_:>5}  n={len(s):<4} var obs {v_obs:.4f}  − var error {v_err:.4f}  "
          f"=  var verdadera {v_true:.4f}   (DE {np.sqrt(v_true):.3f} · fiabilidad "
          f"{1 - v_err/v_obs:.3f})")

# la misma corrección, continua: regresión de log(var verdadera) sobre escolaridad por remuestreo
print("\n   pendiente de la varianza VERDADERA sobre la escolaridad (bootstrap 2000, IC percentil):")


def pendiente_var_verdadera(df):
    """Pendiente de log(var verdadera de θ) por año de escolaridad, sobre residuos del modelo de posición."""
    mu = smf.ols(f"theta ~ {FMU}", data=df).fit()
    t = df.assign(r2=mu.resid ** 2)
    # E[r²] = var verdadera + SE², de modo que se resta el error antes de modelar
    t["r2_neto"] = np.clip(t.r2 - t.se_theta ** 2, 1e-6, None)
    m = smf.ols("np.log(r2_neto) ~ edu + Edad", data=t).fit()
    return float(m.params["edu"])


obs = pendiente_var_verdadera(CTL)
bs = []
for _ in range(2000):
    idx = rng.integers(0, len(CTL), len(CTL))
    try:
        bs.append(pendiente_var_verdadera(CTL.iloc[idx].reset_index(drop=True)))
    except Exception:
        pass
lo, hi = np.percentile(bs, [2.5, 97.5])
R["pendiente_var_verdadera"] = {"estimacion": round(obs, 4),
                                "ic95": [round(float(lo), 4), round(float(hi), 4)],
                                "n_bootstrap": len(bs)}
print(f"     {obs:+.4f}  IC95 [{lo:+.4f}, {hi:+.4f}]   ({len(bs)} réplicas)")

# ============================================================ veredicto
print("\n" + "=" * 96)
print("VEREDICTO")
d_br = R["dispersion"]["ACE bruto"]; d_th = R["dispersion"]["θ latente"]
prop = (d_th["pendiente_log_var_por_anio"] / d_br["pendiente_log_var_por_anio"]
        if d_br["pendiente_log_var_por_anio"] else np.nan)
R["veredicto"] = {
    "pendiente_bruto": d_br["pendiente_log_var_por_anio"],
    "pendiente_latente": d_th["pendiente_log_var_por_anio"],
    "proporcion_conservada": round(float(prop), 3),
    "latente_significativa": bool(d_th["p"] < 0.05),
    "var_verdadera_significativa": bool(lo < 0 and hi < 0)}
print(f"   pendiente en bruto  {d_br['pendiente_log_var_por_anio']:+.4f}  (p={d_br['p']:.2e})")
print(f"   pendiente en θ      {d_th['pendiente_log_var_por_anio']:+.4f}  (p={d_th['p']:.2e})   "
      f"-> conserva el {prop*100:.0f}% de la magnitud")
print(f"   pendiente en varianza verdadera (θ sin error de medición)  {obs:+.4f}  "
      f"IC95 [{lo:+.4f}, {hi:+.4f}]")
if d_th["p"] < 0.05 and hi < 0:
    print("\n   El estrechamiento SOBREVIVE al techo y al error de medición.")
    print("   El argumento general del manuscrito —ningún umbral fijo ocupa la misma posición")
    print("   relativa en todos los tramos— no es un artefacto del ACE-III y es transportable.")
else:
    print("\n   ATENCIÓN: el estrechamiento NO sobrevive de forma inequívoca. El argumento general")
    print("   debe reformularse o restringirse al puntaje bruto, declarando el techo como mecanismo.")

OUT.mkdir(exist_ok=True)
(OUT / "V26_dispersion_latente.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V26_dispersion_latente.json'}")
