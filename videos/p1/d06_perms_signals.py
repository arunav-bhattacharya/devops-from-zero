import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bls -l\b", "L S dash L"), (r"\brwx\b", "R W X"), (r"\br-x\b", "R dash X"),
    (r"\bSIGTERM\b", "sig term"), (r"\bSIGKILL\b", "sig kill"), (r"\bSIGINT\b", "sig int"),
    (r"\bsystemd\b", "system D"), (r"\bsystemctl\b", "system control"), (r"\bjournalctl\b", "journal control"),
    (r"\bwww-data\b", "W W W data"), (r"\bPPID\b", "P P I D"), (r"\bCtrl\+C\b", "control C"),
    (r"\bworker\.sh\b", "worker dot S H"), (r"\bkill -9\b", "kill dash nine"), (r"\bdeploy\.sh\b", "deploy dot S H"),
    (r"\bExecStart\b", "exec start"), (r"\bWantedBy=multi-user\.target\b", "wanted by multi user target"),
    (r"\bRestart=on-failure\b", "restart equals on failure"), (r"\bUser=ubuntu\b", "user equals ubuntu"),
    (r"\bhello-worker\.service\b", "hello worker dot service"),
    (r"\b750\b", "seven five oh"), (r"\b755\b", "seven five five"), (r"\b644\b", "six four four"), (r"\b600\b", "six oh oh"),
])

OWN_C, GRP_C, OTH_C = GOLD_M, TEAL_M, GREEN_M


def panel(w, h, color=GREY_D):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=2)
    return r.set_fill(BLACK, 1)


def lit(b, on=True, w=3):
    return b[0].animate.set_stroke(width=6 if on else w)


class D06PermsSignals(VoiceScene):
    def construct(self):
        self.title_card("Who may touch a file, and how to stop a process", "permission bits, PIDs, signals and systemd")

        # ---------- 1. users and the kernel
        proc = box("nginx worker", BLUE_M, w=2.9, h=1.0, size=28).move_to(LEFT * 4.6 + UP * 0.4)
        pu = M("user: www-data", 22, BLUE_M).next_to(proc, DOWN, buff=0.25)
        f = box("deploy.sh", GREY_B, w=2.6, h=1.0, size=28).move_to(RIGHT * 4.6 + UP * 0.4)
        f[1].become(M("deploy.sh", 26).move_to(f[0]))
        fu = M("owner: root", 22, GREY_B).next_to(f, DOWN, buff=0.25)
        self.beat("On Linux, every file and every process belongs to a user. A process carries the ID of the user it runs as.",
                  FadeIn(proc, shift=RIGHT * 0.2), FadeIn(f, shift=LEFT * 0.2), Succession(Wait(2.2), AnimationGroup(FadeIn(pu), FadeIn(fu))), run_time=3.6)
        kern = box("kernel", PURPLE_M, w=2.0, h=1.0, size=28).move_to(UP * 0.4)
        a1, a2 = edge_arrow(proc, kern), edge_arrow(kern, f)
        self.beat("When the process opens a file, the kernel compares that user with the file's owner and permissions.",
                  FadeIn(kern, scale=0.9), GrowArrow(a1), Succession(Wait(1.0), travel(a1, BLUE_M, 0.7), GrowArrow(a2, run_time=0.5), Indicate(fu, color=YELLOW_M)), run_time=4.0)
        root = chip("root  UID 0", RED_M, size=26).move_to(LEFT * 4.6 + DOWN * 2.0)
        skip = CurvedArrow(root.get_right() + RIGHT * 0.1, f.get_bottom() + DOWN * 0.75, angle=np.radians(30), color=RED_M, stroke_width=3)
        self.beat("Only root, the superuser with user ID zero, skips almost every check.",
                  FadeIn(root, shift=UP * 0.15), Succession(Wait(1.4), Create(skip)), run_time=2.8)
        self.play(FadeOut(VGroup(proc, pu, f, fu, kern, a1, a2, root, skip)), run_time=0.6)

        # ---------- 2. reading ls -l
        cmd = M("$ ls -l deploy.sh", 30, GREY_B).move_to(UP * 3.25).align_to(LEFT * 5.6, LEFT)
        line = M("-rw-r--r-- 1 root root 29 Oct 30 05:10 deploy.sh", 32).move_to(UP * 2.35).align_to(LEFT * 5.6, LEFT)
        self.beat("To see a file's permissions, run ls -l.",
                  Write(cmd), Succession(Wait(0.8), FadeIn(line, shift=DOWN * 0.1)), run_time=2.0)

        def field(a, b):
            return VGroup(*line[a:b])
        rest = [(10, 11, "links"), (11, 19, "owner, group"), (19, 21, "size"), (21, 31, "last change"), (31, 40, "name")]
        rlabs = VGroup(*[T(n, 20, GREY_B).next_to(field(a, b), DOWN, buff=0.22) for a, b, n in rest])
        tcol = [GREY_B, OWN_C, GRP_C, OTH_C]
        PY = 0.35

        def perms(s):
            full = M(s, 90)  # one string keeps the font's baseline; then split it into four groups with gaps
            g = VGroup(VGroup(full[0]), VGroup(*full[1:4]), VGroup(*full[4:7]), VGroup(*full[7:10]))
            for i in range(1, 4):
                g[i].set_color(tcol[i]).shift(RIGHT * 0.5 * i)
            return g.move_to(np.array([0, PY, 0]))
        big = perms("-rw-r--r--")
        FH = big.height + 0.36
        frames = VGroup(*[RoundedRectangle(corner_radius=0.08, width=max(p.width, 0.5) + 0.3, height=FH, stroke_color=c, stroke_width=3).move_to(np.array([p.get_x(), big.get_y(), 0]))
                          for p, c in zip(big, tcol)])
        plabs = VGroup(*[T(n, 28, c).next_to(fr, DOWN, buff=0.25) for n, c, fr in zip(["type", "owner", "group", "others"], tcol, frames)])
        self.beat("Look at the first ten characters. The first one is the type: a dash for a file, d for a directory, l for a link.",
                  TransformFromCopy(field(0, 10), big), Succession(Wait(2.2), AnimationGroup(Create(frames[0]), FadeIn(plabs[0]))), run_time=4.2)
        self.beat("The next nine are three groups of three. What the owner may do, what the group may do, and what everyone else, called others, may do.",
                  LaggedStart(*[AnimationGroup(Create(frames[i]), FadeIn(plabs[i], shift=UP * 0.1)) for i in (1, 2, 3)], lag_ratio=0.6), run_time=6.0)
        self.beat("Then come the links, the owner and group, the size, the time, and the name.",
                  LaggedStart(*[FadeIn(l, shift=UP * 0.08) for l in rlabs], lag_ratio=0.5),
                  Succession(Wait(1.4), Indicate(field(11, 19), color=YELLOW_M)), run_time=4.4)

        legend = VGroup(*[VGroup(M(k, 30, YELLOW_M), T(v, 26, GREY_B)).arrange(RIGHT, buff=0.2)
                          for k, v in [("r", "read"), ("w", "write"), ("x", "execute"), ("-", "not allowed")]]).arrange(RIGHT, buff=0.9).move_to(DOWN * 2.1)
        self.beat("In each triplet, r is read, w is write, and x is execute, which means run. A dash means not allowed.",
                  LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in legend], lag_ratio=0.45), run_time=4.0)

        # ---------- 3. which triplet decides
        cmd2 = M("$ chmod 750 deploy.sh", 30, GREY_B).move_to(cmd, aligned_edge=LEFT)
        line2 = M("-rwxr-x--- 1 root root 29 Oct 30 05:10 deploy.sh", 32).move_to(line, aligned_edge=LEFT)
        big2 = perms("-rwxr-x---")
        self.beat("Now change it with chmod 750. Others get nothing at all.",
                  FadeOut(legend), FadeOut(rlabs), ReplacementTransform(cmd, cmd2), ReplacementTransform(line, line2), ReplacementTransform(big, big2),
                  Succession(Wait(2.2), Indicate(big2[3], color=OTH_C)), run_time=3.4)
        cmd, line, big = cmd2, line2, big2

        def at(i):
            return plabs[i].get_center() + DOWN * 1.0
        dev = chip("dev", BLUE_M, size=28).move_to(at(1))
        q = T("For each check, the kernel picks exactly one triplet.", 26, GREY_B).move_to(DOWN * 2.85)
        self.beat("Say user dev tries to run it. For each check, the kernel picks exactly one triplet.",
                  FadeIn(dev, shift=UP * 0.2), Succession(Wait(1.6), FadeIn(q, shift=UP * 0.1)), run_time=3.2)

        def mark(i, ok):
            return tick(ok, 0.22).next_to(frames[i], UP, buff=0.12)
        q1, m1 = T("Does dev own the file?  No, root does.", 26, GREY_B).move_to(q), mark(1, False)
        self.beat("Owner, if you own the file. dev does not.",
                  Transform(q, q1), Succession(Wait(1.2), Create(m1)), run_time=2.4)
        q2, m2 = T("Is dev in the group root?  No.", 26, GREY_B).move_to(q), mark(2, False)
        self.beat("Else group, if you are in its group. dev is not in the group root.",
                  dev.animate.move_to(at(2)), Transform(q, q2), Succession(Wait(1.6), Create(m2)), run_time=3.0)
        q3 = T("So the others triplet decides:  ---", 26, OTH_C).move_to(q)
        self.beat("Else, others. So for dev, only the last three count, and they are all dashes.",
                  dev.animate.move_to(at(3)), Transform(q, q3), frames[3].animate.set_stroke(width=6), run_time=2.6)
        den = M("Permission denied", 30, RED_M).move_to(q)
        self.beat("Permission denied. The first triplet that fits decides, even if a later one allows more.",
                  Transform(q, den), dev[0].animate.set_stroke(RED_M), Succession(Wait(2.0), Indicate(big[3], color=RED_M)), run_time=3.4)

        # ---------- 4. octal
        self.play(FadeOut(VGroup(dev, m1, m2, q)), frames[3].animate.set_stroke(width=3), FadeOut(plabs), run_time=0.6)
        s750 = "-rwxr-x---"
        vy = frames[1].get_bottom()[1] - 0.35
        vals = VGroup()
        for i in range(1, 4):
            for j in range(3):
                c = s750[1 + 3 * (i - 1) + j]
                v = [4, 2, 1][j] if c != "-" else 0
                vals.add(M(str(v), 26, GREY_B).move_to(np.array([big[i][j].get_x(), vy, 0])))
        self.beat("chmod also takes numbers. r is worth four, w two, and x one. A dash is worth zero.",
                  LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in vals], lag_ratio=0.12), run_time=3.6)
        sums = VGroup(*[M(s, 60, c).move_to(np.array([big[i + 1].get_x(), -1.75, 0])) for i, (s, c) in enumerate([("7", OWN_C), ("5", GRP_C), ("0", OTH_C)])])
        adds = VGroup(*[T(t, 22, GREY_B).next_to(sums[i], DOWN, buff=0.15) for i, t in enumerate(["4 + 2 + 1", "4 + 0 + 1", "0 + 0 + 0"])])
        self.beat("Add them up for each triplet. rwx is seven, r-x is five, and three dashes is zero. That is where 750 comes from.",
                  LaggedStart(*[AnimationGroup(FadeIn(sums[i], shift=UP * 0.15), FadeIn(adds[i])) for i in range(3)], lag_ratio=0.7),
                  Succession(Wait(4.0), Indicate(cmd[6:9], color=YELLOW_M, scale_factor=1.4)), run_time=5.6)
        table = VGroup()
        for i, (n, p, u) in enumerate([("755", "rwxr-xr-x", "scripts and folders"), ("644", "rw-r--r--", "normal files"), ("600", "rw-------", "private keys and secrets")]):
            y = -1.25 - 0.6 * i
            table.add(VGroup(M(n, 28, YELLOW_M).move_to(np.array([-4.0, y, 0]), aligned_edge=LEFT),
                             M(p, 26).move_to(np.array([-2.6, y, 0]), aligned_edge=LEFT),
                             T(u, 24, GREY_B).move_to(np.array([0.2, y, 0]), aligned_edge=LEFT)))
        self.beat("You will see three all the time. 755 for scripts and folders, 644 for files, and 600, owner only, for secrets.",
                  FadeOut(VGroup(sums, adds, vals)), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in table], lag_ratio=0.6), run_time=5.4)
        self.play(FadeOut(VGroup(cmd, line, big, frames, table)), run_time=0.7)

        # ---------- 5. processes
        rows = ["USER         PID    PPID CMD",
                "root          98       1 nginx: master process nginx",
                "www-data      99      98 nginx: worker process",
                "www-data     100      98 nginx: worker process",
                "www-data     101      98 nginx: worker process",
                "www-data     102      98 nginx: worker process"]
        pcmd = M("$ ps -o user,pid,ppid,cmd -C nginx", 24, GREY_B)
        tab = VGroup(*[M(r, 24, GREY_B if i == 0 else WHITE) for i, r in enumerate(rows)]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        out = VGroup(pcmd, tab).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(UP * 1.95)
        self.beat("A program is a file on disk. A process is one running copy of it, and the kernel gives each process an ID, its PID.",
                  Write(pcmd), Succession(Wait(2.4), FadeIn(tab[0], shift=DOWN * 0.1)), run_time=4.0)
        master = box("master  PID 98", GOLD_M, w=3.2, h=0.8, size=26).move_to(DOWN * 0.95)
        mu = M("root", 22, GOLD_M).next_to(master, RIGHT, buff=0.25)
        self.beat("Here is nginx, from the lesson's container. One master process runs as root, with PID 98.",
                  FadeIn(tab[1], shift=DOWN * 0.1), Succession(Wait(1.6), AnimationGroup(FadeIn(master, shift=UP * 0.15), FadeIn(mu))), run_time=3.4)
        ws = VGroup(*[box(f"PID {p}", BLUE_M, w=1.9, h=0.75, size=24) for p in (99, 100, 101, 102)]).arrange(RIGHT, buff=0.45).move_to(DOWN * 2.75)
        edges = VGroup(*[link(master, w_, GREY_B, dashed=False, sw=2) for w_ in ws])
        wu = M("www-data", 22, BLUE_M).next_to(ws, RIGHT, buff=0.25)
        fit(VGroup(ws, wu), 12.8).move_to(DOWN * 2.75)
        edges = VGroup(*[link(master, w_, GREY_B, dashed=False, sw=2) for w_ in ws])
        self.beat("It starts four workers, as the user www-data. Their PPID, the parent's PID, is 98. They are the master's children.",
                  LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in tab[2:]], lag_ratio=0.3),
                  Succession(Wait(1.4), AnimationGroup(Create(edges), LaggedStart(*[GrowFromCenter(w_) for w_ in ws], lag_ratio=0.2), FadeIn(wu))), run_time=5.0)
        self.beat("So the code that answers strangers cannot touch root's files.",
                  Indicate(wu, color=BLUE_M), *[lit(w_) for w_ in ws], run_time=1.6)
        self.play(FadeOut(VGroup(out, master, mu, ws, edges, wu)), run_time=0.7)

        # ---------- 6. signals
        wk = box("worker.sh", GREEN_M, w=2.8, h=1.2, size=30).move_to(LEFT * 4.5 + UP * 0.2)
        wk[1].become(M("worker.sh", 28).move_to(wk[0]))
        pid = M("PID 21", 22, GREY_B).next_to(wk, DOWN, buff=0.2)
        logp = panel(7.9, 3.4).move_to(RIGHT * 2.7 + UP * 0.2)
        logt = T("log", 22, GREY_B).next_to(logp, UP, buff=0.12).align_to(logp, LEFT)
        L0 = logp.get_corner(UL) + RIGHT * 0.25 + DOWN * 0.35

        def logline(i, s, color=WHITE):
            return M(s, 20, color).move_to(L0 + DOWN * 0.48 * i, aligned_edge=LEFT)
        lines = [logline(0, "worker: started with PID 21", GREY_B)] + [logline(i, f"worker: processing job {i}") for i in (1, 2, 3)]
        self.beat("To stop a process, you send it a signal, a short message the kernel delivers. Meet worker.sh.",
                  FadeIn(wk, shift=RIGHT * 0.2), FadeIn(pid), Succession(Wait(2.6), AnimationGroup(Create(logp), FadeIn(logt), FadeIn(lines[0]))), run_time=4.8)
        self.beat("Every two seconds, it processes one job, and prints a line.",
                  Succession(*[Succession(FadeIn(l, shift=UP * 0.1, run_time=0.4), Wait(0.6)) for l in lines[1:]]), run_time=3.0)

        kcmd = M("$ kill 21", 30, GREY_B).move_to(np.array([-4.5, 3.2, 0]))
        sig = chip("SIGTERM 15", GOLD_M, size=24).move_to(kcmd.get_center() + DOWN * 0.7)
        self.beat("Run kill with its PID. That sends SIGTERM, signal fifteen: a polite request to shut down.",
                  Write(kcmd), Succession(Wait(1.6), FadeIn(sig, shift=DOWN * 0.1), sig.animate(run_time=1.0).move_to(wk.get_top() + UP * 0.45)), run_time=4.0)
        trap = M("trap on_term TERM", 22, GOLD_M).next_to(pid, DOWN, buff=0.3)
        l4 = logline(4, "worker: got SIGTERM, finishing job 3, then exiting", GOLD_M)
        l5 = logline(5, "worker: stopped cleanly after job 3", GREEN_M)
        ex0 = M("exit code 0", 26, GREEN_M).next_to(trap, DOWN, buff=0.3)
        self.beat("worker.sh catches it with trap. It finishes the job it is on, closes up, and exits cleanly, with code zero.",
                  FadeIn(trap, shift=UP * 0.1), FadeOut(sig, scale=0.5), Succession(Wait(1.2), FadeIn(l4, shift=UP * 0.1), Wait(1.0), FadeIn(l5, shift=UP * 0.1), Wait(0.4), FadeIn(ex0)),
                  wk[0].animate.set_stroke(GREY_B), run_time=5.0)

        # SIGKILL
        kcmd2 = M("$ kill -9 21", 30, GREY_B).move_to(kcmd)
        fresh = [logline(0, "worker: started with PID 21", GREY_B), logline(1, "worker: processing job 1"), logline(2, "worker: processing job 2")]
        self.beat("Start it again. This time, run kill -9.",
                  FadeOut(VGroup(*lines, l4, l5, ex0)), wk[0].animate.set_stroke(GREEN_M), Transform(kcmd, kcmd2),
                  Succession(Wait(0.5), *[FadeIn(l, run_time=0.35) for l in fresh]), run_time=2.6)
        sig9 = chip("SIGKILL 9", RED_M, size=24).move_to(kcmd.get_center() + DOWN * 0.7)
        cut = tick(False, 0.3).move_to(trap)
        self.beat("That sends SIGKILL, signal nine. It cannot be caught, so the trap never runs.",
                  FadeIn(sig9, shift=DOWN * 0.1), Succession(Wait(0.5), sig9.animate(run_time=0.9).move_to(wk.get_center())),
                  Succession(Wait(2.4), Create(cut)), run_time=3.8)
        ex9 = M("exit code 137", 26, RED_M).move_to(ex0)
        self.beat("The process ends at once, and no cleanup runs. The log just stops, in the middle of a job.",
                  FadeOut(sig9, scale=1.6), wk[0].animate.set_stroke(GREY_D).set_fill(BLACK), wk[1].animate.set_opacity(0.35),
                  Succession(Wait(1.8), Indicate(fresh[2], color=RED_M)), Succession(Wait(3.0), FadeIn(ex9)), run_time=4.6)

        # exit codes table
        self.play(FadeOut(VGroup(wk, pid, logp, logt, *fresh, kcmd, trap, cut)), ex9.animate.move_to(UP * 3.1), run_time=0.8)
        hdr = ["signal", "number", "sent by", "exit code"]
        data = [("SIGINT", "2", "Ctrl+C", "130"), ("SIGTERM", "15", "kill PID", "143"), ("SIGKILL", "9", "kill -9 PID", "137")]
        xs = [-4.2, -1.4, 1.4, 4.4]
        H = VGroup(*[T(h, 24, GREY_B).move_to(np.array([x, 1.9, 0])) for h, x in zip(hdr, xs)])
        R = VGroup(*[VGroup(*[M(c, 26, [WHITE, YELLOW_M, GREY_B, WHITE][j]).move_to(np.array([xs[j], 1.1 - 0.7 * i, 0])) for j, c in enumerate(r)]) for i, r in enumerate(data)])
        rule = Line(LEFT * 5.6, RIGHT * 5.6, stroke_width=1.5, color=GREY_D).move_to(UP * 1.55)
        self.beat("When a signal ends a process, its exit code is 128 plus the signal number.",
                  FadeIn(H), Create(rule), LaggedStart(*[FadeIn(r[:2], shift=UP * 0.1) for r in R], lag_ratio=0.3), run_time=3.2)
        self.beat("So 137 means SIGKILL, 143 means SIGTERM, and 130 means someone pressed Ctrl+C.",
                  LaggedStart(*[FadeIn(R[i][2:], shift=LEFT * 0.1) for i in (2, 1, 0)], lag_ratio=0.6),
                  Succession(Wait(0.6), Indicate(R[2][3], color=RED_M), Transform(ex9, M("exit code 137 = 128 + 9", 26, RED_M).move_to(ex9))), run_time=4.6)

        # docker stop timeline
        tl = Line(LEFT * 5.0, RIGHT * 5.0, stroke_width=3, color=GREY_B).move_to(DOWN * 2.2)
        t0 = M("0 s", 22, GREY_B).next_to(tl.get_start(), DOWN, buff=0.2)
        t10 = M("10 s", 22, GREY_B).next_to(tl.get_end(), DOWN, buff=0.2)
        tl.put_start_and_end_on(LEFT * 3.2 + DOWN * 2.2, RIGHT * 5.6 + DOWN * 2.2)
        t0.next_to(tl.get_start(), DOWN, buff=0.2); t10.next_to(tl.get_end(), DOWN, buff=0.2)
        dl = M("docker stop", 26, WHITE).next_to(tl, LEFT, buff=0.35)
        s1 = chip("SIGTERM", GOLD_M, size=22).next_to(tl.get_start(), UP, buff=0.2)
        s2 = chip("SIGKILL", RED_M, size=22).next_to(tl.get_end(), UP, buff=0.2)
        dot = Dot(tl.get_start(), radius=0.09, color=YELLOW_M)
        self.beat("Containers get the same pair. docker stop sends SIGTERM, waits ten seconds, then sends SIGKILL.",
                  Create(tl), FadeIn(dl), FadeIn(t0), FadeIn(t10), Succession(Wait(1.8), FadeIn(s1, shift=DOWN * 0.1), FadeIn(dot),
                  dot.animate(run_time=2.0, rate_func=linear).move_to(tl.get_end()), FadeIn(s2, shift=DOWN * 0.1)), run_time=5.6)
        k8 = T("Kubernetes: the same, with a 30 second default", 24, GREY_B).next_to(VGroup(t0, t10), DOWN, buff=0.25)
        self.beat("Kubernetes does the same, with a thirty second default. So send SIGTERM first, and keep kill -9 for a process that ignores it.",
                  FadeIn(k8, shift=UP * 0.1), Succession(Wait(3.4), Indicate(s1, color=GOLD_M)), run_time=4.6)
        self.play(FadeOut(VGroup(H, R, rule, ex9, tl, t0, t10, dl, s1, s2, dot, k8)), run_time=0.7)

        # ---------- 7. systemd
        sysd = box("systemd  PID 1", PURPLE_M, w=3.2, h=0.9, size=28).move_to(RIGHT * 3.8 + UP * 2.55)
        self.beat("Who starts the worker again after a reboot, or a crash at 3 am? On almost every Linux server, systemd does.",
                  FadeIn(sysd, shift=DOWN * 0.15), run_time=1.6)
        ulines = ["[Unit]", "Description=Practice worker from Day 6", "After=network.target", "",
                  "[Service]", "ExecStart=/usr/local/bin/worker.sh", "Restart=on-failure", "User=ubuntu", "KillMode=mixed", "",
                  "[Install]", "WantedBy=multi-user.target"]
        U = VGroup(*[M(s if s else ".", 20, PURPLE_M if s.startswith("[") else WHITE) for s in ulines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        for s, m in zip(ulines, U):
            if not s:
                m.set_opacity(0)
        up = panel(6.0, U.height + 0.6).move_to(LEFT * 3.65 + DOWN * 0.15)
        U.move_to(up)
        ut = M("hello-worker.service", 22, GREY_B).next_to(up, UP, buff=0.15).align_to(up, LEFT)
        self.beat("It runs each service from a unit file, like this hello-worker.service.",
                  Create(up), FadeIn(ut), LaggedStart(*[FadeIn(m) for m in U], lag_ratio=0.08), run_time=3.6)

        def hl(i, color=YELLOW_M):
            return SurroundingRectangle(U[i], buff=0.06, corner_radius=0.05, stroke_color=color, stroke_width=2.5)
        w1 = box("worker.sh", GREEN_M, w=2.6, h=0.9, size=26).move_to(RIGHT * 3.8 + UP * 0.25)
        w1[1].become(M("worker.sh", 24).move_to(w1[0]))
        wuser = M("user: ubuntu", 22, GREEN_M).next_to(w1, LEFT, buff=0.3)
        a_s = edge_arrow(sysd, w1, GREY_B)
        h1, h2 = hl(5), hl(7)
        self.beat("ExecStart is the command to run. User says to run it as the normal ubuntu user, not as root.",
                  Create(h1), GrowArrow(a_s), FadeIn(w1, shift=DOWN * 0.15), Succession(Wait(2.2), AnimationGroup(Create(h2), FadeIn(wuser))), run_time=4.4)
        h3 = hl(6)
        w2 = box("worker.sh", GREEN_M, w=2.6, h=0.9, size=26).move_to(w1)
        w2[1].become(M("worker.sh", 24).move_to(w2[0]))
        self.beat("If the worker crashes, Restart=on-failure tells systemd to start it again.",
                  FadeOut(h1), FadeOut(h2), Create(h3), Succession(Wait(1.0), w1[0].animate(run_time=0.4).set_stroke(RED_M), FadeOut(w1, scale=0.6, run_time=0.5),
                                                                 Wait(0.4), travel(a_s, PURPLE_M, 0.6), FadeIn(w2, scale=0.8, run_time=0.5)), run_time=4.0)
        h4 = hl(11)
        boot = T("start at boot", 22, PURPLE_M).next_to(sysd, LEFT, buff=0.3)
        self.beat("WantedBy=multi-user.target means: start it at boot. You switch that on with systemctl enable.",
                  FadeOut(h3), Create(h4), FadeIn(boot, shift=RIGHT * 0.1), run_time=2.6)
        jr = box("journal", GREY_B, w=2.2, h=0.8, size=26).move_to(RIGHT * 3.8 + DOWN * 2.05)
        a_j = edge_arrow(w2, jr, TEAL_M)
        jc = M("journalctl -u hello-worker", 22, TEAL_M).next_to(jr, DOWN, buff=0.25)
        self.beat("Everything the worker prints goes into systemd's journal, and journalctl reads it back.",
                  FadeOut(h4), FadeIn(jr, shift=UP * 0.15), GrowArrow(a_j), Succession(Wait(1.0), travel(a_j, TEAL_M, 0.7), FadeIn(jc)), run_time=3.8)
        h5 = hl(8, GOLD_M)
        stopc = chip("SIGTERM", GOLD_M, size=20).move_to(a_s.get_center() + RIGHT * 1.1)
        self.beat("And stopping the service sends SIGTERM to worker.sh first, so it can finish the job it is on.",
                  Create(h5), Succession(Wait(2.0), FadeIn(stopc, shift=DOWN * 0.1), stopc.animate(run_time=0.8).next_to(w2, RIGHT, buff=0.1)), run_time=4.6)

        self.beat("Permission bits decide who may touch a file. Signals ask, or force, a process to stop. And systemd keeps your services running.",
                  FadeOut(VGroup(h5, stopc)), Indicate(sysd, color=PURPLE_M, scale_factor=1.06), run_time=2.0)
        self.wait(1.2)
