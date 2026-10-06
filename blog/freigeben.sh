#!/bin/bash
# Veröffentlicht den geholten Blog-Entwurf: bauen, speichern, hochladen.
# Aufruf im Website-Ordner:  bash blog/freigeben.sh
set -e
ZIEL="Umbau-Test"   # nach dem Live-Gang der Website: Firmenwissen

cd "$(git rev-parse --show-toplevel)"
if [ ! -f .git/blog-entwurf ]; then
  echo "Hier liegt kein geholter Entwurf. Erst holen: bash blog/holen.sh"
  exit 1
fi
if [ "$(git branch --show-current)" != "$ZIEL" ]; then
  echo "Du bist nicht auf $ZIEL. Erst wechseln: git checkout $ZIEL"
  exit 1
fi
SLUG=$(sed -n 2p .git/blog-entwurf)
TITEL=$(python3 -c "import json,sys; print(next(a['titel'] for a in json.load(open('blog/artikel.json', encoding='utf-8')) if a['slug']==sys.argv[1]))" "$SLUG")

python3 blog/bauen.py
git add blog/ index.html
git commit --quiet -m "Blog: $TITEL"
git push --quiet origin "$ZIEL"
rm .git/blog-entwurf
echo "Veröffentlicht auf $ZIEL: /blog/$SLUG/"
