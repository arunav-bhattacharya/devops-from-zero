import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\b5xx\b", "five X X"), (r"(\d)%", r"\1 percent"), (r"\b404\b", "four oh four"),
    (r"\b3 a\.m\.", "three in the morning"), (r"\b10 GB\b", "ten gigabytes"), (r"\b500 km\b", "500 kilometres"),
])


def dark(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def frame(w, h, color, c, fill=0.08, sw=3):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw)
    return r.set_fill(dark(color, fill), opacity=1).move_to(c)


def lchip(text, color, size=24, mono=False):
    t = (M if mono else T)(text, size)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.34, height=max(0.6, t.height + 0.3), stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.22), opacity=1)
    return VGroup(r, t.move_to(r)).set_z_index(3)


def lamp(color, label):
    c = Circle(radius=0.36, stroke_color=color, stroke_width=4).set_fill(dark(color, 0.15), opacity=1)
    t = T(label, 24, GREY_B).next_to(c, DOWN, buff=0.2)
    return VGroup(c, t)


class D49DataPlan(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("A data plan for failure", "SLOs, error budgets and burn rates")

        # ---------------- 1. three lights on a dark highway
        dash = frame(11.0, 2.6, GREY_B, [0, 0.6, 0], fill=0.05)
        l1 = lamp(RED_M, "oil pressure low").move_to([-3.6, 0.6, 0])
        l2 = lamp(BLUE_M, "washer fluid low").move_to([0, 0.6, 0])
        l3 = lamp(GOLD_M, "service due in 500 km").move_to([3.6, 0.6, 0])
        self.beat("Picture driving home late on a quiet highway. Three lights come on at once.", Create(dash), run_time=1.4)
        self.beat("Oil pressure low. Washer fluid low. A service is due in 500 km.",
                  LaggedStart(*[AnimationGroup(l[0].animate.set_fill(dark(l[0].get_stroke_color(), 0.7)), FadeIn(l[1])) for l in (l1, l2, l3)], lag_ratio=0.6), run_time=3.0)
        stop = T("pull over now", 28, RED_M).next_to(dash, DOWN, buff=0.35).set_x(l1.get_x())
        self.beat("Only one of them means pull over now, and you have about two seconds to know which.",
                  Succession(Wait(0.6), AnimationGroup(Circumscribe(l1[0], Circle, color=RED_M), FadeIn(stop))), run_time=2.6)
        q = T("Which problems should wake an engineer at 3 a.m.?", 32, YELLOW_M).to_edge(UP, buff=0.6)
        self.beat("Software teams face that moment every night. So which problems should wake an engineer at 3 a.m.?",
                  Write(q), run_time=2.4)
        self.play(FadeOut(VGroup(dash, l1, l2, l3, stop)), run_time=0.5)
        opts = VGroup(T("A. CPU on the web servers above 90% for 10 minutes", 26), T("B. database disk 70% full, growing slowly", 26),
                      T("C. 5% of checkout requests failing for 10 minutes", 26), T("D. one pod restarted once, healthy again", 26))
        opts.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(DOWN * 0.2)
        self.beat("Four candidates. CPU above ninety percent. A disk seventy percent full. Five percent of checkouts failing. And one pod, a running copy of the app, that restarted once.",
                  LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.5), run_time=6.0)
        self.guess([0, -2.8, 0])
        hold = T("hold that guess: we come back to it at the end", 24, GREY_B).to_edge(DOWN, buff=0.6)
        self.beat("Hold that guess. To answer it properly, we first need a number that says what working means.", FadeIn(hold), run_time=1.4)
        self.play(FadeOut(VGroup(q, opts, hold)), run_time=0.5)

        # ---------------- 2. the two bad habits
        many = VGroup(*[Circle(radius=0.22, stroke_color=c, stroke_width=3).set_fill(dark(c, 0.6), opacity=1)
                        for c in [RED_M, GOLD_M, BLUE_M, RED_M, GOLD_M, RED_M, BLUE_M, GOLD_M, RED_M, BLUE_M, RED_M, GOLD_M]]).arrange_in_grid(2, 6, buff=0.4)
        many.move_to(UP * 0.8)
        h1 = T("every light urgent", 28, RED_M).next_to(many, DOWN, buff=0.5).shift(LEFT * 3.6)
        h2 = T("after the tenth false alarm: ignore them all", 28, GREY_B).next_to(many, DOWN, buff=0.5).shift(RIGHT * 2.0)
        tape = VGroup(*[Rectangle(width=0.62, height=0.2, stroke_width=0).set_fill(GREY_C, 1).rotate(0.4).move_to(m) for m in many])
        self.beat("It is easy to treat every light as urgent. Then, after the tenth false alarm, you ignore them all, like a driver who tapes over the warning lights. That is alert fatigue.",
                  LaggedStart(*[FadeIn(m, scale=1.3) for m in many], lag_ratio=0.08), FadeIn(h1),
                  Succession(Wait(2.4), FadeIn(h2), LaggedStart(*[FadeIn(t) for t in tape], lag_ratio=0.06)), run_time=6.0)
        self.play(FadeOut(VGroup(many, tape, h1, h2)), run_time=0.5)

        # ---------------- 3. SLI and SLO for hello-devops
        top_ = T("responses to / that are not 5xx", 30, GREEN_M)
        bar = Line(LEFT * 3.2, RIGHT * 3.2, stroke_width=3)
        bot = T("all responses to /", 30)
        frac = VGroup(top_, bar, bot).arrange(DOWN, buff=0.22).move_to(UP * 0.9)
        sli = T("SLI", 34, GREEN_M).next_to(frac, LEFT, buff=0.6)
        self.beat("Start with what users feel. For hello-devops, our tiny lab app, count the good answers at slash, the ones that are not a server failure, and divide by all the answers.",
                  Write(top_), Create(bar), Write(bot), run_time=3.0)
        self.beat("That ratio is called an SLI, a service level indicator.", FadeIn(sli, shift=RIGHT * 0.1), run_time=1.6)
        nf = T("a 404 for a mistyped address is the user's mistake: it does not count", 24, GREY_B).next_to(frac, DOWN, buff=0.45)
        self.beat("A not found, for a mistyped address, is the user's mistake. It does not count against you.", FadeIn(nf), run_time=1.6)
        slo = T("SLO: 99.9% over 30 days", 34, YELLOW_M).next_to(nf, DOWN, buff=0.5)
        self.beat("Now give it a target and a window. Ninety nine point nine percent, over thirty days. A target like that is an SLO, a service level objective.",
                  Write(slo), run_time=2.4)
        why = T("why not 100%?", 28, GREY_B).next_to(slo, RIGHT, buff=0.5)
        self.beat("Why not a hundred? Users rarely notice, because their own phone and network fail far more often. And each extra nine costs far more work.",
                  FadeIn(why), run_time=2.0)
        self.play(FadeOut(VGroup(top_, bar, bot, sli, nf, why)), slo.animate.scale(0.8).to_corner(UL, buff=0.6), run_time=0.6)

        # ---------------- 4. the phone plan, mapped
        phone = RoundedRectangle(corner_radius=0.25, width=1.8, height=3.2, stroke_color=BLUE_M, stroke_width=4).move_to([-4.3, -0.2, 0])
        tank = Rectangle(width=0.9, height=2.2, stroke_color=BLUE_M, stroke_width=2).move_to(phone)
        fill = Rectangle(width=0.9, height=2.2, stroke_width=0).set_fill(BLUE_M, 0.7).move_to(tank)
        gb = T("10 GB a month", 28, BLUE_M).next_to(phone, DOWN, buff=0.3)
        self.beat("Here is a picture that helps. Think of a phone plan with ten gigabytes of data a month.", Create(phone), Create(tank), FadeIn(fill), FadeIn(gb), run_time=1.8)
        vid = T("one video: no panic", 26, GREY_B).move_to([0.6, 1.0, 0])
        self.beat("You do not panic about every video you watch.", fill.animate.stretch_to_fit_height(2.05, about_edge=DOWN), FadeIn(vid), run_time=1.4)
        half = T("half gone on day 3: panic", 26, RED_M).move_to([0.6, 0.2, 0])
        self.beat("You panic when half the data is gone on day three. It is not the amount that scares you. It is the speed.",
                  fill.animate.stretch_to_fit_height(1.1, about_edge=DOWN).set_fill(RED_M, 0.7), FadeIn(half), run_time=2.0)
        maps = VGroup(T("data allowance  =  allowed failure: the error budget", 26, BLUE_M),
                      T("the month  =  the 30-day window", 26, BLUE_M),
                      T("how fast it drains  =  the burn rate", 26, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([1.6, -1.6, 0])
        self.beat("Map it. The data allowance is the failure your target allows: the error budget. The month is the thirty day window. How fast it drains is the burn rate.",
                  LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in maps], lag_ratio=0.7), run_time=5.0)
        self.wait(0.3)
        self.play(FadeOut(VGroup(phone, tank, fill, gb, vid, half, maps)), run_time=0.5)

        # ---------------- 5. the numbers, small
        eq = VGroup(T("budget  =  100%  -  99.9%  =  0.1%", 32)).move_to(UP * 2.0)
        self.beat("So how big is the budget? A hundred percent, minus the target. Point one percent.", Write(eq), run_time=1.8)
        req = VGroup(T("200,000 requests a day  x  30 days  =  6,000,000", 28),
                     T("0.1% of 6,000,000  =  6,000 may fail", 28, GOLD_M)).arrange(DOWN, buff=0.3).move_to(UP * 0.6)
        guessn = T("200,000 a day is a guess, for the example", 22, GREY_B).next_to(req, DOWN, buff=0.25)
        self.beat("Say two hundred thousand requests a day, my guess for the example. Thirty days hold six million, and six thousand of them may fail.",
                  FadeIn(req[0]), FadeIn(guessn), Succession(Wait(1.6), FadeIn(req[1], shift=UP * 0.1)), run_time=4.0)
        mins = T("if everything fails at once:  0.1% of 43,200 minutes  =  43.2 minutes", 28, GOLD_M).next_to(guessn, DOWN, buff=0.45)
        self.beat("If everything fails at once, that is point one percent of a month's minutes. Forty three point two minutes of full outage.",
                  FadeIn(mins, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(VGroup(eq, req, guessn)), mins.animate.move_to(UP * 2.3), run_time=0.6)
        mb = Rectangle(width=10.0, height=0.6, stroke_color=GOLD_M, stroke_width=3).move_to(UP * 0.8)
        ml = T("43.2 minutes a month", 26, GOLD_M).next_to(mb, DOWN, buff=0.2).align_to(mb, LEFT)
        self.beat("One bad deploy breaks everything for twenty minutes. How much of the month is gone?", Create(mb), FadeIn(ml), run_time=1.6)
        self.guess([0, -1.0, 0])
        used = Rectangle(width=10.0 * 20 / 43.2, height=0.6, stroke_width=0).set_fill(RED_M, 0.75).move_to(mb, aligned_edge=LEFT)
        pct = T("20 minutes  =  46% of the month", 30, RED_M).next_to(mb, DOWN, buff=0.7)
        self.beat("Almost half. Twenty out of forty three point two is forty six percent, in one evening.", GrowFromEdge(used, LEFT), FadeIn(pct), run_time=2.0)
        roll = T("so a rollback has to take minutes, not an hour", 28, YELLOW_M).next_to(pct, DOWN, buff=0.4)
        self.beat("So the point is, a rollback has to take minutes, not an hour.", FadeIn(roll, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(mins, mb, ml, used, pct, roll)), run_time=0.5)

        # ---------------- 6. burn rate on a 30-day graph
        ax = Axes(x_range=[0, 30, 5], y_range=[0, 100, 25], x_length=8.6, y_length=4.2, tips=False,
                  axis_config={"stroke_color": GREY_B, "stroke_width": 2, "include_ticks": True}).move_to([0.9, -0.2, 0])
        xl = VGroup(*[T(str(d), 22, GREY_B).next_to(ax.c2p(d, 0), DOWN, buff=0.15) for d in (0, 5, 10, 15, 20, 25, 30)])
        xt = T("days", 24, GREY_B).next_to(ax.c2p(30, 0), DOWN, buff=0.55)
        yl = VGroup(*[T(f"{p}%", 22, GREY_B).next_to(ax.c2p(0, p), LEFT, buff=0.15) for p in (0, 50, 100)])
        yt = T("budget left", 24, GREY_B).next_to(ax.c2p(0, 100), UP, buff=0.25)
        form = T("burn rate  =  error ratio  /  budget", 30, YELLOW_M).to_edge(UP, buff=0.5)
        self.beat("Now the speed. The burn rate is the error ratio right now, divided by the budget.", FadeOut(slo), Write(form), run_time=1.6)
        self.beat("Here is a month, and the budget left, from full to empty.", Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(xt), FadeIn(yt), run_time=2.0)
        b1 = Line(ax.c2p(0, 100), ax.c2p(30, 0), color=GREEN_M, stroke_width=4)
        b1l = T("0.1% failing: rate 1, lasts 30 days", 24, GREEN_M).move_to(ax.c2p(21, 72))
        self.beat("Point one percent failing is burn rate one. The budget lasts exactly thirty days. That is the plan working.", Create(b1), FadeIn(b1l), run_time=2.4)
        b6 = Line(ax.c2p(0, 100), ax.c2p(5, 0), color=GOLD_M, stroke_width=4)
        b6l = T("0.6%: rate 6, gone in 5 days", 24, GOLD_M).move_to(ax.c2p(13.5, 48))
        self.beat("Point six percent failing is burn rate six. The budget is gone in five days.", Create(b6), FadeIn(b6l), run_time=1.8)
        b14 = Line(ax.c2p(0, 100), ax.c2p(30 / 14.4, 0), color=RED_M, stroke_width=4)
        b14l = T("1.44%: rate 14.4, gone in about 2 days", 24, RED_M).move_to(ax.c2p(13.2, 24))
        self.beat("And one point four four percent is burn rate fourteen point four. Gone in about two days.", Create(b14), FadeIn(b14l), run_time=1.8)
        self.beat("Same plan. Only the speed changed.", Indicate(b14, color=RED_M), run_time=1.8)
        self.play(FadeOut(VGroup(b1l, b6l, b14l)), VGroup(ax, xl, yl, xt, yt, b1, b6, b14).animate.scale(0.55).to_corner(DL, buff=0.6), run_time=0.7)
        graph = VGroup(ax, xl, yl, xt, yt, b1, b6, b14)

        # ---------------- 7. break the raw count; where 14.4 comes from
        raw = T("Why not just alert on more than 10 failures?", 30).move_to([1.5, 1.6, 0])
        self.beat("You might be thinking: why the fancy ratio? Why not just alert when more than ten requests fail?", FadeIn(raw), run_time=1.8)
        busy = T("busy shop: 10 failures is nothing", 26, GREY_B).move_to([2.6, 0.6, 0])
        quiet = T("quiet shop: 10 failures is a lot", 26, RED_M).move_to([2.6, -0.1, 0])
        self.beat("Because ten failures mean nothing on a busy shop, and a lot on a quiet one. Burn rate is already scaled to your traffic and your target.",
                  FadeIn(busy), Succession(Wait(1.2), FadeIn(quiet)), run_time=3.0)
        self.play(FadeOut(VGroup(raw, busy, quiet)), run_time=0.4)
        w = VGroup(T("30 days  =  720 hours", 28), T("2% of 720 hours  =  14.4 hours of budget", 28),
                   T("spent in 1 hour  =  burn rate 14.4", 28, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to([2.2, 0.6, 0])
        self.beat("And why fourteen point four? A month has seven hundred and twenty hours. At that speed, one single hour spends two percent of the month's budget.",
                  LaggedStart(*[FadeIn(x, shift=RIGHT * 0.1) for x in w], lag_ratio=0.8), run_time=5.0)
        self.play(FadeOut(w), run_time=0.4)

        # ---------------- 8. page, ticket, dashboard
        cols = [("page", RED_M, "users hurt now"), ("ticket", GOLD_M, "working hours"), ("dashboard", BLUE_M, "everything else")]
        heads = VGroup()
        for i, (n, c, s) in enumerate(cols):
            b = frame(3.6, 3.7, c, [-2.6 + 3.9 * i, -0.4, 0], fill=0.06)
            t = T(n, 30, c).move_to(b.get_top() + DOWN * 0.4)
            st = T(s, 22, GREY_B).next_to(t, DOWN, buff=0.15)
            fit(st, 3.3)
            heads.add(VGroup(b, t, st))
        heads.move_to([1.3, 0.8, 0])
        self.play(FadeOut(graph), FadeOut(form), run_time=0.5)
        heads.move_to([0, 0.1, 0])
        self.beat("Now we can sort the lights. Every alert goes into one of three boxes. Page, ticket, or dashboard.",
                  LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in heads], lag_ratio=0.3), run_time=2.4)
        p1 = T("rate 14.4 over 1 hour", 24, RED_M).next_to(heads[0][2], DOWN, buff=0.3)
        p2 = T("or rate 6 over 6 hours", 24, RED_M).next_to(p1, DOWN, buff=0.15)
        t1 = T("rate 1 over 3 days", 24, GOLD_M).next_to(heads[1][2], DOWN, buff=0.3)
        self.beat("Google's SRE Workbook suggests: page someone at burn rate fourteen point four over one hour, or six over six hours.",
                  FadeIn(p1), FadeIn(p2), run_time=2.2)
        self.beat("Open a ticket, a task for working hours, at burn rate one over three days.", FadeIn(t1), run_time=1.6)
        bad = T("2% failing for an hour: 0.02 / 0.001 = rate 20", 26).to_edge(UP, buff=0.5)
        self.beat("Try one. Two percent of requests fail for an hour. Page, or ticket?", FadeIn(bad), run_time=1.6)
        self.guess([0, -2.6, 0])
        bchip = lchip("rate 20: page", RED_M, 24).next_to(p2, DOWN, buff=0.25)
        self.beat("Two percent over point one percent is burn rate twenty. Above fourteen point four, so it pages.",
                  TransformFromCopy(bad, bchip), run_time=2.4)
        self.play(FadeOut(bad), run_time=0.3)

        # pay off the opening guess
        ga = lchip("C. 5% checkouts failing", RED_M, 22).next_to(bchip, DOWN, buff=0.15)
        gb_ = lchip("B. disk 70%, slowly", GOLD_M, 22).next_to(t1, DOWN, buff=0.25)
        gc = lchip("A. CPU above 90%", BLUE_M, 22).next_to(heads[2][2], DOWN, buff=0.3)
        gd = lchip("D. one pod restart", BLUE_M, 22).next_to(gc, DOWN, buff=0.15)
        self.beat("Back to our four lights. Failed checkouts are something users feel, right now. That is a page.",
                  FadeIn(ga, shift=LEFT * 0.2), run_time=1.6)
        self.beat("The other three are possible causes, which may never hurt anyone. A busy server that answers every request quickly is simply doing its job.",
                  FadeIn(gc, shift=LEFT * 0.2), FadeIn(gd, shift=LEFT * 0.2), run_time=2.4)
        self.beat("So they go on a screen you look at, or on a to-do list.", FadeIn(gb_, shift=LEFT * 0.2), run_time=1.4)
        rule = T("Wake people for what users feel. Put the causes on a dashboard.", 30, YELLOW_M).to_edge(UP, buff=0.5)
        fit(rule, 12.6)
        self.beat("Wake people for what users feel. Put the causes on a dashboard.", Write(rule), run_time=2.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(heads, p1, p2, t1, bchip, ga, gb_, gc, gd, rule)), run_time=0.6)

        # ---------------- 9. guardrails
        g = VGroup(T("a page must be urgent, real, and something a human can act on", 28),
                   T("if an alert fires and nobody needs to act: delete it, or make it a ticket", 28),
                   T("budget spent: pause risky releases until reliability is back", 28),
                   T("budget never touched: speed you never used", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.34).move_to(DOWN * 0.1)
        fit(g, 12.4)
        gt = T("Guardrails", 32, GOLD_M).next_to(g, UP, buff=0.5).align_to(g, LEFT)
        self.beat("A few guardrails. A page must be urgent, real, and something a human can act on. If nobody needs to act, delete it, or make it a ticket.",
                  Write(gt), FadeIn(g[0], shift=RIGHT * 0.1), Succession(Wait(2.6), FadeIn(g[1], shift=RIGHT * 0.1)), run_time=4.0)
        self.beat("When the budget is spent, pause risky releases. And a budget you never touch is speed you never used.",
                  FadeIn(g[2], shift=RIGHT * 0.1), Succession(Wait(1.8), FadeIn(g[3], shift=RIGHT * 0.1)), run_time=3.0)
        self.play(FadeOut(VGroup(g, gt)), run_time=0.5)

        # ---------------- 10. moral, recap, check
        rec = VGroup(T("SLI: good answers over all answers", 28, GREEN_M),
                     T("SLO: the target, 99.9% over 30 days", 28, YELLOW_M),
                     T("error budget: the data plan, 0.1%", 28, BLUE_M),
                     T("burn rate: how fast it drains; fast burns page", 28, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(UP * 0.5)
        self.beat("So the moral of the story. Count good answers, set a target, and treat the failure it allows as your data plan. What wakes people is not a failure, but the speed of the drain.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=8.0)
        self.play(FadeOut(rec), run_time=0.5)
        c1 = T("Quick check: 0.3% of requests fail, all week.", 30).move_to(UP * 0.6)
        c2 = T("What is the burn rate, and is it a page or a ticket?", 30).next_to(c1, DOWN, buff=0.3)
        self.beat("A quick check. Point three percent of requests fail, all week. What is the burn rate, and is it a page or a ticket?",
                  FadeIn(c1), FadeIn(c2), run_time=1.8)
        self.guess([0, -1.0, 0])
        ans = T("Rate 3: the budget lasts 10 days. A ticket, fixed this week.", 30, GREEN_M).next_to(c2, DOWN, buff=0.6)
        fit(ans, 12.6)
        self.beat("Burn rate three. The budget lasts ten days. Nobody needs to wake up, but someone must fix it this week. A ticket.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.2)
