import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Day 41, fifth pass (Venkat style). Restaurant manager world: the host stand at the door.
# Concept: a Service gives changing Pods one fixed address; the EndpointSlice is the host's clipboard of
# ready Pods; kube-proxy writes the rules. Addresses and outputs from the lesson's worked example.
# Colours: Pods = BLUE, Service = GOLD, EndpointSlice = GREEN, kube-proxy rules = PURPLE, calling Pod = TEAL,
# failure = RED, prompts = YELLOW.

SAY.extend([(r"\b10\.96\.171\.215\b", "ten, ninety six, one seven one, two fifteen"), (r"\bEndpointSlices\b", "endpoint slices"),
            (r"\bEndpointSlice\b", "endpoint slice"), (r"\bClusterIP\b", "cluster I P"), (r"\bkube-proxy\b", "cube proxy"),
            (r"\bCoreDNS\b", "core D N S"), (r"\bgRPC\b", "G R P C")])

PODY, TAGY = -2.45, -1.78
PXS = [-5.4, -2.7, 0.0, 2.7, 5.4]
IPS = ["10.244.1.3", "10.244.2.4", "10.244.1.5"]


def tint(c, k=0.18):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def podbox(text, x, color=BLUE_M):
    r = RoundedRectangle(corner_radius=0.1, width=2.0, height=0.66, stroke_color=color, stroke_width=3).move_to([x, PODY, 0])
    r.set_fill(tint(color, 0.22), opacity=1)
    return VGroup(r, M(text, 22).move_to(r))


def tag(text, x, color=GREY_B):
    return M(text, 20, color).move_to([x, TAGY, 0])


class Base(VoiceScene):
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

    def pause_guess(self, pos=None):
        c = chip("pause and guess", YELLOW_M, 26).move_to(pos if pos is not None else [4.6, -3.0, 0])
        n2 = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        n1 = T("1", 30, YELLOW_M).move_to(n2)
        self.play(FadeIn(c, shift=UP * 0.1), FadeIn(n2), run_time=0.4)
        self.wait(0.8)
        self.play(ReplacementTransform(n2, n1), run_time=0.2)
        self.wait(0.8)
        self.play(FadeOut(c), FadeOut(n1), run_time=0.3)


class D41HostStand(Base):
    def construct(self):
        self.title_card("How do you call a Pod that keeps moving?", "one fixed number for a changing floor")

        # ---------- 1. QUESTION + FAMILIAR: the waiter's direct number
        days = VGroup(T("Monday", 28, GREEN_M), T("Wednesday", 28, YELLOW_M), T("Friday", 28, RED_M)).arrange(RIGHT, buff=1.6).move_to([0, 1.6, 0])
        notes = VGroup(T("the waiter answers", 24, GREY_B), T("changed shift", 24, GREY_B), T("a stranger answers", 24, GREY_B))
        for n, d in zip(notes, days):
            n.next_to(d, DOWN, buff=0.2)
        self.steps("A friend loves your restaurant, so they ask one waiter for a direct phone number. On Monday it works. On Wednesday the waiter changes shift. On Friday your friend calls, and a stranger answers.",
                   (0.8, FadeIn(days[0]), FadeIn(notes[0])), (1.4, Wait(1.4)), (0.8, FadeIn(days[1]), FadeIn(notes[1])),
                   (1.0, Wait(1.0)), (0.8, FadeIn(days[2]), FadeIn(notes[2])))
        own = T("the restaurant's own number would have worked every time", 28, GOLD_M).move_to([0, -0.3, 0])
        self.beat("The restaurant's own number would have worked every time, because it always reaches whoever is on the floor.",
                  FadeIn(own, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(days, notes, own)), run_time=0.6)

        pods = [podbox(ip, x) for ip, x in zip(IPS, PXS)]
        tags = [tag("app: hello-devops", x) for x in PXS[:3]]
        self.beat("Pods have the same problem. Every Pod gets its own IP address, the number that names it on the network. Here are three hello-devops Pods.",
                  LaggedStart(*[FadeIn(VGroup(p, t), shift=UP * 0.15) for p, t in zip(pods, tags)], lag_ratio=0.25), run_time=2.2)
        cfg = VGroup(M("url: http://", 26, GREY_B), M("10.244.1.5", 26, BLUE_M), M(":8000", 26, GREY_B)).arrange(RIGHT, buff=0.05).move_to([0, 0.9, 0])
        self.beat("You copy one address from kubectl get pods into a settings file. It works today, so it feels safe. That is the trap.",
                  FadeIn(cfg, shift=DOWN * 0.15), Indicate(pods[2][1], color=BLUE_M), run_time=1.8)
        np_ = podbox("new address", PXS[2])
        self.steps("Then a rollout replaces that Pod. The new Pod gets a new address, and your settings file now points at nobody.",
                   (0.9, pods[2].animate.set_opacity(0.25)), (0.6, Wait(0.6)),
                   (0.9, FadeOut(pods[2]), FadeIn(np_, scale=0.8)), (0.7, cfg[1].animate.set_color(RED_M)))
        pods[2] = np_
        xc = tick(False, 0.35).move_to(cfg)
        self.beat("A Pod address in a settings file is the waiter's direct number. What we want is the restaurant's own number.",
                  Create(xc), run_time=1.2)
        self.play(FadeOut(VGroup(cfg, xc)), run_time=0.5)

        # ---------- 2. ANALOGY + MAP: the host stand and the clipboard
        svc_r = RoundedRectangle(corner_radius=0.12, width=4.4, height=1.1, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.14), 1).move_to([0, 2.75, 0])
        svc_t = VGroup(T("Service: hello-devops", 26), M("10.96.171.215 : 80", 24, GOLD_M)).arrange(DOWN, buff=0.1).move_to(svc_r)
        svc = VGroup(svc_r, svc_t)
        self.beat("Guests at a busy restaurant never hunt for one waiter. They go to the host stand at the door, and the host sends them to a waiter who is on duty and free.",
                  Create(svc_r), run_time=1.6)
        self.beat("In Kubernetes, the host stand is a Service. It gives a changing group of Pods one fixed address, and one name. Here, hello-devops, on port 80.",
                  Write(svc_t), run_time=1.8)
        self.beat("That fixed address is called the ClusterIP. It stays put while Pods come and go.",
                  Indicate(svc_t[1], color=GOLD_M), run_time=1.4)
        sel = chip("selector: app: hello-devops", GOLD_M, 22, mono=True).move_to([0, 1.65, 0])
        self.steps("How does the Service know which waiters are its own? Not by name, since names change. By a label, a key and value tag on each Pod. Take every ready Pod labeled app: hello-devops.",
                   (0.8, FadeIn(sel, shift=DOWN * 0.1)), (2.4, Wait(2.4)),
                   (1.0, *[t.animate.set_color(GOLD_M) for t in tags]))
        CL, CR, CT, CB = 2.0, 6.45, 1.0, -1.35
        crect = RoundedRectangle(corner_radius=0.12, width=CR - CL, height=CT - CB, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.08), 1).move_to([(CL + CR) / 2, (CT + CB) / 2, 0])
        chead = T("EndpointSlice", 26, GREEN_M).move_to([CL + 0.25, CT - 0.3, 0], aligned_edge=LEFT)

        def entry(text, i, color=WHITE):
            return M(text, 22, color).move_to([CL + 0.3, CT - 0.78 - 0.4 * i, 0], aligned_edge=LEFT)

        ents = [entry(f"{ip}:8000 ready", i) for i, ip in enumerate(IPS)]
        self.play(sel.animate.move_to([-3.3, 1.65, 0]), run_time=0.6)
        self.beat("Now the host's clipboard. A controller watches the Pods and keeps a list, called an EndpointSlice: the address and port of every matching Pod, and whether it is ready.",
                  Create(crect), FadeIn(chead), LaggedStart(*[FadeIn(e, shift=RIGHT * 0.1) for e in ents], lag_ratio=0.3), run_time=2.6)
        self.beat("Notice the port. Visitors call the Service on port 80. The app inside each Pod listens on port 8000.",
                  Indicate(svc_t[1], color=GOLD_M), *[Indicate(e, color=GREEN_M) for e in ents], run_time=1.6)
        RL, RR = -6.45, -1.0
        rrect = RoundedRectangle(corner_radius=0.12, width=RR - RL, height=1.45, stroke_color=PURPLE_M, stroke_width=3).set_fill(tint(PURPLE_M, 0.08), 1).move_to([(RL + RR) / 2, 0.25, 0])
        rtxt = VGroup(T("kube-proxy rules, on every node", 24, PURPLE_M), M("10.96.171.215:80", 22, GOLD_M), T("goes to one ready Pod, port 8000", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        rtxt.move_to(rrect).align_to(rrect, LEFT).shift(RIGHT * 0.2)
        self.beat("And on every node, a program called kube-proxy reads both, and writes traffic rules into Linux, the operating system on the node. Traffic for the ClusterIP goes to one ready Pod.",
                  FadeOut(sel), Create(rrect), FadeIn(rtxt), run_time=2.6)

        # ---------- 3. PREDICT + BREAK: where is the host?
        q = T("you ping 10.96.171.215. what answers?", 28, YELLOW_M).move_to([0, -3.2, 0])
        self.beat("So where does the host stand, exactly? Here is a test. You ping the ClusterIP, the command that checks whether an address answers. What answers you?",
                  FadeIn(q, shift=UP * 0.1), run_time=1.6)
        self.pause_guess([-4.6, 2.75, 0])
        nob = T("nothing: the address lives on no network card", 28, RED_M).move_to(q)
        self.beat("Nothing. The ClusterIP lives on no network card. It exists only as those rules. Here our picture bends: there is no host standing anywhere. Just very good signs, painted at every door.",
                  Transform(q, nob), Indicate(rrect, color=PURPLE_M), run_time=2.4)
        self.play(FadeOut(q), run_time=0.4)

        # follow one call
        cli = chip("a calling Pod", TEAL_M, 24).move_to([-4.6, 2.75, 0])
        self.beat("Now follow one call. A Pod sends a request to the Service's address, port 80.",
                  FadeIn(cli, shift=RIGHT * 0.15), run_time=1.2)
        self.steps("The rules on the caller's own node catch it, and pick one ready Pod from the clipboard. The packet goes to that Pod, on port 8000.",
                   (0.9, travel(Line(cli.get_right(), svc_r.get_left()), TEAL_M, 0.9)),
                   (0.9, travel(Line(svc_r.get_left() + DOWN * 0.3, rrect.get_top() + RIGHT * 1.5), TEAL_M, 0.9), Indicate(rtxt[1], color=GOLD_M)),
                   (0.6, Indicate(ents[1], color=GREEN_M)),
                   (0.9, travel(Line(rrect.get_bottom() + RIGHT * 1.0, pods[1].get_top()), TEAL_M, 0.9)),
                   (0.6, Indicate(pods[1][1], color=BLUE_M)))

        # ---------- 4. SHOW: the clipboard follows the floor
        self.beat("Only ready Pods get visitors. Say this Pod starts failing its readiness check. It keeps running, but the controller marks its entry not ready, and the rules skip it.",
                  pods[0].animate.set_opacity(0.35), Transform(ents[0], entry(f"{IPS[0]}:8000 not ready", 0, RED_M)), run_time=2.4)
        self.play(pods[0].animate.set_opacity(1), Transform(ents[0], entry(f"{IPS[0]}:8000 ready", 0)), run_time=0.8)
        more = [podbox("new Pod", PXS[3]), podbox("new Pod", PXS[4])]
        mtags = [tag("app: hello-devops", x, GOLD_M) for x in PXS[3:]]
        plus = entry("+ 2 more", 3, GREEN_M)
        self.beat("Scale to five, and two new Pods appear. As soon as they are ready, the controller adds them to the clipboard. kubectl shows the first three addresses, and counts the rest. Plus two more.",
                  LaggedStart(*[FadeIn(VGroup(p, t), shift=UP * 0.15) for p, t in zip(more, mtags)], lag_ratio=0.3),
                  Succession(Wait(1.4), FadeIn(plus, shift=RIGHT * 0.1)), run_time=2.8)
        self.beat("The floor changed, twice. The Service's name and address did not change at all.",
                  Indicate(svc_t, color=GOLD_M), run_time=1.4)

        # ---------- 5. BREAK: a one letter typo
        self.play(*[FadeOut(VGroup(p, t)) for p, t in zip(more, mtags)], FadeOut(plus), run_time=0.6)
        bad = chip("selector: app: hello-devop", RED_M, 22, mono=True).move_to([0, 1.65, 0])
        self.beat("Now break it on purpose, the way the lab does. Change the selector to hello-devop. One letter missing.",
                  FadeIn(bad, shift=DOWN * 0.1), *[t.animate.set_color(GREY_B) for t in tags], run_time=1.6)
        empty = entry("(no endpoints)", 0, RED_M)
        self.beat("No Pod carries that label, so the clipboard is empty. The Service still exists, and kubectl get svc looks perfectly fine. It just leads nowhere.",
                  *[FadeOut(e) for e in ents], FadeIn(empty), run_time=2.0)
        self.steps("A call arrives, and there is nobody to send it to. Well. That is a very polite host stand, with nobody behind it.",
                   (0.9, travel(Line(cli.get_right(), svc_r.get_left()), TEAL_M, 0.9)), (0.6, Indicate(empty, color=RED_M)))
        rule = T("When a Service fails, read its EndpointSlice before you blame the network.", 26, YELLOW_M).move_to([0, -3.2, 0])
        self.beat("So here is the rule. When a Service fails, read its EndpointSlice before you blame the network.",
                  FadeIn(rule, shift=UP * 0.1), run_time=1.6)
        two = VGroup(T("no addresses: a selector or readiness problem", 24, GREY_B), T("addresses that refuse: a port problem", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        two.move_to([-3.75, -0.55, 0])
        self.beat("No addresses there means a selector or a readiness problem. Addresses that refuse connections mean a port problem. Either way, it is rarely the network itself.",
                  FadeOut(VGroup(rrect, rtxt)), FadeIn(two, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(bad, empty, two, rule)), *[t.animate.set_color(GOLD_M) for t in tags],
                  LaggedStart(*[FadeIn(e) for e in ents], lag_ratio=0.2), run_time=0.9)

        # ---------- 6. NAME: the name in the phone book
        dns = M("hello-devops.hello.svc.cluster.local", 26, GOLD_M).move_to([-1.9, 0.6, 0])
        self.beat("The Service also has a name in the cluster's phone book, CoreDNS. Its full name is the Service, then the namespace, hello, then the cluster's ending.",
                  FadeIn(dns, shift=UP * 0.1), run_time=2.0)
        short = VGroup(T("same namespace:", 24, GREY_B), M("http://hello-devops", 24)).arrange(RIGHT, buff=0.2)
        other = VGroup(T("another namespace:", 24, GREY_B), M("http://hello-devops.hello", 24)).arrange(RIGHT, buff=0.2)
        sh = VGroup(short, other).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([-2.4, -0.45, 0])
        self.beat("From the same namespace, the short name is enough. From another namespace, add the namespace.",
                  FadeIn(short, shift=UP * 0.1), Succession(Wait(1.6), FadeIn(other, shift=UP * 0.1)), run_time=2.8)

        # ---------- 7. GUARDRAIL: per connection, not per request
        self.play(FadeOut(VGroup(dns, sh)), run_time=0.5)
        conn = Line(cli.get_bottom(), pods[2].get_top(), color=TEAL_M, stroke_width=3)
        self.beat("One limit to keep in mind. The pick happens per connection, not per request. The kernel picks a Pod on a connection's first packet, and keeps it until the connection closes.",
                  Create(conn), run_time=2.0)
        self.steps("So a client that keeps one connection open, like HTTP keep-alive or gRPC, can talk to the same Pod for a long time. A curl loop opens a new connection each time, so it spreads.",
                   (2.4, LaggedStart(*[travel(conn, TEAL_M, 0.7) for _ in range(5)], lag_ratio=0.5)), (1.4, Wait(1.4)),
                   (1.6, FadeOut(conn), LaggedStart(*[travel(Line(cli.get_bottom(), p.get_top()), TEAL_M, 0.7) for p in (pods[0], pods[2], pods[1])], lag_ratio=0.6)))

        # ---------- 8. MORAL + quick check
        stage = VGroup(svc, crect, chead, *ents, *pods, *tags, cli)
        self.play(FadeOut(stage), run_time=0.8)
        moral = VGroup(T("Pods change their numbers", 30, BLUE_M), T("the Service keeps one name and one address", 30, GOLD_M),
                       T("the clipboard says who is ready right now", 30, GREEN_M)).arrange(DOWN, buff=0.3).move_to([0, 1.7, 0])
        self.steps("The moral of the story. Pods change their numbers all the time. The Service keeps one name and one address. And its clipboard, the EndpointSlice, says who is ready right now.",
                   (0.8, FadeIn(moral[0], shift=UP * 0.1)), (0.9, Wait(0.9)), (0.8, FadeIn(moral[1], shift=UP * 0.1)), (0.9, Wait(0.9)), (0.8, FadeIn(moral[2], shift=UP * 0.1)))
        ck = VGroup(T("Quick check: curl gets no answer, and the EndpointSlice", 28, YELLOW_M),
                    T("lists no addresses. Is the network broken?", 28, YELLOW_M)).arrange(DOWN, buff=0.15).move_to([0, -0.7, 0])
        self.beat("One quick check. curl gets no answer, and the EndpointSlice lists no addresses at all. Is the network broken?",
                  FadeIn(ck, shift=UP * 0.1), run_time=1.6)
        self.pause_guess([0, -2.0, 0])
        ans = T("Almost never. Check the selector against the Pod labels, and readiness.", 26).move_to([0, -2.3, 0])
        self.beat("Almost never. An empty list means no ready Pod matches. Check the selector against the Pod labels, and check readiness.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.2)
