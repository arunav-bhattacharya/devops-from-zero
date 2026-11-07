import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

OLD, NEW = BLUE_M, GOLD_M
PY = -1.05                     # y of the Pod row
OLD_X = [-5.0, -3.9, -2.8]     # Pod slots under the old ReplicaSet
NEW_X = [2.8, 3.9, 5.0]        # Pod slots under the new ReplicaSet


def tint(c, k=0.3):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def pod(color, x, ready=True):
    c = Circle(radius=0.32, stroke_color=color, stroke_width=3).move_to([x, PY, 0])
    if ready:
        return c.set_fill(tint(color), opacity=1)
    return DashedVMobject(c, num_dashes=16)


def rsbox(name, image, color, count, x):
    r = RoundedRectangle(corner_radius=0.12, width=4.7, height=1.1, stroke_color=color, stroke_width=3).move_to([x, 0.45, 0])
    r.set_fill(tint(color, 0.12), opacity=1)
    nm = M(name, 20, GREY_B).move_to(r.get_corner(UL) + [0.2, -0.2, 0], aligned_edge=UL)
    im = M(image, 20, color).move_to(r.get_corner(DL) + [0.2, 0.2, 0], aligned_edge=DL)
    n = T(str(count), 44, color).move_to(r.get_right() + LEFT * 0.42)
    return VGroup(r, nm, im, n)


class D40Rollout(VoiceScene):
    def construct(self):
        self.title_card("A rolling update, step by step", "two ReplicaSets trade Pods, one ready Pod at a time")

        # the Deployment and its first ReplicaSet
        cl = VGroup(M("Deployment hello-devops", 22, GREY_B), M("replicas: 3", 22), M("template:", 22),
                    M("image: hello-devops:1.0.0", 22, OLD))
        cl.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        cl[3].shift(RIGHT * 0.35)
        crect = RoundedRectangle(corner_radius=0.15, width=cl.width + 0.6, height=cl.height + 0.5, stroke_color=WHITE, stroke_width=3)
        crect.set_fill(BLACK, opacity=1)
        card = VGroup(crect, cl.move_to(crect)).move_to([0, 2.55, 0])
        old = rsbox("hello-devops-698679bfb", "image: hello-devops:1.0.0", OLD, 3, -3.9)
        old_lab = T("ReplicaSet", 22, GREY_B).next_to(old, UP, buff=0.12).align_to(old, LEFT)
        olds = [pod(OLD, x) for x in OLD_X]
        self.beat("hello-devops runs as a Deployment with three replicas. The Deployment does not make Pods itself.",
                  Create(crect), LaggedStart(*[Write(l) for l in cl], lag_ratio=0.2), run_time=2.0)
        self.beat("It owns a ReplicaSet, and the ReplicaSet keeps three Pods of version 1.0.0 running.",
                  Create(old[0]), FadeIn(old[1:]), FadeIn(old_lab), LaggedStart(*[GrowFromCenter(p) for p in olds], lag_ratio=0.2), run_time=2.0)

        svc = box("Service", WHITE, w=2.2, h=0.7, size=26).move_to([0, -2.55, 0])

        def wires(pods):
            return VGroup(*[DashedLine(svc.get_top(), p.get_bottom(), dash_length=0.08, stroke_width=1.5, color=GREY_B) for p in pods])

        def traffic(ws, color=WHITE):
            return LaggedStart(*[travel(Line(w.get_start(), w.get_end()), color, 0.8) for w in ws], lag_ratio=0.15)

        sw = wires(olds)
        self.beat("In front of them, a Service sends requests to every ready Pod.",
                  Create(svc[0]), Write(svc[1]), Create(sw), run_time=1.6)
        self.play(traffic(sw), run_time=1.2)

        # what starts a rollout
        new_img = M("image: hello-devops:1.1.0", 22, NEW).move_to(cl[3], aligned_edge=LEFT)
        self.beat("Now you change the image to 1.1.0. That line sits under template, and only a change to the template starts a rollout.",
                  Transform(cl[3], new_img), Indicate(cl[2], color=NEW), run_time=1.8)
        self.beat("Changing replicas would not. That is only scaling.",
                  Indicate(cl[1], color=GREY_B), run_time=1.0)

        # the Deployment compares templates
        cmp1 = DashedLine([cl[3].get_left()[0], crect.get_bottom()[1] - 0.04, 0], [cl[3].get_left()[0], old[0].get_top()[1] + 0.04, 0], dash_length=0.08, stroke_width=2, color=GREY_B)
        x1 = tick(False, 0.18).move_to(cmp1)
        self.beat("On its next pass, the Deployment controller compares its template with the template inside each ReplicaSet it owns.",
                  Create(cmp1), Indicate(cl[3], color=NEW), Indicate(old[2], color=OLD), run_time=1.8)
        self.beat("1.1.0 is not 1.0.0. None matches.", Create(x1), run_time=0.8)
        new = rsbox("hello-devops-5c7d9f8b6", "image: hello-devops:1.1.0", NEW, 0, 3.9)
        new_lab = T("new ReplicaSet", 22, GREY_B).next_to(new, UP, buff=0.12).align_to(new, RIGHT)
        self.beat("So it creates a new ReplicaSet for the new template, starting at zero Pods.",
                  FadeOut(cmp1), FadeOut(x1), Create(new[0]), FadeIn(new[1:]), FadeIn(new_lab), run_time=1.8)

        # the pace
        rules = VGroup(M("maxSurge: 1", 22, YELLOW_M), T("at most 4 Pods", 24, GREY_B),
                       M("maxUnavailable: 0", 22, YELLOW_M), T("at least 3 ready", 24, GREY_B))
        for i, (m, y) in enumerate(zip(rules, (3.25, 2.83, 2.25, 1.83))):
            m.move_to([3.0, y, 0], aligned_edge=LEFT)
        self.beat("Two settings set the pace. maxSurge is one: at most one extra Pod, so four in all.",
                  FadeIn(rules[0], shift=LEFT * 0.2), FadeIn(rules[1], shift=LEFT * 0.2), run_time=1.4)
        self.beat("maxUnavailable is zero: never fewer than three ready Pods.",
                  FadeIn(rules[2], shift=LEFT * 0.2), FadeIn(rules[3], shift=LEFT * 0.2), run_time=1.4)

        def counts(total, ready):
            g = VGroup(T(f"Pods now: {total}", 28, YELLOW_M if total == 4 else WHITE),
                       T(f"ready now: {ready}", 28, YELLOW_M if ready == 3 else WHITE))
            g.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
            return g.move_to([-6.6, 2.55, 0], aligned_edge=LEFT)

        cnt = counts(3, 3)
        self.play(FadeIn(cnt, shift=RIGHT * 0.2), run_time=0.7)

        def stepcap(text):
            return T(text, 28, YELLOW_M).move_to([0, -3.45, 0])

        def setn(rs, n):
            return Transform(rs[3], T(str(n), 44, rs[0].get_stroke_color()).move_to(rs[3]))

        # step 1
        news = [None, None, None]
        news[0] = pod(NEW, NEW_X[0], ready=False)
        cap = stepcap("1. new ReplicaSet scales to 1")
        self.beat("Step one. The new ReplicaSet scales to one. Now there are four Pods: three old, one new.",
                  FadeIn(cap, shift=UP * 0.15), setn(new, 1), Create(news[0]), Transform(cnt, counts(4, 3)), run_time=1.8)
        nr = T("not ready", 22, NEW).next_to(news[0], DOWN, buff=0.15)
        self.beat("The new Pod is starting, but it is not ready yet. The Service sends it nothing.",
                  FadeIn(nr), traffic(sw), run_time=1.8)
        hold = SurroundingRectangle(VGroup(*olds), color=YELLOW_M, buff=0.15, corner_radius=0.1)
        self.beat("And with maxUnavailable at zero, no old Pod may go. So the Deployment waits.",
                  Create(hold), Indicate(rules[2], color=YELLOW_M), run_time=1.6)

        # readiness gates the step
        probe = M("ready?", 22, TEAL_M).next_to(news[0], UP, buff=0.12)
        self.beat("Readiness decides when each step may happen. The kubelet checks the new Pod, and writes the result into the Pod's status.",
                  FadeIn(probe, shift=DOWN * 0.1), Indicate(news[0], color=TEAL_M, scale_factor=1.2), run_time=2.0)
        self.beat("If it never became ready, the rollout would stall right here. The three old Pods would keep serving.",
                  Wiggle(hold), run_time=1.6)
        self.beat("Kubernetes would not roll back on its own. It waits for you.", run_time=None)
        r0 = pod(NEW, NEW_X[0])
        self.beat("But this one passes. It is ready.",
                  ReplacementTransform(news[0], r0), FadeOut(nr), Transform(probe, M("ready", 22, GREEN_M).move_to(probe)),
                  Transform(cnt, counts(4, 4)), run_time=1.2)
        news[0] = r0

        # step 2
        self.beat("Only now may an old Pod go. The old ReplicaSet scales to two.",
                  Transform(cap, stepcap("2. old ReplicaSet scales to 2")), FadeOut(hold), FadeOut(probe),
                  setn(old, 2), FadeOut(olds[2], scale=0.5), Transform(cnt, counts(3, 3)), run_time=1.8)
        sw2 = wires([olds[0], olds[1], news[0]])
        self.beat("Look at the Service now. It sends requests to ready Pods of both versions. So the new version must work alongside the old one.",
                  Transform(sw, sw2), run_time=1.2)
        self.play(traffic(sw), run_time=1.4)

        # step 3
        news[1] = pod(NEW, NEW_X[1], ready=False)
        self.beat("Step three. The new ReplicaSet scales to two, and waits for that Pod to be ready.",
                  Transform(cap, stepcap("3. new ReplicaSet scales to 2")), setn(new, 2), Create(news[1]), Transform(cnt, counts(4, 3)), run_time=1.6)
        r1 = pod(NEW, NEW_X[1])
        self.play(ReplacementTransform(news[1], r1), Transform(cnt, counts(4, 4)), run_time=0.8)
        news[1] = r1

        # step 4
        news[2] = pod(NEW, NEW_X[2], ready=False)
        r2 = pod(NEW, NEW_X[2])
        self.beat("Step four. The old one scales to one.",
                  Transform(cap, stepcap("4. old to 1, new to 3, old to 0")), setn(old, 1), FadeOut(olds[1], scale=0.5),
                  Transform(cnt, counts(3, 3)), run_time=1.2)
        self.beat("The new one scales to three.",
                  setn(new, 3), Create(news[2]), Transform(cnt, counts(4, 3)), run_time=1.0)
        self.play(ReplacementTransform(news[2], r2), Transform(cnt, counts(4, 4)), run_time=0.7)
        news[2] = r2
        self.beat("And finally, the old one scales to zero.",
                  setn(old, 0), FadeOut(olds[0], scale=0.5), Transform(cnt, counts(3, 3)), Transform(sw, wires(news)), run_time=1.4)
        self.play(traffic(sw, NEW), run_time=1.2)
        self.beat("At no point were there fewer than three ready Pods. The price is room: one extra Pod at a time needs spare CPU and memory on some node.",
                  Indicate(cnt[1], color=YELLOW_M), FadeOut(cap), run_time=1.6)

        # the old ReplicaSet stays as a record
        rev1 = T("revision 1, kept at 0", 22, OLD).move_to(old_lab, aligned_edge=LEFT)
        rev2 = T("revision 2", 22, NEW).move_to(new_lab, aligned_edge=RIGHT)
        self.beat("The old ReplicaSet is not deleted. It stays, at zero, as a record of that version.",
                  old.animate.set_opacity(0.55), Transform(old_lab, rev1), Transform(new_lab, rev2), run_time=1.6)
        self.beat("That record is what makes rollback fast.", Indicate(old[2], color=OLD), run_time=1.0)

        # rollback
        undo = M("$ kubectl rollout undo deployment/hello-devops", 22).move_to([0, -3.45, 0])
        self.beat("Say version 1.1.0 has a bug. You run kubectl rollout undo.", Write(undo), run_time=1.6)
        back = M("image: hello-devops:1.0.0", 22, OLD).move_to(cl[3], aligned_edge=LEFT)
        self.beat("The undo copies the old template back into the Deployment.",
                  Transform(cl[3], back), run_time=1.2)
        cmp2 = DashedLine([cl[3].get_left()[0], crect.get_bottom()[1] - 0.04, 0], [cl[3].get_left()[0], old[0].get_top()[1] + 0.04, 0], dash_length=0.08, stroke_width=2, color=GREEN_M)
        ok = tick(True, 0.2).move_to(cmp2)
        self.beat("Now the template matches the old ReplicaSet, the one still waiting at zero.",
                  old.animate.set_opacity(1), Create(cmp2), Create(ok), run_time=1.6)
        bk = [pod(OLD, x) for x in OLD_X]
        line = "So the Deployment scales it back up, and the new one down, by the same rules, one ready Pod at a time."
        path, dur = voice(line)
        self._cue(line, dur)
        self.add_sound(path)
        t0 = self.renderer.time
        self.play(FadeOut(cmp2), FadeOut(ok), run_time=0.5)
        live = list(news)
        for i in range(3):
            wait_pod = pod(OLD, OLD_X[i], ready=False)
            self.play(setn(old, i + 1), Create(wait_pod), Transform(cnt, counts(4, 3)), run_time=0.5)
            live = [bk[i]] + live
            self.play(ReplacementTransform(wait_pod, bk[i]), Transform(cnt, counts(4, 4)), Transform(sw, wires(live)), run_time=0.45)
            live.remove(news[2 - i])
            self.play(setn(new, 2 - i), FadeOut(news[2 - i], scale=0.5), Transform(cnt, counts(3, 3)), Transform(sw, wires(live)), run_time=0.5)
        left = dur - (self.renderer.time - t0)
        if left > 0.02:
            self.wait(left)
        self.wait(0.25)
        self.play(traffic(sw, OLD), run_time=1.0)
        rev3 = T("revision 3", 22, OLD).move_to(old_lab, aligned_edge=LEFT)
        self.beat("The undo is itself a rollout. The old version comes back with a new number, revision 3.",
                  Transform(old_lab, rev3), new.animate.set_opacity(0.55), run_time=1.4)

        # recap
        recap = T("one ReplicaSet up, one down, each step waits for a ready Pod", 30, YELLOW_M).move_to([0, -3.45, 0])
        self.beat("A rolling update is two ReplicaSets trading Pods. One goes up, one goes down, inside maxSurge and maxUnavailable, and every step waits for a ready Pod.",
                  FadeOut(undo), FadeIn(recap, shift=UP * 0.15), Indicate(rules, color=YELLOW_M, scale_factor=1.03), run_time=2.6)
        self.wait(1.0)
