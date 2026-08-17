#!/usr/bin/env python3
"""postdedup.py – Post-Merge-Dublettencheck (Pflicht).
Trockenlauf per Default, mit --apply werden Zusammenfuehrungen geschrieben.
Vier Gruppierungen ueber die heutigen Neufunde (erstmals_gesehen == TODAY):
 (a) neu/neu  Ortsname + Preis/5k + Grund/100
 (b) neu/neu  ortsunabhaengig Preis/5k + Grund/100 + WF/10
 (c) neu vs. Altbestand, HAEUSER ortsunabhaengig Preis/5k + WF/5 + Grund/100
 (d) neu vs. Altbestand, GRUNDSTUECKE nur mit Ortsname-Match
"""
import json, os, re, sys, unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "bekannte_objekte.json")
CAND_DIR = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "/tmp/immolauf/proj/outputs"
APPLY = "--apply" in sys.argv
TODAY = "2026-08-17"


def norm_ort(s):
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\b\d{4,5}\b", " ", s)
    s = re.sub(r"\b(gde\.?|gemeinde|bezirk|bez\.?|bei|b\.|am|an der|a\.d\.|im|i\.|umgebung|nahe)\b", " ", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z]", "", s)
    return s[:14]


def is_grund(o):
    t = (o.get("typ") or "").lower()
    return ("baugrund" in t or t.startswith("grundst") or t == "bauland"
            or (o.get("wohnflaeche") in (None, 0, "") and ("grund" in t or "bauplatz" in t)))


def r(v, step):
    if v in (None, 0, ""):
        return None
    return int(round(float(v) / step))


def main():
    data = json.load(open(STATE, encoding="utf-8"))
    objekte = data["objekte"]
    neu = [o for o in objekte if o.get("erstmals_gesehen") == TODAY]
    alt = [o for o in objekte if o.get("erstmals_gesehen") != TODAY]
    print(f"Neufunde heute: {len(neu)} · Altbestand: {len(alt)}")

    paare = []  # (primaer, dublette, regel)
    used = set()

    def add(prim, dup, regel):
        if id(dup) in used or id(prim) in used or prim is dup:
            return
        used.add(id(dup))
        paare.append((prim, dup, regel))

    # (a) neu/neu mit Ortsname
    grp = defaultdict(list)
    for o in neu:
        k = (norm_ort(o.get("ort")), r(o.get("preis"), 5000), r(o.get("grundflaeche"), 100))
        if all(x is not None and x != "" for x in k):
            grp[k].append(o)
    for k, g in grp.items():
        if len(g) > 1:
            for d in g[1:]:
                add(g[0], d, "a: neu/neu Ort+Preis+Grund")

    # (b) neu/neu ortsunabhaengig
    grp = defaultdict(list)
    for o in neu:
        if id(o) in used:
            continue
        k = (r(o.get("preis"), 5000), r(o.get("grundflaeche"), 100), r(o.get("wohnflaeche"), 10))
        if all(x is not None for x in k):
            grp[k].append(o)
    for k, g in grp.items():
        if len(g) > 1:
            for d in g[1:]:
                add(g[0], d, "b: neu/neu Preis+Grund+WF")

    # (c) neu vs. Altbestand, Haeuser ortsunabhaengig
    alt_h = defaultdict(list)
    for o in alt:
        if is_grund(o):
            continue
        k = (r(o.get("preis"), 5000), r(o.get("wohnflaeche"), 5), r(o.get("grundflaeche"), 100))
        if all(x is not None for x in k):
            alt_h[k].append(o)
    for o in neu:
        if id(o) in used or is_grund(o):
            continue
        k = (r(o.get("preis"), 5000), r(o.get("wohnflaeche"), 5), r(o.get("grundflaeche"), 100))
        if all(x is not None for x in k) and alt_h.get(k):
            add(alt_h[k][0], o, "c: neu vs. alt Haus Preis+WF+Grund")

    # (d) neu vs. Altbestand, Grundstuecke nur mit Ortsname
    alt_g = defaultdict(list)
    for o in alt:
        if not is_grund(o):
            continue
        k = (norm_ort(o.get("ort")), r(o.get("preis"), 5000), r(o.get("grundflaeche"), 100))
        if all(x is not None and x != "" for x in k):
            alt_g[k].append(o)
    for o in neu:
        if id(o) in used or not is_grund(o):
            continue
        k = (norm_ort(o.get("ort")), r(o.get("preis"), 5000), r(o.get("grundflaeche"), 100))
        if all(x is not None and x != "" for x in k) and alt_g.get(k):
            add(alt_g[k][0], o, "d: neu vs. alt Grundstueck Ort+Preis+Grund")

    print(f"\n{len(paare)} Dubletten-Paare gefunden:\n")
    for prim, dup, regel in paare:
        print(f"[{regel}]")
        print(f"   PRIMAER  {prim.get('ort')} | {prim.get('preis')} | WF {prim.get('wohnflaeche')} | G {prim.get('grundflaeche')} | {(prim.get('titel') or '')[:55]}")
        print(f"   DUBLETTE {dup.get('ort')} | {dup.get('preis')} | WF {dup.get('wohnflaeche')} | G {dup.get('grundflaeche')} | {(dup.get('titel') or '')[:55]}")
        print(f"   {prim.get('url')}\n   {dup.get('url')}\n")

    if not APPLY:
        print("(Trockenlauf – mit --apply anwenden)")
        return

    entfernt = 0
    for prim, dup, regel in paare:
        prim.setdefault("url_alt", [])
        for u in [dup.get("url")] + (dup.get("url_alt") or []):
            if u and u != prim.get("url") and u not in prim["url_alt"]:
                prim["url_alt"].append(u)
        for feld in ("bild", "lat", "lon", "freiheits_score", "freiheits_score_detail",
                     "wohnflaeche", "grundflaeche", "nutzflaeche", "widmung", "zustand",
                     "bergblick", "alleinlage", "preis_hinweis"):
            if prim.get(feld) in (None, "", 0) and dup.get(feld) not in (None, "", 0):
                prim[feld] = dup[feld]
        dp, pp = dup.get("preis"), prim.get("preis")
        if isinstance(dp, (int, float)) and isinstance(pp, (int, float)) and dp < pp:
            prim["preis"] = dp
        prim["zuletzt_gesehen"] = TODAY
        prim["fehlt_seit"] = 0
        objekte.remove(dup)
        entfernt += 1

    aktiv = sum(1 for o in objekte if o.get("status") == "aktiv")
    zu_pruefen = sum(1 for o in objekte if o.get("status") == "zu_pruefen")
    h = data["lauf_historie"][-1]
    h["neu"] = h["neu"] - entfernt
    h["aktiv_gesamt"] = aktiv
    h["davon_hart_ok_aktiv"] = aktiv
    h["davon_zu_pruefen"] = zu_pruefen
    h["dubletten_zusammengefuehrt"] = h.get("dubletten_zusammengefuehrt", 0) + entfernt
    json.dump(data, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    dr_path = os.path.join(CAND_DIR, "delta_result.json")
    dr = json.load(open(dr_path, encoding="utf-8"))
    entfernte_urls = {d.get("url") for _, d, _ in paare}
    dr["neu_liste"] = [o for o in dr["neu_liste"] if o.get("url") not in entfernte_urls]
    dr["neu"] = len(dr["neu_liste"])
    dr["gesamt_objekte"] = len(objekte)
    dr["aktiv_gesamt"] = aktiv
    dr["zu_pruefen"] = zu_pruefen
    dr["dubletten"] = dr.get("dubletten", 0) + entfernt
    json.dump(dr, open(dr_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nAngewendet: {entfernt} zusammengeführt. neu={dr['neu']} aktiv={aktiv} zu_pruefen={zu_pruefen} gesamt={len(objekte)}")


if __name__ == "__main__":
    main()
