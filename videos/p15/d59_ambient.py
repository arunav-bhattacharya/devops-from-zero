import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bistioctl\b", "istio control"), (r"\bistiod\b", "istio D"), (r"\bHBONE\b", "H-bone"),
            (r"\bztunnels?\b", lambda m: "Z tunnel" + ("s" if m.group(0).endswith("s") else "")),
            (r"\bL4\b", "L four"), (r"\bL7\b", "L seven"), (r"\bCNI\b", "C N I"), (r"\bRust\b", "rust")])

ENV = GOLD_M
ZT = TEAL_M
NODE_X, NODE_Y, POD_Y, ZT_Y = 3.85, -0.85, -0.1, -2.45
POD_DX = 1.88


def dark(c, a=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def polyline(*pts, color=YELLOW_M, sw=2):
    return VMobject(stroke_color=color, stroke_width=sw).set_points_as_corners([np.array([x, y, 0]) for x, y in pts])


def ride(pts, color=YELLOW_M, run_time=1.4):
    """A dot that runs along a bent path."""
    path = polyline(*pts)
    d = Dot(radius=0.09, color=color).move_to(path.get_start())
    return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=smooth, run_time=run_time), FadeOut(d, run_time=0.15))


def lock(color=GREEN_M, s=1.0):
    body = RoundedRectangle(corner_radius=0.05, width=0.42, height=0.32, stroke_color=color, stroke_width=3).set_fill(BLACK, 1)
    shackle = Arc(radius=0.14, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(body, UP, buff=0)
    return VGroup(shackle, body).scale(s)


def pulse(rect, w=7, back=None, rt=0.45):
    """Thicken a box outline and bring it back: a highlight that never hides the label."""
    b = back if back is not None else rect.get_stroke_width()
    return Succession(rect.animate(run_time=rt).set_stroke(width=w), rect.animate(run_time=rt).set_stroke(width=b))


def pod(name, x, color=BLUE_M):
    """A sidecar-mode Pod: the app's name on top, an Envoy container below."""
    r = RoundedRectangle(corner_radius=0.14, width=1.75, height=1.9, stroke_color=color, stroke_width=2.5).set_fill(dark(color, 0.10), 1)
    r.move_to([x, POD_Y, 0])
    t = T(name, 20).move_to([x, POD_Y + 0.45, 0]).set_z_index(3)
    e = box("Envoy", ENV, w=1.45, h=0.6, size=22).move_to([x, POD_Y - 0.45, 0])
    e[1].set_z_index(3)
    return VGroup(r, t, e)


class D59Ambient(VoiceScene):
    def construct(self):
        self.title_card("Istio ambient mode", "a ztunnel on every node, a waypoint only where you need one")

        # ---------- A. sidecar mode, as on Day 58
        nodes, nlabs = VGroup(), VGroup()
        for i, sx in enumerate((-1, 1)):
            n = RoundedRectangle(corner_radius=0.2, width=5.85, height=4.7, stroke_color=GREY_B, stroke_width=2).move_to([sx * NODE_X, NODE_Y, 0])
            nodes.add(n)
            nlabs.add(T(f"node {i + 1}", 22, GREY_B).next_to(n, DOWN, buff=0.15))
        names = [["client", "orders", "search"], ["hello-devops", "canary", "web"]]
        pods = []
        for side, sx in enumerate((-1, 1)):
            for k, nm in enumerate(names[side]):
                pods.append(pod(nm, sx * NODE_X + (k - 1) * POD_DX, TEAL_M if side else BLUE_M))
        pods = VGroup(*pods)
        envs = VGroup(*[p[2] for p in pods])
        self.beat("On Day 58, every Pod got its own Envoy. Istio calls that sidecar mode. It is the original design, used since 2017.",
                  LaggedStart(Create(nodes[0]), Create(nodes[1]), lag_ratio=0.3), FadeIn(nlabs),
                  LaggedStart(*[AnimationGroup(FadeIn(p[0]), Write(p[1])) for p in pods], lag_ratio=0.12),
                  Succession(Wait(2.2), LaggedStart(*[GrowFromCenter(e) for e in envs], lag_ratio=0.12)), run_time=4.6)

        cx, hx = pods[0][0].get_center()[0], pods[3][0].get_center()[0]
        side_path = [(cx, POD_Y + 0.3), (cx, POD_Y - 0.45), (cx, -1.6), (hx, -1.6), (hx, POD_Y - 0.45), (hx, POD_Y + 0.3)]
        wire = Line([cx, -1.6, 0], [hx, -1.6, 0], stroke_width=2, color=GREY_D)
        mt = T("mTLS", 20, GREEN_M).move_to([0, -1.32, 0])
        self.beat("Every call passes through two of them, the caller's and the receiver's. Each proxy handles both L4 and L7, so every feature works everywhere.",
                  Create(wire), FadeIn(mt),
                  Succession(Wait(0.6), ride(side_path, run_time=2.4),
                             AnimationGroup(pulse(envs[0][0]), pulse(envs[3][0]))),
                  run_time=4.4)

        cnt = T("6 Pods  →  6 Envoys", 30, ENV).move_to([0, 2.65, 0])
        self.beat("But the cost grows with the mesh. Each sidecar is sized for its own Pod's busiest moment.",
                  FadeIn(cnt, shift=DOWN * 0.1),
                  Succession(Wait(1.6), LaggedStart(*[e[0].animate.set_stroke(width=6) for e in envs], lag_ratio=0.1)), run_time=3.4)
        cnt2 = T("60 Pods  →  60 Envoys", 30, ENV).move_to(cnt)
        cnt3 = T("600 Pods  →  600 Envoys", 30, ENV).move_to(cnt)
        self.beat("Add Pods, and you add Envoys, one for every Pod.",
                  Succession(Transform(cnt, cnt2, run_time=0.8), Wait(0.5), Transform(cnt, cnt3, run_time=0.8)), run_time=2.4)
        rst = T("join or upgrade  =  restart every Pod", 28, RED_M).move_to(cnt)
        self.beat("And joining the mesh, or upgrading it, means restarting every Pod.",
                  FadeOut(cnt, shift=UP * 0.1), FadeIn(rst, shift=DOWN * 0.1),
                  LaggedStart(*[Succession(p.animate(run_time=0.35).set_opacity(0.15), p.animate(run_time=0.35).set_opacity(1)) for p in pods], lag_ratio=0.15),
                  run_time=3.0)
        for e in envs:
            e[0].set_stroke(width=3)

        # ---------- B. ambient mode: ztunnel per node
        two = T("ambient mode: two layers", 30, ZT).move_to([0, 2.65, 0])
        ga = T("GA since Istio 1.24, November 2024", 22, GREY_B).next_to(two, DOWN, buff=0.18)
        short = VGroup()
        for p in pods:
            r = RoundedRectangle(corner_radius=0.14, width=1.75, height=1.0, stroke_color=p[0].get_stroke_color(), stroke_width=2.5).set_fill(p[0].get_fill_color(), 1)
            short.add(r.move_to(p[0]))
        self.beat("Ambient mode splits that work into two layers. It became generally available in Istio 1.24, in November 2024.",
                  FadeOut(rst), FadeOut(wire), FadeOut(mt), FadeIn(two, shift=DOWN * 0.1),
                  LaggedStart(*[FadeOut(e, scale=0.6) for e in envs], lag_ratio=0.08),
                  *[Transform(p[0], s) for p, s in zip(pods, short)], *[p[1].animate.move_to(s) for p, s in zip(pods, short)],
                  Succession(Wait(2.4), FadeIn(ga, shift=DOWN * 0.1)), run_time=4.6)
        apps = VGroup(*[VGroup(p[0], p[1]) for p in pods])

        zts = VGroup(*[box("ztunnel", ZT, w=5.2, h=0.75, size=26).move_to([sx * NODE_X, ZT_Y, 0]) for sx in (-1, 1)])
        for z in zts:
            z[1].set_z_index(3)
        self.beat("The first layer is ztunnel, a small proxy written in Rust. It runs once per node, not once per Pod.",
                  FadeOut(ga), LaggedStart(*[AnimationGroup(DrawBorderThenFill(z[0]), Write(z[1])) for z in zts], lag_ratio=0.3), run_time=2.8)
        redir = VGroup(*[DashedLine(a[0].get_bottom() + DOWN * 0.06, [a[0].get_center()[0], ZT_Y + 0.42, 0], dash_length=0.08,
                                    stroke_width=2.5, color=ZT) for a in apps])
        cni = T("redirect rules from the Istio CNI node agent", 22, ZT).move_to([0, 1.85, 0])
        self.beat("When a Pod joins, the Istio CNI node agent writes redirect rules inside the Pod's network. They send its traffic to the ztunnel on the same node.",
                  FadeIn(cni, shift=DOWN * 0.1), Succession(Wait(2.4), LaggedStart(*[Create(r) for r in redir], lag_ratio=0.12)), run_time=5.0)

        jobs = VGroup(chip("mTLS", GREEN_M, 24), chip("identity", GREEN_M, 24), chip("L4 policy", GREEN_M, 24)).arrange(RIGHT, buff=0.3)
        nohttp = chip("HTTP parsing", RED_M, 24)
        row = VGroup(jobs, nohttp).arrange(RIGHT, buff=0.7).move_to([0, 1.85, 0])
        cross = Line(nohttp.get_corner(DL) + LEFT * 0.08, nohttp.get_corner(UR) + RIGHT * 0.08, stroke_color=RED_M, stroke_width=4)
        self.beat("ztunnel encrypts and authenticates the traffic of every Pod on its node, and enforces L4 rules. But it never parses HTTP.",
                  FadeOut(cni), FadeOut(two),
                  LaggedStart(*[FadeIn(j, shift=UP * 0.1) for j in jobs], lag_ratio=0.3),
                  Succession(Wait(3.2), FadeIn(nohttp, shift=UP * 0.1), Create(cross)), run_time=5.4)
        keys = VGroup(*[chip("certs for this node's Pods", GREEN_M, 20).next_to(z, UP, buff=0.12) for z in zts])
        self.beat("Each ztunnel holds certificates only for the Pods on its own node. An app container never sees a key.",
                  FadeOut(redir), LaggedStart(*[FadeIn(k, shift=UP * 0.1) for k in keys], lag_ratio=0.3), run_time=2.4)

        # ---------- one call, with no waypoint
        self.play(FadeOut(keys), FadeOut(VGroup(jobs, nohttp, cross)), run_time=0.6)
        zl, zr = zts[0][0].get_right()[0], zts[1][0].get_left()[0]
        a_out = [(cx, POD_Y - 0.5), (cx, ZT_Y + 0.38)]
        self.beat("Follow one call, from client to hello-devops. The client opens a plain TCP connection. It has no idea a mesh exists.",
                  apps[0][0].animate.set_stroke(width=6), Succession(Wait(2.6), ride(a_out, run_time=1.0)), run_time=4.4)
        tube = Line([zl, ZT_Y, 0], [zr, ZT_Y, 0], stroke_color=GREEN_M, stroke_width=7)
        hb = T("HBONE", 22, GREEN_M).move_to([0, ZT_Y + 0.42, 0])
        hp = M(":15008", 20, GREEN_M).move_to([0, ZT_Y - 0.4, 0])
        lk = lock(s=0.85).move_to([0, -3.38, 0])
        self.beat("ztunnel wraps the bytes in a tunnel called HBONE, short for HTTP-Based Overlay Network Environment. It is mutual TLS, on port 15008.",
                  apps[0][0].animate.set_stroke(width=2.5), Create(tube), Succession(Wait(1.2), AnimationGroup(FadeIn(hb), FadeIn(hp))),
                  Succession(Wait(4.0), FadeIn(lk, scale=0.6)), run_time=6.0)
        cert = chip("sa/client", GREEN_M, 20, mono=True).move_to([cx, ZT_Y + 0.85, 0])
        self.beat("ztunnel presents the client's certificate. So the other side learns who is calling from the handshake itself.",
                  FadeIn(cert, shift=UP * 0.1),
                  Succession(Wait(1.4), cert.animate(run_time=1.4).move_to([hx, ZT_Y + 0.85, 0])), run_time=3.6)
        a_in = [(hx, ZT_Y + 0.38), (hx, POD_Y - 0.5)]
        self.beat("The ztunnel on the other node checks its L4 policy, unwraps the tunnel, and delivers plain TCP to the app.",
                  pulse(zts[1][0]), Succession(Wait(2.4), ride(a_in, run_time=1.0), pulse(apps[3][0])),
                  run_time=4.4)
        whole = a_out + [(cx, ZT_Y), (hx, ZT_Y)] + a_in
        cheap = T("the cheap path: encryption, identity, L4 policy", 26, GREEN_M).move_to([0, 2.65, 0])
        self.beat("That is the cheap path. Encryption, identity and L4 policy, with no HTTP parsing anywhere.",
                  FadeOut(cert), FadeIn(cheap, shift=DOWN * 0.1), Succession(Wait(0.6), ride(whole, GREEN_M, run_time=2.0)), run_time=3.6)

        # ---------- C. a waypoint, only where you need L7
        need = VGroup(chip("90 / 10 canary split", ENV, 22), chip("header match", ENV, 22), chip("rules on paths and methods", ENV, 22)).arrange(RIGHT, buff=0.3)
        need.move_to([0, 2.65, 0])
        self.beat("But some features need HTTP. A canary split by weight, a match on a header, a rule about paths or methods.",
                  FadeOut(cheap), LaggedStart(*[FadeIn(n, shift=DOWN * 0.1) for n in need], lag_ratio=0.4), run_time=3.4)
        wp = box("waypoint", ENV, w=2.4, h=0.8, size=26).move_to([0, 2.65, 0])
        wp[1].set_z_index(3)
        wpl = T("an Envoy, its own Deployment", 22, ENV).next_to(wp, RIGHT, buff=0.3)
        self.beat("For those, you add a waypoint. It is a full Envoy that runs as its own Deployment, usually one per namespace.",
                  FadeOut(need, shift=UP * 0.1), Succession(Wait(0.4), AnimationGroup(GrowFromCenter(wp), FadeIn(wpl))), run_time=3.6)
        wy = wp[0].get_bottom()[1]
        up_l = polyline((zl, ZT_Y), (-0.45, ZT_Y), (-0.45, wy), color=ENV, sw=4)
        dn_r = polyline((0.45, wy), (0.45, ZT_Y), (zr, ZT_Y), color=ENV, sw=4)
        to_wp = a_out + [(cx, ZT_Y), (-0.45, ZT_Y), (-0.45, wy)]
        self.beat("Now ztunnel sends the bytes to the waypoint instead of straight to a Pod, still inside HBONE.",
                  tube.animate.set_stroke(opacity=0.2), FadeOut(VGroup(hb, hp, lk)), Create(up_l), Create(dn_r),
                  Succession(Wait(1.6), ride(to_wp, run_time=1.8)), run_time=4.4)
        s90 = DashedLine([0.6, 2.25, 0], [hx - 0.1, 0.55, 0], dash_length=0.08, stroke_width=2, color=ENV)
        s10 = DashedLine([1.2, 2.5, 0], [pods[4][0].get_center()[0], 0.55, 0], dash_length=0.08, stroke_width=2, color=ENV)
        w90 = T("90", 22, ENV).move_to(Line([0.6, 2.25, 0], [hx - 0.1, 0.55, 0]).point_from_proportion(0.35) + RIGHT * 0.35)
        w10 = T("10", 22, ENV).move_to(Line([1.2, 2.5, 0], [pods[4][0].get_center()[0], 0.55, 0]).point_from_proportion(0.35) + RIGHT * 0.35)
        self.beat("The waypoint parses HTTP. It applies the route split and the AuthorizationPolicy, and picks a hello-devops Pod.",
                  FadeOut(wpl), pulse(wp[0]),
                  Succession(Wait(1.8), AnimationGroup(Create(s90), Create(s10), FadeIn(w90), FadeIn(w10))), run_time=4.4)
        from_wp = [(0.45, wy), (0.45, ZT_Y), (hx, ZT_Y)] + a_in
        self.beat("Then it opens a new HBONE tunnel, to the ztunnel on that Pod's node, which delivers it.",
                  FadeOut(VGroup(s90, s10, w90, w10)), Succession(Wait(0.4), ride(from_wp, run_time=2.0), pulse(apps[3][0])),
                  run_time=3.6)
        pay = T("HTTP parsing only here", 24, ENV).next_to(wp, RIGHT, buff=0.3)
        self.beat("Most calls only need encryption and identity, which are cheap. So you pay for HTTP parsing only where you add a waypoint.",
                  FadeIn(pay, shift=UP * 0.1), Succession(Wait(1.2), ride(whole, GREEN_M, run_time=1.6), ride(to_wp + from_wp, ENV, run_time=2.2)),
                  run_time=5.6)

        # ---------- D. the latency numbers
        stage = VGroup(nodes, nlabs, apps, zts, tube, up_l, dn_r, wp, pay)
        self.play(FadeOut(stage), run_time=0.8)
        lh = T("Istio's latency tests, p90 to p99, per call", 28).move_to([0, 3.0, 0])
        x0, unit = -2.2, 7.0  # 1 ms = 7 units
        axis = Line([x0, -2.0, 0], [x0 + unit * 1.0, -2.0, 0], stroke_color=GREY_B, stroke_width=2)
        ticks = VGroup()
        for v in (0, 0.25, 0.5, 0.75, 1.0):
            ticks.add(Line([x0 + unit * v, -2.0, 0], [x0 + unit * v, -2.12, 0], stroke_color=GREY_B, stroke_width=2))
            ticks.add(T(f"{v:g} ms", 20, GREY_B).move_to([x0 + unit * v, -2.42, 0]))
        rows = [("sidecars", 0.63, 0.88, ENV, 1.5), ("ztunnel alone", 0.16, 0.20, GREEN_M, 0.3), ("through a waypoint", 0.40, 0.50, BLUE_M, -0.9)]
        bars = []
        for name, a, b, col, y in rows:
            lab = T(name, 26, col).move_to([x0 - 0.3, y, 0], aligned_edge=RIGHT)
            base = Rectangle(width=unit * a, height=0.5, stroke_width=0).set_fill(col, 0.75).move_to([x0 + unit * a / 2, y, 0])
            ext = Rectangle(width=unit * (b - a), height=0.5, stroke_color=col, stroke_width=2).set_fill(col, 0.25).move_to([x0 + unit * (a + b) / 2, y, 0])
            val = T(f"{a:.2f} to {b:.2f} ms", 22, col).next_to(ext, RIGHT, buff=0.2)
            bars.append(VGroup(lab, base, ext, val))
        self.beat("Istio's page comparing the two modes quotes its latency tests, at p90 and p99.",
                  FadeIn(lh), Create(axis), FadeIn(ticks), run_time=2.4)
        self.beat("With sidecars, 0.63 to 0.88 milliseconds per call.",
                  FadeIn(bars[0][0]), GrowFromEdge(bars[0][1], LEFT), Succession(Wait(1.0), AnimationGroup(GrowFromEdge(bars[0][2], LEFT), FadeIn(bars[0][3]))), run_time=2.8)
        self.beat("With ztunnel alone, 0.16 to 0.20.",
                  FadeIn(bars[1][0]), GrowFromEdge(bars[1][1], LEFT), Succession(Wait(0.6), AnimationGroup(GrowFromEdge(bars[1][2], LEFT), FadeIn(bars[1][3]))), run_time=2.2)
        self.beat("And through a waypoint, 0.40 to 0.50.",
                  FadeIn(bars[2][0]), GrowFromEdge(bars[2][1], LEFT), Succession(Wait(0.6), AnimationGroup(GrowFromEdge(bars[2][2], LEFT), FadeIn(bars[2][3]))), run_time=2.2)
        chart = VGroup(lh, axis, ticks, *bars)

        # ---------- E. how a namespace joins
        self.play(FadeOut(chart), run_time=0.7)
        inst = M("istioctl install --set profile=ambient", 24).move_to([0, 3.15, 0])
        parts = VGroup(chip("istiod", BLUE_M, 22), chip("ztunnel", ZT, 22), chip("Istio CNI node agent", ZT, 22)).arrange(RIGHT, buff=0.3).move_to([0, 2.3, 0])
        self.beat("To use ambient mode, install Istio with the ambient profile. It brings istiod, ztunnel, and the Istio CNI node agent.",
                  Write(inst), Succession(Wait(2.2), LaggedStart(*[FadeIn(p, shift=DOWN * 0.1) for p in parts], lag_ratio=0.4)), run_time=4.6)

        def ns_box(x, title, col):
            fr = RoundedRectangle(corner_radius=0.18, width=6.3, height=3.0, stroke_color=col, stroke_width=2.5).move_to([x, -0.9, 0])
            t = T(title, 24, col).next_to(fr, UP, buff=0.14)
            ps = VGroup(*[RoundedRectangle(corner_radius=0.12, width=1.75, height=1.0, stroke_color=TEAL_M, stroke_width=2.5).set_fill(dark(TEAL_M, 0.10), 1)
                          for _ in range(3)]).arrange(RIGHT, buff=0.25).move_to([x, -0.55, 0])
            pl = VGroup(*[T("hello-devops", 20).move_to(p).set_z_index(3) for p in ps])
            return fr, t, ps, pl
        lfr, lt, lps, lpl = ns_box(-3.5, "sidecar mode", ENV)
        rfr, rt, rps, rpl = ns_box(3.5, "ambient mode", ZT)
        ll = M("istio-injection=enabled", 22, ENV).move_to([-3.5, -2.08, 0])
        rl = M("istio.io/dataplane-mode=ambient", 22, ZT).move_to([3.5, -2.08, 0])
        self.beat("Then decide how each namespace joins. Say namespace hello-mesh already has Pods running. Here it is, joining each way.",
                  FadeOut(parts), inst.animate.set_opacity(0.4), Create(lfr), Create(rfr), FadeIn(lt), FadeIn(rt),
                  LaggedStart(*[AnimationGroup(FadeIn(p), Write(t)) for p, t in zip(list(lps) + list(rps), list(lpl) + list(rpl))], lag_ratio=0.1), run_time=4.0)
        side_envs = VGroup(*[box("Envoy", ENV, w=1.2, h=0.45, size=20).next_to(p, DOWN, buff=0.12) for p in lps])
        self.beat("In sidecar mode you label the namespace istio-injection equals enabled. Nothing happens to the running Pods.",
                  Write(ll), Succession(Wait(2.6), Wiggle(lps, scale_value=1.04)), run_time=4.0)
        self.beat("Only Pods created after the label get a sidecar, so you restart your Deployments.",
                  Succession(Wait(1.6), LaggedStart(*[Succession(p.animate(run_time=0.35).set_opacity(0.1), p.animate(run_time=0.35).set_opacity(1)) for p in lps], lag_ratio=0.25),
                             LaggedStart(*[GrowFromCenter(e) for e in side_envs], lag_ratio=0.2)), run_time=4.0)
        self.beat("In ambient mode you label it istio.io/dataplane-mode equals ambient. ztunnel takes over the running Pods at once.",
                  Write(rl), Succession(Wait(3.0), AnimationGroup(*[p.animate.set_stroke(GREEN_M, width=4) for p in rps])), run_time=4.6)
        notes = VGroup(*[T(s, 20, GREEN_M) for s in ("no restart, no extra container", "Pod spec unchanged")]).arrange(DOWN, buff=0.1).move_to([3.5, -1.43, 0])
        self.beat("No restart, no extra container. The node agent adds redirect rules inside each running Pod's network, and the Pod spec never changes.",
                  LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in notes], lag_ratio=0.5), run_time=3.6)
        wcmd = M("istioctl waypoint apply -n hello-mesh --enroll-namespace", 22, ENV).move_to([0, -3.15, 0])
        self.beat("When that namespace needs HTTP features, one istioctl command deploys a waypoint, and sends the namespace's traffic through it.",
                  FadeOut(inst), Write(wcmd), run_time=3.0)
        both = T("never both labels on one namespace: sidecar mode would win", 24, RED_M).move_to([0, 2.65, 0])
        self.beat("One rule. Never put both labels on one namespace. If you do, sidecar mode wins for those Pods.",
                  FadeIn(both, shift=DOWN * 0.1), Succession(Wait(1.6), Indicate(ll, color=RED_M), Indicate(rl, color=RED_M)), run_time=3.6)

        # ---------- recap
        self.play(FadeOut(VGroup(lfr, lt, lps, lpl, side_envs, rfr, rt, rps, rpl, ll, rl, notes, wcmd, both)), run_time=0.8)
        recap = VGroup(T("sidecar mode: an Envoy in every Pod", 28, ENV),
                       T("ambient mode: one ztunnel per node, L4 and mTLS over HBONE", 28, ZT),
                       T("plus a waypoint, only where you need L7", 28, ENV)).arrange(DOWN, buff=0.4).move_to([0, 0.2, 0])
        self.beat("Sidecar mode puts an Envoy in every Pod. Ambient mode puts one ztunnel on each node, for L4 and mutual TLS over HBONE, and adds a waypoint only where you need L7.",
                  Write(recap[0]), Succession(Wait(1.8), Write(recap[1]), Wait(1.8), Write(recap[2])), run_time=8.0)
        self.wait(1.0)
