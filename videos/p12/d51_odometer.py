import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\brate\(\)", "rate"), (r"\birate\b", "I rate"), (r"\[10s\]", "ten seconds"), (r"\[1m\]", "one minute"), (r"\[5m\]", "five minutes"),
    (r"\[30s\]", "thirty seconds"), (r"\bp95\b", "P ninety-five"), (r"(\d)%", r"\1 percent"), (r"\b5xx\b", "five X X"),
    (r"\bhistogram_quantile\b", "histogram quantile"), (r"\bvector\(0\)", "vector zero"),
])

SAMPLES = [(0, 99), (15, 167), (30, 235), (45, 303)]


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


def odo(n, color=WHITE):
    digs = VGroup(*[VGroup(Rectangle(width=0.5, height=0.72, stroke_color=GREY_B, stroke_width=2).set_fill(GREY_D, 0.6), M(ch, 34, color)) for ch in n])
    for d in digs:
        d[1].move_to(d[0])
    return digs.arrange(RIGHT, buff=0.06)


class D51Odometer(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("From odometer to speedometer", "PromQL, rate() and the queries that go quiet")

        # ---------------- 1. the broken speedometer
        sp = Arc(radius=1.4, start_angle=PI * 0.9, angle=-PI * 0.8, stroke_color=GREY_B, stroke_width=5).move_to([-3.2, 1.0, 0])
        needle = Line(sp.get_center() + DOWN * 0.3, sp.get_center() + DOWN * 0.3 + UL * 1.0, stroke_color=RED_M, stroke_width=5)
        sp_l = T("speedometer: broken", 26, RED_M).next_to(sp, DOWN, buff=0.7)
        od = odo("52310").move_to([3.0, 1.0, 0])
        od_l = T("odometer: every km ever driven", 26, GREY_B).next_to(od, DOWN, buff=0.4)
        self.beat("Picture a car whose speedometer has broken. Only the odometer still works, the counter of every kilometre the car has ever driven.",
                  Create(sp), Create(needle), FadeIn(sp_l), FadeIn(od), FadeIn(od_l), run_time=3.0)
        x = tick(False, 0.4).move_to(sp.get_center() + DOWN * 0.2)
        self.beat("It reads fifty two thousand three hundred and ten. Are you going too fast?", Create(x), Indicate(od, color=WHITE), run_time=1.8)
        self.beat("The number cannot tell you. It is precise, and it keeps moving, and it says nothing about right now.", run_time=None)
        od2 = odo("52311").move_to(od)
        n1 = T("now: 52,310", 26, TEAL_M).move_to([3.0, -1.2, 0])
        n2 = T("one minute later: 52,311", 26, TEAL_M).next_to(n1, DOWN, buff=0.2)
        spd = T("1 km in 1 minute = 60 km/h", 30, YELLOW_M).next_to(n2, DOWN, buff=0.35)
        self.beat("But note it now. Note it again a minute later. Divide the difference by the time.",
                  FadeIn(n1), Succession(Wait(0.8), AnimationGroup(Transform(od, od2), FadeIn(n2))), run_time=2.6)
        self.beat("One kilometre in one minute. Sixty kilometres an hour. Now you know your speed.", Write(spd), run_time=1.8)
        self.wait(0.3)
        self.play(FadeOut(VGroup(sp, needle, sp_l, od, od_l, x, n1, n2, spd)), run_time=0.6)

        # ---------------- 2. our counters are odometers
        q0 = M("hello_responses_total", 30, TEAL_M).to_edge(UP, buff=0.7)
        res = VGroup(M('{path="/", status="200"}         303', 24), M('{path="/healthz", status="200"}  3', 24),
                     M('{path="unmatched", status="404"}  1', 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(UP * 1.0)
        self.beat("Our app's counters are odometers. Ask Prometheus for the bare name, hello responses total, and you get three answers, one per label set.",
                  Write(q0), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in res], lag_ratio=0.4), run_time=3.0)
        self.beat("Three hundred and three requests since the app started. That says almost nothing about right now.", Indicate(res[0], color=TEAL_M), run_time=1.8)
        iv = T("one value per series, for one moment: an instant vector", 24, GREY_B).next_to(res, DOWN, buff=0.4)
        self.beat("One value per series, all for the same moment. It is like asking every car in a car park for its odometer reading.", FadeIn(iv), run_time=2.0)
        self.play(FadeOut(VGroup(res, iv)), run_time=0.4)

        # ---------------- 3. a range: four samples, then the speed
        ax = Axes(x_range=[0, 60, 15], y_range=[0, 400, 100], x_length=7.4, y_length=3.8, tips=False,
                  axis_config={"stroke_color": GREY_B, "stroke_width": 2}).move_to([-1.6, -0.4, 0])
        xl = VGroup(*[T(f"{s} s", 22, GREY_B).next_to(ax.c2p(s, 0), DOWN, buff=0.15) for s in (0, 15, 30, 45)])
        dots = VGroup(*[Dot(ax.c2p(t, v), radius=0.1, color=GOLD_M) for t, v in SAMPLES])
        vl = VGroup(*[T(str(v), 24, GOLD_M).next_to(d, UP, buff=0.15) for d, (t, v) in zip(dots, SAMPLES)])
        q1 = M('hello_responses_total{path="/"}[1m]', 28, TEAL_M).move_to(q0)
        self.beat("Add a time range in square brackets, one minute, and you get every reading in that window.",
                  ReplacementTransform(q0, q1), Create(ax), FadeIn(xl), run_time=2.0)
        self.beat("Prometheus reads the app every fifteen seconds, so a minute holds four readings. Ninety nine, one sixty seven, two thirty five, three hundred and three.",
                  LaggedStart(*[AnimationGroup(GrowFromCenter(d), FadeIn(v)) for d, v in zip(dots, vl)], lag_ratio=0.5), run_time=3.6)
        rv = T("all readings in a window: a range vector", 24, GREY_B).next_to(ax, UP, buff=0.2).align_to(ax, LEFT)
        self.beat("That is called a range vector: every reading in the window.", FadeIn(rv), run_time=1.4)
        rise = DashedLine(ax.c2p(45, 99), ax.c2p(45, 303), stroke_color=TEAL_M, stroke_width=3)
        run = DashedLine(ax.c2p(0, 99), ax.c2p(45, 99), stroke_color=TEAL_M, stroke_width=3)
        calc = VGroup(T("last minus first", 26, TEAL_M), T("303 - 99 = 204", 28), T("over 45 seconds", 26, TEAL_M),
                      T("about 4.5 per second", 30, YELLOW_M)).arrange(DOWN, buff=0.2).move_to([4.4, 0.0, 0])
        self.beat("Now do what we did in the car. Last minus first: two hundred and four requests.",
                  Create(rise), FadeIn(calc[0]), FadeIn(calc[1]), run_time=2.0)
        self.beat("Over the forty five seconds between them. About four and a half requests a second. A speed.",
                  Create(run), FadeIn(calc[2]), FadeIn(calc[3]), run_time=2.0)
        fn = M('rate(hello_responses_total{path="/"}[1m])', 28, YELLOW_M).move_to(q1)
        fit(fn, 12.4)
        self.beat("You never do that by hand. The function rate does the subtraction and the division for you, for every series at once.",
                  ReplacementTransform(q1, fn), run_time=2.0)
        nm = T("rate(): the average growth per second of a counter, over a range", 26, YELLOW_M).next_to(fn, DOWN, buff=0.2)
        fit(nm, 12.4)
        self.beat("rate: the average growth per second of a counter, over a time range.", FadeIn(nm), run_time=1.6)
        self.play(FadeOut(VGroup(calc, rise, run, rv, nm)), run_time=0.4)

        # ---------------- 4. predict: a ten second window
        fn10 = M("rate(hello_responses_total[10s])", 28, YELLOW_M).move_to(fn)
        self.beat("Now a small change. Same scrape every fifteen seconds, but a window of only ten seconds. What does this return?",
                  ReplacementTransform(fn, fn10), run_time=1.8)
        fn = fn10
        opts = VGroup(T("A. requests per second", 24), T("B. zero", 24), T("C. an error", 24), T("D. nothing at all", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        opts.move_to([4.6, -0.2, 0])
        self.play(FadeIn(opts), run_time=0.5)
        self.guess([4.6, -2.3, 0])
        win = Rectangle(width=ax.c2p(10, 0)[0] - ax.c2p(0, 0)[0], height=3.6, stroke_color=BLUE_M, stroke_width=3).set_fill(BLUE_M, 0.12)
        win.move_to(ax.c2p(40, 200))
        self.beat("Slide a ten second window along the readings. It usually holds only one.",
                  FadeIn(win), win.animate.move_to(ax.c2p(42, 200)), run_time=1.8)
        self.play(win.animate.move_to(ax.c2p(23, 200)), run_time=1.0)
        self.beat("One reading, nothing to subtract. So the series quietly drops out of the result. No error, no zero. Nothing at all.",
                  opts[3].animate.set_color(GREEN_M), Indicate(dots[1], color=BLUE_M), run_time=2.4)
        self.beat("Well, that is a query that looks right and answers with silence.", run_time=None)
        rule = T("range: at least 4 x the scrape interval", 30, YELLOW_M).move_to([0, -3.15, 0])
        w4 = Rectangle(width=ax.c2p(60, 0)[0] - ax.c2p(0, 0)[0], height=3.6, stroke_color=GREEN_M, stroke_width=3).set_fill(GREEN_M, 0.08).move_to(ax.c2p(30, 200))
        self.beat("The fix is a longer window. Use at least four times the scrape interval. With fifteen seconds, one minute. It needs two readings, and four leave enough when one scrape fails.",
                  ReplacementTransform(win, w4), FadeOut(opts), Write(rule), run_time=3.0)
        self.wait(0.3)
        self.play(FadeOut(VGroup(w4, rule, fn)), run_time=0.4)

        # ---------------- 5. empty is not zero
        e1 = M('hello_responses_total{status=~"5.."}', 26, RED_M).move_to([3.0, 2.6, 0])
        self.play(FadeOut(VGroup(ax, xl, dots, vl)), run_time=0.4)
        e1.move_to([0, 2.4, 0])
        self.beat("That silence has a cousin. Before the app had ever failed, ask for its server errors.", Write(e1), run_time=1.8)
        emp = T("(no series)", 30, GREY_B).next_to(e1, DOWN, buff=0.4)
        self.beat("You get nothing. Not zero. No series with a five hundred label exists yet.", FadeIn(emp), run_time=1.6)
        ch1 = frame(4.6, 2.2, GREEN_M, [-3.2, -1.2, 0], fill=0.06)
        ch1_t = T("errors: 0", 30, GREEN_M).move_to(ch1)
        ch2 = frame(4.6, 2.2, GREY_B, [3.2, -1.2, 0], fill=0.02)
        ch2.set_stroke(opacity=0.5)
        ch2_t = T("(page torn out)", 28, GREY_B).move_to(ch2)
        self.beat("And any maths with an empty side is empty too. An error ratio shows nothing, where you expected zero.", Create(ch2), FadeIn(ch2_t), run_time=1.8)
        fix = M("... or vector(0)", 26, GREEN_M).next_to(emp, DOWN, buff=0.35)
        self.beat("Add or vector zero to the error part, and you get a real zero. It is the difference between a chart that says no errors, and a chart with the page torn out.",
                  FadeIn(fix), Create(ch1), FadeIn(ch1_t), run_time=2.6)
        self.wait(0.3)
        self.play(FadeOut(VGroup(e1, emp, ch1, ch1_t, ch2, ch2_t, fix)), run_time=0.5)

        # ---------------- 6. restarts, and rate then sum
        ax2 = Axes(x_range=[0, 6, 1], y_range=[0, 2600, 500], x_length=6.0, y_length=3.0, tips=False,
                   axis_config={"stroke_color": GREY_B, "stroke_width": 2}).move_to([-3.0, 0.3, 0])
        pts = [(0, 1900), (1, 2080), (2, 2250), (3, 2370), (4, 11), (5, 190)]
        cl = VMobject(stroke_color=GOLD_M, stroke_width=4).set_points_as_corners([ax2.c2p(*p) for p in pts])
        cdots = VGroup(*[Dot(ax2.c2p(*p), radius=0.08, color=GOLD_M) for p in pts])
        la = T("2370", 24, GOLD_M).next_to(cdots[3], UP, buff=0.12)
        lb = T("11", 24, GOLD_M).next_to(cdots[4], RIGHT, buff=0.12)
        self.beat("Odometers have one more trick. When the app restarts, its counter falls back to zero. In one test, it went from two thousand three hundred and seventy to eleven.",
                  Create(ax2), Create(cl), FadeIn(cdots), FadeIn(la), FadeIn(lb), run_time=3.0)
        mech = T("rate() reads any drop as a restart", 26, TEAL_M).move_to([3.4, 1.2, 0])
        mech2 = T("the 11 count as new requests", 26, TEAL_M).next_to(mech, DOWN, buff=0.2)
        self.beat("rate reads any drop as a restart, like a mechanic who sees a lower reading and knows the odometer was replaced. Those eleven count as new requests, not as a fall.",
                  FadeIn(mech), FadeIn(mech2), run_time=2.6)
        self.play(FadeOut(VGroup(ax2, cl, cdots, la, lb, mech, mech2)), run_time=0.4)
        taxis = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.1, width=1.3, height=0.6, stroke_color=c, stroke_width=3).set_fill(dark(c, 0.2), 1),
                                T(n, 22).set_z_index(2)) for c, n in ((BLUE_M, "copy 1"), (BLUE_M, "copy 2"), (BLUE_M, "copy 3"))]).arrange(DOWN, buff=0.3)
        for t in taxis:
            t[1].move_to(t[0])
        taxis.move_to([-5.0, 0.3, 0])
        self.beat("Now run three copies of the app, like a taxi fleet, and you want the total. Two ways to write it. Add the counters first, then take the rate. Or take each rate, then add.",
                  LaggedStart(*[FadeIn(t) for t in taxis], lag_ratio=0.3), run_time=3.0)
        wrong = M("rate(sum(...))", 26, RED_M).move_to([-1.2, 2.0, 0])
        right = M("sum(rate(...))", 26, GREEN_M).move_to([3.6, 2.0, 0])
        self.beat("Let's steelman the first. It looks tidy. One sum, one rate.", FadeIn(wrong), run_time=1.4)
        ax3 = Axes(x_range=[0, 6, 1], y_range=[0, 10, 5], x_length=3.6, y_length=2.4, tips=False, axis_config={"stroke_color": GREY_B, "stroke_width": 2}).move_to([-1.2, -0.3, 0])
        sp1 = VMobject(stroke_color=RED_M, stroke_width=4).set_points_as_corners([ax3.c2p(*p) for p in [(0, 3), (1, 3), (2, 3), (3, 9.5), (4, 3), (5, 3)]])
        ax4 = ax3.copy().move_to([3.6, -0.3, 0])
        fl = VMobject(stroke_color=GREEN_M, stroke_width=4).set_points_as_corners([ax4.c2p(*p) for p in [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3)]])
        self.beat("One copy restarts. Its counter drops, so the total dips. And rate, looking at the total, mistakes that dip for a reset of the whole sum.",
                  Indicate(taxis[1][0], color=RED_M), Create(ax3), run_time=2.4)
        sl = T("false spike", 26, RED_M).next_to(ax3, DOWN, buff=0.25)
        self.beat("You get a spike of traffic that never happened.", Create(sp1), FadeIn(sl), run_time=1.6)
        ok = T("steady", 26, GREEN_M).next_to(ax4, DOWN, buff=0.25)
        self.beat("Take each copy's rate first, where a restart is visible, and then add. Steady, and true.", FadeIn(right), Create(ax4), Create(fl), FadeIn(ok), run_time=2.4)
        r2 = T("Rate first, then add. Never the other way round.", 30, YELLOW_M).to_edge(DOWN, buff=0.6)
        self.beat("So the rule. Take the rate of each series first, then add them up. Never the other way round.", Write(r2), run_time=1.8)
        self.wait(0.3)
        self.play(FadeOut(VGroup(taxis, wrong, right, ax3, sp1, sl, ax4, fl, ok, r2)), run_time=0.5)

        # ---------------- 7. how slow: buckets and an estimate
        self.beat("The third question is how slow. And here Prometheus never stores each request's time. It stores boxes.", run_time=None)
        bx = VGroup()
        specs = [("up to 0.01 s", 80), ("up to 0.025 s", 97)]
        for i, (lab, n) in enumerate(specs):
            b = frame(3.4, 1.2, GOLD_M, [-2.3 + 4.6 * i, 1.4, 0], fill=0.10)
            t1 = T(lab, 26, GOLD_M).move_to(b.get_center() + UP * 0.22)
            t2 = T(f"{n} requests", 26).move_to(b.get_center() + DOWN * 0.25)
            bx.add(VGroup(b, t1, t2))
        self.beat("Picture a post office that sorts parcels by weight into boxes. Up to one kilo, up to two. It never writes down each parcel's weight, only how many landed in each box.",
                  LaggedStart(*[FadeIn(b[0]) for b in bx], lag_ratio=0.3), run_time=2.6)
        self.beat("A histogram does that with request times. Say a hundred requests a second arrive. Eighty finish within ten milliseconds. Ninety seven within twenty five. Each box counts all the smaller ones too.",
                  LaggedStart(*[AnimationGroup(FadeIn(b[1]), FadeIn(b[2])) for b in bx], lag_ratio=0.5), run_time=4.0)
        p95q = T("Where is the 95th request?", 30, YELLOW_M).move_to([0, -0.2, 0])
        self.beat("Where is the ninety fifth request? Pause and guess its time.", FadeIn(p95q), run_time=1.4)
        self.wait(2.0)
        line = NumberLine(x_range=[0.01, 0.025, 0.005], length=8.0, include_numbers=False, stroke_color=GREY_B).move_to([0, -1.6, 0])
        nl = VGroup(T("0.01 s", 22, GREY_B).next_to(line.n2p(0.01), DOWN, buff=0.2), T("0.025 s", 22, GREY_B).next_to(line.n2p(0.025), DOWN, buff=0.2))
        ticks17 = VGroup(*[Line(UP * 0.18, DOWN * 0.18, stroke_color=TEAL_M, stroke_width=3).move_to(line.n2p(0.01 + 0.015 * (k + 0.5) / 17)) for k in range(17)])
        mid = T("17 requests between the two limits", 24, TEAL_M).next_to(line, UP, buff=0.35)
        self.beat("It is somewhere in the box between ten and twenty five milliseconds, which holds seventeen requests. Prometheus assumes they are spread evenly.",
                  Create(line), FadeIn(nl), LaggedStart(*[Create(t) for t in ticks17], lag_ratio=0.05), FadeIn(mid), FadeOut(p95q), run_time=3.0)
        mark = Triangle(color=YELLOW_M).set_fill(YELLOW_M, 1).scale(0.14).rotate(PI).next_to(line.n2p(0.01 + 0.015 * 15 / 17), UP, buff=0.05)
        est = T("0.01 + 15/17 of 0.015  =  about 0.023 s", 28, YELLOW_M).next_to(nl, DOWN, buff=0.35)
        self.beat("So the ninety fifth sits fifteen seventeenths of the way across. About twenty three milliseconds.",
                  ticks17[14].animate.set_color(YELLOW_M).scale(1.5), FadeIn(mark), Write(est), run_time=2.6)
        hq = T("histogram_quantile() makes this estimate: a p95", 26, GREY_B).next_to(est, DOWN, buff=0.2)
        self.beat("The function histogram quantile does exactly this, and that number is a p95: ninety five percent of requests took that long or less.", FadeIn(hq), run_time=2.4)
        self.beat("It is an estimate, and only as sharp as the boxes. Prometheus's own first box runs up to a tenth of a second, so its p95 came out at exactly point zero nine five.",
                  run_time=None)
        self.play(FadeOut(VGroup(bx, line, nl, ticks17, mid, mark, est, hq)), run_time=0.5)

        # ---------------- 8. moral, recap, check
        moral = T("A counter on its own says almost nothing. Ask for its rate.", 32, YELLOW_M).move_to(UP * 2.4)
        fit(moral, 12.6)
        self.beat("So the moral of the story. A counter on its own says almost nothing. Ask for its rate.", Write(moral), run_time=1.8)
        rec = VGroup(T("odometer to speed: last minus first, over the time", 28, TEAL_M),
                     T("a window too short answers with silence", 28, BLUE_M),
                     T("empty is not zero: or vector(0)", 28, GREY_B),
                     T("rate first, then add; buckets give an estimated p95", 28, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("Odometer to speed: last minus first, over the time. A window that is too short answers with silence. Empty is not zero. Rate first, then add. And the boxes give an estimated p95.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=7.0)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.5)
        c1 = T("Quick check: Prometheus scrapes every 15 seconds.", 30).move_to(UP * 0.7)
        c2 = T("Is rate(...[30s]) a safe window?", 30).next_to(c1, DOWN, buff=0.3)
        self.beat("A quick check. Prometheus scrapes every fifteen seconds. Is a thirty second window safe?", FadeIn(c1), FadeIn(c2), run_time=1.6)
        self.guess([0, -1.0, 0])
        ans = T("Too short: one failed scrape leaves one reading. Use 1 minute.", 30, GREEN_M).next_to(c2, DOWN, buff=0.6)
        fit(ans, 12.6)
        self.beat("Too short. It holds about two readings, so one failed scrape leaves only one. Four times fifteen seconds is one minute.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.2)
