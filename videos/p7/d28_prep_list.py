import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\./gradlew\b", "gradle W"), (r"\bcompileKotlin\b", "compile Kotlin"), (r"\bcompileTestKotlin\b", "compile test Kotlin"),
            (r"\bUP-TO-DATE\b", "up to date"), (r"\bdoLast\b", "do last"), (r"\bprintln\b", "print line"),
            (r"build\.gradle\.kts", "build dot gradle dot K T S"), (r"settings\.gradle\.kts", "settings dot gradle dot K T S"),
            (r"\bMain\.kt\b", "main dot K T"), (r"\.gradle\b", "dot gradle")])


def fix_indent(g, size):
    """Text drops leading spaces when lines are left-aligned; shift each line by its indent."""
    cw = M("x" * 20, size).width / 20
    for m in g:
        s = getattr(m, "original_text", "")
        m.shift(RIGHT * (len(s) - len(s.lstrip(" "))) * cw)
    return g


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def line_item(text, color=WHITE, size=26):
    d = Dot(radius=0.06, color=color)
    t = T(text, size, color)
    return VGroup(d, t).arrange(RIGHT, buff=0.2)


class D28PrepList(VoiceScene):
    def construct(self):
        self.title_card("Plan backwards, never cook twice", "how Gradle builds a task graph and skips what is done")

        # ---- 1. the question
        c1 = M("$ ./gradlew test", 30).move_to([0, 1.6, 0])
        c2 = M("$ ./gradlew test", 30).move_to([0, 0.2, 0])
        nc = T("change nothing", 26, GREY_B).move_to([0, 0.9, 0])
        self.beat("You run the tests with Gradle. You change nothing. You run them again.", FadeIn(c1), Succession(Wait(1.2), FadeIn(nc), FadeIn(c2)), run_time=2.4)
        q = T("does it run the tests again? how would it know?", 30, YELLOW_M).move_to([0, -1.4, 0])
        self.beat("Does Gradle run every test again? And if it doesn't, how would it even know that nothing changed?",
                  FadeIn(q, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(c1, c2, nc, q)), run_time=0.6)

        # ---- 2. compiled code, then the bakery
        src = box("Kotlin source", BLUE_M, w=2.7).move_to([-4.9, 1.2, 0])
        cls = box("class files", TEAL_M, w=2.5).move_to([0.0, 1.2, 0])
        jar = box("a jar", GOLD_M, w=2.0).move_to([4.6, 1.2, 0])
        a1, a2 = edge_arrow(src, cls), edge_arrow(cls, jar)
        cl = T("compile", 24, GREY_B).next_to(a1, UP, buff=0.12)
        self.beat("First, why Kotlin needs a build at all. Python runs straight from the text you write. Kotlin source must be compiled, translated into class files a machine can run.",
                  FadeIn(src), GrowArrow(a1), FadeIn(cl), FadeIn(cls), run_time=2.6)
        self.beat("Then those get packed into a jar, one zip file of compiled code. Add tests and libraries, and that's a lot of steps to do in the right order. That's the job of a build tool, like Gradle.",
                  GrowArrow(a2), FadeIn(jar), run_time=2.4)
        self.play(FadeOut(VGroup(src, cls, jar, a1, a2, cl)), run_time=0.6)

        order = T("wedding order: 200 sandwiches", 30, GOLD_M).move_to([-3.2, 3.0, 0])
        menu = VGroup(line_item("sandwiches"), line_item("sauce (eggs: supplier closes at 6)"), line_item("bread"), line_item("dough"), line_item("starter (takes hours)"))
        menu.arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to([-3.2, 0.3, 0])
        self.beat("Now a bakery, the night before a wedding order of two hundred sandwiches. A new baker takes the list, starts at the top, and works down.",
                  FadeIn(order), LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in menu], lag_ratio=0.2), run_time=2.6)
        clock = T("midnight: no bread", 30, RED_M).move_to([3.4, 0.3, 0])
        self.beat("At midnight, the bread isn't ready. Nobody started the dough first, and the starter alone takes hours.",
                  Indicate(menu[4], color=RED_M), FadeIn(clock), run_time=2.0)
        self.beat("He followed the list perfectly. That was the problem. It followed the order of the menu, not the order the work has to happen in.",
                  Indicate(menu, color=GREY_B, scale_factor=1.03), run_time=2.4)
        wish = VGroup(T("plan backwards from what is needed", 28, YELLOW_M), T("and never make the sauce twice", 28, YELLOW_M)).arrange(DOWN, buff=0.15).move_to([3.4, -1.6, 0])
        self.beat("A real kitchen plans backwards from what is needed. And it never makes a sauce twice when this morning's batch is still good. That's exactly how Gradle thinks.",
                  FadeIn(wish), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. tasks, planned backwards
        pos = {"build": [5.2, 0, 0], "assemble": [2.7, 1.5, 0], "check": [2.7, -1.5, 0], "jar": [0.3, 1.5, 0], "test": [0.3, -1.5, 0],
               "classes": [-2.2, 1.5, 0], "compileTestKotlin": [-2.2, -1.5, 0], "compileKotlin": [-4.9, 0, 0]}
        col = {"build": PURPLE_M, "assemble": PURPLE_M, "check": PURPLE_M, "jar": GOLD_M, "test": GREEN_M, "classes": TEAL_M,
               "compileTestKotlin": BLUE_M, "compileKotlin": BLUE_M}
        nodes = {k: mbox(k, col[k], h=0.7, size=22).move_to(p) for k, p in pos.items()}
        for nd in nodes.values():
            nd[1].set_z_index(2)
        deps = [("build", "assemble"), ("build", "check"), ("assemble", "jar"), ("check", "test"), ("jar", "classes"),
                ("test", "compileTestKotlin"), ("classes", "compileKotlin"), ("compileTestKotlin", "compileKotlin")]
        arrs = {d: edge_arrow(nodes[d[0]], nodes[d[1]], GREY_B) for d in deps}
        hdr = T("each line on the prep list is a task", 28, GREY_B).move_to([0, 3.1, 0])
        self.beat("In Gradle, each line of the prep list is a task: a named piece of work, like compileKotlin, test, or jar.",
                  FadeIn(hdr), run_time=1.6)
        self.beat("You ask for build. Gradle starts from there, and plans backwards.", FadeIn(nodes["build"], scale=0.9), run_time=1.4)
        self.beat("Build does no work itself. It groups assemble, which makes the outputs, and check, which runs the tests.",
                  GrowArrow(arrs[("build", "assemble")]), FadeIn(nodes["assemble"]), GrowArrow(arrs[("build", "check")]), FadeIn(nodes["check"]), run_time=2.2)
        self.beat("Assemble needs the jar. The jar needs compiled classes. The classes need compileKotlin.",
                  LaggedStart(AnimationGroup(GrowArrow(arrs[("assemble", "jar")]), FadeIn(nodes["jar"])),
                              AnimationGroup(GrowArrow(arrs[("jar", "classes")]), FadeIn(nodes["classes"])),
                              AnimationGroup(GrowArrow(arrs[("classes", "compileKotlin")]), FadeIn(nodes["compileKotlin"])), lag_ratio=0.55), run_time=3.0)
        self.beat("And check needs test, which needs the compiled tests, which need the main code compiled first.",
                  LaggedStart(AnimationGroup(GrowArrow(arrs[("check", "test")]), FadeIn(nodes["test"])),
                              AnimationGroup(GrowArrow(arrs[("test", "compileTestKotlin")]), FadeIn(nodes["compileTestKotlin"])),
                              GrowArrow(arrs[("compileTestKotlin", "compileKotlin")]), lag_ratio=0.55), run_time=2.8)
        simp = T("simplified", 22, GREY_B).move_to([5.2, -3.2, 0])
        self.add(simp)
        self.beat("Notice compileKotlin is needed twice, but it appears once. Gradle runs each task once, in an order that respects the arrows.",
                  Indicate(nodes["compileKotlin"][1], color=BLUE_M), run_time=2.0)
        runorder = ["compileKotlin", "classes", "compileTestKotlin", "jar", "test", "assemble", "check", "build"]
        self.beat("Now the cooking goes forwards, from the starter to the sandwiches.",
                  LaggedStart(*[nodes[k][0].animate.set_stroke(width=6) for k in runorder], lag_ratio=0.3), run_time=3.0)
        for k in runorder:
            nodes[k][0].set_stroke(width=3)
        gname = T("the task graph: arrows one way, never in a loop", 28, YELLOW_M).move_to([0, 3.1, 0])
        self.beat("This plan is the task graph. Its arrows point one way, and never loop back. The baker's prep list, in the right order at last.",
                  Transform(hdr, gname), run_time=2.0)

        # ---- 4. fingerprints and UP-TO-DATE
        self.beat("Now the second half of the wish. Never make the sauce twice.", run_time=None)
        io = VGroup(T("inputs: source files, classpath, flags", 24, BLUE_M), T("outputs: class files", 24, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        io.move_to([0, -2.45, 0]).align_to(nodes["compileKotlin"], LEFT).shift(LEFT * 0.4)
        self.beat("Every task declares its inputs and its outputs. compileKotlin reads source files and the classpath, the list of jars it can see, and it writes class files.",
                  FadeIn(io), run_time=2.4)
        fp = T("before each task: hash inputs and outputs, compare with the last run", 26, GREY_B).move_to([0, -3.2, 0])
        self.remove(simp)
        self.beat("Before a task runs, Gradle fingerprints them. It hashes their contents, where one changed byte changes the hash, and compares with the hashes it saved in the .gradle folder last time.",
                  FadeIn(fp), run_time=2.6)
        q2 = T("run again, change nothing: what runs?", 28, YELLOW_M).move_to(fp)
        self.beat("So: run the build again, changing nothing. Pause and guess. Which tasks do real work?",
                  FadeOut(fp), FadeOut(io), FadeIn(q2), run_time=1.4)
        self.wait(2.0)
        utd = VGroup(*[T("UP-TO-DATE", 20, GREY_B).next_to(nodes[k], DOWN, buff=0.08) for k in runorder])
        self.beat("None of them. Every task prints UP-TO-DATE, and is skipped. This morning's sauce is still good.",
                  FadeOut(q2), *[nodes[k].animate.set_opacity(0.45) for k in runorder], FadeIn(utd), run_time=2.0)
        for k in runorder:
            nodes[k].set_opacity(1)
        self.play(FadeOut(utd), run_time=0.5)
        q3 = M("$ touch Main.kt", 26, GOLD_M).move_to([0, -3.2, 0])
        self.beat("Let's try to fool it. touch updates a file's time, but not one byte of its contents. Does Gradle fall for it?",
                  FadeIn(q3), run_time=2.0)
        utd2 = T("all 7 tasks still UP-TO-DATE: content, not timestamps", 26, GREEN_M).move_to(q3)
        self.beat("All seven tasks stay up to date. Gradle compares contents, not timestamps.",
                  Transform(q3, utd2), run_time=1.6)
        t2 = T("change only a test file", 26, GOLD_M).move_to([0, -3.2, 0])
        self.beat("Now change one test file. Watch which tasks wake up.", FadeOut(q3), FadeIn(t2), run_time=1.2)
        self.beat("compileTestKotlin and test run. compileKotlin and jar stay up to date, because their inputs are the main source files only.",
                  *[nodes[k][0].animate.set_stroke(width=7) for k in ("compileTestKotlin", "test")],
                  *[nodes[k].animate.set_opacity(0.45) for k in ("compileKotlin", "classes", "jar")], run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. three phases: write the plan, then cook
        self.beat("One question is left. How can Gradle know the whole graph before it runs a single task? It writes the prep list first. Every run has three phases.",
                  run_time=None)
        ph = VGroup(chip("1  initialization: read settings.gradle.kts", BLUE_M, 26), chip("2  configuration: run the build scripts, build the graph", TEAL_M, 26),
                    chip("3  execution: run the task actions", GOLD_M, 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([0, 2.2, 0])
        self.beat("Initialization reads the settings file. Configuration runs the build scripts, which register tasks and build the graph. Only then, execution runs the tasks.",
                  LaggedStart(*[FadeIn(p, shift=RIGHT * 0.1) for p in ph], lag_ratio=0.5), run_time=3.4)
        code = VGroup(M('println("1. initialization")        // settings', 22, BLUE_M),
                      M('println("2. configuration")         // build script', 22, TEAL_M),
                      M('tasks.register("hello") {', 22),
                      M('    println("2b. configuration")', 22, TEAL_M),
                      M('    doLast { println("3. execution") }', 22, GOLD_M),
                      M('}', 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-2.6, -1.3, 0])
        fix_indent(code, 22)
        shn = T("(print texts shortened)", 20, GREY_B).next_to(code, DOWN, buff=0.15).align_to(code, LEFT)
        self.beat("Here's a test from the lesson. Four print lines: one in settings, one at the top of the build script, one inside the hello task's setup block, and one inside doLast.",
                  FadeIn(code), FadeIn(shn), run_time=2.4)
        q4 = T("./gradlew hello: which lines print, in what order?", 26, YELLOW_M).move_to([3.6, -2.9, 0])
        q4 = fit(q4, 5.6)
        self.beat("You run the hello task. Pause and guess: which lines print, and in what order?", FadeIn(q4), run_time=1.4)
        self.wait(2.0)
        outl = VGroup(M("1. initialization", 22, BLUE_M), M("2. configuration", 22, TEAL_M), M("2b. configuration", 22, TEAL_M),
                      M("> Task :hello", 22, GREY_B), M("3. execution", 22, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([0, -1.6, 0])
        outl.align_to(np.array([1.6, 0, 0]), LEFT)
        self.beat("All four. One, two and two b print before any task starts, while the plan is being written. Only line three comes from the task itself.",
                  FadeOut(q4), LaggedStart(*[FadeIn(o, shift=UP * 0.05) for o in outl], lag_ratio=0.3), run_time=3.0)
        self.beat("A build script looks like a program that does the build. It isn't. It only describes the work. Only the code inside doLast runs when the task executes.",
                  Indicate(code[4], color=GOLD_M), run_time=2.6)
        cc = VGroup(M("Reusing configuration cache.", 22, GREY_B), M("> Task :hello", 22, GREY_B), M("3. execution", 22, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(outl, aligned_edge=UL)
        self.beat("Run it a second time. The configuration cache saved the finished prep list, so phases one and two are skipped, and only line three prints.",
                  Transform(outl, cc), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. guardrails
        gt = T("Respect the plan", 34).move_to([0, 2.9, 0])
        self.beat("A few guardrails follow straight from this picture.", FadeIn(gt), run_time=1.0)
        g1 = chip("keep network calls and big file reads out of top-level script code", RED_M, 26).move_to([0, 1.6, 0])
        g2 = chip("a task with no declared outputs always runs", GOLD_M, 26).move_to([0, 0.5, 0])
        g3 = chip("reach for --rerun-tasks often? a task is missing an input", BLUE_M, 26).move_to([0, -0.6, 0])
        g4 = chip("always run ./gradlew: the wrapper pins one Gradle version", TEAL_M, 26).move_to([0, -1.7, 0])
        self.beat("Top-level code in a build script runs every time Gradle configures the build, even for gradlew help. So keep network calls and big file reads out of it.",
                  FadeIn(g1, shift=UP * 0.1), run_time=1.6)
        self.beat("A task with no declared outputs always runs, because there's nothing to compare.", FadeIn(g2, shift=UP * 0.1), run_time=1.4)
        self.beat("If you often reach for rerun tasks to force work, a task is probably missing an input. Fix the build logic instead.",
                  FadeIn(g3, shift=UP * 0.1), run_time=1.6)
        self.beat("And always run ./gradlew, the Gradle Wrapper. It pins the exact Gradle version, so your laptop and every CI runner build the same way.",
                  FadeIn(g4, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. moral and quick check
        mo = VGroup(T("plan backwards from what you asked for,", 30), T("cook forwards, and skip what is already done", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.3, 0])
        self.beat("So, the moral. Gradle plans backwards from what you asked for, cooks forwards in dependency order, and skips every task whose fingerprints didn't change.",
                  FadeIn(mo[0]), Succession(Wait(2.4), FadeIn(mo[1])), run_time=4.0)
        self.beat("The baker who finally reads the list from the bottom.", run_time=None)
        qc = VGroup(T("Quick check", 28, GOLD_M), M('println("hi")   // top of build.gradle.kts', 24),
                    T("In which phase does it print?", 26)).arrange(DOWN, buff=0.25).move_to([0, -1.2, 0])
        self.beat("Quick check. A print line sits at the top of build.gradle.kts. In which phase does it print? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("Configuration: before any task starts.", 26, GREEN_M).move_to(qc[2])
        self.beat("Configuration. It prints while the plan is written, before any task starts.", Transform(qc[2], ans), run_time=1.4)
        self.wait(1.2)
