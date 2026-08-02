#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V20 — Auditoría del ADLQ subescala por subescala, y definición final del grupo control.

El manuscrito afirma que las subescalas de empleo, comunicación y tecnología del ADLQ tienen gradiente
educativo, y por eso descarta el criterio funcional. Nunca lo mostró subescala por subescala. Este
bloque lo hace, y evalúa si alguna parte del ADLQ puede incorporarse sin introducir dependencia de la
exposición.

Puntuación del ADLQ: 0 = sin cambio · 1 a 3 = deterioro creciente · 9 = nunca lo hizo. El 9 es
decisivo: en computadora, cajero o correo electrónico, «nunca lo hizo» es cohorte y escolaridad, no
declive. Tratarlo como incumplimiento fabricaría exactamente el sesgo que se busca evitar, de modo que
se cuenta como «sin declive observable».

Luego reejecuta la comparación entre reglas con las definiciones candidatas, para responder qué le
pasa al gradiente de 44 puntos porcentuales cuando el grupo control se define mejor.

Salida: resultados/V20_adlq_definicion_final.json
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.model_selection import KFold
import duckdb

warnings.filterwarnings("ignore")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
IN = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
TR = lambda e: pd.cut(e, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
BANDAS = ["<7", "7-11", "≥12"]
SESGO_LOGCHI2 = 1.2703628454614782
FP = "ACE ~ edu + I(edu**2) + Edad + C(Sexo)"
RES = {}

craw = pd.read_excel(NM / "Mix neuromentias.xlsx", sheet_name="Base mixta 23+24 (valores)",
                     header=4, dtype=object).dropna(axis=1, how="all")
craw = craw[pd.to_numeric(craw.Edad, errors="coerce") >= 40].reset_index(drop=True)
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
craw["doc"] = nd(craw["dni"])
num = lambda c: pd.to_numeric(craw[c], errors="coerce")

SUB = {
    "A · autocuidado básico": ["Alimentarse_(A)", "Vestido_(A)", "Baño_(A)", "Evacuación_(A)",
                               "Medicación_(A)", "InterésAspectoPersonal_(A)"],
    "B · tareas del hogar":   ["PreparaciónComidas_(B)", "PonerMesa_(B)", "CuidadosHogar_(B)",
                               "MantenimientoHogar_(B)", "ArreglosHogar_(B)", "LavadoRopa_(B)"],
    "C · empleo y vida social": ["Empleo_(C)", "Recreación_(C)", "Reuniones_(C)", "Viaje_(C)"],
    "D · compras y dinero":   ["ComprarComida_(D)", "ManejoEfectivo_(D)", "ManejoFinanzas_(D)"],
    "E · desplazamiento":     ["TransportePúblico_(E)", "Conducir_(E)", "MovilidadBarrio_(E)",
                               "ViajarFueraAmbienteFamiliar_(E)"],
    "F · comunicación":       ["UsoTeléfono_(F)", "Conversación_(F)", "Comprensión_(F)",
                               "Lectura_(F)", "Escritura_(F)"],
    "G · tecnología":         ["UsoDelComputador_(G)", "TelefonoCelular_(G)", "CajeroAutomático_(G)",
                               "AccesoAInternet_(G)", "CorreoElectrónico_(G)", "RedesSociales_(G)"],
}

def sin_declive(items):
    """Cumple si ningún ítem muestra declive. El 9 («nunca lo hizo») no es declive."""
    M = pd.DataFrame({i: num("ADLQ_" + i) for i in items})
    decl = ((M > 0) & (M != 9)).any(axis=1)
    hay = M.notna().any(axis=1)
    return (~decl).astype(float).where(hay)

base = pd.DataFrame({"doc": craw["doc"], "rec": num("LDR_Reconocimiento_A"),
                     "acv": num("APN_ACV")})
for nom, items in SUB.items():
    base[nom] = sin_declive(items).values
com = pd.read_csv(EST / "datos/comunitaria_armonizada.csv")
D = com.merge(base, left_on="dni", right_on="doc", how="left").dropna(subset=["ACE", "edu", "Edad", "Sexo"])
D["tr"] = TR(D.edu)
D["sin_acv"] = (D.acv == 0).astype(float).where(D.acv.notna())
print(f"cohorte comunitaria: {len(D)}\n")

# ─────────────────────────────────────────── A · cada subescala frente a la escolaridad
print("A. INDEPENDENCIA FUNCIONAL POR SUBESCALA, SEGÚN ESCOLARIDAD")
print(f"{'subescala':<26}{'cumple':>8}{'<7':>8}{'7-11':>8}{'≥12':>8}{'p':>9}{'r con edu':>11}  veredicto")
RES["subescalas"] = {}
for nom in SUB:
    v = D[nom]
    sub = D[v.notna()]
    pct = {t: 100*sub[sub.tr == t][nom].mean() for t in BANDAS}
    tab = pd.crosstab(sub.tr, sub[nom] == 1)
    p = stats.chi2_contingency(tab)[1] if tab.shape == (3, 2) else np.nan
    r = stats.spearmanr(sub.edu, sub[nom])[0]
    ok = p >= 0.05
    print(f"{nom:<26}{100*v.mean():>7.0f}%{pct['<7']:>7.0f}%{pct['7-11']:>7.0f}%{pct['≥12']:>7.0f}%"
          f"{p:>9.3f}{r:>11.3f}  {'neutral' if ok else 'GRADIENTE EDUCATIVO'}")
    RES["subescalas"][nom] = {"cumple_pct": round(100*float(v.mean()), 1),
                              "por_tramo": {t: round(pct[t], 1) for t in BANDAS},
                              "p_edu": round(float(p), 4), "r_edu": round(float(r), 3),
                              "neutral": bool(ok)}
NEUTRAS = [n for n in SUB if RES["subescalas"][n]["neutral"]]
print(f"\nsubescalas neutrales: {NEUTRAS or 'ninguna'}")

# ─────────────────────────────────────────── B · definiciones candidatas
def crit(D, cs):
    m = D[cs].notna().all(axis=1)
    return m & (D[cs] == 1).all(axis=1)

CAND = {
    "vigente":                       ["rec10"],
    "vigente + sin ACV":             ["rec10", "sin_acv"],
    "vigente + sin ACV + ADLQ básico": ["rec10", "sin_acv", "A · autocuidado básico"],
    "vigente + sin ACV + ADLQ neutro": ["rec10", "sin_acv"] + NEUTRAS,
    "vigente + ADLQ total":          ["rec10"] + list(SUB),
}
D["rec10"] = (D.rec >= 10).astype(float).where(D.rec.notna())
print("\n\nB. DEFINICIONES CANDIDATAS SOBRE LA COHORTE COMUNITARIA")
print(f"{'definición':<34}{'n':>6}{'<7':>6}{'7-11':>7}{'≥12':>6}{'p edu':>9}{'ACE <7':>9}")
RES["candidatas"] = {}
for nom, cs in CAND.items():
    cs = [c for c in cs if c in D.columns]
    ok = crit(D, cs)
    G = D[ok]
    ev = D[D[cs].notna().all(axis=1)]
    tab = pd.crosstab(ev.tr, (ev[cs] == 1).all(axis=1))
    p = stats.chi2_contingency(tab)[1] if tab.shape == (3, 2) else np.nan
    n_t = {t: int((G.tr == t).sum()) for t in BANDAS}
    print(f"{nom:<34}{len(G):>6}{n_t['<7']:>6}{n_t['7-11']:>7}{n_t['≥12']:>6}{p:>9.3f}"
          f"{G[G.tr=='<7'].ACE.mean():>9.1f}")
    RES["candidatas"][nom] = {"criterios": cs, "n": len(G), "n_por_tramo": n_t,
                              "p_edu": round(float(p), 4),
                              "ACE_medio_lt7": round(float(G[G.tr == "<7"].ACE.mean()), 1)}

# ─────────────────────────────────────────── C · efecto sobre el resultado principal
print("\n\nC. QUÉ LE PASA AL GRADIENTE DE LA REGLA VIGENTE CON CADA DEFINICIÓN")
con = duckdb.connect(str(IN / "db/evaluaciones_v2.duckdb"), read_only=True)
cl = con.execute("select eval_id, bruto rec from resultados_v2 "
                 "where test='Lista de Rey' and subtest like 'Reconoc%'").fetchdf()
cl["rec"] = pd.to_numeric(cl.rec, errors="coerce")
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv").merge(
    cl.dropna(subset=["rec"]).drop_duplicates("eval_id"), on="eval_id", how="left")
cas_all = dx3[dx3.dx3 == "Demencia"][["ACE", "edu", "Edad", "Sexo"]].assign(y=1)

def evalua(ctl_idx):
    ctl = D.loc[ctl_idx, ["ACE", "edu", "Edad", "Sexo"]].assign(y=0)
    E = pd.concat([ctl, cas_all], ignore_index=True).dropna(subset=["ACE", "edu", "Edad", "Sexo"])
    lo = max(E[E.y == 1].Edad.min(), E[E.y == 0].Edad.min())
    hi = min(E[E.y == 1].Edad.max(), E[E.y == 0].Edad.max())
    E = E[E.Edad.between(lo, hi)].copy()
    E["b"] = pd.cut(E.Edad, np.arange(np.floor(lo/5)*5, hi + 6, 5))
    P = [pd.concat([g[g.y == 1].sample(k, random_state=1), g[g.y == 0].sample(k, random_state=1)])
         for _, g in E.groupby("b", observed=True)
         if (k := min((g.y == 1).sum(), (g.y == 0).sum())) > 0]
    if not P: return None
    E = pd.concat(P, ignore_index=True); E["tr"] = TR(E.edu)
    # regla vigente
    sen = E.ACE < np.where(E.edu >= 12, 86, 68)
    fp = {t: 100*sen[(E.y == 0) & (E.tr == t)].mean() for t in BANDAS}
    yv = sen[E.y == 1].mean() + 1 - sen[E.y == 0].mean() - 1
    # corrección continua, calibrada a la misma positividad
    REF = E[E.y == 0].reset_index(drop=True)
    def norma(t_, a_):
        mu = smf.ols(FP, data=t_).fit()
        t2 = t_.assign(lr2=np.log(np.clip(mu.resid**2, 1e-6, None)))
        sd = smf.ols("lr2 ~ edu + Edad", data=t2).fit()
        return (a_.ACE - mu.predict(a_)) / np.sqrt(np.exp(SESGO_LOGCHI2 + sd.predict(a_)))
    z = pd.Series(index=E.index, dtype=float)
    fold = np.zeros(len(REF), int)
    for k, (_, te) in enumerate(KFold(10, shuffle=True, random_state=1).split(REF)): fold[te] = k
    rp = E.index[E.y == 0].values
    for k in range(10):
        o = E.loc[rp[fold == k]]; z.loc[o.index] = norma(REF[fold != k], o).values
    cs_ = E.index[E.y == 1]
    z.loc[cs_] = norma(REF, E.loc[cs_]).values
    cc = z < np.quantile(z, sen.mean())
    fpc = {t: 100*cc[(E.y == 0) & (E.tr == t)].mean() for t in BANDAS}
    yc = cc[E.y == 1].mean() + 1 - cc[E.y == 0].mean() - 1
    return {"n_casos": int((E.y == 1).sum()), "n_ctrl": int((E.y == 0).sum()),
            "ctrl_por_tramo": {t: int(((E.y == 0) & (E.tr == t)).sum()) for t in BANDAS},
            "vig_fp": {t: round(fp[t], 1) for t in BANDAS},
            "vig_grad": round(max(fp.values()) - min(fp.values()), 1),
            "vig_youden": round(float(yv), 3),
            "cont_grad": round(max(fpc.values()) - min(fpc.values()), 1),
            "cont_youden": round(float(yc), 3), "d_youden": round(float(yc - yv), 3)}

print(f"{'definición':<34}{'casos':>7}{'ctrl':>6}{'<7':>5}{'señala <7':>11}{'7-11':>8}{'≥12':>8}"
      f"{'gradiente':>11}{'ΔYouden':>10}")
RES["efecto"] = {}
for nom, cs in CAND.items():
    cs = [c for c in cs if c in D.columns]
    r = evalua(D.index[crit(D, cs)])
    if not r: continue
    print(f"{nom:<34}{r['n_casos']:>7}{r['n_ctrl']:>6}{r['ctrl_por_tramo']['<7']:>5}"
          f"{r['vig_fp']['<7']:>10.1f}%{r['vig_fp']['7-11']:>7.1f}%{r['vig_fp']['≥12']:>7.1f}%"
          f"{r['vig_grad']:>11.1f}{r['d_youden']:>+10.3f}")
    RES["efecto"][nom] = r

Path(EST / "resultados/V20_adlq_definicion_final.json").write_text(
    json.dumps(RES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("\n-> resultados/V20_adlq_definicion_final.json")
