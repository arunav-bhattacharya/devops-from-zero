import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bHelloErrorBudgetFastBurn\b", "hello error budget fast burn"), (r"\bHelloErrorBudgetSlowBurn\b", "hello error budget slow burn"),
    (r"\bHelloDown\b", "hello down"), (r"\bgroup_by\b", "group by"), (r"\bgroup_wait\b", "group wait"), (r"\bamtool\b", "A M tool"),
    (r"\bAlertmanager\b", "alert manager"), (r"\bfor:", "for"), (r"\b3 a\.m\.", "three in the morning"), (r"\b9093\b", "nine oh nine three"),
    (r"(\d)%", r"\1 percent"),
])


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def code(spec, size=20, buff=0.12):
    rows = VGroup(*[M(t, size, c) for t, c in spec])
    cw = M("x" * 40, size).width / 40
    rows.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    for r, (t, _) in zip(rows, spec):
        lead = len(t) - len(t.lstrip(" "))
        r.shift(RIGHT * lead * cw)
    return rows


def panel(w, h, color, c, a=0.06, sw=2.5):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, a), 1).move_to(c)


def stage(label, color=PURPLE_M):
    b = box(label, color, w=5.45, h=0.62, size=22)
    b[1].align_to(b[0], LEFT).shift(RIGHT * 0.22)
    return b


def env(text, color, size=20):
    """A small notification chip (an alert on its way)."""
    return chip(text, color, size, mono=True).set_z_index(6)


class D52AlertPath(VoiceScene):
    def construct(self):
        self.title_card("From alert rule to receiver", "Prometheus decides that it fires; Alertmanager decides who hears")

        # ---- 1. why: nobody watches at 3 a.m.
        dash = panel(3.6, 2.2, GREY_B, [0, 0.4, 0], 0.05, 2)
        curve = VMobject(stroke_color=RED_M, stroke_width=3).set_points_smoothly([[-1.5, -0.3, 0], [-0.8, -0.2, 0], [-0.1, -0.35, 0], [0.4, 0.6, 0], [1.0, 1.1, 0], [1.5, 1.2, 0]])
        zzz = T("3 a.m.: nobody is looking", 28, GREY_B).next_to(dash, DOWN, buff=0.4)
        self.beat("A dashboard helps only while someone is looking at it, and at 3 a.m., nobody is. So Prometheus checks the conditions itself.",
                  FadeIn(dash), Create(curve), Succession(Wait(2.2), FadeIn(zzz, shift=UP * 0.1)), run_time=4.0)
        self.play(FadeOut(VGroup(dash, curve, zzz)), run_time=0.5)

        # ---- 2. the rule, on the left
        prom = panel(6.1, 6.0, RED_M, [-3.45, 0.4, 0], 0.04, 2)
        pl = T("Prometheus", 28, RED_M).move_to(prom.get_corner(UL) + RIGHT * 1.15 + DOWN * 0.38)
        rule = code([("- alert: HelloDown", GOLD_M), ("  expr: up{job=\"hello-devops\"} == 0", WHITE), ("  for: 1m", YELLOW_M),
                     ("  labels:", WHITE), ("    severity: page", BLUE_M)], 20)
        rule.next_to(pl, DOWN, buff=0.3).align_to(pl, LEFT)
        self.beat("An alerting rule is a PromQL query with a name, like HelloDown.",
                  FadeIn(prom), FadeIn(pl), FadeIn(rule[0], shift=RIGHT * 0.1), run_time=2.4)
        self.beat("The comparison filters, so the query returns something only when a scrape fails.",
                  FadeIn(rule[1], shift=RIGHT * 0.1), run_time=2.0)
        self.beat("Prometheus runs it every 15 seconds in the lab. Every series it returns is one active alert.",
                  Indicate(rule[1], color=WHITE, scale_factor=1.03), run_time=2.0)
        self.beat("Its label, severity page, is added to the alert. Alertmanager will route on it.",
                  FadeIn(rule[3:], shift=RIGHT * 0.1), run_time=1.6)

        # states and a timeline of evaluations
        sts = VGroup(box("inactive", GREY_B, w=1.75, h=0.6, size=22), box("pending", GOLD_M, w=1.75, h=0.6, size=22), box("firing", RED_M, w=1.75, h=0.6, size=22))
        sts.arrange(RIGHT, buff=0.3).move_to([-3.45, 0.35, 0])
        sa = VGroup(*[Arrow(sts[i].get_right(), sts[i + 1].get_left(), buff=0.04, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.35) for i in range(2)])
        self.beat("An alert moves through three states: inactive, pending, firing.",
                  LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in sts], lag_ratio=0.4), Create(sa), run_time=2.6)
        TL0, TL1, TY = -6.1, -0.8, -1.35
        tl = Line([TL0, TY, 0], [TL1, TY, 0], stroke_width=2, color=GREY_D)
        n = 13
        xs = np.linspace(TL0 + 0.2, TL1 - 0.2, n)
        tk = VGroup(*[Line([x, TY - 0.1, 0], [x, TY + 0.1, 0], stroke_width=2, color=GREY_D) for x in xs])
        tll = T("one check every 15 s", 22, GREY_B).next_to(tl, DOWN, buff=0.3)
        self.add(tl, tk)
        self.play(FadeIn(tll), Create(tl), run_time=0.6)
        pat = [0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1]  # 1 = condition true
        res = [Dot([x, TY + 0.45, 0], radius=0.09, color=(RED_M if p else GREEN_M)) for x, p in zip(xs, pat)]
        mark = SurroundingRectangle(sts[0], buff=0.06, color=YELLOW_M, stroke_width=4)

        def at(i):
            return mark.animate.move_to(sts[i])
        self.add(mark)
        self.beat("Two checks pass. The alert is inactive.",
                  FadeIn(res[0], scale=0.5), Succession(Wait(1.0), FadeIn(res[1], scale=0.5)), run_time=2.0)
        self.beat("Then a scrape fails. The alert is pending. for: 1m means it must stay true for a whole minute.",
                  FadeIn(res[2], scale=0.5), at(1), Succession(Wait(1.6), FadeIn(res[3], scale=0.5)), Succession(Wait(3.6), FadeIn(rule[2], shift=RIGHT * 0.1)), run_time=5.4)
        self.beat("If one check is false, it goes back to inactive, and the wait starts again.",
                  FadeIn(res[4], scale=0.5), at(0), run_time=1.6)
        blip = T("for: filters out blips", 22, YELLOW_M).move_to([-3.45, TY + 0.85, 0])
        self.beat("So for: filters out blips, like one slow scrape during a deploy.",
                  FadeIn(blip), run_time=1.6)
        self.beat("Now the scrapes keep failing. Pending again, and after a whole minute of true checks, it fires.",
                  FadeOut(blip), Succession(*[FadeIn(r, scale=0.5, run_time=0.32) for r in res[5:10]]),
                  Succession(Wait(0.3), at(1), Wait(2.6), at(2)), run_time=5.2)
        self.play(LaggedStart(*[FadeIn(r, scale=0.5) for r in res[10:]], lag_ratio=0.4), run_time=0.9)

        # ---- 3. Prometheus only decides; Alertmanager tells people
        am = panel(5.9, 6.0, PURPLE_M, [3.6, 0.4, 0], 0.04, 2)
        aml = T("Alertmanager", 28, PURPLE_M).move_to(am.get_corner(UL) + RIGHT * 1.4 + DOWN * 0.38)
        hand = Arrow([-0.25, 0.9, 0], [0.55, 0.9, 0], buff=0, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        self.beat("But Prometheus only decides that an alert fires. It sends no message itself. It hands firing alerts to Alertmanager.",
                  FadeIn(am), FadeIn(aml), GrowArrow(hand), run_time=3.0)
        self.play(travel(hand, RED_M, 0.8), run_time=0.9)
        flood = VGroup(*[Dot(radius=0.07, color=RED_M) for _ in range(24)])
        for i, d in enumerate(flood):
            d.move_to([1.3 + (i % 8) * 0.4, 2.6 - (i // 8) * 0.3, 0])
        self.beat("One broken database can trip dozens of rules at once, and each firing alert is re-sent about once a minute. Straight to a phone, that is a flood.",
                  LaggedStart(*[FadeIn(d, shift=RIGHT * 0.3) for d in flood], lag_ratio=0.08), run_time=4.4)

        # the four jobs, stacked in the Alertmanager panel
        g = stage("group").move_to([3.6, 1.45, 0])
        ih = stage("inhibit?  silenced?").move_to([3.6, 0.3, 0])
        ro = stage("route by labels").move_to([3.6, -0.85, 0])
        pg = mbox("pager", RED_M, w=2.1, h=0.62, size=22).move_to([2.35, -2.0, 0])
        tkt = mbox("tickets", GOLD_M, w=2.1, h=0.62, size=22).move_to([4.85, -2.0, 0])
        SLA, SLB = 4.3, 5.62  # where the two alert chips rest inside a stage
        a1 = Arrow(g.get_bottom(), ih.get_top(), buff=0.06, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        a2 = Arrow(ih.get_bottom(), ro.get_top(), buff=0.06, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        a3 = Arrow(ro.get_bottom() + LEFT * 0.6, pg.get_top(), buff=0.06, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        a4 = Arrow(ro.get_bottom() + RIGHT * 0.6, tkt.get_top(), buff=0.06, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        one = env("1 message", PURPLE_M).move_to(g)
        self.beat("So Alertmanager groups them. Alerts with the same group_by labels become one notification. Fifty pods failing give one message, not fifty.",
                  FadeIn(g), Succession(Wait(3.2), AnimationGroup(*[d.animate.move_to(g.get_center()).set_opacity(0) for d in flood])), run_time=6.0)
        self.remove(flood)
        self.beat("Then each group walks down a tree of routes, matched on labels. In the lab, severity page goes to pager, and everything else to tickets.",
                  GrowArrow(a1), FadeIn(ih), GrowArrow(a2), FadeIn(ro), Succession(Wait(3.4), AnimationGroup(GrowArrow(a3), GrowArrow(a4), FadeIn(pg), FadeIn(tkt))), run_time=7.6)
        self.beat("Inhibition: while one alert fires, it mutes others. The lab mutes ticket alerts for a job while a page fires for the same job.",
                  Indicate(ih, color=PURPLE_M, scale_factor=1.04), run_time=2.0)
        sil = T("silences: made at run time, not in the file", 22, GREY_B).move_to([3.6, 2.45, 0])
        self.beat("Silences are temporary mutes you add at run time, with amtool or in the UI. They are not in the config file.",
                  FadeIn(sil, shift=DOWN * 0.1), run_time=2.0)

        # ---- 4. one real outage, end to end
        self.play(FadeOut(VGroup(rule, sts, sa, tl, tk, tll, *res, mark, sil)), run_time=0.7)
        cmd = M("$ docker compose stop redis", 22, GREY_B).move_to([-3.45, 2.3, 0])
        fast = box("FastBurn  severity=page", RED_M, w=5.0, h=0.62, size=22).move_to([-3.45, 1.4, 0])
        slow = box("SlowBurn  severity=ticket", GOLD_M, w=5.0, h=0.62, size=22).move_to([-3.45, -0.15, 0])
        self.beat("Now a real outage. Stop Redis, and every request to hello-devops fails.",
                  FadeIn(cmd, shift=RIGHT * 0.1), run_time=2.0)
        pend = VGroup(*[chip("pending", GOLD_M, 20).next_to(b, DOWN, buff=0.12) for b in (fast, slow)])
        self.beat("Soon both error budget alerts are pending: the fast burn, a page, and the slow burn, a ticket.",
                  FadeIn(fast, shift=RIGHT * 0.1), FadeIn(slow, shift=RIGHT * 0.1), Succession(Wait(2.4), FadeIn(pend)), run_time=6.0)
        fire = VGroup(*[chip("firing", RED_M, 20).move_to(p) for p in pend])
        self.beat("Two minutes later, both fire.",
                  Transform(pend, fire), run_time=1.6)
        ef = env("FastBurn", RED_M).move_to(hand.get_start() + UP * 0.35)
        es = env("SlowBurn", GOLD_M).move_to(hand.get_start() + DOWN * 0.35)
        self.play(ef.animate.move_to([SLA, g.get_y(), 0]), es.animate.move_to([SLB, g.get_y(), 0]), run_time=1.4)
        wait = M("group_wait: 10s", 20, PURPLE_M).move_to([3.6, 2.45, 0])
        self.beat("Alertmanager waits 10 seconds, the group_wait, for more alerts.",
                  FadeIn(wait), run_time=1.8)
        self.play(ef.animate.move_to([SLA, ih.get_y(), 0]), es.animate.move_to([SLB, ih.get_y(), 0]), run_time=1.0)
        mu = T("muted", 22, GOLD_M).next_to(es, UP, buff=0.1)
        es.save_state()
        self.beat("Then inhibition. The page fires for the job hello-devops, so the ticket for the same job is muted.",
                  Succession(Wait(3.0), AnimationGroup(es.animate.set_opacity(0.25), FadeIn(mu))), run_time=4.4)
        hook = panel(11.8, 0.95, GREY_B, [0, -3.15, 0], 0.05, 2)
        out = M("[pager] FIRING HelloErrorBudgetFastBurn job=hello-devops ...", 20, RED_M).move_to(hook)
        self.beat("The page walks down the tree to the pager, and the webhook prints one line. Only the page arrived.",
                  Succession(ef.animate(run_time=1.0).move_to([SLA, ro.get_y(), 0]), ef.animate(run_time=1.0).move_to(pg), FadeOut(ef, run_time=0.3)),
                  Succession(Wait(2.4), AnimationGroup(FadeIn(hook), FadeIn(out, shift=UP * 0.1)), Indicate(pg, color=RED_M)), run_time=5.4)

        # silence while working, then resolve
        sil2 = chip("silence: the page, for 1 hour", GREY_B, 24).move_to([-3.45, -1.75, 0])
        self.beat("You are working on it, so you silence the page for an hour.",
                  FadeIn(sil2, shift=UP * 0.1), run_time=2.4)
        cmd2 = M("$ docker compose start redis", 22, GREEN_M).move_to(cmd)
        self.beat("Fix Redis, then expire the silence, so you will hear when the alert resolves.",
                  Transform(cmd, cmd2), Succession(Wait(2.6), FadeOut(sil2)), run_time=4.0)
        self.beat("The long windows still hold the outage. About 25 minutes after the fix, the page resolved.",
                  Succession(Wait(2.4), AnimationGroup(Transform(pend[0], chip("resolved", GREEN_M, 20).move_to(pend[0])),
                                                       Transform(out, M("[pager] RESOLVED HelloErrorBudgetFastBurn job=hello-devops ...", 20, GREEN_M).move_to(hook)))), run_time=6.0)
        out2 = M("[tickets] FIRING HelloErrorBudgetSlowBurn job=hello-devops ...", 20, GOLD_M)
        out2.move_to(hook.get_center() + DOWN * 0.2).align_to(out, LEFT)
        self.play(Restore(es), FadeOut(mu), run_time=0.4)
        self.beat("In the same second, Alertmanager released the ticket it had been muting. The outage really did spend budget.",
                  Succession(es.animate(run_time=1.0).move_to([SLB, ro.get_y(), 0]), es.animate(run_time=1.0).move_to(tkt), FadeOut(es, run_time=0.3)),
                  Succession(Wait(2.4), AnimationGroup(out.animate.shift(UP * 0.2), FadeIn(out2, shift=UP * 0.1))),
                  run_time=5.0)
        self.wait(0.6)

        # ---- recap
        self.play(FadeOut(VGroup(cmd, fast, slow, pend, wait, hook, out, out2)), run_time=0.7)
        rec = VGroup(T("Prometheus decides", 30, RED_M), T("that an alert fires.", 30)).arrange(DOWN, buff=0.2).move_to([-3.45, 1.1, 0])
        rec2 = VGroup(T("Alertmanager decides", 30, PURPLE_M), T("who hears about it.", 30)).arrange(DOWN, buff=0.2).move_to([-3.45, -0.9, 0])
        self.beat("Prometheus decides that an alert fires. Alertmanager decides who hears about it.",
                  FadeIn(rec, shift=UP * 0.1), Succession(Wait(2.4), FadeIn(rec2, shift=UP * 0.1)), run_time=4.6)
        self.wait(1.2)
