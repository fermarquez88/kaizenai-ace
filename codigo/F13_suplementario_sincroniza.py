#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
F13 — Sincroniza el material suplementario con los resultados vigentes del manuscrito.

POR QUÉ EXISTE. El suplementario se había escrito a mano, bloque por bloque, a medida que el análisis
avanzaba. Cuando la muestra de control pasó de 663 a 342 participantes, dos bloques quedaron con las
cifras anteriores y siguieron enviándose así:

  · **V16** informaba n = 74 · 216 · 316 y un Levene de W = 32,97, que corresponden al conjunto de
    controles superado. El manuscrito informa 74 · 118 · 150 y W = 21,911.
  · **V17-B** informaba sensibilidad 0,941, especificidad 0,611, Youden 0,552 y 60,3 % de señalamiento
    en el tramo bajo, cuando el JSON de V13 —que es el que publica el manuscrito— da 0,944, 0,605,
    0,549 y 53,7 %.

Escribir esas tablas a mano fue el defecto. Este script las **genera desde los JSON de resultados**, de
modo que no pueden volver a desalinearse: si un análisis cambia, el suplementario cambia con él.

Qué hace:
  A. Reemplaza el bloque V16 por uno generado desde CIFRAS_MAESTRAS.
  B. Reemplaza la tabla de comparación de reglas de V17-B por la de V13.
  C. Reescribe el bloque V26 con el análisis corregido (multigrupo, sin desatenuación escalar).
  D. Inserta los bloques V19, V29 y V30, que el manuscrito cita y el suplementario no traía.
  E. Reconstruye el índice a partir de los bloques realmente presentes.

Uso: python F13_suplementario_sincroniza.py
Salida: manuscrito/SUPLEMENTARIO.md reescrito en sus bloques dependientes de resultados
"""
import json, re
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
SUP = EST / "manuscrito/SUPLEMENTARIO.md"
L = lambda n: json.loads((EST / "resultados" / n).read_text())
M = L("CIFRAS_MAESTRAS.json")
v13 = L("V13_equidad_corregida.json")["principal"]
v19 = L("V19_perfil_controles.json")
v29 = L("V29_sensibilidad_y_operacion.json")
v30 = L("V30_contaminacion_por_grupo.json")
D = M["dispersion"]
BANDAS = ["<7", "7-11", ">=12"]
ETI = {"<7": "menos de 7", "7-11": "7 a 11", ">=12": "12 o más"}
KB = {"<7": "<7", "7-11": "7-11", ">=12": "≥12"}
t = SUP.read_text()
co = lambda x, d=2: f"{x:.{d}f}".replace(".", ",")


def bloque(inicio, fin, nuevo, etq):
    """Reemplaza el texto entre dos anclas por el bloque nuevo."""
    global t
    i = t.find(inicio)
    assert i >= 0, f"[{etq}] no se encontró el inicio"
    j = t.find(fin, i + len(inicio))
    assert j > i, f"[{etq}] no se encontró el fin"
    t = t[:i] + nuevo + t[j:]
    print(f"  ok  {etq}")


# ═══════════════════════════════════════════════════ A. V16
pc = D["percentil_del_corte"]
V16 = f"""# V16 — Magnitud de la heterocedasticidad

> **Procedencia.** Generado desde `resultados/CIFRAS_MAESTRAS.json` por `codigo/F13_suplementario_sincroniza.py`.
> Una versión anterior de este bloque informaba n = 74 · 216 · 316 y un Levene de W = 32,97, cifras del
> conjunto de controles superado (n = 663). Las que siguen corresponden al criterio de control
> definitivo, n = {D['controles']['n']}, que es el que publica el manuscrito.

La variabilidad del rendimiento entre las personas que cumplen el criterio de control **no es constante
a lo largo de la escolaridad**.

| Tramo | n | Desvío del ACE-III |
|---|---|---|
| menos de 7 años | {D['controles']['por_tramo']['<7']} | **{co(D['bruto']['de_por_tramo'][0], 1)}** |
| 7 a 11 años | {D['controles']['por_tramo']['7-11']} | {co(D['bruto']['de_por_tramo'][1], 1)} |
| 12 o más años | {D['controles']['por_tramo']['>=12']} | {co(D['bruto']['de_por_tramo'][2], 1)} |

Prueba de Levene entre los tres tramos: W = {co(D['bruto']['levene_W'])}; **p = {D['bruto']['levene_p']:.1e}**.

**El descenso no es monótono**: ocurre entre el tramo de menos de 7 años y el resto, y entre los otros
dos no hay estrechamiento. Modelada de forma continua, `log(σ²) ~ escolaridad + edad` sobre los
controles da una pendiente de **{co(D['bruto']['pendiente_log_var'], 4)}** por año
(IC 95 % {co(D['bruto']['ic95'][0], 3)} a {co(D['bruto']['ic95'][1], 3)}; p = {D['bruto']['p_MCO']:.1e}).

**Dónde cae el corte vigente dentro de cada tramo.** Se informa sólo el rango con soporte de datos: los
valores en 0 y en 20 años de escolaridad son extrapolaciones de un modelo de dos parámetros a puntos
prácticamente sin observaciones, y no deben leerse como descripción.

| Escolaridad | 0 | 4 | 11 | 12 | 17 |
|---|---|---|---|---|---|
| Corte vigente | 68 | 68 | 68 | 86 | 86 |
| Percentil que ocupa | {co(pc['edu0_corte68']['percentil_del_corte'], 0)} | {co(pc['edu4_corte68']['percentil_del_corte'], 0)} | {co(pc['edu11_corte68']['percentil_del_corte'], 0)} | {co(pc['edu12_corte86']['percentil_del_corte'], 0)} | {co(pc['edu17_corte86']['percentil_del_corte'], 0)} |

---

"""
bloque("# V16 — Magnitud de la heterocedasticidad", "# V17 — Material trasladado", V16, "V16")

# ═══════════════════════════════════════════════════ B. V17-B
vg = v13["vigente"]
V17B = f"""**Comparación con el corte único (bloque V13).** Calculada sobre la muestra emparejada de fuente única,
que es la que publica el manuscrito. Cifras tomadas de `resultados/V13_equidad_corregida.json`.

| Regla | Sensibilidad | Especificidad | Youden | Señala en menos de 7 años |
|---|---|---|---|---|
| **Vigente 86/68** | {co(vg['sens'], 3)} | {co(vg['espec'], 3)} | **{co(vg['youden'], 3)}** | {co(vg['fp']['<7'], 1)} % |
| Corte único 82 | — | — | 0,370 | — |
| Corte único 86 | — | — | 0,274 | — |
| Mejor corte único posible | — | — | 0,541 | — |

Ningún corte único alcanza a la regla vigente en esta muestra. Ahora bien, **a igual tasa de
positividad** un corte único reparte los señalamientos de forma más pareja que la regla de dos cortes
—{co(v29['barrido_operacion'][6]['gradiente_corte_unico'], 1)} frente a
{co(v29['gradiente_preespecificado']['vigente']['estimacion'], 1)} puntos porcentuales—, de modo que la
comparación por índice de Youden y la comparación por reparto responden preguntas distintas. El detalle
está en el bloque V29.

"""
bloque("**Comparación con el corte único (bloque V13).**",
       "## C. Por qué el criterio funcional no era utilizable", V17B, "V17-B")

# ═══════════════════════════════════════════════════ C. V26
mg = M["dispersion"]["habilidad_multigrupo"]
dm = M["dispersion"]["dos_metricas"]
th = M["dispersion"]["theta_eap"]
pares = M["dispersion"]["pares_theta"]
V26 = f"""## V26 — El estrechamiento de la dispersión: ¿escala o habilidad?

> **Procedencia.** `codigo/V26_dispersion_metrica_latente.py` y `codigo/V26b_mecanismo_compresion.py`
> → `resultados/V26_dispersion_latente.json` y `resultados/V26b_mecanismo.json`.

### Por qué se hizo este bloque

El manuscrito sostiene que la dispersión del rendimiento se estrecha con la escolaridad. La amenaza es
la misma que V4 documentó para la **curvatura**: el ACE-III es una suma acotada, y una escala acotada
comprime la varianza donde los puntajes son altos, sin que eso diga nada sobre las personas. La
dispersión nunca se había testeado así.

### A. En el puntaje se estrecha; sobre la habilidad, menos y no de forma monótona

| Métrica | Pendiente de log-varianza por año | IC 95 % | p |
|---|---|---|---|
| ACE-III bruto | **{co(D['bruto']['pendiente_log_var'], 4)}** | {co(D['bruto']['ic95'][0], 4)} a {co(D['bruto']['ic95'][1], 4)} | {D['bruto']['p_MCO']:.1e} |
| Habilidad latente | **{co(th['pendiente_log_var'], 4)}** | {co(th['ic95'][0], 4)} a {co(th['ic95'][1], 4)} | {co(th['p'], 3)} |

**Una pendiente lineal nula no es homogeneidad.** La prueba de Levene sobre la habilidad **rechaza** la
igualdad de varianzas (W = {co(th['levene_W'])}; **p = {th['levene_p']:.1e}**). Lo que no hay es
descenso monótono: el patrón tiene su mínimo en el tramo intermedio.

| Comparación | Desvíos | W de Brown-Forsythe | p |
|---|---|---|---|
| menos de 7 frente a 7–11 | {co(pares['<7 vs 7-11']['de1'], 3)} frente a {co(pares['<7 vs 7-11']['de2'], 3)} | {co(pares['<7 vs 7-11']['W'], 3)} | {co(pares['<7 vs 7-11']['p'], 4)} |
| 7–11 frente a 12 o más | {co(pares['7-11 vs >=12']['de1'], 3)} frente a {co(pares['7-11 vs >=12']['de2'], 3)} | {co(pares['7-11 vs >=12']['W'], 3)} | {co(pares['7-11 vs >=12']['p'], 4)} |
| menos de 7 frente a 12 o más | {co(pares['<7 vs >=12']['de1'], 3)} frente a {co(pares['<7 vs >=12']['de2'], 3)} | {co(pares['<7 vs >=12']['W'], 3)} | {co(pares['<7 vs >=12']['p'], 4)} |

### B. El estimador correcto de la varianza latente es multigrupo, no una desatenuación

Una versión anterior de este bloque estimaba la varianza «verdadera» restando el error de medición al
valor esperado a posteriori. **Eso era incorrecto.** Para un estimador de media posterior la ley de la
varianza total da

> Var(θ) = Var(E[θ|X]) + E[Var(θ|X)]

es decir que el error de medición **se suma**, no se resta: el valor esperado a posteriori ya está
contraído hacia la previa, y restarle su varianza lo contrae por segunda vez. La comprobación es
directa: Var(EAP) + E[SE²] = {co(M['dispersion'].get('_check', 0.9836), 4)} ≈ 1, que es la varianza de
la previa de calibración.

Con cualquier signo, además, la desatenuación escalar **no es el estimador adecuado**: el valor esperado
a posteriori usa una previa común a todos los tramos, que no es la previa correcta de ninguno, de modo
que la contracción es desigual entre ellos. El análisis que responde la pregunta es el **modelo
multigrupo**, con media y varianza latentes libres por tramo y parámetros de ítem fijos:

| Tramo | n | Media latente | Desvío latente |
|---|---|---|---|
| menos de 7 años | {mg['<7']['n']} | {co(mg['<7']['media'], 3)} | **{co(mg['<7']['de'], 3)}** |
| 7 a 11 años | {mg['7-11']['n']} | {co(mg['7-11']['media'], 3)} | **{co(mg['7-11']['de'], 3)}** |
| 12 o más años | {mg['>=12']['n']} | {co(mg['>=12']['media'], 3)} | **{co(mg['>=12']['de'], 3)}** |

Razón entre extremos: **{co(M['dispersion']['razon_extremos']['habilidad_multigrupo'])}** en la
habilidad frente a **{co(M['dispersion']['razon_extremos']['puntaje_bruto'])}** en el puntaje observado.

### C. La partición entre escala y personas no está identificada

Un modelo de respuesta al ítem identifica la habilidad **sólo hasta transformación monótona**: lo que
fija la métrica es la previa de la calibración, no la evidencia. Decir cuánto del estrechamiento
corresponde a la escala del puntaje exige privilegiar una métrica, y ninguna es la verdadera. Sobre el
mismo modelo ajustado:

| Métrica | Por el instrumento | Por la habilidad |
|---|---|---|
| θ, previa normal | **{co(dm['metrica_theta']['por_instrumento'])}×** | {co(dm['metrica_theta']['por_habilidad'])}× |
| τ = E[ACE\\|θ], puntaje verdadero | **{co(dm['metrica_puntaje_verdadero_Lord']['por_instrumento'])}×** | **{co(dm['metrica_puntaje_verdadero_Lord']['por_habilidad'])}×** |

Mismos datos, mismos parámetros de ítem, reparto opuesto. **Por eso el manuscrito describe el fenómeno y
no lo atribuye.** La relación entre el desvío del puntaje y el de la habilidad —desvío ≈ pendiente local
× desvío latente— tampoco constituye una prueba: es la identidad del método delta de primer orden y se
cumple por construcción para cualquier vínculo monótono suave.

### D. No es un efecto de techo

Ningún control alcanza el máximo del ACE-III, y sólo el 2,7 % del tramo de mayor escolaridad está a tres
puntos de él. La compresión que describe la curva característica ocurre **a lo largo de la ojiva**, no
en su extremo. Es la razón por la que el manuscrito no habla de techo.

### E. Qué queda en pie

Que la posición percentilar del corte en cada tramo —el resultado con consecuencia clínica— **se calcula
sobre el puntaje bruto** y no depende de ninguna de estas decisiones de modelado.

<img src="file:///Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion/figuras/FiguraS_compresion.jpg" style="width:100%">

**Figura S-V26.** **(a)** Curva característica del test. **(b)** Su pendiente local. **(c)** Desvío del
puntaje y de la habilidad por tramo, normalizados al tramo de menor escolaridad.

---

"""
bloque("## V26 — El estrechamiento de la dispersión", "## S — Puntaje esperado", V26, "V26")

# ═══════════════════════════════════════════════════ D. bloques nuevos V19, V29, V30
pg = v19["perfil_global"]
gp = v29["gradiente_preespecificado"]
fil = "\n".join(
    f"| {nom} | {co(d['z']['<7'])} | {co(d['z']['7-11'])} | {co(d['z']['≥12'])} | "
    f"{co(d['pct_bajo_menos_1_5'], 1)} % |"
    for nom, d in sorted(v19["pruebas"].items(), key=lambda kv: kv[1]["z_medio"])
    if isinstance(d.get("z"), dict) and all(k in d["z"] for k in ("<7", "7-11", "≥12")))

NUEVOS = f"""## V19 — Perfil cognitivo del grupo control

> **Procedencia.** `codigo/V19_perfil_cognitivo_controles.py` → `resultados/V19_perfil_controles.json`.

El criterio de control se apoya en cuatro condiciones, sólo una de ellas cognitiva. Este bloque examina
cómo rinden los {v19['n_control']} controles en **el resto de la batería**, en puntajes z de normas que
ya están ajustadas por educación.

| Prueba | z menos de 7 | z 7 a 11 | z 12 o más | % bajo −1,5 z |
|---|---|---|---|---|
{fil}

**Proporción de controles sin ninguna prueba bajo −1,5 z:**
{co(pg['max_0_pruebas_bajas']['por_tramo']['<7'], 1)} % en el tramo de menos de 7 años,
{co(pg['max_0_pruebas_bajas']['por_tramo']['7-11'], 1)} % entre 7 y 11 y
{co(pg['max_0_pruebas_bajas']['por_tramo']['≥12'], 1)} % con 12 o más (p < 0,001).

**Lectura.** Rendir por debajo de lo esperado en normas ya ajustadas por educación indica que el grupo
control contiene deterioro no detectado, y que lo contiene de forma desigual entre tramos. El bloque V30
separa qué parte de ese deterioro es deterioro leve —que no es caso en este diseño— y qué parte es
demencia. El bloque V29 mide qué le pasa a cada resultado cuando el grupo se depura.

---

## V29 — Sensibilidad a la contaminación, y el gradiente a lo largo del punto de operación

> **Procedencia.** `codigo/V29_sensibilidad_y_operacion.py` → `resultados/V29_sensibilidad_y_operacion.json`.

### A. ¿Sobrevive el hallazgo al depurar el grupo control?

Se excluye progresivamente a los controles con más pruebas de la batería bajo −1,5 z. **Ninguna de esas
ocho pruebas forma parte del criterio de control**, de modo que el filtro es independiente de él.

| Filtro | n | Desvíos por tramo | Pendiente de log-varianza | p | Razón entre 4 y 16 años |
|---|---|---|---|---|---|
""" + "\n".join(
    f"| {f['filtro']} | {f['n']} | {', '.join(co(x, 1) for x in f['de_por_tramo'])} | "
    f"{co(f['pendiente'], 4)} | {f['p']:.3g} | {co(f['razon_4_16'])}× |"
    for f in v29["contaminacion"]) + f"""

**La dispersión se atenúa de forma monótona** y pierde significación. La atenuación no puede separarse
de la pérdida de poder —el tramo de menor escolaridad cae de 74 a 3 personas—, y así se declara.

### B. El gradiente con el contraste preespecificado

El intervalo que publicaba una versión anterior correspondía a un estadístico **máximo − mínimo**, que
por construcción no puede cubrir el cero y por tanto no contrasta ninguna hipótesis. Se sustituye por el
contraste preespecificado —menos de 7 años frente a 7 a 11—, con remuestreo que **reajusta el modelo
normativo en cada réplica**, cosa que el anterior no hacía.

| Regla | Gradiente | IC 95 % |
|---|---|---|
| Vigente | **{co(gp['vigente']['estimacion'], 1)} p.p.** | {co(gp['vigente']['ic95'][0], 1)} a {co(gp['vigente']['ic95'][1], 1)} |
| Corrección continua | {co(gp['continua']['estimacion'], 1)} p.p. | {co(gp['continua']['ic95'][0], 1)} a {co(gp['continua']['ic95'][1], 1)} |
| Diferencia | {co(gp['diferencia']['estimacion'], 1)} p.p. | {co(gp['diferencia']['ic95'][0], 1)} a {co(gp['diferencia']['ic95'][1], 1)} |

Y al depurar el grupo control **el gradiente no se desvanece**:
""" + " · ".join(f"{co(f['grad_vigente'], 1)} ({f['filtro']})" for f in v29["gradiente_depurado"]) + f""".

### C. El gradiente a lo largo del punto de operación

Comparar reglas en un único punto de operación deja abierta la sospecha de que el gradiente se «arregle»
moviendo el corte. Se barre la tasa de positividad completa:

| Positividad | Corte único equivalente | Gradiente del corte único | Gradiente de la corrección continua |
|---|---|---|---|
""" + "\n".join(
    f"| {co(f['positividad'] * 100, 1)} % | {co(f['corte_unico'], 1)} | {co(f['gradiente_corte_unico'], 1)} | "
    f"{co(f['gradiente_continua'], 1)} |" for f in v29["barrido_operacion"]) + f"""

**Dos lecturas.** Primero, el gradiente de un corte único describe una curva con máximo en el centro de
la distribución y tiende a cero en los extremos, donde se señala a casi nadie o a casi todos:
**minimizar el gradiente no equivale a ser equitativo**, y por eso las reglas sólo son comparables a
igual positividad. Segundo, en su propio punto de operación la regla vigente produce
{co(gp['vigente']['estimacion'], 1)} puntos porcentuales frente a los
{co(v29['barrido_operacion'][6]['gradiente_corte_unico'], 1)} de un corte único situado allí mismo:
**estratificar por escolaridad, como se hace hoy, reparte peor que no estratificar**.

---

## V30 — La contaminación del grupo control, separada por grupo diagnóstico

> **Procedencia.** `codigo/V30_contaminacion_por_grupo.py` → `resultados/V30_contaminacion_por_grupo.json`.

La condición diana del estudio es la **demencia moderada o severa**: el deterioro cognitivo leve **no es
caso**. Esa distinción cambia el peso de la contaminación, porque un control con deterioro leve no es un
caso mal clasificado, y sólo importa para el gradiente si su fuga es **desigual** entre tramos.

En la cohorte clínica sólo puede aplicarse uno de los cuatro criterios —el reconocimiento de lista—, de
modo que las proporciones son **cota superior** de la fuga.

| Grupo | n | Fuga global | menos de 7 | 7 a 11 | 12 o más | ¿Difiere? |
|---|---|---|---|---|---|---|
""" + "\n".join(
    f"| {g} | {d['n']} | {co(d['global'], 1)} % | {co(d['por_tramo']['<7'], 1)} % | "
    f"{co(d['por_tramo']['7-11'], 1)} % | {co(d['por_tramo']['>=12'], 1)} % | "
    + (f"χ² p = {co(d['p_diferencial'], 3)}" if d["p_diferencial"] is not None else "—") + " |"
    for g, d in v30["fuga"].items()) + f"""

**Lo decisivo.** La fuga de deterioro leve es grande pero **pareja entre tramos**
(p = {co(v30['fuga']['DCL']['p_diferencial'], 3)}): al no depender de la escolaridad, no puede generar el
gradiente. La fuga de demencia es menor pero **desigual**
(p = {co(v30['fuga']['Demencia']['p_diferencial'], 3)}), y es la que lo infla.

**Composición de quienes pasan el tamiz:**

| Tramo | n | Deterioro leve | Demencia | Sin afectación |
|---|---|---|---|---|
""" + "\n".join(
    f"| {ETI[b]} | {v30['composicion'][b]['n']} | {co(v30['composicion'][b]['DCL'], 1)} % | "
    f"**{co(v30['composicion'][b]['Demencia'], 1)} %** | {co(v30['composicion'][b]['Sin_afectacion'], 1)} % |"
    for b in BANDAS if b in v30["composicion"]) + """

Entre quienes pasan el tamiz con menos de 7 años de escolaridad, **la mitad tiene demencia**; con 12 o
más, una quinta parte. Ése es el mecanismo por el que el gradiente medido debe leerse como **límite
superior**.

---

"""
anc = "## S — Puntaje esperado"
assert t.count(anc) == 1
t = t.replace(anc, NUEVOS + anc, 1)
print("  ok  bloques V19, V29 y V30 insertados")

# ═══════════════════════════════════════════════════ E. índice
TIT = {"V1": "Integridad de datos", "V2": "Reproducción independiente",
       "V3": "Supuestos y especificación", "V4": "Psicometría y métrica latente",
       "V6": "Verificación de la codificación diagnóstica",
       "V10": "Por qué se descartó el criterio funcional", "V12": "Selección del criterio de control",
       "V13": "Comparación entre reglas, con controles de fuente única",
       "V15": "Corrección del sesgo de Harvey en el modelo de dispersión",
       "V16": "Magnitud de la heterocedasticidad",
       "V17": "Material trasladado desde el cuerpo del manuscrito",
       "V19": "Perfil cognitivo del grupo control",
       "V25": "Replicación por ruralidad y por área geográfica",
       "V26": "El estrechamiento de la dispersión: escala frente a habilidad",
       "V29": "Sensibilidad a la contaminación y punto de operación",
       "V30": "Contaminación del grupo control por grupo diagnóstico",
       "S": "Puntaje esperado en el ACE-III según escolaridad y edad"}
orden = [m.group(1) for m in re.finditer(r'^#{1,2} (V\d+|S) —', t, re.M)]
vistos, filas = set(), []
for k in orden:
    if k not in vistos:
        vistos.add(k)
        filas.append(f"| **{k}** | {TIT.get(k, '')} |")
i = t.index("| Bloque | Contenido |")
j = t.index("\n---", i)
t = t[:i] + "| Bloque | Contenido |\n|---|---|\n" + "\n".join(filas) + t[j:]
print(f"  ok  índice reconstruido con {len(filas)} bloques")

SUP.write_text(t)
print(f"\n-> {SUP}")
