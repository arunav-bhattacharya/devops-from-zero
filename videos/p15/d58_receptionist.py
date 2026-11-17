import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bv1a\b", "v one A"), (r"\bv1b\b", "v one B"), (r"\bv2\b", "v two"), (r"\bredis-b\b", "redis B"),
            (r"\b/healthz\b", "health Z"), (r"\b5xx\b", "five hundreds"), (r"\b10000\b", "ten thousand")])

OFF_C = GREY_B      # offices / services
PRX_C = GOLD_M      # Envoy, the receptionist
OK_C = GREEN_M
BAD_C = RED_M
REQ_C = BLUE_M      # requests
ASK_C = YELLOW_M
V2_C = PURPLE_M     # the canary


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def person(c=REQ_C):
    return Dot(radius=0.09, color=c)


class D58Receptionist(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("A receptionist at every door", "how a proxy makes calls between services behave")

        # ---------- 1. the office building
        offs = VGroup()
        names = ["sales", "orders", "payroll", "support", "legal", "stock", "design", "travel"]
        for i, n in enumerate(names):
            r = RoundedRectangle(corner_radius=0.1, width=2.4, height=1.2, stroke_color=OFF_C, stroke_width=2).set_fill(tint(OFF_C, 0.06), 1)
            offs.add(VGroup(r, T(n, 26, OFF_C).move_to(r)))
        offs.arrange_in_grid(rows=2, cols=4, buff=(0.9, 1.5)).move_to(UP * 0.2)
        self.beat("Picture an office building. Small offices, one team in each. All day, people walk the corridors with requests for each other.",
                  LaggedStart(*[FadeIn(o) for o in offs], lag_ratio=0.1), run_time=3.0)
        walk = []
        for a, b in [(0, 2), (5, 2), (3, 6), (7, 1), (4, 2), (1, 5)]:
            d = person().move_to(offs[a].get_center())
            walk.append(Succession(FadeIn(d, run_time=0.1), d.animate(run_time=1.2).move_to(offs[b].get_center()), FadeOut(d, run_time=0.1)))
        self.beat("Each team has its own habits. One knocks five times, then knocks again. Another gives up after one second. Nobody checks who is at the door.",
                  LaggedStart(*walk, lag_ratio=0.25), run_time=4.0)
        pay = offs[2]
        q = VGroup(*[person() for _ in range(6)]).arrange(LEFT, buff=0.12).next_to(pay, DOWN, buff=0.25)
        self.beat("One afternoon, payroll slows down. A queue forms outside its door.",
                  pay[0].animate.set_stroke(BAD_C, width=3), LaggedStart(*[FadeIn(p) for p in q], lag_ratio=0.25), run_time=2.6)
        jam = VGroup(*[VGroup(*[person() for _ in range(3)]).arrange(LEFT, buff=0.1).next_to(offs[k], DOWN, buff=0.25) for k in (1, 5, 6, 3)])
        self.beat("The people stuck there are late for everyone waiting on them. Soon those queues grow too. By four o'clock, half the building is standing in corridors.",
                  LaggedStart(*[FadeIn(j) for j in jam], lag_ratio=0.4), run_time=4.0)
        self.beat("No team did anything foolish. Each habit made sense from inside one office. The trouble lives between the offices, where nobody is in charge.",
                  run_time=None)
        self.play(FadeOut(VGroup(offs, q, jam)), run_time=0.6)

        # ---------- 2. the list every call needs
        chk = ["how long to wait: a timeout", "whether to try again: retries", "who is calling: encryption and ID",
               "send 10% to a new version", "count failures and slowness"]
        rows = VGroup(*[T(t, 28) for t in chk]).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([-1.3, 0.1, 0])
        hdr = T("Every call between services needs:", 30, ASK_C).move_to(UP * 2.8)
        self.beat("Services, separate programs that call each other over the network, have exactly this building. Before one call is safe, somebody has to decide all of this.",
                  FadeIn(hdr), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in rows], lag_ratio=0.3), run_time=5.0)
        habits = VGroup(T("team A: retry 5 times, wait 30 s", 24, BAD_C), T("team B: never retry, wait 1 s", 24, BAD_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([3.9, -2.6, 0])
        self.beat("None of it is the work the service exists to do. And left alone, every team solves it a little differently. Those are the office habits, and they surface during an outage, when they are hardest to untangle.",
                  FadeIn(habits, shift=UP * 0.1), run_time=3.0)
        wish = T("Wouldn't it be nice if the door handled it, the same way for everyone?", 28, ASK_C).move_to(DOWN * 2.6)
        self.play(FadeOut(habits), run_time=0.4)
        self.beat("Wouldn't it be nice if the door itself handled it, the same way for everyone?",
                  FadeIn(wish, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(rows, hdr, wish)), run_time=0.6)

        # ---------- 3. the receptionist = a proxy
        app = box("app", OFF_C, w=1.8).move_to([-5.0, 0.4, 0])
        rec = box("receptionist", PRX_C, w=2.8).move_to([-1.0, 0.4, 0])
        svc = box("other service", OFF_C, w=2.8).move_to([4.0, 0.4, 0])
        aa, ab = edge_arrow(app, rec), edge_arrow(rec, svc)
        self.beat("So put a receptionist at the door. The app makes a plain call. The receptionist makes the real call on its behalf.",
                  FadeIn(app), GrowArrow(aa), FadeIn(rec), Succession(Wait(2.6), AnimationGroup(GrowArrow(ab), FadeIn(svc))), run_time=4.0)
        jobs = VGroup(*[chip(t, PRX_C, 24) for t in ("time limit", "try again", "check badge", "count")]).arrange(RIGHT, buff=0.25).move_to([-0.2, -1.1, 0])
        self.beat("The receptionist adds the time limit, the second try, the badge check and the counting. One set of habits, for every office.",
                  LaggedStart(*[FadeIn(j, shift=UP * 0.1) for j in jobs], lag_ratio=0.3), travel(aa, REQ_C, 0.8), Succession(Wait(0.8), travel(ab, REQ_C, 0.8)), run_time=4.0)
        nm = VGroup(T("receptionist", 26, PRX_C), T("=  a proxy", 26)).arrange(RIGHT, buff=0.25).move_to([-1.0, 2.2, 0])
        self.beat("A program that does this is called a proxy. The one we'll use is Envoy. And a proxy that lives right next to the app, in the same Pod, is called a sidecar.",
                  FadeIn(nm), Transform(rec[1], T("Envoy", 28).move_to(rec[1])), run_time=3.0)
        self.beat("Here's the nice part: the app doesn't change at all. Packet rules inside the Pod quietly hand every connection to the proxy first. The app keeps calling the same address and never notices.",
                  Indicate(app[1], color=OFF_C), travel(aa, REQ_C, 1.0), run_time=3.0)
        self.play(FadeOut(VGroup(app, aa, ab, svc, jobs, nm)), rec.animate.move_to([-2.0, 0, 0]), run_time=0.8)

        # ---------- 4. the lab: three copies, 90/10
        curl = box("curl", OFF_C, w=1.6).move_to([-5.6, 0, 0])
        rec_l = M(":10000", 22, PRX_C).next_to(rec, DOWN, buff=0.15)
        h = {}
        h["v1a"] = box("v1a", OK_C, w=1.6).move_to([2.6, 1.7, 0])
        h["v1b"] = box("v1b", OK_C, w=1.6).move_to([2.6, 0.3, 0])
        h["v2"] = box("v2", V2_C, w=1.6).move_to([2.6, -1.9, 0])
        g1 = SurroundingRectangle(VGroup(h["v1a"], h["v1b"]), buff=0.2, color=GREY_D, stroke_width=2, corner_radius=0.1)
        g2 = SurroundingRectangle(h["v2"], buff=0.2, color=GREY_D, stroke_width=2, corner_radius=0.1)
        gl1 = M("hello_v1", 22, GREY_B).next_to(g1, RIGHT, buff=0.2)
        gl2 = M("hello_v2", 22, GREY_B).next_to(g2, RIGHT, buff=0.2)
        a0 = edge_arrow(curl, rec)
        a1 = Arrow(rec.get_right(), g1.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        a2 = Arrow(rec.get_right(), g2.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        w1 = T("90", 26, OK_C).move_to(a1.point_from_proportion(0.5) + UP * 0.3)
        w2 = T("10", 26, V2_C).move_to(a2.point_from_proportion(0.5) + DOWN * 0.3 + LEFT * 0.1)
        self.beat("Let's build the smallest version. Our lab app, hello-devops, a tiny web app that greets every visitor, runs as three copies. v1a and v1b are version one.",
                  FadeIn(curl), GrowArrow(a0), FadeIn(rec_l), FadeIn(h["v1a"]), FadeIn(h["v1b"]), Create(g1), FadeIn(gl1), run_time=4.0)
        self.beat("v2 is a canary, a new version that gets a small share of traffic first.",
                  FadeIn(h["v2"]), Create(g2), FadeIn(gl2), run_time=2.0)
        self.beat("Envoy's route sends 90 out of every 100 requests to version one, and 10 to the canary.",
                  GrowArrow(a1), GrowArrow(a2), FadeIn(w1), FadeIn(w2), run_time=2.4)
        pq = T("200 requests: how many reach v2?", 28, ASK_C).move_to([-2.6, -2.6, 0])
        self.beat("We send 200 requests. How many land on the canary? Pause and guess.",
                  FadeIn(pq), run_time=1.8)
        self.pause([-2.6, -3.25, 0])
        dots = []
        for k in range(10):
            tgt = h["v2"] if k == 6 else (h["v1a"] if k % 2 else h["v1b"])
            ln = Line(rec.get_right(), tgt.get_left())
            dots.append(travel(ln, V2_C if k == 6 else REQ_C, 0.6))
        res = VGroup(T("v1:", 26, OK_C), M("175", 26), T("v2:", 26, V2_C), M("25", 26)).arrange(RIGHT, buff=0.25).move_to([-2.6, -2.6, 0])
        self.beat("About twenty, if it split perfectly. The lab got 175 and 25. Envoy picks at random for each request, so the numbers wander a little around 90 and 10.",
                  LaggedStart(*dots, lag_ratio=0.15), Succession(Wait(1.2), Transform(pq, res)), run_time=5.0)
        self.play(FadeOut(pq), run_time=0.4)

        # ---------- 5. break: v1b loses its Redis
        rb = box("redis-b", BAD_C, w=1.9, h=0.7, size=24).move_to([5.6, 0.3, 0])
        rbl = Line(h["v1b"].get_right(), rb.get_left(), stroke_width=2, color=GREY_B)
        self.beat("Now let's break one copy on purpose. v1b keeps its visit count in its own Redis, a small database. We stop it.",
                  gl1.animate.next_to(g1, UP, buff=0.12), FadeIn(rb), Create(rbl), run_time=2.4)
        x = tick(False, 0.3).move_to(rb)
        hz = VGroup(M("/healthz", 22), T("200", 24, OK_C)).arrange(RIGHT, buff=0.15).next_to(h["v1b"], DOWN, buff=0.12)
        rt = VGroup(M("/", 22), T("500", 24, BAD_C)).arrange(RIGHT, buff=0.15).next_to(hz, DOWN, buff=0.06)
        self.beat("Now real visits to v1b fail with error 500. But its health page, slash healthz, still answers 200, all fine.",
                  Create(x), rb[0].animate.set_opacity(0.4), h["v1b"][0].animate.set_stroke(BAD_C), Succession(Wait(1.6), FadeIn(rt)), Succession(Wait(3.2), FadeIn(hz)), run_time=5.0)
        hc = T("health check every 5 s", 24, PRX_C).move_to([-2.0, 1.5, 0])
        self.beat("The obvious hope: Envoy runs its own health check, every five seconds. Surely it notices. Let's be fair; that check really runs. And it keeps passing.",
                  FadeIn(hc), Succession(Wait(3.0), Indicate(hz, color=OK_C)), run_time=4.6)
        self.beat("An office with the door wide open, and a phone nobody answers. A health check only asks: is the door open?",
                  run_time=None)

        # requests hit v1b, fail, retried on v1a
        pq2 = T("20 requests: what does curl see?", 28, ASK_C).move_to([-2.6, -2.6, 0])
        self.beat("So we send twenty requests. What does curl see? Pause and guess.",
                  FadeIn(pq2), run_time=1.6)
        self.pause([-2.6, -3.25, 0])
        anims = []
        for k in range(3):
            l1 = Line(rec.get_right(), h["v1b"].get_left())
            l2 = Line(h["v1b"].get_left(), h["v1a"].get_left())
            anims.append(Succession(travel(l1, REQ_C, 0.5), Flash(h["v1b"].get_left(), color=BAD_C, run_time=0.3), travel(Line(rec.get_right(), h["v1a"].get_left()), REQ_C, 0.5)))
        res2 = VGroup(M("20", 26), T("times 200", 26, OK_C)).arrange(RIGHT, buff=0.2).move_to(pq2)
        self.beat("Twenty times 200. Three requests did fail on v1b. But the route has a retry policy, and each retry goes to a different host than the one that just failed. So v1a answered instead.",
                  LaggedStart(*anims, lag_ratio=0.5), Succession(Wait(1.6), Transform(pq2, res2)), run_time=7.0)
        cnt = VGroup(M("upstream_rq_retry: 3", 22), M("upstream_rq_retry_success: 3", 22), M("ejections_active: 1", 22, BAD_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-4.2, 2.3, 0])
        ej = DashedVMobject(SurroundingRectangle(h["v1b"], buff=0.08, color=BAD_C), num_dashes=24)
        self.play(FadeOut(hc), run_time=0.3)
        self.beat("And after the third error in a row, Envoy took v1b out of the pool. Its admin page says so: three retries, three successes, one host ejected.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in cnt], lag_ratio=0.4), Create(ej), h["v1b"].animate.set_opacity(0.35), run_time=4.0)
        self.beat("That is outlier detection. Instead of asking the door, it watches the real answers. Three 500s in a row, and the host is skipped for thirty seconds, longer each time it happens again.",
                  Indicate(cnt[2], color=BAD_C), run_time=3.0)
        self.beat("Two ways to notice a sick host, then. A health check knocks on the door. Outlier detection listens to the phone calls.",
                  Indicate(hz, color=OK_C), Succession(Wait(1.6), Indicate(rt, color=BAD_C)), run_time=3.4)
        self.play(FadeOut(VGroup(pq2, cnt)), run_time=0.4)

        # ---------- 6. guardrail: retries multiply
        lab = VGroup(curl, a0, rec, rec_l, *h.values(), g1, g2, gl1, gl2, a1, a2, w1, w2, rb, rbl, x, hz, rt, ej)
        self.play(FadeOut(lab), run_time=0.6)
        hd = T("Retries hide failures. That's their use, and their danger.", 30, ASK_C).move_to(UP * 3.0)
        self.beat("Now the guardrail. Retries hide failures. That is their use, and their danger.",
                  FadeIn(hd), run_time=2.0)
        lv = [box(n, OFF_C, w=1.9, h=0.6, size=24) for n in ("A", "B", "C", "D")]
        ys = [1.8, 0.7, -0.4, -1.5]
        for b, y in zip(lv, ys):
            b.move_to([-5.4, y, 0])
        self.beat("Picture a chain: A calls B, B calls C, C calls D. Every hop tries once, and then retries twice. Three tries per hop.",
                  LaggedStart(*[FadeIn(b) for b in lv], lag_ratio=0.25), run_time=3.0)
        counts = [1, 3, 9, 27]
        dts = VGroup()
        for n, y in zip(counts[1:], ys[1:]):
            row = VGroup(*[Dot(radius=0.07, color=REQ_C if n < 27 else BAD_C) for _ in range(n)]).arrange(RIGHT, buff=0.12).move_to([0.4, y, 0]).align_to([-3.9, 0, 0], LEFT)
            dts.add(row)
        nums = VGroup(*[T(f"{n} calls", 26, REQ_C if n < 27 else BAD_C).move_to([5.6, y, 0]) for n, y in zip(counts[1:], ys[1:])])
        self.beat("When D is struggling, one user request becomes three calls to B. Nine to C. And twenty-seven to D, just when D can least afford it.",
                  FadeIn(dts[0]), FadeIn(nums[0]), Succession(Wait(1.4), AnimationGroup(FadeIn(dts[1]), FadeIn(nums[1]))),
                  Succession(Wait(2.6), AnimationGroup(LaggedStart(*[FadeIn(d) for d in dts[2]], lag_ratio=0.03), FadeIn(nums[2]))), run_time=6.0)
        rule = T("Keep retries few, short, and only for requests safe to repeat.", 28).move_to(DOWN * 2.55)
        fit(rule, 12.6)
        self.beat("The kind receptionist turned into a mob. So keep retries few and short, and only for requests that are safe to repeat. The lab's route waits three seconds in total, and gives each try one second.",
                  FadeIn(rule, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(hd, *lv, dts, nums, rule)), run_time=0.6)
        cb = VGroup(T("circuit breakers: past a limit, answer 503 at once", 26),
                    T("instead of letting a queue grow outside the door", 26, GREY_B)).arrange(DOWN, buff=0.18).move_to(UP * 1.4)
        cost = VGroup(T("the price:", 26, ASK_C), T("one extra hop on every call, CPU and memory for every proxy", 26)).arrange(RIGHT, buff=0.25).move_to(DOWN * 0.6)
        fit(cost, 12.6)
        self.beat("And remember the payroll queue? Envoy's circuit breakers are limits on connections and waiting requests. Past a limit, it answers 503, service unavailable, at once, instead of letting the queue grow.",
                  FadeIn(cb, shift=UP * 0.1), run_time=3.0)
        self.beat("None of this is free. Every call takes one extra hop, and every proxy costs CPU and memory.",
                  FadeIn(cost, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(cb, cost)), run_time=0.6)

        # ---------- 7. moral, check
        mor = VGroup(T("The trouble lives between the offices.", 32), T("So put the habits at the door, once.", 32, PRX_C)).arrange(DOWN, buff=0.3).move_to(UP * 1.6)
        self.beat("So the moral of the story. The trouble lives between the offices. Put the habits at the door, once, the same for everyone, and let the receptionist watch who really answers.",
                  Write(mor[0]), Succession(Wait(2.4), FadeIn(mor[1])), run_time=5.0)
        cq = VGroup(T("Quick check: /healthz says 200,", 28), T("but real requests fail. Which tool notices?", 28)).arrange(DOWN, buff=0.15).move_to(DOWN * 0.6)
        self.beat("A quick check. A host's health page says 200, but its real requests fail. Which tool notices? Pause and think.",
                  FadeIn(cq, shift=UP * 0.1), run_time=2.0)
        self.pause([0, -1.9, 0], text="pause and think")
        ans = T("Outlier detection: it watches the real answers.", 28, PRX_C).move_to(DOWN * 2.4)
        self.beat("Outlier detection. It watches the real answers, not the door.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.8)
        self.beat("Next, we hand the receptionists to a building manager, Istio. How does every proxy get its rules and its ID badge, without anyone writing a file?",
                  FadeOut(VGroup(cq, ans)), mor.animate.set_opacity(0.4), run_time=1.6)
        self.wait(1.0)
