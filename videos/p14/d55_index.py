import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bredis\.exceptions\.ConnectionError\b", "redis dot exceptions dot connection error"), (r"\bConnectionError\b", "connection error"),
    (r"\bFluent Bit\b", "fluent bit"), (r"\bfluentd\b", "fluent D"), (r"\bKibana\b", "kibbana"), (r"\b24224\b", "two four two two four"),
    (r"\b14:02\b", "two minutes past two"), (r"\bgrep\b", "grep"),
])


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def pod(color=TEAL_M):
    return Circle(radius=0.32, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1)


def card(i, msg, extra, color=GREY_B):
    t = M(msg, 20)
    head = VGroup(M(f"doc {i}", 20, GREY_B), M(extra, 20, color)).arrange(RIGHT, buff=0.3)
    inner = VGroup(head, t).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    r = RoundedRectangle(corner_radius=0.1, width=6.5, height=inner.height + 0.32, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.06), 1)
    inner.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.2)
    inner.set_z_index(2)
    return VGroup(r, inner)


TOKENS = [("payment", [1, 2]), ("failed", [1]), ("for", [1, 2]), ("order", [1, 2]), ("42", [1]),
          ("card", [1]), ("declined", [1]), ("accepted", [2]), ("43", [2])]


class D55Index(VoiceScene):
    def construct(self):
        self.title_card("How Elasticsearch finds a log line", "one home for every log, and an index of every word")

        # ---- 1. the problem: the pod is gone, and its logs with it
        nodes = VGroup(*[RoundedRectangle(corner_radius=0.12, width=3.0, height=2.0, stroke_color=GREY_B, stroke_width=2) for _ in range(3)]).arrange(RIGHT, buff=0.6).move_to([0, 0.3, 0])
        nl = VGroup(*[T(f"node {i + 1}", 22, GREY_B).next_to(n, UP, buff=0.15) for i, n in enumerate(nodes)])
        pods = VGroup(*[pod().move_to(n.get_center() + UP * 0.25) for n in nodes])
        logs = VGroup(*[VGroup(*[Line(LEFT * 0.7, RIGHT * (0.7 - 0.25 * k), stroke_width=3, color=GREY_B) for k in range(3)]).arrange(DOWN, buff=0.1, aligned_edge=LEFT).next_to(p, DOWN, buff=0.22) for p in pods])
        self.beat("Picture hello-devops on Kubernetes: three pods on three nodes, replaced on every deploy. Each pod prints its own log lines.",
                  Create(nodes), FadeIn(nl), LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.3), Succession(Wait(3.4), LaggedStart(*[Create(l) for l in logs], lag_ratio=0.3)), run_time=6.0)
        ask = T("a payment failed at 14:02. Which pod handled it?", 28, YELLOW_M).move_to([0, 2.7, 0])
        self.beat("A customer says a payment failed at 14:02. Which pod handled it?",
                  FadeIn(ask, shift=DOWN * 0.1), run_time=2.4)
        self.beat("That pod may not exist any more, and its logs left with it.",
                  pods[1].animate.set_opacity(0.15), logs[1].animate.set_opacity(0.1), run_time=2.4)
        self.play(FadeOut(VGroup(nodes, nl, pods, logs, ask)), run_time=0.6)

        # ---- 2. one road for every line
        names = [("hello-devops", TEAL_M), ("Docker engine", GREY_B), ("Fluent Bit", GOLD_M), ("Elasticsearch", PURPLE_M), ("Kibana", GREEN_M)]
        road = VGroup(*[box(n, c, w=2.25, h=0.75, size=22) for n, c in names]).arrange(RIGHT, buff=0.45).move_to([0, 2.65, 0])
        ra = VGroup(*[Arrow(road[i].get_right(), road[i + 1].get_left(), buff=0.05, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.35) for i in range(3)])
        ka = Arrow(road[4].get_left(), road[3].get_right(), buff=0.05, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.35)
        subs = VGroup(T("prints to stdout", 20, GREY_B), T("fluentd driver", 20, GREY_B), T("parses to fields", 20, GREY_B), T("indexes", 20, GREY_B), T("you search", 20, GREY_B))
        for s, b in zip(subs, road):
            s.next_to(b, DOWN, buff=0.15)
        self.beat("Centralized logging fixes this. Every line every container prints is copied, as it is written, to one store you can search.",
                  FadeIn(road[3], shift=UP * 0.1), run_time=2.4)
        self.beat("In the lab, hello-devops prints one event per line to stdout.",
                  FadeIn(road[0]), FadeIn(subs[0]), run_time=1.8)
        line = M('{"level":"INFO",...,"path":"/","status":200,"duration_ms":8}', 20, TEAL_M).move_to([0, 0.6, 0])
        self.beat("The access log is structured: one JSON object per line, with named fields.",
                  FadeIn(line, shift=UP * 0.1), run_time=2.0)
        self.beat("The Docker engine sees every line first. Its fluentd logging driver sends each one to Fluent Bit, on port 24224.",
                  FadeIn(road[1]), FadeIn(subs[1]), GrowArrow(ra[0]), Succession(Wait(2.4), AnimationGroup(FadeIn(road[2]), FadeIn(subs[2]), GrowArrow(ra[1]))), run_time=5.0)
        fields = VGroup(*[chip(t, GOLD_M, 20, mono=True) for t in ('level: INFO', 'path: /', 'status: 200', 'duration_ms: 8')]).arrange(RIGHT, buff=0.25).move_to(line)
        self.beat("Fluent Bit parses the JSON into fields, and sends them on to Elasticsearch, which indexes every field so search is fast.",
                  ReplacementTransform(line, fields), Succession(Wait(2.6), AnimationGroup(GrowArrow(ra[2]), FadeIn(subs[3]))), run_time=5.0)
        self.beat("Kibana is the web page where you search. The pod can be gone, and you can still read what it printed.",
                  FadeIn(road[4]), FadeIn(subs[4]), GrowArrow(ka), Succession(Wait(1.0), travel(ra[0], TEAL_M, 0.6), travel(ra[1], TEAL_M, 0.6), travel(ra[2], GOLD_M, 0.6)), run_time=4.6)
        self.play(FadeOut(fields), run_time=0.5)

        # ---- 3. grep reads everything, every time
        self.play(Indicate(road[3], color=PURPLE_M, scale_factor=1.06), FadeOut(subs), run_time=0.8)
        docs = VGroup(card(1, "Payment FAILED for order 42: card declined", "ERROR", RED_M),
                      card(2, "Payment accepted for order 43", "INFO", GREEN_M),
                      card(3, "Cart 7 is slow to load", "WARN", GOLD_M)).arrange(DOWN, buff=0.25).move_to([-3.5, -0.8, 0])
        self.beat("Inside Elasticsearch, each log event is one JSON document. Here are three.",
                  LaggedStart(*[FadeIn(d, shift=RIGHT * 0.15) for d in docs], lag_ratio=0.3), run_time=2.6)
        scan = Line([-6.65, 0, 0], [-0.35, 0, 0], stroke_width=4, color=YELLOW_M).move_to(docs[0].get_top() + DOWN * 0.05)
        gl = T("grep: read every line, on every search", 24, YELLOW_M).move_to([3.4, -0.2, 0])
        self.beat("With grep, every search reads every line again. Fine for one file, far too slow for a week of logs from fifty pods.",
                  FadeIn(gl), Succession(FadeIn(scan, run_time=0.2), scan.animate(run_time=2.4, rate_func=linear).move_to(docs[2].get_bottom() + UP * 0.05),
                                         scan.animate(run_time=0.1).move_to(docs[0].get_top() + DOWN * 0.05), scan.animate(run_time=2.4, rate_func=linear).move_to(docs[2].get_bottom() + UP * 0.05),
                                         FadeOut(scan, run_time=0.2)), run_time=6.0)
        self.play(FadeOut(gl), run_time=0.4)

        # ---- 4. the analyzer and the inverted index
        once = T("read once, when it arrives", 26, PURPLE_M).move_to([3.4, 1.3, 0])
        self.beat("Elasticsearch does the reading once, when a document arrives.",
                  FadeIn(once), run_time=1.6)
        toks1 = VGroup(*[chip(t, PURPLE_M, 20, mono=True) for t, _ in TOKENS[:7]])
        toks1.arrange_in_grid(rows=2, buff=(0.18, 0.2)).move_to([3.4, 0.0, 0])
        msg1 = docs[0][1][1]
        self.beat("A part called the analyzer splits each text field into words, called tokens, and lowercases them.",
                  docs[0][0].animate.set_stroke(PURPLE_M, width=4), run_time=1.2)
        self.beat("Payment FAILED becomes payment, failed, and so on.",
                  LaggedStart(*[FadeIn(t, shift=RIGHT * 0.4) for t in toks1], lag_ratio=0.2), run_time=2.6)

        # the index: token -> documents
        rows = VGroup()
        for t, ds in TOKENS:
            r = VGroup(M(t, 20, PURPLE_M), M(" ".join(str(d) for d in ds), 20, WHITE))
            rows.add(r)
        colA, colB = rows[:5], rows[5:]
        for col, x0 in ((colA, 0.55), (colB, 3.75)):
            for k, r in enumerate(col):
                r[0].move_to([x0, 0.65 - k * 0.48, 0], aligned_edge=LEFT)
                r[1].move_to([x0 + 1.75, 0.65 - k * 0.48, 0], aligned_edge=LEFT)
        hdr = VGroup(T("token", 22, GREY_B).move_to([0.55, 1.2, 0], aligned_edge=LEFT), T("in docs", 22, GREY_B).move_to([2.3, 1.2, 0], aligned_edge=LEFT),
                     T("token", 22, GREY_B).move_to([3.75, 1.2, 0], aligned_edge=LEFT), T("in docs", 22, GREY_B).move_to([5.5, 1.2, 0], aligned_edge=LEFT))
        ttl = T("the inverted index", 26, PURPLE_M).move_to([3.4, 1.75, 0])
        self.beat("Then, for every token, it records which documents contain it. That list is called an inverted index.",
                  FadeOut(once), FadeIn(ttl), FadeIn(hdr), docs[0][0].animate.set_stroke(GREY_B, width=2),
                  *[AnimationGroup(FadeOut(toks1[i][0]), ReplacementTransform(toks1[i][1], rows[i][0])) for i in range(7)],
                  Succession(Wait(2.0), LaggedStart(*[FadeIn(rows[i][1]) for i in range(7)], lag_ratio=0.2)), run_time=5.0)
        msg2 = docs[1][1][1]
        self.beat("The second document adds its own tokens, and its number to the rows it shares.",
                  FadeIn(rows[7]), FadeIn(rows[8]),
                  *[Indicate(rows[i][1], color=WHITE) for i in (0, 2, 3)], run_time=3.6)

        # ---- 5. searches
        def query(text, color=YELLOW_M):
            return VGroup(T("search:", 22, GREY_B), M(text, 22, color)).arrange(RIGHT, buff=0.2).move_to([2.6, -2.25, 0])

        def light_docs(ids, color=YELLOW_M):
            return [docs[i - 1][0].animate.set_stroke(color, width=4) for i in ids]

        def unlight():
            return [d[0].animate.set_stroke(GREY_B, width=2) for d in docs]

        q1 = query("declined")
        h1 = SurroundingRectangle(rows[6], buff=0.08, color=YELLOW_M, stroke_width=2.5)
        self.beat("It works like the index at the back of a book. To find declined, you look it up once, instead of reading every page.",
                  FadeIn(q1, shift=UP * 0.1), Succession(Wait(2.4), Create(h1)), Succession(Wait(3.6), AnimationGroup(*light_docs([1]))), run_time=5.6)
        q2 = query("payment")
        self.beat("Search payment: one lookup, two documents.",
                  Transform(q1, q2), h1.animate.become(SurroundingRectangle(rows[0], buff=0.08, color=YELLOW_M, stroke_width=2.5)), *light_docs([1, 2]), run_time=2.0)
        q3 = query("payments", RED_M)
        zero = VGroup(T("0 hits", 24, RED_M), tick(False, 0.14)).arrange(RIGHT, buff=0.2).next_to(q2, RIGHT, buff=0.4)
        self.beat("Coming from grep, this is the first surprise. Search payments, and you get nothing.",
                  Transform(q1, q3), FadeOut(h1), *unlight(), Succession(Wait(2.4), FadeIn(zero)), run_time=3.6)
        self.beat("Only payment was stored. The default analyzer does not reduce words to a common stem, so payments is a token nobody ever wrote.",
                  Indicate(rows[0][0], color=PURPLE_M, scale_factor=1.15), run_time=2.4)
        self.play(FadeOut(zero), FadeOut(q1), run_time=0.4)

        # the dotted error name stays one token
        err = VGroup(M("redis.exceptions.ConnectionError: ...", 20, RED_M), M("... service not known", 20, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([3.4, 0.7, 0])
        etok = VGroup(chip("redis.exceptions.connectionerror", PURPLE_M, 20, mono=True),
                      VGroup(chip("service", PURPLE_M, 20, mono=True), chip("not", PURPLE_M, 20, mono=True), chip("known", PURPLE_M, 20, mono=True)).arrange(RIGHT, buff=0.15)).arrange(DOWN, buff=0.2)
        self.play(FadeOut(VGroup(rows, hdr, ttl)), docs.animate.shift(UP * 0.35), run_time=0.6)
        self.beat("The second surprise. When Redis is down, a traceback line holds redis.exceptions.ConnectionError.",
                  FadeIn(err, shift=UP * 0.1), run_time=1.8)
        etok.move_to([3.4, -0.75, 0])
        self.beat("Dots between letters do not split words. So the whole name stays one token.",
                  FadeIn(etok[0], shift=DOWN * 0.2), Succession(Wait(1.2), FadeIn(etok[1], shift=DOWN * 0.2)), run_time=2.4)
        q4 = query("ConnectionError", RED_M)
        z4 = VGroup(T("0 hits", 24, RED_M), tick(False, 0.14)).arrange(RIGHT, buff=0.2).next_to(q4, RIGHT, buff=0.4)
        self.beat("Search ConnectionError, and you get zero hits. It is only part of a token.",
                  FadeIn(q4, shift=UP * 0.1), Succession(Wait(1.6), FadeIn(z4)), run_time=2.6)
        q5 = query('"service not known"', GREEN_M)
        ok5 = VGroup(T("found", 24, GREEN_M), tick(True, 0.16)).arrange(RIGHT, buff=0.2).next_to(q5, RIGHT, buff=0.4)
        self.beat("Search the phrase service not known, from the same error, and you find it at once.",
                  Transform(q4, q5), Transform(z4, ok5), Indicate(etok[1], color=GREEN_M, scale_factor=1.06), run_time=3.0)
        self.play(FadeOut(VGroup(err, etok, q4, z4)), run_time=0.5)

        # keyword fields stay whole
        kw = VGroup(T("level is a keyword field: stored whole", 24, GOLD_M), chip("ERROR", GOLD_M, 22, mono=True)).arrange(DOWN, buff=0.3).move_to([3.4, 0.4, 0])
        self.beat("Not every field is split. A keyword field, such as level, is stored whole, capitals and all, for exact filters and counting.",
                  FadeIn(kw[0]), Succession(Wait(1.4), FadeIn(kw[1], shift=RIGHT * 0.2)), Succession(Wait(2.4), Indicate(docs[0][1][0][1], color=GOLD_M)), run_time=4.8)
        q6 = query("level: error", RED_M)
        z6 = VGroup(T("0 hits", 24, RED_M), tick(False, 0.14)).arrange(RIGHT, buff=0.2).next_to(q6, RIGHT, buff=0.4)
        self.beat("The stored value is ERROR, in capitals. So a term query for error, in lower case, finds nothing.",
                  FadeIn(q6, shift=UP * 0.1), Succession(Wait(2.4), FadeIn(z6)), run_time=4.0)
        self.play(FadeOut(VGroup(kw, q6, z6)), run_time=0.5)

        # ---- recap
        rec = VGroup(T("each line is read once, when it arrives,", 24), T("into an index of whole tokens", 24, PURPLE_M),
                     T("so search for words that were really stored", 24, YELLOW_M)).arrange(DOWN, buff=0.25).move_to([3.4, -0.4, 0])
        self.beat("Elasticsearch reads each log line once, when it arrives, and builds an index of whole tokens. So search for words that were really stored, and check the tokens before you trust an empty result.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rec], lag_ratio=0.6), run_time=8.0)
        self.wait(1.2)
