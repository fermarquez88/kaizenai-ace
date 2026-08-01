# Auditoría bioestadística y neuropsicológica de los bloques V6–V8

> Realizada 2026-08-01, antes de incorporar los resultados al manuscrito.

## Hallazgos nuevos consolidados

| # | Hallazgo | Cifra | Estado |
|---|---|---|---|
| 1 | Estándar de referencia construido sin usar el ACE-III | 690 sin demencia (603 comunitarios + 87 clínicos), 1127 DCL, 627 demencia | ✅ |
| 2 | La etiqueta diagnóstica no es circular | 0 de 2750 oraciones clasificatorias mencionan un test o un puntaje | ✅ |
| 3 | Validación independiente de la etiqueta | ACE-III 92,5 → 78,6 → 54,0; AUC sin demencia vs demencia 0,997 | ✅ |
| 4 | **El ACE-III discrimina peor en baja escolaridad** | AUC 0,855 (<7) · 0,935 (7–11) · 0,957 (≥12), intervalos no solapados | ⚠ nuevo |
| 5 | **La regla vigente supera a cualquier corte único** | Youden 0,628 vs 0,394–0,497 | ⚠ **contradice la conclusión previa** |
| 6 | Los cortes vigentes están altos y deberían ser graduados | óptimos empíricos 57 · 64 · 78 (vigentes 68 · 68 · 86) | exploratorio |
| 7 | **Una corrección continua iguala el desempeño con 11 veces menos inequidad** | Youden 0,628 en ambas; rango de falsos positivos 30,6 → **2,7** | ✅ resultado central |
| 8 | La forma de la asociación no difiere entre estratos diagnósticos | b₂ −0,066 / −0,061 / −0,070; interacción p=0,961 | ✅ |
| 9 | El propio ADLQ tiene sesgo educativo en subescalas específicas | empleo/recreación r=−0,265; comunicación (lectura, escritura) r=−0,160 | ✅ metodológico |

---

## Objeciones del bioestadístico

**1. La tasa de positividad del 57 % no es poblacional.** La muestra está enriquecida en casos
(627 demencias y 1127 DCL frente a 690 controles). La calibración a esa tasa es válida **como
punto de comparación entre reglas**, pero no representa un escenario clínico realista.
→ *Resolución:* declarar que la tasa se fija para igualar reglas, no para describir la población.

**2. Diseño de dos puertas.** Los casos provienen de la cohorte clínica y la mayoría de los
controles de la comunitaria. Esto **infla la exactitud absoluta** y sesga los cortes óptimos.
→ *Resolución:* no reportar exactitud absoluta como resultado. Todas las comparaciones son entre
reglas sobre la misma muestra, donde el sesgo se cancela. Los cortes de 57/64/78 se reportan como
**exploratorios, con validación externa pendiente**, nunca como recomendación clínica.

**3. La muestra normativa contiene deterioro cognitivo leve.** "Sin compromiso funcional" excluye
demencia, no DCL. Las normas construidas sobre ella están desplazadas hacia abajo, y más en baja
escolaridad, donde el DCL es más prevalente.
→ *Resolución:* la corrección continua se presenta como **demostración de forma**, no como norma
utilizable. Se declara la dirección del sesgo.

**4. El DCL se excluyó del cálculo de sensibilidad y especificidad.** Correcto —no es caso ni
control—, pero debe explicitarse porque cambia los denominadores.

**5. Validación cruzada.** El modelo normativo se estimó con 10 particiones sobre la referencia, de
modo que ninguna persona contribuye a su propia norma. Los casos se puntuaron con la referencia
completa, lo cual es correcto porque no participaron de su estimación.

**6. Multiplicidad.** Se comparan cuatro reglas prespecificadas sobre un mismo desenlace; no
requiere corrección adicional. Los cortes óptimos se acompañan de intervalo por remuestreo.

**7. La sensibilidad del criterio de control fue examinada.** Cinco umbrales funcionales: el
elegido (ninguna dificultad) es el más conservador y **el único sin dependencia educativa clara**
(p = 0,108; los umbrales intermedios dan p = 0,011 y p = 0,003).

---

## Objeciones del neuropsicólogo

**1. La etiqueta de demencia no sigue criterios formales.** Proviene de la banda de gravedad
consignada en la conclusión del informe (moderado o superior), no de criterios DSM-5 o NIA-AA. Es
un juicio clínico estructurado, no un diagnóstico etiológico —el propio codebook lo declara—.
→ *Resolución:* llamarla **«deterioro de grado moderado o mayor según el informe clínico»**, nunca
«demencia» a secas, y declararlo en Métodos y Limitaciones.

**2. El menor poder discriminativo en baja escolaridad no se corrige moviendo el umbral.** El área
bajo la curva de 0,855 frente a 0,957 significa que **ninguna elección de corte iguala el desempeño
entre tramos**. La corrección continua iguala los falsos positivos, no la capacidad discriminativa.
→ *Resolución:* decirlo explícitamente. Es una limitación del instrumento en esa población,
coherente con la literatura sobre cribado en baja alfabetización, y no algo que una regla pueda
resolver.

**3. El hallazgo del sesgo educativo dentro del ADLQ merece reporte propio.** Que la escala
funcional incluya ítems de lectura, escritura, uso de computadora y cajero automático significa que
**penaliza la falta de exposición, no el deterioro**. Es un problema del mismo tipo que el que
estudiamos, en el instrumento que usamos como criterio.
→ *Resolución:* reportarlo en Métodos como justificación del criterio restringido, y en Discusión
como observación de interés propio.

**4. La ausencia de diferencias de forma entre estratos (p = 0,961) es un resultado positivo, no un
nulo débil.** Con 690, 1127 y 627 participantes por estrato, la potencia es alta.

---

## Efecto sobre las conclusiones del manuscrito

| Conclusión previa | Estado tras V6–V8 |
|---|---|
| «No hay discontinuidad en los 12 años» | **se mantiene** |
| «El instrumento no tiene sesgo de medición por escolaridad» | **se mantiene** |
| «La forma es continua y con rendimientos decrecientes» | **se mantiene y se refuerza** (no difiere entre estratos) |
| «La carga de la prueba recae sobre la corrección» | **debe revisarse**: la corrección por escolaridad **sí mejora** la clasificación |
| «Sin justificación psicométrica para corregir» | **se matiza**: no hay sesgo de medición, pero la escolaridad **desplaza la distribución real de habilidad**, y eso sí justifica un umbral dependiente de la escolaridad |

**Conclusión nueva, más fuerte y constructiva:** el problema no es que se corrija por escolaridad,
sino **cómo** se corrige. La corrección vigente es direccionalmente correcta pero está mal
calibrada —demasiado alta— y mal especificada —un escalón donde corresponde una curva—. Una
corrección continua alcanza **el mismo desempeño diagnóstico con una fracción de la inequidad**.
