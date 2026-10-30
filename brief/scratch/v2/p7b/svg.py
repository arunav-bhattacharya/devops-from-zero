"""Small helpers for the lesson diagrams. They check box widths against the brief's rule."""


def box(x, y, w, h, cls, label, sub=None):
    tcls = "t" if cls == "bx" else "tk"
    assert w >= 8 * len(label) + 24, (label, w)
    out = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
    ty = y + h / 2 + 5 if sub is None else y + h / 2 - 3
    out += f'<text class="{tcls}" x="{x + w / 2:g}" y="{ty:g}" font-size="13" text-anchor="middle">{label}</text>'
    if sub:
        assert w >= 6.5 * len(sub) + 16, (sub, w)
        out += f'<text class="ts" x="{x + w / 2:g}" y="{y + h / 2 + 13:g}" font-size="11" text-anchor="middle">{sub}</text>'
    return out


def arrow(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ar)"/>'


def cap(x, y, s):
    return f'<text class="ts" x="{x}" y="{y}" font-size="11" text-anchor="middle">{s}</text>'


def svg(h, label, parts):
    assert 140 <= h <= 380
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            + "".join(parts) + "</svg>")
