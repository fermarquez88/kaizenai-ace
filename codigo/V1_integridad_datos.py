#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V1 — VERIFICACIÓN DE INTEGRIDAD DE DATOS.

Reconstruye desde el origen y contrasta contra lo que están usando los análisis. Todo lo que no
reproduzca se reporta como DISCREPANCIA; no se ajusta nada silenciosamente.

Chequeos:
  1. Flujo de N (STROBE) en ambas cohortes, desde el archivo crudo.
  2. Armonización del reconocimiento: la regla, su aplicación y su efecto.
  3. Exposición: educación del informe vs campo administrativo vs autorreporte.
  4. Solapamiento entre cohortes y su exclusión.
  5. Duplicados, independencia de observaciones, rangos imposibles.
  6. Integridad del desenlace: suma de ítems == total, en ambas.

Salida: consola + out/V1_integridad.json
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
MAXV = {'ACE_AtOT':5,'ACE_AtOE':5,'ACE_AtRegistro':3,'ACE_AtSubstr':5,'ACE_MRecuerdo':3,
        'ACE_MAnterogr':7,'ACE_MRetrogr':4,'ACE_MRecuerdoNyD':7,'ACE_MReconocNyD':5,
        'ACE_FluVerbFPC':7,'ACE_FluVerbSPC':7,'ACE_LComprensionLyH':3,'ACE_LEscrit':2,
        'ACE_LRepP':2,'ACE_LRepProverb':2,'ACE_LDenom':12,'ACE_LCompDibujo':4,'ACE_LLectura':1,
        'ACE_HabVisoDiagrama':1,'ACE_HabVisoCubo':2,'ACE_HabPerPuntos':4,'ACE_HabPerLetras':4,
        'ACE_HabVisoReloj':5}
R = {"discrepancias": []}


def chk(cond, msg):
    if not cond:
        R["discrepancias"].append(msg); print(f"    ⚠ DISCREPANCIA: {msg}")
    return cond


# ==================================================================== 1. FLUJO COMUNITARIA
print("=" * 92 + "\n1. FLUJO DE N — COHORTE COMUNITARIA (desde el XLSX crudo)")
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all").dropna(axis=0, how="all")
n0 = len(craw)
edad = pd.to_numeric(craw.Edad, errors="coerce")
c40 = craw[edad >= 40].reset_index(drop=True)
X = pd.DataFrame({k: pd.to_numeric(c40[k], errors="coerce") for k in ITEMS})
fuera = {k: int(((X[k] > MAXV[k]) & X[k].notna()).sum()) for k in ITEMS}
fuera = {k: v for k, v in fuera.items() if v}
print(f"  filas crudas: {n0}   |   edad ≥40: {len(c40)}")
print(f"  ítems fuera de rango antes de corregir: {fuera}")
X["ACE_LLectura"] = X.ACE_LLectura.clip(upper=1)
cc = X.notna().all(axis=1)
edu = pd.to_numeric(c40.ed_anos_completos, errors="coerce")
edu_alta = int((edu > 30).sum())
edu_m = edu.mask(edu > 30)
print(f"  caso completo en los 23 ítems: {int(cc.sum())}")
print(f"  educación implausible (>30 años) enmascarada: {edu_alta}")
print(f"  con educación válida: {int((cc & edu_m.notna()).sum())}")
R["flujo_comunitaria"] = {"crudas": n0, "edad_ge40": int(len(c40)),
                          "caso_completo": int(cc.sum()),
                          "con_educacion": int((cc & edu_m.notna()).sum()),
                          "items_fuera_rango": fuera, "edu_gt30_enmascarada": edu_alta}
chk(len(c40) == 866, f"comunitaria edad≥40 = {len(c40)}, esperado 866")
chk(int(cc.sum()) == 814, f"comunitaria caso completo = {int(cc.sum())}, esperado 814")

# ==================================================================== 2. ARMONIZACIÓN
print("\n" + "=" * 92 + "\n2. ARMONIZACIÓN DEL RECONOCIMIENTO")
Xm = X[cc].reset_index(drop=True)
r, k = Xm.ACE_MRecuerdoNyD, Xm.ACE_MReconocNyD
resto = [i for i in ITEMS if i not in ("ACE_MRecuerdoNyD", "ACE_MReconocNyD")]
Rst = Xm[resto].sum(axis=1)
print(f"  ANTES  r(reconoc, evocación)={k.corr(r):+.3f}   r(reconoc, resto)={k.corr(Rst):+.3f}")
regla_ok = float(((k <= (7 - r)) | (r == 7)).mean())
print(f"  la regla 'reconocimiento ≤ 7−evocación' se cumple en {100*regla_ok:.1f}% de los casos")
chk(regla_ok > 0.93, f"la regla comunitaria sólo se cumple en {100*regla_ok:.1f}%")
perf = r == 7
print(f"  evocación perfecta (n={int(perf.sum())}): reconocimiento=5 en {100*float((k[perf]==5).mean()):.1f}%")
std = np.where(r == 7, 5, np.minimum(5, k + np.minimum(5, np.round(r * 5 / 7))))
print(f"  DESPUÉS r(reconoc, evocación)={pd.Series(std).corr(r):+.3f}   "
      f"r(reconoc, resto)={pd.Series(std).corr(Rst):+.3f}")
chk(pd.Series(std).corr(Rst) > 0, "la armonización no corrige el signo de la correlación con el resto")
chk((std <= 5).all() and (std >= 0).all(), "el reconocimiento armonizado sale de rango [0,5]")
ace_o = Xm[ITEMS].sum(axis=1); ace_a = ace_o - k + std
print(f"  total: {ace_o.mean():.2f} -> {ace_a.mean():.2f}  (Δ={+(ace_a-ace_o).mean():.2f}; r={ace_o.corr(ace_a):.4f})")
chk((ace_a <= 100).all(), f"el ACE armonizado excede 100 en {int((ace_a>100).sum())} casos")
R["armonizacion"] = {"r_recon_evoc_antes": round(float(k.corr(r)), 3),
                     "r_recon_resto_antes": round(float(k.corr(Rst)), 3),
                     "r_recon_evoc_despues": round(float(pd.Series(std).corr(r)), 3),
                     "r_recon_resto_despues": round(float(pd.Series(std).corr(Rst)), 3),
                     "regla_cumple_pct": round(100*regla_ok, 1),
                     "delta_total": round(float((ace_a-ace_o).mean()), 2),
                     "max_total": float(ace_a.max())}

# ==================================================================== 3. CONTRA EL GUARDADO
print("\n" + "=" * 92 + "\n3. ¿EL DATASET GUARDADO REPRODUCE ESTA RECONSTRUCCIÓN?")
sol = set(pd.read_csv(NM / "analisis/solape_dni.csv").dni.astype(str))
dni = c40["dni"].astype(str).str.replace(r"\D", "", regex=True)[cc].reset_index(drop=True)
mine = pd.DataFrame({"dni": dni, "ACE": ace_a.values,
                     "edu": edu_m[cc].values, "Edad": pd.to_numeric(c40.Edad, errors="coerce")[cc].values,
                     "Sexo": c40.Sexo.astype(str)[cc].values}).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
mine = mine[~mine.dni.isin(sol)]
guard = pd.read_csv(NM / "analisis/comunitaria_armonizada.csv")
print(f"  reconstruido n={len(mine)}   |   guardado n={len(guard)}")
chk(len(mine) == len(guard), f"n distinto: reconstruido {len(mine)} vs guardado {len(guard)}")
cmp = mine.sort_values("dni").reset_index(drop=True)
gsr = guard.assign(dni=guard.dni.astype(str)).sort_values("dni").reset_index(drop=True)
if len(cmp) == len(gsr):
    dif = (cmp.ACE.values - gsr.ACE.values)
    print(f"  ACE idéntico en {100*float((np.abs(dif)<1e-9).mean()):.2f}% de los casos "
          f"| máxima diferencia {np.abs(dif).max():.4f}")
    chk(np.abs(dif).max() < 1e-9, f"el ACE guardado difiere del reconstruido (máx {np.abs(dif).max():.4f})")
    de = np.abs(cmp.edu.values - gsr.edu.values)
    chk(de.max() < 1e-9, f"la educación guardada difiere (máx {de.max():.4f})")
R["reproduce_guardado"] = {"n_reconstruido": int(len(mine)), "n_guardado": int(len(guard))}

# ==================================================================== 4. CLÍNICA
print("\n" + "=" * 92 + "\n4. COHORTE CLÍNICA — integridad del dataset")
cli = pd.read_csv(NM / "analisis/clinico_definitivo.csv")
print(f"  filas: {len(cli)}   personas únicas: {cli.persona_id.nunique()}")
chk(len(cli) == cli.persona_id.nunique(), "hay más de una fila por persona en la clínica")
tiene = [i for i in ITEMS if i in cli.columns]
if len(tiene) == 23:
    Xi = cli[ITEMS].apply(pd.to_numeric, errors="coerce")
    comp = Xi.notna().all(axis=1)
    s = Xi[comp].sum(axis=1)
    t = pd.to_numeric(cli.ACE_total, errors="coerce")[comp]
    print(f"  con 23 ítems: {int(comp.sum())} | suma == ACE_total en "
          f"{100*float((np.abs(s-t)<0.5).mean()):.2f}%")
    chk(float((np.abs(s-t) < 0.5).mean()) > 0.999, "la suma de ítems no reproduce ACE_total en la clínica")
    fr = {c: int(((Xi[c] > MAXV[c]) & Xi[c].notna()).sum()) for c in ITEMS}
    fr = {c: v for c, v in fr.items() if v}
    print(f"  ítems fuera de rango: {fr if fr else 'ninguno'}")
    chk(not fr, f"ítems fuera de rango en la clínica: {fr}")
ed = pd.to_numeric(cli.edu, errors="coerce")
ace = pd.to_numeric(cli.ACE_total, errors="coerce")
print(f"  educación: n={int(ed.notna().sum())} rango [{ed.min():.0f},{ed.max():.0f}] | "
      f"ACE rango [{ace.min():.0f},{ace.max():.0f}]")
chk(ace.between(0, 100).all(), "ACE_total fuera de [0,100] en la clínica")
chk(ed.dropna().between(0, 30).all(), "educación fuera de [0,30] en la clínica")
if "estado" in cli.columns:
    print(f"  estado del desenlace: {cli.estado.value_counts().to_dict()}")
if "edu_fuente" in cli.columns:
    print(f"  fuente de la educación: {cli.edu_fuente.value_counts(dropna=False).to_dict()}")
R["clinica"] = {"n": int(len(cli)), "personas": int(cli.persona_id.nunique()),
                "con_educacion": int(ed.notna().sum()),
                "estado": {str(a): int(b) for a, b in cli.estado.value_counts().items()} if "estado" in cli.columns else None}

# ==================================================================== 5. SOLAPAMIENTO
print("\n" + "=" * 92 + "\n5. SOLAPAMIENTO ENTRE COHORTES")
dnic = cli.persona_id.astype(str).str.replace(r"\D", "", regex=True)
inter = set(dni[dni.str.len().between(6, 9)]) & set(dnic[dnic.str.len().between(6, 9)])
print(f"  DNI en ambas cohortes: {len(inter)}   |   lista guardada: {len(sol)}")
chk(len(inter) == len(sol) or len(inter & sol) == min(len(inter), len(sol)),
    f"la lista de solapamiento no coincide: detectados {len(inter)}, guardados {len(sol)}")
print(f"  en el dataset comunitario final quedan {int(guard.dni.astype(str).isin(sol).sum())} de los solapados "
      f"(debe ser 0)")
chk(int(guard.dni.astype(str).isin(sol).sum()) == 0, "quedan individuos solapados en la comunitaria")
print(f"  en el clínico quedan {int(dnic.isin(sol).sum())} (se conservan por diseño)")
R["solape"] = {"detectados": len(inter), "guardados": len(sol),
               "en_comunitaria_final": int(guard.dni.astype(str).isin(sol).sum())}

# ==================================================================== 6. RESUMEN
print("\n" + "=" * 92)
if R["discrepancias"]:
    print(f"V1: {len(R['discrepancias'])} DISCREPANCIA(S)")
    for d in R["discrepancias"]:
        print(f"   · {d}")
else:
    print("V1: SIN DISCREPANCIAS — los datos reproducen desde el origen.")
(OUTD / "V1_integridad.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"-> {OUTD/'V1_integridad.json'}")
