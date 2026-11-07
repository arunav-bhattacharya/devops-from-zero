import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

IN_C, OUT_C, ERR_C = BLUE_M, TEAL_M, RED_M
# level of each of the 37 lines of the lab's app.log (I=INFO, W=WARN, E=ERROR, T=stack trace line)
LEVELS = "IIIIIWIEIIIIWEIIWIIETTIIWIIEIIIIIIIII"


def sarrow(a, b, color, sw=4):
    return Arrow(a, b, buff=0, stroke_width=sw, color=color, max_tip_length_to_length_ratio=0.14, max_stroke_width_to_length_ratio=10)


def label_by(arr, text, side=1, gap=0.12):
    """Place text beside an arrow's middle, on the left (side=1) or right (side=-1) of its direction."""
    s, e = arr.get_start(), arr.get_end()
    d = (e - s) / (np.linalg.norm(e - s) or 1)
    n = np.array([-d[1], d[0], 0]) * side
    ext = abs(n[0]) * text.width / 2 + abs(n[1]) * text.height / 2
    return text.move_to((s + e) / 2 + n * (gap + ext))


def fbox(name, color, w, h, size=22):
    """A file: outlined box with its name at the top inside."""
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3)
    r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.12), opacity=1)
    n = M(name, size, color).move_to(r.get_top() + DOWN * 0.3)
    return VGroup(r, n)


def lit(b, on=True, w=3, **kw):
    return b[0].animate(**kw).set_stroke(width=7 if on else w)


def late(a, b=1.0, f=smooth):
    """Rate function that waits until fraction a of the animation, then runs f until fraction b."""
    return lambda t: f(float(np.clip((t - a) / (b - a), 0, 1)))


def travel_behind(path, color, run_time):
    """Like travel(), but the dot passes behind boxes, as a line does when a program reads it."""
    d = Dot(radius=0.09, color=color).move_to(path.get_start()).set_z_index(-1)
    return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=linear, run_time=run_time), FadeOut(d, run_time=0.1))


class D05Pipes(VoiceScene):
    def construct(self):
        self.title_card("Pipes and the three streams", "how the shell wires programs together")

        # ---------- 1. three streams
        P = LEFT * 0.9
        prog = box("program", WHITE, w=2.8, h=2.2, size=34).move_to(P)
        self.beat("Every Linux program starts with three streams already open. A stream is just a flow of bytes.",
                  Create(prog[0]), Write(prog[1]), run_time=1.6)

        kb = box("keyboard", GREY_B, w=2.3, h=1.0, size=28).move_to(LEFT * 5.35)
        a_in = sarrow(kb.get_right() + RIGHT * 0.1, prog.get_left() + LEFT * 0.1, IN_C)
        l_in = M("0 stdin", 24, IN_C).next_to(a_in, UP, buff=0.14)
        self.beat("Stream zero is stdin. The program reads its input from there. By default, that is your keyboard.",
                  FadeIn(kb), GrowArrow(a_in), Write(l_in), Succession(Wait(1.2), travel(a_in, IN_C, 0.8)), run_time=2.4)

        y1, y2 = 0.5, -0.5
        px = prog.get_right()[0]
        scr = RoundedRectangle(corner_radius=0.15, width=4.4, height=2.2, stroke_color=GREY_B, stroke_width=3).move_to(RIGHT * 4.55)
        scr_l = T("screen", 26, GREY_B).next_to(scr, DOWN, buff=0.15)
        sx = scr.get_left()[0]
        a_out = sarrow([px + 0.1, y1, 0], [sx - 0.1, y1, 0], OUT_C)
        l_out = M("1 stdout", 24, OUT_C).next_to(a_out, UP, buff=0.14)
        self.beat("Stream one is stdout. The program writes its results there. By default, they go to your screen.",
                  Create(scr), FadeIn(scr_l), GrowArrow(a_out), Write(l_out), Succession(Wait(1.2), travel(a_out, OUT_C, 0.8)), run_time=2.4)

        a_err = sarrow([px + 0.1, y2, 0], [sx - 0.1, y2, 0], ERR_C)
        l_err = M("2 stderr", 24, ERR_C).next_to(a_err, DOWN, buff=0.14)
        self.beat("Stream two is stderr, for error messages. By default, that goes to your screen too.",
                  GrowArrow(a_err), Write(l_err), Succession(Wait(1.0), travel(a_err, ERR_C, 0.8)), run_time=2.2)

        fd = T("file descriptors: 0, 1, 2", 28, GREY_B).move_to(DOWN * 2.6)
        self.beat("Zero, one and two are called file descriptors. They are the small numbers a program uses for its open streams.",
                  FadeIn(fd, shift=UP * 0.15),
                  LaggedStart(*[Indicate(l[0], color=YELLOW_M, scale_factor=1.6) for l in (l_in, l_out, l_err)], lag_ratio=0.4), run_time=2.6)

        shell = mbox("shell", GREY_B, w=1.9, h=0.7, size=26).move_to(P + UP * 2.6)
        ports = [prog.get_left() + LEFT * 0.02, np.array([px, y1, 0]), np.array([px, y2, 0])]
        plugs = VGroup(*[Dot(radius=0.11, color=c).move_to(shell.get_bottom()) for c in (IN_C, OUT_C, ERR_C)])
        self.beat("The program does not open these three itself. It inherits them from the shell that started it.",
                  FadeOut(fd), FadeIn(shell, shift=DOWN * 0.2),
                  Succession(Wait(0.8), FadeIn(plugs, run_time=0.2),
                             AnimationGroup(*[p.animate.move_to(q) for p, q in zip(plugs, ports)], run_time=1.4),
                             FadeOut(plugs, run_time=0.3)), run_time=3.0)
        self.remove(*plugs)

        opts = ["a file", "another program", "screen"]
        cyc = [Succession(Wait(0.3), Transform(scr_l, T(o, 26, GREY_B).next_to(scr, DOWN, buff=0.15), run_time=0.5), Wait(0.6)) for o in opts]
        self.beat("The program just writes to stream one. It does not know if one leads to a screen, a file, or another program.",
                  Succession(*cyc), travel(a_out, OUT_C, 1.0), run_time=4.2)

        self.beat("So the shell can point a stream somewhere else before the program starts, and the program needs no change. Redirection and pipes both rely on this.",
                  Circumscribe(shell, color=YELLOW_M, buff=0.08), lit(prog), run_time=1.6)
        self.play(lit(prog, False), run_time=0.3)

        # ---------- 2. redirection
        CX = LEFT * 4.27 + UP * 3.4

        def cmd_text(s, colors=None):
            return M(s, 28, t2c=colors or {}, disable_ligatures=True).move_to(CX, aligned_edge=LEFT)

        cmd = cmd_text("$ ls app.log nosuch")
        lsname = M("ls", 40).move_to(prog[1])
        dimmed = VGroup(kb, a_in, l_in)
        self.beat("Let's try it. Run ls app.log nosuch. One of those files exists, and the other does not.",
                  FadeOut(shell), Write(cmd), Transform(prog[1], lsname), dimmed.animate.set_opacity(0.3), run_time=2.0)

        r_line = M("app.log", 22).move_to(scr.get_center() + UP * 0.5)
        e_line = M("No such file or directory", 20).move_to(scr.get_center() + DOWN * 0.5)
        self.beat("You get one result line and one error line. On screen they look alike, but they travel separately.",
                  Succession(travel(a_out, OUT_C, 0.8), FadeIn(r_line, run_time=0.3)),
                  Succession(Wait(0.5), travel(a_err, ERR_C, 0.8), FadeIn(e_line, run_time=0.3)), run_time=2.0)

        # > out.txt
        out = fbox("out.txt", OUT_C, 4.2, 1.45).move_to(RIGHT * 4.6 + UP * 2.2)
        slot1 = out[0].get_center() + UP * 0.02
        slot2 = out[0].get_center() + DOWN * 0.38
        cmd2 = cmd_text("$ ls app.log nosuch > out.txt", {"> out.txt": OUT_C})
        a_out2 = sarrow([px + 0.1, y1, 0], out[0].get_left() + LEFT * 0.1 + DOWN * 0.2, OUT_C)
        l_out2 = label_by(a_out2, M("1 stdout", 24, OUT_C), side=1)
        self.beat("Put a greater-than sign and a file name after the command. Before ls even starts, the shell points stdout at that file.",
                  FadeOut(VGroup(r_line, e_line)), TransformMatchingShapes(cmd, cmd2), FadeIn(out, shift=LEFT * 0.2),
                  Transform(a_out, a_out2), Transform(l_out, l_out2), run_time=2.4)
        cmd = cmd2

        f_r1 = M("app.log", 22).move_to(slot1)
        e_line = M("No such file or directory", 20).move_to(scr.get_center() + DOWN * 0.5)
        self.beat("The result goes into the file. The error still lands on your screen, because only stream one moved.",
                  Succession(travel(a_out, OUT_C, 0.9), FadeIn(f_r1, run_time=0.3)),
                  Succession(Wait(1.6), travel(a_err, ERR_C, 0.8), FadeIn(e_line, run_time=0.3), Indicate(e_line, color=RED_M)), run_time=3.6)

        cmd3 = cmd_text("$ ls app.log nosuch >> out.txt", {">> out.txt": OUT_C})
        f_r2 = M("app.log", 22).move_to(slot2)
        self.beat("One greater-than sign replaces what was in the file. Two of them add to the end, so a second run leaves two lines.",
                  FadeOut(e_line), TransformMatchingShapes(cmd, cmd3),
                  Succession(Wait(1.6), travel(a_out, OUT_C, 0.9), FadeIn(f_r2, shift=DOWN * 0.1, run_time=0.4)), run_time=3.4)
        cmd = cmd3

        # 2> /dev/null
        null = fbox("/dev/null", GREY_B, 2.4, 0.85).move_to(RIGHT * 4.55 + DOWN * 2.35)
        null[1].move_to(null[0])
        cmd4 = cmd_text("$ ls app.log nosuch > out.txt 2> /dev/null", {"> out.txt": OUT_C, "2> /dev/null": ERR_C})
        a_err2 = sarrow([px + 0.1, y2, 0], null[0].get_left() + LEFT * 0.1 + UP * 0.1, ERR_C)
        l_err2 = label_by(a_err2, M("2 stderr", 24, ERR_C), side=-1)
        self.beat("To move stream two instead, put a two right before the greater-than sign. Here it goes to /dev/null, a special file that throws away everything written to it.",
                  TransformMatchingShapes(cmd, cmd4), FadeIn(null, shift=LEFT * 0.2),
                  Transform(a_err, a_err2), Transform(l_err, l_err2), FadeOut(f_r2), run_time=2.6)
        cmd = cmd4

        ghost = M("No such file", 20, ERR_C).move_to(null[0])
        self.beat("Run it now. The result replaces the file, and the error simply disappears. The screen stays empty.",
                  Succession(travel(a_out, OUT_C, 0.9), Indicate(f_r1, color=OUT_C)),
                  Succession(Wait(0.4), travel(a_err, ERR_C, 0.9), FadeIn(ghost, run_time=0.2), ghost.animate.scale(0.05).set_opacity(0)),
                  Succession(Wait(2.4), Indicate(scr, color=GREY_B, scale_factor=1.03)), run_time=3.6)
        self.remove(ghost)

        # 2>&1
        cmd5 = cmd_text("$ ls app.log nosuch > out.txt 2>&1", {"> out.txt": OUT_C, "2>&1": ERR_C})
        a_err3 = sarrow([px + 0.1, y2, 0], out[0].get_left() + LEFT * 0.1 + DOWN * 0.5, ERR_C)
        f_e = M("No such file or directory", 20).move_to(slot2)
        self.beat("Or write two, greater-than, ampersand, one. Read it as: send two wherever one goes right now.",
                  TransformMatchingShapes(cmd, cmd5), FadeOut(null), FadeOut(l_err), Transform(a_err, a_err3), run_time=2.2)
        cmd = cmd5
        self.beat("Now both lines land in out.txt, and nothing reaches the screen.",
                  Succession(travel(a_out, OUT_C, 0.9), Indicate(f_r1, color=OUT_C)),
                  Succession(Wait(0.5), travel(a_err, ERR_C, 0.9), FadeIn(f_e, run_time=0.3)), run_time=2.4)

        # ---------- 3. pipes
        self.play(FadeOut(VGroup(cmd, prog, dimmed, a_out, l_out, a_err, scr, scr_l, out, f_r1, f_e)), run_time=0.8)

        Y = UP * 0.3
        pcmd = M("$ grep ERROR app.log | wc -l", 30).move_to(UP * 3.1)
        pcmd[17].set_color(YELLOW_M)
        grep = mbox("grep ERROR", GOLD_M, w=2.3, h=1.0, size=26).move_to(LEFT * 2.5 + Y)
        wc = mbox("wc -l", GOLD_M, w=1.7, h=1.0, size=26).move_to(RIGHT * 2.2 + Y)
        self.beat("Now, pipes. A pipe, written as a vertical bar, connects one program's stdout to the next program's stdin.",
                  Write(pcmd), FadeIn(grep, shift=UP * 0.15), FadeIn(wc, shift=UP * 0.15), run_time=2.0)

        gx, wx = grep.get_right()[0], wc.get_left()[0]
        tube = VGroup(Line([gx, Y[1] + 0.24, 0], [wx, Y[1] + 0.24, 0]), Line([gx, Y[1] - 0.24, 0], [wx, Y[1] - 0.24, 0]))
        tube.set_stroke(width=3).set_color_by_gradient(OUT_C, IN_C)
        tube_l = T("pipe: a buffer in memory", 24, GREY_B).move_to(tube.get_center() + UP * 1.0)
        self.beat("Take grep ERROR app.log, piped into wc -l. First, the shell creates the pipe, a small buffer that the operating system keeps in memory.",
                  Indicate(pcmd[17], color=YELLOW_M, scale_factor=1.8), Create(tube, rate_func=late(0.35)),
                  FadeIn(tube_l, shift=DOWN * 0.1, rate_func=late(0.5)), run_time=3.2)

        one = M("1", 26, OUT_C).next_to(tube, DOWN, buff=0.15).align_to(tube, LEFT).shift(RIGHT * 0.15)
        zero = M("0", 26, IN_C).next_to(tube, DOWN, buff=0.15).align_to(tube, RIGHT).shift(LEFT * 0.15)
        self.beat("It points grep's stdout at one end, and wc's stdin at the other. Then it starts both programs at the same moment.",
                  FadeIn(one, shift=UP * 0.1), FadeIn(zero, shift=UP * 0.1),
                  lit(grep, rate_func=late(0.6)), lit(wc, rate_func=late(0.6)), run_time=3.0)

        appf = fbox("app.log", GREY_B, 1.6, 1.5, size=24).move_to(LEFT * 6.0 + Y)
        n37 = T("37 lines", 24, GREY_B).move_to(appf[0].get_center() + DOWN * 0.25)
        a_f = sarrow(appf.get_right() + RIGHT * 0.08, grep.get_left() + LEFT * 0.08, GREY_B, sw=3)
        raw = ["2026-10-30T09:03:05Z INFO  checkout-api req=5f6a7b GET /api/pr...",
               "2026-10-30T09:04:30Z ERROR checkout-api req=8e9f0a database co...",
               "2026-10-30T09:04:31Z INFO  checkout-api req=8e9f0a retrying da..."]
        peek = VGroup(*[M(s, 20, GREY_B, t2c={"ERROR": ERR_C, "INFO": WHITE}) for s in raw]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        peek_box = SurroundingRectangle(peek, buff=0.25, corner_radius=0.1, stroke_color=GREY_D, stroke_width=2)
        peekg = VGroup(peek_box, peek).move_to(DOWN * 2.75)
        self.beat("Here is app.log. It has thirty-seven lines, like these.",
                  lit(grep, False), lit(wc, False), FadeIn(appf), FadeIn(n37), GrowArrow(a_f),
                  FadeIn(peekg, shift=UP * 0.15), run_time=1.8)

        # the stream of lines: every bar is one line of app.log
        x0, xg, xw = appf.get_center()[0], grep.get_center()[0], wc.get_center()[0]
        col = {"I": GREY_B, "W": GOLD_M, "E": ERR_C, "T": GREY_D}
        bars = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.4, height=0.2, stroke_width=0).set_fill(col[c], 0) for c in LEVELS])
        clock = ValueTracker(0)
        v, dt = 2.6, 0.22

        def upd_for(i, err):
            def upd(m):
                t = clock.get_value() - i * dt
                x = x0 + v * t
                end = xw if err else xg
                vis = 0 < t and x < end
                m.move_to([min(x, end), Y[1], 0]).set_fill(opacity=1 if vis else 0)
            return upd
        for i, (b, c) in enumerate(zip(bars, LEVELS)):
            b.set_z_index(-1)
            b.add_updater(upd_for(i, c == "E"), call_updater=True)
        self.add(bars)
        errs = [b for b, c in zip(bars, LEVELS) if c == "E"]
        cnt_l = T("count:", 26, GREY_B)
        cnt = M("0", 32, YELLOW_M)
        cntg = VGroup(cnt_l, cnt).arrange(RIGHT, buff=0.18).next_to(wc, DOWN, buff=0.45)
        cpos = cnt.get_center()
        cnt.n = 0

        def count_upd(m):
            n = sum(1 for b in errs if b.get_center()[0] >= xw - 0.01 and clock.get_value() > 0)
            if n != m.n:
                m.become(M(str(n), 32, YELLOW_M).move_to(cpos)); m.n = n
        cnt.add_updater(count_upd)
        total = (len(LEVELS) - 1) * dt + (xw - x0) / v + 0.2
        half = total * 0.5
        self.beat("grep reads the lines one at a time, and passes on only the lines that contain ERROR. The other lines stop there.",
                  clock.animate(rate_func=linear).set_value(half), FadeIn(cntg), run_time=100)
        self.beat("wc counts each line as it arrives. Lines keep flowing while both programs work. Nobody waits for the whole file.",
                  clock.animate(rate_func=linear).set_value(total), run_time=100)
        for b in bars:
            b.clear_updaters()
        cnt.clear_updaters()
        self.remove(bars)

        scr2 = RoundedRectangle(corner_radius=0.12, width=1.7, height=1.0, stroke_color=GREY_B, stroke_width=3).move_to(RIGHT * 5.5 + Y)
        scr2_l = T("screen", 24, GREY_B).next_to(scr2, UP, buff=0.15)
        a_s = sarrow(wc.get_right() + RIGHT * 0.08, scr2.get_left() + LEFT * 0.08, OUT_C, sw=3)
        four = M("4", 40, YELLOW_M).move_to(scr2)
        self.beat("When the input ends, wc prints its count to its own stdout, your screen. Four.",
                  Create(scr2), FadeIn(scr2_l), GrowArrow(a_s), Succession(Wait(1.6), travel(a_s, OUT_C, 0.6), FadeIn(four, scale=1.5)), run_time=3.2)

        self.beat("Neither program knows the other exists. grep writes to stream one, wc reads stream zero, and the shell joined the two.",
                  Succession(Indicate(one, color=OUT_C, scale_factor=1.8), Indicate(zero, color=IN_C, scale_factor=1.8), Indicate(tube, color=YELLOW_M, scale_factor=1.04)),
                  run_time=3.0)

        gb = grep.get_bottom()
        door = VMobject(stroke_color=ERR_C, stroke_width=4).set_points_as_corners(
            [gb + DOWN * 0.08, [gb[0], -1.3, 0], [scr2.get_center()[0], -1.3, 0], scr2.get_bottom() + DOWN * 0.1])
        tip = Triangle(fill_color=ERR_C, fill_opacity=1, stroke_width=0).scale(0.11).rotate(0).move_to(scr2.get_bottom() + DOWN * 0.16)
        door_l = M("2 stderr skips the pipe", 22, ERR_C).next_to([0.9, -1.3, 0], DOWN, buff=0.15)
        self.beat("Only stdout goes into a pipe. Error messages leave on stderr, skip the pipe, and go straight to your screen.",
                  FadeOut(peekg), Create(door), FadeIn(tip), FadeIn(door_l),
                  Succession(Wait(2.2), travel(door, ERR_C, 1.4)), run_time=3.8)

        belt = Line(appf.get_center(), scr2.get_left())
        idea = T("an assembly line: parts move one at a time, everyone works at once", 26, GREY_B).move_to(DOWN * 2.9)
        dots = [Succession(Wait(0.4 * k), travel_behind(belt, GREY_B, 2.6)) for k in range(7)]
        self.beat("Think of an assembly line. Parts move along the belt one at a time, and every worker works at once. Broken parts leave by a side door, and the next worker never sees them.",
                  FadeIn(idea, shift=UP * 0.15), *dots, Succession(Wait(3.5), travel(door, ERR_C, 1.4)), run_time=5.6)

        recap = VGroup(M("0 stdin  1 stdout  2 stderr", 24), M(">  a file", 24, OUT_C), M("|  the next program", 24, YELLOW_M)).arrange(RIGHT, buff=0.9).move_to(DOWN * 2.9)
        self.beat("Every program gets stdin, stdout and stderr from the shell. A greater-than sign points a stream at a file, and a pipe joins stdout to the next program's stdin.",
                  FadeOut(idea), Write(recap), run_time=3.0)
        self.wait(1.2)
