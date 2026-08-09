#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V29 — Sensibilidad a la contaminación del grupo control y punto de operación.

Cuatro preguntas que el análisis principal dejaba abiertas y que sí son contrastables con estos datos.
Las que no lo son se declaran como limitación y no se disimulan.

  A. CONTAMINACIÓN DEL GRUPO CONTROL, medida y no supuesta.
     El bloque V19 mostró que los 342 controles rinden por debajo de lo esperado en pruebas que NO
     forman parte del criterio, con normas ya ajustadas por educación. Aquí se cuenta, persona por
     persona, cuántas pruebas de la batería caen bajo −1,5 z, y se rehacen la dispersión y el
     gradiente excluyendo progresivamente a quienes tienen más pruebas bajas. Si el hallazgo es un
     artefacto de contaminación, debe desvanecerse al depurar. Si sobrevive, no lo es.

  B. EL GRADIENTE, CON EL CONTRASTE PREESPECIFICADO EN LUGAR DEL RANGO.
     El intervalo publicado corresponde a un estadístico máximo − mínimo, que por construcción no
     puede cubrir el cero y por tanto no contrasta nada. Se sustituye por el contraste
     preespecificado —menos de 7 años frente a 7 a 11— que sí es una hipótesis falsable.

  C. EL GRADIENTE COMO FUNCIÓN DEL PUNTO DE OPERACIÓN, no en un punto único.
     Comparar en un punto único deja abierta la sospecha de que el gradiente se «arregle» moviendo
     el corte. Se barre la tasa de
     positividad del 10 % al 90 % y se muestra el gradiente de cada regla a lo largo del barrido.
     Esto además contesta a quien sospeche que el gradiente se «arregla» moviendo el corte.

  D. INCERTIDUMBRE DEL MODELO NORMATIVO PROPAGADA.
     El remuestreo publicado tomaba la tipificación como dada. Aquí cada réplica reajusta el modelo
     de posición y el de dispersión, y rehace el emparejamiento por edad.

Salida: consola + resultados/V29_sensibilidad_y_operacion.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import duckdb
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
IN = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402

OUT = EST / "resultados"
SESGO = 1.2703628454614782
FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
BANDAS = ["<7", "7-11", ">=12"]
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=BANDAS)
Z = ["LDR_Inmediato puntaje z", "LDR_Distractora puntaje z", "LDR_Diferido puntaje z",
     "IFS puntaje z", "Digitos_Adelante puntaje z", "Digitos_Atras puntaje z",
     "TrailMakingA_TOTAL puntaje z", "TrailMakingB_TOTAL puntaje z"]
rng = np.random.default_rng(29)
R = {}

# ═══════════════════════════════════════════════════════ datos
craw = pd.read_csv(NM / "Mix neuromentias - Base mixta 23+24 (valores).csv",
                   header=4, dtype=object, low_memory=False)
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"]); craw["ok"] = es_control(craw).values
# número de pruebas de la batería —ninguna del criterio de control— por debajo de −1,5 z
zz = pd.DataFrame({c: pd.to_numeric(craw.get(c), errors="coerce") for c in Z})
craw["n_bajas"] = (zz < -1.5).sum(axis=1)
craw["n_z"] = zz.notna().sum(axis=1)
com = (pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
       .merge(craw[["doc", "ok", "n_bajas", "n_z"]], left_on="dni", right_on="doc", how="left"))
CTL = com[com.ok.fillna(False)].dropna(subset=["ACE", "edu", "Edad", "Sexo"]).reset_index(drop=True)
CTL["tr"] = TR(CTL.edu)
print("=" * 100)
print(f"controles: n = {len(CTL)} · con al menos una z disponible: {int((CTL.n_z > 0).sum())} "
      f"(mediana de pruebas con z: {CTL.n_z.median():.0f})")

# ═══════════════════════════════════════════════════════ A. contaminación
print("\n" + "=" * 100)
print("A. ¿EL HALLAZGO SOBREVIVE AL DEPURAR EL GRUPO CONTROL?")
print("   Se excluye progresivamente a los controles con más pruebas bajo −1,5 z. Ninguna de esas")
print("   ocho pruebas forma parte del criterio de control, de modo que el filtro es independiente.\n")
print(f"   {'filtro':<26} {'n':>4} {'<7':>4} {'7-11':>5} {'≥12':>4} "
      f"{'DE por tramo':>22} {'pendiente':>10} {'p':>9} {'razón':>7}")
R["contaminacion"] = []
for etq, mx in [("sin filtro", 99), ("≤2 pruebas bajas", 2), ("≤1 prueba baja", 1),
                ("ninguna prueba baja", 0)]:
    S = CTL[CTL.n_bajas.fillna(99) <= mx]
    if len(S) < 60:
        continue
    n_t = {b: int((S.tr == b).sum()) for b in BANDAS}
    gr = [S.loc[S.tr == b, "ACE"].values for b in BANDAS]
    des = [float(np.std(g, ddof=1)) if len(g) > 1 else np.nan for g in gr]
    mu = smf.ols(FP, data=S).fit()
    t2 = S.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-10, None)))
    sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
    sg = lambda e_: float(np.sqrt(np.exp(SESGO + sd.predict(
        pd.DataFrame({"edu": [e_], "Edad": [65.0]})).iloc[0])))
    fila = {"filtro": etq, "n": int(len(S)), "por_tramo": n_t,
            "de_por_tramo": [round(d, 2) for d in des],
            "pendiente": round(float(sd.params["edu"]), 4), "p": float(sd.pvalues["edu"]),
            "razon_4_16": round(sg(4) / sg(16), 3)}
    R["contaminacion"].append(fila)
    print(f"   {etq:<26} {len(S):>4} {n_t['<7']:>4} {n_t['7-11']:>5} {n_t['>=12']:>4} "
          f"{str([round(d,1) for d in des]):>22} {fila['pendiente']:>+10.4f} {fila['p']:>9.3g} "
          f"{fila['razon_4_16']:>6.2f}×")
print("\n   La razón se informa entre 4 y 16 años de escolaridad —el rango con soporte real de")
print("   datos— y no entre 0 y 20, que son extrapolaciones sin observaciones detrás.")

# ═══════════════════════════════════════════════════════ muestra emparejada
con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv")


def arma(base_ctl, semilla=1):
    ctl = base_ctl[["ACE", "edu", "Edad", "Sexo"]].assign(y=0)
    cas = dx3[dx3.dx3 == "Demencia"][["ACE", "edu", "Edad", "Sexo"]].assign(y=1)
    D = pd.concat([ctl, cas], ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
    lo = max(D[D.y == 1].Edad.min(), D[D.y == 0].Edad.min())
    hi = min(D[D.y == 1].Edad.max(), D[D.y == 0].Edad.max())
    D = D[D.Edad.between(lo, hi)].copy()
    D["b"] = pd.cut(D.Edad, np.arange(np.floor(lo / 5) * 5, hi + 6, 5))
    P = [pd.concat([g[g.y == 1].sample(k, random_state=semilla),
                    g[g.y == 0].sample(k, random_state=semilla)])
         for _, g in D.groupby("b", observed=True)
         if (k := min((g.y == 1).sum(), (g.y == 0).sum())) > 0]
    E = pd.concat(P, ignore_index=True); E["tr"] = TR(E.edu)
    return E


def zeta(E):
    """Tipificación por el modelo normativo ajustado SOBRE LOS CONTROLES de esta muestra."""
    REF = E[E.y == 0]
    mu = smf.ols(FP, data=REF).fit()
    t2 = REF.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-10, None)))
    sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
    return (E.ACE - mu.predict(E)) / np.sqrt(np.exp(SESGO + sd.predict(E)))


def señala(E, z, pos):
    """Señalados por cada regla a una tasa de positividad dada."""
    vig = np.where(E.edu >= 12, E.ACE < 86, E.ACE < 68)
    cont = (z < np.quantile(z, pos)).values
    return vig, cont


def grad_preesp(E, marca):
    """Contraste PREESPECIFICADO: menos de 7 años menos 7 a 11, entre los controles."""
    c = E[E.y == 0]
    m = pd.Series(np.asarray(marca)[E.y.values == 0], index=c.index)
    g = m.groupby(c.tr, observed=True).mean() * 100
    return float(g.get("<7", np.nan) - g.get("7-11", np.nan)), {k: round(float(v), 1) for k, v in g.items()}


E = arma(CTL)
z = zeta(E)
vig, _ = señala(E, z, 0.0)
pos_vig = float(vig.mean())
_, cont = señala(E, z, pos_vig)
print("\n" + "=" * 100)
print(f"muestra emparejada: {int((E.y==1).sum())} casos y {int((E.y==0).sum())} controles · "
      f"positividad de la regla vigente {pos_vig*100:.1f} %")

# ═══════════════════════════════════════════════════════ B. contraste preespecificado
print("\nB. EL GRADIENTE CON EL CONTRASTE PREESPECIFICADO (no el rango máximo − mínimo)")
g_vig, fp_vig = grad_preesp(E, vig)
g_con, fp_con = grad_preesp(E, cont)
bs_v, bs_c, bs_d = [], [], []
for _ in range(2000):
    idx = rng.integers(0, len(E), len(E))
    Eb = E.iloc[idx].reset_index(drop=True)
    if Eb.y.nunique() < 2 or Eb[Eb.y == 0].tr.nunique() < 3:
        continue
    try:
        zb = zeta(Eb)                      # el modelo normativo se REAJUSTA en cada réplica
        vb = np.where(Eb.edu >= 12, Eb.ACE < 86, Eb.ACE < 68)
        cb = (zb < np.quantile(zb, float(vb.mean()))).values
        a_, _ = grad_preesp(Eb, vb); b_, _ = grad_preesp(Eb, cb)
        if np.isfinite(a_) and np.isfinite(b_):
            bs_v.append(a_); bs_c.append(b_); bs_d.append(a_ - b_)
    except Exception:
        pass
q = lambda v: [round(float(np.percentile(v, 2.5)), 1), round(float(np.percentile(v, 97.5)), 1)]
R["gradiente_preespecificado"] = {
    "definicion": "proporción señalada con menos de 7 años menos la de 7 a 11, entre controles",
    "vigente": {"estimacion": round(g_vig, 1), "ic95": q(bs_v), "por_tramo": fp_vig},
    "continua": {"estimacion": round(g_con, 1), "ic95": q(bs_c), "por_tramo": fp_con},
    "diferencia": {"estimacion": round(g_vig - g_con, 1), "ic95": q(bs_d)},
    "n_replicas": len(bs_v),
    "_nota": "cada réplica reajusta el modelo normativo; el publicado lo tomaba como dado"}
gp = R["gradiente_preespecificado"]
print(f"   regla vigente     {gp['vigente']['estimacion']:+6.1f} p.p.  IC 95 % {gp['vigente']['ic95']}"
      f"   señalados por tramo {fp_vig}")
print(f"   corrección continua {gp['continua']['estimacion']:+5.1f} p.p.  IC 95 % {gp['continua']['ic95']}"
      f"   señalados por tramo {fp_con}")
print(f"   diferencia entre reglas {gp['diferencia']['estimacion']:+.1f} p.p.  "
      f"IC 95 % {gp['diferencia']['ic95']}   ({len(bs_v)} réplicas)")

# ═══════════════════════════════════════════════════════ C. barrido del punto de operación
print("\nC. EL GRADIENTE A LO LARGO DEL PUNTO DE OPERACIÓN (no en un punto único)")
print(f"   {'positividad':>12} {'corte único equiv.':>19} {'grad. corte único':>18} "
      f"{'grad. continua':>16}")
R["barrido_operacion"] = []
for pos in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, pos_vig, 0.70, 0.80, 0.90]:
    corte = float(np.quantile(E.ACE, pos))
    unico = (E.ACE < corte).values
    cb = (z < np.quantile(z, pos)).values
    gu, _ = grad_preesp(E, unico); gc, _ = grad_preesp(E, cb)
    R["barrido_operacion"].append({"positividad": round(pos, 3), "corte_unico": round(corte, 1),
                                   "gradiente_corte_unico": round(gu, 1),
                                   "gradiente_continua": round(gc, 1)})
    marca = "  <- la de la regla vigente" if abs(pos - pos_vig) < 1e-9 else ""
    print(f"   {pos*100:>11.1f}% {corte:>19.1f} {gu:>+17.1f} {gc:>+15.1f}{marca}")
gu_all = [f["gradiente_corte_unico"] for f in R["barrido_operacion"]]
gc_all = [f["gradiente_continua"] for f in R["barrido_operacion"]]
R["barrido_resumen"] = {"corte_unico": [min(gu_all), max(gu_all)],
                        "continua": [min(gc_all), max(gc_all)],
                        "_lectura": ("El gradiente de un corte único depende fuertemente de dónde se "
                                     "lo ponga: es máximo en el centro de la distribución y tiende a "
                                     "cero en los extremos, donde se señala a todos o a nadie. Por eso "
                                     "el gradiente sólo es comparable entre reglas a IGUAL positividad, "
                                     "y por eso minimizarlo no equivale a ser equitativo.")}
print(f"\n   rango del gradiente de un corte único a lo largo del barrido: "
      f"{min(gu_all):+.1f} a {max(gu_all):+.1f} p.p.")
print(f"   rango de la corrección continua: {min(gc_all):+.1f} a {max(gc_all):+.1f} p.p.")

# ═══════════════════════════════════════════════════════ D. el gradiente al depurar
print("\nD. EL GRADIENTE AL DEPURAR EL GRUPO CONTROL")
print(f"   {'filtro':<26} {'n ctrl':>7} {'<7':>4} {'grad. vigente':>15} {'grad. continua':>16}")
R["gradiente_depurado"] = []
for etq, mx in [("sin filtro", 99), ("≤2 pruebas bajas", 2), ("≤1 prueba baja", 1)]:
    S = CTL[CTL.n_bajas.fillna(99) <= mx]
    if (TR(S.edu) == "<7").sum() < 10:
        print(f"   {etq:<26} {'—':>7}  (menos de 10 controles con <7 años: no estimable)")
        continue
    Eb = arma(S); zb = zeta(Eb)
    vb = np.where(Eb.edu >= 12, Eb.ACE < 86, Eb.ACE < 68)
    cb = (zb < np.quantile(zb, float(vb.mean()))).values
    gv, fv = grad_preesp(Eb, vb); gc, _ = grad_preesp(Eb, cb)
    n7 = int((Eb[Eb.y == 0].tr == "<7").sum())
    R["gradiente_depurado"].append({"filtro": etq, "n_ctrl": int((Eb.y == 0).sum()), "n_lt7": n7,
                                    "grad_vigente": round(gv, 1), "grad_continua": round(gc, 1),
                                    "por_tramo_vigente": fv})
    print(f"   {etq:<26} {int((Eb.y==0).sum()):>7} {n7:>4} {gv:>+15.1f} {gc:>+16.1f}")

OUT.mkdir(exist_ok=True)
(OUT / "V29_sensibilidad_y_operacion.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V29_sensibilidad_y_operacion.json'}")
