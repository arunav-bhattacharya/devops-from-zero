import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"/venv/bin\b", "slash venv slash bin"), (r"/venv\b", "slash venv"), (r"\bvenv\b", "venv"), (r"\buseradd\b", "user add"),
            (r"\bgunicorn\b", "G-unicorn"), (r"\bapp\.py\b", "app dot pie"), (r"--from=build\b", "dash dash from equals build"),
            (r"\bpip\b", "pip"), (r"\bTrivy\b", "trivvy"), (r"\bJDK\b", "J D K"), (r"\bMB\b", "megabytes"), (r"\bHIGH\b", "high")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def stage_box(cx, title, color):
    r = RoundedRectangle(corner_radius=0.18, width=5.9, height=5.0, stroke_color=color, stroke_width=3).set_fill(BLACK, 1).move_to([cx, 0.1, 0])
    t = T(title, 26, color).next_to(r.get_corner(UL), DR, buff=0.2)
    return VGroup(r, t)


def base_bar(cx):
    r = RoundedRectangle(corner_radius=0.1, width=5.2, height=0.62, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.18), 1).move_to([cx, -1.85, 0])
    t = M("python:3.14-slim", 20, GREY_B).move_to(r).align_to(r, LEFT).shift(RIGHT * 0.25)
    pip = chip("pip", RED_M, 20, mono=True).move_to(r).align_to(r, RIGHT).shift(LEFT * 0.12)
    return VGroup(r, t), pip


def venv_box(cx):
    r = RoundedRectangle(corner_radius=0.12, width=5.2, height=1.75, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.1), 1).move_to([cx, -0.3, 0])
    t = M("/venv", 22, GOLD_M).next_to(r.get_corner(UL), DR, buff=0.14)
    return VGroup(r, t)


def pkgs(vb):
    names = ["flask", "gunicorn", "redis", "prometheus-client"]
    cs = VGroup(*[chip(n, TEAL_M, 20, mono=True) for n in names])
    row1 = VGroup(cs[0], cs[1], cs[2]).arrange(RIGHT, buff=0.15)
    row1.move_to(vb[0]).shift(UP * 0.05 + LEFT * 0.35)
    cs[3].next_to(row1, DOWN, buff=0.12).align_to(row1, LEFT)
    return cs


class D22Multistage(VoiceScene):
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
        self.title_card("Build with tools, ship without them", "a multi-stage build and a non-root user")

        # ---- 0. the problem: the Day 19 image ships its tools
        img = RoundedRectangle(corner_radius=0.18, width=5.6, height=4.4, stroke_color=BLUE_M, stroke_width=3).set_fill(BLACK, 1).move_to([-2.6, 0.1, 0])
        img_t = T("Day 19 image: one stage", 26, BLUE_M).next_to(img.get_corner(UL), DR, buff=0.2)
        items = VGroup(chip("app.py", BLUE_M, 22, mono=True), chip("packages", TEAL_M, 22), chip("pip", RED_M, 22, mono=True),
                       chip("build leftovers", RED_M, 22), chip("python:3.14-slim", GREY_B, 22, mono=True))
        items.arrange(DOWN, buff=0.16).move_to(img).shift(DOWN * 0.3)
        root = chip("runs as root", RED_M, 22).next_to(img, DOWN, buff=0.25)
        self.beat("The Day 19 image has one stage. So everything used to build the app ships with it.",
                  Create(img), FadeIn(img_t), LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in reversed(items)], lag_ratio=0.25), run_time=3.2)
        self.beat("pip is there, and so is anything a compiler step would leave behind. And the app runs as root.",
                  Indicate(items[2], color=RED_M), Succession(Wait(1.0), Indicate(items[3], color=RED_M)), Succession(Wait(3.4), FadeIn(root, shift=UP * 0.1)), run_time=4.4)
        cons = VGroup(T("needs patching", 26), T("shows up in scan reports", 26), T("an attacker can use it", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        cons.move_to([3.6, 0.2, 0])
        brace = Brace(VGroup(items[2], items[3]), RIGHT, color=GREY_B).shift(RIGHT * 0.9)
        self.beat("None of it helps at run time. But all of it needs patching, all of it shows up in scan reports, and an attacker who gets into the container can use those tools as well.",
                  Succession(Wait(1.6), GrowFromCenter(brace), LaggedStart(*[FadeIn(c, shift=LEFT * 0.15) for c in cons], lag_ratio=0.9)), run_time=7.0)
        self.play(FadeOut(VGroup(img, img_t, items, root, cons, brace)), run_time=0.6)

        # ---- 1. two FROM lines, two stages
        LX, RX = -3.55, 3.55
        now = M("FROM python:3.14-slim AS build", 24, YELLOW_M).move_to([0, 3.25, 0])

        def show(text):
            return Transform(now, M(text, 24, YELLOW_M).move_to([0, 3.25, 0]))

        sb = stage_box(LX, "stage: build", GOLD_M)
        fb = stage_box(RX, "final stage", BLUE_M)
        bl, pl = base_bar(LX)
        self.beat("A multi-stage build fixes that. One Dockerfile holds several FROM lines, and each one starts a new stage, from a clean base.",
                  Write(now), Succession(Wait(2.4), AnimationGroup(Create(sb[0]), FadeIn(sb[1]), FadeIn(bl), FadeIn(pl))), run_time=4.6)
        vb = venv_box(LX)
        vpip = chip("pip", RED_M, 20, mono=True).move_to(vb[0]).align_to(vb[0], RIGHT).shift(LEFT * 0.15 + DOWN * 0.42)
        self.beat("The first stage is called build. It makes a virtual environment in /venv: one folder that holds a set of Python packages.",
                  Succession(Wait(1.6), show("RUN python -m venv /venv")), Succession(Wait(2.6), AnimationGroup(Create(vb[0]), FadeIn(vb[1]), FadeIn(vpip))), run_time=5.0)
        pk = pkgs(vb)
        self.steps("It installs the requirements into it. Then it removes pip from it, because pip is only needed to install packages.",
                   (0.8, show("RUN pip install -r requirements.txt")), (1.6, LaggedStart(*[FadeIn(p, scale=0.8) for p in pk], lag_ratio=0.25)),
                   (0.6, Wait(0.6)), (0.8, show("RUN pip uninstall -y pip")), (0.8, vpip.animate.shift(DOWN * 0.5).set_opacity(0)))
        self.remove(vpip)

        br, pr = base_bar(RX)
        self.beat("The final stage starts again, from a fresh python:3.14-slim. Nothing from the build stage is in it.",
                  show("FROM python:3.14-slim"), Succession(Wait(1.0), AnimationGroup(Create(fb[0]), FadeIn(fb[1]), FadeIn(br), FadeIn(pr))), run_time=3.4)
        self.steps("It removes the base image's own pip too. The app does not need it.",
                   (0.8, show("RUN pip uninstall -y pip")), (0.6, Indicate(pr, color=RED_M)), (0.8, pr.animate.shift(DOWN * 0.5).set_opacity(0)))
        self.remove(pr)

        # ---- 2. the one line that crosses
        vcopy = VGroup(vb, pk).copy()
        self.steps("Now the key line. COPY --from=build copies one thing across: the /venv folder, with every package inside it.",
                   (1.0, show("COPY --from=build /venv /venv")), (1.2, Wait(1.2)),
                   (2.0, vcopy.animate(path_arc=-0.6).move_to([RX, vb.get_center()[1], 0])))
        app = chip("app.py", BLUE_M, 22, mono=True).move_to([RX - 1.75, 1.15, 0])
        path = chip("PATH: /venv/bin first", GOLD_M, 20, mono=True).move_to([RX + 0.95, 1.15, 0])
        self.steps("Then it copies app.py. And it puts /venv/bin first on the PATH, so the gunicorn in the venv is the one that runs.",
                   (0.8, show("COPY app.py .")), (0.8, FadeIn(app, shift=DOWN * 0.15)), (1.6, Wait(1.6)),
                   (0.8, show('ENV PATH="/venv/bin:$PATH"')), (0.8, FadeIn(path, shift=DOWN * 0.15)))
        cache = T("stays behind in the build cache", 24, GREY_B).next_to(sb[0], DOWN, buff=0.25)
        the_img = T("this becomes the image", 24, BLUE_M).next_to(fb[0], DOWN, buff=0.25)
        self.beat("Only the last stage becomes the image. The build stage stays behind, in the build cache, on the machine that built it.",
                  Succession(Wait(0.4), FadeIn(the_img, shift=UP * 0.1), fb[0].animate.set_stroke(width=5)),
                  Succession(Wait(2.4), AnimationGroup(VGroup(sb, bl, vb, pk).animate.set_opacity(0.3), FadeIn(cache, shift=UP * 0.1))), run_time=4.6)

        # ---- 3. run as a normal user
        self.play(FadeOut(VGroup(sb, bl, vb, pk, cache)), run_time=0.5)
        user = chip("runs as: root, user ID 0", RED_M, 24).move_to([LX, 0.6, 0])
        self.beat("Next, the user. A container runs as root, user ID 0, unless the image says otherwise.",
                  FadeIn(user, shift=RIGHT * 0.15), run_time=1.6)
        kern = RoundedRectangle(corner_radius=0.1, width=5.6, height=0.62, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.12), 1).move_to([LX, -1.85, 0])
        kern_t = T("the host's shared kernel", 22, GREY_B).move_to(kern)
        esc = Arrow(user.get_bottom(), kern.get_top(), buff=0.15, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.15)
        esc_t = T("breaks out with root's rights", 22, RED_M).next_to(esc, RIGHT, buff=0.15)
        self.beat("Namespaces fence the process in. But it is still root, on a shared kernel. If an attacker breaks out through a bug, they arrive with root's rights.",
                  FadeIn(kern), FadeIn(kern_t), Succession(Wait(4.6), AnimationGroup(GrowArrow(esc), FadeIn(esc_t))), run_time=6.4)
        self.steps("Two lines fix it. useradd creates a normal user, with ID 10001 and no home folder. USER 10001 makes the running container use it.",
                   (1.0, show("RUN useradd --uid 10001 --no-create-home appuser")), (2.6, Wait(2.6)), (0.8, show("USER 10001")),
                   (1.0, Transform(user, chip("runs as: user 10001", GREEN_M, 24).move_to(user)), esc.animate.set_color(GREEN_M), FadeOut(esc_t)))
        nz = T("10001 is plainly not 0", 24, GREEN_M).next_to(esc, RIGHT, buff=0.2)
        self.beat("Write the number, not the name. 10001 is plainly not zero, so Kubernetes can check that it runs as non-root, without looking inside the image.",
                  FadeIn(nz, shift=LEFT * 0.1), Indicate(now, color=YELLOW_M), run_time=2.4)
        ro = T("owned by root: read, not change", 20, BLUE_M).next_to(app, DOWN, buff=0.1).align_to(app, LEFT).shift(LEFT * 0.25)
        own = SurroundingRectangle(app, color=YELLOW_M, buff=0.08, corner_radius=0.1)
        self.beat("The files you copied in still belong to root. So the app can read its own code, but cannot change it. Neither can anyone who breaks into it.",
                  Create(own), Succession(Wait(2.4), FadeIn(ro)), run_time=3.6)
        self.play(FadeOut(VGroup(user, kern, kern_t, esc, nz, own, ro)), FadeOut(now), run_time=0.6)

        # ---- 4. check the gains
        hdr = T("check the gains", 28, YELLOW_M).move_to([LX, 2.35, 0])
        rows = VGroup(
            VGroup(M("whoami", 22, GREY_B), M("root", 22, RED_M), M("uid=10001", 22, GREEN_M)),
            VGroup(M("pip", 22, GREY_B), M("there", 22, RED_M), M("No module named pip", 20, GREEN_M)),
            VGroup(M("size", 22, GREY_B), M("51.8 MB", 22, RED_M), M("49.6 MB", 22, GREEN_M)),
        )
        XS = (-6.3, -4.5, -3.3)
        for i, r in enumerate(rows):
            y = 1.35 - 0.9 * i
            r[0].move_to([XS[0], y, 0], aligned_edge=LEFT)
            r[1].move_to([XS[1], y, 0])
            r[2].move_to([XS[2], y, 0], aligned_edge=LEFT)
        arrows = VGroup(*[Arrow(r[1].get_right(), r[2].get_left(), buff=0.12, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.25) for r in rows])
        cols = VGroup(T("Day 19", 20, GREY_B).move_to([XS[1], 1.95, 0]), T("final", 20, GREY_B).move_to([XS[2], 1.95, 0], aligned_edge=LEFT))
        self.beat("Now check what changed. The app runs as user 10001, and pip is gone.",
                  FadeIn(hdr), FadeIn(cols), LaggedStart(*[AnimationGroup(FadeIn(r), GrowArrow(a)) for r, a in list(zip(rows, arrows))[:2]], lag_ratio=0.6), run_time=3.2)
        self.beat("For this small Python app, the size barely moves. The content went from 51.8 megabytes to 49.6.",
                  FadeIn(rows[2]), GrowArrow(arrows[2]), run_time=2.0)
        scan = VGroup(T("Trivy, HIGH findings in Python packages", 22, GREY_B), VGroup(M("5", 30, RED_M), M("0", 30, GREEN_M)).arrange(RIGHT, buff=1.2))
        scan.arrange(DOWN, buff=0.25).move_to([LX, -1.55, 0])
        sa = Arrow(scan[1][0].get_right(), scan[1][1].get_left(), buff=0.15, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        self.beat("The bigger gain is in the scan. Five HIGH findings sat in libraries that pip carries inside itself. When pip left, they left with it.",
                  FadeIn(scan[0]), FadeIn(scan[1][0]), Succession(Wait(3.6), AnimationGroup(GrowArrow(sa), FadeIn(scan[1][1]))), run_time=5.4)
        self.play(FadeOut(VGroup(hdr, cols, rows, arrows, scan, sa)), run_time=0.5)

        jvm = VGroup(T("a Kotlin service", 26, PURPLE_M),
                     VGroup(chip("JDK", PURPLE_M, 22), chip("Gradle", PURPLE_M, 22)).arrange(RIGHT, buff=0.2),
                     T("stays behind", 22, GREY_B)).arrange(DOWN, buff=0.3).move_to([LX, 0.6, 0])
        jvm2 = VGroup(chip("Java runtime", BLUE_M, 22), chip("the jar", BLUE_M, 22)).arrange(RIGHT, buff=0.2).move_to([LX, -1.3, 0])
        ja = Arrow(jvm.get_bottom(), jvm2.get_top(), buff=0.15, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        ships = T("ships", 22, BLUE_M).next_to(jvm2, DOWN, buff=0.2)
        self.beat("For a Kotlin service the difference is large. The build stage holds a JDK and Gradle. The final stage needs only a Java runtime and the jar.",
                  FadeIn(jvm[0]), Succession(Wait(1.8), FadeIn(jvm[1]), FadeIn(jvm[2])), Succession(Wait(4.2), AnimationGroup(GrowArrow(ja), FadeIn(jvm2), FadeIn(ships))), run_time=6.6)
        self.play(FadeOut(VGroup(jvm, jvm2, ja, ships)), run_time=0.5)

        # ---- 5. recap
        rc = VGroup(T("build with tools in one stage", 28, GOLD_M), T("copy across only /venv", 28, GOLD_M), T("ship the last stage, as user 10001", 28, BLUE_M))
        rc.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([LX, 0.4, 0])
        fit(rc, 6.0)
        self.beat("Build with the tools in one stage. Copy across only what runs. And ship the last stage, as user 10001.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.6), Indicate(vcopy[0][1], color=GOLD_M), run_time=4.4)
        self.wait(1.0)
