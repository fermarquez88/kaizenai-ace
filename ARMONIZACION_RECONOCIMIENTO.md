# Armonización del ítem de reconocimiento del ACE-III (comunidad ↔ clínica)

> Estado 2026-07-30. Procedimiento declarado, reproducible y auditable.
> Dataset resultante: `analisis/comunitaria_armonizada.csv` (n=762).
> Implementación: función `armoniza()` en `ACE/30_analisis_armonizado.py`.

---

## 1. El problema

El ítem `ACE_MReconocNyD` (reconocimiento de nombre y dirección, máximo 5) es **condicional**: la
regla estándar del ACE-III lo administra sólo sobre los elementos que la persona **no** evocó
libremente, y los evocados cuentan como reconocidos. Las dos fuentes aplicaron reglas distintas.

| | Regla aplicada | r evocación–reconocimiento | r con el resto del test | media |
|---|---|---|---|---|
| **Clínica** | estándar (los evocados cuentan) | **+0,652** | **+0,607** | 3,62/5 |
| **Comunitaria** | sólo sobre los NO evocados | **−0,180** | **−0,138** | 2,22/5 |

**La inversión de signo es el diagnóstico.** En un ítem condicional bien puntuado la correlación con
la evocación tiene que ser positiva. Que sea negativa significa que a mayor evocación quedan menos
elementos por reconocer y por lo tanto el puntaje baja: se está puntuando el denominador equivocado.

## 2. Identificación de la regla comunitaria en los propios datos

La tabla cruzada reconocimiento × evocación muestra que el **máximo observado equivale exactamente a
7 − evocación** en cada nivel:

| Evocación | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Máximo de reconocimiento observado | 5 | 5 | 4 | 4 | 3 | 2 | 1 | 5* |

\* La evocación perfecta recibe 5 por convención (38 casos, el 100 % con reconocimiento = 5).

Se cumple en el **95,3 %** de los casos. En la clínica, en cambio, el 99,3 % cumple
reconocimiento ≥ evocación×5/7, que es la firma de la regla estándar.

## 3. La corrección

```python
def armoniza(recuerdo, reconoc):
    """Lleva el reconocimiento de la regla comunitaria a la regla estándar del ACE-III."""
    evocados_bloque = np.minimum(5, np.round(recuerdo * 5 / 7))
    std = np.minimum(5, reconoc + evocados_bloque)
    return np.where(recuerdo == 7, 5, std)
```

Se aplica **sólo a la cohorte comunitaria**. La clínica ya usa la regla estándar.

## 4. Verificación

| | r con el resto del test | r con la evocación | media |
|---|---|---|---|
| Comunitaria, sin armonizar | −0,138 | −0,180 | 2,22 |
| **Comunitaria, armonizada** | **+0,427** | **+0,610** | **4,10** |
| Clínica (referencia) | +0,607 | +0,652 | 3,62 |

La inversión de signo desaparece y la relación con la evocación queda equivalente a la clínica.

**Efecto en el total del ACE-III comunitario:** 75,60 → **77,47** (+1,87; r=0,9964 con el original).

**Efecto en el hallazgo principal:** la curvatura b₂ pasa de −0,0790 a **−0,0835** (p=1×10⁻¹⁰), y la
replicación entre cohortes **mejora**: la diferencia de curvatura pasa de p=0,71 a **p=0,91**.

## 5. Limitaciones declaradas

1. **La aproximación 7→5.** La base guarda totales de bloque, no el desglose de los 5 sub-ítems de
   reconocimiento, de modo que los elementos ya evocados se aproximan por `round(evocación × 5/7)`.
   Recuperar el desglose de los protocolos originales de la cohorte comunitaria eliminaría esta
   aproximación por completo. **Es la única vía para hacerla exacta.**
2. **No es neutral respecto de la exposición.** Añade +1,23 puntos en <7 años frente a +2,33 en ≥12,
   porque quien evoca más recibe más corrección. Por eso todo el análisis se reporta **con y sin**
   armonizar.
3. **Brecha residual.** Aun armonizado, el ítem conserva +0,427 frente a +0,607 de la clínica: no es
   plenamente equivalente. En cualquier análisis de teoría de respuesta al ítem debe quedar **fuera
   del conjunto de anclaje y con parámetros libres por cohorte**.

## 6. Alternativas evaluadas y descartadas

| Alternativa | Por qué se descartó |
|---|---|
| **Excluir el ítem** (escala de 22, máx 95) | El costo sería mínimo (r=0,995 y 0,998 con el total de 23) y el A2 ya lo había marcado como poco informativo (a=0,52), pero descarta información recuperable. Queda como sensibilidad. |
| **Colapsar evocación + reconocimiento** en un ítem 0–12 | No resuelve: la correlación del compuesto con el resto del test sigue siendo 0,499 (comunitaria) frente a 0,682 (clínica), porque el reconocimiento arrastra su regla. |
| **Llevar la clínica a la regla comunitaria** | Empeora todo: deja ambas correlaciones negativas (−0,138 y −0,025) y descarta los 95 casos de evocación perfecta, en los que no había nada que reconocer. |

## 7. Reproducir

```
ACE/.venv/bin/python ACE/30_analisis_armonizado.py
```
Escribe `analisis/comunitaria_armonizada.csv` y `ACE/out/30_armonizado.json` con todos los
resultados (descriptivos, forma funcional, replicación, especificación, políticas de corte,
supuestos y dieciséis sensibilidades).
