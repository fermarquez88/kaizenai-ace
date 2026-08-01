# Registro de correcciones tras la auditoría externa

> Dos revisores independientes —perspectiva *Neurology* y perspectiva *Alzheimer's & Dementia*—
> auditaron el manuscrito y el material suplementario. Este registro documenta cada objeción, su
> verificación y la corrección aplicada. Informes completos en `REVISION_AGENTE_NEUROLOGY.md` y
> `REVISION_AGENTE_ALZHEIMERS.md`.

---

## Objeciones críticas: verificadas y corregidas

### C1. Reporte selectivo del funcionamiento diferencial del ítem

**Objeción.** El manuscrito afirmaba «ningún ítem presentó funcionamiento diferencial de magnitud no
trivial (0 de 23)». Esa cifra provenía **sólo de la cohorte comunitaria**. El análisis en la cohorte
clínica ya existía en `resultados/03_replica_clinica.json`.

**Verificación.** Confirmada. En la cohorte clínica (n focal 567, referencia 1362):

| Ítem | ΔR² ordinal | Efecto | Clase ETS | Dirección |
|---|---|---|---|---|
| Lectura de palabras irregulares | **0,0523** | **moderado** | **C (grande)** | alta escolaridad |
| Repetición de palabras | 0,0281 | despreciable | C (grande) | alta escolaridad |
| Copia del cubo | 0,0201 | despreciable | C (grande) | alta escolaridad |
| Orientación en tiempo | 0,0179 | despreciable | C (grande) | **baja escolaridad** |
| Comprensión lectora | 0,0169 | despreciable | C (grande) | alta escolaridad |
| Escritura | 0,0156 | despreciable | C (grande) | alta escolaridad |

Trece ítems significativos tras corrección por tasa de falso descubrimiento. La lectura de palabras
irregulares **supera el umbral de relevancia de 0,035 que el propio estudio declara**.

**Corrección.** Se reportan ambas cohortes. La afirmación pasa de «el instrumento no presenta sesgo»
a: **existe funcionamiento diferencial a nivel de ítem, con un ítem de magnitud moderada en la
cohorte clínica; los sesgos son bidireccionales y se compensan al agregarse, de modo que el sesgo del
puntaje total permanece entre 0,08 y 0,34 puntos**. Esa compensación —no la ausencia de sesgo— es el
resultado, y es coherente con la revisión sistemática que muestra mayor sesgo educativo en ítems de
lectura, escritura y visoconstrucción.

### C2. «Replicó entre cohortes» era incorrecto

**Objeción.** El test conjunto de igualdad de forma entre cohortes **rechaza**.

**Verificación.** Confirmada en `resultados/V2_reproduccion.json`:

| Contraste | χ² | gl | p |
|---|---|---|---|
| Forma completa (conjunta) | 13,40 | 2 | **0,0012 — rechaza** |
| Componente lineal | 13,31 | 1 | **0,00026 — rechaza** |
| Curvatura | 0,09 | 1 | 0,764 — no rechaza |

**Corrección.** Se afirma únicamente que **replica la curvatura**, se reporta el test conjunto con su
p, y se explicita que las cohortes difieren en el componente lineal —lo esperable dado que una tiene
diez años más y seis puntos menos de rendimiento medio—.

### C3. La planitud del gradiente es una identidad algebraica

**Objeción.** La corrección continua tipifica respecto de una media **y una varianza** estimadas como
función de la escolaridad dentro de los propios controles. Señalar bajo un cuantil fijo de esa
tipificación produce equidistribución **por construcción**; la validación cruzada no lo evita porque
no es un problema de sobreajuste sino de definición.

**Verificación.** Correcta.

**Corrección.** Se elimina la razón entre gradientes como resultado. Se reportan dos cantidades
distintas: **(a)** el gradiente que produce la regla vigente, que es empírico —44,0 puntos
porcentuales, IC 95 % 30,9 a 57,7—, y **(b)** si eliminarlo cuesta desempeño diagnóstico, que es la
pregunta con contenido empírico —diferencia de índice de Youden +0,022, IC 95 % −0,022 a +0,074—. La
planitud residual de 4,0 se declara explícitamente como esperada por construcción.

### C4. Composición del grupo control desbalanceada por tramo educativo

**Objeción.** Los controles mezclaban participantes comunitarios con un solo tamiz y clínicos con
doble tamiz, y la proporción variaba con la exposición: 0,8 % de clínicos en el tramo de menos de 7
años frente al **20,2 %** en el de 12 o más, con medias de ACE-III de 65,5 y 93,0 respectivamente.

**Verificación.** Confirmada.

**Corrección.** El grupo control pasa a ser de **fuente única**: sólo participantes de la cohorte
comunitaria, todos con el mismo criterio. Nueva composición: 78, 80 y 112 controles por tramo. El
análisis se rehízo íntegramente (`V13_equidad_corregida.py`).

### C5. El umbral del criterio de control no excluye deterioro leve

**Objeción.** Con reconocimiento ≥10 el **72,2 %** de los casos de deterioro leve calificaría como
control (media del grupo leve: 10,93).

**Verificación.** Confirmada.

**Corrección.** Se declara explícitamente en Métodos y Limitaciones, y se agrega **análisis de
sensibilidad sobre cuatro umbrales**, con la disyuntiva declarada: umbrales más estrictos excluyen
más deterioro leve (de 72,2 % a 36,6 %) pero introducen dependencia educativa (p pasa de 0,198 a
0,001). El gradiente de la regla vigente se mantiene entre 28,9 y 44,0 en los cuatro, y la diferencia
de Youden entre +0,019 y +0,042.

### C6. Dirección del sesgo de contaminación declarada al revés

**Objeción.** El manuscrito afirmaba que la contaminación del grupo control «atenuaría —no
exageraría— las diferencias observadas». Es al revés: si los controles de baja escolaridad contienen
deterioro no detectado, señalarlos no es un falso positivo, de modo que la contaminación **infla** el
gradiente medido.

**Verificación.** Correcta.

**Corrección.** Se invierte la declaración y se convierte en limitación principal.

---

## Objeciones mayores corregidas

| # | Objeción | Corrección |
|---|---|---|
| M1 | La definición de controles se eligió después de ver los resultados; las versiones nulas sólo estaban en el suplemento | Se declara la secuencia completa en Métodos y Limitaciones, con las tres estimaciones sucesivas y sus intervalos |
| M2 | La razón publicada (4,8) era la mediana bootstrap; el valor directo es 7,43, sin declararlo | Se elimina la razón; se reportan los gradientes con sus intervalos |
| M3 | El área bajo la curva de 0,997 se presentaba como validación de la etiqueta | Se reformula como **firma del sesgo de diseño de dos puertas**, con las cifras publicadas del ACE-III (0,86–0,94) como referencia |
| M4 | Faltaba el flujo de participantes de la cohorte clínica (2242 → 2112) | Agregado a Resultados y a la Tabla 2 |
| M5 | No se declaraba el punto de operación de la comparación | Declarado: 66 % de positividad, y se explicita que es un punto de comparación, no un escenario clínico |
| M6 | Resultados de V7 nunca mencionados: cortes óptimos empíricos y superioridad de la regla vigente sobre el corte único | Ambos incorporados |
| M7 | No se declaraba la clase de evidencia | Declarada **Clase IV** para el objetivo de comparación de reglas |
| M8 | Referencias 26–37 sin citar en el texto | Depuradas |
| M9 | Inconsistencia «cuatro de cada diez» frente a «63 %» | Unificado a la cifra corregida |
| M10 | El método declarado (logística ordinal) no coincidía con el implementado en un script | Se usa y se declara el análisis ordinal; el binario queda como contraste en el suplemento |

---

## Objeciones aceptadas y declaradas como limitación

Cuatro señalamientos son correctos y no admiten corrección con los datos disponibles. Se incorporan
como limitaciones explícitas:

1. **Diseño de dos puertas** con confusión casi completa entre cohorte y condición de caso.
2. **La clasificación de referencia no es independiente del índice**: el mismo profesional administró
   el ACE-III y redactó la conclusión. Que ninguna oración clasificatoria lo mencione no equivale a
   que no lo haya empleado.
3. **El criterio de control es unidimensional** y no excluye deterioro no amnésico ni deterioro leve.
4. **La contaminación del grupo control infla el gradiente medido**, de modo que 44 puntos
   porcentuales es un límite superior.

---

## Lo que la auditoría dejó intacto

Ninguno de los dos revisores objetó: la forma funcional con rendimientos decrecientes; la falsación
de la discontinuidad con prueba de equivalencia y prueba de placebo sobre los catorce cortes; la
reconstrucción documental de la procedencia de la regla; la verificación de unidimensionalidad e
independencia local; el error estándar de medición; ni el hallazgo de que las personas sin deterioro
con menos de 7 años de escolaridad promedian 65,5 puntos, por debajo del corte de 68.
