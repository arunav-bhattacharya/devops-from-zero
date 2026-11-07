import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

PX = -6.45                     # left edge of the text on the /metrics page
NAME = "hello_responses_total"
LABELS = ['{path="/",status="200"}', '{path="/healthz",status="200"}', '{path="/",status="500"}']
PAGE_Y = [1.4, 0.95, 0.5]      # the three metric lines on the page
ROW_Y = [-1.65, -2.3, -2.95]   # the three series in the table
COL_X = [-0.9, 1.15, 3.2, 5.25]
STAMPS = ["14:00:00", "14:00:15", "14:00:30", "14:00:45"]
SERIES = [99, 167, 235, 303]   # the lesson's samples for path="/", status="200"


def dark(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def top(m, z=2):
    m.set_z_index(z)
    return m


_CW = {}


def cw(size):
    """Width of one monospace character at this size (measured once)."""
    if size not in _CW:
        _CW[size] = M("x" * 40, size).width / 40
    return _CW[size]


def cl(text, y, size=20, color=WHITE, x=PX, center=None):
    """Monospace text on a shared baseline (an H sets it, then goes). Left edge at x, or centred on `center`."""
    m = M("H" + text, size, color)
    h = m[0]
    m.shift(np.array([x - cw(size) - h.get_left()[0], y - h.get_center()[1], 0]))
    m.remove(h)
    if center is not None:
        m.shift(RIGHT * (center - m.get_center()[0]))
    return top(m)


def part(line, full, piece):
    s, p = full.replace(" ", ""), piece.replace(" ", "")
    i = s.index(p)
    return line[i:i + len(p)]


def frame(w, h, color, c, fill=0.10, sw=3):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw)
    return r.set_fill(dark(color, fill), opacity=1).move_to(c)


def tween(tr, a, b, rt):
    return UpdateFromAlphaFunc(tr, lambda m, al: m.set_value(a + (b - a) * al), run_time=rt, rate_func=linear)


class D50Scrape(VoiceScene):
    def construct(self):
        self.title_card("How Prometheus collects metrics", "pull, sample, store")

        # ---------- 1. the app and its /metrics page
        app = box("hello-devops", TEAL_M, w=3.2, h=0.7, size=28).move_to([-5.15, 3.1, 0])
        page = frame(8.8, 2.5, TEAL_M, [-2.35, 1.35, 0], fill=0.07, sw=2.5)
        url = cl("web:8000/metrics", 2.3, 20, GREY_B)
        typ = cl("# TYPE hello_responses_total counter", 1.85, 20, GREY_B)
        full = [NAME + l for l in LABELS]
        lines = [cl(f, y, 20) for f, y in zip(full, PAGE_Y)]
        vx = [l.get_right()[0] + cw(20) for l in lines]
        vt = ValueTracker(61)
        val0 = always_redraw(lambda: cl(f"{int(round(vt.get_value()))}.0", PAGE_Y[0], 20, GREEN_M, vx[0]))
        val1 = cl("13.0", PAGE_Y[1], 20, GREEN_M, vx[1])
        val2 = cl("48.0", PAGE_Y[2], 20, GREEN_M, vx[2])
        self.beat("hello-devops already counts the requests it serves. It keeps the numbers in memory, and shows them on a plain web page, its metrics page.",
                  Succession(AnimationGroup(Create(app[0]), Write(app[1])), AnimationGroup(Create(page), FadeIn(url)),
                             AnimationGroup(FadeIn(typ), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in lines], lag_ratio=0.2), FadeIn(val0), FadeIn(val1), FadeIn(val2))),
                  run_time=4.5)
        self.beat("Each line is a metric name, then labels in braces, then the value right now.",
                  Succession(Indicate(part(lines[0], full[0], NAME), color=BLUE_M, scale_factor=1.06),
                             Indicate(part(lines[0], full[0], LABELS[0]), color=YELLOW_M, scale_factor=1.06),
                             Indicate(val0, color=GREEN_M, scale_factor=1.25)), run_time=4.0)
        self.beat("As requests come in, the number grows. But the page only shows the value right now. Nothing remembers what it was ten minutes ago.",
                  tween(vt, 61, 99, 6.0), run_time=6.0)

        # ---------- 2. Prometheus pulls
        prom = box("Prometheus", GOLD_M, w=2.5, h=0.9, size=28).move_to([5.3, 1.35, 0])
        self.beat("Prometheus is a server that collects these numbers every few seconds, and stores them with a timestamp.",
                  Create(prom[0]), Write(prom[1]), run_time=1.6)
        scr = Arrow(prom.get_left(), page.get_right() * [1, 0, 0] + [0, 1.35, 0], buff=0.08, stroke_width=4, color=GOLD_M, max_tip_length_to_length_ratio=0.12)
        get = top(M("GET /metrics", 20, GOLD_M).next_to(scr, UP, buff=0.12))
        tgt = T("target", 24, TEAL_M).next_to(app, RIGHT, buff=0.3)
        self.beat("It collects by pulling. On a timer, it fetches the page. One fetch is called a scrape, and the thing it scrapes is a target.",
                  Succession(AnimationGroup(GrowArrow(scr), FadeIn(get)), travel(scr, GOLD_M, run_time=0.9), FadeIn(tgt, shift=LEFT * 0.1)), run_time=4.5)
        every = top(T("every 15 s", 22, GREY_B).next_to(scr, DOWN, buff=0.12))
        self.beat("The lab scrapes every fifteen seconds. The default is one minute.",
                  FadeIn(every, shift=UP * 0.1), run_time=1.2)

        # ---------- 3. one time series per label set
        self.beat("Look at the metric hello_responses_total. One name, but three different sets of labels.",
                  LaggedStart(*[Indicate(part(l, f, lb), color=YELLOW_M, scale_factor=1.05) for l, f, lb in zip(lines, full, LABELS)], lag_ratio=0.3), run_time=3.0)

        tab = frame(13.4, 3.2, GOLD_M, [0, -1.95, 0], fill=0.05, sw=2)
        tab_t = T("stored in Prometheus", 22, GOLD_M).move_to([0, -0.62, 0]).align_to(tab, LEFT).shift(RIGHT * 0.3)
        store = Arrow(prom.get_bottom(), [prom.get_x(), tab.get_top()[1], 0], buff=0.06, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.25)
        name_h = cl(NAME, -1.1, 20, BLUE_M, -6.45)
        rows = [cl(l, y, 20, YELLOW_M, -6.45) for l, y in zip(LABELS, ROW_Y)]
        self.beat("Each label set is its own time series. A time series is the metric name, plus one exact set of label values.",
                  Succession(AnimationGroup(Create(tab), FadeIn(tab_t), GrowArrow(store)),
                             AnimationGroup(TransformFromCopy(part(lines[0], full[0], NAME), name_h),
                                            *[TransformFromCopy(part(l, f, lb), r) for l, f, lb, r in zip(lines, full, LABELS, rows)])), run_time=4.6)
        self.beat("Change any label value, and you have a different series. Here, that makes three.",
                  LaggedStart(*[Circumscribe(r, color=YELLOW_M, buff=0.08) for r in rows], lag_ratio=0.3), run_time=2.6)
        jobs = cl('+ job="hello-devops", instance="web:8000"', -0.62, 20, GREY_B, tab_t.get_right()[0] + 0.5)
        self.beat("Prometheus adds two labels of its own: job, the job name from its config, and instance, the target's address.",
                  Write(jobs), run_time=2.4)

        # ---------- 4. every scrape adds one sample to every series
        cells = [[None] * 4 for _ in range(3)]
        heads = [cl(s, -1.1, 20, GREY_B, center=x) for s, x in zip(STAMPS, COL_X)]

        def scrape(k, v0):
            vals = [v0, 13, 48]
            snaps = [cl(f"{v}.0", y, 20, GREEN_M, x) for v, y, x in zip(vals, PAGE_Y, vx)]
            for i in range(3):
                cells[i][k] = cl(f"{vals[i]}.0" if i else f"{v0}.0", ROW_Y[i], 20, WHITE, center=COL_X[k])
            return Succession(travel(scr, GOLD_M, run_time=0.7),
                              AnimationGroup(FadeIn(heads[k], shift=DOWN * 0.1),
                                             *[TransformFromCopy(sn, cells[i][k], path_arc=-0.4) for i, sn in enumerate(snaps)]), run_time=2.0)

        self.beat("Now watch a scrape. Each one adds one sample to every series: a timestamp, and a value.",
                  scrape(0, 99), run_time=3.0)
        self.beat("Fifteen seconds later, the counter has grown. Another scrape, another sample.",
                  Succession(tween(vt, 99, 167, 2.0), scrape(1, 167)), run_time=4.0)
        self.beat("And again, every fifteen seconds, for as long as Prometheus runs.",
                  Succession(tween(vt, 167, 235, 1.4), scrape(2, 235), tween(vt, 235, 303, 1.4), scrape(3, 303)), run_time=5.4)
        self.beat("Prometheus keeps only what the counter read at each scrape. Never the single requests in between.",
                  LaggedStart(*[Indicate(cells[0][k], color=YELLOW_M, scale_factor=1.2) for k in range(4)], lag_ratio=0.2), run_time=2.6)

        # ---------- 5. one series as a graph
        keep = VGroup(*cells[0])
        val0.clear_updaters()
        # take the kept cells out of the groups earlier animations left in the scene, so the fade below removes everything else
        self.remove(*keep)
        self.add(keep)
        others = Group(*[m for m in self.mobjects if m is not keep and not isinstance(m, ValueTracker)])
        self.play(FadeOut(others), keep.animate.shift(UP * 0.4), run_time=1.0)

        ax = Axes(x_range=[0, 120, 15], y_range=[0, 500, 100], x_length=10.8, y_length=4.4,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_tip": False, "tick_size": 0.06}).move_to([0.45, -0.55, 0])
        xl = VGroup(*[cl(f"14:0{t // 60}:{t % 60:02d}", ax.c2p(t, 0)[1] - 0.4, 20, GREY_B, center=ax.c2p(t, 0)[0]) for t in (0, 30, 60, 90, 120)])
        yl = VGroup(*[cl(str(v), ax.c2p(0, v)[1], 20, GREY_B, -5.45 - cw(20) * (len(str(v)) - 1)) for v in (0, 100, 200, 300, 400, 500)])
        title = cl(NAME + LABELS[0], 2.55, 22, WHITE, center=0.45)
        part(title, NAME + LABELS[0], LABELS[0]).set_color(YELLOW_M)
        pts = [(0, 99), (15, 167), (30, 235), (45, 303)]
        dots = VGroup(*[top(Dot(ax.c2p(t, v), radius=0.08, color=YELLOW_M), 3) for t, v in pts])
        self.beat("A graph of one series is just these samples, as points, joined by a line.",
                  Succession(AnimationGroup(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(title)),
                             AnimationGroup(*[ReplacementTransform(c, d) for c, d in zip(keep, dots)])), run_time=3.4)
        segs = VGroup(*[Line(ax.c2p(*a), ax.c2p(*b), stroke_width=3, color=TEAL_M) for a, b in zip(pts, pts[1:])])
        self.play(LaggedStart(*[Create(s) for s in segs], lag_ratio=0.5), run_time=1.2)

        # ---------- 6. a counter rises, and drops to zero on a restart
        more = [(60, 371), (75, 439)]
        after = [(90, 32), (105, 100), (120, 168)]
        d2 = VGroup(*[top(Dot(ax.c2p(t, v), radius=0.08, color=YELLOW_M), 3) for t, v in more])
        s2 = VGroup(*[Line(ax.c2p(*a), ax.c2p(*b), stroke_width=3, color=TEAL_M) for a, b in zip(pts[-1:] + more, more)])
        self.beat("This metric is a counter. A counter only goes up.",
                  LaggedStart(*[AnimationGroup(Create(s), GrowFromCenter(d)) for s, d in zip(s2, d2)], lag_ratio=0.6), run_time=2.4)
        rx = ax.c2p(83, 0)[0]
        rline = DashedLine([rx, ax.c2p(0, 0)[1], 0], [rx, ax.c2p(0, 500)[1], 0], dash_length=0.1, stroke_width=2, color=RED_M)
        rlab = top(T("restart", 22, RED_M).next_to(rline, UP, buff=0.1))
        d3 = VGroup(*[top(Dot(ax.c2p(t, v), radius=0.08, color=YELLOW_M), 3) for t, v in after])
        drop = Line(ax.c2p(*more[-1]), ax.c2p(*after[0]), stroke_width=3, color=RED_M)
        s3 = VGroup(*[Line(ax.c2p(*a), ax.c2p(*b), stroke_width=3, color=TEAL_M) for a, b in zip(after, after[1:])])
        self.beat("Or it drops to zero, when the process restarts. Then it starts counting up again.",
                  Succession(AnimationGroup(Create(rline), FadeIn(rlab)), AnimationGroup(Create(drop), GrowFromCenter(d3[0])),
                             LaggedStart(*[AnimationGroup(Create(s), GrowFromCenter(d)) for s, d in zip(s3, d3[1:])], lag_ratio=0.6)), run_time=4.4)

        # ---------- 7. why a raw counter needs rate()
        p303 = dots[3]
        lab303 = top(T("303", 26, YELLOW_M).next_to(p303, UP + LEFT * 0.4, buff=0.12))
        self.beat("So the raw value, like 303, only says how many since the process started. On its own, it tells you little.",
                  Succession(FadeIn(lab303, shift=DOWN * 0.1), Indicate(p303, color=YELLOW_M, scale_factor=1.8)), run_time=2.6)
        a, b = ax.c2p(0, 99), ax.c2p(45, 303)
        corner = np.array([b[0], a[1], 0])
        h1 = Line(a, corner, stroke_width=3, color=YELLOW_M)
        v1 = Line(corner, b, stroke_width=3, color=YELLOW_M)
        h1l = top(T("45 s", 22, YELLOW_M).next_to(h1, DOWN, buff=0.1))
        v1l = top(T("+204", 22, YELLOW_M).next_to(v1, RIGHT, buff=0.1))
        rate_c = chip("about 4.5 requests a second", YELLOW_M, 24).move_to([-2.55, 1.3, 0])
        self.beat("The useful number is how fast it grows. Here it grew by 204 in 45 seconds. That is about 4.5 requests a second.",
                  Succession(FadeOut(lab303), AnimationGroup(Create(h1), FadeIn(h1l)), AnimationGroup(Create(v1), FadeIn(v1l)),
                             FadeIn(rate_c, shift=UP * 0.1)), run_time=6.0)
        rate = chip("rate()", YELLOW_M, 34, mono=True).move_to([4.45, 1.3, 0])
        day = T("details on Day 51", 22, GREY_B).next_to(rate, DOWN, buff=0.15)
        a2, b2 = ax.c2p(90, 32), ax.c2p(120, 168)
        c2 = np.array([b2[0], a2[1], 0])
        h2 = Line(a2, c2, stroke_width=3, color=YELLOW_M)
        v2 = Line(c2, b2, stroke_width=3, color=YELLOW_M)
        h2l = top(T("30 s", 22, YELLOW_M).next_to(h2, UP, buff=0.1))
        v2l = top(T("+136", 22, YELLOW_M).next_to(v2, LEFT, buff=0.1).shift(DOWN * 0.2))
        self.beat("That is a rate. The PromQL function rate() works it out for every series, even across restarts. Day 51 shows how.",
                  Succession(GrowFromCenter(rate), AnimationGroup(Create(h2), FadeIn(h2l), Create(v2), FadeIn(v2l)), FadeIn(day)), run_time=5.5)

        # ---------- recap
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        flow = VGroup(chip("app shows /metrics", TEAL_M, 28), chip("Prometheus scrapes", GOLD_M, 28), chip("one sample per series", BLUE_M, 28))
        flow.arrange(RIGHT, buff=0.7).move_to(UP * 0.5)
        arrs = VGroup(*[arrow(flow[i].get_right(), flow[i + 1].get_left(), GREY_B, buff=0.1) for i in range(2)])
        sub = T("a counter is read through rate()", 30, YELLOW_M).next_to(flow, DOWN, buff=0.7)
        self.beat("The app shows its numbers. Prometheus pulls them on a timer, and stores one sample per series at every scrape. For a counter, you read how fast it grows.",
                  Succession(LaggedStart(*[FadeIn(f, shift=UP * 0.15) for f in flow], *[GrowArrow(a) for a in arrs], lag_ratio=0.3), FadeIn(sub, shift=UP * 0.1)), run_time=5.0)
        self.wait(1.0)
