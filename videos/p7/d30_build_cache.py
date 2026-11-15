import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcompileKotlin\b", "compile Kotlin"), (r"\bcompileTestKotlin\b", "compile test Kotlin"), (r"\bFROM-CACHE\b", "from cache"),
            (r"\bUP-TO-DATE\b", "up to date"), (r"\bgradle\.properties\b", "gradle dot properties"), (r"\bABI\b", "A B I"),
            (r"\borg\.gradle\.caching=true\b", "org dot gradle dot caching equals true"), (r"\b(\d+)s\b", r"\1 seconds")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


XS = [-4.75, -1.6, 1.55, 4.7]
RY = {"greeting": 1.55, "app": -0.55}
NAMES = ["compileKotlin", "jar", "compileTestKotlin", "test"]
ST = {"ran": ("ran", GOLD_M), "cache": ("FROM-CACHE", TEAL_M), "utd": ("UP-TO-DATE", GREEN_M)}


def task(name):
    r = RoundedRectangle(corner_radius=0.1, width=2.75, height=0.62, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1)
    return VGroup(r, M(name, 20).move_to(r).set_z_index(2))


class D30BuildCache(VoiceScene):
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
        self.title_card("Skipping work you already did", "the build cache and compile avoidance")

        # ---- the task graph of two projects
        tasks = {}
        for proj, y in RY.items():
            for n, x in zip(NAMES, XS):
                tasks[(proj, n)] = task(n).move_to([x, y, 0])
        labs = VGroup(*[M(f":{p}", 22, BLUE_M if p == "greeting" else PURPLE_M).move_to([XS[0], y + 0.62, 0]).align_to(tasks[(p, NAMES[0])], LEFT)
                        for p, y in RY.items()])
        arr = VGroup()
        for p in RY:
            arr.add(Arrow(tasks[(p, "compileKotlin")].get_right(), tasks[(p, "jar")].get_left(), buff=0.06, stroke_width=2.5, color=GREY_D, max_tip_length_to_length_ratio=0.25))
            arr.add(Arrow(tasks[(p, "compileTestKotlin")].get_right(), tasks[(p, "test")].get_left(), buff=0.06, stroke_width=2.5, color=GREY_D, max_tip_length_to_length_ratio=0.25))
        cross = Arrow(tasks[("greeting", "jar")].get_corner(DL) + RIGHT * 0.3, tasks[("app", "compileKotlin")].get_corner(UR) + LEFT * 0.4, buff=0.08, stroke_width=2.5, color=GREY_B,
                      max_tip_length_to_length_ratio=0.12)
        allt = VGroup(*tasks.values())
        self.beat("hello-jvm has two projects. greeting is a library, and app uses it. Here are some of their tasks.",
                  FadeIn(labs), LaggedStart(*[FadeIn(t) for t in allt], lag_ratio=0.06), Create(arr), GrowArrow(cross), run_time=2.8)

        marks = {}

        def mark(p, n, kind):
            txt, c = ST[kind]
            t = M(txt, 20, c).next_to(tasks[(p, n)], DOWN, buff=0.1)
            return t

        def set_marks(kinds, rt=1.6):
            """kinds: {(proj, name): kind}; returns animations that light the boxes and swap labels."""
            anims = []
            for key, kind in kinds.items():
                txt, c = ST[kind]
                anims.append(tasks[key][0].animate.set_stroke(c).set_fill(tint(c), 1))
                new = mark(*key, kind)
                if key in marks:
                    anims.append(Transform(marks[key], new))
                else:
                    marks[key] = new
                    anims.append(FadeIn(new))
            return anims

        def reset():
            anims = [t[0].animate.set_stroke(GREY_B).set_fill(BLACK, 1) for t in tasks.values()]
            anims += [FadeOut(m) for m in marks.values()]
            marks.clear()
            return anims

        # ---- 1. clean build, no cache: everything runs
        cmd = M("$ ./gradlew clean build --no-build-cache", 22).move_to([0, 3.25, 0])
        res = M("13 actionable tasks: 13 executed    7s", 22, GOLD_M).move_to([0, -2.1, 0])
        every = {k: "ran" for k in tasks}
        self.steps("Day 28's up-to-date check only helps when the outputs are still there, in the same folder. Run clean, and the outputs are gone. Every task does its work again.",
                   (1.2, FadeIn(cmd)), (2.6, Wait(2.6)), (2.4, LaggedStart(*set_marks(every), lag_ratio=0.05)), (0.8, FadeIn(res)))

        # ---- 2. the build cache: key from inputs, outputs stored under it
        self.play(*reset(), FadeOut(res), run_time=0.7)
        prop = M("org.gradle.caching=true", 22, TEAL_M).move_to([0, 3.25, 0])
        self.beat("Now turn on the build cache, with one line in gradle.properties.",
                  ReplacementTransform(cmd, prop), run_time=1.6)
        ck = tasks[("greeting", "compileKotlin")]
        ins = VGroup(*[chip(t, GREY_B, 20) for t in ("sources", "classpath", "flags")]).arrange(RIGHT, buff=0.15).move_to([-1.3, 2.55, 0])
        key = chip("key 9f3a", YELLOW_M, 20, mono=True).move_to([-4.95, -2.6, 0])
        shelf = RoundedRectangle(corner_radius=0.12, width=12.6, height=1.35, stroke_color=TEAL_M, stroke_width=2).set_fill(BLACK, 1).move_to([0, -2.6, 0])
        shl = M("~/.gradle/caches/build-cache-1", 20, TEAL_M).next_to(shelf, DOWN, buff=0.12).align_to(shelf, RIGHT)
        self.steps("Before a cacheable task runs, Gradle hashes all its inputs into one cache key.",
                   (1.0, FadeIn(shelf), FadeIn(shl)), (1.2, LaggedStart(*[FadeIn(i, shift=DOWN * 0.1) for i in ins], lag_ratio=0.2)),
                   (1.4, ins.animate.scale(0.5).move_to(ck).set_opacity(0)), (1.0, Indicate(ck, color=YELLOW_M)))
        self.remove(ins)
        outs = chip("class files", GOLD_M, 20).next_to(key, RIGHT, buff=0.15)
        entry = VGroup(key, outs)
        self.steps("It runs the task, and stores the outputs under that key.",
                   (0.8, *set_marks({("greeting", "compileKotlin"): "ran"})), (1.4, TransformFromCopy(ck, entry)))
        # the other cacheable tasks
        others = [("app", "compileKotlin"), ("greeting", "compileTestKotlin"), ("app", "compileTestKotlin"), ("greeting", "test"), ("app", "test")]
        ents = VGroup()
        for i, kk in enumerate(others):
            e = chip("key", YELLOW_M, 20, mono=True)
            ents.add(e)
        ents.arrange(RIGHT, buff=0.18).next_to(entry, RIGHT, buff=0.3)
        self.beat("The same happens for each cacheable task: compiling, and testing.",
                  *set_marks({k: "ran" for k in others}), LaggedStart(*[TransformFromCopy(tasks[k], e) for k, e in zip(others, ents)], lag_ratio=0.15), run_time=2.4)

        # ---- 3. clean build with the cache: FROM-CACHE
        self.play(*reset(), run_time=0.7)
        cmd2 = M("$ ./gradlew clean build", 22).move_to([0, 3.25, 0])
        self.beat("Now run clean build again. Clean deletes the outputs. But the inputs did not change, so the keys are the same.",
                  ReplacementTransform(prop, cmd2), Indicate(VGroup(entry, ents), color=YELLOW_M, scale_factor=1.03), run_time=2.4)
        hits = {("greeting", "compileKotlin"): "cache", **{k: "cache" for k in others}}
        self.steps("Gradle finds each key in the cache, copies the outputs in, and prints FROM-CACHE. Compiling and testing never run.",
                   (1.6, LaggedStart(*[Indicate(e, color=TEAL_M) for e in [entry, *ents]], lag_ratio=0.1)),
                   (1.6, *set_marks(hits)))
        res2 = M("13 actionable tasks: 7 executed, 6 from cache    1s", 22, TEAL_M).move_to([0, -1.55, 0])
        self.steps("The jars are rebuilt, because copying files is cheaper than caching them. Seven seconds became one.",
                   (1.2, *set_marks({("greeting", "jar"): "ran", ("app", "jar"): "ran"})), (1.4, Wait(1.4)), (0.8, FadeIn(res2)))

        # ---- 4. the path is not part of the key
        self.play(FadeOut(res2), run_time=0.4)
        nopath = T("the folder path is not part of the key", 26, YELLOW_M).move_to([0, -1.55, 0])
        self.beat("The folder path is not part of the key. So a fresh clone, in another folder, gets hits too.",
                  FadeIn(nopath, shift=UP * 0.1), run_time=2.0)
        clone = M("fresh clone: 20 actionable tasks: 8 executed, 12 from cache", 20, TEAL_M).move_to([0, -1.55, 0])
        self.beat("A fresh clone of hello-jvm on the same laptop built with eight tasks executed, and twelve from cache.",
                  ReplacementTransform(nopath, clone), run_time=1.8)
        self.play(FadeOut(clone), FadeOut(cmd2), *reset(), FadeOut(VGroup(shelf, shl, entry, ents)), run_time=0.7)

        # remote cache, briefly
        rc = box("remote cache (HTTP)", TEAL_M, w=4.0, h=0.8, size=24).move_to([0, -2.55, 0])
        ci = box("CI: clean builds", GOLD_M, w=3.4, h=0.8, size=24).move_to([-4.6, -2.55, 0])
        lap = box("laptops", BLUE_M, w=2.4, h=0.8, size=24).move_to([4.75, -2.55, 0])
        w_ = Arrow(ci.get_right(), rc.get_left(), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.15)
        r_ = Arrow(rc.get_right(), lap.get_left(), buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.15)
        wl = T("write", 20, GOLD_M).next_to(w_, UP, buff=0.08)
        rl = T("read", 20, BLUE_M).next_to(r_, UP, buff=0.08)
        self.beat("Many teams also run a remote cache, an HTTP server every build can read. The Gradle docs recommend that CI fills it from clean builds, and laptops only read.",
                  FadeIn(rc), Succession(Wait(2.6), AnimationGroup(FadeIn(ci), GrowArrow(w_), FadeIn(wl))),
                  Succession(Wait(4.2), AnimationGroup(FadeIn(lap), GrowArrow(r_), FadeIn(rl))), run_time=5.6)
        self.beat("Pull main in the morning, and most of it is already compiled.",
                  travel(w_, GOLD_M, 1.0), Succession(Wait(1.0), travel(r_, BLUE_M, 1.0)), run_time=2.4)
        self.play(FadeOut(VGroup(rc, ci, lap, w_, r_, wl, rl)), run_time=0.6)

        # ---- 5. compile avoidance: three changes to greeting
        ca = T("compile avoidance: change greeting, watch app", 26, YELLOW_M).move_to([0, 3.25, 0])
        self.beat("The Kotlin plugin adds one more trick, compile avoidance. Change greeting in three ways, and watch app.",
                  FadeIn(ca, shift=DOWN * 0.1), run_time=2.0)
        ch = M("1. add a comment", 22, GOLD_M).move_to([0, -1.75, 0])
        self.steps("One. Add a comment. Only greeting's compileKotlin runs. It produces the same class files, so the jar and everything in app stay UP-TO-DATE.",
                   (0.8, FadeIn(ch)), (1.4, *set_marks({("greeting", "compileKotlin"): "ran"})), (2.6, Wait(2.6)),
                   (1.8, *set_marks({("greeting", "jar"): "utd", ("greeting", "compileTestKotlin"): "utd", ("greeting", "test"): "utd", ("app", "compileKotlin"): "utd", ("app", "jar"): "utd",
                                     ("app", "compileTestKotlin"): "utd", ("app", "test"): "utd"})))
        self.play(*reset(), run_time=0.6)
        ch2 = M("2. change a function body", 22, GOLD_M).move_to(ch)
        abi = VGroup(T("ABI: the public signatures", 24, YELLOW_M), T("other code compiles against", 24, YELLOW_M)).arrange(DOWN, buff=0.1).move_to([0, -2.85, 0])
        self.steps("Two. Change a function body. Now the greeting jar and both test tasks run. But app's compileKotlin stays UP-TO-DATE.",
                   (0.8, Transform(ch, ch2)),
                   (1.6, *set_marks({("greeting", "compileKotlin"): "ran", ("greeting", "jar"): "ran", ("greeting", "test"): "ran", ("app", "test"): "ran"})),
                   (1.4, Wait(1.4)), (1.0, *set_marks({("app", "compileKotlin"): "utd"})))
        self.beat("The ABI had not changed. That is the public signatures that other code compiles against.",
                  FadeIn(abi, shift=UP * 0.1), Indicate(cross, color=YELLOW_M), run_time=2.2)
        self.play(*reset(), run_time=0.6)
        ch3 = M("3. add a public function", 22, GOLD_M).move_to(ch)
        self.steps("Three. Add a public function. The ABI changes, and now app's compileKotlin runs too.",
                   (0.8, Transform(ch, ch3)), (1.4, *set_marks({("greeting", "compileKotlin"): "ran", ("greeting", "jar"): "ran"})),
                   (0.8, travel(cross, GOLD_M, 0.8)), (1.0, *set_marks({("app", "compileKotlin"): "ran"})))
        self.beat("So a change behind a stable public API does not ripple through the build. One more reason to split code into projects.",
                  FadeOut(abi), Indicate(labs, color=YELLOW_M), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- recap: four ways
        rcp = VGroup(T("up-to-date check: same folder, nothing changed", 28, GREEN_M),
                     T("build cache: same inputs, any folder or machine", 28, TEAL_M),
                     T("configuration cache: skip the build scripts", 28, BLUE_M),
                     T("daemon: a warm JVM between builds", 28, GOLD_M)).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        self.beat("Gradle has four ways to skip work. Up-to-date checks, in the same folder. The build cache, in any folder or on any machine. The configuration cache, which skips the build scripts. And the daemon, a warm JVM.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.6), run_time=6.0)
        self.wait(1.0)
