import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bOIDC\b", "O I D C"), (r"sts:AssumeRoleWithWebIdentity", "S T S, assume role with web identity"),
            (r"\bsub\b", "sub"), (r"\baud\b", "awd"), (r"\bhello-devops-", "hello devops dash"),
            (r"\bid-token: write\b", "I D token write"), (r"\bpull_request\b", "pull request")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color=BLUE_M, s=1.0):
    head = Circle(radius=0.22, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1).shift(UP * 0.42)
    body = Arc(radius=0.4, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).shift(DOWN * 0.32)
    base = Line(LEFT * 0.4, RIGHT * 0.4, stroke_color=color, stroke_width=3).shift(DOWN * 0.32)
    return VGroup(head, body, base).scale(s)


def key_shape(color=GOLD_M, s=1.0):
    ring = Circle(radius=0.18, stroke_color=color, stroke_width=4)
    shaft = Line(RIGHT * 0.18, RIGHT * 0.75, stroke_color=color, stroke_width=4)
    t1 = Line(RIGHT * 0.6, RIGHT * 0.6 + DOWN * 0.16, stroke_color=color, stroke_width=4)
    t2 = Line(RIGHT * 0.72, RIGHT * 0.72 + DOWN * 0.12, stroke_color=color, stroke_width=4)
    return VGroup(ring, shaft, t1, t2).scale(s)


def card_shape(color=GREEN_M, s=1.0):
    r = RoundedRectangle(corner_radius=0.06, width=0.8, height=0.52, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    stripe = Line(LEFT * 0.32, RIGHT * 0.32, stroke_color=color, stroke_width=4).shift(UP * 0.1)
    return VGroup(r, stripe).scale(s)


def house():
    body = Rectangle(width=2.4, height=1.6, stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.08), 1)
    roof = Polygon(body.get_corner(UL) + LEFT * 0.25, body.get_corner(UR) + RIGHT * 0.25, body.get_top() + UP * 1.0,
                   stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.05), 1)
    door = Rectangle(width=0.55, height=0.95, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.12), 1)
    door.align_to(body, DOWN)
    mat = Rectangle(width=1.0, height=0.16, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.3), 1)
    mat.next_to(body, DOWN, buff=0.06)
    return VGroup(body, roof, door, mat)


def panel(rows, color, buff=0.26):
    fr = RoundedRectangle(corner_radius=0.12, width=rows.width + 2 * buff, height=rows.height + 2 * buff, stroke_color=color, stroke_width=2.5)
    fr.set_fill(tint(color, 0.10), 1)
    return VGroup(fr, rows.move_to(fr))


class D35KeyCard(VoiceScene):
    def steps(self, text, *plays):
        """Speak one line while several animations run one after another inside it."""
        path, dur = voice(text)
        self._cue(text, dur)
        self.add_sound(path)
        t0 = self.renderer.time
        for rt, *anims in plays:
            anims = [x() if callable(x) and getattr(x, "__name__", "") == "<lambda>" else x for x in anims]
            self.play(*anims, run_time=rt)
        left = dur - (self.renderer.time - t0)
        if left > 0.02:
            self.wait(left)
        self.wait(0.25)

    def construct(self):
        self.title_card("A key under the doormat, or a hotel card?", "how a pipeline gets into AWS without a stored key")

        # ---------- 1. the shy question
        pipe = box("pipeline", BLUE_M, w=2.6, size=28).move_to([-4.2, 0.3, 0])
        cloud = RoundedRectangle(corner_radius=0.2, width=3.6, height=2.4, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.06), 1).move_to([4.0, 0.3, 0])
        cl = T("AWS", 30, GOLD_M).move_to(cloud.get_top() + DOWN * 0.45)
        lock = VGroup(RoundedRectangle(corner_radius=0.06, width=0.6, height=0.5, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.2), 1),
                      Arc(radius=0.2, start_angle=0, angle=PI, stroke_color=GOLD_M, stroke_width=3).shift(UP * 0.25)).move_to(cloud.get_center() + DOWN * 0.3)
        gap = DashedLine(pipe.get_right() + RIGHT * 0.2, cloud.get_left() + LEFT * 0.2, dash_length=0.12, color=GREY_B)
        self.beat("Here's a question that sounds simple. A pipeline, the robot on GitHub that runs plan and apply for you, has to get into AWS, Amazon's cloud.",
                  FadeIn(pipe), Create(cloud), FadeIn(cl), FadeIn(lock), Create(gap), run_time=3.0)
        q = T("no phone, no password... so how does AWS let it in?", 30, YELLOW_M).move_to([0, -2.4, 0])
        self.beat("It's not a person. It has no phone for a code and no password in its head. So how does AWS know it's allowed in?",
                  FadeIn(q, shift=UP * 0.15), run_time=2.0)
        self.wait(0.6)
        self.play(FadeOut(VGroup(pipe, cloud, cl, lock, gap, q)), run_time=0.6)

        # ---------- 2. familiar: the key under the doormat
        h = house().move_to([-3.2, 0.4, 0])
        mat = h[3]
        k = key_shape(GOLD_M, 0.9).move_to(mat.get_center() + UP * 0.05)
        self.beat("Let's leave computers for a minute. You're away for two weeks while a builder works on your house. The quick way to let them in? A spare key under the doormat.",
                  Create(h[0]), Create(h[1]), FadeIn(h[2]), Succession(Wait(3.5), AnimationGroup(FadeIn(mat), FadeIn(k, shift=DOWN * 0.3))), run_time=6.0)
        day = T("day 1", 30, TEAL_M).move_to([2.8, 1.6, 0])
        b1 = person(TEAL_M, 0.8).move_to([1.6, -0.4, 0])
        works = T("door opens", 26, GREEN_M).next_to(b1, DOWN, buff=0.3)
        self.beat("On day one, it works. The builder lifts the mat, and in they go.",
                  FadeIn(day), FadeIn(b1, shift=LEFT * 0.2), Succession(Wait(1.0), k.animate.next_to(b1, UP, buff=0.15)), FadeIn(works), run_time=2.4)
        self.play(k.animate.move_to(mat.get_center() + UP * 0.05), run_time=0.6)
        day2 = T("day 400", 30, RED_M).move_to(day)
        b2 = person(RED_M, 0.8).move_to([3.6, -0.4, 0])
        works2 = T("door still opens", 26, RED_M).next_to(b2, DOWN, buff=0.3)
        self.beat("It still works in a year. And it works for anyone who lifts the mat, builder or not.",
                  Transform(day, day2), FadeIn(b2, shift=LEFT * 0.2), Succession(Wait(1.6), AnimationGroup(k.animate.next_to(b2, UP, buff=0.15), FadeIn(works2))), run_time=3.6)
        self.beat("Under the doormat isn't really a hiding place. It's the first place anyone looks, right after the flowerpot.",
                  Indicate(mat, color=TEAL_M, scale_factor=1.3), run_time=1.6)
        self.play(FadeOut(VGroup(h, k, day, b1, b2, works, works2)), run_time=0.6)

        # ---------- 3. pain: the stored access key
        sec = RoundedRectangle(corner_radius=0.15, width=4.2, height=1.8, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.08), 1).move_to([-3.8, 1.0, 0])
        secl = T("GitHub secret", 28, TEAL_M).next_to(sec, UP, buff=0.18)
        ak = chip("AWS access key", GOLD_M, 28).move_to(sec)
        self.beat("The pipeline has its own doormat. The quick way is an AWS access key, saved as a GitHub secret, a hidden setting the pipeline can read.",
                  Create(sec), FadeIn(secl), FadeIn(ak, scale=1.2), run_time=3.0)
        axis = Line([-5.6, -1.9, 0], [5.6, -1.9, 0], stroke_color=GREY_B, stroke_width=2)
        ticks = VGroup(*[T(t, 22, GREY_B).move_to([x, -2.4, 0]) for t, x in (("saved", -5.4), ("a month", -2.0), ("months later", 2.2), ("until someone deletes it", 4.1))])
        bar = Rectangle(width=0.01, height=0.32, stroke_width=0).set_fill(GOLD_M, 0.8).move_to([-5.6, -1.6, 0], aligned_edge=LEFT)
        self.beat("That key works until someone deletes it. Nothing about it expires.",
                  Create(axis), FadeIn(ticks[0]), run_time=1.6)
        leak = ak.copy()
        self.steps("So if it ever leaks, the stolen copy stays useful for months, quietly, for whoever has it.",
                   (1.0, leak.animate.move_to([3.6, 1.0, 0]).set_color(RED_M)),
                   (2.6, bar.animate.stretch_to_fit_width(11.2).move_to([-5.6, -1.6, 0], aligned_edge=LEFT), LaggedStart(*[FadeIn(t) for t in ticks[1:]], lag_ratio=0.5)))
        wish = T("wish: a key that opens one room, and stops working by itself", 28, YELLOW_M).move_to([0, -0.5, 0])
        self.beat("Wouldn't it be nice if the pipeline got a key that opened only one room, and stopped working on its own?",
                  FadeIn(wish, shift=UP * 0.15), run_time=2.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(sec, secl, ak, leak, axis, ticks, bar, wish)), run_time=0.6)

        # ---------- 4. analogy: the hotel desk
        Y, Y2 = 0.7, -1.75
        guest = person(BLUE_M).move_to([-5.2, Y, 0])
        gl = T("you", 26, BLUE_M).next_to(guest, DOWN, buff=0.2)
        office = box("ID office", GREY_B, w=2.4, size=26).move_to([-5.2, Y2, 0])
        desk = box("front desk", GOLD_M, w=2.6, size=28).move_to([-0.6, Y, 0])
        blist = panel(VGroup(T("booking list", 24, PURPLE_M), M("you, room 12", 22)).arrange(DOWN, buff=0.12), PURPLE_M).move_to([-0.6, Y2, 0])
        room = box("room 12", GREEN_M, w=2.2, size=28).move_to([4.6, Y, 0])
        self.beat("A hotel does it differently. You walk up to the front desk.",
                  FadeIn(guest), FadeIn(gl), FadeIn(desk), FadeIn(room), run_time=2.2)
        idc = card_shape(GREY_B, 0.8).next_to(guest, RIGHT, buff=0.25)
        idl = T("ID", 22, GREY_B).next_to(idc, UP, buff=0.1)
        self.beat("You show your ID. The desk doesn't know you, but it knows the office that stamped that ID, and it can tell a real stamp from a fake.",
                  FadeIn(office), Succession(Wait(0.8), AnimationGroup(FadeIn(idc, shift=RIGHT * 0.2), FadeIn(idl))),
                  Succession(Wait(2.6), idc.animate.move_to(desk.get_left() + LEFT * 0.7)), Succession(Wait(2.6), idl.animate.move_to(desk.get_left() + LEFT * 0.7 + UP * 0.5)), run_time=5.0)
        ck1 = tick(True, 0.16).next_to(desk, UP, buff=0.15).shift(LEFT * 0.4)
        self.beat("Then it checks a second thing: is the name on that ID on tonight's booking list?",
                  FadeIn(blist, shift=UP * 0.15), Create(ck1), run_time=2.4)
        ck2 = tick(True, 0.16).next_to(ck1, RIGHT, buff=0.25)
        kc = card_shape(GREEN_M, 0.9).next_to(desk, RIGHT, buff=0.3)
        self.steps("Both yes? It hands you a key card. The card opens room twelve, nothing else. And at checkout, it simply stops working.",
                   (0.6, Create(ck2)), (0.8, FadeIn(kc, scale=0.6)), (1.4, kc.animate.next_to(room, LEFT, buff=0.25)),
                   (0.8, Indicate(room[1], color=GREEN_M)), (1.0, lambda: kc.animate.set_opacity(0.25)))
        self.beat("Nobody had to remember to cancel it. The card cancels itself.", Wait(0.1), run_time=0.4)

        # ---------- 5. map every part out loud
        def swap(old, new, rt=0.9):
            return (rt, ReplacementTransform(old, new))
        job = box("plan job", BLUE_M, w=2.4, size=28).move_to(guest)
        self.steps("Let's map it. You, the guest, are the pipeline's job.", (0.3, Wait(0.3)), swap(VGroup(guest, gl), job))
        gh = box("GitHub", GREY_B, w=2.4, size=28).move_to(office)
        tok = chip("token", PURPLE_M, 24).move_to(idc)
        self.steps("The ID office is GitHub. It signs a pass for the job, called a token. It's short lived, and it soon expires.",
                   (0.3, Wait(0.3)), swap(office, gh), (1.2, Wait(1.2)), swap(VGroup(idc, idl), tok))
        aws = box("AWS", GOLD_M, w=2.6, size=30).move_to(desk)
        trust = panel(VGroup(T("trust policy", 24, PURPLE_M), M("repo: you/hello-devops", 22)).arrange(DOWN, buff=0.12), PURPLE_M).move_to(blist)
        self.steps("The front desk is AWS. The booking list is the role's trust policy, the part that says who may use it.",
                   (0.3, Wait(0.3)), swap(desk, aws), (1.6, Wait(1.6)), swap(blist, trust))
        cred = chip("short-lived credentials", GREEN_M, 22).next_to(room, DOWN, buff=0.4)
        perm = box("role's permissions", GREEN_M, w=3.2, size=26).move_to(room)
        self.steps("The key card is a set of short-lived AWS credentials. And room twelve is what the role may touch, its permissions.",
                   (0.3, Wait(0.3)), (0.9, ReplacementTransform(kc, cred)), (2.0, Wait(2.0)), swap(room, perm))
        self.play(FadeOut(VGroup(ck1, ck2)), run_time=0.4)
        name = T("OIDC: a signed pass, swapped for a card", 28, YELLOW_M).move_to([0, 3.0, 0])
        self.beat("That whole handshake has a name: OIDC, OpenID Connect. It's a standard that lets GitHub prove who a job is, with a signed pass that soon expires.",
                  FadeIn(name, shift=DOWN * 0.15), run_time=2.4)

        # ---------- 6. shrink and show: one real pass
        claims = VGroup(M("aud: sts.amazonaws.com", 22), M("sub: repo:you/hello-devops:pull_request", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cp = panel(claims, PURPLE_M)
        cp[0].stretch_to_fit_width(M("sub: repo:stranger/other-repo:pull_request", 22).width + 0.52)
        claims.align_to(cp[0], LEFT).shift(RIGHT * 0.26)
        cp.move_to([1.6, 2.75, 0])
        self.steps("Let's look at one real pass. It holds claims, named fields that GitHub vouches for. Two matter here.",
                   (0.5, FadeOut(name)), (0.9, FadeIn(cp, shift=DOWN * 0.15)))
        a1 = Arrow(job.get_bottom(), gh.get_top(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.18)
        self.beat("aud, the audience, says who the pass is meant for: AWS's sign-in service. sub, the subject, names the repo and the context the job runs in.",
                  Indicate(claims[0], color=PURPLE_M, scale_factor=1.05), Succession(Wait(2.8), Indicate(claims[1], color=PURPLE_M, scale_factor=1.04)), run_time=4.6)
        self.steps("So the job asks GitHub for a pass.", (0.8, GrowArrow(a1)), (0.6, tok.animate.move_to(gh.get_right() + RIGHT * 0.7)))
        self.steps("It carries the pass to AWS.", (1.2, tok.animate.move_to(aws.get_left() + LEFT * 0.75)))
        okA = tick(True, 0.18).next_to(aws, UP, buff=0.15)
        self.beat("Check one: is GitHub's signature real, and is the audience right? Yes.",
                  Indicate(aws[1], color=GOLD_M), Succession(Wait(1.6), Create(okA)), run_time=2.6)
        okB = tick(True, 0.18).next_to(trust, RIGHT, buff=0.2)
        self.beat("Check two: does the sub match the trust policy? Your repo, yes.",
                  Indicate(trust[1][1], color=PURPLE_M), Succession(Wait(1.6), Create(okB)), run_time=2.4)
        a2 = Arrow(aws.get_right(), perm.get_left(), buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.12)
        self.steps("Then AWS hands back short-lived credentials, and plan runs. No key was stored anywhere.",
                   (0.5, FadeOut(tok)), (0.8, cred.animate.move_to([-2.9, 1.6, 0])), (0.8, GrowArrow(a2)), (0.5, travel(a2, GREEN_M, 0.5)))

        # ---------- 7. break the wrong model: "AWS trusts GitHub"
        self.play(FadeOut(VGroup(okA, okB)), run_time=0.4)
        self.beat("Now let's be skeptical. AWS trusts GitHub's signature. But GitHub signs passes for every repo in the world, strangers included.",
                  Indicate(gh[1], color=GREY_B), run_time=2.4)
        bad = M("sub: repo:stranger/other-repo:pull_request", 22, RED_M).move_to(claims[1], aligned_edge=LEFT)
        job2 = box("stranger's job", RED_M, w=2.8, size=26).move_to(job)
        self.beat("So a stranger's workflow asks GitHub for a pass, and gets a real one. Does AWS let it in? Pause and guess.",
                  ReplacementTransform(job, job2), Transform(claims[1], bad), FadeOut(a2), FadeOut(cred), run_time=2.4)
        self.wait(2.0)
        tok2 = chip("token", RED_M, 24).move_to(gh.get_right() + RIGHT * 0.7)
        okC = tick(True, 0.18).next_to(aws, UP, buff=0.15)
        self.steps("The signature checks out. That pass is genuine.",
                   (0.4, FadeIn(tok2)), (1.0, tok2.animate.move_to(aws.get_left() + LEFT * 0.75)), (0.6, Create(okC)))
        xB = tick(False, 0.2).next_to(trust, RIGHT, buff=0.2)
        err = M("Not authorized to perform sts:AssumeRoleWithWebIdentity", 22, RED_M).move_to([0.6, -3.15, 0])
        self.beat("But the sub names the stranger's repo, and the trust policy names only yours. AWS refuses, with this error: Not authorized to perform sts:AssumeRoleWithWebIdentity.",
                  trust[0].animate.set_stroke(RED_M), Create(xB), Succession(Wait(2.8), FadeIn(err, shift=UP * 0.1)), run_time=4.4)
        self.beat("A perfectly real ID, with the wrong name on it. So the point is: the signature says who wrote the pass. The sub says who it's for. The desk needs both.",
                  Indicate(okC, color=GREEN_M, scale_factor=1.4), Succession(Wait(3.0), Indicate(claims[1], color=RED_M, scale_factor=1.03)), run_time=4.0)

        # exact, character for character
        main = VGroup(job2, gh, a1, aws, trust, perm, tok2, okC, xB, err, cp)
        self.play(FadeOut(main), run_time=0.6)
        old = VGroup(T("repos created before July 15, 2026", 24, GREY_B), M("repo:you/hello-devops:pull_request", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        new = VGroup(T("repos created after July 15, 2026", 24, GREY_B), M("repo:you@123456/hello-devops@456789:pull_request", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        forms = VGroup(old, new).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([0, 0.3, 0])
        self.beat("And the desk reads names character for character. Older repos write the sub like this.",
                  FadeIn(old, shift=UP * 0.15), run_time=1.8)
        self.beat("Repos created after July 15, 2026 put numeric IDs in it, like this. The lab trusts both forms, for your repo only.",
                  FadeIn(new, shift=UP * 0.15), run_time=2.0)
        rule = T("that error? check the sub first", 30, YELLOW_M).next_to(forms, DOWN, buff=0.6)
        self.beat("So when you see that error, don't blame the pipeline. Check the sub first.",
                  FadeIn(rule, shift=UP * 0.15), run_time=1.8)
        self.wait(0.4)
        self.play(FadeOut(VGroup(forms, rule)), run_time=0.7)

        # ---------- 8. guardrail: keep the room small
        perm2 = box("the pipeline's role", GREEN_M, w=4.2, size=28).move_to([0, 2.4, 0])
        self.beat("One more thing. A key card is only as safe as the room it opens. So keep the role small.",
                  FadeIn(perm2), run_time=2.0)
        rows = [("may manage only buckets named hello-devops-...", GREEN_M, True),
                ("may read its own IAM setup, so plan works", GREEN_M, True),
                ("may not change IAM", RED_M, False)]
        items = VGroup()
        for txt, col, ok in rows:
            items.add(VGroup(tick(ok, 0.18), T(txt, 28, col)).arrange(RIGHT, buff=0.35))
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, 0.2, 0])
        self.beat("The lab's role may manage only buckets whose names start with hello-devops.",
                  FadeIn(items[0], shift=RIGHT * 0.15), run_time=1.6)
        self.beat("It may also read its own IAM setup, so that plan works. IAM is AWS's service that decides who may do what.",
                  FadeIn(items[1], shift=RIGHT * 0.15), run_time=1.6)
        self.beat("And it cannot change IAM. Why does that matter? If it could, a pull request could edit the pipeline's own permissions, and turn its key card into a master key.",
                  FadeIn(items[2], shift=RIGHT * 0.15), run_time=2.4)
        lap = T("IAM changes: from your laptop, never from a pull request", 26, GREY_B).next_to(items, DOWN, buff=0.55)
        self.beat("A card that can upgrade itself isn't a card. So you apply IAM changes from your laptop.",
                  FadeIn(lap, shift=UP * 0.1), run_time=2.0)
        idt = M("id-token: write", 24, PURPLE_M)
        idn = T("only on the plan and apply jobs", 26, GREY_B)
        idg = VGroup(idt, idn).arrange(RIGHT, buff=0.4).next_to(lap, DOWN, buff=0.4)
        self.beat("Even asking for a pass is limited. Only the two jobs that log in to AWS get id-token: write. The checks job can only read the repo.",
                  FadeIn(idg, shift=UP * 0.1), run_time=2.4)
        self.wait(0.4)
        self.play(FadeOut(VGroup(perm2, items, lap, idg)), run_time=0.6)

        # ---------- 9. moral, recap, quick check
        m1 = T("A key that never expires is a key under the doormat.", 32, GOLD_M)
        m2 = T("Let the pipeline borrow one that does.", 32, GREEN_M)
        moral = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to([0, 1.6, 0])
        self.beat("So here's the moral of the story. A key that never expires is a key under the doormat. Let the pipeline borrow one that does.",
                  FadeIn(m1, shift=UP * 0.15), Succession(Wait(2.8), FadeIn(m2, shift=UP * 0.15)), run_time=4.0)
        rc = VGroup(T("GitHub signs a pass: the token and its claims", 26, PURPLE_M),
                    T("AWS checks the signature, then the sub, exactly", 26, GOLD_M),
                    T("it hands back a card: credentials that expire", 26, GREEN_M),
                    T("and the card opens one small room", 26, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([0, -1.3, 0])
        self.beat("GitHub signs a pass. AWS checks the signature, then the sub, character for character. It hands back a card that expires. And the card opens one small room.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rc], lag_ratio=0.6), run_time=6.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(moral, rc)), run_time=0.6)
        qq = T("Quick check", 30, YELLOW_M).move_to([0, 2.2, 0])
        qe = M("Not authorized to perform sts:AssumeRoleWithWebIdentity", 24, RED_M).move_to([0, 1.0, 0])
        qt = T("Your plan job fails with this. What do you check first?", 30).move_to([0, 0.0, 0])
        self.beat("A quick check before you go. Your plan job passes its checks, then fails with this error. What do you check first? Pause and think.",
                  FadeIn(qq), FadeIn(qe), FadeIn(qt), run_time=2.4)
        self.wait(2.0)
        ans = T("the token's sub, against the trust policy", 30, GREEN_M).move_to([0, -1.2, 0])
        self.beat("The sub. The name on the pass has to match the booking list, character for character.",
                  FadeIn(ans, shift=UP * 0.15), run_time=1.8)
        self.wait(1.0)
