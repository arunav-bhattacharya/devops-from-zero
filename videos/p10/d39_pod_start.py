import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\brestartPolicy\b", "restart policy"), (r"\bPodInitializing\b", "pod initializing"),
            (r"\bindex\.html\b", "index dot H T M L"), (r"\baccess\.log\b", "access dot log")])

PX = (-4.1, 0.0, 4.1)   # write-page, log-tailer, nginx
CY = 1.2                # container row
CW, CH = 3.3, 1.2


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def cbox(name, role, color, x):
    r = RoundedRectangle(corner_radius=0.12, width=CW, height=CH, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    n = M(name, 26).move_to([x, CY + 0.2, 0])
    ro = T(role, 22, GREY_B).move_to([x, CY - 0.27, 0])
    r.move_to([x, CY, 0])
    g = VGroup(r, n, ro)
    g.color_ = color
    return g


def vol(name, color, pos):
    t = M(name, 22, color)
    r = RoundedRectangle(corner_radius=0.1, width=t.width + 0.6, height=0.56, stroke_color=color, stroke_width=2.5)
    r.set_fill(tint(color, 0.12), 1)
    return VGroup(r, t).move_to(pos)


def waiting(c):
    return [c[0].animate.set_stroke(GREY_D, 2.5).set_fill(BLACK, 1), c[1].animate.set_opacity(0.35), c[2].animate.set_opacity(0.35)]


def running(c):
    return [c[0].animate.set_stroke(c.color_, 5).set_fill(tint(c.color_, 0.22), 1), c[1].animate.set_opacity(1), c[2].animate.set_opacity(1)]


class D39PodStart(VoiceScene):
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
        self.title_card("Inside a Pod: who starts first", "init containers, a sidecar, and one shared IP")

        # ---------- 1. the problem: a helper that must sit next to the app
        ngx = cbox("nginx", "app container", TEAL_M, PX[2])
        tail = cbox("log-tailer", "helper", GOLD_M, PX[1])
        self.beat("Say nginx serves your web page, and writes every request to a log file.",
                  FadeIn(ngx, shift=0.2 * UP), run_time=1.4)
        self.beat("You want a helper that reads each new line of that log. It only works right next to the app, because it must read the app's files.",
                  FadeIn(tail, shift=0.2 * UP), run_time=1.6)

        pod = RoundedRectangle(corner_radius=0.25, width=12.8, height=4.75, stroke_color=BLUE_M, stroke_width=3).move_to([0, 1.05, 0])
        plab = T("Pod: web", 28, BLUE_M).move_to([-5.15, 3.0, 0])
        self.beat("Kubernetes has a wrapper for this, the Pod. One or more containers, placed on one node together.",
                  Create(pod), FadeIn(plab), run_time=1.8)
        ip = chip("one IP, localhost", BLUE_M, 22).move_to([4.6, 3.0, 0])
        self.beat("They share one IP address and one set of ports. So they reach each other on localhost.",
                  FadeIn(ip, shift=0.15 * DOWN), run_time=1.2)
        logs = vol("volume: logs", GREEN_M, [2.05, -0.5, 0])
        l1, l2 = link(ngx, logs, GREEN_M, sw=2.5), link(tail, logs, GREEN_M, sw=2.5)
        self.steps("They can also share volumes. Here, a folder called logs. nginx writes into it, and the helper reads from it.",
                   (1.4, FadeIn(logs), Create(l1), Create(l2)), (1.4, Wait(1.4)),
                   (1.0, travel(Line(ngx.get_bottom(), logs.get_right()), YELLOW_M, 1.0)),
                   (1.0, travel(Line(logs.get_left(), tail.get_bottom()), YELLOW_M, 1.0)))
        self.beat("And they share one life. They start on the same node, and they are removed together.",
                  Succession(pod.animate(run_time=0.6).set_stroke(width=7), pod.animate(run_time=0.6).set_stroke(width=3)), run_time=1.2)

        wp = cbox("write-page", "init container", PURPLE_M, PX[0])
        work = vol("volume: work", BLUE_M, [0, 2.75, 0])
        w1, w2 = link(work, wp, BLUE_M, sw=2.5), link(work, ngx, BLUE_M, sw=2.5)
        self.beat("nginx also needs a page to serve. In the lab's example Pod, a third container writes that page into a second folder, called work.",
                  FadeIn(wp, shift=0.2 * UP), FadeIn(work), Create(w1), Create(w2), run_time=2.4)
        role2 = T("init container", 22, GREY_B).move_to(tail[2])
        self.steps("The manifest lists two init containers, write-page and log-tailer, and one app container, nginx. So who starts first?",
                   (1.0, Transform(tail[2], role2), Indicate(wp[2], color=PURPLE_M)), (0.8, Indicate(tail[2], color=GOLD_M)),
                   (0.8, Indicate(ngx[2], color=TEAL_M)))

        # ---------- 2. the start, as kubectl get -w shows it
        cmd = M("$ kubectl get pod web -w", 22, GREY_B).move_to([-3.6, -1.85, 0], aligned_edge=LEFT).align_to(np.array([-5.2, 0, 0]), LEFT)
        COLS = (-5.2, -2.9, -0.9, 2.6)
        hdr = VGroup(*[M(h, 20, GREY_B).move_to([x, -2.4, 0], aligned_edge=LEFT) for h, x in zip(("NAME", "READY", "STATUS", "AGE"), COLS)])

        def row(ready, status, age, c=WHITE):
            return VGroup(*[M(v, 24, cc).move_to([x, -2.95, 0], aligned_edge=LEFT)
                            for v, x, cc in zip(("web", ready, status, age), COLS, (WHITE, c, c, GREY_B))])
        for m in hdr:
            m.align_to(np.array([0, -2.4, 0]), UP)
        r = row("0/2", "Init:0/2", "1s", PURPLE_M)
        self.beat("Watch it start, with kubectl get and the watch flag. At first, nothing in the Pod is running.",
                  *waiting(wp), *waiting(tail), *waiting(ngx), FadeIn(cmd), FadeIn(hdr), FadeIn(r), run_time=1.8)
        self.beat("Init containers run first, one at a time, in order. Each must exit with code 0 before the next one starts.",
                  *running(wp), run_time=1.2)
        page = chip("index.html", PURPLE_M, 20, mono=True).move_to(wp).shift(UP * 0.1)
        done = VGroup(tick(True, 0.16), T("exited 0", 22, GREEN_M)).arrange(RIGHT, buff=0.15).move_to(wp[2])
        self.steps("The first one writes index.html into the work volume, then exits with code 0. STATUS moves to Init, one of two.",
                   (0.4, FadeIn(page)), (1.4, page.animate.move_to(work).shift(DOWN * 0.0).set_opacity(0)),
                   (0.6, Indicate(work[1], color=BLUE_M)), (1.2, Wait(1.2)),
                   (1.0, wp[0].animate.set_stroke(GREY_B, 2.5).set_fill(BLACK, 1), wp[1].animate.set_color(GREY_B), Transform(wp[2], done),
                    Transform(r, row("0/2", "Init:1/2", "4s", PURPLE_M))))
        q = T("it never exits, so does nginx wait forever?", 24, RED_M).move_to([0, -3.5, 0])
        self.beat("So Kubernetes counts log-tailer as an init container too. But a log tailer never exits. Does nginx wait forever?",
                  Indicate(tail[1], color=GOLD_M), Succession(Wait(2.2), FadeIn(q, shift=0.15 * UP)), run_time=3.4)
        rp = M("restartPolicy: Always", 20, GOLD_M).move_to(tail[2])
        sl = T("sidecar", 24, GOLD_M).move_to([0, 2.08, 0])
        self.beat("No. Look at its one extra line in the manifest: restartPolicy Always. That one line makes it a sidecar.",
                  FadeOut(q), Transform(tail[2], rp), Succession(Wait(2.6), FadeIn(sl, shift=0.1 * DOWN)),
                  run_time=3.4)
        self.beat("Kubernetes starts a sidecar in init order, then moves on as soon as it is running. It does not wait for it to exit.",
                  *running(tail), Transform(r, row("1/2", "PodInitializing", "5s", GOLD_M)), run_time=1.6)
        self.beat("Then nginx starts. READY becomes two of two, because READY counts the sidecar too.",
                  *running(ngx), Transform(r, row("2/2", "Running", "11s", GREEN_M)), run_time=1.6)

        # ---------- 3. what sharing buys you
        cons = VGroup(M("$ kubectl exec web -c nginx -- curl -s localhost", 22, GREY_B),
                      M("hello from the init container", 24, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        cons.move_to([-5.2, -2.6, 0], aligned_edge=LEFT)
        self.beat("Now ask nginx for its page, from inside the Pod, on localhost.",
                  FadeOut(VGroup(cmd, hdr, r)), FadeIn(cons[0]), run_time=1.4)
        self.steps("The answer is the file the init container wrote, before nginx even existed. It stayed behind in the shared volume.",
                   (1.2, travel(Line(work.get_right(), ngx.get_top()), PURPLE_M, 1.2)), (0.8, FadeIn(cons[1], shift=0.1 * UP)),
                   (1.4, Indicate(wp[1], color=PURPLE_M)), (1.0, Indicate(work[1], color=BLUE_M)))
        logl = VGroup(M("$ kubectl logs web -c log-tailer", 22, GREY_B), M('"GET / HTTP/1.1" 200', 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        logl.move_to(cons, aligned_edge=LEFT)
        self.steps("nginx also wrote that request into access.log, in the logs volume. The sidecar read the new line and printed it.",
                   (1.0, FadeOut(cons)), (1.0, travel(Line(ngx.get_bottom(), logs.get_right()), YELLOW_M, 1.0)),
                   (1.0, travel(Line(logs.get_left(), tail.get_bottom()), YELLOW_M, 1.0)), (1.0, FadeIn(logl, shift=0.1 * UP)))

        # ---------- 4. why the order matters: a timeline of log lines
        self.play(FadeOut(logl), run_time=0.5)
        AY, HY = -2.45, -3.15
        app_bar = Rectangle(width=6.6, height=0.3, stroke_width=0).set_fill(TEAL_M, 0.75).move_to([0.3, AY, 0])
        app_l = M("nginx", 22, TEAL_M).move_to([-4.6, AY, 0])
        lines = VGroup(*[Dot(radius=0.08, color=YELLOW_M).move_to([-2.7 + 0.75 * i, AY + 0.33, 0]) for i in range(9)])
        self.beat("Why this order? Think of the old way, where the helper was just a second normal container. Each dot is one log line from nginx.",
                  FadeIn(app_l), GrowFromEdge(app_bar, LEFT), LaggedStart(*[GrowFromCenter(d) for d in lines], lag_ratio=0.15), run_time=2.6)
        old = Rectangle(width=4.0, height=0.3, stroke_width=0).set_fill(GREY_B, 0.6).move_to([0.3, HY, 0])
        old_l = T("old helper", 22, GREY_B).move_to([-4.6, HY, 0])
        miss = T("missed", 22, RED_M).next_to(lines[1], UP, buff=0.12).shift(LEFT * 0.35)
        self.beat("A log shipper that started late missed the first lines.",
                  FadeIn(old_l), GrowFromEdge(old, LEFT), *[lines[i].animate.set_color(RED_M) for i in (0, 1)],
                  Succession(Wait(0.8), FadeIn(miss)), run_time=2.0)
        lost = T("lost", 22, RED_M).next_to(lines[8], UP, buff=0.12).shift(LEFT * 0.3)
        self.beat("And one that stopped early lost the last ones.",
                  *[lines[i].animate.set_color(RED_M) for i in (7, 8)], Succession(Wait(0.6), FadeIn(lost)), run_time=1.6)
        side = Rectangle(width=8.4, height=0.3, stroke_width=0).set_fill(GOLD_M, 0.75).move_to([0.3, HY, 0])
        side_l = M("sidecar", 22, GOLD_M).move_to(old_l)
        self.beat("A native sidecar starts before the app, and stops only after the app has stopped. So it reads every line.",
                  Transform(old, side), FadeOut(old_l), FadeIn(side_l), FadeOut(miss), FadeOut(lost),
                  Succession(Wait(1.6), AnimationGroup(*[d.animate.set_color(GREEN_M) for d in lines])), run_time=3.0)
        self.steps("And if it crashes in between, Kubernetes restarts it.",
                   (0.6, tail[0].animate.set_stroke(RED_M, 5).set_fill(tint(RED_M, 0.22), 1)), (0.6, Wait(0.6)),
                   (0.8, *running(tail)))
        cur = Line([3.4, -2.05, 0], [3.4, -3.45, 0], stroke_width=3, color=WHITE)
        self.steps("At shutdown, the order runs backwards. nginx stops first. The sidecar stops last.",
                   (0.5, FadeIn(cur)), (0.9, cur.animate.move_to([3.75, -2.75, 0])), (0.8, *waiting(ngx)),
                   (0.9, cur.animate.move_to([4.65, -2.75, 0])), (0.8, *waiting(tail)))

        # ---------- 5. what belongs in one Pod
        self.play(FadeOut(VGroup(app_bar, app_l, lines, old, side_l, cur)), run_time=0.6)
        rule = T("one Pod only if they must share a node, an IP, or files", 26, WHITE).move_to([0, -2.2, 0])
        db = T("app and database: separate Pods", 26, GREY_B).move_to([0, -2.95, 0])
        self.steps("So when does a helper belong in the same Pod? Only when the containers must share a node, an IP address, or files. An app and its database belong in separate Pods, so you can scale and replace each one on its own.",
                   (1.0, FadeIn(rule, shift=0.1 * UP)), (1.0, Indicate(ip, color=BLUE_M)), (1.0, Indicate(logs[1], color=GREEN_M)),
                   (4.0, Wait(4.0)), (0.8, FadeIn(db, shift=0.1 * UP)))

        # ---------- 6. recap
        self.play(FadeOut(VGroup(rule, db)), wp[0].animate.set_stroke(PURPLE_M, 5).set_fill(tint(PURPLE_M, 0.22), 1), *running(tail), *running(ngx), run_time=0.8)
        nums = VGroup()
        for i, (c, x) in enumerate(zip((PURPLE_M, GOLD_M, TEAL_M), PX)):
            n = Circle(radius=0.24, stroke_color=c, stroke_width=3).set_fill(BLACK, 1)
            nums.add(VGroup(n, T(str(i + 1), 24, c).move_to(n)).move_to([x - CW / 2 + 0.05, CY + CH / 2 - 0.05, 0]))
        cap = VGroup(T("init first, then the sidecar, then the app", 28, WHITE),
                     T("all share the Pod's IP and volumes", 26, GREY_B)).arrange(DOWN, buff=0.3).move_to([0, -2.6, 0])
        self.beat("Init containers finish first. The sidecar starts next and keeps running. Then the app starts. And all of them share the Pod's IP and volumes.",
                  LaggedStart(*[GrowFromCenter(n) for n in nums], lag_ratio=0.5), Succession(Wait(1.5), FadeIn(cap[0])),
                  Succession(Wait(4.0), FadeIn(cap[1])), run_time=5.0)
        self.wait(1.5)
