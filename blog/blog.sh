#!/bin/bash
# Ein Befehl für den ganzen Blog, von überall im Terminal:
#   blog frei          Entwurf holen und sofort online stellen (wenn er dir so gefällt)
#   blog holen         Entwurf holen und in VS Code öffnen (wenn du etwas ändern willst)
#   blog frei          danach: deine Änderung online stellen
#   blog weg           Entwurf wegwerfen
#   blog schreib LINK  aus deiner eigenen Quelle einen Entwurf schreiben lassen
#   blog stand         zeigt, was gerade wartet
WEB="$HOME/Documents/Website_Firmenwissen-retten_I"
cd "$WEB" 2>/dev/null || { echo "Website-Ordner nicht gefunden: $WEB"; exit 1; }
case "$1" in
  holen)
    bash blog/holen.sh ;;
  frei)
    if [ ! -f .git/blog-entwurf ]; then
      BLOG_OHNE_EDITOR=1 bash blog/holen.sh || exit 1
    fi
    [ -f .git/blog-entwurf ] && bash blog/freigeben.sh ;;
  weg)
    bash blog/verwerfen.sh ;;
  schreib)
    bash blog/schreiben.sh "$2" ;;
  stand)
    if [ -f .git/blog-entwurf ]; then
      echo "Hier geholt, noch nicht online: blog/$(sed -n 2p .git/blog-entwurf)/artikel.md"
      echo "Online stellen: blog frei    Wegwerfen: blog weg"
    else
      W=$(ssh moltbot "ls -1 /mnt/moltdata/quellenradar/blog/briefkasten/neu 2>/dev/null | head -1")
      if [ -n "$W" ]; then
        echo "Beim Pi wartet ein Entwurf: $W"
        echo "So online: blog frei    Erst ändern: blog holen    Wegwerfen: blog weg"
      else
        echo "Nichts wartet. Der Pi sucht wieder morgen um 6:30."
      fi
    fi ;;
  *)
    echo "blog frei          Entwurf online stellen (holt ihn vorher, wenn nötig)"
    echo "blog holen         Entwurf holen und in VS Code öffnen, danach: blog frei"
    echo "blog weg           Entwurf wegwerfen"
    echo "blog schreib LINK  Entwurf aus deiner eigenen Quelle"
    echo "blog stand         zeigt, was gerade wartet" ;;
esac
