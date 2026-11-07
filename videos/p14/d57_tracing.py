import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bOTLP\b", "O T L P"), (r"\bINCRBY\b", "incr by")])

TID = "4bf92f…"


def span_bar(x0, x1, y, color, h=0.5):
    r = Rectangle(width=max(0.06, x1 - x0), height=h, stroke_color=color, stroke_width=2.5,
                  fill_color=interpolate_color(ManimColor("#000000"), ManimColor(color), 0.35), fill_opacity=1)
    return r.move_to([x0, y, 0], aligned_edge=LEFT)


def tag(lines, colors):
    g = VGroup(*[M(t, 20, c) for t, c in zip(lines, colors)]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    return g


class D57Tracing(VoiceScene):
    def construct(self):
        self.title_card("Following one request", "spans, traces and context propagation")

        # ---------- 1. one checkout request, several services
        cust = Circle(radius=0.3, stroke_color=GREY_B, stroke_width=3).set_fill(BLACK, 1).move_to([-6.1, 1.6, 0])
        clab = T("customer", 22, GREY_B).next_to(cust, DOWN, buff=0.15)
        api = box("API", BLUE_M, w=1.8).move_to([-3.9, 1.6, 0])
        fraud = box("fraud check", TEAL_M, w=2.5).move_to([-0.3, 1.6, 0])
        card = box("card partner", GOLD_M, w=2.6).move_to([3.8, 1.6, 0])
        db = box("database", PURPLE_M, w=2.2).move_to([-3.9, -0.5, 0])
        a0 = edge_arrow(cust, api)
        a1 = edge_arrow(api, fraud)
        a2 = edge_arrow(fraud, card)
        a3 = edge_arrow(api, db)
        self.beat("Picture a checkout request on a payments site. It enters an API service.",
                  FadeIn(cust), FadeIn(clab), GrowArrow(a0), Create(api[0]), Write(api[1]), run_time=1.8)
        self.play(travel(a0), run_time=0.7)
        self.beat("The API calls a fraud check, which calls a card partner. The API also writes to a database.",
                  LaggedStart(AnimationGroup(GrowArrow(a1), Create(fraud[0]), Write(fraud[1])),
                              AnimationGroup(GrowArrow(a2), Create(card[0]), Write(card[1])),
                              AnimationGroup(GrowArrow(a3), Create(db[0]), Write(db[1])), lag_ratio=0.45),
                  run_time=3.4)
        self.play(travel(a1, run_time=0.6), travel(a3, run_time=0.6), run_time=0.6)
        self.play(travel(a2, run_time=0.6), run_time=0.6)

        tr = ValueTracker(0)
        clock = always_redraw(lambda: T(f"waited {tr.get_value():.1f} s", 26, YELLOW_M).next_to(clab, DOWN, buff=0.25))
        qs = VGroup(*[T("?", 34, YELLOW_M).next_to(a, UP, buff=0.12) for a in (a1, a2)],
                    T("?", 34, YELLOW_M).next_to(a3, LEFT, buff=0.15))
        self.add(clock)
        self.beat("The customer waited three seconds. Which hop took them?",
                  tr.animate(rate_func=linear).set_value(3.0), run_time=2.2)
        self.play(LaggedStart(*[FadeIn(q, scale=0.6) for q in qs], lag_ratio=0.2), run_time=0.8)
        clock.clear_updaters()

        # metrics: an average per service
        ax = VGroup(Line([-1.25, 0.0, 0], [1.25, 0.0, 0]), Line([-1.25, 0.0, 0], [-1.25, 0.85, 0])).set_stroke(GREY_D, 2).shift(DOWN * 0.15 + LEFT * 0.2)
        pts = [[-1.2, 0.1], [-0.8, 0.12], [-0.4, 0.1], [0.0, 0.15], [0.4, 0.35], [0.8, 0.6], [1.2, 0.78]]
        curve = VMobject(stroke_color=TEAL_M, stroke_width=3).set_points_as_corners([[x - 0.2, y - 0.15, 0] for x, y in pts])
        mlab = M("p95", 20, TEAL_M).next_to(ax, RIGHT, buff=0.15).align_to(ax, UP)
        self.beat("Metrics give you averages per service. The 95th percentile of the fraud check went up.",
                  Create(ax), Create(curve), FadeIn(mlab), run_time=2.0)

        # logs: lines per service, mixed with other requests
        rows = [("12:03:07.101", "api", "POST /checkout", BLUE_M), ("12:03:07.104", "api", "POST /checkout", BLUE_M),
                ("12:03:07.109", "fraud", "check started", TEAL_M), ("12:03:07.113", "fraud", "check started", TEAL_M),
                ("12:03:07.120", "card", "charge sent", GOLD_M), ("12:03:07.131", "card", "charge sent", GOLD_M)]
        logs = VGroup()
        for i, (ts, sv, msg, c) in enumerate(rows):
            r = VGroup(M(ts, 20, GREY_B), M(sv, 20, c), M(msg, 20, WHITE))
            r[0].move_to([0, -0.4 * i, 0], aligned_edge=LEFT)
            r[1].move_to([2.05, -0.4 * i, 0], aligned_edge=LEFT)
            r[2].move_to([3.15, -0.4 * i, 0], aligned_edge=LEFT)
            logs.add(r)
        lpanel = SurroundingRectangle(logs, buff=0.25, corner_radius=0.1, stroke_color=GREY_D, stroke_width=2)
        lg = VGroup(lpanel, logs).move_to([2.6, -1.95, 0])
        llab = T("logs", 22, GREY_B).next_to(lpanel, LEFT, buff=0.2).align_to(lpanel, UP)
        self.beat("Logs give you lines per service, each with its own timestamp. You have to guess which lines belong to this one request.",
                  Create(lpanel), FadeIn(llab), LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in logs], lag_ratio=0.2), run_time=3.0)
        self.beat("Neither one tells you where this request spent its three seconds.",
                  *[Indicate(l, color=YELLOW_M, scale_factor=1.03) for l in logs[0:2]], Wiggle(qs[0]), run_time=1.8)

        # ---------- 2. spans
        self.play(FadeOut(VGroup(ax, curve, mlab, lg, llab, qs)), run_time=0.7)
        self.beat("A trace does. It is the story of one request, told as a tree of timed steps.",
                  *[Indicate(b, color=YELLOW_M, scale_factor=1.06) for b in (api, fraud, card, db)], run_time=2.2)

        cl = VGroup(M("name      fraud check", 22), M("start     12:03:07.300", 22), M("end       12:03:09.950", 22),
                    M("duration  2.65 s", 22, YELLOW_M), M("http.response.status_code = 200", 20, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cbox = RoundedRectangle(corner_radius=0.12, width=cl.width + 0.6, height=cl.height + 0.5, stroke_color=TEAL_M, stroke_width=2.5).set_fill(BLACK, 1)
        scard = VGroup(cbox, cl.move_to(cbox)).move_to([2.4, -1.75, 0])
        slab = T("one span", 24, TEAL_M).next_to(cbox, UP, buff=0.12).align_to(cbox, LEFT)
        sl = link(fraud, scard, TEAL_M)
        self.beat("Each step is a span. It has a name, a start time and an end time, so a duration, and some facts about what happened.",
                  fraud[0].animate.set_stroke(width=6), Create(sl), Create(cbox), FadeIn(slab),
                  LaggedStart(*[FadeIn(cl[i], shift=RIGHT * 0.1) for i in (0, 1, 2, 3, 4)], lag_ratio=0.5), run_time=4.4)
        self.play(FadeOut(VGroup(scard, slab, sl)), fraud[0].animate.set_stroke(width=3), run_time=0.6)

        # trace ID, span ID, parent
        ids = {"api": ("3ac9…", "none"), "fraud": ("b71e…", "3ac9…"), "card": ("52d0…", "b71e…"), "db": ("e94f…", "3ac9…")}
        tags = {}
        for k, b in (("api", api), ("fraud", fraud), ("card", card), ("db", db)):
            sid, par = ids[k]
            t = tag([f"trace  {TID}", f"span   {sid}", f"parent {par}"], [YELLOW_M, TEAL_M, GREY_B])
            t.next_to(b, DOWN, buff=0.22)
            if k == "api":
                t.align_to(a3, LEFT).shift(RIGHT * 0.25)
            tags[k] = t
        self.beat("Every span in the trace carries the same trace ID.",
                  LaggedStart(*[FadeIn(tags[k][0], shift=DOWN * 0.1) for k in tags], lag_ratio=0.2), run_time=1.8)
        self.beat("Each one also has its own span ID, and the span ID of its parent. The parent IDs make the tree.",
                  LaggedStart(*[FadeIn(tags[k][1], shift=DOWN * 0.1) for k in tags], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(tags[k][2], shift=DOWN * 0.1) for k in tags], lag_ratio=0.15), run_time=3.0)
        root = chip("root span", BLUE_M, 22).next_to(api, UP, buff=0.25)
        self.beat("The first span has no parent. It is called the root span.",
                  Indicate(tags["api"][2], color=BLUE_M), FadeIn(root, shift=DOWN * 0.1), run_time=1.6)

        # ---------- 3. context propagation
        others = VGroup(tags["fraud"], tags["card"])
        self.beat("But these spans are made in different services. Each service has to tell the next one which trace it is in.",
                  FadeOut(root), others.animate.set_opacity(0.15), run_time=1.6)
        env = chip("traceparent", YELLOW_M, 20, mono=True).next_to(a1, UP, buff=0.5)
        self.beat("That hand-over is context propagation. The caller injects the context into the outgoing request, as an HTTP header.",
                  FadeIn(env, shift=UP * 0.15), Indicate(api, color=BLUE_M, scale_factor=1.05), run_time=2.4)

        parts = ["00", "4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7", "01"]
        pcol = [GREY_B, YELLOW_M, TEAL_M, GREEN_M]
        hval = M("-".join(parts), 24)
        hdr = VGroup(M("traceparent:", 24), hval).arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
        hdr.move_to([0, -2.6, 0])
        hp = [hval[0:2], hval[3:35], hval[36:52], hval[53:55]]
        hbox = SurroundingRectangle(hdr, buff=0.25, corner_radius=0.1, stroke_color=YELLOW_M, stroke_width=2).set_fill(BLACK, 1)
        self.beat("For HTTP, OpenTelemetry uses the W3C traceparent header. It has four parts, split by dashes.",
                  FadeOut(VGroup(tags["api"], tags["db"])), Create(hbox), Write(hdr), run_time=2.6)

        plabs = ["version", "trace ID: 32 hex characters", "parent span ID: 16 hex", "flags"]
        pl = [T(plabs[i], 22, pcol[i]).next_to(hp[i], DOWN, buff=0.4) for i in range(4)]
        for i in (0, 3):
            pl[i].next_to(hp[i], UP, buff=0.5)
        for i in (1, 2):
            pl[i].next_to(hp[i], DOWN, buff=0.45)
        ul = [Line(hp[i].get_corner(DL) + DOWN * 0.08, hp[i].get_corner(DR) + DOWN * 0.08, stroke_width=3, color=pcol[i]) for i in range(4)]

        def show(i):
            return [hp[i].animate.set_color(pcol[i]), Create(ul[i]), FadeIn(pl[i], shift=UP * 0.1)]

        self.beat("00 is the version of the format.", *show(0), run_time=1.2)
        self.beat("Next comes the trace ID: 32 hex characters, the same for every span of this request.", *show(1), run_time=1.6)
        self.beat("Then the parent span ID: 16 hex characters, the caller's current span.", *show(2), run_time=1.4)
        self.beat("Last, the flags. 01 means sampled: the caller is recording this trace.", *show(3), run_time=1.4)

        # the receiver extracts it, makes a child span, passes it on
        self.beat("The receiver extracts the header, and starts its own span as a child of the caller's span.",
                  env.animate.shift(RIGHT * 0.7).set_opacity(0),
                  tags["fraud"].animate.set_opacity(1), Indicate(fraud, color=TEAL_M, scale_factor=1.05), run_time=2.0)
        env2 = chip("traceparent", YELLOW_M, 20, mono=True).next_to(a2, UP, buff=0.5)
        self.beat("Then it injects the same trace ID into its own outgoing call. Only the parent changes, hop by hop.",
                  FadeIn(env2, shift=RIGHT * 0.3),
                  Succession(tags["card"].animate.set_opacity(1), AnimationGroup(Indicate(tags["card"][0], color=YELLOW_M), Indicate(tags["card"][2], color=WHITE))),
                  run_time=2.6)

        # a hop that drops the header
        prox = box("proxy", RED_M, w=1.3, h=0.6, size=22).move_to(a2.get_center())
        bad = M(f"trace  0d99…", 20, RED_M).move_to(tags["card"][0], aligned_edge=LEFT)
        self.beat("Trouble starts at a hop that does not pass it on, like a proxy that strips unknown headers.",
                  FadeOut(env2), GrowFromCenter(prox), run_time=1.6)
        self.beat("The card partner then starts a new trace, and you get two traces that look unrelated. When a trace stops early, look for that hop first.",
                  Transform(tags["card"][0], bad), Transform(tags["card"][2], M("parent none", 20, RED_M).move_to(tags["card"][2], aligned_edge=LEFT)),
                  Succession(Wait(1.0), Circumscribe(prox, color=RED_M, buff=0.08)), run_time=3.0)
        good0 = M(f"trace  {TID}", 20, YELLOW_M).move_to(tags["card"][0], aligned_edge=LEFT)
        good2 = M("parent b71e…", 20, GREY_B).move_to(tags["card"][2], aligned_edge=LEFT)
        self.play(FadeOut(prox), Transform(tags["card"][0], good0), Transform(tags["card"][2], good2),
                  FadeOut(VGroup(hbox, hdr, *ul, *pl)), run_time=0.8)

        # ---------- 4. the Collector
        self.play(FadeOut(VGroup(tags["fraud"], tags["card"])), run_time=0.5)
        recv = box("receivers", BLUE_M, w=2.0, h=0.7, size=24).move_to([-3.75, -2.05, 0])
        proc = box("processors", TEAL_M, w=2.0, h=0.7, size=24).move_to([-0.8, -2.05, 0])
        expo = box("exporters", GOLD_M, w=2.0, h=0.7, size=24).move_to([2.15, -2.05, 0])
        cframe = RoundedRectangle(corner_radius=0.15, width=8.7, height=1.75, stroke_color=GREY_B, stroke_width=2).move_to([-0.8, -2.3, 0])
        cname = T("OpenTelemetry Collector", 24, GREY_B).next_to(cframe, DOWN, buff=0.12)
        jae = box("Jaeger", PURPLE_M, w=1.9).move_to([5.45, -2.3, 0])
        ia = [Arrow(recv.get_right(), proc.get_left(), buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.35),
              Arrow(proc.get_right(), expo.get_left(), buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.35)]
        self.beat("Each service exports its spans over OTLP, the OpenTelemetry Protocol. Most teams send them to an OpenTelemetry Collector first.",
                  Create(cframe), FadeIn(cname), LaggedStart(*[AnimationGroup(Create(b[0]), Write(b[1])) for b in (recv, proc, expo)], lag_ratio=0.25),
                  *[GrowArrow(a) for a in ia], run_time=3.0)
        srcs = [api, fraud, card, db]
        cols = [BLUE_M, TEAL_M, GOLD_M, PURPLE_M]
        flies = []
        for s, c in zip(srcs, cols):
            p0 = s.get_bottom() if s is not db else s.get_right()
            seg = Line(p0, recv.get_top() + RIGHT * (0.3 * (srcs.index(s) - 1.5)))
            bar = span_bar(0, 0.45, 0, c, h=0.16).move_to(p0)
            flies.append(Succession(FadeIn(bar, run_time=0.1), MoveAlongPath(bar, seg, run_time=1.0), FadeOut(bar, run_time=0.2)))
        self.play(LaggedStart(*flies, lag_ratio=0.2), run_time=2.0)

        rl = M("otlp: 4317, 4318", 20, BLUE_M).next_to(recv, DOWN, buff=0.15)
        pl2 = M("transform/scrub", 20, TEAL_M).next_to(proc, DOWN, buff=0.15)
        el = M("otlp_grpc/jaeger", 20, GOLD_M).next_to(expo, DOWN, buff=0.15)
        self.beat("Receivers take data in. In the lab, the otlp receiver listens on 4317 for gRPC, and 4318 for HTTP.",
                  recv[0].animate.set_stroke(width=6), FadeIn(rl, shift=UP * 0.1), run_time=2.2)
        self.beat("Processors change it. One hashes the client address, because an IP address is personal data.",
                  recv[0].animate.set_stroke(width=3), proc[0].animate.set_stroke(width=6), FadeIn(pl2, shift=UP * 0.1), run_time=2.2)
        ja = edge_arrow(cframe, jae, GOLD_M)
        self.beat("Exporters send it out. Here, to Jaeger, which stores the traces and shows them in a web UI.",
                  proc[0].animate.set_stroke(width=3), expo[0].animate.set_stroke(width=6), FadeIn(el, shift=UP * 0.1),
                  GrowArrow(ja), Create(jae[0]), Write(jae[1]), run_time=2.4)
        self.play(travel(ja, GOLD_M), expo[0].animate.set_stroke(width=3), run_time=0.8)

        # ---------- 5. the waterfall
        self.play(FadeOut(VGroup(cust, clab, clock, api, fraud, card, db, a0, a1, a2, a3, recv, proc, expo, cframe, cname, *ia, rl, pl2, el, ja)),
                  jae.animate.scale(0.75).move_to([5.6, 3.2, 0]), run_time=1.0)
        x0, x1 = -2.4, 6.2
        X = lambda s: x0 + (x1 - x0) * s / 3.0
        axis = Line([x0, -2.6, 0], [x1, -2.6, 0], stroke_width=2, color=GREY_D)
        ticks = VGroup(*[VGroup(Line([X(s), -2.7, 0], [X(s), -2.5, 0], stroke_width=2, color=GREY_D),
                                T(f"{s} s", 22, GREY_B).move_to([X(s), -3.0, 0])) for s in range(4)])
        spans = [("API", 0.0, 3.0, BLUE_M, 0), ("database write", 0.05, 0.25, PURPLE_M, 1),
                 ("fraud check", 0.3, 2.95, TEAL_M, 1), ("card partner", 0.33, 2.93, GOLD_M, 2)]
        bars, labs = VGroup(), VGroup()
        for i, (n, a, b, c, d) in enumerate(spans):
            y = 2.3 - i * 1.1
            bars.add(span_bar(X(a), X(b), y, c))
            labs.add(T(n, 26, c).move_to([-6.6 + 0.35 * d, y, 0], aligned_edge=LEFT))
        thead = M(f"trace {TID}", 22, YELLOW_M).move_to([-6.6, 3.1, 0], aligned_edge=LEFT)
        self.beat("Jaeger draws the spans of one trace on a timeline, one row each. That picture is called a waterfall.",
                  FadeIn(thead), Create(axis), FadeIn(ticks),
                  LaggedStart(*[AnimationGroup(FadeIn(l), GrowFromEdge(b, LEFT)) for l, b in zip(labs, bars)], lag_ratio=0.5), run_time=3.6)
        self.beat("The API span covers all three seconds. The database write is short. The fraud check is long, but it has a child under it.",
                  Indicate(bars[0], color=BLUE_M, scale_factor=1.02), Succession(Wait(0.6), Indicate(bars[1], color=PURPLE_M, scale_factor=1.15)),
                  Succession(Wait(1.6), Indicate(bars[2], color=TEAL_M, scale_factor=1.03)), run_time=4.2)
        hl = SurroundingRectangle(bars[3], buff=0.1, color=YELLOW_M, stroke_width=3)
        br = Brace(bars[3], DOWN, buff=0.22, color=YELLOW_M)
        brt = T("2.6 of 3 seconds", 26, YELLOW_M).next_to(br, DOWN, buff=0.1)
        self.beat("The slow step is the longest bar with nothing underneath it. Here, the card partner: 2.6 of the 3 seconds.",
                  Create(hl), GrowFromCenter(br), FadeIn(brt, shift=UP * 0.1), run_time=2.6)

        # the lab's real slow trace
        self.play(FadeOut(VGroup(hl, br, brt, bars, labs, ticks, thead)), run_time=0.7)
        X2 = lambda ms: x0 + (x1 - x0) * ms / 900.0
        ticks2 = VGroup(*[VGroup(Line([X2(s), -2.7, 0], [X2(s), -2.5, 0], stroke_width=2, color=GREY_D),
                                 T(f"{s} ms", 22, GREY_B).move_to([X2(s), -3.0, 0])) for s in (0, 400, 800)])
        lab2 = VGroup(VGroup(M("GET /", 26, BLUE_M), T("server span", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.18),
                      VGroup(M("INCRBY", 26, TEAL_M), T("client span", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.18))
        lab2[0].move_to([-6.6, 1.1, 0], aligned_edge=LEFT)
        lab2[1].move_to([-6.25, -0.2, 0], aligned_edge=LEFT)
        b2 = VGroup(span_bar(X2(0), X2(835), 1.1, BLUE_M, h=0.6), span_bar(X2(2), X2(834), -0.2, TEAL_M, h=0.6))
        n2 = VGroup(M("835 ms", 24).move_to(b2[0]), M("832 ms", 24).move_to(b2[1]))
        hd = T("hello-devops in the lab: Redis writes paused for 800 ms", 26, GREY_B).move_to([0, 3.1, 0])
        self.beat("It works for hello-devops too. In the lab, Redis writes were paused for 800 milliseconds, and one request was sent.",
                  FadeOut(jae), FadeIn(hd), FadeIn(ticks2), FadeIn(lab2[0]), GrowFromEdge(b2[0], LEFT), run_time=2.8)
        self.beat("GET / took 835 milliseconds, and its child span INCRBY took 832 of them.",
                  FadeIn(n2[0]), FadeIn(lab2[1]), GrowFromEdge(b2[1], LEFT), Succession(Wait(1.2), FadeIn(n2[1])), run_time=3.0)
        hl2 = SurroundingRectangle(b2[1], buff=0.1, color=YELLOW_M, stroke_width=3)
        slow = T("slow step: Redis", 28, YELLOW_M).move_to([X2(420), -1.35, 0])
        self.beat("So Redis is the slow step, and you know where to look next.",
                  Create(hl2), FadeIn(slow, shift=UP * 0.1), run_time=1.6)

        # ---------- recap
        recap = T("one trace ID in traceparent  →  every span joins one waterfall", 28, YELLOW_M).move_to(hd)
        self.beat("One trace ID, carried in traceparent, joins the spans of every service into one waterfall. The longest bar with nothing under it is the slow step.",
                  FadeOut(hd), Write(recap), run_time=3.0)
        self.wait(1.0)
