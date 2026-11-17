import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\breplicaCount\b", "replica count"), (r"\bvalues\.yaml\b", "values dot yammel"), (r"\bprod\.yaml\b", "prod dot yammel"),
            (r"\bimage\.tag\b", "image dot tag"), (r"\bChart\.yaml\b", "chart dot yammel"), (r"--set\b", "dash dash set"),
            (r"\bClusterIP\b", "cluster I P"), (r"\bPodDisruptionBudget\b", "pod disruption budget")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def card(lines, color, w=None, size=22, pad=0.35):
    g = VGroup(*[M(t, size, c) for t, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    r = RoundedRectangle(corner_radius=0.12, width=w or g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=3)
    r.set_fill(tint(color, 0.1), 1)
    g.move_to(r).align_to(r, LEFT).shift(RIGHT * pad)
    return VGroup(r, g)


def sticky(text, c=YELLOW_M, size=22):
    t = M(text, size, BLACK)
    r = Rectangle(width=t.width + 0.35, height=0.55, stroke_width=0).set_fill(c, 0.92)
    t.move_to(r)
    return VGroup(r, t).rotate(0.05)


class D45TwoRoads(VoiceScene):
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
        self.title_card("One recipe, three branches", "Helm fills blanks, Kustomize adds sticky notes")

        # ---------- 1. the photocopied binder
        orig = card([("soup", WHITE), ("salt: 2 spoons", GREY_B), ("oven: 20 min", GREY_B)], TEAL_M).move_to([0, 2.0, 0])
        self.beat("Picture the restaurant opening a second branch, then a third. The quickest plan is to photocopy the recipe binder, once for each kitchen.",
                  FadeIn(orig), run_time=1.4)
        BX = (-4.4, 0, 4.4)
        cps = VGroup(*[orig.copy().move_to([x, -1.0, 0]) for x in BX])
        blabs = VGroup(*[T(f"branch {i + 1}", 24, GREY_B).next_to(c, UP, buff=0.15) for i, c in enumerate(cps)])
        self.play(LaggedStart(*[TransformFromCopy(orig, c) for c in cps], lag_ratio=0.25), FadeIn(blabs), run_time=1.6)
        self.play(FadeOut(orig), run_time=0.4)
        d1 = M("salt: 1 spoon", 22, RED_M).move_to(cps[0][1][1], aligned_edge=LEFT)
        d2 = M("oven: 25 min", 22, RED_M).move_to(cps[2][1][2], aligned_edge=LEFT)
        self.steps("It works for a month. Then one branch cuts the salt in the soup. Another changes the oven time.",
                   (1.4, Wait(1.4)), (0.8, Transform(cps[0][1][1], d1)), (0.6, Wait(0.6)), (0.8, Transform(cps[2][1][2], d2)))
        qs = VGroup(*[T("on purpose?", 24, YELLOW_M).next_to(c, DOWN, buff=0.25) for c in cps])
        self.beat("A year later, the three soups taste different. And nobody can say which changes were on purpose, and which were accidents.",
                  LaggedStart(*[FadeIn(q, shift=UP * 0.1) for q in qs], lag_ratio=0.3), run_time=2.4)

        # same thing in our lab
        yl = VGroup(*[M(n, 26, TEAL_M).move_to(b) for n, b in zip(("dev/", "staging/", "prod/"), blabs)])
        self.steps("Our app is in the same spot. hello-devops has over ten YAML files, plain text files describing its objects. Dev, staging and prod make three copies.",
                   (1.0, FadeOut(qs)), (2.6, Wait(2.6)), (1.0, *[Transform(b, y) for b, y in zip(blabs, yl)]))
        dif = VGroup(*[card([(f"image tag: {t}", GREY_B), (f"replicas: {r}", GREY_B), (f"greeting: {g}", GREY_B)], GREY_B, size=20).move_to([x, -1.0, 0])
                       for t, r, g, x in (("1.1.0", "1", "dev", BX[0]), ("1.0.0", "2", "staging", BX[1]), ("1.0.0", "4", "prod", BX[2]))])
        pdb = M("+ disruption budget", 22, GOLD_M).next_to(dif[2], DOWN, buff=0.25)
        self.beat("Each copy needs its own image tag, its own replica count and its own greeting. And prod also wants a disruption budget.",
                  *[Transform(c, d) for c, d in zip(cps, dif)], Succession(Wait(2.6), FadeIn(pdb)), run_time=3.4)
        fix = M("probe fixed", 22, GREEN_M).next_to(dif[2], DOWN, buff=0.7)
        old = M("old probe", 22, RED_M).next_to(dif[0], DOWN, buff=0.25)
        self.beat("Then someone fixes a probe in prod, and forgets dev.",
                  FadeIn(fix), Succession(Wait(1.2), FadeIn(old)), run_time=2.2)
        self.beat("Copy and paste is a wonderful invention. It makes three things that agree today, and disagree forever after.",
                  run_time=None)
        self.beat("What we want is to write the recipe once, and say only what differs per branch. There are two popular ways.",
                  run_time=None)
        self.play(FadeOut(VGroup(cps, blabs, pdb, fix, old)), run_time=0.6)

        # ---------- 2. road one: a recipe card with blanks (Helm)
        h1 = T("a recipe card with blanks", 30, BLUE_M).move_to([0, 3.2, 0])
        tpl = card([("replicas: {{ .Values.replicaCount }}", WHITE), ("GREETING: {{ .Values.greeting | quote }}", WHITE)], BLUE_M, size=24).move_to([-2.6, 1.6, 0])
        tl = T("template", 24, BLUE_M).next_to(tpl, UP, buff=0.15, aligned_edge=LEFT)
        self.beat("The first way is a recipe card with blanks for the amounts. You write the YAML once, and leave blanks in it.",
                  FadeIn(h1), FadeIn(tpl), FadeIn(tl), run_time=2.0)
        self.beat("This blank reads the replica count from the values. This one reads the greeting, and the pipe wraps it in quotes.",
                  Indicate(tpl[1][0], color=BLUE_M), Succession(Wait(2.2), Indicate(tpl[1][1], color=BLUE_M)), run_time=3.6)
        vals = card([("values.yaml", BLUE_M), ("replicaCount: 2", WHITE), ('greeting: "Hello from Helm!"', WHITE)], BLUE_M, size=22).move_to([-3.8, -0.8, 0])
        kvals = card([("kind-values.yaml", YELLOW_M), ('greeting: "Hello from Helm on kind!"', YELLOW_M)], YELLOW_M, size=22).move_to([-1.0, -2.35, 0])
        self.beat("The chart comes with default settings, the values that fill the blanks. Two replicas. Hello from Helm.",
                  FadeIn(vals), run_time=1.6)
        self.beat("Each branch adds its own values file on top. The lab's file for kind changes only the greeting. When two files set the same key, the later one wins.",
                  FadeIn(kvals, shift=UP * 0.1), Succession(Wait(3.4), Indicate(vals[1][2], color=GREY_B)), run_time=4.4)
        out = card([("replicas: 2", WHITE), ('GREETING: "Hello from Helm on kind!"', WHITE)], GREY_B, size=22).move_to([3.1, -0.9, 0])
        ol = T("plain YAML", 24, GREY_B).next_to(out, UP, buff=0.2)
        fa = Arrow([1.6, 1.4, 0], ol.get_top() + UP * 0.05, buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("Fill the blanks, and out comes plain YAML. Two replicas, and hello from Helm on kind, in quotes.",
                  GrowArrow(fa), FadeIn(out), FadeIn(ol), run_time=2.0)
        hn = VGroup(T("Helm", 34, BLUE_M), T("a tool that installs packaged apps", 24, GREY_B)).arrange(DOWN, buff=0.15).move_to([0, -2.6, 0])
        self.beat("The tool is Helm, which installs packaged apps, a bit like an app store for a cluster. Its package is a chart: templates plus default values.",
                  Transform(h1, T("Helm: templating", 30, BLUE_M).move_to(h1)), FadeOut(vals), FadeOut(kvals), Succession(Wait(0.6), FadeIn(hn)), run_time=2.4)
        cmd = M("helm template hello chart/hello-devops", 24, GREY_B).move_to([0, -2.6, 0])
        self.beat("And helm template fills every blank and prints the result, without touching the cluster. Look before you install.",
                  FadeOut(hn), FadeIn(cmd), run_time=1.6)
        self.play(FadeOut(VGroup(tpl, tl, out, ol, fa, cmd)), run_time=0.6)

        # ---------- 3. releases and revisions: a logbook in pen
        RX = [-4.8 + 2.4 * i for i in range(5)]
        RY = 0.8

        def rev(n, label, c):
            r = RoundedRectangle(corner_radius=0.12, width=2.2, height=1.15, stroke_color=c, stroke_width=3).set_fill(tint(c), 1)
            g = VGroup(M(f"rev {n}", 24, c), T(label, 20, GREY_B)).arrange(DOWN, buff=0.12).move_to(r)
            return VGroup(r, g).move_to([RX[n - 1], RY, 0])
        r1, r2, r3 = rev(1, "install", BLUE_M), rev(2, "upgrade", BLUE_M), rev(3, "upgrade: bad", RED_M)
        links = VGroup(*[Line([RX[i] + 1.1, RY, 0], [RX[i + 1] - 1.1, RY, 0], stroke_width=2, color=GREY_D) for i in range(3)])
        self.beat("When you install a chart, Helm creates a release, one named copy of it. And every install, upgrade or rollback adds a numbered revision, like lines in a logbook.",
                  FadeIn(r1), Succession(Wait(2.0), AnimationGroup(Create(links[0]), FadeIn(r2))), Succession(Wait(3.4), AnimationGroup(Create(links[1]), FadeIn(r3))), run_time=5.0)
        rb = M("helm rollback shop 1", 26, YELLOW_M).move_to([0, -1.2, 0])
        self.beat("Say revision 3 is bad. You run helm rollback, back to 1. Pause and guess: what does the history show afterwards?",
                  FadeIn(rb), run_time=1.6)
        self.wait(2.0)
        r4 = rev(4, "Rollback to 1", GREEN_M)
        echo = DashedLine(r1.get_bottom(), r4.get_bottom(), stroke_width=2, color=GREEN_M, dash_length=0.1)
        echo = ArcBetweenPoints(r1.get_bottom() + DOWN * 0.05, r4.get_bottom() + DOWN * 0.05, angle=PI / 3, color=GREEN_M, stroke_width=2.5)
        self.steps("A brand new revision 4, with the same content as revision 1. Revisions 2 and 3 stay right where they are.",
                   (0.9, Create(links[2]), FadeIn(r4)), (1.2, Create(echo)), (1.6, Indicate(r2[0], color=BLUE_M), Indicate(r3[0], color=RED_M)))
        self.beat("Helm keeps its logbook in pen, not pencil. History is never rewritten.",
                  rb.animate.set_opacity(0.4), run_time=1.4)
        self.play(FadeOut(VGroup(r1, r2, r3, r4, links, echo, rb)), run_time=0.6)

        # ---------- 4. break it: the values that quietly disappear
        dflt = card([("values.yaml", BLUE_M), ("replicaCount: 2", WHITE)], BLUE_M, size=24).move_to([-4.3, 1.5, 0])
        prodf = card([("prod.yaml", YELLOW_M), ("replicaCount: 5", WHITE)], YELLOW_M, size=24).move_to([-4.3, -0.3, 0])
        inst = M("helm install web ./chart -f prod.yaml", 24, GREY_B).move_to([1.8, 1.5, 0])
        res1 = M("replicas: 5", 28, GREEN_M).move_to([1.8, 0.7, 0])
        self.beat("Now a trap that catches nearly everyone. Defaults say two replicas. You install with a prod file that says five. Five run. So far so good.",
                  FadeIn(dflt), Succession(Wait(2.6), FadeIn(prodf)), Succession(Wait(4.0), AnimationGroup(FadeIn(inst), FadeIn(res1))), run_time=5.6)
        upg = M("helm upgrade web ./chart --set image.tag=1.2.0", 24, GREY_B).move_to([1.8, -1.0, 0])
        fit(upg, 8.6)
        self.beat("Later you upgrade, passing only a new image tag. Surely Helm remembers your prod file. How many replicas now? Pause and guess.",
                  FadeIn(upg), run_time=1.6)
        self.wait(2.0)
        res2 = M("replicas: 2", 28, RED_M).move_to([1.8, -1.8, 0])
        self.steps("Two. Well... that's not the number we wanted.",
                   (0.8, FadeIn(res2)), (0.8, Wiggle(res2)), (0.6, prodf.animate.set_opacity(0.25)))
        why = T("pass any values on upgrade: chart defaults + only what you pass now", 24, YELLOW_M).move_to([0, -3.0, 0])
        fit(why, 12.6)
        self.beat("The rule: pass any values on an upgrade, and Helm starts from the chart's defaults plus only what you pass now. Install-time settings quietly vanish.",
                  FadeIn(why, shift=UP * 0.1), Indicate(dflt[1][1], color=BLUE_M), run_time=3.0)
        self.beat("So keep settings in a values file, and pass it with dash f every time.",
                  Transform(why, T("keep settings in a values file; pass it with -f every time", 26, YELLOW_M).move_to(why)), run_time=2.0)
        self.play(FadeOut(VGroup(dflt, prodf, inst, res1, upg, res2, why, h1)), run_time=0.6)

        # ---------- 5. road two: a master recipe with sticky notes (Kustomize)
        h2 = T("a master recipe with sticky notes", 30, GREEN_M).move_to([0, 3.2, 0])
        base = card([("k8s/  (the base)", GREEN_M), ("namespace: hello", WHITE), ("replicas: 3", WHITE), ("image: hello-devops:1.0.0", WHITE),
                     ("GREETING: Hello from Kubernetes!", WHITE)], GREEN_M, w=6.4, size=24).move_to([-3.1, 0.2, 0])
        self.beat("The second way starts from the other end. Keep the recipe as plain, valid YAML, with no blanks at all. That's the base, the master recipe.",
                  FadeIn(h2), FadeIn(base), run_time=2.2)
        self.beat("You've used it already, with kubectl apply dash k.",
                  Indicate(base[1][0], color=GREEN_M), run_time=1.6)
        notes = VGroup(sticky("namespace: hello-prod"), sticky("replicas: 4"), sticky("+ pdb.yaml", GOLD_M), sticky("GREETING: Hello from prod!"))
        for n, y in zip(notes, (1.35, 0.55, -0.25, -1.05)):
            n.move_to([2.9, y, 0])
        ovl = T("overlays/prod", 26, YELLOW_M).move_to([2.9, 2.2, 0])
        self.beat("An overlay is another folder. It points at the base, and lists only the changes for one branch. Those are the sticky notes.",
                  FadeIn(ovl), LaggedStart(*[FadeIn(n, shift=LEFT * 0.2) for n in notes], lag_ratio=0.3), run_time=2.6)
        self.beat("Prod moves everything into the namespace hello-prod, runs four replicas, says hello from prod, and adds one file only prod has: a disruption budget.",
                  *[Indicate(n, color=WHITE, scale_factor=1.05) for n in notes], run_time=3.0)
        tgt = [base[1][1], base[1][2], None, base[1][4]]
        self.steps("Kustomize lays the notes on top, and prints the result. Plain YAML again.",
                   (1.6, notes[0].animate.scale(0.85).move_to(base[1][1].get_right() + RIGHT * 1.5),
                    notes[1].animate.scale(0.85).move_to(base[1][2].get_right() + RIGHT * 2.2),
                    notes[3].animate.scale(0.85).move_to(base[1][4].get_right() + RIGHT * 1.6),
                    notes[2].animate.scale(0.85).move_to(base.get_bottom() + DOWN * 0.5)),
                   (1.0, Wait(1.0)))
        cmdk = M("kubectl kustomize overlays/prod", 24, GREY_B).move_to([0, -3.1, 0])
        self.play(FadeIn(cmdk), run_time=0.5)
        self.steps("Lift the notes off, and the base is untouched. Nothing in the k8s folder changed.",
                   (1.2, notes.animate.shift(RIGHT * 6.5).set_opacity(0)), (1.0, Indicate(base[0], color=GREEN_M)))
        self.remove(notes)
        dnotes = VGroup(sticky("namespace: hello-dev", BLUE_M), sticky("replicas: 1", BLUE_M), sticky("image: hello-devops:1.1.0", BLUE_M), sticky("GREETING: Hello from dev!", BLUE_M))
        for n, y in zip(dnotes, (1.35, 0.55, -0.25, -1.05)):
            n.move_to([2.9, y, 0])
        self.beat("Lay down the dev notes instead. Namespace hello-dev, one replica, a newer image, 1.1.0, and hello from dev.",
                  Transform(ovl, T("overlays/dev", 26, BLUE_M).move_to(ovl)), Transform(cmdk, M("kubectl kustomize overlays/dev", 24, GREY_B).move_to(cmdk)),
                  LaggedStart(*[FadeIn(n, shift=LEFT * 0.2) for n in dnotes], lag_ratio=0.3), run_time=3.0)
        self.beat("One base, two small overlays, running side by side. The tool is built into kubectl, and it's called Kustomize.",
                  Transform(h2, T("Kustomize: patching", 30, GREEN_M).move_to(h2)), run_time=2.0)
        # where the overlay must not live
        cyc = VGroup(M("k8s/overlays/prod  ->  ../../", 24, RED_M), M("error: ... cycle detected", 24, RED_M)).arrange(DOWN, buff=0.15).move_to([0, -3.0, 0])
        self.beat("One trap: put an overlay inside its own base folder, and Kustomize refuses. Cycle detected. Overlays sit next to k8s, never inside it.",
                  FadeOut(cmdk), FadeIn(cyc), run_time=2.0)
        self.play(FadeOut(VGroup(base, dnotes, ovl, cyc, h2)), run_time=0.6)

        # ---------- 6. both roads end in plain YAML
        hb = box("Helm: fill blanks", BLUE_M, w=4.0, size=28).move_to([-3.6, 2.2, 0])
        kb = box("Kustomize: patch a base", GREEN_M, w=4.4, size=28).move_to([3.6, 2.2, 0])
        py = box("plain YAML", WHITE, w=3.2, size=28).move_to([0, 0.0, 0])
        api = box("API server", GREY_B, w=3.2, size=28).move_to([0, -2.2, 0])
        ar = VGroup(edge_arrow(hb, py), edge_arrow(kb, py), edge_arrow(py, api))
        self.beat("Two roads, one destination. Either way, the result is ordinary Kubernetes YAML, and the API server never knows which tool made it.",
                  FadeIn(hb), FadeIn(kb), Succession(Wait(1.2), AnimationGroup(GrowArrow(ar[0]), GrowArrow(ar[1]), FadeIn(py))),
                  Succession(Wait(2.6), AnimationGroup(GrowArrow(ar[2]), FadeIn(api))), run_time=4.4)

        # ---------- 7. guardrails: which one, and when each goes too far
        self.play(VGroup(hb, kb, py, api, ar).animate.scale(0.7).move_to([0, 2.2, 0]), run_time=0.8)
        rows = VGroup(
            VGroup(T("someone else's software", 26), M("Helm", 26, BLUE_M)),
            VGroup(T("your app, a few differences", 26), M("either; Kustomize stays plain", 26, GREEN_M)),
            VGroup(T("your app, many teams, many settings", 26), M("Helm", 26, BLUE_M)))
        for i, r in enumerate(rows):
            y = 0.2 - 0.75 * i
            r[0].move_to([-5.9, y, 0], aligned_edge=LEFT); r[1].move_to([1.0, y, 0], aligned_edge=LEFT)
        self.beat("So which one? Mostly, whose software is it? Someone else's, like Envoy Gateway, ships as a Helm chart.",
                  FadeIn(rows[0]), run_time=1.6)
        self.beat("Your own app, a few differences? Either works, and Kustomize stays plain YAML.",
                  FadeIn(rows[1]), run_time=1.6)
        self.beat("Many teams, many settings? Helm's values give each team one clear place.",
                  FadeIn(rows[2]), run_time=1.6)
        lims = VGroup(T("values.yaml repeats the whole Deployment: gone too far", 24, RED_M),
                      T("an overlay changes half the base: fix the base", 24, RED_M)).arrange(DOWN, buff=0.25).move_to([0, -2.75, 0])
        self.beat("And each has a limit. A values file that repeats the whole Deployment has gone too far. An overlay that changes half the base means the base is wrong.",
                  FadeIn(lims[0]), Succession(Wait(3.0), FadeIn(lims[1])), run_time=4.4)
        self.play(FadeOut(VGroup(hb, kb, py, api, ar, rows, lims)), run_time=0.6)

        # ---------- 8. moral and a quick check
        mor = VGroup(T("Photocopies drift. Write it once, say only what differs.", 30),
                     T("Helm: a recipe card with blanks, and a logbook in pen", 28, BLUE_M),
                     T("pass your values file on every upgrade", 28, YELLOW_M),
                     T("Kustomize: a master recipe with sticky notes", 28, GREEN_M),
                     T("the cluster only ever sees plain YAML", 28, GREY_B)).arrange(DOWN, buff=0.35)
        self.beat("The moral of the story: photocopies drift. Write it once, say only what differs. Helm is a recipe card with blanks and a logbook in pen; pass your values on every upgrade. Kustomize is a master recipe with sticky notes. The cluster only sees plain YAML.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mor], lag_ratio=0.8), run_time=8.0)
        self.play(FadeOut(mor), run_time=0.6)
        q = VGroup(T("Prod needs a bigger memory limit on the web container.", 30), T("Nothing else changes.", 30),
                   T("What do you add to the prod overlay?", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 0.8, 0])
        self.beat("One quick check. Prod needs a bigger memory limit on the base Deployment's web container, and nothing else changes. What do you add to the prod overlay? Pause and think.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in q], lag_ratio=0.5), run_time=4.0)
        self.wait(2.0)
        ans = chip("a patch with only that container's resources", GREEN_M, 28).move_to([0, -1.5, 0])
        self.beat("A small patch naming the Deployment and the web container, with only the changed fields. A sticky note, not a photocopy. Thanks for watching.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.0)
