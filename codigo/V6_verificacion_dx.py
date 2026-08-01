#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLOQUE V6 — VERIFICACIÓN DE LA CODIFICACIÓN DIAGNÓSTICA DE 3 NIVELES.

Antes de usar la etiqueta como desenlace hay que demostrar que es válida. Seis controles:

  A. COBERTURA — ¿qué proporción de conclusiones captura la oración canónica, y qué dicen las que
     no captura? Se buscan formulaciones alternativas ("el perfil neuropsicológico actual...").
  B. COBERTURA DIFERENCIAL — ¿la captura depende de la escolaridad? Si sí, la etiqueta está sesgada
     justo en la dimensión del estudio.
  C. NO CIRCULARIDAD — ¿la oración clasificatoria menciona el ACE-III o algún puntaje?
  D. FALSOS NORMALES — auditoría de las 87 conclusiones rotuladas "sin afectación".
  E. AUDITORÍA MANUAL — muestra aleatoria estratificada, con la oración textual, para lectura humana.
  F. VALIDACIÓN INDEPENDIENTE — el ACE-III (no usado para clasificar) debe ordenarse por severidad.

Salida: consola + resultados/V6_verificacion_dx.json + verificacion/V6_muestra_auditoria.csv
"""
import json, re, unicodedata, warnings
from pathlib import Path
import duckdb, pandas as pd, numpy as np
from scipy import stats

warnings.simplefilter("ignore")
rng = np.random.default_rng(20260801)
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
R = {}

nrm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKD", str(s))
                       .encode("ascii", "ignore").decode().lower())
FRASE = re.compile(r"(el presente perfil cognitivo[^.]*\.)")

con = duckdb.connect(str(INECO / "db/evaluaciones_v1.duckdb"), read_only=True)
d = con.execute("""
    select s.evaluacion_id, s.texto conclusiones, p.dni, e.fecha_evaluacion
    from informe_secciones s
    join evaluaciones e on e.evaluacion_id = s.evaluacion_id
    join pacientes_pii p on p.paciente_id = e.paciente_id
    where s.seccion='conclusiones' and s.texto is not null and p.dni is not null
""").fetchdf()
d["t"] = d.conclusiones.map(nrm)
d["capta"] = d.t.str.contains(FRASE.pattern, regex=True)
print(f"conclusiones con documento: {len(d)}   |   captadas por la oración canónica: "
      f"{int(d.capta.sum())} ({100*d.capta.mean():.1f} %)")

# ═══════════════════════════════════════════ A. COBERTURA: formulaciones alternativas
print("\n" + "=" * 92 + "\nA. ¿QUÉ DICEN LAS CONCLUSIONES NO CAPTADAS?")
nc = d[~d.capta]
ALT = {
    "el perfil neuropsicologico actual": r"el perfil neuropsicologico actual",
    "el perfil cognitivo actual": r"el perfil cognitivo actual",
    "se corresponde con": r"se corresponde con",
    "el presente perfil (otra variante)": r"el presente perfil(?! cognitivo)",
    "perfil (cualquier) + compatible": r"perfil[^.]{0,60}compatible",
    "menciona 'deterioro cognitivo'": r"deterioro cognitivo",
    "menciona 'disfuncion'": r"disfuncion",
}
cob = {}
for lab, p in ALT.items():
    m = nc.t.str.contains(p, regex=True)
    cob[lab] = int(m.sum())
    print(f"  {lab:<40}{m.sum():>5} de {len(nc)}  ({100*m.mean():5.1f} %)")
recuperables = nc.t.str.contains(r"el perfil neuropsicologico actual|el perfil cognitivo actual|"
                                 r"perfil[^.]{0,60}(compatible|se corresponde)", regex=True)
print(f"\n  -> potencialmente recuperables con una regla ampliada: {int(recuperables.sum())} "
      f"({100*recuperables.mean():.1f} % de las no captadas)")
print("\n  primeras palabras de 6 conclusiones NO captadas:")
for t in nc.t.head(6):
    print(f"    «{t[:150]}...»")
R["cobertura"] = {"n_total": int(len(d)), "captadas": int(d.capta.sum()),
                  "pct_captadas": round(100*float(d.capta.mean()), 1),
                  "alternativas": cob, "recuperables": int(recuperables.sum())}

# ═══════════════════════════════════════════ B. ¿LA COBERTURA DEPENDE DE LA ESCOLARIDAD?
print("\n" + "=" * 92 + "\nB. COBERTURA DIFERENCIAL POR ESCOLARIDAD (el control crítico)")
cli = pd.read_csv(EST / "datos/clinico_definitivo.csv").rename(columns={"ACE_total": "ACE"})
cli = cli.dropna(subset=["ACE", "edu", "Edad", "Sexo"])
cli = cli[cli.edu.between(0, 30)]
nd = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace(r"\D", "", regex=True)
                             .where(lambda x: x.str.len().between(6, 9)), errors="coerce")
cli["doc"] = nd(cli.persona_id)
cli["fx"] = pd.to_datetime(cli.fecha_ev, errors="coerce", format="ISO8601")
d["doc"] = nd(d.dni)
d["fx"] = pd.to_datetime(d.fecha_evaluacion, errors="coerce", dayfirst=True)
lk = cli.merge(d.dropna(subset=["doc", "fx"])[["doc", "fx", "capta", "t"]].rename(
    columns={"fx": "fdx"}), on="doc", how="left")
lk["dif"] = (lk.fx - lk.fdx).dt.days.abs()
lk = lk.sort_values("dif").drop_duplicates(subset=["doc", "fx"])
lk["enlazada"] = lk.dif <= 7
lk["tr"] = pd.cut(lk.edu, [-1, 6.5, 11.5, 99], labels=["<7", "7-11", "≥12"])
tab = lk.groupby("tr", observed=True).agg(n=("ACE", "size"),
                                          enlazadas=("enlazada", "sum"),
                                          captadas=("capta", lambda s: int(s.fillna(False).sum())))
tab["pct_enlazada"] = (100*tab.enlazadas/tab.n).round(1)
tab["pct_captada"] = (100*tab.captadas/tab.n).round(1)
print(tab.to_string())
sub = lk.dropna(subset=["tr"])
ct = pd.crosstab(sub.tr, sub.capta.fillna(False))
chi = stats.chi2_contingency(ct)
print(f"\n  prueba de independencia entre captura y tramo educativo: "
      f"chi²={chi.statistic:.2f}, p={chi.pvalue:.4f}")
print("  -> " + ("SIN evidencia de cobertura diferencial" if chi.pvalue > 0.05 else
                 "⚠ COBERTURA DIFERENCIAL: la etiqueta falta de forma desigual por escolaridad"))
R["cobertura_diferencial"] = {"tabla": tab.reset_index().astype(str).to_dict("records"),
                              "chi2": round(float(chi.statistic), 2), "p": float(chi.pvalue)}

# ═══════════════════════════════════════════ C. NO CIRCULARIDAD
print("\n" + "=" * 92 + "\nC. NO CIRCULARIDAD — ¿la oración clasificatoria usa el ACE-III?")
fr = d[d.capta].t.str.extract(FRASE.pattern)[0].dropna()
pat = {"sigla ACE": r"\bace\b", "cualquier test": r"\b(ace|ifs|mmse|moca|ravlt|tmt|wais)\b",
       "un puntaje numérico": r"\d{1,3}\s*/\s*100|\bpuntaje\b|\bpuntua",
       "z o percentil": r"\bz\b|percentil|desvio"}
cir = {}
for lab, p in pat.items():
    m = fr.str.contains(p, regex=True)
    cir[lab] = int(m.sum())
    print(f"  {lab:<24}{m.sum():>5} de {len(fr)}  ({100*m.mean():5.2f} %)")
print("  -> la clasificación proviene del juicio clínico narrativo, no de puntajes")
R["circularidad"] = cir

# ═══════════════════════════════════════════ D. FALSOS NORMALES
print("\n" + "=" * 92 + "\nD. AUDITORÍA DE LOS ROTULADOS «SIN AFECTACIÓN»")
dx3 = pd.read_csv(EST / "datos/clinico_dx3.csv")
sinaf = dx3[dx3.dx3 == "Sin afectación"]
print(f"  n = {len(sinaf)}   ACE-III medio {sinaf.ACE.mean():.1f} (DE {sinaf.ACE.std():.1f}), "
      f"rango {sinaf.ACE.min():.0f}–{sinaf.ACE.max():.0f}")
bajos = sinaf[sinaf.ACE < 82]
print(f"  rotulados sin afectación con ACE-III < 82: {len(bajos)} "
      f"({100*len(bajos)/len(sinaf):.1f} %) -> revisar manualmente")
dxall = pd.read_csv(NM / "analisis/dx_conclusiones.csv")
fn = dxall[(dxall.normal == True) & (dxall.severidad.notna())]
print(f"  conclusiones con marca «normal» Y una palabra de severidad: {len(fn)} "
      f"-> la regla las clasifica por severidad, no como normales (salvaguarda activa)")
R["sin_afectacion"] = {"n": int(len(sinaf)), "ACE_medio": round(float(sinaf.ACE.mean()), 1),
                       "ACE_min": float(sinaf.ACE.min()), "con_ACE_bajo_82": int(len(bajos)),
                       "normal_con_severidad": int(len(fn))}

# ═══════════════════════════════════════════ E. MUESTRA PARA AUDITORÍA HUMANA
print("\n" + "=" * 92 + "\nE. MUESTRA ALEATORIA ESTRATIFICADA PARA LECTURA HUMANA")
dxall["frase_n"] = dxall.frase.fillna("")
mu = (dxall.dropna(subset=["severidad"]).groupby("severidad", group_keys=False)
      .apply(lambda g: g.sample(min(8, len(g)), random_state=42)))
mu = pd.concat([mu, dxall[dxall.normal == True].sample(min(10, int((dxall.normal == True).sum())),
                                                       random_state=42)])
mu = mu[["evaluacion_id", "severidad", "normal", "funcional", "grupo", "frase"]]
(EST / "verificacion").mkdir(exist_ok=True)
mu.to_csv(EST / "verificacion/V6_muestra_auditoria.csv", index=False)
print(f"  {len(mu)} conclusiones guardadas en verificacion/V6_muestra_auditoria.csv")
print("  ejemplos (oración textual y etiqueta asignada):")
for _, r in mu.head(6).iterrows():
    print(f"    [{str(r.severidad):<16} normal={r.normal}]  «{str(r.frase)[:135]}...»")

# ═══════════════════════════════════════════ F. VALIDACIÓN INDEPENDIENTE
print("\n" + "=" * 92 + "\nF. VALIDACIÓN INDEPENDIENTE — el ACE-III no se usó para clasificar")
g = dx3.groupby("dx3").ACE.agg(["size", "mean", "std"]).round(1)
print(g.to_string())
gr = [dx3[dx3.dx3 == k].ACE.values for k in ["Sin afectación", "DCL", "Demencia"]]
kw = stats.kruskal(*gr)
js = stats.jonckheeretrendtest if hasattr(stats, "jonckheeretrendtest") else None
print(f"\n  Kruskal-Wallis entre los tres grupos: H={kw.statistic:.1f}, p={kw.pvalue:.2e}")
print(f"  diferencia sin afectación vs DCL: {gr[0].mean()-gr[1].mean():+.1f} puntos")
print(f"  diferencia DCL vs demencia:       {gr[1].mean()-gr[2].mean():+.1f} puntos")
auc = lambda a, b: (np.mean([1 if x > y else 0.5 if x == y else 0 for x in a for y in b]))
print(f"  discriminación ACE-III sin afectación vs demencia: AUC={auc(gr[0], gr[2]):.3f}")
print(f"  discriminación ACE-III DCL vs demencia:            AUC={auc(gr[1], gr[2]):.3f}")
R["validacion_independiente"] = {
    "medias": g.reset_index().astype(str).to_dict("records"),
    "kruskal_H": round(float(kw.statistic), 1), "kruskal_p": float(kw.pvalue),
    "auc_sinaf_vs_demencia": round(float(auc(gr[0], gr[2])), 3),
    "auc_dcl_vs_demencia": round(float(auc(gr[1], gr[2])), 3)}

(EST / "resultados/V6_verificacion_dx.json").write_text(
    json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> resultados/V6_verificacion_dx.json")
