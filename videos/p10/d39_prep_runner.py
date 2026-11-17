import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Day 39, fifth pass (Venkat style). Restaurant manager world.
# Concept: what a Pod is (a tray), and who starts first inside one: init containers (prep cooks),
# a native sidecar (the runner) and the app. Facts and outputs from the lesson's worked example.
# Colours: Pod = BLUE, write-page (init) = PURPLE, log-tailer (sidecar) = GOLD, nginx (app) = TEAL,
# volumes = GREEN, prompts = YELLOW, failure = RED.

SAY.extend([(r"\brestartPolicy\b", "restart policy"), (r"\bPodInitializing\b", "pod initializing"),
            (r"\binitContainers\b", "init containers"), (r"\bindex\.html\b", "index dot H T M L"),
            (r"\baccess\.log\b", "access dot log"), (r"\bInit:0/2\b", "init, zero of two"), (r"\bInit:1/2\b", "init, one of two")])

PX = (-4.15, 0.0, 4.15)
CY = 1.2
CW, CH = 3.3, 1.2


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def cbox(name, role, color, x):
    r = RoundedRectangle(corner_radius=0.12, width=CW, height=CH, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    r.move_to([x, CY, 0])
    n = M(name, 26).move_to([x, CY + 0.22, 0])
    ro = T(role, 24, GREY_B).move_to([x, CY - 0.27, 0])
    g = VGroup(r, n, ro)
    g.color_ = color
    return g


def vol(name, pos):
    t = M(name, 22, GREEN_M)
    r = RoundedRectangle(corner_radius=0.1, width=t.width + 0.6, height=0.58, stroke_color=GREEN_M, stroke_width=2.5).set_fill(tint(GREEN_M, 0.12), 1)
    return VGroup(r, t).move_to(pos)


def waiting(c):
    return [c[0].animate.set_stroke(GREY_D, 2.5).set_fill(BLACK, 1), c[1].animate.set_opacity(0.35), c[2].animate.set_opacity(0.35)]


def running(c):
    return [c[0].animate.set_stroke(c.color_, 5).set_fill(tint(c.color_, 0.24), 1), c[1].animate.set_opacity(1), c[2].animate.set_opacity(1)]


def person(color, s=1.0):
    head = Circle(radius=0.17, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    body = RoundedRectangle(corner_radius=0.16, width=0.56, height=0.42, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    body.next_to(head, DOWN, buff=0.05)
    return VGroup(head, body).scale(s)


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


class D39PrepRunner(Base):
    def construct(self):
        self.title_card("Who starts first inside a Pod?", "prep cooks, a runner, and then the dish")

        # ---------- 1. QUESTION + FAMILIAR: the tray
        q = T("more than one container: who goes first?", 32, YELLOW_M).move_to([0, 2.6, 0])
        self.beat("A Pod can hold more than one container. So when it starts, who goes first? And what happens if one of them never finishes?",
                  FadeIn(q, shift=DOWN * 0.1), run_time=1.6)
        tray = RoundedRectangle(corner_radius=0.5, width=5.2, height=2.4, stroke_color=BLUE_M, stroke_width=4).set_fill(tint(BLUE_M, 0.08), 1).move_to([0, -0.2, 0])
        main = Circle(radius=0.75, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.3), 1).move_to([-0.9, -0.2, 0])
        side = Circle(radius=0.45, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.3), 1).move_to([1.3, -0.2, 0])
        ml = T("main dish", 26, TEAL_M).next_to(main, DOWN, buff=0.15)
        sl = T("side", 26, GOLD_M).next_to(side, DOWN, buff=0.15)
        self.beat("Before we answer, picture a waiter with a tray. The tray may hold a main dish and a side, but they always travel together, and land on the same table.",
                  FadeOut(q), Create(tray), GrowFromCenter(main), GrowFromCenter(side), FadeIn(ml), FadeIn(sl), run_time=2.4)
        tl = T("a Pod", 30, BLUE_M).next_to(tray, UP, buff=0.25)
        self.beat("A Pod is that tray. One or more containers, which Kubernetes places together on one node.",
                  FadeIn(tl, shift=DOWN * 0.1), run_time=1.4)
        shares = VGroup(chip("one IP address, so localhost works", BLUE_M, 26), chip("shared folders, called volumes", GREEN_M, 26), chip("one life: start and go together", GREY_B, 26))
        shares.arrange(DOWN, buff=0.2).move_to([0, -2.65, 0])
        self.play(VGroup(tray, main, side, ml, sl, tl).animate.shift(UP * 1.2), run_time=0.6)
        self.steps("They share three things. One IP address, so they reach each other on localhost. Folders called volumes, that they can all read and write. And one life: they start on the same node, and they are removed together.",
                   (0.7, FadeIn(shares[0], shift=UP * 0.1)), (1.8, Wait(1.8)), (0.7, FadeIn(shares[1], shift=UP * 0.1)),
                   (1.6, Wait(1.6)), (0.7, FadeIn(shares[2], shift=UP * 0.1)))
        self.beat("Most Pods hold just one container. But the tray matters for helpers that only work right next to the app, because they need its files.",
                  Indicate(side, color=GOLD_M), run_time=1.4)
        self.play(FadeOut(VGroup(tray, main, side, ml, sl, tl, shares)), run_time=0.7)

        # ---------- 2. SHRINK: the lab's example Pod
        pod = RoundedRectangle(corner_radius=0.25, width=12.8, height=4.6, stroke_color=BLUE_M, stroke_width=3).move_to([0, 1.1, 0])
        plab = T("Pod: web", 28, BLUE_M).move_to([-5.0, 2.95, 0])
        ngx = cbox("nginx", "the app", TEAL_M, PX[2])
        self.beat("Here is the example Pod from the lab. Its app is nginx, a web server. It serves one web page, and writes every visit into a log file.",
                  Create(pod), FadeIn(plab), FadeIn(ngx, shift=UP * 0.15), run_time=2.0)
        wp = cbox("write-page", "writes the page", PURPLE_M, PX[0])
        tail = cbox("log-tailer", "reads the log", GOLD_M, PX[1])
        work = vol("volume: work", [-0.2, 2.95, 0])
        logs = vol("volume: logs", [2.05, -0.55, 0])
        w1, w2 = link(work, wp, GREEN_M, sw=2.5), link(work, ngx, GREEN_M, sw=2.5)
        l1, l2 = link(ngx, logs, GREEN_M, sw=2.5), link(tail, logs, GREEN_M, sw=2.5)
        self.steps("It needs two helpers. One writes the page into a shared folder called work, before nginx starts. The other reads each new line of the log, from a folder called logs.",
                   (1.2, FadeIn(wp, shift=UP * 0.15), FadeIn(work), Create(w1), Create(w2)), (1.6, Wait(1.6)),
                   (1.2, FadeIn(tail, shift=UP * 0.15), FadeIn(logs), Create(l1), Create(l2)))

        # ---------- 3. PAIN: the old way, the helper as a plain second container
        AY, HY = -2.35, -3.05
        app_bar = Rectangle(width=6.4, height=0.3, stroke_width=0).set_fill(TEAL_M, 0.75).move_to([0.6, AY, 0])
        app_l = M("nginx", 22, TEAL_M).move_to([-4.6, AY, 0])
        dots = VGroup(*[Dot(radius=0.08, color=YELLOW_M).move_to([-2.3 + 0.72 * i, AY + 0.33, 0]) for i in range(9)])
        self.beat("Now the trouble with the old way, where a helper was just a second, ordinary container. Each dot is one log line from nginx.",
                  FadeIn(app_l), GrowFromEdge(app_bar, LEFT), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.12), run_time=2.6)
        old = Rectangle(width=3.8, height=0.3, stroke_width=0).set_fill(GREY_B, 0.6).move_to([0.6, HY, 0])
        old_l = T("old helper", 24, GREY_B).move_to([-4.6, HY, 0])
        miss = T("missed", 24, RED_M).next_to(dots[1], UP, buff=0.1).shift(LEFT * 0.35)
        lost = T("lost", 24, RED_M).next_to(dots[8], UP, buff=0.1).shift(LEFT * 0.3)
        self.steps("A log shipper that started late missed the first lines. One that stopped early lost the last ones. Like a runner who shows up after the first plates went cold, and leaves before dessert.",
                   (0.8, FadeIn(old_l), GrowFromEdge(old, LEFT)), (0.8, *[dots[i].animate.set_color(RED_M) for i in (0, 1)], FadeIn(miss)),
                   (1.0, Wait(1.0)), (0.8, *[dots[i].animate.set_color(RED_M) for i in (7, 8)], FadeIn(lost)))
        self.play(FadeOut(VGroup(app_bar, app_l, dots, old, old_l, miss, lost)), run_time=0.6)

        # ---------- 4. ANALOGY + MAP: prep cooks and a runner
        prep = person(PURPLE_M).move_to([-3.6, -2.3, 0])
        prep_l = T("prep cook: chops, then leaves", 24, PURPLE_M).next_to(prep, RIGHT, buff=0.25)
        run = person(GOLD_M).move_to([1.6, -2.3, 0])
        run_l = T("runner: early, stays to the end", 24, GOLD_M).next_to(run, RIGHT, buff=0.25)
        prep_l.move_to([-3.25, -2.3, 0], aligned_edge=LEFT)
        prep.next_to(prep_l, LEFT, buff=0.25)
        run_l.move_to([1.95, -2.3, 0], aligned_edge=LEFT)
        run.next_to(run_l, LEFT, buff=0.25)
        self.beat("A real kitchen has two kinds of helper for this. Before the cook starts, a prep cook chops the onions and lays out the plates, then goes home.",
                  FadeIn(prep, shift=UP * 0.15), FadeIn(prep_l), Indicate(wp[1], color=PURPLE_M), run_time=2.0)
        self.beat("A runner arrives early, stays all evening, and leaves only after the last dish is out.",
                  FadeIn(run, shift=UP * 0.15), FadeIn(run_l), Indicate(tail[1], color=GOLD_M), run_time=1.8)
        m1 = T("= init container", 26, PURPLE_M).move_to([-3.1, -3.05, 0])
        m2 = T("= sidecar", 26, GOLD_M).move_to([2.6, -3.05, 0])
        self.beat("Kubernetes has both. The prep cook is an init container. The runner is a sidecar.",
                  FadeIn(m1, shift=UP * 0.1), FadeIn(m2, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(prep, prep_l, run, run_l, m1, m2)), run_time=0.6)

        # ---------- 5. PREDICT, then BREAK the wrong model
        rule = VGroup(T("init containers run first, one at a time, in order", 26),
                      T("each must exit with code 0 before the next starts", 26, GREY_B)).arrange(DOWN, buff=0.15).move_to([0, -2.5, 0])
        self.beat("First the rule for init containers. They run first, one at a time, in order. Each must exit with code 0, which means all went well, before the next one starts. Only then do the app containers start.",
                  FadeIn(rule, shift=UP * 0.1), run_time=2.0)
        man = VGroup(M("initContainers:", 24, GREY_B), M("  - write-page", 24, PURPLE_M), M("  - log-tailer", 24, GOLD_M),
                     M("containers:", 24, GREY_B), M("  - nginx", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        man.move_to([-3.4, -2.55, 0])
        self.play(FadeOut(rule), run_time=0.5)
        self.beat("Now look at the manifest. Under initContainers: write-page, then log-tailer. Under containers: nginx.",
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in man], lag_ratio=0.2), run_time=2.2)
        never = T("log-tailer never exits", 28, RED_M).move_to([2.8, -2.2, 0])
        q2 = T("so does nginx wait forever?", 28, YELLOW_M).move_to([2.8, -2.8, 0])
        self.beat("But a log reader follows the log forever. It never exits. By the rule we just learned, nginx waits for it to exit. So does nginx wait forever?",
                  FadeIn(never), Succession(Wait(2.2), FadeIn(q2, shift=UP * 0.1)), run_time=3.4)
        self.pause_guess([2.8, -3.35, 0])
        self.beat("If the rule were the whole story, yes. Our dish would never leave the kitchen. But log-tailer has one extra line.",
                  Indicate(man[2], color=GOLD_M), run_time=1.4)
        rp = M("restartPolicy: Always", 24, GOLD_M).move_to(tail[2])
        rp2 = M("    restartPolicy: Always", 24, GOLD_M).next_to(man[2], DOWN, buff=0.1).align_to(man[2], LEFT)
        self.play(FadeOut(VGroup(never, q2)), man[3:].animate.shift(DOWN * 0.42), run_time=0.5)
        self.beat("restartPolicy: Always. For an init container, that one line makes it a sidecar.",
                  FadeIn(rp2, shift=DOWN * 0.1), Transform(tail[2], rp), run_time=1.6)
        four = VGroup(T("1. starts in init order, before the app", 24), T("2. Kubernetes moves on once it is running", 24),
                      T("3. restarted if it crashes", 24), T("4. stops only after the app has stopped", 24))
        four.arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0.2, -2.55, 0], aligned_edge=LEFT)
        self.steps("For a sidecar, Kubernetes does four things. It starts it in init order, before the app. It moves on as soon as it is running, without waiting for it to exit. It restarts it if it crashes. And it stops it only after the app containers have stopped.",
                   (0.6, FadeIn(four[0])), (1.4, Wait(1.4)), (0.6, FadeIn(four[1])), (1.8, Wait(1.8)), (0.6, FadeIn(four[2])), (0.9, Wait(0.9)), (0.6, FadeIn(four[3])))
        self.wait(0.5)
        self.play(FadeOut(VGroup(man, rp2, four)), run_time=0.6)

        # ---------- 6. SHOW: the start, as kubectl get -w shows it
        cmd = M("$ kubectl get pod web -n scratch -w", 22, GREY_B).move_to([-5.9, -1.75, 0], aligned_edge=LEFT)
        COLS = (-5.9, -3.6, -1.6, 2.4)
        hdr = VGroup(*[M(h, 22, GREY_B).move_to([x, -2.35, 0], aligned_edge=LEFT) for h, x in zip(("NAME", "READY", "STATUS", "AGE"), COLS)])

        def row(ready, status, age, c=WHITE):
            return VGroup(*[M(v, 26, cc).move_to([x, -2.95, 0], aligned_edge=LEFT)
                            for v, x, cc in zip(("web", ready, status, age), COLS, (WHITE, c, c, GREY_B))])
        r = row("0/2", "Init:0/2", "1s", PURPLE_M)
        self.beat("Let us watch it start, the way the lesson does. At first nothing runs, and STATUS says Init:0/2. The first of two init containers is running.",
                  *waiting(tail), *waiting(ngx), *running(wp), FadeIn(cmd), FadeIn(hdr), FadeIn(r), run_time=2.0)
        page = chip("index.html", PURPLE_M, 22, mono=True).move_to(wp).shift(UP * 0.1)
        done = VGroup(tick(True, 0.16), T("exited 0", 24, GREEN_M)).arrange(RIGHT, buff=0.15).move_to(wp[2])
        self.steps("write-page writes index.html into the work folder, and exits with code 0. The prep cook goes home. STATUS moves to Init:1/2.",
                   (0.4, FadeIn(page)), (1.3, page.animate.move_to(work).set_opacity(0)), (0.5, Indicate(work[1], color=GREEN_M)),
                   (1.0, wp[0].animate.set_stroke(GREY_B, 2.5).set_fill(BLACK, 1), wp[1].animate.set_color(GREY_B), Transform(wp[2], done),
                    Transform(r, row("0/2", "Init:1/2", "4s", PURPLE_M))))
        self.beat("Next, the sidecar starts. As soon as it is running, it counts as ready, one of two, while nginx is still being created.",
                  *running(tail), Transform(r, row("1/2", "PodInitializing", "5s", GOLD_M)), run_time=1.8)
        self.beat("Then nginx starts. READY becomes two of two, because READY counts the sidecar too. The prep cook is not counted. He went home.",
                  *running(ngx), Transform(r, row("2/2", "Running", "11s", GREEN_M)), run_time=1.6)

        # ---------- 7. SHOW the payoff: shared folders
        cons = VGroup(M("$ kubectl exec web -c nginx -- curl -s localhost", 22, GREY_B),
                      M("hello from the init container", 26, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        cons.move_to([-5.9, -2.45, 0], aligned_edge=LEFT)
        self.beat("Now ask nginx for its page, from inside the Pod, on localhost.",
                  FadeOut(VGroup(cmd, hdr, r)), FadeIn(cons[0]), run_time=1.4)
        self.steps("hello from the init container. The prep cook has gone home, but the onions are still chopped. The page lives in the work folder, and the folder belongs to the Pod, not to the container that wrote it.",
                   (1.0, travel(Line(work.get_right(), ngx.get_top()), PURPLE_M, 1.0)), (0.6, FadeIn(cons[1], shift=UP * 0.1)),
                   (2.0, Wait(2.0)), (0.9, Indicate(work[1], color=GREEN_M)))
        logl = VGroup(M("$ kubectl logs web -c log-tailer", 22, GREY_B), M('"GET / HTTP/1.1" 200', 26, GOLD_M),
                      M('"GET /nope HTTP/1.1" 404', 26, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        logl.move_to(cons, aligned_edge=LEFT)
        self.steps("Ask for a page that does not exist too, then read the sidecar's logs. nginx wrote both visits into the logs folder, and the runner printed them.",
                   (0.6, FadeOut(cons)), (1.0, travel(Line(ngx.get_bottom(), logs.get_right()), YELLOW_M, 1.0)),
                   (1.0, travel(Line(logs.get_left(), tail.get_bottom()), YELLOW_M, 1.0)), (0.8, FadeIn(logl, shift=UP * 0.1)))
        self.play(FadeOut(logl), run_time=0.5)

        # the timeline again, fixed
        app_bar = Rectangle(width=6.4, height=0.3, stroke_width=0).set_fill(TEAL_M, 0.75).move_to([0.6, AY, 0])
        app_l = M("nginx", 22, TEAL_M).move_to([-4.6, AY, 0])
        dots = VGroup(*[Dot(radius=0.08, color=YELLOW_M).move_to([-2.3 + 0.72 * i, AY + 0.33, 0]) for i in range(9)])
        sbar = Rectangle(width=8.4, height=0.3, stroke_width=0).set_fill(GOLD_M, 0.75).move_to([0.6, HY, 0])
        s_l = M("sidecar", 22, GOLD_M).move_to([-4.6, HY, 0])
        self.steps("And the old problem with the log lines? The sidecar starts before the app, and stops only after the app has stopped. So every line gets read.",
                   (1.2, FadeIn(app_l), GrowFromEdge(app_bar, LEFT), FadeIn(dots)), (1.4, FadeIn(s_l), GrowFromEdge(sbar, LEFT)),
                   (1.0, *[d.animate.set_color(GREEN_M) for d in dots]))
        self.wait(0.4)
        self.play(FadeOut(VGroup(app_bar, app_l, dots, sbar, s_l)), run_time=0.6)

        # ---------- 8. GUARDRAIL
        g1 = T("Share a Pod only when you must share", 30, WHITE)
        g2 = T("a node, an address, or files.", 30, WHITE)
        gr = VGroup(g1, g2).arrange(DOWN, buff=0.15).move_to([0, -2.3, 0])
        self.beat("So should everything go on one tray? No. Share a Pod only when you must share a node, an address, or files.",
                  FadeIn(gr, shift=UP * 0.1), run_time=1.8)
        db = T("app and database: separate Pods", 28, GREY_B).move_to([0, -3.25, 0])
        self.beat("An app and its database belong in separate Pods, so you can scale and replace each one on its own. A tray, not a moving truck.",
                  FadeIn(db, shift=UP * 0.1), run_time=1.6)

        # ---------- 9. MORAL + quick check
        self.play(FadeOut(VGroup(gr, db)), wp[0].animate.set_stroke(PURPLE_M, 5), run_time=0.6)
        nums = VGroup()
        for i, (c, x) in enumerate(zip((PURPLE_M, GOLD_M, TEAL_M), PX)):
            n = Circle(radius=0.26, stroke_color=c, stroke_width=3).set_fill(BLACK, 1)
            nums.add(VGroup(n, T(str(i + 1), 26, c).move_to(n)).move_to([x - CW / 2 + 0.05, CY + CH / 2 - 0.05, 0]))
        cap = T("prep cooks first, the runner next, then the dish", 30, WHITE).move_to([0, -2.1, 0])
        self.beat("The moral of the story. Prep cooks first, one at a time, and each must finish. The runner next, and it stays to the end. Then the dish. And all of them share the Pod's address and folders.",
                  LaggedStart(*[GrowFromCenter(n) for n in nums], lag_ratio=0.5), Succession(Wait(1.5), FadeIn(cap)), run_time=4.0)
        ck = T("Quick check: READY 1/2, STATUS PodInitializing. Who is running?", 28, YELLOW_M).move_to([0, -2.9, 0])
        self.beat("One quick check. A Pod like ours shows READY one of two, and STATUS PodInitializing. Who is running right now?",
                  FadeIn(ck, shift=UP * 0.1), run_time=1.4)
        self.pause_guess([4.6, -3.45, 0])
        ans = T("The sidecar. write-page has finished, nginx is still being created.", 26, WHITE).move_to([0, -2.9, 0])
        self.beat("The sidecar. write-page has already finished, and nginx is still being created.",
                  FadeOut(ck), FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.2)
