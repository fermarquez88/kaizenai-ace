#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V5 — CONSISTENCIA.

  A. Se consolida UNA sola fuente de verdad numérica: resultados/CIFRAS_MAESTRAS.json.
     Toda cifra del manuscrito debe salir de ahí y de ningún otro lado.
  B. Se barren los entregables existentes buscando cifras que ya no correspondan.

Salida: resultados/CIFRAS_MAESTRAS.json + resultados/V5_consistencia.json
"""
import json, re
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUT = EST / "resultados"
L = lambda n: json.loads((OUT / n).read_text())

v2, v2b, v3, v3b = L("V2_reproduccion.json"), L("V2b_testretest.json"), L("V3_supuestos.json"), L("V3b_addendum.json")
v4, v4b, v4c = L("V4_tri.json"), L("V4b_dif_ordinal.json"), L("V4c_dtf.json")
tri = L("V2b_testretest_por_intervalo.json")
v26, v26b = L("V26_dispersion_latente.json"), L("V26b_mecanismo.json")

d = {r["cohorte"]: r for r in v2["descriptivos"]}
M = {
    "_fuente": "Bloques V1–V4, ejecutados 2026-07-31 sobre los datos corregidos en V1b.",
    "_regla": "Ninguna cifra del manuscrito puede provenir de otro archivo que éste.",

    "n": {"comunitaria": 758, "clinica": 2112, "total": 2870,
          "con_items_completos": {"comunitaria": v4["n"]["comunitaria"], "clinica": v4["n"]["clinica"],
                                  "combinada": v4["n"]["combinada"]},
          "flujo_comunitaria": {"crudo": 867, "edad_ge40": 866, "items_completos": 814,
                                "educacion_valida": 776, "menos_solapamiento": 758},
          "excluidos_comunitaria": {"total": 90, "sin_items": 52, "sin_educacion": 43, "recuperables": 0},
          "solapamiento_excluido": 18},

    "descriptivos": {k: {"n": int(v["n"]), "mujeres_pct": v["mujeres_pct"],
                         "edad_mediana": v["edad_med"], "edad_q1": v["edad_q1"], "edad_q3": v["edad_q3"],
                         "edu_mediana": v["edu_med"], "edu_q1": v["edu_q1"], "edu_q3": v["edu_q3"],
                         "n_lt7": int(v["n_lt7"]), "n_7a11": int(v["n_7a11"]), "n_ge12": int(v["n_ge12"]),
                         "ACE_media": v["ACE_media"], "ACE_de": v["ACE_de"]}
                     for k, v in d.items()},

    "principal_escalon": {
        "comunitaria": v2["falsacion"]["comunitaria"], "clinica": v2["falsacion"]["clínica"],
        "sobre_theta": {"comunitaria": {"b": v4["curvatura_latente"]["comunitaria"]["θ latente"]["escalon"],
                                        "ic95": v4["curvatura_latente"]["comunitaria"]["θ latente"]["escalon_ic95"],
                                        "p": v4["curvatura_latente"]["comunitaria"]["θ latente"]["escalon_p"]},
                        "clinica": {"b": v4["curvatura_latente"]["clínica"]["θ latente"]["escalon"],
                                    "ic95": v4["curvatura_latente"]["clínica"]["θ latente"]["escalon_ic95"],
                                    "p": v4["curvatura_latente"]["clínica"]["θ latente"]["escalon_p"]}},
        "rd_local": v2["rd_local"], "crudo_11_vs_12": v2["crudo"],
        "equivalencia": {k: v3["potencia"][k]["TOST"] for k in v3["potencia"]},
        "mde_80pct": {k: v3["potencia"][k]["mde_80"] for k in v3["potencia"]},
        "placebo": {"comunitaria_puesto12": v3["placebo"]["comunitaria_rank12"],
                    "clinica_puesto12": v3["placebo"]["clínica_rank12"]}},

    "forma": {
        "bruto": {"comunitaria": v2["forma"]["comunitaria"]["b2"], "clinica": v2["forma"]["clínica"]["b2"]},
        "theta": {"comunitaria": {k: v4["curvatura_latente"]["comunitaria"]["θ latente"][k]
                                  for k in ("b2", "ic95", "p", "b2_estandarizado", "p_cuad_vs_lin")},
                  "clinica": {k: v4["curvatura_latente"]["clínica"]["θ latente"][k]
                              for k in ("b2", "ic95", "p", "b2_estandarizado", "p_cuad_vs_lin")}},
        "marginal_bruto": {"comunitaria": v2["forma"]["comunitaria"]["marginal"],
                           "clinica": v2["forma"]["clínica"]["marginal"]},
        "marginal_theta": {"comunitaria": v4["curvatura_latente"]["comunitaria"]["marginal_theta"],
                           "clinica": v4["curvatura_latente"]["clínica"]["marginal_theta"]},
        "replicacion": v2.get("replicacion", {}),
        "spline_vs_cuadratico": {"comunitaria": v2["forma"]["comunitaria"]["spline_vs_cuad"]["p"],
                                 "clinica": v2["forma"]["clínica"]["spline_vs_cuad"]["p"]}},

    "positividad": v2.get("positividad", {}),

    "psicometria": {
        "grm_a_mediana": v4["grm"]["a_mediana"], "grm_a_rango": v4["grm"]["a_rango"],
        "theta_r_con_bruto": v4["theta"]["r_con_bruto"],
        "dif_educacion": {"metodo": v4b["metodo"], "n_focal": v4b["n_focal"],
                          "items_no_triviales": v4b["n_no_trivial"],
                          "items_significativos_efecto_despreciable": 9,
                          "mayor_dR2": max(v["dR2"] for v in v4b["items"].values())},
        "dtf_total": {"comunitaria": v4c["comunitaria"], "clinica": v4c["clínica"]},
        "invarianza_cohorte_items_moderados": v4["invarianza_cohorte"]["n_no_trivial"]},

    "test_retest": {"n_pares": v2b["n_pares"], "n_personas": v2b["n_personas"],
                    "icc": 0.727, "r": 0.774,
                    "eem_extrapolado": v2b["sem"], "eem_ic95": v2b["sem_ic95"],
                    "eem_por_intervalo": {k: v["sem"] for k, v in tri.items()},
                    "eem_rango_declarable": [6.2, 8.4],
                    "escalon_en_eem": v2b["escalon_en_eem"],
                    "cmd95": v2b["cmd95"], "fiabilidad": v2b["fiabilidad"]},

    "robustez": {"cook_max": {k: v["cook_max"] for k, v in v3["influyentes"].items()},
                 "b2_sin_1pct": {k: v["b2_sin_1pct"] for k, v in v3["influyentes"].items()},
                 "especificaciones_covariables": v3["covar_alt"],
                 "desenlace_alternativo": v3["desenlace_alt"],
                 "ipw": v3b.get("ipw", {}),
                 "breusch_pagan_p": 2.22e-14},

    "faltantes": v3["faltantes"],
    "regla_vigente": {"corte_alto": 86, "corte_bajo": 68, "escalon_puntos": 18, "umbral_anios": 12},

    # ── dispersión (V26 corregido 2026-08-09 / V26b) ─────────────────────────────────────
    # El modelo de posición y el de log-varianza se estiman por MCO, igual que en V13 y que en los
    # coeficientes publicados de la calculadora; con HC3 la pendiente es idéntica y el valor p pasa
    # de 8,6×10⁻⁴ a 7,3×10⁻⁴. La desatenuación escalar del EAP se retiró: tenía el signo invertido
    # y, con cualquier signo, no es el estimador correcto. La sustituye el GRM multigrupo.
    "dispersion": {
        "controles": {"n": v26["n"]["controles"], "por_tramo": v26["n"]["controles_por_tramo"]},
        "bruto": {"pendiente_log_var": v26["dispersion"]["ACE bruto"]["pendiente_log_var_por_anio"],
                  "ic95": v26["dispersion"]["ACE bruto"]["ic95"],
                  "p_MCO": v26["dispersion"]["ACE bruto"]["p"],
                  "sigma_edu0": v26["dispersion"]["ACE bruto"]["sigma_edu0"],
                  "sigma_edu20": v26["dispersion"]["ACE bruto"]["sigma_edu20"],
                  "de_por_tramo": v26["dispersion"]["ACE bruto"]["de_por_tramo"],
                  "levene_W": v26["dispersion"]["ACE bruto"]["levene_W"],
                  "levene_p": v26["dispersion"]["ACE bruto"]["levene_p"]},
        "theta_eap": {"pendiente_log_var": v26["dispersion"]["θ latente"]["pendiente_log_var_por_anio"],
                      "ic95": v26["dispersion"]["θ latente"]["ic95"],
                      "p": v26["dispersion"]["θ latente"]["p"],
                      "de_por_tramo": v26["dispersion"]["θ latente"]["de_por_tramo"],
                      "levene_W": v26["dispersion"]["θ latente"]["levene_W"],
                      "levene_p": v26["dispersion"]["θ latente"]["levene_p"],
                      "_nota": ("la pendiente lineal es nula pero el Levene RECHAZA la homogeneidad: "
                                "el patrón no es monótono, no está ausente")},
        "habilidad_multigrupo": v26["multigrupo"],
        "razon_extremos": v26["razon_extremos"],
        "dos_metricas": v26["dos_metricas"],
        "forma_theta": v26b["forma_theta"], "pares_theta": v26b["pares_theta"],
        "percentil_del_corte": v26b["percentil_corte"],
        "_no_identificado": ("Qué parte del estrechamiento corresponde a la escala y qué parte a las "
                             "personas NO está identificado: depende de la métrica privilegiada. "
                             "Ver dos_metricas."),
    },
}
(OUT / "CIFRAS_MAESTRAS.json").write_text(json.dumps(M, indent=2, ensure_ascii=False))
print(f"-> resultados/CIFRAS_MAESTRAS.json  ({len(json.dumps(M))} caracteres)")

# ---------------------------------------------------------------- B. barrido de entregables
OBSOLETAS = {
    "776": "n comunitario previo a excluir el solapamiento (ahora 758)",
    "762": "n comunitario intermedio (ahora 758)",
    "2137": "n clínico de una versión anterior del dataset (ahora 2112/2242)",
    "0,0835": "curvatura comunitaria previa (ahora −0,0784)",
    "-0.0835": "curvatura comunitaria previa (ahora −0,0784)",
    "+0,55": "escalón comunitario previo (ahora +0,04)",
    "17 individuos": "solapamiento previo (ahora 18)",
}
print("\nBARRIDO DE ENTREGABLES — cifras que ya no corresponden")
hall = []
raices = [EST / "entregable_can", NM / "posters_CAN2026/plataforma/12b_educacion_2cohortes",
          NM / "posters_CAN2026/plataforma/A2_irt_dif"]
for raiz in raices:
    if not raiz.exists():
        continue
    for f in sorted(raiz.rglob("*.md")):
        txt = f.read_text(errors="ignore")
        for pat, motivo in OBSOLETAS.items():
            for m in re.finditer(re.escape(pat), txt):
                ln = txt[:m.start()].count("\n") + 1
                hall.append({"archivo": str(f.relative_to(f.parents[3])), "linea": ln,
                             "patron": pat, "motivo": motivo})
if hall:
    for h in hall:
        print(f"  {h['archivo']}:{h['linea']}  «{h['patron']}» -> {h['motivo']}")
else:
    print("  (sin coincidencias)")
print(f"\ntotal de cifras obsoletas detectadas: {len(hall)}")
(OUT / "V5_consistencia.json").write_text(json.dumps(
    {"obsoletas": hall, "n": len(hall)}, indent=2, ensure_ascii=False))
print(f"-> resultados/V5_consistencia.json")
