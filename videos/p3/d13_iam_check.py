import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bASIA\b", "A S I A"), (r"\bAKIA\b", "A K I A"), (r"\bs3:GetObject\b", "S three get object"),
            (r"\bs3:DeleteObject\b", "S three delete object"), (r"\bs3:ListBucket\b", "S three list bucket"),
            (r"\bsts assume-role\b", "S T S assume role"), (r"\bsts get-caller-identity\b", "S T S get caller identity"),
            (r"\bARN\b", "A R N"), (r"\bMFA\b", "M F A"), (r"\baws\b", "A W S"), (r":root\b", " colon root")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def stage(label, color, w=1.8, h=0.8, size=24):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color), opacity=1)
    return VGroup(r, T(label, size).move_to(r))


def card(rows, color, pad=0.3, buff=0.16):
    g = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    r = RoundedRectangle(corner_radius=0.12, width=g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=2.5)
    r.set_fill(tint(color, 0.1), opacity=1)
    g.move_to(r)
    return VGroup(r, g)


class D13IamCheck(VoiceScene):
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
        self.title_card("How AWS decides each call", "credentials, signatures and policies")

        Y = 1.6
        mac = stage("your Mac: aws CLI", TEAL_M, w=2.7, h=0.9, size=24).move_to([-5.0, Y, 0])
        cmd = M("aws s3 cp s3://.../reports/2026-11-06.csv -", 20, WHITE).move_to([-3.4, 3.3, 0])
        fit(cmd, 6.4)
        self.beat("Every command you type with the AWS CLI becomes an API call to AWS. Like this one, which reads a report from a bucket.",
                  FadeIn(mac), Write(cmd), run_time=2.4)
        awsf = RoundedRectangle(corner_radius=0.2, width=7.3, height=6.3, stroke_color=GOLD_M, stroke_width=2).move_to([2.85, -0.25, 0])
        awl = T("AWS", 26, GOLD_M).move_to(awsf.get_corner(DR) + UL * 0.4 + LEFT * 0.1)
        sig = stage("check signature", BLUE_M, w=2.2).move_to([0.55, Y, 0])
        iam = stage("IAM", PURPLE_M, w=1.6).move_to([2.95, Y, 0])
        s3 = stage("S3", GREEN_M, w=1.6).move_to([5.25, Y, 0])
        a0 = Arrow(mac.get_right(), sig.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        a1 = edge_arrow(sig, iam)
        a2 = edge_arrow(iam, s3)
        self.beat("Any call can create, change or delete something. So before S3 does anything, AWS asks two questions.",
                  Create(awsf), FadeIn(awl), FadeIn(s3), GrowArrow(a0), run_time=2.4)
        q1 = T("who is calling?", 24, BLUE_M).next_to(sig, DOWN, buff=0.3)
        q2 = T("may they do this?", 24, PURPLE_M).next_to(iam, DOWN, buff=0.3)
        self.steps("Who is calling? And may they do this, on this resource?",
                   (0.8, FadeIn(sig), FadeIn(q1)), (0.6, GrowArrow(a1)), (0.8, FadeIn(iam), FadeIn(q2)), (0.5, GrowArrow(a2)))

        # 1. credentials and signing
        cred = card([M("access key ID", 22), M("secret", 22, RED_M), M("session token", 22, GREY_B)], TEAL_M).move_to([-5.0, -0.3, 0])
        cl = T("credentials", 22, TEAL_M).next_to(cred, UP, buff=0.15)
        self.beat("The first answer comes from credentials. An access key ID, a secret, and, for temporary credentials, a session token.",
                  FadeIn(cl), Create(cred[0]), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in cred[1]], lag_ratio=0.4), run_time=3.0)
        req = card([M("s3:GetObject", 20), M(".../reports/2026-11-06.csv", 20, GREY_B)], WHITE, pad=0.2, buff=0.1).move_to([-2.1, 2.55, 0])
        fit(req, 3.1)
        stamp = M("+ signature", 20, YELLOW_M).next_to(req, DOWN, buff=0.12).align_to(req, LEFT)
        self.steps("The CLI never sends the secret itself. It uses the secret to sign each request.",
                   (0.6, FadeOut(cmd)), (1.0, FadeIn(req, shift=RIGHT * 0.2)), (0.8, Indicate(cred[1][1], color=RED_M)),
                   (0.8, TransformFromCopy(cred[1][1], stamp)))
        copy = chip("its own copy of the secret", BLUE_M, 20).move_to([0.55, -0.15, 0])
        ok1 = tick(True, 0.22).next_to(sig, UP, buff=0.15)
        self.steps("AWS checks the signature with its own copy of the secret. If they match, AWS knows who is calling.",
                   (1.2, travel(a0, YELLOW_M, 1.2)), (0.8, FadeIn(copy, shift=UP * 0.1)), (1.0, Wait(1.0)), (0.6, Create(ok1)))

        # 2. where the credentials come from
        akia = chip("AKIA...  long-lived key", RED_M, 20, mono=True).move_to([-4.6, -2.3, 0])
        self.beat("So where should those credentials come from? The worst place is a long-lived access key.",
                  FadeIn(akia, shift=UP * 0.1), run_time=1.6)
        spots = VGroup(*[T(t, 20, RED_M) for t in ("a laptop", "a log", "a git repo")]).arrange(RIGHT, buff=0.55).move_to([-4.4, -3.25, 0])
        self.beat("It works for whoever holds it, copied from a laptop, a log or a git repo, until someone deletes it.",
                  LaggedStart(*[TransformFromCopy(akia[1], s) for s in spots], lag_ratio=0.4), run_time=2.6)
        brw = chip("browser sign-in", TEAL_M, 22).move_to([-5.0, -2.3, 0])
        login = M("aws login", 22, TEAL_M).move_to([-5.0, -3.2, 0])
        self.steps("People should sign in through a browser instead. aws login does that. It turns your browser sign-in into temporary keys.",
                   (0.8, FadeOut(spots), FadeOut(akia)), (1.0, FadeIn(brw, shift=UP * 0.1), FadeIn(login)), (1.6, Wait(1.6)),
                   (1.0, Indicate(cred, color=TEAL_M, scale_factor=1.04)))
        ref = T("refreshed every 15 minutes", 20, TEAL_M).next_to(cred, RIGHT, buff=0.25).shift(DOWN * 0.15)
        arc = Arc(radius=0.22, start_angle=PI / 2, angle=-TAU * 0.85, stroke_width=3, color=TEAL_M).add_tip(tip_length=0.12).next_to(ref, UP, buff=0.12)
        self.beat("It stores temporary credentials and refreshes them every 15 minutes. No key ever lands on your disk.",
                  FadeIn(ref), Create(arc), Succession(Wait(1.4), Rotate(arc, -TAU, run_time=1.6)), run_time=3.4)
        self.play(FadeOut(VGroup(brw, login, ref, arc)), run_time=0.5)

        # 3. the policy decision
        pol = card([T("reports-reader-permissions.json", 20, GREY_B),
                    M("Allow  s3:ListBucket   prefix reports/", 20),
                    M("Allow  s3:GetObject    .../reports/*", 20)], PURPLE_M).move_to([2.85, -1.75, 0])
        self.steps("Now the second question. Say the caller has the lab's reports reader policy. It allows listing the reports, and reading the objects under reports.",
                   (1.0, Indicate(iam, color=PURPLE_M)), (1.2, Create(pol[0]), FadeIn(pol[1][0])), (1.6, Wait(1.6)),
                   (0.8, FadeIn(pol[1][1], shift=RIGHT * 0.1)), (0.8, FadeIn(pol[1][2], shift=RIGHT * 0.1)))
        dec = chip("deny", RED_M, 24).move_to([2.95, 0.45, 0])
        self.steps("AWS decides every call the same way. It starts from deny.",
                   (0.6, FadeOut(q1), FadeOut(q2), FadeOut(copy)), (0.4, travel(a1, YELLOW_M, 0.6)), (0.8, FadeIn(dec, scale=0.8)))
        allow = chip("allow", GREEN_M, 24).move_to(dec)
        self.steps("A matching Allow opens the call. s3:GetObject on reports matches, so the call goes through to S3.",
                   (1.2, Indicate(pol[1][2], color=GREEN_M)), (0.6, Transform(dec, allow)), (1.2, Wait(1.2)), (0.8, travel(a2, GREEN_M, 0.8)),
                   (0.5, Indicate(s3, color=GREEN_M)))
        req2 = card([M("s3:DeleteObject", 20, RED_M), M(".../reports/2026-11-06.csv", 20, GREY_B)], WHITE, pad=0.2, buff=0.1).move_to(req)
        fit(req2, 3.1)
        deny2 = chip("deny", RED_M, 24).move_to(dec)
        self.steps("Now try a delete. Nothing in the policy allows s3:DeleteObject. So it stays denied, and S3 never sees it.",
                   (0.8, Transform(req, req2), Transform(dec, chip("deny", RED_M, 24).move_to(dec))),
                   (0.6, travel(a0, YELLOW_M, 0.6)), (0.6, travel(a1, YELLOW_M, 0.6)),
                   (1.2, *[Indicate(r, color=GREY_B) for r in pol[1][1:]]),
                   (0.6, Wiggle(dec)))
        dn = M("Deny   s3:GetObject    .../reports/*", 20, RED_M)
        pol2 = card([T("reports-reader-permissions.json", 20, GREY_B), M("Allow  s3:ListBucket   prefix reports/", 20),
                     M("Allow  s3:GetObject    .../reports/*", 20), dn], PURPLE_M).move_to([2.85, -1.95, 0])
        self.steps("And one more rule. An explicit Deny anywhere beats every Allow.",
                   (1.0, Transform(pol, pol2)), (1.0, Indicate(pol[1][3], color=RED_M)))
        self.play(Transform(pol, card([T("reports-reader-permissions.json", 20, GREY_B), M("Allow  s3:ListBucket   prefix reports/", 20),
                                       M("Allow  s3:GetObject    .../reports/*", 20)], PURPLE_M).move_to([2.85, -1.75, 0])),
                  FadeOut(dec), run_time=0.6)

        # 4. a role: two policies
        self.play(FadeOut(VGroup(pol, cred, cl, ok1, stamp)), run_time=0.6)
        role_r = RoundedRectangle(corner_radius=0.15, width=9.4, height=3.0, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.08), opacity=1)
        role_r.move_to([1.6, -1.5, 0])
        rt = T("role: reports-reader", 26, GOLD_M).move_to(role_r.get_top() + DOWN * 0.38)
        tp = card([T("trust policy", 24, BLUE_M), T("who may assume it", 20, GREY_B), M("Principal: ...:ACCOUNT_ID:root", 20)], BLUE_M, pad=0.22, buff=0.12)
        pp = card([T("permissions policy", 24, PURPLE_M), T("what it may do", 20, GREY_B), M("Allow s3:GetObject ...", 20)], PURPLE_M, pad=0.22, buff=0.12)
        VGroup(tp, pp).arrange(RIGHT, buff=0.35).move_to(role_r.get_center() + DOWN * 0.3)
        self.steps("Programs should not hold keys at all. They assume a role. And a role carries two policies.",
                   (0.6, FadeOut(req)), (1.2, Create(role_r), FadeIn(rt)), (1.4, Wait(1.4)))
        self.beat("The permissions policy, like the one we just read, says what the role may do.",
                  FadeIn(pp, shift=UP * 0.1), run_time=1.4)
        self.beat("The trust policy says who may assume it.", FadeIn(tp, shift=UP * 0.1), run_time=1.2)
        acc = T("= the whole account, not the root user", 20, BLUE_M).next_to(role_r, DOWN, buff=0.15).align_to(tp, LEFT)
        self.beat("Here the Principal ends in root. That means the whole account: any identity in it whose own policy allows assuming the role. It does not mean the root user.",
                  Indicate(tp[1][2], color=BLUE_M), Succession(Wait(1.6), FadeIn(acc, shift=UP * 0.1)), run_time=3.4)

        ar = M("aws sts assume-role", 22, YELLOW_M).move_to([-5.0, 0.3, 0])
        down = Arrow(mac.get_bottom(), [-5.0, -1.2, 0], buff=0.1, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.12)
        yours = chip("your own policy", TEAL_M, 20).move_to([-5.0, -1.55, 0])
        c1 = tick(True, 0.2).next_to(yours, DOWN, buff=0.15)
        c2 = tick(True, 0.2).next_to(tp[1][0], RIGHT, buff=0.25)
        self.steps("aws sts assume-role checks both sides. Your own policy must allow it, and the role's trust policy must list you.",
                   (0.8, FadeIn(ar)), (0.6, GrowArrow(down), FadeIn(yours)), (0.6, Create(c1)), (1.2, Wait(1.2)), (0.6, Indicate(tp, color=BLUE_M, scale_factor=1.04)), (0.5, Create(c2)))
        asia = chip("ASIA...  temporary, 1 hour", GREEN_M, 20, mono=True).move_to([-3.4, 2.75, 0])
        self.steps("Then it hands back temporary credentials. They last an hour by default.",
                   (1.2, TransformFromCopy(role_r, asia)), (0.6, Indicate(asia, color=GREEN_M)))
        akia2 = chip("AKIA...  long-lived", RED_M, 20, mono=True).next_to(asia, DOWN, buff=0.2).align_to(asia, LEFT)
        akia2.shift(UP * 0.0)
        self.beat("Their key ID starts with ASIA. Long-lived keys start with AKIA. So you can tell them apart in a log.",
                  Succession(Wait(1.4), FadeIn(akia2, shift=UP * 0.1)), run_time=2.8)

        # 5. recap
        self.play(FadeOut(VGroup(role_r, rt, tp, pp, acc, ar, down, yours, c1, c2, akia2)), run_time=0.6)
        rc = VGroup(T("signature: who is calling", 26, BLUE_M), T("policies: start at deny, Allow opens, Deny wins", 26, PURPLE_M),
                    T("people sign in, programs assume roles", 26, TEAL_M)).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([1.2, -1.6, 0])
        self.beat("So the signature proves who is calling. The policies start at deny, an Allow opens the call, and a Deny wins. People sign in for short-lived keys, and programs assume roles.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rc], lag_ratio=0.6), run_time=5.0)
        self.wait(1.2)
