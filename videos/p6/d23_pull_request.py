import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcount_visit\b", "count visit"), (r"\brecord_visit\b", "record visit"), (r"\bNameError\b", "name error"),
            (r"#(\d+)", r"number \1"), (r"/hello/<name>", "slash hello slash name"), (r"\brename-visit\b", "rename visit"),
            (r"\bhello-name\b", "hello name"), (r"\bPRs?\b", lambda m: "P R" + ("s" if m.group(0).endswith("s") else ""))])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def commit(color=GREY_B, r=0.2, dashed=False):
    c = Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    if dashed:
        c = DashedVMobject(Circle(radius=r, stroke_color=color, stroke_width=3), num_dashes=10)
    return c


def edge(a, b, color=GREY_B, dashed=False, sw=3):
    pa, pb = a.get_center(), b.get_center()
    d = (pb - pa) / np.linalg.norm(pb - pa)
    s, e = pa + d * 0.22, pb - d * 0.22
    return DashedLine(s, e, dash_length=0.1, stroke_width=sw, color=color) if dashed else Line(s, e, stroke_width=sw, color=color)


class D23PullRequest(VoiceScene):
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

    def card(self, num, branch, color, y):
        r = RoundedRectangle(corner_radius=0.12, width=4.6, height=1.75, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
        r.move_to([4.15, y, 0])
        top = VGroup(T(f"PR {num}", 26, color), M(branch, 22)).arrange(RIGHT, buff=0.3)
        top.move_to(r.get_top() + DOWN * 0.38).align_to(r, LEFT).shift(RIGHT * 0.3)
        tested = T("tested against: main at", 22, GREY_B).move_to(r.get_center() + DOWN * 0.05).align_to(r, LEFT).shift(RIGHT * 0.3)
        return VGroup(r, top, tested)

    def construct(self):
        self.title_card("Why a green pull request can still break main", "what CI on a pull request really tests")

        # ---- 0. merging on your own
        MY = 0.0
        mline = Line([-6.4, MY, 0], [1.0, MY, 0], stroke_width=3, color=GREY_B)
        ml = M("main", 22, GREY_B).next_to(mline, UP, buff=0.12).align_to(mline, LEFT)
        m1 = commit(GREY_B).move_to([-5.5, MY, 0])
        self.beat("Day 9 left you with a clean branch on your laptop. You could merge it into main yourself, and push.",
                  Create(mline), FadeIn(ml), GrowFromCenter(m1), run_time=1.8)
        mine = commit(PURPLE_M).move_to([-3.9, 1.4, 0])
        me = edge(m1, mine, PURPLE_M)
        bad = VGroup(T("nobody else read it", 24, RED_M), T("no test ran, unless you ran one", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        bad.move_to([3.6, 1.5, 0])
        mx = commit(PURPLE_M).move_to([-2.3, MY, 0])
        mxe = VGroup(edge(mine, mx, PURPLE_M), edge(m1, mx))
        self.steps("Then nobody else reads the change before it lands. And no test runs on it, unless you ran one.",
                   (1.0, Create(me), GrowFromCenter(mine)), (1.0, Create(mxe), GrowFromCenter(mx)),
                   (1.6, LaggedStart(*[FadeIn(b, shift=LEFT * 0.1) for b in bad], lag_ratio=0.6)))
        self.play(FadeOut(VGroup(mine, me, mx, mxe, bad)), run_time=0.6)

        # ---- 1. a pull request: a page asking to merge
        pr = RoundedRectangle(corner_radius=0.12, width=4.6, height=2.6, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.08), 1).move_to([4.15, 0.6, 0])
        prt = T("pull request", 28, BLUE_M).next_to(pr.get_top(), DOWN, buff=0.25)
        prm = M("main  <-  your-branch", 22).next_to(prt, DOWN, buff=0.3)
        rv = VGroup(T("review the diff", 24), T("checks: ", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(prm, DOWN, buff=0.35)
        ck = VGroup(tick(True, 0.15), tick(False, 0.12)).arrange(RIGHT, buff=0.3).next_to(rv[1], RIGHT, buff=0.2)
        self.beat("A pull request fixes both. It is a page on GitHub that asks to merge your branch into main.",
                  Create(pr), FadeIn(prt), FadeIn(prm), run_time=2.0)
        self.beat("Teammates review the diff there. And checks run on it: automatic tests that show a green tick or a red cross.",
                  FadeIn(rv[0]), Succession(Wait(1.6), AnimationGroup(FadeIn(rv[1]), Create(ck))), run_time=3.2)
        q = T("but what exactly do the checks test?", 28, YELLOW_M).move_to([0, -3.2, 0])
        self.beat("But what exactly do the checks test? Your branch, as it sits? Not quite.",
                  FadeIn(q, shift=UP * 0.15), run_time=2.0)
        self.play(FadeOut(VGroup(pr, prt, prm, rv, ck, q)), run_time=0.6)

        # ---- 2. two teammates, same morning
        A_Y, B_Y = 1.55, -1.55
        a1 = commit(TEAL_M).move_to([-4.1, A_Y, 0])
        b1 = commit(GOLD_M).move_to([-4.1, B_Y, 0])
        ae, be = edge(m1, a1, TEAL_M), edge(m1, b1, GOLD_M)
        al = M("rename-visit", 22, TEAL_M).next_to(a1, UP, buff=0.2)
        bl = M("hello-name", 22, GOLD_M).next_to(b1, DOWN, buff=0.2)
        an = M("count_visit -> record_visit", 20, TEAL_M).move_to([-4.1, 2.6, 0]).align_to(a1, LEFT).shift(LEFT * 0.6)
        bn = M("new /hello/<name> calls count_visit()", 20, GOLD_M).move_to([-4.1, -2.6, 0]).align_to(b1, LEFT).shift(LEFT * 0.6)
        self.beat("Two teammates start from the same main, on the same morning.",
                  Create(ae), GrowFromCenter(a1), Create(be), GrowFromCenter(b1), FadeIn(al), FadeIn(bl), run_time=2.0)
        self.beat("Teammate A renames a function, count_visit, to record_visit. Its one caller changes too.",
                  FadeIn(an, shift=DOWN * 0.1), run_time=1.8)
        self.beat("Teammate B adds a new endpoint, /hello/<name>, and a test for it. It calls count_visit, which was correct that morning.",
                  FadeIn(bn, shift=UP * 0.1), run_time=2.0)

        # PR #12 and the temporary merge commit
        c12 = self.card("#12", "rename-visit", TEAL_M, A_Y)
        c13 = self.card("#13", "hello-name", GOLD_M, B_Y)
        tm = commit(TEAL_M, dashed=True).move_to([-2.4, 0.75, 0])
        tme = VGroup(edge(m1, tm, GREY_B, dashed=True, sw=2), edge(a1, tm, TEAL_M, dashed=True, sw=2))
        tml = T("temporary merge", 20, TEAL_M).next_to(tm, RIGHT, buff=0.2)
        self.beat("A opens pull request 12. Here is the first fact. GitHub builds a temporary merge commit, of the branch into the current main.",
                  FadeIn(c12), Succession(Wait(2.4), AnimationGroup(Create(tme), Create(tm), FadeIn(tml))), run_time=4.0)
        m1l = M("m1", 22, GREY_B).next_to(m1, DOWN, buff=0.2)
        at12 = M("m1", 22, WHITE).next_to(c12[2], RIGHT, buff=0.15)
        t12 = tick(True, 0.2).move_to(c12[0].get_corner(DR) + UL * 0.42)
        self.steps("CI tests that combination. Your branch, plus main as it is right now. Green.",
                   (1.0, FadeIn(m1l), Indicate(tm, color=YELLOW_M)), (1.2, TransformFromCopy(m1l, at12)), (0.8, Create(t12)))
        tm13 = commit(GOLD_M, dashed=True).move_to([-2.4, -0.75, 0])
        tme13 = VGroup(edge(m1, tm13, GREY_B, dashed=True, sw=2), edge(b1, tm13, GOLD_M, dashed=True, sw=2))
        at13 = M("m1", 22, WHITE).next_to(c13[2], RIGHT, buff=0.15)
        t13 = tick(True, 0.2).move_to(c13[0].get_corner(DR) + UL * 0.42)
        self.steps("B opens pull request 13. Same thing: B's branch plus the same main. Also green.",
                   (1.0, FadeIn(c13)), (1.0, FadeOut(tml), Create(tme13), Create(tm13)), (1.0, TransformFromCopy(m1l, at13)), (0.6, Create(t13)))

        # ---- 3. A merges first
        m2 = commit(TEAL_M).move_to([-1.0, MY, 0])
        m2e = VGroup(edge(m1, m2), edge(a1, m2, TEAL_M))
        m2l = M("m2", 22, TEAL_M).move_to(m2.get_center() + np.array([0.42, 0.36, 0]))
        self.steps("A's pull request merges first. Main moves on, to a new commit where count_visit no longer exists.",
                   (0.8, FadeOut(tm), FadeOut(tme), FadeOut(tm13), FadeOut(tme13)), (1.4, Create(m2e), GrowFromCenter(m2), FadeIn(m2l)),
                   (1.0, FadeOut(VGroup(c12, t12, at12))))
        ev = VGroup(chip("opened", BLUE_M, 22), chip("new commits", BLUE_M, 22), chip("reopened", BLUE_M, 22)).arrange(RIGHT, buff=0.25).move_to([4.15, 3.2, 0])
        evl = T("CI on a PR starts only when:", 22, GREY_B).next_to(ev, DOWN, buff=0.18)
        self.beat("Now the second fact. CI starts only when something happens to the pull request itself. It is opened, gets new commits, or is reopened.",
                  LaggedStart(*[FadeIn(e, shift=DOWN * 0.1) for e in ev], lag_ratio=0.3), FadeIn(evl), run_time=3.0)
        stale = SurroundingRectangle(at13, color=YELLOW_M, buff=0.08)
        self.beat("A new commit on main is not an event on B's pull request. So nothing reruns. Its green tick still says main at m1.",
                  Create(stale), Indicate(t13, color=YELLOW_M), run_time=2.6)

        # ---- 4. B merges: main breaks
        m3 = commit(GOLD_M).move_to([0.5, MY, 0])
        m3e = VGroup(edge(m2, m3), edge(b1, m3, GOLD_M))
        m3l = M("m3", 22, GOLD_M).move_to(m3.get_center() + np.array([0.42, -0.36, 0]))
        noc = T("no conflict: different lines", 22, GREEN_M).move_to([-0.3, 0.95, 0])
        self.beat("So B merges too. Git reports no conflict, because the two branches changed different lines.",
                  FadeOut(stale), FadeOut(VGroup(ev, evl)), Create(m3e), GrowFromCenter(m3), FadeIn(m3l), c13.animate.set_opacity(0.35),
                  t13.animate.set_opacity(0.35), at13.animate.set_opacity(0.35), FadeIn(noc), run_time=2.4)
        err = VGroup(M("NameError: name 'count_visit'", 22, RED_M), M("is not defined", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        err.move_to([4.15, 0.6, 0])
        xm = tick(False, 0.22).next_to(m3, UP, buff=0.25)
        self.steps("Then the tests run on main. The new endpoint calls a function that no longer exists. Main is red.",
                   (0.8, FadeOut(noc)), (1.4, Wait(1.4)), (1.0, Create(xm), m3.animate.set_stroke(RED_M)), (1.0, FadeIn(err, shift=LEFT * 0.1)))
        sem = T("semantic conflict", 28, RED_M).move_to([4.15, 1.75, 0])
        sem2 = T("text merged, meaning did not", 22, GREY_B).next_to(err, DOWN, buff=0.3)
        self.beat("This is a semantic conflict. The text merged cleanly, and the meaning did not.",
                  FadeIn(sem, shift=DOWN * 0.1), FadeIn(sem2), run_time=2.2)

        # ---- 5. the fix: require branches to be up to date
        self.beat("Two green pull requests, one broken main. What would have caught it?",
                  Indicate(VGroup(a1, b1), color=GREEN_M), Indicate(m3, color=RED_M), run_time=2.0)
        # rewind: remove m3
        self.play(FadeOut(VGroup(m3, m3e, m3l, xm, err, sem, sem2)), c13.animate.set_opacity(1), t13.animate.set_opacity(1),
                  at13.animate.set_opacity(1), run_time=1.0)
        rule = chip("Require branches to be up to date before merging", YELLOW_M, 22).move_to([0, 3.25, 0])
        self.beat("Rewind to before B merged. A ruleset option, Require branches to be up to date before merging, changes the story.",
                  FadeIn(rule, shift=DOWN * 0.1), run_time=2.2)
        behind = T("behind main", 22, YELLOW_M).move_to(t13).shift(LEFT * 1.15)
        self.steps("B's branch is behind main now. So pull request 13 must take in the new main first. The Update branch button does that.",
                   (1.2, FadeOut(t13), FadeIn(behind)), (2.0, Wait(2.0)),
                   (1.4, Indicate(m2, color=YELLOW_M)))
        tm2 = commit(GOLD_M, dashed=True).move_to([0.5, -0.75, 0])
        tme2 = VGroup(edge(m2, tm2, GREY_B, dashed=True, sw=2), edge(b1, tm2, GOLD_M, dashed=True, sw=2))
        at13b = M("m2", 22, WHITE).move_to(at13)
        x13 = tick(False, 0.18).move_to(t13)
        self.steps("That is a new commit on the pull request, so CI runs again, on B's branch plus the new main.",
                   (1.4, Create(tme2), Create(tm2)), (1.0, Transform(at13, at13b)), (0.8, Indicate(at13, color=YELLOW_M)))
        blk = chip("merge blocked", RED_M, 22).move_to([4.15, -3.05, 0])
        self.steps("The test fails on the pull request, instead of on main. Main stays green.",
                   (0.8, FadeOut(behind), Create(x13), c13[0].animate.set_stroke(RED_M)), (1.0, FadeIn(blk, shift=UP * 0.1)),
                   (0.8, Indicate(m2, color=GREEN_M)))

        # ---- 6. recap
        rc = VGroup(T("a pull request's checks test your branch merged into main,", 30, WHITE),
                    T("as main was the last time the pull request changed", 30, YELLOW_M)).arrange(DOWN, buff=0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)
        self.beat("So remember: a pull request's checks test your branch merged into main, as main was the last time the pull request changed.",
                  FadeIn(rc, shift=UP * 0.1), run_time=2.4)
        self.wait(1.0)
