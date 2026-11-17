import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bSIGTERM\b", "sig term"), (r"\bSIGKILL\b", "sig kill"), (r"\bgunicorn\b", "green unicorn"),
            (r"\bWORKDIR\b", "work dir"), (r"\brequirements\.txt\b", "requirements dot text"), (r"\bapp\.py\b", "app dot pie"),
            (r"\bpip\b", "pip"), (r"\bCMD\b", "C M D"), (r"\bCOPY \. \.", "copy dot dot")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def row(text, color=WHITE, w=6.4, mono=True, size=24):
    t = (M if mono else T)(text, size if mono else 28, color)
    r = RoundedRectangle(corner_radius=0.08, width=w, height=0.62, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.1), opacity=1)
    t.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.25)
    return VGroup(r, t)


def status(text, color):
    return chip(text, color, 24, mono=True)


class D19NapkinLast(VoiceScene):
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

    def place(self, rows, x=-2.2, top=1.9):
        for i, r in enumerate(rows):
            r.move_to([x, top - i * 0.78, 0])
        return rows

    def construct(self):
        self.title_card("Put the napkin last", "how Docker reuses build steps, and how a container stops politely")

        # 1. the packing list with a strange rule
        lunch = VGroup(row("1. cook the rice    40 min", GOLD_M, mono=False), row("2. add the curry", GOLD_M, mono=False), row("3. pack a napkin", GOLD_M, mono=False))
        self.place(lunch, top=1.2)
        head = T("your packing list", 28, GOLD_M).next_to(lunch, UP, buff=0.35)
        self.steps("Picture packing your lunch every morning from a written list. Cook the rice, which takes forty minutes. Add the curry. Pack a napkin.",
                   (0.6, FadeIn(head)), (1.6, Wait(1.6)), (0.6, FadeIn(lunch[0], shift=DOWN * 0.1)), (1.0, Wait(1.0)), (0.6, FadeIn(lunch[1], shift=DOWN * 0.1)), (0.6, FadeIn(lunch[2], shift=DOWN * 0.1)))
        rule = VGroup(T("strange rule:", 26, RED_M), T("change a step, and redo", 26), T("every step after it", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([4.4, 0.4, 0])
        self.beat("One morning you want a blue napkin instead of a white one. And your list has a strange rule. Change any step, and you must redo every step after it.",
                  lunch[2][0].animate.set_stroke(BLUE_M), Succession(Wait(2.2), FadeIn(rule, shift=LEFT * 0.1)), run_time=3.4)
        self.play(lunch[2][0].animate.set_stroke(GOLD_M), run_time=0.3)
        flip = VGroup(row("1. pack a napkin", BLUE_M, mono=False), row("2. cook the rice    40 min", GOLD_M, mono=False), row("3. add the curry", GOLD_M, mono=False))
        self.place(flip, top=1.2)
        redo = VGroup(*[status("redo", RED_M).next_to(f, RIGHT, buff=0.25) for f in flip])
        self.steps("Fine, as long as the napkin line comes last. But if it came first, you would cook the rice again, forty minutes, just to swap a napkin.",
                   (1.8, Wait(1.8)), (1.0, ReplacementTransform(lunch, flip)), (1.6, LaggedStart(*[FadeIn(r) for r in redo], lag_ratio=0.35)))
        self.beat("Nobody would write a list like that. And yet, in software, we do it all the time.",
                  Indicate(flip[1][1], color=RED_M), run_time=1.4)
        self.play(FadeOut(VGroup(flip, redo, head)), rule.animate.move_to([4.5, 2.75, 0]), run_time=0.7)

        # 2. map onto a Dockerfile
        df = VGroup(row("FROM python:3.14-slim", BLUE_M), row("WORKDIR /app", BLUE_M), row("COPY . .", PURPLE_M), row("RUN pip install -r requirements.txt", GOLD_M))
        self.place(df)
        dh = T("Dockerfile", 28, BLUE_M).next_to(df, UP, buff=0.3)
        self.steps("Docker's recipe for an image is a file called a Dockerfile. It is read from the top, one instruction per line, and each line that changes files becomes a layer, like the tiers from last time.",
                   (0.6, FadeIn(dh)), (2.0, Wait(2.0)), (2.0, LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in df], lag_ratio=0.3)))
        self.beat("Start from a Python base image. Work in a folder called app. Copy in every file of our app, hello-devops. Then pip installs its packages. That is the slow step.",
                  LaggedStart(*[Indicate(r[1], color=WHITE, scale_factor=1.04) for r in df], lag_ratio=0.5), run_time=5.0)
        st = VGroup(status("runs", GREY_B), status("runs", GREY_B), status("runs", GREY_B), status("about 10s", RED_M))
        for s, r in zip(st, df):
            s.next_to(r, RIGHT, buff=0.25)
        self.steps("The first build runs every step. The pip install alone takes about ten seconds.",
                   (1.6, LaggedStart(*[FadeIn(s) for s in st], lag_ratio=0.4)), (0.6, Indicate(st[3][1], color=RED_M)))
        cache = T("build cache: layers kept from earlier builds", 26, GREEN_M).move_to([0, -2.4, 0])
        self.beat("Docker keeps every layer it builds, in a build cache. Next time, it reuses a step if that step, and everything before it, is unchanged.",
                  FadeIn(cache, shift=UP * 0.1), run_time=1.4)

        # 3. predict: edit one comment in app.py
        self.play(FadeOut(st), run_time=0.4)
        edit = T("you change one comment in app.py", 28, YELLOW_M).move_to([0, -3.1, 0])
        self.beat("Now you change one comment in app.py, and build again. Which steps run again? Pause and guess.",
                  FadeIn(edit, shift=UP * 0.1), run_time=1.4)
        self.wait(2.0)
        st2 = VGroup(status("0.0s", GREEN_M), status("CACHED", GREEN_M), status("runs", RED_M), status("runs again", RED_M))
        for s, r in zip(st2, df):
            s.next_to(r, RIGHT, buff=0.25)
        self.steps("The first two are reused. But COPY dot dot copied every file, and one of them changed. So that layer is new. And every layer after it is rebuilt too, including the whole pip install.",
                   (0.8, FadeIn(st2[0]), FadeIn(st2[1])), (2.0, Wait(2.0)), (0.6, FadeIn(st2[2]), df[2][0].animate.set_stroke(RED_M)),
                   (2.6, Wait(2.6)), (0.8, FadeIn(st2[3]), df[3][0].animate.set_stroke(RED_M)))
        self.beat("Ten seconds of installing, for a comment. That is the blue napkin, packed first.", Indicate(rule[0], color=RED_M), run_time=1.6)

        # fair to the rule
        fair = VGroup(T("why the rule exists:", 26, GREY_B), T("each layer is changes on top of the exact layers below", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([0, -2.6, 0])
        self.steps("Is Docker being lazy? Let's be fair to the rule. Each layer holds the changes one step made, on top of the exact layers below it. If a lower layer changed, Docker cannot know whether pip install would give the same result, without running it again.",
                   (0.6, FadeOut(cache), FadeOut(edit)), (2.4, Wait(2.4)), (0.8, FadeIn(fair, shift=UP * 0.1)))
        self.play(FadeOut(fair), run_time=0.4)

        # 4. the fix: reorder
        good = VGroup(row("FROM python:3.14-slim", BLUE_M), row("WORKDIR /app", BLUE_M), row("COPY requirements.txt .", TEAL_M),
                      row("RUN pip install -r requirements.txt", GOLD_M), row("COPY app.py .", PURPLE_M))
        self.place(good, top=1.9)
        self.steps("So we keep the same lines, and change only the order. Copy the list of packages on its own. Install them. And copy the code last.",
                   (0.6, FadeOut(st2)), (1.8, Wait(1.8)), (1.6, ReplacementTransform(df, VGroup(good[0], good[1], good[4], good[3]))), (0.8, FadeIn(good[2], shift=RIGHT * 0.2)))
        df = good
        self.add(df)
        edit = T("change one comment in app.py, again", 28, YELLOW_M).move_to([0, -2.9, 0])
        st3 = VGroup(status("0.0s", GREEN_M), status("CACHED", GREEN_M), status("CACHED", GREEN_M), status("CACHED", GREEN_M), status("runs", PURPLE_M))
        for s, r in zip(st3, df):
            s.next_to(r, RIGHT, buff=0.25)
        tot = T("whole build: 0.3 s", 30, GREEN_M).move_to([4.2, -2.1, 0])
        self.steps("Edit the same comment, and build again. The three steps above the code say cached. Only the last small layer runs, and the whole build takes 0.3 seconds.",
                   (0.6, FadeIn(edit, shift=UP * 0.1)), (1.4, Wait(1.4)), (1.4, LaggedStart(*[FadeIn(s) for s in st3[:4]], lag_ratio=0.3)), (0.6, FadeIn(st3[4])), (1.6, Wait(1.6)), (0.6, FadeIn(tot)))
        self.beat("Roughly thirty times faster than a fresh install, and we did not write a single new line. We just moved the napkin.",
                  Indicate(tot, color=GREEN_M), run_time=1.6)
        r1 = T("Put what changes least at the top. Copy the code last.", 30, YELLOW_M).move_to([0, -3.4, 0])
        self.beat("So here is the rule. Put what changes least at the top. Copy the code last.",
                  FadeOut(edit), FadeIn(r1, shift=UP * 0.1), run_time=1.4)

        # guardrail on what counts as changed
        g = VGroup(VGroup(M("COPY", 24, TEAL_M), T("checks file contents, not times", 26)).arrange(RIGHT, buff=0.3),
                   VGroup(M("RUN ", 24, GOLD_M), T("only compares the command text", 26)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.55, 0])
        self.steps("One honest limit: what counts as changed. COPY checks the contents of files, not when they were touched. RUN only compares the command text. So RUN apt-get update stays cached for months, even when new packages exist.",
                   (0.6, FadeOut(r1), FadeOut(tot)), (1.6, Wait(1.6)), (0.6, FadeIn(g[0], shift=UP * 0.1)), (1.6, Wait(1.6)), (0.6, FadeIn(g[1], shift=UP * 0.1)))
        self.play(FadeOut(VGroup(g, st3, df, dh, rule)), run_time=0.6)

        # 5. part two: stopping politely
        cbox = RoundedRectangle(corner_radius=0.15, width=5.2, height=3.0, stroke_color=GREY_B, stroke_width=3).move_to([1.4, 0.3, 0])
        cl = T("container", 26, GREY_B).next_to(cbox, UP, buff=0.2)
        door = Rectangle(width=0.18, height=1.2, stroke_width=0).set_fill(GREY_B, 0.8).move_to(cbox.get_left())
        stop = M("$ docker stop", 26, WHITE).move_to([-4.6, 2.3, 0])
        self.steps("One more line in the recipe decides how the box stops. When you run docker stop, Docker sends a polite message, SIGTERM, to the container's first process, PID 1. Then it waits ten seconds. If the app is still running, it sends SIGKILL, which ends it at once.",
                   (0.8, Create(cbox), FadeIn(cl), FadeIn(door)), (0.6, FadeIn(stop)), (4.0, Wait(4.0)), (0.6, Indicate(door, color=WHITE)))
        shellf = M('CMD gunicorn app:app', 26, RED_M).move_to([1.4, -2.0, 0])
        sh = box("sh", RED_M, w=1.2, h=0.7, size=28).move_to(cbox.get_left() + RIGHT * 1.1 + UP * 0.3)
        sh1 = M("PID 1", 22, RED_M).next_to(sh, DOWN, buff=0.12)
        gu = box("gunicorn", GREEN_M, w=2.0, h=0.7, size=26).move_to(cbox.get_right() + LEFT * 1.4 + UP * 0.3)
        self.steps("Here is CMD written plainly, as words. Docker runs it through a shell, a program that reads command lines. So the shell, sh, becomes PID 1, and gunicorn, the web server that runs hello-devops, sits behind it.",
                   (0.6, FadeIn(shellf, shift=UP * 0.1)), (2.0, Wait(2.0)), (0.8, FadeIn(sh), FadeIn(sh1)), (2.0, Wait(2.0)), (0.8, FadeIn(gu)))
        self.beat("Pause and guess. How long does docker stop take?")
        self.wait(2.0)
        env = VGroup(RoundedRectangle(corner_radius=0.05, width=1.5, height=0.5, stroke_color=YELLOW_M, stroke_width=2.5).set_fill(tint(YELLOW_M, 0.2), opacity=1), M("SIGTERM", 20, YELLOW_M))
        env[1].move_to(env[0])
        env.move_to(stop.get_bottom() + DOWN * 0.5)
        tt = ValueTracker(0)
        anchor = np.array([4.9, 2.3, 0])
        timer = always_redraw(lambda: M(f"{tt.get_value():.1f} s", 30, YELLOW_M).move_to(anchor))
        self.steps("The message arrives at the door. The shell takes it, and does not pass it on. gunicorn never hears a thing.",
                   (0.4, FadeIn(env), FadeIn(timer)), (1.0, env.animate.move_to(sh.get_left() + LEFT * 0.9)), (0.4, env.animate.move_to(sh)), (0.4, FadeOut(env, scale=0.5)), (1.0, Indicate(gu[1], color=GREEN_M)))
        kill = T("SIGKILL", 30, RED_M).move_to([1.4, 0.3, 0])
        ec = M("10.2 s, exit code 137", 26, RED_M).move_to([1.4, -2.7, 0])
        self.steps("So Docker waits out the full ten seconds, and then kills it. We measured it: 10.2 seconds, and exit code 137.",
                   (2.4, tt.animate.set_value(10.2)), (0.4, FadeIn(kill, scale=1.4)), (0.6, FadeOut(sh), FadeOut(gu), FadeOut(sh1)), (0.6, FadeIn(ec)))
        self.beat("A shell that keeps your mail and never forwards it. So the point is: the app itself has to be PID 1.")
        self.play(FadeOut(VGroup(kill)), run_time=0.3)

        # exec form
        execf = M('CMD ["gunicorn", "app:app"]', 26, GREEN_M).move_to(shellf)
        gu2 = box("gunicorn", GREEN_M, w=2.0, h=0.7, size=26).move_to(cbox.get_left() + RIGHT * 1.5 + UP * 0.3)
        g1 = M("PID 1", 22, GREEN_M).next_to(gu2, DOWN, buff=0.12)
        self.steps("Now write CMD as a list in square brackets. That is called exec form. No shell in between: gunicorn itself is PID 1.",
                   (0.6, FadeOut(ec)), (0.8, Transform(shellf, execf), tt.animate.set_value(0)), (1.6, Wait(1.6)), (0.8, FadeIn(gu2), FadeIn(g1)))
        env2 = env.copy().set_opacity(1).move_to(stop.get_bottom() + DOWN * 0.5)
        ec2 = M("0.6 s, exit code 0", 26, GREEN_M).move_to([1.4, -2.7, 0])
        self.steps("docker stop again. gunicorn gets the message, finishes politely, and exits. 0.6 seconds, and exit code zero.",
                   (0.3, FadeIn(env2)), (1.0, env2.animate.move_to(gu2)), (0.3, FadeOut(env2, scale=0.5)), (0.6, tt.animate.set_value(0.6)), (0.6, FadeOut(gu2), FadeOut(g1)), (0.6, FadeIn(ec2)))

        # guardrail: exec form is half the fix
        half = VGroup(T("exec form is only half the fix:", 26, GOLD_M), T("the app must handle SIGTERM itself", 26, GOLD_M)).arrange(DOWN, buff=0.1).move_to([0, 2.95, 0])
        self.steps("One honest catch. Exec form is only half the fix. The app must also handle SIGTERM itself. gunicorn does. A bare Python script does not, and as PID 1 it waited out the full ten seconds in our test, just like sleep.",
                   (0.8, FadeIn(half, shift=UP * 0.1)))
        timer.clear_updaters()
        self.play(FadeOut(VGroup(half, cbox, cl, door, stop, timer, shellf, ec2)), run_time=0.6)

        # 6. moral and quick check
        mor = VGroup(T("slow, stable steps first; the code last", 28, GOLD_M), T("CMD as a list, so the app is PID 1", 28, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([0, 1.2, 0])
        self.steps("So the moral of the story. Put the slow, stable steps first and the code last, so an edit rebuilds in a blink. And write CMD as a list, so the app itself hears the polite message, and stops in time.",
                   (0.8, FadeIn(mor[0], shift=UP * 0.1)), (3.4, Wait(3.4)), (0.8, FadeIn(mor[1], shift=UP * 0.1)))
        quiz = VGroup(T("Quick check: COPY . . comes before pip install.", 28, YELLOW_M), T("You edit app.py. Does pip run again?", 28, YELLOW_M)).arrange(DOWN, buff=0.12).move_to([0, -0.9, 0])
        self.beat("Quick check. A Dockerfile copies every file, then runs pip install. You edit app.py. Does pip run again?",
                  FadeIn(quiz, shift=UP * 0.1), run_time=1.4)
        self.wait(2.0)
        ans = T("Yes. A changed layer rebuilds every layer after it.", 28, GREEN_M).next_to(quiz, DOWN, buff=0.35)
        self.beat("Yes. A changed layer rebuilds every layer after it. Move the napkin to the end.", FadeIn(ans, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
