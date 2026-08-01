# Material suplementario

**La corrección por escolaridad del ACE-III en la Argentina.** Documentación completa de los doce
bloques de análisis y verificación. Todo el código está en `codigo/`, las salidas en `resultados/` y
las bitácoras detalladas en `verificacion/`.

> **Principio de trabajo.** Cada bloque se ejecutó sobre los datos originales, sin tomar cifras de
> corridas anteriores. Cuando un bloque detectó un defecto, se documentó, se corrigió y se
> reejecutaron todos los bloques dependientes. Tres hallazgos del propio proceso obligaron a
> modificar conclusiones ya escritas; se detallan más abajo.

---

## Índice de bloques

| Bloque | Pregunta | Script | Resultado |
|---|---|---|---|
| V1 | ¿Están íntegros los datos? | `V1_integridad_datos.py`, `V1b_fix_dni_y_solape.py` | Íntegros; 2 defectos de procesamiento corregidos |
| V2 | ¿Reproduce el análisis principal? | `V2_reproduccion_independiente.py` | Reproduce; 1 defecto de fechas corregido |
| V3 | ¿Dependen los resultados de supuestos? | `V3_supuestos_especificacion.py` | 20 especificaciones concordantes |
| V4 | ¿Es la curvatura un artefacto del techo? | `V4_tri_dif_metrica_latente.py` | Persiste el 66 % sobre métrica latente |
| V5 | ¿Son consistentes texto, tablas y figuras? | `V5_consistencia.py` | Fuente única de cifras consolidada |
| V6 | ¿Es válida la codificación diagnóstica? | `V6_verificacion_dx.py` | 90,9 % de cobertura, sin circularidad |
| V7 | ¿Qué dice el estándar de referencia? | `V7_estandar_referencia.py` | La regla vigente supera al corte único |
| V8 | ¿Mejora una corrección continua? | `V8_correccion_continua.py` | Sí, con controles funcionales |
| V9 | ¿Y con otros desenlaces? | (tres desenlaces) | El desenlace leve resultó no interpretable |
| V10 | ¿Se puede mejorar la definición de control? | (cinco definiciones) | Ninguna funcional resuelve el problema |
| V11 | ¿Sobrevive al emparejamiento por edad? | (emparejado + remuestreo) | El efecto se atenúa; hace falta mejor criterio |
| V12 | ¿Y con un criterio cognitivo ciego a la educación? | `V12_equidad_definitiva.py` | **Sí: razón 4,8 (IC 2,3–22,3)** |

---

## Los tres hallazgos que obligaron a cambiar conclusiones

**1. La curvatura era en parte un artefacto del techo (V4).** El análisis inicial sobre el puntaje
bruto daba una razón de cuatro veces entre la pendiente del año 3 y la del año 17. Al reestimar sobre
la habilidad latente del modelo de respuesta graduada, persistió el 66 % de la curvatura y la razón
cayó a dos veces. Se reporta la cifra latente, que es la conservadora.

**2. El desenlace de deterioro leve no era interpretable (V9–V10).** Los controles comunitarios con
menos de 7 años de escolaridad puntuaban 66,1, mientras los casos clínicos de deterioro leve del
mismo tramo puntuaban 67,9 —siendo 8,6 años mayores—. Dos lecturas competían: contaminación del
grupo control, o sobre-aplicación de la etiqueta clínica por efecto del propio corte. Al no poder
distinguirlas, el desenlace se eliminó del manuscrito.

**3. El efecto de equidad se atenuó al propagar la incertidumbre (V11).** La primera estimación daba
una reducción de once veces en el gradiente educativo. Con emparejamiento por edad e intervalos por
remuestreo, la razón cayó a 1,8 con intervalo que incluía la unidad. El hallazgo sólo se recuperó al
redefinir los controles con un criterio cognitivo ciego a la escolaridad (V12), donde la razón fue de
4,8 con intervalo que excluye la unidad.

---

## V1 — Integridad de datos

> Ejecutado 2026-07-31. Scripts: `codigo/V1_integridad_datos.py` y `codigo/V1b_fix_dni_y_solape.py`.
> Salidas: `resultados/V1_integridad.json`, `resultados/V1b_fix.json`.

**Criterio del bloque:** reconstruir cada dataset desde el archivo de origen y contrastarlo contra
lo que están usando los análisis. Todo lo que no reproduzca se reporta como discrepancia; nada se
ajusta en silencio.

---

## Lo que se verificó y reprodujo

| Chequeo | Resultado |
|---|---|
| Flujo de N de la cohorte comunitaria desde el XLSX crudo | 867 filas → 866 con edad ≥40 → **814** caso completo en los 23 ítems → **776** con educación válida ✓ |
| Ítems fuera de rango antes de corregir | 1 caso de `ACE_LLectura`=2 con máximo 1 → truncado, documentado ✓ |
| Educación implausible (>30 años) | 1 caso enmascarado ✓ |
| Regla de puntuación comunitaria del reconocimiento | "reconocimiento ≤ 7 − evocación" se cumple en el **100 %** de los casos ✓ |
| Convención de evocación perfecta | 38 casos, reconocimiento = 5 en el **100 %** ✓ |
| Efecto de la armonización | r con la evocación −0,180 → **+0,610**; r con el resto del test −0,138 → **+0,427** ✓ |
| Rango del ítem armonizado y del total | dentro de [0,5] y ≤100 ✓ |
| Independencia de observaciones en la clínica | 2242 filas = 2242 personas únicas ✓ |
| Suma de los 23 ítems == `ACE_total` en la clínica | 99,63 % — los 8 discordantes son **todos** `solo_total`, donde el total proviene del informe y no de los ítems, tal como define la regla de inclusión ✓ |
| Rangos del desenlace y la exposición en la clínica | ACE en [1,100], educación en [0,25], ningún ítem fuera de rango ✓ |

## Veredicto del bloque

**Las dos bases de datos están íntegras.** Todo lo verificable reprodujo: los flujos de N, los
rangos, la independencia de observaciones, la reconciliación entre suma de ítems y total, y la regla
de puntuación del reconocimiento. En las 626 filas que pudieron parearse de forma no ambigua, el
ACE-III y la educación fueron **idénticos** (diferencia máxima 0,0).

Los dos defectos hallados están en el **procesamiento**, no en los datos, y su efecto práctico es
acotado. Se documentan igual porque cambian el n final y porque establecen una regla para el resto
del estudio.

## Defecto 1 (de procesamiento) — El documento pierde el cero a la izquierda al pasar por CSV

**Detección.** Al parear el dataset comunitario guardado contra la reconstrucción desde el origen,
sólo **626 de 762** filas encontraron pareja por documento. Las 136 sin pareja eran exactamente las
136 con documento de 7 dígitos.

**Causa.** El documento se guardaba como texto conservando el cero inicial (`'0XXXXXXX'`), pero al
releer el CSV pandas infiere la columna como entero y lo pierde (`XXXXXXX`). El pareo entre
datasets, y con él la exclusión del solapamiento, fallaba para esos casos.

**Magnitud real.** El **18 %** de los documentos comunitarios tiene cero inicial (157 de 866).
Comparando la lista de solapamiento como texto se excluían 15 individuos; comparándola como entero,
17. **Efecto práctico: 2 personas que debían excluirse no se excluyeron.**

**Corrección.** El documento se normaliza a **entero canónico** en todas las fuentes: se eliminan
no-dígitos, se descartan longitudes fuera de 6–9 y se convierte a entero, con lo que el cero inicial
deja de existir en cualquier representación. Verificado con un ciclo completo de escritura y
lectura: 758/758 pareados, diferencia máxima 0,000000.

**Los valores en sí nunca estuvieron mal:** en las 626 filas comparables el ACE-III y la educación
eran idénticos (diferencia máxima 0,0). El defecto era de identificación, no de medición.

## Defecto 2 (de procedimiento) — La lista de solapamiento estaba desactualizada

**Detección.** La lista guardada tenía 17 individuos; contra los datasets definitivos se detectaban
14.

**Causa.** Se había calculado contra una versión anterior del dataset clínico (2137 personas). El
dataset definitivo (2242) cambió de composición al recuperarse casos por la regla de inclusión
declarada, de modo que la lista dejó de corresponder.

**Corrección.** Recalculado entre los datasets definitivos: **18 individuos** presentes en ambas
cohortes analíticas. Sólo 10 coincidían con la lista anterior; 8 son nuevos y 7 ya no aplican —
diferencia esperable, porque el dataset clínico definitivo recuperó casos que antes no existían.

**Verificación de que los 18 son la misma persona** (tres criterios independientes del documento,
contra la bóveda de identificación de la base clínica):

| Criterio | Corrobora |
|---|---|
| Edad compatible entre ambas evaluaciones (≤4 años de diferencia) | **18/18** |
| Apellido clínico contenido en el nombre comunitario | **17/18** |
| Sexo coincidente | **17/18** |
| Los tres criterios simultáneamente | **16/18** |

Los dos casos que fallan un criterio (uno el apellido, otro el sexo) tienen coincidencia exacta o
casi exacta de edad y el mismo documento; se interpretan como variantes de carga, no como falsos
pareos. Se excluyen igual, por criterio conservador.

**Consecuencia.** La cohorte comunitaria pasa de 776 a **758** (antes 762). Todos los análisis
posteriores se re-ejecutan sobre esta base.

## Efecto sobre los resultados

La corrección cambia el n de la cohorte comunitaria en 4 participantes. Los resultados se
re-ejecutan íntegramente en el bloque V2; **ninguna cifra publicada debe tomarse de una corrida
anterior a esta corrección.**

## Regla que queda establecida para el estudio

> El documento de identidad se normaliza siempre a entero canónico
> (`str → sólo dígitos → longitud 6–9 → entero`). Nunca se compara como texto entre datasets, y
> nunca se guarda de una forma que dependa de conservar ceros a la izquierda.


---

## V2 — Reproducción independiente

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


---

## V3 — Supuestos y especificación

> Ejecutado 2026-07-31. Scripts: `codigo/V3_supuestos_especificacion.py` (+ addendum).
> Salidas: `resultados/V3_supuestos.json`, `resultados/V3b_addendum.json`.

**Pregunta del bloque:** ¿alguno de los dos resultados —la ausencia de escalón y la curvatura—
depende de un supuesto que no se cumple, de una decisión de modelado, o de un puñado de sujetos?

**Respuesta: no.** Ninguna de las 20 especificaciones alternativas mueve el escalón lejos de cero ni
cambia el signo de la curvatura.

---

## A. Residuos y colinealidad

R² = 0,461 (comunitaria) y 0,305 (clínica). Los residuos tienen cola izquierda (asimetría −0,82 y
−1,32; Shapiro p<10⁻¹²), como corresponde a un test con techo. Breusch-Pagan p = 2,2×10⁻¹⁴ (V2).
Por eso todo el estudio usa **HC3**, que no supone normalidad ni varianza constante.

**El VIF alto del polinomio (14–21) es un artefacto de parametrización, no un problema.** Se
demostró empíricamente: el coeficiente principal de un polinomio es invariante a trasladar la
escala, y al centrar la educación b₂ y su error estándar son **idénticos hasta el sexto decimal**
(−0,078392, EE 0,012919 en las dos parametrizaciones). La inferencia sobre la curvatura no está
afectada por la correlación entre `edu` y `edu²`.

## B. Observaciones influyentes — el resultado no lo produce ningún subgrupo

| | Comunitaria | Clínica |
|---|---|---|
| Distancia de Cook máxima | 0,033 | 0,029 |
| Casos con Cook > 4/n | 51 (6,7 %) | 100 (4,7 %) |
| DFBETA(b₂) máximo | 0,309 | 0,306 |
| b₂ al quitar el 1 % más influyente | −0,0784 → −0,0724 | −0,0784 → −0,0626 |
| Escalón al quitar el 1 % más influyente | +0,04 → +0,79 | +0,13 → −0,03 |

Ningún Cook se acerca a 1. El resultado no depende de observaciones particulares.

## C. Especificación alternativa del desenlace

| | Comunitaria b₂ / escalón | Clínica b₂ / escalón |
|---|---|---|
| Mínimos cuadrados (principal) | −0,0784 / +0,04 | −0,0784 / +0,13 |
| Robusta de Huber | −0,0788 / +0,69 | −0,0867 / +0,53 |
| Regresión de la mediana | −0,0821 / +0,65 | −0,0888 / +0,16 |
| Normal censurada en el techo (100) | −0,0784 / +0,05 | −0,0779 / +0,13 |

El techo no distorsiona nada: sólo 0 y 2 personas alcanzan 100 puntos.

## D. Especificación alternativa de las covariables

Seis especificaciones (edad lineal, cuadrática, en spline; interacción educación×edad;
educación×sexo; sin covariables). **El escalón va de −0,41 a +0,48 en las 12 combinaciones**, con
intervalos que siempre contienen cero; b₂ va de −0,0742 a −0,0814.

## E. Falsación de placebo — el hallazgo más fuerte del bloque

Se estimó el escalón en **los 14 cortes candidatos** (5 a 18 años de escolaridad). Si el corte de
12 capturara algo real, debería destacarse entre los demás.

| Cohorte | Puesto del corte de 12 por magnitud del estadístico | p de permutación entre cortes |
|---|---|---|
| Comunitaria | **14 de 14** (el último) | 1,00 |
| Clínica | 12 de 14 | 0,86 |

**El corte que está en uso clínico es el que menos señal produce de todos los cortes posibles.**
Ninguno de los 14 sobrevive corrección de Bonferroni (α = 0,05/14 = 0,0036) salvo el de 7 años en
la clínica.

### El corte de 7 años: por qué no contradice el resultado
Único corte con señal (−6,4 puntos, p<0,001; robusto en cuatro ventanas de regresión discontinua
local: −6,72, −6,61, −5,43, −6,29). Se descarta como artefacto por tres razones:

1. **Va en sentido contrario.** Los de ≥7 años rinden *peor*, lo opuesto a un efecto educativo.
2. **No replica.** En la cohorte comunitaria el mismo contraste da +0,38 [−2,86; +3,62], p = 0,82.
3. **Es amontonamiento de credencial.** El 14,6 % de la cohorte clínica declara *exactamente* 7
   años ("primaria completa"); las medias crudas clínicas son 6a=62,1 · **7a=58,5** · 8a=60,6 —
   un pozo aislado en el valor de amontonamiento, ausente en la comunitaria (6a=71,1 · 7a=73,5 ·
   8a=74,3).

La educación se amontona en los tres valores de credencial (7, 12 y 17 años): **37,5 %** de la
cohorte comunitaria y **47,3 %** de la clínica declara uno de esos tres valores exactos. Esto se
declara como limitación de medición de la exposición.

> Lectura: el test de placebo es **sensible** —detecta un artefacto de amontonamiento cuando
> existe— y aun así en 12 años no encuentra nada.

## F. Potencia y equivalencia formal

| | Comunitaria | Clínica |
|---|---|---|
| Error estándar del escalón | 1,35 | 1,38 |
| Diferencia mínima detectable (80 % potencia) | **3,79 puntos** | **3,86 puntos** |
| Potencia para detectar un escalón de 18 puntos | >99,99 % | >99,99 % |
| Equivalencia dentro de ±18 puntos (TOST) | p = 1,3×10⁻⁴⁰ | p = 7,4×10⁻³⁹ |
| Equivalencia dentro de ±5 puntos | p = 1,2×10⁻⁴ | p = 2,0×10⁻⁴ |
| Equivalencia dentro de ±3 puntos | p = 0,014 | p = 0,019 |

El estudio tenía potencia para detectar un escalón cinco veces menor que el que la regla supone.
Con dos pruebas unilaterales se concluye equivalencia incluso dentro de un margen de ±3 puntos.

## G. Datos faltantes

De los 866 participantes comunitarios de ≥40 años: 758 analizados, 18 excluidos por solapamiento
con la cohorte clínica, **90 excluidos por datos faltantes**.

| Motivo | n |
|---|---|
| Sin los 23 ítems completos | 52 |
| Sin educación válida | 43 |
| **Con ítems completos Y educación válida** | **0** |

Los dos motivos son casi disjuntos (38 tienen ítems pero no educación; 47 al revés), de modo que
**ningún excluido es recuperable**: a todos les falta el desenlace o la exposición. No hay
análisis de sensibilidad posible por reincorporación.

**Los excluidos difieren de los incluidos** (a declarar como limitación):

| | Incluidos | Excluidos | p |
|---|---|---|---|
| Edad | 63,3 (n=758) | 64,8 (n=108) | 0,100 |
| Educación | 10,3 | **12,0** (n=65) | 0,029 |
| ACE-III | 75,2 | **81,4** (n=56) | 0,001 |

Tienen más educación y mejor rendimiento. Como sensibilidad se ponderó por el inverso de la
probabilidad de inclusión (modelo logístico sobre edad, sexo y educación): escalón **+0,02**
[−2,51; +2,56], b₂ = **−0,0707** (p = 3,4×10⁻⁸). Ninguna conclusión cambia.

---

## Veredicto del bloque

Los dos resultados sobreviven a todo: 20 especificaciones alternativas, tres estimadores robustos,
la eliminación del 1 % más influyente, la ponderación por selección y el test de placebo sobre los
14 cortes candidatos. **La ausencia de escalón en 12 años y la curvatura de la asociación son
propiedades de los datos, no de las decisiones de modelado.**

## Limitaciones que este bloque incorpora al manuscrito

1. La educación se mide con amontonamiento en valores de credencial (37,5 % y 47,3 % en tres
   valores) — limitación de medición de la exposición.
2. Los 90 excluidos de la cohorte comunitaria tenían más educación y mejor ACE-III; no son
   recuperables porque a todos les falta el desenlace o la exposición. La ponderación por
   probabilidad de inclusión no cambia las conclusiones.
3. Los residuos no son normales (cola izquierda por techo); se usa HC3 en todo el estudio.


---

## V4 — Psicometría y métrica latente

> Ejecutado 2026-07-31. Script: `codigo/V4_tri_dif_metrica_latente.py` (+ addenda ordinal y DTF).
> Salidas: `resultados/V4_tri.json`, `V4b_dif_ordinal.json`, `V4c_dtf.json`.

**Pregunta del bloque:** el puntaje bruto del ACE-III es una función ojival de la habilidad latente
y tiene techo, de modo que **comprime en el extremo alto y podría fabricar rendimientos decrecientes
donde no los hay**. Es la objeción psicométrica al resultado principal. Se responde reestimando
todo sobre θ, métrica de intervalo y sin techo.

Muestra con los 23 ítems completos: comunitaria **758**, clínica **2027**, combinada **2785**.

---

## A. Modelo de respuesta graduada (Samejima), métrica común a las dos cohortes

Discriminación mediana **1,54** (rango 0,82–2,27). Los cinco ítems más discriminativos son
recuerdo diferido de nombre y dirección (a=2,27), recuerdo anterógrado (2,08), orientación en
espacio (1,91), memoria retrógrada (1,91) y comprensión lectora (1,90).

θ estimado por valor esperado a posteriori con previa normal estándar (implementación explícita,
integración sobre grilla de 161 puntos en [−4, 4]): media −0,026, DE 0,953, error estándar medio
0,271. Correlación con el puntaje bruto **r = 0,980** (Spearman 0,993).

## B. La curvatura sobrevive en la métrica latente

| | Curvatura b₂ | IC 95 % | p | b₂ estandarizado |
|---|---|---|---|---|
| **Comunitaria**, puntaje bruto | −0,0784 | −0,1037; −0,0531 | 1,3×10⁻⁹ | −0,00587 |
| **Comunitaria**, θ latente | **−0,0031** | −0,0046; −0,0017 | **3,4×10⁻⁵** | −0,00388 |
| **Clínica**, puntaje bruto | −0,0694 | −0,0960; −0,0429 | 2,9×10⁻⁷ | −0,00389 |
| **Clínica**, θ latente | **−0,0026** | −0,0040; −0,0012 | **3,6×10⁻⁴** | −0,00262 |

El modelo cuadrático sigue superando al lineal sobre θ (p = 7,3×10⁻⁶ y 5,4×10⁻⁴).

**Interpretación honesta: parte de la curvatura sí es artefacto de escala, pero la mayor parte no.**
En unidades de desviación estándar del desenlace, la curvatura pasa de −0,00587 a −0,00388 en la
comunitaria y de −0,00389 a −0,00262 en la clínica: sobrevive **el 66 % y el 67 %** de la curvatura
estandarizada, con una concordancia notable entre cohortes. El techo del puntaje bruto exagera los
rendimientos decrecientes en aproximadamente un tercio; los otros dos tercios son propiedad de la
cognición, no del instrumento.

**Pendientes marginales sobre θ** (DE de habilidad por año de escolaridad):

| | 3 años | 7 años | 12 años | 17 años | Razón 3/17 |
|---|---|---|---|---|---|
| Comunitaria | +0,157 | +0,132 | +0,100 | +0,069 | **2,3×** |
| Clínica | +0,157 | +0,136 | +0,110 | +0,084 | **1,9×** |

Sobre el puntaje bruto la razón era ~4×; sobre θ es ~2×. **Se reporta la cifra latente, que es la
conservadora.** Que las dos cohortes den +0,157 en el año 3 es coincidencia numérica, pero la
concordancia del perfil completo no lo es.

## C. El escalón en 12 años tampoco existe en la métrica latente

| Cohorte | Escalón sobre θ | IC 95 % | p |
|---|---|---|---|
| Comunitaria | +0,108 | −0,051; +0,267 | 0,184 |
| Clínica | −0,023 | −0,162; +0,116 | 0,746 |

## D. Funcionamiento diferencial del ítem por educación

Logística ordinal de Zumbo (método primario; la versión binaria es inestable en ítems de piso),
con purificación iterativa del anclaje y control de tasa de falso descubrimiento de
Benjamini-Hochberg. Grupo focal <12 años n=408; referencia ≥12 años n=350.

| Ítem | ΔR² Nagelkerke | q (FDR) | Efecto | Dirección |
|---|---|---|---|---|
| Lectura de palabras irregulares | 0,0272 | 0,0001 | despreciable | favorece alta escolaridad |
| Fluencia semántica | 0,0250 | <0,0001 | despreciable | favorece baja escolaridad |
| Comprensión lectora | 0,0162 | 0,0001 | despreciable | favorece alta escolaridad |
| Escritura | 0,0155 | 0,0068 | despreciable | favorece alta escolaridad |
| Fluencia fonológica | 0,0148 | 0,0006 | despreciable | favorece baja escolaridad |
| Reconocimiento nombre y dirección | 0,0145 | 0,0047 | despreciable | favorece baja escolaridad |
| Letras fragmentadas | 0,0127 | 0,0432 | despreciable | favorece alta escolaridad |

**Ítems con efecto no trivial (ΔR² ≥ 0,035): ninguno.** Nueve ítems alcanzan significación
estadística tras corrección por FDR, todos con efecto despreciable — lo esperable con n=758.

**Esto replica el análisis A2 previo** (Lectura 0,0264 vs 0,0272 acá; Escritura 0,0171 vs 0,0155),
pese a que aquel corrió sobre n=776 sin armonizar el reconocimiento y sin excluir el solapamiento.
La conclusión psicométrica es estable frente a esas correcciones.

**Los sesgos van en direcciones opuestas y se compensan:**

- favorecen **alta** escolaridad (5 ítems): lectura de irregulares, comprensión lectora, escritura,
  letras fragmentadas, cubo — todos alfabetización o visoconstrucción gráfica (Σ|ΔR²| = 0,081)
- favorecen **baja** escolaridad (4 ítems): fluencia semántica, fluencia fonológica, reconocimiento
  y recuerdo diferido de nombre y dirección (Σ|ΔR²| = 0,060)

## E. Funcionamiento diferencial del TEST COMPLETO — el hallazgo central del bloque

Si los sesgos de ítem se compensan, el puntaje total debería ser insesgado a igual habilidad
latente. Se testeó directamente: se modeló el total en función de θ (y θ²) más la educación.

| Cohorte | Baja vs alta escolaridad, a igual θ | IC 95 % | p |
|---|---|---|---|
| Comunitaria | **+0,08 puntos** | −0,22; +0,38 | 0,600 |
| Clínica | **+0,34 puntos** | +0,08; +0,59 | 0,009 |

Por año de escolaridad: +0,001 puntos (p = 0,97) en la comunitaria y −0,070 puntos (p < 0,001) en
la clínica — es decir, menos de 1 punto acumulado a lo largo de 12 años de escolaridad.

> **A igual habilidad cognitiva, el ACE-III mide entre 0,08 y 0,34 puntos distinto según la
> escolaridad. La regla vigente corrige esa diferencia con 18 puntos: entre 50 y 200 veces el
> sesgo que existe.**

El modelo explica el 98,3 % y el 98,5 % de la varianza del total, de modo que la estimación del
sesgo residual es precisa.

## F. Invarianza entre cohortes

Tres de 23 ítems muestran DIF moderado entre la cohorte comunitaria y la clínica: lectura de
palabras irregulares (ΔR² = 0,050), letras fragmentadas (0,045) y escritura (0,038) — los mismos
ítems de alfabetización. Ninguno alcanza efecto grande.

**Consecuencia metodológica:** la falta de invarianza estricta justifica la decisión ya tomada de
**no reportar nunca una estimación marginal combinada**. El análisis usa un marco único con
interacciones cohorte × educación y presenta las cohortes por separado; la réplica se evalúa como
concordancia entre estimaciones independientes, no como precisión de un promedio.

---

## Veredicto del bloque

1. **La curvatura no es un artefacto del techo.** Sobrevive en la métrica latente conservando dos
   tercios de su magnitud estandarizada, con concordancia entre cohortes. Se reportará sobre θ.
2. **El escalón tampoco aparece sobre θ** en ninguna cohorte.
3. **Los ítems del ACE-III no están sesgados por educación de forma relevante**, y sus sesgos
   menores se compensan entre sí.
4. **El sesgo educativo del puntaje total, a igual habilidad, es de 0,08 a 0,34 puntos.** La regla
   lo corrige con 18.

## Lo que esto cambia en el mensaje del manuscrito

El problema no está en el instrumento sino en la regla de decisión. El ACE-III es psicométricamente
razonable y prácticamente insesgado a nivel del total; lo que produce la inequidad es el ajuste
categórico de 18 puntos que se le aplica encima. Esto vuelve el trabajo **constructivo** en lugar
de meramente crítico: no propone descartar el ACE-III, propone reemplazar la corrección categórica
por una continua.

## Pendiente

Reestimar sobre θ las cifras de positividad (bloque V5) y decidir si la figura principal se dibuja
sobre puntaje bruto (interpretable clínicamente) o sobre θ (correcto psicométricamente). Propuesta:
**bruto en la figura, θ en la tabla de sensibilidades**, declarando la atenuación de 4× a 2×.


---

## V6 — Verificación de la codificación diagnóstica

| Control | Resultado |
|---|---|
| Cobertura de la oración canónica | 2750 de 3025 conclusiones (90,9 %) |
| Menciones al ACE-III en la oración clasificatoria | **0 de 2750** |
| Menciones a cualquier test o puntaje | **0 de 2750** |
| Cobertura por tramo educativo | 92,4 % (<7) · 93,9 % (7–11) · 89,5 % (≥12); p = 0,006 |
| Rotulados sin deterioro con ACE-III <82 | 1 de 87 |
| Conclusiones con marca «normal» y palabra de severidad | 25, clasificadas por severidad (salvaguarda activa) |
| Validación independiente (ACE-III no usado para clasificar) | 92,5 · 78,6 · 54,0; Kruskal-Wallis p = 1,4×10⁻²⁰² |

La oración canónica es «el presente perfil cognitivo se corresponde con…». Muestra de 50 conclusiones
para auditoría humana en `verificacion/V6_muestra_auditoria.csv`.

---

## V10 — Por qué se descartó el criterio funcional

El cuestionario de actividades de la vida diaria presenta gradiente educativo en subescalas
específicas:

| Subescala | r con escolaridad | ¿Usable? |
|---|---|---|
| Actividades básicas | +0,010 | sí |
| Manejo de dinero | −0,050 | sí |
| Tareas del hogar | −0,083 | sí |
| Tecnología | −0,154 | no |
| Comunicación (incluye lectura y escritura) | −0,160 | no |
| Transporte y conducción | −0,194 | no |
| Empleo y recreación | **−0,265** | no |

Aun restringido a las tres subescalas neutrales, el criterio funcional no separó a los controles de
baja escolaridad de los casos de deterioro leve, con ninguna de cinco definiciones ensayadas. Motivo:
el cuestionario está **autoinformado en el 73 %** de los casos.

---

## V12 — Selección del criterio de control

Dependencia educativa de todas las pruebas presentes en ambas bases, ajustada por edad y expresada en
desviaciones estándar por año de escolaridad:

| Prueba | Efecto por año | Medias por tramo (<7 · 7–11 · ≥12) |
|---|---|---|
| **Memoria de reconocimiento de lista** | **0,027** | **12,2 · 12,2 · 12,8** |
| Series motoras | 0,036 | 2,1 · 2,4 · 2,7 |
| Control inhibitorio motor | 0,064 | 1,3 · 1,7 · 2,2 |
| Dígitos adelante | 0,070 | 4,4 · 4,5 · 5,2 |
| Trail Making B | 0,081 | 173 · 152 · 102 |
| Trail Making A | 0,088 | 80 · 62 · 43 |
| Total del Ineco Frontal Screening | 0,111 | 14,2 · 18,3 · 22,0 |

Se eligió la **memoria de reconocimiento**: es la menos dependiente de la escolaridad, está en ambas
bases con idéntica escala (0–15) y separa monótonamente los grupos clínicos (13,25 sin deterioro ·
10,93 deterioro leve · 8,55 deterioro moderado o severo). Las series motoras se descartaron por
escalas distintas entre bases (máximo 3 frente a 6). El umbral de 10 puntos es el único en el que la
condición de control no depende del tramo educativo (χ² p = 0,198).

### Resultado con ese criterio

Con 297 casos y 297 controles emparejados por edad (69,7 frente a 69,5 años):

| Regla | Sensibilidad | Especificidad | Youden | <7 | 7–11 | ≥12 | Gradiente |
|---|---|---|---|---|---|---|---|
| Vigente 86/68 | 0,943 | 0,657 | 0,599 | 63,0 | 15,9 | 30,3 | **47,2** |
| Corrección continua | 0,956 | 0,670 | 0,626 | 35,6 | 29,3 | 33,8 | **6,3** |

Intervalos por remuestreo (1000 réplicas): gradiente vigente 32,9 a 59,8; continua 1,9 a 22,8; razón
**4,8 (2,3 a 22,3)**; diferencia de Youden +0,027 (−0,013 a +0,074).

---

## Reproducción

```
codigo/19_build_definitivo.py        # corpus clínico -> clinico_definitivo.csv (~25 min)
codigo/20_dx_desde_conclusiones.py   # clasificación de referencia desde el texto
codigo/V1b_fix_dni_y_solape.py       # normalización de documentos y solapamiento
codigo/V2_reproduccion_independiente.py
codigo/V3_supuestos_especificacion.py
codigo/V4_tri_dif_metrica_latente.py
codigo/V6_verificacion_dx.py
codigo/V12_equidad_definitiva.py     # análisis de equidad + Figura 4
codigo/F1_figuras_manuscrito.py      # Figuras 1 a 3
codigo/F3_tablas_manuscrito.py       # Tablas 1 a 3
codigo/F4_armar_envio.py             # ensamblado y verificación del reglamento
```

Todos los scripts usan rutas absolutas y corren desde cualquier directorio.

---

# V15 — Corrección del sesgo de Harvey en el modelo de dispersión

## El defecto

El modelo normativo continuo estima la dispersión con una segunda regresión sobre el logaritmo del
residuo al cuadrado. Esa estimación **está sesgada**: si ε ~ N(0, σ²), entonces

    E[log ε²] = log σ² + E[log χ²₁] = log σ² − 1,27036

de modo que exponenciar la predicción devuelve una varianza multiplicada por e^(−1,27036) = 0,281, es
decir un **σ 1,887 veces más chico que el real**.

## Cómo se detectó

Revisando por qué el modelo declaraba un percentil 5 que no se comportaba como tal. La comprobación es
directa: tipificar los propios controles con el modelo y contar cuántos caen bajo su percentil 5
nominal.

| | Sin corregir | Con la corrección |
|---|---|---|
| % de controles bajo el percentil 5 nominal | **19,0 %** | **6,5 %** |
| % bajo el percentil 10 nominal | 22,8 % | 11,9 % |
| Desvío de los puntajes tipificados (esperado 1,000) | **1,906** | **1,010** |

El factor 1,906 observado coincide con el 1,887 teórico.

Contraste adicional: el σ modelado tras la corrección reproduce los desvíos residuales observados por
tramo educativo, cosa que sin corregir no ocurría ni de lejos.

| Tramo | Desvío residual observado | σ modelado corregido |
|---|---|---|
| < 7 años | 12,39 | 11,08 |
| 7–11 años | 8,56 | 9,26 |
| ≥ 12 años | 7,42 | 7,01 |

## Qué cambió y qué no

**Cambió** todo lo expresado como percentil absoluto. El σ a los 65 años pasa de 6,8 a **12,9** puntos
sin escolaridad y de 3,1 a **5,8** con veinte. En consecuencia desaparece el régimen en que el corte de
68 quedaba por debajo del percentil 5 entre los 8 y los 11 años: **el corte cae siempre entre el
rendimiento esperado y el percentil 5**. El salto entre 11 y 12 años pasa de 0 → 77 % a **5 → 65 %**.

**No cambió** ninguno de los resultados principales, y la razón es demostrable. Las dos reglas
comparadas se calibran con un **cuantil empírico** de la distribución tipificada
(`np.quantile(z, positividad)`); multiplicar todos los z por una constante es una transformación
monótona creciente, que deja el ordenamiento —y por lo tanto la clasificación— idéntico. Reejecutado
V13 completo:

| | Antes | Después |
|---|---|---|
| Gradiente de la regla vigente | 44,0 [30,9; 57,7] | **44,0 [30,9; 57,7]** |
| Gradiente residual de la continua | 4,0 [2,0; 21,7] | **4,0 [2,0; 21,7]** |
| Δ Youden (continua − vigente) | +0,022 [−0,022; +0,074] | **+0,022 [−0,022; +0,074]** |

Tampoco cambian la curva de rendimiento esperado —estimada por una regresión distinta, no afectada—,
la pendiente de la escolaridad sobre la log-varianza —un desplazamiento del intercepto no la toca— ni
la falsación del escalón.

## Calibración residual

Corregida la dispersión, la calibración es adecuada pero no exacta: cae bajo el percentil 5 nominal el
6,5 % en lugar del 5,0 %. Los residuos tipificados conservan asimetría de **−0,58** y curtosis de
**+0,43**, atribuibles al techo del instrumento. Por eso los percentiles próximos a los extremos deben
leerse como aproximaciones, y así se declara en las limitaciones del manuscrito.

**Implementación:** la constante figura como `SESGO_LOGCHI2` en `codigo/F6_figura_equipo.py`,
`V8_correccion_continua.py`, `V12_equidad_definitiva.py` y `V13_equidad_corregida.py`, y ya está
incorporada al intercepto publicado en `resultados/CALC_coeficientes.json`.

---

# V16 — Magnitud de la heterocedasticidad

La variabilidad del rendimiento entre personas sin deterioro **no es constante a lo largo de la
escolaridad**, y ese es el motivo estructural por el que ningún corte fijo puede funcionar.

| Tramo | n | Media del ACE-III | Desvío |
|---|---|---|---|
| < 7 años | 131 | 65,5 | **13,82** |
| 7–11 años | 216 | 76,3 | 8,58 |
| ≥ 12 años | 316 | 86,0 | 7,77 |

Prueba de Levene entre los tres tramos: W = 32,97; **p = 2,2×10⁻¹⁴**.

Modelada de forma continua, `log(σ²) ~ escolaridad + edad` sobre los controles comunitarios:

| Término | Coeficiente | IC 95 % | p |
|---|---|---|---|
| Escolaridad | **−0,0806** | −0,1132 a −0,0480 | **1,5×10⁻⁶** |
| Edad | +0,0082 | −0,0120 a +0,0285 | 0,430 |

A los 65 años el desvío pasa de **12,9 puntos** sin escolaridad a **5,8** con veinte: se reduce a menos
de la mitad. De ahí que un mismo número ocupe percentiles muy distintos según a quién se aplique.

| Escolaridad | 0 | 4 | 8 | 11 | 12 | 16 | 20 |
|---|---|---|---|---|---|---|---|
| Corte vigente | 68 | 68 | 68 | 68 | 86 | 86 | 86 |
| Percentil que ocupa | **86** | 56 | 20 | **5** | **65** | 42 | 28 |

---

# V17 — Material trasladado desde el cuerpo del manuscrito

Por límite de extensión, el detalle de estos análisis se reporta aquí. Ninguno fue eliminado.

## A. Robustez, especificación completa

Distancia de Cook máxima 0,033 y 0,029; al eliminar el 1 % más influyente la curvatura pasó de −0,0784
a −0,0724 y −0,0626. Las regresiones robusta de Huber, de la mediana y censurada en el techo
coincidieron. En **doce especificaciones de covariables** la discontinuidad osciló entre −0,41 y +0,48,
siempre con intervalos que contienen el cero, y la ponderación por probabilidad de inclusión arrojó
+0,02. En **ocho especificaciones alternativas** la curvatura osciló entre −0,058 y −0,085.

## B. Cortes empíricos exploratorios

Los cortes que maximizan el índice de Youden en la muestra emparejada resultaron **más bajos que los
vigentes en los tres tramos, y graduados**: 57, 64 y 78, frente a 68, 68 y 86. Están sesgados por el
diseño de dos puertas y por optimismo no corregido —no hay validación externa ni corrección por
remuestreo—, de modo que **no constituyen una recomendación clínica** y se reportan sólo para mostrar la
dirección del desajuste. La comparación que sí tiene contenido es que la regla vigente supera a
cualquier corte único: Youden 0,552, frente a 0,497 con corte 82 y 0,394 con corte 86.

## C. Por qué el criterio funcional no era utilizable

El cuestionario de actividades de la vida diaria está autoinformado en el **73 %** de los casos, y sus
subescalas de empleo, comunicación y tecnología presentan gradiente educativo (r hasta **−0,265**):
incluyen ítems de lectura, escritura y uso de tecnología que penalizan la falta de exposición y no el
deterioro. Definir controles con ese instrumento habría fabricado el resultado, porque el criterio de
control habría heredado la propia exposición bajo estudio.

## D. Métrica latente, detalle

Unidimensionalidad esencial: razón entre autovalores 5,75; primer componente 35,8 %. Independencia
local: Q3 medio −0,035, con 2 de 253 pares por encima de 0,20, estructuralmente esperables. Curvatura
sobre la habilidad latente: −0,0031 y −0,0026 (p = 3,4×10⁻⁵ y 3,6×10⁻⁴), que conservan el 66 % y el
67 % de la magnitud observada en la escala bruta. Curvatura por estrato de gravedad: −0,0655, −0,0609 y
−0,0696; interacción p = 0,961.

## E. Funcionamiento diferencial por ítem

Ver los bloques V4-D y V4-E de este suplemento, que reportan el barrido completo en ambas cohortes con
ΔR² de Nagelkerke, q corregido por tasa de falso descubrimiento, delta de Mantel-Haenszel y clase ETS.
