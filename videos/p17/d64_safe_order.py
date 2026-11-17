import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bbase64\b", "base sixty-four"), (r"\bhunter2-example\b", "hunter two example"), (r"\bdb-password\b", "D B password"),
            (r"\bServiceAccount\b", "service account"), (r"\bcan-i\b", "can I"), (r"\$PASSWORD\b", "password")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(rows, color, buff=0.26):
    fr = RoundedRectangle(corner_radius=0.12, width=rows.width + 2 * buff, height=rows.height + 2 * buff, stroke_color=color, stroke_width=2.5)
    fr.set_fill(tint(color, 0.10), 1)
    return VGroup(fr, rows.move_to(fr))


def person(color=BLUE_M, s=1.0):
    head = Circle(radius=0.22, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1).shift(UP * 0.42)
    body = Arc(radius=0.4, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).shift(DOWN * 0.32)
    base = Line(LEFT * 0.4, RIGHT * 0.4, stroke_color=color, stroke_width=3).shift(DOWN * 0.32)
    return VGroup(head, body, base).scale(s)


def safe_shape(color=GOLD_M):
    r = RoundedRectangle(corner_radius=0.1, width=1.3, height=1.2, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.14), 1)
    dial = Circle(radius=0.22, stroke_color=color, stroke_width=3).move_to(r.get_center() + LEFT * 0.15)
    hnd = Line(ORIGIN, RIGHT * 0.25, stroke_color=color, stroke_width=4).move_to(r.get_center() + RIGHT * 0.38)
    return VGroup(r, dial, hnd)


def slip(text, color=WHITE):
    t = T(text, 22, color)
    r = Rectangle(width=t.width + 0.3, height=t.height + 0.25, stroke_color=color, stroke_width=2).set_fill(tint(GREY_B, 0.25), 1)
    return VGroup(r, t.move_to(r))


class D64SafeOrder(VoiceScene):
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
        self.title_card("Who can really read a Secret?", "the safe, the cook, and one order slip")

        # ---------- 1. the shy question
        q1 = T("You keep the database password in a Kubernetes Secret,", 30).move_to([0, 1.1, 0])
        q2 = T("in namespace hello. Who can read it?", 30).move_to([0, 0.5, 0])
        self.beat("Here's a question worth asking before anything leaks. You keep a database password in a Kubernetes Secret, the cluster's place for passwords, in the namespace called hello. Who can read it?",
                  FadeIn(q1, shift=UP * 0.1), Succession(Wait(3.4), FadeIn(q2, shift=UP * 0.1)), run_time=5.0)
        q3 = T("only the people you allowed... right?", 30, YELLOW_M).move_to([0, -0.6, 0])
        self.beat("Kubernetes is the system that runs your containers on a group of machines. A namespace is a named room inside it. And most of us would answer: only the people I allowed. Let's see if that's really true.",
                  FadeIn(q3, shift=UP * 0.1), run_time=3.0)
        self.wait(0.3)
        self.play(FadeOut(VGroup(q1, q2, q3)), run_time=0.5)

        # ---------- 2. the envelope is thin: base64
        env = panel(VGroup(T("Secret db-password", 24, GOLD_M), M("password: aHVudGVyMi1leGFtcGxl", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.15), GOLD_M).move_to([0, 1.4, 0])
        self.beat("First, look inside the envelope. Read the Secret back, and the value comes out like this. Looks scrambled, doesn't it?",
                  FadeIn(env, shift=DOWN * 0.15), run_time=2.4)
        dec = VGroup(M("| base64 -d", 24, GREY_B), M("hunter2-example", 26, RED_M)).arrange(RIGHT, buff=0.5).next_to(env, DOWN, buff=0.6)
        self.beat("It isn't. It's base64, which only writes the same bytes in another alphabet. One more command turns it straight back into the password.",
                  FadeIn(dec[0]), Succession(Wait(2.6), FadeIn(dec[1], shift=LEFT * 0.2)), run_time=4.0)
        ob = T("obscured, but not secret", 30, YELLOW_M).next_to(dec, DOWN, buff=0.55)
        self.beat("The Kubernetes docs call such a value obscured, but not secret. And by default the cluster's database, etcd, stores Secrets unencrypted. A spy novel would be disappointed. So the envelope itself protects nothing.",
                  FadeIn(ob, shift=UP * 0.1), run_time=2.6)
        self.wait(0.3)
        self.play(FadeOut(VGroup(env, dec, ob)), run_time=0.5)

        # ---------- 3. the obvious fix: a lock (RBAC), and it works
        dev = person(BLUE_M).move_to([-5.2, 0.4, 0])
        devl = M("dev", 26, BLUE_M).next_to(dev, DOWN, buff=0.2)
        desk = box("API server", GREY_B, w=2.6, size=28).move_to([-1.6, 0.4, 0])
        deskl = T("the front desk", 24, GREY_B).next_to(desk, DOWN, buff=0.2)
        sf = safe_shape(GOLD_M).move_to([2.6, 2.2, 0])
        sfl = T("Secret", 26, GOLD_M).next_to(sf, RIGHT, buff=0.25)
        self.beat("So the obvious fix is a lock. Every request to Kubernetes goes through one front desk, the API server, and it checks who may do what. That check is called RBAC, role-based access control.",
                  FadeIn(desk), FadeIn(deskl), FadeIn(sf), FadeIn(sfl), run_time=3.0)
        self.beat("Here's a developer identity, dev. It may create Pods, the running copies of an app. It has no rule about Secrets at all.",
                  FadeIn(dev), FadeIn(devl), run_time=2.4)
        rules = panel(VGroup(VGroup(M("can-i get secrets", 22), M("no", 24, RED_M)).arrange(RIGHT, buff=0.5),
                             VGroup(M("can-i create pods", 22), M("yes", 24, GREEN_M)).arrange(RIGHT, buff=0.5)).arrange(DOWN, aligned_edge=RIGHT, buff=0.15), GREY_B).move_to([-3.4, -2.2, 0])
        self.beat("Ask the API server what dev may do. Get secrets? No. Create Pods? Yes.",
                  FadeIn(rules[0]), FadeIn(rules[1][0][0]), FadeIn(rules[1][1][0]),
                  Succession(Wait(1.6), FadeIn(rules[1][0][1])), Succession(Wait(2.8), FadeIn(rules[1][1][1])), run_time=3.6)
        a1 = Arrow(dev.get_right(), desk.get_left(), buff=0.15, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        a2 = Arrow(desk.get_right() + UP * 0.2, sf.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12)
        xx = tick(False, 0.22).move_to(a2.point_from_proportion(0.5))
        err = M('Error from server (Forbidden): secrets "db-password" is forbidden', 22, RED_M).move_to([0.9, -3.2, 0])
        self.steps("So dev asks for the Secret directly, and gets refused. Forbidden. So far so good. The lock works.",
                   (0.8, GrowArrow(a1)), (0.6, travel(a1, BLUE_M, 0.5)), (0.6, GrowArrow(a2)), (0.5, Create(xx)), (0.6, FadeIn(err, shift=UP * 0.1)))
        self.wait(0.3)
        self.play(FadeOut(VGroup(a2, xx, err)), run_time=0.5)

        # ---------- 4. analogy: the order slip to the cook
        cook = person(TEAL_M).move_to([2.6, -0.9, 0])
        cookl = T("the cook", 24, TEAL_M).next_to(cook, RIGHT, buff=0.3)
        self.beat("Now back to the jam shop. A new helper may not open the safe in the office. Fair enough. But the helper may send the cook an order.",
                  FadeIn(cook), FadeIn(cookl), run_time=2.6)
        order = slip("bring me what's in the safe").move_to([-4.3, 2.2, 0])
        self.beat("And the order says: bring me what's in the safe.", FadeIn(order, shift=DOWN * 0.15), run_time=1.6)
        ok = tick(True, 0.2).next_to(desk, UP, buff=0.2)
        self.steps("The front desk checks one thing: may this helper send orders to the kitchen? Yes. The cook, trusting the order, opens the safe and brings it out.",
                   (1.0, order.animate.next_to(desk, UP, buff=0.55)), (0.5, Create(ok)), (1.6, Wait(1.6)),
                   (1.0, order.animate.next_to(cook, LEFT, buff=0.3)), (0.6, cook.animate.move_to(sf.get_center() + DOWN * 1.1)),
                   (0.6, Indicate(sf[0], color=GOLD_M)), (0.6, cook.animate.move_to([2.6, -0.9, 0])))
        self.beat("Nobody ever asked whether the helper was allowed in the safe. Each check was right. The gap is between them.",
                  Wait(0.1), run_time=0.4)
        self.play(FadeOut(VGroup(order, ok)), run_time=0.4)

        # ---------- 5. map, predict, show: the peek Pod
        kub = box("kubelet", TEAL_M, w=2.2, size=28).move_to(cook)
        self.steps("Let's map it. The front desk is the API server. The cook is the kubelet, the helper on each machine that starts Pods. And the order slip is a Pod.",
                   (0.4, Wait(0.4)), (0.8, FadeOut(deskl)), (2.6, Wait(2.6)), (0.9, ReplacementTransform(VGroup(cook, cookl), kub)))
        pod = panel(VGroup(M("Pod peek", 22, BLUE_M), M("env PASSWORD from db-password", 22),
                           M("echo The password is $PASSWORD", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.12), BLUE_M).move_to([-3.6, 2.45, 0])
        self.beat("dev writes a Pod called peek. It loads the Secret into a setting called PASSWORD, and prints it.",
                  FadeIn(pod, shift=DOWN * 0.15), run_time=2.4)
        self.beat("dev can't read Secrets. dev can create Pods. Will this one print the password? Pause and guess.",
                  Indicate(rules[1], color=WHITE, scale_factor=1.03), run_time=2.0)
        self.wait(2.0)
        ok2 = tick(True, 0.2).next_to(desk, UP, buff=0.2)
        created = M("pod/peek created", 22, GREEN_M).next_to(desk, DOWN, buff=0.25)
        a3 = Arrow(desk.get_right() + DOWN * 0.2, kub.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12)
        a4 = Arrow(kub.get_top(), sf.get_bottom(), buff=0.15, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.15)
        self.steps("The API server checks: may dev create Pods here? Yes. pod slash peek, created.",
                   (0.6, travel(a1, BLUE_M, 0.5)), (0.5, Create(ok2)), (0.6, FadeIn(created, shift=UP * 0.1)))
        self.steps("Then the kubelet starts it, and fetches the Secret on the Pod's behalf.",
                   (0.7, GrowArrow(a3)), (0.5, travel(a3, GREY_B, 0.5)), (0.6, GrowArrow(a4)), (0.6, travel(a4, GOLD_M, 0.5)))
        logp = panel(VGroup(M("$ kubectl logs peek", 22, GREY_B), M("The password is hunter2-example", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15), RED_M).move_to([3.0, -2.75, 0])
        self.beat("dev reads the Pod's log. And there it is. The password the rule was meant to protect.",
                  FadeIn(logp, shift=UP * 0.15), run_time=2.0)
        self.beat("Well... the lock was fine. We just ordered the cook to open it.",
                  Indicate(logp[1][1], color=RED_M, scale_factor=1.04), run_time=1.6)
        self.beat("Nobody checks the creator's rights to Secrets. The API server only checked that dev may create the Pod. The same holds for anyone who may create a Deployment, the object that keeps Pods running.",
                  Indicate(ok2, color=GREEN_M, scale_factor=1.4), run_time=2.6)

        # ---------- 6. name it: the namespace is the boundary
        self.play(FadeOut(VGroup(pod, created, ok2, a3, a4, logp)), run_time=0.5)
        room = DashedVMobject(RoundedRectangle(corner_radius=0.3, width=12.6, height=5.6, stroke_color=PURPLE_M, stroke_width=2.5).move_to([0, 0.15, 0]), num_dashes=80)
        rooml = T("namespace hello", 26, PURPLE_M).move_to([4.6, 3.2, 0])
        self.beat("So who can read that Secret? Anyone who may read Secrets, or create Pods, in its namespace. The namespace is the real boundary, and the Secret rule alone protects nothing.",
                  Create(room), FadeIn(rooml), run_time=3.6)
        self.wait(0.3)
        self.play(FadeOut(VGroup(room, rooml, dev, devl, desk, a1, sf, sfl, kub, rules)), run_time=0.6)

        # ---------- 7. guardrails: layers
        gt = T("protect Secrets in layers", 30, YELLOW_M).move_to([0, 2.6, 0])
        L = VGroup(T("1. turn on encryption at rest, so etcd holds only encrypted values", 26),
                   T("2. keep the list of who can create Pods in a namespace short", 26),
                   T("3. keep the real values in a secrets manager", 26),
                   T("4. never put the value in git, not even for one commit", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to([0, 0.3, 0])
        self.beat("So protect Secrets in layers. One: on a real cluster, turn on encryption at rest, so etcd and its backups hold only encrypted values.",
                  FadeIn(gt), FadeIn(L[0], shift=RIGHT * 0.1), run_time=2.6)
        self.beat("Two: keep the list of people and programs who can create Pods in a namespace short. That's who holds the order pad.",
                  FadeIn(L[1], shift=RIGHT * 0.1), run_time=2.2)
        self.beat("Three: keep the real values in a secrets manager, one logged place that stores them, and copy them in only where needed. Four: never put the value in git, not even for one commit.",
                  FadeIn(L[2], shift=RIGHT * 0.1), Succession(Wait(3.4), FadeIn(L[3], shift=RIGHT * 0.1)), run_time=4.6)
        tip = M("kubectl auth can-i --list", 24, TEAL_M).next_to(L, DOWN, buff=0.55)
        self.beat("And test a rule before you rely on it. kubectl auth can-i asks the API server directly what an identity may do.",
                  FadeIn(tip, shift=UP * 0.1), run_time=2.2)
        self.wait(0.3)
        self.play(FadeOut(VGroup(gt, L, tip)), run_time=0.5)

        # ---------- 8. moral, quick check
        m1 = T("A lock on the safe means little", 32, GOLD_M)
        m2 = T("if anyone may order the cook to open it.", 32, GOLD_M)
        m3 = T("Guard the order pad: the namespace.", 32, PURPLE_M)
        moral = VGroup(m1, m2, m3).arrange(DOWN, buff=0.25).move_to([0, 1.2, 0])
        self.beat("So the moral of the story. A lock on the safe means little if anyone may order the cook to open it. Guard the order pad, the namespace.",
                  FadeIn(VGroup(m1, m2), shift=UP * 0.1), Succession(Wait(3.4), FadeIn(m3, shift=UP * 0.1)), run_time=4.6)
        self.wait(0.4)
        self.play(FadeOut(moral), run_time=0.5)
        qq = T("Quick check", 30, YELLOW_M).move_to([0, 2.3, 0])
        qt = T("A Secret sits in namespace hello. By default, who can read it?", 30).move_to([0, 1.3, 0])
        opts = VGroup(T("only Pods that mount it", 26, GREY_B), T("nobody, it is base64", 26, GREY_B),
                      T("anyone who may read Secrets or create Pods there", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([0, 0.0, 0])
        self.beat("A quick check. A Secret sits in namespace hello. By default, who can read it? Pause and think.",
                  FadeIn(qq), FadeIn(qt), LaggedStart(*[FadeIn(o) for o in opts], lag_ratio=0.3), run_time=3.0)
        self.wait(2.0)
        self.beat("Anyone who may read Secrets, or create Pods, in that namespace. Base64 hides nothing, and the cook opens the safe for any order.",
                  opts[2].animate.set_color(GREEN_M), opts[0].animate.set_opacity(0.35), opts[1].animate.set_opacity(0.35), run_time=2.0)
        self.wait(1.0)
