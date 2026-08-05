#!/usr/bin/env python3
"""build_report.py – erzeugt den Delta-Bericht (Markdown) aus delta_result.json."""
import json, os, sys

CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/immolauf/outputs"
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
        f"Suche: 6 Großregionen parallel über Sub-Agenten (Kärnten+Osttirol 11, Salzburg 6, Steiermark 23, Tirol+Vorarlberg 8, OÖ+NÖ 17, Südtirol 5 = 70 Kandidaten, 29 Volltreffer) + **willhaben via Chrome-Browser** (Kärnten & Steiermark, Häuser ≤900k & Grundstücke ≤200k nach Aktualität; Delta ~2 Tage seit letztem Lauf → 990 Anzeigen bis Cutoff 03.08. durchgeblättert (rows=90); nach ID-Dedup gegen 742 bekannte willhaben-IDs 82 neue Kandidaten Exposé-geprüft und 41 übernommen: 28 Häuser + 13 Grundstücke, davon 19 Volltreffer). Bei willhaben-Häusern wurde die echte Grundstücksgröße einzeln aus dem Exposé-Detail (`PLOT/AREA`) verifiziert, bei Grundstücken die Widmung aus dem Exposé-Text (`DESCRIPTION`) belegt; willhaben-Objekte ohne belegte Bauland-Widmung, Häuser mit Grund <1.000 m² bzw. ohne belegbare Grundfläche (46 Exposé-Drops) sowie per Titel-Vorfilter erkannte Freizeit-/Gewerbe-/Ausschluss-Objekte (72) sind nicht als Volltreffer geführt; 6 willhaben-Häuser wurden über das PROPERTY_TYPE-/Titel-Sicherheitsnetz (Mehrfamilienhaus/Bungalow, „vier Einheiten\"/„2 Wohnhäuser\"/Tankstelle) auf TEIL Typ herabgestuft.\n\n"
        f"Häuser 650–900k und Grundstücke 150–200k sind als Near-Miss \"TEIL – verfehlt: Preis\" geführt (Zielpreise 650k bzw. 150k); Objekte mit Freizeit-/Zweitwohnsitz-Widmung als \"TEIL – verfehlt: Widmung\", Zwei-/Mehrfamilienhäuser als \"TEIL – verfehlt: Typ\". ⚠️ Tirol+Vorarlberg nur 1 Volltreffer (Grund meist <1.000 m², Bauland >200k, mehrfach explizite Freizeitwohnsitz-Widmung). ⚠️ Südtirol 0 Volltreffer (Konventionierung/geschlossener Hof; Grundfläche selten beziffert; Bauland kleinparzelliert/Agrar). ⚠️ Salzburg: kein gewidmetes Bauland >1.000 m² unter 200.000 € am Markt (nur 1 Haus-Volltreffer). ⚠️ remax.at robots-gesperrt; idealista/immo.sn.at teils leere Hüllen. "
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

out = os.path.join(ROOT, "berichte", "delta_2026-08-05_0952.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("Bericht geschrieben:", out)
print("Zeilen:", len(lines))
