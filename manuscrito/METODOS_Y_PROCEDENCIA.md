# Métodos y procedencia de datos — Educación y ACE-III en dos cohortes de San Juan

> Documento fuente para el manuscrito. Contiene la especificación completa del diseño, la
> procedencia de cada variable y la auditoría de calidad de datos. Estado: 2026-07-30.

---

## 1. Diseño

Estudio transversal analítico sobre **dos cohortes independientes** de la provincia de San Juan,
Argentina, evaluadas con el mismo instrumento (Addenbrooke's Cognitive Examination III, ACE-III):

| | Cohorte comunitaria | Cohorte clínica |
|---|---|---|
| Fuente | Programa Neuromentia, olas 2023–2024 | Instituto de Neurociencias de San Juan (ex-INECO/Castaño) |
| Reclutamiento | poblacional, comunitario | derivación a un servicio de neuropsicología |
| Selección | independiente de la cognición | **sobre la cognición** (motivo de consulta) |
| Unidad | 1 participante | 1 paciente = 1 evaluación (la basal) |
| n analítico | 762 | 2112 |

**Decisión metodológica central.** Las cohortes **no se combinan para producir una estimación
agregada**. Se colocan en un marco analítico único con un factor `cohorte`, y todas las
estimaciones son específicas de cohorte, derivadas de un modelo con interacciones
`cohorte × (educación + educación²)` — un metaanálisis de datos individuales en una etapa. Esto es
preferible a ajustar modelos separados porque produce contrastes con intervalo de confianza en
lugar de comparaciones informales de valores p, da tests de heterogeneidad con los grados de
libertad correctos y estima las covariables de molestia con toda la información. Una pendiente
marginal sobre la muestra agregada **no se reporta**: la cohorte clínica selecciona sobre el
desenlace y esa estimación no tendría población diana definida (sesgo de colisionador entre
educación y cognición).

## 2. Participantes

**Inclusión (ambas cohortes).** Adultos ≥40 años con ACE-III válido y años de educación válidos.

**Cohorte clínica — exclusiones.** Cohortes no comparables (`wisc_v` pediátrica, `toyota`
ocupacional, `mips` de personalidad); edad implausible (fuera de 18–105); demografía faltante;
evaluaciones posteriores del mismo paciente (se conserva la basal, por independencia de las
observaciones); ACE-III no reconciliable (§4).

**Independencia entre cohortes.** Se identificaron por documento de identidad los individuos
presentes en ambas muestras (n=17; 2,0 % de la comunitaria) y se excluyeron de la **comunitaria**
—la de menor tamaño— para preservar la independencia de las cohortes. Sensibilidad: el análisis se
repite sin la exclusión y excluyéndolos del lado clínico.

## 3. Desenlace — ACE-III total

Puntaje total sobre 100. La interpretación clínica en Argentina emplea **dos puntos de corte según
la educación: 86 para ≥12 años de escolaridad y 68 para <12** (Bruno et al. 2020; D. Bruno,
comunicación personal, 7/10/2024). Sousa y Vivas (2017) proponen 70 para bajo nivel socioeducativo,
prácticamente el mismo valor. Es decir, la práctica vigente **ya reconoce que el umbral depende de
la educación**, y lo resuelve con una función escalón de un solo escalón situado en 12 años.

Esto define el contrafáctico correcto del trabajo. Una versión anterior de este análisis comparaba
contra un corte único de 86 —que nadie aplica— y por lo tanto medía la discrepancia entre dos
procedimientos hipotéticos. El análisis vigente compara tres políticas: corte único de 86, el
escalón 86/68, y un corte continuo derivado de la forma estimada.

El corte es educativo, no etario, lo que justifica ajustar por edad y sexo pero **no** por
educación, que es la exposición.

**Procedencia y validación (cohorte clínica).** El ACE-III se extrae a nivel de ítem por celdas
fijas de la hoja de puntuación (mapeo verificado idéntico en las siete generaciones de plantilla
2020–2026). Regla de inclusión, declarada a priori:

1. Debe existir al menos un total en [1,100], de la hoja o de la tabla de resultados institucional
   (fuentes independientes dentro del mismo archivo).
2. Si los 23 ítems están completos y en rango, y los subtotales de dominio presentes reconcilian,
   su **suma debe coincidir (±0,5) con al menos un total** → se usa la suma de ítems, validada por
   doble fuente.
3. Si los ítems están completos pero **no** coinciden con ningún total → **se excluye**: es un dato
   no reconciliable y no corresponde elegir arbitrariamente una fuente.
4. Si los ítems no están completos pero hay total válido → se usa el total, marcado `solo_total`.

Concordancia entre las dos fuentes de total, donde ambas existen: **97,6 %** de coincidencia exacta
(r=0,996).

**⚠ Sesgo de disponibilidad corregido.** El extractor original exigía que la celda del gran total
de la hoja estuviese cargada. Esa celda está vacía en el **82 %** de los archivos de pacientes de
baja escolaridad, de modo que la tasa de validación caía a **2,6 % en <7 años de educación frente
a 92,8 % en 11–12** — un diferencial de ~35×. Se verificó que **no** se debe a administración
parcial: el ACE-III se administra por igual (93 % en ambos grupos) y los 23 ítems están cargados
(mediana 23/23). La regla anterior dejaba **3 pacientes** con <7 años de escolaridad en la muestra
clínica; la regla de validación cruzada los recupera.

**Cohorte comunitaria.** Suma de los 23 ítems. Un caso con `ACE_LLectura`=2 (máximo del ítem = 1)
se trunca al máximo, como corrección de rango. La columna de total del propio instrumento coincide
con la suma de ítems en el 72 % de los casos, por lo que se usa la suma; el análisis se repite con
la columna de total como sensibilidad.

## 3b. Armonización del ítem de reconocimiento

El ítem de reconocimiento de nombre y dirección (`ACE_MReconocNyD`, máximo 5) es **condicional**: en
la regla estándar del ACE-III se administra sólo sobre los elementos no evocados libremente, y los
evocados cuentan como reconocidos. Las dos fuentes aplicaron reglas distintas:

| | Regla aplicada | r evocación–reconocimiento | r con el resto del test |
|---|---|---|---|
| Clínica | estándar (los evocados cuentan) | **+0,652** | **+0,607** |
| Comunitaria | sólo sobre los no evocados | **−0,180** | **−0,138** |

La inversión de signo es diagnóstica: en un ítem condicional bien puntuado la correlación con la
evocación debe ser positiva. La regla comunitaria queda identificada en los propios datos —el
máximo observado equivale exactamente a 7 − evocación en cada nivel, salvo la evocación perfecta,
que recibe 5 por convención— y por lo tanto es reconstruible:

> reconocimiento estándar = mín(5, reconocimiento observado + elementos ya evocados del bloque)
> y 5 si la evocación fue 7/7

Tras armonizar, la correlación con el resto del test pasa de −0,138 a **+0,427** y con la evocación
a **+0,610**, valores del mismo orden que la clínica. El total comunitario sube 1,87 puntos en
promedio (r=0,996 con el original) y la curvatura pasa de −0,079 a **−0,084**.

**Limitaciones de la armonización, declaradas.** (a) La base guarda totales de bloque y no el
desglose de los 5 sub-ítems de reconocimiento, de modo que los elementos ya evocados se aproximan
por round(evocación × 5/7); recuperar el desglose de los protocolos originales eliminaría esta
aproximación. (b) La corrección **no es neutral respecto de la exposición**: añade +1,23 puntos en
<7 años frente a +2,33 en ≥12, porque quien evoca más recibe más corrección. Por eso todo el
análisis se reporta con y sin armonizar (Tabla 2E). (c) Aun armonizado el ítem conserva una brecha
residual (+0,427 frente a +0,607), por lo que en cualquier análisis de teoría de respuesta al ítem
debe quedar fuera del conjunto de anclaje y con parámetros libres por cohorte.

**Se descartó excluirlo** (escala de 22 ítems): aunque el costo sería mínimo (r=0,995 y 0,998 con el
total de 23), la armonización conserva información y es reconstruible sin supuestos sobre el
comportamiento del ítem. Se descartó también colapsar evocación y reconocimiento en un único ítem
de 0–12: no resuelve el problema (la correlación del compuesto con el resto del test sigue siendo
0,499 frente a 0,682).

## 4. Exposición — años de educación

**⚠ Corrección crítica.** El campo "años de educación" del Excel institucional **asigna 11 por
defecto** a los pacientes de baja escolaridad. Verificado contra el nivel educativo autorreportado
del cuestionario de ingreso (n=951 pacientes enlazados):

| Nivel autorreportado | años esperados | mediana en el Excel | % registrado como 11 |
|---|---|---|---|
| Primario incompleto | ≤6 | 11 | 58 % |
| Primario completo | 7 | 11 | 51 % |
| Secundario completo | 12 | 12 | 11 % |
| Universitario completo | ~17 | 17 | ~0 % |

El sesgo depende del evaluador (uno de ellos, el de mayor volumen, registra correctamente sólo el
10 % de sus pacientes de primaria; otro, el 72 %) y no se corrige restringiendo por año ni por
evaluador. Con esa variable, la cohorte clínica aparentaba un 2,8 % de baja escolaridad cuando el
autorreporte indica ~20,6 %, casi idéntico al 21 % de la cohorte comunitaria.

**Variable utilizada:** los años de educación consignados en el **informe PDF** (campo "Años de
Educación"), enlazados por documento y fecha de evaluación, con re-parseo directo del informe
cuando faltaban. Validación contra el nivel autorreportado: mediana 7 para primaria, 12 para
secundario completo, 15 para terciario, 17 para universitario.

En la cohorte comunitaria la educación son años reales (moda en 7 = primaria completa y 12 =
secundaria completa), sin el artefacto del 11.

## 5. Diseño retirado — estratificación clínica por estado cognitivo

Una versión previa estratificaba la cohorte clínica en cuatro grupos (sin deterioro, deterioro leve
amnésico, leve no amnésico, deterioro mayor) a partir de la **oración diagnóstica** de la sección de
conclusiones del informe. Se retiró del análisis principal por tres razones: usar la cohorte clínica
completa recupera 533 pacientes (2112 en lugar de 1579); estratificar por estado cognitivo condiciona
sobre un mediador del efecto de la educación; y la clasificación depende de reglas de extracción de
texto, no de revisión de historia clínica.

Se conserva la implementación (`ACE/20_dx_desde_conclusiones.py`, `ACE/21_analisis_una_etapa.py`,
`analisis/dx_conclusiones.csv`) por si se retoma como trabajo aparte. Su resultado fue de
**invarianza**: curvatura equivalente en los cinco grupos (b₂ entre −0,042 y −0,083), heterogeneidad
de la forma p=0,29 y de la curvatura p=0,52, con contrastes nulos incluidos comunitaria versus
deterioro mayor (p=0,97) y amnésico versus no amnésico (p=0,89) — pese a que los grupos abarcaban de
92,6 a 54,3 puntos de ACE-III medio y de 76,1 % a 0 % de puntajes en zona de techo.

**Nota sobre por qué no se usó la clasificación precodificada de la base.** El campo `subtipo` de la
tabla de perfil cognitivo, pese a declararse de fuente narrativa, coincide con la clasificación
derivada de los puntajes z en 8896/9618 registros. Los z están normados por bandas de edad ×
**educación**, de modo que estratificar con ellos introduciría circularidad en un estudio cuya
exposición es la educación. La clasificación textual, en cambio, quedó validada externamente: el
ACE-III se ordena monótonamente por severidad (leve 81,4 · leve-moderado 71,3 · moderado 60,5 ·
moderado-severo 46,1 · severo 36,4) y la memoria del ACE-III relativa al resto del test es −0,260 en
el grupo amnésico frente a −0,134 en el no amnésico (t=−12,3; p=8×10⁻³⁰).

## 6. Análisis estadístico

Modelo: `ACE-III ~ (educación + educación²) × cohorte + edad + sexo`, con errores estándar robustos
a heterocedasticidad (HC3).

**Efecto reportado:** la **pendiente marginal** dY/dEdu = b₁ + 2·b₂·educación, evaluada a 3, 7, 12 y
17 años de escolaridad, con intervalo de confianza del 95 % por **método delta** sobre la matriz de
covarianzas HC3. Reemplaza a las pendientes por tramos, que dependen arbitrariamente de dónde se
sitúe el corte (en un análisis previo, la pendiente del tramo superior variaba entre +0,81 y +0,47
según se definiera como ≥12 o >12 años).

**Curvatura:** el coeficiente cuadrático b₂; negativo indica concavidad (pendiente que decrece al
aumentar la escolaridad).

**Replicación de la forma:** razón de verosimilitud entre el modelo de forma común, el de pendiente
lineal específica por cohorte y el de forma completa específica por cohorte, más el contraste de
curvatura entre cohortes con IC95 %. La descomposición importa: la pendiente lineal puede diferir
por selección diferencial sin que difiera la curvatura.

**Consecuencia práctica:** diferencia entre el ACE-III esperado bajo el modelo cuadrático y bajo el
lineal a lo largo del rango de escolaridad, y proporción de evaluados que cambia de lado del punto de
corte de Bruno (86) al ajustar la educación de una forma o de la otra (ambos ajustes referidos a 12
años de escolaridad).

**Verificación de la forma funcional:** lineal vs cuadrática vs spline cúbico natural (4 gl) por
criterio de Akaike y razón de verosimilitud. La especificación cuadrática sólo se sostiene si el
spline no la mejora.

## 7. Auditoría de calidad — defectos detectados y corregidos

| # | Defecto | Efecto si no se corrige | Estado |
|---|---|---|---|
| 1 | Años de educación con valor por defecto 11 en baja escolaridad | La exposición se colapsa; desaparece la concavidad clínica y aparece una falsa interacción con el estado cognitivo | Corregido (informe PDF) |
| 2 | Estratificador derivado de z normados por educación | Circularidad | Corregido (texto de conclusiones) |
| 3 | Extractor del ACE-III con pérdida diferencial por escolaridad (35×) | La muestra clínica pierde casi toda la baja escolaridad | Corregido (validación cruzada) |
| 4 | Test de tendencia sin efecto principal del estrato | Los términos de interacción absorben las diferencias de nivel entre grupos → p espurio (7×10⁻³² frente a 0,38 bien especificado) | Corregido |
| 5 | Parseo de fechas ISO con `dayfirst` | Invierte día/mes o anula; el enlace entre bases cae de ~85 % a 3 % | Corregido |
| 6 | Compuesto de batería construido con z normados por educación | Sugiere falsamente un sesgo educativo del ACE-III | Corregido (puntajes brutos estandarizados en la muestra) |

## 8. Ética

Cohorte comunitaria: IRB 003/20, Comité de Ética de la Universidad Católica de Cuyo (12/05/2020),
con consentimiento informado. Cohorte clínica: base institucional, análisis secundario con
procesamiento **100 % local** y datos identificatorios preservados; los archivos analíticos no
exportan identificadores.

Se empleó inteligencia artificial generativa como apoyo de análisis y redacción, verificada por los
autores; no generó datos ni resultados sintéticos.

## 9. Reproducibilidad

Todo el procesamiento en `neuromentia/ACE/`, entorno `ACE/.venv`, salidas en `ACE/out/`.

| Script | Función |
|---|---|
| `18_auditoria_n.py` | Auditoría del flujo de exclusiones y del n recuperable |
| `19_build_definitivo.py` | Pasada única sobre el corpus: ítems, totales y educación; aplica la regla de inclusión |
| `25_analisis_dos_cohortes.py` | **Análisis principal**: forma por cohorte, replicación, especificación, supuestos, sensibilidades y consecuencia del ajuste lineal |
| `26_figuras_dos_cohortes.py` | Figuras 1 y 2 |
| `20`–`23` | Diseño retirado (estratificación clínica); se conservan por trazabilidad |

---

## 10. Posicionamiento en la literatura (borrador para la Discusión)

**El corte de referencia argentino se derivó en el extremo educativo opuesto al problema.**
El punto de corte de 86 proviene de la validación argentino-chilena del ACE-III (Bruno et al.,
*Neurología (English Edition)* 2020;35:82–88), con sensibilidad 98,5 % y especificidad 82,0 %. Su
muestra tenía **13,2 a 14,4 años de escolaridad media** — es decir, el umbral se calibró en el
tramo donde nuestra pendiente marginal es más plana (+0,60 puntos/año a 17 años de educación) y
donde el ajuste lineal introduce menos error. El trabajo cuantifica cuánto se paga por trasladarlo
al otro extremo: a 2 años de escolaridad el ajuste lineal sobreestima el rendimiento esperado en
4,3 puntos (comunitaria) y 6,4 (clínica).

**Nuestro hallazgo aporta la forma continua que subyace a la solución de dos umbrales.**
Sousa y Vivas (*Neurología Argentina* 2017;9(4):219–224) reconocieron el problema y propusieron un
corte alternativo de 70 para bajo nivel socioeducativo, con sensibilidad y especificidad de 84 %.
Es una solución **categórica**: dos umbrales, un salto discreto. Nuestros datos muestran que la
relación subyacente es una función suave y cóncava, con la misma curvatura en dos cohortes de
selección opuesta (b₂ −0,079 y −0,078; p=0,71). La implicación es que la corrección puede
formularse como un ajuste continuo en lugar de una dicotomía, lo que evita el problema de dónde
poner la frontera entre "bajo" y "medio" nivel socioeducativo.
*Nota: Sousa y Vivas se cita como antecedente de la literatura, no como criterio de interpretación
—la regla del proyecto es el corte de Bruno— y además refiere al ACE original, no al ACE-III.*

**El problema no es exclusivo del ACE-III ni de Argentina.** Franco-Marina et al.
(*International Psychogeriatrics* 2010;22(1):72–81) mostraron en población mexicana envejecida que
**aun después de ajustar el MMSE por nivel educativo persisten efectos de techo y piso**, y que las
personas de baja escolaridad se concentran del lado del techo. Nuestro trabajo aporta la
contraparte metodológica: la insuficiencia no está sólo en la magnitud del ajuste sino en su
**forma**.

**Hay evidencia convergente a nivel de ítem.** Calderón et al. (*PLoS ONE* 2021;16(5):e0251137),
con teoría de respuesta al ítem sobre 1164 participantes, encontraron que ítems de orientación del
ACE-III presentan mal ajuste atribuible a diferencias educativas y ocupacionales más que a
deterioro cognitivo. Nuestro análisis, en cambio, opera a nivel de puntaje total y no puede
localizar el fenómeno en ítems particulares: son enfoques complementarios, y la conjunción sugiere
que la influencia educativa del ACE-III tiene componentes tanto de ítem como de escala.

**Antecedente regional de no linealidad.** Zuno Reyes et al. (*Arch Clin Neuropsychol* 2023)
documentaron efectos lineales y no lineales de los años de escolaridad sobre el CERAD-MX en
población mexicana. Nuestro trabajo extiende ese antecedente al ACE-III, añade la replicación entre
dos regímenes de reclutamiento y traduce la forma funcional a una consecuencia de clasificación.

**Qué NO puede concluir este trabajo.** Que la corrección no lineal mejore la sensibilidad o la
especificidad diagnóstica: eso requiere un diseño con diagnóstico clínico como estándar de
referencia. Lo que se establece es que dos formas de ajuste igualmente defendibles a priori
discrepan en la clasificación de uno de cada ocho adultos de baja escolaridad, y que la evidencia
sobre la forma funcional favorece la cuadrática.
