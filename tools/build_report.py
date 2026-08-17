#!/usr/bin/env python3
"""build_report.py – erzeugt den Delta-Bericht (Markdown) aus delta_result.json."""
import json, os, sys

CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/immolauf/proj/outputs"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = json.load(open(os.path.join(CAND_DIR, "delta_result.json"), encoding="utf-8"))

def fmt_preis(p, hinweis=None):
    if p in (None, 0, ""):
        s = "Preis auf Anfrage"
    else:
        s = f"{int(p):,} €".replace(",", ".")
    if hinweis:
        s += f" ({hinweis})"
    return s

def fmt_flaeche(v):
    if v in (None, 0, ""):
        return "–"
    return f"{int(v):,} m²".replace(",", ".")

lines = []
kopf = (f"# Delta-Bericht Immobilien-Lauf\n\n"
        f"**Delta seit letztem Lauf am {r['prev_letzter_lauf']} (jetzt {r['now']}): "
        f"{r['neu']} neu · {r['preisaenderungen']} Preisänderungen · 0 entfernt · "
        f"{r['aktiv_gesamt']} aktiv gesamt** "
        f"(gesamt geführt {r['gesamt_objekte']}, davon {r['zu_pruefen']} zu prüfen)\n\n"
        f"Suche: 6 Großregionen parallel über Sub-Agenten (Kärnten+Osttirol 33, Salzburg 6, Steiermark 34, Tirol+Vorarlberg 4, OÖ+NÖ 31, Südtirol 12 = 120 Kandidaten, 62 Volltreffer) + **willhaben via Chrome-Browser** (Kärnten & Steiermark, Häuser ≤900k & Grundstücke ≤200k nach Aktualität; Delta ~4 Tage seit letztem Lauf → 1.530 Anzeigen bis Cutoff 13.08. durchgeblättert (rows=90); nach Listen- und Titel-Vorfilter 332 Kandidaten einzeln Exposé-geprüft (0 Fehlversuche) und 230 übernommen, davon nach Abgleich gegen 872 bekannte willhaben-IDs **52 neu**; die 178 bereits bekannten Anzeigen wurden zur Preis- und Sichtprüfung mitgeführt).\n\n"
        f"Bei willhaben-Häusern wurde die echte Grundstücksgröße einzeln aus dem Exposé-Detail (`PLOT/AREA`) verifiziert, bei Grundstücken die Widmung aus dem Exposé-Text (`DESCRIPTION`) belegt; 79 Häuser mit Grund <1.000 m² bzw. ohne belegbare Grundfläche und 23 Grundstücke ohne Bauland-Beleg sind nicht übernommen, 13 weitere Grundstücke mit nur generischem Bauland-Hinweis im Python-Post-Pass auf \"TEIL – Widmung ungesichert\" herabgestuft.\n\n"
        f"Häuser 650–900k und Grundstücke 150–200k sind als Near-Miss \"TEIL – verfehlt: Preis\" geführt (Zielpreise 650k bzw. 150k); Objekte mit Freizeit-/Zweitwohnsitz-Widmung als \"TEIL – verfehlt: Widmung\", Zwei-/Mehrfamilienhäuser, Bungalows und Gewerbe-/Anlageobjekte als \"TEIL – verfehlt: Typ\". ⚠️ **Tirol+Vorarlberg 0 Volltreffer** (Bauland durchweg 250–800 €/m², nichts >1.000 m² unter 200.000 €; Häuser mit großem Grund fast immer Mehrfamilien-/Anlageobjekte oder >900.000 €). Bester Near-Miss: Nassereith 535.000 € / 158,7 m² / 1.101 m² – verfehlt die Wohnfläche um 1,3 m². ⚠️ **Salzburg nur 1 Volltreffer**, Klasse B weiterhin komplett leer (günstigstes Bauland >1.000 m² = 240.000 € in Unternberg); Pongau/Pinzgau faktisch komplett über Budget. ⚠️ **Südtirol nur 1 Volltreffer** (Grundflächen werden systematisch nicht angegeben, Bauland kleinparzelliert/agrarisch oder für Ansässige reserviert, mehrfach geschlossener Hof/Konventionierung). ℹ️ In OÖ/NÖ ist der Engpass die Grundfläche (viele 800–980 m²), nicht der Preis; Pyhrn-Priel/Stodertal derzeit leergefegt. ⚠️ Blockiert/eingeschränkt: trovit + nestoria HTTP 401; derStandard-Immobilien 403/JS-only; remax.at und immoversum.com robots-gesperrt; immosuchmaschine.at Grundstücks-Listen HTTP 410; ImmoScout24-Paginierung und mehrere Regionsseiten 404; laendleimmo.at-Pfade 404; sreal.at ohne nutzbare Trefferliste; dolomitenmarkt.it/pareggerpartner.com ohne Inserats-Markup; immoco.it 404. "
        f"ℹ️ Technischer Hinweis: die Geräte-Brücke zum Mac riss während des ersten willhaben-Datentransfers ab und Chrome wurde neu gestartet – der willhaben-Scan wurde danach vollständig wiederholt. "
        f"Dubletten zusammengeführt: {r['dubletten']} (Zwei-Stufen-Dedup url_norm + Inhalts-Fingerprint im Merge, plus Post-Merge-Check über Ortsname/Preis/Grund und ortsunabhängig gegen den Altbestand). Über Aufnahme-Obergrenze verworfen: {r['verworfen']}.\n")
lines.append(kopf)

lines.append("## NEU (nach Freiheits-Score sortiert)\n")
if not r["neu_liste"]:
    lines.append("_keine neuen Objekte_\n")
for o in r["neu_liste"]:
    urteil = "erfüllt alle harten Kriterien" if (o.get("hart_ok") or "").strip().lower() == "ja" else o.get("hart_ok")
    titel = o.get("titel", "").strip()
    lines.append(f"### {o.get('freiheits_score')} · {titel}")
    lines.append("")
    lines.append(f"- **Region:** {o.get('region','–')} · **Ort:** {o.get('ort','–')}")
    lines.append(f"- **Preis:** {fmt_preis(o.get('preis'), o.get('preis_hinweis'))}")
    lines.append(f"- **Wohnfläche:** {fmt_flaeche(o.get('wohnflaeche'))} · **Grund:** {fmt_flaeche(o.get('grundflaeche'))} · **Typ:** {o.get('typ','–')}")
    if o.get("widmung"):
        lines.append(f"- **Widmung:** {o.get('widmung')}")
    lines.append(f"- **Freiheits-Score {o.get('freiheits_score')}:** {o.get('freiheits_score_detail','')}")
    lines.append(f"- **Urteil:** {urteil}")
    lines.append(f"- **Link:** {o.get('url')}")
    lines.append("")

lines.append("## PREISÄNDERUNGEN\n")
if not r["preisaenderung_liste"]:
    lines.append("_keine_\n")
else:
    for p in r["preisaenderung_liste"]:
        lines.append(f"- {p['titel']}: {int(p['alt']):,} € → {int(p['neu']):,} € · {p['url']}".replace(",", "."))
    lines.append("")

lines.append("## ENTFERNT / VERKAUFT\n")
lines.append("_keine (additiver Neufund-Lauf ohne vollständige Verfügbarkeits-Nachprüfung)_\n")

out = os.path.join(ROOT, "berichte", "delta_2026-08-17_0930.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("Bericht geschrieben:", out)
print("Zeilen:", len(lines))
