import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\blinkerd2-proxy\b", "linkerd two proxy"), (r"\beBPF\b", "e B P F"), (r"\bIPsec\b", "I P sec"),
            (r"\bcilium-envoy\b", "cilium envoy"), (r"\bResilience4j\b", "resilience four J"), (r"\bNetworkPolicy\b", "network policy"),
            (r"\bNetworkPolicies\b", "network policies"), (r"\bztunnel\b", "Z tunnel"), (r"\b0\.6 ms\b", "0.6 milliseconds"),
            (r"\b64 MB\b", "64 megabytes"), (r"\b1536 MB\b", "1536 megabytes")])

NX, NY, NW, NH = 3.45, 0.55, 6.3, 4.3
COLS = (-1.95, -0.65, 0.65, 1.95)
ROWS = (1.85, 0.95, 0.05)
STRIP = -0.95


def tint(c, k=0.15):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def podc(c=TEAL_M):
    return Circle(radius=0.24, stroke_color=c, stroke_width=2.5).set_fill(tint(c, 0.3), 1)


def side(c=GOLD_M):
    return Square(0.24, stroke_color=c, stroke_width=2).set_fill(tint(c, 0.45), 1)


class D60ChooseMesh(VoiceScene):
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

    def head(self, text, color=WHITE):
        return T(text, 30, color).move_to([0, 3.3, 0])

    def construct(self):
        self.title_card("Linkerd, Cilium, or no mesh", "where the proxy runs, and what it costs you")

        # ---------- 1. the made-up product
        nodes, pods = VGroup(), VGroup()
        for sx in (-1, 1):
            n = RoundedRectangle(corner_radius=0.2, width=NW, height=NH, stroke_color=GREY_B, stroke_width=2).move_to([sx * NX, NY, 0])
            nodes.add(n)
            for y in ROWS:
                for x in COLS:
                    pods.add(podc().move_to([sx * NX + x, y, 0]))
        nlab = VGroup(*[M(f"node {i + 1}", 20, GREY_B).next_to(n, DOWN, buff=0.12).align_to(n, LEFT) for i, n in enumerate(nodes)])
        h = self.head("a made-up product: 8 services, 3 Pods each")
        self.beat("Take a made-up product. Eight services, three Pods each. That is twenty four Pods on two nodes.",
                  FadeIn(h), Create(nodes), FadeIn(nlab), LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.03), run_time=3.0)
        self.beat("Every mesh adds proxies to the path of each call. The real question is where those proxies run, and what they cost.",
                  Indicate(pods[3], color=YELLOW_M), Indicate(pods[12], color=YELLOW_M), run_time=1.8)

        # ---------- 2. Linkerd: a sidecar in every Pod
        sides = VGroup(*[side().move_to(p.get_center() + RIGHT * 0.42) for p in pods])
        h2 = self.head("Linkerd: a small proxy in every Pod", GOLD_M)
        self.beat("Linkerd puts a sidecar in every Pod. Its proxy is linkerd2-proxy, a micro-proxy written in Rust. Linkerd does not use Envoy.",
                  Transform(h, h2), LaggedStart(*[GrowFromCenter(s) for s in sides], lag_ratio=0.03), run_time=3.0)
        a, b = pods[3], pods[12]
        sa, sb = sides[3], sides[12]
        path = VMobject(stroke_width=0).set_points_as_corners([a.get_center(), sa.get_center(), sa.get_center() + UP * 0.45,
                                                              sb.get_center() + UP * 0.45, sb.get_center(), b.get_center()])
        call = Dot(radius=0.08, color=YELLOW_M).move_to(a)
        hop = VGroup(T("2 proxies on every call", 22, YELLOW_M)).move_to([0, -2.35, 0])
        self.steps("A call from one Pod to another leaves through its own proxy, and arrives through the other Pod's proxy. Two proxies on every call.",
                   (0.3, FadeIn(call)), (2.4, MoveAlongPath(call, path, rate_func=smooth)), (0.3, FadeOut(call)),
                   (0.8, Indicate(sa, color=YELLOW_M), Indicate(sb, color=YELLOW_M)), (0.6, FadeIn(hop)))
        gets = VGroup(chip("mTLS for all TCP", GOLD_M, 22), chip("golden metrics", GOLD_M, 22), chip("load balancing per request", GOLD_M, 22))
        gets.arrange(RIGHT, buff=0.3).move_to([0, -3.15, 0])
        self.beat("Before you write a single policy, you get mutual TLS for all TCP traffic between meshed Pods, golden metrics for every workload, and load balancing per request.",
                  LaggedStart(*[FadeIn(g, shift=0.1 * UP) for g in gets], lag_ratio=0.6), run_time=5.0)

        # ---------- 3. Cilium: in the kernel, one Envoy per node
        self.play(FadeOut(hop), FadeOut(gets), run_time=0.4)
        h3 = self.head("Cilium: eBPF in the kernel, one Envoy per node", BLUE_M)
        ebpf, envs = VGroup(), VGroup()
        for sx in (-1, 1):
            bar = RoundedRectangle(corner_radius=0.08, width=3.6, height=0.55, stroke_color=BLUE_M, stroke_width=2.5).set_fill(tint(BLUE_M, 0.2), 1)
            bar.move_to([sx * NX - 1.1, STRIP, 0])
            ebpf.add(VGroup(bar, T("kernel: eBPF", 22, BLUE_M).move_to(bar)))
            env = box("cilium-envoy", PURPLE_M, w=2.1, h=0.55, size=20).move_to([sx * NX + 1.95, STRIP, 0])
            env[1].become(M("cilium-envoy", 20).move_to(env[1]))
            envs.add(env)
        self.beat("Cilium works the other way. It is already the network plugin, so it sits on every packet. No sidecars.",
                  Transform(h, h3), LaggedStart(*[ShrinkToCenter(s) for s in sides], lag_ratio=0.02), run_time=2.4)
        self.beat("Pod networking, Service load balancing and network policy run in the Linux kernel, as small eBPF programs. No trip through a proxy.",
                  FadeIn(ebpf, shift=0.1 * UP), run_time=1.8)
        self.beat("Anything that needs HTTP goes to Envoy. But only one Envoy per node, the cilium-envoy DaemonSet.",
                  FadeIn(envs, shift=0.1 * UP), run_time=1.6)
        wire = DashedLine(nodes[0].get_right() + DOWN * 1.5, nodes[1].get_left() + DOWN * 1.5, dash_length=0.08, color=GREEN_M, stroke_width=3)
        enc = T("WireGuard or IPsec between nodes", 22, GREEN_M).move_to([0, -2.35, 0])
        note = T("proves which node sent it, not which workload", 22, GREY_B).move_to([0, -2.9, 0])
        self.steps("Between nodes, Cilium can encrypt with WireGuard or IPsec. That protects the wire. But it proves which node a packet came from, not which workload sent it.",
                   (1.0, Create(wire), FadeIn(enc)), (3.4, Wait(3.4)), (0.8, FadeIn(note)))
        beta = T("workload mTLS in Cilium: still Beta, check first", 22, RED_M).move_to([0, -3.45, 0])
        self.beat("Mutual TLS between workload identities is where Cilium is still moving. Its replacement design is Beta. So if that is your main reason for a mesh, check its status first.",
                  FadeIn(beta, shift=0.1 * UP), run_time=1.6)

        # ---------- 4. what a sidecar mesh costs
        self.play(FadeOut(VGroup(wire, enc, note, beta, ebpf, envs)), run_time=0.5)
        h4 = self.head("what a sidecar per Pod costs", RED_M)
        self.beat("Now the bill. Go back to one sidecar per Pod, and measure one proxy, as the lab does.",
                  Transform(h, h4), LaggedStart(*[GrowFromCenter(s) for s in sides], lag_ratio=0.02), run_time=2.4)
        lat = VGroup(T("one Envoy hop: about +0.6 ms median", 24, WHITE), T("two hops on every call", 22, GREY_B)).arrange(DOWN, buff=0.15).move_to([-3.45, -2.75, 0])
        self.beat("In the worked example, one Envoy hop added about 0.6 ms to the median call. A sidecar mesh puts two such hops on every call.",
                  FadeIn(lat[0], shift=0.1 * UP), Succession(Wait(3.2), FadeIn(lat[1])), run_time=4.0)
        memt = M("24 Pods x 64 MB", 26, WHITE).move_to([3.45, -2.45, 0])
        self.beat("An idle Envoy held about 64 MB of memory. You pay that for every Pod.",
                  FadeIn(memt), LaggedStart(*[Indicate(s, color=RED_M, scale_factor=1.4) for s in sides], lag_ratio=0.02), run_time=2.6)
        mem = M("= 1536 MB", 30, RED_M).move_to([3.45, -3.1, 0])
        self.beat("Twenty four times sixty four. About 1.5 gigabytes of proxies, before they carry any traffic.",
                  Write(mem), run_time=1.6)
        more = VGroup(T("+ upgrades, debugging, people", 24, GREY_B)).move_to([0, -3.6, 0])
        self.play(FadeOut(VGroup(lat, memt, mem)), run_time=0.4)
        bill = VGroup(T("latency", 24), T("CPU and memory", 24), T("upgrades", 24), T("debugging", 24), T("people", 24)).arrange(RIGHT, buff=0.55).move_to([0, -2.5, 0])
        self.beat("And the bill has more lines. Upgrades of every proxy. Debugging, because a call has more places to fail. And people, who own the certificates and read the release notes.",
                  LaggedStart(*[FadeIn(x, shift=0.1 * UP) for x in bill], lag_ratio=0.5), run_time=5.0)

        # ---------- 5. or no mesh at all
        self.play(FadeOut(bill), run_time=0.4)
        h5 = self.head("or no mesh: tools you already have", GREEN_M)
        tools = VGroup(chip("NetworkPolicy: who may talk", GREEN_M, 22), chip("client library: timeouts, retries", GREEN_M, 22),
                       chip("one Gateway: TLS at the edge", GREEN_M, 22), chip("OpenTelemetry, Prometheus", GREEN_M, 22))
        tools.arrange_in_grid(2, 2, buff=(0.4, 0.3)).move_to([0, -2.85, 0])
        self.beat("For a handful of services owned by one team, I would not start with a mesh. Tools you already know cover most of the list.",
                  Transform(h, h5), LaggedStart(*[ShrinkToCenter(s) for s in sides], lag_ratio=0.02), run_time=2.4)
        self.beat("NetworkPolicy decides who may talk to whom. A shared client library sets timeouts and retries. One Gateway handles TLS at the edge. And OpenTelemetry and Prometheus give you per call metrics and traces.",
                  LaggedStart(*[FadeIn(t, shift=0.1 * UP) for t in tools], lag_ratio=0.8), run_time=8.0)
        yet = T("the answer for this product: no mesh yet", 28, GREEN_M).move_to([0, 3.3, 0])
        self.beat("For our made-up product, with one team and no auditor asking for mutual TLS, the checklist says: no mesh yet.",
                  Transform(h, yet), run_time=1.6)

        # ---------- 6. when it changes, adopt one layer at a time
        self.play(FadeOut(tools), run_time=0.4)
        h6 = self.head("if a mesh is worth it: one namespace, one layer at a time", YELLOW_M)
        self.beat("The answer changes as services and teams multiply, with many languages, or when an auditor asks for encryption and identity on every call.",
                  Transform(h, h6), run_time=2.0)
        ns = pods[0:4]
        ladder = VGroup(*[chip(t, YELLOW_M, 22) for t in ("1 observe", "2 mTLS, permissive", "3 mTLS, strict", "4 authorization", "5 traffic policies")])
        ladder.arrange(RIGHT, buff=0.22).move_to([0, -2.6, 0])
        fit(ladder, 13.2)
        frame = SurroundingRectangle(VGroup(*ns, *sides[0:4]), buff=0.18, color=YELLOW_M, stroke_width=2.5, corner_radius=0.1)
        fl = T("one namespace", 20, YELLOW_M).next_to(frame, UP, buff=0.08)
        for l in ladder:
            l.set_opacity(0.25)
        self.steps("Then go one namespace at a time. First, mesh it, and only watch the golden metrics. You will find calls nobody knew about.",
                   (1.0, Create(frame), FadeIn(fl), FadeIn(ladder)), (0.8, *[GrowFromCenter(s) for s in sides[0:4]]),
                   (0.6, ladder[0].animate.set_opacity(1)))
        self.beat("Next, mutual TLS in permissive mode, so meshed callers encrypt and everyone else still works. Then strict, once every caller is meshed.",
                  Succession(ladder[1].animate(run_time=0.6).set_opacity(1), Wait(2.8), ladder[2].animate(run_time=0.6).set_opacity(1)), run_time=4.0)
        self.beat("Then authorization policies, starting with sensitive data. And traffic policies, retries, timeouts and canaries, last.",
                  Succession(ladder[3].animate(run_time=0.6).set_opacity(1), Wait(2.0), ladder[4].animate(run_time=0.6).set_opacity(1)), run_time=3.2)

        # ---------- 7. recap
        rc = T("decide first; then switch it on one layer at a time", 28).move_to([0, -3.4, 0])
        self.beat("Decide first. And if a mesh is worth it, switch it on one layer at a time.",
                  FadeIn(rc, shift=0.1 * UP), run_time=1.6)
        self.wait(1.5)
