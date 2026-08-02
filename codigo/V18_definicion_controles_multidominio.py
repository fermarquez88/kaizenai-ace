#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V18 — Definición multidominio del grupo control, con criterios auditados por neutralidad educativa.

El manuscrito define control con un solo test: memoria de reconocimiento de lista ≥ 10. Un revisor de
Lancet, Neurology, Alzheimer's & Dementia o Nature objetaría dos cosas: que un único test cognitivo no
es «ausencia de deterioro», y que la cohorte comunitaria tiene información funcional, de queja
cognitiva y de antecedentes que no se está usando.

El problema es que casi todo lo disponible depende de la escolaridad, y un criterio de control que
dependa de la exposición hace variar la composición del grupo control con la exposición —exactamente
el sesgo que el diseño necesita evitar—. Por eso cada criterio candidato se somete a la misma prueba
antes de admitirse:

    1. cobertura suficiente
    2. asociación con la escolaridad: si el criterio se cumple más en un tramo educativo que en otro,
       queda descartado o se declara
    3. aporte: ¿excluye a alguien que el criterio vigente no excluía?

Con los que pasan se construyen definiciones anidadas, de la más laxa a la más estricta, y se estima
el gradiente de la regla vigente bajo cada una. La conclusión es robusta si el gradiente sobrevive a
todas.

Salida: resultados/V18_controles_multidominio.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
RES = {}

# ─────────────────────────────────────────────────────── datos
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"])
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")

num = lambda c: pd.to_numeric(craw[c], errors="coerce") if c in craw.columns else pd.Series(np.nan, index=craw.index)

# ─────────────────────────────────────────────────────── criterios candidatos
# Cada uno devuelve True cuando la persona CUMPLE el criterio de normalidad.
# El código 9 del ADLQ y de los ítems de ayuda significa «no corresponde», no dependencia.
AYUDA = ["ayuda_vestir", "ayuda_medicam", "ayuda_dinero", "ayuda_tareas"]
CAMBIO = ["cambios_mem", "cambios_orient", "cambios_leng", "cambios_organ"]
ADLQ_BASICAS = ["ADLQ_Alimentarse_(A)", "ADLQ_Vestido_(A)", "ADLQ_Baño_(A)", "ADLQ_Evacuación_(A)"]
GDS = [c for c in craw.columns if str(c).startswith("Escala_Yesavage")]

def todos_cero(cols):
    """Cumple si todos los ítems valen 0. El 9 (no corresponde) no cuenta como incumplimiento.
    Devuelve NaN cuando no hay dato suficiente, para que la ausencia se audite por separado."""
    M = pd.DataFrame({c: num(c) for c in cols})
    val = M.replace(9, np.nan)
    hay = val.notna().sum(axis=1) >= max(1, len(cols) - 1)
    return ((val.fillna(0) == 0).all(axis=1)).astype(float).where(hay)


def umbral(col, u):
    """Cumple si el valor alcanza el umbral; NaN si no hay medición."""
    v = num(col)
    return (v >= u).astype(float).where(v.notna())


def sin_antecedente(col):
    """Cumple si no consta el antecedente; NaN si no se relevó."""
    v = num(col)
    return (v == 0).astype(float).where(v.notna())

CRIT = {
    "reconocimiento":   (umbral("LDR_Reconocimiento_A", 10),
                         "Memoria de reconocimiento de lista ≥ 10"),
    "func_ayuda":       (todos_cero(AYUDA),
                         "Sin ayuda para vestirse, medicarse, manejar dinero ni tareas"),
    "func_adlq_basica": (todos_cero(ADLQ_BASICAS),
                         "Independiente en las actividades básicas del ADLQ"),
    "sin_queja":        (todos_cero(CAMBIO),
                         "Sin cambios referidos en memoria, orientación, lenguaje ni organización"),
    "sin_acv":          (sin_antecedente("APN_ACV"),
                         "Sin antecedente de accidente cerebrovascular"),
    "sin_tec":          (sin_antecedente("APN_LesionesCabeza"),
                         "Sin antecedente de traumatismo de cráneo"),
    "sin_depresion":    ((lambda g: (g <= 5).astype(float).where(g.notna()))(
                          pd.DataFrame({c: num(c) for c in GDS}).sum(axis=1, min_count=1)),
                         "Sin sintomatología depresiva relevante (Yesavage ≤ 5)"),
}

base = pd.DataFrame({"doc": craw["doc"], "Edad": pd.to_numeric(craw.Edad, errors="coerce")})
for k, (serie, _) in CRIT.items():
    base[k] = serie.values
D = com.merge(base, left_on="dni", right_on="doc", how="left", suffixes=("", "_x"))
D["tr"] = TR(D.edu)
D = D.dropna(subset=["ACE", "edu", "Edad", "Sexo"])
print(f"cohorte comunitaria analítica: {len(D)}\n")

# ─────────────────────────────────────────────────────── A · auditoría de cada criterio
print("A. AUDITORÍA DE CADA CRITERIO CANDIDATO")
print(f"{'criterio':<20}{'cobertura':>10}{'cumple':>9}{'<7':>8}{'7-11':>8}{'≥12':>8}{'p edu':>10}  veredicto")
RES["criterios"] = {}
for k, (_, desc) in CRIT.items():
    v = D[k]
    cob = v.notna().mean()
    if cob < 0.60:
        print(f"{k:<20}{100*cob:>9.0f}%{'—':>9}{'—':>8}{'—':>8}{'—':>8}{'—':>10}  cobertura insuficiente")
        RES["criterios"][k] = {"cobertura": round(100*cob, 1), "admitido": False,
                               "motivo": "cobertura insuficiente"}
        continue
    sub = D[v.notna()]
    pct = {t: 100*sub[sub.tr == t][k].mean() for t in ["<7", "7-11", "≥12"]}
    tab = pd.crosstab(sub.tr, sub[k] == 1)
    p = stats.chi2_contingency(tab)[1] if tab.shape == (3, 2) else np.nan
    # la ausencia del dato también puede depender de la escolaridad
    tabm = pd.crosstab(D.tr, v.notna())
    pm = stats.chi2_contingency(tabm)[1] if tabm.shape == (3, 2) else 1.0
    admite = p >= 0.05
    print(f"{k:<20}{100*cob:>9.0f}%{100*v.mean():>8.0f}%{pct['<7']:>7.0f}%{pct['7-11']:>7.0f}%"
          f"{pct['≥12']:>7.0f}%{p:>10.3f}  {'ADMITIDO' if admite else 'depende de la escolaridad'}"
          f"{'' if pm >= 0.05 else '  · ausencia del dato ligada a la escolaridad (p=%.3f)' % pm}")
    RES["criterios"][k] = {"descripcion": desc, "cobertura": round(100*cob, 1),
                           "cumple_pct": round(100*float(v.mean()), 1),
                           "por_tramo": {t: round(pct[t], 1) for t in pct},
                           "p_edu": round(float(p), 4), "p_ausencia_edu": round(float(pm), 4),
                           "admitido": bool(admite)}

ADMITIDOS = [k for k, r in RES["criterios"].items() if r.get("admitido")]
print(f"\ncriterios neutrales respecto de la escolaridad: {ADMITIDOS}")

# ─────────────────────────────────────────────────────── B · definiciones anidadas
print("\n\nB. DEFINICIONES DE CONTROL, DE LA MÁS LAXA A LA MÁS ESTRICTA")
DEFS = {
    "D0 vigente":      ["reconocimiento"],
    "D1 + funcional":  ["reconocimiento", "func_ayuda"],
    "D2 + sin queja":  ["reconocimiento", "func_ayuda", "sin_queja"],
    "D3 + sin ACV":    ["reconocimiento", "func_ayuda", "sin_queja", "sin_acv"],
    "D4 todo":         ["reconocimiento", "func_ayuda", "sin_queja", "sin_acv", "sin_tec", "sin_depresion"],
    "D5 sólo funcional": ["func_ayuda", "sin_queja"],
}
corte = lambda e: np.where(e >= 12, 86, 68)
print(f"{'definición':<20}{'n':>6}{'<7':>6}{'7-11':>7}{'≥12':>6}{'p edu':>9}"
      f"{'ACE <7':>9}{'señala <7':>11}{'7-11':>8}{'≥12':>8}{'gradiente':>11}")
RES["definiciones"] = {}
for nom, cs in DEFS.items():
    usa = [c for c in cs if RES["criterios"].get(c, {}).get("cobertura", 0) >= 60]
    if not usa: continue
    m = D[usa].notna().all(axis=1)
    ok = m & (D[usa] == 1).all(axis=1)
    C = D[ok]
    if len(C) < 40: continue
    n_t = {t: int((C.tr == t).sum()) for t in ["<7", "7-11", "≥12"]}
    # ¿la condición de control depende del tramo educativo entre quienes tienen el dato?
    ev = D[m]
    tab = pd.crosstab(ev.tr, (ev[usa] == 1).all(axis=1))
    p = stats.chi2_contingency(tab)[1] if tab.shape == (3, 2) else np.nan
    sen = {t: 100*(C[C.tr == t].ACE < corte(C[C.tr == t].edu)).mean() for t in ["<7", "7-11", "≥12"]}
    grad = max(sen.values()) - min(sen.values())
    ace7 = C[C.tr == "<7"].ACE.mean()
    print(f"{nom:<20}{len(C):>6}{n_t['<7']:>6}{n_t['7-11']:>7}{n_t['≥12']:>6}{p:>9.3f}"
          f"{ace7:>9.1f}{sen['<7']:>10.1f}%{sen['7-11']:>7.1f}%{sen['≥12']:>7.1f}%{grad:>10.1f}")
    RES["definiciones"][nom] = {
        "criterios": usa, "n": len(C), "n_por_tramo": n_t, "p_edu": round(float(p), 4),
        "ACE_medio_lt7": round(float(ace7), 1),
        "senalados": {t: round(sen[t], 1) for t in sen}, "gradiente": round(float(grad), 1)}

# ─────────────────────────────────────────────────────── C · qué agrega cada criterio
print("\n\nC. QUÉ EXCLUYE CADA CRITERIO QUE EL VIGENTE NO EXCLUÍA")
v0 = D["reconocimiento"]
RES["aporte"] = {}
for k in ADMITIDOS:
    if k == "reconocimiento": continue
    extra = (v0 == 1) & (D[k] == 0)
    if extra.sum() == 0: continue
    e = D[extra]
    print(f"  {k:<18} excluye a {extra.sum():>3} que el vigente admitía  ·  "
          f"ACE medio {e.ACE.mean():.1f} frente a {D[v0 == 1].ACE.mean():.1f}  ·  "
          f"escolaridad {e.edu.mean():.1f} frente a {D[v0 == 1].edu.mean():.1f}")
    RES["aporte"][k] = {"n_excluidos": int(extra.sum()), "ACE_medio": round(float(e.ACE.mean()), 1),
                        "edu_media": round(float(e.edu.mean()), 1)}

# ─────────────────────────────────────────────────────── D · análisis cuantitativo del sesgo
print("\n\nD. ANÁLISIS CUANTITATIVO DEL SESGO POR CONTAMINACIÓN")
print("Si una fracción de los controles de baja escolaridad tuviera deterioro no detectado,")
print("señalarlos no sería un falso positivo y el gradiente medido bajaría. Cota inferior:\n")
mej = max(RES["definiciones"], key=lambda k: len(RES["definiciones"][k]["criterios"]))
Cm = RES["definiciones"][mej]
print(f"  definición más estricta disponible: {mej}  ·  gradiente {Cm['gradiente']} pp\n")
print(f"{'contaminación en <7':>22}{'señalados <7 corregido':>26}{'gradiente corregido':>22}")
RES["sesgo"] = {"definicion": mej, "gradiente_observado": Cm["gradiente"], "escenarios": {}}
s7, s_med = Cm["senalados"]["<7"], min(Cm["senalados"].values())
for f in (0, 10, 20, 30, 40, 50):
    # Si una fracción f de los controles de <7 tuviera deterioro no detectado, esos no serían
    # controles. Suponiendo el peor caso —que TODOS ellos estaban siendo señalados—, la proporción
    # señalada entre los controles verdaderos pasa a ser (s7 - f) / (100 - f), en porcentaje.
    corr = 100*max(0.0, (s7 - f)) / max(1e-9, 100 - f)
    print(f"{f:>21}%{corr:>25.1f}%{corr - s_med:>21.1f}")
    RES["sesgo"]["escenarios"][f] = {"senalados_lt7": round(corr, 1),
                                     "gradiente": round(corr - s_med, 1)}

Path(EST / "resultados/V18_controles_multidominio.json").write_text(
    json.dumps(RES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"\n-> resultados/V18_controles_multidominio.json")
