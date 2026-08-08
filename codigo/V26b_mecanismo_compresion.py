#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V26b — MECANISMO. Si el estrechamiento de la dispersión no está en la habilidad, ¿de dónde sale?

V26 encontró que la dispersión del ACE-III entre controles se estrecha monótonamente con la
escolaridad en el PUNTAJE BRUTO (13,2 -> 5,8; razón 2,27×) pero NO en la habilidad latente
(pendiente +0,005; p = 0,85). Un nulo no es una explicación. Aquí se testea el mecanismo
candidato y se cuantifica.

MECANISMO PROPUESTO. El puntaje bruto es una función ojival de θ (curva característica del test).
Su pendiente dE[ACE]/dθ es máxima en el centro de la escala y decae hacia los extremos. Los
controles de alta escolaridad viven cerca del techo, donde la pendiente es baja: una misma
dispersión de habilidad se traduce allí en MENOS puntos de ACE-III. La compresión no es una
propiedad de las personas sino del instrumento.

PREDICCIÓN FALSABLE. Si el mecanismo es correcto, entonces para cada tramo educativo
        DE(ACE) ≈ |dE[ACE]/dθ| evaluada en la media del tramo  ×  DE(θ) del tramo
debe reproducir la DE observada del puntaje bruto. Si el mecanismo no alcanza, quedará residuo.

Se testea además la forma de la dispersión sobre θ (¿plana o en U?) y se verifica que la
consecuencia clínica del manuscrito —la posición percentilar del corte por tramo— no depende de
nada de esto, porque se calcula sobre el puntaje bruto, que es el que usa el clínico.

Salida: consola + resultados/V26b_mecanismo.json + figuras/FiguraS_compresion.{jpg,pdf}
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
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL                 # noqa: E402
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.ticker import FuncFormatter                  # noqa: E402

set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
OUT = EST / "resultados"; FIG = EST / "figuras"
SESGO_LOGCHI2 = 1.2703628454614782
EDAD_REF = 65.0
BANDAS = ["<7", "7-11", ">=12"]
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=BANDAS)
rng = np.random.default_rng(261)
R = {}

ITEMS = ['ACE_AtOT', 'ACE_AtOE', 'ACE_AtRegistro', 'ACE_AtSubstr', 'ACE_MRecuerdo', 'ACE_MAnterogr',
         'ACE_MRetrogr', 'ACE_MRecuerdoNyD', 'ACE_MReconocNyD', 'ACE_FluVerbFPC', 'ACE_FluVerbSPC',
         'ACE_LComprensionLyH', 'ACE_LEscrit', 'ACE_LRepP', 'ACE_LRepProverb', 'ACE_LDenom',
         'ACE_LCompDibujo', 'ACE_LLectura', 'ACE_HabVisoDiagrama', 'ACE_HabVisoCubo',
         'ACE_HabPerPuntos', 'ACE_HabPerLetras', 'ACE_HabVisoReloj']

# ============================================================ datos (idéntico a V26)
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
    return s.map(mp).astype(int), len(groups), groups


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


col = {c: collapse_ordinal(D[c]) for c in ITEMS}
Rc = pd.DataFrame({c: col[c][0] for c in ITEMS})
grm = grm_mml(Rc.values.T.astype(int))
a = np.asarray(grm["Discrimination"], float)
b = np.asarray(grm["Difficulty"], float)
theta, se_th = eap(Rc.values.astype(int), a, b)
D["theta"], D["se_theta"] = theta, se_th
CTL = D[(D.cohorte == "comunitaria") & D.ctrl].copy().reset_index(drop=True)
CTL["tr"] = TR(CTL.edu)
print("=" * 96)
print(f"controles comunitarios n = {len(CTL)}  " +
      " · ".join(f"{b_}={int((CTL.tr == b_).sum())}" for b_ in BANDAS))

# ============================================================ A. curva característica del test
# El GRM se ajustó sobre categorías COLAPSADAS. Para volver a puntos de ACE-III se mapea cada
# categoría colapsada al valor MEDIO de los puntajes originales que la componen.
print("\nA. CURVA CARACTERÍSTICA DEL TEST — E[ACE-III | θ] y su pendiente")
grid = np.linspace(-3.5, 3.0, 261)
E_ace = np.zeros_like(grid)
for j, it in enumerate(ITEMS):
    _, K, groups = col[it]
    valores = np.array([np.mean(g) for g in groups])          # puntos de ACE-III por categoría
    thr = b[j][~np.isnan(b[j])]
    cum = 1.0 / (1.0 + np.exp(-a[j] * (grid[:, None] - thr[None, :])))
    P = np.concatenate([np.ones((len(grid), 1)), cum, np.zeros((len(grid), 1))], axis=1)
    P = np.clip(P[:, :-1] - P[:, 1:], 1e-12, 1.0)
    E_ace += P @ valores
dE = np.gradient(E_ace, grid)                                  # pendiente dE[ACE]/dθ
print(f"   E[ACE|θ]: {E_ace.min():.1f} a {E_ace.max():.1f} puntos · pendiente máxima "
      f"{dE.max():.1f} pts/θ en θ={grid[np.argmax(dE)]:+.2f}")
R["tcc"] = {"ace_min": round(float(E_ace.min()), 1), "ace_max": round(float(E_ace.max()), 1),
            "pendiente_max": round(float(dE.max()), 2),
            "theta_de_pendiente_max": round(float(grid[np.argmax(dE)]), 3)}

# ============================================================ B. la predicción falsable
print("\nB. PREDICCIÓN:  DE(ACE) del tramo  ≈  |dE[ACE]/dθ| en la media del tramo  ×  DE(θ) del tramo")
R["prediccion"] = {}
filas = []
for b_ in BANDAS:
    s = CTL[CTL.tr == b_]
    th_m = float(s.theta.mean()); th_sd = float(s.theta.std(ddof=1))
    pend = float(np.interp(th_m, grid, dE))
    pred = pend * th_sd
    obs = float(s.ACE.std(ddof=1))
    R["prediccion"][b_] = {"n": int(len(s)), "theta_media": round(th_m, 3),
                           "theta_de": round(th_sd, 3), "pendiente_local": round(pend, 2),
                           "de_predicha": round(pred, 2), "de_observada": round(obs, 2),
                           "razon_pred_obs": round(pred / obs, 3)}
    filas.append((b_, len(s), th_m, th_sd, pend, pred, obs))
    print(f"   {b_:>5}  n={len(s):<4} θ medio {th_m:+.3f} · DE(θ) {th_sd:.3f} · "
          f"pendiente local {pend:5.1f} pts/θ  ->  DE predicha {pred:5.2f}  vs observada {obs:5.2f}  "
          f"({pred/obs:.2f}×)")
raz = [f[5] / f[6] for f in filas]
print(f"\n   Razón predicha/observada en los tres tramos: " +
      "  ".join(f"{r:.2f}" for r in raz) +
      "   -> el mecanismo reproduce la DE observada" if max(abs(np.array(raz) - 1)) < 0.25
      else f"\n   Razón predicha/observada: {['%.2f' % r for r in raz]} -> el mecanismo no alcanza")
R["prediccion"]["razones"] = [round(float(r), 3) for r in raz]

# cuánto del cociente de DE brutas entre extremos explica la pendiente local
p_lo = R["prediccion"]["<7"]["pendiente_local"]; p_hi = R["prediccion"][">=12"]["pendiente_local"]
sd_lo = R["prediccion"]["<7"]["de_observada"]; sd_hi = R["prediccion"][">=12"]["de_observada"]
th_lo = R["prediccion"]["<7"]["theta_de"]; th_hi = R["prediccion"][">=12"]["theta_de"]
print(f"\n   descomposición del cociente de DE brutas entre extremos ({sd_lo/sd_hi:.2f}×):")
print(f"     por la pendiente del instrumento   {p_lo/p_hi:.2f}×")
print(f"     por la dispersión de habilidad     {th_lo/th_hi:.2f}×")
R["descomposicion"] = {"cociente_de_bruto": round(sd_lo / sd_hi, 3),
                       "por_instrumento": round(p_lo / p_hi, 3),
                       "por_habilidad": round(th_lo / th_hi, 3)}

# ============================================================ C. ¿la dispersión de θ es plana o en U?
print("\nC. FORMA DE LA DISPERSIÓN SOBRE θ  (lineal frente a cuadrática en escolaridad)")
FMU = "edu + I(edu**2) + Edad + C(Sexo)"
mu = smf.ols(f"theta ~ {FMU}", data=CTL).fit()
t2 = CTL.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-10, None)))
m_lin = smf.ols("lr2 ~ edu + Edad", data=t2).fit(cov_type="HC3")
m_cua = smf.ols("lr2 ~ edu + I(edu**2) + Edad", data=t2).fit(cov_type="HC3")
c2 = m_cua.params["I(edu ** 2)"]; ci2 = m_cua.conf_int().loc["I(edu ** 2)"]
vert = -m_cua.params["edu"] / (2 * c2) if c2 else np.nan
print(f"   término cuadrático {c2:+.5f}  IC95 [{ci2[0]:+.5f}, {ci2[1]:+.5f}]  "
      f"p={m_cua.pvalues['I(edu ** 2)']:.4f}")
print(f"   vértice en {vert:.1f} años de escolaridad  "
      f"({'mínimo' if c2 > 0 else 'máximo'} de la dispersión)")
R["forma_theta"] = {"cuadratico": round(float(c2), 5),
                    "ic95": [round(float(ci2[0]), 5), round(float(ci2[1]), 5)],
                    "p": float(m_cua.pvalues["I(edu ** 2)"]),
                    "vertice_anios": round(float(vert), 2),
                    "es_minimo": bool(c2 > 0)}

print("\n   contraste de varianzas por pares (Brown-Forsythe sobre θ):")
R["pares_theta"] = {}
for x, y in [("<7", "7-11"), ("7-11", ">=12"), ("<7", ">=12")]:
    g1 = CTL.loc[CTL.tr == x, "theta"].values; g2 = CTL.loc[CTL.tr == y, "theta"].values
    st, p = stats.levene(g1, g2, center="median")
    R["pares_theta"][f"{x} vs {y}"] = {"W": round(float(st), 3), "p": float(p),
                                       "de1": round(float(np.std(g1, ddof=1)), 3),
                                       "de2": round(float(np.std(g2, ddof=1)), 3)}
    print(f"     {x:>5} vs {y:<5}  DE {np.std(g1, ddof=1):.3f} vs {np.std(g2, ddof=1):.3f}   "
          f"W={st:6.3f}  p={p:.4f}")

# ============================================================ D. la consecuencia clínica no cambia
print("\nD. LA CONSECUENCIA CLÍNICA SE CALCULA SOBRE EL BRUTO Y NO DEPENDE DE NADA DE ESTO")
mu_b = smf.ols(f"ACE ~ {FMU}", data=CTL).fit(cov_type="HC3")
t2b = CTL.assign(lr2=np.log(np.clip(mu_b.resid ** 2, 1e-10, None)))
sd_b = smf.ols("lr2 ~ edu + Edad", data=t2b).fit(cov_type="HC3")
R["percentil_corte"] = {}
for e_, corte in [(0, 68), (4, 68), (11, 68), (12, 86), (17, 86)]:
    g = pd.DataFrame({"edu": [e_], "Edad": [EDAD_REF], "Sexo": [CTL.Sexo.mode()[0]]})
    m_ = float(mu_b.predict(g).iloc[0])
    s_ = float(np.sqrt(np.exp(SESGO_LOGCHI2 + sd_b.predict(g).iloc[0])))
    pct = float(stats.norm.cdf((corte - m_) / s_) * 100)
    R["percentil_corte"][f"edu{e_}_corte{corte}"] = {"esperado": round(m_, 1), "sigma": round(s_, 2),
                                                     "percentil_del_corte": round(pct, 1)}
    print(f"   {e_:>2} años de escuela · corte {corte}:  esperado {m_:5.1f} (σ {s_:4.1f})  "
          f"-> el corte cae en el percentil {pct:4.1f}")

# ============================================================ figura
fig, ax = plt.subplots(1, 3, figsize=(11.4, 3.5))
COLS3 = {"<7": PAL["red"], "7-11": PAL["orange"], ">=12": PAL["blue"]}
ETI = {"<7": "menos de 7", "7-11": "7 a 11", ">=12": "12 o más"}

ax[0].plot(grid, E_ace, color=PAL["ink2"], lw=1.8)
for b_ in BANDAS:
    s = CTL[CTL.tr == b_]; tm = s.theta.mean()
    ax[0].plot([tm], [np.interp(tm, grid, E_ace)], "o", ms=6, color=COLS3[b_],
               label=f"{ETI[b_]} años")
ax[0].set_xlabel("habilidad latente θ"); ax[0].set_ylabel("ACE-III esperado")
ax[0].set_title("a · el puntaje comprime cerca del techo", loc="left")
ax[0].legend(frameon=False, fontsize=7, loc="lower right")
ax[0].yaxis.set_major_formatter(COMA); ax[0].xaxis.set_major_formatter(COMA)

ax[1].plot(grid, dE, color=PAL["ink2"], lw=1.8)
for b_ in BANDAS:
    tm = CTL.loc[CTL.tr == b_, "theta"].mean()
    ax[1].plot([tm], [np.interp(tm, grid, dE)], "o", ms=6, color=COLS3[b_])
ax[1].set_xlabel("habilidad latente θ"); ax[1].set_ylabel("puntos de ACE-III por unidad de θ")
ax[1].set_title("b · pendiente del instrumento", loc="left")
ax[1].xaxis.set_major_formatter(COMA); ax[1].yaxis.set_major_formatter(COMA)

# panel c: las dos dispersiones normalizadas al tramo de menor escolaridad. Se evita el eje
# gemelo, que induce a comparar magnitudes sin unidad común.
x = np.arange(3); w = 0.36
obs_b = np.array([R["prediccion"][b_]["de_observada"] for b_ in BANDAS], float)
# el desvío de habilidad libre de error de medición se toma de V26, que lo estima y lo publica
V26 = json.loads((OUT / "V26_dispersion_latente.json").read_text())
th_b = np.array([V26["var_verdadera"][b_]["de_verdadera"] for b_ in BANDAS], float)
nb, nh = obs_b / obs_b[0] * 100, th_b / th_b[0] * 100
ax2 = ax[2]
ax2.bar(x - w / 2, nb, w, color=PAL["blue"], label="puntaje bruto")
ax2.bar(x + w / 2, nh, w, color=PAL["aqua"], label="habilidad θ (sin error)")
for xi, (a_, b2_) in enumerate(zip(nb, nh)):
    ax2.text(xi - w / 2, a_ + 2, f"{a_:.0f}", ha="center", fontsize=7.5, color=PAL["blue"])
    ax2.text(xi + w / 2, b2_ + 2, f"{b2_:.0f}", ha="center", fontsize=7.5, color=PAL["aqua"])
ax2.axhline(100, color=PAL["baseline"], lw=0.7, ls=":")
ax2.set_xticks(x); ax2.set_xticklabels([ETI[b_] for b_ in BANDAS], fontsize=8)
ax2.set_xlabel("años de escolaridad")
ax2.set_ylabel("dispersión, % del tramo de menor escolaridad")
ax2.set_ylim(0, 118)
ax2.set_title("c · monótona en el bruto, no en la habilidad", loc="left")
ax2.yaxis.set_major_formatter(COMA)
ax2.legend(frameon=False, fontsize=7, loc="upper right")

fig.tight_layout()
for ext in ("jpg", "pdf"):
    fig.savefig(FIG / f"FiguraS_compresion.{ext}", dpi=300, bbox_inches="tight")
print(f"\n-> {FIG/'FiguraS_compresion.jpg'}")

OUT.mkdir(exist_ok=True)
(OUT / "V26b_mecanismo.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"-> {OUT/'V26b_mecanismo.json'}")
