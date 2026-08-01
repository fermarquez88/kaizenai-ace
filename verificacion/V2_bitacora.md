# Bloque V2 — Reproducción independiente del análisis principal

> Ejecutado 2026-07-31. Script: `codigo/V2_reproduccion_independiente.py`.
> Salidas: `resultados/V2_reproduccion.json`, `resultados/V2b_testretest.json`,
> `resultados/V2b_testretest_por_intervalo.json`, log completo en `V2_salida.log`.

**Criterio del bloque:** recalcular todo desde los datasets corregidos en V1b, sin tomar ninguna
cifra de corridas anteriores. **Estas cifras reemplazan a todas las previas.** Ninguna cifra
anterior al 2026-07-31 debe usarse en el manuscrito.

Bases: **comunitaria n=758**, **clínica n=2112** (total **2870**).

---

## A. Las dos cohortes tienen selección opuesta, como requiere el diseño

| | Comunitaria | Clínica |
|---|---|---|
| n | 758 | 2112 |
| Mujeres | 81,0 % | 59,1 % |
| Edad, mediana [Q1–Q3] | 63 [57–69] | 73 [66–78] |
| Educación, mediana [Q1–Q3] | 10 [7–15] | 12 [8–16] |
| <7 / 7–11 / ≥12 años | 159 / 249 / 350 | 184 / 606 / 1322 |
| ACE-III, media (DE) | 77,6 (13,3) | 71,4 (18,7) |
| ACE-III ≤40 | 1,6 % | 7,5 % |

La clínica es 10 años mayor, rinde 6 puntos menos y tiene 5 veces más deterioro grave. Que un
resultado se repita en las dos es informativo justamente por eso.

## B. Análisis principal — el escalón de 12 años no existe

**Indicador de discontinuidad**, ajustado por edad, sexo y la forma continua de la educación
(HC3):

| Cohorte | Escalón | IC 95 % | p |
|---|---|---|---|
| Comunitaria | **+0,04** (EE 1,35) | −2,61 a +2,69 | 0,975 |
| Clínica | **+0,13** (EE 1,38) | −2,56 a +2,83 | 0,924 |

**Prueba de equivalencia** (lo que convierte "no encontramos" en "no está"):

| | Comunitaria | Clínica |
|---|---|---|
| Se descarta un escalón ≥18 puntos | p = 1,3×10⁻⁴⁰ | p = 7,4×10⁻³⁹ |
| Se descarta un escalón ≥5 puntos | p = 0,0001 | p = 0,0002 |

Esto es lo central: no es ausencia de evidencia, es **evidencia de ausencia**. El intervalo de
confianza excluye incluso un escalón clínicamente trivial de 5 puntos, en las dos cohortes.

**Regresión discontinua local** — seis ventanas, ningún resultado significativo, y los signos se
contradicen entre cohortes (positivo en la comunitaria, negativo en la clínica):

| Ventana | Comunitaria | Clínica |
|---|---|---|
| 10–13 años | +1,31 [−4,90; +7,52] | −2,50 [−8,67; +3,66] |
| 9–14 años | +1,95 [−2,41; +6,32] | −3,52 [−8,07; +1,03] |
| 8–15 años | +1,54 [−1,96; +5,05] | −0,57 [−4,05; +2,90] |

**Diferencia cruda 11 vs 12 años:** +3,29 [−0,39; +6,98] comunitaria (n=16 vs 112) y +1,82
[−2,32; +5,97] clínica (n=70 vs 447). Aun sin ajustar por nada, la diferencia observada es una
fracción del salto de 18 puntos que la regla impone.

## C. La forma sí existe, y replica con precisión inusual

| | Comunitaria (n=758) | Clínica (n=2112) |
|---|---|---|
| Curvatura b₂ | **−0,0784** [−0,1037; −0,0531] | **−0,0784** [−0,1057; −0,0512] |
| p | 1,3×10⁻⁹ | 1,7×10⁻⁸ |
| Cuadrático mejor que lineal | p = 2,7×10⁻¹¹ | p = 3,8×10⁻⁸ |
| Spline mejor que cuadrático | p = 1,000 | p = 0,329 |

Las dos curvaturas coinciden **hasta el cuarto decimal**. El contraste formal entre cohortes es
+0,0064 [−0,0307; +0,0435], p = 0,735; la prueba de replicación de la curvatura da p = 0,764.
Dos cohortes con selección opuesta y 10 años de diferencia de edad producen la misma curva.

**Pendiente marginal** (puntos de ACE-III por año de educación), comunitaria: 2,92 a los 3 años ·
2,30 a los 7 · 1,51 a los 12 · **0,73 a los 17**. Clínica: 3,31 · 2,68 · 1,90 · 1,11.
El primer año de escolaridad vale unas **4 veces** lo que el año 17.

El spline natural no mejora al cuadrático en ninguna cohorte: la curva es suave, no tiene codos
ni umbrales. **La educación entra al ACE-III de forma continua y con rendimientos decrecientes.**

## D. Consecuencia de aplicar la regla vigente

Positividad año por año. El corte cambia de 68 a 86 entre los 11 y los 12 años de escolaridad:

| | 11 años | 12 años | Razón |
|---|---|---|---|
| Comunitaria | 6,2 % (1/16) | 52,7 % (59/112) | **8,4×** |
| Clínica | 42,9 % (30/70) | 81,2 % (363/447) | 1,9× |

Por tramo educativo, comunitaria: 56,0 % (<7) · **20,5 %** (7–11) · 40,3 % (≥12). Clínica:
74,5 % · 55,3 % · 61,9 %. En las dos cohortes el tramo 7–11 es el **menos** señalado, pese a ser
el de menor reserva cognitiva: la regla invierte el gradiente de riesgo que pretende corregir.

> No son sensibilidad ni especificidad. No hay estándar de referencia diagnóstico (ver `README.md`).
> Es la proporción de personas que la regla señala como positivas.

## E. Variabilidad test-retest — cuánto es 18 puntos en unidades del instrumento

Subgrupo clínico con evaluaciones repetidas: **218 pares consecutivos de 191 personas**, intervalo
mediano 560 días [Q1–Q3 384–850].

| | valor |
|---|---|
| Correlación test-retest | r = 0,774 |
| Coeficiente de correlación intraclase | 0,727 |
| Cambio medio | −4,22 puntos (DE 11,81) |
| Error estándar de medición (crudo) | 8,35 puntos |
| Cambio mínimo detectable (95 %) | ±23,1 puntos |

**El intervalo largo mezcla error de medición con deterioro real.** En una cohorte con enfermedad
progresiva, el cambio observado a 2 años no es ruido. Se verificó el gradiente esperado:

| Intervalo | n | Cambio medio | DE del cambio | EEM |
|---|---|---|---|---|
| ≤180 días | 11 | +4,64 | 22,53 | 15,93 |
| 181–365 | 37 | −2,00 | 8,72 | **6,17** |
| 366–730 | 97 | −4,46 | 10,53 | 7,45 |
| >730 | 73 | −6,37 | 12,02 | 8,50 |

El gradiente monótono a partir de los 181 días es exactamente lo que predice la suma
"error de medición + deterioro acumulado". El tramo ≤180 días es un artefacto de selección: son
11 reevaluaciones clínicamente motivadas, con dos valores extremos (+61 y +29); sin ellos la DE
baja de 22,5 a 13,3.

Descomposición formal de la varianza — `Var(cambio a t años) = 2·EEM² + t·varianza de la tasa`,
extrapolando a intervalo cero (bootstrap 4000 réplicas):

- **EEM = 8,15 puntos, IC 95 % [1,93; 12,21]** — el intervalo es ancho y así debe declararse
- desviación de la tasa de cambio verdadera = 3,63 puntos/año
- fiabilidad = 0,695

**Lo robusto, que no depende del método de estimación** (EEM entre 6,2 y 8,4 según se estime):

| Cantidad | En unidades de EEM |
|---|---|
| El escalón que impone la regla (18 puntos) | **≈ 2,2** |
| La diferencia cruda observada 11 vs 12 años (+3,29) | ≈ 0,4 |
| El escalón estimado tras ajustar (+0,04) | ≈ 0,005 |

La regla impone entre dos evaluaciones un salto mayor que el error de medición del propio
instrumento, para corregir una diferencia real que es una fracción de ese error.

### Limitación a declarar
El test-retest proviene **sólo de la cohorte clínica** (la comunitaria no tiene reevaluaciones: 0
personas en ambas olas), el intervalo no fue protocolizado, y los 191 sujetos son un subgrupo
seleccionado por seguimiento clínico. La estimación sirve para dar **escala** al escalón de 18
puntos, no como norma de fiabilidad del ACE-III en español.

## F. Sensibilidades de la curvatura

| Especificación | Comunitaria | Clínica |
|---|---|---|
| Principal | −0,0784 (n=758) | −0,0784 (n=2112) |
| Sin armonizar el reconocimiento | −0,0740 | — |
| Columna de total del instrumento | −0,0707 | — |
| Ajustando por ola | −0,0819 | — |
| Excluyendo techo (<95) | −0,0818 (n=726) | −0,0854 (n=2018) |
| Edad restringida 46–85 | −0,0784 | −0,0745 (n=2027) |
| Educación ≤18 años | −0,0710 (n=728) | −0,0583 (n=1992) |
| Sólo ítems validados | — | −0,0707 (n=2018) |

Rango −0,058 a −0,085; el signo y el orden de magnitud no dependen de ninguna decisión analítica.
Breusch-Pagan p = 2,2×10⁻¹⁴ → la varianza no es constante y el uso de errores robustos HC3 en
todo el estudio queda justificado empíricamente.

---

## Veredicto del bloque

**El análisis principal reproduce íntegramente sobre los datos corregidos.** Respecto de las
corridas previas a V1b, las cifras cambian en el tercer decimal salvo el escalón comunitario
(+0,55 → **+0,04**), que se acerca aún más a cero. La curvatura de la cohorte comunitaria pasó de
−0,0835 a −0,0784, con lo que las dos cohortes ahora coinciden hasta el cuarto decimal.

Un defecto de procedimiento hallado y corregido en este bloque: el archivo longitudinal se leía con
`dayfirst=True` sobre fechas ISO, lo que invertía día y mes y reducía los pares utilizables de 218
a 33. Corregido a `format="ISO8601"`. **Es el mismo defecto ya documentado en V1**; queda como
regla del estudio.

## Regla que queda establecida para el estudio

> Las fechas se leen siempre con `format="ISO8601"` en los archivos derivados (v2 y posteriores) y
> con `dayfirst=True` **sólo** en las fuentes v1 con fecha en formato argentino. Nunca se aplica
> `dayfirst` a una fecha ISO.

## Pendiente que este bloque deja abierto

Todos los entregables (`entregable_can/`) todavía contienen cifras anteriores a V1b. Se actualizan
después de V5, no antes, para no reescribirlos dos veces.
