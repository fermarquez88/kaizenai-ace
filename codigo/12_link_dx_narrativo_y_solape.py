#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(A) Enlaza el PERFIL COGNITIVO EXPLICITO de la conclusion del informe PDF (base v1,
    `perfil_cognitivo_inferido` con fuente_dx='narrativa' — el nombre de la tabla enganya:
    es la frase textual de la neuropsicologa, no una inferencia desde z) con los eval_id de v2.
    Join por DNI + fecha de evaluacion.
(B) Identifica los individuos presentes en AMBAS cohortes (comunidad Neuromentia <-> clinica)
    por DNI, para poder excluirlos de una de las dos.
(C) Valida el dx narrativo: ¿separa el ACE-III? ¿concuerda con el reference standard de bateria?

Salida: analisis/dx_narrativo_clinico.csv, analisis/solape_dni.csv, out/12_link.json
"""
import json, re, warnings
from pathlib import Path
import duckdb, pandas as pd, numpy as np

warnings.filterwarnings("ignore")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
pd.set_option("display.width", 260)
R = {}

c1 = duckdb.connect(str(INECO / "db/evaluaciones_v1.duckdb"), read_only=True)
c2 = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)

# ---------------------------------------------------------------- (A) dx narrativo
v1 = c1.execute("""
    select e.evaluacion_id, p.dni, e.fecha_evaluacion, e.programa, e.impresion_diagnostica,
           g.subtipo, g.severidad, g.frase_dx, g.normal_narrativa, g.deterioro_cognitivo
    from evaluaciones e
    join pacientes_pii p on p.paciente_id = e.paciente_id
    left join perfil_cognitivo_inferido g on g.evaluacion_id = e.evaluacion_id
    where p.dni is not null
""").fetchdf()
v1["dni"] = v1.dni.astype(str).str.replace(r"\D", "", regex=True)
v1["f"] = pd.to_datetime(v1.fecha_evaluacion, errors="coerce", dayfirst=True)
print(f"v1 evaluaciones con DNI: {len(v1)}  | con frase_dx: {v1.frase_dx.notna().sum()}")

# ¿'normal' es real o es el default cuando el regex no encontro frase?
tab = pd.crosstab(v1.subtipo.fillna("(sin subtipo)"), v1.frase_dx.notna(), margins=True)
tab.columns = [str(c) for c in tab.columns]
print("\nsubtipo x (tiene frase_dx explicita):")
print(tab.to_string())
R["subtipo_x_frase"] = tab.to_dict()

v2 = c2.execute("""
    select eval_id, persona_id, path, fecha_ev, edad, educacion, sexo, cohorte
    from evaluaciones_v2
    where cohorte in ('nps_adulto','emicar')
""").fetchdf()
v2["dni"] = v2.persona_id.astype(str).str.replace(r"\D", "", regex=True)
v2["f"] = pd.to_datetime(v2.fecha_ev, errors="coerce", dayfirst=True)

j = v2.merge(v1[["dni", "f", "subtipo", "severidad", "frase_dx", "normal_narrativa",
                 "impresion_diagnostica"]], on=["dni", "f"], how="left")
j = j.drop_duplicates("eval_id")
print(f"\nv2 adultas: {len(v2)}  | con dx narrativo enlazado (DNI+fecha): "
      f"{j.subtipo.notna().sum()} ({100*j.subtipo.notna().mean():.1f}%)")
# fallback: sólo DNI, cuando la fecha no matchea (una sola evaluación de esa persona en v1)
solo1 = v1[v1.dni.map(v1.dni.value_counts()) == 1][["dni", "subtipo", "severidad", "frase_dx"]]
j2 = j.merge(solo1, on="dni", how="left", suffixes=("", "_f"))
j2["subtipo"] = j2.subtipo.fillna(j2.subtipo_f)
j2["severidad"] = j2.severidad.fillna(j2.severidad_f)
j2["frase_dx"] = j2.frase_dx.fillna(j2.frase_dx_f)
print(f"tras fallback por DNI unico: {j2.subtipo.notna().sum()} "
      f"({100*j2.subtipo.notna().mean():.1f}%)")
R["cobertura_dx"] = {"v2_adultas": int(len(v2)), "enlazado_dni_fecha": int(j.subtipo.notna().sum()),
                     "enlazado_con_fallback": int(j2.subtipo.notna().sum())}

# ---------------------------------------------------------------- (C) validacion del dx
cli = pd.read_csv(NM / "analisis/ace_items_clinico_v2.csv")
ref = c2.execute("select eval_id, deterioro from reference_standard_pdf").fetchdf()
d = cli.merge(j2[["eval_id", "subtipo", "severidad", "frase_dx"]], on="eval_id", how="left") \
       .merge(ref, on="eval_id", how="left")
print(f"\nmuestra ACE v2 (n={len(d)}) con dx narrativo: {d.subtipo.notna().sum()} "
      f"({100*d.subtipo.notna().mean():.1f}%)")

print("\nVALIDACION — ACE-III por perfil explicito del informe:")
t = d.groupby("subtipo").ACE_total.agg(["count", "mean", "std"]).round(1).sort_values("mean")
print(t.to_string())
R["ACE_por_subtipo"] = t.reset_index().to_dict("records")

print("\nVALIDACION — ACE-III por severidad explicita:")
t2 = d.groupby("severidad").ACE_total.agg(["count", "mean", "std"]).round(1).sort_values("mean")
print(t2.to_string())
R["ACE_por_severidad"] = t2.reset_index().to_dict("records")

d["dx_norm"] = d.subtipo.map(lambda s: None if pd.isna(s) else (s == "normal"))
ct = pd.crosstab(d.dx_norm, d.deterioro, margins=True)
print("\nCONCORDANCIA dx narrativo (normal=True) x reference standard bateria (deterioro):")
print(ct.to_string())
both = d.dropna(subset=["dx_norm", "deterioro"])
if len(both):
    ac = float(((both.dx_norm) != (both.deterioro)).mean())
    R["concordancia_dx_vs_refstd"] = {"n": int(len(both)), "acuerdo": round(ac, 3)}
    print(f"  acuerdo = {ac:.3f}  (n={len(both)})")

d.to_csv(NM / "analisis/dx_narrativo_clinico.csv", index=False)

# ---------------------------------------------------------------- (B) solape de cohortes
com = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                    header=4, dtype=object).dropna(axis=1, how="all")
com = com[pd.to_numeric(com.Edad, errors="coerce") >= 40]
com["dni_n"] = com["dni"].astype(str).str.replace(r"\D", "", regex=True)
com = com[com.dni_n.str.len().between(6, 9)]
cli_dni = set(v2.dni[v2.dni.str.len().between(6, 9)])
sol = com[com.dni_n.isin(cli_dni)]
print(f"\nSOLAPE comunidad<->clinica por DNI: {sol.dni_n.nunique()} individuos"
      f"  ({100*sol.dni_n.nunique()/com.dni_n.nunique():.1f}% de la comunitaria de {com.dni_n.nunique()})")
pd.DataFrame({"dni": sorted(sol.dni_n.unique())}).to_csv(NM / "analisis/solape_dni.csv", index=False)
R["solape"] = {"n_individuos": int(sol.dni_n.nunique()),
               "n_comunidad_con_dni": int(com.dni_n.nunique()),
               "archivo": "analisis/solape_dni.csv"}

(OUTD / "12_link.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> analisis/dx_narrativo_clinico.csv | analisis/solape_dni.csv | {OUTD/'12_link.json'}")
