"""nap_graph.py: /nap timeline -> 24h dial SVG (phone, 380 wide).

Usage: python nap_graph.py "13:00 nap 25" "15:00 cutoff" "21:45 lights" "07:00 up 6" > nap.svg
   or: pipe the /nap code block in (lines like "07:15  lie down", "07:40  alarm, 25 min").
Dial: 00 at top, clockwise. Outer ring = awake/nap/asleep, middle ring = cycles C1..Cn,
inside = polar hypnogram (farther out = lighter sleep). Exact times listed under the dial.
"""
import math, re, sys

BG, INK, DIM, GRID = "#161616", "#ECEAE4", "#9A988F", "#2C2C2A"
AWAKE, NAP, SLEEP, CUT = "#B5B2A8", "#1FA37C", "#7F74DE", "#E8683A"
CYC = ["#8B80E8", "#1FA37C", "#E8683A", "#E0558A", "#3B8FE0", "#D88A1E"]
CX, CY = 190, 214
R_STATE, R_CYC = 140, 118
R_STAGE = {"W": 104, "R": 88, "N1": 72, "N2": 56, "N3": 40}
# minutes per stage in each 90 min cycle: deep sleep early, REM longer later
PATTERN = [
    [("N1", 5), ("N2", 20), ("N3", 45), ("N2", 10), ("R", 10)],
    [("N1", 5), ("N2", 25), ("N3", 30), ("N2", 10), ("R", 20)],
    [("N1", 5), ("N2", 30), ("N3", 15), ("N2", 15), ("R", 25)],
    [("N1", 5), ("N2", 55), ("R", 30)],
    [("N1", 5), ("N2", 45), ("R", 40)],
    [("N1", 5), ("N2", 40), ("R", 45)],
]


def hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def fmt(m):
    m %= 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def dur(m):
    return f"{m // 60}h{m % 60:02d}" if m >= 60 else f"{m} min"


def parse(lines):
    p = {"nap": None, "nap_len": None, "cut": None, "lights": None, "up": None, "cycles": None}
    for raw in lines:
        t = re.match(r"\s*(\d{1,2}:\d{2})\s+(.*)", raw)
        if not t:
            continue
        m, rest = hm(t.group(1)), t.group(2).lower()
        num = re.search(r"(\d+)", rest)
        n = int(num.group(1)) if num else None
        if "lie down" in rest:
            p["nap"] = m
        elif "alarm" in rest:
            if p["nap"] is not None:
                p["nap_len"] = (m - p["nap"]) % 1440
            elif n:
                p["nap"], p["nap_len"] = m - n, n
        elif "no nap" in rest or "cutoff" in rest:
            p["cut"] = m
        elif "nap" in rest:
            p["nap"], p["nap_len"] = m, n or 25
        elif "light" in rest or "bed" in rest:
            p["lights"] = m
        elif re.search(r"\bup\b|wake", rest):
            p["up"], p["cycles"] = m, n
    if p["lights"] is None or p["up"] is None:
        sys.exit("need at least a lights-out line and an up line")
    if p["nap"] is not None and p["nap_len"] is None:
        p["nap_len"] = 25
    if p["cycles"] is None:
        p["cycles"] = max(1, ((p["up"] - p["lights"]) % 1440 - 15) // 90)
    return p


SPLIT = {"lights": 0, "up": 0}  # set in build(): night = right half, day = left half


def ang(m):
    """Minute of day -> degrees (0 = top, clockwise). Night lights..up fills 0-180, day fills 180-360."""
    lo, up = SPLIT["lights"], SPLIT["up"]
    night = (up - lo) % 1440
    off = (m - lo) % 1440
    if off <= night:
        return off / night * 180
    return 180 + (off - night) / (1440 - night) * 180


def pt(r, m, a=None):
    a = math.radians(ang(m) if a is None else a)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def arc(r, m1, m2):
    """Path along radius r from minute m1 to m2 (clockwise, inside one half)."""
    a1 = ang(m1)
    a2 = a1 + ((ang(m2) - a1) % 360 or 359.9)
    (x1, y1), (x2, y2) = pt(r, 0, a1), pt(r, 0, a2)
    return f"M{x1:.1f},{y1:.1f} A{r},{r} 0 {1 if a2 - a1 > 180 else 0} 1 {x2:.1f},{y2:.1f}"


def ring(r, m1, m2, color, w, extra=""):
    return f'<path d="{arc(r, m1, m2)}" stroke="{color}" stroke-width="{w}" fill="none"{extra}/>'


def hypno(onset, i, last):
    """Polar stepped hypnogram for cycle i starting at onset (minutes)."""
    steps = list(PATTERN[min(i, len(PATTERN) - 1)])
    if last:  # end the night with a short wake
        s, d = steps[-1]
        steps[-1] = (s, d - 5)
        steps.append(("W", 5))
    m, d_parts, prev = onset, [], None
    for stage, mins in steps:
        r = R_STAGE[stage]
        x, y = pt(r, m)
        d_parts.append(f"{'M' if prev is None else 'L'}{x:.1f},{y:.1f}")
        x2, y2 = pt(r, m + mins)
        d_parts.append(f"A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}")
        m, prev = m + mins, r
    return " ".join(d_parts)


def build(p):
    lights, up, n = p["lights"], p["up"], p["cycles"]
    onset = up - n * 90
    SPLIT.update(lights=lights, up=up)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 560" font-family="system-ui,Segoe UI,sans-serif">',
           f'<rect width="380" height="560" rx="16" fill="{BG}"/>',
           f'<text x="20" y="34" fill="{INK}" font-size="18" font-weight="600">Today → tomorrow</text>',
           f'<text x="360" y="34" fill="{DIM}" font-size="12" text-anchor="end">night right · day left</text>']
    # stage guide circles + labels (left side, in the awake part of the night)
    for s, r in R_STAGE.items():
        out.append(f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{GRID}" stroke-width="1"/>')
    for s, r in R_STAGE.items():
        name = {"W": "Awake", "R": "REM"}.get(s, s)
        x, y = pt(r, p["lights"] - 18)
        out.append(f'<text x="{x:.1f}" y="{y + 3:.1f}" fill="{DIM}" font-size="8" text-anchor="middle">{name}</text>')
    # outer state ring: awake, then asleep, then nap on top
    out.append(ring(R_STATE, up, lights, AWAKE, 16))
    out.append(ring(R_STATE, lights, up, SLEEP, 16))
    if p["nap"] is not None:
        out.append(ring(R_STATE, p["nap"], p["nap"] + max(p["nap_len"], 8), NAP, 22))
    # hour ticks + numbers
    for h in range(24):
        m = h * 60
        a, b = pt(R_STATE + 11, m), pt(R_STATE + (17 if h % 3 == 0 else 14), m)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{DIM}" stroke-width="1"/>')
        if h % 3 == 0:
            x, y = pt(R_STATE + 28, m)
            out.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" fill="{DIM}" font-size="11" text-anchor="middle">{h:02d}</text>')
    # 15:00-style cutoff spoke
    if p["cut"] is not None:
        a, b = pt(R_CYC - 10, p["cut"]), pt(R_STATE + 18, p["cut"])
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{CUT}" stroke-width="2" stroke-dasharray="4 3"/>')
    # falling asleep gap, cycles ring + polar hypnogram
    out.append(ring(R_STAGE["W"], lights, onset, DIM, 2, ' stroke-dasharray="2 3"'))
    for i in range(n):
        c, m1 = CYC[i % len(CYC)], onset + i * 90
        out.append(ring(R_CYC, m1 + 1, m1 + 89, c, 12))
        x, y = pt(R_CYC, m1 + 45)
        out.append(f'<text x="{x:.1f}" y="{y + 3:.1f}" fill="{BG}" font-size="9" font-weight="700" text-anchor="middle">C{i + 1}</text>')
        out.append(f'<path d="{hypno(m1, i, i == n - 1)}" stroke="{c}" stroke-width="2.2" fill="none" stroke-linejoin="round"/>')
    # center summary
    bed = (up - lights) % 1440
    out += [f'<text x="{CX - 56}" y="{CY + 2}" fill="{INK}" font-size="22" font-weight="700" text-anchor="middle">{n} cycles</text>',
            f'<text x="{CX - 56}" y="{CY + 18}" fill="{DIM}" font-size="10" text-anchor="middle">{dur(bed)} in bed</text>',
            f'<text x="{CX - 56}" y="{CY + 31}" fill="{DIM}" font-size="10" text-anchor="middle">{dur(n * 90)} asleep</text>']
    # exact-time list
    rows = []
    if p["nap"] is not None:
        rows.append((NAP, fmt(p["nap"]) + "–" + fmt(p["nap"] + p["nap_len"]), f"nap, {p['nap_len']} min"))
    if p["cut"] is not None:
        rows.append((CUT, fmt(p["cut"]), "no naps after"))
    rows.append((DIM, fmt(lights), f"lights out, asleep ~{fmt(onset)}"))
    rows.append((SLEEP, fmt(onset) + "–" + fmt(up), " ".join(f"C{i + 1} {fmt(onset + i * 90 + 90)}" for i in range(min(n, 3)))))
    if n > 3:
        rows.append((SLEEP, "", " ".join(f"C{i + 1} {fmt(onset + i * 90 + 90)}" for i in range(3, n))))
    rows.append((AWAKE, fmt(up), f"up, {n} full cycles"))
    y = 412
    for col, t, what in rows:
        out.append(f'<circle cx="26" cy="{y - 4}" r="5" fill="{col}"/>' if t else "")
        out.append(f'<text x="40" y="{y}" fill="{INK}" font-size="13" font-weight="600">{t}</text>')
        out.append(f'<text x="138" y="{y}" fill="{DIM}" font-size="13">{what}</text>')
        y += 22
    out.append("</svg>")
    return "\n".join(s for s in out if s)


if __name__ == "__main__":
    args = sys.argv[1:]
    lines = args if args else sys.stdin.read().splitlines()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(build(parse(lines)) + "\n")
