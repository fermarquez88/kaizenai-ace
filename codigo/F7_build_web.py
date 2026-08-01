#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Envuelve el cuerpo de la calculadora (calculadora/index.html, que es un fragmento pensado
para el visor de artefactos) en un documento HTML completo y autocontenido, apto para
GitHub Pages.

Salida: docs/index.html
"""
from pathlib import Path

EST = Path(__file__).resolve().parent.parent
CUERPO = (EST / "calculadora/index.html").read_text(encoding="utf-8")
(EST / "docs").mkdir(exist_ok=True)

# el fragmento trae su propio <title>; lo extraemos para no duplicarlo en el <head>
TITULO = "ACE-III — rendimiento esperado según escolaridad y edad"
cuerpo = CUERPO.replace(f"<title>{TITULO}</title>\n", "", 1).lstrip()

DESC = ("Calculadora del rendimiento esperado en el ACE-III según años de escolaridad y edad, "
        "con tabla de referencia y simulador de cohortes. Prototipo de investigación.")

RESET = """
/* reset mínimo — el visor de artefactos aporta el suyo; aquí va explícito */
*,*::before,*::after{box-sizing:border-box}
html{-moz-text-size-adjust:none;-webkit-text-size-adjust:none;text-size-adjust:none}
body,h1,h2,h3,h4,p,figure,blockquote,dl,dd{margin:0}
ul[role=list],ol[role=list]{list-style:none;margin:0;padding:0}
h1,h2,h3,h4{text-wrap:balance}
img,picture,svg{max-width:100%;display:block}
input,button,textarea,select{font:inherit;color:inherit}
table{border-collapse:collapse}
"""

TOGGLE_CSS = """
.tema{position:fixed;right:14px;top:14px;z-index:50;background:var(--panel);
  border:1px solid var(--rule-2);color:var(--ink-2);padding:6px 11px;font-size:12px;
  font-family:var(--sans);cursor:pointer;box-shadow:var(--shadow);line-height:1.2}
.tema:hover{color:var(--ink);border-color:var(--ink-3)}
@media print{.tema{display:none}}
"""

TOGGLE_JS = """
(function(){
  var b=document.getElementById("tema");
  var pref=null;
  try{ pref=localStorage.getItem("tema"); }catch(e){}
  function sistema(){ return matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"; }
  function aplicar(t){
    document.documentElement.setAttribute("data-theme",t);
    b.textContent = t==="dark" ? "Tema claro" : "Tema oscuro";
    b.setAttribute("aria-label", t==="dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  }
  aplicar(pref || sistema());
  b.addEventListener("click", function(){
    var t = document.documentElement.getAttribute("data-theme")==="dark" ? "light" : "dark";
    try{ localStorage.setItem("tema",t); }catch(e){}
    aplicar(t);
  });
})();
"""

HTML = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITULO}</title>
<meta name="description" content="{DESC}">
<meta name="color-scheme" content="light dark">
<meta name="author" content="Instituto de Neurociencias, Universidad Católica de Cuyo — San Juan, Argentina">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="{TITULO}">
<meta property="og:description" content="{DESC}">
<meta property="og:locale" content="es_AR">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>">
<style>{RESET}</style>
</head>
<body>
<button class="tema" id="tema" type="button">Tema oscuro</button>
{cuerpo}
<script>{TOGGLE_JS}</script>
</body>
</html>
"""

# el botón de tema necesita su CSS dentro del bloque de estilos del cuerpo
HTML = HTML.replace("</style>\n\n<header class=\"masthead\">",
                    TOGGLE_CSS + "</style>\n\n<header class=\"masthead\">", 1)

destino = EST / "docs/index.html"
destino.write_text(HTML, encoding="utf-8")
(EST / "docs/.nojekyll").write_text("")

print(f"-> docs/index.html  ({len(HTML)/1024:.1f} kB, autocontenido)")
print("-> docs/.nojekyll")
assert "<!doctype html>" in HTML and HTML.count("<body>") == 1, "documento mal formado"
assert ".tema{position:fixed" in HTML, "no se insertó el CSS del selector de tema"
print("verificación: documento completo y con selector de tema")
