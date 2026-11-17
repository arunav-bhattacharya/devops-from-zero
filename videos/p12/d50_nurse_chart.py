import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"/metrics\b", "slash metrics"), (r"/healthz\b", "slash health Z"), (r"/readyz\b", "slash ready Z"),
    (r"\bup = 0\b", "up equals zero"), (r"\bup = 1\b", "up equals one"), (r"\buser_id\b", "user ID"), (r"(\d)%", r"\1 percent"),
    (r"\b3 a\.m\.", "three in the morning"),
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


def person(color=GOLD_M, s=1.0):
    head = Circle(radius=0.16, stroke_color=color, stroke_width=3).set_fill(dark(color, 0.3), opacity=1)
    body = Arc(radius=0.3, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(head, DOWN, buff=0.04)
    return VGroup(head, body).scale(s)


class D50NurseChart(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("The nurse and the chart", "how Prometheus turns a page of numbers into history")

        # ---------------- 1. the ward at night
        bed = frame(3.0, 1.4, GREY_B, [-3.6, -0.3, 0], fill=0.05)
        bed_t = T("bed 4", 26, GREY_B).next_to(bed, DOWN, buff=0.2)
        scr = frame(2.6, 1.3, GREEN_M, [-3.6, 1.6, 0], fill=0.12)
        hr = T("heart 92", 26, GREEN_M).move_to(scr.get_center() + UP * 0.25)
        tp = T("temp 38.4", 26, GREEN_M).move_to(scr.get_center() + DOWN * 0.25)
        self.beat("Picture a hospital ward at night. Beside each bed, a small screen shows the patient's heart rate and temperature, right now.",
                  Create(bed), FadeIn(bed_t), Create(scr), FadeIn(hr), FadeIn(tp), run_time=2.6)
        doc = person(BLUE_M).move_to([1.0, 1.2, 0])
        dq = T("When did the fever start?", 28, BLUE_M).next_to(doc, RIGHT, buff=0.3)
        self.beat("At 3 a.m. a doctor asks a simple question. When did the fever in bed four start?",
                  FadeIn(doc, shift=LEFT * 0.2), Write(dq), run_time=2.0)
        now = T("only knows the present", 24, RED_M).next_to(scr, LEFT, buff=0.25).shift(DOWN * 0.0)
        now.next_to(scr, UP, buff=0.2)
        self.beat("The screen cannot say. It only knows the present.", FadeIn(now), Indicate(tp, color=RED_M), run_time=1.6)
        nurse = person(GOLD_M).move_to([-0.6, -0.4, 0])
        chart = frame(4.0, 2.2, GOLD_M, [3.6, -1.4, 0], fill=0.08)
        ch_t = T("chart", 26, GOLD_M).next_to(chart, UP, buff=0.15)
        rows = VGroup(*[M(f"{h}   bed 4   temp {v}", 22) for h, v in (("01:00", "37.1"), ("01:15", "37.6"), ("01:30", "38.4"))]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(chart)
        self.beat("So a nurse walks the ward every fifteen minutes, and writes every number on a chart, with the time and the bed.",
                  FadeIn(nurse, shift=RIGHT * 0.2), Create(chart), FadeIn(ch_t),
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows], lag_ratio=0.6), run_time=3.6)
        self.beat("Now the doctor has an answer. The fever started between one fifteen and one thirty.", Indicate(rows[2], color=GOLD_M), run_time=1.8)
        ward = VGroup(bed, bed_t, scr, hr, tp, doc, dq, now, nurse, chart, ch_t, rows)
        self.play(FadeOut(ward), run_time=0.6)

        # ---------------- 2. the app's screen: /metrics
        AC = np.array([-4.0, 0.6, 0])
        app = frame(4.7, 3.0, TEAL_M, AC, fill=0.06)
        app_t = T("hello-devops", 28, TEAL_M).move_to(app.get_top() + DOWN * 0.38)
        page_t = M("/metrics", 24, GREY_B).next_to(app_t, DOWN, buff=0.2)
        cnt = VGroup(M("hello_responses_total", 22), M('{path="/",status="200"}', 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(AC + DOWN * 0.3)
        val = M("99.0", 26, GREEN_M).next_to(cnt, DOWN, buff=0.2)
        self.beat("Our app has the same blind spot. hello-devops, the tiny lab app that greets every visitor, keeps a count of visits in memory.",
                  Create(app), Write(app_t), run_time=1.8)
        self.beat("It shows its counts on a plain web page, at slash metrics. Here, the answers to slash that went well. That page is the screen beside the bed.",
                  FadeIn(page_t), FadeIn(cnt), FadeIn(val), run_time=1.8)
        self.beat("It always shows the value right now. Nothing remembers what it was ten minutes ago.", Indicate(val, color=GREEN_M), run_time=1.4)

        # ---------------- 3. Prometheus, the nurse: scrape on a timer
        PC = np.array([0.55, 0.6, 0])
        prom = frame(2.6, 1.0, GOLD_M, PC, fill=0.16)
        prom_t = T("Prometheus", 28).move_to(prom).set_z_index(2)
        nurse = person(GOLD_M, 0.9).next_to(prom, UP, buff=0.15)
        self.beat("Prometheus is the nurse with the chart. It is a program that runs all the time, and collects numbers from your programs every few seconds.",
                  FadeIn(nurse, shift=DOWN * 0.2), GrowFromCenter(prom), Write(prom_t), run_time=2.2)
        get = Arrow(prom.get_left(), app.get_right(), buff=0.1, stroke_width=4, color=GOLD_M, max_tip_length_to_length_ratio=0.15)
        get_l = T("fetch, every 15 s", 22, GOLD_M).next_to(get, UP, buff=0.1)
        self.beat("It collects by pulling. It walks to the app and fetches the page, on a timer. In the lab, every fifteen seconds.",
                  GrowArrow(get), FadeIn(get_l), Succession(Wait(0.5), travel(get, GOLD_M, 0.8)), run_time=2.6)
        tg = T("one fetch: a scrape.  the app it visits: a target", 24, GREY_B).move_to([-2.0, -1.4, 0])
        self.beat("One fetch is called a scrape. The thing it scrapes is a target, one bed on the round.", FadeIn(tg), run_time=1.6)
        # chart on the right
        CHC = np.array([4.5, 0.6, 0])
        chart = frame(3.4, 3.0, GOLD_M, CHC, fill=0.06)
        chart_t = T("the chart", 26, GOLD_M).move_to(chart.get_top() + DOWN * 0.35)
        put = Arrow(prom.get_right(), chart.get_left(), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.15)
        samples = VGroup()
        self.beat("After each scrape, it writes the value down with a timestamp. That history is what you graph, and what you alert on.",
                  Create(chart), FadeIn(chart_t), GrowArrow(put), run_time=1.8)
        tsv = [("14:00:00", "99"), ("14:00:15", "167"), ("14:00:30", "235"), ("14:00:45", "303")]
        for i, (t, v) in enumerate(tsv):
            row = M(f"{t}   {v}", 22).move_to(CHC + UP * (0.45 - 0.42 * i))
            samples.add(row)
            nv = M(v + ".0", 26, GREEN_M).move_to(val)
            self.play(Transform(val, nv), travel(get, GOLD_M, 0.5), run_time=0.6)
            self.play(TransformFromCopy(val, row), run_time=0.5)
        self.beat("Four scrapes, one minute of history. Now we can see the past.", Indicate(samples, color=GOLD_M), run_time=1.4)
        self.play(FadeOut(tg), run_time=0.3)

        # ---------------- 4. predict: the app crashes
        self.beat("Now the app crashes, and stops answering. How does Prometheus find out?",
                  app.animate.set_stroke(RED_M), app_t.animate.set_color(RED_M), FadeOut(val), run_time=1.6)
        opts = VGroup(T("A. the app sends a last message", 24), T("B. its next scrape fails", 24), T("C. it does not notice", 24)).arrange(RIGHT, buff=0.6)
        opts.move_to([0, -1.8, 0]); fit(opts, 12.6)
        self.play(FadeIn(opts), run_time=0.5)
        self.guess([0, -2.7, 0])
        fail = tick(False, 0.3).move_to(get.get_center())
        upz = M("up = 0", 26, RED_M).move_to(CHC + UP * 0.45 - UP * 0.42 * 4 + DOWN * 0.08)
        self.beat("Its next scrape fails. And after every scrape, Prometheus records a value called up. One if the fetch worked. Zero if it failed.",
                  opts[1].animate.set_color(GREEN_M), travel(get, GOLD_M, 0.7), Create(fail), FadeIn(upz), run_time=3.0)
        self.beat("A nurse who finds an empty bed writes no reading on the chart. A patient who has left cannot phone in to say so.",
                  Indicate(upz, color=RED_M), run_time=2.0)
        self.beat("That is the big gift of pulling. Prometheus knows which targets should exist, so silence itself becomes a signal.",
                  run_time=None)
        self.play(FadeOut(VGroup(opts, fail, upz)), app.animate.set_stroke(TEAL_M), app_t.animate.set_color(TEAL_M), run_time=0.5)
        pull = VGroup(T("you can read the same page yourself, with curl", 24), T("a slow Prometheus never blocks your app", 24),
                      T("a 20-second batch job may finish before any scrape: the Pushgateway", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.1, 0])
        self.beat("Two more gifts. You can read the same page yourself with curl, the tool that fetches a web address. And a slow monitoring server never blocks your app.",
                  FadeIn(pull[0]), FadeIn(pull[1]), run_time=2.4)
        self.beat("Pushing still has a place. A batch job that runs for twenty seconds may finish before any scrape. For that, the docs describe the Pushgateway, where such jobs leave their result.",
                  FadeIn(pull[2]), run_time=2.4)
        self.play(FadeOut(VGroup(pull, samples, chart, chart_t, put)), run_time=0.5)

        # ---------------- 5. a time series is a name plus labels
        val = M("303.0", 26, GREEN_M)
        self.play(FadeOut(VGroup(cnt, nurse)), VGroup(prom, prom_t).animate.move_to([-4.3, -2.6, 0]),
                  FadeOut(get), FadeOut(get_l), FadeOut(VGroup(app, app_t, page_t)), run_time=0.6)
        lines = VGroup(M('hello_responses_total{path="/",status="200"}', 24),
                       M('hello_responses_total{path="/healthz",status="200"}', 24),
                       M('hello_responses_total{path="/",status="500"}', 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(UP * 1.6)
        fit(lines, 12.4)
        self.beat("A real page has more lines. Here is one metric, hello responses total, shown three times.",
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in lines], lag_ratio=0.4), run_time=2.4)
        lab = Underline(lines[0][21:], color=YELLOW_M)
        self.beat("The part in braces are labels: a name and a value, like path is slash, or status is 500. A label says which part of the app the number is about, like the bed number on a chart.",
                  Create(lab), run_time=2.6)
        self.play(FadeOut(lab), run_time=0.3)
        self.beat("Same name, three label sets. How many rows does the chart need? Pause and guess.", run_time=None)
        self.wait(2.0)
        grid = VGroup()
        cols_x = [1.6, 3.2, 4.8]
        for r in range(3):
            row = VGroup(*[Square(0.5, stroke_color=GOLD_M, stroke_width=2).set_fill(dark(GOLD_M, 0.2), 1).move_to([x, -0.4 - 0.75 * r, 0]) for x in cols_x])
            grid.add(row)
        rl = VGroup(*[T(t, 24, c).next_to(grid[i], LEFT, buff=0.4) for i, (t, c) in enumerate((("/ and 200", WHITE), ("/healthz and 200", WHITE), ("/ and 500", RED_M)))])
        three = T("3 time series", 30, YELLOW_M).move_to([-4.6, -1.15, 0])
        self.beat("Three rows. Each exact combination of name and label values gets its own row. Change any label value, and you have a different row.",
                  FadeIn(rl), LaggedStart(*[Create(r[0]) for r in grid], lag_ratio=0.3), run_time=2.6)
        self.beat("Each scrape adds one sample, a timestamp and a value, to every row.",
                  LaggedStart(*[Create(r[1]) for r in grid], lag_ratio=0.2), Succession(Wait(0.8), LaggedStart(*[Create(r[2]) for r in grid], lag_ratio=0.2)), run_time=2.4)
        self.beat("That row has a name now. A time series: a metric name, plus one exact set of label values.", Write(three), run_time=1.8)
        jl = T("Prometheus adds two labels itself: job and instance", 24, GREY_B).move_to([0.6, -2.85, 0])
        self.beat("Prometheus adds two labels of its own: job, the name from its config, and instance, the target's address.", FadeIn(jl), run_time=1.8)
        self.play(FadeOut(VGroup(jl, prom, prom_t)), run_time=0.4)

        # ---------------- 6. break it: one careless label
        self.beat("So far so good. Now let's break it, with one word. A label looks free. It is one extra word in your code.",
                  run_time=None)
        self.play(FadeOut(VGroup(lines, rl, three)), grid.animate.scale(0.6).move_to([-4.6, 1.6, 0]), run_time=0.6)
        cost = VGroup(T("one route of the app costs about 20 series", 28),
                      T("15 timing buckets, plus a sum, a count, and a counter or two", 24, GREY_B)).arrange(DOWN, buff=0.18).move_to([1.4, 2.2, 0])
        self.beat("Count what one route already costs. Its timing histogram has fifteen buckets, plus a sum and a count, and the counters add a few more.",
                  FadeIn(cost[0]), FadeIn(cost[1]), run_time=2.6)
        lab44 = T("in the lab: one request to /readyz took the hello series from 44 to 64", 26, GOLD_M).move_to([0.6, 1.0, 0])
        fit(lab44, 12.4)
        self.beat("In the lab, one single request to a route nobody had called before, slash ready Z, took the hello series from forty four to sixty four. Twenty new rows.",
                  FadeIn(lab44, shift=UP * 0.1), run_time=2.6)
        uid = M('user_id="..."', 26, RED_M).move_to([0.6, 0.1, 0])
        self.beat("Now someone adds a user ID label, to see requests per user. There are ten thousand users. How many series for one route?",
                  FadeIn(uid, scale=1.2), run_time=2.2)
        self.guess([0.6, -0.6, 0])
        dots = VGroup(*[Square(0.11, stroke_width=0).set_fill(RED_M, 0.85) for _ in range(40 * 12)]).arrange_in_grid(12, 40, buff=0.04)
        dots.move_to([0.6, -1.75, 0])
        n = T("20 x 10,000 = 200,000 series", 32, RED_M).move_to([0.6, -0.45, 0])
        self.beat("Twenty times ten thousand. Two hundred thousand series, for one route, from one copy of the app.",
                  Write(n), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.003), run_time=3.2)
        whole = T("the whole lab today: about 2,200 series", 26, GREEN_M).next_to(dots, DOWN, buff=0.25)
        self.beat("The whole lab, all four jobs, holds about two thousand two hundred. One careless label makes this app about ninety times bigger than everything Prometheus stores today.",
                  FadeIn(whole), run_time=2.6)
        self.beat("It is the hospital adding a chart row for every visitor. Nobody notices on day one. By the end of the month, the chart room is full and the nurse cannot finish a round.",
                  Wiggle(dots, scale_value=1.03), run_time=2.4)
        self.play(FadeOut(VGroup(cost, lab44, uid, dots, n, whole, grid)), run_time=0.6)

        # ---------------- 7. name it, and the guardrails
        nm = T("cardinality: how many series a metric creates", 32, YELLOW_M).to_edge(UP, buff=0.6)
        self.beat("That number has a name. Cardinality: how many time series a metric creates. Every new combination of label values is a new series.",
                  Write(nm), run_time=2.4)
        ok = VGroup(T("labels with small, fixed sets of values:", 26, GREEN_M), M("status   method   route pattern", 24, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        no = VGroup(T("never in labels:", 26, RED_M), M("user IDs   emails   request IDs   raw URLs", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        VGroup(ok, no).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([0, 0.5, 0])
        self.beat("Labels hold small, fixed sets of values: the status code, the method, the route pattern.", FadeIn(ok, shift=RIGHT * 0.1), run_time=1.6)
        self.beat("Never user IDs, email addresses, request IDs or raw URLs.", FadeIn(no, shift=RIGHT * 0.1), run_time=1.4)
        pat = T("the lab records the route pattern: /nope and /admin.php both become unmatched", 24, GREY_B).next_to(no, DOWN, buff=0.45).set_x(0)
        fit(pat, 12.4)
        self.beat("The lab records the route pattern, not the address typed. So slash nope and slash admin dot P H P both become one value: unmatched.",
                  FadeIn(pat), run_time=2.2)
        logs = T("details about single requests belong in logs and traces", 24, GREY_B).next_to(pat, DOWN, buff=0.25)
        self.beat("Details about one single request belong in logs and traces, later in the course. The guide's rule of thumb: keep most metrics under ten series, and look hard at anything that could pass a hundred.",
                  FadeIn(logs), run_time=2.4)
        self.play(FadeOut(VGroup(nm, ok, no, pat, logs)), run_time=0.5)
        lim = VGroup(T("One honest limit", 30, GOLD_M), T("one copy, on one machine's disk", 28), T("kept 15 days by default; the lab keeps 7", 28)).arrange(DOWN, buff=0.3)
        self.beat("And one honest limit. Prometheus keeps its chart on one machine's disk, in a single copy. Fifteen days by default. The lab keeps seven.",
                  LaggedStart(*[FadeIn(x) for x in lim], lag_ratio=0.5), run_time=2.6)
        self.play(FadeOut(lim), run_time=0.5)

        # ---------------- 8. moral and check
        moral = T("A label with no fixed list of values is a leak with a slow start.", 32, YELLOW_M).move_to(UP * 2.4)
        fit(moral, 12.6)
        self.beat("So the moral of the story. A label with no fixed list of values is a leak with a slow start.", Write(moral), run_time=2.0)
        rec = VGroup(T("the page shows now; the scrape writes history", 28, TEAL_M),
                     T("an empty bed is up = 0", 28, RED_M),
                     T("one row per name plus labels: a time series", 28, GOLD_M),
                     T("every new label value adds rows", 28, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("The page shows only now, and the nurse's rounds write the history. An empty bed is up equals zero. Every name plus labels is one row. And every new label value adds rows.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=7.0)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.5)
        c1 = T("Quick check: a counter has the label method (GET or POST)", 30).move_to(UP * 0.7)
        c2 = T("and the label path (/ or /healthz). At most how many series?", 30).next_to(c1, DOWN, buff=0.25)
        fit(c1, 12.6); fit(c2, 12.6)
        self.beat("A quick check. A counter has a label method, with two values, and a label path, with two values. At most, how many series?",
                  FadeIn(c1), FadeIn(c2), run_time=1.8)
        self.guess([0, -1.0, 0])
        ans = T("Four: every combination is its own row.", 30, GREEN_M).next_to(c2, DOWN, buff=0.6)
        self.beat("Four. Two times two. Every combination is its own row.", FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.2)
