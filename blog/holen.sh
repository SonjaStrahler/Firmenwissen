#!/bin/bash
# Holt den wartenden Blog-Entwurf vom Pi in diesen Website-Ordner und baut die Vorschau.
# Aufruf im Website-Ordner:  bash blog/holen.sh
# Der Pi schreibt nie selbst auf GitHub. Dein Mac holt ab, dein Mac veröffentlicht.
set -e
ZIEL="Umbau-Test"
PI="moltbot"
KASTEN="/mnt/moltdata/quellenradar/blog/briefkasten"

cd "$(git rev-parse --show-toplevel)"
if [ -f .git/blog-entwurf ]; then
  echo "Es liegt schon ein geholter Entwurf hier: $(head -1 .git/blog-entwurf)"
  echo "Erst veröffentlichen (bash blog/freigeben.sh) oder wegwerfen (bash blog/verwerfen.sh)."
  exit 1
fi
if [ "$(git branch --show-current)" != "$ZIEL" ]; then
  echo "Du bist nicht auf $ZIEL. Erst wechseln:"
  echo "  git checkout $ZIEL"
  exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "Hier gibt es noch ungespeicherte Änderungen. Erst speichern, dann nochmal holen:"
  echo "  git add -A && git commit -m \"Zwischenstand\" && git push origin $ZIEL"
  exit 1
fi
git pull --quiet --ff-only origin "$ZIEL"

ID=$(ssh "$PI" "ls -1 $KASTEN/neu 2>/dev/null | head -1")
if [ -z "$ID" ]; then
  echo "Im Briefkasten liegt gerade kein Entwurf."
  exit 0
fi

TMP=$(mktemp -d)
scp -q -r "$PI:$KASTEN/neu/$ID" "$TMP/"
SLUG=$(python3 - "$TMP/$ID" <<'PY'
import json, sys
from datetime import date
from pathlib import Path
quelle = Path(sys.argv[1])
eintrag = json.loads((quelle / "eintrag.json").read_text(encoding="utf-8"))
eintrag["datum"] = date.today().isoformat()
liste_pfad = Path("blog/artikel.json")
liste = json.loads(liste_pfad.read_text(encoding="utf-8"))
if any(a["slug"] == eintrag["slug"] for a in liste):
    sys.exit(f"Den Artikel {eintrag['slug']} gibt es schon in blog/artikel.json.")
ordner = Path("blog") / eintrag["slug"]
ordner.mkdir(parents=True, exist_ok=False)
(ordner / "artikel.md").write_text((quelle / "artikel.md").read_text(encoding="utf-8"), encoding="utf-8")
liste.append(eintrag)
liste_pfad.write_text(json.dumps(liste, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(eintrag["slug"])
PY
)
rm -rf "$TMP"
python3 blog/bauen.py
ssh "$PI" "mkdir -p $KASTEN/abgeholt && mv $KASTEN/neu/$ID $KASTEN/abgeholt/"
printf '%s\n%s\n' "$ID" "$SLUG" > .git/blog-entwurf

echo ""
echo "Geholt: blog/$SLUG/artikel.md"
echo "Ansehen: in VS Code unten „Go Live“, dann /blog/$SLUG/"
echo "Ändern:  blog/$SLUG/artikel.md in VS Code, speichern."
echo "Fertig?  bash blog/freigeben.sh"
