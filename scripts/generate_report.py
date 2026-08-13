#!/usr/bin/env python3
"""Build report/index.html from data/changes/*.json + data/legislation/*.json.

Two layers, one page:
  - "Form instructions" tab: annual year-over-year instruction changes.
  - "Legislation" tab: newly enacted laws, with a Company/Firm audience
    toggle for the dual summaries.

Self-contained output: inline CSS/JS, data embedded as JSON, no external
requests. Never hand-edit report/index.html — edit this script and re-run.

Usage:  python3 scripts/generate_report.py
"""
import json
import pathlib

from jurisdictions import JURISDICTIONS, LEGIS_JURISDICTIONS

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHANGES_DIR = ROOT / "data" / "changes"
LEGIS_DIR = ROOT / "data" / "legislation"
OUT = ROOT / "report" / "index.html"

CATEGORY_LABELS = {
    "reporting-requirement": "Reporting requirement",
    "apportionment": "Apportionment",
    "state-modification": "State modification",
    "income-or-deduction": "Income / deduction",
    "rate-or-threshold": "Rate / threshold",
    "credit-or-incentive": "Credit / incentive",
    "nol-or-limitation": "NOL / limitation",
    "filing-method": "Filing method",
    "filing-procedure": "Filing procedure",
    "due-date": "Due date",
    "new-form-or-schedule": "New form / schedule",
    "conformity": "IRC conformity",
    "definition-change": "Definition change",
    "penalty": "Penalty",
    "other": "Other",
}


def _slim(j: dict) -> dict:
    return {k: j[k] for k in ("id", "name", "kind", "agency", "website")}


def load_data() -> dict:
    return {
        "jurisdictions": [_slim(j) for j in JURISDICTIONS],
        "legisJurisdictions": [_slim(j) for j in LEGIS_JURISDICTIONS],
        "reviews": {p.stem: json.loads(p.read_text())
                    for p in sorted(CHANGES_DIR.glob("*.json"))},
        "legis": {p.stem: json.loads(p.read_text())
                  for p in sorted(LEGIS_DIR.glob("*.json"))},
        "categoryLabels": CATEGORY_LABELS,
    }


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tax Form Changes Tracker</title>
<style>
:root {
  --bg: #f6f5f1;
  --panel: #ffffff;
  --ink: #1e2430;
  --muted: #6b7280;
  --line: #e3e1d9;
  --accent: #1f5f4e;
  --accent-ink: #ffffff;
  --chip: #eceae2;
  --chip-on: #1f5f4e;
  --high: #b4232a;
  --medium: #b26a00;
  --low: #4b5563;
  --unverified-bg: #fdf3d7;
  --unverified-ink: #7a5a00;
  --doc-bg: #fbfaf5;
  --doc-edge: #d9d4c3;
  --shadow: 0 10px 30px rgba(20, 25, 35, .14);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #14181f;
    --panel: #1c222c;
    --ink: #e8eaf0;
    --muted: #9aa3b2;
    --line: #2b3340;
    --accent: #4fae92;
    --accent-ink: #0d1218;
    --chip: #262d39;
    --chip-on: #4fae92;
    --high: #f0716f;
    --medium: #e0a63f;
    --low: #9aa3b2;
    --unverified-bg: #3a3115;
    --unverified-ink: #ecc85e;
    --doc-bg: #202733;
    --doc-edge: #39424f;
    --shadow: 0 10px 30px rgba(0, 0, 0, .5);
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.55 "Segoe UI", system-ui, -apple-system, sans-serif;
}
header {
  padding: 24px 28px 0; border-bottom: 1px solid var(--line);
  background: var(--panel);
}
header h1 { margin: 0 0 4px; font-size: 21px; letter-spacing: .2px; }
header .sub { color: var(--muted); font-size: 13.5px; }
.stats { display: flex; gap: 26px; margin-top: 14px; flex-wrap: wrap; }
.stat b { font-size: 20px; display: block; }
.stat span { color: var(--muted); font-size: 12.5px; }
.tabs { display: flex; gap: 4px; margin-top: 16px; }
.tab {
  border: 1px solid var(--line); border-bottom: none; background: var(--chip);
  color: var(--muted); font: inherit; font-size: 13.5px; font-weight: 600;
  padding: 9px 18px; border-radius: 9px 9px 0 0; cursor: pointer;
}
.tab.on { background: var(--bg); color: var(--ink); }
.layout { display: grid; grid-template-columns: 275px 1fr; min-height: calc(100vh - 150px); }
nav {
  border-right: 1px solid var(--line); background: var(--panel);
  padding: 14px 10px; overflow-y: auto; max-height: calc(100vh - 150px);
  position: sticky; top: 0;
}
nav h2 { font-size: 11px; text-transform: uppercase; letter-spacing: .12em; color: var(--muted); margin: 14px 8px 6px; }
nav button {
  display: flex; justify-content: space-between; align-items: center; gap: 8px;
  width: 100%; text-align: left; border: 0; background: none; color: var(--ink);
  padding: 6px 9px; border-radius: 7px; cursor: pointer; font: inherit; font-size: 13.5px;
}
nav button:hover { background: var(--chip); }
nav button.on { background: var(--accent); color: var(--accent-ink); }
nav button .n {
  font-size: 11.5px; background: var(--chip); color: var(--muted);
  border-radius: 999px; padding: 0 8px; min-width: 22px; text-align: center;
}
nav button.on .n { background: rgba(255,255,255,.25); color: inherit; }
nav button .n.zero { opacity: .45; }
main { padding: 20px 26px 60px; max-width: 1060px; }
.filters {
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
  padding: 12px 0 16px; position: sticky; top: 0; background: var(--bg); z-index: 5;
}
.filters input[type=search] {
  flex: 1 1 220px; padding: 8px 12px; border: 1px solid var(--line);
  border-radius: 8px; background: var(--panel); color: var(--ink); font: inherit;
}
.chip {
  border: 1px solid var(--line); background: var(--chip); color: var(--ink);
  border-radius: 999px; padding: 4px 12px; font-size: 12.5px; cursor: pointer;
}
.chip.on { background: var(--chip-on); border-color: var(--chip-on); color: var(--accent-ink); }
.aud {
  display: inline-flex; border: 1px solid var(--line); border-radius: 999px;
  overflow: hidden; margin-left: auto;
}
.aud button {
  border: 0; background: var(--panel); color: var(--muted); font: inherit;
  font-size: 12.5px; font-weight: 600; padding: 5px 14px; cursor: pointer;
}
.aud button.on { background: var(--accent); color: var(--accent-ink); }
.jur-block { margin: 26px 0 8px; }
.jur-block h3 { margin: 0 0 2px; font-size: 16.5px; }
.jur-block .meta { color: var(--muted); font-size: 12.5px; margin-bottom: 10px; }
.jur-block .gap {
  background: var(--unverified-bg); color: var(--unverified-ink);
  border-radius: 8px; padding: 8px 12px; font-size: 12.5px; margin: 8px 0;
}
.card {
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 14px 16px; margin: 10px 0; cursor: pointer; transition: box-shadow .15s, transform .15s;
}
.card:hover { box-shadow: var(--shadow); transform: translateY(-1px); }
.card h4 { margin: 0 0 6px; font-size: 15px; }
.card p { margin: 6px 0 8px; color: var(--ink); font-size: 13.8px; }
.badges { display: flex; flex-wrap: wrap; gap: 6px; }
.badge {
  font-size: 11px; letter-spacing: .03em; border-radius: 5px; padding: 2px 8px;
  background: var(--chip); color: var(--muted);
}
.badge.cat { background: var(--chip); color: var(--ink); }
.badge.high { color: var(--high); border: 1px solid currentColor; background: transparent; }
.badge.medium { color: var(--medium); border: 1px solid currentColor; background: transparent; }
.badge.low { color: var(--low); border: 1px solid currentColor; background: transparent; }
.badge.unverified { background: var(--unverified-bg); color: var(--unverified-ink); font-weight: 600; }
.badge.stage { border: 1px dashed var(--muted); background: transparent; }
.card .hint { color: var(--muted); font-size: 12px; margin-top: 8px; }
.aud-label { font-size: 11px; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); margin-top: 8px; }
.empty { color: var(--muted); padding: 30px 4px; }
.overlay {
  position: fixed; inset: 0; background: rgba(10, 14, 20, .55);
  display: none; align-items: flex-start; justify-content: center;
  padding: 4vh 16px; z-index: 50; overflow-y: auto;
}
.overlay.open { display: flex; }
.modal {
  background: var(--panel); border-radius: 14px; max-width: 860px; width: 100%;
  box-shadow: var(--shadow); padding: 24px 28px 26px; position: relative;
}
.modal .close {
  position: absolute; top: 14px; right: 14px; border: 0; background: var(--chip);
  color: var(--ink); width: 30px; height: 30px; border-radius: 999px;
  font-size: 15px; cursor: pointer;
}
.modal h3 { margin: 0 34px 8px 0; font-size: 18px; }
.modal .summary { font-size: 14.5px; margin: 8px 0 12px; }
.modal .kv { font-size: 13px; color: var(--muted); margin: 3px 0; }
.modal .kv b { color: var(--ink); font-weight: 600; }
.doc {
  background: var(--doc-bg); border: 1px solid var(--doc-edge);
  border-left: 4px solid var(--accent); border-radius: 8px;
  padding: 14px 18px; margin: 10px 0 4px;
  font-family: Georgia, "Times New Roman", serif; font-size: 14.5px; line-height: 1.65;
  white-space: pre-wrap;
}
.doc-label {
  font-size: 11px; text-transform: uppercase; letter-spacing: .12em;
  color: var(--muted); margin-top: 16px;
}
.doc.prior { border-left-color: var(--muted); opacity: .92; }
.cite { font-size: 12.5px; color: var(--muted); margin-top: 14px; }
.cite a { color: var(--accent); }
.modal .warn {
  background: var(--unverified-bg); color: var(--unverified-ink);
  border-radius: 8px; padding: 8px 12px; font-size: 12.5px; margin-top: 14px;
}
footer { padding: 22px 28px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }
@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  nav { position: static; max-height: none; border-right: 0; border-bottom: 1px solid var(--line); }
  .aud { margin-left: 0; }
}
</style>
</head>
<body>
<header>
  <h1>Tax Form Changes Tracker</h1>
  <div class="sub" id="subtitle"></div>
  <div class="stats" id="stats"></div>
  <div class="tabs">
    <button class="tab on" data-tab="forms">Form instructions</button>
    <button class="tab" data-tab="legis">Legislation</button>
  </div>
</header>
<div class="layout">
  <nav id="nav"></nav>
  <main>
    <div class="filters">
      <input type="search" id="q" placeholder="Search…">
      <span id="catChips"></span>
      <span id="impChips"></span>
      <button class="chip" id="verifiedOnly">verified only</button>
      <span class="aud" id="audToggle" hidden>
        <button data-aud="company" class="on">Company view</button>
        <button data-aud="firm">Firm view</button>
      </span>
    </div>
    <div id="content"></div>
  </main>
</div>
<footer>Generated by scripts/generate_report.py. AI-generated summaries — verify against the cited source documents before relying on any entry. Entries marked UNVERIFIED have not been confirmed against a retrieved source.</footer>

<div class="overlay" id="overlay">
  <div class="modal" id="modal" role="dialog" aria-modal="true"></div>
</div>

<script type="application/json" id="data">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const CAT = DATA.categoryLabels;
const state = { tab: 'forms', jur: null, q: '', cats: new Set(), imps: new Set(),
                verifiedOnly: false, aud: 'company' };

const allChanges = [];
for (const [jid, rev] of Object.entries(DATA.reviews))
  for (const c of rev.changes) allChanges.push({ ...c, _jid: jid, _rev: rev });
const allLaws = [];
for (const [jid, rev] of Object.entries(DATA.legis))
  for (const c of rev.laws) allLaws.push({ ...c, _jid: jid, _rev: rev });

const jurById = Object.fromEntries(
  DATA.jurisdictions.concat(DATA.legisJurisdictions).map(j => [j.id, j]));

function items() { return state.tab === 'forms' ? allChanges : allLaws; }
function jurs()  { return state.tab === 'forms' ? DATA.jurisdictions : DATA.legisJurisdictions; }
function files() { return state.tab === 'forms' ? DATA.reviews : DATA.legis; }
function summaryOf(c) {
  if (state.tab === 'forms') return c.summary;
  return state.aud === 'company' ? c.summary_for_company : c.summary_for_firm;
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function matches(c) {
  if (state.jur && c._jid !== state.jur) return false;
  if (state.cats.size && !state.cats.has(c.category)) return false;
  if (state.imps.size && !state.imps.has(c.impact)) return false;
  if (state.verifiedOnly && c.status !== 'verified') return false;
  if (state.q) {
    const hay = [c.title, c.summary, c.summary_for_company, c.summary_for_firm,
                 c.form, c.bill, c.law_citation, c.who_is_affected,
                 (c.affected_returns || []).join(' '),
                 c.excerpt?.current, c.excerpt?.passage,
                 CAT[c.category], jurById[c._jid]?.name].join(' ').toLowerCase();
    if (!hay.includes(state.q)) return false;
  }
  return true;
}

function renderHeader() {
  document.getElementById('subtitle').textContent = state.tab === 'forms'
    ? 'Year-over-year changes in corporate tax form instructions — the federal corporate suite (1120, 1120-PC, 5471, 5472, 8865, 8858, 1118, 3800, 8990–8993) and all state jurisdictions. Click any change to preview the passage from the actual instructions.'
    : 'Newly enacted legislation with corporate income tax return impact, tracked throughout the year. Toggle Company/Firm view for audience-specific summaries; click any law to preview the operative bill language.';
  const reviewed = Object.keys(files()).length;
  const total = items().length;
  const high = items().filter(c => c.impact === 'high').length;
  const pending = jurs().length - reviewed;
  const nouns = state.tab === 'forms'
    ? ['jurisdictions reviewed', 'awaiting review', 'changes tracked', 'high impact']
    : ['jurisdictions monitored', 'not yet monitored', 'laws tracked', 'high impact'];
  document.getElementById('stats').innerHTML = `
    <div class="stat"><b>${reviewed}</b><span>${nouns[0]}</span></div>
    <div class="stat"><b>${pending}</b><span>${nouns[1]}</span></div>
    <div class="stat"><b>${total}</b><span>${nouns[2]}</span></div>
    <div class="stat"><b>${high}</b><span>${nouns[3]}</span></div>`;
}

function renderNav() {
  const counts = {};
  for (const c of items()) counts[c._jid] = (counts[c._jid] || 0) + 1;
  const groups = [['Federal', 'federal'], ['States', 'state'], ['Local', 'local']];
  let html = `<button class="${state.jur === null ? 'on' : ''}" data-jur="">All jurisdictions <span class="n">${items().length}</span></button>`;
  for (const [label, kind] of groups) {
    const js = jurs().filter(j => j.kind === kind);
    if (!js.length) continue;
    html += `<h2>${label}</h2>`;
    for (const j of js) {
      const n = counts[j.id] || 0;
      const reviewed = j.id in files();
      html += `<button class="${state.jur === j.id ? 'on' : ''}" data-jur="${j.id}">
        ${esc(j.name.replace(' — Legislation', ''))} <span class="n ${n ? '' : 'zero'}">${reviewed ? n : '—'}</span></button>`;
    }
  }
  const nav = document.getElementById('nav');
  nav.innerHTML = html;
  nav.querySelectorAll('button').forEach(b => b.onclick = () => {
    state.jur = b.dataset.jur || null;
    render();
  });
}

function badge(c) {
  return `<span class="badge cat">${esc(CAT[c.category] || c.category)}</span>
    <span class="badge ${c.impact}">${c.impact} impact</span>
    ${c.stage === 'pending-signature' ? '<span class="badge stage">pending signature</span>' : ''}
    ${c.status === 'unverified' ? '<span class="badge unverified">UNVERIFIED</span>' : ''}`;
}

function cardMeta(c) {
  if (state.tab === 'forms') return `<span class="badge">${esc(c.form)}</span>`;
  return `<span class="badge">${esc(c.bill)}</span>
    <span class="badge">enacted ${esc(c.enacted_date)}</span>
    ${c.first_return_year_affected ? `<span class="badge">first return: TY${c.first_return_year_affected}</span>` : ''}`;
}

function renderContent() {
  const el = document.getElementById('content');
  const byJur = new Map();
  for (const c of items().filter(matches)) {
    if (!byJur.has(c._jid)) byJur.set(c._jid, []);
    byJur.get(c._jid).push(c);
  }
  if (!byJur.size) {
    el.innerHTML = '<div class="empty">Nothing matches the current filters.' +
      (state.jur && !(state.jur in files())
        ? (state.tab === 'forms'
           ? ' This jurisdiction has not been reviewed yet — run its agent to populate it.'
           : ' This jurisdiction is not being monitored yet — run its legis- agent to start.') : '') + '</div>';
    return;
  }
  let html = '';
  for (const [jid, list] of byJur) {
    const j = jurById[jid], rev = files()[jid];
    const meta = state.tab === 'forms'
      ? `TY${rev.tax_year} vs TY${rev.compared_to_year} · reviewed ${esc(rev.reviewed_date)}`
      : `window ${esc(rev.window_start)} → ${esc(rev.window_end)} · reviewed ${esc(rev.reviewed_date)}`;
    html += `<section class="jur-block"><h3>${esc((j?.name || jid).replace(' — Legislation', ''))}</h3>
      <div class="meta">${esc(j?.agency || '')} · ${meta}</div>`;
    for (const g of (rev.coverage?.gaps || [])) html += `<div class="gap">⚠ ${esc(g)}</div>`;
    for (const c of list) {
      const audLabel = state.tab === 'legis'
        ? `<div class="aud-label">${state.aud === 'company' ? 'For your tax department' : 'For your client base'}</div>` : '';
      html += `<article class="card" data-key="${jid}::${esc(c.id)}" tabindex="0" role="button">
        <h4>${esc(c.title)}</h4>
        <div class="badges">${badge(c)} ${cardMeta(c)}</div>
        ${audLabel}
        <p>${esc(summaryOf(c))}</p>
        <div class="hint">Click to preview the ${state.tab === 'forms' ? 'passage from the instructions' : 'operative bill language'} ↗</div>
      </article>`;
    }
    html += '</section>';
  }
  el.innerHTML = html;
  el.querySelectorAll('.card').forEach(card => {
    const open = () => openModal(card.dataset.key);
    card.onclick = open;
    card.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } };
  });
}

function openModal(key) {
  const [jid, cid] = key.split('::');
  const c = items().find(x => x._jid === jid && x.id === cid);
  if (!c) return;
  const j = jurById[jid], rev = files()[jid], src = c.source || {};
  const cite = [src.document, src.section && `§ ${src.section}`, src.page && `p. ${src.page}`]
    .filter(Boolean).map(esc).join(' · ');
  let body;
  if (state.tab === 'forms') {
    body = `
      <p class="summary">${esc(c.summary)}</p>
      ${c.who_is_affected ? `<div class="kv"><b>Who is affected:</b> ${esc(c.who_is_affected)}</div>` : ''}
      ${c.effective ? `<div class="kv"><b>Effective:</b> ${esc(c.effective)}</div>` : ''}
      <div class="doc-label">From the ${rev.tax_year} instructions${src.section ? ` — ${esc(src.section)}` : ''}</div>
      <div class="doc">${esc(c.excerpt?.current || '')}</div>
      ${c.excerpt?.prior ? `<div class="doc-label">Prior year (${rev.compared_to_year}) text</div>
        <div class="doc prior">${esc(c.excerpt.prior)}</div>`
        : `<div class="kv" style="margin-top:10px"><b>Prior year:</b> no counterpart passage — this text is new.</div>`}`;
  } else {
    body = `
      <div class="kv"><b>Bill:</b> ${esc(c.bill)}${c.law_citation ? ` · ${esc(c.law_citation)}` : ''}</div>
      <div class="kv"><b>Enacted:</b> ${esc(c.enacted_date)}${c.effective ? ` · <b>Effective:</b> ${esc(c.effective)}` : ''}</div>
      <div class="kv"><b>Returns affected:</b> ${esc((c.affected_returns || []).join(', '))}</div>
      <div class="doc-label">For an in-house tax department</div>
      <p class="summary">${esc(c.summary_for_company)}</p>
      <div class="doc-label">For an accounting firm</div>
      <p class="summary">${esc(c.summary_for_firm)}</p>
      <div class="doc-label">Operative language${src.section ? ` — ${esc(src.section)}` : ''}</div>
      <div class="doc">${esc(c.excerpt?.passage || '')}</div>
      ${c.excerpt?.amended_from ? `<div class="doc-label">Law before amendment</div>
        <div class="doc prior">${esc(c.excerpt.amended_from)}</div>` : ''}`;
  }
  document.getElementById('modal').innerHTML = `
    <button class="close" aria-label="Close">✕</button>
    <h3>${esc(c.title)}</h3>
    <div class="badges">${badge(c)} <span class="badge">${esc((j?.name || jid).replace(' — Legislation', ''))}</span> ${cardMeta(c)}</div>
    ${body}
    <div class="cite">Source: ${cite || esc(src.url || '')}${src.url ? ` — <a href="${esc(src.url)}" target="_blank" rel="noopener">open source document</a>` : ''}${src.prior_url ? ` · <a href="${esc(src.prior_url)}" target="_blank" rel="noopener">prior-year document</a>` : ''}</div>
    ${c.status === 'unverified' ? '<div class="warn">UNVERIFIED — this entry was drafted without confirming the passage against a retrieved copy of the source. Verify before relying on it.</div>' : ''}`;
  const ov = document.getElementById('overlay');
  ov.classList.add('open');
  document.querySelector('#modal .close').onclick = closeModal;
}
function closeModal() { document.getElementById('overlay').classList.remove('open'); }
document.getElementById('overlay').addEventListener('click', e => { if (e.target.id === 'overlay') closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

function renderFilters() {
  const cats = [...new Set(items().map(c => c.category))].sort();
  document.getElementById('catChips').innerHTML = cats.map(c =>
    `<button class="chip ${state.cats.has(c) ? 'on' : ''}" data-cat="${c}">${esc(CAT[c] || c)}</button>`).join(' ');
  document.getElementById('impChips').innerHTML = ['high', 'medium', 'low'].map(i =>
    `<button class="chip ${state.imps.has(i) ? 'on' : ''}" data-imp="${i}">${i}</button>`).join(' ');
  document.querySelectorAll('[data-cat]').forEach(b => b.onclick = () => {
    state.cats.has(b.dataset.cat) ? state.cats.delete(b.dataset.cat) : state.cats.add(b.dataset.cat);
    render();
  });
  document.querySelectorAll('[data-imp]').forEach(b => b.onclick = () => {
    state.imps.has(b.dataset.imp) ? state.imps.delete(b.dataset.imp) : state.imps.add(b.dataset.imp);
    render();
  });
  const v = document.getElementById('verifiedOnly');
  v.classList.toggle('on', state.verifiedOnly);
  v.onclick = () => { state.verifiedOnly = !state.verifiedOnly; render(); };
  document.getElementById('audToggle').hidden = state.tab !== 'legis';
}

document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  if (state.tab === t.dataset.tab) return;
  state.tab = t.dataset.tab;
  state.jur = null; state.cats.clear(); state.imps.clear();
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('on', x === t));
  render();
});
document.querySelectorAll('#audToggle button').forEach(b => b.onclick = () => {
  state.aud = b.dataset.aud;
  document.querySelectorAll('#audToggle button').forEach(x => x.classList.toggle('on', x === b));
  renderContent();
});
document.getElementById('q').addEventListener('input', e => {
  state.q = e.target.value.trim().toLowerCase();
  renderContent();
});

function render() { renderHeader(); renderNav(); renderFilters(); renderContent(); }
render();
</script>
</body>
</html>
"""


def main() -> None:
    data = load_data()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    n_changes = sum(len(r["changes"]) for r in data["reviews"].values())
    n_laws = sum(len(r["laws"]) for r in data["legis"].values())
    print(f"wrote {OUT} — {len(data['reviews'])} form reviews ({n_changes} changes), "
          f"{len(data['legis'])} legislation files ({n_laws} laws)")


if __name__ == "__main__":
    main()
