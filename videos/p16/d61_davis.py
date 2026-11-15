import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bOneAgent\b", "One Agent"), (r"\bSmartscape\b", "Smart scape"), (r"\bDynatrace\b", "Dyna-trace"),
            (r"\bP-12345\b", "P one two three four five"), (r"\bSLOWDOWN\b", "slowdown"), (r"\bp95\b", "P 95"),
            (r"\bPostgres\b", "Postgres"), (r"\btraceparent\b", "trace parent")])


def tint(c, k=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


class D61Davis(VoiceScene):
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
        self.title_card("Dynatrace: one problem, one root cause", "OneAgent, Smartscape and Davis")

        # 1. the problem: four true alerts
        XS = (-4.95, -1.65, 1.65, 4.95)
        Y = 0.9
        names = ("web", "checkout", "payments", "Postgres")
        svc = VGroup(*[box(n, BLUE_M if i < 3 else GREY_B, w=2.4, h=0.8, size=28).move_to([x, Y, 0]) for i, (n, x) in enumerate(zip(names, XS))])
        self.beat("Take a made-up shop. web calls checkout, checkout calls payments, and payments uses a Postgres database.",
                  LaggedStart(*[FadeIn(s, shift=RIGHT * 0.1) for s in svc], lag_ratio=0.3), run_time=3.0)
        pool = chip("connection pool full", RED_M, 22).next_to(svc[2], DOWN, buff=0.3)
        self.beat("At 10:02, the database connection pool inside payments fills up, and database calls start to wait.",
                  FadeIn(pool, shift=UP * 0.1), svc[2][0].animate.set_stroke(RED_M), run_time=2.2)
        al = VGroup(M("FIRING  HighLatency    service=web       p95=2.4s", 20, RED_M),
                    M("FIRING  HighLatency    service=checkout  p95=2.3s", 20, RED_M),
                    M("FIRING  HighErrorRate  service=checkout  errors=5%", 20, RED_M),
                    M("FIRING  HighErrorRate  service=payments  errors=6%", 20, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([0, -2.3, 0])
        self.beat("In your Part 12 stack, each symptom fires its own rule, within a minute.",
                  LaggedStart(*[FadeIn(a, shift=UP * 0.1) for a in al], lag_ratio=0.4), run_time=2.8)
        q = T("which one caused the others?", 28, YELLOW_M).move_to([0, 2.7, 0])
        self.beat("Every alert is true. And none of them says which one caused the others. You dig through three tools to find out.",
                  Succession(Wait(1.6), FadeIn(q, shift=DOWN * 0.1)), run_time=3.4)
        self.play(FadeOut(al), FadeOut(q), FadeOut(pool), svc[2][0].animate.set_stroke(BLUE_M), run_time=0.6)

        # 2. OneAgent and the self-drawn map
        agents = VGroup(*[chip("OneAgent", GOLD_M, 20).next_to(s, DOWN, buff=0.3) for s in svc])
        self.beat("Dynatrace starts with OneAgent, installed once per host. It finds every process, and works out what it is.",
                  LaggedStart(*[FadeIn(a, shift=UP * 0.1) for a in agents], lag_ratio=0.2), run_time=2.8)
        self.beat("It loads a small code module into supported processes. The module records each request as it passes through. Nobody changed the code.",
                  LaggedStart(*[Indicate(s, color=GOLD_M, scale_factor=1.05) for s in svc], lag_ratio=0.2), run_time=3.2)
        calls = VGroup(*[edge_arrow(svc[i], svc[i + 1], GREY_B) for i in range(3)])
        hdr = M("trace header", 20, GOLD_M).move_to([calls[0].get_center()[0], Y + 0.68, 0])
        qmap = T("but how does it know who calls whom?", 28, YELLOW_M).move_to([0, 2.7, 0])
        self.beat("But how does it know who calls whom?", FadeIn(qmap, shift=DOWN * 0.1), run_time=1.4)
        self.steps("The module in the caller adds a trace header to each outgoing request. The module in the receiver reads it. So both ends of the call are linked.",
                   (1.0, GrowArrow(calls[0])), (0.6, FadeIn(hdr)), (1.4, travel(calls[0], GOLD_M, 1.4)), (1.4, Indicate(svc[1], color=GOLD_M, scale_factor=1.05)))
        smap = T("Smartscape: the map nobody draws", 28, TEAL_M).move_to(qmap)
        self.beat("Smartscape records each link it sees. That is the live map of everything, and it draws itself.",
                  FadeOut(hdr), Transform(qmap, smap), LaggedStart(GrowArrow(calls[1]), GrowArrow(calls[2]), lag_ratio=0.5),
                  Succession(Wait(1.0), LaggedStart(travel(calls[1], GOLD_M, 0.8), travel(calls[2], GOLD_M, 0.8), lag_ratio=0.5)), run_time=3.6)
        ids = VGroup(*[M(f"id: {n}", 20, TEAL_M).next_to(a, DOWN, buff=0.25) for n, a in zip(names, agents)])
        sig = VGroup(chip("metric", PURPLE_M, 20), chip("log line", PURPLE_M, 20), chip("span", PURPLE_M, 20)).arrange(RIGHT, buff=0.3).move_to([1.65, -2.9, 0])
        self.beat("Every metric, log line and span carries the ID of the entity it came from. That shared ID is how the signals join, with no join logic from you.",
                  LaggedStart(*[FadeIn(i) for i in ids], lag_ratio=0.2), Succession(Wait(2.4), FadeIn(sig, shift=UP * 0.1)), Succession(Wait(3.4), Indicate(ids[2], color=TEAL_M)), run_time=4.8)
        self.play(FadeOut(sig), FadeOut(ids), FadeOut(agents), run_time=0.5)

        # 3. Davis: baselines, then the walk
        dav = T("Davis", 30, GREEN_M).move_to(qmap)
        self.beat("Davis is the engine that watches all of this. First, it learns a baseline for each service: what normal looks like for it, at this time.",
                  Transform(qmap, dav), run_time=2.4)
        sym = VGroup(*[chip(t, RED_M, 20).next_to(svc[i], DOWN, buff=0.3) for i, t in ((0, "slow"), (1, "slow, errors"), (2, "errors"))])
        self.beat("At 10:02, three services leave their baselines. Davis sees the same symptoms as events.",
                  *[svc[i][0].animate.set_stroke(RED_M) for i in range(3)], LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in sym], lag_ratio=0.3), run_time=2.6)
        walker = RoundedRectangle(corner_radius=0.18, width=2.56, height=1.0, color=YELLOW_M, stroke_width=4).move_to(svc[0])
        self.beat("Then it walks. It starts at the affected entity, web, and follows the links to what web depends on.",
                  Create(walker), run_time=1.8)
        self.steps("At each one it asks: are you unhealthy too? checkout is. So Davis keeps going down.",
                   (1.2, walker.animate.move_to(svc[1])), (1.4, Indicate(sym[1], color=RED_M)), (0.6, Wait(0.6)))
        self.steps("payments is unhealthy too. The time in the traces piles up in its database calls. Keep going.",
                   (1.2, walker.animate.move_to(svc[2])), (1.4, Indicate(sym[2], color=RED_M)))
        ok = chip("healthy", GREEN_M, 20).next_to(svc[3], DOWN, buff=0.3)
        self.steps("Postgres itself looks healthy. The waiting happens in the pool inside payments. So the trail ends here.",
                   (1.2, walker.animate.move_to(svc[3])), (0.8, FadeIn(ok, shift=UP * 0.1), svc[3][0].animate.set_stroke(GREEN_M)), (1.8, Wait(1.8)),
                   (1.0, walker.animate.move_to(svc[2]).set_color(RED_M)))
        ft = T("fault-tree analysis: stop where an unhealthy part's dependencies look fine", 24, GREY_B).move_to([0, -0.95, 0])
        self.beat("Dynatrace calls this walk a fault-tree analysis. It ends at an unhealthy part whose own dependencies look fine. That is the most probable root cause.",
                  FadeIn(ft, shift=UP * 0.1), run_time=2.4)

        # problem card
        pc = RoundedRectangle(corner_radius=0.15, width=7.4, height=2.0, stroke_color=RED_M, stroke_width=3).set_fill(tint(RED_M, 0.1), 1).move_to([0, -2.55, 0])
        pl = VGroup(M("P-12345   SLOWDOWN", 24, RED_M), M("root cause: payments", 22, WHITE), M("affected: web, checkout", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(pc)
        self.beat("So Davis opens one problem, not four alerts. An ID, like P-12345. The category, slowdown. payments as the root cause, and web and checkout as affected.",
                  Create(pc), Succession(Wait(1.6), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in pl], lag_ratio=0.6)), run_time=6.0)
        self.beat("Two graphs that spiked in the same minute are not linked by timing alone. The link comes from the map and the traces.",
                  LaggedStart(*[Indicate(c, color=GOLD_M) for c in calls], lag_ratio=0.3), run_time=2.8)

        # 4. the limit: no agent, no link
        self.play(FadeOut(VGroup(pc, pl, ft)), run_time=0.5)
        dark = VGroup(svc[2], calls[2], svc[3], ok, sym[2])
        self.beat("Now remove OneAgent from payments, in your head. Nobody instruments it, so the map has no link into it.",
                  dark.animate.set_opacity(0.15), walker.animate.move_to(svc[1]).set_color(YELLOW_M), calls[1].animate.set_opacity(0.15), run_time=2.6)
        stop = T("Davis stops at checkout", 28, YELLOW_M).move_to([0, -1.4, 0])
        self.beat("Davis would stop at checkout, because it cannot follow a call into something nobody instruments. A pipe without a sensor does not exist for it.",
                  FadeIn(stop, shift=UP * 0.1), Wiggle(walker), run_time=3.0)
        self.play(FadeOut(VGroup(svc, calls, sym, ok, walker, stop, qmap)), run_time=0.7)

        # 5. recap
        rcp = VGroup(T("OneAgent: install once per host, no code changes", 30, GOLD_M),
                     T("Smartscape: a map drawn from what it sees", 30, TEAL_M),
                     T("one entity ID joins every signal", 30, PURPLE_M),
                     T("Davis: walks the map to one root cause", 30, GREEN_M)).arrange(DOWN, buff=0.4)
        self.beat("OneAgent sees each process. Smartscape draws the map from what it sees. One ID joins every signal. And Davis walks that map, from the symptoms to one root cause.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rcp], lag_ratio=0.5), run_time=5.4)
        self.wait(1.0)
