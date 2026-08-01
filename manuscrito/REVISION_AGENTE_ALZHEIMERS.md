# Informe de revisión — *Alzheimer's & Dementia*

**Manuscrito:** «La corrección por escolaridad del ACE-III en la Argentina: el umbral de los 12 años
no se corresponde con ninguna discontinuidad, y una corrección continua reduce cinco veces el
gradiente educativo de falsos positivos»

**Revisor:** psicometría / epidemiología del deterioro cognitivo / equidad diagnóstica en baja
escolaridad
**Fecha:** 2026-08-01
**Material revisado:** `MANUSCRITO.md`, `SUPLEMENTARIO.md`, `Tabla1–3.md`, `REVISION_ALZHEIMERS_DEMENTIA.md`,
`resultados/*.json` (V1–V12 y salidas previas), `codigo/V4_tri_dif_metrica_latente.py`,
`codigo/V7_estandar_referencia.py`, `codigo/V12_equidad_definitiva.py`

---

## 1. Recomendación editorial

**Revisión mayor — no aceptable en su forma actual (rechazo con invitación a reenviar).**

Fundamento en una frase: la mitad «negativa» del trabajo (forma funcional, falsación del escalón,
procedencia documental) está bien ejecutada y es casi publicable, pero las dos afirmaciones que el
manuscrito eligió poner en el título y en el resumen —que el instrumento **no está sesgado** y que
una corrección continua **reduce cinco veces** el gradiente de falsos positivos— están, la primera,
contradicha por un análisis del propio estudio que no se reporta, y la segunda, apoyada en un grupo
control cuya definición no es reproducible desde los archivos depositados, cuyo umbral admite a la
mayoría de los pacientes con deterioro leve y cuya composición por cohorte no se informa.

---

## 2. Objeciones mayores

### M1. El umbral del criterio de control (reconocimiento ≥ 10/15) admite a la mayoría de los casos de deterioro leve, y eso es fatal para la palabra «falsos» en «falsos positivos»

**Qué está mal.** El material suplementario (V12) valida el criterio mostrando que el reconocimiento
«separa monótonamente los grupos clínicos: **13,25** sin deterioro · **10,93** deterioro leve · 8,55
moderado o severo». Pero el umbral elegido es **10**. Es decir: la media del grupo de deterioro leve
está *por encima del punto de corte que define «control»*. Por construcción, más de la mitad de los
pacientes con deterioro leve de la propia base clínica calificarían como controles.

**Por qué importa.** Toda la afirmación de equidad depende de que el 63,0 % de los controles de baja
escolaridad señalados por la regla vigente sean **falsos** positivos. Si el grupo control admite
deterioro leve por diseño —y en una región donde el manuscrito mismo cita una prevalencia de demencia
del 21,4 % entre personas sin educación formal—, señalar a esas personas puede ser detección
correcta. Esta es exactamente la objeción 1 de la revisión previa: el desenlace de deterioro leve se
eliminó, pero **el problema que ese desenlace hacía visible no se resolvió**; se le quitó el
instrumento de medición. La prueba está en el propio manuscrito: los controles comunitarios de baja
escolaridad promedian **65,5** puntos con el criterio nuevo, frente a **66,1** con el criterio
funcional descartado, y frente a **67,9** que promediaban los casos clínicos de deterioro leve del
mismo tramo. El cambio de criterio movió la media 0,6 puntos.

**Además, la limitación está declarada en la dirección equivocada.** Limitación tercera: «la memoria
de reconocimiento normal no excluye deterioro no amnésico, de modo que el grupo control puede
contener casos disejecutivos; **ello atenuaría —no exageraría— las diferencias observadas**». Es al
revés para el desenlace principal: la contaminación baja el ACE-III de los controles, aumenta la tasa
de señalamiento, y como la contaminación es mayor en baja escolaridad, **infla** el gradiente de 47,2
puntos. La afirmación de dirección es incorrecta y debe corregirse.

**Cambio concreto que pediría.**
1. Reportar la distribución completa del reconocimiento por cohorte y por tramo educativo, y la
   sensibilidad del resultado principal a umbrales 11, 12 y 13 (el umbral 13 sitúa el criterio por
   encima de la media del grupo de deterioro leve).
2. Justificar el umbral con una propiedad de validez (p. ej. valor predictivo negativo frente al
   juicio clínico en la cohorte clínica) y **no** con la ausencia de asociación con la exposición
   (ver M2).
3. Reescribir la limitación tercera con la dirección correcta del sesgo y cuantificarla: bajo qué
   prevalencia de deterioro no detectado en los controles de baja escolaridad se anula el gradiente
   observado (análisis de valor E o de sesgo cuantitativo).
4. Sustituir «falsos positivos» por «positivos entre quienes cumplen el criterio de control» en
   título, resumen y figuras.

---

### M2. El criterio de control se eligió por su ausencia de asociación con la exposición — y esa elección determina el resultado

**Qué está mal.** El umbral de 10 se justifica porque «es el único umbral en el que la condición de
control no depende del tramo educativo (χ² p = 0,198)». Es decir: entre todos los umbrales posibles
se seleccionó el que hace que la composición educativa del grupo control sea plana. Pero la
comparación de reglas mide precisamente cómo varía el señalamiento **por tramo educativo dentro del
grupo control**. Se está eligiendo la definición del denominador optimizando una propiedad del
denominador que condiciona directamente el desenlace.

**Por qué importa.** Es un grado de libertad analítico no prespecificado situado en el punto de mayor
apalancamiento del estudio. El manuscrito declara prespecificación para la prueba de discontinuidad y
para los márgenes de equivalencia, pero **no** para la definición de control, que es la decisión que
más influye en el resultado publicitado en el título.

**Cambio concreto.** Declarar explícitamente que el umbral se seleccionó *post hoc* sobre esa
propiedad; mostrar la curva completa del gradiente y de la razón de gradientes en función del umbral
de reconocimiento (barrido de 8 a 14); y trasladar la afirmación principal a la conclusión más débil
que sobreviva a todo el barrido.

---

### M3. El grupo control mezcla dos definiciones de «control» con distinto rigor, y la mezcla varía por tramo educativo: eso puede fabricar buena parte del gradiente de 47,2 puntos

**Qué está mal.** En `V12_equidad_definitiva.py` (líneas 60-63) los controles son la unión de:

- **comunitarios** con reconocimiento ≥ 10 — *un solo tamiz*, sin ninguna revisión diagnóstica; y
- **clínicos** con `dx3 == "Sin afectación"` **y** reconocimiento ≥ 10 — *doble tamiz*, incluido el
  juicio de un profesional que había visto el ACE-III.

Los 87 clínicos «sin afectación» tienen, según V6, una media de ACE-III de **92,5 (DE 4,3)**, mínimo
74, y **sólo 1 de 87 por debajo de 82**. Son un subgrupo supernormal. Los comunitarios de baja
escolaridad promedian 65,5. Si —como es esperable— los clínicos «sin afectación» se concentran en el
tramo de ≥12 años, entonces el estrato ≥12 del grupo control queda diluido con personas de puntaje ~92
que ninguna regla puede señalar, y el estrato <7 queda compuesto casi exclusivamente por comunitarios
sin tamiz diagnóstico. **El gradiente educativo del señalamiento entre controles se produce entonces,
en parte, por la composición del grupo control y no por la forma de la regla.**

Hay un indicio numérico directo de que algo no cierra: el manuscrito informa que los controles
comunitarios de ≥12 años promedian **86,0** puntos, exactamente el punto de corte de 86. Un grupo
cuya media coincide con el corte debería quedar señalado en torno al 50 % —más aún tras el
emparejamiento por edad, que selecciona a los mayores—. Se informa **30,3 %**. La diferencia sólo se
explica por la incorporación de los controles clínicos supernormales. El lector no puede verificarlo
porque **el manuscrito no informa cuántos controles vienen de cada cohorte, ni su distribución por
tramo educativo**.

**Por qué importa.** Es la objeción 2 de la revisión previa, no resuelta. El emparejamiento por edad
resolvió la confusión por edad, no la confusión por cohorte.

**Cambio concreto.**
1. Tabla obligatoria: controles por **cohorte × tramo educativo**, con media y DE del ACE-III en cada
   celda.
2. Análisis de sensibilidad restringido a **controles comunitarios únicamente** (definición
   homogénea), aunque cambie el n.
3. Análisis de sensibilidad restringido a **controles clínicos únicamente** frente a casos clínicos
   —la comparación de una sola puerta— aun con n reducido, tal como pidió la revisión previa y sigue
   sin aparecer.

---

### M4. La afirmación «el instrumento no está sesgado por escolaridad» está contradicha por un análisis del propio estudio que no se reporta

**Qué está mal.** El análisis de funcionamiento diferencial del ítem se corrió **sólo en la cohorte
comunitaria** (`V4_tri_dif_metrica_latente.py`: `dcom = D[D.cohorte == "comunitaria"]`, n focal 408).
En los resultados depositados existe la misma prueba en la **cohorte clínica**
(`resultados/03_replica_clinica.json`, n focal 567 / referencia 1362), y su resultado es distinto:

| Ítem | ΔR² ordinal (clínica) | Clase | MH delta (ETS) | Dirección |
|---|---|---|---|---|
| Lectura de palabras irregulares | **0,0523** | **moderado** | −3,006 | **C (grande)** | favorece alta escolaridad |
| Repetición de palabras | 0,0281 | pequeño | −1,753 | C (grande) | favorece alta escolaridad |
| Cubo | 0,0201 | pequeño | −1,658 | C (grande) | favorece alta escolaridad |
| Comprensión lectora | 0,0169 | pequeño | −3,089 | C (grande) | favorece alta escolaridad |
| Escritura | 0,0156 | pequeño | −1,871 | C (grande) | favorece alta escolaridad |

Trece ítems significativos tras control de tasa de falso descubrimiento, **uno con ΔR² por encima del
propio umbral de relevancia declarado (0,035)** y seis clasificados **C (grande)** por el criterio
Mantel-Haenszel de ETS, todos en la misma dirección: contra la baja escolaridad. El manuscrito afirma
en el título de sección, en el resumen, en la Tabla 3 y en la Conclusión: «**Ningún ítem presentó
funcionamiento diferencial no trivial**» y «Ítems con funcionamiento diferencial de magnitud no
trivial: **0 de 23**».

Agrava el problema que el suplemento **sí cita ese mismo archivo**, pero sólo las cifras
comunitarias: «Esto replica el análisis A2 previo (Lectura 0,0264 vs 0,0272 acá…)». Se cita la parte
del archivo que confirma y se omite la parte que contradice.

**Por qué importa.** (a) Es reporte selectivo de un resultado desfavorable, la falta más grave que
puede señalar un revisor. (b) Contradice el principio de diseño que el manuscrito declara como su
núcleo —«un resultado presente en ambas no puede atribuirse al mecanismo de selección de
ninguna»—: el resultado psicométrico se presenta a partir de **una sola** cohorte, y la otra no
replica. (c) El ítem discrepante es exactamente el que la teoría predice: lectura de palabras
irregulares, un ítem de alfabetización, en la cohorte con más personas de baja escolaridad reales.

**Cambio concreto.** Reportar el barrido de funcionamiento diferencial en **ambas** cohortes con el
método definitivo de V4, con la misma purificación y el mismo umbral, y reescribir la afirmación como
lo que los datos sostengan (previsiblemente: «un ítem de alfabetización muestra funcionamiento
diferencial de magnitud moderada en la cohorte clínica y despreciable en la comunitaria; el efecto
sobre el total sigue siendo <0,5 puntos»).

---

### M5. El método de funcionamiento diferencial no es el declarado, y el que se usó está sesgado hacia el nulo

Tres defectos en `V4_tri_dif_metrica_latente.py`, todos en la dirección de no encontrar sesgo:

1. **No es regresión logística ordinal.** El manuscrito y el suplemento dicen «Logística ordinal de
   Zumbo (método primario; la versión binaria es inestable en ítems de piso)». El código dicotomiza
   cada ítem en su categoría máxima —`y = (y >= y.max()).astype(int)`— y ajusta `smf.logit`. Es la
   versión **binaria**, precisamente la que el texto dice haber descartado. Es una descripción
   incorrecta de los métodos.
2. **El criterio de emparejamiento incluye el ítem en estudio.** `match = d[anchor_items].sum(axis=1)`
   con `anchor_items` = los 23 ítems. Zumbo exige puntaje **residual** (rest score). Incluir el ítem
   estudiado en el condicionante atenúa sistemáticamente el ΔR².
3. **La purificación es vacua.** El criterio de exclusión del anclaje es `q<0,05 **y** ΔR² ≥ 0,035`, el
   mismo umbral que define «relevante». Como ningún ítem lo alcanza, el ancla final tiene los 23 ítems
   (`anclaje_n = 23`): el procedimiento iterativo no puede, por construcción, retirar nada. Declarar
   «purificación iterativa del anclaje» sobreestima el rigor del procedimiento.

**Cambio concreto.** Reejecutar con logística **ordinal** real, con puntaje residual, y con
purificación basada en significación (no en tamaño de efecto). Reportar el ancla final. Si la
conclusión sobrevive, será mucho más creíble; si no sobrevive, hay que cambiarla.

---

### M6. El grupo focal del análisis de sesgo no es la población sobre la que trata el artículo

El contraste de funcionamiento diferencial —de ítem y de test— es **<12 vs ≥12 años**. Pero el
artículo trata de la baja escolaridad: el corte discutido es 68, el dato central es el de **<7 años**,
y la referencia teórica que estructura la Introducción (Arce Rentería) es sobre **analfabetismo**. El
grupo focal empleado agrupa a 249 personas de 7–11 años con 159 de <7 años, diluyendo justo donde el
sesgo debería estar.

Además, en ningún lugar del manuscrito aparece cuántos participantes tienen **0–3 años de
escolaridad** ni ninguna medida de alfabetización, pese a que la Figura 4 y el modelo normativo se
evalúan desde `edu = 0`.

**Cambio concreto.** (a) Repetir el barrido con grupo focal **<7 años** (y, si el n lo permite, ≤3
años), en ambas cohortes; (b) informar la distribución de escolaridad en 0–6 años y restringir el
trazado del modelo normativo al rango con soporte; (c) declarar que el estudio no midió
alfabetización funcional, lo que es una limitación central para la generalización a poblaciones
latinoamericanas de baja alfabetización.

---

### M7. Invarianza de medición: el modelo latente se calibró combinando dos cohortes que el propio manuscrito declara no invariantes

El manuscrito establece como regla metodológica que «**no se reporta en ningún caso una estimación
marginal combinada**» porque tres ítems de alfabetización no son invariantes entre cohortes. Sin
embargo:

- el modelo de respuesta graduada se estima sobre la **muestra combinada n = 2785** y θ se usa después
  como métrica común en ambas cohortes;
- la forma funcional por estrato de gravedad (−0,0655 / −0,0609 / −0,0696; interacción p = 0,961) se
  estima en `V7_estandar_referencia.py` sobre un conjunto que **funde las dos cohortes** (n = 2444; el
  estrato «Sin demencia» son 603 comunitarios más 87 clínicos).

Es una contradicción interna con la regla declarada. Además, no hay ninguna prueba **formal** de
invarianza de medición por escolaridad: DIF ítem a ítem no es equivalente a un contraste
configural / métrico / escalar. Para esta revista, la afirmación de invarianza requiere un modelo de
respuesta graduada multigrupo con contrastes anidados (o alineación), y las estimaciones de θ deberían
obtenerse por valores plausibles o máxima verosimilitud ponderada, no por valor esperado a posteriori,
cuya contracción hacia la media conjunta es no uniforme a lo largo de θ y puede por sí sola alterar la
curvatura estimada — que es exactamente el resultado que θ debía arbitrar.

**Cambio concreto.** Modelo multigrupo con prueba formal de invarianza por cohorte y por tramo
educativo; θ por valores plausibles; y reejecución de la curvatura latente sobre esa métrica.

---

### M8. La razón de gradientes de 4,8 no es el estimador puntual del estudio, y el remuestreo no propaga la incertidumbre del modelo normativo

**Qué está mal.**
1. Los gradientes informados son **47,2** y **6,3** puntos porcentuales. Su cociente es **7,4**, no
   4,8. El 4,8 es la **mediana bootstrap** del cociente. El manuscrito escribe «La razón entre
   gradientes fue de 4,8» sin advertirlo, y el lector que divida 47,2/6,3 obtendrá otro número. Hay
   que informar ambos y explicar cuál se usa.
2. El bootstrap (`V12`, líneas 123-133) remuestrea la tabla ya emparejada `E` **arrastrando la columna
   `z` ya calculada**: no reajusta el modelo normativo, no rehace la validación cruzada y no rehace el
   emparejamiento. Por tanto el intervalo 2,3–22,3 **subestima** la incertidumbre de la cantidad
   publicada.
3. El cociente se calcula como `rango_vig / max(rango_cont, 0.01)`, lo que trunca el denominador y
   genera colas artificiales —de ahí el límite superior de 22,3—.
4. El estadístico sigue siendo el **rango** (máximo menos mínimo de tres proporciones), exactamente lo
   que la revisión previa pidió reemplazar (objeción 6) por algo más estable, p. ej. la pendiente de la
   proporción señalada sobre los años de escolaridad. No se hizo.

**Cambio concreto.** Bootstrap del **procedimiento completo** (emparejamiento + ajuste del modelo
normativo + validación cruzada + umbralización); reemplazar el rango por la pendiente o por una
diferencia preespecificada <7 vs ≥12; informar el estimador puntual junto con la mediana bootstrap; y
retirar del título toda cifra cuyo intervalo abarque de 2,3 a 22,3.

---

### M9. Un único punto de operación, y además muy lejos de cualquier escenario clínico

La comparación se hace calibrando ambas reglas a la misma positividad global, que en la muestra
emparejada es **64,3 %** (382 de 594). Ninguna regla de cribado opera ahí. La revisión previa lo
señaló (objeción 5) y pidió curvas completas o al menos demostrar que el ordenamiento entre reglas se
mantiene en un rango de tasas de positividad.

Lo notable es que **el estudio hizo ese análisis** —`resultados/V11_corregido.json` contiene cinco
puntos de operación (20 %, 29 %, 40 %, 50 %, 59 %) con los gradientes de ambas reglas— pero (a) está
hecho con la definición **antigua** de control, y (b) **no aparece ni en el manuscrito ni en el
material suplementario**, que sólo dice de V11 «el efecto se atenúa; hace falta mejor criterio».

**Cambio concreto.** Repetir el barrido de puntos de operación con la definición definitiva de control
y publicarlo; añadir curvas de beneficio neto (*decision curve analysis*) estratificadas por tramo
educativo, que es la forma correcta de comparar reglas de decisión en esta revista.

---

### M10. La independencia de la clasificación de referencia respecto del ACE-III sigue afirmada más fuerte de lo que los datos permiten — y la mejor evidencia en contra fue retirada en lugar de discutida

El título de la sección de Métodos sigue diciendo «**Clasificación de referencia, construida sin el
ACE-III**», y el resumen «una clasificación **sin** el ACE-III». Lo demostrado es que ninguna de las
2750 oraciones clasificatorias **menciona** el ACE-III. No es lo mismo: el profesional que escribió la
conclusión administró la prueba.

La evidencia más directa de incorporación está en `V6_verificacion_dx.json` y **dentro de una sola
cohorte**, de modo que no puede atribuirse al diseño de dos puertas: el área bajo la curva del ACE-III
entre «sin afectación» y «demencia» **dentro de la cohorte clínica es 0,997**; los 87 rotulados sin
afectación tienen media 92,5 (DE 4,3) y **sólo 1 de 87 puntúa por debajo de 82**. Una separación
prácticamente perfecta entre etiquetas de informe usando el instrumento que supuestamente no
intervino en la etiqueta es, en esta revista, la definición operativa de sesgo de incorporación. La
revisión previa (objeción 3) pidió que ese 0,997 se presentara explícitamente como medida de la
magnitud del sesgo de diseño. En la versión actual **el número desapareció** del manuscrito y del
suplemento.

**Cambio concreto.** Reponer la cifra, presentarla como estimación de la incorporación residual,
cambiar el encabezado a «Clasificación de referencia construida **sin referencia explícita** al
ACE-III», y añadir a Limitaciones que la incorporación parcial es no cuantificable y probablemente
infla la sensibilidad de todas las reglas.

Añádase que la cobertura de la oración canónica es del **90,9 %** y que **difiere por tramo educativo**
(92,4 % · 93,9 % · 89,5 %; p = 0,006), igual que el enlace (98,4 % · 97,5 % · 96,3 %). Es decir, la
disponibilidad de la etiqueta de referencia depende de la exposición. No se menciona en el manuscrito.

---

### M11. El manuscrito declara que no reportará exactitud absoluta y la reporta

Métodos, sección «Alcance»: «Por eso **no se reporta exactitud absoluta**». Resultados: sensibilidad
0,943, especificidad 0,657, índice de Youden 0,599 y 0,626. Discusión: áreas bajo la curva de 0,855 y
0,957 por tramo educativo. Son medidas de exactitud absoluta.

Peor: **las áreas bajo la curva de la Discusión no provienen de la muestra del análisis principal.**
`V7_estandar_referencia.py` las calcula sobre el grupo control **descartado** —comunitarios sin
compromiso funcional en el ADLQ más los 87 clínicos—, sin emparejamiento por edad y fundiendo
cohortes. El manuscrito dedica un párrafo entero de Métodos y otro de Discusión a explicar por qué ese
criterio funcional era inutilizable («habría fabricado el resultado»), y a la vez apoya en él la
conclusión de que «ninguna elección de umbral iguala el desempeño entre tramos». No puede sostener las
dos cosas.

Por último, la afirmación de que en la comparación entre reglas «**el sesgo se cancela**» no está
justificada: el sesgo de espectro de un diseño de dos puertas no se cancela entre reglas cuya
dependencia de la escolaridad es distinta, que es justamente el contraste de interés.

**Cambio concreto.** (a) Recalcular las áreas bajo la curva por tramo sobre la muestra definitiva
(V12), emparejada y con el criterio de reconocimiento, o retirar la afirmación; (b) reemplazar «no se
reporta exactitud absoluta» por «las medidas de exactitud se reportan únicamente como cantidades
comparativas internas y no son transportables»; (c) eliminar «el sesgo se cancela» o demostrarlo.

---

### M12. Suficiencia del material suplementario: insuficiente para replicar la mitad que sostiene el título

1. **Faltan cinco de los doce bloques.** El índice lista V1–V12; el documento sólo desarrolla V1, V2,
   V3, V4, V6, V10 y V12. **V5, V7, V8, V9 y V11 no tienen sección**, y son precisamente los que
   sostienen la comparación de reglas.
2. **Las tres cifras más citadas del manuscrito no existen en ningún archivo de resultados.** `65,5`
   (con n = 131), `76,3` y `86,0` —las medias de ACE-III por tramo entre comunitarios con
   reconocimiento normal, en negrita en ambos resúmenes, en Resultados, en Discusión y en la
   Conclusión— **no aparecen en `resultados/`**, ni siquiera en `CIFRAS_MAESTRAS.json`, cuyo campo
   `_regla` dice: «Ninguna cifra del manuscrito puede provenir de otro archivo que éste». No hay
   script que las produzca.
3. **La selección del criterio de control no es reproducible.** La tabla de dependencia educativa de
   las siete pruebas (0,027 para reconocimiento, 0,088 Trail A, 0,111 IFS…), las medias por tramo
   12,2 · 12,2 · 12,8, la separación 13,25 · 10,93 · 8,55 y el χ² p = 0,198 del umbral existen
   **únicamente como comentario en el encabezado de `V12_equidad_definitiva.py`**. Ningún script las
   calcula y ningún JSON las contiene. Es la decisión analítica más consecuente del estudio.
4. **No se publican los coeficientes del modelo normativo continuo.** El manuscrito exige, en su
   propia Discusión, «publicar el modelo completo —coeficientes y no sólo tablas resumidas— es
   requisito para que sea utilizable y auditable». No lo hace. Ni siquiera se especifica su forma en el
   texto: es `ACE ~ edu + edu² + Edad + Sexo` para la media y `log(residuo²) ~ edu + Edad` para la
   dispersión (mínimos cuadrados en dos etapas), lo que **no** es el marco GAMLSS que se cita como
   referencia metodológica (ref. 22).
5. **El umbral de la regla continua se fija dentro de la misma muestra evaluada.** En `ev()`, el corte
   es el cuantil empírico de `z` en la muestra que se está evaluando (casos incluidos), calibrado a la
   positividad de la regla vigente. La validación cruzada de diez particiones se aplica al **modelo
   normativo** en los controles, no al **umbral**. Además, `z` de los controles es fuera de partición y
   `z` de los casos se calcula con el modelo ajustado sobre **todos** los controles: los dos brazos no
   reciben el mismo estimador. Hay que declararlo y, preferentemente, corregirlo.

**Cambio concreto.** Completar los bloques faltantes; depositar un script que produzca las cifras
65,5/76,3/86,0 y la selección del criterio de control; publicar los coeficientes del modelo normativo
(media y dispersión) con su matriz de covarianza; y describir la regla continua tal como está
implementada.

---

### M13. La equivalencia dentro de ±3 puntos descansa exclusivamente en el modelo paramétrico global; el diseño local no la sostiene, y hay amontonamiento *en el propio punto de corte*

El intervalo de ±3 proviene del indicador de discontinuidad estimado **condicionando en un polinomio
cuadrático global** de la escolaridad. Los diseños de regresión discontinua local, que son el estimador
apropiado, dan intervalos mucho más anchos: 10–13 años, +1,31 [−4,90; +7,52] y −2,50 [−8,67; +3,66].
Es decir, **el diseño local no puede descartar escalones de 6 a 8 puntos**. Afirmar «equivalencia
dentro de ±3 puntos» sin señalar que esa precisión proviene enteramente del modelo global, y no del
contraste local, es una sobreafirmación.

Adicionalmente, el 37,5 % y el 47,3 % de las cohortes declara exactamente 7, 12 o 17 años. **El corte
está exactamente sobre un valor de amontonamiento.** En regresión discontinua, el amontonamiento de la
variable de asignación en el umbral invalida la identificación estándar; el propio estudio muestra en
el corte de 7 años que el amontonamiento produce artefactos de magnitud −6,4 puntos. No hay prueba de
densidad (McCrary/Cattaneo), no hay selección de ancho de banda óptimo, no hay intervalos robustos
corregidos por sesgo, y no hay especificación tipo *donut*.

**Cambio concreto.** (a) Prueba de densidad en 12; (b) regresión discontinua con ancho de banda
óptimo e intervalos robustos; (c) especificación *donut* excluyendo el valor exacto 12; (d) reformular
la equivalencia como «dentro de ±3 puntos bajo la especificación global; el diseño local no descarta
escalones menores de ~7 puntos».

---

### M14. Los resultados depositados contienen un análisis que contradice la interpretación de la curvatura y no se reporta

`resultados/11_bateria_bruta.json` contiene tres cantidades relevantes y ausentes del manuscrito:

- la curvatura de la asociación escolaridad–rendimiento sobre el **compuesto de la batería
  neuropsicológica** es b₂ = **+0,00103 (p = 0,24)**: es decir, **sin rendimientos decrecientes**, con
  pendiente marginal que *aumenta* con la escolaridad (0,096 → 0,125 entre los años 3 y 17);
- el contraste formal indica que **la curvatura difiere entre instrumentos** (coef. 0,00201;
  IC 0,001–0,003; **p = 1×10⁻⁴**);
- el efecto de la escolaridad sobre el ACE-III **desaparece** al ajustar por el compuesto de la batería
  (b = −0,0018; IC −0,0077 a +0,0040; p = 0,54).

El tercer hallazgo **apoya** la tesis de ausencia de sesgo instrumental y debería reportarse: es la
mejor evidencia del manuscrito de que el gradiente educativo del ACE-III es gradiente de habilidad y no
de instrumento. Los dos primeros **desafían** la afirmación de que «los otros dos tercios [de la
curvatura] son propiedad de la cognición, no del instrumento», porque otra medida de la misma cognición
en las mismas personas no muestra rendimientos decrecientes.

**Cambio concreto.** Reportar los tres, y matizar la Discusión: la forma de rendimientos decrecientes
puede ser específica del ACE-III y no una propiedad general de la relación educación–cognición.

---

## 3. Objeciones menores

1. **Inconsistencia numérica en la Discusión.** «la regla vigente señala a **cuatro de cada diez**
   personas sin deterioro cuando tienen baja escolaridad». El resultado es 63,0 % (Resultados y
   Conclusión: «63 %»), y en la cohorte comunitaria completa 56,0 %. Ningún análisis da 40 %. Parece
   una cifra sobreviviente de una versión anterior.

2. **Tabla 3A no coincide con el texto.** El texto dice «nueve alcanzaron significación». La tabla
   muestra ocho filas, de las cuales sólo **siete** son significativas (incluye Registro de 3 palabras,
   q = 0,219) y **omite dos que sí lo son** (Cubo, q = 0,039; Recuerdo diferido de nombre y dirección,
   q = 0,029). El suplemento V4-D muestra una tercera selección, de siete filas. Unificar y mostrar los
   23 ítems en el suplemento.

3. **La dirección del sesgo de fluencia semántica cambia de signo entre corridas archivadas**:
   `03_replica_clinica.json` (comunidad) la clasifica «favorece alta escolaridad»; `V4b_dif_ordinal.json`
   (β = +0,247) la clasifica «favorece baja escolaridad», y es la versión que llega a Tabla 3 y al
   relato de «sesgos bidireccionales que se compensan». Verificar y unificar la convención de signo.

4. **El resumen sobreafirma el resultado del placebo.** «de catorce cortes fue el menos discontinuo».
   Es el puesto 14 de 14 sólo en la cohorte comunitaria; en la clínica es el 12 de 14. Corregir a «el
   menos discontinuo en la cohorte comunitaria y entre los tres menos discontinuos en la clínica».

5. **«Regresión robusta» en el resumen** describe errores estándar robustos a heterocedasticidad, no
   estimación robusta. Cambiar a «errores estándar robustos».

6. **El intervalo del error estándar de medición se omite.** Se informa «entre 6,2 y 8,4 puntos» (rango
   entre métodos), pero el intervalo formal de la estimación extrapolada es **[1,93; 12,21]**
   (`V2b_testretest.json`), que el propio suplemento reconoce como «ancho y así debe declararse». Con
   ese intervalo, «2,2 errores de medición» podría ser entre 1,5 y 9,3. Debe llevar su incertidumbre.

7. **La fiabilidad test-retest no es fiabilidad.** Intervalo mediano de 560 días en una cohorte con
   enfermedad progresiva; el coeficiente de correlación intraclase de 0,727 es estabilidad, no
   consistencia. Está bien declarado en el suplemento, pero la Tabla 3C lo presenta sin ese matiz.

8. **Las proporciones por tramo no llevan intervalo.** 63,0 % sobre n = 73, 15,9 % sobre n = 82 y
   30,3 % sobre n = 142. La «inversión» del gradiente (7–11 menos señalado que ≥12) es un argumento
   central y descansa en 13/82 frente a 43/142. Añadir intervalos exactos.

9. **«1 de 16» como denominador de una cifra destacada.** El salto 6,2 % → 52,7 % entre 11 y 12 años
   usa n = 16 en el año 11, que además es el mínimo de toda la serie año a año (los años 9 y 10 dan
   17,1 % y 12,0 %). Presentar el contraste agrupando 10–11 frente a 12–13 sería más estable.

10. **«sin que mediara cambio alguno en el rendimiento»** es incorrecto: la diferencia cruda 11 vs 12
    años es +3,29 puntos [−0,39; +6,98]. Decir «sin un cambio detectable».

11. **Frase confusa en Resultados:** «el tramo intermedio resulta el menos señalado pese a ser el de
    menor escolaridad entre los alfabetizados». El tramo <7 tiene menor escolaridad y también está
    mayoritariamente alfabetizado. Reescribir.

12. **Unidimensionalidad e independencia local: evidencia insuficiente para esta revista.** Razón entre
    autovalores 5,75 y 35,8 % de varianza en el primer componente son criterios mínimos; el segundo y
    tercer autovalores superan 1. Se pide índice de varianza común explicada (bifactor) o índices de
    ajuste de un modelo confirmatorio, y estadísticos de ajuste del modelo de respuesta graduada (M2 o
    S-X²), ausentes por completo. Los dos pares con Q₃ > 0,20 (máximo 0,348) se declaran
    «estructuralmente esperables» pero **no se nombran**: hay que nombrarlos.

13. **Métodos incompletos sobre el emparejamiento.** Estratos quinquenales, una única extracción con
    semilla fija, sin sensibilidad a la extracción ni a la anchura del estrato.

14. **STARD declarado pero no implementado** (objeción 8 de la revisión previa): faltan el diagrama de
    flujo de la muestra diagnóstica (sólo hay flujo de la cohorte comunitaria), la declaración de
    cegamiento entre índice y referencia, las tablas 2×2 y los intervalos de todas las medidas de
    exactitud.

15. **Título.** Mejoró mucho respecto de la versión previa, pero (a) sigue conteniendo un estimador
    puntual —«cinco veces»— cuyo intervalo va de 2,3 a 22,3; (b) «falsos positivos» prejuzga la
    validez del grupo control (M1); (c) el diseño (transversal, dos cohortes) sólo aparece en el título
    corto. Sugerencia: «El umbral de 12 años de escolaridad del ACE-III no se corresponde con una
    discontinuidad del rendimiento, y una corrección continua atenúa el gradiente educativo del
    señalamiento: estudio transversal en dos cohortes de San Juan, Argentina».

16. **Generalización.** Una provincia; cohorte comunitaria con 81 % de mujeres y reclutamiento por
    convocatoria abierta; sin medida de calidad educativa ni de alfabetización; sin datos de ruralidad
    ni de lengua. La octava limitación lo menciona de pasada. Para una revista que exige explicitar la
    transportabilidad a poblaciones latinoamericanas, hace falta un párrafo específico que diga qué
    parte del hallazgo se espera transportable (la ausencia de discontinuidad en 12 años, propiedad de
    la regla) y cuál no (las magnitudes de señalamiento, propiedades de esta muestra).

17. **Declaraciones incompletas:** número de palabras «[COMPLETAR]», comité y acta de la cohorte
    clínica «[NÚMERO Y FECHA]», financiamiento y autores sin completar, y la advertencia interna
    «⚠ Verificar cada referencia contra el original antes del envío» todavía dentro del manuscrito.
    Ninguna referencia fue verificable en esta revisión; varias (12, 21, 23, 30, 31, 37) carecen de
    volumen o páginas y una está fechada en 2026.

18. **`README.md` del proyecto está desactualizado** y contradice al manuscrito: «**No hay estándar de
    referencia diagnóstico.** No se estima exactitud diagnóstica… Se exploraron las medidas disponibles
    y ninguna sirve como criterio». Si acompaña al repositorio público, hay que actualizarlo.

---

## 4. Estado de las objeciones de la revisión previa

| # | Objeción previa | Estado | Evidencia en la versión actual |
|---|---|---|---|
| 1 | Los controles de baja escolaridad no son controles; retirar el desenlace de deterioro leve | **Parcialmente resuelta / abierta en lo esencial** | Resuelto: el desenlace leve se eliminó y el suplemento documenta por qué; se añadió emparejamiento por edad y restricción al rango común. **Abierto:** el nuevo criterio (reconocimiento ≥10) admite a la mayoría de los casos de deterioro leve (media del grupo leve = 10,93), la media de los controles de baja escolaridad apenas se movió (66,1 → **65,5**) y la limitación declara la dirección del sesgo al revés (M1) |
| 2 | Confusión casi perfecta entre cohorte y condición de caso | **Parcialmente resuelta** | Resuelto el componente de edad (69,7 vs 69,5). **Abierto:** el 100 % de los casos sigue viniendo de la clínica; no se informa la composición por cohorte de los 297 controles; no se presenta el análisis restringido a controles clínicos que la revisión pidió explícitamente (M3) |
| 3 | El área bajo la curva de 0,997 es señal de alarma, debe presentarse como magnitud del sesgo de diseño | **No resuelta** | La cifra fue **retirada** en lugar de presentada. `V6_verificacion_dx.json` la conserva (0,997; 1 de 87 rotulados sin afectación con ACE < 82) y es intracohorte, es decir, evidencia de incorporación y no de dos puertas (M10) |
| 4 | «Construido sin emplear el ACE-III» es demasiado fuerte; usar «clasificación de referencia» | **Parcialmente resuelta** | Resuelto lo terminológico: se dice «clasificación de referencia» y se declara que no es diagnóstico etiológico ni DSM-5/NIA-AA. **Abierto:** el encabezado de Métodos sigue siendo «construida sin el ACE-III» y el resumen «una clasificación sin el ACE-III» (M10) |
| 5 | Un único punto de operación arbitrario; se piden curvas completas | **No resuelta** | Sigue habiendo un solo punto, ahora a 64,3 % de positividad. El barrido existe en `V11_corregido.json` (5 puntos) pero con el criterio antiguo y **no aparece** en el manuscrito ni en el suplemento (M9) |
| 6 | «Once veces» sin incertidumbre; reemplazar el rango por un estadístico estable | **Parcialmente resuelta** | Muy bien resuelto lo principal: hay intervalos por remuestreo y la magnitud se corrigió honestamente de 11× a **4,8** (2,3–22,3), y el suplemento documenta la atenuación. **Abierto:** el estadístico sigue siendo el rango; el bootstrap no reajusta el modelo normativo; y 47,2/6,3 = **7,4** ≠ 4,8 sin explicación (M8) |
| 7 | Optimismo no corregido en los cortes óptimos (57, 64, 78) | **Resuelta** | Retirados del manuscrito; permanecen sólo en `V7_estandar_referencia.json` |
| 8 | Guía de reporte: corresponde STARD | **Parcialmente resuelta** | STARD se declara ahora en Declaraciones, pero no se implementa ninguno de sus elementos (menor 14) |
| 9 | El título | **Parcialmente resuelta** | Resuelto: fuera la construcción «no es si… sino cómo», fuera «iguala el desempeño diagnóstico», fuera «inequidad». **Abierto:** estimador puntual en el título con intervalo 2,3–22,3, «falsos positivos» prejuzga el grupo control, y el diseño sólo figura en el título corto (menor 15) |
| 10 | Solapamiento de muestras entre análisis | **Resuelta** | Limitación séptima: «los participantes comunitarios contribuyen tanto a la estimación de la forma funcional como al grupo control» |

**Objeción nueva de esta revisión que no existía en la anterior:** el reporte selectivo del
funcionamiento diferencial del ítem (M4). Es, con diferencia, el problema más grave de la versión
actual.

---

## 5. Errores fácticos e inconsistencias numéricas verificadas contra los resultados

| # | Afirmación del manuscrito | Lo que dicen los resultados | Gravedad |
|---|---|---|---|
| 1 | «Ningún ítem presentó funcionamiento diferencial no trivial»; «0 de 23» | Cierto en la cohorte comunitaria (`V4b_dif_ordinal.json`). En la clínica, `03_replica_clinica.json` da Lectura de palabras irregulares ΔR² = **0,0523** («moderado», por encima del umbral 0,035 del propio estudio), MH delta −3,006, clase **C (grande)**, y 13 ítems significativos | **Crítica** |
| 2 | «Logística ordinal de Zumbo (método primario; la versión binaria es inestable…)» | `V4_tri_dif_metrica_latente.py` dicotomiza el ítem en su categoría máxima y ajusta `smf.logit`: es la versión **binaria** | **Crítica** |
| 3 | «con purificación iterativa del anclaje» | El ancla final tiene **23 de 23** ítems (`anclaje_n = 23`): el criterio de exclusión exige ΔR² ≥ 0,035, que ningún ítem alcanza; la purificación no puede retirar nada | Mayor |
| 4 | «La razón entre gradientes fue de 4,8» | 47,16 / 6,35 = **7,43**. El 4,8 es la mediana bootstrap. Las dos cifras deben coexistir en el texto | Mayor |
| 5 | «Las personas de la comunidad con <7 años y reconocimiento normal promediaron 65,5 puntos (n = 131)»; «76,3»; «86,0» | **No figuran en ningún archivo de `resultados/`**, ni en `CIFRAS_MAESTRAS.json`, ni existe script que las produzca | Mayor |
| 6 | «La memoria de reconocimiento resultó la única prácticamente independiente de la escolaridad (0,027…); umbral de 10 puntos (χ² p = 0,198); separa 13,25 · 10,93 · 8,55» | Existe **sólo como comentario** en el encabezado de `V12_equidad_definitiva.py`; ningún script lo calcula, ningún JSON lo contiene | Mayor |
| 7 | «la regla vigente señala a **cuatro de cada diez** personas sin deterioro cuando tienen baja escolaridad» (Discusión) | 63,0 % en la muestra emparejada; 56,0 % en la cohorte comunitaria; 50,4 % con la definición antigua. La Conclusión del propio manuscrito dice **63 %** | Mayor |
| 8 | «no se reporta exactitud absoluta» | Se reportan sensibilidad 0,943, especificidad 0,657, Youden 0,599/0,626 y áreas bajo la curva 0,855/0,935/0,957 | Mayor |
| 9 | «Su capacidad discriminativa… 0,855 con menos de 7 años frente a 0,957 con 12 o más» | Provienen de `V7`, calculadas sobre el grupo control **descartado** (ADLQ + clínicos sin afectación), sin emparejar y fundiendo cohortes; no sobre la muestra V12 del resultado principal | Mayor |
| 10 | «La forma no difiere entre estratos de gravedad (−0,0655, −0,0609, −0,0696; p = 0,961)» | `V7`, sobre un conjunto que **funde ambas cohortes** (n = 2444; el estrato «Sin demencia» = 603 comunitarios + 87 clínicos), contra la regla declarada de no producir estimaciones combinadas | Mayor |
| 11 | «no se reporta ninguna estimación marginal combinada» | El modelo de respuesta graduada se calibra sobre **n = 2785 combinados** pese a los tres ítems no invariantes; θ se usa después como métrica común | Moderada |
| 12 | «error estándar de medición entre 6,2 y 8,4 puntos» → «2,2 errores de medición» | El intervalo de la estimación extrapolada es **[1,93; 12,21]** (`V2b_testretest.json`); el propio suplemento lo reconoce «ancho» | Moderada |
| 13 | Tabla 3A: ocho ítems, texto: «nueve alcanzaron significación» | Nueve significativos en `V4b` (q < 0,05); la tabla muestra siete de ellos, incluye uno no significativo (Registro, q = 0,219) y omite dos significativos (Cubo 0,039; Recuerdo NyD 0,029) | Moderada |
| 14 | «de catorce cortes fue el menos discontinuo» (resumen) | Puesto 14/14 sólo en la comunitaria; 12/14 en la clínica | Menor |
| 15 | «sin que mediara cambio alguno en el rendimiento» (11 vs 12 años) | Diferencia cruda +3,29 puntos [−0,39; +6,98] | Menor |
| 16 | Curvatura clínica «−0,0784» con coincidencia hasta el cuarto decimal | Con n = 2112 (`V2`) es −0,0784; con la submuestra de 23 ítems completos, n = 2027 (`V4`), es **−0,0694** [−0,0960; −0,0429]. La coincidencia no es estable a la muestra; conviene decirlo al declararla fortuita | Menor |
| 17 | «Cambio mínimo detectable (95 %) ±23,1 puntos» (suplemento) vs `cmd95 = 22,6` (JSON) | Discrepancia sin explicar (probablemente crudo vs extrapolado); etiquetar cada una | Menor |
| 18 | Comparación de excluidos «los 90 excluidos tenían más escolaridad (12,0 frente a 10,3)» | La comparación de `V3`/`CIFRAS_MAESTRAS` usa n = 108 excluidos (90 por datos faltantes + 18 por solapamiento), con n = 65 para escolaridad y n = 56 para ACE-III. Precisar los denominadores | Menor |
| 19 | Resultados analizados con datos posteriores a `CIFRAS_MAESTRAS.json` | El archivo declara «Ninguna cifra del manuscrito puede provenir de otro archivo que éste» y sólo contiene V1–V4; todo el análisis de equidad (V6–V12) lo incumple. Actualizar la fuente única | Menor |

---

## 6. Fortalezas

Son reales y quiero dejarlas registradas, porque el manuscrito tiene un núcleo publicable.

1. **La falsación de la discontinuidad en 12 años está muy bien hecha.** Indicador sobre la forma
   continua, regresión discontinua local en tres ventanas y dos cohortes, prueba de equivalencia con
   márgenes preespecificados y anclados en un cambio mínimo clínicamente importante publicado, y
   **prueba de placebo sobre los catorce cortes candidatos**. El diseño convierte correctamente
   «no encontramos» en «no está», dentro de los límites que señalo en M13.

2. **El placebo demuestra su propia sensibilidad.** Que el procedimiento detecte el artefacto de
   amontonamiento en 7 años —con réplica en cuatro ventanas locales, ausencia de réplica en la otra
   cohorte y explicación mecanística por credencial— y aun así no encuentre nada en 12 es un
   argumento metodológicamente elegante y poco habitual.

3. **El diseño de dos cohortes con selección opuesta** es la mejor idea del trabajo. Que la curvatura
   coincida hasta el cuarto decimal entre una cohorte comunitaria de 63 años y una clínica de 73 es un
   resultado difícil de explicar por selección.

4. **La reconstrucción documental de la procedencia de la regla (Tabla 1)** es original, verificable y
   de interés directo para la práctica regional. Es, probablemente, la contribución más duradera del
   manuscrito. La declaración de conflicto de intereses de D.B. es ejemplar.

5. **El anclaje del escalón de 18 puntos en unidades del instrumento** (error de medición, cambio
   mínimo clínicamente importante) es la forma correcta de dimensionar una regla de decisión, y no la
   había visto aplicada a esta discusión.

6. **La honestidad del material suplementario.** La sección «Los tres hallazgos que obligaron a cambiar
   conclusiones» —incluido el reconocimiento de que el efecto de equidad cayó de 11× a 1,8 con
   intervalo que incluía la unidad antes de recuperarse con otro criterio— es una práctica que esta
   revista debería premiar. Las bitácoras V1–V4, con los dos defectos de procesamiento documentados
   (cero a la izquierda en el documento, `dayfirst` sobre fechas ISO) y las reglas que dejan
   establecidas, son de una calidad superior a la habitual.

7. **La observación de que el propio cuestionario funcional presenta gradiente educativo en subescalas
   específicas** (empleo −0,265, comunicación −0,160, tecnología −0,154) es un hallazgo lateral valioso
   que merece publicación propia y que cualquier estudio de equidad diagnóstica en la región debería
   tener en cuenta.

8. **La distinción conceptual central** —funcionamiento diferencial (el test mide igual a igual
   habilidad) frente a desplazamiento de la distribución de la habilidad (la escolaridad mueve dónde
   están las personas)— está formulada con precisión y reconcilia correctamente los hallazgos con la
   literatura que desaconseja el ajuste demográfico. Es el mejor párrafo del manuscrito.

---

## 7. Camino recomendado

Mantengo la recomendación estructural de la revisión previa, porque los hechos nuevos la refuerzan:

**Manuscrito A (casi listo).** Forma funcional, falsación de la discontinuidad con las correcciones de
M13, funcionamiento diferencial **reportado en ambas cohortes** (M4, M5, M6) y procedencia documental.
No necesita clasificación de referencia ni grupo control, y su mensaje ya es completo y útil: *el
umbral de los 12 años no se corresponde con ninguna discontinuidad observable y el sesgo de medición
del total es de fracciones de punto frente a una corrección de 18*.

**Manuscrito B (requiere trabajo sustancial).** La comparación de reglas: definición de control
justificada por validez y no por neutralidad frente a la exposición, composición por cohorte declarada
y analizada, barrido de puntos de operación o curvas de beneficio neto, remuestreo del procedimiento
completo, modelo normativo publicado con sus coeficientes, y reporte STARD.

Si los autores insisten en un único manuscrito para el concurso, la condición mínima para que yo
apoyara su consideración es: corregir M4 y M5 (el reporte del funcionamiento diferencial), aportar la
tabla de composición del grupo control de M3, resolver las inconsistencias 4, 5, 6, 7, 8, 9 y 10 de la
sección 5, y **degradar la afirmación de equidad de conclusión principal a resultado secundario y
explícitamente exploratorio**, con el título reformulado en consecuencia.
