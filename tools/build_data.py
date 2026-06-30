#!/usr/bin/env python3
"""build_data.py – erzeugt data.json (von der Web-App gelesen) aus bekannte_objekte.json.

Aufruf (pfad-relativ, egal wo der Projektordner liegt):
    python3 tools/build_data.py

Ergebnis: ./data.json  = { "meta": {...}, "objekte": [...] }
Wird vom Lauf nach dem Schreiben von bekannte_objekte.json ausgefuehrt.
"""
import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "bekannte_objekte.json")
OUT = os.path.join(ROOT, "data.json")


def lauf_datum(s):
    """ISO-Zeitstempel -> reines Datum (YYYY-MM-DD) fuer den 'letzter Lauf'-Filter."""
    if not s or not isinstance(s, str):
        return None
    return s[:10]


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    objekte = data.get("objekte", [])
    letzter_lauf = data.get("letzter_lauf")

    out = {
        "meta": {
            "letzter_lauf": letzter_lauf,
            "letzter_lauf_datum": lauf_datum(letzter_lauf),
            "anzahl": len(objekte),
            "anzahl_aktiv": sum(1 for o in objekte if o.get("status") == "aktiv"),
            "schema_version": data.get("schema_version"),
            "generiert_am": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "lauf_historie": data.get("lauf_historie", [])[-12:],
        },
        "objekte": objekte,
    }

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"OK: data.json geschrieben ({len(objekte)} Objekte, letzter Lauf {out['meta']['letzter_lauf_datum']})")


if __name__ == "__main__":
    main()
