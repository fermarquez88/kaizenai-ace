#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V19 — Perfil cognitivo del grupo control en la batería completa.

Es la primera pregunta que hace cualquier revisor: el grupo control no se define por la batería —para
evitar circularidad con el índice y dependencia educativa—, pero tiene que verse normal en ella. Si no
se ve normal, el grupo no es creíble.

Hay una trampa que gobierna la lectura de esta tabla. Los puntajes z de esta batería están normados
**por educación**: la norma que se aplica a una persona depende de su escolaridad. En consecuencia,
un z plano entre tramos educativos NO demuestra que los tres grupos rindan igual; demuestra que cada
uno rinde según lo esperado para su propia escolaridad, que es una afirmación distinta y más modesta.
Por eso se reportan las dos escalas lado a lado:

  · el puntaje BRUTO muestra el gradiente educativo real, que existe y es grande
  · el puntaje z muestra que, contra su propia norma, los controles están en rango

Salida: resultados/V19_perfil_controles.json + manuscrito/TablaS_perfil_controles.md
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
import sys as _sys; _sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control

TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
BANDAS = ["<7", "7-11", "≥12"]

craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"])
num = lambda c: pd.to_numeric(craw[c], errors="coerce") if c in craw.columns else pd.Series(np.nan, index=craw.index)

# bruto y z de cada prueba; el reconocimiento define el grupo y se marca como tal
PRUEBAS = [
    ("Rey · codificación (ensayo 1)",  "LDR_Inicial_1",        "LDR_Inicial_1 puntaje z",        False),
    ("Rey · recuerdo inmediato",       "LDR_Inmediato",        "LDR_Inmediato puntaje z",        False),
    ("Rey · lista distractora",        "LDR_Distractora",      "LDR_Distractora puntaje z",      False),
    ("Rey · recuerdo diferido",        "LDR_Diferido",         "LDR_Diferido puntaje z",         False),
    ("Rey · reconocimiento corregido", "LDR_Rec_Corregido",    "LDR_Rec_Corregido puntaje z",    True),
    ("INECO Frontal Screening",        None,                   "IFS puntaje z",                  False),
    ("Dígitos directos",               "Digitos_Adelante",     "Digitos_Adelante puntaje z",     False),
    ("Dígitos inversos",               "Digitos_Atras",        "Digitos_Atras puntaje z",        False),
    ("Trail Making A (segundos)",      "TrailMakingA_TOTAL",   "TrailMakingA_TOTAL puntaje z",   False),
    ("Trail Making B (segundos)",      "TrailMakingB_TOTAL",   "TrailMakingB_TOTAL puntaje z",   False),
]

base = pd.DataFrame({"doc": craw["doc"], "ok": es_control(craw).values})
for _, b, z, _ in PRUEBAS:
    if b: base[b] = num(b)
    if z: base[z] = num(z)
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
D = com.merge(base, left_on="dni", right_on="doc", how="left").dropna(subset=["ACE", "edu", "Edad", "Sexo"])
D["tr"] = TR(D.edu)
C = D[D.ok == True]                                   # el grupo control del estudio
print(f"cohorte comunitaria {len(D)}  ·  grupo control {len(C)}  "
      f"({', '.join(f'{t}: {int((C.tr==t).sum())}' for t in BANDAS)})\n")

def resumen(s, g):
    v = pd.to_numeric(s, errors="coerce")
    out = {"n": int(v.notna().sum())}
    if out["n"] < 10: return None
    out["media"] = float(v.mean()); out["de"] = float(v.std())
    for t in BANDAS:
        w = v[g == t]
        out[t] = (float(w.mean()), int(w.notna().sum()))
    gr = [v[g == t].dropna() for t in BANDAS]
    out["p"] = float(stats.kruskal(*gr).pvalue) if all(len(x) > 4 for x in gr) else np.nan
    return out

RES, FILAS = {"n_control": len(C), "n_por_tramo": {t: int((C.tr == t).sum()) for t in BANDAS}}, []
RES["pruebas"] = {}
print(f"{'prueba':<34}{'n':>5}{'':>3}{'bruto <7':>10}{'7-11':>8}{'≥12':>8}{'p':>9}"
      f"{'':>4}{'z <7':>8}{'7-11':>8}{'≥12':>8}{'p':>9}{'z<-1,5':>9}")
for nom, cb, cz, es_criterio in PRUEBAS:
    rb = resumen(C[cb], C.tr) if cb and cb in C else None
    rz = resumen(C[cz], C.tr) if cz and cz in C else None
    if rz is None: continue
    bajo = 100 * float((pd.to_numeric(C[cz], errors="coerce") < -1.5).mean())
    m = "*" if es_criterio else " "
    b = (f"{rb['<7'][0]:>10.1f}{rb['7-11'][0]:>8.1f}{rb['≥12'][0]:>8.1f}{rb['p']:>9.3f}"
         if rb else f"{'—':>10}{'—':>8}{'—':>8}{'—':>9}")
    print(f"{nom:<34}{rz['n']:>5}{m:>3}{b}    {rz['<7'][0]:>8.2f}{rz['7-11'][0]:>8.2f}"
          f"{rz['≥12'][0]:>8.2f}{rz['p']:>9.3f}{bajo:>8.1f}%")
    RES["pruebas"][nom] = {"criterio_de_control": es_criterio, "n": rz["n"],
                           "bruto": ({t: round(rb[t][0], 2) for t in BANDAS} | {"p": round(rb["p"], 4)}) if rb else None,
                           "z": {t: round(rz[t][0], 2) for t in BANDAS} | {"p": round(rz["p"], 4)},
                           "z_medio": round(rz["media"], 2), "z_de": round(rz["de"], 2),
                           "pct_bajo_menos_1_5": round(bajo, 1)}
    FILAS.append((nom, es_criterio, rz, rb, bajo))

# ── el ACE-III es el índice bajo evaluación: se muestra aparte y con su advertencia
ra = resumen(C["ACE"], C.tr)
RES["ACE_indice"] = {t: round(ra[t][0], 1) for t in BANDAS} | {"p": round(ra["p"], 6)}
print(f"\n{'ACE-III (índice evaluado)':<34}{ra['n']:>5}{' ':>3}{ra['<7'][0]:>10.1f}"
      f"{ra['7-11'][0]:>8.1f}{ra['≥12'][0]:>8.1f}{ra['p']:>9.1e}")

# ── ¿cuántos controles tienen un perfil normal en toda la batería?
zc = [z for _, _, z, _ in PRUEBAS if z in C]
Z = C[zc].apply(pd.to_numeric, errors="coerce")
compl = Z.notna().sum(axis=1) >= 6
n_bajo = (Z < -1.5).sum(axis=1)
print(f"\ncon al menos 6 pruebas con z: {int(compl.sum())} de {len(C)}")
RES["perfil_global"] = {}
for k in (0, 1, 2):
    m = compl & (n_bajo <= k)
    pct = {t: 100*float((m & (C.tr == t)).sum() / max((compl & (C.tr == t)).sum(), 1)) for t in BANDAS}
    tab = pd.crosstab(C[compl].tr, m[compl])
    p = stats.chi2_contingency(tab)[1] if tab.shape == (3, 2) else np.nan
    print(f"  con {k} o menos pruebas bajo −1,5 DE: {int(m.sum()):>4}  "
          f"({pct['<7']:.0f} % · {pct['7-11']:.0f} % · {pct['≥12']:.0f} %)   p = {p:.3f}")
    RES["perfil_global"][f"max_{k}_pruebas_bajas"] = {
        "n": int(m.sum()), "por_tramo": {t: round(pct[t], 1) for t in BANDAS}, "p_edu": round(float(p), 4)}

# ─────────────────────────────────────────────────────── tabla para el suplementario
L = ["## Tabla S. Perfil cognitivo del grupo control en la batería completa", "",
     f"Grupo control (n = {len(C)}): participantes comunitarios que cumplen el criterio de control del estudio",
     "—reconocimiento ≥ 10, sin ACV, sin TEC e independiente en actividades básicas—. Los puntajes **z**, de modo que un z plano",
     "entre tramos no indica rendimiento igual, sino rendimiento acorde a la norma de cada tramo. Por",
     "eso se informan las dos escalas. El asterisco marca la prueba que define el grupo.", "",
     "| Prueba | n | Bruto <7 | 7–11 | ≥12 | p | z <7 | 7–11 | ≥12 | p | z < −1,5 |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
f2 = lambda x: f"{x:.2f}".replace(".", ",")
f1 = lambda x: f"{x:.1f}".replace(".", ",")
fp = lambda x: ("< 0,001" if x < 0.001 else f"{x:.3f}".replace(".", ","))
for nom, es, rz, rb, bajo in FILAS:
    b = f"{f1(rb['<7'][0])} | {f1(rb['7-11'][0])} | {f1(rb['≥12'][0])} | {fp(rb['p'])}" if rb else "— | — | — | —"
    marca = " *" if es else ""
    L.append(f"| {nom}{marca} | {rz['n']} | {b} | {f2(rz['<7'][0])} | "
             f"{f2(rz['7-11'][0])} | {f2(rz['≥12'][0])} | {fp(rz['p'])} | {f1(bajo)} % |")
L += ["", f"| **ACE-III**, índice evaluado | {ra['n']} | {f1(ra['<7'][0])} | {f1(ra['7-11'][0])} | "
      f"{f1(ra['≥12'][0])} | {fp(ra['p'])} | — | — | — | — | — |", "",
      "**Lectura.** En puntaje bruto el gradiente educativo es grande y significativo en la mayoría de",
      "las pruebas: es el fenómeno que el trabajo estudia. En puntaje z, normado por educación, los",
      "tres tramos se ubican en rango y sin diferencias sistemáticas, lo que indica que **los controles",
      "rinden conforme a lo esperado para su propia escolaridad en toda la batería**, y no sólo en la",
      "prueba que los define. El ACE-III se informa sólo en bruto y por separado, porque es el índice",
      "bajo evaluación y normarlo introduciría circularidad."]
Path(EST / "manuscrito/TablaS_perfil_controles.md").write_text("\n".join(L) + "\n", encoding="utf-8")
Path(EST / "resultados/V19_perfil_controles.json").write_text(
    json.dumps(RES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("\n-> resultados/V19_perfil_controles.json + manuscrito/TablaS_perfil_controles.md")
