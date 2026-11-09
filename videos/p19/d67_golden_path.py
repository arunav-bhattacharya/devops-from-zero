import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bFinOps\b", "fin ops"), (r"\bKyverno\b", "Kai-verno"),
            (r"\bServiceAccounts?\b", lambda m: "service account" + ("s" if m.group(0).endswith("s") else "")),
            (r"\bServiceMonitor\b", "service monitor")])

ROAD = GOLD_M


def dark(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def polyline(*pts, color=YELLOW_M, sw=2):
    return VMobject(stroke_color=color, stroke_width=sw).set_points_as_corners([np.array([x, y, 0]) for x, y in pts])


def ride(pts, color=YELLOW_M, run_time=1.4):
    path = polyline(*pts)
    d = Dot(radius=0.1, color=color).move_to(path.get_start()).set_z_index(5)
    return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=smooth, run_time=run_time), FadeOut(d, run_time=0.15))


def pulse(rect, w=7, rt=0.45):
    b = rect.get_stroke_width()
    return Succession(rect.animate(run_time=rt).set_stroke(width=w), rect.animate(run_time=rt).set_stroke(width=b))


def card(lines, color, pad=0.26, align=LEFT):
    g = VGroup(*lines).arrange(DOWN, aligned_edge=align, buff=0.13)
    r = RoundedRectangle(corner_radius=0.12, width=g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.10), 1)
    g.move_to(r)
    for t in g:
        t.set_z_index(3)
    return VGroup(r, g)


def tile(seed):
    """One team's own setup: the same parts, in a slightly different order and shape."""
    rng = np.random.default_rng(seed)
    sq = RoundedRectangle(corner_radius=0.1, width=0.92, height=0.92, stroke_color=GREY_B, stroke_width=2).set_fill(dark(GREY_B, 0.08), 1)
    cols = [BLUE_M, TEAL_M, GREEN_M, YELLOW_M, PURPLE_M]
    rng.shuffle(cols)
    bars = VGroup()
    for i, c in enumerate(cols[:4]):
        w = rng.uniform(0.35, 0.72)
        bars.add(Rectangle(width=w, height=0.1, stroke_width=0).set_fill(c, 0.9))
    bars.arrange(DOWN, buff=0.08, aligned_edge=LEFT).move_to(sq).shift(LEFT * rng.uniform(0.0, 0.08))
    bars.set_z_index(2)
    return VGroup(sq, bars)


class D67GoldenPath(VoiceScene):
    def construct(self):
        self.title_card("The golden path", "a platform team, a paved road, and an owner for every cost")

        # ---------- 1. what one service needs, and 40 teams building it alone
        head = T("what hello-devops needs by now", 30).move_to([0, 3.0, 0])
        rows = [["Dockerfile", "2 workflows, pinned actions", "Kubernetes YAML"],
                ["Argo CD Application", "ServiceMonitor", "dashboard"],
                ["log shipping", "tracing", "policies", "secrets"]]
        cols = [BLUE_M, BLUE_M, TEAL_M, TEAL_M, YELLOW_M, YELLOW_M, YELLOW_M, YELLOW_M, PURPLE_M, PURPLE_M]
        items, k = VGroup(), 0
        for y, row in zip((1.5, 0.45, -0.6), rows):
            r = VGroup()
            for txt in row:
                r.add(chip(txt, cols[k], 24)); k += 1
            r.arrange(RIGHT, buff=0.3).move_to([0, y, 0])
            items.add(*r)
        self.beat("List what hello-devops needs by now. A Dockerfile, two workflows with pinned actions, Kubernetes YAML, and an Argo CD Application.",
                  FadeIn(head), Succession(Wait(1.6), LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in items[:4]], lag_ratio=0.6)), run_time=6.0)
        learned = T("you learned all of it in this course", 26, GREEN_M).move_to([0, -2.0, 0])
        self.beat("A ServiceMonitor, a dashboard, log shipping and tracing. Policies, and a way to get secrets. You learned all of it in this course.",
                  LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in items[4:]], lag_ratio=0.5), Succession(Wait(4.6), FadeIn(learned, shift=UP * 0.1)), run_time=6.4)

        xs = [-5.175 + 1.15 * c for c in range(10)]
        ys = [1.55, 0.4, -0.75, -1.9]
        tiles = VGroup(*[tile(i).move_to([xs[i % 10], ys[i // 10], 0]) for i in range(40)])
        head2 = T("40 product teams, each building it alone", 30).move_to([0, 3.0, 0])
        self.beat("Now picture 40 product teams, each building that alone.",
                  FadeOut(learned), Transform(head, head2), ReplacementTransform(items, tiles[0]),
                  Succession(Wait(1.2), LaggedStart(*[FadeIn(t, scale=0.7) for t in tiles[1:]], lag_ratio=0.05)), run_time=4.0)
        cnt = T("40 times, 40 slightly different ways", 26, YELLOW_M).move_to([0, -3.05, 0])
        oncall = chip("on call", RED_M, 22).move_to([-5.55, 2.4, 0])
        hops = [3, 17, 22, 9, 35, 28]
        self.beat("They solve the same problems 40 times, in 40 slightly different ways. And whoever is on call has to learn every one.",
                  FadeIn(cnt, shift=UP * 0.1),
                  Succession(Wait(3.6), FadeIn(oncall),
                             *[tiles[h][0].animate(run_time=0.5).set_stroke(RED_M, width=5) for h in hops]),
                  run_time=8.0)

        # ---------- 2. a platform team builds self-service
        self.play(FadeOut(VGroup(tiles, cnt, oncall, head)), run_time=0.7)
        teams = VGroup(*[box(n, BLUE_M, w=2.1, h=0.75, size=24).move_to([x, 2.3, 0]) for n, x in
                         zip(("web", "payments", "search", "mobile", "data"), (-5.2, -2.6, 0, 2.6, 5.2))])
        plat = RoundedRectangle(corner_radius=0.2, width=12.6, height=1.9, stroke_color=ROAD, stroke_width=3).set_fill(dark(ROAD, 0.10), 1).move_to([0, -2.45, 0])
        pl = T("internal developer platform", 26, ROAD).move_to(plat.get_top() + DOWN * 0.38).set_z_index(3)
        caps = VGroup(*[chip(t, ROAD, 22) for t in ("templates", "CI", "deploy", "dashboards", "guardrails")]).arrange(RIGHT, buff=0.35).move_to([0, -2.8, 0])
        for c in caps:
            c.set_z_index(3)
        self.beat("Most large companies answer this with platform engineering. A platform team builds an internal developer platform: the self-service capabilities that product teams use to build, ship and run software.",
                  LaggedStart(*[FadeIn(t, shift=DOWN * 0.1) for t in teams], lag_ratio=0.15),
                  Succession(Wait(2.6), AnimationGroup(FadeIn(plat), FadeIn(pl)), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in caps], lag_ratio=0.3)), run_time=9.0)
        downs = VGroup(*[Arrow(t.get_bottom(), [t.get_center()[0], plat.get_top()[1], 0], buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.06)
                         for t in teams])
        ss = T("self-service: no ticket, no week of waiting", 24, GREEN_M).move_to([0, 3.4, 0])
        self.beat("Self-service is the centre. A developer gets an environment, a database or a pipeline without filing a ticket and waiting a week.",
                  FadeIn(ss, shift=DOWN * 0.1), LaggedStart(*[GrowArrow(a) for a in downs], lag_ratio=0.12),
                  Succession(Wait(3.0), LaggedStart(*[travel(a, GREEN_M, run_time=0.8) for a in downs], lag_ratio=0.15)), run_time=6.4)
        ops = card([T("classic operations team", 24, RED_M), T("does the work for you, through tickets", 22)], RED_M, align=ORIGIN).move_to([-3.4, 0.0, 0])
        ptm = card([T("platform team", 24, GREEN_M), T("builds things, so you do the work", 22)], GREEN_M, align=ORIGIN).move_to([3.4, 0.0, 0])
        self.beat("A classic operations team does work for other teams, through tickets. A platform team builds things, so that other teams can do the work themselves.",
                  FadeOut(downs), FadeOut(ss), FadeIn(ops, shift=UP * 0.1), Succession(Wait(3.4), FadeIn(ptm, shift=UP * 0.1)), run_time=7.0)
        prod = VGroup(chip("run as a product", GREEN_M, 24), chip("developers are its customers", GREEN_M, 24)).arrange(RIGHT, buff=0.4).move_to([0, 0.45, 0])
        meas = VGroup(T("success = adoption and speed", 26, GREEN_M), T("not the number of tools installed", 26, RED_M)).arrange(RIGHT, buff=0.6).move_to([0, -0.5, 0])
        strike = Line(meas[1].get_left() + LEFT * 0.05, meas[1].get_right() + RIGHT * 0.05, stroke_color=RED_M, stroke_width=3)
        self.beat("It runs the platform as a product, with developers as its customers. It measures success by adoption and speed, never by the number of tools installed.",
                  FadeOut(ops), FadeOut(ptm), LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in prod], lag_ratio=0.5),
                  Succession(Wait(3.6), FadeIn(meas[0], shift=UP * 0.1), Wait(0.8), FadeIn(meas[1], shift=UP * 0.1), Create(strike)), run_time=8.0)

        # ---------- 3. the golden path
        self.play(FadeOut(VGroup(teams, plat, pl, caps, prod, meas, strike)), run_time=0.7)
        RX0, RX1, RY = -3.6, 4.0, -0.15
        e1 = Line([RX0, RY + 0.6, 0], [RX1, RY + 0.6, 0], stroke_color=ROAD, stroke_width=4)
        e2 = Line([RX0, RY - 0.6, 0], [RX1, RY - 0.6, 0], stroke_color=ROAD, stroke_width=4)
        mid = DashedLine([RX0, RY, 0], [RX1, RY, 0], dash_length=0.25, stroke_width=3, color=ROAD).set_opacity(0.6)
        road = VGroup(e1, e2, mid)
        gh = T("the golden path, or paved road", 30, ROAD).move_to([0, 3.0, 0])
        prodn = chip("production", GREEN_M, 24).move_to([5.75, RY, 0])
        self.beat("The platform's main product is the golden path, which some companies call the paved road. It is a supported, ready-made way to do a common job.",
                  FadeIn(gh), Create(e1), Create(e2), Create(mid), Succession(Wait(3.4), FadeIn(prodn, shift=LEFT * 0.1)), run_time=7.0)
        form = card([T("new service", 22, ROAD), M("name: payments-api", 20), M("team: web", 20, YELLOW_M)], ROAD).move_to([-5.3, RY, 0])
        self.beat("The classic one is create a new service. You fill in a name and a team.",
                  FadeIn(form, shift=RIGHT * 0.1), Succession(Wait(2.4), Indicate(form[1][2], color=YELLOW_M, scale_factor=1.08)), run_time=4.0)
        ms_up = VGroup(chip("Dockerfile", BLUE_M, 22).move_to([-2.75, 1.3, 0]), chip("release workflow", BLUE_M, 22).move_to([-0.15, 1.3, 0]),
                       chip("Argo CD Application", TEAL_M, 22).move_to([2.95, 1.3, 0]))
        ms_dn = VGroup(chip("CI", BLUE_M, 22).move_to([-2.75, -1.6, 0]), chip("Kubernetes YAML", TEAL_M, 22).move_to([-0.15, -1.6, 0]),
                       chip("dashboard", YELLOW_M, 22).move_to([2.95, -1.6, 0]))
        order = [ms_up[0], ms_dn[0], ms_up[1], ms_dn[1], ms_up[2], ms_dn[2]]
        self.beat("You get a repository with a Dockerfile, CI, a release workflow, Kubernetes YAML, an Argo CD Application and a dashboard, already wired together.",
                  LaggedStart(*[FadeIn(m, shift=(DOWN if m in ms_up else UP) * 0.1) for m in order], lag_ratio=0.45),
                  Succession(Wait(5.4), ride([(RX0, RY), (RX1 + 0.6, RY)], ROAD, run_time=1.6)), run_time=7.4)
        comp = chip("compliant: the easy way is the safe way", GREEN_M, 22).move_to([-3.2, 2.15, 0])
        test = chip("tested: starts with current versions", GREEN_M, 22).move_to([3.3, 2.15, 0])
        self.beat("Each path makes two promises. Compliant: security and policy are built in, so the easy way is also the safe way.",
                  Succession(Wait(2.0), FadeIn(comp, shift=DOWN * 0.1)), run_time=6.0)
        self.beat("Tested: the platform team keeps the template working, so a new service starts with current versions.",
                  FadeIn(test, shift=DOWN * 0.1), run_time=5.0)

        # portal: the shop front
        self.play(FadeOut(VGroup(ms_up, ms_dn, comp, test)), run_time=0.6)
        portal = box("developer portal: Backstage", PURPLE_M, w=6.2, h=0.8, size=26).move_to([0, 2.15, 0])
        portal[1].set_z_index(3)
        pparts = VGroup(*[chip(t, PURPLE_M, 22) for t in ("software catalog", "templates", "docs", "plugins")]).arrange(RIGHT, buff=0.3).move_to([0, 1.25, 0])
        front = T("shop front", 22, PURPLE_M).next_to(portal, LEFT, buff=0.3)
        self.beat("Developers find these paths through a developer portal. Backstage is the best-known framework for building one, with a software catalog, templates, docs and plugins.",
                  DrawBorderThenFill(portal[0]), Write(portal[1]), Succession(Wait(3.6), LaggedStart(*[FadeIn(p, shift=DOWN * 0.1) for p in pparts], lag_ratio=0.4)), run_time=8.0)
        shop = box("the platform: templates, pipelines, clusters", ROAD, w=7.6, h=0.8, size=24).move_to([0.2, -1.75, 0])
        shop[1].set_z_index(3)
        behind = T("the shop", 22, ROAD).next_to(shop, LEFT, buff=0.3)
        self.beat("But Backstage is only the shop front. The platform is the shop behind it: the templates, pipelines and clusters.",
                  FadeIn(front), Succession(Wait(1.8), AnimationGroup(DrawBorderThenFill(shop[0]), Write(shop[1]), FadeIn(behind))), run_time=5.0)

        # ---------- 4. guardrails ride on the path
        self.play(FadeOut(VGroup(portal, pparts, front, shop, behind)), run_time=0.6)
        gr_up = VGroup(*[chip(t, GREEN_M, 21) for t in ("pinned actions", "signed image + SBOM", "own ServiceAccount")]).arrange(RIGHT, buff=0.2).move_to([0.45, 1.25, 0])
        gr_dn = VGroup(*[chip(t, GREEN_M, 21) for t in ("Kyverno policies", "team label", "dashboard and alerts")]).arrange(RIGHT, buff=0.2).move_to([0.45, -1.55, 0])
        grh = T("guardrails, built into the path", 26, GREEN_M).move_to([0, 2.3, 0])
        self.beat("The guardrails come with the path. A new service starts with pinned actions, a signed image with an SBOM, its own ServiceAccount, the Kyverno policies, and a dashboard with alerts.",
                  FadeIn(grh), e1.animate.set_stroke(GREEN_M, width=6), e2.animate.set_stroke(GREEN_M, width=6),
                  Succession(Wait(2.4), LaggedStart(*[FadeIn(g, shift=DOWN * 0.1) for g in gr_up], lag_ratio=0.5),
                             LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in gr_dn], lag_ratio=0.5)), run_time=9.0)
        wall = Line([4.4, -2.55, 0], [4.4, 0.6, 0], stroke_color=PURPLE_M, stroke_width=6)
        wl = T("cluster: the same rules for everyone", 22, PURPLE_M).move_to([3.2, -3.05, 0])
        off = [(RX0, RY), (-3.42, RY), (-3.42, -2.25), (4.35, -2.25)]
        self.beat("Teams may still leave the path, when they have a good reason. But the cluster enforces the same rules for everyone, so a team that leaves the path still meets them.",
                  Create(wall), FadeIn(wl), Succession(Wait(2.0), ride(off, BLUE_M, run_time=2.2), pulse(wall, w=10)), run_time=6.6)
        fbot = form[0].get_bottom()[1]
        fb = polyline((-3.42, -2.25), (-5.3, -2.25), (-5.3, fbot - 0.1), color=YELLOW_M, sw=3)
        fbt = Arrow([-5.3, fbot - 0.4, 0], [-5.3, fbot - 0.05, 0], buff=0, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.5)
        wrong = T("many teams leave?  then the path is wrong", 28, YELLOW_M).move_to([0, 3.0, 0])
        self.beat("And if many teams leave the path, the path is wrong. That is the most useful feedback a platform team gets.",
                  FadeOut(grh), FadeOut(gh), LaggedStart(ride(off[:3], BLUE_M, run_time=1.0), ride(off[:3], BLUE_M, run_time=1.0), ride(off[:3], BLUE_M, run_time=1.0), lag_ratio=0.3),
                  Succession(Wait(1.6), AnimationGroup(FadeIn(wrong, shift=DOWN * 0.1), Create(fb), GrowArrow(fbt)), pulse(form[0])), run_time=5.6)

        # ---------- 5. FinOps: every cost gets an owner
        self.play(FadeOut(VGroup(road, form, prodn, gr_up, gr_dn, wall, wl, fb, fbt, wrong)), run_time=0.8)
        bill = card([T("cloud bill", 26), T("owner:  ?", 26, RED_M)], GREY_B, align=ORIGIN).move_to([-3.4, 0.6, 0])
        bill[0].stretch_to_fit_width(3.6)
        one = M("$ one command", 22, GREY_B).move_to([-3.4, 2.2, 0])
        late = T("a month later, no names on it", 22, RED_M).next_to(bill, DOWN, buff=0.3)
        self.beat("One guardrail matters for money: the team label. In the cloud, any engineer can spend money with one command, and the bill arrives a month later, with no names on it.",
                  Succession(Wait(3.4), FadeIn(one, shift=DOWN * 0.1), Wait(1.0), FadeIn(bill, shift=DOWN * 0.1), FadeIn(late)), run_time=8.0)
        c0 = np.array([3.4, 0.6, 0])
        ph = [box(n, GREEN_M, w=1.9, h=0.62, size=24).move_to(on_circle(c0, 1.35, a)) for n, a in (("inform", 90), ("optimize", -30), ("operate", 210))]
        for p in ph:
            p[1].set_z_index(3)
        arcs = VGroup(*[CurvedArrow(on_circle(c0, 1.35, a0), on_circle(c0, 1.35, a1), angle=-np.radians(50), color=GREY_B, stroke_width=3)
                        for a0, a1 in ((55, 5), (-65, -115), (175, 125))])
        fo = T("FinOps", 26, GREEN_M).move_to(c0)
        self.beat("FinOps makes that cost visible, and shared between engineering, finance and the business. It loops through three phases: inform, optimize, operate.",
                  FadeIn(fo), Succession(Wait(4.0), LaggedStart(*[FadeIn(p, scale=0.8) for p in ph], lag_ratio=0.5), Create(arcs)), run_time=8.0)
        own = T("until a cost has an owner, every saving is a guess", 26, YELLOW_M).move_to([0, -2.3, 0])
        self.beat("Everything starts with allocation. Until a cost has an owner, every saving is a guess. In Kubernetes, the owner is a label on each workload.",
                  pulse(ph[0][0]), FadeOut(late), FadeIn(own, shift=UP * 0.1), Succession(Wait(4.2), Transform(bill[1][1], T("owner:  team web", 26, YELLOW_M).move_to(bill[1][1]))),
                  run_time=7.0)

        # node price split by requests
        self.play(FadeOut(VGroup(bill, one, own, fo, arcs, *ph)), run_time=0.7)
        nh = T("one node's price, split by what each Pod requests", 26).move_to([0, 3.0, 0])
        X0, W, BY = -5.5, 11.0, 1.0
        shares = [("web", 0.30, BLUE_M), ("payments", 0.25, TEAL_M), ("search", 0.20, PURPLE_M), ("idle", 0.25, GREY_B)]
        outline = Rectangle(width=W, height=0.85, stroke_color=GREY_B, stroke_width=2).move_to([0, BY, 0])
        segs, x = VGroup(), X0
        for name, f, c in shares:
            r = Rectangle(width=W * f, height=0.85, stroke_color=BLACK, stroke_width=2).set_fill(c, 0.75 if name != "idle" else 0.35)
            r.move_to([x + W * f / 2, BY, 0]); x += W * f
            segs.add(VGroup(r, T(name, 24, WHITE).move_to(r).set_z_index(3)))
        podrow = VGroup()
        for (name, f, c), sg in zip(shares[:3], segs):
            n = max(1, int(round(f * 10)))
            ds = VGroup(*[Circle(radius=0.2, stroke_color=c, stroke_width=3).set_fill(dark(c, 0.3), 1) for _ in range(n)]).arrange(RIGHT, buff=0.14)
            ds.move_to([sg.get_center()[0], 2.05, 0])
            podrow.add(ds)
        self.beat("A cost tool gives each Pod a share of its node's price, based on the CPU and memory it requests, or uses if that is more. Then it adds up the shares by label.",
                  FadeIn(nh), Create(outline), LaggedStart(*[FadeIn(p, shift=DOWN * 0.1) for p in podrow], lag_ratio=0.3),
                  Succession(Wait(4.4), LaggedStart(*[FadeIn(s) for s in segs[:3]], lag_ratio=0.5)), run_time=8.6)
        idl = T("nobody requested this", 22, GREY_B).next_to(segs[3], DOWN, buff=0.2)
        self.beat("Capacity that nobody requested still appears on the bill. It shows as idle. Give that line an owner too, usually the platform team.",
                  Succession(FadeIn(segs[3]), Wait(1.0), FadeIn(idl, shift=UP * 0.1), Wait(1.6),
                                              Transform(segs[3][1], T("idle: platform", 22, WHITE).move_to(segs[3][0]).set_z_index(3))), run_time=6.4)
        # showback: the shares become a report per team
        base_y, hmax = -3.0, 2.4
        bx = [-4.2, -1.4, 1.4, 4.2]
        bars, blabs = VGroup(), VGroup()
        for (name, f, c), x_ in zip(shares, bx):
            h = hmax * f / 0.30
            bars.add(Rectangle(width=1.5, height=h, stroke_width=0).set_fill(c, 0.75 if name != "idle" else 0.35).move_to([x_, base_y + h / 2, 0]))
            blabs.add(T("platform (idle)" if name == "idle" else name, 22).move_to([x_, base_y - 0.3, 0]))
        sbh = T("showback: each team sees its own cost", 24, YELLOW_M).move_to([0, 0.05, 0])
        self.beat("Then each team gets a report of what it used, while the money stays in a central budget. That is showback, and it comes first.",
                  FadeOut(idl), FadeIn(sbh), *[TransformFromCopy(s[0], b) for s, b in zip(segs, bars)], FadeIn(blabs), run_time=4.4)
        self.beat("Teams change what they run, once they see the numbers next to their own name.",
                  LaggedStart(*[Indicate(l, color=YELLOW_M) for l in blabs[:3]], lag_ratio=0.4), run_time=3.0)

        # unit cost
        self.play(FadeOut(VGroup(nh, outline, segs, podrow, bars, blabs, sbh)), run_time=0.7)
        uh = T("totals grow with the business: watch a unit cost", 28).move_to([0, 2.9, 0])
        r1 = VGroup(T("traffic", 28, BLUE_M), M("× 2", 30, BLUE_M)).arrange(RIGHT, buff=0.5)
        r2 = VGroup(T("bill", 28, RED_M), M("× 1.4", 30, RED_M)).arrange(RIGHT, buff=0.5)
        r3 = VGroup(T("cost per request", 28, GREEN_M), M("1.4 / 2 = 0.7", 30, GREEN_M)).arrange(RIGHT, buff=0.5)
        for r, y in zip((r1, r2, r3), (1.6, 0.7, -0.5)):
            r.move_to([0, y, 0])
        self.beat("Totals grow when the business grows, so a unit cost works better. If traffic doubles and the bill grows by 40 percent, each request got cheaper.",
                  FadeIn(uh), Succession(Wait(3.6), FadeIn(r1, shift=UP * 0.1), Wait(0.8), FadeIn(r2, shift=UP * 0.1), Wait(0.6), FadeIn(r3, shift=UP * 0.1)), run_time=8.0)
        inp = VGroup(M("hello_requests_total", 24, BLUE_M), T("+", 28), M("team: web", 24, YELLOW_M)).arrange(RIGHT, buff=0.4).move_to([0, -2.1, 0])
        inl = T("Prometheus counts the requests; the label says whose cost it is", 22, GREY_B).next_to(inp, DOWN, buff=0.25)
        self.beat("hello-devops already has both inputs. Prometheus counts its requests, and the team label says whose cost it is.",
                  FadeIn(inp, shift=UP * 0.1), Succession(Wait(1.4), FadeIn(inl)), run_time=5.0)

        # ---------- 6. the whole loop
        self.play(FadeOut(VGroup(uh, r1, r2, r3, inp, inl)), run_time=0.7)
        lh = T("one template, the same checks, every cost with an owner", 28).move_to([0, 2.7, 0])
        steps = [("Template", ROAD, "pinned, signed"), ("New repo", WHITE, "team label"), ("CI, policy", TEAL_M, "Kyverno, RBAC"),
                 ("Cluster", WHITE, "reserves requests"), ("Showback", GREEN_M, "cost per owner")]
        bxs = VGroup(*[box(n, c, w=2.0, h=0.8, size=24).move_to([x, 1.0, 0]) for (n, c, _), x in zip(steps, (-5.3, -2.65, 0, 2.65, 5.3))])
        for b in bxs:
            b[1].set_z_index(3)
        subs = VGroup(*[T(s, 20, GREY_B).next_to(b, DOWN, buff=0.15) for (_, _, s), b in zip(steps, bxs)])
        arr = VGroup(*[Arrow(bxs[i].get_right(), bxs[i + 1].get_left(), buff=0.06, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.45)
                       for i in range(4)])
        self.beat("Put it together. The template creates a repository with a team label. CI and policy check it. It runs on the cluster, which reserves its requests. And showback shows the cost per owner.",
                  FadeIn(lh), LaggedStart(*[AnimationGroup(DrawBorderThenFill(b[0]), Write(b[1]), FadeIn(s)) for b, s in zip(bxs, subs)], lag_ratio=0.6),
                  Succession(Wait(3.0), LaggedStart(*[GrowArrow(a) for a in arr], lag_ratio=0.7)), run_time=10.0)
        loop = polyline((5.3, 0.15), (5.3, -1.0), (-5.3, -1.0), (-5.3, 0.1), color=YELLOW_M, sw=3)
        loopt = Arrow([-5.3, -0.3, 0], [-5.3, 0.15, 0], buff=0, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.5)
        lt = T("cost reports, and teams that leave the path, feed back into the template", 22, YELLOW_M).move_to([0, -1.4, 0])
        self.beat("Cost reports, and teams that leave the path, feed back into the template.",
                  Create(loop), GrowArrow(loopt), FadeIn(lt), Succession(Wait(1.6), ride([(5.3, 0.15), (5.3, -1.0), (-5.3, -1.0), (-5.3, 0.15)], YELLOW_M, run_time=1.8)),
                  run_time=4.4)
        rec = T("a self-service golden path, guardrails built in, a team label on every cost", 26, ROAD).move_to([0, -2.8, 0])
        self.beat("A platform team turns repeated work into a self-service golden path, with the guardrails built in, and a team label that gives every cost an owner.",
                  Succession(Wait(0.4), Write(rec)), Succession(Wait(2.0), *[ride([(bxs[i].get_center()[0], 1.0), (bxs[i + 1].get_center()[0], 1.0)], ROAD, run_time=0.6) for i in range(4)]),
                  run_time=7.0)
        self.wait(1.0)
