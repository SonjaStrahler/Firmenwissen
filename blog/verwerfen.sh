#!/bin/bash
# Wirft den wartenden Blog-Entwurf weg, egal ob schon geholt oder noch beim Pi.
# Aufruf im Website-Ordner:  bash blog/verwerfen.sh
# Der Pi schreibt danach beim nächsten Lauf (06:30) einen neuen, wenn es eine passende Meldung gibt.
set -e
PI="moltbot"
KASTEN="/mnt/moltdata/quellenradar/blog/briefkasten"

cd "$(git rev-parse --show-toplevel)"
if [ -f .git/blog-entwurf ]; then
  ID=$(sed -n 1p .git/blog-entwurf)
  SLUG=$(sed -n 2p .git/blog-entwurf)
  git checkout -- blog/artikel.json blog/index.html index.html
  rm -rf "blog/$SLUG"
  ssh "$PI" "mkdir -p $KASTEN/verworfen && mv $KASTEN/abgeholt/$ID $KASTEN/verworfen/"
  rm .git/blog-entwurf
else
  ID=$(ssh "$PI" "ls -1 $KASTEN/neu 2>/dev/null | head -1")
  if [ -z "$ID" ]; then
    echo "Es gibt keinen Entwurf zum Wegwerfen."
    exit 0
  fi
  ssh "$PI" "mkdir -p $KASTEN/verworfen && mv $KASTEN/neu/$ID $KASTEN/verworfen/"
fi
echo "Weggeworfen: $ID"
