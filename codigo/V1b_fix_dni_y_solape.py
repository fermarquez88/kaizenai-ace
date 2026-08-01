#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V1b — CORRECCIÓN: normalización de documentos y recálculo del solapamiento.

Dos defectos detectados en V1:
  (a) Los documentos con cero a la izquierda pierden el cero al escribirse y releerse en CSV
      (pandas los infiere como entero). Eso rompía el pareo entre datasets y, en particular,
      la exclusión del solapamiento entre cohortes.
  (b) La lista de solapamiento se había calculado contra una versión anterior del dataset
      clínico; el dataset definitivo cambió de composición.

Corrección: se normaliza el documento a entero (se eliminan no-dígitos y ceros a la izquierda) en
TODAS las fuentes, y el solapamiento se recalcula entre los datasets definitivos.

Salida: analisis/solape_dni.csv (recalculado) + analisis/comunitaria_armonizada.csv (re-excluido)
        + out/V1b_fix.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd

warnings.filterwarnings("ignore")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
ITEMS = ['ACE_AtOT','ACE_AtOE','ACE_AtRegistro','ACE_AtSubstr','ACE_MRecuerdo','ACE_MAnterogr',
         'ACE_MRetrogr','ACE_MRecuerdoNyD','ACE_MReconocNyD','ACE_FluVerbFPC','ACE_FluVerbSPC',
         'ACE_LComprensionLyH','ACE_LEscrit','ACE_LRepP','ACE_LRepProverb','ACE_LDenom',
         'ACE_LCompDibujo','ACE_LLectura','ACE_HabVisoDiagrama','ACE_HabVisoCubo',
         'ACE_HabPerPuntos','ACE_HabPerLetras','ACE_HabVisoReloj']
R = {}


def norm_doc(s):
    """Documento -> entero canónico (sin no-dígitos ni ceros a la izquierda). NaN si no es válido."""
    d = pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
    d = d.where(d.str.len().between(6, 9))
    return pd.to_numeric(d, errors="coerce").astype("Int64")


# ------------------------------------------------ comunitaria, desde el origen
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all").dropna(axis=0, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
X = pd.DataFrame({k: pd.to_numeric(c40[k], errors="coerce") for k in ITEMS})
X["ACE_LLectura"] = X.ACE_LLectura.clip(upper=1)
cc = X.notna().all(axis=1)
Xm = X[cc].reset_index(drop=True)
r, k = Xm.ACE_MRecuerdoNyD.values, Xm.ACE_MReconocNyD.values
rec_std = np.where(r == 7, 5, np.minimum(5, k + np.minimum(5, np.round(r * 5 / 7))))
com = pd.DataFrame({
    "doc": norm_doc(c40["dni"])[cc].values,
    "ACE": (Xm[ITEMS].sum(axis=1) - Xm.ACE_MReconocNyD + rec_std).values,
    "ACE_orig": Xm[ITEMS].sum(axis=1).values,
    "ACE_col": pd.to_numeric(c40["ACE_TOTAL"], errors="coerce")[cc].values,
    "Edad": pd.to_numeric(c40.Edad, errors="coerce")[cc].values,
    "edu": pd.to_numeric(c40.ed_anos_completos, errors="coerce").mask(lambda s: s > 30)[cc].values,
    "Sexo": c40.Sexo.astype(str)[cc].values,
    "ola": pd.to_datetime(c40["Fecha"], errors="coerce").dt.year[cc].values,
}).dropna(subset=["ACE", "Edad", "edu", "Sexo"]).reset_index(drop=True)
print(f"comunitaria con desenlace, edad, educación y sexo: {len(com)}")
print(f"  documentos válidos: {int(com.doc.notna().sum())}  |  sin documento: {int(com.doc.isna().sum())}")

# ------------------------------------------------ clínica definitiva
cli = pd.read_csv(NM / "analisis/clinico_definitivo.csv")
cli["doc"] = norm_doc(cli.persona_id)
cli_ok = cli.dropna(subset=["ACE_total", "edu", "Edad", "Sexo"])
cli_ok = cli_ok[pd.to_numeric(cli_ok.edu, errors="coerce").between(0, 30)]
print(f"clínica analítica: {len(cli_ok)}  |  documentos válidos: {int(cli_ok.doc.notna().sum())}")

# ------------------------------------------------ solapamiento recalculado
inter = sorted(set(com.doc.dropna()) & set(cli_ok.doc.dropna()))
print(f"\nSOLAPAMIENTO recalculado entre los datasets definitivos: {len(inter)} individuos")
prev = set(pd.read_csv(NM / "analisis/solape_dni.csv").dni.astype("Int64").dropna())
print(f"  lista anterior: {len(prev)}   |   coinciden: {len(set(inter) & prev)}")
print(f"  nuevos que no estaban: {sorted(set(inter) - prev)}")
print(f"  de la lista anterior que ya no aplican: {sorted(prev - set(inter))}")
pd.DataFrame({"dni": inter}).to_csv(NM / "analisis/solape_dni.csv", index=False)
R["solape"] = {"n": len(inter), "anterior": len(prev),
               "coinciden": len(set(inter) & prev),
               "nuevos": sorted(int(x) for x in set(inter) - prev),
               "ya_no_aplican": sorted(int(x) for x in prev - set(inter))}

# ------------------------------------------------ exclusión y guardado
com_final = com[~com.doc.isin(inter)].copy()
print(f"\ncomunitaria tras excluir el solapamiento: {len(com)} -> {len(com_final)}")
resta = int(com_final.doc.isin(inter).sum())
print(f"  verificación: quedan {resta} solapados (debe ser 0)")
assert resta == 0
com_final["dni"] = com_final.doc          # se guarda como entero canónico
com_final.drop(columns=["doc"]).to_csv(NM / "analisis/comunitaria_armonizada.csv", index=False)

# ------------------------------------------------ round-trip
back = pd.read_csv(NM / "analisis/comunitaria_armonizada.csv")
back["doc"] = norm_doc(back.dni)
par = com_final.merge(back[["doc", "ACE"]].rename(columns={"ACE": "ACE_back"}), on="doc", how="left")
print(f"\nround-trip: pareados {int(par.ACE_back.notna().sum())}/{len(com_final)}  |  "
      f"diferencia máxima {float((par.ACE-par.ACE_back).abs().max()):.6f}")
assert int(par.ACE_back.notna().sum()) == len(com_final)
assert float((par.ACE - par.ACE_back).abs().max()) < 1e-9
print("  ✓ el documento sobrevive el ciclo de escritura y lectura, y los valores son idénticos")

R["comunitaria"] = {"antes_exclusion": int(len(com)), "final": int(len(com_final))}
(OUTD / "V1b_fix.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> analisis/solape_dni.csv | analisis/comunitaria_armonizada.csv | {OUTD/'V1b_fix.json'}")
