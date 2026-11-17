import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\btfvars\b", "T F vars"), (r"\btfstate\b", "T F state"), (r"\bqa\b", "Q A"), (r"\bhello-stack\b", "hello stack"),
            (r"\bmodule\.dev\b", "module dot dev"), (r"\bmodule\.test\b", "module dot test")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(w, h, color, k=0.08, sw=2.5):
    return RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, k), opacity=1)


def house(color, s=1.0):
    walls = Rectangle(width=1.6, height=1.1, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.22), opacity=1)
    roof = Polygon(walls.get_corner(UL) + LEFT * 0.15, walls.get_corner(UR) + RIGHT * 0.15, walls.get_top() + UP * 0.6,
                   stroke_color=color, stroke_width=3).set_fill(tint(color, 0.32), opacity=1)
    door = Rectangle(width=0.32, height=0.55, stroke_color=color, stroke_width=2).move_to(walls.get_bottom() + UP * 0.275)
    return VGroup(walls, roof, door).scale(s)


def drip(at):
    return VGroup(*[Dot(radius=0.06, color=BLUE_M).move_to(at + DOWN * 0.22 * i) for i in range(3)])


class D34OnePlan(VoiceScene):
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
        self.title_card("Fix the tap once", "one module, two stacks, and a book for each")

        # 1. two houses from copied drawings  [FAMILIAR, PAIN]
        HL, HR = [-3.6, -1.0, 0], [3.6, -1.0, 0]
        h1 = house(TEAL_M).move_to(HL)
        h2 = house(GREEN_M).move_to(HR)
        l1 = T("show home", 26, TEAL_M).next_to(h1, DOWN, buff=0.25)
        l2 = T("family home", 26, GREEN_M).next_to(h2, DOWN, buff=0.25)
        d1 = panel(3.1, 1.2, GREY_B, 0.05).move_to([-3.6, 2.2, 0])
        d2 = panel(3.1, 1.2, GREY_B, 0.05).move_to([3.6, 2.2, 0])
        dt1 = T("drawing", 26, GREY_B).move_to(d1)
        dt2 = T("copy of the drawing", 24, GREY_B).move_to(d2)
        self.beat("A builder puts up the same small house twice. One is a show home that visitors poke around in. The other is where a family will really live.",
                  FadeIn(h1, shift=UP * 0.1), FadeIn(l1), Succession(Wait(1.6), AnimationGroup(FadeIn(h2, shift=UP * 0.1), FadeIn(l2))), run_time=3.6)
        a1 = Arrow(d1.get_bottom(), h1.get_top(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        a2 = Arrow(d2.get_bottom(), h2.get_top(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("The architect copies the drawing for the second plot. For a while, all is well.",
                  Create(d1), FadeIn(dt1), GrowArrow(a1), Succession(Wait(1.0), AnimationGroup(TransformFromCopy(d1, d2), FadeIn(dt2), GrowArrow(a2))), run_time=2.8)
        dr1 = drip(h1[0].get_right() + LEFT * 0.35 + DOWN * 0.1)
        fix = T("tap fixed", 24, GREEN_M).next_to(d1, DOWN, buff=0.1).shift(RIGHT * 1.7)
        self.steps("Then a tap in the show home drips. The architect fixes the show home's drawing,",
                   (0.8, FadeIn(dr1, lag_ratio=0.3)), (1.4, Wait(1.4)), (0.6, Indicate(d1, color=GREEN_M, scale_factor=1.04)), (0.6, FadeOut(dr1)))
        dr2 = drip(h2[0].get_right() + LEFT * 0.35 + DOWN * 0.1)
        self.steps("and forgets the family's copy. A month later, the family's tap drips too, and nobody can say why the two houses differ.",
                   (1.6, Wait(1.6)), (0.8, FadeIn(dr2, lag_ratio=0.3)), (0.8, Indicate(dt2, color=RED_M)))
        self.beat("Copies only stay the same if every change is made twice. And people forget.", run_time=None)
        self.play(FadeOut(VGroup(d1, d2, dt1, dt2, a1, a2, dr2)), run_time=0.5)

        # 2. one standard plan with options  [WISH, ANALOGY, MAP]
        mp = panel(5.0, 1.5, BLUE_M, 0.1, 3).move_to([0, 2.3, 0])
        ml = M("modules/hello-stack", 24, BLUE_M).move_to(mp.get_center() + UP * 0.3)
        mi = T("options in, answers out", 24, GREY_B).move_to(mp.get_center() + DOWN * 0.3)
        self.beat("Wouldn't it be nice to keep one drawing, and just fill in a few options per plot? Builders call that a standard house plan. Terraform calls it a module.",
                  Create(mp), FadeIn(ml), run_time=3.0)
        self.beat("A module is simply a folder of Terraform files. You have written modules since the first lesson without knowing it. The folder where you run terraform is the root module.",
                  Indicate(ml, color=BLUE_M), run_time=3.0)
        self.beat("When the root uses another folder through a module block, that folder becomes a child module. Its variables are the options each buyer picks. Its outputs are what the builder hands back.",
                  FadeIn(mi), run_time=3.2)

        # 3. two calls, two stacks  [SHOW]
        call_d = VGroup(M('module "dev" {', 22, TEAL_M), M('  name      = "hello"', 22), M("  host_port = 8080", 22), M("}", 22, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        call_t = VGroup(M('module "test" {', 22, GREEN_M), M('  name      = "hello-test"', 22), M("  host_port = 8082", 22), M("}", 22, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        call_d.move_to([-3.6, 0.35, 0]); call_t.move_to([3.6, 0.35, 0])
        self.play(h1.animate.shift(DOWN * 0.9), l1.animate.shift(DOWN * 0.9), h2.animate.shift(DOWN * 0.9), l2.animate.shift(DOWN * 0.9), run_time=0.6)
        ad = Arrow(mp.get_bottom() + LEFT * 1.4, call_d.get_top() + RIGHT * 0.4, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.15)
        at = Arrow(mp.get_bottom() + RIGHT * 1.4, call_t.get_top() + LEFT * 0.4, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.15)
        self.beat("In the lab, the infra/local root calls the hello-stack module twice. Once called dev, with the name hello and port 8080.",
                  GrowArrow(ad), FadeIn(call_d), run_time=2.6)
        self.beat("And once called test, with the name hello-test and port 8082. Same plan, two plots.", GrowArrow(at), FadeIn(call_t), run_time=2.4)
        n1 = M("hello-web", 24, TEAL_M).move_to([-3.6, -0.8, 0])
        n2 = M("hello-test-web", 24, GREEN_M).move_to([3.6, -0.8, 0])
        self.beat("Every name inside the module is built from the name option. So Docker gets hello-web and hello-test-web, two containers that never clash.",
                  FadeIn(n1), FadeIn(n2), run_time=2.6)
        ad1 = M("module.dev.docker_container.app", 22, TEAL_M).move_to([-3.4, -0.8, 0])
        ad2 = M("module.test.docker_container.app", 22, GREEN_M).move_to([3.4, -0.8, 0])
        self.play(FadeOut(n1), FadeOut(n2), run_time=0.3)
        self.beat("In the state, each call's resources get a module prefix. module.dev, docker_container.app. module.test, docker_container.app.",
                  FadeIn(ad1), Succession(Wait(1.4), FadeIn(ad2)), run_time=3.0)

        # 4. predict: fix it once  [PREDICT, PAUSE, SHOW]
        self.play(FadeOut(ad1), FadeOut(ad2), run_time=0.3)
        dr3 = drip(h1[0].get_right() + LEFT * 0.35 + DOWN * 0.1)
        self.beat("Now the tap drips again, in the show home. You fix it inside the module, once.",
                  FadeIn(dr3, lag_ratio=0.3), Succession(Wait(1.6), Indicate(ml, color=BLUE_M)), run_time=2.8)
        q = T("one fix in the module. How many stacks change?", 28, YELLOW_M).move_to([0, -0.6, 0])
        self.beat("How many stacks change on their next apply?", FadeIn(q), run_time=1.4)
        self.guess([0, -1.3, 0])
        self.steps("Both. Change a module, and every stack that uses it changes on its next apply. The family's tap gets fixed too, and nobody had to remember.",
                   (0.6, FadeOut(q)), (0.9, travel(ad, BLUE_M, 0.9), travel(at, BLUE_M, 0.9)), (0.6, FadeOut(dr3)),
                   (0.8, Indicate(h1, color=TEAL_M), Indicate(h2, color=GREEN_M)))
        self.beat("That is the one way a module differs from a paper plan. Paper never reaches back into a house already built. A module does, and that is the whole point.",
                  run_time=None)
        self.play(FadeOut(VGroup(ad, at, call_d, call_t)), run_time=0.5)

        # 5. where each house keeps its book  [QUESTION, BREAK]
        q2 = T("but where does each environment keep its book?", 28, YELLOW_M).move_to([0, 0.35, 0])
        self.play(FadeOut(VGroup(h1, h2, l1, l2)), run_time=0.5)
        self.beat("Now a real team has a dev environment and a prod environment, the real one your users depend on. Remember the state, Terraform's book? Where does each one keep it?",
                  FadeIn(q2), run_time=3.2)
        ws = VGroup(M("envs/dev", 24, TEAL_M), M("terraform workspace new qa", 22, GREY_B)).arrange(DOWN, buff=0.15).move_to([0, 0.35, 0])
        self.beat("The tempting shortcut is a workspace. Say a folder called envs/dev runs one small site, site-dev, on port 8201. In that folder, terraform workspace new qa gives the same code a second, empty book.",
                  FadeOut(q2), FadeIn(ws), run_time=3.0)
        pl = VGroup(M("+ module.site.docker_container.site", 22, GREEN_M), M('  name = "site-dev", port 8201', 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        pl.move_to([0, -0.85, 0])
        q3 = T("plan in qa: what happens?", 26, YELLOW_M).next_to(pl, DOWN, buff=0.3)
        self.beat("The book is empty, so the plan wants to create everything again. Read the names. Will it work?", FadeIn(pl), FadeIn(q3), run_time=2.4)
        self.guess([0, -2.25, 0])
        fail = T("no: site-dev and port 8201 are already taken by dev", 26, RED_M).move_to(q3)
        fit(fail, 12.0)
        self.beat("No. It plans the same name, site-dev, and the same port, 8201, that dev already uses. Applying would fail, because the code never uses the workspace name.",
                  Transform(q3, fail), run_time=3.0)
        self.beat("And there is a deeper reason. Workspaces share one backend, the place the book is kept. HashiCorp's docs call that unsuitable when environments need different credentials and access rules.",
                  Indicate(ws[1], color=RED_M), run_time=3.4)
        self.beat("The show home's keys should not open the family's front door.", run_time=None)
        self.play(FadeOut(VGroup(ws, pl, q3)), run_time=0.5)

        # 6. a folder per environment  [NAME]
        fd = panel(3.6, 1.3, TEAL_M, 0.1).move_to([-3.6, 0.35, 0])
        fp = panel(3.6, 1.3, GREEN_M, 0.1).move_to([3.6, 0.35, 0])
        fdl = VGroup(M("envs/dev", 24, TEAL_M), M("terraform.tfstate", 22, GOLD_M)).arrange(DOWN, buff=0.15).move_to(fd)
        fpl = VGroup(M("envs/prod", 24, GREEN_M), M("terraform.tfstate", 22, GOLD_M)).arrange(DOWN, buff=0.15).move_to(fp)
        l1 = T("dev", 26, TEAL_M).move_to(l1); l2 = T("prod", 26, GREEN_M).move_to(l2)
        self.play(FadeIn(VGroup(h1, h2, l1, l2)), run_time=0.5)
        self.beat("So most teams give each long-lived environment its own folder: envs/dev and envs/prod. Each is a short root that calls the shared module, with its own backend and its own book.",
                  Create(fd), Create(fp), FadeIn(fdl), FadeIn(fpl), run_time=3.4)
        b1 = Arrow(mp.get_bottom() + LEFT * 1.4, fd.get_top() + RIGHT * 0.6, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.15)
        b2 = Arrow(mp.get_bottom() + RIGHT * 1.4, fp.get_top() + LEFT * 0.6, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.15)
        self.beat("One plan, shared. Two books, kept apart. An apply in prod has no way to touch dev.",
                  GrowArrow(b1), GrowArrow(b2), Indicate(fdl[1], color=GOLD_M), Indicate(fpl[1], color=GOLD_M), run_time=2.8)
        self.beat("Workspaces still have a use: short-lived copies, such as one stack per feature branch. Then build names from terraform.workspace, so they never clash.",
                  run_time=None)

        # 7. guardrails  [GUARDRAIL]
        self.play(FadeOut(VGroup(h1, h2, l1, l2)), run_time=0.4)
        g = VGroup(T("run terraform init after adding a module", 26, WHITE),
                   T("pin every module that comes from elsewhere", 26, WHITE),
                   T("keep modules focused and roots thin", 26, WHITE),
                   T("test the module: terraform test, with a mock provider", 26, WHITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([0, -2.1, 0])
        self.beat("A few guardrails. After you add a module block, run terraform init, or plan stops with Module not installed.",
                  FadeIn(g[0], shift=UP * 0.1), run_time=2.6)
        self.beat("Pin every module that comes from elsewhere, because an unpinned one can change your infrastructure on the next init.",
                  FadeIn(g[1], shift=UP * 0.1), run_time=2.6)
        self.beat("Keep modules focused and roots thin: a root sets up providers, calls modules, and connects outputs to inputs.",
                  FadeIn(g[2], shift=UP * 0.1), run_time=2.6)
        self.beat("And since a bug in a shared module now reaches every environment, test it. terraform test with a mock provider creates nothing real, so it is cheap enough for every pull request.",
                  FadeIn(g[3], shift=UP * 0.1), run_time=3.2)
        self.play(FadeOut(g), run_time=0.4)

        # 8. moral and check  [MORAL, RECAP]
        mor = T("Write the shape once. Keep the books apart.", 30, YELLOW_M).move_to([0, -1.6, 0])
        self.beat("So the moral of the story. Write the shape once, as a module, so a fix lands everywhere. And give each environment its own folder, so each keeps its own book.",
                  FadeIn(mor), run_time=3.6)
        self.play(FadeOut(mor), run_time=0.4)
        chk = VGroup(T('quick check: inside the module call named "test" is', 26, YELLOW_M), M('resource "docker_container" "app"', 22, YELLOW_M),
                     T("What is its address in the state?", 26, YELLOW_M)).arrange(DOWN, buff=0.12).move_to([0, -1.6, 0])
        self.beat("A quick check. Inside the module call named test there is a docker_container called app. What is its address in the state?",
                  FadeIn(chk), run_time=2.8)
        self.guess([0, -2.9, 0])
        ans = M("module.test.docker_container.app", 26, GREEN_M).move_to([0, -2.9, 0])
        self.beat("module.test.docker_container.app. The call's name goes in front of the normal address.", FadeIn(ans), run_time=2.4)
        self.wait(1.0)
