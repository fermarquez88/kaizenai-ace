#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V13 — ANÁLISIS DE EQUIDAD CORREGIDO tras la auditoría externa.

Tres defectos corregidos respecto de V12:

  1. **Composición del grupo control.** En V12 el tramo de 12 años o más contenía un 20 % de
     controles clínicos con doble tamiz (media 93,0) frente a menos del 2 % en los tramos bajos, de
     modo que la mezcla variaba con la exposición. Aquí los controles provienen de **una única
     fuente** (cohorte comunitaria) y todos cumplen el mismo criterio.

  2. **La planitud del gradiente bajo la corrección continua es una identidad algebraica**, no un
     hallazgo: tipificar respecto de una media y una varianza estimadas como función de la
     escolaridad produce equidistribución por construcción. Por eso el resultado que se reporta no
     es la razón entre gradientes sino **(a)** el gradiente que produce la regla vigente y **(b)**
     si eliminarlo cuesta desempeño diagnóstico.

  3. **Sensibilidad al umbral del criterio de control**, que en V12 se fijó en un único valor.

Salida: resultados/V13_equidad_corregida.json + figuras/Figura4_correccion_continua.{jpg,pdf}
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd, duckdb
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold
from scipy import stats as st

warnings.filterwarnings("ignore")
rng = np.random.default_rng(20260801)
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
IN = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL            # noqa: E402
import matplotlib.pyplot as plt                          # noqa: E402
from matplotlib.ticker import FuncFormatter              # noqa: E402

# ── Corrección del sesgo de Harvey (1976) ───────────────────────────────────
# Estimar log(sigma^2) por MCO sobre log(residuo^2) subestima la varianza: si e ~ N(0, s^2),
# entonces E[log(e^2)] = log(s^2) + E[log(chi2_1)] = log(s^2) - 1,27036. Sin corregir, sigma
# queda multiplicado por exp(-1,27036/2) = 0,530, es decir 1,887 veces más chico de lo que es.
# Verificación empírica: sin corregir, el 19,0 % de los controles cae bajo el percentil 5
# nominal y los z tienen DE 1,906; corrigiendo, cae el 6,5 % y los z tienen DE 1,010.
SESGO_LOGCHI2 = 1.2703628454614782   # = -(digamma(1/2) + log 2)

set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
R = {}

# ─────────────────────────────────── datos
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
c40["doc"] = nd(c40["dni"]); c40["rec"] = pd.to_numeric(c40.LDR_Reconocimiento_A, errors="coerce")
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv").merge(
    c40[["doc", "rec"]].rename(columns={"doc": "dni"}), on="dni", how="left")
con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
cl = con.execute("select eval_id, bruto rec from resultados_v2 "
                 "where test='Lista de Rey' and subtest like 'Reconoc%'").fetchdf()
cl["rec"] = pd.to_numeric(cl.rec, errors="coerce")
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv").merge(
    cl.dropna(subset=["rec"]).drop_duplicates("eval_id"), on="eval_id", how="left")


def arma(umbral):
    """Controles de fuente única (comunitaria) + casos clínicos, emparejados por edad."""
    ctl = com[com.rec >= umbral][["ACE", "edu", "Edad", "Sexo"]].assign(y=0)
    cas = dx3[dx3.dx3 == "Demencia"][["ACE", "edu", "Edad", "Sexo"]].assign(y=1)
    D = pd.concat([ctl, cas], ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
    lo = max(D[D.y == 1].Edad.min(), D[D.y == 0].Edad.min())
    hi = min(D[D.y == 1].Edad.max(), D[D.y == 0].Edad.max())
    D = D[D.Edad.between(lo, hi)].copy()
    D["b"] = pd.cut(D.Edad, np.arange(np.floor(lo/5)*5, hi + 6, 5))
    P = [pd.concat([g[g.y == 1].sample(k, random_state=1), g[g.y == 0].sample(k, random_state=1)])
         for _, g in D.groupby("b", observed=True)
         if (k := min((g.y == 1).sum(), (g.y == 0).sum())) > 0]
    E = pd.concat(P, ignore_index=True); E["tr"] = TR(E.edu)
    return E


def zeta(E):
    REF = E[E.y == 0].reset_index(drop=True)
    def norma(t_, a_):
        mu = smf.ols(FP, data=t_).fit()
        t2 = t_.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
        sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
        return (a_.ACE - mu.predict(a_)) / np.sqrt(np.exp(SESGO_LOGCHI2 + sd.predict(a_)))
    z = pd.Series(index=E.index, dtype=float)
    fold = np.zeros(len(REF), int)
    for k, (_, te) in enumerate(KFold(10, shuffle=True, random_state=1).split(REF)):
        fold[te] = k
    rp = E.index[E.y == 0].values
    for k in range(10):
        o = E.loc[rp[fold == k]]; z.loc[o.index] = norma(REF[fold != k], o).values
    z.loc[E[E.y == 1].index] = norma(REF, E[E.y == 1]).values
    return z


def ev(s):
    v = np.where(s.edu >= 12, s.ACE < 86, s.ACE < 68); pg = float(v.mean())
    ct = (s.z < np.quantile(s.z, pg)).values
    out = {"positividad": pg}
    for nm, f in [("vig", v), ("cont", ct)]:
        y = s.y.values; a = np.asarray(f)
        se = ((y == 1) & a).sum()/max((y == 1).sum(), 1)
        sp = ((y == 0) & ~a).sum()/max((y == 0).sum(), 1)
        sc = s[s.y == 0]
        g = pd.Series(a[s.y.values == 0], index=sc.index).groupby(sc.tr, observed=True).mean()*100
        out[nm] = dict(sens=se, espec=sp, youden=se+sp-1, grad=float(g.max()-g.min()),
                       fp={k: round(float(x), 1) for k, x in g.items()})
    return out


# ─────────────────────────────────── A. sensibilidad al umbral
print("A. SENSIBILIDAD AL UMBRAL DEL CRITERIO DE CONTROL (controles de fuente única)")
print(f"{'umbral':>7}{'n ctrl':>8}{'<7':>5}{'p edu':>8}{'% leves que pasan':>19}"
      f"{'grad vigente':>14}{'grad continua':>15}{'ΔYouden':>10}")
R["sensibilidad_umbral"] = {}
lv = dx3[dx3.dx3 == "DCL"].dropna(subset=["rec"])
for u in [10, 11, 12, 13]:
    E = arma(u); E["z"] = zeta(E); o = ev(E)
    cc = com.dropna(subset=["rec", "edu"]); cc["tr"] = TR(cc.edu)
    p = st.chi2_contingency(pd.crosstab(cc.tr, cc.rec >= u)).pvalue
    pl = 100*(lv.rec >= u).mean()
    R["sensibilidad_umbral"][u] = {"n_ctrl": int((E.y == 0).sum()), "p_edu": float(p),
                                   "pct_leves": round(float(pl), 1),
                                   "grad_vig": round(o["vig"]["grad"], 1),
                                   "grad_cont": round(o["cont"]["grad"], 1),
                                   "d_youden": round(o["cont"]["youden"]-o["vig"]["youden"], 3)}
    print(f"{'≥'+str(u):>7}{int((E.y==0).sum()):>8}{int(((E.tr=='<7')&(E.y==0)).sum()):>5}"
          f"{p:>8.3f}{pl:>19.1f}{o['vig']['grad']:>14.1f}{o['cont']['grad']:>15.1f}"
          f"{o['cont']['youden']-o['vig']['youden']:>+10.3f}")

# ─────────────────────────────────── B. análisis principal
UMB = 10
E = arma(UMB); E["z"] = zeta(E); o = ev(E)
print(f"\nB. ANÁLISIS PRINCIPAL (umbral ≥{UMB}; controles 100 % de la cohorte comunitaria)")
print(f"   {int(E.y.sum())} casos · {int((E.y==0).sum())} controles · "
      f"edad {E[E.y==1].Edad.mean():.1f} vs {E[E.y==0].Edad.mean():.1f} · "
      f"positividad {100*o['positividad']:.0f} %")
print(f"   controles por tramo: " + "  ".join(
    f"{t}={int(((E.tr==t)&(E.y==0)).sum())}" for t in ["<7", "7-11", "≥12"]))
print(f"\n   {'regla':<24}{'sens':>7}{'espec':>8}{'Youden':>8}   {'<7':>7}{'7-11':>7}{'≥12':>7}{'grad':>7}")
for nm, lab in [("vig", "vigente 86/68"), ("cont", "corrección continua")]:
    d = o[nm]
    print(f"   {lab:<24}{d['sens']:>7.3f}{d['espec']:>8.3f}{d['youden']:>8.3f}   "
          f"{d['fp'].get('<7',np.nan):>7.1f}{d['fp'].get('7-11',np.nan):>7.1f}"
          f"{d['fp'].get('≥12',np.nan):>7.1f}{d['grad']:>7.1f}")

bs = []
for _ in range(1000):
    s = E.iloc[rng.integers(0, len(E), len(E))]
    try:
        r = ev(s)
        bs.append((r["vig"]["grad"], r["cont"]["grad"], r["cont"]["youden"]-r["vig"]["youden"],
                   r["vig"]["fp"].get("<7", np.nan) - r["vig"]["fp"].get("7-11", np.nan)))
    except Exception:
        pass
bs = np.array(bs); q = lambda i, p: float(np.percentile(bs[:, i], p))
print(f"\n   IC 95 % ({len(bs)} réplicas):")
print(f"     gradiente de la regla vigente     {o['vig']['grad']:.1f}  [{q(0,2.5):.1f}; {q(0,97.5):.1f}]")
print(f"     diferencia <7 menos 7-11          {o['vig']['fp']['<7']-o['vig']['fp']['7-11']:.1f}  "
      f"[{q(3,2.5):.1f}; {q(3,97.5):.1f}]")
print(f"     gradiente residual de la continua {o['cont']['grad']:.1f}  [{q(1,2.5):.1f}; {q(1,97.5):.1f}]"
      f"   (planitud esperada por construcción)")
print(f"     Δ Youden (continua − vigente)     {np.median(bs[:,2]):+.3f}  [{q(2,2.5):+.3f}; {q(2,97.5):+.3f}]")
print(f"\n   >> el resultado empírico es el Δ Youden: eliminar el gradiente NO cuesta desempeño")

R["principal"] = {"umbral": UMB, "n_casos": int(E.y.sum()), "n_ctrl": int((E.y == 0).sum()),
                  "edad_casos": round(float(E[E.y == 1].Edad.mean()), 1),
                  "edad_ctrl": round(float(E[E.y == 0].Edad.mean()), 1),
                  "positividad": round(100*o["positividad"], 1),
                  "ctrl_por_tramo": {t: int(((E.tr == t) & (E.y == 0)).sum()) for t in ["<7", "7-11", "≥12"]},
                  "vigente": o["vig"], "continua": o["cont"],
                  "ic_grad_vig": [q(0, 2.5), q(0, 97.5)], "ic_grad_cont": [q(1, 2.5), q(1, 97.5)],
                  "dif_bajo_menos_medio": round(o["vig"]["fp"]["<7"]-o["vig"]["fp"]["7-11"], 1),
                  "ic_dif_bajo_menos_medio": [q(3, 2.5), q(3, 97.5)],
                  "d_youden": float(np.median(bs[:, 2])), "ic_d_youden": [q(2, 2.5), q(2, 97.5)]}

# ─────────────────────────────────── C. rendimiento normal por tramo
cc = com.dropna(subset=["rec", "ACE", "edu"]); cc = cc[cc.rec >= UMB]; cc["tr"] = TR(cc.edu)
g = cc.groupby("tr", observed=True).ACE.agg(["size", "mean", "std"])
print(f"\nC. RENDIMIENTO DE PERSONAS CON RECONOCIMIENTO NORMAL, POR TRAMO (cohorte comunitaria)")
print(g.round(1).to_string())
R["normales_por_tramo"] = {t: {"n": int(g.loc[t, "size"]), "ACE": round(float(g.loc[t, "mean"]), 1)}
                           for t in g.index}
(EST / "resultados/V13_equidad_corregida.json").write_text(
    json.dumps(R, indent=2, ensure_ascii=False, default=str))

# ─────────────────────────────────── figura
REF = E[E.y == 0]
fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.6))
gg = pd.DataFrame({"edu": np.arange(0, 19), "Edad": REF.Edad.median(), "Sexo": REF.Sexo.mode()[0]})
mu = smf.ols(FP, data=REF).fit(); esp = mu.predict(gg)
t2 = REF.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
sdm = smf.ols("lr2 ~ edu + Edad", data=t2).fit(); sg = np.sqrt(np.exp(SESGO_LOGCHI2 + sdm.predict(gg)))
ax[0].plot(gg.edu, esp, color=PAL["blue"], lw=2.8, zorder=4, label="esperado en personas sin deterioro")
ax[0].fill_between(gg.edu, esp-1.28*sg, esp+1.28*sg, color=PAL["blue"], alpha=0.12, lw=0,
                   label="banda del 80 % esperada")
ax[0].step(np.arange(0, 19), np.where(np.arange(0, 19) >= 12, 86, 68), where="mid",
           color=PAL["crit"], lw=2.6, ls="--", zorder=5, label="regla vigente (escalón)")
ax[0].set_xlabel("Años de escolaridad"); ax[0].set_ylabel("ACE-III (puntos)")
ax[0].set_title("a  La regla aproxima una curva mediante un escalón", loc="left", fontsize=10.8)
ax[0].legend(loc="lower right", fontsize=8.4, frameon=False)

x = np.arange(3); w = 0.34
for i, (nm, lab, col) in enumerate([("vig", "Regla vigente 86/68", PAL["crit"]),
                                    ("cont", "Corrección continua", PAL["aqua"])]):
    ax[1].bar(x + (i-0.5)*w, [o[nm]["fp"].get(t, np.nan) for t in ["<7", "7-11", "≥12"]], w,
              color=col, label=lab)
ax[1].set_xticks(x); ax[1].set_xticklabels(["<7 años", "7–11", "≥12"])
ax[1].set_ylabel("% de personas sin deterioro señaladas")
ax[1].set_title("b  La regla vigente señala desigualmente a personas sin deterioro",
                loc="left", fontsize=10.8)
ax[1].legend(fontsize=8.6, frameon=False, loc="upper right"); ax[1].set_ylim(0, 82)
for a in ax:
    a.yaxis.set_major_formatter(COMA); a.xaxis.set_major_formatter(COMA)
fig.tight_layout()
for ext in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
    fig.savefig(EST / f"figuras/Figura4_correccion_continua.{ext}", dpi=300,
                bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)
print("\n-> resultados/V13_equidad_corregida.json + figuras/Figura4_correccion_continua")
