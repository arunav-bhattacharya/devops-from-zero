import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bASIA\b", "A S I A"), (r"\bAKIA\b", "A K I A"), (r"\bs3:GetObject\b", "S three get object"),
            (r"\bs3:DeleteObject\b", "S three delete object"), (r"\bs3:ListBucket\b", "S three list bucket"),
            (r"\bsts:AssumeRole\b", "S T S assume role"), (r"\bsts assume-role\b", "S T S assume role"),
            (r"\bAccessDenied\b", "access denied"), (r"\bARN\b", "A R N"), (r"\bMFA\b", "M F A"),
            (r"\baws\b", "A W S"), (r"\bmoto\b", "moe-toe")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(w, h, color, k=0.10, sw=2.5):
    return RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, k), opacity=1)


def key_icon(color=GOLD_M, s=1.0):
    ring = Circle(radius=0.26, stroke_color=color, stroke_width=5)
    shaft = Line(ring.get_right(), ring.get_right() + RIGHT * 0.9, stroke_color=color, stroke_width=5)
    t1 = Line(shaft.get_end(), shaft.get_end() + DOWN * 0.22, stroke_color=color, stroke_width=5)
    t2 = Line(shaft.get_end() + LEFT * 0.25, shaft.get_end() + LEFT * 0.25 + DOWN * 0.16, stroke_color=color, stroke_width=5)
    return VGroup(ring, shaft, t1, t2).scale(s)


def lamp(color=GREY_D):
    return Circle(radius=0.15, stroke_color=GREY_B, stroke_width=2).set_fill(color, opacity=1)


class D13KeyCard(VoiceScene):
    def steps(self, text, *plays):
        """Speak one line and play several animations one after another inside it."""
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
        """The 'pause and guess' beat: a silent two second countdown."""
        c = chip("pause and guess", YELLOW_M, 24).move_to(where)
        n = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        self.play(FadeIn(c), FadeIn(n), run_time=0.3)
        self.wait(0.85)
        self.play(Transform(n, T("1", 30, YELLOW_M).move_to(n)), run_time=0.15)
        self.wait(0.85)
        self.play(FadeOut(c), FadeOut(n), run_time=0.3)

    def construct(self):
        self.title_card("Why your key card still hits locked doors", "how AWS decides every request")

        # 1. the hotel desk: master key, bill, safe, ordinary card  [QUESTION, FAMILIAR]
        mk = key_icon(GOLD_M, 1.3).move_to([-3.6, 0.6, 0])
        mkl = T("master key", 28, GOLD_M).next_to(mk, DOWN, buff=0.35)
        bill = panel(1.5, 1.0, GREY_B, 0.05).move_to([3.6, 0.6, 0])
        bl = T("the bill", 28, GREY_B).next_to(bill, DOWN, buff=0.35)
        lines = VGroup(*[Line(LEFT * 0.45, RIGHT * 0.45, stroke_color=GREY_B, stroke_width=2) for _ in range(3)]).arrange(DOWN, buff=0.2).move_to(bill)
        self.beat("Picture checking into a hotel for a long stay. The desk hands you a master key that opens every door, and a bill that grows every night.",
                  Create(mk), FadeIn(mkl), Create(bill), Create(lines), FadeIn(bl), run_time=3.0)
        bill2 = panel(1.5, 2.2, GREY_B, 0.05).move_to(bill, aligned_edge=UP)
        lines2 = VGroup(*[Line(LEFT * 0.45, RIGHT * 0.45, stroke_color=GREY_B, stroke_width=2) for _ in range(6)]).arrange(DOWN, buff=0.22).move_to(bill2)
        self.play(Transform(bill, bill2), Transform(lines, lines2), bl.animate.next_to(bill2, DOWN, buff=0.35), run_time=1.2)
        safe = panel(1.9, 1.7, BLUE_M, 0.12, 3).move_to([-3.6, 0.6, 0])
        dial = Circle(radius=0.3, stroke_color=BLUE_M, stroke_width=3).move_to(safe)
        sl = T("safe, with MFA", 28, BLUE_M).next_to(safe, DOWN, buff=0.35)
        self.beat("On AWS, the master key is the root user, the email you signed up with. It goes in the safe, behind MFA, a second proof like your fingerprint.",
                  mk.animate.scale(0.5).move_to(safe), FadeOut(mkl), run_time=2.2)
        self.play(FadeIn(safe), Create(dial), FadeIn(sl), run_time=0.8)
        card = panel(2.2, 1.3, TEAL_M, 0.18, 3).move_to([0, 0.6, 0])
        stripe = Rectangle(width=2.2, height=0.22, stroke_width=0).set_fill(TEAL_M, opacity=0.6).move_to(card.get_top() + DOWN * 0.35)
        cl = T("your key card", 28, TEAL_M).next_to(card, DOWN, buff=0.35)
        self.beat("For daily work you carry an ordinary key card instead.", FadeIn(VGroup(card, stripe)), FadeIn(cl), run_time=1.4)
        q = T("my card works... so why AccessDenied?", 32, YELLOW_M).move_to([0, 2.9, 0])
        self.beat("Now the question almost nobody asks out loud. My card is real, so why does AWS still say AccessDenied at some doors? Who decides?",
                  Write(q), run_time=2.6)
        self.play(FadeOut(VGroup(safe, dial, sl, mk, bill, lines, bl, cl, q)), VGroup(card, stripe).animate.scale(0.75).move_to([-5.05, 2.2, 0]), run_time=1.0)

        # 2. the door reader: two questions  [ANALOGY, MAP]
        Y = 2.2
        cardg = VGroup(card, stripe)
        cardl = T("caller", 26, TEAL_M).next_to(cardg, DOWN, buff=0.2)
        rd = panel(4.4, 1.2, PURPLE_M, 0.12, 3).move_to([0.25, Y, 0])
        l1, l2 = lamp(), lamp()
        t1, t2 = T("genuine?", 26), T("on the list?", 26)
        row = VGroup(VGroup(l1, t1).arrange(RIGHT, buff=0.15), VGroup(l2, t2).arrange(RIGHT, buff=0.15)).arrange(RIGHT, buff=0.45).move_to(rd)
        rdl = T("AWS, the door reader", 26, PURPLE_M).next_to(rd, UP, buff=0.18)
        door = panel(2.0, 1.2, GREEN_M, 0.12, 3).move_to([5.25, Y, 0])
        dl = T("bucket", 26, GREEN_M).move_to(door)
        a0 = Arrow([-3.85, Y, 0], rd.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        a1 = Arrow(rd.get_right(), door.get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("Every command you type in the AWS CLI, AWS's command line tool, becomes a request. Picture it walking up to a door with a card reader.",
                  FadeIn(cardl), Create(rd), FadeIn(rdl), GrowArrow(a0), GrowArrow(a1), FadeIn(door), FadeIn(dl), run_time=3.0)
        self.steps("The reader asks two questions. Is this card genuine, so who is calling? And is this door on the card's list?",
                   (1.4, Wait(1.4)), (0.8, FadeIn(row[0])), (1.2, Wait(1.2)), (0.8, FadeIn(row[1])))
        cred = VGroup(M("access key ID", 24), M("secret", 24, RED_M), M("session token", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        credp = panel(cred.width + 0.7, cred.height + 0.6, TEAL_M).move_to([-4.6, -0.6, 0])
        cred.move_to(credp)
        credl = T("inside the card: credentials", 26, TEAL_M).next_to(credp, UP, buff=0.2)
        self.beat("Inside the card are credentials: an access key ID, a secret, and for temporary credentials, a session token.",
                  FadeIn(credl), Create(credp), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in cred], lag_ratio=0.4), run_time=2.6)
        req = VGroup(M("request", 24), M("+ signature", 24, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        reqp = panel(req.width + 0.5, req.height + 0.4, WHITE, 0.0, 2).move_to([-0.3, -0.6, 0])
        req.move_to(reqp)
        self.steps("Notice: the card never hands its secret over. The CLI uses it to sign the request, and only the signature travels.",
                   (1.6, Wait(1.6)), (0.8, Indicate(cred[1], color=RED_M)), (1.0, FadeIn(reqp), FadeIn(req[0])),
                   (0.8, TransformFromCopy(cred[1], req[1])))
        mine = chip("its own copy of the secret", PURPLE_M, 24).move_to([3.6, -0.6, 0])
        self.steps("AWS checks that signature with its own copy of the secret. They match: the first lamp goes green.",
                   (1.0, travel(a0, YELLOW_M, 1.0)), (0.8, FadeIn(mine, shift=UP * 0.1)), (1.4, Wait(1.4)), (0.5, l1.animate.set_fill(GREEN_M)))

        # 3. the card with no checkout date  [PAIN, PREDICT, WISH]
        self.play(FadeOut(VGroup(reqp, req, mine)), l1.animate.set_fill(GREY_D), run_time=0.6)
        akia = chip("access key, made once", RED_M, 26).move_to([1.4, -0.3, 0])
        self.beat("So where does your card come from? Many tutorials begin with: create an access key. Quick, and it works.",
                  FadeIn(akia, shift=UP * 0.1), run_time=2.0)
        qq = T("when does it stop working?", 28, YELLOW_M).next_to(akia, DOWN, buff=0.4)
        self.beat("So, when does that key stop working?", FadeIn(qq), run_time=1.2)
        self.guess([1.4, -2.6, 0])
        days = T("day 1", 28, GREY_B).next_to(qq, DOWN, buff=0.4)
        self.play(FadeIn(days), run_time=0.3)
        for d in ("day 90", "day 400", "day 1100"):
            self.play(Transform(days, T(d, 28, GREY_B).move_to(days)), run_time=0.35)
        ans = T("only when someone deletes it", 28, RED_M).move_to(qq)
        self.beat("Only when someone deactivates or deletes it. Never on its own.",
                  Transform(qq, ans), Indicate(akia[1], color=RED_M), run_time=2.0)
        spots = VGroup(*[chip(t, RED_M, 24) for t in ("a laptop", "a log", "an old commit")]).arrange(RIGHT, buff=0.35).move_to([1.4, -3.0, 0])
        self.beat("And it works for whoever holds it, copied from a laptop, a log file, or an old commit. That is a hotel card that still opens your room three years after checkout, for whoever found it in the car park.",
                  FadeOut(days), LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in spots], lag_ratio=0.5), run_time=3.4)
        self.beat("So the point is this. A key that never expires is only as safe as every place it was ever copied to.", run_time=None)
        self.play(FadeOut(VGroup(akia, qq, spots)), run_time=0.5)
        pas = chip("aws login: a day pass", TEAL_M, 26).move_to([1.4, -0.3, 0])
        ref = T("temporary, refreshed every 15 minutes", 26, TEAL_M).next_to(pas, DOWN, buff=0.35)
        arc = Arc(radius=0.25, start_angle=PI / 2, angle=-TAU * 0.85, stroke_width=3, color=TEAL_M).add_tip(tip_length=0.12).next_to(ref, DOWN, buff=0.3)
        disk = T("no key on your disk", 26, TEAL_M).next_to(arc, DOWN, buff=0.3)
        self.beat("Wouldn't it be nice if the card simply expired by itself? That is aws login, in CLI 2.32.0 or later: a day pass printed from your key card, through your browser.",
                  FadeIn(pas, shift=UP * 0.1), run_time=2.4)
        self.steps("It stores temporary credentials and refreshes them every 15 minutes, and no key ever lands on your disk.",
                   (0.8, FadeIn(ref)), (0.6, Create(arc)), (1.4, Rotate(arc, -TAU, about_point=arc.get_center())), (0.6, FadeIn(disk)))
        self.play(FadeOut(VGroup(pas, ref, arc, disk, credp, cred, credl)), run_time=0.6)

        # 4. the list of doors: a policy  [SHRINK, MAP]
        s1 = VGroup(M("Allow  s3:ListBucket", 24), M("  on   the bucket", 24, GREY_B), M("  if   prefix like reports/*", 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        s2 = VGroup(M("Allow  s3:GetObject", 24), M("  on   .../reports/*", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        pol = VGroup(s1, s2).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        polp = panel(pol.width + 0.8, pol.height + 0.7, PURPLE_M).move_to([-2.2, -1.25, 0])
        pol.move_to(polp)
        poll = T("the card's list: an IAM policy", 26, PURPLE_M).next_to(polp, UP, buff=0.2)
        self.beat("Now the second lamp. The list of doors is an IAM policy, a JSON document. Here is the lab's reports reader, shortened.",
                  FadeIn(poll), Create(polp), FadeIn(s1[0]), FadeIn(s2[0]), run_time=2.4)
        self.steps("Each rule has an Effect, Allow or Deny. An Action, the API call, like s3:GetObject. A Resource, what the call acts on, named by its ARN, its Amazon Resource Name. And an optional Condition that narrows the rule.",
                   (1.0, Indicate(s1[0][:5], color=WHITE)), (1.6, Indicate(s2[0][5:], color=WHITE)), (2.2, FadeIn(s1[1]), FadeIn(s2[1])), (1.4, Wait(1.4)), (1.0, FadeIn(s1[2])))

        # 5. predict, then show: three requests  [PREDICT, SHOW, BREAK]
        RX = 4.0

        def ask(text, y=-0.2):
            r = M(text, 24)
            p = panel(r.width + 0.4, 0.62, WHITE, 0.0, 2).move_to([RX, y, 0])
            return VGroup(p, r.move_to(p))

        def verdict(ok):
            return chip("allowed" if ok else "denied", GREEN_M if ok else RED_M, 26).move_to([RX, -1.25, 0])

        start = T("every request starts at deny", 26, RED_M).move_to([RX, -2.35, 0])
        self.beat("AWS decides every request the same way. It starts from deny.",
                  l1.animate.set_fill(GREEN_M), l2.animate.set_fill(RED_M), FadeIn(start), run_time=1.6)
        r1 = ask("GetObject reports/...csv")
        v1 = verdict(True)
        self.steps("First request: read one report. A matching Allow? Yes, the second rule. Green, and the door opens.",
                   (0.8, FadeIn(r1, shift=LEFT * 0.2)), (1.4, Wait(1.4)), (0.9, Indicate(s2[0], color=GREEN_M)),
                   (0.6, l2.animate.set_fill(GREEN_M), FadeIn(v1)), (0.8, travel(a1, GREEN_M, 0.8), door.animate.set_stroke(width=6)))
        r2 = ask("DeleteObject reports/...csv")
        v2 = verdict(False)
        self.steps("Second request: delete that report. Nothing on the list allows s3:DeleteObject. No Allow, so it stays denied.",
                   (0.6, FadeOut(r1), FadeOut(v1), l2.animate.set_fill(RED_M), door.animate.set_stroke(width=3)),
                   (0.8, FadeIn(r2, shift=LEFT * 0.2)), (1.8, Wait(1.8)), (0.6, FadeIn(v2)), (0.5, Wiggle(v2)))
        r3 = ask("aws s3 ls s3://BUCKET")
        self.steps("Third request: list everything in the bucket. Look at the first rule. It allows s3:ListBucket, on this very bucket. Allowed or denied?",
                   (0.6, FadeOut(r2), FadeOut(v2)), (0.9, FadeIn(r3, shift=LEFT * 0.2)), (1.8, Wait(1.8)), (1.0, Indicate(s1[0], color=WHITE)))
        self.guess([RX, -1.25, 0])
        self.beat("It is tempting to say allowed. The action matches, the bucket matches.", Indicate(s1[1], color=GREY_B), run_time=1.6)
        r3b = ask("ListBucket  prefix: (empty)")
        self.steps("But the Condition says the prefix must start with reports. Listing the whole bucket sends an empty prefix. Empty does not match.",
                   (1.6, Indicate(s1[2], color=GOLD_M)), (1.0, Transform(r3, r3b)), (1.4, Wait(1.4)), (0.6, Indicate(r3[1], color=RED_M)))
        v3 = verdict(False)
        self.beat("So no Allow matches, and we fall back to the default. Denied. Well... that is a locked door we were sure we had a key for.",
                  FadeIn(v3), Indicate(start, color=RED_M), run_time=2.0)
        r4 = ask("ListBucket  prefix: reports/")
        v4 = verdict(True)
        self.steps("Ask for the reports folder instead, and the prefix matches. The lamp goes green.",
                   (0.6, FadeOut(v3), Transform(r3, r4)), (1.0, Indicate(s1[2], color=GOLD_M)), (0.6, l2.animate.set_fill(GREEN_M), FadeIn(v4)))

        # 6. name the rule; an explicit Deny wins  [NAME]
        dn = VGroup(M("Deny   s3:GetObject", 24, RED_M), M("  on   .../reports/*", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        dnp = panel(dn.width + 0.5, dn.height + 0.4, RED_M, 0.12)
        self.play(FadeOut(VGroup(r3, v4, start)), l2.animate.set_fill(GREY_D), run_time=0.6)
        dn.move_to(dnp)
        dng = VGroup(dnp, dn).move_to([RX, -0.5, 0])
        dnl = T("one Deny, in any policy", 26, RED_M).next_to(dng, UP, buff=0.2)
        self.beat("Last rule. Say another policy on the same caller holds one Deny for reading reports.",
                  FadeIn(dnl), FadeIn(dng, shift=LEFT * 0.2), run_time=2.0)
        v5 = verdict(False).move_to([RX, -1.8, 0])
        self.steps("Now the read meets an Allow and a Deny. An explicit Deny anywhere beats every Allow. Denied. The manager's veto: it doesn't matter how many cards say yes.",
                   (1.2, Indicate(s2[0], color=GREEN_M)), (1.0, Indicate(dn, color=RED_M)), (1.0, l2.animate.set_fill(RED_M), FadeIn(v5)))
        rule = VGroup(T("start at deny", 28, RED_M), T("an Allow opens", 28, GREEN_M), T("a Deny beats every Allow", 28, RED_M)).arrange(RIGHT, buff=0.55).move_to([0, -3.1, 0])
        self.play(FadeOut(VGroup(dnl, dng, v5)), polp.animate.shift(UP * 0.3), pol.animate.shift(UP * 0.3), poll.animate.shift(UP * 0.3), l2.animate.set_fill(GREY_D), run_time=0.6)
        self.beat("So, the whole rule. Start at deny. An Allow opens. A Deny beats every Allow.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rule], lag_ratio=0.6), run_time=3.4)
        self.play(FadeOut(VGroup(polp, pol, poll, rule)), run_time=0.6)

        # 7. roles: the contractor's badge  [ANALOGY, MAP, JOKE]
        role = panel(9.6, 3.4, GOLD_M, 0.07, 3).move_to([1.4, -1.45, 0])
        rl = T("role: a badge waiting at the desk", 26, GOLD_M).move_to(role.get_top() + DOWN * 0.38)
        tp = VGroup(T("trust policy", 26, BLUE_M), T("who may collect it", 24, GREY_B), M("Principal ...:ACCOUNT_ID:root", 22))
        tp.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        tpp = panel(tp.width + 0.5, tp.height + 0.5, BLUE_M)
        pp = VGroup(T("permissions policy", 26, PURPLE_M), T("which doors it opens", 24, GREY_B), M("Allow s3:GetObject ...", 22))
        pp.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        ppp = panel(pp.width + 0.5, pp.height + 0.5, PURPLE_M)
        VGroup(tpp, ppp).arrange(RIGHT, buff=0.4).move_to(role.get_center() + UP * 0.05)
        tp.move_to(tpp); pp.move_to(ppp)
        self.beat("Programs, like a server, should not carry a stored key at all. They assume a role. Picture a contractor's badge waiting at the front desk.",
                  Create(role), FadeIn(rl), run_time=2.6)
        self.beat("A role carries two policies. The permissions policy, like the list we just read, says which doors the badge opens.",
                  FadeIn(ppp), FadeIn(pp, shift=UP * 0.1), run_time=2.0)
        self.beat("The trust policy says who may collect the badge at the desk.", FadeIn(tpp), FadeIn(tp[:2], shift=UP * 0.1), run_time=1.6)
        acc = T("= the whole account, not the root user", 24, BLUE_M).move_to(role.get_bottom() + UP * 0.38).align_to(tpp, LEFT).shift(RIGHT * 0.25)
        self.steps("In the lab's trust policy the Principal ends in root. That means the whole account: any identity in it whose own policy allows sts:AssumeRole. It does not mean the root user, despite the name.",
                   (0.9, FadeIn(tp[2])), (1.2, Indicate(tp[2], color=BLUE_M)), (3.0, Wait(3.0)), (0.8, FadeIn(acc, shift=UP * 0.1)))
        c1 = tick(True, 0.22).next_to(tp[0], RIGHT, buff=0.3)
        c2 = tick(True, 0.22).next_to(cardl, RIGHT, buff=0.2)
        self.steps("aws sts assume-role checks both sides: your own policy must allow it, and the trust policy must let you collect it.",
                   (1.2, Wait(1.2)), (0.6, Indicate(cardl, color=TEAL_M), Create(c2)), (1.2, Wait(1.2)), (0.6, Create(c1)))
        asia = chip("ASIA...  temporary, 1 hour", GREEN_M, 24, mono=True).move_to([-3.0, 0.85, 0])
        akia2 = chip("AKIA...  long-lived", RED_M, 24, mono=True).next_to(asia, RIGHT, buff=0.5)
        self.steps("Then it hands back temporary credentials that last an hour by default. Their key ID starts with ASIA. Long-lived keys start with AKIA, so you can tell them apart in a log.",
                   (1.2, TransformFromCopy(rl, asia)), (2.6, Wait(2.6)), (0.8, FadeIn(akia2, shift=UP * 0.1)))
        self.play(FadeOut(VGroup(role, rl, tpp, tp, ppp, pp, acc, c1, c2, asia, akia2)), run_time=0.6)

        # 8. guardrails  [GUARDRAIL]
        g = VGroup(
            T("check a policy before it bites: Access Analyzer, policy simulator", 26, PURPLE_M),
            T("the moto emulator allows every call: cardboard doors", 26, GOLD_M),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([0, -1.2, 0])
        self.beat("Two guardrails. Check a policy before it bites. IAM Access Analyzer validates it, and the policy simulator answers: would this call be allowed? without making the call.",
                  FadeIn(g[0], shift=UP * 0.1), run_time=2.4)
        self.beat("And the practice emulator, moto, allows every call. A hotel with cardboard doors: good for learning the corridors, useless for learning which doors are locked.",
                  FadeIn(g[1], shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(g), run_time=0.6)

        # 9. moral and a check question  [MORAL, RECAP]
        rec = VGroup(T("prove who you are, never send the secret", 28, YELLOW_M), T("start at deny, an Allow opens, a Deny wins", 28, RED_M),
                     T("cards that expire by themselves", 28, TEAL_M)).arrange(DOWN, buff=0.35).move_to([0, -1.0, 0])
        self.beat("So the moral of the story. The card proves who you are without ever sending its secret. Every door starts locked, an Allow opens it, and any Deny shuts it. And the best cards expire by themselves.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rec], lag_ratio=0.7), run_time=5.0)
        self.play(FadeOut(rec), run_time=0.5)
        chk = VGroup(T("quick check: the trust policy lets you collect the badge,", 26, YELLOW_M),
                     T("but your own policy does not allow sts:AssumeRole. Badge or not?", 26, YELLOW_M)).arrange(DOWN, buff=0.12).move_to([0, -0.9, 0])
        fit(chk, 12.4)
        self.beat("A quick check before you go. The trust policy lets you collect the badge, but your own policy does not allow sts:AssumeRole. Do you get the badge?",
                  FadeIn(chk), run_time=2.4)
        self.guess([0, -2.1, 0])
        a = T("no badge: assume-role checks both sides", 28, RED_M).move_to([0, -2.1, 0])
        self.beat("No. assume-role checks both sides, and your side said no.", FadeIn(a), run_time=1.6)
        self.wait(1.0)
