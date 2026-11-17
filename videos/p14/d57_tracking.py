import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\btraceparent\b", "trace parent"), (r"\bINCRBY\b", "increment by"), (r"\bGET /", "get slash"),
            (r"\bJaeger\b", "yay-ger"), (r"\bW3C\b", "W three C"), (r"\bp95\b", "p 95")])

SVC_C = BLUE_M      # services / depots
SPAN_C = TEAL_M     # spans (bars)
SLOW_C = RED_M      # the slow step
ID_C = YELLOW_M     # trace id / tracking number
PAR_C = PURPLE_M    # parent span id
ASK_C = GOLD_M      # questions


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


class D57Tracking(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("Where did the time go?", "a tracking number for every request")

        # ---------- 1. the question
        acc = M('{"path":"/","status":200,"duration_ms":835}', 24).move_to(UP * 1.8)
        dash = VGroup(T("error rate", 28, GREY_B), T("0%", 40, GREEN_M)).arrange(RIGHT, buff=0.4).move_to(UP * 0.4)
        self.beat("One visit to our lab app, hello-devops, took 835 milliseconds. Its log line says status 200, success. The dashboard says the error rate is zero percent.",
                  FadeIn(acc, shift=DOWN * 0.1), Succession(Wait(3.6), FadeIn(dash)), run_time=5.0)
        q = T("So where did those 835 ms go?", 32, ASK_C).move_to(DOWN * 1.2)
        self.beat("Everything says fine. So where did those 835 milliseconds go? Hold that question. We'll answer it with a picture.",
                  Write(q), run_time=2.0)
        self.play(FadeOut(VGroup(acc, dash, q)), run_time=0.6)

        # ---------- 2. the parcel
        names = ["shop", "depot A", "depot B", "depot C", "friend"]
        xs = [-5.4, -2.7, 0, 2.7, 5.4]
        stops = VGroup(*[box(n, SVC_C if 0 < i < 4 else GREY_B, w=2.0, h=0.75, size=26).move_to([x, 2.3, 0]) for i, (n, x) in enumerate(zip(names, xs))])
        road = VGroup(*[edge_arrow(stops[i], stops[i + 1]) for i in range(4)])
        self.beat("Let's leave software for a minute. You order a birthday present for a friend. The shop promises two days.",
                  LaggedStart(*[FadeIn(s) for s in stops], lag_ratio=0.15), LaggedStart(*[GrowArrow(a) for a in road], lag_ratio=0.15), run_time=3.0)
        parcel = Square(0.32, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.5), 1).move_to(stops[0].get_bottom() + DOWN * 0.45)
        took = T("took 5 days", 30, SLOW_C).move_to([0, 0.9, 0])
        self.beat("It takes five.",
                  FadeIn(parcel), parcel.animate.move_to(stops[4].get_bottom() + DOWN * 0.45), Succession(Wait(0.8), FadeIn(took)), run_time=2.0)
        books = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.06, width=2.0, height=0.9, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.06), 1),
                                T("parcel passed,", 22), T("all fine", 22, GREEN_M)) for _ in range(3)])
        for b, s in zip(books, stops[1:4]):
            VGroup(b[1], b[2]).arrange(DOWN, buff=0.06).move_to(b[0])
            b.move_to(s.get_center() + DOWN * 2.6)
        self.beat("You call around. Every depot on the way kept its own logbook. And every logbook says the same thing: a parcel passed through, all fine.",
                  FadeOut(took), FadeOut(parcel), LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in books], lag_ratio=0.3), run_time=3.6)
        self.beat("Three honest logbooks, and nobody can say where your parcel sat for three days.",
                  *[Indicate(b[2], color=GREEN_M) for b in books], run_time=1.8)

        # tracking number
        label = VGroup(RoundedRectangle(corner_radius=0.06, width=2.6, height=0.62, stroke_color=ID_C, stroke_width=2.5).set_fill(tint(ID_C, 0.2), 1),
                       M("track 4bf92f", 24, ID_C)).move_to([0, 0.95, 0])
        label[1].move_to(label[0])
        self.beat("Then you notice the tracking number on the label. Each depot scanned it as the parcel came in, and again as it left.",
                  FadeOut(books), FadeIn(label, scale=1.2), run_time=2.0)
        ax0, ax1 = -4.0, 5.6
        days = VGroup(*[T(f"day {d}", 22, GREY_B).move_to([ax0 + (ax1 - ax0) * d / 5, -2.95, 0]) for d in range(6)])
        axis = Line([ax0, -2.6, 0], [ax1, -2.6, 0], stroke_width=2, color=GREY_D)

        def bar(t0, t1, y, c=SPAN_C):
            x0, x1 = ax0 + (ax1 - ax0) * t0 / 5, ax0 + (ax1 - ax0) * t1 / 5
            return Rectangle(width=max(0.05, x1 - x0), height=0.42, stroke_width=0).set_fill(c, 0.85).move_to([(x0 + x1) / 2, y, 0])
        rowsy = [-0.1, -0.8, -1.5]
        rl = VGroup(*[T(n, 26, SVC_C).move_to([-5.4, y, 0]) for n, y in zip(["depot A", "depot B", "depot C"], rowsy)])
        pb = [bar(0.1, 0.8, rowsy[0]), bar(0.9, 2.9, rowsy[1], SLOW_C), bar(3.1, 3.9, rowsy[2])]
        self.beat("Put the scans in order, on one timeline.",
                  Create(axis), FadeIn(days), FadeIn(rl), run_time=1.6)
        self.beat("In at depot A, out of depot A. In at depot B. And out of depot B... two days later.",
                  GrowFromEdge(pb[0], LEFT), Succession(Wait(1.6), GrowFromEdge(pb[1], LEFT)), run_time=3.6)
        self.play(GrowFromEdge(pb[2], LEFT), run_time=0.8)
        shelf = T("sat on a shelf", 26, SLOW_C).next_to(pb[1], UP, buff=0.12)
        self.beat("There it is. Your parcel sat on a shelf in depot B. One number, copied along the whole road, turned a pile of logbooks into a story.",
                  FadeIn(shelf), Indicate(label[1], color=ID_C), run_time=2.6)
        self.play(FadeOut(VGroup(stops, road, label, axis, days, rl, *pb, shelf)), run_time=0.7)

        # ---------- 3. the same pain in software
        api = box("API", SVC_C, w=2.4, h=0.75, size=26).move_to([-4.6, 2.5, 0])
        fraud = box("fraud check", SVC_C, w=2.6, h=0.75, size=26).move_to([-0.6, 2.5, 0])
        card = box("card partner", SVC_C, w=2.7, h=0.75, size=26).move_to([3.6, 2.5, 0])
        db = box("database", SVC_C, w=2.4, h=0.75, size=26).move_to([-4.6, 1.1, 0])
        c1, c2, c3 = edge_arrow(api, fraud), edge_arrow(fraud, card), edge_arrow(api, db)
        svcs = VGroup(api, fraud, card, db)
        self.beat("Software has the same trouble. Picture a checkout on a shop's website. The request enters an API service, a program that answers requests from other programs.",
                  FadeIn(api), run_time=1.8)
        self.beat("The API calls a fraud check, which calls a card partner. The API also writes to a database. Each one is a separate service with its own job.",
                  GrowArrow(c1), FadeIn(fraud), Succession(Wait(1.4), AnimationGroup(GrowArrow(c2), FadeIn(card))), Succession(Wait(3.0), AnimationGroup(GrowArrow(c3), FadeIn(db))), run_time=5.0)
        wait3 = T("the customer waited 3 seconds", 28, ASK_C).move_to([1.6, 1.1, 0])
        self.beat("The customer waited three seconds. Which hop took them?",
                  FadeIn(wait3), run_time=1.6)
        m1 = VGroup(T("metrics:", 26, GREY_B), T("fraud check p95 went up", 26)).arrange(RIGHT, buff=0.25)
        m2 = VGroup(T("logs:", 26, GREY_B), T("lines per service, each with its own clock", 26)).arrange(RIGHT, buff=0.25)
        mm = VGroup(m1, m2).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([0, -0.6, 0])
        self.beat("Metrics give us numbers per service: the fraud check's 95th percentile went up. Logs give us lines per service, each with its own timestamp, and we have to guess which lines belong to this one request.",
                  FadeIn(m1, shift=UP * 0.1), Succession(Wait(3.4), FadeIn(m2, shift=UP * 0.1)), run_time=6.0)
        self.beat("They are the depots' logbooks. Honest, and no help. Wouldn't it be nice to put a tracking number on the request itself?",
                  Indicate(mm, color=GREY_B, scale_factor=1.03), run_time=2.0)
        self.play(FadeOut(mm), FadeOut(wait3), run_time=0.5)

        # ---------- 4. spans and the waterfall
        ax0, ax1 = -3.6, 5.8
        T_MAX = 3.0
        axis = Line([ax0, -2.75, 0], [ax1, -2.75, 0], stroke_width=2, color=GREY_D)
        secs = VGroup(*[T(f"{s} s", 22, GREY_B).move_to([ax0 + (ax1 - ax0) * s / T_MAX, -3.05, 0]) for s in range(4)])

        def sbar(t0, t1, y, c=SPAN_C):
            x0, x1 = ax0 + (ax1 - ax0) * t0 / T_MAX, ax0 + (ax1 - ax0) * t1 / T_MAX
            return Rectangle(width=max(0.05, x1 - x0), height=0.42, stroke_width=0).set_fill(c, 0.85).move_to([(x0 + x1) / 2, y, 0])
        ry = [0.25, -0.45, -1.15, -1.85]
        rn = ["API", "database", "fraud check", "card partner"]
        rlab = VGroup(*[T(n, 26, SVC_C).move_to([-5.3, y, 0]) for n, y in zip(rn, ry)])
        spans = [sbar(0.0, 3.0, ry[0]), sbar(0.05, 0.25, ry[1]), sbar(0.3, 2.95, ry[2]), sbar(0.33, 2.93, ry[3])]
        self.beat("That's what a trace is. Every service records each step of the request as a span: a name, a start time and an end time. Like a scan in, and a scan out.",
                  Create(axis), FadeIn(secs), FadeIn(rlab[0]), GrowFromEdge(spans[0], LEFT), run_time=4.0)
        self.beat("The database write is short. The fraud check is long. And the card partner sits inside it.",
                  FadeIn(rlab[1]), GrowFromEdge(spans[1], LEFT), Succession(Wait(1.4), AnimationGroup(FadeIn(rlab[2]), GrowFromEdge(spans[2], LEFT))),
                  Succession(Wait(2.8), AnimationGroup(FadeIn(rlab[3]), GrowFromEdge(spans[3], LEFT))), run_time=4.2)
        illu = T("illustrative timings", 22, GREY_B).move_to([4.6, 0.85, 0])
        self.play(FadeIn(illu), run_time=0.4)
        pq = T("Which step is slow?", 30, ASK_C).move_to([1.6, 1.15, 0])
        self.beat("Drawn like this, one row per span, the picture is called a waterfall. So, which step is slow? Pause and guess.",
                  FadeIn(pq), run_time=2.0)
        self.pause([1.1, 0.7, 0])
        self.beat("The obvious answer is the longest bar, the API. Let's be fair to it: it really did take three seconds. But look underneath it. Almost all that time, the API was just waiting for its children.",
                  Indicate(spans[0], color=SPAN_C, scale_factor=1.03), Succession(Wait(3.6), Indicate(VGroup(spans[1], spans[2], spans[3]), color=SPAN_C, scale_factor=1.03)), run_time=6.0)
        self.beat("The fraud check, then? Same story. It is long, but it is waiting for the card partner.",
                  Indicate(spans[2], color=SPAN_C, scale_factor=1.03), run_time=2.0)
        under = T("2.6 of the 3 seconds", 26, SLOW_C).next_to(spans[3], DOWN, buff=0.12)
        self.beat("The slow step is the longest bar with nothing underneath it. Here, the card partner: 2.6 of the 3 seconds.",
                  spans[3].animate.set_fill(SLOW_C, 0.9), FadeIn(under), run_time=2.6)
        self.beat("Waiting isn't working. A long bar can simply mean: I was waiting for someone else.",
                  run_time=None)

        # ---------- 5. name the parts
        self.play(FadeOut(VGroup(pq, under, illu)), run_time=0.4)
        tid = VGroup(*[M("4bf92f...", 22, ID_C).next_to(s, RIGHT, buff=0.15) if i else M("4bf92f...", 22, ID_C).move_to(s) for i, s in enumerate(spans)])
        for i in range(1, 4):
            tid[i].next_to(spans[i], RIGHT, buff=0.15)
        tid[0].move_to(spans[0]).set_color(BLACK)
        self.beat("Now the names. Every span in this trace carries the same trace ID. That's our tracking number.",
                  LaggedStart(*[FadeIn(t) for t in tid[1:]], lag_ratio=0.2), FadeIn(tid[0]), run_time=2.6)
        pa = VGroup(
            CurvedArrow(spans[1].get_left() + LEFT * 0.05, spans[0].get_left() + DOWN * 0.12 + LEFT * 0.05, angle=-PI / 2, color=PAR_C, stroke_width=2.5),
            CurvedArrow(spans[3].get_left() + LEFT * 0.05, spans[2].get_left() + DOWN * 0.12 + LEFT * 0.05, angle=-PI / 2, color=PAR_C, stroke_width=2.5),
        )
        self.beat("Each span also has its own span ID, and the ID of its parent. The parents make the tree. The first span, the API's, has no parent. It is the root span.",
                  Create(pa), Succession(Wait(3.6), Indicate(rlab[0], color=SVC_C)), run_time=5.0)
        self.play(FadeOut(VGroup(pa, tid)), run_time=0.4)

        # ---------- 6. how the number travels
        hdr = VGroup(M("traceparent:", 24, GREY_B), M("00", 24), M("4bf92f3577b34da6a3ce929d0e0e4736", 24, ID_C), M("00f067aa0ba902b7", 24, PAR_C), M("01", 24, GREEN_M)).arrange(RIGHT, buff=0.18)
        fit(hdr, 12.6).move_to([0, 1.45, 0])
        self.play(FadeOut(VGroup(*spans, rlab, axis, secs)), run_time=0.5)
        self.beat("But these spans are made in different services. How does the card partner know which trace it is in? Each caller copies the number onto its outgoing request, in a header, an extra line sent with every web request.",
                  travel(c1, ID_C, 1.0), Succession(Wait(1.2), travel(c2, ID_C, 1.0)), run_time=4.0)
        self.beat("The standard one is called traceparent. It has four parts.",
                  FadeIn(hdr, shift=DOWN * 0.1), run_time=1.6)
        hl = [T("version", 22, GREY_B), T("trace ID, 32 hex characters", 22, ID_C), T("parent span ID, 16 hex", 22, PAR_C), T("sampled", 22, GREEN_M)]
        for t, m in zip(hl, hdr[1:]):
            t.next_to(m, DOWN, buff=0.18)
        hl[3].shift(RIGHT * 0.25)
        self.beat("A version. The trace ID, the same for the whole request. The parent span ID, the caller's current span. And a flag: 01 means the caller is recording this trace.",
                  FadeIn(hl[0]), Succession(Wait(0.8), FadeIn(hl[1])), Succession(Wait(3.0), FadeIn(hl[2])), Succession(Wait(5.0), FadeIn(hl[3])), run_time=7.0)
        hop = VGroup(T("each hop:", 26, GREY_B), T("same trace ID,", 26, ID_C), T("new parent", 26, PAR_C)).arrange(RIGHT, buff=0.25).move_to([0, -0.4, 0])
        self.beat("The caller injects the header. The receiver extracts it, and starts its own span as a child. Hop by hop, the trace ID stays the same, and only the parent changes. That hand-over is called context propagation.",
                  FadeIn(hop, shift=UP * 0.1), travel(c1, ID_C, 1.0), Succession(Wait(1.2), travel(c2, ID_C, 1.0)), run_time=4.0)
        self.play(FadeOut(VGroup(hdr, *hl)), run_time=0.4)

        # ---------- 7. break: a hop that drops the header
        prox = box("proxy", GREY_B, w=1.5, h=0.7, size=24).move_to([1.55, 1.3, 0])
        self.beat("Now let's break it. Put a proxy, a program that forwards requests, between the fraud check and the card partner. Some proxies strip headers they don't know.",
                  FadeIn(prox, shift=DOWN * 0.1), run_time=2.0)
        drop = M("traceparent", 22, ID_C).move_to(c2.get_center() + UP * 0.35)
        self.beat("The header goes in. It does not come out.",
                  FadeIn(drop), Succession(Wait(0.8), drop.animate.move_to(prox.get_bottom() + DOWN * 0.3).set_opacity(0)), run_time=2.0)
        new = VGroup(T("card partner starts a new trace:", 26, SLOW_C), M("7d01c2...", 24, SLOW_C)).arrange(RIGHT, buff=0.25).move_to([0, -1.3, 0])
        self.beat("So the card partner sees no tracking number, and starts a brand new one. A parcel with a fresh label.",
                  FadeIn(new, shift=UP * 0.1), Indicate(card[1], color=SLOW_C), run_time=2.4)
        lie = T("trace 1: fraud check looks slow, with nothing under it", 26, ASK_C).move_to([0, -2.2, 0])
        self.beat("Now you have two traces that look unrelated. And in the first one, the fraud check is a long bar with nothing underneath. It looks guilty, and it isn't.",
                  FadeIn(lie, shift=UP * 0.1), run_time=3.0)
        rule = T("A trace is only as long as its chain of headers.", 30, ID_C).move_to([0, -3.0, 0])
        self.beat("So the point really is: a trace is only as long as its chain of headers. When it stops early, look for the hop that dropped it.",
                  FadeIn(rule), run_time=2.4)
        self.play(FadeOut(VGroup(prox, new, lie, rule, hop, svcs, c1, c2, c3)), run_time=0.6)

        # ---------- 8. back to hello-devops
        app = box("hello-devops", SVC_C, w=3.0, h=0.75, size=26).move_to([-3.0, 2.5, 0])
        red = box("Redis", SVC_C, w=2.0, h=0.75, size=26).move_to([2.5, 2.5, 0])
        ca = edge_arrow(app, red)
        self.beat("Back to our question. hello-devops keeps its visit count in Redis, a small, fast database. In the lab, Redis writes were paused for 800 milliseconds, and one visit was sent.",
                  FadeIn(app), GrowArrow(ca), FadeIn(red), run_time=3.0)
        T_MAX = 900
        axis = Line([ax0, -2.0, 0], [ax1, -2.0, 0], stroke_width=2, color=GREY_D)
        ms = VGroup(*[T(f"{v} ms", 22, GREY_B).move_to([ax0 + (ax1 - ax0) * v / T_MAX, -2.3, 0]) for v in (0, 300, 600, 900)])

        def mbar(t0, t1, y, c=SPAN_C):
            x0, x1 = ax0 + (ax1 - ax0) * t0 / T_MAX, ax0 + (ax1 - ax0) * t1 / T_MAX
            return Rectangle(width=max(0.05, x1 - x0), height=0.48, stroke_width=0).set_fill(c, 0.85).move_to([(x0 + x1) / 2, y, 0])
        g = mbar(0, 835, 0.6); i = mbar(2, 834, -0.3, SLOW_C)
        gl = VGroup(M("GET /", 24, SVC_C).move_to([-5.2, 0.6, 0]), M("INCRBY", 24, SVC_C).move_to([-5.2, -0.3, 0]))
        gt = VGroup(T("835 ms", 26).move_to(g), T("832 ms", 26).move_to(i))
        gt[0].set_color(BLACK); gt[1].set_color(BLACK)
        self.beat("No code changed. Starting the app under a wrapper command, opentelemetry-instrument, was enough to get spans. The trace showed GET slash, taking 835 milliseconds.",
                  Create(axis), FadeIn(ms), FadeIn(gl[0]), GrowFromEdge(g, LEFT), Succession(Wait(3.0), FadeIn(gt[0])), run_time=4.6)
        self.beat("And under it, its child span INCRBY, the Redis command that adds to the count: 832 of those milliseconds. The longest bar with nothing underneath it.",
                  FadeIn(gl[1]), GrowFromEdge(i, LEFT), Succession(Wait(2.4), FadeIn(gt[1])), run_time=4.0)
        self.beat("Status 200, zero errors, and still a slow Redis call. Now you know where to look next.",
                  Indicate(red[1], color=SLOW_C), run_time=2.0)

        # ---------- 9. guardrails
        self.play(FadeOut(VGroup(app, red, ca, axis, ms, g, i, gl, gt)), run_time=0.6)
        gg = VGroup(
            VGroup(T("a metric alert says", 26, GREY_B), T("something is wrong", 26)).arrange(RIGHT, buff=0.25),
            VGroup(T("a trace shows", 26, GREY_B), T("where", 26, ID_C)).arrange(RIGHT, buff=0.25),
            VGroup(T("that request's logs explain", 26, GREY_B), T("why", 26)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, 1.8, 0])
        self.beat("A trace doesn't replace the others. A metric alert says something is wrong. A trace shows where. And the logs of that one request explain why.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in gg], lag_ratio=0.6), run_time=5.0)
        s1 = T("Every trace costs CPU, network and storage, so busy systems keep only some: sampling.", 24)
        s2 = VGroup(T("head sampling:", 24, GREEN_M), T("decide at the start, cheap but blind", 24)).arrange(RIGHT, buff=0.2)
        s3 = VGroup(T("tail sampling:", 24, GREEN_M), T("decide at the end, keeps errors and slow ones, costs memory", 24)).arrange(RIGHT, buff=0.2)
        ss = VGroup(s1, s2, s3).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        fit(ss, 12.6).move_to([0, -1.25, 0])
        self.beat("And recording every request costs CPU, network and storage. So at high traffic, teams keep only some traces. That's sampling.",
                  FadeIn(s1, shift=UP * 0.1), run_time=2.4)
        self.beat("Head sampling decides at the start, and the 01 flag carries that choice to every service. It's cheap, but blind: it can't know yet which requests will fail or crawl. Tail sampling waits for the whole trace, keeps the errors and the slow ones, and pays for it in memory.",
                  FadeIn(s2, shift=UP * 0.1), Succession(Wait(5.6), FadeIn(s3, shift=UP * 0.1)), run_time=8.0)
        self.play(FadeOut(VGroup(gg, ss)), run_time=0.6)

        # ---------- 10. moral, check
        mor = VGroup(T("One tracking number, copied hop by hop.", 32, ID_C), T("The slow step: the longest bar with nothing under it.", 30)).arrange(DOWN, buff=0.3).move_to(UP * 1.6)
        self.beat("So, the whole story in two lines. One tracking number, copied from hop to hop in the traceparent header. And the slow step is the longest bar with nothing underneath it.",
                  Write(mor[0]), Succession(Wait(3.6), FadeIn(mor[1])), run_time=6.0)
        cq = VGroup(T("Quick check: a request crosses four services,", 28), T("but its trace shows only the first two. Where do you look?", 28)).arrange(DOWN, buff=0.18).move_to(DOWN * 0.6)
        self.beat("A quick check. A request crosses four services, but its trace shows only the first two. Where do you look? Pause and think.",
                  FadeIn(cq, shift=UP * 0.1), run_time=2.4)
        self.pause([0, -1.9, 0], text="pause and think")
        ans = T("At the hop between service two and three: something dropped the header.", 26, ID_C).move_to(DOWN * 2.3)
        fit(ans, 12.6)
        self.beat("At the hop between the second and the third. Something there, a proxy, a queue, a homemade client, didn't pass the header on.",
                  FadeIn(ans, shift=UP * 0.1), run_time=2.4)
        self.beat("Next, a new part about the calls between services themselves. When a call is slow or fails, who decides to wait, retry, or give up?",
                  FadeOut(VGroup(cq, ans)), mor.animate.set_opacity(0.4), run_time=1.6)
        self.wait(1.0)
