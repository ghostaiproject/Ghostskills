// calc.js: /nap rules (same as the nap skill). Minutes since local midnight unless noted.
const CUTOFF = 15 * 60;
const pad = n => String(n).padStart(2, "0");
const fmt = m => { m = ((Math.round(m) % 1440) + 1440) % 1440; return pad(Math.floor(m / 60)) + ":" + pad(m % 60); };
const hm = s => { const [h, m] = s.split(":").map(Number); return h * 60 + m; };
const dur = m => m >= 60 ? `${Math.floor(m / 60)}h ${pad(m % 60)}m` : `${m} min`;

// input: {wokeDay:0|1|2, wokeAt:"HH:MM", bed:"HH:MM", wake:"HH:MM"|"", tired:"fine"|"tired"|"wrecked"}, now: Date
function planNap(inp, now) {
  const nowM = now.getHours() * 60 + now.getMinutes() + now.getSeconds() / 60;
  const awake = Math.max(0, Math.round(inp.wokeDay * 1440 + nowM - hm(inp.wokeAt)));
  const lie = Math.ceil((nowM + 5) / 5) * 5;
  let nap = null, backup = null;
  if (lie + 25 <= CUTOFF) {
    const big = inp.tired === "wrecked" && lie + 90 <= CUTOFF;
    nap = { start: lie, len: big ? 90 : 25 };
    if (!big && lie + 90 <= CUTOFF) backup = { start: lie, len: 90 };
  }
  const bed = hm(inp.bed || "22:00");
  let lights, up, cycles, options = null;
  if (inp.wake) {
    up = hm(inp.wake);
    const pick = [5, 6].map(n => ({ n, lights: up - n * 90 - 15 }));
    // distance on the clock between candidate lights-out and the wanted bedtime
    pick.forEach(o => { const d = ((o.lights - bed) % 1440 + 1440) % 1440; o.diff = Math.min(d, 1440 - d); });
    pick.sort((a, b) => a.diff - b.diff || b.n - a.n);
    ({ n: cycles, lights } = pick[0]);
  } else {
    lights = bed; cycles = 6; up = bed + 15 + 6 * 90;
    options = [5, 6].map(n => ({ n, up: fmt(bed + 15 + n * 90) }));
  }
  lights = ((lights % 1440) + 1440) % 1440; up = ((up % 1440) + 1440) % 1440;
  return {
    nowM, awake, lie, nap, backup, cutoff: CUTOFF, lights, up, cycles, options,
    onset: up - cycles * 90, longAwake: awake >= 30 * 60,
  };
}
