import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


def tint(color, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def panel(w, h, color=GREY_B, sw=2.5, a=0.08):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, a), 1)


def card(lines, color):
    """A resource block: address on top, settings below, in a thin outlined box."""
    rows = VGroup(*[M(l, 20, color if i == 0 else WHITE) for i, l in enumerate(lines)]).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
    r = RoundedRectangle(corner_radius=0.1, width=rows.width + 0.35, height=rows.height + 0.3, stroke_color=color, stroke_width=1.5)
    rows.move_to(r)
    return VGroup(r, rows)


def flash(m, color=YELLOW_M, rt=1.2):
    return ShowPassingFlash(m.copy().set_fill(opacity=0).set_stroke(color, 6), time_width=0.6, run_time=rt)


def image_icon():
    return VGroup(*[Rectangle(width=1.0, height=0.2, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.3), 1)
                    for _ in range(3)]).arrange(UP, buff=0.05)


class D31Plan(VoiceScene):
    def construct(self):
        self.title_card("How Terraform decides what to do", "your files, the state, and the real world")

        # ---- 1. imperative versus declarative
        lp = panel(6.0, 3.6, GREY_B).move_to([-3.55, 0.0, 0])
        rp = panel(6.0, 3.6, BLUE_M).move_to([3.55, 0.0, 0])
        lh = VGroup(T("imperative", 30, GREY_B), T("you list the steps", 24, GREY_B)).arrange(DOWN, buff=0.12).next_to(lp, UP, buff=0.25)
        rh = VGroup(T("declarative", 30, BLUE_M), T("you describe the result", 24, BLUE_M)).arrange(DOWN, buff=0.12).next_to(rp, UP, buff=0.25)
        self.beat("You can tell a computer what you want in two ways.",
                  Create(lp), Create(rp), FadeIn(lh), FadeIn(rh), run_time=1.8)
        steps = VGroup(*[T(f"{i}.  {t}", 28) for i, t in ((1, "pull nginx"), (2, "start a container"), (3, "publish port 8090"))])
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(lp)
        script = T("like a shell script", 22, GREY_B).next_to(lp, DOWN, buff=0.25)
        self.beat("Imperative: you list the steps. Pull nginx, then start a container, then publish port 8090. A shell script works this way.",
                  LaggedStart(*[FadeIn(s, shift=RIGHT * 0.15) for s in steps], lag_ratio=0.5), FadeIn(script), run_time=4.0)
        want = VGroup(T("one nginx container", 28), T("called tf-web", 28), T("on port 8090", 28)).arrange(DOWN, buff=0.35).move_to(rp)
        tool = T("the tool works out the steps", 22, BLUE_M).next_to(rp, DOWN, buff=0.25)
        self.beat("Declarative: you describe the result. There is one nginx container called tf-web, on port 8090. The tool works out the steps.",
                  FadeIn(want, shift=UP * 0.15), FadeIn(tool), run_time=3.0)
        self.beat("Terraform is declarative. Your files describe the desired state: what should exist once Terraform is done.",
                  FadeOut(VGroup(lp, lh, steps, script)), flash(rp, BLUE_M), run_time=2.0)

        # ---- 2. the three pictures
        XF, XS, XW = -4.45, 0.0, 4.45
        colY, colH = 0.72, 3.35
        fpan = panel(4.3, colH, BLUE_M).move_to([XF, colY, 0])
        span = panel(4.0, colH, GOLD_M).move_to([XS, colY, 0])
        wpan = panel(4.3, colH, TEAL_M).move_to([XW, colY, 0])

        def head(title, sub, color, x):
            return VGroup(T(title, 28, color), M(sub, 20, GREY_B)).arrange(DOWN, buff=0.1).move_to([x, 3.05, 0])

        fh = head("your files", "main.tf", BLUE_M, XF)
        sh = head("the state", "terraform.tfstate", GOLD_M, XS)
        wh = head("the real world", "Docker", TEAL_M, XW)
        c1 = card(["docker_image.nginx", 'name = "nginx:1.30-alpine"'], BLUE_M)
        c2 = card(["docker_container.web", 'name = "tf-web"', 'restart = "no"', "external = 8090"], BLUE_M)
        VGroup(c1, c2).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(fpan)
        self.beat("Your files hold that desired state. Here, two resources: an nginx image, and a container called tf-web.",
                  FadeOut(VGroup(rp, rh, want, tool)), Create(fpan), FadeIn(fh),
                  Succession(Wait(0.6), LaggedStart(FadeIn(c1, shift=RIGHT * 0.15), FadeIn(c2, shift=RIGHT * 0.15), lag_ratio=0.5)), run_time=3.2)

        empty = T("(empty)", 26, GREY_B).move_to(span)
        self.beat("How does Terraform know what already exists? It keeps a memory. After every apply, it writes a file called the state. It records each object Terraform made, and that object's real ID.",
                  Create(span), FadeIn(sh), Succession(Wait(2.5), FadeIn(empty)), run_time=4.0)
        none = T("no tf-web yet", 24, GREY_B).move_to(wpan)
        self.beat("And then there is the real world. Terraform asks Docker about every ID in the state.",
                  Create(wpan), FadeIn(wh), FadeIn(none), run_time=2.2)

        pp = panel(13.2, 2.4, YELLOW_M, 2, 0.05).move_to([0, -2.5, 0])
        pt = T("plan", 26, YELLOW_M).move_to(pp.get_corner(UL) + RIGHT * 0.55 + DOWN * 0.32)
        self.beat("Every run lines up these three pictures. The plan is the difference, written as actions.",
                  flash(fpan, BLUE_M), flash(span, GOLD_M), flash(wpan, TEAL_M), Create(pp), FadeIn(pt), run_time=2.4)

        PX = pp.get_left()[0] + 0.5

        def plan_lines(*lines):
            g = VGroup()
            for text, color in lines:
                g.add(M(text, 22, color))
            g.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.72, 0]).align_to([PX, 0, 0], LEFT)
            return g

        # ---- 3. first run: create
        p1 = plan_lines(("+ docker_image.nginx       will be created", GREEN_M), ("+ docker_container.web     will be created", GREEN_M),
                        ("Plan: 2 to add, 0 to change, 0 to destroy.", WHITE))
        self.beat("First run. Both resources are in your files, but not in the state. So the plan says: create them. Plan, 2 to add.",
                  flash(c1[0], GREEN_M), flash(c2[0], GREEN_M), Indicate(empty, color=GOLD_M),
                  Succession(Wait(1.6), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.15) for l in p1], lag_ratio=0.4)), run_time=4.4)

        img = image_icon().move_to([XW - 1.4, colY + 0.85, 0])
        img_l = M("nginx:1.30-alpine", 20).next_to(img, RIGHT, buff=0.3)
        ctr = Circle(radius=0.32, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.3), 1).move_to([XW - 1.4, colY - 0.75, 0])
        ctr_l = VGroup(M("tf-web", 22, TEAL_M), M("port 8090", 20), M("restart:", 20), M('"no"', 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        ctr_l.next_to(ctr, RIGHT, buff=0.3)
        ref = Arrow(ctr.get_top(), img.get_bottom(), buff=0.1, stroke_width=2, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        self.beat("Apply carries out the plan. The image comes first, because the container refers to it.",
                  FadeOut(none), Succession(AnimationGroup(FadeIn(img, shift=DOWN * 0.2), FadeIn(img_l)), Wait(0.3),
                                            AnimationGroup(GrowFromCenter(ctr), FadeIn(ctr_l), GrowArrow(ref))), run_time=3.0)
        s1 = VGroup(M("docker_image.nginx", 20, GOLD_M), M("id = sha256:0e52bd05...", 20))
        s2 = VGroup(M("docker_container.web", 20, GOLD_M), M("id = 9aa5b0956097...", 20))
        for s in (s1, s2):
            s.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        VGroup(s1, s2).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(span)
        self.beat("Then apply writes the result back into the state: each address, with the real ID Docker gave it.",
                  FadeOut(empty), FadeOut(p1), TransformFromCopy(img, s1), TransformFromCopy(ctr, s2), run_time=2.4)

        # ---- 4. second run: no changes
        p2 = plan_lines(("docker_image.nginx: Refreshing state... [id=sha256:0e52bd05...]", GREY_B),
                        ("docker_container.web: Refreshing state... [id=9aa5b0956097...]", GREY_B))
        ask1 = DashedLine(s1.get_right() + RIGHT * 0.1, img.get_left() + LEFT * 0.1, dash_length=0.08, stroke_width=2, color=GOLD_M)
        ask2 = DashedLine(s2.get_right() + RIGHT * 0.1, ctr.get_left() + LEFT * 0.1, dash_length=0.08, stroke_width=2, color=GOLD_M)
        self.beat("Now run plan again, without touching the file. Terraform asks Docker about each ID in its state.",
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.15) for l in p2], lag_ratio=0.4), Create(ask1), Create(ask2), run_time=2.8)
        self.play(travel(Line(ask1.get_start(), ask1.get_end()), GOLD_M), travel(Line(ask2.get_start(), ask2.get_end()), GOLD_M), run_time=0.9)
        ok = VGroup(*[tick(True, 0.2).move_to(m[0].get_corner(UR) + LEFT * 0.32 + DOWN * 0.24) for m in (c1, c2)],
                    *[tick(True, 0.2).next_to(m, RIGHT, buff=0.25) for m in (s1[0], s2[0])],
                    tick(True, 0.2).next_to(img, UL, buff=0.02), tick(True, 0.2).next_to(ctr, UL, buff=0.0))
        nochg = plan_lines(("No changes. Your infrastructure matches the configuration.", TEAL_M))
        self.beat("Docker reports both objects, with the settings your file asks for. All three pictures agree, so the plan is empty.",
                  LaggedStart(*[Create(o) for o in ok], lag_ratio=0.15), Succession(Wait(1.6), AnimationGroup(FadeOut(p2), FadeIn(nochg))), run_time=3.6)
        idem = VGroup(T("idempotent", 30, TEAL_M), T("same result, however many runs", 22, GREY_B)).arrange(DOWN, buff=0.1)
        idem.move_to(pp).align_to(pp, RIGHT).shift(LEFT * 0.4 + UP * 0.35)
        nochg.generate_target(); nochg.target.shift(DOWN * 0.45)
        self.beat("A second docker run would fail, because the name is taken. Terraform gives the same result however many times you run it. That is called idempotent.",
                  MoveToTarget(nochg), Succession(Wait(2.2), FadeIn(idem, shift=UP * 0.1)), run_time=4.2)
        self.play(FadeOut(VGroup(ok, ask1, ask2, idem, nochg)), run_time=0.6)

        # ---- 5. change a setting: update in place
        newr = M('restart = "unless-stopped"', 20, YELLOW_M).move_to(c2[1][2], aligned_edge=LEFT)
        self.beat("Now edit the file. Change restart, from no, to unless-stopped.",
                  Transform(c2[1][2], newr), c2[0].animate.stretch_to_fit_width(c1[0].width).align_to(c1[0], LEFT), run_time=1.6)
        p3 = plan_lines(('~ docker_container.web     restart: "no" -> "unless-stopped"', GOLD_M), ("Plan: 0 to add, 1 to change, 0 to destroy.", WHITE))
        self.beat("The container is in your files and in the state, but with other settings. So the plan says: change it, in place.",
                  flash(c2[0], GOLD_M), flash(SurroundingRectangle(s2, buff=0.12), GOLD_M), Succession(Wait(1.8), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.15) for l in p3], lag_ratio=0.4)),
                  run_time=4.0)
        newc = M('"unless-stopped"', 20, YELLOW_M).move_to(ctr_l[3], aligned_edge=LEFT)
        self.beat("Apply makes the change. The container keeps its ID, and the state is updated.",
                  Transform(ctr_l[3], newc), Indicate(s2[1], color=GOLD_M), FadeOut(p3), run_time=2.2)
        self.play(c2[1][2].animate.set_color(WHITE), ctr_l[3].animate.set_color(WHITE), run_time=0.4)

        # ---- 6. remove a block: delete
        gone = DashedVMobject(c2[0].copy().set_stroke(RED_M, 2), num_dashes=40)
        self.beat("Last, delete the container block from your file.",
                  FadeOut(c2[1], shift=LEFT * 0.2), FadeOut(c2[0]), FadeIn(gone), run_time=1.6)
        p4 = plan_lines(("- docker_container.web     will be destroyed", RED_M), ("Plan: 0 to add, 0 to change, 1 to destroy.", WHITE))
        self.beat("It is still in the state, but gone from your files. So the plan says: delete it.",
                  flash(SurroundingRectangle(s2, buff=0.12), RED_M), Succession(Wait(1.2), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.15) for l in p4], lag_ratio=0.4)), run_time=3.0)
        self.beat("Apply removes the container from Docker, and from the state.",
                  FadeOut(VGroup(ctr, ctr_l, ref), scale=0.5), FadeOut(s2, shift=DOWN * 0.1), FadeOut(gone), FadeOut(p4), run_time=2.2)
        self.wait(0.3)

        # ---- recap
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        rec = VGroup(
            VGroup(T("your files", 32, BLUE_M), T("what you want", 28, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("the state", 32, GOLD_M), T("what Terraform made", 28, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("the real world", 32, TEAL_M), T("what is really there", 28, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("plan", 32, YELLOW_M), T("create, change or delete", 28, GREY_B)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("Your files say what you want. The state remembers what Terraform made. Docker says what is really there. The plan is the difference: create, change or delete. And apply makes it so, then writes it down.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rec], lag_ratio=0.6), run_time=6.0)
        self.wait(1.0)
