import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import fg as _fg


def box(*a, **k):  # keep the label drawn above its own filled outline, even when the outline is animated
    b = _fg.box(*a, **k); b[1].set_z_index(1); return b


def chip(*a, **k):
    c = _fg.chip(*a, **k); c[1].set_z_index(1); return c

SAY.extend([(r"\bDaemonSet\b", "daemon set"), (r"\bhostPath\b", "host path"), (r"\bmerge_log\b", "merge log"),
            (r"\bkeep_log\b", "keep log"), (r"\buse_kubelet\b", "use kubelet"), (r"/var/log/containers\b", "slash var slash log slash containers"),
            (r"\bFluent Bit\b", "fluent bit"), (r"\belasticsearch-master\b", "elasticsearch master"),
            (r"\bsuppress_type_name\b", "suppress type name"), (r"\b_type\b", "underscore type"), (r"\bKibana\b", "kibbana"),
            (r"\b3 a\.m\.", "three A M")])

POD_C = TEAL_M      # pods / beds
NODE_C = GREY_B     # nodes / floors
CLERK_C = GOLD_M    # Fluent Bit / the clerk
ES_C = GREEN_M      # Elasticsearch / chart room
API_C = BLUE_M      # Kubernetes API / front desk
ASK_C = YELLOW_M    # questions
FILE_C = PURPLE_M   # the log folder and file name


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def clerk(s=1.0):
    head = Circle(radius=0.12, stroke_color=CLERK_C, stroke_width=3).set_fill(tint(CLERK_C, 0.35), 1)
    body = Arc(radius=0.22, start_angle=0, angle=PI, stroke_color=CLERK_C, stroke_width=3).next_to(head, DOWN, buff=0.04)
    return VGroup(head, body).scale(s)


def pod():
    return Circle(radius=0.24, stroke_color=POD_C, stroke_width=3).set_fill(tint(POD_C, 0.25), 1)


def floor(i, y):
    r = RoundedRectangle(corner_radius=0.12, width=8.6, height=1.15, stroke_color=NODE_C, stroke_width=2).move_to([-2.0, y, 0])
    lab = T(f"node {i}", 24, NODE_C).move_to([-5.75, y, 0])
    pods = VGroup(*[pod().move_to([-4.65 + 0.75 * k, y, 0]) for k in range(4)])
    fold = chip("/var/log/containers", FILE_C, 22, mono=True).move_to([-0.15, y, 0])
    ck = clerk().move_to([1.85, y - 0.02, 0])
    return dict(r=r, lab=lab, pods=pods, fold=fold, ck=ck)


class D56Clerks(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("Who wrote this line?", "one log collector per node, and a stamp on every line")

        # ---------- 1. the question
        nt = RoundedRectangle(corner_radius=0.1, width=6.4, height=1.1, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.07), 1).move_to(UP * 1.2)
        ntx = T("fever at 3 a.m., gave medicine", 30).move_to(nt)
        self.beat("A doctor in our hospital pulls a note from the central chart room. Fever at 3 a.m., gave medicine.",
                  FadeIn(nt), Write(ntx), run_time=2.4)
        q1 = T("Which patient? Which ward?", 30, ASK_C).move_to(DOWN * 0.4)
        self.beat("Which patient? Which ward? The note doesn't say. The nurse was standing right at the bed, so it seemed obvious.",
                  FadeIn(q1, shift=UP * 0.15), run_time=2.0)
        ln = M('{"level":"INFO","path":"/","status":200}', 26).move_to(nt)
        q2 = T("Which pod? Which machine?", 30, ASK_C).move_to(q1)
        self.beat("Our log lines have the same blind spot. Here is a line from our lab app, hello-devops. Which copy of the app wrote it? On which machine?",
                  FadeOut(ntx), FadeOut(nt), Succession(Wait(1.2), FadeIn(ln)), Transform(q1, q2), run_time=3.2)
        self.beat("Two questions, really. Who even collects the lines, when the app runs on many machines? And how does each line learn who wrote it? Let's take them one at a time.",
                  run_time=None)
        self.play(FadeOut(VGroup(ln, q1)), run_time=0.6)

        # ---------- 2. familiar: one laptop
        lap = box("hello-devops", POD_C, w=2.8).move_to([-4.2, 0.6, 0])
        fbx = box("Fluent Bit", CLERK_C, w=2.4).move_to([0, 0.6, 0])
        esx = box("Elasticsearch", ES_C, w=2.8).move_to([4.2, 0.6, 0])
        a1, a2 = edge_arrow(lap, fbx), edge_arrow(fbx, esx)
        cap = T("last time: one laptop", 28, GREY_B).move_to(UP * 2.4)
        self.beat("Last time, everything lived on one laptop. Docker handed every line straight to Fluent Bit, a small program that collects logs and sends them on to Elasticsearch.",
                  FadeIn(cap), FadeIn(lap), Succession(Wait(1.5), AnimationGroup(GrowArrow(a1), FadeIn(fbx))), Succession(Wait(3.0), AnimationGroup(GrowArrow(a2), FadeIn(esx))), run_time=5.0)
        self.play(travel(a1, POD_C, 0.7), run_time=0.7)
        self.play(travel(a2, CLERK_C, 0.7), run_time=0.7)
        self.beat("One machine, one collector. Easy.", run_time=None)
        self.play(FadeOut(VGroup(lap, fbx, esx, a1, a2, cap)), run_time=0.6)

        # ---------- 3. the building
        ys = [2.3, 0.95, -0.4]
        F = [floor(i + 1, y) for i, y in enumerate(ys)]
        es = VGroup(RoundedRectangle(corner_radius=0.15, width=2.9, height=1.5, stroke_color=ES_C, stroke_width=3).set_fill(tint(ES_C), 1))
        es.add(VGroup(T("Elasticsearch", 26, ES_C), T("the chart room", 22, GREY_B)).arrange(DOWN, buff=0.12).move_to(es[0]))
        es.move_to([4.85, 0.95, 0])
        self.beat("Now hello-devops runs on Kubernetes, the system that spreads containers over many machines. Picture the cluster as the hospital building. Each machine, called a node, is one floor.",
                  LaggedStart(*[AnimationGroup(Create(f["r"]), FadeIn(f["lab"])) for f in F], lag_ratio=0.3), Succession(Wait(3.5), FadeIn(es)), run_time=5.4)
        self.beat("Each pod, a running copy of an app, is a bed on that floor. Three nodes, twelve pods.",
                  LaggedStart(*[GrowFromCenter(p) for f in F for p in f["pods"]], lag_ratio=0.06), run_time=2.6)
        lines_anim = []
        for f in F:
            for p in f["pods"]:
                ln = Line(p.get_right(), f["fold"].get_left(), stroke_width=0)
                lines_anim.append(travel(ln, POD_C, 0.8))
        self.beat("On every node, each container's output is written to a file, and all those files sit in one folder, slash var slash log slash containers.",
                  LaggedStart(*[FadeIn(f["fold"]) for f in F], lag_ratio=0.2), Succession(Wait(2.4), LaggedStart(*lines_anim, lag_ratio=0.05)), run_time=5.0)
        fname = M("hello-devops-7c9f8b6d5-x2x4k_hello_web-<container id>.log", 22).move_to([-1.0, -1.65, 0])
        fparts = [(0, 28, "pod", POD_C), (29, 34, "namespace", ASK_C), (35, 38, "container", CLERK_C)]
        fl = VGroup()
        for a, b, t, c in fparts:
            VGroup(*fname[a:b]).set_color(c)
            fl.add(T(t, 22, c).next_to(VGroup(*fname[a:b]), DOWN, buff=0.15 if t != "container" else 0.5))
        self.beat("Look at one file's name. It says who wrote it: the pod, the namespace, and the container. A namespace is a named area of the cluster. Keep this name in mind; it comes back.",
                  FadeIn(fname, shift=UP * 0.1), Succession(Wait(1.8), LaggedStart(*[FadeIn(x) for x in fl], lag_ratio=0.5)), run_time=4.6)
        self.play(FadeOut(VGroup(fname, fl)), run_time=0.5)

        # ---------- 4. steelman the wrong collectors
        ask = VGroup(T("Who reads", 28, ASK_C), T("these folders?", 28, ASK_C)).arrange(DOWN, buff=0.12).move_to([4.85, 2.6, 0])
        self.beat("So who reads these folders? The first idea most of us have: give every bed its own clerk.",
                  FadeIn(ask), run_time=1.6)
        side = VGroup(*[Square(0.2, stroke_width=0).set_fill(CLERK_C, 0.95).move_to(p.get_center() + UR * 0.24) for f in F for p in f["pods"]])
        cnt = T("12 pods, 12 shippers", 26, CLERK_C).move_to([-1.9, -1.65, 0])
        self.beat("A little shipper inside every pod. It works. Twelve pods, twelve shippers.",
                  LaggedStart(*[GrowFromCenter(s) for s in side], lag_ratio=0.05), FadeIn(cnt), run_time=2.6)
        cnt2 = T("40 pods, 40 shippers, 40 settings files", 26, CLERK_C).move_to(cnt)
        self.beat("But grow to forty pods, and you have forty shippers, each with its own memory and its own settings to keep up to date. The hospital now employs more clerks than nurses.",
                  Transform(cnt, cnt2), run_time=1.6)
        self.play(FadeOut(side), FadeOut(cnt), run_time=0.5)
        one = clerk().move_to(F[0]["ck"])
        win = SurroundingRectangle(F[0]["fold"], buff=0.08, color=CLERK_C, stroke_width=2.5)
        self.beat("Fine, the opposite then. One clerk for the whole building. But a clerk can only see the folder on its own floor. Its window, called a hostPath volume, shows that node's own folder, and nothing else.",
                  FadeIn(one, shift=DOWN * 0.2), Succession(Wait(3.0), Create(win)), run_time=5.0)
        reds = VGroup(*[SurroundingRectangle(F[k]["fold"], buff=0.08, color=RED_M, stroke_width=2.5) for k in (1, 2)])
        self.beat("Floors two and three pile up, unread.",
                  Create(reds), run_time=1.6)
        wish = VGroup(T("one clerk per floor,", 28, ASK_C), T("hired by itself", 28, ASK_C)).arrange(DOWN, buff=0.12).move_to(ask)
        self.beat("What we really want is exactly one clerk on every floor. And when a new floor opens, a new clerk should appear, without anyone remembering to hire one.",
                  FadeOut(reds), FadeOut(win), Transform(ask, wish),
                  LaggedStart(*[FadeIn(F[k]["ck"], shift=DOWN * 0.2) for k in (1, 2)], lag_ratio=0.4), run_time=4.0)
        self.remove(one); self.add(F[0]["ck"])

        # ---------- 5. name it, predict
        ds = T("DaemonSet: one copy of a pod on every node", 28, CLERK_C).move_to([-1.9, -1.65, 0])
        self.beat("Kubernetes has exactly that rule. It is called a DaemonSet: run one copy of a pod on every node. The clerk here is Fluent Bit.",
                  FadeIn(ds, shift=UP * 0.1), Indicate(VGroup(*[f["ck"] for f in F]), color=CLERK_C), run_time=3.0)
        pq = VGroup(T("3 nodes, 12 pods.", 28), T("How many", 28, ASK_C), T("Fluent Bit pods?", 28, ASK_C)).arrange(DOWN, buff=0.14).move_to([4.85, -1.55, 0])
        self.beat("So, a quick prediction. Three nodes, twelve pods. How many Fluent Bit pods run? Pause and guess.",
                  FadeOut(ask), FadeIn(pq), run_time=2.0)
        self.pause([4.85, -2.75, 0])
        three = T("3", 44, CLERK_C).move_to([4.85, -2.7, 0])
        self.beat("Three. One per node, not one per pod. Each one reads the files of every pod on its floor.",
                  FadeIn(three, scale=1.4), LaggedStart(*[Indicate(f["ck"], color=CLERK_C, scale_factor=1.4) for f in F], lag_ratio=0.3), run_time=3.0)
        tol = T("a toleration lets it onto the control-plane node", 24, GREY_B).move_to([-1.9, -2.4, 0])
        self.beat("One small print. One of these nodes is the control-plane node, the one that runs Kubernetes itself. The lab's values include a toleration, a setting that lets Fluent Bit onto it. Without it, you would get two.",
                  FadeIn(tol), Indicate(F[0]["lab"], color=NODE_C), run_time=3.0)
        self.play(FadeOut(VGroup(pq, three, tol, ds)), run_time=0.5)

        # ---------- 6. break: install with defaults
        helm = T("helm install, default settings", 26, CLERK_C).move_to([-1.9, -1.65, 0])
        self.beat("We install it with Helm, the package installer for Kubernetes. The naive first try is the chart's default settings. Then we wait.",
                  FadeIn(helm), run_time=1.8)
        ghost = DashedVMobject(RoundedRectangle(corner_radius=0.15, width=2.9, height=0.9, stroke_color=RED_M, stroke_width=2.5), num_dashes=30).move_to([4.85, -1.2, 0])
        gl = M("elasticsearch-master", 22, RED_M).move_to(ghost)
        sends = [Arrow(f["ck"].get_right(), ghost.get_left(), buff=0.15, stroke_width=2.5, color=CLERK_C, max_tip_length_to_length_ratio=0.08) for f in F]
        self.beat("And nothing arrives. The default output sends to a host named elasticsearch-master, which only exists if you installed Elastic's old chart.",
                  Create(ghost), FadeIn(gl), LaggedStart(*[GrowArrow(a) for a in sends], lag_ratio=0.2), run_time=3.4)
        logl = M("HTTP 400 ... unknown parameter [_type]", 22, RED_M).move_to([-1.9, -2.45, 0])
        self.beat("Point it at the right place, and there's a second problem. The default doesn't set suppress_type_name, so Elasticsearch 8 and 9 answer with HTTP 400 and unknown parameter, underscore type.",
                  FadeIn(logl, shift=UP * 0.1), run_time=2.0)
        self.beat("With unlimited retries, Fluent Bit keeps trying forever, quietly. A clerk posting letters to a building that was never built, and never complaining.",
                  *[travel(a, CLERK_C, 1.0) for a in sends], run_time=2.0)
        rule = T("Read one shipper's own log before you open Kibana.", 28, ASK_C).move_to([-1.9, -1.65, 0])
        fit(rule, 8.4)
        self.beat("So the point really is: before you open Kibana and stare at an empty page, read one shipper's own log. It tells you why nothing arrived.",
                  Transform(helm, rule), run_time=2.0)
        outs = [Arrow(f["ck"].get_right(), es[0].get_left(), buff=0.15, stroke_width=2.5, color=CLERK_C, max_tip_length_to_length_ratio=0.08) for f in F]
        self.beat("The lab's values file sets the output itself. Now the lines flow.",
                  FadeOut(VGroup(ghost, gl, logl)), *[ReplacementTransform(a, b) for a, b in zip(sends, outs)],
                  Succession(Wait(1.6), AnimationGroup(*[travel(b, CLERK_C, 1.0) for b in outs])), run_time=3.2)
        self.play(FadeOut(helm), run_time=0.4)

        # ---------- 7. stamping: who wrote this line?
        bare = M('{"level":"INFO","path":"/","status":200}', 22).move_to([-1.9, -1.7, 0])
        self.beat("They arrive. But look at one: still a note with no ward and no bed. Back to our first question. Which pod wrote it?",
                  FadeIn(bare, shift=UP * 0.1), run_time=2.0)
        floors = [VGroup(f["r"], f["lab"], f["pods"], f["fold"], f["ck"]) for f in F]
        o1 = Arrow(F[0]["ck"].get_right() + UP * 0.35, [3.4, 2.65, 0], buff=0.15, stroke_width=2.5, color=CLERK_C, max_tip_length_to_length_ratio=0.08)
        self.play(FadeOut(floors[1]), FadeOut(floors[2]), *[FadeOut(o) for o in outs], floors[0].animate.shift(UP * 0.35),
                  es.animate.move_to([4.85, 2.55, 0]), bare.animate.move_to([-2.5, 1.65, 0]), run_time=1.2)
        self.play(GrowArrow(o1), run_time=0.4)
        fname.move_to([-1.0, 0.95, 0])
        for a, b, t, c in fparts:
            VGroup(*fname[a:b]).set_color(c)
        self.beat("Remember the file name? The clerk reads the line from that file, so the pod, the namespace and the container come for free.",
                  FadeIn(fname, shift=UP * 0.1), run_time=1.8)
        rec = VGroup(
            M("pod_name: hello-devops-7c9f8b6d5-x2x4k", 22, POD_C),
            M("namespace_name: hello", 22, ASK_C),
            M("container_name: web", 22, CLERK_C),
            M("labels: app: hello-devops", 22, API_C),
            M("host: devops-worker", 22, NODE_C),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([-3.2, -1.25, 0])
        rec.align_to([-6.3, 0, 0], LEFT)
        self.beat("The kubernetes filter, a step inside Fluent Bit, stamps them onto the record.",
                  *[ReplacementTransform(VGroup(*fname[a:b]).copy(), rec[k]) for k, (a, b, t, c) in enumerate(fparts)], run_time=2.6)
        api = VGroup(RoundedRectangle(corner_radius=0.15, width=3.4, height=1.3, stroke_color=API_C, stroke_width=3).set_fill(tint(API_C), 1))
        api.add(VGroup(T("Kubernetes API", 26, API_C), T("the front desk", 22, GREY_B)).arrange(DOWN, buff=0.12).move_to(api[0]))
        api.move_to([4.3, -1.75, 0])
        self.beat("Labels are different. They are short name and value tags that people attach to a pod, like app: hello-devops. They are not in the file name. So the clerk asks the front desk, the Kubernetes API.",
                  FadeIn(api), run_time=2.4)
        qa = Arrow(api[0].get_left(), rec[3].get_right() + RIGHT * 0.2, buff=0.1, stroke_width=3, color=API_C, max_tip_length_to_length_ratio=0.06)
        memo = T("answer kept in a cache", 24, API_C).move_to([4.3, -2.8, 0])
        self.beat("And it keeps the answer in memory, a cache, so it doesn't run to the desk again for every single line. The node it ran on gets stamped too.",
                  GrowArrow(qa), Succession(Wait(0.8), AnimationGroup(FadeIn(rec[3], shift=LEFT * 0.2), FadeIn(memo))),
                  Succession(Wait(3.4), FadeIn(rec[4])), run_time=4.6)
        lifted = M("level: INFO   path: /   status: 200", 22).move_to(bare)
        self.beat("One more setting, merge_log. If the message is JSON, its keys become real fields. And keep_log off drops the original string, so nothing is stored twice.",
                  FadeOut(fname), Succession(Wait(1.6), ReplacementTransform(bare, lifted)), run_time=3.4)
        kq = VGroup(T("Kibana:", 26, GREY_B), M("kubernetes.namespace_name: hello", 22, ASK_C)).arrange(RIGHT, buff=0.25).move_to([1.0, 0.95, 0])
        self.beat("Now every line says who wrote it. In Kibana, those stamps become filters you'll use every day: only namespace hello, only app hello-devops, or only one node, to see if one floor is the problem.",
                  FadeIn(kq, shift=UP * 0.1), Indicate(rec[1], color=ASK_C), Succession(Wait(3.0), Indicate(rec[3], color=API_C)), Succession(Wait(5.0), Indicate(rec[4], color=NODE_C)), run_time=7.0)

        # ---------- 8. guardrails
        self.play(FadeOut(VGroup(kq, memo, qa)), run_time=0.5)
        g1 = T("1000 nodes asking the front desk is real load: use_kubelet asks each node instead", 24, API_C)
        g2 = VGroup(T("a chatty pod can opt out:", 24, GREY_B), M('fluentbit.io/exclude: "true"', 22, CLERK_C)).arrange(RIGHT, buff=0.25)
        g3 = T("on first start it reads only new lines: send fresh traffic", 24, GREY_B)
        gs = VGroup(g1, g2, g3).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit(gs, 12.6).move_to([0, -0.15, 0]).align_to([-6.3, 0, 0], LEFT)
        self.play(FadeOut(lifted), rec.animate.set_opacity(0.35), run_time=0.4)
        self.play(FadeOut(rec), run_time=0.4)
        self.beat("A few honest limits. The front desk is the part that can hurt. A thousand nodes asking about pods adds real load to the API server. The filter's use_kubelet option asks each node's own kubelet instead. Our three-node practice cluster doesn't need it.",
                  FadeIn(g1, shift=UP * 0.1), Indicate(api[1][0], color=API_C), run_time=3.0)
        self.beat("A chatty pod can opt out. With the exclude setting on, an annotation on the pod drops its lines right at the node.",
                  FadeIn(g2, shift=UP * 0.1), run_time=2.0)
        self.beat("And on first start, Fluent Bit reads new lines only. So send fresh traffic before you go looking for logs.",
                  FadeIn(g3, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(gs, api, o1)), es.animate.move_to([4.85, 0.95, 0]), floors[0].animate.shift(DOWN * 0.35), run_time=1.0)
        self.play(FadeIn(floors[1]), FadeIn(floors[2]), *[GrowArrow(o) for o in outs], run_time=0.8)

        # ---------- 9. moral, check
        mor = T("One clerk per floor. A stamp on every note.", 32, ASK_C).move_to([-1.9, -1.75, 0])
        fit(mor, 8.4)
        self.beat("So the moral of the story. One clerk per floor, reading that floor's own folder, and stamping every note with the bed it came from. One clerk per floor, a stamp on every note.",
                  Write(mor), run_time=3.0)
        cq = VGroup(T("Quick check:", 28, ASK_C), T("a 4th node joins.", 28), T("How many clerks,", 28), T("and who hires one?", 28)).arrange(DOWN, buff=0.15).move_to([4.85, -1.4, 0])
        self.beat("A quick check. A fourth node joins the cluster. How many Fluent Bit pods now, and who starts the new one? Pause and think.",
                  FadeOut(mor), FadeIn(cq), run_time=2.4)
        self.pause([4.85, -2.95, 0], text="pause and think")
        f4 = floor(4, -1.75)
        outs4 = Arrow(f4["ck"].get_right(), es[0].get_left(), buff=0.15, stroke_width=2.5, color=CLERK_C, max_tip_length_to_length_ratio=0.08)
        self.beat("Four. And nobody hires it. The DaemonSet sees a new floor, and Kubernetes starts a clerk there, by itself.",
                  Create(f4["r"]), FadeIn(f4["lab"]), LaggedStart(*[GrowFromCenter(p) for p in f4["pods"]], lag_ratio=0.1), FadeIn(f4["fold"]),
                  Succession(Wait(2.4), AnimationGroup(FadeIn(f4["ck"], shift=DOWN * 0.2), GrowArrow(outs4))), run_time=4.4)
        self.beat("The lesson's other worry, shelves that never empty, gets a rule for old logs to leave. And next time, one request crosses several services. Where did its time go?",
                  travel(outs4, CLERK_C, 1.0), FadeOut(cq), run_time=2.0)
        self.wait(1.0)
