import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import fg as _fg


def box(*a, **k):  # keep the label drawn above its own filled outline, even when the outline is animated
    b = _fg.box(*a, **k); b[1].set_z_index(1); return b


def chip(*a, **k):
    c = _fg.chip(*a, **k); c[1].set_z_index(1); return c

SAY.extend([(r"\bDQL\b", "D Q L"), (r"\bSQL\b", "sequel"), (r"\bloglevel\b", "log level"), (r"\blog\.level\b", "log dot level"),
            (r"\bfieldsAdd\b", "fields add"), (r"\bcountIf\b", "count if"), (r"\bmakeTimeseries\b", "make time series"),
            (r"\b/healthz\b", "slash health Z"), (r"\b/readyz\b", "slash ready Z"), (r"\bcaseSensitive\b", "case sensitive")])

Q_C = BLUE_M        # the query text
ROW_C = TEAL_M      # records
DROP_C = GREY_D     # dropped records
BAD_C = RED_M
OK_C = GREEN_M
ASK_C = YELLOW_M
GRP_C = GOLD_M      # summarize groups

ROWS = [("/", 200, 12), ("/", 200, 18), ("/", 200, 20), ("/", 500, 350), ("/healthz", 200, 2), ("/readyz", 503, 1001)]


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def table(header, rows, x0=-3.2, y0=0.05, colw=None, dy=0.46, hc=GREY_B, rc=WHITE):
    colw = colw or [1.9] * len(header)
    xs = [x0 + sum(colw[:i]) for i in range(len(header))]
    hd = VGroup(*[M(h, 22, hc).move_to([x, y0, 0], aligned_edge=LEFT) for h, x in zip(header, xs)])
    rs = VGroup()
    for k, r in enumerate(rows):
        y = y0 - (k + 1) * dy
        cells = VGroup(*[M(str(v), 22, rc).move_to([x, y, 0], aligned_edge=LEFT) for v, x in zip(r, xs)])
        bg = Rectangle(width=sum(colw) - 0.1, height=dy - 0.08, stroke_width=0).set_fill(tint(ROW_C, 0.18), 1).move_to([x0 + (sum(colw) - 0.1) / 2 - 0.1, y, 0])
        rs.add(VGroup(bg, cells))
    return hd, rs


class D62Clerk(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def qline(self, s, k, c=Q_C):
        ind = (len(s) - len(s.lstrip(" "))) * 0.174
        return M(s.lstrip(" "), 24, c).move_to([-6.3 + ind, 3.05 - k * 0.42, 0], aligned_edge=LEFT)

    def construct(self):
        self.title_card("Zero rows is not proof", "how a DQL query really runs")

        # ---------- 1. the assistant and the clerk
        arch = VGroup(*[Rectangle(width=0.5, height=1.6, stroke_color=GREY_B, stroke_width=2) for _ in range(8)]).arrange(RIGHT, buff=0.08).move_to([3.6, 0.6, 0])
        al = T("the archive: every clue", 26, GREY_B).next_to(arch, UP, buff=0.2)
        ask = VGroup(T("assistant:", 26, ASK_C), M('level = error', 26)).arrange(RIGHT, buff=0.2).move_to([-3.3, 1.2, 0])
        self.beat("Picture the detective from last time, with a new assistant. The archive now holds every clue the building ever produced. The assistant is sharp, and fluent in the archive language of an old job.",
                  FadeIn(arch), FadeIn(al), run_time=3.0)
        self.beat("They ask the clerk for all reports where level equals error.",
                  FadeIn(ask, shift=RIGHT * 0.2), run_time=1.8)
        empty = VGroup(T("clerk:", 26, GREY_B), T("(nothing)", 26, GREY_B)).arrange(RIGHT, buff=0.2).move_to([-3.3, 0.2, 0])
        note = VGroup(T("case file:", 26, GREY_B), T("no errors this week", 26, OK_C)).arrange(RIGHT, buff=0.2).move_to([-3.3, -0.8, 0])
        self.beat("The clerk comes back empty-handed. The assistant writes in the case file: no errors this week.",
                  FadeIn(empty), Succession(Wait(1.8), FadeIn(note)), run_time=3.4)
        real = T("there were hundreds", 30, BAD_C).move_to([0, -2.3, 0])
        self.beat("In fact, there were hundreds. The clerk simply didn't understand the question, and said nothing.",
                  FadeIn(real, scale=1.2), note[1].animate.set_color(BAD_C), run_time=2.4)
        self.beat("That's the trap with a new query language. Old habits look right, and a wrong question often returns an empty answer instead of an error. Today, the clerk is Dynatrace, and the language is DQL.",
                  run_time=None)
        self.play(FadeOut(VGroup(arch, al, ask, empty, note, real)), run_time=0.6)

        # ---------- 2. familiar: a pipeline
        sh = M("cat access.log | grep 500 | sort", 28).move_to([0, 1.6, 0])
        self.beat("Start from something you already know, a shell pipeline. Each bar hands the lines to the next command, and you read it left to right, in the order it runs.",
                  Write(sh), run_time=2.6)
        sql = VGroup(T("SQL, the database language:", 26, GREY_B), M("SELECT ... FROM ... WHERE ...", 26)).arrange(RIGHT, buff=0.25).move_to([0, 0.2, 0])
        dql = T("DQL: a pipeline, read top to bottom, in the order it runs", 28, Q_C).move_to([0, -1.2, 0])
        self.beat("SQL, the common language for asking databases questions, works differently. SELECT comes first, and the database picks the order. DQL, the Dynatrace Query Language, is a pipeline again. Top to bottom, in the order it runs.",
                  FadeIn(sql), Succession(Wait(4.0), FadeIn(dql)), run_time=6.0)
        self.play(FadeOut(VGroup(sh, sql, dql)), run_time=0.6)

        # ---------- 3. shrink: a table you type
        q = [self.qline("data record(...), ...", 0)]
        qn = T("six records typed into the query", 24, GREY_B).move_to([3.3, 3.05, 0])
        hd, rs = table(["path", "status", "ms"], ROWS)
        self.beat("Let's take the smallest table possible. The data command builds six records right inside the query. Everyone gets the same result, and the store scans nothing.",
                  FadeIn(q[0]), FadeIn(qn), FadeIn(hd), LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in rs], lag_ratio=0.15), run_time=4.0)
        self.beat("Six made-up visits to a web app: a path, a status code, and how many milliseconds each one took.",
                  Indicate(hd, color=GREY_B), run_time=2.0)

        # predict the filter
        q.append(self.qline("| filter status >= 500", 1))
        self.beat("Add one line. Filter, status greater than or equal to 500, the server failures. How many records survive? Pause and guess.",
                  FadeIn(q[1], shift=DOWN * 0.1), run_time=2.4)
        self.pause([3.3, 2.2, 0])
        keep = [3, 5]
        self.beat("Two. The records flow down the pipe, and filter keeps only the ones where the test is true.",
                  *[rs[i].animate.set_opacity(0.15) for i in range(6) if i not in keep], *[Indicate(rs[i][1], color=ROW_C) for i in keep], run_time=2.6)
        self.beat("And notice the test: greater-or-equal. Plain equality, in DQL, is a double equals sign. Remember that, it comes back.",
                  Indicate(q[1], color=Q_C), run_time=2.4)

        # summarize
        sm = [self.qline("| summarize requests = count(),", 1), self.qline("    errors = countIf(status >= 500),", 2), self.qline("    avg_ms = avg(ms), by: {path}", 3)]
        self.beat("Now swap the filter for a summarize. It groups the records by path and makes one row per group.",
                  FadeOut(q[1]), *[rs[i].animate.set_opacity(1) for i in range(6)], LaggedStart(*[FadeIn(l) for l in sm], lag_ratio=0.3), run_time=3.0)
        grp = {"/": [0, 1, 2, 3], "/healthz": [4], "/readyz": [5]}
        ypos = {"/": -0.4, "/healthz": -1.8, "/readyz": -2.6}
        moves = []
        for k, idx in grp.items():
            for j, i in enumerate(idx):
                moves.append(rs[i].animate.move_to(rs[i].get_center() * [1, 0, 0] + [0.25 * j, ypos[k] - 0.12 * j, 0]))
        self.beat("Watch the four visits to slash gather into one pile. Slash healthz and slash readyz each make a pile of one.",
                  *moves, run_time=3.0)
        hd2, rs2 = table(["path", "requests", "errors", "avg_ms"], [("/", 4, 1, 100), ("/healthz", 1, 0, 2), ("/readyz", 1, 1, 1001)], colw=[1.9, 1.9, 1.7, 1.7])
        self.beat("Each pile becomes one row. Four requests on slash, one error, 100 milliseconds on average.",
                  ReplacementTransform(VGroup(*[rs[i] for i in grp["/"]]), rs2[0]), ReplacementTransform(rs[4], rs2[1]), ReplacementTransform(rs[5], rs2[2]),
                  Transform(hd, hd2), run_time=3.0)
        names = SurroundingRectangle(VGroup(*sm[0][10:19]), buff=0.06, color=GRP_C, stroke_width=2)
        braces = SurroundingRectangle(VGroup(*sm[2][-6:]), buff=0.06, color=GRP_C, stroke_width=2)
        self.beat("Two details carry over to every query. Each result gets its name with a single equals sign. And the by list sits in curly braces.",
                  Create(names), Succession(Wait(2.4), Create(braces)), run_time=3.6)
        self.play(FadeOut(names), FadeOut(braces), run_time=0.3)
        fa = [self.qline("| fieldsAdd error_pct =", 4), self.qline("    errors * 100.0 / requests", 5), self.qline("| sort error_pct desc", 6)]
        hd3, rs3 = table(["path", "requests", "errors", "avg_ms", "error_pct"], [("/readyz", 1, 1, 1001, 100), ("/", 4, 1, 100, 25), ("/healthz", 1, 0, 2, 0)], x0=-5.6, colw=[2.0, 2.2, 1.9, 1.9, 2.0])
        self.beat("Add a computed column, the error percentage, and sort by its name. The worst path rises to the top: slash readyz, one hundred percent.",
                  LaggedStart(*[FadeIn(l) for l in fa], lag_ratio=0.3), FadeOut(qn),
                  Succession(Wait(2.4), AnimationGroup(ReplacementTransform(rs2[2], rs3[0]), ReplacementTransform(rs2[0], rs3[1]), ReplacementTransform(rs2[1], rs3[2]), Transform(hd, hd3))), run_time=5.0)
        self.beat("Read it out loud: take the records, group them by path, count, add a percentage, worst first. Every line is one step, in order.",
                  LaggedStart(*[Indicate(l, color=Q_C, scale_factor=1.04) for l in [q[0], *sm, *fa]], lag_ratio=0.2), run_time=4.4)
        self.play(FadeOut(VGroup(q[0], *sm, *fa, hd, rs3)), run_time=0.6)

        # ---------- 4. habits that fail loudly, and one that fails silently
        hh = T("SQL habits, on purpose", 30, ASK_C).move_to([0, 3.0, 0])
        l1 = VGroup(M('| filter status = 500', 24), T("fails: = names a field, it does not compare", 24, BAD_C)).arrange(RIGHT, buff=0.4)
        l2 = VGroup(M('| summarize ..., by: path, status', 24), T("fails: the by list needs braces", 24, BAD_C)).arrange(RIGHT, buff=0.4)
        loud = VGroup(l1, l2).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit(loud, 12.6).move_to([0, 1.7, 0])
        self.beat("Now let's make the assistant's mistakes on purpose. A single equals sign in a filter. Without braces in the by list. Both runs fail, with an error message.",
                  FadeIn(hh), FadeIn(l1), Succession(Wait(2.2), FadeIn(l2)), run_time=4.4)
        self.beat("That's the good kind of mistake. It shouts, you read the message, you fix it.",
                  run_time=None)
        s1 = M('fetch logs, from: -1h', 24, Q_C)
        s2 = M('| filter log.level == "ERROR"', 24, Q_C)
        sq = VGroup(s1, s2).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([-2.8, -0.2, 0])
        self.beat("Now real logs. Fetch the last hour of log records, and filter where log dot level is ERROR. Equality is right this time, double equals. What comes back? Pause and guess.",
                  FadeIn(sq, shift=UP * 0.1), run_time=3.4)
        self.pause([3.2, -0.2, 0])
        zero = VGroup(T("0 records", 30, GREY_B), T("no error message", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([3.2, -0.2, 0])
        self.beat("Zero records. No error, no complaint. And the case file says: no errors this hour.",
                  FadeIn(zero, scale=1.1), run_time=2.4)
        self.beat("Well. The clerk didn't lie. There is simply no field called log dot level. The field is called loglevel, one word. A filter on a field that doesn't exist quietly keeps nothing.",
                  Indicate(VGroup(*s2[7:16]), color=BAD_C), run_time=3.2)
        peek = VGroup(M("| limit 10", 24, OK_C), T("shows the real field names:", 24), M("timestamp  loglevel  content", 24, OK_C)).arrange(RIGHT, buff=0.3)
        fit(peek, 12.6).move_to([0, -1.9, 0])
        self.beat("So start every new query with limit 10, and read the real field names first. Then add one command at a time, and check the row count after each.",
                  FadeIn(peek, shift=UP * 0.1), run_time=3.2)
        rule = T("Zero rows is not proof. Check the field names before you write \"no errors\".", 28, ASK_C).move_to([0, -2.9, 0])
        fit(rule, 12.6)
        self.beat("Zero rows is not proof. Check the field names before you write no errors.",
                  FadeIn(rule), run_time=2.4)
        self.play(FadeOut(VGroup(hh, loud, sq, zero, peek, rule)), run_time=0.6)

        # ---------- 5. order matters
        o1 = M('fetch logs', 24, Q_C)
        o2 = M('| summarize count(), by: {k8s.namespace.name}', 24, Q_C)
        o3 = M('| filter loglevel == "ERROR"', 24, BAD_C)
        oq = VGroup(o1, o2, o3).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([-2.4, 1.8, 0])
        self.beat("One more habit. In SQL, the database picks the order of the work. In DQL, you do. So what if we summarize first, and then filter on loglevel?",
                  FadeIn(oq), run_time=3.0)
        before = VGroup(M("loglevel", 22), M("content", 22), M("k8s.namespace.name", 22)).arrange(RIGHT, buff=0.35).move_to([0, -0.2, 0])
        bl = T("fields before summarize", 24, GREY_B).next_to(before, UP, buff=0.2)
        after = VGroup(M("k8s.namespace.name", 22, GRP_C), M("count()", 22, GRP_C)).arrange(RIGHT, buff=0.35).move_to([0, -1.6, 0])
        alb = T("fields after summarize", 24, GREY_B).next_to(after, UP, buff=0.2)
        self.beat("Follow the records down. Before summarize, each record has its loglevel. After summarize, only the summarized fields exist: the namespace and the count. The filter asks about a field that's gone.",
                  FadeIn(bl), FadeIn(before), Succession(Wait(2.6), AnimationGroup(FadeIn(alb), ReplacementTransform(before[2].copy(), after[0]), FadeIn(after[1]))),
                  Succession(Wait(5.0), Indicate(o3, color=BAD_C)), run_time=7.0)
        fixq = VGroup(M('fetch logs', 24, Q_C), M('| filter loglevel == "ERROR"', 24, OK_C), M('| summarize n = count(), by: {k8s.namespace.name}', 24, Q_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(oq)
        self.beat("So filter first, then summarize. Now the query really counts error records per namespace.",
                  FadeOut(VGroup(bl, before, alb, after)), ReplacementTransform(oq, fixq), run_time=2.6)
        self.play(FadeOut(fixq), run_time=0.5)

        # ---------- 6. guardrails
        g1 = VGroup(T("The store charges for what a query reads.", 26), T("Start with the shortest time window that answers the question.", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        g2 = VGroup(T("Metrics come from", 26), M("timeseries", 24, Q_C), T(", not from fetch.", 26)).arrange(RIGHT, buff=0.15)
        g3 = VGroup(M('contains(content, "timeout", caseSensitive: false)', 24, OK_C), T("not lower(), which skips the index", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        gs = VGroup(g1, g2, g3).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit(gs, 12.6).move_to([0, 0.3, 0])
        self.beat("A few guardrails. The store behind all this, Grail, charges for the data a query scans. A month of logs costs real money on a paid environment, so start with the shortest window that answers the question.",
                  FadeIn(g1, shift=UP * 0.1), run_time=3.4)
        self.beat("Metric values come from a different first command, timeseries. There's no fetch for them.",
                  FadeIn(g2, shift=UP * 0.1), run_time=2.2)
        self.beat("And to match text without caring about capitals, use contains with case sensitive false. Wrapping a field in lower stops Grail from using its index, so it scans far more data.",
                  FadeIn(g3, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(gs), run_time=0.6)

        # ---------- 7. moral, check
        mor = VGroup(T("Records flow down, one command at a time.", 32, Q_C), T("A loud error is a gift. A quiet zero needs checking.", 30, ASK_C)).arrange(DOWN, buff=0.25).move_to([0, 2.0, 0])
        self.beat("So the moral of the story. A DQL query is a pipeline: records flow down, one command at a time, in the order you wrote. A loud error is a gift. A quiet zero needs checking.",
                  Write(mor[0]), Succession(Wait(3.6), FadeIn(mor[1])), run_time=6.0)
        cq = VGroup(T("Quick check: spot the two SQL habits.", 28), M('| filter loglevel = "ERROR" | summarize count(), by: k8s.namespace.name', 22, Q_C)).arrange(DOWN, buff=0.25).move_to([0, -0.3, 0])
        fit(cq, 12.6)
        self.beat("A quick check. This query hides two SQL habits. Can you spot both? Pause and look.",
                  FadeIn(cq), run_time=2.0)
        self.pause([0, -1.5, 0], text="pause and look")
        ans = VGroup(T("a single = where DQL compares with ==,", 26, BAD_C), T("and a by list without braces", 26, BAD_C)).arrange(DOWN, buff=0.12).move_to([0, -2.4, 0])
        self.beat("A single equals sign where DQL compares with double equals. And a by list without curly braces.",
                  FadeIn(ans), run_time=2.4)
        self.beat("With this part, the watching is done. What none of these tools asks is who else might be inside the building. Next, security, starting with the software supply chain.",
                  FadeOut(VGroup(cq, ans)), mor.animate.set_opacity(0.4), run_time=2.0)
        self.wait(1.0)
