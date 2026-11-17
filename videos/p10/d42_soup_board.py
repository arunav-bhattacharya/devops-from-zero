import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Day 42, fifth pass (Venkat style). Restaurant manager world: the specials board and the shift briefing.
# Concept: what a running Pod sees when a ConfigMap changes. Env vars are the briefing (heard once, at start),
# mounted files are the board on the wall (kept up to date by the kubelet), and rollout restart is a new shift.
# Outputs from the lesson's worked example (config-demo).
# Colours: ConfigMap = GREEN, env var = BLUE, mounted file = GOLD, kubelet = TEAL, rollout restart = PURPLE,
# Pod = WHITE, failure = RED, prompts = YELLOW.

SAY.extend([(r"\bConfigMaps\b", "config maps"), (r"\bConfigMap\b", "config map"), (r"\benvFrom\b", "env from"),
            (r"\bsubPath\b", "sub path"), (r"\bconfigMapGenerator\b", "config map generator"), (r"\bREDIS_HOST\b", "redis host"),
            (r"\bGREETING\b", "greeting"), (r"\bCOLOR\b", "color"), (r"\b\.\.data\b", "dot dot data"), (r"\bdemo-config\b", "demo config"),
            (r"\bconfig-demo\b", "config demo")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color, s=1.0):
    head = Circle(radius=0.17, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    body = RoundedRectangle(corner_radius=0.16, width=0.56, height=0.42, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    body.next_to(head, DOWN, buff=0.05)
    return VGroup(head, body).scale(s)


def panel(color, w, h, pos, k=0.1):
    return RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, k), 1).move_to(pos)


class Base(VoiceScene):
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

    def pause_guess(self, pos=None):
        c = chip("pause and guess", YELLOW_M, 26).move_to(pos if pos is not None else [4.6, -3.0, 0])
        n2 = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        n1 = T("1", 30, YELLOW_M).move_to(n2)
        self.play(FadeIn(c, shift=UP * 0.1), FadeIn(n2), run_time=0.4)
        self.wait(0.8)
        self.play(ReplacementTransform(n2, n1), run_time=0.2)
        self.wait(0.8)
        self.play(FadeOut(c), FadeOut(n1), run_time=0.3)


class D42SoupBoard(Base):
    def construct(self):
        self.title_card("I changed the setting. Why the old value?", "the board, the briefing, and who hears the news")

        # ---------- 1. QUESTION + the restaurant scene
        q = T("you change a setting, apply it, no error... and nothing changes", 30, YELLOW_M).move_to([0, 2.8, 0])
        self.beat("You change one setting, you apply it, and there is no error. Yet the app keeps showing the old value. Did something break?",
                  FadeIn(q, shift=DOWN * 0.1), run_time=1.6)
        brd = panel(GREEN_M, 3.6, 1.6, [-4.2, 0.6])
        btx = VGroup(T("today's soup", 26, GREEN_M), T("tomato", 30)).arrange(DOWN, buff=0.15).move_to(brd)
        office = T("the office", 24, GREY_B).next_to(brd, DOWN, buff=0.15)
        ws = VGroup(*[person(BLUE_M).move_to([x, 0.6, 0]) for x in (1.4, 3.0, 4.6)])
        wl = T("waiters, briefed at noon", 24, BLUE_M).next_to(ws, DOWN, buff=0.25)
        self.beat("Let us start in the restaurant. At noon, the manager briefs the waiters on the specials. Today's soup: tomato. That is on the board in the office.",
                  FadeOut(q), Create(brd), FadeIn(btx), FadeIn(office), LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in ws], lag_ratio=0.2), FadeIn(wl), run_time=2.6)
        pump = T("pumpkin", 30).move_to(btx[1])
        self.beat("At two, the manager changes the soup to pumpkin, and writes it on the board.",
                  Transform(btx[1], pump), Indicate(brd, color=GREEN_M), run_time=1.6)
        say = VGroup(*[T("tomato?", 24, BLUE_M).next_to(w, UP, buff=0.15) for w in ws])
        self.beat("But the waiters heard the specials once, at the start of their shift. So they keep offering tomato soup, and the kitchen keeps saying it has none.",
                  LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in say], lag_ratio=0.3), run_time=2.2)
        self.beat("Nobody did anything wrong. The news reached the board, but not the people who had already heard the old version. Your app can have exactly the same afternoon.",
                  Indicate(wl, color=BLUE_M), run_time=1.8)
        self.play(FadeOut(VGroup(brd, btx, office, ws, wl, say)), run_time=0.7)

        # ---------- 2. FAMILIAR: settings outside the image, the ConfigMap
        img = panel(GREY_B, 3.2, 1.0, [-4.2, 2.4], 0.06)
        imt = M("hello-devops image", 24).move_to(img)
        envs = ["laptop", "staging", "production"]
        dest = VGroup(*[chip(e, GREY_B, 24) for e in envs]).arrange(RIGHT, buff=0.4).move_to([2.2, 2.4, 0])
        self.beat("Since the Docker lessons, we have built one image, and changed how it behaves with environment variables, named settings a program reads when it starts. The same image runs everywhere. Only the settings differ.",
                  Create(img), FadeIn(imt), LaggedStart(*[FadeIn(d, shift=RIGHT * 0.1) for d in dest], lag_ratio=0.3), run_time=2.6)
        cm = panel(GREEN_M, 4.2, 1.5, [-4.2, 0.3])
        cmt = VGroup(T("ConfigMap: hello-config", 26, GREEN_M), M("GREETING: ...", 24), M("REDIS_HOST: redis", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(cm)
        self.beat("In Kubernetes, most teams keep those settings in a ConfigMap. A small object with keys and text values. It is the board in the office.",
                  Create(cm), FadeIn(cmt), run_time=2.0)
        two = VGroup(VGroup(M("envFrom", 26, BLUE_M), T("every key becomes an env var:", 24, GREY_B), T("the briefing, heard once at the start", 24, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08),
                     VGroup(M("volume", 26, GOLD_M), T("every key becomes a file:", 24, GREY_B), T("the board on the kitchen wall", 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08))
        two.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([2.6, -0.4, 0])
        self.steps("A container can read it in two main ways. With envFrom, every key becomes an environment variable. That is the briefing at the start of a shift. Or as a volume: every key becomes a file. That is a board on the kitchen wall, which anyone can look at again.",
                   (0.8, FadeIn(two[0], shift=LEFT * 0.1)), (3.2, Wait(3.2)), (0.8, FadeIn(two[1], shift=LEFT * 0.1)))
        self.play(FadeOut(VGroup(img, imt, dest, cm, cmt, two)), run_time=0.7)

        # ---------- 3. SHRINK: the lab's demo, both ways at once
        cmp_ = panel(GREEN_M, 3.6, 1.3, [-4.4, 2.3])
        cmh = T("ConfigMap: demo-config", 24, GREEN_M)
        cmv = M("COLOR: blue", 26)
        cmg = VGroup(cmh, cmv).arrange(DOWN, buff=0.15).move_to(cmp_)
        pod = RoundedRectangle(corner_radius=0.2, width=5.6, height=2.9, stroke_color=WHITE, stroke_width=3).set_fill(BLACK, 1).move_to([2.9, 1.65, 0])
        podl = T("Pod: config-demo", 24, GREY_B).move_to(pod.get_corner(UL) + [0.2, -0.3, 0], aligned_edge=LEFT)
        envb = panel(BLUE_M, 4.8, 0.75, [2.9, 1.65])
        envt = VGroup(T("env var", 24, BLUE_M), M("COLOR=blue", 24)).arrange(RIGHT, buff=0.4).move_to(envb)
        fileb = panel(GOLD_M, 4.8, 0.75, [2.9, 0.65])
        filet = VGroup(T("file", 24, GOLD_M), M("/config/COLOR: blue", 24)).arrange(RIGHT, buff=0.4).move_to(fileb)
        self.beat("Let us shrink this to the lesson's demo. One ConfigMap, demo-config, with one key: COLOR, blue.",
                  Create(cmp_), FadeIn(cmg), run_time=1.6)
        a_env = Arrow(cmp_.get_right() + DOWN * 0.15, envb.get_left(), buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        a_file = Arrow(cmp_.get_bottom() + RIGHT * 0.6, fileb.get_left(), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.12)
        self.beat("And one Pod that reads that value twice. Once as an environment variable, and once as a file.",
                  Create(pod), FadeIn(podl), Create(envb), FadeIn(envt), GrowArrow(a_env), Create(fileb), FadeIn(filet), GrowArrow(a_file), run_time=2.4)
        term = panel(GREY_B, 7.2, 2.3, [-2.9, -2.2], 0.04)
        thead = M("$ kubectl logs -f config-demo", 22, GREY_B).move_to(term.get_corner(UL) + [0.25, -0.3, 0], aligned_edge=LEFT)
        LOGY = [-1.95, -2.45, -2.95]
        log = VGroup()

        def logline(env, f, i):
            return M(f"env={env} file={f}", 26, WHITE if (env == f) else YELLOW_M).move_to([-6.2, LOGY[i], 0], aligned_edge=LEFT)

        def push(env, f):
            anims = []
            if len(log) == 3:
                anims.append(FadeOut(log[0], shift=UP * 0.2))
                for i in (1, 2):
                    anims.append(log[i].animate.move_to([-6.2, LOGY[i - 1], 0], aligned_edge=LEFT))
                log.remove(log[0])
            nl = logline(env, f, len(log))
            log.add(nl)
            anims.append(FadeIn(nl, shift=UP * 0.15))
            return AnimationGroup(*anims)

        self.steps("Every five seconds, it prints both. env equals blue, file equals blue.",
                   (0.8, Create(term), FadeIn(thead)), (0.6, push("blue", "blue")), (1.4, Wait(1.4)), (0.6, push("blue", "blue")))

        # ---------- 4. PREDICT, then SHOW
        cmv2 = M("COLOR: green", 26).move_to(cmv)
        self.beat("Now change the value in the ConfigMap to green. Pause and guess. What will the next lines say?",
                  Transform(cmv, cmv2), Indicate(cmp_, color=GREEN_M), run_time=1.6)
        self.pause_guess([4.4, -2.2, 0])
        self.steps("For a while, nothing changes at all.",
                   (0.6, push("blue", "blue")), (1.0, Wait(1.0)))
        kl = chip("kubelet sync", TEAL_M, 24).move_to([-4.4, 0.75, 0])
        self.steps("Then, on the kubelet's next sync, usually within a minute or so, the file shows green.",
                   (0.6, FadeIn(kl)), (1.0, travel(a_file, TEAL_M, 1.0)),
                   (0.8, Transform(filet[1], M("/config/COLOR: green", 24).move_to(filet[1])), push("blue", "green")))
        self.steps("And the environment variable? Never. It stays blue for the whole life of the container. The briefing is over.",
                   (0.6, push("blue", "green")), (0.8, Indicate(envt[1], color=BLUE_M)), (1.2, Wait(1.2)))

        # ---------- 5. BREAK the wrong model: "surely a loop notices"
        self.beat("Now wait. Didn't we learn that Kubernetes runs a loop for everything? Surely some controller notices the change and restarts the Pod?",
                  Indicate(cmv, color=GREEN_M), run_time=1.8)
        nob = T("no controller acts on a ConfigMap", 28, RED_M).move_to([3.0, -1.4, 0])
        self.beat("No. A ConfigMap is only data. No controller acts on it. The Deployment controller watches its own Pod template, not the ConfigMaps the template names. So changing a ConfigMap never restarts anything.",
                  FadeIn(nob, shift=UP * 0.1), run_time=2.0)
        mom = VGroup(T("the kubelet reads it at two moments:", 24, TEAL_M), T("1. a container starts: fills in env vars", 24),
                     T("2. its regular sync: refreshes files", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([3.3, -2.6, 0])
        self.steps("The kubelet, the helper on each node, reads it at two moments. When it starts a container, to fill in environment variables. And on its regular sync, to refresh the mounted files.",
                   (0.6, FadeIn(mom[0])), (1.6, Wait(1.6)), (0.6, FadeIn(mom[1]), travel(a_env, BLUE_M, 0.6)), (1.2, Wait(1.2)), (0.6, FadeIn(mom[2]), travel(a_file, TEAL_M, 0.6)))
        self.play(FadeOut(VGroup(nob, mom, term, thead, log)), run_time=0.6)

        # how the file is swapped
        ls = VGroup(M("..2026_10_30_09_41_07.2716545396/", 22, GOLD_M), M("..data -> ..2026_10_30_09_41_07...", 22, TEAL_M),
                    M("COLOR -> ..data/COLOR", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([-2.4, -2.2, 0])
        lsh = M("$ ls -la /config", 22, GREY_B).next_to(ls, UP, buff=0.2).align_to(ls, LEFT)
        self.beat("How does the kubelet swap a file safely? List the folder. The real data sits in a folder named after the time. The name dot dot data is a link, a pointer, to it.",
                  FadeIn(lsh), LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in ls], lag_ratio=0.3), run_time=2.6)
        self.beat("On a change, the kubelet writes a new folder, and moves the link in one step. So the app never reads half a file.",
                  Indicate(ls[1], color=TEAL_M), run_time=1.6)
        sp = VGroup(T("mounted with subPath: never updated", 24, RED_M), T("and it helps only if the app reads it again", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        sp.move_to([4.0, -2.3, 0])
        sp.align_to(np.array([1.0, 0, 0]), LEFT)
        self.steps("That link trick is also why a file mounted with subPath, one file placed into an existing folder, is never updated. And even an updated file only helps if your app reads it again. Most apps read config once, at start.",
                   (0.8, FadeIn(sp[0])), (2.4, Wait(2.4)), (0.8, FadeIn(sp[1])))
        self.play(FadeOut(VGroup(ls, lsh, sp)), run_time=0.6)

        # ---------- 6. the fix: a new shift
        self.beat("So how do the waiters hear about the pumpkin soup? A new shift. The new waiters get a fresh briefing.",
                  Indicate(envb, color=BLUE_M), run_time=1.6)
        term = panel(GREY_B, 7.2, 1.6, [-2.9, -2.5], 0.04)
        rep = M("$ kubectl replace --force ...", 22, GREY_B).move_to(term.get_corner(UL) + [0.25, -0.3, 0], aligned_edge=LEFT)
        out = M("env=green file=green", 26).move_to([-6.2, -2.75, 0], aligned_edge=LEFT)
        self.steps("Our demo is a bare Pod, so we replace it: delete it, and create it again from the same spec. The new container starts with the new value. env equals green, file equals green.",
                   (0.6, Create(term), FadeIn(rep)), (1.0, pod.animate.set_stroke(PURPLE_M), envb.animate.set_opacity(0.3)),
                   (0.6, Transform(envt[1], M("COLOR=green", 24).move_to(envt[1])), envb.animate.set_opacity(1), pod.animate.set_stroke(WHITE)),
                   (1.6, Wait(1.6)), (0.6, FadeIn(out, shift=UP * 0.1)))
        self.play(FadeOut(VGroup(term, rep, out, cmp_, cmg, kl, pod, podl, envb, envt, fileb, filet, a_env, a_file)), run_time=0.7)

        # hello-devops: a Deployment, so rollout restart
        dep = panel(WHITE, 5.4, 2.1, [-3.4, 1.6], 0.0)
        dept = VGroup(M("Deployment hello-devops", 24, GREY_B), M("template:", 24), M("  envFrom: hello-config", 24, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        dept.move_to(dep).align_to(dep, LEFT).shift(RIGHT * 0.3)
        cmd = M("$ kubectl rollout restart deployment/hello-devops", 24, PURPLE_M).move_to([0, -0.4, 0])
        self.beat("hello-devops runs as a Deployment, and it reads GREETING through envFrom. So a new greeting needs new Pods. The tool for that is kubectl rollout restart.",
                  Create(dep), FadeIn(dept), Succession(Wait(2.4), FadeIn(cmd, shift=UP * 0.1)), run_time=3.2)
        ann = M("  annotation: <the current time>", 24, PURPLE_M).next_to(dept[2], DOWN, buff=0.15).align_to(dept[2], LEFT)
        self.play(dep.animate.stretch_to_fit_height(2.6).shift(DOWN * 0.25), run_time=0.4)
        self.beat("It writes the current time into an annotation, a note, in the Pod template.",
                  FadeIn(ann, shift=DOWN * 0.1), run_time=1.4)
        pods = VGroup(*[Circle(radius=0.3, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.3), 1) for _ in range(3)]).arrange(RIGHT, buff=0.4).move_to([3.6, 1.6, 0])
        fresh = VGroup(*[Circle(radius=0.3, stroke_color=PURPLE_M, stroke_width=3).set_fill(tint(PURPLE_M, 0.3), 1).move_to(p) for p in pods])
        self.play(LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.2), run_time=0.8)
        self.steps("The template changed, so the Deployment does a normal rolling update, and every new Pod starts with the new values. A new shift, freshly briefed.",
                   (0.6, Indicate(ann, color=PURPLE_M)),
                   (2.4, LaggedStart(*[Transform(p, f) for p, f in zip(pods, fresh)], lag_ratio=0.6)))
        gen = VGroup(T("tools can do this for you:", 24, GREY_B), M("hello-config-7g2m9dfk8t", 24, GREEN_M),
                     T("new content, new name, new template, new rollout", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0, -2.3, 0])
        self.beat("Tools have a neater trick. Kustomize's configMapGenerator adds a hash, a short code worked out from the content, to the ConfigMap's name. New content means a new name, so the template changes, and a rollout happens by itself.",
                  FadeOut(cmd), FadeIn(gen, shift=UP * 0.1), run_time=2.4)

        # ---------- 7. GUARDRAIL: rollback and versioned config
        self.play(FadeOut(gen), run_time=0.5)
        gr = VGroup(T("a rollback brings back the old template, not the old ConfigMap", 26, RED_M),
                    T("so: hello-config-v1, hello-config-v2, and immutable: true", 26, GREY_B)).arrange(DOWN, buff=0.18).move_to([0, -2.2, 0])
        self.beat("One guardrail. A Deployment rollback brings back the old Pod template, but not the old ConfigMap. Change both, roll back, and the old code runs with the new settings. Like reprinting last week's menu with this week's prices on it.",
                  FadeIn(gr[0], shift=UP * 0.1), run_time=2.4)
        self.beat("The fix is to treat config like images. Never change a version, make a new one, hello-config-v2 next to v1. And immutable true makes sure nobody edits a version in place.",
                  FadeIn(gr[1], shift=UP * 0.1), run_time=2.2)

        # ---------- 8. MORAL + quick check
        self.play(FadeOut(VGroup(dep, dept, ann, pods, gr)), run_time=0.7)
        moral = VGroup(T("env vars: the briefing, heard once at the start", 30, BLUE_M), T("mounted files: the board, updated in place", 30, GOLD_M),
                       T("a new shift hears the news: rollout restart", 30, PURPLE_M)).arrange(DOWN, buff=0.3).move_to([0, 1.7, 0])
        self.steps("The moral of the story. Environment variables are the briefing, heard once, at the start. Mounted files are the board, updated in place. And only a new shift, a rollout restart, hears the news.",
                   (0.8, FadeIn(moral[0], shift=UP * 0.1)), (1.2, Wait(1.2)), (0.8, FadeIn(moral[1], shift=UP * 0.1)), (0.9, Wait(0.9)), (0.8, FadeIn(moral[2], shift=UP * 0.1)))
        ck = VGroup(T("Quick check: you change GREETING in hello-config and apply it.", 28, YELLOW_M),
                    T("What do the running hello-devops Pods show?", 28, YELLOW_M)).arrange(DOWN, buff=0.15).move_to([0, -0.7, 0])
        self.beat("One quick check. You change GREETING in hello-config, and apply it. What do the running hello-devops Pods show?",
                  FadeIn(ck, shift=UP * 0.1), run_time=1.6)
        self.pause_guess([0, -2.0, 0])
        ans = T("The old greeting, until a rollout restart gives them new Pods.", 26).move_to([0, -2.3, 0])
        self.beat("The old greeting. They read it once, at start. Run a rollout restart, and the new Pods show the new one.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.2)
