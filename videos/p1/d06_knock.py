import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bls -l\b", "L S dash L"), (r"\brwx\b", "R W X"), (r"\brw-\b", "R W dash"), (r"\br--\b", "R dash dash"),
    (r"\bSIGTERM\b", "sig term"), (r"\bSIGKILL\b", "sig kill"), (r"\bSIGINT\b", "sig int"),
    (r"\bCtrl\+C\b", "control C"), (r"\bworker\.sh\b", "worker dot S H"), (r"\bkill -9\b", "kill dash nine"),
    (r"\./deploy\.sh\b", "dot slash deploy dot S H"), (r"\bdeploy\.sh\b", "deploy dot S H"), (r"\bchmod u\+x\b", "C H mod U plus X"),
    (r"\bchmod 777\b", "C H mod seven seven seven"), (r"\bumask\b", "you-mask"),
    (r"\b755\b", "seven five five"), (r"\b644\b", "six four four"), (r"\b600\b", "six oh oh"), (r"\b666\b", "six six six"),
    (r"\b0022\b", "oh oh two two"), (r"\bdana\b", "Dana"),
])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


OWN_C, GRP_C, OTH_C = GOLD_M, TEAL_M, GREEN_M


def person(color, s=1.0):
    head = Circle(radius=0.24, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    body = RoundedRectangle(corner_radius=0.28, width=0.82, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.2), 1)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(body, head).scale(s)


def triplet(bits, color, label):
    """Three slots r w x; a lit slot shows its letter, an empty one a dash."""
    cells = VGroup()
    for ch, on in zip("rwx", bits):
        sq = RoundedRectangle(corner_radius=0.08, width=0.72, height=0.72, stroke_color=color, stroke_width=2.5)
        sq.set_fill(tint(color, 0.35) if on else BLACK, 1)
        t = M(ch if on else "-", 30, WHITE if on else GREY_D).move_to(sq)
        cells.add(VGroup(sq, t))
    cells.arrange(RIGHT, buff=0.12)
    lab = T(label, 26, color).next_to(cells, UP, buff=0.22)
    return VGroup(cells, lab)


class D06Knock(VoiceScene):
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

    def countdown(self, where, label="pause and guess"):
        c = chip(label, YELLOW_M, size=26).move_to(where)
        self.play(FadeIn(c, scale=0.9), run_time=0.4)
        for n in ("3", "2", "1"):
            d = T(n, 34, YELLOW_M).next_to(c, RIGHT, buff=0.35)
            self.play(FadeIn(d, run_time=0.15))
            self.wait(0.6)
            self.remove(d)
        self.play(FadeOut(c), run_time=0.3)

    def construct(self):
        self.title_card("The master key and the security guard", "two Friday shortcuts, and what to do instead")

        # ---------- 1. Friday afternoon
        p1 = VGroup(M("$ ./deploy.sh", 28), M("bash: ./deploy.sh: Permission denied", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(LEFT * 2.9 + UP * 2.1)
        w = person(GREY_B).move_to(RIGHT * 3.6 + UP * 2.0)
        wl = T("an old worker that won't stop", 26, GREY_B).next_to(w, DOWN, buff=0.2)
        self.beat("Friday afternoon. Your new script for the shop's nightly job won't start. The screen says Permission denied.",
                  FadeIn(p1[0]), Succession(Wait(2.8), FadeIn(p1[1])), run_time=4.0)
        self.beat("Down the hall, an old worker program is still running, and won't stop. Everyone wants to go home.",
                  FadeIn(w), FadeIn(wl), run_time=2.0)
        k = VGroup(chip("the master key", RED_M, 28), M("sudo", 26, RED_M)).arrange(DOWN, buff=0.2).move_to(LEFT * 2.9 + DOWN * 0.9)
        g = VGroup(chip("call security", RED_M, 28), M("kill -9", 26, RED_M)).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.6 + DOWN * 0.9)
        self.beat("Two shortcuts are right there. Borrow the master key for everything. Or call security, and have the worker dragged out mid-task.",
                  Succession(Wait(1.8), FadeIn(k[0], shift=UP * 0.1)), Succession(Wait(3.6), FadeIn(g[0], shift=UP * 0.1)), run_time=5.4)
        self.beat("In the terminal, those are sudo and kill -9. Both work at once, which is why they feel safe.",
                  FadeIn(k[1]), FadeIn(g[1]), run_time=2.4)
        mon = T("and both leave a mess for Monday", 30, YELLOW_M).move_to(DOWN * 2.7)
        self.beat("And both leave a mess for Monday. Let's take the two problems one at a time.",
                  FadeIn(mon, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(p1, w, wl, k, g, mon)), run_time=0.6)

        # ---------- 2. badges and drawers
        badge = VGroup(person(BLUE_M), T("your badge: a user", 26, BLUE_M)).arrange(DOWN, buff=0.2).move_to(LEFT * 4.2 + UP * 0.5)
        drw = box("drawer: deploy.sh", GOLD_M, w=3.6, h=1.0, size=26).move_to(RIGHT * 0.4 + UP * 0.5)
        sign = T("a sign: who may do what", 24, GREY_B).next_to(drw, DOWN, buff=0.25)
        self.beat("In our office building, everyone wears a badge, and every drawer belongs to someone. In Linux, every file and every running program belongs to a user.",
                  FadeIn(badge), Succession(Wait(2.6), FadeIn(drw)), run_time=4.4)
        krn = VGroup(T("the kernel checks", 26, GREY_B), T("badge against sign", 26, GREY_B)).arrange(DOWN, buff=0.1).move_to(RIGHT * 4.6 + UP * 0.5)
        self.beat("When a program opens a file, the kernel, the core of the operating system, checks the badge against the sign on the drawer.",
                  FadeIn(sign), FadeIn(krn), run_time=2.4)
        mk = VGroup(person(RED_M), T("root, user ID 0", 26, RED_M), T("skips almost every check", 24, GREY_B)).arrange(DOWN, buff=0.15).move_to(LEFT * 4.2 + DOWN * 2.2)
        self.beat("The building manager with the master key is called root, user ID zero. The kernel skips almost every check for root.",
                  FadeIn(mk, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(VGroup(badge, drw, sign, krn, mk)), run_time=0.6)

        # ---------- 3. reading the sign: ls -l
        parts = [("-", GREY_B), ("rw-", OWN_C), ("r--", GRP_C), ("r--", OTH_C), (" 1 ", GREY_D), ("root", OWN_C), (" ", WHITE), ("root", GRP_C),
                 (" 29 Oct 30 05:10 deploy.sh", GREY_B)]
        ln = VGroup(*[M(s_, 30, c) for s_, c in parts])
        ln.arrange(RIGHT, buff=0.02)
        ln[4].next_to(ln[3], RIGHT, buff=0.22)
        ln[5].next_to(ln[4], RIGHT, buff=0.22)
        ln[7].next_to(ln[5], RIGHT, buff=0.22)
        ln[8].next_to(ln[7], RIGHT, buff=0.22)
        ln.remove(ln[6])
        ln.move_to(UP * 2.75)
        cmd = M("$ ls -l deploy.sh", 26, GREY_B).next_to(ln, UP, buff=0.2).align_to(ln, LEFT)
        self.beat("So let's read the sign, with ls -l. It looks like noise at first.",
                  FadeIn(cmd), Succession(Wait(1.6), Write(ln)), run_time=3.2)
        TR = VGroup(triplet([1, 1, 0], OWN_C, "owner"), triplet([1, 0, 0], GRP_C, "group"), triplet([1, 0, 0], OTH_C, "everyone else")).arrange(RIGHT, buff=1.0).move_to(UP * 0.2)
        ty = T("the first character is the type: - for a file, d for a directory", 24, GREY_B).move_to(DOWN * 1.6)
        self.beat("The first character is the type: a dash for a file, d for a directory.", Indicate(ln[0], color=WHITE, scale_factor=1.6), FadeIn(ty), run_time=1.6)
        self.beat("Then three groups of three. What the owner may do, what the group may do, and what everyone else may do.",
                  FadeOut(ty), *[TransformFromCopy(ln[i + 1], TR[i]) for i in range(3)], run_time=3.0)
        rwx = T("r = read, w = write, x = execute (run). A dash means not allowed.", 26, GREY_B).move_to(DOWN * 1.5)
        self.beat("R is read, W is write, X is execute, which means run. A dash means not allowed.",
                  FadeIn(rwx), run_time=2.0)
        own = T("owner and group: root and root", 26, GREY_B).move_to(DOWN * 2.2)
        self.beat("Then come the owner and the group. A group is a named set of users.",
                  Indicate(ln[4], color=OWN_C), Indicate(ln[5], color=GRP_C), FadeIn(own), run_time=2.0)
        one = T("the kernel uses exactly one: owner if you own it, else group if you're in it, else everyone else", 26, YELLOW_M).move_to(DOWN * 2.9)
        fit(one, 12.6)
        self.beat("For each check, the kernel picks exactly one group of three: the owner's if you own the file, else the group's if you're in it, else everyone else's. The first that fits decides.",
                  Succession(Wait(1.6), FadeIn(one, shift=UP * 0.1), Indicate(TR[0], color=OWN_C), Indicate(TR[1], color=GRP_C), Indicate(TR[2], color=OTH_C)), run_time=6.4)
        self.play(FadeOut(VGroup(rwx, own, one)), run_time=0.4)

        # ---------- 4. predict: which bit is missing?
        self.beat("Now back to Friday. You are the owner, and running the script says Permission denied. Which slot is empty?",
                  Indicate(TR[0][1], color=OWN_C), run_time=1.6)
        self.countdown(DOWN * 1.6)
        xs = TR[0][0][2]
        self.beat("The owner's X. Nobody may run this file. Not even you.", Circumscribe(xs, color=RED_M, buff=0.06), xs[0].animate.set_stroke(RED_M), run_time=1.8)
        um = VGroup(M("ask for 666", 26, GREY_B), T("minus", 24, GREY_B), M("umask 0022", 26, GREY_B), T("=", 26, GREY_B), M("644", 26, YELLOW_M)).arrange(RIGHT, buff=0.25).move_to(DOWN * 1.6)
        self.beat("That's normal. Programs usually ask for six six six, read and write for everyone, and a setting called the umask removes write for group and others. So a fresh file is 644, with no X for anyone.",
                  Succession(Wait(2.0), LaggedStart(*[FadeIn(u_) for u_ in um], lag_ratio=0.4)), run_time=7.0)

        # octal digits
        dg = VGroup(*[M(str(n), 44, c).next_to(TR[i][0], DOWN, buff=0.35) for i, (n, c) in enumerate([(6, OWN_C), (4, GRP_C), (4, OTH_C)])])
        val = T("r = 4, w = 2, x = 1: add up the slots that are on", 26, GREY_B).move_to(DOWN * 2.6)
        self.beat("Where does 644 come from? R is worth four, W two, X one. Add the slots that are on. Read plus write is six. Read alone is four.",
                  FadeOut(um), FadeIn(val), Succession(Wait(3.4), LaggedStart(*[FadeIn(d_, shift=UP * 0.1) for d_ in dg], lag_ratio=0.5)), run_time=6.0)
        table = VGroup(VGroup(M("755", 26, YELLOW_M), M("rwxr-xr-x", 26), T("scripts and folders", 24, GREY_B)).arrange(RIGHT, buff=0.4),
                       VGroup(M("644", 26, YELLOW_M), M("rw-r--r--", 26), T("normal files", 24, GREY_B)).arrange(RIGHT, buff=0.4),
                       VGroup(M("600", 26, YELLOW_M), M("rw-------", 26), T("private keys and secrets", 24, GREY_B)).arrange(RIGHT, buff=0.4))
        for r_ in table[1:]:
            r_.align_to(table[0], LEFT)
        table.arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(DOWN * 2.6)
        self.beat("Three you'll meet all the time: seven five five for scripts and folders, six four four for files, six oh oh for secrets.",
                  FadeOut(val), LaggedStart(*[FadeIn(r_, shift=UP * 0.1) for r_ in table], lag_ratio=0.7), run_time=5.0)
        self.play(FadeOut(table), run_time=0.4)

        # the shortcut breaks, the one-bit fix
        bad = VGroup(M("sudo ./deploy.sh", 26, RED_M), T("hides the cause, leaves files only root can change", 24, GREY_B),
                     M("chmod 777", 26, RED_M), T("lets every user on the machine change it", 24, GREY_B)).arrange_in_grid(rows=2, cols=2, buff=(0.4, 0.2), col_alignments="rl").move_to(DOWN * 2.4)
        self.beat("Now the shortcuts. sudo hides the real cause, and leaves behind files only root can change. chmod 777 lets every user on the machine change the file. That's not fixing the lock. That's taking the door off.",
                  LaggedStart(*[FadeIn(b_) for b_ in bad], lag_ratio=0.5), run_time=6.4)
        fix = M("$ chmod u+x deploy.sh", 28, GREEN_M).move_to(DOWN * 1.7)
        ln2 = M("-rwxr--r--", 30, WHITE).move_to(ln[0:4])
        self.steps("The real fix is one missing bit. chmod, U plus X: give the owner execute. Nothing else changes.",
                   (0.6, FadeOut(bad), FadeOut(dg)), (0.8, Write(fix)),
                   (0.8, xs[0].animate.set_stroke(OWN_C).set_fill(tint(OWN_C, 0.35), 1), Transform(xs[1], M("x", 30, WHITE).move_to(xs[1]))),
                   (0.6, Indicate(ln[1], color=OWN_C)))
        r1 = T("Fix the one bit that is missing. Never reach for chmod 777.", 30, YELLOW_M).move_to(DOWN * 2.8)
        self.beat("Fix the one bit that is missing. Never reach for chmod 777.", FadeIn(r1, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(cmd, ln, TR, fix, r1)), run_time=0.6)

        # ---------- 5. the worker who won't leave: signals
        jd = box("job description: worker.sh", GREY_B, w=4.6, h=0.85, size=26).move_to(LEFT * 3.6 + UP * 2.75)
        wk = person(BLUE_M).move_to(LEFT * 3.6 + UP * 1.3)
        wkl = T("on shift: a process, with a PID", 26, BLUE_M).next_to(wk, DOWN, buff=0.2)
        self.beat("Now the second problem. A program is a job description in a drawer: a file on disk. A process is one running copy, a worker on shift, with a number called its PID, its process ID.",
                  FadeIn(jd), Succession(Wait(3.0), AnimationGroup(FadeIn(wk, shift=UP * 0.2), FadeIn(wkl))), run_time=5.6)
        logbox = RoundedRectangle(corner_radius=0.12, width=6.6, height=2.75, stroke_color=GREY_B, stroke_width=2).set_fill(BLACK, 1).move_to(RIGHT * 2.9 + UP * 1.55)
        logl = T("its log", 24, GREY_B).next_to(logbox, DOWN, buff=0.12).align_to(logbox, RIGHT)
        LOG_TL = logbox.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.3
        self.beat("The lesson's worker.sh is a pretend background worker. Every two seconds it processes one job, and writes a line.",
                  Create(logbox), FadeIn(logl), run_time=1.6)

        def logline(i, text, color=WHITE):
            return M(text, 22, color).move_to(LOG_TL + DOWN * 0.44 * i, aligned_edge=UL)

        jobs = VGroup(*[logline(i, f"worker: processing job {i + 1}") for i in range(3)])
        self.play(LaggedStart(*[FadeIn(j, shift=UP * 0.05) for j in jobs], lag_ratio=0.8), run_time=2.4)
        kn = VGroup(T("the knock", 28, TEAL_M), T("please finish and go home", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to(LEFT * 3.6 + DOWN * 0.75)
        gd = VGroup(T("security", 28, RED_M), T("carried out mid-task", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to(LEFT * 3.6 + DOWN * 2.0)
        self.beat("There are two ways to end a shift. Knock, and say: please finish up and go home.",
                  FadeIn(kn, shift=UP * 0.1), run_time=2.0)
        self.beat("Or call security, and have them carried out mid-sentence. One leaves tidy desks. The other leaves half-filed papers everywhere.",
                  FadeIn(gd, shift=UP * 0.1), run_time=1.6)
        sigs = VGroup(VGroup(M("SIGTERM 15", 26, TEAL_M), T("the knock:  kill PID", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                      VGroup(M("SIGKILL  9", 26, RED_M), T("security:  kill -9 PID", 24, GREY_B)).arrange(RIGHT, buff=0.3),
                      VGroup(M("SIGINT   2", 26, GOLD_M), T("what Ctrl+C sends", 24, GREY_B)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        sigs.move_to(RIGHT * 2.9 + DOWN * 1.35)
        self.beat("That knock is a signal: a short message the kernel delivers to a process. The polite one is SIGTERM, number fifteen. Plain kill sends it.",
                  Succession(Wait(3.0), FadeIn(sigs[0])), run_time=4.4)
        self.beat("Security is SIGKILL, number nine, sent with kill -9. It cannot be caught, so no cleanup runs. And Ctrl+C sends SIGINT, number two.",
                  FadeIn(sigs[1]), Succession(Wait(3.4), FadeIn(sigs[2])), run_time=4.6)

        # predict: what does the log say after a plain kill?
        self.beat("worker.sh catches SIGTERM with a shell command called trap. It's on job three, and you knock with a plain kill. What does the log say next?",
                  Indicate(jobs[2], color=WHITE), Indicate(kn[0], color=TEAL_M), run_time=1.8)
        self.countdown(RIGHT * 2.9 + DOWN * 2.95)
        t1 = fit(logline(3, "worker: got SIGTERM, finishing job 3, then exiting", TEAL_M), 6.1)
        t2 = logline(4, "worker: stopped cleanly after job 3", TEAL_M)
        ex0 = M("exit code 0", 26, GREEN_M).next_to(logbox, DOWN, buff=0.15).align_to(logbox, LEFT)
        self.steps("It finishes job three, says so, and leaves. Stopped cleanly after job three. Exit code zero, a clean ending.",
                   (0.6, FadeIn(t1, shift=UP * 0.05)), (1.4, Wait(1.4)), (0.6, FadeIn(t2, shift=UP * 0.05)), (0.5, FadeIn(ex0)))
        self.play(FadeOut(VGroup(t1, t2, ex0)), run_time=0.4)
        t3 = VGroup()
        cut = Line(jobs[2].get_right() + RIGHT * 0.15, jobs[2].get_right() + RIGHT * 1.3, stroke_width=3, color=RED_M)
        ex9 = M("exit code 137", 26, RED_M).move_to(ex0, aligned_edge=LEFT)
        self.steps("Run it again, and on job three, send kill -9. The log just stops, mid-job. Nobody finished anything. Exit code 137.",
                   (0.6, Indicate(jobs[2], color=WHITE), Indicate(gd[0], color=RED_M)), (1.6, Wait(1.6)), (0.4, Create(cut)), (0.4, wk.animate.set_opacity(0.25)), (1.4, Wait(1.4)), (0.5, FadeIn(ex9)))
        cd = VGroup(T("killed by a signal: 128 + its number", 26, YELLOW_M),
                    M("130 = Ctrl+C   143 = SIGTERM   137 = SIGKILL", 24, GREY_B)).arrange(DOWN, buff=0.15).move_to(RIGHT * 2.6 + DOWN * 2.85)
        fit(cd, 7.4)
        self.beat("When a signal kills a process, the exit code is 128 plus the signal number. 137 is 128 plus nine. You'll meet it again when Docker or Kubernetes kills a container that used too much memory.",
                  FadeOut(sigs), FadeIn(cd), run_time=3.0)

        # guardrail
        self.play(FadeOut(VGroup(cd, t3, cut, ex9, jobs, logbox, logl)), wk.animate.set_opacity(1), run_time=0.6)
        tl = NumberLine(x_range=[0, 12, 2], length=6.6, include_numbers=True, font_size=24, color=GREY_B).move_to(RIGHT * 2.9 + UP * 0.6)
        tll = T("docker stop", 28, BLUE_M).next_to(tl, UP, buff=1.0).align_to(tl, LEFT)
        k0 = VGroup(Line(DOWN * 0.25, UP * 0.25, color=TEAL_M, stroke_width=4), M("SIGTERM", 24, TEAL_M)).arrange(UP, buff=0.1)
        k0.move_to(tl.n2p(0), aligned_edge=DOWN).shift(UP * 0.05)
        k10 = VGroup(Line(DOWN * 0.25, UP * 0.25, color=RED_M, stroke_width=4), M("SIGKILL", 24, RED_M)).arrange(UP, buff=0.1)
        k10.move_to(tl.n2p(10), aligned_edge=DOWN).shift(UP * 0.05)
        sec = T("seconds", 22, GREY_B).next_to(tl, DOWN, buff=0.5).align_to(tl, RIGHT)
        self.beat("The same pair stops containers. docker stop sends SIGTERM, waits ten seconds, and only then sends SIGKILL. Kubernetes does the same, with a thirty second default.",
                  FadeIn(tll), Create(tl), FadeIn(sec), Succession(Wait(1.6), FadeIn(k0)), Succession(Wait(3.6), FadeIn(k10)), run_time=6.4)
        gr = T("the knock comes first, and the guard waits outside", 26, GREY_B).next_to(sec, DOWN, buff=0.3).align_to(tl, RIGHT)
        fit(gr, 7.0)
        self.beat("The knock comes first, and the guard waits outside. So a program that handles SIGTERM gets to finish its work.", FadeIn(gr), run_time=2.0)
        r2 = T("Knock with SIGTERM first. Keep kill -9 for a process that ignores the knock.", 28, YELLOW_M).move_to(DOWN * 2.95)
        fit(r2, 12.6)
        self.beat("Knock with SIGTERM first. Keep kill -9 for a process that ignores the knock.", FadeIn(r2, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(tl, tll, k0, k10, sec, gr, r2, jd, wk, wkl, kn, gd)), run_time=0.6)

        # ---------- 6. moral, check
        m = VGroup(T("Permission denied? Read the sign, and fix the one missing bit.", 30, GOLD_M),
                   T("A worker that won't stop? Knock with SIGTERM before you call security.", 30, TEAL_M),
                   T("Name the real cause before you reach for the shortcut.", 30, YELLOW_M)).arrange(DOWN, buff=0.35).move_to(UP * 0.3)
        fit(m, 12.6)
        self.beat("So, back to Friday. The script was missing one execute bit. The worker deserved a polite knock, and a few seconds to finish. Neither needed the master key or security. The moral: name the real cause before you reach for the shortcut.",
                  FadeIn(m[0], shift=UP * 0.1), Succession(Wait(3.6), FadeIn(m[1], shift=UP * 0.1)), Succession(Wait(7.0), FadeIn(m[2], shift=UP * 0.1)), run_time=9.6)
        self.play(FadeOut(m), run_time=0.5)
        cq = VGroup(T("A file shows", 30), M("-rw-r-----", 28), T("and belongs to", 30), M("app:ops", 28)).arrange(RIGHT, buff=0.2).move_to(UP * 1.9)
        cq2 = T("Dana is in the group ops, but is not the owner. What can Dana do?", 30).next_to(cq, DOWN, buff=0.25)
        fit(cq2, 12.6)
        opts = VGroup(*[T(o, 28, GREY_B) for o in ("read it and write it", "read it only", "nothing at all", "run it as a program")]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(cq2, DOWN, buff=0.5)
        self.beat("A quick check. A file shows R W dash, R dash dash, dash dash dash. It belongs to user app and group ops. Dana is in ops, but isn't the owner. What can Dana do?",
                  Succession(FadeIn(VGroup(cq, cq2), run_time=0.8), Wait(4.8), LaggedStart(*[FadeIn(o, shift=RIGHT * 0.1) for o in opts], lag_ratio=0.3)), run_time=7.6)
        self.countdown(DOWN * 3.0, "pause and think")
        self.beat("Read it only. Dana is not the owner but is in the group, so the group's three slots decide, and they say R dash dash.",
                  opts[1].animate.set_color(GREEN_M), *[o.animate.set_opacity(0.35) for i, o in enumerate(opts) if i != 1], run_time=1.6)
        self.wait(1.2)
