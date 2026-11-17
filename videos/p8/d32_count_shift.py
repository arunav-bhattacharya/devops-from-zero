import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bfor_each\b", "for each"), (r"\btoset\b", "to set"), (r"\bcount\.index\b", "count dot index")])

NAMES = ["alpha", "bravo", "charlie"]
NC = {"alpha": BLUE_M, "bravo": GOLD_M, "charlie": PURPLE_M}


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(w, h, color, k=0.08, sw=2.5):
    return RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, k), opacity=1)


def shed(color):
    """A little garden shed: walls plus a roof, filled with the owner's colour."""
    walls = Square(side_length=1.1, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), opacity=1)
    roof = Polygon(walls.get_corner(UL) + LEFT * 0.12, walls.get_corner(UR) + RIGHT * 0.12, walls.get_top() + UP * 0.5,
                   stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), opacity=1)
    return VGroup(walls, roof)


class D32CountShift(VoiceScene):
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

    def guess(self, where):
        c = chip("pause and guess", YELLOW_M, 24).move_to(where)
        n = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        self.play(FadeIn(c), FadeIn(n), run_time=0.3)
        self.wait(0.85)
        self.play(Transform(n, T("1", 30, YELLOW_M).move_to(n)), run_time=0.15)
        self.wait(0.85)
        self.play(FadeOut(c), FadeOut(n), run_time=0.3)

    def construct(self):
        self.title_card("One cancelled order, three sheds touched", "count, for_each, and what a copy is called")

        # 1. three copies of a drawing  [FAMILIAR, PAIN, WISH]
        drs = VGroup(*[panel(2.6, 1.8, GREY_B, 0.05) for _ in range(3)]).arrange(RIGHT, buff=0.6).move_to([0, 0.6, 0])
        addrs = VGroup(T("North St", 26, GREEN_M), T("Mill Rd", 26, GREEN_M), T("North St", 26, RED_M))
        for a, d in zip(addrs, drs):
            a.move_to(d.get_center() + DOWN * 0.45)
        cafe = VGroup(*[T("café drawing", 26, GREY_B).move_to(d.get_center() + UP * 0.35) for d in drs])
        self.beat("Your friend's café did well, and now she wants three, in three parts of town. So you copy the drawing three times, and change the street on each copy by hand.",
                  LaggedStart(*[AnimationGroup(Create(d), FadeIn(c)) for d, c in zip(drs, cafe)], lag_ratio=0.4),
                  Succession(Wait(2.6), LaggedStart(FadeIn(addrs[0]), FadeIn(addrs[1]), lag_ratio=0.5)), run_time=4.4)
        self.beat("On the third copy you forget. The builder turns up at the wrong street. The drawing was fine. The copying was the problem.",
                  FadeIn(addrs[2]), Succession(Wait(1.2), Indicate(addrs[2], color=RED_M)), run_time=3.0)
        self.play(FadeOut(VGroup(drs, addrs, cafe)), run_time=0.6)
        lst = VGroup(*[chip(n, NC[n], 26, mono=True) for n in NAMES]).arrange(RIGHT, buff=0.35).move_to([0, 2.75, 0])
        ll = T("names =", 26, GREY_B, ).next_to(lst, LEFT, buff=0.3)
        self.beat("What we want is one drawing and a list of names. Terraform has two ways to make one copy per name: count, and for_each.",
                  FadeIn(ll), LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in lst], lag_ratio=0.3), run_time=3.0)
        q = T("both make three. Does it matter which?", 30, YELLOW_M).move_to([0, 0.4, 0])
        self.beat("And here is the question that sounds too simple to ask. Both make three copies. Does it really matter which one you pick?",
                  Write(q), run_time=2.2)
        self.play(FadeOut(q), run_time=0.4)

        # 2. count: copies known by number  [SHRINK, ANALOGY, MAP]
        xs_l = [-5.0, -3.0, -1.0]
        Y = 0.35
        sheds = [shed(NC[n]).move_to([x, Y, 0]) for n, x in zip(NAMES, xs_l)]
        nums = [T(str(i), 34, WHITE).move_to(s[0]) for i, s in enumerate(sheds)]
        owners = [T(n, 26, NC[n]).next_to(s, DOWN, buff=0.22) for n, s in zip(NAMES, sheds)]
        cl = M("local_file.by_count[ ]", 24, GREY_B).move_to([-3.0, 1.85, 0])
        self.steps("Picture a builder making garden sheds for three families on that list. This builder numbers the sheds by their place on the list. Alpha gets shed zero, bravo shed one, charlie shed two.",
                   (0.6, FadeIn(cl)), (1.8, Wait(1.8)),
                   (2.6, LaggedStart(*[AnimationGroup(FadeIn(s, shift=UP * 0.15), FadeIn(n), FadeIn(o)) for s, n, o in zip(sheds, nums, owners)], lag_ratio=0.45)))
        self.beat("That is count. count equals three makes local_file.by_count zero, one and two, and count.index tells each copy its number. Each one is a small file that says hello to its family.",
                  *[Indicate(n, color=WHITE) for n in nums], run_time=3.6)

        # 3. alpha cancels: predict  [PREDICT, PAUSE]
        self.beat("Now alpha cancels. We remove alpha from the list, and plan.", lst[0].animate.set_opacity(0.25), run_time=1.6)
        q2 = T("how many sheds does the builder touch?", 28, YELLOW_M).move_to([-3.0, -2.2, 0])
        self.beat("How many sheds does the builder touch?", FadeIn(q2), run_time=1.4)
        self.guess([-3.0, -3.0, 0])
        self.beat("The obvious answer is one. Knock down alpha's shed, leave the others alone. Let's see if that is really true.",
                  Indicate(sheds[0], color=BLUE_M), run_time=2.2)
        self.play(FadeOut(q2), run_time=0.3)

        # 4. break it: everyone moves up one place  [BREAK, SHOW]
        new_list = VGroup(lst[1].copy(), lst[2].copy())
        self.steps("The builder reads the new list. Bravo is first now, so bravo gets number zero. Charlie is second, so charlie gets one.",
                   (0.6, FadeOut(lst[0])), (0.9, lst[1].animate.move_to(lst[0]), lst[2].animate.move_to(lst[1])), (2.0, Wait(2.0)),
                   (0.6, Indicate(nums[0], color=WHITE)), (1.0, Wait(1.0)), (0.6, Indicate(nums[1], color=WHITE)))
        mk = lambda i, n: (shed(NC[n]).move_to(sheds[i]), T(n, 26, NC[n]).move_to(owners[i]))
        s0, o0 = mk(0, "bravo")
        s1, o1 = mk(1, "charlie")
        rp0 = T("replaced", 24, RED_M).next_to(o0, DOWN, buff=0.15)
        rp1 = T("replaced", 24, RED_M).next_to(o1, DOWN, buff=0.15)
        self.steps("So shed zero is torn down and rebuilt for bravo. Shed one is torn down and rebuilt for charlie.",
                   (1.0, Transform(sheds[0], s0), Transform(owners[0], o0), FadeIn(rp0)), (1.0, Wait(1.0)),
                   (1.0, Transform(sheds[1], s1), Transform(owners[1], o1), FadeIn(rp1)))
        x2 = tick(False, 0.45).move_to(sheds[2])
        gone = T("destroyed", 24, RED_M).next_to(owners[2], DOWN, buff=0.15)
        self.steps("And shed two has nobody left on the list, so it is knocked down. One cancelled order. Three sheds touched.",
                   (1.4, Wait(1.4)), (0.8, sheds[2].animate.set_opacity(0.25), owners[2].animate.set_opacity(0.25), Create(x2), FadeIn(gone)))
        self.play(*[n.animate.set_opacity(1) for n in nums], run_time=0.2)
        self.beat("Well... bravo and charlie just got brand new sheds they never asked for.", run_time=None)
        why = VGroup(M("[0] hello alpha -> hello bravo", 22, RED_M), M("    # forces replacement", 22, RED_M),
                     M("[2] index out of range for count", 22, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-3.0, -2.7, 0])
        fit(why, 6.0)
        self.beat("The real plan says the same thing. Copy zero's content changes from hello alpha to hello bravo, which forces replacement. And copy two is destroyed, because index two is out of range for count.",
                  LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in why], lag_ratio=0.5), run_time=4.0)

        # 5. for_each: name cards  [SHOW]
        xs_r = [1.4, 3.4, 5.4]
        fsheds = [shed(NC[n]).move_to([x, Y, 0]) for n, x in zip(NAMES, xs_r)]
        cards = [chip(n, NC[n], 22, mono=True).move_to(s[0]) for n, s in zip(NAMES, fsheds)]
        faddr = [M(f'["{n}"]', 22, NC[n]).next_to(s, DOWN, buff=0.22) for n, s in zip(NAMES, fsheds)]
        fl = M("local_file.by_each[ ]", 24, GREY_B).move_to([3.4, 1.85, 0])
        lst_all = VGroup(*[chip(n, NC[n], 26, mono=True) for n in NAMES]).arrange(RIGHT, buff=0.35).move_to([0, 2.75, 0])
        self.steps("Now the second builder, for_each. Same list, but this builder nails a name card to every shed. The address is the name: local_file.by_each alpha, bravo, charlie.",
                   (0.8, FadeOut(VGroup(lst[1], lst[2])), FadeIn(lst_all)), (0.6, FadeIn(fl)), (1.6, Wait(1.6)),
                   (2.4, LaggedStart(*[AnimationGroup(FadeIn(s, shift=UP * 0.15), FadeIn(c), FadeIn(a)) for s, c, a in zip(fsheds, cards, faddr)], lag_ratio=0.45)))
        x3 = tick(False, 0.45).move_to(fsheds[0])
        fg_ = T("destroyed", 24, RED_M).next_to(faddr[0], DOWN, buff=0.15)
        ok = VGroup(*[T("untouched", 24, GREEN_M).next_to(faddr[i], DOWN, buff=0.15) for i in (1, 2)])
        self.steps("Alpha cancels again. The builder looks for the card that says alpha, and knocks down that shed. Bravo's and charlie's sheds keep their cards, so nothing happens to them.",
                   (0.8, FadeOut(lst_all[0])), (1.6, Wait(1.6)),
                   (0.9, fsheds[0].animate.set_opacity(0.25), cards[0].animate.set_opacity(0.25), faddr[0].animate.set_opacity(0.25), Create(x3), FadeIn(fg_)),
                   (1.4, Wait(1.4)), (0.8, FadeIn(ok)))

        # 6. the count, and the name  [NAME]
        tot = M("Plan: 2 to add, 0 to change, 4 to destroy.", 26, WHITE).move_to([0, -3.15, 0])
        self.play(FadeOut(why), run_time=0.3)
        self.beat("The lab's practice folder does both at once, so here is its real summary line. Plan: 2 to add, 0 to change, 4 to destroy.",
                  FadeIn(tot), run_time=2.6)
        three = Brace(VGroup(sheds[0], sheds[2]), DOWN, color=RED_M).next_to(VGroup(*owners), DOWN, buff=0.55)
        t3 = T("3 of the 4 destroys", 26, RED_M).next_to(three, DOWN, buff=0.12)
        one = Brace(fsheds[0], DOWN, color=RED_M).next_to(faddr[0], DOWN, buff=0.55)
        t1 = T("1", 26, RED_M).next_to(one, DOWN, buff=0.12)
        self.steps("Three of those four destroys come from count, for one removed name. Only one comes from for_each.",
                   (0.6, FadeOut(VGroup(rp0, rp1, gone, fg_, ok)), tot.animate.shift(DOWN * 0.0)), (0.8, GrowFromCenter(three), FadeIn(t3)),
                   (1.6, Wait(1.6)), (0.8, GrowFromCenter(one), FadeIn(t1)))
        rule = T("A copy's address is its identity.", 30, YELLOW_M).move_to([0, 1.35, 0])
        self.beat("So here is the whole idea in one line. A copy's address is its identity. With count, the identity is a position, and positions shift. With for_each, it is a name, and names stay put.",
                  Write(rule), run_time=3.0)
        self.play(FadeOut(VGroup(three, t3, one, t1, tot)), run_time=0.4)

        # 7. guardrails  [GUARDRAIL]
        g = VGroup(T("count: nearly identical copies, or an on-off switch", 26, WHITE),
                   M("count = var.enabled ? 1 : 0", 22, GREY_B),
                   T("for_each: each copy has its own name or settings", 26, WHITE),
                   M("for_each = toset(var.names)", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([0, -2.6, 0])
        fit(g, 12.0)
        self.beat("So when is count fine? For nearly identical copies, or as an on-off switch: count equals one if enabled, else zero.",
                  FadeIn(g[0]), FadeIn(g[1]), run_time=2.6)
        self.beat("Use for_each when each copy has its own name or settings. It takes a map or a set. A plain list is rejected with Invalid for_each argument, so wrap it in toset.",
                  FadeIn(g[2]), FadeIn(g[3]), run_time=3.0)
        self.beat("One limit applies to both. Terraform must know the count or the keys before anything exists, so they cannot come from a value that appears only after apply.",
                  Indicate(lst_all[1:], color=GOLD_M), run_time=2.8)
        self.beat("And files are cheap to replace. Containers with data, or servers in a cloud, are not. That is when a shifted number really hurts.",
                  Indicate(sheds[1], color=PURPLE_M), run_time=2.4)
        self.play(FadeOut(g), run_time=0.4)

        # 8. moral and check  [MORAL, RECAP]
        mor = T("Give named things names, not numbers.", 30, GREEN_M).move_to([0, -2.4, 0])
        self.beat("The moral of the story: give named things names, not numbers. Then one cancelled order touches one shed.",
                  FadeIn(mor), run_time=2.6)
        self.play(FadeOut(mor), run_time=0.4)
        chk = T("quick check: with for_each, you remove bravo. How many copies change?", 26, YELLOW_M).move_to([0, -2.4, 0])
        fit(chk, 12.0)
        self.beat("A quick check. In the for_each sheds, bravo cancels too. How many copies does the plan touch?", FadeIn(chk), run_time=2.2)
        self.guess([0, -3.2, 0])
        x4 = tick(False, 0.45).move_to(fsheds[1])
        ans = T("one: only bravo's, the card says so", 28, GREEN_M).move_to([0, -3.2, 0])
        self.beat("One. Only the shed whose card says bravo. Charlie's card still says charlie.",
                  FadeIn(ans), fsheds[1].animate.set_opacity(0.25), cards[1].animate.set_opacity(0.25), Create(x4), run_time=2.4)
        self.wait(1.0)
