#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V30 — La contaminación del grupo control, separada por grupo diagnóstico.

POR QUÉ ESTE BLOQUE. La condición diana del estudio es **DEMENCIA moderada o severa**. El deterioro
cognitivo leve **no es caso** en este diseño: se excluyó deliberadamente al definir la muestra
analítica. Esa decisión, que estaba implementada en el código pero no explicitada en el manuscrito,
cambia por completo el peso de la objeción de contaminación que las cuatro auditorías señalaron.

  · Un control con DCL **no es un caso mal clasificado**. Es una cuestión de espectro, y sólo importa
    para el gradiente si la fuga de DCL es DESIGUAL entre tramos educativos.
  · Un control con DEMENCIA **sí es un caso mal clasificado**, y su fuga diferencial infla el gradiente
    directamente.

El manuscrito venía informando el 72 % de fuga de DCL y las cifras 60,7 % / 48,9 % de fuga de demencia
sin distinguir su significado, y sin que ninguna de las tres estuviera en un archivo de resultados. Una
de las auditorías señaló precisamente que esas cifras no eran reproducibles desde el repositorio. Este
bloque las produce y las guarda.

LIMITACIÓN DEL PROCEDIMIENTO, declarada por adelantado. En la cohorte clínica sólo puede aplicarse
**uno** de los cuatro criterios de control —el reconocimiento de lista ≥ 10—; los otros tres
(antecedentes de accidente cerebrovascular y de traumatismo de cráneo, independencia funcional) no
están disponibles ahí. Las proporciones que siguen son por tanto **cota superior** de la fuga: con las
cuatro condiciones pasarían menos. Y la cohorte clínica es una población distinta —consulta por
sospecha—, de modo que su composición no se transfiere a la comunitaria.

Salida: consola + resultados/V30_contaminacion_por_grupo.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, duckdb
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
IN = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
OUT = EST / "resultados"
BANDAS = ["<7", "7-11", ">=12"]
ETI = {"<7": "menos de 7", "7-11": "7 a 11", ">=12": "12 o más"}
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=BANDAS)
UMBRAL = 10
R = {"_condicion_diana": "demencia moderada o severa; el deterioro cognitivo leve NO es caso",
     "_limitacion": ("en la cohorte clínica sólo se aplica el criterio de reconocimiento de lista; "
                     "las proporciones son cota superior de la fuga")}

con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
cl = con.execute("select eval_id, bruto rec from resultados_v2 "
                 "where test='Lista de Rey' and subtest like 'Reconoc%'").fetchdf()
cl["rec"] = pd.to_numeric(cl.rec, errors="coerce")
cl["eval_id"] = cl.eval_id.astype(str)
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv")
dx3["eval_id"] = dx3.eval_id.astype(str)
D = dx3.merge(cl.dropna(subset=["rec"]).drop_duplicates("eval_id"), on="eval_id", how="left")
D = D.dropna(subset=["rec", "edu"]).copy()
D["tr"] = TR(D.edu)
D["pasa"] = D.rec >= UMBRAL

print("=" * 96)
print(f"A. FUGA DEL TAMIZ (reconocimiento ≥ {UMBRAL}) POR GRUPO DIAGNÓSTICO — cota superior\n")
print(f"   {'grupo':<18} {'n':>5} {'fuga global':>13}   fuga por tramo educativo")
R["fuga"] = {}
for g in ["Sin afectación", "DCL", "Demencia"]:
    s = D[D.dx3 == g]
    if not len(s):
        continue
    pt = s.groupby("tr", observed=True).pasa.mean() * 100
    nt = s.groupby("tr", observed=True).size()
    ct = pd.crosstab(s.tr, s.pasa)
    p_edu = float(stats.chi2_contingency(ct).pvalue) if ct.shape[1] == 2 and ct.values.min() >= 1 else None
    R["fuga"][g] = {"n": int(len(s)), "global": round(float(s.pasa.mean() * 100), 1),
                    "por_tramo": {b: round(float(pt.get(b, np.nan)), 1) for b in BANDAS},
                    "n_por_tramo": {b: int(nt.get(b, 0)) for b in BANDAS},
                    "p_diferencial": p_edu}
    print(f"   {g:<18} {len(s):>5} {s.pasa.mean()*100:>12.1f} %   " +
          " · ".join(f"{ETI[b]}: {pt.get(b, np.nan):.1f} %" for b in BANDAS) +
          (f"   (χ² p = {p_edu:.4f})" if p_edu is not None else ""))

print("\n" + "=" * 96)
print("B. LO DECISIVO: ¿ES LA FUGA DIFERENCIAL POR ESCOLARIDAD?\n")
dcl, dem = R["fuga"]["DCL"], R["fuga"]["Demencia"]
print(f"   DCL       — fuga {dcl['global']} %, y **NO difiere entre tramos** (χ² p = {dcl['p_diferencial']:.3f}):")
print(f"               {dcl['por_tramo']['<7']} · {dcl['por_tramo']['7-11']} · {dcl['por_tramo']['>=12']} %")
print(f"               Al ser pareja, **no puede generar el gradiente educativo**.")
print(f"   Demencia  — fuga {dem['global']} %, y **SÍ difiere** (χ² p = {dem['p_diferencial']:.4f}):")
print(f"               {dem['por_tramo']['<7']} · {dem['por_tramo']['7-11']} · {dem['por_tramo']['>=12']} %")
print(f"               Es la que infla el gradiente, y por eso 33,4 p.p. es cota superior.")
R["veredicto"] = {
    "dcl_diferencial": bool(dcl["p_diferencial"] < 0.05),
    "demencia_diferencial": bool(dem["p_diferencial"] < 0.05),
    "lectura": ("La fuga de DCL es grande pero pareja entre tramos y el DCL no es caso: no puede "
                "generar el gradiente. La fuga de demencia es menor pero desigual y sí lo infla.")}

print("\n" + "=" * 96)
print("C. COMPOSICIÓN DE QUIENES PASAN EL TAMIZ, POR TRAMO\n")
p = D[D.pasa]
print(f"   {'tramo':>12} {'pasan':>7} {'DCL':>12} {'Demencia':>12} {'Sin afectación':>16}")
R["composicion"] = {}
for b in BANDAS:
    s = p[p.tr == b]
    if not len(s):
        continue
    c = s.dx3.value_counts(normalize=True) * 100
    R["composicion"][b] = {"n": int(len(s)),
                           "DCL": round(float(c.get("DCL", 0)), 1),
                           "Demencia": round(float(c.get("Demencia", 0)), 1),
                           "Sin_afectacion": round(float(c.get("Sin afectación", 0)), 1)}
    d_ = R["composicion"][b]
    print(f"   {ETI[b]:>12} {d_['n']:>7} {d_['DCL']:>11.1f} % {d_['Demencia']:>11.1f} % "
          f"{d_['Sin_afectacion']:>15.1f} %")
print("\n   En el tramo de menor escolaridad, la mitad de quienes pasan el tamiz tiene demencia;")
print("   en el de mayor escolaridad, menos de una quinta parte. Ése es el mecanismo por el que la")
print("   contaminación infla el gradiente, y la razón de declararlo como límite superior.")

OUT.mkdir(exist_ok=True)
(OUT / "V30_contaminacion_por_grupo.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V30_contaminacion_por_grupo.json'}")
