# Bloque V3 — Supuestos, especificación, influyentes y potencia

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
