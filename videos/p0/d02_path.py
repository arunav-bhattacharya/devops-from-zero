import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"/opt/homebrew/bin\b", "slash opt slash homebrew slash bin"), (r"/opt/homebrew\b", "slash opt slash homebrew"),
            (r"~/\.zprofile\b", "the dot Z profile file"), (r"\.venv/bin\b", "dot venv slash bin"), (r"\.venv\b", "dot venv"),
            (r"\bvenv\b", "venv"), (r"\bpython3\.14\b", "python three point fourteen"), (r"\bpython3\b", "python three"),
            (r"\bpython@3\.14\b", "python at three point fourteen"), (r"\bwhich -a\b", "which dash A"),
            (r"\bexternally-managed-environment\b", "externally managed environment"), (r"\bPATH\b", "path"), (r"\bpip\b", "pip"),
            (r"\bzsh\b", "Z shell")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def folder(name, cmds, color=GREY_B, w=7.6):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=0.6, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.1), 1)
    n = M(name, 20, color).move_to(r).align_to(r, LEFT).shift(RIGHT * 0.25)
    cs = VGroup(*[chip(c, color, 20, mono=True) for c in cmds]).arrange(RIGHT, buff=0.12)
    for c in cs:
        c[0].stretch_to_fit_height(0.44)
    cs.move_to(r).align_to(r, LEFT).shift(RIGHT * 3.0)
    return VGroup(r, n, cs)


class D02Path(VoiceScene):
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
        self.title_card("How your shell finds a command", "PATH, Homebrew and the venv")

        CX = -2.9
        TOP = 1.3
        GAP = 0.72
        STAGE = [3.0, -3.1, 0]

        def slots(n):
            return [[CX, TOP - GAP * i, 0] for i in range(n)]

        # ---- terminal
        term = RoundedRectangle(corner_radius=0.15, width=5.0, height=1.7, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1).move_to([4.1, 2.45, 0])
        tl = T("terminal", 20, GREY_B).next_to(term, UP, buff=0.1).align_to(term, LEFT)
        tl.next_to(term.get_corner(UL), DR, buff=0.12)
        L1, L2 = [4.1 - 2.25, 2.65, 0], [4.1 - 2.25, 2.15, 0]

        def tline(text, pos, color=WHITE, size=22):
            return M(text, size, color).move_to(pos, aligned_edge=LEFT)

        cmd = tline("$ brew --version", L1)
        self.beat("You install Homebrew, the installer for almost everything else in this course. Then you type brew.",
                  Create(term), FadeIn(tl), Succession(Wait(3.0), Write(cmd)), run_time=4.4)
        out = tline("brew: command not found", L2, RED_M)
        self.beat("And the shell says: command not found.", FadeIn(out, shift=UP * 0.1), run_time=1.2)
        why = T("brew is on the disk. Why can't the shell find it?", 26, YELLOW_M).move_to([0, -0.4, 0])
        self.beat("Homebrew is on your disk. So why can't the shell find it?", FadeIn(why, shift=UP * 0.15), run_time=1.8)
        self.play(FadeOut(why), run_time=0.4)

        # ---- the PATH
        base = VGroup(folder("/usr/bin", ["git", "python3"]), folder("/bin", ["ls", "zsh"]), folder("/usr/sbin", []), folder("/sbin", []))
        for f, p in zip(base, slots(6)):
            f.move_to(p)
        ptitle = T("your PATH, searched from the top", 24, GREY_B).move_to([CX, 2.15, 0])
        self.beat("Your shell is the program that runs what you type. When you type a name, it does not search the whole disk.",
                  Indicate(cmd, color=YELLOW_M), run_time=1.6)
        self.beat("It looks in each folder on a list called your PATH, in order, and it runs the first match.",
                  FadeIn(ptitle), LaggedStart(*[FadeIn(f, shift=DOWN * 0.1) for f in base], lag_ratio=0.25), run_time=3.0)

        cur = Triangle(color=YELLOW_M, fill_opacity=1, stroke_width=0).scale(0.14).rotate(PI / 2)

        def at(row):
            return cur.copy().next_to(row, RIGHT, buff=0.15).get_center()

        cur.move_to(at(base[0]))
        q = M("brew?", 22, YELLOW_M)
        q.add_updater(lambda m: m.next_to(cur, RIGHT, buff=0.12))
        self.steps("Watch it look for brew. Not in the first folder. Not in the next. Not in any of them.",
                   (0.5, FadeIn(cur), FadeIn(q)), (0.9, Wait(0.9)), (0.4, base[0][0].animate.set_stroke(RED_M)),
                   (0.6, cur.animate.move_to(at(base[1]))), (0.4, base[1][0].animate.set_stroke(RED_M)),
                   (0.5, cur.animate.move_to(at(base[2]))), (0.3, base[2][0].animate.set_stroke(RED_M)),
                   (0.4, cur.animate.move_to(at(base[3]))), (0.3, base[3][0].animate.set_stroke(RED_M)))
        self.beat("The list ends, so the shell gives up: command not found.",
                  Indicate(out, color=RED_M), *[f[0].animate.set_stroke(GREY_B) for f in base], run_time=1.8)
        self.play(FadeOut(cur), FadeOut(q), run_time=0.3)
        q.clear_updaters()

        # ---- where Homebrew really is
        hb = folder("/opt/homebrew/bin", ["brew", "python3"], GOLD_M).move_to(STAGE)
        self.beat("On Apple Silicon Macs, Homebrew lives in /opt/homebrew, and puts its commands in /opt/homebrew/bin.",
                  FadeIn(hb, shift=UP * 0.15), run_time=2.4)
        self.beat("But the PATH that macOS starts with does not include that folder. The tool is in the room, but not on the list.",
                  Indicate(ptitle, color=GREY_B), Succession(Wait(2.6), Indicate(hb[0], color=GOLD_M)), run_time=4.2)

        ns = VGroup(T("installer: Next steps", 24, GOLD_M), M("eval ... brew shellenv ...", 22)).arrange(DOWN, buff=0.15).move_to([3.9, 0.55, 0])
        self.beat("When the installer finishes, it prints Next steps: two or three commands. Most people get stuck right here, because they skip them.",
                  FadeIn(ns, shift=DOWN * 0.1), run_time=2.4)
        self.steps("Run exactly what it prints. Those lines add Homebrew's folder to your PATH.",
                   (1.6, Wait(1.6)),
                   (1.4, *[f.animate.move_to(p) for f, p in zip(base, slots(6)[1:])], hb.animate.move_to(slots(6)[0])))
        zp = VGroup(M("~/.zprofile", 22, GOLD_M), T("read by every new shell", 22, GREY_B)).arrange(DOWN, buff=0.12).move_to([3.9, -0.55, 0])
        self.beat("They also save the change in ~/.zprofile, a file each new shell reads when it starts. So open a new terminal tab.",
                  FadeIn(zp, shift=UP * 0.1), Succession(Wait(4.0), FadeOut(out)), run_time=5.0)
        self.play(FadeOut(ns), FadeOut(zp), run_time=0.4)

        cur.move_to(at(hb))
        q = M("brew?", 22, YELLOW_M)
        q.add_updater(lambda m: m.next_to(cur, RIGHT, buff=0.12))
        found = tline("Homebrew prints its version", L2, GREEN_M, 22)
        self.steps("Now type brew again. The search reaches Homebrew's folder, finds brew, and stops. The first match wins.",
                   (0.8, Indicate(cmd, color=YELLOW_M)), (0.5, FadeIn(cur), FadeIn(q)), (0.8, Wait(0.8)),
                   (0.6, hb[0].animate.set_stroke(GREEN_M), Indicate(hb[2][0], color=GREEN_M)), (0.6, FadeIn(found)))
        self.play(FadeOut(cur), FadeOut(q), hb[0].animate.set_stroke(GOLD_M), run_time=0.4)
        q.clear_updaters()

        # ---- python and the venv
        py = chip("python3.14", GOLD_M, 20, mono=True)
        py[0].stretch_to_fit_height(0.44)
        py.next_to(hb[2], RIGHT, buff=0.12)
        hb[2].add(py)
        self.beat("First match wins matters for Python too. Homebrew's default Python is newer than the one this course uses.",
                  Indicate(hb[2][1], color=GOLD_M), run_time=2.8)
        cmd2 = tline("$ brew install python@3.14", L1, WHITE, 20)
        self.beat("So you install python@3.14, and type python3.14 when you create the project's virtual environment.",
                  Transform(cmd, cmd2), FadeOut(found), Succession(Wait(1.6), FadeIn(py, shift=LEFT * 0.1)), run_time=3.8)
        cmd3 = tline("$ python3.14 -m venv .venv", L1, WHITE, 20)
        vb = folder(".venv/bin", ["python", "pip"], TEAL_M).move_to(STAGE)
        self.beat("A venv is a private folder of packages for one project. It has its own bin folder, with its own python and pip.",
                  Transform(cmd, cmd3), Succession(Wait(1.4), FadeIn(vb, shift=UP * 0.15)), run_time=3.6)
        cmd4 = tline("$ source .venv/bin/activate", L1, WHITE, 20)
        pr = tline("(.venv) $", L2, TEAL_M, 22)
        rows = [hb] + list(base)
        self.steps("Activating it puts .venv/bin first on your PATH. Your prompt starts with dot venv in brackets.",
                   (0.8, Transform(cmd, cmd4)), (1.0, Wait(1.0)),
                   (1.4, *[f.animate.move_to(p) for f, p in zip(rows, slots(6)[1:])], vb.animate.move_to(slots(6)[0])),
                   (0.6, FadeIn(pr)))
        cur.move_to(at(vb))
        q = M("python?", 22, YELLOW_M)
        q.add_updater(lambda m: m.next_to(cur, RIGHT, buff=0.12))
        self.steps("Now python and pip mean the copies inside the venv. The search stops at the very first folder. So this project's Flask cannot clash with another project's.",
                   (0.5, FadeIn(cur), FadeIn(q)), (0.6, vb[0].animate.set_stroke(GREEN_M), Indicate(vb[2][0], color=GREEN_M)),
                   (2.6, Wait(2.6)), (0.6, Indicate(vb[2][1], color=GREEN_M)))
        self.play(FadeOut(cur), FadeOut(q), vb[0].animate.set_stroke(TEAL_M), run_time=0.4)
        q.clear_updaters()

        # ---- forgetting to activate
        cmd5 = tline("$ deactivate", L1, WHITE, 20)
        self.steps("deactivate puts your PATH back.",
                   (0.6, Transform(cmd, cmd5), FadeOut(pr)),
                   (1.2, vb.animate.move_to(STAGE), *[f.animate.move_to(p) for f, p in zip(rows, slots(6)[:5])]))
        cmd6 = tline("$ pip install flask", L1, WHITE, 20)
        err = tline("externally-managed-environment", L2, RED_M, 20)
        cur.move_to(at(hb))
        q = M("pip?", 22, YELLOW_M)
        q.add_updater(lambda m: m.next_to(cur, RIGHT, buff=0.12))
        self.steps("Forget to activate, and pip is found in Homebrew's folder instead. Homebrew's own Python refuses, with externally-managed-environment.",
                   (0.6, Transform(cmd, cmd6)), (0.5, FadeIn(cur), FadeIn(q)), (0.6, hb[0].animate.set_stroke(RED_M)),
                   (2.4, Wait(2.4)), (0.6, FadeIn(err)))
        fix = T("the fix: activate the venv first", 22, TEAL_M).next_to(vb, UP, buff=0.2)
        self.beat("That error means one thing: your venv is not active.", FadeIn(fix, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(cur), FadeOut(q), FadeOut(fix), FadeOut(err), hb[0].animate.set_stroke(GOLD_M), run_time=0.4)
        q.clear_updaters()

        # ---- which -a
        cmd7 = tline("$ which -a python3", L1, WHITE, 20)
        wa = VGroup(M("/opt/homebrew/bin/python3", 20, GOLD_M), M("/usr/bin/python3", 20, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        wa.move_to(L2, aligned_edge=LEFT).shift(DOWN * 0.1)
        hits = VGroup(SurroundingRectangle(hb[2][1], color=GOLD_M, buff=0.06), SurroundingRectangle(base[0][2][1], color=GREY_B, buff=0.06))
        self.beat("When the wrong version of a tool runs, try which -a. It lists every match on your PATH, in the order the shell tries them.",
                  Transform(cmd, cmd7), Succession(Wait(2.6), AnimationGroup(FadeIn(wa), Create(hits))), run_time=5.0)
        self.play(FadeOut(hits), run_time=0.4)

        # ---- recap
        rc = T("The shell runs the first match on your PATH.", 30, YELLOW_M).move_to([0, -3.3, 0])
        self.beat("So the shell runs the first match on your PATH. Homebrew's Next steps add its folder, and a venv puts its own folder first.",
                  FadeOut(vb), FadeIn(rc, shift=UP * 0.15), Succession(Wait(2.8), Indicate(hb[0], color=GOLD_M)), run_time=5.4)
        self.wait(1.0)
