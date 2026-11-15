import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bci\.yml\b", "C I dot yammel"), (r"\b3\.13\b", "three thirteen"), (r"\b3\.14\b", "three fourteen"),
            (r"\bPRs?\b", lambda m: "P R" + ("s" if m.group(0).endswith("s") else "")), (r"\bF401\b", "F four oh one"),
            (r"\bapp\.py\b", "app dot pie"), (r"\bfail-fast\b", "fail fast"), (r"\brequirements\*?\.txt\b", "requirements files"),
            (r"\bruff\b", "ruff"), (r"\bpip\b", "pip")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def job(name, color=TEAL_M, w=2.5, h=1.05):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    lab = M(name, 22).move_to(r.get_center() + UP * 0.2)
    out = Rectangle(width=w - 0.9, height=0.18, stroke_color=GREY_B, stroke_width=1.5).move_to(r.get_center() + DOWN * 0.24 + LEFT * 0.25)
    f = Rectangle(width=out.width - 0.04, height=0.12, stroke_width=0).set_fill(color, 0.85).move_to(out)
    f.stretch(0.01, 0, about_edge=LEFT)
    return VGroup(r, lab, out, f)


def fill(j, frac=1.0):
    return j[3].animate.stretch_to_fit_width(max(0.01, (j[2].width - 0.04) * frac), about_edge=LEFT)


def empty(j):
    return j[3].animate.stretch_to_fit_width(0.01, about_edge=LEFT)


def mark_pos(j):
    return j[2].get_right() + RIGHT * 0.38


def recolor(j, c):
    t = j.copy()
    t[0].set_stroke(c).set_fill(tint(c), 1)
    t[3].set_fill(c, 0.85).stretch_to_fit_width(t[2].width - 0.04, about_edge=LEFT)
    return Transform(j, t)


def skip(j):
    t = j.copy().set_opacity(0.35)
    t[2].set_opacity(0); t[3].set_opacity(0)
    return Transform(j, t)


class D25Pipeline(VoiceScene):
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
        self.title_card("A real CI pipeline", "cheap checks first, slow ones last, and a guard at the gate")

        # ---- 0. the problem: people wait for CI
        old = job("test", TEAL_M, 2.4).move_to([0, 1.2, 0])
        d24 = T("Day 24: ci.yml runs the tests once", 26, GREY_B).next_to(old, UP, buff=0.4)
        self.beat("On Day 24, ci.yml ran the tests once. That was the whole pipeline.",
                  FadeIn(d24), FadeIn(old), fill(old), run_time=2.0)
        wait_l = T("people wait for it before they merge", 26, YELLOW_M).move_to([0, -0.4, 0])
        self.beat("A real pipeline checks more. And it has to be quick, because people wait for it before they merge.",
                  FadeIn(wait_l, shift=UP * 0.15), run_time=1.6)
        # a time line: cheap first, slow last
        ax = Arrow([-5.2, -2.0, 0], [5.4, -2.0, 0], buff=0, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.02)
        axl = T("time", 22, GREY_B).next_to(ax, DOWN, buff=0.15).align_to(ax, RIGHT)
        segs = VGroup()
        x = -5.2
        for name, w, c in (("lint", 1.4, BLUE_M), ("test", 3.4, TEAL_M), ("build", 5.0, GOLD_M)):
            r = Rectangle(width=w - 0.08, height=0.62, stroke_color=c, stroke_width=2.5).set_fill(tint(c, 0.3), 1)
            r.move_to([x + w / 2, -1.45, 0])
            segs.add(VGroup(r, M(name, 22).move_to(r)))
            x += w
        rule = T("cheap checks first, slow ones last", 28, WHITE).move_to([0, 0.5, 0])
        self.beat("So the rule is simple. Cheap checks go first, and slow ones last.",
                  FadeOut(d24), FadeOut(old), FadeOut(wait_l), Create(ax), FadeIn(axl),
                  LaggedStart(*[GrowFromEdge(s, LEFT) for s in segs], lag_ratio=0.4), FadeIn(rule), run_time=2.6)
        tags = VGroup(T("seconds", 22, BLUE_M).next_to(segs[0], UP, buff=0.18),
                      T("once per Python version", 22, TEAL_M).next_to(segs[1], UP, buff=0.18),
                      T("the slowest", 22, GOLD_M).next_to(segs[2], UP, buff=0.18))
        self.beat("Lint, with ruff, takes seconds. Then pytest. Then the Docker image build, the slowest of all.",
                  LaggedStart(*[FadeIn(t, shift=DOWN * 0.1) for t in tags], lag_ratio=0.6), FadeOut(rule), run_time=3.0)

        # ---- 1. three jobs, each its own check
        PRX, JX, BX, GX = -5.75, -2.65, 0.55, 4.45
        pr = box("pull request", WHITE, w=1.95, h=0.9, size=24).move_to([PRX, 0, 0])
        lint = job("lint", BLUE_M).move_to([JX, 1.7, 0])
        test = job("test", TEAL_M).move_to([JX, -0.85, 0])
        build = job("build", GOLD_M, w=2.3).move_to([BX, 0, 0])
        self.beat("The lab splits the work into three jobs. Each job runs on its own runner, and shows up on the pull request as its own check.",
                  FadeOut(VGroup(ax, axl, tags)), ReplacementTransform(segs[0], lint), ReplacementTransform(segs[1], test),
                  ReplacementTransform(segs[2], build), Succession(Wait(1.2), FadeIn(pr)), run_time=2.6)
        pa = VGroup(edge_arrow(pr, lint), edge_arrow(pr, test))
        para = T("parallel by default", 24, GREY_B).move_to([JX, 3.05, 0])
        self.beat("Jobs run in parallel by default. Nothing waits for anything.",
                  LaggedStart(*[GrowArrow(a) for a in pa], lag_ratio=0.2), FadeIn(para), run_time=1.6)

        # ---- 2. the matrix
        mx = M('matrix: python-version: ["3.13", "3.14"]', 22, TEAL_M).move_to([1.6, -3.1, 0])
        self.beat("Your app should work on Python 3.13 and 3.14. A matrix runs one job definition several times, with different values.",
                  FadeIn(mx, shift=UP * 0.15), Indicate(test[1], color=TEAL_M), run_time=2.2)
        t13 = job("test (3.13)", TEAL_M).move_to([JX, 0, 0])
        t14 = job("test (3.14)", TEAL_M).move_to([JX, -1.7, 0])
        pa2 = VGroup(edge_arrow(pr, lint), edge_arrow(pr, t13), edge_arrow(pr, t14))
        self.beat("So one test job becomes two. They show up as two checks, test (3.13) and test (3.14).",
                  ReplacementTransform(test, VGroup(t13, t14)), ReplacementTransform(pa, pa2), run_time=1.8)
        jobs = VGroup(lint, t13, t14)

        # ---- 3. needs
        na = VGroup(*[edge_arrow(j, build) for j in jobs])
        nd = M("needs: [lint, test]", 22, GOLD_M).next_to(build, DOWN, buff=0.85).shift(RIGHT * 0.4)
        self.beat("The build job says needs, lint and test. Now it waits. It starts only after all of them succeed.",
                  LaggedStart(*[GrowArrow(a) for a in na], lag_ratio=0.2), FadeIn(nd), Transform(mx, mx.copy().set_opacity(0)), run_time=2.2)
        self.remove(mx)

        # the gate
        gate = RoundedRectangle(corner_radius=0.15, width=3.3, height=3.6, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1).move_to([GX, 0, 0])
        gt = T("merge", 26, GREY_B).next_to(gate.get_top(), DOWN, buff=0.25)
        ga = Arrow(build.get_right(), gate.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.play(Create(gate), FadeIn(gt), GrowArrow(ga), run_time=1.0)

        # ---- 4. a green run
        def run(lfrac, tfrac):
            return [fill(lint, lfrac), fill(t13, tfrac), fill(t14, tfrac)]

        self.steps("Open a pull request, and watch. Lint and both tests start at the same moment. Lint is done in seconds.",
                   (0.9, *[travel(a, YELLOW_M, 0.9) for a in pa2]), (1.6, *run(1.0, 0.4)), (1.4, Wait(1.4)))
        m_l = tick(True, 0.17).move_to(mark_pos(lint))
        self.play(Create(m_l), run_time=0.4)
        m_13, m_14 = tick(True, 0.17).move_to(mark_pos(t13)), tick(True, 0.17).move_to(mark_pos(t14))
        m_b = tick(True, 0.17).move_to(mark_pos(build))
        self.steps("Then the tests pass, and only then does build start. When it passes too, every check is green.",
                   (1.4, fill(t13), fill(t14)), (0.5, Create(m_13), Create(m_14)), (0.9, *[travel(a, GREEN_M, 0.9) for a in na]),
                   (2.0, fill(build)), (0.5, Create(m_b)))

        # ---- 5. the ruleset
        gt2 = T("ruleset on main", 26, YELLOW_M).move_to(gt)
        req = T("required checks:", 22, GREY_B).next_to(gt2, DOWN, buff=0.28).align_to(gate, LEFT).shift(RIGHT * 0.3)
        names = ["lint", "test (3.13)", "test (3.14)", "build"]
        rows = VGroup(*[M(n, 22) for n in names]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(req, DOWN, buff=0.25).align_to(req, LEFT)
        self.beat("But green only helps if red stops the merge. On GitHub you get that with a ruleset on main.",
                  Transform(gt, gt2), gate.animate.set_stroke(YELLOW_M), run_time=1.6)
        self.beat("It lists the check names that must pass. Here, all four.",
                  FadeIn(req), LaggedStart(*[FadeIn(r, shift=LEFT * 0.1) for r in rows], lag_ratio=0.25), run_time=2.0)
        rm = VGroup(*[tick(True, 0.14).next_to(r, RIGHT, buff=0.2) for r in rows])
        rm.align_to(rows, RIGHT).shift(RIGHT * 0.45)
        ok = chip("can merge", GREEN_M, 24).move_to([GX, -2.45, 0])
        srcs = [m_l, m_13, m_14, m_b]
        self.steps("When you click merge, GitHub compares the checks on the pull request's newest commit with that list. Every name is there, and green. The merge is allowed.",
                   (1.2, Wait(1.2)), (2.4, LaggedStart(*[TransformFromCopy(s, m) for s, m in zip(srcs, rm)], lag_ratio=0.3)),
                   (1.0, Wait(1.0)), (0.8, FadeIn(ok, shift=UP * 0.1)))

        # ---- 6. a red run: the unused import
        self.play(FadeOut(VGroup(m_l, m_13, m_14, m_b, rm, ok)), empty(lint), empty(t13), empty(t14), empty(build), run_time=0.8)
        bug = M("app.py:3:8: F401 `json` imported but unused", 22, RED_M).move_to([-0.6, 3.25, 0])
        self.beat("Now a teammate's pull request adds import json to app.py, and never uses it.",
                  FadeOut(para), FadeIn(bug, shift=DOWN * 0.1), run_time=1.6)
        x_l = tick(False, 0.15).move_to(mark_pos(lint))
        self.steps("Lint finds it in seconds, and turns red. Ruff exits with code 1, so the step fails.",
                   (0.8, *[travel(a, YELLOW_M, 0.8) for a in pa2]), (1.2, *run(1.0, 0.3)),
                   (0.8, recolor(lint, RED_M), Create(x_l)))
        sk = T("skipped", 22, GREY_B).move_to(build[2])
        self.steps("Both tests still pass. But build is skipped, because one of its needs failed. You hear about the problem without waiting for the slow part.",
                   (1.6, fill(t13), fill(t14)), (0.5, Create(m_13), Create(m_14)),
                   (1.0, skip(build), FadeIn(sk)))
        rx = VGroup(tick(False, 0.12), tick(True, 0.14), tick(True, 0.14), T("skipped", 20, GREY_B))
        for i, m in enumerate(rx):
            m.move_to([rm[i].get_center()[0], rows[i].get_center()[1], 0])
        rx[3].align_to(rows[3], DOWN).next_to(rows[3], RIGHT, buff=0.25)
        blk = chip("merge blocked", RED_M, 24).move_to([GX, -2.45, 0])
        self.steps("The ruleset sees lint failed. The merge is blocked.",
                   (1.2, LaggedStart(*[FadeIn(m) for m in rx], lag_ratio=0.2)), (0.7, Indicate(rows[0], color=RED_M)), (0.6, FadeIn(blk, shift=UP * 0.1)))

        # ---- 7. the trap: require only build
        self.beat("Here is a trap. What if the ruleset required only build?",
                  *[r.animate.set_opacity(0.15) for r in rows[:3]], *[m.animate.set_opacity(0.15) for m in rx[:3]], FadeOut(blk), run_time=1.6)
        trap = chip("can merge", RED_M, 24).move_to([GX, -2.45, 0])
        trap_l = T("a skipped job counts as passed", 24, RED_M).move_to([0.2, -3.25, 0])
        self.steps("A job that was skipped because its needs failed counts as passed. So the broken pull request could merge.",
                   (1.2, Indicate(rx[3], color=YELLOW_M)), (1.4, FadeIn(trap_l, shift=UP * 0.1)), (1.2, Wait(1.2)), (0.8, FadeIn(trap)))
        self.beat("That is why you require the lint and test checks too, and not only build.",
                  *[r.animate.set_opacity(1) for r in rows[:3]], *[m.animate.set_opacity(1) for m in rx[:3]],
                  FadeOut(trap), FadeIn(blk), FadeOut(trap_l), run_time=1.8)

        # ---- 8. the cache
        keep = t14
        others = VGroup(pr, pa2, lint, x_l, t13, m_13, na, nd, build, sk, ga, gate, gt, req, rows, rx, blk, bug)
        self.play(FadeOut(others), FadeOut(m_14), keep.animate.move_to([-4.6, 2.2, 0]), run_time=1.2)
        fresh = T("starts on an empty machine", 22, GREY_B).next_to(keep, DOWN, buff=0.25)
        net = T("download", 22, GREY_B).move_to([-4.6, -1.4, 0])
        pkgs = VGroup(*[Square(0.26, stroke_color=BLUE_M, stroke_width=2).set_fill(tint(BLUE_M, 0.4), 1) for _ in range(6)]).arrange(RIGHT, buff=0.12)
        pkgs.next_to(net, UP, buff=0.25)
        self.steps("One more thing keeps CI quick. Every job starts on an empty machine. So pip install downloads every package again, on every run.",
                   (1.0, FadeIn(fresh), empty(keep)), (1.0, FadeIn(net), FadeIn(pkgs)),
                   (2.0, LaggedStart(*[p.animate.move_to(keep.get_bottom() + DOWN * 0.02 + RIGHT * (i - 2.5) * 0.3).set_opacity(0) for i, p in enumerate(pkgs)], lag_ratio=0.15), fill(keep)))
        self.remove(pkgs)

        # the key
        KY = 0.9
        parts = [("Linux-x64", BLUE_M), ("python-3.14", TEAL_M), ("pip", GREY_B), ("4f9a", GOLD_M)]
        key = VGroup(*[chip(t, c, 22, mono=True) for t, c in parts]).arrange(RIGHT, buff=0.12).move_to([1.6, KY + 1.3, 0])
        klab = T("cache key", 24, YELLOW_M).next_to(key, UP, buff=0.25)
        self.beat("A cache saves files from one run, and restores them in the next. Each entry is stored under a cache key.",
                  FadeIn(klab), FadeOut(net), run_time=1.4)
        reqf = mbox("requirements*.txt", GOLD_M, size=20, h=0.6).move_to([key[3].get_center()[0] - 0.4, KY - 0.2, 0])
        ha = Arrow(reqf.get_top(), key[3].get_bottom(), buff=0.1, stroke_width=2.5, color=GOLD_M, max_tip_length_to_length_ratio=0.2)
        hl = T("hash", 20, GOLD_M).next_to(ha, RIGHT, buff=0.12)
        self.steps("With cache: pip, setup-python builds the key from the runner's OS and CPU, the Python version, and a hash of your requirements files.",
                   (1.4, FadeIn(key[0], shift=DOWN * 0.1)), (1.2, FadeIn(key[1], shift=DOWN * 0.1), FadeIn(key[2], shift=DOWN * 0.1)),
                   (1.4, FadeIn(reqf), GrowArrow(ha), FadeIn(hl), FadeIn(key[3], shift=DOWN * 0.1)))

        # the store
        shelf = RoundedRectangle(corner_radius=0.15, width=8.6, height=2.3, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1).move_to([1.6, -2.15, 0])
        sl = T("saved caches", 22, GREY_B).next_to(shelf.get_top(), DOWN, buff=0.18)
        miss = M('"pip cache is not found"', 22, RED_M).move_to([1.6, -2.25, 0])
        self.steps("On the first run, the store of saved caches is empty. No key matches. That is a miss. The log says pip cache is not found, and pip downloads everything.",
                   (1.2, Create(shelf), FadeIn(sl)), (1.6, Indicate(key, color=YELLOW_M, scale_factor=1.05)), (1.4, Wait(1.4)), (0.8, FadeIn(miss)))
        saved = VGroup(*[chip(t, c, 20, mono=True) for t, c in parts]).arrange(RIGHT, buff=0.1).move_to([1.6, -2.7, 0])
        self.beat("A job that missed saves a new entry when it finishes.",
                  FadeOut(miss), TransformFromCopy(key, saved), run_time=1.6)
        hit = M('"Cache restored from key"', 22, GREEN_M).move_to([1.6, -1.9, 0])
        self.steps("Next run, the same key exists. An exact hit. The files come back, and pip has almost nothing to download.",
                   (0.6, empty(keep)), (1.2, *[Indicate(a[0], color=GREEN_M, scale_factor=1.05) for a in list(key) + list(saved)]),
                   (0.8, FadeIn(hit)), (1.2, fill(keep)))
        # change the requirements
        newh = chip("7c21", GOLD_M, 22, mono=True).move_to(key[3])
        self.steps("Now you change requirements.txt. Its hash changes, so the key changes too. No exact match.",
                   (0.6, FadeOut(hit), empty(keep)), (0.8, Wiggle(reqf)), (1.0, Transform(key[3], newh)), (1.0, Wait(1.0)))
        pref = SurroundingRectangle(VGroup(saved[0], saved[2]), color=YELLOW_M, buff=0.08, corner_radius=0.08)
        pref2 = SurroundingRectangle(VGroup(key[0], key[2]), color=YELLOW_M, buff=0.08, corner_radius=0.08)
        part = M("partial hit: same start, older hash", 22, YELLOW_M).move_to([1.6, -1.9, 0])
        self.steps("But a key with the same start is there. Same OS, same Python, older hash. That is a partial hit. Those older files come back, and pip downloads only what changed.",
                   (1.2, Create(pref2), Create(pref)), (0.8, FadeIn(part)), (2.4, Wait(2.4)), (1.4, fill(keep)))
        gone = T("unused for 7 days: deleted", 22, GREY_B).next_to(shelf, UP, buff=0.12).align_to(shelf, RIGHT)
        self.beat("GitHub deletes caches nobody used for seven days. So treat the cache as a speed-up that can vanish.",
                  FadeOut(pref), FadeOut(pref2), FadeOut(part), saved.animate.set_opacity(0.25), FadeIn(gone), run_time=1.8)
        self.play(FadeOut(VGroup(gone, keep, fresh, key, klab, reqf, ha, hl, shelf, sl, saved)), run_time=0.7)

        # ---- 9. recap
        rc = VGroup(T("lint and tests in parallel, build waits with needs", 30, GOLD_M),
                    T("a matrix: one job per Python version, one check each", 30, TEAL_M),
                    T("a ruleset requires every check by name", 30, YELLOW_M),
                    T("a cache key: OS, Python, hash of requirements", 30, BLUE_M)).arrange(DOWN, buff=0.42)
        self.beat("Cheap checks first, and build waits with needs. A matrix gives one check per Python version. The ruleset requires every check by name. And the cache key decides what comes back.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.5), run_time=5.0)
        self.wait(1.0)
