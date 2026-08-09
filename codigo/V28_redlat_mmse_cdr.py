#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V28 — ReDLat San Juan: el MMSE contra el CDR, una clasificación de referencia INDEPENDIENTE.

QUÉ APORTA ESTA BASE Y QUÉ NO.

Aporta lo que el trabajo nunca tuvo: el **CDR**, obtenido por entrevista al informante y por tanto
independiente del test cognitivo que se evalúa. Las cuatro auditorías coincidieron en que la objeción
que bloquea el manuscrito es no poder distinguir «la regla sobre-señala sanos» de «esos sanos están
genuinamente deteriorados». Con CDR esa distinción se puede hacer. Además el diseño es de **una sola
puerta**: casos y controles provienen del mismo estudio, con el mismo reclutamiento y los mismos
evaluadores, de modo que no arrastra la confusión entre cohorte y condición de caso.

No aporta el gradiente educativo, y conviene decirlo antes de mirar ningún resultado. ReDLat recluta
con criterios de elegibilidad de resonancia magnética y su muestra tiene 15,2 años de escolaridad
media entre los controles. **Con CDR = 0 hay UNA persona con menos de 7 años de escolaridad.** Ningún
análisis por tramo educativo es defendible en el extremo bajo, y este bloque no lo intenta.

Fuentes: `ReDLat2_DATA_*.csv` y `ReDLatSpanish_DATA_*.csv`, descargados de REDCap. Hay 46 registros
presentes en ambos; **manda ReDLat2**, por indicación del referente del sitio.

BLOQUES
  A. Fusión, cobertura y veredicto de factibilidad por tramo educativo
  B. El MMSE entre los controles definidos por CDR = 0: forma, dispersión y techo
  C. Exactitud diagnóstica de una sola puerta contra el CDR, y qué dice del 0,997 del manuscrito
  D. Dónde caen los cortes publicados del MMSE entre los controles con CDR = 0
  E. Techo comparado entre los tres instrumentos — con la advertencia de que las muestras difieren

Salida: consola + resultados/V28_redlat_mmse.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
DES = Path("/Users/fernandomarquez/Downloads")
OUT = EST / "resultados"
SESGO_LOGCHI2 = 1.2703628454614782
MAX_MMSE = 30
BANDAS = ["<7", "7-11", ">=12"]
ETI = {"<7": "menos de 7", "7-11": "7 a 11", ">=12": "12 o más"}
rng = np.random.default_rng(28)
R = {}

# cortes publicados del MMSE de uso corriente
CORTES_MMSE = [(24, "clásico, demencia (Folstein)"), (26, "deterioro cognitivo leve"),
               (27, "DCL, alta sensibilidad")]

# ═══════════════════════════════════════════════ A. fusión y factibilidad
# el exportador de REDCap deja también archivos *_LABELS_*, que traen los rótulos en vez de los
# códigos y no sirven aquí. Se excluyen y se toma el más reciente por fecha del nombre.
ult = lambda pat: sorted((f for f in DES.glob(pat) if "LABELS" not in f.name),
                         key=lambda f: f.name.split("_DATA_")[-1])[-1]
r1, r2 = ult("ReDLatSpanish_DATA_*.csv"), ult("ReDLat2_DATA_*.csv")
d1 = pd.read_csv(r1, dtype=str, low_memory=False, encoding="utf-8-sig")
d2 = pd.read_csv(r2, dtype=str, low_memory=False, encoding="utf-8-sig")
rep = set(d1.record_id.dropna()) & set(d2.record_id.dropna())
D = pd.concat([d2, d1[~d1.record_id.isin(rep)]], ignore_index=True).copy()
num = lambda c: pd.to_numeric(D.get(c), errors="coerce")
S = pd.DataFrame({"bn": D.record_id, "edu": num("cog_ed"), "edad": num("demo_age"),
                  "mmse": num("mmse_total"), "cdr": num("cdr_cdrtot"),
                  "sexo": D.get("demo_sex").astype(str)}).dropna()
S = S[S.edad >= 40].reset_index(drop=True)
S["tr"] = pd.cut(S.edu, [-1, 6.5, 11.5, 99], labels=BANDAS)
S["caso"] = (S.cdr >= 1).astype(int)

print("=" * 104)
print(f"ReDLat1 {r1.name}: {len(d1)} · ReDLat2 {r2.name}: {len(d2)} · repetidos {len(rep)} (manda ReDLat2)")
print(f"fusionado {len(d1) + len(d2) - len(rep)} · con edad, escolaridad, MMSE, CDR y sexo, y edad ≥ 40: {len(S)}")
R["fuentes"] = {"redlat1": r1.name, "redlat2": r2.name, "repetidos": len(rep),
                "regla": "ReDLat2 tiene precedencia en los registros repetidos",
                "n_fusionado": int(len(d1) + len(d2) - len(rep)), "n_analitico": int(len(S))}

print("\nA. FACTIBILIDAD POR TRAMO EDUCATIVO — se mira ANTES de cualquier resultado")
ct = pd.crosstab(S.tr, S.cdr == 0)
R["factibilidad"] = {}
for b in BANDAS:
    s = S[S.tr == b]
    R["factibilidad"][b] = {"n": int(len(s)), "cdr0": int((s.cdr == 0).sum()),
                            "cdr_0_5": int((s.cdr == 0.5).sum()), "casos": int((s.cdr >= 1).sum()),
                            "edu_media": round(float(s.edu.mean()), 1)}
    d_ = R["factibilidad"][b]
    print(f"   {ETI[b]:>12} años: n={d_['n']:>3}   CDR=0: {d_['cdr0']:>3}   "
          f"CDR=0,5: {d_['cdr_0_5']:>2}   CDR≥1: {d_['casos']:>3}")
n_bajo = R["factibilidad"]["<7"]["cdr0"]
R["veredicto_factibilidad"] = {
    "controles_cdr0_menos_de_7_anios": n_bajo,
    "gradiente_educativo_estimable": bool(n_bajo >= 30),
    "motivo": ("ReDLat recluta con criterios de elegibilidad de resonancia y su muestra de controles "
               "tiene escolaridad alta; el estrato de menos de 7 años queda vacío")}
print(f"\n   VEREDICTO: con CDR = 0 hay {n_bajo} control(es) con menos de 7 años de escolaridad.")
print("   El gradiente educativo NO es estimable en esta base. Este bloque no lo intenta.")

# ═══════════════════════════════════════════════ B. el MMSE entre los CDR = 0
print("\n" + "=" * 104 + "\nB. EL MMSE ENTRE LOS CONTROLES DEFINIDOS POR CDR = 0")
C0 = S[S.cdr == 0].copy()
print(f"   n = {len(C0)} · edad {C0.edad.mean():.1f} · escolaridad {C0.edu.mean():.1f} · "
      f"MMSE {C0.mmse.mean():.2f} (DE {C0.mmse.std(ddof=1):.2f})")
R["controles_cdr0"] = {"n": int(len(C0)), "edad": round(float(C0.edad.mean()), 1),
                       "edu": round(float(C0.edu.mean()), 1),
                       "mmse_media": round(float(C0.mmse.mean()), 2),
                       "mmse_de": round(float(C0.mmse.std(ddof=1)), 2),
                       "pct_del_maximo": round(float(C0.mmse.mean() / MAX_MMSE * 100), 1),
                       "en_el_techo": round(float((C0.mmse >= MAX_MMSE).mean() * 100), 1),
                       "a_2_del_techo": round(float((C0.mmse >= MAX_MMSE - 2).mean() * 100), 1)}
c0 = R["controles_cdr0"]
print(f"   techo: {c0['pct_del_maximo']} % del máximo · en 30: {c0['en_el_techo']} % · "
      f"≥28: {c0['a_2_del_techo']} %")

print("\n   por tramo (el de menos de 7 años se informa pero no se interpreta):")
R["mmse_por_tramo"] = {}
for b in BANDAS:
    s = C0[C0.tr == b]
    if not len(s):
        continue
    R["mmse_por_tramo"][b] = {"n": int(len(s)), "edu": round(float(s.edu.mean()), 1),
                              "media": round(float(s.mmse.mean()), 2),
                              "de": round(float(s.mmse.std(ddof=1)), 2) if len(s) > 1 else None,
                              "en_el_techo": round(float((s.mmse >= MAX_MMSE).mean() * 100), 1)}
    d_ = R["mmse_por_tramo"][b]
    de = f"{d_['de']:.2f}" if d_["de"] is not None else "  — "
    print(f"     {ETI[b]:>12} n={d_['n']:>3}  MMSE {d_['media']:5.2f} (DE {de})  "
          f"en 30: {d_['en_el_techo']:4.1f} %")

# efecto de la escolaridad entre los controles, y dispersión
m = smf.ols("mmse ~ edu + edad + C(sexo)", data=C0).fit(cov_type="HC3")
ci = m.conf_int().loc["edu"]
t2 = C0.assign(lr2=np.log(np.clip(m.resid ** 2, 1e-6, None)))
sd = smf.ols("lr2 ~ edu + edad", data=t2).fit()
cis = sd.conf_int().loc["edu"]
sg = lambda e_: float(np.sqrt(np.exp(SESGO_LOGCHI2 +
                              sd.predict(pd.DataFrame({"edu": [e_], "edad": [C0.edad.mean()]})).iloc[0])))
R["efecto_educacion_cdr0"] = {
    "pendiente_puntos_por_anio": round(float(m.params["edu"]), 4),
    "ic95": [round(float(ci[0]), 4), round(float(ci[1]), 4)], "p": float(m.pvalues["edu"]),
    "dispersion_pendiente_log_var": round(float(sd.params["edu"]), 4),
    "dispersion_ic95": [round(float(cis[0]), 4), round(float(cis[1]), 4)],
    "dispersion_p": float(sd.pvalues["edu"]),
    "sigma_edu8": round(sg(8), 3), "sigma_edu18": round(sg(18), 3),
    "razon_8_18": round(sg(8) / sg(18), 3)}
e = R["efecto_educacion_cdr0"]
print(f"\n   efecto de la escolaridad: {e['pendiente_puntos_por_anio']:+.4f} puntos/año "
      f"[{e['ic95'][0]:+.4f}, {e['ic95'][1]:+.4f}] p={e['p']:.2e}")
print(f"   dispersión: pendiente de log-varianza {e['dispersion_pendiente_log_var']:+.4f} "
      f"[{e['dispersion_ic95'][0]:+.4f}, {e['dispersion_ic95'][1]:+.4f}] p={e['dispersion_p']:.3f}")
print(f"   sigma: 8 años {e['sigma_edu8']:.2f} -> 18 años {e['sigma_edu18']:.2f}  "
      f"(razón {e['razon_8_18']:.2f}×)")
gr = [C0.loc[C0.tr == b, "mmse"].values for b in ["7-11", ">=12"]]
W, pl = stats.levene(*gr, center="median")
R["levene_7a11_vs_ge12"] = {"W": round(float(W), 3), "p": float(pl),
                            "de": [round(float(np.std(g, ddof=1)), 3) for g in gr]}
print(f"   Levene entre 7–11 y ≥12: W={W:.3f} p={pl:.4f}  "
      f"(DE {np.std(gr[0], ddof=1):.2f} frente a {np.std(gr[1], ddof=1):.2f})")

# ═══════════════════════════════════════════════ C. exactitud de una sola puerta
print("\n" + "=" * 104 + "\nC. EXACTITUD DIAGNÓSTICA DE UNA SOLA PUERTA CONTRA EL CDR")
CAS = S[S.cdr >= 1]; CTR = S[S.cdr == 0]
y = np.r_[np.ones(len(CAS)), np.zeros(len(CTR))]
x = np.r_[-CAS.mmse.values, -CTR.mmse.values]
auc = roc_auc_score(y, x)
bs = []
for _ in range(2000):
    i = rng.integers(0, len(y), len(y))
    if len(np.unique(y[i])) == 2:
        bs.append(roc_auc_score(y[i], x[i]))
lo, hi = np.percentile(bs, [2.5, 97.5])
R["auc_una_puerta"] = {"n_casos": int(len(CAS)), "n_controles": int(len(CTR)),
                       "auc": round(float(auc), 3),
                       "ic95": [round(float(lo), 3), round(float(hi), 3)]}
print(f"   MMSE frente a CDR ≥ 1: {len(CAS)} casos y {len(CTR)} controles")
print(f"   área bajo la curva = {auc:.3f}  IC 95 % [{lo:.3f}, {hi:.3f}]")
print(f"\n   El manuscrito informa 0,997 para el ACE-III con diseño de DOS puertas y declara esa cifra")
print(f"   como firma del sesgo de diseño. Aquí, con una sola puerta y referencia independiente, el")
print(f"   valor cae a {auc:.3f}: la inflación del diseño de dos puertas queda cuantificada.")
R["contraste_con_dos_puertas"] = {"ace_dos_puertas": 0.997, "mmse_una_puerta": round(float(auc), 3),
                                  "nota": ("son instrumentos y muestras distintos; el contraste ilustra "
                                           "la magnitud de la inflación, no la mide sobre el ACE-III")}

# ═══════════════════════════════════════════════ D. cortes del MMSE entre los CDR = 0
print("\n" + "=" * 104 + "\nD. DÓNDE CAEN LOS CORTES PUBLICADOS DEL MMSE ENTRE LOS CONTROLES CDR = 0")
R["cortes_mmse"] = []
for v, etq in CORTES_MMSE:
    fila = {"corte": v, "descripcion": etq,
            "total": round(float((C0.mmse < v).mean() * 100), 1)}
    for b in BANDAS:
        s = C0[C0.tr == b]
        fila[b] = round(float((s.mmse < v).mean() * 100), 1) if len(s) else None
    R["cortes_mmse"].append(fila)
    print(f"   corte {v} ({etq:<28}): total {fila['total']:5.1f} %   " +
          "   ".join(f"{ETI[b]}: {fila[b] if fila[b] is not None else '—'}" for b in BANDAS))

# ═══════════════════════════════════════════════ E. techo comparado
print("\n" + "=" * 104 + "\nE. TECHO COMPARADO ENTRE LOS TRES INSTRUMENTOS")
ifs = json.loads((OUT / "V27_replicacion_ifs.json").read_text())
ace = json.loads((OUT / "CIFRAS_MAESTRAS.json").read_text())
comp = [
    {"instrumento": "ACE-III", "maximo": 100, "muestra": "comunitaria San Juan (n = 342)",
     "control": "criterio de cuatro condiciones",
     "media_alta_ed": 85.33, "pct_del_maximo": 85.3,
     "de_media_ed": ace["dispersion"]["bruto"]["de_por_tramo"][1],
     "de_alta_ed": ace["dispersion"]["bruto"]["de_por_tramo"][2]},
    {"instrumento": "IFS", "maximo": 30, "muestra": "comunitaria San Juan (n = 342)",
     "control": "criterio de cuatro condiciones",
     "media_alta_ed": ifs["observado_bajo_corte"][">=12"]["IFS_media"],
     "pct_del_maximo": round(ifs["observado_bajo_corte"][">=12"]["IFS_media"] / 30 * 100, 1),
     "de_media_ed": ifs["observado_bajo_corte"]["7-11"]["IFS_de"],
     "de_alta_ed": ifs["observado_bajo_corte"][">=12"]["IFS_de"]},
    {"instrumento": "MMSE", "maximo": 30, "muestra": "ReDLat San Juan (n = " + str(len(C0)) + ")",
     "control": "CDR = 0, referencia independiente",
     "media_alta_ed": R["mmse_por_tramo"][">=12"]["media"],
     "pct_del_maximo": round(R["mmse_por_tramo"][">=12"]["media"] / 30 * 100, 1),
     "de_media_ed": R["mmse_por_tramo"]["7-11"]["de"],
     "de_alta_ed": R["mmse_por_tramo"][">=12"]["de"]},
]
for c in comp:
    c["razon_de_7a11_sobre_ge12"] = round(c["de_media_ed"] / c["de_alta_ed"], 2)
R["techo_comparado"] = comp
print(f"   {'instrumento':<11} {'máx':>4} {'media ≥12':>10} {'% del máx':>10} "
      f"{'DE 7–11':>8} {'DE ≥12':>8} {'razón':>7}")
for c in comp:
    print(f"   {c['instrumento']:<11} {c['maximo']:>4} {c['media_alta_ed']:>10.2f} "
          f"{c['pct_del_maximo']:>9.1f}% {c['de_media_ed']:>8.2f} {c['de_alta_ed']:>8.2f} "
          f"{c['razon_de_7a11_sobre_ge12']:>7.2f}")
print("\n   ADVERTENCIA: el MMSE proviene de otra muestra, con otra definición de control y otra")
print("   composición educativa. La fila es ilustrativa del orden esperado, no una comparación")
print("   controlada entre instrumentos.")

OUT.mkdir(exist_ok=True)
(OUT / "V28_redlat_mmse.json").write_text(json.dumps(R, ensure_ascii=False, indent=2))
print(f"\n-> {OUT/'V28_redlat_mmse.json'}")
