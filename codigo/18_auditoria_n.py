#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUDITORÍA DE RECUPERACIÓN DE N — cohorte clínica (Instituto de Neurociencias).

Cuantifica cada paso de exclusión y evalúa qué es recuperable sin perder rigor.
Los cuatro frentes:
  A. Cohortes: ¿entra alguna además de nps_adulto + emicar?
  B. ACE-III: casos con TOTAL validado pero sin los 23 ítems completos. Para un análisis del
     puntaje total NO se necesitan los ítems; sólo se necesita que el total sea confiable.
  C. Educación: 209 casos sin años en v1. ¿Se recuperan re-parseando su informe PDF?
  D. Demografía y edad.

No decide: mide. Salida: out/18_auditoria_n.json
"""
import json, os, re, glob, warnings
from pathlib import Path
import duckdb, pandas as pd

warnings.simplefilter("ignore")
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
os.chdir(INECO)
c1 = duckdb.connect(str(INECO / "db/evaluaciones_v1.duckdb"), read_only=True)
c2 = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)
R = {}
pd.set_option("display.width", 260)

# ---------------------------------------------------------------- A. cohortes
print("=" * 92 + "\nA. COHORTES DISPONIBLES (episodios, edad>=40)")
coh = c2.execute("""select cohorte, count(*) episodios, count(distinct persona_id) personas,
    round(avg(edad),1) edad_media, round(avg(educacion),1) educ_media
  from evaluaciones_v2 where edad between 40 and 105 group by 1 order by 2 desc""").fetchdf()
print(coh.to_string())
R["A_cohortes"] = coh.to_dict("records")

# ---------------------------------------------------------------- B. ACE: total vs ítems
print("\n" + "=" * 92 + "\nB. DISPONIBILIDAD DEL ACE-III (episodios de cohortes adultas, edad 40-105)")
c2.execute(f"""create temp table ace23 as select * from
   read_csv_auto('{INECO}/data/interim/ace_items_clinico.csv', header=true)""")
base = c2.execute("""
 with tot as (select eval_id, max(bruto) tot from resultados_v2
              where lower(test) like '%ace%' and bruto is not null and bruto between 1 and 100
              group by 1)
 select e.eval_id, e.persona_id, e.path, e.edad, e.sexo, e.fecha_ev, e.cohorte, e.educacion edu_excel,
        t.tot
 from evaluaciones_v2 e left join tot t on t.eval_id=e.eval_id
 where e.cohorte in ('nps_adulto','emicar') and e.edad between 40 and 105
""").fetchdf()
v2it = pd.read_csv(NM / "analisis/ace_items_clinico_v2.csv")[["eval_id"]].assign(items_ok=1)
base = base.merge(v2it, on="eval_id", how="left")
base["items_ok"] = base.items_ok.fillna(0).astype(int)

def paso(nombre, mask):
    print(f"  {nombre:<58} {int(mask.sum()):>5} episodios | {base[mask].persona_id.nunique():>5} personas")
    return {"episodios": int(mask.sum()), "personas": int(base[mask].persona_id.nunique())}

R["B_flujo"] = {}
R["B_flujo"]["adultas_40_105"] = paso("episodios en cohortes adultas, edad 40-105", pd.Series(True, index=base.index))
R["B_flujo"]["demog_ok"] = paso("con sexo y fecha", base.sexo.notna() & base.fecha_ev.notna())
R["B_flujo"]["con_total"] = paso("con TOTAL de ACE-III válido (1-100)", base.tot.notna())
R["B_flujo"]["con_items"] = paso("con los 23 ÍTEMS validados (dataset v2)", base.items_ok == 1)
R["B_flujo"]["total_sin_items"] = paso("con TOTAL pero SIN ítems -> candidatos a recuperar",
                                       base.tot.notna() & (base.items_ok == 0))

# ---------------------------------------------------------------- C. educación
print("\n" + "=" * 92 + "\nC. EDUCACIÓN (años del informe PDF, v1)")
v1 = c1.execute("""select p.dni, e.fecha_evaluacion, e.anios_educacion
   from evaluaciones e join pacientes_pii p on p.paciente_id=e.paciente_id
   where p.dni is not null and e.anios_educacion is not null""").fetchdf()
v1["dni"] = v1.dni.astype(str).str.replace(r"\D", "", regex=True)
v1["f"] = pd.to_datetime(v1.fecha_evaluacion, errors="coerce", dayfirst=True)
v1 = v1.dropna(subset=["f"]).drop_duplicates(["dni", "f"])
base["dni"] = base.persona_id.astype(str).str.replace(r"\D", "", regex=True)
base["f"] = pd.to_datetime(base.fecha_ev, errors="coerce", dayfirst=True)
base = base.merge(v1[["dni", "f", "anios_educacion"]], on=["dni", "f"], how="left")
# fallback: mismo DNI con una sola evaluación en v1
uno = v1[v1.dni.map(v1.dni.value_counts()) == 1][["dni", "anios_educacion"]]
base = base.merge(uno.rename(columns={"anios_educacion": "edu_dni"}), on="dni", how="left")
base["edu_pdf"] = base.anios_educacion.fillna(base.edu_dni)

con_ace = base[base.tot.notna()]
print(f"  episodios con ACE: {len(con_ace)}")
for lab, col in [("con educación PDF (DNI+fecha)", "anios_educacion"),
                 ("con educación PDF (+fallback DNI único)", "edu_pdf")]:
    n = int(con_ace[col].notna().sum())
    print(f"    {lab:<46} {n:>5}  ({100*n/len(con_ace):.1f}%)")
R["C_educacion"] = {"con_ace": int(len(con_ace)),
                    "pdf_dni_fecha": int(con_ace.anios_educacion.notna().sum()),
                    "pdf_con_fallback": int(con_ace.edu_pdf.notna().sum())}

# los que siguen sin educación: ¿tienen informe PDF re-parseable?
falta = con_ace[con_ace.edu_pdf.isna()]
print(f"  sin educación tras el fallback: {len(falta)} episodios / {falta.persona_id.nunique()} personas")
EXCL = re.compile(r"jotform|cuestion|formul|protocol", re.I)
tienen_pdf = 0
for r in falta.drop_duplicates("persona_id").itertuples():
    carp = os.path.dirname(str(r.path))
    if any(not EXCL.search(os.path.basename(p)) for p in glob.glob(carp + "/*.pdf")):
        tienen_pdf += 1
print(f"    de esas personas, con informe PDF en su carpeta (re-parseables): {tienen_pdf}")
R["C_educacion"]["sin_edu_pero_con_pdf"] = int(tienen_pdf)

# ---------------------------------------------------------------- D. techo alcanzable
print("\n" + "=" * 92 + "\nD. N ALCANZABLE (1 evaluación por persona = basal)")
def basal(d):
    d = d.copy(); d["fp"] = pd.to_datetime(d.fecha_ev, errors="coerce", dayfirst=True)
    return d.sort_values(["persona_id", "fp", "eval_id"]).groupby("persona_id", as_index=False).first()

esc = {
    "actual (ítems validados + edu PDF)": base[(base.items_ok == 1) & base.edu_pdf.notna()],
    "+ casos con TOTAL sin ítems": base[base.tot.notna() & base.edu_pdf.notna()],
    "techo: con TOTAL, cualquier educación": base[base.tot.notna()],
}
R["D_escenarios"] = {}
for k, v in esc.items():
    b = basal(v.dropna(subset=["sexo", "fecha_ev"]))
    lt7 = int((b.edu_pdf < 7).sum()) if "edu_pdf" in b else 0
    print(f"  {k:<44} n={len(b):>5}   con <7 años de educación: {lt7}")
    R["D_escenarios"][k] = {"n": int(len(b)), "n_lt7": lt7}

(OUTD / "18_auditoria_n.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> {OUTD/'18_auditoria_n.json'}")
