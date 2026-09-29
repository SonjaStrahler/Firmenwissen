
# Regeln für diese Website

- Arbeite nur im Branch `Umbau-Test`. Nie in `Firmenwissen` (das ist live).
- `index.html` und die Rechtsseiten sind Exporte aus Claude Design:
  - Struktur `<x-dc>` … `<helmet>` … unverändert lassen.
  - `support.js` nie anfassen (generiert).
  - Platzhalter wie `{{accentColor}}` stehen lassen.
  - Stile stehen inline im `style`-Attribut. Neue Elemente genauso bauen, keine neuen CSS-Dateien, keine Frameworks.
- Farben nur diese: Hintergrund #fbf9f5, Text #1A2240, Aktion #1c7cd2 (Hover #1769b4), Akzent #fd8c4a/#c46a2c, Flächen #f4f5f0, Karten weiß. Schrift Figtree.
- Anrede „Sie“. Keine Emojis. Keine Zahl erfinden.
- `krake.html`, `krake_web.py`, `krake_web.env`, `blog/`, `agb.html`, `avv.html`, `widerruf.html`, `datenschutz.html` nicht ändern, außer der Auftrag nennt die Datei.
- Ändere pro Auftrag nur die genannte Stelle. Zeige am Ende die geänderten Zeilen (git diff).
