#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V8 — DEMOSTRACIÓN: CORRECCIÓN CONTINUA FRENTE AL ESCALÓN.

Pregunta: si corrigiéramos de forma continua **sin señalar a más personas que la regla actual**,
¿desaparecería la inversión del tramo de 7 a 11 años?

Al igualar la tasa global de positividad, la diferencia que quede entre reglas es atribuible a la
**forma** de la corrección (escalón frente a curva), no a su severidad. Es la comparación que aísla
lo que queremos demostrar.

Procedimiento:
  1. El modelo normativo se estima **sólo sobre las personas sin demencia** (referencia correcta).
  2. Se modela la posición esperada (curva en escolaridad + edad + sexo) y, por separado, la
     **dispersión esperada**, porque la varianza no es constante (Breusch-Pagan p = 2×10⁻¹⁴).
  3. Los puntajes tipificados se obtienen por **validación cruzada de 10 particiones**, de modo que
     ninguna persona contribuye a su propia norma.
  4. El umbral tipificado se calibra para igualar la positividad global de la regla vigente.

Advertencia: **no es un estudio normativo.** La muestra de referencia no es poblacional y contiene
deterioro cognitivo leve. Es una demostración de forma, no una norma utilizable.

Salida: consola + resultados/V8_correccion_continua.json + figuras/Figura4_correccion_continua
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL          # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.ticker import FuncFormatter            # noqa: E402
set_style()
COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
R = {}

dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv")
ctrl = pd.read_csv(EST / "datos/controles_comunitarios.csv")
for c in ("Edad", "Sexo"):
    if c not in ctrl.columns:
        ctrl[c] = ctrl[[x for x in ctrl.columns if x.lower().startswith(c.lower())][0]]

cas = dx3[dx3.dx3.isin(["DCL", "Demencia"])][["ACE", "edu", "Edad", "Sexo", "dx3"]]
con = ctrl[["ACE", "edu", "Edad", "Sexo"]].assign(dx3="Sin demencia")
ext = dx3[dx3.dx3 == "Sin afectación"][["ACE", "edu", "Edad", "Sexo"]].assign(dx3="Sin demencia")
D = pd.concat([cas, con, ext], ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
D["tr"] = pd.cut(D.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
D["dem"] = (D.dx3 == "Demencia").astype(int)
D = D.reset_index(drop=True)
REF = D[D.dx3 == "Sin demencia"].reset_index(drop=True)
print(f"muestra total {len(D)}  |  referencia normativa (sin demencia) {len(REF)}")

FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"


def normativo(train, aplicar, con_dispersion=True):
    """Devuelve el puntaje tipificado de `aplicar` según la norma estimada en `train`."""
    mu = smf.ols(FP, data=train).fit()
    esp = mu.predict(aplicar)
    if not con_dispersion:
        return (aplicar.ACE - esp) / np.std(mu.resid, ddof=1)
    tr2 = train.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
    sd = smf.ols("lr2 ~ edu + Edad", data=tr2).fit()
    return (aplicar.ACE - esp) / np.sqrt(np.exp(sd.predict(aplicar)))


# ─────────────────────────────────── puntajes tipificados por validación cruzada
for etq, disp in [("z_pos", False), ("z_posdisp", True)]:
    z = pd.Series(index=D.index, dtype=float)
    kf = KFold(10, shuffle=True, random_state=20260801)
    for tri, tei in kf.split(REF):
        pass                                    # las particiones se usan sobre la referencia
    # cada partición entrena con 9/10 de la referencia y aplica a TODOS los que no la entrenaron
    idx_ref = REF.index.values
    fold = np.zeros(len(REF), dtype=int)
    for k, (_, te) in enumerate(KFold(10, shuffle=True, random_state=20260801).split(REF)):
        fold[te] = k
    ref_pos = D.index[D.dx3 == "Sin demencia"].values
    for k in range(10):
        tr = REF[fold != k]
        # aplica a los de referencia de esta partición y (una sola vez) a todos los casos
        obj = D.loc[ref_pos[fold == k]]
        z.loc[obj.index] = normativo(tr, obj, disp).values
    casos = D[D.dx3 != "Sin demencia"]
    z.loc[casos.index] = normativo(REF, casos, disp).values
    D[etq] = z
print("puntajes tipificados calculados por validación cruzada de 10 particiones")

# ─────────────────────────────────── reglas comparadas a igual positividad global
vig = np.where(D.edu >= 12, D.ACE < 86, D.ACE < 68)
pos_global = float(vig.mean())
print(f"\npositividad global de la regla vigente: {100*pos_global:.1f} % — se calibran las demás a ese valor")

REGLAS = {"vigente 86/68": vig,
          "corte único (calibrado)": D.ACE < np.quantile(D.ACE, pos_global),
          "continua, sólo posición": D.z_pos < np.quantile(D.z_pos, pos_global),
          "continua, posición y dispersión": D.z_posdisp < np.quantile(D.z_posdisp, pos_global)}

dd = D[D.dx3 != "DCL"]
sd = D[D.dx3 == "Sin demencia"]
print("\n" + "=" * 96)
print("COMPARACIÓN A IGUAL TASA GLOBAL DE POSITIVIDAD")
print("=" * 96)
print(f"{'regla':<34}{'sensib.':>9}{'especif.':>10}{'Youden':>9}   falsos positivos por tramo")
print(f"{'':<34}{'':>9}{'':>10}{'':>9}   {'<7':>7}{'7-11':>8}{'≥12':>7}{'rango':>8}")
R["comparacion"] = {}
for nm, fl in REGLAS.items():
    f = pd.Series(np.asarray(fl), index=D.index)
    a = f.loc[dd.index]
    y = dd.dem.values
    tp = int(((y == 1) & a.values).sum()); fn = int(((y == 1) & ~a.values).sum())
    fp = int(((y == 0) & a.values).sum()); tn = int(((y == 0) & ~a.values).sum())
    se, sp = tp/(tp+fn), tn/(tn+fp)
    g = f.loc[sd.index].groupby(sd.tr, observed=True).mean()*100
    rg = float(g.max()-g.min())
    R["comparacion"][nm] = {"sens": round(se, 3), "espec": round(sp, 3),
                            "youden": round(se+sp-1, 3),
                            "fp_tramo": {k: round(float(v), 1) for k, v in g.items()},
                            "rango_fp": round(rg, 1)}
    print(f"{nm:<34}{se:>9.3f}{sp:>10.3f}{se+sp-1:>9.3f}   {g.get('<7',np.nan):>7.1f}"
          f"{g.get('7-11',np.nan):>8.1f}{g.get('≥12',np.nan):>7.1f}{rg:>8.1f}")

inv = lambda g: g.get("7-11", np.nan) < min(g.get("<7", np.nan), g.get("≥12", np.nan))
print("\n¿persiste la inversión del tramo 7–11 (el menos señalado pese a menor escolaridad)?")
for nm in REGLAS:
    g = R["comparacion"][nm]["fp_tramo"]
    print(f"  {nm:<34}{'SÍ, invertido' if inv(g) else 'no, gradiente monótono'}")

# ─────────────────────────────────── figura
print("\ngenerando figura…")
fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.6))
g = pd.DataFrame({"edu": np.arange(0, 19), "Edad": REF.Edad.median(), "Sexo": REF.Sexo.mode()[0]})
mu = smf.ols(FP, data=REF).fit()
esp = mu.predict(g)
ax[0].plot(g.edu, esp, color=PAL["blue"], lw=2.8, label="esperado (corrección continua)", zorder=4)
tr2 = REF.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
sdm = smf.ols("lr2 ~ edu + Edad", data=tr2).fit()
s = np.sqrt(np.exp(sdm.predict(g)))
ax[0].fill_between(g.edu, esp-1.28*s, esp+1.28*s, color=PAL["blue"], alpha=0.12, lw=0,
                   label="banda del 80 % esperada")
ax[0].step(np.arange(0, 19), np.where(np.arange(0, 19) >= 12, 86, 68), where="mid",
           color=PAL["crit"], lw=2.6, ls="--", label="regla vigente (escalón)", zorder=5)
ax[0].set_xlabel("Años de escolaridad"); ax[0].set_ylabel("ACE-III (puntos)")
ax[0].set_title("a  La regla aproxima una curva con un escalón", loc="left", fontsize=10.8)
ax[0].legend(loc="lower right", fontsize=8.4, frameon=False)

et = list(REGLAS); x = np.arange(3); w = 0.2
cols = [PAL["crit"], PAL["muted"], PAL["orange"], PAL["aqua"]]
for i, nm in enumerate(et):
    v = [R["comparacion"][nm]["fp_tramo"].get(t, np.nan) for t in ["<7", "7-11", "≥12"]]
    ax[1].bar(x + (i-1.5)*w, v, w, color=cols[i], label=nm)
ax[1].set_xticks(x); ax[1].set_xticklabels(["<7 años", "7–11", "≥12"])
ax[1].set_ylabel("% de personas sin demencia señaladas")
ax[1].set_title("b  A igual positividad global, la forma cambia el reparto", loc="left", fontsize=10.8)
ax[1].legend(fontsize=8, frameon=False, loc="upper right")
for a in ax:
    a.yaxis.set_major_formatter(COMA); a.xaxis.set_major_formatter(COMA)
fig.tight_layout()
for ext_ in ("jpg", "pdf"):
    kw = {"pil_kwargs": {"quality": 95}} if ext_ == "jpg" else {}
    fig.savefig(EST / f"figuras/Figura4_correccion_continua.{ext_}", dpi=300,
                bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)
print("-> figuras/Figura4_correccion_continua.jpg + .pdf")

R["positividad_global"] = round(100*pos_global, 1)
(EST / "resultados/V8_correccion_continua.json").write_text(
    json.dumps(R, indent=2, ensure_ascii=False, default=str))
print("-> resultados/V8_correccion_continua.json")
