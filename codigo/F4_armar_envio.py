#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ensambla el manuscrito completo listo para envío: texto + tablas + figuras con epígrafes,
y lo convierte a PDF. Verifica el cumplimiento del reglamento del CAN 2026.

Salida: manuscrito/ENVIO_CAN2026.md  y  ENVIO_CAN2026.pdf
"""
import re, subprocess, sys
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
MAN = EST / "manuscrito"; FIG = EST / "figuras"

EPI = {
 "Figura4_correccion_continua": (
  "Figura 4. Corrección continua frente al escalón, a igual tasa de positividad",
  "**(a)** Puntaje esperado según la escolaridad (curva) con su banda del 80 %, estimado sobre las "
  "personas sin deterioro, frente a la regla vigente (escalón). La regla aproxima una curva mediante "
  "un salto situado donde la curva no presenta discontinuidad. **(b)** Proporción de personas sin "
  "deterioro señalada por cada regla, por tramo educativo, con todas las reglas calibradas a la "
  "misma tasa global de positividad. La corrección continua reduce el gradiente educativo de 30,6 a "
  "2,7 puntos porcentuales y elimina la inversión del tramo de 7 a 11 años."),
 "Figura1_forma_funcional": (
  "Figura 1. La forma de la asociación entre escolaridad y rendimiento cognitivo",
  "**(a)** Medias observadas por año de escolaridad (barras: intervalo de confianza del 95 %) y "
  "curva cuadrática ajustada por edad y sexo, con banda de confianza. **(b)** Pendiente marginal: "
  "ganancia de ACE-III por año adicional de escolaridad, estimada por método delta sobre la matriz "
  "de covarianzas robusta. La ganancia decae de forma continua y permanece positiva en todo el "
  "rango. **(c)** Curvatura estandarizada sobre el puntaje bruto y sobre la habilidad latente del "
  "modelo de respuesta graduada. Un tercio de la curvatura observada en el puntaje bruto es "
  "atribuible al techo del instrumento; los dos tercios restantes persisten en una métrica de "
  "intervalo sin techo."),
 "Figura2_falsacion": (
  "Figura 2. Falsación de la discontinuidad en los 12 años de escolaridad",
  "**(a)** Discontinuidad estimada en cada uno de los catorce cortes candidatos, con intervalo de "
  "confianza del 95 %. La línea roja marca el escalón de 18 puntos que resulta de la regla vigente; "
  "la banda ámbar, el corte en uso clínico. Ningún corte se aproxima a 18 puntos y el de 12 años es "
  "el de menor señal. El descenso aislado en 7 años de la cohorte clínica coincide con el valor de "
  "mayor amontonamiento declarativo, va en sentido contrario al efecto educativo y no replica en la "
  "cohorte comunitaria. **(b)** Regresión discontinua local en tres ventanas simétricas alrededor "
  "de los 12 años. **(c)** Prueba de equivalencia: el intervalo de confianza de la discontinuidad "
  "queda contenido incluso dentro de un margen de ±3 puntos."),
 "Figura3_corte_y_dispersion": (
  "Figura 3. Posición del corte vigente respecto del rendimiento esperado y de su dispersión",
  "**(a)** Rendimiento esperado en personas sin deterioro según los años de escolaridad, a los 65 "
  "años (curva continua), percentil 5 (punteada) y corte vigente (escalón rojo). El fondo indica "
  "dónde cae el corte: en rojo, por encima del rendimiento esperado; en ámbar, entre el esperado y "
  "el percentil 5. La banda entre ambas curvas se estrecha a medida que aumenta la escolaridad, "
  "porque la dispersión del rendimiento normal se reduce de 12,9 a 5,8 puntos. **(b)** Proporción "
  "de personas sin deterioro que la regla señala en cada año de escolaridad. El corte cambia de 68 "
  "a 86 puntos entre los 11 y los 12 años y la proporción señalada pasa de 5 % a 65 % sin que medie "
  "ningún cambio en el rendimiento. Modelo estimado sobre los 663 controles comunitarios, con la "
  "corrección de Harvey aplicada a la dispersión; valores ilustrativos, no constituyen normas "
  "poblacionales."),
}

src = (MAN / "MANUSCRITO.md").read_text()

# Las tablas se insertan como imágenes renderizadas con el estilo unificado (codigo/F9).
# Cada imagen ya lleva su título, su subtítulo y su nota al pie, de modo que no se
# duplica nada en el texto.
TABLAS = ["Tabla1", "Tabla2", "Tabla3"]
tablas = "\n\n---\n\n".join(
    f'<img src="file://{FIG}/{k}.jpg" style="width:100%">\n' for k in TABLAS)

# Las figuras van en orden, cada una con su epígrafe debajo.
ORDEN_FIG = ["Figura1_forma_funcional", "Figura2_falsacion",
             "Figura3_corte_y_dispersion", "Figura4_correccion_continua"]
figs = "\n\n---\n\n".join(
    f'## {EPI[k][0]}\n\n<img src="file://{FIG}/{k}.jpg" style="width:100%">\n\n{EPI[k][1]}\n'
    for k in ORDEN_FIG)

for _k in TABLAS + ORDEN_FIG:
    assert (FIG / f"{_k}.jpg").exists(), f"falta figuras/{_k}.jpg — correr F9 y F6 primero"

cab, resto = src.split("# Tablas y figuras", 1)
cola = "\n# Referencias" + resto.split("# Referencias", 1)[1]
doc = cab + "# Tablas\n\n" + tablas + "\n\n---\n\n# Figuras\n\n" + figs + "\n\n---\n" + cola
(MAN / "ENVIO_CAN2026.md").write_text(doc)

# ─────────────────────────────────────────── verificación del reglamento
pal = lambda b: len([w for w in re.sub(r"[#>*|`\[\]]", " ", b).split() if any(c.isalnum() for c in w)])
cuerpo = src.split("# Introducción")[1].split("# Tablas y figuras")[0]
res_es = src.split("## Resumen")[1].split("**Palabras clave")[0]
res_en = src.split("## Abstract")[1].split("**Keywords")[0]
refs = src.split("# Referencias")[1]
n_ref = len(re.findall(r"\n\d+\. ", refs))
años = [int(a) for a in re.findall(r"\b(20\d\d|19\d\d)[;.]", refs)]
rec = sum(1 for a in años if a >= 2021)

chk = [
    ("Cuerpo ≤ 4500 palabras", pal(cuerpo), 4500, pal(cuerpo) <= 4500),
    ("Resumen español ≤ 300", pal(res_es), 300, pal(res_es) <= 300),
    ("Abstract inglés ≤ 300", pal(res_en), 300, pal(res_en) <= 300),
    ("Tablas + figuras ≤ 7", 7, 7, True),
    ("Referencias ≤ 50", n_ref, 50, n_ref <= 50),
    ("≥70 % de los últimos 5 años", round(100*rec/max(len(años), 1), 1), 70, 100*rec/max(len(años), 1) >= 70),
]
print("VERIFICACIÓN DEL REGLAMENTO CAN 2026")
for nom, val, lim, ok in chk:
    print(f"  {'OK  ' if ok else 'FALLA'} {nom:<32} {val}  (límite {lim})")

falta = [l for l in doc.splitlines() if "[" in l and "]" in l and re.search(r"\[[A-ZÁÉÍÓÚÑ ]{3,}[^\]]*\]", l)]
print(f"\nCAMPOS PENDIENTES DE COMPLETAR: {len(falta)}")
for l in falta[:12]:
    print("   " + l.strip()[:110])

pdf = EST / "ENVIO_CAN2026.pdf"
try:
    subprocess.run([sys.executable, str(NM / "ACE/md2pdf.py"), str(MAN / "ENVIO_CAN2026.md"), str(pdf)],
                   capture_output=True, text=True, timeout=280)
except subprocess.TimeoutExpired:
    pass
if pdf.exists():
    print(f"\n-> {pdf}  ({pdf.stat().st_size/1024:.0f} kB)")
