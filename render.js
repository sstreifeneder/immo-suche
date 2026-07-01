/* render.js – gemeinsame Oberflaechen-Logik (Filterleiste, Karten, Bewerten, Namen).
   Wird von index.html und mobile.html genutzt. Baut auf window.Immo (app.js) auf. */
(function () {
  "use strict";
  const I = window.Immo;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  const SORTS = [
    ["gefunden_neu", "Neueste zuerst"],
    ["gefunden_alt", "Älteste zuerst"],
    ["score", "Freiheits-Score"],
    ["konsens", "Familien-Favoriten"],
    ["preis_auf", "Preis aufsteigend"],
    ["preis_ab", "Preis absteigend"],
  ];

  function filterBarHTML(regions) {
    const ropts = ['<option value="">Alle Regionen</option>']
      .concat(regions.map((r) => `<option value="${esc(r)}">${esc(r)}</option>`)).join("");
    const sopts = SORTS.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("");
    return `
      <input type="text" id="f-search" placeholder="Suche Ort, Titel, Typ…" autocomplete="off">
      <select id="f-sort" title="Sortierung">${sopts}</select>
      <select id="f-region">${ropts}</select>
      <select id="f-status" title="Status">
        <option value="">Status: alle</option>
        <option value="aktiv">aktiv</option>
        <option value="zu_pruefen">zu prüfen</option>
        <option value="entfernt">entfernt</option>
      </select>
      <select id="f-hart" title="Harte Kriterien">
        <option value="">Kriterien: alle</option>
        <option value="erfuellt">erfüllt</option>
        <option value="teil">teils</option>
        <option value="verfehlt">verfehlt</option>
      </select>
      <select id="f-mine" title="Meine Bewertung">
        <option value="">Bewertung: alle</option>
        <option value="sehr_interessant">sehr interessant</option>
        <option value="interessant">interessant</option>
        <option value="uninteressant">uninteressant</option>
        <option value="unbewertet">unbewertet</option>
      </select>
      <span class="chiptoggle" data-toggle="onlyLastRun">Nur letzter Lauf</span>
      <span class="chiptoggle" data-toggle="newSinceVisit">Neu seit Besuch</span>
      <span class="chiptoggle" data-toggle="hideUninteressant">Uninteressant aus</span>
    `;
  }

  function ratingButtons(mine) {
    return I.RATING_ORDER.map((w) => {
      const on = mine === w ? " on " + w : "";
      const ic = { sehr_interessant: "★", interessant: "♥", uninteressant: "✕" }[w];
      return `<button class="${w}${on}" data-act="rate" data-wert="${w}">
                <span class="ic">${ic}</span>${esc(I.RATING_LABELS[w])}</button>`;
    }).join("");
  }

  function consensusHTML(items) {
    if (!items || !items.length) return "";
    const chips = items.slice().sort((a, b) => (I.WEIGHTS[b.wert] || 0) - (I.WEIGHTS[a.wert] || 0))
      .map((r) => `<span class="who"><b>${esc(r.name || "?")}</b>: <span class="v ${r.wert}">${esc(I.RATING_LABELS[r.wert] || r.wert)}</span></span>`)
      .join("");
    return `<div class="consensus">${chips}</div>`;
  }

  function cardHTML(o, ctx) {
    const isNew = I.isNewSince(o, ctx.lastSeen);
    const kat = I.hartKat(o);
    const mine = I.myRating(ctx.byUrl, o.url_norm);
    const cons = I.consensus(ctx.byUrl, o.url_norm);
    const statusBadge = o.status === "entfernt" ? `<span class="badge entfernt">entfernt</span>`
      : o.status === "zu_pruefen" ? `<span class="badge teil">zu prüfen</span>` : "";
    const score = (o.freiheits_score || o.freiheits_score === 0)
      ? `<span class="badge score" title="${esc(o.freiheits_score_detail || "")}">Freiheit ${esc(o.freiheits_score)}</span>` : "";
    return `
      <div class="card${isNew ? " new" : ""}" data-url="${esc(o.url_norm)}">
        ${isNew ? '<div class="ribbon">NEU</div>' : ""}
        <h3>${esc(o.titel || "(ohne Titel)")}</h3>
        <div class="loc">${esc(o.ort || "")}${o.region ? " · " + esc(o.region) : ""}</div>
        <div class="row">
          <span class="price">${esc(I.fmtPreis(o.preis))}</span>
        </div>
        <div class="row">
          <span class="fact">Wohnfl. <b>${esc(I.fmtNum(o.wohnflaeche, "m²"))}</b></span>
          <span class="fact">Grund <b>${esc(I.fmtNum(o.grundflaeche, "m²"))}</b></span>
          <span class="fact">Typ <b>${esc(o.typ || "—")}</b></span>
          <span class="fact">gef. <b>${esc(o.erstmals_gesehen || "—")}</b></span>
        </div>
        <div class="badges">
          ${score}
          <span class="badge ${kat}">${esc(I.hartLabel(kat))}</span>
          ${o.bergblick && o.bergblick !== "nein" ? '<span class="badge">Bergblick</span>' : ""}
          ${o.alleinlage ? `<span class="badge">${esc(o.alleinlage)}</span>` : ""}
          ${statusBadge}
        </div>
        <div class="rate">${ratingButtons(mine)}</div>
        ${consensusHTML(cons.items)}
        <div class="cardlinks">
          <a href="${esc(o.url)}" target="_blank" rel="noopener">Inserat öffnen ↗</a>
          ${o.lat && o.lon ? `<a href="https://www.google.com/maps?q=${o.lat},${o.lon}" target="_blank" rel="noopener">Karte ↗</a>` : ""}
        </div>
      </div>`;
  }

  // ---- Name-Modal (geteilt) ----
  function ensureModal() {
    if (document.getElementById("name-modal")) return;
    const el = document.createElement("div");
    el.className = "modal-bg";
    el.id = "name-modal";
    el.innerHTML = `<div class="modal">
        <h2>Wie heißt du?</h2>
        <p>Dein Name erscheint bei deinen Bewertungen, damit die Familie den Konsens sieht. Nur einmal nötig, später änderbar.</p>
        <input type="text" id="name-input" maxlength="24" placeholder="z. B. Stefan">
        <button class="btn" id="name-save">Speichern</button>
      </div>`;
    document.body.appendChild(el);
  }
  function askName(prefill) {
    ensureModal();
    return new Promise((resolve) => {
      const bg = document.getElementById("name-modal");
      const inp = document.getElementById("name-input");
      const save = document.getElementById("name-save");
      inp.value = prefill || I.getMyName() || "";
      bg.classList.add("show");
      inp.focus();
      const done = async () => {
        const v = inp.value.trim();
        if (!v) { inp.focus(); return; }
        await I.setMyName(v);
        bg.classList.remove("show");
        save.removeEventListener("click", done);
        resolve(v);
      };
      save.addEventListener("click", done);
      inp.onkeydown = (e) => { if (e.key === "Enter") done(); };
    });
  }

  // ---- App-Controller ----
  function createApp(opts) {
    const listEl = opts.listEl;
    const filtersEl = opts.filtersEl;
    const countEl = opts.countEl;
    const state = { data: null, byUrl: {}, lastSeen: null, filters: {
      search: "", sort: "gefunden_neu", region: "", status: "", hart: "", myWert: "",
      onlyLastRun: false, newSinceVisit: false, hideUninteressant: false,
    } };

    function ctx() { return { meta: state.data.meta, byUrl: state.byUrl, lastSeen: state.lastSeen }; }

    function getFiltered() {
      let arr = I.applyFilters(state.data.objekte, state.filters, ctx());
      arr = I.sortObjekte(arr, state.filters.sort, ctx());
      return arr;
    }

    function refresh() {
      const arr = getFiltered();
      if (!arr.length) {
        listEl.innerHTML = '<div class="empty">Keine Objekte für diese Auswahl.</div>';
      } else {
        listEl.innerHTML = arr.map((o) => cardHTML(o, ctx())).join("");
      }
      if (countEl) countEl.textContent = arr.length + " von " + state.data.objekte.length + " Objekten";
      if (opts.onRendered) opts.onRendered(arr, ctx());
    }

    function wireFilters() {
      filtersEl.innerHTML = filterBarHTML(I.regionsList(state.data.objekte));
      const bind = (id, key, ev = "change") => {
        const el = document.getElementById(id);
        if (el) el.addEventListener(ev, () => { state.filters[key] = el.value; refresh(); });
      };
      bind("f-search", "search", "input");
      bind("f-sort", "sort");
      bind("f-region", "region");
      bind("f-status", "status");
      bind("f-hart", "hart");
      bind("f-mine", "myWert");
      filtersEl.querySelectorAll(".chiptoggle").forEach((c) => {
        c.addEventListener("click", () => {
          const k = c.getAttribute("data-toggle");
          state.filters[k] = !state.filters[k];
          c.classList.toggle("active", state.filters[k]);
          refresh();
        });
      });
    }

    function wireRatings() {
      listEl.addEventListener("click", async (e) => {
        const btn = e.target.closest('[data-act="rate"]');
        if (!btn) return;
        if (!I.isReady()) { alert("Bewertungen sind noch nicht verbunden (Firebase). Bitte kurz warten und neu laden."); return; }
        const card = btn.closest(".card");
        const urlNorm = card.getAttribute("data-url");
        const wert = btn.getAttribute("data-wert");
        if (!I.getMyName()) { await askName(); }
        const current = I.myRating(state.byUrl, urlNorm);
        try {
          await I.setRating(urlNorm, current === wert ? null : wert); // erneuter Klick = löschen
        } catch (err) { console.error(err); alert("Speichern fehlgeschlagen."); }
        // UI aktualisiert sich via subscribeRatings-Snapshot automatisch
      });
    }

    async function start() {
      state.data = await I.loadData();
      wireFilters();
      wireRatings(); // Klick-Handler für die Bewerten-Buttons aktivieren
      refresh(); // erste Anzeige ohne Bewertungen

      await I.initFirebase();
      if (!I.isReady()) {
        const w = document.createElement("div");
        w.className = "fbwarn";
        w.textContent = "Bewertungen offline – Firebase nicht verbunden. Objektdaten werden trotzdem angezeigt.";
        filtersEl.parentNode.insertBefore(w, filtersEl.nextSibling);
      } else {
        state.lastSeen = await I.getLastSeen();
        I.subscribeRatings((byUrl) => { state.byUrl = byUrl; refresh(); });
        I.touchLastSeen(); // markiert „jetzt" als letzten Besuch für die nächste Sitzung
      }
      refresh();
    }

    return { start, refresh, getFiltered, askName, state };
  }

  window.Immo.ui = { esc, cardHTML, createApp, askName };
})();
