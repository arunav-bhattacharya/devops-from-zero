import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bruff\b", "ruff"), (r"\bpytest\b", "pie test"), (r"needs: \[lint, test\]", "needs lint and test"),
            (r"\b3\.13\b", "three thirteen"), (r"\b3\.14\b", "three fourteen"), (r"\b3\.15\b", "three fifteen"),
            (r"\bcancel-in-progress\b", "cancel in progress"), (r"\btimeout-minutes\b", "timeout minutes")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def plate(color=WHITE, s=1.0):
    o = Circle(radius=0.32, stroke_color=color, stroke_width=3).set_fill(BLACK, 1)
    i = Circle(radius=0.18, stroke_color=color, stroke_width=2)
    return VGroup(o, i).scale(s)


def person(color, s=1.0):
    body = RoundedRectangle(corner_radius=0.22, width=0.86, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1)
    head = Circle(radius=0.21, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1).next_to(body, UP, buff=0.06)
    return VGroup(body, head).scale(s)


def bar(x0, w, y, color, label):
    r = RoundedRectangle(corner_radius=0.08, width=w, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.18), 1)
    r.move_to([x0 + w / 2, y, 0])
    t = M(label, 22, color).move_to(r)
    return VGroup(r, t)


class D25RedMeansStop(VoiceScene):
    def construct(self):
        self.title_card("When red does not mean stop", "quick checks first, a fridge, and a rule on main")

        # ---- 1. the question
        pr = box("pull request", PURPLE_M, w=3.4, h=0.9).move_to([-2.0, 0.6, 0])
        xr = tick(False, 0.28).next_to(pr, RIGHT, buff=0.4)
        tl = T("a test failed", 28, RED_M).next_to(xr, RIGHT, buff=0.3)
        self.beat("A test fails on your pull request. There's the red cross, right on the page.",
                  FadeIn(pr), Create(xr), FadeIn(tl), run_time=1.8)
        q = T("can it still be merged?", 32, YELLOW_M).move_to([0, -1.2, 0])
        self.beat("So, can it still be merged? Most of us would say: of course not, it's red. Keep your answer. We'll test it at the end.",
                  FadeIn(q, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(pr, xr, tl, q)), run_time=0.6)

        # ---- 2. the kitchen's first Saturday
        taster = person(GREEN_M).move_to([0.6, 0.2, 0])
        tsl = T("the taster", 26, GREEN_M).next_to(taster, DOWN, buff=0.2)
        pile = VGroup(*[plate().move_to([-1.5 - 0.75 * i, 0.2, 0]) for i in range(5)])
        self.beat("Picture our kitchen on its first Saturday with a real taster at the pass. She is careful, and that is the problem.",
                  FadeIn(taster), FadeIn(tsl), run_time=1.6)
        tr1 = T("plates pile up", 26, GOLD_M).move_to([-3.0, 1.4, 0])
        self.beat("Plates pile up, while every dish waits its turn.",
                  LaggedStart(*[FadeIn(p, shift=RIGHT * 0.3) for p in pile], lag_ratio=0.2), FadeIn(tr1), run_time=1.6)
        tr2 = T("stock boiled from bones every morning", 26, TEAL_M).move_to([3.4, 2.6, 0])
        self.beat("Each morning the stock is boiled again from bones, because the fridge is emptied every night.",
                  FadeIn(tr2), run_time=1.6)
        waiter = person(GREY_B, 0.8).move_to([3.2, -1.8, 0])
        out = pile[4].copy()
        self.add(out); pile[4].set_opacity(0)
        tr3 = T("a plate nobody tasted", 26, RED_M).move_to([3.2, -3.1, 0])
        self.beat("Then a waiter in a hurry carries one plate out before the taster reaches it. Of course, that's the plate with the wrong sauce.",
                  FadeIn(waiter), out.animate.move_to([4.6, -1.8, 0]).set_stroke(RED_M), Succession(Wait(1.4), FadeIn(tr3)), run_time=3.0)
        mor = T("a slow check gets skipped, and so does an optional one", 28, YELLOW_M).move_to([0, -3.3, 0])
        self.beat("It's easy to blame the waiter. But a check that is slow gets skipped, and so does a check that is optional. People aren't careless. They're busy.",
                  FadeOut(tr3), FadeIn(mor), run_time=2.0)
        self.beat("Three troubles: slow, forgetful, optional. Let's fix them one at a time, starting with slow.",
                  Indicate(tr1, color=GOLD_M), Indicate(tr2, color=TEAL_M), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. quick checks first: the pipeline in time
        hdr = T("one pipeline, over time", 28, GREY_B).move_to([-1.2, 3.1, 0])
        axis = Arrow([-4.3, -2.2, 0], [3.0, -2.2, 0], buff=0, stroke_width=2, color=GREY_B, max_tip_length_to_length_ratio=0.03)
        axl = T("time", 24, GREY_B).next_to(axis, DOWN, buff=0.12).align_to(axis, RIGHT)
        self.beat("A good pass doesn't taste every plate first. It glances. Right table, right dish, still hot? Only plates that pass the glance get the slow taste.",
                  FadeIn(hdr), Create(axis), FadeIn(axl), run_time=2.4)
        X0 = -4.2
        lint = bar(X0, 1.0, 1.7, YELLOW_M, "lint")
        t13 = bar(X0, 3.4, 0.6, BLUE_M, "test (3.13)")
        t14 = bar(X0, 3.4, -0.5, BLUE_M, "test (3.14)")
        self.beat("So the lab's pipeline starts with lint. Ruff reads your code without running it, and flags style problems and likely bugs. It takes seconds.",
                  GrowFromEdge(lint, LEFT), run_time=1.6)
        self.beat("At the same moment, the tests run with pytest. Jobs run in parallel by default, each on its own fresh runner.",
                  GrowFromEdge(t13, LEFT), run_time=1.8)
        mx = M('matrix: python-version: ["3.13", "3.14"]', 22, BLUE_M).move_to([-0.5, -1.45, 0])
        self.beat("And with a matrix, one job written once runs twice, once per Python version. Like testing one recipe in two ovens. Two checks, almost no extra waiting.",
                  GrowFromEdge(t14, LEFT), FadeIn(mx), run_time=2.2)
        bx = t13[0].get_right()[0] + 0.15
        build = bar(bx, 2.4, 1.15, PURPLE_M, "build")
        nd = M("needs: [lint, test]", 22, PURPLE_M).next_to(build, UP, buff=0.2)
        self.beat("Building the Docker image is the slowest check, so it waits. needs: [lint, test] means build starts only after all of them succeed.",
                  GrowFromEdge(build, LEFT), FadeIn(nd), run_time=2.2)
        xl = tick(False, 0.2).next_to(lint, RIGHT, buff=0.2)
        skip = DashedVMobject(build[0].copy().set_fill(opacity=0), num_dashes=40).set_color(GREY_B)
        skl = T("skipped", 24, GREY_B).move_to(build)
        self.beat("If lint fails, build is skipped. You hear about the failure in seconds, without waiting for the slow part.",
                  Create(xl), lint[0].animate.set_stroke(RED_M), FadeOut(build), FadeIn(skip), FadeIn(skl), run_time=2.2)
        self.beat("Remember that skipped box. It comes back.", Indicate(skl, color=GREY_B), run_time=1.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. the fridge: a cache and its label
        self.beat("Trouble two, forgetful. Every job starts on an empty machine, so pip downloads every package again on every run. Stock boiled from bones.",
                  run_time=None)
        fridge = RoundedRectangle(corner_radius=0.15, width=3.0, height=3.6, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.08), 1).move_to([-4.3, 0.2, 0])
        fl = T("cache", 28, TEAL_M).next_to(fridge, UP, buff=0.15)
        jars = VGroup(*[chip(t, TEAL_M, 22) for t in ("pytest", "ruff", "flask")]).arrange(DOWN, buff=0.3).move_to(fridge)
        self.beat("A cache is the fridge. It saves files from one run, such as downloaded packages, and restores them in the next.",
                  Create(fridge), FadeIn(fl), LaggedStart(*[FadeIn(j) for j in jars], lag_ratio=0.3), run_time=2.0)
        label = VGroup(M("Linux-x64", 22), M("python-3.14", 22), M("pip", 22), M("hash: 9c41", 22, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        lbox = SurroundingRectangle(label, color=WHITE, buff=0.2, corner_radius=0.08).set_fill(BLACK, 1)
        lab = VGroup(lbox, label).move_to([1.0, 0.6, 0])
        ll = T("the cache key", 26).next_to(lab, UP, buff=0.2)
        self.beat("Each entry is stored under a cache key, a label for what's inside. A good fridge label says which recipe and which day. This one says: the system, the Python version, pip.",
                  FadeIn(lab, shift=LEFT * 0.2), FadeIn(ll), run_time=2.4)
        hn = T("hash: a fingerprint of the requirements files", 24, YELLOW_M).next_to(lab, DOWN, buff=0.35)
        self.beat("And a hash, a short fingerprint computed from your requirements files, the lists of packages to install.",
                  FadeIn(hn), run_time=1.6)
        hit = T("same key: Cache restored from key", 26, GREEN_M).move_to([1.0, -2.6, 0])
        self.beat("Next run, same files, same key. The log says: Cache restored from key. Seconds, not minutes.",
                  FadeIn(hit), run_time=1.6)
        q2 = T("change one letter in requirements.txt?", 26, YELLOW_M).move_to([1.0, 3.1, 0])
        self.beat("Now change one letter in a requirements file. Pause and guess. Same label, or a new one?",
                  FadeIn(q2), run_time=1.4)
        self.wait(2.0)
        newh = M("hash: 7e02", 22, RED_M).move_to(label[3], aligned_edge=LEFT)
        miss = T("new key: no exact match, so pip downloads what changed", 24, GOLD_M).move_to(hit)
        self.beat("A new one. The hash changes, so the key changes. GitHub restores an older entry with the same start, and pip downloads only what changed. Then the job saves a fresh entry.",
                  Transform(label[3], newh), Transform(hit, miss), run_time=2.2)
        warn = T("a speed-up that can vanish: never rely on it, never put secrets in it", 26, RED_M).move_to([0, -3.35, 0])
        self.beat("One rule for fridges. GitHub deletes caches nobody used for seven days. So a cache is a speed-up that can vanish. Never rely on it, and never put secrets in it.",
                  FadeOut(hn), FadeOut(q2), FadeIn(warn), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. optional: the waiter, and the ruleset
        X0 = -6.0
        lint = bar(X0, 1.0, 2.2, YELLOW_M, "lint")
        t13 = bar(X0, 3.0, 1.1, BLUE_M, "test (3.13)")
        t14 = bar(X0, 3.0, 0.0, BLUE_M, "test (3.14)")
        build = bar(-2.8, 2.2, 1.1, PURPLE_M, "build")
        self.beat("Trouble three, optional. Our pipeline is fast now. But a red check still stops nobody from clicking merge.",
                  FadeIn(VGroup(lint, t13, t14, build)), run_time=1.6)
        rs = RoundedRectangle(corner_radius=0.12, width=4.2, height=2.4, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.08), 1).move_to([3.9, 1.0, 0])
        rst = T("ruleset on main", 28, GOLD_M).next_to(rs.get_top(), DOWN, buff=0.25)
        rq = VGroup(T("required check:", 24, GREY_B), M("build", 24, PURPLE_M)).arrange(RIGHT, buff=0.2).move_to(rs).shift(DOWN * 0.15)
        self.beat("On GitHub, the fix is a ruleset on main: a named list of rules, such as: these checks must pass before a pull request can merge.",
                  Create(rs), FadeIn(rst), run_time=2.0)
        self.beat("Here's a tempting shortcut. Build waits for everything, so let's require only build. If build passed, everything passed. Right?",
                  FadeIn(rq), Indicate(build[1], color=PURPLE_M), run_time=2.2)
        x14 = tick(False, 0.2).next_to(t14, RIGHT, buff=0.2)
        self.beat("Now a test fails. Pause and guess: can this pull request merge?",
                  t14[0].animate.set_stroke(RED_M), t14[1].animate.set_color(RED_M), Create(x14), run_time=1.4)
        self.wait(2.0)
        skip = DashedVMobject(build[0].copy().set_fill(opacity=0), num_dashes=40).set_color(GREY_B)
        skl = T("skipped", 24, GREY_B).move_to(build)
        self.beat("Build needs the tests, so build is skipped. That skipped box again.",
                  FadeOut(build), FadeIn(skip), FadeIn(skl), run_time=1.6)
        cnt = T("skipped counts as passed", 28, RED_M).move_to([3.9, -1.0, 0])
        mb = chip("Merge", GREEN_M, 28).move_to([3.9, -2.2, 0])
        self.beat("And a job skipped because a job it needs failed counts as passed. The ruleset sees build: fine. The merge button lights up.",
                  FadeIn(cnt, shift=UP * 0.1), Succession(Wait(1.8), FadeIn(mb, shift=UP * 0.1)), run_time=3.0)
        self.beat("Well. The waiter just carried out the plate with the wrong sauce. Nobody broke a rule. The rule had a hole.",
                  Indicate(mb, color=RED_M), run_time=2.0)
        rq2 = VGroup(M("lint", 24, YELLOW_M), M("test (3.13)", 24, BLUE_M), M("test (3.14)", 24, BLUE_M), M("build", 24, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        rq2.move_to(rs).shift(DOWN * 0.3)
        blk = chip("Merging is blocked", RED_M, 26).move_to(mb)
        self.beat("The fix: require every check by its exact name. lint, test 3.13, test 3.14, and build. Now the failed test itself is required, and red means stop.",
                  FadeOut(rq), FadeOut(cnt), rs.animate.stretch_to_fit_height(2.7).shift(DOWN * 0.15), FadeIn(rq2), Transform(mb, blk), run_time=2.8)
        self.beat("Each of those is called a required status check. Two more details catch people. A new ruleset starts as Disabled, so set it to Active. And on the Free plan, rulesets are only enforced on public repositories.",
                  Indicate(rst, color=GOLD_M), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. guardrail: keep it fast enough that nobody skips it
        gt = T("Keep it fast, or people work around it", 34).move_to([0, 2.9, 0])
        self.beat("Last guardrail. A slow pipeline brings back trouble one: people stop waiting, or pile many changes into one big pull request.",
                  FadeIn(gt), run_time=1.6)
        g1 = chip("concurrency + cancel-in-progress: stop cooking the old order", TEAL_M, 26).move_to([0, 1.4, 0])
        g2 = chip("timeout-minutes: stop a hung job early", GOLD_M, 26).move_to([0, 0.3, 0])
        g3 = chip("no path filter on pull_request when its checks are required", RED_M, 26).move_to([0, -0.8, 0])
        self.beat("Concurrency with cancel-in-progress cancels a stale run when you push again. The table changed its order, so you stop cooking the old dish.",
                  FadeIn(g1, shift=UP * 0.1), run_time=1.6)
        self.beat("timeout-minutes stops a hung job early.", FadeIn(g2, shift=UP * 0.1), run_time=1.0)
        self.beat("And never put a path filter on pull_request when its checks are required. A docs-only pull request never runs the workflow, so its checks stay Pending forever, and block the merge.",
                  FadeIn(g3, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. moral, loop payoff, quick check
        mo = VGroup(T("quick checks first, a fridge for downloads,", 30),
                    T("and every check required by name", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.3, 0])
        self.beat("So, the moral. Slow gets skipped, so put quick checks first. Forgetful costs minutes, so give it a fridge. Optional gets skipped, so require every check by name.",
                  FadeIn(mo[0]), Succession(Wait(2.8), FadeIn(mo[1])), run_time=4.4)
        back = T("can a red pull request merge? only if your rule has a hole", 26, GREY_B).next_to(mo, DOWN, buff=0.4)
        self.beat("And the question from the start? A red pull request can merge, if your rule has a hole in it.", FadeIn(back), run_time=1.6)
        qc = VGroup(T("Quick check", 28, GOLD_M),
                    T('Next year you add "3.15" to the matrix, and forget the ruleset.', 26),
                    T("Is the new test check required?", 26)).arrange(DOWN, buff=0.22).move_to([0, -1.6, 0])
        self.beat("Quick check. Next year you add Python 3.15 to the matrix, and forget to touch the ruleset. Is the new check required? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("No: the ruleset only knows the names you gave it.", 26, GREEN_M).move_to(qc[2])
        self.beat("No. The ruleset only knows the names you gave it. A new check stays optional until you add it.",
                  Transform(qc[2], ans), run_time=1.4)
        self.wait(1.2)
