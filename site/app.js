(() => {
"use strict";
const C = JSON.parse(document.getElementById("course").textContent);
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const pad = (n) => String(n).padStart(2, "0");
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const today = () => ymd(new Date());
const addDays = (s, n) => { const d = new Date(s + "T12:00:00"); d.setDate(d.getDate() + n); return ymd(d); };
const daysBetween = (a, b) => Math.round((new Date(b + "T12:00:00") - new Date(a + "T12:00:00")) / 864e5);
const fmt = (s, o = { weekday: "short", month: "short", day: "numeric" }) => new Date(s + "T12:00:00").toLocaleDateString("en-US", o);
const nowIso = () => new Date().toISOString();
const L = (id) => C.lessons[id];
const ready = (id) => L(id) && !L(id).pending;
const partOf = (n) => C.parts.find((p) => p.part === n);
const main = $("#main");

/* ---------------- storage ---------------- */
const ls = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage blocked */ } },
};
const KEY = "dfz-progress-v1";
function norm(r) {
  r = r || {};
  return { log: { ...(r.log || {}) }, scores: { ...(r.scores || {}) }, quiz: { ...(r.quiz || {}) }, tasks: { ...(r.tasks || {}) },
    cards: { ...(r.cards || {}) }, days: { ...(r.days || {}) }, start: r.start || null, startU: r.startU || "" };
}
function merge(a, raw) {
  const b = norm(raw), o = norm(a);
  for (const f of ["log", "tasks", "cards"]) for (const [k, e] of Object.entries(b[f])) if (!o[f][k] || (e.u || "") > (o[f][k].u || "")) o[f][k] = e;
  for (const f of ["scores", "quiz", "days"]) for (const [k, v] of Object.entries(b[f])) o[f][k] = Math.max(o[f][k] || 0, v);
  if (b.startU > o.startU) { o.start = b.start; o.startU = b.startU; }
  return o;
}
const sig = (x) => JSON.stringify(norm(x));
let P = norm(ls.get(KEY, {}));
let ref = null, sync = "local", writing = false, again = false, wTimer = null;
async function write() {
  if (!ref) return;
  if (writing) { again = true; return; }
  writing = true;
  try { await ref.set({ ...P, updatedAt: nowIso() }); sync = "cloud"; } catch { sync = "local"; }
  writing = false; sideFoot();
  if (again) { again = false; write(); }
}
function commit() { ls.set(KEY, P); if (ref) { clearTimeout(wTimer); wTimer = setTimeout(write, 600); } chrome(); }
function activity() { const t = today(); P.days[t] = (P.days[t] || 0) + 1; }

const cap = (name) => { try { return window.claude && window.claude.use ? Promise.resolve(window.claude.use(name)).catch(() => null) : Promise.resolve(null); } catch { return Promise.resolve(null); } };
let sample = null;
(async () => {
  const [db, user] = await Promise.all([cap("db"), cap("user")]);
  if (!db || !user) return;
  let uid = null;
  try { uid = await user.id(); } catch { uid = null; }
  if (!uid) return;
  try { ref = db.collection("data/users/" + uid).doc("progress"); } catch { ref = null; return; }
  ref.onSnapshot((snap) => {
    sync = "cloud";
    const d = snap.exists ? snap.data() : null;
    if (!d) { write(); return; }
    const m = merge(P, d), changed = sig(m) !== sig(P);
    P = m; ls.set(KEY, P);
    if (sig(m) !== sig(d)) { clearTimeout(wTimer); wTimer = setTimeout(write, 600); }
    if (changed) { chrome(); if (["home", "plan", "review-idle"].includes(viewKind())) render(false); }
    sideFoot();
  }, () => { sync = "local"; sideFoot(); });
})();
cap("sample").then((s) => { sample = s || null; if (sample) mountAi(); });

/* ---------------- progress ---------------- */
const isDone = (id) => !!(P.log[id] && P.log[id].done);
const doneCount = () => C.order.filter(isDone).length;
const nextUp = () => C.order.find((id) => !isDone(id) && ready(id)) || C.order.find((id) => !isDone(id)) || null;
function setDone(id, done) {
  const prev = P.log[id];
  P.log[id] = { done, at: done ? (prev && prev.done ? prev.at : nowIso()) : (prev ? prev.at : nowIso()), u: nowIso() };
  if (done) { activity(); if (!P.start) { P.start = today(); P.startU = nowIso(); } }
  commit();
  if (done) {
    const n = cardsFor(id).length;
    toast(`Day ${pad(L(id).day)} passed.${n ? ` ${n} cards added to your review deck.` : ""}`);
  }
}
function streak() {
  let d = today(), n = 0;
  if (!P.days[d]) d = addDays(d, -1);
  while (P.days[d]) { n++; d = addDays(d, -1); }
  return n;
}
function startDate() { return P.start || today(); }
function projection() {
  const t = today();
  const remaining = C.order.filter((id) => !isDone(id));
  const doneToday = C.order.some((id) => isDone(id) && P.log[id].at && ymd(new Date(P.log[id].at)) === t);
  const from = doneToday ? addDays(t, 1) : t;
  const finish = remaining.length ? addDays(from, remaining.length - 1) : t;
  const planned = addDays(startDate(), C.order.length - 1);
  return { finish, planned, slip: daysBetween(planned, finish), remaining: remaining.length };
}

/* ---------------- spaced repetition ---------------- */
const IV = [0, 1, 3, 7, 14, 30, 60];
const NEW_PER_SESSION = 20;
function allCards() {
  const out = [];
  for (const id of C.order) if (ready(id)) for (const t of L(id).terms) out.push({ id: t.id, front: esc(t.term), back: t.plain, src: id, unlocked: isDone(id) });
  for (const p of C.parts) if (p.ready) { const all = p.lessons.every(isDone); for (const f of p.flashcards) out.push({ id: f.id, front: f.front, back: f.back, src: "p" + p.part, unlocked: all }); }
  return out;
}
const cardsFor = (lid) => allCards().filter((c) => (c.src === lid || (c.src === "p" + L(lid).part && partOf(L(lid).part).lessons.every(isDone))) && !P.cards[c.id]);
function dueCards() {
  const t = today(), cards = allCards().filter((c) => c.unlocked);
  const due = cards.filter((c) => P.cards[c.id] && P.cards[c.id].due <= t).sort((a, b) => P.cards[a.id].due.localeCompare(P.cards[b.id].due));
  const fresh = cards.filter((c) => !P.cards[c.id]);
  return { due, fresh, total: cards.length };
}
const dueCount = () => { const d = dueCards(); return d.due.length + Math.min(d.fresh.length, NEW_PER_SESSION); };
function rateCard(id, r) {
  const cur = P.cards[id] || { box: 0, n: 0 };
  let box = cur.box, gap;
  if (r === 0) { box = 1; gap = 0; }
  else if (r === 1) { box = Math.max(1, box); gap = Math.max(1, Math.round(IV[box] / 2)); }
  else if (r === 2) { box = Math.min(6, box + 1); gap = IV[box]; }
  else { box = Math.min(6, box + 2); gap = IV[box]; }
  P.cards[id] = { box, due: addDays(today(), gap), n: (cur.n || 0) + 1, u: nowIso() };
  activity(); commit();
}
function preview(id) {
  const box = (P.cards[id] || { box: 0 }).box;
  const lab = (n) => (n === 0 ? "now" : n === 1 ? "1 day" : `${n} days`);
  return [lab(0), lab(Math.max(1, Math.round(IV[Math.max(1, box)] / 2))), lab(IV[Math.min(6, box + 1)]), lab(IV[Math.min(6, box + 2)])];
}

/* ---------------- small UI parts ---------------- */
const GLYPH = {
  passed: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7.2" fill="currentColor"/><path d="M4.8 8.2l2.1 2.1 4.3-4.6" fill="none" stroke="var(--panel)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  running: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-opacity=".3" stroke-width="2"/><path class="spin" d="M8 1.6a6.4 6.4 0 0 1 6.4 6.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="8" cy="8" r="2.4" fill="currentColor"/></svg>',
  queued: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-dasharray="2.6 2.4"/></svg>',
};
const stateOf = (id) => (isDone(id) ? "passed" : id === nextUp() ? "running" : "queued");
const stLabel = { passed: "passed", running: "up next", queued: "queued" };
const glyph = (id) => { const s = stateOf(id); return `<span class="st ${s}" title="${stLabel[s]}" aria-label="${stLabel[s]}">${GLYPH[s]}</span>`; };
const host = (u) => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return ""; } };
const toastEl = $("#toast");
let toastT = null;
function toast(t) { toastEl.textContent = t; toastEl.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => (toastEl.hidden = true), 3200); }
const ICON = {
  arrow: '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  check: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  bulb: '<svg viewBox="0 0 20 20" width="17" height="17" aria-hidden="true"><path d="M10 2.5a5.5 5.5 0 0 0-3.2 10V15h6.4v-2.5A5.5 5.5 0 0 0 10 2.5zM7.8 17.5h4.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  team: '<svg viewBox="0 0 20 20" width="17" height="17" aria-hidden="true"><circle cx="7" cy="7" r="2.6" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="14" cy="8" r="2.1" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M2.5 16.5c.6-2.8 2.4-4.2 4.5-4.2s3.9 1.4 4.5 4.2M12 12.6c2.3-.4 4.5.8 5.3 3.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
  chev: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  play: '<svg viewBox="0 0 12 12" width="9" height="9" aria-hidden="true"><path d="M3 2l7 4-7 4z" fill="currentColor"/></svg>',
  warn: '<svg viewBox="0 0 20 20" width="17" height="17" aria-hidden="true"><path d="M10 2.8l7.8 13.7H2.2z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M10 8v3.8M10 14.2v.3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
};

/* ---------------- chrome: sidebar, badges, theme ---------------- */
const side = $("#side"), scrim = $("#scrim"), menuBtn = $("#menuBtn");
const sideOpen = {};
function route() { return (location.hash || "").slice(1) || "home"; }
function viewKind() { const r = route(); if (r === "review") return review.active ? "review-live" : "review-idle"; return /^d\d\d$/.test(r) ? "lesson" : r; }
function sideHTML() {
  const r = route(), nx = nextUp(), dc = dueCount();
  const link = (h, t, extra = "") => `<a class="navlink${r === h ? " on" : ""}" href="#${h}">${t}${extra}</a>`;
  let s = `<div>${link("home", "Today")}${nx ? `<a class="navlink" href="#${nx}">Up next: Day ${pad(L(nx).day)}</a>` : ""}${link("review", "Review", dc ? ` <span class="due">${dc}</span>` : "")}${link("plan", "Plan and pace")}${link("commands", "Command cheat sheet")}${link("glossary", "Glossary")}${link("library", "Library: links and videos")}${link("labs", "Lab files")}</div>`;
  const curPart = L(r) ? L(r).part : /^p\d+$/.test(r) ? +r.slice(1) : nx ? L(nx).part : 0;
  for (const p of C.parts) {
    const n = p.lessons.filter(isDone).length, open = sideOpen[p.part] ?? p.part === curPart;
    s += `<div class="grp"><div class="grp-h"><button class="grp-tg" data-act="sidetog" data-p="${p.part}" aria-expanded="${open}" aria-label="${open ? "Collapse" : "Expand"} part ${p.part}">${ICON.chev}</button><a class="grp-a" href="#p${p.part}"><span class="grp-n">${p.part}</span><span class="grp-t">${esc(p.title)}</span></a><span class="grp-c tnum">${n}/${p.lessons.length}</span></div>`;
    if (open) for (const id of p.lessons) s += `<a class="ls${r === id ? " on" : ""}" href="#${id}">${glyph(id)}<span class="d">${pad(L(id).day)}</span><span>${esc(L(id).title)}</span></a>`;
    s += "</div>";
  }
  return s + `<p class="foot" id="sideFoot"></p>`;
}
function sideFoot() {
  const f = $("#sideFoot");
  if (f) f.textContent = sync === "cloud" ? "Progress syncs to your account, so your phone and laptop match." : "Progress is saved in this browser.";
}
function chrome() {
  const keep = side.scrollTop;
  side.innerHTML = sideHTML(); side.scrollTop = keep; sideFoot();
  const dc = dueCount(), b = $("#dueBadge");
  b.hidden = !dc; b.textContent = dc;
  const r = route();
  $$(".topnav a").forEach((a) => a.classList.toggle("on", a.dataset.nav === r || (r === "home" && a.dataset.nav === "home")));
}
function openSide(open) { side.classList.toggle("open", open); scrim.hidden = !open; menuBtn.setAttribute("aria-expanded", String(open)); }
menuBtn.addEventListener("click", () => openSide(!side.classList.contains("open")));
scrim.addEventListener("click", () => openSide(false));
side.addEventListener("click", (e) => { if (e.target.closest("a")) openSide(false); });

const themeBtn = $("#themeBtn");
const THEMES = ["system", "light", "dark"];
const TICON = {
  system: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor"/></svg>',
  light: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
  dark: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
};
function theme() { try { return localStorage.getItem("dfz-theme") || "system"; } catch { return "system"; } }
function applyTheme(t) {
  if (t === "system") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", t);
  themeBtn.innerHTML = TICON[t]; themeBtn.title = `Theme: ${t}`; themeBtn.setAttribute("aria-label", `Theme: ${t}`);
}
themeBtn.addEventListener("click", () => { const t = THEMES[(THEMES.indexOf(theme()) + 1) % 3]; try { localStorage.setItem("dfz-theme", t); } catch { /* blocked */ } applyTheme(t); });
applyTheme(theme());

/* ---------------- questions ---------------- */
const QS = {};  // quiz state by key: { ans: [], shown: bool }
function qHTML(key, q, i, st, single) {
  const picked = st.ans[i], reveal = single ? picked != null : st.shown;
  const opts = q.options.map((o, j) => {
    let cls = "opt";
    if (reveal) { if (j === q.answer) cls += " right"; else if (j === picked) cls += " wrong"; } else if (j === picked) cls += " sel";
    return `<button class="${cls}" data-act="pick" data-key="${key}" data-i="${i}" data-j="${j}" aria-pressed="${j === picked}"${reveal ? " disabled" : ""}><span class="key">${"ABCD"[j]}</span><span>${o}</span></button>`;
  }).join("");
  const why = reveal ? `<div class="why"><b>${picked === q.answer ? "Right." : "Not quite."}</b> ${q.why}</div>` : "";
  return `<div class="q"><div class="q-t">${single ? "" : `${i + 1}. `}${q.q}${q.from ? `<span class="from">${esc(q.from)}</span>` : ""}</div><div class="opts">${opts}</div>${why}</div>`;
}
const QUIZ = {};  // key -> { qs, need, onDone, label }
function quizBlock(key) {
  const z = QUIZ[key], st = QS[key] || (QS[key] = { ans: z.qs.map(() => null), shown: false });
  const score = z.qs.reduce((a, q, i) => a + (st.ans[i] === q.answer ? 1 : 0), 0);
  const all = st.ans.every((a) => a != null);
  let foot;
  if (!st.shown) foot = `<div><button class="btn" data-act="grade" data-key="${key}"${all ? "" : " disabled"}>Check my answers</button></div>`;
  else foot = `<div class="row"><span class="score tnum">${score}/${z.qs.length}</span><span class="muted">${z.result(score)}</span><button class="btn ghost sm" data-act="retry" data-key="${key}">Try again</button></div>`;
  return `<div class="quiz" id="quiz-${key}">${z.qs.map((q, i) => qHTML(key, q, i, st, false)).join("")}${foot}</div>`;
}
function refreshQuiz(key) { const el = document.getElementById("quiz-" + key); if (el) el.outerHTML = quizBlock(key); }

/* ---------------- code blocks ---------------- */
let codeN = 0;
function codeBox(c) {
  const id = "cb" + (++codeN);
  return `<div class="code"><div class="code-bar"><span class="fn">${esc(c.title || c.lang)}</span><span class="lg">${esc(c.lang)}</span><button class="copy" data-act="copy" data-target="${id}">Copy</button></div><pre id="${id}"><code>${c.html}</code></pre>${c.run ? `<div class="run"><b>run</b>&nbsp; ${esc(c.run)}</div>` : ""}</div>`;
}
function cmdRows(cmds) {
  return `<div class="cmds">${cmds.map((c) => `<div class="cmd"><pre><code>${c.html}</code></pre><span>${c.what}</span></div>`).join("")}</div>`;
}

/* ---------------- views ---------------- */
function viewHome() {
  const nx = nextUp(), dc = dueCards(), nDue = dc.due.length + Math.min(dc.fresh.length, NEW_PER_SESSION);
  const pr = projection(), dn = doneCount(), tot = C.order.length;
  const learned = Object.values(P.cards).filter((c) => c.box >= 2).length;
  const nl = nx ? L(nx) : null;
  const rows = [];
  if (nDue) rows.push(`<div class="term-row"><span class="k">review</span><span class="v"><a href="#review">${nDue} card${nDue === 1 ? "" : "s"} due</a></span><span class="m">~${Math.max(2, Math.round(nDue / 3))} min</span></div>`);
  if (nl) rows.push(`<div class="term-row"><span class="k">lesson</span><span class="v"><a href="#${nl.id}">Day ${pad(nl.day)} · ${esc(nl.title)}</a></span><span class="m">${nl.minutes} min</span></div>`);
  else rows.push(`<div class="term-row"><span class="k">done</span><span class="v">All ${tot} lessons passed. Keep reviewing, and build the capstone.</span><span class="m"></span></div>`);
  rows.push(`<div class="term-row"><span class="k">check</span><span class="v">3 questions at the end. 2 right marks the day passed.</span><span class="m">3 min</span></div>`);
  const term = `<section class="term" aria-label="Today's session"><div class="term-bar"><i></i><i></i><i></i><span>~/code/hello-devops</span></div><div class="term-body">
    <div class="pr"><b>$</b> devops today${dn === 0 ? " --first-run" : ""}</div>${rows.join("")}
    <div class="term-actions">${nl ? `<a class="btn" href="#${nl.id}">${dn === 0 ? "Start Day 01" : `Open Day ${pad(nl.day)}`} ${ICON.arrow}</a>` : ""}${nDue ? `<a class="btn ghost" href="#review">Review first</a>` : ""}</div></div></section>`;

  let pipe = "";
  C.parts.forEach((p, i) => {
    const n = p.lessons.filter(isDone).length;
    const s = n === p.lessons.length ? "passed" : p.lessons.includes(nx) ? "running" : "queued";
    pipe += `<div class="job"><a class="job-h" href="#p${p.part}"><span class="st ${s}">${GLYPH[s]}</span><span class="jt">${esc(p.tool)}</span><span class="jc tnum">${n}/${p.lessons.length}</span></a><ol>${p.lessons.map((id) => `<li><a href="#${id}" class="${id === nx ? "cur" : ""}">${glyph(id)}<span class="tt">${pad(L(id).day)} ${esc(L(id).title)}</span></a></li>`).join("")}</ol></div>`;
  });

  const partsList = C.parts.map((p) => {
    const n = p.lessons.filter(isDone).length;
    const days = p.lessons.map((id) => L(id).day);
    return `<a class="prow prow-art" href="#p${p.part}"><span class="pthumb" aria-hidden="true">${p.art || ""}</span><span class="pn">${p.part}</span><span><span class="pt">${esc(p.title)}</span><span class="pd">${days.length > 1 ? `Days ${days[0]} to ${days[days.length - 1]}` : `Day ${days[0]}`} · ${p.lessons.length} lessons${p.ready ? "" : " · being written"}</span></span><span class="pp"><span class="label tnum">${n}/${p.lessons.length} passed</span><span class="bar"><i style="width:${(100 * n) / p.lessons.length}%"></i></span></span></a>`;
  }).join("");

  return `<div class="page">
  <section class="hero">
    <span class="label">${tot} lessons · about 45 minutes each · at your own pace</span>
    <h1>DevOps,<em>from zero</em></h1>
    <p class="sub">Linux, networking, Docker, GitHub Actions, Gradle, Terraform and Kubernetes, then how teams run things today: GitOps with Argo CD, Prometheus, Grafana, ELK and EFK, OpenTelemetry, Dynatrace and supply-chain security. You ship a real app, <span style="white-space:nowrap">hello-devops</span>, from your laptop to a cluster.</p>
    <div class="meta"><span>${C.parts.length} parts</span><span>${tot} lessons</span><span>2 lab projects</span><span>Free tools, runs on your laptop</span></div>
  </section>
  ${term}
  <section class="stats" aria-label="Your progress">
    <div class="stat"><span class="n tnum">${dn}<small>/${tot}</small></span><span class="label">lessons passed</span></div>
    <div class="stat"><span class="n tnum">${streak()}</span><span class="label">day streak</span></div>
    <div class="stat"><span class="n tnum">${learned}</span><span class="label">cards remembered</span></div>
    <div class="stat"><span class="n tnum" style="font-size:34px;line-height:46px">${fmt(pr.finish, { month: "short", day: "numeric" })}</span><span class="label"><a href="#plan">projected finish</a></span></div>
  </section>
  <section class="block"><div class="sec-h"><h2>Your run</h2><span class="label">each part is a job, each lesson a step</span></div>
    <div class="pipe">${pipe}</div></section>
  <section class="block"><div class="sec-h"><h2>How each day works</h2><span class="label">40 to 50 focused minutes</span></div>
    <ol class="day-plan">
      <li><span class="mins">5 min</span><b>Review</b><span>Flip the cards that are due. Spacing reviews over days is what makes things stick.</span></li>
      <li><span class="mins">1 min</span><b>Guess</b><span>Answer the warm-up before reading. A wrong guess still helps you remember.</span></li>
      <li><span class="mins">20 min</span><b>Read</b><span>Short sections, one diagram, a worked example with real output.</span></li>
      <li><span class="mins">15 min</span><b>Do</b><span>The hands-on task on your own laptop, on your own hello-devops repo.</span></li>
      <li><span class="mins">3 min</span><b>Check</b><span>Explain it back in your words, then 3 questions. 2 right passes the day.</span></li>
    </ol></section>
  <section class="block"><div class="sec-h"><h2>The parts</h2><span class="label">a short course for each tool</span></div><div class="parts">${partsList}</div></section>
</div>`;
}

function lessonHead(l) {
  const p = partOf(l.part), done = isDone(l.id);
  return `<header class="lhead">
    <div class="plate"><span class="pd">DAY ${pad(l.day)}</span><span class="pp">Part ${p.part} · ${esc(p.title)}</span></div>
    <h1>${esc(l.title)}</h1>
    ${l.goal ? `<p class="goal">${l.goal}</p>` : ""}
    <div class="lmeta"><span class="chip" title="Status">${glyph(l.id)} ${done ? "Passed" : "Not passed yet"}</span><span class="chip">${l.minutes} min</span>
      ${l.pending ? "" : `<button class="chip" data-act="timer" id="timerBtn"><span class="timer${timer.id === l.id ? " live" : ""}" id="timerTxt">${timer.id === l.id ? timerText() : "Start a focus timer"}</span></button>`}
      <button class="chip${done ? " on" : ""}" data-act="done" data-id="${l.id}">${done ? `${ICON.check} Marked passed` : "Mark as passed"}</button></div>
  </header>`;
}

function viewLesson(id) {
  const l = L(id);
  const i = C.order.indexOf(id), prev = i > 0 ? L(C.order[i - 1]) : null, next = i < C.order.length - 1 ? L(C.order[i + 1]) : null;
  const pager = `<nav class="pager" aria-label="Lessons">${prev ? `<a href="#${prev.id}"><span class="label">Previous · Day ${pad(prev.day)}</span><b>${esc(prev.title)}</b></a>` : "<span></span>"}${next ? `<a class="nx" href="#${next.id}"><span class="label">Next · Day ${pad(next.day)}</span><b>${esc(next.title)}</b></a>` : ""}</nav>`;
  if (l.pending) {
    return `<div class="lesson"><article class="lmain">${lessonHead(l)}<div class="pending"><span class="label">Being written</span><p class="prose">This lesson is still being written. It will appear at this same link. Here is what it covers:</p><p class="prose muted">${esc(l.scope)}</p></div>${pager}</article></div>`;
  }
  const toc = [];
  let h = lessonHead(l);
  if (l.guess) {
    QUIZ["g-" + id] = { qs: [l.guess] };
    const st = QS["g-" + id] || (QS["g-" + id] = { ans: [null], shown: false });
    h += `<section class="card warm" id="warm"><span class="label">Warm-up · guess before you read</span><div id="quiz-g-${id}">${qHTML("g-" + id, l.guess, 0, st, true)}</div>${st.ans[0] == null ? `<span class="muted" style="font-size:15px">No score. Guessing first, even wrongly, helps the answer stick.</span>` : ""}</section>`;
  }
  if (l.terms.length) h += `<section class="block"><span class="label">Words you'll meet</span><dl class="terms">${l.terms.map((t) => `<div><dt>${esc(t.term)}</dt><dd>${t.plain}</dd></div>`).join("")}</dl></section>`;
  l.sections.forEach((s, si) => {
    const sid = `s${si + 1}`; toc.push([sid, s.h]);
    let b = `<section class="lsec" id="${sid}"><h2><span class="n">${pad(si + 1)}</span><span>${esc(s.h)}</span></h2><div class="prose">${s.html}</div>`;
    if (si === 0 && l.diagram) b += `<figure class="fig"><div class="fig-box">${l.diagram}</div><figcaption><b>FIG ${pad(l.day)}</b>${l.caption}</figcaption></figure>`;
    if (si === 0 && l.analogy) b += `<aside class="callout analogy"><div class="ch">${ICON.bulb}Analogy</div><div class="prose">${l.analogy}</div></aside>`;
    if (si === Math.min(1, l.sections.length - 1) && l.realWorld) b += `<aside class="callout world"><div class="ch">${ICON.team}In real teams</div><div class="prose">${l.realWorld}</div></aside>`;
    if (si === l.sections.length - 1 && l.mistake) b += `<aside class="callout mistake"><div class="ch">${ICON.warn}Common mistake</div><div class="prose">${l.mistake}</div></aside>`;
    if (s.refs.length) b += `<div class="refs"><span class="label">Further learning</span><ul>${s.refs.map((r) => `<li><span class="kind ${esc(r.kind)}">${r.kind === "watch" ? ICON.play + " " : ""}${esc(r.kind)}</span><span><a href="${esc(r.url)}" target="_blank" rel="noopener">${r.title}</a><span class="host">${esc(host(r.url))}</span></span></li>`).join("")}</ul></div>`;
    h += b + "</section>";
  });
  if (l.worked) {
    toc.push(["worked", "Worked example"]);
    h += `<section class="block" id="worked"><div class="block-h"><span class="num">EX</span><h2>Worked example: ${l.worked.title}</h2></div><ol class="steps">${l.worked.steps.map((s, k) => `<li><div class="rail"><span class="dot">${k + 1}</span>${k < l.worked.steps.length - 1 ? '<span class="line"></span>' : ""}</div><div class="body"><div class="prose">${s.say}</div>${s.code ? `<pre class="cx"><code>${s.code}</code></pre>` : ""}</div></li>`).join("")}</ol></section>`;
  }
  if (l.code.length) { toc.push(["files", "Files"]); h += `<section class="block" id="files"><div class="block-h"><span class="num">{ }</span><h2>Files for this lesson</h2></div>${l.code.map(codeBox).join("")}</section>`; }
  if (l.commands.length) { toc.push(["cmds", "Commands"]); h += `<section class="block" id="cmds"><div class="block-h"><span class="num">$_</span><h2>Commands you used</h2></div>${cmdRows(l.commands)}</section>`; }
  if (l.recap.length) h += `<section class="recap"><span class="label">Remember</span><ul>${l.recap.map((r) => `<li>${r}</li>`).join("")}</ul></section>`;
  toc.push(["task", "Hands-on"]);
  const tdone = !!(P.tasks[id] && P.tasks[id].d);
  h += `<section class="task" id="task"><span class="label">Hands-on · your turn</span><h3>${l.task.title}</h3><ol>${l.task.steps.map((s) => `<li>${s}</li>`).join("")}</ol>
    <div class="grid-hints" id="hints-${id}" data-shown="0">${l.task.hints.length ? `<button class="linkbtn" data-act="hint" data-id="${id}">Stuck? Show a hint</button>` : ""}</div>
    <div class="donewhen"><button class="check-box${tdone ? " on" : ""}" data-act="task" data-id="${id}" aria-pressed="${tdone}" aria-label="I finished the hands-on">${tdone ? ICON.check : ""}</button><div><span class="label">Done when</span><div>${l.task.doneWhen}</div></div></div></section>`;
  if (l.explain) {
    toc.push(["explain", "Explain it back"]);
    const draft = ls.get("dfz-explain-" + id, "");
    h += `<section class="block" id="explain"><div class="block-h"><span class="num">?!</span><h2>Explain it back</h2></div><p class="prose">${l.explain.prompt}</p>
      <textarea class="field" id="ex-${id}" rows="5" placeholder="Write it in your own words. Rough is fine." data-act="draft" data-id="${id}">${esc(draft)}</textarea>
      <div class="row"><button class="btn ghost sm" data-act="model" data-id="${id}">Compare with a model answer</button><span class="ai-slot" data-ai="feedback" data-id="${id}"></span></div>
      <div id="model-${id}" class="callout world" hidden><div class="ch">Model answer</div><div class="prose">${l.explain.answer}</div></div><div id="fb-${id}" class="card" hidden></div></section>`;
  }
  if (l.check.length) {
    toc.push(["check", "Quick check"]);
    const key = "c-" + id;
    QUIZ[key] = { qs: l.check, result: (s) => (s >= 2 ? (isDone(id) ? "Passed. This day is marked done." : "Passed.") : "You need 2. Read the explanations, then try again."), onDone: (s) => { P.scores[id] = Math.max(P.scores[id] || 0, s); if (s >= 2 && !isDone(id)) setDone(id, true); else commit(); } };
    h += `<section class="block" id="check"><div class="block-h"><span class="num">3Q</span><h2>Quick check</h2></div><p class="muted" style="margin:0">New cases, same idea. 2 of 3 right marks Day ${pad(l.day)} passed and adds its words to your review deck.</p>${quizBlock(key)}</section>`;
  }
  if (l.interview.length) {
    toc.push(["interview", "Interview corner"]);
    h += `<section class="block interview" id="interview"><div class="block-h"><span class="num">IV</span><h2>Interview corner</h2></div><div>${l.interview.map((q) => `<details><summary>${q.q}</summary><div class="a prose">${q.a}</div></details>`).join("")}</div></section>`;
  }
  if (l.deeper) {
    toc.push(["deeper", "Go deeper"]);
    h += `<details class="deeper" id="deeper"><summary><span><span class="label">Optional · about ${l.deeper.minutes} minutes</span><h2>Go deeper</h2></span></summary><div class="inner"><div class="prose">${l.deeper.html}</div>${l.sources.length ? `<div class="refs" style="margin-top:16px"><span class="label">Sources</span><ul>${l.sources.map((s) => `<li><span class="kind docs">src</span><span><a href="${esc(s.url)}" target="_blank" rel="noopener">${s.title}</a><span class="host">${esc(host(s.url))}</span></span></li>`).join("")}</ul></div>` : ""}</div></details>`;
  }
  h += `<section class="block" id="tutor" hidden></section>`;
  h += pager;
  const tocHTML = `<nav class="toc" aria-label="On this page"><span class="label">On this page</span><ol>${toc.map(([a, t]) => `<li><a href="#${id}" data-act="jump" data-to="${a}">${esc(t)}</a></li>`).join("")}</ol></nav>`;
  return `<div class="lesson toc-on"><article class="lmain">${h}</article>${tocHTML}</div>`;
}

function viewPart(n) {
  const p = partOf(n);
  if (!p) return viewHome();
  const nDone = p.lessons.filter(isDone).length;
  const list = p.lessons.map((id) => `<a class="prow" href="#${id}"><span class="pn">${pad(L(id).day)}</span><span><span class="pt" style="font-size:24px">${esc(L(id).title)}</span><span class="pd">${L(id).pending ? "being written" : `${L(id).minutes} min${P.scores[id] != null ? ` · check ${P.scores[id]}/3` : ""}`}</span></span><span class="pp" style="justify-items:end">${glyph(id)}</span></a>`).join("");
  let h = `<div class="page" style="max-width:960px">${p.art ? `<figure class="part-art">${p.art}</figure>` : ""}<header class="lhead"><div class="plate"><span class="pd">PART ${p.part}</span><span class="pp">${nDone}/${p.lessons.length} passed</span></div><h1>${esc(p.title)}</h1>${p.intro ? `<p class="goal">${p.intro}</p>` : ""}</header><section class="parts">${list}</section>`;
  if (!p.ready) return h + `<p class="muted">This part is still being written. It will appear here when it's ready.</p></div>`;
  if (p.resources && p.resources.length) h += `<section class="block"><div class="sec-h"><h2>Go deeper</h2><a class="label" href="#library">the full library</a></div><p class="muted" style="margin:0">Hand-picked for this part: official docs, the best free courses and videos, and the books people keep recommending.</p>${resList(p.resources)}</section>`;
  if (p.recap.length) h += `<section class="recap"><span class="label">Part recap</span><ul>${p.recap.map((r) => `<li>${r}</li>`).join("")}</ul></section>`;
  const cmds = p.lessons.filter(ready).flatMap((id) => L(id).commands);
  if (cmds.length) h += `<section class="block"><div class="sec-h"><h2>Cheat sheet</h2><a class="label" href="#commands">all commands</a></div>${cmdRows(cmds)}</section>`;
  if (p.flashcards.length) {
    const all = p.lessons.every(isDone);
    h += `<section class="block"><div class="sec-h"><h2>Flashcards</h2><span class="label">${p.flashcards.length} cards</span></div><p class="muted" style="margin:0">${all ? "These cards are in your review deck. Practise them here any time." : "Pass every lesson in this part and these cards join your spaced review deck. You can practise them here now."}</p>${deckHTML("p" + p.part, p.flashcards)}</section>`;
  }
  if (p.quiz.length) {
    const key = "q-p" + p.part;
    QUIZ[key] = { qs: p.quiz, result: (s) => `Best so far: ${Math.max(P.quiz["p" + p.part] || 0, s)}/${p.quiz.length}.`, onDone: (s) => { P.quiz["p" + p.part] = Math.max(P.quiz["p" + p.part] || 0, s); activity(); commit(); } };
    h += `<section class="block"><div class="sec-h"><h2>Part quiz</h2><span class="label">${p.quiz.length} questions${P.quiz["p" + p.part] != null ? ` · best ${P.quiz["p" + p.part]}/${p.quiz.length}` : ""}</span></div><p class="muted" style="margin:0">Practice only. Questions marked with a part number revisit earlier parts, which helps you keep them.</p>${quizBlock(key)}</section>`;
  }
  return h + "</div>";
}

const DECK = {};
function deckHTML(key, cards) {
  const d = DECK[key] || (DECK[key] = { i: 0, flip: false, order: cards.map((_, k) => k) });
  const c = cards[d.order[d.i]];
  return `<div class="grid-deck" id="deck-${key}" style="display:grid;gap:12px;max-width:640px">
    <div class="fc${d.flip ? " flip" : ""}" role="button" tabindex="0" aria-label="Flip card" data-act="dflip" data-key="${key}"><div class="fc-in"><div class="fc-face"><span class="label">Question</span><div class="fb" style="font-weight:700;font-size:21px">${c.front}</div></div><div class="fc-face fc-back"><span class="label">Answer</span><div class="fb">${c.back}</div></div></div></div>
    <div class="row"><button class="btn ghost sm" data-act="dmove" data-key="${key}" data-d="-1">Previous</button><button class="btn sm" data-act="dmove" data-key="${key}" data-d="1">Next</button><button class="btn ghost sm" data-act="dshuffle" data-key="${key}">Shuffle</button><span class="label tnum">${d.i + 1} / ${cards.length}</span></div></div>`;
}
const deckCards = (key) => partOf(+key.slice(1)).flashcards;

/* review session */
const review = { active: false, queue: [], i: 0, flip: false, seen: 0 };
function startReview() {
  const d = dueCards();
  review.queue = [...d.due, ...d.fresh.slice(0, NEW_PER_SESSION)].map((c) => c.id);
  review.i = 0; review.flip = false; review.seen = 0; review.active = review.queue.length > 0;
}
function viewReview() {
  const cards = allCards(), byId = Object.fromEntries(cards.map((c) => [c.id, c]));
  const counts = [0, 0, 0, 0, 0, 0, 0];
  for (const c of cards) if (c.unlocked && P.cards[c.id]) counts[P.cards[c.id].box]++;
  const newN = cards.filter((c) => c.unlocked && !P.cards[c.id]).length, locked = cards.filter((c) => !c.unlocked).length;
  const boxes = `<div class="boxes">${[["New", newN], ["Box 1", counts[1]], ["Box 2", counts[2]], ["Box 3", counts[3]], ["Box 4", counts[4]], ["Box 5+", counts[5] + counts[6]]].map(([k, v]) => `<div><b class="tnum">${v}</b><span class="label">${k}</span></div>`).join("")}</div>`;
  let body;
  if (review.active && review.i < review.queue.length) {
    const c = byId[review.queue[review.i]];
    const src = c.src.startsWith("d") ? `Day ${pad(L(c.src).day)} · ${esc(L(c.src).title)}` : `Part ${c.src.slice(1)} flashcards`;
    const pv = preview(c.id);
    body = `<section class="block" style="max-width:680px"><div class="row" style="justify-content:space-between"><span class="label tnum">Card ${review.i + 1} of ${review.queue.length}</span><a class="label" href="#${c.src}">${src}</a></div>
      <div class="fc${review.flip ? " flip" : ""}" role="button" tabindex="0" aria-label="Flip card" data-act="rflip"><div class="fc-in"><div class="fc-face"><span class="label">${c.src.startsWith("d") ? "What does this mean?" : "Question"}</span><div class="${c.src.startsWith("d") ? "ft" : "fb"}" ${c.src.startsWith("d") ? "" : 'style="font-weight:700;font-size:21px"'}>${c.front}</div><span class="muted" style="font-size:14px">Say the answer out loud, then flip (space bar).</span></div><div class="fc-face fc-back"><span class="label">Answer</span><div class="fb">${c.back}</div></div></div></div>
      ${review.flip ? `<div class="rate">${["Again", "Hard", "Good", "Easy"].map((t, r) => `<button class="btn ${r === 2 ? "" : "ghost"} sm" data-act="rate" data-r="${r}"><span>${t}</span><small>${pv[r]}</small></button>`).join("")}</div><p class="muted" style="font-size:14px;margin:0">Keys 1 to 4. Be honest: "Again" brings it back soon, which is how it sticks.</p>` : `<div><button class="btn" data-act="rflip">Show answer</button></div>`}</section>`;
  } else if (review.active) {
    body = `<section class="card" style="max-width:680px"><span class="label">Session done</span><h2 style="font:800 34px/1 var(--f-display);text-transform:uppercase">${review.seen} cards reviewed</h2><p class="muted" style="margin:0">Cards you knew come back in a few days, then in a week, then later. Come back tomorrow for the next batch.</p><div class="row"><a class="btn" href="#${nextUp() || "home"}">${nextUp() ? `Go to Day ${pad(L(nextUp()).day)}` : "Back to Today"} ${ICON.arrow}</a></div></section>`;
  } else {
    const d = dueCards(), n = d.due.length + Math.min(d.fresh.length, NEW_PER_SESSION);
    body = `<section class="card" style="max-width:680px"><span class="label">${n ? "Ready" : "All caught up"}</span><h2 style="font:800 34px/1 var(--f-display);text-transform:uppercase">${n ? `${n} card${n === 1 ? "" : "s"} to review` : "Nothing due right now"}</h2><p class="muted" style="margin:0">${n ? "About 5 minutes. Read the front, answer in your head, flip, then rate how well you knew it." : d.total ? "Pass the next lesson to add its words, or come back tomorrow when older cards are due again." : "Pass your first lesson and its key words become review cards here."}</p>${n ? `<div><button class="btn" data-act="rstart">Start review ${ICON.arrow}</button></div>` : ""}</section>`;
  }
  return `<div class="page" style="max-width:860px"><header class="lhead"><div class="plate"><span class="pd">REVIEW</span><span class="pp">spaced repetition</span></div><h1>Remember it</h1><p class="goal">Every term from the lessons you pass becomes a card. Each time you know a card, it waits longer before it comes back: 1 day, 3, 7, 14, then 30. ${locked ? `${locked} more cards unlock as you pass lessons.` : ""}</p></header>${body}<section class="block"><span class="label">Your deck</span>${boxes}</section></div>`;
}

let cmdFilter = "all", cmdQ = "";
function viewCommands() {
  const chips = [["all", "All"], ...C.parts.filter((p) => p.ready && p.lessons.some((id) => ready(id) && L(id).commands.length)).map((p) => ["p" + p.part, p.tool === "Overview" ? "Setup" : p.tool])];
  const q = cmdQ.toLowerCase();
  let body = "";
  for (const p of C.parts) {
    if (cmdFilter !== "all" && cmdFilter !== "p" + p.part) continue;
    for (const id of p.lessons) {
      if (!ready(id)) continue;
      const cmds = L(id).commands.filter((c) => !q || (c.cmd + " " + c.what).toLowerCase().includes(q));
      if (cmds.length) body += `<section class="block"><div class="sec-h" style="border:0;padding:0"><a href="#${id}" style="color:inherit;text-decoration:none"><span class="label">Day ${pad(L(id).day)} · ${esc(p.tool)}</span><h3 style="font:800 24px/1.1 var(--f-display);text-transform:uppercase">${esc(L(id).title)}</h3></a></div>${cmdRows(cmds)}</section>`;
    }
  }
  return `<div class="page" style="max-width:920px"><header class="lhead"><div class="plate"><span class="pd">$_</span><span class="pp">cheat sheet</span></div><h1>Commands</h1><p class="goal">Every command from the lessons, with what it does. Search it when you forget a flag.</p></header>
    <div class="filter"><input class="field" id="cmdq" type="search" placeholder="Search, for example: logs, apply, port" value="${esc(cmdQ)}" data-act="cmdq">${chips.map(([k, t]) => `<button class="chip${cmdFilter === k ? " on" : ""}" data-act="cmdf" data-f="${k}">${esc(t)}</button>`).join("")}</div>
    <div id="cmdBody" style="display:grid;gap:34px">${body || `<p class="muted">No commands match yet.</p>`}</div></div>`;
}

let glQ = "";
function viewGlossary() {
  const terms = [];
  for (const id of C.order) if (ready(id)) for (const t of L(id).terms) terms.push({ ...t, lid: id });
  terms.sort((a, b) => a.term.localeCompare(b.term, "en", { sensitivity: "base" }));
  const q = glQ.toLowerCase();
  let body = "", letter = "";
  for (const t of terms) {
    if (q && !(t.term + " " + t.plain).toLowerCase().includes(q)) continue;
    const L0 = t.term[0].toUpperCase();
    if (L0 !== letter) { letter = L0; body += `<div class="letter">${esc(/[A-Z]/.test(letter) ? letter : "#")}</div>`; }
    body += `<div><dt>${esc(t.term)}</dt><dd>${t.plain}<a class="src" href="#${t.lid}">Day ${pad(L(t.lid).day)} · ${esc(L(t.lid).title)}</a></dd></div>`;
  }
  return `<div class="page" style="max-width:920px"><header class="lhead"><div class="plate"><span class="pd">A–Z</span><span class="pp">${terms.length} terms</span></div><h1>Glossary</h1><p class="goal">Every term the course defines, in plain words, with the day it comes from.</p></header>
    <div class="filter"><input class="field" id="glq" type="search" placeholder="Search terms" value="${esc(glQ)}" data-act="glq"></div><dl class="gl" id="glBody" style="margin:0">${body || `<p class="muted">No terms match.</p>`}</dl></div>`;
}

function resList(items) {
  return `<ul class="res">${items.map((r) => `<li><span class="kind ${esc(r.kind)}">${r.kind === "watch" ? ICON.play + " " : ""}${esc(r.kind)}</span><span class="rb"><a href="${esc(r.url)}" target="_blank" rel="noopener">${r.title}</a><span class="host">${esc(host(r.url))}</span>${r.why ? `<span class="why2">${r.why}</span>` : ""}${r.from ? `<a class="src" href="#${r.from}">Day ${pad(L(r.from).day)} · ${esc(L(r.from).title)}</a>` : ""}</span></li>`).join("")}</ul>`;
}
let libKind = "all", libQ = "";
function viewLibrary() {
  const q = libQ.toLowerCase();
  const kinds = [["all", "All"], ["watch", "Videos"], ["docs", "Docs"], ["read", "Reading"], ["listen", "Listening"]];
  let body = "", total = 0;
  for (const p of C.parts) {
    const seen = new Set(), items = [];
    for (const r of p.resources || []) { if (!seen.has(r.url)) { seen.add(r.url); items.push(r); } }
    for (const id of p.lessons) if (ready(id)) for (const s of L(id).sections) for (const r of s.refs) if (!seen.has(r.url)) { seen.add(r.url); items.push({ ...r, from: id }); }
    const shown = items.filter((r) => (libKind === "all" || r.kind === libKind) && (!q || (r.title + " " + (r.why || "") + " " + r.url).toLowerCase().includes(q)));
    total += shown.length;
    if (shown.length) body += `<section class="block"><div class="sec-h" style="border:0;padding:0"><a href="#p${p.part}" style="color:inherit;text-decoration:none"><span class="label">Part ${p.part}</span><h3 style="font:800 26px/1.1 var(--f-display);text-transform:uppercase;margin:0">${esc(p.title)}</h3></a><span class="label tnum">${shown.length}</span></div>${resList(shown)}</section>`;
  }
  return `<div class="page" style="max-width:920px"><header class="lhead"><div class="plate"><span class="pd">LIB</span><span class="pp">${total} links</span></div><h1>Library</h1><p class="goal">Every link and video in the course in one place, grouped by part. Official docs first, then the best free courses, talks and books.</p></header>
    <div class="filter"><input class="field" id="libq" type="search" placeholder="Search, for example: PromQL, Helm, grep" value="${esc(libQ)}" data-act="libq">${kinds.map(([k, t]) => `<button class="chip${libKind === k ? " on" : ""}" data-act="libk" data-k="${k}">${esc(t)}</button>`).join("")}</div>
    <div style="display:grid;gap:34px">${body || `<p class="muted">Nothing matches yet.</p>`}</div></div>`;
}
let labSel = null;
const LABDESC = {
  "hello-devops": "The Python web app you ship all course: Dockerfiles, Compose, workflows, Terraform, Kubernetes, Helm, Argo CD, monitoring, logging, tracing and policy.",
  "linux": "Sample logs and files for the Linux lessons. Mount this folder into the practice container.",
  "hello-jvm": "A small Kotlin multi-project Gradle build with a Dockerfile and a CI workflow.",
  "terraform-practice": "Small Terraform folders for the language and state exercises.",
};
let labProj = "hello-devops";
function viewLabs() {
  const all = C.labs;
  if (!all.length) return `<div class="page"><p>No lab files yet.</p></div>`;
  const projs = [...new Set(all.map((f) => f.proj))];
  if (!projs.includes(labProj)) labProj = projs[0];
  const files = all.filter((f) => f.proj === labProj);
  if (!labSel || !files.find((f) => f.path === labSel)) labSel = files[0].path;
  const f = files.find((x) => x.path === labSel), rel = (x) => x.path.slice(x.proj.length + 1);
  const dl = L("d" + pad(f.day));
  return `<div class="page"><header class="lhead"><div class="plate"><span class="pd">LAB</span><span class="pp">finished reference · ${all.length} files</span></div><h1>Lab files</h1><p class="goal">The finished lab repos, every file checked. Build yours by following the lessons, then come here to compare. Copy a file only when you are truly stuck.</p></header>
    <div class="filter">${projs.map((x) => `<button class="chip${x === labProj ? " on" : ""}" data-act="labp" data-p="${esc(x)}">${esc(x)}</button>`).join("")}</div>
    <p class="muted" style="margin:0">${esc(LABDESC[labProj] || "")}</p>
    <div class="labgrid"><div class="labtree" role="list">${files.map((x) => `<button class="${x.path === labSel ? "on" : ""}" data-act="lab" data-p="${esc(x.path)}" role="listitem"><span>${esc(rel(x))}</span><small>D${pad(x.day)}</small></button>`).join("")}</div>
    <div style="min-width:0;display:grid;gap:10px"><span class="label">Final version from Day ${pad(f.day)}${dl ? ` · <a href="#${dl.id}">${esc(dl.title)}</a>` : ""} · ${f.lines} lines</span>${codeBox({ title: f.path, lang: f.lang, html: f.html })}</div></div></div>`;
}

function viewPlan() {
  const st = startDate(), pr = projection();
  const rows = C.order.map((id, k) => {
    const l = L(id), planned = addDays(st, k), done = isDone(id);
    const when = done && P.log[id].at ? `passed ${fmt(ymd(new Date(P.log[id].at)), { month: "short", day: "numeric" })}` : planned < today() ? "behind" : "";
    return `<tr><td>${glyph(id)}</td><td class="dt tnum">D${pad(l.day)}</td><td><a href="#${id}">${esc(l.title)}</a></td><td class="dt">${fmt(planned)}</td><td class="dt">${when}</td></tr>`;
  }).join("");
  const behind = C.order.filter((id, k) => !isDone(id) && addDays(st, k) < today()).length;
  return `<div class="page" style="max-width:920px"><header class="lhead"><div class="plate"><span class="pd">PLAN</span><span class="pp">one lesson a day</span></div><h1>Plan and pace</h1><p class="goal">One lesson a day takes ${C.order.length} days, about 8 weeks. Long lessons split well over two sittings, and short ones pair well on a weekend. The plan moves with you.</p></header>
    <section class="stats"><div class="stat"><span class="n tnum" style="font-size:34px">${fmt(st, { month: "short", day: "numeric" })}</span><span class="label">start date</span></div><div class="stat"><span class="n tnum" style="font-size:34px">${fmt(pr.planned, { month: "short", day: "numeric" })}</span><span class="label">planned finish</span></div><div class="stat"><span class="n tnum" style="font-size:34px">${fmt(pr.finish, { month: "short", day: "numeric" })}</span><span class="label">projected finish</span></div><div class="stat"><span class="n tnum" style="font-size:34px;${behind ? "color:var(--orange)" : ""}">${behind}</span><span class="label">behind plan</span></div></section>
    <div class="row"><label class="label" for="startIn">Start date</label><input class="field" id="startIn" type="date" value="${st}" style="max-width:200px" data-act="start"><span class="muted" style="font-size:15px">Your start is set the day you pass your first lesson. Change it any time.</span></div>
    <div class="tablewrap"><table class="plan-t"><thead><tr><th></th><th>Day</th><th>Lesson</th><th>Planned</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table></div>
    <section class="block"><span class="label">Start over</span><div class="row" id="resetRow"><button class="btn ghost sm" data-act="reset">Reset all progress</button></div></section></div>`;
}

/* ---------------- AI helpers (only when the page can ask Claude) ---------------- */
const TUTOR = (l) => `You are a patient tutor for one learner: an experienced software engineer (backend, Kotlin) who is new to DevOps and the cloud, working through a hands-on course on a Mac.
Teach like a good human tutor:
- If the message does not show what he is stuck on, ask ONE short question first.
- Each reply: a few short sentences, one small step forward (a hint, a tiny example, or a command to try), at most one question.
- Prefer hints over full answers. If he is clearly stuck, give a concrete foothold, then let him finish.
- If he asks for a quiz, a summary or flashcards, just make it.
- Very simple English. Short sentences. Define any DevOps term you use. No emojis. Never open with praise.
- Stay on this lesson. Commands are for macOS with zsh.

Lesson: Day ${l.day}, ${l.title}
Lesson text:
${l.text}`;
const mdLite = (t) => esc(t).replace(/```[a-z]*\n([\s\S]*?)```/g, (_m, c) => `<pre class="cx">${c}</pre>`).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
  .split(/\n{2,}/).map((p) => (p.startsWith("<pre") ? p : /^\s*[-*] /m.test(p) ? "<ul>" + p.split(/\n/).map((x) => x.replace(/^\s*[-*] /, "")).filter(Boolean).map((x) => `<li>${x}</li>`).join("") + "</ul>" : `<p>${p.replace(/\n/g, "<br>")}</p>`)).join("");
const chat = {};
function mountAi() {
  const r = route();
  if (!/^d\d\d$/.test(r) || !ready(r) || !sample) return;
  const box = $("#tutor");
  if (box) { box.hidden = false; renderTutor(r); }
  $$(".ai-slot[data-ai=feedback]").forEach((s) => { s.innerHTML = `<button class="btn ghost sm" data-act="feedback" data-id="${s.dataset.id}">Get feedback from Claude</button>`; });
}
function renderTutor(id) {
  const box = $("#tutor"); if (!box) return;
  const c = chat[id] || (chat[id] = { msgs: [], busy: false, err: "" });
  const chips = ["Explain it more simply", "I'm stuck on the hands-on", "Quiz me on this lesson", "How is this used at work?"];
  box.innerHTML = `<div class="block-h"><span class="num">AI</span><h2>Ask the tutor</h2></div><p class="muted" style="margin:0">It knows this lesson. It helps you find the answer yourself, one step at a time.</p>
    <div class="tutor-msgs">${c.msgs.map((m) => `<div class="${m.role === "user" ? "u" : "a prose"}">${m.role === "user" ? esc(m.content) : m.content ? mdLite(m.content) : '<span class="muted">Thinking...</span>'}</div>`).join("")}</div>
    ${c.msgs.length ? "" : `<div class="row">${chips.map((t) => `<button class="chip" data-act="ask" data-q="${esc(t)}">${esc(t)}</button>`).join("")}</div>`}
    <textarea class="field" id="tq-${id}" rows="2" placeholder="Ask anything about this lesson (Ctrl or Cmd + Enter to send)"></textarea>
    <div class="row"><button class="btn sm" data-act="ask"${c.busy ? " disabled" : ""}>Ask</button>${c.msgs.length ? `<button class="btn ghost sm" data-act="askreset">Start over</button>` : ""}${c.err ? `<span style="color:var(--red)">${esc(c.err)}</span>` : ""}</div>`;
}
async function ask(id, text) {
  text = (text || "").trim();
  const c = chat[id];
  if (!text || c.busy || !sample) return;
  c.busy = true; c.err = "";
  const hist = [...c.msgs, { role: "user", content: text }];
  c.msgs = [...hist, { role: "assistant", content: "" }]; renderTutor(id);
  const payload = hist.map((m, i) => (i === 0 ? { ...m, content: TUTOR(L(id)) + "\n\nLearner: " + m.content } : m));
  try {
    const r = await sample(payload, { cache: false, onText: (u) => { c.msgs[c.msgs.length - 1].content = u.text; const last = $("#tutor .tutor-msgs > div:last-child"); if (last) last.innerHTML = mdLite(u.text); } });
    c.msgs[c.msgs.length - 1].content = r.text;
  } catch (e) {
    c.msgs = hist.slice(0, -1);
    c.err = e && e.code === "rate_limited" ? "Too many questions just now. Try again in a minute." : e && e.code === "not_granted" ? "Asking Claude is turned off for this page." : "That didn't go through. Try again.";
  }
  c.busy = false; renderTutor(id);
}
async function feedback(id) {
  const l = L(id), ta = $("#ex-" + id), out = $("#fb-" + id);
  if (!sample || !ta || ta.value.trim().length < 20) { toast("Write at least a sentence or two first."); return; }
  out.hidden = false; out.innerHTML = '<span class="muted">Reading your explanation...</span>';
  const prompt = `A learner new to DevOps explained an idea in their own words. Give short, honest feedback in very simple English: first what they got right (one line), then the most important thing missing or wrong (one or two lines), then one question that pushes them a little further. No praise words, no emojis, under 120 words.

Prompt they answered and a good answer: ${l.explain.raw}
Their explanation: ${ta.value}`;
  try { const r = await sample(prompt, { cache: false, onText: (u) => { out.innerHTML = mdLite(u.text); } }); out.innerHTML = mdLite(r.text); }
  catch { out.innerHTML = '<span class="muted">Feedback is not available right now. Compare with the model answer instead.</span>'; }
}

/* ---------------- focus timer ---------------- */
const timer = { id: null, start: 0, iv: null };
function timerText() { const s = Math.floor((Date.now() - timer.start) / 1000); return `Focus ${pad(Math.floor(s / 60))}:${pad(s % 60)} / ${L(timer.id).minutes}:00 · stop`; }
function tickTimer() { const t = $("#timerTxt"); if (t && timer.id === route()) t.textContent = timerText(); }

/* ---------------- render ---------------- */
let firstRender = true;
function render(scroll = true) {
  const r = route();
  codeN = 0;
  let html;
  if (/^d\d\d$/.test(r) && L(r)) html = viewLesson(r);
  else if (/^p\d$/.test(r) && partOf(+r.slice(1))) html = viewPart(+r.slice(1));
  else if (r === "review") html = viewReview();
  else if (r === "commands") html = viewCommands();
  else if (r === "glossary") html = viewGlossary();
  else if (r === "labs") html = viewLabs();
  else if (r === "library") html = viewLibrary();
  else if (r === "plan") html = viewPlan();
  else html = viewHome();
  main.innerHTML = html;
  chrome();
  if (scroll) { window.scrollTo(0, 0); if (!firstRender) main.focus({ preventScroll: true }); }
  firstRender = false;
  const l = L(r);
  document.title = l ? `Day ${pad(l.day)}: ${l.title} · DevOps from Zero` : "DevOps from Zero";
  if (l && !l.pending) { watchToc(); mountAi(); }
}
let tocIO = null;
function watchToc() {
  if (tocIO) tocIO.disconnect();
  const links = $$(".toc a");
  if (!links.length || typeof IntersectionObserver === "undefined") return;
  tocIO = new IntersectionObserver((ents) => {
    const vis = ents.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (vis[0]) links.forEach((a) => a.classList.toggle("act", a.dataset.to === vis[0].target.id));
  }, { rootMargin: "-80px 0px -65% 0px" });
  links.forEach((a) => { const el = document.getElementById(a.dataset.to); if (el) tocIO.observe(el); });
}

/* ---------------- events ---------------- */
document.addEventListener("click", async (e) => {
  const b = e.target.closest("[data-act]");
  if (!b) return;
  const a = b.dataset.act, r = route();
  if (a === "pick") {
    const key = b.dataset.key, st = QS[key], i = +b.dataset.i, j = +b.dataset.j;
    if (!st) return;
    st.ans[i] = j;
    if (key.startsWith("g-")) { const box = $("#warm"); if (box) { const z = QUIZ[key]; box.querySelector(`#quiz-${key}`).innerHTML = qHTML(key, z.qs[0], 0, st, true); const hint = box.querySelector(".muted"); if (hint) hint.remove(); } }
    else refreshQuiz(key);
  } else if (a === "grade") {
    const key = b.dataset.key, z = QUIZ[key], st = QS[key];
    st.shown = true;
    const s = z.qs.reduce((acc, q, i) => acc + (st.ans[i] === q.answer ? 1 : 0), 0);
    z.onDone(s);
    refreshQuiz(key);
    if (key.startsWith("c-")) { const head = $(".lhead"); if (head) head.outerHTML = lessonHead(L(r)); }
  } else if (a === "retry") {
    const key = b.dataset.key; QS[key] = { ans: QUIZ[key].qs.map(() => null), shown: false }; refreshQuiz(key);
  } else if (a === "done") {
    const id = b.dataset.id; setDone(id, !isDone(id)); const head = $(".lhead"); if (head) head.outerHTML = lessonHead(L(id));
  } else if (a === "task") {
    const id = b.dataset.id, on = !(P.tasks[id] && P.tasks[id].d);
    P.tasks[id] = { d: on, u: nowIso() }; if (on) activity(); commit();
    b.classList.toggle("on", on); b.innerHTML = on ? ICON.check : ""; b.setAttribute("aria-pressed", String(on));
    if (on) toast("Nice. Now explain it back, then take the quick check.");
  } else if (a === "hint") {
    const id = b.dataset.id, box = $("#hints-" + id), n = +box.dataset.shown + 1, hints = L(id).task.hints;
    box.dataset.shown = n;
    box.innerHTML = hints.slice(0, n).map((h, k) => `<div class="hint"><span class="label">Hint ${k + 1}</span>${h}</div>`).join("") + (n < hints.length ? `<button class="linkbtn" data-act="hint" data-id="${id}" style="margin-top:8px">Show another hint</button>` : "");
    box.style.display = "grid"; box.style.gap = "8px";
  } else if (a === "model") {
    const m = $("#model-" + b.dataset.id); m.hidden = !m.hidden; b.textContent = m.hidden ? "Compare with a model answer" : "Hide the model answer";
  } else if (a === "feedback") {
    feedback(b.dataset.id);
  } else if (a === "copy") {
    const el = document.getElementById(b.dataset.target);
    const text = el ? el.innerText : "";
    try { await navigator.clipboard.writeText(text); b.textContent = "Copied"; }
    catch { const rg = document.createRange(); rg.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(rg); b.textContent = "Selected"; }
    setTimeout(() => (b.textContent = "Copy"), 1500);
  } else if (a === "jump") {
    e.preventDefault(); const el = document.getElementById(b.dataset.to); if (el) { if (el.tagName === "DETAILS") el.open = true; el.scrollIntoView({ behavior: "smooth", block: "start" }); }
  } else if (a === "timer") {
    if (timer.id === r) { clearInterval(timer.iv); timer.id = null; b.querySelector(".timer").classList.remove("live"); b.querySelector(".timer").textContent = "Start a focus timer"; }
    else { clearInterval(timer.iv); timer.id = r; timer.start = Date.now(); timer.iv = setInterval(tickTimer, 1000); b.querySelector(".timer").classList.add("live"); tickTimer(); }
  } else if (a === "rstart") { startReview(); render(); }
  else if (a === "rflip") { review.flip = !review.flip; render(false); }
  else if (a === "rate") { rateNow(+b.dataset.r); }
  else if (a === "dflip") { const d = DECK[b.dataset.key]; d.flip = !d.flip; b.classList.toggle("flip", d.flip); }
  else if (a === "dmove" || a === "dshuffle") {
    const key = b.dataset.key, d = DECK[key], cards = deckCards(key);
    if (a === "dshuffle") { d.order = d.order.map((v) => [Math.random(), v]).sort((x, y) => x[0] - y[0]).map((x) => x[1]); d.i = 0; }
    else d.i = (d.i + +b.dataset.d + cards.length) % cards.length;
    d.flip = false; $("#deck-" + key).outerHTML = deckHTML(key, cards);
  } else if (a === "cmdf") { cmdFilter = b.dataset.f; render(false); }
  else if (a === "lab") { labSel = b.dataset.p; render(false); }
  else if (a === "labp") { labProj = b.dataset.p; labSel = null; render(false); }
  else if (a === "libk") { libKind = b.dataset.k; render(false); }
  else if (a === "sidetog") { const n = +b.dataset.p, cur = b.getAttribute("aria-expanded") === "true"; sideOpen[n] = !cur; chrome(); }
  else if (a === "reset") {
    $("#resetRow").innerHTML = `<span>This clears every lesson, score and review card${ref ? " on all your devices" : ""}.</span><button class="btn sm" data-act="reset2">Yes, reset</button><button class="btn ghost sm" data-act="reset0">Keep my progress</button>`;
  } else if (a === "reset2") { P = norm({}); commit(); if (ref) write(); render(); toast("Progress reset."); }
  else if (a === "reset0") { render(false); }
  else if (a === "ask") { const ta = $("#tq-" + r); ask(r, b.dataset.q || (ta && ta.value)); }
  else if (a === "askreset") { chat[r] = { msgs: [], busy: false, err: "" }; renderTutor(r); }
});
function rateNow(rv) {
  const id = review.queue[review.i];
  rateCard(id, rv);
  review.seen++;
  if (rv === 0) review.queue.push(id);
  review.i++; review.flip = false; render(false);
}
let inputT = null;
document.addEventListener("input", (e) => {
  const t = e.target, a = t.dataset && t.dataset.act;
  if (a === "draft") { clearTimeout(inputT); inputT = setTimeout(() => ls.set("dfz-explain-" + t.dataset.id, t.value), 400); }
  else if (a === "cmdq" || a === "glq" || a === "libq") {
    if (a === "cmdq") cmdQ = t.value; else if (a === "glq") glQ = t.value; else libQ = t.value;
    const pos = t.selectionStart; render(false); const n = $("#" + a); if (n) { n.focus(); try { n.setSelectionRange(pos, pos); } catch { /* search input */ } }
  }
});
document.addEventListener("change", (e) => {
  const t = e.target;
  if (t.dataset && t.dataset.act === "start" && /^\d{4}-\d\d-\d\d$/.test(t.value)) { P.start = t.value; P.startU = nowIso(); commit(); render(false); }
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") openSide(false);
  const tag = (e.target.tagName || "").toLowerCase();
  if (tag === "textarea" && (e.metaKey || e.ctrlKey) && e.key === "Enter" && e.target.id.startsWith("tq-")) { ask(route(), e.target.value); return; }
  if (tag === "input" || tag === "textarea") return;
  if (route() === "review" && review.active && review.i < review.queue.length) {
    if (e.key === " " || e.key === "Enter") { e.preventDefault(); review.flip = !review.flip; render(false); }
    else if (review.flip && ["1", "2", "3", "4"].includes(e.key)) rateNow(+e.key - 1);
  } else if ((e.key === " " || e.key === "Enter") && e.target.dataset && e.target.dataset.act === "dflip") { e.preventDefault(); e.target.click(); }
});
window.addEventListener("hashchange", () => { if (route() === "review") review.active = false; render(); });
render();
})();
