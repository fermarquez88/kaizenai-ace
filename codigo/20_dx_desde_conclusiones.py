#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLASIFICACIÓN CLÍNICA DESDE LA CONCLUSIÓN DEL INFORME (texto), no desde los puntajes z.

Por qué no `perfil_cognitivo_inferido.subtipo`: coincide con `subtipo_z` en 8896/9618 — es el
perfil derivado de los z, que están normados por edad × EDUCACIÓN. Usarlo para estratificar un
estudio cuya exposición es la educación sería circular. Además contradice al texto (casos
rotulados `normal` cuya conclusión dice "compromiso de severidad leve a predominio de la atención").

Fuente: sección `conclusiones` del informe. Se exige la oración diagnóstica canónica
("El presente perfil cognitivo se corresponde con...") y se usa SÓLO esa oración: extenderla
arrastra el listado de recomendaciones ("...neuropsicología, actividades...") y contamina el
criterio funcional. De 3713 conclusiones, 2764 la contienen; las 949 restantes son informes de
imágenes o cierres administrativos que la segmentación capturó mal -> se excluyen.

Ejes: normalidad · severidad · compromiso funcional · dominio predominante · extensión.
Validación independiente (no se usó para clasificar): el ACE-III debe ordenarse por severidad, y
el grupo amnésico debe mostrar peor MEMORIA del ACE-III relativa al resto del test.

Salida: analisis/dx_conclusiones.csv + out/20_dx.json
"""
import json, re, unicodedata, warnings
from pathlib import Path
import duckdb, pandas as pd, numpy as np
from scipy import stats as st

warnings.simplefilter("ignore")
INECO = Path("/Users/fernandomarquez/Documents/Claude/Projects/Instituto de neurociencias - Castaño")
NM = Path("/Users/fernandomarquez/Documents/Claude/Projects/neuromentia")
OUTD = NM / "ACE/out"; OUTD.mkdir(exist_ok=True)
c1 = duckdb.connect(str(INECO / "db/evaluaciones_v1.duckdb"), read_only=True)
R = {}


def nrm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s)


FRASE = re.compile(r"(el presente perfil cognitivo[^.]*\.)")          # UNA sola oración
NORMAL = re.compile(r"no presenta (importancia|relevancia) clinica|dentro de (los )?parametros|"
                    r"perfil cognitivo normal|sin (evidencia de )?deterioro|"
                    r"no se (evidencia|observa)|rendimiento (cognitivo )?normal|"
                    r"no parece ser de (gran )?relevancia")
FUNCIONAL = re.compile(r"suficiente para (comprometer|afectar)")
MULT = re.compile(r"multiples dominios|mas de un dominio|varios dominios")
# severidad: de la más grave a la más leve; el orden importa
SEV = [("moderado-severo", r"moderad[oa]\s*a\s*(?:sever[oa]|grave)"),
       ("leve-moderado", r"leve\s*a\s*moderad"),
       ("severo", r"\b(sever[oa]|grave)\b"),
       ("moderado", r"\bmoderad[oa]\b"),
       ("leve", r"\bleve\b|disfuncion")]
PRED = re.compile(r"predominio\s+(?:de\s+(?:la|las|los|el)\s+|del\s+|de\s+|en\s+el\s+)?"
                  r"([a-z]+(?:\s+(?:y|e)\s+[a-z]+)?(?:\s+[a-z]+)?)")
AMN = re.compile(r"amnesic|mnesic|memoria")
NOAMN = re.compile(r"atencion|atencional|ejecutiv|lenguaje|linguistic|visuoespacial|visoespacial|"
                   r"velocidad|praxi|gnosi")


def clasifica(txt):
    m = FRASE.search(nrm(txt))
    if not m:
        return None
    f = m.group(1)
    o = {"frase": f[:280], "normal": bool(NORMAL.search(f)),
         "funcional": bool(FUNCIONAL.search(f)), "multiples": bool(MULT.search(f))}
    o["severidad"] = next((n for n, p in SEV if re.search(p, f)), None)
    # predominio explícito; si no lo hay, se usa la mención de dominios en la propia oración
    preds = [x.group(1) for x in PRED.finditer(f)]
    txtp = " ".join(preds) if preds else f
    a, na = bool(AMN.search(txtp)), bool(NOAMN.search(txtp))
    o["predominio_explicito"] = bool(preds)
    o["perfil"] = "amnesico" if (a and not na) else ("no_amnesico" if (na and not a) else
                                                     ("mixto" if (a and na) else None))
    return o


def grupo(r):
    if r["normal"] and r["severidad"] is None:
        return "1_sin_deterioro"
    if r["funcional"] or r["severidad"] in ("moderado", "moderado-severo", "severo"):
        return "4_deterioro_mayor"
    if r["severidad"] in ("leve", "leve-moderado"):
        return {"amnesico": "2_leve_amnesico", "no_amnesico": "3_leve_no_amnesico",
                "mixto": "2_leve_amnesico"}.get(r["perfil"])
    return None


d = c1.execute("""
    select s.evaluacion_id, s.texto conclusiones, p.dni, e.fecha_evaluacion
    from informe_secciones s
    join evaluaciones e on e.evaluacion_id = s.evaluacion_id
    join pacientes_pii p on p.paciente_id = e.paciente_id
    where s.seccion='conclusiones' and s.texto is not null and p.dni is not null
""").fetchdf()
cl = [clasifica(t) for t in d.conclusiones]
d["_ok"] = [c is not None for c in cl]
print(f"conclusiones con DNI: {len(d)} | con oración diagnóstica canónica: {int(d._ok.sum())}")
d = pd.concat([d[d._ok].reset_index(drop=True),
               pd.DataFrame([c for c in cl if c])], axis=1)
d["grupo"] = d.apply(grupo, axis=1)
d["dni"] = d.dni.astype(str).str.replace(r"\D", "", regex=True)
d["f"] = pd.to_datetime(d.fecha_evaluacion, errors="coerce", dayfirst=True)

print("\nseveridad:", d.severidad.value_counts(dropna=False).to_dict())
print("perfil:", d.perfil.value_counts(dropna=False).to_dict(),
      f"| predominio explícito: {int(d.predominio_explicito.sum())}")
print("compromiso funcional:", int(d.funcional.sum()), "| múltiples dominios:", int(d.multiples.sum()))
print("GRUPO:", d.grupo.value_counts(dropna=False).to_dict())
d.drop(columns=["conclusiones", "_ok"]).to_csv(NM / "analisis/dx_conclusiones.csv", index=False)

# ---------------------------------------------------------------- validación
cli = pd.read_csv(NM / "analisis/clinico_educacion_corregida.csv")
cli["dni"] = cli.persona_id.astype(str).str.replace(r"\D", "", regex=True)
cli["f"] = pd.to_datetime(cli.fecha_ev, errors="coerce", format="ISO8601")   # ISO: NO dayfirst
v = cli.drop(columns=[c for c in ["severidad", "subtipo", "frase_dx"] if c in cli.columns]).merge(
    d.drop_duplicates(["dni", "f"])[["dni", "f", "grupo", "severidad", "perfil", "funcional"]],
    on=["dni", "f"], how="inner")
print(f"\nenlazado con la muestra ACE: {len(v)} ({100*len(v)/len(cli):.1f}%)")

print("\n(a) ACE-III total por severidad — no se usó para clasificar:")
ORD = ["leve", "leve-moderado", "moderado", "moderado-severo", "severo"]
print(v.groupby("severidad").ACE_total.agg(["count", "mean", "std"]).round(1)
      .reindex(ORD).dropna().to_string())

MEM = ["ACE_MRecuerdo", "ACE_MAnterogr", "ACE_MRetrogr", "ACE_MRecuerdoNyD", "ACE_MReconocNyD"]
if all(c in v.columns for c in MEM):
    v["MEM"] = v[MEM].sum(axis=1)
    v["mem_rel"] = v.MEM / 26 - (v.ACE_total - v.MEM) / 74
    print("\n(b) ACE-III y memoria relativa por grupo (más negativo = memoria peor que el resto):")
    print(v.groupby("grupo").agg(n=("ACE_total", "size"), ACE=("ACE_total", "mean"),
                                 memoria_26=("MEM", "mean"),
                                 memoria_relativa=("mem_rel", "mean")).round(2).to_string())
    a = v[v.grupo == "2_leve_amnesico"].mem_rel.dropna()
    b = v[v.grupo == "3_leve_no_amnesico"].mem_rel.dropna()
    if len(a) > 20 and len(b) > 20:
        tt = st.ttest_ind(a, b, equal_var=False)
        print(f"\n  leve amnésico ({a.mean():.3f}, n={len(a)}) vs leve no amnésico "
              f"({b.mean():.3f}, n={len(b)}): t={tt.statistic:.2f}, p={tt.pvalue:.2e}")
        R["validacion_amnesico"] = {"amnesico": round(float(a.mean()), 4),
                                    "no_amnesico": round(float(b.mean()), 4),
                                    "t": round(float(tt.statistic), 2), "p": float(tt.pvalue),
                                    "n_amn": int(len(a)), "n_noamn": int(len(b))}

R["grupos"] = {str(k): int(x) for k, x in d.grupo.value_counts(dropna=False).items()}
R["severidad"] = {str(k): int(x) for k, x in d.severidad.value_counts(dropna=False).items()}
R["enlazado"] = int(len(v))
(OUTD / "20_dx.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str))
print(f"\n-> analisis/dx_conclusiones.csv | {OUTD/'20_dx.json'}")
