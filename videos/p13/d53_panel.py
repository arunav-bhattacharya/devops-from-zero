import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\$__rate_interval", "rate interval"), (r"\{\{status\}\}", "status, in double braces"), (r"\btimeInterval\b", "time interval"),
    (r"\bscrape_interval\b", "scrape interval"), (r"\bprometheus\.yml\b", "prometheus dot yammel"), (r"\ballowUiUpdates\b", "allow U I updates"),
    (r"\bUI\b", "U I"), (r"\buid\b", "U I D"), (r"\bPostgreSQL\b", "postgres Q L"), (r"\bhello_responses_total\b", "hello responses total"),
])


def tint(color, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def panel(w, h, color=GREY_B, sw=2.5, a=0.08):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, a), 1)


def code_line(text, size=20, color=WHITE):
    t = M("|" + text, size, color)
    t[0].set_opacity(0)
    return t


def lines(spec, size=20, buff=0.14):
    return VGroup(*[code_line(t, size, c) for t, c in spec]).arrange(DOWN, aligned_edge=LEFT, buff=buff)


def flash(m, color=YELLOW_M, rt=1.2):
    return ShowPassingFlash(m.copy().set_fill(opacity=0).set_stroke(color, 6), time_width=0.6, run_time=rt)


def mover(text, color, a, b, rt=1.0, mono=True):
    """A small chip that rides along an arrow from a to b and then disappears."""
    c = chip(text, color, 20, mono=mono).move_to(a).set_z_index(5)
    return Succession(FadeIn(c, run_time=0.15), c.animate(run_time=rt, rate_func=smooth).move_to(b), FadeOut(c, run_time=0.2))


# graph area of the panel
GX0, GX1, GY0, GY1 = -5.5, 5.6, -2.55, 0.75
YS = (GY1 - GY0 - 0.3) / 5.0  # one request per second, in scene units


def gy(v):
    return GY0 + v * YS


def series_200(x):
    return 4.42 + 0.06 * np.sin(5 * x) if x < 2.2 else 0.02


class D53Panel(VoiceScene):
    def construct(self):
        self.title_card("How a Grafana panel works", "a data source, a query, a step, and the series that come back")

        # ---- 1. Grafana draws, Prometheus remembers
        gf = box("Grafana", GOLD_M, w=2.8, h=0.9, size=32).move_to([0, 1.7, 0])
        pr = box("Prometheus", RED_M, w=2.8, h=0.9, size=32).move_to([4.7, 1.7, 0])
        pr_sub = T("scrapes and stores the metrics", 22, GREY_B).next_to(pr, DOWN, buff=0.2)
        self.beat("Grafana is a web app for looking at data that lives somewhere else. In the lab, Prometheus scrapes and stores the metrics.",
                  FadeIn(gf), Succession(Wait(2.6), AnimationGroup(FadeIn(pr), FadeIn(pr_sub))), run_time=4.6)
        ask = Arrow(gf.get_right(), pr.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        askl = M("PromQL", 22, YELLOW_M).next_to(ask, UP, buff=0.12)
        gf_sub = VGroup(T("its own small database:", 22, GREY_B), T("dashboards, users, alert rules", 22, GREY_B)).arrange(DOWN, buff=0.08).next_to(gf, DOWN, buff=0.2)
        self.beat("Grafana asks Prometheus questions in PromQL, and draws the answers. Its own small database holds dashboards, users and alert rules. The numbers stay in Prometheus.",
                  GrowArrow(ask), FadeIn(askl), Succession(Wait(3.4), FadeIn(gf_sub, shift=UP * 0.1)), Succession(Wait(7.0), Indicate(pr_sub, color=RED_M)), run_time=8.4)
        self.play(travel(Line(ask.get_start(), ask.get_end()), YELLOW_M, 0.7), run_time=0.8)

        dss = VGroup(chip("Loki: logs", GREY_B, 22), chip("Tempo: traces", GREY_B, 22), chip("PostgreSQL", GREY_B, 22)).arrange(DOWN, buff=0.22).move_to([4.7, -1.35, 0])
        dsl = T("data sources", 26, GOLD_M).move_to([4.7, 0.45, 0])
        dsa = VGroup(*[Arrow(gf.get_corner(DR) + LEFT * 0.3, d.get_left(), buff=0.12, stroke_width=2, color=GREY_D, max_tip_length_to_length_ratio=0.08) for d in dss])
        self.beat("Each system Grafana can ask is a data source. One Grafana can talk to many at once: Prometheus for metrics, Loki for logs, Tempo for traces, and more.",
                  FadeOut(gf_sub), FadeOut(pr_sub), FadeIn(dsl), Succession(Wait(3.4), LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(d, shift=RIGHT * 0.1)) for a, d in zip(dsa, dss)], lag_ratio=0.35)),
                  run_time=7.6)
        self.play(FadeOut(VGroup(dss, dsa, dsl)), run_time=0.5)

        br = box("browser", BLUE_M, w=2.8, h=0.9, size=32).move_to([-4.7, 1.7, 0])
        gb = Arrow(br.get_right(), gf.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("Here is what happens when you open a dashboard. Your browser loads the dashboard's JSON from the Grafana server.",
                  FadeIn(br), GrowArrow(gb), Succession(Wait(2.6), mover("JSON", GOLD_M, gb.get_end(), gb.get_start(), 1.2)), run_time=5.0)
        prox = chip("access: proxy", GOLD_M, 20, mono=True).next_to(gf, DOWN, buff=0.35)
        self.beat("For each panel, the browser sends the panel's query to Grafana. Grafana passes it on to Prometheus. That is what access proxy means in the data source file.",
                  Succession(mover("query", YELLOW_M, gb.get_start(), gb.get_end(), 1.2), Wait(0.8), mover("query", YELLOW_M, ask.get_start(), ask.get_end(), 1.2)),
                  Succession(Wait(5.0), FadeIn(prox, shift=UP * 0.1)), run_time=7.4)
        mini = VGroup(Line([-5.9, -0.9, 0], [-3.5, -0.9, 0], stroke_width=2, color=GREY_B), Line([-5.9, -0.9, 0], [-5.9, 0.4, 0], stroke_width=2, color=GREY_B))
        curve = VMobject(stroke_color=GREEN_M, stroke_width=3).set_points_smoothly([[-5.8, -0.5, 0], [-5.2, -0.1, 0], [-4.6, -0.35, 0], [-4.1, 0.15, 0], [-3.6, -0.05, 0]])
        self.beat("Prometheus answers, and the browser draws the result.",
                  Succession(mover("series", GREEN_M, ask.get_end(), ask.get_start(), 0.9), mover("series", GREEN_M, gb.get_end(), gb.get_start(), 0.9),
                             AnimationGroup(Create(mini), Create(curve))), run_time=3.2)
        empty = T("an empty graph? usually a scrape or query problem", 26, GREY_B).move_to([0, -2.3, 0])
        self.beat("So Grafana can't show anything Prometheus never scraped. An empty graph is usually a scrape or query problem.",
                  FadeIn(empty, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(br, gb, gf, ask, askl, pr, prox, mini, curve, empty)), run_time=0.6)

        # ---- 2. one panel: a query, run over the time range at a step
        fr = panel(13.2, 6.6, GREY_B, 2, 0.04).move_to([0, -0.25, 0])
        title = T("Rate", 26).move_to(fr.get_corner(UL) + RIGHT * 0.55 + DOWN * 0.35)
        q = code_line("sum by (status) (rate(hello_responses_total[$__rate_interval]))", 22, YELLOW_M)
        q.next_to(title, DOWN, buff=0.25).align_to(title, LEFT)
        base = Line([GX0, GY0, 0], [GX1, GY0, 0], stroke_width=2, color=GREY_B)
        yax = Line([GX0, GY0, 0], [GX0, GY1, 0], stroke_width=2, color=GREY_B)
        t0 = M("now-30m", 20, GREY_B).next_to([GX0, GY0, 0], DOWN, buff=0.18)
        t1 = M("now", 20, GREY_B).next_to([GX1, GY0, 0], DOWN, buff=0.18)
        self.beat("A panel is one box on a dashboard: a query, and a visualization. This one is a time series graph.",
                  Create(fr), FadeIn(title), Succession(Wait(1.6), FadeIn(q, shift=RIGHT * 0.1)), Succession(Wait(3.4), AnimationGroup(Create(base), Create(yax), FadeIn(t0), FadeIn(t1))),
                  run_time=5.4)

        def sample_marks(n, color=YELLOW_M):
            xs = np.linspace(GX0 + 0.25, GX1, n)
            ticks = VGroup(*[Line([x, GY0, 0], [x, GY1, 0], stroke_width=1.2, color=GREY_D) for x in xs])
            dots = VGroup(*[Dot([x, GY0, 0], radius=0.06, color=color) for x in xs])
            return xs, ticks, dots

        xs, tks, dts = sample_marks(24)
        self.beat("A graph panel sends a range query. Prometheus runs the same PromQL once for each point, at evenly spaced times.",
                  Succession(Wait(2.0), LaggedStart(*[AnimationGroup(Create(t), FadeIn(d, scale=0.5)) for t, d in zip(tks, dts)], lag_ratio=0.25)), run_time=5.6)
        br_ = BraceBetweenPoints([xs[11], GY0 - 0.05, 0], [xs[12], GY0 - 0.05, 0], DOWN, buff=0.05, color=YELLOW_M)
        stl = T("step", 22, YELLOW_M).next_to(br_, DOWN, buff=0.08)
        st15 = M("step = 15s", 22, YELLOW_M).move_to([3.4, GY1 + 0.15, 0])
        self.beat("The gap between points is the step. Grafana picks it from the time range and the panel's width. On the lab's 30 minute graph, the step is 15 seconds.",
                  GrowFromCenter(br_), FadeIn(stl), Succession(Wait(6.0), FadeIn(st15, shift=DOWN * 0.1)), run_time=8.0)

        # 7 days: points far apart, a one-minute window misses the spikes
        xs7, tks7, dts7 = sample_marks(8)
        t07 = M("now-7d", 20, GREY_B).move_to(t0)
        st7 = M("step = many minutes", 22, YELLOW_M).move_to(st15)
        self.beat("Stretch the range to 7 days, and the points are many minutes apart.",
                  FadeOut(br_), FadeOut(stl), Transform(t0, t07), Transform(st15, st7), ReplacementTransform(tks, tks7), ReplacementTransform(dts, dts7), run_time=2.4)
        gap = xs7[1] - xs7[0]
        spikes = [xs7[1] + gap * 0.45, xs7[3] + gap * 0.55, xs7[5] + gap * 0.4]
        def raw(x):
            v = 0.9 + 0.15 * np.sin(3.1 * x)
            for s in spikes:
                v += 3.2 * np.exp(-((x - s) / 0.09) ** 2)
            return v
        rx = np.arange(GX0 + 0.25, GX1 + 0.001, 0.02)
        rawl = VMobject(stroke_color=GREY_B, stroke_width=2).set_points_as_corners([[x, gy(raw(x)), 0] for x in rx])
        rawlab = T("what really happened", 22, GREY_B).move_to([spikes[0] + 1.6, gy(3.7), 0])
        win1 = VGroup(*[Rectangle(width=gap * 0.1, height=GY1 - GY0, stroke_width=0).set_fill(TEAL_M, 0.45).move_to([x - gap * 0.05, (GY0 + GY1) / 2, 0]) for x in xs7])
        wl = M("[1m]", 22, TEAL_M).move_to([3.4, GY1 + 0.15, 0]).shift(LEFT * 3.6)
        self.beat("Say there are short spikes between the points. A one minute window then looks at one minute out of every ten, and misses the spikes in between.",
                  Create(rawl), FadeIn(rawlab), Succession(Wait(3.0), AnimationGroup(FadeIn(win1), FadeIn(wl))),
                  run_time=8.0)
        miss = VGroup(*[tick(False, 0.14).move_to([s, gy(raw(s)) + 0.3, 0]) for s in spikes])
        self.play(LaggedStart(*[Create(m) for m in miss], lag_ratio=0.3), run_time=1.0)

        def wrect(x, w):
            l = max(x - w, GX0 + 0.02)
            return Rectangle(width=x - l, height=GY1 - GY0, stroke_width=0).set_fill(TEAL_M, 0.22).move_to([(x + l) / 2, (GY0 + GY1) / 2, 0])
        win2 = VGroup(*[wrect(x, gap * 1.04) for x in xs7])
        wl2 = M("[$__rate_interval]", 22, TEAL_M).move_to(wl, aligned_edge=LEFT)
        rule = VGroup(T("the larger of", 22, GREY_B), M("step + 1 scrape", 22, TEAL_M), T("and", 22, GREY_B), M("4 scrapes", 22, TEAL_M)).arrange(RIGHT, buff=0.2)
        rule.move_to([0.6, GY1 + 0.62, 0]).align_to(q, LEFT)
        self.beat("$__rate_interval grows with the step. Grafana takes the larger of two values: the step plus one scrape interval, or four scrape intervals.",
                  ReplacementTransform(win1, win2), Transform(wl, wl2), FadeOut(miss), FadeOut(st15), Succession(Wait(3.0), FadeIn(rule, shift=DOWN * 0.1)), run_time=7.0)
        self.play(FadeOut(VGroup(rawl, rawlab, win2, wl, rule, tks7, dts7)), run_time=0.7)

        # the scrape interval must be known; what the 30-minute graph really ran
        t03 = M("now-30m", 20, GREY_B).move_to(t0)
        cfg = VGroup(VGroup(T("data source file", 22, GREY_B), M("timeInterval: 15s", 24, GOLD_M)).arrange(DOWN, buff=0.12),
                     T("=", 34, WHITE),
                     VGroup(M("prometheus.yml", 22, GREY_B), M("scrape_interval: 15s", 24, RED_M)).arrange(DOWN, buff=0.12)).arrange(RIGHT, buff=0.6).move_to([0, -0.4, 0])
        self.beat("That only works if Grafana knows the scrape interval. That is timeInterval 15s in the data source file, and it must match scrape_interval in prometheus.yml.",
                  Transform(t0, t03), FadeIn(cfg[0], shift=UP * 0.1), Succession(Wait(5.4), AnimationGroup(FadeIn(cfg[1]), FadeIn(cfg[2], shift=UP * 0.1))), run_time=8.4)
        ran = lines([("Expr: sum(rate(hello_responses_total[1m0s]))", WHITE), ("Step: 15s", WHITE)], 22, 0.12).move_to([0, -1.75, 0])
        self.beat("On the 30 minute graph, the range became one minute: four scrapes.",
                  FadeIn(ran, shift=UP * 0.1), Succession(Wait(2.4), flash(SurroundingRectangle(ran[0][-7:-3], buff=0.06), TEAL_M)), run_time=3.6)
        self.play(FadeOut(VGroup(cfg, ran)), run_time=0.5)

        # ---- 3. the series come back, and the panel draws them
        s200 = code_line('{status="200"}   4.42   4.38   4.45   ...   0.02', 22, GREEN_M)
        s500 = code_line('{status="500"}      no series yet       ...   0.24', 22, RED_M)
        sers = VGroup(s200, s500).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, -0.7, 0])
        self.beat("What comes back is a set of series: one per status, each a list of values over time.",
                  LaggedStart(FadeIn(s200, shift=DOWN * 0.1), FadeIn(s500, shift=DOWN * 0.1), lag_ratio=0.5), run_time=3.0)
        nos = T("before any request fails, the 500 series does not exist", 22, GREY_B).next_to(sers, DOWN, buff=0.3)
        self.beat("Before any request has failed, the 500 series does not exist at all. Here Redis was stopped near the end.",
                  FadeIn(nos), Indicate(s500, color=RED_M, scale_factor=1.03), run_time=3.4)
        X = np.arange(GX0 + 0.25, GX1 + 0.001, 0.05)
        l200 = VMobject(stroke_color=GREEN_M, stroke_width=4).set_points_as_corners([[x, gy(series_200(x)), 0] for x in X])
        X5 = np.arange(2.2, GX1 + 0.001, 0.05)
        l500 = VMobject(stroke_color=RED_M, stroke_width=4).set_points_as_corners([[x, gy(0.24), 0] for x in X5])
        yl = VGroup(*[M(str(v), 20, GREY_B).next_to([GX0, gy(v), 0], LEFT, buff=0.12) for v in (0, 2, 4)])
        self.beat("The panel draws each series as a line.",
                  FadeOut(nos), ReplacementTransform(s200, l200), ReplacementTransform(s500, l500), FadeIn(yl), run_time=2.4)
        leg = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.4, stroke_width=4, color=GREEN_M), M("200", 22)).arrange(RIGHT, buff=0.15),
                     VGroup(Line(ORIGIN, RIGHT * 0.4, stroke_width=4, color=RED_M), M("500", 22)).arrange(RIGHT, buff=0.15)).arrange(RIGHT, buff=0.5)
        leg.move_to([0, -3.15, 0])
        legf = VGroup(T("legend:", 22, GREY_B), M("{{status}}", 22, YELLOW_M)).arrange(RIGHT, buff=0.2).next_to(leg, LEFT, buff=0.8)
        self.beat("Write {{status}} in the legend field, and each line is named from its labels: 200, or 500.",
                  FadeIn(legf), Succession(Wait(2.6), FadeIn(leg, shift=UP * 0.1)), run_time=4.2)
        unit = VGroup(M("4.42", 22, GREY_B), M("->", 22, GREY_B), M("4.42 req/s", 22, GREEN_M)).arrange(RIGHT, buff=0.2).move_to([-2.4, gy(4.42) + 0.45, 0])
        self.beat("Settings change only the display. The unit turns 4.42 into 4.42 requests per second, and an override paints the 500 line red, whatever the palette says.",
                  FadeIn(unit, shift=DOWN * 0.1), Succession(Wait(4.4), flash(l500, RED_M)), run_time=6.4)
        self.play(FadeOut(unit), run_time=0.4)
        graph = VGroup(fr, title, q, base, yax, t0, t1, l200, l500, yl, leg, legf)

        # ---- 4. variables change the query
        self.play(FadeOut(graph), run_time=0.7)
        dj = VGroup(T("job", 24, GREY_B), chip("hello-devops", BLUE_M, 22, mono=True)).arrange(RIGHT, buff=0.2)
        dpth = VGroup(T("path", 24, GREY_B), chip("All", BLUE_M, 22, mono=True)).arrange(RIGHT, buff=0.2)
        bar = VGroup(dj, dpth).arrange(RIGHT, buff=0.8).to_edge(UP, buff=0.5).to_edge(LEFT, buff=0.6)
        sel = code_line('hello_responses_total{job=~"$job"}', 26, YELLOW_M).move_to([-2.6, 0.6, 0])
        self.beat("A dashboard variable is a dropdown at the top of the dashboard. Its value goes into every query that mentions it.",
                  FadeIn(dj, shift=DOWN * 0.1), Succession(Wait(2.8), FadeIn(sel, shift=RIGHT * 0.1)), run_time=5.0)
        lst = VGroup(M("hello-devops", 22, BLUE_M), T("... the same dashboard for 40 services", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        lst.next_to(dj[1], DOWN, buff=0.2).align_to(dj[1], LEFT)
        lbox = SurroundingRectangle(lst, buff=0.15, corner_radius=0.08, stroke_color=BLUE_M, stroke_width=2).set_fill(tint(BLUE_M, 0.1), 1)
        self.beat("job is a Query variable. Grafana asks Prometheus for every value of the job label. Today that is only hello-devops. With 40 services, the same dashboard would serve all 40.",
                  Succession(Wait(2.4), AnimationGroup(FadeIn(lbox), FadeIn(lst[0]))), Succession(Wait(7.0), FadeIn(lst[1])), run_time=9.4)
        self.play(FadeOut(VGroup(lbox, lst)), run_time=0.4)
        sel2 = code_line('hello_responses_total{job=~"$job", path=~"$path"}', 26, YELLOW_M).move_to(sel, aligned_edge=LEFT)
        self.beat("path depends on job. It lists the paths of the chosen job, allows several at once, and has an All option.",
                  FadeIn(dpth, shift=DOWN * 0.1), Transform(sel, sel2), run_time=3.0)
        multi = chip("/  +  /healthz", BLUE_M, 22, mono=True).move_to(dpth[1], aligned_edge=LEFT)
        sub = code_line('path=~"/|/healthz"', 26, TEAL_M)
        sub.shift(np.array([sel2[-14].get_left()[0] - sub[1].get_left()[0], sel2.get_y() - 1.25 - sub.get_y(), 0]))
        ap = sel2[-8:-1].get_bottom()
        arr = Arrow(ap, [ap[0], sub.get_top()[1], 0], buff=0.1, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        self.beat("With several values selected, Grafana inserts a regular expression, slash, pipe, slash healthz.",
                  Transform(dpth[1], multi), Succession(Wait(2.0), AnimationGroup(GrowArrow(arr), FadeIn(sub, shift=DOWN * 0.1))), run_time=4.6)
        ok = VGroup(M("=~", 30, TEAL_M), tick(True, 0.18)).arrange(RIGHT, buff=0.25)
        bad = VGroup(M("=", 30, RED_M), tick(False, 0.16)).arrange(RIGHT, buff=0.25)
        rules = VGroup(ok, bad).arrange(RIGHT, buff=1.0).move_to([-2.6, -2.0, 0])
        self.beat("So queries must match with equals tilde, not with equals. Forgetting this is the most common variable bug.",
                  FadeIn(rules, shift=UP * 0.1), flash(SurroundingRectangle(sel2[-10:-8], buff=0.08), TEAL_M), run_time=3.4)
        self.play(FadeOut(VGroup(bar, sel, sub, arr, rules)), run_time=0.6)

        # ---- 5. dashboards are JSON, provisioned from files
        js = lines([("{", WHITE), ('  "uid": "hello-red",', YELLOW_M), ('  "templating": { "list": [ job, path ] },', BLUE_M),
                    ('  "panels": [', WHITE), ('    { "type": "timeseries", "title": "Rate",', WHITE), ('      "targets": [ { "expr": "sum by (status) ..." } ] }', WHITE),
                    ("  ]", WHITE), ("}", WHITE)], 20, 0.1)
        jp = panel(js.width + 0.6, js.height + 0.45, GOLD_M, 2, 0.05)
        js.move_to(jp)
        jg = VGroup(jp, js).move_to([-2.3, 0.6, 0])
        jl = M("hello-red.json", 22, GOLD_M).next_to(jp, UP, buff=0.12).align_to(jp, LEFT)
        self.beat("Underneath, every dashboard is a JSON document. A uid, the variables, and the panels, each with its queries.",
                  FadeIn(jp), FadeIn(jl), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in js], lag_ratio=0.12),
                  Succession(Wait(3.4), flash(SurroundingRectangle(js[1], buff=0.06), YELLOW_M), flash(SurroundingRectangle(js[2], buff=0.06), BLUE_M), flash(SurroundingRectangle(js[4:6], buff=0.06), WHITE)),
                  run_time=6.4)
        url = VGroup(T("URL:", 22, GREY_B), M("/d/hello-red/...", 22, YELLOW_M)).arrange(RIGHT, buff=0.2).next_to(jp, DOWN, buff=0.3).align_to(jp, LEFT)
        self.beat("The uid is part of the URL. Keep it fixed, and links never break.",
                  FadeIn(url, shift=UP * 0.1), Indicate(js[1], color=YELLOW_M, scale_factor=1.03), run_time=2.8)

        tree = VGroup(*[code_line(s, 22, c) for s, c in (("provisioning/", GREY_B), ("  datasources/", RED_M), ("  dashboards/", GOLD_M), ("  alerting/", GREY_B))])
        tree.arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([4.0, 1.3, 0])
        tree.shift(RIGHT * (2.4 - tree.get_left()[0]))
        git = chip("git", PURPLE_M, 22, mono=True).next_to(jl, RIGHT, buff=0.35)
        self.beat("If the JSON is the dashboard, keep it in git, and review changes like code. Provisioning loads such files when Grafana starts, from its provisioning folder.",
                  FadeIn(git, shift=RIGHT * 0.1), Succession(Wait(3.6), LaggedStart(*[FadeIn(t, shift=LEFT * 0.1) for t in tree], lag_ratio=0.25)), run_time=7.4)
        prov = lines([("allowUiUpdates: false", YELLOW_M), ("updateIntervalSeconds: 30", YELLOW_M)], 22, 0.12).next_to(tree, DOWN, buff=0.5).align_to(tree, LEFT)
        self.beat("In the provider file, allowUiUpdates false makes the Save button refuse, because the file is the truth. And Grafana checks the folder for changed files every 30 seconds.",
                  Indicate(tree[2], color=GOLD_M, scale_factor=1.04), FadeIn(prov[0], shift=UP * 0.1), Succession(Wait(5.0), FadeIn(prov[1], shift=UP * 0.1)), run_time=8.0)
        self.play(FadeOut(VGroup(jg, jl, url, tree, git, prov)), run_time=0.6)

        # the everyday loop
        steps = ["change it in the UI", "export the JSON", "paste over the file", "commit, open a PR", "Grafana loads it"]
        cols = [BLUE_M, GOLD_M, GOLD_M, PURPLE_M, TEAL_M]
        c0, R = np.array([0, -0.15, 0]), 2.55
        nodes = VGroup(*[box(s, c, h=0.75, size=26).move_to(c0 + R * np.array([1.25 * np.cos(np.radians(90 - i * 72)), 0.92 * np.sin(np.radians(90 - i * 72)), 0])) for i, (s, c) in enumerate(zip(steps, cols))])
        arcs = VGroup(*[Arrow(nodes[i].get_center(), nodes[(i + 1) % 5].get_center(), buff=0.0, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.12) for i in range(5)])
        for i, a in enumerate(arcs):
            p, qq = ends(nodes[i], nodes[(i + 1) % 5])
            a.put_start_and_end_on(p + (qq - p) * 0.08, qq - (qq - p) * 0.08)
        self.beat("So the everyday loop is: change the dashboard in the UI until you like it, export its JSON, and paste it over the file. Commit, and open a pull request. Grafana picks up the file within 30 seconds.",
                  LaggedStart(*[AnimationGroup(FadeIn(n, shift=UP * 0.1), GrowArrow(a)) for n, a in zip(nodes, arcs)], lag_ratio=0.7), run_time=10.0)
        self.play(FadeOut(VGroup(nodes, arcs)), run_time=0.6)

        # ---- recap
        rec = VGroup(
            VGroup(T("data source", 30, GOLD_M), T("Grafana asks it; the numbers stay there", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("query", 30, YELLOW_M), T("run once per point, over the range, at the step", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("series", 30, GREEN_M), T("drawn as lines, named from their labels", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("variables", 30, BLUE_M), T("change every query that mentions them", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("provisioning", 30, TEAL_M), T("dashboards as JSON files in git", 26, GREY_B)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.42, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("Grafana stores dashboards, not data. Every panel sends its query through a data source, over the time range at a step, and draws the series that come back.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rec], lag_ratio=0.5), run_time=8.0)
        self.wait(1.0)
