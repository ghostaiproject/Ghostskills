// ui.js: form state, render, countdown, copy alarm. Saved answers stay in this browser only.
const $ = id => document.getElementById(id);
const KEY = "nap-planner-v1";
const EXAMPLE = { wokeDay: 1, wokeAt: "10:30", bed: "22:00", wake: "07:00", tired: "fine" };
let state = { ...EXAMPLE }, plan = null, isExample = true;

try { const s = JSON.parse(localStorage.getItem(KEY) || "null"); if (s) { state = { ...EXAMPLE, ...s }; isExample = false; } } catch (e) {}

function syncForm() {
  document.querySelectorAll(".pills").forEach(g => {
    const name = g.dataset.name;
    g.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(String(state[name]) === b.dataset.v)));
  });
  $("wokeAt").value = state.wokeAt; $("wake").value = state.wake;
  const preset = ["21:00", "22:00", "23:00"].includes(state.bed);
  $("bedOther").value = preset ? "" : state.bed;
}

document.querySelectorAll(".pills").forEach(g => g.addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b) return;
  state[g.dataset.name] = g.dataset.name === "wokeDay" ? Number(b.dataset.v) : b.dataset.v;
  syncForm();
}));
$("wokeAt").addEventListener("input", e => state.wokeAt = e.target.value);
$("wake").addEventListener("input", e => state.wake = e.target.value);
$("bedOther").addEventListener("input", e => { if (e.target.value) { state.bed = e.target.value; syncForm(); } });

$("form").addEventListener("submit", e => {
  e.preventDefault();
  if (!state.wokeAt) { $("wokeAt").focus(); return; }
  isExample = false;
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (err) {}
  render();
  $("result").scrollIntoView({ behavior: "smooth", block: "start" });
});

$("copy").addEventListener("click", async () => {
  if (!plan || !plan.nap) return;
  const text = `Alarm ${fmt(plan.nap.start + plan.nap.len)} (nap ${plan.nap.len} min)`;
  try { await navigator.clipboard.writeText(text); $("copy").textContent = "Copied"; }
  catch (err) { const r = document.createRange(); r.selectNodeContents($("alarmAt")); getSelection().removeAllRanges(); getSelection().addRange(r); $("copy").textContent = "Selected"; }
  setTimeout(() => $("copy").textContent = "Copy alarm", 1800);
});

function countdown(m, nowM) {
  const d = Math.round(((m - nowM) % 1440 + 1440) % 1440);
  return d <= 0 ? "now" : `in ${dur(d)}`;
}

function render() {
  const now = new Date();
  plan = planNap(state, now);
  const p = plan;
  $("example").hidden = !isExample;
  $("clock").textContent = fmt(p.nowM);
  const has = !!p.nap;
  document.querySelector(".lie").hidden = !has; document.querySelector(".alarm").hidden = !has;
  $("noNap").hidden = has;
  if (has) {
    const end = p.nap.start + p.nap.len;
    $("lieAt").textContent = fmt(p.nap.start); $("lieIn").textContent = countdown(p.nap.start, p.nowM);
    $("alarmAt").textContent = fmt(end); $("alarmLen").textContent = `${p.nap.len} min nap · ${countdown(end, p.nowM)}`;
  }
  $("backup").textContent = p.backup ? `Backup if 25 min isn't enough: one full cycle, alarm ${fmt(p.backup.start + 90)}. Never 35–60 min.` : "";
  $("lightsAt").textContent = fmt(p.lights); $("upAt").textContent = fmt(p.up);
  $("cyc").textContent = p.cycles; $("awake").textContent = dur(p.awake).replace(" ", "");
  $("warn").hidden = !p.longAwake;
  $("dial").innerHTML = drawDial(p);
  const rows = [];
  if (has) rows.push(["var(--nap)", `${fmt(p.nap.start)}–${fmt(p.nap.start + p.nap.len)}`, `nap, ${p.nap.len} min`]);
  rows.push(["var(--cut)", fmt(p.cutoff), "no naps after"]);
  rows.push(["var(--dim)", fmt(p.lights), `lights out, asleep ~${fmt(p.onset)}`]);
  for (let i = 0; i < p.cycles; i++) rows.push([`var(--c${i % 6})`, fmt(p.onset + i * 90 + 90), `C${i + 1} ends${i === p.cycles - 1 ? ", wake up" : ""}`]);
  if (p.options) rows.push(["var(--sleep)", p.options.map(o => o.up).join(" / "), "5 or 6 cycles (no wake time set)"]);
  $("times").innerHTML = rows.map(([c, t, w]) => `<li><i style="background:${c}"></i><b>${t}</b><span>${w}</span></li>`).join("");
}

syncForm(); render();
setInterval(() => { if (plan) { const n = new Date(); $("clock").textContent = fmt(n.getHours() * 60 + n.getMinutes());
  if (plan.nap) { const nm = n.getHours() * 60 + n.getMinutes(); $("lieIn").textContent = countdown(plan.nap.start, nm);
    $("alarmLen").textContent = `${plan.nap.len} min nap · ${countdown(plan.nap.start + plan.nap.len, nm)}`; } } }, 30000);
