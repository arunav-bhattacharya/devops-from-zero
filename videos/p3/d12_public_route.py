import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"10\.0\.0\.0/16", "10 dot 0 dot 0 dot 0 slash 16"), (r"0\.0\.0\.0/0", "0 dot 0 dot 0 dot 0 slash 0"),
    (r"10\.0\.11\.5", "10 dot 0 dot 11 dot 5"), (r"\bPayFlow\b", "Pay flow"), (r"\bpublic-a\b", "public A"), (r"\bpublic-b\b", "public B"),
    (r"\bprivate-a\b", "private A"), (r"\bprivate-b\b", "private B"), (r"\bprivate-x\b", "private X"), (r"/24\b", " slash 24"),
    (r"\blb-sg\b", "L B S G"), (r"\bapp-sg\b", "app S G"), (r"\bdb-sg\b", "D B S G"), (r"\bIPv4\b", "I P V 4"),
])

PUB, PRIV, IGW, NAT, LB, APP, DB = GREEN_M, BLUE_M, GOLD_M, PURPLE_M, YELLOW_M, TEAL_M, GREY_B
AZX = {"a": -4.4, "b": -0.4}
PUB_Y, PRIV_Y = 0.55, -1.45
SUB_W, SUB_H = 3.3, 1.6


def tint(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def subnet(name, cidr, color, x, y):
    r = RoundedRectangle(corner_radius=0.12, width=SUB_W, height=SUB_H, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), 1).move_to([x, y, 0])
    n = M(name, 22, color).move_to(r.get_corner(UL) + RIGHT * 0.15 + DOWN * 0.25, aligned_edge=LEFT)
    c = M(cidr, 22, GREY_B).move_to(r.get_corner(UR) + LEFT * 0.15 + DOWN * 0.25, aligned_edge=RIGHT)
    return VGroup(r, n, c)


def thing(label, color, size=24):
    return chip(label, color, size)


def rt_card(title, rows, color, w=4.3):
    t = T(title, 26, color)
    rr = VGroup(*[VGroup(M(d, 22), T(tg, 24, c)).arrange(RIGHT, buff=0.35) for d, tg, c in rows])
    for r in rr:
        r[1].move_to(r[0].get_right() + RIGHT * (1.75 - r[0].width + 0.35), aligned_edge=LEFT)
    rr.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    box_ = RoundedRectangle(corner_radius=0.12, width=w, height=rr.height + 1.05, stroke_color=color, stroke_width=2.5).set_fill(BLACK, 1)
    t.move_to(box_.get_top() + DOWN * 0.32)
    rr.next_to(t, DOWN, buff=0.22).align_to(box_, LEFT).shift(RIGHT * 0.25)
    return VGroup(box_, t, rr)


class D12PublicRoute(VoiceScene):
    def construct(self):
        self.title_card("What makes a subnet public?", "a private floor, two buildings, and the doors between them")

        # ---------- 1. the hotel and the question
        h1 = T("build a house", 34, GREY_B)
        h2 = T("rent a hotel room", 34, IGW)
        hg = VGroup(h1, h2).arrange(RIGHT, buff=2.0).move_to(UP * 0.5)
        x = tick(False, 0.3).next_to(h1, DOWN, buff=0.3)
        ok = tick(True, 0.3).next_to(h2, DOWN, buff=0.3)
        self.beat("For a friend's wedding in another city, you book a hotel room for two nights. Nobody builds a house for a weekend. Renting computers that way is the cloud.",
                  FadeIn(h1), Succession(Wait(2.4), AnimationGroup(Create(x), FadeIn(h2))), Succession(Wait(4.0), Create(ok)), run_time=7.0)
        q = T("If I call a subnet “public”, is it public?", 34, YELLOW_M).move_to(DOWN * 1.8)
        self.beat("Today we rent a whole private floor of the hotel, and decide which rooms the street can reach. And here's the question people are shy to ask. If I call a network public, is it public? Hold that thought.",
                  Succession(Wait(6.0), FadeIn(q, shift=UP * 0.1)), run_time=9.0)
        self.play(FadeOut(VGroup(hg, x, ok, q)), run_time=0.6)

        # ---------- 2. the floor: VPC, two buildings, four subnets
        vpc = RoundedRectangle(corner_radius=0.2, width=8.2, height=5.0, stroke_color=WHITE, stroke_width=2.5).move_to([-2.4, -0.4, 0])
        vl = M("VPC 10.0.0.0/16", 24).move_to(vpc.get_corner(DL) + RIGHT * 0.2 + UP * 0.28, aligned_edge=LEFT)
        self.beat("PayFlow, a made-up payments company, wants its checkout to run in the cloud. First, the floor. A VPC is your own private network inside the provider. You give it a private block, 10.0.0.0/16, which is 65,536 addresses.",
                  Succession(Wait(5.0), AnimationGroup(Create(vpc), FadeIn(vl))), run_time=10.0)
        azs = VGroup()
        for k, xx in AZX.items():
            r = DashedVMobject(RoundedRectangle(corner_radius=0.15, width=3.7, height=4.3, stroke_color=GREY_B, stroke_width=2).move_to([xx, -0.25, 0]), num_dashes=60)
            l = T(f"zone {k}", 24, GREY_B).next_to(r.get_top(), DOWN, buff=0.12)
            azs.add(VGroup(r, l))
        self.beat("The floor spans two availability zones. In hotel terms, two separate buildings across town, each on its own power supply.",
                  LaggedStart(*[Create(a[0]) for a in azs], lag_ratio=0.4), LaggedStart(*[FadeIn(a[1]) for a in azs], lag_ratio=0.4), run_time=3.0)
        subs = {
            "pa": subnet("public-a", "10.0.1.0/24", PUB, AZX["a"], PUB_Y), "pb": subnet("public-b", "10.0.2.0/24", PUB, AZX["b"], PUB_Y),
            "va": subnet("private-a", "10.0.11.0/24", PRIV, AZX["a"], PRIV_Y), "vb": subnet("private-b", "10.0.12.0/24", PRIV, AZX["b"], PRIV_Y),
        }
        self.beat("Then you split the block into subnets, smaller blocks of rooms. In AWS, each subnet lives in exactly one zone, so we need some in both. Four /24s, each with 251 usable addresses, because AWS keeps five of every subnet for itself.",
                  Succession(Wait(2.0), LaggedStart(*[FadeIn(s, shift=DOWN * 0.1) for s in subs.values()], lag_ratio=0.4)), run_time=11.0)

        # ---------- 3. the obvious model: the name makes it public. Break it.
        igw = box("internet gateway", IGW, w=3.0, h=0.7, size=24).move_to([-2.4, 2.45, 0])
        net = T("the internet", 26, GREY_B).next_to(igw, UP, buff=0.18)
        self.beat("Now our question. The one called public-a. Is it public? The obvious answer is yes. It says so on the door.",
                  Indicate(subs["pa"][1], color=PUB, scale_factor=1.3), run_time=2.4)
        rt = rt_card("public-a's route table", [("10.0.0.0/16", "local", GREY_B)], PUB).move_to([4.35, 0.6, 0])
        self.beat("Let's see if that's really true. What decides where traffic goes is the subnet's route table. Say public-a's table has just one line. 10.0.0.0/16, local. Every subnet on the floor can reach every other one.",
                  Succession(Wait(3.2), FadeIn(rt, shift=LEFT * 0.2)), run_time=9.0)
        self.beat("And that's all it has. No way in from the street, and no way out. Pause and guess. With this table, is public-a public?",
                  FadeIn(net), run_time=1.6, after=2.2)
        stuck = T("not public, whatever it's called", 26, RED_M).next_to(rt, DOWN, buff=0.3)
        self.beat("No. It's a room with a sign on the door that says, street view. The sign doesn't build a window.",
                  FadeIn(stuck, shift=UP * 0.1), run_time=1.6)
        row2 = VGroup(M("0.0.0.0/0", 22), T("internet gateway", 24, IGW))
        row2[1].move_to(row2[0].get_right() + RIGHT * (1.75 - row2[0].width + 0.35), aligned_edge=LEFT)
        row2.next_to(rt[2], DOWN, buff=0.22, aligned_edge=LEFT)
        rt2 = rt_card("public-a's route table", [("10.0.0.0/16", "local", GREY_B), ("0.0.0.0/0", "internet gateway", IGW)], PUB).move_to(rt)
        self.beat("Now add one line. 0.0.0.0/0, which means every address, goes to the internet gateway, the floor's front door to the street.",
                  FadeOut(stuck), Transform(rt, rt2), Succession(Wait(4.6), FadeIn(igw, shift=DOWN * 0.15)), run_time=7.0)
        door = Line(igw[0].get_bottom() + LEFT * 1.0, subs["pa"][0].get_top() + RIGHT * 0.6, stroke_width=3, color=IGW)
        self.beat("That line is what makes public-a public. Not its name. Its route table.",
                  Create(door), Indicate(rt[2][1], color=IGW), run_time=2.0)
        self.beat("Same question, one more time. A packet for 10.0.11.5 matches both lines. Which one wins? Pause and guess.",
                  Indicate(rt[2][0], color=WHITE), Indicate(rt[2][1], color=WHITE), run_time=2.0, after=2.2)
        self.beat("The more specific one, 10.0.0.0/16, wins over every address. So traffic between subnets stays on the floor.",
                  Indicate(rt[2][0][0], color=GREY_B, scale_factor=1.2), run_time=2.0)

        # ---------- 4. private subnets: the mail desk
        nat_a = thing("NAT gateway", NAT, 22).move_to(subs["pa"][0].get_center() + DOWN * 0.25 + RIGHT * 0.6)
        lb = thing("load balancer", LB, 22).move_to(subs["pa"][0].get_center() + DOWN * 0.25 + LEFT * 0.75)
        self.play(FadeOut(rt), run_time=0.5)
        rtp = rt_card("private-a's route table", [("10.0.0.0/16", "local", GREY_B), ("0.0.0.0/0", "NAT gateway", NAT)], PRIV).move_to([4.35, -1.2, 0])
        self.beat("The private subnets get a different second line. 0.0.0.0/0 goes to a NAT gateway instead, which sits in a public subnet.",
                  FadeIn(rtp, shift=LEFT * 0.2), Succession(Wait(4.0), FadeIn(nat_a, scale=0.8)), run_time=6.4)
        app = thing("app", APP).move_to(subs["va"][0].get_center() + DOWN * 0.2 + LEFT * 0.75)
        db = thing("database", DB).move_to(subs["va"][0].get_center() + DOWN * 0.2 + RIGHT * 0.7)
        self.beat("The usual layout puts the load balancer in a public subnet, and the app and the database in private ones.",
                  FadeIn(lb, scale=0.8), Succession(Wait(2.6), AnimationGroup(FadeIn(app, scale=0.8), FadeIn(db, scale=0.8))), run_time=4.6)
        outp = VMobject().set_points_as_corners([app.get_top(), nat_a.get_bottom() + DOWN * 0.05])
        outp2 = VMobject().set_points_as_corners([nat_a.get_top(), igw[0].get_bottom() + RIGHT * 0.6])
        self.beat("The NAT gateway is the hotel's mail desk. The app can send letters out, say to download a package, and the replies come back.",
                  Succession(Wait(2.0), MoveAlongPath(Dot(color=NAT, radius=0.08), outp, run_time=1.0), MoveAlongPath(Dot(color=NAT, radius=0.08), outp2, run_time=1.0)), run_time=5.4)
        for m in list(self.mobjects):
            if isinstance(m, Dot):
                self.remove(m)
        stranger = Dot(color=RED_M, radius=0.09).move_to(net.get_right() + RIGHT * 0.6)
        blocked = tick(False, 0.28).move_to(subs["va"][0].get_top() + UP * 0.05 + LEFT * 1.2)
        self.beat("But no visitor goes upstairs. Nobody outside can start a connection to the app. It has no public address, and no route in.",
                  Succession(FadeIn(stranger, run_time=0.4), stranger.animate(run_time=1.6).move_to(subs["va"][0].get_top() + UP * 0.25 + LEFT * 1.2)), Succession(Wait(2.0), Create(blocked)), run_time=5.0)
        self.beat("So even a wrong firewall rule can't expose it directly. That's a nice property to get for free.",
                  FadeOut(stranger), FadeOut(blocked), run_time=1.6)

        # ---------- 5. locks on the doors: security groups in a chain
        self.play(FadeOut(rtp), run_time=0.5)
        sg = VGroup(M("lb-sg    inbound 443    from 0.0.0.0/0", 22, LB), M("app-sg   inbound 8000   from lb-sg", 22, APP),
                    M("db-sg    inbound 5432   from app-sg", 22, DB)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        sgt = T("security groups", 26, WHITE)
        sgb = RoundedRectangle(corner_radius=0.12, width=sg.width + 0.5, height=sg.height + 1.1, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1)
        sgt.move_to(sgb.get_top() + DOWN * 0.32)
        sg.next_to(sgt, DOWN, buff=0.22)
        sgg = VGroup(sgb, sgt, sg)
        fit(sgg, 4.5).move_to([4.45, -0.4, 0])
        self.beat("Routes decide where traffic may go. Locks decide who gets in. In AWS, each machine has a security group, a lock on its own door, and we chain them.",
                  FadeIn(sgb), FadeIn(sgt), run_time=2.0)
        p1 = VMobject().set_points_as_corners([igw[0].get_bottom() + LEFT * 1.0, lb.get_top()])
        p2 = VMobject().set_points_as_corners([lb.get_bottom(), app.get_top()])
        p3 = VMobject().set_points_as_corners([app.get_right(), db.get_left()])
        self.beat("The load balancer accepts port 443 from anywhere.",
                  FadeIn(sg[0]), MoveAlongPath(Dot(color=LB, radius=0.08), p1), run_time=2.0)
        self.beat("The app accepts port 8000 only from the load balancer's group.",
                  FadeIn(sg[1]), MoveAlongPath(Dot(color=APP, radius=0.08), p2), run_time=2.0)
        self.beat("And the database accepts 5432 only from the app's group. Rules name groups, not addresses, so they keep working when machines come and go.",
                  FadeIn(sg[2]), MoveAlongPath(Dot(color=DB, radius=0.08), p3), run_time=2.4)
        for m in list(self.mobjects):
            if isinstance(m, Dot):
                self.remove(m)
        self.beat("And replies need no rules at all. A security group remembers each connection, so the answer to an allowed request gets out on its own.",
                  Indicate(sgt, color=WHITE), run_time=1.6)
        self.play(FadeOut(sgg), run_time=0.5)

        # ---------- 6. two zones: one goes dark
        nat_b = thing("NAT gateway", NAT, 22).move_to(subs["pb"][0].get_center() + DOWN * 0.25 + RIGHT * 0.6)
        app_b = thing("app", APP).move_to(subs["vb"][0].get_center() + DOWN * 0.2 + LEFT * 0.75)
        db_b = thing("database", DB).move_to(subs["vb"][0].get_center() + DOWN * 0.2 + RIGHT * 0.7)
        self.beat("Zone b gets the same set. Its own app and database, and its own NAT gateway.",
                  LaggedStart(FadeIn(nat_b), FadeIn(app_b), FadeIn(db_b), lag_ratio=0.3), run_time=2.4)
        tables = VGroup(M("private-a  0.0.0.0/0  NAT in public-a", 22, PRIV), M("private-b  0.0.0.0/0  NAT in public-b", 22, PRIV)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        tables.move_to([0, 3.15, 0]).shift(RIGHT * 0.0)
        tb = VGroup(T("each private table", 24, PRIV), tables).arrange(DOWN, buff=0.15)
        fit(tb, 4.6).move_to([4.45, 0.9, 0])
        self.beat("And here's a small choice that matters. Each private subnet's table points to the NAT gateway in its own zone.",
                  FadeIn(tb, shift=LEFT * 0.2), run_time=2.0)
        self.beat("Pause and guess. Zone a loses power. Can the app in zone b still reach out?",
                  Indicate(azs[0][1], color=RED_M, scale_factor=1.3), run_time=1.6, after=2.2)
        za = VGroup(subs["pa"], subs["va"], lb, nat_a, app, db, azs[0], door)
        darkx = tick(False, 0.6).move_to(azs[0][0])
        self.beat("Zone a goes dark. But zone b's route goes to its own NAT gateway, so zone b can still reach out, and keeps working.",
                  za.animate.set_opacity(0.2), Create(darkx), Succession(Wait(3.0), MoveAlongPath(Dot(color=NAT, radius=0.08), VMobject().set_points_as_corners([app_b.get_top(), nat_b.get_bottom()]), run_time=1.2)), run_time=6.0)
        for m in list(self.mobjects):
            if isinstance(m, Dot):
                self.remove(m)
        self.beat("One shared NAT gateway would be cheaper, and many teams accept that for test environments. They just know that zone b then depends on zone a.",
                  Indicate(nat_b[1], color=NAT), run_time=1.6)
        self.play(FadeOut(darkx), za.animate.set_opacity(1), FadeOut(tb), run_time=0.7)

        # ---------- 7. guardrail: the rooms nobody sleeps in
        hour = VGroup(lb, nat_a, nat_b)
        bill = VGroup(T("bills every hour, even with no traffic:", 26, RED_M), T("load balancer, two NAT gateways, any public IPv4 address", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        fit(bill, 4.6).move_to([4.45, 0.4, 0])
        self.beat("Now remember the hotel bill. Some of these pieces bill every hour just for existing, even when no request arrives. The load balancer, the two NAT gateways, and any public IPv4 address.",
                  Succession(Wait(3.6), FadeIn(bill, shift=LEFT * 0.2), LaggedStart(*[Indicate(h[1], color=RED_M) for h in hour], lag_ratio=0.4)), run_time=10.0)
        alert = T("A budget alert only tells you. Deleting stops the bill.", 26, YELLOW_M)
        fit(alert, 4.6).next_to(bill, DOWN, buff=0.5)
        self.beat("Those are the rooms nobody sleeps in. A budget alert only sends you an email, it doesn't stop anything. So after a test, that list is what you delete first.",
                  FadeIn(alert, shift=UP * 0.1), run_time=2.0)

        # ---------- 8. moral and check
        everything = VGroup(vpc, vl, azs, *subs.values(), igw, net, door, lb, nat_a, app, db, nat_b, app_b, db_b, bill, alert)
        self.play(FadeOut(everything), run_time=0.7)
        m1 = T("The route table, not the name,", 40)
        m2 = T("makes a subnet public.", 40, PUB)
        mg = VGroup(m1, m2).arrange(DOWN, buff=0.25).move_to(UP * 1.4)
        rec = T("public: 0.0.0.0/0 to the internet gateway.  private: 0.0.0.0/0 to a NAT gateway.", 26, GREY_B).next_to(mg, DOWN, buff=0.6)
        fit(rec, 12.6)
        self.beat("So, the moral of the story. The route table, not the name, makes a subnet public. Every address to the internet gateway means public. Every address to a NAT gateway means private, out only.",
                  Write(m1), Succession(Wait(1.6), Write(m2)), Succession(Wait(5.6), FadeIn(rec)), run_time=10.0)
        self.play(VGroup(mg, rec).animate.scale(0.75).to_edge(UP, buff=0.8).set_opacity(0.6), run_time=0.6)
        c1 = M("subnet private-x:  0.0.0.0/0  ->  internet gateway", 26)
        c2 = T("Public or private?", 32, YELLOW_M)
        cg = VGroup(c1, c2).arrange(DOWN, buff=0.45).move_to(DOWN * 0.4)
        self.beat("A quick check. A subnet named private-x has a route that sends every address to the internet gateway. Public, or private? Pause and guess.",
                  FadeIn(c1), Succession(Wait(4.0), FadeIn(c2)), run_time=6.0, after=2.2)
        ans = T("Public. Whatever its name says.", 30, PUB).next_to(cg, DOWN, buff=0.5)
        self.beat("Public. The route table decides, whatever the name on the door says.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.5)
