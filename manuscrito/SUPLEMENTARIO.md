# Material suplementario

**La escolaridad desplaza y estrecha la distribución del rendimiento en el ACE-III: ningún punto de corte fijo es equitativo entre niveles educativos en dos cohortes argentinas**

**Autores.** Fernando Márquez¹˒²˒³˒⁶; Luciana Vita²˒³˒⁵; Paula Arellano³˒⁵; M. Laura Noguera²˒³˒⁴˒⁵; María Beatriz Bistué Millón²˒⁴˒⁵; M. Sol Cañadas²˒⁵; M. Celeste Moyano³˒⁵; Mariana Zanino³˒⁵; Cristian Posleman²˒⁵; Iara Jácome¹˒³; Florencia Portillo³˒⁵; M. Florencia Porra²˒⁵; Yesica Arbo⁶; Julieta Quiroga⁶; Daniel Lucato⁶; Martín A. Bruno²˒⁵; Diana Bruno¹˒³.

**Afiliaciones.** ¹ Instituto de Neurociencias de San Juan (Clínica El Castaño), San Juan, Argentina. ² Instituto de Ciencias Biomédicas (ICBM), Facultad de Ciencias Médicas, y ³ Instituto de Investigaciones en Psicología Básica y Aplicada (IIPBA), Facultad de Filosofía y Humanidades, Universidad Católica de Cuyo, San Juan, Argentina. ⁴ Ministerio de Salud Pública, Gobierno de San Juan, Argentina. ⁵ CONICET, Argentina. ⁶ Hospital Descentralizado Dr. Guillermo Rawson, San Juan, Argentina.

**Autor de correspondencia.** Fernando Márquez — fmarquez.mum@gmail.com

Documentación de los bloques de análisis y verificación del estudio. El código está en `codigo/`, las
salidas numéricas en `resultados/` y las bitácoras detalladas en `verificacion/`, todo en el
repositorio público <https://github.com/fermarquez88/kaizenai-ace>.

> **Principio de trabajo.** Cada bloque se ejecutó sobre los datos originales, sin tomar cifras de
> corridas anteriores. Cuando un bloque detectó un defecto, se documentó, se corrigió y se
> reejecutaron todos los bloques dependientes. Tres hallazgos del propio proceso obligaron a
> modificar conclusiones ya escritas; se detallan más abajo.

---

## Índice de bloques

| Bloque | Contenido |
|---|---|
| **V1** | Integridad de datos |
| **V2** | Reproducción independiente |
| **V3** | Supuestos y especificación |
| **V4** | Psicometría y métrica latente |
| **V6** | Verificación de la codificación diagnóstica |
| **V10** | Por qué se descartó el criterio funcional |
| **V12** | Selección del criterio de control |
| **V13** | Comparación entre reglas, con controles de fuente única |
| **V25** | Replicación por ruralidad y por área geográfica |
| **V26** | El estrechamiento de la dispersión: escala frente a habilidad |
| **S** | Puntaje esperado en el ACE-III según escolaridad y edad |

---

## Los tres hallazgos que obligaron a cambiar conclusiones

**1. La curvatura era en parte un artefacto del techo (V4).** El análisis inicial sobre el puntaje
bruto daba una razón de cuatro veces entre la pendiente del año 3 y la del año 17. Al reestimar sobre
la habilidad latente del modelo de respuesta graduada, persistió dos tercios de la curvatura. El
manuscrito reporta la magnitud sobre el puntaje bruto, que es la escala en que se aplica la regla, y
declara que un tercio del efecto es atribuible al techo del instrumento.

**2. El desenlace de deterioro leve no era interpretable (V9–V10).** Los controles comunitarios con
menos de 7 años de escolaridad puntuaban 66,1, mientras los casos clínicos de deterioro leve del
mismo tramo puntuaban 67,9 —siendo 8,6 años mayores—. Dos lecturas competían: contaminación del
grupo control, o sobre-aplicación de la etiqueta clínica por efecto del propio corte. Al no poder
distinguirlas, el desenlace se eliminó del manuscrito.

**3. La razón entre gradientes dejó de reportarse (V11–V13).** Las primeras estimaciones expresaban el
efecto de equidad como una razón entre el gradiente de la regla vigente y el de la corrección continua.
Esa razón resultó inutilizable por dos motivos independientes. Primero, era inestable: pasó de once
veces a 1,8 con intervalo que incluía la unidad al emparejar por edad y propagar la incertidumbre.
Segundo, y decisivo, **la planitud del gradiente de la corrección continua es una consecuencia
algebraica de tipificar respecto de la escolaridad, no un hallazgo**: señalar bajo un cuantil fijo de
esa tipificación produce equidistribución por construcción. Hoy no se reporta ninguna razón. Se
reportan dos cantidades con contenido empírico: el gradiente que produce la regla vigente y si
eliminarlo cuesta desempeño diagnóstico.

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

### Resultado con ese criterio, superado por V13

Con controles de fuente mixta —comunitarios y clínicos— este bloque estimó un gradiente de la regla
vigente de 47,2 puntos porcentuales y una diferencia de Youden de +0,027. **Esas cifras no son las
publicadas.** La auditoría externa objetó que la composición del grupo control variaba con la
exposición: 0,8 % de controles clínicos en el tramo de menos de 7 años frente al 20,2 % en el de 12 o
más, con medias de ACE-III de 65,5 y 93,0 respectivamente. El análisis se rehízo con controles de
fuente única; sus resultados son los del bloque siguiente y son los que publica el manuscrito.

---

## V13 — Comparación entre reglas, con controles de fuente única

> **Procedencia.** `codigo/V13_equidad_corregida.py` → `resultados/V13_equidad_corregida.json`.
> De este bloque provienen las dos cifras titulares del manuscrito. **Reemplaza a V12.**

Corrige tres defectos señalados por la auditoría externa: los controles pasan a ser de fuente única,
se agrega sensibilidad al umbral del criterio, y el efecto deja de expresarse como razón entre
gradientes para reportarse como gradiente con su intervalo.

### A. Muestra

Casos de deterioro moderado o severo y controles comunitarios, emparejados por edad en estratos
quinquenales dentro del rango común.

| | Casos | Controles |
|---|---|---|
| n | 195 | 195 |
| Edad media, años | 67,2 | 66,9 |
| Con menos de 7 años de escolaridad | — | 54 |
| Con 7 a 11 años | — | 59 |
| Con 12 años o más | — | 82 |

Punto de operación común a ambas reglas: **66,9 % de positividad**. Es un punto de
comparación y no un escenario clínico; iguala la severidad para que la diferencia entre reglas refleje
su **forma**.

### B. Desempeño y reparto de los señalamientos

| Regla | Sensibilidad | Especificidad | Youden | < 7 años | 7–11 | ≥ 12 | Gradiente |
|---|---|---|---|---|---|---|---|
| Vigente 86/68 | 0,944 | 0,605 | 0,549 | 53,7 % | 20,3 % | 43,9 % | **33,4 pp** |
| Corrección continua | 0,944 | 0,605 | 0,549 | 42,6 % | 40,7 % | 36,6 % | 6,0 pp |

Las tres columnas por tramo son el porcentaje de personas **sin deterioro** que cada regla señala. El
gradiente es la diferencia entre el tramo más señalado y el menos señalado.

Intervalos por remuestreo, 1000 réplicas:

| Cantidad | Estimación | IC 95 % | Lectura |
|---|---|---|---|
| Gradiente de la regla vigente | **33,4 pp** | 17,4 a 49,2 | empírico |
| Gradiente residual de la continua | 6,0 pp | 1,9 a 23,9 | esperado por construcción |
| Diferencia de Youden, continua − vigente | **0,000** | −0,037 a +0,062 | empírico |

> **Qué es un hallazgo y qué no.** La corrección continua tipifica respecto de una media y una varianza
> estimadas como función de la escolaridad. Señalar bajo un cuantil fijo de esa tipificación produce
> equidistribución **por construcción**, de modo que el gradiente residual de 6,0
> no es un resultado. Las dos cantidades con contenido empírico son el gradiente que produce la regla
> vigente y el costo diagnóstico de eliminarlo. Su intervalo incluye el cero y excluye pérdidas
> mayores a 0,062: la conclusión es de **equivalencia**, no de superioridad.

### C. Sensibilidad al umbral del criterio de control

El criterio define como control a quien reúne cuatro condiciones: **10 puntos o más en memoria de
reconocimiento de lista, sin antecedente de accidente cerebrovascular, sin antecedente de traumatismo
de cráneo e independiente en las actividades básicas de la vida diaria** (n = 342; χ² de neutralidad
educativa p = 0,504). Esta tabla varía el umbral de reconocimiento y deja fijas las otras tres.
Umbrales más estrictos excluyen más deterioro leve, pero introducen dependencia educativa.

| Umbral | n controles | p de asociación con el tramo educativo | Casos leves que califican | Gradiente vigente | Δ Youden |
|---|---|---|---|---|---|
| **10** | 195 | 0,374 | 72,2 % | 33,4 pp | 0,000 |
| 11 | 187 | 0,806 | 63,3 % | 27,3 pp | +0,011 |
| 12 | 174 | 0,778 | 51,2 % | 34,8 pp | −0,023 |
| 13 | 147 | 0,963 | 36,6 % | 21,3 pp | 0,000 |

En los cuatro umbrales la condición de control es independiente del tramo educativo; el de 10 es el
que más holgura ofrece sin perder representación del tramo de menor escolaridad (p = 0,374). Los más estrictos ganan pureza del grupo control y pierden independencia respecto de la
exposición, que es lo que el diseño necesita preservar. **El gradiente de la regla vigente se sostiene
entre 21,3 y 34,8 puntos porcentuales en los cuatro umbrales, y la diferencia de Youden entre −0,023 y
+0,011**: la conclusión no depende de esta elección.

> **Limitación principal.** Con el umbral empleado, el 72,2 % de los casos clínicos
> de deterioro leve calificaría como control. Si parte de los controles de baja escolaridad tiene
> deterioro no detectado, señalarlos no es un falso positivo, de modo que **la contaminación infla el
> gradiente medido**: los 33,4 puntos porcentuales son un límite superior.

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
| % de controles bajo el percentil 5 nominal | **18,7 %** | **5,8 %** |
| % bajo el percentil 10 nominal | 22,8 % | 11,9 % |
| Desvío de los puntajes tipificados (esperado 1,000) | **1,902** | **1,008** |

El factor 1,902 observado coincide con el 1,887 teórico.

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
| Gradiente de la regla vigente | 33,4 [17,4; 49,2] | **33,4 [17,4; 49,2]** |
| Gradiente residual de la continua | 4,0 [2,0; 21,7] | **4,0 [2,0; 21,7]** |
| Δ Youden (continua − vigente) | 0,000 [−0,037; +0,062] | **0,000 [−0,037; +0,062]** |

Tampoco cambian la curva de rendimiento esperado —estimada por una regresión distinta, no afectada—,
la pendiente de la escolaridad sobre la log-varianza —un desplazamiento del intercepto no la toca— ni
la falsación del escalón.

## Calibración residual

Corregida la dispersión, la calibración es adecuada pero no exacta: cae bajo el percentil 5 nominal el
5,8 % en lugar del 5,0 %. Los residuos tipificados conservan asimetría de **−0,58** y curtosis de
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
| < 7 años | 74 | 66,0 | **14,3** |
| 7–11 años | 216 | 76,3 | 8,58 |
| ≥ 12 años | 316 | 86,0 | 7,77 |

Prueba de Levene entre los tres tramos: W = 32,97; **p = 2,2×10⁻¹⁴**.

Modelada de forma continua, `log(σ²) ~ escolaridad + edad` sobre los controles comunitarios:

| Término | Coeficiente | IC 95 % | p |
|---|---|---|---|
| Escolaridad | **−0,0819** | −0,130 a −0,034 | **8,6×10⁻⁴** |
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

Este material proviene de **dos muestras distintas** y conviene no confundirlas.

**Cortes óptimos por tramo (bloque V7).** Los cortes que maximizan el índice de Youden resultaron más
bajos que los vigentes en los tres tramos y graduados: **57, 64 y 78**, frente a 68, 68 y 86. Se
calcularon sobre la muestra de V7, que **no está emparejada por edad** y cuyos controles se definieron
con el criterio funcional que V10 descartó. Son exploratorios, están sesgados por el diseño y por
optimismo no corregido, y **no constituyen una recomendación clínica**: se reportan sólo para mostrar
la dirección del desajuste. Dentro de esa misma muestra la regla vigente rinde Youden 0,628.

**Comparación con el corte único (bloque V13).** Calculada sobre la muestra emparejada de fuente única,
que es la que publica el manuscrito:

| Regla | Sensibilidad | Especificidad | Youden | Señala en < 7 años |
|---|---|---|---|---|
| **Vigente 86/68** | 0,941 | 0,611 | **0,552** | 60,3 % |
| Corte único 82 | 0,952 | 0,419 | 0,370 | 92,3 % |
| Corte único 86 | 0,985 | 0,289 | 0,274 | 98,7 % |
| Mejor corte único posible (67) | — | — | 0,541 | — |

**Ningún corte único iguala a la regla vigente en esta muestra.** Ajustar por escolaridad mejora la
clasificación; el problema es la forma de ese ajuste, no su existencia.

> **Por qué se separan.** Una versión anterior comparaba el Youden de V13 (0,552) contra los cortes
> únicos de V7 (0,497 y 0,394), que salen de otra muestra, sin emparejar y con controles de fuente
> mixta. La conclusión cualitativa no cambia —y de hecho se refuerza sobre la muestra emparejada—, pero
> las cifras no eran comparables entre sí.

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

---

## V25 — Replicación por ruralidad y por área geográfica

> **Procedencia.** `codigo/V25_replicacion_geografica.py` → `resultados/V25_replicacion_geografica.json`.

Dos preguntas que conviene no confundir, porque no miden lo mismo ni tienen el mismo respaldo.

**Ruralidad.** Variable `ZonaResidencia` del cuestionario, ítem 2.06 del bloque de determinantes
sociales. El diccionario de variables del programa la define como **área de residencia, 1 = urbano y
2 = rural**. La codificación es consistente con los datos: la categoría 2 es cero en Capital, casi cero
en Rawson y Rivadavia, se concentra en 25 de Mayo, 9 de Julio y Albardón, y su escolaridad media es 7,0
frente a 9,8. Cubre 596 de 758 participantes.

**Área.** Departamento del **centro de evaluación**, no del domicilio. Gran San Juan = Capital, Chimbas,
Rawson, Rivadavia, Santa Lucía y Pocito; periferia = el resto. Cubre 621 de 758. La distinción importa:
un participante puede haberse evaluado en un departamento distinto del que vive, de modo que esta
variable mide **dónde se hizo el tamizaje** y sólo aproxima dónde reside la persona. El protocolo
ambiental del programa señala ese mismo artefacto y prevé reemplazarlo por geocodificación del
domicilio real.

### A. La forma funcional replica en los cuatro estratos

| Estrato | n | Escolaridad media | Curvatura | IC 95 % | Pendiente a 3 y a 17 años | p |
|---|---|---|---|---|---|---|
| Rural | 84 | 7,0 | −0,1801 | −0,3139 a −0,0464 | 4,01 → −1,04 | 0,0035 |
| Urbana | 512 | 9,8 | −0,0699 | −0,1058 a −0,0339 | 2,74 → 0,79 | 1,5×10⁻⁵ |
| Gran San Juan | 383 | 10,2 | −0,0458 | −0,0816 a −0,0100 | 2,18 → 0,89 | 0,014 |
| Periferia | 238 | 8,3 | −0,0977 | −0,1623 a −0,0332 | 3,13 → 0,40 | 0,0003 |

Los cuatro intervalos excluyen el cero. Las interacciones no rechazan la igualdad de forma: **p = 0,072**
para curvatura × ruralidad y **p = 0,138** para curvatura × área. La asociación es curvilínea en todos
los estratos y no hay evidencia de que su forma difiera entre ellos.

La pendiente rural a los 17 años es negativa, pero **casi no hay rurales con esa escolaridad**: es
extrapolación fuera del soporte de los datos y no debe leerse como un hallazgo.

### B. El trato desigual sí difiere: la periferia lo sufre al doble

Proporción de **controles** —los 342 que cumplen el criterio del estudio— que la regla vigente señala,
con intervalo de Wilson al 95 %.

| Estrato | < 7 años | 7 a 11 | ≥ 12 | Gradiente |
|---|---|---|---|---|
| **Periferia** | **69,2 % (27/39)** [54-81] | 17,4 % (8/46) [9-31] | 47,4 % (18/38) [32-63] | **51,8 pp** |
| Gran San Juan | 28,6 % (10/35) [16-45] | 16,7 % (12/72) [10-27] | 41,1 % (46/112) [32-50] | 24,4 pp |
| Rural | 60,0 % (9/15) [36-80] | 12,5 % (2/16) [3-36] | 30,0 % (3/10) [11-60] | 47,5 pp |
| Urbana | 47,5 % (28/59) [35-60] | 18,0 % (18/100) [12-27] | 43,5 % (60/138) [35-52] | 29,5 pp |

**El contraste por área es sólido.** En el tramo de menor escolaridad, el intervalo de la periferia
[54-81] **no se solapa** con el del Gran San Juan [16-45]: entre personas que cumplen el mismo criterio
de normalidad, la regla señala a cerca de siete de cada diez en la periferia y a menos de tres de cada
diez en el área metropolitana.

**El contraste por ruralidad no lo es.** Descansa sobre quince personas en la celda decisiva y su
intervalo [36-80] se superpone ampliamente con el urbano [35-60]. Indica una dirección; no permite
concluir nada. Se informa por transparencia y porque el área, que sí tiene respaldo, apunta al mismo lado.

### C. La dispersión sigue el mismo patrón

| Estrato | n controles | Desvío de 0 a 20 años de escolaridad | Pendiente | p |
|---|---|---|---|---|
| Periferia | 123 | 13,6 → 5,2 | −0,0956 | 0,036 |
| Gran San Juan | 219 | 10,5 → 6,8 | −0,0444 | 0,213 |
| Urbana | 297 | 11,8 → 6,0 | −0,0675 | 0,016 |
| Rural | 41 | — | — | muestra insuficiente |

El estrechamiento de la varianza es marcado y significativo en la periferia, y ni marcado ni
significativo en el Gran San Juan. Es coherente con el gradiente del apartado anterior: donde la
dispersión se comprime más, un corte fijo se desplaza más rápido entre percentiles.

<img src="file:///Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion/figuras/FiguraS_geografia.jpg" style="width:100%">

**Figura S. Proporción de controles señalados por la regla vigente, por tramo de escolaridad.**
**(a)** Por área. **(b)** Por zona de residencia declarada. Barras de error: intervalo de Wilson al
95 %. Debajo de cada barra, el número de controles. La amplitud de los intervalos del panel (b) muestra
por qué el contraste rural no es concluyente.

### D. El salto observado, en las dos cohortes

Los apartados anteriores usan el modelo. Este muestra el dato crudo: la proporción de participantes que
queda bajo el corte vigente, año de escolaridad por año de escolaridad, sin ajustar por nada.

<img src="file:///Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion/figuras/FiguraS_salto_observado.jpg" style="width:82%">

**Figura S2. Proporción por debajo del corte vigente según los años de escolaridad completos.** Se
muestran los años con al menos cinco observaciones. La línea punteada vertical marca el punto en que el
corte pasa de 68 a 86 puntos; la punteada de color une los dos años contiguos que ese cambio separa.
Entre los 11 y los 12 años de escolaridad la proporción señalada se multiplica por **8,4** en la cohorte
comunitaria —del 6,2 % (1 de 16) al 52,7 % (59 de 112)— y por **2,0** en la clínica, del 42,0 % (29 de 69)
al 82,4 % (350 de 425). Ningún cambio en el rendimiento acompaña ese salto: lo produce íntegramente la
regla.

### Qué se puede afirmar y qué no

**Se puede afirmar** que la forma curvilínea de la asociación replica con independencia del área y de la
ruralidad, y que el gradiente de señalamiento es sustancialmente mayor en la periferia que en el Gran
San Juan.

**No se puede afirmar** que la regla clasifique *mal* a esas personas. «Señalar» significa quedar por
debajo del corte y ser derivado a evaluación, no recibir un diagnóstico. El criterio de control no
excluye el deterioro leve, de modo que parte de los señalados puede tener deterioro no detectado; la
contaminación medida es desigual —60,7 % frente a 48,9 % entre los extremos educativos— pero esos doce
puntos no alcanzan para explicar un gradiente de cincuenta y dos.

**Tampoco se puede afirmar** nada sobre la ruralidad como tal, por las razones del apartado B, ni
descartar que la diferencia entre áreas refleje composición socioeconómica no medida antes que
geografía. A eso se suma que el área es la del centro de evaluación y no la del domicilio. El diseño es
transversal y observacional.

---

## V26 — El estrechamiento de la dispersión: ¿escala o habilidad?

> **Procedencia.** `codigo/V26_dispersion_metrica_latente.py` y `codigo/V26b_mecanismo_compresion.py`
> → `resultados/V26_dispersion_latente.json` y `resultados/V26b_mecanismo.json`.

### Por qué se hizo este bloque

El manuscrito sostiene que la dispersión del rendimiento normal se estrecha con la escolaridad y deriva
de ahí su afirmación más general —ningún umbral fijo ocupa la misma posición relativa en todos los
tramos—. Esa afirmación es la que transporta a otros instrumentos, de modo que convenía atacarla antes
de invertir en cualquier extensión.

La amenaza es la que V4 ya había documentado para la **curvatura**: el ACE-III topa en 100 y los
controles de alta escolaridad se apilan contra el techo, de modo que su varianza se comprime por
construcción. V4 mostró que un tercio de la curvatura observada era techo. La dispersión nunca se había
testeado así.

### A. El estrechamiento existe en el puntaje y no en la habilidad

Modelo de posición y de log-varianza (Harvey 1976) sobre los **342 controles
comunitarios** (74 · 118 ·
150 por tramo), estimado por mínimos cuadrados, igual que en V13 y
que en los coeficientes publicados de la calculadora.

| Métrica | Pendiente de log-varianza por año | IC 95 % | p |
|---|---|---|---|
| ACE-III bruto | **-0,0819** | -0,1293 a -0,0344 | 8,6×10⁻⁴ |
| Habilidad latente θ | **+0,0048** | -0,0454 a +0,0551 | 0,850 |

Con errores robustos HC3 la pendiente del puntaje bruto es idéntica y su valor p pasa a
7,3×10⁻⁴; se conserva mínimos cuadrados por coherencia con los coeficientes ya
publicados.

En el puntaje bruto la dispersión pasa de **13,2** puntos sin escolaridad a
**5,8** con veinte años, a los 65 años de edad. Sobre θ la pendiente es
indistinguible de cero.

| | Desvío del ACE-III | Desvío de θ | Desvío de θ sin error de medición | Fiabilidad |
|---|---|---|---|---|
| menos de 7 años | 14,26 | 0,742 | 0,697 | 0,884 |
| 7 a 11 | 8,05 | 0,472 | 0,395 | 0,700 |
| 12 o más | 8,18 | 0,609 | 0,533 | 0,765 |

La varianza observada de θ contiene el error de medición del propio estimador. Como ese error varía con
el nivel de la escala, se descontó por tramo: var(θ observada) = var verdadera + E[SE(θ)²]. La columna
corregida es la que debe leerse.

**Un descargo que juega en contra del hallazgo.** El valor esperado a posteriori contrae θ hacia la
previa, lo que comprime varianza y por tanto **achata** las diferencias entre tramos. Un estrechamiento
que sobreviviera en θ sería conservador. No sobrevive.

### B. El mecanismo, con su predicción falsable

El puntaje bruto es una función ojival de θ: la curva característica del test. Su pendiente
dE[ACE]/dθ es máxima en el centro de la escala —21,0 puntos por
unidad de θ en θ = -1,35— y decae hacia los extremos.
Los controles de alta escolaridad viven cerca del techo, donde la pendiente es baja: la misma
dispersión de habilidad rinde allí menos puntos.

Si el mecanismo es correcto, entonces para cada tramo debe cumplirse

> desvío del puntaje ≈ |dE[ACE]/dθ| evaluada en la media del tramo × desvío de θ del tramo

| Tramo | θ medio | Desvío de θ | Pendiente local | Desvío predicho | Desvío observado | Razón |
|---|---|---|---|---|---|---|
| menos de 7 | -0,516 | 0,742 | 19,1 | 14,20 | 14,26 | 1,00 |
| 7 a 11 | -0,044 | 0,472 | 16,6 | 7,82 | 8,05 | 0,97 |
| 12 o más | +0,650 | 0,609 | 12,0 | 7,31 | 8,17 | 0,89 |

La predicción reproduce el desvío observado en los tres tramos. Entre los extremos el desvío del
puntaje difiere en un factor de **1,75**, la
pendiente del instrumento en **1,59** y la
dispersión de habilidad en apenas **1,22**.

> **Advertencia de lectura.** Los dos factores no multiplican exactamente al cociente observado: la
> descomposición es una linealización local y su residuo es el que aparece en la columna de razones
> (0,89 en el tramo superior). No debe presentarse como una partición exacta de la varianza.

### C. Sobre la habilidad, la dispersión no es monótona

El término cuadrático de la escolaridad en el modelo de dispersión sobre θ es
**+0,00546** (IC 95 % -0,00256 a
+0,01348; p = 0,182), con vértice en
10,4 años. **No alcanza significación**, de modo que la forma
en U no queda establecida; lo que sí queda establecido es que **no es monótona**:

| Comparación | Desvíos de θ | W de Brown-Forsythe | p |
|---|---|---|---|
| menos de 7 frente a 7–11 | 0,742 frente a 0,472 | 16,583 | 0,0001 |
| 7–11 frente a 12 o más | 0,472 frente a 0,609 | 6,375 | 0,0122 |
| menos de 7 frente a 12 o más | 0,742 frente a 0,609 | 3,836 | 0,0514 |

El tramo intermedio tiene la distribución de habilidad **más estrecha** y los dos extremos no difieren
entre sí. Es el mismo tramo de 7 a 11 años que la regla vigente **menos señala** entre personas sin
deterioro (20,3 %) y donde **peor detecta** los casos (85,7 %). Tres hechos independientes convergen en
la misma banda; el trabajo no ofrece una explicación única para esa convergencia y la deja planteada.

### D. Lo que este bloque cambió en el manuscrito

| Antes | Ahora |
|---|---|
| «la escolaridad desplaza **y estrecha** la distribución de la habilidad» | la escolaridad **desplaza** la distribución de la habilidad; el estrechamiento está en el **puntaje** y lo produce la escala |
| el estrechamiento se presentaba como propiedad de la población | se declara como propiedad conjunta de la población y de la métrica, con el peso de cada una cuantificado |
| percentil 83 del corte de 68 sin escolaridad | percentil 82 (cifra de la muestra de control definitiva, n = 342) |
| percentil 70 del corte de 86 a los 12 años | percentil 69 |

**Lo que no cambió**, porque se calcula sobre el puntaje bruto, que es el que usa el clínico: la
posición percentilar del corte en cada tramo, el gradiente de señalamiento y todas las conclusiones
sobre el umbral de los 12 años.

### E. Consecuencia para la extensión a otros instrumentos

El hallazgo convierte la generalización en una **hipótesis previa** en vez de una exploración: si la
compresión la produce el techo de la escala, todo cribado acotado debe mostrarla, y **más cuanto más
bajo sea su techo**. El Mini-Mental, con 30 puntos frente a los 100 del ACE-III, debería mostrarla de
forma más marcada. Es contrastable y falsable.

<img src="file:///Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion/figuras/FiguraS_compresion.jpg" style="width:100%">

**Figura S-V26.** **(a)** Curva característica del test: ACE-III esperado en función de la habilidad
latente, con la posición media de cada tramo educativo. **(b)** Su pendiente, que decae hacia el techo.
**(c)** Desvío del puntaje bruto y de la habilidad por tramo; el primero se estrecha de forma monótona,
el segundo no.

---

## S — Puntaje esperado en el ACE-III según escolaridad y edad

> **Procedencia.** `codigo/F6_figura_equipo.py` → `tablas/EQUIPO_tabla_esperados_edad.csv`.
> Es la tabla completa que la Figura 2 del manuscrito reproduce sólo a los 65 años.

Cada celda: **puntaje esperado** en una persona sin deterioro y, entre paréntesis, el **percentil 5**.
Modelo de posición y dispersión estimado sobre los 342 controles comunitarios, promediado sobre la
distribución de sexo de la muestra y con la corrección de Harvey aplicada a la varianza. El corte
vigente es 68 hasta los 11 años de escolaridad y 86 desde los 12.

<img src="file:///Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion/figuras/Tabla3.jpg" style="width:100%">

**Lectura.** El corte de 68 supera al rendimiento esperado hasta los 4 años de escolaridad a los
65 años, y el de 86 vuelve a superarlo entre los 12 y los 15. En esos dos tramos la regla declara
anormal el rendimiento medio de una persona sin deterioro.

**Valores ilustrativos: no constituyen normas poblacionales.**
