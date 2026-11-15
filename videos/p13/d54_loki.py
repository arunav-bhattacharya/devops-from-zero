import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bLogQL\b", "log Q L"), (r"\bservice_name\b", "service name"), (r"\bline_format\b", "line format"), (r"\bduration_ms\b", "duration M S"),
    (r"\bLoki\b", "lowkey"), (r"\bAlloy\b", "alloy"), (r"/healthz\b", "health Z"), (r"\breq-42\b", "rek forty-two"),
    (r"\bdocker compose logs\b", "docker compose logs"), (r'!= "/healthz"', "not equals health Z"),
])


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def panel(w, h, color, c, a=0.06, sw=2.5):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, a), 1).move_to(c)


def marks(n, x0, y, color, w=0.22, gap=0.12):
    """Little bars standing for log lines in a stream."""
    return VGroup(*[Rectangle(width=w, height=0.26, stroke_width=0).set_fill(color, 0.75).move_to([x0 + i * (w + gap), y, 0]) for i in range(n)])


LINES = [('{"method":"GET","path":"/","status":200,...}', "/", 200),
         ('{"method":"GET","path":"/healthz","status":200,...}', "/healthz", 200),
         ('{"method":"GET","path":"/","status":500,...}', "/", 500),
         ('{"method":"GET","path":"/healthz","status":200,...}', "/healthz", 200),
         ('{"method":"GET","path":"/","status":200,...}', "/", 200),
         ('{"method":"GET","path":"/","status":500,...}', "/", 500)]


class D54Loki(VoiceScene):
    def construct(self):
        self.title_card("How Loki finds a log line", "labels pick the streams, and the text stays cheap")

        # ---- 1. the problem
        c0 = box("web container", TEAL_M, w=3.2, h=0.8, size=26).move_to([-3.0, 1.4, 0])
        ll = VGroup(*[Line(LEFT * 1.3, RIGHT * (1.3 - 0.35 * (k % 3)), stroke_width=3, color=GREY_B) for k in range(4)]).arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(c0, DOWN, buff=0.3)
        cmd = M("$ docker compose logs", 24, GREY_B).move_to([2.6, 1.4, 0])
        self.beat("So far you have read logs with docker compose logs. That works on one machine, while the containers exist.",
                  FadeIn(c0), LaggedStart(*[Create(l) for l in ll], lag_ratio=0.3), FadeIn(cmd), run_time=4.4)
        x = tick(False, 0.4).move_to(c0)
        ten = T("and with ten servers, you search in ten places", 26, GREY_B).move_to([0, -1.6, 0])
        self.beat("Remove a container, and its logs go with it. With ten servers, you would search in ten places.",
                  Create(x), c0.animate.set_opacity(0.3), ll.animate.set_opacity(0.15), Succession(Wait(2.4), FadeIn(ten)), run_time=4.4)
        self.play(FadeOut(VGroup(c0, ll, cmd, x, ten)), run_time=0.6)

        # ---- 2. containers -> Alloy -> Loki, with streams
        svc = [("web", TEAL_M), ("prometheus", RED_M), ("grafana", GOLD_M)]
        conts = VGroup(*[box(n, c, w=2.3, h=0.7, size=24) for n, c in svc]).arrange(DOWN, buff=0.55).move_to([-5.55, 0.0, 0])
        alloy = box("Alloy", PURPLE_M, w=1.7, h=0.8, size=26).move_to([-3.25, 0.0, 0])
        loki = panel(8.2, 4.3, BLUE_M, [2.4, -0.1, 0], 0.04, 2)
        lokil = T("Loki", 28, BLUE_M).next_to(loki, UP, buff=0.15).align_to(loki, LEFT)
        ca = VGroup(*[Arrow(c.get_right(), alloy.get_left(), buff=0.08, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.15) for c in conts])
        push = Arrow(alloy.get_right(), [loki.get_left()[0], 0, 0], buff=0.08, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        pl = T("push", 22, GREY_B).next_to(push, UP, buff=0.1)
        self.beat("Loki is Grafana Labs' log store: one place for the logs of every container.",
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in conts], lag_ratio=0.25), FadeIn(loki), FadeIn(lokil), run_time=3.0)
        self.beat("Loki does not scrape like Prometheus. A log is a stream of events, with no current value to read. So a collector sends the lines as they appear. In the lab, that is Grafana Alloy.",
                  Succession(Wait(5.0), AnimationGroup(FadeIn(alloy), *[GrowArrow(a) for a in ca])), Succession(Wait(7.0), AnimationGroup(GrowArrow(push), FadeIn(pl))), run_time=9.6)

        # streams: one lane per label set
        LX0 = -1.35
        lanes = VGroup()
        labs = VGroup()
        ys = [1.1, 0.0, -1.1]
        for (n, c), y in zip(svc, ys):
            lab = M(f'{{service="{n}"}}', 20, c).move_to([LX0, y, 0], aligned_edge=LEFT)
            labs.add(lab)
            lanes.add(Line([LX0 + 2.9, y, 0], [6.25, y, 0], stroke_width=1.5, color=GREY_D))
        self.beat("Alloy gives each line a few labels, such as service web, and the container name.",
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in labs], lag_ratio=0.3), run_time=2.6)
        ms = [marks(9, LX0 + 3.1, y, c) for (n, c), y in zip(svc, ys)]
        self.beat("All lines with the same labels form one log stream. Here, three streams.",
                  *[Create(l) for l in lanes], *[LaggedStart(*[FadeIn(m, shift=RIGHT * 0.2) for m in mm], lag_ratio=0.15) for mm in ms],
                  *[travel(a, c, 1.2) for a, (n, c) in zip(ca, svc)], run_time=4.0)

        # only the labels are indexed; the text goes into chunks
        idx = panel(2.6, 1.1, BLUE_M, [4.95, 1.45, 0], 0.12, 2)
        self.play(*[l.animate.shift(DOWN * 0.45) for l in labs], *[l.animate.shift(DOWN * 0.45) for l in lanes], *[m.animate.shift(DOWN * 0.45) for m in ms], run_time=0.6)
        idxl = VGroup(T("index:", 22, BLUE_M), T("3 label sets", 22, WHITE)).arrange(DOWN, buff=0.08).move_to(idx)
        chunks = VGroup(*[SurroundingRectangle(m, buff=0.06, stroke_color=GREY_B, stroke_width=1.5) for m in ms])
        cl = T("text: compressed into chunks, not indexed", 22, GREY_B).move_to([2.4, -2.0, 0])
        self.beat("Here is the main idea. Loki indexes only the labels. The text of each line is compressed into chunks, and not indexed at all.",
                  FadeIn(idx), FadeIn(idxl), Indicate(labs, color=BLUE_M, scale_factor=1.03), Succession(Wait(3.6), AnimationGroup(Create(chunks), FadeIn(cl))), run_time=6.6)
        es = T("Elasticsearch indexes every word: more disk and memory, faster word search", 22, PURPLE_M).move_to([0.0, -3.1, 0])
        self.beat("Elasticsearch indexes every word instead. That costs more disk and memory, and in return finds a word across all logs faster. Loki stays cheap to run.",
                  FadeIn(es, shift=UP * 0.1), run_time=2.6)
        self.play(FadeOut(es), FadeOut(cl), run_time=0.5)

        # ---- 3. a query: labels first, then scan the text
        q = M('{service_name="web"}', 24, YELLOW_M).move_to([0, 3.3, 0])
        self.beat("A LogQL query starts with a stream selector in braces. Loki adds a service_name label by itself, copied from service. So this picks the web stream.",
                  FadeIn(q, shift=DOWN * 0.1), Succession(Wait(4.2), AnimationGroup(labs[1:].animate.set_opacity(0.2), VGroup(*ms[1:]).animate.set_opacity(0.15),
                                                                                        chunks[1:].animate.set_opacity(0.15), Indicate(labs[0], color=TEAL_M))), run_time=7.4)
        self.beat("The labels picked one stream. Only its text gets scanned.",
                  Indicate(idx, color=BLUE_M, scale_factor=1.05), chunks[0].animate.set_stroke(YELLOW_M, width=3), run_time=2.0)

        # zoom into the web stream
        self.play(FadeOut(VGroup(conts, alloy, ca, push, pl, idx, idxl, labs[1:], lanes, *ms[1:], chunks[1:])), run_time=0.7)
        sbox = panel(7.2, 3.9, TEAL_M, [2.25, -0.55, 0], 0.05, 2)
        rows = VGroup(*[M(t, 20) for t, _, _ in LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(sbox)
        self.play(ReplacementTransform(VGroup(ms[0], chunks[0]), sbox), labs[0].animate.move_to(sbox.get_corner(UL) + UP * 0.3, aligned_edge=LEFT),
                  loki.animate.set_opacity(0.0), lokil.animate.set_opacity(0.0), run_time=1.0)
        self.beat("Inside that stream, the lines are plain text. The query's pipeline scans just these.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows], lag_ratio=0.2), run_time=3.0)

        # the pipeline, one step at a time (steps listed on the left)
        steps = VGroup(M('!= "/healthz"', 22, GOLD_M), M("| json", 22, GOLD_M), M("| status >= 500", 22, GOLD_M), M('| line_format', 22, GOLD_M))
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([-4.6, -0.5, 0]).align_to([-6.3, 0, 0], LEFT)
        head = T("pipeline", 24, GOLD_M).next_to(steps, UP, buff=0.45).align_to(steps, LEFT)
        sa = VGroup(*[Arrow(steps[i].get_bottom(), steps[i + 1].get_top(), buff=0.08, stroke_width=2, color=GREY_B, max_tip_length_to_length_ratio=0.3).align_to(steps[i], LEFT).shift(RIGHT * 0.25) for i in range(3)])
        hz = [i for i, (_, p, _) in enumerate(LINES) if p == "/healthz"]
        self.beat('Step one, a line filter. != "/healthz" drops every line that contains /healthz. The health checks are gone.',
                  FadeIn(head), FadeIn(steps[0], shift=RIGHT * 0.1), q.animate.become(M('{service_name="web"} != "/healthz"', 24, YELLOW_M).move_to([0, 3.3, 0])),
                  Succession(Wait(3.2), AnimationGroup(*[rows[i].animate.set_color(RED_M) for i in hz])), Succession(Wait(5.0), AnimationGroup(*[rows[i].animate.set_opacity(0.0) for i in hz])), run_time=6.6)
        keep = [i for i in range(len(LINES)) if i not in hz]
        kept = VGroup(*[rows[i] for i in keep])
        self.play(kept.animate.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(sbox), run_time=0.7)

        # | json: fields become labels for this query
        tbl = VGroup()
        for i in keep:
            _, p, s = LINES[i]
            tbl.add(VGroup(chip("method: GET", GOLD_M, 20, mono=True), chip(f"path: {p}", GOLD_M, 20, mono=True), chip(f"status: {s}", RED_M if s >= 500 else GOLD_M, 20, mono=True)).arrange(RIGHT, buff=0.2))
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(sbox)
        self.beat("Step two, | json. It parses each JSON line, so method, path, status and duration_ms become labels, for this query only.",
                  GrowArrow(sa[0]), FadeIn(steps[1], shift=RIGHT * 0.1), q.animate.become(M('{service_name="web"} != "/healthz" | json', 24, YELLOW_M).move_to([0, 3.3, 0])),
                  Succession(Wait(2.4), *[ReplacementTransform(kept[k], tbl[k], run_time=0.5) for k in range(len(keep))]), run_time=6.0)
        bad = [k for k, i in enumerate(keep) if LINES[i][2] >= 500]
        good = [k for k in range(len(keep)) if k not in bad]
        self.beat("Step three, a filter on a field: status greater than or equal to 500. Only the failed requests stay.",
                  GrowArrow(sa[1]), FadeIn(steps[2], shift=RIGHT * 0.1), q.animate.become(M('{service_name="web"} != "/healthz" | json | status >= 500', 24, YELLOW_M).move_to([0, 3.3, 0])),
                  Succession(Wait(3.0), AnimationGroup(*[tbl[k].animate.set_opacity(0.0) for k in good])), run_time=5.0)
        fails = VGroup(*[tbl[k] for k in bad])
        self.play(fails.animate.arrange(DOWN, buff=0.35).move_to(sbox), run_time=0.6)
        outs = VGroup(*[M("GET / -> 500", 26, RED_M) for _ in bad]).arrange(DOWN, buff=0.45).move_to(sbox)
        lf = M('| line_format "{{.method}} {{.path}} -> {{.status}}"', 20, GOLD_M).move_to([2.25, 1.85, 0])
        self.beat("Step four, line_format, rewrites each line from its fields. Now each one reads GET slash, arrow, 500. Easy to scan.",
                  GrowArrow(sa[2]), FadeIn(steps[3], shift=RIGHT * 0.1), FadeIn(lf), Succession(Wait(2.6), *[ReplacementTransform(fails[k], outs[k], run_time=0.6) for k in range(len(bad))]), run_time=5.4)
        cheap = VGroup(T("cheapest first:", 22, GREY_B), T("line filter before the parser", 22, YELLOW_M)).arrange(DOWN, buff=0.08, aligned_edge=LEFT).next_to(steps, DOWN, buff=0.4).align_to(steps, LEFT)
        self.beat("Put line filters before the parser. A plain text filter is the cheapest step, and every line it drops is a line the parser never touches.",
                  Indicate(steps[0], color=YELLOW_M), FadeIn(cheap, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(steps, sa, head, cheap, outs, lf, q, sbox, labs[0])), run_time=0.7)

        # ---- 4. cardinality: a label with endless values
        loki2 = panel(8.2, 4.3, BLUE_M, [2.4, -0.1, 0], 0.04, 2)
        idx2 = panel(2.6, 1.1, BLUE_M, [4.95, 1.45, 0], 0.12, 2)
        il2 = VGroup(T("index:", 22, BLUE_M), T("1 label set", 22, WHITE)).arrange(DOWN, buff=0.08).move_to(idx2)
        one = M('{service="web"}', 20, TEAL_M).move_to([LX0, 0.0, 0], aligned_edge=LEFT)
        onem = marks(9, LX0 + 3.1, 0.0, TEAL_M)
        self.beat("One last rule, and it matters most. Here is the web stream again.",
                  FadeIn(loki2), FadeIn(idx2), FadeIn(il2), FadeIn(one), FadeIn(onem), run_time=2.0)
        stack = VGroup(*[M(f'user_id="{1000 + 7 * k}"', 20, TEAL_M) for k in range(8)]).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([LX0, -0.6, 0], aligned_edge=LEFT)
        dotsv = M("...", 22, TEAL_M).next_to(stack, DOWN, buff=0.08).align_to(stack, LEFT)
        tiny = VGroup(*[marks(1, LX0 + 3.1 + (k % 3) * 0.34, s.get_y(), TEAL_M) for k, s in enumerate(stack)])
        il3 = VGroup(T("index:", 22, BLUE_M), T("thousands of sets", 22, RED_M)).arrange(DOWN, buff=0.08).move_to(idx2)
        self.beat("Every new label value makes a new stream. Put a user ID in a label, and one stream becomes thousands of tiny ones.",
                  Succession(Wait(2.6), AnimationGroup(ReplacementTransform(one, stack), FadeIn(dotsv), ReplacementTransform(onem, tiny), Transform(il2, il3))), run_time=6.0)
        slow = T("Loki slows down, and fills its index with tiny chunks", 22, RED_M).move_to([2.4, -2.75, 0])
        self.beat("Loki slows down, and fills its index with tiny chunks.",
                  FadeIn(slow, shift=UP * 0.1), Indicate(idx2, color=RED_M, scale_factor=1.06), run_time=2.4)
        self.play(FadeOut(VGroup(stack, dotsv, tiny, slow)), run_time=0.6)

        good_l = VGroup(T("good labels:", 24, GREEN_M), M("service  environment  cluster  container", 20, GREEN_M)).arrange(RIGHT, buff=0.3)
        bad_l = VGroup(T("bad labels:", 24, RED_M), M("request ID  user ID  IP address", 20, RED_M)).arrange(RIGHT, buff=0.3)
        filt = VGroup(T("IDs stay in the line:", 24, GREY_B), M('|= "req-42"', 22, YELLOW_M)).arrange(RIGHT, buff=0.3)
        rules = VGroup(good_l, bad_l, filt).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([2.4, -0.4, 0])
        self.beat("So keep labels few: service, environment, cluster, container. Never a request ID, a user ID, or an IP address. Keep those in the line itself, where a filter finds them.",
                  Transform(il2, VGroup(T("index:", 22, BLUE_M), T("a few label sets", 22, WHITE)).arrange(DOWN, buff=0.08).move_to(idx2)),
                  FadeIn(good_l, shift=UP * 0.1), Succession(Wait(4.4), FadeIn(bad_l, shift=UP * 0.1)), Succession(Wait(7.4), FadeIn(filt, shift=UP * 0.1)), run_time=10.0)
        self.play(FadeOut(VGroup(rules, loki2, idx2, il2)), run_time=0.6)

        # ---- recap
        rec = VGroup(T("Labels pick the streams.", 32, BLUE_M), T("A pipeline scans just their text.", 32, GOLD_M),
                     T("Keep labels few, and the text stays cheap.", 32)).arrange(DOWN, buff=0.35).move_to([0, 0.2, 0])
        self.beat("In Loki, labels pick the streams, and a pipeline scans just their text. Keep labels few, and the text stays cheap.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rec], lag_ratio=0.6), run_time=6.0)
        self.wait(1.2)
