import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"settings\.gradle\.kts", "settings dot gradle dot K T S"), (r"build\.gradle\.kts", "build dot gradle dot K T S"),
    (r"gradle\.properties", "gradle dot properties"), (r"\./gradlew\b", "gradle W"), (r"(?<![\w.])\.gradle\b", "dot gradle"),
    (r"\bdoLast\b", "do last"), (r"\bcompileTestKotlin\b", "compile test Kotlin"), (r"\bcompileKotlin\b", "compile Kotlin"),
    (r"\bUP-TO-DATE\b", "up to date"), (r"\bFROM-CACHE\b", "from cache"), (r"\bNO-SOURCE\b", "no source"),
    (r"\bSKIPPED\b", "skipped"), (r"\bDAG\b", "dag"), (r"\bMain\.kt\b", "main dot K T"), (r"\bMainTest\.kt\b", "main test dot K T"),
    (r"\bprintln\b", "print line"), (r"\btasks\.register\b", "tasks dot register"),
])


def tint(color, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def panel(w, h, color=GREY_B, sw=2.5, a=0.08):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, a), 1)


def code_line(text, size=20, color=WHITE):
    """Monospace line with an invisible bar in front, so every line has the same height and left edge."""
    t = M("|" + text, size, color)
    t[0].set_opacity(0)
    return t


def code_block(lines, size=20, buff=0.16):
    g = VGroup(*[code_line(t, size, c) for t, c in lines])
    return g.arrange(DOWN, aligned_edge=LEFT, buff=buff)


def flash(m, color=YELLOW_M, rt=1.2):
    return ShowPassingFlash(m.copy().set_fill(opacity=0).set_stroke(color, 6), time_width=0.6, run_time=rt)


def task(name, color=TEAL_M, w=None, size=20):
    m = mbox(name, color, w=w, h=0.66, size=size)
    m[1].set_z_index(2)  # the label stays above its box when only the box is animated
    return m


def harrow(a, b, color=GREY_B):
    return Arrow(a.get_right(), b.get_left(), buff=0.1, stroke_width=3, color=color,
                 max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=8)


def make_graph():
    """The task graph of ./gradlew build, laid out left to right in the order the tasks can run."""
    Y1, Y2 = 1.15, -1.15
    t = {
        "compileKotlin": task("compileKotlin").move_to([-5.35, 0, 0]),
        "classes": task("classes").move_to([-2.35, Y1, 0]),
        "compileTestKotlin": task("compileTestKotlin").move_to([-2.35, Y2, 0]),
        "jar": task("jar").move_to([0.75, Y1, 0]),
        "test": task("test").move_to([0.75, Y2, 0]),
        "assemble": task("assemble", GREY_B).move_to([3.25, Y1, 0]),
        "check": task("check", GREY_B).move_to([3.25, Y2, 0]),
        "build": task("build", YELLOW_M).move_to([5.75, 0, 0]),
    }
    pairs = [("compileKotlin", "classes"), ("compileKotlin", "compileTestKotlin"), ("classes", "jar"), ("compileTestKotlin", "test"),
             ("jar", "assemble"), ("test", "check"), ("assemble", "build"), ("check", "build")]
    arrows = {p: edge_arrow(t[p[0]], t[p[1]]) for p in pairs}
    return t, arrows


def dot_graph(center, s=0.3):
    """The same graph as small dots, for the phase pictures (no labels, so nothing tiny to read)."""
    g, _ = make_graph()
    c0 = np.array([0.2, 0, 0])
    d = {k: Circle(radius=0.14, stroke_color=TEAL_M, stroke_width=2.5).set_fill(tint(TEAL_M, 0.3), 1)
         .move_to(np.array(center) + (v.get_center() - c0) * s * np.array([1.0, 1.6, 1])) for k, v in g.items()}
    d["build"].set_stroke(YELLOW_M)
    pairs = [("compileKotlin", "classes"), ("compileKotlin", "compileTestKotlin"), ("classes", "jar"), ("compileTestKotlin", "test"),
             ("jar", "assemble"), ("test", "check"), ("assemble", "build"), ("check", "build")]
    a = {p: Arrow(d[p[0]].get_center(), d[p[1]].get_center(), buff=0.17, stroke_width=2, color=GREY_B,
                  max_tip_length_to_length_ratio=0.25, max_stroke_width_to_length_ratio=8) for p in pairs}
    return d, a


ORDER = ["compileKotlin", "classes", "compileTestKotlin", "jar", "test", "assemble", "check", "build"]


class D28Gradle(VoiceScene):
    def construct(self):
        self.title_card("How Gradle thinks", "three phases, a task graph, and work it can skip")

        # ---- 1. a task: name, inputs, outputs
        names = VGroup(task("compileKotlin", size=24), task("test", size=24), task("jar", size=24)).arrange(RIGHT, buff=0.8).move_to(UP * 0.4)
        unit = T("a task: one named unit of work", 28, GREY_B).to_edge(UP, buff=0.8)
        self.beat("Gradle's unit of work is a task. A task has a name, such as compileKotlin, test, or jar.",
                  FadeIn(unit), LaggedStart(*[AnimationGroup(Create(n[0]), Write(n[1])) for n in names], lag_ratio=0.35), run_time=3.0)

        ck = names[0]
        ins = VGroup(chip("Main.kt", BLUE_M, 24, mono=True), chip("classpath", BLUE_M, 24), chip("compiler flags", BLUE_M, 24)).arrange(DOWN, buff=0.3)
        ins.move_to([-4.6, -0.2, 0])
        outs = VGroup(chip("class files", GREEN_M, 24)).move_to([4.6, -0.2, 0])
        inl = T("inputs", 28, BLUE_M).next_to(ins, UP, buff=0.35)
        outl = T("outputs", 28, GREEN_M).next_to(outs, UP, buff=0.35)
        self.play(FadeOut(names[1:]), ck.animate.move_to([0, -0.2, 0]), run_time=0.8)
        in_arrows = VGroup(*[Arrow(i.get_right(), ck.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1) for i in ins])
        self.beat("It also declares its inputs: the source files, the classpath, and the compiler flags.",
                  FadeIn(inl), LaggedStart(*[FadeIn(i, shift=RIGHT * 0.15) for i in ins], lag_ratio=0.3), Create(in_arrows), run_time=2.6)
        out_arrow = edge_arrow(ck, outs)
        self.beat("And its outputs. For compileKotlin, those are the class files.",
                  FadeIn(outl), GrowArrow(out_arrow), FadeIn(outs, shift=RIGHT * 0.15), run_time=2.0)
        self.play(*[travel(Line(a.get_start(), a.get_end()), BLUE_M, 0.8) for a in in_arrows], run_time=0.9)
        self.play(travel(Line(out_arrow.get_start(), out_arrow.get_end()), GREEN_M, 0.7), run_time=0.8)
        self.play(FadeOut(VGroup(unit, ins, outs, inl, outl, in_arrows, out_arrow, ck)), run_time=0.6)

        # ---- 2. the task graph
        g, ga = make_graph()
        head = M("./gradlew build", 30, YELLOW_M).to_edge(UP, buff=0.55)
        chain = [g["compileKotlin"], g["classes"], g["jar"]]
        self.beat("Tasks depend on other tasks. jar needs compiled classes, so it depends on classes, which depends on compileKotlin.",
                  Succession(*[AnimationGroup(Create(t[0]), Write(t[1])) for t in reversed(chain)], lag_ratio=0),
                  Succession(Wait(1.6), AnimationGroup(GrowArrow(ga[("classes", "jar")]), GrowArrow(ga[("compileKotlin", "classes")]))), run_time=4.2)
        rest = [g[k] for k in ("compileTestKotlin", "test", "assemble", "check", "build")]
        rest_a = [a for p, a in ga.items() if p not in (("classes", "jar"), ("compileKotlin", "classes"))]
        self.beat("When you ask for build, Gradle collects every task it needs, and puts them in a task graph.",
                  FadeIn(head, shift=DOWN * 0.15), LaggedStart(*[AnimationGroup(Create(t[0]), Write(t[1])) for t in rest], lag_ratio=0.2),
                  Succession(Wait(1.2), LaggedStart(*[GrowArrow(a) for a in rest_a], lag_ratio=0.1)), run_time=3.6)
        dag = T("a DAG: the arrows point one way, and never loop back", 26, GREY_B).to_edge(DOWN, buff=0.6)
        self.beat("The graph is a DAG, a directed acyclic graph. The arrows point one way, and never loop back.",
                  FadeIn(dag, shift=UP * 0.1), LaggedStart(*[flash(a.copy(), YELLOW_M, 1.0) for a in ga.values()], lag_ratio=0.08), run_time=3.0)
        nums = VGroup(*[T(str(i + 1), 22, YELLOW_M).next_to(g[k], UP, buff=0.12) for i, k in enumerate(ORDER)])
        self.beat("Gradle runs each task once, in an order that respects the arrows.",
                  LaggedStart(*[AnimationGroup(g[k][0].animate.set_stroke(YELLOW_M, 5), FadeIn(n, shift=DOWN * 0.1)) for k, n in zip(ORDER, nums)], lag_ratio=0.35),
                  run_time=3.4)
        self.play(*[g[k][0].animate.set_stroke(TEAL_M if k not in ("assemble", "check", "build") else (YELLOW_M if k == "build" else GREY_B), 3) for k in ORDER],
                  FadeOut(nums), FadeOut(dag), run_time=0.6)
        gb1 = T("makes the outputs", 22, GREY_B).next_to(g["assemble"], UP, buff=0.15)
        gb2 = T("runs the tests", 22, GREY_B).next_to(g["check"], DOWN, buff=0.15)
        nowork = VGroup(T("no work", 22, YELLOW_M), T("of its own", 22, YELLOW_M)).arrange(DOWN, buff=0.08).next_to(g["build"], DOWN, buff=0.2)
        self.beat("build itself does no work. It groups assemble, which makes the outputs, and check, which runs the tests.",
                  FadeIn(nowork), Succession(Wait(1.4), FadeIn(gb1, shift=DOWN * 0.1), Wait(0.6), FadeIn(gb2, shift=UP * 0.1)),
                  Indicate(g["build"], color=YELLOW_M, scale_factor=1.08), run_time=4.0)
        graph = VGroup(*g.values(), *ga.values())
        self.play(FadeOut(VGroup(head, gb1, gb2, nowork, graph)), run_time=0.8)

        # ---- 3. the three phases
        PY = 2.6
        ph = [box("1  initialization", BLUE_M, w=3.7, h=0.75, size=26).move_to([-4.4, PY, 0]),
              box("2  configuration", GOLD_M, w=3.7, h=0.75, size=26).move_to([0, PY, 0]),
              box("3  execution", GREEN_M, w=3.7, h=0.75, size=26).move_to([4.4, PY, 0])]
        pa = [harrow(ph[0], ph[1]), harrow(ph[1], ph[2])]
        self.beat("Gradle wants the whole plan before it does any work. So every run goes through three phases, in this order.",
                  LaggedStart(AnimationGroup(Create(ph[0][0]), Write(ph[0][1])), GrowArrow(pa[0]), AnimationGroup(Create(ph[1][0]), Write(ph[1][1])),
                              GrowArrow(pa[1]), AnimationGroup(Create(ph[2][0]), Write(ph[2][1])), lag_ratio=0.35), run_time=4.0)

        sfile = mbox("settings.gradle.kts", BLUE_M, size=20, h=0.62).move_to([-4.4, 1.0, 0])
        root = chip("root project", BLUE_M, 22).move_to([-4.4, -0.35, 0])
        app = chip("app", BLUE_M, 22, mono=True).move_to([-4.4, -1.45, 0])
        tree = VGroup(edge_arrow(sfile, root), edge_arrow(root, app))
        self.beat("Initialization. Gradle reads settings.gradle.kts, and decides which projects take part. In hello-jvm, the root project and app.",
                  flash(ph[0][0], BLUE_M), FadeIn(sfile, shift=DOWN * 0.15),
                  Succession(Wait(1.6), AnimationGroup(GrowArrow(tree[0]), FadeIn(root)), AnimationGroup(GrowArrow(tree[1]), FadeIn(app))), run_time=4.6)

        bfile = mbox("build.gradle.kts", GOLD_M, size=20, h=0.62).move_to([0, 1.0, 0])
        mini, mini_a = dot_graph([0, -0.85, 0])
        mg = VGroup(*mini.values(), *mini_a.values())
        self.beat("Configuration. Gradle runs the build scripts of those projects. They register tasks and set their properties. And Gradle builds the task graph for what you asked.",
                  flash(ph[1][0], GOLD_M), FadeIn(bfile, shift=DOWN * 0.15),
                  Succession(Wait(2.8), LaggedStart(*[GrowFromCenter(mini[k]) for k in ORDER], lag_ratio=0.12), LaggedStart(*[GrowArrow(a) for a in mini_a.values()], lag_ratio=0.05)),
                  run_time=6.4)

        ex, ex_a = dot_graph([4.4, -0.85, 0])
        eg = VGroup(*ex.values(), *ex_a.values())
        act = T("task actions run", 22, GREEN_M).move_to([4.4, 1.0, 0])
        self.beat("Execution. Gradle runs the actions of the tasks in the graph, in dependency order.",
                  flash(ph[2][0], GREEN_M), TransformFromCopy(mg, eg), FadeIn(act), run_time=2.4)
        self.play(LaggedStart(*[ex[k].animate.set_fill(GREEN_M, 1).set_stroke(GREEN_M) for k in ORDER], lag_ratio=0.25), run_time=2.0)
        self.play(FadeOut(VGroup(sfile, root, app, tree, bfile, mg, eg, act)), run_time=0.6)

        # ---- 4. a build script only describes the work
        src = code_block([
            ('println("2. configuration: running build.gradle.kts")', WHITE),
            ("", WHITE),
            ('tasks.register("hello") {', WHITE),
            ('    println("2b. configuration: setting up the hello task")', WHITE),
            ('    doLast { println("3. execution: hello runs its action") }', WHITE),
            ("}", WHITE),
        ], 20, 0.14)
        sp = panel(src.width + 0.7, src.height + 0.55, GREY_B, 2, 0.06)
        src.move_to(sp)
        script = VGroup(sp, src).move_to([0.25, 0.3, 0])
        stitle = M("build.gradle.kts", 20, GREY_B).next_to(sp, UP, buff=0.12).align_to(sp, LEFT)
        self.beat("Careful here. A build script looks like a program that does the build. It only describes the work.",
                  FadeIn(sp), FadeIn(stitle), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in src], lag_ratio=0.2), run_time=3.4)

        def bar(line, color):
            return Line(UP * 0.17, DOWN * 0.17, stroke_width=7, color=color).next_to(sp, LEFT, buff=0.12).set_y(line.get_y())

        bars = VGroup(bar(src[0], GOLD_M), bar(src[2], GOLD_M), bar(src[3], GOLD_M), bar(src[4], GREEN_M))
        self.beat("Code at the top level runs during configuration. So does code inside tasks.register.",
                  src[0].animate.set_color(GOLD_M), FadeIn(bars[0]), flash(ph[1][0], GOLD_M),
                  Succession(Wait(1.8), AnimationGroup(src[2].animate.set_color(GOLD_M), src[3].animate.set_color(GOLD_M), FadeIn(bars[1]), FadeIn(bars[2]))), run_time=3.6)
        self.beat("Only the code inside doLast runs when the task executes.",
                  src[4].animate.set_color(GREEN_M), FadeIn(bars[3]), flash(ph[2][0], GREEN_M), run_time=2.0)

        cmd = code_line("$ ./gradlew hello", 20, YELLOW_M)
        outl = [code_line("1. initialization: reading settings.gradle.kts", 20, BLUE_M),
                code_line("2. configuration: running build.gradle.kts", 20, GOLD_M),
                code_line("2b. configuration: setting up the hello task", 20, GOLD_M),
                code_line("3. execution: hello runs its action", 20, GREEN_M)]
        out = VGroup(cmd, *outl).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0.25, -2.45, 0]).align_to(sp, LEFT).shift(RIGHT * 0.35)
        self.beat("Run the hello task. Lines one and two print before any task starts. Only line three comes from the task's action.",
                  FadeIn(cmd), Succession(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in outl[:3]], lag_ratio=0.4), Wait(1.0), FadeIn(outl[3], shift=UP * 0.1)),
                  run_time=4.8)

        cmd2 = code_line("$ ./gradlew help", 20, YELLOW_M).move_to(cmd, aligned_edge=LEFT)
        strike = Line(outl[2].get_left() + LEFT * 0.1, outl[2].get_right() + RIGHT * 0.1, color=RED_M, stroke_width=3)
        self.beat("Now run help instead. Line two still prints. Top-level code is not lazy: it runs every time Gradle configures the build.",
                  Transform(cmd, cmd2), FadeOut(outl[3]), outl[2][1:].animate.set_opacity(0.3), Indicate(outl[1], color=GOLD_M), run_time=3.0)
        lazy = chip("tasks.register is lazy", GOLD_M, 20, mono=True).next_to(outl[2], RIGHT, buff=0.5)
        self.beat("But line 2b is gone. tasks.register is lazy, so Gradle only sets up a task when the graph needs it.",
                  Create(strike), FadeIn(lazy, shift=LEFT * 0.1), run_time=2.4)
        keep = T("keep network calls and big file reads out of top-level code", 26, RED_M).move_to([0.25, -2.2, 0])
        self.beat("So keep network calls, big file reads and calls to other programs out of top-level code. It slows every run.",
                  FadeOut(VGroup(lazy, cmd, *outl[:3], strike)), Succession(Wait(0.5), FadeIn(keep, shift=UP * 0.1)), Indicate(src[0], color=RED_M, scale_factor=1.03), run_time=2.6)
        self.play(FadeOut(VGroup(sp, src, stitle, bars, keep)), *[FadeOut(p) for p in ph], *[FadeOut(a) for a in pa], run_time=0.7)

        # ---- 5. fingerprints and UP-TO-DATE
        ck = task("compileKotlin", TEAL_M, size=24).move_to([0, 1.3, 0])
        ins = VGroup(chip("Main.kt", BLUE_M, 22, mono=True), chip("classpath", BLUE_M, 22), chip("compiler flags", BLUE_M, 22)).arrange(DOWN, buff=0.25).move_to([-4.9, 1.3, 0])
        outs = chip("class files", GREEN_M, 22).move_to([4.9, 1.3, 0])
        hin = ["9f2c", "77d1", "a3e0"]
        hashes = VGroup(*[M(h + "...", 20, YELLOW_M).next_to(i, RIGHT, buff=0.25) for h, i in zip(hin, ins)])
        hout = M("41ab...", 20, YELLOW_M).next_to(outs, DOWN, buff=0.2)
        a_in = VGroup(*[Arrow(h.get_right(), ck.get_left(), buff=0.15, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.12) for h in hashes])
        a_out = edge_arrow(ck, outs)
        self.beat("Now, why is the second run fast? Before a task runs, Gradle fingerprints its inputs and outputs.",
                  FadeIn(ck), LaggedStart(*[FadeIn(i, shift=RIGHT * 0.1) for i in ins], lag_ratio=0.2), FadeIn(outs), Create(a_in), GrowArrow(a_out), run_time=3.0)
        self.beat("It hashes their contents, the same idea as Git's hashes on Day 8.",
                  LaggedStart(*[Write(h) for h in hashes], lag_ratio=0.3), Write(hout), run_time=2.4)

        store = panel(6.6, 1.5, GREY_B, 2, 0.06).move_to([0, -1.25, 0])
        stl = M(".gradle", 22, GREY_B).next_to(store, UP, buff=0.1).align_to(store, LEFT)
        saved = VGroup(*[M(h + "...", 20, GREY_B) for h in hin + ["41ab"]]).arrange(RIGHT, buff=0.45).move_to(store).shift(UP * 0.15)
        slab = T("saved after the last run", 20, GREY_B).next_to(saved, DOWN, buff=0.18)
        self.beat("Then it compares those hashes with the ones it saved in the project's .gradle folder after the last run.",
                  FadeIn(store), FadeIn(stl), FadeIn(saved), FadeIn(slab), run_time=2.2)
        self.play(LaggedStart(*[AnimationGroup(Indicate(h, color=YELLOW_M), Indicate(sv, color=YELLOW_M)) for h, sv in zip([*hashes, hout], saved)], lag_ratio=0.4), run_time=2.0)
        ticks = VGroup(*[tick(True, 0.15).next_to(s, DOWN, buff=0.12) for s in saved])
        utd = M("UP-TO-DATE", 26, GREY_B).next_to(ck, UP, buff=0.3)
        self.beat("If nothing changed, it prints UP-TO-DATE, and skips the task.",
                  FadeOut(slab), LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.2), Succession(Wait(1.0), FadeIn(utd, shift=DOWN * 0.1)),
                  ck[0].animate.set_stroke(GREY_B).set_fill(tint(GREY_B, 0.1)), run_time=2.6)

        newh = M("c58e...", 20, RED_M).move_to(hashes[0], aligned_edge=LEFT)
        cross = tick(False, 0.15).move_to(ticks[0])
        self.beat("Change one byte in Main.kt, and its hash changes. The fingerprints differ, so the task runs again, and prints no label.",
                  Indicate(ins[0], color=RED_M), Transform(hashes[0], newh), Transform(ticks[0], cross),
                  Succession(Wait(2.4), AnimationGroup(FadeOut(utd), ck[0].animate.set_stroke(TEAL_M, 6).set_fill(tint(TEAL_M, 0.3)))), run_time=4.6)
        self.play(*[travel(Line(a.get_start(), a.get_end()), BLUE_M, 0.7) for a in a_in], run_time=0.8)
        tch = VGroup(M("$ touch Main.kt", 22, YELLOW_M), T("new timestamp, same content: still UP-TO-DATE", 24, GREY_B)).arrange(RIGHT, buff=0.4).to_edge(DOWN, buff=0.45)
        self.beat("Timestamps do not matter. Touch the file without changing it, and the task stays up to date. Only content counts.",
                  FadeIn(tch, shift=UP * 0.1), ck[0].animate.set_stroke(TEAL_M, 3).set_fill(tint(TEAL_M, 0.14)), run_time=2.6)
        self.play(FadeOut(VGroup(ck, ins, outs, hashes, hout, a_in, a_out, store, stl, saved, ticks, tch)), run_time=0.6)

        # ---- 6. a test-only change on the graph
        g, ga = make_graph()
        G = VGroup(*g.values(), *ga.values())
        edit = VGroup(T("change only", 26, GREY_B), M("MainTest.kt", 26, RED_M)).arrange(RIGHT, buff=0.25).to_edge(UP, buff=0.6)
        self.beat("Back to the graph. This time, change only MainTest.kt, and build again.",
                  FadeIn(G), FadeIn(edit, shift=DOWN * 0.1), run_time=2.0)
        same = ["compileKotlin", "classes", "jar"]
        lbl = VGroup(*[M("UP-TO-DATE", 20, GREY_B).next_to(g[k], DOWN, buff=0.12) for k in same])
        self.beat("compileKotlin and jar stay up to date, because their inputs are the main source files only.",
                  *[g[k][0].animate.set_stroke(GREY_D).set_fill(tint(GREY_B, 0.05)) for k in same], *[g[k][1].animate.set_opacity(0.55) for k in same],
                  LaggedStart(*[FadeIn(l) for l in lbl], lag_ratio=0.25), run_time=3.0)
        work = VGroup(*[T("does work", 20, TEAL_M).next_to(g[k], DOWN, buff=0.12) for k in ("compileTestKotlin", "test")])
        self.beat("Only compileTestKotlin and test do real work.",
                  *[g[k][0].animate.set_stroke(TEAL_M, 6).set_fill(tint(TEAL_M, 0.35)) for k in ("compileTestKotlin", "test")],
                  LaggedStart(*[FadeIn(w) for w in work], lag_ratio=0.3), run_time=2.2)
        self.play(travel(Line(ga[("compileTestKotlin", "test")].get_start(), ga[("compileTestKotlin", "test")].get_end()), TEAL_M, 0.7), run_time=0.8)
        self.play(FadeOut(VGroup(G, edit, lbl, work)), run_time=0.6)

        # ---- 7. the labels on task lines
        rows = [("UP-TO-DATE", GREY_B, "nothing changed since the last run, so it was skipped"),
                ("NO-SOURCE", BLUE_M, "nothing to work on, like compileJava in a Kotlin-only project"),
                ("SKIPPED", PURPLE_M, "skipped on purpose, for example under --dry-run"),
                ("FROM-CACHE", GOLD_M, "the outputs were copied from the build cache"),
                ("(no label)", TEAL_M, "the task did real work")]
        tab = VGroup(*[VGroup(M(a, 24, c), T(b, 26, WHITE)) for a, c, b in rows])
        for r in tab:
            r[1].next_to(r[0], RIGHT, buff=0.5)
        LX = -6.3
        for i, r in enumerate(tab):
            r[0].move_to([LX, 2.0 - i * 0.95, 0], aligned_edge=LEFT)
            r[1].move_to([LX + 3.05, 2.0 - i * 0.95, 0], aligned_edge=LEFT)
        tl = T("labels on task lines", 30, GREY_B).to_edge(UP, buff=0.45)
        self.beat("You will see four labels on task lines. UP-TO-DATE, NO-SOURCE, SKIPPED, and FROM-CACHE. No label means the task did real work.",
                  FadeIn(tl), Succession(Wait(1.2), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in tab], lag_ratio=0.55)), run_time=7.0)
        noout = T("a task with no declared outputs is never up to date: it always runs", 26, YELLOW_M).to_edge(DOWN, buff=0.4)
        self.beat("And a task that declares no outputs can never be up to date. There is nothing to compare, so it always runs.",
                  FadeIn(noout, shift=UP * 0.1), Indicate(tab[0][0], color=YELLOW_M), run_time=2.6)
        self.play(FadeOut(VGroup(tl, tab, noout)), run_time=0.6)

        # ---- 8. the configuration cache
        PY = 0.9
        ph = [box("1  initialization", BLUE_M, w=3.7, h=0.75, size=26).move_to([-4.4, PY, 0]),
              box("2  configuration", GOLD_M, w=3.7, h=0.75, size=26).move_to([0, PY, 0]),
              box("3  execution", GREEN_M, w=3.7, h=0.75, size=26).move_to([4.4, PY, 0])]
        pa = [harrow(ph[0], ph[1]), harrow(ph[1], ph[2])]
        prop = VGroup(M("gradle.properties", 20, GREY_B), M("org.gradle.configuration-cache=true", 22, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        prop.to_edge(UP, buff=0.5)
        self.beat("One more trick. The configuration cache saves the result of the first two phases. hello-jvm turns it on in gradle.properties.",
                  *[FadeIn(p) for p in ph], *[FadeIn(a) for a in pa], Succession(Wait(2.6), FadeIn(prop, shift=DOWN * 0.1)),
                  Succession(Wait(1.0), AnimationGroup(flash(ph[0][0], BLUE_M), flash(ph[1][0], GOLD_M))), run_time=5.0)
        hop = CurvedArrow(ph[0].get_bottom() + DOWN * 0.1, ph[2].get_bottom() + DOWN * 0.1, angle=np.radians(50), color=YELLOW_M, stroke_width=3)
        hopl = T("configuration cache hit", 24, YELLOW_M).move_to([0, -1.55, 0])
        reuse = M("Reusing configuration cache.", 22, GREY_B).move_to([0, -2.35, 0])
        self.beat("The next run with the same scripts and tasks goes straight to execution.",
                  ph[0].animate.set_opacity(0.35), ph[1].animate.set_opacity(0.35), Create(hop), FadeIn(hopl), run_time=2.2)
        self.play(travel(hop, YELLOW_M, 1.0), FadeIn(reuse), run_time=1.1)
        noproj = VGroup(M("doLast { project.version }", 22, RED_M), tick(False, 0.16)).arrange(RIGHT, buff=0.3).move_to([0, -1.55, 0])
        self.beat("In return, a running task may not reach back into project, the live build model. On a cache hit the build scripts never ran, so that model does not exist.",
                  FadeOut(reuse), FadeOut(hopl), Succession(Wait(0.4), FadeIn(noproj, shift=UP * 0.1)), Succession(Wait(3.2), AnimationGroup(flash(ph[1][0], RED_M))), run_time=6.0)
        err = VGroup(M("Invocation of 'Task.project' by task ':bad'", 20, RED_M),
                     M("at execution time is unsupported with the configuration cache.", 20, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([0, -2.55, 0])
        self.beat("So Gradle forbids it on every run, hit or miss. The build fails with this error.",
                  FadeIn(err, shift=UP * 0.1), run_time=2.0)
        fix = VGroup(M('val v = project.version.toString()', 20, GOLD_M), M('doLast { println("version is $v") }', 20, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        fix.move_to([0, -2.45, 0])
        self.beat("The fix: read the value during configuration, and keep only the result for the action.",
                  FadeOut(err), FadeOut(noproj), FadeIn(fix, shift=UP * 0.1), ph[1].animate.set_opacity(1), run_time=2.4)
        self.play(FadeOut(VGroup(prop, hop, fix, *ph, *pa)), run_time=0.6)

        # ---- 9. the build cache: FROM-CACHE
        jar = task("jar", TEAL_M, size=24).move_to([-2.2, 0.3, 0])
        cache = panel(3.4, 1.9, GOLD_M, 2.5, 0.08).move_to([3.3, 0.3, 0])
        cl = T("build cache", 26, GOLD_M).next_to(cache, UP, buff=0.15)
        stored = chip("app.jar", GOLD_M, 22, mono=True).move_to(cache)
        outbox = chip("app.jar", GREEN_M, 22, mono=True).move_to([-2.2, -1.3, 0])
        jarr = Arrow(jar.get_bottom(), outbox.get_top(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        outl2 = T("output", 22, GREEN_M).next_to(outbox, LEFT, buff=0.3)
        self.beat("The build cache is a different store. When a task's outputs are already in it, Gradle copies them instead of doing the work, and the task line says FROM-CACHE.",
                  FadeIn(jar), FadeIn(cache), FadeIn(cl), FadeIn(stored), GrowArrow(jarr), FadeIn(outl2),
                  Succession(Wait(3.0), AnimationGroup(ReplacementTransform(stored.copy(), outbox, path_arc=-0.6))), run_time=6.0)
        fc = M("> Task :app:jar FROM-CACHE", 24, GOLD_M).move_to([0, -2.6, 0])
        d30 = T("Day 30 sets it up", 24, GREY_B).next_to(fc, DOWN, buff=0.2)
        self.beat("Day 30 shows how to set it up.", FadeIn(fc, shift=UP * 0.1), FadeIn(d30), run_time=1.6)
        self.play(FadeOut(VGroup(jar, cache, cl, stored, outbox, fc, d30, jarr, outl2)), run_time=0.6)

        # ---- recap
        rec = VGroup(
            VGroup(T("initialization", 30, BLUE_M), T("read the settings, pick the projects", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("configuration", 30, GOLD_M), T("run the scripts, build the task graph", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("execution", 30, GREEN_M), T("run the task actions, in order", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(M("UP-TO-DATE", 26, GREY_B), T("same fingerprints, so the task is skipped", 26, GREY_B)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("Read the settings. Run the scripts to build the task graph. Then run the tasks. And any task whose inputs and outputs did not change is skipped, as UP-TO-DATE.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rec], lag_ratio=0.6), run_time=7.0)
        self.wait(1.0)
