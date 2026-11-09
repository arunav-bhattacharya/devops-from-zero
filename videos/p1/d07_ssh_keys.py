import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bssh-keygen\b", "S S H keygen"), (r"\bssh-agent\b", "S S H agent"), (r"\bssh devbox\b", "S S H dev box"),
    (r"ubuntu@192\.168\.64\.5", "ubuntu at 192 dot 168 dot 64 dot 5"), (r"\bssh\b", "S S H"),
    (r"\bed25519\b", "E D two five five one nine"), (r"\bauthorized_keys\b", "authorized keys"), (r"\bknown_hosts\b", "known hosts"),
    (r"\bls -l\b", "L S dash L"), (r"\b600\b", "six oh oh"), (r"\b644\b", "six four four"), (r"\bGitHub\b", "git hub"),
])

PRIV, PUB, HOST = GOLD_M, TEAL_M, PURPLE_M
LX, RX = -4.6, 4.6           # laptop and server centres
PIPE_Y = 0.55


def key_icon(color, s=1.0, filled=True):
    """A small key drawn with strokes: ring, shaft and two teeth."""
    ring = Circle(radius=0.17, stroke_color=color, stroke_width=4)
    if filled:
        ring.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.45), 1)
    a = ring.get_right()
    shaft = Line(a, a + RIGHT * 0.5, stroke_width=4, color=color)
    t1 = Line(a + RIGHT * 0.36, a + RIGHT * 0.36 + DOWN * 0.14, stroke_width=4, color=color)
    t2 = Line(a + RIGHT * 0.5, a + RIGHT * 0.5 + DOWN * 0.18, stroke_width=4, color=color)
    return VGroup(ring, shaft, t1, t2).scale(s)


def container(title, sub, x):
    r = RoundedRectangle(corner_radius=0.18, width=4.4, height=5.0, stroke_color=GREY_B, stroke_width=2.5).move_to(np.array([x, -0.5, 0]))
    t = T(title, 28).move_to(r.get_top() + DOWN * 0.38)
    g = VGroup(r, t)
    if sub:
        s = M(sub, 20, GREY_B).next_to(t, RIGHT, buff=0.25)
        VGroup(t, s).move_to(r.get_top() + DOWN * 0.38)
        g.add(s)
    return g


def filepanel(name, x, y, h=1.6):
    r = RoundedRectangle(corner_radius=0.1, width=4.0, height=h, stroke_color=GREY_D, stroke_width=2).set_fill(BLACK, 1).move_to(np.array([x, y, 0]))
    n = M(name, 20, GREY_B).move_to(r.get_corner(UL) + RIGHT * 0.15 + DOWN * 0.25, aligned_edge=LEFT)
    return VGroup(r, n)


def fp_chip(text, color=HOST):
    c = chip(text, color, size=20, mono=True)
    c[0].set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.2), opacity=1)
    return c


class D07SshKeys(VoiceScene):
    def construct(self):
        self.title_card("How SSH keys work", "a key pair, trust both ways, and a secret that never travels")

        # ---------- 1. the two machines
        lap = container("your laptop", None, LX)
        srv = container("server", "192.168.64.5", RX)
        self.beat("Servers sit in data centres and clouds, where you have no keyboard and no screen.",
                  Create(srv[0]), Write(srv[1]), FadeIn(srv[2]), run_time=2.0)
        pipe = VGroup(Line(np.array([-2.3, PIPE_Y + 0.2, 0]), np.array([2.3, PIPE_Y + 0.2, 0])),
                      Line(np.array([-2.3, PIPE_Y - 0.2, 0]), np.array([2.3, PIPE_Y - 0.2, 0]))).set_stroke(GREY_B, 2.5)
        enc = T("encrypted connection", 22, GREY_B).next_to(pipe, UP, buff=0.18)
        self.beat("SSH gives you a shell on such a machine, over an encrypted connection.",
                  Create(lap[0]), Write(lap[1]), Succession(Wait(1.0), AnimationGroup(Create(pipe), FadeIn(enc))), run_time=3.0)
        cmd = M("$ ssh ubuntu@192.168.64.5", 28).move_to(UP * 3.25)
        self.beat("Running ssh ubuntu@192.168.64.5 logs you in as ubuntu, on the machine at that address.",
                  Write(cmd), Succession(Wait(2.6), Indicate(srv[2], color=YELLOW_M)), run_time=4.0)
        pw = fp_chip("password", RED_M).move_to(np.array([0, PIPE_Y, 0]))
        x_pw = tick(False, 0.3).move_to(pw)
        self.beat("Passwords work, but people guess them and reuse them. Keys are safer, and quicker.",
                  FadeIn(pw, scale=0.8), Succession(Wait(2.2), Create(x_pw)), run_time=3.4)
        self.play(FadeOut(VGroup(pw, x_pw)), run_time=0.4)

        # ---------- 2. the key pair
        gen = M('$ ssh-keygen -t ed25519 -C "you@example.com"', 26).move_to(cmd)
        folder = M("~/.ssh/", 20, GREY_B).move_to(np.array([-6.45, 1.15, 0]), aligned_edge=LEFT)
        k_priv = key_icon(PRIV).move_to(np.array([-6.05, 0.62, 0]))
        n_priv = M("id_ed25519", 20, PRIV).next_to(k_priv, RIGHT, buff=0.25)
        k_pub = key_icon(PUB, filled=False).move_to(np.array([-6.05, 0.0, 0]))
        n_pub = M("id_ed25519.pub", 20, PUB).next_to(k_pub, RIGHT, buff=0.25)
        self.beat("Create a key pair with ssh-keygen. ed25519 is the modern key type, and the comment helps you tell keys apart.",
                  ReplacementTransform(cmd, gen), Succession(Wait(2.4), AnimationGroup(FadeIn(folder), FadeIn(VGroup(k_priv, n_priv), shift=RIGHT * 0.2),
                                                                                      FadeIn(VGroup(k_pub, n_pub), shift=RIGHT * 0.2), lag_ratio=0.3)), run_time=5.0)
        cmd = gen
        stays = DashedVMobject(lap[0].copy().set_stroke(PRIV, 3), num_dashes=60)
        self.beat("A key pair is two files. The private key stays on your laptop. It works like a password, so never copy it anywhere else.",
                  Indicate(VGroup(k_priv, n_priv), color=PRIV, scale_factor=1.15), Succession(Wait(2.6), Create(stays)), run_time=4.4)
        self.beat("The public key is safe to share. You put it on servers, and in GitHub.",
                  FadeOut(stays), Indicate(VGroup(k_pub, n_pub), color=PUB, scale_factor=1.15), run_time=2.0)

        lock = VGroup(RoundedRectangle(corner_radius=0.04, width=0.3, height=0.24, stroke_color=PRIV, stroke_width=3).set_fill(BLACK, 1),
                      Arc(radius=0.1, start_angle=0, angle=PI, stroke_color=PRIV, stroke_width=3).shift(UP * 0.12))
        lock[1].next_to(lock[0], UP, buff=0)
        lock.next_to(n_priv, RIGHT, buff=0.22)
        self.beat("Set a passphrase when it asks. It encrypts the private key file, so a stolen copy is useless without it.",
                  FadeIn(lock, scale=0.6), run_time=1.4)
        m_priv = M("600", 22, GREY_B).move_to(np.array([-2.78, 0.62, 0]))
        m_pub = M("644", 22, GREY_B).move_to(np.array([-2.78, 0.0, 0]))
        self.beat("And ls -l shows the private key with mode 600, for the owner only, and the public key with 644.",
                  Succession(Wait(1.6), FadeIn(m_priv, shift=LEFT * 0.1), Wait(1.4), FadeIn(m_pub, shift=LEFT * 0.1)), run_time=4.4)

        # ---------- 3. authorized_keys
        auth = filepanel("~/.ssh/authorized_keys", RX, -1.8)
        other = VGroup(key_icon(GREY_B, 0.8, filled=False), M("admin@example.com", 20, GREY_B)).arrange(RIGHT, buff=0.2)
        other.move_to(auth[0].get_corner(UL) + RIGHT * 0.2 + DOWN * 0.72, aligned_edge=LEFT)
        mine_k = key_icon(PUB, 0.8, filled=False)
        mine = VGroup(mine_k, M("you@example.com", 20, PUB)).arrange(RIGHT, buff=0.2)
        mine.move_to(auth[0].get_corner(UL) + RIGHT * 0.2 + DOWN * 1.2, aligned_edge=LEFT)
        self.beat("The server keeps the public keys it trusts in a file called authorized_keys, one per line.",
                  FadeIn(auth, shift=UP * 0.15), Succession(Wait(1.6), FadeIn(other)), run_time=3.2)
        fly = k_pub.copy()
        self.beat("So a copy of your public key goes there, as one more line.",
                  Succession(fly.animate(run_time=1.6, path_arc=-0.6).move_to(np.array([0, PIPE_Y, 0])),
                             Transform(fly, mine_k.copy(), run_time=1.2, path_arc=-0.4), FadeIn(mine[1], run_time=0.5)), run_time=3.6)
        self.remove(fly); self.add(mine)

        # ---------- 4. the server proves who it is
        hk = key_icon(HOST).move_to(np.array([3.05, 0.9, 0]))
        hk_l = T("host key", 24, HOST).next_to(hk, RIGHT, buff=0.25)
        self.beat("Now connect. Trust has to run both ways. First, your laptop checks that this really is your server, which has a key of its own, the host key.",
                  Transform(cmd, M("$ ssh ubuntu@192.168.64.5", 28).move_to(cmd)), Succession(Wait(3.4), FadeIn(VGroup(hk, hk_l), shift=DOWN * 0.1)), run_time=6.0)
        fp = fp_chip("SHA256:4fK9...q2Lw").move_to(np.array([RX, 0.25, 0]))
        prompt = M("Are you sure you want to continue connecting (yes/no/[fingerprint])?", 20, YELLOW_M).move_to(UP * 2.5)
        self.beat("The first time you connect, ssh shows the server's fingerprint, and asks if you are sure you want to continue connecting.",
                  FadeIn(fp, shift=DOWN * 0.1), Succession(Wait(1.0), fp.animate(run_time=1.6).move_to(np.array([0, PIPE_Y, 0]))),
                  Succession(Wait(3.0), FadeIn(prompt, shift=DOWN * 0.1)), run_time=5.2)
        kh = filepanel("~/.ssh/known_hosts", LX, -1.8)
        kh_ip = M("192.168.64.5", 20).move_to(kh[0].get_corner(UL) + RIGHT * 0.2 + DOWN * 0.72, aligned_edge=LEFT)
        yes = M("yes", 22, GREEN_M).next_to(prompt, DOWN, buff=0.12)
        self.beat("Say yes, and ssh stores it in known_hosts, on your laptop.",
                  FadeIn(yes), FadeIn(kh, shift=UP * 0.15), Succession(Wait(1.0), AnimationGroup(FadeIn(kh_ip),
                  fp.animate(run_time=1.4).move_to(kh[0].get_corner(UL) + RIGHT * 0.2 + DOWN * 1.2, aligned_edge=LEFT))), run_time=3.2)
        stored = fp
        self.play(FadeOut(VGroup(prompt, yes)), run_time=0.4)

        fp2 = fp_chip("SHA256:4fK9...q2Lw").move_to(np.array([RX, 0.25, 0]))
        ok1 = tick(True, 0.25).next_to(stored, RIGHT, buff=0.15)
        self.beat("Next time, ssh compares the server's fingerprint with the stored one. They match, so it carries on.",
                  FadeIn(fp2, shift=DOWN * 0.1), Succession(Wait(0.8), fp2.animate(run_time=1.5).move_to(np.array([0, PIPE_Y, 0]))),
                  Succession(Wait(2.6), Indicate(stored, color=GREEN_M), Create(ok1)), run_time=4.6)
        self.play(FadeOut(VGroup(fp2, ok1)), run_time=0.4)

        bad = fp_chip("SHA256:Zp1x...7Hc0", RED_M).move_to(np.array([RX, 0.25, 0]))
        x2 = tick(False, 0.3).move_to(np.array([-1.6, PIPE_Y, 0]))
        refuse = T("ssh refuses to connect", 26, RED_M).move_to(UP * 2.5)
        self.beat("If that fingerprint ever changes, ssh refuses to connect, because someone may be pretending to be your server.",
                  srv[0].animate.set_stroke(RED_M), FadeIn(bad, shift=DOWN * 0.1),
                  Succession(Wait(0.6), bad.animate(run_time=1.4).move_to(np.array([0.6, PIPE_Y, 0])), Create(x2), FadeIn(refuse), Indicate(stored, color=YELLOW_M)),
                  pipe.animate.set_stroke(RED_M), run_time=5.0)
        self.play(FadeOut(VGroup(bad, x2, refuse)), srv[0].animate.set_stroke(GREY_B), pipe.animate.set_stroke(GREY_B), run_time=0.6)

        # ---------- 5. you prove you hold the private key
        data = fp_chip("7f3a9c...e21b", BLUE_M).move_to(np.array([0, PIPE_Y, 0]))
        dlab = T("unique to this connection", 22, BLUE_M).next_to(pipe, DOWN, buff=0.2)
        self.beat("Then the server checks you. Your ssh takes a piece of data that is unique to this connection.",
                  FadeIn(data, scale=0.8), FadeIn(dlab, shift=UP * 0.1), Indicate(VGroup(mine), color=PUB), run_time=2.8)
        spot = np.array([LX, -0.6, 0])
        pk = k_priv.copy()
        self.beat("It signs that data with the private key.",
                  data.animate.move_to(spot), FadeOut(dlab),
                  Succession(Wait(1.2), pk.animate(run_time=0.8).next_to(spot, LEFT, buff=0.1).shift(RIGHT * 0.25)), run_time=2.4)
        sig = fp_chip("signature", PRIV).move_to(spot)
        self.beat("The result is a signature. Only the signature crosses the connection.",
                  FadeOut(pk), ReplacementTransform(data, sig), Succession(Wait(1.2), sig.animate(run_time=1.8).move_to(np.array([RX, -0.6, 0]))), run_time=3.6)
        chk = mine_k.copy()
        ok2 = tick(True, 0.25).next_to(sig, RIGHT, buff=0.15)
        self.beat("The server checks that signature with your public key, from authorized_keys.",
                  Indicate(mine, color=PUB), Succession(Wait(1.0), chk.animate(run_time=1.0).next_to(sig, LEFT, buff=0.15), Create(ok2)), run_time=3.4)
        shell = M("ubuntu@devbox:~$", 24, GREEN_M).move_to(UP * 2.5)
        self.beat("It matches, so you are in. And the private key itself never left your laptop.",
                  FadeIn(shell, shift=DOWN * 0.1), Succession(Wait(1.8), AnimationGroup(Create(stays), Indicate(VGroup(k_priv, n_priv, lock), color=PRIV, scale_factor=1.12))), run_time=4.0)
        self.play(FadeOut(VGroup(sig, chk, ok2, stays)), run_time=0.5)

        # ---------- 6. everyday conveniences
        scene_parts = VGroup(lap, srv, pipe, enc, folder, k_priv, n_priv, k_pub, n_pub, lock, m_priv, m_pub, auth, other, mine, hk, hk_l, kh, kh_ip, stored, shell)
        cfg = VGroup(*[M(s, 26, c) for s, c in [("Host devbox", YELLOW_M), ("    HostName 192.168.64.5", WHITE), ("    User ubuntu", WHITE), ("    IdentityFile ~/.ssh/id_ed25519", WHITE)]])
        cfg.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        for l in cfg[1:]:
            l.shift(RIGHT * 0.6)
        cp = RoundedRectangle(corner_radius=0.12, width=cfg.width + 0.8, height=cfg.height + 0.8, stroke_color=GREY_D, stroke_width=2).set_fill(BLACK, 1)
        cfgg = VGroup(cp, cfg.move_to(cp)).move_to(UP * 0.3)
        cname = M("~/.ssh/config", 22, GREY_B).next_to(cp, UP, buff=0.15).align_to(cp, LEFT)
        self.beat("Two things make everyday use easier. A Host entry in your ssh config file gives the server a short name.",
                  FadeOut(scene_parts), Succession(Wait(1.2), AnimationGroup(Create(cp), FadeIn(cname), LaggedStart(*[FadeIn(l) for l in cfg], lag_ratio=0.3))), run_time=5.0)
        short = M("$ ssh devbox", 28).move_to(cmd)
        self.beat("So ssh devbox replaces the long command.",
                  ReplacementTransform(cmd, short), Indicate(cfg[0], color=YELLOW_M), run_time=2.0)
        agent = T("ssh-agent: holds your unlocked key, so you type the passphrase once", 24, GREY_B).move_to(DOWN * 2.6)
        self.beat("And ssh-agent holds your unlocked key, so you type the passphrase only once.",
                  FadeIn(agent, shift=UP * 0.1), run_time=1.6)

        # ---------- 7. recap
        self.play(FadeOut(VGroup(cfgg, cname, agent, short)), run_time=0.6)
        rec = VGroup(
            VGroup(key_icon(PRIV), T("private key: stays on your laptop", 26)).arrange(RIGHT, buff=0.35),
            VGroup(key_icon(PUB, filled=False), T("public key: one line in authorized_keys", 26)).arrange(RIGHT, buff=0.35),
            VGroup(key_icon(HOST), T("known_hosts: remembers the server's fingerprint", 26)).arrange(RIGHT, buff=0.35),
            VGroup(fp_chip("signature", PRIV), T("the only thing that crosses", 26)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(ORIGIN)
        self.beat("The private key stays home. The public key goes in authorized_keys. known_hosts remembers the server. And only a signature crosses the wire.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rec], lag_ratio=0.6), run_time=7.0)
        self.wait(1.2)
