#!/bin/bash
# Immobiliensuche – Auto-Push
# Committet & pusht neue Lauf-Ergebnisse automatisch nach GitHub.
# Wird per LaunchAgent (de.immosuche.autopush) alle paar Minuten aufgerufen.
# Nutzt die im macOS-Schlüsselbund gespeicherte GitHub-Anmeldung (osxkeychain).
set -u

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$HOME/Library/Logs/immo-autopush.log"
STAMP="$REPO/.git/immo-last-push"   # Zeitstempel des letzten Pushes (liegt in .git/, nicht versioniert)
COOLDOWN_MIN=10                     # Mindestabstand zwischen zwei Pushes (verhindert ueberlappende Pages-Deployments)
cd "$REPO" || exit 1

# Stale Git-Locks aus der Cowork-/Mount-Umgebung entfernen (sonst blockieren sie git)
rm -f .git/index.lock .git/HEAD.lock .git/objects/maintenance.lock 2>/dev/null

# Fehlende Objektbilder lokal laden und data.json neu erzeugen (best effort, braucht Netz)
python3 "$REPO/tools/fetch_images.py" >>"$LOG" 2>&1 || true
python3 "$REPO/tools/build_data.py"   >>"$LOG" 2>&1 || true

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

# Push-Cooldown: nur pushen, wenn der letzte Push mind. COOLDOWN_MIN Minuten her ist.
# Ein Immobilien-Lauf erzeugt oft mehrere Commits kurz hintereinander (Daten zuerst,
# nachgeladene Bilder ein paar Minuten spaeter). Ohne Cooldown loest JEDER Push ein eigenes
# GitHub-Pages-Deployment aus; ein neueres verdraengt dann das noch laufende aeltere, das
# daraufhin "Deployment failed, try again later" meldet. Mit dem Cooldown werden mehrere
# Commits zu EINEM Push (= EIN Deployment) gebuendelt und Deployments ueberlappen sich nicht.
now=$(date +%s)
if [ -f "$STAMP" ]; then
  last="$(cat "$STAMP" 2>/dev/null || echo 0)"
  [ -z "$last" ] && last=0
  age_min=$(( (now - last) / 60 ))
  if [ "$age_min" -lt "$COOLDOWN_MIN" ]; then
    echo "$(date '+%Y-%m-%d %H:%M')  Cooldown aktiv (${age_min}/${COOLDOWN_MIN} min) – $AHEAD Commit(s) offen, Push im naechsten Zyklus gebuendelt" >>"$LOG"
    exit 0
  fi
fi

if git push origin main >>"$LOG" 2>&1; then
  date +%s > "$STAMP"
  echo "$(date '+%Y-%m-%d %H:%M')  OK gepusht ($AHEAD Commit(s))" >>"$LOG"
else
  # Remote evtl. voraus -> rebasen und erneut versuchen
  if git pull --rebase origin main >>"$LOG" 2>&1 && git push origin main >>"$LOG" 2>&1; then
    date +%s > "$STAMP"
    echo "$(date '+%Y-%m-%d %H:%M')  OK nach rebase" >>"$LOG"
  else
    echo "$(date '+%Y-%m-%d %H:%M')  FEHLER push – siehe Log oben" >>"$LOG"
  fi
fi
