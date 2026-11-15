import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bls -l -h\b", "L S dash L, dash H"), (r"\bls -lh\b", "L S dash L H"), (r"\bls\b", "L S"), (r"\brm -r\b", "R M dash R"),
            (r"\brm\b", "R M"), (r"\*\.log\b", "star dot log"), (r"\*\.txt\b", "star dot text"), (r"\bzsh\b", "Z shell"),
            (r"\bnotes\.txt\b", "notes dot text"), (r"\bArray<String>", "array of string"), (r"/usr/bin/ls\b", "slash user slash bin slash L S"),
            (r"\bserver/var/log\b", "server slash var slash log"), (r"\bPATH\b", "path")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def words_of(tm, line):
    """Split a Text mobject into one VGroup per space-separated word (Text drops spaces from its glyphs)."""
    out, i = VGroup(), 0
    for w in line.split(" "):
        out.add(VGroup(*tm[i:i + len(w)]))
        i += len(w)
    return out


def wchip(w, color, size=26):
    return chip(w, color, size, mono=True)


class D03ShellLine(VoiceScene):
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

    def term(self, line):
        bar = RoundedRectangle(corner_radius=0.12, width=12.4, height=0.95, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, opacity=1).move_to([0, 2.9, 0])
        p = M("$", 30, GREY_B).move_to(bar.get_left() + RIGHT * 0.4)
        t = M(line, 30).next_to(p, RIGHT, buff=0.3)
        return bar, p, t

    def argrow(self, prog, args, y=-1.4, pc=GOLD_M, ac=TEAL_M):
        pb = mbox(prog, pc, size=26, h=0.75)
        cells = VGroup(*[wchip(a, ac, 24) for a in args]).arrange(RIGHT, buff=0.25)
        idx = VGroup(*[M(str(i), 20, GREY_B).next_to(c, UP, buff=0.12) for i, c in enumerate(cells)])
        lab = M("args", 22, ac).next_to(cells, LEFT, buff=0.3)
        row = VGroup(pb, VGroup(lab, cells)).arrange(RIGHT, buff=0.8)
        row.move_to([0, y, 0])
        idx = VGroup(*[M(str(i), 20, GREY_B).next_to(c, UP, buff=0.12) for i, c in enumerate(cells)])
        return pb, lab, cells, idx

    def construct(self):
        self.title_card("What the shell does with your line", "words, arguments and wildcards")

        # 1. three parts
        tw = RoundedRectangle(corner_radius=0.15, width=12.8, height=6.6, stroke_color=GREY_D, stroke_width=2).move_to([0, -0.2, 0])
        twl = T("terminal: the window", 24, GREY_B).move_to(tw.get_corner(UL) + RIGHT * 1.7 + DOWN * 0.35)
        self.beat("People say the command line for three different things. The terminal is the window.",
                  Create(tw), FadeIn(twl), run_time=2.0)
        sh = box("shell", BLUE_M, w=2.4, h=0.9, size=30).move_to([-3.0, 0.2, 0])
        shl = T("bash on Linux, zsh on a Mac", 22, BLUE_M).next_to(sh, DOWN, buff=0.25)
        self.beat("The shell is the program running inside it. It reads the line you type, and starts other programs.",
                  FadeIn(sh), FadeIn(shl), run_time=1.8)
        pg = mbox("/usr/bin/ls", GOLD_M, size=26, h=0.9).move_to([3.2, 0.2, 0])
        pa = edge_arrow(sh, pg)
        pgl = T("a command is a program file", 22, GOLD_M).next_to(pg, DOWN, buff=0.25)
        self.beat("And a command is usually a program file on disk. ls is the file /usr/bin/ls. The shell finds it by searching the folders in PATH.",
                  GrowArrow(pa), FadeIn(pg), FadeIn(pgl), run_time=2.4)
        self.play(FadeOut(VGroup(tw, twl, sh, shl, pg, pa, pgl)), run_time=0.6)

        # 2. splitting into words
        line = "ls -l -h server/var/log"
        bar, p, t = self.term(line)
        self.beat("Here is what happens between Enter and the program. Take this line.",
                  FadeIn(bar), FadeIn(p), AddTextLetterByLetter(t), run_time=2.0)
        ws = words_of(t, line)
        chips = VGroup(*[wchip(w, BLUE_M) for w in line.split(" ")]).arrange(RIGHT, buff=0.45).move_to([0, 1.1, 0])
        sl = T("the shell splits on spaces", 22, BLUE_M).next_to(chips, DOWN, buff=0.3)
        self.beat("Before any program starts, the shell takes it apart. It splits the line on spaces, into words.",
                  LaggedStart(*[TransformFromCopy(w, c) for w, c in zip(ws, chips)], lag_ratio=0.25), FadeIn(sl), run_time=2.6)
        pb, lab, cells, idx = self.argrow("ls", line.split(" ")[1:])
        self.beat("The first word is the program to run.",
                  chips[0].animate.set_color(GOLD_M), TransformFromCopy(chips[0], pb), run_time=1.4)
        self.beat("Every other word becomes an argument: a plain string handed to that program.",
                  LaggedStart(*[TransformFromCopy(c, d) for c, d in zip(chips[1:], cells)], lag_ratio=0.3), FadeIn(lab), FadeIn(idx), run_time=2.4)
        kt = M("fun main(args: Array<String>)", 24, GREY_B).move_to([0, -2.7, 0])
        self.beat("You know this shape from Kotlin: fun main, with args, an array of strings. The shell builds args, and the program decides what each one means.",
                  Write(kt), Succession(Wait(2.2), Indicate(VGroup(lab, cells), color=TEAL_M, scale_factor=1.05)), run_time=3.8)
        opt = T("starts with a dash: an option", 22, GREY_B).next_to(cells[0:2], DOWN, buff=0.3)
        self.beat("By habit, arguments that start with a dash are options, also called flags. The last one is a folder to work on.",
                  FadeIn(opt), Indicate(cells[0], color=WHITE), Indicate(cells[1], color=WHITE), Succession(Wait(2.4), Indicate(cells[2], color=TEAL_M)), run_time=3.6)
        self.play(FadeOut(VGroup(chips, sl, pb, lab, cells, idx, kt, opt)), run_time=0.5)

        # 3. a space in a file name
        line2 = "ls my notes.txt"
        t2 = M(line2, 30).next_to(p, RIGHT, buff=0.3)
        self.play(Transform(t, t2), run_time=0.6)
        chips2 = VGroup(*[wchip(w, BLUE_M) for w in line2.split(" ")]).arrange(RIGHT, buff=0.45).move_to([0, 1.1, 0])
        pb2, lab2, cells2, idx2 = self.argrow("ls", ["my", "notes.txt"])
        errs = T("two files asked for, two errors", 24, RED_M).move_to([0, -2.75, 0])
        self.steps("Because spaces split words, a file name with a space in it causes trouble. ls my notes.txt asks for two files, my and notes.txt, and prints two errors.",
                   (1.0, FadeIn(chips2)), (1.6, Wait(1.6)), (1.0, FadeIn(pb2), FadeIn(lab2), TransformFromCopy(chips2[1:], cells2), FadeIn(idx2)),
                   (1.4, Wait(1.4)), (0.8, FadeIn(errs, shift=UP * 0.1)))
        line3 = 'ls "my notes.txt"'
        t3 = M(line3, 30).next_to(p, RIGHT, buff=0.3)
        chips3 = VGroup(wchip("ls", BLUE_M), wchip('"my notes.txt"', BLUE_M)).arrange(RIGHT, buff=0.45).move_to([0, 1.1, 0])
        pb3, lab3, cells3, idx3 = self.argrow("ls", ["my notes.txt"])
        self.beat("Quote the name, and it stays one word. Better still, keep spaces out of the file names you create.",
                  FadeOut(errs), Transform(t, t3), Transform(chips2, chips3), Transform(VGroup(pb2, lab2), VGroup(pb3, lab3)),
                  Transform(cells2, cells3), Transform(idx2, idx3), run_time=2.0)
        self.play(FadeOut(VGroup(chips2, pb2, lab2, cells2, idx2)), run_time=0.5)

        # 4. wildcards
        files = ["access.log", "app.log", "events.jsonl", "logs", "pods.json", "server", "start-lab.sh"]
        fl = VGroup(*[M(f, 22) for f in files]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        fr = RoundedRectangle(corner_radius=0.12, width=fl.width + 0.7, height=fl.height + 0.9, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, opacity=1)
        fl.move_to(fr).shift(DOWN * 0.15)
        fh = M("/work", 22, GREY_B).move_to(fr.get_top() + DOWN * 0.28)
        folder = VGroup(fr, fh, fl).move_to([4.9, -0.85, 0])
        line4 = "echo *.log"
        t4 = M(line4, 30).next_to(p, RIGHT, buff=0.3)
        self.beat("Now a wildcard, also called a glob. In the lab, type echo star dot log. The star matches any run of characters.",
                  Transform(t, t4), FadeIn(folder, shift=LEFT * 0.2), run_time=2.0)
        LX = -1.6
        chips4 = VGroup(wchip("echo", BLUE_M), wchip("*.log", YELLOW_M)).arrange(RIGHT, buff=0.45).move_to([LX, 1.1, 0])
        self.beat("The shell splits the line, as before. But it sees a pattern.",
                  Succession(FadeIn(chips4, run_time=0.7), Indicate(chips4[1], color=YELLOW_M, run_time=0.8)), run_time=1.6)
        scan = SurroundingRectangle(fl[0], color=YELLOW_M, buff=0.06, stroke_width=2)
        self.steps("Before the program starts, the shell reads the folder, and keeps the names that fit.",
                   (0.6, Create(scan)), *[(0.28, scan.animate.move_to(fl[i]).stretch_to_fit_width(fl[i].width + 0.12)) for i in range(1, 7)],
                   (0.5, FadeOut(scan), fl[0].animate.set_color(GREEN_M), fl[1].animate.set_color(GREEN_M),
                    *[fl[i].animate.set_opacity(0.35) for i in range(2, 7)]))
        m1, m2 = wchip("access.log", GREEN_M), wchip("app.log", GREEN_M)
        VGroup(m1, m2).arrange(RIGHT, buff=0.25).next_to(chips4[0], RIGHT, buff=0.45)
        self.beat("Then it puts them, sorted, in place of the pattern.",
                  FadeOut(chips4[1]), TransformFromCopy(fl[0], m1), TransformFromCopy(fl[1], m2), run_time=1.8)
        pb4, lab4, cells4, idx4 = self.argrow("echo", ["access.log", "app.log"], ac=GREEN_M)
        VGroup(pb4, lab4, cells4, idx4).shift(RIGHT * (LX - VGroup(pb4, lab4, cells4).get_x()))
        out = M("access.log app.log", 24, WHITE).move_to([LX, -2.75, 0])
        self.steps("The program never sees the pattern, only the names. And echo just prints the arguments it receives.",
                   (1.2, FadeIn(pb4), FadeIn(lab4), TransformFromCopy(VGroup(m1, m2), cells4), FadeIn(idx4)), (1.8, Wait(1.8)), (0.8, FadeIn(out, shift=UP * 0.1)))
        prev = T("a free preview: put echo in front of a risky command", 22, YELLOW_M).move_to([LX, -3.45, 0])
        self.beat("That makes echo a good preview. Put it in front of a risky command, and it prints the line the program would get.",
                  FadeIn(prev, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(prev, out, pb4, lab4, cells4, idx4)), run_time=0.5)

        # quotes, and no match
        t5 = M('echo "*.log"', 30).next_to(p, RIGHT, buff=0.3)
        q5 = VGroup(wchip("echo", BLUE_M), wchip('"*.log"', GREY_B)).arrange(RIGHT, buff=0.45).move_to([LX, 1.1, 0])
        o5 = M("*.log", 24).move_to([LX, -1.4, 0])
        self.steps("Quotes switch globbing off. echo, with star dot log in quotes, prints the star itself.",
                   (0.8, Transform(t, t5), FadeOut(VGroup(chips4[0], m1, m2)), FadeIn(q5), fl.animate.set_opacity(1).set_color(WHITE)),
                   (1.6, Wait(1.6)), (0.8, FadeIn(o5, shift=UP * 0.1)))
        t6 = M("echo *.txt", 30).next_to(p, RIGHT, buff=0.3)
        q6 = VGroup(wchip("echo", BLUE_M), wchip("*.txt", YELLOW_M)).arrange(RIGHT, buff=0.45).move_to([LX, 1.1, 0])
        o6 = VGroup(T("bash:", 24, BLUE_M), M("*.txt", 24)).arrange(RIGHT, buff=0.3)
        o7 = VGroup(T("zsh:", 24, PURPLE_M), M("no matches found: *.txt", 24, PURPLE_M)).arrange(RIGHT, buff=0.3)
        VGroup(o6, o7).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([LX, -1.8, 0])
        self.steps("And when nothing matches? Here bash and zsh disagree. In bash, the pattern passes on unchanged, so echo prints star dot text.",
                   (0.8, Transform(t, t6), FadeOut(o5), Transform(q5, q6)), (1.0, Wiggle(fl)), (2.0, Wait(2.0)), (0.8, FadeIn(o6, shift=UP * 0.1)))
        self.beat("In zsh, the shell refuses to run the line. You will see the zsh way on your Mac, and the bash way on every server.",
                  FadeIn(o7, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(q5, o6, o7, folder)), run_time=0.5)

        # 5. the stray space
        line8 = "rm -r old logs"
        t8 = M(line8, 30).next_to(p, RIGHT, buff=0.3)
        self.beat("Now the most common mistake. One stray space is enough. Say you type rm -r old logs.",
                  Transform(t, t8), run_time=1.6)
        chips8 = VGroup(*[wchip(w, BLUE_M) for w in line8.split(" ")]).arrange(RIGHT, buff=0.45).move_to([0, 1.1, 0])
        pb8, lab8, cells8, idx8 = self.argrow("rm", ["-r", "old", "logs"], ac=RED_M)
        self.steps("The shell splits on that space. So rm gets two folders, old and logs.",
                   (1.2, FadeIn(chips8)), (0.8, Wait(0.8)), (1.2, FadeIn(pb8), FadeIn(lab8), TransformFromCopy(chips8[1:], cells8), FadeIn(idx8)),
                   (0.6, Indicate(cells8[1], color=RED_M)), (0.6, Indicate(cells8[2], color=RED_M)))
        gone = T("both deleted. rm has no trash and no undo.", 26, RED_M).move_to([0, -2.75, 0])
        self.beat("It deletes both. rm has no trash and no undo, and nothing brings them back.",
                  FadeIn(gone, shift=UP * 0.1), run_time=1.6)
        safe = VGroup(M("$ pwd", 24, GREEN_M), M("$ echo rm -r old logs", 24, GREEN_M)).arrange(RIGHT, buff=0.8).move_to([0, -3.45, 0])
        self.beat("So before any delete, run pwd, preview the line with echo, and read it once more.",
                  FadeIn(safe, shift=UP * 0.1), run_time=1.8)

        # 6. recap
        self.play(FadeOut(VGroup(chips8, pb8, lab8, cells8, idx8, gone, safe)), run_time=0.5)
        rc = VGroup(T("1. split the line on spaces", 28, BLUE_M), T("2. expand the wildcards", 28, YELLOW_M),
                    T("3. start the program with the words", 28, GOLD_M)).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([0, -0.4, 0])
        self.beat("So the shell rewrites your line before the program starts. It splits on spaces, expands the wildcards, and only then runs the program. rm only ever sees file names.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rc], lag_ratio=0.6), run_time=5.0)
        self.wait(1.2)
