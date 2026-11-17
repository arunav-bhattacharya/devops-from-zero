import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

OLD = "Hello from Kubernetes!"


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


def person(color=GOLD_M, s=1.0):
    head = Circle(radius=0.16, stroke_color=color, stroke_width=3).set_fill(dark(color, 0.3), opacity=1)
    body = Arc(radius=0.3, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(head, DOWN, buff=0.04)
    return VGroup(head, body).scale(s)


def pod(color=TEAL_M):
    return Circle(radius=0.24, stroke_color=color, stroke_width=3).set_fill(dark(color, 0.25), opacity=1)


class D47BoardRoom(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("The board and the room", "GitOps with Argo CD, told in a restaurant")

        # ---------------- 1. the restaurant: a board and a room that drift apart
        board = frame(3.8, 3.4, TEAL_M, [-4.3, 0.2, 0], fill=0.08)
        b_head = T("Tonight", 30, TEAL_M).move_to(board.get_top() + DOWN * 0.45)
        b_lines = VGroup(T("6 tables, all apart", 26), T("fish: on", 26), T("3 cooks", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        b_lines.next_to(b_head, DOWN, buff=0.4)
        b_lab = T("the board", 26, TEAL_M).next_to(board, DOWN, buff=0.25)
        room = frame(5.6, 3.4, PURPLE_M, [3.3, 0.2, 0], fill=0.05)
        r_lab = T("the room", 26, PURPLE_M).next_to(room, DOWN, buff=0.25)
        tables = VGroup(*[Circle(radius=0.32, stroke_color=GREY_B, stroke_width=3).set_fill(GREY_D, 0.5) for _ in range(6)])
        tables.arrange_in_grid(2, 3, buff=(0.9, 0.7)).move_to(room.get_center() + LEFT * 0.7)
        fish = lchip("fish", BLUE_M, 24).move_to(room.get_center() + RIGHT * 1.9 + UP * 0.6)
        self.beat("Picture a small restaurant on a busy Friday night. On the kitchen wall hangs a board with tonight's plan.",
                  Create(board), Write(b_head), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in b_lines], lag_ratio=0.3), FadeIn(b_lab), run_time=2.6)
        self.beat("And out front is the room, where the plan really happens.",
                  Create(room), FadeIn(r_lab), LaggedStart(*[GrowFromCenter(t) for t in tables], lag_ratio=0.1), FadeIn(fish), run_time=2.0)
        joined = RoundedRectangle(corner_radius=0.3, width=1.6, height=0.85, stroke_color=GOLD_M, stroke_width=3)
        self.beat("Around seven, a waiter joins two tables for a big group.",
                  tables[1].animate.move_to(tables[0].get_center() + RIGHT * 0.66), run_time=1.4)
        joined.move_to(VGroup(tables[0], tables[1]))
        self.play(Create(joined), run_time=0.5)
        cross = tick(False, 0.35).move_to(fish).set_z_index(4)
        self.beat("A cook takes the fish off, because it ran out.", Create(cross), fish.animate.set_opacity(0.4), run_time=1.0)
        self.beat("Nobody writes any of it on the board.",
                  Succession(Indicate(b_lines[0], color=TEAL_M), Indicate(b_lines[1], color=TEAL_M)), run_time=1.8)
        neq = VGroup(Line(LEFT * 0.3, RIGHT * 0.3).shift(UP * 0.1), Line(LEFT * 0.3, RIGHT * 0.3).shift(DOWN * 0.1),
                     Line(DL * 0.28, UR * 0.28)).set_stroke(RED_M, 5).move_to([-0.15, 0.2, 0])
        self.beat("By nine, the board and the room tell two different stories. And the next shift believes the board.",
                  Create(neq), run_time=1.2)
        q = T("Who keeps the board and the room in step?", 34, YELLOW_M).to_edge(UP, buff=0.7)
        self.beat("So here is the question. Who keeps the board and the room in step?", Write(q), run_time=1.8)
        self.wait(0.6)
        rest = VGroup(board, b_head, b_lines, b_lab, room, r_lab, tables, joined, fish, cross, neq, q)
        self.play(FadeOut(rest), run_time=0.7)

        # ---------------- 2. the familiar way: apply from laptops
        cl = frame(4.4, 3.2, PURPLE_M, [3.6, 0.0, 0], fill=0.05)
        cl_t = T("cluster", 28, PURPLE_M).move_to(cl.get_top() + DOWN * 0.4)
        cl_pods = VGroup(*[pod() for _ in range(3)]).arrange(RIGHT, buff=0.4).move_to(cl.get_center() + DOWN * 0.2)
        lap = mbox("kubectl apply -k k8s", GOLD_M, size=24, h=0.8).move_to([-3.8, 0.0, 0])
        lap_l = T("your laptop", 26, GOLD_M).next_to(lap, UP, buff=0.25)
        a0 = Arrow(lap.get_right(), cl.get_left(), buff=0.1, stroke_width=4, color=GOLD_M, max_tip_length_to_length_ratio=0.08)
        self.beat("Software has the same problem. All through the last part, you told the cluster what to run with one command, from your laptop.",
                  Create(cl), Write(cl_t), LaggedStart(*[GrowFromCenter(p) for p in cl_pods], lag_ratio=0.2), FadeIn(lap), FadeIn(lap_l), GrowArrow(a0), run_time=3.0)
        self.beat("For one person, that is fine. One cook writes the board and cooks the food.", travel(a0, GOLD_M, 1.0), run_time=1.2)
        laps = VGroup(*[mbox("kubectl apply", GOLD_M, size=22, h=0.7) for _ in range(3)]).arrange(DOWN, buff=0.55).move_to([-3.8, 0.0, 0])
        arrs = VGroup(*[Arrow(l.get_right(), cl.get_left() + UP * (0.8 - 0.8 * i), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.08) for i, l in enumerate(laps)])
        self.beat("Add a few colleagues, and it breaks in quiet ways.",
                  FadeOut(lap_l), ReplacementTransform(lap, laps[1]), FadeIn(laps[0]), FadeIn(laps[2]), ReplacementTransform(a0, arrs[1]), GrowArrow(arrs[0]), GrowArrow(arrs[2]), run_time=1.8)
        pains = VGroup(T("a fix by hand at night, never in the files", 26), T("the last apply wins", 26),
                       T("which version is running right now?", 26), T("every laptop holds a key to the cluster", 26))
        pains.arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(DOWN, buff=0.6)
        pains.set_color(GREY_A)
        self.play(VGroup(cl, cl_t, cl_pods, laps, arrs).animate.shift(UP * 1.0), run_time=0.6)
        self.beat("Someone fixes the app by hand at night and never updates the files.", FadeIn(pains[0], shift=UP * 0.1), run_time=1.0)
        self.beat("Two people apply different versions, and the last one wins. A fine rule for a pillow fight, and a poor one for the real system your users depend on.",
                  FadeIn(pains[1], shift=UP * 0.1), Succession(travel(arrs[0], GOLD_M, 0.6), travel(arrs[2], RED_M, 0.6)), run_time=2.0)
        self.beat("Nobody can say which version is running. And every laptop holds a key that can change the cluster.",
                  FadeIn(pains[2], shift=UP * 0.1), FadeIn(pains[3], shift=UP * 0.1), run_time=1.8)
        drift = T("drift: the files say one thing, the cluster runs another", 28, RED_M).to_edge(UP, buff=0.55)
        self.beat("That difference, between what the files say and what really runs, has a name. Drift. It is our Friday night board, in software.",
                  Write(drift), run_time=2.0)
        wish = T("wish: one place for every change, and someone who keeps the room equal to it", 26, YELLOW_M).move_to(drift)
        self.beat("Wouldn't it be nice if there were one place where every change happens, and someone who keeps the room equal to it, all the time?",
                  FadeOut(pains), ReplacementTransform(drift, fit(wish, 12.6)), run_time=2.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(cl, cl_t, cl_pods, laps, arrs, wish)), run_time=0.7)

        # ---------------- 3. the map: git is the board, the cluster is the room, Argo CD is the manager
        GC = np.array([-4.45, 0.25, 0])
        git = frame(3.7, 4.6, TEAL_M, GC, fill=0.08)
        git_t = T("git repo", 28, TEAL_M).move_to(git.get_top() + DOWN * 0.4)
        git_a = T("the board", 24, GREY_B).next_to(git_t, DOWN, buff=0.12)
        g_file = M("k8s/configmap.yaml", 22, GREY_B).move_to(GC + UP * 0.75)
        g_key = M("GREETING:", 22).next_to(g_file, DOWN, buff=0.3).align_to(g_file, LEFT)
        g_val = T(OLD, 26).next_to(g_key, DOWN, buff=0.18).align_to(g_file, LEFT)
        g_rep = M("replicas: 3", 22).next_to(g_val, DOWN, buff=0.35).align_to(g_file, LEFT)
        CC = np.array([2.55, 0.25, 0])
        clu = frame(7.6, 4.6, PURPLE_M, CC, fill=0.05)
        clu_t = T("cluster", 28, PURPLE_M).move_to(clu.get_corner(UL) + RIGHT * 0.85 + DOWN * 0.4)
        clu_a = T("the room", 24, GREY_B).next_to(clu_t, RIGHT, buff=0.25)
        LC = np.array([4.35, 1.05, 0])
        live = frame(3.5, 1.55, PURPLE_M, LC, fill=0.14, sw=2.5)
        l_key = M("GREETING:", 22).move_to(LC + UP * 0.32).align_to(live, LEFT).shift(RIGHT * 0.25)
        l_val = T(OLD, 26).move_to(LC + DOWN * 0.3).align_to(l_key, LEFT)
        pods = VGroup(*[pod() for _ in range(3)]).arrange(RIGHT, buff=0.35).move_to([4.35, -0.75, 0])
        pods_l = T("3 copies of hello-devops", 22, GREY_B).next_to(pods, DOWN, buff=0.2)
        self.beat("Back to the restaurant, with new names. The board is git, the tool that keeps every saved version of your files.",
                  Create(git), Write(git_t), FadeIn(git_a), run_time=2.0)
        self.beat("On the board: a file that sets the greeting of hello-devops, our tiny web app, and how many copies should run.",
                  FadeIn(g_file), FadeIn(g_key), Write(g_val), FadeIn(g_rep), run_time=2.4)
        self.beat("The room is the cluster, the group of machines where the app really runs.",
                  Create(clu), Write(clu_t), FadeIn(clu_a), Create(live), FadeIn(l_key), FadeIn(l_val),
                  LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.2), FadeIn(pods_l), run_time=2.6)
        AC = np.array([0.15, 0.55, 0])
        argo = frame(2.3, 1.0, GOLD_M, AC, fill=0.16)
        argo_t = T("Argo CD", 28).move_to(argo).set_z_index(2)
        mgr = person(GOLD_M, 0.9).next_to(argo, UP, buff=0.15)
        self.beat("And the floor manager is a program that lives inside the cluster. Here, that program is Argo CD.",
                  FadeIn(mgr, shift=DOWN * 0.2), GrowFromCenter(argo), Write(argo_t), run_time=1.8)
        pull = Arrow(git.get_right() + UP * 0.3, argo.get_left() + UP * 0.1, buff=0.08, stroke_width=4, color=TEAL_M, max_tip_length_to_length_ratio=0.2)
        pull_l = T("reads", 22, TEAL_M).next_to(pull, UP, buff=0.08)
        self.beat("Notice the direction. Nobody phones changes in from outside. The manager walks over and reads the board.",
                  GrowArrow(pull), FadeIn(pull_l), Succession(Wait(0.6), travel(pull, TEAL_M, 1.0)), run_time=2.2)
        cmp_ = Arrow(argo.get_right() + UP * 0.15, live.get_left() + DOWN * 0.1, buff=0.08, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.2)
        cmp_l = T("compares, fixes", 22, GOLD_M).next_to(cmp_, DOWN, buff=0.06).shift(DOWN * 0.15)
        self.beat("Then it looks at the room, compares the two, and applies only the difference. Then it does it again. And again.",
                  GrowArrow(cmp_), FadeIn(cmp_l), Succession(Wait(0.4), travel(cmp_, GOLD_M, 0.8), travel(pull, TEAL_M, 0.8), travel(cmp_, GOLD_M, 0.8)), run_time=3.4)
        timing = VGroup(T("board: checked about every 3 minutes", 22, TEAL_M), T("room: watched, changes seen in seconds", 22, GOLD_M))
        timing.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([0.9, -1.55, 0])
        self.beat("How often? It checks git about every three minutes: a hundred and twenty seconds, plus a random wait of up to sixty, so many apps do not all ask at once.",
                  FadeIn(timing[0], shift=UP * 0.1), run_time=1.2)
        self.beat("The room it watches all the time, so a change in the cluster is seen within seconds.", FadeIn(timing[1], shift=UP * 0.1), run_time=1.0)
        name = T("GitOps: files in git say what should run, and a program keeps the real system matching them", 24, YELLOW_M)
        fit(name, 12.6).to_edge(UP, buff=0.55)
        self.beat("Now this idea has earned its name. Files in git say what should run, and a program keeps the real system matching them. That is GitOps.",
                  Write(name), run_time=2.6)
        ci_n = T("CI only changes a file in git: no cluster key", 22, GREY_B).next_to(git, DOWN, buff=0.22)
        self.beat("And notice who no longer needs a key to the cluster: your build pipeline. It changes a file in git, and that is all it does.",
                  FadeIn(ci_n, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(name, timing, ci_n)), run_time=0.5)

        # statuses
        s_sync = lchip("Synced", GREEN_M, 24).move_to([0.15, -0.95, 0])
        s_hl = lchip("Healthy", GREEN_M, 24).move_to([0.15, -1.75, 0])
        s_l1 = T("matches git?", 22, GREY_B).next_to(s_sync, LEFT, buff=0.2)
        s_l2 = T("does it work?", 22, GREY_B).next_to(s_hl, LEFT, buff=0.2)
        VGroup(s_sync, s_hl, s_l1, s_l2).shift(RIGHT * 0.55)
        self.beat("The manager writes down two separate things. Sync status: does the room match the board?",
                  FadeIn(s_l1), FadeIn(s_sync, shift=UP * 0.1), run_time=1.2)
        self.beat("And health: are the guests happy? Does the app actually work?", FadeIn(s_l2), FadeIn(s_hl, shift=UP * 0.1), run_time=1.2)

        # ---------------- 4. predict: a hand edit with the default settings
        edit = lchip("kubectl patch: GREETING", RED_M, 22, mono=True).move_to([4.35, 2.95, 0])
        hand = T("Edited by hand", 26, RED_M).move_to(l_val, aligned_edge=LEFT)
        self.beat("Now play the colleague who fixes things by hand. Change the greeting in the live cluster, and skip git.",
                  FadeIn(edit, shift=DOWN * 0.2), ReplacementTransform(l_val, hand), Circumscribe(live, color=RED_M, buff=0.05), run_time=2.2)
        l_val = hand
        self.beat("Argo CD runs with its default settings. What happens to that hand edit?", Indicate(argo_t, color=GOLD_M), run_time=1.2)
        self.guess([0.4, 2.95, 0])
        out = lchip("OutOfSync", GOLD_M, 24).move_to(s_sync)
        self.beat("The edit stays. Argo CD sees it within seconds, and marks the app OutOfSync.",
                  ReplacementTransform(s_sync, out), run_time=1.2)
        s_sync = out
        self.beat("But it is still Healthy, because the app runs fine. Two questions, two answers.", Indicate(s_hl[1], color=GREEN_M), run_time=1.2)
        self.beat("Out of the box, Argo CD is a manager who only takes notes. Very polite. Not much help at nine on a Friday.",
                  Wiggle(mgr, scale_value=1.15), run_time=1.6)
        self.beat("So the point is: seeing a difference is only half the job. What to do about it is a setting you choose.", run_time=None)

        # ---------------- 5. the switches: automated sync, self-heal, prune
        sw = VGroup(M("automated sync", 22), M("selfHeal: true", 22), M("prune: true", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        sw_box = frame(sw.width + 0.6, sw.height + 0.5, GOLD_M, [0, 0, 0], fill=0.10, sw=2.5)
        swg = VGroup(sw_box, sw.move_to(sw_box)).move_to([-0.1, -2.85, 0]).shift(LEFT * 1.5)
        sw_n = VGroup(T("apply new commits by itself", 22, GREY_B), T("undo hand edits", 22, GREY_B), T("delete what left git", 22, GREY_B))
        for n, l in zip(sw_n, sw):
            n.next_to(l, RIGHT, buff=0.0).set_x(swg.get_right()[0] + 0.3 + n.width / 2)
        self.play(FadeOut(edit), VGroup(s_sync, s_hl, s_l1, s_l2).animate.shift(UP * 0.3), run_time=0.4)
        self.beat("Three switches decide how strict the manager is. Automated sync applies new commits by itself.",
                  Create(sw_box), FadeIn(sw[0]), FadeIn(sw_n[0]), run_time=1.6)
        self.beat("Self-heal undoes changes made in the cluster but not in git.", FadeIn(sw[1]), FadeIn(sw_n[1]), run_time=1.2)
        self.beat("And prune deletes things from the cluster after you delete them from git.", FadeIn(sw[2]), FadeIn(sw_n[2]), run_time=1.2)
        self.beat("Self-heal and prune are both off by default. A careful choice, for a tool that can delete things.",
                  Indicate(sw[1], color=GOLD_M), Indicate(sw[2], color=GOLD_M), run_time=1.6)
        back = T(OLD, 26).move_to(l_val, aligned_edge=LEFT)
        syn = lchip("Synced", GREEN_M, 24).move_to(s_sync)
        self.beat("Turn self-heal on, and watch the hand edit. After a short pause, Argo CD puts git's text back.",
                  sw[1].animate.set_color(GOLD_M), Succession(Wait(0.8), travel(cmp_, GOLD_M, 0.8), AnimationGroup(ReplacementTransform(l_val, back), ReplacementTransform(s_sync, syn))), run_time=3.0)
        l_val, s_sync = back, syn
        self.beat("You did nothing. To change the greeting for good, you change the board: edit the file, commit, and push.",
                  Indicate(g_val, color=TEAL_M), run_time=1.6)

        # ---------------- 6. break it: two controllers, one field
        self.play(FadeOut(VGroup(live, l_key, l_val)), FadeOut(swg), FadeOut(sw_n), pods.animate.move_to([4.35, 1.0, 0]), pods_l.animate.move_to([4.35, 0.35, 0]), run_time=0.7)
        hpa = frame(2.3, 0.9, BLUE_M, [4.35, -1.25, 0], fill=0.16)
        hpa_t = T("autoscaler", 26).move_to(hpa).set_z_index(2)
        self.beat("So far so good. Now let's be unkind to it. On Day 43 you added an autoscaler, a controller that adds copies when the app is busy.",
                  GrowFromCenter(hpa), Write(hpa_t), run_time=2.0)
        five = VGroup(*[pod() for _ in range(5)]).arrange(RIGHT, buff=0.18).move_to([4.35, 1.0, 0])
        three = VGroup(*[pod() for _ in range(3)]).arrange(RIGHT, buff=0.35).move_to([4.35, 1.0, 0])
        up_a = Arrow(hpa.get_top(), pods_l.get_bottom(), buff=0.08, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.3)
        self.beat("A rush comes in. The autoscaler sets five copies, where git says three.",
                  GrowArrow(up_a), Transform(pods, five), Transform(pods_l, T("5 copies", 22, BLUE_M).move_to(pods_l)), Indicate(g_rep, color=TEAL_M), run_time=2.0)
        self.beat("Self-heal sees a difference from git, and sets it back to three.",
                  travel(cmp_, GOLD_M, 0.6), Transform(pods, three.copy()), Transform(pods_l, T("3 copies", 22, GOLD_M).move_to(pods_l)), run_time=1.6)
        self.beat("The autoscaler raises it again. Back to three. Up to five.",
                  Succession(Transform(pods, five.copy(), run_time=0.7), Transform(pods, three.copy(), run_time=0.7), Transform(pods, five.copy(), run_time=0.7)), run_time=2.4)
        self.beat("They fight for as long as the rush lasts. It is the manager sending home the extra waiters the head waiter just called in.",
                  Succession(Transform(pods, three.copy(), run_time=0.6), Transform(pods, five.copy(), run_time=0.6)), Wiggle(mgr), run_time=2.2)
        fix = lchip("ignoreDifferences: /spec/replicas", TEAL_M, 22, mono=True).move_to([-3.2, -2.95, 0])
        self.beat("The fix is to give that field one owner. The lab tells Argo CD to ignore the replica count, with ignoreDifferences.",
                  FadeIn(fix, shift=UP * 0.1), g_rep.animate.set_opacity(0.35), run_time=1.8)
        self.beat("The other way out is to leave replicas out of git, so there is nothing to compare.", Indicate(g_rep, color=GREY_B), run_time=1.4)
        rule = T("Give each field one owner.", 30, YELLOW_M).to_edge(UP, buff=0.55)
        self.beat("Two controllers fighting over one field never stop. Give each field one owner.", Write(rule), run_time=1.6)
        self.wait(0.4)
        self.play(FadeOut(VGroup(hpa, hpa_t, up_a, fix, rule)), pods_l.animate.become(T("3 copies of hello-devops", 22, GREY_B).move_to(pods_l)),
                  g_rep.animate.set_opacity(1), run_time=0.6)

        # ---------------- 7. break it again: rollback the wrong way, then git revert
        log_t = T("history", 22, TEAL_M).move_to(GC + DOWN * 1.05).align_to(g_file, LEFT)
        c1 = T("Deploy hello-devops", 22).next_to(log_t, DOWN, buff=0.18).align_to(g_file, LEFT)
        self.play(FadeIn(log_t), FadeIn(c1), run_time=0.5)
        c2 = T("typo in the image tag", 22, RED_M).next_to(c1, DOWN, buff=0.12).align_to(g_file, LEFT)
        bad = VGroup(*[pod(RED_M) for _ in range(3)]).arrange(RIGHT, buff=0.35).move_to(pods)
        nh = lchip("not Healthy", RED_M, 24).move_to(s_hl)
        self.beat("Sooner or later, a bad change gets into git itself. Say someone pushes a typo in the image tag.",
                  FadeIn(c2, shift=UP * 0.1), run_time=1.4)
        self.beat("Argo CD applies it, so the app is Synced. But the new copies cannot pull an image that does not exist. Not Healthy.",
                  travel(pull, TEAL_M, 0.7), Transform(pods, bad), ReplacementTransform(s_hl, nh), run_time=2.6)
        s_hl = nh
        undo = lchip("kubectl rollout undo", GOLD_M, 22, mono=True).move_to([4.35, 2.95, 0])
        self.beat("You might be thinking: there is a one command undo, from Day 40. kubectl rollout undo. It fixes the cluster.",
                  FadeIn(undo, shift=DOWN * 0.2), Transform(pods, three.copy()), run_time=2.2)
        self.beat("With self-heal on, what happens next?", run_time=None)
        self.guess([0.4, 2.95, 0])
        self.beat("Argo CD compares the room with the board. The board still says the typo. So it puts the bad version straight back.",
                  Succession(travel(pull, TEAL_M, 0.6), travel(cmp_, GOLD_M, 0.6), Transform(pods, bad.copy())), run_time=3.0)
        self.beat("Well, that is not the help we wanted. Our manager is loyal to the board, even when the board is wrong.",
                  Wiggle(mgr), run_time=1.4)
        self.play(FadeOut(undo), run_time=0.4)
        rev = lchip("git revert <sha>", TEAL_M, 22, mono=True).move_to([-4.45, 2.95, 0])
        c3 = T("Revert the typo", 22, GREEN_M).next_to(c2, DOWN, buff=0.12).align_to(g_file, LEFT)
        self.beat("So a rollback is a commit. git revert makes a new commit that undoes the bad one. The history stays intact.",
                  FadeIn(rev, shift=DOWN * 0.2), FadeIn(c3, shift=UP * 0.1), run_time=2.0)
        hl = lchip("Healthy", GREEN_M, 24).move_to(s_hl)
        self.beat("Push it. Argo CD reads the board, and deploys the state from before.",
                  Succession(travel(pull, TEAL_M, 0.7), travel(cmp_, GOLD_M, 0.7), AnimationGroup(Transform(pods, three.copy()), ReplacementTransform(s_hl, hl))), run_time=2.4)
        s_hl = hl
        self.wait(0.3)
        main = VGroup(git, git_t, git_a, g_file, g_key, g_val, g_rep, log_t, c1, c2, c3, clu, clu_t, clu_a, pods, pods_l, argo, argo_t, mgr,
                      pull, pull_l, cmp_, cmp_l, s_sync, s_hl, s_l1, s_l2, rev)
        self.play(FadeOut(main), run_time=0.7)

        # ---------------- 8. guardrail: the emergency order, and the price
        steps = VGroup(T("1. turn off automated sync for that one app", 28), T("2. fix the cluster by hand, and write down every change", 28),
                       T("3. put the same fix into git", 28, YELLOW_M), T("4. turn automated sync back on", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        st_t = T("In a real emergency", 32, GOLD_M).next_to(steps, UP, buff=0.5)
        VGroup(st_t, steps).move_to(UP * 0.3)
        self.beat("One honest limit. In a real emergency, you may have to touch the cluster by hand. Then follow this order.",
                  Write(st_t), run_time=1.4)
        self.beat("Turn off automated sync for that one app. Fix the cluster by hand, and write down every change.",
                  FadeIn(steps[0], shift=RIGHT * 0.1), FadeIn(steps[1], shift=RIGHT * 0.1), run_time=1.6)
        self.beat("Put the same fix into git. Then turn automated sync back on.",
                  FadeIn(steps[2], shift=RIGHT * 0.1), FadeIn(steps[3], shift=RIGHT * 0.1), run_time=1.4)
        self.beat("Skip step three, and the next sync quietly undoes your fix.", Indicate(steps[2], color=YELLOW_M), run_time=1.2)
        price = T("the price: one more system to learn and upgrade, seven extra Pods on your laptop", 24, GREY_B).to_edge(DOWN, buff=0.7)
        fit(price, 12.6)
        self.beat("And the pull model has a price: one more system to learn and keep upgraded. On your laptop, seven extra Pods. For a cluster more than one person touches, I think it is worth it.",
                  FadeIn(price, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(st_t, steps, price)), run_time=0.6)

        # ---------------- 9. moral, recap and a check question
        moral = T("A change that is not in git did not happen.", 38, YELLOW_M).move_to(UP * 2.3)
        self.beat("So the moral of the story. A change that is not in git did not happen.", Write(moral), run_time=1.8)
        rec = VGroup(T("git is the board; Argo CD is the manager in the room", 28, TEAL_M),
                     T("default: it only takes notes; self-heal undoes hand edits", 28, GOLD_M),
                     T("one owner per field, or two controllers fight", 28, BLUE_M),
                     T("a rollback is a commit: git revert", 28, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("Git is the board, and Argo CD is the manager in the room. By default it only takes notes. Self-heal undoes hand edits. Give each field one owner. And a rollback is a commit.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.6), run_time=6.0)
        self.play(FadeOut(rec), run_time=0.5)
        chk = T("Quick check: you delete a file from git, and prune is off.", 30).move_to(UP * 0.4)
        chk2 = T("What happens to that object in the cluster?", 30).next_to(chk, DOWN, buff=0.3)
        self.beat("A quick check before you go. You delete a file from git, and prune is off. What happens to that object in the cluster?",
                  FadeIn(chk), FadeIn(chk2), run_time=1.8)
        self.guess([0, -1.2, 0])
        ans = T("It stays. Argo CD only marks it for pruning.", 30, GREEN_M).next_to(chk2, DOWN, buff=0.6)
        self.beat("It stays. Argo CD only marks it for pruning, and waits for you.", FadeIn(ans, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
