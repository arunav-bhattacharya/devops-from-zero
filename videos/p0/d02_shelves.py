import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"/opt/homebrew/bin\b", "slash opt slash homebrew slash bin"), (r"/opt/homebrew\b", "slash opt slash homebrew"),
            (r"~/\.zprofile\b", "the dot Z profile file"), (r"\(\.venv\)", "dot venv in brackets"), (r"\.venv\b", "dot venv"),
            (r"\bvenv\b", "venv"), (r"\bpython3\.14\b", "python three point fourteen"), (r"\bpython@3\.14\b", "python at three point fourteen"), (r"\bpip3\.14\b", "pip three point fourteen"),
            (r"\bexternally-managed-environment\b", "externally managed environment"), (r"\bPATH\b", "path"),
            (r"\bzsh\b", "Z shell"), (r"\bbrew --version\b", "brew dash dash version"), (r"\bpytest\b", "pie test")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


SH_W = 6.8
CX = -2.6
PARK = np.array([CX, -2.95, 0])


def slot(i):
    return np.array([CX, 2.25 - 0.76 * i, 0])


def shelf(name, items, color=GREY_B):
    """One folder drawn as a shelf: its name on the left, the commands it holds sitting on the right."""
    r = RoundedRectangle(corner_radius=0.1, width=SH_W, height=0.62, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.1), 1)
    n = M(name, 22, color).move_to(r).align_to(r, LEFT).shift(RIGHT * 0.25)
    cs = VGroup(*[chip(c, color, 22, mono=True) for c in items]).arrange(RIGHT, buff=0.14)
    for c in cs:
        c[0].stretch_to_fit_height(0.46)
    if len(cs):
        cs.move_to(r).align_to(r, LEFT).shift(RIGHT * 3.25)
    return VGroup(r, n, cs)


def person(color, s=1.0):
    head = Circle(radius=0.24, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    body = RoundedRectangle(corner_radius=0.28, width=0.82, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), 1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(body, head).scale(s)


class D02Shelves(VoiceScene):
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
        self.title_card("Installed, but not found", "the shelves your shell checks, in order")

        # ---------- 1. the shy question
        term = RoundedRectangle(corner_radius=0.15, width=8.6, height=1.8, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1).move_to(UP * 1.2)
        tl = T("terminal", 22, GREY_B).next_to(term, UP, buff=0.12).align_to(term, LEFT)
        L1 = term.get_left() + RIGHT * 0.4 + UP * 0.38
        L2 = term.get_left() + RIGHT * 0.4 + DOWN * 0.38

        def tline(text, pos, color=WHITE, size=26):
            return M(text, size, color).move_to(pos, aligned_edge=LEFT)

        ok = tline("Installation successful!", L1, GREEN_M)
        self.beat("You have just installed a tool. Homebrew, an app that installs other tools on a Mac. The installer prints a long wall of text that ends in success.",
                  Create(term), FadeIn(tl), Succession(Wait(3.4), FadeIn(ok)), run_time=4.4)
        cmd = tline("$ brew --version", L1)
        out = tline("zsh: command not found: brew", L2, RED_M)
        self.beat("Feeling good, you type brew --version. And the terminal says: command not found.",
                  FadeOut(ok), Succession(Wait(0.8), Write(cmd), Wait(1.0), FadeIn(out, shift=UP * 0.1)), run_time=3.6)
        q = T("did the install fail?", 34, YELLOW_M).move_to(DOWN * 1.4)
        self.beat("So, did the install fail? Should you download it again? Restart the Mac?",
                  FadeIn(q, shift=UP * 0.15), run_time=1.8)
        self.beat("None of those. The tool is on your Mac, right now. To see why the terminal can't find it, let's go to the kitchen.",
                  FadeOut(q), run_time=2.0)
        self.play(FadeOut(VGroup(term, tl, cmd, out)), run_time=0.6)

        # ---------- 2. the kitchen: flour in the wrong cupboard
        you = person(BLUE_M).move_to(RIGHT * 2.7 + UP * 0.6)
        youl = T("you", 26, BLUE_M).next_to(you, DOWN, buff=0.2)
        rows = VGroup(*[shelf(n, its).move_to(slot(i)) for i, (n, its) in enumerate(zip(["top shelf", "middle shelf", "bottom shelf"],
                                                                                       [["sugar", "salt"], ["yeast"], ["oil"]]))])
        cup = shelf("back-door cupboard", ["flour"], GOLD_M).move_to(PARK)
        self.beat("Last night the flour arrived, and you put it in a cupboard by the back door. In the morning, you go looking for it.",
                  FadeIn(you, shift=UP * 0.2), FadeIn(youl), Succession(Wait(1.2), FadeIn(cup, shift=UP * 0.1)), run_time=2.8)
        self.beat("You check your usual shelves, one by one, from the top.",
                  LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in rows], lag_ratio=0.3), run_time=2.0)
        cur = Triangle(color=YELLOW_M, fill_opacity=1, stroke_width=0).scale(0.14).rotate(PI / 2)

        def at(row):
            return row[0].get_right() + RIGHT * 0.3

        cur.move_to(at(rows[0]))
        self.steps("Not on the top shelf. Not on the middle one. Not on the bottom one.",
                   (0.4, FadeIn(cur)), (0.6, rows[0][0].animate.set_stroke(RED_M)),
                   (0.5, cur.animate.move_to(at(rows[1]))), (0.6, rows[1][0].animate.set_stroke(RED_M)),
                   (0.5, cur.animate.move_to(at(rows[2]))), (0.6, rows[2][0].animate.set_stroke(RED_M)))
        nf = T('"we have no flour"', 30, RED_M).move_to(RIGHT * 4.6 + UP * 2.4)
        self.beat("So you announce: we have no flour. But you do. It is in the kitchen. It is just not on any shelf you check.",
                  FadeIn(nf, shift=UP * 0.1), Succession(Wait(2.6), Indicate(cup[2], color=GOLD_M)), run_time=4.2)
        self.play(FadeOut(cur), FadeOut(nf), *[r[0].animate.set_stroke(GREY_B) for r in rows], run_time=0.5)

        # ---------- 3. map it onto the Mac
        sh = T("the shell", 26, BLUE_M).move_to(youl)
        self.beat("Your Mac does exactly this. The program inside the terminal window that runs what you type is called the shell. On a Mac it is zsh. The shell is you, looking for the flour.",
                  Succession(Wait(3.0), Transform(youl, sh)), run_time=4.0)
        F = [("/usr/bin", ["git", "python3"]), ("/bin", ["ls", "zsh"]), ("/usr/sbin", []), ("/sbin", [])]
        base = VGroup(*[shelf(n, its).move_to(slot(i)) for i, (n, its) in enumerate(F)])
        self.beat("The shelves are folders on your disk. A command, like ls or git, is a program file sitting in one of those folders.",
                  ReplacementTransform(rows, base[:3]), FadeIn(base[3]), run_time=2.2)
        pt = T("the folders it checks, in order", 26, GREY_B).next_to(base, UP, buff=0.3).align_to(base, LEFT)
        few = T("a few of them, on a new Mac", 22, GREY_B).next_to(base, DOWN, buff=0.25).align_to(base, LEFT)
        self.beat("When you type a name, the shell does not search your whole Mac. It checks a short list of folders, in order, and runs the first match it finds.",
                  FadeIn(pt, shift=DOWN * 0.1), FadeIn(few), run_time=2.0)
        hb = shelf("/opt/homebrew/bin", ["brew"], GOLD_M).move_to(PARK)
        self.beat("And the cupboard by the back door? On Apple Silicon Macs, Homebrew lives in /opt/homebrew, and puts its commands in /opt/homebrew/bin.",
                  FadeOut(few), Succession(Wait(1.6), ReplacementTransform(cup, hb)), run_time=3.0)
        cur.move_to(at(base[0]))
        qq = M("brew?", 24, YELLOW_M).next_to(cur, RIGHT, buff=0.2)
        qq.add_updater(lambda m_: m_.next_to(cur, RIGHT, buff=0.2))
        self.steps("Watch the shell look for brew.",
                   (0.4, FadeIn(cur), FadeIn(qq)), (0.4, base[0][0].animate.set_stroke(RED_M)),
                   *[(0.4, cur.animate.move_to(at(base[i])), base[i][0].animate.set_stroke(RED_M)) for i in range(1, 4)])
        self.beat("The list ends, so it gives up. Command not found. The list macOS starts you with does not include Homebrew's shelf.",
                  Indicate(pt, color=GREY_B), Succession(Wait(2.6), Indicate(hb[1], color=GOLD_M)), run_time=4.0)
        self.play(FadeOut(cur), FadeOut(qq), *[b[0].animate.set_stroke(GREY_B) for b in base], run_time=0.4)
        qq.clear_updaters()

        # ---------- 4. name it
        name = T("PATH", 40, YELLOW_M).move_to(pt, aligned_edge=LEFT)
        pt2 = T("the folders your shell searches, in order", 26, GREY_B).next_to(name, RIGHT, buff=0.35).align_to(name, DOWN)
        self.beat("That list of shelves has a name. It is called your PATH.",
                  ReplacementTransform(pt, VGroup(name, pt2)), run_time=1.6)
        self.beat("So command not found is a report about the list, not about your disk. The shell is telling you where it looked.",
                  Indicate(name, color=YELLOW_M), run_time=1.6)

        # ---------- 5. the fix: Next steps
        ns = VGroup(T("==> Next steps", 26, GOLD_M), T("run these commands to add", 22, GREY_B), T("Homebrew to your PATH", 22, GREY_B)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        ns.move_to(RIGHT * 4.6 + UP * 1.3)
        self.beat("Here is the step everyone skips. When the Homebrew installer finishes, it prints Next steps, with two or three commands to run.",
                  FadeOut(you), FadeOut(youl), FadeIn(ns, shift=DOWN * 0.1), run_time=2.4)
        self.beat("It is easy to miss, because they come right after a wall of text that looks like the job is done. An installer that ends with homework.",
                  Indicate(ns[0], color=GOLD_M), run_time=1.8)
        self.beat("So the point is: read the last lines of any installer. Run exactly what this one prints. Those lines add Homebrew's folder to your PATH.",
                  Succession(Wait(3.2), AnimationGroup(*[b.animate.move_to(slot(i + 1)) for i, b in enumerate(base)], hb.animate.move_to(slot(0)))), run_time=5.0)
        rows2 = VGroup(hb, *base)
        zp = VGroup(M("~/.zprofile", 24, GOLD_M), T("read by every", 24, GREY_B), T("new shell", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to(RIGHT * 4.6 + DOWN * 1.0)
        self.beat("They also save the change in ~/.zprofile, a file each new shell reads when it starts. So open a new terminal tab.",
                  FadeIn(zp, shift=UP * 0.1), run_time=2.4)
        cur.move_to(at(hb))
        qq = M("brew?", 24, YELLOW_M).next_to(cur, RIGHT, buff=0.2)
        hit = VGroup(T("found:", 26, GREEN_M), T("brew runs", 26, GREEN_M)).arrange(RIGHT, buff=0.2).next_to(qq, RIGHT, buff=0.35)
        self.steps("Type brew again. The search reaches Homebrew's shelf, finds brew, and stops.",
                   (0.6, FadeOut(ns)), (0.5, FadeIn(cur), FadeIn(qq)), (1.2, Wait(1.2)),
                   (0.6, hb[0].animate.set_stroke(GREEN_M), Indicate(hb[2][0], color=GREEN_M)), (0.6, FadeIn(hit)))
        r1 = T("When a tool is installed but not found, check PATH first.", 28, YELLOW_M).move_to(DOWN * 2.95)
        self.beat("When a tool is installed but not found, check PATH first.", FadeOut(zp), FadeIn(r1, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(cur, qq, hit, r1)), hb[0].animate.set_stroke(GOLD_M), run_time=0.5)

        # ---------- 6. first match wins: the venv
        py = chip("pip3.14", GOLD_M, 22, mono=True)
        py[0].stretch_to_fit_height(0.46)
        py.next_to(hb[2], RIGHT, buff=0.14)
        hb[2].add(py)
        self.beat("Homebrew's shelf holds more than brew. This course installs python@3.14 there, with pip3.14, the tool that installs Python packages.",
                  Succession(Wait(3.4), FadeIn(py, shift=LEFT * 0.1)), run_time=4.4)
        jars = VGroup(chip("rye starter", GOLD_M, 26), chip("white starter", BLUE_M, 26)).arrange(DOWN, buff=0.3).move_to(RIGHT * 4.6 + UP * 0.6)
        self.beat("Now a second kitchen problem. A baker who makes rye and white bread keeps a separate starter jar for each. Share one jar, and the rye ends up in the white loaf.",
                  LaggedStart(*[FadeIn(j, shift=LEFT * 0.1) for j in jars], lag_ratio=0.5), run_time=2.4)
        self.beat("Python projects have the same risk, because two projects may want different versions of the same package, the add-on code they use.",
                  Wiggle(jars), run_time=1.4)
        vb = shelf(".venv/bin", ["python", "pip"], TEAL_M).move_to(PARK)
        self.beat("So each project gets a virtual environment, or venv: a private folder of packages for one project. It has its own bin shelf, with its own python, and its own pip, Python's package installer.",
                  FadeOut(jars), Succession(Wait(2.4), FadeIn(vb, shift=UP * 0.15)), run_time=3.6)
        act = VGroup(M("$ source", 24), M(".venv/bin/activate", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(RIGHT * 4.5 + UP * 1.1)
        self.beat("You switch it on with source .venv/bin/activate.", FadeIn(act), run_time=1.4)
        self.beat("So here is a question. Where on the list does activating put the venv's shelf? And then, when you type python, which one runs?",
                  Indicate(vb[1], color=TEAL_M), run_time=1.8)
        self.countdown(RIGHT * 4.3 + DOWN * 0.4)
        prm = M("(.venv) $", 26, TEAL_M).next_to(act, DOWN, buff=0.3).align_to(act, LEFT)
        self.steps("Activating puts the venv's shelf first on your PATH, and your prompt starts with (.venv).",
                   (1.6, *[r.animate.move_to(slot(i + 1)) for i, r in enumerate(rows2)], vb.animate.move_to(slot(0))),
                   (0.6, FadeIn(prm)))
        cur.move_to(at(vb))
        qq = M("python?", 24, YELLOW_M).next_to(cur, RIGHT, buff=0.2)
        self.steps("So python and pip now mean the copies inside the venv. The search stops at the very first shelf.",
                   (0.5, FadeIn(cur), FadeIn(qq)), (0.7, vb[0].animate.set_stroke(GREEN_M), Indicate(vb[2][0], color=GREEN_M)))
        self.beat("This project's packages can't clash with another project's. First match wins, and the first shelf is yours.",
                  Indicate(vb[2][1], color=GREEN_M), run_time=1.6)
        self.play(FadeOut(cur), FadeOut(qq), vb[0].animate.set_stroke(TEAL_M), run_time=0.4)

        # ---------- 7. break it: forget to activate
        nt = VGroup(M("$ pip3.14", 24), M("install flask", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(act, aligned_edge=UL)
        self.steps("Now the trap. Tomorrow you open a new terminal, forget to activate, and install a package.",
                   (1.6, FadeOut(act), FadeOut(prm), vb.animate.move_to(PARK), *[r.animate.move_to(slot(i)) for i, r in enumerate(rows2)]),
                   (0.6, FadeIn(nt)))
        cur.move_to(at(hb))
        qq = M("pip3.14?", 24, YELLOW_M).next_to(cur, RIGHT, buff=0.2)
        err = VGroup(M("error:", 22, RED_M), M("externally-", 22, RED_M), M("managed-environment", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        err.next_to(nt, DOWN, buff=0.35).align_to(nt, LEFT)
        self.steps("This time the search finds pip on Homebrew's shelf. And Homebrew's own Python refuses, with externally-managed-environment.",
                   (0.5, FadeIn(cur), FadeIn(qq)), (0.6, hb[0].animate.set_stroke(RED_M), Indicate(hb[2][1], color=RED_M)), (2.0, Wait(2.0)), (0.6, FadeIn(err)))
        self.beat("Well. That is a very long way of saying: wrong shelf. The error means one thing. Your venv is not active.",
                  Indicate(err, color=RED_M), run_time=1.6)
        self.beat("And the tempting shortcut, sudo pip with no venv, only makes packages from different projects fight over versions. Homebrew's Python refuses that anyway.",
                  Wiggle(hb[2]), run_time=1.4)
        r2 = T("Before any pip install, check that your prompt starts with (.venv).", 28, YELLOW_M).move_to(DOWN * 2.95)
        fit(r2, 12.4)
        self.beat("So before any pip install, check that your prompt starts with (.venv). If it doesn't, activate first.",
                  FadeOut(VGroup(cur, qq, vb)), hb[0].animate.set_stroke(GOLD_M), FadeIn(r2, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(r2, nt, err)), run_time=0.5)

        # ---------- 8. moral, recap, check
        m = T("The shell runs the first match on your PATH.", 32, YELLOW_M).move_to(DOWN * 2.95)
        self.beat("So, the moral of the story. The shell never searches your whole Mac. It checks a short list of shelves, in order, and runs the first match.",
                  FadeIn(m, shift=UP * 0.1), run_time=2.4)
        self.beat("Homebrew's Next steps put its shelf on the list. And a venv puts its own shelf first, for one project.",
                  Indicate(hb[1], color=GOLD_M), run_time=2.0)
        self.play(FadeOut(VGroup(m, name, pt2, rows2)), run_time=0.7)
        cq = T("A new terminal, in your hello-devops folder.", 30).move_to(UP * 2.0)
        cq2 = VGroup(M("pytest", 28, WHITE), T("says command not found. It worked yesterday.", 30)).arrange(RIGHT, buff=0.25).next_to(cq, DOWN, buff=0.25)
        opts = VGroup(*[T(o, 28, GREY_B) for o in ("your test files were deleted overnight", "pytest only runs while Docker is open",
                                                   "this new terminal has no active venv", "your GitHub login has expired")])
        opts.arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(cq2, DOWN, buff=0.5)
        self.beat("A quick check. You open a new terminal in your hello-devops folder, and pytest says command not found. It worked yesterday. What is wrong?",
                  FadeIn(cq), FadeIn(cq2), Succession(Wait(4.4), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3)), run_time=6.6)
        self.countdown(DOWN * 3.0, "pause and think")
        self.beat("pytest lives on the venv's shelf, and every new terminal starts without the venv active. Activate it, and the shelf is back on the list.",
                  opts[2].animate.set_color(GREEN_M), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 2], run_time=1.6)
        self.wait(1.2)
