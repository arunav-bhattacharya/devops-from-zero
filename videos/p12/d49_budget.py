import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\b5xx\b", "five X X"), (r"(\d)%", r"\1 percent"), (r"(?<=\s)/(?=[\s,.]|$)", "slash"),
    (r"\b404\b", "four oh four"), (r"\b3 a\.m\.", "three in the morning"), (r"\b50 ms\b", "50 milliseconds"),
])


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def tween(tr, a, b, rt, rf=linear):
    return UpdateFromAlphaFunc(tr, lambda m, al: m.set_value(a + (b - a) * rf(al)), run_time=rt)


def flow(line, colors, rt=3.0, lag=0.12):
    """A stream of request dots along a line, one colour each."""
    anims = []
    for c in colors:
        d = Dot(radius=0.09, color=c).move_to(line.get_start())
        anims.append(Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, line.copy(), rate_func=linear, run_time=1.2), FadeOut(d, run_time=0.1)))
    return LaggedStart(*anims, lag_ratio=lag, run_time=rt)


# the budget tank and the graph share one height: 100% of the budget at the top, 0% at the bottom
YB, YT = -2.75, 1.45
TX, TW = -5.15, 1.3
GX0, GX1 = -2.55, 6.3


def gx(day):
    return GX0 + (GX1 - GX0) * day / 30


def gy(frac):
    return YB + (YT - YB) * frac


class D49Budget(VoiceScene):
    def construct(self):
        self.title_card("An SLO turns requests into a budget", "error budget, burn rate, and who gets woken up")

        # ---- 1. the problem: some requests fail. Is that bad?
        app = box("hello-devops", TEAL_M, w=3.0, h=0.8, size=28).move_to([-4.7, 0.4, 0])
        track = Line([-3.1, 0.4, 0], [3.6, 0.4, 0], stroke_width=2, color=GREY_D)
        users = box("users", BLUE_M, w=1.8, h=0.8, size=28).move_to([4.7, 0.4, 0])
        q = T("3 a.m.: wake someone up, or not?", 30, YELLOW_M).move_to([0, 2.6, 0])
        cols = [GREEN_M] * 7 + [RED_M] + [GREEN_M] * 9 + [RED_M] + [GREEN_M] * 4
        self.beat("hello-devops answers requests all day, and a few of them always fail.",
                  FadeIn(app), Create(track), FadeIn(users), flow(track, cols, 3.6), run_time=3.8)
        self.beat("So at 3 a.m., how many failures are too many? When should a person wake up?",
                  FadeIn(q, shift=DOWN * 0.15), flow(track, cols[3:15], 3.2), run_time=4.0)
        self.play(FadeOut(q), run_time=0.4)

        # ---- 2. SLI: good events over valid events
        num = T("responses to / that are not 5xx", 26, GREEN_M)
        bar_ = Line(LEFT * 2.6, RIGHT * 2.6, stroke_width=2.5, color=WHITE)
        den = T("all responses to /", 26, WHITE)
        frac = VGroup(num, bar_, den).arrange(DOWN, buff=0.2).move_to([0.3, -1.7, 0])
        sli_l = T("SLI =", 30, BLUE_M).next_to(frac, LEFT, buff=0.35)
        self.beat("First, decide what good means, seen from the user's side.",
                  Indicate(app, color=TEAL_M, scale_factor=1.05), flow(track, [GREEN_M] * 6, 2.4), run_time=2.6)
        self.beat("A good event is a response to / that is not 5xx. A valid event is any response to /.",
                  FadeIn(num, shift=UP * 0.1), Succession(Wait(2.6), AnimationGroup(Create(bar_), FadeIn(den, shift=UP * 0.1))), run_time=5.0)
        # a 404 for a mistyped URL leaves the stream
        bad = VGroup(Dot(radius=0.09, color=GREY_B), M("404", 20, GREY_B)).arrange(UP, buff=0.12)
        bad.move_to([-3.0, 0.62, 0])
        side = ArcBetweenPoints([-0.6, 0.4, 0], [1.0, 1.6, 0], angle=-PI / 3)
        nc = T("a mistyped URL: not counted", 22, GREY_B).move_to([1.45, 1.82, 0], aligned_edge=LEFT)
        self.beat("A 404 for a mistyped URL is the user's mistake, so it does not count.",
                  Succession(bad.animate(run_time=1.0, rate_func=linear).move_to([-0.6, 0.62, 0]),
                             MoveAlongPath(bad, side.shift(UP * 0.22), run_time=1.0), FadeIn(nc, run_time=0.5)), run_time=3.0)
        self.beat("Good events over valid events: that ratio is the SLI, the service level indicator.",
                  FadeOut(bad), FadeOut(nc), FadeIn(sli_l, shift=RIGHT * 0.1), run_time=2.0)

        # the chain at the top: SLI, SLO, budget
        c1 = chip("SLI = good / valid", BLUE_M, 24)
        c2 = chip("SLO: 99.9% over 30 days", TEAL_M, 24)
        c3 = chip("error budget: 0.1%", GOLD_M, 24)
        chain = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.75).move_to([0, 3.05, 0])
        a12 = Arrow(c1.get_right(), c2.get_left(), buff=0.1, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        a23 = Arrow(c2.get_right(), c3.get_left(), buff=0.1, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        self.play(ReplacementTransform(VGroup(sli_l, frac), c1), run_time=1.2)
        self.beat("An SLO is a target for that ratio over a time window: 99.9% of requests to / succeed, over the last 30 days.",
                  GrowArrow(a12), FadeIn(c2, shift=RIGHT * 0.15), run_time=2.4)
        self.beat("The rest is the error budget, the failure the SLO still allows: 100% minus 99.9%, so 0.1%.",
                  GrowArrow(a23), FadeIn(c3, shift=RIGHT * 0.15), Succession(Wait(3.0), Indicate(c3, color=GOLD_M, scale_factor=1.06)), run_time=5.0)
        self.play(FadeOut(VGroup(app, track, users)), run_time=0.6)

        # ---- 3. the budget as a tank
        shell = Rectangle(width=TW, height=YT - YB, stroke_color=GOLD_M, stroke_width=3).move_to([TX, (YT + YB) / 2, 0])
        lvl = ValueTracker(1.0)

        def fill_rect():
            h = max(0.001, (YT - YB) * lvl.get_value())
            return Rectangle(width=TW - 0.12, height=h, stroke_width=0).set_fill(GOLD_M, 0.55).move_to([TX, YB + h / 2, 0])
        fill = always_redraw(fill_rect)
        tl = T("budget left", 24, GOLD_M).next_to(shell, UP, buff=0.22)
        pct = always_redraw(lambda: M(f"{lvl.get_value() * 100:.0f}%", 22, GOLD_M).next_to(shell, DOWN, buff=0.18))
        self.beat("Say hello-devops gets 200,000 requests a day.",
                  Create(shell), FadeIn(fill), FadeIn(tl), FadeIn(pct), run_time=2.0)
        n1 = VGroup(T("30 days:", 26, GREY_B), M("6,000,000 requests", 26)).arrange(RIGHT, buff=0.25)
        n2 = VGroup(T("may fail:", 26, GREY_B), M("6,000", 26, GOLD_M)).arrange(RIGHT, buff=0.25)
        n3 = VGroup(T("or all fail for:", 26, GREY_B), M("43.2 minutes", 26, RED_M)).arrange(RIGHT, buff=0.25)
        nums = VGroup(n1, n2, n3).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([0.6, 0.2, 0]).align_to([-3.6, 0, 0], LEFT)
        self.beat("Thirty days hold 6 million requests, and 6,000 of them may fail.",
                  FadeIn(n1, shift=RIGHT * 0.1), Succession(Wait(2.6), FadeIn(n2, shift=RIGHT * 0.1)), run_time=4.2)
        self.beat("If everything fails at once, that is 43.2 minutes of full outage.",
                  FadeIn(n3, shift=RIGHT * 0.1), run_time=2.0)
        dep = chip("bad deploy: 20 minutes down", RED_M, 24).move_to([0.2, -2.3, 0]).align_to(nums, LEFT)
        half = T("almost half the month, gone", 26, RED_M).next_to(dep, RIGHT, buff=0.4)
        self.beat("Now one bad deploy breaks everything for 20 minutes. That alone spends almost half the month.",
                  FadeIn(dep, shift=UP * 0.1), Succession(Wait(1.0), tween(lvl, 1.0, 1 - 20 / 43.2, 2.4, smooth), FadeIn(half, shift=LEFT * 0.1)), run_time=4.4)
        self.play(FadeOut(VGroup(n1, n2, n3, dep, half)), run_time=0.6)

        # ship or pause
        ship = chip("budget left: ship at normal speed", GREEN_M, 24).move_to([0.6, 0.3, 0]).align_to([-3.6, 0, 0], LEFT)
        pause = chip("budget spent: pause risky releases", RED_M, 24).next_to(ship, DOWN, buff=0.45).align_to(ship, LEFT)
        self.beat("The budget gives developers and operators the same number. While budget is left, you ship at normal speed.",
                  Indicate(tl, color=GOLD_M, scale_factor=1.08), Succession(Wait(3.0), FadeIn(ship, shift=RIGHT * 0.1)), run_time=4.0)
        self.beat("When it is spent, you pause risky releases until reliability is back.",
                  tween(lvl, 1 - 20 / 43.2, 0.0, 2.0, smooth), FadeIn(pause, shift=RIGHT * 0.1), run_time=2.6)
        self.play(FadeOut(VGroup(ship, pause)), tween(lvl, 0.0, 1.0, 1.0, smooth), run_time=1.0)

        # ---- 4. burn rate: how fast, not how much
        how = T("at 3 a.m., the question is: how fast?", 28, YELLOW_M).move_to([1.9, 0.0, 0])
        self.beat("But at 3 a.m., the question is how fast the budget is going.",
                  FadeIn(how, shift=UP * 0.1), run_time=2.0)
        br = VGroup(T("burn rate =", 28, WHITE), T("error ratio now", 28, RED_M), T("/", 28, WHITE), T("budget", 28, GOLD_M)).arrange(RIGHT, buff=0.2)
        br.move_to([1.9, 2.15, 0])
        self.beat("That is the burn rate: the current error ratio, divided by the budget.",
                  FadeOut(how), FadeIn(br, shift=DOWN * 0.1), run_time=2.2)

        xax = Line([GX0, YB, 0], [GX1, YB, 0], stroke_width=2, color=GREY_B)
        yax = Line([GX0, YB, 0], [GX0, YT, 0], stroke_width=2, color=GREY_B)
        ticks = VGroup(*[M(str(d), 20, GREY_B).next_to([gx(d), YB, 0], DOWN, buff=0.15) for d in (0, 5, 10, 20, 30)])
        dl = T("days", 22, GREY_B).next_to(ticks[-1], LEFT, buff=0.35)
        guide = DashedLine([GX0 - 0.12, YT, 0], [TX + TW / 2 + 0.1, YT, 0], dash_length=0.08, stroke_width=1.5, color=GREY_D)
        self.beat("Draw the budget over the 30 days, full at the top.",
                  Create(xax), Create(yax), FadeIn(ticks), FadeIn(dl), Create(guide), run_time=2.4)

        def burn_line(rate, tr, color):
            def mk():
                d = min(tr.get_value(), 30 / rate)
                d = max(d, 0.01)
                return Line([gx(0), gy(1), 0], [gx(d), gy(1 - rate * d / 30), 0], stroke_width=4, color=color)
            return always_redraw(mk)

        def legend(text, color, y):
            row = VGroup(Line(ORIGIN, RIGHT * 0.45, stroke_width=4, color=color), T(text, 20, color)).arrange(RIGHT, buff=0.2)
            return row.move_to([0, y, 0]).align_to([1.15, 0, 0], LEFT)

        t1, t6, t14 = ValueTracker(0), ValueTracker(0), ValueTracker(0)
        l1, l6, l14 = burn_line(1, t1, GREEN_M), burn_line(6, t6, GOLD_M), burn_line(14.4, t14, RED_M)
        g1 = legend("0.1% fail: burn rate 1, lasts 30 days", GREEN_M, 1.2)
        g6 = legend("0.6% fail: burn rate 6, gone in 5 days", GOLD_M, 0.65)
        g14 = legend("1.44% fail: burn rate 14.4, about 2 days", RED_M, 0.1)
        self.add(l1)
        self.beat("If 0.1% of requests fail, that is burn rate 1. The budget lasts exactly 30 days.",
                  FadeIn(g1), Succession(Wait(2.0), AnimationGroup(tween(t1, 0, 30, 4.5), tween(lvl, 1.0, 0.0, 4.5))), run_time=7.0)
        self.add(l6)
        self.beat("At 0.6%, the burn rate is 6. The budget is gone in 5 days.",
                  FadeIn(g6), AnimationGroup(tween(t6, 0, 5, 2.4), tween(lvl, 1.0, 0.0, 2.4)), run_time=3.0)
        self.add(l14)
        self.beat("At 1.44%, the burn rate is 14.4. The budget is gone in about 2 days.",
                  FadeIn(g14), AnimationGroup(tween(t14, 0, 30 / 14.4, 1.6), tween(lvl, 1.0, 0.0, 1.6)), run_time=2.6)
        self.play(tween(lvl, 0.0, 1.0, 0.8, smooth), run_time=0.8)
        self.wait(0.6)
        l1.clear_updaters(); l6.clear_updaters(); l14.clear_updaters()
        graph = VGroup(xax, yax, ticks, dl, guide, l1, l6, l14, g1, g6, g14)
        self.play(FadeOut(graph), FadeOut(shell), FadeOut(fill), FadeOut(tl), FadeOut(pct), run_time=0.8)

        # ---- 5. where 14.4 comes from
        hb = Rectangle(width=12.0, height=0.55, stroke_color=GOLD_M, stroke_width=2.5).set_fill(tint(GOLD_M, 0.35), 1).move_to([0, 0.75, 0])
        hl = T("the whole budget, spent at burn rate 1: 720 hours", 24, GOLD_M).next_to(hb, UP, buff=0.22)
        h0 = M("0 h", 20, GREY_B).next_to(hb.get_corner(DL), DOWN, buff=0.15)
        h1 = M("720 h", 20, GREY_B).next_to(hb.get_corner(DR), DOWN, buff=0.15).shift(LEFT * 0.25)
        self.beat("Why the odd 14.4? Work backwards. At burn rate 1, the budget is spread over all 720 hours of 30 days.",
                  FadeOut(br), Create(hb), FadeIn(hl), FadeIn(h0), FadeIn(h1), run_time=3.0)
        sl = Rectangle(width=12.0 * 0.02 * 1.0, height=0.55, stroke_width=0).set_fill(RED_M, 0.9).move_to(hb.get_left() + RIGHT * 0.12)
        sl_l = T("2% of 720 = 14.4 hours of budget", 24, RED_M).move_to([-2.6, -0.4, 0])
        sl_a = Arrow(sl_l.get_left() + LEFT * 0.05, sl.get_bottom(), buff=0.1, stroke_width=2.5, color=RED_M, max_tip_length_to_length_ratio=0.15)
        self.beat("Page once a single hour has spent 2% of the budget. 2% of 720 hours is 14.4 hours of budget.",
                  FadeIn(sl), Succession(Wait(2.8), AnimationGroup(GrowArrow(sl_a), FadeIn(sl_l))), run_time=5.4)
        slot = RoundedRectangle(corner_radius=0.1, width=2.2, height=1.0, stroke_color=WHITE, stroke_width=2.5).move_to([2.9, -1.9, 0])
        slot_l = T("1 hour", 24).next_to(slot, UP, buff=0.15)
        blob = sl.copy()
        eq = T("14.4 hours of budget in 1 hour = burn rate 14.4", 26, YELLOW_M).move_to([0, -3.15, 0])
        self.beat("Spend that in one hour, and that is burn rate 14.4.",
                  Create(slot), FadeIn(slot_l),
                  Succession(Wait(0.8), blob.animate(run_time=1.4).set_fill(RED_M, 0.9).stretch_to_fit_width(1.9).stretch_to_fit_height(0.75).move_to(slot)),
                  Succession(Wait(2.6), FadeIn(eq, shift=UP * 0.1)), run_time=4.4)
        rules = VGroup(
            VGroup(chip("page", RED_M, 24), T("burn rate 14.4 over 1 hour, or 6 over 6 hours", 24)).arrange(RIGHT, buff=0.3),
            VGroup(chip("ticket", GOLD_M, 24), T("burn rate 1 over 3 days", 24)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, -1.55, 0])
        self.beat("These numbers come from Google's SRE Workbook. Page at 14.4 over one hour, or 6 over six hours. Ticket at 1 over three days.",
                  FadeOut(VGroup(slot, slot_l, blob, eq, sl_a, sl_l)), Succession(Wait(0.8), FadeIn(rules[0], shift=UP * 0.1)), Succession(Wait(4.0), FadeIn(rules[1], shift=UP * 0.1)), run_time=6.0)
        self.play(FadeOut(VGroup(hb, hl, h0, h1, sl, rules)), run_time=0.7)

        # ---- 6. sort alerts into page, ticket, dashboard
        bins = VGroup(box("page", RED_M, w=3.6, h=1.1, size=30), box("ticket", GOLD_M, w=3.6, h=1.1, size=30), box("dashboard only", GREY_B, w=3.6, h=1.1, size=30))
        bins.arrange(RIGHT, buff=0.6).move_to([0, -2.6, 0])
        subs = VGroup(T("users hurt now, act now", 22, GREY_B), T("in working hours", 22, GREY_B), T("everything else", 22, GREY_B))
        for s, b in zip(subs, bins):
            s.next_to(b, UP, buff=0.2)
        self.beat("Sort every alert into three groups. Page: users hurt now, and a human must act now. Ticket: a human, in working hours. Everything else: dashboard only.",
                  LaggedStart(*[AnimationGroup(FadeIn(b, shift=UP * 0.15), FadeIn(s)) for b, s in zip(bins, subs)], lag_ratio=0.8), run_time=8.6)

        def case(text, color):
            return chip(text, color, 24).move_to([0, 1.2, 0])

        cA = case("2% fail for 60 minutes", RED_M)
        mA = T("burn rate 0.02 / 0.001 = 20, above 14.4", 24, RED_M).next_to(cA, DOWN, buff=0.3)
        self.beat("A bad hour: 2% of requests fail for 60 minutes. Burn rate 20, above 14.4.",
                  FadeIn(cA, shift=DOWN * 0.15), Succession(Wait(2.4), FadeIn(mA)), run_time=4.0)
        self.beat("So it pages.",
                  FadeOut(mA), cA.animate.scale(0.85).move_to(bins[0].get_top() + UP * 1.05), FadeOut(subs[0]), run_time=1.0)
        cB = case("0.3% fail all week", GOLD_M)
        mB = T("burn rate 3: the budget lasts 10 days", 24, GOLD_M).next_to(cB, DOWN, buff=0.3)
        self.beat("A slow leak: 0.3% fail all week. Burn rate 3: the budget lasts 10 days. Nobody needs to wake up, but someone must fix it this week.",
                  FadeIn(cB, shift=DOWN * 0.15), Succession(Wait(2.6), FadeIn(mB)), Succession(Wait(5.6), AnimationGroup(FadeOut(mB), cB.animate.scale(0.85).move_to(bins[1].get_top() + UP * 1.05), FadeOut(subs[1]))), run_time=7.0)
        cC = case("CPU at 90%, answers in 50 ms", GREY_B)
        cD = case("one pod restart", GREY_B)
        self.beat("A server at 90% CPU that answers every request in 50 ms is simply doing its job.",
                  FadeIn(cC, shift=DOWN * 0.15), run_time=1.6)
        self.play(cC.animate.scale(0.85).move_to(bins[2].get_top() + UP * 1.05), FadeOut(subs[2]), FadeIn(cD, shift=DOWN * 0.15), run_time=0.9)
        self.beat("CPU, memory, single restarts: these are causes, and many never hurt anyone. They go on the dashboard.",
                  cD.animate.scale(0.85).move_to(bins[2].get_top() + UP * 1.75), run_time=1.6)
        fat = T("page on causes, and people learn to ignore the pager", 26, YELLOW_M).move_to([0, 1.6, 0])
        self.beat("Page on causes, and people learn that pages are noise, and ignore the real one too.",
                  FadeIn(fat, shift=DOWN * 0.1), run_time=2.2)

        # ---- recap
        rec = VGroup(T("An SLO turns raw requests into a budget,", 30), T("and the burn rate decides who gets woken up.", 30, YELLOW_M)).arrange(DOWN, buff=0.2).move_to([0, 1.4, 0])
        self.beat("An SLO turns raw requests into a budget, and the burn rate decides who gets woken up.",
                  FadeOut(fat), FadeIn(rec, shift=UP * 0.1), Circumscribe(bins[0], color=RED_M), run_time=3.0)
        self.wait(1.2)
