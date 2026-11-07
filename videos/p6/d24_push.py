import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


def tint(color, a=0.18):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def flash(b, color=YELLOW_M, rt=1.2):
    return ShowPassingFlash(b[0].copy().set_fill(opacity=0).set_stroke(color, 7), time_width=0.6, run_time=rt)


def panel(w, h, color=GREY_B, sw=2):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(BLACK, 1)


def progress(w=3.2, h=0.24, color=TEAL_M):
    out = Rectangle(width=w, height=h, stroke_color=GREY_B, stroke_width=2)
    f = Rectangle(width=w - 0.04, height=h - 0.06, stroke_width=0).set_fill(color, 0.8)
    f.move_to(out).stretch(0.01, 0, about_edge=LEFT).align_to(out, LEFT).shift(RIGHT * 0.02)
    return VGroup(out, f)


def code_line(text, size=20, color=WHITE):
    """Monospace line that keeps its leading spaces: an invisible bar at the start fixes the left edge and the line height."""
    t = M("|" + text, size, color)
    t[0].set_opacity(0)
    return t


def vis(line):
    return VGroup(*line[1:])


def fill_up(p):
    return p[1].animate.stretch_to_fit_width(p[0].width - 0.04, about_edge=LEFT)


class D24Push(VoiceScene):
    def construct(self):
        self.title_card("What happens when you push", "event, workflow, runner, steps, result")

        # ---- 0. the laptop and the chain
        lap = panel(3.2, 1.2, WHITE)
        cmd = M("$ git push", 28)
        laptop = VGroup(lap, cmd.move_to(lap)).move_to([-5.0, 1.55, 0])
        lap_l = T("your laptop", 22, GREY_B).next_to(laptop, UP, buff=0.15)
        gh = box("GitHub Actions", BLUE_M, size=30, h=1.0).move_to([3.2, 1.55, 0])
        gh_l = T("a machine that is nobody's laptop", 24, GREY_B).next_to(gh, DOWN, buff=0.3)
        a0 = Arrow(laptop.get_right(), gh.get_left(), buff=0.2, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        self.beat("CI needs a machine that is nobody's laptop. One that runs the same commands for every push, and posts the result on the commit. GitHub Actions gives you that machine.",
                  Create(lap), FadeIn(lap_l), Write(cmd), Succession(Wait(1.5), FadeIn(gh_l), Wait(3.0), AnimationGroup(GrowArrow(a0), FadeIn(gh))), run_time=7.0)

        names = ["event", "workflow", "jobs", "runner", "steps", "result"]
        chain = VGroup()
        for i, n in enumerate(names):
            c = chip(f"{i + 1}  {n}", GREY_B, 24)
            chain.add(c)
        chain.arrange(RIGHT, buff=0.55).move_to([0, 3.3, 0])
        links = VGroup(*[Arrow(chain[i].get_right(), chain[i + 1].get_left(), buff=0.06, stroke_width=2, color=GREY_D,
                               max_tip_length_to_length_ratio=0.3) for i in range(5)])
        self.beat("Here is the chain that one git push sets off.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in chain], lag_ratio=0.15), LaggedStart(*[GrowArrow(a) for a in links], lag_ratio=0.15),
                  FadeOut(VGroup(gh, gh_l, a0)), Indicate(cmd, color=YELLOW_M), run_time=2.2)

        def on(i):
            return chain[i][0].animate.set_stroke(YELLOW_M, 3).set_fill(YELLOW_M, 0.25)

        def done(i):
            return chain[i][0].animate.set_stroke(GREEN_M, 2.5).set_fill(GREEN_M, 0.15)

        # ---- 1. the event
        ev = panel(3.2, 2.0, GOLD_M)
        ev_rows = VGroup(T("event", 26, GOLD_M), M("push", 22), M("commit 9f2c1e7", 22), M("branch main", 22)).arrange(DOWN, buff=0.16)
        event = VGroup(ev, ev_rows.move_to(ev)).move_to([-5.0, -1.25, 0])
        a1 = Arrow(laptop.get_bottom(), event.get_top(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        self.beat("One. GitHub records an event: a push, of this commit, to this branch.",
                  on(0), GrowArrow(a1), Create(ev), LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in ev_rows], lag_ratio=0.25), run_time=2.4)
        self.play(travel(a1), run_time=0.7)

        # ---- 2. the workflow file
        yml = ["name: ci", "on:", "  push:", "  workflow_dispatch:", "jobs:", "  test:", "    runs-on: ubuntu-latest", "    steps:",
               "      - uses: actions/checkout@v7", "      ..."]
        rows = VGroup(*[code_line(l, 20) for l in yml]).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        fp = panel(rows.width + 0.8, rows.height + 0.6)
        rows.move_to(fp).align_to(fp, LEFT).shift(RIGHT * 0.4)
        wf = VGroup(fp, rows).move_to([2.6, -0.25, 0])
        wf_l = M(".github/workflows/ci.yml", 22, GREY_B).next_to(wf, UP, buff=0.15).align_to(wf, LEFT)
        a2 = Arrow(event.get_right(), [fp.get_left()[0], rows[2].get_y(), 0], buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
        hl_on = SurroundingRectangle(VGroup(vis(rows[1]), vis(rows[2])), color=YELLOW_M, buff=0.07, stroke_width=2)
        self.beat("Two. GitHub reads the workflows folder in the commit you pushed, and starts a run of every workflow that listens for push.",
                  done(0), on(1), Create(fp), FadeIn(wf_l), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows], lag_ratio=0.08),
                  GrowArrow(a2), Succession(Wait(1.6), Create(hl_on)), run_time=3.6)
        hl_job = SurroundingRectangle(vis(rows[5]), color=YELLOW_M, buff=0.07, stroke_width=2)
        self.beat("Three. The run starts its jobs. This workflow has one job, called test.",
                  done(1), on(2), ReplacementTransform(hl_on, hl_job), run_time=1.6)

        # ---- 3. a fresh runner for the job
        hl_runs = SurroundingRectangle(vis(rows[6]), color=YELLOW_M, buff=0.07, stroke_width=2)
        self.beat("Four. For each job, GitHub starts a new virtual machine, called the runner.",
                  done(2), on(3), ReplacementTransform(hl_job, hl_runs), run_time=1.4)
        vm = panel(13.0, 6.0, BLUE_M, 3).move_to([0, -0.55, 0])
        vm_t = VGroup(T("runner", 30, BLUE_M), M("ubuntu-latest", 24, WHITE)).arrange(RIGHT, buff=0.3)
        vm_t.move_to(vm.get_corner(UL) + RIGHT * (vm_t.width / 2 + 0.4) + DOWN * 0.5)
        fresh = T("a fresh virtual machine", 22, GREY_B).next_to(vm_t, DOWN, buff=0.15).align_to(vm_t, LEFT)
        self.play(FadeOut(VGroup(laptop, lap_l, event, a1, a2, wf, wf_l, hl_runs)), run_time=0.6)
        self.play(GrowFromCenter(vm), FadeIn(vm_t), FadeIn(fresh), run_time=1.0)

        tools = VGroup(*[chip(t, BLUE_M, 24) for t in ("Ubuntu", "git", "Docker", "Python")]).arrange_in_grid(2, 2, buff=(0.25, 0.25))
        tools.next_to(fresh, DOWN, buff=0.45).align_to(fresh, LEFT)
        fold = VGroup(Polygon([0, 0, 0], [0.25, 0, 0], [0.33, 0.1, 0], [0.75, 0.1, 0], [0.75, -0.42, 0], [0, -0.42, 0], stroke_color=GREY_B, stroke_width=2))
        files = T("your files: none", 24, GREY_B)
        frow = VGroup(fold, files).arrange(RIGHT, buff=0.25).next_to(tools, DOWN, buff=0.55).align_to(tools, LEFT)
        self.beat("It comes with Ubuntu and common tools, like git, Docker and Python. But none of your files.",
                  LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tools], lag_ratio=0.2), FadeIn(frow), run_time=2.6)

        # ---- 4. steps, in order
        sx = -1.6
        step_txt = [("uses", "actions/checkout@v7"), ("uses", "actions/setup-python@v7"), ("run", "pip install -r requirements-dev.txt"), ("run", "pytest -q")]
        steps = VGroup()
        for i, (k, t) in enumerate(step_txt):
            n = T(str(i + 1), 24, GREY_B)
            c = Circle(radius=0.23, stroke_color=GREY_B, stroke_width=2).move_to(n)
            kind = M(k + ":", 20, PURPLE_M if k == "uses" else TEAL_M)
            body = M(t, 20)
            row = VGroup(VGroup(c, n), kind, body).arrange(RIGHT, buff=0.22)
            kind.align_to(row, ORIGIN)
            steps.add(row)
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([sx, -0.75, 0]).align_to([sx, 0, 0], LEFT)
        for r in steps:
            r[2].next_to(r[0], RIGHT, buff=1.05)
            r[1].next_to(r[0], RIGHT, buff=0.2)
        st_l = T("steps, in order", 24, GREY_B).next_to(steps, UP, buff=0.4).align_to(steps, LEFT)
        flow = Arrow(steps[0][0].get_bottom() + DOWN * 0.02, steps[3][0].get_top() + UP * 0.02, buff=0.05, stroke_width=2, color=GREY_D,
                     max_tip_length_to_length_ratio=0.06)
        self.beat("Five. A program on that machine, the runner application, runs the job's steps, in order. Each step is a ready-made action, or a shell command.",
                  done(3), on(4), FadeIn(st_l), LaggedStart(*[FadeIn(s, shift=DOWN * 0.1) for s in steps], lag_ratio=0.3), run_time=3.4)

        def run_step(i, ok=True, code="exit 0"):
            r = steps[i]
            mark = tick(ok, 0.2).next_to(r[2], RIGHT, buff=0.3)
            ec = M(code, 20, GREEN_M if ok else RED_M).next_to(mark, RIGHT, buff=0.2) if i != 2 else VGroup()
            return mark, ec, AnimationGroup(r[0][0].animate.set_stroke(GREEN_M if ok else RED_M, 3), Create(mark), FadeIn(ec))

        repo = T("your repository", 24, TEAL_M).move_to(files, aligned_edge=LEFT)
        m1, e1, an1 = run_step(0)
        self.beat("Checkout copies your repository onto the machine.",
                  an1, Transform(files, repo), fold.animate.set_stroke(TEAL_M).set_fill(TEAL_M, 0.2), run_time=1.6)
        m2, e2, an2 = run_step(1)
        m3, e3, an3 = run_step(2)
        self.beat("Setup python sets up Python 3.14. Then pip installs the dependencies.",
                  Succession(an2, Wait(0.6), an3), run_time=2.8)

        rule = VGroup(VGroup(M("exit 0", 22, GREEN_M), T("pass", 24)).arrange(RIGHT, buff=0.3),
                      VGroup(M("not 0", 22, RED_M), T("fail, job stops", 24)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        rule[1][1].align_to(rule[0][1], LEFT)
        rule.next_to(frow, DOWN, buff=0.45).align_to(frow, LEFT)
        self.beat("A step passes when its command exits with zero. Any other number fails it.",
                  FadeIn(rule, shift=UP * 0.1), Indicate(e1, color=GREEN_M), run_time=2.0)
        m4b, e4b, an4b = run_step(3, False, "exit 1")
        self.beat("pytest exits with 1 when a test fails. The job stops there, and the whole run turns red.",
                  an4b, vm.animate.set_stroke(RED_M), chain[5][0].animate.set_stroke(RED_M, 3).set_fill(RED_M, 0.2), run_time=2.0)
        m4, e4, an4 = run_step(3)
        self.beat("Here, every test passes. pytest exits with zero, and the job is green.",
                  FadeOut(VGroup(m4b, e4b)), an4, vm.animate.set_stroke(GREEN_M), chain[5][0].animate.set_stroke(GREY_B, 2.5).set_fill(GREY_B, 0.18),
                  run_time=1.8)
        self.play(FadeOut(VGroup(vm, vm_t, fresh, tools, fold, files, steps, st_l, rule, m1, e1, m2, e2, m3, e3, m4, e4)), run_time=0.6)

        # ---- 5. several jobs: parallel unless one needs another
        def job(name, color=TEAL_M):
            b = panel(4.0, 1.5, BLUE_M, 2.5)
            t = VGroup(M(name, 26, WHITE), T("fresh machine", 22, GREY_B)).arrange(RIGHT, buff=0.35)
            t.move_to(b).shift(UP * 0.3 + LEFT * 0.3)
            p = progress(3.3).move_to(b).shift(DOWN * 0.32)
            return VGroup(b, t, p)

        lint, test, build = job("lint"), job("test"), job("build")
        lint.move_to([-3.6, 1.1, 0]); test.move_to([-3.6, -1.2, 0]); build.move_to([3.4, -0.05, 0])
        ln = Arrow(lint.get_right(), build.get_left() + UP * 0.3, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        tn = Arrow(test.get_right(), build.get_left() + DOWN * 0.3, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        needs = M("needs: [lint, test]", 22, YELLOW_M).next_to(build, UP, buff=0.3)
        self.beat("A workflow can have more than one job. Jobs run in parallel, unless one needs another.",
                  on(2), done(4), LaggedStart(FadeIn(lint, shift=RIGHT * 0.2), FadeIn(test, shift=RIGHT * 0.2), FadeIn(build, shift=LEFT * 0.2), lag_ratio=0.3),
                  run_time=2.4)
        tl = tick(True, 0.2).next_to(lint[0], RIGHT, buff=-0.45).shift(UP * 0.45)
        tt = tick(True, 0.2).next_to(test[0], RIGHT, buff=-0.45).shift(UP * 0.45)
        self.beat("Lint and test start at the same moment, each on its own fresh machine.",
                  fill_up(lint[2]), fill_up(test[2]), Succession(Wait(1.6), AnimationGroup(Create(tl), Create(tt))), run_time=2.8)
        wait_l = T("waiting", 24, GOLD_M).next_to(build, DOWN, buff=0.25)
        tb = tick(True, 0.2).next_to(build[0], RIGHT, buff=-0.45).shift(UP * 0.45)
        self.beat("Build says needs, lint and test. So it waits, and starts only after both succeed.",
                  Write(needs), GrowArrow(ln), GrowArrow(tn), FadeIn(wait_l),
                  Succession(Wait(1.2), AnimationGroup(travel(ln), travel(tn)), FadeOut(wait_l), fill_up(build[2]), Create(tb)), run_time=4.2)
        own = T("no file moves between jobs, unless you save it", 24, GREY_B).move_to([0, -3.15, 0])
        self.beat("And no file moves from one job to the next, unless you save it.",
                  FadeIn(own, shift=UP * 0.1), *[flash(j, BLUE_M) for j in (lint, test, build)], run_time=1.8)

        # ---- 6. the result, then the machines are deleted
        row = panel(12.4, 1.0, GREY_B).move_to([0, 1.55, 0])
        rc = VGroup(M("9f2c1e7", 24, GREY_B), T("Run tests in CI", 26)).arrange(RIGHT, buff=0.5)
        rc.move_to(row).align_to(row, LEFT).shift(RIGHT * 0.4)
        checks = VGroup()
        for n in ("lint", "test", "build"):
            checks.add(VGroup(tick(True, 0.16), M(f"ci / {n}", 20, GREEN_M)).arrange(RIGHT, buff=0.15))
        checks.arrange(RIGHT, buff=0.45).move_to(row).align_to(row, RIGHT).shift(LEFT * 0.4)
        commit_l = T("on the commit and its pull request", 22, GREY_B).next_to(row, UP, buff=0.15).align_to(row, LEFT)
        small = VGroup(*[mbox(n, BLUE_M, size=26, w=2.6, h=0.9) for n in ("lint", "test", "build")]).arrange(RIGHT, buff=0.7).move_to([0, -1.6, 0])
        sm_l = T("three fresh machines", 22, GREY_B).next_to(small, DOWN, buff=0.25)
        self.play(FadeOut(VGroup(ln, tn, needs, own, tl, tt, tb, lint, test, build)), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in small], lag_ratio=0.2), FadeIn(sm_l), run_time=0.8)
        self.beat("Six. The result appears on the commit, and on its pull request: a green tick, or a red cross.",
                  done(2), on(5), Create(row), FadeIn(commit_l), FadeIn(rc), LaggedStart(*[FadeIn(c, shift=LEFT * 0.1) for c in checks], lag_ratio=0.3),
                  run_time=2.6)
        gone = T("machines deleted", 26, RED_M).move_to([0, -1.6, 0])
        self.beat("Then GitHub deletes the machines. Nothing on them is kept.",
                  done(5), *[j.animate.scale(0.05).set_opacity(0) for j in small], FadeOut(sm_l), FadeIn(gone), run_time=2.2)
        self.beat("Your laptop took no part. It only pushed.",
                  FadeOut(gone), FadeIn(laptop.move_to([0, -1.7, 0])), FadeIn(lap_l.next_to(laptop, UP, buff=0.15)), run_time=1.6)
        self.play(FadeOut(VGroup(row, rc, checks, commit_l, laptop, lap_l)), run_time=0.6)

        # ---- recap
        rec = VGroup(T("push  →  event  →  workflow", 30, YELLOW_M), T("→  a fresh runner per job  →  steps in order  →  result", 30, YELLOW_M)).arrange(DOWN, buff=0.3)
        rec.move_to([0, 0.5, 0])
        rec2 = T("then the machine is thrown away", 28, GREY_B).next_to(rec, DOWN, buff=0.45)
        self.beat("Push, event, workflow, a fresh runner for each job, steps in order, and the result on the commit. Then the machine is thrown away.",
                  Write(rec), FadeIn(rec2, shift=UP * 0.1), *[done(i) for i in range(6)], run_time=3.6)
        self.wait(1.0)
