import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

PODY, TAGY = -1.65, -1.07


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def podbox(text, x, color=BLUE_M):
    r = RoundedRectangle(corner_radius=0.1, width=1.9, height=0.6, stroke_color=color, stroke_width=3).move_to([x, PODY, 0])
    r.set_fill(tint(color, 0.2), opacity=1)
    return VGroup(r, M(text, 20).move_to(r))


def tag(text, x):
    return M(text, 20, GREY_B).move_to([x, TAGY, 0])


def noderect(cx, name):
    r = RoundedRectangle(corner_radius=0.15, width=6.35, height=3.4, stroke_color=GREY_B, stroke_width=2).move_to([cx, -2.0, 0])
    lab = T(name, 20, GREY_B).move_to(r.get_corner(UL) + [0.15, -0.14, 0], aligned_edge=UL)
    return VGroup(r, lab)


def rules(cx, ips):
    t = T("kube-proxy rules", 20, PURPLE_M)
    l1 = VGroup(M("10.96.171.215:80", 20, TEAL_M), T("goes to one of", 20, GREY_B)).arrange(RIGHT, buff=0.2)
    l2 = M("  ".join(ip + ":8000" for ip in ips), 20, BLUE_M)
    g = VGroup(t, l1, l2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    r = RoundedRectangle(corner_radius=0.1, width=5.9, height=1.1, stroke_color=PURPLE_M, stroke_width=2.5).move_to([cx, -2.98, 0])
    r.set_fill(tint(PURPLE_M, 0.1), opacity=1)
    g.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.2)
    return VGroup(r, g)


class D41Service(VoiceScene):
    def construct(self):
        self.title_card("How a Service finds its Pods", "a stable name in front, Pods coming and going behind")

        # Pods with their own IPs, on two nodes
        n1, n2 = noderect(-3.625, "devops-worker"), noderect(3.625, "devops-worker2")
        pa, pb, pc = podbox("10.244.1.3", -5.0), podbox("10.244.1.5", -2.2), podbox("10.244.2.4", 1.9)
        ta, tb, tc = tag("app: hello-devops", -5.0), tag("app: hello-devops", -2.2), tag("app: hello-devops", 1.9)
        self.beat("Every Pod gets its own IP address. Here are three hello-devops Pods, on two nodes.",
                  FadeIn(n1), FadeIn(n2), LaggedStart(*[FadeIn(VGroup(p, t), shift=UP * 0.15) for p, t in ((pa, ta), (pb, tb), (pc, tc))], lag_ratio=0.25), run_time=2.2)

        cfg = VGroup(M("url: http://", 24, GREY_B), M("10.244.1.5", 24, BLUE_M), M(":8000", 24, GREY_B)).arrange(RIGHT, buff=0.05).move_to([0, 2.3, 0])
        self.beat("Say a config file points straight at one of them.",
                  FadeIn(cfg, shift=DOWN * 0.15), Indicate(pb, color=BLUE_M), run_time=1.4)
        pb2 = podbox("10.244.1.7", -2.2)
        self.beat("But Pod IPs do not last. Rollouts, scaling and failures replace Pods all the time.",
                  pb.animate.set_stroke(RED_M).set_opacity(0.3), run_time=1.4)
        self.beat("The new Pod gets a new IP. The config file now points at nothing.",
                  FadeOut(pb), FadeIn(pb2, scale=0.8), cfg[1].animate.set_color(RED_M), run_time=1.6)
        pb = pb2
        xc = tick(False, 0.3).move_to(cfg)
        self.beat("So never put a Pod IP in a config file. Put a Service in front of the Pods instead.",
                  Create(xc), run_time=1.0)
        self.play(FadeOut(VGroup(cfg, xc)), run_time=0.5)

        # the Service: stable ClusterIP and DNS name
        sl = VGroup(T("Service hello-devops", 26),
                    M("ClusterIP 10.96.171.215", 22, TEAL_M),
                    VGroup(M("port 80", 20, GREY_B), T("to", 20, GREY_B), M("targetPort 8000", 20, GREY_B)).arrange(RIGHT, buff=0.15))
        sl.arrange(DOWN, buff=0.15)
        srect = RoundedRectangle(corner_radius=0.15, width=4.4, height=sl.height + 0.45, stroke_color=TEAL_M, stroke_width=3)
        srect.set_fill(tint(TEAL_M, 0.1), opacity=1)
        svc = VGroup(srect, sl.move_to(srect)).move_to([0, 2.3, 0])
        dns = M("hello-devops.hello.svc.cluster.local", 20, TEAL_M).move_to([0, 3.45, 0])
        self.beat("A Service gives a changing set of Pods one stable virtual IP address, and one DNS name.",
                  Create(srect), Write(sl[0]), FadeIn(sl[1:]), Write(dns), run_time=2.2)
        self.beat("The API server gives it an address from the Service range. That address is its ClusterIP, and it stays put while Pods come and go.",
                  Indicate(sl[1], color=TEAL_M), run_time=1.4)
        self.beat("Other Pods call it on port 80. The app inside each Pod listens on port 8000.",
                  Indicate(sl[2], color=WHITE), run_time=1.4)
        self.beat("The full name adds the namespace, hello, and the cluster suffix. From the same namespace, the short name hello-devops is enough.",
                  Indicate(dns, color=TEAL_M, scale_factor=1.05), run_time=1.8)

        # the selector
        sel_l = VGroup(T("selector", 22, GREY_B), M("app: hello-devops", 22, YELLOW_M)).arrange(DOWN, buff=0.15)
        sel_r = RoundedRectangle(corner_radius=0.12, width=sel_l.width + 0.5, height=sel_l.height + 0.45, stroke_color=YELLOW_M, stroke_width=2.5)
        sel_r.set_fill(tint(YELLOW_M, 0.08), opacity=1)
        sel = VGroup(sel_r, sel_l.move_to(sel_r)).move_to([-4.75, 2.3, 0])
        self.beat("How does the Service know which Pods are its own? With a label selector, just like a Deployment.",
                  Create(sel_r), FadeIn(sel_l), run_time=1.6)
        self.beat("It takes every ready Pod labeled app: hello-devops.",
                  LaggedStart(*[t.animate.set_color(YELLOW_M) for t in (ta, tb, tc)], lag_ratio=0.25), run_time=1.4)
        cl = podbox("client", 4.6, GREY_B)
        tcl = tag("app: client", 4.6)
        xcl = tick(False, 0.15).next_to(tcl, RIGHT, buff=0.12)
        self.beat("A Pod with another label, like this client, is left out.",
                  FadeIn(VGroup(cl, tcl), shift=UP * 0.15), run_time=1.2)
        self.play(Create(xcl), run_time=0.5)

        # the EndpointSlice
        ex0, ex1 = 2.84, 5.25
        ph = M("EndpointSlice", 22, GREEN_M)
        ips = [("10.244.1.3", pa), ("10.244.1.7", pb), ("10.244.2.4", pc)]
        rows = VGroup(*[VGroup(M(ip + ":8000", 20), T("ready", 22, GREEN_M)) for ip, _ in ips])
        prect = RoundedRectangle(corner_radius=0.15, width=4.1, height=1.9, stroke_color=GREEN_M, stroke_width=3).move_to([4.7, 2.26, 0])
        prect.set_fill(tint(GREEN_M, 0.07), opacity=1)
        ph.move_to([ex0, 2.95, 0], aligned_edge=LEFT)
        for i, r in enumerate(rows):
            r[0].move_to([ex0, 2.5 - 0.41 * i, 0], aligned_edge=LEFT)
            r[1].move_to([ex1, 2.5 - 0.41 * i, 0], aligned_edge=LEFT)
        self.beat("The EndpointSlice controller watches the Pods. It keeps a list: the IP and port of each matching Pod, and whether it is ready.",
                  Create(prect), Write(ph),
                  LaggedStart(*[TransformFromCopy(p[1], r[0]) for (_, p), r in zip(ips, rows)], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(r[1]) for r in rows], lag_ratio=0.3), run_time=2.6)
        self.beat("Whenever a Pod comes, goes, or changes readiness, the controller updates the list.",
                  Indicate(rows, color=GREEN_M, scale_factor=1.04), run_time=1.2)
        self.beat("Say this Pod starts failing its readiness check. It keeps running, but its entry is marked not ready.",
                  pc[0].animate.set_stroke(RED_M), Transform(rows[2][1], T("not ready", 22, RED_M).move_to(rows[2][1], aligned_edge=LEFT)),
                  rows[2][0].animate.set_opacity(0.45), run_time=1.8)

        # kube-proxy rules on every node
        rl1, rl2 = rules(-3.625, ["10.244.1.3", "10.244.1.7"]), rules(3.625, ["10.244.1.3", "10.244.1.7"])
        self.beat("The third piece is kube-proxy, on every node. It watches Services and EndpointSlices, and writes packet rules into the node's Linux kernel.",
                  LaggedStart(FadeIn(rl1, shift=UP * 0.15), FadeIn(rl2, shift=UP * 0.15), lag_ratio=0.3), run_time=2.2)
        self.beat("The rules say: traffic for the ClusterIP, port 80, goes to one of these ready Pods, on port 8000. The Pod that is not ready is skipped.",
                  Indicate(rl1[1][1][0], color=TEAL_M), Indicate(rl2[1][1][0], color=TEAL_M), Indicate(rl1[1][2], color=BLUE_M), Indicate(rl2[1][2], color=BLUE_M), run_time=2.4)
        self.beat("So the ClusterIP lives on no network card. It exists only as these rules.",
                  Indicate(sl[1], color=TEAL_M), run_time=1.2)

        # follow one call
        coredns = mbox("CoreDNS", GOLD_M, w=1.6, h=0.55, size=22).move_to([5.9, 0.6, 0])
        self.beat("Now follow one call. The client sends a request to hello-devops, by name.",
                  cl[0].animate.set_stroke(WHITE, width=5), run_time=1.0)
        ans = VGroup(M("hello-devops", 20, WHITE), T("is", 20, GREY_B), M("10.96.171.215", 20, TEAL_M)).arrange(RIGHT, buff=0.15)
        ans = VGroup(SurroundingRectangle(ans, color=GOLD_M, buff=0.14, corner_radius=0.08, stroke_width=2).set_fill(BLACK, opacity=1), ans).move_to([2.55, 0.6, 0])
        dpath = [cl.get_right(), [6.3, PODY, 0], [6.3, 0.33, 0]]
        self.beat("First, CoreDNS, the cluster's DNS server, turns the name into the ClusterIP.",
                  FadeIn(coredns), Succession(*[travel(Line(a, b), GOLD_M, 0.5) for a, b in zip(dpath[:-1], dpath[1:])]), run_time=1.8)
        self.play(FadeIn(ans, shift=LEFT * 0.2), Indicate(sl[1], color=TEAL_M), run_time=1.0)

        a1 = Arrow(cl.get_bottom(), [4.6, -2.43, 0], buff=0.04, stroke_width=4, color=YELLOW_M, max_tip_length_to_length_ratio=0.3)
        self.beat("The packet leaves for the ClusterIP, port 80. The rules in the kernel of the client's own node catch it.",
                  GrowArrow(a1), cl[0].animate.set_stroke(GREY_B, width=3), run_time=1.2)
        self.play(rl2[0].animate.set_stroke(width=6), run_time=0.6)
        a2 = Arrow([2.6, -2.43, 0], pb.get_bottom(), buff=0.04, stroke_width=4, color=YELLOW_M, max_tip_length_to_length_ratio=0.1)
        self.beat("They pick one ready Pod, and send the packet to its IP, on port 8000. Here, a Pod on the other node.",
                  GrowArrow(a2), run_time=1.4)
        self.play(travel(a1, YELLOW_M, 0.4), run_time=0.5)
        self.play(travel(a2, YELLOW_M, 0.8), rl2[0].animate.set_stroke(width=2.5), run_time=0.9)
        self.play(Indicate(pb, color=YELLOW_M), run_time=0.8)

        # per connection, not per request
        self.beat("kube-proxy itself carries nothing. The kernel picks a Pod on a connection's first packet, and keeps it until the connection closes.",
                  LaggedStart(*[travel(Line(a2.get_start(), a2.get_end()), YELLOW_M, 0.8) for _ in range(4)], lag_ratio=0.4), run_time=2.6)
        a3 = Arrow([2.6, -2.43, 0], pa.get_bottom(), buff=0.04, stroke_width=4, color=GOLD_M, max_tip_length_to_length_ratio=0.06)
        self.beat("A new connection may land on another Pod. That is how the load spreads.",
                  a2.animate.set_opacity(0.3), GrowArrow(a3), run_time=1.2)
        self.play(LaggedStart(*[travel(Line(a3.get_start(), a3.get_end()), GOLD_M, 0.9) for _ in range(3)], lag_ratio=0.4),
                  Indicate(pa, color=GOLD_M), run_time=2.0)

        # recap
        self.play(FadeOut(VGroup(a1, a2, a3, ans)), run_time=0.5)
        self.beat("Pods come and go. The name and the ClusterIP stay.",
                  Indicate(dns, color=TEAL_M, scale_factor=1.04), Indicate(sl[1], color=TEAL_M), run_time=1.4)
        self.beat("The EndpointSlice tracks the ready Pods, and kube-proxy's rules on every node send each call to one of them.",
                  Indicate(rows, color=GREEN_M, scale_factor=1.04), rl1[0].animate.set_stroke(width=5), rl2[0].animate.set_stroke(width=5), run_time=2.2)
        self.wait(1.0)
