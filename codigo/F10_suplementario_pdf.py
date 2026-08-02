#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maqueta el material suplementario como PDF con la identidad visual del trabajo.

El diseño es el mismo de las figuras y las tablas: paleta de azul, rojo, ámbar y grises —sin
verde—, tablas tipográficas sin bordes verticales con una regla bajo el encabezado, y todas las
cifras en monoespaciada tabular. Los bloques de verificación se numeran y se abren con una regla
del color que corresponde a su veredicto.

Uso: python F10_suplementario_pdf.py
Salida: SUPLEMENTARIO.pdf
"""
import re, subprocess, sys, tempfile, html
from pathlib import Path

EST = Path("/Users/fernandomarquez/Documents/Claude/Projects/ACE-III_educacion")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC = EST / "manuscrito/SUPLEMENTARIO.md"
OUT = EST / "SUPLEMENTARIO.pdf"
FIG = EST / "figuras"

# paleta idéntica a la de nature_style, que es la de todas las figuras del trabajo
CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
@page :first { margin: 0; }
:root {}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  font-size: 10pt; line-height: 1.52; color: #0b0b0b;
  -webkit-font-smoothing: antialiased;
}
.mono, code, td.num, .cifra {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-variant-numeric: tabular-nums;
}

/* ── portada ───────────────────────────────────────────────── */
.portada {
  height: 297mm; padding: 42mm 24mm 22mm; page-break-after: always;
  display: flex; flex-direction: column; background: #fcfcfb;
}
.portada .eyebrow {
  font-family: "SF Mono", Menlo, monospace; font-size: 8.4pt; letter-spacing: .16em;
  text-transform: uppercase; color: #8a8880; margin: 0 0 10mm;
}
.portada h1 {
  font-size: 25pt; line-height: 1.18; font-weight: 600; letter-spacing: -.015em;
  margin: 0 0 6mm; color: #0b0b0b; border: 0; padding: 0;
}
.portada .sub { font-size: 12pt; color: #52514e; margin: 0 0 14mm; line-height: 1.45; }
.portada .regla { height: 3px; background: #2a78d6; width: 54mm; margin: 0 0 14mm; }
.portada .meta { margin-top: auto; font-size: 9pt; color: #52514e; line-height: 1.6; }
.portada .meta b { color: #0b0b0b; }
.portada .cifras {
  display: flex; gap: 14mm; margin: 0 0 14mm; padding: 6mm 0;
  border-top: 1px solid #e1e0d9; border-bottom: 1px solid #e1e0d9;
}
.portada .cifras div { flex: 0 0 auto; }
.portada .cifras .n {
  font-family: "SF Mono", Menlo, monospace; font-size: 20pt; color: #2a78d6;
  font-variant-numeric: tabular-nums; line-height: 1;
}
.portada .cifras .l {
  font-size: 8.2pt; color: #8a8880; text-transform: uppercase; letter-spacing: .07em;
  margin-top: 2mm;
}

/* ── jerarquía ─────────────────────────────────────────────── */
h1 {
  font-size: 15pt; font-weight: 600; letter-spacing: -.012em; color: #0b0b0b;
  margin: 0 0 4mm; padding: 0 0 2.5mm; border-bottom: 2px solid #0b0b0b;
  page-break-before: always; page-break-after: avoid; break-after: avoid;
}
h1.sigue { page-break-before: auto; }
h2 {
  font-size: 11.4pt; font-weight: 600; color: #0b0b0b; margin: 7mm 0 2.5mm;
  padding-left: 3mm; border-left: 3px solid #2a78d6;
  page-break-after: avoid; break-after: avoid;
}
h3 {
  font-size: 10pt; font-weight: 600; color: #52514e; margin: 5mm 0 1.8mm;
  text-transform: none; page-break-after: avoid; break-after: avoid;
}
p { margin: 0 0 2.8mm; orphans: 3; widows: 3; }
strong { font-weight: 600; }
em { font-style: italic; color: #52514e; }
hr { border: 0; border-top: 1px solid #e1e0d9; margin: 6mm 0; }
ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.2mm; }
a { color: #1b5aa8; text-decoration: none; }
code {
  font-size: 8.8pt; background: #f2f2ed; padding: .3mm 1.2mm; border-radius: 2px;
  color: #0b0b0b;
}

/* ── tablas, con la estética de las figuras ────────────────── */
table {
  border-collapse: collapse; width: 100%; margin: 3.5mm 0 4.5mm; font-size: 8.9pt;
  page-break-inside: avoid; break-inside: avoid;
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-variant-numeric: tabular-nums;
}
th {
  text-align: left; font-weight: 600; color: #0b0b0b; padding: 1.6mm 2.4mm 1.9mm;
  border-bottom: 1.4px solid #0b0b0b; vertical-align: bottom; font-size: 8.6pt;
}
th:not(:first-child) { text-align: center; }
td {
  padding: 1.5mm 2.4mm; border-bottom: .6px solid #e1e0d9; vertical-align: top;
  text-align: center;
}
td:first-child { text-align: left; }
tbody tr:last-child td { border-bottom: .8px solid #c3c2b7; }

/* ── cajas ─────────────────────────────────────────────────── */
blockquote {
  margin: 3.5mm 0 4mm; padding: 3mm 4mm; background: #fcfcfb;
  border-left: 3px solid #c3c2b7; font-size: 9.4pt; color: #52514e;
  page-break-inside: avoid;
}
blockquote p { margin: 0 0 1.8mm; }
blockquote p:last-child { margin: 0; }
blockquote.veredicto { border-left-color: #2a78d6; background: rgba(42,120,214,.05); color: #0b0b0b; }
blockquote.alerta   { border-left-color: #d03b3b; background: rgba(208,59,59,.05); color: #0b0b0b; }
blockquote.aviso    { border-left-color: #fab219; background: rgba(250,178,25,.07); color: #0b0b0b; }

/* ── figuras ───────────────────────────────────────────────── */
figure { margin: 4mm 0 5mm; page-break-inside: avoid; break-inside: avoid; }
figure img { width: 100%; display: block; }
figcaption { font-size: 8.4pt; color: #52514e; margin-top: 2mm; line-height: 1.45; }
figcaption b { color: #0b0b0b; }

/* ── índice ────────────────────────────────────────────────── */
.indice { font-size: 9.4pt; }
.indice td { text-align: left; }
.indice td:first-child {
  font-family: "SF Mono", Menlo, monospace; color: #2a78d6; font-weight: 600;
  white-space: nowrap; width: 16mm;
}
"""


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'&lt;(https?://[^&\s]+?)&gt;', r'<a href="\1">\1</a>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


def clase_cita(txt: str) -> str:
    b = txt.lower()
    if any(k in b for k in ("veredicto", "queda establecid", "se confirma")): return " class=\"veredicto\""
    if any(k in b for k in ("defecto", "error", "incorrect", "obsolet", "invalid")): return " class=\"alerta\""
    if any(k in b for k in ("pendiente", "limitaci", "cautela", "advertencia")): return " class=\"aviso\""
    return ""


def md_a_html(md: str) -> str:
    out, L, i = [], md.split("\n"), 0
    primer_h1 = True
    while i < len(L):
        l = L[i]

        if re.match(r'^\|', l):                                    # tabla
            filas = []
            while i < len(L) and re.match(r'^\|', L[i]):
                filas.append([c.strip() for c in L[i].strip().strip('|').split('|')]); i += 1
            filas = [f for f in filas if not all(re.fullmatch(r':?-{2,}:?', (c or '-').strip()) for c in f)]
            if filas:
                out.append('<table>')
                out.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in filas[0]) + '</tr></thead><tbody>')
                for f in filas[1:]:
                    out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in f) + '</tr>')
                out.append('</tbody></table>')
            continue

        m = re.match(r'^(#{1,6}) +(.*)', l)
        if m:
            n, txt = len(m.group(1)), m.group(2)
            cls = ''
            if n == 1:
                if primer_h1: cls = ' class="sigue"'; primer_h1 = False
            out.append(f'<h{n}{cls}>{inline(txt)}</h{n}>'); i += 1; continue

        if re.match(r'^\s*---+\s*$', l):
            out.append('<hr>'); i += 1; continue

        if re.match(r'^\s*[-*] ', l) or re.match(r'^\s*\d+\. ', l):
            orden = bool(re.match(r'^\s*\d+\. ', l)); tag = 'ol' if orden else 'ul'
            out.append(f'<{tag}>')
            while i < len(L) and (re.match(r'^\s*[-*] ', L[i]) or re.match(r'^\s*\d+\. ', L[i])):
                item = [re.sub(r'^\s*(?:[-*]|\d+\.) ', '', L[i])]; i += 1
                while i < len(L) and L[i].startswith('  ') and L[i].strip() and not re.match(r'^\s*(?:[-*]|\d+\.) ', L[i]):
                    item.append(L[i].strip()); i += 1
                out.append('<li>' + inline(' '.join(item)) + '</li>')
            out.append(f'</{tag}>'); continue

        if re.match(r'^>', l):
            blk = []
            while i < len(L) and re.match(r'^>', L[i]):
                blk.append(re.sub(r'^> ?', '', L[i])); i += 1
            texto = ' '.join(blk)
            out.append(f'<blockquote{clase_cita(texto)}><p>' + inline(texto) + '</p></blockquote>'); continue

        if not l.strip(): i += 1; continue

        par = []
        while i < len(L) and L[i].strip() and not re.match(r'^(#{1,6} |\||>|\s*[-*] |\s*\d+\. |\s*---+\s*$)', L[i]):
            par.append(L[i]); i += 1
        out.append('<p>' + inline(' '.join(par)) + '</p>')
    return "\n".join(out)


def portada(n_bloques: int, n_figuras: int, n_tablas: int) -> str:
    return f"""<div class="portada">
  <p class="eyebrow">Material suplementario</p>
  <div class="regla"></div>
  <h1>Escolaridad y ACE-III en dos cohortes argentinas</h1>
  <p class="sub">Verificación, análisis de sensibilidad y material trasladado desde el cuerpo del
  manuscrito por límite de extensión.</p>
  <div class="cifras">
    <div><div class="n">{n_bloques}</div><div class="l">bloques de verificación</div></div>
    <div><div class="n">{n_figuras}</div><div class="l">figuras</div></div>
    <div><div class="n">{n_tablas}</div><div class="l">tablas</div></div>
  </div>
  <div class="meta">
    <b>Congreso Argentino de Neurología 2026</b><br>
    Instituto de Neurociencias de San Juan (Clínica El Castaño) · Universidad Católica de Cuyo ·
    Hospital Dr. Guillermo Rawson · CONICET<br><br>
    Código, datos agregados y bitácoras: <b>github.com/fermarquez88/kaizenai-ace</b><br>
    Calculadora del modelo normativo: <b>fermarquez88.github.io/kaizenai-ace</b><br><br>
    <em>Los datos individuales no se distribuyen: contienen identificadores directos y texto libre
    de conclusiones clínicas.</em>
  </div>
</div>"""


def main():
    md = SRC.read_text(encoding="utf-8")
    cuerpo = md_a_html(md)
    n_bloques = len(re.findall(r'^#{1,2} V\d+', md, re.M))
    n_tablas = cuerpo.count('<table')
    n_figuras = cuerpo.count('<figure')
    doc = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
           f'<title>Material suplementario — ACE-III y escolaridad</title>'
           f'<style>{CSS}</style></head><body>'
           f'{portada(n_bloques, n_figuras, n_tablas)}{cuerpo}</body></html>')
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "sup.html"
        tmp.write_text(doc, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
                        f"file://{tmp}"], capture_output=True, timeout=280)
    if OUT.exists():
        print(f"-> {OUT.name}  ({OUT.stat().st_size/1024:.0f} kB)")
        print(f"   {n_bloques} bloques · {n_tablas} tablas · {n_figuras} figuras")
    else:
        print("no se generó el PDF", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
