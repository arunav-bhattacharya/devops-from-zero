import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Day 38, fifth pass (Venkat style), second video. Restaurant manager world.
# Concept: one kubectl apply, followed from the door to the stove. "created" means stored.
# Colours: terminal = WHITE, API server (the rail) = GOLD, etcd = GREEN, controllers = PURPLE,
# scheduler = BLUE, kubelet and containerd and Pods = TEAL, failure = RED, prompts = YELLOW.

SAY.extend([(r"\bnginx:1\.28\b", "engine X, one point two eight"), (r"\bapp\.yaml\b", "app dot yammel")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def glow(b, on=True):
    return b[0].animate.set_stroke(width=6 if on else 3)


def hop(*pts, color=YELLOW_M, run_time=0.6):
    return Succession(*[travel(Line(a, b), color, run_time) for a, b in zip(pts[:-1], pts[1:])])


def stream(a, b, color=GREY_B, n=3):
    return LaggedStart(*[travel(Line(a, b), color, 0.8) for _ in range(n)], lag_ratio=0.35)


def tbox(title, color, w, h, size=26):
    t = T(title, size)
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    return VGroup(r, t)


NODE_X = (-1.35, 1.85, 5.05)
NODE_Y = -2.6


def node(cx, name):
    r = RoundedRectangle(corner_radius=0.15, width=2.9, height=1.5, stroke_color=GREY_B, stroke_width=2).move_to([cx, NODE_Y, 0])
    r.set_fill(BLACK, opacity=1)
    lab = T(name, 22, GREY_B).next_to(r, UP, buff=0.08).align_to(r, RIGHT)
    kl = mbox("kubelet", TEAL_M, w=1.75, h=0.52, size=22).move_to([cx - 0.45, NODE_Y + 0.36, 0])
    cd = mbox("containerd", TEAL_M, w=1.75, h=0.52, size=22).move_to([cx - 0.45, NODE_Y - 0.36, 0])
    slot = DashedVMobject(Circle(radius=0.28, stroke_color=GREY_D, stroke_width=2), num_dashes=14).move_to([cx + 0.95, NODE_Y, 0])
    return VGroup(r, lab, kl, cd, slot)


class Base(VoiceScene):
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

    def pause_guess(self, pos=None):
        c = chip("pause and guess", YELLOW_M, 26).move_to(pos if pos is not None else [4.6, -3.0, 0])
        n2 = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        n1 = T("1", 30, YELLOW_M).move_to(n2)
        self.play(FadeIn(c, shift=UP * 0.1), FadeIn(n2), run_time=0.4)
        self.wait(0.8)
        self.play(ReplacementTransform(n2, n1), run_time=0.2)
        self.wait(0.8)
        self.play(FadeOut(c), FadeOut(n1), run_time=0.3)


class D38TicketRail(Base):
    def construct(self):
        self.title_card("kubectl said created. Is it running?", "following one order from the door to the stove")

        # ---------- 1. QUESTION: the manifest and the instant answer
        yl = VGroup(M("kind: Deployment", 26), M("name: web", 26), M("replicas: 2", 26, YELLOW_M), M("image: nginx:1.28", 26))
        yl.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        yr = RoundedRectangle(corner_radius=0.15, width=yl.width + 0.8, height=yl.height + 0.7, stroke_color=YELLOW_M, stroke_width=3).set_fill(tint(YELLOW_M, 0.08), 1)
        card = VGroup(yr, yl.move_to(yr)).move_to([-3.2, 0.3, 0])
        yname = M("app.yaml", 24, GREY_B).next_to(card, UP, buff=0.2)
        self.beat("Say you write a small file, a manifest, that asks for two copies of nginx. nginx is a web server, handy for tests.",
                  Create(yr), LaggedStart(*[Write(l) for l in yl], lag_ratio=0.25), FadeIn(yname), run_time=2.2)
        trect = RoundedRectangle(corner_radius=0.12, width=4.8, height=1.1, stroke_color=WHITE, stroke_width=2.5).set_fill(BLACK, 1).move_to([3.3, 0.3, 0])
        cmd = M("$ kubectl apply -f app.yaml", 22).move_to(trect).shift(UP * 0.2)
        resp = M("deployment.apps/web created", 22, GREEN_M).move_to(trect).shift(DOWN * 0.2)
        self.steps("You type kubectl apply. And in under a second, it answers. Created.",
                   (0.6, Create(trect)), (1.2, Write(cmd)), (0.8, Wait(0.8)), (0.8, Write(resp)))
        q = T("at this moment, is anything running?", 30, YELLOW_M).move_to([0, -2.2, 0])
        self.beat("So here is the question. At this very moment, is your app running?",
                  FadeIn(q, shift=UP * 0.1), run_time=1.2)
        self.pause_guess([0, -3.1, 0])

        # ---------- 2. steelman the remote-control model, then break it
        self.play(FadeOut(q), run_time=0.4)
        remote = VGroup(T("kubectl as a remote control?", 28, GREY_B), T("press the button, the containers start", 26, GREY_B)).arrange(DOWN, buff=0.15).move_to([0, -2.4, 0])
        self.beat("It is tempting to picture kubectl as a remote control. You press the button, it reaches into a machine, starts your containers, and created means done.",
                  FadeIn(remote, shift=UP * 0.1), run_time=1.4)
        gp = VGroup(M("$ kubectl get pods", 22, GREY_B),
                    M("NAME                  READY   STATUS", 22, GREY_B),
                    M("web-5d8f6b7c9-qm4zt   0/1     ContainerCreating", 22),
                    M("web-5d8f6b7c9-x7k2p   0/1     ContainerCreating", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        gp.move_to([0, -2.3, 0])
        self.beat("Let us check. Two seconds later, ask kubectl get pods.",
                  FadeOut(remote), FadeIn(gp[0]), run_time=1.0)
        hl = SurroundingRectangle(VGroup(gp[2][-20:], gp[3][-20:]), color=RED_M, buff=0.08, corner_radius=0.06)
        self.beat("Zero of one ready. Still being created. Well. Created, yes. Cooked, no.",
                  LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in gp[1:]], lag_ratio=0.3), Succession(Wait(1.0), Create(hl)), run_time=2.4)
        self.play(FadeOut(VGroup(gp, hl, card, yname)), VGroup(trect, cmd, resp).animate.move_to([-4.12, 2.85, 0]), run_time=0.9)
        resp.set_opacity(0)

        # ---------- 3. ANALOGY + MAP: the ticket rail, built part by part
        api = tbox("API server", GOLD_M, 2.5, 1.0)
        api_n = T("the ticket rail", 22, GREY_B)
        api.move_to([0, 2.85, 0])
        api_n.next_to(api, DOWN, buff=0.12)
        self.beat("Here is a better picture. In our restaurant, a waiter takes your order, pins the ticket on the rail, and says got it. Got it does not mean your soup is ready. It means your ticket is on the rail.",
                  Create(api[0]), run_time=1.4)
        self.beat("Kubernetes has a rail too. It is the API server, the front door that every request goes through.",
                  Write(api[1]), FadeIn(api_n), run_time=1.4)
        PL, PR, PT, PB = 2.2, 6.45, 3.35, 0.75
        prect = RoundedRectangle(corner_radius=0.15, width=PR - PL, height=PT - PB, stroke_color=GREEN_M, stroke_width=3).move_to([(PL + PR) / 2, (PT + PB) / 2, 0])
        prect.set_fill(tint(GREEN_M, 0.07), 1)
        phead = M("etcd", 24, GREEN_M).move_to([PL + 0.25, PT - 0.3, 0], aligned_edge=LEFT)
        prule = Line([PL + 0.12, PT - 0.6, 0], [PR - 0.12, PT - 0.6, 0], stroke_width=1.5, color=GREEN_M)
        etcd = VGroup(prect, phead, prule)
        etcd_n = T("the rail's memory", 22, GREY_B).next_to(phead, RIGHT, buff=0.4)
        a_ae = Arrow([1.25, 2.85, 0], [PL, 2.85, 0], buff=0.05, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        self.beat("Its memory is etcd, a database that holds the whole cluster state. Only the API server talks to it.",
                  Create(prect), FadeIn(phead), Create(prule), FadeIn(etcd_n), GrowArrow(a_ae), run_time=1.8)
        dctl = tbox("Deployment\ncontroller", PURPLE_M, 2.8, 1.0, 24).move_to([-4.9, 1.3, 0])
        rctl = tbox("ReplicaSet\ncontroller", PURPLE_M, 2.8, 1.0, 24).move_to([-4.9, 0.05, 0])
        ctl_n = T("the floor manager", 22, GREY_B).next_to(rctl, DOWN, buff=0.12)
        sch = tbox("scheduler", BLUE_M, 2.8, 0.8, 26).move_to([-4.9, -1.35, 0])
        sch_n = T("the head chef", 22, GREY_B).next_to(sch, DOWN, buff=0.12)
        self.beat("Around the rail stand the staff. The floor manager, played here by two controllers: the Deployment controller and the ReplicaSet controller.",
                  FadeIn(dctl, shift=RIGHT * 0.2), FadeIn(rctl, shift=RIGHT * 0.2), FadeIn(ctl_n), run_time=1.8)
        self.beat("The head chef, the scheduler, who hands each dish to a station.",
                  FadeIn(sch, shift=RIGHT * 0.2), FadeIn(sch_n), run_time=1.2)
        nodes = VGroup(*[node(x, f"node-{i + 1}") for i, x in enumerate(NODE_X)])
        cook_n = T("the station cook", 22, GREY_B).next_to(nodes[0][2], UP, buff=0.5)
        self.beat("And at each station, which Kubernetes calls a node, a cook: the kubelet. It never cooks with its own hands. It passes the job to containerd, which pulls images and starts containers.",
                  LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in nodes], lag_ratio=0.2), FadeIn(cook_n), run_time=2.4)

        # the one rule: everyone watches the rail
        self.play(FadeOut(VGroup(api_n, etcd_n, ctl_n, sch_n, cook_n)), run_time=0.6)
        w_d, w_r, w_s = [link(m, api, GREY_B, sw=2) for m in (dctl, rctl, sch)]
        kls = VGroup(*[DashedLine(n[2].get_top(), api.get_bottom() + RIGHT * (0.5 * (i - 1)), dash_length=0.08, stroke_width=2, color=GREY_B) for i, n in enumerate(nodes)])
        allw = VGroup(w_d, w_r, w_s, *kls)
        self.beat("Now, the one rule of this kitchen. Nobody calls anybody. Every part keeps one eye on the rail.",
                  LaggedStart(*[Create(w) for w in allw], lag_ratio=0.12), run_time=2.0)
        self.beat("That is called a watch. It is one long request, and the API server streams every change down it, as it happens.",
                  *[stream(w.get_end(), w.get_start(), GOLD_M, 2) for w in allw], run_time=2.6)

        # ---------- 4. SHOW: the seven steps
        def caption(n, text):
            g = VGroup(T(f"step {n} of 7", 24, GREY_B), T(text, 26, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            return g.move_to([-6.45, -2.75, 0], aligned_edge=LEFT)

        X0 = PL + 0.28
        IN = [PL, 2.85, 0]

        def rec(text, y, color=WHITE):
            return M(text, 22, color).move_to([X0, y, 0], aligned_edge=LEFT)

        cap = caption(1, "send the manifest")
        ych = chip("app.yaml", YELLOW_M, 22, mono=True).move_to([-4.12, 1.9, 0]).set_opacity(0)
        self.beat("Step one. kubectl reads its config file to find the cluster's address and your credentials. Then it sends the manifest to the API server.",
                  FadeIn(cap, shift=UP * 0.1), hop([-1.77, 2.85, 0], [-1.25, 2.85, 0], color=YELLOW_M, run_time=0.8), glow(api), run_time=2.0)
        checks = VGroup(*[VGroup(tick(True, 0.13), T(t, 24)).arrange(RIGHT, buff=0.15) for t in ("who are you?", "allowed?", "valid?")])
        checks.arrange(RIGHT, buff=0.35).move_to([0.4, 1.75, 0])
        checks.align_to(np.array([-2.7, 0, 0]), LEFT)
        r_dep = rec("Deployment web", PT - 0.95, YELLOW_M)
        self.steps("Step two. The API server checks who you are, and whether you may do this. It validates the object, and stores it in etcd. Then it answers created, and kubectl exits.",
                   (0.4, Transform(cap, caption(2, "check and store"))),
                   (1.6, LaggedStart(*[AnimationGroup(FadeIn(c[1]), Create(c[0])) for c in checks], lag_ratio=0.5)),
                   (0.8, hop(IN, [X0 + 1.0, PT - 0.95, 0], color=YELLOW_M, run_time=0.5), FadeIn(r_dep, shift=RIGHT * 0.1)),
                   (0.9, FadeOut(checks), resp.animate.set_opacity(1), glow(api, False)))
        self.beat("Remember the guess? We are only at step two. The ticket is on the rail, and no cook has touched it yet.",
                  *[Indicate(n[4], color=GREY_B, scale_factor=1.4) for n in nodes], Indicate(r_dep, color=YELLOW_M), run_time=2.0)

        r_rs = rec("ReplicaSet web-5d8f6b7c9", PT - 1.5, PURPLE_M)
        self.steps("Step three. The Deployment controller sees the new Deployment through its watch. It creates a ReplicaSet, a helper object that keeps a set number of identical Pods.",
                   (0.4, Transform(cap, caption(3, "make a ReplicaSet"))),
                   (1.0, stream(w_d.get_end(), w_d.get_start(), YELLOW_M, 1), glow(dctl)),
                   (1.6, Wait(1.6)),
                   (1.0, hop(w_d.get_start(), w_d.get_end(), IN, color=PURPLE_M, run_time=0.45), FadeIn(r_rs, shift=RIGHT * 0.1), glow(dctl, False)))
        r_p = [rec("Pod 1", PT - 1.85, TEAL_M), rec("Pod 2", PT - 2.3, TEAL_M)]
        s_p = [M("node: none", 22, RED_M).next_to(r_p[0], RIGHT, buff=0.3), M("node: none", 22, RED_M).next_to(r_p[1], RIGHT, buff=0.3)]
        self.steps("Step four. The ReplicaSet controller sees the ReplicaSet, and creates two Pod objects. A Pod wraps a container and gives it an address. These two have no node yet.",
                   (0.4, Transform(cap, caption(4, "make two Pods"))),
                   (1.0, stream(w_r.get_end(), w_r.get_start(), PURPLE_M, 1), glow(rctl)),
                   (1.0, hop(w_r.get_start(), w_r.get_end(), IN, color=TEAL_M, run_time=0.45), FadeIn(r_p[0], shift=RIGHT * 0.1), FadeIn(r_p[1], shift=RIGHT * 0.1), glow(rctl, False)),
                   (1.8, Wait(1.8)), (0.8, Write(s_p[0]), Write(s_p[1])))
        cross = tick(False, 0.5).move_to(nodes[2][0])
        bars = VGroup(*[Rectangle(width=wd, height=0.14, stroke_width=0, fill_color=BLUE_M, fill_opacity=0.9) for wd in (1.6, 1.3)])
        for b, n in zip(bars, nodes[:2]):
            b.move_to(n[0].get_corner(UL) + UP * 0.22 + RIGHT * 0.12, aligned_edge=LEFT)
        n_p = [M("node: node-1", 22, BLUE_M).next_to(r_p[0], RIGHT, buff=0.3), M("node: node-2", 22, BLUE_M).next_to(r_p[1], RIGHT, buff=0.3)]
        self.steps("Step five. The scheduler sees two Pods without a node. It filters out nodes that cannot take them, scores the rest, and writes a node name into each Pod.",
                   (0.4, Transform(cap, caption(5, "pick a node"))),
                   (1.0, stream(w_s.get_end(), w_s.get_start(), TEAL_M, 1), glow(sch)),
                   (1.0, nodes[2].animate.set_opacity(0.3), Create(cross)),
                   (0.9, *[GrowFromEdge(b, LEFT) for b in bars]),
                   (1.0, hop(w_s.get_start(), w_s.get_end(), IN, color=BLUE_M, run_time=0.45), Transform(s_p[0], n_p[0]), Transform(s_p[1], n_p[1])),
                   (0.4, glow(sch, False), FadeOut(bars)))
        pods = VGroup(*[Circle(radius=0.28, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.35), 1).move_to(n[4]) for n in nodes[:2]])
        self.steps("Step six. The kubelet on each chosen node sees a Pod given to it. It asks containerd to pull the image and start the container.",
                   (0.4, Transform(cap, caption(6, "start the containers"))),
                   (1.2, stream(kls[0].get_end(), kls[0].get_start(), BLUE_M, 1), stream(kls[1].get_end(), kls[1].get_start(), BLUE_M, 1), glow(nodes[0][2]), glow(nodes[1][2])),
                   (0.8, glow(nodes[0][2], False), glow(nodes[1][2], False), glow(nodes[0][3]), glow(nodes[1][3])),
                   (1.0, *[FadeOut(n[4]) for n in nodes[:2]], LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.3), glow(nodes[0][3], False), glow(nodes[1][3], False)))
        f_p = [M("node-1 Running", 22, GREEN_M).next_to(r_p[0], RIGHT, buff=0.3), M("node-2 Running", 22, GREEN_M).next_to(r_p[1], RIGHT, buff=0.3)]
        self.steps("Step seven. The kubelet reports back. The Pod is running, and here is its IP address. The API server stores that in the Pod's status.",
                   (0.4, Transform(cap, caption(7, "report back"))),
                   (1.0, hop(kls[0].get_start(), kls[0].get_end(), color=GREEN_M, run_time=0.9), hop(kls[1].get_start(), kls[1].get_end(), color=GREEN_M, run_time=0.9)),
                   (0.9, hop(IN, [X0 + 1.0, PT - 1.85, 0], color=GREEN_M, run_time=0.5), Transform(s_p[0], f_p[0]), Transform(s_p[1], f_p[1])))
        self.beat("Seven steps, and every one went through the rail. Nobody sent orders to anybody. Each part acted on what it found there.",
                  FadeOut(cap), allw.animate.set_stroke(GOLD_M, width=3), glow(api), run_time=1.8)
        self.play(allw.animate.set_stroke(GREY_B, width=2), glow(api, False), run_time=0.5)

        # ---------- 5. BREAK the "just phone each other" idea: why the rail
        self.beat("You might be thinking: wouldn't it be quicker if the scheduler just phoned the kubelet? Let us see why the rail wins. Think about the night something crashes.",
                  Indicate(w_s, color=YELLOW_M), run_time=1.6)
        sx = tick(False, 0.35).move_to(sch)
        pend = chip("new Pods: Pending", RED_M, 24).move_to([-4.9, -2.7, 0])
        self.beat("Say the scheduler stops. New Pods would wait in Pending, with no node, for as long as it is gone.",
                  sch.animate.set_opacity(0.3), Create(sx), FadeIn(pend, shift=UP * 0.1), run_time=1.6)
        self.beat("When it comes back, it does not need to remember where it was. It reads the rail again and carries on, as if nothing happened. The rail remembers, so nobody else has to.",
                  FadeOut(sx), sch.animate.set_opacity(1), FadeOut(pend), stream(w_s.get_end(), w_s.get_start(), GOLD_M, 3), run_time=2.4)
        ax = tick(False, 0.35).move_to(api)
        err = M("error: cannot reach cluster", 22, RED_M).move_to(resp)
        self.beat("And if the rail itself goes down? kubectl fails, but the containers that already run keep running.",
                  api.animate.set_opacity(0.3), Create(ax), FadeOut(resp), FadeIn(err), *[Indicate(p, color=TEAL_M) for p in pods], run_time=2.2)
        self.play(FadeOut(ax), api.animate.set_opacity(1), FadeOut(err), run_time=0.6)

        # ---------- 6. SHOW the proof, then NAME the guardrail
        stage = VGroup(trect, cmd, api, etcd, a_ae, dctl, rctl, sch, nodes, allw, pods, cross, r_dep, r_rs, *r_p, *s_p)
        self.play(FadeOut(stage), run_time=0.8)
        ev_cmd = M("$ kubectl get events", 26).move_to([0, 3.0, 0])
        rows = [("deployment-controller", "ScalingReplicaSet"), ("replicaset-controller", "SuccessfulCreate"),
                ("replicaset-controller", "SuccessfulCreate"), ("default-scheduler", "Scheduled"), ("default-scheduler", "Scheduled"),
                ("kubelet", "Pulling"), ("kubelet", "Pulled"), ("kubelet", "Created"), ("kubelet", "Started")]
        cols = [PURPLE_M] * 3 + [BLUE_M] * 2 + [TEAL_M] * 4
        head = VGroup(M("FROM", 24, GREY_B), M("REASON", 24, GREY_B))
        table = VGroup(head, *[VGroup(M(a, 24, c), M(b, 24)) for (a, b), c in zip(rows, cols)])
        for i, r in enumerate(table):
            r[0].move_to([-4.6, 2.3 - i * 0.5, 0], aligned_edge=LEFT)
            r[1].move_to([0.6, 2.3 - i * 0.5, 0], aligned_edge=LEFT)
        self.beat("You do not have to take my word for any of this. Each step leaves a short record called an event, and kubectl get events shows the whole chain, in order.",
                  Write(ev_cmd), FadeIn(head), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in table[1:]], lag_ratio=0.15), run_time=3.2)
        self.beat("Deployment controller, ReplicaSet controller, scheduler, then the kubelet. The same chain we just walked.",
                  Indicate(table[1][0], color=PURPLE_M), Indicate(table[2][0], color=PURPLE_M), Indicate(table[4][0], color=BLUE_M), Indicate(table[6][0], color=TEAL_M), run_time=2.0)
        stop = Line([-4.75, 2.3 - 3.5 * 0.5, 0], [4.2, 2.3 - 3.5 * 0.5, 0], color=RED_M, stroke_width=4)
        stuck = chip("Pending, no node name", RED_M, 24).next_to(stop, RIGHT, buff=0.25).shift(LEFT * 0.0)
        stuck.move_to([3.6, stop.get_center()[1] - 0.55, 0])
        self.beat("And when something is stuck, the chain simply stops at one step. A Pod that fits on no node stays Pending, with no node name, and its events say why.",
                  Create(stop), table[4:].animate.set_opacity(0.2), FadeIn(stuck, shift=LEFT * 0.2), run_time=2.4)
        self.beat("That is why, on a team, kubectl get events is often the first command anyone runs after a bad release.",
                  Indicate(ev_cmd, color=WHITE), run_time=1.4)

        # ---------- 7. MORAL + quick check
        self.play(FadeOut(VGroup(ev_cmd, table, stop, stuck)), run_time=0.7)
        moral = VGroup(T("created means stored, not running", 32, YELLOW_M),
                       T("everyone watches the rail and does their part", 30, GOLD_M)).arrange(DOWN, buff=0.35).move_to([0, 1.5, 0])
        self.steps("So the moral of the story. kubectl apply hangs a ticket on the rail. Created means stored, not running. Then everyone watches the rail and does their part, a few seconds later. So after an apply, check with kubectl get pods.",
                   (0.8, FadeIn(moral[0], shift=UP * 0.1)), (2.4, Wait(2.4)), (0.8, FadeIn(moral[1], shift=UP * 0.1)))
        check = T("Quick check: the scheduler is down. You apply a Deployment.", 28, YELLOW_M)
        check2 = T("Does kubectl still say created?", 28, YELLOW_M)
        cg = VGroup(check, check2).arrange(DOWN, buff=0.2).move_to([0, -0.9, 0])
        self.beat("One quick check. The scheduler is down, and you apply a new Deployment. Does kubectl still say created?",
                  FadeIn(cg, shift=UP * 0.1), run_time=1.6)
        self.pause_guess([0, -2.3, 0])
        ans = VGroup(T("Yes. Step two only needs the API server and etcd.", 26),
                     T("The Pods wait in Pending until the head chef is back.", 26, GREY_B)).arrange(DOWN, buff=0.18).move_to([0, -2.5, 0])
        self.beat("Yes. Step two only needs the API server and etcd. The Pods wait in Pending until the head chef is back.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.2)
