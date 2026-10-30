"""Inline SVG diagrams for Part 6. Only the classes the page styles are used."""

HEAD = '<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'


def box(x, y, w, h, cls, label, tcls=None):
    tcls = tcls or ("t" if cls == "bx" else "tk")
    cx = x + w / 2
    cy = y + h / 2 + 5
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>'
            f'<text x="{cx:g}" y="{cy:g}" font-size="13" text-anchor="middle" class="{tcls}">{label}</text>')


def cap(x, y, text):
    return f'<text x="{x}" y="{y}" font-size="11" text-anchor="middle" class="ts">{text}</text>'


def lbl(x, y, text):
    return f'<text x="{x}" y="{y}" font-size="13" text-anchor="middle" class="t">{text}</text>'


def arrow(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" marker-end="url(#ar)"/>'


def svg(h, label, parts):
    return HEAD.format(h=h, label=label) + "".join(parts) + "</svg>"


# Day 25: code, plan, apply, provider, Docker, with the state file underneath.
D25 = svg(234, "Terraform reads main.tf, plans against the state file, and applies through a provider to Docker", [
    box(8, 40, 92, 44, "bx", "main.tf"),
    box(120, 40, 92, 44, "bxo", "plan"),
    box(232, 40, 92, 44, "bxt", "apply"),
    box(344, 40, 92, 44, "bxp", "provider"),
    box(456, 40, 96, 44, "bxg", "Docker"),
    arrow(102, 62, 118, 62), arrow(214, 62, 230, 62), arrow(326, 62, 342, 62), arrow(438, 62, 454, 62),
    cap(504, 104, "real world"),
    box(168, 150, 116, 44, "bx", "state file"),
    arrow(196, 148, 172, 90, True), cap(150, 124, "reads"),
    arrow(280, 88, 262, 146, True), cap(306, 124, "writes"),
    cap(280, 222, "plan compares code, state and reality; apply makes them match"),
])

# Day 26: what one removal does to count copies and to for_each copies.
D26 = svg(214, "Removing alpha from a list: count replaces and destroys numbered copies, for_each destroys only alpha", [
    lbl(50, 55, "count"),
    box(100, 28, 136, 44, "bxo", "[0] replaced"),
    box(250, 28, 136, 44, "bxo", "[1] replaced"),
    box(400, 28, 136, 44, "bxp", "[2] destroyed"),
    cap(318, 90, "numbered copies shift down by one"),
    lbl(50, 135, "for_each"),
    box(100, 108, 136, 44, "bxp", "alpha gone"),
    box(250, 108, 136, 44, "bxt", "bravo kept"),
    box(400, 108, 136, 44, "bxt", "charlie kept"),
    cap(318, 170, "named copies stay where they are"),
    cap(280, 200, "the plan after removing alpha from the list"),
])

# Day 27: the three pictures plan compares.
D27 = svg(280, "Plan compares your code, the state file and the real world", [
    box(8, 30, 150, 48, "bx", "your .tf code"),
    box(215, 30, 130, 48, "bxo", "plan"),
    box(402, 30, 150, 48, "bxg", "state file"),
    arrow(160, 54, 211, 54), arrow(400, 54, 349, 54),
    cap(83, 96, "desired state"), cap(477, 96, "Terraform's memory"),
    box(205, 170, 150, 48, "bxt", "real world"),
    arrow(280, 168, 280, 82), cap(318, 128, "refresh"),
    cap(280, 236, "what really exists"),
    cap(280, 266, "plan compares all three; apply makes reality match the code"),
])

# Day 28: one root module calls the same child module twice.
D28 = svg(250, "The infra/local root module calls the hello-stack module twice, as dev and test", [
    box(8, 96, 130, 48, "bx", "infra/local"),
    cap(73, 162, "root module"),
    box(200, 40, 150, 48, "bxo", "module dev"),
    cap(275, 104, "port 8080"),
    box(200, 152, 150, 48, "bxt", "module test"),
    cap(275, 216, "port 8082"),
    box(412, 96, 140, 48, "bxg", "hello-stack"),
    cap(482, 162, "one folder of code"),
    arrow(140, 110, 198, 70), arrow(140, 130, 198, 170),
    arrow(352, 70, 410, 108), arrow(352, 170, 410, 132),
    cap(280, 240, "two calls, one module, two separate stacks"),
])

# Day 29: the pipeline and the OIDC login (kept from the first edition).
D29 = ('<svg viewBox="0 0 560 252" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A pull request runs checks and a plan job; after merge and approval the apply job runs; both swap an OIDC token for an IAM role that acts on S3">'
       '<rect x="8" y="30" width="120" height="44" rx="10" class="bx"/><text x="68" y="57" font-size="13" text-anchor="middle" class="t">pull request</text>'
       '<rect x="150" y="30" width="100" height="44" rx="10" class="bxo"/><text x="200" y="57" font-size="13" text-anchor="middle" class="tk">plan job</text>'
       '<rect x="272" y="30" width="140" height="44" rx="10" class="bx"/><text x="342" y="57" font-size="13" text-anchor="middle" class="t">merge, approve</text>'
       '<rect x="434" y="30" width="118" height="44" rx="10" class="bxt"/><text x="493" y="57" font-size="13" text-anchor="middle" class="tk">apply job</text>'
       '<line x1="130" y1="52" x2="147" y2="52" class="ln" marker-end="url(#ar)"/>'
       '<line x1="252" y1="52" x2="269" y2="52" class="ln" marker-end="url(#ar)"/>'
       '<line x1="414" y1="52" x2="431" y2="52" class="ln" marker-end="url(#ar)"/>'
       '<text x="200" y="92" font-size="11" text-anchor="middle" class="ts">after checks pass</text>'
       '<text x="500" y="106" font-size="11" text-anchor="middle" class="ts">environment gate</text>'
       '<rect x="80" y="170" width="120" height="44" rx="10" class="bxp"/><text x="140" y="197" font-size="13" text-anchor="middle" class="tk">OIDC token</text>'
       '<rect x="250" y="170" width="110" height="44" rx="10" class="bxg"/><text x="305" y="197" font-size="13" text-anchor="middle" class="tk">IAM role</text>'
       '<rect x="410" y="170" width="110" height="44" rx="10" class="bx"/><text x="465" y="197" font-size="13" text-anchor="middle" class="t">AWS S3</text>'
       '<line x1="202" y1="192" x2="247" y2="192" class="ln" marker-end="url(#ar)"/><text x="225" y="184" font-size="11" text-anchor="middle" class="ts">swap</text>'
       '<line x1="362" y1="192" x2="407" y2="192" class="ln" marker-end="url(#ar)"/><text x="385" y="184" font-size="11" text-anchor="middle" class="ts">acts on</text>'
       '<line x1="190" y1="98" x2="132" y2="166" class="lnd" marker-end="url(#ar)"/>'
       '<line x1="490" y1="78" x2="172" y2="166" class="lnd" marker-end="url(#ar)"/>'
       '<text x="280" y="240" font-size="11" text-anchor="middle" class="ts">short-lived credentials, no stored keys</text></svg>')
