import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import random

SAY.extend([
    (r"\$__rate_interval", "rate interval"), (r"\brate\(\)", "rate"), (r"\[1m\]", "one minute"), (r"(\d)%", r"\1 percent"),
    (r"\b3 a\.m\.", "three in the morning"), (r"\breq/s\b", "requests per second"), (r"\bvector\(0\)", "vector zero"),
    (r"\bLast \*", "Last star"),
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


class D53ReadableBoard(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("A board worth reading", "Grafana panels, units, thresholds and the step")

        # ---------------- 1. forty numbers in small handwriting
        random.seed(7)
        board = frame(10.6, 4.6, GREY_B, [0, 0.0, 0], fill=0.04)
        nums = VGroup()
        for i in range(40):
            if i % 3 == 0:
                s = f"{random.randint(97, 103)}.{random.randint(0, 9)} F"
            elif i % 3 == 1:
                s = f"{random.randint(36, 39)}.{random.randint(0, 9)} C"
            else:
                s = f"{random.randint(60, 130)}"
            nums.add(T(s, 20, GREY_B))
        nums.arrange_in_grid(5, 8, buff=(0.35, 0.35)).move_to(board)
        self.beat("Picture a doctor called to the ward at 3 a.m. On the wall hangs a board with forty numbers, in small handwriting.",
                  Create(board), LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.02), run_time=3.0)
        cf = VGroup(*[SurroundingRectangle(nums[i], color=GOLD_M, buff=0.05, stroke_width=2) for i in (0, 1, 9, 10)])
        self.beat("Some temperatures in Celsius, some in Fahrenheit, nothing circled. She has one minute to pick a patient.",
                  LaggedStart(*[Create(c) for c in cf], lag_ratio=0.3), run_time=3.0)
        self.beat("Every team builds that board by accident. Each number was added for a good reason. Nobody planned the whole.", FadeOut(cf), run_time=1.6)
        self.play(FadeOut(VGroup(board, nums)), run_time=0.5)

        # ---------------- 2. predict: where do the numbers live?
        q = T("A Grafana dashboard shows 7 days of request rates.", 30).move_to(UP * 2.3)
        q2 = T("Where do those numbers live?", 32, YELLOW_M).next_to(q, DOWN, buff=0.25)
        self.beat("Our version of that board is a dashboard, a web page of graphs drawn by a tool called Grafana. It shows seven days of request rates. Where do those numbers live?",
                  FadeIn(q), Write(q2), run_time=3.0)
        opts = VGroup(T("A. in Grafana's own database, copied every 15 seconds", 26), T("B. in Prometheus; each panel asks when the page loads", 26),
                      T("C. in the dashboard's file, saved with every panel", 26), T("D. in your browser's cache", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.5)
        self.play(LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3), run_time=1.6)
        self.guess([0, -2.8, 0])
        self.beat("Let's watch a page load, and see.", run_time=None)
        self.play(FadeOut(VGroup(q, q2, opts)), run_time=0.4)

        # ---------------- 3. the flow
        BR = np.array([-4.8, 0.4, 0]); GR = np.array([0.0, 0.4, 0]); PR = np.array([4.8, 0.4, 0])
        br = frame(2.8, 2.6, BLUE_M, BR, fill=0.06)
        br_t = T("your browser", 26, BLUE_M).next_to(br, UP, buff=0.15)
        gr = frame(2.8, 1.2, GOLD_M, GR, fill=0.14)
        gr_t = T("Grafana", 28).move_to(gr).set_z_index(2)
        gr_n = T("stores dashboards, not numbers", 22, GOLD_M).next_to(gr, DOWN, buff=0.2)
        pr = frame(2.8, 1.2, TEAL_M, PR, fill=0.14)
        pr_t = T("Prometheus", 28).move_to(pr).set_z_index(2)
        pr_n = T("the patient chart", 22, TEAL_M).next_to(pr, DOWN, buff=0.2)
        self.beat("Three players. Your browser, Grafana, and Prometheus, the tool that collects and stores the app's numbers.",
                  Create(br), FadeIn(br_t), GrowFromCenter(gr), Write(gr_t), GrowFromCenter(pr), Write(pr_t), run_time=2.4)
        a1 = Arrow(gr.get_left() + UP * 0.25, br.get_right() + UP * 0.25, buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.12)
        js = lchip("dashboard JSON", GOLD_M, 22).next_to(a1, UP, buff=0.12)
        panels = VGroup(*[Rectangle(width=1.0, height=0.7, stroke_color=BLUE_M, stroke_width=2) for _ in range(4)]).arrange_in_grid(2, 2, buff=0.15).move_to(BR + DOWN * 0.1)
        self.beat("First, the browser loads the dashboard from Grafana: a file listing the panels, the boxes on the page, and each one's query. No numbers.",
                  GrowArrow(a1), FadeIn(js), travel(a1, GOLD_M, 0.8), LaggedStart(*[Create(p) for p in panels], lag_ratio=0.2), run_time=3.2)
        a2 = Arrow(br.get_right() + DOWN * 0.3, gr.get_left() + DOWN * 0.3, buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        a3 = Arrow(gr.get_right(), pr.get_left(), buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        ql = T("query", 22, BLUE_M).next_to(a2, DOWN, buff=0.1)
        self.beat("Then each panel sends its query. Grafana passes it on to Prometheus.",
                  GrowArrow(a2), FadeIn(ql), GrowArrow(a3), Succession(travel(a2, BLUE_M, 0.6), travel(a3, BLUE_M, 0.6)), run_time=2.4)
        a4 = Arrow(pr.get_left() + DOWN * 0.45, gr.get_right() + DOWN * 0.45, buff=0.1, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.12)
        lines = VGroup(*[VMobject(stroke_color=TEAL_M, stroke_width=2).set_points_as_corners([p.get_corner(DL) + RIGHT * (0.1 + 0.2 * k) + UP * (0.15 + 0.3 * abs(np.sin(k + j))) for k in range(5)]) for j, p in enumerate(panels)])
        self.beat("Prometheus answers, and the browser draws the result.",
                  GrowArrow(a4), Succession(travel(a4, TEAL_M, 0.6), travel(a2.copy().rotate(PI), TEAL_M, 0.6)), LaggedStart(*[Create(l) for l in lines], lag_ratio=0.2), run_time=2.6)
        self.beat("So the answer is B. Grafana stores dashboards, users and settings, but the numbers stay in Prometheus. Grafana is the board. Prometheus is the patient chart behind it.",
                  FadeIn(gr_n), FadeIn(pr_n), run_time=3.0)
        cons = VGroup(T("never scraped: Grafana cannot show it", 24, GREY_B), T("Prometheus deletes old samples: that part of every graph goes empty", 24, GREY_B),
                      T("every refresh runs every query again", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([0, -2.6, 0])
        fit(cons, 12.4)
        self.beat("So Grafana cannot show what Prometheus never scraped, or what it already deleted, after seven days in the lab. And every refresh runs every query again.",
                  FadeIn(cons[0]), FadeIn(cons[1]), Succession(Wait(3.0), FadeIn(cons[2]), travel(a3, BLUE_M, 0.4), travel(a3, BLUE_M, 0.4)), run_time=5.6)
        self.play(FadeOut(VGroup(br, br_t, gr, gr_t, gr_n, pr, pr_t, pr_n, a1, js, panels, a2, a3, ql, a4, lines, cons)), run_time=0.6)

        # ---------------- 4. one panel, from raw counter to a readable number
        P = np.array([3.6, 0.2, 0])
        pan = frame(4.4, 3.4, BLUE_M, P, fill=0.06)
        pan_t = T("Rate", 26, BLUE_M).move_to(pan.get_top() + DOWN * 0.35)
        big = T("563", 72).move_to(P + DOWN * 0.2)
        qq = M('hello_responses_total{job="hello-devops"}', 24).move_to([-2.6, 1.8, 0])
        fit(qq, 6.6)
        self.beat("Now let's build one panel the doctor could read. Start from the raw counter of hello-devops, our tiny lab app. Five hundred and sixty three.",
                  Create(pan), FadeIn(pan_t), Write(qq), FadeIn(big), run_time=2.6)
        self.beat("That is the total since the app started. It only climbs.", Indicate(big, color=WHITE), run_time=1.8)
        qq2 = VGroup(M('sum by (status)', 24, YELLOW_M), M('(rate(hello_responses_total[1m]))', 24, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(qq)
        fit(qq2, 6.6)
        big2 = T("4.42", 72).move_to(big)
        self.beat("Wrap it in rate, and add the paths together. Now it reads four point four two.", ReplacementTransform(qq, qq2), ReplacementTransform(big, big2), run_time=2.0)
        qq, big = qq2, big2
        self.beat("Four point four two what? The panel does not know. Nobody reading it at 3 a.m. should have to guess.", Wiggle(big), run_time=1.8)
        unit = lchip("unit: requests/sec", GOLD_M, 24).move_to([-2.6, 0.6, 0])
        big3 = T("4.42 req/s", 54).move_to(big)
        self.beat("So set the panel's unit. The data does not change. Only how it is shown.", FadeIn(unit, shift=RIGHT * 0.2), ReplacementTransform(big, big3), run_time=2.0)
        big = big3
        exs = VGroup(T("0.0347  ->  3.47%", 26), T("0.231  ->  231 ms", 26), T("1610612736  ->  1.50 GiB", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([-2.6, -1.4, 0])
        self.beat("Prometheus stores base units: seconds, bytes, ratios between zero and one. The unit makes them human.",
                  LaggedStart(*[FadeIn(e, shift=RIGHT * 0.1) for e in exs], lag_ratio=0.5), run_time=3.4)
        rule0 = T("Keep the ratio in PromQL; set the unit in the panel.", 26, YELLOW_M).to_edge(DOWN, buff=0.55)
        self.beat("So never multiply by a hundred in your query to get a percentage. Keep the ratio, and set the unit.", FadeIn(rule0), run_time=1.8)
        self.play(FadeOut(VGroup(qq, unit, exs, rule0)), run_time=0.4)

        # ---------------- 5. the error ratio: no data, then thresholds
        pan2_t = T("Error ratio", 26, BLUE_M).move_to(pan_t)
        nd = T("No data", 56, GREY_B).move_to(big)
        eq = VGroup(M('sum(rate(...{status=~"5.."}[1m]))', 22), M('/ sum(rate(...[1m]))', 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-2.6, 1.9, 0])
        self.beat("Second panel, the error ratio. Nothing has failed yet. So what does it show? You might expect zero.",
                  ReplacementTransform(pan_t, pan2_t), ReplacementTransform(big, nd), FadeIn(eq), run_time=2.4)
        pan_t = pan2_t
        self.beat("Instead it says No data. The failure series does not exist yet, and a division with an empty side is empty.", Indicate(nd, color=GREY_B), run_time=2.0)
        fix = M("... or vector(0)", 24, GREEN_M).next_to(eq, DOWN, buff=0.3)
        z = T("0%", 72, GREEN_M).move_to(nd)
        self.beat("Add or vector zero to the error part, and the panel gets a real zero.", FadeIn(fix), ReplacementTransform(nd, z), run_time=1.8)
        big = z
        th = VGroup(lchip("below 1%: green", GREEN_M, 22), lchip("from 1%: orange", GOLD_M, 22), lchip("from 5%: red", RED_M, 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([-2.6, -1.2, 0])
        self.beat("Now the red zone, like the one on a car's rev counter. In Grafana it is called a threshold.",
                  run_time=None)
        self.beat("The lab's error ratio is green below one percent, orange from one percent, and red from five.",
                  LaggedStart(*[FadeIn(t, shift=RIGHT * 0.1) for t in th], lag_ratio=0.5), run_time=2.4)
        b2 = T("3.47%", 72, GOLD_M).move_to(big)
        self.beat("So a ratio of point zero three four seven shows as three point four seven percent, in orange. Nobody has to remember anything.",
                  ReplacementTransform(big, b2), pan.animate.set_stroke(GOLD_M), run_time=2.0)
        big = b2
        self.beat("Use color only for what someone should act on. If every panel is red or green all day, people stop seeing colors.",
                  run_time=None)
        self.play(FadeOut(VGroup(pan, pan_t, big, eq, fix, th)), run_time=0.5)

        # ---------------- 6. break it: the fixed range goes blind zoomed out
        tl = NumberLine(x_range=[0, 60, 10], length=11.6, include_numbers=False, stroke_color=GREY_B).move_to([0, -0.4, 0])
        tl_l = T("minutes", 22, GREY_B).next_to(tl, DOWN, buff=0.25).align_to(tl, RIGHT)
        sp_x = tl.n2p(34.5)
        spike = VGroup(Line(sp_x, sp_x + UP * 2.2, stroke_color=RED_M, stroke_width=6))
        sp_l = T("a 3-minute spike of errors", 24, RED_M).next_to(spike, UP, buff=0.15)
        self.beat("One more trap, and it hides until you zoom out. A graph panel asks for many points. The gap between two points is called the step, and Grafana picks it from the time range.",
                  Create(tl), FadeIn(tl_l), run_time=2.6)
        self.beat("Here is an hour, with a short spike of errors in the middle. My spike, for the example.", GrowFromEdge(spike, DOWN), FadeIn(sp_l), run_time=1.8)
        steps = [tl.n2p(x) for x in range(0, 61, 10)]
        pts = VGroup(*[Dot(p, radius=0.09, color=BLUE_M) for p in steps])
        wins = VGroup(*[Rectangle(width=tl.n2p(1)[0] - tl.n2p(0)[0], height=1.6, stroke_color=BLUE_M, stroke_width=2).set_fill(BLUE_M, 0.25).next_to(p, UP, buff=0).align_to(p, RIGHT) for p in steps[1:]])
        q1 = M("rate(...[1m])", 26, BLUE_M).to_edge(UP, buff=0.6)
        self.beat("Zoom out far, and the points land about ten minutes apart. Each point runs rate with a fixed window of one minute. Does the spike show up? Pause and guess.",
                  Write(q1), LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.1), LaggedStart(*[FadeIn(w) for w in wins], lag_ratio=0.1), run_time=3.6)
        self.wait(2.0)
        miss = T("each window sees 1 minute out of every 10: the spike falls in a gap", 24, RED_M).move_to([0, -1.5, 0])
        fit(miss, 12.4)
        self.beat("It falls in a gap. Each window sees one minute out of every ten, and the graph says all is well.",
                  FadeIn(miss), Indicate(spike, color=RED_M), run_time=3.0)
        q2 = M("rate(...[$__rate_interval])", 26, GREEN_M).move_to(q1)
        wide = VGroup(*[Rectangle(width=tl.n2p(10)[0] - tl.n2p(0)[0] + (tl.n2p(0.25)[0] - tl.n2p(0)[0]), height=1.6, stroke_color=GREEN_M, stroke_width=2).set_fill(GREEN_M, 0.18).next_to(p, UP, buff=0).align_to(p, RIGHT) for p in steps[1:]])
        self.beat("Grafana's helper, rate interval, grows with the step. It takes the step plus one scrape, or four scrapes, whichever is larger. Now every window touches the next one.",
                  ReplacementTransform(q1, q2), ReplacementTransform(wins, wide), FadeOut(miss), run_time=3.0)
        caught = T("the window that covers the spike sees it", 24, GREEN_M).move_to([0, -1.5, 0])
        self.beat("And the window that covers the spike sees it.", FadeIn(caught), Indicate(wide[3], color=GREEN_M), run_time=1.6)
        rule = T("A fixed range that looks fine zoomed in goes blind zoomed out.", 28, YELLOW_M).move_to([0, -2.6, 0])
        fit(rule, 12.4)
        self.beat("A fixed range that looks fine zoomed in goes blind zoomed out. Use rate interval in every rate.",
                  Write(rule), run_time=3.0)
        self.play(FadeOut(VGroup(tl, tl_l, spike, sp_l, pts, wide, q2, caught, rule)), run_time=0.6)

        # ---------------- 7. guardrails
        g = VGroup(T("pick the chart from the question: a line for change, a stat for now", 26),
                   T("a stat's Calculation: Last *, not a mean that hides an outage", 26),
                   T("layout for on-call: numbers on top, the same signals over time below", 26),
                   T("dashboards are JSON: keep them in git, with a fixed uid", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(DOWN * 0.1)
        fit(g, 12.4)
        gt = T("Guardrails", 32, GOLD_M).next_to(g, UP, buff=0.45).align_to(g, LEFT)
        self.beat("A few guardrails. Pick the chart from the question. A line for how it changes, one big number for right now.", Write(gt), FadeIn(g[0], shift=RIGHT * 0.1), run_time=2.0)
        self.beat("For a stat, use Last star, the last value that is not empty. A mean of seven days hides a ten minute outage.",
                  FadeIn(g[1], shift=RIGHT * 0.1), run_time=2.4)
        self.beat("Lay the page out for the tired reader: is it broken, since when, and where. Four numbers on top, the same signals over time below.", FadeIn(g[2], shift=RIGHT * 0.1), run_time=2.2)
        self.beat("And every dashboard is a JSON file underneath. Keep it in git, so nobody's late night edit quietly changes it.", FadeIn(g[3], shift=RIGHT * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(g, gt)), run_time=0.5)

        # ---------------- 8. moral, recap, check
        moral = T("Grafana draws. Prometheus remembers.", 38, YELLOW_M).move_to(UP * 2.4)
        self.beat("So the moral of the story. Grafana draws. Prometheus remembers.", Write(moral), run_time=1.6)
        rec = VGroup(T("every panel asks Prometheus again, on every load", 28, TEAL_M),
                     T("units and red zones make a number readable", 28, GOLD_M),
                     T("No data is not zero: or vector(0)", 28, GREY_B),
                     T("the window must grow with the step: $__rate_interval", 28, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("Every panel asks Prometheus again, on every load. Units and red zones make a number readable. No data is not zero. And the window must grow with the step.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=6.6)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.5)
        c1 = T("Quick check: Prometheus in the lab keeps samples for 7 days.", 30).move_to(UP * 0.7)
        c2 = T("You open a 30-day graph. What do the first 23 days show?", 30).next_to(c1, DOWN, buff=0.3)
        fit(c1, 12.6); fit(c2, 12.6)
        self.beat("A quick check. The lab's Prometheus keeps samples for seven days. You open a thirty day graph. What do the first twenty three days show?",
                  FadeIn(c1), FadeIn(c2), run_time=2.0)
        self.guess([0, -1.0, 0])
        ans = T("Nothing. Grafana keeps no copy of its own.", 30, GREEN_M).next_to(c2, DOWN, buff=0.6)
        self.beat("Nothing. Those samples are gone from Prometheus, and Grafana keeps no copy of its own.", FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.2)
