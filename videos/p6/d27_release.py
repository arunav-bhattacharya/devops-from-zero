import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bGITHUB_TOKEN\b", "GitHub token"), (r"\bGHCR\b", "G H C R"), (r"\bghcr\.io\b", "G H C R dot I O"),
            (r"\brelease\.yml\b", "release dot yammel"), (r"\bv1\.2\.0\b", "v 1.2.0"), (r"\bv\*", "v star"), (r"\bQEMU\b", "Q emu"),
            (r"\bBuildx\b", "build X"), (r"\bamd64\b", "A M D 64"), (r"\barm64\b", "arm 64"), (r"\bSHA\b", "shah"), (r"\bv4\b", "v 4"),
            (r"\bGitHub\b", "git hub"), (r"\bCI\b", "C I")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def sbox(label, color=GREY_B, w=2.9, h=0.56, size=22):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.12), 1)
    return VGroup(r, T(label, size).move_to(r))


class D27Release(VoiceScene):
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
        self.title_card("From a git tag to an image", "a short-lived token, only the rights it needs, and a person at the gate")

        # ---- 0. the problem: a key to the registry
        key = chip("a stored key", RED_M, 30).move_to([0, 1.3, 0])
        opens = VGroup(chip("lives for months", GREY_B, 24), chip("works from anywhere", GREY_B, 24), chip("painful to rotate", GREY_B, 24)).arrange(RIGHT, buff=0.4).move_to([0, -0.6, 0])
        ka = VGroup(*[Arrow(key.get_bottom(), o.get_top(), buff=0.12, stroke_width=2.5, color=RED_M, max_tip_length_to_length_ratio=0.15) for o in opens])
        self.beat("A release job has to write to a registry, so it needs a key. The simple way is to store a key as a secret. That key lives for months, works from anywhere, and is painful to rotate.",
                  FadeIn(key, shift=DOWN * 0.15), Succession(Wait(4.6), LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(o)) for a, o in zip(ka, opens)], lag_ratio=0.5)), run_time=8.4)
        leak = T("if it leaks: usable until someone notices", 28, RED_M).move_to([0, -2.3, 0])
        self.beat("If it leaks, an attacker can use it until someone notices. Here is how release.yml does better.",
                  FadeIn(leak, shift=UP * 0.15), run_time=2.4)
        self.play(FadeOut(VGroup(key, opens, ka, leak)), run_time=0.6)

        # ---- 1. the tag starts the run
        LXc = -5.2
        tag = chip("push tag v1.2.0", YELLOW_M, 20, mono=True).move_to([LXc, 2.75, 0])
        run = sbox("run of release.yml", BLUE_M, w=2.6, size=22).move_to([LXc, 1.45, 0])
        a1 = Arrow(tag.get_bottom(), run.get_top(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        trig = M('tags: ["v*"]', 20, GREY_B).next_to(run, DOWN, buff=0.15)
        self.beat("It starts when you push a version tag, such as v1.2.0. Any tag that matches v star starts a run of release.yml.",
                  FadeIn(tag, shift=DOWN * 0.1), Succession(Wait(2.0), AnimationGroup(GrowArrow(a1), FadeIn(run), FadeIn(trig))), run_time=4.4)
        self.play(travel(a1, YELLOW_M, 0.7), run_time=0.7)

        # ---- 2. the gate
        gate = sbox("environment: production", GOLD_M, w=3.1, h=0.62, size=20).move_to([LXc, -0.15, 0])
        a2 = Arrow(trig.get_bottom(), gate.get_top(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        rule = T("required reviewers", 22, GOLD_M).next_to(gate, DOWN, buff=0.2)
        self.beat("Without a gate, every tag you push ships at once, even one you pushed by mistake. So the job names an environment: production.",
                  Succession(Wait(3.4), AnimationGroup(GrowArrow(a2), FadeIn(gate))), run_time=5.0)
        self.beat("Before the job starts, GitHub checks the environment's rules. Here, a required reviewer.",
                  FadeIn(rule, shift=UP * 0.1), Indicate(gate[1], color=GOLD_M), run_time=2.4)
        wait = T("waiting...", 22, GREY_B).next_to(rule, DOWN, buff=0.2)
        self.beat("The run stops and waits. It can wait up to thirty days for a person to say yes.",
                  FadeIn(wait), Succession(Wait(1.2), Indicate(wait, color=GREY_B, scale_factor=1.05), Indicate(wait, color=GREY_B, scale_factor=1.05)), run_time=3.2)
        ok = VGroup(tick(True, 0.2), T("approved", 22, GREEN_M)).arrange(RIGHT, buff=0.2).move_to(wait)
        self.beat("One approval lets the job go on.",
                  Transform(wait, ok), gate[0].animate.set_stroke(GREEN_M), run_time=1.2)

        # ---- 3. the job and its token
        job = RoundedRectangle(corner_radius=0.18, width=6.0, height=5.6, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1).move_to([0.75, 0.15, 0])
        job_t = T("job: image, on a fresh runner", 24, GREY_B).next_to(job.get_corner(UL), DR, buff=0.18)
        a3 = Arrow(gate.get_right(), [job.get_left()[0], gate.get_center()[1], 0], buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.18)
        self.beat("Now the job starts, on a fresh machine.", GrowArrow(a3), Create(job), FadeIn(job_t), run_time=1.6)
        tok = chip("GITHUB_TOKEN", GREEN_M, 22, mono=True).move_to([2.35, 1.75, 0])
        life = VGroup(Line([-1.85, -2.05, 0], [3.35, -2.05, 0], stroke_width=4, color=GREEN_M),
                      T("job starts", 20, GREY_B).move_to([-1.3, -2.4, 0]), T("job ends: token expires", 20, GREY_B).move_to([2.2, -2.4, 0]))
        life_l = T("token lifetime (6 hours at most)", 20, GREEN_M).move_to([0.75, -1.75, 0])
        self.steps("Every job gets a token without asking: the GITHUB_TOKEN. GitHub creates it when the job starts, and it expires when the job ends.",
                   (1.0, GrowFromCenter(tok)), (2.2, Wait(2.2)), (1.6, Create(life[0]), FadeIn(life[1]), FadeIn(life_l)), (0.8, FadeIn(life[2])))
        scope = T("only this repository", 20, GREY_B).next_to(tok, DOWN, buff=0.15)
        self.beat("It only works on the current repository. But what may it do there?",
                  FadeIn(scope), run_time=1.6)

        perms = VGroup(M("contents: read", 22, GREY_B), M("packages: write", 22, GREEN_M), M("others: none", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        perms.move_to([1.15, 0.2, 0], aligned_edge=LEFT)
        self.steps("You decide, with the permissions key. At the top of the workflow, the default for every job is contents: read.",
                   (2.6, Wait(2.6)), (0.8, FadeIn(perms[0], shift=UP * 0.1)))
        self.steps("This job alone adds packages: write, to push images. Any permission you do not list becomes none.",
                   (0.9, FadeIn(perms[1], shift=UP * 0.1)), (1.8, Wait(1.8)), (0.8, FadeIn(perms[2], shift=UP * 0.1)))
        lp = T("least privilege", 24, YELLOW_M).next_to(perms, DOWN, buff=0.25)
        self.beat("That is least privilege. The token gets only the access its task needs.", FadeIn(lp, shift=UP * 0.1), run_time=1.6)

        # ---- 4. the steps, and every action holds the token
        names = ["checkout", "QEMU + Buildx", "log in to ghcr.io", "metadata: tags", "build and push"]
        stp = VGroup(*[sbox(f"{i + 1}  {n}", GREY_B, w=2.9, size=22) for i, n in enumerate(names)])
        for i, s_ in enumerate(stp):
            s_.move_to([-0.65, 1.75 - 0.68 * i, 0])
        self.play(FadeOut(lp), run_time=0.3)
        self.beat("Then the steps run in order.",
                  LaggedStart(*[FadeIn(s_, shift=RIGHT * 0.1) for s_ in stp], lag_ratio=0.2), run_time=1.6)

        def on(i, c=YELLOW_M):
            return stp[i][0].animate.set_stroke(c, 3.5).set_fill(tint(c, 0.2), 1)

        self.steps("Checkout fetches the code at the tag. QEMU, an emulator, lets this amd64 runner build arm64 steps too.",
                   (0.8, on(0)), (1.6, Wait(1.6)), (0.8, on(0, GREEN_M), on(1)))
        self.steps("The login step logs in to ghcr.io with the job's own GITHUB_TOKEN. No password is stored anywhere.",
                   (0.8, on(1, GREEN_M), on(2)), (0.8, Wait(0.8)), (1.0, Indicate(tok, color=GREEN_M)))
        meta = VGroup(*[chip(t, BLUE_M, 20, mono=True) for t in ("1.2.0", "sha-9f2c1e7", "latest")]).arrange(DOWN, buff=0.12)
        ghcr = RoundedRectangle(corner_radius=0.15, width=2.2, height=4.0, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.06), 1).move_to([5.55, -0.05, 0])
        ghcr_t = M("ghcr.io", 22, BLUE_M).next_to(ghcr.get_top(), DOWN, buff=0.2)
        meta.next_to(ghcr_t, DOWN, buff=0.3)
        self.steps("The metadata step turns the git tag into image tags: 1.2.0, sha plus the short commit, and latest.",
                   (0.8, on(2, GREEN_M), on(3)), (0.8, Create(ghcr), FadeIn(ghcr_t)),
                   (2.4, LaggedStart(*[FadeIn(m, shift=LEFT * 0.15) for m in meta], lag_ratio=0.5)))
        plat = T("amd64 + arm64", 20, GREY_B).next_to(meta, DOWN, buff=0.3)
        push = Arrow(stp[4].get_right(), [ghcr.get_left()[0], stp[4].get_center()[1], 0], buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.08)
        self.steps("Then build and push makes the image for both CPU types, and pushes them under one multi-platform tag.",
                   (0.8, on(3, GREEN_M), on(4)), (1.4, Wait(1.4)), (1.0, GrowArrow(push)), (1.0, travel(push, BLUE_M, 1.0)), (0.6, FadeIn(plat)), (0.4, on(4, GREEN_M)))

        keys = VGroup(*[Dot(radius=0.07, color=GREEN_M).move_to(tok.get_center()) for _ in stp])
        self.add(keys)
        self.steps("Here is the catch. Every action in the job can use the token, even if you never pass it on. Whatever the token may do, every action may do.",
                   (2.0, Wait(2.0)), (1.6, LaggedStart(*[k.animate.move_to(s_[0].get_right() + LEFT * 0.2) for k, s_ in zip(keys, stp)], lag_ratio=0.15)),
                   (0.8, Indicate(perms[1], color=GREEN_M)))
        self.play(FadeOut(keys), run_time=0.3)

        # ---- 5. pin third-party actions
        self.play(FadeOut(VGroup(perms, scope)), run_time=0.4)
        lab = T("someone else's code", 20, YELLOW_M).move_to([2.25, 1.0, 0])
        cl = Line([1.0, -0.2, 0], [3.55, -0.2, 0], stroke_width=2, color=GREY_B)
        cms = VGroup(Dot([2.33, -0.2, 0], color=GREY_B), Dot([1.6, -0.2, 0], color=GREEN_M), Dot([3.05, -0.2, 0], color=RED_M).set_opacity(0))
        good_l = M("81c6f93d", 20, GREEN_M).next_to(cms[1], DOWN, buff=0.15)
        v4 = chip("v4", YELLOW_M, 20, mono=True).next_to(cms[1], UP, buff=0.35)
        v4a = Arrow(v4.get_bottom(), cms[1].get_center(), buff=0.08, stroke_width=2.5, color=YELLOW_M, max_tip_length_to_length_ratio=0.3)
        self.beat("And an action is someone else's code, running with your token. A tag such as v4 is only a label on one commit.",
                  FadeIn(lab), Succession(Wait(2.4), AnimationGroup(Create(cl), FadeIn(cms[:2]), FadeIn(good_l), FadeIn(v4), GrowArrow(v4a))), run_time=4.8)
        bad_l = T("malicious", 20, RED_M).next_to(cms[2], DOWN, buff=0.15)
        v4b = chip("v4", YELLOW_M, 20, mono=True).next_to(cms[2], UP, buff=0.35)
        v4ba = Arrow(v4b.get_bottom(), cms[2].get_center(), buff=0.08, stroke_width=2.5, color=YELLOW_M, max_tip_length_to_length_ratio=0.3)
        self.steps("Whoever controls the action's repository can move it. In March 2025 that really happened: the tags of a popular action were moved to a malicious commit, which printed CI secrets into the logs.",
                   (2.6, Wait(2.6)), (0.6, cms[2].animate.set_opacity(1), FadeIn(bad_l)),
                   (1.2, Transform(v4, v4b), Transform(v4a, v4ba)))
        pin = M("@81c6f93d # v4.7.0", 20, GREEN_M).move_to([2.2, -1.33, 0])
        pin_b = SurroundingRectangle(cms[1], color=GREEN_M, buff=0.12, corner_radius=0.08)
        self.beat("A full commit SHA cannot be moved. So release.yml pins every third-party action to one, with the version in a comment. Dependabot moves the pins for you.",
                  Succession(Wait(1.2), AnimationGroup(Create(pin_b), FadeIn(pin, shift=UP * 0.1))), run_time=4.6)

        # ---- 6. job ends
        self.steps("When the job ends, the token expires. What is left is the image in GHCR, built once from the tag.",
                   (1.0, Wait(1.0)), (1.2, life[0].animate.set_color(GREY_D), tok.animate.set_opacity(0.15), job.animate.set_stroke(GREY_D)),
                   (1.0, ghcr.animate.set_stroke(width=5)))
        self.play(FadeOut(VGroup(lab, cl, cms, good_l, bad_l, v4, v4a, pin, pin_b)), run_time=0.4)

        # ---- 7. recap
        self.beat("A tag starts the run. A person opens the gate. The job gets a short-lived token with only the rights it needs, and pinned actions use it to push one image.",
                  Indicate(tag, color=YELLOW_M), Succession(Wait(1.6), Indicate(wait, color=GREEN_M)), Succession(Wait(3.0), Indicate(tok, color=GREEN_M)),
                  Succession(Wait(6.0), Indicate(ghcr_t, color=BLUE_M)), run_time=7.6)
        self.wait(1.0)
