#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V27b — Los puntos de corte publicados del IFS, aplicados a la misma muestra.

QUÉ OBLIGÓ A ESTE ANÁLISIS. La revisión bibliográfica del IFS cambió el encuadre de V27. La premisa
de V27 —«el IFS usa un corte fijo porque se asumió que la educación no importaba»— es **falsa como
descripción de la literatura**: Sierra Sanjurjo et al. (2018) ya publicaron normas del IFS
estratificadas por edad y educación, con grilla de corrección y cortes por estrato, y declararon
explícitamente que los estudios previos «se limitaron a participantes con alto nivel educativo, lo que
impide su generalización a poblaciones con menos de 12 años de educación formal». La revisión
sistemática de cribados en Latinoamérica (Custodio et al., 2020) pide de forma expresa que «la validez
diagnóstica del IFS se evalúe en poblaciones con bajo nivel educativo».

De modo que lo que ocurre no es que la literatura ignore la educación, sino que **la práctica clínica
sigue clasificando con el corte bruto de 25**, derivado en una muestra de 14,5 años de escolaridad
media, mientras la corrección publicada no se aplica. Es el mismo desajuste aguas abajo que el trabajo
ya documentó para el ACE-III.

LO QUE SE AGREGA AQUÍ, y que la bibliografía hace obligatorio:

  A. Los OCHO cortes publicados del IFS, aplicados a los mismos 342 controles. Van de 17 a 27,5 sobre
     una escala de 30: un tercio del rango del instrumento. Si un corte es una propiedad del
     instrumento, ocho valores distintos para el mismo instrumento no pueden serlo todos.

  B. Anclaje externo. Las medias y los desvíos de los grupos control publicados, ordenados por la
     escolaridad de su muestra, junto a nuestros tres tramos. La pregunta es si el desvío crece cuando
     la escolaridad baja **entre estudios independientes**, y no sólo dentro de nuestra muestra.

Cortes publicados que se aplican (todos sobre el total de 30 puntos):

  17     Moreira et al. 2014, Portugal, óptimo frente a enfermedad de Alzheimer
  17,5   Flowers Benton et al. 2014, Colombia (n = 395), óptimo frente a DCL y Alzheimer
  17,6   Custodio et al. 2024, Perú, óptimo para demencia en participantes ANALFABETOS
  18     Validación chilena (IFS-Ch), óptimo frente a demencia
  18,3   Custodio et al. 2024, Perú, óptimo para demencia en participantes alfabetizados
  22     Custodio et al. 2024, Perú, óptimo para DCL en participantes analfabetos
  22,5   Zabala et al. 2019, Colombia, policonsumidores
  23,7   Custodio et al. 2024, Perú, óptimo para DCL en participantes alfabetizados
  25     Torralva et al. 2009, Argentina (INECO), original — **es el que aplica la práctica local**
  25,5   Bruno et al. 2015, Argentina, esclerosis múltiple remitente-recurrente
  26,25  Pinasco et al. 2021, Argentina, traumatismo craneoencefálico
  27,5   Baez et al. 2014, Argentina, trastorno bipolar y TDAH

Salida: consola + resultados/V27b_cortes_publicados.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402

OUT = EST / "resultados"
BANDAS = ["<7", "7-11", ">=12"]
ETI = {"<7": "menos de 7", "7-11": "7 a 11", ">=12": "12 o más"}
R = {}

CORTES = [
    (17.0,  "Moreira 2014",        "Portugal",  "Alzheimer"),
    (17.5,  "Flowers Benton 2014", "Colombia",  "DCL y Alzheimer"),
    (17.6,  "Custodio 2024",       "Perú",      "demencia, analfabetos"),
    (18.0,  "IFS-Ch",              "Chile",     "demencia"),
    (18.3,  "Custodio 2024",       "Perú",      "demencia, alfabetizados"),
    (22.0,  "Custodio 2024",       "Perú",      "DCL, analfabetos"),
    (22.5,  "Zabala 2019",         "Colombia",  "policonsumidores"),
    (23.7,  "Custodio 2024",       "Perú",      "DCL, alfabetizados"),
    (25.0,  "Torralva 2009",       "Argentina", "original — el que se aplica"),
    (25.5,  "Bruno 2015",          "Argentina", "esclerosis múltiple"),
    (26.25, "Pinasco 2021",        "Argentina", "traumatismo craneoencefálico"),
    (27.5,  "Baez 2014",           "Argentina", "bipolar y TDAH"),
]

# grupos control publicados con media, desvío y escolaridad de la muestra
PUBLICADOS = [
    {"estudio": "Torralva 2009", "pais": "Argentina (INECO, Buenos Aires)", "n": 26,
     "educacion": 14.5, "ifs_media": 27.4, "ifs_de": 1.6},
    {"estudio": "IFS-Ch", "pais": "Chile", "n": 30,
     "educacion": 11.9, "ifs_media": 21.7, "ifs_de": 3.4},
]

# ─────────────────────────────────────────────────────────── datos
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw = pd.read_csv(NM / "Mix neuromentias - Base mixta 23+24 (valores).csv",
                   header=4, dtype=object, low_memory=False)
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
craw["doc"] = nd(craw["dni"]); craw["ctrl"] = es_control(craw).values
craw["IFS"] = pd.to_numeric(craw["IFS_Total"], errors="coerce")
com = (pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
       .merge(craw[["doc", "ctrl", "IFS"]], left_on="dni", right_on="doc", how="left"))
CTL = com[com.ctrl.fillna(False)].dropna(subset=["IFS", "edu", "Edad"]).reset_index(drop=True)
CTL["tr"] = pd.cut(CTL.edu, [-1, 6.5, 11.5, 99], labels=BANDAS)
print("=" * 104)
print(f"controles comunitarios con IFS: n = {len(CTL)}  " +
      " · ".join(f"{b}={int((CTL.tr == b).sum())}" for b in BANDAS))
R["n"] = {"total": int(len(CTL)), **{b: int((CTL.tr == b).sum()) for b in BANDAS}}

# ═══════════════════════════════════════════ A. los cortes publicados sobre la misma muestra
print("\n" + "=" * 104)
print("A. LOS DOCE CORTES PUBLICADOS DEL IFS, APLICADOS A LOS MISMOS 342 CONTROLES")
print("   (proporción de personas SIN DETERIORO que cada corte señalaría)\n")
print(f"   {'corte':>6}  {'procedencia':<22} {'población':<11} "
      f"{'<7':>7} {'7-11':>7} {'≥12':>7} {'total':>7}   gradiente")
R["cortes"] = []
for v, est, pais, pob in CORTES:
    fila = {"corte": v, "estudio": est, "pais": pais, "poblacion": pob}
    props = {}
    for b in BANDAS:
        s = CTL[CTL.tr == b]
        props[b] = round(float((s.IFS < v).mean() * 100), 1)
    fila["por_tramo"] = props
    fila["total"] = round(float((CTL.IFS < v).mean() * 100), 1)
    fila["gradiente"] = round(max(props.values()) - min(props.values()), 1)
    R["cortes"].append(fila)
    marca = "  <-- el que se aplica" if v == 25.0 else ""
    print(f"   {v:>6.2f}  {est:<22} {pais:<11} "
          f"{props['<7']:>6.1f}% {props['7-11']:>6.1f}% {props['>=12']:>6.1f}% "
          f"{fila['total']:>6.1f}% {fila['gradiente']:>10.1f} p.p.{marca}")

rango = [c[0] for c in CORTES]
R["rango_de_cortes"] = {"minimo": min(rango), "maximo": max(rango),
                        "amplitud": round(max(rango) - min(rango), 2),
                        "pct_de_la_escala": round((max(rango) - min(rango)) / 30 * 100, 1),
                        "n_cortes": len(CORTES)}
print(f"\n   Los cortes publicados abarcan de {min(rango)} a {max(rango)} sobre 30 puntos: "
      f"{max(rango)-min(rango):.2f} puntos, el {(max(rango)-min(rango))/30*100:.0f} % de la escala.")

# cuál sería el gradiente mínimo alcanzable con un corte único
g = [(c["gradiente"], c["corte"], c["total"]) for c in R["cortes"]]
gmin = min(g); gmax = max(g)
R["gradiente_extremos"] = {"minimo": {"corte": gmin[1], "gradiente": gmin[0], "señalados": gmin[2]},
                           "maximo": {"corte": gmax[1], "gradiente": gmax[0], "señalados": gmax[2]}}
print(f"   Gradiente mínimo entre los publicados: {gmin[0]:.1f} p.p. con el corte {gmin[1]} "
      f"(señala al {gmin[2]:.1f} % del total)")
print(f"   Gradiente máximo: {gmax[0]:.1f} p.p. con el corte {gmax[1]} "
      f"(señala al {gmax[2]:.1f} %)")

# ═══════════════════════════════════════════ B. anclaje externo
print("\n" + "=" * 104)
print("B. ANCLAJE EXTERNO — grupos control publicados y nuestros tramos, ordenados por escolaridad\n")
filas = []
for p in PUBLICADOS:
    filas.append({"fuente": p["estudio"] + " · " + p["pais"], "n": p["n"],
                  "educacion": p["educacion"], "media": p["ifs_media"], "de": p["ifs_de"],
                  "tipo": "publicado"})
for b in BANDAS:
    s = CTL[CTL.tr == b]
    filas.append({"fuente": f"San Juan · {ETI[b]} años", "n": int(len(s)),
                  "educacion": round(float(s.edu.mean()), 1),
                  "media": round(float(s.IFS.mean()), 1),
                  "de": round(float(s.IFS.std(ddof=1)), 2), "tipo": "propio"})
filas.sort(key=lambda f: -f["educacion"])
R["anclaje_externo"] = filas
print(f"   {'fuente':<34} {'n':>5} {'educación':>10} {'IFS medio':>10} {'DE':>7}")
for f in filas:
    print(f"   {f['fuente']:<34} {f['n']:>5} {f['educacion']:>10.1f} {f['media']:>10.1f} {f['de']:>7.2f}")

ed = np.array([f["educacion"] for f in filas]); de = np.array([f["de"] for f in filas])
me = np.array([f["media"] for f in filas])
r_de = stats.spearmanr(ed, de)
r_me = stats.spearmanr(ed, me)
R["correlaciones_entre_estudios"] = {
    "escolaridad_vs_de": {"rho": round(float(r_de.statistic), 3), "p": float(r_de.pvalue)},
    "escolaridad_vs_media": {"rho": round(float(r_me.statistic), 3), "p": float(r_me.pvalue)},
    "n_puntos": len(filas)}
print(f"\n   escolaridad de la muestra frente al DESVÍO del grupo control:  "
      f"rho de Spearman = {r_de.statistic:+.3f}  (n = {len(filas)} puntos)")
print(f"   escolaridad de la muestra frente a la MEDIA del grupo control: "
      f"rho de Spearman = {r_me.statistic:+.3f}")
print("\n   Nota: son sólo cinco puntos y dos provienen de estudios independientes. El signo es")
print("   consistente con el hallazgo interno, pero no constituye una prueba formal.")

# comparación directa con los dos estudios publicados
alto = CTL[CTL.tr == ">=12"]
R["comparacion_directa"] = {
    "San_Juan_ge12": {"n": int(len(alto)), "educacion": round(float(alto.edu.mean()), 1),
                      "media": round(float(alto.IFS.mean()), 2),
                      "de": round(float(alto.IFS.std(ddof=1)), 2)},
    "distancia_a_Torralva_en_DE_de_Torralva": round(float((27.4 - alto.IFS.mean()) / 1.6), 2),
    "distancia_a_Chile_en_DE_de_Chile": round(float((21.7 - alto.IFS.mean()) / 3.4), 2)}
cd = R["comparacion_directa"]
print(f"\n   Nuestro tramo de 12 o más años (media {cd['San_Juan_ge12']['media']}, "
      f"escolaridad {cd['San_Juan_ge12']['educacion']} años):")
print(f"     está a {cd['distancia_a_Torralva_en_DE_de_Torralva']:+.2f} desvíos del control de "
      f"Torralva (Buenos Aires, 14,5 años)")
print(f"     está a {cd['distancia_a_Chile_en_DE_de_Chile']:+.2f} desvíos del control chileno "
      f"(11,9 años)")

OUT.mkdir(exist_ok=True)
(OUT / "V27b_cortes_publicados.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V27b_cortes_publicados.json'}")
