import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bDaemonSet\b", "daemon set"), (r"\bhostPath\b", "host path"), (r"\bmerge_log\b", "merge log"),
            (r"\bkeep_log\b", "keep log"), (r"\buse_kubelet\b", "use kubelet"), (r"/var/log\b", "slash var slash log"),
            (r"\bFluent Bit\b", "fluent bit"), (r"\bcri\b", "C R I"), (r"\btail -f\b", "tail dash F")])


def tint(c, k=0.15):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def bx(lines, color, pos, w=2.8, h=0.95):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color), 1)
    g = VGroup(*lines).arrange(DOWN, buff=0.1)
    return VGroup(r, g.move_to(r)).move_to(pos)


def ar(a, b, color=GREY_B):
    return Arrow(a, b, buff=0.1, stroke_width=3, color=color, max_tip_length_to_length_ratio=0.15)


BOT = -2.85   # the strip under the node, for lines and records


class D56EfkNode(VoiceScene):
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
        self.title_card("One log line, from Pod to Elasticsearch", "a Fluent Bit on every node, and what it adds")

        # ---------- 1. the node, the app, the runtime
        node = RoundedRectangle(corner_radius=0.2, width=7.7, height=4.25, stroke_color=GREY_B, stroke_width=2).move_to([-2.85, 0.6, 0])
        nl = M("node: devops-worker", 20, GREY_B).next_to(node, UP, buff=0.1).align_to(node, LEFT)
        app = bx([M("hello-devops", 22), T("container web", 20, GREY_B)], TEAL_M, [-5.15, 1.75, 0])
        rt = bx([M("containerd", 22), T("the runtime", 20, GREY_B)], GREY_B, [-5.15, -0.6, 0])
        self.beat("On Day 55, Docker handed each log line straight to Fluent Bit. Kubernetes works differently. Here is one node, with hello-devops running on it.",
                  Create(node), FadeIn(nl), FadeIn(app, shift=0.1 * DOWN), run_time=2.2)
        a1 = ar(app.get_bottom(), rt.get_top())
        a1l = M("stdout", 20, GREY_B).next_to(a1, LEFT, buff=0.12)
        self.beat("The app just prints to stdout. The container runtime on the node catches every line.",
                  FadeIn(rt), GrowArrow(a1), FadeIn(a1l), run_time=1.6)
        fold = bx([M("/var/log/containers", 20, BLUE_M), M("one file per container", 20, GREY_B)], BLUE_M, [-1.25, 1.75, 0], w=3.4)
        a2 = ar(rt.get_right(), fold.get_left() + DOWN * 0.15)
        fname = VGroup(M("hello-devops-7c9f8b6d5-x2x4k", 20, TEAL_M), M("_", 20, GREY_B), M("hello", 20, YELLOW_M), M("_", 20, GREY_B),
                       M("web", 20, GOLD_M), M("-<container id>.log", 20, GREY_B)).arrange(RIGHT, buff=0.04).move_to([-0.6, BOT + 0.3, 0])
        fparts = VGroup(T("pod", 20, TEAL_M).next_to(fname[0], DOWN, buff=0.15), T("namespace", 20, YELLOW_M).next_to(fname[2], DOWN, buff=0.15),
                        T("container", 20, GOLD_M).next_to(fname[4], DOWN, buff=0.15).shift(RIGHT * 0.25))
        self.steps("It writes each container's output to a file. The kubelet links those files into one folder, and the file name says who wrote it: the pod, the namespace, and the container.",
                   (1.2, GrowArrow(a2), FadeIn(fold)), (2.2, Wait(2.2)), (1.0, FadeIn(fname)),
                   (1.6, LaggedStart(*[FadeIn(p, shift=0.1 * UP) for p in fparts], lag_ratio=0.5)))

        # the wrapped line
        self.play(FadeOut(VGroup(fname, fparts)), run_time=0.4)
        wl = VGroup(M("2026-10-30T10:15:02.123456789Z", 20, GREY_B), M("stdout", 20, BLUE_M), M("F", 20, RED_M),
                    M('{"level":"INFO","path":"/","status":200}', 20, WHITE)).arrange(RIGHT, buff=0.2).move_to([0, BOT + 0.3, 0])
        wlab = VGroup(*[T(t, 20, c).next_to(m, DOWN, buff=0.15) for t, c, m in
                        (("timestamp", GREY_B, wl[0]), ("stream", BLUE_M, wl[1]), ("flag", RED_M, wl[2]), ("the app's message", WHITE, wl[3]))])
        self.steps("Each line in that file is wrapped by the runtime. A timestamp, the stream, a flag, and then the app's own message.",
                   (1.0, FadeIn(wl[3])), (1.4, FadeIn(wl[0]), FadeIn(wl[1]), FadeIn(wl[2])),
                   (2.0, LaggedStart(*[FadeIn(x) for x in wlab], lag_ratio=0.4)))
        self.beat("The flag is F for a full line, or P for a partial one, when the runtime splits a very long line.",
                  Indicate(wl[2], color=RED_M, scale_factor=1.6), run_time=1.6)

        # ---------- 2. the shipper: a DaemonSet
        self.play(FadeOut(VGroup(wl, wlab)), run_time=0.4)
        fb = bx([T("Fluent Bit", 24, GOLD_M), T("one per node", 20, GREY_B)], GOLD_M, [-1.25, -0.6, 0], w=3.4)
        a3 = ar(fold.get_bottom(), fb.get_top(), GOLD_M)
        a3l = T("hostPath", 20, GOLD_M).next_to(a3, RIGHT, buff=0.12)
        self.beat("So the job is: read every file in that folder, on every node. A DaemonSet does exactly that. It runs one copy of a pod on each node.",
                  FadeIn(fb, shift=0.1 * UP), run_time=1.6)
        self.beat("A hostPath volume shows the node's own /var/log folder inside the Fluent Bit container. So it can read the files.",
                  GrowArrow(a3), FadeIn(a3l), run_time=1.4)

        nodes = VGroup()
        for i in range(4):
            n = RoundedRectangle(corner_radius=0.1, width=1.6, height=0.9, stroke_color=GREY_B, stroke_width=2).move_to([-4.6 + 1.95 * i, BOT, 0])
            s = Square(0.3, stroke_color=GOLD_M, stroke_width=2).set_fill(tint(GOLD_M, 0.5), 1).move_to(n.get_center() + RIGHT * 0.45)
            nodes.add(VGroup(n, s))
        nlb = T("one Fluent Bit per node", 22, GOLD_M).move_to([4.2, BOT, 0])
        self.steps("Your kind cluster has three nodes, so three copies. Add a node, and Kubernetes starts another Fluent Bit there, by itself.",
                   (1.2, LaggedStart(*[FadeIn(n) for n in nodes[:3]], lag_ratio=0.3), FadeIn(nlb)), (2.0, Wait(2.0)),
                   (0.6, FadeIn(nodes[3][0])), (0.6, GrowFromCenter(nodes[3][1])))
        self.play(FadeOut(VGroup(nodes, nlb)), run_time=0.4)
        q = T("why not a log sidecar in every app pod?", 24, YELLOW_M).move_to([-3.4, BOT + 0.45, 0])
        many = VGroup(*[VGroup(Circle(radius=0.08, stroke_color=TEAL_M, stroke_width=1.5), Square(0.11, stroke_width=0).set_fill(GOLD_M, 0.9).shift(RIGHT * 0.15))
                        for _ in range(40)]).arrange_in_grid(4, 10, buff=(0.12, 0.08)).move_to([3.5, BOT + 0.1, 0])
        ml = T("40 pods, 40 shippers", 22, GOLD_M).next_to(many, LEFT, buff=0.35).shift(DOWN * 0.45)
        self.steps("Why not a log sidecar in every app pod? It works. But forty app pods would mean forty shippers, each with its own memory and config, instead of one per node.",
                   (1.0, FadeIn(q)), (1.8, LaggedStart(*[FadeIn(m) for m in many], lag_ratio=0.03)), (0.6, FadeIn(ml)))
        self.play(FadeOut(VGroup(q, many, ml)), run_time=0.4)

        # ---------- 3. tail: unwrap and join
        p1 = VGroup(M("... P", 20, RED_M), M('{"level":"INFO","pa', 20)).arrange(RIGHT, buff=0.2)
        p2 = VGroup(M("... F", 20, GREEN_M), M('th":"/","status":200}', 20)).arrange(RIGHT, buff=0.2)
        pp = VGroup(p1, p2).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to([-3.2, BOT + 0.1, 0])
        tl = M("multiline.parser: docker, cri", 20, GOLD_M).move_to([3.7, BOT + 0.55, 0])
        self.steps("The tail input follows each file, the way tail -f does. With the multiline parser set to docker and cri, it unwraps this format, and joins P pieces back together.",
                   (1.0, travel(a3, GOLD_M, 1.0)), (1.0, FadeIn(pp)), (1.4, Wait(1.4)), (0.8, FadeIn(tl)))
        joined = M('{"level":"INFO","path":"/","status":200}', 20).move_to([3.3, BOT - 0.25, 0])
        onel = T("one record", 20, GREEN_M).next_to(joined, DOWN, buff=0.12)
        self.beat("In the lab test, a line split into a P and an F part came out as one record.",
                  ReplacementTransform(VGroup(p1[1].copy(), p2[1].copy()), joined), p1.animate.set_opacity(0.3), p2.animate.set_opacity(0.3),
                  Succession(Wait(1.6), FadeIn(onel)), run_time=2.6)
        bm = T("db: where it stopped", 20, BLUE_M).move_to(fb[1][1])
        fbl = fb[1][1].copy()
        self.beat("A small database stores how far each file was read. So a restarted Fluent Bit continues where it stopped.",
                  FadeOut(pp), Transform(fb[1][1], bm), run_time=1.6)
        self.play(FadeOut(VGroup(tl, onel)), joined.animate.move_to([-3.6, BOT + 0.35, 0]), run_time=0.6)

        # ---------- 4. who wrote this line? the kubernetes filter
        api = bx([T("Kubernetes API", 24, BLUE_M)], BLUE_M, [4.65, 1.85, 0], w=3.4, h=0.8)
        self.beat("But a bare log line does not say which pod wrote it. How would anyone find it later, among thousands?",
                  Indicate(joined, color=YELLOW_M), run_time=1.6)
        f1 = VGroup(M("pod_name: hello-devops-7c9f8b6d5-x2x4k", 20, TEAL_M), M("namespace_name: hello", 20, YELLOW_M),
                    M("container_name: web", 20, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([2.6, BOT + 0.0, 0])
        self.steps("The kubernetes filter adds that. The pod name, the namespace and the container come from the file name, for free.",
                   (1.2, travel(a3, GOLD_M, 1.0)), (1.8, LaggedStart(*[FadeIn(f, shift=0.15 * RIGHT) for f in f1], lag_ratio=0.4)))
        a4 = ar(fb.get_right() + UP * 0.2, api.get_left() + DOWN * 0.15, BLUE_M)
        cache = T("labels cached", 20, BLUE_M).move_to(fbl)
        lab = M("labels: app: hello-devops", 20, BLUE_M).next_to(f1, UP, buff=0.14).align_to(f1, LEFT)
        self.steps("For the labels, it asks the Kubernetes API about the pod, then keeps the answer in a cache, so it does not ask again for every line.",
                   (1.0, GrowArrow(a4)), (1.0, travel(a4, BLUE_M, 1.0)), (0.8, FadeIn(lab, shift=0.1 * DOWN)), (2.0, Wait(2.0)), (0.6, Transform(fb[1][1], cache)))

        # merge_log
        lifted = VGroup(M("level: INFO", 20), M("path: /", 20), M("status: 200", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([-4.9, BOT, 0])
        self.steps("Then merge_log checks whether the message is JSON. If it is, its keys become real fields. And keep_log off drops the original string, so you do not store it twice.",
                   (1.6, ReplacementTransform(joined, lifted)), (2.4, Wait(2.4)), (0.8, Indicate(lifted, color=WHITE)))

        # ship it
        es = bx([T("Elasticsearch", 24, GREEN_M), T("outside the cluster", 20, GREY_B)], GREEN_M, [4.65, -0.6, 0], w=3.4)
        a5 = ar(fb.get_right() + DOWN * 0.1, es.get_left() + DOWN * 0.1, GREEN_M)
        rec = VGroup(lifted, lab, f1)
        self.steps("The finished record goes to Elasticsearch, outside the cluster.",
                   (0.8, FadeIn(es), GrowArrow(a5)), (1.2, travel(a5, GREEN_M, 1.2)))
        kq = M("kubernetes.namespace_name: hello", 20, GREEN_M).next_to(es, DOWN, buff=0.25)
        self.beat("In Kibana, those fields become the filters you use every day. Show me only namespace hello.",
                  FadeIn(kq, shift=0.1 * UP), Indicate(f1[1], color=YELLOW_M), run_time=2.0)
        big = T("1000 nodes asking the API adds real load: use_kubelet asks the local kubelet", 22, GREY_B).move_to([0, 3.35, 0])
        fit(big, 13.0)
        self.beat("One warning about scale. A thousand nodes asking the API server about pods adds real load. The filter's use_kubelet option asks the local kubelet instead.",
                  FadeIn(big, shift=0.1 * DOWN), Indicate(a4, color=BLUE_M), run_time=2.4)

        # ---------- 5. recap
        self.play(FadeOut(VGroup(big, kq, rec)), Transform(fb[1][1], fbl), run_time=0.5)
        rc = T("each node: tail the files, add who wrote them, ship to Elasticsearch", 26).move_to([0, BOT, 0])
        fit(rc, 13.0)
        self.beat("Every node runs its own Fluent Bit. It tails the node's container log files, adds labels from the Kubernetes API, and ships to Elasticsearch outside the cluster.",
                  FadeIn(rc, shift=0.1 * UP), travel(a3, GOLD_M, 1.2), run_time=3.0)
        self.play(travel(a5, GREEN_M, 1.0), run_time=1.0)
        self.wait(1.2)
