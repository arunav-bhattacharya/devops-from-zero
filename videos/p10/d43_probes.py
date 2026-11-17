import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"/healthz\b", "health Z"), (r"/readyz\b", "ready Z"), (r"\bperiodSeconds\b", "period seconds"),
            (r"\btimeoutSeconds\b", "timeout seconds"), (r"\bfailureThreshold\b", "failure threshold"),
            (r"\binitialDelaySeconds\b", "initial delay seconds"), (r"\bEndpointSlice\b", "endpoint slice")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def waiter(c=TEAL_M, s=1.0):
    head = Circle(radius=0.2, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.3), opacity=1)
    body = RoundedRectangle(corner_radius=0.15, width=0.62, height=0.72, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.2), opacity=1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale(s)


def dot(c, r=0.09):
    return Circle(radius=r, stroke_color=c, stroke_width=2).set_fill(tint(c, 0.7), opacity=1)


class D43Probes(VoiceScene):
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
        self.title_card("Running is not the same as working", "three health checks, three different actions")

        # ---------- 1. the clipboard that counts, but does not notice
        XS = [-2.1, -0.3, 1.5, 3.3]
        ws = VGroup(*[waiter().move_to([x, -0.2, 0]) for x in XS])
        clip = RoundedRectangle(corner_radius=0.12, width=2.4, height=2.2, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.1), opacity=1)
        clip.move_to([-5.2, -0.2, 0])
        ctitle = T("on the floor", 26, GOLD_M).move_to(clip.get_center() + UP * 0.55)
        cnum = T("4", 64, WHITE).move_to(clip.get_center() + DOWN * 0.3)
        clipg = VGroup(clip, ctitle, cnum)
        self.beat("Picture a busy Friday night in a restaurant. The manager's clipboard says four waiters are on the floor.",
                  FadeIn(clipg), LaggedStart(*[GrowFromCenter(w) for w in ws], lag_ratio=0.2), run_time=2.6)
        frz = T("frozen", 26, GREY_B).next_to(ws[1], DOWN, buff=0.3)
        brk = T("card reader broken", 26, GREY_B).next_to(ws[3], DOWN, buff=0.3)
        self.beat("And that's true. But look closer. One of them has stood frozen at the coffee machine for ten minutes.",
                  ws[1].animate.set_opacity(0.45), FadeIn(frz, shift=UP * 0.1), run_time=2.0)
        self.beat("Another can't take orders, because their card reader is broken.",
                  ws[3].animate.set_opacity(0.45), FadeIn(brk, shift=UP * 0.1), run_time=1.6)
        guests = VGroup(*[Circle(radius=0.17, stroke_color=PURPLE_M, stroke_width=2.5).set_fill(tint(PURPLE_M, 0.3), 1) for _ in range(6)])
        guests.arrange(RIGHT, buff=0.22).move_to([1.6, 2.5, 0])
        glab = T("guests waiting", 26, PURPLE_M).next_to(guests, LEFT, buff=0.35)
        self.beat("The count is right, and guests are still waiting. Being on the floor is not the same as working.",
                  LaggedStart(*[FadeIn(g, shift=LEFT * 0.2) for g in guests], lag_ratio=0.15), FadeIn(glab),
                  Succession(Wait(2.0), Indicate(cnum, color=GOLD_M)), run_time=3.4)

        # the question
        run_t = M("Running", 26, GREEN_M).move_to(ctitle)
        self.beat("Now the same scene in Kubernetes. It tells you your Pod is Running. So your app works. Right? Let's see if that's really true.",
                  FadeOut(guests), FadeOut(glab), Transform(ctitle, run_t), run_time=2.0)

        # ---------- 2. what Kubernetes already handles, and what it misses
        crash = ws[0]
        rl = T("process exits", 26, RED_M).next_to(crash, DOWN, buff=0.3)
        fresh = waiter().move_to(crash)
        self.steps("Kubernetes already handles one kind of trouble. When a container's process exits, it starts it again.",
                   (1.0, FadeIn(rl, shift=UP * 0.1)), (0.8, Wait(0.8)), (0.8, FadeOut(crash, shift=DOWN * 0.3)), (0.8, GrowFromCenter(fresh)),
                   (0.6, FadeOut(rl)))
        ws.submobjects[0] = fresh
        self.beat("But our two waiters didn't crash. From the outside, they look just like healthy ones.",
                  Indicate(frz, color=WHITE), Indicate(brk, color=WHITE), run_time=2.2)
        stuck = T("stuck", 26, GREY_B).move_to(frz)
        nored = T("can't reach Redis", 26, GREY_B).move_to(brk)
        self.beat("Our lab app, hello-devops, keeps its visit count in Redis, a small database. A stuck app is the frozen waiter. An app that's up but can't reach Redis is the broken card reader.",
                  Transform(frz, stuck), Transform(brk, nored), run_time=2.4)
        pulse = M("has a pulse", 26, GREEN_M).move_to(ctitle)
        self.beat("Honestly, Running should have been called: has a pulse.",
                  Transform(ctitle, pulse), run_time=1.2)
        self.beat("It only tells you the process exists. That's the clipboard's mistake.",
                  Transform(ctitle, M("Running", 26, GREEN_M).move_to(ctitle)), run_time=1.6)
        self.beat("Wouldn't it be nice if the manager walked the floor, and actually asked each waiter a question, every so often?",
                  run_time=None)
        self.play(FadeOut(VGroup(clipg, ws[0], ws[2], frz, brk, ctitle)), run_time=0.6)

        # ---------- 3. the manager asks: a probe
        me = ws[1]
        mgr = waiter(GOLD_M).move_to([-3.6, 0.6, 0])
        self.play(me.animate.set_opacity(1).move_to([3.2, 0.6, 0]), FadeOut(ws[3]), FadeIn(mgr), run_time=1.0)
        qa = Arrow(mgr.get_right() + UP * 0.2, me.get_left() + UP * 0.2, buff=0.25, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.06)
        qt = T("\"How are you doing?\"", 26, GOLD_M).next_to(qa, UP, buff=0.15)
        aa = Arrow(me.get_left() + DOWN * 0.2, mgr.get_right() + DOWN * 0.2, buff=0.25, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.06)
        at = T("\"Fine!\"", 26, TEAL_M).next_to(aa, DOWN, buff=0.15)
        self.steps("Walk over, ask, listen.",
                   (1.0, GrowArrow(qa), FadeIn(qt)), (0.8, travel(qa, GOLD_M, 0.8)), (1.0, GrowArrow(aa), FadeIn(at)), (0.8, travel(aa, TEAL_M, 0.8)))
        ml = M("kubelet", 26, GOLD_M).next_to(mgr, DOWN, buff=0.3)
        mls = T("helper program on each node", 22, GREY_B).next_to(ml, DOWN, buff=0.12)
        wl = M("container", 26, TEAL_M).next_to(me, DOWN, buff=0.3)
        self.beat("Let's map that. The manager is the kubelet, the helper program on each node. The waiter is your container.",
                  FadeIn(ml), FadeIn(mls), Succession(Wait(2.4), FadeIn(wl)), run_time=3.4)
        qt2 = M("GET /healthz", 26, GOLD_M).move_to(qt)
        at2 = M("200", 26, TEAL_M).move_to(at)
        self.beat("The question is a probe: a small check on a timer. In the lab, the kubelet asks the container for a web address, like /healthz.",
                  Transform(qt, qt2), run_time=1.6)
        rules = VGroup(chip("200 to 399: pass", GREEN_M, 26), chip("503: not available", RED_M, 26)).arrange(RIGHT, buff=0.6).move_to([0, -2.6, 0])
        self.beat("The answer is a status code, the number a web server sends back. 200 to 399 is a pass. 503 means not available.",
                  Transform(at, at2), travel(aa, TEAL_M, 0.9), FadeIn(rules[0], shift=UP * 0.1), Succession(Wait(3.4), FadeIn(rules[1], shift=UP * 0.1)), run_time=4.6)
        self.play(FadeOut(VGroup(mgr, me, qa, qt, aa, at, ml, mls, wl, rules)), run_time=0.6)

        # ---------- 4. three questions, three actions
        Y = (1.9, 0.0, -1.9)
        COL = (GOLD_M, RED_M, BLUE_M)
        heads = T("one question is not enough", 28, GREY_B).move_to([0, 3.2, 0])
        self.beat("One question isn't enough. A good manager asks three, and each answer has its own action.",
                  FadeIn(heads), run_time=1.4)
        figs = VGroup(*[waiter(TEAL_M, 0.75).move_to([-5.6, y, 0]) for y in Y])
        quest = VGroup(*[T(q, 24).move_to([-1.85, y, 0]) for q, y in zip(
            ("\"Have you finished starting?\"", "\"Are you stuck?\"", "\"Can you take tables right now?\""), Y)])

        def action(lines, c, y):
            g = VGroup(*[T(l, 24 if i else 26, WHITE if i == 0 else GREY_B) for i, l in enumerate(lines)]).arrange(DOWN, buff=0.1)
            r = RoundedRectangle(corner_radius=0.12, width=3.5, height=g.height + 0.4, stroke_color=c, stroke_width=3).set_fill(tint(c), 1)
            r.move_to([4.6, y, 0]); g.move_to(r)
            return VGroup(r, g)

        acts = VGroup(action(["others wait", "never passes: restart"], COL[0], Y[0]),
                      action(["restart container", "go home, fresh one in"], COL[1], Y[1]),
                      action(["no new visitors", "keeps running"], COL[2], Y[2]))
        arrs = VGroup(*[Arrow([0.75, y, 0], [2.7, y, 0], buff=0.05, stroke_width=3, color=c, max_tip_length_to_length_ratio=0.12) for y, c in zip(Y, COL)])
        apron = T("still tying the apron", 20, GREY_B).next_to(figs[0], RIGHT, buff=0.2).shift(DOWN * 0.45)
        self.beat("First, to a new waiter still tying an apron: have you finished starting?",
                  FadeIn(figs[0]), FadeIn(quest[0], shift=RIGHT * 0.1), run_time=1.8)
        self.beat("Until it's yes, the other questions wait, so a slow start isn't mistaken for a stuck one. If yes never comes, it's restarted.",
                  GrowArrow(arrs[0]), FadeIn(acts[0]), run_time=1.8)
        self.beat("Second, to everyone, every so often: are you stuck?",
                  FadeIn(figs[1]), FadeIn(quest[1], shift=RIGHT * 0.1), run_time=1.4)
        self.beat("After enough no's in a row, the waiter goes home and a fresh one comes in. That's a restart.",
                  GrowArrow(arrs[1]), FadeIn(acts[1]), run_time=1.8)
        self.beat("Third: can you take tables right now?",
                  FadeIn(figs[2]), FadeIn(quest[2], shift=RIGHT * 0.1), run_time=1.4)
        self.beat("While it's no, no new tables go to that waiter. But nobody goes home.",
                  GrowArrow(arrs[2]), FadeIn(acts[2]), run_time=1.8)

        names = VGroup(*[M(n, 26, c).move_to([-5.6, y, 0]) for n, c, y in zip(("startup", "liveness", "readiness"), COL, Y)])
        self.steps("Now the names: the startup probe, the liveness probe, and the readiness probe.",
                   (0.9, FadeOut(heads)), (0.7, Transform(figs[0], names[0])), (0.7, Transform(figs[1], names[1])), (0.7, Transform(figs[2], names[2])))
        sub = T("wait, restart, or stop sending visitors", 28, YELLOW_M).move_to([0, 3.2, 0])
        self.beat("Three questions, three actions: wait, restart, or stop sending visitors.",
                  FadeIn(sub, shift=DOWN * 0.1), run_time=1.4)
        paths = VGroup(*[M(p, 22, GREY_B).next_to(names[i], DOWN, buff=0.15) for i, p in enumerate(("/healthz", "/healthz", "/readyz"))])
        self.beat("Our app has two addresses for this. /healthz answers while the process can serve. /readyz also checks Redis, and returns 503 when it's down.",
                  FadeIn(paths[0]), FadeIn(paths[1]), Succession(Wait(3.6), FadeIn(paths[2])), run_time=4.6)
        self.play(FadeOut(VGroup(quest, arrs, acts, sub)), run_time=0.6)

        # ---------- 5. how fast each one acts: multiply
        left = VGroup(VGroup(figs[0], paths[0]), VGroup(figs[1], paths[1]), VGroup(figs[2], paths[2]))
        self.play(left.animate.set_opacity(0.0), run_time=0.6)
        self.remove(left)
        X0, SC = -3.2, 0.15  # seconds to x units
        TY = (1.8, 0.0, -1.8)
        nm2 = VGroup(*[M(n, 26, c).move_to([-5.2, y, 0]) for n, c, y in zip(("startup", "liveness", "readiness"), COL, TY)])
        axes = VGroup(*[Line([X0, y, 0], [X0 + 63 * SC, y, 0], stroke_width=2, color=GREY_D) for y in TY])
        ticks = VGroup()
        for y in TY:
            for s in (0, 30, 60):
                ticks.add(T(f"{s} s", 20, GREY_B).move_to([X0 + s * SC, y - 0.4, 0]))
        st_dots = VGroup(*[dot(GREY_B, 0.07).move_to([X0 + 2 * (k + 1) * SC, TY[0], 0]) for k in range(30)])
        st_lab = M("2 s apart x 30 = 60 s", 24, GOLD_M).move_to([X0 + 30 * SC, TY[0] + 0.5, 0])
        self.steps("How fast does each one act? Multiply how often it checks by how many misses it allows. The lab's startup probe checks every two seconds, and allows thirty failures: up to sixty seconds to start.",
                   (1.2, FadeIn(nm2), Create(axes), FadeIn(ticks)), (2.8, LaggedStart(*[GrowFromCenter(d) for d in st_dots], lag_ratio=0.15)), (0.8, FadeIn(st_lab)))
        lv_dots = VGroup(*[dot(GREEN_M if k < 2 else RED_M).move_to([X0 + 10 * (k + 1) * SC, TY[1], 0]) for k in range(5)])
        self.beat("Your turn. Liveness checks every ten seconds, and acts after three misses in a row. How long does a stuck container keep its job? Pause and guess.",
                  GrowFromCenter(lv_dots[0]), GrowFromCenter(lv_dots[1]), run_time=1.6)
        self.wait(2.0)
        lv_lab = M("10 s x 3 = about 30 s", 24, RED_M).move_to([X0 + 40 * SC, TY[1] + 0.5, 0])
        rst = chip("restart", RED_M, 22).next_to(lv_dots[4], RIGHT, buff=0.3)
        self.steps("About thirty seconds. Miss, miss, miss, and it's replaced.",
                   (0.9, Wait(0.9)), (0.4, GrowFromCenter(lv_dots[2])), (0.4, GrowFromCenter(lv_dots[3])), (0.4, GrowFromCenter(lv_dots[4])),
                   (0.6, FadeIn(lv_lab), FadeIn(rst)))
        rd_dots = VGroup(*[dot(GREEN_M if k == 0 else RED_M).move_to([X0 + 5 * (k + 1) * SC, TY[2], 0]) for k in range(3)])
        rd_lab = M("5 s x 2 = about 10 s", 24, BLUE_M).move_to([X0 + 30 * SC, TY[2] + 0.5, 0])
        nov = chip("no visitors", BLUE_M, 22).next_to(rd_dots[2], RIGHT, buff=0.3)
        self.beat("Readiness checks every five seconds, and acts after two misses. So a Pod stops getting visitors within about ten seconds.",
                  LaggedStart(*[GrowFromCenter(d) for d in rd_dots], lag_ratio=0.4), Succession(Wait(1.4), AnimationGroup(FadeIn(rd_lab), FadeIn(nov))), run_time=3.0)

        self.play(FadeOut(VGroup(nm2, axes, ticks, st_dots, st_lab, lv_dots, lv_lab, rst, rd_dots, rd_lab, nov)), run_time=0.6)

        # ---------- 6. break it on purpose: liveness that checks Redis
        redis = mbox("redis", PURPLE_M, w=2.0, h=0.75, size=26).move_to([0, 2.5, 0])
        PX = (-3.6, 0, 3.6)
        pods = VGroup(*[waiter(TEAL_M, 0.8).move_to([x, -0.3, 0]) for x in PX])
        plab = VGroup(*[M("hello-devops", 22, GREY_B).next_to(p, DOWN, buff=0.2) for p in pods])
        wires = VGroup(*[link(redis, p, GREY_B) for p in pods])
        bad = M("liveness: /healthz checks Redis too", 26, RED_M).move_to([0, -2.6, 0])
        self.beat("Now a tempting idea. If checking is good, more checking is better. So let's make /healthz check Redis too.",
                  FadeIn(redis), LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.2), FadeIn(plab), Create(wires), run_time=2.6)
        self.beat("Liveness now asks about Redis as well. Sounds responsible, right?", FadeIn(bad, shift=UP * 0.1), run_time=1.2)
        rx = tick(False, 0.3).move_to(redis)
        self.beat("Picture Redis going down, for just one minute.",
                  Create(rx), wires.animate.set_color(RED_M), run_time=1.4)
        xs = VGroup(*[tick(False, 0.25).move_to(p) for p in pods])
        self.steps("Every hello-devops Pod fails liveness at about the same time. And the kubelet restarts all of them.",
                   (1.6, LaggedStart(*[Create(x) for x in xs], lag_ratio=0.2)), (1.4, Wait(1.4)),
                   (1.0, FadeOut(xs), *[p.animate.scale(0.5).set_opacity(0.15) for p in pods]))
        casc = T("a small outage becomes a full one", 28, RED_M).move_to([0, -3.3, 0])
        self.steps("But restarts can't fix Redis. And while they happen, no Pod can serve anything at all. A small outage just became a full one.",
                   (1.6, *[p.animate.scale(2.0).set_opacity(1) for p in pods]), (0.6, Wait(0.6)),
                   (0.8, LaggedStart(*[Create(x) for x in xs], lag_ratio=0.2)), (1.6, Wait(1.6)), (0.8, FadeIn(casc, shift=UP * 0.1)))
        self.beat("It's the manager who hears the card network is down for the whole street, and sends every waiter home. Well... nobody's card reader is a problem now.",
                  run_time=None)
        self.beat("So the point is: a restart only fixes trouble inside the container. The docs warn this leads to cascading failures, one failure setting off the next.",
                  Indicate(casc, color=RED_M), run_time=2.0)
        self.play(FadeOut(VGroup(xs, casc, bad)), run_time=0.5)
        rule = VGroup(T("Liveness asks about the container alone.", 30, YELLOW_M), T("Leave the database out of it.", 30, YELLOW_M)).arrange(DOWN, buff=0.2)
        rule.move_to([0, -2.85, 0])
        self.beat("Liveness asks about the container alone. Leave the database out of it.",
                  FadeIn(rule, shift=UP * 0.1), run_time=1.6)

        # ---------- 7. the fix, and a prediction
        good = M("readiness: /readyz checks Redis", 26, BLUE_M).move_to([0, -2.6, 0])
        self.beat("Checks on other services belong in readiness, because failing it only pauses visitors.",
                  FadeOut(rule), FadeIn(good, shift=UP * 0.1), run_time=1.6)
        cmd = M("kubectl scale deployment redis -n hello --replicas=0", 22, WHITE).move_to([0, 3.4, 0])
        fit(cmd, 12.6)
        self.beat("Let's try it the way the lab does. Scale Redis to zero. Pause and guess: what happens to READY, and what happens to RESTARTS?",
                  FadeOut(redis), FadeOut(rx), FadeOut(wires), FadeIn(cmd), run_time=2.4)
        self.wait(2.0)
        hdr = VGroup(M("READY", 24, GREY_B), M("STATUS", 24, GREY_B), M("RESTARTS", 24, GREY_B))
        CX = (-2.6, 0.2, 3.2)
        rows = VGroup()
        for j in range(3):
            y = 1.2 - 0.6 * j
            rows.add(VGroup(M("0/1", 24, BLUE_M).move_to([CX[0], y, 0]), M("Running", 24, GREEN_M).move_to([CX[1], y, 0]), M("0", 24, WHITE).move_to([CX[2], y, 0])))
        for h, x in zip(hdr, CX):
            h.move_to([x, 2.0, 0])
        tabl = VGroup(hdr, rows)
        self.steps("READY drops to zero of one. STATUS still says Running. And RESTARTS stays at zero.",
                   (0.8, FadeOut(VGroup(pods, plab)), FadeIn(hdr)), (0.9, LaggedStart(*[FadeIn(r[0]) for r in rows], lag_ratio=0.2)),
                   (0.8, LaggedStart(*[FadeIn(r[1]) for r in rows], lag_ratio=0.2)), (0.6, Wait(0.6)),
                   (0.8, LaggedStart(*[FadeIn(r[2]) for r in rows], lag_ratio=0.2)))
        self.beat("That quiet gap is the whole point. The waiters stay on the floor. They just don't get new tables.",
                  Indicate(VGroup(*[r[0] for r in rows]), color=BLUE_M), Succession(Wait(1.2), Indicate(VGroup(*[r[2] for r in rows]), color=WHITE)), run_time=2.6)
        flow = VGroup(chip("probe fails", BLUE_M, 22), chip("Pod not Ready", BLUE_M, 22), chip("Service skips it", BLUE_M, 22)).arrange(RIGHT, buff=0.7).move_to([0, -0.9, 0])
        farr = VGroup(*[Arrow(flow[i].get_right(), flow[i + 1].get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2) for i in range(2)])
        self.steps("The failed check marks the Pod not ready, and the Service skips it.",
                   (0.8, FadeIn(flow[0])), (0.8, GrowArrow(farr[0]), FadeIn(flow[1])), (0.8, GrowArrow(farr[1]), FadeIn(flow[2])))
        back = VGroup(*[M("1/1", 24, BLUE_M).move_to(r[0]) for r in rows])
        cmd2 = M("kubectl scale deployment redis -n hello --replicas=1", 22, WHITE).move_to(cmd)
        fit(cmd2, 12.6)
        self.beat("Scale Redis back to one, and the Pods become ready again, on their own. Nobody touched them.",
                  Transform(cmd, cmd2), Succession(Wait(1.4), AnimationGroup(*[Transform(r[0], b) for r, b in zip(rows, back)])), run_time=2.6)
        self.play(FadeOut(VGroup(flow, farr)), run_time=0.5)

        # ---------- 8. guardrail
        lim = T("if every Pod fails readiness at once: no ready Pods, users get errors", 26, RED_M).move_to([0, -0.9, 0])
        fit(lim, 12.4)
        zero = VGroup(*[M("0/1", 24, BLUE_M).move_to(r[0]) for r in rows])
        self.beat("One honest limit. If every Pod fails readiness at once, the Service has no ready Pods left, and users get errors.",
                  *[Transform(r[0], z) for r, z in zip(rows, zero)], FadeIn(lim, shift=UP * 0.1), FadeOut(good), run_time=2.4)
        lab = VGroup(chip("timeoutSeconds: 2", BLUE_M, 24, mono=True), chip("failureThreshold: 2", BLUE_M, 24, mono=True)).arrange(RIGHT, buff=0.6).move_to([0, -1.95, 0])
        self.beat("So the lab's readiness probe isn't too strict: a two second timeout, and two failures.",
                  LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in lab], lag_ratio=0.4), run_time=2.0)
        self.play(FadeOut(VGroup(cmd, tabl, lim, lab)), run_time=0.6)

        # ---------- 9. moral and a quick check
        mor = VGroup(T("Being present is not the same as working.", 32, WHITE),
                     T("startup: wait", 28, GOLD_M),
                     T("liveness: go home, a fresh one comes in", 28, RED_M),
                     T("readiness: step aside for a moment", 28, BLUE_M),
                     T("liveness never asks about the database", 28, YELLOW_M)).arrange(DOWN, buff=0.35)
        mor.move_to([0, 0.2, 0])
        self.beat("The moral of the story: being present is not the same as working. Startup waits. Liveness sends you home. Readiness steps you aside. And liveness never asks about the database.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mor], lag_ratio=0.7), run_time=6.0)
        self.play(FadeOut(mor), run_time=0.6)
        q = VGroup(T("An app needs 90 seconds to start.", 30), T("Liveness kills it at 30 seconds, again and again.", 30),
                   T("Which probe fixes it?", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 0.8, 0])
        self.beat("One quick check before you go. An app needs ninety seconds to start, and liveness kills it at thirty, again and again. Which probe fixes it? Pause and think.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in q], lag_ratio=0.5), run_time=4.0)
        self.wait(2.0)
        ans = chip("a startup probe that allows more than 90 s", GOLD_M, 28).move_to([0, -1.6, 0])
        self.beat("A startup probe that allows more than ninety seconds. It holds liveness back until the app has started. Thanks for watching.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.0)
