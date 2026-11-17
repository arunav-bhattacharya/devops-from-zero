import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bistiod\b", "istio D"), (r"\bSPIFFE\b", "spiffy"), (r"\bServiceAccount\b", "service account"),
            (r"\bPeerAuthentication\b", "peer authentication"), (r"\bAuthorizationPolicy\b", "authorization policy"),
            (r"\bPERMISSIVE\b", "permissive"), (r"\bSTRICT\b", "strict"), (r"\bDISABLE\b", "disable"), (r"\bALLOW\b", "allow"),
            (r"\bztunnel\b", "zee tunnel"), (r"\bSDS\b", "S D S"), (r"\bRBAC\b", "R-back"), (r"\bhello-mesh\b", "hello mesh")])

MGR_C = GOLD_M      # istiod, the badge office
APP_C = TEAL_M      # app containers
PRX_C = BLUE_M      # Envoy sidecars (door readers)
BADGE_C = GREEN_M   # certificates / badges
BAD_C = RED_M
ASK_C = YELLOW_M
OUT_C = GREY_B      # the outside Pod


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def badge(name, c=BADGE_C):
    r = RoundedRectangle(corner_radius=0.06, width=1.5, height=0.5, stroke_color=c, stroke_width=2.5).set_fill(tint(c, 0.3), 1)
    return VGroup(r, T(name, 22).move_to(r))


def podbox(name, ns, x, y, sidecar=True, c=APP_C, h=1.8):
    r = RoundedRectangle(corner_radius=0.15, width=3.2, height=h, stroke_color=GREY_D, stroke_width=2).move_to([x, y, 0])
    yy = y + 0.2
    app = Circle(radius=0.34, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.25), 1).move_to([x - 0.7, yy, 0])
    al = T(name, 22, c).next_to(r, UP, buff=0.1)
    nsl = M(f"ns: {ns}", 20, GREY_B).next_to(r, DOWN, buff=0.1)
    g = dict(r=r, app=app, lab=al, ns=nsl)
    if sidecar:
        px = Square(0.62, stroke_color=PRX_C, stroke_width=3).set_fill(tint(PRX_C, 0.25), 1).move_to([x + 0.7, yy, 0])
        g["px"] = px
        g["pxl"] = T("Envoy", 20, PRX_C).move_to(px)
    return g


def badge_at(b, g):
    return b.scale(0.75).move_to(g["app"].get_center() + DOWN * 0.68)


def grp(g):
    return VGroup(*g.values())


class D59Badges(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("No badge, no entry", "identity, mutual TLS and who may open which door")

        # ---------- 1. the strict Monday
        door = RoundedRectangle(corner_radius=0.1, width=1.6, height=2.6, stroke_color=MGR_C, stroke_width=3).move_to([1.5, 0.2, 0])
        reader = Square(0.35, stroke_color=PRX_C, stroke_width=3).set_fill(tint(PRX_C, 0.4), 1).next_to(door, LEFT, buff=0.15).shift(UP * 0.3)
        sign = T("no badge, no entry", 28, MGR_C).next_to(door, UP, buff=0.3)
        self.beat("Our office building now has a building manager. Each morning, the badge office prints every worker a fresh badge, good for one day. Door readers check badges, not faces.",
                  Create(door), FadeIn(reader), run_time=3.0)
        workers = VGroup(*[VGroup(Dot(radius=0.12, color=APP_C), badge("staff").scale(0.6)).arrange(DOWN, buff=0.05) for _ in range(3)]).arrange(RIGHT, buff=0.3).move_to([-2.4, 0.2, 0])
        self.beat("One Monday the manager makes the rule strict. No badge, no entry.",
                  FadeIn(sign), FadeIn(workers), run_time=2.0)
        self.play(*[w.animate.move_to(door.get_center() + RIGHT * (2.6 + 0.6 * i)) for i, w in enumerate(workers)], run_time=1.4)
        guests = VGroup(*[VGroup(Dot(radius=0.12, color=OUT_C), T(n, 22, OUT_C)).arrange(DOWN, buff=0.08) for n in ("cleaner", "plants", "courier")]).arrange(RIGHT, buff=0.35).move_to([-3.0, -2.0, 0])
        self.beat("By ten o'clock, the cleaners, the plant service and the courier with the morning reports are all stuck on the pavement. Nobody had told them about badges.",
                  FadeIn(guests, shift=RIGHT * 0.3), Succession(Wait(2.0), Flash(reader, color=BAD_C)), run_time=4.0)
        self.beat("Every door worked perfectly. The people who got hurt were the ones nobody remembered. Hold on to that, because we are going to make this exact mistake on purpose.",
                  run_time=None)
        self.play(FadeOut(VGroup(door, reader, sign, workers, guests)), run_time=0.6)

        # ---------- 2. familiar: one-sided TLS
        cli = box("you", GREY_B, w=1.8).move_to([-4.0, 0.6, 0])
        shop = box("web shop", GREY_B, w=2.4).move_to([3.6, 0.6, 0])
        cert = badge("shop's ID").move_to([0.2, 1.3, 0])
        ar1 = edge_arrow(cli, shop)
        self.beat("You've met half of this already. With ordinary HTTPS, only the server proves who it is. The shop shows its ID card. You, the customer, stay anonymous.",
                  FadeIn(cli), FadeIn(shop), GrowArrow(ar1), Succession(Wait(2.2), FadeIn(cert, shift=LEFT * 0.4)), run_time=4.4)
        q = T("but who is calling?", 30, ASK_C).move_to([0.2, -0.6, 0])
        self.beat("Between services, that isn't enough. The fraud check wants to know: who is calling me? Mutual TLS means both sides show an ID card. Each one learns who the other is.",
                  FadeIn(q), Succession(Wait(3.4), FadeIn(badge("caller's ID").move_to([0.2, -1.6, 0]), shift=RIGHT * 0.4)), run_time=5.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

        # ---------- 3. the building: istiod and two Pods
        mgr = VGroup(RoundedRectangle(corner_radius=0.15, width=3.4, height=1.15, stroke_color=MGR_C, stroke_width=3).set_fill(tint(MGR_C), 1))
        mgr.add(VGroup(T("istiod", 28, MGR_C), T("the badge office", 22, GREY_B)).arrange(DOWN, buff=0.08).move_to(mgr[0]))
        mgr.move_to([0, 2.55, 0])
        C = podbox("client", "hello-mesh", -4.3, -0.1)
        H = podbox("hello-devops", "hello-mesh", 4.3, -0.1)
        self.beat("Now the real building. Istio's control plane, a program called istiod, is the badge office. Here are two Pods in the namespace hello-mesh: a small client, and hello-devops.",
                  FadeIn(mgr), Succession(Wait(2.6), AnimationGroup(*[FadeIn(grp(g)) for g in (C, H)])), run_time=5.0)
        self.beat("Each Pod has an Envoy sidecar next to the app. The sidecar is the door reader.",
                  Indicate(C["px"], color=PRX_C), Indicate(H["px"], color=PRX_C), run_time=2.0)

        # the name on the badge
        sp = M("spiffe://cluster.local/ns/hello-mesh/sa/client", 26)
        parts = [(0, 9, GREY_B), (9, 22, GREY_B), (22, 36, ASK_C), (36, 46, BADGE_C)]
        for a, b, c in parts:
            VGroup(*sp[a:b]).set_color(c)
        sp.move_to([0, -2.35, 0])
        spl = VGroup(T("namespace", 22, ASK_C).next_to(VGroup(*sp[26:36]), DOWN, buff=0.15),
                     T("ServiceAccount", 22, BADGE_C).next_to(VGroup(*sp[40:46]), DOWN, buff=0.15))
        self.beat("What name goes on the badge? It comes from the Pod's ServiceAccount, the identity Kubernetes gives a program. Istio writes it in a standard shape called a SPIFFE ID.",
                  FadeIn(sp, shift=UP * 0.1), run_time=3.0)
        self.beat("This one reads: in the cluster's trust domain, namespace hello-mesh, ServiceAccount client. Two Pods that share a ServiceAccount share a name, which is why the lab gives each Deployment its own.",
                  LaggedStart(*[FadeIn(x) for x in spl], lag_ratio=0.5), run_time=3.0)
        self.play(FadeOut(VGroup(sp, spl)), run_time=0.5)

        # ---------- 4. four steps to a badge
        st = VGroup(T("1. make a key and a request", 24), T("2. send it, with the ServiceAccount token", 24),
                    T("3. istiod checks, signs for 24 hours", 24, MGR_C), T("4. hand it to Envoy, renew before expiry", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        st.move_to([0, -2.45, 0])
        up = Arrow(C["px"].get_top(), mgr[0].get_left() + DOWN * 0.2, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        down = Arrow(mgr[0].get_left() + DOWN * 0.45, C["px"].get_top() + RIGHT * 0.2, buff=0.12, stroke_width=3, color=BADGE_C, max_tip_length_to_length_ratio=0.08)
        self.beat("How does the client get its badge? Four steps. A small Istio agent next to Envoy makes a private key, the secret half, and a signing request.",
                  FadeIn(st[0]), Indicate(C["px"], color=PRX_C), run_time=2.6)
        self.beat("It sends the request to istiod, with the Pod's ServiceAccount token as proof of who it is.",
                  FadeIn(st[1]), GrowArrow(up), Succession(Wait(0.8), travel(up, GREY_B, 1.0)), run_time=2.6)
        self.beat("istiod checks the token, and signs a certificate valid for 24 hours.",
                  FadeIn(st[2]), Indicate(mgr[1][0], color=MGR_C), run_time=2.4)
        cb = badge_at(badge("client"), C)
        hb = badge_at(badge("hello-devops"), H)
        self.beat("The agent hands key and certificate to Envoy, and renews them before they expire. Nobody rotates a certificate by hand, and a stolen badge is only good for a day.",
                  FadeIn(st[3]), GrowArrow(down), Succession(Wait(1.0), AnimationGroup(FadeIn(cb, scale=1.4), FadeIn(hb, scale=1.4))), run_time=4.4)
        self.play(FadeOut(VGroup(up, down, st)), run_time=0.5)

        # ---------- 5. the handshake
        hs1 = Arrow(C["px"].get_right(), H["px"].get_left() + UP * 0.25, buff=0.15, stroke_width=3, color=BADGE_C, max_tip_length_to_length_ratio=0.04).shift(UP * 0.25)
        hs2 = Arrow(H["px"].get_left() + DOWN * 0.25, C["px"].get_right() + DOWN * 0.25, buff=0.15, stroke_width=3, color=BADGE_C, max_tip_length_to_length_ratio=0.04)
        hsl = T("mutual TLS handshake: both show a badge", 24, BADGE_C).move_to([0, 0.95, 0])
        self.beat("Now the client calls hello-devops. The app makes a plain call. Its sidecar opens a mutual TLS connection, and the two door readers show each other their badges.",
                  GrowArrow(hs1), Succession(Wait(1.6), GrowArrow(hs2)), Succession(Wait(2.6), FadeIn(hsl)), run_time=4.4)
        who = T("caller: client", 24, BADGE_C).move_to([0, -0.85, 0])
        self.beat("The receiving reader learns who is calling from the handshake itself, not from anything the app wrote. You can't fake it with a header.",
                  FadeIn(who, shift=UP * 0.1), Indicate(hb, color=BADGE_C), run_time=3.0)
        self.play(FadeOut(VGroup(hsl, who)), run_time=0.4)

        # ---------- 6. PERMISSIVE, STRICT, and the Monday mistake
        O = podbox("outside", "outside", -4.3, -2.5, sidecar=False, c=OUT_C, h=1.4)
        O["lab"].next_to(O["r"], LEFT, buff=0.2)
        O["ns"].next_to(O["r"], RIGHT, buff=0.15)
        self.beat("But not every caller lives in the mesh. Here's a Pod in another namespace, called outside. It has no sidecar, so no badge.",
                  FadeIn(grp(O)), run_time=2.2)
        mode = VGroup(T("PeerAuthentication:", 26, GREY_B), T("PERMISSIVE", 26, ASK_C)).arrange(RIGHT, buff=0.25).move_to([3.6, -2.3, 0])
        plain = Arrow(O["r"].get_right(), H["px"].get_bottom() + LEFT * 0.1, buff=0.12, stroke_width=3, color=OUT_C, max_tip_length_to_length_ratio=0.06)
        self.beat("Istio's default is PERMISSIVE. Each door accepts badges, and plain text too. So the outside Pod's call still works.",
                  FadeIn(mode), GrowArrow(plain), Succession(Wait(1.8), travel(plain, OUT_C, 1.0)), run_time=4.0)
        self.beat("Now our strict Monday. We apply a PeerAuthentication that says STRICT: mutual TLS only. What happens to the outside Pod's next call? Pause and guess.",
                  Transform(mode[1], T("STRICT", 26, BAD_C).move_to(mode[1], aligned_edge=LEFT)), run_time=3.0)
        self.pause([3.6, -3.05, 0])
        cut = tick(False, 0.25).move_to(plain.point_from_proportion(0.6))
        e56 = VGroup(T("curl exit code", 24, BAD_C), M("56", 26, BAD_C)).arrange(RIGHT, buff=0.15).move_to([0.2, -1.45, 0])
        self.beat("Refused. curl exits with code 56. The connection was cut before any HTTP answer arrived.",
                  travel(plain, OUT_C, 0.8), Succession(Wait(0.8), AnimationGroup(Create(cut), FadeIn(e56))), run_time=3.0)
        self.beat("Well. That looks exactly like a network fault, which is why it's so confusing at work. The cleaner is on the pavement, and the door reader has no idea a cleaner was ever expected.",
                  Indicate(O["app"], color=OUT_C), run_time=2.4)
        rule = T("Start PERMISSIVE. Check every caller. Then go STRICT.", 28, ASK_C).move_to([0, 1.0, 0])
        self.beat("So the rule: start PERMISSIVE, check every caller of the namespace, and only then switch to STRICT. Go strict after every caller has a badge.",
                  FadeIn(rule, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(rule, e56, cut, plain, mode, grp(O))), run_time=0.6)

        # ---------- 7. AuthorizationPolicy: the friendly ALLOW
        mon = podbox("prometheus", "monitoring", -4.3, -2.45, sidecar=True, c=PURPLE_M, h=1.6)
        mon["lab"].next_to(mon["r"], LEFT, buff=0.2)
        mon["ns"].next_to(mon["r"], RIGHT, buff=0.15)
        mb = badge_at(badge("prometheus", PURPLE_M), mon)
        self.beat("Badges are verified now, so we can decide who may open which door. That's an AuthorizationPolicy. A workload with no policy lets everyone in. Say a second caller, a monitoring Pod, also visits hello-devops.",
                  FadeIn(grp(mon)), FadeIn(mb), run_time=4.0)
        ma = Arrow(mon["px"].get_right(), H["px"].get_bottom() + RIGHT * 0.1, buff=0.12, stroke_width=3, color=PURPLE_M, max_tip_length_to_length_ratio=0.06)
        ca = Arrow(C["px"].get_right(), H["px"].get_left(), buff=0.15, stroke_width=3, color=BADGE_C, max_tip_length_to_length_ratio=0.04)
        self.play(FadeOut(hs1), FadeOut(hs2), run_time=0.3)
        self.beat("Both calls work.",
                  GrowArrow(ma), GrowArrow(ca), travel(ma, PURPLE_M, 0.9), travel(ca, BADGE_C, 0.9), run_time=1.6)
        pol = VGroup(T("ALLOW", 26, BADGE_C), T("from: client, GET only", 24)).arrange(RIGHT, buff=0.25).move_to([3.6, 1.35, 0])
        fit(pol, 5.4)
        self.beat("Now a team adds one friendly rule for hello-devops: ALLOW the client, for GET requests. They only meant to let the client in. What happens to the monitoring Pod? Pause and guess.",
                  FadeIn(pol, shift=DOWN * 0.1), run_time=3.0)
        self.pause([3.6, 0.75, 0])
        x2 = tick(False, 0.22).move_to(ma.point_from_proportion(0.7))
        r403 = M("403 RBAC: access denied", 24, BAD_C).move_to([1.0, -1.45, 0])
        self.beat("Locked out. Once any ALLOW policy selects a workload, every request no ALLOW rule matches gets 403, access denied.",
                  travel(ma, PURPLE_M, 0.8), Succession(Wait(0.8), AnimationGroup(Create(x2), FadeIn(r403))), travel(ca, BADGE_C, 0.8), run_time=3.4)
        rule2 = T("An ALLOW policy is also a deny for everyone it does not name.", 28, ASK_C).move_to([0, 1.0, 0])
        fit(rule2, 12.6)
        self.beat("That one friendly rule became a guest list, and the monitoring Pod isn't on it. An ALLOW policy is also a deny for everyone it doesn't name.",
                  FadeIn(rule2, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(rule2, r403, x2, ma, ca, pol, grp(mon), mb)), run_time=0.6)

        # ---------- 8. guardrails
        g1 = T("ambient mode: the node's ztunnel sees connections, not paths or methods", 24)
        g2 = T("so a policy with HTTP rules must sit on a waypoint, or it is treated as DENY", 24, BAD_C)
        g3 = T("Istio is one more big system: objects, upgrades, its own certificate authority", 24, GREY_B)
        gs = VGroup(g1, g2, g3).arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        fit(gs, 12.6).move_to([0, -2.3, 0])
        self.beat("Two honest limits. In ambient mode, the guard on each node, ztunnel, sees connections, not paths or methods. A policy with HTTP rules has to sit on a waypoint, an Envoy for that namespace. If it lands on ztunnel instead, Istio fails safe and treats it as a DENY.",
                  FadeIn(g1), Succession(Wait(4.0), FadeIn(g2)), run_time=6.0)
        self.beat("And Istio itself is one more big system to run, with its own objects, upgrades and certificate authority.",
                  FadeIn(g3), run_time=2.2)
        self.play(FadeOut(gs), run_time=0.5)

        # ---------- 9. moral, check
        mor = VGroup(T("A badge says who. A policy says who may.", 32, BADGE_C), T("Before you lock a door, list everyone who uses it.", 30, ASK_C)).arrange(DOWN, buff=0.25).move_to([0, -1.9, 0])
        self.beat("So the moral of the story. istiod prints every workload a one-day badge, and the door readers check it in the handshake. A badge says who. A policy says who may. And before you lock any door, list everyone who uses it.",
                  Write(mor[0]), Succession(Wait(5.0), FadeIn(mor[1])), run_time=7.0)
        self.play(FadeOut(mor), run_time=0.4)
        cq = VGroup(T("Quick check: you go STRICT, and a job in another namespace,", 26),
                    T("with no sidecar, now fails with a cut connection. Why?", 26)).arrange(DOWN, buff=0.12).move_to([0, -1.9, 0])
        self.beat("A quick check. You switch to STRICT, and a job in another namespace, with no sidecar, starts failing with a cut connection. Why? Pause and think.",
                  FadeIn(cq), run_time=2.4)
        self.pause([0, -3.0, 0], text="pause and think")
        ans = T("It has no badge, so its plain-text call is refused.", 28, BADGE_C).move_to([0, -3.0, 0])
        self.beat("It has no badge. STRICT accepts mutual TLS only, so its plain-text call is refused.",
                  FadeIn(ans), run_time=2.0)
        self.beat("Next, lighter meshes, and the question this one leaves open. Does your team need a mesh at all?",
                  FadeOut(VGroup(cq, ans)), run_time=1.4)
        self.wait(1.0)
