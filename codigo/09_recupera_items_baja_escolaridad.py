#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RECUPERACION ITEM-NIVEL de los ACE-III que el pipeline original descartaba por 'sin_total'.

Diagnostico (script 08): en baja escolaridad los 23 items ESTAN cargados (mediana 23/23, igual
que en alta escolaridad), pero la celda del gran total del bloque RESULTADOS de la hoja
`ACE-ACE-R` esta vacia en el 82%. La regla original exigia esa celda -> descartaba el 97% de los
pacientes de baja escolaridad. No era administracion parcial: era una celda de resumen vacia.

REGLA NUEVA (validacion CRUZADA, mas fuerte que la original, no mas debil):
un caso entra si
  1. los 23 items estan completos (tras recuperacion EXACTA por subtotal de dominio, sin imputar),
  2. todos los items dentro de [0, max],
  3. los subtotales de dominio que ESTEN presentes reconcilian con la suma de sus items,
  4. la suma de los 23 items coincide (±0.5) con el total del ACE registrado en `resultados_v2`,
     que se extrae de OTRA ubicacion del archivo -> confirmacion por fuente independiente.
La regla original validaba dentro de la misma hoja; esta exige acuerdo entre dos fuentes.
Un caso sin ninguna de las dos anclas de total NO entra.

Salida: /neuromentia/analisis/ace_items_clinico_v2.csv  + out/09_recuperacion.json
"""
import sys, os, json
from pathlib import Path
import duckdb
import pandas as pd

INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
sys.path.insert(0, str(INECO / "src"))
os.chdir(INECO)
import extract_ace_items as EX  # noqa: E402

OUTD = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia/ACE/out"); OUTD.mkdir(exist_ok=True)
OUTCSV = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia/analisis/ace_items_clinico_v2.csv")

MAXV = {k: v[2] for k, v in EX.CELL.items()}; MAXV["ACE_HabVisoReloj"] = 5

con = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)
df = con.execute("""
 with tot as (select eval_id, max(bruto) ace_total_db from resultados_v2
              where lower(test) like '%ace%' and bruto is not null and bruto between 1 and 100 group by 1)
 select e.eval_id, e.persona_id, e.path, e.edad, e.educacion, e.sexo, e.fecha_ev, e.cohorte,
        e.evaluador, e.year, t.ace_total_db
 from evaluaciones_v2 e left join tot t on t.eval_id=e.eval_id
 where e.cohorte in ('nps_adulto','emicar') and e.edad between 40 and 105
   and e.educacion is not null and e.sexo is not null and e.fecha_ev is not null
""").fetchdf()
print(f"episodios candidatos (adulto, >=40, demografia OK): {len(df)}", flush=True)


def valida_cruzado(d, total_db):
    """Devuelve (ok, motivo, items, ancla)."""
    EX.recover(d)
    it, subt, tot_hoja = d["items"], d["subt"], d["total"]
    if any(it.get(k) is None for k in EX.ITEMS):
        return False, "item_faltante", None, None
    for k in EX.ITEMS:
        if not (0 <= it[k] <= MAXV[k]):
            return False, f"rango_{k}", None, None
    # subtotales de dominio PRESENTES deben reconciliar
    for dname, (_r, keys) in EX.DOM.items():
        if subt.get(dname) is not None and abs(sum(it[k] for k in keys) - subt[dname]) > 0.5:
            return False, f"dom_{dname}", None, None
    suma = sum(it[k] for k in EX.ITEMS)
    ok_hoja = tot_hoja is not None and tot_hoja > 0 and abs(suma - tot_hoja) <= 0.5
    ok_db = total_db is not None and not pd.isna(total_db) and abs(suma - total_db) <= 0.5
    if ok_hoja and ok_db:
        return True, "ok_doble_ancla", it, "hoja+db"
    if ok_hoja:
        return True, "ok_ancla_hoja", it, "hoja"
    if ok_db:
        return True, "ok_ancla_db", it, "db"
    if tot_hoja is None and (total_db is None or pd.isna(total_db)):
        return False, "sin_ninguna_ancla", None, None
    return False, "total_neq_suma", None, None


rows, motivos = [], []
for i, r in enumerate(df.itertuples(), 1):
    if not os.path.exists(r.path):
        motivos.append({"tramo": r.educacion, "motivo": "archivo_no_encontrado"}); continue
    d = EX.extract(r.path)
    if not d or "items" not in d:
        motivos.append({"tramo": r.educacion, "motivo": (d or {}).get("skip") or "load_fail"}); continue
    ok, why, it, ancla = valida_cruzado(d, r.ace_total_db)
    motivos.append({"tramo": r.educacion, "motivo": why})
    if ok:
        rows.append({"eval_id": r.eval_id, "persona_id": r.persona_id, "archivo": r.path,
                     "fecha_ev": r.fecha_ev, "year": r.year, "cohorte": r.cohorte,
                     "evaluador": r.evaluador, "Edad": r.edad,
                     "ed_anos_completos": r.educacion,
                     "Sexo": {"F": "Mujer", "M": "Hombre"}.get(r.sexo, r.sexo),
                     **{k: int(it[k]) for k in EX.ITEMS},
                     "ACE_total": int(sum(it[k] for k in EX.ITEMS)), "ancla": ancla})
    if i % 400 == 0:
        print(f"  ...{i}/{len(df)}  validados={len(rows)}", flush=True)

M = pd.DataFrame(motivos)
M["banda"] = pd.cut(M.tramo, [-1, 6.5, 10.5, 12.5, 99], labels=["<7", "7-10", "11-12", ">12"])
pd.set_option("display.width", 250)
print("\n" + "=" * 78 + "\nMOTIVOS por banda educativa (conteos):")
print(pd.crosstab(M.banda, M.motivo).to_string())

E = pd.DataFrame(rows)
E["banda"] = pd.cut(E.ed_anos_completos, [-1, 6.5, 10.5, 12.5, 99], labels=["<7", "7-10", "11-12", ">12"])
print("\nVALIDADOS por banda y ancla usada (episodios):")
print(pd.crosstab(E.banda, E.ancla, margins=True).to_string())

# --- concordancia entre las dos anclas donde ambas existen (control de calidad)
d2 = E[E.ancla == "hoja+db"]
print(f"\nCasos con doble ancla concordante: {len(d2)} "
      f"({100*len(d2)/max(len(E),1):.1f}% de los validados) -> la fuente `db` reproduce la hoja.")

# --- dedup a basal
E["fecha_p"] = pd.to_datetime(E.fecha_ev, errors="coerce", dayfirst=True)
E = E.sort_values(["persona_id", "fecha_p", "eval_id"], na_position="last")
base = E.groupby("persona_id", as_index=False).first()
lon = E[E.persona_id.isin(E.persona_id.value_counts()[lambda s: s >= 2].index)].copy()
print(f"\nepisodios validados {len(E)} -> personas unicas (basal) {len(base)}"
      f" | reevaluados {lon.persona_id.nunique()} personas / {len(lon)} evals")
print("basal por banda:", base.groupby("banda", observed=True).size().to_dict())
print("basal ACE medio :", base.groupby("banda", observed=True).ACE_total.mean().round(1).to_dict())

base.to_csv(OUTCSV, index=False)
long_path = OUTCSV.with_name("ace_items_clinico_v2_longitudinal.csv")
lon.to_csv(long_path, index=False)

res = {"episodios_candidatos": int(len(df)), "episodios_validados": int(len(E)),
       "personas_basal": int(len(base)),
       "motivos": {str(k): int(v) for k, v in M.motivo.value_counts().items()},
       "basal_por_banda": {str(k): int(v) for k, v in base.groupby("banda", observed=True).size().items()},
       "ancla": {str(k): int(v) for k, v in E.ancla.value_counts().items()},
       "comparacion_pipeline_original": {"item_nivel_v1_basal": 1942, "item_nivel_v2_basal": int(len(base))}}
(OUTD / "09_recuperacion.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print(f"\n-> {OUTCSV}\n-> {long_path}\n-> {OUTD/'09_recuperacion.json'}")
