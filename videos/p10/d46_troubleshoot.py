import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bImagePullBackOff\b", "image pull back off"), (r"\bErrImagePull\b", "err image pull"),
            (r"\bCrashLoopBackOff\b", "crash loop back off"), (r"\bBackOff\b", "back off"), (r"\bOOMKilled\b", "O O M killed"),
            (r"\bFailedScheduling\b", "failed scheduling"), (r"\bSIGKILL\b", "sig kill"), (r"\bSIGTERM\b", "sig term"),
            (r"\bMemoryPressure\b", "memory pressure"), (r"\bDiskPressure\b", "disk pressure"), (r"\bNotReady\b", "not ready"),
            (r"\btargetPort\b", "target port"), (r"--previous\b", "dash dash previous"), (r"\bsearch-api\b", "search A P I"),
            (r"\bendpoints\b", "end points"), (r"\bkind load docker-image\b", "kind load docker image")])

PX, PW, PY, PH = 2.15, 9.0, 0.05, 6.9   # terminal panel
TX, TY, LS = PX - PW / 2 + 0.3, PY + PH / 2 - 0.35, 0.39


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


class D46Troubleshoot(VoiceScene):
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

    # terminal helpers: lines are appended under the last one
    def tadd(self, *specs):
        out = VGroup()
        for spec in specs:
            text, color = (spec, WHITE) if isinstance(spec, str) else spec
            if text.startswith("$"):
                color = GREY_B if color == WHITE else color
            ind = len(text) - len(text.lstrip(" "))
            m = M(text, 20, color) if text.strip() else M(".", 20, BLACK)
            m.move_to([TX + 0.1455 * ind, TY - LS * self.nl, 0], aligned_edge=LEFT)
            self.nl += 1
            self.lines.add(m)
            out.add(m)
        return out

    def tclear(self):
        old = self.lines
        self.lines, self.nl = VGroup(), 0
        return FadeOut(old)

    def show(self, g):
        return LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in g], lag_ratio=0.25)

    def hl(self, m, color=YELLOW_M):
        return SurroundingRectangle(m, color=color, buff=0.06, stroke_width=2.5, corner_radius=0.05)

    def construct(self):
        self.title_card("Troubleshooting, step by step", "a fixed order beats guessing")
        self.lines, self.nl = VGroup(), 0

        # 1. guessing vs a method
        g = VGroup(chip("restart it", GREY_B, 26), chip("raise the limit", GREY_B, 26), chip("edit the YAML", GREY_B, 26))
        for c, p in zip(g, ([-3.6, 1.2, 0], [0.4, -0.4, 0], [3.8, 1.0, 0])):
            c.move_to(p)
        self.beat("When something breaks, the urge is to change three things, and hope.",
                  LaggedStart(*[FadeIn(c, scale=0.8) for c in g], lag_ratio=0.3), run_time=1.8)
        xs = VGroup(*[tick(False, 0.3).move_to(c) for c in g])
        self.beat("Kubernetes punishes that. Many parts react on their own, so a guess can change the evidence before you have read it.",
                  *[c.animate.set_opacity(0.3) for c in g], LaggedStart(*[Create(x) for x in xs], lag_ratio=0.3), run_time=2.4)
        self.beat("A fixed order of checks is faster, even when you think you already know the answer.",
                  FadeOut(g), FadeOut(xs), run_time=1.0)

        # 2. the layers, bottom up
        lay = VGroup(*[box(n, c, w=3.0, h=0.8, size=28) for n, c in (("Pod", TEAL_M), ("Service", GREEN_M), ("route", PURPLE_M))])
        for b, y in zip(lay, (-1.0, 0.4, 1.8)):
            b.move_to([-2.6, y, 0])
        node = RoundedRectangle(corner_radius=0.12, width=3.0, height=0.8, stroke_color=GOLD_M, stroke_width=3)
        node = VGroup(DashedVMobject(node, num_dashes=40), T("node", 28, GOLD_M)).move_to([-2.6, -2.4, 0])
        ups = VGroup(*[Arrow(lay[i].get_top(), lay[i + 1].get_bottom(), buff=0.08, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3) for i in range(2)])
        qs = VGroup(T("scheduled, running, ready, restarting?", 24, TEAL_M), T("selects those Pods? targetPort right?", 24, GREEN_M),
                    T("Gateway or Ingress sends traffic to it?", 24, PURPLE_M), T("many Pods failing at once?", 24, GOLD_M))
        for q, m in zip(qs, (*lay, node)):
            q.next_to(m, RIGHT, buff=0.6)
        nums = VGroup(*[T(str(i + 1), 28, GREY_B).next_to(m, LEFT, buff=0.4) for i, m in enumerate((*lay, node))])
        self.beat("Work from the bottom up, because each layer depends on the one below it. First the Pod. Is it scheduled, running, ready, restarting?",
                  FadeIn(lay[0], shift=UP * 0.2), FadeIn(nums[0]), Succession(Wait(1.8), FadeIn(qs[0], shift=RIGHT * 0.15)), run_time=3.0)
        self.beat("Then the Service. Does it select those Pods, and does its targetPort match the port the app listens on?",
                  GrowArrow(ups[0]), FadeIn(lay[1], shift=UP * 0.2), FadeIn(nums[1]), FadeIn(qs[1], shift=RIGHT * 0.15), run_time=2.2)
        self.beat("Then the route. Does the Gateway or Ingress send traffic to that Service?",
                  GrowArrow(ups[1]), FadeIn(lay[2], shift=UP * 0.2), FadeIn(nums[2]), FadeIn(qs[2], shift=RIGHT * 0.15), run_time=2.0)
        self.beat("The node sits under every Pod, yet it comes last. A sick node shows up as many Pods failing at once, so a single broken Pod rarely points there.",
                  Create(node[0]), FadeIn(node[1]), FadeIn(nums[3]), Succession(Wait(1.6), FadeIn(qs[3], shift=RIGHT * 0.15)), run_time=3.0)
        self.play(FadeOut(VGroup(lay, node, ups, qs, nums)), run_time=0.6)

        # 3. the ladder of commands
        names = (("1. kubectl get", TEAL_M), ("2. describe: Events", TEAL_M), ("3. logs --previous", TEAL_M),
                 ("4. Service: endpoints", GREEN_M), ("5. the node", GOLD_M))
        lad = VGroup(*[mbox(n, c, w=3.6, h=0.7, size=20) for n, c in names])
        for b, y in zip(lad, (2.6, 1.4, 0.2, -1.0, -2.2)):
            b.move_to([-4.75, y, 0])
        for b in lad:
            b[1].move_to(b[0]).align_to(b[0], LEFT).shift(RIGHT * 0.25)
        lad_l = VGroup(*[Line(lad[i].get_bottom(), lad[i + 1].get_top(), stroke_width=2, color=GREY_D) for i in range(4)])
        panel = RoundedRectangle(corner_radius=0.15, width=PW, height=PH, stroke_color=GREY_D, stroke_width=2).move_to([PX, PY, 0])
        panel.set_fill("#0a0a0a", opacity=1)

        def light(i):
            return [b[0].animate.set_stroke(width=7 if j == i else 3, opacity=1 if j == i else 0.5) for j, b in enumerate(lad)]

        self.beat("For each layer, the commands are nearly always the same. kubectl get, for STATUS, READY and RESTARTS.",
                  Create(lad[0][0]), Write(lad[0][1]), Create(panel), run_time=2.0)
        self.beat("kubectl describe, reading the Events at the bottom first.",
                  Create(lad_l[0]), Create(lad[1][0]), Write(lad[1][1]), run_time=1.4)
        self.beat("kubectl logs, with --previous if the container restarted.",
                  Create(lad_l[1]), Create(lad[2][0]), Write(lad[2][1]), run_time=1.4)
        self.beat("Then up a layer, to the Service and its endpoints. And the node, last.",
                  Create(lad_l[2]), Create(lad[3][0]), Write(lad[3][1]), Succession(Wait(1.4), AnimationGroup(Create(lad_l[3]), Create(lad[4][0]), Write(lad[4][1]))), run_time=2.6)

        # 4. Pending
        a = self.tadd("$ kubectl get pods -n hello", ("NAME                 READY  STATUS", GREY_B), "hello-devops-x7k2p   0/1    Pending")
        self.beat("Start with a Pod that never starts. kubectl get says Pending.",
                  *light(0), self.show(a), run_time=1.8)
        st = a[2]
        nolog = T("no logs yet: the container has not run", 22, GREY_B).move_to([PX, -2.95, 0])
        self.beat("Pending means the scheduler found no node. The container has not run yet, so kubectl logs has nothing to show.",
                  Indicate(st, color=YELLOW_M, scale_factor=1.03), FadeIn(nolog), run_time=2.0)
        b = self.tadd("", "$ kubectl describe pod hello-devops-x7k2p -n hello", ("Events:", GREY_B), ("  Warning  FailedScheduling", GOLD_M),
                      "  0/3 nodes are available:", "  1 node(s) had untolerated taint(s),", "  2 Insufficient cpu.")
        self.beat("The answer is in the Events. Read the FailedScheduling event slowly, because it accounts for every node.",
                  *light(1), self.show(b[1:]), run_time=2.4)
        h1, h2, h3 = self.hl(b[4]), self.hl(b[5]), self.hl(b[6])
        self.steps("Zero of three nodes are available. One is ruled out by a taint: kind's control plane. And two lack free CPU for the request.",
                   (0.6, Create(h1)), (1.8, Wait(1.8)), (0.6, ReplacementTransform(h1, h2)), (2.4, Wait(2.4)), (0.6, ReplacementTransform(h2, h3)))
        cause = chip("cause: the request is bigger than any node's free room", YELLOW_M, 22).move_to([PX, -2.95, 0])
        self.beat("So the request is larger than any node's free room. Lower the request, remove other workloads, or add a node.",
                  FadeOut(nolog), FadeIn(cause, shift=UP * 0.15), run_time=1.6)
        self.play(self.tclear(), FadeOut(h3), FadeOut(cause), run_time=0.6)

        # 5. ImagePullBackOff
        a = self.tadd("$ kubectl get pods -n debug-lab", ("NAME                  READY  STATUS", GREY_B), "catalog-6b7f9-q2l8v   0/1    ErrImagePull")
        self.beat("Next, the lab's catalog service. Its status is ErrImagePull, then ImagePullBackOff.",
                  *light(0), self.show(a), run_time=1.6)
        self.play(Transform(a[2], M("catalog-6b7f9-q2l8v   0/1    ImagePullBackOff", 20).move_to(a[2], aligned_edge=LEFT)), run_time=0.8)
        b = self.tadd("", "$ kubectl describe pod catalog-6b7f9-q2l8v -n debug-lab", ("Events:", GREY_B),
                      ("  Warning  Failed   Failed to pull image", RED_M), ('                    "hello-devops:1.0.1"', RED_M),
                      ("  Normal   BackOff  Back-off pulling image", GREY_B))
        self.beat("Again, the container never ran, so there are no logs. Go to describe, and read the Events.",
                  *light(1), self.show(b[1:]), run_time=2.2)
        h = self.hl(b[5], GREY_B)
        self.beat("BackOff in a status only means the kubelet now waits longer between tries. It is never the cause.",
                  Create(h), run_time=1.0)
        h2 = self.hl(VGroup(b[3], b[4]), RED_M)
        self.beat("Look for the first error. Failed to pull image hello-devops, version 1.0.1.",
                  ReplacementTransform(h, h2), run_time=1.0)
        cause = chip("cause: tag 1.0.1, but kind has only hello-devops:1.0.0", YELLOW_M, 22).move_to([PX, -2.95, 0])
        self.beat("But the image loaded into kind is 1.0.0. So check the name and the tag, the registry login for private images, and on kind, whether you ran kind load docker-image.",
                  FadeIn(cause, shift=UP * 0.15), run_time=1.6)
        self.play(self.tclear(), FadeOut(h2), FadeOut(cause), run_time=0.6)

        # 6. CrashLoopBackOff
        a = self.tadd("$ kubectl get pods -n debug-lab", ("NAME                  READY  STATUS            RESTARTS", GREY_B),
                      "reports-5c8d7-tr5vn   0/1    CrashLoopBackOff  1")
        self.steps("Now reports. RESTARTS keeps going up, and the status says CrashLoopBackOff.",
                   (1.2, *light(0), self.show(a)),
                   *[(0.45, Transform(a[2], M(f"reports-5c8d7-tr5vn   0/1    CrashLoopBackOff  {n}", 20).move_to(a[2], aligned_edge=LEFT))) for n in (2, 3, 4)])
        # restart back-off timeline
        T0, SC = PX - 3.9, 0.075
        gaps = [10, 20, 40, 80]
        xs_ = [T0]
        for gp in gaps:
            xs_.append(xs_[-1] + gp * SC)
        ty = 0.6
        tl = Line([T0 - 0.2, ty, 0], [PX + 4.1, ty, 0], stroke_width=2, color=GREY_B)
        crashes = VGroup(*[tick(False, 0.12).move_to([x, ty, 0]) for x in xs_[:4]])
        glabs = VGroup(*[T(f"{gp} s", 20, GREY_B).move_to([(xs_[i] + xs_[i + 1]) / 2, ty + 0.35, 0]) for i, gp in enumerate(gaps[:3])])
        more = T("... up to 5 min", 20, GREY_B).move_to([xs_[3] + 1.5, ty + 0.35, 0])
        self.beat("The container keeps exiting, and the kubelet waits longer before each restart. 10 seconds, then 20, then 40, up to five minutes.",
                  Create(tl), LaggedStart(*[Create(crashes[i]) if i == 0 else AnimationGroup(FadeIn(glabs[i - 1]), Create(crashes[i])) for i in range(4)],
                                          FadeIn(more), lag_ratio=0.6), run_time=3.4)
        sym = T("a symptom, not a cause", 24, YELLOW_M).move_to([PX, -0.3, 0])
        self.beat("CrashLoopBackOff is a symptom. But this time the container ran, so there is evidence.",
                  FadeIn(sym, shift=UP * 0.15), run_time=1.2)
        self.play(FadeOut(VGroup(tl, crashes, glabs, more, sym)), run_time=0.5)
        self.nl = 3
        b = self.tadd("", "$ kubectl logs reports-5c8d7-tr5vn -n debug-lab --previous", ("$", GREY_B))
        empty = T("(empty)", 22, GREY_B).next_to(b[2], RIGHT, buff=0.3)
        self.beat("Read logs --previous. That shows the container that crashed, not the fresh one.",
                  *light(2), self.show(b[1:]), run_time=1.8)
        self.beat("Its log is empty. The process was killed from outside, before it could print anything.",
                  FadeIn(empty), run_time=1.0)
        c = self.tadd("", "$ kubectl describe pod reports-5c8d7-tr5vn -n debug-lab", ("Last State:  Terminated", GREY_B),
                      ("  Reason:    OOMKilled", RED_M), ("  Exit Code: 137", RED_M))
        self.beat("So read Last State in describe. Reason, OOMKilled. Exit code, 137.",
                  *light(1), self.show(c[1:]), run_time=2.0)
        h = self.hl(VGroup(c[3], c[4]), RED_M)
        cause = chip("cause: its memory limit, 40Mi, is too small", YELLOW_M, 22).move_to([PX, -2.95, 0])
        self.beat("The container went over its memory limit. Its file sets the limit to only 40Mi.",
                  Create(h), FadeIn(cause, shift=UP * 0.15), run_time=1.6)
        self.play(self.tclear(), FadeOut(h), FadeOut(cause), FadeOut(empty), run_time=0.6)

        # exit codes
        codes = VGroup(*[VGroup(M(cd, 26, col), T(txt, 24)).arrange(RIGHT, buff=0.5) for cd, col, txt in (
            ("0  ", GREEN_M, "finished on purpose"), ("1  ", GOLD_M, "the app's own error: read the logs"),
            ("137", RED_M, "SIGKILL (128 + 9), most often the OOM killer"), ("143", BLUE_M, "SIGTERM (128 + 15), the polite stop"))])
        codes.arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([PX, 0.6, 0])
        for row in codes:
            row[1].move_to([row[0].get_left()[0] + 1.0, row[0].get_center()[1], 0], aligned_edge=LEFT)
        ech = T("exit code under Last State", 24, GREY_B).next_to(codes, UP, buff=0.5)
        self.beat("The exit code narrows things down fast. Zero, the process finished on purpose. One, the app exited with its own error.",
                  FadeIn(ech), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in codes[:2]], lag_ratio=0.6), run_time=2.8)
        self.beat("137, killed with SIGKILL, most often the out of memory killer. 143, stopped with SIGTERM, the polite stop signal.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in codes[2:]], lag_ratio=0.6), run_time=2.8)
        self.play(FadeOut(VGroup(codes, ech)), run_time=0.5)

        # 7. Service with no endpoints
        a = self.tadd("$ kubectl get pods -n debug-lab -l app=search", ("NAME                 READY  STATUS", GREY_B),
                      ("search-7d4b9-2qkzt   1/1    Running", GREEN_M), ("search-7d4b9-8hx7m   1/1    Running", GREEN_M))
        fail = T("but requests to http://search.debug-lab fail", 22, RED_M).move_to([PX, -2.95, 0])
        self.beat("Then search. Both Pods are Running and ready. Yet requests to the search Service fail.",
                  *light(0), self.show(a), Succession(Wait(1.6), FadeIn(fail)), run_time=2.6)
        b = self.tadd("", "$ kubectl get endpointslices -n debug-lab \\", "    -l kubernetes.io/service-name=search",
                      ("NAME           ENDPOINTS", GREY_B), ("search-x5k9p   <unset>", RED_M))
        self.beat("Every Pod looks healthy, so move up a layer, to the Service, and ask for its endpoints.",
                  *light(3), self.show(b[1:]), run_time=2.4)
        h = self.hl(b[4], RED_M)
        self.beat("Unset. The Service matches no Pods, so it sends traffic nowhere.", Create(h), run_time=1.0)
        c = self.tadd("", ("Service selector:   app: search-api", GOLD_M), ("Pod labels:         app=search", GREEN_M))
        self.beat("Compare the Service's selector with the Pods' labels. The selector asks for app: search-api. The Pods are labeled app: search.",
                  FadeOut(h), self.show(c[1:]), run_time=2.4)
        hs = VGroup(self.hl(c[1][-10:], RED_M), self.hl(c[2][-6:], GREEN_M))
        cause = chip("cause: the selector matches no Pod labels", YELLOW_M, 22).move_to([PX, -2.95, 0])
        self.beat("They do not match. Fix the selector, and check that targetPort is the port the app listens on.",
                  Create(hs), FadeOut(fail), FadeIn(cause, shift=UP * 0.15), run_time=1.8)
        self.play(self.tclear(), FadeOut(hs), FadeOut(cause), run_time=0.6)

        # 8. the node
        a = self.tadd("$ kubectl get nodes", ("NAME                   STATUS", GREY_B), "devops-control-plane   Ready",
                      "devops-worker          Ready", ("devops-worker2         NotReady", RED_M))
        self.beat("And the node? Look there when many Pods fail at once, all on one node. kubectl get nodes shows NotReady when a kubelet stops reporting.",
                  *light(4), self.show(a), run_time=2.6)
        b = self.tadd("", "$ kubectl describe node devops-worker2", ("Conditions:", GREY_B), ("  MemoryPressure", GOLD_M), ("  DiskPressure", GOLD_M))
        self.beat("Then kubectl describe node shows conditions such as MemoryPressure and DiskPressure, and lists the Pods on it with their requests.",
                  self.show(b[1:]), run_time=2.2)
        self.play(self.tclear(), run_time=0.6)

        # 9. keep the evidence
        ev = VGroup(T("before you delete anything:", 28, YELLOW_M),
                    M("describe   logs --previous", 26, TEAL_M),
                    T("Events are kept for about an hour", 24, GREY_B)).arrange(DOWN, buff=0.4).move_to([PX, 0.6, 0])
        self.beat("One habit matters most. Deleting the broken Pod throws away the evidence. Events are kept for about an hour, so run describe and logs --previous first.",
                  FadeIn(ev[0], shift=UP * 0.15), Succession(Wait(2.0), FadeIn(ev[2], shift=UP * 0.15)), Succession(Wait(3.6), FadeIn(ev[1], shift=UP * 0.15)), *light(1), run_time=5.0)
        self.play(FadeOut(ev), run_time=0.5)

        # 10. recap
        rc = VGroup(T("Pod, then Service, then route, then node", 28, YELLOW_M),
                    T("get, describe, logs --previous", 28, TEAL_M),
                    T("change one thing at a time", 28, WHITE)).arrange(DOWN, buff=0.45).move_to([PX, 0.6, 0])
        self.beat("Debug from the bottom up: Pod, then Service, then route, then node. Get, describe, logs. And change one thing at a time.",
                  *[b[0].animate.set_stroke(width=3, opacity=1) for b in lad], LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.5), run_time=4.0)
        self.wait(1.0)
