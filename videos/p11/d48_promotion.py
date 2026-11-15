import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bApplicationSet\b", "application set"), (r"\byq\b", "Y Q"), (r"\bv1\.1\.0\b", "v 1.1.0"),
            (r"\bnewTag\b", "new tag"), (r"\bbump-image\b", "bump image")])

GX, AX, NX = -4.3, 0.3, 4.6     # columns: git files, Argo CD apps, namespaces
DY, PY = 1.0, -1.2              # rows: dev, prod


def tint(c, k=0.15):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def frame(w, h, color, pos):
    return RoundedRectangle(corner_radius=0.2, width=w, height=h, stroke_color=color, stroke_width=2).move_to(pos)


def ofile(env, tag, y):
    r = RoundedRectangle(corner_radius=0.1, width=3.5, height=1.1, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.08), 1)
    t = M(f"overlays/{env}", 20, GREY_B)
    v = M(f'newTag: "{tag}"', 22, WHITE)
    g = VGroup(t, v).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    return VGroup(r, g.move_to(r)).move_to([GX, y, 0])


def podc(color=TEAL_M):
    return Circle(radius=0.2, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.3), 1)


class D48Promotion(VoiceScene):
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
        self.title_card("Promotion is a pull request", "one image, two environments, every step in git")

        # ---------- 1. two environments in one cluster
        nsd = RoundedRectangle(corner_radius=0.15, width=3.6, height=1.5, stroke_color=TEAL_M, stroke_width=2.5).move_to([NX, DY, 0])
        nsp = RoundedRectangle(corner_radius=0.15, width=3.6, height=1.5, stroke_color=BLUE_M, stroke_width=2.5).move_to([NX, PY, 0])
        nld = M("hello-dev", 20, TEAL_M).next_to(nsd, UP, buff=0.1).align_to(nsd, LEFT)
        nlp = M("hello-prod", 20, BLUE_M).next_to(nsp, UP, buff=0.1).align_to(nsp, LEFT)
        dpods = VGroup(podc()).move_to(nsd).shift(UP * 0.2)
        ppods = VGroup(*[podc() for _ in range(4)]).arrange(RIGHT, buff=0.3).move_to(nsp).shift(UP * 0.2)
        dver = M("1.0.0", 22, GREY_B).next_to(dpods, DOWN, buff=0.18)
        pver = M("1.0.0", 22, GREY_B).next_to(ppods, DOWN, buff=0.18)
        self.beat("Dev is where new versions land first. Prod is what users see. Here both live in your kind cluster, in two namespaces.",
                  Create(nsd), Create(nsp), FadeIn(nld), FadeIn(nlp), GrowFromCenter(dpods[0]),
                  LaggedStart(*[GrowFromCenter(p) for p in ppods], lag_ratio=0.2), FadeIn(dver), FadeIn(pver), run_time=2.6)
        self.beat("Dev runs one Pod. Prod runs four. Both run version 1.0.0 today.",
                  Indicate(dpods, color=TEAL_M), Indicate(ppods, color=BLUE_M), run_time=1.6)

        gfr = frame(4.0, 4.1, GREY_B, [GX, -0.05, 0])
        glab = T("git, branch main", 22, GREY_B).move_to([GX, 1.72, 0])
        fdev, fprod = ofile("dev", "1.0.0", DY - 0.15), ofile("prod", "1.0.0", PY - 0.15)
        self.beat("In git, each environment has its own Kustomize overlay. The line that matters is the image tag.",
                  Create(gfr), FadeIn(glab), FadeIn(fdev, shift=0.1 * RIGHT), FadeIn(fprod, shift=0.1 * RIGHT), run_time=2.0)

        # ApplicationSet stamps out one Application per environment
        aset = VGroup(M("ApplicationSet", 22, GOLD_M), M("env: dev, env: prod", 20, GREY_B), M("hello-devops-{{.env}}", 20, WHITE)).arrange(DOWN, buff=0.12)
        asr = SurroundingRectangle(aset, buff=0.2, corner_radius=0.12, color=GOLD_M, stroke_width=2.5).set_fill(tint(GOLD_M, 0.1), 1)
        asg = VGroup(asr, aset).move_to([AX, -2.95, 0])
        self.beat("Argo CD needs one Application per environment. An ApplicationSet writes them from one template: a list of values, and an Application with a placeholder.",
                  FadeIn(asg, shift=0.15 * UP), run_time=1.8)
        apd = box("hello-devops-dev", TEAL_M, w=3.0, h=0.7, size=20).move_to([AX, DY, 0])
        app = box("hello-devops-prod", BLUE_M, w=3.0, h=0.7, size=20).move_to([AX, PY, 0])
        for a in (apd, app):
            a[1].become(M(a[1].text, 20).move_to(a[1]))
        alab = T("Argo CD", 22, GOLD_M).move_to([AX, 2.0, 0])
        self.steps("The controller fills it in once per entry. Two Applications appear, one for dev and one for prod.",
                   (1.2, TransformFromCopy(asg, apd), FadeIn(alab)), (1.2, TransformFromCopy(asg, app)))
        e1, e2 = edge_arrow(fdev, apd), edge_arrow(fprod, app)
        e3, e4 = edge_arrow(apd, nsd), edge_arrow(app, nsp)
        self.beat("Each one watches its own folder in git, and deploys it to its own namespace.",
                  FadeOut(asg), GrowArrow(e1), GrowArrow(e2), GrowArrow(e3), GrowArrow(e4), run_time=1.8)

        # ---------- 2. the question
        q = T("how does version 1.1.0 get from dev to prod?", 28, YELLOW_M).move_to([0, -3.1, 0])
        self.beat("Now you have a new version, 1.1.0. How does it travel from dev to prod, safely?",
                  FadeIn(q, shift=0.1 * UP), run_time=1.4)

        # step 1: build once
        ci = box("CI", GREY_B, w=1.4, h=0.7, size=26).move_to([-5.6, 3.05, 0])
        img = chip("hello-devops:1.1.0", YELLOW_M, 22, mono=True).move_to([-1.6, 3.05, 0])
        ca = Arrow(ci.get_right(), img.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12)
        once = T("built once", 22, YELLOW_M).next_to(img, RIGHT, buff=0.3)
        self.beat("Step one. You push the tag v1.1.0, and CI builds the image. Once.",
                  FadeOut(q), FadeIn(ci), GrowArrow(ca), Succession(Wait(1.2), AnimationGroup(FadeIn(img, shift=0.1 * RIGHT), FadeIn(once))), run_time=2.6)

        # step 2: PR to dev
        def pr(title, color):
            lines = VGroup(T(title, 22, color), M('-  newTag: "1.0.0"', 20, RED_M), M('+  newTag: "1.1.0"', 20, GREEN_M)).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            r = SurroundingRectangle(lines, buff=0.15, corner_radius=0.12, color=color, stroke_width=2.5).set_fill(tint(color, 0.1), 1)
            return VGroup(r, lines).move_to([AX - 0.2, -2.95, 0])
        pr1 = pr("pull request: dev", TEAL_M)
        self.beat("Step two. A pull request changes one line in the dev overlay.",
                  FadeIn(pr1, shift=0.15 * UP), run_time=1.4)
        merged = chip("merged", GREEN_M, 20).next_to(pr1, RIGHT, buff=0.3)
        nd = M('newTag: "1.1.0"', 22, YELLOW_M).move_to(fdev[1][1], aligned_edge=LEFT)
        self.steps("You merge it. Now git says dev runs 1.1.0.",
                   (0.6, FadeIn(merged)), (1.0, Transform(fdev[1][1], nd)))
        sync = T("sync", 20, GOLD_M).next_to(e3, UP, buff=0.08)
        self.steps("Argo CD sees the change in its folder, and deploys dev.",
                   (1.0, travel(e1, YELLOW_M, 1.0)), (1.0, travel(e3, YELLOW_M, 1.0), FadeIn(sync)),
                   (0.8, dpods[0].animate.set_stroke(YELLOW_M).set_fill(tint(YELLOW_M, 0.3)), Transform(dver, M("1.1.0", 22, YELLOW_M).move_to(dver))))
        tst = VGroup(tick(True, 0.18), T("tested", 20, GREEN_M)).arrange(RIGHT, buff=0.12).next_to(dver, LEFT, buff=0.35)
        self.beat("Step three. You test dev.",
                  FadeOut(sync), FadeIn(tst), run_time=1.0)

        # step 4: PR to prod
        pr2 = pr("pull request: prod", BLUE_M)
        self.beat("Step four. A second pull request sets the prod overlay to the same 1.1.0.",
                  FadeOut(pr1), FadeOut(merged), FadeIn(pr2, shift=0.15 * UP), run_time=1.6)
        rv = VGroup(tick(True, 0.16), T("reviewed", 20, GREEN_M)).arrange(RIGHT, buff=0.12).next_to(pr2, RIGHT, buff=0.3)
        mg2 = chip("merged", GREEN_M, 20).next_to(rv, DOWN, buff=0.15).align_to(rv, LEFT)
        npd = M('newTag: "1.1.0"', 22, YELLOW_M).move_to(fprod[1][1], aligned_edge=LEFT)
        self.steps("Someone reviews it, and merges it.",
                   (0.8, FadeIn(rv)), (0.6, FadeIn(mg2)), (0.8, Transform(fprod[1][1], npd)))
        self.steps("Argo CD syncs prod, and the rollout replaces the four prod Pods, one at a time. Dev is not touched, because its folder did not change.",
                   (1.0, travel(e2, YELLOW_M, 1.0)), (0.8, travel(e4, YELLOW_M, 0.8)),
                   *[(0.55, p.animate.set_stroke(YELLOW_M).set_fill(tint(YELLOW_M, 0.3))) for p in ppods],
                   (0.6, Transform(pver, M("1.1.0", 22, YELLOW_M).move_to(pver))), (1.0, Indicate(nsd, color=TEAL_M)))

        # same bytes
        self.play(FadeOut(VGroup(pr2, rv, mg2)), run_time=0.5)
        same = T("the image was never rebuilt: prod runs the exact bytes dev ran", 24, YELLOW_M).move_to([0, -3.1, 0])
        self.steps("Notice what never happened. The image was never rebuilt. Prod runs the exact bytes that dev ran. Build once, deploy many.",
                   (1.0, Indicate(img, color=YELLOW_M)), (1.0, Indicate(dver, color=YELLOW_M), Indicate(pver, color=YELLOW_M)),
                   (1.0, FadeIn(same, shift=0.1 * UP)))

        # ---------- 3. who writes that one line?
        self.play(FadeOut(same), run_time=0.4)
        wq = T("who writes that one line?", 26, WHITE).move_to([-3.6, -2.45, 0])
        b1 = Rectangle(width=5.6, height=0.32, stroke_width=0).set_fill(RED_M, 0.8).move_to([0.9, -2.95, 0], aligned_edge=LEFT)
        b2 = Rectangle(width=0.07, height=0.32, stroke_width=0).set_fill(GREEN_M, 0.9).move_to([0.9, -3.45, 0], aligned_edge=LEFT)
        k1 = M("kustomize edit set image", 20, GREY_B).next_to(b1, LEFT, buff=0.25)
        k2 = M("yq", 20, GREY_B).next_to(b2, LEFT, buff=0.25).align_to(k1, RIGHT)
        n1 = T("80 lines", 22, WHITE).move_to(b1)
        n2 = T("1 line", 20, GREEN_M).next_to(b2, RIGHT, buff=0.2)
        self.steps("Who writes that line? The classic tool, kustomize edit set image, rewrote the whole prod file: 80 lines changed to set one tag.",
                   (0.8, FadeIn(wq)), (1.2, FadeIn(k1), GrowFromEdge(b1, LEFT)), (0.6, FadeIn(n1)))
        self.beat("yq changes only the field you name. One line. The lab's bump-image workflow uses yq, then pushes a branch and opens the pull request.",
                  FadeIn(k2), GrowFromEdge(b2, LEFT), FadeIn(n2), run_time=1.6)
        self.play(FadeOut(VGroup(wq, b1, b2, k1, k2, n1, n2)), run_time=0.5)

        # ---------- 4. undo
        rev = chip("Revert", RED_M, 22).move_to([-1.0, -3.05, 0])
        self.beat("And if prod misbehaves? Press Revert on the merged pull request. It opens a new one that puts the old tag back.",
                  FadeIn(rev, shift=0.1 * UP), run_time=1.6)
        od = M('newTag: "1.0.0"', 22, WHITE).move_to(fprod[1][1], aligned_edge=LEFT)
        self.steps("Merge it, and Argo CD puts 1.0.0 back.",
                   (0.8, Transform(fprod[1][1], od)), (0.8, travel(e2, GREY_B, 0.8)), (0.8, travel(e4, GREY_B, 0.8)),
                   (0.8, *[p.animate.set_stroke(TEAL_M).set_fill(tint(TEAL_M, 0.3)) for p in ppods], Transform(pver, M("1.0.0", 22, GREY_B).move_to(pver))))
        self.play(FadeOut(rev), run_time=0.4)

        # ---------- 5. why never latest
        lat = M('newTag: "latest"', 22, RED_M).move_to(fprod[1][1], aligned_edge=LEFT)
        self.beat("This only works if a tag always means the same image. Say the overlay said latest instead.",
                  Transform(fprod[1][1], lat), run_time=1.4)
        imgA = chip("image A", GREY_B, 20).move_to([-1.8, -3.05, 0])
        imgB = chip("image B", YELLOW_M, 20).move_to([1.8, -3.05, 0])
        tagl = chip("latest", RED_M, 20, mono=True).next_to(imgA, UP, buff=0.15)
        self.beat("latest points at different images over time. Today image A.",
                  FadeIn(imgA), FadeIn(imgB), FadeIn(tagl), run_time=1.4)
        same_git = T("git: no change", 22, RED_M).move_to([GX, -2.45, 0])
        self.steps("Tomorrow it moves to image B. But the file in git did not change. So Argo CD sees nothing to sync, and git no longer tells you what runs.",
                   (1.0, tagl.animate.next_to(imgB, UP, buff=0.15)), (1.2, Wait(1.2)), (0.8, FadeIn(same_git)), (1.0, Indicate(app, color=RED_M)))
        self.beat("And a revert cannot bring the old version back. Use a version tag like 1.1.0, or a digest, which nobody can move.",
                  FadeOut(VGroup(imgA, imgB, tagl, same_git)), Transform(fprod[1][1], M('newTag: "1.0.0"', 22, WHITE).move_to(fprod[1][1], aligned_edge=LEFT)),
                  run_time=2.0)

        # ---------- 6. recap
        rc = T("build once, then promote the same tag with a pull request", 28).move_to([0, -3.1, 0])
        self.beat("Build the image once. Then promote the same tag from dev to prod with a pull request. Review it, merge it, and let Argo CD deploy it.",
                  FadeIn(rc, shift=0.1 * UP), Indicate(fdev[1][1], color=YELLOW_M), Indicate(fprod[1][1], color=YELLOW_M), run_time=3.0)
        self.wait(1.5)
