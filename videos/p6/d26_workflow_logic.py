import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bGITHUB_OUTPUT\b", "github output"), (r"\bruns-on\b", "runs on"), (r"\$TITLE\b", "dollar title"),
            (r"\benv\b", "E N V"), (r"\bif:", "if"), (r"\bsteps\.meta\.outputs\.version\b", "steps dot meta dot outputs dot version"),
            (r"\bneeds\.version\.outputs\.version\b", "needs dot version dot outputs dot version"), (r"\bid\b", "I D")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def part(m, text, sub):
    """The glyphs of substring sub inside Text m (Text drops spaces, so count non-space characters)."""
    i = text.index(sub)
    a = len(text[:i].replace(" ", ""))
    return m[a:a + len(sub.replace(" ", ""))]


def lane(y0, y1, color, name):
    r = Rectangle(width=13.5, height=y1 - y0, stroke_width=0).set_fill(tint(color, 0.07), 1).move_to([0, (y0 + y1) / 2, 0])
    top = Line([-6.75, y1, 0], [6.75, y1, 0], stroke_width=1.5, color=tint(color, 0.6))
    lab = T(name, 22, color).move_to([-5.55, (y0 + y1) / 2, 0])
    return VGroup(r, top, lab).set_z_index(-1)


class D26WorkflowLogic(VoiceScene):
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
        self.title_card("Who fills in the blanks, and when", "expressions, the shell, and values passed between jobs")

        # ---- the three lanes
        L_GH, L_RUN, L_SH = (2.15, 3.65), (-0.55, 2.0), (-3.3, -0.7)
        gh = lane(*L_GH, BLUE_M, "GitHub")
        rn = lane(*L_RUN, TEAL_M, "runner")
        sh = lane(*L_SH, GOLD_M, "shell")
        CX = 1.05  # centre of the content area
        S1 = 'run: echo "Branch ${{ github.ref_name }}"'
        step = M(S1, 22).move_to([CX, 0.75, 0])
        self.beat("A workflow is text with blanks in it. This step prints the branch name.",
                  FadeIn(step, shift=UP * 0.1), run_time=1.6)
        blank = SurroundingRectangle(part(step, S1, "${{ github.ref_name }}"), color=YELLOW_M, buff=0.06, corner_radius=0.05)
        self.beat("The part in dollar and double braces is an expression. And the text is filled in at two different moments, by different programs.",
                  Create(blank), run_time=1.8)
        self.beat("Picture three places. GitHub's servers. The runner, the machine that runs a job. And the shell, bash, on that machine.",
                  LaggedStart(FadeIn(gh), FadeIn(rn), FadeIn(sh), lag_ratio=0.5), run_time=3.0)

        # moment one: the runner pastes the result
        ctx = chip("github.ref_name = main", BLUE_M, 22, mono=True).move_to([CX, 2.9, 0])
        filled = M('run: echo "Branch main"', 22).move_to(step, aligned_edge=LEFT)
        one = chip("1", YELLOW_M, 22).move_to([-4.3, 0.75, 0])
        self.steps("Moment one. Just before the step starts, the runner works out each expression, and pastes the result into the text. On a push to main, the result is main.",
                   (0.8, FadeIn(one)), (1.6, FadeIn(ctx, shift=DOWN * 0.1)), (1.6, Wait(1.6)),
                   (1.4, ReplacementTransform(step, filled), FadeOut(blank), ctx.animate.set_opacity(0.4)))
        two = chip("2", YELLOW_M, 22).move_to([-4.3, -2.0, 0])
        cmd = M('$ echo "Branch main"', 22, GOLD_M).move_to([CX, -1.55, 0]).align_to(filled, LEFT)
        out = M("Branch main", 22, WHITE).next_to(cmd, DOWN, buff=0.25).align_to(cmd, LEFT)
        self.steps("Moment two. The shell gets the finished script, and runs it. The expression never reaches bash. It was replaced before bash even started.",
                   (0.8, FadeIn(two)), (1.4, TransformFromCopy(filled, cmd)), (0.8, FadeIn(out)), (2.0, Wait(2.0)), (1.0, Indicate(filled, color=YELLOW_M)))
        self.play(FadeOut(VGroup(filled, cmd, out, ctx)), run_time=0.6)

        # ---- consequence 1: pasted text becomes code
        st2 = M('run: echo "Title: ${{ github.event.pull_request.title }}"', 20).move_to([CX, 0.75, 0])
        title = M('fix"; echo pwned; echo "', 22, RED_M)
        tc = VGroup(T("PR title:", 22, BLUE_M), title).arrange(RIGHT, buff=0.25).move_to([CX, 2.9, 0])
        self.beat("Why does this matter? Say a step prints a pull request title. Someone else writes that title.",
                  FadeIn(st2, shift=UP * 0.1), FadeIn(tc), run_time=2.0)
        P2 = 'run: echo "Title: fix"; echo pwned; echo ""'
        p2 = M(P2, 20).move_to(st2, aligned_edge=LEFT)
        part(p2, P2, 'fix"; echo pwned; echo "').set_color(RED_M)
        self.steps("The runner pastes the title in as text. Its quote mark ends your string.",
                   (1.4, ReplacementTransform(st2, p2)), (1.2, Indicate(part(p2, P2, 'fix"'), color=RED_M)))
        sh_out = VGroup(M("Title: fix", 22), M("pwned", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([CX, -1.55, 0]).align_to(p2, LEFT)
        warn = T("a command from the title ran", 24, RED_M).next_to(sh_out, RIGHT, buff=0.8)
        self.steps("So bash runs a command the title added. Pasted text became code.",
                   (1.0, FadeIn(sh_out[0])), (0.8, FadeIn(sh_out[1])), (0.8, FadeIn(warn, shift=LEFT * 0.1)))
        safe = VGroup(M("env:", 20, GREEN_M), M("  TITLE: ${{ github.event.pull_request.title }}", 20, GREEN_M),
                      M('run: echo "Title: $TITLE"', 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([CX, 0.75, 0])
        self.beat("The fix: put the value in env, and use dollar TITLE in the script.",
                  FadeOut(sh_out), FadeOut(warn), ReplacementTransform(p2, safe), run_time=1.8)
        var = chip('TITLE = fix"; echo pwned; echo "', GREEN_M, 20, mono=True).move_to([CX, -1.2, 0])
        so2 = M('Title: fix"; echo pwned; echo "', 22).next_to(var, DOWN, buff=0.3).align_to(var, LEFT)
        self.steps("Now the script itself never changes. The title travels as a variable, and the shell treats it as data. It just prints it.",
                   (1.4, Indicate(safe[2], color=GREEN_M)), (1.2, TransformFromCopy(title, var[1])), (0.1, FadeIn(var[0])), (1.0, FadeIn(so2)))
        self.play(FadeOut(VGroup(safe, var, so2, tc)), run_time=0.6)

        # ---- consequence 2: a job-level if runs before any runner exists
        jif = M("if: env.DEPLOY == 'yes'", 22).move_to([CX - 1.3, 2.9, 0])
        self.beat("Now a job's own keys, such as if and runs-on. GitHub's servers work those out, before any runner exists.",
                  FadeIn(jif, shift=DOWN * 0.1), rn.animate.set_opacity(0.25), sh.animate.set_opacity(0.25), FadeOut(one), FadeOut(two), run_time=2.0)
        have = VGroup(*[chip(n, BLUE_M, 22, mono=True) for n in ("github", "needs", "vars", "inputs")]).arrange(RIGHT, buff=0.2)
        nope = VGroup(*[chip(n, GREY_D, 22, mono=True) for n in ("env", "steps", "runner")]).arrange(RIGHT, buff=0.2)
        have.move_to([CX - 1.5, 1.2, 0]); nope.next_to(have, RIGHT, buff=0.6)
        hl = T("known at that moment", 22, BLUE_M).next_to(have, DOWN, buff=0.25)
        nl = T("do not exist yet", 22, GREY_B).next_to(nope, DOWN, buff=0.25)
        self.beat("At that moment, GitHub only knows four contexts: github, needs, vars and inputs.",
                  LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in have], lag_ratio=0.2), FadeIn(hl), run_time=2.4)
        err = chip("error", RED_M, 22).next_to(jif, RIGHT, buff=0.4)
        self.steps("The env, steps and runner contexts do not exist yet. So if env dot DEPLOY on a job is an error.",
                   (1.4, LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in nope], lag_ratio=0.2), FadeIn(nl)), (1.2, Indicate(part(jif, "if: env.DEPLOY == 'yes'", "env"), color=RED_M)), (0.8, FadeIn(err)))
        q = T("when something behaves strangely: which moment am I in?", 26, YELLOW_M).move_to([0, -2.0, 0])
        self.beat("When something behaves strangely, ask which of the two moments you are in.",
                  FadeIn(q, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(jif, have, nope, hl, nl, err, q, rn, sh)), run_time=0.7)

        # ---- passing values: step output, job output, needs
        JY, JH, JW = -0.75, 4.0, 5.6
        jv = RoundedRectangle(corner_radius=0.15, width=JW, height=JH, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.07), 1).move_to([-3.45, JY, 0])
        jb = RoundedRectangle(corner_radius=0.15, width=JW, height=JH, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.07), 1).move_to([3.45, JY, 0])
        jvl = M("job: version", 22, TEAL_M).move_to([-3.45, 1.0, 0])
        jbl = M("job: build   needs: version", 22, TEAL_M).move_to([3.45, 1.0, 0])
        ghl = gh[2]
        self.beat("Now the other problem: passing a value along. Each step runs in a new shell. Each job runs on a new machine.",
                  ghl.animate.move_to([0, 3.3, 0]).set_opacity(1), Create(jv), FadeIn(jvl), Create(jb), FadeIn(jbl), run_time=2.4)
        s1 = VGroup(M('echo "version=1.4.0"', 20), M('>> "$GITHUB_OUTPUT"', 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        s1[1].shift(RIGHT * 0.4)
        s1.move_to([-3.45, 0.05, 0])
        s1l = T("step, id: meta", 20, GREY_B).move_to([-3.45, 0.55, 0]).align_to(s1, LEFT)
        f = RoundedRectangle(corner_radius=0.08, width=3.0, height=0.5, stroke_color=GOLD_M, stroke_width=2.5).set_fill(tint(GOLD_M, 0.2), 1).move_to([-3.45, -1.0, 0])
        fl = M("$GITHUB_OUTPUT  (a file)", 20, GOLD_M).next_to(f, UP, buff=0.1)
        self.steps("So you append the value to a file the runner gives every step. Its path is in the variable GITHUB_OUTPUT.",
                   (1.2, FadeIn(s1l), Write(s1)), (1.0, FadeIn(f), FadeIn(fl)), (1.2, Indicate(s1[1], color=GOLD_M)))
        line = M("version=1.4.0", 20, GOLD_M).move_to(s1[0][5:18])
        self.steps("The step writes a line, version equals 1.4.0.",
                   (1.4, line.animate.move_to(f.get_center())))
        so = chip("steps.meta.outputs.version = 1.4.0", TEAL_M, 20, mono=True).move_to([-3.45, -1.7, 0])
        self.steps("When the step ends, the runner reads the file and records what you wrote. Later steps in this job read it as steps.meta.outputs.version.",
                   (1.2, Indicate(f, color=GOLD_M)), (1.4, TransformFromCopy(line, so)))
        # job output up to GitHub
        jo = M("job outputs: version", 20, TEAL_M).move_to([-3.45, -2.35, 0])
        up = Arrow(jv.get_top() + RIGHT * 1.6, [-1.85, 2.4, 0], buff=0.05, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.12)
        val = chip("version = 1.4.0", YELLOW_M, 20, mono=True).move_to([0, 2.65, 0])
        self.steps("Between jobs you need one more hop, because jobs share nothing. The job's outputs block names the value. When the job ends, the runner sends it to GitHub.",
                   (2.2, Wait(2.2)), (1.0, FadeIn(jo)), (1.0, GrowArrow(up)), (1.0, travel(up, YELLOW_M, 1.0)), (0.8, FadeIn(val, shift=RIGHT * 0.2)))
        dn = Arrow([1.85, 2.4, 0], jb.get_top() + LEFT * 1.6, buff=0.05, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.12)
        no = chip("needs.version.outputs.version", TEAL_M, 20, mono=True).move_to([3.45, 0.2, 0])
        bs = M('echo "Building $VERSION"', 20).move_to([3.45, -0.8, 0])
        self.steps("GitHub hands it to every job that needs this one. That job reads it as needs.version.outputs.version.",
                   (1.0, GrowArrow(dn)), (1.0, travel(dn, YELLOW_M, 1.0)), (1.4, TransformFromCopy(val, no)), (1.0, FadeIn(bs)))
        warn2 = T("never write a secret here: everyone who can read the run sees it", 24, RED_M).move_to([0, -3.3, 0])
        self.beat("Outputs are always strings. And never write a secret into these files. Everyone who can read the run can see them.",
                  FadeIn(warn2, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- recap
        rc = VGroup(T("1. GitHub and the runner paste in expressions", 30, BLUE_M),
                    T("2. then the shell runs the finished text", 30, GOLD_M),
                    T("3. values travel: file, step output, job output, needs", 30, TEAL_M)).arrange(DOWN, buff=0.45)
        self.beat("Expressions are pasted in first, then the shell runs the finished text. And a value travels from a file, to a step output, to a job output, and through needs.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.5), run_time=5.0)
        self.wait(1.0)
