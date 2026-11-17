import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bFinOps\b", "fin ops"), (r"\bServiceMonitor\b", "service monitor"), (r"\bpayments-api\b", "payments A P I"),
            (r"\bcheck\.sh\b", "check dot S H"), (r"\bgit mv\b", "git move"), (r"\bOpenCost\b", "open cost"), (r"\bIDP\b", "I D P")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def term(lines, w=12.6, size=22):
    g = VGroup(*[M(t, size, c) for t, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    fit(g, w - 0.6)
    r = RoundedRectangle(corner_radius=0.1, width=w, height=g.height + 0.5, stroke_color=GREY_D, stroke_width=2).set_fill("#0b0b0b", 1)
    g.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.3)
    return VGroup(r, g)


def track(pts, c=GOLD_M, w=4):
    m = VMobject(stroke_color=c, stroke_width=w).set_points_smoothly([np.array([x, y, 0]) for x, y in pts])
    return m


class D67PavedPath(VoiceScene):
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
        self.title_card("Pave where people walk", "golden paths, and a name on every cost")

        # ---------- 1. the park
        lawn = RoundedRectangle(corner_radius=0.3, width=9.0, height=5.6, stroke_color=GREEN_M, stroke_width=2).set_fill(tint(GREEN_M, 0.12), 1).move_to([0, -0.2, 0])
        houses = VGroup(*[Square(0.55, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.2), 1).move_to([-5.6, 1.6 - 1.1 * i, 0]) for i in range(4)])
        hl = T("houses", 24, GREY_B).next_to(houses, DOWN, buff=0.2)
        stn = box("station", GREY_B, w=1.7, h=1.2, size=24).move_to([5.6, -0.2, 0])
        self.beat("Picture a town park, a wide lawn between the houses and the station.",
                  FadeIn(lawn), FadeIn(houses), FadeIn(hl), FadeIn(stn), run_time=2.0)
        mud = VGroup(*[track([(-5.3, 1.6 - 1.1 * i), (-2.0 + 0.7 * i, 0.9 - 0.9 * i + 0.3 * ((i * 7) % 3)), (1.6, -0.3 + 0.4 * ((i * 5) % 3 - 1)), (4.75, -0.2)], "#8B6B4A", 5) for i in range(4)])
        mud.add(track([(-5.3, 0.5), (-1.0, 2.2), (2.6, 1.0), (4.75, 0.0)], "#8B6B4A", 5), track([(-5.3, -0.6), (-0.5, -2.6), (3.0, -1.6), (4.75, -0.4)], "#8B6B4A", 5))
        self.beat("People cut across it. And soon, muddy tracks run in every direction.",
                  LaggedStart(*[Create(m) for m in mud], lag_ratio=0.3), run_time=3.0)
        sign = VGroup(Rectangle(width=3.4, height=0.8, stroke_color=RED_M, stroke_width=3).set_fill(BLACK, 1), T("Keep off the grass", 26, RED_M)).move_to([0, 2.95, 0])
        sign[1].move_to(sign[0])
        self.beat("The council puts up a sign. Keep off the grass. Nobody reads it.",
                  FadeIn(sign, shift=DOWN * 0.2), Succession(Wait(2.0), Wiggle(sign)), run_time=3.0)
        paved = VGroup(track([(-5.3, 1.6), (-1.5, 0.9), (1.6, -0.1), (4.75, -0.2)], GREY_B, 14), track([(-5.3, -1.7), (-1.0, -1.0), (1.6, -0.1)], GREY_B, 14))
        lamps = VGroup(*[Dot(radius=0.09, color=YELLOW_M).move_to(p) for p in ([-3.3, 1.55, 0], [-0.2, 0.8, 0], [3.0, 0.2, 0], [-3.0, -1.0, 0])])
        self.beat("The next spring, a new park keeper tries something else. Paved paths, exactly where the tracks were, with lights and benches.",
                  FadeOut(sign), LaggedStart(*[Create(p) for p in paved], lag_ratio=0.4), Succession(Wait(2.4), LaggedStart(*[GrowFromCenter(l) for l in lamps], lag_ratio=0.2)), run_time=4.4)
        self.beat("Within a month, the mud is gone. And nobody needed a sign.",
                  mud.animate.set_stroke(opacity=0.0), run_time=2.0)
        self.beat("Rules feel like the quick fix. A path people want to walk takes longer to build, and it works. So what has this to do with software?",
                  run_time=None)
        self.play(FadeOut(VGroup(lawn, houses, hl, stn, mud, paved, lamps)), run_time=0.6)

        # ---------- 2. what one app needs, times forty
        need = VGroup(*[chip(t, TEAL_M, 22) for t in ("Dockerfile", "2 workflows, pinned", "Kubernetes YAML", "Argo CD Application",
                                                       "ServiceMonitor", "dashboard", "log shipping", "tracing", "policies", "secrets")])
        need.arrange_in_grid(rows=5, cols=2, buff=(0.4, 0.25)).move_to([-3.4, 0.0, 0])
        nl = T("hello-devops needs:", 28, TEAL_M).next_to(need, UP, buff=0.3)
        self.beat("List what hello-devops needs by now. A Dockerfile and workflows, Kubernetes YAML and Argo CD, metrics, dashboards, logs, tracing, policies and secrets.",
                  FadeIn(nl), LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in need], lag_ratio=0.35), run_time=9.0)
        teams = VGroup(*[Square(0.32, stroke_color=GOLD_M, stroke_width=2).set_fill(tint(GOLD_M, 0.3), 1) for _ in range(40)]).arrange_in_grid(rows=5, cols=8, buff=0.14)
        teams.move_to([3.6, 0.0, 0])
        tl = T("40 teams", 28, GOLD_M).next_to(teams, UP, buff=0.3)
        self.beat("You learned all of it in this course. Now picture forty product teams, each building that alone.",
                  FadeIn(tl), LaggedStart(*[GrowFromCenter(t) for t in teams], lag_ratio=0.03), run_time=3.0)
        wob = [t.animate.rotate(0.35 * ((i * 7) % 5 - 2)).set_fill(tint([GOLD_M, RED_M, PURPLE_M, BLUE_M, GREEN_M][i % 5], 0.35), 1) for i, t in enumerate(teams)]
        self.beat("They solve the same problems forty ways, and whoever is on call learns every one. Muddy tracks.",
                  *wob, run_time=3.0)

        # the tempting fix, and why it stalls
        mand = VGroup(Rectangle(width=4.6, height=0.8, stroke_color=RED_M, stroke_width=3).set_fill(BLACK, 1), T("Standard pipeline: mandatory", 26, RED_M)).move_to([3.6, -2.6, 0])
        mand[1].move_to(mand[0])
        self.beat("The tempting fix is the sign: a mandatory standard. Teams use it because a manager said so, and look for ways around it.",
                  FadeIn(mand, shift=UP * 0.1), run_time=2.0)
        portal = box("a shiny portal", BLUE_M, w=3.4, size=26).move_to([-3.4, -2.6, 0])
        self.beat("Or buy a developer portal, a website listing every service. Picture one that, six months later, few teams use. Pause and guess: why?",
                  FadeIn(portal), run_time=2.4)
        self.wait(2.0)
        empty = T("little real self-service behind it", 24, BLUE_M).next_to(portal, UP, buff=0.2)
        self.beat("Usually because there was little real self-service behind it. A beautiful map of paths that don't exist. Nobody walks a map.",
                  FadeIn(empty), run_time=2.0)
        self.play(FadeOut(VGroup(need, nl, teams, tl, mand, portal, empty)), run_time=0.6)

        # ---------- 3. name it: platform engineering and the golden path
        pe = T("platform engineering", 34, GOLD_M).move_to([0, 2.8, 0])
        d1 = VGroup(T("a platform team builds self-service tools", 26), T("so product teams can ship by themselves", 26)).arrange(DOWN, buff=0.12).next_to(pe, DOWN, buff=0.3)
        self.beat("What works is the paved path. Most large companies call the work platform engineering. A platform team builds self-service tools, so product teams can ship by themselves.",
                  FadeIn(pe), FadeIn(d1), run_time=2.6)
        tick_ = T("ticket, wait a week", 26, RED_M).move_to([-3.4, 0.2, 0])
        ss = T("self-service: get it yourself, now", 26, GREEN_M).move_to([3.0, 0.2, 0])
        self.beat("Self-service means you get what you need yourself, at once. No ticket, no waiting a week for another team.",
                  FadeIn(tick_), Succession(Wait(1.6), AnimationGroup(FadeIn(ss), tick_.animate.set_opacity(0.3))), run_time=3.0)
        gp = box("golden path: \"create a new service\"", YELLOW_M, w=7.2, size=28).move_to([0, -1.3, 0])
        gpp = VGroup(chip("compliant: security built in", YELLOW_M, 22), chip("tested: kept working", YELLOW_M, 22)).arrange(RIGHT, buff=0.5).next_to(gp, DOWN, buff=0.35)
        self.beat("Its main product is the golden path, a ready-made way to do a common job, like create a new service. Two promises: compliant, with security built in, and tested, kept working.",
                  FadeIn(gp), Succession(Wait(5.0), LaggedStart(*[FadeIn(g) for g in gpp], lag_ratio=0.6)), run_time=8.0)
        self.beat("And the portal? That's the map at the park gate. Useful, but the platform is the paths themselves.",
                  run_time=None)
        self.play(FadeOut(VGroup(pe, d1, tick_, ss, gp, gpp)), run_time=0.6)

        # ---------- 4. show: hello-devops becomes a template
        t1 = term([("$ gh repo edit <your-github-user>/hello-devops --template", GREY_B),
                   ("$ grep -rl hello-devops k8s chart .github argocd | wc -l", GREY_B), ("27", YELLOW_M)], w=12.6).move_to([0, 2.2, 0])
        self.beat("Let's pave one. Mark hello-devops as a template. Then count the files that hard-code its name. Twenty-seven, in the core folders alone. Each one is a line a new team must change.",
                  FadeIn(t1[0]), FadeIn(t1[1][0]), Succession(Wait(2.6), AnimationGroup(FadeIn(t1[1][1]), FadeIn(t1[1][2]))), run_time=5.6)
        t2 = term([("$ gh repo create <your-github-user>/payments-api --template ... --clone", GREY_B),
                   ("$ grep -rl hello-devops ... | xargs sed -i '' 's/hello-devops/payments-api/g'", GREY_B),
                   ("$ grep -rl hello-devops --exclude-dir=.git . | wc -l", GREY_B), ("0", GREEN_M)], w=12.6).move_to([0, 0.0, 0])
        self.beat("Now play the new team. Create payments-api from the template, replace the old name everywhere, and check none is left. Zero.",
                  FadeIn(t2[0]), LaggedStart(*[FadeIn(l) for l in t2[1]], lag_ratio=0.5), run_time=4.0)
        self.beat("Run the same checks as the original. Pause and guess: all green?", run_time=None)
        self.wait(2.0)
        t3 = term([("$ ai/check.sh", GREY_B), ("PASS  pytest      PASS  kubeconform k8s/", GREEN_M), ("FAIL  helm lint", RED_M),
                   ("stat chart/payments-api/Chart.yaml: no such file or directory", RED_M)], w=12.6).move_to([0, -2.4, 0])
        self.beat("One fails, and it's a real template bug. The rename changed the chart inside its files, but not its folder.",
                  FadeIn(t3[0]), LaggedStart(*[FadeIn(l) for l in t3[1]], lag_ratio=0.4), run_time=3.0)
        fix = term([("$ git mv chart/hello-devops chart/payments-api", GREY_B), ("$ ai/check.sh | tail -1", GREY_B), ("8 passed, 0 failed, 0 skipped", GREEN_M)], w=12.6).move_to(t3)
        self.beat("Fix it, and fix the template too. Eight passed. That failure was a fresh muddy track, showing where a path was missing.",
                  Transform(t3, fix), run_time=2.0)
        self.play(FadeOut(VGroup(t1, t2, t3)), run_time=0.6)

        # ---------- 5. FinOps: every cost gets an owner
        bill = VGroup(Rectangle(width=3.2, height=1.6, stroke_color=GREY_B, stroke_width=3).set_fill(tint(GREY_B, 0.1), 1), T("one cloud bill", 26), T("no names on it", 22, RED_M))
        bill[1].move_to(bill[0].get_center() + UP * 0.3); bill[2].move_to(bill[0].get_center() + DOWN * 0.35)
        bill.move_to([-4.2, 1.6, 0])
        self.beat("Paths carry one more thing: the bill. The park pays one water bill, and nobody knows which bed drinks most. A cloud bill arrives with no names on it.",
                  FadeIn(bill), run_time=2.4)
        fo = VGroup(T("FinOps", 32, GREEN_M), T("make cost visible, and give it owners", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([2.4, 1.6, 0])
        self.beat("FinOps makes that cost visible, and it starts with an owner for every cost. In Kubernetes, a team label on every workload.",
                  FadeIn(fo), run_time=2.4)
        NX, NW, NH = -4.4, 8.8, 1.0
        nodeb = Rectangle(width=NW, height=NH, stroke_color=WHITE, stroke_width=3).move_to([NX + NW / 2, -0.9, 0])
        nl2 = T("one node: its full price", 24, GREY_B).next_to(nodeb, UP, buff=0.15).align_to(nodeb, LEFT)
        parts = (("team: web", 0.35, BLUE_M), ("team: data", 0.25, PURPLE_M), ("team: pay", 0.15, GOLD_M))
        segs = VGroup(); x = NX
        for lab, f, c in parts:
            r = Rectangle(width=NW * f - 0.04, height=NH - 0.1, stroke_width=0).set_fill(tint(c, 0.55), 1).move_to([x + NW * f / 2, -0.9, 0])
            segs.add(VGroup(r, T(lab, 22, WHITE).move_to(r)))
            x += NW * f
        idle = Rectangle(width=NW * 0.25 - 0.04, height=NH - 0.1, stroke_color=GREY_B, stroke_width=1.5).set_fill(BLACK, 1).move_to([x + NW * 0.125, -0.9, 0])
        idlel = T("idle", 22, GREY_B).move_to(idle)
        self.beat("A cost tool splits each node's price between its Pods, by what they request, or use if that's more, then adds up by label.",
                  Create(nodeb), FadeIn(nl2), LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in segs], lag_ratio=0.5), run_time=4.4)
        self.beat("Why requests? Because the scheduler reserves them. You pay for what you set aside, even when the CPUs sit idle.",
                  Indicate(segs[0][1], color=WHITE), run_time=1.6)
        self.beat("And the line people forget: capacity nobody requested still costs money. That's idle cost, sprinklers watering an empty field. Give it an owner too.",
                  FadeIn(idle), FadeIn(idlel), Succession(Wait(3.0), Indicate(idlel, color=WHITE)), run_time=4.4)
        sb = T("showback: each team sees its own share; the money stays central", 24, GREEN_M).move_to([0, -2.4, 0])
        fit(sb, 12.4)
        self.beat("Show each team its share while the money stays central. That's showback, and it comes first.",
                  FadeIn(sb, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(VGroup(bill, fo, nodeb, nl2, segs, idle, idlel, sb)), run_time=0.6)

        # predict: unit cost
        tr = VGroup(T("traffic", 28), M("x 2", 34, TEAL_M)).arrange(RIGHT, buff=0.4).move_to([-3.2, 1.6, 0])
        bl2 = VGroup(T("bill", 28), M("+ 40%", 34, RED_M)).arrange(RIGHT, buff=0.4).move_to([3.2, 1.6, 0])
        self.beat("Totals grow with the business, so try this. Traffic doubles, and the bill grows forty percent. Did each request get cheaper, or dearer? Pause and guess.",
                  FadeIn(tr), Succession(Wait(5.0), FadeIn(bl2)), run_time=6.0)
        self.wait(2.0)
        calc = M("1.4 / 2 = 0.7", 40, YELLOW_M).move_to([0, 0.0, 0])
        cl = T("cost per request fell by about 30%", 30, GREEN_M).move_to([0, -1.2, 0])
        self.beat("Cheaper. One point four times the cost, for two times the requests, is zero point seven. The bill went up, and each request got about thirty percent cheaper.",
                  Write(calc), Succession(Wait(3.4), FadeIn(cl)), run_time=4.4)
        self.beat("That's a unit cost, and hello-devops already has both inputs. Prometheus counts its requests, and the team label says whose they are.",
                  run_time=None)
        self.play(FadeOut(VGroup(tr, bl2, calc, cl)), run_time=0.6)

        # ---------- 6. guardrails: the limit is the size of the problem
        g = VGroup(T("one repo, one team: a template repository is enough", 26),
                   T("a portal pays off with many teams", 26),
                   T("a cost tool is useless until workloads carry owner labels", 26),
                   T("many teams leave the path? the path is wrong", 26, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([0, 0.3, 0])
        self.beat("The honest limits: each tool solves a pain you feel only at some size. One team? A template repository is enough. A portal pays off with many teams. A cost tool needs owner labels first.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in g[:3]], lag_ratio=0.8), run_time=8.0)
        self.beat("And watch where people leave the path. If many teams do, the path is wrong. That's the most useful feedback a platform team gets.",
                  FadeIn(g[3], shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(g), run_time=0.6)

        # ---------- 7. moral and a quick check
        mor = VGroup(T("Build the path people already want to walk.", 30),
                     T("a rule alone won't keep them on it", 28, RED_M),
                     T("golden path: self-service, compliant, tested", 28, YELLOW_M),
                     T("every cost gets an owner; idle gets one too", 28, GREEN_M),
                     T("watch the cost per request, not the total", 28, TEAL_M)).arrange(DOWN, buff=0.35)
        self.beat("The moral of the story: build the path people want to walk. A rule alone won't keep them on it. Self-service, compliant, tested. Every cost gets an owner, idle too. And watch cost per request.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mor], lag_ratio=0.8), run_time=9.0)
        self.play(FadeOut(mor), run_time=0.6)
        q = VGroup(T("Your cluster bill doubled,", 30), T("and nobody knows which team caused it.", 30),
                   T("Which FinOps step comes first?", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 0.8, 0])
        self.beat("One quick check. Your cluster bill doubled, and nobody knows which team caused it. Which FinOps step comes first? Pause and think.",
                  LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in q], lag_ratio=0.5), run_time=3.6)
        self.wait(2.0)
        ans = chip("label every workload with its owning team", GREEN_M, 28).move_to([0, -1.5, 0])
        self.beat("Label every workload with its owning team. Until a cost has an owner, every saving is a guess. Thanks for watching.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.6)
        self.wait(1.0)
