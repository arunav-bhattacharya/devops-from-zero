import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

DIM = 0.22


def glow(b, on=True):
    return b[0].animate.set_stroke(width=6 if on else 3)


def hop(*pts, color=YELLOW_M, run_time=0.8):
    """A dot that runs through a list of points, one leg after another."""
    return Succession(*[travel(Line(a, b), color, run_time) for a, b in zip(pts[:-1], pts[1:])])


def stream(a, b, color=GREY_B, n=3):
    """A few dots flowing from a to b, like changes streamed down a watch."""
    return LaggedStart(*[travel(Line(a, b), color, 0.9) for _ in range(n)], lag_ratio=0.35)


def node(cx, name):
    r = RoundedRectangle(corner_radius=0.15, width=3.2, height=1.75, stroke_color=GREY_B, stroke_width=2).move_to([cx, -2.75, 0])
    r.set_fill(BLACK, opacity=1)
    lab = T(name, 20, GREY_B).next_to(r, UP, buff=0.1).align_to(r, RIGHT).shift(LEFT * 0.12)
    kl = mbox("kubelet", TEAL_M, w=1.75, h=0.5, size=20).move_to([cx - 0.55, -2.3, 0])
    cd = mbox("containerd", TEAL_M, w=1.75, h=0.5, size=20).move_to([cx - 0.55, -3.2, 0])
    a = Arrow(kl.get_bottom(), cd.get_top(), buff=0.04, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.35)
    slot = DashedVMobject(Circle(radius=0.3, stroke_color=GREY_D, stroke_width=2), num_dashes=14).move_to([cx + 1.0, -2.75, 0])
    return VGroup(r, lab, kl, cd, a, slot)


class D38Apply(VoiceScene):
    def construct(self):
        self.title_card("What happens when you run kubectl apply", "seven steps, and every one goes through the API server")

        # the manifest
        ylines = VGroup(M("kind: Deployment", 26), M("name: web", 26), M("replicas: 2", 26, YELLOW_M), M("image: nginx:1.28", 26))
        ylines.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        yrect = RoundedRectangle(corner_radius=0.15, width=ylines.width + 0.8, height=ylines.height + 0.7, stroke_color=YELLOW_M, stroke_width=3)
        yrect.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(YELLOW_M), 0.08), opacity=1)
        ycard = VGroup(yrect, ylines.move_to(yrect))
        yname = T("app.yaml", 26, GREY_B).next_to(ycard, UP, buff=0.25)
        self.beat("Say you write a Deployment that asks for two copies of nginx.",
                  Create(yrect), LaggedStart(*[Write(l) for l in ylines], lag_ratio=0.25), FadeIn(yname), run_time=2.0)

        # the whole map, dim: terminal, control plane, nodes
        trect = RoundedRectangle(corner_radius=0.12, width=4.2, height=1.0, stroke_color=GREY_B, stroke_width=2.5).move_to([-4.7, 3.0, 0])
        trect.set_fill(BLACK, opacity=1)
        cmd = M("$ kubectl apply -f app.yaml", 20).move_to([-4.7, 3.18, 0]).align_to(trect, LEFT).shift(RIGHT * 0.15)
        resp = M("deployment.apps/web created", 20, GREEN_M).move_to([-4.7, 2.8, 0]).align_to(cmd, LEFT)
        api = box("API server", GOLD_M, w=2.3, h=0.8, size=26).move_to([-0.25, 3.0, 0])
        PL = 2.15  # left edge of the etcd panel
        prect = RoundedRectangle(corner_radius=0.15, width=6.8 - PL, height=3.0, stroke_color=GREEN_M, stroke_width=3).move_to([(PL + 6.8) / 2, 1.85, 0])
        prect.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(GREEN_M), 0.07), opacity=1)
        phead = M("etcd", 22, GREEN_M).move_to([4.5, 3.12, 0]).align_to(prect, LEFT).shift(RIGHT * 0.22)
        prule = Line([PL + 0.12, 2.9, 0], [6.68, 2.9, 0], stroke_width=1.5, color=GREEN_M)
        etcd = VGroup(prect, phead, prule)
        dctl = box("Deployment\ncontroller", PURPLE_M, w=2.3, h=1.0, size=24).move_to([-5.3, 1.35, 0])
        rctl = box("ReplicaSet\ncontroller", PURPLE_M, w=2.3, h=1.0, size=24).move_to([-5.3, 0.0, 0])
        sch = box("scheduler", PURPLE_M, w=2.3, h=0.8, size=24).move_to([-5.3, -1.3, 0])
        nodes = VGroup(node(-1.8, "node-1"), node(1.6, "node-2"), node(5.0, "node-3"))
        cluster = VGroup(api, etcd, dctl, rctl, sch, nodes)
        ychip = chip("app.yaml", YELLOW_M, 20, mono=True).move_to([-2.75, 2.0, 0])
        self.beat("You run kubectl apply, against a cluster like this one. Interviewers love to ask what happens next. So let us follow it, step by step.",
                  ReplacementTransform(VGroup(ycard, yname), ychip), Create(trect), Write(cmd),
                  FadeIn(cluster.set_opacity(DIM), lag_ratio=0.05), run_time=2.6)

        def lit(*ms):
            return [m.animate.set_opacity(1) for m in ms]

        # step caption, bottom left
        def caption(n, text):
            g = VGroup(T(f"step {n} of 7", 24, GREY_B), T(text, 28, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            return g.move_to([-6.75, -2.6, 0], aligned_edge=LEFT)

        # step 1: kubectl
        cap = caption(1, "send the YAML")
        conf = chip("~/.kube/config", GREY_B, 20, mono=True).next_to(ychip, DOWN, buff=0.25)
        self.beat("Step one. kubectl reads the config file in your home folder, to find the cluster and your credentials.",
                  FadeIn(cap, shift=UP * 0.15), FadeIn(conf, shift=UP * 0.15), run_time=1.6)
        a_ka = Arrow([-2.6, 3.0, 0], [-1.4, 3.0, 0], buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.22)
        https = T("HTTPS", 20, GREY_B).next_to(a_ka, UP, buff=0.12)
        self.beat("Then it sends the YAML to the API server, over HTTPS.",
                  FadeOut(conf), *lit(api), GrowArrow(a_ka), FadeIn(https),
                  ychip.animate.scale(0.8).move_to(api.get_bottom() + DOWN * 0.4), run_time=2.0)

        # step 2: checks, storage, answer
        checks = VGroup(*[VGroup(tick(True, 0.13), T(t, 24)).arrange(RIGHT, buff=0.18) for t in ("who are you?", "allowed?", "valid?")])
        checks.arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(api, DOWN, buff=0.35)
        self.beat("Step two. The API server checks who you are, and whether you may do this.",
                  Transform(cap, caption(2, "check and store")), FadeOut(ychip),
                  LaggedStart(FadeIn(checks[0][1]), Create(checks[0][0]), FadeIn(checks[1][1]), Create(checks[1][0]), lag_ratio=0.4), run_time=2.0)

        a_ae = Arrow([0.9, 3.0, 0], [PL, 3.0, 0], buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        X0 = PL + 0.25
        IN = [PL, 3.0, 0]

        def rec(text, y, color=WHITE, indent=0.0):
            return M(text, 20, color).move_to([4.5, y, 0]).align_to([X0 + indent, 0, 0], LEFT)

        r_dep = rec("Deployment web", 2.6, YELLOW_M)
        self.beat("It validates the object, and stores it in etcd, the cluster's database.",
                  FadeIn(checks[2][1]), Create(checks[2][0]), GrowArrow(a_ae), *lit(etcd), run_time=1.8)
        self.play(hop(api.get_right(), IN, [X0 + 0.9, 2.6, 0], color=YELLOW_M, run_time=0.5), FadeIn(r_dep, shift=RIGHT * 0.15), run_time=1.0)
        self.beat("Then it answers created, and kubectl exits.",
                  FadeOut(checks), hop(api.get_left(), [-2.6, 3.0, 0], color=GREEN_M, run_time=0.6), Write(resp), run_time=1.4)

        self.beat("That took under a second. But look at the nodes. Nothing runs there yet. Your request is only stored.",
                  *lit(nodes), run_time=1.6)
        self.play(*[Indicate(n[5], color=GREY_B, scale_factor=1.3) for n in nodes], Indicate(r_dep, color=YELLOW_M), run_time=1.2)

        # step 3: Deployment controller
        w_d, w_r, w_s = [link(m, api, GREY_B, sw=2) for m in (dctl, rctl, sch)]
        ang = np.arctan2(api.get_center()[1] - dctl.get_center()[1], api.get_center()[0] - dctl.get_center()[0])
        wlab = T("watch", 20, GREY_B).rotate(ang).move_to(interpolate(w_d.get_start(), w_d.get_end(), 0.42) + 0.2 * np.array([np.sin(ang), -np.cos(ang), 0]))
        self.beat("Step three. The Deployment controller watches the API server. A watch is one long request. The API server streams every change down it.",
                  Transform(cap, caption(3, "make a ReplicaSet")), *lit(dctl), Create(w_d), FadeIn(wlab), run_time=2.0)
        self.play(stream(w_d.get_end(), w_d.get_start()), run_time=1.4)
        r_rs = rec("ReplicaSet web-5d8f6b7c9", 2.18, PURPLE_M)
        self.beat("It sees the new Deployment, and creates a ReplicaSet. That is a helper object that keeps a set number of identical Pods.",
                  glow(dctl), Indicate(r_dep, color=YELLOW_M), run_time=1.2)
        self.play(hop(w_d.get_start(), w_d.get_end(), IN, color=PURPLE_M, run_time=0.6), FadeIn(r_rs, shift=RIGHT * 0.15), glow(dctl, False), run_time=1.4)

        # step 4: ReplicaSet controller
        r_p1 = rec("Pod web-5d8f6b7c9-qm4zt", 1.76, BLUE_M)
        r_p2 = rec("Pod web-5d8f6b7c9-x7k2p", 0.98, BLUE_M)
        s_p1 = rec("node: none", 1.4, RED_M, 0.3)
        s_p2 = rec("node: none", 0.62, RED_M, 0.3)
        self.beat("Step four. The ReplicaSet controller sees the ReplicaSet, and creates two Pod objects.",
                  Transform(cap, caption(4, "make two Pods")), *lit(rctl), Create(w_r), run_time=1.6)
        self.play(glow(rctl), Indicate(r_rs, color=PURPLE_M), run_time=0.8)
        self.play(hop(w_r.get_start(), w_r.get_end(), IN, color=BLUE_M, run_time=0.6),
                  LaggedStart(FadeIn(r_p1, shift=RIGHT * 0.15), FadeIn(r_p2, shift=RIGHT * 0.15), lag_ratio=0.5), glow(rctl, False), run_time=1.6)
        self.beat("They have no node yet.", LaggedStart(Write(s_p1), Write(s_p2), lag_ratio=0.4), run_time=1.0)

        # step 5: scheduler
        self.beat("Step five. The scheduler sees two Pods without a node.",
                  Transform(cap, caption(5, "pick a node")), *lit(sch), Create(w_s), run_time=1.4)
        self.play(glow(sch), Indicate(s_p1, color=RED_M), Indicate(s_p2, color=RED_M), run_time=0.9)
        cross = tick(False, 0.55).move_to(nodes[2][0])
        self.beat("It filters out nodes that cannot take them.",
                  nodes[2].animate.set_opacity(0.3), Create(cross), run_time=1.2)
        bars = VGroup(*[Rectangle(width=wd, height=0.14, stroke_width=0, fill_color=YELLOW_M, fill_opacity=0.9)
                        for wd in (1.25, 1.1)])
        for b, n in zip(bars, nodes[:2]):
            b.move_to(n[0].get_corner(UL) + UP * 0.2, aligned_edge=LEFT).shift(RIGHT * 0.12)
        self.beat("It scores the rest.", *[GrowFromEdge(b, LEFT) for b in bars], run_time=1.0)
        n_p1 = rec("node: node-1", 1.4, TEAL_M, 0.3)
        n_p2 = rec("node: node-2", 0.62, TEAL_M, 0.3)
        self.beat("And it writes a node name into each Pod.",
                  hop(w_s.get_start(), w_s.get_end(), IN, color=TEAL_M, run_time=0.6),
                  Transform(s_p1, n_p1), Transform(s_p2, n_p2), run_time=1.8)
        self.play(glow(sch, False), FadeOut(bars), run_time=0.5)

        # step 6: kubelets start the containers
        kls = VGroup(*[link(n[2], api, GREY_B, sw=2) for n in nodes[:2]])
        self.beat("Step six. The kubelet on each chosen node sees a Pod assigned to it.",
                  Transform(cap, caption(6, "start containers")), Create(kls), run_time=1.4)
        self.play(stream(kls[0].get_end(), kls[0].get_start(), TEAL_M, 2), stream(kls[1].get_end(), kls[1].get_start(), TEAL_M, 2),
                  glow(nodes[0][2]), glow(nodes[1][2]), run_time=1.4)
        pods = VGroup(*[Circle(radius=0.3, stroke_color=BLUE_M, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(BLUE_M), 0.3), opacity=1).move_to(n[5]) for n in nodes[:2]])
        a_cp = VGroup(*[Arrow(n[3].get_right(), n[5].get_left(), buff=0.05, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.35) for n in nodes[:2]])
        self.beat("It asks containerd to pull the image, and start the container.",
                  *[travel(n[4], TEAL_M, 0.6) for n in nodes[:2]], glow(nodes[0][2], False), glow(nodes[1][2], False),
                  glow(nodes[0][3]), glow(nodes[1][3]), run_time=1.2)
        self.play(*[GrowArrow(a) for a in a_cp], *[FadeOut(n[5]) for n in nodes[:2]], LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.3),
                  glow(nodes[0][3], False), glow(nodes[1][3], False), run_time=1.2)

        # step 7: status flows back
        self.beat("Step seven. The kubelet reports back. The Pod is running, and here is its IP address.",
                  Transform(cap, caption(7, "report status")),
                  hop(kls[0].get_start(), kls[0].get_end(), color=GREEN_M, run_time=0.9), hop(kls[1].get_start(), kls[1].get_end(), color=GREEN_M, run_time=0.9), run_time=2.0)
        f_p1 = rec("node-1  Running  10.244.1.3", 1.4, GREEN_M, 0.25)
        f_p2 = rec("node-2  Running  10.244.2.4", 0.62, GREEN_M, 0.25)
        self.beat("The API server stores that in the Pod's status.",
                  hop(api.get_right(), IN, color=GREEN_M, run_time=0.6), Transform(s_p1, f_p1), Transform(s_p2, f_p2), run_time=1.6)

        # who talks to whom
        allw = VGroup(w_d, w_r, w_s, kls[0], kls[1])
        self.beat("Now look at who talked to whom. Every step went through the API server.",
                  FadeOut(cap), allw.animate.set_stroke(GOLD_M, width=3), glow(api), run_time=1.6)
        self.beat("No part sent orders to another. Each one acted on what it found there.",
                  *[stream(w.get_end(), w.get_start(), GOLD_M, 2) for w in allw], run_time=2.0)
        self.wait(0.4)

        # events
        stage = VGroup(trect, cmd, resp, a_ka, https, a_ae, r_dep, r_rs, r_p1, r_p2, s_p1, s_p2,
                       w_d, w_r, w_s, wlab, kls, pods, a_cp, cross, cluster)
        self.play(FadeOut(stage), run_time=0.8)
        ev_cmd = M("$ kubectl get events", 26).move_to(UP * 3.0)
        rows = [("deployment-controller", "ScalingReplicaSet"), ("replicaset-controller", "SuccessfulCreate"),
                ("replicaset-controller", "SuccessfulCreate"), ("default-scheduler", "Scheduled"), ("default-scheduler", "Scheduled"),
                ("kubelet", "Pulling"), ("kubelet", "Pulled"), ("kubelet", "Created"), ("kubelet", "Started")]
        cols = [PURPLE_M] * 5 + [TEAL_M] * 4
        head = VGroup(M("FROM", 24, GREY_B), M("REASON", 24, GREY_B))
        table = VGroup(head, *[VGroup(M(a, 24, c), M(b, 24)) for (a, b), c in zip(rows, cols)])
        for i, r in enumerate(table):
            r[0].move_to([-4.6, 2.2 - i * 0.5, 0], aligned_edge=LEFT)
            r[1].move_to([0.4, 2.2 - i * 0.5, 0], aligned_edge=LEFT)
        self.beat("Each step also leaves a short record, called an event. kubectl get events shows the whole chain, in order.",
                  Write(ev_cmd), FadeIn(head), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in table[1:]], lag_ratio=0.15), run_time=3.0)
        stop = Line([-4.75, 2.2 - 3.5 * 0.5, 0], [3.6, 2.2 - 3.5 * 0.5, 0], color=RED_M, stroke_width=4)
        pend = chip("Pending, no node", RED_M, 24).next_to(stop, RIGHT, buff=0.3)
        self.beat("If a step cannot happen, the chain stops there. A Pod that fits on no node stays Pending, with no node name. Its events say why.",
                  Create(stop), table[4:].animate.set_opacity(0.2), FadeIn(pend, shift=LEFT * 0.2), run_time=2.4)
        recap = T("kubectl apply stores your wish. The rest of the cluster makes it real.", 30, YELLOW_M).to_edge(DOWN, buff=0.6)
        self.beat("So kubectl apply only stores your wish. The controllers, the scheduler and the kubelet make it real, a few seconds later.",
                  FadeOut(stop), FadeOut(pend), table[4:].animate.set_opacity(1), FadeIn(recap, shift=UP * 0.15), run_time=2.0)
        self.wait(1.0)
