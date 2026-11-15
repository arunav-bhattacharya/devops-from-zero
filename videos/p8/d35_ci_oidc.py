import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bOIDC\b", "O I D C"), (r"\btflint\b", "T F lint"), (r"\btrivy\b", "trivy"), (r"sts:AssumeRoleWithWebIdentity", "S T S assume role with web identity"),
            (r"token\.actions\.githubusercontent\.com", "token dot actions dot github user content dot com"),
            (r"sts\.amazonaws\.com", "S T S dot amazon A W S dot com"), (r"\bsub\b", "sub"), (r"\baud\b", "aud"),
            (r"hello-devops-\B", "hello devops dash"), (r"\bfmt\b", "format")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def tbox(title, sub, color, w=4.0, h=0.95):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.12), 1)
    g = VGroup(T(title, 24, WHITE), T(sub, 20, GREY_B)).arrange(DOWN, buff=0.08).move_to(r)
    return VGroup(r, g)


class D35CiOidc(VoiceScene):
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
        self.title_card("Terraform in CI, with no stored keys", "checks, plan, apply, and a token swap")

        # 1. the problem: a stored key
        sec = RoundedRectangle(corner_radius=0.15, width=4.4, height=2.2, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.06), 1).move_to([-3.0, 0.3, 0])
        secl = T("GitHub secrets", 26, GREY_B).next_to(sec, UP, buff=0.18)
        key = chip("AWS access key", GOLD_M, 26).move_to(sec)
        self.beat("One way to let a pipeline into AWS is an access key, saved as a GitHub secret.",
                  Create(sec), FadeIn(secl), FadeIn(key, scale=1.2), run_time=2.0)
        leak = key.copy()
        valid = T("still works for months", 26, RED_M).move_to([3.2, -0.5, 0])
        self.steps("That key works until someone deletes it. So if it leaks, it stays useful for months.",
                   (1.4, leak.animate.move_to([3.2, 0.3, 0]).set_color(RED_M)), (0.6, FadeIn(valid)))
        self.play(FadeOut(VGroup(sec, secl, key, leak, valid)), run_time=0.6)

        # 2. the pipeline
        names = (("pull request", GREY_B), ("checks", TEAL_M), ("plan", BLUE_M), ("approve", GOLD_M), ("apply", GREEN_M))
        row = VGroup(*[box(n, c, w=2.2, h=0.72, size=24) for n, c in names]).arrange(RIGHT, buff=0.45).move_to([0, 3.0, 0])
        rarr = VGroup(*[edge_arrow(row[i], row[i + 1]) for i in range(4)])
        self.beat("The lab's pipeline stores no key. It runs when anything under infra changes, in three jobs.",
                  FadeIn(row[0]), run_time=1.4)
        chk = VGroup(*[chip(t, TEAL_M, 20, mono=True) for t in ("fmt -check", "tflint", "trivy", "validate", "module tests")]).arrange(DOWN, buff=0.14).next_to(row[1], DOWN, buff=0.35)
        nl = T("no cloud login", 22, TEAL_M).next_to(chk, DOWN, buff=0.2)
        self.beat("checks runs on every pull request and push, with no cloud login. Formatting, tflint, a trivy scan, validate, and the module's tests.",
                  GrowArrow(rarr[0]), FadeIn(row[1]), Succession(Wait(1.6), FadeIn(nl)), Succession(Wait(2.4), LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in chk], lag_ratio=0.3)), run_time=5.4)
        x = tick(False, 0.2).next_to(chk[0], RIGHT, buff=0.2)
        self.beat("The cheap checks run first. So a formatting slip fails before anything logs in to AWS.",
                  Succession(Wait(1.2), AnimationGroup(chk[0][0].animate.set_stroke(RED_M), Create(x))), run_time=2.6)
        self.play(FadeOut(VGroup(chk, nl, x)), run_time=0.5)
        pd = VGroup(M("terraform plan -out=tfplan", 20, BLUE_M), T("plan shown on the summary page", 22, GREY_B)).arrange(DOWN, buff=0.15).next_to(row[2], DOWN, buff=0.35)
        self.beat("plan runs on pull requests, once the checks pass. It logs in to AWS, runs terraform plan, and puts the plan on the run's summary page for reviewers.",
                  GrowArrow(rarr[1]), FadeIn(row[2]), Succession(Wait(2.4), FadeIn(pd, shift=DOWN * 0.1)), run_time=4.2)
        ad = VGroup(T("after a merge to main", 22, GREY_B), T("waits in production", 22, GOLD_M), T("for a reviewer", 22, GOLD_M)).arrange(DOWN, buff=0.1).next_to(row[3], DOWN, buff=0.35)
        self.beat("apply runs after a merge to main. It waits in the production environment until a required reviewer approves. Then it plans and applies.",
                  GrowArrow(rarr[2]), FadeIn(row[3]), FadeIn(ad, shift=DOWN * 0.1), Succession(Wait(3.6), AnimationGroup(GrowArrow(rarr[3]), FadeIn(row[4]))), run_time=5.0)
        self.play(FadeOut(pd), FadeOut(ad), run_time=0.5)
        q = T("two jobs log in to AWS. How, with no key?", 30, YELLOW_M).move_to([0, 0.6, 0])
        self.beat("So two jobs log in to AWS. How, with no key?",
                  FadeIn(q, shift=UP * 0.1), Indicate(row[2], color=BLUE_M), Indicate(row[4], color=GREEN_M), run_time=2.0)
        self.play(FadeOut(q), row[2][0].animate.set_stroke(width=6), run_time=0.5)

        # 3. the token swap
        job = tbox("plan job", "a GitHub runner", BLUE_M, w=2.7, h=1.0).move_to([-5.0, 1.0, 0])
        gh = tbox("GitHub", "signs tokens", GREY_B, w=2.7, h=1.0).move_to([-5.0, -1.0, 0])
        aws = RoundedRectangle(corner_radius=0.15, width=4.2, height=4.15, stroke_color=GOLD_M, stroke_width=2.5).set_fill(tint(GOLD_M, 0.05), 1).move_to([4.55, -0.4, 0])
        awsl = T("AWS", 26, GOLD_M).next_to(aws, UP, buff=0.12).align_to(aws, LEFT)
        prov = tbox("OIDC provider", "checks GitHub's signature, aud", PURPLE_M, w=3.9).move_to([4.55, 0.95, 0])
        trust = tbox("role trust policy", "checks sub, exactly", PURPLE_M, w=3.9).move_to([4.55, -0.35, 0])
        perm = tbox("role permissions", "only buckets hello-devops-*", GREEN_M, w=3.9).move_to([4.55, -1.65, 0])
        jg = Arrow(job.get_bottom(), gh.get_top(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("OIDC. First, the job asks GitHub for a token.",
                  FadeIn(job), FadeIn(gh), GrowArrow(jg), run_time=2.0)
        tok = chip("token", PURPLE_M, 24).move_to([-2.6, -1.0, 0])
        claims = VGroup(M("aud: sts.amazonaws.com", 20, WHITE), M("sub: repo:you/hello-devops:pull_request", 20, WHITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        cbox = RoundedRectangle(corner_radius=0.12, width=claims.width + 0.5, height=claims.height + 0.45, stroke_color=PURPLE_M, stroke_width=2).set_fill(tint(PURPLE_M, 0.08), 1)
        cl = VGroup(cbox, claims.move_to(cbox)).move_to([-1.0, -2.55, 0])
        cll = T("claims", 22, PURPLE_M).next_to(cl, UP, buff=0.12).align_to(cl, LEFT)
        self.beat("GitHub signs a short-lived token. It holds claims: named fields, such as the repo and branch the job runs for.",
                  FadeIn(tok, shift=RIGHT * 0.2), Succession(Wait(1.6), AnimationGroup(FadeIn(cl), FadeIn(cll))), run_time=3.6)
        self.steps("The job hands the token to AWS.",
                   (0.8, tok.animate.move_to(job.get_right() + RIGHT * 0.9)), (0.4, Create(aws)), (0.3, FadeIn(awsl)),
                   (1.2, tok.animate.move_to([1.2, 0.95, 0])))
        self.beat("But how does AWS know the token is real? AWS never sees you. It only trusts GitHub's signature.",
                  FadeIn(prov), run_time=1.8)
        ok1 = tick(True, 0.18).next_to(prov, LEFT, buff=0.15)
        self.beat("An OIDC provider for token.actions.githubusercontent.com lets AWS check that signature. And the token's aud claim must be sts.amazonaws.com.",
                  Succession(Wait(3.2), Indicate(claims[0], color=PURPLE_M, scale_factor=1.06)), Succession(Wait(4.0), Create(ok1)), run_time=5.6)
        self.steps("Next, the role's trust policy checks the sub claim. It names your repo and the context, such as pull_request. It has to match exactly, character for character.",
                   (0.8, FadeIn(trust), tok.animate.move_to([1.2, -0.35, 0])), (1.6, Wait(1.6)),
                   (1.4, Indicate(claims[1], color=PURPLE_M, scale_factor=1.04)))
        bad = M("sub: repo:you/other-repo:pull_request", 20, RED_M).move_to(claims[1], aligned_edge=LEFT)
        err = M("Not authorized to perform sts:AssumeRoleWithWebIdentity", 20, RED_M).move_to([0.6, -3.35, 0])
        good = claims[1].copy()
        self.beat("If the sub names any other repo, the login fails with: Not authorized to perform sts:AssumeRoleWithWebIdentity. So check the sub first.",
                  Transform(claims[1], bad), trust[0].animate.set_stroke(RED_M), Succession(Wait(2.0), FadeIn(err, shift=UP * 0.1)), run_time=3.6)
        ok2 = tick(True, 0.18).next_to(trust, LEFT, buff=0.15)
        self.beat("With the right sub, it passes.",
                  Transform(claims[1], good), trust[0].animate.set_stroke(PURPLE_M), FadeOut(err), Create(ok2), run_time=1.6)
        cred = chip("short-lived credentials", GREEN_M, 22).move_to([0.0, 0.9, 0])
        self.steps("Then AWS hands back short-lived credentials for that role. No key was stored anywhere.",
                   (0.6, FadeOut(tok)), (0.6, FadeIn(cred, shift=LEFT * 0.2)), (1.4, cred.animate.move_to([-1.6, 1.55, 0])))

        # 4. a small role
        s3 = tbox("S3 bucket", "hello-devops-...", TEAL_M, w=3.4).move_to([-0.75, -0.35, 0])
        self.play(FadeOut(cl), FadeOut(cll), run_time=0.4)
        ja = Arrow(job.get_right() + DOWN * 0.3, s3.get_left() + UP * 0.1, buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.12)
        self.beat("Now terraform plan runs with those credentials. And the role is small. It may manage only buckets whose names start with hello-devops.",
                  FadeIn(perm), Succession(Wait(1.6), AnimationGroup(GrowArrow(ja), FadeIn(s3))), Succession(Wait(3.6), Indicate(perm, color=GREEN_M, scale_factor=1.04)), run_time=5.4)
        noiam = chip("cannot change IAM", RED_M, 22).move_to([-0.75, -2.0, 0])
        self.beat("It cannot change IAM. So a pull request cannot give the pipeline more power. You apply IAM changes from your laptop.",
                  FadeIn(noiam, shift=UP * 0.1), run_time=2.4)

        # 5. apply does the same swap
        sub2 = M("sub: ...:environment:production", 20, GREEN_M).move_to([-0.75, -3.0, 0])
        self.beat("The apply job does the same swap after approval. Its token's sub names the context environment production, and the trust policy must allow that too.",
                  row[2][0].animate.set_stroke(width=3), row[4][0].animate.set_stroke(width=6), Transform(job[1][0], T("apply job", 24, WHITE).move_to(job[1][0])),
                  job[0].animate.set_stroke(GREEN_M), FadeIn(sub2, shift=UP * 0.1), run_time=3.6)
        self.wait(0.6)
        self.play(FadeOut(VGroup(job, gh, jg, aws, awsl, prov, trust, perm, ok1, ok2, cred, s3, ja, noiam, sub2, row, rarr)), run_time=0.7)

        # 6. recap
        rcp = VGroup(T("checks first, with no cloud login", 30, TEAL_M), T("plan on pull requests, apply after approval", 30, BLUE_M),
                     T("a signed token, swapped for short-lived credentials", 30, PURPLE_M), T("the trust policy checks sub; the role stays small", 30, GREEN_M)).arrange(DOWN, buff=0.4)
        self.beat("Cheap checks first. Plan on pull requests, apply after approval. Each AWS job swaps a signed token for short-lived credentials. The trust policy checks who, and the role limits what.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.5), run_time=5.4)
        self.wait(1.0)
