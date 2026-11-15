import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bfor_each\b", "for each"), (r"\bcount\.index\b", "count dot index"), (r"\btoset\b", "to set"),
            (r"\bby_count\b", "by count"), (r"\bby_each\b", "by each")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def slot(addr, content, color=BLUE_M, w=2.9, h=1.25):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.12), 1)
    a = M(addr, 24, YELLOW_M)
    c = M(content, 22, WHITE)
    g = VGroup(a, c).arrange(DOWN, buff=0.18).move_to(r)
    return VGroup(r, a, c)


class D32Loops(VoiceScene):
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
        self.title_card("count or for_each", "a copy's address is its identity")

        # 1. the list, with positions under each name
        LY = 3.05
        head = M("names = [", 28)
        items = VGroup(M('"alpha",', 28, GOLD_M), M('"bravo",', 28, GOLD_M), M('"charlie"', 28, GOLD_M))
        tail = M("]", 28)
        lst = VGroup(head, *items, tail).arrange(RIGHT, buff=0.22).move_to([0, LY, 0])
        idx = VGroup(*[M(str(i), 22, GREY_B).next_to(items[i], DOWN, buff=0.14) for i in range(3)])
        self.beat("You have a list of three names: alpha, bravo and charlie. You want one file for each name.",
                  Write(lst), run_time=2.0)
        self.beat("To make several copies of a resource, you need a meta-argument, an argument Terraform itself reads on any resource. There are two: count, and for_each.",
                  Indicate(items, color=GOLD_M, scale_factor=1.08), run_time=2.0)

        # 2. count row
        CX = (-2.5, 0.75, 4.0)
        RY = 0.75
        clab = M("count = length(var.names)", 24, BLUE_M).move_to([-1.3, RY + 1.2, 0]).align_to([-6.6, 0, 0], LEFT)
        crow = VGroup(*[slot(f"[{i}]", f"hello {n}", BLUE_M).move_to([CX[i], RY, 0]) for i, n in enumerate(("alpha", "bravo", "charlie"))])
        cname = M("count", 28, BLUE_M).move_to([-5.6, RY, 0])
        self.beat("count takes a number. Here, the length of the list, so three.",
                  FadeIn(clab, shift=DOWN * 0.15), FadeIn(cname), run_time=1.6)
        self.beat("It makes three copies, and count.index tells each copy its number: zero, one and two.",
                  LaggedStart(*[Create(s[0]) for s in crow], lag_ratio=0.25),
                  LaggedStart(*[FadeIn(s[1], scale=1.3) for s in crow], lag_ratio=0.25), FadeIn(idx), run_time=2.6)
        flows = VGroup(*[Arrow(items[i].get_bottom() + DOWN * 0.38, crow[i].get_top(), buff=0.1, stroke_width=2.5, color=GREY_B,
                               max_tip_length_to_length_ratio=0.15) for i in range(3)])
        self.beat("Copy zero reads the name in place zero. So the files say hello alpha, hello bravo, and hello charlie.",
                  LaggedStart(*[AnimationGroup(GrowArrow(flows[i]), FadeIn(crow[i][2])) for i in range(3)], lag_ratio=0.4), run_time=2.8)

        q = T("but how does Terraform tell the copies apart?", 28, GREY_B).move_to([0, -1.4, 0])
        self.beat("But how does Terraform tell these copies apart, from one run to the next?",
                  FadeIn(q, shift=UP * 0.15), run_time=1.4)
        ans = T("by its address:  local_file.by_count[0]", 28, YELLOW_M).move_to(q)
        self.beat("By its address. The first file is local_file.by_count, zero. A copy's address is its identity.",
                  Transform(q, ans), Succession(Wait(1.6), Indicate(crow[0][1], color=YELLOW_M, scale_factor=1.3)), run_time=3.0)
        self.beat("With count, the address is a number. It says where the copy sits in the list, not which name it holds.",
                  LaggedStart(*[Indicate(i, color=YELLOW_M, scale_factor=1.4) for i in idx], lag_ratio=0.3), run_time=2.4)
        self.play(FadeOut(q), run_time=0.4)

        # 3. remove alpha: everything shifts
        strike = Line(items[0].get_left(), items[0].get_right(), stroke_width=4, color=RED_M)
        self.beat("Now delete alpha from the list, and run plan. You might expect only one file to go. Watch.",
                  Create(strike), items[0].animate.set_color(RED_M), run_time=1.6)
        new_b = M('"bravo",', 28, GOLD_M)
        new_c = M('"charlie"', 28, GOLD_M)
        nl = VGroup(M("names = [", 28), new_b, new_c, M("]", 28)).arrange(RIGHT, buff=0.22).move_to([0, LY, 0])
        nl.align_to(lst, LEFT)
        self.beat("Every name after alpha moves up one place. Bravo is now in place zero, and charlie in place one.",
                  FadeOut(VGroup(items[0], strike)), items[1].animate.move_to(new_b), items[2].animate.move_to(new_c),
                  tail.animate.move_to(nl[3]), run_time=2.4)
        # repoint arrows: place 0 now holds bravo, place 1 holds charlie, place 2 is empty
        self.play(flows[2].animate.set_opacity(0.0), idx[2].animate.set_opacity(0.25), run_time=0.6)

        old0, old1 = crow[0][2], crow[1][2]
        n0 = M("hello bravo", 22, GOLD_M).move_to(old0)
        n1 = M("hello charlie", 22, GOLD_M).move_to(old1)
        rep0 = chip("replaced", GOLD_M, 22).next_to(crow[0], DOWN, buff=0.22)
        rep1 = chip("replaced", GOLD_M, 22).next_to(crow[1], DOWN, buff=0.22)
        self.steps("Terraform compares address by address. Copy zero said hello alpha. Now it must say hello bravo. The content changed, and that forces a replacement.",
                   (1.2, Indicate(crow[0][1], color=YELLOW_M, scale_factor=1.3)), (1.6, Wait(1.6)),
                   (1.2, Transform(old0, n0), crow[0][0].animate.set_stroke(GOLD_M)), (1.4, Wait(1.4)), (0.8, FadeIn(rep0, shift=UP * 0.1)))
        self.beat("The same happens to copy one. It said hello bravo, and now it must say hello charlie.",
                  Transform(old1, n1), crow[1][0].animate.set_stroke(GOLD_M), Succession(Wait(1.6), FadeIn(rep1, shift=UP * 0.1)), run_time=2.8)
        x2 = tick(False, 0.2).move_to(crow[2][0].get_corner(UR) + [-0.3, -0.3, 0])
        des2 = chip("destroyed", RED_M, 22).next_to(crow[2], DOWN, buff=0.22)
        self.beat("And copy two is out of range. There is no place two any more, so it is destroyed.",
                  crow[2][0].animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.1)), crow[2][1:].animate.set_opacity(0.3),
                  Succession(Wait(0.8), AnimationGroup(Create(x2), FadeIn(des2, shift=UP * 0.1))), run_time=2.4)
        sumc = T("one name removed, three files touched", 28, RED_M).move_to([0, -2.1, 0])
        self.beat("You removed one name, and three files were touched.",
                  FadeIn(sumc, shift=UP * 0.15), run_time=1.4)

        # 4. undo, then build the for_each row
        self.play(FadeOut(VGroup(sumc, rep0, rep1, des2, x2, flows, idx)), run_time=0.5)
        lst2 = VGroup(M("names = [", 28), M('"alpha",', 28, GOLD_M), M('"bravo",', 28, GOLD_M), M('"charlie"', 28, GOLD_M), M("]", 28)).arrange(RIGHT, buff=0.22).move_to([0, LY, 0])
        crow2 = VGroup(*[slot(f"[{i}]", f"hello {n}", BLUE_M).move_to([CX[i], RY, 0]) for i, n in enumerate(("alpha", "bravo", "charlie"))])
        cur_list = VGroup(head, items[1], items[2], tail)
        self.beat("Put alpha back, and try the same thing with for_each.",
                  Transform(cur_list, lst2), FadeOut(crow), FadeIn(crow2), run_time=1.6)
        self.remove(cur_list); self.add(lst2)
        crow = crow2
        EY = -1.85
        elab = M("for_each = toset(var.names)", 24, TEAL_M).move_to([0, EY + 1.2, 0]).align_to([-6.6, 0, 0], LEFT)
        ename = M("for_each", 26, TEAL_M).move_to([-5.6, EY, 0])
        self.beat("for_each takes a map, or a set of strings. A plain list is rejected, so you wrap it in toset.",
                  FadeIn(elab, shift=DOWN * 0.15), FadeIn(ename), Succession(Wait(2.4), Indicate(elab, color=TEAL_M, scale_factor=1.05)), run_time=3.2)
        erow = VGroup(*[slot(f'["{n}"]', f"hello {n}", TEAL_M).move_to([CX[i], EY, 0]) for i, n in enumerate(("alpha", "bravo", "charlie"))])
        self.beat("Each key becomes one copy, and the key is in the address. local_file.by_each, alpha. Bravo. Charlie.",
                  LaggedStart(*[AnimationGroup(Create(s[0]), FadeIn(s[1], scale=1.2), FadeIn(s[2])) for s in erow], lag_ratio=0.35), run_time=3.2)
        self.beat("Here, the identity is the name, not a position.",
                  LaggedStart(*[Indicate(s[1], color=YELLOW_M, scale_factor=1.2) for s in erow], lag_ratio=0.25), run_time=1.8)

        # 5. remove alpha again, both rows at once
        it = lst2[1:4]
        strike = Line(it[0].get_left(), it[0].get_right(), stroke_width=4, color=RED_M)
        self.beat("Delete alpha again.", Create(strike), it[0].animate.set_color(RED_M), run_time=1.0)
        nl2 = VGroup(M("names = [", 28), M('"bravo",', 28, GOLD_M), M('"charlie"', 28, GOLD_M), M("]", 28)).arrange(RIGHT, buff=0.22).move_to([0, LY, 0]).align_to(lst2, LEFT)
        c0 = M("hello bravo", 22, GOLD_M).move_to(crow[0][2])
        c1 = M("hello charlie", 22, GOLD_M).move_to(crow[1][2])
        x2 = tick(False, 0.2).move_to(crow[2][0].get_corner(UR) + [-0.3, -0.3, 0])
        self.steps("The count row shifts, just like before. Two copies replaced, and one destroyed.",
                   (1.2, FadeOut(VGroup(it[0], strike)), it[1].animate.move_to(nl2[1]), it[2].animate.move_to(nl2[2]), lst2[4].animate.move_to(nl2[3])),
                   (1.6, Transform(crow[0][2], c0), Transform(crow[1][2], c1), crow[0][0].animate.set_stroke(GOLD_M), crow[1][0].animate.set_stroke(GOLD_M),
                    crow[2][0].animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.1)), crow[2][1:].animate.set_opacity(0.3), Create(x2)))
        xa = tick(False, 0.2).move_to(erow[0][0].get_corner(UR) + [-0.3, -0.3, 0])
        self.beat("In the for_each row, the key alpha is not in the set any more. So only that copy is destroyed.",
                  Succession(Wait(1.2), AnimationGroup(erow[0][0].animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.1)), erow[0][1:].animate.set_opacity(0.3), Create(xa))), run_time=3.0)
        keep = VGroup(*[chip("kept", GREEN_M, 22).next_to(erow[i], DOWN, buff=0.18) for i in (1, 2)])
        self.beat("Bravo and charlie keep their names, so their addresses did not change. They stay exactly as they are.",
                  LaggedStart(*[FadeIn(k, shift=UP * 0.1) for k in keep], lag_ratio=0.4),
                  *[Indicate(erow[i][1], color=GREEN_M, scale_factor=1.2) for i in (1, 2)], run_time=2.6)

        # 6. the real plan line
        self.play(FadeOut(keep), run_time=0.4)
        plan = M("Plan: 2 to add, 0 to change, 4 to destroy.", 26, WHITE).move_to([0.3, -3.35, 0])
        self.beat("The real plan says: 2 to add, 0 to change, 4 to destroy. A replace counts as one destroy and one add.",
                  Write(plan), run_time=2.6)
        b3 = SurroundingRectangle(VGroup(crow), color=RED_M, buff=0.12, corner_radius=0.1)
        self.beat("Three of the four destroys come from count, for one removed name.",
                  Create(b3), run_time=1.6)
        self.beat("Files are cheap to replace. Containers with data, or cloud servers, are not.",
                  Indicate(plan, color=RED_M, scale_factor=1.05), run_time=2.0)
        self.play(FadeOut(VGroup(lst2[1:], lst2[0], crow, erow, x2, xa, b3, plan, clab, elab, cname, ename)), run_time=0.7)

        # 7. when to use which
        lc = VGroup(T("count", 34, BLUE_M), T("nearly identical copies", 26), T("or an on-off switch", 26),
                    M("count = var.enabled ? 1 : 0", 22, BLUE_M)).arrange(DOWN, buff=0.3)
        rc = VGroup(T("for_each", 34, TEAL_M), T("each copy has its own", 26), T("name or settings", 26),
                    M('["blue"]  ["green"]', 22, TEAL_M)).arrange(DOWN, buff=0.3)
        pl = RoundedRectangle(corner_radius=0.15, width=5.6, height=3.4, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.08), 1).move_to([-3.2, 0.7, 0])
        pr = RoundedRectangle(corner_radius=0.15, width=5.6, height=3.4, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.08), 1).move_to([3.2, 0.7, 0])
        lc.move_to(pl); rc.move_to(pr)
        self.beat("The docs give simple advice. Use count for nearly identical copies, or as an on-off switch.",
                  Create(pl), FadeIn(lc[0]), Succession(Wait(1.4), FadeIn(lc[1:3])), Succession(Wait(3.4), Write(lc[3])), run_time=4.6)
        self.beat("Use for_each when each copy has its own name or settings.",
                  Create(pr), FadeIn(rc[0]), Succession(Wait(1.0), FadeIn(rc[1:3])), Succession(Wait(2.0), Write(rc[3])), run_time=3.0)
        lim = T("the count or the keys must be known before anything exists", 26, YELLOW_M).move_to([0, -1.75, 0])
        self.beat("One limit applies to both. The plan lists every copy by its address, so Terraform must know the count or the keys before anything exists.",
                  FadeIn(lim, shift=UP * 0.15), run_time=2.0)

        # 8. recap
        rec = T("count: known by position, and positions shift", 28, BLUE_M).move_to([0, -2.7, 0])
        rec2 = T("for_each: known by name, so only the removed copy goes", 28, TEAL_M).move_to([0, -3.35, 0])
        self.beat("So remember: count copies are known by position, and positions shift. for_each copies are known by name, so only the removed one goes.",
                  FadeIn(rec, shift=UP * 0.15), Succession(Wait(2.6), FadeIn(rec2, shift=UP * 0.15)), run_time=4.0)
        self.wait(1.0)
