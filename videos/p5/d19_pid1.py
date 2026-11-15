import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"--entrypoint\b", "dash dash entry point"), (r"\bENTRYPOINT\b", "entry point"), (r"\bCMD\b", "C M D"),
            (r"\bgunicorn\b", "G-unicorn"), (r"\bGunicorn\b", "G-unicorn"), (r"\bSIGTERM\b", "sig term"), (r"\bSIGKILL\b", "sig kill"),
            (r"/bin/sh -c", "bin S H, dash C"), (r"\bDockerfile\b", "Docker file")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def proc(pid, cmd, color, w=4.4, h=0.72, size=22):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.16), opacity=1)
    if pid:
        p = M(pid, size, YELLOW_M)
        c = M(cmd, size)
        g = VGroup(p, c).arrange(RIGHT, buff=0.3)
    else:
        g = M(cmd, size)
    fit(g, w - 0.4)
    return VGroup(r, g.move_to(r))


def shell(w, h, label, color=GREY_B):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=2).set_fill(BLACK, 1)
    t = T(label, 20, GREY_B).next_to(r.get_corner(UL), DR, buff=0.15)
    return VGroup(r, t)


class D19Pid1(VoiceScene):
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
        self.title_card("What runs when a container starts", "CMD, ENTRYPOINT, and who is PID 1")

        # ---- 0. the teaser: one line, two ways, two stop times
        lines = ["FROM python:3.14-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install ...", "COPY app.py .", "CMD ..."]
        df = VGroup(*[M(l, 24, GREY_B if i < 5 else YELLOW_M) for i, l in enumerate(lines)]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        dfr = RoundedRectangle(corner_radius=0.15, width=df.width + 0.9, height=df.height + 0.7, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.08), 1)
        dfile = VGroup(dfr, df.move_to(dfr)).move_to([0, 0.1, 0])
        dlab = T("Dockerfile", 26, BLUE_M).next_to(dfile, UP, buff=0.25)
        self.beat("A Dockerfile ends with a line that builds nothing. It only says what the container runs when it starts.",
                  Create(dfr), FadeIn(dlab), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in df], lag_ratio=0.25), run_time=3.2)
        self.play(df[:5].animate.set_opacity(0.35), Indicate(df[5], color=YELLOW_M), run_time=0.8)
        sh_line = M("CMD gunicorn app:app", 28, RED_M)
        ex_line = M('CMD ["gunicorn", "app:app"]', 28, GREEN_M)
        pair = VGroup(sh_line, ex_line).arrange(DOWN, aligned_edge=LEFT, buff=0.7).move_to([-2.4, 0, 0])
        self.beat("Here are two ways to write that line, for the same app.",
                  FadeOut(VGroup(dfr, dlab, df[:5])), ReplacementTransform(df[5], sh_line), FadeIn(ex_line, shift=UP * 0.15), run_time=1.8)
        t_sh = T("docker stop: 10.2 s", 28, RED_M).move_to([1.4, sh_line.get_center()[1], 0], aligned_edge=LEFT)
        t_ex = T("docker stop: 0.6 s", 28, GREEN_M).move_to([1.4, ex_line.get_center()[1], 0], aligned_edge=LEFT)
        self.beat("The lesson timed docker stop on both. One container stopped in 0.6 seconds. The other needed 10.2 seconds.",
                  Succession(Wait(1.6), FadeIn(t_ex, shift=LEFT * 0.15), Wait(1.4), FadeIn(t_sh, shift=LEFT * 0.15)), run_time=4.4)
        q = T("same app, same image: why?", 30, YELLOW_M).move_to([0, -2.2, 0])
        self.beat("Same app, same image. So why the big difference? Let's build it up from the start.", FadeIn(q, shift=UP * 0.15), run_time=1.4)
        self.play(FadeOut(VGroup(pair, t_sh, t_ex, q)), run_time=0.6)

        # ---- 1. CMD and ENTRYPOINT with the greeter image
        ep = M('ENTRYPOINT ["echo", "Hello,"]', 24, GOLD_M)
        cm = M('CMD ["world"]', 24, BLUE_M)
        card_t = VGroup(ep, cm).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        cr = RoundedRectangle(corner_radius=0.15, width=card_t.width + 0.8, height=card_t.height + 0.8, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1)
        card = VGroup(cr, card_t.move_to(cr)).move_to([-3.6, 0.3, 0])
        clab = T("image: greeter", 24, GREY_B).next_to(card, UP, buff=0.25)
        self.beat("First, CMD and ENTRYPOINT. Both say what runs when a container starts. Take a tiny image called greeter.",
                  Create(cr), FadeIn(clab), Succession(Wait(1.6), LaggedStart(Write(ep), Write(cm), lag_ratio=0.5)), run_time=3.4)

        run1 = M("$ docker run greeter", 26).move_to([1.7, 2.5, 0], aligned_edge=LEFT)
        prog = chip("echo Hello,", GOLD_M, 26, mono=True)
        argc = chip("world", BLUE_M, 26, mono=True)
        line = VGroup(prog, argc).arrange(RIGHT, buff=0.25).move_to([3.3, 0.3, 0])
        runs = T("what runs", 22, GREY_B).next_to(line, UP, buff=0.3)
        self.steps("When you type docker run greeter, Docker puts the two together. ENTRYPOINT gives the program: echo Hello. CMD gives its default argument: world.",
                   (1.2, Write(run1)), (1.0, FadeIn(runs)), (1.4, TransformFromCopy(ep, prog)), (1.6, Wait(1.6)),
                   (1.4, TransformFromCopy(cm, argc)))
        out = M("Hello, world", 30, GREEN_M).move_to([3.3, -1.6, 0])
        oa = Arrow(line.get_bottom(), out.get_top(), buff=0.2, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("So it prints: Hello, world.", GrowArrow(oa), FadeIn(out, shift=DOWN * 0.1), run_time=1.2)

        ana_t = M("Ana", 26, PURPLE_M).next_to(run1, RIGHT, buff=0.22)
        self.beat("Now type a name after the image: docker run greeter Ana.",
                  Succession(Wait(1.4), Write(ana_t)), run_time=2.4)
        ana = chip("Ana", PURPLE_M, 26, mono=True).move_to(argc)
        self.steps("What you type replaces CMD. Ana takes the place of world.",
                   (0.8, Indicate(ana_t, color=PURPLE_M)),
                   (1.2, argc.animate.shift(DOWN * 0.9).set_opacity(0), TransformFromCopy(ana_t, ana)))
        self.remove(argc)
        out2 = M("Hello, Ana", 30, GREEN_M).move_to(out)
        self.beat("But ENTRYPOINT stays. Ana is added after it, so the program is the same. It prints: Hello, Ana.",
                  Indicate(prog, color=GOLD_M), Succession(Wait(2.6), Transform(out, out2)), run_time=3.6)
        tags = VGroup(T("fixed", 22, GOLD_M).next_to(prog, DOWN, buff=0.2).align_to(prog, LEFT).shift(RIGHT * 0.1), T("default, replaced", 22, BLUE_M).next_to(cm, DOWN, buff=0.25).align_to(cm, LEFT))
        cr2 = RoundedRectangle(corner_radius=0.15, width=cr.width, height=cr.height + 0.5, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1).move_to(cr).align_to(cr, UP)
        self.steps("So CMD is a default, and ENTRYPOINT is fixed. Only the flag --entrypoint swaps the program itself. For a web app, CMD alone is the simple choice.",
                   (1.2, FadeIn(tags[1]), Transform(cr, cr2)), (0.8, FadeIn(tags[0])), (3.4, Wait(3.4)), (1.0, Indicate(cm, color=BLUE_M)))
        self.play(FadeOut(VGroup(card, clab, tags, run1, ana_t, prog, ana, runs, oa, out)), run_time=0.6)

        # ---- 2. exec form and shell form
        LX, RX = -3.45, 3.45
        h_sh = T("shell form", 28, RED_M).move_to([LX, 3.3, 0])
        h_ex = T("exec form", 28, GREEN_M).move_to([RX, 3.3, 0])
        c_sh = M("CMD gunicorn app:app", 24).next_to(h_sh, DOWN, buff=0.25)
        c_ex = M('CMD ["gunicorn", "app:app"]', 24).next_to(h_ex, DOWN, buff=0.25)
        div = DashedLine([0, 3.6, 0], [0, -3.4, 0], dash_length=0.1, stroke_width=1.5, color=GREY_D)
        self.beat("Next, how you write the line. There are two forms.",
                  FadeIn(h_sh), FadeIn(h_ex), Create(div), FadeIn(c_sh), FadeIn(c_ex), run_time=1.6)

        box_r = shell(5.6, 2.9, "container").move_to([RX, -0.3, 0])
        box_l = shell(5.6, 2.9, "container").move_to([LX, -0.3, 0])
        g_ex = proc("PID 1", "gunicorn app:app", GREEN_M).move_to([RX, 0.35, 0])
        self.beat("Exec form is a JSON list. Docker starts gunicorn directly. So your app runs as PID 1, the first process in the container.",
                  Indicate(c_ex, color=GREEN_M), Succession(Wait(1.8), AnimationGroup(FadeIn(box_r), GrowFromCenter(g_ex))), run_time=3.6)
        c_sh2 = M('/bin/sh -c "gunicorn app:app"', 24, RED_M).move_to(c_sh)
        self.beat("Shell form is plain text. Docker runs it through a shell: /bin/sh -c, and then your command.",
                  Succession(Wait(1.8), Transform(c_sh, c_sh2)), run_time=3.0)
        s_pid = proc("PID 1", '/bin/sh -c "gunicorn ..."', RED_M, w=5.1, size=20).move_to([LX, 0.35, 0])
        s_kid = proc("", "gunicorn app:app", GREY_B, w=3.4, h=0.66).move_to([LX + 0.4, -0.95, 0])
        s_ln = Line(s_pid.get_bottom() + LEFT * 1.6, [s_pid.get_left()[0] + 0.6, s_kid.get_center()[1], 0], stroke_width=2.5, color=GREY_B)
        s_ln2 = Line(s_ln.get_end(), s_kid.get_left(), stroke_width=2.5, color=GREY_B)
        kid_l = T("child", 20, GREY_B).next_to(s_ln, LEFT, buff=0.1)
        self.beat("Now the shell is PID 1, and gunicorn is only its child.",
                  FadeIn(box_l), GrowFromCenter(s_pid), Succession(Wait(1.0), AnimationGroup(Create(s_ln), Create(s_ln2), FadeIn(s_kid), FadeIn(kid_l))), run_time=2.8)

        # ---- 3. docker stop on both
        stop = chip("docker stop", YELLOW_M, 26, mono=True).move_to([0, 1.9, 0])
        c_sh.set_opacity(0.4); c_ex.set_opacity(0.4)
        sig_r = Arrow(stop.get_right(), g_ex.get_top(), buff=0.1, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.12)
        sig_l = Arrow(stop.get_left(), s_pid.get_top(), buff=0.1, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.12)
        sig_t = M("SIGTERM", 22, YELLOW_M).next_to(stop, DOWN, buff=0.15)
        self.steps("Now run docker stop on both. Docker sends a signal called SIGTERM to PID 1. It means: please finish up and exit.",
                   (0.8, FadeOut(div), c_sh.animate.set_opacity(0.4), c_ex.animate.set_opacity(0.4), FadeIn(stop, scale=0.8)),
                   (1.4, Wait(1.4)), (1.0, GrowArrow(sig_l), GrowArrow(sig_r), FadeIn(sig_t)),
                   (1.0, travel(sig_l, YELLOW_M, 1.0), travel(sig_r, YELLOW_M, 1.0)))

        tv_r, tv_l = ValueTracker(0), ValueTracker(0)
        clk_r = always_redraw(lambda: M(f"{tv_r.get_value():4.1f} s", 30, GREEN_M).move_to([RX, -2.35, 0]))
        clk_l = always_redraw(lambda: M(f"{tv_l.get_value():4.1f} s", 30, RED_M if tv_l.get_value() > 9.99 else WHITE).move_to([LX, -2.35, 0]))
        self.add(clk_r, clk_l)
        ex0 = chip("Exited (0)", GREEN_M, 24, mono=True).move_to([RX, -3.1, 0])
        self.steps("On the right, gunicorn gets it. It finishes its work, and exits on its own, with code 0, in 0.6 seconds.",
                   (1.2, Indicate(g_ex, color=GREEN_M)), (1.0, Wait(1.0)),
                   (1.0, tv_r.animate.set_value(0.6), g_ex.animate.set_opacity(0.25), box_r[0].animate.set_stroke(GREEN_M)), (0.8, FadeIn(ex0, shift=UP * 0.1)))
        drop = tick(False, 0.2).next_to(s_pid, RIGHT, buff=0.12)
        np_l = T("not passed on", 20, RED_M).next_to(s_ln2, DOWN, buff=0.12).align_to(s_ln2, LEFT)
        np_l.next_to(s_kid, DOWN, buff=0.15)
        dot = Dot(radius=0.08, color=YELLOW_M).move_to(s_pid.get_bottom() + LEFT * 1.6)
        self.steps("On the left, the shell gets it. But the shell does not pass SIGTERM on to its child. Gunicorn never hears it.",
                   (1.2, Indicate(s_pid, color=RED_M)), (0.8, Wait(0.8)), (0.6, FadeIn(dot)),
                   (1.0, dot.animate.move_to(s_ln.get_end()).set_opacity(0.0)), (0.8, FadeIn(np_l)), (0.6, Create(drop)))
        self.remove(dot)
        slow = T("clock sped up", 20, GREY_B).next_to(clk_l, LEFT, buff=0.3)
        sk = M("SIGKILL", 22, RED_M).next_to(stop, DOWN, buff=0.15)
        self.steps("So Docker waits. After 10 seconds, it gives up and sends SIGKILL.",
                   (0.5, FadeIn(slow)), (3.4, tv_l.animate(rate_func=linear).set_value(10.0)),
                   (0.6, Transform(sig_t, sk), sig_l.animate.set_color(RED_M), sig_r.animate.set_opacity(0.2)),
                   (0.8, travel(sig_l, RED_M, 0.8)))
        ex137 = chip("Exited (137)", RED_M, 24, mono=True).move_to([LX, -3.1, 0])
        self.steps("The container ends with code 137, after 10.2 seconds. In production, every deploy then waits ten extra seconds per container, and requests in flight are cut off.",
                   (1.0, s_pid.animate.set_opacity(0.25), s_kid.animate.set_opacity(0.25), tv_l.animate.set_value(10.2), FadeOut(slow)),
                   (0.6, FadeIn(ex137, shift=UP * 0.1), box_l[0].animate.set_stroke(RED_M)))
        self.play(FadeOut(VGroup(s_pid, s_kid, s_ln, s_ln2, kid_l, np_l, drop, ex137, box_l, h_sh, c_sh, sig_l, sig_r, sig_t, stop, ex0, g_ex, box_r, h_ex, c_ex)),
                  FadeOut(clk_l), FadeOut(clk_r), run_time=0.7)
        self.remove(clk_l, clk_r)

        # ---- 4. PID 1 is special
        q2 = T("So is exec form the whole fix?", 32, YELLOW_M).move_to([0, 3.1, 0])
        self.beat("So is exec form the whole fix? Not quite. PID 1 is special in Linux.", FadeIn(q2, shift=DOWN * 0.15), run_time=1.4)
        rule = VGroup(T("The kernel drops any signal", 30), T("that PID 1 has no handler for.", 30), T("SIGKILL aside.", 26, GREY_B)).arrange(DOWN, buff=0.18)
        rr = RoundedRectangle(corner_radius=0.15, width=rule.width + 0.8, height=rule.height + 0.6, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.08), 1)
        rbox = VGroup(rr, rule.move_to(rr)).move_to([0, 1.25, 0])
        self.beat("The kernel drops any signal that PID 1 has no handler for. SIGKILL is the only exception.",
                  Create(rr), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rule], lag_ratio=0.4), run_time=2.8)

        b2l = shell(5.6, 2.1, "container, exec form").move_to([LX, -1.45, 0])
        b2r = shell(5.6, 2.1, "container, exec form").move_to([RX, -1.45, 0])
        p_g = proc("PID 1", "gunicorn", GREEN_M, w=3.2).move_to([RX - 0.7, -1.6, 0])
        hnd = chip("handler", GREEN_M, 22).next_to(p_g, RIGHT, buff=0.2)
        self.beat("A handler is code in the program that says what to do when a signal arrives. Gunicorn has one for SIGTERM.",
                  FadeIn(b2r), GrowFromCenter(p_g), Succession(Wait(2.4), FadeIn(hnd, shift=LEFT * 0.1)), run_time=3.4)
        p_p = proc("PID 1", "a bare Python script", GOLD_M, w=4.6).move_to([LX, -1.6, 0])
        noh = T("no handler", 22, RED_M).next_to(p_p, DOWN, buff=0.15)
        self.beat("A bare Python script has none. So even in exec form, as PID 1, its SIGTERM is simply dropped.",
                  FadeIn(b2l), GrowFromCenter(p_p), Succession(Wait(1.0), FadeIn(noh)), run_time=2.6)
        tv3 = ValueTracker(0)
        clk3 = always_redraw(lambda: M(f"{tv3.get_value():4.1f} s", 28, RED_M if tv3.get_value() > 9.99 else WHITE).move_to([LX, -3.15, 0]))
        tv4 = ValueTracker(0)
        clk4 = always_redraw(lambda: M(f"{tv4.get_value():4.1f} s", 28, GREEN_M).move_to([RX, -3.15, 0]))
        self.add(clk3, clk4)
        self.steps("In the lesson's test, it waited out the full 10 seconds, just like sleep did on Day 17.",
                   (0.5, Wait(0.5)), (0.4, tv4.animate.set_value(0.6), p_g.animate.set_opacity(0.3)),
                   (3.2, tv3.animate(rate_func=linear).set_value(10.0)), (0.6, p_p.animate.set_opacity(0.3), b2l[0].animate.set_stroke(RED_M)))
        self.play(FadeOut(VGroup(q2, rbox, b2l, b2r, p_g, hnd, p_p, noh)), FadeOut(clk3), FadeOut(clk4), run_time=0.6)
        self.remove(clk3, clk4)

        need = VGroup(VGroup(tick(True, 0.22), T("exec form, so your app is PID 1", 30)).arrange(RIGHT, buff=0.35),
                      VGroup(tick(True, 0.22), T("an app that handles SIGTERM", 30)).arrange(RIGHT, buff=0.35)).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        need.move_to([0, 0.6, 0])
        self.beat("So you need both. Exec form, so your app is PID 1. And an app that handles SIGTERM itself, as gunicorn does.",
                  LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in need], lag_ratio=0.6), run_time=3.0)

        # ---- 5. recap
        rc = VGroup(M('ENTRYPOINT ["echo", "Hello,"]', 24, GOLD_M), M('CMD ["world"]', 24, BLUE_M)).arrange(RIGHT, buff=0.6).move_to([0, -1.9, 0])
        rl = VGroup(T("fixed", 22, GOLD_M).next_to(rc[0], DOWN, buff=0.2), T("default", 22, BLUE_M).next_to(rc[1], DOWN, buff=0.2))
        self.beat("ENTRYPOINT is fixed, and CMD is a default. Write both as a JSON list, so your app is PID 1, and it hears docker stop.",
                  FadeIn(rc, shift=UP * 0.15), FadeIn(rl), Succession(Wait(2.6), need[0][1].animate.set_color(GREEN_M)), run_time=4.4)
        self.wait(1.0)
