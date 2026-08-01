#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CONSTRUCCIÓN DEFINITIVA del dataset clínico (una sola pasada sobre el corpus).

Para CADA episodio candidato registra: los 23 ítems si están completos, la suma, el total del
bloque RESULTADOS de la hoja, el total registrado en `resultados_v2` (fuente independiente), y
los años de educación leídos del INFORME PDF. Así la regla de inclusión se aplica después, de
forma explícita y auditable, en vez de estar embebida en el extractor.

REGLA DE INCLUSIÓN (declarada a priori)
  Desenlace ACE-III total, válido si:
    (i)  hay al menos un total (hoja o `resultados_v2`) en [1,100]; Y
    (ii) si los 23 ítems están completos y en rango, su suma coincide (±0,5) con al menos un
         total -> se usa la suma de ítems (validada por doble fuente); Y
    (iii) si los ítems están completos pero NO coinciden con ningún total -> se EXCLUYE
          (dato no reconciliable, no se elige arbitrariamente una fuente); Y
    (iv) si los ítems no están completos -> se usa el total, marcado `solo_total`.
  Exposición: años de educación del informe PDF (el campo del Excel institucional asigna 11 por
  defecto en baja escolaridad; ver auditoría). Prioridad: v1 (ya parseado) -> re-parseo del PDF.

Salida: analisis/clinico_definitivo.csv + out/19_build.json
"""
import json, os, re, sys, glob, warnings
from pathlib import Path
import duckdb, pandas as pd

warnings.simplefilter("ignore")
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
sys.path.insert(0, str(INECO / "src"))
os.chdir(INECO)
import extract_ace_items as EX  # noqa: E402
import pdfplumber                # noqa: E402

MAXV = {k: v[2] for k, v in EX.CELL.items()}; MAXV["ACE_HabVisoReloj"] = 5
EXCL_PDF = re.compile(r"jotform|cuestion|formul|protocol", re.I)
RX_EDU = re.compile(r"A[nñ]os de Educaci[oó]n\s*:?\s*([0-9]{1,2})", re.I)
c1 = duckdb.connect(str(INECO / "db/evaluaciones_v1.duckdb"), read_only=True)
c2 = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)

# ------------------------------------------------ candidatos
cand = c2.execute("""
 with tot as (select eval_id, max(bruto) tot_db from resultados_v2
              where lower(test) like '%ace%' and bruto is not null and bruto between 1 and 100 group by 1)
 select e.eval_id, e.persona_id, e.path, e.edad, e.sexo, e.fecha_ev, e.cohorte, e.evaluador,
        e."year" anio, e.educacion edu_excel, t.tot_db
 from evaluaciones_v2 e left join tot t on t.eval_id=e.eval_id
 where e.cohorte in ('nps_adulto','emicar') and e.edad between 40 and 105
   and e.sexo is not null and e.fecha_ev is not null
""").fetchdf()
print(f"candidatos (cohortes adultas, 40-105, demografía OK): {len(cand)}", flush=True)

# ------------------------------------------------ educación del informe PDF (v1)
v1 = c1.execute("""select p.dni, e.fecha_evaluacion, e.anios_educacion
   from evaluaciones e join pacientes_pii p on p.paciente_id=e.paciente_id
   where p.dni is not null and e.anios_educacion is not null""").fetchdf()
v1["dni"] = v1.dni.astype(str).str.replace(r"\D", "", regex=True)
v1["f"] = pd.to_datetime(v1.fecha_evaluacion, errors="coerce", dayfirst=True)
v1 = v1.dropna(subset=["f"]).drop_duplicates(["dni", "f"])
cand["dni"] = cand.persona_id.astype(str).str.replace(r"\D", "", regex=True)
cand["f"] = pd.to_datetime(cand.fecha_ev, errors="coerce", format="ISO8601")
cand = cand.merge(v1[["dni", "f", "anios_educacion"]], on=["dni", "f"], how="left")
uno = v1[v1.dni.map(v1.dni.value_counts()) == 1][["dni", "anios_educacion"]] \
        .rename(columns={"anios_educacion": "edu_dni"})
cand = cand.merge(uno, on="dni", how="left")
cand["edu_pdf"] = cand.anios_educacion.fillna(cand.edu_dni)
cand["edu_fuente"] = cand.anios_educacion.notna().map({True: "v1_dni_fecha", False: None})
cand.loc[cand.edu_fuente.isna() & cand.edu_dni.notna(), "edu_fuente"] = "v1_dni_unico"
print(f"  con educación del informe (v1): {int(cand.edu_pdf.notna().sum())}", flush=True)

# ------------------------------------------------ pasada única sobre el corpus
filas = []
n_reparse_ok = 0
for i, r in enumerate(cand.itertuples(), 1):
    rec = {"eval_id": r.eval_id, "items_ok": 0, "suma": None, "tot_hoja": None,
           "motivo": None, "edu_reparse": None}
    p = str(r.path)
    if os.path.exists(p):
        d = EX.extract(p)
        if d and "items" in d:
            EX.recover(d)
            it, subt, th = d["items"], d["subt"], d["total"]
            rec["tot_hoja"] = th
            falt = [k for k in EX.ITEMS if it.get(k) is None]
            if not falt:
                fuera = [k for k in EX.ITEMS if not (0 <= it[k] <= MAXV[k])]
                dom_mal = [dn for dn, (_x, ks) in EX.DOM.items()
                           if subt.get(dn) is not None and abs(sum(it[k] for k in ks) - subt[dn]) > 0.5]
                if fuera:
                    rec["motivo"] = "rango"
                elif dom_mal:
                    rec["motivo"] = "dominio_no_cuadra"
                else:
                    rec["items_ok"] = 1
                    rec["suma"] = sum(it[k] for k in EX.ITEMS)
                    for k in EX.ITEMS:
                        rec[k] = int(it[k])
            else:
                rec["motivo"] = "items_incompletos"
        else:
            rec["motivo"] = (d or {}).get("skip") or "no_abre"
    else:
        rec["motivo"] = "archivo_ausente"
    # educación: re-parseo del informe PDF sólo si falta
    if pd.isna(getattr(r, "edu_pdf")):
        for q in glob.glob(os.path.dirname(p) + "/*.pdf"):
            if EXCL_PDF.search(os.path.basename(q)):
                continue
            try:
                with pdfplumber.open(q) as pdf:
                    t = "\n".join((pg.extract_text() or "") for pg in pdf.pages[:2])
            except Exception:
                continue
            mm = RX_EDU.search(t or "")
            if mm:
                rec["edu_reparse"] = int(mm.group(1)); n_reparse_ok += 1
                break
    filas.append(rec)
    if i % 300 == 0:
        print(f"  ...{i}/{len(cand)}  items_ok={sum(f['items_ok'] for f in filas)}"
              f"  edu_reparse={n_reparse_ok}", flush=True)

E = pd.DataFrame(filas)
d = cand.merge(E, on="eval_id", how="left")
print(f"\nre-parseo de educación desde PDF: +{n_reparse_ok} episodios")
d["edu"] = d.edu_pdf.fillna(d.edu_reparse)
d.loc[d.edu_fuente.isna() & d.edu_reparse.notna(), "edu_fuente"] = "pdf_reparse"
print(f"educación final disponible: {int(d.edu.notna().sum())}/{len(d)} "
      f"({100*d.edu.notna().mean():.1f}%)  por fuente: {d.edu_fuente.value_counts().to_dict()}")

# ------------------------------------------------ regla de inclusión
tot_ok = d[["tot_db", "tot_hoja"]].apply(
    lambda s: pd.to_numeric(s, errors="coerce").where(lambda x: x.between(1, 100)))
d["hay_total"] = tot_ok.notna().any(axis=1)
concuerda = d.items_ok.eq(1) & tot_ok.sub(d.suma, axis=0).abs().le(0.5).any(axis=1)
d["estado"] = "excluido_sin_total"
d.loc[d.hay_total & d.items_ok.eq(0), "estado"] = "solo_total"
d.loc[d.items_ok.eq(1) & ~concuerda, "estado"] = "excluido_no_reconcilia"
d.loc[concuerda, "estado"] = "items_validados"
d["ACE_total"] = d.suma.where(concuerda, tot_ok.bfill(axis=1).iloc[:, 0])

print("\nestado por episodio:", d.estado.value_counts().to_dict())
print("motivos de los que no tienen ítems:", d[d.items_ok.eq(0)].motivo.value_counts().to_dict())

inc = d[d.estado.isin(["items_validados", "solo_total"]) & d.ACE_total.notna()].copy()
inc = inc.sort_values(["persona_id", "f", "eval_id"])
basal = inc.groupby("persona_id", as_index=False).first()
reev = inc[inc.persona_id.duplicated(keep=False)]
print(f"\nepisodios incluidos {len(inc)} -> personas (basal) {len(basal)} "
      f"| reevaluados {reev.persona_id.nunique()} personas / {len(reev)} evals")
b = basal[basal.edu.notna()]
print(f"basal con educación válida: {len(b)}  | con <7 años: {int((b.edu<7).sum())} "
      f"({100*(b.edu<7).mean():.1f}%)")
print("  por estado:", b.estado.value_counts().to_dict())

basal["Sexo"] = basal.sexo.map({"F": "Mujer", "M": "Hombre"})
basal["Edad"] = basal.edad
basal.to_csv(NM / "analisis/clinico_definitivo.csv", index=False)
res = {"candidatos": int(len(cand)), "estado": {k: int(v) for k, v in d.estado.value_counts().items()},
       "personas_basal": int(len(basal)), "basal_con_educacion": int(len(b)),
       "basal_lt7": int((b.edu < 7).sum()),
       "edu_fuente": {str(k): int(v) for k, v in basal.edu_fuente.value_counts().items()},
       "reparse_pdf": int(n_reparse_ok),
       "reevaluados_personas": int(reev.persona_id.nunique())}
(OUTD / "19_build.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print(f"\n-> analisis/clinico_definitivo.csv | {OUTD/'19_build.json'}")
