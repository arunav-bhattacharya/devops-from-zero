import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcapstone-check\.sh\b", "capstone check dot S H"), (r"\bArgo CD\b", "Argo C D"), (r"\bKyverno\b", "Kai-verno"),
            (r"\bPASS\b", "pass"), (r"\bFAIL\b", "fail"), (r"\bSKIP\b", "skip"), (r"\bkubectl\b", "cube control"),
            (r"\bhello-jvm\b", "hello J V M"), (r"\bport-forward\b", "port forward"), (r"\b8081\b", "eighty eighty-one")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


STAGES = ["Foundations", "Containers", "CI", "JVM build", "Infrastructure", "Kubernetes", "GitOps", "Metrics", "Dashboards",
          "Logs", "Traces", "Dynatrace (optional)", "Security", "AI and platform"]
COL = {"PASS": GREEN_M, "FAIL": RED_M, "SKIP": GOLD_M}


def res_line(status, text, size=20):
    s = M(status, size, COL[status])
    t = M(text, size, GREY_B)
    g = VGroup(s, t).arrange(RIGHT, buff=0.3)
    return g


class D68Capstone(VoiceScene):
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
        self.title_card("Done means the check passes", "acceptance checks for your capstone")

        # ---- 0. the path of stages
        rows = VGroup()
        for i, n in enumerate(STAGES):
            d = Circle(radius=0.09, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1)
            t = T(f"{i + 1}  {n}", 20, GREY_B)
            rows.add(VGroup(d, t).arrange(RIGHT, buff=0.18))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([-5.0, -0.05, 0]).align_to([-6.6, 0, 0], LEFT)
        spine = Line(rows[0][0].get_center(), rows[-1][0].get_center(), stroke_width=2, color=GREY_D)
        self.add(spine.set_opacity(0))
        lap = T("your laptop", 20, GREY_B).next_to(rows, UP, buff=0.12).align_to(rows, LEFT)
        users = T("users", 20, GREY_B).next_to(rows, DOWN, buff=0.12).align_to(rows, LEFT)
        self.beat("The capstone is one final project that uses every part of the course together. One small code change travels from your laptop to users.",
                  FadeIn(lap), spine.animate.set_opacity(1), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows], lag_ratio=0.12), Succession(Wait(5.0), FadeIn(users)), run_time=7.0)
        dot = Dot(radius=0.08, color=YELLOW_M).move_to(rows[0][0])
        self.beat("Fourteen stages, in order. And at every stage, you can prove that the change got there.",
                  Succession(FadeIn(dot, run_time=0.1), dot.animate(run_time=3.0, rate_func=linear).move_to(rows[-1][0]), FadeOut(dot, run_time=0.2)), run_time=3.6)

        # ---- 1. what done means
        q = T("When is a stage done?", 32, YELLOW_M).move_to([1.85, 2.6, 0])
        no = VGroup(tick(False, 0.2), T("when it looks fine", 28)).arrange(RIGHT, buff=0.3)
        yes = VGroup(tick(True, 0.22), T("when its acceptance check passes", 28)).arrange(RIGHT, buff=0.3)
        VGroup(no, yes).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([1.85, 1.0, 0])
        self.beat("So when is a stage done? Not when it looks fine. When its acceptance check passes.",
                  FadeIn(q, shift=DOWN * 0.1), Succession(Wait(1.6), FadeIn(no, shift=RIGHT * 0.1)), Succession(Wait(2.6), FadeIn(yes, shift=RIGHT * 0.1)), run_time=4.4)
        self.play(FadeOut(VGroup(no, yes)), run_time=0.4)

        # ---- 2. weak vs strong, for stage 7
        hl = SurroundingRectangle(rows[6], color=YELLOW_M, buff=0.07, corner_radius=0.06)
        weak_h = T("weak", 24, RED_M).move_to([-1.6, 1.55, 0])
        weak = T('"Argo CD works."', 26).next_to(weak_h, RIGHT, buff=0.4)
        self.beat("Take stage 7, GitOps. A weak check says: Argo CD works.",
                  Create(hl), Transform(q, T("Stage 7: two versions of a check", 30, YELLOW_M).move_to(q)), FadeIn(weak_h), FadeIn(weak), run_time=2.6)
        strong_h = T("strong", 24, GREEN_M).move_to([-1.6, 0.55, 0])
        strong = VGroup(T("after a merge, with no kubectl:", 22, GREY_B), M("kubectl -n argocd get application hello-devops", 20),
                        M("Synced  Healthy", 22, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        strong.next_to(strong_h, RIGHT, buff=0.4).align_to(strong_h, UP).shift(UP * 0.12)
        self.beat("A strong check says: after a merge, with no kubectl from you, this command reports Synced and Healthy.",
                  FadeIn(strong_h), LaggedStart(*[FadeIn(s_, shift=RIGHT * 0.1) for s_ in strong], lag_ratio=0.6), run_time=4.0)
        props = ["observable", "binary", "runnable"]
        means = ["looks at the running system", "PASS or FAIL, no judgment call", "one command, repeat it any time"]
        ptab = VGroup()
        for i, (p, m) in enumerate(zip(props, means)):
            y = -1.45 - 0.62 * i
            ptab.add(VGroup(T(p, 24, YELLOW_M).move_to([-1.6, y, 0], aligned_edge=LEFT), T(m, 22, GREY_B).move_to([0.75, y, 0], aligned_edge=LEFT)))
        self.steps("A good check has three properties. It is observable: it looks at the running system, not your memory. It is binary: anyone who runs it gets PASS or FAIL. And it is runnable: one command.",
                   (1.6, Wait(1.6)), (1.0, FadeIn(ptab[0][0]), FadeIn(ptab[0][1])), (2.0, Wait(2.0)),
                   (1.0, FadeIn(ptab[1][0]), FadeIn(ptab[1][1])), (2.0, Wait(2.0)), (1.0, FadeIn(ptab[2][0]), FadeIn(ptab[2][1])))
        wx = tick(False, 0.18).next_to(weak, RIGHT, buff=0.3)
        self.beat("The weak version cannot clearly fail. So passing it tells you nothing.",
                  Create(wx), weak.animate.set_color(GREY_D), run_time=1.8)
        self.play(FadeOut(VGroup(weak_h, weak, wx, strong_h, strong, ptab)), FadeOut(hl), run_time=0.5)

        # ---- 3. the pattern: an if that prints PASS or FAIL
        code = VGroup(M('got=$(curl -s localhost:8000/ | jq -r .version)', 20, GREY_B),
                      M('if [[ "$got" == "1.2.0" ]]', 20),
                      M('then echo "PASS  app reports 1.2.0"', 20, GREEN_M),
                      M("else echo \"FAIL  app reports '$got'\"", 20, RED_M),
                      M("fi", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        code.move_to([1.85, 0.6, 0])
        for i in (2, 3):
            code[i].shift(RIGHT * 0.3)
        self.beat("Here is the pattern. Ask the running app for its version. If it says 1.2.0, print PASS. Otherwise, print FAIL.",
                  Transform(q, T("one check = one if", 30, YELLOW_M).move_to(q)), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in code], lag_ratio=0.4), run_time=5.0)
        res = res_line("PASS", "app reports 1.2.0", 24).move_to([1.85, -1.6, 0])
        self.beat("Every line of the lab's capstone-check.sh follows this pattern.",
                  FadeIn(res, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(code, res)), run_time=0.5)

        # ---- 4. the whole script, early: a to-do list
        term = RoundedRectangle(corner_radius=0.15, width=9.0, height=4.3, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1).move_to([1.95, 0.15, 0])
        cmd = M("$ security/capstone-check.sh", 22, YELLOW_M).next_to(term.get_corner(UL), DR, buff=0.25)
        L = [("FAIL", "Deployment hello-devops is not ready"), ("PASS", "App reports version 1.2.0"), ("FAIL", "Argo CD Application not found"),
             ("SKIP", "cosign not installed"), ("FAIL", "Prometheus has no hello_requests_total"), ("FAIL", "Jaeger has no services yet")]
        lines = VGroup(*[res_line(s_, t) for s_, t in L]).arrange(DOWN, aligned_edge=LEFT, buff=0.16).next_to(cmd, DOWN, buff=0.3).align_to(cmd, LEFT)
        dots = M("...", 20, GREY_B).next_to(lines, DOWN, buff=0.12).align_to(lines, LEFT)
        summ = M("1 passed, 8 failed, 2 skipped", 22).next_to(dots, DOWN, buff=0.2).align_to(lines, LEFT)
        self.beat("The script turns 11 of the 14 stages into checks like that. Each line prints PASS, FAIL or SKIP. SKIP means a tool or an address is missing.",
                  FadeOut(q), Create(term), Write(cmd), Succession(Wait(2.6), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in lines], lag_ratio=0.3)), run_time=6.8)
        ex1 = T("exits with 1 if anything failed", 20, GREY_B).next_to(summ, RIGHT, buff=0.4)
        self.beat("It ends with a count, and exits with 1 if anything failed. So the same file could run in CI later.",
                  FadeIn(dots), FadeIn(summ), Succession(Wait(2.0), FadeIn(ex1)), run_time=3.6)
        self.beat("Run it early, and almost everything fails. That is normal. Read the output as your to-do list, in order.",
                  LaggedStart(*[Indicate(lines[i][0], color=RED_M) for i in (0, 2, 4, 5)], lag_ratio=0.3), run_time=3.2)

        # ---- 5. work down the list
        def mark(i, c):
            return rows[i][0].animate.set_fill(c, 1).set_stroke(c)

        def flip(i, status, text):
            return Transform(lines[i], res_line(status, text).move_to(lines[i], aligned_edge=LEFT))

        commit = chip("git commit", TEAL_M, 20, mono=True).move_to([4.9, -2.75, 0])
        self.steps("Finish a stage, and run the script again. When its line turns green, commit. Now you can always go back to the last green point.",
                   (1.0, mark(5, GREEN_M), Indicate(rows[5], color=GREEN_M)), (1.2, Wait(1.2)),
                   (0.8, flip(0, "PASS", "Deployment hello-devops is rolled out")), (1.6, Wait(1.6)), (0.6, FadeIn(commit, shift=UP * 0.1)))
        self.steps("Then the next stage. GitOps passes, and you commit again.",
                   (0.8, mark(6, GREEN_M)), (0.8, flip(2, "PASS", "Argo CD: Synced/Healthy")), (0.8, Indicate(commit, color=TEAL_M)))

        # ---- 6. a new stage breaks an old line
        self.play(FadeOut(VGroup(dots, summ, ex1)), run_time=0.4)
        pf = chip("new port-forward grabs port 8081", GOLD_M, 22).move_to([1.95, -2.75, 0])
        pf.align_to(term, LEFT)
        self.beat("Now you start the next stage. Along the way, a new port-forward grabs port 8081, where the app used to answer.",
                  mark(7, YELLOW_M), Succession(Wait(2.6), FadeIn(pf, shift=UP * 0.1)), run_time=4.6)
        self.beat("You were working on metrics. But the line that turns red is an old one: the app check, from a stage you finished long ago.",
                  Succession(Wait(2.4), AnimationGroup(flip(1, "FAIL", "App at localhost:8081: no answer"), mark(5, RED_M))), run_time=5.4)
        ar = VGroup(SurroundingRectangle(lines[1], color=GOLD_M, buff=0.08, corner_radius=0.06), SurroundingRectangle(pf, color=GOLD_M, buff=0.08, corner_radius=0.1))
        self.beat("That old red line points you straight at the cause. You fix the port, and it turns green again.",
                  Create(ar), Succession(Wait(3.0), AnimationGroup(flip(1, "PASS", "App reports version 1.2.0"), mark(5, GREEN_M), FadeOut(pf), FadeOut(ar))), run_time=5.0)
        rule = T("run it after every stage, and read every line", 24, YELLOW_M).move_to([1.95, -2.75, 0])
        self.beat("So run it after every stage, and read every line, not only the newest one. You run the whole test suite for the same reason, not only the newest test.",
                  FadeIn(rule, shift=UP * 0.1), run_time=2.0)

        # ---- 7. why not test at the end
        self.play(FadeOut(rule), FadeOut(commit), run_time=0.4)
        late = T("test only at the end: five broken things at once", 24, RED_M).move_to([1.95, -2.75, 0])
        self.steps("Compare the other way. Build all fourteen stages first, and test at the end. Now five things are broken at once, and you cannot tell which one causes the others.",
                   (3.0, Wait(3.0)), (1.2, LaggedStart(*[flip(i, "FAIL", L[i][1] if i != 0 else "Deployment hello-devops is not ready") for i in (0, 1, 2)], lag_ratio=0.3),
                                      *[mark(i, RED_M) for i in (5, 6, 7)], FadeIn(late, shift=UP * 0.1)))
        self.play(*[flip(i, "PASS", t) for i, t in ((0, "Deployment hello-devops is rolled out"), (1, "App reports version 1.2.0"), (2, "Argo CD: Synced/Healthy"))],
                  mark(5, GREEN_M), mark(6, GREEN_M), mark(7, GREY_B), FadeOut(late), run_time=0.8)

        # ---- 8. recap
        rc = T("one stage, one green check, one commit", 28, GREEN_M).move_to([1.95, -2.75, 0])
        self.beat("One stage at a time. A stage is done when its check passes. Run all the checks after every stage, and commit at each green point.",
                  FadeIn(rc, shift=UP * 0.15), run_time=2.4)
        self.wait(1.0)
