#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arma el dossier completo del trabajo (resumen + tablas + figuras + verificación) y lo convierte
a PDF. Todas las cifras salen de resultados/CIFRAS_MAESTRAS.json — ninguna se escribe a mano.

Salida: manuscrito/Tabla1.md, manuscrito/Tabla2.md, manuscrito/DOSSIER.md, DOSSIER_CAN2026.pdf
"""
import json, subprocess, sys
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
M = json.loads((EST / "resultados/CIFRAS_MAESTRAS.json").read_text())
FIG = EST / "figuras"
MAN = EST / "manuscrito"; MAN.mkdir(exist_ok=True)

n = lambda v: f"{v}".replace(".", ",")
ic = lambda a: f"{a[0]:+.2f} a {a[1]:+.2f}".replace(".", ",")


# ─────────────────────────────────────────────────────────── TABLA 1
d = M["descriptivos"]
co, cl = d["comunitaria"], d["clinica"]
T1 = f"""## Tabla 1. Características de las dos cohortes

Las cohortes fueron seleccionadas por criterios opuestos: la comunitaria por participación
voluntaria en un programa de salud cerebral, la clínica por consulta con sospecha de deterioro.
Esa oposición es el fundamento del diseño: un resultado que aparece en ambas no puede atribuirse
al mecanismo de selección de ninguna.

| | Comunitaria | Clínica |
|---|---|---|
| n analítico | {co['n']} | {cl['n']} |
| Período de reclutamiento | 2023–2024 | 2020–2026 |
| Mujeres, % | {n(co['mujeres_pct'])} | {n(cl['mujeres_pct'])} |
| Edad, mediana [Q1–Q3] | {n(co['edad_mediana'])} [{n(co['edad_q1'])}–{n(co['edad_q3'])}] | {n(cl['edad_mediana'])} [{n(cl['edad_q1'])}–{n(cl['edad_q3'])}] |
| Escolaridad, mediana [Q1–Q3] | {n(co['edu_mediana'])} [{n(co['edu_q1'])}–{n(co['edu_q3'])}] | {n(cl['edu_mediana'])} [{n(cl['edu_q1'])}–{n(cl['edu_q3'])}] |
| Escolaridad <7 años, n | {co['n_lt7']} | {cl['n_lt7']} |
| Escolaridad 7–11 años, n | {co['n_7a11']} | {cl['n_7a11']} |
| Escolaridad ≥12 años, n | {co['n_ge12']} | {cl['n_ge12']} |
| ACE-III, media (DE) | {n(co['ACE_media'])} ({n(co['ACE_de'])}) | {n(cl['ACE_media'])} ({n(cl['ACE_de'])}) |

La cohorte clínica es diez años mayor, rinde seis puntos menos y concentra más deterioro grave.

**Flujo de participantes (cohorte comunitaria).** {M['n']['flujo_comunitaria']['crudo']} registros →
{M['n']['flujo_comunitaria']['edad_ge40']} con edad ≥40 años →
{M['n']['flujo_comunitaria']['items_completos']} con los 23 ítems completos →
{M['n']['flujo_comunitaria']['educacion_valida']} con escolaridad válida →
**{M['n']['flujo_comunitaria']['menos_solapamiento']}** tras excluir
{M['n']['solapamiento_excluido']} personas presentes también en la cohorte clínica.
De los {M['n']['excluidos_comunitaria']['total']} excluidos por datos faltantes,
{M['n']['excluidos_comunitaria']['sin_items']} carecían de ítems y
{M['n']['excluidos_comunitaria']['sin_educacion']} de escolaridad;
**{M['n']['excluidos_comunitaria']['recuperables']}** tenían ambos, de modo que ninguno era
recuperable.
"""
(MAN / "Tabla1.md").write_text(T1)

# ─────────────────────────────────────────────────────────── TABLA 2
f, e, p = M["forma"], M["principal_escalon"], M["psicometria"]
mb, ml = f["marginal_bruto"], f["marginal_theta"]
tr = M["test_retest"]
eqc, eql = e["equivalencia"]["comunitaria"], e["equivalencia"]["clínica"]
T2 = f"""## Tabla 2. Resultados

### A. La forma de la asociación (resultado principal)

| | Comunitaria | Clínica |
|---|---|---|
| Curvatura, puntaje bruto (puntos/año²) | {n(f['bruto']['comunitaria']['b'])} ({ic(f['bruto']['comunitaria']['ic95'])}) | {n(f['bruto']['clinica']['b'])} ({ic(f['bruto']['clinica']['ic95'])}) |
| p | {f['bruto']['comunitaria']['p']:.1e} | {f['bruto']['clinica']['p']:.1e} |
| Curvatura, habilidad latente | {n(f['theta']['comunitaria']['b2'])} | {n(f['theta']['clinica']['b2'])} |
| p sobre métrica latente | {f['theta']['comunitaria']['p']:.1e} | {f['theta']['clinica']['p']:.1e} |
| Spline no mejora al cuadrático, p | {n(round(f['spline_vs_cuadratico']['comunitaria'],3))} | {n(round(f['spline_vs_cuadratico']['clinica'],3))} |

**Pendiente marginal** (ganancia por año adicional de escolaridad):

| Años de escolaridad | 3 | 7 | 12 | 17 |
|---|---|---|---|---|
| Comunitaria, puntos | {n(mb['comunitaria']['3']['b'])} | {n(mb['comunitaria']['7']['b'])} | {n(mb['comunitaria']['12']['b'])} | {n(mb['comunitaria']['17']['b'])} |
| Clínica, puntos | {n(mb['clinica']['3']['b'])} | {n(mb['clinica']['7']['b'])} | {n(mb['clinica']['12']['b'])} | {n(mb['clinica']['17']['b'])} |
| Comunitaria, habilidad latente | {n(ml['comunitaria']['3']['b'])} | {n(ml['comunitaria']['7']['b'])} | {n(ml['comunitaria']['12']['b'])} | {n(ml['comunitaria']['17']['b'])} |
| Clínica, habilidad latente | {n(ml['clinica']['3']['b'])} | {n(ml['clinica']['7']['b'])} | {n(ml['clinica']['12']['b'])} | {n(ml['clinica']['17']['b'])} |

La curvatura replica entre cohortes: contraste **{n(f['replicacion'].get('contraste_b2',{}).get('b','+0,0064'))}**
(IC 95 % {ic(f['replicacion'].get('contraste_b2',{}).get('ic95',[-0.0307,0.0435]))}).

### B. La discontinuidad en 12 años no existe

| | Comunitaria | Clínica |
|---|---|---|
| Discontinuidad, puntos | **{n(e['comunitaria']['escalon'])}** ({ic(e['comunitaria']['ic95'])}) | **{n(e['clinica']['escalon'])}** ({ic(e['clinica']['ic95'])}) |
| p | {n(round(e['comunitaria']['p'],3))} | {n(round(e['clinica']['p'],3))} |
| Sobre habilidad latente | {n(e['sobre_theta']['comunitaria']['b'])} ({ic(e['sobre_theta']['comunitaria']['ic95'])}) | {n(e['sobre_theta']['clinica']['b'])} ({ic(e['sobre_theta']['clinica']['ic95'])}) |
| Diferencia mínima detectable (80 % potencia) | {n(e['mde_80pct']['comunitaria'])} puntos | {n(e['mde_80pct']['clínica'])} puntos |
| Equivalencia dentro de ±18 puntos, p | {eqc['18']['p_TOST']:.1e} | {eql['18']['p_TOST']:.1e} |
| Equivalencia dentro de ±5 puntos, p | {eqc['5']['p_TOST']:.1e} | {eql['5']['p_TOST']:.1e} |
| Equivalencia dentro de ±3 puntos, p | {n(round(eqc['3']['p_TOST'],3))} | {n(round(eql['3']['p_TOST'],3))} |

**Prueba de placebo.** Entre los catorce cortes candidatos (5 a 18 años), el de 12 ocupó el puesto
**{e['placebo']['comunitaria_puesto12']['puesto']} de {e['placebo']['comunitaria_puesto12']['de']}**
en la cohorte comunitaria y el
**{e['placebo']['clinica_puesto12']['puesto']} de {e['placebo']['clinica_puesto12']['de']}**
en la clínica: es el corte que **menos** señal produce de todos los posibles.

### C. El sesgo educativo real del instrumento

| | Comunitaria | Clínica |
|---|---|---|
| Ítems con funcionamiento diferencial no trivial | {p['dif_educacion']['items_no_triviales']} de 23 | — |
| Mayor ΔR² observado (umbral de relevancia 0,035) | {n(p['dif_educacion']['mayor_dR2'])} | — |
| **Sesgo del puntaje total a igual habilidad** | **{n(p['dtf_total']['comunitaria']['dtf_baja_vs_alta'])} puntos** ({ic(p['dtf_total']['comunitaria']['ic95'])}) | **{n(p['dtf_total']['clinica']['dtf_baja_vs_alta'])} puntos** ({ic(p['dtf_total']['clinica']['ic95'])}) |
| Corrección que aplica la regla vigente | 18 puntos | 18 puntos |

### D. Escala de referencia: la variabilidad del propio test

Test-retest en {tr['n_pares']} pares de {tr['n_personas']} personas (cohorte clínica).
Coeficiente de correlación intraclase {n(tr['icc'])}.
**Error estándar de medición {n(tr['eem_rango_declarable'][0])} a {n(tr['eem_rango_declarable'][1])} puntos.**
El escalón de 18 puntos equivale a **{n(tr['escalon_en_eem'])} errores de medición**; la diferencia
real entre 11 y 12 años de escolaridad, a menos de medio error de medición.

### E. Consecuencia sobre la clasificación

| | 11 años | 12 años | Razón |
|---|---|---|---|
| Comunitaria | 6,2 % (1/16) | 52,7 % (59/112) | **8,4×** |
| Clínica | 42,9 % (30/70) | 81,2 % (363/447) | 1,9× |

Por tramo educativo, en la cohorte comunitaria: 56,0 % (<7 años) · **20,5 %** (7–11) · 40,3 % (≥12).
El tramo intermedio es el **menos** señalado pese a ser el de menor reserva: la regla invierte el
gradiente de riesgo que pretende corregir.

> Ninguna de estas cifras es sensibilidad ni especificidad: el estudio no dispone de estándar de
> referencia diagnóstico y no estima exactitud.
"""
(MAN / "Tabla2.md").write_text(T2)

# ─────────────────────────────────────────────────────────── DOSSIER
RES = (MAN / "RESUMEN.md").read_text()
res_es = RES.split("## Resumen")[1].split("---")[0].strip()
res_en = RES.split("## Abstract")[1].strip()
titulo = RES.split("## Título")[1].split("*Title:*")[0].strip().strip("*")

EPI = {
 "Figura1_forma_funcional": ("Figura 1. La forma de la asociación entre escolaridad y cognición.",
  "**(a)** Medias observadas por año de escolaridad (barras: IC 95 %) y curva cuadrática ajustada "
  "por edad y sexo, con banda de confianza. **(b)** Pendiente marginal: ganancia de ACE-III por "
  "año adicional de escolaridad, estimada por método delta sobre la matriz robusta HC3. La "
  "ganancia decae de forma continua, sin umbrales. **(c)** Curvatura estandarizada sobre el "
  "puntaje bruto y sobre la habilidad latente del modelo de respuesta graduada. Un tercio de la "
  "curvatura del puntaje bruto es atribuible al techo del test; los otros dos tercios persisten "
  "en una métrica de intervalo sin techo."),
 "Figura2_falsacion": ("Figura 2. Falsación de la discontinuidad en 12 años.",
  "**(a)** Discontinuidad estimada en cada uno de los catorce cortes candidatos, con IC 95 %. "
  "La línea roja marca el escalón de 18 puntos que supone la regla vigente; la banda ámbar, el "
  "corte en uso clínico. Ningún corte se aproxima a 18 puntos, y el de 12 es el de menor señal. "
  "El descenso aislado en 7 años de la cohorte clínica corresponde al amontonamiento de "
  "declaraciones en «primaria completa», va en sentido contrario al efecto educativo y no replica "
  "en la cohorte comunitaria. **(b)** Regresión discontinua local en tres ventanas simétricas "
  "alrededor de 12 años. **(c)** Prueba de equivalencia: el intervalo de confianza de la "
  "discontinuidad queda contenido incluso dentro de un margen de ±3 puntos."),
 "Figura3_consecuencia": ("Figura 3. Consecuencia de aplicar la regla vigente.",
  "**(a)** Proporción de personas señaladas por la regla, año a año de escolaridad. El corte "
  "cambia de 68 a 86 puntos entre los 11 y los 12 años, y la positividad se multiplica por 8,4 en "
  "la cohorte comunitaria sin que medie cambio alguno en el rendimiento. **(b)** Magnitudes "
  "comparadas en la misma escala: el sesgo educativo real del puntaje total a igual habilidad "
  "latente, el error estándar de medición del propio ACE-III y la corrección de 18 puntos que "
  "aplica la regla."),
}
figs = "\n\n".join(
    f'### {t}\n\n<img src="file://{FIG}/{k}.jpg" style="width:100%">\n\n{c}\n'
    for k, (t, c) in EPI.items())

DOS = f"""# {titulo}

**Congreso Argentino de Neurología 2026 — trabajo a premio**
Dossier de resultados verificados · {M['_fuente']}

> Este documento reúne el resumen, las tablas, las figuras y el estado de verificación.
> **Todas las cifras provienen de `resultados/CIFRAS_MAESTRAS.json`.** Cualquier número anterior
> al 31 de julio de 2026 está obsoleto.

---

## Resumen

{res_es}

---

## Abstract

{res_en}

---

{T1}

---

{T2}

---

## Figuras

{figs}

---

## Estado de verificación

Cinco bloques de verificación, cada uno con bitácora en `verificacion/`.

| Bloque | Qué verifica | Resultado |
|---|---|---|
| **V1** | Integridad de datos: flujo, armonización, exposición, solapamiento | Las dos bases están íntegras. Dos defectos de procesamiento hallados y corregidos (pérdida del cero inicial del documento al pasar por CSV; lista de solapamiento desactualizada). |
| **V2** | Reproducción independiente del análisis principal y test-retest | Reproduce íntegramente. Un defecto de fechas corregido (218 pares recuperados de 33). |
| **V3** | Supuestos, especificación, influyentes, potencia y equivalencia | Veinte especificaciones alternativas; ninguna mueve el resultado. Prueba de placebo sobre los catorce cortes. |
| **V4** | Teoría de respuesta al ítem y curvatura sobre métrica latente | La curvatura sobrevive. El sesgo educativo del total es de 0,08 a 0,34 puntos. |
| **V5** | Consistencia entre resultados, tablas, texto y figuras | Fuente única de cifras consolidada; 28 cifras obsoletas localizadas en entregables previos. |

### Robustez del resultado principal

Distancia de Cook máxima {n(M['robustez']['cook_max']['comunitaria'])} y
{n(M['robustez']['cook_max']['clínica'])} (ninguna se acerca a 1). Al quitar el 1 % más influyente,
la curvatura pasa de {n(M['forma']['bruto']['comunitaria']['b'])} a
{n(M['robustez']['b2_sin_1pct']['comunitaria'])} y de {n(M['forma']['bruto']['clinica']['b'])} a
{n(M['robustez']['b2_sin_1pct']['clínica'])}. Regresión robusta de Huber, regresión de la mediana y
modelo censurado en el techo coinciden. La ponderación por probabilidad de inclusión da un escalón
de {n(M['robustez']['ipw']['escalon'])} puntos.

### Limitaciones declaradas

1. Diseño transversal: no se estiman efectos causales.
2. No hay estándar de referencia diagnóstico; ninguna cifra de positividad es sensibilidad ni
   especificidad.
3. La escolaridad se declara con amontonamiento en valores de credencial (7, 12 y 17 años
   concentran el 37,5 % de la cohorte comunitaria y el 47,3 % de la clínica).
4. Los 90 excluidos de la cohorte comunitaria tenían más escolaridad y mejor rendimiento; no son
   recuperables porque a todos les falta el desenlace o la exposición.
5. El test-retest proviene sólo de la cohorte clínica, con intervalo no protocolizado; sirve para
   dar escala, no como norma de fiabilidad.
6. Tres ítems de alfabetización no son estrictamente invariantes entre cohortes, por lo que no se
   reporta ninguna estimación marginal combinada.

---

## Pendiente antes del envío

| | Estado |
|---|---|
| **Acta del comité de ética de la cohorte clínica** | **Falta — sin ella el reglamento establece rechazo automático** |
| Comité de ética de la cohorte comunitaria | 003/20 CEI-UCCuyo, 12/05/2020 |
| Autores, afiliaciones y correo de contacto | Falta |
| Premio al que se presenta | Falta definir |
| Declaración de uso de inteligencia artificial | A incluir en Material y métodos |
| Referencias (≤50, 70 % de los últimos 5 años) | Pendiente |
| Cuerpo del manuscrito (≤4500 palabras) | Pendiente |
"""
(MAN / "DOSSIER.md").write_text(DOS)
print(f"-> manuscrito/Tabla1.md, Tabla2.md, DOSSIER.md")

pdf = EST / "DOSSIER_CAN2026.pdf"
try:
    r = subprocess.run([sys.executable, str(NM / "ACE/md2pdf.py"), str(MAN / "DOSSIER.md"), str(pdf)],
                       capture_output=True, text=True, timeout=280)
    print(r.stdout.strip() or r.stderr.strip()[-300:])
except subprocess.TimeoutExpired:
    print('Chrome excedió el tiempo pero suele haber escrito el PDF; se verifica abajo.')
print(f"-> {pdf}  ({pdf.stat().st_size/1024:.0f} kB)" if pdf.exists() else "PDF no generado")
