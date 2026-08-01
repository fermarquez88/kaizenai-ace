#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CONTROL CRITICO del Bloque 2.

El compuesto de bateria basado en `z_pdf` esta normado por bandas edad x EDUCACION (la base
tiene "Normas baja ed"), de modo que la educacion ya esta parcialmente removida del z. Comparar
un ACE-III crudo contra un z normado por educacion inflaria artificialmente el contraste.

Aca se reconstruye el compuesto con los puntajes BRUTOS, estandarizados DENTRO de la muestra
(z de muestra, sin normas) -> libre de ajuste educativo por construccion. Solo asi el contraste
"la educacion mueve al ACE pero no a la bateria" es interpretable.

Ademas: prueba formal de que la CURVATURA (no la pendiente media) difiere entre desenlaces, y
evidencia directa del mecanismo techo.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, duckdb
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
OUTD = NM / "ACE/out"
R = {}

cli = pd.read_csv(NM / "analisis/ace_items_clinico_v2.csv").rename(columns={"ed_anos_completos": "edu"})
cli["edu"] = pd.to_numeric(cli.edu, errors="coerce").mask(lambda s: s > 30)
con = duckdb.connect(str(INECO / "db/evaluaciones_v2.duckdb"), read_only=True)

# --- brutos de todos los tests NO-ACE, en formato largo
raw = con.execute("""
    select eval_id, test, coalesce(subtest,'') sub, name, bruto
    from resultados_v2
    where bruto is not null and lower(test) not like '%ace%'
""").fetchdf()
raw = raw[raw.eval_id.isin(cli.eval_id)]
raw["var"] = raw["test"].fillna("") + "|" + raw["sub"].fillna("") + "|" + raw["name"].fillna("")

# solo variables presentes en >=60% de las evaluaciones (evita composicion variable por paciente)
nev = cli.eval_id.nunique()
cov = raw.groupby("var").eval_id.nunique()
keep = cov[cov >= 0.60 * nev].index
raw = raw[raw["var"].isin(keep)]
print(f"variables de bateria retenidas (cobertura >=60%): {len(keep)}  de {cov.size}")
print("  ", ", ".join(sorted(keep)[:12]), "...")

# --- z DE MUESTRA por variable (sin normas) + orientacion (mayor = mejor)
# tests donde MAYOR ES PEOR (tiempos / errores) -> se invierten
PEOR = ("tiempo", "time", "error", "perseverac", "intrusion", "falso", "tmt", "trail", "stroop time")
def signo(v):
    s = v.lower()
    return -1.0 if any(p in s for p in PEOR) else 1.0

raw["z_muestra"] = raw.groupby("var").bruto.transform(
    lambda s: (s - s.mean()) / s.std() if s.std() and s.std() > 0 else np.nan)
raw["z_muestra"] *= raw["var"].map(signo)
raw = raw[raw.z_muestra.abs() <= 5]

comp = raw.groupby("eval_id").agg(BAT_raw=("z_muestra", "mean"), n_var=("z_muestra", "size")).reset_index()
d = cli.merge(comp, on="eval_id", how="inner")
d = d[d.n_var >= 8].dropna(subset=["edu", "Edad", "Sexo", "ACE_total", "BAT_raw"])
print(f"muestra analitica: n={len(d)}  | variables por eval: mediana {d.n_var.median():.0f}")

# orientacion del compuesto: debe correlacionar positivo con el ACE
r_ace = d.BAT_raw.corr(d.ACE_total)
print(f"correlacion compuesto-bruto vs ACE-III: r={r_ace:.3f}  (debe ser positiva y sustancial)")
R["r_compuesto_ACE"] = round(float(r_ace), 3)

d["ACE_z"] = (d.ACE_total - d.ACE_total.mean()) / d.ACE_total.std()
d["BAT_z"] = (d.BAT_raw - d.BAT_raw.mean()) / d.BAT_raw.std()


def perfil(y, lab):
    mq = smf.ols(f"{y} ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    ml = smf.ols(f"{y} ~ edu + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    nm = list(mq.params.index); i1, i2 = nm.index("edu"), nm.index("I(edu ** 2)")
    V = np.asarray(mq.cov_params()); b1, b2 = mq.params.iloc[i1], mq.params.iloc[i2]
    o = {"lineal": round(float(ml.params["edu"]), 4), "b2": round(float(b2), 5),
         "p_b2": float(mq.pvalues.iloc[i2]), "marginal": {}}
    for e in (3, 7, 12, 17):
        g = np.zeros(len(nm)); g[i1] = 1; g[i2] = 2 * e
        est = float(b1 + 2 * b2 * e); se = float(np.sqrt(g @ V @ g))
        o["marginal"][str(e)] = [round(est, 3), round(est - 1.96 * se, 3), round(est + 1.96 * se, 3)]
    m = "  ".join(f"e{k}:{v[0]}[{v[1]},{v[2]}]" for k, v in o["marginal"].items())
    print(f"  {lab:<34} lin={o['lineal']:<7} b2={o['b2']:<9} p={o['p_b2']:.1e}\n     {m}")
    return o


print("\nPendiente educativa (DE del desenlace por año), ajustada edad+sexo, HC3:")
R["ACE"] = perfil("ACE_z", "ACE-III")
R["BATERIA_bruta"] = perfil("BAT_z", "Bateria SIN ACE (brutos)")

# --- test formal: la CURVATURA difiere entre desenlaces (apareado, cluster por persona)
lon = pd.concat([d.assign(Y=d.ACE_z, inst="1_ACE"), d.assign(Y=d.BAT_z, inst="2_BAT")])
m_full = smf.ols("Y ~ (edu + I(edu**2))*C(inst) + Edad + C(Sexo)", data=lon).fit(
    cov_type="cluster", cov_kwds={"groups": lon.persona_id})
m_red = smf.ols("Y ~ edu*C(inst) + I(edu**2) + Edad + C(Sexo)", data=lon).fit(
    cov_type="cluster", cov_kwds={"groups": lon.persona_id})
kq = [i for i in m_full.params.index if i.startswith("I(edu ** 2):")]
R["curvatura_difiere_entre_instrumentos"] = {
    "coef": round(float(m_full.params[kq[0]]), 5), "p": float(m_full.pvalues[kq[0]]),
    "ic95": [round(x, 5) for x in m_full.conf_int().loc[kq[0]].tolist()]}
print(f"\n>> CURVATURA difiere entre ACE y bateria: coef={R['curvatura_difiere_entre_instrumentos']['coef']} "
      f"IC95 {R['curvatura_difiere_entre_instrumentos']['ic95']} p={R['curvatura_difiere_entre_instrumentos']['p']:.2e}")

# --- gradiente del ACE que persiste fijando la cognicion medida por la bateria
ma = smf.ols("ACE_z ~ edu + BAT_z + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
R["ACE_ajustado_por_bateria"] = {"b_edu": round(float(ma.params["edu"]), 4),
                                 "ic95": [round(x, 4) for x in ma.conf_int().loc["edu"].tolist()],
                                 "p": float(ma.pvalues["edu"]),
                                 "crudo": R["ACE"]["lineal"],
                                 "pct_persiste": round(100 * float(ma.params["edu"]) / R["ACE"]["lineal"], 1)}
print(f">> gradiente educativo del ACE fijando la bateria: {R['ACE_ajustado_por_bateria']['b_edu']} DE/año "
      f"({R['ACE_ajustado_por_bateria']['pct_persiste']}% del crudo) p={R['ACE_ajustado_por_bateria']['p']:.1e}")

# --- mecanismo TECHO: dispersion y proximidad al maximo por tramo educativo
print("\nMecanismo techo — ACE-III por tramo educativo (clinica):")
b = pd.cut(d.edu, [-1, 6.5, 10.5, 12.5, 99], labels=["<7", "7-10", "11-12", ">12"])
t = d.groupby(b, observed=True).ACE_total.agg(["count", "mean", "std",
                                               lambda s: 100 * (s >= 90).mean()]).round(2)
t.columns = ["n", "media", "DE", "pct>=90"]
print(t.to_string())
R["techo_por_tramo"] = t.reset_index().to_dict("records")

OUTD.mkdir(exist_ok=True)
(OUTD / "11_bateria_bruta.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> {OUTD/'11_bateria_bruta.json'}")
