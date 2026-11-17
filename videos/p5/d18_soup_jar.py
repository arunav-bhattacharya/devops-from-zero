import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bsha256\b", "shah two fifty six"), (r"\bkB\b", "kilobytes"), (r"\bMB\b", "megabytes"),
            (r"\bpython:3\.14-slim\b", "python three fourteen slim"), (r"\bbig\.bin\b", "big dot bin"), (r"\bdive\b", "dive"),
            (r"\bOverlayFS\b", "overlay F S")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def tier(label, color, w=4.4, h=0.7, size=26, note=None):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.16), opacity=1)
    t = T(label, size, color).move_to(r)
    g = VGroup(r, t)
    return g


class D18SoupJar(VoiceScene):
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
        self.title_card("The soup jar under the sticker", "why deleting a file never makes an image lighter")

        # 1. the stacked lunchbox
        X = -2.6
        soup = tier("soup jar", GOLD_M).move_to([X, -1.6, 0])
        jar = RoundedRectangle(corner_radius=0.12, width=0.7, height=0.5, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.5), opacity=1).move_to(soup).shift(RIGHT * 1.4)
        self.beat("Picture a stacked lunchbox, the kind with tiers that click together. In the bottom tier, you put a heavy jar of soup.",
                  FadeIn(soup, shift=UP * 0.2), FadeIn(jar), run_time=2.0)
        sticker = tier("sticker: \"no soup\"", PURPLE_M).next_to(soup, UP, buff=0.08)
        self.beat("Then you change your mind. So you add a tier on top, with a sticker that says: no soup.",
                  FadeIn(sticker, shift=DOWN * 0.3), run_time=1.6)
        scale_ = VGroup(Line([3.0, -2.2, 0], [5.6, -2.2, 0], stroke_width=4, color=GREY_B), Line([4.3, -2.2, 0], [4.3, -2.9, 0], stroke_width=4, color=GREY_B))
        wt = T("still heavy", 28, RED_M).move_to([4.3, -1.6, 0])
        stack = VGroup(soup, jar, sticker)
        self.steps("Your friend lifts the box and frowns. It is just as heavy as before.",
                   (0.6, Create(scale_)), (0.8, stack.animate.shift(UP * 0.35)), (0.6, FadeIn(wt, shift=DOWN * 0.1)), (0.6, stack.animate.shift(DOWN * 0.35)))
        q = T("if I delete a file, does the image get smaller?", 30, YELLOW_M).move_to([0, 3.0, 0])
        self.beat("Silly with soup. But software images work exactly this way, and smart people get caught. So, today's question. If I delete a file, does the image get smaller?",
                  FadeIn(q, shift=DOWN * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(stack, scale_, wt, q)), run_time=0.6)

        # 2. why tiers at all
        one = RoundedRectangle(corner_radius=0.15, width=4.4, height=3.2, stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.1), opacity=1).move_to([X, 0, 0])
        onel = VGroup(T("one big archive", 28, GREY_B), M("about 135 MB", 24, GREY_B)).arrange(DOWN, buff=0.15).move_to(one)
        lab = M("python:3.14-slim", 26, BLUE_M).next_to(one, UP, buff=0.3)
        self.beat("Last time, we treated an image as one sealed box. Take python 3.14 slim, a base image with Debian Linux and Python inside. It unpacks to about 135 megabytes.",
                  FadeIn(lab), Create(one), FadeIn(onel), run_time=2.2)
        copies = VGroup(*[one.copy().set_opacity(0.0).set_stroke(opacity=0.6).scale(0.35).move_to([2.2 + (i % 4) * 1.15, 1.2 - (i // 4) * 1.4, 0]) for i in range(8)])
        self.steps("If it really were one big archive, every small change to your app would mean shipping all of it again. And ten Python images would store Python ten times.",
                   (2.6, Wait(2.6)), (0.8, Indicate(onel[1], color=GREY_B)), (1.6, LaggedStart(*[TransformFromCopy(one, c) for c in copies], lag_ratio=0.12)))
        self.beat("Wouldn't it be nice to ship and store only what changed?", FadeOut(copies), run_time=1.0)

        # 3. layers
        L1 = tier("Debian files   87.7 MB", BLUE_M).move_to([X, -1.9, 0])
        L2 = tier("Python build   42.1 MB", BLUE_M).next_to(L1, UP, buff=0.08)
        L3 = tier("small layer", BLUE_M, h=0.5, size=24).next_to(L2, UP, buff=0.08)
        L4 = tier("small layer", BLUE_M, h=0.5, size=24).next_to(L3, UP, buff=0.08)
        base = VGroup(L1, L2, L3, L4)
        self.steps("So an image is really a stack of tiers, called layers. Each layer is a set of file changes, compared with the layer below. For this image: Debian files at the bottom, then the Python build, then two small layers.",
                   (0.8, FadeOut(VGroup(one, onel))), (3.4, Wait(3.4)), (0.8, FadeIn(L1, shift=UP * 0.2)), (0.6, FadeIn(L2, shift=DOWN * 0.2)), (0.8, LaggedStart(FadeIn(L3, shift=DOWN * 0.2), FadeIn(L4, shift=DOWN * 0.2), lag_ratio=0.4)))
        df = VGroup(M("RUN  ...   -> a layer", 24, GREEN_M), M("COPY ...   -> a layer", 24, GREEN_M), M("CMD, ENV   -> 0B, settings only", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        df.move_to([3.3, 0.6, 0])
        dft = T("a Dockerfile: the recipe, one step per line", 26, GREY_B).next_to(df, UP, buff=0.35)
        fit(dft, 6.2)
        self.steps("Images are built from a Dockerfile, a recipe with one step per line. A step that changes files, like RUN or COPY, makes a new layer. A step that only changes settings, like CMD or ENV, makes no layer at all.",
                   (0.8, FadeIn(dft)), (2.4, Wait(2.4)), (0.6, FadeIn(df[0])), (0.6, FadeIn(df[1])), (2.0, Wait(2.0)), (0.6, FadeIn(df[2])))
        self.play(FadeOut(VGroup(df, dft)), run_time=0.5)

        # 4. fingerprints: shared layers
        fp = M("sha256:4f2e...", 22, BLUE_M).next_to(L2, RIGHT, buff=0.3)
        self.beat("Every layer is named by its fingerprint, a sha256 digest computed from its bytes. The same content gets the same name, on every machine. Change one byte, and the name changes.",
                  FadeIn(fp, shift=LEFT * 0.1), run_time=1.6)
        self.play(FadeOut(fp), run_time=0.3)
        X2 = 3.0
        base2 = base.copy().move_to([X2, base.get_y(), 0])
        appA = tier("app A file", GREEN_M, h=0.5, size=24).next_to(L4, UP, buff=0.08)
        appB = tier("app B file", TEAL_M, h=0.5, size=24).next_to(base2, UP, buff=0.08)
        self.steps("So now build two images, both starting from python 3.14 slim, each adding one small file.",
                   (0.8, TransformFromCopy(base, base2)), (0.6, FadeIn(appA, shift=DOWN * 0.2)), (0.6, FadeIn(appB, shift=DOWN * 0.2)))
        self.steps("Docker lists each one at about 178 megabytes. But the bottom four layers have the same fingerprints. So they are stored once.",
                   (2.6, Wait(2.6)), (0.8, *[Indicate(b[0], color=BLUE_M) for b in base2]), (1.2, base2.animate.move_to(base).set_opacity(0.0)))
        self.remove(base2)
        appB.generate_target(); appB.target.next_to(appA, UP, buff=0.08)
        uq = VGroup(M("unique: 16.84 kB each", 24, GREEN_M), M("shared: 178.3 MB", 24, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.2, 0.2, 0])
        self.steps("Only 16.84 kilobytes of each image are its own. The other 178.3 megabytes are shared. Pulls and pushes skip shared layers too.",
                   (0.8, MoveToTarget(appB)), (0.6, FadeIn(uq[0])), (1.4, Wait(1.4)), (0.6, FadeIn(uq[1])))
        self.beat("Real lunchboxes cannot share a tier. Images can, because the name comes from the content.", Indicate(uq[1], color=BLUE_M), run_time=1.4)
        self.play(FadeOut(VGroup(appA, appB, uq)), run_time=0.5)

        # 5. the container's own tier: copy-on-write
        ctr = DashedVMobject(RoundedRectangle(corner_radius=0.1, width=4.4, height=0.7, stroke_color=GOLD_M, stroke_width=3), num_dashes=40).next_to(L4, UP, buff=0.12)
        ctl = T("container layer: writable", 26, GOLD_M).move_to(ctr)
        ro = T("read-only", 26, BLUE_M).next_to(base, RIGHT, buff=0.35)
        self.steps("Every layer so far is read-only. When a container starts, Docker adds one thin writable tier on top, for that container alone.",
                   (0.6, FadeIn(ro)), (2.4, Wait(2.4)), (0.8, Create(ctr), FadeIn(ctl)))
        view = VGroup(Line([X, 3.2, 0], [X, 2.7, 0], stroke_width=3, color=WHITE), T("the container looks down from the top", 26)).arrange(RIGHT, buff=0.3)
        view.move_to([X + 1.8, 3.0, 0])
        eye = Arrow([X - 2.8, 2.7, 0], [X - 2.8, -2.2, 0], buff=0, stroke_width=3, color=WHITE, max_tip_length_to_length_ratio=0.05)
        self.steps("The container sees all the tiers merged into one folder tree. To read a file, it looks from the top down, and uses the first copy it finds.",
                   (0.6, FadeIn(view[1])), (1.6, Wait(1.6)), (1.4, GrowArrow(eye)))
        cfg = T("a file", 24, BLUE_M).move_to(L2).shift(RIGHT * 1.3)
        L2t = L2[1]
        self.play(L2t.animate.shift(LEFT * 0.6), FadeIn(cfg), run_time=0.5)
        cfg_up = T("its copy", 24, GOLD_M).move_to(ctr).shift(RIGHT * 1.3)
        self.steps("Now the app changes a file that came from the image. The first write copies the whole file up into the container's tier, and later writes change that copy. That is called copy-on-write.",
                   (2.4, Wait(2.4)), (1.2, TransformFromCopy(cfg, cfg_up), ctl.animate.shift(LEFT * 0.7)), (2.4, Wait(2.4)), (0.6, Indicate(cfg_up, color=GOLD_M)))
        self.beat("The original below never changes. From above, the copy on top simply wins.",
                  cfg.animate.set_opacity(0.4), run_time=1.0)
        self.play(FadeOut(VGroup(cfg, cfg_up, eye, view[1], ro)), L2t.animate.shift(RIGHT * 0.6), ctl.animate.shift(RIGHT * 0.7), run_time=0.5)
        self.play(FadeOut(VGroup(ctr, ctl, base)), run_time=0.5)

        # 6. predict: create in one step, delete in the next
        A1 = tier("alpine:3.22", BLUE_M, w=4.0).move_to([-3.4, -1.9, 0])
        A2 = tier("RUN: make /big.bin  50 MB", GOLD_M, w=4.0, size=24).next_to(A1, UP, buff=0.08)
        A3 = tier("RUN: rm /big.bin", PURPLE_M, w=4.0, size=24).next_to(A2, UP, buff=0.08)
        two = VGroup(A1, A2, A3)
        tl = T("two steps", 28).next_to(two, UP, buff=0.3)
        self.steps("Now the soup. Start from Alpine, a tiny Linux image. One RUN step creates a 50 megabyte file. The next RUN step deletes it.",
                   (0.6, FadeIn(A1), FadeIn(tl)), (2.6, Wait(2.6)), (0.8, FadeIn(A2, shift=DOWN * 0.2)), (1.4, Wait(1.4)), (0.8, FadeIn(A3, shift=DOWN * 0.2)))
        self.beat("The file is gone. Nobody inside the container can see it. So how big is the image? Pause and guess.", Indicate(A3[1], color=PURPLE_M), run_time=1.4)
        self.wait(2.0)
        wo = T("whiteout", 26, PURPLE_M).next_to(A3, RIGHT, buff=0.3)
        self.steps("Remember the rule: a layer can only add changes. So the delete step adds a tiny marker, called a whiteout, that hides the file below. The 50 megabytes stay in their layer, and ship with every pull.",
                   (2.6, Wait(2.6)), (0.6, FadeIn(wo)), (3.0, Wait(3.0)), (0.8, Indicate(A2[0], color=GOLD_M)))
        B1 = tier("alpine:3.22", BLUE_M, w=4.0).move_to([3.4, -1.9, 0])
        B2 = tier("RUN: make && rm", GREEN_M, w=4.0, size=24).next_to(B1, UP, buff=0.08)
        onel2 = T("one step", 28).next_to(VGroup(B1, B2), UP, buff=0.3).align_to(tl, UP)
        self.steps("Compare the same work done in one RUN step, creating and deleting joined with and and.",
                   (0.8, FadeIn(B1), FadeIn(B2, shift=DOWN * 0.2), FadeIn(onel2)), (0.4, wo.animate.set_opacity(0.0)))
        ta, tb = ValueTracker(0), ValueTracker(0)
        pa, pb = tl.get_top() + UP * 0.55, onel2.get_top() + UP * 0.55
        sa_g = always_redraw(lambda: T(f"{ta.get_value():.1f} MB", 36, RED_M).move_to(pa))
        sb_g = always_redraw(lambda: T(f"{tb.get_value():.1f} MB", 36, GREEN_M).move_to(pb))
        self.steps("Weigh both. The two-step image: 53.8 megabytes. The one-step image: 3.8. About fourteen times bigger, for a file nobody can even see.",
                   (0.3, FadeIn(sa_g), FadeIn(sb_g)), (1.8, ta.animate.set_value(53.8)), (1.2, tb.animate.set_value(3.8)), (1.4, Wait(1.4)), (0.6, Wiggle(A2[1])))
        self.beat("The sticker weighs nothing. The soup still weighs fifty megabytes.", Wiggle(A2), run_time=1.4)
        self.remove(wo)

        # 7. name the rule, the fix, and dive
        rule = T("A delete in a later step only hides the file.", 30, YELLOW_M).move_to([0, 2.95, 0])
        sa_g.clear_updaters(); sb_g.clear_updaters()
        self.play(FadeOut(VGroup(sa_g, sb_g)), run_time=0.3)
        self.beat("So here is the rule. A delete in a later step only hides the file. Clean up in the same step. Or, as we will see later, copy only the results into a fresh, clean stage.",
                  FadeIn(rule, shift=DOWN * 0.1), Indicate(B2[0], color=GREEN_M), run_time=2.0)
        dive = VGroup(M("$ CI=true dive", 24, GREY_B), M("efficiency: 14%", 24, RED_M), M("wasted: 50 MB in /big.bin", 24, RED_M), M("FAIL", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        dive.move_to([0, 0.95, 0])
        self.steps("A tool called dive makes the waste visible. It walks the image layer by layer. For the two-step image it said: efficiency 14 percent, 50 megabytes wasted in big dot bin. Fail.",
                   (0.6, FadeIn(dive[0])), (2.8, Wait(2.8)), (0.6, FadeIn(dive[1])), (0.6, FadeIn(dive[2])), (1.0, Wait(1.0)), (0.6, FadeIn(dive[3])))
        self.play(FadeOut(VGroup(dive, rule, two, tl, B1, B2, onel2)), run_time=0.6)

        # 8. guardrail
        g = VGroup(T("size costs you on every pull, every disk, every patch", 28, GREEN_M),
                   T("copy-on-write: copying a big file up is slow", 28, GOLD_M),
                   T("the container tier dies with the container", 28, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([0, 0.4, 0])
        self.steps("Why care? Every deploy and every CI run pulls the image. It takes disk on every machine. And every extra package is one more thing to patch.",
                   (0.8, FadeIn(g[0], shift=UP * 0.1)))
        self.steps("And the writable tier has its own limits. Copying a big file up is slow, and the tier dies with the container. That is why databases keep their files somewhere else, in volumes.",
                   (0.8, FadeIn(g[1], shift=UP * 0.1)), (2.0, Wait(2.0)), (0.8, FadeIn(g[2], shift=UP * 0.1)))
        self.play(FadeOut(g), run_time=0.5)

        # 9. moral and quick check
        mor = VGroup(T("an image is a stack of read-only layers", 28, BLUE_M), T("shared by fingerprint, stored once", 28, BLUE_M),
                     T("a container adds one writable tier on top", 28, GOLD_M), T("a later delete is a sticker, not a removal", 28, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, 0.5, 0])
        self.steps("So, the moral of the story. An image is a stack of read-only layers, shared by fingerprint. A container adds one writable tier on top. And a delete in a later layer is a sticker, not a removal.",
                   (0.6, FadeIn(mor[0], shift=UP * 0.1)), (1.2, Wait(1.2)), (0.6, FadeIn(mor[1], shift=UP * 0.1)), (0.8, Wait(0.8)), (0.6, FadeIn(mor[2], shift=UP * 0.1)), (1.4, Wait(1.4)), (0.6, FadeIn(mor[3], shift=UP * 0.1)))
        self.play(FadeOut(mor), run_time=0.4)
        quiz = T("Quick check: one step downloads a file, a later step deletes it. Did the image shrink?", 26, YELLOW_M).move_to([0, 0.6, 0])
        fit(quiz, 12.4)
        self.beat("Quick check. One step downloads a big file, and a later step deletes it. Did the image shrink?", FadeIn(quiz, shift=UP * 0.1), run_time=1.2)
        self.wait(2.0)
        ans = T("No. The bytes stay below; the delete only hides them.", 28, GREEN_M).next_to(quiz, DOWN, buff=0.35)
        self.beat("No. The bytes stay in the lower layer. The delete only hides them. Clean up in the same step.", FadeIn(ans, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
