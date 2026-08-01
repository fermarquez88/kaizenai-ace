#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Forma funcional educacion -> ACE-III en dos cohortes independientes de San Juan.
  COMUNIDAD  : Programa Neuromentia (poblacional, ≥40)
  CLINICA    : Instituto de Neurociencias, dataset basado en TOTAL del ACE-III (07_build)

Especificacion (identica en ambas):  ACE_total ~ f(educacion) + Edad + Sexo,  HC3.
  f = lineal | cuadratica | spline cubico natural (4 gl)
Comparacion por AIC y razon de verosimilitud.

Mejora sobre el abstract vigente: en vez de pendientes por tramos arbitrarios (cuyos rotulos no
coincidian con los cortes usados), se reporta la PENDIENTE MARGINAL dY/dEdu a valores fijos de
educacion, con IC95% por metodo delta sobre la matriz HC3. Los tramos se conservan solo como
sensibilidad y se testean AMBAS definiciones de corte.

Salida: consola + out/07_educacion_2cohortes.json
"""
import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from patsy import dmatrix
from scipy import stats

warnings.filterwarnings("ignore")

BASE = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
ANA = BASE / "analisis"
OUTD = Path(__file__).resolve().parent / "out"
OUTD.mkdir(exist_ok=True)

ITEMS = ['ACE_AtOT','ACE_AtOE','ACE_AtRegistro','ACE_AtSubstr',
         'ACE_MRecuerdo','ACE_MAnterogr','ACE_MRetrogr','ACE_MRecuerdoNyD','ACE_MReconocNyD',
         'ACE_FluVerbFPC','ACE_FluVerbSPC',
         'ACE_LComprensionLyH','ACE_LEscrit','ACE_LRepP','ACE_LRepProverb','ACE_LDenom',
         'ACE_LCompDibujo','ACE_LLectura',
         'ACE_HabVisoDiagrama','ACE_HabVisoCubo','ACE_HabPerPuntos','ACE_HabPerLetras',
         'ACE_HabVisoReloj']
R = {}


def load_comunidad():
    com = pd.read_excel(BASE / "Mix neuromentias.xlsx",
                        sheet_name="Base mixta 23+24 (valores)", header=4, dtype=object)
    com = com.dropna(axis=1, how="all").dropna(axis=0, how="all").reset_index(drop=True)
    com = com[pd.to_numeric(com.Edad, errors="coerce") >= 40].reset_index(drop=True)
    X = pd.DataFrame({c: pd.to_numeric(com[c], errors="coerce") for c in ITEMS})
    X["ACE_LLectura"] = X["ACE_LLectura"].clip(upper=1)
    cc = X.notna().all(axis=1).values
    d = pd.DataFrame({
        "ACE_total": X[cc].sum(axis=1).values,
        "Edad": pd.to_numeric(com["Edad"], errors="coerce")[cc].values,
        "edu": pd.to_numeric(com["ed_anos_completos"], errors="coerce").mask(lambda s: s > 30)[cc].values,
        "Sexo": com["Sexo"].astype(str)[cc].values})
    return d.dropna().reset_index(drop=True)


def load_clinica():
    c = pd.read_csv(ANA / "ace_total_clinico_baseline.csv")
    d = pd.DataFrame({"ACE_total": pd.to_numeric(c.ACE_total, errors="coerce"),
                      "Edad": pd.to_numeric(c.Edad, errors="coerce"),
                      "edu": pd.to_numeric(c.ed_anos_completos, errors="coerce").mask(lambda s: s > 30),
                      "Sexo": c.Sexo.astype(str)})
    return d.dropna().reset_index(drop=True)


def lrt(m0, m1):
    chi2 = 2 * (m1.llf - m0.llf); df = int(m1.df_model - m0.df_model)
    return {"chi2": round(float(chi2), 2), "df": df, "p": float(stats.chi2.sf(chi2, df))}


def analiza(d, label, marg_at=(3, 7, 12, 17)):
    out = {"n": int(len(d))}
    lin = smf.ols("ACE_total ~ edu + Edad + C(Sexo)", data=d).fit()
    qua = smf.ols("ACE_total ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit()
    sp = dmatrix("cr(edu, df=4) - 1", d, return_type="dataframe")
    sp.columns = [f"sp{i}" for i in range(sp.shape[1])]
    dsp = pd.concat([d.reset_index(drop=True), sp.reset_index(drop=True)], axis=1)
    spl = smf.ols("ACE_total ~ " + " + ".join(sp.columns) + " + Edad + C(Sexo)", data=dsp).fit()
    out["AIC"] = {"lineal": round(lin.aic, 1), "cuadratica": round(qua.aic, 1), "spline": round(spl.aic, 1)}
    out["LRT"] = {"cuad_vs_lin": lrt(lin, qua), "spline_vs_lin": lrt(lin, spl),
                  "spline_vs_cuad": lrt(qua, spl)}

    ml = smf.ols("ACE_total ~ edu + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    ci = ml.conf_int().loc["edu"]
    out["pendiente_lineal_unica"] = {"b": round(float(ml.params["edu"]), 3),
                                     "ic95": [round(float(ci[0]), 3), round(float(ci[1]), 3)]}

    # --- pendiente marginal dY/dEdu = b1 + 2*b2*edu, IC95% por metodo delta (HC3)
    mq = smf.ols("ACE_total ~ edu + I(edu**2) + Edad + C(Sexo)", data=d).fit(cov_type="HC3")
    names = list(mq.params.index); i1, i2 = names.index("edu"), names.index("I(edu ** 2)")
    V = np.asarray(mq.cov_params()); b1, b2 = mq.params.iloc[i1], mq.params.iloc[i2]
    out["curvatura_b2"] = {"b2": round(float(b2), 4),
                           "ic95": [round(float(mq.conf_int().iloc[i2, 0]), 4),
                                    round(float(mq.conf_int().iloc[i2, 1]), 4)],
                           "p": float(mq.pvalues.iloc[i2])}
    out["pendiente_marginal"] = {}
    for e in marg_at:
        g = np.zeros(len(names)); g[i1] = 1.0; g[i2] = 2.0 * e
        est = float(b1 + 2 * b2 * e); se = float(np.sqrt(g @ V @ g))
        out["pendiente_marginal"][f"edu={e}"] = {
            "b": round(est, 3), "ic95": [round(est - 1.96 * se, 3), round(est + 1.96 * se, 3)],
            "n_cerca_+-2a": int(((d.edu >= e - 2) & (d.edu <= e + 2)).sum())}

    # --- tramos, ambas definiciones de corte (sensibilidad / auditoria del abstract)
    defs = {"A_<7_7a12_>12": [("<7", d.edu < 7), ("7-12", (d.edu >= 7) & (d.edu <= 12)), (">12", d.edu > 12)],
            "B_<7_7a11_>=12": [("<7", d.edu < 7), ("7-11", (d.edu >= 7) & (d.edu <= 11)), (">=12", d.edu >= 12)]}
    out["tramos"] = {}
    for k, bandas in defs.items():
        out["tramos"][k] = {}
        for name, mask in bandas:
            sub = d[mask]; rec = {"n": int(len(sub))}
            if len(sub) >= 25 and sub.edu.nunique() >= 3:
                mm = smf.ols("ACE_total ~ edu + Edad + C(Sexo)", data=sub).fit(cov_type="HC3")
                cc_ = mm.conf_int().loc["edu"]
                rec.update({"b": round(float(mm.params["edu"]), 3),
                            "ic95": [round(float(cc_[0]), 3), round(float(cc_[1]), 3)]})
            else:
                rec.update({"b": None, "ic95": None, "nota": "n insuficiente"})
            out["tramos"][k][name] = rec

    out["descriptivos"] = {
        "ACE": [round(float(d.ACE_total.mean()), 2), round(float(d.ACE_total.std()), 2),
                float(d.ACE_total.min()), float(d.ACE_total.max())],
        "pct_ACE_ge95": round(100 * float((d.ACE_total >= 95).mean()), 2),
        "pct_ACE_le40": round(100 * float((d.ACE_total <= 40).mean()), 2),
        "pct_ACE_lt86_Bruno": round(100 * float((d.ACE_total < 86).mean()), 1),
        "edad": [round(float(d.Edad.mean()), 1), round(float(d.Edad.std()), 1),
                 float(d.Edad.min()), float(d.Edad.max())],
        "edu": [round(float(d.edu.mean()), 2), round(float(d.edu.std()), 2), float(d.edu.median())],
        "pct_mujeres": round(100 * float((d.Sexo == "Mujer").mean()), 1)}

    print(f"\n{'='*80}\n{label}   n={out['n']}")
    a = out["AIC"]; print(f"  AIC lin {a['lineal']} | cuad {a['cuadratica']} | spline {a['spline']}"
                          f"   ->  mejor: {min(a, key=a.get)}")
    print(f"  LRT cuad vs lin chi2={out['LRT']['cuad_vs_lin']['chi2']} p={out['LRT']['cuad_vs_lin']['p']:.2e}"
          f" | spline vs cuad chi2={out['LRT']['spline_vs_cuad']['chi2']} p={out['LRT']['spline_vs_cuad']['p']:.3f}")
    print(f"  curvatura b2 = {out['curvatura_b2']['b2']} {out['curvatura_b2']['ic95']} p={out['curvatura_b2']['p']:.2e}")
    print(f"  pendiente lineal unica {out['pendiente_lineal_unica']['b']} {out['pendiente_lineal_unica']['ic95']}")
    print("  pendiente marginal (puntos ACE-III por año):")
    for k, v in out["pendiente_marginal"].items():
        print(f"     {k:<8} {v['b']:>6}  IC95 {v['ic95']}   (n±2a={v['n_cerca_+-2a']})")
    for k in defs:
        s = "  ".join(f"{n}: b={r['b']} (n={r['n']})" for n, r in out["tramos"][k].items())
        print(f"  tramos {k}: {s}")
    dd = out["descriptivos"]
    print(f"  ACE {dd['ACE'][0]}±{dd['ACE'][1]} [{dd['ACE'][2]},{dd['ACE'][3]}] | ≥95 {dd['pct_ACE_ge95']}% "
          f"| ≤40 {dd['pct_ACE_le40']}% | <86(Bruno) {dd['pct_ACE_lt86_Bruno']}%")
    print(f"  edad {dd['edad'][0]}±{dd['edad'][1]} | edu {dd['edu'][0]}±{dd['edu'][1]} (mdn {dd['edu'][2]}) "
          f"| mujeres {dd['pct_mujeres']}%")
    return out


com, cli = load_comunidad(), load_clinica()
R["comunidad"] = analiza(com, "COMUNIDAD — Neuromentia (poblacional)")
R["clinica"] = analiza(cli, "CLINICA — Inst. Neurociencias (total ACE-III, derivados)")

# ---------- soporte comun
lo_e, hi_e = max(com.Edad.min(), cli.Edad.min()), min(com.Edad.max(), cli.Edad.max())
lo_u, hi_u = max(com.edu.min(), cli.edu.min()), min(com.edu.max(), cli.edu.max())
coms = com[com.Edad.between(lo_e, hi_e) & com.edu.between(lo_u, hi_u)]
clis = cli[cli.Edad.between(lo_e, hi_e) & cli.edu.between(lo_u, hi_u)]
R["soporte_comun"] = {"edad": [float(lo_e), float(hi_e)], "edu": [float(lo_u), float(hi_u)],
                      "n_com": int(len(coms)), "n_cli": int(len(clis))}
print(f"\n>>> soporte comun: edad [{lo_e},{hi_e}] educacion [{lo_u},{hi_u}] "
      f"-> comunidad {len(coms)}, clinica {len(clis)}")
R["comunidad_soporte"] = analiza(coms, "COMUNIDAD — soporte comun")
R["clinica_soporte"] = analiza(clis, "CLINICA — soporte comun")

# ---------- heterogeneidad de la forma funcional entre settings
pool = pd.concat([coms.assign(setting="comunidad"), clis.assign(setting="clinica")], ignore_index=True)
m0 = smf.ols("ACE_total ~ edu + I(edu**2) + Edad + C(Sexo) + C(setting)", data=pool).fit()
m1 = smf.ols("ACE_total ~ (edu + I(edu**2))*C(setting) + Edad + C(Sexo)", data=pool).fit()
m2 = smf.ols("ACE_total ~ edu*C(setting) + I(edu**2) + Edad + C(Sexo)", data=pool).fit()
R["heterogeneidad"] = {
    "n_pool": int(len(pool)),
    "forma_completa_vs_comun": lrt(m0, m1),
    "solo_pendiente_lineal": lrt(m0, m2),
    "solo_curvatura_(m1_vs_m2)": lrt(m2, m1),
    "nota": "Test de heterogeneidad de la forma funcional entre cohortes; NO es una muestra combinada."}
print(f"\n>>> Heterogeneidad forma x setting (n={len(pool)}): "
      f"chi2={R['heterogeneidad']['forma_completa_vs_comun']['chi2']} "
      f"p={R['heterogeneidad']['forma_completa_vs_comun']['p']:.2e} | "
      f"curvatura difiere: chi2={R['heterogeneidad']['solo_curvatura_(m1_vs_m2)']['chi2']} "
      f"p={R['heterogeneidad']['solo_curvatura_(m1_vs_m2)']['p']:.3f}")

# ---------- sensibilidad: colapsar 11 y 12 (mismo nivel 'secundario completo' segun plan)
cli_c = cli.copy(); cli_c["edu"] = cli_c.edu.replace({11: 12})
com_c = com.copy(); com_c["edu"] = com_c.edu.replace({11: 12})
R["sens_11a12_clinica"] = analiza(cli_c, "CLINICA — sensibilidad: 11 años recodificado a 12")
R["sens_11a12_comunidad"] = analiza(com_c, "COMUNIDAD — sensibilidad: 11 años recodificado a 12")

# ---------- soporte por tramo (cuanto n aporta cada cohorte donde importa)
R["soporte_por_tramo"] = {
    "comunidad": {"<7": int((com.edu < 7).sum()), "7-10": int(((com.edu >= 7) & (com.edu <= 10)).sum()),
                  "11-12": int(((com.edu >= 11) & (com.edu <= 12)).sum()), ">12": int((com.edu > 12).sum())},
    "clinica": {"<7": int((cli.edu < 7).sum()), "7-10": int(((cli.edu >= 7) & (cli.edu <= 10)).sum()),
                "11-12": int(((cli.edu >= 11) & (cli.edu <= 12)).sum()), ">12": int((cli.edu > 12).sum())}}
print("\n>>> soporte por tramo:", json.dumps(R["soporte_por_tramo"], ensure_ascii=False))

(OUTD / "07_educacion_2cohortes.json").write_text(json.dumps(R, indent=2, ensure_ascii=False))
print(f"\n-> {OUTD/'07_educacion_2cohortes.json'}")
