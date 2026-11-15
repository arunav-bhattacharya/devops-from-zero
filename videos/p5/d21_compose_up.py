import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcompose\.yaml\b", "compose dot yammel"), (r"\bdepends_on\b", "depends on"), (r"\bservice_healthy\b", "service healthy"),
            (r"\bredis-cli\b", "redis C L I"), (r"\bREDIS_HOST\b", "redis host"), (r"\bdown -v\b", "down dash V"),
            (r"\bhealthcheck\b", "health check")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def code_line(text, size=20, color=WHITE):
    """Monospace line that keeps its leading spaces (an invisible bar fixes the left edge)."""
    t = M("|" + text, size, color)
    t[0].set_opacity(0)
    return t


def cbox(name, color, w=3.0, h=1.05):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.14), opacity=1)
    n = M(name, 20).move_to(r).shift(UP * 0.2)
    return VGroup(r, n)


def status(text, color, anchor):
    return T(text, 22, color).move_to(anchor[0]).shift(DOWN * 0.24)


def cylinder(w=1.1, h=0.75, color=GOLD_M):
    top = Ellipse(width=w, height=0.28, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    body = Rectangle(width=w, height=h, stroke_width=0).set_fill(tint(color, 0.14), 1)
    bot = Ellipse(width=w, height=0.28, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.14), 1)
    body.move_to(ORIGIN); top.move_to(body.get_top()); bot.move_to(body.get_bottom())
    sides = VGroup(Line(body.get_corner(UL), body.get_corner(DL)), Line(body.get_corner(UR), body.get_corner(DR))).set_stroke(color, 3)
    return VGroup(bot, body, sides, top)


class D21ComposeUp(VoiceScene):
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
        self.title_card("From compose.yaml to a running stack", "you describe the app; Compose works out the steps")

        # ---- 0. the problem: by hand, in the right order
        cmds = VGroup(M("$ docker network create ...", 26), M("$ docker volume create ...", 26),
                      M("$ docker run -d ... redis", 26), M("$ docker run -d ... hello-devops", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        cmds.move_to([-0.6, 0.5, 0])
        nums = VGroup(*[T(str(i + 1), 26, YELLOW_M).next_to(c, LEFT, buff=0.4) for i, c in enumerate(cmds)])
        self.beat("On Day 20 you wired up hello-devops and Redis by hand. A network, a volume, and two long docker run commands, typed in the right order.",
                  LaggedStart(*[AnimationGroup(FadeIn(n), Write(c)) for n, c in zip(nums, cmds)], lag_ratio=0.5), run_time=5.0)
        imp = T("imperative: you tell Docker each step", 28, GREY_B).move_to([0, -2.2, 0])
        self.beat("That is imperative. You tell Docker each step. It works, and nobody wants to do it twice.",
                  FadeIn(imp, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(VGroup(cmds, nums, imp)), run_time=0.6)

        # ---- 1. the file
        yl = [("services:", WHITE), ("  web:", BLUE_M), ("    build: .", WHITE), ('    ports: ["8000:8000"]', WHITE), ("    environment:", WHITE),
              ("      REDIS_HOST: redis", WHITE), ('      APP_VERSION: "1.0.0"', WHITE), ("    depends_on:", WHITE), ("      redis:", WHITE),
              ("        condition: service_healthy", WHITE), ("  redis:", RED_M), ("    image: redis:8-alpine", WHITE),
              ("    volumes: [redis-data:/data]", WHITE), ("    healthcheck:", WHITE), ('      test: ["CMD", "redis-cli", "ping"]', WHITE),
              ("      interval: 5s", WHITE), ("volumes:", WHITE), ("  redis-data:", GOLD_M)]
        code = VGroup(*[code_line(t, 20, c) for t, c in yl]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        cr = RoundedRectangle(corner_radius=0.15, width=5.5, height=code.height + 0.5, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.06), 1)
        card = VGroup(cr, code.move_to(cr)).move_to([-4.0, -0.4, 0])
        fit(code, 5.2)
        ctitle = M("compose.yaml", 24, BLUE_M).next_to(card, UP, buff=0.2)
        self.beat("Docker Compose is declarative. You describe the finished app in one file, compose.yaml.",
                  Create(cr), FadeIn(ctitle), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.08) for l in code], lag_ratio=0.08), run_time=3.4)
        self.beat("It has one entry per service: one for web, built from your Dockerfile, and one for Redis, from a ready-made image. And it declares a named volume.",
                  Indicate(code[1], color=BLUE_M), Succession(Wait(2.4), Indicate(code[10], color=RED_M)), Succession(Wait(4.4), Indicate(code[17], color=GOLD_M)), run_time=6.0)

        # ---- 2. compose is only a client
        cmd = M("$ docker compose up -d", 24, YELLOW_M).move_to([2.9, 3.35, 0])
        eng = RoundedRectangle(corner_radius=0.18, width=7.7, height=5.85, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1).move_to([2.9, -0.35, 0])
        eng_l = T("Docker Engine, project hello-devops", 22, GREY_B).next_to(eng.get_corner(UL), DR, buff=0.18)
        self.beat("Then you run docker compose up. Compose is only a client. It turns the file into the same requests to Docker Engine that your docker run commands made.",
                  Write(cmd), Succession(Wait(1.6), AnimationGroup(Create(eng), FadeIn(eng_l))), run_time=4.0)
        req = VGroup(*[Dot(radius=0.07, color=YELLOW_M) for _ in range(3)])
        self.play(LaggedStart(*[Succession(FadeIn(d.move_to(cr.get_right()), run_time=0.1),
                                           d.animate(run_time=0.8).move_to(eng.get_left() + RIGHT * 0.6 + UP * (0.6 - 0.6 * i)),
                                           FadeOut(d, run_time=0.2)) for i, d in enumerate(req)], lag_ratio=0.3), run_time=1.6)

        # ---- 3. the steps it works out
        net = RoundedRectangle(corner_radius=0.15, width=7.2, height=2.35, stroke_color=TEAL_M, stroke_width=2.5).set_fill(tint(TEAL_M, 0.05), 1).move_to([2.9, 0.75, 0])
        net_l = M("network hello-devops_default", 20, TEAL_M).next_to(net.get_corner(UL), DR, buff=0.14)
        vol = cylinder().move_to([4.75, -1.65, 0])
        vol_l = M("hello-devops_redis-data", 20, GOLD_M).next_to(vol, DOWN, buff=0.15)
        self.beat("It works out the steps. First the things the containers need: the volume, and a network for this project.",
                  Succession(FadeIn(vol), FadeIn(vol_l)), Succession(Wait(1.6), AnimationGroup(Create(net), FadeIn(net_l))), run_time=3.2)
        names = T("names come from the folder: hello-devops", 22, GREY_B).move_to([2.9, -3.0, 0])
        self.beat("Every name starts with the project, and the project is named after the folder.",
                  FadeIn(names, shift=UP * 0.1), Indicate(net_l, color=TEAL_M), Indicate(vol_l, color=GOLD_M), run_time=2.2)
        self.play(FadeOut(names), run_time=0.4)

        redis = cbox("hello-devops-redis-1", RED_M).move_to([4.75, 0.45, 0])
        web = cbox("hello-devops-web-1", BLUE_M).move_to([1.05, 0.45, 0])
        vlink = Line(redis.get_bottom(), vol.get_top() + UP * 0.12, stroke_width=2.5, color=GOLD_M)
        r_st = status("created", GREY_B, redis)
        self.beat("Then the Redis container, with the volume mounted at slash data. The -1 is a counter, because Compose can run several copies of one service.",
                  GrowFromCenter(redis), Create(vlink), FadeIn(r_st), Succession(Wait(3.4), Indicate(redis[1][-2:], color=YELLOW_M)), run_time=4.6)

        # ---- 4. running is not ready
        self.beat("Now the catch. depends_on makes Compose start Redis before web.",
                  Indicate(code[7], color=YELLOW_M), run_time=1.6)
        r_run = status("running", GREEN_M, redis)
        q = T("running, but ready?", 26, YELLOW_M).move_to([1.05, 1.5, 0])
        self.beat("In its short form, it only waits until the Redis container is running. But a database can need several more seconds before it accepts connections.",
                  Transform(r_st, r_run), Succession(Wait(2.8), FadeIn(q, shift=DOWN * 0.1)), run_time=4.4)
        run_ready = T("running is not ready", 26, RED_M).move_to(q)
        self.beat("Running is not the same as ready.", Transform(q, run_ready), run_time=1.0)

        tv = ValueTracker(0)
        clk = always_redraw(lambda: M(f"t = {tv.get_value():.1f} s", 22, GREY_B).move_to([5.6, 2.55, 0]))
        hc = VGroup(M("redis-cli ping", 20, RED_M), T("every 5 s, timeout 3 s, 5 retries", 20, GREY_B)).arrange(DOWN, buff=0.1).move_to([1.05, -1.55, 0])
        self.beat("A healthcheck closes that gap. It is a command Docker runs inside the container, on a schedule. Here, redis-cli ping, every five seconds.",
                  FadeOut(q), Indicate(VGroup(code[13], code[14], code[15]), color=RED_M), Succession(Wait(3.0), FadeIn(hc)), run_time=5.0)
        r_sta = status("health: starting", GOLD_M, redis)
        self.add(clk)
        e0 = chip("exit 0", GREEN_M, 20, mono=True).next_to(redis, UP, buff=0.15)
        self.steps("Exit code zero means healthy. Until a check passes, Redis shows starting.",
                   (0.6, Transform(r_st, r_sta)), (2.6, tv.animate(rate_func=linear).set_value(5.0)), (0.6, FadeIn(e0, shift=DOWN * 0.1)))
        r_ok = status("healthy", GREEN_M, redis)
        self.beat("In the lesson's run, Redis showed healthy after 5.8 seconds.",
                  tv.animate(rate_func=linear).set_value(5.8), Succession(Wait(0.8), AnimationGroup(Transform(r_st, r_ok), FadeOut(e0))), run_time=2.0)
        w_st = status("started", GREEN_M, web)
        self.beat("The long form of depends_on, with condition service_healthy, waits for exactly that. Only now does Compose start web, at 6.0 seconds.",
                  Indicate(code[9], color=GREEN_M), Succession(Wait(3.2), AnimationGroup(GrowFromCenter(web), FadeIn(w_st), tv.animate.set_value(6.0))), run_time=5.0)
        self.play(FadeOut(hc), FadeOut(clk), run_time=0.4)
        self.remove(clk)

        # ---- 5. names as DNS, one published port
        dns = Arrow(web.get_right(), redis.get_left(), buff=0.12, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.15)
        dns_l = M("redis:6379", 20, TEAL_M).next_to(dns, UP, buff=0.12)
        self.beat("Every service is on the project network, so service names work as DNS names. Web finds Redis by the name redis.",
                  Indicate(code[5], color=TEAL_M), GrowArrow(dns), FadeIn(dns_l), Succession(Wait(2.0), travel(dns, TEAL_M, 1.0)), run_time=4.0)
        mac = chip("your Mac: localhost:8000", WHITE, 22).move_to([1.05, -2.75, 0])
        up = Arrow(mac.get_top(), web.get_bottom(), buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        up_l = M("8000:8000", 20, BLUE_M).next_to(up, RIGHT, buff=0.15).shift(DOWN * 0.3)
        nop = T("no ports", 22, GREY_B).next_to(vol, LEFT, buff=0.7).shift(UP * 0.15)
        self.beat("Only port 8000 is published to your Mac. Redis has no ports entry, because only web talks to it.",
                  FadeIn(mac), GrowArrow(up), FadeIn(up_l), Indicate(code[3], color=BLUE_M), Succession(Wait(2.8), FadeIn(nop)), run_time=4.0)
        self.play(travel(up, BLUE_M, 0.8), run_time=0.8)
        self.play(FadeOut(nop), run_time=0.3)

        # ---- 6. up again: labels and a hash
        tag_w = chip("hash a1f3", BLUE_M, 20, mono=True).next_to(web, UP, buff=0.12).shift(RIGHT * 0.6)
        tag_r = chip("hash 9c4b", RED_M, 20, mono=True).next_to(redis, UP, buff=0.12).shift(RIGHT * 0.6)
        self.beat("But how does Compose know what is already there? It labels every container with its project, its service, and a hash of that service's settings.",
                  Succession(Wait(3.0), LaggedStart(FadeIn(tag_w, shift=DOWN * 0.1), FadeIn(tag_r, shift=DOWN * 0.1), lag_ratio=0.4)), run_time=5.0)
        new_line = code_line('      APP_VERSION: "1.1.0"', 20, YELLOW_M).scale(code[6].height / code_line('      APP_VERSION: "1.0.0"', 20).height)
        new_line.move_to(code[6], aligned_edge=LEFT)
        self.beat("Say you change one setting of web, and run up again.",
                  Transform(code[6], new_line), Indicate(cmd, color=YELLOW_M), run_time=1.8)
        cmp_w = chip("file says 7e20", YELLOW_M, 20, mono=True).next_to(tag_w, LEFT, buff=0.2)
        xw = tick(False, 0.18).next_to(cmp_w, LEFT, buff=0.15)
        ok_r = tick(True, 0.2).next_to(tag_r, LEFT, buff=0.2)
        self.beat("Compose compares the labels with the file. Redis matches, so it keeps running. Web's hash is different.",
                  Succession(Wait(1.6), FadeIn(ok_r)), Succession(Wait(3.4), AnimationGroup(FadeIn(cmp_w), FadeIn(xw))), run_time=5.0)
        web2 = cbox("hello-devops-web-1", BLUE_M).move_to(web)
        tag_w2 = chip("hash 7e20", BLUE_M, 20, mono=True).move_to(tag_w)
        w_st2 = status("recreated", YELLOW_M, web2)
        self.steps("So only web is recreated.",
                   (0.6, FadeOut(web), FadeOut(w_st), FadeOut(tag_w), FadeOut(cmp_w), FadeOut(xw), FadeOut(dns), FadeOut(dns_l), FadeOut(up), FadeOut(up_l)),
                   (0.8, FadeIn(web2), FadeIn(w_st2), FadeIn(tag_w2)))
        self.play(FadeOut(ok_r), FadeOut(tag_r), FadeOut(tag_w2), run_time=0.4)

        # ---- 7. down keeps the volume
        cmd_d = M("$ docker compose down", 24, YELLOW_M).move_to(cmd)
        self.beat("docker compose down removes the containers, and the network.",
                  Transform(cmd, cmd_d),
                  Succession(Wait(1.0), AnimationGroup(FadeOut(VGroup(web2, w_st2, redis, r_st)), FadeOut(vlink)), Wait(0.4), FadeOut(VGroup(net, net_l))), run_time=3.0)
        keep = T("kept: your visit count", 22, GOLD_M).next_to(vol, LEFT, buff=0.5)
        self.beat("It keeps named volumes. So the next up finds your Redis data, and the visit count carries on.",
                  Indicate(vol, color=GOLD_M), FadeIn(keep, shift=RIGHT * 0.1), run_time=2.4)
        warn = T("down -v also deletes the volumes", 22, RED_M).next_to(keep, DOWN, buff=0.75).align_to(keep, LEFT)
        warn.move_to([2.9, -3.05, 0])
        self.beat("docker compose down -v also deletes the volumes, and your data with them.",
                  FadeIn(warn, shift=UP * 0.1), FadeOut(mac), run_time=1.8)
        self.play(FadeOut(VGroup(keep, warn)), run_time=0.4)

        # ---- 8. recap
        rc = VGroup(T("You describe the app.", 30, BLUE_M), T("up makes the steps, in order,", 30), T("and waits for healthy, not just running.", 30, GREEN_M)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rc.move_to([2.9, 0.6, 0])
        self.beat("compose.yaml describes the whole app. docker compose up makes the steps, in the right order, and with a healthcheck it waits for ready, not just running.",
                  FadeOut(eng_l), LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.6), run_time=5.0)
        self.wait(1.0)
