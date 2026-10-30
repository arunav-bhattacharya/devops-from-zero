"""Shared helpers for building content/p5.json (Part 5: Builds with Gradle)."""
import pathlib

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-jvm")
HERE = pathlib.Path(__file__).resolve().parent
D22 = HERE / "d22"
DEMO = HERE / "lifecycle-demo"


def lab(path):
    """Return a lab file's text without the trailing newline."""
    return (LAB / path).read_text().rstrip("\n")


def d22(path):
    return (D22 / path).read_text().rstrip("\n")


def demo(path):
    return (DEMO / path).read_text().rstrip("\n")


def svg(h, label, body):
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{label}">{body}</svg>')


def box(x, y, w, h, cls, text, size=13):
    tcls = "t" if cls == "bx" else "tk"
    cx = x + w / 2
    cy = y + h / 2 + 4.5
    return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<text class="{tcls}" x="{cx:g}" y="{cy:g}" font-size="{size}" text-anchor="middle">{text}</text>')


def arrow(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ar)"/>'


def line(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def cap(x, y, text, anchor="middle", cls="ts", size=11):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{text}</text>'
