# Bloque V1 — Integridad de datos

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
