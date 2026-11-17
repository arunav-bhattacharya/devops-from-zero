import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\btfstate\b", "T F state"), (r"\bterraform\.tfstate\b", "terraform dot T F state"), (r"\bnginx\b", "engine X"),
            (r"\btf-web\b", "T F web"), (r"-/\+", "minus plus"), (r"\bdocker run\b", "docker run")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(w, h, color, k=0.08, sw=2.5):
    return RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, k), opacity=1)


def chair(color=GREY_B):
    seat = Line(LEFT * 0.16, RIGHT * 0.16, stroke_color=color, stroke_width=3)
    back = Line(seat.get_left(), seat.get_left() + UP * 0.32, stroke_color=color, stroke_width=3)
    l1 = Line(seat.get_left(), seat.get_left() + DOWN * 0.2, stroke_color=color, stroke_width=3)
    l2 = Line(seat.get_right(), seat.get_right() + DOWN * 0.2, stroke_color=color, stroke_width=3)
    return VGroup(seat, back, l1, l2)


class D31ThreePictures(VoiceScene):
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

    def guess(self, where):
        c = chip("pause and guess", YELLOW_M, 24).move_to(where)
        n = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        self.play(FadeIn(c), FadeIn(n), run_time=0.3)
        self.wait(0.85)
        self.play(Transform(n, T("1", 30, YELLOW_M).move_to(n)), run_time=0.15)
        self.wait(0.85)
        self.play(FadeOut(c), FadeOut(n), run_time=0.3)

    def construct(self):
        self.title_card("Run it twice, get one café", "how Terraform decides what to do")

        # 1. the café nobody wrote down  [FAMILIAR, QUESTION]
        room = panel(5.6, 3.0, GREY_B, 0.04).move_to([-2.9, 0.2, 0])
        rl = T("café number one", 26, GREY_B).next_to(room, UP, buff=0.2)
        machine = box("coffee machine", GOLD_M, w=2.6, h=0.7, size=24).move_to(room.get_center() + UP * 0.8 + LEFT * 1.1)
        fridge = box("fridge: 4 degrees", BLUE_M, w=2.6, h=0.7, size=24).move_to(room.get_center() + UP * 0.8 + RIGHT * 1.35)
        chairs = VGroup(*[chair() for _ in range(12)]).arrange(RIGHT, buff=0.18).move_to(room.get_center() + DOWN * 0.7)
        self.beat("A friend opens a small café, and you help her set up. You plug in the coffee machine, set the fridge to four degrees, and line up twelve chairs.",
                  Create(room), FadeIn(rl), FadeIn(machine), FadeIn(fridge), LaggedStart(*[FadeIn(c) for c in chairs], lag_ratio=0.08), run_time=4.0)
        room2 = DashedVMobject(panel(5.6, 3.0, GREY_B, 0.0), num_dashes=60).move_to([3.4, 0.2, 0])
        r2l = T("café number two", 26, GREY_B).next_to(room2, UP, buff=0.2)
        qm = T("?", 72, YELLOW_M).move_to(room2)
        self.beat("Nobody writes any of it down. A year later she opens a second café, exactly the same please. And you stand in the empty room, and can't remember half of it.",
                  Create(room2), FadeIn(r2l), Succession(Wait(2.6), FadeIn(qm, scale=0.6)), run_time=4.2)
        self.play(FadeOut(VGroup(room, rl, machine, fridge, chairs, room2, r2l, qm)), run_time=0.6)

        # 2. the list of steps fails the second time  [PAIN, WISH]
        script = VGroup(M("1. pull the nginx image", 24), M("2. start a container: tf-web", 24), M("3. publish port 8090", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        sp = panel(script.width + 0.6, script.height + 0.55, GREY_B, 0.05).move_to([-2.6, 0.6, 0])
        script.move_to(sp)
        spl = T("a list of steps: a shell script", 26, GREY_B).next_to(sp, UP, buff=0.2)
        self.beat("So we write it down. The first idea is a list of steps, a shell script. On a computer our café is one container, a sealed box running nginx, a program that serves a web page, on port 8090.",
                  FadeIn(spl), Create(sp), LaggedStart(*[FadeIn(s, shift=RIGHT * 0.1) for s in script], lag_ratio=0.4), run_time=4.0)
        run1 = VGroup(T("run 1:", 26), T("works", 26, GREEN_M)).arrange(RIGHT, buff=0.2).move_to([3.6, 1.2, 0])
        run2 = VGroup(T("run 2:", 26), T("fails: the name tf-web is taken", 26, RED_M)).arrange(RIGHT, buff=0.2)
        run2.next_to(run1, DOWN, buff=0.45).align_to(run1, LEFT)
        fit(run2, 6.4)
        self.steps("Run it once. It works. Run it again, and the second run fails, because the name tf-web is already taken.",
                   (0.9, FadeIn(run1)), (1.6, Wait(1.6)), (0.9, FadeIn(run2)))
        self.beat("A list of steps only knows how to start from nothing. It has no idea what is already there. Wouldn't it be nice to describe the finished room, and let a helper work out what is missing?",
                  Indicate(run2[1], color=RED_M), run_time=2.0)
        self.play(FadeOut(VGroup(script, sp, spl, run1, run2)), run_time=0.6)

        # 3. the drawing, the builder and the notebook  [ANALOGY, MAP]
        W, H, Y = 4.0, 2.7, 0.75
        fp = panel(W, H, BLUE_M).move_to([-4.45, Y, 0])
        stp = panel(W, H, GOLD_M).move_to([0, Y, 0])
        wp = panel(W, H, GREEN_M).move_to([4.45, Y, 0])
        fl = T("your files", 28, BLUE_M).next_to(fp, UP, buff=0.18)
        stl = T("the state", 28, GOLD_M).next_to(stp, UP, buff=0.18)
        wl = T("the real world", 28, GREEN_M).next_to(wp, UP, buff=0.18)
        code = VGroup(M('name    = "tf-web"', 22), M('port    = 8090', 22), M('restart = "no"', 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(fp)
        self.beat("That helper is Terraform. Picture an architect's drawing of the house, and a builder who compares the drawing with the house on every visit.",
                  Create(fp), FadeIn(fl), run_time=2.4)
        self.steps("The drawing is your Terraform files. They describe the desired state: one nginx container called tf-web, on port 8090.",
                   (1.2, Wait(1.2)), (1.4, LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in code], lag_ratio=0.4)))
        self.beat("The house is the real world, the containers Docker is actually running. Right now, there are none.",
                  Create(wp), FadeIn(wl), run_time=1.8)
        nb = T("empty", 26, GREY_B).move_to(stp)
        self.beat("And the builder keeps a notebook of everything built so far. That notebook is the state, a file called terraform.tfstate. Today it is empty.",
                  Create(stp), FadeIn(stl), Succession(Wait(2.2), FadeIn(nb)), run_time=3.2)
        bl = T("Terraform, the builder, lines up all three", 26, GREY_B).move_to([0, -1.25, 0])
        self.beat("Every run, the builder lines up these three pictures, and writes down the difference as a list of actions. That list is the plan.",
                  FadeIn(bl), *[Indicate(m, color=c, scale_factor=1.04) for m, c in ((fl, BLUE_M), (stl, GOLD_M), (wl, GREEN_M))], run_time=3.0)

        # 4. first plan, first apply  [SHRINK, SHOW]
        planp = panel(12.6, 1.3, GREY_B, 0.04).move_to([0, -2.65, 0])
        pl = T("plan", 26, GREY_B).move_to(planp.get_left() + RIGHT * 0.55)
        self.play(FadeOut(bl), Create(planp), FadeIn(pl), run_time=0.6)
        p1 = M("+ docker_container.web    create", 26, GREEN_M).move_to(planp)
        self.beat("In the files, but not in the state? Create it. The plan prints a plus.", FadeIn(p1, shift=UP * 0.1), Indicate(code, color=BLUE_M, scale_factor=1.03), run_time=2.2)
        box_c = RoundedRectangle(corner_radius=0.12, width=2.6, height=1.0, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.25), opacity=1).move_to(wp)
        bc = VGroup(M("tf-web :8090", 22), M("id 9aa5b095...", 22, GREY_B)).arrange(DOWN, buff=0.12).move_to(box_c)
        rec = VGroup(M("docker_container.web", 22, GOLD_M), M("id 9aa5b095...", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(stp)
        self.steps("You type terraform apply, and say yes. It also pulls the nginx image first, because the container refers to it. Then Docker starts the container, and gives it an ID.",
                   (2.0, Wait(2.0)), (1.0, GrowFromCenter(box_c)), (0.6, FadeIn(bc)), (0.4, Wait(0.4)))
        self.steps("And the builder writes it in the notebook: this address, docker_container.web, is the container with ID 9aa5b095.",
                   (1.2, FadeOut(nb), TransformFromCopy(bc[1], rec[1])), (0.8, FadeIn(rec[0])), (0.6, Indicate(rec, color=GOLD_M, scale_factor=1.05)))

        # 5. run it again: predict  [PREDICT, PAUSE, SHOW, NAME]
        q = T("apply again, nothing changed. What happens?", 28, YELLOW_M).move_to(planp)
        self.beat("Now the question from the start. You run apply again, without changing anything. Does the builder make a second café?",
                  FadeOut(p1), FadeIn(q), run_time=2.4)
        self.guess([0, -1.4, 0])
        ask = CurvedArrow(stp.get_bottom() + RIGHT * 0.8 + DOWN * 0.08, wp.get_bottom() + LEFT * 0.8 + DOWN * 0.08, angle=np.radians(50), color=GOLD_M, stroke_width=3)
        askp = ArcBetweenPoints(stp.get_bottom() + RIGHT * 0.8 + DOWN * 0.08, wp.get_bottom() + LEFT * 0.8 + DOWN * 0.08, angle=np.radians(50))
        self.steps("Watch. First, Terraform asks Docker about every ID in the notebook. Those are the Refreshing state lines. Is 9aa5b095 still there? Yes, with port 8090.",
                   (0.6, FadeOut(q)), (1.4, Wait(1.4)), (0.6, Create(ask)), (0.8, travel(askp, GOLD_M, 0.8)), (1.4, Wait(1.4)), (0.6, Indicate(box_c, color=GREEN_M)))
        nc = M("No changes. Your infrastructure matches the configuration.", 24, GREY_B).move_to(planp)
        fit(nc, 11.0)
        self.beat("Files, notebook and world all agree. So the plan is empty. No changes.", FadeIn(nc), run_time=1.8)
        names = VGroup(T("declarative: you describe the result", 26, BLUE_M), T("idempotent: a second run changes nothing", 26, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([0, -1.3, 0])
        self.play(FadeOut(nc), run_time=0.3)
        self.beat("Now we can name what we just saw. Describing the result instead of the steps is called declarative. And a command that gives the same result however many times you run it is called idempotent.",
                  LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in names], lag_ratio=1.2), run_time=4.2)
        self.play(FadeOut(names), FadeOut(ask), run_time=0.5)

        # 6. a change in place  [SHOW]
        self.beat("The second rule of the plan: an object in both the files and the state, but with other settings? Change it.", run_time=None)
        code_r = M('restart = "unless-stopped"', 22).move_to(code[2], aligned_edge=LEFT)
        p2 = M('~ restart = "no" -> "unless-stopped"', 24, YELLOW_M).move_to(planp.get_center() + UP * 0.22)
        s2 = M("Plan: 0 to add, 1 to change, 0 to destroy.", 22, GREY_B).move_to(planp.get_center() + DOWN * 0.3)
        self.steps("Change restart from no to unless-stopped. Docker can change that on a running container. So the plan shows a tilde: update in place. Same container, same ID.",
                   (1.0, Transform(code[2], code_r)), (1.4, Wait(1.4)), (0.8, FadeIn(p2), FadeIn(s2)), (1.6, Wait(1.6)), (0.8, Indicate(bc[1], color=GREY_B)))

        # 7. break it: a one-word edit replaces the object  [PREDICT, BREAK]
        self.play(FadeOut(p2), FadeOut(s2), run_time=0.4)
        code_p = M('port    = 8091', 22).move_to(code[1], aligned_edge=LEFT)
        self.beat("So far so good. Now one more tiny edit. Change the port, 8090 to 8091. One word, again. Another tilde?",
                  Transform(code[1], code_p), run_time=2.2)
        self.guess([0, -1.4, 0])
        p3 = M("-/+ external = 8090 -> 8091  # forces replacement", 24, RED_M).move_to(planp.get_center() + UP * 0.22)
        fit(p3, 11.0)
        s3 = M("Plan: 1 to add, 0 to change, 1 to destroy.", 22, GREY_B).move_to(planp.get_center() + DOWN * 0.3)
        self.steps("No. Docker cannot move a running container to a new port. So the plan says minus plus: replace. Destroy the old one, create a new one. And the line ends with forces replacement.",
                   (1.4, Wait(1.4)), (1.0, FadeIn(p3), FadeIn(s3)), (1.6, Wait(1.6)), (0.8, Indicate(p3[-18:], color=RED_M)))
        box_c2 = box_c.copy()
        bc2 = VGroup(M("tf-web :8091", 22), M("id b848c226...", 22, GREY_B)).arrange(DOWN, buff=0.12).move_to(box_c)
        rec2 = VGroup(M("docker_container.web", 22, GOLD_M), M("id b848c226...", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(stp)
        self.steps("Apply, and the container comes back with a new ID. For nginx, that is a second of downtime. For a database, it can mean an empty database.",
                   (0.8, FadeOut(box_c), FadeOut(bc)), (0.9, FadeIn(box_c2), FadeIn(bc2), Transform(rec, rec2)), (2.4, Wait(2.4)))
        self.beat("Well... that was a lot of building for one changed number.", run_time=None)

        # 8. guardrails  [GUARDRAIL]
        self.play(FadeOut(p3), FadeOut(s3), run_time=0.4)
        sym = VGroup(M("+  create", 24, GREEN_M), M("~  update in place", 24, YELLOW_M), M("-/+  replace", 24, RED_M), M("-  destroy", 24, RED_M)).arrange(RIGHT, buff=0.6).move_to(planp)
        fit(sym, 11.4)
        self.beat("So learn the four symbols. Plus creates. Tilde updates in place. Minus plus replaces. And minus alone destroys.",
                  LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in sym], lag_ratio=0.5), run_time=3.4)
        rule = T("Read the plan before you type yes.", 30, YELLOW_M).move_to([0, -1.35, 0])
        self.beat("And build one habit while the containers are toys. Read the summary line, and search the plan for forces replacement. If the numbers surprise you, stop and find out why.",
                  Write(rule), run_time=2.6)
        self.play(FadeOut(rule), run_time=0.4)
        lim = T("the builder only comes when called", 28, GREY_B).move_to([0, -1.35, 0])
        self.beat("One honest limit of the picture. This builder only comes when called. Terraform looks only when you run plan or apply, so a change made by hand stays until your next run.",
                  FadeIn(lim), run_time=2.6)
        self.play(FadeOut(lim), FadeOut(sym), run_time=0.5)

        # 9. moral and check  [MORAL, RECAP]
        mor = T("files  vs  notebook  vs  world  =  the plan", 30, WHITE).move_to(planp)
        self.beat("So the moral of the story. Write the finished room down, not the steps. Terraform compares your files, its notebook and the real world, and the difference is the plan. That is why running it twice gives you one café, not two.",
                  FadeIn(mor), *[Indicate(m, color=c, scale_factor=1.04) for m, c in ((fl, BLUE_M), (stl, GOLD_M), (wl, GREEN_M))], run_time=5.0)
        self.play(FadeOut(mor), run_time=0.4)
        chk = T("quick check: a teammate deletes tf-web by hand. You run plan. What does it show?", 26, YELLOW_M).move_to(planp)
        fit(chk, 12.0)
        self.beat("A quick check. A teammate deletes the tf-web container by hand. You run plan, without changing any file. What does the plan show?",
                  FadeIn(chk), FadeOut(box_c2), FadeOut(bc2), run_time=2.6)
        self.guess([0, -1.4, 0])
        ans = M("+ docker_container.web    create", 26, GREEN_M).move_to(planp)
        self.beat("A create. The refresh asks Docker about the ID in the notebook, Docker says it is gone, and the drawing still asks for it.",
                  FadeOut(chk), FadeIn(ans), travel(askp, GOLD_M, 1.0), run_time=2.6)
        self.wait(1.0)
