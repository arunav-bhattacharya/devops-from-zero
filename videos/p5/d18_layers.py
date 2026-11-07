import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


def tint(color, a=0.22):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def layer(name, size="", color=GREY_B, w=5.0, h=0.42, fs=22, mono=True):
    """One image layer: a flat filled slab with a name on the left and a size on the right."""
    r = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2).set_fill(tint(color), 1)
    g = VGroup(r)
    if name:
        n = (M if mono else T)(name, fs, WHITE)
        n.move_to(r.get_left() + RIGHT * (n.width / 2 + 0.2))
        g.add(n)
    else:
        g.add(VGroup())
    if size:
        s = T(size, fs, GREY_B).move_to(r.get_right() + LEFT * 0.2, aligned_edge=RIGHT)
        g.add(s)
    else:
        g.add(VGroup())
    return g


def flash(b, color=YELLOW_M, rt=1.2):
    return ShowPassingFlash(b[0].copy().set_fill(opacity=0).set_stroke(color, 7), time_width=0.6, run_time=rt)


def ring(l, color, sw=3.5):
    """A coloured outline drawn over a layer (does not touch the layer itself)."""
    return l[0].copy().set_fill(opacity=0).set_stroke(color, sw)


def code_panel(lines, fs=22, w=6.0, color=GREY_B):
    rows = VGroup(*[M(l, fs) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    r = RoundedRectangle(corner_radius=0.15, width=w, height=rows.height + 0.8, stroke_color=color, stroke_width=2)
    r.set_fill(BLACK, 1)
    rows.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.35)
    return VGroup(r, rows)


def tag(text, color, fs=22):
    return chip(text, color, fs, mono=True)


class D18Layers(VoiceScene):
    def construct(self):
        self.title_card("Image layers and the build cache", "why one changed step rebuilds every step after it")

        # ---- 1. a Dockerfile builds a stack of layers
        df = code_panel(["FROM python:3.14-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt",
                         "COPY app.py .", 'CMD ["gunicorn", ...]'], fs=22, w=6.3).move_to([-3.6, 0.55, 0])
        df_l = T("Dockerfile", 26, GREY_B).next_to(df, UP, buff=0.2).align_to(df, LEFT)
        rows = df[1]
        self.beat("An image is built from a Dockerfile, a list of build steps that Docker follows from top to bottom.",
                  Create(df[0]), FadeIn(df_l), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in rows], lag_ratio=0.15), run_time=3.0)

        X = 3.75
        base = VGroup(layer("Debian files", "87.7 MB", GREY_B, h=0.5, mono=False), layer("Python", "42.1 MB", GREY_B, h=0.46, mono=False),
                      layer("", "", GREY_B, h=0.3), layer("", "", GREY_B, h=0.3)).arrange(UP, buff=0.06)
        base.move_to([X, -2.75, 0], aligned_edge=DOWN)
        rest = VGroup(layer("WORKDIR /app", "8.19 kB", BLUE_M), layer("COPY requirements.txt", "12.3 kB", BLUE_M),
                      layer("RUN pip install", "26.7 MB", GOLD_M, h=0.5), layer("COPY app.py", "12.3 kB", TEAL_M))
        for i, l in enumerate(rest):
            l.next_to(base if i == 0 else rest[i - 1], UP, buff=0.06)
        for l in rest:
            l[2].set_opacity(0)
        img_l = M("hello-devops:1.0.0", 24, WHITE).move_to([X, 2.95, 0])
        bb = Brace(base, LEFT, buff=0.1, color=GREY_B)
        bb_l = T("base image", 22, GREY_B).next_to(bb, LEFT, buff=0.1)

        def point(i, lay):
            a = Arrow([df[0].get_right()[0] + 0.05, rows[i].get_y(), 0], lay.get_left() + LEFT * 0.05, buff=0.05, stroke_width=2.5, color=YELLOW_M,
                      max_tip_length_to_length_ratio=0.12)
            return a

        hl = SurroundingRectangle(rows[0], color=YELLOW_M, buff=0.08, stroke_width=2)
        p0 = point(0, base)
        self.beat("The first step picks a base image. The slim Python image already brings four layers: Debian files, the Python build, and two small ones.",
                  Create(hl), GrowArrow(p0), FadeIn(img_l), LaggedStart(*[GrowFromEdge(b, DOWN) for b in base], lag_ratio=0.4), run_time=3.4)
        self.play(FadeOut(p0), FadeIn(bb_l), GrowFromCenter(bb), run_time=0.6)

        anims = []
        for i, l in enumerate(rest):
            anims.append(Succession(hl.animate(run_time=0.3).become(SurroundingRectangle(rows[i + 1], color=YELLOW_M, buff=0.08, stroke_width=2)),
                                    FadeIn(l, shift=DOWN * 0.3, run_time=0.6)))
        ro = T("every layer: read-only", 26, BLUE_M).next_to(base, DOWN, buff=0.28)
        self.beat("Each step that changes files adds one read-only layer, on top of the ones below. A layer holds only the file changes that one step made.",
                  Succession(*anims, FadeIn(ro, run_time=0.6)), run_time=4.4)
        self.beat("The pip install layer holds the weight, 26.7 megabytes. The code layer is only 12.3 kilobytes.",
                  *[l[2].animate.set_opacity(1) for l in rest], flash(rest[2], GOLD_M), run_time=2.2)

        cfg = layer("config: CMD, ENV, ...", "0B", PURPLE_M, h=0.5).next_to(rest[-1], UP, buff=0.45)
        p5 = point(5, cfg)
        self.beat("Steps that only change settings, like the default command, add no layer. They only edit the image's config.",
                  hl.animate.become(SurroundingRectangle(rows[5], color=YELLOW_M, buff=0.08, stroke_width=2)), GrowArrow(p5), FadeIn(cfg, shift=DOWN * 0.2),
                  run_time=2.4)
        self.wait(0.2)

        # ---- 2. layers are named by their content
        self.play(FadeOut(VGroup(df, df_l, cfg, bb, bb_l, p5, hl)), FadeOut(ro), run_time=0.6)
        hexes = ["e4f2a91c", "07bd53e8", "c3a96f10", "5a1e7d24", "9b80c4f3", "2fd6e0a7", "71c5b9e2", "d84a3c6f"]
        digs = VGroup()
        for h, l in zip(hexes, [*base, *rest]):
            digs.add(M(f"sha256:{h}...", 20, GREY_B).next_to(l, LEFT, buff=0.35))
        same = T("same content, same name, on every machine", 26, TEAL_M).move_to([0, 3.35, 0])
        self.beat("Docker names every layer by its digest, a sha256 hash of its content. The same content gets the same name, on every machine.",
                  LaggedStart(*[FadeIn(d, shift=RIGHT * 0.15) for d in digs], lag_ratio=0.12), FadeOut(img_l),
                  Succession(Wait(1.6), FadeIn(same, shift=DOWN * 0.15)), run_time=4.0)
        top = rest[3]
        newd = M("sha256:6e19f8b0...", 20, RED_M).move_to(digs[7], aligned_edge=RIGHT)
        byte = T("1 byte changed", 22, RED_M).next_to(top, UP, buff=0.15)
        self.beat("Change one byte, and the name changes.",
                  Create(ring(top, RED_M)), FadeIn(byte, shift=DOWN * 0.1), Transform(digs[7], newd), run_time=1.6)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        # two images on one base
        def tower(x, name):
            b = VGroup(layer("Debian files", "", GREY_B, w=3.6, h=0.46, mono=False, fs=22), layer("Python", "", GREY_B, w=3.6, h=0.42, mono=False),
                       layer("", "", GREY_B, w=3.6, h=0.26), layer("", "", GREY_B, w=3.6, h=0.26)).arrange(UP, buff=0.06)
            t = layer("one small file", "", TEAL_M, w=3.6, h=0.42, mono=False).next_to(b, UP, buff=0.06)
            g = VGroup(b, t).move_to([x, -0.9, 0])
            lab = M(name, 22, WHITE).next_to(g, UP, buff=0.3)
            return g, lab

        A, Al = tower(-3.4, "image one")
        B, Bl = tower(3.4, "image two")
        self.beat("Images share layers. Build two images from the same base, each adding one small file.",
                  LaggedStart(FadeIn(A, shift=UP * 0.2), FadeIn(Al), FadeIn(B, shift=UP * 0.2), FadeIn(Bl), lag_ratio=0.25), run_time=2.6)
        eqs = VGroup(*[T("=", 30, TEAL_M).move_to([0, A[0][i].get_y(), 0]) for i in range(2)])
        self.beat("Their four base layers are the same bytes, with the same digests.",
                  *[flash(A[0][i], TEAL_M) for i in range(4)], *[flash(B[0][i], TEAL_M) for i in range(4)],
                  FadeIn(eqs), run_time=2.0)
        nb = VGroup(layer("Debian files", "", GREY_B, w=7.3, h=0.46, mono=False), layer("Python", "", GREY_B, w=7.3, h=0.42, mono=False),
                    layer("", "", GREY_B, w=7.3, h=0.26), layer("", "", GREY_B, w=7.3, h=0.26)).arrange(UP, buff=0.06).move_to([0, -1.7, 0])
        shared = nb
        At, Bt = A[1], B[1]
        ty = nb.get_top()[1] + 0.27
        self.beat("So your disk and the registry store them only once.",
                  FadeOut(eqs), ReplacementTransform(A[0], nb), B[0].animate.move_to(nb).set_opacity(0),
                  At.animate.move_to([-1.85, ty, 0]), Bt.animate.move_to([1.85, ty, 0]),
                  Al.animate.move_to([-1.85, ty + 0.65, 0]), Bl.animate.move_to([1.85, ty + 0.65, 0]), run_time=2.2)
        self.remove(B[0])
        sh_l = T("shared: 178.3 MB", 26, GREY_B).next_to(shared, DOWN, buff=0.3)
        ua = T("its own: 16.84 kB", 24, TEAL_M).next_to(Al, UP, buff=0.2)
        ub = T("its own: 16.84 kB", 24, TEAL_M).next_to(Bl, UP, buff=0.2)
        each = T("each image: 178 MB", 26, WHITE).move_to([0, 2.3, 0])
        self.beat("docker system df listed each image at 178 megabytes. But only 16.84 kilobytes of each was its own.",
                  FadeIn(each), FadeIn(sh_l), LaggedStart(FadeIn(ua, shift=DOWN * 0.1), FadeIn(ub, shift=DOWN * 0.1), lag_ratio=0.5), run_time=3.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        # ---- 3. the container's thin writable layer
        W = 6.2
        nl = VGroup(layer("", "", GREY_B, w=W, h=0.62), layer("", "", GREY_B, w=W, h=0.62), layer("", "", GREY_B, w=W, h=0.62)).arrange(UP, buff=0.08)
        nl.move_to([-3.3, -1.5, 0])
        conf = tag("nginx.conf", GREY_B).move_to([-5.27, nl[1].get_y(), 0])
        page = tag("50x.html", GREY_B).move_to([-1.12, nl[2].get_y(), 0])
        nl_l = T("nginx image: read-only", 24, GREY_B).next_to(nl, DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.15) for l in nl], lag_ratio=0.2), FadeIn(conf), FadeIn(page), FadeIn(nl_l), run_time=1.2)
        wl = layer("", "", GOLD_M, w=W, h=0.62).next_to(nl, UP, buff=0.08)
        wl_l = T("container layer: writable", 24, GOLD_M).next_to(wl, UP, buff=0.22)
        self.beat("Start a container from the nginx image, and Docker adds one thin writable layer on top.",
                  GrowFromEdge(wl, DOWN), FadeIn(wl_l, shift=DOWN * 0.1), run_time=2.2)

        view = RoundedRectangle(corner_radius=0.15, width=5.4, height=3.3, stroke_color=WHITE, stroke_width=2).move_to([3.9, -0.9, 0])
        v_l = T("what the container sees", 24, WHITE).next_to(view, UP, buff=0.2)
        slash = M("/", 30).move_to(view.get_corner(UL) + RIGHT * 0.4 + DOWN * 0.4)
        v_conf = conf.copy()
        v_page = page.copy()
        VGroup(v_conf, v_page).arrange(DOWN, buff=0.16, aligned_edge=LEFT).next_to(slash, DOWN, buff=0.2).align_to(slash, LEFT).shift(RIGHT * 0.3)
        ov = T("OverlayFS: one merged tree", 24, GREY_B).next_to(view, DOWN, buff=0.25)
        self.beat("OverlayFS shows all the layers as one folder tree. That merged view is the container's root folder.",
                  Create(view), FadeIn(v_l), Write(slash), TransformFromCopy(conf, v_conf), TransformFromCopy(page, v_page), FadeIn(ov), run_time=3.0)

        scan = Arrow(UP * 0.5, DOWN * 0.5, buff=0, stroke_width=5, color=YELLOW_M, max_tip_length_to_length_ratio=0.3)
        scan.next_to(wl, LEFT, buff=0.25)
        self.beat("A read looks from the top layer down, and uses the first copy of the file it finds.",
                  FadeIn(scan), Succession(scan.animate(run_time=1.2).next_to(nl[1], LEFT, buff=0.25), Indicate(conf, color=YELLOW_M, run_time=0.8)),
                  run_time=2.2)
        up = conf.copy().set_color(GOLD_M)
        up[0].set_stroke(GOLD_M).set_fill(GOLD_M, 0.18)
        cmark = M("C", 24, GOLD_M)
        self.beat("The first write to that file copies the whole file up, into the container layer. Later writes change that copy. This is copy-on-write.",
                  FadeOut(scan), up.animate.move_to([conf.get_x(), wl.get_y(), 0]), v_conf[0].animate.set_stroke(GOLD_M), run_time=2.2)
        up.move_to([conf.get_x(), wl.get_y(), 0])
        new = tag("/tmp/new.txt", GOLD_M).move_to([-3.01, wl.get_y(), 0])
        v_new = new.copy().next_to(v_page, DOWN, buff=0.16, aligned_edge=LEFT)
        self.beat("A new file goes straight into the container layer.",
                  FadeIn(new, shift=DOWN * 0.2), TransformFromCopy(new, v_new), run_time=1.6)
        wo = Rectangle(width=page.width, height=page.height, stroke_color=WHITE, stroke_width=2).set_fill(WHITE, 0.85)
        wo.stretch_to_fit_width(1.25).move_to([page.get_x(), wl.get_y(), 0])
        wo_l = T("whiteout", 20, BLACK)
        wo_l.move_to(wo)
        page_gone = page.copy().set_opacity(0.35)
        self.beat("A delete only adds a small marker, a whiteout, that hides the file below.",
                  FadeIn(VGroup(wo, wo_l), shift=DOWN * 0.2), FadeOut(v_page), Transform(page, page_gone),
                  v_new.animate.move_to(v_page, aligned_edge=LEFT), run_time=2.4)
        diff = VGroup(M("$ docker diff web", 22, WHITE), M("C /etc/nginx/nginx.conf", 20, GOLD_M), M("A /tmp/new.txt", 20, GOLD_M),
                      M("D /usr/share/nginx/html/50x.html", 20, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        diff.move_to(view).align_to(view, LEFT).shift(RIGHT * 0.25)
        self.beat("docker diff lists those changes: C for changed, A for added, and D for deleted.",
                  FadeOut(VGroup(slash, v_conf, v_new, ov)), Transform(v_l, T("only the container layer", 24, GOLD_M).move_to(v_l)),
                  LaggedStart(*[FadeIn(d, shift=RIGHT * 0.15) for d in diff], lag_ratio=0.3), run_time=2.8)
        self.beat("Remove the container, and its layer goes with it. The image never changes.",
                  FadeOut(VGroup(wl, wl_l, up, new, wo, wo_l), shift=UP * 0.3), FadeOut(VGroup(view, v_l, diff)),
                  page.animate.set_opacity(1), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        # ---- 4. the build cache
        good = ["FROM python:3.14-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt", "COPY app.py ."]
        df2 = code_panel(good, fs=22, w=6.3).move_to([-3.6, 0.4, 0])
        rows2 = df2[1]
        LW, LX = 3.2, 2.0
        stk = VGroup(layer("base layers", "", GREY_B, w=LW, h=0.6, mono=False), layer("WORKDIR", "", BLUE_M, w=LW, h=0.5),
                     layer("COPY requirements", "", BLUE_M, w=LW, h=0.5, fs=20), layer("RUN pip install", "", GOLD_M, w=LW, h=0.5),
                     layer("COPY app.py", "", TEAL_M, w=LW, h=0.5)).arrange(UP, buff=0.07).move_to([LX, 0.2, 0])
        cache_l = T("build cache", 26, GREY_B).next_to(stk, UP, buff=0.3)
        def status(i, text, color):
            return tag(text, color, 20).next_to(stk[i], RIGHT, buff=0.3)

        cached = VGroup(*[status(i, "CACHED", GREEN_M) for i in range(1, 5)])
        cur = SurroundingRectangle(rows2[1], color=YELLOW_M, buff=0.08, stroke_width=2)
        steps_anim = [Create(cur)]
        for i in range(1, 5):
            steps_anim.append(Succession(cur.animate(run_time=0.25).become(SurroundingRectangle(rows2[i], color=YELLOW_M, buff=0.08, stroke_width=2)),
                                         FadeIn(cached[i - 1], shift=LEFT * 0.15, run_time=0.45)))
        self.beat("Back to building. Docker keeps every layer it builds in a build cache. On the next build, if a step and everything before it are unchanged, Docker reuses the saved layer, and prints CACHED.",
                  Succession(AnimationGroup(FadeIn(df2), LaggedStart(*[FadeIn(l, shift=UP * 0.15) for l in stk], lag_ratio=0.2), FadeIn(cache_l), run_time=1.6),
                             Wait(1.4), *steps_anim), run_time=6.4)
        self.play(FadeOut(cur), FadeOut(cached), run_time=0.5)

        edit = T("requirements.txt edited", 24, RED_M).next_to(df2, DOWN, buff=0.35).align_to(df2, LEFT)
        reb = VGroup(status(1, "CACHED", GREEN_M), *[status(i, "rebuild", RED_M) for i in (2, 3, 4)])
        rings = VGroup(*[ring(stk[i], RED_M) for i in (2, 3, 4)])
        self.beat("But if something changed, Docker rebuilds that layer, and every layer after it, even ones whose steps did not change.",
                  FadeIn(edit), rows2[2].animate.set_color(RED_M), FadeIn(reb[0]),
                  LaggedStart(*[AnimationGroup(FadeIn(r, shift=LEFT * 0.15), Create(rr)) for r, rr in zip(reb[1:], rings)],
                              lag_ratio=0.45), run_time=3.0)
        why = VGroup(T("each layer = changes on top of", 24, GREY_B), T("the exact layers below it", 24, GREY_B)).arrange(DOWN, buff=0.15)
        why.move_to([0, -3.15, 0])
        self.beat("Why? Each layer holds the changes one step made, on top of the exact layers below it. If a lower layer changes, Docker cannot know whether a later pip install would give the same result, without running it again.",
                  FadeIn(why, shift=UP * 0.15), flash(stk[3], YELLOW_M, 2.0), run_time=3.0)
        self.play(FadeOut(VGroup(edit, reb, why, rings)), rows2[2].animate.set_color(WHITE), run_time=0.6)

        # the order of steps
        bad = ["FROM python:3.14-slim", "WORKDIR /app", "COPY . .", "RUN pip install -r requirements.txt", 'CMD ["gunicorn", ...]']
        df_bad = code_panel(bad, fs=22, w=6.3, color=RED_M).move_to(df2)
        stk_bad = VGroup(stk[0].copy(), stk[1].copy(), layer("COPY . .", "", TEAL_M, w=LW, h=0.5), stk[3].copy()).arrange(UP, buff=0.07)
        stk_bad.move_to(stk, aligned_edge=DOWN)
        self.beat("So the order of the steps matters. Say you copy all your code first, and install after.",
                  FadeTransform(df2, df_bad), FadeTransform(stk, stk_bad), FadeOut(cache_l), run_time=2.2)
        e2 = T("one comment edited in app.py", 24, RED_M).next_to(df_bad, DOWN, buff=0.35).align_to(df_bad, LEFT)
        rb2 = VGroup(status(0, "CACHED", GREEN_M).next_to(stk_bad[1], RIGHT, buff=0.3),
                     tag("rebuild", RED_M, 20).next_to(stk_bad[2], RIGHT, buff=0.3), tag("rebuild", RED_M, 20).next_to(stk_bad[3], RIGHT, buff=0.3))
        slow = T("about 10 s, every edit", 26, RED_M).next_to(stk_bad, DOWN, buff=0.4)
        self.beat("Now edit one comment in your code. The copy step changes, so the slow install runs again, on every single edit.",
                  FadeIn(e2), df_bad[1][2].animate.set_color(RED_M), LaggedStart(*[FadeIn(r, shift=LEFT * 0.15) for r in rb2], lag_ratio=0.35),
                  Create(ring(stk_bad[2], RED_M)), Create(ring(stk_bad[3], RED_M)), FadeIn(slow), run_time=3.0)
        self.play(FadeOut(VGroup(e2, rb2, slow)), run_time=0.5)

        df_good = code_panel(good, fs=22, w=6.3, color=GREEN_M).move_to(df_bad)
        stk_good = VGroup(layer("base layers", "", GREY_B, w=LW, h=0.6, mono=False), layer("WORKDIR", "", BLUE_M, w=LW, h=0.5),
                          layer("COPY requirements", "", BLUE_M, w=LW, h=0.5, fs=20), layer("RUN pip install", "", GOLD_M, w=LW, h=0.5),
                          layer("COPY app.py", "", TEAL_M, w=LW, h=0.5)).arrange(UP, buff=0.07).move_to(stk_bad, aligned_edge=DOWN)
        order = T("rarely changed  →  often changed", 26, GREEN_M).move_to([0, 3.3, 0])
        old = [m for m in self.mobjects if m not in (df_bad, stk_bad)]
        self.beat("So order the steps from rarely changed to often changed: the base image, then the requirements file on its own, then pip install, and the code last.",
                  Succession(AnimationGroup(FadeOut(Group(*old)), FadeOut(df_bad), FadeIn(df_good), FadeOut(stk_bad), FadeIn(stk_good), FadeIn(order), run_time=1.2),
                             *[Indicate(df_good[1][i], color=GREEN_M, scale_factor=1.06, run_time=0.9) for i in (0, 2, 3, 4)]), run_time=5.4)
        e3 = T("one comment edited in app.py", 24, TEAL_M).next_to(df_good, DOWN, buff=0.35).align_to(df_good, LEFT)
        rb3 = VGroup(*[tag("CACHED", GREEN_M, 20).next_to(stk_good[i], RIGHT, buff=0.3) for i in (1, 2, 3)],
                     tag("rebuild", GOLD_M, 20).next_to(stk_good[4], RIGHT, buff=0.3))
        fast = T("0.3 s, against about 10 s", 26, GREEN_M).next_to(stk_good, DOWN, buff=0.4)
        self.beat("Now a code edit rebuilds only the last, small layer. In the lesson, that build took 0.3 seconds, against about 10 seconds for a fresh pip install.",
                  FadeIn(e3), LaggedStart(*[FadeIn(r, shift=LEFT * 0.15) for r in rb3], lag_ratio=0.3), Create(ring(stk_good[4], GOLD_M)),
                  FadeIn(fast), run_time=3.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        # ---- recap
        rec = VGroup(
            VGroup(T("layers", 34, BLUE_M), T("read-only, named by content, shared", 30, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("container", 34, GOLD_M), T("one thin writable layer on top", 30, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("cache", 34, GREEN_M), T("a change rebuilds everything after it", 30, GREY_B)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("Layers are read-only, named by their content, and shared. A container adds one thin writable layer. And a change rebuilds every step after it, so slow, stable steps go first.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rec], lag_ratio=0.5), run_time=4.0)
        self.wait(1.0)
