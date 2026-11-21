import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"/healthz\b", "slash health Z"), (r"\bLogQL\b", "log Q L"), (r"\bservice_name\b", "service name"),
    (r"\bcount_over_time\b", "count over time"), (r"\bline_format\b", "line format"), (r"\bLGTM\b", "L G T M"),
    (r"\b14:02\b", "fourteen oh two"),
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


def folder(label, color, w=2.2):
    tab = Rectangle(width=0.7, height=0.18, stroke_color=color, stroke_width=2.5).set_fill(dark(color, 0.3), 1)
    body = Rectangle(width=w, height=1.0, stroke_color=color, stroke_width=2.5).set_fill(dark(color, 0.18), 1)
    tab.next_to(body, UP, buff=0).align_to(body, LEFT)
    t = M(label, 20, color).move_to(body)
    fit(t, w - 0.2)
    return VGroup(tab, body, t)


class D54RecordsOffice(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("The records office", "how Loki stores logs, and how LogQL reads them")

        # ---------------- 1. the board shows when, the notes say why
        bd = frame(4.6, 2.2, GOLD_M, [-3.4, 1.0, 0], fill=0.06)
        bd_t = T("the board", 26, GOLD_M).next_to(bd, UP, buff=0.15)
        ln = VMobject(stroke_color=RED_M, stroke_width=4).set_points_as_corners(
            [bd.get_corner(DL) + RIGHT * (0.3 + 0.4 * k) + UP * (0.5 + (0.15 if k < 6 else 1.1)) for k in range(10)])
        at = T("bed 4: worse at 14:02", 24, RED_M).next_to(bd, DOWN, buff=0.25)
        self.beat("Picture the doctor from last time, now looking at a clear board. It says bed four got worse at fourteen oh two.",
                  Create(bd), FadeIn(bd_t), Create(ln), FadeIn(at), run_time=2.6)
        notes = frame(4.2, 2.2, BLUE_M, [3.4, 1.0, 0], fill=0.06)
        notes_t = T("the nurses' notes", 26, BLUE_M).next_to(notes, UP, buff=0.15)
        nl = VGroup(*[Line(LEFT * 1.6, RIGHT * (1.6 - 0.5 * (k % 2)), stroke_color=BLUE_M, stroke_width=2) for k in range(5)]).arrange(DOWN, buff=0.28, aligned_edge=LEFT).move_to(notes)
        self.beat("Useful, but it is not the story. The story is in the nurses' notes: what the patient said, what was given, what went wrong.",
                  Create(notes), FadeIn(notes_t), LaggedStart(*[Create(l) for l in nl], lag_ratio=0.2), run_time=2.8)
        drawer = VGroup(T("each ward's drawer is emptied", 24, GREY_B), T("when the patient leaves", 24, GREY_B)).arrange(DOWN, buff=0.08).next_to(notes, DOWN, buff=0.2)
        self.beat("But each ward keeps its notes in its own drawer, and the drawer is emptied when the patient leaves.",
                  FadeIn(drawer), LaggedStart(*[l.animate.set_opacity(0.15) for l in nl], lag_ratio=0.2), run_time=2.4)
        sw = VGroup(M("docker compose logs", 26, TEAL_M), T("one machine, only while the container exists", 24, GREY_B),
                    T("ten servers: ten places to search", 24, GREY_B)).arrange(DOWN, buff=0.18).move_to([0, -2.2, 0])
        self.beat("Our app has the same drawer. docker compose logs shows the app's logs, the lines a program writes as it works, on one machine. Remove the container, and they go with it.",
                  FadeIn(sw[0]), FadeIn(sw[1]), run_time=3.0)
        self.beat("With ten servers, you would search in ten places, at 3 in the morning.", FadeIn(sw[2]), run_time=1.6)
        self.play(FadeOut(VGroup(bd, bd_t, ln, at, notes, notes_t, nl, drawer, sw)), run_time=0.6)

        # ---------------- 2. predict: what goes in the index?
        q = T("Loki keeps every container's log lines in one place.", 30).move_to(UP * 2.4)
        q2 = T("What does it put in its index, its lookup list?", 32, YELLOW_M).next_to(q, DOWN, buff=0.25)
        self.beat("So we want one place for the logs of every container. That place is Loki, Grafana Labs' log store. To find lines fast, it keeps an index, a lookup list. What goes in it?",
                  FadeIn(q), Write(q2), run_time=3.2)
        opts = VGroup(T("A. only the labels on each stream, such as service and container", 26), T("B. every word of every line, like a search engine", 26),
                      T("C. only the WARNING and ERROR lines", 26), T("D. nothing: every query reads all the logs", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.5)
        fit(opts, 12.4)
        self.play(LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3), run_time=1.6)
        self.beat("Let's be fair to B. Every word, like a search engine. That sounds like the fastest way to find anything.", Indicate(opts[1], color=GREY_B), run_time=2.0)
        self.guess([0, -2.8, 0])
        self.play(FadeOut(VGroup(q, q2, opts)), run_time=0.4)

        # ---------------- 3. the records office, mapped
        cat = frame(3.8, 3.6, GOLD_M, [-4.5, 0.2, 0], fill=0.08)
        cat_t = T("catalogue", 26, GOLD_M).move_to(cat.get_top() + DOWN * 0.35)
        entries = VGroup(*[T(t, 22) for t in ("ward A, bed 4, Monday", "ward A, bed 5, Monday", "ward B, bed 1, Monday", "ward A, bed 4, Tuesday")]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        entries.next_to(cat_t, DOWN, buff=0.3)
        fit(entries, 3.4)
        self.beat("Picture a hospital records office. It files notes by ward, bed and date, and never catalogues the words inside.",
                  Create(cat), FadeIn(cat_t), LaggedStart(*[FadeIn(e, shift=RIGHT * 0.1) for e in entries], lag_ratio=0.3), run_time=3.0)
        shelf = VGroup(*[folder(f, BLUE_M, w=1.7) for f in ("A 4 Mon", "A 5 Mon", "B 1 Mon", "A 4 Tue", "B 2 Tue", "C 3 Tue")]).arrange_in_grid(2, 3, buff=(0.35, 0.55)).move_to([2.6, 0.2, 0])
        self.beat("The folders sit on the shelves, full of pages.", LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in shelf], lag_ratio=0.15), run_time=1.8)
        clerk = Circle(radius=0.15, stroke_color=GREEN_M, stroke_width=3).set_fill(dark(GREEN_M, 0.4), 1).move_to([-1.4, -2.4, 0])
        find = T('find "allergy" for bed 4 on Monday', 24, GREEN_M).move_to([1.6, -2.7, 0])
        self.beat("To find a phrase, a clerk looks up bed four on Monday, opens just that folder, and reads.",
                  FadeIn(find), Succession(FadeIn(clerk), Indicate(entries[0], color=GREEN_M), clerk.animate.move_to(shelf[0].get_bottom() + DOWN * 0.25),
                                                          shelf[0][1].animate.set_fill(dark(GREEN_M, 0.4))), run_time=3.2)
        self.beat("The catalogue stays tiny. And the reading is quick, because the folders are few.", run_time=None)
        self.beat("That is Loki. The answer is A. It indexes only the labels.", run_time=None)
        lab = VGroup(T("labels:", 24, GOLD_M), M('service="web"', 22, GOLD_M), M('container=', 22, GOLD_M), M('"observability-web-1"', 22, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        lab.move_to([-4.5, -0.1, 0])
        fit(lab, 3.5)
        self.beat("Each log line carries a few labels, a name and a value, such as service is web. The catalogue holds those, and nothing else.",
                  FadeOut(entries), FadeIn(lab), run_time=2.4)
        stream = T("all lines with the same labels: one log stream, one folder", 24, BLUE_M).next_to(shelf, UP, buff=0.3)
        fit(stream, 7.0)
        self.beat("All lines with exactly the same labels form one log stream. That is a folder.", FadeIn(stream), Indicate(shelf[0][1], color=BLUE_M), run_time=2.0)
        chunks = T("the text inside: compressed, not indexed at all", 24, GREY_B).next_to(shelf, DOWN, buff=0.3)
        self.beat("The text of each line is packed tight, compressed, and not indexed at all.", FadeOut(find), FadeOut(clerk), FadeIn(chunks), run_time=1.8)
        es = T("a search engine for logs indexes every word: more disk and memory, faster at one word across all logs", 22, GREY_B).to_edge(DOWN, buff=0.6)
        fit(es, 12.4)
        self.beat("So why not B? A store that indexes every word finds a word across all logs faster, but pays in disk and memory. Loki chose the small catalogue.",
                  FadeIn(es), run_time=3.2)
        self.wait(0.3)
        self.play(FadeOut(VGroup(cat, cat_t, lab, shelf, stream, chunks, es)), run_time=0.6)

        # ---------------- 4. the porter: Alloy
        cs = VGroup(*[mbox(n, TEAL_M, size=22, w=2.0, h=0.7) for n in ("web", "redis", "prometheus")]).arrange(DOWN, buff=0.35).move_to([-4.8, 0.2, 0])
        al = frame(2.4, 1.0, PURPLE_M, [-0.6, 0.2, 0], fill=0.16)
        al_t = T("Alloy", 28).move_to(al).set_z_index(2)
        lk = frame(2.4, 1.0, BLUE_M, [2.6, 0.2, 0], fill=0.16)
        lk_t = T("Loki", 28).move_to(lk).set_z_index(2)
        gf = frame(2.0, 0.9, GOLD_M, [5.3, 0.2, 0], fill=0.16)
        gf_t = T("Grafana", 24).move_to(gf).set_z_index(2)
        self.beat("Someone has to carry the notes to the office. A log has no current value to scrape; it is a stream of events. So a collector sends the lines as they appear.",
                  LaggedStart(*[FadeIn(c) for c in cs], lag_ratio=0.2), GrowFromCenter(lk), Write(lk_t), run_time=3.2)
        ar = VGroup(*[Arrow(c.get_right(), al.get_left(), buff=0.1, stroke_width=2.5, color=TEAL_M, max_tip_length_to_length_ratio=0.1) for c in cs])
        a2 = Arrow(al.get_right(), lk.get_left(), buff=0.1, stroke_width=3, color=PURPLE_M, max_tip_length_to_length_ratio=0.15)
        a3 = Arrow(gf.get_left(), lk.get_right(), buff=0.08, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.25)
        self.beat("In the lab that porter is Grafana Alloy. It finds each container, labels it, follows its output, and pushes the lines to Loki.",
                  GrowFromCenter(al), Write(al_t), LaggedStart(*[GrowArrow(a) for a in ar], lag_ratio=0.2), GrowArrow(a2),
                  Succession(Wait(1.0), LaggedStart(*[travel(a, TEAL_M, 0.6) for a in ar], lag_ratio=0.3), travel(a2, PURPLE_M, 0.6)), run_time=4.4)
        old = T("Promtail, the older shipper in many tutorials, reached end of life on 2 March 2026", 22, GREY_B).to_edge(DOWN, buff=0.7)
        fit(old, 12.4)
        self.beat("Older tutorials use Promtail, which reached end of life on the second of March, 2026.", FadeIn(old), run_time=2.2)
        self.beat("And Grafana asks Loki, right next to Prometheus.", GrowFromCenter(gf), Write(gf_t), GrowArrow(a3), run_time=1.6)
        self.play(FadeOut(VGroup(cs, al, al_t, lk, lk_t, gf, gf_t, ar, a2, a3, old)), run_time=0.6)

        # ---------------- 5. LogQL, one step at a time
        qb = M('{service_name="web"}', 26, GOLD_M).to_corner(UL, buff=0.7)
        raw = [('GET /healthz 200', GREY_B), ('GET / 200', WHITE), ('GET /healthz 200', GREY_B), ('GET / 500', RED_M), ('Traceback (most recent call last):', PURPLE_M),
               ('GET / 200', WHITE), ('GET /healthz 200', GREY_B), ('GET / 500', RED_M), ('GET / 200', WHITE)]
        rows = VGroup(*[M('{"method":"' + s.split()[0] + '","path":"' + s.split()[1] + '","status":' + s.split()[2] + '}', 22, c) if not s.startswith("Trace") else M(s, 22, c) for s, c in raw])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0.2, -0.6, 0])
        self.beat("Now let's ask the office. Loki's query language, LogQL, borrows a lot from PromQL. Braces pick the folders: here, every line from the app.",
                  Write(qb), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.08), run_time=3.6)
        q1 = M('!= "/healthz"', 26, BLUE_M).next_to(qb, RIGHT, buff=0.2)
        hz = [i for i, (s, c) in enumerate(raw) if "/healthz" in s]
        self.beat("Then a pipe, and steps that read inside them. First, drop every line that contains slash health Z, the health checks.",
                  FadeIn(q1), *[rows[i].animate.set_opacity(0.12) for i in hz], run_time=2.2)
        q2 = M("| json", 26, BLUE_M).next_to(q1, RIGHT, buff=0.2)
        self.beat("Next, json: read each line's names and values, so method, path and status become labels for this query.", FadeIn(q2), run_time=2.0)
        q3 = M("| status >= 500", 26, BLUE_M).next_to(qb, DOWN, buff=0.25).align_to(qb, LEFT)
        keep = [i for i, (s, c) in enumerate(raw) if s.endswith("500")]
        self.beat("Then keep only the failed requests: status five hundred or more.",
                  FadeIn(q3), *[rows[i].animate.set_opacity(0.12) for i in range(len(raw)) if i not in keep and i not in hz], run_time=2.2)
        q4 = M('| line_format "{{.method}} {{.path}} -> {{.status}}"', 24, BLUE_M).next_to(q3, RIGHT, buff=0.2)
        fit(VGroup(q3, q4), 12.4)
        outs = VGroup(*[M("GET / -> 500", 26, RED_M).move_to(rows[i], aligned_edge=LEFT) for i in keep])
        self.beat("And rewrite each line in a shape that is easy to scan.", FadeIn(q4), *[ReplacementTransform(rows[i], o) for i, o in zip(keep, outs)], run_time=2.2)
        tip = T("put the cheap text filter first: every line it drops, the parser never touches", 24, YELLOW_M).to_edge(DOWN, buff=0.55)
        fit(tip, 12.4)
        self.beat("Notice the order. The plain text filter came first. It is the cheapest step, and every line it drops is a line the parser never has to read.", FadeIn(tip), run_time=2.6)
        self.wait(0.3)
        self.play(FadeOut(VGroup(qb, q1, q2, q3, q4, outs, tip, *[rows[i] for i in range(len(raw)) if i not in keep])), run_time=0.6)

        # ---------------- 6. logs into numbers, and the traceback trap
        mq = M('sum by (status) (count_over_time({service_name="web"} | json | __error__="" [5m]))', 22, GOLD_M).to_edge(UP, buff=0.7)
        fit(mq, 12.4)
        self.beat("LogQL can also turn lines into numbers. Count the requests by status over five minutes, and graph them next to the Prometheus panels.",
                  Write(mq), run_time=2.4)
        tb = M("Traceback (most recent call last):", 24, PURPLE_M).move_to([0, 0.8, 0])
        err = M('__error__="..."', 24, RED_M).next_to(tb, DOWN, buff=0.3)
        self.beat("But when Redis is down, the app prints a Python traceback, lines that are not JSON. The parser marks them with an error label.",
                  FadeIn(tb), FadeIn(err), run_time=2.8)
        dr = T("a metric query refuses to run until you drop them: __error__=\"\"", 24, YELLOW_M).next_to(err, DOWN, buff=0.4)
        fit(dr, 12.4)
        self.beat("A metric query refuses to run until you drop them, with the empty error label.",
                  FadeIn(dr), Indicate(mq, color=YELLOW_M), run_time=2.4)
        self.play(FadeOut(VGroup(mq, tb, err, dr)), run_time=0.5)

        # ---------------- 7. break it: a label per visitor
        cat = frame(3.9, 3.0, GOLD_M, [-4.5, 0.4, 0], fill=0.08)
        cat_t = T("catalogue", 26, GOLD_M).move_to(cat.get_top() + DOWN * 0.35)
        few = VGroup(*[M(s, 22) for s in ('service="web"', 'service="redis"', 'service="prometheus"')]).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(cat_t, DOWN, buff=0.3)
        self.beat("Now let's break it on purpose. Today the catalogue is tiny: a few services, a few containers.",
                  Create(cat), FadeIn(cat_t), FadeIn(few), run_time=1.8)
        idl = M('request_id="..."', 26, RED_M).move_to([1.6, 2.2, 0])
        self.beat("Someone thinks: let's add the request ID as a label, so we can find any request instantly. What happens to the office? Pause and guess.",
                  FadeIn(idl, scale=1.2), run_time=2.4)
        self.wait(2.0)
        many = VGroup(*[folder("", RED_M, w=0.5).scale(0.6) for _ in range(60)]).arrange_in_grid(5, 12, buff=(0.12, 0.2)).move_to([2.2, -0.2, 0])
        self.beat("Every new label value makes a new stream: one folder per request. The catalogue grows bigger than the notes.",
                  LaggedStart(*[FadeIn(f) for f in many], lag_ratio=0.02), cat.animate.set_stroke(RED_M), run_time=3.4)
        self.beat("Well, that is one way to make a fast system slow.", Wiggle(cat), run_time=1.4)
        self.play(FadeOut(VGroup(many, idl, cat, cat_t, few)), run_time=0.5)
        good = VGroup(T("good labels", 28, GREEN_M), M("service  environment  cluster  container", 24, GREEN_M)).arrange(DOWN, buff=0.15)
        bad = VGroup(T("bad labels", 28, RED_M), M("request ID  user ID  IP address", 24, RED_M)).arrange(DOWN, buff=0.15)
        VGroup(good, bad).arrange(DOWN, buff=0.5).move_to(UP * 0.8)
        keep_l = T("keep those values in the line itself, where a filter finds them", 26, YELLOW_M).next_to(bad, DOWN, buff=0.45)
        docs = T("Loki's docs: no more than 10 to 15 labels, each with few values", 24, GREY_B).next_to(keep_l, DOWN, buff=0.3)
        self.beat("So the labels are for things with a few values: service, environment, cluster, container. Never request IDs, user IDs or IP addresses.",
                  FadeIn(good), FadeIn(bad), run_time=2.6)
        self.beat("Keep those values in the line, where a text filter finds them. Loki's docs suggest ten to fifteen labels at most, each with few values.",
                  FadeIn(keep_l), FadeIn(docs), run_time=2.6)
        self.play(FadeOut(VGroup(good, bad, keep_l, docs)), run_time=0.5)

        # ---------------- 8. the honest limit, moral, check
        lim = VGroup(T("Loki is fast because it reads only a few folders.", 30),
                     T("Finding one word across every log at once: the wrong tool.", 30, GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        self.beat("One honest limit. Loki is fast because it reads only a few folders. To find one word across every log at once, it is the wrong tool. The next lesson brings a store that indexes every word.",
                  FadeIn(lim[0]), Succession(Wait(1.8), FadeIn(lim[1])), run_time=3.6)
        self.play(FadeOut(lim), run_time=0.5)
        moral = T("Labels pick the folders. The text stays cheap.", 36, YELLOW_M).move_to(UP * 2.4)
        self.beat("So the moral of the story. Labels pick the folders. The text stays cheap.", Write(moral), run_time=1.8)
        rec = VGroup(T("one place for every container's lines", 28, TEAL_M),
                     T("the catalogue holds labels; a stream is a folder", 28, GOLD_M),
                     T("LogQL: pick folders, filter text, then parse", 28, BLUE_M),
                     T("IDs go in the line, never in a label", 28, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("One place for every container's lines. The catalogue holds only labels. LogQL picks folders, filters text, then parses. And IDs go in the line, never in a label.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=7.0)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.5)
        c1 = T("Quick check: which query reads less?", 30).move_to(UP * 0.9)
        c2 = M('{service_name="web"} |= "timeout"', 26).next_to(c1, DOWN, buff=0.35)
        c3 = T("or the same filter over every service's logs?", 30).next_to(c2, DOWN, buff=0.3)
        self.beat("A quick check. Which reads less: the web service's lines, filtered for the word timeout? Or the same filter over every service's logs?",
                  FadeIn(c1), FadeIn(c2), FadeIn(c3), run_time=2.4)
        self.guess([0, -1.2, 0])
        ans = T("The first: the labels pick one folder before any reading starts.", 28, GREEN_M).next_to(c3, DOWN, buff=0.6)
        fit(ans, 12.6)
        self.beat("The first. The labels pick one folder before any reading starts.", FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.2)
