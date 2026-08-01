# Cambios para aplicar en el documento colaborativo

## 0 · Título — a decidir con el equipo

El título vigente apuntaba a «la corrección por escolaridad del ACE-III **en la Argentina**» y decía que
**produce** un gradiente. Como el hallazgo de la dispersión mostró que el problema no es dónde está el
umbral sino que ninguno puede estar bien puesto, los tres candidatos apuntan al **umbral fijo como
método** y no a ningún punto de corte en particular ni a sus autores.

**A — el que quedó puesto en el archivo:**

> Escolaridad y ACE-III en dos cohortes argentinas: una asociación continua y con variabilidad
> decreciente que ningún umbral fijo puede capturar
> *Corto:* Escolaridad, variabilidad y puntos de corte en el ACE-III

**B — propuesta metodológica:**

> Del punto de corte a la norma continua: escolaridad, variabilidad y clasificación en el ACE-III en dos
> cohortes argentinas
> *Corto:* Del punto de corte a la norma continua en el ACE-III

**C — descriptivo neutro:**

> Forma y variabilidad de la asociación entre escolaridad y ACE-III en dos cohortes argentinas:
> implicancias para la interpretación por puntos de corte
> *Corto:* Forma y variabilidad de la asociación escolaridad–ACE-III

El gradiente de 44 puntos porcentuales se conserva en el resumen, en Resultados y en la Figura 4.

---

Referencia: estado del manuscrito **antes** de los cambios de hoy (`versiones/v5_pre_dispersion.md`)
frente al actual. Si el Doc está en un estado anterior, avisá y regenero la lista contra esa versión.

Los cambios son de cuatro clases: **[NUEVO]** contenido que antes no existía, **[TONO]** redacción
diplomática, **[RECORTE]** compresión por límite de extensión —el contenido pasó al suplementario, no
se perdió— y **[DATO]** cifras que cambiaron.

Cuerpo: 4400 palabras (antes 4673). Resumen 300. Abstract 286.

---

## 1 · Resumen

**[TONO]** Buscar `un escalón de 18 puntos jamás testeado` → reemplazar por
`un escalón de 18 puntos nunca evaluado`.

**[NUEVO + RECORTE]** El párrafo de **Material y métodos** se acorta y el de **Resultados** incorpora
la dispersión. Reemplazar los tres párrafos —Métodos, Resultados y Conclusiones— por:

> **Material y métodos.** Estudio transversal en dos cohortes de San Juan de selección opuesta:
> comunitaria (n = 758) y clínica (n = 2112). Regresión robusta, prueba de placebo sobre los catorce
> cortes y equivalencia. Modelo de respuesta graduada para métrica latente y funcionamiento
> diferencial. Las reglas se compararon frente a una clasificación construida sin el ACE-III (Clase IV).
>
> **Resultados.** La pendiente cayó de 2,9 a 0,7 puntos/año entre los años 3 y 17 y la curvatura
> replicó entre cohortes (p = 0,764). **La dispersión del rendimiento normal se estrechó de 12,9 a 5,8
> puntos al aumentar la escolaridad (p = 1,5×10⁻⁶): el corte de 68 ocupa el percentil 86 sin
> escolaridad y el 5 con once años.** No hubo discontinuidad a los 12 años (+0,04 y +0,13), con
> equivalencia dentro de ±3 puntos, y fue el menos discontinuo de los catorce. El sesgo por ítem fue
> bidireccional y el del total, 0,08 y 0,34 puntos. **Las personas sin deterioro con menos de 7 años de
> escolaridad promediaron 65,5 puntos, bajo el corte de 68.** La regla señaló al **60,3 %** de esos
> controles frente al **16,2 %** de los de 7 a 11: **44,1 puntos porcentuales** (IC 95 % 30,8 a 57,7).
> Eliminarlo no costó desempeño (Youden +0,022; IC −0,022 a +0,074).
>
> **Conclusiones.** El umbral carece de correlato empírico y el sesgo de medición es despreciable, pero
> la escolaridad desplaza la distribución de la habilidad y **estrecha su dispersión: ningún corte fijo
> ocupa la misma posición en todos los tramos**. Ese trato desigual puede eliminarse sin costo
> diagnóstico.

El **Abstract** en inglés tiene los mismos cambios; está en el PDF y en el archivo.

---

## 2 · Introducción

**[TONO]** En el párrafo del corte de 86, reemplazar:

| Antes | Ahora |
|---|---|
| El **86** procede de la validación argentino-chilena del ACE-III², que propone **un único punto de corte**, informa su rendimiento diagnóstico y **declara con transparencia la composición educativa de su muestra** —14,4 años de escolaridad—, sin proponer estratificación por nivel educativo. | El **86** procede de la validación argentino-chilena del ACE-III², **el estudio que puso el instrumento en condiciones de uso en la región**. Propone **un único punto de corte**, informa su rendimiento diagnóstico y **declara con transparencia la composición educativa de su muestra** —14,4 años de escolaridad—, sin proponer estratificación por nivel educativo **ni el umbral que hoy se aplica**. |

**[TONO · el cambio más importante]** Agregar, inmediatamente después de la frase que termina en
`umbral que no aparece en ninguna fuente primaria`, esta oración nueva:

> **Ninguno de los dos estudios de origen propuso esa regla compuesta**: cada uno derivó su corte para
> su propia población y lo informó con su alcance. La regla vigente es un producto de la práctica, no
> de una u otra publicación.

**[RECORTE]** En la cita de Sousa y Vivas se suprime la primera mitad y queda sólo:
`advirtieron que «quedó pendiente la realización de un estudio con bajo nivel escolar»¹⁰`.

**[RECORTE]** Los dos párrafos de contexto regional y el del debate internacional se comprimen sin
perder ninguna referencia. Ver el PDF; ningún argumento ni cita desaparece.

---

## 3 · Material y métodos

**[NUEVO]** El apartado que empezaba con `**Comparación de reglas.**` pasa a llamarse
`**Modelo de posición y dispersión.**` y su primera mitad se reemplaza por:

> **Modelo de posición y dispersión.** La corrección continua estima el puntaje esperado como función
> suave de escolaridad, edad y sexo **y, por separado, la dispersión esperada**, mediante una segunda
> regresión sobre el logaritmo del residuo al cuadrado. Esa estimación subestima la varianza en
> E[log χ²₁] = −1,270 y se corrigió en consecuencia²⁸; sin la corrección la dispersión queda 1,9 veces
> por debajo de la real y el 19 % de los controles cae bajo su propio percentil 5 nominal, frente al
> 6,5 % una vez corregida. Se ajustó **sólo sobre los controles**, con validación cruzada de diez
> particiones.

*(Referencia nueva, la 38: Harvey AC. Estimating regression models with multiplicative
heteroscedasticity. Econometrica. 1976;44(3):461-5.)*

**[RECORTE]** Se suprime el apartado `**Alcance.**` completo: repetía la primera limitación.

**[RECORTE]** Se comprimen `Casos`, `Controles`, `Declaración de procedimiento`, `Forma funcional`,
`Métrica latente` y `Prespecificación`. El detalle numérico —unidimensionalidad, Q3, y el porqué del
fracaso del criterio funcional— pasó al suplementario.

---

## 4 · Resultados

**[NUEVO]** Insertar una sección entera **antes** de `## No existe discontinuidad en los 12 años`:

> ## La dispersión se estrecha a medida que aumenta la escolaridad
>
> La variabilidad del rendimiento entre personas sin deterioro **no es constante**: el desvío del
> ACE-III fue de **13,8 puntos** con menos de 7 años de escolaridad, 8,6 entre 7 y 11 y 7,8 con 12 o
> más (Levene p = 2,2×10⁻¹⁴). Modelada de forma continua, la dispersión cae **0,081 unidades de
> log-varianza por año** (IC 95 % −0,113 a −0,048; p = 1,5×10⁻⁶), de modo que a los 65 años pasa de
> **12,9 puntos** sin escolaridad a **5,8** con veinte: los puntajes se abren abajo y se comprimen
> contra el techo del instrumento arriba.
>
> De ahí que un mismo número ocupe posiciones muy distintas según a quién se aplique. **El corte de 68
> se sitúa en el percentil 86 de las personas sin deterioro que no completaron ningún año de escuela y
> en el percentil 5 de quienes completaron once** (Figura 3); el de 86, en el percentil 65 de quienes
> completaron doce.

**[RECORTE]** La sección `## Robustez` se reduce a cuatro líneas y remite al suplementario.

**[RECORTE]** La sección `## Los cortes vigentes están por encima de los valores empíricos` desaparece
como sección: su contenido se funde al final de `## Eliminar ese gradiente no cuesta desempeño
diagnóstico`, conservando la defensa clave —la regla vigente supera a cualquier corte único— y
mandando los cortes exploratorios al suplementario.

**[RECORTE]** En `Escala de referencia`, el test-retest ya no se narra: está en la Tabla 3.

---

## 5 · Discusión

**[NUEVO]** Agregar, después de `sobrecorrige en el extremo alto y subcorrige en el bajo¹⁹.`:

> A la forma se suma la dispersión, y juntas alcanzan para una conclusión más general. Como la
> variabilidad del rendimiento normal se reduce a menos de la mitad entre los extremos de escolaridad,
> **ningún número fijo puede ocupar la misma posición relativa en todos los tramos**, con independencia
> de dónde se lo sitúe: el problema no es que el umbral de los 12 años esté mal ubicado, sino que un
> umbral único es incapaz de representar distribuciones cuyo ancho difiere al doble. Es la razón de que
> el corte de 68 declare anormal a la mayoría de quienes no fueron a la escuela y casi a nadie con once
> años de escolaridad.

**[TONO]** Encabezado: `## El umbral de los 12 años no se corresponde con nada observable` →
`## El umbral de los 12 años no tiene correlato en los datos`.

**[TONO]** Reemplazar el párrafo de la reconstrucción documental por:

> La reconstrucción documental (Tabla 1) explica por qué: **el umbral no fue estimado a partir de
> datos**, sino que resulta de yuxtaponer dos cortes derivados en poblaciones distintas y con criterios
> de escolaridad distintos²،⁹. **Conviene subrayarlo: no hay aquí un defecto de los estudios de origen**,
> que informaron su alcance con transparencia y no propusieron la regla compuesta. El desajuste se
> produce aguas abajo, cuando la práctica los combina —proceso ordinario en la formación de reglas de
> decisión y rara vez verificado después—, y la heterogeneidad de cortes es endémica en el cribado
> cognitivo⁴.

**[RECORTE]** Se suprime el párrafo sobre el cuestionario funcional en `## Lo que ninguna regla de
decisión puede resolver` (pasó al suplementario, bloque V17-C).

---

## 6 · Limitaciones

**[NUEVO]** La **cuarta** limitación —antes «el criterio de control es unidimensional»— se fusiona con
la tercera, y la cuarta pasa a ser:

> **Cuarta: el percentil supone normalidad condicional.** Corregida la dispersión, la calibración es
> adecuada pero no exacta —cae bajo el percentil 5 nominal el 6,5 % de los controles y los residuos
> conservan asimetría de −0,58 por el techo del instrumento—, de modo que los percentiles extremos son
> aproximaciones.

**[RECORTE]** Las limitaciones quinta a octava se agrupan en un solo párrafo. Ninguna se elimina.

---

## 7 · Conclusión

**[NUEVO]** Se agrega la dispersión al primer párrafo:
`Además **la dispersión del rendimiento normal se estrecha al aumentar la escolaridad**, de 12,9 a 5,8 puntos.`

**[TONO]** En el último párrafo:

| Antes | Ahora |
|---|---|
| pero la corrección vigente **está mal especificada**: un escalón donde corresponde una curva, situado donde no hay discontinuidad **y calibrado por encima de los valores empíricos** | pero **la forma de la corrección vigente no coincide con la de la asociación que corrige**: un escalón donde los datos describen una curva, situado en un punto donde no hay discontinuidad |

---

## 8 · Declaraciones

**[NUEVO]** Reemplazar `Disponibilidad de datos y código` por:

> **Disponibilidad de datos, código y material suplementario.** El código de análisis, las salidas
> numéricas y las bitácoras de verificación están disponibles en el repositorio público
> <https://github.com/fermarquez88/kaizenai-ace>. Los datos individuales no se distribuyen: contienen
> identificadores directos y texto libre de conclusiones clínicas. Se publican los coeficientes del
> modelo normativo, que permiten reproducirlo sin acceder a los datos de origen.
>
> - **Material suplementario:** <https://github.com/fermarquez88/kaizenai-ace/blob/main/manuscrito/SUPLEMENTARIO.md>
> - **Calculadora del modelo:** <https://fermarquez88.github.io/kaizenai-ace/>

**[DATO]** `Número total de palabras del cuerpo:` → **4400**.

---

## 9 · Referencias

Once referencias —la 26 y las 28 a 37— **no estaban citadas en el texto**. Se resolvió así:

| Referencia | Dónde se citó ahora |
|---|---|
| 26 Calderón 2021, TRI del ACE-III | Métodos, junto al modelo de respuesta graduada |
| 28 Sachs 2021, normas ajustadas del MoCA | Introducción, con la evidencia sobre normalización demográfica |
| 29 Valles-Salgado 2024, cinco pruebas de cribado | Introducción, con la heterogeneidad de cortes |
| 30 Llibre-Guerra 2024, determinantes sociales | Introducción, párrafo regional |
| 31 Brown 2025, normas en peruanos | Discusión, comparación regional de adaptaciones |
| 32 Marquine 2023, normas en latinos | Discusión, comparación regional de adaptaciones |
| 33 Salemme 2025, pronóstico del deterioro leve | Limitaciones, tercera |
| 34 Islam 2023 *(era la 36)* | Discusión, cribado en baja alfabetización |
| 35 Legaz 2024 *(era la 37)* | Introducción, párrafo regional |
| **Sarasola 2005** *(era la 34)* | **Eliminada:** antigua y sin lugar natural |
| **Ganguli 2010** *(era la 35)* | **Eliminada:** antigua y sin lugar natural |

Se agrega **36. Harvey AC. Estimating regression models with multiplicative heteroscedasticity.
*Econometrica*. 1976;44(3):461-5**, por la corrección de la dispersión.

Quedan **36 referencias, ninguna sin citar, 72,2 % de los últimos cinco años**. Conviene que verifiques
las ubicaciones: cada una se puso donde el texto ya hacía la afirmación que la referencia sostiene.

---

## 10 · Tablas y figuras

Las tres tablas ahora son **imágenes renderizadas** con un estilo único —cada una lleva su título, su
subtítulo y su nota al pie dentro de la imagen—, y están en `figuras/Tabla1.jpg`, `Tabla2.jpg` y
`Tabla3.jpg`. En el Doc reemplazan a las tablas de texto.

| | Antes | Ahora |
|---|---|---|
| **Tabla 3** | Psicometría, funcionamiento diferencial y comparación de reglas | **Puntajes esperados según escolaridad y edad**, más la posición del corte. El detalle por ítem pasó al suplementario |
| **Figura 3** | Consecuencia de aplicar la regla vigente | **Posición del corte respecto del esperado y del percentil 5**, y proporción señalada año a año |
| **Figura 4** | — | Se corrigió el eje del panel b: mostraba «0, 1, 2» en lugar de los tramos educativos |
| **Paleta** | incluía verde | Sólo azul, rojo, ámbar y grises |

---

## 11 · Pendientes

1. **Acta del comité de ética de la cohorte clínica** — comité, número y fecha. Es motivo de rechazo
   automático si falta.
2. **Financiamiento** — declarar, o la fórmula «El estudio no recibió financiamiento específico».
3. **Filiación** — agregar Instituto de Neurociencias San Juan a Diana Bruno, Fernando Márquez e Iara
   Jácome.
4. **Corrección factual pendiente, de Diana.** Dice que el 68 **no proviene de la versión impresa**
   sino de un **protocolo interno de INECO** que lo incluía por practicidad, y que la versión libre no
   lo trae. Afecta a la Tabla 1 (fila «Vía de incorporación a la práctica local»), a la Introducción y a
   la Discusión. Refuerza el argumento: un protocolo interno tiene menos estatus de fuente primaria que
   una versión impresa publicada. **Sin aplicar, a la espera de confirmarlo.**, por la corrección de la dispersión.
