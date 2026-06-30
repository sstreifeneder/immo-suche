# Immobiliensuche – Erweiterung: Online-Dashboard (PWA) + Bewertungen

Stand: 2026-06-30. Dieses Dokument ist der abgestimmte Umsetzungsplan **und** deine Setup-Checkliste.

---

## 1. Ziel
- Projektdateien online statt nur lokal.
- `mobile.html` von mehreren Android-Handys erreichbar, gleiche Datenbasis für alle.
- Pro Nutzer eigene Bewertungen (ohne Login), plus Sortier-/Filterfunktionen.

## 2. Architektur (entschieden)

```
Lauf (Cowork)  ──schreibt──>  bekannte_objekte.json + data.json   (lokal im Projektordner)
                                          │
                                   git push (dein PC)
                                          ▼
                              GitHub Repo + GitHub Pages
                          (App-Dateien + data.json, "geheime" URL)
                                          │
        ┌─────────────────────────────────┴───────────────────────────┐
        ▼                                                               ▼
  Android-Handys laden App + data.json von Pages          Handys lesen/schreiben Bewertungen
        (gleiche Objektbasis für alle)                    direkt bei Firebase (pro Gerät/Person)
```

- **Geteilte Objektdaten:** `data.json` im Repo, ausgeliefert über GitHub Pages.
- **App:** `index.html` (Desktop) + `mobile.html` (PWA), beide statisch, lesen `data.json`.
- **Bewertungen/Namen:** Firebase Firestore mit **anonymer Geräte-Identität** (kein Login; Gerät merkt sich, wer es ist).
- **Veröffentlichung:** Lauf aktualisiert `data.json` lokal; Push zu GitHub vom PC. Ich teste, ob ich direkt aus der Sitzung pushen kann; sonst bekommst du einen fertigen 1-Klick-Befehl.

Warum diese Trennung: Die Lauf-Umgebung hat **keinen eigenen Internetzugang** – sie kann nicht selbst online schreiben. Die Handys sprechen direkt mit Firebase und umgehen das. Bewertungen liegen getrennt von der geteilten Datei, damit ein neuer Lauf sie nie überschreibt.

## 3. Datenmodell

**`data.json`** (vom Lauf erzeugt):
```
{ "meta": { "letzter_lauf": "...", "lauf_id": "...", "anzahl": 108 },
  "objekte": [ { "url", "url_norm", "titel", "ort", "preis", "wohnflaeche",
                 "grundflaeche", "typ", "freiheits_score", "hart_ok",
                 "status", "erstmals_gesehen", "zuletzt_gesehen", "lat", "lon", ... } ] }
```
`url_norm` = stabiler Schlüssel. **Bewertungen hängen an `url_norm`** → überleben neue Läufe und Portal-Doppel.

**Firestore** (pro Nutzer):
- `users/{uid}` = `{ name }` – einmalig gewählter Anzeigename.
- `ratings/{uid}_{url_norm}` = `{ uid, name, url_norm, wert, ts }` – `wert` ∈ sehr_interessant / interessant / uninteressant.
- `views/{uid}` = `{ last_seen_ts }` – für „neu seit meinem letzten Besuch".

## 4. Features

**Geteilt (alle gleich):** Objektliste + Detailansicht, Karte (Desktop), Freiheits-Score, harte-Kriterien-Status.

**Pro Nutzer:**
- Bewerten: sehr interessant / interessant / uninteressant (Standard: unbewertet).
- Namen einmalig wählen (für die Konsens-Ansicht).
- „Neu seit meinem letzten Besuch"-Markierung.

**Sortieren/Filtern:**
- Sortieren: gefunden am (auf/ab), Freiheits-Score, Preis.
- Filter: nur letzter Lauf · neu seit letztem Besuch · Bundesland/Region · Status (aktiv/zu prüfen/entfernt) · harte Kriterien (erfüllt/teilweise/verfehlt) · meine Bewertung · „uninteressant ausblenden".
- **Familien-Konsens-Ansicht:** Favoriten nach Summe aller Bewertungen, mit Namen („Stefan: sehr interessant").

**PWA:** installierbar („Zum Startbildschirm"), offline nutzbar (letzter Stand gecacht).

_Optional später:_ Push-Benachrichtigung bei neuem Lauf.

## 5. Dateistruktur (Projektordner = Repo)
```
index.html · mobile.html · app.js · styles.css · firebase-config.js
manifest.webmanifest · sw.js · data.json · icons/
bekannte_objekte.json · kriterien.md · tools/build_data.py
berichte/ · README.md · PLAN_UND_SETUP.md · .gitignore
```
`kriterien.md` wird angepasst: Ausgabeschritt schreibt künftig `data.json` (HTML bleibt statisch, kein Neubau pro Lauf).

## 6. Was ich baue
Alles aus Abschnitt 4–5, mit Platzhalter in `firebase-config.js`. Sobald deine Firebase-Config + das Repo da sind, verdrahten und veröffentlichen wir.

---

## 7. Setup-Checkliste (dein Part)

### A) GitHub
1. Falls nötig: Account auf **github.com**.
2. Neues Repo, **unauffälliger Name** (z. B. `wohn-7q3xz`). Sichtbarkeit **public** (kostenlose Pages); echter Schutz kommt über die „geheime" URL, nicht über Privatheit.
3. Repo-Namen/URL an mich – ich verbinde ihn mit dem Projektordner, ersten Push machen wir zusammen.
4. Nach dem ersten Push: **Settings → Pages → Branch `main` / root** aktivieren, dann steht die App-URL.

### B) Firebase (nur für Bewertungen)
1. **console.firebase.google.com** → Projekt anlegen (Name egal).
2. **Build → Firestore Database → Datenbank erstellen** (Produktionsmodus, Region Europa z. B. `europe-west`).
3. **Build → Authentication → Sign-in method → „Anonymous" aktivieren.**
4. **Projekt-Einstellungen (Zahnrad) → Allgemein → App hinzufügen → Web (`</>`)** → die angezeigte **Config** kopieren (`apiKey`, `authDomain`, `projectId`, …).
5. **Firestore → Regeln** mit folgendem Text ersetzen und veröffentlichen:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{db}/documents {
    function signedIn() { return request.auth != null; }
    match /users/{uid}   { allow read: if signedIn();
                           allow write: if signedIn() && request.auth.uid == uid; }
    match /ratings/{id}  { allow read: if signedIn();
                           allow create, update, delete:
                             if signedIn() && request.resource.data.uid == request.auth.uid; }
    match /views/{uid}   { allow read, write: if signedIn() && request.auth.uid == uid; }
  }
}
```
6. Mir die **Web-Config** geben → ich trage sie in `firebase-config.js` ein.

---

## 8. Sicherheitshinweis (bewusst so gewählt)
- „Geheime URL": Objektdaten sind für **jeden mit dem Pages-Link** lesbar. Der obskure Repo-Name erschwert das Auffinden, ist aber **kein echter Zugriffsschutz**. Wenn du später echten Schutz willst, ginge das über ein Login (Phase-2-Option).
- Firestore-Regeln: Schreiben nur auf eigene Geräte-ID; Bewertungen sind familienweit lesbar (nötig für die Konsens-Ansicht).
