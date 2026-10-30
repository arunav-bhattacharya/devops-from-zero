"""Tiny helpers that build the lesson diagrams and check box widths."""


def box(x, y, w, h, cls, label, sub=None):
    tcls = "t" if cls == "bx" else "tk"
    assert w >= 8 * len(label) + 24, (label, w)
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>'
    ty = y + h / 2 + 5 if sub is None else y + h / 2 - 2
    out += f'<text x="{x + w / 2:g}" y="{ty:g}" font-size="13" text-anchor="middle" class="{tcls}">{label}</text>'
    if sub:
        out += f'<text x="{x + w / 2:g}" y="{y + h / 2 + 13:g}" font-size="11" text-anchor="middle" class="ts">{sub}</text>'
    return out


def arrow(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" marker-end="url(#ar)"/>'


def cap(x, y, s):
    return f'<text x="{x}" y="{y}" font-size="11" text-anchor="middle" class="ts">{s}</text>'


def svg(h, label, parts):
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            + "".join(parts) + "</svg>")


def d13():
    y, h = 40, 44
    p = [
        box(8, y, 92, h, "bx", "main.tf"),
        box(120, y, 92, h, "bxo", "plan"),
        box(232, y, 92, h, "bxt", "apply"),
        box(344, y, 92, h, "bxp", "provider"),
        box(456, y, 96, h, "bxg", "Docker"),
        arrow(102, 62, 118, 62), arrow(214, 62, 230, 62), arrow(326, 62, 342, 62), arrow(438, 62, 454, 62),
        cap(504, 104, "real world"),
        box(168, 150, 116, h, "bx", "state file"),
        arrow(196, 148, 172, 90, dashed=True), cap(150, 124, "reads"),
        arrow(280, 88, 262, 146, dashed=True), cap(306, 124, "writes"),
        cap(280, 222, "plan compares code, state and reality; apply makes them match"),
    ]
    return svg(234, "Terraform reads main.tf, plans against the state file, and applies through a provider to Docker", p)


def d14():
    h = 44
    p = [
        box(8, 30, 120, h, "bx", "variables"),
        box(215, 30, 130, h, "bxo", "root module"),
        box(432, 30, 120, h, "bx", "outputs"),
        arrow(130, 52, 211, 52), cap(171, 44, "tfvars, -var"),
        arrow(347, 52, 428, 52), cap(389, 44, "after apply"),
        box(110, 160, 130, h, "bxt", "child module"),
        box(320, 160, 130, h, "bxg", "state file"),
        arrow(250, 76, 190, 156), cap(168, 122, "module block"),
        arrow(310, 76, 370, 156), cap(404, 122, "remembers"),
        cap(175, 226, "./modules/site"),
        cap(385, 226, "S3 with a lock in teams"),
    ]
    return svg(240, "Variables flow into the root module, which calls a child module, writes state and prints outputs", p)


def d15():
    h = 44
    p = [
        box(8, 30, 120, h, "bx", "pull request"),
        box(150, 30, 100, h, "bxo", "plan job"),
        box(272, 30, 140, h, "bx", "merge, approve"),
        box(434, 30, 118, h, "bxt", "apply job"),
        arrow(130, 52, 147, 52), arrow(252, 52, 269, 52), arrow(414, 52, 431, 52),
        cap(500, 106, "environment gate"),
        box(80, 170, 120, h, "bxp", "OIDC token"),
        box(250, 170, 110, h, "bxg", "IAM role"),
        box(410, 170, 110, h, "bx", "AWS S3"),
        arrow(202, 192, 247, 192), cap(225, 184, "swap"),
        arrow(362, 192, 407, 192), cap(385, 184, "acts on"),
        arrow(200, 78, 132, 166, dashed=True),
        arrow(490, 78, 172, 166, dashed=True),
        cap(280, 240, "short-lived credentials, no stored keys"),
    ]
    return svg(252, "A pull request runs a plan job; after merge and approval the apply job runs; both swap an OIDC token for an IAM role that acts on S3", p)
