#!/usr/bin/env python3
"""
blog/bauen.py — baut den Blog aus blog/artikel.json.

Was es tut, in dieser Reihenfolge:
1. Jeder Artikel mit "quelle": "md" wird aus blog/<slug>/artikel.md neu gebaut
   (Vorlage: blog/_vorlage.html). Handgemachte Seiten ("quelle": "html") bleiben unberührt.
2. Die Blog-Übersicht blog/index.html bekommt ihre Karten neu:
   oben alle Grundlagen, darunter die 10 neuesten Artikel, der neueste mit „Neu“.
3. Die Startseite index.html zeigt im Abschnitt „Aus dem Blog“ die 2 neuesten Artikel.

Aufruf aus dem Website-Ordner:   python3 blog/bauen.py
Nur Python-Standardbibliothek. Läuft beliebig oft, das Ergebnis ist immer gleich.

artikel.md beginnt mit einem Kopf zwischen zwei Zeilen "---", danach Markdown:
  ## Zwischenüberschrift · **fett** · *kursiv* · [Text](https://…) · - Liste · > Zitat
Eine Listenzeile, die mit einer Adresse endet, wird ein Link mit dem Text davor.
"""
import html
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
BLOG = WURZEL / "blog"
DOMAIN = "https://firmenwissen-retten.de"
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]
MAX_NEU = 10
MAX_START = 2


def datum_lang(iso):
    d = date.fromisoformat(iso)
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


def esc(t):
    return html.escape(t, quote=True)


# ---------- Markdown, bewusst klein gehalten ----------

def inline(t):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<em>\1</em>", t)
    return t


def listenpunkt(t):
    m = re.match(r"^(.*?)[\s:,–-]*\s(https?://\S+)\s*$", t)
    if m and m.group(1).strip():
        text = m.group(1).strip().rstrip(":,").strip()
        return f'<a href="{esc(m.group(2))}">{inline(text)}</a>'
    return inline(t)


def markdown(md):
    zeilen = md.strip().splitlines()
    out, absatz, liste, zitat = [], [], [], []

    def leeren():
        if absatz:
            out.append(f"<p>{inline(' '.join(absatz))}</p>")
            absatz.clear()
        if liste:
            out.append("<ul>\n" + "\n".join(f"<li>{listenpunkt(x)}</li>" for x in liste) + "\n</ul>")
            liste.clear()
        if zitat:
            out.append(f"<blockquote><p>{inline(' '.join(zitat))}</p></blockquote>")
            zitat.clear()

    for z in zeilen:
        s = z.strip()
        if not s:
            leeren()
        elif s.startswith("### "):
            leeren(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            leeren(); out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "):
            continue  # die H1 setzt die Vorlage
        elif s.startswith("- "):
            if absatz or zitat:
                leeren()
            liste.append(s[2:])
        elif s.startswith("> "):
            if absatz or liste:
                leeren()
            zitat.append(s[2:])
        else:
            if liste or zitat:
                leeren()
            absatz.append(s)
    leeren()
    return "\n".join(out)


def kopf_lesen(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("artikel.md braucht einen Kopf zwischen zwei Zeilen ---")
    kopf = {}
    for z in m.group(1).splitlines():
        if ":" in z:
            k, v = z.split(":", 1)
            kopf[k.strip()] = v.strip()
    return kopf, m.group(2)


def woerter(md):
    return len(re.findall(r"\w+", md))


# ---------- Artikelseite ----------

def baue_artikel(a, vorlage):
    ordner = BLOG / a["slug"]
    kopf, md = kopf_lesen((ordner / "artikel.md").read_text(encoding="utf-8"))
    url = f"{DOMAIN}/blog/{a['slug']}/"
    geaendert = a.get("geaendert", a["datum"])
    bild_html, og_bild, bild_abs = "", "", None
    if a.get("bild"):
        bild_abs = DOMAIN + a["bild"]
        bild_html = (f'      <img class="fr-article-image" src="{esc(a["bild"])}" '
                     f'alt="{esc(a.get("bild_alt", ""))}" width="1200" height="675">')
        og_bild = f'<meta property="og:image" content="{esc(bild_abs)}">\n'
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["titel"],
        "description": a["beschreibung"],
        "datePublished": a["datum"],
        "dateModified": geaendert,
        "author": {"@type": "Person", "name": "Sonja Strahler",
                   "url": "https://www.linkedin.com/in/sonja-strahler/"},
        "publisher": {"@type": "Organization", "name": "Ein offener Blick GmbH",
                      "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/Favicon.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    if bild_abs:
        jsonld["image"] = bild_abs
    werte = {
        "TITEL_SEITE": esc(f"{a['titel']} | Second – Firmenwissen retten"),
        "TITEL": esc(a["titel"]),
        "BESCHREIBUNG": esc(a["beschreibung"]),
        "URL": url,
        "OG_BILD": og_bild,
        "DATUM": a["datum"],
        "GEAENDERT": geaendert,
        "JSONLD": json.dumps(jsonld, ensure_ascii=False, indent=2),
        "KATEGORIE": esc(a["kategorie"]),
        "UNTERZEILE": esc(kopf.get("unterzeile", "")),
        "DATUM_LANG": datum_lang(a["datum"]),
        "GEAENDERT_LANG": datum_lang(geaendert),
        "LESEZEIT": str(max(1, math.ceil(woerter(md) / 200))),
        "BILD": bild_html,
        "TEXT": markdown(md),
    }
    seite = vorlage
    for k, v in werte.items():
        seite = seite.replace("{{" + k + "}}", v)
    rest = re.findall(r"\{\{[A-Z_]+\}\}", seite)
    if rest:
        raise ValueError(f"Platzhalter nicht gefüllt: {rest}")
    (ordner / "index.html").write_text(seite, encoding="utf-8")


# ---------- Karten ----------

def typo_feld(a, klasse):
    satz = a.get("kernsatz") or a["titel"]
    return f'<div class="{klasse}"><span>{esc(satz)}</span></div>'


def karte_uebersicht(a, neu):
    href = f"/blog/{a['slug']}/"
    teile = [f'      <a class="fr-blog-card" href="{href}">']
    if neu:
        teile.append('        <span class="fr-blog-card__badge">Neu</span>')
    if a.get("bild"):
        teile.append(f'        <img class="fr-blog-card__image" src="{esc(a["bild"])}" '
                     f'alt="{esc(a.get("bild_alt", ""))}" loading="lazy" width="1200" height="675">')
    else:
        teile.append("        " + typo_feld(a, "fr-blog-card__typo"))
    teile += [
        '        <div class="fr-blog-card__body">',
        f'          <span class="fr-blog-card__category">{esc(a["kategorie"])}</span>',
        f'          <h3 class="fr-blog-card__title">{esc(a["titel"])}</h3>',
        f'          <p class="fr-blog-card__teaser">{esc(a["teaser"])}</p>',
        f'          <span class="fr-blog-card__date">{datum_lang(a["datum"])}</span>',
        '        </div>',
        '      </a>',
    ]
    return "\n".join(teile)


def karte_grundlage(a):
    return "\n".join([
        f'      <a class="fr-blog-card" href="/blog/{a["slug"]}/">',
        '        <div class="fr-blog-card__body">',
        '          <span class="fr-blog-card__category">Grundlage</span>',
        f'          <h2 class="fr-blog-card__title">{esc(a["titel"])}</h2>',
        f'          <p class="fr-blog-card__teaser">{esc(a["teaser"])}</p>',
        '          <span class="fr-blog-card__read">Lesen →</span>',
        '        </div>',
        '      </a>',
    ])


START_KARTE = ('        <a class="fr-auftauchen fr-blogkarte" href="/blog/{slug}/" style="display:block; '
               'background:#fff; border:1px solid rgba(26,34,64,.10); border-radius:var(--radius,14px); '
               'overflow:hidden; text-decoration:none; transition:border-color .18s ease;" '
               'style-hover="border-color:rgba(28,124,210,.5);">\n'
               '          {bild}\n'
               '          <div style="padding:0 30px 34px;">\n'
               '            <div class="fr-auftauchen" style="margin-top:20px; font-family:ui-monospace,\'SF Mono\',Menlo,monospace; '
               'font-size:12px; letter-spacing:.02em; color:rgba(26,34,64,.44);">{datum}</div>\n'
               '            <h3 class="fr-auftauchen" style="margin-top:14px; font-size:20px; font-weight:500; line-height:1.3; '
               'letter-spacing:-.01em; color:#1A2240;">{titel}</h3>\n'
               '            <div class="fr-auftauchen" style="margin-top:18px; color:#1c7cd2; font-weight:500; font-size:15px;">Lesen →</div>\n'
               '          </div>\n'
               '        </a>')


def karte_start(a):
    if a.get("bild"):
        bild = (f'<div class="fr-blogkarte__bild"><img src="{esc(a["bild"])}" alt="" loading="lazy" '
                'style="display:block; width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;"></div>')
    else:
        satz = esc(a.get("kernsatz") or a["titel"])
        bild = ('<div class="fr-blogkarte__bild" style="aspect-ratio:16/9; background:#1A2240; border-radius:10px; '
                'display:flex; align-items:flex-end; padding:clamp(22px,3vw,36px); box-sizing:border-box;">'
                '<span style="color:#fff; font-size:clamp(22px,2.4vw,32px); font-weight:500; line-height:1.18; '
                f'letter-spacing:-.015em;"><span style="color:#fd8c4a;">„</span>{satz}<span style="color:#fd8c4a;">“</span></span></div>')
    return START_KARTE.format(slug=a["slug"], bild=bild, datum=datum_lang(a["datum"]), titel=esc(a["titel"]))


def ersetze_zwischen(text, start, ende, neu, wo):
    i = text.find(start)
    j = text.find(ende, i + len(start)) if i >= 0 else -1
    if i < 0 or j < 0:
        raise ValueError(f"Marke nicht gefunden in {wo}: {start!r}")
    return text[:i + len(start)] + "\n" + neu + "\n" + text[j:]


def main():
    liste = json.loads((BLOG / "artikel.json").read_text(encoding="utf-8"))
    vorlage = (BLOG / "_vorlage.html").read_text(encoding="utf-8")

    for a in liste:
        if a.get("quelle") == "md":
            baue_artikel(a, vorlage)

    grundlagen = sorted([a for a in liste if a["typ"] == "grundlage"], key=lambda a: a["datum"])
    artikel = sorted([a for a in liste if a["typ"] == "artikel"], key=lambda a: a["datum"], reverse=True)

    p = BLOG / "index.html"
    t = p.read_text(encoding="utf-8")
    t = ersetze_zwischen(t, "<!-- GRUNDLAGEN:START -->", "<!-- GRUNDLAGEN:ENDE -->",
                         "\n".join(karte_grundlage(a) for a in grundlagen), "blog/index.html")
    t = ersetze_zwischen(t, "<!-- NEU:START -->", "<!-- NEU:ENDE -->",
                         "\n".join(karte_uebersicht(a, i == 0) for i, a in enumerate(artikel[:MAX_NEU])),
                         "blog/index.html")
    p.write_text(t, encoding="utf-8")

    p = WURZEL / "index.html"
    t = p.read_text(encoding="utf-8")
    t = ersetze_zwischen(t, '<div class="fr-blogkarten">', '\n      </div>\n      <a class="fr-auftauchen" href="/blog/"',
                         "\n".join(karte_start(a) for a in artikel[:MAX_START]), "index.html")
    p.write_text(t, encoding="utf-8")

    print(f"Fertig: {len(grundlagen)} Grundlagen, {min(len(artikel), MAX_NEU)} Artikel in der Übersicht, "
          f"{min(len(artikel), MAX_START)} auf der Startseite.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # klare Meldung statt Stacktrace
        print(f"FEHLER: {e}")
        sys.exit(1)
