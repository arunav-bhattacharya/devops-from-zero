import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\b7f3a9c\b", "seven F three A nine C"), (r"\bapp\.log\b", "app dot log"), (r"\bgrep -c\b", "grep dash C"),
            (r"\bgrep -i\b", "grep dash I"), (r"\bgrep -w\b", "grep dash W"), (r"\bgrep -q\b", "grep dash Q"),
            (r"(?<!\w)-E\b", "dash E"), (r"(?<!\w)-i\b", "dash I"), (r"(?<!\w)-c\b", "dash C"), (r"(?<!\w)-w\b", "dash W"),
            (r"(?<!\w)-o\b", "dash O"), (r"(?<!\w)-v\b", "dash V"), (r"(?<!\w)-q\b", "dash Q"),
            (r"\becho \$\?", "echo dollar question mark"), (r"\$\?", "dollar question mark"),
            (r"\bERROR\|WARN\b", "ERROR bar WARN"), (r"\[0-9\]\+ms", "zero to nine, plus, M S"), (r"\[0-9\]", "zero to nine"),
            (r"\bms\$", "M S dollar"), (r"\b1200ms\b", "1200 M S"), (r"\b2900ms\b", "2900 M S"), (r"\bms\b", "M S"),
            (r"\*\.log\b", "star dot log"), (r"\blogs/\*\.log\b", "logs slash star dot log"), (r"\\d\b", "backslash D"),
            (r"\bgrep\b", "grep")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


PAGE = [
    (6, "WARN  req=2c3d4e slow query took 1200ms"),
    (7, "INFO  req=5f6a7b GET /api/products 200 18ms"),
    (8, "ERROR req=8e9f0a database connection refused"),
    (9, "INFO  req=8e9f0a retrying database connection"),
    (10, "INFO  req=8e9f0a database connection restored"),
    (11, "INFO  req=b52d18 GET /healthz 200 3ms"),
    (12, "INFO  req=7f3a9c POST /api/checkout started"),
    (13, "WARN  req=7f3a9c answered slowly: 2900ms"),
    (14, "ERROR req=7f3a9c timeout after 3000ms"),
    (15, "INFO  req=7f3a9c POST /api/checkout 504 6012ms"),
    (16, "INFO  req=3b4c5d GET /api/orders/1001 200 22ms"),
    (17, "WARN  req=6e7f8a retrying after error"),
    (18, "INFO  req=6e7f8a POST /api/checkout 200 812ms"),
    (19, "INFO  req=c63e29 GET /healthz 200 2ms"),
    (20, "ERROR req=9d0e1f NullPointerException"),
]
LEVEL_C = {"INFO": GREY_B, "WARN": GOLD_M, "ERROR": RED_M}


def glyphs(tm, line, sub, start=0):
    """Glyphs of the first occurrence of sub in line (Text drops spaces, so count non-space characters)."""
    k = line.index(sub, start)
    a = len(line[:k].replace(" ", ""))
    return VGroup(*tm[a:a + len(sub.replace(" ", ""))])


class D04Highlighter(VoiceScene):
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
        self.title_card("When grep says nothing", "a highlighter, a shape, and a silence that lies")

        # ---------- 1. the phone call
        ref = chip("customer reference: 7f3a9c", YELLOW_M, size=30).move_to(UP * 2.2)
        books = VGroup(*[box(n, GREY_B, w=2.5, h=1.3, size=26) for n in ("gateway", "checkout", "payments", "worker")]).arrange(RIGHT, buff=0.4).move_to(DOWN * 0.2)
        bl = T("four logbooks, a few thousand lines each", 26, GREY_B).next_to(books, DOWN, buff=0.35)
        self.beat("The phone rings at the office front desk. A customer's order failed this morning, and they read you a reference: 7f3a9c.",
                  FadeIn(ref, shift=DOWN * 0.15), run_time=2.0)
        self.beat("Somewhere in the building, four departments each keep a logbook, a few thousand lines long. The answer is in there, and the customer is waiting on the line.",
                  LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in books], lag_ratio=0.2), FadeIn(bl), run_time=3.0)
        q = T("your search prints nothing. good news?", 32, YELLOW_M).move_to(DOWN * 2.75)
        self.beat("Nobody reads four logbooks from the top. You ask the building questions instead. But here is one nobody thinks to ask: when your search prints nothing at all, is that good news?",
                  Succession(Wait(5.0), FadeIn(q, shift=UP * 0.1)), run_time=6.4)
        self.beat("Hold on to that one. By the end, you'll know why silence can lie.", Indicate(q, color=YELLOW_M), run_time=1.6)
        self.play(FadeOut(VGroup(ref, books, bl, q)), run_time=0.6)

        # ---------- 2. one page of the logbook
        L = VGroup()
        for n, txt in PAGE:
            num = M(f"{n:>2}", 22, GREY_D)
            tx = M(txt, 22, WHITE)
            lv = txt.split(" ")[0]
            glyphs(tx, txt, lv).set_color(LEVEL_C[lv])
            L.add(VGroup(num, tx).arrange(RIGHT, buff=0.3))
        L.arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        for row in L:
            row[0].align_to(L, LEFT)
        hl = VGroup(*[Rectangle(width=L.get_right()[0] - L.get_left()[0] + 0.3, height=0.32, stroke_width=0).set_fill(YELLOW_M, 0)
                      .move_to([L.get_center()[0], r.get_center()[1], 0]) for r in L])
        cap = T("app.log, lines 6 to 20 (trimmed to fit)", 22, GREY_B).next_to(L, DOWN, buff=0.22).align_to(L, LEFT)
        self.add(hl)
        self.beat("Every department keeps a logbook at its door, one line per visitor. A log file is the same idea: a plain text file that a program adds to, one line per event.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in L], lag_ratio=0.08), FadeIn(cap), run_time=3.6)
        self.beat("Here is one page of the lab's app.log. The whole file has 37 lines. Each holds a level, like INFO or ERROR, a request ID, and a message.",
                  Succession(Wait(2.6), Indicate(VGroup(*[glyphs(r[1], PAGE[i][1], PAGE[i][1].split(' ')[0]) for i, r in enumerate(L)]), scale_factor=1.05)), run_time=4.0)

        cmd_pos = np.array([-6.4, 3.0, 0])

        def cmd(text):
            return M("$ " + text, 28).move_to(cmd_pos, aligned_edge=LEFT)

        RX = 4.4

        def sweep(match, tm=None):
            """A highlighter runs down the page; matching lines stay marked, the rest fade."""
            band = Rectangle(width=hl[0].width, height=0.34, stroke_color=YELLOW_M, stroke_width=2).set_fill(YELLOW_M, 0.12).move_to(hl[0])
            plays = [(0.2, FadeIn(band))]
            for i in range(len(L)):
                a = [band.animate.move_to(hl[i])]
                if i in match:
                    a.append(hl[i].animate.set_fill(opacity=0.22))
                plays.append((0.12, *a))
            plays.append((0.4, FadeOut(band), *[L[i].animate.set_opacity(0.3) for i in range(len(L)) if i not in match]))
            return plays

        def reset():
            return [*[r.animate.set_opacity(1) for r in L], *[h.animate.set_fill(opacity=0) for h in hl]]

        # ---------- 3. the highlighter: grep
        c1 = cmd("grep 7f3a9c app.log")
        self.beat("Picture running a highlighter down every line of the page, then keeping only the marked lines. That is exactly what grep does.",
                  run_time=None)
        self.steps("grep reads its input one line at a time, checks whether the pattern appears anywhere in the line, and keeps the lines where it does.",
                   (1.0, Write(c1)), *sweep([6, 7, 8, 9]))
        o1 = VGroup(T("4 lines:", 28, YELLOW_M), T("one customer's request", 26, GREY_B)).arrange(DOWN, buff=0.15).move_to([RX, 0.3, 0])
        self.beat("Four lines, the whole story of the customer's request on this page. The highlighter is the pattern. The page is the input. The marked lines are the output.",
                  FadeIn(o1, shift=LEFT * 0.1), run_time=2.4)
        self.play(*reset(), FadeOut(o1), run_time=0.5)

        # options as questions
        c2 = cmd("grep ERROR app.log")
        self.steps("Each option answers a question you will ask when something is broken. Start plain: grep ERROR, in capitals.",
                   (0.6, Transform(c1, c2)), *sweep([2, 8, 14]))
        o2 = VGroup(T("4 lines in the file", 28, RED_M), T("(3 on this page)", 24, GREY_B)).arrange(DOWN, buff=0.15).move_to([RX, 0.3, 0])
        self.beat("In the whole file, that is 4 lines. You can see three of them here.", FadeIn(o2), run_time=1.4)
        c3 = cmd("grep -i error app.log")
        o3 = VGroup(T("-i ignores case:", 28, GOLD_M), T("5 lines", 28, GOLD_M), T("the extra one says", 24, GREY_B), T('"retrying after error"', 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([RX, 0.3, 0])
        self.steps("Did I miss any? Logs are messy about case, so dash I ignores it. Five lines. The extra one is a WARN line that says retrying after error.",
                   (0.6, Transform(c1, c3), FadeOut(o2), *reset()), *sweep([2, 8, 11, 14]), (0.6, FadeIn(o3)))
        c4 = cmd("grep -c 200 app.log")
        o4 = VGroup(M("-c 200", 26, WHITE), T("16 in the file", 26, GREY_B), M("-c -w 200", 26, TEAL_M), T("14: whole words only", 26, TEAL_M)).arrange(DOWN, buff=0.12).move_to([RX, 0.3, 0])
        self.steps("How many lines say 200? Dash C counts them: 16. But look at line 6. 1200ms contains 200 too.",
                   (0.6, Transform(c1, c4), FadeOut(o3), *reset()), *sweep([0, 1, 5, 10, 12, 13]),
                   (0.6, FadeIn(o4[:2])), (0.8, Indicate(glyphs(L[0][1], PAGE[0][1], "1200ms"), color=RED_M)))
        self.steps("Add dash W, and only 200 standing alone counts. The answer drops to 14.",
                   (0.6, hl[0].animate.set_fill(opacity=0), L[0].animate.set_opacity(0.3)), (0.6, FadeIn(o4[2:])))
        self.play(*reset(), FadeOut(o4), run_time=0.5)

        # exit code
        c5 = cmd("grep -q ERROR app.log ; echo $?")
        ec = VGroup(VGroup(M("0", 30, GREEN_M), T("found a match", 26, GREY_B)).arrange(RIGHT, buff=0.3),
                    VGroup(M("1", 30, YELLOW_M), T("no match", 26, GREY_B)).arrange(RIGHT, buff=0.3),
                    VGroup(M("2", 30, RED_M), T("something went wrong", 26, GREY_B)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([RX, 0.3, 0])
        self.beat("grep also hands back a number when it ends, called its exit code. The shell keeps the last one in $?. Quiet grep, then echo $?, prints 0.",
                  Transform(c1, c5), Succession(Wait(3.0), FadeIn(ec[0])), run_time=4.4)
        self.beat("Zero means found a match. One means no match. Two means something went wrong, like a missing file. Keep that one in your pocket.",
                  LaggedStart(FadeIn(ec[1]), FadeIn(ec[2]), lag_ratio=0.6), run_time=2.4)
        self.play(FadeOut(ec), run_time=0.4)

        # ---------- 4. describing text by its shape
        durs = [(0, "1200ms"), (1, "18ms"), (5, "3ms"), (7, "2900ms"), (8, "3000ms"), (9, "6012ms"), (10, "22ms"), (12, "812ms"), (13, "2ms")]
        self.beat("Now a harder question. You want every duration on the page: 18ms, 1200ms, 3ms. No single word matches them all.",
                  LaggedStart(*[Indicate(glyphs(L[i][1], PAGE[i][1], d), color=YELLOW_M) for i, d in durs[:3]], lag_ratio=0.4), run_time=2.6)
        shape = VGroup(chip("some digits", BLUE_M, 26), T("then", 26, GREY_B), chip("ms", BLUE_M, 26, mono=True)).arrange(RIGHT, buff=0.2).move_to([RX, 1.6, 0])
        self.beat("But they share a shape: some digits, then ms. A pattern that describes a shape like that is called a regular expression, or regex.",
                  FadeIn(shape, shift=DOWN * 0.1), run_time=2.0)
        rx = VGroup(VGroup(M("[0-9]", 30, BLUE_M), T("any one digit", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                    VGroup(M("+", 30, BLUE_M), T("one or more of it", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                    VGroup(M("ms", 30, BLUE_M), T("the letters ms", 24, GREY_B)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([RX, -0.2, 0])
        self.beat("Square brackets with zero to nine means any one digit. A plus means one or more of it. Then the letters ms.",
                  LaggedStart(*[FadeIn(r, shift=LEFT * 0.1) for r in rx], lag_ratio=0.5), run_time=3.0)
        c6 = cmd("grep -o -E '[0-9]+ms' app.log")
        marks = VGroup(*[glyphs(L[i][1], PAGE[i][1], d) for i, d in durs])
        self.steps("Run it with dash O, which prints only the part that matched, and dash E, which we'll come back to in a moment. Out come the durations, one per line.",
                   (0.8, Transform(c1, c6)), (1.6, LaggedStart(*[m.animate.set_color(YELLOW_M) for m in marks], lag_ratio=0.12)))
        more = VGroup(VGroup(M(".", 28, BLUE_M), T("any one character", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                      VGroup(M("*", 28, BLUE_M), T("repeat: zero or more", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                      VGroup(M("^  $", 28, BLUE_M), T("start, end of the line", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                      VGroup(M("|", 28, BLUE_M), T("or", 24, GREY_B)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([RX, -0.2, 0])
        self.beat("A few more symbols. A dot is any one character. A star is zero or more of the thing before it. Caret and dollar pin the start and the end of a line. And a bar means or.",
                  FadeOut(VGroup(rx, shape)), *[m.animate.set_color(WHITE) for m in marks], Succession(Wait(0.6), LaggedStart(*[FadeIn(r, shift=LEFT * 0.1) for r in more], lag_ratio=0.6)), run_time=6.6)

        # ---------- 5. predict, then break: the silent bar
        c7 = cmd('grep "ERROR|WARN" app.log')
        self.beat("So you want every line with ERROR or WARN. You type grep, then ERROR bar WARN in quotes. No dash E this time. What prints?",
                  FadeOut(more), Transform(c1, c7), run_time=1.8)
        self.countdown([RX, 0.3, 0])
        band = Rectangle(width=hl[0].width, height=0.34, stroke_color=YELLOW_M, stroke_width=2).set_fill(YELLOW_M, 0.12).move_to(hl[0])
        self.steps("Nothing. Not one line. And the exit code is 1: no match.",
                   (0.2, FadeIn(band)), *[(0.1, band.animate.move_to(hl[i])) for i in range(1, len(L))],
                   (0.4, FadeOut(band), *[r.animate.set_opacity(0.3) for r in L]))
        nothing = VGroup(T("(nothing)", 30, GREY_B), M("$? = 1", 28, YELLOW_M)).arrange(DOWN, buff=0.25).move_to([RX, 0.3, 0])
        self.add(nothing)
        lit = M("ERROR|WARN", 30, YELLOW_M).move_to([RX, -1.4, 0])
        litl = T("searched as plain text", 24, GREY_B).next_to(lit, DOWN, buff=0.15)
        self.beat("Here is why. Plain grep speaks the older, basic dialect of regex. In it, the bar is an ordinary character. So grep looked for the exact text E R R O R, bar, W A R N.",
                  Succession(Wait(4.6), AnimationGroup(FadeIn(lit), FadeIn(litl))), run_time=6.0)
        self.beat("And not a single line in this logbook contains that.", Wiggle(lit), run_time=1.4)
        c8 = cmd("grep -E 'ERROR|WARN' app.log")
        o8 = VGroup(T("8 lines in the file", 28, GREEN_M), T("(6 on this page)", 24, GREY_B)).arrange(DOWN, buff=0.15).move_to([RX, 0.3, 0])
        self.steps("Add dash E, for extended regex, where the bar means or. Now it finds 8 lines.",
                   (0.6, Transform(c1, c8), FadeOut(VGroup(nothing, lit, litl)), *[r.animate.set_opacity(1) for r in L]), *sweep([0, 2, 7, 8, 11, 14]), (0.5, FadeIn(o8)))
        self.beat("So the first grep did answer. It answered, perfectly, a question you never meant to ask.",
                  Indicate(c1, color=YELLOW_M), run_time=1.6)
        rule = VGroup(T("An empty result answers your pattern,", 28, YELLOW_M), T("not your question. Check the pattern.", 28, YELLOW_M)).arrange(DOWN, buff=0.12).move_to([RX, -1.7, 0])
        fit(rule, 4.2)
        self.beat("And that is the open question from the start. An empty result is an answer to your pattern, not to your question. So check the pattern before you trust the silence. And echo $? tells you whether grep found nothing, or failed.",
                  FadeIn(rule, shift=UP * 0.1), run_time=2.4)
        self.play(*reset(), FadeOut(VGroup(o8, rule)), run_time=0.6)

        # ---------- 6. guardrails: two languages, quote every pattern
        self.play(FadeOut(VGroup(L, hl, cap)), run_time=0.5)
        c9 = cmd("grep -E 'ERROR|WARN' logs/*.log")
        cl = VGroup(T("the clerk (shell) reads", 26, BLUE_M), M("*  =  any file name", 26, BLUE_M), M("logs/*.log", 26, BLUE_M),
                    T("unquoted: expanded to file names", 24, GREY_B)).arrange(DOWN, buff=0.2).move_to([-3.3, 0.2, 0])
        wk = VGroup(T("grep (regex) reads", 26, GOLD_M), M("*  =  zero or more", 26, GOLD_M), M("'ERROR|WARN'", 26, GOLD_M),
                    T("in single quotes: left alone", 24, GREY_B)).arrange(DOWN, buff=0.2).move_to([3.3, 0.2, 0])
        self.beat("One more trap. Last time, the clerk at the front desk read a star as any file name. Inside grep, a star means zero or more of the last character. Two languages, same symbols.",
                  Transform(c1, c9), FadeIn(cl[:2]), Succession(Wait(3.4), FadeIn(wk[:2])), run_time=6.0)
        self.beat("In this one command, both live side by side. The clerk expands the unquoted logs/*.log into file names. It leaves the regex alone, because it sits in single quotes.",
                  FadeIn(cl[2:]), Succession(Wait(3.0), FadeIn(wk[2:])), run_time=5.0)
        r2 = T("The quotes decide who reads what. Quote every pattern.", 28, YELLOW_M).move_to(DOWN * 2.6)
        self.beat("So the quotes decide who reads what. Put every grep pattern in single quotes.", FadeIn(r2, shift=UP * 0.1), run_time=1.6)
        dd = VGroup(M("grep -E '\\d'", 26, RED_M), T("the letter d, not a digit: write [0-9]", 26, GREY_B)).arrange(RIGHT, buff=0.4).move_to(DOWN * 3.25)
        self.beat("And if you have used regex in a programming language, leave backslash D at home. GNU grep reads it as the letter d. Write zero to nine in brackets instead.",
                  FadeIn(dd, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(cl, wk, r2, dd, c1)), run_time=0.5)

        # ---------- 7. moral, check
        m = VGroup(T("grep keeps the lines that match a pattern.", 30, YELLOW_M),
                   T("A regex describes a shape. Silence is an answer to your pattern.", 28, GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.3)
        self.beat("So, the moral of the story. grep is a highlighter: it keeps the lines that match a pattern. A regex describes text by its shape. And when grep goes quiet, that silence is an answer to your pattern. Check it, before you tell the customer all is well.",
                  FadeIn(m[0], shift=UP * 0.1), Succession(Wait(4.0), FadeIn(m[1], shift=UP * 0.1)), run_time=6.0)
        self.play(FadeOut(m), run_time=0.5)
        cq = VGroup(T("Which command counts the lines of", 30), M("app.log", 28), T("that end with", 30), M("ms", 28), T("?", 30)).arrange(RIGHT, buff=0.18).move_to(UP * 1.8)
        opts = VGroup(M("grep -c '^ms' app.log", 26, GREY_B), M("grep -c 'ms*' app.log", 26, GREY_B), M("grep -c 'ms$' app.log", 26, GREY_B),
                      M("grep -c -F 'ms$' app.log", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(cq, DOWN, buff=0.55)
        self.beat("A quick check. Which command counts the lines of app.log that end with ms?",
                  FadeIn(cq), Succession(Wait(2.2), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3)), run_time=4.4)
        self.countdown(DOWN * 3.0, "pause and think")
        self.beat("The third one. Dollar pins the pattern to the end of the line. With dash F, grep would hunt for the text ms dollar itself.",
                  opts[2].animate.set_color(GREEN_M), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 2], run_time=1.6)
        self.wait(1.2)
