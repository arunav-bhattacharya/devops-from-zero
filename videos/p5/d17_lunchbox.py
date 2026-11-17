import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcgroups?\b", lambda m: "C groups" if m.group(0).endswith("s") else "C group"), (r"\bdocker rm\b", "docker R M"),
            (r"\bps\b", "P S")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def proc(color=GREY_B, r=0.2):
    return Circle(radius=r, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.3), opacity=1)


def lunchbox(color=GOLD_M, w=2.2, h=1.5):
    base = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color, stroke_width=3.5).set_fill(tint(color, 0.08), opacity=1)
    handle = Arc(radius=0.32, start_angle=0, angle=PI, stroke_color=color, stroke_width=3.5).next_to(base, UP, buff=0)
    return VGroup(base, handle)


class D17Lunchbox(VoiceScene):
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
        self.title_card("A lunchbox, not a tiny computer", "what really runs when a container runs")

        # 1. it works in my kitchen
        dish = Circle(radius=0.55, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.25), opacity=1)
        dl = T("your dish", 26, GOLD_M).next_to(dish, DOWN, buff=0.2)
        home = RoundedRectangle(corner_radius=0.15, width=4.6, height=3.2, stroke_color=GREEN_M, stroke_width=3).move_to([-3.4, 0.2, 0])
        hl = T("your kitchen", 26, GREEN_M).next_to(home, UP, buff=0.2)
        VGroup(dish, dl).move_to(home.get_center() + DOWN * 0.1)
        self.beat("Picture cooking your best dish for a friend's party. At home, it comes out perfect every time.",
                  Create(home), FadeIn(hl), GrowFromCenter(dish), FadeIn(dl), run_time=2.0)
        away = RoundedRectangle(corner_radius=0.15, width=4.6, height=3.2, stroke_color=RED_M, stroke_width=3).move_to([3.4, 0.2, 0])
        al = T("your friend's kitchen", 26, RED_M).next_to(away, UP, buff=0.2)
        diffs = VGroup(T("hotter oven", 26, RED_M), T("no fresh garlic", 26, RED_M), T("different salt", 26, RED_M)).arrange(DOWN, buff=0.18).move_to(away.get_center() + UP * 0.8)
        self.steps("At your friend's house, the oven runs hotter, there is no fresh garlic, and the salt is a different kind.",
                   (0.8, Create(away), FadeIn(al)), (0.8, VGroup(dish, dl).animate.move_to(away.get_center() + DOWN * 0.5)),
                   (0.5, FadeIn(diffs[0])), (0.7, FadeIn(diffs[1])), (0.6, FadeIn(diffs[2])))
        self.beat("The dish fails, and you stand in their kitchen saying: but it works at home.",
                  dish.animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.25)), Wiggle(dish), run_time=1.6)
        code = VGroup(M("Python 3.14", 24, GREEN_M).move_to(home.get_center() + UP * 0.6), M("Python 3.12", 24, RED_M).move_to(diffs[0]))
        tests = T("same code: passes on your Mac, fails in CI", 26, YELLOW_M).move_to([0, -2.4, 0])
        self.steps("Software has the same problem. Your test passes on your Mac with Python 3.14, and fails on the CI machine, which has Python 3.12. Nobody touched the code. Everything around it changed.",
                   (2.0, Wait(2.0)), (0.6, FadeIn(code[0])), (1.4, Wait(1.4)), (0.8, FadeOut(diffs), FadeIn(code[1])), (0.8, FadeIn(tests, shift=UP * 0.1)))
        self.play(FadeOut(VGroup(home, hl, away, al, code, tests)), VGroup(dish, dl).animate.move_to([-4.2, 0.4, 0]), dish.animate.set_stroke(GOLD_M).set_fill(tint(GOLD_M, 0.25)), run_time=0.8)

        # 2. the wish: pack the kitchen with the dish
        box_ = lunchbox(GOLD_M, 4.8, 2.7).move_to([0.6, 0.2, 0])
        self.beat("Wouldn't it be nice to carry the kitchen along with the dish? Pack it like a lunchbox: the meal plus its own fork, salt and napkin.",
                  Create(box_), run_time=1.6)
        items = VGroup(chip("app", GOLD_M, 24), chip("Python 3.14", BLUE_M, 24), chip("libraries", TEAL_M, 24), chip("settings", PURPLE_M, 24))
        items.arrange_in_grid(2, 2, buff=0.2).move_to(box_[0])
        self.steps("Into the box goes the app, the runtime that runs its code, the libraries it uses, and its settings.",
                   (0.8, ReplacementTransform(VGroup(dish, dl), items[0])), (0.6, FadeIn(items[1], shift=DOWN * 0.1)), (0.6, FadeIn(items[2], shift=DOWN * 0.1)), (0.6, FadeIn(items[3], shift=DOWN * 0.1)))
        seal = T("image", 30, GOLD_M).next_to(box_, DOWN, buff=0.3)
        sub = T("sealed and read-only", 26, GREY_B).next_to(seal, DOWN, buff=0.12)
        self.beat("Then you seal it. That sealed, read-only package is called an image. Docker is the tool that builds images and runs them.",
                  box_[0].animate.set_stroke(width=6), FadeIn(seal), FadeIn(sub), run_time=1.6)
        self.beat("And the same image runs the same way on your Mac, on a CI machine, and on a cloud server. The kitchen travels with the dish.",
                  Indicate(seal, color=GOLD_M), run_time=1.4)
        self.play(FadeOut(VGroup(items, sub)), box_[0].animate.set_stroke(width=3.5), run_time=0.5)
        self.play(FadeOut(seal), box_.animate.scale(0.42).move_to([-5.3, 2.55, 0]), run_time=0.8)
        imgl = T("image", 24, GOLD_M).next_to(box_, DOWN, buff=0.12)
        self.play(FadeIn(imgl), run_time=0.3)
        image = VGroup(box_, imgl)

        # 3. the wrong model: a tiny computer
        q = T("so what is running? a tiny computer?", 30, YELLOW_M).move_to([1.0, 2.9, 0])
        self.beat("Now open one box and run it. So what is actually running? A tiny computer inside your computer?",
                  FadeIn(q, shift=DOWN * 0.1), run_time=1.6)
        vm = RoundedRectangle(corner_radius=0.15, width=4.8, height=3.6, stroke_color=BLUE_M, stroke_width=3).move_to([1.0, -0.4, 0])
        vml = VGroup(box("virtual hardware", BLUE_M, w=4.3, h=0.6, size=26), box("its own kernel", BLUE_M, w=4.3, h=0.6, size=26),
                     box("a whole operating system", BLUE_M, w=4.3, h=0.6, size=26), box("your app", GOLD_M, w=4.3, h=0.6, size=26))
        vml.arrange(UP, buff=0.12).move_to(vm)
        vmn = T("a virtual machine", 28, BLUE_M).next_to(vm, RIGHT, buff=0.4)
        self.steps("That is a fair guess, because there is an older way that works exactly like that: a virtual machine, or VM. It pretends to be a whole computer.",
                   (0.6, Create(vm), FadeIn(vmn)), (2.0, Wait(2.0)), (2.0, LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in vml], lag_ratio=0.4)))
        self.beat("It boots a full operating system with its own kernel. The kernel is the core of an operating system: it starts programs, hands out memory, and talks to the hardware.",
                  Indicate(vml[1][1], color=BLUE_M), run_time=1.6)
        slowc = T("booting: many seconds", 26, BLUE_M).next_to(vm, DOWN, buff=0.2)
        self.beat("Booting all of that takes many seconds. If a container were that, it would be a busy little place.",
                  FadeIn(slowc), run_time=1.4)

        # predict, then show
        cmd = M("$ docker run --rm alpine ps", 26, GREY_B).move_to([1.0, 2.9, 0])
        self.beat("Let's test it. Alpine is a tiny Linux image. We ask it to list every process it can see.",
                  FadeOut(q), FadeIn(cmd), run_time=1.4)
        self.beat("A real computer runs hundreds of programs. How many will this container list? Pause and guess.")
        self.wait(2.0)
        out = VGroup(M("PID   COMMAND", 24, GREY_B), M("1     ps", 24, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([1.0, -0.4, 0])
        self.steps("One. Just ps itself, running as PID 1. A PID is the number Linux gives each running program, and 1 goes to the first one.",
                   (0.8, FadeOut(VGroup(vm, vml, vmn, slowc)), FadeIn(out)), (1.6, Wait(1.6)), (0.6, Indicate(out[1], color=GREEN_M)))
        self.beat("Well, that is not a busy computer. That is one lonely program.", run_time=None)
        self.play(FadeOut(out), FadeOut(cmd), run_time=0.5)

        # 4. what it really is: a process with walls and a budget
        kern = box("Linux kernel", TEAL_M, w=11.0, h=0.66, size=28).move_to([0.4, -2.45, 0])
        host = VGroup(*[proc().move_to([x, y, 0]) for x, y in [(-4.0, -1.5), (-3.2, -0.7), (-4.3, 0.2), (-3.0, 0.5), (4.3, -1.4), (5.0, -0.5), (4.0, 0.3), (5.2, 0.6),
                                                               (-1.4, -1.6), (1.9, -1.6), (2.6, -0.4), (-2.0, -0.2)]])
        self.steps("Here is what really happens. Down at the bottom is the kernel of the machine. Above it run lots of ordinary programs, called processes.",
                   (0.8, FadeIn(kern, shift=UP * 0.1)), (1.4, Wait(1.4)), (1.4, LaggedStart(*[GrowFromCenter(p) for p in host], lag_ratio=0.08)))
        me = proc(GOLD_M, 0.26).move_to([0.3, -0.3, 0])
        mel = M("PID 1", 22, GOLD_M).next_to(me, DOWN, buff=0.15)
        me.set_z_index(3); mel.set_z_index(3)
        self.beat("A container is one more of those. A normal Linux process. No second computer, no second kernel.",
                  GrowFromCenter(me), run_time=1.2)
        walls = lunchbox(GOLD_M, 2.3, 1.8).move_to([0.3, -0.25, 0])
        ns = VGroup(T("walls: namespaces", 26, GOLD_M), T("its own view of programs,", 24, GREY_B), T("network, name and files", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        ns.move_to([0.4, 2.55, 0])
        self.steps("But the kernel gives it two extra things. First, walls. Like a lunchbox in the office fridge: the food inside cannot see the other boxes. Linux calls these walls namespaces.",
                   (2.2, Wait(2.2)), (1.0, Create(walls), FadeIn(mel)), (3.0, Wait(3.0)), (0.8, FadeIn(ns, shift=DOWN * 0.1)))
        self.beat("Inside its walls, the process gets its own list of programs, its own network, its own name, and its own files. That is why ps saw only itself.",
                  *[p.animate.set_opacity(0.25) for p in host], run_time=1.6)
        bud = VGroup(Rectangle(width=0.36, height=1.5, stroke_color=PURPLE_M, stroke_width=2.5), Rectangle(width=0.36, height=0.6, stroke_width=0).set_fill(PURPLE_M, 0.7))
        bud[1].align_to(bud[0], DOWN)
        bud.next_to(walls, RIGHT, buff=0.35).shift(DOWN * 0.15)
        cap = DashedLine(bud[0].get_corner(UL) + DOWN * 0.25 + LEFT * 0.1, bud[0].get_corner(UR) + DOWN * 0.25 + RIGHT * 0.1, color=RED_M, stroke_width=3)
        bl = VGroup(T("budget: cgroups", 26, PURPLE_M), T("a cap on CPU and memory", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(bud, RIGHT, buff=0.3)
        self.steps("Second, a budget. A cap on how much processor time and memory it may use. Linux calls this a cgroup, short for control group.",
                   (0.6, FadeIn(bud)), (1.4, Wait(1.4)), (0.6, Create(cap), FadeIn(bl, shift=LEFT * 0.1)))
        self.steps("Go past the memory cap, and the kernel kills it.",
                   (1.0, bud[1].animate.stretch_to_fit_height(1.3).align_to(bud[0], DOWN)), (0.4, bud[1].animate.set_fill(RED_M)), (0.4, me.animate.set_opacity(0.2)))
        self.play(bud[1].animate.stretch_to_fit_height(0.6).align_to(bud[0], DOWN).set_fill(PURPLE_M), me.animate.set_opacity(1), run_time=0.6)
        nm = T("a container = a process + walls + a budget", 30, YELLOW_M).move_to([0.4, -1.75, 0])
        self.beat("So a container is a process, with walls and a budget. Not a tiny computer. A process that was told, very firmly, to mind its own business.",
                  FadeIn(nm, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(nm), run_time=0.4)

        # shared kernel = one office microwave
        others = VGroup(lunchbox(BLUE_M, 1.5, 1.2).move_to([-3.6, -0.5, 0]), lunchbox(GREEN_M, 1.5, 1.2).move_to([4.5, -0.5, 0]))
        ops = VGroup(proc(BLUE_M, 0.22).move_to(others[0][0]), proc(GREEN_M, 0.22).move_to(others[1][0]))
        lines = VGroup(*[DashedLine(m.get_bottom(), kern.get_top() + RIGHT * (m.get_x() - kern.get_x()) * 0.9, stroke_width=2, color=TEAL_M) for m in (others[0][0], walls[0], others[1][0])])
        self.steps("Start two more containers, and here is the twist. They all use the same kernel, like lunches that all go through one office microwave.",
                   (1.0, FadeOut(host), FadeOut(VGroup(ns, bud, cap, bl)), LaggedStart(Create(others[0]), Create(others[1]), lag_ratio=0.3), FadeIn(ops)), (2.0, Wait(2.0)), (1.2, LaggedStart(*[Create(l) for l in lines], lag_ratio=0.25)))
        fast = T("no kernel to boot: starts in about a second", 26, TEAL_M).move_to([0.6, 2.6, 0])
        self.beat("Nothing has to boot. So a container starts in about a second.", FadeIn(fast, shift=UP * 0.1), run_time=1.2)
        self.play(FadeOut(fast), run_time=0.4)

        # 5. on a Mac: the small Linux VM
        mac = RoundedRectangle(corner_radius=0.2, width=12.6, height=6.8, stroke_color=GREY_B, stroke_width=2.5).move_to([0.2, 0.0, 0])
        macl = T("your Mac", 26, GREY_B).move_to([-5.0, 2.95, 0])
        self.beat("Now a puzzle for Mac users. A Mac has its own kernel, and it is not Linux. So which kernel runs these containers? Pause and guess.",
                  FadeOut(image), Create(mac), FadeIn(macl), run_time=2.0)
        self.wait(2.0)
        vm2 = DashedVMobject(RoundedRectangle(corner_radius=0.15, width=11.8, height=5.0, stroke_color=TEAL_M, stroke_width=2.5), num_dashes=70).move_to([0.4, -0.7, 0])
        vml2 = T("one small Linux VM, run by Docker Desktop", 26, TEAL_M).move_to([0.9, 2.15, 0])
        self.steps("The Linux kernel of one small VM. Docker Desktop, the Mac app that installs Docker, quietly starts it in the background, and every container shares its kernel.",
                   (1.0, Create(vm2)), (0.8, FadeIn(vml2, shift=DOWN * 0.1)), (2.0, Wait(2.0)), (1.0, Indicate(kern[1], color=TEAL_M)))
        self.play(FadeOut(VGroup(mac, macl, vm2, vml2)), run_time=0.6)

        # 6. one image, many opened boxes, each with its own ketchup
        image.move_to([-5.3, 2.35, 0])
        self.play(FadeIn(image), run_time=0.5)
        lid = T("one image, many containers", 28, GOLD_M).move_to([0.8, 2.6, 0])
        self.beat("Back to the lunchbox shop. One sealed image can start many containers, and each one is its own opened copy.",
                  FadeIn(lid), *[Indicate(b[1], color=c) for b, c in ((others[0], BLUE_M), (walls, GOLD_M), (others[1], GREEN_M))], run_time=1.8)
        k = Square(0.32, stroke_width=0).set_fill(RED_M, 0.9).move_to(walls[0].get_corner(UR) + LEFT * 0.35 + DOWN * 0.3)
        kl = T("a file it wrote", 24, RED_M).next_to(walls, UP, buff=0.45)
        self.steps("When the app writes a file, it lands in a thin writable layer that belongs to that copy only. Like ketchup you add after opening. The other boxes never see it.",
                   (2.0, Wait(2.0)), (0.6, GrowFromCenter(k), FadeIn(kl)), (2.4, Wait(2.4)), (0.6, Indicate(others[0][1], color=BLUE_M)), (0.6, Indicate(others[1][1], color=GREEN_M)))
        rm = M("$ docker rm", 24, RED_M).next_to(walls, UP, buff=0.45)
        self.steps("Remove the container, and its ketchup goes with it. The image itself never changes.",
                   (0.6, FadeOut(kl), FadeIn(rm)), (0.8, FadeOut(VGroup(walls, me, mel, k)), FadeOut(lines[1])), (0.8, Indicate(image[0][0], color=GOLD_M)))
        self.play(FadeOut(rm), run_time=0.4)

        # 7. guardrail: the cost of sharing
        self.play(FadeOut(lid), run_time=0.3)
        g = VGroup(T("one kernel for all: a kernel bug can hit every container", 26, RED_M),
                   T("only programs built for that kernel and that CPU", 26, RED_M),
                   T("what a container writes is lost with docker rm", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0.6, 1.55, 0])
        self.steps("Speed has a price, though. Because every container shares one kernel, a kernel bug can affect all of them. A container can only run programs built for that kernel and that processor. And whatever it writes is lost when you remove it.",
                   (0.8, FadeIn(g[0], shift=UP * 0.1)), (4.0, Wait(4.0)), (0.8, FadeIn(g[1], shift=UP * 0.1)), (2.4, Wait(2.4)), (0.8, FadeIn(g[2], shift=UP * 0.1)))
        self.play(FadeOut(g), FadeOut(image), run_time=0.5)

        # 8. moral and quick check
        mor = VGroup(T("image: the sealed box", 28, GOLD_M), T("container: an opened copy, a process with walls and a budget", 28, WHITE),
                     T("all of them share one kernel", 28, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0.6, 1.55, 0])
        fit(mor, 11.0)
        self.steps("So the moral of the story. The image is the sealed box. A container is an opened copy: just a process, with walls and a budget. And they all share one kernel, the office microwave.",
                   (0.6, FadeIn(mor[0], shift=UP * 0.1)), (1.6, Wait(1.6)), (0.6, FadeIn(mor[1], shift=UP * 0.1)), (3.0, Wait(3.0)), (0.6, FadeIn(mor[2], shift=UP * 0.1)))
        quiz = VGroup(T("Quick check: ten containers from one image.", 28, YELLOW_M), T("One writes a file. Do the others see it?", 28, YELLOW_M)).arrange(DOWN, buff=0.12)
        self.play(FadeOut(mor), run_time=0.4)
        quiz.move_to([0.4, 1.6, 0])
        self.beat("Quick check. You start ten containers from one image, and one of them writes a file. Do the other nine see it?",
                  FadeIn(quiz, shift=UP * 0.1), run_time=1.4)
        self.wait(2.0)
        no = T("No. The file sits in that container's own layer.", 28, GREEN_M).next_to(quiz, DOWN, buff=0.3)
        self.beat("No. It sits in that one container's own layer, its ketchup. The image, and the other boxes, never change.",
                  FadeIn(no, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
