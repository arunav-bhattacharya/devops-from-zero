import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Day 40, fifth pass (Venkat style). Restaurant manager world: changing shifts one waiter at a time.
# Concept: a rolling update (maxSurge 1, maxUnavailable 0, 3 replicas, as in the lab), readiness as the gate,
# and a broken version that stalls instead of breaking the floor.
# Colours: version 1.0.0 = BLUE, version 1.1.0 = GOLD, broken version = RED, Service = WHITE,
# readiness = TEAL, counts and prompts = YELLOW.

SAY.extend([(r"\b1\.0\.0\b", "one point oh point oh"), (r"\b1\.1\.0\b", "one point one point oh"), (r"\bmaxSurge\b", "max surge"),
            (r"\bmaxUnavailable\b", "max unavailable"), (r"\bImagePullBackOff\b", "image pull back off"),
            (r"\bErrImagePull\b", "error image pull"), (r"\bProgressDeadlineExceeded\b", "progress deadline exceeded"),
            (r"\bprogressDeadlineSeconds\b", "progress deadline seconds"), (r"\bReplicaSets\b", "replica sets"), (r"\bReplicaSet\b", "replica set")])

OLD, NEW, BAD = BLUE_M, GOLD_M, RED_M
PY = -1.05
LX = [-5.0, -3.9, -2.8]
RX = [2.8, 3.9, 5.0]


def tint(c, k=0.3):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def pod(color, x, ready=True):
    c = Circle(radius=0.32, stroke_color=color, stroke_width=3).move_to([x, PY, 0])
    if ready:
        return c.set_fill(tint(color), opacity=1)
    return DashedVMobject(c, num_dashes=16)


def rsbox(version, color, count, x):
    r = RoundedRectangle(corner_radius=0.12, width=4.4, height=1.1, stroke_color=color, stroke_width=3).move_to([x, 0.45, 0])
    r.set_fill(tint(color, 0.12), opacity=1)
    nm = T("ReplicaSet", 24, GREY_B).move_to(r.get_corner(UL) + [0.2, -0.24, 0], aligned_edge=UL)
    im = M(version, 24, color).move_to(r.get_corner(DL) + [0.2, 0.22, 0], aligned_edge=DL)
    n = T(str(count), 44, color).move_to(r.get_right() + LEFT * 0.45)
    return VGroup(r, nm, im, n)


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


class D40ShiftChange(Base):
    def construct(self):
        self.title_card("Change every waiter without closing the doors", "a rolling update, one ready Pod at a time")

        # ---------- 1. QUESTION + two bad plans
        xs = [-2.2, 0, 2.2]
        tables = VGroup(*[RoundedRectangle(corner_radius=0.15, width=1.5, height=0.9, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1).move_to([x, -0.9, 0]) for x in xs])
        olds = VGroup(*[person(OLD).next_to(t, UP, buff=0.15) for t in tables])
        q = T("new menu at noon: how do you swap the whole shift?", 30, YELLOW_M).move_to([0, 2.7, 0])
        self.beat("Saturday, noon, a full restaurant. A new menu is ready, and the waiters trained for it wait at the back door. How do you swap the whole shift while guests keep arriving?",
                  FadeIn(tables), LaggedStart(*[FadeIn(o, shift=DOWN * 0.1) for o in olds], lag_ratio=0.2), FadeIn(q, shift=DOWN * 0.1), run_time=2.4)
        news = VGroup(*[person(NEW).move_to(o) for o in olds])
        closed = chip("doors closed: nobody serving", BAD, 26).move_to([0, -2.6, 0])
        self.steps("Plan A. Close for an hour. Send the old shift home, then let the new one in. Simple. And the street would remember that hour.",
                   (0.9, *[FadeOut(o, shift=LEFT * 0.3) for o in olds]), (0.8, FadeIn(closed, shift=UP * 0.1)), (1.2, Wait(1.2)),
                   (0.9, LaggedStart(*[FadeIn(n, shift=LEFT * 0.3) for n in news], lag_ratio=0.2)))
        self.play(FadeOut(closed), *[n.animate.become(person(OLD).move_to(n)) for n in news], run_time=0.6)
        bad = VGroup(*[person(BAD).move_to(o) for o in olds])
        lost = chip("can't find the plates", BAD, 26).move_to([0, -2.6, 0])
        self.steps("Plan B. Swap everyone at once, no closing. Bold. But if the new waiters cannot find the plates, every table notices, all together. Bold is not a release plan.",
                   (0.9, *[Transform(n, person(NEW).move_to(n)) for n in news]), (1.2, Wait(1.2)),
                   (0.8, *[Transform(n, b) for n, b in zip(news, bad)], *[t.animate.set_stroke(BAD) for t in tables], FadeIn(lost, shift=UP * 0.1)))
        self.beat("So the point is: we need a third way. Change the shift a little at a time, and never leave a table alone.",
                  FadeOut(VGroup(news, lost, q)), *[t.animate.set_stroke(GREY_B) for t in tables], run_time=1.4)
        self.play(FadeOut(tables), run_time=0.5)

        # ---------- 2. FAMILIAR: the Deployment and its first shift list
        cl = VGroup(M("Deployment hello-devops", 24, GREY_B), M("replicas: 3", 24), M("image: hello-devops:1.0.0", 24, OLD))
        cl.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        crect = RoundedRectangle(corner_radius=0.15, width=cl.width + 0.6, height=cl.height + 0.5, stroke_color=WHITE, stroke_width=3).set_fill(BLACK, 1)
        card = VGroup(crect, cl.move_to(crect)).move_to([0, 2.5, 0])
        self.beat("Kubernetes has a shift manager for this, the Deployment. Ours runs hello-devops, three copies, version 1.0.0.",
                  Create(crect), LaggedStart(*[Write(l) for l in cl], lag_ratio=0.2), run_time=2.0)
        old = rsbox("1.0.0", OLD, 3, -3.9)
        opods = [pod(OLD, x) for x in LX]
        self.beat("It does not make Pods itself. It keeps a shift list for each version, called a ReplicaSet, and the ReplicaSet keeps three Pods of that version running.",
                  Create(old[0]), FadeIn(old[1:]), LaggedStart(*[GrowFromCenter(p) for p in opods], lag_ratio=0.2), run_time=2.2)
        svc = box("Service", WHITE, w=2.2, h=0.7, size=26).move_to([0, -2.3, 0])

        def wires(pods):
            return VGroup(*[DashedLine(svc.get_top(), p.get_bottom(), dash_length=0.08, stroke_width=1.5, color=GREY_B) for p in pods])

        def traffic(ws, color=WHITE):
            return LaggedStart(*[travel(Line(w.get_start(), w.get_end()), color, 0.7) for w in ws], lag_ratio=0.15)

        sw = wires(opods)
        self.beat("In front of them, a Service sends visitors to every Pod that is ready.",
                  Create(svc[0]), Write(svc[1]), Create(sw), run_time=1.4)
        self.play(traffic(sw), run_time=1.1)

        new_img = M("image: hello-devops:1.1.0", 24, NEW).move_to(cl[2], aligned_edge=LEFT)
        self.beat("Now you change the image to 1.1.0. That line is part of the Pod template, the recipe for each Pod, and only a change to the template starts a new version.",
                  Transform(cl[2], new_img), run_time=1.6)
        new = rsbox("1.1.0", NEW, 0, 3.9)
        self.beat("So the Deployment opens a second shift list, a new ReplicaSet for 1.1.0, starting at zero Pods.",
                  Create(new[0]), FadeIn(new[1:]), run_time=1.6)

        # ---------- 3. ANALOGY + MAP: the careful shift change, and its two dials
        self.beat("A careful manager changes shifts like this. One new waiter comes in. When they are ready, one old waiter goes home. Repeat until the whole floor is new.",
                  Indicate(new[0], color=NEW), Indicate(old[0], color=OLD), run_time=2.0)
        rules = VGroup(M("maxSurge: 1", 24, YELLOW_M), T("extra Pods allowed", 24, GREY_B),
                       M("maxUnavailable: 0", 24, YELLOW_M), T("missing Pods allowed", 24, GREY_B))
        for m, y in zip(rules, (3.15, 2.75, 2.2, 1.8)):
            m.move_to([3.05, y, 0], aligned_edge=LEFT)
        self.steps("Two dials set the pace. maxSurge: how many extra Pods may exist above the wanted number. maxUnavailable: how many may be missing below it. The lab picks one, and zero.",
                   (0.8, FadeIn(rules[0], shift=LEFT * 0.2), FadeIn(rules[1], shift=LEFT * 0.2)), (1.8, Wait(1.8)),
                   (0.8, FadeIn(rules[2], shift=LEFT * 0.2), FadeIn(rules[3], shift=LEFT * 0.2)))
        pq = T("at most how many Pods? at least how many ready?", 28, YELLOW_M).move_to([0, -3.2, 0])
        self.beat("Three replicas, one extra allowed, none missing. So during the update: at most how many Pods? And at least how many ready?",
                  FadeIn(pq, shift=UP * 0.1), run_time=1.4)
        self.pause_guess([-4.6, 2.55, 0])

        def counts(total, ready):
            g = VGroup(T(f"Pods now: {total}", 28, YELLOW_M if total == 4 else WHITE),
                       T(f"ready now: {ready}", 28, YELLOW_M if ready == 3 else WHITE))
            g.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            return g.move_to([-6.45, 2.5, 0], aligned_edge=LEFT)

        cnt = counts(3, 3)
        self.beat("At most four. At least three ready. Let us watch it hold.",
                  FadeOut(pq), FadeIn(cnt, shift=RIGHT * 0.2), run_time=1.2)

        # ---------- 4. SHOW: the four steps
        def stepcap(text):
            return T(text, 28, YELLOW_M).move_to([0, -3.2, 0])

        def setn(rs, n):
            return Transform(rs[3], T(str(n), 44, rs[0].get_stroke_color()).move_to(rs[3]))

        npods = [None, None, None]
        npods[0] = pod(NEW, RX[0], ready=False)
        cap = stepcap("1. one new Pod comes in")
        self.beat("Step one. The new ReplicaSet scales to one. Four Pods: three old, one new.",
                  FadeIn(cap, shift=UP * 0.15), setn(new, 1), Create(npods[0]), Transform(cnt, counts(4, 3)), run_time=1.6)
        probe = M("ready?", 24, TEAL_M).next_to(npods[0], UP, buff=0.12)
        self.beat("It is starting, but not ready yet, so the Service sends it nothing. And no old Pod may leave. Everyone waits for one word: ready.",
                  FadeIn(probe), traffic(sw), run_time=2.0)
        ok = pod(NEW, RX[0])
        nw = wires([ok])
        self.beat("The new Pod passes its readiness check. Now it gets visitors.",
                  Transform(npods[0], ok), FadeOut(probe), Create(nw), run_time=1.4)
        self.play(traffic(VGroup(*sw, *nw)), run_time=1.1)
        cap2 = stepcap("2. then one old Pod goes home")
        self.beat("Step two. Only now may one old Pod go. The old ReplicaSet scales to two.",
                  Transform(cap, cap2), setn(old, 2), FadeOut(opods[0]), FadeOut(sw[0]), Transform(cnt, counts(3, 3)), run_time=1.6)
        cap3 = stepcap("3. repeat: in, wait for ready, out")
        npods[1] = pod(NEW, RX[1])
        npods[2] = pod(NEW, RX[2])
        w1, w2 = wires([npods[1]]), wires([npods[2]])
        self.steps("Then the same again. A second new Pod, wait for ready, one more old Pod home. And a third.",
                   (0.4, Transform(cap, cap3)),
                   (0.9, setn(new, 2), GrowFromCenter(npods[1]), Create(w1), Transform(cnt, counts(4, 3))),
                   (0.9, setn(old, 1), FadeOut(opods[1]), FadeOut(sw[1]), Transform(cnt, counts(3, 3))),
                   (0.9, setn(new, 3), GrowFromCenter(npods[2]), Create(w2), Transform(cnt, counts(4, 3))),
                   (0.9, setn(old, 0), FadeOut(opods[2]), FadeOut(sw[2]), Transform(cnt, counts(3, 3))))
        allnew = VGroup(*nw, *w1, *w2)
        self.play(traffic(allnew, NEW), run_time=1.1)
        self.beat("Never fewer than three ready Pods. The price is speed, and room on some node for one extra Pod at a time.",
                  FadeOut(cap), Indicate(cnt[1], color=YELLOW_M), run_time=1.6)
        both = T("for a while, both versions serve visitors", 26, GREY_B).move_to([0, -3.2, 0])
        self.beat("And notice: in the middle, both versions served visitors at once. So version two must work alongside version one.",
                  FadeIn(both, shift=UP * 0.1), run_time=1.6)
        drawer = chip("1.0.0 ReplicaSet: 0 Pods, kept", OLD, 24).move_to([-3.9, -0.2, 0])
        self.beat("The old ReplicaSet is not deleted. It stays at zero, like last month's menu in a drawer, and that makes going back fast.",
                  FadeOut(both), Transform(old, drawer), run_time=1.8)

        # ---------- 5. BREAK: a version that can never start
        self.play(FadeOut(old), FadeOut(cnt), run_time=0.8)
        self.play(new.animate.move_to([-3.9, 0.45, 0]), *[p.animate.move_to([x, PY, 0]) for p, x in zip(npods, LX)],
                  FadeOut(allnew), run_time=1.0)
        sw = wires(npods)
        self.play(Create(sw), run_time=0.5)
        bad_img = M("image: hello-devops:1.10", 24, BAD).move_to(cl[2], aligned_edge=LEFT)
        self.beat("Now the scary one. Someone ships a typo: a tag that does not exist. Pause and guess. What do the visitors notice? And does Kubernetes roll back on its own?",
                  Transform(cl[2], bad_img), run_time=1.6)
        self.pause_guess([0, -3.05, 0])
        brs = rsbox("1.10", BAD, 1, 3.9)
        bp = pod(BAD, RX[0], ready=False)
        cnt = counts(4, 3)
        self.beat("A third ReplicaSet scales to one. Its Pod cannot pull, that is download, its image.",
                  Create(brs[0]), FadeIn(brs[1:]), Create(bp), FadeIn(cnt), run_time=1.8)
        st = M("ErrImagePull", 22, BAD).next_to(bp, DOWN, buff=0.15)
        st2 = M("ImagePullBackOff", 22, BAD).move_to(st)
        self.steps("ErrImagePull. Then ImagePullBackOff. It never becomes ready.",
                   (0.6, FadeIn(st)), (1.2, Wait(1.2)), (0.6, Transform(st, st2)))
        hold = SurroundingRectangle(VGroup(*npods), color=YELLOW_M, buff=0.15, corner_radius=0.1)
        self.beat("And with maxUnavailable at zero, no old Pod may leave. So the three good Pods keep serving every visitor. The broken one gets none.",
                  Create(hold), traffic(sw, NEW), run_time=2.2)
        stall = T("the rollout stalls, and waits", 30, YELLOW_M).move_to([0, -3.2, 0])
        self.beat("Visitors notice very little. The rollout simply stalls. But Kubernetes does not roll back by itself. It waits.",
                  FadeIn(stall, shift=UP * 0.1), run_time=1.6)
        dl = VGroup(T("after 600 s, by default:", 22, GREY_B), M("ProgressDeadlineExceeded", 22, BAD)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        dl.move_to([2.55, 2.75, 0], aligned_edge=LEFT)
        self.beat("After six hundred seconds by default, the Deployment reports ProgressDeadlineExceeded.",
                  FadeOut(rules), FadeIn(dl), run_time=1.6)
        undo = M("$ kubectl rollout undo deployment/hello-devops", 24, WHITE).move_to([0, -3.2, 0])
        self.steps("kubectl rollout status, with a timeout, then fails, so an automatic check can notice. And you, or that check, run rollout undo.",
                   (0.6, FadeOut(stall)), (1.6, Wait(1.6)), (0.8, FadeIn(undo, shift=UP * 0.1)))
        back = M("image: hello-devops:1.1.0", 24, NEW).move_to(cl[2], aligned_edge=LEFT)
        self.beat("The broken shift list goes back to zero. The floor never noticed.",
                  Transform(cl[2], back), Transform(brs[3], T("0", 44, BAD).move_to(brs[3])), FadeOut(bp), FadeOut(st), FadeOut(hold),
                  Transform(cnt, counts(3, 3)), run_time=1.8)

        # ---------- 6. NAME + GUARDRAIL: ready is the whole safety
        self.play(FadeOut(VGroup(undo, dl, brs)), run_time=0.7)
        name = T("rolling update", 36, YELLOW_M).move_to([3.9, 0.9, 0])
        gl = VGroup(T("a few Pods at a time,", 24, GREY_B), T("so the app keeps answering", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([3.0, 0.05, 0])
        gl.align_to(np.array([0.3, 0, 0]), LEFT)
        name.align_to(gl, LEFT)
        self.beat("What we just watched has a name: a rolling update. It replaces old Pods with new ones a few at a time, so the app keeps answering. It is the default strategy.",
                  FadeIn(name, shift=UP * 0.1), FadeIn(gl), run_time=2.0)
        self.beat("But every step waited for one word: ready. So who decides that? A readiness check, which the kubelet asks every few seconds: can you take visitors?",
                  Indicate(cnt[1], color=TEAL_M), run_time=2.0)
        apron = T("no readiness check: ready the moment the container starts", 26, BAD).move_to([0, -3.2, 0])
        self.beat("Without one, a Pod counts as ready as soon as its container starts. A new waiter who is ready the moment they walk in, apron or not.",
                  FadeIn(apron, shift=UP * 0.1), run_time=1.8)
        self.beat("And a version that starts but answers every request with an error is worse than our typo. It looks ready, and the rollout completes.",
                  Indicate(apron, color=BAD), run_time=1.6)
        rule = T("A Deployment is only as careful as its readiness check.", 30, YELLOW_M).move_to([0, -3.2, 0])
        self.beat("So here is the rule. A Deployment is only as careful as its readiness check. Add one before you trust rolling updates.",
                  FadeOut(apron), FadeIn(rule, shift=UP * 0.1), run_time=1.8)

        # ---------- 7. MORAL + quick check
        stage = VGroup(card, new, *npods, sw, svc, cnt, name, gl, rule)
        self.play(FadeOut(stage), run_time=0.8)
        moral = VGroup(T("one in, wait for ready, one out", 32, NEW), T("the old menu stays in the drawer", 30, OLD),
                       T("a broken version stalls; it does not roll back", 30, BAD)).arrange(DOWN, buff=0.3).move_to([0, 1.6, 0])
        self.steps("The moral of the story. One in, wait for ready, one out. The old menu stays in the drawer. And a broken version stalls, so you roll back yourself.",
                   (0.8, FadeIn(moral[0], shift=UP * 0.1)), (1.2, Wait(1.2)), (0.8, FadeIn(moral[1], shift=UP * 0.1)), (1.0, Wait(1.0)), (0.8, FadeIn(moral[2], shift=UP * 0.1)))
        ck = VGroup(T("Quick check: 4 replicas, both dials at the default 25%.", 28, YELLOW_M),
                    T("How many extra Pods, and how many missing?", 28, YELLOW_M)).arrange(DOWN, buff=0.15).move_to([0, -0.8, 0])
        self.beat("One quick check. Four replicas, with both dials at their default, twenty five percent. How many extra Pods may exist, and how many may be missing?",
                  FadeIn(ck, shift=UP * 0.1), run_time=1.8)
        self.pause_guess([0, -2.1, 0])
        ans = VGroup(T("One extra (surge rounds up), one missing (unavailable rounds down).", 26),
                     T("So at least 3 available, and at most 5 in total.", 26, GREY_B)).arrange(DOWN, buff=0.15).move_to([0, -2.4, 0])
        self.beat("One extra, because surge rounds up. One missing, because unavailable rounds down. So at least three available Pods, and at most five in total.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.8)
        self.wait(1.2)
