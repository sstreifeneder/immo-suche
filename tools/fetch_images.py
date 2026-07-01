#!/usr/bin/env python3
"""fetch_images.py – laedt fehlende Objektbilder (Feld `bild`) lokal ins Repo.
Laeuft auf dem Mac (braucht Netz), wird vom Auto-Push aufgerufen. Nicht-destruktiv:
setzt pro Objekt `bild_lokal` = images/<hash>.<ext>. Bereits vorhandene Dateien werden
uebersprungen (nur neue werden geladen). Anschliessend erzeugt der Auto-Push data.json neu."""
import json, os, hashlib, glob, ssl, datetime
import urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "bekannte_objekte.json")
IMGDIR = os.path.join(ROOT, "images")
LOG = os.path.expanduser("~/Library/Logs/immo-images.log")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
EXT = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/pjpeg": ".jpg",
       "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}\n")
    except Exception:
        pass


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        return urllib.request.urlopen(req, timeout=25)
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), ssl.SSLError):
            return urllib.request.urlopen(req, timeout=25, context=ssl._create_unverified_context())
        raise


def main():
    os.makedirs(IMGDIR, exist_ok=True)
    data = json.load(open(SRC, encoding="utf-8"))
    dl = fail = changed = 0

    for o in data["objekte"]:
        bild = o.get("bild")
        key = o.get("url_norm") or o.get("url")
        if not bild or not key:
            continue
        h = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]

        existing = glob.glob(os.path.join(IMGDIR, h + ".*"))
        if existing:
            rel = "images/" + os.path.basename(existing[0])
            if o.get("bild_lokal") != rel:
                o["bild_lokal"] = rel
                changed += 1
            continue

        try:
            with fetch(bild) as r:
                ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                if not ct.startswith("image/"):
                    fail += 1
                    log(f"kein Bild ({ct or '?'}) {bild[:90]}")
                    continue
                blob = r.read()
            if len(blob) < 800:  # zu klein -> vermutlich Platzhalter/Fehlerbild
                fail += 1
                log(f"zu klein ({len(blob)}B) {bild[:90]}")
                continue
            fn = h + EXT.get(ct, ".jpg")
            with open(os.path.join(IMGDIR, fn), "wb") as f:
                f.write(blob)
            o["bild_lokal"] = "images/" + fn
            dl += 1
            changed += 1
        except Exception as e:
            fail += 1
            log(f"FEHLER {bild[:90]}: {e}")

    if changed:
        json.dump(data, open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log(f"fertig: {dl} geladen, {fail} fehlgeschlagen, {changed} Objekte aktualisiert")
    print(f"Bilder: {dl} geladen, {fail} fehlgeschlagen, {changed} Objekte aktualisiert")


if __name__ == "__main__":
    main()
