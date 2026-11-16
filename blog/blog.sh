#!/bin/bash
# Ein Befehl für den ganzen Blog, von überall im Terminal:
#   blog frei          ältesten Entwurf holen und sofort online stellen (wenn er dir so gefällt)
#   blog holen         ältesten Entwurf holen und in VS Code öffnen (wenn du etwas ändern willst)
#   blog frei          danach: deine Änderung online stellen
#   blog weg           ältesten Entwurf wegwerfen
#   blog schreib LINK  aus deiner eigenen Quelle einen Entwurf schreiben lassen
#   blog stand         zeigt alles, was gerade wartet
#   blog live          schiebt Umbau-Test auf die Website (Backup vorher), macht blog frei automatisch
# Seit 11.11.2026 (Vorrat 3): Die Maschine schreibt weiter, bis 3 Entwürfe auf dich
# warten. Mehrere wartende arbeitest du mit mehreren blog frei / blog weg ab, ältester zuerst.
WEB="$HOME/Documents/Website_Firmenwissen-retten_I"
cd "$WEB" 2>/dev/null || { echo "Website-Ordner nicht gefunden: $WEB"; exit 1; }
KASTEN_NEU="/mnt/moltdata/quellenradar/blog/briefkasten/neu"
kasten_rest() {
  R=$(ssh moltbot "ls -1 $KASTEN_NEU 2>/dev/null | wc -l" 2>/dev/null | tr -d ' ')
  case "$R" in
    "")  ;;
    0)   echo "Briefkasten leer. Der Pi sucht wieder morgen um 6:30." ;;
    1)   echo "Noch 1 Entwurf im Briefkasten. Weiter mit: blog frei · blog holen · blog weg" ;;
    *)   echo "Noch $R Entwürfe im Briefkasten. Weiter mit: blog frei · blog holen · blog weg" ;;
  esac
}
case "$1" in
  holen)
    bash blog/holen.sh ;;
  frei)
    if [ ! -f .git/blog-entwurf ]; then
      BLOG_OHNE_EDITOR=1 bash blog/holen.sh || exit 1
    fi
    [ -f .git/blog-entwurf ] && bash blog/freigeben.sh && kasten_rest ;;
  weg)
    bash blog/verwerfen.sh && kasten_rest ;;
  schreib)
    bash blog/schreiben.sh "$2" ;;
  live)
    bash blog/live.sh ;;
  stand)
    [ -f .git/blog-entwurf ] && {
      echo "Hier geholt, noch nicht online: blog/$(sed -n 2p .git/blog-entwurf)/artikel.md"
      echo "Online stellen: blog frei    Wegwerfen: blog weg"
    }
    L=$(ssh moltbot "ls -1 $KASTEN_NEU 2>/dev/null")
    if [ -n "$L" ]; then
      N=$(printf '%s\n' "$L" | wc -l | tr -d ' ')
      if [ "$N" = "1" ]; then echo "Beim Pi wartet 1 Entwurf:"; else echo "Beim Pi warten $N Entwürfe (ältester zuerst):"; fi
      printf '%s\n' "$L" | sed 's/^/  /'
      echo "So online: blog frei    Erst ändern: blog holen    Wegwerfen: blog weg"
      echo "(blog frei/holen/weg nehmen immer den ältesten. Voll ist der Vorrat bei 3.)"
    elif [ ! -f .git/blog-entwurf ]; then
      echo "Nichts wartet. Der Pi sucht wieder morgen um 6:30."
    fi ;;
  *)
    echo "blog frei          ältesten Entwurf online stellen (holt ihn vorher, wenn nötig)"
    echo "blog holen         ältesten Entwurf holen und in VS Code öffnen, danach: blog frei"
    echo "blog weg           ältesten Entwurf wegwerfen"
    echo "blog schreib LINK  Entwurf aus deiner eigenen Quelle"
    echo "blog stand         zeigt alles, was gerade wartet"
    echo "blog live          schiebt Umbau-Test auf die Website (mit Backup vorher)" ;;
esac
