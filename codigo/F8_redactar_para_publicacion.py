#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redacta los identificadores directos y el texto clínico textual que quedaron dentro de dos archivos
de resultados, para que puedan publicarse sin exponer datos individuales.

Qué se redacta y por qué:

  resultados/V1b_fix.json
      /solape/nuevos y /solape/ya_no_aplican contenían los documentos de identidad de los
      participantes presentes en ambas bases. Se reemplazan por el conteo, que es lo único que el
      resultado necesita informar.

  resultados/04_piloto_diagnostico.json
      /casos[]/dx/frase_dx contenía la oración de conclusión transcripta de historias clínicas
      reales. Se reemplaza por una marca de redacción; la codificación derivada de cada oración
      —que es el resultado— se conserva intacta.

Los archivos originales se copian a datos/_originales_sin_redactar/, que está fuera del control de
versiones, de modo que nada se pierde localmente.

Idempotente: correrlo dos veces no cambia nada la segunda vez.
"""
import json, shutil
from pathlib import Path

EST = Path(__file__).resolve().parent.parent
RES = EST / "resultados"
BAK = EST / "datos/_originales_sin_redactar"
BAK.mkdir(parents=True, exist_ok=True)

MARCA_ID = "[documentos redactados para publicación — ver codigo/F8_redactar_para_publicacion.py]"
MARCA_TX = "[conclusión clínica redactada para publicación]"

cambios = []


def respaldar(p: Path):
    destino = BAK / p.name
    if not destino.exists():
        shutil.copy2(p, destino)


# ── 1. documentos de identidad en el cálculo de solapamiento ────────────────
p = RES / "V1b_fix.json"
d = json.loads(p.read_text(encoding="utf-8"))
sol = d.get("solape", {})
for clave in ("nuevos", "ya_no_aplican"):
    v = sol.get(clave)
    if isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
        respaldar(p)
        sol[clave] = {"n": len(v), "_redactado": MARCA_ID}
        cambios.append(f"V1b_fix.json  /solape/{clave}: {len(v)} documentos -> conteo")
if cambios:
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# ── 2. oraciones de conclusión transcriptas ─────────────────────────────────
p = RES / "04_piloto_diagnostico.json"
d = json.loads(p.read_text(encoding="utf-8"))
n = 0


def limpiar(o):
    global n
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k == "frase_dx" and isinstance(v, str) and v != MARCA_TX:
                o[k] = MARCA_TX
                n += 1
            else:
                limpiar(v)
    elif isinstance(o, list):
        for v in o:
            limpiar(v)


limpiar(d)
if n:
    respaldar(p)
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    cambios.append(f"04_piloto_diagnostico.json  frase_dx: {n} oraciones -> marca de redacción")

# ── informe ─────────────────────────────────────────────────────────────────
if cambios:
    for c in cambios:
        print("  redactado:", c)
    print(f"\noriginales respaldados en {BAK.relative_to(EST)}/ (fuera del control de versiones)")
else:
    print("nada que redactar: los archivos ya estaban limpios")
