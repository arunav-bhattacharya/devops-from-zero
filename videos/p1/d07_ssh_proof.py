import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bssh-keygen\b", "S S H keygen"), (r"ubuntu@192\.168\.64\.5", "ubuntu at 192 dot 168 dot 64 dot 5"), (r"\bssh\b", "S S H"),
    (r"\bid_ed25519\.pub\b", "I D, E D two five five one nine, dot pub"), (r"\bid_ed25519\b", "I D, E D two five five one nine"),
    (r"\bauthorized_keys\b", "authorized keys"), (r"\bknown_hosts\b", "known hosts"),
    (r"\bls -l\b", "L S dash L"), (r"\b600\b", "six oh oh"), (r"\b644\b", "six four four"),
])

PRIV, PUB, FPC, DATA, SIG, PW = GOLD_M, TEAL_M, PURPLE_M, BLUE_M, YELLOW_M, RED_M
LX, RX, BY = -4.3, 4.3, -0.45      # laptop and server centres, box centre height
WIRE_Y = 0.55


def key_icon(color, s=1.0):
    ring = Circle(radius=0.17, stroke_color=color, stroke_width=4).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.45), 1)
    a = ring.get_right()
    shaft = Line(a, a + RIGHT * 0.5, stroke_width=4, color=color)
    t1 = Line(a + RIGHT * 0.36, a + RIGHT * 0.36 + DOWN * 0.14, stroke_width=4, color=color)
    t2 = Line(a + RIGHT * 0.5, a + RIGHT * 0.5 + DOWN * 0.18, stroke_width=4, color=color)
    return VGroup(ring, shaft, t1, t2).scale(s)


def padlock(color, s=1.0, open_=False):
    body = RoundedRectangle(corner_radius=0.06, width=0.5, height=0.4, stroke_color=color, stroke_width=4)
    body.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.35), 1)
    sh = Arc(radius=0.16, start_angle=0, angle=PI, stroke_color=color, stroke_width=4)
    sh.next_to(body, UP, buff=0).shift(DOWN * 0.02)
    if open_:
        sh.shift(UP * 0.1 + RIGHT * 0.0)
    hole = Dot(radius=0.04, color=BLACK).move_to(body)
    return VGroup(body, sh, hole).scale(s)


def building(title, x, sub=None):
    r = RoundedRectangle(corner_radius=0.18, width=4.5, height=4.7, stroke_color=GREY_B, stroke_width=2.5).move_to(np.array([x, BY, 0]))
    t = T(title, 28).move_to(r.get_top() + DOWN * 0.38)
    g = VGroup(r, t)
    if sub:
        s = M(sub, 22, GREY_B).next_to(t, RIGHT, buff=0.25)
        VGroup(t, s).move_to(r.get_top() + DOWN * 0.38)
        g.add(s)
    return g


def panel(name, x, y, w=4.0, h=1.35):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=GREY_D, stroke_width=2).set_fill(BLACK, 1).move_to(np.array([x, y, 0]))
    n = M(name, 20, GREY_B).move_to(r.get_corner(UL) + RIGHT * 0.15 + DOWN * 0.24, aligned_edge=LEFT)
    return VGroup(r, n)


def pchip(text, color, size=22, mono=True):
    c = chip(text, color, size=size, mono=mono)
    c[0].set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.22), opacity=1)
    return c


class D07SshProof(VoiceScene):
    def construct(self):
        self.title_card("The secret stays home", "how SSH keys let a server know it's you")

        # ---------- 1. the shy question
        big = padlock(PUB, 2.2).move_to(UP * 0.5)
        bl = T("your public key", 30, PUB).next_to(big, DOWN, buff=0.45)
        self.beat("Here is a question that a lot of people are too shy to ask.", FadeIn(big, scale=0.7), FadeIn(bl), run_time=1.6)
        eyes = VGroup(*[T(s, 26, GREY_B) for s in ("a stranger", "a coworker", "the whole internet")])
        for e, p in zip(eyes, (LEFT * 4.6 + UP * 1.6, RIGHT * 4.6 + UP * 1.6, DOWN * 2.4)):
            e.move_to(p)
        self.beat("To log in to a server with SSH keys, you hand out your public key. And public means anyone may see it.",
                  LaggedStart(*[FadeIn(e, shift=0.2 * (ORIGIN - e.get_center()) / np.linalg.norm(e.get_center())) for e in eyes], lag_ratio=0.5), run_time=3.2)
        q = T("?", 96, YELLOW_M).next_to(big, RIGHT, buff=0.5)
        self.beat("So what stops a stranger from copying it, and logging in as you? Hold on to that question. We will answer it on the way.",
                  Write(q), run_time=1.2)
        self.play(FadeOut(VGroup(big, bl, eyes, q)), run_time=0.6)

        # ---------- 2. the familiar way: a password
        lap = building("your laptop", LX)
        srv = building("server", RX, "192.168.64.5")
        wire = VGroup(Line(np.array([-2.05, WIRE_Y + 0.18, 0]), np.array([2.05, WIRE_Y + 0.18, 0])),
                      Line(np.array([-2.05, WIRE_Y - 0.18, 0]), np.array([2.05, WIRE_Y - 0.18, 0]))).set_stroke(GREY_B, 2.5)
        enc = T("encrypted connection", 24, GREY_B).next_to(wire, DOWN, buff=0.22)
        cmd = M("$ ssh ubuntu@192.168.64.5", 28).move_to(UP * 2.95)
        self.beat("Let's start with what you already know. SSH gives you a shell on a far away machine, over an encrypted connection.",
                  Create(lap[0]), Write(lap[1]), Create(srv[0]), Write(srv[1]), FadeIn(srv[2]),
                  Succession(Wait(1.6), AnimationGroup(Create(wire), FadeIn(enc))), run_time=4.0)
        self.beat("Running ssh ubuntu@192.168.64.5 logs you in as ubuntu, on the machine at that address.",
                  Write(cmd), Succession(Wait(2.8), Indicate(srv[2], color=YELLOW_M)), run_time=4.2)
        pw = pchip("password", PW, mono=False).move_to(np.array([LX, 0.55, 0]))
        self.beat("With a password, you type the secret, and the secret itself travels to the server. Every single time.",
                  Succession(FadeIn(pw, scale=0.8, run_time=0.6), Wait(0.6), pw.animate(run_time=1.6).move_to(np.array([RX, 0.55, 0])), FadeOut(pw, run_time=0.3)), run_time=4.0)
        self.remove(pw)
        pw = pchip("password", PW, mono=False).move_to(np.array([LX, 0.55, 0]))
        reuse = VGroup(*[pchip("password", PW, size=20, mono=False) for _ in range(5)]).arrange(RIGHT, buff=0.2).move_to(DOWN * 3.35)
        self.beat("And people guess passwords, and reuse them. Use the same one in five places, and one leak opens all five.",
                  Succession(FadeIn(pw, run_time=0.5), Wait(0.3), pw.animate(run_time=1.2).move_to(np.array([0, 0.55, 0]))),
                  LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in reuse], lag_ratio=0.25), run_time=5.0)
        self.beat("A password is like a house key that you hand to the front door every morning, and trust the door to give it back.",
                  Wiggle(pw), run_time=1.6)
        self.beat("So the real problem is simple. To be useful, a password has to leave home.",
                  FadeOut(reuse), pw.animate.move_to(np.array([RX, 0.55, 0])), run_time=1.8)
        stays = DashedVMobject(lap[0].copy().set_stroke(PRIV, 3), num_dashes=70)
        self.beat("Wouldn't it be nice if you could prove who you are, and your secret never left your laptop at all?",
                  FadeOut(pw), Succession(Wait(1.6), Create(stays)), run_time=3.6)
        self.play(FadeOut(stays), FadeOut(cmd), run_time=0.5)

        # ---------- 3. the office building: a padlock you hand out, a key you keep
        office = T("your office", 28).move_to(lap[1])
        other_b = T("another building", 28).move_to(srv[1:].get_center())
        self.beat("Let's step into our office building for a moment. You need to work in another building, across town.",
                  Transform(lap[1], office), FadeOut(srv[2]), Transform(srv[1], other_b), run_time=1.8)
        key = key_icon(PRIV, 1.25).move_to(np.array([LX - 1.15, 0.75, 0]))
        lock = padlock(PUB, 1.25).move_to(np.array([LX + 1.0, 0.75, 0]))
        self.beat("Here is the trick. You own a padlock that you are happy to hand out to anyone. And you own one key, the only thing that opens it.",
                  FadeIn(lock, scale=0.7), Succession(Wait(3.4), FadeIn(key, shift=RIGHT * 0.2)), run_time=5.6)
        board = panel("the guard's board", RX, -1.75)
        others = VGroup(padlock(GREY_B, 0.8), padlock(GREY_B, 0.8)).arrange(RIGHT, buff=0.45)
        others.move_to(board[0].get_center() + LEFT * 1.0 + DOWN * 0.15)
        slot = board[0].get_center() + RIGHT * 0.65 + DOWN * 0.15
        fly = lock.copy()
        self.beat("You give the other building's guard a copy of your padlock. He hangs it on his board, next to the padlocks of everyone he trusts.",
                  FadeIn(board, shift=UP * 0.15), FadeIn(others),
                  Succession(Wait(2.4), fly.animate(run_time=2.2, path_arc=-0.5).scale(0.64).move_to(slot)), run_time=5.6)
        mine = fly
        stays = DashedVMobject(lap[0].copy().set_stroke(PRIV, 3), num_dashes=70)
        self.beat("The key never leaves your desk.",
                  Create(stays), Indicate(key, color=PRIV, scale_factor=1.2), run_time=1.6)
        self.play(FadeOut(stays), run_time=0.4)

        # ---------- map it out loud
        l_key = T("private key", 26, PRIV).next_to(key, DOWN, buff=0.3)
        l_lock = T("public key", 26, PUB).next_to(lock, DOWN, buff=0.3)
        self.beat("Now let's map it. The key is your private key.", FadeIn(l_key, shift=UP * 0.1), run_time=1.2)
        self.beat("The padlock is your public key.", FadeIn(l_lock, shift=UP * 0.1), run_time=1.2)
        bname = M("~/.ssh/authorized_keys", 20, GREY_B).move_to(board[1], aligned_edge=LEFT)
        self.beat("And the guard's board is a file on the server, called authorized_keys. One public key per line.",
                  Transform(board[1], bname), Transform(srv[1], T("server", 28).move_to(srv[1])), Transform(lap[1], T("your laptop", 28).move_to(lap[1])),
                  run_time=2.2)
        gen = M('$ ssh-keygen -t ed25519 -C "you@example.com"', 26).move_to(UP * 2.95)
        f_key = M("id_ed25519", 22, PRIV).next_to(l_key, DOWN, buff=0.22)
        f_lock = M("id_ed25519.pub", 22, PUB).next_to(l_lock, DOWN, buff=0.22)
        self.beat("You make the pair with one command, ssh-keygen. It writes two files, id_ed25519, the private key, and id_ed25519.pub, the public one.",
                  Write(gen), Succession(Wait(3.8), FadeIn(f_key, shift=UP * 0.1), Wait(1.6), FadeIn(f_lock, shift=UP * 0.1)), run_time=7.0)

        # loop payoff: the stranger with your padlock
        thief = padlock(GREY_B, 1.25)
        thief_l = T("a stranger's copy", 24, GREY_B)
        tg = VGroup(thief, thief_l).arrange(DOWN, buff=0.25).move_to(np.array([0, -1.75, 0]))
        self.beat("So, back to our question. A stranger who copies your public key gets, well, a padlock.",
                  FadeIn(tg, shift=UP * 0.15), run_time=1.6)
        self.beat("A padlock can't open anything. It can only check the key that opens it. A public key works the same way. It can check, but it can never log in.",
                  Succession(Wiggle(thief, run_time=1.5), Wait(2.7), FadeOut(tg, run_time=0.8)), run_time=5.0)

        # ---------- 4. the obvious fix, broken on purpose
        self.play(FadeOut(gen), run_time=0.4)
        walk = key.copy()
        self.beat("But how does the guard know that you hold the key? The obvious answer: walk the key over and show it to him.",
                  Succession(Wait(3.0), walk.animate(run_time=2.2).move_to(np.array([1.2, WIRE_Y, 0]))), run_time=5.2)
        xk = tick(False, 0.32).move_to(walk)
        self.beat("Well. Now your secret has left home, which is the one thing we wanted to avoid. That's just a password with extra steps.",
                  walk.animate.set_color(PW), Create(xk), run_time=1.8)
        self.beat("So here is where the padlock story stops. On the real wire, nothing gets locked, and no key travels.",
                  FadeOut(walk), FadeOut(xk), run_time=1.4)

        # ---------- 5. what really crosses: a signature
        data = pchip("7f3a9c...e21b", DATA).move_to(np.array([0, WIRE_Y + 0.0, 0]))
        dlab = T("unique to this connection", 24, DATA).move_to(enc)
        self.beat("When you connect, there is a small piece of data that belongs to this one connection, and to no other.",
                  FadeIn(data, scale=0.8), FadeOut(enc), FadeIn(dlab), run_time=2.2)
        opts = VGroup(pchip("private key?", PRIV, 24, False), pchip("public key?", PUB, 24, False), pchip("the data?", DATA, 24, False)).arrange(RIGHT, buff=0.5).move_to(UP * 2.95)
        self.beat("Your laptop has three things to work with. The private key, the public key, and that data. Which one crosses the wire to prove it's you?",
                  LaggedStart(*[FadeIn(o, shift=DOWN * 0.1) for o in opts], lag_ratio=0.5), run_time=4.4)
        pause = T("pause and guess", 26, GREY_B).move_to(DOWN * 3.35)
        self.beat("Pause and guess.", FadeIn(pause), run_time=0.6, after=2.2)
        spot = np.array([LX, -1.0, 0])
        self.beat("None of them. Your ssh takes the data, and signs it with the private key.",
                  FadeOut(pause), FadeOut(opts), FadeOut(dlab),
                  Succession(Wait(0.8), data.animate(run_time=1.4).move_to(spot)), run_time=3.0)
        pk = key.copy()
        sig = pchip("signature", SIG, 24, False).move_to(spot)
        self.beat("Out comes something new, a signature.",
                  Succession(pk.animate(run_time=0.9).next_to(spot, LEFT, buff=0.05), AnimationGroup(FadeOut(pk), ReplacementTransform(data, sig), run_time=0.8)), run_time=2.0)
        sig_lab = T("only this crosses", 24, SIG)
        self.beat("And only the signature crosses the wire.",
                  sig.animate.move_to(np.array([0, WIRE_Y, 0])), run_time=1.6)
        sig_lab.next_to(sig, DOWN, buff=0.3)
        self.play(FadeIn(sig_lab), run_time=0.4)
        check_at = np.array([RX + 0.7, 0.55, 0])
        self.beat("The server checks it with your public key, from authorized_keys.",
                  FadeOut(sig_lab), sig.animate(run_time=1.4).move_to(check_at),
                  Succession(Wait(1.4), Indicate(mine, color=PUB, scale_factor=1.3)), run_time=3.4)
        chk = mine.copy()
        ok = tick(True, 0.26)
        self.beat("It fits. So you are in.",
                  Succession(chk.animate(run_time=1.0).next_to(sig, LEFT, buff=0.2), Create(ok.next_to(sig, DOWN, buff=0.2), run_time=0.5)), run_time=1.8)
        shell = M("ubuntu@server:~$", 24, GREEN_M).move_to(UP * 2.95)
        stays = DashedVMobject(lap[0].copy().set_stroke(PRIV, 3), num_dashes=70)
        self.beat("And the private key itself never left your laptop.",
                  FadeIn(shell, shift=DOWN * 0.1), Create(stays), Indicate(key, color=PRIV, scale_factor=1.2), run_time=2.4)
        self.play(FadeOut(VGroup(chk, ok, stays)), run_time=0.4)

        # replay attempt
        old = sig
        new_data = pchip("c41d08...9ab2", DATA).move_to(np.array([0, WIRE_Y, 0]))
        tom = T("tomorrow", 24, DATA).move_to(enc)
        self.beat("What if someone records that signature, and tries it tomorrow? Pause and guess.",
                  FadeOut(shell), old.animate.set_opacity(0.45).move_to(np.array([0, -1.75, 0])), FadeIn(new_data), FadeIn(tom), run_time=2.4, after=2.0)
        xs = tick(False, 0.28).next_to(old, RIGHT, buff=0.2)
        self.beat("Tomorrow's connection has different data, so yesterday's signature fits nothing. It's about as useful as yesterday's bus ticket.",
                  Indicate(new_data[1], color=DATA), Succession(Wait(2.4), Create(xs)), run_time=3.6)
        self.beat("A signature proves it's you once, for one connection only.",
                  FadeOut(VGroup(old, xs, new_data, tom)), run_time=1.0)
        enc = T("encrypted connection", 24, GREY_B).next_to(wire, DOWN, buff=0.22)
        self.play(FadeIn(enc), run_time=0.4)

        # ---------- 6. trust runs the other way: known_hosts
        self.beat("Trust also runs the other way. What if the building you walk into is a fake, set up to look like yours?",
                  Succession(Wait(2.4), Indicate(srv[0], color=RED_M, scale_factor=1.03)), run_time=4.4)
        fp = pchip("SHA256:4fK9...q2Lw", FPC).move_to(np.array([RX, 1.0, 0]))
        self.beat("Every server has a fingerprint, a short code that identifies it.",
                  FadeIn(fp, shift=DOWN * 0.1), run_time=1.4)
        prompt = M("Are you sure you want to continue connecting (yes/no/[fingerprint])?", 22, YELLOW_M)
        fit(prompt, 12.6).move_to(UP * 2.95)
        self.beat("The first time you connect, ssh shows you that fingerprint, and asks if you are sure you want to continue connecting.",
                  fp.animate(run_time=1.6).move_to(np.array([0, WIRE_Y + 0.75, 0])), Succession(Wait(2.4), FadeIn(prompt, shift=DOWN * 0.1)), run_time=5.0)
        kh = panel("~/.ssh/known_hosts", LX, -1.75)
        yes = M("yes", 24, GREEN_M).next_to(prompt, DOWN, buff=0.15)
        stored_at = kh[0].get_center() + DOWN * 0.18
        self.beat("Say yes, and ssh writes it down in a file on your laptop, called known_hosts. Your notebook of familiar faces.",
                  FadeIn(yes), FadeIn(kh, shift=UP * 0.15),
                  Succession(Wait(1.6), fp.animate(run_time=1.6).move_to(stored_at)), run_time=4.6)
        stored = fp
        self.play(FadeOut(VGroup(prompt, yes)), run_time=0.4)
        fp2 = pchip("SHA256:4fK9...q2Lw", FPC).move_to(np.array([RX, 1.0, 0]))
        ok1 = tick(True, 0.24).next_to(stored, UP, buff=0.12).shift(RIGHT * 1.3)
        self.beat("Next time, ssh compares the server's fingerprint with the one in the notebook. Same face, so it carries on.",
                  Succession(FadeIn(fp2, shift=DOWN * 0.1, run_time=0.5), Wait(0.3), fp2.animate(run_time=1.4).move_to(np.array([0, WIRE_Y + 0.75, 0]))),
                  Succession(Wait(3.4), Indicate(stored[1], color=GREEN_M), Create(ok1)), run_time=5.2)
        self.play(FadeOut(VGroup(fp2, ok1)), run_time=0.4)
        bad = pchip("SHA256:Zp1x...7Hc0", RED_M).move_to(np.array([RX, 1.0, 0]))
        x2 = tick(False, 0.3).move_to(np.array([-1.3, WIRE_Y + 0.75, 0]))
        refuse = T("ssh refuses to connect", 28, RED_M).move_to(UP * 2.95)
        self.beat("If that fingerprint ever changes, ssh refuses to connect, because someone may be pretending to be your server.",
                  Succession(FadeIn(bad, shift=DOWN * 0.1, run_time=0.5), Wait(0.1), bad.animate(run_time=1.4).move_to(np.array([0.4, WIRE_Y + 0.75, 0])), Create(x2), FadeIn(refuse), Indicate(stored[1], color=YELLOW_M)),
                  run_time=5.0)
        self.beat("ssh is the friend who says, that's not our usual doorman, and won't go in, however nice the uniform. So a refusal is a warning to read, not a hurdle to jump.",
                  Wiggle(refuse), run_time=1.6)
        self.play(FadeOut(VGroup(bad, x2, refuse)), run_time=0.5)

        # ---------- 7. guardrails, on the same picture
        g1 = T("1. the private key never gets copied", 26, PRIV).move_to(UP * 2.95)
        stays = DashedVMobject(lap[0].copy().set_stroke(PRIV, 3), num_dashes=70)
        self.beat("Three habits keep this safe. One. Never copy the private key anywhere else. It works like a password.",
                  FadeIn(g1, shift=DOWN * 0.1), Create(stays), run_time=2.8)
        tiny = padlock(PRIV, 0.6).next_to(key, RIGHT, buff=0.2)
        g2 = T("2. a passphrase locks the key file", 26, PRIV).move_to(g1)
        self.beat("Two. Set a passphrase when ssh-keygen asks. It encrypts the private key file, so a stolen copy is useless without it.",
                  FadeOut(stays), ReplacementTransform(g1, g2), Succession(Wait(1.8), FadeIn(tiny, scale=0.6)), run_time=3.6)
        m1 = M("600", 22, GREY_B).next_to(f_key, DOWN, buff=0.15)
        m2 = M("644", 22, GREY_B).next_to(f_lock, DOWN, buff=0.15)
        g3 = T("3. check the modes with ls -l", 26, WHITE).move_to(g1)
        self.beat("Three. ls -l shows the private key with mode 600, for you alone, and the public key with 644.",
                  ReplacementTransform(g2, g3), Succession(Wait(1.8), FadeIn(m1, shift=DOWN * 0.1), Wait(1.4), FadeIn(m2, shift=DOWN * 0.1)), run_time=5.0)

        # ---------- 8. moral, recap and a check question
        everything = VGroup(lap, srv, wire, enc, key, lock, l_key, l_lock, f_key, f_lock, board, others, mine, kh, stored, tiny, m1, m2, g3)
        self.play(FadeOut(everything), run_time=0.7)
        moral = T("The secret stays home. Only proof travels.", 40)
        self.beat("So here is the moral of the story. The secret stays home, and only proof travels.",
                  Write(moral), run_time=2.4)
        rec = VGroup(
            VGroup(padlock(PUB, 0.8), T("public key: hand it out, one line in authorized_keys", 26)).arrange(RIGHT, buff=0.35),
            VGroup(key_icon(PRIV, 0.9), T("private key: never leaves your laptop", 26)).arrange(RIGHT, buff=0.35),
            VGroup(pchip("signature", SIG, 22, False), T("fresh for every connection", 26)).arrange(RIGHT, buff=0.35),
            VGroup(pchip("SHA256:4fK9...", FPC, 20), T("known_hosts: the faces you trust", 26)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to(DOWN * 0.55)
        self.beat("The padlock goes everywhere. The key goes nowhere. Every login is a fresh signature. And known_hosts remembers the faces you trust.",
                  moral.animate.scale(0.75).to_edge(UP, buff=0.75),
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rec], lag_ratio=0.7), run_time=7.0)
        self.play(FadeOut(VGroup(moral, rec)), run_time=0.6)
        qq = T("A new teammate needs to log in to the server.", 32)
        qq2 = T("What do they send you, and where does it go?", 32, YELLOW_M)
        qg = VGroup(qq, qq2).arrange(DOWN, buff=0.35).move_to(UP * 1.2)
        self.beat("A quick check before you go. A new teammate needs to log in to the server. What do they send you, and where does it go? Pause and guess.",
                  FadeIn(qq), Succession(Wait(3.0), FadeIn(qq2)), run_time=5.0, after=2.2)
        ans = VGroup(padlock(PUB, 1.0), T("their public key, as one more line in authorized_keys", 28, PUB)).arrange(RIGHT, buff=0.4).move_to(DOWN * 1.0)
        self.beat("Their public key, as one more line in authorized_keys. Their private key stays home, on their laptop.",
                  FadeIn(ans, shift=UP * 0.15), run_time=1.6)
        self.wait(1.5)
