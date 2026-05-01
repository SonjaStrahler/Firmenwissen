# Firmenwissen retten — Workflow & Dokumentation

## 📍 Projektübersicht

- **Live-Website:** https://firmenwissen-retten.de
- **Repository:** https://github.com/SonjaStrahler/Firmenwissen
- **Server:** Proxmox Container 102 (192.168.178.102)
- **Server-Pfad:** /var/www/firmenwissen

### Temporärer Hinweis: INQA-/Fördertexte ausgeblendet

Die INQA-/80%-Förderhinweise sind in `index.html` nicht gelöscht, sondern vorübergehend mit der CSS-Klasse `funding-temporarily-hidden` optisch unsichtbar gemacht. Zusätzlich wurden die Meta-Description und Open-Graph-Description neutral formuliert, damit Suchmaschinen keine ungeprüften Förderaussagen als Vorschau anzeigen.

Zum Wieder-Einblenden nach Genehmigung:
1. In `index.html` nach `funding-temporarily-hidden` suchen.
2. Die Klasse an den gewünschten Elementen entfernen.
3. Die Meta-Texte im `<head>` bei Bedarf wieder um die genehmigte Förderaussage ergänzen.

---

## 📂 Wo liegt das Projekt?

**Lokaler Arbeitsordner:**
```
~/Documents/Website_Firmenwissen-retten
```

**Quick-Check:**
```bash
pwd
# Sollte zeigen: /Users/Sonja/Documents/Website_Firmenwissen-retten

git remote -v
# Sollte zeigen: https://github.com/SonjaStrahler/Firmenwissen.git
```

---

## 🌳 Branch-Struktur

```
Test-Firmenwissen  →  Firmenwissen (LIVE!)  →  Retten-Firmenwissen (Backup)
    (Arbeiten)          (Server/Proxmox)          (Sicherung)
```

- **Test-Firmenwissen:** Hier arbeitest du aktiv
- **Firmenwissen:** LIVE-Website! Der Server zieht hieraus.
- **Retten-Firmenwissen:** Backup für stabile Versionen

**Branch wechseln:**
```bash
git checkout Test-Firmenwissen
git checkout Firmenwissen
git checkout Retten-Firmenwissen
```

**Aktuellen Branch anzeigen:**
```bash
git branch
```

---

## 🚀 Täglicher Workflow

### 1. Morgens — Arbeit beginnen

```bash
cd ~/Documents/Website_Firmenwissen-retten
git checkout Test-Firmenwissen
git pull origin Test-Firmenwissen
git status
```

### 2. Während der Arbeit — Speichern (CMD+S nicht vergessen!)

Nach jedem Arbeitsblock (alle 30-60 Min):

```bash
git status
git add .
git commit -m "Beschreibung was du gemacht hast"
git push origin Test-Firmenwissen
```

### 3. Live schalten — SCHRITT FÜR SCHRITT!

⚠️ WICHTIG: KEIN All-in-One Befehl! Immer Schritt für Schritt!

**Schritt 1:** Zu Firmenwissen wechseln
```bash
git checkout Firmenwissen
```

**Schritt 2:** Aktualisieren
```bash
git pull origin Firmenwissen
```

**Schritt 3:** Test-Branch mergen
```bash
git merge Test-Firmenwissen
```

Falls Konflikt:
```bash
git checkout --theirs [dateiname]
git add [dateiname]
git commit -m "Merge Konflikt gelöst"
```

**Schritt 4:** Zu GitHub pushen
```bash
git push origin Firmenwissen
```

**Schritt 5:** Server aktualisieren
```bash
# Auf Proxmox Host:
pct enter 102

# Im Container:
/root/update-firmenwissen.sh

exit
```

**Schritt 6:** Zurück zum Arbeits-Branch
```bash
git checkout Test-Firmenwissen
```

### 4. Abends — Backup in Retten-Firmenwissen

```bash
git checkout Firmenwissen
git pull origin Firmenwissen
git checkout Retten-Firmenwissen
git pull origin Retten-Firmenwissen
git merge Firmenwissen
git push origin Retten-Firmenwissen
git checkout Test-Firmenwissen
```

---

## 🆘 Häufige Probleme & Lösungen

### Problem 1: "assume-unchanged" — Änderungen kommen nicht an

**Diagnose auf dem Mac:**
```bash
git ls-files -v | grep "^h"
```

**Lösung auf dem Mac:**
```bash
git update-index --no-assume-unchanged [dateiname]
```

**Diagnose + Lösung auf dem Server:**
```bash
pct enter 102
cd /var/www/firmenwissen
git ls-files -v | grep "^h"
git update-index --no-assume-unchanged [dateiname]
git reset --hard origin/Firmenwissen
```

### Problem 2: Merge Conflict

```bash
git checkout --theirs [dateiname]
git add [dateiname]
git commit -m "Merge Konflikt gelöst"
```

Oder in VS Code:
1. Datei öffnen
2. Konflikte mit `<<<<<<< HEAD` und `>>>>>>>` finden
3. Entscheiden welche Version du willst
4. Marker löschen, speichern
5. `git add .` und `git commit`

### Problem 3: "Your local changes would be overwritten"

```bash
git add .
git commit -m "Speichere aktuelle Änderungen"
# Dann nochmal den Merge/Pull versuchen
```

### Problem 4: Website zeigt alte Inhalte trotz Push

```bash
pct enter 102
cd /var/www/firmenwissen
git pull origin Firmenwissen
exit
```

Dann Browser: **CMD + Shift + R** (Hard Refresh)

### Problem 5: Ich bin im falschen Branch!

```bash
git branch
# Der aktive hat ein *

git checkout Test-Firmenwissen
```

---

## 🔍 Wichtige Git-Befehle (Cheat Sheet)

```bash
# Status & Info
pwd                          # Wo bin ich?
git status                   # Was hat sich geändert?
git branch                   # Welche Branches? (* = aktuell)
git log --oneline -5         # Letzte 5 Commits
git remote -v                # GitHub-Verbindung

# Branch wechseln
git checkout [branch-name]   # Zu Branch wechseln

# Änderungen speichern
git add .                    # Alle Änderungen
git add [datei]              # Nur eine Datei
git commit -m "Nachricht"    # Commit erstellen
git push origin [branch]     # Zu GitHub hochladen

# Änderungen holen
git pull origin [branch]     # Neueste Version holen

# Mergen
git merge [branch-name]      # Branch mergen

# Rückgängig machen
git checkout -- [datei]      # Datei zurücksetzen
git reset --hard HEAD        # Alles zurücksetzen
```

---

## 🖥️ Server-Befehle (Proxmox)

```bash
# In Container einloggen
pct enter 102

# Website updaten
/root/update-firmenwissen.sh

# Oder manuell:
cd /var/www/firmenwissen
git pull origin Firmenwissen

# Git-Status checken
git log --oneline -3
git status

# Nginx neu laden (falls nötig)
systemctl reload nginx
systemctl status nginx
```

---

## 📞 Brand-Farben

```
Blau:        #61b6e2
Pink/Lila:   #ca72da
Orange/Gelb: #feb365
Hell:        #f5f4f7
Dunkel:      #000000
```

---

## 🔗 Wichtige Links

- **GitHub:** https://github.com/SonjaStrahler/Firmenwissen
- **Live-Website:** https://firmenwissen-retten.de
- **Nginx Proxy Manager:** Container 101 (http://192.168.178.101:81)
- **Proxmox Host:** 192.168.178.50

---

## ✅ Checkliste vor dem Live-Schalten

- [ ] Alle Änderungen committed und gepusht?
- [ ] `git status` zeigt "nothing to commit"?
- [ ] Lokal getestet (Live Server)?
- [ ] Keine offensichtlichen Fehler?
- [ ] Bereit für Live?

**Dann → Schritt für Schritt zu Firmenwissen mergen!**

---

## 🎯 Wichtige Regeln

1. **IMMER Schritt-für-Schritt mergen** — Keine All-in-One-Befehle!
2. **Nur in Test-Firmenwissen arbeiten** — Keine extra Feature-Branches!
3. **Nach jedem Arbeitsblock pushen** — Nichts geht verloren!
4. **assume-unchanged checken** — Bei Problemen mit `git ls-files -v | grep "^h"`
5. **Firmenwissen = Live** — Was in Firmenwissen ist, ist online!
6. **Retten-Firmenwissen als Backup** — Abends mergen!
