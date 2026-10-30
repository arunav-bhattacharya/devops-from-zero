"""Rough layout checks: text boxes vs rects and other text, lines vs rects, viewBox bounds."""
import re, sys
def parse(s):
    H = int(re.search(r'viewBox="0 0 560 (\d+)"', s).group(1))
    rects = [tuple(float(v) for v in m) for m in re.findall(r'<rect class="[^"]+" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', s)]
    texts = []
    for m in re.finditer(r'<text class="(\w+)" x="([\d.]+)" y="([\d.]+)" font-size="(\d+)" text-anchor="(\w+)">([^<]*)</text>', s):
        cls, x, y, fs, anc, t = m.groups(); x, y, fs = float(x), float(y), float(fs)
        w = len(t) * fs * (0.62 if cls in ("t", "tk") else 0.58)
        x0 = x - w / 2 if anc == "middle" else (x - w if anc == "end" else x)
        texts.append((x0, y - fs * 0.8, w, fs, t))
    lines = [tuple(float(v) for v in m) for m in re.findall(r'<line class="\w+" x1="([\d.-]+)" y1="([\d.-]+)" x2="([\d.-]+)" y2="([\d.-]+)"', s)]
    return H, rects, texts, lines
def ov(a, b, pad=0):
    return a[0] < b[0] + b[2] + pad and b[0] < a[0] + a[2] + pad and a[1] < b[1] + b[3] + pad and b[1] < a[1] + a[3] + pad
def inside(t, r):
    return t[0] >= r[0] and t[0] + t[2] <= r[0] + r[2] and t[1] >= r[1] and t[1] + t[3] <= r[1] + r[3]
def check(name, s):
    H, rects, texts, lines = parse(s); bad = []
    for t in texts:
        if t[0] < 8 or t[0] + t[2] > 552 or t[1] < 0 or t[1] + t[3] > H - 4: bad.append(f"text out of bounds: {t[4]!r}")
        owners = [r for r in rects if inside(t, r)]
        for r in rects:
            if r not in owners and ov(t, r): bad.append(f"text {t[4]!r} overlaps rect at {r[:2]}")
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            if ov(a, b): bad.append(f"text {a[4]!r} overlaps text {b[4]!r}")
    for r in rects:
        if r[1] + r[3] > H - 8: bad.append(f"rect at {r[:2]} too close to bottom")
    for (x1, y1, x2, y2) in lines:
        for k in range(1, 20):
            px, py = x1 + (x2 - x1) * k / 20, y1 + (y2 - y1) * k / 20
            for t in texts:
                if t[0] <= px <= t[0] + t[2] and t[1] <= py <= t[1] + t[3]: bad.append(f"line crosses text {t[4]!r}"); break
            for r in rects:
                if r[0] + 2 < px < r[0] + r[2] - 2 and r[1] + 2 < py < r[1] + r[3] - 2: bad.append(f"line {x1,y1,x2,y2} crosses rect {r[:2]}"); break
    print(name, "OK" if not bad else "\n  " + "\n  ".join(sorted(set(bad))))
if __name__ == "__main__":
    import svg
    for n in ("d47", "d48", "d49"): check(n, getattr(svg, n)())
