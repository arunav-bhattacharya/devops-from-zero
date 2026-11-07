import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


def tint(color, a=0.25):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def proc(color=GREY_B, r=0.13):
    """One process, drawn as a small filled circle."""
    return Circle(radius=r, stroke_color=color, stroke_width=2).set_fill(tint(color, 0.3), opacity=1)


def flash(b, color, rt=1.2):
    """A light that runs once around a box's border (leaves the box itself untouched)."""
    return ShowPassingFlash(b[0].copy().set_fill(opacity=0).set_stroke(color, 8), time_width=0.6, run_time=rt)


def frame(w, h, color=GREY_B, dashed=True, sw=2):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw)
    return DashedVMobject(r, num_dashes=int((w + h) * 5), dashed_ratio=0.55) if dashed else r


def meter(label, color, frac, cap=0.7, w=2.6, h=0.3):
    """A budget meter: outline, fill level and a cap mark."""
    out = Rectangle(width=w, height=h, stroke_color=GREY_B, stroke_width=2)
    fill = Rectangle(width=w * frac, height=h - 0.06, stroke_width=0).set_fill(color, opacity=0.75)
    fill.move_to(out.get_left() + RIGHT * (w * frac / 2 + 0.0))
    capx = out.get_left()[0] + w * cap
    capl = Line([capx, out.get_bottom()[1] - 0.12, 0], [capx, out.get_top()[1] + 0.12, 0], stroke_width=4, color=WHITE)
    lab = T(label, 24, GREY_B).next_to(out, LEFT, buff=0.25)
    return VGroup(out, fill, capl, lab)


class D17Container(VoiceScene):
    def construct(self):
        self.title_card("What a container really is", "an ordinary process with blinkers and a budget")

        # ---- 1. a VM is a whole pretend computer
        vm = VGroup(
            box("virtual hardware", GREY_B, w=4.4, h=0.66, size=26),
            box("its own kernel", GOLD_M, w=4.4, h=0.66, size=26),
            box("full operating system", BLUE_M, w=4.4, h=0.66, size=26),
            box("your app", TEAL_M, w=4.4, h=0.66, size=26),
        ).arrange(UP, buff=0.12).move_to(LEFT * 3.2 + DOWN * 0.2)
        vm_lab = T("virtual machine", 30, GREY_B).next_to(vm, UP, buff=0.35)
        self.beat("A virtual machine pretends to be a whole computer. It has virtual hardware, and it boots a full operating system with its own kernel.",
                  FadeIn(vm_lab), LaggedStart(*[FadeIn(l, shift=UP * 0.25) for l in vm], lag_ratio=0.4), run_time=3.2)

        jobs = VGroup(T("starts processes", 26), T("hands out memory", 26), T("talks to the hardware", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        jobs.next_to(vm, RIGHT, buff=1.3).shift(DOWN * 0.3)
        brace = Brace(jobs, LEFT, color=GOLD_M)
        klink = Line(vm[1].get_right() + RIGHT * 0.1, brace.get_left() + LEFT * 0.1, stroke_width=2, color=GOLD_M)
        self.beat("The kernel is the core of an operating system. It starts processes, hands out memory, and talks to the hardware.",
                  vm[1][0].animate.set_stroke(width=6), Create(klink), GrowFromCenter(brace),
                  LaggedStart(*[FadeIn(j, shift=RIGHT * 0.2) for j in jobs], lag_ratio=0.35), run_time=3.0)

        track = Rectangle(width=4.4, height=0.26, stroke_color=GREY_B, stroke_width=2).next_to(vm, DOWN, buff=0.5)
        fillb = Rectangle(width=4.36, height=0.2, stroke_width=0).set_fill(GOLD_M, opacity=0.8)
        fillb.move_to(track).stretch(0.01, 0, about_edge=LEFT).align_to(track, LEFT).shift(RIGHT * 0.02)
        boot = T("booting: many seconds", 24, GOLD_M).next_to(track, DOWN, buff=0.22)
        self.beat("Booting all of that takes many seconds. And each VM holds on to its own share of memory.",
                  vm[1][0].animate.set_stroke(width=3), FadeOut(VGroup(jobs, brace, klink)), Create(track), FadeIn(boot),
                  fillb.animate.stretch_to_fit_width(4.36, about_edge=LEFT), run_time=3.4)
        self.play(FadeOut(VGroup(vm, vm_lab, track, fillb, boot)), run_time=0.6)

        # ---- 2. a container is a normal Linux process
        host = RoundedRectangle(corner_radius=0.15, width=8.0, height=5.6, stroke_color=GREY_B, stroke_width=2).move_to([-2.6, -0.45, 0])
        host_lab = T("one Linux machine", 26, GREY_B).next_to(host, UP, buff=0.18).align_to(host, LEFT).shift(RIGHT * 0.2)
        kern = box("Linux kernel", GOLD_M, w=7.4, h=0.6, size=26).move_to([-2.6, -2.75, 0])
        grid = VGroup(*[proc() for _ in range(20)])
        for i, p in enumerate(grid):
            r, c = divmod(i, 5)
            p.move_to([-3.4 + c * 1.0, 1.6 - r * 0.75, 0])
        app = proc(TEAL_M, 0.3).move_to([-5.0, 0.45, 0])
        app_lab = T("your app", 22, TEAL_M).next_to(app, DOWN, buff=0.18)
        self.beat("A container has none of that. It is a normal Linux process, the same kind you listed with ps on Day 6.",
                  Create(host), FadeIn(host_lab), FadeIn(kern), LaggedStart(*[GrowFromCenter(p) for p in grid], lag_ratio=0.05),
                  GrowFromCenter(app), FadeIn(app_lab), run_time=3.0)

        ns_h = T("namespaces", 30, BLUE_M).move_to([4.2, 2.5, 0])
        cg_h = T("cgroups", 30, GOLD_M).move_to([4.2, -0.5, 0])
        self.beat("The kernel gives it two extra things.",
                  flash(kern, YELLOW_M),
                  LaggedStart(FadeIn(ns_h, shift=LEFT * 0.2), FadeIn(cg_h, shift=LEFT * 0.2), lag_ratio=0.4), run_time=1.8)

        fence = frame(2.0, 2.4, BLUE_M, sw=3).move_to([-5.0, 0.45, 0])
        view = VGroup(*[chip(t, BLUE_M, 24) for t in ("processes", "network", "hostname", "files")])
        view.arrange_in_grid(2, 2, buff=(0.25, 0.22)).next_to(ns_h, DOWN, buff=0.35)
        own = T("its own view of:", 24, GREY_B).next_to(view, UP, buff=0.18)
        ns_h.generate_target(); ns_h.target.next_to(own, UP, buff=0.18)
        VGroup(ns_h.target, own, view).move_to([4.2, 1.55, 0])
        self.beat("Namespaces give the process a private view of the system: its own process list, network, hostname and files.",
                  Create(fence), MoveToTarget(ns_h), FadeIn(own),
                  LaggedStart(*[FadeIn(v, shift=DOWN * 0.15) for v in view], lag_ratio=0.3), run_time=3.2)

        flaps = VGroup(
            Line(app.get_center() + LEFT * 0.48 + UP * 0.32, app.get_center() + LEFT * 0.48 + DOWN * 0.32),
            Line(app.get_center() + RIGHT * 0.48 + UP * 0.32, app.get_center() + RIGHT * 0.48 + DOWN * 0.32),
        ).set_stroke(BLUE_M, 7)
        self.beat("They work like the blinkers on a horse, the flaps that stop it seeing to the side.",
                  Create(flaps), grid.animate.set_opacity(0.15), run_time=2.0)

        cpu = meter("CPU", GOLD_M, 0.42)
        mem = meter("memory", GOLD_M, 0.5)
        meters = VGroup(cpu, mem).arrange(DOWN, buff=0.45, aligned_edge=RIGHT)
        bud = T("a budget:", 24, GREY_B)
        cg_h.generate_target()
        VGroup(cg_h.target, bud, meters).arrange(DOWN, buff=0.3).move_to([4.2, -1.55, 0])
        meters.align_to(cg_h.target, ORIGIN)
        self.beat("cgroups, short for control groups, give it a budget: a cap on CPU and memory.",
                  MoveToTarget(cg_h), FadeIn(bud), LaggedStart(FadeIn(cpu), FadeIn(mem), lag_ratio=0.4),
                  app.animate.set_stroke(GOLD_M, 4), run_time=2.6)

        mf = mem[1]
        cross = tick(False, 0.3).move_to(app)
        self.beat("Past the memory cap, the kernel kills it.",
                  Succession(mf.animate(run_time=1.0).stretch_to_fit_width(mem[0].width - 0.04, about_edge=LEFT).set_fill(RED_M),
                             AnimationGroup(app.animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.35)), Create(cross), run_time=0.6)),
                  run_time=1.6)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. see the blinkers work with Alpine
        cmd = M("$ docker run --rm alpine ps", 30).move_to([0, 3.05, 0]).to_edge(LEFT, buff=0.7)
        inside = RoundedRectangle(corner_radius=0.15, width=6.0, height=3.6, stroke_color=BLUE_M, stroke_width=3).move_to([-3.6, -0.35, 0])
        in_lab = T("what the container sees", 26, BLUE_M).next_to(inside, UP, buff=0.2)
        self.beat("You can watch namespaces work with Alpine, a tiny Linux image. Run ps inside it.",
                  Write(cmd), Create(inside), FadeIn(in_lab), run_time=2.2)
        out = VGroup(M("PID   USER     TIME  COMMAND", 24, GREY_B), M("    1 root      0:00 ps", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        out.move_to(inside).shift(UP * 0.5)
        one = SurroundingRectangle(out[1][0], color=YELLOW_M, buff=0.1)
        pid = T("PID 1: the first process", 24, YELLOW_M).next_to(out, DOWN, buff=0.55)
        self.beat("It lists a single process: ps itself, running as PID 1, the number a system gives its first process.",
                  FadeIn(out, shift=DOWN * 0.15), Create(one), FadeIn(pid), run_time=2.4)

        whole = RoundedRectangle(corner_radius=0.15, width=5.2, height=3.6, stroke_color=GREY_B, stroke_width=2).move_to([3.7, -0.35, 0])
        wh_lab = T("what the machine runs", 26, GREY_B).next_to(whole, UP, buff=0.2)
        dots = VGroup(*[proc(GREY_B, 0.07) for _ in range(160)]).arrange_in_grid(10, 16, buff=0.17).move_to(whole)
        mine = dots[70].set_stroke(TEAL_M).set_fill(TEAL_M, 1)
        self.beat("The machine runs hundreds of processes, and the container sees none of them.",
                  Create(whole), FadeIn(wh_lab), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.01), run_time=2.6)

        cmd2 = M("$ docker run --rm alpine ls /", 30).move_to(cmd, aligned_edge=LEFT)
        folders = VGroup(M("bin   dev   etc   home  lib", 24, TEAL_M), M("media mnt   opt   proc  root", 24, TEAL_M),
                         M("run   sbin  srv   sys   tmp", 24, TEAL_M), M("usr   var", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        folders.move_to(inside).shift(UP * 0.2)
        img = box("alpine image", TEAL_M, size=24).next_to(inside, DOWN, buff=0.35)
        self.beat("In the same way, listing the root folder shows Alpine's own folders.",
                  Transform(cmd, cmd2), FadeOut(VGroup(out, one, pid)), LaggedStart(*[FadeIn(f, shift=DOWN * 0.1) for f in folders], lag_ratio=0.2),
                  run_time=2.2)
        a_img = edge_arrow(img, inside, TEAL_M)
        host_files = T("host files: hidden", 24, GREY_B).next_to(whole, DOWN, buff=0.35)
        self.beat("Those files come from the image. None of the host's files show up.",
                  FadeIn(img, shift=UP * 0.15), GrowArrow(a_img), FadeIn(host_files), dots.animate.set_opacity(0.25), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. the five steps of docker run
        head = M("docker run nginx", 30, YELLOW_M).move_to([0, 3.35, 0]).to_edge(LEFT, buff=0.5)
        steps_txt = ["send the request", "pull the image if missing", "add a writable layer", "namespaces and a cgroup", "start it as PID 1"]
        steps = VGroup()
        for i, s in enumerate(steps_txt):
            n = T(str(i + 1), 26, GREY_B)
            c = Circle(radius=0.24, stroke_color=GREY_B, stroke_width=2).move_to(n)
            steps.add(VGroup(VGroup(c, n), T(s, 24, GREY_B).next_to(c, RIGHT, buff=0.22)))
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.42).next_to(head, DOWN, buff=0.6).align_to(head, LEFT)
        self.beat("Put together, docker run nginx does five things, in this order.",
                  Write(head), LaggedStart(*[FadeIn(s, shift=RIGHT * 0.15) for s in steps], lag_ratio=0.2), run_time=2.4)

        def on(i):
            s = steps[i]
            return AnimationGroup(s[0][0].animate.set_stroke(YELLOW_M, 3).set_fill(tint(YELLOW_M, 0.3), 1),
                                  s[0][1].animate.set_color(YELLOW_M), s[1].animate.set_color(WHITE))

        def done(i):
            s = steps[i]
            return AnimationGroup(s[0][0].animate.set_stroke(GREEN_M, 3).set_fill(tint(GREEN_M, 0.25), 1),
                                  s[0][1].animate.set_color(GREEN_M), s[1].animate.set_color(GREY_B))

        mac_lab = T("your Mac", 22, GREY_B).move_to([-0.2, 3.4, 0])
        cli = mbox("docker", WHITE, size=24, h=0.7).next_to(mac_lab, DOWN, buff=0.15)
        vmf = frame(8.1, 5.4, GREY_B).move_to([2.75, -0.85, 0])
        vm_l = T("Linux VM", 22, GREY_B).move_to(vmf.get_corner(UR) + LEFT * 0.85 + DOWN * 0.35)
        eng = box("Docker Engine", PURPLE_M, size=24, h=0.7).move_to([0.75, 0.95, 0])
        kbar = box("Linux kernel", GOLD_M, w=7.5, h=0.55, size=24).move_to([2.75, -3.05, 0])
        a1 = Arrow(cli.get_bottom(), eng.get_top(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("One. The docker command on your Mac sends the request to Docker Engine, inside the Linux VM.",
                  on(0), FadeIn(mac_lab), FadeIn(cli), Create(vmf), FadeIn(vm_l), FadeIn(kbar), GrowFromCenter(eng), GrowArrow(a1), run_time=2.6)
        self.play(travel(a1), run_time=0.8)

        hub = box("Docker Hub", GREY_B, size=24, h=0.7).move_to([5.4, 2.95, 0])
        hub_l = T("registry", 22, GREY_B).next_to(hub, LEFT, buff=0.25)
        stack = VGroup(*[Rectangle(width=2.6, height=0.36, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.2), 1)
                         for _ in range(3)]).arrange(UP, buff=0.06).move_to([4.0, -1.55, 0])
        st_l = T("nginx image", 22, GREY_B).next_to(stack, LEFT, buff=0.55)
        a2 = Arrow(hub.get_bottom(), stack.get_top() + UP * 0.05, buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        self.beat("Two. The engine checks whether it already has the image, and pulls it from the registry if not.",
                  done(0), on(1), FadeIn(hub), FadeIn(hub_l), GrowArrow(a2),
                  LaggedStart(*[FadeIn(l, shift=DOWN * 0.6) for l in stack], lag_ratio=0.3), FadeIn(st_l), run_time=2.8)

        wl = Rectangle(width=2.6, height=0.3, stroke_color=GOLD_M, stroke_width=2.5).set_fill(tint(GOLD_M, 0.35), 1).next_to(stack, UP, buff=0.06)
        wl_l = T("writable layer", 22, GOLD_M).next_to(wl, LEFT, buff=0.55)
        root = M("/", 30, WHITE).next_to(VGroup(stack, wl), RIGHT, buff=0.35)
        rbr = Brace(VGroup(stack, wl), RIGHT, buff=0.08, color=GREY_B)
        root.next_to(rbr, RIGHT, buff=0.15)
        self.beat("Three. It puts a fresh writable layer on top of the image's files. That merged folder tree becomes the container's root folder.",
                  done(1), on(2), FadeOut(a2), GrowFromEdge(wl, DOWN), FadeIn(wl_l), GrowFromCenter(rbr), Write(root), run_time=2.8)

        fence = frame(3.1, 3.1, BLUE_M, sw=3).move_to([4.0, -0.75, 0])
        gauge_o = Rectangle(width=0.32, height=1.6, stroke_color=GOLD_M, stroke_width=2).move_to([6.15, -0.6, 0])
        gauge_f = Rectangle(width=0.26, height=0.7, stroke_width=0).set_fill(GOLD_M, 0.75).align_to(gauge_o, DOWN).shift(UP * 0.03).set_x(gauge_o.get_x())
        gauge_l = T("cgroup", 22, GOLD_M).next_to(gauge_o, DOWN, buff=0.15)
        ns_l = T("namespaces", 22, BLUE_M).next_to(fence, UP, buff=0.12)
        self.beat("Four. It asks the kernel for new namespaces, and a cgroup.",
                  done(2), on(3), flash(kbar, YELLOW_M), FadeOut(VGroup(rbr, root)),
                  Create(fence), FadeIn(ns_l), Create(gauge_o), GrowFromEdge(gauge_f, DOWN), FadeIn(gauge_l), run_time=2.4)

        p1 = proc(TEAL_M, 0.26).move_to([3.0, 0.2, 0])
        p1_l = T("nginx, PID 1", 22, TEAL_M).next_to(p1, RIGHT, buff=0.2)
        self.beat("Five. It starts the image's default command inside them, as PID 1. For nginx, that is the nginx server.",
                  done(3), on(4), GrowFromCenter(p1), FadeIn(p1_l), run_time=2.2)

        helpers = VGroup(mbox("containerd", PURPLE_M, size=22, h=0.6), mbox("runc", PURPLE_M, size=22, h=0.6)).arrange(RIGHT, buff=0.3)
        h_l = T("steps 3 to 5 are handed to", 22, PURPLE_M)
        hg = VGroup(h_l, helpers).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(steps, DOWN, buff=0.7).align_to(steps, LEFT)
        self.beat("The engine hands steps three to five to two helper programs, containerd and runc.",
                  steps[4][0][0].animate.set_stroke(GREEN_M, 3).set_fill(tint(GREEN_M, 0.25), 1), steps[4][0][1].animate.set_color(GREEN_M),
                  *[steps[i][1].animate.set_color(PURPLE_M) for i in (2, 3, 4)], FadeIn(h_l),
                  LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in helpers], lag_ratio=0.3),
                  flash(eng, YELLOW_M), run_time=2.4)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. why a container starts fast
        lab_vm = T("virtual machine", 28, GREY_B).move_to([-5.2, 1.1, 0])
        seq = VGroup(box("virtual hardware", GREY_B, w=2.55, h=0.66, size=22), box("boot a kernel", GOLD_M, w=2.15, h=0.66, size=22),
                     box("boot the OS", BLUE_M, w=1.95, h=0.66, size=22), box("app", TEAL_M, w=1.0, h=0.66, size=22)).arrange(RIGHT, buff=0.1)
        seq.move_to([2.0, 1.1, 0])
        vm_t = T("many seconds", 24, GOLD_M).next_to(seq, DOWN, buff=0.25)
        self.beat("Now compare the start of a virtual machine. Virtual hardware, its own kernel, a whole operating system, and only then your app. That takes many seconds.",
                  FadeIn(lab_vm), LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in seq], lag_ratio=0.6), FadeIn(vm_t), run_time=4.4)

        lab_c = T("container", 28, GREY_B).move_to([-5.2, -1.2, 0])
        cp = proc(TEAL_M, 0.22).move_to([-2.85, -1.2, 0])
        cf = frame(1.0, 1.0, BLUE_M, sw=3).move_to(cp)
        c_t = T("about a second", 24, TEAL_M).next_to(cf, RIGHT, buff=0.35)
        no_k = VGroup(T("no second kernel to boot", 24, GREY_B)).next_to(c_t, RIGHT, buff=0.8)
        self.beat("A container skips all of that. No second kernel has to boot. Docker builds nothing new: it only puts fences around a process. So it starts in about a second.",
                  FadeIn(lab_c), GrowFromCenter(cp), Create(cf), FadeIn(c_t), Circumscribe(seq[1], color=GOLD_M, time_width=0.5), FadeIn(no_k), run_time=4.0)
        self.play(FadeOut(VGroup(lab_vm, seq, vm_t, lab_c, cp, cf, c_t, no_k)), run_time=0.6)

        kb = box("one shared Linux kernel", GOLD_M, w=10.0, h=0.66, size=26).move_to([0, -1.6, 0])
        cs = VGroup()
        for name in ("web", "cache", "app"):
            f = frame(2.4, 1.6, BLUE_M, sw=3)
            p = proc(TEAL_M, 0.22).move_to(f).shift(UP * 0.15)
            cs.add(VGroup(f, p, T(name, 22, TEAL_M).next_to(p, DOWN, buff=0.15)))
        cs.arrange(RIGHT, buff=0.9).next_to(kb, UP, buff=0.45)
        self.beat("You pay for that speed by sharing. Every container on a host uses the same kernel.",
                  FadeIn(kb), LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cs], lag_ratio=0.25), run_time=2.4)
        bug = T("kernel bug", 24, RED_M).next_to(kb, DOWN, buff=0.3)
        self.beat("So a kernel bug can affect all of them.",
                  kb[0].animate.set_stroke(RED_M), FadeIn(bug, shift=UP * 0.1),
                  *[c[1].animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.35)) for c in cs], run_time=1.6)
        cpu = VGroup(chip("built for that kernel", GOLD_M, 24), chip("built for that CPU", GOLD_M, 24)).arrange(RIGHT, buff=0.5).move_to([0, 2.9, 0])
        self.beat("And a container can only run programs built for that kernel, and that CPU.",
                  kb[0].animate.set_stroke(GOLD_M), FadeOut(bug), *[c[1].animate.set_stroke(TEAL_M).set_fill(tint(TEAL_M, 0.3)) for c in cs],
                  LaggedStart(FadeIn(cpu[0], shift=DOWN * 0.15), FadeIn(cpu[1], shift=DOWN * 0.15), lag_ratio=0.4), run_time=2.2)
        self.play(FadeOut(VGroup(kb, cs, cpu)), run_time=0.6)

        # ---- recap
        rec = VGroup(
            VGroup(T("a process", 34, TEAL_M), T("started from an image's files", 30, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("namespaces", 34, BLUE_M), T("its own view", 30, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("cgroups", 34, GOLD_M), T("its limits", 30, GREY_B)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("So a container is an ordinary Linux process, started from an image's files. Namespaces give it its own view, and cgroups give it limits.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rec], lag_ratio=0.5), run_time=3.6)
        self.wait(1.0)
