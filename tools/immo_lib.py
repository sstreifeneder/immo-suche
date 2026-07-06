#!/usr/bin/env python3
"""immo_lib.py – gemeinsame Normalisierung + Dedup-Helfer fuer den Immobilien-Lauf.

url_norm  = normalisierte URL (Primaerschluessel)
dedup_fp  = Inhalts-Fingerprint (Zweitschluessel) aus Ort+Preis+Wohnflaeche+Grundflaeche
            (bei Baugrundstuecken ohne Wohnflaeche)
"""
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "cid",
                 "source", "utm_source", "utm_medium", "utm_campaign",
                 "utm_term", "utm_content", "wt_mc", "trackingId"}


def url_norm(url: str) -> str:
    """Schema/Host klein, fuehrendes www. weg, Tracking-Params + Anker weg, trailing / weg."""
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    parts = urlsplit(url)
    scheme = (parts.scheme or "https").lower()
    host = (parts.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    # query filtern
    q = [(k, v) for (k, v) in parse_qsl(parts.query, keep_blank_values=False)
         if not (k.lower() in TRACKING_KEYS or any(k.lower().startswith(p) for p in TRACKING_PREFIXES))]
    query = urlencode(q)
    path = parts.path or ""
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return urlunsplit((scheme, host, path, query, ""))  # Anker (fragment) verworfen


def _plz_or_ort(ort: str) -> str:
    if not ort:
        return ""
    ort = str(ort)
    m = re.search(r"\b(\d{4,5})\b", ort)  # AT 4-stellig, IT 5-stellig
    if m:
        return m.group(1)
    # sonst kleingeschriebener Ortsname ohne Bez.-Zusatz / Klammern
    ort = re.split(r"[(/,]", ort)[0]
    ort = re.sub(r"\b(bez\.?|bezirk)\b.*", "", ort, flags=re.I)
    return re.sub(r"\s+", "", ort.strip().lower())


def _round(v, step):
    try:
        return int(round(float(v) / step) * step)
    except (TypeError, ValueError):
        return None


def dedup_fp(ort, preis, wohnflaeche, grundflaeche, is_grundstueck=False):
    """Fingerprint aus Ort|Preis|Wohnflaeche|Grundflaeche (gerundet). Grundstueck: ohne WF.
    Gueltig nur, wenn >=3 der 4 (bzw. >=3 der 3 bei Grundstueck) Werte bekannt sind."""
    o = _plz_or_ort(ort)
    p = _round(preis, 5000)
    g = _round(grundflaeche, 100)
    if is_grundstueck:
        vals = [o or None, p, g]
        known = sum(1 for x in vals if x not in (None, "", 0))
        if known < 3:
            return None
        return f"{o}|{p}|{g}"
    w = _round(wohnflaeche, 5)
    vals = [o or None, p, w, g]
    known = sum(1 for x in vals if x not in (None, "", 0))
    if known < 3:
        return None
    return f"{o}|{p}|{w}|{g}"


if __name__ == "__main__":
    # Selbsttest
    assert url_norm("https://www.immobilienscout24.at/expose/123?utm_source=x#foto") == \
        "https://immobilienscout24.at/expose/123"
    assert url_norm("https://WWW.Willhaben.at/iad/immobilien/d/haus/1/") == \
        "https://willhaben.at/iad/immobilien/d/haus/1"
    print("dedup_fp Haus:", dedup_fp("8453 Eichberg", 635000, 210, 37744))
    print("dedup_fp Grund:", dedup_fp("9871 Seeboden", 145000, None, 1450, is_grundstueck=True))
    print("immo_lib OK")
