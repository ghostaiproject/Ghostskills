// dial.js: 24h split dial (port of nap_graph.py). Night = right half, day = left half.
const CX = 190, CY = 190, R_STATE = 150, R_CYC = 126;
const R_STAGE = { W: 110, R: 94, N1: 78, N2: 62, N3: 46 };
const PATTERN = [
  [["N1", 5], ["N2", 20], ["N3", 45], ["N2", 10], ["R", 10]],
  [["N1", 5], ["N2", 25], ["N3", 30], ["N2", 10], ["R", 20]],
  [["N1", 5], ["N2", 30], ["N3", 15], ["N2", 15], ["R", 25]],
  [["N1", 5], ["N2", 55], ["R", 30]],
  [["N1", 5], ["N2", 45], ["R", 40]],
  [["N1", 5], ["N2", 40], ["R", 45]],
];

function drawDial(p) {
  const night = ((p.up - p.lights) % 1440 + 1440) % 1440;
  const ang = m => { const off = ((m - p.lights) % 1440 + 1440) % 1440;
    return off <= night ? off / night * 180 : 180 + (off - night) / (1440 - night) * 180; };
  const pt = (r, a) => { const t = a * Math.PI / 180; return [CX + r * Math.sin(t), CY - r * Math.cos(t)]; };
  const P = ([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`;
  const arc = (r, m1, m2) => { const a1 = ang(m1); let a2 = a1 + (((ang(m2) - a1) % 360 + 360) % 360 || 359.9);
    return `M${P(pt(r, a1))} A${r},${r} 0 ${a2 - a1 > 180 ? 1 : 0} 1 ${P(pt(r, a2))}`; };
  const ring = (r, m1, m2, cls, w, extra = "") =>
    `<path d="${arc(r, m1, m2)}" class="${cls}" stroke-width="${w}" fill="none"${extra}/>`;
  const txt = (x, y, s, cls, anchor = "middle") =>
    `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" class="${cls}" text-anchor="${anchor}">${s}</text>`;
  const o = [];
  for (const r of Object.values(R_STAGE)) o.push(`<circle cx="${CX}" cy="${CY}" r="${r}" class="d-grid" fill="none"/>`);
  for (const [s, r] of Object.entries(R_STAGE)) {
    const [x, y] = pt(r, ang(p.lights) - 7);
    o.push(txt(x, y + 3, { W: "Awake", R: "REM" }[s] || s, "d-stage", "end"));
  }
  o.push(ring(R_STATE, p.up, p.lights, "s-awake", 16));
  o.push(ring(R_STATE, p.lights, p.up, "s-sleep", 16));
  if (p.nap) o.push(ring(R_STATE, p.nap.start, p.nap.start + Math.max(p.nap.len, 8), "s-nap", 24));
  for (let h = 0; h < 24; h++) {
    const a = ang(h * 60), big = h % 3 === 0;
    o.push(`<line x1="${pt(R_STATE + 11, a)[0].toFixed(1)}" y1="${pt(R_STATE + 11, a)[1].toFixed(1)}" x2="${pt(R_STATE + (big ? 18 : 14), a)[0].toFixed(1)}" y2="${pt(R_STATE + (big ? 18 : 14), a)[1].toFixed(1)}" class="d-tick"/>`);
    if (big) { const [x, y] = pt(R_STATE + 29, a); o.push(txt(x, y + 4, pad(h), "d-hour")); }
  }
  const [c1, c2] = [pt(R_CYC - 10, ang(p.cutoff)), pt(R_STATE + 18, ang(p.cutoff))];
  o.push(`<line x1="${c1[0].toFixed(1)}" y1="${c1[1].toFixed(1)}" x2="${c2[0].toFixed(1)}" y2="${c2[1].toFixed(1)}" class="d-cut"/>`);
  o.push(ring(R_STAGE.W, p.lights, p.onset, "d-fall", 2));
  for (let i = 0; i < p.cycles; i++) {
    const m1 = p.onset + i * 90, c = `c${i % 6}`;
    o.push(ring(R_CYC, m1 + 1, m1 + 89, c, 13));
    const [x, y] = pt(R_CYC, ang(m1 + 45));
    o.push(txt(x, y + 3.5, "C" + (i + 1), "d-ctag"));
    const steps = PATTERN[Math.min(i, 5)].map(s => [...s]);
    if (i === p.cycles - 1) { steps[steps.length - 1][1] -= 5; steps.push(["W", 5]); }
    let m = m1, d = "";
    for (const [st, mins] of steps) {
      const r = R_STAGE[st];
      d += `${d ? "L" : "M"}${P(pt(r, ang(m)))} A${r},${r} 0 0 1 ${P(pt(r, ang(m + mins)))} `;
      m += mins;
    }
    o.push(`<path d="${d}" class="${c} d-hyp" fill="none"/>`);
  }
  // markers: now + alarm on the outer ring
  const mark = (m, cls, label) => { const [x, y] = pt(R_STATE, ang(m)); const [lx, ly] = pt(R_STATE - 26, ang(m));
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="6" class="${cls}"/>` + txt(lx, ly + 4, label, "d-mark"); };
  o.push(mark(p.nowM, "m-now", "now"));
  if (p.nap) o.push(mark(p.nap.start + p.nap.len, "m-alarm", ""));
  o.push(txt(CX - 62, CY - 2, `${p.cycles} cycles`, "d-big"));
  o.push(txt(CX - 62, CY + 16, `${dur((p.up - p.lights + 1440) % 1440)} in bed`, "d-sub"));
  o.push(txt(CX - 62, CY + 30, `${dur(p.cycles * 90)} asleep`, "d-sub"));
  return `<svg viewBox="0 0 380 380" role="img" aria-label="24 hour sleep dial">${o.join("")}</svg>`;
}
