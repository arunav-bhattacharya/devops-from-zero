import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bhistogram_quantile\b", "histogram quantile"), (r"\bp95\b", "P ninety-five"), (r"\ble\b", "L E"),
    (r"\[10s\]", "ten seconds"), (r"\[5m\]", "five minutes"), (r"(?<=\s)/(?=[\s,.]|$)", "slash"), (r"(\d)%", r"\1 percent"),
    (r"\brate\(\)", "rate"),
])

Q1 = 'histogram_quantile(0.95, sum by (le) ('
Q2 = 'rate(hello_request_duration_seconds_bucket{path="/"}[5m])))'
LES = ["0.005", "0.01", "0.025", "0.05"]
NOW = [36000, 72000, 87300, 90000]          # each bucket's total at "now"
STEP = [600, 1200, 1455, 1500]              # growth per 15 s scrape: 40, 80, 97, 100 per second
RATES = [40, 80, 97, 100]
CX = [-0.9, 1.15, 3.2, 5.25]                # table columns
ROWS = [("-285s", 19), ("...", None), ("-30s", 2), ("-15s", 1), ("now", 0)]
RY = [1.15, 0.62, 0.09, -0.44, -0.97]


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def part(line, full, piece):
    s, p = full.replace(" ", ""), piece.replace(" ", "")
    i = s.index(p)
    return line[i:i + len(p)]


def hl(m, color=YELLOW_M):
    return SurroundingRectangle(m, buff=0.06, corner_radius=0.05, stroke_color=color, stroke_width=2.5)


class D51Quantile(VoiceScene):
    def construct(self):
        self.title_card("A p95 latency query, inside out", "select, range, rate, sum by le, then the quantile")

        # ---- 0. the question
        q1, q2 = M(Q1, 20, GREY_B), M(Q2, 20, GREY_B)
        q = VGroup(q1, q2).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        q2.shift(RIGHT * 2 * M("x" * 40, 20).width / 40)
        q.move_to([0, 3.25, 0])
        p95 = VGroup(T("p95 = 200 ms", 34, YELLOW_M), T("95% of requests took 200 ms or less", 28, GREY_B)).arrange(DOWN, buff=0.3).move_to([0, 0.6, 0])
        self.beat("How long do requests to / take? An average hides the slow ones. So teams ask for a percentile, such as the p95.",
                  FadeIn(p95[0], shift=UP * 0.1), run_time=2.0)
        self.beat("A p95 of 200 milliseconds means 95% of requests took 200 milliseconds or less.",
                  FadeIn(p95[1], shift=UP * 0.1), run_time=1.6)
        self.beat("In PromQL, the p95 for hello-devops is this one line. It looks scary. Read it from the inside out.",
                  FadeOut(p95), Write(q), run_time=3.0)

        # the five steps, as a column on the left
        names = [("selector", BLUE_M), ("range [5m]", TEAL_M), ("rate()", GREEN_M), ("sum by (le)", GOLD_M), ("histogram_quantile", PURPLE_M)]
        steps = VGroup(*[mbox(n, c, w=3.3, h=0.62, size=22) for n, c in names]).arrange(DOWN, buff=0.55).move_to([-5.0, -0.25, 0])
        sarr = VGroup(*[Arrow(steps[i].get_bottom(), steps[i + 1].get_top(), buff=0.06, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.3) for i in range(4)])
        pieces = ['hello_request_duration_seconds_bucket{path="/"}', '[5m]', 'rate(', 'sum by (le)', 'histogram_quantile(0.95,']
        self.beat("There are five steps. Each one takes the output of the one before.",
                  LaggedStart(*[AnimationGroup(FadeIn(s, shift=RIGHT * 0.1), *( [GrowArrow(sarr[i])] if i < 4 else [])) for i, s in enumerate(steps)], lag_ratio=0.35), run_time=3.4)

        def light(i, on=True):
            return steps[i][0].animate.set_stroke(width=6 if on else 3)

        def qpart(i, color):
            line, full = (q1, Q1) if i >= 3 else (q2, Q2)
            return part(line, full, pieces[i]).animate.set_color(color)

        # ---- 1. selector: one series per bucket
        heads = VGroup(*[M(f'le="{v}"', 20, BLUE_M).move_to([x, 2.15, 0]) for v, x in zip(LES, CX)])
        dots = M("...", 22, GREY_B).move_to([6.35, 2.15, 0])
        hist = T("each bucket is a counter: requests that took this long or less", 24, GREY_B).move_to([2.2, 2.6, 0])
        self.beat("Latency lives in a histogram. Each bucket is a counter, and its le label is a limit, in seconds.",
                  light(0), qpart(0, BLUE_M), LaggedStart(*[FadeIn(h, shift=DOWN * 0.1) for h in heads], lag_ratio=0.2), FadeIn(dots), run_time=3.0)
        self.beat("The selector picks every bucket series for path /. One series per bucket, so one column per series.",
                  FadeIn(hist), run_time=2.0)

        tlab = VGroup(*[M(r, 20, GREY_B).move_to([-2.35, y, 0]) for (r, _), y in zip(ROWS, RY)])
        cells = VGroup()
        for (r, back), y in zip(ROWS, RY):
            row = VGroup(*[M(f"{n - back * s}" if back is not None else "...", 20, WHITE if back is not None else GREY_B).move_to([x, y, 0]) for n, s, x in zip(NOW, STEP, CX)])
            cells.add(row)
        sep = Line([-2.95, 1.75, 0], [6.55, 1.75, 0], stroke_width=1.5, color=GREY_D)
        self.beat("Every 15 seconds, each scrape adds one row: every counter's total since the process started.",
                  FadeOut(hist), Create(sep), LaggedStart(*[AnimationGroup(FadeIn(t), FadeIn(c, shift=DOWN * 0.08)) for t, c in zip(tlab, cells)], lag_ratio=0.35), run_time=4.0)

        # ---- 2. the range
        win = Rectangle(width=9.5, height=RY[0] - RY[-1] + 0.5, stroke_color=TEAL_M, stroke_width=2.5).set_fill(TEAL_M, 0.07)
        win.move_to([1.8, (RY[0] + RY[-1]) / 2, 0])
        wl = T("the last 5 minutes: 20 samples per series", 24, TEAL_M).move_to([1.8, -1.75, 0])
        self.beat("Step two, the range in square brackets. [5m] keeps every sample from the last 5 minutes. At a 15 second scrape, that is 20 samples per series.",
                  light(0, False), light(1), qpart(1, TEAL_M), FadeIn(win), Succession(Wait(3.0), FadeIn(wl, shift=UP * 0.1)), run_time=5.0)
        win10 = Rectangle(width=9.5, height=0.42, stroke_color=RED_M, stroke_width=2.5).set_fill(RED_M, 0.07).move_to([1.8, RY[-1], 0])
        wl10 = T("[10s]: only one sample. rate() needs two, so: empty", 24, RED_M).move_to(wl)
        self.beat("Make the range too short, and it fails quietly. [10s] holds only one sample, and rate needs at least two. The series just drops out of the result. No error.",
                  Transform(win, win10), Transform(wl, wl10), Succession(Wait(3.6), cells[:4].animate.set_opacity(0.25)), run_time=5.6)
        win5 = Rectangle(width=9.5, height=RY[0] - RY[-1] + 0.5, stroke_color=TEAL_M, stroke_width=2.5).set_fill(TEAL_M, 0.07).move_to([1.8, (RY[0] + RY[-1]) / 2, 0])
        wl5 = T("use at least 4 times the scrape interval", 24, TEAL_M).move_to(wl)
        self.beat("So use at least 4 times the scrape interval. Then a failed scrape still leaves enough samples.",
                  Transform(win, win5), Transform(wl, wl5), cells[:4].animate.set_opacity(1), run_time=2.4)

        # ---- 3. rate()
        calc = VGroup(M("(72000 - 49200) / 285 s", 22, GREEN_M), M("= 80 per second", 22, GREEN_M)).arrange(RIGHT, buff=0.3).move_to([1.8, -1.75, 0])
        self.beat("Step three, rate. Roughly, it subtracts the first sample in the window from the last, and divides by the seconds between them.",
                  light(1, False), light(2), qpart(2, GREEN_M), FadeOut(wl),
                  Succession(Wait(2.2), AnimationGroup(Indicate(cells[0][1], color=GREEN_M), Indicate(cells[4][1], color=GREEN_M))),
                  Succession(Wait(4.0), FadeIn(calc, shift=UP * 0.1)), run_time=6.4)
        rrow = VGroup(*[M(str(r), 28, GREEN_M).move_to([x, 0.1, 0]) for r, x in zip(RATES, CX)])
        rlab = T("requests per second that took this long or less", 24, GREEN_M).move_to([1.8, -0.75, 0])
        self.beat("Each column collapses to one number. Each bucket now reads: requests per second that took this long or less.",
                  FadeOut(win), FadeOut(calc), FadeOut(tlab),
                  *[ReplacementTransform(VGroup(*[cells[k][i] for k in range(5)]), rrow[i]) for i in range(4)],
                  Succession(Wait(2.4), FadeIn(rlab, shift=UP * 0.1)), run_time=4.4)
        ex = T("say 100 requests a second arrive", 24, GREY_B).move_to([1.8, -1.45, 0])
        self.beat("Say 100 requests a second arrive. 80 of them finished within 0.01 seconds, and 97 within 0.025.",
                  FadeIn(ex), Succession(Wait(2.4), Indicate(rrow[1], color=GREEN_M)), Succession(Wait(4.4), Indicate(rrow[2], color=GREEN_M)), run_time=6.0)

        # ---- 4. sum by (le)
        keep = VGroup(*[hl(h, GOLD_M) for h in heads])
        sl = T("adds up paths and instances, keeps le", 24, GOLD_M).move_to(ex)
        self.beat("Step four, sum by le. It adds up paths and instances, bucket by bucket, and keeps le, the bucket limits.",
                  light(2, False), light(3), qpart(3, GOLD_M), FadeOut(ex), FadeIn(sl), Succession(Wait(3.6), LaggedStart(*[Create(k) for k in keep], lag_ratio=0.2)), run_time=6.0)
        nole = VGroup(M("sum (...)", 22, RED_M), T("without le: empty, the limits are gone", 24, RED_M)).arrange(RIGHT, buff=0.3).move_to([1.8, -2.25, 0])
        self.beat("Drop le, and the result is empty, because the last step needs those limits.",
                  FadeIn(nole, shift=UP * 0.1), run_time=1.8)
        avg = T("never average percentiles: sum the buckets, then compute once", 24, YELLOW_M).move_to(nole)
        self.beat("This is also why you never average percentiles from several servers. Sum the buckets first, then compute the percentile once.",
                  Transform(nole, avg), run_time=1.8)
        self.play(FadeOut(VGroup(keep, nole, sl, rlab, sep, dots)), run_time=0.6)

        # ---- 5. histogram_quantile: bars, the 95 line, and the even spread
        B0, SC = -1.2, 3.0 / 100
        bars = VGroup(*[Rectangle(width=1.1, height=r * SC, stroke_color=PURPLE_M, stroke_width=2.5).set_fill(tint(PURPLE_M, 0.45), 1)
                        .move_to([x, B0 + r * SC / 2, 0]) for r, x in zip(RATES, CX)])
        base = Line([-2.0, B0, 0], [6.4, B0, 0], stroke_width=2, color=GREY_B)
        self.beat("Step five, histogram_quantile, with 0.95. Draw each bucket as a bar.",
                  light(3, False), light(4), qpart(4, PURPLE_M), Create(base),
                  *[ReplacementTransform(rrow[i], bars[i]) for i in range(4)], heads.animate.move_to([heads.get_x(), B0 - 0.3, 0]), run_time=3.0)
        vals = VGroup(*[M(str(r), 22, WHITE).move_to(b.get_top() + DOWN * 0.32) for r, b in zip(RATES, bars)])
        line95 = DashedLine([-2.0, B0 + 95 * SC, 0], [6.4, B0 + 95 * SC, 0], dash_length=0.1, stroke_width=2.5, color=YELLOW_M)
        l95 = T("95% of 100 = 95", 24, YELLOW_M).move_to([-0.9, B0 + 95 * SC + 0.45, 0])
        self.add(vals)
        self.beat("95% of 100 is 95. Draw that line.",
                  FadeIn(vals), Create(line95), FadeIn(l95), run_time=2.0)
        self.beat("The 0.01 bucket holds 80, below the line. The 0.025 bucket holds 97, above it. So the 95th request is somewhere between 0.01 and 0.025 seconds.",
                  Succession(Wait(0.6), Indicate(bars[1], color=PURPLE_M, scale_factor=1.04), Wait(1.8), Indicate(bars[2], color=YELLOW_M, scale_factor=1.04)), run_time=6.2)

        # the bucket between 0.01 and 0.025, spread evenly
        NL0, NL1, NY = -1.4, 5.6, -2.7
        nl = Line([NL0, NY, 0], [NL1, NY, 0], stroke_width=2.5, color=GREY_B)
        e0 = M("0.01 s", 20, GREY_B).next_to([NL0, NY, 0], DOWN, buff=0.15)
        e1 = M("0.025 s", 20, GREY_B).next_to([NL1, NY, 0], DOWN, buff=0.15)
        held = T("17 requests in this bucket: 97 - 80", 24, PURPLE_M).move_to([2.1, NY + 0.6, 0])
        self.beat("That bucket holds 17 requests, 97 minus 80. Prometheus does not know their exact times.",
                  Create(nl), FadeIn(e0), FadeIn(e1), FadeIn(held, shift=UP * 0.1), run_time=2.6)
        pts = VGroup(*[Dot([NL0 + (NL1 - NL0) * k / 17, NY, 0], radius=0.07, color=PURPLE_M) for k in range(1, 18)])
        self.beat("So it assumes they are spread evenly across the bucket.",
                  LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.12), run_time=2.4)
        x15 = NL0 + (NL1 - NL0) * 15 / 17
        mark = VGroup(Line([x15, NY - 0.05, 0], [x15, NY + 0.32, 0], stroke_width=3, color=YELLOW_M))
        self.beat("The 95th request is the 15th of those 17.",
                  FadeOut(held), LaggedStart(*[Indicate(p, color=YELLOW_M, scale_factor=1.6) for p in pts[:15]], lag_ratio=0.15),
                  Succession(Wait(2.0), AnimationGroup(pts[14].animate.set_color(YELLOW_M).scale(1.5), Create(mark))), run_time=3.0)
        ans = VGroup(M("0.01 + 15/17 x 0.015", 24, YELLOW_M), M("= about 0.023 s", 24, YELLOW_M)).arrange(RIGHT, buff=0.3).move_to([2.1, NY + 0.62, 0])
        self.beat("So the answer is 0.01, plus 15 seventeenths of the bucket's 0.015 second width. About 0.023 seconds.",
                  FadeIn(ans[0], shift=UP * 0.1), Succession(Wait(4.0), FadeIn(ans[1], shift=UP * 0.1)), run_time=6.0)

        # ---- 6. an estimate, only as good as the buckets
        self.play(FadeOut(VGroup(bars, vals, line95, l95, base, heads, nl, e0, e1, pts, mark, ans)), run_time=0.7)
        est = T("an estimate, only as precise as the buckets", 30, YELLOW_M).move_to([1.8, 2.0, 0])
        cA = VGroup(T("Prometheus's own API: a few ms", 24), T("first bucket 0 to 0.1 s", 24, GREY_B), M("p95 = 0.095", 24, PURPLE_M)).arrange(DOWN, buff=0.2)
        cB = VGroup(T("hello-devops, Redis outage", 24), T("bucket 5 to 7.5 s", 24, GREY_B), M("p95 = 6.12 s", 24, PURPLE_M)).arrange(DOWN, buff=0.2)
        cards = VGroup(cA, cB).arrange(RIGHT, buff=1.0).move_to([1.8, 0.2, 0])
        self.beat("So the answer is always an estimate. Both of these happened in the lab.",
                  FadeIn(est, shift=DOWN * 0.1), run_time=1.8)
        self.beat("Prometheus's own query API answered in a few milliseconds. But its first bucket is 0 to 0.1 seconds, so the p95 came out at exactly 0.095.",
                  FadeIn(cA[0]), Succession(Wait(3.0), FadeIn(cA[1])), Succession(Wait(5.6), FadeIn(cA[2], shift=UP * 0.1)), run_time=7.6)
        self.beat("During a Redis outage, hello-devops's p95 read 6.12 seconds: somewhere in the 5 to 7.5 second bucket.",
                  FadeIn(cB[0]), Succession(Wait(2.4), FadeIn(cB[2], shift=UP * 0.1)), Succession(Wait(3.8), FadeIn(cB[1])), run_time=6.0)
        tip = T("so put bucket limits near the latencies you care about", 26, GREY_B).move_to([1.8, -1.9, 0])
        self.beat("So choose bucket limits around the latencies you care about.",
                  FadeIn(tip, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(est, cards, tip)), run_time=0.6)

        # ---- recap
        rec = VGroup(T("select the buckets, take a range, rate,", 30), T("sum by le, then estimate the quantile", 30, PURPLE_M)).arrange(DOWN, buff=0.25).move_to([1.8, 0.2, 0])
        self.beat("A p95 query, inside out: select the buckets, take a range, rate, sum by le, then estimate the quantile.",
                  light(4, False), LaggedStart(*[Indicate(s, color=s[0].get_stroke_color(), scale_factor=1.06) for s in steps], lag_ratio=0.3),
                  FadeIn(rec, shift=UP * 0.1), run_time=5.0)
        self.wait(1.2)
