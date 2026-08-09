#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V27 — El análisis completo del ACE-III, reproducido sobre el IFS.

POR QUÉ ESTE INSTRUMENTO Y NO OTRO. El objeto que discute el trabajo es el instrumento de cribado que
clasifica comparando un puntaje BRUTO contra un número. En la base local hay exactamente dos: el
ACE-III, con dos cortes según escolaridad, y el **INECO Frontal Screening**, con un **corte fijo único
de 25 sobre 30** (Torralva 2009) que **no estratifica por educación**. Es el caso simétrico, y además:

  · es de otro dominio —ejecutivo, no memoria ni lenguaje—;
  · su contenido es casi no alfabetizado: series motoras, instrucciones conflictivas, control
    inhibitorio, meses hacia atrás, dígitos inversos, memoria de trabajo visual, refranes;
  · se administró a las MISMAS personas de las dos cohortes, de modo que la comparación no cambia de
    muestra, de evaluador ni de período.

QUÉ PREDICE V26. Si el estrechamiento de la dispersión lo produce la no linealidad de la escala cerca
del techo, entonces todo cribado acotado debe mostrarlo, y **más cuanto más bajo sea su techo**. El IFS
topa en 30 frente a los 100 del ACE-III. La predicción es que muestre MÁS compresión, no menos.

QUÉ FALSARÍA EL ARGUMENTO. Si el IFS —que apenas contiene lectoescritura— NO mostrara asociación
curvilínea con la escolaridad ni compresión, entonces el efecto sería específico del contenido del
ACE-III y el mensaje general del trabajo tendría que restringirse. Las dos salidas son informativas y
ninguna se privilegia de antemano.

⚠ ADVERTENCIA DE VALIDEZ — LEER ANTES DE USAR CUALQUIER RESULTADO ENTRE COHORTES.
El bloque V12 del material suplementario documenta que **las series motoras —subtest 1 del IFS— se
puntúan con escalas distintas en las dos bases: máximo 3 en una y 6 en la otra**. Los totales del IFS
de la cohorte comunitaria y de la clínica **NO están en la misma escala**, de modo que todo lo que
compara cohortes en este bloque —forma funcional, replicación de la curvatura, discontinuidad y prueba
de placebo entre cohortes— **no es válido hasta que se armonice el instrumento**, con un procedimiento
análogo al que se aplicó al ítem de reconocimiento del ACE-III (ver ARMONIZACION_RECONOCIMIENTO.md).

Lo que SÍ es válido, porque usa una sola base: la dispersión entre los 342 controles comunitarios, la
posición percentilar de los cortes y todo el bloque V27b.

Dos reservas adicionales del mismo orden: el total clínico se extrae con `max(bruto)` por evaluación,
lo que resuelve duplicados por el valor más alto y sesga al alza; y se supone, sin comprobarlo, que la
fila sin rótulo de subtest es la del total.

ESTRUCTURA — replica bloque por bloque el análisis del ACE-III:
  A. forma funcional (lineal · cuadrática · spline), pendiente marginal y replicación entre cohortes
  B. discontinuidad en 12 años, prueba de placebo sobre los catorce cortes y equivalencia
  C. dispersión entre controles: Levene, modelo de Harvey y posición percentilar del corte vigente
  D. techo: cuánta compresión cabe esperar y cuánta se observa
  E. cuadro comparativo ACE-III frente a IFS

Salida: consola + resultados/V27_replicacion_ifs.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import duckdb
from patsy import dmatrix
from scipy import stats

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402

OUT = EST / "resultados"
SESGO_LOGCHI2 = 1.2703628454614782
EDAD_REF = 65.0
CORTE_IFS = 25          # Torralva et al. 2009, J Int Neuropsychol Soc 15:777-86
MAX_IFS = 30
BANDAS = ["<7", "7-11", ">=12"]
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=BANDAS)
FQ = "y ~ edu + I(edu**2) + Edad + C(Sexo)"
R = {"_instrumento": {"nombre": "INECO Frontal Screening", "maximo": MAX_IFS,
                      "corte": CORTE_IFS, "estratifica_por_educacion": False,
                      "fuente_del_corte": "Torralva T, et al. J Int Neuropsychol Soc. 2009;15:777-86"}}


def lrt(m0, m1):
    c = 2 * (m1.llf - m0.llf); df = int(m1.df_model - m0.df_model)
    return {"chi2": round(float(c), 2), "df": df, "p": float(stats.chi2.sf(c, df))}


# ═══════════════════════════════════════════════════════ datos
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")

# ── comunitaria: el IFS vive en la planilla cruda de Neuromentia
craw = pd.read_csv(NM / "Mix neuromentias - Base mixta 23+24 (valores).csv",
                   header=4, dtype=object, low_memory=False)
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
craw["doc"] = nd(craw["dni"])
craw["ctrl"] = es_control(craw).values
craw["IFS"] = pd.to_numeric(craw["IFS_Total"], errors="coerce")
com = (pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
       .merge(craw[["doc", "ctrl", "IFS"]], left_on="dni", right_on="doc", how="left"))
com = com.dropna(subset=["IFS", "edu", "Edad", "Sexo"]).reset_index(drop=True)
com["cohorte"] = "comunitaria"

# ── clínica: el IFS vive en la base del Instituto
c = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)
ifs_cli = c.execute("""select eval_id, max(bruto) IFS from resultados_v2
                       where test = 'IFS' and (subtest is null or subtest = '')
                         and bruto is not null group by 1""").fetchdf()
ifs_cli["eval_id"] = ifs_cli.eval_id.astype(str)
cli = pd.read_csv(EST / "datos/clinico_definitivo.csv")
cli["eval_id"] = cli.eval_id.astype(str)
cli = cli.merge(ifs_cli, on="eval_id", how="left")
cli = cli.dropna(subset=["IFS", "edu", "Edad", "Sexo"])
cli = cli[cli.edu.between(0, 30)].reset_index(drop=True)
cli["cohorte"] = "clínica"; cli["ctrl"] = False

for d in (com, cli):
    d["y"] = d.IFS
COH = [("comunitaria", com), ("clínica", cli)]
print("=" * 100)
print(f"IFS disponible — comunitaria {len(com)} · clínica {len(cli)}")
R["n"] = {"comunitaria": int(len(com)), "clinica": int(len(cli))}
for nm, d in COH:
    t_ = TR(d.edu)
    R["n"][f"{nm}_por_tramo"] = {b: int((t_ == b).sum()) for b in BANDAS}
    print(f"   {nm:<13} " + " · ".join(f"{b}={int((t_ == b).sum())}" for b in BANDAS) +
          f"   media {d.y.mean():.1f} (DE {d.y.std():.1f})")

# ═══════════════════════════════════════════════════════ A. forma funcional
print("\n" + "=" * 100 + "\nA. FORMA FUNCIONAL")
R["forma"] = {}
for nm, d in COH:
    m1 = smf.ols("y ~ edu + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    m2 = smf.ols(FQ, data=d).fit(cov_type="HC3")
    sp = smf.ols("y ~ cr(edu, df=4) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    b2 = float(m2.params["I(edu ** 2)"]); ci = m2.conf_int().loc["I(edu ** 2)"]
    # pendiente marginal por método delta
    marg = {}
    for e_ in (3, 17):
        g = np.zeros(len(m2.params)); g[list(m2.params.index).index("edu")] = 1
        g[list(m2.params.index).index("I(edu ** 2)")] = 2 * e_
        val = float(g @ m2.params); se = float(np.sqrt(g @ m2.cov_params() @ g))
        marg[str(e_)] = {"b": round(val, 3), "ic95": [round(val - 1.96 * se, 3),
                                                      round(val + 1.96 * se, 3)]}
    R["forma"][nm] = {"cuad_vs_lin": lrt(smf.ols("y ~ edu + Edad + C(Sexo)", data=d).fit(),
                                         smf.ols(FQ, data=d).fit()),
                      "spline_vs_cuad": lrt(smf.ols(FQ, data=d).fit(),
                                            smf.ols("y ~ cr(edu, df=4) + Edad + C(Sexo)", data=d).fit()),
                      "b2": round(b2, 4), "ic95": [round(float(ci[0]), 4), round(float(ci[1]), 4)],
                      "p_b2": float(m2.pvalues["I(edu ** 2)"]), "marginal": marg}
    f = R["forma"][nm]
    print(f"   {nm:<13} cuadrático vs lineal p={f['cuad_vs_lin']['p']:.2e} · "
          f"spline vs cuadrático p={f['spline_vs_cuad']['p']:.3f}")
    print(f"   {'':13} curvatura {b2:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}] p={f['p_b2']:.2e} · "
          f"pendiente 3 años {marg['3']['b']:+.3f} -> 17 años {marg['17']['b']:+.3f}")

D = pd.concat([com[["y", "edu", "Edad", "Sexo", "cohorte"]],
               cli[["y", "edu", "Edad", "Sexo", "cohorte"]]], ignore_index=True)
mi = smf.ols("y ~ (edu + I(edu**2)) * C(cohorte) + Edad + C(Sexo)", data=D).fit(cov_type="HC3")
k = [p for p in mi.params.index if "I(edu ** 2):" in p][0]
cid = mi.conf_int().loc[k]
R["replicacion_curvatura"] = {"contraste": round(float(mi.params[k]), 4),
                              "ic95": [round(float(cid[0]), 4), round(float(cid[1]), 4)],
                              "p": float(mi.pvalues[k])}
print(f"\n   replicación de la curvatura entre cohortes: contraste {mi.params[k]:+.4f} "
      f"[{cid[0]:+.4f}, {cid[1]:+.4f}]  p={mi.pvalues[k]:.3f}")

# ═══════════════════════════════════════════════════════ B. discontinuidad y placebo
print("\n" + "=" * 100 + "\nB. ¿HAY DISCONTINUIDAD EN 12 AÑOS? (el IFS no estratifica, de modo que aquí")
print("   la pregunta es si la habría si alguien decidiera estratificarlo)")
R["discontinuidad"] = {}
for nm, d in COH:
    s = d.assign(post=(d.edu >= 12).astype(int))
    m = smf.ols("y ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
    ci = m.conf_int().loc["post"]
    R["discontinuidad"][nm] = {"escalon": round(float(m.params["post"]), 3),
                               "ic95": [round(float(ci[0]), 3), round(float(ci[1]), 3)],
                               "p": float(m.pvalues["post"])}
    print(f"   {nm:<13} {m.params['post']:+.3f}  IC95 [{ci[0]:+.3f}, {ci[1]:+.3f}]  p={m.pvalues['post']:.3f}")

print("\n   prueba de placebo sobre los catorce cortes candidatos:")
R["placebo"] = {}
for nm, d in COH:
    filas = []
    for u in range(4, 18):
        s = d.assign(post=(d.edu >= u).astype(int))
        if s.post.mean() in (0, 1) or min(s.post.sum(), len(s) - s.post.sum()) < 20:
            continue
        m = smf.ols("y ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
        filas.append({"umbral": u, "escalon": round(float(m.params["post"]), 3),
                      "p": float(m.pvalues["post"]), "z": abs(float(m.tvalues["post"]))})
    orden = sorted(filas, key=lambda r: -r["z"])
    puesto = [i for i, r in enumerate(orden, 1) if r["umbral"] == 12]
    R["placebo"][nm] = {"cortes": filas, "puesto_de_12": puesto[0] if puesto else None,
                        "de": len(filas)}
    print(f"   {nm:<13} el corte de 12 años ocupa el puesto {puesto[0] if puesto else '-'} de {len(filas)}"
          f"   (mayor señal: {orden[0]['umbral']} años, escalón {orden[0]['escalon']:+.3f}, "
          f"p={orden[0]['p']:.3f})")

print("\n   equivalencia (dos pruebas unilaterales) frente a márgenes en unidades del IFS:")
R["equivalencia"] = {}
for nm, d in COH:
    s = d.assign(post=(d.edu >= 12).astype(int))
    m = smf.ols("y ~ edu + I(edu**2) + post + Edad + C(Sexo)", data=s).fit(cov_type="HC3")
    b, se = float(m.params["post"]), float(m.bse["post"])
    R["equivalencia"][nm] = {}
    for mar in (5.4, 1.5, 0.9):     # 18/100·30 = 5,4 · el escalón del ACE llevado a la escala del IFS
        p = max(stats.norm.sf((b + mar) / se), stats.norm.cdf((b - mar) / se))
        R["equivalencia"][nm][str(mar)] = float(p)
    print(f"   {nm:<13} " + " · ".join(f"±{k}: p={v:.2e}"
                                       for k, v in R["equivalencia"][nm].items()))

# ═══════════════════════════════════════════════════════ C. dispersión entre controles
print("\n" + "=" * 100 + "\nC. DISPERSIÓN ENTRE LOS CONTROLES COMUNITARIOS")
CTL = com[com.ctrl.fillna(False)].copy().reset_index(drop=True)
CTL["tr"] = TR(CTL.edu)
print(f"   n = {len(CTL)}  " + " · ".join(f"{b}={int((CTL.tr == b).sum())}" for b in BANDAS))
gr = [CTL.loc[CTL.tr == b, "y"].values for b in BANDAS]
W, pl = stats.levene(*gr, center="median")
des = [round(float(np.std(g, ddof=1)), 3) for g in gr]
mu = smf.ols(FQ, data=CTL).fit()
t2 = CTL.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-6, None)))
sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
sg = lambda e_: float(np.sqrt(np.exp(SESGO_LOGCHI2 +
                                     sd.predict(pd.DataFrame({"edu": [e_], "Edad": [EDAD_REF]})).iloc[0])))
ci = sd.conf_int().loc["edu"]
R["dispersion"] = {"n": int(len(CTL)),
                   "por_tramo": {b: int((CTL.tr == b).sum()) for b in BANDAS},
                   "de_por_tramo": des, "levene_W": round(float(W), 3), "levene_p": float(pl),
                   "pendiente_log_var": round(float(sd.params["edu"]), 4),
                   "ic95": [round(float(ci[0]), 4), round(float(ci[1]), 4)],
                   "p": float(sd.pvalues["edu"]),
                   "sigma_edu0": round(sg(0), 3), "sigma_edu20": round(sg(20), 3),
                   "razon": round(sg(0) / sg(20), 3)}
print(f"   DE por tramo: {des}   Levene W={W:.3f} p={pl:.2e}")
print(f"   pendiente de log-varianza {sd.params['edu']:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}] "
      f"p={sd.pvalues['edu']:.2e}")
print(f"   sigma a los 65 años: 0 años {sg(0):.2f} -> 20 años {sg(20):.2f}  (razón {sg(0)/sg(20):.2f}×)")

print("\n   dónde cae el corte de 25 dentro de cada tramo:")
R["percentil_del_corte"] = {}
for e_ in (0, 4, 8, 11, 12, 17):
    g = pd.DataFrame({"edu": [e_], "Edad": [EDAD_REF], "Sexo": [CTL.Sexo.mode()[0]]})
    m_ = float(mu.predict(g).iloc[0]); s_ = sg(e_)
    pct = float(stats.norm.cdf((CORTE_IFS - m_) / s_) * 100)
    R["percentil_del_corte"][f"edu{e_}"] = {"esperado": round(m_, 2), "sigma": round(s_, 2),
                                            "percentil": round(pct, 1)}
    print(f"     {e_:>2} años: esperado {m_:5.2f} (σ {s_:4.2f})  -> el corte de 25 cae en el "
          f"percentil {pct:4.1f}")

# ═══════════════════════════════════════════════════════ D. techo
print("\n" + "=" * 100 + "\nD. TECHO — el IFS topa en 30; el ACE-III, en 100")
R["techo"] = {}
for b in BANDAS:
    s = CTL[CTL.tr == b]
    if not len(s):
        continue
    R["techo"][b] = {"n": int(len(s)), "media": round(float(s.y.mean()), 2),
                     "pct_del_maximo": round(float(s.y.mean() / MAX_IFS * 100), 1),
                     "en_el_techo": round(float((s.y >= MAX_IFS).mean() * 100), 1),
                     "a_2_del_techo": round(float((s.y >= MAX_IFS - 2).mean() * 100), 1)}
    d_ = R["techo"][b]
    print(f"   {b:>5} n={d_['n']:<4} media {d_['media']:5.2f} ({d_['pct_del_maximo']:.0f} % del máximo) · "
          f"=30: {d_['en_el_techo']:4.1f} %  ≥28: {d_['a_2_del_techo']:5.1f} %")

# ── proporción OBSERVADA de controles bajo cada corte, sin modelo de por medio
print("\n   proporción observada de controles bajo su corte (sin modelo):")
R["observado_bajo_corte"] = {}
for b in BANDAS:
    s_ = CTL[CTL.tr == b]
    corte_ace = 68 if b != ">=12" else 86
    R["observado_bajo_corte"][b] = {
        "n": int(len(s_)),
        "IFS_media": round(float(s_.y.mean()), 2), "IFS_de": round(float(s_.y.std(ddof=1)), 2),
        "pct_bajo_IFS25": round(float((s_.y < CORTE_IFS).mean() * 100), 1),
        "pct_bajo_su_corte_ACE": round(float((s_.ACE < corte_ace).mean() * 100), 1)}
    d_ = R["observado_bajo_corte"][b]
    print(f"     {b:>5} n={d_['n']:<4} IFS {d_['IFS_media']:5.2f} (DE {d_['IFS_de']:.2f}) · "
          f"bajo 25: {d_['pct_bajo_IFS25']:5.1f} %   |   bajo su corte de ACE: "
          f"{d_['pct_bajo_su_corte_ACE']:5.1f} %")

# ═══════════════════════════════════════════════════════ E. cuadro comparativo
ACE = json.loads((OUT / "CIFRAS_MAESTRAS.json").read_text())
R["comparacion"] = {
    "curvatura": {"ACE_comunitaria": ACE["forma"]["bruto"]["comunitaria"]["b"],
                  "ACE_clinica": ACE["forma"]["bruto"]["clinica"]["b"],
                  "IFS_comunitaria": R["forma"]["comunitaria"]["b2"],
                  "IFS_clinica": R["forma"]["clínica"]["b2"]},
    "curvatura_relativa_al_maximo": {
        "ACE_comunitaria": round(ACE["forma"]["bruto"]["comunitaria"]["b"] / 100 * 1000, 3),
        "IFS_comunitaria": round(R["forma"]["comunitaria"]["b2"] / MAX_IFS * 1000, 3),
        "ACE_clinica": round(ACE["forma"]["bruto"]["clinica"]["b"] / 100 * 1000, 3),
        "IFS_clinica": round(R["forma"]["clínica"]["b2"] / MAX_IFS * 1000, 3)},
    "dispersion_razon_extremos": {"ACE": ACE["dispersion"]["bruto"]["sigma_edu0"] /
                                  ACE["dispersion"]["bruto"]["sigma_edu20"],
                                  "IFS": R["dispersion"]["razon"]},
    "percentil_del_corte_sin_escolaridad": {
        "ACE_corte68": ACE["dispersion"]["percentil_del_corte"]["edu0_corte68"]["percentil_del_corte"],
        "IFS_corte25": R["percentil_del_corte"]["edu0"]["percentil"]},
    "percentil_del_corte_11_anios": {
        "ACE_corte68": ACE["dispersion"]["percentil_del_corte"]["edu11_corte68"]["percentil_del_corte"],
        "IFS_corte25": R["percentil_del_corte"]["edu11"]["percentil"]},
}
cc = R["comparacion"]
print("\n" + "=" * 100 + "\nE. ACE-III FRENTE A IFS")
print(f"   curvatura cruda        ACE {cc['curvatura']['ACE_comunitaria']:+.4f} / "
      f"{cc['curvatura']['ACE_clinica']:+.4f}   IFS {cc['curvatura']['IFS_comunitaria']:+.4f} / "
      f"{cc['curvatura']['IFS_clinica']:+.4f}")
print(f"   curvatura por mil del máximo del instrumento (comparable entre escalas)")
print(f"                          ACE {cc['curvatura_relativa_al_maximo']['ACE_comunitaria']:+.2f} / "
      f"{cc['curvatura_relativa_al_maximo']['ACE_clinica']:+.2f}   "
      f"IFS {cc['curvatura_relativa_al_maximo']['IFS_comunitaria']:+.2f} / "
      f"{cc['curvatura_relativa_al_maximo']['IFS_clinica']:+.2f}")
print(f"   razón de dispersión entre extremos   ACE {cc['dispersion_razon_extremos']['ACE']:.2f}×   "
      f"IFS {cc['dispersion_razon_extremos']['IFS']:.2f}×")
print(f"   percentil del corte sin escolaridad  ACE {cc['percentil_del_corte_sin_escolaridad']['ACE_corte68']:.0f}"
      f"   IFS {cc['percentil_del_corte_sin_escolaridad']['IFS_corte25']:.0f}")
print(f"   percentil del corte con 11 años      ACE {cc['percentil_del_corte_11_anios']['ACE_corte68']:.0f}"
      f"   IFS {cc['percentil_del_corte_11_anios']['IFS_corte25']:.0f}")

OUT.mkdir(exist_ok=True)
(OUT / "V27_replicacion_ifs.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V27_replicacion_ifs.json'}")
