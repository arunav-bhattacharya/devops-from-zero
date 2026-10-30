#!/usr/bin/env python3
"""Freight Notation plates: one SVG cover per course part.

Colors come only from CSS classes (the site maps them to theme tokens), so every
plate follows light and dark mode. Output: site/art/pN.svg and design/plates.html.
Usage: python3 design/covers.py
"""
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site/art"
W, H = 1200, 440
X0, Y0, X1, Y1 = 340, 78, 1140, 372  # motif field
f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")


def frame(n, noun, caption, days):
    g = []
    # surveyor's grid
    d = "".join(f"M{x} 40V400" for x in range(40, 1161, 20)) + "".join(f"M40 {y}H1160" for y in range(40, 401, 20))
    g.append(f'<rect class="cv-bg" x="20" y="20" width="1160" height="400" rx="6"/>')
    g.append(f'<path class="cv-g" d="{d}"/>')
    # crop marks
    for cx, cy, sx, sy in ((40, 40, -1, -1), (1160, 40, 1, -1), (40, 400, -1, 1), (1160, 400, 1, 1)):
        g.append(f'<path class="cv-cm" d="M{cx + sx * 4} {cy}h{sx * 12}M{cx} {cy + sy * 4}v{sy * 12}"/>')
    # outline numeral, large and quiet
    g.append(f'<text class="cv-num" x="60" y="370">{n:02d}</text>')
    g.append(f'<text class="cv-lab" x="62" y="66">PLATE {n:02d}</text>')
    g.append(f'<text class="cv-lab cv-r" x="1138" y="66">{noun.upper()}</text>')
    g.append(f'<text class="cv-cap" x="62" y="392">{caption}</text>')
    g.append(f'<text class="cv-cap cv-r" x="1138" y="392">{days}</text>')
    return g


# ---------------- motifs ----------------
def m_route(r):
    """Start: 55 stations on a boustrophedon route; part boundaries as larger rings."""
    pts, rows, per = [], 5, 11
    for i in range(55):
        row, k = divmod(i, per)
        if row % 2:
            k = per - 1 - k
        pts.append((X0 + 40 + k * 70, Y0 + 30 + row * 60))
    d = "M" + "L".join(f"{x} {y}" for x, y in pts)
    out = [f'<path class="cv-sm" d="{d}" fill="none"/>']
    starts = {1, 3, 8, 11, 17, 22, 25, 30, 39, 41, 45, 47, 50, 52, 54}
    for i, (x, y) in enumerate(pts, 1):
        if i == 1:
            out.append(f'<circle class="cv-fo" cx="{x}" cy="{y}" r="7"/>')
        elif i in starts:
            out.append(f'<circle class="cv-bgf cv-sk" cx="{x}" cy="{y}" r="6"/>')
        else:
            out.append(f'<circle class="cv-fm" cx="{x}" cy="{y}" r="2.6"/>')
    x, y = pts[-1]
    out.append(f'<circle class="cv-st" cx="{x}" cy="{y}" r="11" fill="none"/>')
    return out


def m_streams(r):
    """Linux: lines of text as dashes; a pipe column; one matching row survives the filter."""
    out, cw, rh = [], 9, 15
    match = 9
    for row in range(19):
        y = Y0 + 8 + row * rh
        x, col = X0, 0
        n = r.randint(26, 44)
        while col < n:
            ln = r.choice((1, 2, 3, 4, 6, 8))
            if col + ln > 46:
                break
            cls = "cv-fo" if row == match else "cv-fm"
            op = "" if row == match else f' opacity="{r.choice((0.35, 0.5, 0.7))}"'
            out.append(f'<rect class="{cls}" x="{x + col * cw}" y="{y}" width="{ln * cw - 3}" height="5" rx="1"{op}/>')
            col += ln + 1
    px = X0 + 47 * cw + 6
    out.append(f'<path class="cv-sk" d="M{px} {Y0}V{Y1 - 4}" stroke-width="2.4"/>')
    out.append(f'<path class="cv-sk" d="M{px + 10} {Y0}V{Y1 - 4}" stroke-width="2.4"/>')
    # output side: only the match, then counts
    y = Y0 + 8 + match * rh
    out.append(f'<rect class="cv-fo" x="{px + 34}" y="{y}" width="230" height="5" rx="1"/>')
    for k in range(4):
        out.append(f'<rect class="cv-ft" x="{px + 34}" y="{Y1 - 70 + k * 15}" width="{18 + k * 8}" height="5" rx="1" opacity="0.8"/>')
    return out


def m_cidr(r):
    """Networking: an address space subdivided like CIDR blocks; packets on two arcs."""
    out, s, ox, oy = [], 16, X0 + 10, Y0 + 6
    for i in range(16):
        for j in range(16):
            out.append(f'<rect class="cv-bx" x="{ox + j * s + 1}" y="{oy + i * s + 1}" width="{s - 3}" height="{s - 3}" rx="1.5"/>')
    blocks = [(0, 0, 8, "cv-sk"), (8, 0, 4, "cv-sm"), (12, 0, 2, "cv-sm"), (8, 4, 4, "cv-sm"), (0, 8, 8, "cv-sm"), (12, 12, 1, "cv-so")]
    for bx, by, n, cls in blocks:
        out.append(f'<rect class="{cls}" x="{ox + bx * s - 1}" y="{oy + by * s - 1}" width="{n * s + 1}" height="{n * s + 1}" fill="none" rx="2"/>')
    out.append(f'<rect class="cv-fo" x="{ox + 12 * s + 1}" y="{oy + 12 * s + 1}" width="{s - 3}" height="{s - 3}" rx="1.5"/>')
    # two hosts and packet arcs
    hx, hy = X1 - 60, Y0 + 70
    out.append(f'<rect class="cv-bgf cv-sk" x="{hx - 22}" y="{hy - 22}" width="44" height="44" rx="4"/>')
    out.append(f'<rect class="cv-bgf cv-sk" x="{hx - 22}" y="{Y1 - 92}" width="44" height="44" rx="4"/>')
    sx, sy = ox + 12 * s + 6, oy + 12 * s + 6
    for k, (tx, ty) in enumerate(((hx, hy), (hx, Y1 - 70))):
        cx, cy = (sx + tx) / 2, min(sy, ty) - 110 + k * 160
        out.append(f'<path class="{"cv-st" if k else "cv-sm"}" d="M{sx} {sy}Q{f(cx)} {f(cy)} {tx - 24} {ty}" fill="none" stroke-dasharray="2 7" stroke-linecap="round"/>')
    for t in (0.25, 0.5, 0.75):
        cx, cy = (sx + hx) / 2, min(sy, hy) - 110
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t * t * (hx - 24)
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t * t * hy
        out.append(f'<circle class="cv-fk" cx="{f(x)}" cy="{f(y)}" r="3.2"/>')
    return out


def m_stacks(r):
    """Docker: a container yard; stacked boxes with corrugation; one orange box on top."""
    out, bw, bh, gap = [], 58, 26, 8
    heights = [3, 5, 2, 6, 4, 7, 3, 5, 8, 4, 2, 6]
    for c, hgt in enumerate(heights):
        x = X0 + 6 + c * (bw + 8)
        for k in range(hgt):
            y = Y1 - 6 - (k + 1) * (bh + gap) + gap
            top = k == hgt - 1
            cls = "cv-fo" if (c == 8 and top) else ("cv-ft" if (c == 3 and k == 2) else "cv-bx2")
            out.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{bw}" height="{bh}" rx="2"/>')
            ticks = "".join(f"M{x + 6 + i * 6} {y + 5}v{bh - 10}" for i in range(9))
            out.append(f'<path class="{"cv-sbg" if cls in ("cv-fo", "cv-ft") else "cv-sm"}" d="{ticks}" opacity="0.55"/>')
    out.append(f'<path class="cv-sk" d="M{X0} {Y1 - 2}H{X1}" stroke-width="2"/>')
    return out


def m_run(r):
    """GitHub Actions: a workflow run graph with a matrix job; one step still running."""
    out = []
    cols = [1, 3, 1, 2, 1]
    names_y = {}
    xs = [X0 + 20 + i * 160 for i in range(5)]
    nodes = []
    for ci, n in enumerate(cols):
        ys = [Y0 + 145 + (k - (n - 1) / 2) * 62 for k in range(n)]
        for y in ys:
            nodes.append((ci, xs[ci], y))
        names_y[ci] = ys
    for ci in range(4):
        for ya in names_y[ci]:
            for yb in names_y[ci + 1]:
                xa, xb = xs[ci] + 120, xs[ci + 1]
                mx = (xa + xb) / 2
                out.append(f'<path class="cv-sm" d="M{xa} {f(ya)}H{f(mx)}V{f(yb)}H{xb}" fill="none"/>')
    for ci, x, y in nodes:
        out.append(f'<rect class="cv-bgf cv-sk" x="{x}" y="{f(y - 18)}" width="120" height="36" rx="18"/>')
        cls = "cv-fo" if ci == 3 and y == names_y[3][1] else ("cv-bx2" if ci == 4 else "cv-ft")
        out.append(f'<circle class="{cls}" cx="{x + 20}" cy="{f(y)}" r="7"/>')
        for k in range(3):
            out.append(f'<rect class="cv-fm" x="{x + 38}" y="{f(y - 7 + k * 6)}" width="{60 - k * 14}" height="2.4" opacity="0.6"/>')
    return out


def m_dag(r):
    """Gradle: a task graph in layers; up-to-date tasks hollow, executed ones filled."""
    out, layers = [], [3, 5, 6, 5, 3, 1]
    pos = []
    for li, n in enumerate(layers):
        x = X0 + 30 + li * 148
        pos.append([(x, Y0 + 147 + (k - (n - 1) / 2) * 50) for k in range(n)])
    rr = random.Random(7)
    edges = []
    for li in range(len(layers) - 1):
        for j, (xb, yb) in enumerate(pos[li + 1]):
            srcs = rr.sample(range(len(pos[li])), min(len(pos[li]), rr.choice((1, 2, 2, 3))))
            for s in srcs:
                edges.append((pos[li][s], (xb, yb), li))
    hot = {(0, 1), (1, 2), (2, 3), (3, 2), (4, 1), (5, 0)}
    for (xa, ya), (xb, yb), li in edges:
        mx = (xa + xb) / 2
        out.append(f'<path class="cv-sm" d="M{xa + 9} {f(ya)}C{f(mx)} {f(ya)} {f(mx)} {f(yb)} {xb - 9} {f(yb)}" fill="none" opacity="0.55"/>')
    for li, layer in enumerate(pos):
        for k, (x, y) in enumerate(layer):
            if (li, k) in hot:
                out.append(f'<circle class="cv-fo" cx="{x}" cy="{f(y)}" r="9"/>')
            elif (li + k) % 3 == 0:
                out.append(f'<circle class="cv-ft" cx="{x}" cy="{f(y)}" r="9"/>')
            else:
                out.append(f'<circle class="cv-bgf cv-sk" cx="{x}" cy="{f(y)}" r="8"/>')
    return out


def m_plan(r):
    """Terraform: a plan read as a field of marks: no change (dot), create (+), update (~), destroy (-)."""
    out, s = [], 26
    rr = random.Random(13)
    for i in range(11):
        for j in range(30):
            x, y = X0 + 10 + j * s, Y0 + 14 + i * s
            v = rr.random()
            if v < 0.84:
                out.append(f'<circle class="cv-fm" cx="{x}" cy="{y}" r="1.8" opacity="0.6"/>')
            elif v < 0.93:
                out.append(f'<path class="cv-st" d="M{x - 6} {y}h12M{x} {y - 6}v12" stroke-width="2"/>')
            elif v < 0.988:
                out.append(f'<path class="cv-sk" d="M{x - 7} {y + 1}q3.5 -6 7 0t7 0" fill="none" stroke-width="1.6"/>')
            else:
                out.append(f'<path class="cv-so" d="M{x - 7} {y}h14" stroke-width="2.6" stroke-linecap="round"/>')
    return out


def m_reconcile(r):
    """Kubernetes: seven spokes, rings of replicas; one missing, being restored."""
    out, cx, cy = [], X0 + 400, Y0 + 147
    for ring, (rad, n) in enumerate(((52, 7), (96, 14), (138, 21))):
        out.append(f'<circle class="cv-sm" cx="{cx}" cy="{cy}" r="{rad}" fill="none" opacity="0.35"/>')
        for k in range(n):
            a = -math.pi / 2 + 2 * math.pi * k / n
            x, y = cx + rad * math.cos(a), cy + rad * math.sin(a)
            if ring == 2 and k == 5:
                out.append(f'<circle class="cv-so" cx="{f(x)}" cy="{f(y)}" r="7.5" fill="none" stroke-dasharray="3 3"/>')
            else:
                out.append(f'<circle class="{"cv-ft" if ring == 0 else "cv-fk" if ring == 1 else "cv-fm"}" cx="{f(x)}" cy="{f(y)}" r="{6 if ring else 7}"/>')
    for k in range(7):
        a = -math.pi / 2 + 2 * math.pi * k / 7
        out.append(f'<path class="cv-sm" d="M{f(cx + 14 * math.cos(a))} {f(cy + 14 * math.sin(a))}L{f(cx + 40 * math.cos(a))} {f(cy + 40 * math.sin(a))}" opacity="0.6"/>')
    out.append(f'<circle class="cv-bgf cv-sk" cx="{cx}" cy="{cy}" r="10"/>')
    # control loop arc toward the missing replica
    a0, a1 = -math.pi / 2 + 2 * math.pi * 3 / 21, -math.pi / 2 + 2 * math.pi * 4.6 / 21
    R = 162
    out.append(f'<path class="cv-so" d="M{f(cx + R * math.cos(a0))} {f(cy + R * math.sin(a0))}A{R} {R} 0 0 1 {f(cx + R * math.cos(a1))} {f(cy + R * math.sin(a1))}" fill="none" stroke-width="2.2" stroke-linecap="round"/>')
    out.append(f'<circle class="cv-fo" cx="{f(cx + R * math.cos(a1))}" cy="{f(cy + R * math.sin(a1))}" r="3.6"/>')
    return out


def m_sync(r):
    """Argo CD: commits on the top lane, cluster states on the bottom; one drift pulled back."""
    out, ytop, ybot = [], Y0 + 50, Y1 - 50
    out.append(f'<path class="cv-sk" d="M{X0} {ytop}H{X1 - 20}M{X0} {ybot}H{X1 - 20}" stroke-width="1.6"/>')
    for k in range(13):
        x = X0 + 30 + k * 60
        out.append(f'<circle class="cv-bgf cv-sk" cx="{x}" cy="{ytop}" r="7"/>')
        drift = k == 8
        bx = x + (18 if drift else 0)
        out.append(f'<path class="cv-sm" d="M{x} {ytop + 9}V{ybot - 9}" opacity="{0.25 if drift else 0.5}" stroke-dasharray="{"3 5" if drift else "none"}"/>')
        out.append(f'<rect class="{"cv-fo" if drift else "cv-ft"}" x="{bx - 7}" y="{ybot - 7}" width="14" height="14" rx="2"/>')
        if drift:
            out.append(f'<path class="cv-so" d="M{bx} {ybot + 12}q-9 22 -18 4" fill="none" stroke-width="2" stroke-linecap="round"/>')
            out.append(f'<circle class="cv-fo" cx="{bx - 18}" cy="{ybot + 16}" r="3"/>')
    for k in range(40):
        x = X0 + 10 + k * 20
        out.append(f'<path class="cv-sm" d="M{x} {ybot + 34}v{4 if k % 5 else 9}" opacity="0.6"/>')
    return out


def m_counters(r):
    """Prometheus: counters as staircases sampled at scrape ticks; one rate curve."""
    out = []
    rr = random.Random(5)
    n = 40
    xs = [X0 + 10 + k * 19.5 for k in range(n)]
    for si, (base, slope, cls) in enumerate(((Y1 - 30, 4.2, "cv-sm"), (Y1 - 40, 3.0, "cv-sm"), (Y1 - 20, 6.2, "cv-sk"))):
        y, d = base, f"M{f(xs[0])} {base}"
        for k in range(1, n):
            y -= max(0, rr.gauss(slope, slope * 0.7))
            y = max(Y0 + 20, y)
            d += f"H{f(xs[k])}V{f(y)}"
        out.append(f'<path class="{cls}" d="{d}" fill="none" opacity="{0.45 if cls == "cv-sm" else 0.9}"/>')
    # rate: smooth line in teal, a spike in orange
    pts = []
    for k in range(n):
        v = 0.5 + 0.18 * math.sin(k / 3.1) + (0.42 if 26 <= k <= 28 else 0)
        pts.append((xs[k], Y0 + 230 - v * 120))
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)
    out.append(f'<path class="cv-st" d="{d}" fill="none" stroke-width="2"/>')
    for k in (26, 27, 28):
        out.append(f'<circle class="cv-fo" cx="{f(pts[k][0])}" cy="{f(pts[k][1])}" r="4"/>')
    for x in xs:
        out.append(f'<path class="cv-sm" d="M{f(x)} {Y1 + 2}v6" opacity="0.7"/>')
    return out


def m_panels(r):
    """Grafana: a dashboard of panels; heatmap, sparklines, stat bars; one alerting panel."""
    out = []
    rr = random.Random(11)
    panels = [(0, 0, 3, 2, "heat"), (3, 0, 2, 1, "spark"), (5, 0, 1, 1, "stat"), (3, 1, 2, 1, "spark"), (5, 1, 1, 1, "alert"),
              (0, 2, 2, 1, "bars"), (2, 2, 2, 1, "spark"), (4, 2, 2, 1, "bars")]
    cw, ch, g = 130, 92, 8
    for px, py, pw, ph, kind in panels:
        x, y, w, h = X0 + px * (cw + g), Y0 + py * (ch + g), pw * cw + (pw - 1) * g, ph * ch + (ph - 1) * g
        out.append(f'<rect class="cv-bgf cv-sm" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>')
        out.append(f'<rect class="cv-fm" x="{x + 10}" y="{y + 10}" width="{min(70, w - 20)}" height="3" opacity="0.5"/>')
        if kind == "heat":
            for i in range(9):
                for j in range(19):
                    v = max(0.06, min(1, rr.random() * (1 - abs(i - 4) / 6) * 1.3))
                    out.append(f'<rect class="cv-ft" x="{x + 12 + j * 20.5}" y="{y + 26 + i * 18}" width="18" height="15" rx="1.5" opacity="{v:.2f}"/>')
        elif kind == "spark":
            d = "M" + "L".join(f"{f(x + 12 + k * (w - 24) / 24)} {f(y + h - 18 - (0.5 + 0.35 * math.sin(k / 2.2 + px)) * (h - 44))}" for k in range(25))
            out.append(f'<path class="cv-sk" d="{d}" fill="none" stroke-width="1.6"/>')
        elif kind == "stat":
            out.append(f'<rect class="cv-ft" x="{x + 12}" y="{y + 36}" width="{w - 24}" height="34" rx="3"/>')
        elif kind == "alert":
            out.append(f'<rect class="cv-fo" x="{x + 12}" y="{y + 36}" width="{w - 24}" height="34" rx="3"/>')
        elif kind == "bars":
            for k in range(14):
                bh = 10 + rr.random() * (h - 44)
                out.append(f'<rect class="cv-fm" x="{x + 12 + k * (w - 24) / 14}" y="{f(y + h - 10 - bh)}" width="{f((w - 24) / 14 - 4)}" height="{f(bh)}" rx="1" opacity="0.55"/>')
    return out


def m_waterfall(r):
    """Logs and traces: a trace waterfall over faint log lines; the slow span in orange."""
    out = []
    rr = random.Random(3)
    for row in range(19):
        y = Y0 + 4 + row * 15.5
        x = X0
        while x < X1 - 40:
            ln = rr.choice((20, 34, 50, 70, 12))
            out.append(f'<rect class="cv-fm" x="{x}" y="{f(y)}" width="{ln}" height="3" opacity="0.18"/>')
            x += ln + 8
    spans = [(0, 0, 760), (1, 20, 210), (2, 40, 90), (2, 140, 70), (1, 240, 470), (2, 262, 120), (3, 280, 70), (2, 396, 300), (3, 410, 260), (1, 720, 30)]
    for k, (depth, start, length) in enumerate(spans):
        y = Y0 + 18 + k * 28
        x = X0 + 20 + start
        cls = "cv-fo" if k == 8 else ("cv-ft" if depth == 0 else "cv-bx2")
        out.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{length}" height="14" rx="2"/>')
        out.append(f'<path class="cv-sm" d="M{X0 + 6 + depth * 12} {y + 7}h6" opacity="0.8"/>')
    return out


def m_topology(r):
    """Dynatrace: services over processes over hosts; a root-cause path highlighted."""
    out = []
    lanes = [(Y0 + 30, 6, "svc"), (Y0 + 140, 8, "proc"), (Y0 + 250, 5, "host")]
    pos = {}
    for li, (y, n, kind) in enumerate(lanes):
        span = X1 - X0 - 80
        for k in range(n):
            pos[(li, k)] = (X0 + 40 + k * span / (n - 1), y)
    rr = random.Random(21)
    edges = []
    for k in range(6):
        for t in rr.sample(range(8), 2):
            edges.append(((0, k), (1, t)))
    for k in range(8):
        edges.append(((1, k), (2, min(4, k * 5 // 8))))
    path = {((0, 2), (1, 3)), ((1, 3), (2, 1))}
    edges += list(path)
    for a, b in edges:
        (xa, ya), (xb, yb) = pos[a], pos[b]
        hot = (a, b) in path
        out.append(f'<path class="{"cv-so" if hot else "cv-sm"}" d="M{f(xa)} {f(ya)}L{f(xb)} {f(yb)}" opacity="{1 if hot else 0.35}" stroke-width="{2.4 if hot else 1}"/>')
    for (li, k), (x, y) in pos.items():
        hot = (li, k) in ((0, 2), (1, 3), (2, 1))
        if li == 0:
            out.append(f'<path class="{"cv-fo" if hot else "cv-bgf cv-sk"}" d="M{f(x)} {f(y - 12)}l12 12l-12 12l-12 -12z"/>')
        elif li == 1:
            out.append(f'<circle class="{"cv-fo" if hot else "cv-bgf cv-sk"}" cx="{f(x)}" cy="{f(y)}" r="9"/>')
        else:
            out.append(f'<rect class="{"cv-fo" if hot else "cv-ft"}" x="{f(x - 14)}" y="{f(y - 10)}" width="28" height="20" rx="2"/>')
    return out


def m_seal(r):
    """DevSecOps: a guilloche-like seal of ticks; a short chain of custody; a hazard band."""
    out, cx, cy = [], X0 + 210, Y0 + 147
    for ring, (rad, n, ln) in enumerate(((130, 120, 10), (112, 90, 7), (95, 72, 5), (78, 48, 4))):
        for k in range(n):
            a = 2 * math.pi * k / n + ring * 0.03
            x1, y1 = cx + rad * math.cos(a), cy + rad * math.sin(a)
            x2, y2 = cx + (rad - ln) * math.cos(a), cy + (rad - ln) * math.sin(a)
            out.append(f'<path class="{"cv-sk" if ring == 0 else "cv-sm"}" d="M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}" opacity="{0.9 if ring == 0 else 0.5}"/>')
    out.append(f'<circle class="cv-st" cx="{cx}" cy="{cy}" r="56" fill="none" stroke-width="2"/>')
    out.append(f'<path class="cv-st" d="M{cx - 20} {cy + 2}l13 13l27 -29" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    # chain of custody
    for k in range(6):
        x = X0 + 420 + k * 64
        out.append(f'<rect class="{"cv-fo" if k == 5 else "cv-bgf cv-sk"}" x="{x}" y="{cy - 14}" width="40" height="28" rx="14"/>')
        if k < 5:
            out.append(f'<path class="cv-sm" d="M{x + 40} {cy}h24"/>')
    # hazard band
    hb = "".join(f'<path class="cv-fy" d="M{X0 + 420 + i * 16} {Y1 - 30}h8l-8 14h-8z"/>' for i in range(24))
    out.append(hb)
    return out


def m_converge(r):
    """Capstone: fourteen small emblems around one central container."""
    out, cx, cy, R = [], X0 + 400, Y0 + 147, 128
    for k in range(14):
        a = -math.pi / 2 + 2 * math.pi * k / 14
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        out.append(f'<path class="cv-sm" d="M{f(cx + 44 * math.cos(a))} {f(cy + 44 * math.sin(a))}L{f(x - 16 * math.cos(a))} {f(y - 16 * math.sin(a))}" opacity="0.45"/>')
        shape = k % 4
        if shape == 0:
            out.append(f'<circle class="cv-bgf cv-sk" cx="{f(x)}" cy="{f(y)}" r="11"/>')
        elif shape == 1:
            out.append(f'<rect class="cv-bgf cv-sk" x="{f(x - 11)}" y="{f(y - 11)}" width="22" height="22" rx="3"/>')
        elif shape == 2:
            out.append(f'<path class="cv-bgf cv-sk" d="M{f(x)} {f(y - 13)}l13 13l-13 13l-13 -13z"/>')
        else:
            out.append(f'<circle class="cv-ft" cx="{f(x)}" cy="{f(y)}" r="9"/>')
    out.append(f'<circle class="cv-sm" cx="{cx}" cy="{cy}" r="{R}" fill="none" opacity="0.3"/>')
    out.append(f'<rect class="cv-fo" x="{cx - 40}" y="{cy - 22}" width="80" height="44" rx="3"/>')
    ticks = "".join(f"M{cx - 32 + i * 8} {cy - 14}v28" for i in range(9))
    out.append(f'<path class="cv-sbg" d="{ticks}" opacity="0.6"/>')
    return out


PLATES = [
    (0, "start", "route survey of a learning path", m_route),
    (1, "linux", "one line survives the filter", m_streams),
    (2, "networking", "an address space, subdivided", m_cidr),
    (3, "docker", "stacked layers in the yard", m_stacks),
    (4, "actions", "a run with one step in progress", m_run),
    (5, "gradle", "the task graph, mostly up to date", m_dag),
    (6, "terraform", "a plan read as a field of marks", m_plan),
    (7, "kubernetes", "the loop restores what went missing", m_reconcile),
    (8, "argo cd", "drift pulled back to what git says", m_sync),
    (9, "prometheus", "counters, sampled; a rate that spikes", m_counters),
    (10, "grafana", "one panel turns", m_panels),
    (11, "logs and traces", "the slow span", m_waterfall),
    (12, "dynatrace", "a root cause, traced through layers", m_topology),
    (13, "devsecops", "sealed, with a chain of custody", m_seal),
    (14, "capstone", "every part, converging", m_converge),
]


def plate(n, noun, caption, fn, days):
    body = frame(n, noun, caption, days) + fn(random.Random(n))
    return (f'<svg class="cv" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Plate {n}: {noun}">'
            + "".join(body) + "</svg>")


def main():
    import json
    idx = json.loads((ROOT / "brief/index.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    svgs = []
    for (n, noun, cap, fn), P in zip(PLATES, idx):
        days = [int(L["id"][1:]) for L in P["lessons"]]
        rng = f"DAY {days[0]:02d}" if len(days) == 1 else f"DAYS {days[0]:02d} TO {days[-1]:02d}"
        svg = plate(n, noun, cap, fn, rng)
        (OUT / f"p{n}.svg").write_text(svg)
        svgs.append(svg)
    css = (ROOT / "site/art.css").read_text()
    fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Stencil+Display:wght@700&family=Atkinson+Hyperlegible+Mono:wght@400&display=swap">'
    page = (f'<!doctype html><meta charset="utf-8">{fonts}<style>:root{{--bg:#edf0f3;--panel:#ffffff;--panel-2:#e2e7ec;--ink:#132130;--mute:#485766;--faint:#6f7d8b;--rule:#cdd5dd;--orange:#c84410;--teal:#0a6a7e;--yellow:#e8ad00;'
            '--f-stencil:"Big Shoulders Stencil Display",sans-serif;--f-mono:"Atkinson Hyperlegible Mono",monospace}'
            '.dark{--bg:#0c131a;--panel:#131d27;--panel-2:#1a2633;--ink:#e1e8ee;--mute:#a5b2be;--faint:#75838f;--rule:#253341;--orange:#ff7d3f;--teal:#4fbad1;--yellow:#f3c341}'
            f'body{{margin:0;background:var(--bg)}}.sheet{{display:grid;grid-template-columns:1fr 1fr;gap:28px;padding:40px;width:2400px;background:var(--bg)}}{css}</style>'
            '<svg width="0" height="0" style="position:absolute"><defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="arh"/></marker></defs></svg>'
            f'<div class="sheet" id="light">{"".join(svgs)}</div><div class="sheet dark" id="dark">{"".join(svgs)}</div>')
    (ROOT / "design/plates.html").write_text(page)
    print("wrote", len(svgs), "plates;", sum(len(s) for s in svgs) // 1024, "KB total")


if __name__ == "__main__":
    main()
