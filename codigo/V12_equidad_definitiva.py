#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V12 — ANÁLISIS DE EQUIDAD DEFINITIVO, con controles definidos por un criterio cognitivo
independiente del ACE-III y ciego a la escolaridad.

Solución al problema detectado en la revisión: los controles definidos por ausencia de compromiso
funcional resultaron indistinguibles de los casos de deterioro leve en baja escolaridad. La causa
era que el criterio funcional —autoinformado en el 73 % de los casos— no excluye deterioro.

**Criterio nuevo:** memoria de **reconocimiento de lista**, presente en ambas bases con la misma
escala (0–15) y con dependencia educativa nula (0,027 desviaciones por año; medias 12,2 · 12,2 ·
12,8 por tramo educativo; independencia respecto del tramo p = 0,198 en el umbral empleado).
El criterio se valida por sí mismo: separa los grupos clínicos (13,25 sin deterioro · 10,93
deterioro leve · 8,55 deterioro moderado o severo).

Además: emparejamiento por edad, desenlace restringido a deterioro moderado o severo, e intervalos
de confianza por remuestreo sobre todas las cantidades.

Salida: resultados/V12_equidad_definitiva.json + figuras/Figura4_correccion_continua.{jpg,pdf}
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd, duckdb
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")
rng = np.random.default_rng(20260801)
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
IN = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL            # noqa: E402
import matplotlib.pyplot as plt                          # noqa: E402
from matplotlib.ticker import FuncFormatter              # noqa: E402
set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
R = {}

# ─────────────────────────────────── datos con la medida de reconocimiento
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
c40["doc"] = nd(c40["dni"]); c40["rec"] = pd.to_numeric(c40.LDR_Reconocimiento_A, errors="coerce")
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
M = com.merge(c40[["doc", "rec"]].rename(columns={"doc": "dni"}), on="dni", how="left")

con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
cl = con.execute("select eval_id, bruto rec from resultados_v2 "
                 "where test='Lista de Rey' and subtest like 'Reconoc%'").fetchdf()
cl["rec"] = pd.to_numeric(cl.rec, errors="coerce")
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv").merge(
    cl.dropna(subset=["rec"]).drop_duplicates("eval_id"), on="eval_id", how="left")

UMB = 10                                    # umbral educativamente neutral (p = 0,198)
ctl = pd.concat([
    M[M.rec >= UMB][["ACE", "edu", "Edad", "Sexo"]],
    dx3[(dx3.dx3 == "Sin afectación") & (dx3.rec >= UMB)][["ACE", "edu", "Edad", "Sexo"]]
], ignore_index=True).assign(y=0)
cas = dx3[dx3.dx3 == "Demencia"][["ACE", "edu", "Edad", "Sexo"]].assign(y=1)
D = pd.concat([ctl, cas], ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])

lo, hi = max(D[D.y == 1].Edad.min(), D[D.y == 0].Edad.min()), min(D[D.y == 1].Edad.max(), D[D.y == 0].Edad.max())
D = D[D.Edad.between(lo, hi)].copy()
D["b"] = pd.cut(D.Edad, np.arange(np.floor(lo/5)*5, hi + 6, 5))
E = pd.concat([pd.concat([g[g.y == 1].sample(min((g.y == 1).sum(), (g.y == 0).sum()), random_state=1),
                          g[g.y == 0].sample(min((g.y == 1).sum(), (g.y == 0).sum()), random_state=1)])
               for _, g in D.groupby("b", observed=True)
               if min((g.y == 1).sum(), (g.y == 0).sum()) > 0], ignore_index=True)
E["tr"] = TR(E.edu)
print(f"casos {int(E.y.sum())} · controles {int((E.y==0).sum())} · "
      f"edad {E[E.y==1].Edad.mean():.1f} vs {E[E.y==0].Edad.mean():.1f}")

REF = E[E.y == 0].reset_index(drop=True)
FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"


def norma(tr_, ap):
    mu = smf.ols(FP, data=tr_).fit()
    t2 = tr_.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
    sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
    return (ap.ACE - mu.predict(ap)) / np.sqrt(np.exp(sd.predict(ap)))


z = pd.Series(index=E.index, dtype=float)
fold = np.zeros(len(REF), int)
for k, (_, te) in enumerate(KFold(10, shuffle=True, random_state=1).split(REF)):
    fold[te] = k
rp = E.index[E.y == 0].values
for k in range(10):
    o = E.loc[rp[fold == k]]; z.loc[o.index] = norma(REF[fold != k], o).values
z.loc[E[E.y == 1].index] = norma(REF, E[E.y == 1]).values
E["z"] = z


def ev(s):
    v = np.where(s.edu >= 12, s.ACE < 86, s.ACE < 68); pg = float(v.mean())
    ct = (s.z < np.quantile(s.z, pg)).values
    out = {}
    for nm, f in [("vig", v), ("cont", ct)]:
        y = s.y.values; a = np.asarray(f)
        se = ((y == 1) & a).sum()/max((y == 1).sum(), 1)
        sp = ((y == 0) & ~a).sum()/max((y == 0).sum(), 1)
        sc = s[s.y == 0]
        g = pd.Series(a[s.y.values == 0], index=sc.index).groupby(sc.tr, observed=True).mean()*100
        out[nm] = dict(sens=se, espec=sp, youden=se+sp-1, rango=float(g.max()-g.min()),
                       fp={k: round(float(x), 1) for k, x in g.items()})
    return out


o = ev(E)
print(f"\n{'regla':<24}{'sens':>7}{'espec':>8}{'Youden':>8}   {'<7':>7}{'7-11':>7}{'≥12':>7}{'rango':>8}")
for nm, lab in [("vig", "vigente 86/68"), ("cont", "corrección continua")]:
    d = o[nm]
    print(f"{lab:<24}{d['sens']:>7.3f}{d['espec']:>8.3f}{d['youden']:>8.3f}   "
          f"{d['fp'].get('<7',np.nan):>7.1f}{d['fp'].get('7-11',np.nan):>7.1f}"
          f"{d['fp'].get('≥12',np.nan):>7.1f}{d['rango']:>8.1f}")

bs = []
for _ in range(1000):
    s = E.iloc[rng.integers(0, len(E), len(E))]
    try:
        r = ev(s)
        bs.append((r["vig"]["rango"], r["cont"]["rango"],
                   r["vig"]["rango"]/max(r["cont"]["rango"], .01),
                   r["cont"]["youden"] - r["vig"]["youden"]))
    except Exception:
        pass
bs = np.array(bs); q = lambda i, p: float(np.percentile(bs[:, i], p))
print(f"\nIC 95 % ({len(bs)} réplicas):")
print(f"  gradiente vigente  {o['vig']['rango']:.1f}  [{q(0,2.5):.1f}; {q(0,97.5):.1f}]")
print(f"  gradiente continua {o['cont']['rango']:.1f}  [{q(1,2.5):.1f}; {q(1,97.5):.1f}]")
print(f"  razón              {np.median(bs[:,2]):.1f}×  [{q(2,2.5):.1f}; {q(2,97.5):.1f}]")
print(f"  Δ Youden           {np.median(bs[:,3]):+.3f}  [{q(3,2.5):+.3f}; {q(3,97.5):+.3f}]")

R = {"umbral_reconocimiento": UMB, "n_casos": int(E.y.sum()), "n_controles": int((E.y == 0).sum()),
     "edad_casos": round(float(E[E.y == 1].Edad.mean()), 1),
     "edad_controles": round(float(E[E.y == 0].Edad.mean()), 1),
     "controles_por_tramo": {t: int(((E.tr == t) & (E.y == 0)).sum()) for t in ["<7", "7-11", "≥12"]},
     "vigente": o["vig"], "continua": o["cont"],
     "ic_rango_vig": [q(0, 2.5), q(0, 97.5)], "ic_rango_cont": [q(1, 2.5), q(1, 97.5)],
     "razon": float(np.median(bs[:, 2])), "ic_razon": [q(2, 2.5), q(2, 97.5)],
     "dif_youden": float(np.median(bs[:, 3])), "ic_dif_youden": [q(3, 2.5), q(3, 97.5)]}
(EST / "resultados/V12_equidad_definitiva.json").write_text(
    json.dumps(R, indent=2, ensure_ascii=False, default=str))

# ─────────────────────────────────── Figura 4
fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.6))
g = pd.DataFrame({"edu": np.arange(0, 19), "Edad": REF.Edad.median(), "Sexo": REF.Sexo.mode()[0]})
mu = smf.ols(FP, data=REF).fit(); esp = mu.predict(g)
t2 = REF.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
sdm = smf.ols("lr2 ~ edu + Edad", data=t2).fit(); sg = np.sqrt(np.exp(sdm.predict(g)))
ax[0].plot(g.edu, esp, color=PAL["blue"], lw=2.8, zorder=4, label="esperado en personas sin deterioro")
ax[0].fill_between(g.edu, esp-1.28*sg, esp+1.28*sg, color=PAL["blue"], alpha=0.12, lw=0,
                   label="banda del 80 % esperada")
ax[0].step(np.arange(0, 19), np.where(np.arange(0, 19) >= 12, 86, 68), where="mid",
           color=PAL["crit"], lw=2.6, ls="--", zorder=5, label="regla vigente (escalón)")
ax[0].set_xlabel("Años de escolaridad"); ax[0].set_ylabel("ACE-III (puntos)")
ax[0].set_title("a  La regla aproxima una curva mediante un escalón", loc="left", fontsize=10.8)
ax[0].legend(loc="lower right", fontsize=8.4, frameon=False)

x = np.arange(3); w = 0.34
for i, (nm, lab, col) in enumerate([("vig", "Regla vigente 86/68", PAL["crit"]),
                                    ("cont", "Corrección continua", PAL["aqua"])]):
    v = [o[nm]["fp"].get(t, np.nan) for t in ["<7", "7-11", "≥12"]]
    ax[1].bar(x + (i-0.5)*w, v, w, color=col, label=lab)
ax[1].set_xticks(x); ax[1].set_xticklabels(["<7 años", "7–11", "≥12"])
ax[1].set_ylabel("% de personas sin deterioro señaladas")
ax[1].set_title("b  A igual positividad, la forma cambia quién queda señalado",
                loc="left", fontsize=10.8)
ax[1].legend(fontsize=8.6, frameon=False, loc="upper right")
ax[1].annotate("", xy=(-0.17, o["vig"]["fp"]["<7"]), xytext=(0.17, o["cont"]["fp"]["<7"]),
               arrowprops=dict(arrowstyle="<->", color=PAL["ink2"], lw=1.2))
ax[1].text(0, (o["vig"]["fp"]["<7"] + o["cont"]["fp"]["<7"])/2 + 3,
           f"−{o['vig']['fp']['<7']-o['cont']['fp']['<7']:.0f}".replace(".", ",") + " pp",
           ha="center", fontsize=9.4, color=PAL["ink2"], fontweight="semibold")
ax[1].set_ylim(0, 78)
for a in ax:
    a.yaxis.set_major_formatter(COMA); a.xaxis.set_major_formatter(COMA)
fig.tight_layout()
for ext in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
    fig.savefig(EST / f"figuras/Figura4_correccion_continua.{ext}", dpi=300,
                bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)
print("\n-> resultados/V12_equidad_definitiva.json + figuras/Figura4_correccion_continua")
