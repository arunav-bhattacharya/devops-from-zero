import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bOOMKilled\b", "O O M killed"), (r"\bOOM\b", "O O M"), (r"\bHorizontalPodAutoscaler\b", "horizontal pod autoscaler"),
            (r"\bHPA\b", "H P A"), (r"\bSIGKILL\b", "sig kill"), (r"\bcgroups\b", "C groups"), (r"/healthz\b", "health Z"),
            (r"/readyz\b", "ready Z"), (r"\bminReplicas\b", "min replicas"), (r"\bmaxReplicas\b", "max replicas"),
            (r"\bmetrics-server\b", "metrics server"), (r"\bceil\b", "ceiling")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def card(lines, color, size=22, pad=0.4):
    g = VGroup(*[M(t, size, c) for t, c, _ in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    for m, (_, _, ind) in zip(g, lines):
        m.shift(RIGHT * 0.3 * ind)
    r = RoundedRectangle(corner_radius=0.15, width=g.width + 2 * pad, height=g.height + 1.6 * pad, stroke_color=color, stroke_width=3)
    r.set_fill(tint(color, 0.1), opacity=1)
    g.move_to(r)
    return VGroup(r, g)


def pod(color=TEAL_M, r=0.3):
    return Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.28), opacity=1)


def dot(ok):
    c = GREEN_M if ok else RED_M
    return Circle(radius=0.13, stroke_color=c, stroke_width=2.5).set_fill(tint(c, 0.6 if ok else 0.45), opacity=1)


class D43Health(VoiceScene):
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
        self.title_card("Probes, resources and scaling", "is it healthy, how much does it get, how many copies")

        # 1. running is not healthy
        p = pod(TEAL_M, 0.6).move_to(LEFT * 0.6 + UP * 0.2)
        st = chip("Running", GREEN_M, 26).next_to(p, DOWN, buff=0.4)
        self.beat("Kubernetes already restarts a container whenever its process exits.",
                  GrowFromCenter(p), FadeIn(st), run_time=1.4)
        stuck = VGroup(T("stuck?", 28, RED_M), T("can't reach its database?", 28, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(p, RIGHT, buff=1.0)
        self.beat("But an app can stay up and still be useless. Stuck, or running but unable to reach its database.",
                  LaggedStart(*[FadeIn(s, shift=LEFT * 0.15) for s in stuck], lag_ratio=0.5), Succession(Wait(1.6), Indicate(st, color=GREEN_M)), run_time=2.8)
        kub = box("kubelet", GREY_B, w=2.0, h=0.7, size=26).move_to([-5.6, 0.2, 0])
        ga = Arrow(kub.get_right() + UP * 0.12, p.get_left() + UP * 0.12, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        gl = M("GET /healthz", 22, GREY_B).next_to(ga, UP, buff=0.1)
        ra = Arrow(p.get_left() + DOWN * 0.12, kub.get_right() + DOWN * 0.12, buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.1)
        rl = M("200", 22, GREEN_M).next_to(ra, DOWN, buff=0.1)
        pas = T("200 to 399 = pass", 26, GREEN_M).move_to([-2.0, -2.4, 0])
        self.steps("A probe is a small check that the kubelet runs on a timer. Here, an HTTP GET. Any status from 200 to 399 counts as a pass.",
                   (1.6, FadeOut(stuck), FadeIn(kub), GrowArrow(ga), FadeIn(gl)), (0.8, travel(ga, GREY_B, 0.8)),
                   (0.8, GrowArrow(ra), FadeIn(rl)), (0.8, FadeIn(pas)))
        self.play(FadeOut(VGroup(p, st, kub, ga, gl, ra, rl, pas)), run_time=0.6)

        # 2. three probes, three actions
        Y = (2.0, 0.0, -2.0)
        kb = box("kubelet", GREY_B, w=1.6, h=0.75, size=24).move_to([-5.85, 0, 0])
        names = (("startup", "GET /healthz", GOLD_M), ("liveness", "GET /healthz", RED_M), ("readiness", "GET /readyz", BLUE_M))
        pbs = VGroup()
        for (n, path, c), y in zip(names, Y):
            r = RoundedRectangle(corner_radius=0.12, width=2.4, height=1.0, stroke_color=c, stroke_width=3).move_to([-3.25, y, 0])
            r.set_fill(tint(c, 0.12), opacity=1)
            g = VGroup(T(n, 26), M(path, 20, GREY_B)).arrange(DOWN, buff=0.1).move_to(r)
            pbs.add(VGroup(r, g))
        ka = VGroup(*[edge_arrow(kb, b) for b in pbs])
        self.beat("There are three probes. Each asks a different question, and a failure leads to a different action.",
                  FadeIn(kb), LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(b)) for a, b in zip(ka, pbs)], lag_ratio=0.25), run_time=2.4)
        qs = VGroup(*[T(q, 22, GREY_B).move_to([0.6, y + 0.55, 0]) for q, y in zip(
            ('"Have you finished starting?"', '"Are you stuck?"', '"Can you take traffic right now?"'), Y)])
        DX = [-0.9 + 0.42 * i for i in range(8)]

        def row(results, y):
            return VGroup(*[dot(ok).move_to([x, y - 0.12, 0]) for ok, x in zip(results, DX)])

        def act(text, c, y):
            b = RoundedRectangle(corner_radius=0.12, width=3.4, height=0.8, stroke_color=c, stroke_width=3).move_to([4.85, y, 0])
            b.set_fill(tint(c, 0.14), opacity=1)
            return VGroup(b, T(text, 24).move_to(b))

        # startup
        rest = VGroup(pbs[1], pbs[2], ka[1], ka[2])
        wt = VGroup(*[T("waiting", 22, GREY_B).move_to([0.6, y - 0.12, 0]) for y in Y[1:]])
        self.beat("The startup probe asks: have you finished starting? Until it passes, the other two wait.",
                  FadeIn(qs[0]), rest.animate.set_opacity(0.3), FadeIn(wt), run_time=1.6)
        s_row = row([False] * 5 + [True], Y[0])
        s_lab = T("every 2 s, up to 30 x 2 s = 60 s", 20, GOLD_M).move_to([0.6, Y[0] - 0.62, 0])
        self.beat("In the lab, it allows thirty failures, two seconds apart. So the app gets up to sixty seconds to boot.",
                  LaggedStart(*[GrowFromCenter(d) for d in s_row[:5]], lag_ratio=0.3), FadeIn(s_lab), run_time=2.4)
        a0 = act("others wait", GOLD_M, Y[0])
        s_arr = Arrow(s_row[-1].get_right(), a0.get_left(), buff=0.15, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.12)
        self.beat("The moment the app answers, startup passes, and hands over to liveness and readiness.",
                  GrowFromCenter(s_row[5]), Succession(Wait(0.5), AnimationGroup(GrowArrow(s_arr), FadeIn(a0))),
                  Succession(Wait(1.2), AnimationGroup(rest.animate.set_opacity(1), FadeOut(wt))), run_time=2.6)

        # liveness
        l_row = row([True, True, False, False, False], Y[1])
        l_lab = T("every 10 s, acts after 3 misses", 20, RED_M).move_to([0.6, Y[1] - 0.62, 0])
        self.beat("The liveness probe asks: are you stuck? It checks /healthz every ten seconds.",
                  FadeIn(qs[1]), LaggedStart(*[GrowFromCenter(d) for d in l_row[:2]], lag_ratio=0.4), FadeIn(l_lab), run_time=2.0)
        a1 = act("restart container", RED_M, Y[1])
        l_arr = Arrow(l_row[-1].get_right(), a1.get_left(), buff=0.15, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.12)
        rs = M("RESTARTS: 1", 20, RED_M).next_to(a1, DOWN, buff=0.12)
        self.beat("After three failures in a row, the kubelet kills the container and starts a new one. In the lab, that takes about thirty seconds.",
                  LaggedStart(*[GrowFromCenter(d) for d in l_row[2:]], lag_ratio=0.5),
                  Succession(Wait(1.8), AnimationGroup(GrowArrow(l_arr), FadeIn(a1))), Succession(Wait(2.6), FadeIn(rs)), run_time=3.4)

        # readiness
        r_row = row([True, False, False], Y[2])
        r_lab = T("every 5 s, acts after 2 misses", 20, BLUE_M).move_to([0.6, Y[2] - 0.62, 0])
        self.beat("The readiness probe asks: can you take traffic right now? It checks /readyz every five seconds. And /readyz also pings Redis.",
                  FadeIn(qs[2]), GrowFromCenter(r_row[0]), FadeIn(r_lab), run_time=2.0)
        a2 = act("no Service traffic", BLUE_M, Y[2])
        r_arr = Arrow(r_row[-1].get_right(), a2.get_left(), buff=0.15, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        nr = T("keeps running", 20, GREEN_M).next_to(a2, DOWN, buff=0.12)
        self.beat("After two misses, the Pod gets no traffic from Services, within about ten seconds. Nothing restarts.",
                  LaggedStart(*[GrowFromCenter(d) for d in r_row[1:]], lag_ratio=0.5),
                  Succession(Wait(1.2), AnimationGroup(GrowArrow(r_arr), FadeIn(a2))), Succession(Wait(2.4), FadeIn(nr)), run_time=3.2)
        self.play(FadeOut(VGroup(kb, pbs, ka, qs, s_row, s_lab, a0, s_arr, l_row, l_lab, a1, l_arr, rs, r_row, r_lab, a2, r_arr, nr)), run_time=0.6)

        # 3. the liveness trap
        redis = mbox("redis", RED_M, size=26, w=2.0, h=0.75).move_to([0, 2.4, 0])
        redis[0].set_stroke(TEAL_M); redis[0].set_fill(tint(TEAL_M, 0.14))
        px = (-3.6, 0, 3.6)
        pods = VGroup(*[pod(TEAL_M, 0.42).move_to([x, -0.6, 0]) for x in px])
        plab = VGroup(*[M("hello-devops", 20, GREY_B).next_to(q, DOWN, buff=0.15) for q in pods])
        wires = VGroup(*[link(redis, q, GREY_B) for q in pods])
        bad = M("liveness: /healthz checks Redis", 24, RED_M).move_to([0, -2.3, 0])
        self.beat("Now the trap. Never make the liveness probe depend on something outside the container, such as Redis.",
                  FadeIn(redis), LaggedStart(*[GrowFromCenter(q) for q in pods], lag_ratio=0.2), FadeIn(plab), Create(wires), FadeIn(bad), run_time=2.4)
        xs = VGroup(*[tick(False, 0.25).move_to(q) for q in pods])
        casc = T("a small outage becomes a full one", 26, RED_M).move_to([0, -3.15, 0])
        self.steps("Picture Redis going down for a minute. Every Pod fails liveness at about the same time, and the kubelet restarts all of them. Restarts cannot fix Redis.",
                   (1.0, redis[0].animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.2)), wires.animate.set_color(RED_M)), (1.4, Wait(1.4)),
                   (1.4, *[q.animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.25)) for q in pods], LaggedStart(*[Create(x) for x in xs], lag_ratio=0.1)),
                   (2.0, Wait(2.0)), (0.8, FadeIn(casc, shift=UP * 0.15)))
        good = M("readiness: /readyz checks Redis", 24, BLUE_M).move_to(bad)
        self.beat("Dependency checks belong in readiness, because failing it only pauses traffic. Nothing restarts.",
                  FadeOut(xs), FadeOut(casc), Transform(bad, good),
                  *[q.animate.set_stroke(TEAL_M).set_fill(tint(TEAL_M, 0.1)).set_opacity(0.55) for q in pods], run_time=2.0)
        self.play(FadeOut(VGroup(redis, pods, plab, wires, bad)), run_time=0.6)

        # 4. requests and limits
        rc = card([("resources:", WHITE, 0), ("requests:", TEAL_M, 1), ("cpu: 100m", TEAL_M, 2), ("memory: 128Mi", TEAL_M, 2),
                   ("limits:", RED_M, 1), ("memory: 256Mi", RED_M, 2)], WHITE, size=22)
        rc.move_to([-4.6, 0.2, 0])
        self.steps("Each container can say how much CPU and memory it needs. 100m means 100 millicores, a tenth of one core. 128Mi means 128 mebibytes. There are two numbers, a request and a limit.",
                   (1.6, Create(rc[0]), FadeIn(rc[1][0]), FadeIn(rc[1][1])), (1.6, Wait(1.6)), (0.8, FadeIn(rc[1][2])), (1.6, Wait(1.6)),
                   (0.8, FadeIn(rc[1][3])), (1.0, Wait(1.0)), (0.8, FadeIn(rc[1][4]), FadeIn(rc[1][5])))

        BX, BW, BH = 2.3, 6.4, 0.8
        bins, fills = VGroup(), VGroup()
        for name, y, used in (("devops-worker", 1.4, [1.6, 2.2, 1.6]), ("devops-worker2", -0.9, [1.4, 1.6])):
            r = Rectangle(width=BW, height=BH, stroke_color=GREY_B, stroke_width=2.5).move_to([BX, y, 0])
            lab = M(name, 20, GREY_B).next_to(r, UP, buff=0.12).align_to(r, LEFT)
            x0 = r.get_left()[0]
            f = VGroup()
            for w in used:
                b = Rectangle(width=w - 0.06, height=BH - 0.16, stroke_color=TEAL_M, stroke_width=1.5).set_fill(tint(TEAL_M, 0.3), opacity=1)
                b.move_to([x0 + w / 2, y, 0]); x0 += w
                f.add(b)
            bins.add(VGroup(r, lab)); fills.add(f)
        rh = T("reserved by requests", 22, TEAL_M).move_to([BX, -2.15, 0])
        self.beat("A request is what the scheduler reserves. It puts a Pod only on a node whose unreserved room fits the request.",
                  FadeIn(bins), LaggedStart(*[FadeIn(b) for f in fills for b in f], lag_ratio=0.1), FadeIn(rh), Indicate(rc[1][1], color=TEAL_M), run_time=2.6)
        newp = Rectangle(width=1.5 - 0.06, height=BH - 0.16, stroke_color=YELLOW_M, stroke_width=2).set_fill(tint(YELLOW_M, 0.35), opacity=1)
        newp.move_to([-1.6, 3.15, 0])
        npl = T("new Pod", 20, YELLOW_M).next_to(newp, LEFT, buff=0.15)
        tgt = [bins[1][0].get_left()[0] + 3.0 + 0.75, -0.9, 0]
        self.steps("This new Pod does not fit on the first node. It does fit on the second.",
                   (0.8, FadeIn(newp), FadeIn(npl)), (1.0, newp.animate.move_to([BX + 2.25, 1.4, 0]), FadeOut(npl)),
                   (0.5, Wiggle(newp)), (1.0, newp.animate.move_to(tgt)))
        big = Rectangle(width=3.0 - 0.06, height=BH - 0.16, stroke_color=RED_M, stroke_width=2).set_fill(tint(RED_M, 0.3), opacity=1).move_to([-0.1, 3.15, 0])
        pend = chip("Pending", RED_M, 24).next_to(big, RIGHT, buff=0.3)
        self.beat("If no node has room for the request, the Pod stays Pending. The scheduler counts requests, not live use.",
                  FadeIn(big, shift=DOWN * 0.15), Succession(Wait(0.8), FadeIn(pend)), Succession(Wait(2.6), Indicate(rh, color=TEAL_M)), run_time=3.6)
        self.play(FadeOut(VGroup(bins, fills, rh, newp, big, pend)), run_time=0.6)

        lim = T("limit: the most it may use, enforced by the kernel (cgroups)", 24, RED_M).move_to([1.4, 2.6, 0])
        self.beat("A limit is the most the container may use. The Linux kernel enforces it while the container runs, with cgroups.",
                  FadeIn(lim, shift=DOWN * 0.15), Indicate(rc[1][4], color=RED_M), run_time=2.0)
        self.beat("At the limit, the two resources behave very differently. Too much CPU makes you slow. Too much memory gets you killed.",
                  rc.animate.set_opacity(0.0), run_time=1.6)
        self.remove(rc)

        # CPU: throttled
        cpu_h = T("CPU at its limit", 28, BLUE_M).move_to([-3.6, 1.7, 0])
        ex = M("limit cpu: 200m", 22, GREY_B).next_to(cpu_h, DOWN, buff=0.3)
        WIN = 1.8
        wins = VGroup()
        for i in range(3):
            x0 = -6.3 + i * WIN
            frame = Rectangle(width=WIN, height=0.6, stroke_color=GREY_B, stroke_width=2).move_to([x0 + WIN / 2, -0.2, 0])
            run = Rectangle(width=WIN * 0.2, height=0.6, stroke_width=0).set_fill(BLUE_M, opacity=0.85).move_to([x0 + WIN * 0.1, -0.2, 0])
            wins.add(VGroup(frame, run))
        wl = VGroup(T("20 ms run", 20, BLUE_M), T("80 ms wait", 20, GREY_B)).arrange(RIGHT, buff=0.4).next_to(wins[0], DOWN, buff=0.25).align_to(wins[0], LEFT)
        wlab = T("every 100 ms", 20, GREY_B).next_to(wins, UP, buff=0.15)
        thr = chip("throttled: still running, only slower", BLUE_M, 22).move_to([-3.6, -2.0, 0])
        div = DashedLine([0, 2.2, 0], [0, -3.3, 0], dash_length=0.1, stroke_width=1.5, color=GREY_D)
        self.beat("The kernel enforces a CPU limit as a time budget. With 200m, the container gets 20 milliseconds of CPU in every 100, then waits.",
                  FadeIn(cpu_h), FadeIn(div), FadeIn(ex),
                  LaggedStart(*[AnimationGroup(Create(w[0]), GrowFromEdge(w[1], LEFT)) for w in wins], lag_ratio=0.4), FadeIn(wlab), FadeIn(wl), run_time=2.6)
        self.beat("It waits even when other cores sit idle. That is throttling. It keeps running, only slower.",
                  FadeIn(thr, shift=UP * 0.15), run_time=1.6)

        # memory: OOMKilled
        mem_h = T("memory over its limit", 28, RED_M).move_to([3.6, 1.7, 0])
        G0, GH = -2.9, 3.6
        gauge = Rectangle(width=1.0, height=GH, stroke_color=GREY_B, stroke_width=2.5).move_to([2.4, G0 + GH / 2, 0])
        yreq, ylim = G0 + GH * 128 / 300, G0 + GH * 256 / 300
        lreq = DashedLine([1.75, yreq, 0], [3.05, yreq, 0], dash_length=0.08, stroke_width=2.5, color=TEAL_M)
        llim = Line([1.75, ylim, 0], [3.05, ylim, 0], stroke_width=3.5, color=RED_M)
        treq = M("request 128Mi", 20, TEAL_M).next_to(lreq, RIGHT, buff=0.2)
        tlim = M("limit 256Mi", 20, RED_M).next_to(llim, RIGHT, buff=0.2)
        fill = Rectangle(width=0.9, height=0.01, stroke_width=0).set_fill(GOLD_M, opacity=0.8).move_to([2.4, G0, 0], aligned_edge=DOWN)
        self.add(fill)
        f2 = Rectangle(width=0.9, height=GH * 200 / 300, stroke_width=0).set_fill(GOLD_M, opacity=0.8).move_to([2.4, G0, 0], aligned_edge=DOWN)
        self.steps("Memory cannot be taken back once a process holds it. Between request and limit, a container may use whatever the node has spare.",
                   (1.6, FadeIn(mem_h), Create(gauge), Create(lreq), Create(llim), FadeIn(treq), FadeIn(tlim)), (1.2, Wait(1.2)), (1.8, Transform(fill, f2)))
        f3 = Rectangle(width=0.9, height=GH * 275 / 300, stroke_width=0).set_fill(RED_M, opacity=0.85).move_to([2.4, G0, 0], aligned_edge=DOWN)
        oom = VGroup(M("OOMKilled", 26, RED_M), M("Exit Code: 137", 24, RED_M), T("137 = 128 + 9, SIGKILL", 20, GREY_B)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        oom.move_to([5.2, -2.75, 0])
        self.steps("Over the memory limit, the kernel's out of memory killer stops it. Kubernetes shows OOMKilled, exit code 137: signal 9, SIGKILL.",
                   (1.6, Transform(fill, f3)), (0.6, Flash(llim.get_center(), color=RED_M, line_length=0.3, flash_radius=0.7)),
                   (1.8, LaggedStart(*[FadeIn(o, shift=LEFT * 0.15) for o in oom], lag_ratio=0.4)))
        self.play(FadeOut(VGroup(cpu_h, ex, wins, wl, wlab, thr, div, mem_h, gauge, lreq, llim, treq, tlim, fill, oom, lim)), run_time=0.6)

        # the lab's choice
        rc.set_opacity(1).move_to([-3.2, 0.2, 0])
        nolim = VGroup(T("no CPU limit, on purpose", 28, YELLOW_M), T("rely on the CPU request", 24, GREY_B)).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([2.6, 0.2, 0])
        self.beat("The lab sets no CPU limit, on purpose. For a web app like this one, rely on the request. But always set requests.",
                  FadeIn(rc),
                  FadeIn(nolim[0], shift=LEFT * 0.15), Succession(Wait(1.6), FadeIn(nolim[1])), run_time=2.6)
        self.play(FadeOut(VGroup(rc, nolim)), run_time=0.6)

        # 5. the HorizontalPodAutoscaler
        PX = [-3.75 + 1.5 * i for i in range(6)]
        BASE, U = -1.9, 0.02  # bar base y, units per millicore

        def bar(x, m, c=GOLD_M):
            return Rectangle(width=0.6, height=max(0.01, m * U), stroke_width=0).set_fill(c, opacity=0.8).move_to([x, BASE, 0], aligned_edge=DOWN)

        def reqbox(x):
            return Rectangle(width=0.7, height=100 * U, stroke_color=TEAL_M, stroke_width=2).move_to([x, BASE, 0], aligned_edge=DOWN)

        tline = DashedLine([-4.4, BASE + 70 * U, 0], [4.4, BASE + 70 * U, 0], dash_length=0.1, stroke_width=2.5, color=YELLOW_M)
        tlab = T("target 70m", 20, YELLOW_M).next_to(tline, LEFT, buff=0.15)
        hp = VGroup(*[pod(TEAL_M, 0.24).move_to([x, BASE - 0.45, 0]) for x in PX])
        rq = VGroup(*[reqbox(x) for x in PX])
        bars = VGroup(*[bar(x, 50) for x in PX[:3]])
        loop = VGroup(T("HorizontalPodAutoscaler", 28, WHITE), T("every 15 s", 24, GREY_B)).arrange(RIGHT, buff=0.4).move_to([0, 3.2, 0])
        self.beat("A HorizontalPodAutoscaler changes the number of replicas of a Deployment for you. It is one more control loop, and it runs every fifteen seconds.",
                  FadeIn(loop), LaggedStart(*[GrowFromCenter(q) for q in hp[:3]], lag_ratio=0.2), run_time=2.4)
        self.beat("It reads each Pod's CPU use, as a percentage of the Pod's CPU request.",
                  LaggedStart(*[Create(r) for r in rq[:3]], lag_ratio=0.2), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), run_time=2.4)
        rql = T("request 100m", 20, TEAL_M).next_to(rq[0], LEFT, buff=0.15)
        self.beat("The lab targets 70 percent of the 100m request. That is 70m per Pod.",
                  FadeIn(rql), Create(tline), FadeIn(tlab), run_time=1.8)
        hot = VGroup(*[bar(x, 140) for x in PX[:3]])
        vals = VGroup(*[M("140m", 20, GOLD_M).next_to(b, UP, buff=0.1) for b in hot])
        self.beat("Say three Pods average 140m under load. That is twice the target.",
                  *[Transform(b, h) for b, h in zip(bars, hot)], FadeIn(vals), run_time=1.8)
        fml = M("desired = ceil(3 x 140 / 70) = 6", 28, YELLOW_M).move_to([0, 2.3, 0])
        self.beat("So it works out how many replicas would bring the average back to the target. Ceil of three times 140, over 70. Six.",
                  Write(fml), run_time=2.6)
        mm = VGroup(chip("minReplicas: 3", TEAL_M, 22, mono=True), chip("maxReplicas: 6", TEAL_M, 22, mono=True)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        mm.move_to([5.3, 1.5, 0])
        cool = VGroup(*[bar(x, 70) for x in PX])
        self.steps("Then it sets the Deployment's replica count, between minReplicas, three, and maxReplicas, six.",
                   (0.8, FadeIn(mm, shift=LEFT * 0.15)),
                   (1.6, LaggedStart(*[AnimationGroup(GrowFromCenter(hp[i]), Create(rq[i])) for i in range(3, 6)], lag_ratio=0.25)),
                   (1.2, *[Transform(b, c) for b, c in zip(bars, cool[:3])], *[GrowFromEdge(c, DOWN) for c in cool[3:]], FadeOut(vals)))
        bars.add(*cool[3:])
        down = chip("scale down: waits 5 min by default, 2 min in the lab", GREY_B, 22).move_to([0, -3.3, 0])
        self.beat("It scales up at once, but down slowly, on purpose. By default it wants five minutes of lower numbers before it removes Pods. The lab shortens that to two.",
                  FadeIn(down, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(down), run_time=0.4)
        need = VGroup(chip("needs metrics-server", BLUE_M, 22), chip("needs a CPU request", RED_M, 22)).arrange(RIGHT, buff=0.5).move_to([0, -3.3, 0])
        self.beat("It needs metrics-server for the numbers. And without a CPU request, it has no percentage to compute, so it does nothing.",
                  FadeIn(need[0], shift=UP * 0.15), Succession(Wait(2.0), AnimationGroup(FadeIn(need[1], shift=UP * 0.15), rq.animate.set_stroke(RED_M))), run_time=3.2)
        self.play(FadeOut(VGroup(loop, hp, rq, bars, rql, tline, tlab, fml, mm, need)), run_time=0.6)

        # 6. recap
        rcp = VGroup(T("probes: wait, restart, or stop traffic", 30, GOLD_M),
                     T("requests: where a Pod fits", 30, TEAL_M),
                     T("limits: CPU throttled, memory OOMKilled", 30, RED_M),
                     T("HPA: more Pods from the average CPU", 30, YELLOW_M)).arrange(DOWN, buff=0.4)
        self.beat("Probes decide when to wait, restart, or stop traffic. Requests decide where a Pod fits. At the limit, CPU is throttled and memory is killed. And the HPA adds Pods from the average CPU.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.5), run_time=5.0)
        self.wait(1.0)
