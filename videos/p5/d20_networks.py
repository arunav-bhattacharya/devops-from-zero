import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"127\.0\.0\.11", "one two seven, dot zero, dot zero, dot eleven"), (r"172\.17\.0\.5", "one seven two, dot seventeen, dot zero, dot five"),
            (r"\bREDIS_HOST\b", "redis host"), (r"\bveth\b", "vee-eth"), (r"\beth0\b", "eth zero"), (r"\bdocker rm\b", "docker R M"),
            (r"(?<![\w/])/data\b", "slash data"), (r"(?<!\w)-p\b", "dash P"), (r"\bhello-net\b", "hello net"),
            (r"\bgithub\.com\b", "github dot com"), (r"\bredis-data\b", "redis data")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def cont(title, sub, color, w=2.6, h=1.6, subc=GREY_B):
    r = RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color), opacity=1)
    t = T(title, 30).move_to(r.get_center() + UP * 0.38)
    s = M(sub, 22, subc).move_to(r.get_center() + DOWN * 0.12) if sub else VGroup()
    return VGroup(r, t, s)


def cylinder(label, color=GOLD_M, w=2.2, h=1.1):
    ry = 0.16
    body = Rectangle(width=w, height=h, stroke_width=0).set_fill(tint(color, 0.22), opacity=1)
    sides = VGroup(Line(body.get_corner(UL), body.get_corner(DL)), Line(body.get_corner(UR), body.get_corner(DR))).set_stroke(color, 3)
    bot = Ellipse(width=w, height=2 * ry, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.22), opacity=1).move_to(body.get_bottom())
    top = Ellipse(width=w, height=2 * ry, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), opacity=1).move_to(body.get_top())
    lab = M(label, 22).move_to(body.get_center() + DOWN * 0.08)
    return VGroup(bot, body, sides, top, lab)


class D20Networks(VoiceScene):
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

    def run_dot(self, path, color=YELLOW_M, rt=1.2):
        d = Dot(radius=0.09, color=color).move_to(path.get_start())
        return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, path, rate_func=smooth, run_time=rt), FadeOut(d, run_time=0.15))

    def construct(self):
        self.title_card("How containers find each other", "networks give names, volumes keep the data")

        WX, DX, RX, CY, BAR = -2.6, 0.8, 4.2, 0.5, 2.3
        web = cont("web", "hello-devops", TEAL_M).move_to([WX, CY, 0])
        red = cont("redis", "visits: 5", RED_M, subc=YELLOW_M).move_to([RX, CY, 0])

        # 1. the problem: localhost
        self.beat("hello-devops keeps its visit count in Redis. So the web container has to reach the Redis container.",
                  FadeIn(web, shift=UP * 0.15), Succession(Wait(1.0), FadeIn(red, shift=UP * 0.15)), run_time=2.6)
        env = M("REDIS_HOST=localhost", 22, YELLOW_M).next_to(web, DOWN, buff=0.35)
        self.beat("A first try: set REDIS_HOST to localhost.", Write(env), run_time=1.4)
        los = VGroup()
        for c in (web, red):
            lo = chip("own localhost", GREY_B, 20).next_to(c, UP, buff=0.3)
            los.add(lo)
        self.beat("But every container gets its own network namespace. Its own network card, its own IP address, and its own localhost.",
                  LaggedStart(*[FadeIn(l, shift=DOWN * 0.1) for l in los], lag_ratio=0.4), run_time=2.4)
        loop = CurvedArrow(web[0].get_right() + UP * 0.35, web[0].get_right() + DOWN * 0.35, angle=-PI * 1.4, color=RED_M, stroke_width=3)
        x = tick(False, 0.3).move_to(red[0].get_left() + LEFT * 1.6)
        self.steps("So inside a container, localhost means that container itself. The app calls itself, and nothing there listens on Redis's port.",
                   (1.4, Create(loop)), (1.6, Wait(1.6)), (0.8, Create(x)), (0.6, Wiggle(env)))
        self.play(FadeOut(VGroup(loop, x, los)), run_time=0.6)

        # 2. the default bridge
        host = RoundedRectangle(corner_radius=0.2, width=11.2, height=6.9, stroke_color=GREY_D, stroke_width=2).move_to([1.0, 0.05, 0])
        hlab = T("Docker host, the Linux VM", 22, GREY_B).move_to(host.get_corner(UL) + RIGHT * 2.0 + DOWN * 0.35)
        bar = Line([-4.2, BAR, 0], [6.2, BAR, 0], stroke_width=7, color=GREY_B)
        blab = M("bridge", 24, GREY_B).move_to([5.5, BAR + 0.4, 0])
        self.beat("Docker connects containers through a bridge, a virtual network switch inside the Linux VM.",
                  FadeOut(env), Create(host), FadeIn(hlab), Create(bar), FadeIn(blab), run_time=2.4)

        def cable(c, color=GREY_B):
            return Line(c[0].get_top(), [c.get_x(), BAR, 0], stroke_width=3, color=color)

        def eth(c, color=GREY_B):
            return M("eth0", 20, color).move_to(c[0].get_top() + DOWN * 0.2 + RIGHT * 0.8)

        cw, cr = cable(web), cable(red)
        ew, er = eth(web), eth(red)
        self.beat("Each container gets a virtual cable, called a veth pair. One end is eth0 inside the container. The other end plugs into the bridge.",
                  FadeIn(ew), FadeIn(er), Succession(Wait(1.2), AnimationGroup(Create(cw), Create(cr))), run_time=3.0)
        ipw = M("172.17.0.4", 20, GREY_B).next_to(cw, LEFT, buff=0.15).shift(DOWN * 0.05)
        ipr = M("172.17.0.5", 20, GREY_B).next_to(cr, LEFT, buff=0.15).shift(DOWN * 0.05)
        self.beat("Start a container without the network flag, and it joins this default network, called bridge. It gets an address such as 172.17.0.5.",
                  FadeIn(ipw), Succession(Wait(2.4), FadeIn(ipr, run_time=0.5), Indicate(ipr, color=WHITE, run_time=0.5)), run_time=3.4)

        ask = M("ping redis", 22, WHITE).next_to(web, DOWN, buff=0.35)
        bad = M("bad address 'redis'", 22, RED_M).next_to(ask, DOWN, buff=0.2)
        self.steps("Now ask for Redis by name, from the web container. On the default bridge, that fails. Bad address. There is no lookup by name.",
                   (1.0, FadeIn(ask)), (1.4, Wait(1.4)), (0.8, FadeIn(bad, shift=UP * 0.1)))
        path = VMobject().set_points_as_corners([cw.get_start(), cw.get_end(), cr.get_end(), cr.get_start()])
        ask2 = M("ping 172.17.0.5", 22, WHITE).move_to(ask)
        ok = M("reply", 22, GREEN_M).move_to(bad)
        self.steps("By IP address, it works.",
                   (0.6, Transform(ask, ask2), FadeOut(bad)), (1.2, self.run_dot(path, YELLOW_M, 1.2)),
                   (0.4, FadeIn(ok)))
        ipr2 = M("172.17.0.?", 20, RED_M).move_to(ipr)
        self.beat("But those addresses change when containers restart. So you cannot hard-code them.",
                  Transform(ipr, ipr2), Succession(Wait(1.4), Wiggle(ask)), run_time=2.6)
        oth = cont("other app", "", GREY_B, w=2.6, h=1.3).move_to([DX, CY, 0])
        oth[1].move_to(oth[0])
        co = cable(oth)
        self.beat("And every container started without the network flag lands on this same bridge. So unrelated apps can talk to each other.",
                  FadeOut(ask), FadeOut(ok), FadeIn(oth, shift=UP * 0.15), Succession(Wait(0.6), Create(co)),
                  Succession(Wait(2.4), self.run_dot(
                             VMobject().set_points_as_corners([co.get_start(), co.get_end(), cr.get_end(), cr.get_start()]), GREY_B, 1.2)), run_time=4.0)

        # 3. a user-defined network
        cmd = M("docker network create hello-net", 24).move_to([0.8, -2.55, 0])
        nlab = M("hello-net", 24, TEAL_M).move_to(blab)
        self.beat("Docker's own docs recommend a network you create yourself. A user-defined network. You make one with docker network create.",
                  Write(cmd), Succession(Wait(2.2), AnimationGroup(bar.animate.set_color(TEAL_M), Transform(blab, nlab))), run_time=3.6)
        self.beat("Start both containers on hello-net. The other app is not on it, so it cannot reach them. Each app gets its own private network.",
                  FadeOut(co), oth.animate.set_opacity(0.0), cw.animate.set_color(TEAL_M), cr.animate.set_color(TEAL_M),
                  Transform(ipw, M("172.23.0.2", 20, TEAL_M).move_to(ipw)), Transform(ipr, M("172.23.0.3", 20, TEAL_M).move_to(ipr)), run_time=2.4)
        self.remove(oth)

        dr = RoundedRectangle(corner_radius=0.14, width=2.9, height=1.75, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M), opacity=1).move_to([DX, CY, 0])
        dt = VGroup(T("Docker DNS", 26), M("127.0.0.11", 22, BLUE_M)).arrange(DOWN, buff=0.12).move_to(dr.get_center() + UP * 0.35)
        rows = VGroup(M("web    172.23.0.2", 20, GREY_B), M("redis  172.23.0.3", 20, GREY_B)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        dns = VGroup(dr, dt)
        self.beat("Now each container gets a DNS server, at 127.0.0.11. Docker's embedded DNS server.",
                  FadeOut(cmd), Create(dr), Write(dt), run_time=2.0)
        q1 = Arrow(web[0].get_right() + UP * 0.25, dr.get_left() + UP * 0.25, buff=0.08, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.25)
        a1 = Arrow(dr.get_left() + DOWN * 0.35, web[0].get_right() + DOWN * 0.35, buff=0.08, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.25)
        ql = M("redis?", 22, YELLOW_M).next_to(web, DOWN, buff=0.35)
        al = M("172.23.0.3", 22, GREEN_M).next_to(ql, DOWN, buff=0.15)
        self.beat("The web app asks it: where is redis?", GrowArrow(q1), FadeIn(ql), run_time=1.4)
        # grow the DNS box to show its table
        dr2 = RoundedRectangle(corner_radius=0.14, width=2.9, height=2.3, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M), opacity=1).move_to([DX, CY - 0.2, 0])
        dt2 = dt.copy().move_to(dr2.get_top() + DOWN * 0.5)
        rows.next_to(dt2, DOWN, buff=0.2)
        self.steps("It answers by name, with the current IP address of that container.",
                   (0.8, Transform(dr, dr2), Transform(dt, dt2), FadeIn(rows)), (0.6, Indicate(rows[1], color=GREEN_M)),
                   (0.8, GrowArrow(a1), FadeIn(al)))
        vis6 = M("visits: 6", 22, YELLOW_M).move_to(red[2])
        self.steps("Then the app connects to that address, over the network. Visits goes up by one.",
                   (1.4, self.run_dot(path, YELLOW_M, 1.4)), (0.8, Transform(red[2], vis6)))

        # but how does it know?
        eng = box("Docker Engine", GREY_B, w=3.0, h=0.75, size=24).move_to([DX, -2.4, 0])
        ea = Arrow(eng.get_top(), dr.get_bottom(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.25)
        hq = T("but how does it know?", 26, YELLOW_M).move_to([-2.6, -2.4, 0])
        self.beat("But how does the DNS server know?", FadeOut(VGroup(q1, a1, ql, al)), FadeIn(hq, shift=UP * 0.1), run_time=1.2)
        self.steps("Docker Engine handed out those addresses in the first place. So it already has the list.",
                   (1.0, FadeIn(eng)), (0.8, GrowArrow(ea)), (1.0, Indicate(ipw, color=WHITE), Indicate(ipr, color=WHITE), Indicate(rows, color=WHITE)))
        gh = VGroup(M("github.com", 22, GREY_B), T("passed on to the host's DNS", 22, GREY_B)).arrange(DOWN, buff=0.12).move_to([-3.0, -2.4, 0])
        self.beat("Names it does not know, such as github.com, it passes on to the host's DNS servers.",
                  FadeOut(hq), FadeIn(gh, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(eng, ea, gh)), run_time=0.5)

        # -p only for outside
        nop = chip("no -p", GREY_B, 22, mono=True).move_to([RX, -1.0, 0])
        self.beat("Containers on the same network reach each other on any port. Redis needs no -p at all.",
                  FadeIn(nop, shift=UP * 0.1), run_time=1.6)
        mac = box("Mac", WHITE, w=1.3, h=0.8, size=26).move_to([-5.95, -1.6, 0])
        mp = M("-p 8000", 22, TEAL_M).next_to(mac, UP, buff=0.25)
        ma = Arrow(mac.get_right(), web[0].get_corner(DL) + RIGHT * 0.3, buff=0.12, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.15)
        self.steps("The -p flag is only for traffic from outside. The web container is published on port 8000, so your Mac can reach it.",
                   (1.0, Wait(1.0)), (1.0, FadeIn(mac), FadeIn(mp)), (0.8, GrowArrow(ma)), (1.0, travel(ma, TEAL_M, 1.0)))
        self.play(FadeOut(VGroup(mac, mp, ma, nop)), run_time=0.5)

        # 4. the data: volume
        layer = Rectangle(width=2.3, height=0.36, stroke_color=GREY_B, stroke_width=2).set_fill(tint(GREY_B, 0.3), opacity=1)
        layer.move_to(red[0].get_bottom() + UP * 0.32)
        ll = T("writable layer", 20, GREY_B).move_to(layer)
        dpath = M("/data", 22, WHITE).next_to(red, DOWN, buff=0.3)
        self.beat("Now the data. Redis writes the count to its /data folder.",
                  FadeIn(dpath), Indicate(red[2], color=YELLOW_M), run_time=1.6)
        self.beat("Without a mount, that folder sits in the container's thin writable layer. And docker rm deletes that layer, with the count in it.",
                  FadeIn(layer), FadeIn(ll), Succession(Wait(2.8), AnimationGroup(VGroup(red, layer, ll, er).animate.set_opacity(0.15), cr.animate.set_opacity(0.2),
                                                                              ipr.animate.set_opacity(0.2))), run_time=4.0)
        vol = cylinder("redis-data").move_to([RX, -2.35, 0])
        red_b = red.copy().set_opacity(1)
        red_b[0].set_fill(tint(RED_M), opacity=1)
        self.beat("So keep the data outside the container, in a volume: storage that Docker manages, which outlives the containers that use it.",
                  FadeOut(layer), FadeOut(ll), Transform(red, red_b), er.animate.set_opacity(1), cr.animate.set_opacity(1), ipr.animate.set_opacity(1),
                  FadeOut(dpath), Succession(Wait(1.6), FadeIn(vol, shift=UP * 0.15)), run_time=3.2)
        self.add(er)
        mnt = Line(red[0].get_bottom(), vol[3].get_top(), stroke_width=3, color=GOLD_M)
        mlab = M("/data", 22, GOLD_M).next_to(mnt, LEFT, buff=0.15)
        flag = VGroup(M("-v", 26), M("redis-data", 26, GOLD_M), M(":", 26), M("/data", 26, WHITE)).arrange(RIGHT, buff=0.12).move_to([-1.4, -2.1, 0])
        fl1 = T("volume name", 20, GOLD_M).next_to(flag[1], DOWN, buff=0.2)
        fl2 = T("folder inside", 20, WHITE).next_to(flag[3], DOWN, buff=0.2).shift(RIGHT * 0.2)
        self.steps("Mount it with -v redis-data:/data. The name on the left is the volume. The folder on the right is inside the container.",
                   (1.2, Create(mnt), FadeIn(mlab), FadeIn(flag)), (0.8, Wait(0.8)), (0.8, FadeIn(fl1), Indicate(flag[1], color=GOLD_M)),
                   (0.6, Wait(0.6)), (0.8, FadeIn(fl2), Indicate(flag[3], color=WHITE)))

        # 5. replace Redis
        self.beat("Now swap Redis. Stop it with docker stop, so it can save its data first. Then remove it.",
                  FadeOut(VGroup(fl1, fl2)),
                  Succession(Wait(1.8), AnimationGroup(FadeOut(red), FadeOut(cr), FadeOut(er), FadeOut(mnt), FadeOut(mlab), ipr.animate.set_opacity(0.0),
                                                       rows[1].animate.set_opacity(0.25))), run_time=3.4)
        self.beat("The volume stays. Docker never deletes a named volume by itself.",
                  Indicate(vol, color=GOLD_M, scale_factor=1.08), run_time=1.6)
        red2 = cont("redis", "visits: ?", RED_M, subc=GREY_B).move_to([RX, CY, 0])
        cr2, er2 = cable(red2, TEAL_M), eth(red2)
        ipn = M("172.23.0.4", 20, TEAL_M).move_to(ipr)
        rown = M("redis  172.23.0.4", 20, GREY_B).move_to(rows[1], aligned_edge=LEFT)
        mnt2 = Line(red2[0].get_bottom(), vol[3].get_top(), stroke_width=3, color=GOLD_M)
        self.steps("Start a brand-new Redis container, on the same network, with the same volume. Docker hands it an address, maybe a new one.",
                   (1.2, FadeIn(red2, shift=DOWN * 0.15), FadeIn(er2)), (0.8, Create(cr2), Create(mnt2), FadeIn(mlab)),
                   (1.4, Wait(1.4)), (1.0, FadeIn(ipn), Transform(rows[1], rown)))
        q2 = Arrow(web[0].get_right() + UP * 0.25, dr.get_left() + UP * 0.25, buff=0.08, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.25)
        a2 = Arrow(dr.get_left() + DOWN * 0.35, web[0].get_right() + DOWN * 0.35, buff=0.08, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.25)
        ql2 = M("redis?", 22, YELLOW_M).next_to(web, DOWN, buff=0.35)
        al2 = M("172.23.0.4", 22, GREEN_M).next_to(ql2, DOWN, buff=0.15)
        self.steps("The web app still asks for redis by name, and gets the new address. Nothing in the app changes.",
                   (0.6, FadeOut(flag)), (0.8, GrowArrow(q2), FadeIn(ql2)), (0.6, Indicate(rows[1], color=GREEN_M)), (0.8, GrowArrow(a2), FadeIn(al2)))
        up = Dot(radius=0.09, color=GOLD_M).move_to(mnt2.get_end())
        v5 = M("visits: 5", 22, YELLOW_M).move_to(red2[2])
        v6 = M("visits: 6", 22, YELLOW_M).move_to(red2[2])
        self.steps("And the new Redis finds the old data in the volume. The count carries on, from five to six.",
                   (1.0, FadeIn(up, run_time=0.1), up.animate.move_to(mnt2.get_start())), (0.6, FadeOut(up), Transform(red2[2], v5)),
                   (1.0, Wait(1.0)), (0.6, Transform(red2[2], v6), Flash(red2[2].get_center(), color=YELLOW_M, flash_radius=0.8)))

        # 6. recap
        rc = VGroup(T("network: names, through Docker's DNS", 24, TEAL_M), T("volume: data outlives the container", 24, GOLD_M)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        rc.move_to([-1.1, -2.35, 0])
        self.beat("A user-defined network gives containers names, through Docker's DNS. A volume keeps the data when the container goes.",
                  FadeOut(VGroup(q2, a2, ql2, al2)), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rc], lag_ratio=0.6), run_time=3.4)
        self.wait(1.2)
