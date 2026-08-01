# Informe de revisión por pares

**Revista:** *Neurology* (American Academy of Neurology) — revisión aplicada a un manuscrito enviado
al concurso de premio del Congreso Argentino de Neurología 2026.
**Manuscrito:** «La corrección por escolaridad del ACE-III en la Argentina: el umbral de los 12 años
no se corresponde con ninguna discontinuidad, y una corrección continua reduce cinco veces el
gradiente educativo de falsos positivos».
**Revisor:** neurología cognitiva / metodología.
**Material revisado:** `MANUSCRITO.md`, `SUPLEMENTARIO.md`, `Tabla1–3.md`, `resultados/V1–V12*.json`,
`codigo/V12_equidad_definitiva.py`, `verificacion/`.

---

## 1. Recomendación editorial

### **REVISIÓN MAYOR** — condicionada.

El trabajo contiene un hallazgo de primer orden y bien ejecutado (la falsación empírica del umbral de
12 años, con prueba de equivalencia, placebo sobre los catorce cortes y réplica en dos cohortes de
selección opuesta), pero la segunda mitad del manuscrito —la que da título, resumen y conclusión— se
apoya en una comparación cuyo resultado principal **es en gran medida una consecuencia aritmética del
procedimiento de ajuste**, obtenida además tras una secuencia de decisiones dependientes de los datos
que el manuscrito no declara y que el propio material suplementario documenta. Tal como está, la
sección de equidad no puede publicarse en *Neurology*.

**Condición explícita:** si en la revisión los autores no pueden (a) desmontar la circularidad de la
Objeción M1, (b) reportar íntegramente el árbol de decisiones de la definición de controles (M2) y
(c) corregir la afirmación de réplica (M3), mi recomendación pasa a **rechazo**, con invitación a
reenviar un manuscrito centrado exclusivamente en la falsación del umbral, que sí es publicable.

**Clasificación del nivel de evidencia (requisito de *Neurology*).** El manuscrito no incluye la
declaración obligatoria de clase de evidencia. Para el objetivo 4 (comparación de reglas frente a una
clasificación de referencia) el diseño es un **caso–control de dos puertas**, con controles de una
fuente distinta a la de los casos, muestreo no consecutivo, clasificación de referencia emitida por el
mismo profesional que administró el test índice y sin cegamiento declarado: **Clase IV**. Esto debe
figurar en el resumen estructurado y debe limitar explícitamente lo que las conclusiones pueden
afirmar. Los objetivos 1 a 3 no son preguntas diagnósticas y deben presentarse como análisis
observacional transversal, sin clase de evidencia pero con la advertencia STROBE correspondiente.

---

## 2. Objeciones mayores

---

### M1. La reducción del gradiente de 47,2 a 6,3 puntos porcentuales es, en su mayor parte, una identidad algebraica, no un hallazgo empírico

**Qué está mal.** En `codigo/V12_equidad_definitiva.py` (líneas 78–97) la «corrección continua» se
construye así:

```python
REF = E[E.y == 0]                                  # SOLO los controles
FP  = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
def norma(tr_, ap):
    mu = smf.ols(FP, data=tr_).fit()               # media esperada por escolaridad
    sd = smf.ols("lr2 ~ edu + Edad", ...)           # dispersión esperada por escolaridad
    return (ap.ACE - mu.predict(ap)) / np.sqrt(np.exp(sd.predict(ap)))
```

Es decir: `z` es el residuo estudentizado del puntaje respecto de una media **y una varianza
estimadas dentro del propio grupo control como funciones de la escolaridad**. Por construcción, `z`
tiene media ≈ 0 y varianza ≈ 1 **en cada nivel de escolaridad entre los controles**. Cuando después se
señala a todo el que queda por debajo de un cuantil fijo de `z` (línea 102), la proporción de
controles señalados es necesariamente aproximadamente igual en todos los tramos educativos. **El
gradiente de 6,3 puntos porcentuales no es una estimación de nada: es el ruido de muestreo que sobra
después de haber impuesto la planitud.** La validación cruzada de diez particiones protege contra el
sobreajuste de la media condicional; **no** anula la tautología, porque la planitud no proviene del
sobreajuste sino de la definición del estimando.

**Por qué importa.** El título, el resumen, la conclusión y la recomendación práctica del manuscrito
descansan sobre la razón 4,8. Un lector de *Neurology* leerá «una corrección continua reduce cinco
veces la desigualdad de trato» como un resultado empírico comparativo. No lo es. El único contenido
empírico genuino de este análisis es lo que el manuscrito trata como secundario: **que aplanar el
gradiente no costó sensibilidad** (0,943 → 0,956) **ni índice de Youden** (0,599 → 0,626).

**Cambio que pido.**
1. Eliminar la razón de gradientes del título, del resumen y de la conclusión.
2. Reescribir el párrafo de Métodos «Comparación de reglas» agregando, textualmente:
   > «La corrección continua estandariza el puntaje respecto de la media y la dispersión esperadas en
   > los controles como función de la escolaridad. En consecuencia, **la uniformidad de la tasa de
   > señalamiento entre tramos educativos en los controles es una propiedad construida del
   > procedimiento y no un resultado del análisis.** El gradiente residual de la regla continua
   > cuantifica únicamente el error de muestreo y la mala especificación del modelo. La cantidad
   > informativa de esta comparación es, por lo tanto, **cuánto se aparta la regla vigente de una
   > regla educativamente neutra a igual tasa de positividad, y a qué costo diagnóstico.**»
3. Reescribir el resultado de equidad como una cantidad de una sola regla, con su intervalo:
   > «A igual tasa de positividad, la regla vigente señaló al 63,0 % de los controles con <7 años de
   > escolaridad, al 15,9 % de los de 7 a 11 y al 30,3 % de los de ≥12 (gradiente 47,2 puntos
   > porcentuales; IC 95 % 32,9 a 59,8). Una regla educativamente neutra por construcción alcanzó la
   > misma sensibilidad (0,956 frente a 0,943) y el mismo índice de Youden (diferencia +0,027; IC 95 %
   > −0,013 a +0,074), lo que indica que la desigualdad de trato de la regla vigente **no es el precio
   > de su rendimiento diagnóstico**.»
   Esta última frase sí es un hallazgo, es defendible y es la que hay que llevar al título.

---

### M2. La definición de controles fue elegida después de ver los resultados, y las definiciones alternativas —que dan resultados nulos— están en el suplemento pero no en el manuscrito

**Qué está mal.** El propio suplemento lo documenta con encomiable franqueza (sección «Los tres
hallazgos que obligaron a cambiar conclusiones», punto 3):

> «La primera estimación daba una reducción de once veces… Con emparejamiento por edad e intervalos
> por remuestreo, la razón cayó a **1,8 con intervalo que incluía la unidad**. El hallazgo sólo se
> recuperó al redefinir los controles con un criterio cognitivo ciego a la escolaridad (V12), donde la
> razón fue de 4,8.»

Los archivos lo confirman:

| Bloque | Definición de controles | Razón de gradientes | IC 95 % |
|---|---|---|---|
| `V8_correccion_continua.json` | funcional (sin compromiso) | 30,6 / 2,7 = **11,3** | no reportado |
| `V11_corregido.json` | funcional + emparejado por edad + bootstrap | **1,8** | **0,50 a 8,05 (incluye 1)** |
| `V12_equidad_definitiva.json` | reconocimiento de lista ≥10 | **4,8** | 2,3 a 22,3 |

A esto se suma que el umbral del criterio finalmente adoptado se eligió **por su resultado sobre la
propia variable que determina el hallazgo**: el manuscrito dice que 10 puntos es «el umbral en el que
la condición de control no depende del tramo educativo (χ² p = 0,198)». Elegir el punto de corte del
criterio de control para maximizar la no significación de su asociación con la exposición es una
decisión dependiente de los datos aplicada exactamente sobre el eje del resultado.

**Por qué importa.** Tres capas de selección dependiente de los datos (definición de control ensayada
cinco veces, umbral elegido por su p, y estimando que es plano por construcción) convergen sobre el
número que da título al trabajo. Un manuscrito que no declara esto en el cuerpo no es evaluable. Es
además incompatible con la sección «Prespecificación y multiplicidad», que hoy da a entender que sólo
«±3 y las sensibilidades» fueron exploratorios.

**Cambio que pido.**
1. Añadir al final de la sección «Controles» de Métodos:
   > «La definición de controles no estaba prespecificada. Se ensayaron cinco definiciones basadas en
   > el cuestionario funcional (material suplementario V10), ninguna de las cuales separó a los
   > controles de baja escolaridad de los casos de deterioro leve. Con la definición funcional y
   > emparejamiento por edad, la razón entre gradientes fue de 1,8 (IC 95 % 0,50 a 8,05). La
   > definición finalmente adoptada —memoria de reconocimiento de lista— se seleccionó tras esos
   > análisis, y su umbral (10 puntos) se eligió por ser el valor en el que la condición de control no
   > se asociaba al tramo educativo. **Todo el análisis de equidad debe leerse, por lo tanto, como
   > exploratorio y generador de hipótesis.**»
2. Incorporar la tabla de arriba como tabla suplementaria citada desde el cuerpo.
3. Marcar el objetivo 4 como exploratorio en la lista de Objetivos de la Introducción.
4. Sustituir el χ² p = 0,198 por una **prueba de equivalencia** sobre la asociación entre condición de
   control y tramo educativo. Los autores exigen TOST para el escalón de 12 años; deben exigírselo a
   sí mismos aquí. Un p = 0,198 no es evidencia de neutralidad educativa del criterio.

---

### M3. «Replicó entre cohortes» es incorrecto: la prueba formal de igualdad de forma la rechaza

**Qué está mal.** El manuscrito afirma en el resumen («replicó entre cohortes»), en la Discusión
(«replicada en cohortes de selección opuesta») y en la Conclusión («una forma que se reproduce entre
cohortes»). Lo que muestra `resultados/V2_reproduccion.json` es:

```
/replicacion/forma/p     = 0,0012      ← test conjunto de los términos educativos: RECHAZA la igualdad
/replicacion/lineal/p    = 0,00026     ← el componente lineal difiere entre cohortes
/replicacion/curvatura/p = 0,764       ← sólo la curvatura replica
/replicacion/contraste_b2 = +0,0064 [−0,0307; +0,0435]
```

El manuscrito reporta únicamente el contraste de b₂ y omite el test conjunto. **Lo que replica es la
curvatura, no la forma.** Las pendientes marginales lo dejan ver: 2,92 / 2,30 / 1,51 / 0,73 en la
comunitaria frente a 3,31 / 2,68 / 1,90 / 1,11 en la clínica — la clínica está desplazada hacia arriba
en toda la escala.

**Por qué importa.** La réplica en cohortes de selección opuesta es el argumento de validez interna
central del trabajo («un resultado presente en ambas no puede atribuirse al mecanismo de selección de
ninguna»). Sostenerlo sobre una prueba que se omitió y que rechaza es un defecto de reporte grave, no
un matiz.

**Cambio que pido.** Reemplazar en Resultados por:
> «El contraste formal de los términos educativos entre cohortes rechazó la igualdad de la forma
> completa (p = 0,0012), a expensas del componente lineal (p = 0,0003): la cohorte clínica rinde por
> encima en toda la escala. **La curvatura, en cambio, sí replicó** (contraste +0,0064; IC 95 % −0,0307
> a +0,0435; p = 0,73), que es el parámetro relevante para la pregunta de este trabajo.»
Y corregir en consecuencia el resumen, la Discusión y la Conclusión: se replicó la **curvatura**, no
«la forma».

---

### M4. La «razón 4,8» no es la estimación puntual del estudio, sino la mediana de la distribución bootstrap; el estimando en sí está mal comportado

**Qué está mal.** En `V12_equidad_definitiva.py` línea 146: `"razon": float(np.median(bs[:, 2]))`. La
razón calculada sobre los datos observados es **47,16 / 6,35 = 7,43**, no 4,8. Reportar la mediana
bootstrap como si fuera la estimación puntual, junto a un IC percentil, sin declararlo, no es
aceptable; y la distancia entre 7,4 y 4,8 es en sí misma el diagnóstico de que el estadístico es
fuertemente sesgado y asimétrico. Se confirma con el intervalo: **2,3 a 22,3**, un rango de un orden de
magnitud.

Tres problemas adicionales del estimando:
- El «gradiente» es **max − min de tres proporciones**, un estadístico de rango: sesgado hacia arriba,
  no monótono y con varianza dominada por el tramo más pequeño (n = 73 en <7 años).
- El denominador se acota artificialmente en `max(rango_cont, 0.01)` (línea 129), lo que trunca la cola
  del cociente de forma arbitraria y hace el IC superior no interpretable.
- El emparejamiento por edad se ejecuta **una sola vez con semilla fija** (líneas 70–73) y el bootstrap
  remuestrea la muestra ya emparejada: **la incertidumbre del sorteo de emparejamiento no se propaga**.

**Por qué importa.** El «cinco veces» del título es un número que ni corresponde a la estimación
puntual ni tiene una precisión que permita afirmar «cinco».

**Cambio que pido.**
1. Sustituir el estimando por una **interacción formal** en un modelo único sobre los controles:
   `señalado ~ regla × tramo educativo` con errores agrupados por sujeto, y reportar la razón de
   probabilidades de la interacción con su IC. Es interpretable, tiene un modelo detrás y admite
   prueba de multiplicidad.
2. Si se conserva el bootstrap, declarar explícitamente qué se reporta («mediana bootstrap») o —mejor—
   reportar la estimación plug-in con IC corregido por sesgo y aceleración (BCa), y **rehacer el
   emparejamiento dentro de cada réplica**.
3. Reportar además el análisis de sensibilidad ya existente en `V11_corregido.json`, que muestra que el
   gradiente y la razón dependen fuertemente del punto de operación (a 20 % de positividad: 6,2 frente
   a 1,9; a 50 %: 23,0 frente a 9,9).

---

### M5. El grupo control no es independiente del ACE-III, y Métodos lo describe de un modo que no coincide con el código

**Qué está mal.** Métodos dice: «Se definió como control a quien obtuvo 10 puntos o más» en memoria de
reconocimiento, y encabeza la sección «Clasificación de referencia, **construida sin el ACE-III**». El
código (líneas 60–63) muestra que los controles son la unión de:

```python
M[M.rec >= UMB]                                              # comunitarios: sólo reconocimiento
dx3[(dx3.dx3 == "Sin afectación") & (dx3.rec >= UMB)]        # clínicos: reconocimiento Y etiqueta del informe
```

Los controles clínicos requieren además la etiqueta «Sin afectación» del informe. Y esa etiqueta,
según `V6_verificacion_dx.json`, corresponde a un grupo de 87 personas con **ACE-III medio 92,5,
mínimo 74, y sólo 1 de 87 por debajo de 82**, con **AUC 0,997 frente al grupo «Demencia»**.

**Por qué importa.** Un AUC de 0,997 entre la etiqueta narrativa y el test índice no es «validación
independiente» —así lo presenta el suplemento V6— sino **la firma característica del sesgo de
incorporación**: es aritméticamente muy improbable que un juicio clínico verdaderamente independiente
del ACE-III separe al ACE-III casi perfectamente. Que la oración clasificatoria no *mencione* el
ACE-III (0 de 2750) demuestra ausencia de mención, no ausencia de uso, y el propio manuscrito lo
admite en la Limitación segunda; pero entonces no puede a la vez titular la sección «construida sin el
ACE-III». Además, ese subgrupo entra en el grupo control del análisis de equidad, donde su altísimo
rendimiento en el ACE-III infla la especificidad de ambas reglas.

**Cambio que pido.**
1. Cambiar el encabezado de la sección a **«Clasificación de referencia, construida sin recurrir al
   puntaje del ACE-III»** y describir el criterio de control tal como está implementado, con las dos
   ramas explícitas y el n de cada una.
2. Reportar, para el grupo control, la composición por fuente (comunitaria / clínica) y por tramo
   educativo, y el ACE-III medio de cada rama.
3. Añadir en Limitaciones:
   > «Los controles de origen clínico se identificaron por la etiqueta “sin afectación” del informe,
   > emitida por el mismo profesional que administró el ACE-III. Ese subgrupo presenta un ACE-III
   > medio de 92,5 puntos y se separa del grupo con deterioro moderado o severo con un AUC de 0,997,
   > cifra compatible con incorporación del test índice en el juicio clínico. La especificidad de
   > ambas reglas está en consecuencia sobreestimada, y las comparaciones sólo son válidas entre
   > reglas sobre la misma muestra.»
4. Análisis de sensibilidad obligatorio: repetir V12 **excluyendo los controles clínicos**, sólo con
   controles comunitarios. Si el resultado sobrevive, es un argumento fuerte; si no, hay que decirlo.

---

### M6. La dirección declarada del sesgo por contaminación del grupo control es, con alta probabilidad, la contraria

**Qué está mal.** Limitación tercera: «La memoria de reconocimiento normal no excluye deterioro no
amnésico… ello **atenuaría —no exageraría—** las diferencias observadas.» No se ofrece justificación, y
el razonamiento no se sostiene: si el grupo control contiene casos verdaderos no detectados por el
criterio de reconocimiento, y esa contaminación es **mayor en el tramo de baja escolaridad** —lo que es
esperable, porque el propio manuscrito cita una prevalencia de demencia de 21,4 % sin educación formal
frente a 9,9 % con ella⁵—, entonces parte del 63,0 % de «controles» de <7 años señalados por la regla
vigente son **verdaderos positivos**, y el gradiente de 47,2 puntos está **inflado**, no atenuado.

Lo mismo afecta al dato más citado del trabajo: los 65,5 puntos medios de los controles comunitarios
de <7 años. Si ese grupo está contaminado, la media está deprimida por casos reales y la afirmación «el
corte de 68 clasifica como anormal el rendimiento normal de baja escolaridad» pierde apoyo.

Agravante: el umbral de 10 sobre 15 en reconocimiento de lista es un criterio **débil** para «ausencia
de deterioro». No se informa el nivel de azar de la tarea, ni la desviación estándar por tramo, ni qué
proporción de la cohorte comunitaria queda excluida por él.

**Por qué importa.** Es la explicación alternativa principal de todo el bloque de equidad y hoy está
descartada por afirmación, no por argumento ni por dato.

**Cambio que pido.**
1. Sustituir la Limitación tercera por:
   > «El criterio de control es unidimensional y de umbral bajo. Si contiene casos verdaderos no
   > amnésicos, y si esa contaminación es mayor en el tramo de menor escolaridad —esperable dada la
   > mayor prevalencia de deterioro en ese tramo—, el gradiente atribuido a la regla vigente estaría
   > **sobreestimado**. No podemos descartar esta explicación con los datos disponibles.»
2. Añadir un análisis de sesgo cuantitativo: recalcular el gradiente bajo escenarios plausibles de
   contaminación diferencial (p. ej. 5 %, 10 %, 20 % de casos verdaderos entre los controles de <7 años
   y la mitad de esas cifras en ≥12) y reportar a partir de qué nivel de contaminación el hallazgo
   desaparece. Es un análisis de diez líneas de código y es lo que decide la credibilidad del trabajo.
3. Reportar nivel de azar, media, DE y n del reconocimiento por tramo educativo y por cohorte.

---

### M7. Resultados relevantes que contradicen o matizan el mensaje están en los archivos y no en el manuscrito

**Qué está mal.** `resultados/V7_estandar_referencia.json` contiene dos resultados que el manuscrito no
menciona en ninguna parte:

| Hallazgo en V7 | Cifra | ¿Aparece en el manuscrito? |
|---|---|---|
| Corte óptimo por tramo frente a la clasificación de referencia | **57** (<7), **64** (7–11), **78** (≥12) | **No** |
| Regla vigente 86/68 frente a corte único calibrado | Youden **0,628** frente a **0,497** (corte 82) y **0,394** (corte 86) | **No** |

El primero muestra que **ambos** cortes vigentes están demasiado altos —incluido el 86 en el tramo de
alta escolaridad (78 óptimo; IC 75–79)—, lo que reencuadra el problema: no es sólo la *forma* de la
corrección, es también su *nivel*. El segundo muestra que la regla vigente, por arbitraria que sea su
procedencia documental, **supera a un corte único calibrado**, que es la alternativa que un lector
consideraría primero. El índice del suplemento lo dice en una línea («V7 | La regla vigente supera al
corte único») y el cuerpo no lo recoge.

**Por qué importa.** Omitir del cuerpo el resultado que más matiza la tesis es reporte selectivo, y en
este caso además debilita al manuscrito: reconocer que la regla vigente mejora a un corte único
refuerza el argumento de que la discusión es «no si corregir sino cómo», que es precisamente la tesis
de los autores.

**Cambio que pido.** Añadir a Resultados una subsección breve:
> «Frente a la misma clasificación de referencia, la regla vigente superó a cualquier corte único
> calibrado (índice de Youden 0,628 frente a 0,497 con corte 82 y 0,394 con corte 86): corregir por
> escolaridad mejora el rendimiento respecto de no corregir. Sin embargo, los cortes empíricamente
> óptimos por tramo fueron 57 (<7 años), 64 (7–11) y 78 (≥12), de modo que **ambos cortes vigentes
> están situados por encima de su óptimo, también en el tramo de mayor escolaridad**. Estos valores no
> constituyen una propuesta normativa —provienen de un diseño de dos puertas— pero indican que el
> problema de la regla vigente no es sólo su forma escalonada sino también su nivel.»

---

### M8. «Sin perder desempeño» y «sin costo diagnóstico» son conclusiones de no inferioridad sin margen de no inferioridad — el doble estándar inferencial del propio manuscrito

**Qué está mal.** El manuscrito hace, con razón, una defensa explícita de la diferencia entre ausencia
de evidencia y evidencia de ausencia («**evidencia de ausencia**, no ausencia de evidencia») y aplica
TOST al escalón de 12 años. Después, para el desempeño diagnóstico, concluye «sin perder desempeño»
(resumen), «El desempeño diagnóstico no se resintió» (Resultados), «sin costo diagnóstico» (Discusión y
Conclusión) a partir de una diferencia de Youden de **+0,027 con IC 95 % −0,013 a +0,074**, es decir un
intervalo que contiene el cero y que admite una pérdida de hasta 0,013. Es exactamente la falacia que
el propio texto denuncia dos páginas antes.

**Por qué importa.** «Sin costo» es la afirmación que hace de la propuesta algo accionable. Sin margen
prespecificado, no está sostenida.

**Cambio que pido.**
1. Prespecificar (y declarar como *post hoc* si se especifica ahora) un margen de no inferioridad
   sobre el índice de Youden —sugiero Δ = 0,05, justificándolo— y aplicar TOST, igual que para el
   escalón.
2. Mientras tanto, sustituir en los cuatro lugares por:
   > «sin diferencia detectable en el índice de Youden (diferencia +0,027; IC 95 % −0,013 a +0,074).
   > El intervalo es compatible con una pérdida de hasta 0,013, de modo que **no puede concluirse
   > formalmente no inferioridad**.»
3. Eliminar del resumen «sin perder desempeño» y del título/conclusión «sin costo».

---

### M9. La comparación «18 puntos frente a 0,08–0,34 puntos de sesgo» es una confusión de categorías que contradice el argumento central de la propia Discusión

**Qué está mal.** Resultados afirma: «La regla corrige esa diferencia con **18 puntos**, unas 2,2 veces
el error estándar de medición». El suplemento V4 lo amplifica: «La regla vigente corrige esa diferencia
con 18 puntos: **entre 50 y 200 veces el sesgo que existe**». Pero la Discusión sostiene —correctamente—
que la corrección **no** existe para corregir funcionamiento diferencial sino para compensar el
desplazamiento de la distribución de habilidad. Si eso es cierto, el DTF de 0,08–0,34 puntos **no es el
referente contra el cual medir los 18 puntos**, y la comparación no significa nada.

Segundo problema, técnico: el DTF se estima regresando el puntaje total sobre θ y θ², donde θ fue
estimado **a partir de esos mismos ítems** (r = 0,980 con el bruto; R² del modelo 0,983–0,985). Es casi
una identidad; el «sesgo residual» que queda es en buena parte el error de estimación de θ, no una
propiedad del instrumento. Presentarlo como «la estimación del sesgo residual es precisa» porque el
modelo explica el 98,5 % de la varianza invierte el argumento: ese 98,5 % es la señal de la
circularidad, no de la precisión.

**Cambio que pido.**
1. Eliminar del manuscrito y del suplemento toda comparación numérica entre los 18 puntos y el DTF
   («2,2 veces el EEM» en ese contexto, «entre 50 y 200 veces el sesgo que existe»).
2. Reformular el resultado de DTF:
   > «A igual habilidad latente estimada por el propio modelo, la diferencia del total entre tramos
   > educativos fue de +0,08 puntos (−0,22 a +0,38) en la comunitaria y +0,34 (+0,08 a +0,59) en la
   > clínica. Dado que θ se estima a partir de los mismos ítems, esta cantidad debe leerse como una
   > cota superior de la magnitud del sesgo detectable con este diseño, no como una estimación
   > insesgada del funcionamiento diferencial del test.»
3. Conservar la escala de referencia del EEM sólo donde sí corresponde: para dimensionar el escalón de
   18 puntos frente al ruido del instrumento, con la incertidumbre completa (ver M10).
4. Corregir además la afirmación del resumen «el instrumento no está sesgado»: en la cohorte clínica el
   DTF **es estadísticamente significativo** (+0,34; IC 0,08 a 0,59; p = 0,009). La redacción correcta
   es «detectable pero de magnitud clínicamente despreciable».

---

### M10. Afirmaciones cuantitativas centrales sin ninguna medida de incertidumbre

*Neurology* exige intervalo o error estándar en toda afirmación cuantitativa. Faltan en, al menos, los
siguientes lugares —todos ellos titulares del trabajo:

| Afirmación | Dónde | Qué falta |
|---|---|---|
| «promediaron **65,5 puntos** (n = 131)… por debajo del corte de 68»; 76,3 y 86,0 | Resumen, Resultados, Discusión, Conclusión | DE e **IC 95 %**. Con DE ≈ 13 el IC sería aproximadamente 63,3 a 67,7: el límite superior roza el 68. La afirmación puede seguir siendo válida, pero debe mostrarse. |
| «pasó de **6,2 % (1 de 16)** a **52,7 %** entre los 11 y los 12 años» | Resultados | IC de una proporción con **n = 16** (IC exacto ≈ 0,2 % a 30,2 %). Presentar un salto de 8,4× con denominador 16 y sin intervalo es indefendible. |
| «unas **2,2 errores de medición**» y «**3,6 veces** el cambio mínimo clínicamente importante» | Resultados, Tabla 3C | El EEM formal es 8,15 con **IC 95 % 1,93 a 12,21** (`V2b_testretest.json`): el escalón equivale a entre **1,5 y 9,3 EEM**. Además, con el rango declarado de 6,2–8,4 el cociente es 2,1–2,9, no 2,2. |
| «capacidad discriminativa 0,855 frente a 0,957» | Discusión | Los IC existen en `V7` (0,800–0,901 y 0,938–0,967) y deben citarse, además de identificar la muestra (ver M11). |
| «el techo explica **un tercio** del efecto» | Resultados | Es un tercio de la **curvatura estandarizada**, sin intervalo. Debe decirse así y, si es posible, con IC. |
| Pendientes 2,9 → 0,7 | Resumen | Los IC existen (2,43–3,42 y 0,47–0,99). Al menos el del extremo. |

**Cambio que pido.** Añadir IC a las seis. Y en el caso de la comparación 11 frente a 12 años,
sustituir el par de porcentajes por la diferencia cruda ya calculada, que sí tiene intervalo: **+3,29
puntos (IC 95 % −0,39 a +6,98)** en la comunitaria y **+1,82 (−2,32 a +5,97)** en la clínica.

---

### M11. Cifras del manuscrito que provienen de análisis distintos, con muestras y clasificaciones de referencia distintas, presentados como si fueran el mismo

**Qué está mal.** El manuscrito describe **una** clasificación de referencia (casos = deterioro
moderado o severo del informe; controles = reconocimiento ≥10, emparejados). Pero las cifras de la
Discusión «capacidad discriminativa 0,855 con <7 años frente a 0,957 con ≥12» provienen de
`V7_estandar_referencia.json`, que usa **otra** definición de control (etiqueta «Sin demencia» del
informe, sin criterio de reconocimiento y sin emparejamiento; n = 121 / 207 / 362). El lector no tiene
forma de saberlo. Lo mismo ocurre con la curvatura por estrato de gravedad (−0,0655 / −0,0609 /
−0,0696, interacción p = 0,961), también de V7 y también sobre otra muestra.

Análogamente, el resumen atribuye al «Modelo de respuesta graduada (n = 2785)» tanto la métrica latente
**como el funcionamiento diferencial**, pero el DIF de ítem corrió sobre **n = 758** (focal 408,
referencia 350) y **sólo en la cohorte comunitaria**: en la clínica no se testeó DIF de ítem en
absoluto.

**Por qué importa.** Es un requisito básico de STARD/STROBE que cada estimación identifique su
población analítica. Aquí además cambia la interpretación: la conclusión general «el ACE-III no
presenta sesgo de medición por escolaridad» se apoya en un análisis realizado en una sola cohorte, con
408 sujetos en el grupo focal, sin réplica.

**Cambio que pido.**
1. Añadir a cada estimación del cuerpo el n y la definición de muestra («cohorte comunitaria, n = 758»,
   «muestra clínica con clasificación de referencia del informe, n = 690 controles»…).
2. Corregir el resumen: «Modelo de respuesta graduada (n = 2785) para la métrica latente; el
   funcionamiento diferencial del ítem se evaluó en la cohorte comunitaria (n = 758; grupo focal 408).»
3. Añadir a Limitaciones: «El funcionamiento diferencial del ítem no se evaluó en la cohorte clínica;
   la conclusión de ausencia de sesgo de ítem no está replicada.»
4. Resolver la incoherencia interna del modelo psicométrico: se ajusta un **único** modelo de respuesta
   graduada sobre las dos cohortes combinadas (n = 2785) para obtener una métrica común, y al mismo
   tiempo se declara que **tres ítems no son invariantes entre cohortes** y que por eso no se reporta
   ninguna estimación marginal combinada. Ambas cosas no pueden sostenerse a la vez. O se estima con
   parámetros parcialmente libres (invarianza parcial) o se justifica por qué la no invarianza de tres
   ítems no compromete la métrica común. Como mínimo, sensibilidad excluyendo esos tres ítems.

---

### M12. Guías de reporte: faltan elementos obligatorios de STROBE y prácticamente todo STARD

**Qué falta, en orden de gravedad:**

1. **No hay flujo de participantes de la cohorte clínica.** V1 informa 2242 personas en la base
   definitiva; el análisis usa 2112. **Los 130 excluidos no aparecen en ningún lado**, ni el motivo, ni
   la comparación incluidos/excluidos. La Tabla 2 sólo trae el flujo comunitario. STROBE 13a.
2. **No hay diagrama de flujo STARD** para la comparación de reglas: cuántas personas tenían medida de
   reconocimiento disponible, cuántos casos y controles elegibles antes del emparejamiento, cuántos se
   perdieron por el rango común de edad, cuántos por el emparejamiento 1:1. Hoy sólo se sabe el
   resultado final (297 + 297).
3. **No hay declaración de cegamiento** entre el test índice y la clasificación de referencia
   (STARD 10–11). Es imposible aquí, y por eso mismo debe declararse expresamente.
4. **No se declara el punto de operación.** Métodos dice «Ambas reglas se calibraron a la misma tasa de
   positividad» sin decir cuál. Del código y de las cifras se deduce ≈ **64 %** de positividad global en
   la muestra emparejada. Una tasa de positividad del 64 % no es un punto de operación de cribado
   realista y condiciona por completo la magnitud del gradiente (V11 muestra gradientes de 6,2 a 23,0
   según el punto elegido). Debe declararse en Métodos y acompañarse del análisis a otros puntos.
5. **Ética incompleta.** El comité, el número de acta y la fecha de la cohorte clínica están en blanco
   (`[COMITÉ]`, `[NÚMERO Y FECHA]`). El manuscrito no es evaluable ni publicable así.
6. **Disponibilidad de datos y código** sin URL ni DOI ni condiciones de acceso.
7. **Sin registro ni protocolo con fecha.** Dado el volumen de análisis exploratorios documentado en el
   suplemento, la ausencia de un plan de análisis fechado es material.
8. Campos en blanco: número de palabras del cuerpo, financiamiento, autores y afiliaciones.
9. **Las figuras 1 a 4 no se aportaron** para la revisión. No puedo evaluar la correspondencia entre
   figuras y texto ni la afirmación «Ningún dato se presenta simultáneamente en tabla y figura».

---

### M13. Sobreafirmación y precisión terminológica en título, resumen y conclusiones

1. **Título.** Excede con holgura el límite de *Neurology*, contiene **dos conclusiones declarativas** y
   una **estimación puntual sin incertidumbre** («reduce cinco veces») que además no es la estimación
   puntual del estudio (M4) y que es en parte tautológica (M1). Y llama **«falsos positivos»** a
   personas clasificadas como sin deterioro por un umbral en una única prueba de reconocimiento: sin
   estándar de referencia diagnóstico, no hay falsos positivos, hay **señalamientos discordantes con el
   criterio de control**.
   **Título propuesto:**
   > «El umbral de 12 años de escolaridad del ACE-III en la Argentina no se corresponde con ninguna
   > discontinuidad: dos cohortes de selección opuesta»
   con subtítulo o segunda oración en el resumen para la parte de equidad.
2. **«personas cognitivamente normales»** (Conclusión) y «personas sin deterioro» (Discusión):
   sustituir sistemáticamente por **«personas con memoria de reconocimiento de lista preservada»**. Es
   lo único que el dato sostiene.
3. **«concentra casi cinco veces más deterioro grave»** (Resultados, Participantes): la cifra
   subyacente es el porcentaje con **ACE-III ≤ 40** (7,5 % frente a 1,6 %), es decir una banda de
   puntaje, no una categoría de gravedad clínica. Este es exactamente el error terminológico que hay
   que evitar en neurología cognitiva. Además, **la Tabla 2 no contiene esa fila**, de modo que el
   texto afirma algo que la tabla no muestra. Reescribir: «y una proporción cinco veces mayor de
   puntajes muy bajos (ACE-III ≤ 40: 7,5 % frente a 1,6 %)», y añadir la fila a la Tabla 2.
4. **«dos administraciones sucesivas del test»** (Resultados, escala de referencia): el intervalo
   mediano entre administraciones es de **560 días** en una cohorte con enfermedad progresiva. No es
   test-retest en sentido estricto y el suplemento lo reconoce. Reescribir: «un salto mayor que la
   variabilidad observada entre dos administraciones separadas por una mediana de 560 días, que mezcla
   error de medición y cambio verdadero».
5. **«evidencia de ausencia»** para el escalón: aquí sí está justificado y es una de las mejores partes
   del trabajo. Pero el resumen presenta la equivalencia dentro de ±3 puntos como resultado principal
   («con equivalencia dentro de ±3 puntos») cuando Métodos declara ese margen **exploratorio**. Llevar
   al resumen el margen prespecificado (±5, anclado en el cambio mínimo clínicamente importante) y
   dejar el de ±3 en Resultados con la etiqueta de exploratorio.
6. **«de catorce cortes fue el menos discontinuo»** (resumen) y «con el corte en uso último entre
   catorce» (Discusión): sólo es cierto en la cohorte comunitaria (puesto 14 de 14). En la clínica fue
   el **12 de 14**. Corregir a «puesto 14 de 14 y 12 de 14 respectivamente».
7. **«no puede atribuirse al mecanismo de selección de ninguna»** (Métodos, Tabla 2): es demasiado
   fuerte. Dos cohortes de la misma provincia comparten sesgos de alfabetización, de acceso y de
   declaración de escolaridad. Atenuar a «hace improbable que se deba al mecanismo de selección de una
   de ellas».

---

## 3. Objeciones menores

**m1.** Las referencias **26 a 37 no están citadas en el texto** (el cuerpo cita 1–25). Doce
referencias huérfanas. Eliminarlas o incorporarlas.

**m2.** **Numeración inconsistente entre texto y Tabla 1:** el texto cita García-Caballero como ⁹ y
Sousa y Vivas como ¹⁰; la Tabla 1 los cita como ⁷ y ⁸. Corregir.

**m3.** **Tabla 3A no coincide con el texto.** El texto dice «nueve alcanzaron significación». La tabla
lista ocho ítems, uno de los cuales (**Registro de 3 palabras, q = 0,219**) **no es significativo** y no
está marcado como tal, y **omite dos que sí lo son** (`ACE_HabVisoCubo`, ΔR² = 0,0096, q = 0,039;
`ACE_MRecuerdoNyD`, ΔR² = 0,0056, q = 0,029). La tabla en realidad muestra «los ocho mayores por ΔR²».
Reetiquetar la tabla o listar los nueve significativos, y en cualquier caso marcar la significación.

**m4.** **Contradicción interna entre Discusión y Conclusión.** Discusión: «la regla vigente señala a
**cuatro de cada diez** personas sin deterioro cuando tienen baja escolaridad». Conclusión: «señala al
**63 %** de las personas sin deterioro y baja escolaridad». La cifra correcta es 63,0 %; el 34,3 %
global (1 − especificidad 0,657) es otra cosa. Unificar.

**m5.** **El b₂ clínico se reporta como −0,0784 en el cuerpo, pero el bloque V4 usa −0,0694** porque
corre sobre n = 2027 (casos con los 23 ítems completos) y no 2112. El manuscrito yuxtapone ambas
estimaciones sin declarar el cambio de muestra. Añadir el n a cada una.

**m6.** El ítem de **reconocimiento de nombre y dirección aparece con DIF educativo** (ΔR² = 0,0145,
q = 0,005) y es **precisamente el ítem que se armonizó** entre bases. Debe declararse que su DIF puede
ser en parte un artefacto de la armonización, y aportarse la sensibilidad sin ese ítem.

**m7.** **Cobertura diferencial de la clasificación diagnóstica por educación** (92,4 % / 93,9 % /
89,5 %; p = 0,006) y **275 conclusiones no captadas** por la oración canónica: no se discute qué pasó
con esas 275 personas ni si su exclusión es diferencial. Debe entrar en Limitaciones.

**m8.** Los **denominadores del corpus diagnóstico no cierran** con los de la cohorte: 3025
conclusiones, 2750 captadas, 2242 evaluaciones en la base, 2112 analizadas. Añadir el encadenamiento
completo.

**m9.** La **Tabla 2 tiene invertido el rótulo** «Comparación de excluidos frente a incluidos»: las
primeras cifras de cada par (63,28; 10,34; 75,18) son las de los **incluidos**. Además el manuscrito
habla de «los 90 excluidos» pero las comparaciones se hacen sobre **n = 108, 65 y 56** según la variable
(y 108 > 90, porque incluye los 18 excluidos por solapamiento). Corregir el rótulo y declarar el n de
cada comparación.

**m10.** **El EEM «entre 6,2 y 8,4 puntos según el método»** no es un rango entre métodos: 6,17 es el
EEM del subgrupo de 181–365 días y 8,35 el del conjunto. Reformular como «según el intervalo entre
administraciones». Y añadir el dato decisivo: en el subgrupo test-retest hay **n = 1 persona con menos
de 7 años de escolaridad** (`V2_reproduccion.json`, `/test_retest/por_tramo`), de modo que el EEM del
tramo de baja escolaridad —el que importa para el argumento— es esencialmente desconocido, y los EEM
disponibles ya difieren entre tramos (5,99 en 7–11 frente a 8,91 en ≥12).

**m11.** Discrepancia menor entre archivos: **cambio mínimo detectable 23,1** (`V2_reproduccion.json`)
frente a **22,6** (`V2b_testretest.json`). Y el salto de positividad 11→12 años figura como **8,4×** en
el suplemento y **8,5** en el JSON. Unificar.

**m12.** **Unidimensionalidad.** Razón entre autovalores 5,75 con **35,8 % de varianza en el primer
componente** es un apoyo modesto para unidimensionalidad esencial. Reportar índices de ajuste de un
modelo unifactorial (CFI, TLI, RMSEA) o al menos declarar el criterio empleado y su umbral.

**m13.** La **discusión del VIF** (14–21, con la demostración de invarianza al centrado) es correcta
pero pertenece al suplemento, no al cuerpo del manuscrito; hoy no está en el cuerpo, lo cual está bien
— sólo asegurar que no reaparezca en la versión revisada.

**m14.** El **modelo de dispersión** de la corrección continua (`lr2 ~ edu + Edad`) es un ajuste en dos
etapas sobre residuos cuadrados logaritmizados, sin propagación de incertidumbre hacia z. Si se
mantiene la propuesta, usar un marco conjunto (GAMLSS, como los propios autores citan en la
referencia 22) o declarar la limitación.

**m15.** **Nombrar el test de reconocimiento en cada cohorte.** El código toma
`LDR_Reconocimiento_A` en la base comunitaria y `test='Lista de Rey' / subtest like 'Reconoc%'` en la
clínica. Aunque la escala sea idéntica (0–15), el manuscrito debe nombrar el instrumento, la lista y el
procedimiento de administración en cada cohorte, y justificar la comparabilidad. Es la variable que
define el grupo control.

**m16.** «**Ningún ítem presentó funcionamiento diferencial no trivial**» descansa en el umbral
ΔR² ≥ 0,035 de Zumbo. Ese umbral es convencional y discutido; declararlo como convención elegida y
reportar en paralelo un criterio alternativo (p. ej. tamaños de efecto de Jodoin-Gierl o el DTF
esperado) para que la conclusión no dependa de un solo punto de corte.

**m17.** La declaración de uso de **inteligencia artificial** cumple la sección V de ICMJE, pero debe
precisar en qué tareas concretas (programación, edición de estilo) y confirmar que ningún resultado
numérico, figura o referencia fue generado por ella. Dado que las referencias llevan la advertencia
«⚠ Verificar cada referencia contra el original antes del envío», esa verificación debe estar hecha
antes del envío, no señalada dentro del manuscrito.

**m18.** El **conflicto de intereses de D.B.** está bien declarado. Añadir que no participó en la
codificación de la procedencia documental (Tabla 1) o, si participó, cómo se mitigó.

**m19.** «**La escolaridad se declaró con amontonamiento en valores de credencial (37,5 % y 47,3 % en 7,
12 y 17 años)**»: excelente observación, pero tiene una consecuencia analítica que no se explora. Con
amontonamiento en 12 años, la estimación del escalón **en 12** es la más vulnerable a error de medición
diferencial de la exposición (personas con 11 o 13 años reales que declaran 12). Ese error atenúa
cualquier escalón verdadero hacia cero. Debe declararse como amenaza específica al resultado
principal, y no sólo como limitación genérica de medición. Sugiero un análisis excluyendo a quienes
declaran exactamente 12 y comparando 10–11 con 13–14.

**m20.** El **valor 68 «figura en el protocolo impreso de la versión argentina»**: para *Neurology* esta
afirmación documental necesita una referencia citable (edición, año, editor del protocolo) o una figura
suplementaria con la reproducción de la página. Es la pieza central de la Tabla 1.

---

## 4. Errores fácticos e inconsistencias numéricas verificadas contra los archivos de resultados

| # | Afirmación del manuscrito | Lo que dicen los archivos | Fuente |
|---|---|---|---|
| E1 | «La **razón** entre gradientes **fue de 4,8**» | La razón calculada sobre los datos es **47,16 / 6,35 = 7,43**. El 4,79 es la **mediana bootstrap** (`np.median(bs[:,2])`), no declarado como tal | `V12_equidad_definitiva.json`; `codigo/V12_equidad_definitiva.py` l. 146 |
| E2 | «replicó entre cohortes» / «una forma que se reproduce entre cohortes» | El test conjunto de la forma **rechaza la igualdad**: p = 0,0012; el componente lineal difiere, p = 0,00026. Sólo la curvatura replica (p = 0,764) | `V2_reproduccion.json` `/replicacion/` |
| E3 | «de catorce cortes fue el menos discontinuo» (resumen) | Puesto **14 de 14** sólo en la comunitaria; **12 de 14** en la clínica | `V3_supuestos.json` `/placebo/*_rank12` |
| E4 | «la regla vigente señala a **cuatro de cada diez** personas sin deterioro cuando tienen baja escolaridad» (Discusión) frente a «señala al **63 %**» (Conclusión) | La cifra en <7 años es **63,0 %**; el 34,3 % es el global (1 − especificidad) | `V12_equidad_definitiva.json` |
| E5 | «concentra casi cinco veces más **deterioro grave**» | La cifra es el porcentaje con **ACE-III ≤ 40** (7,5 % frente a 1,6 %): banda de puntaje, no categoría de gravedad. **Esa fila no está en la Tabla 2** | `V2_reproduccion.json` `/descriptivos/pct_le40` |
| E6 | «el escalón de 18 puntos equivale a **2,2 errores de medición**» | 18 / 8,15 = 2,21, pero el EEM tiene **IC 95 % 1,93 a 12,21** → el cociente va de **1,5 a 9,3**. Y con el rango declarado 6,2–8,4 sería **2,1 a 2,9**, no «2,2» | `V2b_testretest.json` |
| E7 | Tabla 3A: se listan 8 ítems como resultado del barrido de DIF; el texto dice «**nueve** alcanzaron significación» | La tabla incluye un ítem **no** significativo (Registro, q = 0,219) y **omite dos significativos** (Cubo q = 0,039; Recuerdo diferido N y D q = 0,029) | `V4b_dif_ordinal.json` |
| E8 | «el instrumento **no está sesgado**» (resumen, conclusión) | El DTF clínico es **estadísticamente significativo**: +0,34 (0,08 a 0,59), p = 0,009 | `V4c_dtf.json` |
| E9 | Curvatura clínica «−0,0784» junto a la comparación con la métrica latente | En el bloque de métrica latente la curvatura clínica cruda es **−0,0694** (n = 2027, no 2112). No se declara el cambio de muestra | `V4_tri.json` `/curvatura_latente/clínica/` |
| E10 | «Modelo de respuesta graduada (n = 2785) para métrica latente **y funcionamiento diferencial**» | El DIF de ítem corrió sobre **n = 758** (focal 408 / referencia 350), sólo en la comunitaria | `V4b_dif_ordinal.json`, `V4_tri.json` `/dif_educacion/` |
| E11 | «Comparación de **excluidos frente a incluidos**: edad 63,28 frente a 64,84…» (Tabla 2) | El orden está invertido: 63,28 corresponde a los **incluidos**. Además los n son 108 / 65 / 56, no 90 | `V3_supuestos.json` `/faltantes/` |
| E12 | «los **90 excluidos** tenían más escolaridad (12,0 frente a 10,3; p = 0,029) y mejor rendimiento» | La comparación de edad usa n = 108 excluidos (incluye los 18 del solapamiento); la de escolaridad n = 65; la de ACE n = 56 | `V3_supuestos.json` `/faltantes/` |
| E13 | Cohorte clínica: n analítico 2112 | La base definitiva tiene **2242** personas. **No se explica el paso 2242 → 2112** en ninguna parte del manuscrito ni del suplemento | `V1_integridad.json`, `V2_reproduccion.json` |
| E14 | «Ambas reglas se calibraron a la misma tasa de positividad» | La tasa no se declara; del código y las cifras se deduce ≈ **64,3 %** | `codigo/V12_equidad_definitiva.py` l. 101–102 |
| E15 | Suplemento V2: «salto **8,4×**» | El archivo da **8,5** | `V2_reproduccion.json` `/positividad/comunitaria/salto_veces` |
| E16 | Suplemento V2: cambio mínimo detectable «±23,1» | `V2b_testretest.json` da **22,6** | discrepancia entre archivos |
| E17 | Suplemento V6 presenta AUC 0,997 como «validación independiente (ACE-III no usado para clasificar)» | Un AUC de 0,997 entre etiqueta narrativa y test índice es **evidencia a favor** de incorporación, no en contra. Además, 1 de 87 «sin afectación» tiene ACE < 82 y el mínimo del grupo es 74 | `V6_verificacion_dx.json` |
| E18 | Referencias | Las referencias **26 a 37 no se citan** en el cuerpo; Tabla 1 numera a García-Caballero y a Sousa-Vivas como ⁷ y ⁸ mientras el texto usa ⁹ y ¹⁰ | `MANUSCRITO.md`, `Tabla1.md` |
| E19 | Métodos: clasificación de referencia «construida sin el ACE-III», controles = reconocimiento ≥10 | Los controles clínicos requieren **además** la etiqueta «Sin afectación» del informe | `codigo/V12_equidad_definitiva.py` l. 60–63 |
| E20 | Resultados de V7 usados en Discusión (AUC 0,855 / 0,957; curvatura por estrato) | Provienen de una **clasificación de referencia distinta** de la descrita en Métodos, sin emparejamiento y con otros n | `V7_estandar_referencia.json` |

---

## 5. Fortalezas

Las señalo porque son reales y porque determinan que la recomendación sea revisión mayor y no rechazo.

1. **La falsación del umbral de 12 años es metodológicamente ejemplar.** El conjunto —indicador de
   discontinuidad sobre la forma continua ya especificada, regresión discontinua local en tres
   ventanas, prueba de placebo sobre los catorce cortes candidatos con corrección de Bonferroni y
   prueba de equivalencia frente a tres márgenes— es más de lo que la mayoría de los trabajos sobre
   puntos de corte ofrece. El razonamiento «evidencia de ausencia, no ausencia de evidencia», anclado
   en una diferencia mínima detectable de 3,8 puntos, es correcto y está bien argumentado.

2. **El test de placebo demuestra su propia sensibilidad.** Que el único corte con señal (7 años en la
   clínica) resulte explicable por amontonamiento de credencial, vaya en el sentido contrario al
   efecto educativo y no replique en la otra cohorte, es exactamente el control positivo que valida el
   procedimiento. Es la mejor página del manuscrito.

3. **La anticipación de la objeción psicométrica es excelente y honesta.** Reestimar la curvatura sobre
   la métrica latente para descartar el artefacto de techo, encontrar que sobrevive dos tercios, y
   **reportar la cifra conservadora** es una decisión que muchos autores no toman. (Aunque después el
   cuerpo del manuscrito reporta la razón de 4× del puntaje bruto en el resumen en lugar de la de 2×
   sobre θ que el suplemento declara preferible — ver M10 y corregirlo.)

4. **La reconstrucción documental de la procedencia de los dos cortes (Tabla 1) es una contribución
   original y de valor práctico inmediato para la neurología argentina**, y está expuesta sin
   personalizar la crítica: se señala explícitamente que los estudios de origen no cometieron error
   alguno y que el desajuste se produce aguas abajo. Es el tono adecuado.

5. **La disciplina de verificación es superior a la habitual.** Doce bloques documentados, con detección
   y corrección de defectos de procesamiento reales (ceros a la izquierda en el documento de identidad,
   `dayfirst` sobre fechas ISO), reejecución completa aguas abajo, y una regla explícita de no reutilizar
   cifras de corridas anteriores. La sección «Los tres hallazgos que obligaron a cambiar conclusiones»
   es el tipo de transparencia que la revista quiere ver — **por eso mismo tiene que estar en el cuerpo
   del manuscrito y no sólo en el suplemento** (M2).

6. **El diseño de dos cohortes con selección opuesta** es una elección inteligente y bien explotada, y
   la decisión de no reportar nunca una estimación marginal combinada por falta de invarianza estricta
   es metodológicamente rigurosa.

7. **La distinción conceptual entre funcionamiento diferencial y desplazamiento de la distribución de
   habilidad** —«el test no está sesgado, pero la escolaridad desplaza la distribución de la habilidad
   misma»— es correcta, está bien articulada y reconcilia con elegancia el hallazgo con la literatura
   que desaconseja el ajuste demográfico. Es el aporte conceptual más sólido del trabajo y debería ser
   el eje del manuscrito revisado, en lugar de la razón de gradientes.

---

### Nota final al editor

El manuscrito contiene dos trabajos. El primero —la falsación del umbral de 12 años y la
caracterización de la forma funcional— es sólido, original, relevante para la práctica regional y, con
las correcciones de M3, M10, M12 y M13, publicable. El segundo —la demostración de que una corrección
continua reduce la desigualdad de trato— no está en condiciones de publicarse en su forma actual: su
resultado principal es en gran parte una propiedad construida del procedimiento (M1), se obtuvo tras
una búsqueda no declarada entre definiciones de control (M2), su estimación puntual no es la que se
reporta (M4) y su grupo control no es independiente del test índice (M5). Sugiero al editor que, si los
autores prefieren no acometer M1 y M2, se les invite a reenviar sólo el primer trabajo, con el análisis
de equidad reducido a la afirmación que sí está sostenida: que la regla vigente trata de forma muy
desigual a personas con criterio de control equivalente, y que ese trato desigual no parece ser el
precio de su rendimiento diagnóstico.
