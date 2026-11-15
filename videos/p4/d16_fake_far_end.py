import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bgh-runs\b", "G H runs"), (r"\baws-report\b", "A W S report"), (r"\burllib3\b", "U R L lib three"),
            (r"\bGITHUB_TOKEN\b", "github token"), (r"\braise_for_status\b", "raise for status"), (r"\.json\(\)", "dot jay-son"),
            (r"\bboto3\b", "bo-toe three"), (r"\bmock_aws\b", "mock A W S"), (r"\bmoto\b", "moe-toe"), (r"\bpytest\b", "pie test"),
            (r"\bbackoff=0\b", "backoff equals zero"), (r"\bConnectionError\b", "connection error"), (r"\bIAM\b", "I A M"),
            (r"\b502\b", "five oh two"), (r"\b503\b", "five oh three"), (r"\b504\b", "five oh four"), (r"\b500\b", "five hundred"),
            (r"\b404\b", "four oh four"), (r"\b401\b", "four oh one"), (r"\b429\b", "four twenty-nine"), (r"\b200\b", "two hundred")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def code_chip(text, color, size=22):
    return chip(text, color, size, mono=True)


class D16FakeFarEnd(VoiceScene):
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

    def run_dot(self, pts, color=YELLOW_M, rt=1.2):
        d = Dot(radius=0.09, color=color).move_to(pts[0])
        p = VMobject().set_points_as_corners(pts)
        return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, p, rate_func=smooth, run_time=rt), FadeOut(d, run_time=0.15))

    def construct(self):
        self.title_card("A real service in a run, a fake one in a test", "requests, retries, responses and moto")

        Y = 1.3
        code = mbox("gh-runs", TEAL_M, size=26, w=1.9, h=0.8).move_to([-5.5, Y, 0])
        gh = mbox("api.github.com", GREY_B, size=24, w=2.8, h=0.8).move_to([4.85, Y, 0])
        self.beat("The lab's gh-runs tool lists a repo's recent GitHub Actions runs, and exits 1 when one of them failed.",
                  FadeIn(code), Succession(Wait(1.2), FadeIn(gh)), run_time=2.6)
        get = M("GET /repos/OWNER/REPO/actions/runs", 22, GREY_B).move_to([0, 2.6, 0])
        straight = Arrow(code.get_right(), gh.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.03)
        self.beat("It asks with one GET request to the GitHub API. Let's follow that request through the code.",
                  Write(get), GrowArrow(straight), Succession(Wait(1.4), travel(straight, YELLOW_M, 1.2)), run_time=3.2)

        ses = box("Session", BLUE_M, w=1.9, h=0.8, size=26).move_to([-2.85, Y, 0])
        ret = box("urllib3 Retry", PURPLE_M, w=2.3, h=0.8, size=24).move_to([-0.2, Y, 0])
        wall = DashedLine([1.75, 2.15, 0], [1.75, -0.2, 0], dash_length=0.1, stroke_width=2, color=GREY_D)
        wl = T("network", 20, GREY_B).next_to(wall, DOWN, buff=0.1)
        a1, a2 = edge_arrow(code, ses), edge_arrow(ses, ret)
        a3 = Arrow(ret.get_right(), gh.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        hdr = VGroup(M("Accept: application/vnd.github+json", 20), M("X-GitHub-Api-Version: 2026-03-10", 20),
                     M("Authorization: Bearer <token from GITHUB_TOKEN>", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        hdr.move_to([-2.2, -0.9, 0]).align_to(code, LEFT)
        self.steps("It starts in a requests Session. The session keeps the connection open, and sends the same headers with every call.",
                   (1.0, FadeOut(straight), FadeIn(ses), GrowArrow(a1)), (1.0, Wait(1.0)),
                   (1.6, LaggedStart(*[FadeIn(h, shift=RIGHT * 0.1) for h in hdr], lag_ratio=0.3)))
        self.beat("The media type GitHub recommends, a pinned API version, and the token, read from the GITHUB_TOKEN environment variable. It is never printed.",
                  Indicate(hdr[0], color=WHITE), Succession(Wait(1.8), Indicate(hdr[1], color=WHITE)), Succession(Wait(3.0), Indicate(hdr[2], color=BLUE_M)), run_time=4.4)
        to = code_chip("timeout=(3.05, 10)", YELLOW_M).next_to(ses, DOWN, buff=0.3)
        self.beat("Always pass a timeout. Requests has no default, so a server that never answers hangs your script forever.",
                  FadeOut(hdr), FadeIn(to, shift=UP * 0.1), run_time=2.0)
        self.beat("Under the hood, requests sends every call through urllib3, a lower-level HTTP library. The lab gives the session a Retry.",
                  FadeIn(ret), GrowArrow(a2), run_time=2.0)
        self.steps("Then the request crosses the network to GitHub.",
                   (0.6, Create(wall), FadeIn(wl), GrowArrow(a3)),
                   (1.4, self.run_dot([code.get_right(), ses.get_center(), ret.get_center(), gh.get_left()], YELLOW_M, 1.4)))

        # the answer comes back
        def back(label, color, stop=None):
            c = code_chip(label, color, 22).move_to(gh.get_center() + DOWN * 0.95)
            return c

        ok = back("200 + JSON", GREEN_M)
        path_back = [gh.get_left(), ret.get_center(), ses.get_center(), code.get_right()]
        rs = code_chip("raise_for_status()", GREEN_M).next_to(code, DOWN, buff=0.3)
        js = code_chip(".json()", GREEN_M).next_to(rs, DOWN, buff=0.15)
        self.steps("GitHub answers. Call raise_for_status first: a 404 or a 500 is not an exception in requests until you ask for one. Then read the body with .json().",
                   (0.6, FadeIn(ok, shift=UP * 0.1)), (1.4, self.run_dot(path_back, GREEN_M, 1.4)), (1.0, FadeIn(rs)), (2.4, Wait(2.4)), (0.8, FadeIn(js)))

        # retries
        self.play(FadeOut(VGroup(ok, rs, js)), run_time=0.4)
        bad = back("502", RED_M)
        wt = T("wait, then ask again", 22, PURPLE_M).next_to(ret, DOWN, buff=0.3)
        self.steps("Now GitHub has a bad moment, and answers 502.",
                   (1.2, self.run_dot([code.get_right(), ses.get_center(), ret.get_center(), gh.get_left()], YELLOW_M, 1.2)),
                   (0.5, FadeIn(bad, shift=UP * 0.1)), (0.8, self.run_dot([gh.get_left(), ret.get_center()], RED_M, 0.8)))
        bo = M("waits 0, then 2, then 4 s", 20, PURPLE_M).next_to(wt, DOWN, buff=0.12)
        ok2 = back("200 + JSON", GREEN_M)
        self.steps("Asking again can help here. So Retry waits, and sends it again. With a backoff factor of 1, it waits 0, then 2, then 4 seconds.",
                   (0.6, FadeIn(wt)), (0.8, self.run_dot([ret.get_center(), gh.get_left()], YELLOW_M, 0.8)),
                   (0.5, Transform(bad, ok2)), (1.0, self.run_dot(path_back, GREEN_M, 1.0)), (1.0, Wait(1.0)), (0.6, FadeIn(bo)))
        lst = code_chip("retry: 429, 500, 502, 503, 504", PURPLE_M, 20).move_to([-0.2, -1.6, 0])
        nf = back("404", RED_M)
        self.steps("The lab retries only when asking again can help: a 429, or a 500, 502, 503 or 504. A 404 or a 401 is never retried, because the answer will not change.",
                   (0.6, FadeOut(VGroup(wt, bo)), FadeIn(lst)), (2.4, Wait(2.4)), (0.6, Transform(bad, nf)),
                   (1.4, self.run_dot(path_back, RED_M, 1.4)), (0.4, Indicate(code, color=RED_M)))
        gm = code_chip('allowed_methods=["GET"]', PURPLE_M, 20).next_to(lst, DOWN, buff=0.15)
        self.beat("And only for GET. A repeated GET is harmless, while a repeated POST may start two deploys.",
                  FadeIn(gm, shift=UP * 0.1), run_time=1.8)

        # 2. tests: fake the far end
        self.play(FadeOut(VGroup(bad, lst, gm, to)), run_time=0.4)
        hard = T("a 502 on purpose?", 26, YELLOW_M).move_to([0, -0.6, 0])
        self.beat("So how do you test the 502 case? You cannot make GitHub fail on purpose. And tests that call the real service are slow, flaky, and need secrets in CI.",
                  FadeIn(hard), Succession(Wait(2.8), Wiggle(gh)), run_time=4.0)
        resp = RoundedRectangle(corner_radius=0.14, width=3.0, height=2.3, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.12), opacity=1).move_to([4.85, Y - 0.55, 0])
        rt = M("responses", 24, GREEN_M).move_to(resp.get_top() + DOWN * 0.35)
        q = VGroup(M("1st: 502", 22, RED_M), M("2nd: 200", 22, GREEN_M)).arrange(DOWN, buff=0.16, aligned_edge=LEFT).next_to(rt, DOWN, buff=0.3)
        tlab = T("under pytest", 22, GREEN_M).next_to(resp, DOWN, buff=0.15)
        self.steps("Replace the service, and keep your code as it is. The responses library replaces the step where requests hands data to the network.",
                   (0.6, FadeOut(hard)), (1.2, gh.animate.set_opacity(0.15)), (1.4, Wait(1.4)),
                   (1.2, FadeIn(resp), FadeIn(rt), FadeIn(tlab)))
        self.beat("The test registers canned answers, in order. A 502, then a 200.",
                  LaggedStart(*[FadeIn(x, shift=RIGHT * 0.1) for x in q], lag_ratio=0.5), run_time=1.8)
        rl = resp.get_left()
        ok3 = T("retry proven", 22, GREEN_M).next_to(code, DOWN, buff=0.3)
        b0 = T("backoff=0: no sleeping", 20, PURPLE_M).next_to(ret, DOWN, buff=0.3)
        self.steps("Run the same code. The first answer is the 502. Retry asks again, and gets the 200. That proves the retry works. The test sets backoff=0, so it does not sleep.",
                   (1.0, self.run_dot([code.get_right(), ses.get_center(), ret.get_center(), rl], YELLOW_M, 1.0)), (0.4, Indicate(q[0], color=RED_M)),
                   (0.6, self.run_dot([rl, ret.get_center()], RED_M, 0.6)), (0.6, self.run_dot([ret.get_center(), rl], YELLOW_M, 0.6)),
                   (0.4, Indicate(q[1], color=GREEN_M)), (1.0, self.run_dot([rl, ret.get_center(), ses.get_center(), code.get_right()], GREEN_M, 1.0)),
                   (0.6, FadeIn(ok3)), (1.2, Wait(1.2)), (0.6, FadeIn(b0)))
        ce = code_chip("ConnectionError", RED_M, 20).next_to(wall, UP, buff=0.15).shift(DOWN * 0.0)
        self.steps("A request to any URL you did not register raises ConnectionError. So a test cannot reach the internet by accident.",
                   (1.2, self.run_dot([code.get_right(), ses.get_center(), ret.get_center(), wall.get_center() + UP * 0.0], RED_M, 1.2)),
                   (0.6, FadeIn(ce, shift=DOWN * 0.1)))
        self.play(FadeOut(VGroup(ok3, b0, ce, get)), run_time=0.4)

        # 3. AWS the same way: boto3 and moto
        Y2 = -2.0
        rep = mbox("aws-report", TEAL_M, size=24, w=2.1, h=0.8).move_to([-5.4, Y2, 0])
        cli = box("boto3 client", BLUE_M, w=2.3, h=0.8, size=24).move_to([-2.2, Y2, 0])
        aws = mbox("AWS", GOLD_M, size=26, w=2.0, h=0.8).move_to([4.85, Y2, 0])
        b1 = edge_arrow(rep, cli)
        b2 = Arrow(cli.get_right(), aws.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.05)
        wall2 = DashedLine([1.75, -1.2, 0], [1.75, -2.8, 0], dash_length=0.1, stroke_width=2, color=GREY_D)
        sg = T("signed HTTPS", 20, GREY_B).next_to(b2, UP, buff=0.12).shift(LEFT * 0.9)
        self.steps("AWS works the same way. boto3 turns each method call into an HTTPS request to an AWS API, signed with your credentials.",
                   (1.2, FadeIn(rep), GrowArrow(b1), FadeIn(cli)), (1.0, GrowArrow(b2), FadeIn(aws), Create(wall2), FadeIn(sg)),
                   (1.4, self.run_dot([rep.get_right(), cli.get_center(), aws.get_left()], YELLOW_M, 1.4)))
        mo = RoundedRectangle(corner_radius=0.14, width=3.0, height=1.2, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.12), opacity=1).move_to([0.2, Y2, 0])
        mot = VGroup(M("moto", 24, GREEN_M), T("fake AWS in memory", 20, GREY_B)).arrange(DOWN, buff=0.12).move_to(mo)
        self.steps("Inside mock_aws, moto catches each request just before it would be sent, and answers it from an in-memory fake AWS. That fake starts empty for each test.",
                   (1.0, aws.animate.set_opacity(0.15)), (1.0, FadeIn(mo), FadeIn(mot)), (1.2, self.run_dot([rep.get_right(), cli.get_center(), mo.get_left()], YELLOW_M, 1.2)),
                   (1.0, self.run_dot([mo.get_left(), cli.get_center(), rep.get_right()], GREEN_M, 1.0)))
        early = box("client made at import", RED_M, w=3.2, h=0.7, size=22).move_to([-1.6, -3.35, 0])
        leak = Arrow(early.get_right(), aws.get_corner(DL) + RIGHT * 0.3, buff=0.12, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.08)
        self.steps("One rule from the moto docs. Start the mock before you create any client. A client made earlier, for example at import time, is not mocked. It can reach real AWS, with whatever keys your shell holds.",
                   (1.6, Wait(1.6)), (1.0, FadeIn(early)), (1.0, Wait(1.0)), (0.8, GrowArrow(leak), aws.animate.set_opacity(1)),
                   (1.2, self.run_dot([early.get_right(), aws.get_corner(DL) + RIGHT * 0.3], RED_M, 1.2)))
        self.play(FadeOut(VGroup(early, leak)), aws.animate.set_opacity(0.15), run_time=0.5)
        iam = T("does not check IAM permissions by default", 22, YELLOW_M).move_to([0.2, -3.3, 0])
        self.beat("And moto is a model of AWS, not AWS. It does not check IAM permissions unless you ask. So run a new check once against a real account, before you trust it.",
                  FadeIn(iam, shift=UP * 0.1), Succession(Wait(3.2), aws.animate.set_opacity(1)), run_time=4.2)

        # 4. recap
        self.play(FadeOut(iam), run_time=0.4)
        rc = T("same code: the real service in a run, a fake one under pytest", 26, WHITE).move_to([0, -3.3, 0])
        fit(rc, 12.6)
        self.beat("So the code never changes. In a run it talks to the real service. Under pytest, the far end is fake, and you can make it fail any way you like.",
                  FadeIn(rc, shift=UP * 0.1), Indicate(resp, color=GREEN_M, scale_factor=1.04), Indicate(mo, color=GREEN_M, scale_factor=1.04), run_time=4.0)
        self.wait(1.2)
