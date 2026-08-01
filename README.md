# kaizenai-ace

**Escolaridad y ACE-III en dos cohortes de San Juan, Argentina.**
Código, resultados, figuras, manuscrito y calculadora del estudio.

### → [Calculadora en línea](https://fermarquez88.github.io/kaizenai-ace/)

Rendimiento esperado en el ACE-III según años de escolaridad y edad, con tabla de referencia y
simulador de cohortes. **Valores ilustrativos: no son normas poblacionales y no deben usarse para
decidir sobre un paciente.**

---

## El problema

En Argentina el Addenbrooke's Cognitive Examination III se interpreta con **dos puntos de corte según
la escolaridad: 86 para quienes tienen 12 años o más, 68 para quienes tienen menos**. La regla supone
que el rendimiento da un salto de 18 puntos al cruzar los 12 años de escuela.

Este trabajo pregunta tres cosas, en dos cohortes independientes con selección opuesta:

1. **¿Existe ese salto?** ¿La escolaridad se asocia al ACE-III de forma discontinua a los 12 años, o
   de forma continua?
2. **¿De dónde salió la regla?** Reconstrucción documental de la procedencia de cada corte y del
   umbral que los separa.
3. **¿Qué consecuencia tiene aplicarla?** Sobre quién recae el señalamiento y sobre quién no.

## Las cohortes

| | Comunitaria | Clínica |
|---|---|---|
| Origen | Programa Neuromentia, olas 2023–2024 | Instituto de Neurociencias de San Juan |
| Selección | tamizaje comunitario | consulta por queja cognitiva |
| n analítico | 758 | 2112 |
| Edad, mediana (Q1–Q3) | 63 (57–69) | 73 (66–78) |
| Escolaridad, mediana (Q1–Q3) | 10 (7–15) | 12 (8–16) |
| ACE-III, media (DE) | 77,6 (13,3) | 71,4 (18,7) |
| Mujeres | 81,0 % | 59,1 % |

Los 18 participantes presentes en ambas bases se excluyeron de la comunitaria.

## Qué hay acá

```
codigo/          los scripts, numerados por orden de ejecución
  07–32          construcción de los datasets analíticos y análisis principal
  V1–V13         bloques de verificación independiente
  F1–F7          figuras, tablas, entregables y armado de la calculadora
resultados/      salidas numéricas en JSON, agregadas
verificacion/    bitácoras de cada bloque de verificación
figuras/         figuras del manuscrito y del material para el equipo (jpg + pdf)
tablas/          tablas de referencia en csv y markdown
manuscrito/      manuscrito, suplementario, auditorías y versiones anteriores
entregable_can/  paquete del resumen para el congreso
calculadora/     fuente de la calculadora
docs/            la calculadora publicada en GitHub Pages
datos/           vacío por diseño — ver datos/README.md
```

### Cadena de análisis

```
   BASE CLÍNICA                              BASE COMUNITARIA
        │                                            │
  19_build_definitivo.py                             │
   ítems, totales y educación desde el informe       │
        │                                            │
  20_dx_desde_conclusiones.py                        │
   perfil cognitivo desde el texto libre             │
        │                                            │
        └──────────────┬─────────────────────────────┘
                       │
            V1b_fix_dni_y_solape.py
             normaliza documentos y recalcula el solapamiento
                       │
            30_analisis_armonizado.py
             forma funcional, replicación, sensibilidades
                       │
            31_falsacion_escalon.py          ← análisis principal
                       │
            V13_equidad_corregida.py         ← comparación de reglas
```

Los scripts `07`–`18` documentan la auditoría de calidad de datos: cómo se detectaron los defectos.
Se conservan por trazabilidad y no forman parte de la cadena vigente.

### Verificación

Cada bloque `V` reejecuta una parte del análisis de forma independiente y deja bitácora en
[`verificacion/`](verificacion/):

| | Qué verifica |
|---|---|
| V1 · V1b | Integridad de los datos, flujo de participantes, solapamiento entre bases |
| V2 | Reproducción del análisis principal desde cero, y test-retest |
| V3 | Supuestos, especificación, casos influyentes, equivalencia y test de placebo |
| V4 | Teoría de respuesta al ítem, funcionamiento diferencial y curvatura sobre la métrica latente |
| V5 | Consistencia entre JSON, tablas, texto y figuras |
| V6 | Seis controles sobre la etiqueta diagnóstica extraída de texto libre |
| V7 | Estándar de referencia y cortes empíricos exploratorios |
| V8 · V12 · V13 | Modelo normativo continuo y comparación entre reglas |

Las objeciones de las dos auditorías externas —perspectiva *Neurology* y perspectiva *Alzheimer's &
Dementia*— y la corrección aplicada a cada una están en
[`manuscrito/REGISTRO_CORRECCIONES.md`](manuscrito/REGISTRO_CORRECCIONES.md).

## Reproducir

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python codigo/V2_reproduccion_independiente.py
```

Los scripts requieren los datos individuales, que **no se distribuyen** — ver
[`datos/README.md`](datos/README.md). Lo que sí puede reproducirse sin ellos es la función normativa,
a partir de los coeficientes publicados en
[`resultados/CALC_coeficientes.json`](resultados/CALC_coeficientes.json):

```
esperado = 59,094931 + 1,078577·[mujer] + 3,316084·escolaridad
           − 0,078103·escolaridad² − 0,087546·edad

log(σ²)  = 3,311962 − 0,080615·escolaridad + 0,008199·edad
```

Estimados sobre 663 participantes comunitarios con memoria de reconocimiento en rango normal —un
criterio independiente del ACE-III y sin gradiente educativo—. Es el mismo modelo que corre en la
calculadora.

## Alcance

**No hay estándar de referencia diagnóstico.** No se estima exactitud diagnóstica y ninguna cifra de
positividad es sensibilidad ni especificidad. Lo que el estudio establece es una incoherencia interna
de la regla vigente, de magnitud medible. Evidencia de Clase IV para el objetivo de comparación de
reglas.

## Datos y ética

Los datos individuales incluyen documento de identidad, fechas de evaluación y texto libre de
conclusiones clínicas, y **no se publican en ningún caso**. El directorio `datos/` está excluido del
control de versiones. Las solicitudes de acceso, seudonimizado y bajo acuerdo de uso, requieren aval
del comité de ética que aprobó el estudio.

## Autores

Márquez, Fernando<sup>¹,²,³</sup>; Arellano, Paula Virginia<sup>²,⁴</sup>; Bruno, Diana<sup>¹,²</sup>; Vita, Luciana<sup>²,⁴</sup>; Bistué, María Beatriz<sup>²,⁴</sup>; Moyano, María Celeste<sup>²,⁴</sup>; Noguera Roberto, María Laura<sup>²</sup>; Zanino, Mariana<sup>²,⁴</sup>; Posleman, Cristian Ignacio<sup>²,⁴</sup>; Jácome, Iara<sup>¹,²</sup>; Portillo, Florencia<sup>²,⁴</sup>; Lucato, Daniel<sup>³</sup>; Bruno, Martín Alejandro<sup>²,⁴</sup>.

<sup>1</sup> Instituto de Neurociencias de San Juan · <sup>2</sup> Universidad Católica de Cuyo, San Juan, Argentina · <sup>3</sup> Hospital Dr. Guillermo Rawson ·
<sup>4</sup> Consejo Nacional de Investigaciones Científicas y Técnicas (CONICET)

## Licencia

Código bajo [MIT](LICENSE). Textos, figuras y tablas bajo
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).

## Aviso

Prototipo de investigación. La calculadora no diagnostica ni reemplaza la evaluación clínica, y sus
valores no constituyen normas poblacionales. Un puntaje por debajo del percentil 5 indica que ese
rendimiento es infrecuente en personas sin deterioro de la misma escolaridad y edad; nada más que eso.
