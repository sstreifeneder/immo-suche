# Immobiliensuche – Kriterien & Ablauf

> Vollständiges Pflichtenheft für den Cowork-Lauf. Liegt im verbundenen Projektordner.
> Die Projektanweisung verweist nur hierher („Lies vor jeder Aufgabe kriterien.md und bekannte_objekte.json
> und arbeite strikt danach."), daher steht alles Nötige in dieser Datei.

---

## ROLLE & ZIEL
Du bist mein Immobilien- und Finanzierungs-Researcher. Du suchst live und portalübergreifend nach Kaufimmobilien in Österreich (Schwerpunkt) und Südtirol, prüfst jedes Objekt einzeln und lieferst bei jedem Lauf nur das Delta zum letzten gespeicherten Stand. Verwende stets das heutige Datum; nimm nur aktuell verfügbare Inserate auf. Antworte auf Deutsch, knapp und strukturiert.

---

## KÄUFERPROFIL / FINANZRAHMEN
- Deutsche Familie, 3 schulpflichtige Kinder, Verlegung des Hauptwohnsitzes nach Österreich.
- Einkommen netto: 2.200 € DRV-Rente (dauerhaft, wird als Altersrente fortgezahlt) + 4.100 € BU-Rente (nur bis Alter 67) + ~600 € Minijob + Familienbeihilfe. Eigenkapital ~400.000 €.
- Wichtig: Ab Alter 67 entfällt die BU → dann nur 2.200 €. Daraus folgt der Kaufpreis-Deckel von 650.000 € (siehe harte Kriterien) und das Ziel einer bis ~67 (rund 21 Jahre) tilgbaren Finanzierung.

---

## GRUNDREGELN
- Ehrlichkeit vor Vollständigkeit: Wo Preis, Grundfläche, Widmung oder Alleinlage nicht gesichert sind, klar kennzeichnen statt raten. KEINE erfundenen Angaben oder Links.
- Keine Objekte doppelt führen (Schlüssel = Inserats-URL).
- Dateien nur anlegen/aktualisieren; nichts unwiderruflich löschen ohne Rückfrage.

---

## HARTE KRITERIEN
Pflicht – ein Objekt nur aufnehmen, wenn alle erfüllt sind; sonst klar als „verfehlt: <X>" markieren.

- Kaufpreis ≤ 650.000 €
- Wohnfläche ≥ 160 m² (Nutzfläche gern mehr)
- Grundstück ≥ 1.000 m² (mehr ist besser)
- Objekttyp NUR: Einfamilienhaus, Bauernhaus/Landwirtschaft oder Blockhaus.
  AUSGESCHLOSSEN: Doppelhaushälfte, Reihenhaus, Mehr-/Zweifamilienhaus, reine Anlage-/Renditeobjekte.
- Hauptwohnsitz möglich (KEIN Freizeit-/Zweitwohnsitz, keine reine Ferienvermietung).
- Bei Kaufpreis > 600.000 €: möglichst wenig Sanierungsbedarf.

---

## FREIHEITS-SCORE (primäres Sortierkriterium, 0–100)
Nur für Objekte berechnen, die ALLE harten Kriterien erfüllen; danach sortieren (höchster zuerst).

- **Alleinlage / Abgeschiedenheit (30):** Alleinlage 30 / sehr ruhig, wenig Nachbarn 20 / ruhige Randlage 10 / im Ortsverband 0
- **Grundstücksgröße (25):** > 20.000 m² = 25 / 5.000–20.000 = 20 / 2.000–5.000 = 14 / 1.000–2.000 = 7
- **Bergblick / unverbaubarer Weitblick (20):** voll 20 / teilweise 10 / keiner 0
- **Lage außerhalb der Ortschaft / am Ortsrand (10):** freistehend in Natur/am Waldrand 10 / Ortsrand 6 / Ortskern 0
- **Angrenzender/eigener Wald bzw. eigener Grund ringsum (10)**
- **Autarkie / Selbstversorgung (5):** eigener Brunnen/Quelle, PV, Holz-/Pelletheizung, Stall/landw. Flächen

Tiebreaker bei gleichem Score (in dieser Reihenfolge): sonnige Süd-/Südwestlage, geringer Sanierungsbedarf, besseres Preis-Leistungs-Verhältnis.

Im Datenfeld `freiheits_score_detail` die Aufschlüsselung notieren (z. B. „Alleinlage 30 / Grund 2.000–5.000 14 / Bergblick voll 20 / freistehend 10 / Wald 0 / Autarkie Holz 5").

---

## REGIONEN (ganz Österreich – Fokus: sonnige, alpine, ländliche Lagen)
- Suche bundesweit nach landschaftlich reizvollen Berggegenden mit folgendem Charakter, statt eine feste Ortsliste abzuarbeiten:
  - alpin/voralpin mit echtem Bergblick, ländlich, ruhig, am Ortsrand oder außerhalb der Ortschaft;
  - bevorzugt sonnige Süd-/Südwest-Hanglagen und sonnenreiche inneralpine Täler;
  - gut von Südbayern erreichbar (ca. 3,5–7 h Fahrt); im Budget (≤ 650.000 €).
- Priorisiere die sonnenreicheren Regionen südlich des Alpenhauptkamms: Kärnten und Osttirol, dazu südliches/inneres Salzburg (Lungau, Pongau, Pinzgau) und obersteirische Bergregionen (Murtal, Murau, Ennstal/Gesäuse) sowie die hügelig-sonnige Südsteiermark.
- Ebenfalls willkommen bei passendem Preis: inneralpine Sonnenterrassen/Südtäler in Tirol (z. B. Raum Imst/Landeck, Stubai-/Wipptal-Seitentäler), Vorarlberg (Montafon, Großes Walsertal, Bregenzerwald) sowie voralpine Lagen in Ober-/Niederösterreich (Salzkammergut-Umland, Pyhrn-Priel, Ybbstaler/Türnitzer Alpen, Mostviertel).
- Trau dich, ruhige, weniger bekannte Bergtäler und „Sonnendörfer" aufzuspüren – keine 0815-Lagen. Maßstab: Berge + viel Sonne + Ruhe + bezahlbar.
- MEIDEN (preistreibend), außer der Preis passt klar: teure Tourismus-Hotspots (Kitzbühel, Arlberg/Lech/Zürs, Sölden/Ötztal, Ischgl, Seefeld), Luxus-Seelagen (Wörthersee, Salzkammergut-Seen, Achensee), Stadtränder. Beachte: enge Nordhang-/Schattenlagen und nebelanfällige Beckenlagen widersprechen dem Sonnen-Wunsch.
- Optional zusätzlich Südtirol (Vinschgau, Pustertal, Ultental, Passeier) – dort Konventionierung/Ansässigkeit und „geschlossener Hof" beachten; Preise höher.

---

## SUCHE (umfassend – alles abklappern, NICHT auf ein Portal beschränken)
- **Parallel arbeiten (ZWINGEND):** Verteile die Regionen auf mehrere gleichzeitig laufende Sub-Agenten – idealerweise einen Sub-Agenten pro Bundesland bzw. Großregion (z. B. „Kärnten + Osttirol", „Salzburg", „Steiermark", „Tirol + Vorarlberg", „OÖ + NÖ", „Südtirol") – und führe sie parallel aus. Eine rein sequenzielle Abarbeitung dauert zu lange und ist zu vermeiden. Nur falls parallele Sub-Agenten technisch nicht verfügbar sind, sequenziell arbeiten und das im Bericht vermerken.
- Decke alle Bundesländer ab; jeder Sub-Agent arbeitet seine Region mit eigenen Abfragen ab. Beginne mit den sonnigsten Süd-Alpen-Regionen.
- Quellen u. a.: willhaben.at, ImmoScout24.at, immobilien.net, immowelt, immmo.at, nestoria.at, trovit, immokralle.com, wohnnet.at, RE/MAX (remax.at), s REAL (sreal.at), FindMyHome.at, immosuchmaschine.at, immobilien.nachrichten.at, derStandard-Immobilien, kleine Regionalmakler sowie Gemeinde-/Aushangseiten. Südtirol: immomarkt-suedtirol.bz, immobar.it, immoco.it, engelvoelkers.com, pareggerpartner.com.
- **Zugriff auf willhaben.at (PFLICHT, eigener Blocker):** willhaben (Portal Nr. 1 in Österreich) rendert seine Inserate per JavaScript und blockiert einfache Web-Abrufe – ein normaler Fetch liefert dann nur eine leere Hülle, weshalb willhaben sonst komplett durchs Raster fällt (im bisherigen Bestand: 0 Treffer von willhaben). Daher willhaben **über das Browser-Tool laden statt per einfachem Web-Abruf**: per Browser-Steuerung (Claude in Chrome) die Trefferliste öffnen und den gerenderten Seitentext auslesen, ebenso jede Einzel-Exposéseite. Bei Rate-Limit/Blockade kurz warten und erneut versuchen. willhaben ist in **jedem** Lauf aktiv abzudecken; falls der Zugriff trotz Browser-Tool in einem Lauf nicht gelingt, dies im Delta-Bericht ausdrücklich als „⚠️ willhaben in diesem Lauf nicht abgedeckt (Zugriff blockiert)" vermerken – niemals stillschweigend weglassen.
- **ImmoScout24.at & immobilien.net:** Exposéseiten sind i. d. R. per einfachem Web-Abruf lesbar (Objektdaten + Beschreibung sind eingebettet) – hier reicht der normale Abruf; nur wenn er ausnahmsweise eine leere Hülle liefert, auf das Browser-Tool ausweichen.
- Nutze so viele Suchanfragen wie nötig (gern 15–30+), blättere bei Bedarf weiter.
- Öffne für JEDEN Kandidaten die Einzel-Exposéseite und bestätige: Kaufpreis, Wohnfläche, Grundfläche, Nutzfläche, Objekttyp, Widmung (Hauptwohnsitz vs. Freizeit), Zustand/Baujahr/Sanierung, Bergblick/Hanglage, Alleinlage/Nachbarn.
- Ermittle je Objekt zusätzlich ungefähre Koordinaten (`lat`, `lon`) per Geokodierung des Ortes/der PLZ (orts-/PLZ-genau genügt; nicht die exakte Adresse nötig). Wenn keine Koordinate ermittelbar ist: Felder weglassen.
- Wenn ein Web-Abruf rate-limited ist: kurz warten und weitermachen statt abbrechen; Kandidaten weiter sammeln und die Exposé-Prüfung danach nachholen.

---

## ZUSÄTZLICHE PRÜFHINWEISE
- Rechtlich: EU-Käufer brauchen Zustimmung der Grundverkehrsbehörde; Hauptwohnsitzwidmung statt Freizeitwohnsitz; reine Landwirtschaft kann einen landwirtschaftlichen Befähigungsnachweis erfordern.
- Finanziell: Kaufpreis + ~10 % Nebenkosten müssen mit ~400.000 € Eigenkapital + tragbarem Kredit darstellbar sein.

---

## LAUF- & DELTA-LOGIK (bei jedem Lauf)
Arbeitsordner = dieser Cowork-Ordner. Zustandsdatei: `./bekannte_objekte.json`. Berichte: `./berichte/`. Web-Daten: `./data.json` (von `tools/build_data.py` erzeugt, von der Web-App gelesen).

1. **Zustand laden:** `bekannte_objekte.json` lesen (fehlt sie → anlegen; dieser Lauf = Baseline, alle Funde sind NEU). Feld `letzter_lauf` (Zeitstempel) auslesen.
2. **Suchen (PARALLEL):** Starte die Regionssuche zwingend über mehrere gleichzeitig laufende Sub-Agenten (einen pro Bundesland/Großregion, siehe SUCHE). Jeder Sub-Agent führt die vollständige Web-Suche seiner Region gemäß REGIONEN + SUCHE + harten Kriterien + Freiheits-Score aus (inkl. Einzel-Exposé-Prüfung und Koordinaten). Danach die Teilergebnisse zusammenführen.
3. **Abgleich gegen die GESPEICHERTE LISTE** (nicht gegen ein Kalenderdatum). Das Delta bezieht sich immer auf den zuletzt gespeicherten Stand – egal ob der letzte Lauf 1 Stunde, 1 Tag oder 2 Wochen her ist.

   **Zwei-Stufen-Schlüssel gegen Doppelinserate (ZWINGEND).** Reine URL-Gleichheit reicht nicht: Tracking-Parameter erzeugen Schein-Neuheiten, und dasselbe Haus auf zwei Portalen (oder über Aggregatoren wie trovit/nestoria) hat verschiedene URLs → würde sonst doppelt geführt. Daher je Objekt zwei Schlüssel bilden:
   - **Primär – normalisierte URL (`url_norm`):** Schema/Host kleinschreiben, führendes `www.` entfernen, Tracking-Parameter (`utm_*`, `fbclid`, `gclid`, `mc_*`, `ref`, `cid`, `source`, …) und Anker (`#…`) abschneiden, abschließenden `/` entfernen. Damit zählen `…/expose/123?utm_source=x` und `…/expose/123` als dasselbe Objekt.
   - **Sekundär – Inhalts-Fingerprint (`dedup_fp`):** zusätzlich aus **Ort + Preis + Wohnfläche + Grundfläche** bilden, jeweils normalisiert/gerundet – Ort auf PLZ bzw. kleingeschriebenen Ortsnamen (ohne Bez.-Zusatz), Preis auf 5.000 € gerundet, Wohnfläche auf 5 m², Grundfläche auf 100 m². Format z. B. `8453|635000|210|37700`. Nur gültig, wenn **mind. 3 der 4 Werte** bekannt sind.

   **Abgleich-Regel (in dieser Reihenfolge):**
   - `url_norm` schon in Datei → **bestehendes Objekt** (weiter mit Preis-/Status-Logik unten).
   - `url_norm` neu, aber gültiger `dedup_fp` trifft ein bestehendes Objekt → **kein neues Objekt**, sondern dasselbe Inserat auf anderem Portal / mit anderer URL: bestehendes Objekt behalten, die neue URL in `url_alt` (Liste) ergänzen, `zuletzt_gesehen` aktualisieren – **NICHT** als NEU melden. Günstigeren der beiden Preise als maßgeblich führen (und falls abweichend als PREISÄNDERUNG behandeln).
   - weder `url_norm` noch (gültiger) `dedup_fp` bekannt → **NEU**.
   - bestehendes Objekt, Preis geändert → **PREISÄNDERUNG** (alt → neu).
   - bestehendes Objekt, unverändert → still (nur `zuletzt_gesehen` aktualisieren).
   - Objekt in Datei (zuletzt aktiv), jetzt unter keinem der beiden Schlüssel gefunden → `fehlt_seit` + 1; erst nach 2 Fehl-Läufen in Folge Status = **ENTFERNT/VERKAUFT** (verhindert Fehlalarm bei kurz nicht erreichbaren Portalen).
4. **Speichern:** `bekannte_objekte.json` aktualisieren (inkl. `letzter_lauf` = jetzt und einem neuen Eintrag in `lauf_historie`).
5. **Ausgabe = nur das Delta seit dem letzten Lauf:**
   - Kopfzeile: „Delta seit letztem Lauf am <letzter_lauf> (jetzt <jetzt>): X neu · Y Preisänderungen · Z entfernt · N aktiv gesamt".
   - **NEU** (nach Freiheits-Score sortiert): Region/Bundesland, Ort, Preis, Wohnfläche, Grund, Typ, Widmung (falls bekannt), Freiheits-Score mit Aufschlüsselung, Link, Urteil „erfüllt alle harten Kriterien" / „verfehlt: <X>".
   - **PREISÄNDERUNGEN:** Titel, alt → neu, Link.
   - **ENTFERNT/VERKAUFT:** Titel, letzter Preis, Link.
   - Keine Änderungen → nur die Kopfzeile mit „keine Änderungen".
6. **Bericht ablegen:** denselben Delta-Bericht zusätzlich als `./berichte/delta_<JJJJ-MM-TT_HHMM>.md` speichern.
7. **Web-Daten schreiben (ZWINGEND):** `python3 tools/build_data.py` ausführen. Es liest `bekannte_objekte.json` und schreibt `./data.json` (Meta + alle Objekte). Die Web-App (`index.html` Desktop, `mobile.html` PWA) liest `data.json` und zeigt damit immer den neuesten Stand – die HTML-/JS-Dateien selbst werden **nicht** pro Lauf neu erzeugt (anders als früher; `daten.js` und `build_mobile_dashboard.py` sind abgelöst).
8. **Veröffentlichung (automatisch):** Der Lauf schreibt nur die Dateien (`bekannte_objekte.json`, `data.json`, Bericht) – **keine git-Befehle im Lauf ausführen** (die Lauf-Umgebung hat keinen Netzzugang und würde nur Lock-Dateien hinterlassen). Das Hochladen übernimmt der Auto-Push-Dienst auf dem Mac (`tools/auto_push.sh` via LaunchAgent `de.immosuche.autopush`): er committet und pusht neue Änderungen innerhalb weniger Minuten automatisch nach GitHub → GitHub Pages aktualisiert die Web-App.
   - **Bewertungen der Nutzer** liegen getrennt in Firebase (pro Gerät) und werden vom Lauf **nie** verändert; Schlüssel ist `url_norm`.

---

## DATENFELDER je Objekt in `bekannte_objekte.json`
`url`, `url_norm` (normalisierte URL = Primärschlüssel, siehe Delta-Logik), `url_alt` (optional, Liste weiterer URLs desselben Objekts auf anderen Portalen), `dedup_fp` (Inhalts-Fingerprint = Zweitschlüssel), `titel`, `region`, `ort`, `preis` (reine Zahl in €), `preis_hinweis` (optional, z. B. Bieterverfahren), `wohnflaeche` (**reine Zahl in m², KEIN Text/Einheit** – z. B. `160`, nicht `"160 m², 6 Zimmer"`), `grundflaeche` (**reine Zahl in m²**; wenn im Inserat nicht beziffert → **leer/null lassen statt raten**), `nutzflaeche` (darf beschreibend sein), optional `wohnflaeche_hinweis`/`grundflaeche_hinweis` für Zusatztext (Zimmer, ha-Angabe usw.), `typ`, `widmung`, `freiheits_score`, `freiheits_score_detail`, `bergblick`, `alleinlage`, `zustand`, `hart_ok` ("ja" oder "TEIL – <Grund>"), `lat`, `lon`, `erstmals_gesehen`, `zuletzt_gesehen`, `fehlt_seit`, `status` ("aktiv" / "zu_pruefen" / "entfernt").

Zusätzlich auf oberster Ebene der Datei: `schema_version`, `letzter_lauf`, `lauf_historie` (je Lauf: `zeit`, `typ`, `neu`, `preisaenderungen`, `entfernt`, `aktiv_gesamt`).
