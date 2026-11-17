import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"!cancelled\(\)", "not cancelled"), (r"success\(\)", "success"), (r"failure\(\)", "failure"), (r"cancelled\(\)", "cancelled"), (r"always\(\)", "always"), (r"\bpytest\b", "pie test"), (r"refs/heads/main", "refs heads main"),
            (r"\bbreak-build\b", "break build")])


def fix_indent(g, size):
    """Text drops leading spaces when lines are left-aligned; shift each line by its indent."""
    cw = M("x" * 20, size).width / 20
    for m in g:
        s = getattr(m, "original_text", "")
        m.shift(RIGHT * (len(s) - len(s.lstrip(" "))) * cw)
    return g


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def step_row(name, cond, y, color=WHITE, w=9.6):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=0.8, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.06), 1)
    r.move_to([-0.6, y, 0])
    n = T(name, 26).move_to(r.get_left() + RIGHT * 0.3, aligned_edge=LEFT)
    c = M(cond, 22, BLUE_M).next_to(n, RIGHT, buff=0.5) if cond else VMobject()
    return VGroup(r, n, c)


class D26HiddenSuccess(VoiceScene):
    def construct(self):
        self.title_card("The rule nobody wrote down", "every if gets a hidden success()")

        # ---- 1. the question
        c0 = M("if: github.ref == 'refs/heads/main'", 30, BLUE_M).move_to([0, 1.2, 0])
        self.beat("Here's a step condition: run only on the main branch.", Write(c0), run_time=1.6)
        on = T("the run is on main", 28, GREEN_M).move_to([0, 0.0, 0])
        q = T("so the step runs... right?", 30, YELLOW_M).move_to([0, -1.2, 0])
        self.beat("The run is on main. So the condition is true, and the step runs. Right? Not always. And the reason is a rule nobody wrote down.",
                  FadeIn(on), Succession(Wait(1.4), FadeIn(q)), run_time=3.0)
        self.play(FadeOut(VGroup(c0, on, q)), run_time=0.6)

        # ---- 2. the kitchen note
        note = RoundedRectangle(corner_radius=0.08, width=5.6, height=1.5, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.1), 1).move_to([0, 2.2, 0])
        nt = VGroup(T("On Saturdays,", 30), T("the last cook mops the floor.", 30)).arrange(DOWN, buff=0.1).move_to(note)
        self.beat("Picture the closing routine in our kitchen. A note on the wall says: on Saturdays, the last cook mops the floor.",
                  FadeIn(note), Write(nt), run_time=2.4)
        tlx = Line([-5.6, -0.4, 0], [5.6, -0.4, 0], stroke_width=3, color=GREY_B)
        hours = VGroup(*[T(h, 24, GREY_B).next_to([x, -0.4, 0], DOWN, buff=0.2) for h, x in [("6 pm", -5.0), ("9 pm", -1.0), ("close", 4.6)]])
        self.beat("It's Saturday. The evening runs along.", Create(tlx), FadeIn(hours), run_time=1.4)
        oil = T("oil tips over", 28, RED_M).move_to([-1.0, 0.45, 0])
        xo = tick(False, 0.24).next_to([-1.0, -0.4, 0], UP, buff=0.0).shift(UP * 0.0)
        xo.move_to([-1.0, -0.4, 0])
        self.beat("At nine o'clock, a pot of oil tips over.", FadeIn(oil, shift=DOWN * 0.1), Create(xo), run_time=1.2)
        stop = Line([-0.9, -0.4, 0], [5.6, -0.4, 0], stroke_width=6, color=GREY_D)
        hr = T("house rule: everyone stops at the first problem", 26, GREY_B).move_to([2.0, -1.9, 0])
        self.beat("The house rule says everyone stops at the first problem. So the evening ends early, and nobody mops.",
                  Create(stop), FadeIn(hr), run_time=1.8)
        mop = T("not mopped", 26, RED_M).move_to([4.6, 0.45, 0])
        self.beat("It was the one night the floor really needed it.", FadeIn(mop), run_time=1.2)
        tru = T("Saturday: true", 26, GREEN_M).next_to(note, RIGHT, buff=0.3)
        self.beat("The note was clear. Its condition was true: it was Saturday.", FadeIn(tru), run_time=1.6)
        hid = T("...and only if everything has gone well so far", 28, YELLOW_M).move_to([0, -3.1, 0])
        self.beat("What nobody read was the unwritten rule underneath. And only if everything has gone well so far.",
                  FadeIn(hid, shift=UP * 0.1), run_time=2.0)
        self.beat("Workflow conditions carry the same invisible rule, written, if you like, in invisible ink.", Indicate(hid, color=YELLOW_M), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. the same thing in a job
        hdr = T("one job, steps in order", 28, GREY_B).move_to([-0.6, 3.1, 0])
        s1 = step_row("check out the code", "", 2.0)
        s2 = step_row("run the tests", "", 0.9)
        s3 = step_row("upload the report", "if: github.ref == 'refs/heads/main'", -0.2)
        self.beat("Now the same story in a job. A job is a list of steps that run in order on one machine.",
                  FadeIn(hdr), FadeIn(s1), FadeIn(s2), run_time=1.6)
        self.beat("The third step has our note: upload the report, but only on main.", FadeIn(s3), run_time=1.6)
        k1 = tick(True, 0.2).move_to(s1[0].get_right() + RIGHT * 0.45)
        k2 = tick(False, 0.18).move_to(s2[0].get_right() + RIGHT * 0.45)
        self.beat("The run is on main. Checkout passes. Then a test fails. That's the oil.",
                  Create(k1), Succession(Wait(1.0), AnimationGroup(Create(k2), s2[0].animate.set_stroke(RED_M))), run_time=2.4)
        q2 = T("does the upload step run?", 30, YELLOW_M).move_to([-0.6, -1.6, 0])
        self.beat("The condition is true. Pause and guess: does the upload step run?", FadeIn(q2), run_time=1.4)
        self.wait(2.0)
        sk = T("skipped", 26, GREY_B).move_to(s3[0].get_right() + RIGHT * 0.75)
        self.beat("No. It's skipped. Exactly like the mop.", FadeOut(q2), s3.animate.set_opacity(0.45), FadeIn(sk), run_time=1.4)

        # reveal the hidden success()
        s3.set_opacity(1)
        real = M("if: success() && github.ref == 'refs/heads/main'", 22, BLUE_M).move_to(s3[2], aligned_edge=LEFT)
        self.beat("Here's why. Every if that doesn't mention a status function gets an invisible success() added to the front.",
                  Transform(s3[2], real), run_time=2.0)
        box_s = SurroundingRectangle(s3[2][3:12], color=YELLOW_M, buff=0.06)
        sq = T("success(): did everything before this succeed?", 26, YELLOW_M).move_to([-0.6, -1.6, 0])
        self.beat("success() asks one question: did everything before this succeed? After the failed test, the answer is no. So the whole condition is false.",
                  Create(box_s), FadeIn(sq), run_time=2.4)
        nf = T("a step with no if at all gets the same success()", 26, GREY_B).move_to([-0.6, -2.5, 0])
        self.beat("A step with no if at all behaves the same way. That's how a job stops at its first failure. Every later step asks, so far, so good? And hears no.",
                  FadeIn(nf), run_time=2.4)
        self.beat("Honestly, success() could have been named so far so good. That's all it means.", Indicate(box_s, color=YELLOW_M), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. name the four status functions
        ht = T("four status functions", 32).move_to([0, 3.0, 0])
        rows = [("success()", "everything before succeeded (the default)", GREEN_M),
                ("failure()", "something before failed", RED_M),
                ("cancelled()", "the run was cancelled", GREY_B),
                ("always()", "true no matter what, even during a cancel", GOLD_M)]
        self.beat("Now that you've met one, here's the family. They're called status functions: questions about what happened earlier in the run.",
                  FadeIn(ht), run_time=1.6)
        grp = VGroup()
        says = ["success(): everything before succeeded. That's the default.",
                "failure(): something before failed.",
                "cancelled(): the run was cancelled.",
                "And always(): true no matter what, even while the run is being cancelled."]
        for i, ((f, d, c), s) in enumerate(zip(rows, says)):
            y = 1.7 - i * 1.05
            fm = M(f, 28, c).move_to([-4.0, y, 0])
            dm = T(d, 26).move_to([-2.2, y, 0], aligned_edge=LEFT)
            grp.add(VGroup(fm, dm))
            self.beat(s, FadeIn(fm, shift=RIGHT * 0.1), FadeIn(dm), run_time=1.2)
        rule = T("Want something else? Write the status function yourself.", 28, YELLOW_M).move_to([0, -2.8, 0])
        self.beat("So when you mean something other than so far so good, you say so, by writing the status function yourself.",
                  FadeIn(rule), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. fix the step
        s1 = step_row("check out the code", "", 2.0)
        s2 = step_row("run the tests", "", 0.9, RED_M)
        s3 = step_row("upload the report", "if: ${{ !cancelled() }}", -0.2)
        k1 = tick(True, 0.2).move_to(s1[0].get_right() + RIGHT * 0.45)
        k2 = tick(False, 0.18).move_to(s2[0].get_right() + RIGHT * 0.45)
        self.beat("Back to the report. A test report is most useful exactly when a test failed. So write !cancelled(): run whatever happened, unless someone cancelled the run.",
                  FadeIn(VGroup(s1, s2, s3, k1, k2)), run_time=2.4)
        k3 = tick(True, 0.2).move_to(s3[0].get_right() + RIGHT * 0.45)
        cb = T("the Day 25 upload step uses exactly this", 26, GREY_B).move_to([-0.6, -1.5, 0])
        self.beat("Now the upload runs after the failed test. That's the condition the Day 25 pipeline put on its upload step.",
                  Create(k3), FadeIn(cb), run_time=1.8)
        sm = M("if: ${{ failure() && steps.smoke.outcome == 'failure' }}", 22, BLUE_M).move_to([-0.6, -2.6, 0])
        self.beat("And to run only when one particular step failed, combine them: failure(), and that step's outcome is failure.",
                  FadeIn(sm), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. the same rule between jobs: a report with always()
        jv = box("version", TEAL_M, w=2.4).move_to([-4.6, 0.8, 0])
        jb = box("build", PURPLE_M, w=2.4).move_to([-0.6, 0.8, 0])
        jr = box("report", GOLD_M, w=2.4).move_to([3.6, 0.8, 0])
        a1, a2 = edge_arrow(jv, jb), edge_arrow(jb, jr)
        a3 = CurvedArrow(jv.get_top() + UP * 0.05, jr.get_top() + UP * 0.05, angle=-0.6, color=GREY_B, stroke_width=3)
        nl = M("needs", 22, GREY_B).next_to(a1, UP, buff=0.1)
        self.beat("The same rule works between jobs. In the lesson's practice workflow, build needs version, and report needs both.",
                  LaggedStart(FadeIn(jv), GrowArrow(a1), FadeIn(jb), GrowArrow(a2), FadeIn(jr), Create(a3), lag_ratio=0.25), FadeIn(nl), run_time=2.4)
        al = M("if: always()", 24, GOLD_M).next_to(jr, DOWN, buff=0.25)
        self.beat("The report job only reads and prints the other jobs' results, so it carries if: always().",
                  FadeIn(al), run_time=1.6)
        bb = M("--input break-build=true", 24, RED_M).move_to([-0.6, -1.0, 0])
        self.beat("Now tick the box that breaks the build on purpose.", FadeIn(bb), run_time=1.0)
        xb = tick(False, 0.2).next_to(jb, DOWN, buff=0.25)
        kv = tick(True, 0.2).next_to(jv, DOWN, buff=0.25)
        out = VGroup(M("Job results were [", 22), M('  "success",', 22, GREEN_M), M('  "failure"', 22, RED_M), M("]", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        fix_indent(out, 22)
        out.move_to([3.6, -1.75, 0])
        self.beat("Version passes. Build exits with 1. And report still runs, thanks to always(), and prints what it saw: one success, one failure.",
                  Create(kv), Succession(Wait(0.8), AnimationGroup(Create(xb), jb[0].animate.set_stroke(RED_M))),
                  FadeOut(al), Succession(Wait(2.2), FadeIn(out, shift=UP * 0.1)), run_time=3.6)
        self.beat("Without always(), report would have been skipped, quietly, and the one job that tells you what went wrong would say nothing.",
                  Indicate(jr[1], color=GOLD_M), run_time=2.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. guardrails
        gt = T("Should every step say always()?", 34).move_to([0, 2.9, 0])
        self.beat("So should we sprinkle always() everywhere, to be safe? Please don't.", FadeIn(gt), run_time=1.6)
        g1 = chip("always() also runs while the run is being cancelled", GOLD_M, 26).move_to([0, 1.5, 0])
        g2 = chip("a stuck always() step hangs until the timeout", RED_M, 26).move_to([0, 0.4, 0])
        g3 = chip("to run whatever happened, prefer !cancelled()", GREEN_M, 26).move_to([0, -0.7, 0])
        g4 = chip("always() fits small jobs that only report", TEAL_M, 26).move_to([0, -1.8, 0])
        self.beat("An always() step also runs while the run is being cancelled. If it gets stuck, it hangs until the timeout. GitHub's docs warn against it on important steps.",
                  FadeIn(g1, shift=UP * 0.1), Succession(Wait(1.6), FadeIn(g2, shift=UP * 0.1)), run_time=3.0)
        self.beat("To run whatever happened, prefer !cancelled(). Keep always() for small jobs that only report, like ours.",
                  FadeIn(g3, shift=UP * 0.1), Succession(Wait(1.4), FadeIn(g4, shift=UP * 0.1)), run_time=2.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 8. moral and quick check
        mo = VGroup(T("Every if gets a hidden success().", 32),
                    T("When you mean something else, write the status function yourself.", 28, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        self.beat("So here's the moral. Every if gets a hidden success(). When you mean something else, write the status function yourself.",
                  FadeIn(mo[0]), Succession(Wait(2.0), FadeIn(mo[1])), run_time=3.6)
        self.beat("And the floor gets mopped, whatever happened at nine.", run_time=None)
        qc = VGroup(T("Quick check", 28, GOLD_M), M("if: ${{ failure() }}", 26, BLUE_M),
                    T("An earlier step failed. Does this step run?", 26)).arrange(DOWN, buff=0.25).move_to([0, -1.2, 0])
        self.beat("Quick check. A step says if: failure(). An earlier step in the job failed. Does it run? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("Yes: it names a status function, so no hidden success() is added.", 26, GREEN_M).move_to(qc[2])
        self.beat("Yes. It names a status function, so no hidden success() is added, and failure() is true.",
                  Transform(qc[2], ans), run_time=1.4)
        self.wait(1.2)
