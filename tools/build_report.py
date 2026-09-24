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
        f"Suche: 6 Großregionen parallel über Sub-Agenten (Kärnten+Osttirol 103, Salzburg 20, Steiermark 69, Tirol+Vorarlberg 26, OÖ+NÖ 65, Südtirol 24 = 307 Kandidaten inkl. Preis-Updates bekannter Inserate, 107 Volltreffer nach Normalisierung) + **willhaben via Chrome-Browser** (Kärnten & Steiermark, Häuser ≤900k & Grundstücke ≤200k nach Aktualität; Delta ~5,5 Wochen seit letztem Lauf → alle vier Listen **vollständig** durchgeblättert (rows=90; Kärnten Häuser 11 Seiten, Steiermark Häuser 22, Kärnten Grundstücke 4, Steiermark Grundstücke 8 = 3.873 Anzeigen); nach Listen- und Titel-Vorfilter (1.770 Häuser <160 m² Wohnfläche, 541 Grundstücke ≤1.000 m², 547 Ausschluss-Typen, 17 Freizeit, 74 Preis-Artefakte) 406 bereits bekannte Anzeigen als Preis-/Sicht-Stubs mitgeführt und 518 neue Kandidaten einzeln Exposé-geprüft (0 Fehlversuche): 186 Häuser mit Grund <1.000 m² bzw. ohne belegbare `PLOT/AREA` und 56 Grundstücke ohne Bauland-Beleg aussortiert, **276 übernommen**; im Python-Post-Pass 111 Grundstücke mit nur generischem Bauland-Hinweis auf \"TEIL – Widmung ungesichert\" herabgestuft).\n\n"
        f"Häuser 650–900k und Grundstücke 150–200k sind als Near-Miss \"TEIL – verfehlt: Preis\" geführt (Zielpreise 650k bzw. 150k); Freizeit-/Zweitwohnsitz-Widmung als \"TEIL – verfehlt: Widmung\", Zwei-/Mehrfamilienhäuser, Bungalows und Gewerbe-/Anlageobjekte als \"TEIL – verfehlt: Typ\". "
        f"🔔 **Durch Preissenkung jetzt im Zielpreis (Preis war der einzige Mangel – bitte neu prüfen):** Anwesen Leutschach a.d. Weinstraße 690k → 499k (323 m² / 13.109 m²), EFH Lieboch 695k → 649k (210 m² / 1.102 m²), Baugrund Köttmannsdorf 184k → 149k (1.261 m²), Bauland Kumberg/Gschwendt 175k → 149k (1.214 m², Doppelhaus-Baubewilligung). "
        f"ℹ️ Tirol+Vorarlberg nur 2 Volltreffer (Feldkirch 590k, Häselgehr/Lechtal 469k), weiterhin keine Baugrundstücke >1.000 m² unter 200k. Salzburg: 1 neuer Volltreffer (St. Michael im Lungau 480k/180/1.576), Klasse B weiterhin leer. Südtirol: kein neuer Volltreffer (große Grundstücke praktisch nur als geschlossene Höfe, Bauparzellen 100–400 m²). OÖ/NÖ: Engpass bleibt die Grundfläche (viele 860–980 m²). "
        f"⚠️ Blockiert/eingeschränkt: direkter curl-Abruf aller Portale vom Proxy gesperrt (nur Web-Abruf); remax.at und idealista robots-gesperrt; trovit 401; derStandard 403; raiffeisen-immobilien und sREAL-Exposés 404; ImmoScout24-Trefferlisten brechen ab Seite ~6–11 ab (Kärnten ~150 von 239, Steiermark ~126 von 186 Häusern erreicht); mehrere immowelt-/IS24-Exposés 410 (gelöscht). "
        f"ℹ️ Technik: willhaben lief über die Chrome-Steuerung der Geräte-Brücke; das eingebaute Browser-Fenster verlangte für willhaben eine Einzelfreigabe pro Aktion und war daher für den Scan ungeeignet. "
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

out = os.path.join(ROOT, "berichte", "delta_2026-09-24_1015.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("Bericht geschrieben:", out)
print("Zeilen:", len(lines))
