import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\./gradlew\b", "gradle W"), (r"\bcompileKotlin\b", "compile Kotlin"), (r"\bFROM-CACHE\b", "from cache"),
            (r"\bUP-TO-DATE\b", "up to date"), (r"\bABI\b", "A B I"), (r"\bsetup-gradle\b", "setup gradle"),
            (r":app:compileKotlin", "app's compile Kotlin"), (r":greeting:compileKotlin", "greeting's compile Kotlin")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def card(title, sub, color, w=3.0):
    t = T(title, 26, color)
    s = T(sub, 22, GREY_B)
    g = VGroup(t, s).arrange(DOWN, buff=0.12)
    r = RoundedRectangle(corner_radius=0.12, width=max(w, g.width + 0.45), height=g.height + 0.45, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
    return VGroup(r, g.move_to(r))


class D30SharedFridge(VoiceScene):
    def construct(self):
        self.title_card("The shared fridge", "four ways Gradle skips work, and the build cache up close")

        # ---- 1. the question
        cmd = M("$ ./gradlew clean build", 30).move_to([0, 1.6, 0])
        cl = T("clean: delete the build folders first", 26, GREY_B).next_to(cmd, DOWN, buff=0.3)
        self.beat("Gradle's build cache is switched on. You run clean build. Clean deletes the build folders first, every compiled file, gone.",
                  FadeIn(cmd), Succession(Wait(1.6), FadeIn(cl)), run_time=2.8)
        q = T("so compileKotlin has to compile again... right?", 30, YELLOW_M).move_to([0, -0.6, 0])
        self.beat("So compileKotlin has to compile everything again. Right? The outputs are gone. Keep your answer, we'll check it in a minute.",
                  FadeIn(q, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(cmd, cl, q)), run_time=0.6)

        # ---- 2. the bakery's slow morning
        hd = T("the bakery's busiest morning", 30, GOLD_M).move_to([0, 3.0, 0])
        hab = VGroup(T("the oven went cold overnight: forty minutes to heat", 26),
                     T("the prep list is written again, though the orders are the same", 26),
                     T("each branch makes its own dough, though main made it an hour ago", 26),
                     T("the van carries the whole kitchen to deliver one box of bread", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([0, 0.6, 0])
        self.beat("Picture our bakery on its busiest morning.", FadeIn(hd), run_time=1.0)
        says = ["The oven went cold overnight, and takes forty minutes to heat.",
                "The prep list is written again from scratch, though the orders are the same as yesterday.",
                "Each branch makes its own croissant dough, though the main branch made the same dough an hour ago.",
                "And the van carries the whole kitchen, mixer included, to deliver one box of bread."]
        for h, s in zip(hab, says):
            self.beat(s, FadeIn(h, shift=RIGHT * 0.1), run_time=1.2)
        late = T("each costs a few minutes; together, every delivery is late", 28, RED_M).move_to([0, -2.3, 0])
        self.beat("None of these looks serious. Each costs a few minutes, so nobody fixes it. It's never one big disaster. It's four small ones, holding hands.",
                  FadeIn(late), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. the four cures, mapped
        cs = VGroup(card("up-to-date", "the sauce still in the pot", GREEN_M), card("build cache", "a shared fridge", TEAL_M),
                    card("config cache", "yesterday's prep list", BLUE_M), card("daemon", "an oven kept warm", GOLD_M)).arrange_in_grid(rows=2, cols=2, buff=(0.5, 0.35)).move_to([0, 1.5, 0])
        self.beat("Gradle has four separate ways to skip repeated work, and they're easy to mix up. So let's give each one a picture.",
                  run_time=None)
        says = ["Up-to-date checks, from last time, skip a task whose inputs and outputs didn't change, in the same folder. The sauce still in the pot.",
                "The build cache copies a task's outputs from an earlier run anywhere, even another folder or another machine, when the inputs match. A shared fridge.",
                "The configuration cache skips running the build scripts when they didn't change. Yesterday's prep list.",
                "And the daemon is a background program Gradle keeps running between builds, so Gradle itself starts fast. An oven kept warm."]
        for c, s in zip(cs, says):
            self.beat(s, FadeIn(c, shift=DOWN * 0.1), run_time=1.4)
        self.beat("The build cache saves the most work, so let's open the fridge.", Indicate(cs[1][1][0], color=TEAL_M), run_time=1.6)
        self.play(FadeOut(VGroup(cs[0], cs[2], cs[3])), cs[1].animate.move_to([0, 3.0, 0]), run_time=0.8)

        # ---- 4. how the fridge is labelled
        task = mbox("compileKotlin", BLUE_M, size=24).move_to([-5.0, 0.6, 0])
        ins = VGroup(M("source files", 22), M("classpath", 22), M("compiler flags", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(task, DOWN, buff=0.35).align_to(task, LEFT)
        inl = T("inputs", 24, BLUE_M).next_to(ins, RIGHT, buff=0.3)
        self.beat("Take one task, compileKotlin. Its inputs are the source files, the classpath, and the compiler flags.",
                  FadeIn(task), FadeIn(ins), FadeIn(inl), run_time=2.0)
        keyb = mbox("cache key  9f3a...", YELLOW_M, size=22).move_to([-0.4, 0.6, 0])
        ka = edge_arrow(task, keyb)
        kl = T("hash every input", 24, GREY_B).next_to(ka, UP, buff=0.1)
        self.beat("Before it runs, Gradle hashes all of those inputs into one cache key, a label made of their fingerprints.",
                  GrowArrow(ka), FadeIn(kl), FadeIn(keyb), run_time=2.0)
        fr = RoundedRectangle(corner_radius=0.15, width=3.4, height=3.4, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.06), 1).move_to([4.5, -0.2, 0])
        shelves = VGroup(*[mbox(f"key {k}", TEAL_M, h=0.6, size=20) for k in ("41c0...", "9f3a...", "d27e...")]).arrange(DOWN, buff=0.25).move_to(fr)
        self.beat("The fridge holds earlier outputs, each one filed under the key of the inputs that made it.",
                  Create(fr), LaggedStart(*[FadeIn(s) for s in shelves], lag_ratio=0.2), run_time=1.8)
        fa = edge_arrow(keyb, shelves[1], YELLOW_M)
        self.beat("If the fridge already has that key, Gradle copies the outputs in and prints FROM-CACHE. No compiling.",
                  GrowArrow(fa), Indicate(shelves[1][1], color=YELLOW_M), run_time=1.8)
        np_ = T("the folder path is not part of the key", 26, GREY_B).move_to([0, -2.9, 0])
        self.beat("Notice what's not in the key: the folder path. So a fresh clone, in another folder, can still find its outputs.",
                  FadeIn(np_), run_time=2.0)
        lab = T("illustrative keys", 20, GREY_B).next_to(fr, DOWN, buff=0.12)
        self.add(lab)

        # predict: clean build
        q2 = T("clean build: compiles, or FROM-CACHE?", 28, YELLOW_M).move_to(np_)
        self.beat("Back to our question. Clean deleted the outputs. Pause and guess: does compileKotlin compile, or come from the cache?",
                  FadeOut(np_), FadeIn(q2), run_time=1.8)
        self.wait(2.0)
        a2 = T("FROM-CACHE: not up to date, but the inputs match a stored key", 26, GREEN_M).move_to(q2)
        self.beat("From cache. It isn't up to date, since its outputs were deleted. But its inputs didn't change, so their key is still in the fridge. Gradle restores the outputs instead of compiling.",
                  Transform(q2, a2), run_time=2.4)
        self.beat("So that's the difference. Up-to-date needs the sauce still in the pot. The cache only needs the same recipe and the same ingredients.",
                  Indicate(cs[1], color=TEAL_M), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. the numbers, and a fridge shared between branches
        res = M("20 actionable tasks: 8 executed, 12 from cache", 28, TEAL_M).move_to([0, 2.4, 0])
        self.beat("The lesson tried it. A fresh clone of hello-jvm, in a new folder on the same laptop, built with twenty actionable tasks: eight executed, twelve from cache.",
                  FadeIn(res), run_time=2.4)
        ci = box("CI: clean builds", PURPLE_M, w=3.2).move_to([-4.7, -0.3, 0])
        rc = box("remote cache", TEAL_M, w=3.0).move_to([0.0, -0.3, 0])
        lp = VGroup(box("laptop", WHITE, w=2.2, h=0.7, size=24), box("laptop", WHITE, w=2.2, h=0.7, size=24)).arrange(DOWN, buff=0.4).move_to([4.4, -0.3, 0])
        w = edge_arrow(ci, rc, PURPLE_M)
        wl = T("writes", 24, PURPLE_M).next_to(w, UP, buff=0.1)
        r1, r2 = edge_arrow(rc, lp[0], TEAL_M), edge_arrow(rc, lp[1], TEAL_M)
        rl = T("read", 24, TEAL_M).move_to([2.2, 0.5, 0])
        self.beat("Many teams also run a remote cache, a server every build can read. That's the fridge shared between branches.",
                  FadeIn(rc), run_time=1.6)
        self.beat("The Gradle docs recommend that CI fills it from clean builds, and laptops only read. So half finished local changes never reach the shared cache.",
                  FadeIn(ci), GrowArrow(w), FadeIn(wl), Succession(Wait(1.4), AnimationGroup(FadeIn(lp), GrowArrow(r1), GrowArrow(r2), FadeIn(rl))), run_time=3.2)
        mor = T("pull main in the morning, and most of it is already compiled", 26, GOLD_M).move_to([0, -2.6, 0])
        self.beat("Pull main in the morning, and most of it is already compiled. Nobody makes the same dough twice.", FadeIn(mor), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. compile avoidance
        g = mbox("greeting", BLUE_M, size=24).move_to([-3.6, 1.0, 0])
        a = mbox("app", WHITE, size=24).move_to([2.4, 1.0, 0])
        ga = edge_arrow(a, g)
        gal = T("uses", 24, GREY_B).next_to(ga, UP, buff=0.1)
        self.beat("One more way to skip work, from the Kotlin plugin. Remember the two projects: app uses greeting, our little library. When greeting changes, must app recompile?",
                  FadeIn(g), FadeIn(a), GrowArrow(ga), FadeIn(gal), run_time=2.6)
        rows = VGroup()
        data = [("add a comment", "only :greeting:compileKotlin ran", GREEN_M), ("change a function body", "?", YELLOW_M),
                ("add a public function", ":app:compileKotlin ran too", RED_M)]
        for i, (ch, rs, c) in enumerate(data):
            y = -0.4 - i * 1.0
            rows.add(VGroup(T(ch, 26).move_to([-3.6, y, 0]), T(rs, 26, c).move_to([2.4, y, 0])))
        self.beat("The lesson changed greeting in three ways. One: add a comment. Only greeting's compile ran. It produced the same class files, so everything in app stayed up to date.",
                  FadeIn(rows[0]), run_time=2.4)
        self.beat("Three: add a public function. Now app's compile ran too.", FadeIn(rows[2]), run_time=1.6)
        self.beat("Two: change the code inside a function. Pause and guess. Does app recompile?", FadeIn(rows[1]), run_time=1.6)
        self.wait(2.0)
        ans = T(":app:compileKotlin stayed UP-TO-DATE", 26, GREEN_M).move_to(rows[1][1])
        self.beat("No. app's compile stayed up to date. greeting's jar and the tests ran, but app compiles only against greeting's public signatures, and those didn't change.",
                  Transform(rows[1][1], ans), run_time=2.4)
        abi = T("ABI: the public signatures other code compiles against", 28, YELLOW_M).move_to([0, -3.3, 0])
        self.beat("That set of public signatures is called the ABI, the application binary interface. A change behind a stable public API doesn't ripple through the build. One more reason to prefer implementation.",
                  FadeIn(abi), run_time=2.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. guardrails in CI
        gt = T("In CI, let setup-gradle do the caching", 34).move_to([0, 2.9, 0])
        self.beat("Now take this to CI, where every runner starts fresh. The setup-gradle action caches libraries, the wrapper's Gradle, and the local build cache between runs.",
                  FadeIn(gt), run_time=2.0)
        g1 = chip("don't add cache: gradle or another ~/.gradle cache: they conflict", RED_M, 26).move_to([0, 1.5, 0])
        g2 = chip("don't run clean build in CI: just ./gradlew build", GOLD_M, 26).move_to([0, 0.4, 0])
        g3 = chip("distrust a cache hit? a task input is missing", BLUE_M, 26).move_to([0, -0.7, 0])
        g4 = chip("configuration cache: a miss is slower, never wrong", TEAL_M, 26).move_to([0, -1.8, 0])
        self.beat("Two traps, because more caching sounds safer. Don't add another cache for the Gradle folder. It conflicts with setup-gradle.",
                  FadeIn(g1, shift=UP * 0.1), run_time=1.6)
        self.beat("And don't run clean build in CI. On a fresh runner clean has nothing to delete, and on a reused machine it throws away work Gradle could have skipped.",
                  FadeIn(g2, shift=UP * 0.1), run_time=1.6)
        self.beat("If you distrust a cache hit, the real fix is a task input that's missing from the build logic. And remember, for the configuration cache, a miss is only slower, never wrong.",
                  FadeIn(g3, shift=UP * 0.1), Succession(Wait(1.8), FadeIn(g4, shift=UP * 0.1)), run_time=3.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 8. moral and quick check
        mo = VGroup(T("same inputs, same outputs:", 30), T("label the work by what went in, and share it", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.3, 0])
        self.beat("So, the moral. Same inputs give the same outputs. Label finished work by what went into it, and anyone, anywhere, can reuse it.",
                  FadeIn(mo[0]), Succession(Wait(2.0), FadeIn(mo[1])), run_time=3.6)
        self.beat("The van with the whole kitchen in it? That's packing the image, and the lesson does it next.", run_time=None)
        qc = VGroup(T("Quick check", 28, GOLD_M), T("You clone the project into a brand new folder and build.", 26),
                    T("UP-TO-DATE, or FROM-CACHE?", 26)).arrange(DOWN, buff=0.22).move_to([0, -1.4, 0])
        self.beat("Quick check. You clone the project into a brand new folder, cache on, and build. Will tasks be up to date, or from cache? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("FROM-CACHE, where the cache has it: up-to-date needs the same folder.", 26, GREEN_M).move_to(qc[2])
        self.beat("From cache, for every task the fridge already holds. Up-to-date checks only work in the same folder. The fridge works anywhere.", Transform(qc[2], ans), run_time=1.4)
        self.wait(1.2)
