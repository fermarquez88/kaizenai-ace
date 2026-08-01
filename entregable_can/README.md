# 12b — Falsación del escalón educativo del ACE-III (CAN 2026)

Sustituye a `12_educacion_no_lineal/`, archivado.

## Hallazgo

La regla argentina de interpretación del ACE-III usa **dos puntos de corte según la educación: 86
para ≥12 años y 68 para <12** (Bruno 2020). Eso supone una **discontinuidad del rendimiento
esperado a los 12 años de escolaridad**. Los datos la excluyen:

| Cohorte | Escalón estimado en 12 años [IC95%] | p | Salto que impone la regla |
|---|---|---|---|
| Comunitaria (n=762) | **+0,55 [−2,09; +3,20]** | 0,68 | **18** |
| Clínica (n=2112) | **+0,13 [−2,56; +2,83]** | 0,92 | **18** |

El límite superior de ambos intervalos excluye la regla **por un factor de seis**, en dos cohortes
con selección opuesta. Regresión discontinua local nula en las seis especificaciones.

**Consecuencia:** la positividad de la regla desciende de forma monótona con la escolaridad y salta
donde cambia el corte — de **6,2 % a los 11 años a 52,2 % a los 12** en la cohorte comunitaria
(8,4 veces) y de 42,9 % a 81,2 % en la clínica. El salto está en la regla, no en el rendimiento.

## Contenido

| Archivo | Qué es |
|---|---|
| `texto_plataforma.md` | Resumen español (298/300 palabras; relevancia 49/50), ABSTRACT inglés, nota de robustez |
| `Tabla1.md` | Cohortes, armonización del ítem de reconocimiento, procedencia y validación de cada variable |
| `Tabla2.md` | A falsación · B positividad año por año · C forma de la asociación · D límites del corte continuo · E comparación a tasa igualada · F varianza · G quince sensibilidades |
| `Figura1_falsacion_del_escalon.jpg` | (a) positividad año por año con el salto de 8,4× · (b) rendimiento continuo · (c) escalón estimado contra el impuesto |
| `Figura2_consecuencia_y_forma.jpg` | (a) reparto a tasa igualada · (b) curvatura en ambas cohortes |
| `referencias.md` | Ocho referencias; las cuatro del núcleo verificadas contra la fuente |

Documento fuente del manuscrito:
[`../../../manuscritos/educacion_2cohortes/METODOS_Y_PROCEDENCIA.md`](../../../manuscritos/educacion_2cohortes/METODOS_Y_PROCEDENCIA.md)

## Cadena reproducible

`ACE/`, entorno `ACE/.venv`, salidas en `ACE/out/`.

| Script | Función |
|---|---|
| `19_build_definitivo.py` | Dataset clínico: ítems, totales y educación del informe → `analisis/clinico_definitivo.csv` |
| `30_analisis_armonizado.py` | Armoniza el reconocimiento y corre forma, replicación, especificación, supuestos y sensibilidades → `analisis/comunitaria_armonizada.csv` |
| `31_falsacion_escalon.py` | **Análisis principal**: falsación del escalón, RD local, positividad anual, autocrítica del corte continuo, tasa igualada, escala |
| `32_figuras_falsacion.py` | Figuras 1 y 2 |

## Cinco decisiones que hay que poder defender

1. **El entregable es una falsación, no una propuesta de corte.** El corte continuo se presenta como ilustración, con sus cuatro límites reportados en la Tabla 2D — incluido que su anclaje lo deja en la media condicional, de modo que aplanar la positividad es mecánico.
2. **Las cohortes no se combinan** para una estimación agregada: la clínica selecciona sobre la cognición.
3. **La educación clínica viene del informe**, no del campo administrativo, que asigna 11 años por defecto en baja escolaridad.
4. **El ítem de reconocimiento se armonizó** con una regla reconstruida de los propios datos, y todo se reporta con y sin.
5. **No se estima exactitud diagnóstica.** No hay estándar de referencia; ninguna cifra de positividad es sensibilidad o especificidad.

## Pendiente antes de enviar

- **Aprobación o exención documentada del comité de ética para la cohorte clínica** — compuerta binaria en cualquier revista internacional.
- Acta del Comité de Ética para el premio CAN y verificación de ineditismo.
- Confirmar autoría y filiaciones.
