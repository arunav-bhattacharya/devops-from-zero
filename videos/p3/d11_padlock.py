import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bpaypa1-login\.example\b", "paypa one dash login dot example"), (r"\btickets\.example\b", "tickets dot example"),
    (r"\bLet's Encrypt\b", "Let's Encrypt"), (r"\bSNI\b", "S N I"), (r"\bClientHello\b", "client hello"),
    (r"\blocalhost\.crt\b", "localhost dot C R T"), (r"--cacert", "dash dash C A cert"), (r"\bcurl\b", "curl"),
])

ME, SRV, BAD, KEY, CERT, ROOT = BLUE_M, TEAL_M, RED_M, GREEN_M, GOLD_M, PURPLE_M
LAP = np.array([-5.2, -0.2, 0])
SRVP = np.array([5.2, -0.2, 0])
HOPS_X = [-2.15, 0.0, 2.15]
PATH_Y = -0.2


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def padlock(color, s=1.0):
    body = RoundedRectangle(corner_radius=0.06, width=0.5, height=0.4, stroke_color=color, stroke_width=4).set_fill(tint(color, 0.35), 1)
    sh = Arc(radius=0.16, start_angle=0, angle=PI, stroke_color=color, stroke_width=4).next_to(body, UP, buff=0).shift(DOWN * 0.02)
    return VGroup(body, sh).scale(s)


def postcard(lines, color=WHITE, w=2.6):
    t = VGroup(*[M(l, 22, color) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    r = Rectangle(width=max(w, t.width + 0.4), height=t.height + 0.4, stroke_color=color, stroke_width=2.5).set_fill("#101010", 1)
    return VGroup(r, t.move_to(r))


def envelope(color=CERT, w=1.3, h=0.85):
    r = Rectangle(width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1)
    flap = VMobject(stroke_color=color, stroke_width=2.5).set_points_as_corners([r.get_corner(UL), r.get_center() + DOWN * 0.08, r.get_corner(UR)])
    return VGroup(r, flap)


def cert_card(title, lines, color, w=4.2):
    t = T(title, 26, color)
    body = VGroup(*[T(l, 24) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    r = RoundedRectangle(corner_radius=0.12, width=max(w, body.width + 0.6), height=body.height + 1.0, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), 1)
    t.move_to(r.get_top() + DOWN * 0.32)
    body.next_to(t, DOWN, buff=0.18).align_to(r, LEFT).shift(RIGHT * 0.3)
    return VGroup(r, t, body)


class D11Padlock(VoiceScene):
    def construct(self):
        self.title_card("What the padlock proves", "a sealed envelope, and who holds the other end")

        # ---------- 1. the cafe and the question
        bar = RoundedRectangle(corner_radius=0.14, width=8.6, height=0.8, stroke_color=GREY_B, stroke_width=2.5).move_to(UP * 0.6)
        lk = padlock(GREEN_M, 0.8).move_to(bar.get_left() + RIGHT * 0.55)
        url = M("https://tickets.example/pay", 28).next_to(lk, RIGHT, buff=0.35)
        self.beat("Picture a café with free Wi-Fi. You buy a train ticket on your laptop, and you see the little padlock next to the web address. Safe, you think.",
                  Create(bar), FadeIn(url), Succession(Wait(5.0), FadeIn(lk, scale=0.6)), run_time=7.0)
        q = T("Safe from what?", 40, YELLOW_M).move_to(DOWN * 1.4)
        self.beat("Then a friend asks a fair question. Safe from what? Hold on to that one.",
                  Succession(Wait(1.8), Write(q)), run_time=3.0)
        self.play(FadeOut(VGroup(bar, lk, url, q)), run_time=0.6)

        # ---------- 2. plain HTTP is a postcard
        lap = box("your laptop", ME, w=2.6, h=1.2).move_to(LAP)
        srv = box("ticket site", SRV, w=2.6, h=1.2).move_to(SRVP)
        hops = VGroup(*[box(n, GREY_B, w=1.95, h=0.75, size=24) for n in ("café Wi-Fi", "router", "provider")])
        for h, x in zip(hops, HOPS_X):
            h.move_to(np.array([x, PATH_Y, 0]))
        links = VGroup(link(lap, hops[0]), link(hops[0], hops[1]), link(hops[1], hops[2]), link(hops[2], srv))
        self.beat("Between your laptop and the ticket site sit a lot of machines you don't own. The café's Wi-Fi, routers, your provider. Each one passes your message along.",
                  FadeIn(lap), FadeIn(srv), Succession(Wait(2.6), LaggedStart(*[FadeIn(h) for h in hops], lag_ratio=0.4)), Succession(Wait(4.0), Create(links)), run_time=8.0)
        card = postcard(["POST /pay", "password=tr41n"]).move_to(LAP + UP * 1.8)
        self.beat("Plain web traffic is a postcard. It's readable text, the language called HTTP.",
                  FadeIn(card, shift=DOWN * 0.2), run_time=1.6)
        eyes = VGroup(*[T("reads it", 24, RED_M).next_to(h, DOWN, buff=0.25) for h in hops])
        self.beat("So whoever runs one of those machines, or simply shares the café's open Wi-Fi, can read your password, or even change the page.",
                  card.animate(run_time=3.2, rate_func=linear).move_to(np.array([HOPS_X[2], PATH_Y + 1.8, 0])),
                  Succession(Wait(1.2), LaggedStart(*[FadeIn(e, shift=UP * 0.1) for e in eyes], lag_ratio=0.6)), run_time=5.0)
        changed = postcard(["POST /pay", "password=tr41n", "+ an extra line"], RED_M).move_to(card)
        self.play(Transform(card, changed), run_time=0.7)
        self.beat("What we want is a sealed envelope. Nobody on the way can read it, nobody can change it without being caught, and we know who opens it at the other end.",
                  FadeOut(card), FadeOut(eyes), run_time=1.2)

        # ---------- 3. the key problem: obvious fix, broken
        self.beat("To seal anything, both ends need the same secret key. Here's the puzzle. How do two machines agree on a key, when everyone in the café is listening?",
                  Indicate(lap[1], color=ME), Indicate(srv[1], color=SRV), run_time=1.6)
        kchip = chip("key", KEY, 26).move_to(LAP + UP * 1.6)
        self.beat("The obvious answer: just send the key across. Let's see how that goes.",
                  Succession(FadeIn(kchip, scale=0.8, run_time=0.6), Wait(1.0), kchip.animate(run_time=2.2, rate_func=linear).move_to(np.array([HOPS_X[1], PATH_Y + 1.6, 0]))), run_time=4.2)
        copies = VGroup(*[chip("key", KEY, 22).next_to(h, DOWN, buff=0.25) for h in hops])
        self.beat("Well. Now everyone on the way has a copy of the key, and the seal is worth nothing.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in copies], lag_ratio=0.4), run_time=1.8)
        self.play(FadeOut(VGroup(kchip, copies)), run_time=0.5)

        # ---------- 4. the trick: secret plus public value
        sa = VGroup(Circle(radius=0.26, stroke_color=CERT, stroke_width=3).set_fill(tint(CERT, 0.5), 1), M("a", 24))
        sa[1].move_to(sa[0]); sa.move_to(LAP + DOWN * 1.5)
        sb = VGroup(Circle(radius=0.26, stroke_color=SRV, stroke_width=3).set_fill(tint(SRV, 0.5), 1), M("b", 24))
        sb[1].move_to(sb[0]); sb.move_to(SRVP + DOWN * 1.5)
        lab_s = T("secret, never sent", 24, GREY_B).next_to(sa, DOWN, buff=0.2)
        lab_s2 = T("secret, never sent", 24, GREY_B).next_to(sb, DOWN, buff=0.2)
        self.beat("Here's the trick. Each side picks a random secret of its own, and keeps it. It never travels.",
                  GrowFromCenter(sa), GrowFromCenter(sb), FadeIn(lab_s), FadeIn(lab_s2), run_time=1.8)
        pa = chip("A", CERT, 26, mono=True).move_to(LAP + UP * 1.4)
        pb = chip("B", SRV, 26, mono=True).move_to(SRVP + UP * 1.4)
        self.beat("From its secret, each side makes a public value, and sends only that. Capital A goes one way, capital B the other.",
                  Succession(AnimationGroup(FadeIn(pa), FadeIn(pb), run_time=0.6), Wait(2.4), AnimationGroup(pa.animate(run_time=2.4).move_to(SRVP + UP * 1.4 + LEFT * 0.9), pb.animate(run_time=2.4).move_to(LAP + UP * 1.4 + RIGHT * 0.9))), run_time=6.4)
        seen = VGroup(*[chip("A, B", GREY_B, 22, mono=True).next_to(h, DOWN, buff=0.25) for h in hops])
        self.beat("The café sees A and B. That's all it sees.",
                  LaggedStart(*[FadeIn(c) for c in seen], lag_ratio=0.3), run_time=1.6)
        k1 = chip("same key", KEY, 26).move_to(LAP + UP * 2.6)
        k2 = chip("same key", KEY, 26).move_to(SRVP + UP * 2.6)
        mix1 = VGroup(M("a + B", 24, WHITE)).next_to(k1, DOWN, buff=0.15)
        mix2 = VGroup(M("b + A", 24, WHITE)).next_to(k2, DOWN, buff=0.15)
        self.beat("Now each side combines its own secret with the other side's public value. Your laptop mixes little a with B. The site mixes little b with A. And both arrive at the same key.",
                  Succession(Wait(3.0), FadeIn(mix1)), Succession(Wait(5.2), FadeIn(mix2)), Succession(Wait(8.0), AnimationGroup(FadeIn(k1, shift=UP * 0.1), FadeIn(k2, shift=UP * 0.1))), run_time=10.0)
        nope = T("A and B alone are not enough", 26, RED_M).move_to(DOWN * 2.6)
        self.beat("The public values alone are not enough to work it out. It feels like a magic trick, and it's the kind that holds up.",
                  FadeIn(nope), Indicate(seen[1][1], color=GREY_B), run_time=2.0)
        env = envelope(KEY).move_to(LAP + UP * 1.4 + RIGHT * 0.9)
        self.beat("From here on, the request travels sealed. The café sees an envelope, not a postcard.",
                  FadeOut(VGroup(pa, pb, seen, nope, mix1, mix2, lab_s, lab_s2, sa, sb)),
                  Succession(Wait(1.0), FadeIn(env), env.animate(run_time=2.4).move_to(SRVP + UP * 1.4 + LEFT * 0.9)), run_time=4.6)
        self.play(FadeOut(env), run_time=0.4)

        # ---------- 5. sealed to whom? the impostor and the certificate
        fake = box("impostor", BAD, w=2.0, h=0.75, size=24).move_to(np.array([HOPS_X[0], PATH_Y - 1.6, 0]))
        self.beat("But wait. A sealed envelope to whom? Someone in the café could play the same trick with you, and pretend to be the ticket site.",
                  Succession(FadeIn(fake, shift=UP * 0.2, run_time=0.6), Wiggle(fake, run_time=1.4)), run_time=2.6)
        self.beat("So the seal is only worth something if you know who holds the other end.",
                  Indicate(srv[1], color=SRV), run_time=1.4)
        cc = cert_card("certificate", ["names: tickets.example", "public key: the site's", "valid: from this date to that"], CERT)
        cc.move_to(np.array([4.25, 2.05, 0]))
        self.beat("So the site sends a certificate. It's a signed statement that says: this public key belongs to these names, from this date to that date.",
                  FadeOut(VGroup(k1, k2)), FadeIn(cc, shift=DOWN * 0.2), run_time=2.4)
        sig = chip("signature", CERT, 22).move_to(SRVP + DOWN * 1.5)
        self.beat("And it sends a signature that only the matching private key can make. That's the same proof your SSH key gave in Day 7.",
                  Succession(FadeIn(sig, run_time=0.5), Wait(1.5), sig.animate(run_time=2.4).move_to(LAP + DOWN * 1.5)), run_time=5.0)
        self.play(FadeOut(VGroup(sig, fake)), run_time=0.5)
        self.remove(sig, fake)

        # ---------- 6. the chain up to a root you already trust
        world = VGroup(lap, srv, hops, links)
        self.play(world.animate.set_opacity(0.15), cc.animate.move_to(np.array([1.6, -2.3, 0])), run_time=0.8)
        ic = cert_card("intermediate CA", ["signs servers' certificates"], CERT, w=4.6).move_to(np.array([1.6, 0.0, 0]))
        rc = cert_card("root CA", ["key kept offline"], ROOT, w=4.6).move_to(np.array([1.6, 1.95, 0]))
        a1 = arrow(cc[0].get_top(), ic[0].get_bottom(), GREY_B)
        a2 = arrow(ic[0].get_top(), rc[0].get_bottom(), GREY_B)
        sl1 = T("signed by", 24, GREY_B).next_to(a1, RIGHT, buff=0.15)
        sl2 = T("signed by", 24, GREY_B).next_to(a2, RIGHT, buff=0.15)
        self.beat("But who signed the certificate? A certificate authority, a CA. Your browser can't ask you about every site, so it trusts a few CAs to vouch for them, the way a passport office vouches for a photo.",
                  Succession(Wait(3.0), AnimationGroup(GrowArrow(a1), FadeIn(sl1), FadeIn(ic, shift=DOWN * 0.15))), run_time=9.0)
        self.beat("Usually an intermediate CA signs the server's certificate, and a root CA signs the intermediate. That lets the root keys stay offline, locked away.",
                  Succession(Wait(3.4), AnimationGroup(GrowArrow(a2), FadeIn(sl2), FadeIn(rc, shift=DOWN * 0.15))), run_time=6.4)
        store = RoundedRectangle(corner_radius=0.12, width=3.4, height=1.5, stroke_color=ROOT, stroke_width=2.5).set_fill(BLACK, 1).move_to(np.array([-4.4, 2.2, 0]))
        stl = T("trust store", 26, ROOT).next_to(store.get_top(), DOWN, buff=0.22)
        stc = T("root CA", 24).next_to(stl, DOWN, buff=0.18)
        stn = T("on your laptop", 24, GREY_B).next_to(store, DOWN, buff=0.15)
        self.beat("Your operating system and browser ship with a trust store, a short list of root CAs they already trust. The client follows the chain up, link by link, until it reaches one of them.",
                  FadeIn(VGroup(store, stl, stc, stn)), Succession(Wait(4.4), Indicate(cc[1], color=CERT), Indicate(ic[1], color=CERT), Indicate(rc[1], color=ROOT)), run_time=8.0)
        okt = tick(True, 0.3).next_to(store, RIGHT, buff=0.25)
        match = DashedLine(rc[0].get_left(), store.get_right(), dash_length=0.1, color=ROOT)
        self.beat("It matches, so the padlock appears. If any link is missing, expired, or made out to another name, the connection fails.",
                  Create(match), Succession(Wait(1.0), Create(okt)), run_time=2.2)

        # break: the self-signed lab certificate
        err = M("curl: (60) SSL certificate problem: self-signed certificate", 22, RED_M).move_to(UP * 3.15)
        fit(err, 12.6)
        self.beat("You'll see that failure in the lab. A certificate you make yourself for localhost is signed by itself, so curl refuses it, and it's right to. It can't tell it from an attacker's.",
                  Write(err), Succession(Wait(3.0), AnimationGroup(FadeOut(VGroup(match, okt)), a1.animate.set_opacity(0.2), ic.animate.set_opacity(0.2), a2.animate.set_opacity(0.2), rc.animate.set_opacity(0.2), sl1.animate.set_opacity(0.2), sl2.animate.set_opacity(0.2))), run_time=8.0)
        fix = M("$ curl --cacert localhost.crt https://localhost:8443/", 22, GREEN_M).move_to(err)
        self.beat("With --cacert localhost.crt, you tell curl to trust exactly that one certificate. It still checks the name and the dates.",
                  ReplacementTransform(err, fix), run_time=2.0)
        self.play(FadeOut(VGroup(fix, a1, a2, ic, rc, sl1, sl2, cc, store, stl, stc, stn)), world.animate.set_opacity(1), run_time=0.8)

        # ---------- 7. the guess: paypa1-login.example
        bar = RoundedRectangle(corner_radius=0.14, width=8.6, height=0.8, stroke_color=GREY_B, stroke_width=2.5).move_to(UP * 2.4)
        lk = padlock(GREEN_M, 0.8).move_to(bar.get_left() + RIGHT * 0.55)
        url = M("https://paypa1-login.example", 28).next_to(lk, RIGHT, buff=0.35)
        self.beat("Now back to the café question. Your browser shows a padlock on paypa1-login.example. Look at that name carefully. Pause and guess. What does the padlock prove?",
                  FadeOut(world), Create(bar), FadeIn(lk), FadeIn(url), Succession(Wait(5.0), Indicate(url[13], color=RED_M, scale_factor=1.6)), run_time=8.0, after=2.2)
        p1 = VGroup(tick(True, 0.25), T("nobody on the way can read or change it", 28)).arrange(RIGHT, buff=0.3)
        p2 = VGroup(tick(True, 0.25), T("the other end really controls this name", 28)).arrange(RIGHT, buff=0.3)
        p3 = VGroup(tick(False, 0.25), T("the other end is honest", 28, RED_M)).arrange(RIGHT, buff=0.3)
        pg = VGroup(p1, p2, p3).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(DOWN * 0.5)
        self.beat("It proves the traffic is sealed, so nobody on the way can read or change it. And it proves the other end controls that name.",
                  FadeIn(p1, shift=RIGHT * 0.2), Succession(Wait(3.4), FadeIn(p2, shift=RIGHT * 0.2)), run_time=5.6)
        self.beat("That's all. Let's Encrypt, a free CA, gives a certificate to anyone who controls a domain, including this one. The padlock says nothing about whether they're honest.",
                  Succession(Wait(5.2), FadeIn(p3, shift=RIGHT * 0.2)), run_time=7.0)
        self.beat("So the padlock is a very good envelope, and a terrible character reference.",
                  Indicate(p3[1], color=RED_M), run_time=1.6)

        # ---------- 8. limits
        self.play(FadeOut(VGroup(bar, lk, url, pg)), run_time=0.6)
        l1 = T("Not hidden: the server's IP address, and usually the host name (SNI)", 28)
        l2 = T("Let's Encrypt certificates: 90 days today, 45 days from 2028", 28)
        l3 = T("So renewal must be automated, and watched", 28, YELLOW_M)
        lg = VGroup(l1, l2, l3).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(UP * 0.2)
        fit(lg, 12.6)
        self.beat("Two more limits. TLS doesn't hide everything. Everyone on the path still sees the server's IP address, and usually the host name too, because the browser names the site in a field called SNI, before encryption starts.",
                  FadeIn(l1, shift=RIGHT * 0.2), run_time=1.6)
        self.beat("And certificates expire, on purpose, sooner each year. Let's Encrypt certificates last 90 days today, and 45 days from 2028. Nobody should renew those by hand, so renewal must be automated, and watched.",
                  Succession(Wait(1.0), FadeIn(l2, shift=RIGHT * 0.2)), Succession(Wait(8.0), FadeIn(l3, shift=RIGHT * 0.2)), run_time=11.0)
        self.play(FadeOut(lg), run_time=0.6)

        # ---------- 9. moral and check
        m1 = T("Sealed on the way. Checked at the other end.", 38)
        m2 = T("Trust in the people behind it is still your call.", 30, GREY_B).next_to(m1, DOWN, buff=0.4)
        mg = VGroup(m1, m2).move_to(UP * 0.8)
        self.beat("So, the moral of the story. TLS seals the envelope on the way, and checks who holds the other end. Whether the people behind that name deserve your money is still your call.",
                  Write(m1), Succession(Wait(5.0), FadeIn(m2, shift=UP * 0.1)), run_time=8.0)
        self.play(mg.animate.scale(0.75).to_edge(UP, buff=0.8).set_opacity(0.6), run_time=0.6)
        c1 = T("You pay on https://tickets.example from the café.", 30)
        c2 = T("What can someone on the café Wi-Fi still see?", 32, YELLOW_M)
        cg = VGroup(c1, c2).arrange(DOWN, buff=0.4).move_to(DOWN * 0.2)
        self.beat("A quick check. You pay on tickets.example, over HTTPS, from the café. What can someone on the café Wi-Fi still see? Pause and guess.",
                  FadeIn(c1), Succession(Wait(3.6), FadeIn(c2)), run_time=5.0, after=2.2)
        ans = VGroup(T("the site's IP address, and usually its name", 28, GREEN_M), T("not your password, not the page", 28, GREEN_M)).arrange(DOWN, buff=0.2).next_to(cg, DOWN, buff=0.6)
        self.beat("The site's IP address, and usually its name, because SNI travels before the seal. But not your password, and not the page. Those are inside the envelope.",
                  FadeIn(ans[0], shift=UP * 0.1), Succession(Wait(4.4), FadeIn(ans[1], shift=UP * 0.1)), run_time=6.0)
        self.wait(1.5)
