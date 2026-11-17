import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\braise_for_status\(\)", "raise for status"), (r"\bmoto\b", "moe-toe"), (r"\bpytest\b", "pie test"),
            (r"\bOrderedRegistry\b", "ordered registry"), (r"\bConnectionError\b", "connection error"),
            (r"\bbackoff=0\b", "backoff equals zero"), (r"\b3\.05\b", "three point oh five")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color=WHITE, s=1.0):
    head = Circle(radius=0.28, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), opacity=1)
    body = RoundedRectangle(corner_radius=0.35, width=0.95, height=0.85, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), opacity=1)
    body.next_to(head, DOWN, buff=0.08)
    return VGroup(head, body).scale(s)


def clock(color=YELLOW_M, r=0.5):
    face = Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), opacity=1)
    hand = Line(ORIGIN, UP * r * 0.8, stroke_width=4, color=color)
    return VGroup(face, hand)


class D16SilentPhone(VoiceScene):
    def steps(self, text, *plays):
        path, dur = voice(text)
        self._cue(text, dur)
        self.add_sound(path)
        t0 = self.renderer.time
        for rt, *anims in plays:
            self.play(*anims, run_time=rt)
        left = dur - (self.renderer.time - t0)
        if left > 0.02:
            self.wait(left)
        self.wait(0.25)

    def construct(self):
        self.title_card("The silent phone", "hang up in time, call back only when it helps, and rehearse with a friend")

        # 1. the helper phones the supplier
        helper = person(WHITE).move_to([-4.6, 0.2, 0])
        hl = T("helper", 26, GREY_B).next_to(helper, DOWN, buff=0.25)
        sup = person(GOLD_M).move_to([4.6, 0.2, 0])
        sl = T("supplier", 26, GOLD_M).next_to(sup, DOWN, buff=0.25)
        wire = Line(helper.get_right() + RIGHT * 0.25, sup.get_left() + LEFT * 0.25, stroke_width=3, color=GREY_B)
        back = Line(wire.get_end(), wire.get_start())
        self.beat("Our helper has a new morning job. Phone the supplier, and ask which of yesterday's orders went wrong.",
                  FadeIn(helper, shift=UP * 0.2), FadeIn(hl), FadeIn(sup, shift=UP * 0.2), FadeIn(sl), Create(wire), run_time=2.2)
        ans = T("\"orders 12 and 15\"", 26, GOLD_M).next_to(wire, UP, buff=0.3)
        self.steps("Most days, that takes a minute. Question out, answer back, done.",
                   (0.8, travel(wire, WHITE, 0.8)), (0.8, travel(back, GOLD_M, 0.8), FadeIn(ans)))
        self.play(FadeOut(ans), run_time=0.4)
        clk = clock().move_to([0, 2.3, 0])
        tl = T("waiting", 26, YELLOW_M).next_to(clk, RIGHT, buff=0.3)
        self.steps("One morning, the supplier picks up, says nothing, and never hangs up.",
                   (0.8, travel(wire, WHITE, 0.8)), (0.5, FadeIn(clk), FadeIn(tl)), (2.0, Rotate(clk[1], -TAU, about_point=clk[0].get_center())))
        noon = T("noon", 28, YELLOW_M).move_to(tl, aligned_edge=LEFT)
        self.beat("The helper was told to call and wait for the answer. So it stands there with the phone at its ear, until you come back at noon. No report. And no error either.",
                  Rotate(clk[1], -3 * TAU, about_point=clk[0].get_center()), Transform(tl, noon), run_time=5.0)
        q = T("how long should a script wait? and how do you test the bad days?", 28, YELLOW_M).move_to([0, -2.6, 0])
        fit(q, 12.4)
        self.beat("A call that never ends does not look like a failure. It just looks slow. So two questions for today. How long should a script wait? And how do you test the bad days, without the internet?",
                  FadeIn(q, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(VGroup(q, clk, tl)), run_time=0.5)

        # 2. map: the phone call is a web request
        api = mbox("api.github.com", GOLD_M, size=22).next_to(sup, UP, buff=0.35)
        self.beat("In computer terms, the supplier is a web service such as GitHub, where code and its automatic checks live. It opens a door for programs, called an API.",
                  FadeIn(api, shift=DOWN * 0.1), run_time=1.8)
        req = M("GET /repos/.../actions/runs", 22).next_to(wire, UP, buff=0.3)
        self.steps("The helper's question is a request, sent to a web address.",
                   (0.6, FadeIn(req, shift=UP * 0.1)), (0.8, travel(wire, WHITE, 0.8)))
        resp = VGroup(chip("200", GREEN_M, 26, mono=True), M("+ a JSON body", 22, GREEN_M)).arrange(RIGHT, buff=0.25).next_to(wire, DOWN, buff=0.3)
        self.steps("The answer comes back with a status code, like 200 for fine, or 404 for not found, and a body, often JSON text.",
                   (0.8, travel(back, GOLD_M, 0.8)), (0.6, FadeIn(resp, shift=DOWN * 0.1)))
        self.play(FadeOut(resp), run_time=0.4)

        # 3. predict: no timeout
        code = M("requests.get(url)", 26, BLUE_M).move_to([0, 2.6, 0])
        self.beat("In Python, the requests library makes that call in one line.", FadeIn(code, shift=DOWN * 0.1), FadeOut(req), run_time=1.2)
        self.steps("Now the silent morning. The server accepts the connection, and then never answers. How long does this line wait? Pause and guess.",
                   (2.5, Wait(2.5)), (0.8, travel(wire, WHITE, 0.8)), (0.6, sup.animate.set_opacity(0.35)))
        self.wait(2.0)
        clk = clock().move_to([0, -1.3, 0])
        forever = T("forever", 30, RED_M).next_to(clk, RIGHT, buff=0.35)
        self.beat("Forever. requests has no default timeout. As long as the connection stays open, it waits.",
                  FadeIn(clk), FadeIn(forever), Rotate(clk[1], -2 * TAU, about_point=clk[0].get_center()), run_time=3.4)
        self.beat("It is the most patient library you will ever meet, and that is exactly the problem.",
                  Rotate(clk[1], -TAU, about_point=clk[0].get_center()), run_time=2.0)
        code2 = M("requests.get(url, timeout=(3.05, 10))", 26, BLUE_M).move_to(code)
        parts = VGroup(T("up to 3.05 s to connect", 26, BLUE_M), T("then up to 10 s of silence", 26, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([0, -2.6, 0])
        self.steps("So we always pass a timeout. This one waits up to 3.05 seconds to connect, then up to 10 seconds of silence while the answer arrives.",
                   (0.8, Transform(code, code2), FadeOut(forever)), (1.2, Wait(1.2)), (0.6, FadeIn(parts[0])), (1.6, Wait(1.6)), (0.6, FadeIn(parts[1])))
        hang = T("hangs up: Timeout error", 28, GREEN_M).next_to(clk, RIGHT, buff=0.35)
        self.steps("After that, the helper hangs up and reports an error. Loud, early, and honest.",
                   (1.0, Rotate(clk[1], -PI / 2, about_point=clk[0].get_center())), (0.6, clk[0].animate.set_stroke(GREEN_M), FadeIn(hang)))
        rule = T("A call without a timeout is a promise to wait forever.", 30, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("Here is the rule. A call without a timeout is a promise to wait forever. Always set one.",
                  parts.animate.shift(UP * 0.15), FadeIn(rule, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(clk, hang, parts, rule)), sup.animate.set_opacity(1), run_time=0.6)

        # 4. call back? steelman 'retry everything', then break it
        code3 = M("session with Retry", 26, BLUE_M).move_to(code)
        self.beat("Next, the bad answers. You might think: easy, if anything goes wrong, just call back. Retry everything, three times.",
                  Transform(code, code3), run_time=1.4)
        busy = VGroup(chip("502", RED_M, 26, mono=True), T("line busy", 26, RED_M)).arrange(RIGHT, buff=0.25)
        nope = VGroup(chip("404", PURPLE_M, 26, mono=True), T("no such order", 26, PURPLE_M)).arrange(RIGHT, buff=0.25)
        key = VGroup(chip("401", PURPLE_M, 26, mono=True), T("bad key card", 26, PURPLE_M)).arrange(RIGHT, buff=0.25)
        bads = VGroup(busy, nope, key).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, -1.9, 0])
        self.steps("Let's be fair and try it on three bad days. The line is busy. The supplier says no such order. Or your key card, the token that proves who you are, is wrong.",
                   (0.6, FadeIn(busy, shift=UP * 0.1)), (2.2, Wait(2.2)), (0.6, FadeIn(nope, shift=UP * 0.1)), (1.6, Wait(1.6)), (0.6, FadeIn(key, shift=UP * 0.1)))
        tb = tick(True, 0.25).next_to(busy, RIGHT, buff=0.5)
        self.steps("Busy line? Calling back later can really help. Next time, someone picks up.",
                   (0.8, travel(wire, WHITE, 0.8)), (0.6, Create(tb)))
        n3 = T("same answer, 3 times", 26, RED_M).next_to(nope, RIGHT, buff=0.5)
        self.steps("No such order? Call back, and you hear no such order again. And again. The answer will not change.",
                   (0.6, travel(wire, WHITE, 0.6)), (0.6, travel(back, PURPLE_M, 0.6)), (0.6, travel(wire, WHITE, 0.6)), (0.6, travel(back, PURPLE_M, 0.6)), (0.5, FadeIn(n3)))
        n4 = T("same answer", 26, RED_M).next_to(key, RIGHT, buff=0.5)
        self.beat("Same for a bad key card. The supplier will not suddenly like your card on the third try.", FadeIn(n4), run_time=1.0)
        rset = VGroup(T("retry:", 26, GREEN_M), M("429  500  502  503  504", 24, GREEN_M), T("a dropped call", 26, GREEN_M)).arrange(RIGHT, buff=0.3)
        nset = VGroup(T("never retry:", 26, RED_M), M("401  404", 24, RED_M)).arrange(RIGHT, buff=0.3)
        sets = VGroup(rset, nset).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([0, -1.9, 0])
        self.steps("So the lab retries only when asking again can help. 429, too many requests. A 500, 502, 503 or 504. Or a dropped connection. Never a 401, and never a 404.",
                   (0.6, FadeOut(VGroup(bads, tb, n3, n4))), (0.8, FadeIn(rset, shift=UP * 0.1)), (5.0, Wait(5.0)), (0.8, FadeIn(nset, shift=UP * 0.1)))
        idem = T("and only GET: asking twice does no more than asking once", 26, BLUE_M).move_to([0, -3.3, 0])
        self.beat("And only for GET, the method for reading. A repeated GET is harmless. A repeated POST may start two deploys.",
                  FadeIn(idem, shift=UP * 0.1), run_time=1.2)
        self.play(FadeOut(VGroup(sets, idem)), run_time=0.5)

        # backoff: wait longer each time
        ax = Line([-5.0, -2.0, 0], [5.0, -2.0, 0], stroke_width=2, color=GREY_D)
        xs = [-4.6, -3.4, -0.9, 3.9]
        tries = VGroup(*[chip(t, c, 24, mono=True).move_to([x, -1.35, 0]) for t, c, x in zip(("502", "502", "502", "200"), (RED_M, RED_M, RED_M, GREEN_M), xs)])
        gaps = VGroup(*[T(w, 26, GREY_B).move_to([(a + b) / 2, -2.45, 0]) for w, a, b in zip(("0 s", "2 s", "4 s"), xs[:-1], xs[1:])])
        marks = VGroup(*[Line([x, -1.9, 0], [x, -2.1, 0], stroke_width=3, color=GREY_B) for x in xs])
        bl = T("backoff: wait longer after each failed try", 26, GREY_B).move_to([0, -3.15, 0])
        self.steps("If the line stays busy, the helper waits a little longer each time, so the server can recover. With a backoff factor of 1, that is zero, then two, then four seconds.",
                   (0.6, Create(ax), FadeIn(bl)), (0.6, FadeIn(tries[0]), Create(marks[0])), (1.6, Wait(1.6)),
                   (0.6, FadeIn(gaps[0]), FadeIn(tries[1]), Create(marks[1])), (0.8, FadeIn(gaps[1]), FadeIn(tries[2]), Create(marks[2])),
                   (1.0, FadeIn(gaps[2]), FadeIn(tries[3]), Create(marks[3])))
        tl = VGroup(ax, tries, gaps, marks, bl)
        self.beat("And if the server sends a Retry-After header, saying when to call back, it obeys that.",
                  Indicate(gaps[2], color=YELLOW_M), run_time=1.2)
        self.play(FadeOut(tl), run_time=0.5)

        # 5. how to test the bad days: the friend
        self.beat("So far so good. But how do you test the busy line? You cannot ask GitHub to be busy on Tuesday at ten so the helper can practise.",
                  Wiggle(api), run_time=1.6)
        slow = VGroup(T("slow", 26, RED_M), T("flaky", 26, RED_M), T("needs secrets", 26, RED_M)).arrange(RIGHT, buff=0.7).move_to([0, -2.0, 0])
        self.beat("And tests that call the real service are slow, flaky, which means they fail now and then for reasons outside your code, and they need secrets in CI.",
                  LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in slow], lag_ratio=0.5), run_time=3.0)
        self.play(FadeOut(slow), run_time=0.4)
        friend = person(TEAL_M).move_to(sup)
        fl = T("a friend", 26, TEAL_M).next_to(friend, DOWN, buff=0.25)
        card = VGroup(M("1st call: 502", 22, TEAL_M), M("2nd call: 200", 22, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        cr = RoundedRectangle(corner_radius=0.08, width=card.width + 0.4, height=card.height + 0.35, stroke_color=TEAL_M, stroke_width=2.5).set_fill(tint(TEAL_M, 0.1), opacity=1)
        script = VGroup(cr, card.move_to(cr)).next_to(friend, UP, buff=0.35)
        self.steps("So, a friend plays the supplier. The friend answers the phone and says whatever you wrote down.",
                   (0.8, FadeOut(sup), FadeOut(sl), FadeOut(api), FadeIn(friend), FadeIn(fl)), (1.4, Wait(1.4)), (0.8, FadeIn(script, shift=DOWN * 0.1)))
        self.beat("Notice what did not change. The helper is the same. Its checklist is the same. Only the far end of the line is pretend.",
                  Indicate(helper[0], color=WHITE), Indicate(wire, color=WHITE), run_time=2.0)

        # map: responses and the test
        lib = mbox("responses", TEAL_M, size=24).next_to(script, LEFT, buff=0.4)
        self.beat("In Python, that friend is a library called responses. It steps in exactly where requests hands data to the network.",
                  FadeIn(lib, shift=RIGHT * 0.1), run_time=1.6)
        reg = M("registries.OrderedRegistry", 22, TEAL_M).next_to(code, DOWN, buff=0.2)
        self.beat("The test writes the answers down in order. A 502 first, then a 200.",
                  FadeIn(reg), Indicate(card[0], color=TEAL_M), Succession(Wait(0.6), Indicate(card[1], color=TEAL_M)), run_time=2.0)
        self.beat("Now we run the real code against the friend. What will the test see? Pause and guess.", run_time=None)
        self.wait(2.0)
        r1 = chip("502", RED_M, 24, mono=True).next_to(wire, DOWN, buff=0.3).shift(LEFT * 1.0)
        r2 = chip("200", GREEN_M, 24, mono=True).next_to(wire, DOWN, buff=0.3).shift(RIGHT * 1.0)
        self.steps("First call: 502. The line is busy, so Retry calls back. Second call: 200. The run passes, and that proves the retry works.",
                   (0.7, travel(wire, WHITE, 0.7)), (0.7, travel(back, RED_M, 0.7), FadeIn(r1)), (1.8, Wait(1.8)),
                   (0.7, travel(wire, WHITE, 0.7)), (0.7, travel(back, GREEN_M, 0.7), FadeIn(r2)))
        b0 = M("backoff=0", 22, TEAL_M).next_to(reg, DOWN, buff=0.15)
        self.beat("The test passes backoff=0, so it does not even sleep between the calls.", FadeIn(b0), run_time=1.2)
        stray = T("a number you never wrote down", 26, RED_M).move_to([0, -2.4, 0])
        cerr = M("ConnectionError", 24, RED_M).next_to(stray, DOWN, buff=0.2)
        self.steps("And if the helper dials a number you never wrote down, the friend raises ConnectionError. So a test cannot reach the real internet by accident.",
                   (0.8, FadeIn(stray, shift=UP * 0.1)), (1.6, Wait(1.6)), (0.6, FadeIn(cerr)))
        self.play(FadeOut(VGroup(stray, cerr, r1, r2)), run_time=0.4)
        mock = T("a stand-in like this is called a mock", 28, TEAL_M).move_to([0, -2.4, 0])
        tests = M("8 passed in 0.12s", 24, GREEN_M).next_to(mock, DOWN, buff=0.25)
        self.steps("A stand-in like this has a name. It is called a mock. The lab's eight GitHub tests use one, and they run in about a tenth of a second, with no network.",
                   (0.8, FadeIn(mock, shift=UP * 0.1)), (2.6, Wait(2.6)), (0.6, FadeIn(tests)))
        self.play(FadeOut(VGroup(mock, tests, reg, b0)), run_time=0.4)

        # 6. AWS: moto, and its limit
        moto = mbox("moto: a fake AWS in memory", TEAL_M, size=22).move_to(lib, aligned_edge=RIGHT)
        self.beat("Amazon's cloud gets a friend too. Inside a test, moto catches each request just before it would be sent, and answers from a fake AWS that lives only in memory, and starts empty for every test.",
                  Transform(lib, moto), Transform(code, M("boto3 client", 26, BLUE_M).move_to(code)), run_time=2.0)
        lim = VGroup(T("moto does not check permissions", 28, RED_M), T("unless you ask it to", 26, GREY_B)).arrange(DOWN, buff=0.15).move_to([0, -2.3, 0])
        self.beat("But a friend is not the supplier. moto does not check permissions, the rules for who may do what, unless you ask it to. So a test can pass while the real account would say access denied.",
                  FadeIn(lim, shift=UP * 0.1), run_time=1.6)
        rule2 = T("A fake proves your logic, not your permissions.", 30, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("So here is the guardrail. A fake proves your logic, not your permissions. Run a new check once against a real account before you trust it.",
                  FadeIn(rule2, shift=UP * 0.1), run_time=1.4)
        first = T("and start the mock before you create any client", 26, GREY_B).move_to(lim[1])
        self.beat("One more rule from the moto docs. Start the mock before you create any client. A client made earlier is not mocked.",
                  Transform(lim[1], first), run_time=1.4)
        self.play(FadeOut(VGroup(lim, rule2, script, lib)), run_time=0.5)

        # 7. moral and quick check
        mor = VGroup(T("hang up in time", 28, BLUE_M), T("call back only when it can help", 28, GREEN_M),
                     T("rehearse with a friend, then try the real thing once", 28, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.3, 0])
        self.steps("So, the helper's new habits. Hang up in time. Call back only when it can help. And rehearse with a friend, then try the real thing once.",
                   (0.6, FadeIn(mor[0], shift=UP * 0.1)), (1.2, Wait(1.2)), (0.6, FadeIn(mor[1], shift=UP * 0.1)), (1.2, Wait(1.2)), (0.6, FadeIn(mor[2], shift=UP * 0.1)))
        self.play(FadeOut(mor), run_time=0.4)
        quiz = T("Quick check: the answer is 401, bad token. Call back?", 28, YELLOW_M).move_to([0, -2.6, 0])
        self.beat("Quick check before you go. The answer is a 401. Your token is wrong. Should the helper call back?",
                  FadeIn(quiz, shift=UP * 0.1), run_time=1.2)
        self.wait(2.0)
        no = T("No. The answer will not change. Fix the token instead.", 28, GREEN_M).next_to(quiz, DOWN, buff=0.3)
        self.beat("No. The answer will not change. Fix the token instead.", FadeIn(no, shift=UP * 0.1), run_time=1.0)
        self.wait(1.2)
