#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DIAGNOSTICO DE VALIDEZ (gate del estudio):
por que la extraccion item-nivel del ACE-III falla en 97% de los pacientes de baja escolaridad
y solo en 3% de los de alta, si el ACE se administra por igual (93% en ambos).

Importa porque el tramo <7 años de la cohorte clinica depende de `total_informe` (no verificado
contra items). Dos escenarios con consecuencias opuestas:
  (a) items TODOS en blanco / no hay hoja -> el evaluador solo cargo el total. El total es valido.
  (b) faltan items ESPECIFICOS (lectura, escritura, denominacion) -> administracion parcial:
      el total seria una suma sobre menos items => sesgado A LA BAJA en baja escolaridad
      => inflaria artificialmente el gradiente educativo. INUTILIZABLE.

Corre el mismo extract()/validate() del pipeline y registra, por tramo educativo, el motivo y
QUE items faltan.
"""
import sys, json, os
from pathlib import Path
from collections import Counter
import duckdb

INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
sys.path.insert(0, str(INECO / "src"))
os.chdir(INECO)
import extract_ace_items as EX  # noqa: E402

OUTD = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia/ACE/out")
CORP = "data/interim/corpus_full/Pacientes INECO"

con = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)
q = """
 with tot as (select eval_id, max(bruto) ace_total_db from resultados_v2
              where lower(test) like '%ace%' and bruto is not null and bruto between 1 and 100 group by 1)
 select e.eval_id, e.path, e.educacion, e.edad, t.ace_total_db,
        case when e.educacion<7 then '1.<7' when e.educacion<11 then '2.7-10'
             when e.educacion<=12 then '3.11-12' else '4.>12' end tramo
 from evaluaciones_v2 e join tot t on t.eval_id=e.eval_id
 where e.cohorte in ('nps_adulto','emicar') and e.edad between 40 and 105
   and e.educacion is not null and e.sexo is not null and e.fecha_ev is not null
"""
df = con.execute(q).fetchdf()
print(f"episodios con total ACE: {len(df)}")

# baja escolaridad completa + muestra de comparacion en alta
bajos = df[df.tramo.isin(["1.<7", "2.7-10"])]
altos = df[df.tramo.isin(["3.11-12", "4.>12"])].sample(n=400, random_state=7)
work = pd._concat if False else __import__("pandas").concat([bajos, altos])
print(f"a diagnosticar: {len(work)}  (baja {len(bajos)} / muestra alta {len(altos)})")

res = []
for i, r in enumerate(work.itertuples(), 1):
    p = r.path
    if not os.path.exists(p):
        res.append({"tramo": r.tramo, "motivo": "archivo_no_encontrado", "n_items": None, "faltan": []})
        continue
    d = EX.extract(p)
    if not d or "items" not in d:
        res.append({"tramo": r.tramo, "motivo": (d or {}).get("skip") or "load_fail",
                    "n_items": None, "faltan": []})
        continue
    EX.recover(d)
    it = d["items"]
    faltan = [k for k in EX.ITEMS if it.get(k) is None]
    ok, why = EX.validate(d)
    res.append({"tramo": r.tramo, "motivo": why, "n_items": 23 - len(faltan), "faltan": faltan,
                "total_hoja": d.get("total"), "total_db": r.ace_total_db})
    if i % 200 == 0:
        print(f"  ...{i}/{len(work)}", flush=True)

pd = __import__("pandas")
R = pd.DataFrame(res)
pd.set_option("display.width", 250)

print("\n" + "=" * 78)
print("MOTIVO DE FALLO ITEM-NIVEL POR TRAMO EDUCATIVO (% dentro del tramo)")
ct = pd.crosstab(R.tramo, R.motivo, normalize="index").mul(100).round(1)
print(ct.to_string())
print("\nconteos absolutos:")
print(pd.crosstab(R.tramo, R.motivo).to_string())

print("\n" + "=" * 78)
print("NUMERO DE ITEMS RECUPERADOS (0 = hoja vacia de items; 23 = completos)")
print(R.groupby("tramo").n_items.describe()[["count", "mean", "50%", "min", "max"]].round(1).to_string())
print("\ndistribucion de n_items por tramo:")
print(pd.crosstab(R.tramo, R.n_items.fillna(-1).astype(int)).to_string())

print("\n" + "=" * 78)
print("ITEMS FALTANTES MAS FRECUENTES, tramos bajos (si es administracion parcial, deberian")
print("concentrarse en lectura/escritura/denominacion; si es carga, faltan TODOS por igual)")
for tr in ["1.<7", "2.7-10", "3.11-12", "4.>12"]:
    sub = R[(R.tramo == tr) & (R.motivo != "ok")]
    c = Counter(x for f in sub.faltan for x in f)
    tot = len(sub)
    if not tot:
        continue
    top = ", ".join(f"{k}:{round(100*v/tot)}%" for k, v in c.most_common(6))
    print(f"  {tr:<8} (n fallidos={tot})  {top}")

OUTD.mkdir(exist_ok=True)
R.drop(columns=["faltan"]).to_csv(OUTD / "08_diag_fallo_items.csv", index=False)
print(f"\n-> {OUTD/'08_diag_fallo_items.csv'}")
