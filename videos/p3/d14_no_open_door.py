import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bSSM\b", "S S M"), (r"\bssm-user\b", "S S M user"), (r"\bssm start-session\b", "S S M start session"),
            (r"\baws\b", "A W S"), (r"\bEC2\b", "E C two"), (r"\b0\.0\.0\.0/0\b", "zero zero zero zero slash zero"),
            (r"\.pem\b", " P E M"), (r"\bAmazonSSMManagedInstanceCore\b", "Amazon S S M managed instance core"),
            (r"\bssmmessages\b", "S S M messages"), (r"\bec2messages\b", "E C two messages"), (r"\blocalhost\b", "local host")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(w, h, color, k=0.10, sw=2.5):
    return RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, k), opacity=1)


def person(color=RED_M, s=1.0):
    head = Circle(radius=0.14, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), opacity=1)
    body = Arc(radius=0.24, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(head, DOWN, buff=0.04)
    return VGroup(head, body).scale(s)


class D14NoOpenDoor(VoiceScene):
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

    def guess(self, where):
        c = chip("pause and guess", YELLOW_M, 24).move_to(where)
        n = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        self.play(FadeIn(c), FadeIn(n), run_time=0.3)
        self.wait(0.85)
        self.play(Transform(n, T("1", 30, YELLOW_M).move_to(n)), run_time=0.15)
        self.wait(0.85)
        self.play(FadeOut(c), FadeOut(n), run_time=0.3)

    def construct(self):
        self.title_card("A server with no open door", "and how you still get in")

        # 1. the flat far away  [FAMILIAR]
        flat = panel(4.4, 3.4, GREEN_M, 0.08, 3).move_to([3.9, -0.9, 0])
        fl = T("the flat: your EC2 server", 26, GREEN_M).next_to(flat, UP, buff=0.2)
        app = box("hello-devops", GREEN_M, w=2.6, h=0.7, size=26).move_to(flat.get_center() + DOWN * 0.9 + RIGHT * 0.3)
        self.beat("Picture renting a flat in a city you will never visit. On AWS that flat is an EC2 instance, a virtual server you rent by the second.",
                  Create(flat), FadeIn(fl), run_time=2.4)
        note = chip("note for the caretaker", GOLD_M, 24).move_to(flat.get_center() + UP * 0.6 + RIGHT * 0.3)
        self.beat("You leave a note for the caretaker, and the server unpacks hello-devops, a tiny web app, all by itself.",
                  FadeIn(note, shift=DOWN * 0.1), Succession(Wait(1.6), FadeIn(app, shift=UP * 0.1)), run_time=3.0)
        self.play(FadeOut(note), run_time=0.4)
        door = Rectangle(width=0.22, height=1.4, stroke_width=0).set_fill(GOLD_M, opacity=1).move_to(flat.get_left() + DOWN * 0.3)
        dl = T("the lock: a security group", 26, GOLD_M).next_to(flat, DOWN, buff=0.25)
        self.beat("The flat's door has a lock. On AWS, the lock is a security group, a firewall wrapped around the server.",
                  FadeIn(door), FadeIn(dl), run_time=2.0)
        q = T("but how do I get in?", 32, YELLOW_M).move_to([-3.4, 2.9, 0])
        self.beat("Which brings up the question everybody has on day one. I can't walk in. So how do I get a shell on that machine?",
                  Write(q), run_time=2.0)

        # 2. the quick way: port 22 open to the world  [PAIN]
        mac = box("your Mac", TEAL_M, w=2.3, h=0.8, size=26).move_to([-5.2, -1.6, 0])
        crowd = VGroup(*[person(RED_M, 0.9) for _ in range(5)]).arrange(RIGHT, buff=0.25).move_to([-3.4, 1.5, 0])
        crl = T("the whole internet", 26, RED_M).next_to(crowd, DOWN, buff=0.2)
        p22 = chip("port 22 open to 0.0.0.0/0", RED_M, 24, mono=True).move_to(door.get_center() + LEFT * 2.0 + UP * 0.3)
        self.beat("Many tutorials take the quick way. They open port 22, the door for SSH, the secure remote login, to every address on the internet.",
                  FadeOut(q), FadeIn(mac), FadeIn(p22), run_time=2.4)
        knocks = VGroup(*[Arrow(p.get_bottom(), door.get_left() + UP * (0.5 - 0.25 * i), buff=0.12, stroke_width=2.5, color=RED_M,
                                max_tip_length_to_length_ratio=0.06) for i, p in enumerate(crowd)])
        self.beat("You can get in now. So can everyone else who wants to try. Every stranger on the internet can walk up and rattle that handle.",
                  LaggedStart(*[FadeIn(p, shift=DOWN * 0.1) for p in crowd], lag_ratio=0.2), FadeIn(crl),
                  Succession(Wait(1.2), LaggedStart(*[GrowArrow(k) for k in knocks], lag_ratio=0.2)), run_time=3.4)
        pem = chip("key pair: a .pem file", RED_M, 24).next_to(mac, UP, buff=0.35)
        self.beat("And the old key pair way adds a private key file you download once, and must never lose or leak. That is a front door key under the mat.",
                  FadeIn(pem, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(VGroup(knocks, crowd, crl, p22, pem)), run_time=0.6)

        # 3. the lab's group: no inbound rules  [WISH, PREDICT]
        rules = VGroup(M("inbound:  []", 24, GOLD_M), M("outbound: everything", 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rp = panel(rules.width + 0.5, rules.height + 0.45, GOLD_M).move_to([-1.3, -1.0, 0])
        rules.move_to(rp)
        rl = T("hello-devops-web", 26, GOLD_M).next_to(rp, UP, buff=0.18)
        self.beat("The lab does the opposite. Its security group, hello-devops-web, has no inbound rules at all. Outbound allows everything, by default.",
                  FadeIn(rl), Create(rp), FadeIn(rules[0]), Succession(Wait(1.8), FadeIn(rules[1])), run_time=3.2)
        x = tick(False, 0.3).move_to(door.get_center() + LEFT * 0.55)
        try1 = Arrow(mac.get_right(), door.get_left() + DOWN * 0.3, buff=0.1, stroke_width=3, color=TEAL_M, max_tip_length_to_length_ratio=0.06)
        self.beat("Nobody on the internet can start a connection to the server. You included. Congratulations: you have built the safest flat in the city, and even you can't get in.",
                  GrowArrow(try1), Succession(Wait(1.2), Create(x)), run_time=2.6)
        self.play(FadeOut(try1), FadeOut(x), run_time=0.4)
        qq = T("no inbound rules. Can traffic ever come in?", 28, YELLOW_M).move_to([-1.3, 2.9, 0])
        self.beat("So here is the puzzle. With zero inbound rules, can any traffic ever come in through that door?", FadeIn(qq), run_time=1.8)
        self.guess([-1.3, 2.2, 0])

        # 4. break the wrong model: the lock is stateful  [BREAK]
        pkgs = box("packages online", GREY_B, w=2.9, h=0.8, size=26).move_to([-1.3, 1.6, 0])
        out = Arrow(door.get_left() + UP * 0.3, pkgs.get_right() + DOWN * 0.1, buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.08)
        back = Arrow(pkgs.get_right() + DOWN * 0.3, door.get_left() + UP * 0.05, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        self.beat("It is tempting to say no, never. Let's test that. On first boot, the server downloads packages. That is the server calling out, and outbound is allowed.",
                  FadeOut(qq), FadeIn(pkgs), Succession(Wait(2.6), GrowArrow(out)), run_time=3.6)
        self.steps("But a download is a conversation. The packages have to come back in, through the same door. And they do.",
                   (1.6, Wait(1.6)), (0.9, GrowArrow(back)), (1.0, travel(back, GREY_B, 1.0)), (0.5, Indicate(rules[0], color=GOLD_M)))
        stl = T("stateful: replies to allowed traffic come back in", 26, GOLD_M).move_to([-1.0, -2.7, 0])
        self.beat("The lock is stateful. It remembers the calls the flat made, and lets the replies back in without a rule of their own. Inbound rules are only about strangers starting a conversation.",
                  FadeIn(stl, shift=UP * 0.1), run_time=2.6)
        self.beat("So the wrong model was: no inbound rules means nothing comes in. The right one: nobody can start a conversation from outside, but the flat can call anyone it likes.",
                  Indicate(out, color=GREEN_M), run_time=2.6)
        self.play(FadeOut(VGroup(pkgs, out, back, stl, rp, rules, rl)), run_time=0.6)

        # 5. the phone line dialled from inside: Session Manager  [ANALOGY, MAP, SHOW]
        sm = box("Systems Manager", PURPLE_M, w=3.2, h=0.85, size=26).move_to([-1.0, 2.3, 0])
        agent = box("SSM Agent", PURPLE_M, w=2.2, h=0.7, size=26).move_to(flat.get_center() + UP * 0.55 + RIGHT * 0.3)
        self.beat("Now you can guess the trick. If the flat can call out, let it call. Put a phone inside, and have the flat dial the front desk and keep the line open.",
                  FadeIn(sm), run_time=2.4)
        line = Line(agent.get_left() + LEFT * 0.05, sm.get_bottom() + RIGHT * 0.7, stroke_color=PURPLE_M, stroke_width=4)
        self.steps("On AWS, the phone is a small program on the server called the SSM Agent. It keeps an outbound HTTPS connection open to AWS Systems Manager.",
                   (0.9, FadeIn(agent, shift=UP * 0.1)), (1.4, Wait(1.4)), (1.2, Create(line)), (1.0, travel(line, PURPLE_M, 1.0)))
        cmd = M("aws ssm start-session --target i-...", 24, TEAL_M).next_to(mac, UP, buff=0.35).align_to(mac, LEFT)
        iam = chip("IAM: may you join?", BLUE_M, 24).next_to(sm, LEFT, buff=0.3)
        fit(iam, 2.6).next_to(sm, LEFT, buff=0.3)
        self.steps("Then you run aws ssm start-session on your Mac. AWS checks your IAM permissions, the rules from last lesson about who may do what.",
                   (1.0, Write(cmd)), (1.8, Wait(1.8)), (0.8, FadeIn(iam, shift=RIGHT * 0.1)))
        you = Line(cmd.get_top() + UP * 0.08 + RIGHT * 0.6, sm.get_corner(DL) + RIGHT * 0.5, stroke_color=TEAL_M, stroke_width=4)
        shell = T("signed in as ssm-user, with sudo", 26, TEAL_M).move_to([-3.0, -3.0, 0])
        self.steps("If they allow it, AWS joins your terminal to the line the agent already holds open. You arrive as ssm-user, a user with sudo rights.",
                   (1.0, Create(you)), (0.6, travel(you, TEAL_M, 0.6)), (0.8, travel(line.copy().reverse_points(), PURPLE_M, 0.8)),
                   (1.6, Wait(1.6)), (0.8, FadeIn(shell, shift=UP * 0.1)))
        self.beat("Look at the door. It never opened. Zero inbound rules, still. No port, and no key to lose.",
                  Indicate(door, color=GOLD_M, scale_factor=1.15), run_time=2.0)
        nm = T("Session Manager", 30, PURPLE_M).next_to(sm, UP, buff=0.18)
        self.beat("This is Session Manager, part of AWS Systems Manager. It costs nothing extra on EC2.", Write(nm), run_time=1.6)

        # 6. what the phone line needs  [NAME, GUARDRAIL]
        self.play(FadeOut(VGroup(shell, cmd)), run_time=0.4)
        need = VGroup(T("1. the SSM Agent on the server", 26), T("2. a role with AmazonSSMManagedInstanceCore", 26),
                      T("3. outbound HTTPS to ssm, ssmmessages, ec2messages", 26), T("4. the Session Manager plugin on your Mac", 26))
        need.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        fit(need, 6.4)
        np_ = panel(need.width + 0.5, need.height + 0.45, PURPLE_M, 0.06).move_to([-2.85, -1.55, 0])
        need.move_to(np_)
        self.beat("The line needs four things. The agent on the server, which AWS's and Canonical's Ubuntu images, and Amazon Linux 2023, already include.",
                  Create(np_), FadeIn(need[0]), run_time=2.6)
        self.beat("An instance role with the AWS managed policy AmazonSSMManagedInstanceCore.", FadeIn(need[1]), run_time=1.8)
        self.beat("Outbound HTTPS from the server to three AWS endpoints in its region. A public IP and the default outbound rule cover that.",
                  FadeIn(need[2]), Indicate(line, color=PURPLE_M), run_time=2.4)
        self.beat("And the Session Manager plugin, an add-on for the CLI, on your Mac.", FadeIn(need[3]), Indicate(mac[0], color=TEAL_M), run_time=1.8)
        self.play(FadeOut(np_), FadeOut(need), run_time=0.5)

        # 7. bonus: the same line carries port 8000  [SHOW, JOKE]
        fwd = M("localhost:8000  ->  port 8000 on the server", 24, TEAL_M).move_to([-2.4, -3.0, 0])
        fit(fwd, 7.4)
        self.steps("The same line carries more than a shell. The document AWS-StartPortForwardingSession makes localhost:8000 on your Mac reach port 8000 on the server.",
                   (1.6, Wait(1.6)), (0.9, FadeIn(fwd, shift=UP * 0.1)), (0.6, travel(you, TEAL_M, 0.6)),
                   (0.8, travel(line.copy().reverse_points(), PURPLE_M, 0.8)), (0.6, Indicate(app[0], color=GREEN_M)))
        self.beat("So you can open hello-devops in your own browser, through a door that is still locked. The caretaker holds the phone up to the radio.",
                  Indicate(door, color=GOLD_M, scale_factor=1.15), run_time=2.4)
        self.play(FadeOut(fwd), run_time=0.4)

        # 8. three ways in, one rule  [GUARDRAIL, MORAL]
        self.play(FadeOut(VGroup(iam, nm)), run_time=0.4)
        ways = VGroup(
            VGroup(T("Session Manager", 26, PURPLE_M), T("no open port, no key", 24, GREY_B)),
            VGroup(T("EC2 Instance Connect", 26, GOLD_M), T("one-time key, port 22 still open", 24, GREY_B)),
            VGroup(T("key pair", 26, RED_M), T("port 22 and a .pem file", 24, GREY_B)),
        )
        for w in ways:
            w.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        ways.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to([-3.2, -1.3, 0])
        self.beat("AWS gives you three ways in. Session Manager, with no open port and no key.", FadeIn(ways[0], shift=UP * 0.1), run_time=2.0)
        self.beat("EC2 Instance Connect pushes a one-time SSH key for you, but port 22 must still be open, either to AWS's Instance Connect address range or through an Instance Connect Endpoint.",
                  FadeIn(ways[1], shift=UP * 0.1), run_time=2.6)
        self.beat("And key pairs, the old way: port 22, plus a file you must never lose or leak.", FadeIn(ways[2], shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(ways), run_time=0.5)
        rule = VGroup(T("Open no inbound door.", 30, GOLD_M), T("Let the server dial out.", 30, PURPLE_M), T("Let IAM decide who may join.", 30, BLUE_M))
        rule.arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([-3.0, -1.2, 0])
        self.beat("So the moral of the story fits in three short lines. Open no inbound door. Let the server dial out. And let IAM decide who may join.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rule], lag_ratio=0.7), travel(line, PURPLE_M, 1.0), run_time=4.4)
        self.play(FadeOut(rule), run_time=0.5)

        # 9. check question  [RECAP]
        chk = VGroup(T("quick check: a teammate allows port 22 from 0.0.0.0/0 to SSH in.", 26, YELLOW_M),
                     T("Which change gives them a shell and closes the port?", 26, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        fit(chk, 7.0).move_to([-2.85, -1.0, 0])
        self.beat("A quick check. A teammate's security group allows port 22 from every address, so they can SSH in. Which change gives them a shell and closes the port?",
                  FadeIn(chk), run_time=2.6)
        self.guess([-2.85, -2.3, 0])
        ans = T("Session Manager, then delete the port 22 rule", 26, PURPLE_M).move_to([-2.85, -2.4, 0])
        fit(ans, 7.0)
        self.beat("Use Session Manager, and delete the port 22 rule. The agent connects out, and IAM decides who may open a session.",
                  FadeIn(ans), travel(line, PURPLE_M, 1.0), run_time=2.6)
        self.wait(1.0)
