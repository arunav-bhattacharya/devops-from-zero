import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bKustomize\b", "customize"), (r"\bkind-values\.yaml\b", "kind values dot yammel"), (r"\bvalues\.yaml\b", "values dot yammel"),
            (r"\bpdb\.yaml\b", "P D B dot yammel"), (r"--set\b", "dash dash set"), (r"\bClusterIP\b", "cluster I P"),
            (r"\bNodePort\b", "node port"), (r"\bPodDisruptionBudget\b", "pod disruption budget"), (r"\breplicaCount\b", "replica count"),
            (r"\b-f\b", "dash F"), (r"\bhello-prod\b", "hello prod"), (r"\bhello-dev\b", "hello dev"), (r"\bk8s/", "K eights")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def card(lines, color, title=None, size=20, w=None, pad=0.35):
    g = VGroup(*[M(t, size, c) for t, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    r = RoundedRectangle(corner_radius=0.12, width=w or g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=3)
    r.set_fill(tint(color, 0.1), 1)
    g.move_to(r).align_to(r, LEFT).shift(RIGHT * pad)
    out = VGroup(r, g)
    if title:
        out.add(T(title, 22, color).next_to(r, UP, buff=0.15).align_to(r, LEFT))
    return out


def folder(name, color=GREY_B, w=2.2, h=1.5):
    body = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.12), 1)
    tab = RoundedRectangle(corner_radius=0.06, width=w * 0.4, height=0.24, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.12), 1)
    tab.next_to(body, UP, buff=-0.04).align_to(body, LEFT)
    lab = M(name, 22).move_to(body).shift(UP * 0.3)
    return VGroup(tab, body, lab)


class D45Packaging(VoiceScene):
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
        self.title_card("Packaging with Helm and Kustomize", "fill in blanks, or patch a base")

        # ---- 0. the problem: three copies drift apart
        src = folder("k8s/", WHITE, w=2.6, h=1.7).move_to([0, 1.9, 0])
        files = VGroup(*[Rectangle(width=0.3, height=0.38, stroke_color=GREY_B, stroke_width=1.5).set_fill(BLACK, 1) for _ in range(10)])
        files.arrange(RIGHT, buff=0.06).scale(0.62).move_to(src[1]).shift(DOWN * 0.3)
        n = T("more than ten YAML files", 22, GREY_B).next_to(src, RIGHT, buff=0.4)
        self.beat("hello-devops now has more than ten YAML files. Now run it for dev, staging and prod.",
                  FadeIn(src), LaggedStart(*[FadeIn(f) for f in files], lag_ratio=0.08), FadeIn(n), run_time=2.2)
        envs = [("dev", BLUE_M), ("staging", TEAL_M), ("prod", GOLD_M)]
        cps = VGroup(*[folder(e, c, w=2.6, h=1.7).move_to([x, -1.2, 0]) for (e, c), x in zip(envs, (-4.3, 0, 4.3))])
        diffs = VGroup(*[VGroup(*[M(t, 20, c) for t in ln]).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(f[1]).shift(DOWN * 0.25)
                         for f, ln, (_, c) in zip(cps, (("tag 1.1.0", "replicas 1"), ("tag 1.0.0", "replicas 2"), ("tag 1.0.0", "replicas 4")), envs)])
        cl = VGroup(*[link(src, f, GREY_B) for f in cps])
        self.beat("The easy way is to copy the folder three times. Each copy gets its own image tag, replica count and greeting.",
                  LaggedStart(*[TransformFromCopy(src, f) for f in cps], lag_ratio=0.3), Create(cl), Succession(Wait(1.6), FadeIn(diffs)), run_time=3.0)
        pdb = M("+ disruption budget", 20, GOLD_M).next_to(cps[2], DOWN, buff=0.2)
        self.beat("Prod also wants a disruption budget.", FadeIn(pdb, shift=UP * 0.1), run_time=1.0)
        fix = M("probe fixed", 20, GREEN_M).next_to(pdb, DOWN, buff=0.12)
        old = M("old probe", 20, RED_M).next_to(cps[0], DOWN, buff=0.2)
        self.steps("Then the copies drift apart. Someone fixes a probe in prod, and forgets dev.",
                   (1.6, Wait(1.6)), (0.8, FadeIn(fix, shift=UP * 0.1)), (1.2, Wait(1.2)), (0.8, FadeIn(old, shift=UP * 0.1)))
        q = T("which differences are on purpose?", 30, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("Six months later, nobody knows which differences are on purpose.",
                  FadeIn(q, shift=UP * 0.15), *[Wiggle(f) for f in cps], run_time=2.0)
        self.play(FadeOut(VGroup(src, files, n, cps, diffs, cl, pdb, fix, old, q)), run_time=0.7)

        # ---- 1. two roads to the same place
        helm = box("Helm: fill in blanks", BLUE_M, w=4.0, h=0.95, size=28).move_to([-4.1, 1.7, 0])
        kus = box("Kustomize: patch a base", TEAL_M, w=4.0, h=0.95, size=28).move_to([-4.1, -1.7, 0])
        yml = box("plain Kubernetes YAML", WHITE, w=3.6, h=0.95, size=28).move_to([1.15, 0, 0])
        api = box("API server", GREY_B, w=2.2, h=0.95, size=28).move_to([5.25, 0, 0])
        r1, r2, r3 = edge_arrow(helm, yml), edge_arrow(kus, yml), edge_arrow(yml, api)
        self.beat("There are two popular answers, and they come from opposite directions.",
                  FadeIn(helm, shift=RIGHT * 0.2), FadeIn(kus, shift=RIGHT * 0.2), run_time=1.6)
        self.beat("Helm is templating. Write the YAML once, with blanks, and fill the blanks for each environment.",
                  Indicate(helm, color=BLUE_M, scale_factor=1.05), run_time=1.6)
        self.beat("Kustomize is patching. Keep plain, valid YAML as a base, and describe each environment as a small set of changes on top.",
                  Indicate(kus, color=TEAL_M, scale_factor=1.05), run_time=1.6)
        self.steps("Either way, the result is ordinary Kubernetes YAML. The API server never knows which tool made it.",
                   (1.6, GrowArrow(r1), GrowArrow(r2), FadeIn(yml)), (0.8, travel(r1, BLUE_M, 0.8), travel(r2, TEAL_M, 0.8)),
                   (1.0, GrowArrow(r3), FadeIn(api)), (0.8, travel(r3, YELLOW_M, 0.8)))
        roads = VGroup(helm, kus, yml, api, r1, r2, r3)
        self.play(FadeOut(roads), run_time=0.6)

        # ---- 2. Helm: a template with blanks
        hd = T("Helm", 30, BLUE_M).move_to([-5.9, 3.3, 0])
        tpl = card([("replicas: {{ .Values.replicaCount }}", WHITE), ("GREETING: {{ .Values.greeting | quote }}", WHITE)], BLUE_M, "templates/")
        tpl.move_to([-3.45, 1.85, 0])
        self.beat("Start with Helm. A package is called a chart. Its templates are YAML with placeholders.",
                  FadeIn(hd), Create(tpl[0]), FadeIn(tpl[2]), LaggedStart(*[Write(l) for l in tpl[1]], lag_ratio=0.4), run_time=2.4)
        bl = VGroup(SurroundingRectangle(tpl[1][0][9:], color=YELLOW_M, buff=0.05, corner_radius=0.05),
                    SurroundingRectangle(tpl[1][1][9:], color=YELLOW_M, buff=0.05, corner_radius=0.05))
        self.beat("Each placeholder is a blank. This one reads replicaCount from the values. This one reads the greeting, and wraps it in quotes.",
                  Succession(Create(bl[0]), Wait(1.4), Create(bl[1])), run_time=3.2)

        # values layers: a table
        CX = [-3.0, 0.1, 3.0]  # layer name, replicaCount, greeting columns
        RY = {"head": -0.55, "set": -1.15, "f": -1.75, "def": -2.35, "res": -3.2}

        def cell(t, col, row, color=WHITE, size=20):
            return M(t, size, color).move_to([CX[col], RY[row], 0])

        head = VGroup(T("layer", 22, GREY_B).move_to([CX[0], RY["head"], 0]), cell("replicaCount", 1, "head", GREY_B), cell("greeting", 2, "head", GREY_B))
        hline = Line([-4.7, RY["head"] - 0.3, 0], [4.85, RY["head"] - 0.3, 0], stroke_width=1.5, color=GREY_D)
        r_def = VGroup(cell("values.yaml", 0, "def", BLUE_M), cell("2", 1, "def"), cell('"Hello from Helm!"', 2, "def"))
        self.beat("The chart's values.yaml holds the default settings. Two replicas. Hello from Helm.",
                  FadeIn(head), Create(hline), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in r_def], lag_ratio=0.3), run_time=2.4)
        r_f = VGroup(cell("-f kind-values.yaml", 0, "f", TEAL_M), cell('"Hello from Helm on kind!"', 2, "f"))
        self.beat("Your own values file goes on top, with -f. The lab's kind-values.yaml changes only the greeting.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in r_f], lag_ratio=0.3), run_time=1.8)
        up = Arrow([5.35, RY["def"] - 0.2, 0], [5.35, RY["set"] + 0.2, 0], buff=0, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.15)
        upl = T("later wins", 22, YELLOW_M).next_to(up, UP, buff=0.12)
        self.beat("Layers stack in order. When two layers set the same key, the later one wins.",
                  GrowArrow(up), FadeIn(upl), r_def[2].animate.set_opacity(0.3), run_time=1.6)
        rline = Line([-4.7, RY["res"] + 0.38, 0], [4.85, RY["res"] + 0.38, 0], stroke_width=1.5, color=GREY_D)
        res = VGroup(T("result", 22, YELLOW_M).move_to([CX[0], RY["res"], 0]), cell("2", 1, "res", YELLOW_M), cell('"Hello from Helm on kind!"', 2, "res", YELLOW_M))
        self.beat("So the result is two replicas, and Hello from Helm on kind.",
                  Create(rline), FadeIn(res[0]), TransformFromCopy(r_def[1], res[1]), TransformFromCopy(r_f[1], res[2]), run_time=2.0)

        # render
        outc = card([("replicas: 2", WHITE), ('GREETING: "Hello from Helm on kind!"', WHITE)], WHITE, "rendered YAML")
        outc.move_to([3.65, 1.85, 0])
        ra = Arrow(tpl[0].get_right(), outc[0].get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        cmd = M("helm template hello chart/hello-devops", 20, GREY_B).move_to([0, 3.35, 0])
        self.steps("helm template fills every blank and prints the final YAML, without touching the cluster. Render before you install.",
                   (1.0, FadeIn(cmd)), (1.0, GrowArrow(ra)),
                   (1.6, Create(outc[0]), FadeIn(outc[2]), TransformFromCopy(res[1], outc[1][0]), TransformFromCopy(res[2], outc[1][1])))
        rev = chip("revision 1", BLUE_M, 22).move_to([3.55, 3.35, 0]).align_to(outc[0], RIGHT)
        self.beat("helm install applies it, and records revision 1 of a release named hello.",
                  FadeOut(cmd), FadeIn(rev, shift=DOWN * 0.1), run_time=1.6)

        # the upgrade surprise
        r_set = VGroup(cell("--set replicaCount=4", 0, "set", GOLD_M), cell("4", 1, "set"))
        self.beat("Later you run helm upgrade, with just one new setting. Set replicaCount to four.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in r_set], lag_ratio=0.3), r_def[1].animate.set_opacity(0.3), run_time=1.8)
        self.steps("Here is the surprise. When you pass any values on an upgrade, Helm starts from the chart's defaults plus only the values you pass now. The file you gave at install time is dropped.",
                   (2.0, Wait(2.0)), (1.6, Wait(1.6)), (1.4, r_f.animate.set_opacity(0.15), r_def[2].animate.set_opacity(1)),
                   (1.4, Transform(res[1], cell("4", 1, "res", YELLOW_M)), Transform(res[2], cell('"Hello from Helm!"', 2, "res", RED_M))))
        rev2 = chip("revision 2", BLUE_M, 22).move_to(rev)
        out2 = VGroup(M("replicas: 4", 20), M('GREETING: "Hello from Helm!"', 20, RED_M))
        for a, b in zip(out2, outc[1]):
            a.move_to(b, aligned_edge=LEFT)
        self.beat("Revision 2 has four replicas, and the old greeting is back. That surprises nearly everyone the first time.",
                  Transform(rev, rev2), Transform(outc[1][0], out2[0]), Transform(outc[1][1], out2[1]), run_time=1.8)
        fixit = T("keep settings in a values file, pass it with -f every time", 24, GREEN_M).move_to([0, 0.15, 0])
        self.beat("So keep your settings in a values file, and pass it with -f every time.",
                  FadeIn(fixit, shift=UP * 0.1), r_f.animate.set_opacity(1), run_time=1.6)
        helm_all = VGroup(hd, tpl, bl, head, hline, r_def, r_f, r_set, up, upl, rline, res, outc, ra, rev, fixit)
        self.play(FadeOut(helm_all), run_time=0.7)

        # ---- 3. Kustomize: a base and tracing-paper overlays
        kd = T("Kustomize", 30, TEAL_M).move_to([-5.45, 3.3, 0])
        rows = [("namespace: ", "hello"), ("replicas: ", "3"), ("image: hello-devops:", "1.0.0"), ("type: ", "NodePort")]
        full = VGroup(*[M(k + v, 22) for k, v in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        NK = [len(k.replace(" ", "")) for k, _ in rows]
        keys = VGroup(*[f[:n] for f, n in zip(full, NK)])
        vals = VGroup(*[f[n:] for f, n in zip(full, NK)])
        body = full

        def newvals(texts, color):
            out = []
            for f, (k, _), t, n in zip(full, rows, texts, NK):
                m = M(k + t, 22).move_to(f, aligned_edge=LEFT)
                out.append(m[n:].set_color(color))
            return out
        base_r = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.1, stroke_color=WHITE, stroke_width=3).set_fill(BLACK, 1)
        base_r.move_to([-3.2, 0.4, 0])
        body.move_to(base_r).align_to(base_r, LEFT).shift(RIGHT * 0.4 + UP * 0.25)
        bt = M("k8s/  (the base)", 22, WHITE).next_to(base_r, UP, buff=0.15).align_to(base_r, LEFT)
        self.beat("Now Kustomize. It is built into kubectl. The base is your plain k8s folder, the files you already apply.",
                  FadeIn(kd), Create(base_r), FadeIn(bt), LaggedStart(*[FadeIn(VGroup(k, v)) for k, v in zip(keys, vals)], lag_ratio=0.2), run_time=2.4)
        okv = T("plain, valid YAML", 22, GREY_B).next_to(base_r, DOWN, buff=0.2).align_to(base_r, LEFT)
        self.beat("Every file stays as it is, and you can still read and apply it.",
                  FadeIn(okv), run_time=1.2)

        def sheet(name, color):
            s = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.1, stroke_color=color, stroke_width=3).set_fill(color, 0.1)
            lab = M(name, 22, color).next_to(s, DOWN, buff=0.15).align_to(s, RIGHT)
            return VGroup(s, lab)

        prod = sheet("overlays/prod", GOLD_M).move_to(base_r.get_center() + DOWN * 4.8)
        prod[1].next_to(prod[0], DOWN, buff=0.15).align_to(prod[0], RIGHT)
        self.beat("An overlay is another folder, with its own kustomization file. It points at the base and lists changes. Think of a sheet of tracing paper laid on top.",
                  FadeOut(okv), prod.animate.move_to(base_r.get_center() + DOWN * 0.13), run_time=2.6)
        pv = ["hello-prod", "4", "1.0.0", "ClusterIP"]
        nv = newvals(pv, GOLD_M)
        self.steps("The prod overlay moves every object into the namespace hello-prod. It sets four replicas. It switches the Service to ClusterIP.",
                   (1.6, Transform(vals[0], nv[0])), (1.2, Transform(vals[1], nv[1])), (1.4, Wait(1.4)), (1.0, Transform(vals[3], nv[3])))
        pdb = M("+ PodDisruptionBudget", 22, GOLD_M).next_to(keys, DOWN, buff=0.32).align_to(keys, LEFT)
        self.beat("And it adds one file that only prod has, a PodDisruptionBudget.",
                  FadeIn(pdb, shift=UP * 0.1), run_time=1.4)
        outk = card([("namespace: hello-prod", WHITE), ("replicas: 4", WHITE), ("image: hello-devops:1.0.0", WHITE), ("type: ClusterIP", WHITE),
                     ("kind: PodDisruptionBudget", WHITE)], WHITE, "rendered YAML", size=20).move_to([3.6, 0.3, 0])
        ka = Arrow(base_r.get_right() + RIGHT * 0.05, outk[0].get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        kc = M("kubectl kustomize overlays/prod", 20, GREY_B).move_to([2.0, 3.3, 0])
        self.steps("kubectl kustomize prints the result. Plain YAML again.",
                   (0.8, FadeIn(kc)), (0.8, GrowArrow(ka)), (1.4, Create(outk[0]), FadeIn(outk[2]), LaggedStart(*[FadeIn(l) for l in outk[1]], lag_ratio=0.15)))

        # lift the sheet: the base is untouched
        bv = newvals([v for _, v in rows], WHITE)
        self.steps("Lift the sheet off, and the base is untouched. Nothing in k8s changed.",
                   (1.4, prod.animate.shift(DOWN * 4.8), FadeOut(pdb), *[Transform(vals[i], bv[i]) for i in range(4)], FadeOut(outk), FadeOut(ka), FadeOut(kc)))
        self.remove(prod)
        dev = sheet("overlays/dev", BLUE_M).move_to(base_r.get_center() + DOWN * 4.8)
        dev[1].next_to(dev[0], DOWN, buff=0.15).align_to(dev[0], RIGHT)
        dvv = ["hello-dev", "1", "1.1.0", "ClusterIP"]
        dnv = newvals(dvv, BLUE_M)
        self.steps("Lay down the dev sheet instead. Namespace hello-dev, one replica, and a newer image, 1.1.0.",
                   (1.4, dev.animate.move_to(base_r.get_center() + DOWN * 0.13)),
                   (2.4, LaggedStart(*[Transform(vals[i], dnv[i]) for i in range(4)], lag_ratio=0.3)))
        side = VGroup(chip("hello", WHITE, 22, mono=True), chip("hello-dev", BLUE_M, 22, mono=True), chip("hello-prod", GOLD_M, 22, mono=True)).arrange(DOWN, buff=0.3)
        side.move_to([3.6, 0.4, 0])
        sl = T("namespaces in one cluster", 22, GREY_B).next_to(side, UP, buff=0.3)
        self.beat("One base, two small overlays. Applied, they run side by side, each in its own namespace.",
                  FadeIn(sl), LaggedStart(*[FadeIn(c, shift=LEFT * 0.15) for c in side], lag_ratio=0.3), run_time=2.4)
        kus_all = VGroup(kd, base_r, bt, keys, vals, dev, side, sl)
        self.play(FadeOut(kus_all), run_time=0.7)

        # ---- 4. which road, and recap
        roads.move_to(ORIGIN + UP * 0.6)
        self.add(roads)
        self.play(FadeIn(roads), run_time=0.8)
        a = T("someone else's software: Helm", 26, BLUE_M)
        b = T("your own app, a few differences: either, often Kustomize", 26, TEAL_M)
        ab = VGroup(a, b).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([0, -2.75, 0])
        self.beat("Which one? Most third-party software ships as Helm charts. For your own app with a few differences per environment, either works, and Kustomize keeps every file as plain YAML.",
                  FadeIn(a, shift=UP * 0.1), Succession(Wait(2.6), FadeIn(b, shift=UP * 0.1)), run_time=4.4)
        self.beat("Helm fills in blanks. Kustomize patches a base. The cluster only ever sees plain YAML.",
                  Indicate(helm, color=BLUE_M, scale_factor=1.05), Succession(Wait(1.0), Indicate(kus, color=TEAL_M, scale_factor=1.05)),
                  Succession(Wait(2.2), Indicate(yml, color=YELLOW_M, scale_factor=1.05)), run_time=3.6)
        self.wait(1.0)
