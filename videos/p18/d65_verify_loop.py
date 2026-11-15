import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bkubeconform\b", "cube conform"), (r"\btimeoutSeconds\b", "timeout seconds"), (r"\bcontainerPort\b", "container port"),
            (r"\bREDIS_HOST\b", "redis host"), (r"/healthz\b", "health Z"), (r"/readyz\b", "ready Z"), (r"-strict\b", "dash strict"),
            (r"\bapp\.py\b", "app dot pie"), (r"\bAGENTS\.md\b", "agents dot M D")])

DRAFT = [
    ("selector:", 0), ("matchLabels: {app: hello-devops}", 1), ("template:", 0), ("metadata:", 1), ("labels: {app: hello}", 2),
    ("spec:", 1), ("containers:", 2), ("- image: hello-devops:latest", 2), ("ports:", 3), ('- containerPort: "8000"', 3),
    ("env:", 3), ("- name: REDIS_HOST", 3), ("value: localhost", 4), ("livenessProbe:", 3), ("httpGet:", 4),
    ("path: /health", 5), ("timeout: 3", 4), ("resources:", 3), ("limits: {cpu: 500m}", 4),
]
LX, LY0, LDY = -6.35, 2.85, 0.33
CX = 3.2    # column of the check boxes


def tint(c, k=0.15):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def badge(n, color):
    c = Circle(radius=0.17, stroke_color=color, stroke_width=2.5).set_fill(BLACK, 1)
    return VGroup(c, T(str(n), 20, color).move_to(c))


def check(title, cmd, color, y, h, w=4.6):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), 1).move_to([CX, y, 0])
    t = T(title, 24, color).move_to([CX, y + h / 2 - 0.27, 0])
    g = VGroup(r, t)
    if cmd:
        g.add(M(cmd, 20, GREY_B).move_to([CX, y + h / 2 - 0.63, 0]))
    return g


class D65VerifyLoop(VoiceScene):
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

    def line(self, i, text, color=WHITE):
        return M(text, 20, color).move_to([LX + 0.3 * DRAFT[i][1], LY0 - i * LDY, 0], aligned_edge=LEFT)

    def construct(self):
        self.title_card("The verify loop", "the model drafts, and a tool you trust decides")

        # ---------- 1. the draft
        ask = chip("Write a Kubernetes Deployment for hello-devops: 3 replicas, a liveness probe, Redis", GREY_B, 22)
        ask.move_to([0, 3.2, 0])
        self.beat("You ask an assistant for a Kubernetes Deployment for hello-devops. No files, no versions. It answers in seconds.",
                  FadeIn(ask, shift=0.1 * DOWN), run_time=1.4)
        card = RoundedRectangle(corner_radius=0.15, width=5.9, height=6.85, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.05), 1)
        card.move_to([-3.75, 0.05, 0])
        lines = VGroup(*[self.line(i, t) for i, (t, _) in enumerate(DRAFT)])
        ttl = M("deployment-ai-draft.yaml, trimmed", 20, GREY_B).move_to([-3.75, 3.2, 0])
        self.beat("A model writes by predicting likely text, one small piece at a time. It is not looking anything up. It produces the shape it has seen thousands of times.",
                  FadeOut(ask), FadeIn(card), FadeIn(ttl), LaggedStart(*[FadeIn(l, shift=0.05 * RIGHT) for l in lines], lag_ratio=0.12), run_time=5.0)
        self.beat("Common shapes come out well. Rare details come out as guesses, and the guesses look exactly like facts. Can you spot them?",
                  Indicate(lines, color=WHITE, scale_factor=1.02), run_time=2.0)
        self.beat("So one rule for this whole lesson. The model drafts, and a tool you trust decides.")

        # ---------- 2. the loop on the right
        kc = check("schema check", "kubeconform -strict", BLUE_M, 2.55, 1.6)
        dr = check("server dry run", "kubectl apply --dry-run=server", PURPLE_M, 0.8, 1.3)
        rv = check("your review", None, GOLD_M, -1.15, 2.0)
        prb = box("pull request", GREEN_M, w=3.0, h=0.6, size=24).move_to([CX, -2.75, 0])
        down = VGroup(ar := Arrow(kc.get_bottom(), dr.get_top(), buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3),
                      Arrow(dr.get_bottom(), rv.get_top(), buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3),
                      Arrow(rv.get_bottom(), prb.get_top(), buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3))
        back = CurvedArrow(rv.get_right() + RIGHT * 0.08, kc.get_right() + RIGHT * 0.08, angle=TAU / 10, color=GREY_B, stroke_width=3)
        bl = T("fix, run again", 20, GREY_B).rotate(PI / 2).move_to(back.point_from_proportion(0.5) + RIGHT * 0.25)
        self.steps("Every draft goes round a loop. Read it. Run a check you trust. Fix what it finds, and run it again, until it passes. Then review the whole diff as a pull request.",
                   (0.8, FadeIn(kc)), (0.6, GrowArrow(down[0]), FadeIn(dr)), (0.6, GrowArrow(down[1]), FadeIn(rv)),
                   (1.0, Create(back), FadeIn(bl)), (1.0, Wait(1.0)), (0.6, GrowArrow(down[2]), FadeIn(prb)))

        def scan(color, rt=1.6):
            bar = Line([LX - 0.15, LY0 + 0.2, 0], [-1.05, LY0 + 0.2, 0], stroke_width=3, color=color)
            return Succession(FadeIn(bar, run_time=0.1), bar.animate(run_time=rt).shift(DOWN * (LDY * len(DRAFT) + 0.1)), FadeOut(bar, run_time=0.15))

        def mark(i, n, color):
            b = badge(n, color).move_to([-1.1, LY0 - i * LDY, 0])
            return b, lines[i].animate.set_color(color)

        # kubeconform -strict
        f1 = VGroup(T("1  port: got string, want integer", 20), T("2  timeout: not a probe field", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        f1.move_to([CX, 2.13, 0])
        b1, m1 = mark(9, 1, BLUE_M)
        b2, m2 = mark(16, 2, BLUE_M)
        self.steps("First, kubeconform. It checks each object against the official schema for its kind, without a cluster.",
                   (1.2, kc[0].animate.set_stroke(width=6)), (1.8, scan(BLUE_M)))
        self.steps("It finds two mistakes that a YAML parser would never notice. containerPort must be a number, not a string. And timeout is not a probe field at all. The real one is timeoutSeconds.",
                   (0.8, FadeIn(b1), m1, FadeIn(f1[0])), (2.6, Wait(2.6)), (0.8, FadeIn(b2), m2, FadeIn(f1[1])))
        self.beat("That second one is the mistake models make most often. A field that sounds right, in the right place, with perfect indentation. Without dash strict, it slips through.",
                  Succession(Wait(3.4), AnimationGroup(f1[1].animate.set_opacity(0.3), b2.animate.set_opacity(0.3))),
                  Succession(Wait(5.0), AnimationGroup(f1[1].animate.set_opacity(1), b2.animate.set_opacity(1))), run_time=5.6)
        fx1 = self.line(9, "- containerPort: 8000", GREEN_M)
        fx2 = self.line(16, "timeoutSeconds: 3", GREEN_M)
        ok1 = tick(True, 0.2).next_to(kc[1], RIGHT, buff=0.25)
        self.steps("Fix those two lines, and run it again. Now kubeconform is happy.",
                   (1.0, Transform(lines[9], fx1), Transform(lines[16], fx2), FadeOut(b1), FadeOut(b2)), (1.4, scan(BLUE_M, 1.2)),
                   (0.6, Create(ok1), f1.animate.set_opacity(0.35), kc[0].animate.set_stroke(width=3)))

        # server dry run
        f2 = T("3  selector does not match labels", 20).move_to([CX, 0.4, 0])
        b3, m3 = mark(1, 3, PURPLE_M)
        b3b, m3b = mark(4, 3, PURPLE_M)
        self.steps("The API server is not. Some rules live only in the server. A server dry run sends the object, runs every check of a real apply, and then throws it away.",
                   (1.0, dr[0].animate.set_stroke(width=6)), (2.6, Wait(2.6)), (1.6, scan(PURPLE_M)))
        self.beat("It finds the third mistake. The selector says app hello-devops, but the Pod labels say app hello. They must match.",
                  FadeIn(b3), m3, FadeIn(b3b), m3b, Succession(Wait(1.4), FadeIn(f2)), run_time=2.6)
        fx3 = self.line(4, "labels: {app: hello-devops}", GREEN_M)
        ok2 = tick(True, 0.2).next_to(dr[1], RIGHT, buff=0.2)
        self.steps("Fix it, and both checks pass.",
                   (1.0, Transform(lines[4], fx3), lines[1].animate.set_color(WHITE), FadeOut(b3), FadeOut(b3b)),
                   (0.6, Create(ok2), f2.animate.set_opacity(0.35), dr[0].animate.set_stroke(width=3)))

        # the review
        q = T("checks prove shape, not intent", 22, GOLD_M).move_to([CX, -0.8, 0])
        self.beat("But is it right for hello-devops? Checks prove shape, not intent. No schema knows that your app listens on 8000, or which path is healthy.",
                  rv[0].animate.set_stroke(width=6), FadeIn(q), run_time=2.0)
        routes = M("app.py: /healthz, /readyz", 20, GREY_B).move_to([CX, -1.2, 0])
        b4, m4 = mark(15, 4, GOLD_M)
        self.beat("Read the routes in app.py. The probe uses slash health, but the app serves /healthz.",
                  FadeIn(routes), FadeIn(b4), m4, run_time=2.0)
        b5, m5 = mark(7, 5, GOLD_M)
        b6, m6 = mark(12, 6, GOLD_M)
        b7, m7 = mark(13, 7, GOLD_M)
        b8, m8 = mark(18, 8, GOLD_M)
        more = VGroup(T("5 :latest   6 not the Service redis", 20), T("7 no readiness probe   8 CPU limit", 20)).arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([CX, -1.72, 0])
        self.steps("Three more things are wrong for hello-devops. The image is latest. REDIS_HOST is localhost, instead of the Service name redis. And there is no readiness probe on /readyz. The draft also sets a CPU limit, which the lab leaves out on purpose.",
                   (0.8, FadeIn(b5), m5), (1.6, Wait(1.6)), (0.8, FadeIn(b6), m6), (2.0, Wait(2.0)), (0.8, FadeIn(b7), m7, FadeIn(more[0])),
                   (1.6, Wait(1.6)), (0.8, FadeIn(b8), m8, FadeIn(more[1])))
        fixes = [(15, "path: /healthz"), (7, "- image: hello-devops:1.0.0"), (12, "value: redis")]
        self.steps("Paste the tool output and your notes back, ask for a fixed version, and run the same checks again.",
                   (1.0, travel(back, GREY_B, 1.0)),
                   (1.4, *[Transform(lines[i], self.line(i, t, GREEN_M)) for i, t in fixes], lines[13].animate.set_color(GREEN_M),
                    lines[18].animate.set_opacity(0.25), FadeOut(VGroup(b4, b5, b6, b7, b8))),
                   (1.4, scan(BLUE_M, 1.2)), (1.4, scan(PURPLE_M, 1.2)))
        ok3 = tick(True, 0.2).next_to(rv[1], RIGHT, buff=0.25)
        self.beat("When it matches the tested deployment file, and both checks pass, only then does it go into a pull request.",
                  Create(ok3), rv[0].animate.set_stroke(width=3), FadeOut(VGroup(q, routes, more)),
                  Succession(Wait(1.4), Indicate(prb, color=GREEN_M)), run_time=2.8)

        # ---------- 3. recap
        rc = VGroup(T("a tool checks every draft;", 28, WHITE), T("a person reviews what", 28, GOLD_M),
                    T("tools cannot see", 28, GOLD_M)).arrange(DOWN, buff=0.3).move_to([-3.75, 0.05, 0])
        self.beat("That is the verify loop. A tool you trust checks every draft, and a person reviews what tools cannot see.",
                  FadeOut(lines), FadeOut(ttl), LaggedStart(*[FadeIn(r, shift=0.1 * UP) for r in rc], lag_ratio=0.5), run_time=2.4)
        self.wait(1.5)
