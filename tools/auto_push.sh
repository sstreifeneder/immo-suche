#!/bin/bash
# Immobiliensuche – Auto-Push
# Committet & pusht neue Lauf-Ergebnisse automatisch nach GitHub.
# Wird per LaunchAgent (de.immosuche.autopush) alle paar Minuten aufgerufen.
# Nutzt die im macOS-Schlüsselbund gespeicherte GitHub-Anmeldung (osxkeychain).
set -u

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$HOME/Library/Logs/immo-autopush.log"
cd "$REPO" || exit 1

# Stale Git-Locks aus der Cowork-/Mount-Umgebung entfernen (sonst blockieren sie git)
rm -f .git/index.lock .git/HEAD.lock .git/objects/maintenance.lock 2>/dev/null

# Geänderte Dateien committen (falls vorhanden)
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "Auto-Push: Lauf-Aktualisierung $(date '+%Y-%m-%d %H:%M')" >>"$LOG" 2>&1
fi

# Nichts zu pushen? (weder neue Commits noch offene Änderungen) -> fertig
AHEAD="$(git rev-list '@{u}..HEAD' --count 2>/dev/null || echo 1)"
if [ "$AHEAD" = "0" ]; then
  exit 0
fi

if git push origin main >>"$LOG" 2>&1; then
  echo "$(date '+%Y-%m-%d %H:%M')  OK gepusht" >>"$LOG"
else
  # Remote evtl. voraus -> rebasen und erneut versuchen
  if git pull --rebase origin main >>"$LOG" 2>&1 && git push origin main >>"$LOG" 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M')  OK nach rebase" >>"$LOG"
  else
    echo "$(date '+%Y-%m-%d %H:%M')  FEHLER push – siehe Log oben" >>"$LOG"
  fi
fi
