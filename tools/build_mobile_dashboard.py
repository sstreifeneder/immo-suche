#!/usr/bin/env python3
"""
Erzeugt die mobile, eigenstaendige Dashboard-Datei mit allen Daten direkt eingebettet.
Liest:  ../bekannte_objekte.json   (relativ zu diesem Skript)
Schreibt: ../immobilien-dashboard-mobile.html

Aufruf (am Ende jedes Laufs, nach dem Schreiben von bekannte_objekte.json):
    python3 tools/build_mobile_dashboard.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)  # Projekt-Stammordner (enthaelt bekannte_objekte.json)
SRC = os.path.join(BASE, "bekannte_objekte.json")
OUT = os.path.join(BASE, "immobilien-dashboard-mobile.html")

if not os.path.exists(SRC):
    sys.exit(f"FEHLER: {SRC} nicht gefunden – zuerst bekannte_objekte.json schreiben.")

DATA = json.load(open(SRC, encoding="utf-8"))
DATA_JS = json.dumps(DATA, ensure_ascii=False)

TPL = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=1">
<meta name="theme-color" content="#234e3a">
<title>Höhenmesser – Mobil</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>
:root{
  --snow:#e7ebe4; --surface:#ffffff; --surface-2:#f4f6f1;
  --ink:#16201b; --muted:#6c7a71; --faint:#94a299;
  --line:#d6ddd2; --line-soft:#e4e9df;
  --pine:#2f6b4f; --pine-deep:#234e3a;
  --sun:#dd9f37; --sun-deep:#bd7e1c;
  --amber:#c98326; --danger:#b0493a; --sky:#4d7c8a;
  --shadow:0 1px 2px rgba(20,40,30,.05), 0 8px 24px -12px rgba(20,40,30,.18);
}
*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
html,body{margin:0}
body{background:var(--snow); color:var(--ink); font-family:'IBM Plex Sans',system-ui,-apple-system,Segoe UI,sans-serif; font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased; overscroll-behavior-y:none}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace; font-variant-numeric:tabular-nums}

/* ---------- Header ---------- */
.top{position:relative; overflow:hidden; background:var(--pine-deep); color:#eaf1ea; border-bottom:3px solid var(--sun); padding-top:env(safe-area-inset-top)}
.top__contours{position:absolute; inset:0; opacity:.16; pointer-events:none}
.top__inner{position:relative; padding:16px 15px 14px}
.brand{display:flex; align-items:baseline; gap:9px; flex-wrap:wrap}
.brand h1{font-family:'Fraunces',Georgia,serif; font-weight:600; font-size:23px; letter-spacing:-.01em; margin:0; line-height:1}
.brand .tag{font-size:10.5px; letter-spacing:.12em; text-transform:uppercase; color:#bcd2c4}
.runline{margin-top:6px; font-size:12px; color:#c2d4c8}
.runline b{color:#f0e3c8; font-weight:500}
.stats{display:flex; gap:8px; margin-top:13px; overflow-x:auto; -webkit-overflow-scrolling:touch; scrollbar-width:none; padding-bottom:2px}
.stats::-webkit-scrollbar{display:none}
.stat{flex:0 0 auto; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12); border-radius:11px; padding:8px 12px; min-width:74px}
.stat .n{font-family:'Fraunces',serif; font-size:20px; font-weight:600; line-height:1.05; display:block}
.stat .l{font-size:10px; letter-spacing:.05em; text-transform:uppercase; color:#acc3b4; margin-top:2px; white-space:nowrap}
.stat.is-sun .n{color:var(--sun)} .stat.is-amber .n{color:#f0c27a}

/* ---------- Controls (sticky) ---------- */
.wrap{padding:0 14px 90px}
.controls{position:sticky; top:0; z-index:600; background:var(--snow); padding:10px 0 9px; border-bottom:1px solid var(--line-soft); margin-bottom:13px; display:flex; flex-direction:column; gap:8px}
.row{display:flex; gap:8px}
.segmented{display:flex; background:var(--surface-2); border:1px solid var(--line); border-radius:10px; padding:3px; gap:2px}
.segmented.full{width:100%}
.segmented.full button{flex:1}
.segmented.scroll{overflow-x:auto; -webkit-overflow-scrolling:touch; scrollbar-width:none}
.segmented.scroll::-webkit-scrollbar{display:none}
.segmented button{font:inherit; font-size:13.5px; cursor:pointer; border:0; background:transparent; color:var(--muted); padding:9px 13px; border-radius:8px; transition:.12s; white-space:nowrap; min-height:40px}
.segmented button[aria-pressed="true"]{background:var(--surface); color:var(--pine-deep); font-weight:600; box-shadow:0 1px 2px rgba(20,40,30,.08)}
.field{position:relative; flex:1}
.search{font:inherit; font-size:16px; width:100%; padding:11px 12px 11px 34px; border:1px solid var(--line); border-radius:10px; background:var(--surface); color:var(--ink)}
.search:focus{outline:2px solid var(--pine); outline-offset:1px; border-color:var(--pine)}
.field .ico{position:absolute; left:11px; top:50%; transform:translateY(-50%); color:var(--faint); pointer-events:none}
select.ctl{font:inherit; font-size:14px; flex:1; min-width:0; padding:11px 30px 11px 12px; border:1px solid var(--line); border-radius:10px; background:var(--surface) url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M2 4l4 4 4-4' stroke='%236c7a71' stroke-width='1.5' fill='none' stroke-linecap='round'/></svg>") no-repeat right 11px center; -webkit-appearance:none; appearance:none; color:var(--ink); cursor:pointer; min-height:44px}
select.ctl:focus{outline:2px solid var(--pine); outline-offset:1px}
.count{font-size:12.5px; color:var(--muted); padding:0 2px}

/* ---------- Cards ---------- */
.grid{display:grid; grid-template-columns:1fr; gap:12px}
.card{background:var(--surface); border:1px solid var(--line); border-radius:15px; box-shadow:var(--shadow); padding:14px 14px 12px; display:flex; flex-direction:column; gap:11px}
.card.is-removed{opacity:.62}
.card.is-removed .card__title{text-decoration:line-through; text-decoration-color:var(--faint)}
.card__head{display:flex; gap:12px; align-items:flex-start}
.gauge{flex:0 0 auto; width:58px; text-align:center}
.gauge svg{display:block}
.gauge .lbl{font-size:9px; letter-spacing:.1em; text-transform:uppercase; color:var(--faint); margin-top:1px}
.card__headmain{min-width:0; flex:1}
.badges{display:flex; gap:6px; flex-wrap:wrap; margin-bottom:6px}
.badge{font-size:10.5px; font-weight:600; letter-spacing:.02em; padding:2.5px 8px; border-radius:999px; line-height:1.4; white-space:nowrap}
.badge--top{background:#e4f0e8; color:var(--pine-deep)}
.badge--check{background:#fbeed6; color:#8a5a13}
.badge--neu{background:var(--sun); color:#2a200a}
.badge--removed{background:#f3ddd8; color:#8a3325}
.badge--price{background:#e1ecef; color:#2f5d6b}
.card__title{font-family:'Fraunces',Georgia,serif; font-weight:500; font-size:16.5px; line-height:1.22; color:var(--ink); text-decoration:none; display:block}
.card__loc{font-size:12.5px; color:var(--muted); margin-top:5px; display:flex; align-items:flex-start; gap:5px}
.facts{display:grid; grid-template-columns:1fr 1fr; gap:1px; background:var(--line-soft); border:1px solid var(--line-soft); border-radius:11px; overflow:hidden}
.fact{background:var(--surface); padding:8px 11px}
.fact .l{font-size:10px; letter-spacing:.04em; text-transform:uppercase; color:var(--faint)}
.fact .v{font-size:14px; margin-top:1px; color:var(--ink)}
.fact .v.price{color:var(--pine-deep); font-weight:600}
.tags{display:flex; gap:6px; flex-wrap:wrap}
.chip{font-size:11.5px; color:var(--muted); background:var(--surface-2); border:1px solid var(--line-soft); border-radius:7px; padding:3px 8px; display:inline-flex; align-items:center; gap:5px}
.chip svg{flex:0 0 auto}
.chip.warn{color:#8a5a13; background:#fbf3e2; border-color:#f0dfbd}
.cardfoot{display:flex; align-items:center; gap:10px; margin-top:auto; padding-top:2px}
.more{font:inherit; font-size:13px; color:var(--muted); background:var(--surface-2); border:1px solid var(--line-soft); border-radius:8px; cursor:pointer; padding:9px 12px; display:inline-flex; align-items:center; gap:6px; min-height:40px}
.more svg{transition:transform .15s}
.more[aria-expanded="true"] svg{transform:rotate(180deg)}
.cta{margin-left:auto; font-size:13.5px; font-weight:600; text-decoration:none; color:#fff; background:var(--pine); border:1px solid var(--pine); border-radius:8px; padding:10px 15px; display:inline-flex; align-items:center; gap:6px; min-height:40px}
.cta:active{background:var(--pine-deep)}
.details{display:none; border-top:1px dashed var(--line); padding-top:11px; font-size:13px}
.details.open{display:block}
.drow{display:flex; gap:8px; padding:4px 0; align-items:baseline}
.drow .dl{flex:0 0 86px; color:var(--faint); font-size:11px; letter-spacing:.03em; text-transform:uppercase}
.drow .dv{color:var(--ink); min-width:0}
.scoredetail{font-size:12px; color:var(--muted); background:var(--surface-2); border-radius:8px; padding:8px 10px; margin-top:4px; line-height:1.5}
.empty{text-align:center; padding:60px 20px; color:var(--muted)}
.empty h3{font-family:'Fraunces',serif; font-weight:500; color:var(--ink); margin:0 0 6px}

/* ---------- Map ---------- */
#mapwrap{display:none}
#mapwrap.show{display:block}
.grid.hide{display:none}
#map{height:68vh; min-height:380px; border:1px solid var(--line); border-radius:14px; box-shadow:var(--shadow); z-index:1}
.mapnote{font-size:12px; color:var(--muted); margin:10px 2px 0}
.legend{display:flex; gap:12px; flex-wrap:wrap; margin:11px 2px 0; font-size:11.5px; color:var(--muted)}
.legend span{display:inline-flex; align-items:center; gap:6px}
.legend i{width:11px; height:11px; border-radius:50%; display:inline-block; border:1px solid rgba(0,0,0,.15)}
.leaflet-popup-content{font-family:'IBM Plex Sans',sans-serif; margin:11px 13px}
.pop-t{font-family:'Fraunces',serif; font-weight:500; font-size:15px; color:var(--ink); text-decoration:none; display:block; line-height:1.25}
.pop-m{font-size:12.5px; color:var(--muted); margin:3px 0 7px}
.pop-row{display:flex; gap:10px; align-items:center; font-size:13px}
.pop-score{font-family:'IBM Plex Mono',monospace; font-weight:600; color:#fff; border-radius:6px; padding:1px 7px; font-size:12px}
.pop-cta{display:inline-block; margin-top:8px; font-size:13px; font-weight:500; color:#fff; background:var(--pine); text-decoration:none; border-radius:7px; padding:7px 12px}

footer{padding:6px 16px calc(28px + env(safe-area-inset-bottom)); color:var(--faint); font-size:11.5px; line-height:1.6}
footer code{background:var(--surface-2); border:1px solid var(--line-soft); border-radius:5px; padding:1px 5px; font-size:11px}

/* sehr schmale Geräte */
@media (max-width:360px){ .facts{grid-template-columns:1fr 1fr} .brand h1{font-size:21px} }
@media (prefers-reduced-motion:reduce){*{transition:none!important; animation:none!important}}
.card{animation:rise .35s ease both}
@keyframes rise{from{opacity:0; transform:translateY(6px)}to{opacity:1; transform:none}}
</style>
</head>
<body>
<header class="top">
  <svg class="top__contours" preserveAspectRatio="none" viewBox="0 0 1200 220" aria-hidden="true">
    <g fill="none" stroke="#ffffff" stroke-width="1.2">
      <path d="M-20 180 C 200 120, 360 160, 560 110 S 980 60, 1220 120"/>
      <path d="M-20 150 C 220 95, 380 130, 600 80 S 1000 30, 1220 90"/>
      <path d="M-20 120 C 240 70, 420 100, 640 55 S 1020 10, 1220 65"/>
      <path d="M-20 92 C 260 50, 440 78, 680 35 S 1040 -5, 1220 42"/>
    </g>
  </svg>
  <div class="top__inner">
    <div class="brand"><h1>Höhenmesser</h1><span class="tag">Freiheits-Radar · mobil</span></div>
    <div class="runline" id="runline"></div>
    <div class="stats" id="stats"></div>
  </div>
</header>

<div class="wrap">
  <div class="controls">
    <div class="segmented full" id="viewSeg" role="group" aria-label="Ansicht">
      <button data-v="liste" aria-pressed="true">Liste</button>
      <button data-v="karte" aria-pressed="false">Karte</button>
    </div>
    <div class="field">
      <svg class="ico" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5"/><path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      <input id="q" class="search" type="search" placeholder="Ort, Titel oder Region…">
    </div>
    <div class="segmented scroll" id="statusSeg" role="group" aria-label="Status filtern">
      <button data-s="alle" aria-pressed="true">Alle</button>
      <button data-s="top">Top-Treffer</button>
      <button data-s="pruefen">Zu prüfen</button>
      <button data-s="neu">Neu</button>
      <button data-s="entfernt">Entfernt</button>
    </div>
    <div class="row">
      <select id="region" class="ctl" aria-label="Region"></select>
      <select id="sort" class="ctl" aria-label="Sortierung">
        <option value="score">Freiheits-Score ↓</option>
        <option value="preis_asc">Preis ↑</option>
        <option value="preis_desc">Preis ↓</option>
        <option value="grund">Grundfläche ↓</option>
        <option value="gesehen">Zuletzt gesehen ↓</option>
      </select>
    </div>
    <span class="count" id="count"></span>
  </div>

  <div class="grid" id="grid"></div>

  <div id="mapwrap">
    <div id="map"></div>
    <div class="legend">
      <span><i style="background:#dd9f37"></i> ≥ 85</span>
      <span><i style="background:#3f8a63"></i> 70–84</span>
      <span><i style="background:#4d7c8a"></i> 55–69</span>
      <span><i style="background:#93a39a"></i> &lt; 55 / offen</span>
    </div>
    <div class="mapnote" id="mapnote"></div>
  </div>
</div>

<footer>
  Mobile Testansicht · alle Daten in dieser Datei eingebettet (Stand siehe oben) · Score 0–100 aus Alleinlage, Grundgröße, Bergblick, Ortsferne, Wald &amp; Autarkie · Kartenpins orts-/PLZ-genau (ungefähr). Karte braucht Internet, Liste funktioniert offline.
</footer>

<script>
const EMBEDDED = __DATA_JSON__;
let DATA = EMBEDDED, statusFilter='alle', view='liste';
let map=null, markerLayer=null, mapInit=false;

const $ = s => document.querySelector(s);
const grid = $('#grid');
const fmtEur = n => (typeof n==='number') ? new Intl.NumberFormat('de-AT',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n) : 'auf Anfrage';
const fmtArea = n => (typeof n==='number') ? new Intl.NumberFormat('de-AT').format(n)+' m²' : '–';
const fmtGrund = n => { if(typeof n!=='number') return '–'; const m=new Intl.NumberFormat('de-AT').format(n)+' m²'; return n>=10000?`${m} · ${(n/10000).toLocaleString('de-AT',{maximumFractionDigits:2})} ha`:m; };
const runDate = () => (DATA.letzter_lauf||'').slice(0,10);
const isBaseline = () => { const h=DATA.lauf_historie||[]; return h.length && h[h.length-1].typ==='baseline'; };
const isNeu = o => !isBaseline() && o.erstmals_gesehen===runDate() && o.status!=='entfernt';
const isTop = o => o.hart_ok==='ja' && o.status!=='entfernt';
const isPruefen = o => o.status==='zu_pruefen' || (typeof o.hart_ok==='string' && o.hart_ok.startsWith('TEIL'));
const isRemoved = o => o.status==='entfernt';
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function scoreColor(s){ if(s>=85)return '#dd9f37'; if(s>=70)return '#3f8a63'; if(s>=55)return '#4d7c8a'; return '#93a39a'; }
function gauge(score){
  const s=Math.max(0,Math.min(100,score||0)), r=24, c=2*Math.PI*r, off=c*(1-s/100), col=scoreColor(s);
  const shown = (score==null)?'–':s;
  return `<svg width="58" height="58" viewBox="0 0 60 60" role="img" aria-label="Freiheits-Score ${shown}">
    <circle cx="30" cy="30" r="${r}" fill="none" stroke="var(--line-soft)" stroke-width="6"/>
    <circle cx="30" cy="30" r="${r}" fill="none" stroke="${col}" stroke-width="6" stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" transform="rotate(-90 30 30)"/>
    <text x="30" y="31" text-anchor="middle" font-family="'IBM Plex Mono',monospace" font-size="17" font-weight="500" fill="var(--ink)">${shown}</text>
    <text x="30" y="41" text-anchor="middle" font-family="'IBM Plex Sans',sans-serif" font-size="7" fill="var(--faint)">/ 100</text></svg>`;
}
const pin=`<svg width="12" height="12" viewBox="0 0 16 16" fill="none" style="flex:0 0 auto;margin-top:2px"><path d="M8 14s5-4.5 5-8.5A5 5 0 0 0 3 5.5C3 9.5 8 14 8 14z" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="5.5" r="1.8" stroke="currentColor" stroke-width="1.3"/></svg>`;
const peak=`<svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M2 13l4-8 3 5 2-3 3 6z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>`;
const sunI=`<svg width="12" height="12" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.2"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.4 1.4M11.6 11.6L13 13M13 3l-1.4 1.4M4.4 11.6L3 13" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>`;
const tree=`<svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M8 2l4 6H4zM6 8l2.5 4h-5zM8 14v-2" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>`;

function bergblickChip(o){ const v=(o.bergblick||'').toLowerCase(); if(!v||v.startsWith('unbest')||v.startsWith('nein'))return (v&&v.startsWith('unbest'))?`<span class="chip warn">${peak} Bergblick unbestätigt</span>`:''; if(v.startsWith('teil'))return `<span class="chip">${peak} Bergblick teils</span>`; return `<span class="chip">${peak} Bergblick</span>`; }

function card(o){
  const removed=isRemoved(o), badges=[];
  if(isNeu(o))badges.push('<span class="badge badge--neu">Neu</span>');
  if(removed)badges.push('<span class="badge badge--removed">Entfernt</span>');
  else if(isTop(o))badges.push('<span class="badge badge--top">Erfüllt alle Kriterien</span>');
  else if(isPruefen(o))badges.push('<span class="badge badge--check">Zu prüfen</span>');
  if(o.preis_hinweis && /bieter/i.test(o.preis_hinweis))badges.push('<span class="badge badge--price">Bieterverfahren</span>');
  const tags=[bergblickChip(o)];
  if((o.alleinlage||'').toLowerCase().includes('allein'))tags.push(`<span class="chip">${peak} Alleinlage</span>`);
  if(/holz|pellet|quelle|brunnen|pv|photovolt|autark/i.test((o.zustand||'')+' '+(o.freiheits_score_detail||'')))tags.push(`<span class="chip">${sunI} Autarkie-Plus</span>`);
  if(/wald/i.test(o.freiheits_score_detail||''))tags.push(`<span class="chip">${tree} Wald</span>`);
  return `<article class="card${removed?' is-removed':''}">
    <div class="card__head">
      <div class="gauge">${gauge(o.freiheits_score)}<div class="lbl">Freiheit</div></div>
      <div class="card__headmain">
        <div class="badges">${badges.join('')}</div>
        <a class="card__title" href="${esc(o.url)}" target="_blank" rel="noopener">${esc(o.titel)}</a>
        <div class="card__loc">${pin}<span>${esc(o.ort)} · ${esc(o.region)}</span></div>
      </div>
    </div>
    <div class="facts">
      <div class="fact"><div class="l">Kaufpreis</div><div class="v price">${esc(fmtEur(o.preis))}</div></div>
      <div class="fact"><div class="l">Wohnfläche</div><div class="v">${esc(fmtArea(o.wohnflaeche))}</div></div>
      <div class="fact"><div class="l">Grundstück</div><div class="v">${esc(fmtGrund(o.grundflaeche))}</div></div>
      <div class="fact"><div class="l">Typ</div><div class="v">${esc(o.typ||'–')}</div></div>
    </div>
    <div class="tags">${tags.join('')}</div>
    <div class="cardfoot">
      <button class="more" aria-expanded="false">Details <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
      <a class="cta" href="${esc(o.url)}" target="_blank" rel="noopener">Zum Exposé →</a>
    </div>
    <div class="details">
      ${o.preis_hinweis?`<div class="drow"><span class="dl">Preis-Info</span><span class="dv">${esc(o.preis_hinweis)}</span></div>`:''}
      <div class="drow"><span class="dl">Widmung</span><span class="dv">${esc(o.widmung||'–')}</span></div>
      <div class="drow"><span class="dl">Zustand</span><span class="dv">${esc(o.zustand||'–')}</span></div>
      <div class="drow"><span class="dl">Einordnung</span><span class="dv">${esc(o.hart_ok==='ja'?'Erfüllt alle harten Kriterien':o.hart_ok)}</span></div>
      <div class="drow"><span class="dl">Gesehen</span><span class="dv mono">${esc(o.erstmals_gesehen)} → ${esc(o.zuletzt_gesehen)}${o.fehlt_seit?` · fehlt seit ${o.fehlt_seit}`:''}</span></div>
      <div class="scoredetail">${esc(o.freiheits_score_detail||'')}</div>
    </div>
  </article>`;
}

function passes(o){
  if(statusFilter==='top'&&!isTop(o))return false;
  if(statusFilter==='pruefen'&&!isPruefen(o))return false;
  if(statusFilter==='neu'&&!isNeu(o))return false;
  if(statusFilter==='entfernt'&&!isRemoved(o))return false;
  const reg=$('#region').value; if(reg!=='alle'&&o.region!==reg)return false;
  const q=$('#q').value.trim().toLowerCase();
  if(q){const hay=(o.titel+' '+o.ort+' '+o.region+' '+o.typ).toLowerCase(); if(!hay.includes(q))return false;}
  return true;
}
function getList(){
  const key=$('#sort').value, num=v=>(typeof v==='number'?v:-Infinity);
  const arr=(DATA.objekte||[]).filter(passes);
  if(key==='score')arr.sort((a,b)=>(b.freiheits_score||0)-(a.freiheits_score||0));
  else if(key==='preis_asc')arr.sort((a,b)=>(typeof a.preis==='number'?a.preis:Infinity)-(typeof b.preis==='number'?b.preis:Infinity));
  else if(key==='preis_desc')arr.sort((a,b)=>num(b.preis)-num(a.preis));
  else if(key==='grund')arr.sort((a,b)=>num(b.grundflaeche)-num(a.grundflaeche));
  else if(key==='gesehen')arr.sort((a,b)=>String(b.zuletzt_gesehen).localeCompare(String(a.zuletzt_gesehen)));
  return arr;
}
function renderList(list){
  grid.innerHTML=list.length?list.map(card).join(''):`<div class="empty"><h3>Keine Objekte für diese Filter</h3><p>Setz Suche oder Status zurück.</p></div>`;
  grid.querySelectorAll('.more').forEach(btn=>btn.addEventListener('click',()=>{
    const d=btn.closest('.card').querySelector('.details'); const open=d.classList.toggle('open'); btn.setAttribute('aria-expanded',open?'true':'false');
  }));
}
function popup(o){
  const s=o.freiheits_score; const col=scoreColor(s||0);
  return `<a class="pop-t" href="${esc(o.url)}" target="_blank" rel="noopener">${esc(o.titel)}</a>
    <div class="pop-m">${esc(o.ort)} · ${esc(o.region)}</div>
    <div class="pop-row"><span class="pop-score" style="background:${col}">${s==null?'–':s}</span><b>${esc(fmtEur(o.preis))}</b></div>
    <div class="pop-row" style="color:var(--muted);margin-top:3px">${esc(fmtArea(o.wohnflaeche))} Wfl · ${esc(fmtGrund(o.grundflaeche))}</div>
    <a class="pop-cta" href="${esc(o.url)}" target="_blank" rel="noopener">Zum Exposé →</a>`;
}
function renderMap(list){
  const note=$('#mapnote');
  if(typeof L==='undefined'){ note.textContent='Die Karte benötigt eine Internetverbindung (Kartenbibliothek + Kacheln). Die Liste funktioniert offline.'; return; }
  if(!mapInit){
    map=L.map('map',{scrollWheelZoom:false});
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'&copy; OpenStreetMap'}).addTo(map);
    markerLayer=L.layerGroup().addTo(map); mapInit=true;
  }
  markerLayer.clearLayers();
  const pts=[]; let ohne=0;
  list.forEach(o=>{
    if(typeof o.lat==='number'&&typeof o.lon==='number'){
      const s=o.freiheits_score||0;
      const m=L.circleMarker([o.lat,o.lon],{radius:7+s/12,color:'#16201b',weight:1.2,fillColor:scoreColor(s),fillOpacity:.88});
      m.bindPopup(popup(o)); markerLayer.addLayer(m); pts.push([o.lat,o.lon]);
    } else ohne++;
  });
  setTimeout(()=>map.invalidateSize(),60);
  if(pts.length)map.fitBounds(pts,{padding:[30,30],maxZoom:11}); else map.setView([47.6,14.2],7);
  note.textContent = ohne?`${ohne} Objekt(e) ohne Koordinaten – in der Liste sichtbar. Pins sind ungefähr (Ort/PLZ).`:'Pins sind ungefähr (Ort/PLZ), nicht die exakte Liegenschaft.';
}
function render(){
  const list=getList();
  $('#count').textContent=`${list.length} von ${(DATA.objekte||[]).length} Objekten`;
  if(view==='liste') renderList(list); else renderMap(list);
}
function header(){
  const o=DATA.objekte||[];
  const aktiv=o.filter(x=>!isRemoved(x)).length, top=o.filter(isTop).length, pruefen=o.filter(isPruefen).length, neu=o.filter(isNeu).length, entfernt=o.filter(isRemoved).length;
  const prices=o.filter(x=>isTop(x)&&typeof x.preis==='number').map(x=>x.preis);
  const avg=prices.length?Math.round(prices.reduce((a,b)=>a+b,0)/prices.length):null;
  const dt=DATA.letzter_lauf?new Date(DATA.letzter_lauf):null;
  const when=dt?dt.toLocaleString('de-AT',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}):'–';
  const h=DATA.lauf_historie||[], last=h[h.length-1]||{};
  const kind=isBaseline()?'Baseline':`Delta: ${last.neu??0} neu · ${last.preisaenderungen??0} Preis · ${last.entfernt??0} entfernt`;
  $('#runline').innerHTML=`Stand <b>${esc(when)}</b> · ${esc(kind)}`;
  const stat=(n,l,cls='')=>`<div class="stat ${cls}"><span class="n">${n}</span><span class="l">${l}</span></div>`;
  $('#stats').innerHTML=stat(aktiv,'Aktiv')+stat(top,'Top','is-sun')+stat(pruefen,'Prüfen','is-amber')+stat(neu,'Neu')+stat(entfernt,'Entfernt')+stat(avg!=null?fmtEur(avg):'–','Ø Top');
  const regions=[...new Set(o.map(x=>x.region))].sort((a,b)=>a.localeCompare(b,'de'));
  const sel=$('#region'), cur=sel.value||'alle';
  sel.innerHTML=`<option value="alle">Alle Regionen</option>`+regions.map(r=>`<option value="${esc(r)}">${esc(r)}</option>`).join('');
  sel.value=[...sel.options].some(op=>op.value===cur)?cur:'alle';
}

$('#q').addEventListener('input',render);
$('#region').addEventListener('change',render);
$('#sort').addEventListener('change',render);
$('#statusSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;statusFilter=b.dataset.s;[...e.currentTarget.children].forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));render();});
$('#viewSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;view=b.dataset.v;[...e.currentTarget.children].forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));
  $('#grid').classList.toggle('hide',view!=='liste'); $('#mapwrap').classList.toggle('show',view==='karte'); render();});

header(); render();
</script>
</body>
</html>
"""

out = TPL.replace("__DATA_JSON__", DATA_JS)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(out)

print(f"OK: {OUT} ({len(out)} Bytes, {len(DATA.get('objekte', []))} Objekte eingebettet)")
