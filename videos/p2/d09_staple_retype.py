import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bd6aad6e\b", "D 6 A A D 6 E"), (r"\bd229503\b", "D 2 2 9 5 0 3"), (r"\bc711550\b", "C 7 1 1 5 5 0"),
    (r"\ba18a0e8\b", "A 1 8 A 0 E 8"), (r"\b25ff3e9\b", "2 5 F F 3 E 9"),
    (r"\bcurrency-first\b", "currency first"), (r"\bTAX_RATE\b", "tax rate"), (r"\bgit merge-base\b", "git merge base"),
    (r"--force-with-lease", "force with lease"), (r"--force\b", "force"), (r"\brebased\b", "re-based"), (r"\brebase\b", "re-base"),
    (r"\breflog\b", "ref log"),
])

ANA, BEN, MERGE, BASE, NOTE = GOLD_M, TEAL_M, GREEN_M, PURPLE_M, YELLOW_M
TOP, BOT = 0.7, -1.5
X0, X1, X2 = -4.6, -0.6, 3.4


def tint(c, a=0.3):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def commit(h, color, pos, below=True):
    c = Circle(radius=0.36, stroke_color=color, stroke_width=3).set_fill(tint(color), 1).move_to(pos)
    t = M(h, 24, color).next_to(c, DOWN if below else UP, buff=0.18)
    return VGroup(c, t)


def back(a, b, color=GREY_B):
    pa, pb = ends(a[0], b[0])
    return Arrow(pa, pb, buff=0.06, stroke_width=3, color=color, tip_length=0.2,
                 max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=8)


def sticky(text, color=NOTE, size=24):
    t = M(text, size, BLACK)
    r = Rectangle(width=t.width + 0.45, height=0.58, stroke_width=0).set_fill(color, 1)
    fold = Polygon(r.get_corner(DR) + LEFT * 0.2, r.get_corner(DR), r.get_corner(DR) + UP * 0.2, stroke_width=0).set_fill(interpolate_color(ManimColor(color), ManimColor("#000000"), 0.35), 1)
    return VGroup(r, t.move_to(r), fold)


def card(title, code, color, w=4.0):
    t = T(title, 26, color)
    c = M(code, 24)
    r = RoundedRectangle(corner_radius=0.12, width=max(w, c.width + 0.6), height=1.45, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), 1)
    t.move_to(r.get_top() + DOWN * 0.38)
    c.move_to(r.get_center() + DOWN * 0.22)
    return VGroup(r, t, c)


class D09StapleRetype(VoiceScene):
    def construct(self):
        self.title_card("Merge staples, rebase retypes", "two ways to bring two lines of work back together")

        # ---------- 1. the question and the weekend copies
        q1 = T("merge", 44, MERGE)
        q2 = T("rebase", 44, BEN)
        qq = VGroup(q1, T("or", 32, GREY_B), q2).arrange(RIGHT, buff=0.6).move_to(UP * 0.4)
        self.beat("Merge and rebase both bring two lines of work back together. So what is the real difference? And why do people argue about it? Let's find out.",
                  FadeIn(q1, shift=RIGHT * 0.2), Succession(Wait(0.8), FadeIn(qq[1])), Succession(Wait(1.4), FadeIn(q2, shift=LEFT * 0.2)), run_time=3.0)
        self.play(FadeOut(qq), run_time=0.5)

        fri = card("Friday's price list", "1543.12 EUR", GREY_B).move_to(UP * 1.9)
        ana = card("Ana's copy", "1,543.12 EUR", ANA).move_to(LEFT * 3.4 + DOWN * 1.2)
        ben = card("Ben's copy", "EUR 1543.12", BEN).move_to(RIGHT * 3.4 + DOWN * 1.2)
        la, lb = arrow(fri[0].get_bottom() + LEFT * 0.6, ana[0].get_top(), GREY_B), arrow(fri[0].get_bottom() + RIGHT * 0.6, ben[0].get_top(), GREY_B)
        self.beat("Picture Ana and Ben, who each take a copy of the shop's price list home for the weekend.",
                  FadeIn(fri), Succession(Wait(2.0), AnimationGroup(GrowArrow(la), GrowArrow(lb), FadeIn(ana), FadeIn(ben))), run_time=4.4)
        self.beat("Ana groups the thousands with commas. Ben moves the currency to the front. And on Monday, both have changed the same line.",
                  Indicate(ana[2], color=ANA), Succession(Wait(1.8), Indicate(ben[2], color=BEN)), run_time=4.4)
        self.play(FadeOut(VGroup(la, lb)), run_time=0.4)
        self.beat("The easy way to combine them is to keep whichever copy arrived last.",
                  ben.animate.move_to(ana).shift(RIGHT * 0.25 + DOWN * 0.15), run_time=2.0)
        lost = T("Ana's weekend: gone", 28, RED_M).next_to(ana, DOWN, buff=0.3).shift(RIGHT * 0.25)
        self.beat("And that is how a weekend of work quietly disappears. Last one wins is a fine rule for a race, and a terrible rule for a document.",
                  FadeIn(lost, shift=UP * 0.1), run_time=1.6)
        self.beat("So what we really want is both changes, and a question only when they truly clash.",
                  FadeOut(VGroup(fri, ana, ben, lost)), run_time=1.2)

        # ---------- 2. shape one: fast-forward
        b0 = commit("d6aad6e", ANA, [X0, TOP, 0])
        f1 = commit("a18a0e8", BEN, [X1, TOP, 0])
        a01 = back(f1, b0)
        mn = sticky("main").next_to(b0[0], UP, buff=0.35)
        ot = sticky("other", BEN).next_to(f1[1], DOWN, buff=0.25)
        self.beat("In Git, each copy is a branch, a sticky note on a commit. Let's start with the easy shape. Main sits at d6aad6e, and a branch called other has one commit on top of it.",
                  GrowFromCenter(b0), FadeIn(mn, shift=UP * 0.15),
                  Succession(Wait(5.6), AnimationGroup(GrowArrow(a01), GrowFromCenter(f1), FadeIn(ot, shift=UP * 0.15))), run_time=8.4)
        cmd = M("$ git merge other", 26).move_to(UP * 3.05)
        self.beat("On main, you run git merge other. Pause and guess. Does Git need to create anything new here?",
                  Write(cmd), run_time=1.8, after=2.0)
        out = M("Updating d6aad6e..a18a0e8   Fast-forward", 22, GREY_B).next_to(cmd, DOWN, buff=0.2)
        self.beat("No. Main gained nothing since other split off. So Git just slides the main note forward. That's a fast-forward.",
                  Succession(Wait(1.6), mn.animate(run_time=1.4).next_to(f1[0], UP, buff=0.35)), Succession(Wait(4.0), FadeIn(out)), run_time=6.4)
        self.play(FadeOut(VGroup(b0, f1, a01, mn, ot, cmd, out)), run_time=0.6)

        # ---------- 3. shape two: both moved, the puzzle that needs a base
        base = commit("c711550", BASE, [X0, TOP, 0])
        am = commit("d6aad6e", ANA, [X1, TOP, 0])
        bb = commit("d229503", BEN, [X1, BOT, 0], below=True)
        e1, e2 = back(am, base), back(bb, base)
        mn = sticky("main").next_to(am[0], UP, buff=0.35)
        cf = sticky("currency-first", BEN).next_to(bb[0], RIGHT, buff=0.4)
        graph = VGroup(base, am, bb, e1, e2)
        self.beat("Now the real shape. Ana's commit on main and Ben's on currency-first both start from c711550. Both sides moved.",
                  GrowFromCenter(base), Succession(Wait(1.6), AnimationGroup(GrowArrow(e1), GrowFromCenter(am), FadeIn(mn))),
                  Succession(Wait(3.2), AnimationGroup(GrowArrow(e2), GrowFromCenter(bb), FadeIn(cf))), run_time=6.4)
        self.play(FadeOut(VGroup(graph, mn, cf)), run_time=0.6)

        cm = card("main", "TAX_RATE = 0.25", ANA).move_to(LEFT * 3.2 + DOWN * 1.4)
        cb = card("branch", "TAX_RATE = 0.20", BEN).move_to(RIGHT * 3.2 + DOWN * 1.4)
        self.beat("Before we merge, a puzzle. Say one line has two versions. Main says the tax rate is 0.25. The branch says 0.20. Which one should the merge keep? Pause and guess.",
                  FadeIn(cm, shift=UP * 0.15), Succession(Wait(3.6), FadeIn(cb, shift=UP * 0.15)), run_time=6.6, after=2.2)
        shrug = T("?", 90, YELLOW_M).move_to(DOWN * 1.4)
        self.beat("Honestly, you can't tell. Maybe main raised it. Maybe the branch lowered it. Two versions are not enough to know who changed what.",
                  Write(shrug), run_time=1.4)
        cbase = card("merge base", "TAX_RATE = 0.20", BASE).move_to(UP * 1.5)
        self.beat("So Git brings in a third version, the newest commit that both branches contain. In our story, that's Friday's copy, the one they both took home.",
                  FadeOut(shrug), FadeIn(cbase, shift=DOWN * 0.15), run_time=3.0)
        chg = T("changed", 26, ANA).next_to(cm, UP, buff=0.2)
        same = T("same as base", 26, BEN).next_to(cb, UP, buff=0.2)
        self.beat("Say the base has 0.20. Now it's plain. The branch never touched that line. Only main changed it, so Git takes 0.25.",
                  Succession(Wait(1.6), FadeIn(same)), Succession(Wait(3.8), FadeIn(chg), Indicate(cm[2], color=ANA)), run_time=6.0)
        self.play(FadeOut(VGroup(cm, cb, cbase, chg, same)), FadeIn(VGroup(graph, mn, cf)), run_time=0.8)
        mb = M("$ git merge-base main currency-first", 24).move_to(UP * 3.05)
        mbo = M("c711550", 24, BASE).next_to(mb, DOWN, buff=0.18)
        name = T("three-way merge: the base and the two tips", 30, YELLOW_M).move_to(DOWN * 3.2)
        self.beat("That third version is called the merge base. In our repo, git merge-base main currency-first prints c711550. Base plus two tips makes three, which is why it's called a three-way merge.",
                  FadeIn(mb), Succession(Wait(4.6), FadeIn(mbo), Indicate(base[1], color=BASE, scale_factor=1.3)), Succession(Wait(8.0), FadeIn(name, shift=UP * 0.1)), run_time=11.0)
        self.beat("A change made on only one side goes in as it is. Only a line that both sides changed, in different ways, is a conflict.",
                  FadeOut(VGroup(mb, mbo)), run_time=1.4)
        self.play(FadeOut(name), run_time=0.6)

        # ---------- 4. the real clash: markers
        cmd = M("$ git merge currency-first", 26).move_to(UP * 3.05)
        self.beat("And Ana and Ben did change the same line. Run git merge currency-first, and Git stops halfway.",
                  Write(cmd), run_time=1.8)
        self.play(FadeOut(VGroup(graph, mn, cf)), run_time=0.5)
        code = VGroup(M("<<<<<<< HEAD", 24, ANA), M('    return f"{total(net):,.2f} {CURRENCY}"', 24, ANA), M("=======", 24, GREY_B),
                      M('    return f"{CURRENCY} {total(net):.2f}"', 24, BEN), M(">>>>>>> currency-first", 24, BEN)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        pane = RoundedRectangle(corner_radius=0.12, width=code.width + 0.8, height=code.height + 0.7, stroke_color=GREY_D, stroke_width=2).set_fill("#0c0c0c", 1)
        fname = M("price.py", 22, GREY_B).next_to(pane, UP, buff=0.12).align_to(pane, LEFT)
        cg = VGroup(pane, code.move_to(pane), fname).move_to(DOWN * 0.2)
        self.beat("The file now holds both versions, between marker lines. Your side, from HEAD, on top. Ben's side below the equals signs.",
                  FadeIn(pane), FadeIn(fname), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in code], lag_ratio=0.35), run_time=6.0)
        self.beat("The first time, it looks as if Git broke your file. It didn't. It's asking you a question.",
                  Succession(Indicate(code[0], color=ANA, run_time=1.0), Indicate(code[4], color=BEN, run_time=1.0), Wiggle(code[2], run_time=1.4)), run_time=3.4)
        fixed = M('    return f"{CURRENCY} {total(net):,.2f}"', 24, MERGE).move_to(code).align_to(code, LEFT)
        runout = M("$ python3 price.py   ->   EUR 1,543.12", 24, MERGE).next_to(pane, DOWN, buff=0.4)
        self.beat("Here both ideas are good. So you write one line with the currency first, and the commas kept, and you delete every marker. The program prints EUR 1,543.12.",
                  Succession(Wait(2.6), AnimationGroup(FadeOut(code[0]), FadeOut(code[2]), FadeOut(code[4]), FadeOut(code[3]), ReplacementTransform(code[1], fixed))),
                  Succession(Wait(6.4), FadeIn(runout)), run_time=8.8)
        rule = T("Git checks that the text merged, not that the code works.", 28, YELLOW_M).move_to(DOWN * 3.3)
        self.beat("One warning, though. Git checks that the text merged, not that the code works. So run the tests after every conflict.",
                  FadeIn(rule, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(pane, fname, fixed, runout, rule)), run_time=0.5)

        # ---------- 5. the merge commit staples both
        mc = commit("25ff3e9", MERGE, am[0].get_center() + RIGHT * 4.0)
        p1, p2 = back(mc, am, MERGE), back(mc, bb, MERGE)
        self.add(graph, mn, cf)
        self.play(FadeIn(VGroup(graph, mn, cf)), run_time=0.5)
        cmd2 = M("$ git add price.py && git commit", 26).move_to(cmd)
        self.beat("Then git add marks the file resolved, and git commit finishes the merge. Git writes a merge commit, with two parents. Main's old tip, and Ben's commit.",
                  ReplacementTransform(cmd, cmd2), Succession(Wait(3.6), GrowFromCenter(mc), AnimationGroup(GrowArrow(p1), GrowArrow(p2))),
                  Succession(Wait(5.0), mn.animate(run_time=1.2).next_to(mc[0], UP, buff=0.35)), run_time=9.0)
        staple = T("a cover note that says: these two joined here", 28, MERGE).move_to(DOWN * 3.1)
        self.beat("In the office, it staples both drafts together, with a cover note that says, these two joined here. Nothing is lost, and nothing is rewritten.",
                  FadeIn(staple, shift=UP * 0.1), Indicate(p1, color=MERGE), Indicate(p2, color=MERGE), run_time=3.0)
        self.play(FadeOut(VGroup(mc, p1, p2, staple, cmd2)), mn.animate.next_to(am[0], UP, buff=0.35), run_time=0.8)

        # ---------- 6. rebase: retype the pages
        cmd3 = M("$ git rebase main", 26).move_to(UP * 3.05)
        on = T("on currency-first:", 26, GREY_B).next_to(cmd3, LEFT, buff=0.3)
        VGroup(on, cmd3).move_to(UP * 3.05)
        self.beat("Now rewind, and try the other way. On Ben's branch, run git rebase main. Rebase retypes Ben's pages, so they start after the latest version of main.",
                  FadeIn(on), Write(cmd3), run_time=2.4)
        ghost = bb.copy()
        new_pos = np.array([am[0].get_center()[0] + 4.0, am[0].get_center()[1], 0])
        self.beat("Same words, fresh pages. Pause and guess. Does Ben's retyped commit keep its ID, d229503?",
                  ghost.animate(run_time=1.8, path_arc=0.6).move_to(new_pos + DOWN * 0.15), bb.animate.set_opacity(0.3), e2.animate.set_opacity(0.3), run_time=2.0, after=2.2)
        nc = Circle(radius=0.36, stroke_color=BEN, stroke_width=3).set_fill(tint(BEN), 1).move_to(new_pos)
        nl = T("new ID", 26, BEN).next_to(nc, DOWN, buff=0.18)
        ea = back(VGroup(nc), am, GREY_B)
        self.beat("It can't. Remember from last time, a commit's ID covers its parent. The retyped commit has a new parent, so it's a new commit, with a new ID.",
                  Succession(Wait(1.8), AnimationGroup(ReplacementTransform(ghost[0], nc), ReplacementTransform(ghost[1], nl))),
                  Succession(Wait(5.2), GrowArrow(ea)), run_time=7.4)
        self.beat("Then the currency-first note moves to the copy. The old commit still exists, but no branch points at it any more. The reflog still knows it.",
                  cf.animate(run_time=1.4).next_to(nc, UP, buff=0.35), Succession(Wait(3.4), Indicate(bb[1], color=BEN)), run_time=6.0)
        straight = T("a straight line, as if Ben started today", 26, BEN).move_to(DOWN * 3.2)
        self.beat("The result is a straight line of history, as if Ben had started his work today.",
                  FadeIn(straight, shift=UP * 0.1), Succession(Wait(0.6), travel(ea, YELLOW_M, 0.6), travel(e1, YELLOW_M, 0.6)), run_time=3.2)
        self.beat("Merge kept both drafts, stapled. Rebase retyped one of them. Both end with Ana's and Ben's changes in.",
                  FadeOut(straight), run_time=1.0)

        # ---------- 7. the guardrail: never retype pages someone already has
        self.play(FadeOut(VGroup(on, cmd3)), run_time=0.4)
        mate = RoundedRectangle(corner_radius=0.15, width=3.4, height=1.9, stroke_color=GREY_B, stroke_width=2.5).move_to(RIGHT * 4.6 + DOWN * 2.45)
        mt = T("a teammate's copy", 26, GREY_B).next_to(mate, UP, buff=0.15)
        old_pg = M("d229503", 24, BEN).move_to(mate)
        self.beat("Now the rule that matters more than the rest. Say a teammate already copied Ben's branch, with the old d229503 in it.",
                  Create(mate), FadeIn(mt), Succession(Wait(3.4), FadeIn(old_pg)), run_time=5.6)
        twice = T("each change twice, under old and new IDs", 26, RED_M).move_to(UP * 3.05)
        self.beat("Ben rebases and shares the new copy. Now the teammate holds pages the branch no longer has. If they merge, their history holds each of Ben's changes twice, under the old and the new IDs.",
                  Indicate(nl, color=BEN), Succession(Wait(3.6), Indicate(old_pg, color=RED_M)), Succession(Wait(7.0), FadeIn(twice, shift=DOWN * 0.1)), run_time=10.0)
        self.beat("Unlike a typist, Git retypes in a second. That's exactly why this mistake is so easy to make.",
                  Wiggle(twice), run_time=1.2)
        r1 = T("Rebase your own branch, never commits others already have.", 28, YELLOW_M).move_to(UP * 3.05)
        fit(r1, 12.6)
        self.beat("So rebase your own branch before anyone builds on it. Never rebase commits that other people already have.",
                  ReplacementTransform(twice, r1), run_time=1.6)
        r2 = VGroup(M("git push --force", 24, RED_M), T("trusts you", 26, RED_M), M("git push --force-with-lease", 24, MERGE), T("checks first", 26, MERGE))
        r2g = VGroup(VGroup(r2[0], r2[1]).arrange(RIGHT, buff=0.3), VGroup(r2[2], r2[3]).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(LEFT * 3.2 + DOWN * 2.95)
        self.beat("And after a rebase of your own branch, a normal push is refused. A plain force push overwrites the shared branch, no matter what. Force with lease refuses if a teammate pushed in the meantime, so their commit survives. Use the lease every time.",
                  Succession(Wait(3.6), FadeIn(r2g[0], shift=UP * 0.1), Wait(4.4), FadeIn(r2g[1], shift=UP * 0.1)), run_time=12.0)

        # ---------- 8. moral and check
        everything = VGroup(base, am, bb, e1, e2, mn, cf, nc, nl, ea, mate, mt, old_pg, r1, r2g)
        self.play(FadeOut(everything), run_time=0.7)
        moral = VGroup(T("Merge staples.", 44, MERGE), T("Rebase retypes.", 44, BEN)).arrange(DOWN, buff=0.3).move_to(UP * 1.6)
        rec = VGroup(T("fast-forward: only the note moves", 28), T("three-way: compare both tips with the base", 28),
                     T("rebase: new commits, new IDs, your branch only", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 1.4)
        self.beat("So, the moral of the story. Merge staples. Rebase retypes. A fast-forward only moves a note. A three-way merge compares both tips with the base. And rebase makes new commits, so keep it to your own branch.",
                  Write(moral[0]), Succession(Wait(1.4), Write(moral[1])), Succession(Wait(3.2), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rec], lag_ratio=1.1)), run_time=11.0)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.6)
        q = T("Your teammate already pulled your branch.", 32)
        q2 = T("Should you rebase it now?", 32, YELLOW_M)
        qg = VGroup(q, q2).arrange(DOWN, buff=0.35).move_to(UP * 0.8)
        self.beat("A quick check. Your teammate already pulled your branch. Should you rebase it now? Pause and guess.",
                  FadeIn(q), Succession(Wait(2.4), FadeIn(q2)), run_time=4.0, after=2.2)
        a = T("No. Their copy holds the old pages. Merge instead.", 30, MERGE).move_to(DOWN * 1.0)
        self.beat("No. Their copy holds the old pages, so a rebase would leave every change in their history twice. Merge instead.",
                  FadeIn(a, shift=UP * 0.1), run_time=1.6)
        self.wait(1.5)
