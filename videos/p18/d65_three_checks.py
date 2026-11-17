import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bkubeconform\b", "cube conform"), (r"--strict-mode\b", "dash dash strict mode"), (r"(?<![\w-])-strict\b", "dash strict"),
            (r"\bcontainerPort\b", "container port"), (r"\btimeoutSeconds\b", "timeout seconds"), (r"/healthz\b", "slash health Z"),
            (r"/health\b", "slash health"), (r"/readyz\b", "slash ready Z"), (r"\bREDIS_HOST\b", "redis host"),
            (r":latest\b", " colon latest"), (r"--dry-run=server", "dry run server"), (r"\bAGENTS\.md\b", "agents dot M D")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(rows, color, buff=0.26):
    fr = RoundedRectangle(corner_radius=0.12, width=rows.width + 2 * buff, height=rows.height + 2 * buff, stroke_color=color, stroke_width=2.5)
    fr.set_fill(tint(color, 0.10), 1)
    return VGroup(fr, rows.move_to(fr))


def card(lines, color=GREY_B):
    rows = VGroup(*[T(l, 26, c) for l, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    fr = Rectangle(width=rows.width + 0.8, height=rows.height + 0.7, stroke_color=color, stroke_width=2.5).set_fill(tint(GOLD_M, 0.08), 1)
    return VGroup(fr, rows.move_to(fr))


DRAFT = [("selector:    app: hello-devops", WHITE),
         ("Pod labels:  app: hello", WHITE),
         ("image: hello-devops:latest", WHITE),
         ('containerPort: "8000"', WHITE),
         ("livenessProbe path: /health", WHITE),
         ("livenessProbe timeout: ...", WHITE),
         ("env REDIS_HOST: localhost", WHITE),
         ("resources limits cpu: ...", WHITE),
         ("(no readinessProbe)", GREY_B)]


class D65ThreeChecks(VoiceScene):
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
        self.title_card("Neat handwriting is not a proof", "the verify loop for AI-written files")

        # ---------- 1. the shy question
        ask = panel(T("Which kubeconform flag rejects unknown fields?", 28), BLUE_M).move_to([0, 1.6, 0])
        ans = panel(M("--strict-mode", 28, WHITE), GREY_B).move_to([0, 0.2, 0])
        self.beat("You ask an AI assistant which flag makes kubeconform, a tool that checks Kubernetes files, reject unknown fields.",
                  FadeIn(ask, shift=DOWN * 0.15), run_time=2.6)
        self.beat("It answers in two seconds, with no sign of doubt. Strict mode.",
                  FadeIn(ans, shift=UP * 0.15), run_time=1.8)
        q = T("it sounded certain. Is it right?", 30, YELLOW_M).move_to([0, -1.3, 0])
        self.beat("So here's the question we're shy to ask out loud. It sounded so sure. Doesn't that count for something? Hold your answer.",
                  FadeIn(q, shift=UP * 0.1), run_time=2.4)
        self.wait(0.3)
        self.play(FadeOut(VGroup(ask, ans, q)), run_time=0.5)

        # ---------- 2. familiar: the intern's recipe card
        cd = card([("Strawberry jam", WHITE), ("boil at setting 11", WHITE), ("add 2 spoons of Moonberry pectin", WHITE)]).move_to([-2.8, 0.3, 0])
        self.beat("Back to the jam shop. A summer intern has read every cookbook in the library, and writes you a strawberry jam card in thirty seconds, in lovely handwriting.",
                  FadeIn(cd, shift=UP * 0.15), run_time=3.0)
        stove = VGroup(RoundedRectangle(corner_radius=0.12, width=2.4, height=1.6, stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.08), 1))
        dial = VGroup(*[T(str(n), 22, GREY_B) for n in range(1, 7)]).arrange(RIGHT, buff=0.18)
        stove.add(dial.move_to(stove[0]))
        stove.move_to([3.6, 0.9, 0])
        stl = T("your stove: settings 1 to 6", 24, GREY_B).next_to(stove, DOWN, buff=0.2)
        x1 = tick(False, 0.2).next_to(cd[1][1], RIGHT, buff=0.3)
        self.beat("It looks perfect. It also says to boil the fruit at a setting your stove doesn't have.",
                  FadeIn(stove), FadeIn(stl), Succession(Wait(2.0), AnimationGroup(cd[1][1].animate.set_color(RED_M), Create(x1))), run_time=3.2)
        x2 = tick(False, 0.2).next_to(cd[1][2], RIGHT, buff=0.3)
        nob = T("no such brand", 24, RED_M).move_to([3.6, -1.4, 0])
        self.beat("And it names a brand of pectin that doesn't exist.",
                  cd[1][2].animate.set_color(RED_M), Create(x2), FadeIn(nob), run_time=1.8)
        self.beat("The intern wasn't lying. They wrote what recipe cards usually look like. Neat handwriting and a confident tone feel like being right. They aren't the same thing.",
                  Indicate(cd[1], color=GOLD_M, scale_factor=1.03), run_time=2.6)

        # ---------- 3. what the model does: likely text
        self.play(FadeOut(VGroup(stove, stl, nob)), run_time=0.4)
        lm = VGroup(T("a language model writes the likely next words", 28, BLUE_M),
                    T("common shapes: come out well", 26, GREEN_M),
                    T("rare or recent details: guesses that look like facts", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([2.6, 0.3, 0])
        self.play(FadeOut(VGroup(x1, x2)), run_time=0.3)
        self.play(cd.animate.scale(0.75).move_to([-4.3, 2.2, 0]), run_time=0.6)
        lm.move_to([0.6, -0.6, 0])
        self.beat("An AI assistant works the same way. Inside it sits a language model, a program trained on a huge amount of text to predict the next words. It isn't looking anything up.",
                  FadeIn(lm[0], shift=UP * 0.1), run_time=3.0)
        self.beat("So common shapes come out well, because it has seen them thousands of times. Rare or recent details, a renamed flag, an exact field, a version, come out as guesses that look exactly like facts.",
                  FadeIn(lm[1], shift=UP * 0.1), Succession(Wait(2.8), FadeIn(lm[2], shift=UP * 0.1)), run_time=5.0)
        self.beat("And it sounds just as sure when it is wrong. So its confidence tells you nothing.",
                  Indicate(lm[2], color=RED_M, scale_factor=1.03), run_time=2.0)
        help_ = panel(VGroup(M("$ kubeconform -h", 24, GREY_B), M("-strict", 26, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15), GREEN_M).move_to([0.6, 2.2, 0])
        self.beat("Remember strict mode? It was wrong. The real flag is minus strict, and the tool's own help text settles it in seconds.",
                  FadeIn(help_, shift=DOWN * 0.15), run_time=2.4)
        self.wait(0.3)
        self.play(FadeOut(VGroup(cd, lm, help_)), run_time=0.5)

        # ---------- 4. a real draft, and a prediction
        rows = VGroup(*[M(t, 22, c) for t, c in DRAFT]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        dp = panel(rows, GOLD_M, buff=0.3).move_to([-3.4, -0.25, 0])
        dl = T("the AI's draft, key lines", 24, GOLD_M).next_to(dp, UP, buff=0.18)
        self.beat("Now a real case from the lab. You ask an assistant for a Kubernetes Deployment for hello-devops, our tiny web app, with three copies, a health check and Redis as the database. No files, no versions.",
                  FadeIn(dl), FadeIn(dp[0]), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows], lag_ratio=0.12), run_time=5.0)
        self.beat("A Deployment is the settings file that tells Kubernetes how to run your app. The answer came back in seconds, neatly indented. How many mistakes are in it? Pause and guess.",
                  Indicate(dl, color=GOLD_M, scale_factor=1.1), run_time=2.6)
        self.wait(2.0)

        # ---------- 5. three checks, one after another
        def filt(title, sub, color, y):
            r = RoundedRectangle(corner_radius=0.12, width=5.6, height=1.75, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1).move_to([3.5, y, 0])
            t = M(title, 22, color).move_to(r.get_top() + DOWN * 0.3).align_to(r, LEFT).shift(RIGHT * 0.25)
            s = T(sub, 22, GREY_B).next_to(t, RIGHT, buff=0.25)
            return VGroup(r, t, s)

        f1 = filt("kubeconform -strict", "the schema", TEAL_M, 2.1)
        f2 = filt("dry-run=server", "the cluster", BLUE_M, 0.05)
        f3 = filt("your review", "the intent", PURPLE_M, -2.0)

        def flag(i, color=RED_M):
            return rows[i].animate.set_color(color)

        def note(f, lines, color=RED_M):
            g = VGroup(*[T(l, 22, color) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            return g.next_to(f[1], DOWN, buff=0.15, aligned_edge=LEFT)

        scan = Line([-6.0, 0, 0], [0.0, 0, 0], stroke_color=TEAL_M, stroke_width=4).move_to([dp.get_x(), dp.get_top()[1] - 0.1, 0])
        self.beat("Check one. kubeconform checks each object against the official schema, the list of allowed fields and their types. With minus strict, it also rejects fields the schema doesn't know.",
                  FadeIn(f1), run_time=3.0)
        n1 = note(f1, ["port: got string, want integer", "'timeout' not allowed"])
        self.steps("It finds two. The port is written as text, not a number. And timeout isn't a probe field at all. The real one is timeoutSeconds.",
                   (0.2, FadeIn(scan)), (1.4, scan.animate.move_to([dp.get_x(), dp.get_bottom()[1] + 0.1, 0])), (0.2, FadeOut(scan)),
                   (0.6, flag(3), FadeIn(n1[0])), (1.4, Wait(1.4)), (0.6, flag(5), FadeIn(n1[1])))
        self.beat("Without minus strict, the invented field slips straight through. A made-up field looks exactly like a real one, sitting where a real one would sit.",
                  Indicate(rows[5], color=RED_M, scale_factor=1.04), run_time=2.4)
        self.beat("Fix those two, and kubeconform is happy. Are we done? I know what you're thinking: the checker said valid. Let's be suspicious anyway.",
                  Indicate(f1[1], color=TEAL_M), run_time=2.4)
        self.beat("Check two. A server dry run sends the file to the cluster's front desk, the API server. It runs every check of a real apply, then throws the object away. Here we run it against kind, the small practice cluster on your laptop.",
                  FadeIn(f2), run_time=3.4)
        n2 = note(f2, ["`selector` does not match", "template `labels`"])
        self.steps("It finds one more. The selector looks for app hello-devops, but the Pods are labelled app hello. The Deployment could never find its own Pods.",
                   (0.6, Wait(0.6)), (0.8, flag(0, GOLD_M), flag(1, GOLD_M), FadeIn(n2, shift=UP * 0.1)), (2.0, Wait(2.0)),
                   (0.8, Indicate(rows[1], color=GOLD_M, scale_factor=1.04)))
        self.beat("Some rules live only in the server, and a schema can't see them. That's why the loop doesn't stop at the first green tick.",
                  Wait(0.1), run_time=0.4)
        self.beat("Check three is you. No tool knows what hello-devops actually needs. So you read it, the way you'd read the intern's card next to your own stove.",
                  FadeIn(f3), run_time=3.0)
        n3 = note(f3, ["app serves /healthz, not /health", ":latest, REDIS_HOST should be redis,", "no readiness probe on /readyz"])
        self.steps("The probe asks for slash health, but the app serves slash health Z. The image is latest. REDIS_HOST is localhost instead of the Service name, redis. And there's no readiness probe.",
                   (0.6, flag(4, PURPLE_M), FadeIn(n3[0])), (2.0, Wait(2.0)), (0.6, flag(2, PURPLE_M), FadeIn(n3[1])),
                   (1.6, flag(6, PURPLE_M)), (0.8, flag(8, PURPLE_M), FadeIn(n3[2])))
        self.beat("The draft also sets a CPU limit, which the lab leaves out on purpose. Neat, confident, and wrong in many small places, exactly like the jam card.",
                  flag(7, PURPLE_M), run_time=2.4)
        self.wait(0.4)

        # ---------- 6. name it: the verify loop
        self.play(FadeOut(VGroup(n1, n2, n3)), run_time=0.4)
        loop = VGroup(T("draft", 26, GOLD_M), T("check", 26, TEAL_M), T("fix", 26, PURPLE_M), T("check again", 26, BLUE_M))
        loop.arrange(RIGHT, buff=0.9).move_to([0, 3.1, 0])
        larr = VGroup(*[Arrow(loop[i].get_right(), loop[i + 1].get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25) for i in range(3)])
        self.play(FadeOut(VGroup(dp, dl, rows)), f1.animate.move_to([0, 1.85, 0]), f2.animate.move_to([0, 0.0, 0]),
                  f3.animate.move_to([0, -1.85, 0]), run_time=0.8)
        self.beat("Paste the exact errors back, ask for a fixed version, and run the same checks again. This habit has a name: the verify loop. Draft, check with a tool you trust, fix, check again.",
                  LaggedStart(*[FadeIn(w) for w in loop], lag_ratio=0.4), Succession(Wait(1.6), LaggedStart(*[GrowArrow(a) for a in larr], lag_ratio=0.4)), run_time=5.0)
        rule = T("nothing that failed or skipped a check reaches main", 26, YELLOW_M).move_to([0, -3.1, 0])
        self.beat("Nothing that has failed or skipped a check reaches main, the shared branch that releases come from.",
                  FadeIn(rule, shift=UP * 0.1), run_time=2.0)

        # ---------- 7. guardrail: what each check can and can't see
        cs = VGroup(T("needs no cluster, knows only the schema", 22, GREY_B).next_to(f1[1], DOWN, buff=0.2, aligned_edge=LEFT),
                    T("needs kind, knows your cluster's rules", 22, GREY_B).next_to(f2[1], DOWN, buff=0.2, aligned_edge=LEFT),
                    T("the only one that knows what you meant", 22, GREY_B).next_to(f3[1], DOWN, buff=0.2, aligned_edge=LEFT))
        self.beat("Each check has a limit. kubeconform needs no cluster, but knows only the schema. The dry run needs kind, but knows your cluster's rules. Checks prove shape, not intent. Only your review knows what you meant.",
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in cs], lag_ratio=0.9), run_time=6.0)
        self.beat("Which gives a plain rule. Use AI for work you could check yourself, and never for a file you couldn't review.",
                  Indicate(f3[1], color=PURPLE_M), run_time=2.4)
        self.wait(0.4)
        self.play(FadeOut(VGroup(f1, f2, f3, cs, loop, larr, rule)), run_time=0.5)

        # ---------- 8. moral and quick check
        m1 = T("The model drafts.", 36, GOLD_M)
        m2 = T("A tool you trust decides.", 36, TEAL_M)
        moral = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to([0, 1.4, 0])
        self.beat("So the moral of the story. The model drafts. A tool you trust decides. And you decide what the tools can't see.",
                  FadeIn(m1, shift=UP * 0.12), Succession(Wait(1.6), FadeIn(m2, shift=UP * 0.12)), run_time=3.6)
        self.wait(0.4)
        self.play(FadeOut(moral), run_time=0.5)
        qq = T("Quick check", 30, YELLOW_M).move_to([0, 2.3, 0])
        qt = T("An assistant says, with no doubt: use --strict-mode.", 30).move_to([0, 1.2, 0])
        qt2 = T("What do you do before you use it?", 30).move_to([0, 0.5, 0])
        self.beat("A quick check. An assistant tells you, with no doubt at all, to use strict mode. What do you do before you use it? Pause and think.",
                  FadeIn(qq), FadeIn(qt), FadeIn(qt2), run_time=2.6)
        self.wait(2.0)
        a = T("check the tool's own help: kubeconform -h", 30, GREEN_M).move_to([0, -0.8, 0])
        self.beat("Check the tool's own help. Here, kubeconform minus h shows the real flag, minus strict. A few seconds of checking beats any amount of confidence.",
                  FadeIn(a, shift=UP * 0.15), run_time=2.4)
        self.wait(1.0)
