#!/usr/bin/env python3
"""build_report.py – erzeugt den Delta-Bericht (Markdown) aus delta_result.json."""
import json, os, sys

CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/sessions/fervent-loving-thompson/mnt/outputs"
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
        f"Suche: 6 Großregionen parallel über Sub-Agenten (Kärnten+Osttirol 14, Salzburg 7, Steiermark 9, Tirol+Vorarlberg 13, OÖ+NÖ 36, Südtirol 35 = 114 Kandidaten) + **willhaben via Chrome-Browser** (Kärnten & Steiermark, Häuser & Grundstücke nach Aktualität, 690 Anzeigen durchgeblättert; nach Filterung und Dedup gegen 320 bekannte willhaben-IDs 64 Kandidaten, davon 38 nach Exposé-Prüfung übernommen). Bei willhaben-Häusern wurde die Grundstücksgröße einzeln aus dem Exposé-Detail (`PLOT/AREA`) verifiziert, bei Grundstücken die Widmung aus dem Exposé-Text (`DESCRIPTION`) belegt; Objekte ohne belegte Bauland-Widmung, mit Grund <1.000 m² oder mit ausgeschlossenem Typ (Doppel-/Reihen-/Mehrfamilienhaus, Gasthaus/Gewerbe, Freizeitwohnsitz) sind nicht als Volltreffer geführt.\n\n"
        f"Häuser 650–900k und Grundstücke 150–200k sind als Near-Miss „TEIL – verfehlt: Preis\" geführt (Zielpreise 650k bzw. 150k). ⚠️ Tirol+Vorarlberg 0 Volltreffer (Grund durchweg <1.000 m², Bauland >1.000 m² durchweg >200k; mehrfach explizite Freizeitwohnsitz-Widmung). ⚠️ Südtirol nur 1 Volltreffer (Konventionierung/geschlossener Hof; Bauland kleinparzelliert und konventioniert). ⚠️ Salzburg: kein gewidmetes Bauland >1.000 m² unter 200.000 € am Markt. ⚠️ Rate-Limit: web_fetch lief bei mehreren Sub-Agenten ins HTTP 429 – 5 Kärntner Objekte nur listenbasiert erfasst (als TEIL/ohne Bild geführt, im nächsten Lauf nachzuverifizieren); remax.at, sreal.at, findmyhome.at, wohnnet.at sowie Teile von OÖ (Molln, Windischgarsten, Hinterstoder, Spital am Pyhrn) blieben unabgedeckt. Leere Hüllen: immmo.at, immo.sn.at, teilweise immobiliare.it. "
        f"Dubletten zusammengeführt: {r['dubletten']} (Zwei-Stufen-Dedup url_norm + Inhalts-Fingerprint, plus Post-Merge-Check über Ortsname/Preis/Grund). Über Aufnahme-Obergrenze verworfen: {r['verworfen']}.\n")
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

out = os.path.join(ROOT, "berichte", "delta_2026-07-20_0930.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("Bericht geschrieben:", out)
print("Zeilen:", len(lines))
