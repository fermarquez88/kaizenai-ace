#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Estilo unificado para todas las tablas y figuras del trabajo.

Contrato de diseño, tomado de la tabla de puntajes esperados:
  · paleta: azul (rendimiento esperado / corrección continua), rojo (regla vigente),
    ámbar (régimen intermedio) y grises. Nada de verde.
  · tablas tipográficas: sin bordes verticales, una regla bajo el encabezado, bandas de color
    al 7 % para los regímenes, la columna del corte en rojo.
  · epígrafe de panel: «a  Frase declarativa», alineado a la izquierda.
  · nota al pie en gris, alineada a la izquierda.
  · coma decimal en todos los ejes y celdas.

Salidas: figuras/Tabla1.{jpg,pdf}, Tabla2, Tabla3  y  FIGURAS_Y_TABLAS.pdf
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(NM / "manuscritos"))
from nature_style import set_style, C as PAL              # noqa: E402
import matplotlib.pyplot as plt                            # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages       # noqa: E402
set_style()

SESGO_LOGCHI2 = 1.2703628454614782
TINTE = 0.07          # opacidad de las bandas de régimen
GRIS = PAL["ink2"]


# ─────────────────────────────────────────────────────────── motor de tablas
# Maquetación determinista: cada bloque reserva una altura fija en pulgadas y se posiciona
# en coordenadas absolutas, de modo que nada se superpone al cambiar el número de filas.
H_TIT, H_LIN, H_NOTA, H_FILA = 0.30, 0.19, 0.155, 0.245
G_TIT, G_SUB, G_NOTA = 0.10, 0.26, 0.20
MARGEN = 0.16


def tabla(titulo, subtitulo, columnas, filas, nota, anchos=None,
          resalta=None, tinte_fila=None, col_roja=None, ancho=9.6, alto_fila=None,
          bloque2=None):
    # bloque2: (rótulo, columnas, filas, anchos) — se dibuja debajo, dentro de la misma tabla
    resalta = resalta or set()
    tinte_fila = tinte_fila or {}
    nf, nc = len(filas), len(columnas)
    hf = alto_fila or H_FILA
    n_sub = len(subtitulo.split("\n")) if subtitulo else 0
    n_not = len(nota.split("\n")) if nota else 0
    n_enc = max(len(str(c).split("\n")) for c in columnas)
    # altura de cada fila según sus saltos de línea
    altos = [hf + (max(1, max(len(str(c).split("\n")) for c in fl)) - 1)*H_LIN for fl in filas]

    h_enc = H_LIN*n_enc + 0.16
    h_tab = sum(altos)
    h_b2 = 0.0
    if bloque2:
        _rot, _cols, _fils, _anch = bloque2
        h_b2 = 0.34 + H_LIN + 0.16 + len(_fils)*H_FILA + 0.30
    H = (MARGEN + H_TIT + G_TIT + n_sub*H_LIN + G_SUB + h_enc + h_tab + h_b2
         + (G_NOTA + n_not*H_NOTA if nota else 0) + MARGEN)

    fig = plt.figure(figsize=(ancho, H))
    inv = lambda pulg: 1 - pulg/H          # pulgadas desde arriba -> fracción de figura
    anchos = anchos or [1.0/nc]*nc
    acum = np.concatenate([[0], np.cumsum(anchos)])
    x0, x1 = MARGEN/ancho, 1 - MARGEN/ancho
    X = lambda f: x0 + f*(x1-x0)
    centros = [(acum[i]+acum[i+1])/2 for i in range(nc)]

    y = MARGEN
    fig.text(x0, inv(y), titulo, fontsize=12.4, ha="left", va="top", fontweight="semibold")
    y += H_TIT + G_TIT
    if subtitulo:
        fig.text(x0, inv(y), subtitulo, fontsize=9.2, color=PAL["ink"], ha="left", va="top",
                 linespacing=1.5)
        y += n_sub*H_LIN
    y += G_SUB

    y_enc = y
    for j, enc in enumerate(columnas):
        ha = "left" if j == 0 else "center"
        fig.text(X(acum[j]) if j == 0 else X(centros[j]), inv(y_enc), enc, fontsize=9.3,
                 ha=ha, va="top", fontweight="bold", linespacing=1.3)
    y += h_enc
    fig.add_artist(plt.Line2D([x0, x1], [inv(y-0.06)]*2, color=PAL["ink"], lw=1.1,
                              transform=fig.transFigure))

    yf = y
    for i, fl in enumerate(filas):
        h = altos[i]
        if i in tinte_fila:
            fig.patches.append(plt.Rectangle((x0, inv(yf+h)), x1-x0, h/H,
                                             transform=fig.transFigure, lw=0,
                                             color=tinte_fila[i], alpha=TINTE, zorder=0))
        peso = "bold" if i in resalta else "normal"
        for j, cel in enumerate(fl):
            col = PAL["crit"] if (col_roja is not None and j == col_roja) else PAL["ink"]
            ha = "left" if j == 0 else "center"
            fig.text(X(acum[j]) if j == 0 else X(centros[j]), inv(yf + h/2), str(cel),
                     fontsize=9.3, ha=ha, va="center", color=col, fontweight=peso,
                     linespacing=1.35, zorder=2)
        yf += h
    fig.add_artist(plt.Line2D([x0, x1], [inv(yf+0.02)]*2, color=PAL["baseline"], lw=0.8,
                              transform=fig.transFigure))

    if bloque2:
        rot, cols2, fils2, anch2 = bloque2
        yf += 0.34
        fig.text(x0, inv(yf), rot, fontsize=9.6, ha="left", va="top", fontweight="semibold")
        yf += H_LIN + 0.16
        ac2 = np.concatenate([[0], np.cumsum(anch2)])
        ce2 = [(ac2[i]+ac2[i+1])/2 for i in range(len(cols2))]
        for j, enc in enumerate(cols2):
            fig.text(X(ac2[j]) if j == 0 else X(ce2[j]), inv(yf), enc, fontsize=9.3,
                     ha="left" if j == 0 else "center", va="top", fontweight="bold")
        yf += H_LIN + 0.10
        fig.add_artist(plt.Line2D([x0, x1], [inv(yf-0.04)]*2, color=PAL["ink"], lw=1.0,
                                  transform=fig.transFigure))
        for i, fl in enumerate(fils2):
            for j, cel in enumerate(fl):
                fig.text(X(ac2[j]) if j == 0 else X(ce2[j]), inv(yf + H_FILA/2), str(cel),
                         fontsize=9.3, ha="left" if j == 0 else "center", va="center",
                         color=PAL["crit"] if i == 0 else PAL["ink"],
                         fontweight="bold" if i == 1 else "normal")
            yf += H_FILA
        fig.add_artist(plt.Line2D([x0, x1], [inv(yf+0.02)]*2, color=PAL["baseline"], lw=0.8,
                                  transform=fig.transFigure))
    if nota:
        fig.text(x0, inv(yf + G_NOTA), nota, fontsize=8.1, color=GRIS, ha="left", va="top",
                 linespacing=1.5)
    return fig


def guardar(fig, nombre):
    for ext in ("jpg", "pdf"):
        kw = {"pil_kwargs": {"quality": 95}} if ext == "jpg" else {}
        fig.savefig(EST / f"figuras/{nombre}.{ext}", dpi=300, bbox_inches="tight",
                    facecolor="white", **kw)
    print(f"  -> figuras/{nombre}.jpg + .pdf")


# ─────────────────────────────────────────────────────────── modelo normativo
craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
c40 = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
c40["doc"] = nd(c40["dni"]); c40["rec"] = pd.to_numeric(c40.LDR_Reconocimiento_A, errors="coerce")
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv").merge(
    c40[["doc", "rec"]].rename(columns={"doc": "dni"}), on="dni", how="left")
REF = com[com.rec >= 10].dropna(subset=["ACE", "edu", "Edad", "Sexo"])
mu = smf.ols("ACE ~ edu + I(edu**2) + Edad + C(Sexo)", data=REF).fit()
t2 = REF.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
PM = REF.Sexo.value_counts(normalize=True)["Mujer"]
esp = lambda e, a: float(mu.predict(pd.DataFrame({"edu":[e],"Edad":[a],"Sexo":["Mujer"]}))[0]*PM
                       + mu.predict(pd.DataFrame({"edu":[e],"Edad":[a],"Sexo":["Hombre"]}))[0]*(1-PM))
sg = lambda e, a: float(np.sqrt(np.exp(SESGO_LOGCHI2 +
                        sd.predict(pd.DataFrame({"edu":[e],"Edad":[a]}))[0])))
corte = lambda e: 86 if e >= 12 else 68
def regimen(e, a=65):
    c, E, P = corte(e), esp(e, a), esp(e, a) - 1.645*sg(e, a)
    return PAL["crit"] if c > E else (PAL["warn"] if c > P else PAL["blue"])

print(f"modelo sobre {len(REF)} controles comunitarios\n")

# ═══════════════════════════════════════════════════════════ TABLA 1
F1 = [
 ["Fuente primaria", "Validación argentino-chilena\ndel ACE-III (2020)²",
  "Validación del ACE en comunidad\nrural española (2006)⁹"],
 ["Instrumento", "ACE-III", "ACE (versión original)"],
 ["País de la muestra", "Argentina y Chile", "España, comunidad rural"],
 ["Vía de incorporación\na la práctica local", "directa",
  "protocolo impreso de la\nversión argentina"],
 ["Grupo control", "139 controles", "comunidad rural"],
 ["Escolaridad de\nlos controles", "14,4 años (DE 3,8)", "no expresada en años"],
 ["Criterio de nivel\neducativo", "no estratifica por educación",
  "edad de finalización\nde la escolaridad"],
 ["Rendimiento\ndiagnóstico informado", "sensibilidad 98 %\nespecificidad 82 %",
  "punto óptimo en el grupo\nde bajo nivel"],
 ["¿Propone un umbral en\n12 años de escolaridad?", "No", "No"],
]
fig = tabla(
 "Tabla 1. Procedencia documental de los dos puntos de corte en uso",
 "Cada corte proviene de un estudio distinto, sobre un instrumento distinto y una población distinta.",
 ["", "Corte de 86", "Corte de 68"], F1,
 "Ninguno de los dos estudios de origen propone la regla compuesta ni el umbral de los 12 años: cada uno derivó su corte para su propia\n"
 "población y lo informó con su alcance. El escalón de 18 puntos resulta de componer ambas fuentes en la práctica clínica. El vacío para\n"
 "baja escolaridad comenzó a cubrirse con una normatización específica sobre 500 personas con menos de 12 años de instrucción, que halló\n"
 "un corte óptimo de 68,5 con sensibilidad del 97 % y especificidad del 72 %.",
 anchos=[0.30, 0.35, 0.35], alto_fila=0.30, resalta={8},
 tinte_fila={8: PAL["blue"]}, ancho=10.2)
guardar(fig, "Tabla1"); plt.close(fig)

# ═══════════════════════════════════════════════════════════ TABLA 2
F2 = [
 ["n analítico", "758", "2112"],
 ["Período de reclutamiento", "2023–2024", "2020–2026"],
 ["Mujeres, %", "81,0", "59,1"],
 ["Edad, años, mediana [Q1–Q3]", "63,0 [57,0–69,0]", "73,0 [66,0–78,0]"],
 ["Escolaridad, años, mediana [Q1–Q3]", "10,0 [7,0–15,0]", "12,0 [8,0–16,0]"],
 ["   escolaridad < 7 años, n", "159", "184"],
 ["   escolaridad 7–11 años, n", "249", "606"],
 ["   escolaridad ≥ 12 años, n", "350", "1322"],
 ["ACE-III total, media (DE)", "77,6 (13,3)", "71,4 (18,7)"],
 ["Escolaridad declarada en 7, 12 o 17 años, %", "37,5", "47,3"],
 ["", "", ""],
 ["Flujo de la cohorte comunitaria", "n", ""],
 ["   registros iniciales", "867", ""],
 ["   edad ≥ 40 años", "866", ""],
 ["   con los 23 ítems completos", "814", ""],
 ["   con escolaridad válida", "776", ""],
 ["   eliminados por presencia en ambas cohortes", "−18", ""],
 ["   muestra analítica", "758", ""],
]
fig = tabla(
 "Tabla 2. Características de las dos cohortes y flujo de participantes",
 "Las cohortes se seleccionaron por criterios opuestos —participación voluntaria en un programa de salud cerebral frente a consulta\n"
 "por sospecha de deterioro—. Un resultado presente en ambas no puede atribuirse al mecanismo de selección de ninguna.",
 ["", "Comunitaria", "Clínica"], F2,
 "De los 90 excluidos, 52 no tenían los 23 ítems y 43 no tenían escolaridad válida; ninguno disponía de ambos datos, de modo que ninguno\n"
 "era recuperable. Los excluidos tenían menos escolaridad (10,34 frente a 12,03 años; p = 0,029) y menor puntaje (75,18 frente a 81,38;\n"
 "p = 0,001), diferencia declarada como limitación.",
 anchos=[0.46, 0.27, 0.27], alto_fila=0.235, resalta={0, 11, 17},
 ancho=9.8)
guardar(fig, "Tabla2"); plt.close(fig)

# ═══════════════════════════════════════════════════════════ TABLA 3
EDADES = [50, 60, 70, 80]
FILAS3 = [0, 2, 4, 6, 8, 10, 11, 12, 14, 16, 18, 20]
F3 = [[f"{e}", f"{corte(e)}"] + [f"{esp(e,a):.0f}  ({esp(e,a)-1.645*sg(e,a):.0f})" for a in EDADES]
      for e in FILAS3]
fig = tabla(
 "Tabla 3. Puntaje esperado en el ACE-III según escolaridad y edad",
 "Cada celda: el puntaje esperado en una persona sin deterioro y, entre paréntesis, el percentil 5. El color de fondo indica dónde cae el\n"
 "corte vigente: en rojo, por encima del rendimiento esperado; en ámbar, entre el esperado y el percentil 5.",
 ["Años de\nescolaridad", "Corte\nvigente"] + [f"{a} años" for a in EDADES], F3,
 "El percentil que ocupa el corte equivale a la proporción de personas sin deterioro de esa escolaridad que la regla señala: un mismo\n"
 "número ocupa el percentil 86 entre quienes no completaron ningún año de escuela y el percentil 5 entre quienes completaron once.\n"
 "Modelo de posición y dispersión estimado sobre 663 participantes comunitarios con memoria de reconocimiento normal —criterio\n"
 "independiente del ACE-III y sin gradiente educativo—, promediado sobre la distribución de sexo de la muestra y con la corrección de\n"
 "Harvey aplicada a la varianza. Valores ilustrativos: no constituyen normas poblacionales.",
 anchos=[0.15, 0.13] + [0.18]*4, alto_fila=0.245, col_roja=1,
 tinte_fila={i: regimen(e) for i, e in enumerate(FILAS3)},
 ancho=9.6,
 bloque2=("Posición del corte vigente dentro de su propio grupo, a los 65 años",
          ["Años de escolaridad"] + [f"{e}" for e in [0,4,8,11,12,16,20]],
          [["Corte vigente"] + [f"{corte(e)}" for e in [0,4,8,11,12,16,20]],
           ["Percentil que ocupa"] + [f"{100*stats.norm.cdf((corte(e)-esp(e,65))/sg(e,65)):.0f}"
                                      for e in [0,4,8,11,12,16,20]]],
          [0.23] + [0.11]*7))
guardar(fig, "Tabla3"); plt.close(fig)

# ═══════════════════════════════════════════════════════════ PDF con todo
ORDEN = [("Tabla1", "Tabla 1"), ("Tabla2", "Tabla 2"), ("Tabla3", "Tabla 3"),
         ("Figura1_forma_funcional", "Figura 1"), ("Figura2_falsacion", "Figura 2"),
         ("Figura3_corte_y_dispersion", "Figura 3"),
         ("Figura4_correccion_continua", "Figura 4")]
import matplotlib.image as mpimg
destino = EST / "FIGURAS_Y_TABLAS.pdf"
with PdfPages(destino) as pdf:
    for k, rot in ORDEN:
        img = mpimg.imread(str(EST / f"figuras/{k}.jpg"))
        h, w = img.shape[:2]
        anchura = 10.5
        f = plt.figure(figsize=(anchura, anchura*h/w + 0.30))
        a = f.add_axes([0, 0, 1, anchura*h/w/(anchura*h/w + 0.30)])
        a.imshow(img); a.axis("off")
        f.text(0.004, 0.995, rot, fontsize=8, color=GRIS, ha="left", va="top")
        pdf.savefig(f, dpi=300); plt.close(f)
print(f"\n-> {destino.name}  ({len(ORDEN)} páginas: 3 tablas + 4 figuras)")
print("listo")
