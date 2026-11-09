import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bKyverno\b", "Kai-verno"), (r"\bClusterRoleBinding\b", "cluster role binding"), (r"\bClusterRole\b", "cluster role"),
            (r"\bRoleBinding\b", "role binding"), (r"\bServiceAccounts?\b", lambda m: "service account" + ("s" if m.group(0).endswith("s") else "")),
            (r"\bautomountServiceAccountToken\b", "auto-mount service account token"), (r"\bcan-i\b", "can I"),
            (r"\bdb-password\b", "D B password"), (r"\bhunter2-example\b", "hunter two example"), (r"\bcluster-admin\b", "cluster admin")])

GY = 2.45            # y of the three gates
GX = [-3.3, -0.45, 2.4]
REQ_X, ETCD_X = -6.15, 5.65
LOW = 0.9            # everything below this line is the changing detail area


def dark(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def polyline(*pts, color=YELLOW_M, sw=2):
    return VMobject(stroke_color=color, stroke_width=sw).set_points_as_corners([np.array([x, y, 0]) for x, y in pts])


def ride(pts, color=YELLOW_M, run_time=1.4):
    path = polyline(*pts)
    d = Dot(radius=0.1, color=color).move_to(path.get_start()).set_z_index(5)
    return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=smooth, run_time=run_time), FadeOut(d, run_time=0.15))


def pulse(rect, w=7, rt=0.45):
    b = rect.get_stroke_width()
    return Succession(rect.animate(run_time=rt).set_stroke(width=w), rect.animate(run_time=rt).set_stroke(width=b))


def card(lines, color, pad=0.28, align=LEFT):
    """A panel of text lines (Text mobjects) with an outline."""
    g = VGroup(*lines).arrange(DOWN, aligned_edge=align, buff=0.14)
    r = RoundedRectangle(corner_radius=0.12, width=g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.10), 1)
    g.move_to(r)
    for t in g:
        t.set_z_index(3)
    return VGroup(r, g)


class D64Access(VoiceScene):
    def construct(self):
        self.title_card("Who may do what", "authentication, RBAC, and admission")

        # ---------- 1. three gates in front of etcd
        frame = RoundedRectangle(corner_radius=0.2, width=8.8, height=2.0, stroke_color=GREY_B, stroke_width=2).move_to([(GX[0] + GX[2]) / 2, 2.6, 0])
        flab = T("API server", 22, GREY_B).move_to(frame.get_corner(UL) + np.array([0.2, -0.26, 0]), aligned_edge=LEFT)
        names = [("authentication", BLUE_M), ("authorization", GOLD_M), ("admission", PURPLE_M)]
        gates = VGroup(*[box(n, c, w=2.35, h=0.75, size=24).move_to([x, GY, 0]) for (n, c), x in zip(names, GX)])
        for g in gates:
            g[1].set_z_index(3)
        subs = VGroup(*[T(s, 20, GREY_B).next_to(g, DOWN, buff=0.14) for s, g in
                        zip(("who are you?", "may you do this?", "is it acceptable?"), gates)])
        req = chip("request", WHITE, 22).move_to([REQ_X, GY, 0])
        etcd = mbox("etcd", GREY_B, w=1.5, h=0.75, size=24).move_to([ETCD_X, GY, 0])
        etcd[1].set_z_index(3)
        short = lambda a, b: Arrow(a.get_right(), b.get_left(), buff=0.04, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.5)
        arrs = VGroup(edge_arrow(req, gates[0]), short(gates[0], gates[1]), short(gates[1], gates[2]), edge_arrow(gates[2], etcd))
        self.beat("Every request to the Kubernetes API passes three gates, in order. Only then is anything stored in etcd, the cluster's database.",
                  Create(frame), FadeIn(flab), FadeIn(req),
                  LaggedStart(*[AnimationGroup(DrawBorderThenFill(g[0]), Write(g[1])) for g in gates], lag_ratio=0.3),
                  Succession(Wait(2.4), AnimationGroup(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.25), DrawBorderThenFill(etcd[0]), Write(etcd[1]))), run_time=5.0)
        path_all = [(REQ_X + 0.6, GY), (GX[0], GY), (GX[1], GY), (GX[2], GY), (ETCD_X, GY)]

        tok = chip("token", BLUE_M, 20, mono=True).move_to([REQ_X, 1.55, 0])
        who = chip("system:serviceaccount:hello:dev", BLUE_M, 20, mono=True).move_to([GX[0] + 0.6, 0.35, 0])
        self.beat("Gate one is authentication. Who are you? A certificate or a token answers.",
                  FadeIn(subs[0], shift=UP * 0.1), pulse(gates[0][0]), FadeIn(tok, shift=UP * 0.1),
                  Succession(Wait(1.8), AnimationGroup(ride(path_all[:2], run_time=0.9), tok.animate(run_time=0.9).move_to([GX[0], 1.25, 0]).set_opacity(0)),
                             FadeIn(who, shift=DOWN * 0.1)), run_time=4.0)
        self.beat("Gate two is authorization. May you do this? RBAC answers.",
                  FadeIn(subs[1], shift=UP * 0.1), pulse(gates[1][0]), Succession(Wait(0.8), ride(path_all[1:3], run_time=0.9)), run_time=3.0)
        self.beat("Gate three is admission. Is this particular object acceptable?",
                  FadeIn(subs[2], shift=UP * 0.1), pulse(gates[2][0]), Succession(Wait(0.8), ride(path_all[2:], run_time=1.2), pulse(etcd[0])), run_time=3.2)
        self.remove(tok)

        # ---------- 2. RBAC: the question and the four objects
        self.play(FadeOut(who), FadeOut(subs), gates[0].animate.set_opacity(0.35), gates[2].animate.set_opacity(0.35), run_time=0.7)
        q_may = T("may", 30)
        def slot(t, c):
            ch = chip(t, c, 26)
            ch[0].stretch_to_fit_width(1.8)
            return ch
        q_id, q_vb, q_rs = slot("identity", BLUE_M), slot("verb", GOLD_M), slot("resource", TEAL_M)
        q_end = T("?", 30)
        qrow = VGroup(q_may, q_id, T("do", 30), q_vb, T("on", 30), q_rs, q_end).arrange(RIGHT, buff=0.25).move_to([0, 0.35, 0])
        self.beat("Start with RBAC, role-based access control. For every request, it answers one question. May this identity do this verb on this resource?",
                  Succession(Wait(2.8), LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in qrow], lag_ratio=0.25)), run_time=6.0)

        role = box("Role", BLUE_M, w=3.2, h=0.7, size=26).move_to([-3.6, -0.9, 0])
        crole = box("ClusterRole", BLUE_M, w=3.2, h=0.7, size=26).move_to([-3.6, -2.55, 0])
        rb = box("RoleBinding", GOLD_M, w=3.2, h=0.7, size=26).move_to([1.6, -0.9, 0])
        crb = box("ClusterRoleBinding", GOLD_M, w=3.2, h=0.7, size=26).move_to([1.6, -2.55, 0])
        cap = lambda s, b, c: T(s, 20, c).next_to(b, DOWN, buff=0.12)
        c_role, c_crole = cap("get, list, watch on pods, one namespace", role, BLUE_M), cap("the same, for the whole cluster", crole, BLUE_M)
        c_rb, c_crb = cap("gives a role, in one namespace", rb, GOLD_M), cap("gives a ClusterRole, everywhere", crb, GOLD_M)
        self.beat("It uses four objects. A Role lists rules, such as get, list and watch on pods, inside one namespace. A ClusterRole is the same, for the whole cluster.",
                  DrawBorderThenFill(role[0]), Write(role[1]), FadeIn(c_role),
                  Succession(Wait(4.0), AnimationGroup(DrawBorderThenFill(crole[0]), Write(crole[1]), FadeIn(c_crole))), run_time=6.4)
        subj = VGroup(chip("user", GREEN_M, 22), chip("group", GREEN_M, 22), chip("ServiceAccount", GREEN_M, 22)).arrange(DOWN, buff=0.22).move_to([5.45, -1.72, 0])
        a_rb = Arrow(rb.get_right(), subj.get_left() + UP * 0.45, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        a_crb = Arrow(crb.get_right(), subj.get_left() + DOWN * 0.45, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("A RoleBinding gives a Role, or a ClusterRole, to a subject in one namespace. A ClusterRoleBinding gives a ClusterRole to a subject everywhere.",
                  DrawBorderThenFill(rb[0]), Write(rb[1]), FadeIn(c_rb),
                  Succession(Wait(3.6), AnimationGroup(DrawBorderThenFill(crb[0]), Write(crb[1]), FadeIn(c_crb))), run_time=6.4)
        self.beat("The subject is a user, a group, or a ServiceAccount. A ServiceAccount is an identity for a program: a Pod, a CI job, an AI agent.",
                  GrowArrow(a_rb), GrowArrow(a_crb), LaggedStart(*[FadeIn(s, shift=LEFT * 0.1) for s in subj], lag_ratio=0.4),
                  Succession(Wait(3.2), pulse(subj[2][0])), run_time=5.4)
        four = VGroup(role, crole, rb, crb, c_role, c_crole, c_rb, c_crb, subj, a_rb, a_crb)

        # ---------- 3. a real example from the lab
        self.play(FadeOut(four), run_time=0.7)
        ns = RoundedRectangle(corner_radius=0.2, width=13.0, height=3.4, stroke_color=GREY_B, stroke_width=2).move_to([0, -1.9, 0])
        nsl = T("namespace hello", 22, GREY_B).move_to(ns.get_corner(UL) + np.array([0.22, -0.28, 0]), aligned_edge=LEFT)
        sa = card([T("ServiceAccount", 22, GREEN_M), M("dev", 24)], GREEN_M, align=ORIGIN).move_to([-4.6, -1.75, 0])
        self.beat("Here is a real one, from the lab. A ServiceAccount called dev, in namespace hello.",
                  Create(ns), FadeIn(nsl), Transform(q_id[1], M("dev", 26).move_to(q_id[1])), FadeIn(sa, shift=UP * 0.1), run_time=3.0)
        rl = card([T("Role", 22, BLUE_M), M("pod-creator", 22), M("pods:  get, list, watch,", 20), M("       create, delete", 20), M("pods/log:  get", 20)], BLUE_M).move_to([3.95, -1.75, 0])
        nosec = T("no rule mentions Secrets", 22, RED_M).next_to(rl, DOWN, buff=0.15)
        self.beat("A Role called pod-creator. It may get, list, watch, create and delete Pods, and read their logs. No rule mentions Secrets.",
                  FadeIn(rl, shift=UP * 0.1), Transform(q_vb[1], T("create", 26).move_to(q_vb[1])), Transform(q_rs[1], T("pods", 26).move_to(q_rs[1])),
                  Succession(Wait(4.2), FadeIn(nosec, shift=UP * 0.1)), run_time=6.0)
        rbx = card([T("RoleBinding", 22, GOLD_M), M("dev-pod-creator", 22)], GOLD_M, align=ORIGIN).move_to([-0.55, -1.75, 0])
        a1 = edge_arrow(rbx, sa)
        a2 = edge_arrow(rbx, rl)
        l1 = T("subject", 20, GREY_B).next_to(a1, UP, buff=0.08)
        l2 = T("roleRef", 20, GREY_B).next_to(a2, UP, buff=0.08)
        self.beat("And a RoleBinding, dev-pod-creator, that gives the Role to dev.",
                  FadeIn(rbx, shift=UP * 0.1), Succession(Wait(1.0), AnimationGroup(GrowArrow(a1), GrowArrow(a2), FadeIn(l1), FadeIn(l2))), run_time=3.0)
        ex = VGroup(ns, nsl, sa, rl, nosec, rbx, a1, a2, l1, l2)

        # can-i
        self.play(FadeOut(ex), FadeOut(qrow), run_time=0.7)
        c1 = M("$ kubectl auth can-i get secrets -n hello --as=system:serviceaccount:hello:dev", 20)
        r1 = M("no", 22, RED_M)
        c2 = M("$ kubectl auth can-i create pods -n hello --as=system:serviceaccount:hello:dev", 20)
        r2 = M("yes", 22, GREEN_M)
        term = VGroup(c1, r1, c2, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -0.7, 0])
        self.beat("Before you rely on a rule, test it. kubectl auth can-i asks the API server directly. The as flag acts as dev, for one request.",
                  Write(c1), run_time=3.0)
        safe = T("looks safe", 26, GREEN_M).move_to([0, -2.6, 0])
        self.beat("May dev get secrets? No. May dev create pods? Yes. It looks safe.",
                  FadeIn(r1), Succession(Wait(1.4), Write(c2, run_time=1.2), FadeIn(r2), Wait(0.6), FadeIn(safe, shift=UP * 0.1)), run_time=4.6)

        # ---------- 4. the trap: a Pod creator reads the Secret
        self.play(FadeOut(term), FadeOut(safe), gates[0].animate.set_opacity(1), gates[2].animate.set_opacity(1), run_time=0.7)
        sec = card([T("Secret", 22, RED_M), M("db-password", 22)], RED_M, align=ORIGIN).move_to([-4.7, -1.2, 0])
        kub = box("kubelet", TEAL_M, w=2.0, h=0.8, size=26).move_to([0, -1.2, 0])
        kub[1].set_z_index(3)
        peek = card([T("Pod peek", 22, BLUE_M), M("env PASSWORD", 20), M("from db-password", 20)], BLUE_M, align=ORIGIN).move_to([4.6, -1.2, 0])
        self.beat("Now dev creates a Pod called peek. It loads the db-password Secret into an environment variable, and prints it.",
                  FadeIn(peek, shift=UP * 0.1), FadeIn(kub, shift=UP * 0.1), Succession(Wait(2.4), FadeIn(sec, shift=UP * 0.1)), run_time=4.4)
        ok1 = tick(True, 0.2).move_to(gates[0].get_corner(UR) + np.array([-0.05, 0.3, 0]))
        ok2 = tick(True, 0.2).move_to(gates[1].get_corner(UR) + np.array([-0.05, 0.3, 0]))
        ok3 = tick(True, 0.2).move_to(gates[2].get_corner(UR) + np.array([-0.05, 0.3, 0]))
        q2 = T("may dev create pods?  yes", 22, GOLD_M).move_to([GX[1], 1.25, 0])
        self.beat("RBAC checks one thing. May dev create Pods? Yes. So the Pod passes, and is stored.",
                  Succession(ride(path_all[:2], run_time=0.6), Create(ok1), ride(path_all[1:3], run_time=0.6), AnimationGroup(FadeIn(q2), Create(ok2)),
                             Wait(1.0), ride(path_all[2:4], run_time=0.6), Create(ok3), ride(path_all[3:], run_time=0.6), pulse(etcd[0])), run_time=5.2)
        a_sk = edge_arrow(sec, kub, RED_M)
        a_kp = edge_arrow(kub, peek, RED_M)
        self.beat("Then the kubelet fetches the Secret for the Pod. Nobody checks dev's rights to Secrets.",
                  GrowArrow(a_sk), Succession(Wait(0.6), travel(a_sk, RED_M, run_time=0.9), GrowArrow(a_kp), travel(a_kp, RED_M, run_time=0.9)), run_time=4.0)
        logl = M("$ kubectl -n hello logs peek --as=system:serviceaccount:hello:dev", 20).move_to([0, -2.75, 0])
        out = M("The password is hunter2-example", 26, RED_M).move_to([0, -3.3, 0])
        self.beat("dev reads the Pod's log, and there is the password the Role was meant to protect.",
                  Write(logl), Succession(Wait(1.6), FadeIn(out, shift=UP * 0.1)), run_time=4.0)
        bound = T("the real boundary is the namespace", 28, YELLOW_M).move_to([0, 0.35, 0])
        self.beat("So the real boundary is the namespace. Anyone who may create Pods there can read its Secrets.",
                  FadeIn(bound, shift=DOWN * 0.1), FadeOut(q2), run_time=3.4)
        trap = VGroup(sec, kub, peek, a_sk, a_kp, logl, out, bound, ok1, ok2, ok3)

        # ---------- 5. least privilege
        self.play(FadeOut(trap), gates[0].animate.set_opacity(0.35), gates[2].animate.set_opacity(0.35), run_time=0.7)
        lp = T("least privilege: only what each identity needs", 28, GREEN_M).move_to([0, 0.35, 0])
        rules = VGroup(T("1.  Bind inside a namespace with a RoleBinding.", 24),
                       T("2.  Avoid wildcards: *  also grants every type added later.", 24),
                       T("3.  No cluster-admin for daily work.", 24),
                       T("4.  Know the big rights: create pods, nodes/proxy, escalate, bind, impersonate.", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        rules.move_to([0, -1.75, 0])
        self.beat("That is why least privilege matters. Give each identity only what it needs. The official good practices fit in four lines.",
                  FadeIn(lp, shift=DOWN * 0.1), run_time=4.2)
        self.beat("Bind inside a namespace, with a RoleBinding, whenever you can. Avoid wildcards. A star grants every resource type that exists today, and every type added later.",
                  FadeIn(rules[0], shift=RIGHT * 0.1), Succession(Wait(3.0), FadeIn(rules[1], shift=RIGHT * 0.1)), run_time=7.0)
        self.beat("Do not use cluster-admin for daily work. And know the rights that are bigger than they look: creating Pods, nodes proxy, and the verbs that change RBAC itself.",
                  FadeIn(rules[2], shift=RIGHT * 0.1), Succession(Wait(2.4), FadeIn(rules[3], shift=RIGHT * 0.1), Wait(1.0), Indicate(rules[3], color=YELLOW_M, scale_factor=1.03)), run_time=7.4)

        self.play(FadeOut(rules), run_time=0.6)
        job = T("a CI job only needs to update the image of Deployments in namespace shop", 24).move_to([0, -0.45, 0])
        bad = card([T("ClusterRoleBinding", 22, RED_M), M("cluster-admin", 22)], RED_M, align=ORIGIN).move_to([-3.4, -2.0, 0])
        good = card([T("Role in namespace shop", 22, GREEN_M), M("deployments:  get, patch", 22)], GREEN_M, align=ORIGIN).move_to([3.2, -2.0, 0])
        xb = tick(False, 0.3).next_to(bad, DOWN, buff=0.25)
        okg = tick(True, 0.3).next_to(good, DOWN, buff=0.25)
        self.beat("Say a CI job only needs to update the image of Deployments in namespace shop.",
                  FadeIn(job, shift=UP * 0.1), run_time=2.6)
        self.beat("Not cluster-admin. A Role in shop, with get and patch on deployments, and nothing more.",
                  FadeIn(bad, shift=UP * 0.1), Create(xb), Succession(Wait(1.4), AnimationGroup(FadeIn(good, shift=UP * 0.1), Create(okg))), run_time=4.4)
        self.play(FadeOut(VGroup(job, bad, good, xb, okg)), run_time=0.6)
        hab = VGroup(T("one ServiceAccount per app, never  default", 24),
                     M("automountServiceAccountToken: false", 24, GREEN_M)).arrange(DOWN, buff=0.4).move_to([0, -1.5, 0])
        self.beat("Two habits for ServiceAccounts. Give each app its own, never the namespace's default.",
                  FadeIn(hab[0], shift=UP * 0.1), run_time=3.0)
        self.beat("And if the app never calls the Kubernetes API, set automountServiceAccountToken to false. Then a broken-into Pod has no token to steal.",
                  Write(hab[1]), run_time=3.0)

        # ---------- 6. admission: the last check before etcd
        self.play(FadeOut(hab), FadeOut(lp), gates[2].animate.set_opacity(1), gates[1].animate.set_opacity(0.35), run_time=0.7)
        cmp_ = VGroup(T("RBAC: may you create Pods at all?", 26, GOLD_M), T("admission: is this Pod acceptable?", 26, PURPLE_M)).arrange(DOWN, buff=0.35).move_to([0, -0.6, 0])
        self.beat("Now the third gate. RBAC decides whether you may create Pods at all. Admission decides whether this Pod is acceptable.",
                  pulse(gates[2][0]), FadeIn(cmp_[0], shift=UP * 0.1), Succession(Wait(2.6), FadeIn(cmp_[1], shift=UP * 0.1)), run_time=5.0)
        mv = VGroup(chip("mutating: change it", PURPLE_M, 22), chip("validating: reject it", PURPLE_M, 22)).arrange(RIGHT, buff=0.5).move_to([0, -2.3, 0])
        self.beat("Admission controllers can change an object, called mutating, or reject it, called validating, before it is stored in etcd.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mv], lag_ratio=0.6), run_time=4.0)
        self.play(FadeOut(cmp_), FadeOut(mv), gates[0].animate.set_opacity(1), gates[1].animate.set_opacity(1), run_time=0.6)

        ky = box("Kyverno", PURPLE_M, w=2.2, h=0.75, size=26).move_to([GX[2], 0.25, 0])
        ky[1].set_z_index(3)
        hook = DashedLine(gates[2].get_bottom(), ky.get_top(), dash_length=0.08, stroke_width=2.5, color=PURPLE_M)
        hl = T("webhook", 20, PURPLE_M).next_to(hook, RIGHT, buff=0.15)
        self.beat("Kyverno runs your own rules at this gate, as a webhook. The API server sends it each matching request, and waits for the answer: allow, or deny.",
                  DrawBorderThenFill(ky[0]), Write(ky[1]), Create(hook), FadeIn(hl),
                  Succession(Wait(3.6), travel(Line(hook.get_start(), hook.get_end()), PURPLE_M, run_time=0.7), travel(Line(hook.get_end(), hook.get_start()), PURPLE_M, run_time=0.7)),
                  run_time=6.0)
        pol = card([M("kind: ValidatingPolicy", 20), M("name: disallow-latest-tag", 20), M("validationActions: [Deny]", 20),
                    M("namespace: hello", 20), M("!c.image.endsWith(':latest')", 20, YELLOW_M)], PURPLE_M).move_to([-3.6, -1.15, 0])
        self.beat("The lab's policy, disallow-latest-tag, denies any image tagged latest, in namespace hello.",
                  FadeIn(pol, shift=UP * 0.1), Succession(Wait(2.4), Indicate(pol[1][4], color=YELLOW_M, scale_factor=1.05)), run_time=4.0)
        cmd = M("$ kubectl -n hello run test --image=nginx:latest", 22).move_to([0, -3.05, 0])
        self.beat("Watch one request. Someone runs a test Pod with the image nginx, tag latest.",
                  Write(cmd), run_time=3.0)
        ok1 = tick(True, 0.2).move_to(gates[0].get_corner(UR) + np.array([-0.05, 0.3, 0]))
        ok2 = tick(True, 0.2).move_to(gates[1].get_corner(UR) + np.array([-0.05, 0.3, 0]))
        no3 = tick(False, 0.22).move_to(gates[2].get_corner(UR) + np.array([-0.05, 0.3, 0]))
        deny = chip("deny", RED_M, 22).next_to(ky, RIGHT, buff=0.3)
        down = [(GX[2], GY - 0.4), (GX[2], 0.62)]
        self.beat("Authentication passes. RBAC says this identity may create Pods. Then Kyverno checks the object, and says deny.",
                  Succession(ride(path_all[:2], run_time=0.6), Create(ok1), Wait(0.6), ride(path_all[1:3], run_time=0.6), Create(ok2), Wait(0.8),
                             ride(down, PURPLE_M, run_time=0.6), AnimationGroup(ky[0].animate.set_stroke(RED_M, width=5), FadeIn(deny, shift=LEFT * 0.1))),
                  run_time=6.0)
        msg = VGroup(T("The :latest tag is not allowed.", 22, RED_M), T("Use a fixed version tag, for example 1.2.0.", 22, RED_M)).arrange(DOWN, buff=0.12)
        msg.move_to([3.5, -1.4, 0])
        back = [(GX[2], GY - 0.4), (GX[2], 1.3), (REQ_X, 1.3), (REQ_X, GY - 0.35)]
        none = T("nothing stored", 20, RED_M).next_to(etcd, DOWN, buff=0.18)
        self.beat("The request is rejected, with the policy's message. Nothing is stored in etcd.",
                  Create(no3), Succession(ride(back, RED_M, run_time=1.4), FadeIn(msg, shift=UP * 0.1), Wait(0.4), FadeIn(none)), run_time=4.2)
        cmd2 = M("$ kubectl -n hello run test --image=busybox:1.37", 22).move_to(cmd)
        ok3 = tick(True, 0.2).move_to(no3)
        stored = T("stored: Pod test", 20, GREEN_M).next_to(etcd, DOWN, buff=0.18)
        self.beat("Try again with the image busybox, tag 1.37. All three gates say yes, and the Pod is stored.",
                  FadeOut(msg), FadeOut(deny), FadeOut(none), ky[0].animate.set_stroke(PURPLE_M, width=3), Transform(cmd, cmd2), FadeOut(no3),
                  Succession(Wait(2.2), ride(path_all[:3], run_time=0.9), ride(down, PURPLE_M, run_time=0.5), ride(down[::-1], GREEN_M, run_time=0.5),
                             Create(ok3), ride(path_all[2:], GREEN_M, run_time=0.9), AnimationGroup(pulse(etcd[0]), FadeIn(stored))), run_time=6.4)

        # ---------- 7. Pod Security Admission, and how to roll out a rule
        self.play(FadeOut(VGroup(pol, cmd, stored, ok1, ok2, ok3)), run_time=0.6)
        lv = VGroup(*[chip(t, c, 22) for t, c in (("privileged: no restrictions", GREY_B), ("baseline: blocks known escapes to the node", GOLD_M),
                                                    ("restricted: current hardening practice", GREEN_M))]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        lv.move_to([-3.2, -1.25, 0])
        psa = T("Pod Security Admission, built in", 24, PURPLE_M).next_to(lv, UP, buff=0.3).align_to(lv, LEFT)
        self.beat("Kubernetes also has a built-in admission check for Pod hardening, Pod Security Admission. It has three levels: privileged, baseline, and restricted.",
                  FadeIn(psa), Succession(Wait(3.4), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in lv], lag_ratio=0.5)), run_time=7.0)
        lab = M("pod-security.kubernetes.io/enforce: baseline", 20).move_to([-2.2, -3.05, 0])
        modes = VGroup(T("enforce: rejects", 22), T("warn: shows a warning", 22), T("audit: writes the audit log", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        modes.move_to([4.6, -1.7, 0])
        self.beat("You switch it on per namespace, with a label. Enforce rejects, warn shows the user a warning, and audit writes to the audit log.",
                  FadeOut(hl), FadeOut(ky), FadeOut(hook), Write(lab), Succession(Wait(2.0), LaggedStart(*[FadeIn(m, shift=LEFT * 0.1) for m in modes], lag_ratio=0.6)), run_time=6.0)
        roll = VGroup(chip("Audit", GOLD_M, 24), T("→", 28), chip("read the reports", GREY_B, 24), T("→", 28), chip("fix", GREY_B, 24), T("→", 28), chip("Deny", RED_M, 24))
        roll.arrange(RIGHT, buff=0.25).move_to([0, -1.5, 0])
        self.beat("Roll out every new rule the same way. Audit first, read the reports, fix what fails, then Deny.",
                  FadeOut(VGroup(psa, lv, lab, modes)), Succession(Wait(0.6), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in roll], lag_ratio=0.3)), run_time=4.6)

        # ---------- recap
        self.play(FadeOut(roll), run_time=0.5)
        rec = VGroup(*[T(s, 20, c).next_to(g, DOWN, buff=0.14) for s, c, g in
                       zip(("who are you?", "may you do this?", "is it acceptable?"), (BLUE_M, GOLD_M, PURPLE_M), gates)])
        last = T("and every identity gets only what it needs", 28, GREEN_M).move_to([0, -1.2, 0])
        self.beat("Authentication asks who you are. RBAC asks what you may do. Admission asks whether this object is acceptable. And every identity gets only what it needs.",
                  LaggedStart(*[AnimationGroup(FadeIn(r, shift=UP * 0.1), pulse(g[0])) for r, g in zip(rec, gates)], lag_ratio=0.9),
                  Succession(Wait(5.6), FadeIn(last, shift=UP * 0.1)), run_time=8.0)
        self.wait(1.0)
