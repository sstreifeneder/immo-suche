#!/usr/bin/env python3
"""merge_run.py – fuehrt Kandidaten (cand_*.json aus outputs) mit bekannte_objekte.json zusammen.
Zwei-Stufen-Dedup (url_norm + dedup_fp), Delta-Klassifikation, Speichern + lauf_historie.
Ausgabe: schreibt bekannte_objekte.json neu und druckt Delta-Statistik + Delta-Objekte als JSON.
"""
import json, os, sys, glob, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from immo_lib import url_norm, dedup_fp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "bekannte_objekte.json")
CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/immolauf/proj/outputs"
NOW_ISO = "2026-08-13T09:25:00+02:00"
TODAY = "2026-08-13"

def is_grund(o):
    t = (o.get("typ") or "").lower()
    return ("baugrund" in t or t.startswith("grundst") or "bauland" == t) or \
           (o.get("wohnflaeche") in (None, 0, "") and ("grund" in t or "bauplatz" in t))

def compute_fp(o):
    return dedup_fp(o.get("ort"), o.get("preis"), o.get("wohnflaeche"), o.get("grundflaeche"), is_grundstueck=is_grund(o))

def acceptance_ok(o):
    p = o.get("preis")
    if p in (None, 0, ""):
        return True  # Preis auf Anfrage -> als TEIL zulaessig
    p = float(p)
    if is_grund(o):
        return p <= 200000
    return p <= 900000

def main():
    data = json.load(open(STATE, encoding="utf-8"))
    objekte = data["objekte"]
    prev_letzter_lauf = data.get("letzter_lauf")

    # Index aufbauen
    by_urlnorm = {}
    by_fp = {}
    for o in objekte:
        un = o.get("url_norm") or url_norm(o.get("url", ""))
        o["url_norm"] = un
        if un:
            by_urlnorm[un] = o
        for a in o.get("url_alt", []) or []:
            by_urlnorm[url_norm(a)] = o
        fp = o.get("dedup_fp")
        if fp:
            by_fp.setdefault(fp, o)

    # Kandidaten laden
    cands = []
    for f in sorted(glob.glob(os.path.join(CAND_DIR, "cand_*.json"))):
        arr = json.load(open(f, encoding="utf-8"))
        for c in arr:
            c["_src"] = os.path.basename(f)
        cands.append((os.path.basename(f), arr))

    neu, preisaenderungen, dubletten, verworfen, unveraendert = [], [], [], [], 0
    # innerhalb des Laufs schon gesehene Schluessel (gegen Doppel unter den Kandidaten)
    run_seen_urlnorm = set()
    run_seen_fp = set()

    for fname, arr in cands:
        for c in arr:
            if not acceptance_ok(c):
                verworfen.append(c)
                continue
            un = url_norm(c.get("url", ""))
            fp = compute_fp(c)
            c["url_norm"] = un
            if fp:
                c["dedup_fp"] = fp

            # Innerhalb desselben Laufs bereits verarbeitet?
            if un in run_seen_urlnorm or (fp and fp in run_seen_fp):
                # Dublette unter Kandidaten -> ueberspringen (bereits als NEU/existing behandelt)
                dubletten.append(c)
                continue

            existing = by_urlnorm.get(un) or (by_fp.get(fp) if fp else None)
            if existing:
                # bestehendes Objekt
                if un != (existing.get("url_norm")) and un not in [url_norm(a) for a in existing.get("url_alt", []) or []]:
                    existing.setdefault("url_alt", []).append(c.get("url"))
                    dubletten.append({"titel": c.get("titel"), "url": c.get("url"), "merged_into": existing.get("url")})
                existing["zuletzt_gesehen"] = TODAY
                existing["fehlt_seit"] = 0
                # Preisaenderung?
                old_p = existing.get("preis")
                new_p = c.get("preis")
                if isinstance(old_p, (int, float)) and isinstance(new_p, (int, float)) and old_p != new_p:
                    # guenstigeren fuehren
                    if new_p < old_p:
                        preisaenderungen.append({"titel": existing.get("titel"), "alt": old_p, "neu": new_p, "url": existing.get("url")})
                        existing["preis"] = new_p
                run_seen_urlnorm.add(un)
                if fp:
                    run_seen_fp.add(fp)
                continue

            # NEU
            o = dict(c)
            o.pop("_src", None)
            o["erstmals_gesehen"] = TODAY
            o["zuletzt_gesehen"] = TODAY
            o["fehlt_seit"] = 0
            hart = (o.get("hart_ok") or "").strip().lower()
            o["status"] = "aktiv" if hart == "ja" else "zu_pruefen"
            if o.get("lat") is not None and o.get("lon") is not None:
                o["geo_quelle"] = "orts-/PLZ-genau (ungefähr)"
            objekte.append(o)
            by_urlnorm[un] = o
            if fp:
                by_fp[fp] = o
            run_seen_urlnorm.add(un)
            if fp:
                run_seen_fp.add(fp)
            neu.append(o)

    # Speichern
    data["letzter_lauf"] = NOW_ISO
    aktiv_gesamt = sum(1 for o in objekte if o.get("status") == "aktiv")
    zu_pruefen = sum(1 for o in objekte if o.get("status") == "zu_pruefen")
    hist = {
        "zeit": NOW_ISO, "typ": "delta", "neu": len(neu), "preisaenderungen": len(preisaenderungen),
        "entfernt": 0, "aktiv_gesamt": aktiv_gesamt, "davon_zu_pruefen": zu_pruefen,
        "davon_hart_ok_aktiv": aktiv_gesamt,
        "willhaben": "abgedeckt (Chrome via Geräte-Brücke, __NEXT_DATA__, Kärnten & Steiermark, Häuser ≤900k & Grundstücke ≤200k nach Aktualität). Delta ~8 Tage seit letztem Lauf (05.08. 09:52) → geblättert bis Cutoff 05.08. (rows=90): Kärnten Häuser 8 Seiten, Steiermark Häuser 14, Kärnten Grundstücke 3, Steiermark Grundstücke 6 = 2.622 Anzeigen im Delta-Fenster erfasst. Nach ID-Dedup gegen 781 bekannte willhaben-IDs (556 übersprungen) und WF≥160- bzw. Grund>1.000-Filter plus Titel-Vorfilter (331 Ausschluss-Typen/Freizeit/Gewerbe) blieben 299 neue Kandidaten, alle einzeln Exposé-geprüft (PLOT/AREA für die echte Grundfläche, DESCRIPTION für Widmung/Typ/Lagemerkmale). Übernommen: 97 (66 Häuser + 31 Grundstücke), davon 44 Volltreffer. Aussortiert: 115 Häuser mit Grund <1.000 m² bzw. ohne belegbare PLOT/AREA, 83 Grundstücke ohne im Exposé belegte Bauland-Widmung, 4 Flächen-Artefakte; zusätzlich 5 Häuser über das PROPERTY_TYPE-/Titel-Sicherheitsnetz im Python-Post-Pass auf TEIL Typ herabgestuft (Geschäftslokal, „2 Wohnhäuser\", „Drei Häuser\", Anlage-Immobilie, „Arbeiten & Wohnen\"). Häuser 650–900k und Grundstücke 150–200k als TEIL Preis geführt.",
        "sub_agenten": "6 Großregionen parallel (Kärnten+Osttirol 22, Salzburg 8, Steiermark 28, Tirol+Vorarlberg 6, OÖ+NÖ 31, Südtirol 12 = 107 Kandidaten, 42 Volltreffer nach Normalisierung; Regions-cands waren sauber, 0× \"OK\"→\"ja\" nötig). Volltreffer u.a.: Kärnten/Osttirol 10 (Bauernhaus Rieding/Koralpe 650k/199/18.826 Score 95, EFH Fischertratten/Maltatal 455k/180/2.416, Landhaus Mühldorf/Mölltal 398k/300/1.500, Baugründe Hadersdolf/Gailtal 75,45k/1.006 & Kötschach-Mauthen 110k/1.090 & St. Salvator b. Friesach 125k/2.191 & Liebenfels 52k/1.036); OÖ+NÖ 14 (Sacherl Kollerschlag/Böhmerwald 599k/254/11.443 Score 85, Bauernsacherl Waldhausen i. Strudengau 630k/230/120.997 Score 80, Payerbach/Rax 565k/192/7.012 Score 70, Tambergau/Stodertal 495k/196/1.963, Schalchen/Innviertel 399k/200/24.654, Baugründe Penk 129k/1.431 & Allhartsberg 125k/1.715 & Vorderstoder 119,8k/1.001); Steiermark 14 (Anwesen Deutschlandsberg 300k/170/9.667 Score 75, Stainz 598k/190/12.869 Score 70, Krakaudorf 545k/258/2.659, Baugründe Kindberg 130k/2.102 Score 64 & St. Katharein a.d. Laming 107k/1.070 & Pöls 110k/2.390 & Rastal/Tragöß 75k/1.737); Salzburg 2 (Bauernhaus Taxenbach 570k/200/1.475 Score 62, Landhaus Anthering 540k/160/2.248); Tirol+Vorarlberg 1 (Blockhaus Boden/Bschlabertal 520k/210/1.163 Score 56, Exposé schließt Freizeitnutzung ausdrücklich aus); Südtirol 1 (Mühlwald/Tauferer Ahrntal 540k/312/1.500 Score 43). Strukturbefunde: Tirol+Vorarlberg 0 Baugrundstücke im Raster (nichts >1.000 m² unter 200k in 9 Bezirken; Häuser fast durchweg <1.000 m² Grund); Salzburg weiterhin kein gewidmetes Bauland >1.000 m² unter 200.000 € am Markt, Objekte ≥160 m²/≥1.000 m² starten bei 790k; Südtirol Bauland kleinparzelliert/agrarisch, Grundfläche selten beziffert; bei Häusern ist bundesweit die Kombination WF≥160 + Grund≥1.000 der engste Filter, bei Grundstücken die belegte Bauland-Widmung. Blockiert/eingeschränkt: remax.at robots-gesperrt; immowelt.at Suchseiten HTTP 410; findmyhome.at/sreal.at/derStandard-Immobilien mehrfach 404; laendleimmo.at Query-URLs robots-gesperrt; immoversum.com robots-gesperrt; idealista.it HTTP 400; dolomitenmarkt.it liefert kein Inserats-Markup; mehrere Exposés HTTP 410/404 (abgelaufen) verworfen.",
        "dubletten_zusammengefuehrt": len([d for d in dubletten if isinstance(d, dict) and d.get("merged_into")]),
        "verworfen_ueber_obergrenze": len(verworfen),
        "hinweis": "additiver Neufund-Lauf; keine vollständige Verfügbarkeits-Nachprüfung -> kein fehlt_seit-Inkrement, entfernt=0. willhaben-Zugriff diesmal nicht über die Claude-in-Chrome-Extension (nicht verbunden), sondern über die Chrome-Steuerung der Geräte-Brücke.",
    }
    data.setdefault("lauf_historie", []).append(hist)
    json.dump(data, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    result = {
        "prev_letzter_lauf": prev_letzter_lauf, "now": NOW_ISO,
        "neu": len(neu), "preisaenderungen": len(preisaenderungen),
        "dubletten": len([d for d in dubletten if isinstance(d, dict) and d.get("merged_into")]),
        "verworfen": len(verworfen), "gesamt_objekte": len(objekte),
        "aktiv_gesamt": aktiv_gesamt, "zu_pruefen": zu_pruefen,
        "neu_liste": sorted(neu, key=lambda x: -(x.get("freiheits_score") or 0)),
        "preisaenderung_liste": preisaenderungen,
        "verworfen_liste": [{"titel": v.get("titel"), "preis": v.get("preis"), "url": v.get("url")} for v in verworfen],
    }
    json.dump(result, open(os.path.join(CAND_DIR, "delta_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("NEU:", len(neu), "| PREIS:", len(preisaenderungen), "| DUBLETTEN:", result["dubletten"],
          "| VERWORFEN:", len(verworfen), "| GESAMT:", len(objekte), "| aktiv:", aktiv_gesamt, "| zu_pruefen:", zu_pruefen)
    print("--- NEU (nach Freiheits-Score) ---")
    for o in result["neu_liste"]:
        sc = o.get('freiheits_score')
        sc = f"{sc:>3}" if isinstance(sc, (int, float)) else "  –"
        print(f"  {sc} | {(o.get('hart_ok') or '')[:1]} | {o.get('preis')} | {o.get('ort')} | {(o.get('typ') or '')[:30]} | {(o.get('titel') or '')[:45]}")

if __name__ == "__main__":
    main()
