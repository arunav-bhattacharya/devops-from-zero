import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bnames\.txt\.new\b", "names dot text dot new"), (r"\bnames\.txt\b", "names dot text"), (r"\bapp\.log\b", "app dot log"),
            (r"\baccess\.log\b", "access dot log"), (r"\breport\.txt\b", "report dot text"), (r"\bbackup\.log\b", "backup dot log"),
            (r"\./backup\.sh\b", "dot slash backup dot S H"), (r"/dev/null\b", "dev null"), (r"\buniq -c\b", "unique dash C"),
            (r"\buniq\b", "unique"), (r"\bsort -rn\b", "sort dash R N"), (r"\bhead -n 5\b", "head dash N five"), (r"\bwc -l\b", "W C dash L"),
            (r"\bls\b", "L S"), (r"\bawk\b", "awk"), (r"2>&1", "two, greater than, ampersand one"), (r"2>", "two greater than"),
            (r">>", "double greater than"), (r"(?<=\s)>(?=\s)", "greater than"), (r"\$1\b", "dollar one"),
            (r"\b203\.0\.113\.7\b", "203 dot 0 dot 113 dot 7")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def desk(name, color, w=2.0):
    return mbox(name, color, w=w, h=0.85, size=24)


class D05Chutes(VoiceScene):
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

    def construct(self):
        self.title_card("Trays and chutes", "how one program's output becomes the next one's input")

        # ---------- 1. the manager at nine
        ask = VGroup(T('"Traffic jumped overnight.', 32), T('Who is calling us, and what is failing?', 32), T('A short report by ten, please."', 32)).arrange(DOWN, buff=0.18).move_to(UP * 1.4)
        logf = VGroup(mbox("access.log", GREY_B, size=26, h=0.85), T("238 lines from the web server", 26, GREY_B)).arrange(RIGHT, buff=0.4).move_to(DOWN * 1.0)
        self.beat("Nine in the morning. Your manager stops at your desk. Traffic to the shop jumped overnight. Who is calling us, and what is failing? A short report by ten, please.",
                  LaggedStart(*[FadeIn(a, shift=UP * 0.1) for a in ask], lag_ratio=0.6), run_time=5.0)
        self.beat("You have the web server's logbook, a few hundred lines long. Last time, grep could pick out lines. But the manager wants counts and rankings.",
                  FadeIn(logf, shift=UP * 0.1), run_time=2.4)
        sp = T("copy it all into a spreadsheet and count by hand?", 28, GREY_B).move_to(DOWN * 2.5)
        self.beat("The first idea is to copy everything into a spreadsheet and count by hand. It works. By lunchtime. Tomorrow.",
                  FadeIn(sp, shift=UP * 0.1), run_time=2.0)
        self.beat("There is a much better way, and it starts with how paper moves between desks in our office.",
                  FadeOut(VGroup(ask, logf, sp)), run_time=1.6)

        # ---------- 2. three trays
        d = desk("program", WHITE, w=2.6).move_to(UP * 0.4)
        inn = chip("in-tray", BLUE_M, 26).next_to(d, LEFT, buff=1.3)
        out = chip("out-tray", GREEN_M, 26).next_to(d, RIGHT, buff=1.3)
        err = chip("complaints", RED_M, 26).next_to(d, DOWN, buff=1.1)
        a_in = edge_arrow(inn, d, BLUE_M)
        a_out = edge_arrow(d, out, GREEN_M)
        a_err = edge_arrow(d, err, RED_M)
        self.beat("Every desk in the building has three trays. Work comes in through the in-tray. Finished pages go in the out-tray.",
                  FadeIn(d), Succession(Wait(1.4), AnimationGroup(FadeIn(inn), GrowArrow(a_in))), Succession(Wait(2.8), AnimationGroup(FadeIn(out), GrowArrow(a_out))), run_time=4.4)
        self.beat("And complaints, like this page is unreadable, go in a third tray, so they never get mixed up with the good work.",
                  FadeIn(err), GrowArrow(a_err), run_time=2.0)
        n0 = VGroup(M("stdin", 26, BLUE_M), M("0", 26, BLUE_M)).arrange(RIGHT, buff=0.25).next_to(inn, UP, buff=0.25)
        n1 = VGroup(M("stdout", 26, GREEN_M), M("1", 26, GREEN_M)).arrange(RIGHT, buff=0.25).next_to(out, UP, buff=0.25)
        n2 = VGroup(M("stderr", 26, RED_M), M("2", 26, RED_M)).arrange(RIGHT, buff=0.25).next_to(err, RIGHT, buff=0.35)
        self.beat("Every Linux program has the same three trays. Each one is a stream, a flow of bytes. Standard input, number zero, is where it reads.",
                  Succession(Wait(3.6), FadeIn(n0, shift=DOWN * 0.1)), run_time=4.4)
        self.beat("Standard output, number one, is where it writes its results. Standard error, number two, is where it writes its complaints.",
                  FadeIn(n1, shift=DOWN * 0.1), Succession(Wait(2.4), FadeIn(n2, shift=LEFT * 0.1)), run_time=3.6)
        scr = VGroup(T("keyboard", 24, GREY_B).next_to(inn, DOWN, buff=0.25), T("screen", 24, GREY_B).next_to(out, DOWN, buff=0.25),
                     T("screen", 24, GREY_B).next_to(n2, DOWN, buff=0.15).align_to(n2, LEFT))
        self.beat("By default, input is your keyboard, and both outputs go to your screen. Here is the key part. The program doesn't set up its trays. The shell that starts it does.",
                  LaggedStart(*[FadeIn(s) for s in scr], lag_ratio=0.4), Succession(Wait(4.0), Indicate(d[1], color=WHITE)), run_time=6.0)
        self.beat("A program writes to tray one the same way, whether tray one leads to the screen, to a file, or to another program. So the shell can point a tray somewhere else, and the program never knows.",
                  Wiggle(a_out), run_time=1.6)

        # ---------- 3. redirection, and the guess
        fileb = mbox("note.txt", GREEN_M, size=24, h=0.8).move_to(out)
        cm = M("$ echo hi > note.txt", 28).move_to(UP * 3.0)
        self.beat("Pointing a tray at a file is called redirection. echo hi, greater than, note dot text. The shell opens the file, points tray one at it, and then starts echo.",
                  Write(cm), FadeOut(scr[1]), Succession(Wait(3.2), ReplacementTransform(out, fileb)), run_time=5.2)
        forms = VGroup(VGroup(M(">  file", 26, GREEN_M), T("replace what is in it", 24, GREY_B)).arrange(RIGHT, buff=0.35),
                       VGroup(M(">> file", 26, GREEN_M), T("add to the end", 24, GREY_B)).arrange(RIGHT, buff=0.35),
                       VGroup(M("2> /dev/null", 26, RED_M), T("throw complaints in the bin", 24, GREY_B)).arrange(RIGHT, buff=0.35))
        forms.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(LEFT * 3.4 + DOWN * 2.6)
        self.beat("A single greater than replaces what was in the file. A double one adds to the end. And two, greater than, dev null, sends complaints to a special file that throws everything away, like a bin by the door.",
                  LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in forms], lag_ratio=0.9), run_time=7.0)
        self.play(FadeOut(VGroup(d, inn, fileb, err, a_in, a_out, a_err, n0, n1, n2, scr[0], scr[2], forms, cm)), run_time=0.6)

        names = VGroup(M("cara", 26), M("ben", 26), M("ana", 26)).arrange(DOWN, buff=0.15)
        nf = RoundedRectangle(corner_radius=0.12, width=2.4, height=1.8, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.1), 1)
        nfl = M("names.txt", 24, GOLD_M).next_to(nf, UP, buff=0.15)
        names.move_to(nf)
        nfile = VGroup(nf, nfl, names).move_to(LEFT * 3.6 + DOWN * 0.3)
        cm2 = M("$ sort names.txt > names.txt", 28).move_to(UP * 2.8)
        self.beat("Now a guess. You want to sort a file in place, so you type: sort names.txt, greater than, names.txt. What is in the file afterwards?",
                  FadeIn(nfile), Write(cm2), run_time=2.4)
        self.countdown(RIGHT * 2.8 + DOWN * 0.3)
        st = desk("sort", TEAL_M).move_to(RIGHT * 2.8 + DOWN * 0.3)
        o1 = T("1. the shell opens names.txt for writing: it is emptied", 26, GREY_B).move_to(DOWN * 2.3)
        o2 = T("2. only then does sort start, and reads an empty file", 26, GREY_B).next_to(o1, DOWN, buff=0.2)
        self.steps("Nothing. The file is empty. Watch the order. The shell sets up the trays before the program starts. Opening the file for writing empties it.",
                   (1.6, Wait(1.6)), (0.6, FadeIn(o1)), (0.8, FadeOut(names)), (0.4, nf.animate.set_stroke(RED_M)))
        a_rd = edge_arrow(nfile, st, GREY_B)
        self.steps("Only then does sort start. It reads the file, finds nothing, and writes nothing back.",
                   (0.8, FadeIn(st), GrowArrow(a_rd)), (0.6, FadeIn(o2)), (0.6, travel(a_rd, GREY_B, 0.6)))
        self.beat("The shell is very efficient. It cleared the desk before the worker even sat down.", Indicate(nf, color=RED_M), run_time=1.6)
        rule = T("> empties the file before the command starts. Never redirect into the file you are reading.", 26, YELLOW_M).move_to(DOWN * 3.25)
        fit(rule, 12.6)
        fix = M("$ sort names.txt > names.txt.new && mv names.txt.new names.txt", 24, GREEN_M).move_to(UP * 2.2)
        fit(fix, 12.6)
        self.beat("So the rule: a single greater than empties the file before the command starts. Never redirect into the file you are reading. Write to a new file, then move it into place.",
                  FadeIn(rule, shift=UP * 0.1), Succession(Wait(4.4), FadeIn(fix, shift=DOWN * 0.1)), run_time=6.0)
        self.play(FadeOut(VGroup(nfile, cm2, st, a_rd, o1, o2, rule, fix)), run_time=0.6)

        # ---------- 4. the chute: a pipe
        g = desk("grep ERROR", GOLD_M, w=2.6).move_to(LEFT * 3.0 + UP * 0.4)
        w_ = desk("wc -l", TEAL_M, w=2.0).move_to(RIGHT * 3.0 + UP * 0.4)
        ch = edge_arrow(g, w_, GREEN_M)
        chl = T("a chute: out-tray straight into in-tray", 26, GREEN_M).next_to(ch, UP, buff=0.3)
        cm3 = M("$ grep ERROR app.log | wc -l", 28).move_to(UP * 2.8)
        self.beat("A more useful place to send a tray is another desk. Imagine a chute, from one worker's out-tray straight into the next worker's in-tray.",
                  FadeIn(g), FadeIn(w_), Succession(Wait(2.6), AnimationGroup(GrowArrow(ch), FadeIn(chl))), run_time=4.6)
        res = M("4", 34, GREEN_M).next_to(w_, RIGHT, buff=0.5)
        self.steps("That chute is the pipe, the vertical bar. grep picks the error lines, the pipe drops them into wc, and wc counts them. Four.",
                   (1.0, Write(cm3)), (0.6, travel(ch, GREEN_M, 0.6)), (0.6, travel(ch, GREEN_M, 0.6)), (0.6, FadeIn(res, scale=1.3)))
        ers = chip("complaints", RED_M, 24).next_to(g, DOWN, buff=1.0)
        a_e = edge_arrow(g, ers, RED_M)
        scrn = T("straight to your screen", 24, GREY_B).next_to(ers, RIGHT, buff=0.3)
        self.beat("Notice, only tray one goes down the chute. Complaints skip it and land on your screen, which is exactly what they are for.",
                  GrowArrow(a_e), FadeIn(ers), FadeIn(scrn), run_time=2.0)
        self.beat("Neither worker knows the other exists. Each one just reads its in-tray, and fills its out-tray. Programs like that, which read lines, keep or change some, and write lines, are called filters.",
                  Indicate(g[1], color=GOLD_M), Succession(Wait(1.0), Indicate(w_[1], color=TEAL_M)), run_time=2.4)
        self.play(FadeOut(VGroup(g, w_, ch, chl, cm3, res, ers, a_e, scrn)), run_time=0.6)

        # ---------- 5. build the report, one desk at a time
        specs = [("awk", "awk '{print $1}'", BLUE_M), ("sort", "sort", TEAL_M), ("uniq -c", "uniq -c", GOLD_M), ("sort -rn", "sort -rn", TEAL_M), ("head", "head -n 5", PURPLE_M)]
        D = VGroup(*[desk(n, c, w=2.0) for n, _, c in specs]).arrange(RIGHT, buff=0.62).move_to(UP * 1.6)
        C = VGroup(*[edge_arrow(D[i], D[i + 1], GREEN_M, buff=0.06) for i in range(4)])
        cmdline = M("$ awk '{print $1}' access.log", 26).move_to(UP * 2.95).align_to(D, LEFT)
        panel_tl = np.array([D.get_left()[0] + 0.2, 0.55, 0])

        def panel(lines, color=WHITE):
            g_ = VGroup(*[M(l, 24, color) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            return g_.move_to(panel_tl, aligned_edge=UL)

        aw = D[0].copy().move_to(D[0])
        self.beat("Now the manager's report. We'll build it the way you always should: one desk at a time, looking at the output after each step.",
                  run_time=None)
        p1 = panel(["203.0.113.7", "10.0.0.2", "198.51.100.23", "203.0.113.99", "..."])
        self.beat("Desk one is awk, a small tool for columns. It reads a table one row at a time. Dollar one means the first column, and in access.log that is the client's IP address, the number that identifies a computer on a network.",
                  FadeIn(D[0]), Write(cmdline), Succession(Wait(5.4), FadeIn(p1, shift=DOWN * 0.1)), run_time=7.6)
        side = T("238 lines, one IP each", 26, GREY_B).move_to(RIGHT * 3.6 + DOWN * 0.5)
        self.beat("One IP per request. 238 lines.", FadeIn(side), run_time=1.2)

        # break: uniq without sort
        u = desk("uniq -c", GOLD_M, w=2.0).move_to(D[1])
        cu = edge_arrow(D[0], u, GREEN_M, buff=0.06)
        cmdl2 = M("$ awk '{print $1}' access.log | uniq -c", 26).move_to(cmdline, aligned_edge=LEFT)
        self.beat("We want a count per IP. There is a tool for counting repeated lines: uniq, with dash C. Let's drop it straight in.",
                  Transform(cmdline, cmdl2), FadeIn(u), GrowArrow(cu), run_time=2.0)
        p2 = panel(["1 203.0.113.7", "1 10.0.0.2", "1 198.51.100.23", "1 203.0.113.99", "..."], GOLD_M)
        self.steps("And every count is one. Well. That's not the report we wanted.",
                   (0.6, travel(cu, GREEN_M, 0.6)), (0.6, ReplacementTransform(p1, p2)))
        mem = T("uniq only compares each line with the line just before it", 26, GOLD_M).move_to(RIGHT * 0.8 + DOWN * 2.6)
        self.beat("Here is why. uniq merges repeated lines only when they sit right next to each other. It remembers just the line before. That is what keeps it fast on huge files.",
                  FadeIn(mem, shift=UP * 0.1), run_time=2.4)
        self.beat("It is the colleague who only remembers the last person who walked past. The same visitor came back sixty times, but never twice in a row.",
                  Indicate(u[1], color=GOLD_M), run_time=1.8)
        self.beat("So the point is: put the same IPs next to each other first. That is a job for sort.",
                  FadeOut(mem), run_time=1.4)
        cmdl3 = M("$ awk '{print $1}' access.log | sort | uniq -c", 26).move_to(cmdline, aligned_edge=LEFT)
        p3 = panel(["18 10.0.0.2", "12 192.0.2.101", "37 192.0.2.15", "44 198.51.100.23", "7 198.51.100.77",
                    "21 198.51.100.8", "29 203.0.113.42", "61 203.0.113.7", "9 203.0.113.99"], GOLD_M)
        self.steps("Insert sort before uniq. Now identical IPs sit together, and uniq can count them.",
                   (0.8, Transform(cmdline, cmdl3), u.animate.move_to(D[2]), FadeOut(cu)), (0.6, FadeIn(D[1]), GrowArrow(C[0]), GrowArrow(C[1])),
                   (0.6, travel(C[0], GREEN_M, 0.4)), (0.4, travel(C[1], GREEN_M, 0.4)), (0.6, FadeOut(side), ReplacementTransform(p2, p3)))
        tx = T("sort orders text, so 10.0.0.2 comes first", 24, GREY_B).move_to(RIGHT * 3.6 + DOWN * 0.9)
        self.beat("Nine IPs, each with a real count. And notice, sort orders text, character by character, so 10.0.0.2 comes first.",
                  FadeIn(tx), run_time=1.8)
        cmdl4 = M("$ ... | sort | uniq -c | sort -rn | head -n 5", 26).move_to(cmdline, aligned_edge=LEFT)
        p4 = panel(["61 203.0.113.7", "44 198.51.100.23", "37 192.0.2.15", "29 203.0.113.42", "21 198.51.100.8"], PURPLE_M)
        self.steps("Now rank them. sort dash R N sorts the counts as numbers, largest first. And head keeps the top five.",
                   (0.8, Transform(cmdline, cmdl4), FadeOut(tx)), (0.6, FadeIn(D[3]), GrowArrow(C[2])), (0.6, FadeIn(D[4]), GrowArrow(C[3])),
                   (1.0, Succession(*[travel(c, GREEN_M, 0.25) for c in C])), (0.6, ReplacementTransform(p3, p4)))
        top = T("one client sent 61 of the 238 requests", 28, YELLOW_M).move_to(RIGHT * 2.8 + DOWN * 0.4)
        self.beat("There is your first answer. One client sent 61 of the 238 requests.", FadeIn(top, shift=LEFT * 0.1), Indicate(p4[0], color=YELLOW_M), run_time=2.0)
        save = VGroup(M("> report.txt", 26, GREEN_M), T("then", 24, GREY_B), M(">> report.txt", 26, GREEN_M), T("for the next answer", 24, GREY_B)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.6)
        fit(save, 12.4)
        self.beat("Send it to report dot text with a single greater than. Then add the next answer, the failing pages, with a double one. Use a single one twice by mistake, and the first answer is gone.",
                  FadeIn(save, shift=UP * 0.1), run_time=2.6)
        self.play(FadeOut(VGroup(top, save)), run_time=0.4)

        # ---------- 6. guardrails
        g1 = fit(T("build it one step at a time, and look at each output", 28, YELLOW_M), 7.4).move_to(DOWN * 1.1 + RIGHT * 2.4)
        self.beat("Notice how we got here. One desk at a time, looking at the output after each step. That is how we caught uniq in the act, instead of hunting for the broken step at the end.",
                  FadeIn(g1), run_time=2.4)
        self.play(FadeOut(g1), run_time=0.3)
        g2 = T("only one machine's files: hundreds of servers need a central log store", 26, GREY_B).move_to(DOWN * 2.6)
        fit(g2, 12.4)
        self.beat("And the honest limit. These tools read the files on one machine. That is enough for this report. For hundreds of servers, you need a central place for logs, which comes much later in the course.",
                  FadeIn(g2, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(VGroup(g2, p4, D, C, u, cmdline)), run_time=0.6)

        # ---------- 7. moral, check
        m = VGroup(T("three trays: 0 in, 1 out, 2 complaints", 30, WHITE), T("the shell points them before the program starts", 28, GREY_B),
                   T("a pipe is a chute from one out-tray to the next in-tray", 28, GREEN_M)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        self.beat("So, the moral of the story. Every program has three trays. The shell points them, at the screen, a file, or the next desk, before the program starts. And a pipe is just a chute from one out-tray to the next in-tray. Small filters, chained, turn raw lines into an answer.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in m], lag_ratio=0.9), run_time=8.0)
        self.play(FadeOut(m), run_time=0.5)
        cq = VGroup(M("./backup.sh > backup.log", 28), T("but its errors still show on the screen.", 30)).arrange(RIGHT, buff=0.3).move_to(UP * 1.9)
        fit(cq, 12.6)
        cq2 = T("Which line sends both trays into the log?", 30).next_to(cq, DOWN, buff=0.25)
        opts = VGroup(M("./backup.sh 2>&1 > backup.log", 26, GREY_B), M("./backup.sh > backup.log 2>&1", 26, GREY_B),
                      M("./backup.sh | backup.log", 26, GREY_B), M("./backup.sh >> backup.log", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(cq2, DOWN, buff=0.5)
        self.beat("A quick check. A job runs backup, with its output sent to backup dot log, but its error messages still appear on the screen. Read two, greater than, ampersand one, as: send tray two wherever tray one goes right now. Which line fixes it?",
                  FadeIn(cq), FadeIn(cq2), Succession(Wait(6.4), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3)), run_time=9.0)
        self.countdown(DOWN * 3.05, "pause and think")
        self.beat("The second one. The shell reads redirections left to right. First tray one points at the file, then tray two follows it there.",
                  opts[1].animate.set_color(GREEN_M), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 1], run_time=1.6)
        self.wait(1.2)
