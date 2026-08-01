**Tabla 2.** Falsación del escalón educativo del ACE-III, forma de la asociación y consecuencias de la regla vigente. Modelos ajustados por edad y sexo, errores robustos HC3.

### A. ¿Existe la discontinuidad que la regla supone? — análisis principal

Magnitud del escalón en 12 años, estimada con un indicador `1[educación ≥12]` dentro de un modelo de educación continua:

| Cohorte | n | Escalón estimado [IC95%] | p | **Salto que impone la regla** |
|---|---:|---|---|---:|
| Comunitaria | 762 | **+0,55 [−2,09; +3,20]** | 0,68 | **18** |
| Clínica | 2112 | **+0,13 [−2,56; +2,83]** | 0,92 | **18** |

*El límite superior de ambos intervalos excluye la regla por un factor de seis, en dos cohortes con selección opuesta. Es una falsación, no una discrepancia de modelo: no depende del anclaje, del punto de operación ni de la forma funcional elegida.*

**Regresión discontinua local** (ventanas alrededor de 12 años, término lineal):

| Ventana | Comunitaria | Clínica |
|---|---|---|
| 10–13 años | +1,58 [−4,57; +7,73] p=0,62 | −2,50 [−8,66; +3,66] p=0,43 |
| 9–14 años | +2,16 [−2,17; +6,49] p=0,33 | −3,52 [−8,07; +1,03] p=0,13 |
| 8–15 años | +1,68 [−1,78; +5,15] p=0,34 | −0,57 [−4,05; +2,90] p=0,75 |

**Diferencia cruda 11 vs 12 años**, sin modelo: +3,42 [−0,25; +7,10] en la comunitaria (n=16 y 115) y +1,82 [−2,32; +5,97] en la clínica (n=70 y 447).

**Control negativo con una medida funcional independiente.** En la cohorte comunitaria se dispone del Activities of Daily Living Questionnaire (ADLQ), respondido por informante (n=730). El ADLQ es **educacionalmente neutro** (r=0,057 con los años de escolaridad), de modo que sirve para descartar que el salto refleje diferencias reales de estado funcional entre quienes tienen 11 y 12 años. No lo hace: el escalón estimado pasa de +0,55 a **+0,61 [−2,05; +3,28] (p=0,65)** al ajustar por ADLQ, y el salto persiste **dentro** de cada estrato funcional — en el estrato con peor función, **0 % de los de 11 años quedan marcados frente a 47 % de los de 12**. La discontinuidad no se explica porque el grupo de 11 años esté funcionalmente mejor.

⚠️ *El ADLQ **no** se usa como estándar de referencia diagnóstico y no lo es: no correlaciona con el ACE-III en esta muestra (r=0,046) y quienes la regla marca no tienen peor función (en el tramo 7–11, 1,25 frente a 1,53). En una muestra comunitaria de adultos mayormente funcionales tiene escasa varianza (19,5 % en cero exacto). Se emplea sólo como control negativo.*

**Efecto credencial**: indicadores simultáneos en 7 y 12 años. Comunitaria: primaria completa +0,34 (p=0,85), secundaria completa +0,65 (p=0,66) — sin efecto credencial. Clínica: ≥12 años −1,79 (p=0,22), pero **≥7 años −7,23 (p<0,001)**, artefacto de la concentración de casos en 7 años (n=309) que señala fragilidad de la extrapolación hacia el extremo inferior en esa cohorte.

### B. Consecuencia: la positividad de la regla, año por año

Porcentaje por debajo del corte vigente (68 si <12 años; 86 si ≥12):

| Años de educación | 2 | 4 | 6 | 7 | 9 | 10 | **11** | **12** | 14 | 17 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Comunitaria** | 76 | 72 | 31 | 24 | 17 | 12 | **6** | **52** | 52 | 17 |
| *(n)* | *21* | *18* | *54* | *144* | *41* | *25* | *16* | *115* | *21* | *30* |
| **Clínica** | 80 | 90 | 59 | 64 | 48 | 41 | **43** | **81** | 54 | 49 |
| *(n)* | *15* | *21* | *96* | *309* | *107* | *81* | *70* | *447* | *54* | *243* |

*Descenso monótono con la escolaridad seguido de un salto abrupto exactamente donde cambia el corte: **8,4 veces** en la cohorte comunitaria (6,2 % → 52,2 %) y **1,9 veces** en la clínica (42,9 % → 81,2 %). El salto no está en el rendimiento —que es continuo— sino en la regla.*

### C. Forma de la asociación: cóncava y continua, con la misma curvatura en ambas cohortes

| Cohorte | n | Pendiente lineal única | Curvatura b₂ [IC95%] | p |
|---|---:|---|---|---|
| Comunitaria | 762 | +1,64 [1,48; 1,80] | −0,084 [−0,109; −0,058] | 1×10⁻¹⁰ |
| Clínica | 2112 | +1,89 [1,71; 2,08] | −0,078 [−0,106; −0,051] | 2×10⁻⁸ |

**Pendiente marginal por año de educación (puntos ACE-III)**

| Años de educación | 3 | 7 | 12 | 17 |
|---|---|---|---|---|
| Comunitaria | +2,98 [2,48; 3,48] | +2,31 [2,00; 2,62] | +1,47 [1,34; 1,61] | +0,64 [0,38; 0,90] |
| Clínica | +3,31 [2,78; 3,84] | +2,68 [2,35; 3,01] | +1,90 [1,74; 2,05] | +1,11 [0,82; 1,41] |

**Replicación entre cohortes** (modelo único con interacciones): la forma completa difiere (χ²=14,96; 2 gl; p=6×10⁻⁴) por el **término lineal** (χ²=14,95; 1 gl; p=1×10⁻⁴), esperable bajo selección diferencial; la **curvatura no difiere** (χ²=0,01; 1 gl; **p=0,92**; diferencia +0,002 [−0,035; +0,039], y p=0,90 en soporte etario común).

⚠️ *Esto es **no-refutación** de una forma común, no demostración de identidad: el intervalo admite que la curvatura clínica sea entre 0,5 y 1,45 veces la comunitaria.*

**Especificación verificada:** el spline cúbico natural (4 gl) no mejora sobre la cuadrática en ninguna cohorte (p=1,00 y p=0,33). Supuestos: Breusch-Pagan p=8×10⁻¹⁴ (HC3 justificado); factor de inflación de la varianza ≈1,0 con educación centrada.

### D. Un corte continuo como ilustración — y por qué NO se propone como herramienta

Se construyó un corte que varía con la educación siguiendo la forma estimada, anclado a 86 en la mediana educativa del grupo ≥12 años. **Se presenta como ilustración de la magnitud del desajuste, no como reemplazo clínico.** Cuatro razones, todas verificadas:

| Objeción | Verificación |
|---|---|
| **El anclaje deja el corte en la media condicional**, de modo que aplanar la positividad es mecánico y no evidencia de calibración | El ACE-III esperado en el ancla es 86,3 (comunitaria): el corte queda a **0,3 puntos de la media condicional (z=−0,03)**; en la clínica z=+0,56 |
| **El aplanamiento no identifica la forma funcional** | Rango de positividad entre tramos: cuadrática 5,4 · lineal 13,9 · log 10,9 (comunitaria); pero en la clínica **la lineal aplana mejor** (3,2 frente a 5,5) |
| **El anclaje es un parámetro libre con mucha palanca** | Positividad global según dónde se ancle: 60,9 % (12 años) · 53,4 % (13,2) · 43,3 % (15, el usado) · 37,5 % (17) |
| **La curva no transfiere entre cohortes** | Diferencia entre ambas curvas: +5,7 puntos a 0 años de escolaridad, +3,3 a 7 años, 0 en el ancla. Aplicar la curva clínica a la comunitaria lleva la positividad de 43,3 % a 52,5 % |

*Lo que **no** es un problema, y conviene reportarlo: no hay sobreajuste. Validación cruzada de 10 pliegues, calibrando en 9/10 y aplicando al pliegue no visto: 43,3 % dentro de muestra frente a 43,2 % fuera (comunitaria) y 64,7 % frente a 64,5 % (clínica); discordancia individual 0,92 % y 0,14 %.*

### E. La comparación justa: a tasa global de derivación igualada

Anclando el corte continuo para que marque exactamente la misma proporción global que la regla vigente:

| | <7 años | 7–11 años | ≥12 años | **Rango entre tramos** |
|---|---:|---:|---:|---:|
| **Comunitaria** — escalón vigente | 55,6 | 20,8 | 40,6 | **34,8 pp** |
| **Comunitaria** — corte continuo | 41,2 | 38,4 | 34,7 | **6,6 pp** |
| **Clínica** — escalón vigente | 74,5 | 55,3 | 61,9 | **19,2 pp** |
| **Clínica** — corte continuo | 54,3 | 61,9 | 61,6 | **7,5 pp** |

*A igual carga de derivación, la regla vigente distribuye la positividad de forma cinco veces más desigual entre estratos educativos. Reclasificación: 14,4 % y 15,2 %. Es la comparación que no depende del anclaje, y el resultado sobrevive.*

*El desajuste tiene **dos direcciones**: la regla **sobre-marca** el estrato de menor escolaridad (55,6 % frente a 41,2 %) y **sub-marca** el intermedio (20,8 % frente a 38,4 %). Ambas son consecuencia del mismo defecto: una banda única de 0 a 11 años juzgada contra un solo número.*

### F. La varianza también depende de la educación

Desviación estándar residual del modelo, modelada como función de la educación:

| Años de educación | 2 | 7 | 12 | 17 | p (educación) |
|---|---:|---:|---:|---:|---|
| Comunitaria | 7,3 | 5,7 | 4,4 | 3,4 | 2×10⁻¹⁰ |
| Clínica | 10,4 | 8,9 | 7,6 | 6,4 | 3×10⁻⁹ |

Observada por tramo (comunitaria): 13,0 · 10,2 · 8,0.

*Un umbral fijo aplicado a un estrato con mayor dispersión residual pierde especificidad **aunque la media esté perfectamente centrada**. Cualquier corrección adecuada debe ser de **localización y escala**, no sólo de localización. Es la línea que este análisis deja abierta y no resuelve.*

### G. Sensibilidades (curvatura b₂)

| Análisis | Comunitaria | Clínica |
|---|---|---|
| **Principal** (ACE-III armonizado) | **−0,084** | **−0,078** |
| Sin armonizar el ítem de reconocimiento | −0,079 | — |
| Sin excluir el solapamiento entre cohortes | −0,081 (n=776) | −0,078 |
| Columna de total del instrumento en vez de suma de ítems | −0,076 | — |
| Ajustando por ola de reclutamiento | −0,087 | — |
| Excluyendo puntajes de techo (<95) | −0,084 (n=731) | −0,085 (n=2018) |
| Restringido a edad 46–85 | −0,084 | −0,075 (n=2027) |
| Restringido a educación ≤18 años | −0,073 (n=732) | −0,058 (n=1992) |
| Sólo ítems validados por doble fuente | — | −0,071 (n=2018) |
| Ajustando por servicios del hogar | −0,083 (n=714) | — |
| + provincia de nacimiento | −0,082 (n=714) | — |
| + **ocupación de toda la vida** | −0,081 (n=714) | — |
| + síntomas depresivos (Yesavage-15) | −0,087 (n=686) | — |
| Edad con spline natural (4 gl) | −0,082 | −0,079 |
| Excluyendo los ítems con carga de alfabetización | −0,073 | −0,065 |

*La curvatura se mantiene entre −0,058 y −0,087 en los quince análisis, sin cambio de signo. No se atenúa al condicionar por ocupación de toda la vida ni por nivel socioeconómico del hogar, ni al retirar los ítems de escritura, comprensión lectora y lectura de palabras irregulares: el gradiente educativo del ACE-III no es reducible a sesgo alfabetizacional de ítem.*

**Curvatura por dominio (comunitaria, b₂ reescalado a 100 puntos)**

| Dominio | Máximo | % en techo | b₂ |
|---|---:|---:|---|
| Visuoespacial | 16 | 24,8 | −0,109 |
| Lenguaje | 26 | 23,0 | −0,096 |
| Atención/orientación | 18 | 23,1 | −0,084 |
| **Memoria** | 26 | **3,7** | **−0,056** |
| **Fluencia** | 14 | **4,3** | **−0,050** |

*Hay dosis-respuesta entre densidad de techo y curvatura, lo que indica un componente de compresión de escala. Pero la concavidad **sobrevive en memoria y fluencia**, los dominios prácticamente sin techo: no es enteramente métrica. Estos datos no permiten cuantificar la proporción sin un análisis sobre la métrica latente.*

*ACE-III: Addenbrooke's Cognitive Examination III; gl: grados de libertad; IC95%: intervalo de confianza del 95%; pp: puntos porcentuales. Pendiente marginal: dY/dEdu = b₁ + 2·b₂·educación, con IC95% por método delta sobre la matriz HC3. b₂ negativo indica concavidad. **Diseño transversal, sin estándar de referencia diagnóstico: no se estima exactitud y ninguna cifra debe leerse como sensibilidad o especificidad.***
