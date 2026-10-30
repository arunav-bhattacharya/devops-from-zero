"""Tiny helpers for the Part 12 diagrams, with size and overlap checks."""

W = 560


class Diagram:
    def __init__(self, h, label):
        assert 140 <= h <= 380
        self.h, self.label, self.parts, self.rects, self.texts = h, label, [], [], []

    def _inside(self, x0, y0, x1, y1, what):
        assert x0 >= 8 and y0 >= 8 and x1 <= W - 8 and y1 <= self.h - 8, (what, x0, y0, x1, y1)

    def box(self, x, y, w, h, cls, label):
        assert w >= 8 * len(label) + 24, (label, w)
        self._inside(x, y, x + w, y + h, label)
        for (a, b, c, d, name) in self.rects:
            sep = x + w + 12 <= a or c + 12 <= x or y + h + 12 <= b or d + 12 <= y
            assert sep, ("boxes too close", label, name)
        self.rects.append((x, y, x + w, y + h, label))
        tcls = "t" if cls == "bx" else "tk"
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>')
        self.parts.append(
            f'<text x="{x + w / 2:g}" y="{y + h / 2 + 5:g}" font-size="13" text-anchor="middle" class="{tcls}">{label}</text>')

    def arrow(self, x1, y1, x2, y2, dashed=False):
        cls = "lnd" if dashed else "ln"
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" marker-end="url(#ar)"/>')

    def cap(self, x, y, s):
        half = len(s) * 6.2 / 2
        x0, x1, y0, y1 = x - half, x + half, y - 10, y + 2
        self._inside(x0, y0, x1, y1, s)
        for (a, b, c, d, name) in self.rects:
            assert x1 <= a or c <= x0 or y1 <= b or d <= y0, ("caption overlaps box", s, name)
        self.parts.append(f'<text x="{x}" y="{y}" font-size="11" text-anchor="middle" class="ts">{s}</text>')

    def svg(self):
        return (f'<svg viewBox="0 0 {W} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" '
                f'aria-label="{self.label}">' + "".join(self.parts) + "</svg>")


def d50():
    d = Diagram(330, "OneAgent sends data through ActiveGate to Grail. Smartscape and PurePath traces feed Davis, "
                     "which opens one problem with a root cause")
    d.cap(85, 20, "in pods and hosts")
    d.cap(280, 20, "relay")
    d.cap(475, 20, "every signal")
    d.box(20, 30, 130, 44, "bxo", "OneAgent")
    d.box(215, 30, 130, 44, "bxt", "ActiveGate")
    d.box(410, 30, 130, 44, "bxp", "Grail")
    d.arrow(152, 52, 211, 52)
    d.arrow(347, 52, 406, 52)
    d.box(140, 140, 140, 44, "bx", "Smartscape")
    d.box(320, 140, 120, 44, "bx", "PurePath")
    d.arrow(450, 76, 232, 136)
    d.arrow(466, 76, 404, 136)
    d.cap(85, 166, "the map")
    d.cap(495, 166, "the traces")
    d.box(200, 250, 100, 44, "bxg", "Davis")
    d.box(380, 250, 120, 44, "bx", "Problem")
    d.arrow(222, 186, 238, 246)
    d.arrow(366, 186, 272, 246)
    d.arrow(302, 272, 376, 272)
    d.cap(120, 276, "walks both")
    d.cap(440, 312, "one root cause")
    return d.svg()


def d51():
    d = Diagram(224, "You write a DynaKube. The Operator reads it and runs a webhook that injects OneAgent into the "
                     "hello pod, plus an ActiveGate that relays data to Grail, which you query from a Notebook with DQL")
    d.cap(63, 20, "you write it")
    d.cap(205, 20, "Helm installs it")
    d.cap(352, 20, "relay")
    d.cap(498, 20, "Dynatrace SaaS")
    d.box(8, 30, 110, 44, "bx", "DynaKube")
    d.box(150, 30, 110, 44, "bxo", "Operator")
    d.box(292, 30, 120, 44, "bxt", "ActiveGate")
    d.box(444, 30, 108, 44, "bxp", "Grail")
    d.arrow(120, 52, 146, 52)
    d.arrow(262, 52, 288, 52)
    d.arrow(414, 52, 440, 52)
    d.box(150, 140, 110, 44, "bx", "Webhook")
    d.box(292, 140, 120, 44, "bxo", "hello pod")
    d.arrow(205, 76, 205, 136)
    d.arrow(262, 162, 288, 162)
    d.arrow(352, 138, 352, 78)
    d.cap(275, 128, "injects")
    d.cap(380, 110, "data")
    d.cap(352, 202, "with OneAgent")
    d.cap(110, 166, "in kind")
    d.box(444, 140, 108, 44, "bx", "Notebook")
    d.arrow(498, 76, 498, 136)
    d.cap(520, 110, "DQL")
    return d.svg()


if __name__ == "__main__":
    print(d50()[:200])
    print(d51()[:200])
