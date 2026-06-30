# Immobiliensuche – Online-Dashboard

Gemeinsame Haus-Suche (Österreich/Südtirol) mit geteilter Datenbasis und **individuellen Bewertungen pro Person**. Läuft als Website + installierbare PWA.

## Aufbau

| Datei | Zweck |
|------|-------|
| `index.html` | Desktop-Dashboard (Liste + Karte) |
| `mobile.html` | Mobile PWA (installierbar auf Android) |
| `app.js` | Kern: Daten laden, Firebase, Filter/Sort/Konsens |
| `render.js` | Oberfläche: Filterleiste, Karten, Bewerten, Namen |
| `styles.css` | Gestaltung |
| `firebase-config.js` | Firebase-Web-Config (öffentlich, kein Geheimnis) |
| `manifest.webmanifest`, `sw.js`, `icons/` | PWA (Installation + Offline) |
| `data.json` | **Geteilte** Objektdaten, vom Lauf erzeugt |
| `bekannte_objekte.json` | Zustandsdatei des Suchlaufs (Quelle für `data.json`) |
| `kriterien.md` | Pflichtenheft für den Suchlauf |
| `tools/build_data.py` | erzeugt `data.json` aus `bekannte_objekte.json` |

## Datenfluss

```
Suchlauf  →  bekannte_objekte.json  →  tools/build_data.py  →  data.json  →  git push
                                                                              ↓
                                                                    GitHub Pages (Website)
                                                          ↙                              ↘
                              Handys/Browser laden data.json            Bewertungen ↔ Firebase
                                  (gleiche Daten für alle)               (pro Gerät/Person, getrennt)
```

Bewertungen liegen **getrennt** in Firebase und werden vom Lauf nie überschrieben. Verknüpfung Objekt↔Bewertung über `url_norm` (stabil über Läufe und Portal-Doppel hinweg).

## Nach einem Lauf veröffentlichen

```bash
python3 tools/build_data.py
git add -A
git commit -m "Lauf JJJJ-MM-TT"
git push
```

Die Lauf-Umgebung hat oft keinen Netzzugang – dann den `git push` **lokal auf deinem PC** ausführen. GitHub Pages aktualisiert die Website danach automatisch.

## PWA auf Android installieren

Website-URL im Chrome öffnen → Menü (⋮) → **„Zum Startbildschirm hinzufügen"**. Danach startet sie wie eine App; der letzte Datenstand ist offline verfügbar.

## Bewertungen

Pro Objekt: **sehr interessant / interessant / uninteressant** (erneuter Tipp = zurücknehmen). Jede Person wählt einmalig einen Namen; die Familien-Konsens-Sortierung gewichtet sehr interessant = +2, interessant = +1, uninteressant = −2.

## Firestore-Regeln

Siehe `PLAN_UND_SETUP.md`, Abschnitt 7B. Schreiben nur auf die eigene Geräte-ID; Bewertungen sind familienweit lesbar (für die Konsens-Ansicht).

## Hinweise

- „Geheime URL": Objektdaten sind für jeden mit dem Link lesbar – kein echter Zugriffsschutz.
- Die alten Dateien `daten.js`, `immobilien-dashboard.html`, `immobilien-dashboard-mobile.html` sind **abgelöst** und können gelöscht werden.
