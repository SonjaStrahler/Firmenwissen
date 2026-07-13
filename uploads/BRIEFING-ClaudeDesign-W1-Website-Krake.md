# BRIEFING Claude Design — W1: Krake-Sektion für die Website

> Von: Architekt Krake-Strecke. Stand: 10.07.2026. Auftraggeberin: Sonja.
> Ziel: Eine fertige, eigenständige HTML-Sektion (oder Seite) für die Website
> einoffenerblick.de — die Hilfe-Krake als öffentliches Schaufenster, plus zwei
> Video-Platzhalter. **Nur Optik und Frontend** — der Server-Endpunkt entsteht
> parallel als eigene Etappe (K5) auf dem Pi. Die Verbindung ist unten als
> fester Schnittstellen-Vertrag definiert, damit beide Seiten am Ende
> zusammenpassen, ohne aufeinander zu warten.

---

## Was mitgeliefert wird (Referenzmaterial)

1. `MOCKUP-K3-v3-Startansicht-FINAL.html` — die abgenommene App-Startansicht.
   **Nur als Referenz für Aufbau und Ruhe der Krake-Sektion** (Krake → Titel →
   Fragefeld → Merksatz → Beispielfragen). NICHT die Farben übernehmen!
2. `krake.png` — das Maskottchen (42 KB, transparent). Die Krake behält ihre
   eigenen Farben (Entscheid 07.07.).
3. `index.html` — die bestehende Landingpage (Struktur, Ton, Bausteine).
4. Farbwelt der Website (gilt, wie die  App-Palette):
   
## Was NICHT auf die Website gehört

- Keine Seitenleiste, keine Räume, kein „Mockup-Umschalter" — all das ist App.
- Keine App-Interna im Text (keine Technik-Begriffe, keine Preise-Details,
  die nicht ohnehin auf der Seite stehen).
- Keine Rechts-Zusagen („DSGVO-konform" o. Ä.) — beschreiben statt versprechen.

---

## Aufbau der Sektion (von oben nach unten)

**1. Die Krake als Blickfang.** Maskottchen groß und freundlich, Überschrift im
Ton der Marke, z. B. „Fragen Sie einfach — die Krake antwortet." Untertitel in
einem Satz: Sie beantwortet Fragen rund um die App und das Retten von
Firmenwissen — aus geprüftem Wissen, ehrlich, ohne Verkaufssprech.

**2. Das Fragefeld.** Ein Eingabefeld + Absenden-Knopf (Himmelblau als
Aktionsfarbe, wie die bestehenden Buttons der Seite). Darunter klein der
Merksatz: „Fragen Sie wie einen Kollegen, nicht wie eine Suchmaschine."

**3. Drei klickbare Beispielfragen** (auf der Website sind das einfache
Buttons/Links — Klick füllt das Feld und sendet ab):
- „Was macht diese App eigentlich?"
- „Wer sieht meine Daten?"
- „Was kostet das?"

**4. Antwortkarte.** Erscheint unter dem Feld: weiße Karte, dunkle Schrift,
ruhig. Während des Wartens ein dezenter Lade-Hinweis („Einen Moment …").

**5. Zwei Video-Slots** (nebeneinander auf Desktop, untereinander mobil),
16:9, mit Platzhalter-Postern im Website-Stil und Titelzeile:
- Slot A: **„Ein persönlicher Gruß"** — Sonja stellt sich vor.
- Slot B: **„Hinter den Kulissen"** — wo das Wissen wirklich liegt.
Technisch: einfache `<video>`- oder Einbettungs-Container mit Poster-Bild;
die Videodateien/Links kommen später, die Slots dürfen bis dahin ein
Platzhalter-Poster mit Play-Symbol zeigen. Kein Autoplay, kein Ton ungefragt.

**6. Kleingedrucktes unter dem Feld (Pflicht, dezent):**
- „Bitte keine persönlichen oder vertraulichen Daten in die Frage schreiben."
- Verweis auf die Datenschutzerklärung der Seite (bestehender Link).
- „Die Krake beantwortet Fragen zur App — keine Rechts- oder Steuerberatung."

---

## Der Schnittstellen-Vertrag (damit W1 und K5 zusammenpassen)

Das Fragefeld spricht per JavaScript mit einem Server-Endpunkt. Im Kopf des
Skripts steht EINE Konstante:

```js
const KRAKE_ENDPOINT = ""; // leer = Endpunkt noch nicht live
```

**Verhalten:**
- `KRAKE_ENDPOINT` leer → „Bald-Modus": Absenden zeigt freundlich
  „Die Krake zieht gerade hier ein — schauen Sie in wenigen Tagen wieder
  vorbei." Beispielfragen zeigen in diesem Modus vorbereitete statische
  Antworten (Texte liefert Sonja aus der Hilfe-Wissensbasis) — so wirkt die
  Sektion vom ersten Tag an lebendig.
- `KRAKE_ENDPOINT` gesetzt → `fetch` POST, JSON `{"frage": "<text>"}`,
  Antwort JSON `{"antwort": "<text>"}`. Antwort in die Karte.
- Fehler/Nicht-erreichbar → freundlicher Einzeiler, kein Technik-Kauderwelsch.
- Server-Meldungen (z. B. Tagesdeckel erreicht) kommen als normales
  `antwort`-Feld — die Website zeigt sie einfach an, keine Sonderlogik.

Live-Schalten ist damit später ein Handgriff: URL in die Konstante, fertig.

---

## Abnahme (Sonja, im Browser)

1. Sektion passt optisch zur bestehenden Landingpage (Farbwelt, Roboto, Ton).
2. Krake, Feld, Merksatz, drei klickbare Beispielfragen, Antwortkarte,
   zwei Video-Slots, Kleingedrucktes — alles da, mobil sauber.
3. Bald-Modus funktioniert (Endpunkt-Konstante leer): freundliche Meldung,
   statische Beispiel-Antworten.
4. Kein Wort Rechts-Zusage, keine App-Interna, keine fremden Farben im UI
   (Krake-Bild ausgenommen).
