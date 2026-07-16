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
CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/sessions/keen-confident-ramanujan/mnt/outputs"
NOW_ISO = "2026-07-16T13:58:00+02:00"
TODAY = "2026-07-16"

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
        "willhaben": "abgedeckt (Chrome, __NEXT_DATA__, Kärnten & Steiermark, Häuser & Grundstücke nach Aktualität; diesmal deutlich tiefer geblättert: 420 Häuser-Inserate Kärnten (zurück bis 11.07.), 600 Häuser Steiermark (bis 13.07.), je 180 Grundstücke Kärnten/Steiermark (bis 08.07. bzw. 13.07.) → 123 Kandidaten, 66 Volltreffer. Grundflächen der Häuser je Exposé-Detail (PLOT/AREA) verifiziert, Widmung der Grundstücke aus dem Exposé-Text (DESCRIPTION) belegt. Volltreffer-Häuser: Eichberg/Leibnitz Alleinlage 635k/210 m²/37.744 m² (Score 90) + Gamlitz Allein-/Ruhelage 497k/240 m²/31.139 m² (75) + Eibiswald Landwirtschaft 590k/160 m²/75.000 m² (65) + Aichach/Villach-Land 450k/206 m² (57) + Deutschlandsberg Anwesen 300k/170 m²/9.667 m² (51) + Flamberg 292k (49, reserviert) + Birkfeld 395k (48) + Ludmannsdorf 395k (47) + Unterlamm 650k (47). Volltreffer-Grundstücke: Kötschach-Mauthen 110k/1.090, Klagenfurt-Römerweg 167k/1.284, Villach-Wollanig 179,5k/1.059 (alle Bauland-Wohngebiet), Völkermarkt/Töllerberg 79,5k/1.185 + St. Jakob im Rosental 74,5k/1.126 (Bauland-Dorfgebiet), Ludmannsdorf 99,5k/1.064, Feldkirchen 109k/1.096, Penk 90k/1.251, Eibiswald/Haselbach 60k/1.086, Fohnsdorf 112k/1.120, Laßnitzthal 88,3k/2.102, Keutschacher Seental 189k. Near-Miss/TEIL: Vorau Bauernhof 798,5k/2,86 ha (85), Feldkirchen Alleinlage 750k/3,75 ha (80), Seiersberg 695k (64), St. Stefan/Koralpe 885k, Graßnitzberg 879k, Völkermarkt 857k; verworfen bzw. TEIL wegen Typ/Widmung: Gewerbegebiet Friesach (2x), Zweitwohnsitzwidmung Sittersdorf, Aufschließungsgebiet Ossiach, Bauland-Anteil Pudlach, Ferienwohnanlage Treffen, Wohn-/Geschäftshäuser, vermietetes Anlageobjekt Graz-Straßgang.",
        "sub_agenten": "6 Großregionen parallel (Kärnten+Osttirol 9, Salzburg 6, Steiermark 20, Tirol+Vorarlberg 3, OÖ+NÖ 4, Südtirol 6 Kandidaten). Volltreffer: Kärnten Sonnenchalet Eitweg/Lavanttal (340k, 260 m², 1.277 m², Alleinlage+Panoramablick, Pellet+Solar, Score 62) + Baugrund St. Jakob im Rosental/Schlatten (72k, 1.131 m², Bauland-Dorfgebiet); Salzburg Bauernhaus Hopfberg/Taxenbach (Bieterverfahren ab 570k, 200 m², 1.475 m², 1.100 m Seehöhe, Score 62); Steiermark EFH Krakaudorf/Murau (545k, 258 m², 2.659 m², 50) + Judenburg (499k, 167 m², 47) + Unterlamm (650k, 243 m², 43) + Gnas (280k, 198 m²) + Bauernhaus St. Stefan ob Stainz (610k, 168 m²) + Baugründe Fohnsdorf 112k/1.120, Rettenbach-Sonnenhang 148k/1.481, St. Lambrecht 69k/1.380, Bad Schwanberg 60k/1.890; OÖ+NÖ Baugrund Perwarth/Randegg (51,8k, 1.044 m², Bauland-Wohnen). Tirol+Vorarlberg 0 Volltreffer (Grund durchweg <1.000 m², Bauland >1.000 m² durchweg >200k). Südtirol 0 Volltreffer (Konventionierung/geschlossener Hof/Preis auf Anfrage; Baugrundstücke >1.000 m² unter 200k praktisch nicht am Markt). Blockiert: pareggerpartner.com JS-leer, engelvoelkers.com JS-Hülle, immowelt/immobilien.net/immobilien.nachrichten.at für OÖ+NÖ leer; idealista/casa.it bot-blockiert (nur Snippets). immomarkt-suedtirol.bz diesmal lesbar.",
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
