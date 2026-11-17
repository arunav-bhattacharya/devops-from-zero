import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\blogsum\.py\b", "log sum dot pie"), (r"\blogsum\b", "log sum"), (r"\bjq\b", "J Q"),
            (r"\bnope\.log\b", "nope dot log"), (r"\baccess\.log\b", "access dot log"), (r"\bsubprocess\.run\b", "sub process dot run"),
            (r"\bcheck=True\b", "check equals true"), (r"\bCalledProcessError\b", "called process error"),
            (r"\bFileNotFoundError\b", "file not found error"), (r"\buv\b", "U V")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color=WHITE, s=1.0):
    head = Circle(radius=0.28, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), opacity=1)
    body = RoundedRectangle(corner_radius=0.35, width=0.95, height=0.85, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), opacity=1)
    body.next_to(head, DOWN, buff=0.08)
    return VGroup(head, body).scale(s)


def paper(color, w=1.5, h=1.1, lines=3):
    r = RoundedRectangle(corner_radius=0.06, width=w, height=h, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.12), opacity=1)
    ls = VGroup(*[Line(LEFT * (w / 2 - 0.22), RIGHT * (w / 2 - 0.22), stroke_width=2, color=color).set_opacity(0.6) for _ in range(lines)])
    ls.arrange(DOWN, buff=h / (lines + 1.4)).move_to(r)
    return VGroup(r, ls)


class D15HelperReport(VoiceScene):
    def steps(self, text, *plays):
        """Speak one line and run several animations in order inside it."""
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
        self.title_card("Done, or failed?", "how a script reports back, so people and machines can trust it")

        # 1. the shop helper and the checklist
        helper = person(WHITE).move_to([-1.6, 0.4, 0])
        hl = T("helper", 26, GREY_B).next_to(helper, DOWN, buff=0.25)
        cl = VGroup(T("1. open the stock room", 26), T("2. count visitors in the door book", 26),
                    T("3. leave a note: done or failed", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        cl_r = RoundedRectangle(corner_radius=0.1, width=cl.width + 0.6, height=cl.height + 0.6, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.1), opacity=1)
        checklist = VGroup(cl_r, cl.move_to(cl_r)).move_to([3.0, 0.4, 0])
        cll = T("checklist", 26, BLUE_M).next_to(checklist, UP, buff=0.25)
        self.beat("Picture leaving a helper in charge of your shop for the morning. You hand over a written checklist.",
                  FadeIn(helper, shift=UP * 0.2), FadeIn(hl), Create(cl_r), FadeIn(cll), run_time=2.0)
        self.steps("Open the stock room. Count yesterday's visitors in the door book. Then leave a note that says done or failed.",
                   (0.8, Write(cl[0])), (1.4, Write(cl[1])), (1.4, Write(cl[2])))
        note = VGroup(RoundedRectangle(corner_radius=0.06, width=1.5, height=0.8, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.2), opacity=1),
                      T("done", 30, GREEN_M)).move_to([-1.6, -2.4, 0])
        note[1].move_to(note[0])
        self.beat("At lunch, the note says done.", FadeIn(note, shift=UP * 0.2), FadeOut(hl), run_time=1.0)
        x1 = tick(False, 0.3).next_to(cl[0], LEFT, buff=0.15)
        self.beat("Later you learn the stock room key never turned. The helper just moved on.",
                  Create(x1), cl[0].animate.set_color(RED_M), run_time=1.4)
        q = T("when a script ends, how does anyone know it worked?", 30, YELLOW_M).move_to([0, 3.1, 0])
        self.beat("Nobody lied. The checklist never said what to do when a step fails. So here is the question for today. When a script ends, how does anyone know whether it really worked?",
                  Wiggle(note), Succession(Wait(3.0), FadeIn(q, shift=DOWN * 0.15)), run_time=5.0)
        self.play(FadeOut(VGroup(checklist, cll, x1, note, q)), helper.animate.move_to([-2.0, 0.3, 0]), run_time=0.8)

        # 2. map the shop onto a script
        hl2 = M("logsum.py", 24).next_to(helper, DOWN, buff=0.25)
        self.beat("A script is that helper. It is a file of instructions the computer follows in order. Ours is logsum, a small Python script from the lab.",
                  FadeIn(hl2, shift=UP * 0.1), run_time=1.6)
        book = paper(GOLD_M, 1.3, 1.6, 5).move_to([-5.3, 0.3, 0])
        bl = VGroup(T("door book", 26, GOLD_M), M("access.log", 22, GOLD_M)).arrange(DOWN, buff=0.12).next_to(book, DOWN, buff=0.25)
        ba = Arrow(book.get_right(), helper.get_left(), buff=0.2, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("Its door book is a web server's access log. One line for every visit, or request.",
                  FadeIn(book, shift=RIGHT * 0.2), FadeIn(bl), GrowArrow(ba), run_time=1.8)

        X = 2.0
        sheet = paper(WHITE, 2.0, 1.1, 3).move_to([X, 2.1, 0])
        sticky = paper(RED_M, 1.1, 0.75, 2).move_to([X, 0.3, 0])
        thumb = VGroup(Circle(radius=0.42, stroke_color=YELLOW_M, stroke_width=3).set_fill(tint(YELLOW_M, 0.12), opacity=1)).move_to([X, -1.45, 0])
        lab_s = VGroup(T("report sheet", 26), M("stdout", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(sheet, RIGHT, buff=0.35)
        lab_e = VGroup(T("note for the manager", 26, RED_M), M("stderr", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(sticky, RIGHT, buff=0.5)
        lab_x = VGroup(T("thumbs up or down", 26, YELLOW_M), M("exit code", 22, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(thumb, RIGHT, buff=0.5)
        lab_e.align_to(lab_s, LEFT); lab_x.align_to(lab_s, LEFT)
        hr = helper.get_right() + RIGHT * 0.15
        oa = VGroup(*[Arrow(hr, o.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1) for o in (sheet, sticky, thumb)])
        self.beat("When it finishes, it reports back on three separate channels.",
                  LaggedStart(*[GrowArrow(a) for a in oa], lag_ratio=0.3), run_time=1.6)
        self.beat("The report sheet is standard output, or stdout. The real results go there.",
                  FadeIn(sheet, shift=RIGHT * 0.15), FadeIn(lab_s), run_time=1.6)
        self.beat("The note for the manager is standard error, or stderr. That is for messages meant for people: warnings, and the reason something failed.",
                  FadeIn(sticky, shift=RIGHT * 0.15), FadeIn(lab_e), run_time=1.8)
        num = M("?", 34, YELLOW_M).move_to(thumb)
        self.beat("And the thumbs up or down at the end is the exit code. One number. Zero means success. Any other number means some kind of failure.",
                  FadeIn(thumb, shift=RIGHT * 0.15), FadeIn(num), FadeIn(lab_x), run_time=1.8)

        # 3. CI reads only the number
        ci = box("CI", GREY_B, w=1.5, h=0.8, size=28).move_to([5.6, -2.9, 0])
        cia = Arrow(thumb.get_bottom(), ci.get_left(), buff=0.12, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.15)
        cia = CurvedArrow(thumb.get_bottom() + DOWN * 0.08, ci.get_left() + LEFT * 0.1, angle=PI / 3, color=YELLOW_M, stroke_width=3)
        self.beat("Now meet the most important reader of all. CI, the robot that runs your script every time someone changes the code.",
                  FadeIn(ci, shift=UP * 0.15), run_time=1.4)
        self.steps("It does not read the report. It does not read the note. It looks at one number, and decides.",
                   (0.6, sheet.animate.set_opacity(0.3), lab_s.animate.set_opacity(0.3)), (0.9, Wait(0.9)),
                   (0.6, sticky.animate.set_opacity(0.3), lab_e.animate.set_opacity(0.3)), (0.6, Wait(0.6)), (1.0, Create(cia)))
        self.beat("A very busy manager. It only ever looks at the thumb. So if that number is wrong, nothing else you printed matters.",
                  Indicate(num, color=YELLOW_M, scale_factor=1.4), run_time=1.4)
        self.play(sheet.animate.set_opacity(1), lab_s.animate.set_opacity(1), sticky.animate.set_opacity(1), lab_e.animate.set_opacity(1), run_time=0.5)

        # 4. predict, then run
        cmd = M("$ uv run scripts/logsum.py access access.log", 24, GREY_B).move_to([0, 3.35, 0])
        self.beat("Let's run it on the lab's log. uv is the tool that runs our Python scripts.",
                  FadeIn(cmd, shift=DOWN * 0.1), run_time=1.4)
        rq_t, er_t = ValueTracker(0), ValueTracker(0)
        anchor1, anchor2 = np.array([-4.4, -2.3, 0]), np.array([-4.4, -2.85, 0])
        rq = always_redraw(lambda: M(f"{rq_t.get_value():.0f}", 30, GOLD_M).move_to(anchor1, aligned_edge=RIGHT))
        er = always_redraw(lambda: M(f"{er_t.get_value():.0f}", 30, RED_M).move_to(anchor2, aligned_edge=RIGHT))
        l1 = T("requests", 26, GOLD_M).next_to(anchor1, RIGHT, buff=0.2)
        l2 = T("server errors", 26, RED_M).next_to(anchor2, RIGHT, buff=0.2)
        counts = VGroup(rq, er, l1, l2)
        pc = M("4.6%", 30, RED_M).next_to(l2, RIGHT, buff=0.4)
        self.steps("The helper reads 238 requests. 11 of them were server errors. That is 4.6 percent.",
                   (0.3, FadeIn(counts)), (1.6, rq_t.animate.set_value(238), travel(ba, GOLD_M, 1.4)),
                   (1.2, er_t.animate.set_value(11)), (0.6, FadeIn(pc)))
        limit = M("limit 1.0%", 26, YELLOW_M).next_to(pc, UP, buff=0.25).align_to(pc, LEFT)
        self.beat("The limit is 1 percent unless you say otherwise. So what exit code should it hand back? Pause and guess.",
                  FadeIn(limit, shift=DOWN * 0.1), run_time=1.2)
        self.wait(2.0)
        one = M("1", 34, RED_M).move_to(thumb)
        self.steps("One. The check found a problem, and CI turns red.",
                   (0.6, travel(oa[2], YELLOW_M, 0.6)), (0.5, Transform(num, one)), (0.8, ci[0].animate.set_stroke(RED_M), travel(cia, YELLOW_M, 0.8)))
        rep = VGroup(M("238 requests", 20), M("5xx 11", 20), M("4.6%", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to(sheet)
        why = VGroup(M("ERROR error rate 4.6%", 20, RED_M), M("above the limit of 1.0%", 20, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(lab_e, DOWN, buff=0.25).align_to(lab_e, LEFT)
        self.steps("The report went to stdout. And the one-line reason went to stderr: the error rate, 4.6 percent, is above the limit of 1.0 percent.",
                   (0.6, travel(oa[0], WHITE, 0.6)), (0.6, FadeOut(sheet[1]), FadeIn(rep)), (1.2, Wait(1.2)),
                   (0.6, travel(oa[1], RED_M, 0.6)), (0.8, FadeIn(why, shift=UP * 0.1)))
        cmd5 = M("$ uv run scripts/logsum.py access access.log --max-error-rate 5", 24, GREY_B).move_to(cmd)
        fit(cmd5, 12.6)
        zero = M("0", 34, GREEN_M).move_to(thumb)
        self.steps("Raise the limit to 5 percent with a flag, and the same log passes. Exit code zero. CI goes green.",
                   (0.8, Transform(cmd, cmd5), Transform(limit, M("limit 5%", 26, YELLOW_M).move_to(limit, aligned_edge=LEFT)), FadeOut(why)),
                   (1.4, Wait(1.4)), (0.6, travel(oa[2], YELLOW_M, 0.6)), (0.5, Transform(num, zero)), (0.6, ci[0].animate.set_stroke(GREEN_M)))
        rq.clear_updaters(); er.clear_updaters()
        self.play(FadeOut(VGroup(counts, pc, limit)), run_time=0.5)

        # 5. why keep the channels apart: a program reads the report
        jq = mbox("jq", GREEN_M, size=26, w=1.2, h=0.7).move_to([5.6, 2.0, 0])
        lab_s2 = lab_s.copy()
        self.play(lab_s.animate.next_to(sheet, DOWN, buff=0.15), run_time=0.5)
        ja = Arrow(sheet.get_right(), jq.get_left(), buff=0.15, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.12)
        cmdj = M("$ uv run scripts/logsum.py access access.log --format json | jq", 24, GREY_B).move_to(cmd)
        fit(cmdj, 12.6)
        self.beat("Why keep the report and the note apart? Because the report is often read by another program. Here, jq, a small tool that picks values out of JSON.",
                  Transform(cmd, cmdj), FadeIn(jq), GrowArrow(ja), run_time=2.0)
        js = M('{"error_rate": 4.62, ...}', 20, GREEN_M).move_to([3.3, 1.5, 0], aligned_edge=LEFT)
        val = M("4.62", 26, GREEN_M).next_to(jq, UP, buff=0.2)
        self.steps("JSON is a plain text format that programs use to swap data. With format json, stdout holds only JSON. So jq reads it cleanly, and finds the error rate: 4.62.",
                   (0.6, FadeOut(rep), FadeIn(js)), (2.6, Wait(2.6)), (0.8, travel(ja, GREEN_M, 0.8)), (0.6, FadeIn(val, shift=DOWN * 0.1)))
        bad = M("starting...", 20, RED_M).move_to(js, aligned_edge=LEFT)
        self.steps("Now say the helper uses print for a cheerful starting message. print writes to stdout. So the first line jq sees is: starting dot dot dot.",
                   (2.4, Wait(2.4)), (0.8, FadeIn(bad, shift=DOWN * 0.1), js.animate.shift(DOWN * 0.32)), (0.8, travel(ja, RED_M, 0.8)))
        jx = tick(False, 0.3).next_to(jq, UP, buff=0.2)
        self.beat("And jq fails. One friendly hello broke the whole report.",
                  FadeOut(val), Create(jx), jq[0].animate.set_stroke(RED_M), run_time=1.2)
        self.steps("So the rule is simple. Messages for people go to stderr. The report stays alone on stdout.",
                   (0.8, bad.animate.move_to(why.get_left() + RIGHT * bad.width / 2)), (0.6, FadeOut(jx), jq[0].animate.set_stroke(GREEN_M), js.animate.shift(UP * 0.32)), (0.8, travel(ja, GREEN_M, 0.8), FadeIn(val)))
        self.play(FadeOut(VGroup(jq, ja, val, bad, js)), FadeIn(sheet[1]), FadeIn(lab_s2), FadeOut(lab_s), run_time=0.6)
        lab_s = lab_s2

        # 6. break it: the helper that never crashes
        cmdn = M("$ uv run scripts/logsum.py access nope.log", 24, GREY_B).move_to(cmd)
        wrap = SurroundingRectangle(VGroup(helper, hl2), color=PURPLE_M, buff=0.2, corner_radius=0.15)
        wl = VGroup(M("try: ...", 22, PURPLE_M), M("except Exception: pass", 22, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(wrap, UP, buff=0.2)
        self.beat("Now the big trap. You might think the safest script is one that never crashes. So let's wrap the whole thing in try, and except Exception, pass. Catch every error, and do nothing.",
                  Create(wrap), FadeIn(wl, shift=DOWN * 0.1), Transform(num, M("?", 34, YELLOW_M).move_to(thumb)), ci[0].animate.set_stroke(GREY_B), run_time=2.4)
        self.steps("Give it a log file that is not there. Pause and guess. What does CI see?",
                   (0.8, Transform(cmd, cmdn), Transform(bl[1], M("nope.log", 22, RED_M).move_to(bl[1])), book.animate.set_opacity(0.25)))
        self.wait(2.0)
        self.steps("A zero. Green. The file was never read, nothing was checked, and the note says done.",
                   (0.6, travel(oa[2], YELLOW_M, 0.6)), (0.5, Transform(num, zero.copy())), (0.6, ci[0].animate.set_stroke(GREEN_M)),
                   (1.2, Wait(1.2)), (0.6, Indicate(cia, color=GREEN_M)))
        key = T("the stock room key, written in Python", 26, RED_M).move_to([-2.8, -2.6, 0])
        self.beat("That is the stuck key from the opening, written in Python.", FadeIn(key, shift=UP * 0.1), run_time=1.0)
        self.beat("Honestly, except Exception pass should have been named: close your eyes and smile.",
                  Wiggle(wl), run_time=1.4)
        rule = T("A hidden failure looks exactly like success.", 30, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("Jokes aside, here is the point. A hidden failure looks exactly like success.",
                  key.animate.shift(UP * 0.3), FadeIn(rule, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(key, rule, wrap, wl)), run_time=0.6)

        # 7. the same trap when calling another program
        git = mbox("git", TEAL_M, size=26, w=1.3, h=0.7).move_to([-5.4, 2.6, 0])
        call = M('subprocess.run(["git", "pull"])', 22, TEAL_M).move_to([-2.0, 3.2, 0])
        ga = Arrow(helper.get_top(), git.get_right(), buff=0.2, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.12)
        self.play(FadeOut(cmd), run_time=0.4)
        self.beat("The same trap waits when a script asks another program for help. subprocess.run starts git, the tool that saves versions of files, and waits for it.",
                  FadeIn(git), GrowArrow(ga), FadeIn(call), Transform(num, M("?", 34, YELLOW_M).move_to(thumb)), ci[0].animate.set_stroke(GREY_B), run_time=2.4)
        gx = M("exit 1", 22, RED_M).next_to(git, DOWN, buff=0.15)
        self.steps("Git fails, say with a merge conflict. run only writes git's exit code down. And your script carries on to the next line, as if git had worked.",
                   (0.8, git[0].animate.set_stroke(RED_M), FadeIn(gx)), (2.0, Wait(2.0)), (1.2, helper.animate.shift(RIGHT * 0.25)), (0.6, helper.animate.shift(LEFT * 0.25)))
        call2 = M('subprocess.run([...], check=True)', 22, TEAL_M).move_to(call)
        loud = M("CalledProcessError", 22, RED_M).next_to(call2, DOWN, buff=0.15)
        self.steps("Add check=True, and the failure becomes loud. Python raises CalledProcessError, and the script stops instead of pretending.",
                   (0.8, Transform(call, call2)), (1.4, Wait(1.4)), (0.6, FadeIn(loud, shift=DOWN * 0.1)), (0.5, Wiggle(helper)))
        self.play(FadeOut(VGroup(git, gx, ga, call, loud)), run_time=0.6)

        # 8. name it: the exit code contract
        con = VGroup(
            VGroup(M("0", 30, GREEN_M), T("all good", 26)).arrange(RIGHT, buff=0.35),
            VGroup(M("1", 30, RED_M), T("the check found a problem", 26)).arrange(RIGHT, buff=0.35),
            VGroup(M("2", 30, GOLD_M), T("the script could not do its job", 26)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([-3.5, -2.55, 0])
        self.beat("So the lab gives every script the same contract for that number. Zero, all good. One, the check found a problem. Two, the script could not do its job.",
                  LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in con], lag_ratio=0.7), Transform(num, M("?", 34, YELLOW_M).move_to(thumb)), run_time=4.6)
        cmd = M("$ uv run scripts/logsum.py access nope.log", 24, GREY_B).move_to([0, 3.35, 0])
        nf = VGroup(M("ERROR no such file:", 22, RED_M), M("nope.log", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(lab_e, DOWN, buff=0.25).align_to(lab_e, LEFT)
        two = M("2", 34, GOLD_M).move_to(thumb)
        self.steps("The real logsum catches FileNotFoundError by name. It writes one clear line on stderr, no such file, nope.log. And it hands back two.",
                   (0.6, FadeIn(cmd)), (1.8, Wait(1.8)), (0.6, travel(oa[1], RED_M, 0.6)), (0.8, FadeIn(nf, shift=UP * 0.1)),
                   (0.6, travel(oa[2], YELLOW_M, 0.6)), (0.5, Transform(num, two)), (0.6, Indicate(con[2][1], color=GOLD_M)))
        self.beat("Now a caller can tell the error rate is too high apart from the log is missing. Different trouble, different number.",
                  Indicate(con[1][1], color=RED_M), Succession(Wait(1.8), Indicate(con[2][1], color=GOLD_M)), run_time=3.2)

        # 9. guardrail
        self.play(FadeOut(VGroup(con, nf, cmd)), run_time=0.5)
        g = VGroup(T("catch the errors you expect, by name", 28, GREEN_M), T("let everything else crash, loudly", 28, GREEN_M),
                   T("call programs with a list, check=True, a timeout", 28, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-2.4, -2.55, 0])
        self.steps("Three habits keep the helper honest. Catch the errors you expect, by name, and turn each one into a clear line. Let everything else crash, with its traceback, the trail of lines that shows where it broke. And when you call another program, pass a list, check equals true, and a timeout.",
                   (0.8, FadeIn(g[0], shift=UP * 0.1)), (4.0, Wait(4.0)), (0.8, FadeIn(g[1], shift=UP * 0.1)), (4.2, Wait(4.2)), (0.8, FadeIn(g[2], shift=UP * 0.1)))
        self.play(FadeOut(g), run_time=0.5)

        # 10. moral and quick check
        mor = VGroup(T("report on the sheet, reasons in the note,", 28), T("the verdict in the thumb", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-6.2, -2.75, 0], aligned_edge=LEFT)
        self.beat("So back to the shop. The report goes on the sheet. The reasons go in the note. And the verdict is the thumb. A good helper says failed, out loud.",
                  FadeIn(mor, shift=UP * 0.1), LaggedStart(Indicate(lab_s[0], color=WHITE), Indicate(lab_e[0], color=RED_M), Indicate(lab_x[0], color=YELLOW_M), lag_ratio=0.5), run_time=4.0)
        quiz = VGroup(T("Quick check: it prints \"all fine\"", 28, YELLOW_M), T("and exits with 1. Did it pass?", 28, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-6.2, -2.75, 0], aligned_edge=LEFT)
        self.beat("Quick check before you go. A script prints all fine, then exits with one. Did it pass?",
                  FadeOut(mor), FadeIn(quiz, shift=UP * 0.1), Transform(num, M("1", 34, RED_M).move_to(thumb)), run_time=1.4)
        self.wait(2.0)
        self.beat("No. CI trusts the number, not the words.", ci[0].animate.set_stroke(RED_M), Indicate(num, color=RED_M, scale_factor=1.4), run_time=1.2)
        self.wait(1.2)
