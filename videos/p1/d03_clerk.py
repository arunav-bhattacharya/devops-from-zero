import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bls -l -h\b", "L S dash L, dash H"), (r"\bls -lh\b", "L S dash L H"), (r"\bls -l\b", "L S dash L"), (r"\bls\b", "L S"),
            (r"\brm -rf\b", "R M dash R F"), (r"\brm -r\b", "R M dash R"), (r"\brm -i\b", "R M dash I"), (r"\brm\b", "R M"),
            (r"\*\.log\b", "star dot log"), (r"\*\.txt\b", "star dot text"), (r"\bzsh\b", "Z shell"),
            (r"\bnotes\.txt\b", "notes dot text"), (r"/usr/bin/ls\b", "slash user slash bin slash L S"),
            (r"\bserver/var/log\b", "server slash var slash log"), (r"\bPATH\b", "path"), (r"\bpwd\b", "P W D"),
            (r"\bcd\b", "C D"), (r"(?<!\w)-l\b", "dash L"), (r"(?<!\w)-i\b", "dash I"), (r"(?<!\w)-f\b", "dash F"), (r"\.secret\.txt\b", "dot secret dot text"),
            (r"\breport\.txt\b", "report dot text"), (r"\bapp\.log\b", "app dot log"), (r"\baccess\.log\b", "access dot log")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color, s=1.0):
    head = Circle(radius=0.24, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    body = RoundedRectangle(corner_radius=0.28, width=0.82, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), 1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(body, head).scale(s)


def words_of(tm, line):
    """Split a Text mobject into one VGroup per space-separated word (Text drops spaces from its glyphs)."""
    out, i = VGroup(), 0
    for w in line.split(" "):
        out.add(VGroup(*tm[i:i + len(w)]))
        i += len(w)
    return out


def wchip(w, color, size=26):
    return chip(w, color, size, mono=True)


class D03Clerk(VoiceScene):
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

    def countdown(self, where, label="pause and guess"):
        c = chip(label, YELLOW_M, size=26).move_to(where)
        self.play(FadeIn(c, scale=0.9), run_time=0.4)
        for n in ("3", "2", "1"):
            d = T(n, 34, YELLOW_M).next_to(c, RIGHT, buff=0.35)
            self.play(FadeIn(d, run_time=0.15))
            self.wait(0.6)
            self.remove(d)
        self.play(FadeOut(c), run_time=0.3)

    def note(self, line):
        bar = RoundedRectangle(corner_radius=0.12, width=11.6, height=0.95, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, opacity=1).move_to([0, 2.75, 0])
        p = M("$", 30, GREY_B).move_to(bar.get_left() + RIGHT * 0.4)
        t = M(line, 30).next_to(p, RIGHT, buff=0.3)
        return bar, p, t

    def argrow(self, prog, args, y=-1.5, pc=GOLD_M, ac=TEAL_M, x=0.0):
        pb = mbox(prog, pc, size=26, h=0.75)
        cells = VGroup(*[wchip(a, ac, 26) for a in args]).arrange(RIGHT, buff=0.25)
        lab = T("arguments", 26, ac).next_to(cells, LEFT, buff=0.3)
        row = VGroup(pb, VGroup(lab, cells)).arrange(RIGHT, buff=0.7).move_to([x, y, 0])
        return pb, lab, cells

    def construct(self):
        self.title_card("What the shell does with your line", "a note, a clerk, and a worker")

        # ---------- 1. the shy question
        bar, p, t = self.note("rm *.log")
        self.beat("A folder holds two log files. You type rm *.log to delete them. Simple enough.",
                  FadeIn(bar), FadeIn(p), AddTextLetterByLetter(t), run_time=2.4)
        q = T("what does the rm program actually receive?", 32, YELLOW_M).move_to(UP * 0.8)
        opts = VGroup(T("the text *.log, which rm matches itself", 28, GREY_B), T("two file names", 28, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(q, DOWN, buff=0.45)
        self.beat("But here's a question most people never ask. What does rm actually receive? Does rm even know what a star means?",
                  FadeIn(q, shift=UP * 0.1), Succession(Wait(2.4), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.5)), run_time=4.4)
        self.countdown(DOWN * 1.9)
        self.beat("Hold on to your guess. We'll come back to it.",
                  FadeOut(VGroup(q, opts, bar, p, t)), run_time=1.6)

        # ---------- 2. the office: window, clerk, worker
        win = RoundedRectangle(corner_radius=0.12, width=3.2, height=2.6, stroke_color=GREY_B, stroke_width=3).move_to(LEFT * 3.2 + DOWN * 0.1)
        winl = T("the window", 26, GREY_B).next_to(win, UP, buff=0.2)
        you = person(WHITE).next_to(win, LEFT, buff=0.55)
        clerk = person(BLUE_M).move_to(win)
        clerkl = T("the clerk", 26, BLUE_M).next_to(win, DOWN, buff=0.25)
        self.beat("Picture your first day in a big office building. At a small window in the lobby sits a clerk who reads each note you pass through.",
                  FadeIn(you, shift=RIGHT * 0.2), Create(win), FadeIn(winl), Succession(Wait(2.6), AnimationGroup(FadeIn(clerk), FadeIn(clerkl))), run_time=4.2)
        room = RoundedRectangle(corner_radius=0.12, width=3.0, height=2.6, stroke_color=GOLD_M, stroke_width=3).move_to(RIGHT * 3.9 + DOWN * 0.1)
        worker = person(GOLD_M).move_to(room)
        workl = T("a worker", 26, GOLD_M).next_to(room, DOWN, buff=0.25)
        lk = DashedLine(win.get_right(), room.get_left(), dash_length=0.12, stroke_width=2, color=GREY_B)
        self.beat("The clerk doesn't do most jobs. It knows which worker does each one, calls them, and passes back what they say.",
                  Create(room), FadeIn(worker), FadeIn(workl), Succession(Wait(2.4), Create(lk)), run_time=4.2)
        m1 = T("terminal", 30, GREY_B).move_to(winl)
        m2 = T("shell: zsh, bash", 30, BLUE_M).move_to(clerkl)
        m3 = T("command: /usr/bin/ls", 30, GOLD_M).move_to(workl)
        self.beat("Let's map it. The terminal is the window: the app you type into.", Transform(winl, m1), run_time=1.4)
        self.beat("The shell is the clerk: the program inside the window that reads your line and starts other programs. zsh on your Mac, usually bash on Linux servers.",
                  Transform(clerkl, m2), run_time=1.8)
        self.beat("A command is the worker, usually a program file on disk. ls, which lists files, is the file /usr/bin/ls. The clerk finds it through your PATH.",
                  Transform(workl, m3), run_time=2.0)
        bi = T("cd: a job the clerk does itself", 24, BLUE_M).move_to(DOWN * 2.6 + LEFT * 3.2)
        self.beat("A few commands, like cd, are jobs the clerk does itself. Those are called builtins.", FadeIn(bi, shift=UP * 0.1), run_time=1.6)
        self.beat("And here's the thing about this clerk. Brilliant at reading. Hopeless at guessing. It does exactly what the note says.",
                  Indicate(clerk, color=BLUE_M), run_time=1.6)
        office = VGroup(win, winl, you, clerk, clerkl, room, worker, workl, lk, bi)
        self.play(FadeOut(office), run_time=0.7)

        # ---------- 3. how the clerk cuts a note into words
        line = "ls -l -h server/var/log"
        bar, p, t = self.note(line)
        self.beat("So let's watch the clerk read one note: ls -l -h server/var/log.",
                  FadeIn(bar), FadeIn(p), AddTextLetterByLetter(t), run_time=2.4)
        ws = words_of(t, line)
        chips = VGroup(*[wchip(w, BLUE_M) for w in line.split(" ")]).arrange(RIGHT, buff=0.45).move_to([0, 1.2, 0])
        sl = T("1. split the line on spaces", 26, BLUE_M).next_to(chips, DOWN, buff=0.3)
        self.beat("Before any program starts, the clerk takes the note apart. The shell splits the line on spaces, into words.",
                  LaggedStart(*[TransformFromCopy(w, c) for w, c in zip(ws, chips)], lag_ratio=0.25), FadeIn(sl), run_time=2.6)
        pb, lab, cells = self.argrow("ls", line.split(" ")[1:])
        self.beat("The first word is the program to run.", chips[0].animate.set_color(GOLD_M), TransformFromCopy(chips[0], pb), run_time=1.4)
        self.beat("Every other word becomes an argument: a plain piece of text, handed to that program.",
                  LaggedStart(*[TransformFromCopy(c, d) for c, d in zip(chips[1:], cells)], lag_ratio=0.3), FadeIn(lab), run_time=2.4)
        dk = T("the shell has no idea what -l means. ls decides.", 26, GREY_B).move_to(DOWN * 2.55)
        self.beat("Notice: the shell doesn't know what -l means. It only cuts the line into pieces. The program decides what each piece means.",
                  FadeIn(dk, shift=UP * 0.1), Succession(Wait(2.4), Indicate(pb, color=GOLD_M)), run_time=3.6)
        opt = VGroup(M("-l  -a", 24), T("short options", 24, GREY_B), M("-lh = -l -h", 24), T("grouped", 24, GREY_B),
                     M("--all", 24), T("long options", 24, GREY_B)).arrange_in_grid(rows=3, cols=2, buff=(0.4, 0.18), col_alignments="lr")
        opt.move_to(RIGHT * 3.2 + DOWN * 2.75)
        self.beat("By habit, words that start with a dash are options, or flags. Short ones are one letter and can be grouped. Long ones are words after two dashes.",
                  FadeOut(dk), Succession(Wait(1.6), LaggedStart(*[FadeIn(o) for o in opt], lag_ratio=0.25)), run_time=5.0)
        self.play(FadeOut(VGroup(chips, sl, pb, lab, cells, opt)), run_time=0.5)

        # ---------- 4. break it: a space in a name
        line2 = "ls my notes.txt"
        t2 = M(line2, 30).next_to(p, RIGHT, buff=0.3)
        self.play(Transform(t, t2), run_time=0.6)
        chips2 = VGroup(*[wchip(w, BLUE_M) for w in line2.split(" ")]).arrange(RIGHT, buff=0.45).move_to([0, 1.2, 0])
        self.beat("Now a file called my notes.txt, with a space in its name. You type ls my notes.txt. How many files does ls go looking for?",
                  FadeIn(chips2[0]), run_time=1.6)
        self.countdown(DOWN * 0.2)
        pb2, lab2, cells2 = self.argrow("ls", ["my", "notes.txt"], ac=RED_M)
        errs = T("two files asked for, two errors", 28, RED_M).move_to([0, -2.6, 0])
        self.steps("Two. The clerk splits on that space, so ls asks for a file called my, and a file called notes.txt. Two errors.",
                   (0.8, FadeIn(chips2[1:])), (1.0, FadeIn(pb2), FadeIn(lab2), TransformFromCopy(chips2[1:], cells2)), (1.4, Wait(1.4)),
                   (0.8, FadeIn(errs, shift=UP * 0.1)))
        self.beat("The clerk did a perfect job. Of exactly what the note said.", Indicate(pb2[1], color=GOLD_M), run_time=1.4)
        line3 = 'ls "my notes.txt"'
        t3 = M(line3, 30).next_to(p, RIGHT, buff=0.3)
        chips3 = VGroup(wchip("ls", BLUE_M), wchip('"my notes.txt"', BLUE_M)).arrange(RIGHT, buff=0.45).move_to([0, 1.2, 0])
        pb3, lab3, cells3 = self.argrow("ls", ["my notes.txt"])
        self.beat("Quote the name, or put a backslash before the space, and it stays one word. Better still, keep spaces out of your file names.",
                  FadeOut(errs), Transform(t, t3), Transform(chips2, chips3), Transform(VGroup(pb2, lab2), VGroup(pb3, lab3)), Transform(cells2, cells3), run_time=2.0)
        self.play(FadeOut(VGroup(chips2, pb2, lab2, cells2)), run_time=0.5)

        # ---------- 5. wildcards: the clerk fetches the names
        oct_ = T('"shred every report from October"', 30, PURPLE_M).move_to(UP * 1.2)
        self.beat("Now a different kind of note. Suppose it says: shred every report from October.",
                  FadeOut(VGroup(bar, p, t)), FadeIn(oct_, shift=DOWN * 0.1), run_time=1.6)
        lst = VGroup(M("oct-03.pdf", 26, PURPLE_M), M("oct-17.pdf", 26, PURPLE_M), M("oct-29.pdf", 26, PURPLE_M)).arrange(RIGHT, buff=0.5).move_to(DOWN * 0.3)
        hear = T("the worker never hears the word October", 26, GREY_B).next_to(lst, DOWN, buff=0.45)
        self.beat("The clerk walks to the drawer, writes down every October report's name, and hands the worker that list. The worker never hears the word October.",
                  Succession(Wait(2.0), LaggedStart(*[FadeIn(l, shift=DOWN * 0.1) for l in lst], lag_ratio=0.3)), Succession(Wait(4.2), FadeIn(hear)), run_time=5.6)
        self.play(FadeOut(VGroup(oct_, lst, hear)), run_time=0.5)

        files = ["access.log", "app.log", "events.jsonl", "logs", "pods.json", "server", "start-lab.sh"]
        fl = VGroup(*[M(f, 24) for f in files]).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        fr = RoundedRectangle(corner_radius=0.12, width=fl.width + 0.7, height=fl.height + 0.9, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, opacity=1)
        fl.move_to(fr).shift(DOWN * 0.15)
        fh = M("/work", 22, GREY_B).move_to(fr.get_top() + DOWN * 0.28)
        folder = VGroup(fr, fh, fl).move_to([4.7, -0.55, 0])
        LX = -1.5
        bar, p, t = self.note("echo *.log")
        self.beat("A pattern for file names works the same way. In the lab, type echo *.log. The star matches any run of characters, even none.",
                  FadeIn(bar), FadeIn(p), AddTextLetterByLetter(t), FadeIn(folder, shift=LEFT * 0.2), run_time=2.4)
        chips4 = VGroup(wchip("echo", BLUE_M), wchip("*.log", YELLOW_M)).arrange(RIGHT, buff=0.45).move_to([LX, 1.2, 0])
        self.beat("The shell splits the line, as before. But one word is a pattern.",
                  Succession(FadeIn(chips4, run_time=0.7), Indicate(chips4[1], color=YELLOW_M, run_time=0.8)), run_time=1.6)
        scan = SurroundingRectangle(fl[0], color=YELLOW_M, buff=0.06, stroke_width=2)
        self.steps("So, before the program starts, the clerk reads the folder, and keeps the names that fit.",
                   (0.6, Create(scan)), *[(0.28, scan.animate.move_to(fl[i]).stretch_to_fit_width(fl[i].width + 0.12)) for i in range(1, 7)],
                   (0.5, FadeOut(scan), fl[0].animate.set_color(GREEN_M), fl[1].animate.set_color(GREEN_M), *[fl[i].animate.set_opacity(0.35) for i in range(2, 7)]))
        mm1, mm2 = wchip("access.log", GREEN_M), wchip("app.log", GREEN_M)
        VGroup(mm1, mm2).arrange(RIGHT, buff=0.25).next_to(chips4[0], RIGHT, buff=0.45)
        sl2 = T("2. swap the pattern for the matching names, sorted", 26, YELLOW_M).move_to([LX, 0.35, 0])
        self.beat("Then it puts them, sorted, in place of the pattern.",
                  FadeOut(chips4[1]), TransformFromCopy(fl[0], mm1), TransformFromCopy(fl[1], mm2), FadeIn(sl2), run_time=1.8)
        pb4, lab4, cells4 = self.argrow("echo", ["access.log", "app.log"], ac=GREEN_M, x=LX)
        out = M("access.log app.log", 26).move_to([LX, -2.6, 0])
        self.steps("The program never sees the pattern, only the names. And echo just prints the arguments it receives.",
                   (1.2, FadeIn(pb4), FadeIn(lab4), TransformFromCopy(VGroup(mm1, mm2), cells4)), (1.8, Wait(1.8)), (0.8, FadeIn(out, shift=UP * 0.1)))
        self.beat("So, back to our opening question. What did rm receive? Not a star. Two file names.",
                  Indicate(cells4, color=GREEN_M), run_time=2.0)
        nm = T("a pattern like *.log is called a glob, or wildcard", 26, GREY_B).move_to([LX, -3.3, 0])
        self.beat("A pattern like this is called a glob, or a wildcard. Now you know who does the matching. The clerk, not the worker.",
                  FadeIn(nm, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(nm, out, pb4, lab4, cells4, sl2)), run_time=0.5)

        # quotes, hidden files, no match
        t5 = M('echo "*.log"', 30).next_to(p, RIGHT, buff=0.3)
        q5 = VGroup(wchip("echo", BLUE_M), wchip('"*.log"', GREY_B)).arrange(RIGHT, buff=0.45).move_to([LX, 1.2, 0])
        o5 = M("*.log", 26).move_to([LX, -0.6, 0])
        self.steps("Quotes switch globbing off: in quotes, echo prints the star itself. And a star skips hidden files, whose names start with a dot.",
                   (0.8, Transform(t, t5), FadeOut(VGroup(chips4[0], mm1, mm2)), FadeIn(q5), fl.animate.set_opacity(1).set_color(WHITE)),
                   (1.4, Wait(1.4)), (0.8, FadeIn(o5, shift=UP * 0.1)))
        t6 = M("echo *.txt", 30).next_to(p, RIGHT, buff=0.3)
        q6 = VGroup(wchip("echo", BLUE_M), wchip("*.txt", YELLOW_M)).arrange(RIGHT, buff=0.45).move_to([LX, 1.2, 0])
        o6 = VGroup(T("bash:", 26, BLUE_M), M("*.txt", 26)).arrange(RIGHT, buff=0.3)
        o7 = VGroup(T("zsh:", 26, PURPLE_M), M("no matches found: *.txt", 24, PURPLE_M)).arrange(RIGHT, buff=0.3)
        VGroup(o6, o7).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([LX, -1.2, 0])
        self.steps("And when nothing matches? In bash the pattern passes on unchanged, as if the clerk found no October reports and handed over the words themselves.",
                   (0.8, Transform(t, t6), FadeOut(o5), Transform(q5, q6)), (1.0, Wiggle(fl)), (2.6, Wait(2.6)), (0.8, FadeIn(o6, shift=UP * 0.1)))
        self.beat("In zsh, the shell refuses to run the line at all. You will see the zsh way on your Mac, and the bash way on every server.",
                  FadeIn(o7, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(q5, o6, o7, folder)), run_time=0.5)

        # ---------- 6. the shredder: one stray space
        line8 = "rm -r old logs"
        t8 = M(line8, 30).next_to(p, RIGHT, buff=0.3)
        self.beat("Now the dangerous one, the shredder. You mean to delete one folder called old logs, with a space in its name. You type rm -r old logs.",
                  Transform(t, t8), run_time=2.0)
        chips8 = VGroup(*[wchip(w, BLUE_M) for w in line8.split(" ")]).arrange(RIGHT, buff=0.45).move_to([0, 1.2, 0])
        pb8, lab8, cells8 = self.argrow("rm", ["-r", "old", "logs"], ac=RED_M)
        self.steps("You already know what the clerk does. It splits on the space, so rm gets two folders, old and logs.",
                   (1.0, FadeIn(chips8)), (0.8, Wait(0.8)), (1.2, FadeIn(pb8), FadeIn(lab8), TransformFromCopy(chips8[1:], cells8)),
                   (0.5, Indicate(cells8[1], color=RED_M)), (0.5, Indicate(cells8[2], color=RED_M)))
        gone = T("both deleted. rm has no trash and no undo.", 28, RED_M).move_to([0, -2.55, 0])
        self.beat("It deletes both. rm has no trash and no undo. The Mac's Trash belongs to Finder. rm just removes the names.",
                  FadeIn(gone, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(chips8, pb8, lab8, cells8, gone)), run_time=0.5)
        habits = VGroup(
            VGroup(M("$ pwd", 26, GREEN_M), T("where am I?", 26, GREY_B)).arrange(RIGHT, buff=0.5),
            VGroup(M("$ echo rm -r old logs", 26, GREEN_M), T("what will rm get?", 26, GREY_B)).arrange(RIGHT, buff=0.5),
            VGroup(M("$ rm -i *.log", 26, GREEN_M), T("ask before each file", 26, GREY_B)).arrange(RIGHT, buff=0.5),
            VGroup(M("rm -rf", 26, RED_M), T("read it twice: -f switches off every question", 26, GREY_B)).arrange(RIGHT, buff=0.5))
        grid = VGroup(*[x for h in habits for x in h]).arrange_in_grid(rows=4, cols=2, buff=(0.5, 0.32), col_alignments="rl").move_to(DOWN * 0.3)
        habits = VGroup(*[VGroup(grid[2 * k], grid[2 * k + 1]) for k in range(4)])
        fit(habits, 12.4)
        self.beat("So, the guardrails. Run pwd, to see where you are. Put echo in front, to see exactly what rm will get.",
                  FadeIn(habits[0], shift=UP * 0.1), Succession(Wait(2.0), FadeIn(habits[1], shift=UP * 0.1)), run_time=3.6)
        self.beat("While you learn, add -i, so rm asks before each file. And read any rm -rf line twice. The -f part switches off every question.",
                  FadeIn(habits[2], shift=UP * 0.1), Succession(Wait(2.4), FadeIn(habits[3], shift=UP * 0.1)), run_time=4.0)
        r = T("rm has no undo. Look before you delete.", 32, YELLOW_M).move_to(DOWN * 2.75)
        self.beat("rm has no undo. Look before you delete.", FadeIn(r, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(habits, r, bar, p, t)), run_time=0.5)

        # ---------- 7. moral, recap, check
        rc = VGroup(T("1. split the line on spaces", 30, BLUE_M), T("2. swap patterns for real names", 30, YELLOW_M),
                    T("3. hand the worker a plain list", 30, GOLD_M)).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([0.6, 0.6, 0])
        self.beat("So that's the whole path of one note. The clerk splits it on spaces, swaps patterns for real names, and hands the worker a plain list.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in rc], lag_ratio=0.6), run_time=5.0)
        self.beat("The program only ever sees what the clerk wrote down. So when in doubt, ask echo to read the clerk's list aloud.",
                  Indicate(rc[2], color=GOLD_M), run_time=1.6)
        self.play(FadeOut(rc), run_time=0.6)
        cq = VGroup(T("A folder holds", 30), M("report.txt", 28), T("and", 30), M(".secret.txt", 28)).arrange(RIGHT, buff=0.2).move_to(UP * 1.9)
        cq2 = VGroup(T("What does", 30), M("echo *.txt", 28), T("print in bash?", 30)).arrange(RIGHT, buff=0.2).next_to(cq, DOWN, buff=0.25)
        opts = VGroup(M("report.txt .secret.txt", 26, GREY_B), M("report.txt", 26, GREY_B), M("*.txt", 26, GREY_B), T("an error about hidden files", 26, GREY_B))
        opts.arrange(DOWN, aligned_edge=LEFT, buff=0.24).next_to(cq2, DOWN, buff=0.5)
        self.beat("A quick check. A folder holds report.txt and .secret.txt. What does echo *.txt print, in bash?",
                  FadeIn(cq), FadeIn(cq2), Succession(Wait(4.0), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3)), run_time=6.2)
        self.countdown(DOWN * 3.0, "pause and think")
        self.beat("Just report.txt. A star at the start of a glob skips names that begin with a dot, so the clerk leaves the hidden file off the list.",
                  opts[1].animate.set_color(GREEN_M), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 1], run_time=1.6)
        self.wait(1.2)
