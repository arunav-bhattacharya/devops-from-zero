import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import fg as _fg


def box(*a, **k):  # keep the label drawn above its own filled outline, even when the outline is animated
    b = _fg.box(*a, **k); b[1].set_z_index(1); return b


def chip(*a, **k):
    c = _fg.chip(*a, **k); c[1].set_z_index(1); return c

SAY.extend([(r"\bztunnel\b", "zee tunnel"), (r"\beBPF\b", "e B P F"), (r"\bcilium-envoy\b", "cilium envoy"),
            (r"\b1\.46 ms\b", "1.46 milliseconds"), (r"\b2\.09 ms\b", "2.09 milliseconds"), (r"\b0\.6 ms\b", "0.6 milliseconds"),
            (r"\b64 MB\b", "64 megabytes"), (r"\b1536 MB\b", "1536 megabytes"), (r"\b1280 MB\b", "1280 megabytes"),
            (r"\b365\b", "three hundred and sixty five")])

POD_C = TEAL_M
PRX_C = GOLD_M
NODE_C = GREY_B
ASK_C = YELLOW_M
BILL_C = RED_M
OK_C = GREEN_M


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def pod(r=0.2):
    return Circle(radius=r, stroke_color=POD_C, stroke_width=2.5).set_fill(tint(POD_C, 0.25), 1)


def proxy(s=0.2):
    return Square(s, stroke_width=0).set_fill(PRX_C, 0.95)


class D60Bill(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("Do you need a service mesh?", "the page the brochure leaves out")

        # ---------- 1. the bakery and the brochure
        shop = VGroup(Rectangle(width=2.6, height=1.6, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.08), 1))
        shop.add(Rectangle(width=0.55, height=0.9, stroke_color=GOLD_M, stroke_width=3).move_to(shop[0].get_bottom() + UP * 0.45))
        shop.add(T("bakery", 26, GOLD_M).next_to(shop[0], UP, buff=0.15))
        shop.move_to([-4.6, -0.6, 0])
        tower = VGroup(Rectangle(width=1.9, height=4.4, stroke_color=NODE_C, stroke_width=3))
        win = VGroup(*[Square(0.22, stroke_color=NODE_C, stroke_width=1.5) for _ in range(24)]).arrange_in_grid(8, 3, buff=(0.28, 0.24)).move_to(tower[0])
        tower.add(win, T("tower", 26, NODE_C).next_to(tower[0], UP, buff=0.15))
        tower.move_to([4.8, 0.2, 0])
        self.beat("Picture a small bakery: three people in the back, and one door. A salesman comes by with a brochure.",
                  FadeIn(shop), run_time=2.0)
        bro = VGroup(*[VGroup(tick(True, 0.14), T(t, 26)).arrange(RIGHT, buff=0.2) for t in ("badge readers on every door", "a guard on every floor", "a control room that sees it all")]).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        broc = SurroundingRectangle(bro, buff=0.3, color=GREY_B, stroke_width=2, corner_radius=0.1)
        brg = VGroup(broc, bro).move_to([0.2, 0.5, 0])
        self.beat("Badge readers on every door. A guard on every floor. A control room that watches it all. The tower down the street runs on it, and its managers would never go back.",
                  FadeIn(broc), LaggedStart(*[FadeIn(b, shift=RIGHT * 0.1) for b in bro], lag_ratio=0.4), Succession(Wait(3.6), FadeIn(tower)), run_time=5.2)
        self.beat("It's a fine system. But the bakery has one door, and everyone inside knows everyone else.",
                  Indicate(shop[1], color=GOLD_M, scale_factor=1.2), run_time=2.2)
        miss = T("missing page: the monthly bill, and who looks after it", 28, BILL_C).move_to([0, -2.8, 0])
        self.beat("What the brochure leaves out is the monthly bill, and the person who has to look after it all.",
                  FadeIn(miss, shift=UP * 0.1), run_time=2.0)
        self.beat("The last two lessons were the brochure: a receptionist at every door, badges checked in every handshake. Today, the missing page. And then the bakery's question: do we need any of this?",
                  run_time=None)
        self.play(FadeOut(VGroup(shop, tower, brg, miss)), run_time=0.6)

        # ---------- 2. the bill has five lines
        lines = ["latency: every proxy adds a hop", "CPU and memory: for every proxy", "upgrades: control plane and every proxy",
                 "debugging: more places for a call to fail", "people: someone owns certificates and release notes"]
        bill = VGroup(*[T(t, 26) for t in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        bh = T("The bill", 30, BILL_C)
        bg = VGroup(bh, bill).arrange(DOWN, buff=0.35).move_to([0, 0.2, 0])
        self.beat("The bill has five lines. Latency, because every proxy adds a hop. CPU and memory, for every proxy. Upgrades. Debugging, because a failed call now has more places to fail. And people.",
                  FadeIn(bh), LaggedStart(*[FadeIn(b, shift=RIGHT * 0.1) for b in bill], lag_ratio=0.5), run_time=8.0)
        self.beat("The first two we can measure in five minutes. So let's.",
                  Indicate(VGroup(bill[0], bill[1]), color=BILL_C, scale_factor=1.03), run_time=1.6)
        self.play(FadeOut(bg), run_time=0.5)

        # ---------- 3. measure one hop
        c1 = box("curl", NODE_C, w=1.6).move_to([-5.2, 1.6, 0])
        a1 = box("app", POD_C, w=1.6).move_to([2.2, 1.6, 0])
        c2 = box("curl", NODE_C, w=1.6).move_to([-5.2, -0.4, 0])
        e2 = box("Envoy", PRX_C, w=1.8).move_to([-1.5, -0.4, 0])
        a2 = box("app", POD_C, w=1.6).move_to([2.2, -0.4, 0])
        r1, r2a, r2b = edge_arrow(c1, a1), edge_arrow(c2, e2), edge_arrow(e2, a2)
        lab1 = T("direct", 26, GREY_B).next_to(r1, UP, buff=0.12)
        lab2 = T("one proxy hop", 26, PRX_C).next_to(c2, UP, buff=0.2).align_to(c2, LEFT)
        self.beat("Take the receptionist lab from two lessons ago. Send 300 requests straight to the app, and 300 through Envoy. Same app, same laptop.",
                  FadeIn(c1), FadeIn(a1), GrowArrow(r1), FadeIn(lab1), Succession(Wait(2.4), AnimationGroup(FadeIn(c2), FadeIn(e2), FadeIn(a2), GrowArrow(r2a), GrowArrow(r2b), FadeIn(lab2))), run_time=5.0)
        self.beat("How much does one hop add to the middle request? Pause and guess.",
                  travel(r1, POD_C, 0.8), Succession(travel(r2a, PRX_C, 0.6), travel(r2b, PRX_C, 0.6)), run_time=2.0)
        self.pause([0, -1.9, 0])
        t1 = VGroup(T("median", 24, GREY_B), M("1.46 ms", 26)).arrange(RIGHT, buff=0.2).next_to(a1, RIGHT, buff=0.4)
        t2 = VGroup(T("median", 24, GREY_B), M("2.09 ms", 26, PRX_C)).arrange(RIGHT, buff=0.2).next_to(a2, RIGHT, buff=0.4)
        self.beat("Direct, the median was 1.46 ms. Through Envoy, 2.09 ms. About 0.6 ms more.",
                  FadeIn(t1), Succession(Wait(1.8), FadeIn(t2)), run_time=3.4)
        mem = VGroup(T("one idle Envoy holds about", 26), M("64 MB", 28, PRX_C), T("of memory", 26)).arrange(RIGHT, buff=0.2).move_to([0, -1.9, 0])
        self.beat("Tiny, right? And the idle Envoy, with its tiny config, holds about 64 MB of memory. These are one laptop's numbers. Yours will differ, which is exactly why you measure your own.",
                  FadeIn(mem, shift=UP * 0.1), run_time=3.0)
        two = T("a sidecar mesh puts two hops on every call", 26, BILL_C).move_to([0, -2.75, 0])
        self.beat("One more thing. A sidecar mesh puts a proxy at both ends, so every call crosses two of them.",
                  FadeIn(two), run_time=2.2)
        self.play(FadeOut(VGroup(c1, a1, c2, e2, a2, r1, r2a, r2b, lab1, lab2, t1, t2, two)), mem.animate.move_to([0, 3.0, 0]), run_time=0.7)

        # ---------- 4. multiply
        pods = VGroup(*[pod() for _ in range(24)]).arrange_in_grid(3, 8, buff=(0.7, 0.55)).move_to([0, 0.6, 0])
        svc = VGroup(*[T(f"s{i + 1}", 22, GREY_B).next_to(pods[i], UP, buff=0.2) for i in range(8)])
        self.beat("Now a made-up payments product. Eight services, three Pods each. Twenty-four Pods.",
                  LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.03), FadeIn(svc), run_time=3.0)
        sides = VGroup(*[proxy().move_to(p.get_center() + RIGHT * 0.33) for p in pods])
        tot = ValueTracker(0)
        tl = always_redraw(lambda: VGroup(T("sidecars:", 26, GREY_B), M(f"{int(round(tot.get_value()))} MB", 28, PRX_C)).arrange(RIGHT, buff=0.25).move_to([0, -1.55, 0]))
        self.add(tl)
        self.beat("Give every Pod a sidecar at 64 MB each. Before a single request is carried, the proxies need 1536 MB, about one and a half gigabytes.",
                  LaggedStart(*[FadeIn(s, scale=1.5) for s in sides], lag_ratio=0.05), tot.animate.set_value(1536), run_time=5.0)
        tl2 = tl.copy().clear_updaters(); self.remove(tl); self.add(tl2)
        self.beat("The bakery would be paying a guard per loaf.",
                  Indicate(tl2[1], color=PRX_C), run_time=1.6)

        # ---------- 5. break: sidecar-free does not mean proxy-free
        nodes = VGroup(*[RoundedRectangle(corner_radius=0.12, width=4.0, height=2.6, stroke_color=NODE_C, stroke_width=2) for _ in range(3)]).arrange(RIGHT, buff=0.3).move_to([0, 0.35, 0])
        nl = VGroup(*[T(f"node {i + 1}", 24, NODE_C).next_to(n, UP, buff=0.1) for i, n in enumerate(nodes)])
        tgt = []
        for k in range(3):
            g = VGroup(*[pod() for _ in range(8)]).arrange_in_grid(2, 4, buff=(0.45, 0.4)).move_to(nodes[k].get_center() + DOWN * 0.2)
            tgt.extend(list(g))
        self.beat("Other meshes share proxies instead. Let's put our twenty-four Pods on three nodes, the machines they run on.",
                  FadeOut(svc), FadeOut(sides), FadeOut(tl2), Create(nodes), FadeIn(nl), *[pods[i].animate.move_to(tgt[i].get_center()) for i in range(24)], run_time=3.0)
        gq = VGroup(T("Cilium is called sidecar-free.", 28), T("Where does an HTTP retry run?", 28, ASK_C)).arrange(DOWN, buff=0.15).move_to([0, -2.4, 0])
        self.beat("Cilium, a network plugin with a mesh built in, is often called sidecar-free. So where does an HTTP retry actually run? Pause and guess.",
                  FadeIn(gq), run_time=2.6)
        self.pause([0, -3.25, 0])
        kern = T("in the kernel?", 26, GREY_B).move_to([-4.6, -1.65, 0])
        self.beat("The tempting answer: in eBPF, the small programs Cilium runs inside the Linux kernel. Let's be fair. eBPF really does move packets and balance connections there.",
                  FadeIn(kern), run_time=3.0)
        np_ = VGroup(*[VGroup(Square(0.42, stroke_width=0).set_fill(PRX_C, 0.95), T("Envoy", 20, PRX_C)).arrange(RIGHT, buff=0.1).move_to(n.get_corner(UR) + LEFT * 0.7 + DOWN * 0.38) for n in nodes])
        self.beat("But it doesn't read HTTP. Anything that needs HTTP runs in an Envoy, one per node. Sidecar-free doesn't mean proxy-free.",
                  FadeOut(kern), LaggedStart(*[FadeIn(p, scale=1.4) for p in np_], lag_ratio=0.3), run_time=3.4)
        amb = T("Istio ambient: one ztunnel per node, and a waypoint only where you need HTTP", 24, GREY_B).move_to([0, -1.65, 0])
        fit(amb, 12.6)
        self.beat("Istio's ambient mode is built the same way: one small proxy per node, ztunnel, and an Envoy waypoint only where you ask for HTTP features. Three node proxies instead of twenty-four sidecars.",
                  FadeOut(gq), FadeIn(amb), run_time=3.2)
        self.beat("The price of sharing: a noisy neighbor can slow your traffic, and a broken node proxy hurts every Pod on that node.",
                  Indicate(nodes[1], color=BILL_C), run_time=2.4)
        self.play(FadeOut(VGroup(nodes, nl, pods, np_, amb, mem)), run_time=0.6)

        # ---------- 6. the decision
        chk = ["fewer than about ten services, one or two teams", "one or two languages: a shared library can retry",
               "NetworkPolicies already limit who talks to whom", "one Gateway handles TLS and routing from outside",
               "OpenTelemetry and Prometheus already show errors and latency", "no auditor asks for encryption on every internal call"]
        rows = VGroup(*[VGroup(Square(0.3, stroke_color=GREY_B, stroke_width=2), T(t, 24)).arrange(RIGHT, buff=0.25) for t in chk]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.move_to([0, 0.35, 0])
        ch = T("The lab's checklist, for our payments product", 28, ASK_C).move_to([0, 3.0, 0])
        self.beat("Now the bakery's question, for our made-up product. The lab has a checklist. One team, two languages, NetworkPolicies, one Gateway, OpenTelemetry already, and no auditor asking for encryption on every internal call.",
                  FadeIn(ch), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.2), run_time=6.0)
        ticks = [tick(True, 0.14).move_to(r[0]) for r in rows]
        verdict = T("No mesh yet. Look again when a second team or an auditor arrives.", 28, OK_C).move_to([0, -2.3, 0])
        fit(verdict, 12.6)
        self.beat("Every box is ticked. So the answer is: no mesh yet. Write a note to look again when a second team, or a compliance rule, arrives.",
                  LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15), Succession(Wait(2.0), FadeIn(verdict)), run_time=4.0)
        self.beat("And remember what a mesh can't do. It won't speed up a slow database query. It only wraps proxies around the slow call.",
                  run_time=None)
        self.play(FadeOut(VGroup(ch, rows, *ticks, verdict)), run_time=0.6)

        # ---------- 7. guardrails: adopt in steps, and the date
        steps = ["observe", "mTLS, permissive", "mTLS, strict", "authorization", "traffic rules"]
        st = VGroup()
        for i, s in enumerate(steps):
            b = box(s, BLUE_M, w=3.0, h=0.62, size=24).move_to([-4.6 + i * 2.3, -2.2 + i * 0.85, 0])
            st.add(b)
        sh = T("If you do adopt one: one namespace at a time", 28, ASK_C).move_to([0, 3.0, 0])
        self.beat("If the answer is yes, adopt it one namespace at a time, one step at a time. First only observe. You'll find calls nobody knew about.",
                  FadeIn(sh), FadeIn(st[0], shift=UP * 0.1), run_time=3.0)
        self.beat("Then mutual TLS in permissive mode. Then strict, once every caller is meshed. Then authorization. Traffic rules come last.",
                  LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in st[1:]], lag_ratio=0.5), run_time=5.0)
        self.play(FadeOut(VGroup(sh, st)), run_time=0.5)
        cal = VGroup(RoundedRectangle(corner_radius=0.1, width=2.6, height=2.2, stroke_color=BILL_C, stroke_width=3),
                     M("365", 44, BILL_C), T("days", 26, BILL_C))
        VGroup(cal[1], cal[2]).arrange(DOWN, buff=0.1).move_to(cal[0])
        cal.move_to([-3.8, 0.4, 0])
        ln = VGroup(T("Linkerd's default trust anchor,", 26), T("the mesh's root certificate,", 26), T("expires after a year.", 26, BILL_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([2.2, 0.4, 0])
        self.beat("One last line of the bill hides in the easy path. Linkerd, a lighter mesh, creates a root certificate when you install it, the trust anchor. It expires after 365 days.",
                  FadeIn(cal), FadeIn(ln), run_time=3.4)
        r2 = T("A certificate you did not choose still expires. Write down the date.", 28, ASK_C).move_to([0, -2.0, 0])
        fit(r2, 12.6)
        self.beat("A team that takes the defaults and never looks again has a mesh that breaks a year later. A certificate you didn't choose still expires. Write down the date.",
                  FadeIn(r2, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(cal, ln, r2)), run_time=0.5)

        # ---------- 8. moral, check
        mor = VGroup(T("Write down the problems you expect it to solve.", 30), T("Measure before and after. Remove it if nothing moves.", 30, ASK_C)).arrange(DOWN, buff=0.25).move_to([0, 1.9, 0])
        self.beat("So the moral of the story. A mesh is a fine system with a real bill. Before you buy it, write down the two or three problems you expect it to solve. Measure them before and after, and take the mesh out again if the numbers don't move.",
                  Write(mor[0]), Succession(Wait(4.0), FadeIn(mor[1])), run_time=7.0)
        cq = VGroup(T("Quick check: 10 services, 2 Pods each, a 64 MB sidecar per Pod.", 26), T("How much memory before any traffic?", 26, ASK_C)).arrange(DOWN, buff=0.15).move_to([0, -0.5, 0])
        self.beat("A quick check. Ten services, two Pods each, a 64 MB sidecar in every Pod. How much memory before any traffic? Pause and work it out.",
                  FadeIn(cq), run_time=2.4)
        self.pause([0, -1.6, 0], text="pause and work it out")
        ans = T("20 Pods x 64 MB = 1280 MB, and two hops on every call", 28, PRX_C).move_to([0, -2.2, 0])
        self.beat("Twenty Pods times 64 MB: 1280 MB. And still two hops on every call.",
                  FadeIn(ans, shift=UP * 0.1), run_time=2.0)
        self.beat("Next, we leave the open-source parts behind, and meet one commercial product that collects every signal at once. What do you gain when one tool sees everything, and what do you give up?",
                  FadeOut(VGroup(cq, ans)), mor.animate.set_opacity(0.4), run_time=2.0)
        self.wait(1.0)
