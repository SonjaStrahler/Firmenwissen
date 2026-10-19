#!/bin/bash
# Bringt den Stand von Umbau-Test auf die Website, mit Sicherung vorher.
#   1. Retten-Firmenwissen (Backup) bekommt den Stand, der gerade live ist.
#   2. Firmenwissen (live, holt sich der Proxmox) bekommt den Stand von Umbau-Test.
# Geht nur vorwärts. Hat Live etwas, das Umbau-Test nicht hat, bricht es ab und ändert nichts.
# Liegt auf Umbau-Test noch etwas anderes als Blog, wird es gezeigt und erst nach „j“ mitgenommen.
set -e
BAU="Umbau-Test"; LIVE="Firmenwissen"; BACKUP="Retten-Firmenwissen"
cd "$(git rev-parse --show-toplevel)"
git fetch --quiet origin "$BAU" "$LIVE" "$BACKUP"
if ! git merge-base --is-ancestor "origin/$LIVE" "origin/$BAU"; then
  echo "Halt: Auf $LIVE liegt etwas, das in $BAU fehlt. Nichts geändert. Bitte Claude fragen."
  exit 1
fi
if [ "$(git rev-parse "origin/$LIVE")" = "$(git rev-parse "origin/$BAU")" ]; then
  echo "Die Website ist schon auf dem neuesten Stand."
  exit 0
fi
# Was ginge mit online, das kein Blog ist? Das zeigen wir und fragen.
ANDERES=$(git log --reverse --format='%ad  %s' --date=format:'%d.%m.' "origin/$LIVE..origin/$BAU" | grep -v '  Blog' || true)
if [ -n "$ANDERES" ]; then
  echo "Mit online gehen würde auch das hier (kein Blog):"
  echo "$ANDERES" | sed 's/^/  /'
  printf "Soll das mit online? Ja = j, Nein = n: "
  read -r ANTWORT
  if [ "$ANTWORT" != "j" ]; then
    echo "Nichts geändert. Die Website bleibt, wie sie ist. Später nochmal: blog live"
    exit 0
  fi
fi
if [ "$(git rev-parse "origin/$LIVE^{tree}")" != "$(git rev-parse "origin/$BACKUP^{tree}")" ]; then
  SICHERUNG=$(git commit-tree "origin/$LIVE^{tree}" -p "origin/$BACKUP" -p "origin/$LIVE" -m "Backup: Live-Stand vom $(date +%d.%m.%Y)")
  git push --quiet origin "$SICHERUNG:refs/heads/$BACKUP"
  echo "Gesichert: der bisherige Live-Stand liegt in $BACKUP."
fi
git push --quiet origin "origin/$BAU:refs/heads/$LIVE"
echo "Live geschoben: $LIVE hat jetzt den Stand von $BAU."
echo "Auf der Website steht es nach dem nächsten täglichen Update des Proxmox."
