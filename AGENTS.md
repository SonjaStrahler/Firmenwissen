
# Regeln für diese Website

- Arbeite nur im Branch `Umbau-Test`. Nie in `Firmenwissen` (das ist live).
- `index.html` und die Rechtsseiten sind Exporte aus Claude Design:
  - Struktur `<x-dc>` … `<helmet>` … unverändert lassen.
  - `support.js` nie anfassen (generiert).
  - Platzhalter wie `{{accentColor}}` stehen lassen.
  - Stile dürfen inline im `style`-Attribut oder in einem `<style>`-Block im `<helmet>` stehen. Effektklassen erhalten das Präfix `fr-`.
  - GSAP mit ScrollTrigger und Lenis liegen in assets/js/. Eigenes JavaScript darf in einem `<script>` am Ende von `<body>` stehen.
  - Die Krake-Logik im `<script type="text/x-dc">` nicht anfassen.
- Farben nur diese: Hintergrund #fbf9f5, Text #1A2240, Aktion #1c7cd2 (Hover #1769b4), Akzent #fd8c4a/#c46a2c, Flächen #f4f5f0, Karten weiß. Schrift Figtree.
- Keine fremden Server: Schriften, Skripte, Bilder und Videos liegen in assets/ und werden mit /assets/... eingebunden. Kein Google Fonts, kein CDN, keine YouTube-Einbettung.
- Anrede „Sie“. Keine Emojis. Keine Zahl erfinden.
- `krake.html`, `krake_web.py`, `krake_web.env`, `blog/`, `agb.html`, `avv.html`, `widerruf.html`, `datenschutz.html` nicht ändern, außer der Auftrag nennt die Datei.
- Ändere pro Auftrag nur die genannte Stelle. Zeige am Ende die geänderten Zeilen (git diff).
