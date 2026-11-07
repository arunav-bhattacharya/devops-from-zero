import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import re

# spoken form for this scene only (captions keep the real spelling)
_LOCAL = [(re.compile(r"(?<=\w)\.com\b"), " dot com"), (re.compile(r"\bTLS 1\.3\b"), "T L S one point three")]


def _say(t):
    for p, r in _LOCAL:
        t = p.sub(r, t)
    return t


def card(lines, color=GREY_B, size=22, pad=0.25):
    txt = VGroup(*[M(l, size) if isinstance(l, str) else l for l in lines]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    r = RoundedRectangle(corner_radius=0.1, width=txt.width + 2 * pad, height=txt.height + 2 * pad, stroke_color=color, stroke_width=2.5)
    r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.12), opacity=1)
    return VGroup(r, txt.move_to(r))


def key_icon(color=TEAL_M, s=1.0):
    ring = Circle(radius=0.13, stroke_color=color, stroke_width=4)
    shaft = Line(ring.get_right(), ring.get_right() + RIGHT * 0.42, stroke_width=4, color=color)
    t1 = Line(shaft.get_end(), shaft.get_end() + DOWN * 0.13, stroke_width=4, color=color)
    t2 = Line(shaft.get_end() + LEFT * 0.14, shaft.get_end() + LEFT * 0.14 + DOWN * 0.1, stroke_width=4, color=color)
    return VGroup(ring, shaft, t1, t2).scale(s)


def lock_icon(color=GOLD_M, s=1.0):
    body = RoundedRectangle(corner_radius=0.04, width=0.34, height=0.26, stroke_color=color, stroke_width=3).set_fill(color, 0.5)
    shackle = Arc(radius=0.11, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(body, UP, buff=0)
    return VGroup(body, shackle).scale(s)


def two_line_box(top, bottom, color, w=2.6, h=1.05, size_top=26, size_bot=22, mono_bot=True):
    t = VGroup(T(top, size_top), (M if mono_bot else T)(bottom, size_bot, color)).arrange(DOWN, buff=0.1)
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3)
    r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.14), opacity=1)
    return VGroup(r, t.move_to(r))


class D11Https(VoiceScene):
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
        self.title_card("HTTPS, step by step", "a sealed line, and proof of who is on the other end")

        # ---------- 1. plain HTTP on the path
        y0 = 1.2
        you = box("you", WHITE, w=1.5, h=0.8).move_to([-5.6, y0, 0])
        srv = box("server", TEAL_M, w=1.8, h=0.8).move_to([5.5, y0, 0])
        hops = VGroup(*[Circle(radius=0.36, stroke_color=GREY_B, stroke_width=3).set_fill(BLACK, 1).move_to([x, y0, 0]) for x in (-2.8, 0.0, 2.8)])
        hl = VGroup(T("café Wi-Fi", 22, GREY_B), T("router", 22, GREY_B), T("router", 22, GREY_B))
        for h, l in zip(hops, hl):
            l.next_to(h, DOWN, buff=0.3)
        nodes = [you, *hops, srv]
        links = VGroup(*[Line(a.get_right(), b.get_left(), stroke_width=2, color=GREY_D) for a, b in zip(nodes[:-1], nodes[1:])])
        path = Line(you.get_right(), srv.get_left())
        req = card(["POST /login", "password=s3cret"], WHITE).move_to([-4.6, 2.85, 0])
        self.beat("Plain HTTP is readable text. Every router between you and the server passes it along.",
                  FadeIn(you), FadeIn(srv), LaggedStart(*[Create(l) for l in links], lag_ratio=0.15),
                  LaggedStart(*[GrowFromCenter(h) for h in hops], lag_ratio=0.2), FadeIn(hl), FadeIn(req, shift=DOWN * 0.15), run_time=2.6)
        self.play(travel(path, YELLOW_M, run_time=1.6), run_time=1.6)

        spy = box("someone on the same Wi-Fi", RED_M, h=0.75, size=24).move_to([-2.8, -0.75, 0])
        spy_l = DashedLine(hops[0].get_bottom() + DOWN * 0.55, spy.get_top(), dash_length=0.08, stroke_width=2, color=RED_M)
        copy = req.copy()
        self.beat("Whoever runs one of them, or shares an open café Wi-Fi with you, could read your password.",
                  FadeIn(spy), Create(spy_l), copy.animate.move_to([-2.8, -1.95, 0]), run_time=2.2)
        self.play(copy[1][1].animate.set_color(RED_M), Circumscribe(copy, color=RED_M, buff=0.06), run_time=1.0)

        resp = card(["HTTP/1.1 200 OK", "<p>Welcome back</p>"], TEAL_M).move_to([4.4, 2.85, 0])
        evil = M("<script src=x.js>", 22, RED_M).move_to(resp[1][1], aligned_edge=LEFT)
        self.beat("Or change the page on its way back.",
                  FadeIn(resp, shift=DOWN * 0.15), travel(Line(srv.get_left(), hops[2].get_center()), TEAL_M), run_time=1.6)
        self.play(Indicate(hops[2], color=RED_M), Transform(resp[1][1], evil), run_time=1.0)
        self.wait(0.3)

        # ---------- 2. HTTPS: the same request inside TLS
        tube = RoundedRectangle(corner_radius=0.45, width=srv.get_left()[0] - you.get_right()[0] + 0.2, height=0.95,
                                stroke_color=GOLD_M, stroke_width=4).move_to([(srv.get_left()[0] + you.get_right()[0]) / 2, y0, 0])
        tube.set_fill(GOLD_M, 0.07).set_z_index(-1)
        tls_l = T("TLS", 28, GOLD_M).next_to(tube, UP, buff=0.12).shift(LEFT * 1.6)
        scr1 = VGroup(M("9f3a c1e0 77b2", 22, GREY_B), M("e04b 5d19 aa7c", 22, GREY_B))
        self.beat("HTTPS is HTTP inside a TLS connection. The same request, sealed on its way.",
                  FadeOut(resp), Create(tube), FadeIn(tls_l), run_time=1.8)
        chips = VGroup(chip("confidentiality", BLUE_M, 26), chip("integrity", TEAL_M, 26), chip("authentication", GOLD_M, 26)).arrange(RIGHT, buff=0.5).move_to([1.3, -3.25, 0])
        scr_req = VGroup(*[s.copy().move_to(l, aligned_edge=LEFT) for s, l in zip(scr1, req[1])])
        scr_cp = VGroup(*[s.copy().move_to(l, aligned_edge=LEFT) for s, l in zip(scr1, copy[1])])
        self.beat("TLS gives you three things. First, confidentiality. Nobody on the path can read the traffic.",
                  FadeIn(chips[0], shift=UP * 0.15), Transform(req[1], scr_req), Transform(copy[1], scr_cp),
                  req[0].animate.set_stroke(GOLD_M), copy[0].animate.set_stroke(GREY_D), run_time=2.0)
        self.play(travel(path, GOLD_M, run_time=1.2), run_time=1.2)

        caught = VGroup(tick(False, 0.2), T("change detected", 22, RED_M)).arrange(RIGHT, buff=0.15).next_to(you, UP, buff=0.3).align_to(you, LEFT)
        self.beat("Second, integrity. Nobody can change it without the change being detected.",
                  FadeIn(chips[1], shift=UP * 0.15), Succession(Indicate(hops[2], color=RED_M),
                                                                travel(Line(hops[2].get_center(), you.get_right()), RED_M), FadeIn(caught)), run_time=2.6)
        cert = VGroup(T("certificate", 22, GOLD_M), M("example.com", 22)).arrange(DOWN, buff=0.08)
        cert_r = RoundedRectangle(corner_radius=0.08, width=cert.width + 0.35, height=cert.height + 0.3, stroke_color=GOLD_M, stroke_width=2.5).set_fill(BLACK, 1)
        certg = VGroup(cert_r, cert.move_to(cert_r)).next_to(srv, DOWN, buff=0.35)
        k = key_icon(GOLD_M, 0.9).next_to(certg, DOWN, buff=0.2)
        self.beat("Third, authentication. The server proves it holds the private key for a certificate that names this host.",
                  FadeIn(chips[2], shift=UP * 0.15), FadeIn(certg, shift=UP * 0.15), Succession(Wait(0.8), Create(k)), run_time=2.6)
        self.wait(0.3)

        # ---------- 3. the handshake
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        cl = box("client", WHITE, w=2.2, h=0.8).move_to([-4.6, 2.75, 0])
        sv = box("server", TEAL_M, w=2.2, h=0.8).move_to([4.6, 2.75, 0])
        xc, xs = -4.6, 4.6
        lc = DashedLine([xc, 2.3, 0], [xc, -3.4, 0], dash_length=0.1, stroke_width=2, color=GREY_D)
        ls = DashedLine([xs, 2.3, 0], [xs, -3.4, 0], dash_length=0.1, stroke_width=2, color=GREY_D)
        self.beat("Before any HTTP flows, the client and the server run a handshake. In TLS 1.3, it takes one round trip.",
                  FadeIn(cl), FadeIn(sv), Create(lc), Create(ls), run_time=1.8)

        def msg(y1, y2, color, to_server=True):
            p1, p2 = ([xc, y1, 0], [xs, y2, 0]) if to_server else ([xs, y1, 0], [xc, y2, 0])
            return Arrow(p1, p2, buff=0.05, stroke_width=4, color=color, max_tip_length_to_length_ratio=0.03)

        ch = msg(1.75, 1.35, YELLOW_M)
        ch_l = M("ClientHello", 24, YELLOW_M).move_to(ch.point_from_proportion(0.5) + UP * 0.3)
        ch_d = T("ciphers   ·   its key half   ·   the host name", 22, GREY_B).move_to(ch.point_from_proportion(0.5) + DOWN * 0.32)
        self.beat("The client says hello. It lists the ciphers it supports, sends its half of a key exchange, and names the host it wants.",
                  GrowArrow(ch), FadeIn(ch_l), Succession(Wait(0.6), FadeIn(ch_d, shift=DOWN * 0.1)), run_time=2.6)

        sh = msg(0.5, 0.1, BLUE_M, to_server=False)
        sh_l = M("ServerHello + key half", 24, BLUE_M).move_to(sh.point_from_proportion(0.5) + UP * 0.3)
        sh_d = VGroup(lock_icon(GOLD_M, 0.8), T("then, encrypted: certificate  +  signature", 22, GOLD_M)).arrange(RIGHT, buff=0.18)
        sh_d.move_to(sh.point_from_proportion(0.5) + DOWN * 0.36)
        self.beat("The server answers with its own hello, and its half of the key exchange. Then, already encrypted, it sends its certificate, and a signature that proves it holds the matching private key.",
                  GrowArrow(sh), FadeIn(sh_l), Succession(Wait(2.0), FadeIn(sh_d, shift=DOWN * 0.1)), run_time=4.0)

        # key agreement
        yk = -1.25
        cs = Dot([-3.5, yk, 0], radius=0.14, color=GOLD_M)
        ss = Dot([3.5, yk, 0], radius=0.14, color=PURPLE_M)
        cs_l = T("secret", 22, GOLD_M).next_to(cs, DOWN, buff=0.15)
        ss_l = T("secret", 22, PURPLE_M).next_to(ss, DOWN, buff=0.15)
        pc = Circle(radius=0.13, stroke_color=GOLD_M, stroke_width=4).move_to(cs).set_fill(BLACK, 1)
        ps = Circle(radius=0.13, stroke_color=PURPLE_M, stroke_width=4).move_to(ss).set_fill(BLACK, 1)
        pub = T("public values", 22, GREY_B).move_to([0, yk + 0.38, 0])
        self.beat("How can two machines agree on a key while others listen? Each side keeps a random secret, and sends only a public value made from it.",
                  Succession(AnimationGroup(GrowFromCenter(cs), GrowFromCenter(ss), FadeIn(cs_l), FadeIn(ss_l)), Wait(1.0),
                             AnimationGroup(pc.animate.move_to([2.75, yk, 0]), ps.animate.move_to([-2.75, yk, 0]), FadeIn(pub))), run_time=4.0)
        k1 = key_icon(TEAL_M, 1.0).move_to([-3.1, yk - 1.0, 0])
        k2 = key_icon(TEAL_M, 1.0).move_to([3.1, yk - 1.0, 0])
        same = T("the same key", 24, TEAL_M).move_to([0, yk - 1.0, 0])
        nope = T("not enough to work it out", 22, GREY_B).next_to(pub, DOWN, buff=0.12)
        self.beat("Each side combines its own secret with the other's public value. Both arrive at the same key. The public values alone are not enough to work it out.",
                  Succession(AnimationGroup(TransformFromCopy(VGroup(cs, ps), k1), TransformFromCopy(VGroup(ss, pc), k2)), FadeIn(same),
                             FadeIn(nope)), run_time=4.0)
        kx = VGroup(cs, ss, cs_l, ss_l, pc, ps, pub, k1, k2, same, nope)

        # the client checks the certificate
        checks = VGroup(*[VGroup(tick(True, 0.16), T(t, 24)).arrange(RIGHT, buff=0.2) for t in ("the right name", "still valid", "signed by someone it trusts")])
        checks.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([-1.0, -1.45, 0])
        q = T("?", 30, YELLOW_M).move_to(checks[2][0])
        self.beat("The client checks the certificate. The right name. Still valid. Signed by someone it trusts.",
                  FadeOut(kx), Succession(Wait(0.6), *[FadeIn(c, shift=RIGHT * 0.15) for c in checks[:2]],
                                          AnimationGroup(FadeIn(checks[2][1], shift=RIGHT * 0.15), FadeIn(q))), run_time=3.6)
        enc = msg(-2.65, -3.05, GOLD_M)
        enc_l = VGroup(lock_icon(GOLD_M, 0.8), T("the HTTP request, encrypted", 22, GOLD_M)).arrange(RIGHT, buff=0.15).move_to(enc.point_from_proportion(0.5) + UP * 0.32)
        self.beat("From here on, everything, including the HTTP request, is encrypted.",
                  GrowArrow(enc), FadeIn(enc_l), run_time=1.6)
        self.wait(0.3)

        # ---------- 4. certificates and the chain of trust
        self.play(FadeOut(Group(*[m for m in self.mobjects])), run_time=0.8)
        rows = [("names", "example.com"), ("public key", "3f:9a:c1:e0"), ("valid", "Nov 1 to Jan 30"), ("signed by", "Intermediate CA")]
        labels = VGroup(*[T(a, 26, GREY_B) for a, _ in rows]).arrange(DOWN, buff=0.32, aligned_edge=RIGHT)
        vals = VGroup(*[M(b, 26) for _, b in rows])
        for v, l in zip(vals, labels):
            v.next_to(l, RIGHT, buff=0.45)
        body = VGroup(labels, vals)
        frame = RoundedRectangle(corner_radius=0.15, width=body.width + 0.9, height=body.height + 0.8, stroke_color=TEAL_M, stroke_width=3)
        frame.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(TEAL_M), 0.1), opacity=1)
        big = VGroup(frame, body.move_to(frame)).move_to([0, 0.0, 0])
        btitle = T("certificate", 30, TEAL_M).next_to(big, UP, buff=0.25)
        self.beat("But a signature only proves the server holds some private key. Who says that key belongs to example.com? A certificate, signed by someone the browser trusts.",
                  Create(frame), FadeIn(btitle), Succession(Wait(1.6), LaggedStart(*[AnimationGroup(FadeIn(labels[i]), Write(vals[i])) for i in range(2)], lag_ratio=0.4)), run_time=4.0)
        self.beat("A certificate is a signed statement. This public key belongs to these names, from this date to that date.",
                  Succession(Indicate(vals[1], color=YELLOW_M), Indicate(vals[0], color=YELLOW_M), AnimationGroup(FadeIn(labels[2]), Write(vals[2]))), run_time=3.4)
        self.beat("A certificate authority, a CA, signs it, after checking that the requester controls those names.",
                  FadeIn(labels[3]), Write(vals[3]), Circumscribe(VGroup(labels[0], vals[0]), color=YELLOW_M, buff=0.08), run_time=2.4)

        # shrink into the chain column
        def cert_box(t1, t2, color):
            g = VGroup(T(t1, 24, color), M(t2, 22) if t2 else VGroup()).arrange(DOWN, buff=0.08)
            r = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.95, stroke_color=color, stroke_width=3)
            r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.14), opacity=1)
            return VGroup(r, g.move_to(r))

        cx = 0.9
        c_srv = cert_box("certificate", "example.com", TEAL_M).move_to([cx, -2.35, 0])
        c_int = cert_box("Intermediate CA", None, PURPLE_M).move_to([cx, -0.45, 0])
        c_root = cert_box("Root CA", None, GOLD_M).move_to([cx, 1.6, 0])
        self.play(ReplacementTransform(VGroup(big, btitle), c_srv), run_time=1.0)

        store_items = VGroup(chip("Root CA", GOLD_M, 24), chip("another root", GREY_B, 24), chip("another root", GREY_B, 24)).arrange(DOWN, buff=0.22)
        store_r = RoundedRectangle(corner_radius=0.15, width=3.2, height=store_items.height + 1.1, stroke_color=BLUE_M, stroke_width=3)
        store_r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(BLUE_M), 0.08), opacity=1)
        store = VGroup(store_r, store_items.move_to(store_r).shift(DOWN * 0.2)).move_to([-4.7, 0.6, 0])
        store_t = T("trust store", 26, BLUE_M).move_to(store_r.get_top() + DOWN * 0.35)
        store_s = T("in your OS and browser", 22, GREY_B).next_to(store_r, DOWN, buff=0.15)
        self.beat("Your operating system and browser ship a trust store. A list of root CAs they trust.",
                  Create(store_r), FadeIn(store_t), FadeIn(store_s), LaggedStart(*[FadeIn(s, shift=RIGHT * 0.15) for s in store_items], lag_ratio=0.25), run_time=2.4)

        s1 = Arrow(c_root.get_bottom(), c_int.get_top(), buff=0.08, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        s2 = Arrow(c_int.get_bottom(), c_srv.get_top(), buff=0.08, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        s1l = T("signs", 22, GREY_B).next_to(s1, RIGHT, buff=0.15)
        s2l = T("signs", 22, GREY_B).next_to(s2, RIGHT, buff=0.15)
        self.beat("Roots rarely sign server certificates directly. A root signs an intermediate CA, and the intermediate signs the server's certificate.",
                  Succession(FadeIn(c_root, shift=DOWN * 0.15), AnimationGroup(GrowArrow(s1), FadeIn(s1l)), FadeIn(c_int, shift=DOWN * 0.15),
                             AnimationGroup(GrowArrow(s2), FadeIn(s2l))), run_time=4.2)
        off = VGroup(lock_icon(GOLD_M, 1.0), T("key kept offline", 22, GOLD_M)).arrange(RIGHT, buff=0.15).next_to(c_root, RIGHT, buff=0.3)
        self.beat("That lets the root keys stay offline, locked away.", FadeIn(off, shift=LEFT * 0.15), run_time=1.2)

        server = box("server", TEAL_M, w=1.7, h=0.8).move_to([5.3, -1.4, 0])
        sent = DashedVMobject(SurroundingRectangle(VGroup(c_int, c_srv), buff=0.18, corner_radius=0.15), num_dashes=60).set_stroke(TEAL_M, 2)
        sent_l = T("sent by the server", 22, TEAL_M).next_to(server, DOWN, buff=0.2)
        sl = DashedLine(server.get_left(), sent.get_right() + DOWN * 0.0, dash_length=0.08, stroke_width=2, color=TEAL_M)
        climb = VMobject().set_points_as_corners([c_srv.get_center(), c_int.get_center(), c_root.get_center()])
        dot = Dot(c_srv.get_center(), radius=0.1, color=YELLOW_M)
        match = DashedLine(c_root.get_left(), store_items[0].get_right(), dash_length=0.1, stroke_width=3, color=GREEN_M)
        ok = tick(True, 0.25).move_to(match.get_center() + UP * 0.35)
        self.beat("The server sends its certificate, plus the intermediates. The client follows that chain up, to a root it already trusts.",
                  Succession(AnimationGroup(FadeIn(server), Create(sent), FadeIn(sent_l), Create(sl)),
                             AnimationGroup(FadeIn(dot), MoveAlongPath(dot, climb, rate_func=smooth)),
                             AnimationGroup(Create(match), Create(ok))), run_time=5.0)
        self.play(FadeOut(dot), run_time=0.3)

        bad = tick(False, 0.25).next_to(c_int, RIGHT, buff=0.35)
        why = T("missing, expired,\nor another name", 22, RED_M).next_to(bad, RIGHT, buff=0.25)
        fail = T("connection fails", 28, RED_M).move_to([-4.7, -2.4, 0])
        self.beat("If any link is missing, expired, or made out to another name, the connection fails.",
                  c_int[0].animate.set_stroke(RED_M), Create(bad), FadeIn(why), match.animate.set_stroke(RED_M).set_opacity(0.4), FadeOut(ok),
                  Succession(Wait(1.0), FadeIn(fail, shift=UP * 0.1)), run_time=2.8)
        self.wait(0.3)

        # ---------- 5. where TLS ends: the reverse proxy
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        cl2 = box("client", WHITE, w=1.6, h=0.8).move_to([-5.8, 0.3, 0])
        ng_t = VGroup(T("nginx", 30), T("reverse proxy", 22, GREY_B), T("TLS ends here", 22, GOLD_M)).arrange(DOWN, buff=0.12)
        ng_r = RoundedRectangle(corner_radius=0.15, width=2.7, height=1.8, stroke_color=GOLD_M, stroke_width=3)
        ng_r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(GOLD_M), 0.12), opacity=1)
        ng = VGroup(ng_r, ng_t.move_to(ng_r)).move_to([-1.0, 0.3, 0])
        app1 = two_line_box("app1", "HTTP :8000", TEAL_M).move_to([4.4, 1.75, 0])
        app2 = two_line_box("app2", "HTTP :8000", TEAL_M).move_to([4.4, -1.15, 0])
        self.beat("In production, a request rarely goes straight to your app. A reverse proxy, such as nginx, or a load balancer, sits in front of the app copies.",
                  FadeIn(cl2), Create(ng_r), Write(ng_t[0]), FadeIn(ng_t[1]), FadeIn(app1, shift=LEFT * 0.2), FadeIn(app2, shift=LEFT * 0.2), run_time=2.6)

        tube2 = RoundedRectangle(corner_radius=0.3, width=ng.get_left()[0] - cl2.get_right()[0] + 0.2, height=0.6, stroke_color=GOLD_M, stroke_width=4)
        tube2.move_to([(ng.get_left()[0] + cl2.get_right()[0]) / 2, 0.3, 0]).set_fill(GOLD_M, 0.05).set_z_index(-1)
        core2 = Line(cl2.get_right(), ng.get_left(), stroke_width=2, color=GOLD_M).set_z_index(-1)
        tube2_l = VGroup(lock_icon(GOLD_M, 0.8), T("HTTPS", 24, GOLD_M)).arrange(RIGHT, buff=0.12).next_to(tube2, UP, buff=0.15)
        ncert = VGroup(T("certificate", 22, GOLD_M), M("example.com", 20)).arrange(DOWN, buff=0.06)
        ncr = RoundedRectangle(corner_radius=0.08, width=ncert.width + 0.3, height=ncert.height + 0.25, stroke_color=GOLD_M, stroke_width=2.5).set_fill(BLACK, 1)
        ncg = VGroup(ncr, ncert.move_to(ncr)).next_to(ng, UP, buff=0.3)
        self.beat("The proxy holds the certificate, and runs the handshake with the client. TLS ends there. This is called TLS termination.",
                  Create(tube2), Create(core2), FadeIn(tube2_l), FadeIn(ncg, shift=DOWN * 0.15), Succession(Wait(1.6), FadeIn(ng_t[2]), Circumscribe(ng_t[2], color=GOLD_M)), run_time=3.4)

        l1 = Arrow(ng.get_right() + UP * 0.3, app1.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        l2 = Arrow(ng.get_right() + DOWN * 0.3, app2.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        pl = T("plain HTTP", 22, GREY_B).move_to([1.85, 0.3, 0])
        self.beat("Behind it, the proxy talks plain HTTP to the app copies on port 8000, and spreads the requests across them.",
                  GrowArrow(l1), GrowArrow(l2), FadeIn(pl), Succession(Wait(0.6), travel(Line(cl2.get_right(), ng.get_left()), GOLD_M, run_time=0.6),
                                                                      travel(l1, YELLOW_M, run_time=0.6), travel(Line(cl2.get_right(), ng.get_left()), GOLD_M, run_time=0.6),
                                                                      travel(l2, YELLOW_M, run_time=0.6)), run_time=3.4)
        hdrs = card(["X-Forwarded-Proto: https", "X-Forwarded-For: <client address>"], GREY_B, 22).move_to([1.2, -2.85, 0])
        self.beat("It adds headers, so the app still knows the truth. X-Forwarded-Proto says the client used HTTPS, even though the app only saw plain HTTP.",
                  FadeIn(hdrs, shift=UP * 0.15), Succession(Wait(1.6), Indicate(hdrs[1][0], color=YELLOW_M)), run_time=3.0)

        x1 = tick(False, 0.3).move_to(app1)
        x2 = tick(False, 0.3).move_to(app2)
        e502 = M("502 Bad Gateway", 22, RED_M).move_to([(ng.get_left()[0] + cl2.get_right()[0]) / 2, -0.4, 0])
        r502 = Arrow([ng.get_left()[0] - 0.05, -0.8, 0], [cl2.get_right()[0] + 0.05, -0.8, 0], buff=0, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.1)
        self.beat("And if no copy answers, the proxy itself replies: 502, Bad Gateway.",
                  FadeOut(hdrs), app1.animate.set_opacity(0.35), app2.animate.set_opacity(0.35), Create(x1), Create(x2),
                  Succession(Wait(1.0), AnimationGroup(GrowArrow(r502), FadeIn(e502, shift=LEFT * 0.3))), run_time=2.4)
        self.wait(0.3)

        # ---------- recap
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        recap = VGroup(
            VGroup(lock_icon(GOLD_M, 1.0), T("TLS encrypts, and proves control of the name", 30)).arrange(RIGHT, buff=0.3),
            VGroup(key_icon(PURPLE_M, 1.0), T("the chain leads up to a root you already trust", 30)).arrange(RIGHT, buff=0.3),
            VGroup(Dot(radius=0.12, color=TEAL_M), T("in production, TLS often ends at the proxy", 30)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("So: TLS encrypts the traffic, and proves control of the name. The certificate chain leads up to a root you already trust. And in production, TLS often ends at the proxy in front of your apps.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in recap], lag_ratio=0.9), run_time=8.0)
        self.wait(1.0)
