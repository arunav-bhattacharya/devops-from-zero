import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *
import re

# spoken form of addresses for this scene only (captions keep the real spelling)
_LOCAL = [(re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b"), r"\1 dot \2 dot \3 dot \4")]


def _say(t):
    for p, r in _LOCAL:
        t = p.sub(r, t)
    return t


def panel(title, rows, color, size=20, w=None):
    head = T(title, 22, color)
    body = VGroup(*[M(r, size) if isinstance(r, str) else r for r in rows]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    inner = VGroup(head, body).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    r = RoundedRectangle(corner_radius=0.1, width=w or inner.width + 0.5, height=inner.height + 0.4, stroke_color=color, stroke_width=2.5)
    r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.1), opacity=1)
    inner.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.25)
    return VGroup(r, inner)


def ring_flash(p, color):
    c = Circle(radius=0.12, stroke_color=color, stroke_width=5).move_to(p)
    return Succession(FadeIn(c, run_time=0.05), c.animate(run_time=0.5).scale(3.2).set_stroke(opacity=0), FadeOut(c, run_time=0.05))


class D14RequestPath(VoiceScene):
    def beat(self, text, *anims, run_time=None, after=0.25):
        path, dur = voice(_say(text))
        self._cue(text, dur)
        self.add_sound(path)
        if anims:
            rt = min(run_time if run_time else max(0.8, dur * 0.55), max(0.5, dur))
            self.play(*anims, run_time=rt)
            rest = dur - rt
        else:
            rest = dur
        if rest > 0.02:
            self.wait(rest)
        if after:
            self.wait(after)

    def construct(self):
        self.title_card("One request to your own server", "VPC, route table, internet gateway and security group")

        # ---------- 1. build the network
        vpc = RoundedRectangle(corner_radius=0.2, width=9.75, height=6.5, stroke_color=BLUE_M, stroke_width=3).move_to([1.875, -0.3, 0])
        vpc.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(BLUE_M), 0.05), opacity=1).set_z_index(-3)
        vpc_l = VGroup(T("VPC", 26, BLUE_M), M("172.31.0.0/16", 22, BLUE_M)).arrange(RIGHT, buff=0.25)
        vpc_l.next_to(vpc.get_corner(UL), DR, buff=0.18).shift(RIGHT * 0.9)
        self.beat("Your server lives inside a VPC, your own private network in AWS. The default VPC is the block 172.31.0.0/16.",
                  Create(vpc), FadeIn(vpc_l), run_time=2.2)

        sub = RoundedRectangle(corner_radius=0.15, width=5.8, height=3.5, stroke_color=GREEN_M, stroke_width=2.5).move_to([1.4, 0.6, 0])
        sub.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(GREEN_M), 0.06), opacity=1).set_z_index(-2)
        sub_l = VGroup(T("public subnet", 24, GREEN_M), M("172.31.0.0/20", 22, GREEN_M)).arrange(RIGHT, buff=0.25)
        sub_l.next_to(sub.get_corner(UL), DR, buff=0.15)
        self.beat("Each availability zone gets one /20 subnet. That is 4,096 addresses, minus the 5 that AWS keeps.",
                  Create(sub), FadeIn(sub_l), run_time=2.0)

        ec2_t = VGroup(T("EC2: hello-devops", 24), M("private 172.31.0.5", 20, TEAL_M), M("gunicorn on 0.0.0.0:8000", 20, GREY_B), M("SSM Agent", 20, PURPLE_M)).arrange(DOWN, buff=0.12)
        ec2_r = RoundedRectangle(corner_radius=0.12, width=3.9, height=1.8, stroke_color=TEAL_M, stroke_width=3)
        ec2_r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(TEAL_M), 0.14), opacity=1)
        ec2 = VGroup(ec2_r, ec2_t.move_to(ec2_r)).move_to([1.4, 0.5, 0])
        ec2_t[3].set_opacity(0)
        self.beat("Your server lands in one of them. It only knows its private address, 172.31.0.5.",
                  Create(ec2_r), Write(ec2_t[0]), Succession(Wait(0.8), FadeIn(ec2_t[1])), run_time=2.4)
        self.beat("On it, gunicorn listens on 0.0.0.0, port 8000, so outside traffic can reach it. Something else decides who may.",
                  FadeIn(ec2_t[2], shift=UP * 0.1), run_time=1.4)

        igw_t = VGroup(T("internet gateway", 22), M("54.214.91.141", 20, GOLD_M), M("172.31.0.5", 20, TEAL_M)).arrange(DOWN, buff=0.1)
        igw_t[1:].set_opacity(0)
        igw_r = RoundedRectangle(corner_radius=0.12, width=2.6, height=1.45, stroke_color=GOLD_M, stroke_width=3)
        igw_r.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(GOLD_M), 0.16), opacity=1)
        igw = VGroup(igw_r, igw_t.move_to(igw_r)).move_to([vpc.get_left()[0], 0.75, 0])
        self.beat("An internet gateway is attached to the VPC. It is the VPC's front door.",
                  GrowFromCenter(igw), run_time=1.4)

        rt_rows = [M("172.31.0.0/16  →  local", 20), M("0.0.0.0/0      →  igw-...", 20)]
        rtab = panel("route table", rt_rows, GREEN_M).move_to([-0.55, -2.4, 0])
        rt_link = DashedLine(sub.get_bottom() + LEFT * 1.95, rtab.get_top() + RIGHT * 0.0, dash_length=0.08, stroke_width=2, color=GREEN_M)
        rt_link.put_start_and_end_on(np.array([-0.55, sub.get_bottom()[1], 0]), np.array([-0.55, rtab.get_top()[1], 0]))
        rows = rtab[1][1]
        rows[1].set_opacity(0)
        self.beat("The subnet's route table has two rules. Addresses inside the VPC stay local.",
                  Create(rt_link), FadeIn(rtab[0]), FadeIn(rtab[1][0]), Succession(Wait(0.6), FadeIn(rows[0], shift=RIGHT * 0.1)), run_time=2.2)
        to_igw = DashedLine(rtab.get_left() + UP * 0.0, igw.get_bottom(), dash_length=0.08, stroke_width=2, color=GOLD_M)
        to_igw.put_start_and_end_on(rows[1].get_left() + LEFT * 0.35, igw.get_bottom() + DOWN * 0.05)
        self.beat("And 0.0.0.0/0, which means every address, goes to the internet gateway. That one route is what makes the subnet public.",
                  rows[1].animate.set_opacity(1), Succession(Wait(1.6), Create(to_igw), Indicate(rows[1], color=GOLD_M)), run_time=3.6)

        pair = igw_t[1:]
        swap = VGroup(T("public", 20, GOLD_M), T("private", 20, TEAL_M)).arrange(DOWN, buff=0.12, aligned_edge=RIGHT).next_to(igw, LEFT, buff=0.2).shift(DOWN * 0.18)
        self.beat("The server also gets a public address, but it never sees it. The internet gateway holds the pair, and swaps one for the other.",
                  Succession(Wait(1.0), AnimationGroup(pair.animate.set_opacity(1), FadeIn(swap, shift=RIGHT * 0.1)), Wait(0.6), Swap(pair[0], pair[1]), Swap(pair[0], pair[1])), run_time=5.0)

        sg = DashedVMobject(SurroundingRectangle(ec2, buff=0.25, corner_radius=0.15), num_dashes=70).set_stroke(RED_M, 3)
        sg_l = T("security group", 20, RED_M).next_to(sg, DOWN, buff=0.05)
        sgp = panel("security group  hello-devops-web", [M("in:   none", 20, RED_M), M("out:  all", 20)], RED_M, w=4.75).move_to([4.15, -2.4, 0])
        sg_link = DashedLine([4.15, sg.get_bottom()[1], 0], [4.15, sgp.get_top()[1], 0], dash_length=0.08, stroke_width=2, color=RED_M)
        self.beat("Last, the firewall. A security group wraps the server. The lab's group, hello-devops-web, starts with no inbound rules at all.",
                  Create(sg), FadeIn(sg_l), Succession(Wait(1.2), AnimationGroup(Create(sg_link), FadeIn(sgp))), run_time=3.4)
        self.wait(0.3)

        # ---------- 2. one request, dropped
        mac = VGroup(T("your Mac", 24), M("203.0.113.7", 20, GREY_B)).arrange(DOWN, buff=0.08)
        mac_r = RoundedRectangle(corner_radius=0.12, width=2.0, height=0.95, stroke_color=WHITE, stroke_width=3).set_fill(BLACK, 1)
        macg = VGroup(mac_r, mac.move_to(mac_r)).move_to([-5.75, 2.6, 0])
        src = M("from 203.0.113.7", 22)
        dst = M("to 54.214.91.141:8000", 22, YELLOW_M)
        readout = VGroup(src, dst).arrange(RIGHT, buff=0.6).move_to([2.0, 3.42, 0])
        p_in1 = Line(macg.get_corner(DR) + LEFT * 0.2, igw.get_corner(UL) + RIGHT * 0.2)
        p_in2 = Line(igw.get_right(), sg.get_left() + UP * 0.3)
        p_in3 = Line(sg.get_left() + UP * 0.3, ec2.get_left() + UP * 0.3)
        wire = VGroup(Line(p_in1.get_start(), p_in1.get_end(), stroke_width=2, color=GREY_D),
                      Line(p_in2.get_start(), p_in3.get_end(), stroke_width=2, color=GREY_D)).set_z_index(-1)
        self.beat("Now send one request from your Mac, to the public address, on port 8000.",
                  FadeIn(macg, shift=RIGHT * 0.2), Create(wire), FadeIn(readout, shift=DOWN * 0.15), run_time=2.0)

        dot = Dot(p_in1.get_start(), radius=0.1, color=YELLOW_M)
        dst2 = M("to 172.31.0.5:8000", 22, TEAL_M).move_to(dst, aligned_edge=LEFT)
        self.beat("At the internet gateway, the public destination is swapped for the private one.",
                  Succession(FadeIn(dot, run_time=0.1), MoveAlongPath(dot, p_in1), AnimationGroup(Indicate(igw_t, color=GOLD_M, scale_factor=1.08), Transform(dst, dst2))), run_time=2.6)
        drop_x = tick(False, 0.2).move_to(sg.get_left() + UP * 0.3)
        self.beat("Inside, it reaches the security group. No rule allows it, so the packet is dropped. Silently.",
                  Succession(MoveAlongPath(dot, p_in2), AnimationGroup(FadeOut(dot, scale=0.3), ring_flash(p_in2.get_end(), RED_M), Create(drop_x)),
                             Indicate(sgp[1][1][0], color=RED_M)), run_time=2.8)
        tout = M("timed out", 22, RED_M).next_to(macg, DOWN, buff=0.25)
        self.beat("Your curl hears nothing back, and times out. Day 10 said a timeout means a drop. Here is the drop.",
                  FadeIn(tout, shift=UP * 0.1), Succession(Wait(2.0), Circumscribe(drop_x, color=RED_M, shape=Circle, buff=0.1)), run_time=3.4)

        # ---------- 3. one rule, and the full round trip
        rule = M("in:   8000 from 203.0.113.7/32", 20, GREEN_M).move_to(sgp[1][1][0], aligned_edge=LEFT)
        self.beat("So add one inbound rule. TCP port 8000, from your own address only, as a /32.",
                  FadeOut(tout), FadeOut(drop_x), Transform(dst, M("to 54.214.91.141:8000", 22, YELLOW_M).move_to(dst2, aligned_edge=LEFT)),
                  ReplacementTransform(sgp[1][1][0], rule), sg.animate.set_stroke(GREEN_M), sg_l.animate.set_color(GREEN_M), run_time=2.4)

        dot = Dot(p_in1.get_start(), radius=0.1, color=YELLOW_M)
        self.beat("Send it again. The gateway swaps the address. The security group finds a matching rule, and lets it in.",
                  Succession(FadeIn(dot, run_time=0.1), MoveAlongPath(dot, p_in1), AnimationGroup(Transform(dst, dst2.copy()), Indicate(igw_t, color=GOLD_M, scale_factor=1.08)),
                             MoveAlongPath(dot, p_in2), AnimationGroup(ring_flash(p_in2.get_end(), GREEN_M), Indicate(rule, color=GREEN_M)),
                             MoveAlongPath(dot, p_in3), FadeOut(dot, scale=0.3)), run_time=4.4)

        # the reply
        r_src = M("from 172.31.0.5:8000", 22, TEAL_M).move_to(src, aligned_edge=LEFT)
        r_dst = M("to 203.0.113.7", 22).next_to(r_src, RIGHT, buff=0.6)
        rdot = Dot(ec2.get_left() + DOWN * 0.3, radius=0.1, color=GREEN_M)
        out1 = Line(ec2.get_left() + DOWN * 0.3, sg.get_left() + DOWN * 0.3)
        self.beat("gunicorn answers. The reply needs no rule of its own. The security group is stateful. It remembers the connection, and lets the answer out.",
                  Indicate(ec2_t[2], color=TEAL_M), Transform(src, r_src), Transform(dst, r_dst),
                  Succession(Wait(2.2), FadeIn(rdot, run_time=0.1), MoveAlongPath(rdot, out1), ring_flash(out1.get_end(), GREEN_M)), run_time=4.6)
        out2 = Line(out1.get_end(), rows[1].get_right() + RIGHT * 0.15)
        out3 = Line(rows[1].get_left() + LEFT * 0.35, igw.get_bottom() + DOWN * 0.05)
        self.beat("Your Mac's address is outside the VPC, so the only route that matches is 0.0.0.0/0, to the internet gateway.",
                  Succession(MoveAlongPath(rdot, out2), Indicate(rows[1], color=GOLD_M), MoveAlongPath(rdot, out3)), run_time=3.6)
        back1 = Line(igw.get_corner(UL) + RIGHT * 0.2, macg.get_corner(DR) + LEFT * 0.2)
        r_src2 = M("from 54.214.91.141:8000", 22, YELLOW_M).move_to(src, aligned_edge=LEFT)
        hello = M('200  {"message": "Hello from EC2"}', 22, GREEN_M).move_to([2.0, 3.42, 0])
        self.beat("The gateway swaps the private source back to the public one. So your Mac gets its answer from the address it called.",
                  Succession(AnimationGroup(Indicate(igw_t, color=GOLD_M, scale_factor=1.08), Transform(src, r_src2), dst.animate.next_to(r_src2, RIGHT, buff=0.6)),
                             MoveAlongPath(rdot, back1), AnimationGroup(FadeOut(rdot), Indicate(mac, color=GREEN_M, scale_factor=1.08))), run_time=4.0)
        self.play(FadeOut(VGroup(src, dst), shift=UP * 0.1), FadeIn(hello, shift=UP * 0.1), run_time=0.8)

        # ---------- 4. no port 22: Session Manager
        p22 = VGroup(M("22", 22, RED_M), tick(False, 0.14)).arrange(RIGHT, buff=0.12)
        p22_r = RoundedRectangle(corner_radius=0.08, width=p22.width + 0.3, height=0.5, stroke_color=RED_M, stroke_width=2).set_fill(BLACK, 1)
        p22g = VGroup(p22_r, p22.move_to(p22_r)).move_to(sg.get_right() + RIGHT * 0.22 + UP * 0.45)
        self.beat("Port 8000 is open to you alone, and port 22 stays closed. So how do you get a shell on the server?",
                  Indicate(rule, color=GREEN_M), FadeIn(p22g, scale=0.8), run_time=2.4)

        ssm = box("Systems Manager", PURPLE_M, w=2.75, h=0.8, size=22).move_to([-5.4, -2.35, 0])
        agent = ec2_t[3]
        ya = agent.get_center()[1]
        conn = VMobject(stroke_color=PURPLE_M, stroke_width=4).set_points_as_corners(
            [np.array([ec2.get_left()[0], ya, 0]), np.array([igw.get_right()[0], 0.2, 0]), np.array([igw.get_left()[0], 0.2, 0]), ssm.get_corner(UR) + LEFT * 0.4])
        conn.set_z_index(-1)
        conn_l = T("outbound\nHTTPS", 20, PURPLE_M).move_to([-5.5, -0.95, 0])
        self.beat("With Session Manager. A small program on the server, the SSM Agent, keeps an outbound HTTPS connection open to Systems Manager.",
                  FadeOut(hello), agent.animate.set_opacity(1), Succession(Wait(1.6), AnimationGroup(FadeIn(ssm), Create(conn), FadeIn(conn_l))), run_time=4.2)
        rev = conn.copy().reverse_points()
        self.beat("Outbound is allowed by default. And because the security group is stateful, traffic on that connection flows both ways.",
                  Indicate(sgp[1][1][1], color=PURPLE_M),
                  Succession(Wait(1.6), AnimationGroup(travel(conn, PURPLE_M, run_time=1.4), travel(rev, YELLOW_M, run_time=1.4))), run_time=3.6)
        cmd = M("$ aws ssm start-session --target i-...", 22).move_to([2.0, 3.42, 0])
        ss_arrow = Arrow([-6.45, macg.get_bottom()[1], 0], [-6.45, ssm.get_top()[1], 0], buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.06)
        iam = VGroup(tick(True, 0.15), T("IAM check", 22, GREEN_M)).arrange(RIGHT, buff=0.12).next_to(ssm, DOWN, buff=0.2)
        self.beat("On your Mac, you run start-session. AWS checks your IAM permissions, and joins your terminal to that connection.",
                  FadeIn(cmd, shift=DOWN * 0.1), GrowArrow(ss_arrow), Succession(Wait(1.8), FadeIn(iam)), Succession(Wait(2.4), travel(conn, PURPLE_M, run_time=1.0)), run_time=4.0)
        prompt = M("ssm-user@ip-172-31-0-5:~$", 22, GREEN_M).move_to([2.0, 3.42, 0])
        self.beat("You arrive as ssm-user. No port to open, and no key to lose.",
                  ReplacementTransform(cmd, prompt), Indicate(p22, color=RED_M), run_time=2.0)

        # ---------- recap: walk the path once more
        self.beat("So one request: the route table points to the gateway, the gateway swaps the address, and the security group opens one port. And Session Manager dials out, so port 22 stays shut.",
                  Succession(Circumscribe(rows[1], color=GOLD_M, buff=0.06), Circumscribe(igw, color=GOLD_M, buff=0.06),
                             Circumscribe(rule, color=GREEN_M, buff=0.06), Wait(0.6), AnimationGroup(travel(conn, PURPLE_M, run_time=1.2), Indicate(p22, color=RED_M))), run_time=9.0)
        self.wait(1.2)
