import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


def dark(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def frame(w, h, color, c, fill=0.08, sw=3):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw)
    return r.set_fill(dark(color, fill), opacity=1).move_to(c)


def lchip(text, color, size=24, mono=False):
    t = (M if mono else T)(text, size)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.34, height=max(0.6, t.height + 0.3), stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.22), opacity=1)
    return VGroup(r, t.move_to(r)).set_z_index(3)


def bowl(color):
    b = Arc(radius=0.42, start_angle=PI, angle=PI, stroke_color=color, stroke_width=4)
    rim = Line(LEFT * 0.48, RIGHT * 0.48, stroke_color=color, stroke_width=4)
    soup = Polygon(*[0.38 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(PI, 2 * PI, 16)], stroke_width=0).set_fill(color, 0.55)
    return VGroup(soup, b, rim)


def pod(color=TEAL_M):
    return Circle(radius=0.2, stroke_color=color, stroke_width=3).set_fill(dark(color, 0.25), opacity=1)


class D48SignedCard(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("One soup, two rooms", "moving a tested version from dev to prod with GitOps")

        # ---------------- 1. the soup that changed on the way
        tk = frame(4.6, 3.4, BLUE_M, [-3.6, 0.0, 0], fill=0.06)
        tk_t = T("test kitchen", 28, BLUE_M).move_to(tk.get_top() + DOWN * 0.4)
        mr = frame(4.6, 3.4, GOLD_M, [3.6, 0.0, 0], fill=0.06)
        mr_t = T("main dining room", 28, GOLD_M).move_to(mr.get_top() + DOWN * 0.4)
        self.beat("Picture the restaurant from last time, now with a second room. Next door, the owner has opened a small test kitchen.",
                  Create(mr), Write(mr_t), Create(tk), Write(tk_t), run_time=2.4)
        s1 = bowl(GREEN_M).move_to(tk.get_center() + DOWN * 0.1)
        s1_l = T("Tuesday: a hit", 26, GREEN_M).next_to(s1, DOWN, buff=0.35)
        self.beat("New dishes are tried there on a few regulars first. On Tuesday, a new soup is a hit.",
                  FadeIn(s1, shift=UP * 0.2), FadeIn(s1_l), run_time=1.8)
        s2 = bowl(RED_M).move_to(mr.get_center() + DOWN * 0.1)
        s2_l = T("Friday: from memory", 26, RED_M).next_to(s2, DOWN, buff=0.35)
        salt = T("+ salt, other stock", 22, GREY_B).next_to(s2, UP, buff=0.25)
        self.beat("On Friday, the main kitchen cooks it from memory. A little more salt. A different stock.",
                  FadeIn(s2, shift=UP * 0.2), FadeIn(s2_l), FadeIn(salt), run_time=1.8)
        qm = T("?", 60, YELLOW_M).next_to(mr, RIGHT, buff=0.1).shift(LEFT * 0.9 + UP * 0.6)
        self.beat("The regulars ask why it tastes wrong. An easy trap: it feels like the same soup. Same name, same pot, same cooks.",
                  FadeIn(qm, scale=1.4), Indicate(s2, color=RED_M), run_time=2.0)
        q = T("How does a dish move from one room to the other without changing on the way?", 30, YELLOW_M)
        fit(q, 12.6).to_edge(UP, buff=0.6)
        self.play(VGroup(tk, tk_t, mr, mr_t, s1, s1_l, s2, s2_l, salt, qm).animate.shift(DOWN * 0.5), run_time=0.5)
        self.beat("So here is our question. How does a dish move from one room to the other, without changing on the way?", Write(q), run_time=2.2)
        self.wait(0.5)
        self.play(FadeOut(VGroup(tk, tk_t, mr, mr_t, s1, s1_l, s2, s2_l, salt, qm, q)), run_time=0.7)

        # ---------------- 2. two environments from shared files
        CC = np.array([3.5, 0.3, 0])
        clu = frame(5.2, 5.0, PURPLE_M, CC, fill=0.04)
        clu_t = T("cluster", 26, PURPLE_M).move_to(clu.get_top() + DOWN * 0.38)
        dev = frame(4.4, 2.0, BLUE_M, CC + UP * 0.95, fill=0.10, sw=2.5)
        dev_t = M("hello-dev", 22, BLUE_M).move_to(dev.get_corner(UL) + RIGHT * 0.85 + DOWN * 0.3)
        prod = frame(4.4, 2.0, GOLD_M, CC + DOWN * 1.35, fill=0.10, sw=2.5)
        prod_t = M("hello-prod", 22, GOLD_M).move_to(prod.get_corner(UL) + RIGHT * 0.95 + DOWN * 0.3)
        dpods = VGroup(pod(BLUE_M)).move_to(dev.get_center() + DOWN * 0.25 + LEFT * 1.2)
        dsay = T("Hello from dev!", 24, BLUE_M).next_to(dpods, RIGHT, buff=0.4)
        ppods = VGroup(*[pod(GOLD_M) for _ in range(4)]).arrange(RIGHT, buff=0.25).move_to(prod.get_center() + DOWN * 0.25 + LEFT * 0.6)
        pmem = T("more memory", 22, GOLD_M).next_to(ppods, RIGHT, buff=0.3)
        self.beat("Software teams keep the same pair of rooms. Each running copy of the app, with one purpose, is called an environment.",
                  Create(clu), Write(clu_t), run_time=1.6)
        self.beat("Dev is the test kitchen, where new versions land first. In the lab it runs one copy, and answers Hello from dev.",
                  Create(dev), Write(dev_t), GrowFromCenter(dpods[0]), FadeIn(dsay), run_time=2.0)
        self.beat("Prod is the main room, the copy your users see. It runs four copies, with more memory.",
                  Create(prod), Write(prod_t), LaggedStart(*[GrowFromCenter(p) for p in ppods], lag_ratio=0.15), FadeIn(pmem), run_time=2.0)
        GC = np.array([-3.7, 0.3, 0])
        git = frame(5.0, 5.0, TEAL_M, GC, fill=0.05)
        git_t = T("git repo (the board)", 26, TEAL_M).move_to(git.get_top() + DOWN * 0.38)
        base = mbox("k8s/  shared files", TEAL_M, size=22, w=3.6, h=0.7).move_to(GC + UP * 1.35)
        od = mbox("overlays/dev", BLUE_M, size=22, w=3.6, h=0.7).move_to(GC + DOWN * 0.05)
        op = mbox("overlays/prod", GOLD_M, size=22, w=3.6, h=0.7).move_to(GC + DOWN * 1.35)
        self.beat("Both rooms run from one board. The shared files sit in one folder, and each environment gets an overlay: a folder that changes a few settings on top.",
                  Create(git), Write(git_t), FadeIn(base), FadeIn(od, shift=DOWN * 0.1), FadeIn(op, shift=DOWN * 0.1), run_time=3.0)
        # tags in the overlays
        dtag = M('newTag: "1.2.0"', 22, BLUE_M).next_to(od, DOWN, buff=0.12)
        ptag = M("newTag: old tag", 22, GOLD_M).next_to(op, DOWN, buff=0.12)
        self.play(FadeIn(dtag), FadeIn(ptag), run_time=0.5)
        self.beat("Each overlay also names the version to run. An image is your app, packed with everything it needs. Its tag is the version label.",
                  Indicate(dtag, color=BLUE_M), Indicate(ptag, color=GOLD_M), run_time=2.0)
        argo = frame(1.6, 0.8, GREY_B, [0, 0.0, 0], fill=0.10)
        argo_t = T("Argo CD", 24).move_to(argo).set_z_index(2)
        ad = Arrow(od.get_right(), dev.get_left(), buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.1)
        ap = Arrow(op.get_right(), prod.get_left(), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.1)
        argo.move_to([-0.15, 2.75, 0]); argo_t.move_to(argo)
        self.beat("Argo CD, the manager from last time, deploys each overlay to its own namespace.",
                  FadeIn(argo), FadeIn(argo_t), GrowArrow(ad), GrowArrow(ap), Succession(Wait(0.5), AnimationGroup(travel(ad, BLUE_M, 0.8), travel(ap, GOLD_M, 0.8))), run_time=2.4)
        main = VGroup(clu, clu_t, dev, dev_t, prod, prod_t, dpods, dsay, ppods, pmem, git, git_t, base, od, op, dtag, ptag, argo, argo_t, ad, ap)

        # ---------------- 3. the ApplicationSet: one blank board with gaps
        self.play(main.animate.set_opacity(0.15), run_time=0.5)
        tmpl = VGroup(M("name: hello-devops-{{.env}}", 24), M("path: overlays/{{.env}}", 24), M("namespace: hello-{{.env}}", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        tb = frame(tmpl.width + 0.7, tmpl.height + 0.6, TEAL_M, [0, 0, 0], fill=0.12)
        tg = VGroup(tb, tmpl.move_to(tb)).move_to([-2.6, 1.1, 0])
        tg_t = T("template", 26, TEAL_M).next_to(tg, UP, buff=0.2)
        lst = VGroup(M("env: dev", 24, BLUE_M), M("env: prod", 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        lb = frame(lst.width + 0.7, lst.height + 0.6, GREY_B, [0, 0, 0], fill=0.10)
        lg = VGroup(lb, lst.move_to(lb)).move_to([3.6, 1.1, 0])
        lg_t = T("list", 26, GREY_B).next_to(lg, UP, buff=0.2)
        self.beat("Argo CD needs one Application per environment. You could copy the file and change three lines. That works, until someone forgets one.",
                  run_time=None)
        self.beat("An ApplicationSet writes those copies for you. It has a template: an ordinary Application with gaps in it.",
                  Create(tb), Write(tmpl), FadeIn(tg_t), run_time=2.4)
        self.beat("And it has a list that says which word goes in the gaps. In the restaurant, it is a blank board, filled in once for each room.",
                  Create(lb), Write(lst), FadeIn(lg_t), run_time=2.4)
        a1 = lchip("hello-devops-dev", BLUE_M, 24, mono=True).move_to([-2.0, -1.5, 0])
        a2 = lchip("hello-devops-prod", GOLD_M, 24, mono=True).move_to([2.4, -1.5, 0])
        self.beat("Apply it, and two Applications appear: hello-devops-dev, and hello-devops-prod.",
                  TransformFromCopy(VGroup(tg, lst[0]), a1), TransformFromCopy(VGroup(tg, lst[1]), a2), run_time=2.2)
        more = T("delete the ApplicationSet: its apps go too", 24, GREY_B).next_to(VGroup(a1, a2), DOWN, buff=0.45)
        self.beat("Delete the ApplicationSet, and its apps go too, with everything they deployed.",
                  FadeIn(more, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(tg, tg_t, lg, lg_t, a1, a2, more)), main.animate.set_opacity(1), run_time=0.7)
        # restore fills that set_opacity(1) made solid
        for f, c, a in ((clu, PURPLE_M, 0.04), (git, TEAL_M, 0.05), (dev, BLUE_M, 0.10), (prod, GOLD_M, 0.10)):
            f.set_fill(dark(c, a), opacity=1)

        # ---------------- 4. predict: how does 1.2.0 move to prod?
        self.beat("Now the real question. Version 1.2.0 runs well in dev. How do you move it to prod?", Indicate(dtag, color=BLUE_M), run_time=1.6)
        self.play(main.animate.set_opacity(0.12), run_time=0.4)
        opts = VGroup(T("A. rebuild the image from main for prod", 28), T("B. run kubectl set image in the prod namespace", 28),
                      T("C. copy the 1.2.0 tag into the prod folder with a pull request", 28), T("D. click Sync on the prod app", 28))
        opts.arrange(DOWN, aligned_edge=LEFT, buff=0.38).move_to(UP * 0.1)
        fit(opts, 12.4)
        self.beat("Four answers. Rebuild the image for prod. Change prod by hand with kubectl. Copy the tag into the prod folder with a pull request. Or click Sync on prod.",
                  LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.5), run_time=6.0)
        self.guess([0, -2.6, 0])
        xs = [tick(False, 0.25).next_to(opts[i], LEFT, buff=0.2) for i in (0, 1, 3)]
        n1 = T("a new soup with an old name", 24, RED_M).next_to(opts[0], DOWN, buff=0.08).align_to(opts[0], LEFT).shift(RIGHT * 0.5)
        self.beat("Let's be fair to each one. A rebuild sounds harmless, but it can produce a slightly different app. A new soup, with an old name.",
                  Create(xs[0]), opts[0].animate.set_opacity(0.5), run_time=1.6)
        self.beat("A hand edit with kubectl skips the board, so Argo CD undoes it.", Create(xs[1]), opts[1].animate.set_opacity(0.5), run_time=1.4)
        self.beat("And Sync only applies what git already says. Git still says the old tag for prod.", Create(xs[2]), opts[3].animate.set_opacity(0.5), run_time=1.4)
        ok = tick(True, 0.25).next_to(opts[2], LEFT, buff=0.2)
        self.beat("That leaves the pull request. Promotion is a small text change in git.", Create(ok), opts[2].animate.set_color(GREEN_M), run_time=1.4)
        self.play(FadeOut(VGroup(opts, ok, *xs)), main.animate.set_opacity(1), run_time=0.6)
        for f, c, a in ((clu, PURPLE_M, 0.04), (git, TEAL_M, 0.05), (dev, BLUE_M, 0.10), (prod, GOLD_M, 0.10)):
            f.set_fill(dark(c, a), opacity=1)

        # ---------------- 5. the promotion, step by step
        reg = lchip("hello-devops:1.2.0", GREEN_M, 24, mono=True).move_to([-3.7, -2.85, 0])
        once = T("built once", 22, GREEN_M).next_to(reg, RIGHT, buff=0.25)
        dold = M("newTag: old tag", 22, BLUE_M).move_to(dtag)
        self.beat("Let's replay the whole journey, from the start.", ReplacementTransform(dtag, dold), dpods[0].animate.set_fill(dark(GREY_B, 0.3)), run_time=1.2)
        dtag = dold
        self.beat("Step one. CI builds the image once, when you push the tag v1.2.0.", FadeIn(reg, shift=UP * 0.2), FadeIn(once), run_time=1.6)
        pr1 = lchip("pull request: dev to 1.2.0", BLUE_M, 22).move_to([2.3, -2.85, 0])
        dnew = M('newTag: "1.2.0"', 22, BLUE_M).move_to(dtag)
        self.beat("Step two. A pull request sets the dev overlay to 1.2.0. You merge it, and Argo CD deploys dev.",
                  FadeIn(pr1, shift=UP * 0.1), ReplacementTransform(dtag, dnew), Succession(Wait(0.6), travel(ad, BLUE_M, 0.8)),
                  dpods[0].animate.set_fill(dark(GREEN_M, 0.4)), run_time=2.8)
        dtag = dnew
        self.beat("Step three. You test dev, the way the regulars taste the soup.", Circumscribe(dev, color=BLUE_M), run_time=1.4)
        pr2 = lchip("pull request: prod to 1.2.0", GOLD_M, 22).move_to(pr1)
        sign = lchip("reviewed, merged: prod to 1.2.0", GREEN_M, 22).move_to(pr2)
        ptag2 = M('newTag: "1.2.0"', 22, GOLD_M).move_to(ptag)
        self.beat("Step four. A second pull request sets the prod overlay to the same 1.2.0. Someone reviews it and merges it. That is the head chef's signature on the card.",
                  FadeOut(pr1), FadeIn(pr2), Succession(Wait(1.0), AnimationGroup(ReplacementTransform(ptag, ptag2), ReplacementTransform(pr2, sign))), run_time=3.4)
        ptag = ptag2
        self.beat("Argo CD sees the change, and deploys prod.",
                  travel(ap, GOLD_M, 0.9), LaggedStart(*[p.animate.set_fill(dark(GREEN_M, 0.4)) for p in ppods], lag_ratio=0.2), run_time=1.8)
        same = T("built once: dev and prod run the same bytes", 22, GREEN_M).next_to(reg, RIGHT, buff=0.25)
        self.beat("Notice what never happened. The image was never rebuilt. Prod runs the exact bytes that dev ran. Build once, deploy many.",
                  FadeOut(sign), Succession(Indicate(reg, color=GREEN_M), ReplacementTransform(once, same)), run_time=2.6)
        undo = T("Revert on the merged pull request puts the old tag back", 22, GREY_B).move_to(same, aligned_edge=LEFT)
        self.beat("And you get a clean undo for free. Press Revert on the merged pull request, and a new one puts the old tag back.",
                  ReplacementTransform(same, undo), run_time=1.6)
        same = undo
        rule = T("Build once, and move that same image.", 30, YELLOW_M).to_edge(UP, buff=0.5)
        self.play(FadeOut(VGroup(argo, argo_t)), run_time=0.3)
        self.beat("So the rule. A rebuilt image is a new soup with an old name. Build once, and move that same image.", Write(rule), run_time=1.8)
        self.wait(0.4)
        self.play(FadeOut(VGroup(rule, same)), run_time=0.5)

        # ---------------- 6. break it: latest
        lt = M('newTag: "latest"', 22, RED_M).move_to(ptag)
        self.beat("This only works if a tag always means the same image. So let's break it. Set prod to the tag latest.",
                  ReplacementTransform(ptag, lt), run_time=1.6)
        ptag = lt
        imgA = lchip("image A", GREEN_M, 24).move_to([-0.2, -2.85, 0])
        imgB = lchip("image B", RED_M, 24).move_to([2.2, -2.85, 0])
        ptr = Arrow(reg.get_right() + RIGHT * 0.1, imgA.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        reg2 = lchip("hello-devops:latest", RED_M, 24, mono=True).move_to(reg)
        self.beat("On Monday, latest points at one image.", ReplacementTransform(reg, reg2), FadeIn(imgA), GrowArrow(ptr), run_time=1.4)
        reg = reg2
        ptr2 = Arrow(reg.get_right() + RIGHT * 0.1, imgB.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("On Wednesday, it points at another. Git did not change at all, but what runs did.",
                  FadeIn(imgB), ReplacementTransform(ptr, ptr2), imgA.animate.set_opacity(0.4), run_time=1.6)
        self.beat("Ordering latest is like ordering the chef's surprise. Lovely at a birthday dinner. Not for the main room on a Friday.",
                  Wiggle(ptag), run_time=1.8)
        self.beat("So the point is: with latest, git no longer tells you what runs, and a revert cannot bring the old version back.",
                  Indicate(ptag, color=RED_M), run_time=1.8)
        dig = M("@sha256:...", 22, GREEN_M).move_to(ptag)
        good = T("a version like 1.2.0 is good; a digest is stronger", 22, GREEN_M).move_to([0.6, -2.85, 0])
        self.beat("A version like 1.2.0 is good. A digest is stronger: a fingerprint worked out from the image's contents, so nobody can move it to a different image.",
                  FadeOut(VGroup(imgA, imgB, ptr2, reg)), ReplacementTransform(ptag, dig), FadeIn(good), run_time=2.4)
        ptag = dig
        self.wait(0.3)
        self.play(FadeOut(VGroup(clu, clu_t, dev, dev_t, prod, prod_t, dpods, dsay, ppods, pmem, ad, ap, good)), run_time=0.6)

        gitg = VGroup(git, git_t, base, od, op, dtag, ptag)
        self.play(gitg.animate.scale(0.8).move_to([-4.3, 0.4, 0]), run_time=0.6)

        # ---------------- 8. guardrails
        g = VGroup(T("prod moves only by a reviewed pull request", 28),
                   T("never latest: a version, or better, a digest", 28),
                   T("Image Updater may write dev's tags; it commits with no review", 28),
                   T("no password on the board: only locked secrets, or pointers", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        g.move_to([1.5, 0.3, 0]); fit(g, 7.6)
        gt = T("Guardrails", 30, GOLD_M).next_to(g, UP, buff=0.4).align_to(g, LEFT)
        self.beat("A few guardrails. Prod moves only by a reviewed pull request.", Write(gt), FadeIn(g[0], shift=RIGHT * 0.1), run_time=1.6)
        self.beat("Never latest. Use a version, or better, a digest.", FadeIn(g[1], shift=RIGHT * 0.1), run_time=1.2)
        self.beat("An add-on, Argo CD Image Updater, can write new tags for you, but it commits straight to the branch, with no signature. My advice: let it handle dev at most, and keep prod on pull requests.",
                  FadeIn(g[2], shift=RIGHT * 0.1), run_time=1.6)
        self.beat("And nobody writes the safe's code on the board. A password in git is no longer a secret, so commit only locked secrets, or pointers to them.",
                  FadeIn(g[3], shift=RIGHT * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(g, gt, gitg)), run_time=0.6)

        # ---------------- 9. moral, recap, check
        moral = T("Build once. Move the same image, with a signed card.", 36, YELLOW_M).move_to(UP * 2.4)
        fit(moral, 12.6)
        self.beat("So the moral of the story. Build once, and move the same image, with a signed card.", Write(moral), run_time=1.8)
        rec = VGroup(T("dev is the test kitchen, prod is the main room", 28, BLUE_M),
                     T("one blank board, filled in per room: the ApplicationSet", 28, TEAL_M),
                     T("promotion: a pull request copies the tested tag", 28, GREEN_M),
                     T("a rebuild or latest is a new soup with an old name", 28, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("Dev is the test kitchen, prod the main room. One blank board, filled in per room. A dish moves as a signed card that copies the tag dev already ran. And a rebuild, or latest, is a new soup with an old name.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=8.0)
        self.play(FadeOut(rec), run_time=0.5)
        c1 = T("Quick check: you add  env: staging  to the ApplicationSet's list.", 30).move_to(UP * 0.4)
        c2 = T("What do you get?", 30).next_to(c1, DOWN, buff=0.3)
        fit(c1, 12.6)
        self.beat("A quick check. You add a third entry, env staging, to the ApplicationSet's list. What do you get?",
                  FadeIn(c1), FadeIn(c2), run_time=1.8)
        self.guess([0, -1.2, 0])
        ans = T("A third Application, from the same template. Nothing copied.", 30, GREEN_M).next_to(c2, DOWN, buff=0.6)
        self.beat("A third Application, written from the same template. Nobody copied a file, so nobody forgot a line.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.2)
