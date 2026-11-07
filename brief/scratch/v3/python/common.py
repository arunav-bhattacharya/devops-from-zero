"""Shared helpers for the Part 4 build: read lab files, build small SVG diagrams."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs" / "python-ops"


def lab(rel: str) -> str:
    """The exact text of a lab file, without the final newline."""
    return (LAB / rel).read_text(encoding="utf-8").rstrip("\n")


def svg_box(cls: str, x: int, y: int, w: int, h: int, label: str) -> str:
    text_cls = "t" if cls == "bx" else "tk"
    cx, cy = x + w // 2, y + h // 2 + 5
    return (
        f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
        f'<text class="{text_cls}" x="{cx}" y="{cy}" font-size="13" text-anchor="middle">{label}</text>'
    )


def svg_line(x1, y1, x2, y2, dashed=False) -> str:
    cls = "lnd" if dashed else "ln"
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ar)"/>'


def svg_text(cls: str, x: int, y: int, label: str) -> str:
    size = 11 if cls == "ts" else 13
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{label}</text>'


def svg(height: int, aria: str, parts: list[str]) -> str:
    return (
        f'<svg viewBox="0 0 560 {height}" xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{aria}">' + "".join(parts) + "</svg>"
    )
