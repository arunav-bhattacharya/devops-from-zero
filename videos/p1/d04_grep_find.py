import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\b7f3a9c\b", "seven F three A nine C"), (r"\bgrep\b", "grep"), (r"\s-c\b", " dash C"), (r"\s-v\b", " dash V"),
            (r"\s-o\b", " dash O"), (r"\s-E\b", " dash E"), (r"\s-l\b", " dash L"), (r"\s-exec\b", " dash exec"),
            (r"\b2ms\b", "2 M S"), (r"\b34ms\b", "34 M S"), (r"\b2900ms\b", "2900 M S"), (r"\bms\b", "M S"), (r"09:06", "nine oh six")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


LOG = [
    "09:06:12 INFO  req=b2e410 GET /api/cart 200 2ms",
    "09:06:18 INFO  req=7f3a9c POST /api/checkout started for cart 5521",
    "09:06:18 INFO  req=7f3a9c calling payments-api: charge 59.90 EUR",
    "09:06:19 INFO  req=c91d07 GET /health 200 1ms",
    "09:06:21 WARN  req=7f3a9c payments-api answered slowly: 2900ms",
    "09:06:22 INFO  req=5d0e33 GET /api/cart 200 34ms",
    "09:06:24 ERROR req=7f3a9c timeout talking to payments-api after 3000ms",
    "09:06:24 INFO  req=7f3a9c POST /api/checkout 504 6012ms",
]
HIT = [i for i, l in enumerate(LOG) if "7f3a9c" in l]
LVL = {"INFO": GREY_B, "WARN": GOLD_M, "ERROR": RED_M}


def logline(t, size=20):
    m = M(t, size, WHITE)
    for k, c in LVL.items():
        p = t.find(k)
        if p >= 0 and p < 16:
            n = len(t[:p].replace(" ", ""))
            m[n:n + len(k)].set_color(c)
    return m


def fileicon(color=GREY_B, w=0.42, h=0.52):
    return Polygon([-w / 2, h / 2, 0], [w / 2 - 0.12, h / 2, 0], [w / 2, h / 2 - 0.12, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0],
                   stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.15), 1)


class D04GrepFind(VoiceScene):
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
        self.title_card("Searching text", "grep picks lines, find picks files")

        # 1. the problem
        ref = chip("failed checkout, about 09:06, reference 7f3a9c", RED_M, 26).move_to([0, 2.2, 0])
        self.beat("A customer reports a failed checkout at about 09:06, and quotes the reference 7f3a9c.",
                  FadeIn(ref, shift=DOWN * 0.15), run_time=1.6)
        svcs = VGroup(*[mbox(n, GREY_B, w=2.7, h=0.7, size=22) for n in ("gateway", "checkout-api", "payments-api", "orders-worker")]).arrange(RIGHT, buff=0.35).move_to([0, 0.2, 0])
        tags = VGroup(*[M("req=7f3a9c", 20, YELLOW_M).next_to(s, DOWN, buff=0.2) for s in svcs])
        self.beat("The services write that request ID on every log line. So the story is in the logs. But where, and in which lines?",
                  LaggedStart(*[FadeIn(s) for s in svcs], lag_ratio=0.15), Succession(Wait(1.0), LaggedStart(*[FadeIn(t) for t in tags], lag_ratio=0.15)), run_time=3.2)
        self.play(FadeOut(VGroup(ref, svcs, tags)), run_time=0.5)

        # 2. the log file
        PX = 0.0
        lines = VGroup(*[logline(t) for t in LOG]).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        top = RoundedRectangle(corner_radius=0.12, width=11.4, height=lines.height + 0.5, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.06), 1)
        top.move_to([PX, 1.75, 0]); lines.move_to(top)
        flab = M("checkout.log", 22, GREY_B).next_to(top, UP, buff=0.1).align_to(top, LEFT)
        self.beat("A log is a plain text file that a program adds to, one line per event. A time, a level, the request ID, and a message.",
                  Create(top), FadeIn(flab), LaggedStart(*[FadeIn(l, shift=UP * 0.05) for l in lines], lag_ratio=0.12), run_time=3.4)
        big = T("on a server: 2 GB of these", 26, GREY_B).move_to([0, -1.2, 0])
        self.beat("This one has eight lines. On a server, a log can be 2 gigabytes. cat would print it all, and it would scroll past for minutes.",
                  Succession(Wait(2.2), FadeIn(big, shift=UP * 0.1)), run_time=3.2)
        self.play(FadeOut(big), run_time=0.4)

        # 3. grep, line by line
        cmd = M("$ grep 7f3a9c checkout.log", 24, YELLOW_M).move_to([0, -0.2, 0]).align_to(top, LEFT)
        out = RoundedRectangle(corner_radius=0.12, width=11.4, height=2.75, stroke_color=TEAL_M, stroke_width=2.5).set_fill(tint(TEAL_M, 0.06), 1).move_to([PX, -2.15, 0])
        self.beat("grep answers one question: which lines contain this text?",
                  Write(cmd), Create(out), run_time=2.0)
        bar = Rectangle(width=11.1, height=0.33, stroke_width=0).set_fill(YELLOW_M, 0.18).move_to([PX, lines[0].get_y(), 0])
        slots = [out.get_top()[1] - 0.3 - 0.36 * k for k in range(5)]
        got = VGroup()

        def scan(i):
            anims = [bar.animate.move_to([PX, lines[i].get_y(), 0])]
            return anims

        def keep(i, k):
            c = lines[i].copy()
            tgt = c.copy().move_to([0, slots[k], 0]).align_to(out, LEFT).shift(RIGHT * 0.15)
            got.add(c)
            return AnimationGroup(lines[i].animate.set_opacity(1), Transform(c, tgt))

        self.steps("It reads its input one line at a time, and checks whether the pattern appears anywhere in the line.",
                   (0.6, FadeIn(bar)), (0.8, lines[0].animate.set_opacity(0.35)), (0.7, *scan(1)), (0.9, keep(1, 0)), (0.7, *scan(2)), (0.9, keep(2, 1)))
        self.steps("Lines that contain it are printed. The rest are skipped.",
                   (0.5, *scan(3)), (0.4, lines[3].animate.set_opacity(0.35)), (0.5, *scan(4)), (0.7, keep(4, 2)),
                   (0.5, *scan(5)), (0.4, lines[5].animate.set_opacity(0.35)), (0.5, *scan(6)), (0.7, keep(6, 3)), (0.5, *scan(7)), (0.7, keep(7, 4)))
        self.play(FadeOut(bar), run_time=0.3)
        self.beat("Five lines. Like a highlighter dragged down a printout, then you cut out only the marked lines.",
                  Indicate(got, color=TEAL_M, scale_factor=1.02), run_time=2.0)

        # 4. options answer questions
        cmd_c = M("$ grep -c 7f3a9c checkout.log", 24, YELLOW_M).move_to(cmd, aligned_edge=LEFT)
        five = M("5", 36, TEAL_M).move_to(out)
        self.beat("Each option changes one part of that, and answers one question. How many? -c counts the matching lines.",
                  Transform(cmd, cmd_c), Succession(Wait(2.4), AnimationGroup(FadeOut(got), FadeIn(five, scale=1.4))), run_time=3.6)
        cmd_v = M("$ grep -v 7f3a9c checkout.log", 24, YELLOW_M).move_to(cmd, aligned_edge=LEFT)
        rest = VGroup()
        for k, i in enumerate((0, 3, 5)):
            rest.add(lines[i].copy().set_opacity(1).move_to([0, slots[k], 0]).align_to(out, LEFT).shift(RIGHT * 0.15))
        self.beat("What is left without it? -v inverts the match. Now grep prints only the lines it skipped before.",
                  Transform(cmd, cmd_v), FadeOut(five),
                  *[lines[i].animate.set_opacity(1 if i not in HIT else 0.35) for i in range(8)],
                  Succession(Wait(1.6), LaggedStart(*[TransformFromCopy(lines[i], r) for i, r in zip((0, 3, 5), rest)], lag_ratio=0.3)), run_time=3.4)

        # 5. regex: a shape, tried at every position
        self.play(FadeOut(rest), *[l.animate.set_opacity(1) for l in lines], run_time=0.5)
        durs = VGroup()
        for i, d in ((0, "2ms"), (3, "1ms"), (4, "2900ms"), (5, "34ms"), (6, "3000ms"), (7, "6012ms")):
            t = LOG[i]; p = t.rfind(d)
            n0 = len(t[:p].replace(" ", ""))
            durs.add(lines[i][n0:n0 + len(d)])
        self.beat("Plain words only get you so far. Say you want every duration: 2ms, 34ms, 2900ms. No single word matches them all.",
                  LaggedStart(*[x.animate.set_color(GOLD_M) for x in durs], lag_ratio=0.15), run_time=2.6)
        self.beat("But they share a shape: digits, then ms. A regular expression is a pattern that describes a shape.",
                  Indicate(durs, color=GOLD_M, scale_factor=1.15), run_time=2.0)
        cmd_r = M("$ grep -o -E '[0-9]+ms' checkout.log", 24, YELLOW_M).move_to(cmd, aligned_edge=LEFT)
        self.beat("Square brackets with 0 to 9 match any one digit. Plus means one or more of it. Then the letters m s.",
                  Transform(cmd, cmd_r), Succession(Wait(0.8), Indicate(cmd[10:15], color=GOLD_M, scale_factor=1.3), Indicate(cmd[15], color=GOLD_M, scale_factor=1.6),
                                                     Indicate(cmd[16:18], color=GOLD_M, scale_factor=1.3)), run_time=4.2)

        # zoom on one line
        L = lines[5]
        t = LOG[5]

        def seg(a, b):
            n0 = len(t[:a].replace(" ", "")); n1 = len(t[:b].replace(" ", ""))
            return L[n0:n1]

        def probe(a, b, ok):
            s = seg(a, b)
            c = GREEN_M if ok else RED_M
            return SurroundingRectangle(s, color=c, buff=0.05, stroke_width=3)

        self.play(*[l.animate.set_opacity(0.25) for l in lines if l is not L], run_time=0.4)
        p_09 = probe(0, 2, False); i5 = t.find('5d0'); p_5 = probe(i5, i5 + 1, False); i2 = t.find('200'); p_200 = probe(i2, i2 + 3, False); i3 = t.find('34ms'); p_34 = probe(i3, i3 + 4, True)
        why = T("digits, then a space: no ms", 24, RED_M).move_to(out)
        self.steps("When grep reads a line, it tries the pattern at every position. Here, 09 is digits, but then comes a colon, not ms. No fit.",
                   (0.5, Create(p_09)), (2.4, Wait(2.4)), (0.4, FadeOut(p_09)), (0.5, Create(p_5)), (0.4, FadeOut(p_5)))
        self.steps("At 200, the digits fit, but then comes a space. No fit. At 34ms, the whole pattern fits. The line matches.",
                   (0.6, Create(p_200), FadeIn(why)), (1.4, Wait(1.4)), (0.4, FadeOut(p_200), FadeOut(why)), (0.8, Create(p_34)))
        ex = VGroup(*[M(d, 24, GOLD_M) for d in ("2ms", "1ms", "2900ms", "34ms", "3000ms", "6012ms")]).arrange(RIGHT, buff=0.55).move_to(out)
        self.beat("And -o prints only the part that matched. grep turns into an extractor.",
                  FadeOut(p_34), *[l.animate.set_opacity(1) for l in lines], LaggedStart(*[TransformFromCopy(d, e) for d, e in zip(durs, ex)], lag_ratio=0.15), run_time=2.8)
        self.beat("Plus belongs to extended regular expressions, so you add -E. In plain grep, plus is an ordinary character.",
                  Indicate(cmd[7:9], color=YELLOW_M, scale_factor=1.4), run_time=2.4)
        cmd_w = M("$ grep 'WARN|ERROR' checkout.log", 24, YELLOW_M).move_to(cmd, aligned_edge=LEFT)
        none = T("nothing found", 28, RED_M).move_to(out)
        self.beat("The same trap catches the bar. grep with WARN bar ERROR, and no -E, looks for that exact text, bar included. It finds nothing.",
                  FadeOut(ex), Transform(cmd, cmd_w), Succession(Wait(2.4), FadeIn(none)), run_time=3.6)
        cmd_we = M("$ grep -E 'WARN|ERROR' checkout.log", 24, YELLOW_M).move_to(cmd, aligned_edge=LEFT)
        we = VGroup(*[lines[i].copy().move_to([0, slots[k], 0]).align_to(out, LEFT).shift(RIGHT * 0.15) for k, i in enumerate((4, 6))])
        self.beat("With -E, the bar means or, and both lines come back.",
                  Transform(cmd, cmd_we), FadeOut(none), Succession(Wait(1.0), LaggedStart(*[TransformFromCopy(lines[i], w) for i, w in zip((4, 6), we)], lag_ratio=0.3)), run_time=2.6)
        self.play(FadeOut(VGroup(top, flab, lines, cmd, out, we, durs)), run_time=0.6)

        # 6. find: picks files, never opens them
        root = M("logs/", 26, BLUE_M).move_to([-5.6, 1.0, 0])
        names = ("gateway.log", "worker.log", "payments.log", "checkout.log", "notes.txt")
        ys = [2.4 - 0.75 * k for k in range(5)]
        fi = VGroup()
        for n, y in zip(names, ys):
            ic = fileicon().move_to([-3.6, y, 0])
            fi.add(VGroup(ic, M(n, 22, WHITE).next_to(ic, RIGHT, buff=0.2)))
        trunk = Line([-5.6, 0.75, 0], [-5.6, ys[-1], 0], stroke_width=2, color=GREY_D)
        twigs = VGroup(*[Line([-5.6, y, 0], [-3.9, y, 0], stroke_width=2, color=GREY_D) for y in ys])
        trunk.put_start_and_end_on([-4.6, ys[0] + 0.0, 0], [-4.6, ys[-1], 0])
        twigs = VGroup(*[Line([-4.6, y, 0], [-3.9, y, 0], stroke_width=2, color=GREY_D) for y in ys])
        root.move_to([-4.6, ys[0] + 0.75, 0])
        self.beat("Sometimes the question is about files, not lines. Which logs mention this request at all?",
                  FadeIn(root), Create(trunk), Create(twigs), LaggedStart(*[FadeIn(f) for f in fi], lag_ratio=0.15), run_time=2.6)
        fcmd = M("$ find logs -name '*.log' -exec grep -l 7f3a9c {} +", 24, YELLOW_M).move_to([0, -3.3, 0])
        self.beat("find walks down through every folder under a starting point, and tests each file it meets.",
                  Write(fcmd[:21]), run_time=2.0)
        walker = Dot(radius=0.09, color=YELLOW_M).move_to(root.get_bottom() + DOWN * 0.05)
        marks = VGroup()
        self.add(walker)
        path_anims = []
        for k, f in enumerate(fi):
            ok = names[k].endswith(".log")
            mk = tick(ok, 0.16).next_to(f, RIGHT, buff=0.25)
            marks.add(mk)
        self.steps("Here the test is a name. Star dot log is a glob, so it is quoted. Each name that fits passes. notes.txt does not.",
                   (1.0, Indicate(fcmd[9:21], color=YELLOW_M, scale_factor=1.1)),
                   *[(0.5, walker.animate.move_to([-4.6, ys[k], 0]), Create(marks[k]), fi[k].animate.set_opacity(1 if names[k].endswith(".log") else 0.35)) for k in range(5)],
                   (0.3, FadeOut(walker)))
        note = T("find never opens a file: name, type, size, age", 24, GREY_B).move_to([2.6, 2.95, 0])
        self.beat("It never opens a file. It only looks at what it knows about each one: the name, the type, the size, and the age.",
                  FadeIn(note, shift=DOWN * 0.1), run_time=2.0)

        gb = mbox("grep -l 7f3a9c", GOLD_M, w=3.0, h=0.8, size=24).move_to([1.2, 0.9, 0])
        passed = VGroup(*[fi[k] for k in range(4)])
        fa = VGroup(*[Arrow(fi[k][1].get_right() + RIGHT * 0.55, gb.get_left(), buff=0.12, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.1) for k in range(4)])
        self.beat("Then -exec hands the list of paths to grep.",
                  Write(fcmd[21:]), FadeIn(gb), LaggedStart(*[GrowArrow(a) for a in fa], lag_ratio=0.15), run_time=2.4)
        res = VGroup(*[M(f"logs/{names[k]}", 22, TEAL_M) for k in range(4)]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([5.0, 0.9, 0])
        ra = Arrow(gb.get_right(), res.get_left(), buff=0.15, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.15)
        self.beat("grep reads every line of them, and -l prints only the names of files that match. All four. Four services touched this request.",
                  LaggedStart(*[travel(a, YELLOW_M, 0.7) for a in fa], lag_ratio=0.2), Succession(Wait(1.8), AnimationGroup(GrowArrow(ra), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in res], lag_ratio=0.2))), run_time=4.4)
        self.wait(0.5)
        self.play(FadeOut(VGroup(root, trunk, twigs, fi, marks, note, gb, fa, res, ra, fcmd)), run_time=0.6)

        # 7. recap
        rcp = VGroup(T("find picks files: by name, type, size or age", 30, BLUE_M),
                     T("grep picks lines: by a word or a pattern", 30, GOLD_M),
                     T("options answer questions: -c, -v, -o, -l", 30, TEAL_M),
                     T("quote every pattern; add -E for + and |", 30, YELLOW_M)).arrange(DOWN, buff=0.4)
        self.beat("find picks files, by name, type, size or age. grep picks lines, by a word or a pattern. Its options answer your questions. And quote every pattern.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.5), run_time=5.0)
        self.wait(1.0)
