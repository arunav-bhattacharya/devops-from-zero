import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bCrashLoopBackOff\b", "crash loop back off"), (r"\bImagePullBackOff\b", "image pull back off"),
            (r"\bCreateContainerConfigError\b", "create container config error"), (r"\bContainerCreating\b", "container creating"),
            (r"\bREDIS_HOST\b", "redis host"), (r"\bNXDOMAIN\b", "N X domain"),
            (r"\bnslookup\b", "N S lookup"), (r"\bprintenv\b", "print env"), (r"--previous\b", "dash dash previous"),
            (r"\bOOMKilled\b", "O O M killed"), (r"\bConfigMap\b", "config map"), (r"\bbusybox\b", "busy box")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(c, s=1.0):
    head = Circle(radius=0.2, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.3), opacity=1)
    body = RoundedRectangle(corner_radius=0.15, width=0.62, height=0.72, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.2), opacity=1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale(s)


def term(lines, w=12.6, size=22):
    g = VGroup(*[M(t, size, c) for t, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    fit(g, w - 0.6)
    r = RoundedRectangle(corner_radius=0.1, width=w, height=g.height + 0.5, stroke_color=GREY_D, stroke_width=2).set_fill("#0b0b0b", 1)
    g.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.3)
    return VGroup(r, g)


class D46Method(VoiceScene):
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
        self.title_card("Read before you touch", "a fixed order of checks for a broken Pod")

        # ---------- 1. the manager who changed three things
        mgr = person(GOLD_M).move_to([-5.2, 0.0, 0])
        guest = T("\"The food never came.\"", 28, PURPLE_M).move_to([-2.6, 2.6, 0])
        self.beat("Picture a Saturday night, and a guest who says the food never came.",
                  FadeIn(guest), FadeIn(mgr), run_time=1.6)
        ch = VGroup(chip("restart the oven", RED_M, 26), chip("reset the card reader", RED_M, 26), chip("move two cooks", RED_M, 26)).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([-1.2, 0.0, 0])
        self.beat("The new manager runs into the kitchen, restarts the oven, resets the card reader, and moves two cooks to other stations.",
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in ch], lag_ratio=0.6), run_time=4.0)
        soup = chip("soup arrives", GREEN_M, 26).move_to([4.2, 0.0, 0])
        qm = VGroup(*[T("?", 36, YELLOW_M).next_to(c, RIGHT, buff=0.3) for c in ch])
        self.beat("Ten minutes later, the soup arrives. Which of the three changes fixed it? Nobody knows. Maybe none of them did.",
                  FadeIn(soup), Succession(Wait(1.6), LaggedStart(*[FadeIn(q) for q in qm], lag_ratio=0.3)), run_time=3.4)
        nxt = T("next Saturday: again", 28, RED_M).move_to([4.2, -1.2, 0])
        self.beat("And next Saturday, it happens again.", FadeIn(nxt), run_time=1.2)
        self.beat("Three changes and a happy ending isn't a diagnosis. It's a lottery ticket that happened to win. So when a Pod won't start, where do you look first?",
                  run_time=None)
        self.play(FadeOut(VGroup(mgr, guest, ch, soup, qm, nxt)), run_time=0.6)

        # ---------- 2. why guessing is worse in Kubernetes
        pod = RoundedRectangle(corner_radius=0.15, width=3.0, height=2.6, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.1), 1).move_to([-3.6, 0.2, 0])
        pl = M("broken Pod", 24, TEAL_M).next_to(pod, UP, buff=0.15)
        clues = VGroup(chip("crashed container's logs", GREY_B, 22), chip("its last state", GREY_B, 22), chip("newest events", GREY_B, 22)).arrange(DOWN, buff=0.25).move_to(pod)
        self.beat("Kubernetes makes guessing worse. A broken Pod is full of clues. The crashed container's logs. Its last state. The newest events.",
                  FadeIn(pod), FadeIn(pl), LaggedStart(*[FadeIn(c) for c in clues], lag_ratio=0.5), run_time=3.6)
        dl = M("kubectl delete pod ...", 24, RED_M).move_to([2.6, 1.2, 0])
        self.steps("Now restart or delete it, to see if it helps. Kubernetes happily starts a fresh one. And the clues go with the old one.",
                   (1.2, FadeIn(dl)), (1.4, Wait(1.4)), (1.2, clues.animate.shift(DOWN * 0.6).set_opacity(0)), (1.0, Indicate(pod, color=TEAL_M)))
        self.remove(clues)
        rule = VGroup(T("Read the evidence before you change anything.", 30, YELLOW_M), T("A restart deletes clues.", 30, YELLOW_M)).arrange(DOWN, buff=0.2).move_to([0, -2.6, 0])
        self.beat("So here's the rule. Read the evidence before you change anything. A restart deletes clues.",
                  FadeIn(rule, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(pod, pl, dl, rule)), run_time=0.6)

        # ---------- 3. the ladder: Pod, Service, route, node
        LX = -2.6
        route = box("route: Gateway", BLUE_M, w=3.6, size=26).move_to([LX, 2.4, 0])
        svc = box("Service", BLUE_M, w=3.6, size=26).move_to([LX, 0.95, 0])
        pd = box("Pod", TEAL_M, w=3.6, size=26).move_to([LX, -0.5, 0])
        node = box("node", GREY_B, w=7.0, size=26).move_to([LX + 1.0, -2.1, 0])
        rest = VGroup(T("the front door", 26, GOLD_M).next_to(route, RIGHT, buff=0.6), T("the host's list", 26, GOLD_M).next_to(svc, RIGHT, buff=0.6),
                      T("the table", 26, GOLD_M).next_to(pd, RIGHT, buff=0.6), T("the whole kitchen", 26, GOLD_M).next_to(node, RIGHT, buff=0.3))
        ups = VGroup(edge_arrow(pd, svc), edge_arrow(svc, route))
        self.beat("A method beats guessing. Work from the bottom up, because each layer depends on the one below it.",
                  FadeIn(node), FadeIn(pd), FadeIn(svc), FadeIn(route), GrowArrow(ups[0]), GrowArrow(ups[1]), run_time=2.4)

        def num(n, m):
            c = Circle(radius=0.24, stroke_color=YELLOW_M, stroke_width=2.5).set_fill(BLACK, 1)
            return VGroup(c, T(str(n), 24, YELLOW_M).move_to(c)).next_to(m, LEFT, buff=0.25)
        n1, n2, n3, n4 = num(1, pd), num(2, svc), num(3, route), num(4, node)
        self.beat("One, the Pod. Is it scheduled, running, ready, restarting? That's the table.",
                  FadeIn(n1), FadeIn(rest[2]), run_time=1.6)
        self.beat("Two, the Service. Does it select those Pods, and send to the port the app listens on? The host's list.",
                  FadeIn(n2), FadeIn(rest[1]), run_time=1.6)
        self.beat("Three, the route. Does the Gateway send traffic to that Service? The front door.",
                  FadeIn(n3), FadeIn(rest[0]), run_time=1.6)
        self.beat("And four, the node, the whole kitchen. It sits under every Pod, yet it comes last.",
                  FadeIn(n4), FadeIn(rest[3]), run_time=1.6)
        many = VGroup(*[Circle(radius=0.16, stroke_color=RED_M, stroke_width=2.5).set_fill(tint(RED_M, 0.4), 1) for _ in range(5)]).arrange(RIGHT, buff=0.2).move_to(node.get_center() + RIGHT * 1.6)
        self.beat("Why last? A sick kitchen shows up as many tables failing at once. One broken Pod rarely points there.",
                  LaggedStart(*[GrowFromCenter(m) for m in many], lag_ratio=0.15), run_time=2.0)
        self.play(FadeOut(many), run_time=0.4)
        ladder = VGroup(route, svc, pd, node, ups, n1, n2, n3, n4, rest)
        self.play(ladder.animate.scale(0.62).move_to([-3.9, 0.6, 0]), run_time=1.0)
        cmds = VGroup(M("1  kubectl get", 24), M("2  kubectl describe", 24), M("3  kubectl logs --previous", 24),
                      M("4  kubectl get events", 24), M("5  exec, port-forward, debug", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([3.2, 0.6, 0])
        notes = VGroup(T("STATUS, READY, RESTARTS", 20, GREY_B), T("Events at the bottom first", 20, GREY_B), T("the one that crashed", 20, GREY_B),
                       T("the whole namespace, by time", 20, GREY_B), T("test from inside", 20, GREY_B))
        for c, n in zip(cmds, notes):
            n.next_to(c, DOWN, buff=0.06).align_to(c, LEFT).shift(RIGHT * 0.5)
        cmds_g = VGroup(*[VGroup(c, n) for c, n in zip(cmds, notes)]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([3.0, 0.4, 0])
        self.beat("At every layer, the commands are nearly always the same five. Get, for the status. Describe, reading the Events at the bottom first. Logs. Events for the whole namespace. And then, tests from inside.",
                  LaggedStart(*[FadeIn(c, shift=LEFT * 0.15) for c in cmds_g], lag_ratio=0.6), run_time=9.0)

        # ---------- 4. two families of states
        self.play(FadeOut(cmds_g), run_time=0.5)
        hA = T("never started", 28, GOLD_M).move_to([0.5, 2.7, 0])
        hB = T("started, then failed", 28, RED_M).move_to([4.6, 2.7, 0])
        sA = VGroup(*[M(s, 22, WHITE) for s in ("Pending", "ContainerCreating", "ImagePullBackOff", "CreateContainerConfigError")]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        sA.next_to(hA, DOWN, buff=0.4)
        sB = VGroup(*[M(s, 22, WHITE) for s in ("CrashLoopBackOff", "OOMKilled", "Running, 0/1 ready")]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        sB.next_to(hB, DOWN, buff=0.4)
        self.beat("Down at the Pod, the trouble comes in two families. In the first, the container never ran at all.",
                  FadeIn(hA), LaggedStart(*[FadeIn(s) for s in sA], lag_ratio=0.3), run_time=2.6)
        evA = chip("no logs: read the Events", GOLD_M, 22).next_to(sA, DOWN, buff=0.4)
        self.beat("So kubectl logs has nothing to show. The cook never lit the stove, so there's no smoke to read. The answer is in describe, under Events.",
                  FadeIn(evA, shift=UP * 0.1), run_time=2.0)
        self.beat("In the second family, the container ran at least once. So it left clues in its logs, and in its last state.",
                  FadeIn(hB), LaggedStart(*[FadeIn(s) for s in sB], lag_ratio=0.3), run_time=2.4)
        q = T("logs show nothing. Where is the error?", 24, YELLOW_M).next_to(sB, DOWN, buff=0.4)
        self.beat("Here's a classic. A Pod is in CrashLoopBackOff. kubectl logs shows nothing useful. Where's the error message? Pause and guess.",
                  Indicate(sB[0], color=RED_M), FadeIn(q), run_time=2.0)
        self.wait(2.0)
        aB = chip("kubectl logs --previous", RED_M, 22, mono=True).move_to(q)
        self.beat("In the previous container's log. After a restart, plain logs shows the new container, which may not have printed anything yet. Dash dash previous shows the one that crashed. The note left by the cook who just went home.",
                  Transform(q, aB), run_time=1.6)
        bo = T("\"BackOff\" = waits longer between tries. Never the cause.", 24, GREY_B).move_to([2.6, -3.2, 0])
        self.beat("And notice the word BackOff in two of these names. It only means the kubelet now waits longer between tries. It's never the cause. Look for the first error.",
                  FadeIn(bo, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(hA, hB, sA, sB, evA, q, bo)), run_time=0.6)

        # ---------- 5. a real case: one letter too many
        self.play(ladder.animate.scale(0.75).move_to([-5.0, 2.0, 0]).set_opacity(0.5), run_time=0.8)
        case = T("someone changed REDIS_HOST in the ConfigMap, then restarted the Deployment", 22, GREY_B).move_to([1.3, 3.3, 0])
        fit(case, 8.6)
        t1 = term([("$ kubectl get pods -n hello -l app=hello-devops", GREY_B),
                   ("NAME                           READY  STATUS   RESTARTS", GREY_B),
                   ("hello-devops-5d8f7c6b9-4kq2w   0/1    Running  0", YELLOW_M),
                   ("hello-devops-6c9f8b7d4-2qkzt   1/1    Running  0", WHITE),
                   ("hello-devops-6c9f8b7d4-8hx7m   1/1    Running  0", WHITE),
                   ("hello-devops-6c9f8b7d4-tr5vn   1/1    Running  0", WHITE)], w=9.6).move_to([1.3, 1.1, 0])
        self.beat("Let's run the method on a real mistake. Someone changed one setting for the app, and restarted it. Now the rollout never finishes.",
                  FadeIn(case), run_time=1.6)
        self.beat("Step one, get. One new Pod is Running, but zero of one ready. The three old Pods keep serving, so users see nothing wrong yet.",
                  FadeIn(t1), Succession(Wait(2.0), Indicate(t1[1][2], color=YELLOW_M)), run_time=3.6)
        self.beat("The app counts visits in Redis. So the tempting move is obvious. Restart Redis! Let's not. Let's read first.",
                  run_time=None)
        t2 = term([("$ kubectl events -n hello --for pod/hello-devops-5d8f7c6b9-4kq2w --types=Warning", GREY_B),
                   ("Warning  Unhealthy  Readiness probe failed: HTTP probe failed with statuscode: 503", RED_M),
                   ("$ kubectl get pods -n hello -l app=redis", GREY_B),
                   ("redis-7c6d9f5b8d-q2l8v   1/1   Running   0", GREEN_M)], w=12.6).move_to([0, -1.6, 0])
        self.beat("Step two, the events. Readiness fails with 503, and the app returns 503 when it can't reach Redis. But Redis itself is Running and ready.",
                  FadeIn(t2[0]), LaggedStart(*[FadeIn(l) for l in t2[1]], lag_ratio=0.6), run_time=4.0)
        self.beat("So restarting Redis would have changed nothing, and taught us nothing. The problem is between the two.",
                  Indicate(t2[1][3], color=GREEN_M), run_time=1.8)
        self.play(FadeOut(VGroup(t1, t2)), run_time=0.5)
        t3 = term([("$ kubectl exec hello-devops-5d8f7c6b9-4kq2w -n hello -- printenv REDIS_HOST", GREY_B),
                   ("rediss", YELLOW_M),
                   ("$ kubectl exec hello-devops-5d8f7c6b9-4kq2w -n hello -- nslookup rediss", GREY_B),
                   ('exec: "nslookup": executable file not found in $PATH', RED_M)], w=12.6).move_to([0, 1.1, 0])
        self.beat("Check what the new Pod was given. printenv says rediss, with two S's at the end. It looks almost right.",
                  FadeIn(t3[0]), FadeIn(t3[1][0]), Succession(Wait(1.4), FadeIn(t3[1][1])), run_time=2.6)
        self.beat("We want to test that name from inside the Pod's network. But the app's image has no DNS tools. No nslookup at all.",
                  FadeIn(t3[1][2]), Succession(Wait(1.6), FadeIn(t3[1][3])), run_time=3.0)
        helper = person(GREEN_M, 0.7).move_to([5.6, -1.4, 0])
        self.beat("So we send a helper with a toolbox to stand next to the cook. kubectl debug adds a temporary extra container to the running Pod, with an image you choose, such as busybox.",
                  FadeIn(helper, shift=LEFT * 0.3), run_time=1.8)
        t4 = term([("$ kubectl debug -it hello-devops-5d8f7c6b9-4kq2w -n hello --image=busybox:1.37 --target=web", GREY_B),
                   ("/ # nslookup rediss.hello.svc.cluster.local", GREY_B),
                   ("** server can't find rediss.hello.svc.cluster.local: NXDOMAIN", RED_M),
                   ("/ # nslookup redis.hello.svc.cluster.local", GREY_B),
                   ("Name:    redis.hello.svc.cluster.local   Address: 10.96.84.21", GREEN_M)], w=11.0).move_to([-0.6, -1.7, 0])
        self.beat("It shares the Pod's network, so its answers are the app's answers. Pause and guess: does the name rediss exist?",
                  FadeIn(t4[0]), FadeIn(t4[1][0]), FadeIn(t4[1][1]), run_time=2.0)
        self.wait(2.0)
        self.beat("NXDOMAIN. No such name. And the correct name, redis with one S, resolves to the Redis Service's address.",
                  FadeIn(t4[1][2]), Succession(Wait(1.6), AnimationGroup(FadeIn(t4[1][3]), FadeIn(t4[1][4]))), run_time=3.4)
        found = chip("cause: a typo in the ConfigMap", YELLOW_M, 26).move_to([1.3, 3.3, 0])
        self.beat("That's the proof. A typo in the ConfigMap, one letter too many. Redis and the network are fine. One change fixes it, and we know exactly why.",
                  Transform(case, found), run_time=1.8)
        self.beat("By the way, that helper has a name: an ephemeral container. Ephemeral means short-lived. It's never restarted, and it goes away when the Pod is deleted.",
                  Indicate(helper, color=GREEN_M), run_time=2.0)
        self.play(FadeOut(VGroup(t3, t4, helper, case)), run_time=0.6)

        # ---------- 6. guardrails
        self.play(ladder.animate.set_opacity(1).scale(1 / 0.75 / 0.62).move_to([-2.8, 0.3, 0]), run_time=1.0)
        g1 = VGroup(T("change one thing at a time", 28, YELLOW_M), T("then watch what happens", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([3.8, 1.8, 0])
        g2 = VGroup(M("Forbidden", 28, RED_M), T("a locked door, not a broken one", 24, GREY_B), M("kubectl auth can-i", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([3.8, 0.0, 0])
        g3 = VGroup(T("bugs in your own code", 28, PURPLE_M), T("need the app's logs, metrics, traces", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([3.8, -2.0, 0])
        self.beat("A few guardrails. First, change one thing at a time, and watch what happens. That's the opposite of our manager.",
                  FadeIn(g1), run_time=1.8)
        self.beat("Second, an error that says Forbidden is not a bug. Your YAML is fine. Your key just doesn't open that door. Ask the cluster with kubectl auth can-i.",
                  FadeIn(g2), run_time=2.0)
        self.beat("Third, the honest limit. The method finds causes only in what Kubernetes can see. A bug inside your app's own code still needs the app's logs, and later, metrics and traces.",
                  FadeIn(g3), run_time=2.0)
        self.play(FadeOut(VGroup(ladder, g1, g2, g3)), run_time=0.6)

        # ---------- 7. moral and a quick check
        mor = VGroup(T("Read before you touch. A restart deletes clues.", 30),
                     T("bottom up: Pod, Service, route; the node when many fail", 28, BLUE_M),
                     T("get, describe, logs --previous, events, then test inside", 28, TEAL_M),
                     T("never started: read the Events", 28, GOLD_M),
                     T("no tools in the image: kubectl debug", 28, GREEN_M)).arrange(DOWN, buff=0.35)
        self.beat("So, the moral of the story. Read before you touch, because a restart deletes clues. Climb from the bottom: the Pod, the Service, the route, and the node when many fail together. At each step: get, describe, logs with previous, events, then test from inside. If it never started, read the Events. And if the image has no tools, bring your own with kubectl debug.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mor], lag_ratio=0.8), run_time=11.0)
        self.play(FadeOut(mor), run_time=0.6)
        qq = VGroup(T("A new Pod stays Pending. Its event says:", 30),
                    M("0/3 nodes are available: 1 node(s) had untolerated taint(s),", 22, GREY_B),
                    M("2 Insufficient memory", 22, GREY_B),
                    T("What is the most likely fix?", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 0.9, 0])
        self.beat("One quick check. A new Pod stays Pending. Its event says zero of three nodes are available. One had a taint, and two had insufficient memory. What's the most likely fix? Pause and think.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in qq], lag_ratio=0.5), run_time=4.5)
        self.wait(2.0)
        ans = chip("lower the memory request, or free up room", GOLD_M, 28).move_to([0, -1.7, 0])
        self.beat("Lower the memory request, or free up room. The scheduler counts requests, and the event accounted for every node. Read slowly, and it tells you. Thanks for watching.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.0)
