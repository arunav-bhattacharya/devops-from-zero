import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import re

# spoken form of addresses and ".com" for this scene only (captions keep the real spelling)
_LOCAL = [(re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b"), r"\1 dot \2 dot \3 dot \4"),
          (re.compile(r"(?<=\w)\.com\b"), " dot com"), (re.compile(r"(?<!\w)\.com\b"), "dot com")]


def _say(t):
    for p, r in _LOCAL:
        t = p.sub(r, t)
    return t


def ghost(b):
    g = b.copy()
    g[0].set_stroke(GREY_D, 2).set_fill(BLACK, 1)
    g[1].set_color(GREY_D)
    return g


def card(lines, color=GREY_B, size=20, pad=0.3, dashed=False):
    txt = VGroup(*[M(l, size) if isinstance(l, str) else l for l in lines]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    r = RoundedRectangle(corner_radius=0.1, width=txt.width + 2 * pad, height=txt.height + 2 * pad, stroke_color=color, stroke_width=2.5)
    r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.12), opacity=1)
    if dashed:
        r = DashedVMobject(r, num_dashes=40).set_stroke(color, 2)
    return VGroup(r, txt.move_to(r))


def parrow(p1, p2):
    return Arrow(p1, p2, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15, max_stroke_width_to_length_ratio=8)


def back(arrow):
    """A line from an arrow's tip back to its start, for replies."""
    return Line(arrow.get_end(), arrow.get_start())


class D10DnsTcp(VoiceScene):
    def beat(self, text, *anims, run_time=None, after=0.25):
        path, dur = voice(_say(text))
        self._cue(text, dur)
        self.add_sound(path)
        if anims:
            rt = min(run_time if run_time else max(0.8, dur * 0.55), max(0.5, dur))
            self.play(*anims, run_time=rt)
            rest = dur - rt
        else:
            rest = dur
        if rest > 0.02:
            self.wait(rest)
        if after:
            self.wait(after)

    def construct(self):
        self.title_card("From a name to a connection", "DNS finds the address, then TCP opens the line")

        # ---------- part 1: the DNS chain
        cmd = M("$ curl https://example.com", 28).move_to(UP * 3.3)
        app = box("your app", WHITE, w=1.8, h=0.85, size=26).move_to(LEFT * 5.85 + UP * 1.2)
        want = T("example.com = ?", 24, YELLOW_M).next_to(app, DOWN, buff=0.35).align_to(app, LEFT)
        self.beat("Your app wants to connect to example.com. But machines connect to addresses, not names.",
                  Write(cmd), Create(app[0]), Write(app[1]), FadeIn(want, shift=UP * 0.15), run_time=2.0)

        stub = box("stub resolver", TEAL_M, w=2.4, h=0.85, size=24).move_to(LEFT * 2.9 + UP * 1.2)
        rec = box("recursive resolver", BLUE_M, w=2.8, h=0.85, size=24).move_to(RIGHT * 0.55 + UP * 1.2)
        root = box("root", GREY_B, w=2.4, h=0.7, size=24).move_to(RIGHT * 5.2 + UP * 2.75)
        tld = box("TLD  (.com)", GOLD_M, w=2.4, h=0.7, size=24).move_to(RIGHT * 5.2 + UP * 1.15)
        auth = box("authoritative", GREEN_M, w=2.4, h=0.7, size=24).move_to(RIGHT * 5.2 + DOWN * 0.6)
        chain = [stub, rec, root, tld, auth]
        ghosts = [ghost(b) for b in chain]
        self.beat("DNS turns the name into an address. No single server knows every name, so the question travels down a chain.",
                  LaggedStart(*[FadeIn(g) for g in ghosts], lag_ratio=0.2), run_time=2.0)

        a1 = edge_arrow(app, stub)
        self.beat("First stop, the stub resolver. It is a small part of your operating system.",
                  ReplacementTransform(ghosts[0], stub), Succession(GrowArrow(a1), travel(a1)), run_time=2.0)

        hosts = chip("/etc/hosts", GREY_B, 20, mono=True).next_to(stub, DOWN, buff=0.4)
        scache_t = T("cache", 22, GREY_B)
        scache = RoundedRectangle(corner_radius=0.1, width=2.5, height=1.3, stroke_color=GREY_D, stroke_width=2).move_to(LEFT * 2.9 + DOWN * 1.75)
        scache_t.next_to(scache, UP, buff=0.12)
        x1 = tick(False, 0.16).next_to(hosts, RIGHT, buff=0.15)
        x2 = tick(False, 0.2).move_to(scache)
        self.beat("It checks the file /etc/hosts, and its own cache. Nothing there.",
                  Succession(AnimationGroup(FadeIn(hosts), FadeIn(scache_t), Create(scache)), AnimationGroup(Create(x1), Create(x2))), run_time=2.4)

        a2 = edge_arrow(stub, rec)
        rlab = T("router, provider, or 1.1.1.1", 22, GREY_B).next_to(rec, DOWN, buff=0.25).shift(LEFT * 0.2)
        self.beat("So it asks a recursive resolver. Your router, your internet provider, or a public one such as 1.1.1.1.",
                  ReplacementTransform(ghosts[1], rec), FadeIn(rlab), Succession(GrowArrow(a2), travel(a2)), run_time=2.4)

        rcache_t = T("cache", 22, GREY_B)
        rcache = scache.copy().move_to(RIGHT * 0.55 + DOWN * 1.75)
        rcache_t.next_to(rcache, UP, buff=0.12)
        x3 = tick(False, 0.2).move_to(rcache)
        a3 = parrow(rec.get_right() + UP * 0.22, root.get_left() + DOWN * 0.1)
        self.beat("Its cache is empty too. So it starts at the top, and asks a root server.",
                  Succession(AnimationGroup(FadeIn(rcache_t), Create(rcache)), Create(x3)),
                  ReplacementTransform(ghosts[2], root), Succession(Wait(0.6), GrowArrow(a3), travel(a3)), run_time=2.6)

        say_root = T("ask the .com servers", 22, YELLOW_M).move_to(RIGHT * 5.2 + UP * 1.95)
        self.beat("The root does not know the answer. Each level only knows who runs the level below it. So the root says: ask the servers for .com.",
                  Succession(Wait(1.2), AnimationGroup(FadeIn(say_root, shift=DOWN * 0.1), travel(back(a3), YELLOW_M))), run_time=3.2)

        a4 = parrow(rec.get_right(), tld.get_left())
        say_tld = T("ask example.com's\nname servers", 22, YELLOW_M).move_to(RIGHT * 5.3 + UP * 0.28)
        self.beat("Next, a .com server, called a TLD server, for top-level domain. It says: ask example.com's own name servers.",
                  ReplacementTransform(ghosts[3], tld), Succession(GrowArrow(a4), travel(a4), Wait(0.8),
                                                                   AnimationGroup(FadeIn(say_tld, shift=DOWN * 0.1), travel(back(a4), YELLOW_M))), run_time=4.0)

        a5 = parrow(rec.get_right() + DOWN * 0.22, auth.get_left() + UP * 0.1)
        ans = card(["example.com  A  203.0.113.10", "TTL 3600"], GREEN_M).move_to(RIGHT * 4.45 + DOWN * 1.9)
        self.beat("Last, the authoritative server for example.com gives the real answer: the address.",
                  ReplacementTransform(ghosts[4], auth), Succession(GrowArrow(a5), travel(a5), FadeIn(ans, shift=DOWN * 0.15)), run_time=3.0)

        # the answer flows back and is cached
        def entry(addr="203.0.113.10", ttl="TTL 3600", col=WHITE):
            g = VGroup(M("example.com", 20), M(addr, 20, col), M(ttl, 20, GREY_B)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            return g

        rent = entry().move_to(rcache)
        sent = entry().move_to(scache)
        got = VGroup(M("example.com", 20, GREEN_M), M("= 203.0.113.10", 20, GREEN_M)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        got.next_to(app, DOWN, buff=0.3).align_to(app, LEFT)
        self.beat("The answer flows back to your app, and each layer on the way caches it.",
                  Succession(AnimationGroup(travel(back(a5), GREEN_M), FadeOut(x3), TransformFromCopy(ans[1], rent)),
                             AnimationGroup(travel(back(a2), GREEN_M), FadeOut(x2), TransformFromCopy(rent, sent)),
                             AnimationGroup(travel(back(a1), GREEN_M), ReplacementTransform(want, got))), run_time=3.6)
        rcache.set_stroke(BLUE_M); scache.set_stroke(TEAL_M)

        # TTL counts down
        tv = ValueTracker(3600)
        def ttl_at(anchor):
            return always_redraw(lambda: M(f"TTL {int(tv.get_value())}", 20, YELLOW_M).move_to(anchor, aligned_edge=LEFT))
        r_ttl, s_ttl = ttl_at(rent[2]), ttl_at(sent[2])
        self.remove(rent[2], sent[2]); self.add(r_ttl, s_ttl)
        self.beat("Every record has a TTL, in seconds. It says how long anyone may cache it. This one says an hour, and the clock is running.",
                  Indicate(ans[1][1], color=YELLOW_M), tv.animate(rate_func=linear).set_value(3588), run_time=4.0)

        # a second lookup is answered from the cache
        hit = SurroundingRectangle(scache, color=GREEN_M, buff=0.06, corner_radius=0.1)
        far = VGroup(root, tld, auth, a3, a4, a5, say_root, say_tld, ans)
        self.beat("Ask again within that hour, and the stub answers straight from its cache. No trip to the root at all.",
                  far.animate.set_opacity(0.25), travel(a1, YELLOW_M), Succession(Wait(0.7), Create(hit), travel(back(a1), GREEN_M)),
                  tv.animate(rate_func=linear).set_value(3580), run_time=3.0)
        self.play(FadeOut(hit), far.animate.set_opacity(1), run_time=0.6)

        # the site moves: caches still hold the old answer
        new_ans = M("example.com  A  203.0.113.20", 20, YELLOW_M).move_to(ans[1][0])
        self.beat("Now say the site moves to a new address. The authoritative server changes its answer right away.",
                  Transform(ans[1][0], new_ans), Circumscribe(auth, color=GREEN_M, buff=0.08), run_time=1.8)
        old1 = T("cache: old answer", 22, RED_M).move_to(rcache_t)
        old2 = T("cache: old answer", 22, RED_M).move_to(scache_t)
        self.beat("People say a DNS change takes time to propagate. What really happens is that old answers sit in caches, until their TTL runs out.",
                  rent[1].animate.set_color(RED_M), sent[1].animate.set_color(RED_M), ReplacementTransform(rcache_t, old1), ReplacementTransform(scache_t, old2),
                  tv.animate(rate_func=linear).set_value(3560), run_time=3.2)
        self.beat("So teams lower the TTL a day before a planned move. One hour becomes 60 seconds, so old answers expire within a minute.",
                  tv.animate.set_value(60), Transform(ans[1][1], M("TTL 60", 20, YELLOW_M).move_to(ans[1][1], aligned_edge=LEFT)), run_time=2.2)
        self.wait(0.3)

        # ---------- part 2: the TCP handshake
        r_ttl.clear_updaters(); s_ttl.clear_updaters()
        rest = [m for m in self.mobjects if m not in (cmd, app, got)]
        self.play(*[FadeOut(m) for m in rest], run_time=0.8)
        cl = box("your app", WHITE, w=2.6, h=0.85, size=26).move_to(LEFT * 4.6 + UP * 2.4)
        sv_lab = VGroup(T("server", 26), M("203.0.113.10:443", 22, TEAL_M)).arrange(DOWN, buff=0.1)
        sv_r = RoundedRectangle(corner_radius=0.12, width=3.4, height=1.15, stroke_color=TEAL_M, stroke_width=3)
        sv_r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(TEAL_M), 0.14), opacity=1)
        sv = VGroup(sv_r, sv_lab.move_to(sv_r)).move_to(RIGHT * 4.6 + UP * 2.4)
        p443 = VGroup(M("https://example.com", 26), T("names no port, so:  443", 26, TEAL_M)).arrange(DOWN, buff=0.25).move_to(UP * 0.4)
        self.beat("Now the app has an address. The URL names no port, so curl uses 443, the HTTPS port.",
                  ReplacementTransform(app, cl), FadeOut(got), ReplacementTransform(cmd, p443[0]), Create(sv_r), Write(sv_lab),
                  Succession(Wait(1.0), FadeIn(p443[1], shift=UP * 0.1)), run_time=2.6)

        xc, xs, y_top, y_bot = cl.get_center()[0], sv.get_center()[0], 1.75, -3.3
        lc = DashedLine([xc, cl.get_bottom()[1] - 0.05, 0], [xc, y_bot, 0], dash_length=0.1, stroke_width=2, color=GREY_D)
        ls = DashedLine([xs, sv.get_bottom()[1] - 0.05, 0], [xs, y_bot, 0], dash_length=0.1, stroke_width=2, color=GREY_D)

        def msg(y1, y2, name, quote, color, to_server=True):
            p1, p2 = ([xc, y1, 0], [xs, y2, 0]) if to_server else ([xs, y1, 0], [xc, y2, 0])
            a = Arrow(p1, p2, buff=0.05, stroke_width=4, color=color, max_tip_length_to_length_ratio=0.03)
            lab = M(name, 24, color).move_to(a.point_from_proportion(0.5) + UP * 0.32)
            q = T(quote, 22, GREY_B).move_to(a.point_from_proportion(0.5) + DOWN * 0.42) if quote else VGroup()
            return a, lab, q

        self.beat("Before any data moves, TCP opens a connection with a three-step handshake.",
                  FadeOut(p443), Create(lc), Create(ls), run_time=1.4)
        syn = msg(1.3, 0.8, "SYN", "I want to talk.", YELLOW_M)
        self.beat("One. The client sends SYN. I want to talk.",
                  GrowArrow(syn[0]), FadeIn(syn[1]), FadeIn(syn[2]), run_time=1.4)
        sack = msg(-0.1, -0.6, "SYN-ACK", "Fine, I hear you.", BLUE_M, to_server=False)
        self.beat("Two. The server answers SYN-ACK. Fine, I hear you.",
                  GrowArrow(sack[0]), FadeIn(sack[1]), FadeIn(sack[2]), run_time=1.4)
        ack = msg(-1.4, -1.9, "ACK", None, GREEN_M)
        opened = Line([xc, -2.6, 0], [xs, -2.6, 0], stroke_width=8, color=GREEN_M)
        olab = T("connection open", 26, GREEN_M).next_to(opened, DOWN, buff=0.2)
        self.beat("Three. The client sends ACK, and the connection is open. Now the bytes can flow, in order.",
                  Succession(AnimationGroup(GrowArrow(ack[0]), FadeIn(ack[1])), AnimationGroup(Create(opened), FadeIn(olab))), run_time=2.4)
        self.play(travel(opened, YELLOW_M, run_time=0.8), run_time=0.8)

        # ---------- part 3: refused vs timed out
        hs = VGroup(*syn, *sack, *ack, opened, olab)
        port8000 = M("203.0.113.10:8000", 22, RED_M).move_to(sv_lab[1])
        nol = T("nothing listens on 8000", 22, RED_M).next_to(sv, DOWN, buff=0.15).shift(LEFT * 0.0)
        self.beat("But connections fail, and the error tells you which step broke. Say you try port 8000, where nothing listens.",
                  FadeOut(hs), Transform(sv_lab[1], port8000), run_time=1.6)
        self.play(FadeIn(nol, shift=DOWN * 0.1), run_time=0.5)
        syn2 = msg(1.0, 0.4, "SYN", None, YELLOW_M)
        rst = msg(0.2, -0.4, "RST (a reset)", None, RED_M, to_server=False)
        refused = M("Connection refused", 26, RED_M).next_to([xc + 0.4, -1.2, 0], RIGHT, buff=0)
        fast = T("back in about 1 ms", 24, GREY_B).next_to(refused, DOWN, buff=0.2, aligned_edge=LEFT)
        self.beat("The machine is there, so it answers your SYN, with a reset. Connection refused.",
                  Succession(AnimationGroup(GrowArrow(syn2[0]), FadeIn(syn2[1])), AnimationGroup(GrowArrow(rst[0]), FadeIn(rst[1])),
                             FadeIn(refused, shift=UP * 0.1)), run_time=2.6)
        self.beat("A refusal comes back in about a millisecond. The host is there, but nothing listens on that port.",
                  FadeIn(fast), Indicate(nol, color=RED_M), run_time=1.6)

        # timeout: a firewall drops the SYN
        self.play(FadeOut(VGroup(*syn2, *rst, refused, fast, nol)), Transform(sv_lab[1], M("203.0.113.10:443", 22, TEAL_M).move_to(sv_lab[1])), run_time=0.7)
        wall_x = 1.6
        wall = Rectangle(width=0.22, height=4.2, stroke_color=RED_M, stroke_width=2).set_fill(RED_M, 0.35).move_to([wall_x, -0.6, 0])
        wlab = T("firewall", 24, RED_M).next_to(wall, UP, buff=0.12)
        self.beat("A timeout is different. Nothing answers at all. A firewall dropped the packets, or the address is wrong, or unreachable.",
                  FadeIn(wall), FadeIn(wlab), run_time=1.6)

        ys = [1.3, 0.6, -0.6, -2.4]
        tries = VGroup()
        for i, y in enumerate(ys):
            a = Arrow([xc, y, 0], [wall_x - 0.45, y - 0.22, 0], buff=0.05, stroke_width=4, color=YELLOW_M, max_tip_length_to_length_ratio=0.04)
            lab = M("SYN" if i == 0 else "SYN again", 22, YELLOW_M).move_to(a.point_from_proportion(0.45) + UP * 0.28)
            xx = tick(False, 0.12).move_to([wall_x - 0.27, y - 0.22, 0])
            tries.add(VGroup(a, lab, xx))
        waits = VGroup()
        for y1, y2 in zip(ys[:-1], ys[1:]):
            ln = Line([xc - 0.35, y1 - 0.08, 0], [xc - 0.35, y2 + 0.08, 0], stroke_width=3, color=GREY_B)
            waits.add(ln)
        wl = T("waits\nlonger\neach time", 22, GREY_B).move_to([xc - 1.35, -0.4, 0])
        self.beat("Your machine hears nothing back, so it sends the SYN again.",
                  Succession(AnimationGroup(GrowArrow(tries[0][0]), FadeIn(tries[0][1])), Create(tries[0][2]), Create(waits[0]),
                             AnimationGroup(GrowArrow(tries[1][0]), FadeIn(tries[1][1])), Create(tries[1][2])), run_time=2.6)
        self.beat("It resends a few times, waiting longer each time, before it gives up.",
                  Succession(Create(waits[1]), AnimationGroup(GrowArrow(tries[2][0]), FadeIn(tries[2][1])), Create(tries[2][2]),
                             Create(waits[2]), AnimationGroup(GrowArrow(tries[3][0]), FadeIn(tries[3][1])), Create(tries[3][2])),
                  FadeIn(wl), run_time=3.4)
        tout = M("Timed out", 26, GOLD_M).next_to([xc - 0.45, -2.45, 0], LEFT, buff=0)
        self.beat("Timed out. So even the waiting is a clue.", FadeIn(tout, shift=UP * 0.1), Indicate(wl, color=GOLD_M), run_time=1.4)

        # ---------- recap table
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        rows = [("Could not resolve host", "DNS failed: no packet was sent", BLUE_M),
                ("Connection refused", "a reset: nothing listens on that port", RED_M),
                ("Timed out", "no answer: dropped, or a wrong address", GOLD_M)]
        table = VGroup()
        for i, (err, why, col) in enumerate(rows):
            e = chip(err, col, 22, mono=True)
            w = T(why, 26)
            table.add(VGroup(e, w))
        for i, r in enumerate(table):
            r[0].move_to([-3.6, 1.3 - 1.25 * i, 0])
            r[1].next_to([-1.15, 1.3 - 1.25 * i, 0], RIGHT, buff=0)
        head = T("read the error first", 30, GREY_B).move_to(UP * 2.75)
        self.beat("So read the error first. Could not resolve host means DNS failed, and no packet went to the server at all.",
                  FadeIn(head), FadeIn(table[0][0], shift=RIGHT * 0.2), Write(table[0][1]), run_time=2.4)
        self.beat("Connection refused means a reset. The host answered, but nothing listens on that port.",
                  FadeIn(table[1][0], shift=RIGHT * 0.2), Write(table[1][1]), run_time=2.0)
        self.beat("And a timeout means no answer. The packets were dropped, or the address is wrong.",
                  FadeIn(table[2][0], shift=RIGHT * 0.2), Write(table[2][1]), run_time=2.0)
        recap = T("name  →  address  →  handshake  →  connected", 30, YELLOW_M).move_to(DOWN * 2.6)
        self.beat("First DNS turns the name into an address. Then TCP shakes hands with that address and port.",
                  Write(recap), run_time=2.4)
        self.wait(1.0)
