"""Tiny helpers to draw lesson diagrams with the page's CSS classes only (Parts 13 and 14)."""

COLORED = {"bxo", "bxt", "bxg", "bxp"}


def svg(h, label, parts):
    assert 140 <= h <= 380
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{label}">{"".join(parts)}</svg>')


def box(x, y, w, h, cls, label):
    need = 8 * len(label) + 24
    assert w >= need, f"box {label!r} too narrow: {w} < {need}"
    assert x >= 8 and x + w <= 552, f"box {label!r} leaves the edge"
    tcls = "tk" if cls in COLORED else "t"
    cx, cy = x + w / 2, y + h / 2 + 5
    return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<text class="{tcls}" x="{cx:g}" y="{cy:g}" font-size="13" text-anchor="middle">{label}</text>')


def arrow(x1, y1, x2, y2, dashed=False, head=True):
    cls = "lnd" if dashed else "ln"
    end = ' marker-end="url(#ar)"' if head else ""
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{end}/>'


def note(x, y, text, anchor="middle"):
    return f'<text class="ts" x="{x}" y="{y}" font-size="11" text-anchor="{anchor}">{text}</text>'


def label(x, y, text, anchor="middle"):
    return f'<text class="t" x="{x}" y="{y}" font-size="13" text-anchor="{anchor}">{text}</text>'
