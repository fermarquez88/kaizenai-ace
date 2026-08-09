# Auditoría del manuscrito ENVIO_CAN2026

**Revisión adversarial por cuatro revisores independientes**

*Neurology · Alzheimer's & Dementia · The Lancet / Lancet Regional Health – Americas · Nature*

**Fecha:** 9 de agosto de 2026
**Objeto:** `manuscrito/ENVIO_CAN2026_v2.md` y los bloques de análisis V25 a V28
**Encargo:** Fernando Márquez

---

## Cómo se hizo esta auditoría

Se encargó a cuatro revisores independientes, cada uno con el perfil y los estándares de una revista
distinta, una revisión **adversarial**: la consigna explícita fue encontrar lo que falla, no validar.
Cada uno recibió el manuscrito completo, el material suplementario, las salidas numéricas en JSON y
**el código fuente de los análisis**, con instrucción de leer el código y no sólo los resultados.
Ninguno vio la revisión de los otros.

Las objeciones cuantificables **se verificaron una por una** antes de aceptarlas, corriendo el código
correspondiente. El resultado de esa verificación abre este documento, porque cambia el peso que hay
que dar a cada objeción: algunas se confirmaron y obligaron a rehacer análisis; otras se sostienen
como juicio pero no como error demostrable.

> **Advertencia de lectura.** Este documento reproduce las cuatro revisiones tal como fueron
> emitidas, incluidas las afirmaciones que la verificación posterior matizó o no pudo confirmar.
> Donde eso ocurre se señala en el cuerpo. Se conserva el texto original porque el valor de una
> auditoría está en lo que dijo, no en lo que resistió.

---

## Resumen ejecutivo

### Recuento de objeciones

| Revisor | Fatales | Mayores | Moderadas | Menores | Recomendación |
|---|---|---|---|---|---|
| **Neurology** | 4 | 15 | 12 | 8 | Rechazo con invitación a reenviar |
| **Alzheimer's & Dementia** | 3 | 10 | 6 | 4 | **Rechazo** (no «con invitación») |
| **Lancet** | 3 | 11 | 10 | 5 | Reorientar el mensaje |
| **Nature** | 4 | 7 | 6 | 6 | **Rechazo** para el grupo Nature |

### En qué convergen los cuatro, sin haberse consultado

**1. El grupo control es el punto de quiebre.** Los cuatro llegaron por caminos distintos a la misma
conclusión: todo lo que depende del grupo control —el gradiente de 33,4 puntos porcentuales, la
comparación de reglas, la afirmación de equidad— no está identificado. El bloque V19 del propio
repositorio muestra que los 342 controles rinden entre −1,3 y −2,7 desvíos en pruebas que **no**
forman parte del criterio, con normas ya ajustadas por educación, y que sólo el **4,1 %** de los
controles con menos de 7 años de escolaridad no tiene ninguna prueba baja, frente al **28,7 %** de los
de 12 o más.

**2. El criterio de control se eligió por el procedimiento equivocado.** Se adoptó el peldaño con el
valor p más alto de una escalera de seis candidatos (p = 0,041 · 0,000 · 0,215 · **0,504** · 0,025 ·
0,0002). Seleccionar sobre la no significación no acredita independencia. Y la condición impuesta
—igualdad de **tasas de aceptación**— no es la correcta: lo sería la igualdad de **sensibilidad al
deterioro**, y como la prevalencia verdadera sí difiere por escolaridad, forzar tasas iguales **obliga**
a que el grupo de menor escolaridad esté más contaminado, justo en la dirección que infla el gradiente.

**3. El bloque V26 contenía errores demostrables.** Tres revisores independientes señalaron el signo
invertido de la desatenuación; dos, el carácter tautológico de la «predicción falsable»; dos, la no
identificación de la métrica latente. **Los tres se verificaron y se confirmaron.**

**4. Lo que sobrevive intacto.** Los cuatro coinciden, y lo consignan explícitamente:

- La **reconstrucción documental** de la procedencia del 86 y del 68, y la constatación de que el
  umbral de los 12 años no aparece en ninguna fuente primaria. Es el mejor aporte del trabajo y no
  depende de ningún supuesto estadístico.
- La **forma funcional** curvilínea, replicada en dos cohortes de selección opuesta y ahora también en
  un segundo instrumento.
- La **falsación de la discontinuidad** con prueba de equivalencia y placebo sobre los catorce cortes.
  Tres revisores la califican de aporte metodológico genuino, y destacan que detecte el artefacto de
  amontonamiento en 7 años como prueba de que el procedimiento discrimina.
- La **ausencia de sesgo de medición por ítem**, que mata limpiamente la explicación «los ítems están
  sesgados».

---

# Verificación de las objeciones cuantificables

Antes de reproducir las revisiones, el resultado de comprobar sus afirmaciones contra el código.

## Confirmadas

### El signo de la desatenuación estaba invertido

`V26_dispersion_metrica_latente.py` calculaba `var_verdadera = var(θ̂) − E[SE²]`. Para un estimador de
media posterior la ley de la varianza total da lo contrario:

> Var(θ) = Var(E[θ|X]) + E[Var(θ|X)] = Var(θ̂_EAP) + E[SE²]

**Comprobación decisiva:**

| Cantidad | Valor |
|---|---|
| Var(EAP) | 0,9090 |
| E[SE²] | 0,0746 |
| **Var(EAP) + E[SE²]** | **0,9836** ≈ 1, la varianza de la previa |
| Var(EAP) − E[SE²] | 0,8344, incompatible con el propio modelo |

La serie publicada 0,697 · 0,395 · 0,533 era incorrecta. **Objeción confirmada.**

### El bootstrap de la varianza verdadera estaba dominado por el recorte

La pendiente se estimaba sobre `log(clip(r² − SE², 1e-6))`. Verificado: **140 de 342 observaciones
(40,9 %)** caen en el recorte y reciben log(1e-6) = −13,82 como variable dependiente. La cifra
publicada carecía de interpretación. **Objeción confirmada.**

### La «predicción falsable» no era falsable

La relación *desvío del puntaje ≈ pendiente local × desvío de habilidad* es la identidad del método
delta de primer orden. El revisor de Nature la simuló bajo cuatro escenarios sustantivamente opuestos:

| Escenario (dispersión **verdadera** de habilidad) | Razón tramo 1 | 2 | 3 |
|---|---|---|---|
| A · como en el paper (0,74 / 0,47 / 0,61) | 0,96 | 0,92 | 0,90 |
| B · **exactamente constante** (0,60 / 0,60 / 0,60) | 0,95 | 0,92 | 0,90 |
| C · **compresión en las personas** (1,00 / 0,70 / 0,40) | 0,99 | 0,92 | 0,94 |
| D · **compresión inversa** (0,40 / 0,70 / 1,00) | 0,93 | 0,92 | 0,80 |

Las razones son indistinguibles entre el escenario que el manuscrito afirmaba y su negación exacta.
**Objeción confirmada, y concedida sin reservas: fue un error de encuadre.**

### La partición entre escala y personas no está identificada

Un modelo de respuesta al ítem identifica la habilidad sólo hasta transformación monótona. Verificado
sobre el mismo modelo ajustado:

| Métrica | Por el instrumento | Por la habilidad |
|---|---|---|
| θ, previa normal (la que usaba el manuscrito) | **1,59×** | 1,22× |
| τ = E[ACE\|θ], puntaje verdadero de Lord | **1,00×** | **1,74×** |

Mismo modelo, mismos datos, conclusión opuesta. **Objeción confirmada.**

### La comparación del IFS entre cohortes no es válida

El propio material suplementario, bloque V12, documenta: *«Las **series motoras** se descartaron por
**escalas distintas entre bases (máximo 3 frente a 6)**»*. Las series motoras son el subtest 1 del IFS,
de modo que los totales de las dos bases no están en la misma escala. **Objeción confirmada.** Invalida
la forma funcional, la replicación de curvatura, la discontinuidad y el placebo del bloque V27; no
invalida lo que usa una sola base.

### El perfil del grupo control, y una frase codificada

`V19_perfil_controles.json` confirma los z negativos en toda la batería, y la frase interpretativa que
afirma lo contrario —«los tres tramos se ubican en rango y sin diferencias sistemáticas»— **está
codificada como cadena literal** en la línea 144 del script, no derivada de los resultados.
**Objeción confirmada.**

## No verificadas

- Que las cifras de contaminación **60,7 % y 48,9 %** no existan en ningún archivo del repositorio:
  la búsqueda por subcadena devolvió coincidencias que pueden ser espurias. **Requiere comprobación
  dirigida.**
- Las objeciones sobre gobernanza de datos de ReDLat, interpretación normativa y estructura del
  trabajo son juicios editoriales, no errores demostrables.

## Corregido tras la verificación

El bloque V26 se rehízo: se eliminó la desatenuación escalar y el bootstrap defectuoso, se sustituyeron
por un **GRM multigrupo con media y varianza latentes libres por tramo** —que no usa el EAP y no
arrastra su contracción—, se incorporó el Levene sobre θ, y se declaró explícitamente la no
identificación de la métrica.

| Tramo | n | Media latente | DE latente |
|---|---|---|---|
| menos de 7 años | 74 | −0,555 | 0,732 |
| 7 a 11 | 118 | −0,062 | 0,411 |
| 12 o más | 150 | +0,687 | 0,598 |

Razón entre extremos **1,22×** frente a **1,74×** en el puntaje bruto, con patrón **no monótono**.

<div style="page-break-before: always"></div>

# Revisor 1 — *Neurology*

*Perfil: exactitud diagnóstica y clasificación de evidencia (AAN).*

> **Nota operativa previa del revisor:** el manuscrito no contiene ninguna mención al IFS, al MMSE ni
> a ReDLat. V27/V27b/V28 no están incorporados y tampoco figuran en `CIFRAS_MAESTRAS.json`. La revisión
> los trata como material candidato.

## FATAL

**F1. La desatenuación del error de medición tiene el signo invertido.** Para un estimador bayesiano de
media posterior la ley de la varianza total da **var verdadera = var(EAP) + E[SE²]**. El EAP ya está
contraído; restarle otra vez el error descuenta la contracción dos veces. Con el signo corregido las DE
pasan de 0,697 · 0,395 · 0,533 a **0,784 · 0,538 · 0,677**, y la razón entre extremos de 1,31 a **1,16**.
*Qué pediría:* GRM multigrupo con medias y varianzas latentes libres por tramo, o valores plausibles.

**F2. «Sobre la habilidad latente desaparece» es no-significación presentada como ausencia.** Tres
problemas, cada uno suficiente: (a) el límite inferior del intervalo, −0,0454, implica conservar hasta
el **55 %** de la pendiente bruta; (b) el propio V26 **rechaza la homocedasticidad en θ** (Levene
W = 8,157, **p = 3,5×10⁻⁴**) y eso no aparece en el manuscrito; (c) el nulo es un artefacto de forma:
una pendiente lineal sobre una función en U es ≈ 0 por construcción.

**F3. El bootstrap de la pendiente de la varianza verdadera está mal especificado.** Aproximadamente el
40 % de las observaciones reciben `log(1e-6) = −13,8`. El resultado publicado carece de interpretación.

**F4. «Lo produce la escala» no es contrastable con un GRM unidimensional.** La escala θ es la que hace
normal a la población de calibración, por definición de la previa. Con **r(θ, bruto) = 0,98**, θ es un
reetiquetado no lineal del mismo puntaje. Y la «predicción falsable» es la identidad del método delta:
**se cumple necesariamente**.

## MAYOR

**M1.** El estrechamiento bruto observado no es monótono (14,3 / 8,1 / 8,2) y el «13,2 → 5,8» es
extrapolación fuera del soporte: la escolaridad media del tramo bajo es 4,1 años y la del alto 14,7.

**M2.** Las DE por tramo son incondicionales: el Levene compara cantidades que contienen la varianza
*entre* niveles educativos dentro de cada banda. Debe repetirse sobre residuos del modelo de posición.

**M3.** El grupo «sin deterioro» admite el 72 % de los DCL clínicos, con contaminación diferencial
(60,7 % frente a 48,9 %). Y los controles de ≥12 años puntúan **3,27 DE por debajo** de los controles
normativos publicados con escolaridad equivalente.

**M4.** El criterio de control se eligió maximizando un p de no significación (0,504 entre seis
candidatos). No acredita independencia; garantiza un p inflado.

**M5.** El IC de los 33,4 pp corresponde a un estadístico máx − mín seleccionado, que **no puede cubrir
el cero**. Debe informarse el contraste preespecificado.

**M6.** El bootstrap de equidad no propaga la incertidumbre del modelo normativo ni del emparejamiento:
el IC del ΔYouden **está subestimado**.

**M7.** «Sin costo demostrable» es una afirmación de no inferioridad sin margen preespecificado, y el
punto estimado **no es estable**: el ΔYouden va de −0,023 a +0,039 según la definición de control.

**M8.** El sesgo bidireccional que se compensa es **la firma de multidimensionalidad**, no de ausencia
de sesgo. La cancelación es una propiedad de esta mezcla de ítems, no de equidad. Y la evidencia de
dimensionalidad es débil: primer factor 35,8 % de la varianza, tres autovalores > 1, Q3 máximo 0,348.

**M9.** El DTF continuo, significativo y mayor, no se informa: **−0,07 por año, p = 4,8×10⁻⁶**, ≈ 1,2
puntos sobre el rango, frente a los 0,34 del contraste dicotómico que sí se publica. Reporte selectivo.

**M10.** El GRM se calibra sobre 2785 casos, **72,8 % clínicos**, y el θ resultante se usa sólo sobre
342 controles comunitarios, pese a que la Limitación octava reconoce que tres ítems no son invariantes
entre cohortes.

**M11.** El colapso de categorías, guiado por los datos, fija la curva característica de la que sale
todo el mecanismo. La TCC reconstruida **no alcanza el techo** que el argumento invoca.

**M12.** La afirmación de mejor detección en el tramo intermedio descansa en **cuatro pacientes**
(54/63 frente a 58/63), sin IC ni McNemar. Y la frase sobre los once casos no detectados afirma una
intersección que las propias cifras excluyen.

**M13.** Multiplicidad: el control por familia cubre sólo la discontinuidad. La equivalencia a **±3**
**no sobrevive Bonferroni** sobre las seis pruebas declaradas.

**M14.** El extremo del salto descansa en dieciséis personas: el IC exacto de 1/16 va de 0,2 % a 30 %.

**M15.** La dispersión **no está entre los objetivos declarados** y no tiene clase de evidencia
asignada, pese a ser la segunda cláusula del título. Y se declara STARD sin diagrama de flujo,
cegamiento ni tratamiento de indeterminados.

## MODERADA (selección)

Dos valores distintos para la misma cantidad (1,22 en el texto, 1,31 implícito en el pie de figura) ·
el p = 0,051 atribuido a la comparación equivocada · la descomposición no cierra (1,595 × 1,218 = 1,94
frente a 1,745 observado) · las razones predicha/observada tienen deriva sistemática y el criterio de
éxito está fijado dentro de un `print` · «cerca del techo» no describe los datos: sólo el 2,7 % del
tramo alto está a ≤3 puntos del techo · el EEM se informa sin su intervalo, que va de 1,5 a 9,3 EEM por
escalón · p = 0,764 atribuido al contraste equivocado · V28 se contradice consigo mismo · V28 excluye
los 42 sujetos con CDR = 0,5, que es sesgo de espectro · V28 declara el estrato inestimable y luego lo
usa · V27b correlaciona sobre cinco puntos, tres del mismo estudio · el «gradiente» por corte del IFS
está saturado.

## Lo que el revisor consigna como inusualmente bien hecho

La reconstrucción documental · la prueba de placebo sobre los catorce cortes · declarar que la planitud
de la corrección continua es una identidad algebraica y no un hallazgo · la corrección de Harvey
implementada con el signo correcto y verificada empíricamente · la escalera de definiciones de control
de V22, que muestra robustez genuina y **no está en el manuscrito** · el bloque A de V28, que declara la
infactibilidad del estrato de baja escolaridad *antes* de mirar los resultados: «conducta ejemplar».

<div style="page-break-before: always"></div>

# Revisor 2 — *Alzheimer's & Dementia*

*Perfil: psicometría, normas neuropsicológicas y equidad diagnóstica en Latinoamérica.*

> **Recomendación: rechazo.** No «rechazo con invitación»: la objeción 1 de la revisión previa no fue
> resuelta, y la evidencia generada desde entonces por el propio equipo **la agrava**.

## FATAL 1 — El criterio de control se eligió maximizando un p de no-asociación, que es la condición equivocada

| Peldaño | n | p (χ² control × tramo) | gradiente |
|---|---|---|---|
| 1. reconocimiento ≥10 | 663 | 0,041 | 44,0 pp |
| 2. + sin ACV | 508 | 0,000 | 34,4 pp |
| 3. + … | 366 | 0,215 | 35,0 pp |
| **4. el publicado** | **342** | **0,504** | **33,4 pp** |
| 5. + … | 172 | 0,025 | 41,8 pp |
| 6. + … | 128 | 0,0002 | 40,5 pp |

Y el p de 0,504 **se recupera agregando** el criterio «sin traumatismo de cráneo», que excluye a 154
personas. El componente `func_adlq_basica` está marcado `"admitido": false` en V18 (p_edu = 0,0176) **y
sin embargo integra el criterio final**.

**El punto central:** «igual tasa de aceptación» y «igual sensibilidad al deterioro» sólo coinciden si
la prevalencia verdadera es independiente de la escolaridad. **El propio manuscrito afirma lo
contrario** (10,7 % frente a 21,4 % sin educación formal). Forzar tasas iguales **obliga** a que el
grupo control de baja escolaridad esté más contaminado.

**Mecanismo verificable:** el criterio usa aciertos crudos de reconocimiento sin corregir falsos
positivos. Entre quienes lo pasan, el **reconocimiento corregido** tiene z = **−2,55 · −1,28 · −0,46**
(p < 0,001). La neutralidad educativa celebrada **es un artefacto del sesgo de respuesta**.

## FATAL 2 — El grupo control no se ve normal en ninguna prueba, y el archivo que lo demuestra no se envía

| Prueba | z <7 | 7-11 | ≥12 | % con z < −1,5 |
|---|---|---|---|---|
| Trail Making A | **−2,73** | −2,07 | −0,68 | 43,0 % |
| Rey · reconocimiento corregido | **−2,55** | −1,28 | −0,46 | 31,0 % |
| Trail Making B | −1,96 | −2,10 | −0,62 | 35,4 % |
| Rey · recuerdo inmediato | −1,62 | −1,67 | −0,76 | 38,6 % |
| Dígitos directos | −1,32 | −1,29 | −0,78 | 46,8 % |

Sin ninguna prueba bajo −1,5 z: **4,1 % · 2,5 % · 28,7 %** (p < 0,001).

Estar 2,7 desvíos por debajo de una norma **que ya corrige por escolaridad** no es «rendir conforme a lo
esperado»: es deterioro. Y el texto interpretativo que afirma lo contrario **está codificado como cadena
literal** en el script. El material no figura en el suplementario enviado.

## FATAL 3 — La defensa cuantitativa del gradiente descansa en seis personas

El «35 % de contaminación» sale de la definición «D4 todo», con n = 87 controles y **6 en el tramo de
menos de 7 años**. Esa definición tiene p_edu = 0,000, es decir, es una de las que el propio criterio
declarado descarta. Y las cifras **60,7 % y 48,9 % no aparecen en ningún archivo del repositorio**,
violando la regla que el propio proyecto estampa en `CIFRAS_MAESTRAS.json`. *(Esta última afirmación no
pudo verificarse de forma concluyente; ver la sección de verificación.)*

## MAYOR (síntesis)

**4.** El intervalo de la pendiente latente traducido a razón de desvíos es **[0,58 · 1,58]**: los datos
son compatibles con un estrechamiento de hasta 1,58, más de lo que el manuscrito reporta como
observado. **5.** El signo invertido del EAP, con la tabla de valores correctos, y la incoherencia entre
el 1,22 del texto y el 1,31 del pie de figura. **6.** La métrica θ no está identificada y la «predicción
falsable» es una identidad; la calibración mezcla dos poblaciones que el propio V4-F declara no
invariantes. **7.** V26 esconde que sobre θ la dispersión **sí** es heterogénea, y no contrasta la
hipótesis alternativa —contaminación diferencial— que predice los mismos datos. **8.** Las cifras
titulares son extrapolación fuera del soporte. **9.** **La comparación ACE-III / IFS no es legítima**:
el suplementario documenta escalas distintas entre bases para las series motoras; además `max(bruto)`
resuelve duplicados por el máximo y no existe bloque de armonización análogo al del ACE-III. **10.** Un
corte que señala al 88 % del propio grupo control, sobre una muestra 3,27 DE por debajo de la norma, no
permite leer los percentiles como evidencia de inequidad. **11.** V28 no aporta: el AUC de 0,948 no
cuantifica nada del ACE-III, el estrechamiento del MMSE se estima sobre 21 personas y se contradice con
su propio Levene (p = 0,155), y el 31,1 % está exactamente en el techo. **12.** El punto de operación
único sigue sin resolverse. **13.** El título conserva el término normativo, es una afirmación universal
sostenida sobre dos cortes en una provincia, y **contradice la propia conclusión de V26**.

## MODERADA — Inconsistencias internas verificables

| Cantidad | Cuerpo | Suplementario | JSON |
|---|---|---|---|
| n de controles por tramo | 74 · 118 · 150 | **V16: 74 · 216 · 316** | 74 · 118 · 150 |
| σ del ACE a 0 años | 13,2 | **V16: 12,9** | 13,183 |
| Percentil del corte 68 sin escolaridad | 82 | **V16: 86** | 82,0 |
| Youden de la regla vigente | 0,549 | **V17-B: 0,552** | 0,5487 |
| % señalado en <7, regla vigente | 53,7 % | **V17-B: 60,3 %** | 53,7 % |

Los bloques V16 y V17-B están calculados sobre conjuntos de controles superados y **el suplemento los
sigue enviando**. Además: el manuscrito afirma que el suplemento contiene las «siete definiciones
alternativas» y **no las contiene**; y la cobertura de la clasificación de referencia falta de manera
diferencial por escolaridad (92,4 % · 93,9 % · 89,5 %; p = 0,006), sin discutirse.

## ¿Debería dividirse en dos manuscritos?

**Sí, y con más razón que en agosto.** *Manuscrito A* —listo o casi—: forma funcional, falsación,
ausencia de DIF y procedencia documental; no requiere grupo control ni clasificación de referencia y
sobrevive intacto. *Manuscrito B* —requiere **rediseño**, no revisión—: la comparación de reglas exige
un grupo control definido por referencia independiente del cribado, reclutado en el estrato de baja
escolaridad. **Y el bloque V26 no debería ir en ninguno de los dos en su forma actual.**

## Lo que el revisor consigna como de primera calidad

La forma funcional · la falsación de la discontinuidad, «el mejor aporte metodológico del trabajo» · la
ausencia de sesgo de medición · la reconstrucción documental · y **la honestidad de varios bloques
internos**: la detección y corrección del sesgo de Harvey, el registro de los tres hallazgos que
obligaron a cambiar conclusiones, el retiro del desenlace de deterioro leve, el abandono del «once
veces», y el veredicto de factibilidad de V28 escrito antes de mirar los resultados. *«Ese estándar es
superior al de la mayoría de los manuscritos que reviso. El problema no es la voluntad de autocrítica:
es que en los tres puntos donde la autocrítica habría desmontado el titular —la definición de control,
el nulo de V26 y la armonización del IFS— el proceso se detuvo justo antes.»*

<div style="page-break-before: always"></div>

# Revisor 3 — *The Lancet / Lancet Regional Health – Americas*

*Perfil: salud pública, equidad, generalización y consecuencias para la política sanitaria.*

> **Encuadre del revisor:** el trabajo tiene un núcleo excelente envuelto en una afirmación de equidad
> que, con estos datos, no está identificada. Los tres bloques nuevos no refuerzan la tesis: **la
> desestabilizan**. En particular, V27b contiene la evidencia más fuerte del repositorio y apunta en
> una dirección distinta de la que el manuscrito defiende.

## FATAL 1 — No se puede separar «efecto de la escolaridad» de «el corte no transporta a San Juan»

- Tramo de 12 o más años de San Juan: n = 150, escolaridad **14,7 años**, IFS **22,17**.
- Controles de Torralva 2009 (INECO, Buenos Aires): n = 26, escolaridad **14,5 años**, IFS **27,4**.
- A escolaridad prácticamente idéntica, **5,2 puntos de diferencia**.

Dentro de San Juan, todo el gradiente educativo del IFS va de 14,9 a 22,2: **7,3 puntos sobre 10,6 años
de escolaridad**. La brecha de sitio a escolaridad constante equivale al **71 % de todo el rango
educativo interno de la muestra**. Y San Juan con 14,7 años coincide con los controles chilenos de
**11,9 años**: el punto atípico es el grupo de n = 26 de un centro terciario porteño del que sale el
corte que se aplica en todo el país.

La misma señal está en el ACE-III y el manuscrito no la lee: **la media de los controles con 12 o más
años es 85,3 contra un corte de 86**. En el diseño de una puerta las tres tasas son 67,7 · 52,5 · 62,0 %:
**todos los tramos por encima del 50 %**.

**El remate está en `V19_perfil_controles.json`:** aplicadas las normas publicadas —ya estratificadas
por educación—, el z del IFS es **−1,38 · −1,02 · −1,19 por tramo, p = 0,166**. La norma educativa borra
el gradiente y deja **un corrimiento uniforme de ≈ 1,2 DE**. Ésa es la descomposición que el manuscrito
necesita y no hace.

**Consecuencia de política:** bajo la lectura del manuscrito, la solución es una corrección continua por
escolaridad. Bajo la lectura alternativa, esa corrección es un parche que deja intacto el problema
mayor: **ningún corte importado de una muestra metropolitana pequeña sirve en la provincia, a ningún
nivel educativo**.

## FATAL 2 — El grupo control, con déficit diferencial por escolaridad

*(Coincide con el revisor de A&D; se remite a su tabla.)* Añade: el gradiente por umbral de
reconocimiento es **33,4 · 27,3 · 34,8 · 21,3** y por peldaño **44,0 · 34,4 · 35,0 · 33,4 · ≈41,8**. Un
rango de 21 a 44 pp **no es independencia de la definición**, contra lo que afirma el manuscrito.

## FATAL 3 — La declaración de disponibilidad de código es falsa tal como está escrita

Según el propio `PROCEDENCIA.md`, están sin script **las cinco figuras y las dos tablas del manuscrito
enviado**. V25 y V27b leen fuera del árbol del repositorio, y **V28 lee por glob desde
`~/Downloads/`**. Once scripts escriben fuera del repositorio.

Sobre ética: **ReDLat es un tercer conjunto de datos**, de un consorcio con su propio IRB, acuerdo de
uso y política de publicación. El acta 003/20 cubre las dos cohortes sanjuaninas, no ReDLat.

## MAYOR (síntesis)

**M1.** El «gradiente» es **paridad demográfica**, la métrica de equidad más débil, y V27b la reduce al
absurdo: el corte 27,5 alcanza un gradiente de **2,7 pp señalando al 98,5 %**. La métrica tiene óptimos
degenerados en ambos extremos y es **provablemente incompatible con la calibración** cuando la
prevalencia difiere por estrato. **M2.** Los doce cortes del IFS no son comparables: cuatro provienen de
otras condiciones diana. El subconjunto defendible abarca 8 puntos y sigue siendo contundente.
**M3.** «3,27 desvíos» usa el denominador más pequeño disponible; en DE propio es 1,47. **M4.** **La
dispersión no replica en el Gran San Juan** (pendiente −0,0444, **p = 0,213**, n = 219, el 64 % de los
controles); el gradiente va de 24,4 a 51,8 pp entre áreas. **M5.** La variable geográfica indexa el
**centro de evaluación**, no la residencia, y la ruralidad **se codifica por deducción**. **M6.** La
cohorte comunitaria —81 % mujeres, convocatoria voluntaria, sin tasa de participación— no permite hablar
de población, y la exclusión fue diferencial. **M7.** La aritmética del flujo no cierra: 109 frente a
«los 90 excluidos» frente a 95. **M8.** «Sin costo demostrable» sin margen, y con ventaja de muestra
para la regla nueva. **M9.** El cambio mínimo detectable al 95 % es de **22,6 puntos de ACE-III**, y la
calculadora ya está publicada mientras el texto dice que no constituye norma. **M10.** **Ninguna medida
de nivel socioeconómico** en un trabajo sobre equidad. **M11.** La compresión se atribuye al techo y
**el IFS lo desmiente**: 0 % en el techo y razón de dispersión 2,17 frente a 2,27 del ACE-III.

## El mensaje publicable más fuerte, según este revisor

> No es «el escalón educativo es inequitativo». Es **el problema de transporte de los puntos de corte**,
> con el escalón argentino como caso ilustrativo de un artefacto de composición aguas abajo.

En una cohorte comunitaria provincial argentina, **todos** los cortes de cribado en uso clasifican como
anormal a una fracción grande de personas sin deterioro **en todos los niveles de escolaridad**: el 86
del ACE-III señala al 43,9 % de los controles con 12 o más años, cuya media (85,3) queda por debajo del
propio corte; el 25 del IFS señala al 77,3 % de esas mismas personas y **al 100 % de las que tienen
menos de 7 años**. A escolaridad idéntica, el grupo provincial rinde 5,2 puntos menos que los 26
controles porteños de los que salió el corte.

**La implicancia no es un escalón mejor ubicado: es que los cortes derivados en muestras de conveniencia
de centros metropolitanos requieren datos normativos locales.**

Lo que **no** dejaría afirmar en ninguna versión: «una corrección continua elimina el trato desigual sin
costo diagnóstico demostrable».

<div style="page-break-before: always"></div>

# Revisor 4 — *Nature* (Human Behaviour / Medicine / Reviews Neurology)

*Perfil: novedad conceptual, rigor metodológico y solidez de las afirmaciones mecanicistas.*

> **Recomendación: rechazo para cualquier revista del grupo *Nature*.** El hallazgo central que se
> presenta como mecanismo es una identidad algebraica, la cantidad que lo cuantifica no está
> identificada, y el propio repositorio contiene el análisis que lo refuta —sin que aparezca en el
> manuscrito.

## FATAL

**F1. La «predicción falsable» no puede fallar.** Demostrado por simulación propia bajo cuatro
escenarios opuestos (tabla en la sección de verificación de este documento). Las razones son
indistinguibles entre el escenario que el manuscrito afirma y su negación exacta. **La prueba no tiene
poder discriminante alguno.**

**F2. La cifra central (19,1 → 12,0 puntos por unidad de θ) no está identificada.** Un modelo de TRI
identifica θ sólo hasta transformación monótona. Y no es un tecnicismo: en la métrica de puntaje
verdadero de Lord la conclusión se invierte —1,00× instrumento y 1,94× habilidad—. *«Mismo modelo,
mismos datos: "la escala explica casi todo" o "la escala no explica nada", según qué reparametrización
se privilegie. El manuscrito no discute esta elección; ni siquiera la menciona.»*

**F3. El IFS refuta la versión "cerca del techo" del mecanismo — y ese resultado está en el repositorio,
ausente del manuscrito.** V27 declara por escrito, antes de mirar, que el mecanismo predice **más**
compresión cuanto más bajo el techo. El IFS: 0 % en el techo en los tres tramos, y compresión de
**2,17×** frente a 2,27× del ACE-III. *«Lo agravante no es el resultado; es su ausencia.»*

**F4. Las cifras titulares son extrapolaciones fuera del soporte.** Entre los controles hay **cero con 0
años** de escolaridad y **una sola persona con exactamente 20**. El «rendimiento esperado 55,9 puntos
con σ = 13,18 sin escolaridad» que genera el percentil 82 **no tiene ni un solo control detrás**.

## MAYOR (síntesis)

**M1.** «Desaparece» es selección de la prueba que da el nulo buscado: el Levene sobre θ es
significativo y la forma es en U. **M2.** La curva característica está mal construida: colapso dirigido
por los datos, **remapeo con media no ponderada** en lugar de esperanza condicional, y como síntoma
visible `E[ACE|θ]` va de 12,6 a 99,0 en vez de 0 a 100. **M3.** La defensa de la contracción del EAP es
incompleta, y hay asimetría en el uso de las cifras. **M4.** La descomposición sobreexplica en un 11 %
sin declararlo. **M5.** La distinción «no hay sesgo de ítem pero sí no linealidad de escala» **es real y
bien conocida**, pero aquí no está establecida: el manuscrito exagera el lado «no hay sesgo», el umbral
ΔR² = 0,035 es de baja potencia, hay circularidad de identificación, y la no linealidad **se postula, no
se establece**. **M6.** Un grupo control del que el 88 % falla otro cribado no es un grupo control, y
eso ofrece una explicación alternativa, más simple y no descartada, para **todo el patrón**.

## M7 — Novedad: el núcleo mecanicista es psicometría de manual

| Afirmación del manuscrito | Origen |
|---|---|
| El puntaje bruto no es lineal en el rasgo latente; las razones de varianza no son invariantes a transformación monótona | **Lord 1953**; Lord & Novick 1968 |
| σ_Y ≈ \|g′(x̄)\| σ_X | método delta; libro de texto |
| Piso y techo comprimen varianza y curvan asociaciones | psicometría clásica |
| Ausencia de DIF es compatible con no linealidad de escala | Meredith 1993; Michell 1997; Embretson 1996 |
| Un corte fijo ocupa percentiles distintos si el rasgo se desplaza | consecuencia inmediata |

*«El aporte del trabajo aquí no es conceptual: es verificar localmente algo que ya se sabía. Para
Nature Human Behaviour o Nature Medicine, esto es descalificante por sí solo.»*

**Lo que sí es genuinamente valioso y no está siendo el centro del trabajo:** la reconstrucción
documental · la prueba de placebo, *«aquí sí hay una hipótesis que podía morir y no murió»* · y el
cuadro de los doce cortes publicados del IFS, *«más informativo sobre la fragilidad de los cortes fijos
que toda la sección de mecanismo, y está sin usar»*.

## Cómo debería reformularse la afirmación, según este revisor

> El ACE-III es una suma ordinal acotada. Su relación con cualquier rasgo latente subyacente es monótona
> pero no lineal, de modo que **las razones de varianza entre grupos situados en distintos puntos de la
> escala no son interpretables como diferencias de variabilidad entre personas**. En consecuencia, un
> umbral fijo ocupa posiciones percentilares distintas según el tramo educativo, y esa consecuencia
> clínica es válida con independencia de cuál sea la métrica «verdadera». **No estamos en condiciones de
> determinar qué parte de la compresión corresponde a la escala y qué parte a las personas: esa
> partición requiere un ancla externa que estos datos no proveen.**

## Qué haría falta para publicar en *Nature*

1. Un **ancla externa de habilidad** independiente de los ítems del ACE-III.
2. Una **muestra normativa con soporte real en 0–6 años** de escolaridad y control validado contra
   referencia independiente.
3. Un **desenlace prospectivo**.
4. **Preinscripción y validación externa**.

**¿Alcanzable con estos datos? No.** Lo que sí es alcanzable y merece publicarse: el trabajo documental
sobre la procedencia del escalón, la prueba de placebo, el gradiente presentado como límite superior, y
el cuadro de los doce cortes del IFS. *«Recortar el mecanismo y quedarse con eso mejoraría el trabajo,
no lo empobrecería.»*

<div style="page-break-before: always"></div>

# Anexo — Estado de cada objeción

## Ya corregido

| Objeción | Corrección |
|---|---|
| Signo invertido de la desatenuación | Eliminada; sustituida por **GRM multigrupo** con media y varianza latentes libres |
| Bootstrap con 40,9 % de recorte | Eliminado |
| «Predicción falsable» tautológica | Retirada la presentación como predicción; se declara identidad del método delta |
| Métrica no identificada | Declarado explícitamente, con la comparación en las dos métricas |
| «Cerca del techo» | Retirado: ningún control está en el techo |
| Levene sobre θ omitido | Informado en Resultados |
| Extrapolación a 0 y 20 años | Razones sólo dentro del rango con soporte (4 a 16 años) |
| Gradiente por máx − mín | Sustituido por el **contraste preespecificado**, IC 16,7 a 49,7 |
| Bootstrap sin propagar la incertidumbre del modelo | Cada réplica **reajusta el modelo normativo** |
| Punto de operación único | **Barrido del 10 % al 90 %**, con el hallazgo de que un corte único reparte mejor (19,5 frente a 33,4 pp) |
| Contaminación supuesta y no medida | **Medida**: la dispersión se atenúa de −0,082 a −0,035; el gradiente no |
| Equivalencia a ±3 sin corrección por familia | Declarada frente a ±5; ±3 pasa a exploratorio |
| DTF continuo no informado | Informado: −0,07 por año, p = 4,8×10⁻⁶, 1,2 puntos |
| Clase de evidencia de la dispersión | Asignada |
| «Sin costo demostrable» | Sustituido por la lectura correcta del intervalo |
| Título normativo y afirmación sobre la habilidad | Título descriptivo que declara el diseño |
| Figuras huérfanas sin script | `F11_figuras_instrumento_y_equidad.py` |
| Coeficientes de la calculadora sin script | `CALC_coeficientes.py`, con verificación contra lo publicado |
| Mapa de procedencia inexistente | `PROCEDENCIA.md`, auto-regenerable |
| PDF suplementario sin figuras | Corregido: las etiquetas se imprimían como texto |

## Pendiente, y por qué

| Objeción | Estado |
|---|---|
| **Armonización del IFS** (series motoras, escalas 3 frente a 6) | **Decidido hacerlo**; hasta entonces V27 no compara cohortes |
| Bloques V16 y V17-B obsoletos en el suplementario | Requiere depuración del suplemento |
| Tabla del perfil de controles (V19) ausente del suplemento | Debe incorporarse, con lectura acorde a sus valores p |
| Frase interpretativa codificada en V19 | Debe eliminarse del script |
| Cifras 60,7 % y 48,9 % de procedencia dudosa | Requiere comprobación dirigida |
| Aritmética del flujo de participantes (109 / 95 / 90) | Requiere reconciliación |
| Scripts que escriben fuera del árbol; V28 leyendo de `~/Downloads` | Reproducibilidad no resuelta |
| Gobernanza de ReDLat | Requiere autorización documentada del consorcio si V28 se publica |
| Medidas de nivel socioeconómico ausentes | No hay datos; limitación declarada |
| Ancla externa de habilidad | **No alcanzable con estos datos** |
| Referencia independiente en baja escolaridad | **Requiere reclutamiento nuevo**: ReDLat tiene 1 control con CDR = 0 y menos de 7 años |
| División en dos manuscritos | **Decidida**; pendiente de ejecución |

---

## Nota final

Cuatro revisores independientes, con estándares de cuatro revistas distintas, coincidieron en que el
núcleo del trabajo —la procedencia documental del umbral, la forma funcional y su falsación— es sólido y
publicable, y en que la capa de equidad no está identificada con estos datos. Tres de los cuatro
consignaron explícitamente que el estándar de autocrítica del proyecto es superior al habitual. Uno
señaló dónde se detuvo: *«en los tres puntos donde la autocrítica habría desmontado el titular, el
proceso se detuvo justo antes»*.

Ese es el valor de esta auditoría, y la razón de conservarla completa.
