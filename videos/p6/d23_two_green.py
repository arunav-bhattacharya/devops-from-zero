import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcount_visit\b", "count visit"), (r"\brecord_visit\b", "record visit"), (r"\bNameError\b", "name error"),
            (r"/hello/<name>", "slash hello slash name"), (r"-m 1\b", "dash m one"), (r"\bm1\b", "m one"), (r"\bm2\b", "m two")])

STOCK = "#D9B36C"


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def cook(color):
    body = RoundedRectangle(corner_radius=0.22, width=0.86, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1)
    head = Circle(radius=0.21, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1).next_to(body, UP, buff=0.06)
    hat = RoundedRectangle(corner_radius=0.08, width=0.42, height=0.3, stroke_color=WHITE, stroke_width=2.5).set_fill(BLACK, 1).next_to(head, UP, buff=0.02)
    return VGroup(body, head, hat)


def pot(color):
    body = RoundedRectangle(corner_radius=0.16, width=1.45, height=1.0, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.12), 1)
    rim = Line(LEFT * 0.88, RIGHT * 0.88, stroke_width=6, color=color).move_to(body.get_top())
    hl = Line(LEFT * 0.16, ORIGIN, stroke_width=5, color=color).next_to(body, LEFT, buff=0).shift(UP * 0.2)
    hr = Line(ORIGIN, RIGHT * 0.16, stroke_width=5, color=color).next_to(body, RIGHT, buff=0).shift(UP * 0.2)
    return VGroup(body, rim, hl, hr)


def card(lines, color, w=3.6):
    txt = VGroup(*[T(l, 26) for l in lines]).arrange(DOWN, buff=0.12)
    r = RoundedRectangle(corner_radius=0.1, width=w, height=txt.height + 0.4, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), 1)
    return VGroup(r, txt.move_to(r))


def commit(color=GREY_B, r=0.2, dashed=False):
    if dashed:
        return DashedVMobject(Circle(radius=r, stroke_color=color, stroke_width=3), num_dashes=10)
    return Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)


def edge(a, b, color=GREY_B, dashed=False, sw=3):
    pa, pb = a.get_center(), b.get_center()
    d = (pb - pa) / np.linalg.norm(pb - pa)
    s, e = pa + d * 0.22, pb - d * 0.22
    return DashedLine(s, e, dash_length=0.1, stroke_width=sw, color=color) if dashed else Line(s, e, stroke_width=sw, color=color)


class D23TwoGreen(VoiceScene):
    def prcard(self, num, branch, color, y, result):
        r = RoundedRectangle(corner_radius=0.12, width=4.5, height=1.9, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
        r.move_to([4.15, y, 0])
        top = VGroup(T(f"PR {num}", 26, color), M(branch, 22)).arrange(RIGHT, buff=0.3)
        top.move_to(r.get_top() + DOWN * 0.38).align_to(r, LEFT).shift(RIGHT * 0.3)
        res = T(result, 26).move_to(r.get_center()).align_to(r, LEFT).shift(RIGHT * 0.3)
        tk = tick(True, 0.2).next_to(res, RIGHT, buff=0.3)
        tested = T("tested with main at", 24, GREY_B).move_to(r.get_center() + DOWN * 0.55).align_to(r, LEFT).shift(RIGHT * 0.3)
        return VGroup(r, top, res, tk, tested)

    def construct(self):
        self.title_card("Two green pull requests, one broken main", "what the checks on a pull request really test")

        # ---- 1. the puzzle
        p1 = chip("pull request", PURPLE_M, 28).move_to([-4.2, 1.2, 0])
        p2 = chip("pull request", PURPLE_M, 28).move_to([-4.2, -1.2, 0])
        t1, t2 = tick(True, 0.24).next_to(p1, RIGHT, buff=0.3), tick(True, 0.24).next_to(p2, RIGHT, buff=0.3)
        mainb = box("main", WHITE, w=2.4, h=1.0, size=32).move_to([3.6, 0, 0])
        a1, a2 = edge_arrow(t1, mainb), edge_arrow(t2, mainb)
        self.beat("Here is a puzzle that catches almost every team once. Two pull requests. Both have a green tick.",
                  FadeIn(p1, shift=RIGHT * 0.2), FadeIn(p2, shift=RIGHT * 0.2), Create(t1), Create(t2), run_time=2.0)
        self.beat("Both merge, and Git reports no conflict.", FadeIn(mainb), GrowArrow(a1), GrowArrow(a2), run_time=1.6)
        xm = tick(False, 0.3).next_to(mainb, DOWN, buff=0.35)
        self.beat("And then main is broken. How can two greens make a red?",
                  mainb[0].animate.set_stroke(RED_M), Create(xm), run_time=1.4)
        self.beat("Let's leave code alone for a minute, and walk into a restaurant kitchen.",
                  FadeOut(VGroup(p1, p2, t1, t2, mainb, a1, a2, xm)), run_time=1.0)

        # ---- 2. the kitchen
        book = box("house recipe book", WHITE, w=4.0, h=0.9, size=30).move_to([0, 2.75, 0])
        self.beat("Every cook here works from one house recipe book.", FadeIn(book, shift=DOWN * 0.2), run_time=1.2)
        ca, cb = cook(TEAL_M).move_to([-5.6, 0.75, 0]), cook(GOLD_M).move_to([-5.6, -1.95, 0])
        self.beat("One Friday morning, two cooks each set out to improve it.",
                  FadeIn(ca, shift=UP * 0.2), FadeIn(cb, shift=UP * 0.2), run_time=1.4)
        bp, gp = pot(BLUE_M).move_to([2.0, -0.7, 0]), pot(GREEN_M).move_to([4.8, -0.7, 0])
        bpl = T("blue pot", 26, BLUE_M).next_to(bp, DOWN, buff=0.3)
        gpl = T("green pot", 26, GREEN_M).next_to(gp, DOWN, buff=0.3)
        stock = Rectangle(width=1.2, height=0.5, stroke_width=0).set_fill(STOCK, 0.75).move_to(bp[0].get_bottom() + UP * 0.33)
        self.add(stock)
        stock.set_opacity(0)
        self.beat("The first cook moves the spare stock out of the blue pot, into a new green pot.",
                  FadeIn(bp), FadeIn(bpl), stock.animate.set_fill(STOCK, 0.75), run_time=1.6)
        self.play(FadeIn(gp), FadeIn(gpl), run_time=0.6)
        self.play(stock.animate.move_to(gp[0].get_bottom() + UP * 0.33), run_time=1.2)
        cardA = card(["stock: blue pot"], TEAL_M).move_to([-2.9, 0.75, 0])
        cardA2 = card(["stock: green pot"], TEAL_M).move_to(cardA)
        self.play(FadeIn(cardA, shift=RIGHT * 0.2), run_time=0.6)
        self.beat("Then they fix every recipe card that named the blue pot. Careful work.",
                  Transform(cardA, cardA2), run_time=1.4)
        cardB = card(["new soup: a ladle", "from the blue pot"], GOLD_M).move_to([-2.9, -1.95, 0])
        self.beat("The second cook, working from the breakfast cards, writes a new soup. Its card says: take a ladle from the blue pot.",
                  FadeIn(cardB, shift=RIGHT * 0.2), run_time=1.6)
        ka, kb = tick(True, 0.24).next_to(cardA, RIGHT, buff=0.3), tick(True, 0.24).next_to(cardB, RIGHT, buff=0.3)
        self.beat("Each cook checks their own work. Both changes look fine.", Create(ka), Create(kb), run_time=1.4)
        la = edge_arrow(cardA, book, TEAL_M)
        lb = Arrow(cardB.get_top() + RIGHT * 1.2, book.get_bottom() + RIGHT * 0.6, buff=0.12, stroke_width=3, color=GOLD_M,
                   max_tip_length_to_length_ratio=0.1)
        self.beat("At noon, both changes are in the book. The new soup reaches for the blue pot.",
                  GrowArrow(la), GrowArrow(lb), run_time=1.6)
        ladle = Arrow(cardB.get_right() + UP * 0.1, bp.get_left() + DOWN * 0.15, buff=0.15, stroke_width=4, color=GOLD_M,
                      max_tip_length_to_length_ratio=0.12)
        self.play(GrowArrow(ladle), run_time=0.8)
        empty = tick(False, 0.34).move_to(bp[0])
        self.beat("And the pot is empty.", Create(empty), bp[0].animate.set_stroke(RED_M), run_time=1.0)
        self.beat("Nobody was careless. Each check was honest, and the two changes never touched the same card.",
                  Indicate(ka, color=GREEN_M), Indicate(kb, color=GREEN_M), run_time=2.0)
        combo = T("the trouble lives in the combination", 28, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("The trouble lives in the combination, and nobody tasted the combination. The soup was perfect. For yesterday's kitchen.",
                  FadeIn(combo, shift=UP * 0.15), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. map the kitchen onto GitHub
        hk, hg = T("in the kitchen", 30, GREY_B), T("on GitHub", 30, GREY_B)
        hk.move_to([-3.4, 2.9, 0]); hg.move_to([3.0, 2.9, 0])
        rows = [("the recipe book", "main", "the branch of code everyone uses", WHITE),
                ("a cook's copy", "a branch", "your own line of changes", GOLD_M),
                ("the head chef's desk", "a pull request", "asks to add a branch to main", PURPLE_M),
                ("the taster", "the checks", "automatic tests: tick or cross", GREEN_M)]
        self.beat("Now let's map the kitchen onto GitHub, the website that keeps a team's shared copy of the code.",
                  FadeIn(hk), FadeIn(hg), run_time=1.4)
        says = ["The recipe book is main, the branch of code everyone uses.",
                "A cook's copy is a branch, a separate line of changes where you can work without touching main.",
                "The page on the head chef's desk is a pull request. It asks to add your branch to main, so people and tests can check it first.",
                "And the taster is the checks: automatic tests that show a green tick or a red cross."]
        for i, ((k, g, sub, col), s) in enumerate(zip(rows, says)):
            y = 1.8 - i * 1.4
            lk = T(k, 28).move_to([-3.4, y, 0])
            lg = T(g, 30, col).move_to([3.0, y + 0.18, 0])
            ls = T(sub, 22, GREY_B).next_to(lg, DOWN, buff=0.1)
            ar = Arrow([-1.3, y, 0], [0.8, y, 0], buff=0, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
            self.beat(s, FadeIn(lk), GrowArrow(ar), FadeIn(lg, shift=LEFT * 0.15), FadeIn(ls), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. the same story in hello-devops
        MY = 0.0
        mline = Line([-6.4, MY, 0], [1.0, MY, 0], stroke_width=3, color=WHITE)
        ml = M("main", 22).next_to(mline, UP, buff=0.12).align_to(mline, LEFT)
        m1 = commit(WHITE).move_to([-5.5, MY, 0])
        m1l = M("m1", 22).next_to(m1, DOWN, buff=0.2)
        self.beat("Here is the same story in our lab app, hello-devops, a tiny web app that greets every visitor and counts the visits.",
                  Create(mline), FadeIn(ml), GrowFromCenter(m1), FadeIn(m1l), run_time=2.0)
        A_Y, B_Y = 1.55, -1.55
        ac = commit(TEAL_M).move_to([-4.1, A_Y, 0]); bc = commit(GOLD_M).move_to([-4.1, B_Y, 0])
        ae, be = edge(m1, ac, TEAL_M), edge(m1, bc, GOLD_M)
        an = M("count_visit -> record_visit", 22, TEAL_M).move_to([-3.2, 2.45, 0])
        bn = M("new /hello/<name> calls count_visit()", 22, GOLD_M).move_to([-2.6, -2.45, 0])
        self.beat("Teammate A renames a function, count_visit, to record_visit, and fixes its one caller. That's the stock changing pots.",
                  Create(ae), GrowFromCenter(ac), FadeIn(an, shift=DOWN * 0.1), run_time=2.0)
        self.beat("Teammate B adds a new web address, /hello/<name>, with a test. It calls count_visit, which was correct that morning.",
                  Create(be), GrowFromCenter(bc), FadeIn(bn, shift=UP * 0.1), run_time=2.0)
        c12 = self.prcard("12", "rename-visit", TEAL_M, A_Y, "3 passed")
        c13 = self.prcard("13", "hello-name", GOLD_M, B_Y, "4 passed")
        self.beat("Pull request 12: three tests pass. Pull request 13: four tests pass. Two green ticks.",
                  FadeIn(VGroup(*c12[:3])), Create(c12[3]), Succession(Wait(1.4), AnimationGroup(FadeIn(VGroup(*c13[:3])), Create(c13[3]))), run_time=3.0)
        m2 = commit(TEAL_M).move_to([-1.0, MY, 0]); m3 = commit(GOLD_M).move_to([0.5, MY, 0])
        m2e = VGroup(edge(m1, m2), edge(ac, m2, TEAL_M)); m3e = VGroup(edge(m2, m3), edge(bc, m3, GOLD_M))
        m2l = M("m2", 22, TEAL_M).move_to(m2.get_center() + np.array([0.42, 0.36, 0]))
        noc = T("no conflict: different lines", 24, GREEN_M).move_to([-0.6, 0.95, 0])
        self.beat("Both merge. No conflict, because the branches changed different lines.",
                  Create(m2e), GrowFromCenter(m2), FadeIn(m2l), Succession(Wait(0.6), AnimationGroup(Create(m3e), GrowFromCenter(m3))),
                  FadeIn(noc), run_time=2.4)
        q = T("tests on main: green or red?", 30, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("Now the tests run on main. Pause and guess. Green, or red?", FadeIn(q, shift=UP * 0.15), run_time=1.2)
        self.wait(2.0)
        err = VGroup(M("NameError: name 'count_visit'", 22, RED_M), M("is not defined", 22, RED_M),
                     M("1 failed, 3 passed", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([4.15, 0.0, 0])
        xm3 = tick(False, 0.22).next_to(m3, UP, buff=0.25)
        self.beat("Red. NameError: name count_visit is not defined. One failed, three passed.",
                  FadeOut(q), FadeOut(noc), FadeOut(c12), FadeOut(c13), Create(xm3), m3.animate.set_stroke(RED_M),
                  FadeIn(err, shift=LEFT * 0.1), run_time=1.8)
        self.beat("Well. That's not the lunch we planned. The new address calls a function that no longer exists.",
                  Indicate(bn, color=GOLD_M), run_time=1.6)
        sem = T("semantic conflict", 32, RED_M).move_to([4.15, 1.6, 0])
        sem2 = T("the text merged, the meaning did not", 24, GREY_B).move_to([4.15, -1.4, 0])
        self.beat("Now that you've seen it, it gets a name: a semantic conflict. The text merged cleanly. The meaning did not.",
                  FadeIn(sem, shift=DOWN * 0.1), Succession(Wait(1.6), FadeIn(sem2)), run_time=3.0)

        # ---- 5. what did the tick really promise?
        self.play(FadeOut(VGroup(m3, m3e, xm3, err, sem, sem2)), run_time=0.8)
        c13 = self.prcard("13", "hello-name", GOLD_M, B_Y, "4 passed")
        qq = T("what did this tick promise?", 28, YELLOW_M).move_to([4.15, 0.3, 0])
        self.beat("Let's rewind to just before 13 merged. What did its green tick really promise? Most of us read it as: my branch works with main.",
                  FadeIn(VGroup(*c13[:3])), Create(c13[3]), FadeIn(qq), run_time=2.2)
        self.beat("That's almost right, and the almost is the bug.", Indicate(qq, color=YELLOW_M), run_time=1.2)
        tm = commit(GOLD_M, dashed=True).move_to([-2.6, -0.8, 0])
        tme = VGroup(edge(m1, tm, GREY_B, dashed=True, sw=2), edge(bc, tm, GOLD_M, dashed=True, sw=2))
        tml = T("temporary merge", 24, GOLD_M).next_to(tm, RIGHT, buff=0.2)
        self.beat("Fact one. GitHub builds a temporary merge commit, your branch joined with the current main, and the checks test that combination.",
                  FadeOut(qq), Create(tme), Create(tm), FadeIn(tml), run_time=2.4)
        at13 = M("m1", 22).next_to(c13[4], RIGHT, buff=0.15)
        self.beat("When pull request 13 was opened, main was at m1. So: green, with m1.",
                  FadeIn(c13[4]), TransformFromCopy(m1l, at13), run_time=2.0)
        ev = VGroup(chip("opened", PURPLE_M, 24), chip("new commits", PURPLE_M, 24), chip("reopened", PURPLE_M, 24)).arrange(RIGHT, buff=0.25)
        evl = T("checks start only when the PR is:", 24, GREY_B)
        evg = VGroup(evl, ev).arrange(DOWN, buff=0.2).move_to([3.4, 2.75, 0])
        self.beat("Fact two. The checks start only when something happens to the pull request itself. It is opened, it gets new commits, or it is reopened.",
                  FadeOut(tml), FadeIn(evl), LaggedStart(*[FadeIn(e, shift=DOWN * 0.1) for e in ev], lag_ratio=0.3), run_time=3.0)
        self.beat("Now pull request 12 merges, and main moves on to m2. Is that an event on pull request 13?",
                  FadeOut(tm), FadeOut(tme), Indicate(m2, color=TEAL_M), run_time=2.0)
        stale = SurroundingRectangle(at13, color=YELLOW_M, buff=0.08)
        self.beat("No. Nothing reruns. The tick still says m1.", Create(stale), run_time=1.2)
        lab = T("green, as of yesterday's main", 26, YELLOW_M).next_to(c13[0], UP, buff=0.2)
        self.beat("Honestly, that tick should come with a label: green, as of yesterday's main.",
                  FadeIn(lab, shift=UP * 0.1), run_time=1.6)
        self.beat("A tick is a photo of one moment. It is not a live camera.", Indicate(c13[3], color=GREEN_M), run_time=1.4)

        # ---- 6. the fix: taste it in today's kitchen
        self.play(FadeOut(VGroup(lab, stale, evg)), run_time=0.6)
        rule = chip("Require branches to be up to date before merging", YELLOW_M, 24).move_to([0, 3.0, 0])
        self.beat("So the wish is simple: taste the soup in today's kitchen.", run_time=None)
        self.beat("A ruleset, a set of rules for a branch, has an option for exactly that. Require branches to be up to date before merging. Day 25 builds one.",
                  FadeIn(rule, shift=DOWN * 0.1), run_time=2.0)
        behind = T("behind main", 24, YELLOW_M).move_to(c13[3]).shift(LEFT * 0.95)
        self.beat("Pull request 13 is now behind main, so it cannot merge yet. The Update branch button brings the new main into the branch.",
                  FadeOut(c13[3]), FadeOut(c13[2]), FadeIn(behind), Succession(Wait(2.2), Indicate(m2, color=TEAL_M)), run_time=3.4)
        tm2 = commit(GOLD_M, dashed=True).move_to([0.5, -0.8, 0])
        tme2 = VGroup(edge(m2, tm2, GREY_B, dashed=True, sw=2), edge(bc, tm2, GOLD_M, dashed=True, sw=2))
        at2 = M("m2", 22).move_to(at13)
        self.beat("That is a new commit on the pull request, so the checks run again, on B's branch plus m2.",
                  Create(tme2), Create(tm2), Transform(at13, at2), run_time=2.2)
        x13 = tick(False, 0.2).move_to(behind.get_right() + RIGHT * 0.5)
        res2 = T("1 failed", 26, RED_M).move_to(behind, aligned_edge=LEFT)
        blk = chip("merge blocked", RED_M, 24).move_to([4.15, -3.05, 0])
        self.beat("Red, on the pull request instead of on main. The merge is blocked, and main stays green.",
                  Transform(behind, res2), Create(x13), c13[0].animate.set_stroke(RED_M), tm2.animate.set_color(RED_M),
                  FadeIn(blk, shift=UP * 0.1), Succession(Wait(1.6), Indicate(m2, color=GREEN_M)), run_time=3.0)
        rv = M("git revert -m 1 --no-edit HEAD", 24).move_to([-2.7, -3.15, 0])
        self.beat("And if a break does slip through, undo it with a new commit. A merge commit has two parents, so -m 1 tells revert to keep the first one, main's side.",
                  FadeIn(rv, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. guardrails
        gq = T("Should every repository turn the rule on?", 34).move_to([0, 2.85, 0])
        self.beat("Should every repository turn this rule on? Mostly, yes. But it has a cost.", FadeIn(gq), run_time=1.4)
        g1 = card(["busy repository:", "update, rerun, update, rerun"], YELLOW_M, w=5.6).move_to([-3.25, 1.0, 0])
        g2 = card(["many PRs an hour:", "a merge queue"], PURPLE_M, w=5.6).move_to([3.25, 1.0, 0])
        g3 = card(["cheapest guard:", "small branches, merged in a day or two"], TEAL_M, w=7.4).move_to([0, -1.7, 0])
        self.beat("On a busy repository, people keep updating their branches and rerunning the checks.",
                  FadeIn(g1, shift=UP * 0.15), run_time=1.4)
        self.beat("When many pull requests land every hour, teams use a merge queue. GitHub tests main plus the pull requests ahead of yours, and merges only when that passes.",
                  FadeIn(g2, shift=UP * 0.15), run_time=1.6)
        self.beat("And the cheapest guard costs nothing: small branches, merged within a day or two. Less time waiting means less time for main to move under you.",
                  FadeIn(g3, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 8. moral and a quick check
        mo = VGroup(T("a pull request's checks test your branch merged into main,", 30),
                    T("as main was the last time the pull request changed", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 1.6, 0])
        self.beat("So here's the moral. A pull request's checks test your branch merged into main, as main was the last time the pull request changed.",
                  FadeIn(mo[0], shift=UP * 0.1), Succession(Wait(2.4), FadeIn(mo[1], shift=UP * 0.1)), run_time=4.0)
        tk = T("Two honest checks can miss the combination. Taste it in today's kitchen.", 28, GREY_B).next_to(mo, DOWN, buff=0.6)
        self.beat("Two honest checks can still miss the combination. So taste it in today's kitchen.", FadeIn(tk), run_time=1.4)
        qc = VGroup(T("Quick check", 28, GOLD_M),
                    T("Your PR went green yesterday. This morning, main got a new commit.", 26),
                    T("Has your check run again?", 26)).arrange(DOWN, buff=0.2).move_to([0, -2.1, 0])
        self.beat("Quick check. Your pull request went green yesterday. This morning, a teammate merged into main. Has your check run again? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("No: nothing happened to your PR. Press Update branch.", 26, GREEN_M).move_to(qc[2])
        self.beat("No. Nothing happened to your pull request, so nothing reran. Press Update branch, or let the ruleset insist.",
                  Transform(qc[2], ans), run_time=1.4)
        self.wait(1.2)
