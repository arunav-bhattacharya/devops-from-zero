import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bdepends_on\b", "depends on"), (r"\bservice_healthy\b", "service healthy"), (r"\bcompose\.yaml\b", "compose dot yammel"),
            (r"\bredis-cli\b", "redis C L I"), (r"\bREDIS_HOST\b", "redis host"), (r"\bdown -v\b", "down dash V")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def cylinder(color=GREEN_M, w=1.5, h=1.0):
    top = Ellipse(width=w, height=0.36, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), opacity=1)
    body = Rectangle(width=w, height=h, stroke_width=0).set_fill(tint(color, 0.14), opacity=1)
    bot = Ellipse(width=w, height=0.36, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.14), opacity=1)
    top.move_to(body.get_top()); bot.move_to(body.get_bottom())
    sides = VGroup(Line(body.get_corner(UL), body.get_corner(DL)), Line(body.get_corner(UR), body.get_corner(DR))).set_stroke(color, 3)
    return VGroup(bot, body, sides, top)


def station(name, color, w=2.2, h=1.1):
    r = RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), opacity=1)
    return VGroup(r, M(name, 26, color).move_to(r))


def yaml(lines, x0=-6.3, y0=2.6, dy=0.4, size=22):
    g = VGroup()
    for i, (ind, txt, col) in enumerate(lines):
        m = M(txt, size, col)
        m.move_to([x0 + ind * 0.32, y0 - i * dy, 0], aligned_edge=LEFT)
        g.add(m)
    return g


YL = {"services": (0, "services:", BLUE_M), "web": (1, "web:", GOLD_M), "build": (2, "build: .", WHITE), "ports": (2, "ports:", WHITE),
      "p8000": (3, '- "8000:8000"', WHITE), "env": (2, "environment:", WHITE), "rh": (3, "REDIS_HOST: redis", TEAL_M),
      "dep_s": (2, "depends_on: [redis]", PURPLE_M), "dep": (2, "depends_on:", PURPLE_M), "dep_r": (3, "redis:", PURPLE_M),
      "dep_c": (4, "condition: service_healthy", PURPLE_M), "redis": (1, "redis:", RED_M), "image": (2, "image: redis:8-alpine", WHITE),
      "vols": (2, "volumes:", WHITE), "rd": (3, "- redis-data:/data", GREEN_M), "hc": (2, "healthcheck:", RED_M),
      "hc_t": (3, 'test: ["CMD", "redis-cli", "ping"]', RED_M), "hc_i": (3, "interval: 5s", RED_M), "hc_o": (3, "timeout: 3s", RED_M),
      "hc_r": (3, "retries: 5", RED_M), "volumes": (0, "volumes:", BLUE_M), "rdata": (1, "redis-data:", GREEN_M)}
BASE = ["services", "web", "build", "ports", "p8000", "env", "rh", "redis", "image", "vols", "rd", "volumes", "rdata"]


def rtext(items, top=3.15, size=26, x=1.0, buff=0.1):
    """Short lines stacked in the right half of the frame, left edge at x, top edge at top."""
    g = VGroup(*[T(t, size, c) for t, c in items]).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return g.move_to([x, top, 0], aligned_edge=UL)


class D21KitchenPlan(VoiceScene):
    def lay(self, keys, x0=-6.3, y0=3.05, dy=0.305):
        """Animations that move the shown YAML lines into the order of keys, fading new lines in and old ones out."""
        if not hasattr(self, "ym"):
            self.ym = {}
        anims = []
        for i, k in enumerate(keys):
            ind, txt, col = YL[k]
            pos = np.array([x0 + ind * 0.28, y0 - i * dy, 0])
            if k in self.ym:
                anims.append(self.ym[k].animate.move_to(pos, aligned_edge=LEFT))
            else:
                m = M(txt, 22, col).move_to(pos, aligned_edge=LEFT)
                self.ym[k] = m
                anims.append(FadeIn(m, shift=RIGHT * 0.1))
        for k in [k for k in self.ym if k not in keys]:
            anims.append(FadeOut(self.ym.pop(k)))
        return anims

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
        self.title_card("The plan on the kitchen wall", "Docker Compose: one file, one command, and ready before running")

        # 1. opening a kitchen by phone
        you = Circle(radius=0.3, stroke_color=WHITE, stroke_width=3).set_fill(tint(WHITE, 0.2), opacity=1).move_to([-5.2, 0.3, 0])
        yl = T("you, on the phone", 26, GREY_B).next_to(you, DOWN, buff=0.2)
        cooks = VGroup(*[Circle(radius=0.26, stroke_color=c, stroke_width=3).set_fill(tint(c, 0.25), opacity=1).move_to([2.2, y, 0]) for c, y in ((RED_M, 1.6), (GOLD_M, 0.3), (GREEN_M, -1.0))])
        orders = VGroup(T("light the oven", 26, RED_M), T("now start the sauce", 26, GOLD_M), T("now open the pantry", 26, GREEN_M))
        for o, c in zip(orders, cooks):
            o.next_to(c, RIGHT, buff=0.3)
        lines = VGroup(*[DashedLine(you.get_right(), c.get_left(), dash_length=0.1, stroke_width=2, color=GREY_B) for c in cooks])
        self.steps("Picture opening a small restaurant kitchen every morning by phoning each cook with orders. Light the oven. Now start the sauce. Now open the pantry.",
                   (0.6, FadeIn(you), FadeIn(yl), FadeIn(cooks)), (2.4, Wait(2.4)), (0.6, Create(lines[0]), FadeIn(orders[0])), (0.6, Create(lines[1]), FadeIn(orders[1])), (0.6, Create(lines[2]), FadeIn(orders[2])))
        self.beat("It works. Until the day you are ill, and nobody else knows the order.", you.animate.set_opacity(0.25), lines.animate.set_opacity(0.2), run_time=1.4)
        self.play(you.animate.set_opacity(1), lines.animate.set_opacity(1), run_time=0.4)
        hot = T("lit is not the same as ready", 28, YELLOW_M).move_to([0, -2.6, 0])
        self.beat("Or the cook starts the sauce before the oven is hot, because lit is not the same as ready.",
                  Wiggle(orders[1]), FadeIn(hot, shift=UP * 0.1), run_time=2.0)
        last = VGroup(M("$ docker network create ...", 22, GREY_B), M("$ docker volume create ...", 22, GREY_B), M("$ docker run ... redis", 22, GREY_B), M("$ docker run ... hello-devops", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([-2.4, 0.3, 0])
        self.steps("That is exactly how we started hello-devops and Redis last time. A network, a volume, and two long commands, typed in the right order. Phone calls, one by one.",
                   (0.8, FadeOut(VGroup(cooks, orders, lines, hot, yl)), you.animate.move_to([-5.6, 0.3, 0])), (2.2, LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in last], lag_ratio=0.3)))
        self.play(FadeOut(VGroup(last, you)), run_time=0.5)

        # 2. the plan on the wall: compose.yaml
        panel = RoundedRectangle(corner_radius=0.15, width=6.9, height=6.8, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.06), opacity=1).move_to([-3.05, -0.05, 0])
        pl = M("compose.yaml", 24, BLUE_M).move_to(panel.get_corner(UR) + LEFT * 1.25 + DOWN * 0.35)
        self.steps("The fix is a plan pinned to the kitchen wall. In Docker, that plan is one file, compose.yaml, read by Docker Compose, a tool that runs an app made of several containers.",
                   (0.8, Create(panel), FadeIn(pl)), (2.4, Wait(2.4)), (1.6, LaggedStart(*self.lay(BASE), lag_ratio=0.06)))
        y = self.ym
        # kitchen on the right
        net = Line([0.6, -0.6, 0], [6.4, -0.6, 0], stroke_width=4, color=TEAL_M)
        nl = M("hello-devops_default", 22, TEAL_M).next_to(net, DOWN, buff=0.15).align_to(net, RIGHT)
        web = station("web", GOLD_M).move_to([1.9, 1.0, 0])
        red = station("redis", RED_M).move_to([4.75, 1.0, 0])
        cw = Line(web.get_bottom(), [web.get_x(), -0.6, 0], stroke_width=3, color=TEAL_M)
        cr = Line(red.get_bottom(), [red.get_x(), -0.6, 0], stroke_width=3, color=TEAL_M)
        pan = cylinder(GREEN_M, 1.5, 0.8).move_to([4.75, -2.2, 0])
        pnl = M("redis-data", 22, GREEN_M).next_to(pan, LEFT, buff=0.25)
        mnt = DashedLine(red.get_bottom() + DOWN * 0.05, pan.get_top(), dash_length=0.1, stroke_width=2.5, color=GREEN_M)
        self.steps("Under services, one entry per station. Web, built from our Dockerfile, and Redis, a ready-made image. Under volumes, the pantry: a named volume that keeps Redis's data.",
                   (1.4, Indicate(y["web"], color=GOLD_M), FadeIn(web)), (1.2, Indicate(y["redis"], color=RED_M), FadeIn(red)), (1.4, Wait(1.4)), (1.0, Indicate(y["rdata"], color=GREEN_M), FadeIn(pan), FadeIn(pnl)))
        self.steps("You do not even write the network. Compose makes one for the project, puts every service on it, and so service names work as addresses. Web finds Redis simply as redis.",
                   (1.2, Create(net), Create(cw), Create(cr), FadeIn(nl)), (2.6, Wait(2.6)), (0.8, Indicate(y["rh"], color=TEAL_M)), (1.0, travel(Line(web.get_right(), red.get_left()), TEAL_M, 1.0)))
        p8 = M("8000", 24, GOLD_M).next_to(web, UP, buff=0.25)
        self.beat("Only web publishes a port, 8000, to your Mac. Redis has no port at all, because only web talks to it.",
                  FadeIn(p8, shift=DOWN * 0.1), Indicate(y["p8000"], color=WHITE), run_time=1.6)
        decl = rtext([("phone calls: tell each step", GREY_B), ("the plan: describe", BLUE_M), ("the finished kitchen", BLUE_M)])
        self.beat("Notice the switch. No more phone calls telling each step. You describe the finished kitchen, and docker compose up works out the steps.",
                  FadeOut(p8), FadeIn(decl, shift=DOWN * 0.1), run_time=1.8)
        self.play(FadeOut(decl), run_time=0.4)

        # 3. the trap: running is not ready
        k1 = BASE[:7] + ["dep_s"] + BASE[7:]
        self.beat("Now the trap from the opening. We want Redis started before web, so we add depends on, redis. Surely that means: wait for Redis.",
                  *self.lay(k1), run_time=1.8)
        therm = VGroup(RoundedRectangle(corner_radius=0.1, width=0.28, height=1.1, stroke_color=RED_M, stroke_width=2.5))
        fill = Rectangle(width=0.18, height=0.15, stroke_width=0).set_fill(RED_M, 0.8).align_to(therm[0], DOWN).shift(UP * 0.05)
        therm.add(fill).next_to(red, RIGHT, buff=0.2)
        self.steps("Let's be fair and watch it. Compose starts Redis. Its container is running. But a database can need several more seconds before it accepts connections.",
                   (2.0, Wait(2.0)), (0.6, red[0].animate.set_stroke(width=6)), (0.6, FadeIn(therm)), (2.0, fill.animate.stretch_to_fit_height(0.4).align_to(therm[0], DOWN).shift(UP * 0.05)))
        miss = tick(False, 0.25).move_to([3.45, 1.0, 0])
        self.steps("The short form only waits for running. So web starts right away, calls Redis, and nobody answers yet.",
                   (1.6, Wait(1.6)), (0.6, web[0].animate.set_stroke(width=6)), (0.8, travel(Line(web.get_right(), red.get_left()), GOLD_M, 0.8)), (0.4, Create(miss)))
        self.beat("The sauce went in, and the oven was only lit.", Wiggle(web), run_time=1.2)
        self.play(FadeOut(miss), web[0].animate.set_stroke(width=3), red[0].animate.set_stroke(width=3), fill.animate.stretch_to_fit_height(0.15).align_to(therm[0], DOWN).shift(UP * 0.05), run_time=0.5)

        # the fix: healthcheck + service_healthy
        k2 = BASE[:7] + ["dep_s"] + BASE[7:11] + ["hc", "hc_t", "hc_i", "hc_o", "hc_r"] + BASE[11:]
        k3 = BASE[:7] + ["dep", "dep_r", "dep_c"] + BASE[7:11] + ["hc", "hc_t", "hc_i", "hc_o", "hc_r"] + BASE[11:]
        self.steps("The fix is a healthcheck. Docker runs redis-cli ping inside the container every five seconds, with a three second timeout and five retries. Exit code zero means healthy.",
                   (1.0, *self.lay(k2)), (2.6, Wait(2.6)), (0.6, Indicate(y["hc_t"], color=RED_M)))
        self.steps("And the long form of depends on waits for it. Condition: service healthy.",
                   (1.0, *self.lay(k3)), (0.6, Indicate(y["dep_c"], color=PURPLE_M)))
        up = M("$ docker compose up -d", 24, WHITE).move_to([3.4, 2.75, 0])
        hl = chip("Healthy  5.8s", GREEN_M, 24, mono=True).next_to(red, UP, buff=0.25)
        sl = chip("Started  6.0s", GOLD_M, 24, mono=True).next_to(web, UP, buff=0.25)
        self.steps("Run docker compose up. The volume and network are created. Redis warms up, and turns healthy after 5.8 seconds. Only then does web start, at 6.0.",
                   (0.6, FadeIn(up)), (1.6, Wait(1.6)), (2.0, fill.animate.stretch_to_fit_height(0.95).align_to(therm[0], DOWN).shift(UP * 0.05).set_fill(GREEN_M)), (0.6, FadeIn(hl)), (1.0, Wait(1.0)), (0.6, FadeIn(sl)))
        visits = M('"visits": 1, 2, 3', 24, GOLD_M).move_to([3.4, -1.35, 0])
        self.steps("Call the app three times, and the visit count goes one, two, three, all kept by Redis.",
                   (1.6, Wait(1.6)), (0.6, FadeIn(visits)), (0.6, travel(Line(web.get_right(), red.get_left()), TEAL_M, 0.6)))
        rule = rtext([("Running is not ready.", YELLOW_M), ("Make the app wait for healthy.", YELLOW_M)], size=28)
        self.beat("So here is the rule. Running is not ready. Make the app wait for healthy.",
                  FadeOut(up), FadeIn(rule, shift=DOWN * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(rule, hl, sl)), run_time=0.4)

        # 4. predict: down keeps the pantry
        dn = M("$ docker compose down", 24, WHITE).move_to([3.4, 2.75, 0])
        self.beat("Closing time. docker compose down. What happens to the visit count, three so far? Pause and guess.",
                  FadeIn(dn), run_time=1.4)
        self.wait(2.0)
        stuff = VGroup(web, red, cw, cr, net, nl, therm)
        self.steps("Down removes the containers and the network. The counters get cleared. But the named volume stays. That is the pantry.",
                   (1.2, stuff.animate.set_opacity(0.15)), (1.6, Wait(1.6)), (0.8, Indicate(pan[3], color=GREEN_M), Indicate(pnl, color=GREEN_M)))
        self.steps("Bring it back up, and the count carries on where it left off. It does not start again at one.",
                   (0.8, stuff.animate.set_opacity(1), Transform(dn, M("$ docker compose up -d", 24, WHITE).move_to(dn))), (1.4, Wait(1.4)), (0.6, Transform(visits, T("the count carries on", 26, GOLD_M).move_to(visits))))
        dv = M("$ docker compose down -v", 24, RED_M).move_to(dn)
        self.steps("But add two characters, dash v, and Compose deletes the named volumes too, and your data with them, for good.",
                   (0.6, Transform(dn, dv)), (1.6, Wait(1.6)), (0.8, FadeOut(pan, scale=0.6), pnl.animate.set_color(RED_M).set_opacity(0.5), stuff.animate.set_opacity(0.15)))
        r2 = rtext([("Plain down clears the counters.", YELLOW_M), ("Down -v empties the pantry.", YELLOW_M)], top=-1.0)
        self.beat("Two commands that look almost the same. Plain down clears the counters. Down dash v empties the pantry too.",
                  FadeOut(visits), FadeIn(r2, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(r2, dn, visits, pnl)), stuff.animate.set_opacity(1), FadeIn(pan), run_time=0.6)
        pnl = M("redis-data", 22, GREEN_M).next_to(pan, LEFT, buff=0.25)
        self.add(pnl)

        # 5. guardrails
        g = rtext([("healthchecks cover startup only:", GOLD_M), ("the app must still cope", GOLD_M), ("if Redis dies later", GOLD_M), ("Compose runs on one machine only", RED_M)], top=3.25)
        self.steps("Two honest limits. A healthcheck only covers startup. If Redis dies later, hello-devops answers its readiness check with a 503, and the app must cope. And Compose runs everything on one machine. If that machine dies, so does the app.",
                   (0.8, FadeIn(g[0]), FadeIn(g[1]), FadeIn(g[2])), (5.4, Wait(5.4)), (0.8, FadeIn(g[3])))
        self.play(FadeOut(g), run_time=0.5)

        # 6. moral and quick check
        mor = rtext([("one file is the plan on the wall", BLUE_M), ("wait for healthy, not running", PURPLE_M), ("down keeps the pantry,", GREEN_M), ("down -v empties it", GREEN_M)], top=3.25)
        self.steps("So the moral of the story. One file is the plan on the wall, and one command makes the kitchen match it. Wait for healthy, not for running. And down keeps the pantry, unless you say dash v.",
                   (0.6, FadeIn(mor[0])), (3.0, Wait(3.0)), (0.6, FadeIn(mor[1])), (1.4, Wait(1.4)), (0.6, FadeIn(mor[2]), FadeIn(mor[3])))
        self.play(FadeOut(mor), run_time=0.4)
        quiz = rtext([("Quick check: depends_on: [redis],", YELLOW_M), ("no healthcheck.", YELLOW_M), ("What can go wrong?", YELLOW_M)], top=3.25)
        self.beat("Quick check. A compose file says depends on redis, the short form, with no healthcheck. What can go wrong?",
                  FadeIn(quiz, shift=DOWN * 0.1), FadeOut(pan), FadeOut(pnl), run_time=1.4)
        self.wait(2.0)
        ans = rtext([("Web can start before Redis", GREEN_M), ("accepts connections: a cold oven.", GREEN_M)], top=-1.2)
        self.beat("Web can start before Redis accepts connections. The sauce goes into a cold oven.", FadeIn(ans, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
