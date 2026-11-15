import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bGatewayClass\b", "gateway class"), (r"\bHTTPRoutes?\b", lambda m: "H T T P route" + ("s" if m.group(0).endswith("s") else "")),
            (r"\bingress-nginx\b", "ingress engine X"), (r"\bx-canary\b", "X canary"), (r"\bNodePort\b", "node port"),
            (r"\bLoadBalancer\b", "load balancer"), (r"\bPROGRAMMED\b", "programmed")])

XG = -1.3          # column of the Gateway, the controller and the proxy
PY = -1.3          # the data path row
SX, SY = (4.3, (-0.35, -2.45))   # Services


def tint(c, k=0.15):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def obj(kind, name, color, pos, w=3.2):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=0.95, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    g = VGroup(T(kind, 24, color), M(name, 20)).arrange(DOWN, buff=0.1)
    return VGroup(r, g.move_to(r)).move_to(pos)


def svc(name, color, pos):
    r = RoundedRectangle(corner_radius=0.12, width=3.1, height=1.05, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    n = M(name, 22)
    c = T("requests: 0", 22, GREY_B)
    VGroup(n, c).arrange(DOWN, buff=0.12)
    g = VGroup(r, VGroup(n, c).move_to(r)).move_to(pos)
    return g


def polyline(*pts, color=YELLOW_M):
    return VMobject(stroke_color=color, stroke_width=2).set_points_as_corners([np.array([x, y, 0]) for x, y in pts])


def ride(pts, color=YELLOW_M, run_time=1.2):
    path = polyline(*pts)
    d = Dot(radius=0.09, color=color).move_to(path.get_start())
    return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=smooth, run_time=run_time), FadeOut(d, run_time=0.12))


class D44Gateway(VoiceScene):
    def steps(self, text, *plays):
        path, dur = voice(text)
        self._cue(text, dur)
        self.add_sound(path)
        t0 = self.renderer.time
        for rt, *anims in plays:
            self.play(*anims, run_time=rt)
        left = dur - (self.renderer.time - t0)
        if left > 0.02:
            self.wait(left)
        self.wait(0.25)

    def count(self, s, n):
        new = T(f"requests: {n}", 22, GREY_B).move_to(s[1][1])
        return Transform(s[1][1], new)

    def construct(self):
        self.title_card("Gateway API: objects that program a proxy", "how a request finds its Service, and how a canary gets 10%")

        # ---------- 1. the problem: a Service only sees connections
        cli = box("curl", GREY_B, w=1.8, h=0.8, size=26).move_to([-5.6, PY, 0])
        dev = svc("hello-devops", TEAL_M, [SX, SY[0], 0])
        a0 = Arrow(cli.get_right(), dev.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.04)
        pf = T("NodePort or port-forward", 22, GREY_B).next_to(a0, DOWN, buff=0.15).shift(LEFT * 0.6)
        self.beat("So far you reached hello-devops with a NodePort, or with kubectl port-forward. Both are fine on a laptop. Neither is how real users arrive.",
                  FadeIn(cli), FadeIn(dev), GrowArrow(a0), FadeIn(pf), run_time=2.4)
        wants = VGroup(*[chip(t, BLUE_M, 22) for t in ("one entry point", "route by host and path", "TLS in one place", "gradual releases")])
        wants.arrange(RIGHT, buff=0.25).move_to([0, 2.9, 0])
        fit(wants, 13.0)
        self.beat("For traffic from outside, you usually want one entry point for many apps, routing by host name and path, TLS in one place, and gradual releases.",
                  LaggedStart(*[FadeIn(w, shift=0.15 * DOWN) for w in wants], lag_ratio=0.45), run_time=4.4)
        lb = box("LoadBalancer Service", GREY_B, w=3.4, h=0.9, size=24).move_to([XG, PY, 0])
        a1 = Arrow(cli.get_right(), lb.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        a2 = Arrow(lb.get_right(), dev.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        self.beat("A Service of type LoadBalancer gives you an address. But it works with connections, at layer 4.",
                  FadeOut(wants), FadeOut(pf), ReplacementTransform(a0, VGroup(a1, a2)), FadeIn(lb), run_time=1.8)
        req = VGroup(M("GET /api", 22, YELLOW_M), M("x-canary: always", 20, YELLOW_M)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        reqbox = SurroundingRectangle(req, buff=0.15, color=YELLOW_M, stroke_width=2, corner_radius=0.08).set_fill(BLACK, 1)
        pkt = VGroup(reqbox, req).move_to([-5.6, 0.25, 0])
        blind = T("sees only: a connection to port 80", 24, RED_M).move_to([XG, 0.0, 0])
        self.steps("The request carries a path and headers. A layer 4 Service never looks at them. To it, this is only a connection.",
                   (0.8, FadeIn(pkt, shift=0.1 * DOWN)), (1.2, pkt.animate.move_to([XG - 3.0, 0.25, 0])),
                   (0.8, pkt.animate.set_opacity(0.35), FadeIn(blind, shift=0.1 * UP)))
        prox = box("Envoy proxy", GOLD_M, w=2.8, h=0.9, size=26).move_to([XG, PY, 0])
        l7 = T("reads HTTP: layer 7", 22, GOLD_M).next_to(prox, DOWN, buff=0.2)
        self.beat("Routing on those needs a proxy that understands HTTP, at layer 7. Plus a Kubernetes object that tells the proxy what to do.",
                  FadeOut(blind), FadeOut(pkt), ReplacementTransform(lb, prox), FadeIn(l7), run_time=2.0)

        # ---------- 2. Ingress, briefly
        ing = obj("Ingress", "hosts, paths, TLS", GREY_B, [XG, 2.85, 0], w=3.4)
        ann = T("everything else: annotations, different per controller", 22, GREY_B).move_to([XG + 1.5, 1.85, 0])
        self.beat("The older API for this is Ingress. It was small on purpose. Hosts, paths and TLS. Everything else went into annotations, which each controller defined its own way.",
                  FadeIn(ing), Succession(Wait(3.2), FadeIn(ann, shift=0.1 * DOWN)), run_time=4.4)
        fz = chip("frozen", RED_M, 22).next_to(ing, RIGHT, buff=0.3)
        ret = T("ingress-nginx retired March 24, 2026", 22, RED_M).next_to(fz, RIGHT, buff=0.3)
        self.beat("The Ingress API is now frozen. And ingress-nginx, the most popular controller, was retired on March 24, 2026. The newer API is the Gateway API.",
                  FadeOut(ann), FadeIn(fz), Succession(Wait(1.6), FadeIn(ret)), run_time=3.2)
        self.play(FadeOut(VGroup(ing, fz, ret)), run_time=0.5)

        # ---------- 3. one object per role
        gc = obj("GatewayClass", "eg", PURPLE_M, [-5.0, 2.85, 0], w=2.9)
        gw = obj("Gateway", "hello-gateway", BLUE_M, [XG, 2.85, 0])
        hr = obj("HTTPRoute", "hello-devops", GREEN_M, [3.5, 2.85, 0])
        own = VGroup(T("platform team", 20, GREY_B).next_to(gc, DOWN, buff=0.15),
                     T("HTTP on port 80", 20, GREY_B).next_to(gw, DOWN, buff=0.15),
                     T("app team", 20, GREY_B).next_to(hr, DOWN, buff=0.15))
        self.steps("It splits the job by who owns what. A GatewayClass says which controller handles it. The platform team creates it once per cluster.",
                   (1.0, FadeIn(gc, shift=0.1 * DOWN)), (3.0, Wait(3.0)), (0.8, FadeIn(own[0])))
        self.beat("A Gateway is an entry point, with listeners, such as HTTP on port 80.",
                  FadeIn(gw, shift=0.1 * DOWN), Succession(Wait(1.6), FadeIn(own[1])), run_time=2.4)
        self.beat("And an HTTPRoute holds the routing rules for one app. App teams own these, and attach them to a Gateway.",
                  FadeIn(hr, shift=0.1 * DOWN), Succession(Wait(1.4), FadeIn(own[2])), run_time=2.4)

        # ---------- 4. kubectl apply -k: the controller reads, the proxy routes
        ctl = box("Envoy Gateway controller", GREY_B, w=3.9, h=0.8, size=24).move_to([XG, 0.65, 0])
        self.play(FadeOut(own), FadeOut(l7), run_time=0.5)
        wl = VGroup(link(gc, ctl, GREY_B), link(gw, ctl, GREY_B), link(hr, ctl, GREY_B))
        self.beat("Now apply the lab's folder. Envoy Gateway's controller watches these objects.",
                  FadeIn(ctl), Create(wl), prox.animate.set_opacity(0.3), run_time=1.6)
        acc = VGroup(tick(True, 0.15), T("accepted", 20, GREEN_M)).arrange(RIGHT, buff=0.12).next_to(gc, DOWN, buff=0.15)
        self.steps("Step one. The class eg names the controller. Envoy Gateway sees its own name, and accepts the class.",
                   (1.0, Indicate(gc[1][1], color=PURPLE_M)), (1.4, travel(Line(wl[0].get_start(), wl[0].get_end()), PURPLE_M, 1.2)), (0.8, FadeIn(acc)))
        made = T("in envoy-gateway-system", 20, GOLD_M).next_to(prox, DOWN, buff=0.2)
        sett = Arrow(ctl.get_bottom(), prox.get_top(), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.18)
        self.steps("Step two. The Gateway uses class eg. So the controller creates an Envoy proxy, a Deployment and a Service, for it.",
                   (1.0, Indicate(gw[1][0], color=BLUE_M)), (1.2, travel(Line(wl[1].get_start(), wl[1].get_end()), BLUE_M, 1.0)), (1.2, prox.animate.set_opacity(1), FadeIn(made)))
        self.steps("Step three. The HTTPRoute attaches to hello-gateway, and points at the hello-devops Service.",
                   (1.2, travel(Line(wl[2].get_start(), wl[2].get_end()), GREEN_M, 1.2)), (1.0, Indicate(dev[0], color=TEAL_M)))
        st = T("settings", 20, GOLD_M).next_to(sett, RIGHT, buff=0.12)
        self.steps("Step four. The controller turns the route into Envoy settings, and sends them to the proxy. Now it starts forwarding.",
                   (1.0, GrowArrow(sett), FadeIn(st)), (1.2, travel(sett, GOLD_M, 1.0)), (0.6, Indicate(prox[1], color=GOLD_M)))
        rpath = [(cli.get_right()[0], PY), (prox.get_left()[0], PY), (prox.get_right()[0], PY), (dev.get_left()[0], SY[0])]
        self.steps("A request now goes from curl, to Envoy, to hello-devops. Look where the controller is. It never handles a request. It only watches objects and writes settings.",
                   (1.8, ride(rpath, YELLOW_M, 1.8)), (0.4, self.count(dev, 1)), (1.6, ride(rpath, YELLOW_M, 1.6)), (0.4, self.count(dev, 2)),
                   (1.0, Indicate(ctl[1], color=GREY_B)))
        pfl = T("on kind: port-forward", 20, GREY_B).next_to(a1, DOWN, buff=0.15)
        self.beat("On kind there is no cloud, so the proxy's Service never gets a real address. The routing still works. You reach Envoy with port-forward.",
                  FadeIn(pfl), FadeOut(made), run_time=1.6)

        # ---------- 5. canary: two rules, weights and a header
        can = svc("hello-canary", GOLD_M, [SX, SY[1], 0])
        a3 = Arrow(prox.get_right(), can.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        self.play(FadeOut(acc), self.count(dev, 0), run_time=0.5)
        self.beat("Now a canary. A second version of the app, hello-canary, gets its own Service.",
                  FadeIn(can, shift=0.15 * LEFT), GrowArrow(a3), run_time=1.6)
        rules = VGroup(M("rule 1: header x-canary: always", 20, GOLD_M), M("rule 2: path /, weights 90 and 10", 20, WHITE)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        rules.move_to([3.85, 1.25, 0])
        w90 = M("90", 24, TEAL_M).move_to(a2.point_from_proportion(0.55) + UP * 0.35)
        w10 = M("10", 24, GOLD_M).move_to(a3.point_from_proportion(0.55) + DOWN * 0.35 + LEFT * 0.1)
        self.beat("The lab's canary route has two rules. Look at rule two first. It sends traffic to both Services, with weights 90 and 10.",
                  Indicate(hr[0], color=GREEN_M), FadeIn(rules), Succession(Wait(2.8), AnimationGroup(FadeIn(w90), FadeIn(w10))), run_time=4.0)
        p_dev = rpath
        p_can = [(cli.get_right()[0], PY), (prox.get_left()[0], PY), (prox.get_right()[0], PY), (can.get_left()[0], SY[1])]
        order = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        rides = [ride(p_can if o else p_dev, GOLD_M if o else YELLOW_M, 1.3) for o in order]
        self.steps("So about nine of every ten requests go to hello-devops, and one to the canary.",
                   (3.4, LaggedStart(*rides, lag_ratio=0.2)), (0.5, self.count(dev, 9), self.count(can, 1)))
        self.beat("Envoy picks a backend at random for each request, in proportion to the weights. So fifty requests rarely split exactly 45 and 5.",
                  LaggedStart(*[ride(p_can if i % 7 == 3 else p_dev, GOLD_M if i % 7 == 3 else YELLOW_M, 1.0) for i in range(14)], lag_ratio=0.15),
                  Succession(Wait(3.2), AnimationGroup(self.count(dev, 46), self.count(can, 4))), run_time=4.2)
        self.beat("That is a canary release. The new version gets a small share of real traffic, while you watch its errors and latency.",
                  Indicate(can[0], color=GOLD_M), run_time=1.4)

        # header rule
        hpkt = chip("x-canary: always", GOLD_M, 20, mono=True).move_to([-5.6, -0.3, 0])
        self.beat("Rule one is for testers. A request with the header x-canary, always.",
                  FadeIn(hpkt, shift=0.1 * DOWN), Indicate(rules[0], color=GOLD_M), run_time=1.6)
        q = T("both rules match. which one wins?", 24, YELLOW_M).move_to([-3.6, -2.9, 0])
        self.beat("It also has the path slash, so both rules match it. Which one wins?",
                  FadeIn(q, shift=0.1 * UP), run_time=1.4)
        win = T("the more specific match wins", 24, GOLD_M).move_to(q)
        self.steps("The most specific match wins. A header match is more specific than a path alone. So this request always goes to the canary. You never order rules by hand.",
                   (0.8, Transform(q, win), rules[1].animate.set_opacity(0.4)),
                   (1.2, hpkt.animate.move_to([XG, PY + 0.75, 0]).scale(0.85)),
                   (1.4, ride(p_can, GOLD_M, 1.4), FadeOut(hpkt)), (0.4, self.count(can, 5)))
        self.play(FadeOut(q), rules[1].animate.set_opacity(1), run_time=0.5)
        z = M("0", 24, GOLD_M).move_to(w10)
        self.beat("If the canary looks good, you move the weights. If not, you set the canary to zero, and every request goes back to hello-devops.",
                  Transform(w10, z), a3.animate.set_opacity(0.25), run_time=2.0)
        self.play(LaggedStart(*[ride(p_dev, YELLOW_M, 1.0) for _ in range(5)], lag_ratio=0.2), run_time=2.0)

        # ---------- 6. recap
        rc = T("objects on top program the proxy; the proxy carries the requests", 26).move_to([0, -3.45, 0])
        self.beat("The objects on top only configure the proxy. The proxy carries the real requests, and splits them between the Services.",
                  FadeIn(rc, shift=0.1 * UP), Indicate(VGroup(gc, gw, hr), color=WHITE, scale_factor=1.03), run_time=3.0)
        self.wait(1.5)
