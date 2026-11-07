import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

GIT_C = np.array([-4.45, 0.15, 0])      # git repo box (and the CI pipeline before it)
CL_C = np.array([2.65, -0.3, 0])        # the cluster
ARGO_C = np.array([0.4, 1.45, 0])
LIVE_C = np.array([4.6, 1.45, 0])
OLD, NEW = "Hello from Kubernetes!", "Hello from GitOps!"


def dark(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def top(m, z=2):
    m.set_z_index(z)
    return m


def frame(w, h, color, c, fill=0.10, sw=3):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw)
    return r.set_fill(dark(color, fill), opacity=1).move_to(c)


def pod(color=TEAL_M):
    return Circle(radius=0.26, stroke_color=color, stroke_width=3).set_fill(dark(color, 0.25), opacity=1)


def sign(ok):
    g = VGroup(Line(LEFT * 0.24, RIGHT * 0.24).shift(UP * 0.09), Line(LEFT * 0.24, RIGHT * 0.24).shift(DOWN * 0.09))
    if not ok:
        g.add(Line(DL * 0.22 + LEFT * 0.04, UR * 0.22 + RIGHT * 0.04))
    return top(g.set_stroke(GREEN_M if ok else RED_M, 5))


def lchip(text, color, size=22, mono=False):
    """chip() with a solid fill, for things that sit on top of lines or boxes."""
    t = (M if mono else T)(text, size)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.3, height=max(0.6, t.height + 0.3), stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.25), opacity=1)
    return top(VGroup(r, t.move_to(r)), 3)


class D47GitOps(VoiceScene):
    def construct(self):
        self.title_card("GitOps with Argo CD", "git holds the desired state, the cluster pulls it in")

        # ---------- the cluster, with what runs in it
        cl = frame(8.2, 3.8, PURPLE_M, [CL_C[0], 1.05, 0], fill=0.06)
        cl_big = frame(8.2, 6.5, PURPLE_M, CL_C, fill=0.06)
        cl.set_z_index(-1); cl_big.set_z_index(-1)   # the cluster stays behind everything in it, even while it grows
        cl_lab = T("cluster", 26, PURPLE_M).move_to([0, 2.6, 0]).align_to(cl, LEFT).shift(RIGHT * 0.3)
        live = frame(3.8, 1.6, PURPLE_M, LIVE_C, fill=0.14, sw=2.5)
        live_head = top(M("ConfigMap hello-config", 20, GREY_B).move_to(LIVE_C + UP * 0.5))
        live_key = top(M("GREETING:", 20).move_to(LIVE_C + UP * 0.05).align_to(live, LEFT).shift(RIGHT * 0.25))
        live_val = top(T(OLD, 24).move_to(LIVE_C + DOWN * 0.42).align_to(live_key, LEFT))
        live_lab = T("live state", 22, PURPLE_M).next_to(live, UP, buff=0.12).align_to(live, RIGHT)
        pods = VGroup(*[pod() for _ in range(3)]).arrange(RIGHT, buff=0.4).move_to([4.6, 0.05, 0])
        pods_lab = M("hello-devops", 20, GREY_B).next_to(pods, DOWN, buff=0.18)
        cur = {"live": live_val}

        # ---------- part 1: a push deploy
        ci = frame(4.6, 5.0, GREY_B, GIT_C, fill=0.08)
        ci_t = T("CI pipeline", 28).move_to(GIT_C + UP * 2.1)
        steps = VGroup(box("test", GREY_B, w=3.2, h=0.7, size=26), box("build image", GREY_B, w=3.2, h=0.7, size=26),
                       mbox("kubectl apply", GOLD_M, w=3.2, h=0.7, size=22)).arrange(DOWN, buff=0.35).move_to(GIT_C + UP * 0.25)
        sarr = VGroup(*[Arrow(steps[i].get_bottom(), steps[i + 1].get_top(), buff=0.04, stroke_width=3, color=GREY_B,
                              max_tip_length_to_length_ratio=0.35) for i in range(2)])
        self.beat("Start with a push deploy. Your CI pipeline tests the code and builds the image. Its last step is kubectl apply.",
                  Create(ci), Write(ci_t), LaggedStart(*[FadeIn(s, shift=DOWN * 0.1) for s in steps], *[GrowArrow(a) for a in sarr], lag_ratio=0.25), run_time=3.0)
        push = Arrow(steps[2].get_right() + RIGHT * 0.05, pods.get_left() + LEFT * 0.1, buff=0.05, stroke_width=4, color=GOLD_M,
                     max_tip_length_to_length_ratio=0.05)
        push_lab = top(T("push", 24, GOLD_M).next_to(push.get_center(), UP, buff=0.2))
        self.beat("Something outside the cluster sends the change in.",
                  Create(cl), Write(cl_lab), FadeIn(live), FadeIn(live_head), FadeIn(live_key), FadeIn(live_val), FadeIn(live_lab),
                  LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.2), FadeIn(pods_lab), GrowArrow(push), FadeIn(push_lab), run_time=2.4)
        self.play(travel(push, GOLD_M, run_time=1.0), run_time=1.0)

        key = lchip("cluster key", GOLD_M, 22).move_to(GIT_C + DOWN * 1.75)
        self.beat("So CI must hold a key that can write to the cluster. Any workflow that can read that secret can change production.",
                  Succession(FadeIn(key, shift=UP * 0.15), Wait(0.8), Transform(key[0], key[0].copy().set_stroke(RED_M).set_fill(dark(RED_M, 0.3))),
                             Wiggle(key, scale_value=1.12)), run_time=3.6)

        edit = lchip("kubectl edit", RED_M, 22, mono=True).move_to([LIVE_C[0], 3.35, 0])
        hand = top(T("Edited by hand", 24, RED_M).move_to(live_val, aligned_edge=LEFT))
        self.beat("And the deploy only happens while the pipeline runs. If someone edits the cluster an hour later, nothing notices.",
                  Succession(AnimationGroup(ci.animate.set_stroke(opacity=0.35), ci_t.animate.set_opacity(0.35), steps.animate.set_opacity(0.35),
                                            sarr.animate.set_opacity(0.35), push.animate.set_opacity(0.25), push_lab.animate.set_opacity(0.25)),
                             FadeIn(edit, shift=DOWN * 0.3), AnimationGroup(FadeOut(live_val), FadeIn(hand), Circumscribe(live, color=RED_M, buff=0.06))),
                  run_time=5.0)
        cur["live"] = hand

        # ---------- part 2: git is the source of truth, the agent pulls
        git = frame(4.6, 5.0, TEAL_M, GIT_C, fill=0.08)
        git_t = T("Git repo", 28, TEAL_M).move_to(GIT_C + UP * 2.1)
        des_lab = T("desired state", 22, TEAL_M).move_to([0, 0.2, 0]).align_to(git, LEFT).shift(RIGHT * 0.3)
        card = frame(4.2, 2.0, TEAL_M, GIT_C + DOWN * 1.3, fill=0.14, sw=2.5)
        g_head = top(M("k8s/configmap.yaml", 20, GREY_B).move_to(card.get_top() + DOWN * 0.32).align_to(card, LEFT).shift(RIGHT * 0.25))
        g_key = top(M("GREETING:", 20).move_to(card.get_center() + DOWN * 0.02).align_to(g_head, LEFT))
        g_val = top(T(OLD, 24).move_to(card.get_center() + DOWN * 0.5).align_to(g_head, LEFT))
        cur["git"] = g_val
        cibox = frame(2.2, 0.62, GREY_B, [-5.2, -3.1, 0], fill=0.10, sw=2.5)
        ci_s = T("CI", 24).move_to(cibox)
        fresh = top(T(OLD, 24).move_to(hand, aligned_edge=LEFT))
        self.beat("GitOps closes that gap from the other side. Git becomes the only place where changes happen. It holds the desired state.",
                  Succession(AnimationGroup(FadeOut(VGroup(steps, sarr, push, push_lab, edit)), ReplacementTransform(ci, cibox), ReplacementTransform(ci_t, ci_s),
                                            key.animate.move_to([-2.95, -3.1, 0]), FadeOut(hand), FadeIn(fresh)),
                             AnimationGroup(Create(git), Write(git_t)),
                             AnimationGroup(FadeIn(des_lab), Create(card), FadeIn(g_head), FadeIn(g_key), FadeIn(g_val))), run_time=6.0)
        cur["live"] = fresh

        argo = frame(2.6, 1.0, GOLD_M, ARGO_C, fill=0.16)
        argo_t = top(T("Argo CD", 28).move_to(argo))
        self.beat("A program inside the cluster keeps the cluster equal to git, all the time. Here, that program is Argo CD.",
                  GrowFromCenter(argo), Write(argo_t), run_time=1.8)

        pull = Arrow(git.get_right() * [1, 0, 0] + [0, 1.45, 0], argo.get_left(), buff=0.06, stroke_width=4, color=TEAL_M, max_tip_length_to_length_ratio=0.2)
        pull_lab = top(T("pull", 22, TEAL_M).move_to([-1.8, 1.8, 0]))
        apply_a = Arrow(argo.get_right() + UP * 0.2, live.get_left() * [1, 0, 0] + [0, 1.65, 0], buff=0.06, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.2)
        apply_l = top(T("apply", 20, GOLD_M).next_to(apply_a, UP, buff=0.08))
        w0, w1 = live.get_left() * [1, 0, 0] + [-0.06, 1.2, 0], argo.get_right() + [0.06, -0.25, 0]
        watch = DashedLine(w0, w1, dash_length=0.08, stroke_width=2.5, color=GREY_B).add_tip(tip_length=0.14, tip_width=0.14)
        watch_path = Line(w0, w1)
        watch_l = top(T("watch", 20, GREY_B).next_to(watch, DOWN, buff=0.08))
        yml = top(mbox("YAML", TEAL_M, w=0.95, h=0.45, size=20), 3)
        self.beat("Argo CD pulls. It reads git, and applies what it finds.",
                  Succession(AnimationGroup(GrowArrow(pull), FadeIn(pull_lab)),
                             Succession(FadeIn(yml.move_to(pull.get_start() + RIGHT * 0.35), run_time=0.2), yml.animate(run_time=0.9).move_to(argo.get_left() + RIGHT * 0.1),
                                        FadeOut(yml, run_time=0.2)),
                             AnimationGroup(GrowArrow(apply_a), FadeIn(apply_l)), travel(apply_a, GOLD_M, run_time=0.8)), run_time=3.6)
        self.beat("It also watches the live objects it manages, so it sees any change in the cluster within seconds.",
                  Create(watch), FadeIn(watch_l), run_time=1.6)

        up = Arrow(cibox.get_top(), [cibox.get_x(), git.get_bottom()[1], 0], buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        nokey = top(VGroup(Line(key.get_corner(DL), key.get_corner(UR)), Line(key.get_corner(UL), key.get_corner(DR))).set_stroke(RED_M, 4), 4)
        self.beat("CI still tests the code and builds the image. Then it changes a file in git, and that is all CI does. It needs no cluster key at all.",
                  Succession(GrowArrow(up), travel(up, GREY_B, run_time=0.6), Wait(1.5), Create(nokey), FadeOut(VGroup(key, nokey))), run_time=6.0)

        def crow(msg, color=WHITE):
            d = Dot(radius=0.08, color=TEAL_M)
            t = T(msg, 21, color)
            g = VGroup(d, t)
            d.move_to([-6.45, 1.62, 0]); t.next_to(d, RIGHT, buff=0.16)
            return top(g)

        commits = [crow("Deploy hello-devops")]
        self.beat("And git log becomes your deploy log. It shows who changed what, and when.",
                  FadeIn(commits[0], shift=DOWN * 0.15), run_time=1.4)

        # ---------- part 3: compare, Synced
        cmp_lab = T("Argo CD compares", 22, GOLD_M).move_to([0, -0.6, 0]).align_to(cl, LEFT).shift(RIGHT * 0.35)
        r_git = top(lchip("git", TEAL_M, 20, mono=True)).move_to([-0.6, -1.2, 0])
        r_live = top(lchip("live", PURPLE_M, 20, mono=True)).move_to([-0.6, -1.95, 0])
        r_live.align_to(r_git, LEFT)
        c_git = top(T(OLD, 24).next_to(r_git, RIGHT, buff=0.3))
        c_live = top(T(OLD, 24).next_to(r_live, RIGHT, buff=0.3)).align_to(c_git, LEFT)
        cur["cg"], cur["cl"] = c_git, c_live
        sg_pos = np.array([4.35, -1.57, 0])
        eq = sign(True).move_to(sg_pos)
        self.beat("Argo CD keeps comparing two things: the desired state from git, and the live state in the cluster.",
                  Succession(Transform(cl, cl_big), AnimationGroup(FadeIn(cmp_lab), FadeIn(r_git), FadeIn(r_live),
                                                                TransformFromCopy(cur["git"], c_git), TransformFromCopy(cur["live"], c_live))), run_time=3.6)

        sync_l = T("sync", 22, GREY_B)
        sync_c = lchip("Synced", GREEN_M, 24)
        sync = VGroup(sync_l, sync_c).arrange(RIGHT, buff=0.2).move_to([0.9, -2.95, 0])
        heal_l = T("health", 22, GREY_B)
        heal_c = lchip("Healthy", GREEN_M, 24)
        health = VGroup(heal_l, heal_c).arrange(RIGHT, buff=0.2).move_to([4.3, -2.95, 0])
        cur["sync"] = sync_c
        self.beat("When every object it manages matches git, the app is Synced.",
                  GrowFromCenter(eq), FadeIn(sync, shift=UP * 0.1), run_time=1.6)
        self.beat("A second status, health, answers a different question: does it work? Here, Healthy.",
                  FadeIn(health, shift=UP * 0.1), Circumscribe(pods, color=GREEN_M, buff=0.1), run_time=2.0)

        def set_text(k, text, color=WHITE):
            new = top(T(text, 24, color).move_to(cur[k], aligned_edge=LEFT))
            a = AnimationGroup(FadeOut(cur[k]), FadeIn(new))
            cur[k] = new
            return a

        def set_sync(ok):
            new = lchip("Synced" if ok else "OutOfSync", GREEN_M if ok else YELLOW_M, 24).move_to(cur["sync"], aligned_edge=LEFT)
            a = AnimationGroup(FadeOut(cur["sync"]), FadeIn(new))
            cur["sync"] = new
            return a

        def set_sign(ok):
            new = sign(ok).move_to(sg_pos)
            a = AnimationGroup(FadeOut(cur.get("sign", eq)), FadeIn(new))
            cur["sign"] = new
            return a

        # ---------- part 4: drift, OutOfSync, self-heal
        patch = lchip("kubectl patch", RED_M, 22, mono=True).move_to([LIVE_C[0], 3.35, 0])
        self.beat("Now a teammate fixes something by hand. They change the greeting in the live ConfigMap, and skip git.",
                  Succession(FadeIn(patch, shift=DOWN * 0.3), AnimationGroup(set_text("live", "Edited by hand", RED_M), Circumscribe(live, color=RED_M, buff=0.06))),
                  run_time=3.2)
        self.beat("Argo CD sees it at once. Live no longer matches git, so the app is OutOfSync.",
                  Succession(AnimationGroup(travel(watch_path, GREY_B, run_time=0.7), FadeOut(patch)),
                             AnimationGroup(set_text("cl", "Edited by hand", RED_M), set_sign(False)), set_sync(False)), run_time=3.4)
        self.beat("But it is still Healthy, because the app still runs fine. Sync and health are two separate questions.",
                  Wiggle(heal_c, scale_value=1.12), Circumscribe(pods, color=GREEN_M, buff=0.1), run_time=2.0)

        sh = lchip("self-heal: off", GREY_B, 22).move_to([ARGO_C[0], 0.3, 0])
        sh_on = lchip("self-heal: on", GOLD_M, 22).move_to(sh)
        self.beat("By default, Argo CD only reports this drift. Undoing it is a setting called self-heal, and it stays off until you turn it on.",
                  Succession(FadeIn(sh, shift=DOWN * 0.1), Wait(2.2), AnimationGroup(FadeOut(sh), FadeIn(sh_on))), run_time=5.6)
        self.beat("With self-heal on, Argo CD syncs git's version back after a short pause. You did nothing.",
                  Succession(Circumscribe(sh_on, color=GOLD_M, buff=0.06), travel(apply_a, GOLD_M, run_time=0.8),
                             AnimationGroup(set_text("live", OLD), Circumscribe(live, color=GREEN_M, buff=0.06)),
                             AnimationGroup(set_text("cl", OLD), set_sign(True)), set_sync(True)), run_time=4.4)

        # ---------- part 5: a change made the GitOps way
        gp = lchip("git commit, git push", TEAL_M, 22, mono=True).move_to([GIT_C[0], 3.25, 0])
        c2 = crow("Change the greeting")
        self.beat("To change the greeting for good, change git. Edit the file, commit, and push.",
                  Succession(FadeIn(gp, shift=DOWN * 0.2), AnimationGroup(commits[0].animate.shift(DOWN * 0.45), FadeIn(c2, shift=DOWN * 0.15)),
                             AnimationGroup(set_text("git", NEW, YELLOW_M), Circumscribe(card, color=TEAL_M, buff=0.06))), run_time=4.0)
        commits.insert(0, c2)
        self.beat("Argo CD pulls the new commit, and finds that the cluster differs. OutOfSync.",
                  Succession(FadeOut(gp), travel(pull, TEAL_M, run_time=0.8),
                             AnimationGroup(set_text("cg", NEW, YELLOW_M), set_sign(False)), set_sync(False)), run_time=3.6)
        self.beat("So it applies the difference. Synced again, with the new greeting.",
                  Succession(travel(apply_a, GOLD_M, run_time=0.8), set_text("live", NEW, YELLOW_M),
                             AnimationGroup(set_text("cl", NEW, YELLOW_M), set_sign(True)), set_sync(True)), run_time=3.2)

        # ---------- part 6: roll back with git revert
        rv = lchip("git revert HEAD", TEAL_M, 22, mono=True).move_to([GIT_C[0], 3.25, 0])
        c3 = crow('Revert "Change the greeting"')
        self.beat("Now say that commit was a mistake. With GitOps, a rollback is a commit too. You run git revert.",
                  Succession(Indicate(c2, color=RED_M, scale_factor=1.06), FadeIn(rv, shift=DOWN * 0.2)), run_time=3.6)
        self.beat("It makes a new commit that undoes the bad one. History stays intact.",
                  Succession(AnimationGroup(*[c.animate.shift(DOWN * 0.45) for c in commits], FadeIn(c3, shift=DOWN * 0.15)),
                             set_text("git", OLD)), run_time=3.0)
        commits.insert(0, c3)
        self.beat("Push it, and Argo CD deploys the state from before.",
                  Succession(FadeOut(rv), travel(pull, TEAL_M, run_time=0.7), AnimationGroup(set_text("cg", OLD), set_sign(False), set_sync(False)),
                             travel(apply_a, GOLD_M, run_time=0.7), set_text("live", OLD),
                             AnimationGroup(set_text("cl", OLD), set_sign(True)), set_sync(True)), run_time=4.4)

        undo = lchip("kubectl rollout undo", GREY_B, 22, mono=True).move_to([LIVE_C[0], 3.35, 0])
        x = top(VGroup(Line(undo.get_corner(DL), undo.get_corner(UR)), Line(undo.get_corner(UL), undo.get_corner(DR))).set_stroke(RED_M, 4), 4)
        self.beat("Why not kubectl rollout undo? It changes the cluster but not git, so self-heal would put the bad version straight back.",
                  Succession(FadeIn(undo, shift=DOWN * 0.2), Wait(1.2), Create(x)), run_time=4.0)

        # ---------- recap
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
        r1 = T("git holds the desired state", 40, TEAL_M).move_to(UP * 0.7)
        r2 = T("Argo CD, inside the cluster, pulls it and keeps the cluster equal to git", 28).next_to(r1, DOWN, buff=0.5)
        self.beat("Git holds what you want. Argo CD, inside the cluster, pulls it, compares, and keeps the cluster equal to git.",
                  Write(r1), FadeIn(r2, shift=UP * 0.15), run_time=3.0)
        self.wait(1.0)
