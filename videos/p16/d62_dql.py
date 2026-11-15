import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bDQL\b", "D Q L"), (r"\bSQL\b", "sequel"), (r"\bfieldsAdd\b", "fields add"), (r"\bcountIf\b", "count if"),
    (r"\berror_pct\b", "error percent"), (r"\bavg_ms\b", "average M S"), (r"\bfrom: -1h\b", "from minus one hour"),
    (r"\bfrom: -30d\b", "from minus thirty days"), (r"\bDynatrace\b", "dyna-trace"), (r"/healthz\b", "health Z"), (r"/readyz\b", "ready Z"),
    (r">=", "greater than or equal to"), (r"(?<=\s)/(?=[\s,.]|$)", "slash"), (r"==", "double equals"), (r"\bdesc\b", "descending"),
])

DATA = [("/", 200, 12), ("/", 200, 18), ("/", 200, 20), ("/", 500, 350), ("/healthz", 200, 2), ("/readyz", 503, 1001)]
COLX = [1.0, 2.35, 3.6, 4.85, 6.0]
HY, RY0, RS = 2.35, 1.8, 0.47
QX = -6.35


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def cell(v, x, y, color=WHITE):
    return M(str(v), 20, color).move_to([x, y, 0])


def row(vals, y, color=WHITE):
    return VGroup(*[cell(v, COLX[i], y, color) for i, v in enumerate(vals)])


def header(names):
    return VGroup(*[M(n, 20, GREY_B).move_to([COLX[i], HY, 0]) for i, n in enumerate(names)])


def ql(text, y, color=WHITE):
    return M(text, 20, color).move_to([QX, y, 0], aligned_edge=LEFT)


class D62Dql(VoiceScene):
    def construct(self):
        self.title_card("A DQL query is a pipeline", "records flow down, one command at a time")

        # ---- 1. the SQL habit
        sql = VGroup(M("SELECT path, count(*)", 24, BLUE_M), M("FROM logs", 24, BLUE_M), M("WHERE status >= 500", 24, BLUE_M), M("GROUP BY path", 24, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        sql.move_to([-3.4, 0.3, 0])
        sl = T("SQL: the database picks the order", 24, BLUE_M).next_to(sql, UP, buff=0.4)
        self.beat("If you think in SQL, you write SELECT first, and the database picks the order it really runs in.",
                  FadeIn(sl), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in sql], lag_ratio=0.25), run_time=4.0)
        dq = VGroup(M("fetch logs", 24, TEAL_M), M("| filter status >= 500", 24, TEAL_M), M("| summarize n = count(), by: {path}", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        dq.move_to([3.0, 0.3, 0])
        dl = T("DQL: top to bottom, in the order it runs", 24, TEAL_M).next_to(dq, UP, buff=0.4)
        down = Arrow(dq.get_corner(UR) + RIGHT * 0.3, dq.get_corner(DR) + RIGHT * 0.3, buff=0, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.2)
        self.beat("DQL, the Dynatrace Query Language, reads top to bottom, in the order it runs. That is the biggest change.",
                  FadeIn(dl), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in dq], lag_ratio=0.25), Succession(Wait(3.0), GrowArrow(down)), run_time=5.4)
        self.play(FadeOut(VGroup(sql, sl, dq, dl, down)), run_time=0.6)

        # ---- 2. Grail and the pipe
        grail = box("Grail", PURPLE_M, w=2.6, h=0.9, size=32).move_to([-4.2, 0.4, 0])
        kinds = VGroup(*[chip(k, PURPLE_M, 22) for k in ("logs", "spans", "events", "problems", "metrics")]).arrange(RIGHT, buff=0.25).move_to([1.6, 0.4, 0])
        self.beat("Grail is the store behind everything in Dynatrace. It keeps logs, spans, events, problems and metrics side by side, and you read all of it with DQL.",
                  FadeIn(grail), Succession(Wait(2.4), LaggedStart(*[FadeIn(k, shift=LEFT * 0.1) for k in kinds], lag_ratio=0.3)), run_time=6.0)
        pipe = T("the first command produces records; each | hands them to the next", 24, GREY_B).move_to([0, -1.2, 0])
        self.beat("A DQL query is a pipeline, like a shell pipeline. The first command produces records. Each pipe hands them to the next command, which filters, reshapes or counts them.",
                  FadeIn(pipe, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(grail, kinds, pipe)), run_time=0.6)

        # ---- 3. data: six records
        q = VGroup(ql('data record(path = "/", status = 200,', 2.35, TEAL_M), ql('            ms = 12), ...  6 records', 1.95, TEAL_M))
        hd = header(["path", "status", "ms"])
        rows = VGroup(*[row(r, RY0 - i * RS) for i, r in enumerate(DATA)])
        sep = Line([0.3, HY - 0.27, 0], [6.6, HY - 0.27, 0], stroke_width=1.5, color=GREY_D)
        self.beat("Start with the data command. It builds a small table inside the query. Six records, with path, status and ms. Grail scans nothing, so everyone gets the same result.",
                  FadeIn(q, shift=RIGHT * 0.1), Succession(Wait(2.6), AnimationGroup(FadeIn(hd), Create(sep), LaggedStart(*[FadeIn(r, shift=LEFT * 0.15) for r in rows], lag_ratio=0.2))), run_time=7.0)
        cnt = T("6 rows", 24, GREY_B).move_to([3.5, -1.3, 0])
        self.play(FadeIn(cnt), run_time=0.4)

        # ---- 4. filter
        f = ql("| filter status >= 500", 1.4, GOLD_M)
        self.beat("Add a filter on a new line. Records flow down the pipe, and filter keeps the ones where the condition is true.",
                  FadeIn(f, shift=DOWN * 0.1), Succession(Wait(3.0), travel(Line([QX - 0.15, 2.35, 0], [QX - 0.15, 1.4, 0]), GOLD_M, 0.8)), run_time=4.6)
        drop = [0, 1, 2, 4]
        self.beat("Only two records have a status of 500 or more. The others stop here.",
                  *[rows[i].animate.set_opacity(0.15) for i in drop], *[rows[i][1].animate.set_color(GOLD_M) for i in (3, 5)],
                  Transform(cnt, T("2 rows", 24, GOLD_M).move_to(cnt)), run_time=2.4)
        eq = VGroup(M(">=", 24, GOLD_M), T("compares.", 24, GREY_B), M("==", 24, GOLD_M), T("tests equality. A single", 24, GREY_B), M("=", 24, RED_M), T("only names a field.", 24, GREY_B)).arrange(RIGHT, buff=0.15)
        eq.move_to([0, -2.6, 0])
        self.beat("Note the operators. Equality in DQL is ==. A single = gives a field a name, as you will see next.",
                  FadeIn(eq, shift=UP * 0.1), run_time=2.8)
        self.play(FadeOut(eq), *[rows[i].animate.set_opacity(1) for i in drop], *[rows[i][1].animate.set_color(WHITE) for i in (3, 5)], FadeOut(cnt), run_time=0.6)

        # ---- 5. summarize
        s = VGroup(ql("| summarize requests = count(),", 1.4, GOLD_M), ql("    errors = countIf(status >= 500),", 1.0, GOLD_M), ql("    avg_ms = avg(ms), by: {path}", 0.6, GOLD_M))
        self.beat("Now replace the filter with summarize. It groups the records by path, and computes one row per group.",
                  ReplacementTransform(f, s), run_time=2.4)
        groups = {"/": [0, 1, 2, 3], "/healthz": [4], "/readyz": [5]}
        gcol = {"/": TEAL_M, "/healthz": BLUE_M, "/readyz": RED_M}
        self.beat("Four records share the path /. One each have /healthz and /readyz.",
                  *[rows[i].animate.set_color(gcol[DATA[i][0]]) for i in range(6)], run_time=2.0)
        hd2 = header(["path", "requests", "errors", "avg_ms"])
        out = [("/", 4, 1, 100), ("/healthz", 1, 0, 2), ("/readyz", 1, 1, 1001)]
        orows = VGroup(*[row(r, RY0 - i * RS, gcol[r[0]]) for i, r in enumerate(out)])
        self.beat("The four records of / fold into one row: 4 requests, 1 error, and an average of 100 milliseconds.",
                  ReplacementTransform(hd, hd2), ReplacementTransform(VGroup(*[rows[i] for i in groups["/"]]), orows[0]),
                  ReplacementTransform(rows[4], orows[1]), ReplacementTransform(rows[5], orows[2]), run_time=3.0)
        nm = VGroup(T("each result gets a name with one", 24, GREY_B), M("=", 24, GOLD_M), T(", and", 24, GREY_B), M("by: {path}", 24, GOLD_M), T("sits in braces", 24, GREY_B)).arrange(RIGHT, buff=0.15)
        nm.move_to([0, -2.6, 0])
        self.beat("Each result gets a name with a single =. And the by list sits in braces.",
                  FadeIn(nm, shift=UP * 0.1), Indicate(s[0], color=GOLD_M, scale_factor=1.03), Succession(Wait(2.4), Indicate(s[2], color=GOLD_M, scale_factor=1.03)), run_time=4.0)
        self.play(FadeOut(nm), run_time=0.4)

        # ---- 6. fieldsAdd and sort
        fa = ql("| fieldsAdd error_pct = errors * 100.0 / requests", 0.2, GOLD_M)
        fit(fa, 6.1).move_to([QX, 0.2, 0], aligned_edge=LEFT)
        hd3 = header(["path", "requests", "errors", "avg_ms", "error_pct"])
        pct = VGroup(*[cell(v, COLX[4], RY0 - i * RS, YELLOW_M) for i, v in enumerate((25, 0, 100))])
        self.beat("Add a computed field. fieldsAdd keeps every column, and adds one: errors times 100, divided by requests.",
                  FadeIn(fa, shift=DOWN * 0.1), Transform(hd2, hd3), Succession(Wait(3.0), LaggedStart(*[FadeIn(p, shift=LEFT * 0.1) for p in pct], lag_ratio=0.3)), run_time=5.4)
        so = ql("| sort error_pct desc", -0.2, GOLD_M)
        order = [2, 0, 1]
        self.beat("Then sort by the name you gave it. The worst path comes first: /readyz at 100 percent, / at 25, /healthz at 0.",
                  FadeIn(so, shift=DOWN * 0.1),
                  Succession(Wait(1.6), AnimationGroup(*[VGroup(orows[k], pct[k]).animate.move_to([VGroup(orows[k], pct[k]).get_x(), RY0 - order.index(k) * RS, 0]) for k in range(3)])),
                  run_time=5.0)
        tail = T("sort by the name, never by an expression", 24, GREY_B).move_to([3.5, -0.4, 0])
        self.play(FadeIn(tail), run_time=0.5)
        self.wait(0.6)

        # ---- 7. order matters
        self.play(FadeOut(tail), run_time=0.4)
        late = ql("| filter status >= 500", -0.6, RED_M)
        gone = T("after summarize, status no longer exists", 24, RED_M).move_to([3.5, -0.6, 0])
        self.beat("Order matters. A command only sees what the one before it passed on. After summarize, only the summarized fields exist.",
                  FadeIn(late, shift=DOWN * 0.1), Succession(Wait(3.6), FadeIn(gone)), Indicate(hd2, color=RED_M, scale_factor=1.03), run_time=5.4)
        first = T("so filter first", 24, GREEN_M).next_to(gone, DOWN, buff=0.25)
        self.beat("So filter first. And watch out: several SQL habits do not even fail. They quietly return zero rows, and zero rows looks like no errors.",
                  FadeIn(first), run_time=2.6)
        self.play(FadeOut(VGroup(late, gone, first)), run_time=0.5)

        # ---- 8. the same commands on real logs
        fetch = ql("fetch logs, from: -1h", 2.15, TEAL_M)
        self.beat("Now put fetch logs, from minus one hour, where data was. The same commands work on real logs.",
                  ReplacementTransform(q, fetch), FadeOut(VGroup(orows, pct)), run_time=2.6)
        only = T("only the first line changed", 24, TEAL_M).move_to([3.5, 1.3, 0])
        self.beat("Only the first line changed. The commands below it do not care where the records came from.",
                  Indicate(fetch, color=TEAL_M, scale_factor=1.04), FadeIn(only), run_time=2.6)

        # ---- 9. what it costs: the scan happens at the top
        sack1 = Rectangle(width=0.7, height=0.5, stroke_color=TEAL_M, stroke_width=2.5).set_fill(TEAL_M, 0.35).move_to([1.4, -1.3, 0])
        sack2 = Rectangle(width=4.6, height=1.3, stroke_color=RED_M, stroke_width=2.5).set_fill(RED_M, 0.25).move_to([4.2, -1.5, 0])
        l1 = M("-1h", 22, TEAL_M).next_to(sack1, DOWN, buff=0.15)
        l2 = M("-30d", 22, RED_M).next_to(sack2, DOWN, buff=0.15)
        self.beat("Grail charges queries by the data they scan. And the scan happens in the first command.",
                  FadeOut(only), Indicate(fetch, color=GOLD_M, scale_factor=1.04), run_time=2.4)
        self.beat("One hour of logs is a small scan. from minus thirty days, over all logs, costs real money on a paid environment.",
                  FadeIn(sack1), FadeIn(l1), Succession(Wait(2.4), AnimationGroup(GrowFromEdge(sack2, LEFT), FadeIn(l2))), run_time=5.2)
        short = T("use the shortest window that answers the question", 26, YELLOW_M).move_to([0, -3.15, 0])
        self.beat("So a narrow time window at the start matters more than anything later in the pipe. Use the shortest window that answers the question.",
                  FadeIn(short, shift=UP * 0.1), run_time=2.6)
        self.play(FadeOut(VGroup(sack1, sack2, l1, l2, short, hd2, sep)), run_time=0.6)

        # ---- recap
        rec = VGroup(T("the first command fetches,", 30, TEAL_M), T("each pipe passes records on,", 30, GOLD_M), T("a short window keeps the scan small", 30, YELLOW_M)).arrange(DOWN, buff=0.3)
        rec.move_to([3.4, 0.6, 0])
        self.beat("Read DQL top to bottom. The first command fetches, each pipe passes the records on, and a short time window keeps the scan small.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rec], lag_ratio=0.6), run_time=6.0)
        self.wait(1.2)
