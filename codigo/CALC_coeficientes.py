#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CALC — Reestima y publica los coeficientes del modelo normativo.

Por qué existe este script. El manuscrito declara, en disponibilidad de datos, que «se publican los
coeficientes del modelo normativo, que permiten reproducirlo sin acceder a los datos de origen». Esos
coeficientes viven en `resultados/CALC_coeficientes.json` y alimentan la calculadora en línea. La
auditoría del repositorio encontró que ese archivo **no lo generaba ningún script**: se había producido
en una sesión interactiva. Un archivo publicado como garantía de reproducibilidad que a su vez no es
reproducible es exactamente el defecto que la declaración pretende evitar.

Qué estima. Sobre los controles comunitarios —criterio de `criterio_control.py`— dos modelos:

  · POSICIÓN     ACE ~ edu + edu² + Edad + C(Sexo)
  · DISPERSIÓN   log(residuo²) ~ edu + Edad, con la corrección de sesgo de Harvey (1976)

La corrección de Harvey es indispensable: estimar log σ² por mínimos cuadrados sobre log(residuo²)
subestima la varianza en E[log χ²₁] = −1,27036. Sin ella, el 19 % de los controles cae bajo su propio
percentil 5 nominal; con ella, el 6,5 %. El intercepto que se publica **ya la incluye**, y se conserva
también el valor sin corregir para que la diferencia sea auditable.

El script verifica además que lo que produce coincide con lo publicado, y avisa si no.

Salida: resultados/CALC_coeficientes.json
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
sys.path.insert(0, str(EST / "codigo"))
from criterio_control import es_control                      # noqa: E402

OUT = EST / "resultados/CALC_coeficientes.json"
SESGO_LOGCHI2 = 1.2703628454614782      # = −(digamma(1/2) + log 2); Harvey 1976
FMU = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
FSD = "lr2 ~ edu + Edad"

# ─────────────────────────────────────────────────────────── datos: controles comunitarios
craw = pd.read_csv(NM / "Mix neuromentias - Base mixta 23+24 (valores).csv",
                   header=4, dtype=object, low_memory=False)
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"])
craw["ctrl"] = es_control(craw).values
REF = (pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
       .merge(craw[["doc", "ctrl"]], left_on="dni", right_on="doc", how="left"))
REF = REF[REF.ctrl.fillna(False)].dropna(subset=["ACE", "edu", "Edad", "Sexo"]).reset_index(drop=True)
print(f"controles comunitarios: n = {len(REF)}")

# ─────────────────────────────────────────────────────────── modelos
mu = smf.ols(FMU, data=REF).fit()
t2 = REF.assign(lr2=np.log(np.clip(mu.resid ** 2, 1e-6, None)))
sd = smf.ols(FSD, data=t2).fit()

sd_pub = dict(sd.params)
sd_pub["Intercept_sin_corregir"] = float(sd.params["Intercept"])
sd_pub["Intercept"] = float(sd.params["Intercept"]) + SESGO_LOGCHI2

sigma = lambda d, corr: np.sqrt(np.exp((SESGO_LOGCHI2 if corr else 0.0) + sd.predict(d)))
z = lambda corr: (REF.ACE - mu.predict(REF)) / sigma(REF, corr)
ver = {("corregido" if c else "sin_corregir"): {
           "pct_bajo_p5_nominal": round(float((z(c) < -1.6448536269514722).mean() * 100), 1),
           "de_de_los_z": round(float(z(c).std(ddof=1)), 3)} for c in (False, True)}

# validación cruzada de diez particiones sobre el modelo de posición
kf = KFold(n_splits=10, shuffle=True, random_state=7)
err = []
for tr, te in kf.split(REF):
    m = smf.ols(FMU, data=REF.iloc[tr]).fit()
    err.append(REF.iloc[te].ACE.values - m.predict(REF.iloc[te]).values)
err = np.concatenate(err)

R = {
    "mu": {k: float(v) for k, v in mu.params.items()},
    "sd": {k: float(v) for k, v in sd_pub.items()},
    "n": int(len(REF)),
    "p_sexo": {k: float(v) for k, v in REF.Sexo.value_counts(normalize=True).items()},
    "edad": [float(REF.Edad.min()), float(REF.Edad.max())],
    "edu": [float(REF.edu.min()), float(REF.edu.max())],
    "r2": float(mu.rsquared),
    "rmse": float(np.sqrt(np.mean(err ** 2))),
    "_correccion_harvey": {
        "constante": SESGO_LOGCHI2,
        "motivo": ("Estimar log(sigma^2) por MCO sobre log(residuo^2) subestima la varianza en "
                   "E[log(chi2_1)] = -1,27036 (Harvey 1976). El intercepto publicado ya la incluye."),
        "verificacion": ver},
    "_criterio_control": ("Reconocimiento de lista >= 10, sin antecedente de accidente cerebrovascular, "
                          "sin antecedente de traumatismo de craneo e independiente en las actividades "
                          "basicas del ADLQ (peldano 4 de la escalera de V22; chi2 p = 0,504 de "
                          "neutralidad educativa)"),
    "_procedencia": "codigo/CALC_coeficientes.py",
}

# ─────────────────────────────────────────────────────────── ¿coincide con lo ya publicado?
if OUT.exists():
    prev = json.loads(OUT.read_text())
    dif = [(k, prev["mu"].get(k), v) for k, v in R["mu"].items()
           if abs(prev["mu"].get(k, np.nan) - v) > 1e-6]
    dif += [(f"sd.{k}", prev["sd"].get(k), v) for k, v in R["sd"].items()
            if abs(prev["sd"].get(k, np.nan) - v) > 1e-6]
    if dif:
        print("\nATENCIÓN — los coeficientes reestimados NO coinciden con los publicados:")
        for k, a, b in dif:
            print(f"   {k}: publicado {a} -> reestimado {b}")
    else:
        print("los coeficientes reestimados coinciden con los publicados (tolerancia 1e-6)")
    if prev["n"] != R["n"]:
        print(f"ATENCIÓN — n publicado {prev['n']} frente a reestimado {R['n']}")

OUT.write_text(json.dumps(R, indent=1, ensure_ascii=False))
print(f"\nposición  R² = {R['r2']:.4f}   error cuadrático medio en validación cruzada = {R['rmse']:.3f}")
print(f"dispersión  pendiente por año de escolaridad = {sd.params['edu']:+.5f}")
print(f"calibración  bajo el percentil 5 nominal: sin corregir "
      f"{ver['sin_corregir']['pct_bajo_p5_nominal']} % · corregido "
      f"{ver['corregido']['pct_bajo_p5_nominal']} %")
print(f"-> {OUT}")
