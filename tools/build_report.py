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
        f"Suche: 6 Großregionen parallel über Sub-Agenten (Kärnten+Osttirol 22, Salzburg 8, Steiermark 28, Tirol+Vorarlberg 6, OÖ+NÖ 31, Südtirol 12 = 107 Kandidaten, 42 Volltreffer) + **willhaben via Chrome-Browser** (Kärnten & Steiermark, Häuser ≤900k & Grundstücke ≤200k nach Aktualität; Delta ~8 Tage seit letztem Lauf → 2.622 Anzeigen im Delta-Fenster bis Cutoff 05.08. durchgeblättert (rows=90); nach ID-Dedup gegen 781 bekannte willhaben-IDs und Titel-Vorfilter 299 neue Kandidaten einzeln Exposé-geprüft und 97 übernommen: 66 Häuser + 31 Grundstücke, davon 44 Volltreffer). Bei willhaben-Häusern wurde die echte Grundstücksgröße einzeln aus dem Exposé-Detail (`PLOT/AREA`) verifiziert, bei Grundstücken die Widmung aus dem Exposé-Text (`DESCRIPTION`) belegt; 115 Häuser mit Grund <1.000 m² bzw. ohne belegbare Grundfläche und 83 Grundstücke ohne belegte Bauland-Widmung sind nicht übernommen, 5 weitere Häuser über das PROPERTY_TYPE-/Titel-Sicherheitsnetz auf TEIL Typ herabgestuft.\n\n"
        f"Häuser 650–900k und Grundstücke 150–200k sind als Near-Miss \"TEIL – verfehlt: Preis\" geführt (Zielpreise 650k bzw. 150k); Objekte mit Freizeit-/Zweitwohnsitz-Widmung als \"TEIL – verfehlt: Widmung\", Zwei-/Mehrfamilienhäuser und Gewerbe-/Anlageobjekte als \"TEIL – verfehlt: Typ\". ⚠️ Tirol+Vorarlberg nur 1 Volltreffer und **0 Baugrundstücke** (in 9 Bezirken kein unbebautes Grundstück >1.000 m² unter 200.000 €; Häuser fast durchweg Grund <1.000 m², mehrfach Freizeitwohnsitz-Widmung). ⚠️ Südtirol nur 1 Volltreffer (Konventionierung/geschlossener Hof; Grundfläche selten beziffert; Bauland kleinparzelliert/agrarisch). ⚠️ Salzburg: weiterhin kein gewidmetes Bauland >1.000 m² unter 200.000 € am Markt; Häuser ≥160 m² auf ≥1.000 m² starten faktisch bei 790.000 €. ⚠️ Blockiert: remax.at robots-gesperrt; immowelt.at Suchseiten HTTP 410; findmyhome.at/sreal.at/derStandard-Immobilien 404; laendleimmo.at + immoversum.com robots-gesperrt; idealista.it HTTP 400. "
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

out = os.path.join(ROOT, "berichte", "delta_2026-08-13_0925.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("Bericht geschrieben:", out)
print("Zeilen:", len(lines))
