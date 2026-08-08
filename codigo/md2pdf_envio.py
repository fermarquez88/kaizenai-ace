#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convierte un .md a PDF listo para imprimir/circular, 100% local.
markdown -> HTML (con CSS de impresion) -> PDF via Chrome headless.

Uso: python md2pdf.py archivo.md [salida.pdf]
"""
import subprocess, sys, tempfile
from pathlib import Path
import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 18mm 17mm 20mm 17mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
       font-size: 10.2pt; line-height: 1.5; color: #000; margin: 0; }
h1 { font-size: 16pt; line-height: 1.25; margin: 0 0 4mm; padding-bottom: 3mm;
      color: #000; }
h2 { font-size: 12pt; margin: 7mm 0 2.5mm; color: #000;
     page-break-after: avoid; break-after: avoid; }
h3 { font-size: 10.6pt; margin: 6mm 0 2mm; color: #000;
     page-break-after: avoid; break-after: avoid; }
p { margin: 0 0 2.6mm; orphans: 3; widows: 3; }
strong { color: #000; }
hr { border: none; margin: 4mm 0; }
ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.4mm; }
blockquote { margin: 3mm 0 3.5mm; padding: 3mm 4mm; background: none;
              font-size: 10pt; }
blockquote p { margin: 0; }
table { border-collapse: collapse; width: 100%; margin: 3.5mm 0 2mm; font-size: 9pt;
        page-break-inside: avoid; break-inside: avoid;
        font-variant-numeric: tabular-nums; }
thead tr { border-top: 1.1pt solid #000; }
th { background: none; color: #000; text-align: left; font-weight: 600;
     padding: 1.6mm 2mm 1.4mm; border: none; border-bottom: 1.1pt solid #000;
     vertical-align: bottom; }
td { padding: 1.3mm 2mm; border: none; vertical-align: top; text-align: left; }
tbody tr:last-child td { border-bottom: 0.8pt solid #000; }
table + p, table + blockquote { font-size: 8.6pt; color: #444; margin-top: 1.5mm; }
code { font-family: "SF Mono", Menlo, monospace; font-size: 9pt;
       background: none; padding: 0.3mm 1mm; border-radius: 2px; }
/* bloque de encabezado (Para/De/Fecha) */
body > p:first-of-type { padding:0; margin-bottom:3mm; }
"""


def main():
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix(".pdf")
    html_body = markdown.markdown(src.read_text(encoding="utf-8"),
                                  extensions=["tables", "fenced_code", "sane_lists"])
    doc = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
           f'<title>{src.stem}</title><style>{CSS}</style></head>'
           f'<body>{html_body}</body></html>')
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "doc.html"
        tmp.write_text(doc, encoding="utf-8")
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer", f"--print-to-pdf={out}",
               f"--user-data-dir={td}/profile", tmp.as_uri()]
        # Chrome headless a veces escribe el PDF y no termina el proceso. El criterio de éxito es
        # que el archivo exista y sea nuevo, no que el proceso salga limpio.
        antes = out.stat().st_mtime if out.exists() else 0
        r = None
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            pass
    if not out.exists() or out.stat().st_mtime <= antes:
        if r is not None:
            print("FALLO\n", r.stdout[-2000:], r.stderr[-2000:])
        else:
            print("FALLO: Chrome expiró sin escribir el PDF")
        sys.exit(1)
    print(f"OK -> {out}  ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
