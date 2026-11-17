import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bfor: 10m\b", "for ten minutes"), (r"\bfor: 1m\b", "for one minute"), (r"\bfor: 2m\b", "for two minutes"), (r"\bfor:", "for"),
    (r"\bamtool\b", "A M tool"), (r"\bpromtool\b", "prom tool"), (r"(\d)%", r"\1 percent"), (r"\b3 a\.m\.", "three in the morning"),
    (r"\bgroup_wait\b", "group wait"), (r"\birate\b", "I rate"), (r"\brate\(\)", "rate"),
])


def dark(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def frame(w, h, color, c, fill=0.08, sw=3):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw)
    return r.set_fill(dark(color, fill), opacity=1).move_to(c)


def lchip(text, color, size=24, mono=False):
    t = (M if mono else T)(text, size)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.34, height=max(0.6, t.height + 0.3), stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.22), opacity=1)
    return VGroup(r, t.move_to(r)).set_z_index(3)


def monitor(color=GREEN_M):
    r = RoundedRectangle(corner_radius=0.06, width=0.62, height=0.46, stroke_color=color, stroke_width=2.5).set_fill(dark(color, 0.2), 1)
    w = VMobject(stroke_color=color, stroke_width=2).set_points_as_corners([[-0.22, 0, 0], [-0.08, 0, 0], [-0.03, 0.13, 0], [0.03, -0.13, 0], [0.08, 0, 0], [0.22, 0, 0]])
    return VGroup(r, w.move_to(r))


class D52NursesStation(VoiceScene):
    def guess(self, at):
        q = T("pause and guess", 26, YELLOW_M).move_to(at)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(q), run_time=0.3)

    def construct(self):
        self.title_card("The nurses' station", "alerting rules, Alertmanager, and who hears what")

        # ---------------- 1. twenty monitors, one flicker
        mons = VGroup(*[monitor() for _ in range(20)]).arrange_in_grid(4, 5, buff=(0.35, 0.35)).move_to([-3.6, 0.0, 0])
        doc = VGroup(Circle(radius=0.2, stroke_color=BLUE_M, stroke_width=3).set_fill(dark(BLUE_M, 0.3), 1),
                     Arc(radius=0.36, start_angle=0, angle=PI, stroke_color=BLUE_M, stroke_width=3))
        doc[1].next_to(doc[0], DOWN, buff=0.04)
        doc.move_to([4.6, 0.3, 0])
        phone = RoundedRectangle(corner_radius=0.08, width=0.4, height=0.7, stroke_color=BLUE_M, stroke_width=2.5).next_to(doc, LEFT, buff=0.3)
        doc_l = T("the doctor", 26, BLUE_M).next_to(doc, DOWN, buff=0.3)
        self.beat("Picture a hospital night shift. Twenty bedside monitors, and one doctor with a phone.",
                  LaggedStart(*[FadeIn(m) for m in mons], lag_ratio=0.03), FadeIn(doc), FadeIn(phone), FadeIn(doc_l), run_time=2.4)
        arrows = VGroup(*[Line(m.get_right(), phone.get_left(), stroke_color=RED_M, stroke_width=1.5).set_opacity(0.6) for m in mons])
        self.beat("The power flickers, and all twenty beep at once. If each one rang her phone, she would get twenty calls about one problem.",
                  LaggedStart(*[m[0].animate.set_stroke(RED_M).set_fill(dark(RED_M, 0.4)) for m in mons], lag_ratio=0.03),
                  LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.03), Wiggle(phone), run_time=3.4)
        b12 = mons[11]
        lab12 = T("bed 12: a real emergency", 24, YELLOW_M).next_to(mons, DOWN, buff=0.3)
        self.beat("Worse, a real emergency in bed twelve would be one more ring in the noise.",
                  Circumscribe(b12, color=YELLOW_M), FadeIn(lab12), run_time=2.0)
        q = T("Who decides which beep reaches a person?", 34, YELLOW_M).to_edge(UP, buff=0.6)
        self.beat("More alarms feel like more safety. Each one on its own looks sensible. Together, they bury the one that matters. So who decides which beep reaches a person?",
                  Write(q), run_time=3.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(mons, doc, phone, doc_l, arrows, lab12, q)), run_time=0.6)

        # ---------------- 2. an alerting rule: a query that runs by itself
        self.beat("Last time, our queries said how busy, how broken and how slow hello-devops is. But they answer only when asked, and at 3 a.m. nobody asks.",
                  run_time=None)
        rule = VGroup(M("alert: HelloDown", 26, GOLD_M), M('expr: up{job="hello-devops"} == 0', 26), M("for: 1m", 26, YELLOW_M),
                      M("labels: severity: page", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rb = frame(rule.width + 0.7, rule.height + 0.6, GOLD_M, [0, 0, 0], fill=0.08)
        rg = VGroup(rb, rule.move_to(rb)).move_to([-2.0, 0.6, 0])
        self.beat("So we give a query a name, and Prometheus runs it by itself, every fifteen seconds in the lab. That is an alerting rule.",
                  Create(rb), Write(rule[0]), Write(rule[1]), run_time=3.0)
        n1 = T("returns something only when a scrape fails", 24, GREY_B).next_to(rg, RIGHT, buff=0.4).align_to(rule[1], UP).shift(DOWN * 0.0)
        n1.next_to(rg, DOWN, buff=0.35).align_to(rg, LEFT)
        self.beat("The condition: up is zero. It returns something only when a scrape fails. Every series it returns is one active alert.",
                  FadeIn(n1), Indicate(rule[1], color=WHITE), run_time=2.2)
        n2 = T("must stay true for a whole minute", 24, YELLOW_M).next_to(n1, DOWN, buff=0.2).align_to(n1, LEFT)
        n3 = T("a label that the next stop routes on", 24, RED_M).next_to(n2, DOWN, buff=0.2).align_to(n1, LEFT)
        self.beat("for one minute: the condition must stay true for a whole minute first. And a label, severity page, that the next stop will route on.",
                  FadeIn(rule[2]), FadeIn(n2), FadeIn(rule[3]), FadeIn(n3), run_time=2.6)
        self.play(FadeOut(VGroup(rg, n1, n2, n3)), run_time=0.5)

        # ---------------- 3. predict: for: 10m with one false check
        ax = Axes(x_range=[0, 22, 2], y_range=[0, 1, 1], x_length=10.0, y_length=1.2, tips=False,
                  axis_config={"stroke_color": GREY_B, "stroke_width": 2, "include_ticks": False}).move_to([0.6, 0.9, 0])
        xl = VGroup(*[T(str(m), 22, GREY_B).next_to(ax.c2p(m, 0), DOWN, buff=0.15) for m in range(0, 23, 2)])
        xt = T("minutes", 22, GREY_B).next_to(ax.c2p(22, 0), DOWN, buff=0.55)
        cond = T("condition", 24, GREY_B).next_to(ax.c2p(0, 1), LEFT, buff=0.25)
        hd = M("for: 10m", 30, YELLOW_M).to_edge(UP, buff=0.6)
        self.beat("Now a puzzle. A rule says for ten minutes. The condition is true for eight minutes, false for one single check, then true again.",
                  Write(hd), Create(ax), FadeIn(xl), FadeIn(xt), FadeIn(cond), run_time=3.0)
        on1 = Rectangle(width=ax.c2p(8, 0)[0] - ax.c2p(0, 0)[0], height=0.6, stroke_width=0).set_fill(RED_M, 0.7).move_to(ax.c2p(4, 0.5))
        off = Rectangle(width=ax.c2p(8.25, 0)[0] - ax.c2p(8, 0)[0], height=0.6, stroke_width=0).set_fill(GREEN_M, 0.9).move_to(ax.c2p(8.125, 0.5))
        on2 = Rectangle(width=ax.c2p(22, 0)[0] - ax.c2p(8.25, 0)[0], height=0.6, stroke_width=0).set_fill(RED_M, 0.7).move_to(ax.c2p(15.125, 0.5))
        self.play(GrowFromEdge(on1, LEFT), run_time=1.0)
        self.play(FadeIn(off), run_time=0.3)
        self.play(GrowFromEdge(on2, LEFT), run_time=1.0)
        self.beat("When does it fire?", run_time=None)
        self.guess([0, -0.7, 0])
        st_y = -1.3
        lab_s = T("alert", 24, GREY_B).move_to([ax.c2p(0, 0)[0] - 0.65, st_y, 0])
        p1 = Rectangle(width=ax.c2p(8, 0)[0] - ax.c2p(0, 0)[0], height=0.5, stroke_width=0).set_fill(GOLD_M, 0.75).move_to([ax.c2p(4, 0)[0], st_y, 0])
        p1t = T("pending", 24, BLACK).move_to(p1).set_z_index(2)
        self.beat("While the condition is true, the alert is pending. The clock is running.",
                  FadeIn(lab_s), GrowFromEdge(p1, LEFT), FadeIn(p1t), run_time=2.4)
        r0 = T("back to zero", 24, GREEN_M).next_to([ax.c2p(8.1, 0)[0], st_y, 0], DOWN, buff=0.45)
        self.beat("Then one false check. The alert goes back to inactive, and the clock goes back to zero. Eight minutes, gone.",
                  p1.animate.set_fill(GREY_D, 0.6), FadeIn(r0, shift=UP * 0.1), run_time=2.2)
        p2 = Rectangle(width=ax.c2p(18.25, 0)[0] - ax.c2p(8.25, 0)[0], height=0.5, stroke_width=0).set_fill(GOLD_M, 0.75).move_to([ax.c2p(13.25, 0)[0], st_y, 0])
        p2t = T("pending again: 10 minutes", 24, BLACK).move_to(p2).set_z_index(2)
        f1 = Rectangle(width=ax.c2p(22, 0)[0] - ax.c2p(18.25, 0)[0], height=0.5, stroke_width=0).set_fill(RED_M, 0.85).move_to([ax.c2p(20.125, 0)[0], st_y, 0])
        f1t = T("firing", 24, BLACK).move_to(f1).set_z_index(2)
        self.beat("It starts again, and fires ten minutes after the condition became true again. Not at minute ten. At about minute eighteen.",
                  GrowFromEdge(p2, LEFT), FadeIn(p2t), Succession(Wait(1.4), AnimationGroup(GrowFromEdge(f1, LEFT), FadeIn(f1t))), run_time=3.4)
        states = T("inactive  ->  pending  ->  firing", 28, GOLD_M).move_to([0, -2.7, 0])
        self.beat("Three states: inactive, pending, firing. And that is the whole point of the wait. It filters out alerts that flip on and off.",
                  Write(states), run_time=2.4)
        self.beat("A good bedside monitor does the same: it waits a few seconds, so a patient turning over in bed does not set it off.",
                  run_time=None)
        self.play(FadeOut(VGroup(ax, xl, xt, cond, hd, on1, off, on2, lab_s, p1, p1t, r0, p2, p2t, f1, f1t, states)), run_time=0.6)

        # ---------------- 4. the flood, and the station
        PC = np.array([-4.6, 0.3, 0])
        prom = frame(2.6, 1.0, GOLD_M, PC, fill=0.16)
        prom_t = T("Prometheus", 28).move_to(prom).set_z_index(2)
        prom_n = T("decides: does it fire?", 22, GOLD_M).next_to(prom, DOWN, buff=0.2)
        self.beat("So the monitors can beep. But Prometheus only decides that an alert fires. It never sends a message to a person itself.",
                  GrowFromCenter(prom), Write(prom_t), FadeIn(prom_n), run_time=2.4)
        AC = np.array([0.2, 0.3, 0])
        am = frame(3.0, 3.6, TEAL_M, AC, fill=0.08)
        am_t = T("Alertmanager", 28, TEAL_M).move_to(am.get_top() + DOWN * 0.4)
        am_n = T("the nurses' station", 22, GREY_B).next_to(am_t, DOWN, buff=0.1)
        pg = frame(2.2, 0.9, RED_M, [4.9, 1.4, 0], fill=0.16)
        pg_t = M("pager", 26).move_to(pg).set_z_index(2)
        tk = frame(2.2, 0.9, BLUE_M, [4.9, -0.8, 0], fill=0.16)
        tk_t = M("tickets", 26).move_to(tk).set_z_index(2)
        self.beat("Firing alerts go to a separate service, Alertmanager. It is our nurses' station.", Create(am), Write(am_t), FadeIn(am_n), run_time=2.0)
        self.beat("And from there to receivers, the places messages land. In the lab, one for pages, and one for tickets.",
                  GrowFromCenter(pg), Write(pg_t), GrowFromCenter(tk), Write(tk_t), run_time=2.0)
        a_in = Arrow(prom.get_right(), am.get_left(), buff=0.1, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.15)
        a_pg = Arrow(am.get_right() + UP * 0.6, pg.get_left(), buff=0.1, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.15)
        a_tk = Arrow(am.get_right() + DOWN * 0.6, tk.get_left(), buff=0.1, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.15)
        self.play(GrowArrow(a_in), GrowArrow(a_pg), GrowArrow(a_tk), run_time=0.8)
        main = VGroup(prom, prom_t, prom_n, am, am_t, am_n, pg, pg_t, tk, tk_t, a_in, a_pg, a_tk)

        # grouping
        many = VGroup(*[Dot(radius=0.07, color=RED_M) for _ in range(12)])
        def stream(n):
            return LaggedStart(*[Succession(FadeIn(d.move_to(a_in.get_start()), run_time=0.05), d.animate(run_time=0.6).move_to(am.get_center() + DOWN * 0.3), FadeOut(d, run_time=0.1)) for d in VGroup(*[Dot(radius=0.07, color=RED_M) for _ in range(n)])], lag_ratio=0.15)
        g1 = T("grouping", 26, TEAL_M).move_to(AC + UP * 0.1)
        self.beat("One broken database can trip dozens of rules at once, and Prometheus re-sends each firing alert about once a minute. Straight to a phone, that is a flood.",
                  stream(14), run_time=3.2)
        msg = lchip("1 message", RED_M, 22).move_to(a_pg.get_center() + UP * 0.45)
        self.beat("So the station's first job is grouping. Alerts that share the same labels become one message. Twenty beds, one power flicker.",
                  FadeIn(g1), stream(10), Succession(Wait(1.6), FadeIn(msg, shift=RIGHT * 0.2)), run_time=3.6)
        g2 = T("routing", 26, TEAL_M).next_to(g1, DOWN, buff=0.15)
        r1 = M('severity="page"', 22, RED_M).next_to(a_pg, UP, buff=0.12).shift(LEFT * 0.0)
        r2 = M("everything else", 22, BLUE_M).next_to(a_tk, DOWN, buff=0.12)
        self.play(FadeOut(msg), run_time=0.3)
        self.beat("Second, routing. Each group walks down a tree of routes, matched on labels. Severity page goes to the pager. Everything else goes to tickets.",
                  FadeIn(g2), FadeIn(r1), FadeIn(r2), Succession(Wait(1.6), AnimationGroup(travel(a_pg, RED_M, 0.7), travel(a_tk, BLUE_M, 0.7))), run_time=3.4)
        self.beat("A heart alarm goes to the doctor. A broken drip goes on the morning list.", run_time=None)
        g3 = T("inhibition", 26, TEAL_M).next_to(g2, DOWN, buff=0.15)
        g4 = T("silences", 26, TEAL_M).next_to(g3, DOWN, buff=0.15)
        self.beat("Third, inhibition. While a page fires for a job, the lab mutes that job's ticket alerts. Small alarms stay quiet while a team is at the bed.",
                  FadeIn(g3), run_time=2.2)
        self.beat("And fourth, silences. A mute you set for a while, with an author and a comment, for a planned procedure.", FadeIn(g4), run_time=1.8)

        # ---------------- 5. the lab outage, through the station
        self.play(FadeOut(VGroup(r1, r2)), run_time=0.3)
        out = T("lab: stop Redis, the app's small database", 24, GREY_B).to_edge(UP, buff=0.5)
        fa = lchip("FastBurn: page", RED_M, 22).move_to(PC + UP * 1.6)
        sa = lchip("SlowBurn: ticket", BLUE_M, 22).move_to(PC + DOWN * 1.35)
        self.beat("Now watch the lab's real outage. Stop Redis, the small database the app needs. Within a minute, both error budget alerts are pending.",
                  FadeIn(out), FadeIn(fa, shift=DOWN * 0.1), FadeIn(sa, shift=UP * 0.1), FadeOut(prom_n), run_time=2.6)
        fire = T("for: 2m passes: both fire", 22, GOLD_M).next_to(prom, UP, buff=0.12).shift(RIGHT * 0.0)
        self.beat("Two minutes later, both fire, and both reach the station.",
                  fa[0].animate.set_fill(dark(RED_M, 0.6)), sa[0].animate.set_fill(dark(BLUE_M, 0.6)), travel(a_in, GOLD_M, 0.8), run_time=2.0)
        line = M("[pager] FIRING HelloErrorBudgetFastBurn ... 4.52%", 22, RED_M).move_to([0.6, -2.85, 0])
        fit(line, 12.4)
        self.beat("Ten seconds later, the webhook in the lab prints one line. Only the page arrived.",
                  travel(a_pg, RED_M, 0.8), FadeIn(line, shift=UP * 0.1), run_time=2.2)
        sup = T("suppressed", 24, BLUE_M).next_to(tk, DOWN, buff=0.2)
        self.beat("The ticket was muted by inhibition.", Indicate(g3, color=TEAL_M), FadeIn(sup), sa.animate.set_opacity(0.4), run_time=2.0)
        self.wait(0.3)
        self.play(FadeOut(VGroup(out, fa, sa, line, sup)), run_time=0.5)

        # ---------------- 6. break it: the station follows its rules exactly
        self.beat("So far so good. But the station follows its rules exactly as written. A wrong route sends the page nowhere, and nobody at the desk notices.",
                  a_pg.animate.set_opacity(0.2), pg.animate.set_opacity(0.3), run_time=2.4)
        self.play(a_pg.animate.set_opacity(1), pg.animate.set_opacity(1), run_time=0.4)
        pg.set_fill(dark(RED_M, 0.16), opacity=1)
        self.play(FadeOut(main), FadeOut(VGroup(g1, g2, g3, g4)), run_time=0.5)
        t1 = VGroup(M("promtool test rules", 26, GREEN_M), T("made-up series in, the exact alerts expected out", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        t2 = VGroup(M("amtool config routes test severity=page", 26, GREEN_M), T("prints: pager", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        VGroup(t1, t2).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([0, 1.0, 0])
        self.beat("So test the alarms, the way hospitals do. promtool runs made-up series through your rules, and checks the exact alerts you expect.",
                  FadeIn(t1, shift=RIGHT * 0.1), run_time=2.2)
        stories = T("the lab tests three stories: app down, fast burn pages, slow leak opens a ticket", 24, GREY_B).next_to(t1, DOWN, buff=0.15).align_to(t1, LEFT)
        fit(stories, 12.4)
        self.play(t2.animate.shift(DOWN * 0.4), FadeIn(stories), run_time=0.6)
        self.beat("And amtool tests the routing tree. Ask it where a page goes, and it should say: pager.", FadeIn(t2, shift=RIGHT * 0.1), run_time=2.0)
        rr = T("An alert you have never seen fire is only a hope.", 32, YELLOW_M).to_edge(DOWN, buff=0.7)
        self.beat("An alert you have never seen fire is only a hope. Test it before it matters.", Write(rr), run_time=2.0)
        self.play(FadeOut(VGroup(t1, t2, stories, rr)), run_time=0.5)
        k1 = T("On Kubernetes, a ServiceMonitor says what to scrape.", 28).move_to([0, 2.0, 0])
        k2 = M("release: monitoring", 28, RED_M).next_to(k1, DOWN, buff=0.4)
        self.beat("One more silent trap, on Kubernetes. There, an object called a ServiceMonitor tells Prometheus what to scrape.",
                  FadeIn(k1), run_time=2.0)
        self.beat("The lab's Prometheus reads only those with the label release, monitoring. Leave it out. What happens? Pause and guess.",
                  FadeIn(k2), run_time=2.0)
        self.wait(2.0)
        k3 = T("nothing fails: no error, no event, and your app never shows up", 26, RED_M).next_to(k2, DOWN, buff=0.4)
        k4 = T("an alarm sheet dropped in the wrong tray", 26, GREY_B).next_to(k3, DOWN, buff=0.25)
        self.beat("Nothing fails. No error, no event, and your app simply never shows up. An alarm sheet, dropped in the wrong tray.",
                  FadeIn(k3), FadeIn(k4), run_time=2.4)
        k5 = T("after every apply, check that the target appears", 28, YELLOW_M).next_to(k4, DOWN, buff=0.45)
        self.beat("So after every apply, check that the target really appears.", Write(k5), run_time=1.6)
        self.play(FadeOut(VGroup(k1, k2, k3, k4, k5)), run_time=0.5)

        # ---------------- 7. guardrail checklist
        g = VGroup(T("does it fire on a symptom users feel?", 28), T("is its for: long enough to skip blips?", 28),
                   T("does it use rate(), never irate()?", 28), T("does the text say what is wrong, with a runbook link?", 28),
                   T("would the person paged know what to do next?", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.2)
        gt = T("Before you merge a new alert", 32, GOLD_M).next_to(g, UP, buff=0.45).align_to(g, LEFT)
        self.beat("Before you merge a new alert, ask five questions. Does it fire on a symptom users feel? Is its wait long enough to skip blips?",
                  Write(gt), FadeIn(g[0], shift=RIGHT * 0.1), FadeIn(g[1], shift=RIGHT * 0.1), run_time=3.0)
        self.beat("Does it use rate, never I rate? Does its text say what is wrong, and link to a runbook, a short page of first steps?",
                  FadeIn(g[2], shift=RIGHT * 0.1), FadeIn(g[3], shift=RIGHT * 0.1), run_time=3.0)
        self.beat("And would the person paged know what to do next?", FadeIn(g[4], shift=RIGHT * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(g, gt)), run_time=0.5)

        # ---------------- 8. moral, recap, check
        moral = T("Prometheus decides that an alert fires. Alertmanager decides who hears it.", 30, YELLOW_M).move_to(UP * 2.4)
        fit(moral, 12.6)
        self.beat("So the moral of the story. Prometheus decides that an alert fires. Alertmanager decides who hears about it.", Write(moral), run_time=2.2)
        rec = VGroup(T("a rule is a query with a name and a wait", 28, GOLD_M),
                     T("one false check sends the wait back to zero", 28, YELLOW_M),
                     T("the station groups, routes, mutes and silences", 28, TEAL_M),
                     T("test alarms before they matter", 28, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        self.beat("A rule is a query with a name and a wait, and one false check resets the wait. The station groups, routes, mutes and silences. And you test the alarms before they matter.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rec], lag_ratio=0.7), run_time=7.0)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.5)
        c1 = T("Quick check: fifty pods fail at the same moment,", 30).move_to(UP * 0.7)
        c2 = T("and their alerts share the same grouping labels. How many messages?", 30).next_to(c1, DOWN, buff=0.3)
        fit(c2, 12.6)
        self.beat("A quick check. Fifty pods fail at the same moment, and their alerts share the same grouping labels. How many messages reach a person?",
                  FadeIn(c1), FadeIn(c2), run_time=2.0)
        self.guess([0, -1.0, 0])
        ans = T("One. Fifty pods, one flicker, one message.", 30, GREEN_M).next_to(c2, DOWN, buff=0.6)
        self.beat("One. Fifty pods, one flicker, one message.", FadeIn(ans, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
