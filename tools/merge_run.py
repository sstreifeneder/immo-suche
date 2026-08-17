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
NOW_ISO = "2026-08-17T09:30:00+02:00"
TODAY = "2026-08-17"

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
        "willhaben": "abgedeckt (Chrome via Geräte-Brücke, __NEXT_DATA__, Kärnten & Steiermark, Häuser ≤900k & Grundstücke ≤200k nach Aktualität). Delta ~4 Tage seit letztem Lauf (13.08. 09:25) → geblättert bis Cutoff 13.08. (rows=90): Kärnten Häuser 8 Seiten, Steiermark Häuser 12, Kärnten Grundstücke 4, Steiermark Grundstücke 6 = 1.530 Anzeigen im Delta-Fenster erfasst. Nach Listen-Filter (539 Häuser Wohnfläche <160 m², 232 Grundstücke ≤1.000 m², 185 Ausschluss-Typen/Freizeit/Gewerbe im Titel, 27 Preis-Artefakte) blieben 332 Kandidaten, alle einzeln Exposé-geprüft (PLOT/AREA für die echte Grundfläche, DESCRIPTION für Widmung/Typ/Lagemerkmale), 0 Fehlversuche. Aussortiert im Exposé: 79 Häuser mit Grund <1.000 m² bzw. ohne belegbare PLOT/AREA, 23 Grundstücke ohne Bauland-Beleg. Übernommen 230, davon nach Abgleich gegen 872 bekannte willhaben-IDs 52 neu; die 178 bereits bekannten Anzeigen wurden nur als Preis-/Sicht-Stubs übergeben (zuletzt_gesehen + Preisprüfung). Im Python-Post-Pass 13 Grundstücke mit nur generischem Bauland-Hinweis auf 'TEIL – verfehlt: Widmung ungesichert' herabgestuft. Häuser 650–900k und Grundstücke 150–200k als TEIL Preis geführt. Hinweis: die Geräte-Brücke zum Mac riss während des ersten Datentransfers ab und Chrome wurde neu gestartet – der willhaben-Scan wurde danach vollständig wiederholt.",
        "sub_agenten": "6 Großregionen parallel (Kärnten+Osttirol 33, Salzburg 6, Steiermark 34, Tirol+Vorarlberg 4, OÖ+NÖ 31, Südtirol 12 = 120 Kandidaten, 62 Volltreffer nach Normalisierung). Volltreffer u.a.: Kärnten/Osttirol 20 (EFH Weinberg/Sittersdorf 365k/230/9.585 inkl. ~6.200 m² Eigenwald Score 60, Landhaus Liebenfels/St. Leonhard 550k/220/5.896 Score 60, EFH Malta-Fischertratten 455k/180/2.416 Score 50, Feistritz a.d. Gail 259k/230/2.770, Baugründe Duel b. Velden 110k/1.163 Bauland-Dorfgebiet & St. Andrä 60k/1.191 & St. Salvator 125k/2.191 & Vordertheißenegg 49k/1.119); Steiermark 21 (Anwesen Stainz 650k/190/12.869 Score 65, Leutschach a.d. Weinstraße 499k/323/13.109 saniert A++ mit PV Score 65, Sacherl Stadl an der Mur 145k/160/1.939 Score 53, Unterlamm 650k/243/1.176, Zeltweg 550k/400/2.009, Baugrund Maria Lankowitz/Puchbach 81,8k/4.796 mit Waldanteil und eigener Quelle Score 54); OÖ+NÖ 19 (EFH Ramsau/Türnitzer Alpen 450k/280/1.918 Waldlichtung Score 72, Payerbach/Rax 565k/192/7.012 inkl. 6.839 m² Eigenwald Score 65, Unterkohlstätten/Günser Bergland 179k/226/3.717 Score 59, Ulrichsberg-Schöneben 349k/170/1.600 Score 52, Blockhaus St. Florian am Inn 319k/162/1.150 Score 48, Baugründe Maigen/Weinzierl 58,8k/4.103 & Helpfau-Uttendorf 149k/3.201 & Anzendorf 98k/1.435); Salzburg 1 (Landhaus Kobl b. Anthering 540k/160/2.248, Alleinlage, Nutzwasserbrunnen, Score 59); Südtirol 1 (Mühlwald/Tauferer Ahrntal 540k/312/1.500 Score 33); Tirol+Vorarlberg 0. Strukturbefunde: Tirol+Vorarlberg weiterhin 0 Volltreffer – Bauland durchweg 250–800 €/m² (nichts >1.000 m² unter 200k), Häuser mit großem Grund fast immer Mehrfamilien-/Anlageobjekte oder >900k; bester Near-Miss Nassereith 535k/158,7/1.101 (verfehlt die Wohnfläche um 1,3 m²) und Fügenberg 689k/165/1.196 in absoluter Alleinlage mit ausdrücklichem Hauptwohnsitz. Salzburg: Klasse B komplett leer (günstigstes Bauland >1.000 m² = 240k in Unternberg), Pongau/Pinzgau faktisch komplett über Budget, Lungau scheitert an der Wohnfläche. Südtirol: Grundflächen werden systematisch nicht angegeben, Bauland kleinparzelliert/agrarisch oder für Ansässige reserviert, mehrfach geschlossener Hof/Konventionierung. OÖ/NÖ: Engpass ist die Grundfläche (viele 800–980 m²), nicht der Preis; Pyhrn-Priel/Stodertal derzeit leergefegt. Blockiert/eingeschränkt: trovit + nestoria HTTP 401; derStandard-Immobilien 403 bzw. JS-only; remax.at robots-gesperrt; immoversum.com robots/DNS; immosuchmaschine.at Grundstücks-Listen HTTP 410; ImmoScout24-Paginierung und mehrere Regionsseiten 404; findmyhome.at/tirol 404; laendleimmo.at-Pfade 404; sreal.at ohne nutzbare Trefferliste; dolomitenmarkt.it und pareggerpartner.com ohne Inserats-Markup; immoco.it 404; mehrere Exposés zwischenzeitlich 410 (gelöscht).",
        "dubletten_zusammengefuehrt": len([d for d in dubletten if isinstance(d, dict) and d.get("merged_into")]),
        "verworfen_ueber_obergrenze": len(verworfen),
        "hinweis": "additiver Neufund-Lauf; keine vollständige Verfügbarkeits-Nachprüfung -> kein fehlt_seit-Inkrement, entfernt=0. willhaben-Zugriff über die Chrome-Steuerung der Geräte-Brücke (Claude-in-Chrome-Extension nicht verbunden).",
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
