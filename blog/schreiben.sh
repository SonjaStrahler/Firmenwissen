#!/bin/bash
# Lässt den Pi einen Blog-Entwurf aus einer Quelle schreiben, die du selbst ausgesucht hast.
# Aufruf im Website-Ordner:  bash blog/schreiben.sh https://…
set -e
LINK="$1"
if [ -z "$LINK" ]; then
  echo "Der Link fehlt. Aufruf: bash blog/schreiben.sh https://…"
  exit 1
fi
if ! [[ "$LINK" =~ ^https?://[^[:space:]\'\"\;\`\$\\]+$ ]]; then
  echo "Das sieht nicht wie ein Link aus: $LINK"
  exit 1
fi
echo "Der Pi liest die Quelle und schreibt. Das dauert 1 bis 3 Minuten …"
ssh moltbot "cd /home/molty/.openclaw/quellenradar && .venv/bin/python blogschreiber.py '$LINK'" | tail -1
echo "Die Mail mit dem Entwurf ist unterwegs. Dann wie immer: bash blog/holen.sh"
