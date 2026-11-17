import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcapstone-check\.sh\b", "capstone check dot S H"), (r"/readyz\b", "ready Z")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def term(lines, w=12.6, size=22):
    g = VGroup(*[M(t, size, c) for t, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    fit(g, w - 0.6)
    r = RoundedRectangle(corner_radius=0.1, width=w, height=g.height + 0.5, stroke_color=GREY_D, stroke_width=2).set_fill("#0b0b0b", 1)
    g.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.3)
    return VGroup(r, g)


def person(c, s=1.0):
    head = Circle(radius=0.2, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.3), opacity=1)
    body = RoundedRectangle(corner_radius=0.15, width=0.62, height=0.72, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.2), opacity=1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale(s)


STAGES = ("foundations", "containers", "CI", "JVM build", "infrastructure", "Kubernetes", "GitOps",
          "metrics", "dashboards", "logs", "traces", "Dynatrace", "security", "AI, platform")


class D68KeeperWalk(VoiceScene):
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

    def path_and_stops(self, y=0.0):
        xs = [-5.4 + 10.8 * i / 13 for i in range(14)]
        line = Line([-6.0, y, 0], [6.0, y, 0], stroke_width=10, color=GREY_D)
        stops = VGroup(*[Circle(radius=0.2, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1).move_to([x, y, 0]) for x in xs])
        nums = VGroup(*[T(str(i + 1), 20, GREY_B).move_to(s) for i, s in enumerate(stops)])
        labs = VGroup(*[T(n, 20, GREY_B).next_to(s, UP if i % 2 == 0 else DOWN, buff=0.3) for i, (n, s) in enumerate(zip(STAGES, stops))])
        return line, stops, nums, labs

    def construct(self):
        self.title_card("The walk before opening night", "acceptance checks for your capstone")

        # ---------- 1. the keeper's walk
        line, stops, nums, labs = self.path_and_stops(-0.6)
        gate = T("gate", 24, GREY_B).move_to([-6.0, 0.9, 0])
        stn = T("station", 24, GREY_B).move_to([6.0, 0.9, 0])
        self.beat("The new path through the park opens on Saturday. On Friday evening, the keeper walks it once more, from the gate to the station, with a clipboard.",
                  Create(line), FadeIn(gate), FadeIn(stn), run_time=2.4)
        lamps = VGroup(*[Dot(radius=0.1, color=GREY_D).move_to([x, 1.4, 0]) for x in (-3.5, -0.5, 2.5)])
        bridge = Arc(radius=0.9, start_angle=PI * 0.15, angle=PI * 0.7, stroke_color=GREY_B, stroke_width=4).move_to([0.9, -0.15, 0])
        drain = Rectangle(width=0.7, height=0.25, stroke_color=BLUE_M, stroke_width=2.5).move_to([4.0, -1.4, 0])
        keeper = person(GREEN_M, 0.8).move_to([-5.6, -1.9, 0])
        self.steps("Does every lamp come on at dusk? Does the little bridge hold a heavy bin lorry? Does the drain by the pond take a bucket of water?",
                   (0.8, FadeIn(keeper), FadeIn(lamps)), (0.8, *[l.animate.set_color(YELLOW_M) for l in lamps]), (0.6, Wait(0.6)),
                   (0.8, Create(bridge), keeper.animate.move_to([0.9, -1.9, 0])), (0.8, Wait(0.8)),
                   (0.8, FadeIn(drain), keeper.animate.move_to([4.0, -2.3, 0])), (0.6, drain.animate.set_fill(BLUE_M, 0.6)))
        self.beat("Each part passed its own test when it was built. The walk is the first time they all have to work together.",
                  run_time=None)
        swl = T("lamp and sprinklers: same switch", 24, RED_M).move_to([0, 2.6, 0])
        self.beat("Skipping the walk is tempting. Every piece was checked, so the whole thing must be fine. That's exactly how a lamp ends up wired to the same switch as the sprinklers.",
                  Succession(Wait(3.4), FadeIn(swl)), run_time=4.4)
        self.play(FadeOut(VGroup(lamps, bridge, drain, swl, gate, stn)), keeper.animate.move_to([-6.0, -1.9, 0]), run_time=0.6)

        # ---------- 2. the capstone: one change, fourteen stops
        self.beat("Your capstone is that walk. One small code change travels from your laptop to users, through every part of this course.",
                  LaggedStart(*[FadeIn(s) for s in stops], lag_ratio=0.06), FadeIn(nums), run_time=2.4)
        self.beat("Fourteen stages, in order. Foundations, containers, CI, and so on, all the way to security, AI and the platform.",
                  LaggedStart(*[FadeIn(l, shift=UP * 0.05) for l in labs], lag_ratio=0.12), run_time=4.4)
        opt = T("optional", 20, GOLD_M).next_to(labs[11], DOWN, buff=0.08)
        self.beat("Stage twelve, Dynatrace, is optional. Do it last, so its trial clock starts when everything else already works.",
                  FadeIn(opt), Indicate(labs[11], color=GOLD_M), run_time=2.0)
        rules = VGroup(T("go in order", 26), T("done = its check passes, not \"looks fine\"", 26, YELLOW_M), T("commit after each stage", 26)).arrange(DOWN, buff=0.15).move_to([1.0, -2.65, 0])
        self.beat("Three rules. Go in order. A stage is done when its check passes, not when it looks fine. And commit after each stage.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rules], lag_ratio=0.9), run_time=6.0)
        walk = VGroup(line, stops, nums, labs, opt, keeper)
        self.play(FadeOut(rules), walk.animate.scale(0.8).move_to([0, 2.3, 0]), run_time=0.8)

        # ---------- 3. what makes a check worth trusting
        weak = VGroup(T("weak", 26, RED_M), T("\"Argo CD works\"", 28)).arrange(DOWN, buff=0.2).move_to([-3.6, -0.2, 0])
        strong = VGroup(T("strong", 26, GREEN_M), T("after a merge, with no kubectl,", 24), M("kubectl -n argocd get application hello-devops", 22, GREY_B),
                        T("reports Synced and Healthy", 24)).arrange(DOWN, buff=0.15).move_to([2.5, -0.4, 0])
        self.beat("But what counts as a check? Take stage seven, GitOps. Here are two ways to write its check.",
                  FadeIn(weak), FadeIn(strong), run_time=2.0)
        self.beat("Pause and guess: which one could ever fail?", run_time=None)
        self.wait(2.0)
        self.beat("Argo CD works can't clearly fail. You'd just shrug and say it looks fine. So passing it tells you nothing. The strong one looks at the running system, after a real merge.",
                  Wiggle(weak[1]), Succession(Wait(3.6), Indicate(strong[2], color=GREEN_M)), run_time=5.0)
        rule = T("A check that cannot fail proves nothing.", 30, YELLOW_M).move_to([0, -2.6, 0])
        self.beat("So here's the rule. A check that cannot fail proves nothing. Make every check able to say FAIL.",
                  FadeIn(rule, shift=UP * 0.1), run_time=1.6)
        props = VGroup(chip("observable: looks at the running system", TEAL_M, 24), chip("binary: PASS or FAIL, no judgment", TEAL_M, 24),
                       chip("runnable: one command, repeat any time", TEAL_M, 24)).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([0, -0.6, 0])
        self.beat("A good check is observable: it looks at the running system. Binary: pass or fail. And runnable: one command you can repeat.",
                  FadeOut(VGroup(weak, strong, rule)), LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in props], lag_ratio=0.9), run_time=9.0)
        self.play(FadeOut(props), run_time=0.5)

        # ---------- 4. show: a checklist line becomes a check
        t1 = term([("$ docker run --rm --entrypoint id hello-devops:1.2.0 -u", GREY_B), ("10001", YELLOW_M),
                   ("$ got=$(curl -s localhost:8000/ | jq -r .version)", GREY_B),
                   ('$ if [[ "$got" == "1.2.0" ]]; then echo "PASS  app reports 1.2.0";', GREY_B),
                   ('  else echo "FAIL  app reports \'$got\'"; fi', GREY_B),
                   ("PASS  app reports 1.2.0", GREEN_M)], w=12.6).move_to([0, -0.4, 0])
        self.steps("Let's turn one line of the checklist into such a check. Stage two: the image runs as a non-root user, and reports its version. Ask the image itself, not your memory of the Dockerfile. User 10001.",
                   (1.0, Indicate(labs[1], color=WHITE)), (2.8, Wait(2.8)), (0.8, FadeIn(t1[0]), FadeIn(t1[1][0])), (1.2, Wait(1.2)), (0.6, FadeIn(t1[1][1])))
        self.beat("Then make it binary. This little if prints PASS or FAIL. Every line of the lab's capstone check script follows the same pattern.",
                  FadeIn(t1[1][2]), FadeIn(t1[1][3]), FadeIn(t1[1][4]), Succession(Wait(2.2), FadeIn(t1[1][5])), run_time=3.6)
        self.play(FadeOut(t1), run_time=0.5)
        t2 = term([("$ security/capstone-check.sh        (trimmed)", GREY_B),
                   ("FAIL  Deployment hello-devops is not ready", RED_M),
                   ("PASS  App at http://localhost:8000/ reports version 1.2.0", GREEN_M),
                   ("FAIL  Argo CD Application hello-devops not found in namespace argocd", RED_M),
                   ("SKIP  cosign not installed", GOLD_M),
                   ("FAIL  Prometheus at http://localhost:9090 has no hello_requests_total", RED_M),
                   ("1 passed, 8 failed, 2 skipped", WHITE)], w=12.6).move_to([0, -0.5, 0])
        self.beat("The script turns eleven of the fourteen stages into checks. Run it this early, and almost everything fails. One passed, eight failed, two skipped. That's normal. Read it as your to-do list, in order.",
                  FadeIn(t2[0]), LaggedStart(*[FadeIn(l) for l in t2[1]], lag_ratio=0.3), run_time=4.4)
        self.beat("Skip means a tool or address is missing. And the script exits with one on any failure, so CI could run it.",
                  Indicate(t2[1][4], color=GOLD_M), run_time=2.0)
        q2 = T("Argo CD fails, Prometheus fails. Which do you fix first? Pause and guess.", 26, YELLOW_M).move_to([0, -3.2, 0])
        fit(q2, 12.6)
        self.beat("Quick one. Argo CD fails, and Prometheus fails. Which do you fix first? Pause and guess.",
                  FadeIn(q2), Indicate(t2[1][3], color=RED_M), Indicate(t2[1][5], color=RED_M), run_time=2.0)
        self.wait(2.0)
        self.beat("Argo CD. The deploy feeds the rest. If the app isn't deployed, Prometheus has nothing to scrape. Stages depend on the ones before them.",
                  Transform(q2, T("Argo CD first: the deploy feeds the rest", 26, GREEN_M).move_to(q2)), run_time=2.0)
        self.play(FadeOut(VGroup(t2, q2)), run_time=0.5)

        # ---------- 5. break the shortcut: only check today's stage
        self.play(walk.animate.scale(1 / 0.8).move_to([0, 0.2, 0]), run_time=0.8)
        for i in range(8):
            stops[i].set_stroke(GREEN_M).set_fill(tint(GREEN_M, 0.4), 1)
        self.beat("Now a tempting shortcut. Say stages one to eight are green. You've just finished stage nine. Why not run only the check for the stage you just did? It's faster.",
                  *[Indicate(stops[i], color=GREEN_M, scale_factor=1.15) for i in range(8)], run_time=3.0)
        self.steps("Let's be fair to it, and try. Say the port-forward you started for stage nine's dashboard grabbed port 8081. Stage nine's own check passes.",
                   (2.4, Wait(2.4)), (0.8, stops[8].animate.set_stroke(GREEN_M).set_fill(tint(GREEN_M, 0.4), 1)), (1.0, Indicate(labs[8], color=GREEN_M)))
        self.beat("Pause and guess: is everything still green?", run_time=None)
        self.wait(2.0)
        x6 = tick(False, 0.18).move_to(stops[5])
        self.steps("No. The old stage six check, the app on localhost 8081, now fails. The shortcut would never have told you.",
                   (0.6, Wait(0.6)), (0.8, stops[5].animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.4), 1), Create(x6)), (1.0, Indicate(labs[5], color=RED_M)))
        self.beat("Later stages often break earlier ones: a new policy rejects Redis, a port gets taken. So rerun the whole script after every stage. The keeper tries every lamp, not just today's.",
                  run_time=None)
        self.play(FadeOut(x6), stops[5].animate.set_stroke(GREEN_M).set_fill(tint(GREEN_M, 0.4), 1), run_time=0.6)

        # ---------- 6. a game day: the bucket in the drain
        self.play(walk.animate.scale(0.8).move_to([0, 2.3, 0]), run_time=0.8)
        gd = T("game day: break it on purpose", 30, BLUE_M).move_to([0, 0.5, 0])
        self.beat("Checks prove the path works when things go right. A game day finds out what happens when they go wrong. You break something on purpose, like pouring a bucket into the drain before the first storm.",
                  FadeIn(gd), run_time=2.4)
        cmd = M("kubectl scale deployment redis -n hello --replicas=0", 22, WHITE).move_to([0, -0.3, 0])
        exp = VGroup(T("write down first what you expect:", 24, GREY_B), T("/readyz returns 503, Pods go unready, an alert fires,", 24),
                     T("error logs in Kibana, a failed span in Jaeger", 24)).arrange(DOWN, buff=0.14).move_to([0, -1.6, 0])
        self.beat("If you do one drill, scale Redis to zero. But first, write down what you expect: 503 from the readiness check, unready Pods, an alert, error logs in Kibana, a failed span in Jaeger.",
                  FadeIn(cmd), Succession(Wait(3.6), LaggedStart(*[FadeIn(e) for e in exp], lag_ratio=0.6)), run_time=9.0)
        diff = T("expected vs. what happened: where they differ, your picture was wrong", 24, YELLOW_M).move_to([0, -3.0, 0])
        fit(diff, 12.4)
        self.beat("Afterwards, write down what really happened. Wherever the two differ, your picture of the system was wrong. That's the part worth writing up, and the story interviewers like most.",
                  FadeIn(diff, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(VGroup(walk, gd, cmd, exp, diff)), run_time=0.6)

        # ---------- 7. the honest limit
        lim = VGroup(T("The capstone runs on kind.", 30), T("Still ahead: real traffic, a real cloud bill, a night on call.", 28, GOLD_M)).arrange(DOWN, buff=0.3).move_to([0, 0.6, 0])
        self.beat("One honest limit. The capstone runs on kind, the practice cluster on your laptop. Real traffic, a real cloud bill and a night on call are still ahead of you. That's what the next three months are for.",
                  FadeIn(lim[0]), Succession(Wait(2.6), FadeIn(lim[1])), run_time=4.0)
        self.play(FadeOut(lim), run_time=0.5)

        # ---------- 8. moral and a quick check
        mor = VGroup(T("Walk the whole path before opening night.", 30),
                     T("a stage is done when its check passes", 28, YELLOW_M),
                     T("a good check is observable, binary, runnable", 28, TEAL_M),
                     T("rerun every check after every stage", 28, GREEN_M),
                     T("break it on purpose, and write down what you expect", 28, BLUE_M)).arrange(DOWN, buff=0.35)
        self.beat("The moral of the story: walk the whole path before opening night. Done means the check passes. Checks are observable, binary, runnable. Rerun them all after every stage. And break it on purpose, expectations first.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mor], lag_ratio=0.8), run_time=9.0)
        self.play(FadeOut(mor), run_time=0.6)
        q = VGroup(T("You want to show an interviewer you can do DevOps work.", 30), T("Which gives the strongest evidence?", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 1.8, 0])
        opts = VGroup(chip("a list of 20 tools on your CV", GREY_B, 24), chip("a multiple-choice certificate", GREY_B, 24),
                      chip("a repo where a commit becomes a checked deploy", GREY_B, 24), chip("a screenshot of a busy dashboard", GREY_B, 24)).arrange(DOWN, buff=0.22).move_to([0, -0.9, 0])
        self.beat("One last check. You want to show an interviewer that you can do DevOps work. Which gives the strongest evidence? Pause and think.",
                  FadeIn(q), LaggedStart(*[FadeIn(o, shift=UP * 0.1) for o in opts], lag_ratio=0.3), run_time=4.0)
        self.wait(2.0)
        self.beat("A repository where a commit becomes a checked deploy. Run the capstone check now, even if most lines say FAIL. That list is your route. Thanks for walking the path with me.",
                  opts[2][0].animate.set_stroke(GREEN_M).set_fill(GREEN_M, 0.3), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 2], run_time=1.6)
        self.wait(1.0)
