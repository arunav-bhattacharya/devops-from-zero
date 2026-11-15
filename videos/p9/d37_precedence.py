import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bgroup_vars\b", "group vars"), (r"\bhost_vars\b", "host vars"), (r"\bhello_devops_greeting\b", "hello devops greeting"),
            (r"\bweb1\b", "web one"), (r"\bweb2\b", "web two"), (r"\bJinja2\b", "jinja two"), (r"\s-e\b", " dash E"),
            (r"\bvars/", "vars folder"), (r"\bdefaults/", "defaults folder")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


LEVELS = [("role defaults", GREEN_M), ("group_vars/all", TEAL_M), ("group_vars/web", TEAL_M), ("host_vars/web2", TEAL_M),
          ("play vars:", BLUE_M), ("role vars", PURPLE_M), ("-e extra vars", GOLD_M)]


class D37Precedence(VoiceScene):
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
        self.title_card("Which value wins?", "Ansible variables, from role defaults to -e")

        # hosts on the right
        HX = 4.3

        def host(name, y, x=HX, w=4.4):
            r = RoundedRectangle(corner_radius=0.14, width=w, height=1.55, stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.08), 1).move_to([x, y, 0])
            n = M(name, 26, WHITE).move_to(r.get_top() + DOWN * 0.35).align_to(r, LEFT).shift(RIGHT * 0.3)
            g = M("greeting:", 20, GREY_B).next_to(n, RIGHT, buff=0.4)
            return VGroup(r, n, g)

        web1, web2 = host("web1", 1.25), host("web2", -1.25)

        def val(text, h, color=WHITE):
            return M(text, 20, color).move_to(h[0].get_center() + DOWN * 0.3)

        v1, v2 = val("(none)", web1, GREY_B), val("(none)", web2, GREY_B)
        self.beat("Two web servers run the same playbook. Each needs a greeting, and the two should be allowed to differ a little.",
                  LaggedStart(FadeIn(web1), FadeIn(web2), lag_ratio=0.3), FadeIn(v1), FadeIn(v2), run_time=2.4)

        # the ladder
        X0, Y0, DY = -4.4, -2.7, 0.88
        rungs = VGroup()
        for i, (name, c) in enumerate(LEVELS):
            r = RoundedRectangle(corner_radius=0.1, width=2.9, height=0.62, stroke_color=c, stroke_width=2.5).set_fill(tint(c, 0.12), 1)
            rungs.add(VGroup(r, M(name, 20, WHITE).move_to(r)).move_to([X0, Y0 + i * DY, 0]))
        up = Arrow([-6.4, Y0 - 0.3, 0], [-6.4, Y0 + 6 * DY + 0.3, 0], buff=0, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.05)
        weak = T("weakest", 22, GREY_B).next_to(rungs[0], DOWN, buff=0.2).align_to(rungs[0], LEFT).shift(LEFT * 0.4)
        strong = T("strongest", 22, GOLD_M).next_to(rungs[6], UP, buff=0.18).align_to(rungs[6], LEFT).shift(LEFT * 0.4)
        self.beat("But a variable can be set in many places. The docs list 22 levels. In practice you need seven, from weakest to strongest.",
                  GrowArrow(up), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rungs], lag_ratio=0.15), FadeIn(weak), FadeIn(strong), run_time=4.0)
        self.play(rungs.animate.set_opacity(0.5), run_time=0.4)

        def put(i, text, color=WHITE):
            return M(text, 20, color).next_to(rungs[i], RIGHT, buff=0.25)

        def on(i):
            return rungs[i].animate.set_opacity(1)

        V = {1: v1, 2: v2}
        H = {1: web1, 2: web2}

        def setv(k, text, color, src=None):
            new = val(text, H[k], color)
            old = V[k]; V[k] = new
            if src is None:
                return AnimationGroup(FadeOut(old), FadeIn(new))
            return AnimationGroup(FadeOut(old), TransformFromCopy(src, new, path_arc=-0.4))

        # 1. role defaults
        d = put(0, '"Hello, DevOps!"', GREEN_M)
        self.steps("Start at the bottom. The role's defaults file says: Hello, DevOps! That is only the author's suggestion, so it is the weakest.",
                   (1.0, on(0), FadeIn(d, shift=RIGHT * 0.1)), (1.8, Wait(1.8)),
                   (1.6, setv(1, "Hello, DevOps!", GREEN_M, d), setv(2, "Hello, DevOps!", GREEN_M, d)))

        # 2. group_vars/web
        g = put(2, '"Hello from Ansible"', TEAL_M)
        self.steps("Next, the inventory. The file group_vars/web/vars.yml sets the greeting for the whole web group: Hello from Ansible.",
                   (1.0, on(2), FadeIn(g, shift=RIGHT * 0.1)), (1.6, Wait(1.6)),
                   (1.6, d.animate.set_opacity(0.35), setv(1, "Hello from Ansible", TEAL_M, g), setv(2, "Hello from Ansible", TEAL_M, g)))
        self.beat("It sits higher, so it wins on both servers. The default is still there. It just loses.",
                  Indicate(d, color=GREEN_M, scale_factor=1.05), run_time=1.6)

        # 3. host_vars/web2
        hv = put(3, '"Hello from web2, the canary"', TEAL_M)
        self.steps("Now host_vars/web2.yml gives web2, the canary, its own text. A host beats its group.",
                   (1.0, on(3), FadeIn(hv, shift=RIGHT * 0.1)), (1.6, Wait(1.6)),
                   (1.6, setv(2, "Hello from web2, the canary", TEAL_M, hv)))
        self.beat("It names only web2, so web1 keeps the group's value.",
                  Indicate(V[1], color=TEAL_M, scale_factor=1.08), run_time=1.4)

        # 4. -e
        e = put(6, '"Hi from -e"', GOLD_M)
        self.steps("What you type for one run beats everything. Add -e with Hi from -e, and both hosts print Hi from -e.",
                   (1.0, on(6), FadeIn(e, shift=RIGHT * 0.1)), (1.6, Wait(1.6)),
                   (1.6, setv(1, "Hi from -e", GOLD_M, e), setv(2, "Hi from -e", GOLD_M, e)))
        self.beat("But only for that one command. Run again without it, and the inventory values are back.",
                  FadeOut(e), rungs[6].animate.set_opacity(0.5),
                  setv(1, "Hello from Ansible", TEAL_M, g), setv(2, "Hello from web2, the canary", TEAL_M, hv), run_time=2.0)

        # 5. the pattern, and how to ask
        q = T("how do you know which one won?", 26, GREY_B).move_to([3.9, 3.15, 0])
        self.beat("So how do you know which one won? Ansible never asks you, and never warns. It picks the winner by this list, silently.",
                  FadeIn(q, shift=DOWN * 0.1), run_time=1.6)
        dbg = M("ansible web -m ansible.builtin.debug -a var=hello_devops_greeting", 20, YELLOW_M).move_to([0.3, -3.35, 0])
        self.beat("So you ask each host what it sees. The debug module prints a variable after all the rules. Here, exactly the two values on screen.",
                  Write(dbg), Succession(Wait(2.4), AnimationGroup(Indicate(V[1], color=YELLOW_M), Indicate(V[2], color=YELLOW_M))), run_time=3.6)
        self.play(FadeOut(q), FadeOut(dbg), run_time=0.4)

        # 6. role vars break the pattern
        rv = put(5, '"fixed in vars/"', PURPLE_M)
        self.beat("One level breaks the pattern. Role vars, in the role's vars folder, sit above group_vars and host_vars.",
                  on(5), Indicate(rungs[5], color=PURPLE_M, scale_factor=1.06), run_time=1.8)
        self.steps("Put the greeting there by mistake, and it beats the whole inventory.",
                   (0.8, FadeIn(rv, shift=RIGHT * 0.1)),
                   (1.6, setv(1, "fixed in vars/", PURPLE_M, rv), setv(2, "fixed in vars/", PURPLE_M, rv)))
        x = tick(False, 0.22).next_to(hv, RIGHT, buff=0.2)
        self.beat("Now change host_vars for web2. Nothing happens, and Ansible gives no warning.",
                  Indicate(hv, color=TEAL_M, scale_factor=1.06), Succession(Wait(1.2), AnimationGroup(Create(x), Wiggle(V[2]))), run_time=2.8)
        keep = VGroup(T("defaults/: settings a user may change", 24, GREEN_M), T("vars/: the role's own fixed details", 24, PURPLE_M)).arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([HX - 0.3, 3.05, 0])
        self.beat("So defaults is for every setting a user may want to change, and vars is for the role's own fixed details.",
                  FadeIn(keep, shift=DOWN * 0.1), FadeOut(rv), FadeOut(x), rungs[5].animate.set_opacity(0.5),
                  setv(1, "Hello from Ansible", TEAL_M, g), setv(2, "Hello from web2, the canary", TEAL_M, hv), run_time=3.0)
        self.play(FadeOut(keep), run_time=0.4)
        v1, v2 = V[1], V[2]

        # 7. templates: the winning value, filled in per host
        ladder = VGroup(rungs, up, weak, strong, d, g, hv)
        self.play(ladder.animate.set_opacity(0), run_time=0.6)
        self.remove(ladder)
        mac = RoundedRectangle(corner_radius=0.15, width=5.7, height=3.2, stroke_color=BLUE_M, stroke_width=2.5).set_fill(tint(BLUE_M, 0.06), 1).move_to([-3.75, 0, 0])
        macl = T("your Mac: the control node", 24, BLUE_M).next_to(mac, UP, buff=0.18)
        tpl = VGroup(M("hello-devops.env.j2", 22, GOLD_M), M("GREETING={{ hello_devops_greeting }}", 20, WHITE)).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(mac)
        self.beat("Where does the winning value go? Often into a template. The template module reads a Jinja2 file on your Mac.",
                  Create(mac), FadeIn(macl), FadeIn(tpl), FadeOut(web1[2]), FadeOut(web2[2]),
                  Transform(web1[0], host("web1", 1.25, 3.95, 5.5)[0]), Transform(web2[0], host("web2", -1.25, 3.95, 5.5)[0]),
                  web1[1].animate.shift(LEFT * 0.7), web2[1].animate.shift(LEFT * 0.7),
                  v1.animate.shift(LEFT * 0.35), v2.animate.shift(LEFT * 0.35), run_time=2.4)
        self.beat("Double curly braces print a value. Here, the greeting.",
                  Indicate(tpl[1], color=GOLD_M, scale_factor=1.05), run_time=1.6)
        f1 = M("GREETING=Hello from Ansible", 20, TEAL_M).move_to(v1)
        f2 = M("GREETING=Hello from web2, the canary", 20, TEAL_M).move_to(v2)
        a1 = Arrow(mac.get_right() + UP * 0.4, web1[0].get_left(), buff=0.15, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.1)
        a2 = Arrow(mac.get_right() + DOWN * 0.4, web2[0].get_left(), buff=0.15, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.1)
        lab1 = M("/etc/hello-devops.env", 20, GREY_B).next_to(web1[1], RIGHT, buff=0.5)
        lab2 = M("/etc/hello-devops.env", 20, GREY_B).next_to(web2[1], RIGHT, buff=0.5)
        self.steps("It fills the file in for each host, with that host's values, and copies the result to the server.",
                   (1.0, GrowArrow(a1), GrowArrow(a2)), (1.0, travel(a1, GOLD_M, 1.0), travel(a2, GOLD_M, 1.0)),
                   (1.2, Transform(v1, f1), Transform(v2, f2), FadeIn(lab1), FadeIn(lab2)))
        nj = chip("servers need no Jinja2", GREEN_M, 24).move_to([HX, -3.05, 0])
        self.beat("One file, two results. Templates render on the control node, so the servers do not need Jinja2.",
                  FadeIn(nj, shift=UP * 0.1), Indicate(tpl[0], color=GOLD_M), run_time=2.4)
        self.play(FadeOut(VGroup(mac, macl, tpl, a1, a2, nj, web1[0], web1[1], web2[0], web2[1], v1, v2, lab1, lab2)), run_time=0.7)

        # 8. recap
        rcp = VGroup(T("knobs in role defaults", 30, GREEN_M), T("shared values in group_vars", 30, TEAL_M),
                     T("exceptions in host_vars", 30, TEAL_M), T("one-off overrides with -e", 30, GOLD_M)).arrange(DOWN, buff=0.4)
        self.beat("Put knobs in role defaults, shared values in group_vars, exceptions in host_vars, and one-off overrides in -e. Set each value in one place, and ask Ansible what it sees.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.5), run_time=5.0)
        self.wait(1.0)
