import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import fg as _fg


def box(*a, **k):  # keep the label drawn above its own filled outline, even when the outline is animated
    b = _fg.box(*a, **k); b[1].set_z_index(1); return b


def chip(*a, **k):
    c = _fg.chip(*a, **k); c[1].set_z_index(1); return c

SAY.extend([(r"\bOneAgent\b", "one agent"), (r"\bSmartscape\b", "smart scape"), (r"\bPurePath\b", "pure path"),
            (r"\bPostgres\b", "post gress"), (r"\bP-12345\b", "P 1 2 3 4 5"), (r"\bSLOWDOWN\b", "slowdown"),
            (r"\b10:02\b", "ten oh two"), (r"\bp95\b", "p 95")])

SVC_C = BLUE_M      # services on the map
BAD_C = RED_M       # unhealthy
OK_C = GREEN_M      # healthy
DAV_C = GOLD_M      # Davis, the detective
ASK_C = YELLOW_M
MAP_C = GREY_B      # links


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def lens(c=DAV_C):
    ring = Circle(radius=0.22, stroke_color=c, stroke_width=4)
    handle = Line(ring.point_at_angle(-PI / 4), ring.point_at_angle(-PI / 4) + np.array([0.22, -0.22, 0]), stroke_width=6, color=c)
    return VGroup(ring, handle)


class D61Detective(VoiceScene):
    def pause(self, where, secs=2.4, text="pause and guess"):
        lab = T(text, 26, ASK_C)
        ring = Circle(radius=0.2, stroke_color=ASK_C, stroke_width=4).rotate(PI / 2)
        g = VGroup(ring, lab).arrange(RIGHT, buff=0.22).move_to(where)
        self.play(FadeIn(g), run_time=0.3)
        self.play(Uncreate(ring), run_time=secs, rate_func=linear)
        self.play(FadeOut(lab), run_time=0.3)

    def construct(self):
        self.title_card("One cracked pipe, not four alarms", "how Dynatrace walks from symptoms to a root cause")

        # ---------- 1. the detective
        floors = VGroup(*[RoundedRectangle(corner_radius=0.05, width=5.0, height=0.95, stroke_color=MAP_C, stroke_width=2) for _ in range(4)]).arrange(DOWN, buff=0).move_to([-2.6, 0.1, 0])
        fl = VGroup(*[T(f"floor {5 - i}", 24, MAP_C).move_to(f.get_left() + RIGHT * 0.75) for i, f in enumerate(floors)])
        comp = [("wet ceiling", 1), ("flickering lights", 2), ("smell of damp", 3)]
        cl = VGroup(*[T(t, 24, BAD_C).move_to(floors[i].get_center() + RIGHT * 0.7) for t, i in comp])
        self.beat("Picture a detective, called to an office building at ten in the morning. Tenants are waiting with complaints. A wet ceiling on the fourth floor. Flickering lights on the third. A smell of damp on the second.",
                  FadeIn(floors), FadeIn(fl), Succession(Wait(3.4), LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in cl], lag_ratio=0.6)), run_time=7.0)
        reps = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.05, width=1.5, height=0.42, stroke_color=GREY_B, stroke_width=2), T("report", 20, GREY_B)) for _ in range(3)])
        for r in reps:
            r[1].move_to(r[0])
        reps.arrange(DOWN, buff=0.15).move_to([3.6, 0.1, 0])
        self.beat("A tidy detective writes one report per complaint, and goes home. It feels like progress. Each complaint is real, and each one gets an answer.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in reps], lag_ratio=0.3), run_time=3.6)
        pipe = VGroup(Line(floors[0].get_center() + LEFT * 0.9, floors[3].get_center() + LEFT * 0.9, stroke_width=4, color=SVC_C))
        crack = VGroup(tick(False, 0.2).move_to(floors[0].get_center() + LEFT * 0.9), T("cracked pipe", 24, DAV_C).move_to(floors[0].get_center() + RIGHT * 1.0))
        self.beat("A good detective walks upstairs, and finds one cracked pipe on the fifth floor, which explains all of them.",
                  FadeOut(reps), Create(pipe), Succession(Wait(1.6), FadeIn(crack)), run_time=3.6)
        self.beat("What nobody asked was how the complaints connect. Hold on to that picture. Today's tool tries to be the good detective.",
                  Indicate(crack[1], color=DAV_C), run_time=2.4)
        self.play(FadeOut(VGroup(floors, fl, cl, pipe, crack)), run_time=0.6)

        # ---------- 2. four alerts
        al = VGroup(*[M(t, 22, BAD_C) for t in ("FIRING HighLatency   web       p95=2.4s", "FIRING HighLatency   checkout  p95=2.3s",
                                                 "FIRING HighErrorRate checkout  errors=5%", "FIRING HighErrorRate payments  errors=6%")]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        al.move_to([0, 0.6, 0])
        shop = T("a made-up shop: web calls checkout, checkout calls payments, payments uses Postgres", 24, GREY_B).move_to([0, 2.8, 0])
        fit(shop, 12.6)
        self.beat("Now a made-up shop. Web calls checkout, checkout calls payments, and payments keeps its data in a Postgres database. At 10:02, four alerts fire within a minute.",
                  FadeIn(shop), Succession(Wait(4.6), LaggedStart(*[FadeIn(a, shift=DOWN * 0.1) for a in al], lag_ratio=0.3)), run_time=7.0)
        q = T("Which one is the cause, and which are echoes?", 30, ASK_C).move_to([0, -1.4, 0])
        self.beat("Every alert is true. And not one of them says which caused the others. Which one is the cause, and which are just echoes?",
                  FadeIn(q), run_time=2.6)
        tabs = VGroup(*[chip(t, GREY_B, 24) for t in ("Grafana", "Jaeger", "Kibana")]).arrange(RIGHT, buff=0.4).move_to([0, -2.5, 0])
        self.beat("With the stack we built ourselves, we go digging. A dashboard shows three services went bad together. A trace shows a long database span inside payments. A log search for that trace ID. We get there, in three tools, matching IDs by hand.",
                  LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tabs], lag_ratio=0.8), run_time=7.0)
        first = SurroundingRectangle(al[0], buff=0.08, color=ASK_C, stroke_width=2.5)
        self.beat("You might be thinking: easy, the cause is whatever went bad first. Let's be fair, that's where most of us would start. But all four went bad in the same minute. Timing alone can't tell a cause from an echo.",
                  FadeOut(tabs), Create(first), run_time=3.0)
        self.beat("What we need is the plumbing plan: who calls whom.",
                  FadeOut(first), run_time=1.6)
        self.play(FadeOut(VGroup(q, shop)), al.animate.scale(0.9).move_to([3.3, 2.6, 0]), run_time=0.8)

        # ---------- 3. the map
        names = ["web", "checkout", "payments", "Postgres"]
        ys = [2.3, 0.75, -0.8, -2.35]
        S = [box(n, SVC_C, w=2.6, h=0.75, size=26).move_to([-3.6, y, 0]) for n, y in zip(names, ys)]
        links = [edge_arrow(S[i], S[i + 1], MAP_C) for i in range(3)]
        ll = VGroup(*[T("calls", 22, MAP_C).next_to(l, RIGHT, buff=0.15) for l in links[:2]], T("uses", 22, MAP_C).next_to(links[2], RIGHT, buff=0.15))
        self.beat("Dynatrace draws that plan by itself. Its agent, OneAgent, runs on every machine and records each call as it passes through. Dynatrace calls each thing it watches an entity.",
                  LaggedStart(*[FadeIn(s) for s in S], lag_ratio=0.25), run_time=3.6)
        self.beat("The calls become links on a live map, called Smartscape. Web calls checkout, checkout calls payments, payments uses Postgres. The building's plumbing plan, redrawn every minute.",
                  LaggedStart(*[GrowArrow(l) for l in links], lag_ratio=0.4), FadeIn(ll), Succession(Wait(2.4), LaggedStart(*[travel(l, SVC_C, 0.6) for l in links], lag_ratio=0.6)), run_time=5.6)
        base = T("each one compared with its own normal", 24, GREY_B).move_to([3.3, 0.0, 0])
        self.beat("An engine called Davis watches every entity against its own baseline, what normal looks like for it at this time. At 10:02, web, checkout and payments leave their baselines.",
                  FadeIn(base), Succession(Wait(3.6), AnimationGroup(*[S[i][0].animate.set_stroke(BAD_C) for i in range(3)])), run_time=5.6)

        # ---------- 4. predict, then the walk
        pq = T("Where will the trail end?", 30, ASK_C).move_to([3.3, -1.0, 0])
        self.beat("Davis starts at the affected entity and walks down the links. Where will the trail end? Pause and guess.",
                  FadeOut(base), FadeIn(pq), run_time=2.0)
        self.pause([3.3, -1.7, 0])
        dv = lens().move_to(S[0].get_right() + RIGHT * 0.6)
        dvl = T("Davis", 24, DAV_C).next_to(dv, RIGHT, buff=0.15)
        self.beat("Start at web. Unhealthy. What does it depend on? Checkout.",
                  FadeIn(dv), FadeIn(dvl), run_time=2.0)
        self.beat("Is checkout unhealthy too? Yes. Keep going down. Payments? Also unhealthy. Keep going.",
                  VGroup(dv, dvl).animate.move_to(S[1].get_right() + RIGHT * 1.0), Succession(Wait(2.4), VGroup(dv, dvl).animate.move_to(S[2].get_right() + RIGHT * 1.0)), run_time=4.2)
        self.beat("Postgres? The obvious guess is the database. The slow spans were database calls, after all. Let's look.",
                  VGroup(dv, dvl).animate.move_to(S[3].get_right() + RIGHT * 1.0), run_time=2.6)
        ok = VGroup(tick(True, 0.18), T("healthy", 24, OK_C)).arrange(RIGHT, buff=0.15).next_to(S[3], DOWN, buff=0.12)
        self.beat("Postgres looks healthy. The waiting happens inside payments, in its connection pool, the fixed set of open connections it shares. Every call queues for a free one.",
                  S[3][0].animate.set_stroke(OK_C), FadeIn(ok), run_time=3.4)
        self.beat("So the trail ends at payments: an unhealthy component whose own dependencies look fine. That is the most probable root cause.",
                  VGroup(dv, dvl).animate.move_to(S[2].get_right() + RIGHT * 1.0), Indicate(S[2][1], color=BAD_C), run_time=3.0)
        self.beat("The database was the alibi everybody believed. The pipe cracked one floor up.",
                  run_time=None)

        # ---------- 5. name it
        self.play(FadeOut(pq), run_time=0.3)
        prob = VGroup(M("P-12345  SLOWDOWN", 24, DAV_C), VGroup(T("root cause:", 24, GREY_B), T("payments", 24, BAD_C)).arrange(RIGHT, buff=0.2),
                      VGroup(T("affected:", 24, GREY_B), T("web, checkout", 24)).arrange(RIGHT, buff=0.2)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        pbox = SurroundingRectangle(prob, buff=0.3, color=DAV_C, stroke_width=2.5, corner_radius=0.1)
        pg = VGroup(pbox, prob).move_to([3.3, -0.6, 0])
        self.beat("Dynatrace calls this walk a fault-tree analysis. Instead of four alerts, it opens one problem: an ID like P-12345, the category SLOWDOWN, payments as the root cause, and web and checkout listed as affected.",
                  al.animate.set_opacity(0.3), Create(pbox), Succession(Wait(2.4), LaggedStart(*[FadeIn(p) for p in prob], lag_ratio=0.6)), run_time=6.0)
        self.beat("Four complaints, one cracked pipe. And notice how Davis linked them: by following recorded calls, not by timing.",
                  *[Indicate(l, color=SVC_C) for l in links[:2]], run_time=3.0)

        # ---------- 6. break: an unwatched service
        self.play(FadeOut(pg), al.animate.set_opacity(1), S[2][0].animate.set_stroke(BAD_C), run_time=0.5)
        blind = DashedVMobject(RoundedRectangle(corner_radius=0.12, width=2.6, height=0.75, stroke_color=GREY_D, stroke_width=3), num_dashes=30).move_to(S[2])
        self.beat("Now let's break it on purpose. Picture payments running without OneAgent. Nobody instrumented it. Where does the walk end now? Pause and guess.",
                  FadeOut(S[2][0]), FadeIn(blind), S[2][1].animate.set_color(GREY_D), links[1].animate.set_opacity(0.25), links[2].animate.set_opacity(0.25), run_time=3.6)
        self.pause([3.3, -1.7, 0])
        self.beat("At checkout. Davis can't follow a call into something nobody measures. So it names checkout, which is only a victim.",
                  VGroup(dv, dvl).animate.move_to(S[1].get_right() + RIGHT * 1.0), Indicate(S[1][1], color=BAD_C), run_time=3.0)
        rule = VGroup(T("Davis can only follow", 28, DAV_C), T("what something measured.", 28, DAV_C), T("An unwatched service", 28), T("is where its trail ends.", 28)).arrange(DOWN, buff=0.12).move_to([3.4, -1.2, 0])
        self.beat("So the point really is: Davis can only follow what something measured. An unwatched service is where its trail ends. A pipe with no sensor.",
                  FadeIn(rule, shift=UP * 0.1), run_time=3.0)
        self.play(FadeOut(VGroup(rule, blind, dv, dvl, ok, al, ll, *S, *links)), run_time=0.7)

        # ---------- 7. guardrails
        g1 = VGroup(T("It compares each service with its own past.", 26), T("A service that was always slow looks normal. Your SLOs are still yours to write.", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        g2 = VGroup(T("One agent and one map cost something:", 26), T("money, lock-in, and telemetry that lives on someone else's servers.", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        g3 = VGroup(T("OneAgent sees a program only from its start:", 26), T("restart the apps you want traced.", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        gs = VGroup(g1, g2, g3).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit(gs, 12.6).move_to([0, 0.3, 0])
        self.beat("A few honest limits. Davis doesn't know what you promised your users. It compares each service with its own past, so a service that has always been slow looks normal. Your service level objectives are still yours to write.",
                  FadeIn(g1, shift=UP * 0.1), run_time=3.4)
        self.beat("The one-agent, one-map approach is paid for in money, in lock-in, and in control: your data lives on Dynatrace's servers.",
                  FadeIn(g2, shift=UP * 0.1), run_time=2.6)
        self.beat("And OneAgent only sees a program from its start. A process that was already running when you installed it shows up with no traces, until you restart it.",
                  FadeIn(g3, shift=UP * 0.1), run_time=2.6)
        self.play(FadeOut(gs), run_time=0.6)

        # ---------- 8. moral, check
        mor = VGroup(T("Don't answer each complaint.", 32), T("Follow the pipes to the one that cracked.", 32, DAV_C)).arrange(DOWN, buff=0.25).move_to([0, 1.9, 0])
        self.beat("So the moral of the story. Don't answer each complaint. Follow the pipes to the one that cracked: start at the symptom, walk down what it depends on, and stop at the first broken thing whose own dependencies look fine.",
                  Write(mor[0]), Succession(Wait(2.2), FadeIn(mor[1])), run_time=7.0)
        cq = VGroup(T("Quick check: Davis names checkout as the root cause.", 26), T("You know checkout calls a service nobody instrumented. What do you suspect?", 26)).arrange(DOWN, buff=0.15).move_to([0, -0.4, 0])
        fit(cq, 12.6)
        self.beat("A quick check. Davis names checkout as the root cause. But you know checkout calls a service that nobody instrumented. What do you suspect? Pause and think.",
                  FadeIn(cq), run_time=2.4)
        self.pause([0, -1.6, 0], text="pause and think")
        ans = T("The trail may have ended at the blind spot: look one step further down.", 26, DAV_C).move_to([0, -2.2, 0])
        fit(ans, 12.6)
        self.beat("That the trail ended at the blind spot. The real cause may sit one step further down, where nobody measured. Instrument it, or go and look.",
                  FadeIn(ans), run_time=2.4)
        self.beat("Next, we get our own data into Dynatrace, and learn the language that reads it. How do you ask one question of metrics, logs and traces at once?",
                  FadeOut(VGroup(cq, ans)), mor.animate.set_opacity(0.4), run_time=2.0)
        self.wait(1.0)
