# Bloque V4 — Teoría de respuesta al ítem, DIF y curvatura sobre la métrica latente

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
