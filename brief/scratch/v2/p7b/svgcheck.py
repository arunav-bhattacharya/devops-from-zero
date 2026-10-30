"""Rough overlap check for the lesson diagrams (text width estimated from font size)."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
L = json.loads((ROOT / "content/parts/p7b.json").read_text())


def parse(svg):
    rects = [tuple(float(x) for x in m) for m in re.findall(r'<rect class="\w+" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)]
    texts = []
    for m in re.finditer(r'<text class="(\w+)" x="([\d.]+)" y="([\d.]+)" font-size="(\d+)" text-anchor="middle">([^<]*)</text>', svg):
        _, x, y, fs, t = m.groups()
        x, y, fs = float(x), float(y), int(fs)
        w = len(t) * fs * 0.55
        texts.append((x - w / 2, y - fs * 0.8, w, fs, t))
    lines = [tuple(float(v) for v in m) for m in re.findall(r'<line class="\w+" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg)]
    return rects, texts, lines


def inter(a, b):
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


def inside(t, r):
    return t[0] >= r[0] - 1 and t[1] >= r[1] - 1 and t[0] + t[2] <= r[0] + r[2] + 1 and t[1] + t[3] <= r[1] + r[3] + 1


def hits(line, b, lo=0, hi=101, pad=0):
    x1, y1, x2, y2 = line
    for i in range(lo, hi):
        x, y = x1 + (x2 - x1) * i / 100, y1 + (y2 - y1) * i / 100
        if b[0] + pad < x < b[0] + b[2] - pad and b[1] + pad < y < b[1] + b[3] - pad:
            return True
    return False


for les in L:
    svg = les["diagram"]
    H = int(re.search(r"0 0 560 (\d+)", svg).group(1))
    rects, texts, lines = parse(svg)
    probs = []
    for i, a in enumerate(rects):
        if a[0] < 8 or a[1] < 8 or a[0] + a[2] > 552 or a[1] + a[3] > H - 8:
            probs.append(("rect edge", a))
        probs += [("rect overlap", a, b) for b in rects[i + 1:] if inter(a, b)]
    for i, t in enumerate(texts):
        if t[0] < 4 or t[0] + t[2] > 556 or t[1] + t[3] > H:
            probs.append(("text edge", t[4]))
        own = [r for r in rects if inside(t, r)]
        probs += [("text over rect", t[4], r) for r in rects if r not in own and inter(t[:4], r)]
        probs += [("text overlap", t[4], u[4]) for u in texts[i + 1:] if inter(t[:4], u[:4])]
        if not own:
            probs += [("line through text", t[4], ln) for ln in lines if hits(ln, t[:4])]
    for ln in lines:
        probs += [("line through rect", ln, r) for r in rects if hits(ln, r, 5, 96, 2)]
    print(les["id"], "H", H, "problems:", probs or "none")
