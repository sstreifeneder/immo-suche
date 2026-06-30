/* app.js – gemeinsamer Kern fuer index.html (Desktop) und mobile.html (PWA).
   Laedt data.json, verbindet Firebase (anonyme Geraete-Identitaet), verwaltet
   Bewertungen/Namen/Besuche und liefert Filter-/Sortier-/Konsens-Logik.
   Reines Rendering macht jede Seite selbst. */
window.Immo = (function () {
  "use strict";

  const WEIGHTS = { sehr_interessant: 2, interessant: 1, uninteressant: -2 };
  const RATING_LABELS = {
    sehr_interessant: "sehr interessant",
    interessant: "interessant",
    uninteressant: "uninteressant",
  };
  const RATING_ORDER = ["sehr_interessant", "interessant", "uninteressant"];

  // ---- stabiler Hash (cyrb53) fuer Firestore-Doc-IDs aus url_norm ----
  function hash(str) {
    str = String(str || "");
    let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    for (let i = 0, ch; i < str.length; i++) {
      ch = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
    h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
    h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(16);
  }

  // ---- State ----
  let auth = null, db = null, uid = null, myName = null, ready = false;

  // ---- Daten laden ----
  async function loadData() {
    const r = await fetch("data.json?cb=" + Date.now(), { cache: "no-store" });
    if (!r.ok) throw new Error("data.json HTTP " + r.status);
    return await r.json();
  }

  // ---- Firebase ----
  function firebaseAvailable() {
    return !!(window.firebaseConfig && window.firebase && window.firebaseConfig.apiKey);
  }

  async function initFirebase() {
    if (!firebaseAvailable()) {
      console.warn("[Immo] Firebase nicht konfiguriert – Bewertungen deaktiviert.");
      return null;
    }
    try {
      if (!firebase.apps.length) firebase.initializeApp(window.firebaseConfig);
      auth = firebase.auth();
      db = firebase.firestore();
      await new Promise((resolve) => {
        let done = false;
        auth.onAuthStateChanged(async (user) => {
          if (user && !done) {
            done = true;
            uid = user.uid;
            ready = true;
            await loadMyName();
            resolve();
          }
        });
        auth.signInAnonymously().catch((e) => {
          console.error("[Immo] Anonyme Anmeldung fehlgeschlagen:", e);
          if (!done) { done = true; resolve(); }
        });
      });
      return uid;
    } catch (e) {
      console.error("[Immo] Firebase-Init fehlgeschlagen:", e);
      return null;
    }
  }

  function isReady() { return ready; }
  function getUid() { return uid; }

  async function loadMyName() {
    try {
      const d = await db.collection("users").doc(uid).get();
      myName = d.exists ? (d.data().name || null) : null;
    } catch (e) { myName = null; }
  }
  function getMyName() { return myName; }
  async function setMyName(name) {
    myName = (name || "").trim() || null;
    if (!ready) return;
    await db.collection("users").doc(uid).set({ name: myName, ts: Date.now() }, { merge: true });
  }

  // ---- Bewertungen ----
  function ratingDocId(url_norm) { return uid + "_" + hash(url_norm); }

  async function setRating(url_norm, wert) {
    if (!ready) throw new Error("Firebase nicht bereit");
    const ref = db.collection("ratings").doc(ratingDocId(url_norm));
    if (wert === null || wert === undefined) {
      await ref.delete();
    } else {
      await ref.set({ uid, name: myName || "", url_norm, wert, ts: Date.now() });
    }
  }

  // Live-Abo aller Bewertungen (Familie): cb(byUrl) mit byUrl[url_norm] = [{uid,name,wert,ts}]
  function subscribeRatings(cb) {
    if (!ready) { cb({}); return function () {}; }
    return db.collection("ratings").onSnapshot(
      (snap) => {
        const byUrl = {};
        snap.forEach((d) => {
          const r = d.data();
          (byUrl[r.url_norm] = byUrl[r.url_norm] || []).push(r);
        });
        cb(byUrl);
      },
      (err) => { console.error("[Immo] ratings-Abo:", err); cb({}); }
    );
  }

  function myRating(byUrl, url_norm) {
    const arr = byUrl[url_norm] || [];
    const m = arr.find((r) => r.uid === uid);
    return m ? m.wert : null;
  }
  function consensus(byUrl, url_norm) {
    const arr = byUrl[url_norm] || [];
    let score = 0;
    arr.forEach((r) => { score += WEIGHTS[r.wert] || 0; });
    return { score, items: arr };
  }

  // ---- Besuche / "neu seit letztem Besuch" ----
  async function getLastSeen() {
    if (!ready) return null;
    try {
      const d = await db.collection("views").doc(uid).get();
      return d.exists ? (d.data().last_seen || null) : null;
    } catch (e) { return null; }
  }
  async function touchLastSeen() {
    if (!ready) return;
    try {
      await db.collection("views").doc(uid).set({ last_seen: new Date().toISOString() }, { merge: true });
    } catch (e) {}
  }

  // ---- Ableitungen / Helfer ----
  function bundesland(o) {
    return String(o.region || "").split("(")[0].trim() || "—";
  }
  function hartKat(o) {
    const h = String(o.hart_ok || "").toLowerCase();
    if (h === "ja") return "erfuellt";
    if (h.includes("verfehlt")) return "verfehlt";
    return "teil";
  }
  function hartLabel(kat) {
    return { erfuellt: "erfüllt", teil: "teils", verfehlt: "verfehlt" }[kat] || kat;
  }
  function isNewSince(o, lastSeen) {
    if (!lastSeen) return false;
    return String(o.erstmals_gesehen || "") > String(lastSeen).slice(0, 10);
  }
  function isLastRun(o, meta) {
    return meta && meta.letzter_lauf_datum && o.erstmals_gesehen === meta.letzter_lauf_datum;
  }

  function fmtPreis(p) {
    if (p === null || p === undefined || p === "" || p === 0) return "Preis a. A.";
    const n = typeof p === "number" ? p : parseInt(String(p).replace(/[^\d]/g, ""), 10);
    if (!n) return "Preis a. A.";
    return n.toLocaleString("de-DE") + " €";
  }
  function fmtNum(v, unit) {
    if (v === null || v === undefined || v === "" || v === 0) return "—";
    const n = typeof v === "number" ? v : parseFloat(String(v).replace(/[^\d.,]/g, "").replace(",", "."));
    if (!isFinite(n)) return "—";
    return Math.round(n).toLocaleString("de-DE") + (unit ? " " + unit : "");
  }

  // ---- Filter & Sortierung ----
  // f: {onlyLastRun, newSinceVisit, region, status, hart, myWert, hideUninteressant, search}
  // ctx: {meta, byUrl, lastSeen}
  function applyFilters(objekte, f, ctx) {
    f = f || {};
    const byUrl = (ctx && ctx.byUrl) || {};
    const meta = ctx && ctx.meta;
    const lastSeen = ctx && ctx.lastSeen;
    const q = (f.search || "").trim().toLowerCase();

    return objekte.filter((o) => {
      if (f.onlyLastRun && !isLastRun(o, meta)) return false;
      if (f.newSinceVisit && !isNewSince(o, lastSeen)) return false;
      if (f.region && bundesland(o) !== f.region) return false;
      if (f.status && (o.status || "") !== f.status) return false;
      if (f.hart && hartKat(o) !== f.hart) return false;

      const mine = myRating(byUrl, o.url_norm);
      if (f.hideUninteressant && mine === "uninteressant") return false;
      if (f.myWert) {
        if (f.myWert === "unbewertet") { if (mine) return false; }
        else if (mine !== f.myWert) return false;
      }
      if (q) {
        const hay = (o.titel + " " + o.ort + " " + o.region + " " + (o.typ || "")).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function numOr(v, fallback) {
    const n = typeof v === "number" ? v : parseInt(String(v || "").replace(/[^\d]/g, ""), 10);
    return isFinite(n) && n > 0 ? n : fallback;
  }

  function sortObjekte(arr, key, ctx) {
    const byUrl = (ctx && ctx.byUrl) || {};
    const a = arr.slice();
    const cmp = {
      gefunden_neu: (x, y) => String(y.erstmals_gesehen || "").localeCompare(String(x.erstmals_gesehen || "")) ||
                              (numOr(y.freiheits_score, 0) - numOr(x.freiheits_score, 0)),
      gefunden_alt: (x, y) => String(x.erstmals_gesehen || "").localeCompare(String(y.erstmals_gesehen || "")),
      score:        (x, y) => numOr(y.freiheits_score, 0) - numOr(x.freiheits_score, 0),
      preis_auf:    (x, y) => numOr(x.preis, 9e12) - numOr(y.preis, 9e12),
      preis_ab:     (x, y) => numOr(y.preis, -1) - numOr(x.preis, -1),
      konsens:      (x, y) => consensus(byUrl, y.url_norm).score - consensus(byUrl, x.url_norm).score ||
                              (numOr(y.freiheits_score, 0) - numOr(x.freiheits_score, 0)),
    }[key] || (() => 0);
    a.sort(cmp);
    return a;
  }

  function regionsList(objekte) {
    return Array.from(new Set(objekte.map(bundesland))).filter((x) => x && x !== "—").sort();
  }

  return {
    WEIGHTS, RATING_LABELS, RATING_ORDER, hash,
    loadData, firebaseAvailable, initFirebase, isReady, getUid,
    getMyName, setMyName,
    setRating, subscribeRatings, myRating, consensus,
    getLastSeen, touchLastSeen,
    bundesland, hartKat, hartLabel, isNewSince, isLastRun,
    fmtPreis, fmtNum, applyFilters, sortObjekte, regionsList,
  };
})();
