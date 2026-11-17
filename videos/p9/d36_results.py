import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bjq\b", "J Q"), (r"\bsysctl\.conf\b", "sys control dot conf"), (r"\bmotd\b", "M O T D"),
            (r"\bidempotence\b", "eye-dem-potence"), (r"\blineinfile\b", "line in file"), (r"\bweb2\b", "web two"),
            (r"\blb1\b", "L B one"), (r"\bweb1\b", "web one"), (r"\bansible-doc\b", "ansible doc")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(rows, color, buff=0.28):
    fr = RoundedRectangle(corner_radius=0.12, width=rows.width + 2 * buff, height=rows.height + 2 * buff, stroke_color=color, stroke_width=2.5)
    fr.set_fill(tint(color, 0.10), 1)
    return VGroup(fr, rows.move_to(fr))


def pot():
    p = Polygon([-0.55, 0.45, 0], [0.55, 0.45, 0], [0.4, -0.55, 0], [-0.4, -0.55, 0], stroke_color=GOLD_M, stroke_width=3)
    p.set_fill(tint(GOLD_M, 0.10), 1)
    stem = Line([0, 0.45, 0], [0, 1.25, 0], stroke_color=GREEN_M, stroke_width=4)
    l1 = Ellipse(width=0.5, height=0.22, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.4), 1).move_to([0.25, 0.95, 0]).rotate(0.5)
    l2 = Ellipse(width=0.5, height=0.22, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.4), 1).move_to([-0.25, 1.15, 0]).rotate(-0.5)
    return VGroup(p, stem, l1, l2)


def water(level):
    """Water in the pot; level 0..1 fills the pot, above 1 spills over the rim."""
    h = max(0.05, 1.0 * level)
    r = Rectangle(width=1.0 if level <= 1 else 1.3, height=h, stroke_width=0).set_fill(BLUE_M, 0.55)
    r.move_to([0, -0.55 + h / 2, 0])
    return r


def thermo(deg, color=TEAL_M):
    r = RoundedRectangle(corner_radius=0.1, width=1.2, height=1.5, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.10), 1)
    t = T(f"{deg}°", 32, color).move_to(r)
    return VGroup(r, t)


def door(locked=True):
    d = Rectangle(width=0.9, height=1.6, stroke_color=PURPLE_M, stroke_width=3).set_fill(tint(PURPLE_M, 0.12), 1)
    knob = Dot(radius=0.06, color=PURPLE_M).move_to(d.get_right() + LEFT * 0.18)
    lab = T("locked" if locked else "open", 22, PURPLE_M if locked else RED_M).next_to(d, DOWN, buff=0.15)
    return VGroup(d, knob, lab)


class D36Results(VoiceScene):
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

    def construct(self):
        self.title_card("Chores or results?", "why an Ansible playbook is safe to run twice")

        # ---------- 1. the shy question
        q1 = T("You run the same setup twice on a server.", 34).move_to([0, 0.8, 0])
        q2 = T("Is that safe? And why would it not be?", 34, YELLOW_M).move_to([0, -0.2, 0])
        self.beat("Here's a question most people are too polite to ask. You run the same setup on a server twice. Is that safe? And why on earth wouldn't it be?",
                  FadeIn(q1, shift=UP * 0.15), Succession(Wait(2.2), FadeIn(q2, shift=UP * 0.15)), run_time=4.0)
        self.beat("Before computers, let's look after a house.", FadeOut(VGroup(q1, q2)), run_time=1.0)

        # ---------- 2. familiar: the neighbour's list of chores
        chores = VGroup(T("water the plants", 28), T("turn the heating on", 28), T("lock the back door", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        lst = panel(chores, GREY_B, buff=0.35).move_to([-3.9, 0.0, 0])
        lt = T("the neighbour's list", 26, GREY_B).next_to(lst, UP, buff=0.2)
        P = pot().move_to([1.2, 0.2, 0])
        W = water(0.0).move_to(P[0].get_bottom() + UP * 0.025)
        TH = thermo(15, GREY_B).move_to([3.3, 0.2, 0])
        D = door(False).move_to([5.3, 0.1, 0])
        self.beat("Your neighbour goes away for a week and leaves you a list of chores. Water the plants. Turn the heating on. Lock the back door.",
                  FadeIn(lst), FadeIn(lt), Succession(Wait(2.4), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in chores], lag_ratio=0.7)),
                  FadeIn(P), FadeIn(TH), FadeIn(D), run_time=5.4)
        day = T("Monday", 30, YELLOW_M).move_to([3.3, 2.6, 0])
        self.add(W)

        def wlevel(lv):
            return water(lv).align_to(P[0], DOWN).shift(UP * 0.0).set_x(P[0].get_x())
        self.steps("On Monday you do every chore, top to bottom. Good job.",
                   (0.5, FadeIn(day)), (0.8, Indicate(chores[0], color=BLUE_M), Transform(W, wlevel(0.3))),
                   (0.8, Indicate(chores[1], color=TEAL_M), Transform(TH, thermo(20, TEAL_M).move_to(TH))),
                   (0.8, Indicate(chores[2], color=PURPLE_M), Transform(D, door(True).move_to(D))))
        lv = 0.3
        for dname in ("Tuesday", "Wednesday", "Thursday"):
            lv += 0.25
            self.play(Transform(day, T(dname, 30, YELLOW_M).move_to(day)), Indicate(chores[0], color=BLUE_M), Transform(W, wlevel(lv)), run_time=0.9)
        self.beat("And every day after, you water the plants again, because the list says so.", Wait(0.2), run_time=0.4)
        swim = T("swimming", 28, BLUE_M).next_to(P, UP, buff=0.25)
        self.steps("By Friday, the pots are swimming. Those plants didn't need a sitter. They needed a lifeguard.",
                   (0.6, Transform(day, T("Friday", 30, RED_M).move_to(day))), (1.0, Transform(W, wlevel(1.25)), FadeIn(swim)))
        self.beat("And notice, the trouble wasn't you. You followed the list perfectly. The list said what to do, when it should have said how the house should be.",
                  Indicate(lst[0], color=GREY_B, scale_factor=1.03), run_time=2.0)

        # ---------- 3. the same list, written as results
        results = VGroup(T("soil damp", 28, BLUE_M), T("room at 20 degrees", 28, TEAL_M), T("door locked", 28, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        results.move_to(chores, aligned_edge=LEFT)
        self.play(FadeOut(swim), Transform(W, wlevel(0.3)), Transform(day, T("next week", 30, YELLOW_M).move_to(day)), run_time=0.8)
        self.beat("So let's rewrite the list as results. Soil damp. Room at twenty degrees. Door locked.",
                  Succession(Wait(1.4), LaggedStart(*[ReplacementTransform(c, r) for c, r in zip(chores, results)], lag_ratio=0.5)), run_time=4.0)
        oks = VGroup(*[T("ok", 26, GREEN_M).next_to(results[i], RIGHT, buff=0.5) for i in range(3)])
        oks.align_to(oks[1], LEFT)
        self.beat("Now each line starts with a look. Is the soil damp? Yes, so you do nothing. Is the room warm? Yes. Is the door locked? Yes.",
                  Succession(Wait(1.0), AnimationGroup(Indicate(P[0], color=BLUE_M), FadeIn(oks[0]))),
                  Succession(Wait(3.6), AnimationGroup(Indicate(TH[1], color=TEAL_M), FadeIn(oks[1]))),
                  Succession(Wait(4.8), AnimationGroup(Indicate(D[0], color=PURPLE_M), FadeIn(oks[2]))), run_time=6.2)
        self.beat("Run this list a hundred times and the house stays exactly right. Checking twice does no harm.",
                  Indicate(results, color=WHITE, scale_factor=1.03), run_time=2.0)
        self.play(FadeOut(oks), run_time=0.4)
        self.beat("Now say the wind blows the back door open on Wednesday.",
                  Transform(D, door(False).move_to(D)), Transform(day, T("Wednesday", 30, YELLOW_M).move_to(day)), run_time=1.6)
        ch = T("changed", 26, YELLOW_M).next_to(results[2], RIGHT, buff=0.5).align_to(oks[0], LEFT)
        oks2 = VGroup(oks[0].copy(), oks[1].copy())
        self.beat("The same list notices. Soil fine, room fine, door open, so you lock it. One line reports changed, and only that one did any work.",
                  FadeIn(oks2), Succession(Wait(2.4), AnimationGroup(Transform(D, door(True).move_to(D)), FadeIn(ch))), run_time=4.6)
        self.wait(0.4)
        self.play(FadeOut(VGroup(P, W, TH, D, day, oks2, ch)), run_time=0.6)

        # ---------- 4. map it onto Ansible
        tasks = VGroup(M("apt: name=jq state=present", 22, BLUE_M), M("copy: dest=/etc/motd", 22, TEAL_M), M("service: name=nginx state=started", 22, PURPLE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        plist = panel(tasks, GOLD_M, buff=0.35).move_to([-3.5, 0.0, 0])
        plt = T("playbook", 26, GOLD_M).next_to(plist, UP, buff=0.2)
        self.beat("Ansible, the tool that sets up the inside of servers, works exactly like the second list. A playbook is the list. Each line is a task, and each task names a module, a small program that does one job.",
                  ReplacementTransform(lst, plist), ReplacementTransform(lt, plt), Succession(Wait(3.0), LaggedStart(*[ReplacementTransform(r, t) for r, t in zip(results, tasks)], lag_ratio=0.4)), run_time=6.0)
        srv = RoundedRectangle(corner_radius=0.15, width=4.0, height=3.4, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.06), 1).move_to([3.9, 0.0, 0])
        sl = T("a fresh server", 26, TEAL_M).next_to(srv, UP, buff=0.2)
        st = VGroup(T("jq: missing", 26, GREY_B), T("/etc/motd: old text", 26, GREY_B), T("nginx: stopped", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(srv)
        self.beat("And each task is written as a result. name jq, state present, means jq must be installed. It doesn't say install it. It says how the server should be.",
                  Create(srv), FadeIn(sl), FadeIn(st), Indicate(tasks[0], color=BLUE_M, scale_factor=1.04), run_time=4.0)

        # ---------- 5. predict, then show: run it twice
        runl = T("run 1", 28, YELLOW_M).move_to([0.3, 2.65, 0])
        self.beat("Let's run it. The module looks at the server first, and acts only where something differs.", FadeIn(runl), run_time=1.6)
        chs = VGroup(*[T("changed", 24, YELLOW_M).next_to(tasks[i], DOWN, buff=0.08).align_to(tasks[i], RIGHT) for i in range(3)])
        st_new = [T("jq: installed", 26, GREEN_M), T("/etc/motd: our text", 26, GREEN_M), T("nginx: running", 26, GREEN_M)]
        plays = []
        for i in range(3):
            a = Arrow(plist.get_right(), srv.get_left() + UP * (st[i].get_y() - srv.get_y()), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.1)
            a.put_start_and_end_on(np.array([plist.get_right()[0] + 0.1, tasks[i].get_y(), 0]), np.array([srv.get_left()[0] - 0.1, st[i].get_y(), 0]))
            plays.append((0.7, travel(a, GOLD_M, 0.6)))
            plays.append((0.6, Transform(st[i], st_new[i].move_to(st[i], aligned_edge=LEFT)), FadeIn(chs[i])))
        self.steps("First run, fresh server. Missing, so install. Old text, so write. Stopped, so start. Three tasks, three changed.", *plays)
        self.beat("Now the real question. We run the same playbook again, one minute later, nothing touched. How many tasks change? Pause and guess.",
                  Transform(runl, T("run 2", 28, YELLOW_M).move_to(runl)), FadeOut(chs), run_time=2.2)
        self.wait(2.0)
        okk = VGroup(*[T("ok", 24, GREEN_M).next_to(tasks[i], DOWN, buff=0.08).align_to(tasks[i], RIGHT) for i in range(3)])
        plays2 = []
        for i in range(3):
            a = Line(np.array([plist.get_right()[0] + 0.1, tasks[i].get_y(), 0]), np.array([srv.get_left()[0] - 0.1, st[i].get_y(), 0]))
            plays2.append((0.6, travel(a, GREEN_M, 0.5)))
            plays2.append((0.4, FadeIn(okk[i]), Indicate(st[i], color=GREEN_M, scale_factor=1.04)))
        self.steps("Zero. Each module looks, finds the server already right, and reports ok.", *plays2)
        self.play(FadeOut(VGroup(srv, sl, st, okk, runl)), run_time=0.6)

        # the real recap lines from the lab
        r1 = VGroup(T("first run", 24, GREY_B), M("lb1  : ok=9  changed=7", 24, YELLOW_M), M("web1 : ok=3  changed=2", 24, YELLOW_M), M("web2 : ok=3  changed=2", 24, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        r2 = VGroup(T("second run", 24, GREY_B), M("lb1  : ok=8  changed=0", 24, GREEN_M), M("web1 : ok=3  changed=0", 24, GREEN_M), M("web2 : ok=3  changed=0", 24, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        recs = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([3.4, -0.1, 0])
        self.beat("Here's the lab's real first playbook on its three practice servers. The first run changes things everywhere.",
                  FadeIn(r1, shift=UP * 0.1), run_time=2.0)
        self.beat("The second run reports changed equals zero on every server. It took about ten seconds, and touched nothing.",
                  FadeIn(r2, shift=UP * 0.1), run_time=2.0)
        idem = T("idempotent: safe to repeat", 30, GREEN_M).move_to([0, 3.0, 0])
        self.beat("This property has a name: idempotence. An idempotent task is safe to repeat. Running it again, when nothing needs to change, changes nothing.",
                  FadeIn(idem, shift=DOWN * 0.15), run_time=2.4)
        self.wait(0.4)
        self.play(FadeOut(VGroup(recs, idem)), run_time=0.6)

        # ---------- 6. drift: the door blown open
        motd = VGroup(T("/etc/motd on web2", 24, GREY_B),
                      M("web2 is managed by Ansible.", 22), M("Manual changes will be overwritten.", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        mp = panel(motd, TEAL_M).move_to([3.2, 0.3, 0])
        self.beat("Remember the door the wind blew open? On servers, it's a person. Someone logs in to web2 and adds a line to its login message by hand.",
                  FadeIn(mp), Indicate(tasks[1], color=TEAL_M, scale_factor=1.04), run_time=2.6)
        hand = M("edited by hand", 22, RED_M).next_to(motd, DOWN, aligned_edge=LEFT, buff=0.14)
        mp2 = panel(VGroup(motd.copy(), hand.copy()).arrange(DOWN, aligned_edge=LEFT, buff=0.14), TEAL_M).move_to(mp)
        self.play(Transform(mp[0], mp2[0]), motd.animate.move_to(mp2[1][0]), FadeIn(hand.move_to(mp2[1][1])), run_time=0.9)
        drift = T("drift: the server no longer matches the code", 26, RED_M).next_to(mp, DOWN, buff=0.4)
        self.beat("Now the server and the code disagree. That gap is called drift.", FadeIn(drift, shift=UP * 0.1), run_time=1.6)
        chg = T("changed: [web2]", 24, YELLOW_M).next_to(plist, DOWN, buff=0.35)
        self.beat("The next run looks, finds the extra line, and puts the file back. One task reports changed, exactly like the back door.",
                  Succession(Wait(1.4), AnimationGroup(FadeOut(hand, shift=RIGHT * 0.4), FadeIn(chg))), run_time=3.2)
        self.wait(0.4)
        self.play(FadeOut(VGroup(mp, motd, drift, chg)), run_time=0.6)

        # ---------- 7. break it: a chore hiding inside a playbook
        bad = M("shell: echo 'vm.swappiness=10' >> /etc/sysctl.conf", 22, RED_M).move_to([0, 2.65, 0])
        self.beat("So far so good. Now a trap. Ansible also has a shell module, which runs any command line you give it. Here's a task someone adds to a nightly playbook.",
                  FadeOut(VGroup(plist, plt, tasks)), Succession(Wait(2.2), FadeIn(bad, shift=DOWN * 0.15)), run_time=4.4)
        self.beat("It appends one line to a settings file. Ansible is idempotent, we just saw it. So after a week of nightly runs, how many copies of that line are in the file? Pause and guess.",
                  Indicate(bad, color=RED_M, scale_factor=1.03), run_time=2.4)
        self.wait(2.0)
        fbox = RoundedRectangle(corner_radius=0.12, width=6.4, height=4.0, stroke_color=GREY_B, stroke_width=2.5).set_fill(tint(GREY_B, 0.06), 1).move_to([0.6, -0.65, 0])
        fl = T("/etc/sysctl.conf", 24, GREY_B).next_to(fbox, LEFT, buff=0.3).align_to(fbox, UP)
        cnt = T("night 0", 26, YELLOW_M).next_to(fbox, LEFT, buff=0.3).shift(DOWN * 0.8)
        self.add(fbox, fl, cnt)
        lines = VGroup()
        for i in range(7):
            ln = M("vm.swappiness=10", 22, RED_M if i else WHITE).move_to([0.6, 0.95 - 0.45 * i, 0])
            lines.add(ln)
        self.steps("Well... seven. One for every night.",
                   *[(0.32, FadeIn(lines[i], shift=DOWN * 0.1), Transform(cnt, T(f"night {i + 1}", 26, YELLOW_M).move_to(cnt))) for i in range(7)])
        self.beat("The shell module can't look first. It has no idea what your command means, so it just runs it, every time, and reports changed every time. That's a chore, hiding in a list of results.",
                  Indicate(bad, color=RED_M, scale_factor=1.03), run_time=2.4)
        self.beat("Ansible's tasks are idempotent only when the module is. The tool can't make a chore safe for you.", Wait(0.1), run_time=0.4)
        good = M("lineinfile: line='vm.swappiness=10'", 22, GREEN_M).move_to(bad)
        self.beat("The fix is a module that knows the result: lineinfile, with the line you want. It checks whether the line is there, and adds it once.",
                  Transform(bad, good), Succession(Wait(1.8), AnimationGroup(FadeOut(lines[1:]), lines[0].animate.set_color(GREEN_M), Transform(cnt, T("night 7", 26, GREEN_M).move_to(cnt)))), run_time=4.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(bad, fbox, fl, cnt, lines[0])), run_time=0.6)

        # ---------- 8. guardrails
        g = VGroup(
            VGroup(M("command", 26, GOLD_M), T("and", 26, GREY_B), M("shell", 26, GOLD_M), T("report changed on every run", 26)).arrange(RIGHT, buff=0.2),
            VGroup(T("look for a real module first:", 26), M("ansible-doc -l | grep apt", 24, TEAL_M)).arrange(RIGHT, buff=0.25),
            VGroup(T("no state file: delete a task, and jq stays installed", 26)),
            VGroup(T("to remove something, say so:", 26), M("state=absent", 24, TEAL_M)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, -0.1, 0])
        gt = T("a few guardrails", 30, YELLOW_M).next_to(g, UP, buff=0.5)
        self.beat("A few guardrails. Command and shell always say changed. So look for a real module first. ansible-doc minus l lists every module you have, and grep finds the one you need.",
                  FadeIn(gt), FadeIn(g[0], shift=RIGHT * 0.1), Succession(Wait(2.6), FadeIn(g[1], shift=RIGHT * 0.1)), run_time=4.6)
        self.beat("And here's where our house sitter story stops working. A good sitter would notice a broken window that no line on the list mentions. Ansible never does.",
                  Wait(0.1), run_time=0.4)
        self.beat("It keeps no state file and no memory of past runs. Delete the jq task from the playbook, and jq stays installed. To remove something, you write a task that says so, such as state absent.",
                  FadeIn(g[2], shift=RIGHT * 0.1), Succession(Wait(3.6), FadeIn(g[3], shift=RIGHT * 0.1)), run_time=5.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(g, gt)), run_time=0.6)

        # ---------- 9. moral, recap, quick check
        m1 = T("A chore repeated does harm.", 34, RED_M)
        m2 = T("A result checked twice does none.", 34, GREEN_M)
        m3 = T("Write tasks as results.", 34, YELLOW_M)
        moral = VGroup(m1, m2, m3).arrange(DOWN, buff=0.3).move_to([0, 1.3, 0])
        self.beat("So the moral of the story. A chore repeated does harm, and a result checked twice does none. Write tasks as results.",
                  LaggedStart(*[FadeIn(m, shift=UP * 0.12) for m in moral], lag_ratio=0.8), run_time=4.4)
        rc = T("look first, act only where it differs, report ok or changed", 28, GREY_B).move_to([0, -1.0, 0])
        self.beat("Every good module does the same three things. It looks first. It acts only where the server differs. And it tells you which: ok, or changed.",
                  FadeIn(rc, shift=UP * 0.1), run_time=2.4)
        self.wait(0.4)
        self.play(FadeOut(VGroup(moral, rc)), run_time=0.6)
        qq = T("Quick check", 30, YELLOW_M).move_to([0, 2.2, 0])
        qc = M("shell: apt-get install -y nginx", 26, GOLD_M).move_to([0, 1.0, 0])
        qt = T("nginx is already installed. What does this task report?", 30).move_to([0, 0.0, 0])
        self.beat("A quick check. This task runs on a server where nginx is already installed. Does it report ok, or changed? Pause and think.",
                  FadeIn(qq), FadeIn(qc), FadeIn(qt), run_time=2.4)
        self.wait(2.0)
        ans = T("changed, on every run: shell cannot look first", 30, GREEN_M).move_to([0, -1.2, 0])
        self.beat("Changed. Every single run. The shell module can't look first, so it never knows the job was already done.",
                  FadeIn(ans, shift=UP * 0.15), run_time=2.0)
        self.wait(1.0)
