import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bGatewayClass\b", "gateway class"), (r"\bHTTPRoutes?\b", lambda m: "H T T P route" + ("s" if m.group(0).endswith("s") else "")),
            (r"\bingress-nginx\b", "ingress engine X"), (r"\bx-canary\b", "X canary"), (r"\bNodePort\b", "node port"),
            (r"\bLoadBalancer\b", "load balancer"), (r"\bPROGRAMMED\b", "programmed"), (r"\bResolvedRefs\b", "resolved refs")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(c, s=1.0):
    head = Circle(radius=0.2, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.3), opacity=1)
    body = RoundedRectangle(corner_radius=0.15, width=0.62, height=0.72, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.2), opacity=1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale(s)


def obj(kind, sub, color, w=3.0):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=1.05, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    g = VGroup(M(kind, 24, color), T(sub, 22, GREY_B)).arrange(DOWN, buff=0.1).move_to(r)
    return VGroup(r, g)


def envelope(text, c=YELLOW_M, size=22):
    t = M(text, size, c)
    r = Rectangle(width=t.width + 0.4, height=0.55, stroke_color=c, stroke_width=2.5).set_fill(BLACK, 1)
    t.move_to(r)
    return VGroup(r, t)


class D44FrontDoor(VoiceScene):
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

    def construct(self):
        self.title_card("One door for many kitchens", "Gateway, HTTPRoute, and a one-in-ten canary")

        # ---------- 1. the food hall
        wall_top = Line([-1.2, 3.3, 0], [-1.2, 0.5, 0], stroke_width=4, color=GREY_B)
        wall_bot = Line([-1.2, -0.7, 0], [-1.2, -3.3, 0], stroke_width=4, color=GREY_B)
        dlab = T("street door", 24, GREY_B).move_to([-1.2, -0.1, 0]).rotate(PI / 2).shift(LEFT * 0.35)
        names = ("noodles", "tacos", "curry", "pizza", "our kitchen")
        KY = (2.6, 1.3, 0.0, -1.3, -2.6)
        kit = VGroup(*[box(n, TEAL_M if i == 4 else GREY_B, w=2.8, h=0.8, size=26).move_to([4.4, y, 0]) for i, (n, y) in enumerate(zip(names, KY))])
        self.beat("Picture our restaurant moving into a food hall. Five kitchens now share one street door.",
                  Create(wall_top), Create(wall_bot), FadeIn(dlab), LaggedStart(*[FadeIn(k, shift=LEFT * 0.2) for k in kit], lag_ratio=0.2), run_time=2.6)
        host = person(GOLD_M).move_to([0.2, -0.1, 0])
        hl = T("host", 26, GOLD_M).next_to(host, DOWN, buff=0.2)
        guests = VGroup(*[Circle(radius=0.17, stroke_color=PURPLE_M, stroke_width=2.5).set_fill(tint(PURPLE_M, 0.3), 1).move_to([-5.8 + 0.5 * (i % 3), 0.6 - 0.6 * (i // 3), 0]) for i in range(6)])
        self.beat("Guests shouldn't have to know which side door leads to which kitchen. So one host stands at the entrance, and sends each guest to the right place.",
                  FadeIn(guests), FadeIn(host), FadeIn(hl), run_time=2.4)
        g0 = guests[0]
        self.play(g0.animate.move_to([-0.6, -0.1, 0]), run_time=0.7)
        self.play(g0.animate.move_to(kit[1].get_left() + LEFT * 0.3), run_time=0.7)
        g1 = guests[1]
        self.play(g1.animate.move_to([-0.6, -0.1, 0]), run_time=0.6)
        self.play(g1.animate.move_to(kit[4].get_left() + LEFT * 0.3), run_time=0.6)
        tast = T("1 table in 10: tasting menu", 24, YELLOW_M).move_to([4.4, -3.35, 0])
        self.beat("On test nights, the host even sends one table in ten to the new tasting menu. Keep that in mind, we'll come back to it.",
                  FadeIn(tast, shift=UP * 0.1), run_time=1.6)
        self.beat("Now here's a question that feels too simple to ask. Our app already has a Service, with an address. Why would we need anything more, to let visitors in?",
                  run_time=None)
        self.play(FadeOut(VGroup(wall_top, wall_bot, dlab, kit, host, hl, guests, tast)), run_time=0.6)

        # ---------- 2. side doors, and what we really want
        app = box("hello-devops", TEAL_M, w=3.0, size=28).move_to([3.6, 0.3, 0])
        sd1 = M("localhost:8081  (NodePort)", 24, GREY_B).move_to([-3.2, 1.2, 0])
        sd2 = M("kubectl port-forward", 24, GREY_B).move_to([-3.2, -0.6, 0])
        a1 = Arrow(sd1.get_right(), app.get_left() + UP * 0.15, buff=0.2, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        a2 = Arrow(sd2.get_right(), app.get_left() + DOWN * 0.15, buff=0.2, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        self.beat("So far, you've reached hello-devops through side doors. A NodePort that kind maps to localhost 8081. Or kubectl port-forward, a tunnel to one Pod.",
                  FadeIn(app), FadeIn(sd1), GrowArrow(a1), Succession(Wait(2.4), AnimationGroup(FadeIn(sd2), GrowArrow(a2))), run_time=4.0)
        self.beat("Both are fine on a laptop. Neither is how real users arrive.", run_time=None)
        self.play(FadeOut(VGroup(sd1, sd2, a1, a2)), run_time=0.5)
        wants = VGroup(chip("one door for many apps", GOLD_M, 24), chip("route by host name and path", GOLD_M, 24),
                       chip("TLS in one place", GOLD_M, 24), chip("gradual releases", GOLD_M, 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        wants.move_to([-3.4, 0.3, 0])
        self.beat("For real visitors, you want one door for many apps, so you pay for one load balancer instead of ten. Routing by host name and path. TLS, the encryption behind https, in one place. And gradual releases.",
                  LaggedStart(*[FadeIn(w, shift=RIGHT * 0.15) for w in wants], lag_ratio=0.7), run_time=8.0)
        self.play(FadeOut(wants), run_time=0.5)

        # a LoadBalancer Service: a door with no host
        door = RoundedRectangle(corner_radius=0.1, width=1.6, height=2.2, stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.1), 1).move_to([-0.6, 0.3, 0])
        doorl = M("LoadBalancer", 24, GREY_B).next_to(door, UP, buff=0.2)
        env = envelope("GET shop.example.com/api").move_to([-4.6, 0.3, 0])
        hdr = M("x-canary: always", 22, GREY_B).next_to(env, DOWN, buff=0.15)
        self.beat("A Service of type LoadBalancer does give you an address. But it's a door with no host.",
                  FadeIn(door), FadeIn(doorl), FadeIn(env), FadeIn(hdr), run_time=2.0)
        l4 = T("layer 4: connections only", 26, GREY_B).next_to(door, DOWN, buff=0.3)
        self.steps("It works with connections, at layer 4. It never opens the envelope. Never looks at the web address, or at a header, a labelled line of extra information sent with each request.",
                   (0.8, FadeIn(l4)), (1.4, VGroup(env, hdr).animate.move_to([-0.6, 0.3, 0]).scale(0.6)), (1.4, VGroup(env, hdr).animate.move_to([3.6, 0.3, 0]).scale(1 / 0.6).set_opacity(0)),
                   (1.0, Indicate(app[1], color=TEAL_M)))
        self.remove(env, hdr)
        self.beat("Excellent hinges. No opinions. It can't send slash api to one app, and everything else to another.",
                  Indicate(doorl, color=WHITE), run_time=1.4)
        self.beat("What we want is the host. Someone who opens each request, reads it, and decides where it goes.",
                  run_time=None)
        self.play(FadeOut(VGroup(door, doorl, l4)), run_time=0.5)

        # ---------- 3. a proxy, and a book of rules
        prox = VGroup(person(GOLD_M, 0.9), M("proxy", 26, GOLD_M)).arrange(DOWN, buff=0.2).move_to([-0.6, 0.3, 0])
        pl = T("reads web requests: layer 7", 24, GOLD_M).next_to(prox, DOWN, buff=0.25)
        self.beat("A program that does that is called a proxy. It sits in front of your apps, and passes each request on. One that reads web requests works at layer 7.",
                  FadeIn(prox), Succession(Wait(3.2), FadeIn(pl)), run_time=4.2)
        book = RoundedRectangle(corner_radius=0.08, width=3.0, height=2.4, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.1), 1).move_to([-4.6, 0.3, 0])
        bt = VGroup(M("Ingress", 26, BLUE_M), T("hosts, paths, TLS", 24)).arrange(DOWN, buff=0.25).move_to(book)
        self.beat("But a host needs a book of rules. Kubernetes' older object for those rules is called Ingress. Small, on purpose: host names, paths, and TLS.",
                  FadeIn(book), FadeIn(bt), run_time=2.4)
        notes = VGroup(T("rewrite?", 20, RED_M), T("timeouts!", 20, RED_M), T("canary=10", 20, RED_M), T("see p.4", 20, RED_M))
        for n, p in zip(notes, ([-6.55, 1.2, 0], [-6.5, 0.1, 0], [-6.5, -1.0, 0], [-3.4, -1.25, 0])):
            n.move_to(p).rotate(0.15)
        self.beat("Everything else went into annotations, notes in the margin. And each controller used its own shorthand. A config written for one rarely worked on another.",
                  LaggedStart(*[FadeIn(n, scale=0.8) for n in notes], lag_ratio=0.4), run_time=2.8)
        froz = VGroup(chip("Ingress API: frozen", GREY_B, 22), chip("ingress-nginx retired: March 24, 2026", RED_M, 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        froz.move_to([3.3, 2.6, 0])
        self.beat("Today the Ingress API is frozen, with no new features. And ingress-nginx, the most popular controller, was retired on March 24, 2026.",
                  FadeIn(froz[0]), Succession(Wait(1.6), FadeIn(froz[1])), run_time=3.0)
        self.play(FadeOut(VGroup(book, bt, notes, froz)), run_time=0.5)

        # ---------- 4. the Gateway API: one object per role
        OY = 2.55
        gc = obj("GatewayClass", "who staffs the door", BLUE_M).move_to([-4.4, OY, 0])
        gw = obj("Gateway", "the street door", BLUE_M).move_to([-0.6, OY, 0])
        hr = obj("HTTPRoute", "a kitchen's line in the book", BLUE_M, w=3.5).move_to([3.4, OY, 0])
        self.beat("The newer set of objects is the Gateway API. It splits the job by who owns what, just like the food hall.",
                  prox.animate.move_to([-0.6, -1.3, 0]), FadeOut(pl), app.animate.move_to([4.2, -1.3, 0]), run_time=1.6)
        own = VGroup(T("platform team, once per cluster", 20, GREY_B).next_to(gc, DOWN, buff=0.15),
                     T("listeners: HTTP on port 80", 20, GREY_B).next_to(gw, DOWN, buff=0.15),
                     T("app teams", 20, GREY_B).next_to(hr, DOWN, buff=0.15))
        self.beat("A GatewayClass says which controller handles the door. That's the company that staffs the entrance. The platform team creates it once per cluster.",
                  FadeIn(gc), FadeIn(own[0]), run_time=2.0)
        self.beat("A Gateway is the street door itself, with listeners, such as HTTP on port 80.",
                  FadeIn(gw), FadeIn(own[1]), run_time=1.8)
        self.beat("And an HTTPRoute is each kitchen's line in the host's book: slash goes to the hello-devops Service. App teams write these, and attach them to a Gateway.",
                  FadeIn(hr), FadeIn(own[2]), run_time=2.4)
        objs = VGroup(gc, gw, hr, own)

        # predict: does traffic flow?
        cmd = M("kubectl apply  (fresh kind cluster)", 24, WHITE).move_to([-0.6, 0.6, 0])
        self.beat("Let's try it. A fresh kind cluster, nothing extra installed. We apply a Gateway and an HTTPRoute. Pause and guess: does traffic start flowing?",
                  FadeIn(cmd), run_time=1.6)
        self.wait(2.0)
        err = M('error: no matches for kind "Gateway"', 24, RED_M).move_to(cmd)
        self.beat("Well... not even close. The apply fails. No matches for kind.",
                  Transform(cmd, err), Wiggle(gw), run_time=1.6)
        crd = chip("install the CRDs: new object types", BLUE_M, 24).move_to([-0.6, 0.6, 0])
        self.beat("The Gateway API isn't built into Kubernetes. You install it as CRDs, new object types that the API server learns.",
                  FadeOut(cmd), FadeIn(crd), run_time=1.6)
        self.beat("And even then, nothing routes. A job description is not a host. Somebody has to read these objects, and act on them. That somebody is a controller.",
                  Indicate(prox[1], color=GOLD_M), run_time=2.0)
        self.play(FadeOut(crd), run_time=0.4)

        # ---------- 5. Envoy Gateway, step by step
        ctl = box("Envoy Gateway controller", GREY_B, w=4.4, h=0.75, size=24).move_to([-0.6, 0.55, 0])
        self.beat("The lab uses Envoy Gateway, an open source controller that runs the Envoy proxy. Watch what happens when you apply the lab's gateway folder.",
                  FadeIn(ctl), run_time=1.6)
        nums = VGroup(*[Circle(radius=0.22, stroke_color=YELLOW_M, stroke_width=2.5).set_fill(BLACK, 1) for _ in range(4)])
        nt = VGroup(*[T(str(i + 1), 22, YELLOW_M) for i in range(4)])
        badge = VGroup(*[VGroup(c, t.move_to(c)) for c, t in zip(nums, nt)])
        badge[0].move_to(gc.get_corner(UL) + RIGHT * 0.05 + DOWN * 0.05)
        badge[1].move_to(gw.get_corner(UL) + RIGHT * 0.05 + DOWN * 0.05)
        badge[2].move_to(hr.get_corner(UL) + RIGHT * 0.05 + DOWN * 0.05)
        badge[3].move_to(ctl.get_corner(UL) + RIGHT * 0.05 + DOWN * 0.05)
        e1 = Arrow(gc.get_bottom() + DOWN * 0.3, ctl.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        self.beat("One. The class eg names the controller. Envoy Gateway sees its own name, and accepts the class.",
                  FadeIn(badge[0]), GrowArrow(e1), run_time=1.8)
        e2 = Arrow(ctl.get_bottom(), prox.get_top(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("Two. The Gateway, hello-gateway, uses class eg. So the controller starts an Envoy proxy for it, a Deployment and a Service.",
                  FadeIn(badge[1]), Succession(Wait(1.8), AnimationGroup(GrowArrow(e2), Indicate(prox[1], color=GOLD_M))), run_time=3.2)
        e3 = DashedLine(hr.get_bottom() + DOWN * 0.3, app.get_top(), dash_length=0.1, stroke_width=2, color=BLUE_M)
        self.beat("Three. The HTTPRoute hello-devops attaches to hello-gateway, and points at the hello-devops Service.",
                  FadeIn(badge[2]), Create(e3), run_time=2.0)
        self.steps("Four. The controller turns the route into Envoy settings, and sends them to the proxy. Now it starts forwarding.",
                   (0.6, FadeIn(badge[3])), (1.6, travel(e2, BLUE_M, 1.0)), (0.6, Wait(0.6)), (0.8, Indicate(prox[0], color=GOLD_M)))
        curl = M("curl", 26, PURPLE_M).move_to([-5.4, -1.3, 0])
        p1 = Arrow(curl.get_right(), prox.get_left(), buff=0.2, stroke_width=3, color=PURPLE_M, max_tip_length_to_length_ratio=0.1)
        p2 = Arrow(prox.get_right(), app.get_left(), buff=0.2, stroke_width=3, color=PURPLE_M, max_tip_length_to_length_ratio=0.1)
        self.steps("Now a request. From curl, to Envoy, to hello-devops. Look where the controller is. It never handles a single request.",
                   (0.8, FadeIn(curl), GrowArrow(p1), GrowArrow(p2)), (1.0, travel(p1, PURPLE_M, 1.0)), (1.0, travel(p2, PURPLE_M, 1.0)),
                   (1.2, Indicate(ctl[1], color=WHITE)))
        self.beat("It watches objects and writes settings. The proxy carries the traffic. The staffing company trains the host. The host greets the guests.",
                  run_time=None)
        prog = VGroup(M("PROGRAMMED  False", 22, GREY_B), T("no addresses on kind: fine, use port-forward", 20, GREY_B)).arrange(DOWN, buff=0.1).move_to([-0.6, -3.05, 0])
        self.beat("One kind quirk. The proxy's Service has type LoadBalancer, and kind has no cloud to give it an address. So the Gateway shows PROGRAMMED, False. You can ignore it. The routing works, and you reach the proxy with port-forward.",
                  FadeIn(prog, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(prog, badge, e1)), run_time=0.5)

        # ---------- 6. the canary, by weight
        can = box("hello-canary", YELLOW_M, w=3.0, size=28).move_to([4.2, -2.8, 0])
        self.play(app.animate.move_to([4.2, -0.7, 0]), FadeOut(e3), run_time=0.8)
        p2b = Arrow(prox.get_right(), app.get_left(), buff=0.2, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.1)
        p3 = Arrow(prox.get_right(), can.get_left(), buff=0.2, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.1)
        w90 = M("90", 26, TEAL_M).next_to(p2b.get_center(), UP, buff=0.15)
        w10 = M("10", 26, YELLOW_M).next_to(p3.get_center(), DOWN, buff=0.2)
        self.beat("Now, the tasting menu. A second version of the app, hello-canary, gets its own Service.",
                  FadeIn(can), Transform(p2, p2b), run_time=1.6)
        self.beat("A rule in an HTTPRoute can send traffic to more than one Service, with weights. Ninety, and ten.",
                  GrowArrow(p3), FadeIn(w90), FadeIn(w10), run_time=2.0)
        self.beat("So about nine of every ten requests go to hello-devops, and one to the canary.",
                  Indicate(w90, color=TEAL_M), Succession(Wait(1.6), Indicate(w10, color=YELLOW_M)), run_time=3.0)
        self.beat("Here's a prediction for you. We send fifty requests. Pause and guess: is it exactly forty-five and five?",
                  run_time=None)
        self.wait(2.0)
        picks = np.random.default_rng(0).random(50) < 0.1
        n_can = int(picks.sum()); n_app = 50 - n_can
        assert (n_app, n_can) == (44, 6)
        ca = Integer(0, font_size=34, color=TEAL_M).next_to(app, UP, buff=0.15)
        cc = Integer(0, font_size=34, color=YELLOW_M).next_to(can, UP, buff=0.15)
        self.add(ca, cc)
        anims = []
        k_app = k_can = 0
        for to_can in picks:
            path = p3 if to_can else p2
            anims.append(travel(path, YELLOW_M if to_can else TEAL_M, run_time=0.5))
        path_, dur = voice("Let's see. Envoy picks a backend for each request at random, in proportion to the weights.")
        self._cue("Let's see. Envoy picks a backend for each request at random, in proportion to the weights.", dur)
        self.add_sound(path_)
        self.play(LaggedStart(*anims, lag_ratio=0.12), ChangeDecimalToValue(ca, n_app), ChangeDecimalToValue(cc, n_can), run_time=max(dur, 4.0))
        self.wait(0.3)
        ex = T("one example run", 20, GREY_B).next_to(cc, LEFT, buff=0.3)
        self.beat("This run: forty-four and six. Close to ninety and ten, rarely exact. Run it again, and you'll get different numbers.",
                  FadeIn(ex), run_time=1.6)
        self.beat("That's a canary release. A new version gets a small share of real traffic, while you watch its errors and response times. If it looks good, you move the weights. If not, you set the canary to zero.",
                  Transform(w10, M("0", 26, YELLOW_M).move_to(w10)), Succession(Wait(5.0), Transform(w10, M("10", 26, YELLOW_M).move_to(w10))), run_time=6.0)
        # the header rule
        tester = envelope("x-canary: always", YELLOW_M).move_to([-5.0, -2.6, 0])
        self.beat("The lab adds one more rule, for testers. A request with the header x-canary, always, goes straight to the canary. It has the path slash too, so both rules match. Which one wins?",
                  FadeIn(tester), run_time=1.6)
        self.wait(1.0)
        pth = VMobject().set_points_as_corners([tester.get_right(), prox.get_left() + DOWN * 0.3, prox.get_right() + DOWN * 0.5, can.get_left()])
        self.steps("The most specific match wins. With equal paths, more header matches win. So the tester always lands on the canary, and you never order the rules by hand.",
                   (1.6, Wait(1.6)), (1.6, MoveAlongPath(tester, pth)), (0.6, Indicate(can[1], color=YELLOW_M)))
        self.play(FadeOut(VGroup(tester, ex, ca, cc)), run_time=0.5)

        # ---------- 7. guardrails: TLS at the door, and where to look first
        lock = chip("HTTPS listener: tls.mode Terminate", GREEN_M, 22, mono=True).move_to([-3.8, 0.55, 0])
        self.beat("Two habits before you rely on this. First, set TLS once, on the Gateway. An HTTPS listener with mode Terminate decrypts at the proxy, using a certificate from a Secret.",
                  FadeOut(ctl), FadeIn(lock, shift=DOWN * 0.1), run_time=2.2)
        plain = T("last hop: unencrypted", 22, RED_M).move_to([1.7, -2.05, 0])
        self.beat("It's the host who checks every booking at the door, so the kitchens don't have to. But notice: the last hop, from the proxy to your Pods, stays unencrypted. Part 15 deals with that.",
                  Succession(Wait(4.0), FadeIn(plain)), run_time=5.0)
        dbg = M("kubectl describe httproute", 24, WHITE).move_to([2.6, 0.55, 0])
        cond = T("Accepted? ResolvedRefs?", 22, GREY_B).next_to(dbg, DOWN, buff=0.15)
        self.beat("Second. When curl gets a 404 or a 500, it's tempting to start changing the Gateway. Usually the route never attached, or it points at a Service that doesn't exist. Run kubectl describe httproute first.",
                  FadeIn(dbg), Succession(Wait(4.0), FadeIn(cond)), Indicate(hr[1][0], color=BLUE_M), run_time=5.0)
        self.play(FadeOut(VGroup(objs, prox, app, can, p1, p2, p3, w90, w10, curl, e2, lock, plain, dbg, cond)), run_time=0.6)

        # ---------- 8. moral and quick check
        mor = VGroup(T("A Service is a door. A proxy is the host.", 32),
                     T("GatewayClass: who staffs the door", 28, BLUE_M),
                     T("Gateway: the door and its listeners", 28, BLUE_M),
                     T("HTTPRoute: each app's line in the book, with weights", 28, BLUE_M),
                     T("the controller writes settings; the proxy carries requests", 28, GOLD_M)).arrange(DOWN, buff=0.35)
        self.beat("So, the moral of the story. A Service is a door. A proxy is the host. The GatewayClass says who staffs the door. The Gateway is the door and its listeners. Each app writes its own line in the book, an HTTPRoute, weights and all. And the controller only writes settings. The proxy carries the requests.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mor], lag_ratio=0.8), run_time=10.0)
        self.play(FadeOut(mor), run_time=0.6)
        q = VGroup(T("A shop wants /api sent to Service api,", 30), T("and every other path to Service web, through one Gateway.", 30),
                   T("What do you write?", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 0.8, 0])
        self.beat("One quick check. A shop wants slash api sent to the Service api, and every other path to the Service web, through one Gateway. What do you write? Pause and think.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in q], lag_ratio=0.5), run_time=4.0)
        self.wait(2.0)
        ans = chip("one HTTPRoute with two path rules", BLUE_M, 28).move_to([0, -1.5, 0])
        self.beat("One HTTPRoute, with two rules that match on path. The slash api rule is more specific, so it wins for those requests, and slash takes the rest. Thanks for watching.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.0)
