# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

# ── Criterio de control del estudio (peldaño 4 de la escalera de V22) ──────────
# Cuatro criterios, tres dominios, y el mejor perfil de neutralidad educativa de todas las
# combinaciones evaluadas (chi2 p = 0,504):
#   · cognitivo   memoria de reconocimiento de lista >= 10
#   · medico      sin antecedente de accidente cerebrovascular
#   · medico      sin antecedente de traumatismo de craneo
#   · funcional   independiente en las actividades basicas del ADLQ
# El codigo 9 del ADLQ significa «nunca lo hizo» y no cuenta como dependencia.
ADLQ_BASICAS = ["ADLQ_Alimentarse_(A)", "ADLQ_Vestido_(A)", "ADLQ_Baño_(A)", "ADLQ_Evacuación_(A)"]


def es_control(c40):
    """Devuelve la mascara del criterio de control sobre el marco crudo de la cohorte comunitaria."""
    n = lambda c: pd.to_numeric(c40[c], errors="coerce")
    M = pd.DataFrame({c: n(c) for c in ADLQ_BASICAS}).replace(9, np.nan)
    abvd = (M.fillna(0) == 0).all(axis=1) & (M.notna().sum(axis=1) >= len(ADLQ_BASICAS) - 1)
    return ((n("LDR_Reconocimiento_A") >= 10) & (n("APN_ACV") == 0)
            & (n("APN_LesionesCabeza") == 0) & abvd)

