#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera las tres tablas del manuscrito desde resultados/CIFRAS_MAESTRAS.json.

Regla del reglamento CAN respetada: **ningún dato aparece a la vez en tabla y en figura.**
  - Forma funcional, falsación y consecuencia clasificatoria -> SÓLO figuras.
  - Procedencia documental, características de cohortes y psicometría -> SÓLO tablas.

Salida: manuscrito/Tabla1.md (procedencia), Tabla2.md (cohortes), Tabla3.md (psicometría)
"""
import json
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
M = json.loads((EST / "resultados/CIFRAS_MAESTRAS.json").read_text())
DIF = json.loads((EST / "resultados/V4b_dif_ordinal.json").read_text())
MAN = EST / "manuscrito"
n = lambda v: f"{v}".replace(".", ",")
ic = lambda a: f"{a[0]:+.2f} a {a[1]:+.2f}".replace(".", ",")

# ══════════════════════════════════════════════ TABLA 1 — procedencia documental
T1 = """## Tabla 1. Procedencia documental de los dos puntos de corte en uso

| | **Corte de 86** | **Corte de 68** |
|---|---|---|
| Fuente primaria | Validación argentino-chilena del ACE-III (2020)² | Validación del ACE en comunidad rural española (2006)⁷ |
| Vía de incorporación a la práctica local | directa | protocolo impreso de la versión argentina |
| **Instrumento** | **ACE-III** | **ACE (versión original)** |
| **País de la muestra** | Argentina y Chile | **España (comunidad rural)** |
| Composición del grupo control | 139 controles | comunidad rural |
| **Escolaridad de los controles** | **14,4 años (DE 3,8)** | no expresada en años |
| **Criterio de nivel educativo** | **no estratifica por educación** | **edad de finalización de la escolaridad** |
| Rendimiento diagnóstico informado | sensibilidad 98 %, especificidad 82 % | punto óptimo en el grupo de bajo nivel |
| ¿Propone un umbral en 12 años de escolaridad? | **No** | **No** |

**Nota.** La verificación del texto completo de la validación argentino-chilena² confirma que
propone un único punto de corte, sin estratificación por nivel educativo, y que declara la
composición educativa de su muestra. El valor 68 y el umbral de «menos de 12 años de educación»
figuran en el protocolo impreso de la versión argentina del ACE-III, que consigna además valores
normativos basados en 63 controles y 142 pacientes. El único estudio argentino de valores normativos
en bajo nivel socioeducativo⁸ se realizó sobre el ACE (no sobre el ACE-III), con 44 controles de
6 años de escolaridad media, definió el nivel por el índice de Hollingshead —que combina educación
y ocupación— y recomendó un corte de 70.

**El escalón de 18 puntos en los 12 años de escolaridad resulta de componer ambas fuentes. El
umbral no aparece en ninguna de las dos.**
"""
(MAN / "Tabla1.md").write_text(T1)

# ══════════════════════════════════════════════ TABLA 2 — cohortes
d = M["descriptivos"]; co, cl = d["comunitaria"], d["clinica"]
fl = M["n"]["flujo_comunitaria"]; ex = M["n"]["excluidos_comunitaria"]
fa = M["faltantes"]
T2 = f"""## Tabla 2. Características de las dos cohortes y flujo de participantes

Las cohortes fueron seleccionadas por criterios opuestos —participación voluntaria en un programa
de salud cerebral frente a consulta por sospecha de deterioro—. Esa oposición es el fundamento del
diseño: un resultado presente en ambas no puede atribuirse al mecanismo de selección de ninguna.

| | Comunitaria | Clínica |
|---|---|---|
| n analítico | **{co['n']}** | **{cl['n']}** |
| Período de reclutamiento | 2023–2024 | 2020–2026 |
| Mujeres, % | {n(co['mujeres_pct'])} | {n(cl['mujeres_pct'])} |
| Edad, años, mediana [Q1–Q3] | {n(co['edad_mediana'])} [{n(co['edad_q1'])}–{n(co['edad_q3'])}] | {n(cl['edad_mediana'])} [{n(cl['edad_q1'])}–{n(cl['edad_q3'])}] |
| Escolaridad, años, mediana [Q1–Q3] | {n(co['edu_mediana'])} [{n(co['edu_q1'])}–{n(co['edu_q3'])}] | {n(cl['edu_mediana'])} [{n(cl['edu_q1'])}–{n(cl['edu_q3'])}] |
| Escolaridad <7 años, n | {co['n_lt7']} | {cl['n_lt7']} |
| Escolaridad 7–11 años, n | {co['n_7a11']} | {cl['n_7a11']} |
| Escolaridad ≥12 años, n | {co['n_ge12']} | {cl['n_ge12']} |
| ACE-III total, media (DE) | {n(co['ACE_media'])} ({n(co['ACE_de'])}) | {n(cl['ACE_media'])} ({n(cl['ACE_de'])}) |
| Escolaridad declarada en 7, 12 o 17 años, % | 37,5 | 47,3 |

### Flujo de participantes (cohorte comunitaria)

| Etapa | n |
|---|---|
| Registros iniciales | {fl['crudo']} |
| Edad ≥40 años | {fl['edad_ge40']} |
| Con los 23 ítems del ACE-III completos | {fl['items_completos']} |
| Con escolaridad válida | {fl['educacion_valida']} |
| **Eliminados por presencia en ambas cohortes** | **−{M['n']['solapamiento_excluido']}** |
| **Muestra analítica** | **{fl['menos_solapamiento']}** |

**Motivo de exclusión de los {ex['total']} participantes con datos faltantes:** {ex['sin_items']} sin
los 23 ítems, {ex['sin_educacion']} sin escolaridad válida, **{ex['recuperables']} con ambos datos
disponibles**. Al ser los motivos casi disjuntos, ningún excluido era recuperable.

**Comparación de excluidos frente a incluidos** (a declarar como limitación): edad
{n(fa['edad']['incluidos_media'])} frente a {n(fa['edad']['excluidos_media'])} años (p = {n(round(fa['edad']['p'],3))});
escolaridad {n(fa['educación']['incluidos_media'])} frente a {n(fa['educación']['excluidos_media'])} años
(p = {n(round(fa['educación']['p'],3))}); ACE-III {n(fa['ACE-III (columna)']['incluidos_media'])} frente a
{n(fa['ACE-III (columna)']['excluidos_media'])} puntos (p = {n(round(fa['ACE-III (columna)']['p'],3))}).
"""
(MAN / "Tabla2.md").write_text(T2)

# ══════════════════════════════════════════════ TABLA 3 — psicometría
LAB = {'ACE_LLectura': 'Lectura de palabras irregulares', 'ACE_FluVerbSPC': 'Fluencia semántica',
       'ACE_LCompDibujo': 'Comprensión lectora', 'ACE_LEscrit': 'Escritura',
       'ACE_FluVerbFPC': 'Fluencia fonológica', 'ACE_MReconocNyD': 'Reconocimiento nombre y dirección',
       'ACE_HabPerLetras': 'Letras fragmentadas', 'ACE_HabVisoCubo': 'Copia del cubo',
       'ACE_MRecuerdoNyD': 'Recuerdo diferido nombre y dirección', 'ACE_AtRegistro': 'Registro de 3 palabras'}
it = sorted(DIF["items"].items(), key=lambda t: -t[1]["dR2"])[:8]
filas = "\n".join(
    f"| {LAB.get(k, k.replace('ACE_',''))} | {n(round(v['dR2'],4))} | {n(round(v['q'],4))} | despreciable | "
    f"{'alta escolaridad' if v['beta'] < 0 else 'baja escolaridad'} |" for k, v in it)
p = M["psicometria"]; dtf = p["dtf_total"]; tr = M["test_retest"]
T3 = f"""## Tabla 3. Funcionamiento diferencial del ítem y del test según escolaridad

Modelo de respuesta graduada de Samejima sobre la muestra combinada con los 23 ítems completos
(n = {M['n']['con_items_completos']['combinada']}). Discriminación mediana **{n(p['grm_a_mediana'])}**
(rango {n(p['grm_a_rango'][0])}–{n(p['grm_a_rango'][1])}); correlación entre la habilidad latente y el
puntaje bruto **{n(p['theta_r_con_bruto'])}**.

### A. Funcionamiento diferencial del ítem (cohorte comunitaria, n focal = {p['dif_educacion']['n_focal']})

Regresión logística ordinal de Zumbo con purificación iterativa del anclaje y control de la tasa de
falso descubrimiento. Umbral de relevancia: ΔR² de Nagelkerke ≥ 0,035.

| Ítem | ΔR² de Nagelkerke | q (FDR) | Magnitud | Favorece a |
|---|---|---|---|---|
{filas}

**Ítems con funcionamiento diferencial de magnitud no trivial: {p['dif_educacion']['items_no_triviales']} de 23.**
Nueve ítems alcanzaron significación estadística, todos con efecto despreciable. Los sesgos son
**bidireccionales**: alfabetización y visoconstrucción favorecen a la escolaridad alta; las
fluencias verbales y el recuerdo diferido, a la baja.

### B. Funcionamiento diferencial del test completo

A igual habilidad latente, diferencia del puntaje total entre baja (<12 años) y alta escolaridad:

| Cohorte | Diferencia, puntos | IC 95 % | p | R² del modelo |
|---|---|---|---|---|
| Comunitaria | **{n(dtf['comunitaria']['dtf_baja_vs_alta'])}** | {ic(dtf['comunitaria']['ic95'])} | {n(round(dtf['comunitaria']['p'],3))} | 0,983 |
| Clínica | **{n(dtf['clinica']['dtf_baja_vs_alta'])}** | {ic(dtf['clinica']['ic95'])} | {n(round(dtf['clinica']['p'],3))} | 0,985 |
| *Corrección que aplica la regla vigente* | *18* | — | — | — |

### C. Escala de referencia del instrumento

Test-retest en **{tr['n_pares']} pares** de {tr['n_personas']} personas de la cohorte clínica.
Coeficiente de correlación intraclase **{n(tr['icc'])}**; correlación test-retest {n(tr['r'])}.
Error estándar de medición estimado entre **{n(tr['eem_rango_declarable'][0])} y
{n(tr['eem_rango_declarable'][1])} puntos** según el método de estimación.

**El escalón de 18 puntos equivale a {n(tr['escalon_en_eem'])} errores estándar de medición del
propio instrumento.**

### D. Invarianza entre cohortes

{p['invarianza_cohorte_items_moderados']} de 23 ítems —todos de alfabetización— mostraron
funcionamiento diferencial de magnitud moderada entre la cohorte comunitaria y la clínica. Por esa
razón el análisis emplea un marco único con interacciones cohorte × escolaridad y **no reporta en
ningún caso una estimación marginal combinada**.
"""
(MAN / "Tabla3.md").write_text(T3)
print("-> manuscrito/Tabla1.md (procedencia), Tabla2.md (cohortes), Tabla3.md (psicometría)")
for f in ("Tabla1", "Tabla2", "Tabla3"):
    print(f"   {f}.md  {len((MAN/(f+'.md')).read_text().split())} palabras")
