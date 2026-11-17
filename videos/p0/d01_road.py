import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bhello-devops\b", "hello dev ops"), (r"\bCI/CD\b", "C I C D")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color, s=1.0):
    head = Circle(radius=0.24, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    body = RoundedRectangle(corner_radius=0.28, width=0.82, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), 1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(body, head).scale(s)


def loaf(s=1.0, color=GOLD_M):
    e = Ellipse(width=0.9, height=0.48, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    cuts = VGroup(*[Line([-0.08, -0.1, 0], [0.08, 0.1, 0], stroke_width=2.5, color=color).shift(RIGHT * dx) for dx in (-0.2, 0, 0.2)])
    return VGroup(e, cuts).scale(s)


def van(color=GOLD_M):
    b = RoundedRectangle(corner_radius=0.08, width=1.3, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.15), 1)
    cab = RoundedRectangle(corner_radius=0.08, width=0.5, height=0.45, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.15), 1)
    cab.next_to(b, RIGHT, buff=0.0).align_to(b, DOWN)
    w = VGroup(*[Circle(radius=0.13, stroke_color=color, stroke_width=3).set_fill(BLACK, 1).move_to(b.get_corner(DL) + RIGHT * x) for x in (0.3, 1.5)])
    return VGroup(b, cab, w)


BW, BH = 2.1, 1.2
TOP_Y, BOT_Y = 1.75, -0.85
TOP_X = [-5.2, -2.6, 0.0, 2.6, 5.2]
BOT_X = [5.2, 1.75, -1.75, -5.2]


def step(n, name, color):
    r = RoundedRectangle(corner_radius=0.12, width=BW, height=BH, stroke_color=color, stroke_width=3)
    r.set_fill(BLACK if ManimColor(color).to_hex().upper() == "#FFFFFF" else tint(color), opacity=1)
    lab = T(name, 30).move_to(r)
    num = M(str(n), 20, GREY_B).move_to(r.get_corner(UL) + RIGHT * 0.22 + DOWN * 0.24)
    return VGroup(r, lab, num)


class D01Road(VoiceScene):
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

    def countdown(self, where, label="pause and guess"):
        c = chip(label, YELLOW_M, size=26).move_to(where)
        self.play(FadeIn(c, scale=0.9), run_time=0.4)
        for n in ("3", "2", "1"):
            d = T(n, 34, YELLOW_M).next_to(c, RIGHT, buff=0.35)
            self.play(FadeIn(d, run_time=0.15))
            self.wait(0.6)
            self.remove(d)
        self.play(FadeOut(c), run_time=0.3)

    def construct(self):
        self.title_card("The road from kitchen to customer", "what DevOps is, and where a mistake gets caught")

        # ---------- 1. the shy question
        q1 = T("the code is written.", 40).move_to(UP * 0.6)
        q2 = T("so the job is done?", 40, YELLOW_M).next_to(q1, DOWN, buff=0.45)
        self.beat("Here is a question people are often too polite to ask. If programmers write the code, what is all this other work about?",
                  Write(q1), run_time=2.0)
        self.beat("Surely the job is done when the code is written. Right?", FadeIn(q2, shift=UP * 0.15), run_time=1.4)
        self.beat("Let's answer that one in a kitchen.", FadeOut(VGroup(q1, q2)), run_time=1.0)

        # ---------- 2. the bakery: one loaf, then forty
        you = person(BLUE_M).move_to(LEFT * 4.6 + DOWN * 0.2)
        youl = T("you", 26, BLUE_M).next_to(you, DOWN, buff=0.2)
        one = loaf(1.4).move_to(LEFT * 1.6 + DOWN * 0.1)
        self.beat("Picture yourself baking bread in your home kitchen. The neighbours love it.",
                  FadeIn(you, shift=UP * 0.2), FadeIn(youl), Succession(Wait(1.2), GrowFromCenter(one)), run_time=2.6)
        cafe = box("café", TEAL_M, w=2.0, h=1.0, size=30).move_to(RIGHT * 4.9 + UP * 2.2)
        grid = VGroup(*[loaf(0.42) for _ in range(40)]).arrange_in_grid(rows=5, cols=8, buff=(0.12, 0.16)).move_to(RIGHT * 1.6 + DOWN * 0.6)
        forty = T("40 loaves, every morning", 28, TEAL_M).next_to(grid, DOWN, buff=0.35)
        self.beat("Then the café down the street asks for forty loaves, every morning, starting Monday.",
                  FadeIn(cafe, shift=LEFT * 0.2), Succession(Wait(1.4), AnimationGroup(ReplacementTransform(one, grid[0]),
                  LaggedStart(*[GrowFromCenter(g) for g in grid[1:]], lag_ratio=0.03))), FadeIn(forty), run_time=4.0)
        self.beat("Baking one good loaf was never the hard part. The hard part is forty good loaves, on time, every single morning, while you keep improving the recipe.",
                  Indicate(forty, color=TEAL_M), run_time=1.6)
        burnt = grid[13]
        self.beat("And nobody gets a burnt one.",
                  burnt[0].animate.set_stroke(GREY_D).set_fill(GREY_D, 1), burnt[1].animate.set_color(BLACK), run_time=1.0)
        self.play(burnt[0].animate.set_stroke(GOLD_M).set_fill(tint(GOLD_M, 0.3), 1), burnt[1].animate.set_color(GOLD_M), run_time=0.5)
        sw = T("software: it only helps people while it runs, every day, after every change", 26, GREY_B).move_to(DOWN * 3.3)
        self.beat("Software has the same problem. A program helps nobody until it runs for real people, every day, and keeps running after each change.",
                  FadeIn(sw, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(grid, forty, sw)), run_time=0.6)

        # ---------- 3. the wall
        self.play(you.animate.move_to(LEFT * 4.6 + UP * 0.2), youl.animate.move_to(LEFT * 4.6 + DOWN * 0.75), run_time=0.6)
        cousin = person(GOLD_M).move_to(RIGHT * 0.9 + UP * 0.2)
        cl = T("your cousin", 26, GOLD_M).next_to(cousin, DOWN, buff=0.2)
        v = van().next_to(cousin, RIGHT, buff=0.5).shift(DOWN * 0.1)
        self.beat("Let's grow the bakery a little. You bake, and your cousin drives the loaves to the café.",
                  FadeIn(cousin, shift=UP * 0.2), FadeIn(cl), Succession(Wait(1.6), FadeIn(v, shift=RIGHT * 0.3)), run_time=3.0)
        wall = Line(UP * 1.9 + LEFT * 1.85, DOWN * 1.6 + LEFT * 1.85, stroke_width=10, color=GREY_D)
        call = T("7:00  the bread is flat!", 28, RED_M).next_to(cafe, DOWN, buff=0.3).align_to(cafe, RIGHT)
        self.beat("One Friday, the café calls at seven. The bread is flat.",
                  Create(wall), FadeIn(call, shift=DOWN * 0.1), cafe[0].animate.set_stroke(RED_M), run_time=1.8)
        sb1 = T("the hot van!", 26, BLUE_M).next_to(you, UP, buff=0.35)
        sb2 = T("the dough!", 26, GOLD_M).next_to(cousin, UP, buff=0.35)
        self.beat("Your cousin can't fix it, because only you know the recipe. So you blame the hot van, and your cousin blames the dough.",
                  Succession(Wait(2.4), FadeIn(sb1, shift=DOWN * 0.1), Wait(0.6), FadeIn(sb2, shift=DOWN * 0.1)), run_time=4.2)
        nob = T("still no bread", 26, RED_M).next_to(call, DOWN, buff=0.2).align_to(call, RIGHT)
        self.beat("And the café? Still no bread. The only thing that arrived on time was the blame.",
                  FadeIn(nob), run_time=1.6)
        self.beat("So the point is: with a wall in the middle, nobody owns the whole road from oven to shelf.",
                  Indicate(wall, color=GREY_B), run_time=1.6)

        # map onto software
        dev = T("developers", 28, BLUE_M).move_to(youl)
        ops = T("operations", 28, GOLD_M).move_to(cl)
        srv = T("write the code", 24, GREY_B).next_to(dev, DOWN, buff=0.15)
        srv2 = T("run it on servers", 24, GREY_B).next_to(ops, DOWN, buff=0.15)
        self.beat("Software companies were split the same way for years. Developers wrote the code, the instructions that tell a computer what to do.",
                  FadeOut(VGroup(sb1, sb2, nob, call)), cafe[0].animate.set_stroke(TEAL_M), Transform(youl, dev), FadeIn(srv), run_time=2.4)
        self.beat("A second team, operations, ran that code on servers. A server is a computer that stays on day and night, and answers other computers.",
                  Transform(cl, ops), FadeIn(srv2), run_time=2.4)
        clock = T("2 a.m.", 30, RED_M).next_to(cousin, UP, buff=0.35)
        self.beat("When the app broke at two in the morning, operations got the call. But only the developers understood the code.",
                  FadeIn(clock, shift=DOWN * 0.1), Succession(Wait(2.4), Indicate(you[1], color=BLUE_M)), run_time=3.4)
        crate = box("release", PURPLE_M, w=1.5, h=0.7, size=24).move_to(LEFT * 4.6 + DOWN * 2.6)
        self.beat("So both sides made releases rare. A release is one batch of changes handed to users. Rare releases grew huge, and everyone dreaded them.",
                  FadeIn(crate), Succession(Wait(2.2), crate.animate(run_time=2.4).move_to(RIGHT * 0.9 + DOWN * 2.55).scale(1.6)), run_time=4.6)
        wish = T("wouldn't it be nice if the one who knows the recipe also got the 7 a.m. call?", 26, YELLOW_M).move_to(UP * 3.05)
        fit(wish, 11.4)
        self.beat("Wouldn't it be nice if the person who knows the recipe also heard about the flat bread?",
                  FadeIn(wish, shift=DOWN * 0.1), run_time=1.8)

        # ---------- 4. name it: DevOps
        team = RoundedRectangle(corner_radius=0.2, width=10.2, height=2.6, stroke_color=GREEN_M, stroke_width=3).move_to(LEFT * 0.55 + UP * 0.1)
        teaml = T("one team: build it, and run it", 28, GREEN_M).next_to(team, DOWN, buff=0.25)
        self.beat("That wish has a name. DevOps: a way of working where the people who build software also share the work of running it.",
                  FadeOut(VGroup(wish, clock, crate, srv, srv2)), Uncreate(wall), Create(team), FadeIn(teaml), run_time=3.0)
        oc = T("on-call: take turns answering the early call", 26, GREY_B).move_to(DOWN * 2.6)
        self.beat("In the bakery, you and your cousin share one goal, good bread at seven, and you take turns answering the early call. Teams call that on-call duty.",
                  FadeIn(oc, shift=UP * 0.1), run_time=2.4)
        cols = [("culture", TEAL_M, "share the goal"), ("practices", GOLD_M, "small changes, taste every batch"), ("tools", BLUE_M, "the timer and the mixer")]
        three = VGroup()
        for i, (nm, c, sub) in enumerate(cols):
            ch = chip(nm, c, size=28)
            s = T(sub, 22, GREY_B).next_to(ch, DOWN, buff=0.2)
            three.add(VGroup(ch, s))
        three.arrange(RIGHT, buff=0.7).move_to(DOWN * 2.75)
        self.beat("You make small recipe changes, taste every batch, and watch the café shelf. Then you buy the timer and the mixer that make those habits cheap. Teams call those three layers culture, practices and tools.",
                  FadeOut(oc), Succession(Wait(5.2), LaggedStart(*[FadeIn(g, shift=UP * 0.15) for g in three], lag_ratio=0.5)), run_time=7.6)
        self.beat("Notice the order, though. A shiny new mixer never got two people talking. Buy every tool and keep the wall, and you still have the wall.",
                  Indicate(three[2][0], color=BLUE_M), Succession(Wait(2.6), Indicate(three[0][0], color=TEAL_M)), run_time=4.2)
        self.beat("Tools make good habits cheap. They don't create them.", run_time=None)
        self.play(FadeOut(VGroup(team, teaml, three, you, youl, cousin, cl, v, cafe)), run_time=0.7)

        # ---------- 5. one change down the bakery road, and the skipped tasting
        names = ["recipe card", "test batch", "tasting", "bag", "van", "café shelf"]
        road = VGroup(*[box(n, GOLD_M if n != "café shelf" else TEAL_M, w=1.85, h=0.85, size=24) for n in names]).arrange(RIGHT, buff=0.32).move_to(UP * 0.9)
        ra = VGroup(*[edge_arrow(road[i], road[i + 1], GREY_B, buff=0.05) for i in range(5)])
        chg = T("change: less sugar", 28, YELLOW_M).move_to(UP * 2.6)
        self.beat("Now follow one change down the road. Say you decide to use less sugar.",
                  FadeIn(chg, shift=DOWN * 0.1), run_time=1.6)
        self.steps("You write it on the recipe card, bake a test batch, and taste it. You bag the loaves, the van takes them to the café, and you watch who buys a second one.",
                   (0.6, FadeIn(road[0])), (0.5, GrowArrow(ra[0]), FadeIn(road[1])), (0.5, GrowArrow(ra[1]), FadeIn(road[2])),
                   (1.0, Wait(1.0)), (0.5, GrowArrow(ra[2]), FadeIn(road[3])), (0.5, GrowArrow(ra[3]), FadeIn(road[4])), (0.5, GrowArrow(ra[4]), FadeIn(road[5])))
        x = tick(False, 0.35).move_to(road[2])
        self.beat("Now picture a busy Tuesday. You skip the tasting, to save ten minutes.",
                  road[2][0].animate.set_stroke(GREY_D), road[2][1].animate.set_color(GREY_D), Create(x), run_time=1.6)
        tue = T("Tuesday", 26, YELLOW_M).next_to(road[2], DOWN, buff=0.9)
        fri = T("Friday", 26, RED_M).next_to(road[5], DOWN, buff=0.9)
        far = Arrow(tue.get_right(), fri.get_left(), buff=0.25, color=RED_M, stroke_width=4, max_tip_length_to_length_ratio=0.05)
        com = T('"your bread tastes of nothing"', 26, RED_M).next_to(fri, DOWN, buff=0.35).align_to(fri, RIGHT)
        self.beat("On Friday, an unhappy café owner tells you the bread tastes of nothing.",
                  FadeIn(fri), FadeIn(com, shift=UP * 0.1), road[5][0].animate.set_stroke(RED_M), run_time=2.0)
        self.beat("The mistake was made on Tuesday. You paid for it on Friday, far down the road.",
                  FadeIn(tue), Succession(Wait(1.4), GrowArrow(far)), run_time=3.0)
        self.beat("Hold on to that distance, from where a mistake is made to where it is found. It is the whole story of today.",
                  Indicate(far, color=RED_M), run_time=1.8)
        self.play(FadeOut(VGroup(road, ra, x, tue, fri, far, com, chg)), run_time=0.7)

        # ---------- 6. the pipeline
        spec = [(1, "Code", WHITE), (2, "Build", GOLD_M), (3, "Test", GOLD_M), (4, "Package", TEAL_M), (5, "Release", TEAL_M),
                (6, "Deploy", PURPLE_M), (7, "Run", GREEN_M), (8, "Observe", YELLOW_M), (9, "Feedback", WHITE)]
        pos = [np.array([x_, TOP_Y, 0]) for x_ in TOP_X] + [np.array([x_, BOT_Y, 0]) for x_ in BOT_X]
        S = [step(n, nm, c).move_to(p) for (n, nm, c), p in zip(spec, pos)]
        A = [edge_arrow(S[i], S[i + 1], GREY_B, buff=0.08) for i in range(8)] + [edge_arrow(S[8], S[0], GREY_B, buff=0.08)]

        def show(i):
            return AnimationGroup(Create(S[i][0]), Write(S[i][1]), FadeIn(S[i][2]))

        head = T("the pipeline", 30, GREY_B).move_to(UP * 0.45)
        self.beat("Software takes the same road. It is called the pipeline: a fixed series of steps, run by machines, that carries a change to real users.",
                  FadeIn(head), run_time=1.4)
        self.beat("Code. You change code on your laptop, and commit it to git, a tool that saves snapshots of your files.", show(0), run_time=1.4)

        def go(i, text, rt=1.6):
            self.beat(text, GrowArrow(A[i - 1]), Succession(Wait(0.3), travel(A[i - 1], YELLOW_M, 0.5)), Succession(Wait(0.6), show(i)), run_time=rt)

        go(1, "Build. A machine turns the code into something that can run.")
        go(2, "Test. Automated tests, small programs that check your program, make sure the change works and broke nothing else.")
        go(3, "Package. The app and everything it needs go into one bundle, a container image, so it runs the same on any machine.")
        go(4, "Release. The package gets a version number, and goes to a shared store, called a registry.")
        go(5, "Deploy. The new version replaces the old one on the servers.")
        go(6, "Run. Software on the servers keeps the app alive, and restarts it if it crashes.")
        go(7, "Observe. Graphs, logs and alerts show how the app behaves.")
        go(8, "Feedback. What you learn shapes the next change.")
        self.beat("And the loop starts again.", FadeOut(head), GrowArrow(A[8]), Succession(Wait(0.3), travel(A[8], YELLOW_M, 0.6)), run_time=1.2)

        brace = Brace(VGroup(S[5], S[6]), DOWN, buff=0.15, color=GREY_B)
        prod = T("production: the real, live system", 26, GREY_B).next_to(brace, DOWN, buff=0.12)
        self.beat("The real, live system that your users use is called production.", GrowFromCenter(brace), FadeIn(prod), run_time=1.6)
        bk = [(0, "recipe card"), (2, "tasting"), (3, "bag")]
        bl = VGroup(*[T(t, 24, GOLD_M).next_to(S[i][0], UP, buff=0.15) for i, t in bk])
        vl = T("van", 24, GOLD_M).next_to(S[5][0], UP, buff=0.12)
        self.beat("And here is the bakery, mapped. The recipe card is the code. The tasting is the test. The bag is the package. And the van is the deploy.",
                  FadeOut(VGroup(brace, prod)), Succession(Wait(1.6), FadeIn(bl[0]), Wait(0.9), FadeIn(bl[1]), Wait(0.9), FadeIn(bl[2]), Wait(0.9), FadeIn(vl)), run_time=6.0)

        # ---------- 7. predict: where does the mistake get caught?
        diff = VGroup(M("hello-devops", 24, GREY_B), M('- "Hello, DevOps!"', 24, RED_M), M('+ "Hi there"', 24, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        diff.move_to(UP * 0.45)
        self.beat("Let's send one tiny change down this road. Tomorrow you create hello-devops, a tiny web app that answers every visit with a greeting and a count of visits so far.",
                  FadeOut(VGroup(bl, vl)), FadeIn(diff[0]), run_time=1.6)
        self.beat("You change its greeting from Hello, DevOps! to Hi there, and push. But one test still expects the old greeting.",
                  LaggedStart(FadeIn(diff[1], shift=RIGHT * 0.2), FadeIn(diff[2], shift=RIGHT * 0.2), lag_ratio=0.6), run_time=2.4)
        self.beat("Where on the road does this mistake get caught?", Indicate(VGroup(*[s[0] for s in S]), color=YELLOW_M, scale_factor=1.02), run_time=1.4)
        self.countdown(DOWN * 2.55)
        cross = tick(False, 0.3).move_to(S[2][0].get_corner(UR) + LEFT * 0.32 + DOWN * 0.3)
        self.steps("Right here, at the test step. It fails at once.",
                   (0.6, travel(A[0], YELLOW_M, 0.6)), (0.6, travel(A[1], YELLOW_M, 0.6)),
                   (0.6, S[2][0].animate.set_stroke(RED_M, width=6), Create(cross)))
        soon = T("found 2 minutes later, on your own branch", 28, GREEN_M).move_to(DOWN * 2.45)
        late = T("not from a user on Friday night", 26, GREY_B).next_to(soon, DOWN, buff=0.2)
        self.beat("You find out two minutes later, on your own branch, instead of from a user on Friday night. A branch is your own line of work, kept apart from everyone else's.",
                  FadeIn(soon, shift=UP * 0.1), Succession(Wait(2.4), FadeIn(late)), run_time=3.4)
        self.beat("Remember the tasting we skipped on Tuesday? This is that tasting, done by a machine, every single time.",
                  Indicate(S[2][1], color=RED_M), run_time=1.6)
        rule = T("each step catches its own mistake, close to where it was made", 28, YELLOW_M).move_to(DOWN * 2.6)
        self.beat("And every step catches a different kind of mistake, as close as possible to where it was made.",
                  FadeOut(VGroup(soon, late, diff)), FadeIn(rule, shift=UP * 0.1), run_time=2.0)
        ok = tick(True, 0.22).move_to(cross)
        self.beat("Fix the test, push again, and the change moves on.",
                  ReplacementTransform(cross, ok), S[2][0].animate.set_stroke(GOLD_M, width=3),
                  Succession(Wait(0.6), *[travel(A[i], YELLOW_M, 0.3) for i in range(2, 8)]), run_time=3.0)
        self.play(FadeOut(ok), FadeOut(rule), run_time=0.4)

        # ---------- 8. name: CI/CD
        ci = [S[i] for i in range(1, 6)]
        cil = T("CI/CD: steps 2 to 6", 30, GOLD_M).move_to(UP * 0.45)
        self.beat("Steps two to six have a name you will see everywhere: CI/CD.",
                  *[s[0].animate.set_stroke(width=6) for s in ci], FadeIn(cil), run_time=1.6)
        cit = T("continuous integration: small changes, often, each one built and tested", 26, GREY_B).move_to(DOWN * 2.35)
        cdt = T("continuous delivery: every change that passes is ready to release", 26, GREY_B).next_to(cit, DOWN, buff=0.25)
        fit(VGroup(cit, cdt), 12.6)
        self.beat("Continuous integration means you add small changes to the shared code often, and a machine builds and tests each one.",
                  FadeIn(cit, shift=UP * 0.1), run_time=1.6)
        self.beat("Continuous delivery means every change that passes is ready to release, at any time. You build both in Part 6.",
                  FadeIn(cdt, shift=UP * 0.1), run_time=1.6)
        self.play(*[s[0].animate.set_stroke(width=3) for s in ci], FadeOut(VGroup(cit, cdt, cil)), run_time=0.6)

        # ---------- 9. guardrails
        p1 = T("deciding what to change: a person", 28, BLUE_M).move_to(UP * 0.62)
        p2 = T("building, testing, shipping: a machine", 28, GOLD_M).next_to(p1, DOWN, buff=0.22)
        self.beat("So, should a machine do everything? No. Deciding what to change takes a person. Building, testing and shipping do not.",
                  Succession(Wait(2.4), FadeIn(p1, shift=UP * 0.1), Wait(0.8), FadeIn(p2, shift=UP * 0.1)), run_time=4.2)
        r1 = T("When a step goes the same way every time, give it to a machine.", 28, YELLOW_M).move_to(DOWN * 2.55)
        self.beat("When a step goes the same way every time, give it to a machine.", FadeIn(r1, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(p1, p2, r1)), run_time=0.5)

        chs = VGroup(chip("flour", GOLD_M, 26), chip("oven", GOLD_M, 26), chip("time", GOLD_M, 26)).arrange(RIGHT, buff=0.35).move_to(LEFT * 1.6 + UP * 0.45)
        dry = VGroup(loaf(0.8), T("dry", 26, RED_M)).arrange(RIGHT, buff=0.25).next_to(chs, RIGHT, buff=0.9)
        qm = T("which one?", 28, RED_M).move_to(DOWN * 2.45)
        self.beat("One more guardrail. Say you change the flour, the oven setting and the baking time, all on the same day. The bread comes out dry.",
                  LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in chs], lag_ratio=0.5), Succession(Wait(3.6), FadeIn(dry)), run_time=4.6)
        self.beat("Which change did it? You can't tell. A release with 300 changes in it can fail in 300 places.",
                  FadeIn(qm), Succession(Wait(1.0), Wiggle(chs)), run_time=2.6)
        r2 = T("Change one thing at a time, and you will know what broke.", 28, YELLOW_M).move_to(DOWN * 2.45)
        self.beat("So change one thing at a time, and you will know what broke.", FadeOut(qm), FadeIn(r2, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(chs, dry, r2)), run_time=0.5)
        nt = chip("a new tool?", YELLOW_M, size=28).move_to(UP * 0.45)
        self.beat("Every part of this course owns one stretch of this road. When a new tool shows up, come back here and ask which step it owns.",
                  FadeIn(nt, scale=0.9), Succession(Wait(2.6), LaggedStart(*[Indicate(s[0], color=YELLOW_M, scale_factor=1.04) for s in S], lag_ratio=0.15)), run_time=5.0)
        self.play(FadeOut(nt), run_time=0.4)

        # ---------- 10. moral, recap, check
        d1 = T("finished code: the halfway point", 28, GREY_B).move_to(UP * 0.7)
        d2 = T("done: it runs well in production, and you can see it", 28, GREEN_M).next_to(d1, DOWN, buff=0.25)
        self.beat("So, is the job done when the code is written? Not quite. In a DevOps team, finished code is only the halfway point.",
                  FadeIn(d1, shift=UP * 0.1), run_time=2.0)
        self.beat("You are done when the change runs well in production, and you can see that it does.",
                  FadeIn(d2, shift=UP * 0.1), Indicate(S[6][1], color=GREEN_M), Succession(Wait(1.6), Indicate(S[7][1], color=YELLOW_M)), run_time=3.0)
        self.beat("One team owns the whole road. Every step catches its own mistake, close to where it was made. And whatever repeats goes to a machine.",
                  Succession(Wait(3.6), *[travel(a, YELLOW_M, 0.35) for a in A]), run_time=6.4)
        self.play(FadeOut(VGroup(d1, d2)), *[FadeOut(s) for s in S], *[FadeOut(a) for a in A], run_time=0.8)

        cq = T("A script builds the app and runs the tests,", 30).move_to(UP * 1.6)
        cq2 = T("but someone runs it by hand once a week. Best next step?", 30).next_to(cq, DOWN, buff=0.25)
        opts = VGroup(*[T(o, 28, GREY_B) for o in ("keep the script in git", "run it on every push", "write more unit tests", "hire a release manager")])
        opts.arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(cq2, DOWN, buff=0.5)
        self.beat("A quick check before you go. Your team has a script that builds the app and runs the tests, but someone runs it by hand once a week. What is the best next step?",
                  FadeIn(cq), FadeIn(cq2), Succession(Wait(5.0), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3)), run_time=7.4)
        self.countdown(DOWN * 3.0, "pause and think")
        self.beat("Run it on every push. Feedback in minutes beats a tasting once a week.",
                  opts[1].animate.set_color(GREEN_M), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 1], run_time=1.6)
        self.wait(1.2)
