import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


BW, BH = 2.1, 1.25          # step box size
TOP_Y, BOT_Y = 1.85, -0.75   # the two rows of the loop
TOP_X = [-5.4, -2.7, 0.0, 2.7, 5.4]
BOT_X = [5.4, 1.8, -1.8, -5.4]


def step(n, name, color):
    """One pipeline step: outlined box, step number at top left, name in the middle (tool lines come later)."""
    r = RoundedRectangle(corner_radius=0.12, width=BW, height=BH, stroke_color=color, stroke_width=3)
    r.set_fill(BLACK if ManimColor(color).to_hex().upper() == "#FFFFFF" else interpolate_color(ManimColor("#000000"), ManimColor(color), 0.14), opacity=1)
    lab = T(name, 28).move_to(r)
    num = M(str(n), 20, GREY_B).move_to(r.get_corner(UL) + RIGHT * 0.22 + DOWN * 0.24)
    lab.set_z_index(2); num.set_z_index(2)
    return VGroup(r, lab, num)


def tool_lines(b, tool, part, color):
    """Tool name and course part, placed in the lower half of a step box."""
    t = fit(T(tool, 22, color), BW - 0.25).move_to(b[0].get_center() + DOWN * 0.12)
    p = T(part, 20, GREY_B).move_to(b[0].get_center() + DOWN * 0.42)
    return VGroup(t, p).set_z_index(2)


def lit(b, on=True):
    return b[0].animate.set_stroke(width=6 if on else 3)


class D01Map(VoiceScene):
    def construct(self):
        self.title_card("The DevOps map", "follow one change from your laptop to your users, and back")

        # ---------- 1. the old split
        dev = box("developers", BLUE_M, w=3.0, h=1.1, size=32).move_to(LEFT * 3.6 + UP * 0.6)
        ops = box("operations", GOLD_M, w=3.0, h=1.1, size=32).move_to(RIGHT * 3.6 + UP * 0.6)
        wall = Line(UP * 2.3, DOWN * 1.3, stroke_width=10, color=GREY_D)
        dlab = T("write the code", 24, GREY_B).next_to(dev, DOWN, buff=0.3)
        olab = T("install it, keep it running", 24, GREY_B).next_to(ops, DOWN, buff=0.3)
        self.beat("Here is the older way of shipping software. One team writes the code.",
                  Create(dev[0]), Write(dev[1]), FadeIn(dlab, shift=UP * 0.1), run_time=1.8)
        self.beat("A separate operations team, called ops, installs it on servers and keeps it running.",
                  Create(ops[0]), Write(ops[1]), FadeIn(olab, shift=UP * 0.1), Create(wall), run_time=2.2)

        clock = T("2 a.m.", 30, RED_M).next_to(ops, UP, buff=0.35)
        q = T("?", 44, RED_M).move_to(UP * 2.9)
        call = CurvedArrow(ops.get_top() + UP * 0.1 + LEFT * 0.6, dev.get_top() + UP * 0.1 + RIGHT * 0.6, angle=np.radians(50), color=RED_M, stroke_width=3)
        self.beat("When the app breaks at two in the morning, ops gets the call. But only the developers understand the code.",
                  FadeIn(clock, shift=DOWN * 0.1), ops[0].animate.set_stroke(RED_M, width=5),
                  Succession(Wait(1.6), AnimationGroup(Create(call), FadeIn(q))), run_time=3.4)

        crate = box("release", PURPLE_M, w=1.2, h=0.7, size=22).move_to(dev.get_center() + DOWN * 2.1)
        self.beat("Each side blames the other. So releases get rare and huge, and everyone dreads them.",
                  FadeOut(call), FadeOut(q), FadeIn(crate),
                  Succession(Wait(0.6), crate.animate(run_time=2.4).move_to(ops.get_center() + DOWN * 2.1).scale(1.9)), run_time=3.4)

        team = box("one team: build it, and run it", GREEN_M, w=7.6, h=1.2, size=34).move_to(UP * 0.9)
        self.beat("DevOps removes that split. The people who build software also share the work of running it.",
                  FadeOut(VGroup(crate, clock, dlab, olab)), Uncreate(wall),
                  ReplacementTransform(VGroup(dev, ops), team), run_time=2.6)

        cols = [("Culture", TEAL_M, "shared goals and on-call"),
                ("Practices", GOLD_M, "small changes, automated\ntests and deploys"),
                ("Tools", BLUE_M, "make the practices cheap\nenough to do every day")]
        three = VGroup()
        for i, (name, c, sub) in enumerate(cols):
            ch = chip(name, c, size=30).move_to(np.array([-4.4 + 4.4 * i, -1.0, 0]))
            s = T(sub, 22, GREY_B).next_to(ch, DOWN, buff=0.3)
            three.add(VGroup(ch, s))
        links = VGroup(*[link(team, g[0], GREY_D) for g in three])
        self.beat("It has three parts. A shared culture, practices like small changes and automated tests, and tools that make those practices cheap.",
                  Create(links), LaggedStart(*[Succession(FadeIn(g[0], shift=UP * 0.15), FadeIn(g[1], shift=UP * 0.1)) for g in three], lag_ratio=0.45), run_time=5.6)
        self.beat("A team that installs Kubernetes but keeps the wall between dev and ops ends up with the same wall, plus Kubernetes.",
                  Indicate(three[0][0], color=TEAL_M), run_time=1.6)
        self.play(FadeOut(VGroup(team, three, links)), run_time=0.7)

        # ---------- 2. the path of one change
        head = T("the pipeline", 30, GREY_B).move_to(UP * 3.5)
        spec = [(1, "Code", WHITE), (2, "Build", GOLD_M), (3, "Test", GOLD_M), (4, "Package", TEAL_M), (5, "Release", TEAL_M),
                (6, "Deploy", PURPLE_M), (7, "Run", GREEN_M), (8, "Observe", YELLOW_M), (9, "Feedback", WHITE)]
        pos = [np.array([x, TOP_Y, 0]) for x in TOP_X] + [np.array([x, BOT_Y, 0]) for x in BOT_X]
        S = [step(n, name, c).move_to(p) for (n, name, c), p in zip(spec, pos)]
        A = [edge_arrow(S[i], S[i + 1], GREY_B, buff=0.08) for i in range(8)]
        A.append(edge_arrow(S[8], S[0], GREY_B, buff=0.08))

        def show(i):
            return AnimationGroup(Create(S[i][0]), Write(S[i][1]), FadeIn(S[i][2]))

        self.beat("Every change takes the same road to your users. Engineers call that road the pipeline.",
                  FadeIn(head, shift=DOWN * 0.1), run_time=1.2)

        diff = VGroup(M('- "Hello, DevOps!"', 22, RED_M), M('+ "Hi there"', 22, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        app = M("hello-devops", 22, GREY_B)
        card = VGroup(app, diff).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(np.array([-5.0, 3.2, 0]))
        card.align_to(S[0][0], LEFT)
        self.beat("Take hello-devops, the tiny web app you create tomorrow. You change its default greeting from \"Hello, DevOps!\" to \"Hi there\".",
                  head.animate.set_opacity(0), FadeIn(app, shift=DOWN * 0.1),
                  Succession(Wait(2.4), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.2) for l in diff], lag_ratio=0.5)), run_time=4.4)
        self.remove(head)
        self.beat("Step one is code. You change code on your laptop, and commit it to git.",
                  show(0), run_time=1.6)

        def go(i, extra=(), rt=None, text=""):
            self.beat(text, GrowArrow(A[i - 1]), Succession(Wait(0.4), travel(A[i - 1], YELLOW_M, 0.6)), Succession(Wait(0.7), show(i)), *extra,
                      run_time=rt or 2.0)

        go(1, text="Step two, build. A machine turns the source code into something that can run.")
        go(2, text="Step three, test. Automated tests check that the change works, and broke nothing else.")

        cross = tick(False, 0.3).move_to(S[2][0].get_corner(UR) + LEFT * 0.3 + DOWN * 0.3)
        note = M('a test still expects "Hello, DevOps!"', 22, RED_M).move_to(np.array([0.9, 3.05, 0]))
        self.beat("And here, the test step fails at once, because one test still expects the old greeting.",
                  S[2][0].animate.set_stroke(RED_M, width=5), Create(cross), FadeIn(note, shift=DOWN * 0.1), run_time=2.0)

        soon = T("found 2 minutes later, on your own branch", 24, GREEN_M).move_to(np.array([0.9, 3.55, 0]))
        late = T("a user on Friday night", 24, GREY_B).next_to(soon, RIGHT, buff=0.5)
        strike = Line(late.get_left(), late.get_right(), stroke_width=3, color=RED_M)
        fit(VGroup(soon, late), 9.6).move_to(np.array([1.3, 3.55, 0]))
        strike.put_start_and_end_on(late.get_left() + LEFT * 0.05, late.get_right() + RIGHT * 0.05)
        self.beat("You find out two minutes later, on your own branch, instead of from a user on Friday night.",
                  FadeIn(soon, shift=DOWN * 0.1), Succession(Wait(1.8), AnimationGroup(FadeIn(late), Create(strike))), run_time=3.4)
        self.beat("Each step of the pipeline catches a different kind of mistake, as close as possible to where it was made.",
                  LaggedStart(Indicate(S[1][1], color=GOLD_M), Indicate(S[2][1], color=RED_M), lag_ratio=0.5), run_time=2.0)

        ok = tick(True, 0.22).move_to(cross)
        self.beat("Update that test, push again, and this time the change moves on.",
                  FadeOut(VGroup(note, soon, late, strike)), ReplacementTransform(cross, ok),
                  S[2][0].animate.set_stroke(GOLD_M, width=3), Succession(Wait(0.6), travel(A[1], YELLOW_M, 0.6)), run_time=2.2)
        self.play(FadeOut(ok), run_time=0.4)

        go(3, text="Step four, package. The app and everything it needs go into one bundle, a container image, so it runs the same on any machine.", rt=2.4)
        tag = M("hello-devops:1.0.1", 22, TEAL_M).next_to(S[4][0], UP, buff=0.35).shift(LEFT * 0.4)
        go(4, extra=[Succession(Wait(1.6), FadeIn(tag, shift=DOWN * 0.1))],
           text="Step five, release. The package gets a version number, and goes to a shared store, called a registry.", rt=2.6)

        old = M("1.0.0", 22, GREY_B).next_to(S[5][0], DOWN, buff=0.35)
        new = M("1.0.1", 22, TEAL_M).move_to(old)
        go(5, extra=[Succession(Wait(1.4), FadeIn(old), Wait(0.3), FadeOut(old, shift=DOWN * 0.2), FadeIn(new, shift=DOWN * 0.2))],
           text="Step six, deploy. The new version replaces the old one on the servers.", rt=3.0)

        copies = VGroup(*[Circle(radius=0.16, stroke_color=GREEN_M, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(GREEN_M), 0.3), 1)
                          for _ in range(3)]).arrange(RIGHT, buff=0.25).next_to(S[6][0], DOWN, buff=0.35)
        go(6, extra=[Succession(Wait(1.6), GrowFromCenter(copies[0]), Wait(1.2), LaggedStart(GrowFromCenter(copies[1]), GrowFromCenter(copies[2]), lag_ratio=0.4))],
           text="Step seven, run. Software on the servers keeps the app alive. It restarts it if it crashes, and starts extra copies when traffic grows.", rt=5.0)

        brace = Brace(VGroup(S[5], S[6]), DOWN, buff=0.2, color=GREY_B)
        prod = T("production: the real system your users use", 24, GREY_B).next_to(brace, DOWN, buff=0.15)
        self.beat("This is production, the real system your users use. Merging your code was only the halfway point.",
                  FadeOut(VGroup(copies, new)), GrowFromCenter(brace), FadeIn(prod, shift=UP * 0.1), run_time=2.0)

        spark = VMobject(stroke_color=YELLOW_M, stroke_width=3).set_points_smoothly(
            [np.array([-2.7 + 0.3 * k, -1.95 + 0.25 * np.sin(k * 1.3) + (0.35 if k == 4 else 0), 0]) for k in range(7)])
        go(7, extra=[FadeOut(VGroup(brace, prod)), Succession(Wait(1.4), Create(spark, run_time=1.2))],
           text="Step eight, observe. Graphs, logs and alerts show how the app behaves for real users.", rt=2.8)
        go(8, extra=[FadeOut(spark), FadeOut(tag)],
           text="Step nine, feedback. What you learn shapes the next change, and the loop starts again.", rt=2.0)
        self.play(travel(A[8], YELLOW_M, 0.7), FadeOut(card), run_time=0.8)

        # CI/CD
        ci = VGroup(*S[1:6])
        cil = T("CI/CD: steps 2 to 6", 28, GOLD_M).move_to(np.array([1.8, 0.55, 0]))
        self.beat("CI/CD covers steps two to six. A machine builds and tests every small change, and keeps each one that passes ready to release. You build both in Part 6.",
                  *[lit(b) for b in ci], FadeIn(cil, shift=UP * 0.1), Succession(Wait(2.6), Indicate(VGroup(S[1], S[2]), color=GOLD_M, scale_factor=1.04),
                                                                          Indicate(S[4], color=TEAL_M, scale_factor=1.04)), run_time=5.2)
        self.play(*[lit(b, False) for b in ci], FadeOut(cil), run_time=0.6)

        # ---------- 3. which part owns each step
        def own(idxs, tool, part, color, text, extra=(), rt=2.0):
            anims = []
            for i in idxs:
                tl = tool_lines(S[i], tool, part, color)
                anims += [S[i][1].animate.move_to(S[i][0].get_center() + UP * 0.3), FadeIn(tl, shift=UP * 0.1), FadeOut(S[i][2])]
                S[i].add(tl)
            self.beat(text, *anims, *[lit(S[i]) for i in idxs], *extra, run_time=rt)
            self.play(*[lit(S[i], False) for i in idxs], run_time=0.3)

        self.beat("Now, the course itself. Each of its 20 parts owns one piece of that path.",
                  LaggedStart(*[Indicate(s[0], color=GREY_B, scale_factor=1.05) for s in S], lag_ratio=0.12), FadeOut(S[8][2]), run_time=3.0)
        own([0], "Git", "Part 2", BLUE_M, "Git, in Part 2, keeps every change.")
        own([1, 2], "Actions, Gradle", "Parts 6, 7", GOLD_M,
            "GitHub Actions, in Part 6, tests and builds on every push. Gradle, in Part 7, builds, tests and packages a Kotlin app.", rt=2.6)
        own([3], "Docker", "Part 5", TEAL_M, "Docker, in Part 5, packages the app into an image that runs the same everywhere.")
        own([4], "Actions", "Part 6", TEAL_M, "And GitHub Actions also publishes the image on every push.")
        own([6], "Kubernetes", "Part 10", GREEN_M, "Kubernetes, in Part 10, runs the containers across a cluster, and keeps them healthy.", rt=2.6)
        own([5], "Argo CD", "Part 11", PURPLE_M, "Argo CD, in Part 11, deploys by making the cluster match what git says.")
        own([7], "Prometheus, EFK", "Parts 12 to 14", YELLOW_M,
            "Prometheus, Grafana, and the logs and traces of Parts 12 to 14 tell you how it behaves.", rt=2.4)

        tf = box("Terraform, Ansible", GREY_B, w=2.9, h=0.95, size=24).move_to(np.array([1.8, -2.4, 0]))
        tfp = T("Parts 8, 9", 20, GREY_B)
        tf[1].shift(UP * 0.15); tfp.next_to(tf[1], DOWN, buff=0.1); tf.add(tfp)
        a_tf = edge_arrow(tf, S[6], GREY_B, buff=0.08)
        l_tf = T("creates", 20, GREY_B).next_to(a_tf, LEFT, buff=0.15)
        self.beat("Terraform, in Part 8, creates the ground it runs on. Ansible, in Part 9, sets up the servers on it.",
                  FadeIn(tf, shift=UP * 0.15), GrowArrow(a_tf), FadeIn(l_tf), run_time=2.2)

        sec = box("DevSecOps", RED_M, w=2.4, h=0.95, size=24).move_to(np.array([5.4, -2.4, 0]))
        secp = T("Part 17", 20, GREY_B)
        sec[1].shift(UP * 0.15); secp.next_to(sec[1], DOWN, buff=0.1); sec.add(secp)
        a_sec = DashedLine(sec.get_top() + UP * 0.08, S[5][0].get_bottom() + DOWN * 0.08, dash_length=0.08, stroke_width=3, color=RED_M)
        l_sec = T("checks", 20, GREY_B).next_to(a_sec, RIGHT, buff=0.15)
        self.beat("DevSecOps, in Part 17, adds security checks at every step.",
                  FadeIn(sec, shift=UP * 0.15), Create(a_sec), FadeIn(l_sec),
                  Succession(Wait(1.0), LaggedStart(*[Circumscribe(s[0], color=RED_M, buff=0.04, run_time=0.8) for s in S], lag_ratio=0.15)), run_time=3.4)

        bar = RoundedRectangle(corner_radius=0.12, width=12.9, height=0.5, stroke_color=WHITE, stroke_width=2).set_fill(BLACK, 1).move_to(DOWN * 3.42)
        bar_t = T("Linux (Part 1) and networking (Part 3) underneath everything", 24).move_to(bar)
        self.beat("Underneath everything sit Linux and networking, Parts 1 and 3. Every server and container runs Linux, and talks over a network.",
                  Create(bar), Write(bar_t), run_time=2.6)
        helpers = T("helpers at every layer: Python scripts (Part 4), AI assistants (Part 18)", 24, GREY_B).move_to(UP * 3.42)
        self.beat("Python scripts and AI assistants, Parts 4 and 18, help at every layer.",
                  FadeIn(helpers, shift=DOWN * 0.1), run_time=1.6)

        newt = chip("a new tool?", YELLOW_M, size=26).move_to(np.array([0.0, 0.55, 0]))
        self.beat("Do not try to memorize the list. When a new tool appears, in this course or at work, come back here, and ask which step it owns.",
                  FadeIn(newt, scale=0.8),
                  Succession(Wait(2.6), LaggedStart(*[Indicate(s[0], color=YELLOW_M, scale_factor=1.05) for s in S], lag_ratio=0.15)), run_time=5.0)

        self.beat("One change flows from code to users, and comes back as feedback. Each part of this course owns one step of that loop.",
                  FadeOut(newt), Succession(*[travel(a, YELLOW_M, 0.45) for a in A]), run_time=5.0)
        self.wait(1.2)
