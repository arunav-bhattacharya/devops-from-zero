import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bConfigMaps\b", "config maps"), (r"\bConfigMap\b", "config map"), (r"\bconfigMapKeyRef\b", "config map key ref"),
            (r"\bconfigMapRef\b", "config map ref"), (r"\bconfigMapGenerator\b", "config map generator"),
            (r"\benvFrom\b", "E N V from"), (r"\benv vars\b", "environment variables"), (r"\benv var\b", "environment variable"),
            (r"\benv\b", "E N V"), (r"\bbase64\b", "base sixty-four"), (r"\btmpfs\b", "temp F S"), (r"\bsubPath\b", "sub path"),
            (r"\.\.data\b", "dot dot data"), (r"\bSOPS\b", "sops"), (r"\bREDIS_HOST\b", "redis host"), (r"\bGREETING\b", "greeting"),
            (r"\bCOLOR\b", "color"), (r"\bdemo-config\b", "demo config"), (r"\bhello-config\b", "hello config")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def card(lines, color, size=22, pad=0.45):
    """A YAML card: monospace lines in a rounded frame. lines = [(text, colour, indent)]."""
    g = VGroup(*[M(t, size, c) for t, c, _ in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    for m, (_, _, ind) in zip(g, lines):
        m.shift(RIGHT * 0.3 * ind)
    r = RoundedRectangle(corner_radius=0.15, width=g.width + 2 * pad, height=g.height + 2 * pad * 0.8, stroke_color=color, stroke_width=3)
    r.set_fill(tint(color, 0.1), opacity=1)
    g.move_to(r)
    return VGroup(r, g)


def pod(color=TEAL_M, r=0.3):
    return Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.28), opacity=1)


class D42Config(VoiceScene):
    def steps(self, text, *plays):
        """Speak one line while playing several animations one after another: plays = [(run_time, anim, ...)]."""
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
        self.title_card("Config outside the image", "ConfigMaps and Secrets, and how they reach a Pod")

        # 1. one image, many places
        img = mbox("hello-devops:1.0.0", BLUE_M, size=24, h=0.75).move_to(UP * 2.3)
        envs = VGroup(*[box(n, GREY_B, w=2.7, h=0.75, size=26) for n in ("laptop", "staging", "production")])
        for e, x in zip(envs, (-4.4, 0, 4.4)):
            e.move_to([x, -0.2, 0])
        arrs = VGroup(*[edge_arrow(img, e) for e in envs])
        sets = VGroup(*[chip(t, c, 22, mono=True) for t, c in (("LOG_LEVEL=debug", TEAL_M), ("LOG_LEVEL=info", GOLD_M), ("LOG_LEVEL=warn", PURPLE_M))])
        for s, e in zip(sets, envs):
            s.next_to(e, DOWN, buff=0.45)
        self.steps("Since Part 5, you have built one image, and changed how it behaves with environment variables. The same image runs on your laptop, in staging and in production.",
                   (1.2, Create(img[0]), Write(img[1])), (2.4, Wait(2.4)),
                   (2.0, LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(e)) for a, e in zip(arrs, envs)], lag_ratio=0.25)),
                   (1.1, LaggedStart(*[travel(a, BLUE_M, 0.7) for a in arrs], lag_ratio=0.15)))
        self.beat("Only the settings differ.",
                  LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in sets], lag_ratio=0.25), run_time=1.4)
        rule = T("store config in the environment", 30, YELLOW_M).to_edge(DOWN, buff=0.7)
        self.beat("That is the twelve-factor rule. Store config in the environment.", Write(rule), run_time=1.6)
        self.play(FadeOut(VGroup(img, envs, arrs, sets, rule)), run_time=0.6)

        # 2. the ConfigMap object, next to the Deployment that names it
        cm = card([("kind: ConfigMap", GREY_B, 0), ("name: hello-config", WHITE, 0), ("data:", WHITE, 0),
                   ('GREETING: "Hello from Kubernetes!"', YELLOW_M, 1), ('REDIS_HOST: "redis"', YELLOW_M, 1)], YELLOW_M)
        cm.move_to([-3.3, 0.3, 0])
        dep = card([("kind: Deployment", GREY_B, 0), ("name: hello-devops", WHITE, 0), ("envFrom:", BLUE_M, 0),
                    ("- configMapRef:", BLUE_M, 1), ("name: hello-config", BLUE_M, 3)], BLUE_M)
        dep.move_to([3.6, 0.3, 0])
        self.beat("In Kubernetes, most teams put those settings in a ConfigMap. It is a small object, with a data section of keys and string values.",
                  Create(cm[0]), LaggedStart(*[Write(l) for l in cm[1]], lag_ratio=0.2), run_time=2.6)
        yl = dep[1][4].get_center()[1]
        ln = DashedLine([dep[0].get_left()[0] - 0.05, yl, 0], [cm[0].get_right()[0] + 0.05, yl, 0], dash_length=0.08, stroke_width=2, color=BLUE_M)
        where = chip("staging", GOLD_M, 24).next_to(cm, UP, buff=0.3)
        same = T("same in every environment", 24, BLUE_M).next_to(dep, UP, buff=0.35)
        self.steps("The Deployment only names it. So the Deployment stays the same in every environment, and only the ConfigMap differs.",
                   (1.6, Create(dep[0]), LaggedStart(*[Write(l) for l in dep[1]], lag_ratio=0.15)), (0.8, Create(ln), Indicate(dep[1][4], color=BLUE_M)),
                   (0.9, FadeIn(where), FadeIn(same)), (1.0, Transform(where, chip("production", PURPLE_M, 24).move_to(where)), Indicate(cm[1][3], color=YELLOW_M)))
        lim1 = chip("at most 1 MiB", GREY_B, 24).next_to(cm, DOWN, buff=0.4).shift(LEFT * 1.4)
        lim2 = chip("not secret", RED_M, 24).next_to(lim1, RIGHT, buff=0.4)
        self.beat("It holds at most one mebibyte. And it is not secret at all: anyone who can read objects in the namespace can read it.",
                  FadeIn(lim1, shift=UP * 0.15), Succession(Wait(1.4), FadeIn(lim2, shift=UP * 0.15)), run_time=2.4)
        self.play(FadeOut(VGroup(cm, dep, ln, where, same, lim1, lim2)), run_time=0.6)

        # 3. three ways into a container
        cm2 = card([("hello-config", GREY_B, 0), ("GREETING", YELLOW_M, 0), ("REDIS_HOST", YELLOW_M, 0)], YELLOW_M, size=24)
        cm2.move_to([-5.15, 0.2, 0])
        ctr = RoundedRectangle(corner_radius=0.18, width=4.6, height=5.6, stroke_color=TEAL_M, stroke_width=3).move_to([4.35, 0.0, 0])
        ctr.set_fill(tint(TEAL_M, 0.08), opacity=1)
        ctl = T("container", 24, TEAL_M).next_to(ctr, UP, buff=0.12)
        ways = VGroup(
            VGroup(M("env", 24, BLUE_M), M("configMapKeyRef", 20, GREY_B)).arrange(DOWN, buff=0.12),
            VGroup(M("envFrom", 24, BLUE_M), M("configMapRef", 20, GREY_B)).arrange(DOWN, buff=0.12),
            VGroup(M("volume", 24, GREEN_M), M("mountPath", 20, GREY_B)).arrange(DOWN, buff=0.12),
        )
        ys = (1.75, 0.0, -1.75)
        for w, y in zip(ways, ys):
            w.move_to([-0.6, y, 0])
        a_in = VGroup(*[Arrow(cm2[0].get_right(), w.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1) for w in ways])
        res = [
            VGroup(M("HELLO_TEXT=Hello...", 22, BLUE_M), T("one key, a new name", 20, GREY_B)).arrange(DOWN, buff=0.1, aligned_edge=LEFT),
            VGroup(M("GREETING=Hello from...", 22, BLUE_M), M("REDIS_HOST=redis", 22, BLUE_M)).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
            VGroup(M("/config/", 22, GREEN_M), M("GREETING", 22, GREEN_M), M("REDIS_HOST", 22, GREEN_M)).arrange(DOWN, buff=0.1, aligned_edge=LEFT),
        ]
        res[2][1].shift(RIGHT * 0.35); res[2][2].shift(RIGHT * 0.35)
        for r, y in zip(res, ys):
            r.move_to([4.35, y, 0])
        a_out = VGroup(*[Arrow(w.get_right(), [ctr.get_left()[0], w.get_center()[1], 0], buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12) for w in ways])
        self.beat("A Pod can use a ConfigMap in three ways, and you can mix them.",
                  Create(cm2[0]), FadeIn(cm2[1]), Create(ctr), FadeIn(ctl), run_time=1.8)
        self.beat("With env and configMapKeyRef, one key becomes one environment variable. You can rename it on the way.",
                  GrowArrow(a_in[0]), FadeIn(ways[0]), GrowArrow(a_out[0]), FadeIn(res[0], shift=RIGHT * 0.15), Indicate(cm2[1][1], color=YELLOW_M), run_time=2.4)
        self.beat("With envFrom and configMapRef, every key becomes an environment variable with the same name.",
                  GrowArrow(a_in[1]), FadeIn(ways[1]), GrowArrow(a_out[1]), FadeIn(res[1], shift=RIGHT * 0.15), run_time=2.2)
        lab = chip("the lab uses this", YELLOW_M, 20).next_to(ways[1], DOWN, buff=0.18)
        self.beat("The lab uses this, so GREETING and REDIS_HOST arrive as env vars.",
                  FadeIn(lab), Indicate(res[1], color=BLUE_M, scale_factor=1.05), run_time=1.6)
        self.beat("Or mount it as a volume. Every key becomes a file, in a folder you choose.",
                  GrowArrow(a_in[2]), FadeIn(ways[2]), GrowArrow(a_out[2]), FadeIn(res[2], shift=RIGHT * 0.15), run_time=2.2)
        self.beat("Env vars suit short values your code reads at start. Files suit whole config files, and anything your code may read again later.",
                  Indicate(res[1], color=BLUE_M, scale_factor=1.05), Succession(Wait(1.2), Indicate(res[2], color=GREEN_M, scale_factor=1.05)), run_time=3.0)
        self.play(FadeOut(VGroup(cm2, ctr, ctl, ways, a_in, a_out, *res, lab)), run_time=0.6)

        # 4. change a ConfigMap: what a running Pod sees
        dcm = card([("demo-config", GREY_B, 0), ("COLOR: blue", BLUE_M, 0)], YELLOW_M, size=26)
        dcm.move_to([-5.0, 1.3, 0])
        kub = box("kubelet", GREY_B, w=2.0, h=0.7, size=24).move_to([-0.9, 1.3, 0])
        pr = RoundedRectangle(corner_radius=0.18, width=4.4, height=3.0, stroke_color=TEAL_M, stroke_width=3).move_to([4.3, 1.3, 0])
        pr.set_fill(tint(TEAL_M, 0.08), opacity=1)
        prl = M("Pod config-demo", 22, TEAL_M).next_to(pr, UP, buff=0.12)
        ev = VGroup(T("env var", 22, GREY_B), M("COLOR=blue", 26, BLUE_M)).arrange(DOWN, buff=0.1).move_to([4.3, 2.1, 0])
        fv = VGroup(T("file /config/COLOR", 22, GREY_B), M("blue", 26, BLUE_M)).arrange(DOWN, buff=0.1).move_to([4.3, 0.5, 0])
        self.beat("The lesson's demo makes this visible. A ConfigMap, demo-config, holds COLOR: blue.",
                  Create(dcm[0]), FadeIn(dcm[1]), run_time=1.6)
        self.beat("A Pod reads that one value twice: as an env var, and as a file.",
                  Create(pr), FadeIn(prl), FadeIn(ev, shift=LEFT * 0.15), FadeIn(fv, shift=LEFT * 0.15), run_time=1.8)
        logbox = RoundedRectangle(corner_radius=0.12, width=6.6, height=2.0, stroke_color=GREY_D, stroke_width=2).move_to([2.5, -2.45, 0])
        logt = M("$ kubectl logs config-demo", 22, GREY_B).move_to(logbox.get_corner(UL) + [0.25, -0.3, 0], aligned_edge=UL)

        def logline(env, file):
            return M(f"env={env} file={file}", 22, t2c={"blue": BLUE_M, "green": GREEN_M})

        lines = VGroup(logline("blue", "blue"), logline("blue", "blue")).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        lines.next_to(logt, DOWN, buff=0.18, aligned_edge=LEFT)
        self.beat("Every five seconds, it prints both. env equals blue, file equals blue.",
                  Create(logbox), FadeIn(logt), LaggedStart(*[FadeIn(l) for l in lines], lag_ratio=0.5), run_time=2.0)

        def tick_log(env, file):
            new = logline(env, file).move_to(lines[1].get_left(), aligned_edge=LEFT)
            anim = AnimationGroup(FadeOut(lines[0], shift=UP * 0.2), lines[1].animate.move_to(lines[0].get_left(), aligned_edge=LEFT),
                                  FadeIn(new, shift=UP * 0.2))
            return anim, VGroup(lines[1], new)

        new_val = M("COLOR: green", 26, GREEN_M).move_to(dcm[1][1], aligned_edge=LEFT)
        self.beat("Now change the value in the ConfigMap to green.", Transform(dcm[1][1], new_val), run_time=1.2)
        anim, lines = tick_log("blue", "blue")
        self.beat("A ConfigMap is only data. No controller acts on it. So changing it never restarts anything.",
                  anim, Indicate(pr, color=TEAL_M, scale_factor=1.02), run_time=1.6)
        a_start = Arrow(kub.get_right() + UP * 0.12, [pr.get_left()[0], ev.get_center()[1], 0], buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.1)
        a_sync = Arrow(kub.get_right() + DOWN * 0.12, [pr.get_left()[0], fv.get_center()[1], 0], buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.1)
        l_start = T("at container start", 20, BLUE_M).move_to(a_start.get_center() + UP * 0.42 + LEFT * 0.25)
        l_sync = T("on each sync", 20, GREEN_M).move_to(a_sync.get_center() + DOWN * 0.42 + LEFT * 0.25)
        a_read = Arrow(dcm[0].get_right(), kub.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12)
        self.beat("The kubelet reads it at two moments. When it starts a container, to fill in env vars.",
                  FadeIn(kub), GrowArrow(a_read), GrowArrow(a_start), FadeIn(l_start), run_time=2.0)
        self.beat("And on its regular sync, to refresh the mounted files.",
                  GrowArrow(a_sync), FadeIn(l_sync), run_time=1.2)
        anim, lines = tick_log("blue", "blue")
        self.play(anim, travel(a_read, GREEN_M, 0.6), run_time=0.8)
        anim, lines = tick_log("blue", "green")
        self.beat("For a while, nothing changes. Then, on the kubelet's next sync, usually within a minute or so, the file shows green.",
                  travel(a_sync, GREEN_M, 0.8), Succession(Wait(0.6), AnimationGroup(Transform(fv[1], M("green", 26, GREEN_M).move_to(fv[1])), anim)), run_time=2.2)
        cross = tick(False, 0.22).next_to(ev[1], RIGHT, buff=0.25)
        self.beat("The env var never changes. It was set once, when the container started.",
                  Create(cross), Indicate(ev[1], color=BLUE_M), run_time=1.4)
        sp = chip("subPath: never updated", RED_M, 22).move_to([-4.3, -1.9, 0])
        rd = chip("the app must read the file again", GOLD_M, 22).move_to([-4.3, -2.9, 0])
        self.beat("A file mounted with subPath is never updated. And even an updated file only helps if your app reads it again. Most apps read config once, at start.",
                  FadeIn(sp, shift=UP * 0.15), Succession(Wait(1.8), FadeIn(rd, shift=UP * 0.15)), run_time=2.8)
        self.play(FadeOut(VGroup(dcm, kub, pr, prl, ev, fv, logbox, logt, lines, a_read, a_start, a_sync, l_start, l_sync, cross, sp, rd)), run_time=0.6)

        # 6. new env vars need new Pods
        cmd = M("$ kubectl rollout restart deployment/hello-devops", 24).move_to(UP * 3.0)
        tpl = card([("template:", WHITE, 0), ("annotations:", GREY_B, 1), ("restartedAt: <now>", GOLD_M, 2)], WHITE, size=22)
        tpl.move_to([-3.9, 0.9, 0])
        self.beat("So hello-devops, which uses env vars, needs new Pods to see a new greeting. The tool for that is kubectl rollout restart.",
                  Write(cmd), run_time=2.0)
        self.beat("It writes the current time into an annotation in the Pod template.",
                  Create(tpl[0]), FadeIn(tpl[1][:2]), Succession(Wait(0.4), Write(tpl[1][2])), run_time=1.6)
        xs = (1.0, 2.8, 4.6)
        olds = VGroup(*[pod(BLUE_M, 0.38).move_to([x, 0.9, 0]) for x in xs])
        oldl = VGroup(*[M("blue", 20, BLUE_M).next_to(p, DOWN, buff=0.15) for p in olds])
        self.play(LaggedStart(*[GrowFromCenter(p) for p in olds], lag_ratio=0.15), FadeIn(oldl), run_time=0.8)
        news = VGroup(*[pod(GREEN_M, 0.38).move_to([x, 0.9, 0]) for x in xs])
        newl = VGroup(*[M("green", 20, GREEN_M).next_to(p, DOWN, buff=0.15) for p in news])
        self.beat("The template changed, so the Deployment does a normal rolling update.",
                  Indicate(tpl[1][2], color=GOLD_M), run_time=1.2)
        steps = [AnimationGroup(FadeOut(olds[i], scale=0.5), FadeOut(oldl[i]), GrowFromCenter(news[i]), FadeIn(newl[i])) for i in range(3)]
        self.beat("Every new Pod starts with the new values.", LaggedStart(*steps, lag_ratio=0.6), run_time=2.4)
        self.play(FadeOut(VGroup(cmd, tpl, news, newl)), run_time=0.6)

        # 7. Secrets and base64
        sec = card([("kind: Secret", GREY_B, 0), ("name: demo-secret", WHITE, 0), ("data:", WHITE, 0), ("password: czNjcjN0IQ==", PURPLE_M, 1)], PURPLE_M)
        sec.move_to([-3.6, 1.2, 0])
        self.beat("A Secret looks like a ConfigMap, but it is meant for sensitive values: passwords, API tokens, TLS keys. Pods use it the same three ways.",
                  Create(sec[0]), LaggedStart(*[Write(l) for l in sec[1][:3]], lag_ratio=0.2), run_time=2.4)
        self.beat("Its values sit in data, encoded in base64.", Write(sec[1][3]), run_time=1.2)
        plain = M("s3cr3t!", 32, WHITE).move_to([-4.4, -1.9, 0])
        enc = M("czNjcjN0IQ==", 32, PURPLE_M).move_to([3.4, -1.9, 0])
        fw = Arrow(plain.get_right(), enc.get_left(), buff=0.3, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08).shift(UP * 0.3)
        bw = Arrow(enc.get_left(), plain.get_right(), buff=0.3, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.08).shift(DOWN * 0.3)
        fwl = M("base64", 22, GREY_B).next_to(fw, UP, buff=0.1)
        bwl = M("base64 --decode", 22, RED_M).next_to(bw, DOWN, buff=0.1)
        self.beat("Base64 is a way to write any bytes as plain letters, so binary keys fit in YAML.",
                  FadeIn(plain), GrowArrow(fw), FadeIn(fwl), TransformFromCopy(plain, enc), run_time=2.2)
        self.beat("It is not encryption. Anyone can reverse it, with one command.",
                  GrowArrow(bw), FadeIn(bwl), Succession(Wait(0.6), Indicate(plain, color=RED_M)), run_time=2.0)
        # envelope: a note in an envelope that is not sealed
        body = Rectangle(width=2.6, height=1.6, stroke_color=PURPLE_M, stroke_width=3).set_fill(tint(PURPLE_M, 0.15), opacity=1)
        flap = Polygon(body.get_corner(UL), body.get_corner(UR), body.get_top() + UP * 0.9, stroke_color=PURPLE_M, stroke_width=3)
        flap.set_fill(tint(PURPLE_M, 0.1), opacity=1)
        pocket = VGroup(Line(body.get_corner(DL), body.get_center() + UP * 0.1), Line(body.get_corner(DR), body.get_center() + UP * 0.1)).set_stroke(PURPLE_M, 2)
        conf = T("confidential", 22, PURPLE_M).move_to(body.get_center() + UP * 0.45)
        note = Rectangle(width=1.6, height=0.9, stroke_color=WHITE, stroke_width=2).set_fill(BLACK, opacity=1).move_to(body.get_top() + DOWN * 0.05)
        notet = M("s3cr3t!", 20).move_to(note)
        env = VGroup(VGroup(note, notet), body, flap, pocket, conf).move_to([3.6, 1.1, 0])
        self.steps("It is like a note in an envelope marked confidential. Base64 is an envelope that is not sealed.",
                   (1.2, FadeIn(env, shift=UP * 0.2)), (1.4, Wait(1.4)), (1.2, env[0].animate.shift(UP * 1.0 + RIGHT * 2.0)))
        self.play(FadeOut(VGroup(sec, plain, enc, fw, bw, fwl, bwl, env)), run_time=0.6)

        # 8. what protects a Secret, and what does not
        plus = VGroup(
            T("sent only to nodes that run a Pod that needs it", 24),
            T("kept in memory (tmpfs) on the node, never on disk", 24),
            T("kubectl describe shows sizes, not values", 24),
            T("RBAC can allow ConfigMaps but not Secrets", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        ticks = VGroup(*[tick(True, 0.16).next_to(p, LEFT, buff=0.3) for p in plus])
        pl = VGroup(ticks, plus).move_to([0, 1.05, 0])
        shd = T("what protects a Secret", 32, PURPLE_M).move_to([0, 3.2, 0])
        self.beat("A Secret does get some protection that a ConfigMap does not.", Write(shd), run_time=1.4)
        self.beat("It is sent only to nodes that need it, and kept in memory there. describe shows sizes, not values. And access rules can allow ConfigMaps but not Secrets.",
                  LaggedStart(*[AnimationGroup(Create(ticks[i]), FadeIn(plus[i], shift=RIGHT * 0.15)) for i in range(4)], lag_ratio=0.7), run_time=6.0)
        minus = VGroup(T("stored unencrypted in etcd, by default", 24, RED_M),
                       T("anyone who can create a Pod can read every Secret in the namespace", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        crosses = VGroup(*[tick(False, 0.16).next_to(m, LEFT, buff=0.3) for m in minus])
        mn = VGroup(crosses, minus).next_to(pl, DOWN, buff=0.6).align_to(pl, LEFT)
        self.beat("But by default, Secrets are stored unencrypted in etcd. And anyone who can create a Pod in a namespace can mount, and so read, every Secret in it.",
                  Create(crosses[0]), FadeIn(minus[0], shift=RIGHT * 0.15),
                  Succession(Wait(2.4), AnimationGroup(Create(crosses[1]), FadeIn(minus[1], shift=RIGHT * 0.15))), run_time=3.8)
        self.play(FadeOut(VGroup(pl, mn, shd)), run_time=0.6)

        steps = VGroup(T("1. encryption at rest", 28, GREEN_M), T("2. RBAC: few may read Secrets", 28, GREEN_M),
                       T("3. limit who can create Pods", 28, YELLOW_M), T("4. each container gets only what it needs", 28, GREEN_M))
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([-2.2, 0.9, 0])
        self.beat("So turn on encryption at rest, and limit who can read Secrets. Limit who can create Pods, the step people often forget. And give each container only what it needs.",
                  LaggedStart(*[FadeIn(s, shift=RIGHT * 0.15) for s in steps], lag_ratio=0.9), run_time=7.0)
        git = mbox("git", RED_M, size=26, w=1.6, h=0.75).move_to([4.3, 1.2, 0])
        gx = tick(False, 0.3).next_to(git, RIGHT, buff=0.3)
        tools = VGroup(*[chip(t, TEAL_M, 22) for t in ("External Secrets Operator", "Sealed Secrets", "SOPS")]).arrange(RIGHT, buff=0.3).move_to([0, -2.6, 0])
        self.beat("A Secret manifest with real values never goes into git, where base64 is plain text forever. External Secrets Operator, Sealed Secrets or SOPS keep the real values out.",
                  FadeIn(git), Succession(Wait(1.0), Create(gx)), Succession(Wait(4.0), LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in tools], lag_ratio=0.3)), run_time=6.5)
        self.play(FadeOut(VGroup(steps, git, gx, tools)), run_time=0.6)

        # 9. recap
        rc = VGroup(T("settings live outside the image", 30, YELLOW_M),
                    T("env vars: read once, at start", 30, BLUE_M),
                    T("mounted files: updated in place", 30, GREEN_M),
                    T("base64: hides nothing", 30, PURPLE_M)).arrange(DOWN, buff=0.4)
        self.beat("Config lives outside the image. Env vars are read once, at start. Mounted files update in place. And base64 hides nothing.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.45), run_time=4.0)
        self.wait(1.0)
