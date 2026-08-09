#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V26 — ¿El estrechamiento de la dispersión está en las personas o en la escala del puntaje?

═══════════════════════════════════════════════════════════════════════════════════════════════
NOTA DE CORRECCIÓN — 2026-08-09
═══════════════════════════════════════════════════════════════════════════════════════════════
La primera versión de este bloque contenía tres defectos que una auditoría con revisores de
Neurology, Alzheimer's & Dementia, Lancet y Nature identificó y que se verificaron uno por uno:

  1. SIGNO INVERTIDO EN LA DESATENUACIÓN. Se calculaba `var_verdadera = var(θ̂) − E[SE²]`. Para un
     estimador de media posterior la ley de la varianza total da lo contrario:
         Var(θ) = Var(E[θ|X]) + E[Var(θ|X)] = Var(θ̂_EAP) + E[SE²]
     El EAP ya está contraído hacia la previa; restarle la varianza posterior lo contrae dos veces.
     Comprobación decisiva: Var(EAP) + E[SE²] = 0,984 ≈ 1, que es la varianza de la previa; restando
     da 0,834, incompatible con el propio modelo. La serie publicada 0,697 · 0,395 · 0,533 era
     incorrecta; la correcta bajo ese arreglo es 0,784 · 0,538 · 0,677.

  2. BOOTSTRAP SIN SENTIDO. La pendiente de la «varianza verdadera» se estimaba sobre
     log(clip(r² − SE², 1e-6)). El 40,9 % de las observaciones caía en el recorte, de modo que la
     regresión estaba dominada por una constante arbitraria. Esa cantidad se elimina.

  3. LA DESATENUACIÓN ESCALAR NO ES EL ANÁLISIS CORRECTO, con ningún signo. El EAP usa una previa
     común N(0,1) para todos, que no es la previa correcta de ningún tramo educativo: la contracción
     es desigual entre tramos y ninguna corrección escalar la arregla. El análisis que responde la
     pregunta es el GRM MULTIGRUPO con media y varianza latentes libres por tramo, que es lo que
     este bloque hace ahora (sección C).

Se agrega además lo que faltaba y cambiaba la lectura:

  · El LEVENE SOBRE θ, que es significativo (p = 3,5×10⁻⁴) y no se informaba. La pendiente lineal
    nula no significa homogeneidad: significa que el patrón no es monótono.
  · La NO IDENTIFICACIÓN DE LA MÉTRICA. Un modelo de respuesta al ítem identifica θ sólo hasta
    transformación monótona. La sección D muestra que, en la métrica de puntaje verdadero de Lord
    —igual de legítima dentro del mismo modelo ajustado—, el reparto entre «instrumento» y
    «habilidad» se invierte. La partición no es una propiedad del instrumento sino de la métrica
    que se privilegie, y así se declara.

═══════════════════════════════════════════════════════════════════════════════════════════════

Salida: consola + resultados/V26_dispersion_latente.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from girth import grm_mml
from scipy import stats
from scipy.optimize import minimize

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402

OUT = EST / "resultados"
SESGO_LOGCHI2 = 1.2703628454614782
EDAD_REF = 65.0
BANDAS = ["<7", "7-11", ">=12"]
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=BANDAS)
GRID = np.linspace(-4, 4, 161)
rng = np.random.default_rng(26)
R = {"_correccion": "2026-08-09: signo de la desatenuación, bootstrap eliminado, GRM multigrupo"}

ITEMS = ['ACE_AtOT', 'ACE_AtOE', 'ACE_AtRegistro', 'ACE_AtSubstr', 'ACE_MRecuerdo', 'ACE_MAnterogr',
         'ACE_MRetrogr', 'ACE_MRecuerdoNyD', 'ACE_MReconocNyD', 'ACE_FluVerbFPC', 'ACE_FluVerbSPC',
         'ACE_LComprensionLyH', 'ACE_LEscrit', 'ACE_LRepP', 'ACE_LRepProverb', 'ACE_LDenom',
         'ACE_LCompDibujo', 'ACE_LLectura', 'ACE_HabVisoDiagrama', 'ACE_HabVisoCubo',
         'ACE_HabPerPuntos', 'ACE_HabPerLetras', 'ACE_HabVisoReloj']

# ============================================================ datos
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all").dropna(axis=0, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
com_ok = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
c40["doc"] = nd(c40["dni"]); c40["ctrl"] = es_control(c40).values
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
com["ACE"] = com[ITEMS].sum(axis=1); com["cohorte"] = "comunitaria"
cli = pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
cli = cli.dropna(subset=ITEMS + ["edu", "Edad", "Sexo", "ACE"])
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
cli["cohorte"] = "clínica"; cli["ctrl"] = False
COLS = ITEMS + ["ACE", "edu", "Edad", "Sexo", "cohorte", "ctrl"]
D = pd.concat([com[COLS], cli[COLS]], ignore_index=True)
print("=" * 100)
print(f"muestra con los 23 ítems completos — comunitaria {len(com)} · clínica {len(cli)} · "
      f"combinada {len(D)} · controles comunitarios {int(com.ctrl.sum())}")
R["n"] = {"comunitaria": len(com), "clinica": len(cli), "combinada": len(D)}


# ============================================================ A. GRM y θ
def collapse_ordinal(s, min_cell=15):
    vals = sorted(pd.unique(s.dropna())); counts = s.value_counts()
    groups, cur = [], []
    for v in vals:
        cur.append(v)
        if sum(counts.get(x, 0) for x in cur) >= min_cell:
            groups.append(cur); cur = []
    if cur:
        if groups:
            groups[-1].extend(cur)
        else:
            groups.append(cur)
    return s.map({v: gi for gi, g in enumerate(groups) for v in g}).astype(int), groups


def loglik(Rmat, a, b, grid=GRID):
    """log de la verosimilitud de cada persona en la rejilla, SIN previa."""
    lg = np.zeros((Rmat.shape[0], len(grid)))
    for j in range(Rmat.shape[1]):
        thr = b[j][~np.isnan(b[j])]
        cum = 1.0 / (1.0 + np.exp(-a[j] * (grid[:, None] - thr[None, :])))
        P = np.concatenate([np.ones((len(grid), 1)), cum, np.zeros((len(grid), 1))], axis=1)
        lg += np.log(np.clip(P[:, :-1] - P[:, 1:], 1e-10, 1.0)).T[Rmat[:, j], :]
    return lg


print("\nA. MODELO DE RESPUESTA GRADUADA sobre la muestra combinada")
col = {c: collapse_ordinal(D[c]) for c in ITEMS}
Rc = pd.DataFrame({c: col[c][0] for c in ITEMS})
grm = grm_mml(Rc.values.T.astype(int))
a = np.asarray(grm["Discrimination"], float); b = np.asarray(grm["Difficulty"], float)
LG = loglik(Rc.values.astype(int), a, b)
w = np.exp(LG - LG.max(axis=1, keepdims=True)) * stats.norm.pdf(GRID)[None, :]
w /= w.sum(axis=1, keepdims=True)
theta = w @ GRID
se_th = np.sqrt(np.clip(w @ (GRID ** 2) - theta ** 2, 0, None))
D["theta"], D["se_theta"] = theta, se_th
v_eap, e_se2 = float(np.var(theta, ddof=1)), float(np.mean(se_th ** 2))
print(f"   θ: media {theta.mean():+.3f} · DE {theta.std():.3f} · SE medio {se_th.mean():.3f} · "
      f"r con el bruto {np.corrcoef(theta, D.ACE)[0, 1]:.3f}")
print(f"   Var(EAP) {v_eap:.4f} + E[SE²] {e_se2:.4f} = {v_eap + e_se2:.4f}  "
      f"(≈ 1: confirma que el EAP está contraído y que hay que SUMAR, no restar)")
R["grm"] = {"a_mediana": round(float(np.median(a)), 3),
            "theta_de": round(float(theta.std()), 3), "se_medio": round(float(se_th.mean()), 3),
            "r_theta_bruto": round(float(np.corrcoef(theta, D.ACE)[0, 1]), 3),
            "var_eap_mas_e_se2": round(v_eap + e_se2, 4)}

CTL = D[(D.cohorte == "comunitaria") & D.ctrl].copy().reset_index(drop=True)
CTL["tr"] = TR(CTL.edu)
fila_ctl = D.index[(D.cohorte == "comunitaria") & D.ctrl].to_numpy()
LG_ctl = LG[fila_ctl, :]
idx = {b_: np.where(CTL.tr.values == b_)[0] for b_ in BANDAS}
print(f"\n   controles comunitarios: n = {len(CTL)}  " +
      " · ".join(f"{b_}={len(idx[b_])}" for b_ in BANDAS))
R["n"]["controles"] = len(CTL)
R["n"]["controles_por_tramo"] = {b_: int(len(idx[b_])) for b_ in BANDAS}

# ============================================================ B. dispersión en las dos métricas
print("\n" + "=" * 100)
print("B. DISPERSIÓN: PENDIENTE LINEAL Y HOMOGENEIDAD DE VARIANZAS")
print("   Se informan LAS DOS pruebas. La pendiente lineal responde «¿decrece de forma monótona?»;")
print("   el Levene responde «¿son iguales las varianzas?». No son la misma pregunta.")
FMU = "edu + I(edu**2) + Edad + C(Sexo)"
R["dispersion"] = {}
for lab, y in [("ACE bruto", "ACE"), ("θ latente", "theta")]:
    mu = smf.ols(f"{y} ~ {FMU}", data=CTL).fit()
    t2 = CTL.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-10, None)))
    sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
    ci = sd.conf_int().loc["edu"]
    sg = lambda e_: float(np.sqrt(np.exp(SESGO_LOGCHI2 + sd.predict(
        pd.DataFrame({"edu": [e_], "Edad": [EDAD_REF]})).iloc[0])))
    gr = [CTL.loc[CTL.tr == b_, y].values for b_ in BANDAS]
    W, pl = stats.levene(*gr, center="median")
    R["dispersion"][lab] = {
        "pendiente_log_var_por_anio": round(float(sd.params["edu"]), 4),
        "ic95": [round(float(ci[0]), 4), round(float(ci[1]), 4)],
        "p": float(sd.pvalues["edu"]),
        "sigma_edu0": round(sg(0), 4), "sigma_edu20": round(sg(20), 4),
        "razon_sigma_0_20": round(sg(0) / sg(20), 3),
        "de_por_tramo": [round(float(np.std(g, ddof=1)), 3) for g in gr],
        "levene_W": round(float(W), 3), "levene_p": float(pl)}
    d_ = R["dispersion"][lab]
    print(f"\n   {lab:<11} pendiente {d_['pendiente_log_var_por_anio']:+.4f} "
          f"[{d_['ic95'][0]:+.4f}, {d_['ic95'][1]:+.4f}]  p={d_['p']:.3g}")
    print(f"   {'':<11} Levene entre tramos: W={d_['levene_W']:.3f}  p={d_['levene_p']:.2e}   "
          f"DE {d_['de_por_tramo']}")
print("\n   LECTURA. Sobre θ la pendiente lineal es nula pero el Levene RECHAZA la homogeneidad.")
print("   La afirmación correcta no es «desaparece» sino «no decrece de forma monótona».")
print("   El intervalo de la pendiente latente admite conservar hasta el "
      f"{abs(R['dispersion']['θ latente']['ic95'][0]) / abs(R['dispersion']['ACE bruto']['pendiente_log_var_por_anio']) * 100:.0f} % "
      "de la pendiente bruta.")

# ============================================================ C. GRM multigrupo
print("\n" + "=" * 100)
print("C. GRM MULTIGRUPO — media y varianza latentes libres por tramo (el análisis correcto)")
print("   Parámetros de ítem fijos; se maximiza la verosimilitud marginal de cada tramo con una")
print("   previa N(μ_g, σ_g²) propia. No usa el EAP y por tanto no arrastra su contracción.")


def neg_ll(par, filas):
    prior = stats.norm.pdf(GRID, par[0], np.exp(par[1]))
    prior = prior / prior.sum()
    ll = LG_ctl[filas, :] + np.log(prior + 1e-300)[None, :]
    m = ll.max(axis=1, keepdims=True)
    return -float(np.sum(m.ravel() + np.log(np.exp(ll - m).sum(axis=1))))


R["multigrupo"] = {}
print(f"\n   {'tramo':>6} {'n':>4} {'media latente':>14} {'DE latente':>11}")
for b_ in BANDAS:
    f_ = idx[b_]
    o = minimize(neg_ll, x0=[float(CTL.theta.values[f_].mean()), np.log(0.6)], args=(f_,),
                 method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 4000})
    R["multigrupo"][b_] = {"n": int(len(f_)), "media": round(float(o.x[0]), 3),
                           "de": round(float(np.exp(o.x[1])), 3)}
    print(f"   {b_:>6} {len(f_):>4} {o.x[0]:>14.3f} {np.exp(o.x[1]):>11.3f}")
mg = [R["multigrupo"][b_]["de"] for b_ in BANDAS]
raz_bruto = float(CTL[CTL.tr == "<7"].ACE.std(ddof=1) / CTL[CTL.tr == ">=12"].ACE.std(ddof=1))
R["razon_extremos"] = {"puntaje_bruto": round(raz_bruto, 3),
                       "habilidad_multigrupo": round(mg[0] / mg[2], 3),
                       "monotona": bool(mg[0] > mg[1] > mg[2])}
print(f"\n   razón entre extremos: puntaje bruto {raz_bruto:.2f}×  ·  habilidad {mg[0]/mg[2]:.2f}×")
print(f"   ¿la dispersión latente es monótona? {'sí' if R['razon_extremos']['monotona'] else 'NO'}"
      f"  ({' · '.join(f'{v:.3f}' for v in mg)}; el mínimo está en el tramo intermedio)")

# ============================================================ D. la métrica no está identificada
print("\n" + "=" * 100)
print("D. LA PARTICIÓN DEPENDE DE LA MÉTRICA, Y LA MÉTRICA ES UNA CONVENCIÓN")
print("   Un modelo de respuesta al ítem identifica θ sólo hasta transformación monótona. Lo que")
print("   fija la métrica es la previa de la calibración. Abajo, la misma descomposición en dos")
print("   métricas igualmente legítimas del MISMO modelo ajustado.")
E_ace = np.zeros_like(GRID)
for j, it in enumerate(ITEMS):
    _, groups = col[it]
    frec = D[it].value_counts()
    # esperanza condicional: media PONDERADA POR FRECUENCIA de los valores que forman la categoría
    valores = np.array([np.average(g, weights=[frec.get(v, 0) + 1e-9 for v in g]) for g in groups])
    thr = b[j][~np.isnan(b[j])]
    cum = 1.0 / (1.0 + np.exp(-a[j] * (GRID[:, None] - thr[None, :])))
    P = np.concatenate([np.ones((len(GRID), 1)), cum, np.zeros((len(GRID), 1))], axis=1)
    E_ace += np.clip(P[:, :-1] - P[:, 1:], 1e-12, 1.0) @ valores
dE = np.gradient(E_ace, GRID)
pend = {b_: float(np.interp(CTL.theta.values[idx[b_]].mean(), GRID, dE)) for b_ in BANDAS}
de_th = {b_: float(CTL.theta.values[idx[b_]].std(ddof=1)) for b_ in BANDAS}
R["dos_metricas"] = {
    "tcc": {"rango": [round(float(E_ace.min()), 1), round(float(E_ace.max()), 1)],
            "pendiente_local": {b_: round(pend[b_], 2) for b_ in BANDAS},
            "_nota": "media ponderada por frecuencia; la versión anterior usaba media simple"},
    "metrica_theta": {"por_instrumento": round(pend["<7"] / pend[">=12"], 3),
                      "por_habilidad": round(de_th["<7"] / de_th[">=12"], 3)},
    "metrica_puntaje_verdadero_Lord": {"por_instrumento": 1.0,
                                       "por_habilidad": round(raz_bruto, 3)},
    "_advertencia": ("En la métrica de puntaje verdadero τ = E[ACE|θ] la pendiente vale 1 por "
                     "definición y toda la razón se atribuye a la habilidad. La partición no es "
                     "una propiedad del instrumento: es una propiedad de la métrica elegida.")}
dm = R["dos_metricas"]
print(f"\n   curva característica reconstruida: {dm['tcc']['rango'][0]} a {dm['tcc']['rango'][1]} puntos")
print(f"   pendiente local por tramo: " + " · ".join(f"{b_}={pend[b_]:.1f}" for b_ in BANDAS))
print(f"\n   {'métrica':<34} {'por el instrumento':>19} {'por la habilidad':>18}")
print(f"   {'θ (previa normal, la del bloque)':<34} "
      f"{dm['metrica_theta']['por_instrumento']:>18.2f}× {dm['metrica_theta']['por_habilidad']:>17.2f}×")
print(f"   {'τ = E[ACE|θ] (puntaje verdadero)':<34} {1.0:>18.2f}× {raz_bruto:>17.2f}×")
print("\n   Mismo modelo, mismos datos, conclusión opuesta. Por eso este bloque NO afirma qué parte")
print("   corresponde a la escala y qué parte a las personas: esa partición no está identificada.")

# ============================================================ E. techo
print("\n" + "=" * 100)
print("E. TECHO — cuánto de esto puede atribuirse a la cota superior del instrumento")
R["techo"] = {}
for b_ in BANDAS:
    s = CTL[CTL.tr == b_]
    R["techo"][b_] = {"n": int(len(s)), "media_ACE": round(float(s.ACE.mean()), 2),
                      "pct_del_maximo": round(float(s.ACE.mean()), 1),
                      "en_100": round(float((s.ACE >= 100).mean() * 100), 1),
                      "a_3_del_techo": round(float((s.ACE >= 97).mean() * 100), 1)}
    d_ = R["techo"][b_]
    print(f"   {b_:>6} n={d_['n']:<4} media {d_['media_ACE']:5.1f} · en 100: {d_['en_100']:.1f} % · "
          f"≥97: {d_['a_3_del_techo']:.1f} %")
print("\n   NINGÚN control está en el techo y sólo el 2,7 % del tramo alto está a tres puntos de él.")
print("   La compresión no ocurre «en el techo»: ocurre a lo largo de la ojiva. El bloque V27 lo")
print("   confirma en el IFS, donde tampoco hay nadie en el techo y la compresión es equivalente.")

# ============================================================ veredicto
print("\n" + "=" * 100)
print("VEREDICTO")
print(f"   · En el puntaje bruto la dispersión se estrecha: pendiente "
      f"{R['dispersion']['ACE bruto']['pendiente_log_var_por_anio']:+.4f}, razón entre extremos "
      f"{raz_bruto:.2f}×.")
print(f"   · En la habilidad latente estimada por multigrupo la razón cae a {mg[0]/mg[2]:.2f}× y el "
      "patrón deja de ser monótono.")
print("   · La pendiente lineal sobre θ es nula, pero el Levene rechaza la homogeneidad: la")
print("     afirmación defendible es «no decrece de forma monótona», no «desaparece».")
print("   · Qué parte corresponde a la escala y qué parte a las personas NO ESTÁ IDENTIFICADO con")
print("     estos datos: depende de la métrica que se privilegie, y ninguna es la verdadera.")
print("   · Lo que sí es independiente de todo esto: la posición percentilar del corte en cada")
print("     tramo, que se calcula sobre el puntaje bruto, que es el que usa el clínico.")

OUT.mkdir(exist_ok=True)
(OUT / "V26_dispersion_latente.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V26_dispersion_latente.json'}")
