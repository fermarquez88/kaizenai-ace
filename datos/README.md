# Datos

**Los datos individuales no se distribuyen en este repositorio.**

Los archivos que este directorio contiene en la copia de trabajo incluyen documento de identidad,
fechas de evaluación, rutas de archivo con nombres de pacientes y texto libre de conclusiones
clínicas. Nada de eso puede publicarse. El directorio está excluido por `.gitignore`, con la única
excepción de este archivo.

## Qué se necesita para reproducir el análisis

Los scripts de [`../codigo/`](../codigo/) esperan estos archivos:

| Archivo | Contenido | Filas |
|---|---|---|
| `comunitaria_armonizada.csv` | Cohorte comunitaria, ACE-III armonizado, escolaridad, edad, sexo | 758 |
| `clinico_definitivo.csv` | Cohorte clínica, ítems del ACE-III, batería completa | 2112 |
| `clinico_dx3.csv` | Cohorte clínica con el perfil cognitivo codificado en tres niveles | 2112 |
| `controles_comunitarios.csv` | Subconjunto sin deterioro por criterio de reconocimiento | 663 |
| `dx_conclusiones.csv` | Oración clasificatoria extraída del texto libre y su codificación | 2750 |
| `solape_dni.csv` | Identificadores compartidos entre ambas bases, para descartar duplicados | — |

Además, `Mix neuromentias.xlsx` (hoja `Base mixta 23+24 (valores)`), que vive fuera de este árbol.

## Qué sí está publicado

Todo lo que permite auditar el análisis sin acceder a datos individuales:

- **[`../codigo/`](../codigo/)** — los scripts completos, incluidos los de verificación
- **[`../resultados/`](../resultados/)** — las salidas numéricas en JSON, agregadas
- **[`../verificacion/`](../verificacion/)** — las bitácoras de cada bloque de verificación
- **[`../figuras/`](../figuras/)** y **[`../tablas/`](../tablas/)** — las figuras y tablas del trabajo
- **[`../docs/`](../docs/)** — la calculadora, que lleva los coeficientes del modelo estimado

Los coeficientes publicados en [`../resultados/CALC_coeficientes.json`](../resultados/CALC_coeficientes.json)
permiten reproducir la función normativa completa sin los datos de origen.

## Acceso

Las solicitudes de acceso a datos individuales, seudonimizados y bajo acuerdo de uso, se dirigen al
autor de correspondencia y requieren aval del comité de ética que aprobó el estudio.
