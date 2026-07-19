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
CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/sessions/serene-pensive-sagan/mnt/outputs"
NOW_ISO = "2026-07-19T10:10:00+02:00"
TODAY = "2026-07-19"

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
        "willhaben": "abgedeckt (Chrome, __NEXT_DATA__, Kärnten & Steiermark, Häuser & Grundstücke nach Aktualität bis 16.07.). Geblättert: Kärnten Häuser 11 Seiten/326, Steiermark Häuser 15 Seiten/447 (≤650k), Kärnten Grundstücke 4 Seiten/102, Steiermark Grundstücke 9 Seiten/248. Nach Filter (WF≥160, zulässige Typen, Grund≥1.000 je Exposé-PLOT/AREA, Widmung je Exposé-DESCRIPTION, Dedup gegen 236 bekannte willhaben-IDs) 86 Kandidaten: 51 Häuser (48 ja, 3 TEIL) + 35 Grundstücke (24 ja, 11 TEIL). Volltreffer-Häuser u.a. Hirschegg-Pack Alleinlage 399k/274 m²/7.650 m² (Score 90), Stainz Landhaus 598k/210 m²/14.000 m² (80), Sittersdorf/Altendorf Anwesen 330k/172 m²/13.704 m² (75, als TEIL wg. Typ), St. Ulrich am Waasen Alleinlage 390k/230 m²/4.138 m² (64), Schöder/Murau Bauernhaus 460k/293 m²/1.313 m² (62), St. Jakob im Rosental 585k/180 m²/2.348 m² Karawankenblick (60). Volltreffer-Grundstücke u.a. Patergassen 59k/3.001 m² (50), Eibiswald/Stammeregg 59k/2.793 m² (50), St. Katharein a.d. Laming 107k/1.070 m² Bergpanorama (43), Launsdorf 150k/1.081 m² (43), St. Jakob/Rosenbach 95k/1.621 m² (33). Near-Miss/TEIL: Häuser mit mehreren Wohneinheiten (Keutschach, Weinberg/Sittersdorf), Grundstücke 150–200k (Niklasdorf, Kumberg, St. Magdalena/Lemberg, St. Martin am Grimming) sowie Feriengebiet-/Baulandanteil-Fälle (Strallegg, Steyeregg).",
        "sub_agenten": "6 Großregionen parallel (Kärnten+Osttirol 21, Salzburg 16, Steiermark 12, Tirol+Vorarlberg 14, OÖ+NÖ 14, Südtirol 7 = 84 Kandidaten). Volltreffer u.a.: Kärnten Alleinlage-Landhaus Diex (548k, 280 m², 4.163 m², eigene Quelle+Pellets, Score 69) + Baugründe Ludmannsdorf 99,5k/1.064 & 98k/1.410, Liebenfels 52k/1.036, St. Margarethen/Völkermarkt 79,5k/1.185; Salzburg Bauernhaus Taxenbach/Hopfberg (Bieterverfahren 570k, 200 m², 1.475 m², Score 62) + EFH Schwarzach 579k/178 m²; Steiermark EFH Judenburg 299k/179 + Knittelfeld 499k/258 + Pöls-Oberkurzheim 389k/328 + Baugründe St. Lambrecht 69k/1.380 & Wies-Sulmtal 54k; OÖ+NÖ EFH Ulrichsberg 420k/250/1.230 + Gresten 280k/188 + Waidhofen/Ybbs 400k/170/1.500 + Baugründe Perwarth 51,8k/1.044, St. Nikola 54k/1.143, Vorderstoder 119,8k/1.001, Gresten 74,6k/1.244, Steinakirchen 133k/1.663. Tirol+Vorarlberg 0 Volltreffer (Grund durchweg <1.000 m², Bauland >1.000 m² durchweg >200k; teils Freizeitwohnsitz/Preis auf Anfrage). Südtirol 0 Volltreffer (Konventionierung/geschlossener Hof; Bauland >1.000 m² unter 200k praktisch nicht am Markt). Blockiert/Hochpreis: pareggerpartner.com, engelvoelkers.com; idealista/immobilienscout24 JS-lastig.",
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
