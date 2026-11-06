#!/usr/bin/env python3
"""Logo e copertine di Casa Respira.

Produce in assets/:
  logo.svg, logo-orizzontale.svg, logo-512.png, favicon.svg
  og/<slug>.png  (1200x630) per home, sezioni, guide e notizie
Richiede: cairosvg, font IBM Plex Sans e Fraunces installati.
"""
import os, sys, html, pathlib, re
import cairosvg

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build as B  # riusa dati, casa_svg, TEMI

ROOT = pathlib.Path(B.OUT)
ASSETS = ROOT / "assets"
OG = ASSETS / "og"

INK = "#16222E"; AMBRA = "#C98A00"; ARIA = "#2E7FB8"; CARTA = "#F7F3EC"


def esc(s): return html.escape(s, quote=True)


# ------------------------------------------------------------ logo
def logo_mark(size=120, bg=True):
    """Icona: tetto-arco azzurro, base ambra (il terreno), punto radon che sale."""
    r = size * 0.18
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="{size}" height="{size}" role="img" aria-label="Casa Respira">
{'<rect width="120" height="120" rx="26" fill="' + INK + '"/>' if bg else ''}
<path d="M24 78 A36 36 0 0 1 96 78" fill="none" stroke="{ARIA}" stroke-width="10" stroke-linecap="round"/>
<path d="M40 78 A20 20 0 0 1 80 78" fill="none" stroke="{ARIA}" stroke-width="7" stroke-linecap="round" opacity=".5"/>
<rect x="28" y="84" width="64" height="10" rx="5" fill="{AMBRA}"/>
<circle cx="60" cy="66" r="6" fill="{AMBRA}"/>
</svg>"""


def logo_orizzontale():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 120" width="520" height="120" role="img" aria-label="Casa Respira, aria e acqua di casa, misurate e spiegate">
<g transform="translate(0,0) scale(1)">{logo_mark(120, bg=True).split('>',1)[1].rsplit('</svg>',1)[0]}</g>
<text x="142" y="62" font-family="Fraunces, Georgia, serif" font-weight="600" font-size="46" fill="{INK}">Casa Respira</text>
<text x="144" y="92" font-family="IBM Plex Sans, sans-serif" font-size="19" fill="#5F6E7B">aria e acqua di casa, misurate e spiegate</text>
</svg>"""


# ------------------------------------------------------------ copertine
def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines


def copertina(titolo, sottotitolo, tema=None, chiave=None, etichetta=None):
    """1200x630. Sinistra: etichetta, titolo, sottotitolo. Destra: casa con tema acceso. In basso: marchio."""
    colore = B.TEMI.get("/" + tema + "/", (None, ARIA, "#E6F1F9"))[1] if tema else ARIA
    chiaro = B.TEMI.get("/" + tema + "/", (None, ARIA, "#EEF2F5"))[2] if tema else "#EEF2F5"
    casa = B.casa_svg(tema, cls="casa")
    casa_inner = casa.split('>', 1)[1].rsplit('</svg>', 1)[0]
    # con focus: spegne gli altri livelli (il CSS della pagina qui non c'è)
    if tema:
        for t in ["radon", "muffa", "aria", "ventilazione", "acqua"]:
            if t != tema:
                casa_inner = casa_inner.replace(f'<g class="l-{t}">', f'<g class="l-{t}" opacity=".18">')
    lines = wrap(titolo, 22)
    fs = 56 if len(lines) <= 2 else (48 if len(lines) == 3 else 42)
    y0 = 250 if len(lines) <= 2 else 225
    tspans = "".join(f'<tspan x="80" dy="{0 if i == 0 else fs * 1.12}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    y_sub = y0 + fs * 1.12 * (len(lines) - 1) + 54
    sub_lines = wrap(sottotitolo, 46)[:2]
    sub = "".join(f'<tspan x="80" dy="{0 if i == 0 else 30}">{esc(l)}</tspan>' for i, l in enumerate(sub_lines))
    chiave_svg = ""
    if chiave:
        n, u = chiave
        chiave_svg = f'''<g transform="translate(80,{y_sub + 30 * len(sub_lines) + 62})">
<text font-family="Fraunces, Georgia, serif" font-weight="600" font-size="64" fill="{INK}">{esc(n)}</text>
<text x="{len(n) * 38 + 14}" y="-2" font-family="IBM Plex Sans, sans-serif" font-weight="500" font-size="24" fill="{colore}">{esc(u)}</text></g>'''
    etic = f'<rect x="80" y="112" rx="16" width="{len(etichetta) * 12 + 36}" height="34" fill="{chiaro}"/><text x="98" y="135" font-family="IBM Plex Sans, sans-serif" font-weight="600" font-size="19" fill="{colore}">{esc(etichetta)}</text>' if etichetta else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#F4EEE3"/></linearGradient></defs>
<rect width="1200" height="630" fill="url(#bg)"/>
<rect x="0" y="618" width="1200" height="12" fill="{colore}"/>
{etic}
<text y="{y0}" font-family="Fraunces, Georgia, serif" font-weight="500" font-size="{fs}" fill="{INK}">{tspans}</text>
<text y="{y_sub}" font-family="IBM Plex Sans, sans-serif" font-size="22" fill="#2A3845">{sub}</text>
{chiave_svg}
<g transform="translate(640,96) scale(0.84)">{casa_inner}</g>
<g transform="translate(80,548) scale(0.4)">{logo_mark(120).split('>', 1)[1].rsplit('</svg>', 1)[0]}</g>
<text x="140" y="572" font-family="Fraunces, Georgia, serif" font-weight="600" font-size="26" fill="{INK}">Casa Respira</text>
<text x="140" y="596" font-family="IBM Plex Sans, sans-serif" font-size="15" fill="#5F6E7B">casarespira.it · aria e acqua di casa, misurate e spiegate</text>
</svg>"""


def png(svg, path, w=None):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(path), output_width=w)


def main():
    OG.mkdir(parents=True, exist_ok=True)
    (ASSETS / "logo.svg").write_text(logo_mark(120), encoding="utf-8")
    (ASSETS / "logo-orizzontale.svg").write_text(logo_orizzontale(), encoding="utf-8")
    png(logo_mark(120), ASSETS / "logo-512.png", 512)
    png(logo_mark(120), ASSETS / "logo-192.png", 192)
    (ASSETS / "favicon.svg").write_text(logo_mark(120), encoding="utf-8")

    covers = {"home": copertina("Cosa respiri e cosa bevi dentro casa?",
                                "Radon, muffa, aria, ventilazione e acqua, spiegati con i numeri delle fonti pubbliche.",
                                None, None, "Guida indipendente")}
    for path, nome, lead, prev in B.SEZIONI:
        t = B.TEMI[path][0]
        covers[t] = copertina(nome, lead, t, None, "Sezione")
    for p in B.PAGES:
        if p["status"] != "live": continue
        slug = p["path"].strip("/").replace("/", "-")
        t = B.tema_di(p["path"]) or None
        ch = (p["chiave"][0], p["chiave"][1]) if p.get("chiave") else None
        covers[slug] = copertina(p["title"], p["desc"], t, ch, "Guida" if t else None)
    for n in B.NEWS:
        covers["news-" + n[0]] = copertina(n[3], n[2], "radon", None, "Notizia")
    covers["news"] = copertina("News", "Campagne di misura gratuite, nuove aree prioritarie, norme. Solo con fonte e data.", None, None, "Notizie")
    for slug, svg in covers.items():
        png(svg, OG / f"{slug}.png")
    print("copertine:", len(covers), "| logo ok")


if __name__ == "__main__":
    main()
