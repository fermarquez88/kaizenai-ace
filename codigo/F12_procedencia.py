#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
F12 — Mapa de procedencia: qué script produce cada salida, y qué salida no produce ninguno.

Por qué existe. El trabajo declara publicar el código completo. La auditoría del repositorio encontró
tres clases de agujero en esa promesa:

  1. Figuras y JSON presentes en el repositorio que **ningún script generaba** (se habían producido en
     sesiones interactivas). Dos figuras del manuscrito y los coeficientes de la calculadora estaban en
     ese estado; ya se corrigieron con `F11_figuras_instrumento_y_equidad.py` y `CALC_coeficientes.py`.
  2. Scripts de la cadena temprana que escriben **fuera del árbol del repositorio** (en el proyecto
     Neuromentia), de modo que quien clone el repositorio no puede regenerar sus salidas ni siquiera
     con los datos.
  3. Salidas heredadas de versiones anteriores del análisis, conservadas por trazabilidad, cuyo script
     ya no forma parte de la cadena vigente.

Este script recorre `codigo/` buscando escrituras y las cruza contra lo que hay en `resultados/`,
`figuras/` y `tablas/`. Produce PROCEDENCIA.md, que se regenera y por lo tanto no se desactualiza.

Uso: python F12_procedencia.py
Salida: PROCEDENCIA.md
"""
import re
from pathlib import Path
from collections import defaultdict

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
COD = EST / "codigo"
DIRS = {"resultados": "*.json", "figuras": "*.jpg", "tablas": "*"}
# nombres que aparecen en el código pero corresponden a rutas fuera del repositorio
FUERA = re.compile(r'NM\s*/\s*"|NM\s*/\s*f"|INECO\s*/\s*"')

# ── 1. qué nombra cada script
nombra = defaultdict(set)
escribe_fuera = set()
for py in sorted(COD.glob("*.py")):
    txt = py.read_text(errors="ignore")
    for m in re.finditer(r'[\w\-]+\.(?:json|jpg|pdf|csv|md)', txt):
        nombra[py.name].add(m.group(0))
    if FUERA.search(txt) and re.search(r'OUTD|out/|/ "ACE/out"', txt):
        escribe_fuera.add(py.name)

productor = defaultdict(list)
for script, salidas in nombra.items():
    for s in salidas:
        productor[s].append(script)

# ── 2. cruzar con lo que existe
filas, huerfanas = [], []
for d, patron in DIRS.items():
    for f in sorted((EST / d).glob(patron)):
        if f.name.startswith("."):
            continue
        # el .pdf de una figura lo produce el mismo script que su .jpg
        clave = f.name if f.name in productor else f.with_suffix(".jpg").name
        prods = productor.get(clave) or productor.get(f.name) or []
        prods = [p for p in prods if not p.startswith("F12")]
        if prods:
            filas.append((f"{d}/{f.name}", " · ".join(sorted(prods))))
        else:
            huerfanas.append(f"{d}/{f.name}")

L = ["# Procedencia de cada salida", "",
     "> Generado por `codigo/F12_procedencia.py`. **No editar a mano**: se regenera.", "",
     "El trabajo declara publicar el código completo. Esta tabla es la comprobación de esa",
     "declaración: para cada archivo de `resultados/`, `figuras/` y `tablas/`, qué script lo produce.",
     "", "---", "", "## Salidas con script identificado", "",
     "| Salida | Script |", "|---|---|"]
L += [f"| `{a}` | `{b}` |" for a, b in filas]

L += ["", "---", "", "## Salidas sin script en el repositorio", ""]
if huerfanas:
    L += [f"Son **{len(huerfanas)}**. Corresponden a la cadena exploratoria temprana (bloques 00–28),",
          "ejecutada antes de que el repositorio existiera y conservada por trazabilidad, y a bloques de",
          "verificación cuyo script vive fuera del árbol. **No forman parte de la cadena vigente**: el",
          "análisis del manuscrito se reproduce con los scripts listados arriba.", "",
          "| Salida |", "|---|"]
    L += [f"| `{h}` |" for h in huerfanas]
else:
    L += ["Ninguna."]

L += ["", "---", "", "## Scripts que escriben fuera del árbol del repositorio", ""]
if escribe_fuera:
    L += ["Estos scripts dejan sus salidas en el proyecto Neuromentia y no en `resultados/`. Quien clone",
          "el repositorio no puede regenerarlas aunque disponga de los datos. Se documenta como",
          "limitación de reproducibilidad conocida.", "",
          "| Script |", "|---|"]
    L += [f"| `codigo/{s}` |" for s in sorted(escribe_fuera)]
else:
    L += ["Ninguno."]

(EST / "PROCEDENCIA.md").write_text("\n".join(L) + "\n")
print(f"-> PROCEDENCIA.md")
print(f"   {len(filas)} salidas con script · {len(huerfanas)} sin script · "
      f"{len(escribe_fuera)} scripts escriben fuera del árbol")
