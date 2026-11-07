import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\biptables\b", "I P tables"), (r"\bEDS\b", "E D S"), (r"\bADS\b", "A D S"),
            (r"\bistiod\b", "istio D"), (r"\b1337\b", "thirteen thirty-seven")])

ENV = GOLD_M


def polyline(*pts, color=YELLOW_M):
    return VMobject(stroke_color=color, stroke_width=2).set_points_as_corners([np.array([x, y, 0]) for x, y in pts])


def ride(pts, color=YELLOW_M, run_time=1.4):
    """A dot that runs along a bent path."""
    path = polyline(*pts)
    d = Dot(radius=0.09, color=color).move_to(path.get_start())
    return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=smooth, run_time=run_time), FadeOut(d, run_time=0.15))


def lock(color=GREEN_M, s=1.0):
    body = RoundedRectangle(corner_radius=0.05, width=0.42, height=0.32, stroke_color=color, stroke_width=3).set_fill(BLACK, 1)
    shackle = Arc(radius=0.14, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(body, UP, buff=0)
    return VGroup(shackle, body).scale(s)


class D58Sidecar(VoiceScene):
    def construct(self):
        self.title_card("How a sidecar catches traffic", "iptables, Envoy, and the control plane")

        # ---------- A. two Pods, two apps
        podL = RoundedRectangle(corner_radius=0.2, width=5.4, height=4.35, stroke_color=GREY_B, stroke_width=2).move_to([-4.0, -1.275, 0])
        podR = podL.copy().move_to([4.0, -1.275, 0])
        labL = T("checkout Pod", 24, GREY_B).move_to(podL.get_corner(UL) + np.array([0.2, -0.3, 0]), aligned_edge=LEFT)
        labR = T("fraud-check Pod", 24, GREY_B).move_to(podR.get_corner(UR) + np.array([-0.2, -0.3, 0]), aligned_edge=RIGHT)
        appL = box("checkout", BLUE_M, w=2.1).move_to([-5.3, -0.55, 0])
        appR = box("fraud check", TEAL_M, w=2.2).move_to([5.3, -0.55, 0])
        self.beat("Two services in a mesh. A checkout app calls a fraud check over HTTP.",
                  Create(podL), Create(podR), FadeIn(labL), FadeIn(labR),
                  Create(appL[0]), Write(appL[1]), Create(appR[0]), Write(appR[1]), run_time=2.4)
        want = CurvedArrow(np.array([-5.3, 1.05, 0]), np.array([5.3, 1.05, 0]), angle=-0.42, color=GREY_B, stroke_width=2.5)
        want_d = DashedVMobject(want, num_dashes=40)
        url = M("http://fraud-check/", 22, WHITE).move_to([0, 2.25, 0])
        self.beat("Nobody changes the app's code or its URLs. The app still sends its request to fraud-check, as if nothing were in between.",
                  Create(want_d), FadeIn(url, shift=DOWN * 0.1), run_time=2.4)

        envL = box("Envoy", ENV, w=1.8).move_to([-2.7, -0.55, 0])
        envR = box("Envoy", ENV, w=1.8).move_to([2.7, -0.55, 0])
        self.beat("In sidecar mode, every Pod gets an extra container: an Envoy proxy. The containers of a Pod share one network, so the proxy can see the app's traffic.",
                  GrowFromCenter(envL), GrowFromCenter(envR),
                  Succession(Wait(1.2), AnimationGroup(Indicate(podL, color=WHITE, scale_factor=1.0), Indicate(podR, color=WHITE, scale_factor=1.0))), run_time=3.4)

        # ---------- B. iptables rules catch the call
        def rules():
            ls = VGroup(M("outgoing  → Envoy :15001", 20), M("incoming  → Envoy :15006", 20), M("UID 1337  → skip", 20))
            ls.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            fr = RoundedRectangle(corner_radius=0.1, width=5.2, height=ls.height + 0.3, stroke_color=PURPLE_M, stroke_width=2)
            fr.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(PURPLE_M), 0.12), 1)
            nm = T("iptables", 22, PURPLE_M).move_to(fr.get_left() + RIGHT * 0.68)
            ls.move_to(fr).align_to(fr, RIGHT).shift(LEFT * 0.18)
            return VGroup(fr, ls, nm)
        strL = rules().move_to([-4.0, -2.75, 0])
        strR = rules().move_to([4.0, -2.75, 0])
        self.beat("A proxy only helps if traffic passes through it. So before the app starts, an init container or a CNI plugin writes iptables rules inside the Pod's network.",
                  FadeIn(strL, shift=UP * 0.15), FadeIn(strR, shift=UP * 0.15), run_time=3.0)
        pL = M(":15001", 20, ENV).next_to(envL, DOWN, buff=0.1).shift(LEFT * 0.35)
        pR = M(":15006", 20, ENV).next_to(envR, DOWN, buff=0.1).shift(RIGHT * 0.35)
        self.beat("They are the same kernel packet rules kube-proxy writes. Istio's rules send outgoing connections to Envoy on port 15001, and incoming ones to port 15006.",
                  Succession(Wait(1.8), AnimationGroup(strL[1][0].animate.set_color(YELLOW_M), FadeIn(pL, shift=UP * 0.1)),
                             AnimationGroup(strR[1][1].animate.set_color(YELLOW_M), FadeIn(pR, shift=UP * 0.1))), run_time=5.0)
        self.play(strL[1][0].animate.set_color(WHITE), strR[1][1].animate.set_color(WHITE), run_time=0.4)

        # one call, caught on its way out
        sy = strL[0].get_top()[1]
        out1 = [(-5.3, -0.96), (-5.3, sy + 0.02), (-2.95, sy + 0.02), (-2.95, -0.96)]
        self.beat("Watch one call. The app opens a connection to fraud-check.",
                  appL[0].animate.set_stroke(width=6), run_time=1.0)
        self.beat("The kernel matches the outgoing rule, and quietly hands the connection to Envoy, on port 15001. The app never notices.",
                  Succession(ride(out1[:2], run_time=0.8), Indicate(strL[1][0], color=YELLOW_M, scale_factor=1.04), ride(out1[1:], run_time=1.2)),
                  appL[0].animate.set_stroke(width=3), run_time=3.6)
        orig = chip("original address: fraud-check", YELLOW_M, 20).move_to([-4.0, -1.72, 0])
        oa = Arrow([-2.35, -1.4, 0], [-2.35, -0.95, 0], buff=0.02, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.35)
        self.beat("So how does Envoy know where the app meant to go? The kernel remembers the original address of every redirected connection, and Envoy reads it back.",
                  Succession(Wait(2.4), FadeIn(orig, shift=UP * 0.1), AnimationGroup(GrowArrow(oa), Indicate(envL, color=YELLOW_M, scale_factor=1.06))), run_time=5.0)

        # ---------- C. inside Envoy: listener, route, cluster, endpoint
        overview = VGroup(podL, podR, labL, labR, appL, appR, want_d, url, envL, envR, strL, strR, pL, pR, orig, oa)
        self.play(FadeOut(overview), run_time=0.8)
        head = T("inside the checkout Pod's Envoy", 26, ENV).move_to([0, 3.35, 0])
        dn = box("checkout app", BLUE_M, size=26).move_to([-5.25, 1.75, 0])
        dnl = T("downstream", 22, GREY_B).next_to(dn, UP, buff=0.15)
        lis = box("listener :15001", ENV, size=26).move_to([-1.725, 1.75, 0])
        hcm = RoundedRectangle(corner_radius=0.15, width=4.9, height=1.75, stroke_color=ENV, stroke_width=2).move_to([3.0, 1.85, 0])
        hcml = T("HTTP connection manager", 22, ENV).move_to(hcm.get_top() + DOWN * 0.32)
        fil = box("HTTP filters", GREY_B, w=2.1, h=0.62, size=24).move_to([1.9, 1.55, 0])
        rtr = box("router", ENV, w=1.5, h=0.62, size=24).move_to([4.4, 1.55, 0])
        a_dl = edge_arrow(dn, lis)
        a_lh = Arrow(lis.get_right(), hcm.get_left() + DOWN * 0.1, buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        a_fr = Arrow(fil.get_right(), rtr.get_left(), buff=0.08, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        self.beat("Now follow the request inside Envoy. Downstream is the side that sends requests to Envoy: here, the checkout app.",
                  FadeIn(head), Create(dn[0]), Write(dn[1]), FadeIn(dnl), run_time=2.4)

        rl = VGroup(T("route table", 22, GREY_B),
                    M("virtual host  Host: fraud-check", 20),
                    M("route         prefix /", 20),
                    M("  → cluster fraud-check", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        rfr = RoundedRectangle(corner_radius=0.12, width=rl.width + 0.5, height=rl.height + 0.45, stroke_color=BLUE_M, stroke_width=2).set_fill(BLACK, 1)
        rtab = VGroup(rfr, rl.move_to(rfr)).move_to([-4.0, -1.2, 0])
        clu = box("cluster fraud-check", GREEN_M, size=24).move_to([1.15, -1.2, 0])
        clu_n = T("a group of hosts for one service", 22, GREEN_M).next_to(clu, DOWN, buff=0.2)
        eps = VGroup(*[mbox(t, TEAL_M, w=2.3, h=0.52, size=20) for t in ("10.0.1.7:8000", "10.0.2.4:8000", "10.0.3.9:8000")]).arrange(DOWN, buff=0.14).move_to([5.2, -1.2, 0])
        upl = T("upstream", 22, GREY_B).next_to(eps, UP, buff=0.18)
        self.beat("Upstream is the side Envoy sends them on to: the fraud check Pods.",
                  LaggedStart(*[FadeIn(e, shift=LEFT * 0.1) for e in eps], lag_ratio=0.2), FadeIn(upl), run_time=2.0)
        self.beat("A listener accepts the connection, and runs its filter chain. Here, that is the HTTP connection manager. It turns the bytes into HTTP requests.",
                  GrowArrow(a_dl), Create(lis[0]), Write(lis[1]),
                  Succession(Wait(1.6), AnimationGroup(GrowArrow(a_lh), Create(hcm), FadeIn(hcml))), run_time=4.4)
        self.play(travel(a_dl), run_time=0.6)
        self.play(travel(a_lh), run_time=0.6)
        self.beat("Then it runs the HTTP filters in order. The router comes last, because it is the filter that sends the request upstream.",
                  Create(fil[0]), Write(fil[1]), Succession(Wait(1.0), AnimationGroup(GrowArrow(a_fr), Create(rtr[0]), Write(rtr[1]))), run_time=3.6)
        a_rt = Arrow(rtr.get_bottom(), rfr.get_corner(UR) + LEFT * 0.6, buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.06)
        self.beat("The router looks up the route table. A virtual host matches the Host header. Inside it, the first route whose match fits wins.",
                  GrowArrow(a_rt), Create(rfr), FadeIn(rl[0]),
                  Succession(Wait(0.8), FadeIn(rl[1], shift=RIGHT * 0.1), Wait(0.8), FadeIn(rl[2], shift=RIGHT * 0.1)), run_time=5.0)
        a_rc = edge_arrow(rtab, clu)
        self.beat("The route names a cluster. In Envoy, a cluster is a group of upstream hosts for one service. It has nothing to do with a Kubernetes cluster.",
                  FadeIn(rl[3], shift=RIGHT * 0.1), GrowArrow(a_rc), Create(clu[0]), Write(clu[1]),
                  Succession(Wait(1.6), FadeIn(clu_n, shift=UP * 0.1)), run_time=4.4)
        a_ce = edge_arrow(clu, eps[1])
        pick = SurroundingRectangle(eps[1], buff=0.07, color=YELLOW_M, stroke_width=3)
        self.beat("The cluster's load balancer picks one endpoint, a single address and port. It sends the request over a pooled connection, one that Envoy keeps open and reuses.",
                  GrowArrow(a_ce), Succession(Wait(1.2), Create(pick)), run_time=3.4)
        self.play(travel(a_ce), run_time=0.7)
        pipe = VGroup(head, dn, dnl, lis, hcm, hcml, fil, rtr, a_dl, a_lh, a_fr, a_rt, rtab, a_rc, clu, clu_n, eps, upl, a_ce, pick)

        # ---------- D. leaving the Pod, mTLS, arriving in the other Pod
        self.play(FadeOut(pipe), run_time=0.7)
        self.play(FadeIn(VGroup(podL, podR, labL, labR, appL, appR, envL, envR, strL, strR, pL, pR)), run_time=0.8)
        ry = strR[0].get_top()[1]
        out2 = [(-2.45, -0.96), (-2.45, sy + 0.02)]
        cross = [(-2.45, sy + 0.02), (-1.5, -2.75), (1.5, -2.75), (2.45, ry + 0.02)]
        self.beat("Envoy's own call now leaves the Pod. It passes the same iptables rules, but they skip traffic from the proxy's own user, ID 1337 in Istio. Otherwise the call would loop straight back into Envoy.",
                  Succession(ride(out2, run_time=0.8), Indicate(strL[1][2], color=YELLOW_M, scale_factor=1.04), Wait(1.5), ride(cross[:3], run_time=1.2)), run_time=6.2)
        wire = Line([-1.45, -2.75, 0], [1.45, -2.75, 0], stroke_color=GREEN_M, stroke_width=3)
        lk = lock().move_to([0, -2.2, 0])
        mt = T("mTLS", 24, GREEN_M).next_to(wire, DOWN, buff=0.15)
        cL = chip("cert: checkout", GREEN_M, 20, mono=True).move_to([-2.9, -1.72, 0])
        cR = chip("cert: fraud-check", GREEN_M, 20, mono=True).move_to([2.75, -1.72, 0])
        self.beat("Between the Pods, the two proxies use mutual TLS. Both sides show a certificate, so each knows who the other is.",
                  Create(wire), FadeIn(cL, shift=UP * 0.1), FadeIn(cR, shift=UP * 0.1),
                  Succession(Wait(1.2), AnimationGroup(cL.animate.shift(RIGHT * 1.2), cR.animate.shift(LEFT * 1.2)),
                             AnimationGroup(cL.animate.shift(LEFT * 1.2), cR.animate.shift(RIGHT * 1.2)), AnimationGroup(FadeIn(lk, scale=0.6), FadeIn(mt))),
                  run_time=4.4)
        self.play(FadeOut(VGroup(cL, cR)), run_time=0.5)
        in1 = [(1.5, -2.75), (2.45, ry + 0.02)]
        in2 = [(2.45, ry + 0.02), (2.95, ry + 0.02), (2.95, -0.96)]
        self.beat("In the fraud check Pod, the incoming rule sends the connection to its Envoy, on port 15006.",
                  Succession(ride(in1, run_time=0.6), Indicate(strR[1][1], color=YELLOW_M, scale_factor=1.04), ride(in2, run_time=0.8)), run_time=3.0)
        a_ea = edge_arrow(envR, appR, ENV)
        self.beat("That second proxy does the same work for incoming calls, then passes the request to the fraud check app.",
                  GrowArrow(a_ea), Succession(Wait(0.8), travel(a_ea, run_time=0.8), Indicate(appR, color=TEAL_M, scale_factor=1.05)), run_time=3.2)
        self.beat("The app made a plain HTTP call. The proxies add the timeout, the retries, the encryption and the metrics.",
                  Indicate(envL, color=ENV, scale_factor=1.08), Indicate(envR, color=ENV, scale_factor=1.08), run_time=2.0)

        # ---------- E. where the config comes from: xDS
        self.play(FadeOut(a_ea), run_time=0.5)
        self.beat("Where does all this config come from? Pods start and stop all day, each with a new IP. A mesh may have hundreds of Envoys that must learn every change within seconds.",
                  Indicate(appR, color=WHITE, scale_factor=1.05), Succession(Wait(2.0), Wiggle(envL), Wiggle(envR)), run_time=4.0)
        bsL = chip("bootstrap", GREY_B, 20, mono=True).move_to([-2.7, -1.72, 0])
        bsR = chip("bootstrap", GREY_B, 20, mono=True).move_to([2.7, -1.72, 0])
        cp = box("istiod", BLUE_M, w=1.9, h=0.85).move_to([-2.6, 2.75, 0])
        cpl = T("control plane", 22, BLUE_M).next_to(cp, UP, buff=0.12)
        xL = DashedLine(cp.get_bottom(), envL.get_top() + UP * 0.05, dash_length=0.1, stroke_width=2.5, color=BLUE_M)
        xR = DashedLine(cp.get_bottom(), envR.get_top() + UP * 0.05, dash_length=0.1, stroke_width=2.5, color=BLUE_M)
        self.beat("Each Envoy starts from a small static file, the bootstrap. It says where its config server is: the control plane. In Istio, that is istiod.",
                  FadeIn(bsL, shift=UP * 0.1), FadeIn(bsR, shift=UP * 0.1),
                  Succession(Wait(1.6), AnimationGroup(Create(cp[0]), Write(cp[1]), FadeIn(cpl), Create(xL), Create(xR))), run_time=4.2)
        k8s = box("Kubernetes API", GREY_B, w=2.5, size=24).move_to([-5.5, 2.75, 0])
        a_kc = edge_arrow(k8s, cp)
        dL = Line(cp.get_bottom(), envL.get_top() + UP * 0.05)
        dR = Line(cp.get_bottom(), envR.get_top() + UP * 0.05)
        self.beat("The control plane watches the Kubernetes API for Services, EndpointSlices and your routing objects. It turns them into Envoy objects, and pushes them to every proxy, over gRPC.",
                  Create(k8s[0]), Write(k8s[1]), GrowArrow(a_kc),
                  Succession(Wait(2.6), AnimationGroup(travel(dL, BLUE_M, run_time=1.0), travel(dR, BLUE_M, run_time=1.0))), run_time=5.4)

        names = [("LDS", "listeners"), ("RDS", "routes"), ("CDS", "clusters"), ("EDS", "endpoints"), ("SDS", "secrets")]
        cols = [ENV, BLUE_M, GREEN_M, TEAL_M, PURPLE_M]
        xds = [chip(f"{a}  {b}", c, 20) for (a, b), c in zip(names, cols)]
        slots = [[-0.15, 3.15], [2.3, 3.15], [4.75, 3.15], [-0.15, 2.4], [2.3, 2.4]]
        for ch, (x, y) in zip(xds, slots):
            ch.move_to([x, y, 0])
        xh = T("xDS, over gRPC", 20, BLUE_M).move_to([-0.1, 0.4, 0])
        self.beat("The APIs that carry them are called xDS, one for each kind of object. LDS sends listeners. RDS sends route tables. CDS sends clusters.",
                  FadeIn(xh), Succession(Wait(2.4), FadeIn(xds[0], shift=DOWN * 0.1), Wait(0.5), FadeIn(xds[1], shift=DOWN * 0.1), Wait(0.5), FadeIn(xds[2], shift=DOWN * 0.1)),
                  run_time=6.0)
        self.beat("EDS sends endpoints, the Pod IPs behind each cluster. They change most often. And SDS sends secrets: TLS certificates and keys.",
                  Succession(FadeIn(xds[3], shift=DOWN * 0.1), Wait(2.2), FadeIn(xds[4], shift=DOWN * 0.1)), run_time=4.4)
        allx = VGroup(*xds)
        ads = SurroundingRectangle(allx, buff=0.15, corner_radius=0.12, color=WHITE, stroke_width=2)
        adsl = T("ADS: one stream", 22, WHITE).next_to(ads, DOWN, buff=0.1).align_to(ads, RIGHT)
        self.beat("Order matters. A route that names a cluster Envoy has not received yet sends its traffic nowhere.",
                  Indicate(xds[1], color=RED_M), run_time=2.0)
        self.beat("So many control planes send everything over one stream, called ADS, with clusters before the routes that use them.",
                  Create(ads), FadeIn(adsl), Succession(Wait(1.6), AnimationGroup(xds[2].animate.move_to(xds[1]), xds[1].animate.move_to(xds[2]))),
                  run_time=4.0)
        newep = chip("+ 10.0.4.2:8000", TEAL_M, 20, mono=True).move_to([-2.9, -1.72, 0])
        self.beat("Each object is separate. When a new fraud check Pod starts, the control plane adds its endpoint over EDS, without touching the listener or the routes.",
                  FadeOut(bsL), FadeOut(bsR), Indicate(xds[3], color=TEAL_M, scale_factor=1.1),
                  Succession(Wait(2.0), travel(dL, TEAL_M, run_time=1.0), FadeIn(newep, shift=DOWN * 0.1)), run_time=5.0)
        x_cp = tick(False, 0.35).move_to(cp)
        self.beat("And if the control plane goes down, the proxies keep serving with the last config they received. You only lose the ability to change it.",
                  FadeOut(newep), cp.animate.set_opacity(0.35), Create(x_cp), xL.animate.set_opacity(0.25), xR.animate.set_opacity(0.25),
                  Succession(Wait(1.4), ride(out1, run_time=0.9),
                             ride(out2 + cross[1:] + in2[1:], run_time=1.2)),
                  run_time=5.4)

        # ---------- recap
        recap = VGroup(T("iptables catches the call  →  Envoy reads the original address", 26, YELLOW_M),
                       T("listener  →  route  →  cluster  →  endpoint  →  mTLS  →  :15006", 26, YELLOW_M)).arrange(DOWN, buff=0.22)
        recap.move_to([0, 2.45, 0])
        self.play(FadeOut(VGroup(xh, allx, ads, adsl, k8s, a_kc, cp, cpl, x_cp, xL, xR)), run_time=0.7)
        self.beat("iptables catches the call, and Envoy reads the original address. Then listener, route, cluster, endpoint, and mutual TLS to the other proxy. The control plane feeds it all over xDS.",
                  Write(recap[0]), Succession(Wait(2.6), Write(recap[1])), run_time=6.0)
        self.wait(1.0)
