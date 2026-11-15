import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\beu-central-1\b", "E U central one"), (r"10\.0\.0\.0/16", "ten dot zero dot zero dot zero, slash sixteen"),
            (r"0\.0\.0\.0/0", "zero dot zero dot zero dot zero, slash zero"), (r"(?<![\w.])/24\b", "slash twenty-four"),
            (r"\bAZs\b", "A Zs"), (r"\bAZ\b", "A Z"), (r"\bNAT\b", "nat"), (r"\bPayFlow\b", "pay flow")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def mini(label, color, w=1.7, h=0.5, size=22):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.22), opacity=1)
    return VGroup(r, T(label, size).move_to(r))


def server(color=TEAL_M):
    r = RoundedRectangle(corner_radius=0.1, width=1.5, height=1.0, stroke_color=color, stroke_width=3.5).set_fill(tint(color, 0.2), opacity=1)
    ls = VGroup(*[Line(LEFT * 0.45, RIGHT * 0.45, stroke_width=3, color=color).shift(UP * dy) for dy in (0.18, -0.12)])
    return VGroup(r, ls.move_to(r))


class D12TwoZones(VoiceScene):
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

    def dot_path(self, pts, color=YELLOW_M, rt=1.6):
        d = Dot(radius=0.09, color=color).move_to(pts[0])
        p = VMobject().set_points_as_corners(pts)
        return Succession(FadeIn(d, run_time=0.05), MoveAlongPath(d, p, rate_func=smooth, run_time=rt), FadeOut(d, run_time=0.15))

    def construct(self):
        self.title_card("One network across two zones", "regions, availability zones, public and private subnets")

        AX = (-3.05, 3.05)

        # 1. things fail at every size
        s1 = server().move_to([0, 0.3, 0])
        lab = T("checkout API", 24, GREY_B).next_to(s1, DOWN, buff=0.25)
        self.beat("PayFlow, the made-up payments company, wants its checkout API to keep running when things break.",
                  GrowFromCenter(s1), FadeIn(lab), run_time=1.8)
        x1 = tick(False, 0.3).move_to(s1)
        self.beat("Things fail at every size. One server dies.", s1.animate.set_stroke(RED_M), Create(x1), run_time=1.4)
        s2 = server().move_to([1.0, 0.3, 0])
        lab.generate_target(); lab.target.move_to([0, -0.75, 0])
        self.beat("So run two copies.", FadeOut(x1), s1.animate.set_stroke(TEAL_M).move_to([-1.0, 0.3, 0]), GrowFromCenter(s2),
                  MoveToTarget(lab), run_time=1.2)
        dc = RoundedRectangle(corner_radius=0.15, width=4.6, height=2.6, stroke_color=GREY_B, stroke_width=2).move_to([0, 0.15, 0])
        dcl = T("one data center", 22, GREY_B).next_to(dc, UP, buff=0.15)
        self.beat("But both copies sit in one data center. If it loses power or floods, both go down together.",
                  Create(dc), FadeIn(dcl), Succession(Wait(2.4), AnimationGroup(dc.animate.set_stroke(RED_M), s1.animate.set_stroke(RED_M), s2.animate.set_stroke(RED_M))),
                  run_time=3.6)

        # 2. availability zones and a region
        cols = VGroup(*[DashedVMobject(RoundedRectangle(corner_radius=0.15, width=5.65, height=4.65, stroke_color=GREY_B, stroke_width=2), num_dashes=70)
                        .move_to([x, -0.82, 0]) for x in AX])
        azl = VGroup(*[T(f"AZ {n}", 24, GREY_B).move_to([x, -2.85, 0]) for n, x in zip("ab", AX)])
        self.steps("So run copies in two or more availability zones. AWS describes a zone as one or more separate data centers, with their own power, networking and connectivity.",
                   (0.6, FadeOut(dc), FadeOut(dcl), FadeOut(lab), s1.animate.set_stroke(TEAL_M), s2.animate.set_stroke(TEAL_M)),
                   (1.6, Create(cols), FadeIn(azl), s1.animate.set_stroke(TEAL_M).move_to([AX[0], -0.5, 0]), s2.animate.set_stroke(TEAL_M).move_to([AX[1], -0.5, 0])))
        fib = DoubleArrow(s1.get_right() + RIGHT * 0.15, s2.get_left() + LEFT * 0.15, buff=0, stroke_width=3, color=BLUE_M, tip_length=0.18)
        fl = T("fast private fiber", 24, BLUE_M).move_to([0, 2.0, 0])
        self.beat("The zones are linked by fast private fiber. Close enough for fast traffic between them, and far enough apart not to fail together.",
                  GrowFromCenter(fib), FadeIn(fl), Succession(Wait(1.5), travel(Line(fib.get_start(), fib.get_end()), BLUE_M, 1.0)), run_time=3.6)
        reg = RoundedRectangle(corner_radius=0.2, width=13.2, height=6.5, stroke_color=WHITE, stroke_width=2).move_to([0, -0.4, 0])
        rl = VGroup(T("region", 24), M("eu-central-1", 22, GREY_B), T("(Frankfurt)", 22, GREY_B)).arrange(RIGHT, buff=0.2)
        rl.move_to(reg.get_corner(UL) + RIGHT * (rl.width / 2 + 0.3) + DOWN * 0.3)
        self.beat("The zones sit inside a region, a geographic area, such as eu-central-1 in Frankfurt. For most apps, two or three zones in one region is the right amount.",
                  Create(reg), FadeIn(rl), run_time=2.2)

        # 3. a VPC and four subnets
        vpc = RoundedRectangle(corner_radius=0.18, width=12.4, height=5.45, stroke_color=BLUE_M, stroke_width=3).move_to([0, -0.62, 0])
        vl = M("VPC 10.0.0.0/16", 22, BLUE_M).move_to([4.6, 1.8, 0])
        self.beat("Now the network. A VPC is your own private network inside the provider. You give it a private block, 10.0.0.0/16.",
                  FadeOut(fib), FadeOut(fl), FadeOut(s1), FadeOut(s2), Create(vpc), Write(vl), run_time=2.4)

        def subnet(name, cidr, x, y, color):
            r = RoundedRectangle(corner_radius=0.12, width=5.25, height=1.75, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), opacity=1).move_to([x, y, 0])
            t = VGroup(M(name, 22), M(cidr, 22, GREY_B)).arrange(RIGHT, buff=0.35).move_to([x, y + 0.55, 0])
            return VGroup(r, t)

        PY, QY = 0.55, -1.6
        pub = VGroup(subnet("public-a", "10.0.1.0/24", AX[0], PY, GREY_B), subnet("public-b", "10.0.2.0/24", AX[1], PY, GREY_B))
        prv = VGroup(subnet("private-a", "10.0.11.0/24", AX[0], QY, GREY_B), subnet("private-b", "10.0.12.0/24", AX[1], QY, GREY_B))
        self.beat("Then you split it into subnets, smaller blocks. In AWS each subnet lives in exactly one zone. So an app in two zones needs subnets in both.",
                  LaggedStart(*[FadeIn(s, shift=DOWN * 0.1) for s in (pub[0], prv[0], pub[1], prv[1])], lag_ratio=0.3), run_time=3.0)
        res = chip("/24 = 256 addresses, 251 usable", GREY_B, 22).move_to([-3.7, 3.3, 0])
        self.beat("AWS keeps 5 addresses in every subnet. So a /24 gives you 251 usable addresses, not 256.",
                  FadeIn(res, shift=DOWN * 0.1), run_time=1.6)

        # 4. what makes a subnet public: the route table
        q = T("public or private?", 26, YELLOW_M).move_to([3.4, 3.3, 0])
        self.beat("So which ones are public? Not because of the name. The route table decides.",
                  FadeOut(res), FadeIn(q), *[Indicate(s[1][0], color=YELLOW_M) for s in (*pub, *prv)], run_time=2.0)
        loc = M("10.0.0.0/16  local", 20, BLUE_M).move_to([-4.3, 1.8, 0])
        self.steps("Every route table has a local route. 10.0.0.0/16 goes to local, so all subnets in the VPC can reach each other.",
                   (1.2, FadeIn(loc)), (1.6, Wait(1.6)),
                   (1.2, self.dot_path([pub[0].get_center() + DOWN * 0.2, prv[1].get_center() + DOWN * 0.2], BLUE_M, 1.2)))

        net = box("Internet", WHITE, w=2.0, h=0.55, size=24).move_to([0, 3.3, 0])
        igw = mini("internet gateway", GOLD_M, w=2.7).move_to([0, vpc.get_top()[1], 0])
        def route(txt, s, color):
            return M(txt, 20, color).move_to(s.get_center() + UP * 0.1)
        rp = VGroup(*[route("0.0.0.0/0  internet gateway", s, GOLD_M) for s in pub])
        self.steps("A public subnet adds 0.0.0.0/0, the default route that means every address, to an internet gateway, the VPC's front door.",
                   (0.6, FadeOut(q), FadeIn(net)), (1.0, FadeIn(igw)), (1.4, LaggedStart(*[FadeIn(r) for r in rp], lag_ratio=0.3)),
                   (0.8, *[s[0].animate.set_stroke(TEAL_M) for s in pub]))
        lbs = VGroup(*[mini("load balancer", TEAL_M, w=2.2).move_to([x - 1.2, PY - 0.45, 0]) for x in AX])
        self.steps("So the load balancer goes here, in both zones. It can have a public address, and the internet can reach it.",
                   (1.0, LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in lbs], lag_ratio=0.3)),
                   (1.8, self.dot_path([net.get_bottom(), igw.get_center(), lbs[0].get_center()], YELLOW_M, 1.8)))

        rq = VGroup(*[route("0.0.0.0/0  NAT gateway", s, PURPLE_M) for s in prv])
        nats = VGroup(*[mini("NAT", PURPLE_M, w=1.4).move_to([x + 1.55, PY - 0.45, 0]) for x in AX])
        self.beat("A private subnet sends 0.0.0.0/0 to a NAT gateway instead. Each zone gets its own, in its public subnet.",
                  LaggedStart(*[FadeIn(r) for r in rq], lag_ratio=0.3), *[s[0].animate.set_stroke(PURPLE_M) for s in prv],
                  Succession(Wait(1.8), LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in nats], lag_ratio=0.3)), run_time=3.4)
        apps = VGroup(*[mini("app", PURPLE_M, w=1.4).move_to([x - 1.2, QY - 0.45, 0]) for x in AX])
        dbs = VGroup(*[mini("DB", PURPLE_M, w=1.4).move_to([x + 1.2, QY - 0.45, 0]) for x in AX])
        self.beat("The app and the database go in the private subnets.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in (apps[0], dbs[0], apps[1], dbs[1])], lag_ratio=0.2), run_time=1.6)
        self.steps("Their machines can reach out, for example to download packages. The NAT gateway sends them out, under its own public address.",
                   (2.2, self.dot_path([apps[0].get_top(), nats[0].get_bottom(), nats[0].get_center(), igw.get_center(), net.get_bottom()], PURPLE_M, 2.2)),
                   (1.2, Wait(1.2)), (0.6, Indicate(nats[0], color=PURPLE_M)))
        blk = tick(False, 0.25).move_to(nats[0].get_center() + DOWN * 0.62)
        self.steps("But nobody outside can start a connection to them. Only replies get back in.",
                   (1.6, self.dot_path([net.get_bottom(), igw.get_center(), nats[0].get_center(), nats[0].get_center() + DOWN * 0.62], RED_M, 1.6)),
                   (0.5, Create(blk)))
        self.steps("So the request goes to the load balancer, and the load balancer forwards it to the app. That follows the local route. 10.0.0.0/16 is more specific than 0.0.0.0/0, so the traffic stays inside the VPC.",
                   (0.4, FadeOut(blk)),
                   (2.2, self.dot_path([net.get_bottom(), igw.get_center(), lbs[0].get_center(), apps[0].get_center()], YELLOW_M, 2.2)),
                   (1.0, Indicate(loc, color=BLUE_M)))
        self.beat("Even a wrong firewall rule cannot expose the app directly. It has no public address, and no route in from the internet.",
                  *[Indicate(m, color=PURPLE_M) for m in (*apps, *dbs)], run_time=2.0)

        # 5. a zone fails
        A = VGroup(pub[0], prv[0], lbs[0], nats[0], apps[0], dbs[0], rp[0], rq[0])
        self.beat("Now zone a loses power.",
                  cols[0].animate.set_stroke(RED_M), A.animate.set_opacity(0.25), azl[0].animate.set_color(RED_M), run_time=1.4)
        self.steps("Zone b keeps working. It has its own load balancer, its own app, and its own NAT gateway, because each private subnet routes to the NAT in its own zone.",
                   (2.2, self.dot_path([net.get_bottom(), igw.get_center(), lbs[1].get_center(), apps[1].get_center()], YELLOW_M, 2.2)),
                   (1.6, Wait(1.6)),
                   (2.2, self.dot_path([apps[1].get_top(), nats[1].get_bottom(), nats[1].get_center(), igw.get_center(), net.get_bottom()], PURPLE_M, 2.2)))
        self.beat("One shared NAT gateway would be cheaper, and many teams accept that for test environments.",
                  Indicate(nats[1], color=PURPLE_M), run_time=1.6)

        # 6. what bills while idle
        bill = chip("bills every hour, even idle", GOLD_M, 22).move_to([3.7, 3.3, 0])
        hl = VGroup(*[SurroundingRectangle(m, color=GOLD_M, buff=0.07, corner_radius=0.12, stroke_width=4) for m in (*lbs, *nats)])
        self.beat("And watch the bill. The load balancer and the two NAT gateways bill every hour, even with no traffic.",
                  cols[0].animate.set_stroke(GREY_B), A.animate.set_opacity(1), azl[0].animate.set_color(GREY_B),
                  Succession(Wait(1.6), AnimationGroup(FadeIn(bill, shift=DOWN * 0.1), *[Create(h) for h in hl])), run_time=3.4)
        self.beat("So that is the list you delete first, after a test.",
                  *[Wiggle(VGroup(m, h)) for m, h in zip((*lbs, *nats), hl)], run_time=1.6)

        # 7. recap
        rc = T("spread copies across zones; the route table makes a subnet public or private", 24, WHITE)
        fit(rc, 12.4).move_to([0, 3.3, 0])
        self.beat("Spread copies across zones. And remember, the route table, not the name, makes a subnet public or private.",
                  FadeOut(VGroup(net, bill, hl)), FadeIn(rc, shift=DOWN * 0.1), run_time=2.4)
        self.wait(1.2)
