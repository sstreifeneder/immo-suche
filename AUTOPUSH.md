# Auto-Push einrichten (einmalig)

Damit neue Lauf-Ergebnisse ohne manuelles `git push` online gehen. Ein kleiner Hintergrunddienst auf deinem Mac prüft alle 5 Minuten, ob sich im Projektordner etwas geändert hat, und pusht es automatisch nach GitHub (GitHub Pages aktualisiert dann die App).

Voraussetzung: Du hast **einmal erfolgreich per Token gepusht** (die Anmeldung liegt jetzt im Schlüsselbund) — das ist erledigt.

## Installieren

```bash
# LaunchAgent kopieren und starten
cp ~/Immobiliensuche/Immobiliensuche/tools/de.immosuche.autopush.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/de.immosuche.autopush.plist 2>/dev/null
launchctl load  ~/Library/LaunchAgents/de.immosuche.autopush.plist
```

Das war's. Der Dienst läuft ab jetzt automatisch (auch nach Neustart) und pusht Änderungen innerhalb von ~5 Minuten.

## Sofort testen

```bash
bash ~/Immobiliensuche/Immobiliensuche/tools/auto_push.sh
cat ~/Library/Logs/immo-autopush.log
```

Im Log sollte „OK gepusht" stehen (oder „nichts zu tun", wenn gerade alles aktuell ist).

## Status / Stoppen

```bash
launchctl list | grep immosuche          # läuft der Dienst?
# Stoppen/entfernen:
launchctl unload ~/Library/LaunchAgents/de.immosuche.autopush.plist
rm ~/Library/LaunchAgents/de.immosuche.autopush.plist
```

## Hinweise
- Läuft nur, solange dein Mac an und du angemeldet bist (der Schlüsselbund muss entsperrt sein). Für die Cowork-Läufe ist das ohnehin der Fall.
- Der Token läuft nach der gewählten Frist ab (z. B. 90 Tage). Wenn im Log ein Push-Fehler auftaucht, einfach einmal neu `git push` mit frischem Token — danach greift der Automatismus wieder.
- Wenn der Projektordner verschoben wird, den Pfad in `tools/de.immosuche.autopush.plist` anpassen und den LaunchAgent neu laden.
