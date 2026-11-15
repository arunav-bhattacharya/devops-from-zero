import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bhost_port\b", "host port"), (r"terraform\.workspace", "terraform dot workspace"),
            (r"module\.dev\.url", "module dot dev dot url"), (r"\btfstate\b", "T F state"), (r"\bqa\b", "Q A")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def code(lines, size=22, buff=0.14):
    out = VGroup()
    for t, c in lines:
        if t.startswith(" ") or not t:
            m = M("|" + t, size, c)
            m[0].set_opacity(0)
        else:
            m = M(t, size, c)
        out.add(m)
    return out.arrange(DOWN, aligned_edge=LEFT, buff=buff)


def card(lines, color, size=22, pad=0.3, w=None):
    g = code(lines, size)
    r = RoundedRectangle(corner_radius=0.12, width=w or g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=3)
    r.set_fill(tint(color, 0.12), 1)
    g.move_to(r)
    return VGroup(r, g)


def res(label, color=TEAL_M, w=3.3):
    return mbox(label, color, w=w, h=0.52, size=20)


def doc(label, color=GOLD_M, w=0.62, h=0.78):
    body = Polygon([-w / 2, h / 2, 0], [w / 2 - 0.18, h / 2, 0], [w / 2, h / 2 - 0.18, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0],
                   stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.15), 1)
    rows = VGroup(*[Line(LEFT * (w / 2 - 0.12), RIGHT * (w / 2 - 0.16), stroke_width=2, color=color) for _ in range(3)]).arrange(DOWN, buff=0.13).move_to(body).shift(DOWN * 0.05)
    lab = M(label, 20, color).next_to(body, DOWN, buff=0.12)
    return VGroup(body, rows, lab)


class D34Modules(VoiceScene):
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
        self.title_card("Modules and environments", "write the shape once, call it twice")

        # 1. the problem: copied folders drift apart
        fa = box("infra/local", BLUE_M, w=3.2, h=1.0, size=28).move_to([-3.0, 0.6, 0])
        pa = M("port 8080", 22, GREY_B).next_to(fa, DOWN, buff=0.2)
        self.beat("You have one hello-devops stack, on port 8080. Now you want a second one for testing.",
                  FadeIn(fa), FadeIn(pa), run_time=1.6)
        fb = box("infra/local-copy", BLUE_M, w=3.2, h=1.0, size=28).move_to([3.0, 0.6, 0])
        pb = M("port 8082", 22, GREY_B).next_to(fb, DOWN, buff=0.2)
        cp = Arrow(fa.get_right(), fb.get_left(), buff=0.2, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        cpl = T("copy", 24, GREY_B).next_to(cp, UP, buff=0.12)
        self.beat("Copying the folder works for a week.",
                  GrowArrow(cp), FadeIn(cpl), TransformFromCopy(fa, fb), FadeIn(pb), run_time=1.8)
        fix = chip("fixed", GREEN_M, 22).next_to(fa, UP, buff=0.25)
        old = chip("not fixed", RED_M, 22).next_to(fb, UP, buff=0.25)
        self.beat("Then someone fixes a setting in one copy, and forgets the other. Now every fix has to be made twice.",
                  Succession(AnimationGroup(FadeIn(fix, shift=DOWN * 0.1), fa[0].animate.set_stroke(GREEN_M)), Wait(1.0),
                             AnimationGroup(FadeIn(old, shift=DOWN * 0.1), fb[0].animate.set_stroke(RED_M))), run_time=3.0)
        self.play(FadeOut(VGroup(fa, pa, fb, pb, cp, cpl, fix, old)), run_time=0.6)

        # 2. one module, two calls
        mod = card([("hello-stack", GOLD_M), ("", WHITE), ('"${var.name}-net"', WHITE), ('"${var.name}-redis"', WHITE),
                    ('"${var.name}-web"', WHITE), ("port: var.host_port", WHITE)], GOLD_M, size=20, pad=0.28)
        mod.move_to([0.45, 0.2, 0])
        mlab = T("child module: one folder", 22, GOLD_M).next_to(mod, UP, buff=0.2)
        self.beat("A module is a folder of .tf files. You write the shape of the stack once, in a folder called hello-stack.",
                  Create(mod[0]), FadeIn(mod[1][0]), FadeIn(mlab), run_time=2.2)
        self.beat("Every name inside it is built from an input, var.name. So is the port.",
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in mod[1][2:]], lag_ratio=0.3), run_time=2.2)

        dev = card([('module "dev"', BLUE_M), ('  name = "hello"', WHITE), ("  host_port = 8080", WHITE)], BLUE_M, size=20, w=3.5).move_to([-4.3, 1.55, 0])
        tst = card([('module "test"', PURPLE_M), ('  name = "hello-test"', WHITE), ("  host_port = 8082", WHITE)], PURPLE_M, size=20, w=3.5).move_to([-4.3, -1.15, 0])
        root = DashedVMobject(RoundedRectangle(corner_radius=0.15, width=3.8, height=5.3, stroke_color=GREY_B, stroke_width=2), num_dashes=60).move_to([-4.3, 0.2, 0])
        rlab = T("infra/local: the root", 22, GREY_B).next_to(root, UP, buff=0.12)
        self.beat("The folder where you run terraform is the root module. It calls hello-stack with a module block.",
                  Create(root), FadeIn(rlab), FadeIn(dev), run_time=2.4)
        self.beat("And it can call it again, with a different name and port.",
                  FadeIn(tst, shift=UP * 0.15), run_time=1.4)

        a_dm = Arrow(dev.get_right(), mod.get_left() + UP * 0.6, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        a_tm = Arrow(tst.get_right(), mod.get_left() + DOWN * 0.6, buff=0.12, stroke_width=3, color=PURPLE_M, max_tip_length_to_length_ratio=0.12)
        SX = 4.95
        dstack = VGroup(res("hello-net", BLUE_M), res("hello-redis", BLUE_M), res("hello-web :8080", BLUE_M)).arrange(DOWN, buff=0.14).move_to([SX, 1.55, 0])
        tstack = VGroup(res("hello-test-net", PURPLE_M), res("hello-test-redis", PURPLE_M), res("hello-test-web :8082", PURPLE_M)).arrange(DOWN, buff=0.14).move_to([SX, -1.15, 0])
        a_md = Arrow(mod.get_right() + UP * 0.6, dstack.get_left(), buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        a_mt = Arrow(mod.get_right() + DOWN * 0.6, tstack.get_left(), buff=0.12, stroke_width=3, color=PURPLE_M, max_tip_length_to_length_ratio=0.12)
        self.steps("It works like a function. The variables are its parameters. The call dev passes in the name hello, and port 8080.",
                   (1.6, GrowArrow(a_dm)), (1.0, Indicate(dev[1][1:], color=BLUE_M, scale_factor=1.05)), (1.0, travel(a_dm, BLUE_M, 1.0)))
        self.steps("The resources are the side effects. Out come real objects: hello-net, hello-redis and hello-web.",
                   (1.2, GrowArrow(a_md)), (0.8, travel(a_md, BLUE_M, 0.8)),
                   (2.2, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in dstack], lag_ratio=0.35)))
        self.steps("Call it twice, and you get two sets of real objects. The test call makes hello-test-web, on port 8082.",
                   (1.0, GrowArrow(a_tm)), (0.8, travel(a_tm, PURPLE_M, 0.8)), (1.0, GrowArrow(a_mt)), (0.6, travel(a_mt, PURPLE_M, 0.6)),
                   (1.8, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tstack], lag_ratio=0.35)))

        q = T("Docker refuses two containers with the same name. So why no clash?", 24, GREY_B).move_to([0, -3.35, 0])
        self.beat("But wait. Docker refuses two containers with the same name. Why is there no clash?",
                  FadeIn(q, shift=UP * 0.15), run_time=1.6)
        self.beat("Because the module builds every name from var.name. Hello for dev, and hello-test for test.",
                  Indicate(mod[1][2:5], color=GOLD_M, scale_factor=1.05),
                  Succession(Wait(1.6), AnimationGroup(Indicate(dstack[2], color=BLUE_M), Indicate(tstack[2], color=PURPLE_M))), run_time=3.2)
        self.play(FadeOut(q), run_time=0.4)

        # outputs and addresses
        outl = M('module.dev.url = "http://localhost:8080"', 22, BLUE_M).move_to([0, -3.35, 0])
        self.beat("The outputs are its return values. The root reads them as module.dev.url.",
                  Write(outl), Indicate(dev, color=BLUE_M, scale_factor=1.03), run_time=2.2)
        addr = M("module.dev.docker_container.app", 24, YELLOW_M).move_to([SX - 1.1, 3.35, 0])
        self.beat("Here is the difference from a function. A function call is gone once it returns. A module call lives on in the state.",
                  Circumscribe(VGroup(dstack, tstack), color=YELLOW_M, buff=0.15), run_time=2.6)
        self.beat("Its resources get addresses with a module prefix, such as module.dev.docker_container.app. They stay until you remove the call.",
                  FadeIn(addr, shift=DOWN * 0.15), Succession(Wait(2.4), Indicate(dstack[2], color=YELLOW_M)), run_time=3.4)

        # one fix reaches both
        self.beat("Now the fix from before. You make it once, in the module.",
                  FadeOut(addr), FadeOut(outl), mod[0].animate.set_stroke(GREEN_M, 5), run_time=1.4)
        self.steps("And every stack that calls it changes on its next apply. Nothing drifts apart.",
                   (0.9, travel(a_md, GREEN_M, 0.9), travel(a_mt, GREEN_M, 0.9)),
                   (1.0, *[r[0].animate.set_stroke(GREEN_M) for r in dstack], *[r[0].animate.set_stroke(GREEN_M) for r in tstack]))
        self.play(FadeOut(VGroup(mod, mlab, dev, tst, root, rlab, a_dm, a_tm, a_md, a_mt, dstack, tstack)), run_time=0.7)

        # 3. environments: a folder each
        self.beat("Dev, test and prod need the same shape, with small differences. One clean way is one folder per environment.",
                  run_time=None)
        site = box("modules/site", GOLD_M, w=3.0, h=0.85, size=26).move_to([0, 2.4, 0])
        ed = card([("envs/dev", BLUE_M), ('name = "site-dev"', WHITE), ("port = 8201", WHITE)], BLUE_M, size=20, w=3.4).move_to([-3.6, -0.1, 0])
        ep = card([("envs/prod", RED_M), ("port = 8202", WHITE), ('message = "Hello from prod"', WHITE)], RED_M, size=20, w=4.4).move_to([3.6, -0.1, 0])
        ad = edge_arrow(ed, site, BLUE_M); ap = edge_arrow(ep, site, RED_M)
        self.beat("Each one is a short root. A provider, and one call to the shared module. Only the arguments differ.",
                  FadeIn(site), FadeIn(ed), FadeIn(ep), Succession(Wait(1.0), AnimationGroup(GrowArrow(ad), GrowArrow(ap))), run_time=3.0)
        sd = doc("terraform.tfstate", BLUE_M).next_to(ed, DOWN, buff=0.35)
        sp = doc("terraform.tfstate", RED_M).next_to(ep, DOWN, buff=0.35)
        wall = DashedLine([0, 0.9, 0], [0, -3.4, 0], dash_length=0.12, stroke_width=2.5, color=GREY_B)
        self.beat("Each folder has its own state file. So a prod apply has no way to touch dev.",
                  FadeIn(sd, shift=UP * 0.1), FadeIn(sp, shift=UP * 0.1), Succession(Wait(1.6), Create(wall)), run_time=2.8)

        # workspace: same folder, second empty state
        self.play(ep.animate.set_opacity(0.25), sp.animate.set_opacity(0.25), ap.animate.set_opacity(0.25), run_time=0.5)
        wcmd = M("terraform workspace new qa", 22, YELLOW_M).move_to([-4.4, 2.4, 0])
        sq = doc("qa: empty", YELLOW_M).next_to(sd, RIGHT, buff=0.6)
        self.beat("Compare a workspace. In envs/dev, run terraform workspace new qa. Terraform switches to a second, empty state.",
                  FadeIn(wcmd, shift=DOWN * 0.1), Succession(Wait(2.4), FadeIn(sq, shift=LEFT * 0.15)), run_time=3.4)
        pl = VGroup(M("plan: create site-dev on 8201", 22, YELLOW_M), M("already taken", 22, RED_M)).arrange(DOWN, buff=0.15).move_to([-3.3, -3.05, 0])
        self.beat("An empty state means nothing exists yet. So the plan wants to create everything again, with the same name site-dev, and port 8201.",
                  Indicate(sq, color=YELLOW_M), FadeIn(pl[0], shift=LEFT * 0.15), run_time=3.0)
        self.beat("Dev already uses both. Applying would fail, because the code does not use the workspace name anywhere.",
                  FadeIn(pl[1], shift=UP * 0.1), Indicate(ed[1][1:], color=RED_M, scale_factor=1.05), run_time=2.4)
        fixw = M('name = "site-${terraform.workspace}"', 22, GREEN_M).move_to(pl)
        self.beat("If you use workspaces, build names from terraform.workspace.",
                  FadeOut(pl), FadeIn(fixw), run_time=1.6)
        note = T("workspaces share one backend", 26, YELLOW_M).move_to([3.3, -3.2, 0])
        self.beat("But workspaces share one backend. HashiCorp's docs say that makes them unsuitable when environments need separate credentials. So most teams use a folder per long-lived environment.",
                  FadeIn(note, shift=UP * 0.1), Succession(Wait(4.0), AnimationGroup(ep.animate.set_opacity(1), sp.animate.set_opacity(1), ap.animate.set_opacity(1))), run_time=5.0)
        self.play(FadeOut(VGroup(site, ed, ep, ad, ap, sd, sp, wall, wcmd, sq, fixw, note)), run_time=0.7)

        # 4. recap
        rcp = VGroup(T("a module: a folder you call with inputs", 30, GOLD_M),
                     T("each call makes its own real objects", 30, BLUE_M),
                     T("outputs hand values back to the root", 30, TEAL_M),
                     T("a folder, and a state, per environment", 30, RED_M)).arrange(DOWN, buff=0.4)
        self.beat("A module is a folder you call with inputs. Each call makes its own real objects, and hands values back through outputs. And each long-lived environment gets its own folder, and its own state.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.6), run_time=6.0)
        self.wait(1.0)
