#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ensambla cualquier versión del manuscrito a PDF, con las figuras que le corresponden.

Uso:  python F5_armar_version.py <archivo_md> <salida.pdf> [n_figuras]

Las versiones v1 y v2 (enfoque de falsación) llevan 3 figuras; la v3 (corrección continua) lleva 4.
"""
import re, subprocess, sys
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
MAN = EST / "manuscrito"; FIG = EST / "figuras"

EPI = [
 ("Figura1_forma_funcional",
  "Figura 1. La forma de la asociación entre escolaridad y rendimiento cognitivo",
  "**(a)** Medias observadas por año de escolaridad (barras: intervalo de confianza del 95 %) y curva "
  "cuadrática ajustada por edad y sexo, con banda de confianza. **(b)** Pendiente marginal: ganancia "
  "de ACE-III por año adicional de escolaridad, estimada por método delta sobre la matriz de "
  "covarianzas robusta. La ganancia decae de forma continua y permanece positiva en todo el rango. "
  "**(c)** Curvatura estandarizada sobre el puntaje bruto y sobre la habilidad latente del modelo de "
  "respuesta graduada. Un tercio de la curvatura observada en el puntaje bruto es atribuible al techo "
  "del instrumento; los dos tercios restantes persisten en una métrica de intervalo sin techo."),
 ("Figura2_falsacion",
  "Figura 2. Falsación de la discontinuidad en los 12 años de escolaridad",
  "**(a)** Discontinuidad estimada en cada uno de los catorce cortes candidatos, con intervalo de "
  "confianza del 95 %. La línea roja marca el escalón de 18 puntos que resulta de la regla vigente; la "
  "banda ámbar, el corte en uso clínico. Ningún corte se aproxima a 18 puntos y el de 12 años es el de "
  "menor señal. El descenso aislado en 7 años de la cohorte clínica coincide con el valor de mayor "
  "amontonamiento declarativo, va en sentido contrario al efecto educativo y no replica en la cohorte "
  "comunitaria. **(b)** Regresión discontinua local en tres ventanas simétricas alrededor de los 12 "
  "años. **(c)** Prueba de equivalencia: el intervalo de confianza de la discontinuidad queda contenido "
  "incluso dentro de un margen de ±3 puntos."),
 ("Figura3_consecuencia",
  "Figura 3. Consecuencia de aplicar la regla vigente",
  "**(a)** Proporción de personas señaladas por la regla, año a año de escolaridad. El corte cambia de "
  "68 a 86 puntos entre los 11 y los 12 años. **(b)** Magnitudes comparadas en la misma escala: el "
  "sesgo educativo del puntaje total a igual habilidad latente en cada cohorte, el error estándar de "
  "medición del propio ACE-III y la corrección de 18 puntos que aplica la regla."),
 ("Figura4_correccion_continua",
  "Figura 4. Corrección continua frente al escalón, a igual tasa de positividad",
  "**(a)** Puntaje esperado según la escolaridad (curva) con su banda del 80 %, estimado sobre las "
  "personas sin deterioro, frente a la regla vigente (escalón). **(b)** Proporción de personas sin "
  "deterioro señalada por cada regla, por tramo educativo, con todas las reglas calibradas a la misma "
  "tasa global de positividad."),
]

src_path = Path(sys.argv[1]) if len(sys.argv) > 1 else MAN / "MANUSCRITO.md"
out_pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else EST / "ENVIO_CAN2026.pdf"
n_fig = int(sys.argv[3]) if len(sys.argv) > 3 else 4

src = src_path.read_text()
tablas = "\n\n---\n\n".join((MAN / f"Tabla{i}.md").read_text().strip() for i in (1, 2, 3))
figs = "\n\n---\n\n".join(
    f'## {t}\n\n<img src="file://{FIG}/{k}.jpg" style="width:100%">\n\n{c}\n'
    for k, t, c in EPI[:n_fig])

cab, resto = src.split("# Tablas y figuras", 1)
cola = "\n# Referencias" + resto.split("# Referencias", 1)[1]
doc = cab + "# Tablas\n\n" + tablas + "\n\n---\n\n# Figuras\n\n" + figs + "\n\n---\n" + cola
tmp = MAN / (out_pdf.stem + ".md")
tmp.write_text(doc)

pal = lambda b: len([w for w in re.sub(r"[#>*|`\[\]]", " ", b).split() if any(c.isalnum() for c in w)])
cuerpo = src.split("# Introducción")[1].split("# Tablas y figuras")[0]
res_es = src.split("## Resumen")[1].split("**Palabras clave")[0]
res_en = src.split("## Abstract")[1].split("**Keywords")[0]
refs = src.split("# Referencias")[1]
años = [int(a) for a in re.findall(r"\b(20\d\d|19\d\d)[;.]", refs)]
rec = sum(1 for a in años if a >= 2021)
print(f"{src_path.name}:  cuerpo {pal(cuerpo)}  |  resumen {pal(res_es)}  |  abstract {pal(res_en)}  "
      f"|  tablas+figuras {3+n_fig}  |  refs {len(re.findall(chr(10)+r'[0-9]+[.] ', refs))} "
      f"({100*rec/max(len(años),1):.1f} % recientes)")

try:
    subprocess.run([sys.executable, str(NM / "ACE/md2pdf.py"), str(tmp), str(out_pdf)],
                   capture_output=True, text=True, timeout=280)
except subprocess.TimeoutExpired:
    pass
if out_pdf.exists():
    print(f"  -> {out_pdf.name}  ({out_pdf.stat().st_size/1024:.0f} kB)")
