# Blog

Hier liegt alles, was den Blog ausmacht. Jede Datei hat genau eine Aufgabe.

| Datei | Wofür | Wer ändert sie |
|---|---|---|
| `STIMME.md` | Wie geschrieben wird (Teil 1) und Sonjas persönliche Sätze (Teil 2) | Teil 1 nur mit Sonjas Wort, Teil 2 Sonja selbst |
| `QUELLEN.md` | Wo die Maschine nach Meldungen sucht, und wie sie bewertet | Sonja, jederzeit |
| `artikel.json` | Liste aller Artikel und Grundlagen, die Wahrheit für Übersicht und Startseite | die Maschine oder Claude |
| `<slug>/artikel.md` | der Text eines Artikels | die Maschine oder Claude |
| `bauen.py` | baut aus Liste und Texten die Seiten, die Übersicht und die zwei Karten auf der Startseite | niemand, nur bei Fehlern |
| `_vorlage.html` | das Aussehen jeder Artikelseite | nur mit Sonjas Wort |

**Einen persönlichen Satz ergänzen:** `STIMME.md` öffnen, ganz unten in Teil 2 eine Zeile mit einem Strich davor anfügen, speichern, wie immer pushen.

**Einen Artikel bauen** (macht die Maschine): Text nach `blog/<slug>/artikel.md`, Eintrag in `artikel.json`, dann im Website-Ordner `python3 blog/bauen.py`.

Keine fremden Server, keine YouTube-Einbettung. Bilder liegen in `blog/images/`, Videos in `assets/video/`.
