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
CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/sessions/fervent-loving-thompson/mnt/outputs"
NOW_ISO = "2026-07-20T09:30:00+02:00"
TODAY = "2026-07-20"

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
        "willhaben": "abgedeckt (Chrome, __NEXT_DATA__, Kärnten & Steiermark, Häuser & Grundstücke nach Aktualität). Geblättert: Kärnten Häuser 10 Seiten/300 (≤900k), Steiermark Häuser + Kärnten/Steiermark Grundstücke (≤200k) bis Inseratsdatum 17./18.07. – 690 Anzeigen gesamt. Nach Filter (WF≥160 bzw. Grund>1.000 m², zulässige Typen, Dedup gegen 320 bekannte willhaben-IDs, Beschränkung auf seit dem letzten Lauf neu inserierte Objekte) 64 Kandidaten, davon 38 nach Exposé-Prüfung (PLOT/AREA für die echte Grundstücksgröße, DESCRIPTION für Widmung/Lage) übernommen: 25 Häuser + 13 Grundstücke, 10 Volltreffer. Volltreffer-Häuser: Gamlitz/Südsteiermark Landgut 430k/185 m²/41.467 m² (Score 75, Hauptgebäude entkernt), Übersbach bei Fürstenfeld 290k/207 m²/2.755 m² (54, nahezu alleinstehend in Sackgasse), Limbach/Dechantskirchen 549k/248 m²/1.718 m² (38, PV), Obergöriach/Moosburg 550k/212 m²/1.721 m² (33), Bleiberg-Kreuth 396k/303 m²/2.163 m² (24, hochwertig renoviert), Hartberg 645k/168 m²/1.060 m² (22). Volltreffer-Grundstücke: Timmersdorf/Traboch 118k/1.202 m² Bauland-Wohngebiet mit Bergpanorama (43), Thörl-Maglern/Arnoldstein 128,7k/1.716 m² Bergblick (27), St. Margarethen b. Knittelfeld 79,5k/1.023 m² WA (23), Kirchbach in Stmk. 75k/1.202 m² Wohnen Allgemein (7). Aussortiert: 15 Häuser mit Grund <1.000 m² (Exposé-PLOT/AREA), 10 Grundstücke ohne Widmungshinweis, 7 Häuser mit zwei/mehreren Wohneinheiten (Wolfsberg 3-Familien-Villa, Gödersdorf, Spittal, Poggersdorf, Veitsch, Teufenbach, Thörl), Gasthaus Apfelberg und ehem. Gasthof Rinnegg (Typ), Lieboch (861,6k über Aufnahmegrenze). Near-Miss/TEIL: Häuser 698–890k (Feldbach, Fernitz, Allerheiligen b. Wildon, St. Stefan ob Stainz, Bad Mitterndorf, Sinabelkirchen, Graz-Passivhaus), Grundstücke 165–200k (St. Josef/Weststmk. Dorfgebiet, Murau Wohnen Rein, Hengsberg Bauerwartungsland, Mail/St. Veit) sowie Baugründe ohne belegte Widmungskategorie (Eichkögl, Maria Lankowitz, Feistritz am Kammersberg).",
        "sub_agenten": "6 Großregionen parallel (Kärnten+Osttirol 14, Salzburg 7, Steiermark 9, Tirol+Vorarlberg 13, OÖ+NÖ 36, Südtirol 35 = 114 Kandidaten, 25 Volltreffer). Volltreffer u.a.: OÖ+NÖ Alleinlage-Bungalow Aschach an der Steyr (449k, 207 m², 3.159 m², Score 69) + ehem. Mühle Wartberg an der Krems (475k, 240 m², 1.682 m²) + Mühldorf/Scharnstein (559k, 214 m², 3.520 m²) + Baugründe Vorderstoder 119,8k/1.001, Gresten 137,3k/2.288 & 74,6k/1.244, St. Leonhard-Perwarth 56,5k/1.002 & 51,8k/1.044; Steiermark St. Oswald ob Eibiswald (630k, 280 m², 11.321 m², Waldrand/900 m, Quellwasser+PV+Erdwärme, Score 85) + Krakaudorf (545k, 258 m², 2.659 m²) + Pöls-Oberkurzheim (389k, 328 m², 1.185 m²) + Baugründe St. Lambrecht 69k/1.380 (Allg. Wohngebiet) & Krakau 146,1k/3.246; Kärnten+Osttirol EFH Reisach/Kirchbach im Gailtal (495k, 308 m², 1.909 m², Karnische Alpen, Score 48) + Hermagor (410k, 240 m², 1.495 m²) + Tratten/St. Stefan im Gailtal (239k, 166 m², 1.122 m²) + Baugrund Ferndorf 96k/1.990 (SW-Ausrichtung); Salzburg Bauernhaus Hopfberg/Taxenbach (Bieterverfahren 570k, 200 m², 1.475 m², Bj. 1759, eigene Quelle, Score 62); Südtirol nur Mühlwald/Pustertal (540k, 312 m², 1.500 m², stark sanierungsbedürftig, Score 33); Tirol+Vorarlberg 0 Volltreffer. Strukturbefunde: In Salzburg, Tirol/Vorarlberg und Südtirol ist gewidmetes Bauland >1.000 m² unter 200.000 € derzeit praktisch nicht am Markt; in Osttirol dominieren Freizeitwohnsitz-Widmungen. Blockiert/eingeschränkt: web_fetch lief bei mehreren Sub-Agenten session-weit ins HTTP-429-Rate-Limit (Kärnten: 5 Objekte nur listenbasiert, als TEIL/bild=null geführt; OÖ+NÖ und Tirol/Vorarlberg konnten remax.at, sreal.at, findmyhome.at, wohnnet.at nicht mehr abrufen); immmo.at und immo.sn.at liefern leere Hüllen, immobiliare.it-Exposés teils nicht abrufbar.",
        "dubletten_zusammengefuehrt": len([d for d in dubletten if isinstance(d, dict) and d.get("merged_into")]),
        "verworfen_ueber_obergrenze": len(verworfen),
        "hinweis": "additiver Neufund-Lauf; keine vollständige Verfügbarkeits-Nachpruefung -> kein fehlt_seit-Inkrement, entfernt=0",
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
