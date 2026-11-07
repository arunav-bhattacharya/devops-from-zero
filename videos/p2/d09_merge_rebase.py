import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

MAIN_C, FEAT_C, MERGE_C, PTR_C = BLUE_M, GOLD_M, PURPLE_M, GREY_B
TOP, BOT = 0.85, -0.75


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def late(a, b=1.0, f=smooth):
    """Rate function that waits until fraction a of the animation, then runs f until fraction b."""
    return lambda t: f(float(np.clip((t - a) / (b - a), 0, 1)))


def node(letter, color, r=0.36, size=30):
    c = Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    return VGroup(c, T(letter, size).move_to(c))


def back(a, b, color=GREY_B):
    """Arrow from commit a back to its parent b, edge to edge."""
    return edge_arrow(a, b, color, buff=0.06)


def btag(text, color):
    return chip(text, color, size=24, mono=True)


class D09MergeRebase(VoiceScene):
    def construct(self):
        self.title_card("Merge or rebase?", "two ways to bring lines of work together")

        X = {"A": -5.4, "B": -3.6, "C": -1.8, "D": -1.8, "E": 0.0}
        A, B = node("A", MAIN_C).move_to([X["A"], TOP, 0]), node("B", MAIN_C).move_to([X["B"], TOP, 0])
        ab = back(B, A)
        main_t = btag("main", MAIN_C).next_to(B, UP, buff=0.35)
        self.beat("Sooner or later, two lines of work have to come together. Git gives you two ways to do it: merge and rebase.",
                  GrowFromCenter(A), GrowFromCenter(B), GrowArrow(ab), FadeIn(main_t, shift=DOWN * 0.15), run_time=2.0)

        # ---------- 1. fast-forward
        D, E = node("D", FEAT_C).move_to([X["D"], TOP, 0]), node("E", FEAT_C).move_to([X["E"], TOP, 0])
        dB, eD = back(D, B), back(E, D)
        feat_t = btag("feature", FEAT_C).next_to(E, DOWN, buff=0.35)
        self.beat("You start a branch called feature, and make two commits on it, D and E. Meanwhile, main stays where it was.",
                  LaggedStart(AnimationGroup(GrowArrow(dB), GrowFromCenter(D)), AnimationGroup(GrowArrow(eD), GrowFromCenter(E)), lag_ratio=0.5),
                  FadeIn(feat_t, shift=UP * 0.15), Indicate(main_t, color=MAIN_C, rate_func=late(0.6, 1.0, there_and_back)), run_time=3.0)

        on = T("on main:", 26, GREY_B)
        cmd = M("$ git merge feature", 28)
        cmdg = VGroup(on, cmd).arrange(RIGHT, buff=0.3).move_to(UP * 3.4)
        self.beat("Now you switch to main, and run git merge feature.", FadeIn(on), Write(cmd), run_time=1.6)
        main_t2 = btag("main", MAIN_C).next_to(E, UP, buff=0.35)
        self.beat("main gained no commits since feature split off from it. So git simply moves the main pointer forward, to E. It creates nothing new.",
                  Transform(main_t, main_t2, rate_func=late(0.35)), run_time=2.4)
        ff = M("Fast-forward", 26, GREEN_M).next_to(cmdg, DOWN, buff=0.25)
        line = VGroup(A, B, D, E)
        self.beat("That is called a fast-forward, and git prints exactly that. History stays one straight line.",
                  FadeIn(ff, shift=DOWN * 0.1), Indicate(line, color=YELLOW_M, scale_factor=1.05, rate_func=late(0.4, 1.0, there_and_back)), run_time=2.2)

        # ---------- 2. three-way merge
        C = node("C", MAIN_C).move_to([X["C"], TOP, 0])
        cB = back(C, B)
        main_t3 = btag("main", MAIN_C).next_to(C, UP, buff=0.35)
        D2, E2 = D.copy().move_to([X["D"], BOT, 0]), E.copy().move_to([X["E"], BOT, 0])
        self.beat("Now a different story. While you worked on feature, someone added a commit C to main.",
                  FadeOut(ff), D.animate.move_to(D2), E.animate.move_to(E2), feat_t.animate.next_to(E2, DOWN, buff=0.35),
                  Transform(dB, back(D2, B)), Transform(eD, back(E2, D2)), FadeOut(main_t),
                  Succession(Wait(1.0), AnimationGroup(GrowFromCenter(C), GrowArrow(cB), FadeIn(main_t3, shift=DOWN * 0.15))), run_time=2.8)
        main_t = main_t3

        ring = Circle(radius=0.52, stroke_color=YELLOW_M, stroke_width=4).move_to(B)
        base_l = T("merge base", 26, YELLOW_M).next_to(ring, UP, buff=0.15)
        self.beat("Both branches have new commits now, so a fast-forward is impossible. Git finds the merge base: the newest commit that both branches contain. Here, that is B.",
                  Succession(Wait(3.0), AnimationGroup(Create(ring), FadeIn(base_l, shift=DOWN * 0.1))), run_time=4.4)

        def vbox(head, val, color):
            g = VGroup(T(head, 24, color), M(f"TAX_RATE = {val}", 22)).arrange(DOWN, buff=0.15)
            r = RoundedRectangle(corner_radius=0.12, width=2.75, height=g.height + 0.4, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.12), 1)
            return VGroup(r, g.move_to(r))
        vb = vbox("base B", "0.20", YELLOW_M).move_to([-4.75, -3.05, 0])
        vm = vbox("main C", "0.25", MAIN_C).move_to([-1.75, -3.05, 0])
        vf = vbox("feature E", "0.20", FEAT_C).move_to([1.25, -3.05, 0])
        self.beat("Then it compares each side with the base. Say the base has a tax rate of 0.20. main changed it to 0.25, and feature still has 0.20.",
                  LaggedStart(FadeIn(vb, shift=UP * 0.15), FadeIn(vm, shift=UP * 0.15), FadeIn(vf, shift=UP * 0.15), lag_ratio=0.6), run_time=4.0)
        res = vbox("result", "0.25", GREEN_M).move_to([4.75, -3.05, 0])
        r_a = Arrow(vf.get_right(), res.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        self.beat("Only main changed that line, so git takes 0.25. Without the base, git would see two different lines, and could not tell which side changed.",
                  Indicate(vm, color=MAIN_C, scale_factor=1.06), GrowArrow(r_a, rate_func=late(0.3)), FadeIn(res, shift=LEFT * 0.15, rate_func=late(0.4)), run_time=2.8)
        conf = T("both sides changed the same line, differently?  a conflict: git stops and asks you", 24, RED_M).move_to(DOWN * 3.05)
        self.beat("If both sides had changed that same line in different ways, that would be a conflict, and git would stop and ask you.",
                  FadeOut(VGroup(vb, vm, vf, res, r_a)), FadeIn(conf, rate_func=late(0.3)), run_time=2.0)

        Mn = node("M", MERGE_C).move_to([1.8, TOP, 0])
        mC, mE = back(Mn, C, MERGE_C), back(Mn, E, MERGE_C)
        two = T("two parents", 26, MERGE_C).next_to(Mn, RIGHT, buff=0.3)
        self.beat("So git combines the two sets of changes into a new merge commit, M. It has two parents: C, and E.",
                  FadeOut(conf), FadeOut(ring), FadeOut(base_l), GrowFromCenter(Mn), GrowArrow(mC, rate_func=late(0.3)), GrowArrow(mE, rate_func=late(0.45)),
                  FadeIn(two, rate_func=late(0.5)), run_time=2.6)
        main_t4 = btag("main", MAIN_C).next_to(Mn, UP, buff=0.35)
        safe = VGroup(tick(True, 0.22), T("history shows both lines.  safe on shared branches", 26, GREEN_M)).arrange(RIGHT, buff=0.25).move_to(DOWN * 3.05)
        self.beat("main moves to M. The history shows both lines of work, and no existing commit changed. That is why a merge is safe on shared branches.",
                  Transform(main_t, main_t4), Succession(Wait(2.4), FadeIn(safe, shift=UP * 0.1)), run_time=3.6)

        # ---------- 3. rebase
        self.play(FadeOut(VGroup(Mn, mC, mE, two, safe, cmdg)), Transform(main_t, btag("main", MAIN_C).next_to(C, UP, buff=0.35)), run_time=1.0)
        on2 = T("on feature:", 26, GREY_B)
        cmd2 = M("$ git rebase main", 28)
        cmdg2 = VGroup(on2, cmd2).arrange(RIGHT, buff=0.3).move_to(UP * 3.4)
        self.beat("Rebase is the other way to bring your branch up to date. Same start as before. This time, on feature, you run git rebase main.",
                  FadeIn(on2), Write(cmd2), run_time=2.0)

        steps = VGroup(T("1. list your commits that main does not have", 26), T("2. move your branch to main's newest commit", 26),
                       T("3. apply your commits again, one at a time", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([0, -3.05, 0])
        rD = Circle(radius=0.52, stroke_color=YELLOW_M, stroke_width=4).move_to(D)
        rE = Circle(radius=0.52, stroke_color=YELLOW_M, stroke_width=4).move_to(E)
        self.beat("It works in three steps. First, it lists the commits on your branch that main does not have: D and E.",
                  FadeIn(steps[0], shift=UP * 0.1), Succession(Wait(2.4), AnimationGroup(Create(rD), Create(rE))), run_time=3.4)

        feat_c = btag("feature", FEAT_C).next_to(main_t, UP, buff=0.12)
        self.beat("Second, it moves your branch to main's newest commit, C.",
                  FadeIn(steps[1], shift=UP * 0.1), FadeOut(rD), FadeOut(rE), Transform(feat_t, feat_c, rate_func=late(0.3)), run_time=2.2)

        D1, E1 = node("D'", FEAT_C).move_to([0.0, TOP, 0]), node("E'", FEAT_C).move_to([1.8, TOP, 0])
        d1C, e1D = back(D1, C), back(E1, D1)
        f_d1 = btag("feature", FEAT_C).next_to(D1, UP, buff=0.35)
        f_e1 = btag("feature", FEAT_C).next_to(E1, UP, buff=0.35)
        self.beat("Third, it applies your commits again, one at a time, on top. D prime, then E prime.",
                  FadeIn(steps[2], shift=UP * 0.1),
                  Succession(Wait(1.6), AnimationGroup(TransformFromCopy(D, D1), GrowArrow(d1C), Transform(feat_t, f_d1)), Wait(0.3),
                             AnimationGroup(TransformFromCopy(E, E1), GrowArrow(e1D), Transform(feat_t, f_e1))), run_time=4.4)

        # why new IDs
        self.play(FadeOut(steps), run_time=0.5)

        def card(title, parent, color):
            g = VGroup(M(title, 24, color), M(f"parent {parent}", 22, YELLOW_M if "'" in title else WHITE), T("the same change", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            r = RoundedRectangle(corner_radius=0.12, width=3.0, height=g.height + 0.45, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.12), 1)
            return VGroup(r, g.move_to(r))
        k1 = card("commit D", "B", GREY_B).move_to([-3.4, -2.85, 0])
        k2 = card("commit D'", "C", FEAT_C).move_to([1.4, -2.85, 0])
        k_a = Arrow(k1.get_right(), k2.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        newid = T("new parent, so a new hash", 26, YELLOW_M).next_to(k2, RIGHT, buff=0.35)
        fit(newid, 6.9 - k2.get_right()[0] - 0.35 - 0.3)
        self.beat("Each replayed commit has a new parent. The parent is part of a commit's hash, so D prime is a new commit, with a new ID.",
                  FadeIn(k1, shift=UP * 0.1), GrowArrow(k_a, rate_func=late(0.3)), FadeIn(k2, shift=UP * 0.1, rate_func=late(0.35)),
                  FadeIn(newid, rate_func=late(0.7)), run_time=4.2)

        gone = VGroup(D, E, dB, eD)
        refl = T("only the reflog points here", 24, GREY_B).next_to(VGroup(D, E), DOWN, buff=0.3)
        self.beat("The old D and E still exist, but no branch points to them any more. Only the reflog does.",
                  FadeOut(VGroup(k1, k2, k_a, newid)), gone.animate.set_opacity(0.3), FadeIn(refl, rate_func=late(0.4)), run_time=2.4)
        straight = VGroup(A, B, C, D1, E1)
        self.beat("You end up with one straight line of history, as if you had started your work today.",
                  Indicate(straight, color=YELLOW_M, scale_factor=1.05), run_time=2.0)

        # ---------- 4. never rebase commits others have
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)
        warn = T("Do not rebase commits that other people already have.", 34, RED_M).move_to(UP * 3.3)

        def row(y, letters, xs, colors):
            ns = VGroup(*[node(l, c, r=0.3, size=26).move_to([x, y, 0]) for l, x, c in zip(letters, xs, colors)])
            ar = VGroup(*[back(ns[i + 1], ns[i]) for i in range(len(ns) - 1)])
            return ns, ar
        xs = [-5.0, -3.6, -2.2, -0.8, 0.6]
        yours, y_ar = row(1.7, ["A", "B", "C", "D'", "E'"], xs, [MAIN_C] * 3 + [FEAT_C] * 2)
        y_lab = T("your copy, after the rebase", 26, GREY_B).next_to(yours, UP, buff=0.3).align_to(yours, LEFT)
        theirs, t_ar = row(-0.7, ["A", "B", "C"], xs[:3], [MAIN_C] * 3)
        tD, tE = node("D", FEAT_C, r=0.3, size=26).move_to([-2.2, -2.1, 0]), node("E", FEAT_C, r=0.3, size=26).move_to([-0.8, -2.1, 0])
        tdB, teD = back(tD, theirs[1]), back(tE, tD)
        t_lab = T("a teammate's copy, fetched earlier", 26, GREY_B).next_to(theirs, UP, buff=0.3).align_to(theirs, LEFT)
        old_hl = VGroup(*[Circle(radius=0.42, stroke_color=RED_M, stroke_width=3).move_to(n) for n in (tD, tE)])
        self.beat("Now the one rule that matters most. Do not rebase commits that other people already have.",
                  Write(warn), FadeIn(VGroup(yours, y_ar, y_lab)), run_time=2.4)
        self.beat("Say a teammate fetched your branch before you rebased it. Their copy still holds the old D and E. Your history and theirs no longer match.",
                  FadeIn(VGroup(theirs, t_ar, t_lab)), FadeIn(VGroup(tD, tE, tdB, teD), rate_func=late(0.3)),
                  Create(old_hl, rate_func=late(0.65)), run_time=4.0)

        tD1, tE1 = yours[3].copy().move_to([-0.8, -0.7, 0]), yours[4].copy().move_to([0.6, -0.7, 0])
        tdc, ted = back(tD1, theirs[2]), back(tE1, tD1)
        tM = node("M", MERGE_C, r=0.3, size=26).move_to([2.2, -1.4, 0])
        tmE1, tmE = back(tM, tE1, MERGE_C), back(tM, tE, MERGE_C)
        self.beat("If they now merge your rebased branch, their history holds each of your changes twice, under the old IDs and the new ones.",
                  TransformFromCopy(yours[3], tD1), TransformFromCopy(yours[4], tE1), GrowArrow(tdc), GrowArrow(ted),
                  Succession(Wait(1.8), AnimationGroup(GrowFromCenter(tM), GrowArrow(tmE1), GrowArrow(tmE))), run_time=3.6)
        twice = VGroup(*[Circle(radius=0.42, stroke_color=RED_M, stroke_width=3).move_to(n) for n in (tD1, tE1)])
        tw_l = T("each change twice", 26, RED_M).next_to(tM, RIGHT, buff=0.4)
        self.beat("Someone has to clean that up by hand.",
                  Create(twice), FadeIn(tw_l, shift=LEFT * 0.1), run_time=1.6)
        ok = VGroup(tick(True, 0.24), T("your own branch, before anyone builds on it: fine", 28, GREEN_M)).arrange(RIGHT, buff=0.3).move_to(DOWN * 3.3)
        self.beat("Rebasing your own branch, before anyone builds on it, is fine. That is how most teams use it.",
                  FadeIn(ok, shift=UP * 0.15), run_time=1.6)

        # ---------- recap
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)
        r1 = VGroup(T("merge", 34, MERGE_C), T("adds a commit with two parents. safe on shared branches.", 28)).arrange(RIGHT, buff=0.35)
        r2 = VGroup(T("rebase", 34, FEAT_C), T("copies your commits on top, with new IDs. only for your own branch.", 28)).arrange(RIGHT, buff=0.35)
        rec = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to(ORIGIN)
        fit(rec, 13.0)
        self.beat("A merge adds a commit with two parents, and it is safe on shared branches. A rebase copies your commits on top with new IDs: great for your own branch, never for commits others have.",
                  FadeIn(r1, shift=UP * 0.15), FadeIn(r2, shift=UP * 0.15, rate_func=late(0.45)), run_time=6.0)
        self.wait(1.2)
