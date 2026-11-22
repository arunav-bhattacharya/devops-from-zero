import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import fg as _fg


def box(*a, **k):  # keep the label drawn above its own filled outline, even when the outline is animated
    b = _fg.box(*a, **k); b[1].set_z_index(1); return b


def chip(*a, **k):
    c = _fg.chip(*a, **k); c[1].set_z_index(1); return c

SAY.extend([
    (r"\bredis\.exceptions\.connectionerror\b", "redis dot exceptions dot connection error"),
    (r"\bredis\.exceptions\.ConnectionError\b", "redis dot exceptions dot connection error"),
    (r"\bConnectionError\b", "connection error"), (r"\bconnectionerror\b", "connection error"),
    (r"\bdisk\.full\.warning\b", "disk dot full dot warning"), (r"\bgrep\b", "grep"),
])

NOTE_C = GREY_B      # notes (documents)
CLERK_C = GOLD_M     # the clerk (analyzer)
CARD_C = PURPLE_M    # index cards (tokens)
ASK_C = YELLOW_M     # searches


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def word_parts(tm, s):
    """Split a Text mobject into one VGroup per word (Text drops spaces from its glyphs)."""
    out, i = [], 0
    for w in s.split():
        out.append(VGroup(*tm[i:i + len(w)])); i += len(w)
    return out


def note(n, lines, w=6.7):
    head = T(f"note {n}", 22, GREY_B)
    body = [T(l, 23) for l in lines]
    inner = VGroup(head, *body).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    r = RoundedRectangle(corner_radius=0.1, width=w, height=inner.height + 0.36, stroke_color=NOTE_C, stroke_width=2.5)
    r.set_fill(tint(NOTE_C, 0.07), 1)
    inner.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.22)
    inner.set_z_index(1)
    return VGroup(r, inner)


def clerk():
    head = Circle(radius=0.13, stroke_color=CLERK_C, stroke_width=3).set_fill(tint(CLERK_C, 0.3), 1)
    body = Arc(radius=0.24, start_angle=0, angle=PI, stroke_color=CLERK_C, stroke_width=3).next_to(head, DOWN, buff=0.04)
    return VGroup(head, body)


def card_row(tok, nums):
    c = chip(tok, CARD_C, 22, mono=True)
    n = M(nums, 24).next_to(c, RIGHT, buff=0.2)
    return VGroup(c, n)


class D55Tokens(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("Why a search can miss a word you can see", "how Elasticsearch files every word of a log")

        # ---------- 1. the question
        err1 = M("redis.exceptions.ConnectionError: Error -2 connecting to redis:6379", 24, RED_M).move_to(UP * 1.6)
        sb = RoundedRectangle(corner_radius=0.15, width=8.0, height=0.8, stroke_color=ASK_C, stroke_width=2.5).move_to(DOWN * 0.4)
        q0 = VGroup(T("search:", 26, GREY_B), M("ConnectionError", 26, ASK_C)).arrange(RIGHT, buff=0.25).move_to(sb).align_to(sb, LEFT).shift(RIGHT * 0.3)
        self.beat("Here is a line from our lab app, hello-devops. Redis, the small database that keeps its visit count, is down, so the app writes this error.",
                  FadeIn(err1, shift=DOWN * 0.15), run_time=2.0)
        self.beat("All the logs go to one store you can search. So you type ConnectionError into the search box.",
                  Create(sb), Succession(Wait(1.6), Write(q0)), run_time=3.4)
        z0 = VGroup(T("0 hits", 28, RED_M), tick(False, 0.16)).arrange(RIGHT, buff=0.2).next_to(sb, RIGHT, buff=0.35)
        z0.shift(LEFT * (z0.get_right()[0] - 6.3) if z0.get_right()[0] > 6.3 else 0)
        self.beat("The word is right there on your screen. And the answer is zero hits.",
                  Succession(Wait(1.6), FadeIn(z0, scale=1.2)), Indicate(VGroup(*err1[0:32]), color=RED_M, scale_factor=1.05), run_time=3.4)
        qn = T("How can a search miss a word you can see?", 32, ASK_C).move_to(DOWN * 2.2)
        self.beat("How can a search miss a word you can read with your own eyes? Hold on to that question. By the end, that zero will make perfect sense.",
                  Write(qn), run_time=2.2)
        self.play(FadeOut(VGroup(err1, sb, q0, z0, qn)), run_time=0.6)

        # ---------- 2. the chart room, and reading everything
        n1 = note(1, ["Payment FAILED for order 42: card declined"]).move_to([-3.1, 1.6, 0])
        n2 = note(2, ["Payment accepted for order 43"]).move_to([-3.1, 0.3, 0])
        lab_n = T("the chart room", 28, NOTE_C).move_to([-3.1, 3.0, 0])
        self.beat("Let's go back to the hospital. Every note from every bed is copied to one chart room. Here are two notes from the payment desk.",
                  FadeIn(lab_n), LaggedStart(FadeIn(n1, shift=RIGHT * 0.2), FadeIn(n2, shift=RIGHT * 0.2), lag_ratio=0.4), run_time=3.2)
        ask1 = T("Which notes say declined?", 28, ASK_C).move_to([3.6, 1.6, 0])
        self.beat("A doctor asks: which notes say declined? The simplest plan is to read every note, from the first word to the last.",
                  FadeIn(ask1, shift=LEFT * 0.2), run_time=1.8)
        cnt = ValueTracker(0)
        counter = always_redraw(lambda: VGroup(T("words read:", 26, GREY_B), M(str(int(round(cnt.get_value()))), 28, ASK_C)).arrange(RIGHT, buff=0.25).move_to([3.6, 0.3, 0]))

        def sweep(rt):
            parts = []
            for n in (n1, n2):
                l = Line(UP * 0.5, DOWN * 0.5, stroke_width=5, color=ASK_C).move_to(n[0].get_left() + RIGHT * 0.1)
                parts += [FadeIn(l, run_time=0.05), l.animate(run_time=rt / 2 - 0.1, rate_func=linear).move_to(n[0].get_right() + LEFT * 0.1), FadeOut(l, run_time=0.05)]
            return Succession(*parts)
        self.add(counter)
        self.beat("That is what the terminal command grep does. It reads every word, every time.",
                  sweep(3.0), cnt.animate(run_time=3.0, rate_func=linear).set_value(12), run_time=3.3)
        self.play(n1[0].animate.set_stroke(ASK_C, width=4), run_time=0.5)
        ask2 = T("Which notes say accepted?", 28, ASK_C).move_to(ask1)
        self.beat("Found it. Then she asks a second question, and the reading starts again from page one.",
                  n1[0].animate.set_stroke(NOTE_C, width=2.5), Transform(ask1, ask2),
                  Succession(Wait(1.2), AnimationGroup(sweep(2.6), cnt.animate(run_time=2.6, rate_func=linear).set_value(24))), run_time=4.0)

        # many notes
        self.remove(counter)
        cnt_static = counter.copy().clear_updaters(); self.add(cnt_static)
        grid = VGroup(*[RoundedRectangle(corner_radius=0.03, width=0.36, height=0.2, stroke_color=NOTE_C, stroke_width=1.5).set_fill(tint(NOTE_C, 0.07), 1) for _ in range(18 * 12)])
        grid.arrange_in_grid(rows=12, cols=18, buff=(0.12, 0.1)).move_to(DOWN * 0.2)
        week = T("a week of logs from fifty containers", 28, NOTE_C).move_to(UP * 3.0)
        self.beat("Two notes are fine. But a week of logs from fifty containers is a mountain of notes.",
                  FadeOut(VGroup(n1, n2, ask1, cnt_static, lab_n)), FadeIn(week),
                  LaggedStart(*[FadeIn(g) for g in grid], lag_ratio=0.01), run_time=3.6)
        crawl = Line(UP * 0.13, DOWN * 0.13, stroke_width=4, color=ASK_C).move_to(grid[0].get_left())
        self.beat("By the time the doctor finishes reading, the patient has gone home, and so has the doctor.",
                  Succession(FadeIn(crawl, run_time=0.1), crawl.animate(run_time=3.0, rate_func=linear).move_to(grid[17].get_right())), run_time=3.2)
        self.play(FadeOut(crawl), run_time=0.2)
        wish = T("Wouldn't it be nice to read each note once, when it arrives?", 30, ASK_C).move_to(DOWN * 3.0)
        self.beat("So here is the wish. Wouldn't it be nice to do the reading once, when a note arrives, and never again?",
                  FadeIn(wish, shift=UP * 0.15), run_time=2.2)
        self.play(FadeOut(VGroup(grid, week, wish)), run_time=0.6)

        # ---------- 3. the index at the back of a book
        page = RoundedRectangle(corner_radius=0.08, width=4.2, height=4.6, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.06), 1).move_to([-2.6, 0, 0])
        ih = T("Index", 30).move_to(page.get_top() + DOWN * 0.5)
        entries = [("bandage", "12"), ("declined", "37, 81"), ("fever", "5, 40, 96"), ("pill", "18")]
        ent = VGroup(*[VGroup(T(a, 26), T(b, 26, GREY_B)).arrange(RIGHT, buff=0.5) for a, b in entries]).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        ent.next_to(ih, DOWN, buff=0.45)
        self.beat("You already own a thing that grants that wish. The index at the back of a book.",
                  Create(page), Write(ih), LaggedStart(*[FadeIn(e) for e in ent], lag_ratio=0.2), run_time=3.0)
        hl = SurroundingRectangle(ent[1], buff=0.1, color=ASK_C, stroke_width=2.5)
        look = T("look up one word, get page numbers", 26, ASK_C).move_to([2.9, 0.6, 0])
        self.beat("To find declined, you don't read the book. You look up one word, and it hands you page numbers.",
                  Create(hl), FadeIn(look, shift=LEFT * 0.2), run_time=2.4)
        once = T("someone did the reading once", 26, GREY_B).move_to([2.9, -0.4, 0])
        self.beat("Somebody did the slow reading once, when the book was made. Every reader after that gets it for free.",
                  FadeIn(once, shift=LEFT * 0.2), run_time=2.0)
        self.play(FadeOut(VGroup(page, ih, ent, hl, look, once)), run_time=0.6)

        # ---------- 4. the clerk builds the cards
        n1.move_to([-3.1, 1.9, 0]); n2.move_to([-3.1, 0.6, 0])
        for n in (n1, n2):
            n[0].set_stroke(NOTE_C, width=2.5)
        lab_c = T("the clerk's cards", 28, CARD_C).move_to([3.65, 3.0, 0])
        lab_n.move_to([-3.1, 3.0, 0])
        ck = clerk().move_to([0.5, 1.9, 0])
        self.beat("So the chart room hires a clerk. Each time a note arrives, the clerk reads it once, and files every word on its own index card.",
                  FadeIn(lab_n), FadeIn(n1, shift=RIGHT * 0.2), FadeIn(ck, shift=DOWN * 0.2), FadeIn(lab_c), run_time=2.6)

        TOK = ["payment", "failed", "for", "order", "42", "card", "declined", "accepted", "43"]
        pos = {}
        for k, t in enumerate(TOK):
            col, row = (0, k) if k < 5 else (1, k - 5)
            pos[t] = np.array([0.95 + col * 2.95, 2.25 - row * 0.72, 0])
        rows = {}
        s1 = "Payment FAILED for order 42: card declined"
        w1 = word_parts(n1[1][1], s1)
        toks1 = ["payment", "failed", "for", "order", "42", "card", "declined"]
        anims = []
        for wp, t in zip(w1, toks1):
            r = card_row(t, "1"); r.move_to(pos[t], aligned_edge=LEFT); rows[t] = r
            anims.append(AnimationGroup(ReplacementTransform(wp.copy(), r[0][1]), Create(r[0][0])))
        self.beat("Watch two habits. It splits the text into words, and it writes each one in lower case. Capital FAILED becomes plain failed.",
                  LaggedStart(*anims, lag_ratio=0.25), Indicate(w1[1], color=CLERK_C), run_time=5.0)
        self.beat("On every card, it writes the number of the note the word came from. Note one.",
                  LaggedStart(*[FadeIn(rows[t][1], shift=LEFT * 0.1) for t in toks1], lag_ratio=0.1), run_time=2.0)

        s2 = "Payment accepted for order 43"
        w2 = word_parts(n2[1][1], s2)
        self.play(FadeIn(n2, shift=RIGHT * 0.2), ck.animate.move_to([0.5, 0.6, 0]), run_time=0.8)
        for t in ("accepted", "43"):
            r = card_row(t, "2"); r.move_to(pos[t], aligned_edge=LEFT); rows[t] = r
        new_nums = {t: M("1 2", 24).move_to(rows[t][1], aligned_edge=LEFT) for t in ("payment", "for", "order")}
        self.beat("Note two arrives. New words get new cards. Words the clerk has seen before just get one more number.",
                  ReplacementTransform(w2[1].copy(), rows["accepted"][0][1]), Create(rows["accepted"][0][0]),
                  ReplacementTransform(w2[4].copy(), rows["43"][0][1]), Create(rows["43"][0][0]),
                  FadeIn(rows["accepted"][1]), FadeIn(rows["43"][1]),
                  Succession(Wait(2.4), AnimationGroup(*[Transform(rows[t][1], new_nums[t]) for t in new_nums])), run_time=5.0)
        self.beat("Payment, for, and order now say: notes one and two.",
                  *[Indicate(rows[t][1], color=CARD_C) for t in ("payment", "for", "order")], run_time=2.0)

        # ---------- 5. predict, then show
        sb = RoundedRectangle(corner_radius=0.15, width=7.0, height=0.8, stroke_color=ASK_C, stroke_width=2.5).move_to([-1.6, -2.6, 0])

        def qtext(s, c=ASK_C):
            return VGroup(T("search:", 26, GREY_B), M(s, 26, c)).arrange(RIGHT, buff=0.25).move_to(sb).align_to(sb, LEFT).shift(RIGHT * 0.3)

        def result(s, ok):
            c = GREEN_M if ok else RED_M
            return VGroup(T(s, 28, c), tick(ok, 0.16)).arrange(RIGHT, buff=0.2).next_to(sb, RIGHT, buff=0.4)

        q = qtext("payment")
        self.beat("Now let's search. Payment. How many notes come back? Pause and guess.",
                  Create(sb), Write(q), run_time=2.0)
        self.pause([3.6, -1.4, 0])
        box1 = SurroundingRectangle(rows["payment"], buff=0.08, color=ASK_C, stroke_width=3)
        r1 = result("2 hits", True)
        self.beat("Two. The search went straight to one card, read the numbers one and two, and was done.",
                  Create(box1), Succession(Wait(1.2), AnimationGroup(n1[0].animate.set_stroke(ASK_C, width=4), n2[0].animate.set_stroke(ASK_C, width=4), FadeIn(r1))), run_time=3.2)
        self.beat("Notice what it did not do. It did not read a single note.",
                  Indicate(lab_n, color=ASK_C), run_time=1.6)
        q2 = qtext("payments")
        self.beat("One small change. Payments, with an s at the end. Pause and guess.",
                  FadeOut(box1), FadeOut(r1), n1[0].animate.set_stroke(NOTE_C, width=2.5), n2[0].animate.set_stroke(NOTE_C, width=2.5), Transform(q, q2), run_time=1.6)
        self.pause([3.6, -1.4, 0])
        r2 = result("0 hits", False)
        self.beat("Zero. There is no card that says payments. The clerk files words as they are, only lowercased. It never trims them down to a shorter stem.",
                  FadeIn(r2, scale=1.2), Succession(Wait(1.0), Indicate(rows["payment"][0][1], color=CARD_C, scale_factor=1.2)), run_time=3.0)

        # ---------- 6. break the grep picture
        self.play(FadeOut(VGroup(q, r2)), run_time=0.4)
        self.beat("Now, our mystery. Most of us picture search like grep, only faster: it finds any piece of text. Let's be fair to that picture. Grep really would find ConnectionError inside the error line.",
                  run_time=None)
        cards = VGroup(*rows.values())
        n3 = note(3, ["redis.exceptions.ConnectionError: ...", "... service not known"]).move_to([-3.1, -0.85, 0])
        self.beat("But Elasticsearch never looks at the notes when you search. It looks at the cards. So let's watch the clerk file the error.",
                  FadeOut(cards), FadeIn(n3, shift=RIGHT * 0.2), ck.animate.move_to([0.5, -0.85, 0]), run_time=2.6)
        s3a = "redis.exceptions.ConnectionError: ..."
        s3b = "... service not known"
        w3a = word_parts(n3[1][1], s3a)
        w3b = word_parts(n3[1][2], s3b)
        long = card_row("redis.exceptions.connectionerror", "3").move_to([0.75, -0.25, 0], aligned_edge=LEFT)
        sv = VGroup(*[card_row(t, "3") for t in ("service", "not", "known")]).arrange(RIGHT, buff=0.4).move_to([0.75, -1.1, 0], aligned_edge=LEFT)
        long.move_to([0.6, 1.6, 0], aligned_edge=LEFT)
        sv.move_to([0.75, 0.7, 0], aligned_edge=LEFT)
        self.beat("Here is the surprise. Dots between letters do not split a word. So the whole dotted name goes on one single card.",
                  ReplacementTransform(w3a[0].copy(), long[0][1]), Create(long[0][0]), Succession(Wait(2.4), FadeIn(long[1])), run_time=3.6)
        self.beat("Service, not, and known each get a card of their own.",
                  *[AnimationGroup(ReplacementTransform(w3b[i + 1].copy(), sv[i][0][1]), Create(sv[i][0][0]), FadeIn(sv[i][1])) for i in range(3)], run_time=2.0)
        q3 = qtext("ConnectionError")
        self.beat("Now search ConnectionError. Is there a card with exactly that word on it? Pause and guess.",
                  FadeIn(q3), run_time=1.6)
        self.pause([3.6, -1.4, 0])
        grep_ok = VGroup(T("grep reads the line:", 26, GREY_B), T("found", 26, GREEN_M), tick(True, 0.14)).arrange(RIGHT, buff=0.2).move_to([3.6, -0.3, 0])
        es_no = VGroup(T("the cards:", 26, GREY_B), T("no such card", 26, RED_M), tick(False, 0.14)).arrange(RIGHT, buff=0.2).move_to([3.6, -0.95, 0])
        r3 = result("0 hits", False)
        self.beat("No. There is a card for the whole dotted name, but none for connection error on its own. Zero hits.",
                  FadeIn(grep_ok), Succession(Wait(1.6), AnimationGroup(FadeIn(es_no), FadeIn(r3, scale=1.2))), Indicate(long[0][1], color=CARD_C, scale_factor=1.06), run_time=3.6)
        self.beat("Well. The search swears it has never heard of a word that is sitting right there. And it isn't lying. Zero hits really means: no card with that exact word.",
                  run_time=None)
        q4 = qtext('"service not known"', ASK_C)
        r4 = result("found", True)
        self.beat("So ask for words that really are on cards. The phrase service not known, from the same error. Found, at once.",
                  FadeOut(VGroup(grep_ok, es_no, r3)), Transform(q3, q4),
                  Succession(Wait(2.0), AnimationGroup(Indicate(sv, color=ASK_C, scale_factor=1.05), n3[0].animate.set_stroke(ASK_C, width=4), FadeIn(r4))), run_time=4.0)
        self.beat("That's the zero from the start. The error happened. We asked for a word that was never filed.",
                  run_time=None)

        # ---------- 7. name it
        self.play(FadeOut(VGroup(q3, r4, sb, sv, long, n3)), n1[0].animate.set_stroke(NOTE_C, width=2.5), ck.animate.move_to([0.5, 1.9, 0]), run_time=0.6)
        cards = VGroup(*rows.values())
        self.play(FadeIn(cards), run_time=0.6)

        def nm(a, ca, b):
            return VGroup(T(a, 26, ca), T("=", 26, GREY_B), T(b, 26)).arrange(RIGHT, buff=0.22)
        names = VGroup(nm("each note", NOTE_C, "a document"), nm("the clerk", CLERK_C, "the analyzer"),
                       nm("a word on a card", CARD_C, "a token"), nm("the box of cards", CARD_C, "an inverted index"))
        for i, g in enumerate(names):
            g.move_to([-3.3 if i % 2 == 0 else 3.4, -1.75 if i < 2 else -2.6, 0])
        self.beat("Now we can give the real names. In Elasticsearch, each log event is a document.",
                  Indicate(n1[0], color=NOTE_C, scale_factor=1.02), FadeIn(names[0], shift=UP * 0.15), run_time=2.2)
        self.beat("The clerk is called the analyzer. Each word on a card is a token.",
                  Indicate(ck, color=CLERK_C), FadeIn(names[1], shift=UP * 0.15),
                  Succession(Wait(1.6), AnimationGroup(Indicate(rows["declined"][0][1], color=CARD_C), FadeIn(names[2], shift=UP * 0.15))), run_time=2.8)
        frame_c = SurroundingRectangle(cards, buff=0.15, color=CARD_C, stroke_width=2.5)
        self.beat("And the box of cards is an inverted index: a table from each word to the documents that contain it. It is the book's index, turned around from the way the notes were written.",
                  Create(frame_c), FadeIn(names[3], shift=UP * 0.15), run_time=2.4)
        self.play(FadeOut(VGroup(names, n1, n2, ck, lab_n, lab_c, cards, frame_c)), run_time=0.6)

        # ---------- 8. guardrails
        g_t = T("Before you trust a zero", 32).move_to(UP * 3.0)
        a1 = VGroup(M("_analyze", 26, CLERK_C), T("shows the cards a line would get", 26)).arrange(RIGHT, buff=0.35)
        a1t = VGroup(*[chip(t, CARD_C, 22, mono=True) for t in ("payment", "failed", "for", "order", "42", "card", "declined")]).arrange(RIGHT, buff=0.15)
        r1g = VGroup(a1, a1t).arrange(DOWN, buff=0.3).move_to(UP * 1.6)
        self.beat("Three habits before you trust an empty result. First, ask the clerk. Elasticsearch has an analyze request that shows the exact tokens a line would be filed under.",
                  FadeIn(g_t), FadeIn(a1), Succession(Wait(3.0), LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in a1t], lag_ratio=0.12)), run_time=5.2)
        k1a = VGroup(T("a keyword field is filed whole:", 26), chip("ERROR", GOLD_M, 24, mono=True)).arrange(RIGHT, buff=0.3)
        k1b = VGroup(T("search", 26, GREY_B), M("level: error", 26, ASK_C), T("0 hits", 26, RED_M), tick(False, 0.13)).arrange(RIGHT, buff=0.3)
        k1 = VGroup(k1a, k1b).arrange(DOWN, buff=0.3).move_to(DOWN * 0.35)
        self.beat("Second, not every field gets cut into words. A keyword field, such as level, is filed whole, capitals and all. Its stored value is ERROR, so an exact search for error in lower case finds nothing.",
                  FadeIn(k1a[0]), Succession(Wait(2.6), FadeIn(k1a[1])), Succession(Wait(5.2), FadeIn(k1b)), run_time=7.6)
        clock = Circle(radius=0.32, stroke_color=GREY_B, stroke_width=3)
        hand = Line(clock.get_center(), clock.get_center() + UP * 0.24, stroke_width=3, color=GREY_B)
        r3g = VGroup(VGroup(clock, hand), T("a brand-new note is on the cards in about one second", 26)).arrange(RIGHT, buff=0.35).move_to(DOWN * 2.1)
        self.beat("Third, a note that arrived this very instant may not be on the cards yet. Elasticsearch makes new documents searchable within about one second, in a step called a refresh.",
                  FadeIn(r3g), Rotate(hand, angle=-TAU, about_point=clock.get_center()), run_time=4.4)
        self.play(FadeOut(VGroup(g_t, r1g, k1, r3g)), run_time=0.6)

        # ---------- 9. moral and check
        rule = VGroup(T("Search finds whole tokens, never pieces of them.", 34), T("Ask for words that are really there.", 34, ASK_C)).arrange(DOWN, buff=0.35).move_to(UP * 1.6)
        self.beat("So read the whole story out loud. The clerk reads each note once, when it arrives. It files every word, lowercased, on its own card. And a search looks up whole cards, never pieces of them.",
                  run_time=None)
        self.beat("Search finds whole tokens, never pieces of them. Ask for words that are really there.",
                  Write(rule[0]), Succession(Wait(2.2), FadeIn(rule[1])), run_time=4.0)
        chk = VGroup(T("Quick check: a line says", 28), M("disk.full.warning", 28, CARD_C)).arrange(RIGHT, buff=0.25)
        chk2 = VGroup(T("Does a search for", 28), M("full", 28, ASK_C), T("find it?", 28)).arrange(RIGHT, buff=0.2)
        chkg = VGroup(chk, chk2).arrange(DOWN, buff=0.3).move_to(DOWN * 0.9)
        self.beat("A quick check. A log line says disk.full.warning. Does a search for full find it? Pause and think.",
                  FadeIn(chkg, shift=UP * 0.15), run_time=2.4)
        self.pause([0, -2.4, 0], text="pause and think")
        ans = VGroup(T("No:", 28, RED_M), T("dots between letters keep it one token", 28)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.4)
        self.beat("No. Dots between letters keep the whole name as one token. Search for the whole name, and check with analyze if you are not sure.",
                  FadeIn(ans, shift=UP * 0.1), run_time=2.2)
        self.beat("Next, many copies of our app will share this one store. How do we know which copy wrote each line?",
                  FadeOut(VGroup(chkg, ans)), rule.animate.set_opacity(0.4), run_time=1.6)
        self.wait(1.0)
