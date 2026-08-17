#!/usr/bin/env python3
"""normalize.py – Sicherheitsnetz fuer cand_*.json vor merge_run.py.
Siehe Projektgedaechtnis 'immo-lauf-cand-normalisierung'.
"""
import json, glob, os, re, sys

CAND_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/immolauf/proj/outputs"

RX_TYP = re.compile(r"mehrfamilien|zweifamilien|bungalow|villa|reihenhaus|doppelhaus|zinshaus|gasthaus|chalet|apartment|almhütte|berghütte|wohnung|büro|gewerbe|hotel", re.I)
RX_TITEL = re.compile(r"wohneinheiten|whgen|(zwei|drei|vier|2|3|4)\s+(wohnh|häuser|einheiten|wohnungen)|wohnhäuser|anlageobjekt|anlageimmobilie|renditeimmobilie|investment|tankstelle|geschäftslokal|geschäftshaus|betriebsobjekt|lagerhalle|werkstatt|arbeiten & wohnen|wohnen und vermieten|mietwohnhaus|vollvermietet|vermietungspotenzial|projektentwicklung|mehrgeschossig|liegenschaftspaket|ensemble|garagen|firmenstandort", re.I)
RX_ELW = re.compile(r"einliegerwohnung", re.I)
RX_FREIZEIT = re.compile(r"freizeitwohnsitz|zweitwohnsitz|ferienimmobilie|freizeitgrund|freizeitwohn", re.I)
# Harter Ausschluss: nie gesichertes Wohn-Bauland
RX_KEIN_BAULAND_HART = re.compile(r"beabsichtigtes bauland|aufschließungsgebiet|firmenstandort|betriebsgebiet|betriebsbaugebiet|industriegebiet|gewerbegebiet|gewerbegrund|freizeitgrund", re.I)
# Weicher Ausschluss: nur wenn KEIN positiver Bauland-Beleg vorhanden (Mischparzellen Bauland+Grünland sind ok)
RX_KEIN_BAULAND_WEICH = re.compile(r"freiland|grünland|waldfläche|waldgrund|forstgrund|streuobst|landwirtschaftsfl", re.I)
RX_BAULAND_POS = re.compile(r"bauland|baumischgebiet|dorfgebiet|wohngebiet|als baugrund ausgewiesen|baubewilligung", re.I)
# Widmung ausdruecklich nicht belegt
RX_WIDM_UNSICHER = re.compile(r"nicht genannt|nicht belegt|nicht ausgewiesen|ungesichert|unklar|vermutlich|vermutet|nicht angegeben", re.I)

log = []


def is_grund(o):
    t = (o.get("typ") or "").lower()
    return ("baugrund" in t or t.startswith("grundst") or t == "bauland"
            or (o.get("wohnflaeche") in (None, 0, "") and ("grund" in t or "bauplatz" in t)))


def teil(o, grund, tag):
    if (o.get("hart_ok") or "").strip().lower() == "ja":
        o["hart_ok"] = "TEIL – " + grund
        log.append(f"  [{tag}] {(o.get('titel') or '')[:60]} -> {grund}")


def main():
    files = sorted(glob.glob(os.path.join(CAND_DIR, "cand_*.json")))
    total = 0
    verworfen_total = 0
    for f in files:
        arr = json.load(open(f, encoding="utf-8"))
        out = []
        for o in arr:
            total += 1
            # (1) hart_ok "OK (...)" -> "ja"
            h = (o.get("hart_ok") or "").strip()
            if h.lower().startswith("ok"):
                o["hart_ok"] = "ja"
                log.append(f"  [ok->ja] {(o.get('titel') or '')[:60]}")

            titel = (o.get("titel") or "")
            typ = (o.get("typ") or "")
            widmung = (o.get("widmung") or "")
            zustand = (o.get("zustand") or "")
            alltext = " ".join([titel, typ, widmung, zustand])
            p = o.get("preis")
            g = o.get("grundflaeche")
            w = o.get("wohnflaeche")
            grundstueck = is_grund(o)

            # (5) Preis-Artefakte verwerfen
            if isinstance(p, (int, float)) and p not in (None, 0):
                if (0 < p < 1000) or (float(p) % 1 != 0):
                    verworfen_total += 1
                    log.append(f"  [VERWORFEN Preis-Artefakt {p}] {titel[:60]}")
                    continue

            # (2) Preis-Ziel
            if isinstance(p, (int, float)):
                if grundstueck and p > 150000:
                    teil(o, "verfehlt: Preis (>150.000 € Ziel; innerhalb 200.000 € Aufnahme)", "preis")
                elif (not grundstueck) and p > 650000:
                    teil(o, "verfehlt: Preis (>650.000 € Ziel; innerhalb 900.000 € Aufnahme)", "preis")

            # (3) Wohnflaeche Haeuser
            if not grundstueck:
                if w in (None, 0, "") or (isinstance(w, (int, float)) and w > 1000):
                    teil(o, "Wohnfläche ungesichert/implausibel", "wf")
                elif isinstance(w, (int, float)) and w < 160:
                    teil(o, "verfehlt: Wohnfläche <160 m²", "wf")

            # (4) Grundflaeche
            if g in (None, 0, ""):
                teil(o, "Grundfläche ungesichert", "gf")
            elif grundstueck and g <= 1000:
                teil(o, "verfehlt: Grundfläche ≤1.000 m²", "gf")
            elif (not grundstueck) and g < 1000:
                teil(o, "verfehlt: Grundfläche <1.000 m²", "gf")

            # Typ-Sicherheitsnetz (nur Haeuser)
            if not grundstueck:
                if (RX_TYP.search(typ) or RX_TITEL.search(titel)) and not RX_ELW.search(alltext):
                    teil(o, "verfehlt: Typ", "typ")

            # Freizeit-Check (beide Klassen)
            if RX_FREIZEIT.search(alltext):
                teil(o, "verfehlt: Widmung (Freizeitwohnsitz)", "freizeit")

            # Grundstuecke ohne echtes Bauland
            if grundstueck:
                if RX_KEIN_BAULAND_HART.search(alltext):
                    teil(o, "verfehlt: Widmung (kein gesichertes Bauland)", "bauland_hart")
                elif RX_KEIN_BAULAND_WEICH.search(alltext) and not RX_BAULAND_POS.search(alltext):
                    teil(o, "verfehlt: Widmung (kein gesichertes Bauland)", "bauland_weich")
                elif RX_WIDM_UNSICHER.search(widmung) or not widmung.strip():
                    teil(o, "verfehlt: Widmung ungesichert", "widm_unsicher")
                # willhaben-Grundstuecke mit generischer Widmung -> ungesichert
                elif widmung.strip() == "Bauland laut Inserat":
                    teil(o, "verfehlt: Widmung ungesichert", "widm_generisch")

            # (6) Score nur bei Volltreffern
            if (o.get("hart_ok") or "").strip().lower() != "ja":
                o["freiheits_score"] = None
                o["freiheits_score_detail"] = None
            out.append(o)
        json.dump(out, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        ja = sum(1 for x in out if (x.get("hart_ok") or "").strip().lower() == "ja")
        print(f"{os.path.basename(f)}: {len(out)} Objekte, {ja} Volltreffer")
    print(f"\nGesamt {total} geprüft, {verworfen_total} verworfen, {len(log)} Änderungen:")
    for l in log:
        print(l)


if __name__ == "__main__":
    main()
