import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

NX = 4.0                      # x of the managed nodes
NY = [2.2, 0.3, -1.6]         # y of web1, web2, lb1
NAMES = ["web1", "web2", "lb1"]
PORTS = ["2201", "2202", "2203"]
TX = -6.55                    # left edge of text inside the control-node panel
LX0, LX1 = -0.95, 2.35        # the SSH lines run between these x values
SLOT = [1.95 - 0.44 * i for i in range(11)]   # terminal rows in the panel


def dark(c, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def top(m, z=2):
    """Draw m above boxes and lines, whatever order things were added in."""
    m.set_z_index(z)
    return m


def stroke_to(m, c):
    return Transform(m, m.copy().set_stroke(c))


def recolor(m, c):
    return Transform(m, m.copy().set_color(c))


def jchip(text, color):
    """A JSON result chip with a solid fill, so the SSH line does not show through it."""
    t = M(text, 20)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.3, height=0.56, stroke_color=color, stroke_width=2.5)
    r.set_fill(dark(color, 0.22), opacity=1)
    return top(VGroup(r, t.move_to(r)), 3)


_CW = {}


def cw(size):
    """Width of one monospace character at this size (measured once)."""
    if size not in _CW:
        _CW[size] = M("x" * 40, size).width / 40
    return _CW[size]


def cl(text, y, size=20, color=WHITE, x=TX):
    """One line of code or terminal output, left edge at x, on a shared baseline (an H sets it, then goes)."""
    m = M("H" + text, size, color)
    h = m[0]
    m.shift(np.array([x - cw(size) - h.get_left()[0], y - h.get_center()[1], 0]))
    m.remove(h)
    return top(m)


def part(line, full, piece):
    """The glyphs of `piece` inside a line made by cl() from the text `full`."""
    s, p = full.replace(" ", ""), piece.replace(" ", "")
    i = s.index(p)
    return line[i:i + len(p)]


def node_box(name, port, y):
    r = RoundedRectangle(corner_radius=0.14, width=3.2, height=1.55, stroke_color=TEAL_M, stroke_width=3)
    r.set_fill(dark(TEAL_M), opacity=1).move_to([NX, y, 0])
    head = VGroup(T(name, 28), M(":" + port, 20, GREY_B)).arrange(RIGHT, buff=0.22)
    head.move_to([NX, y + 0.4, 0])
    return VGroup(r, top(head))


def state_row(label, y, ok):
    t = cl(label, y, 20, WHITE, NX - 1.3)
    return t, top(tick(ok, 0.14).move_to([NX + 1.15, y, 0]))


class D36Idempotence(VoiceScene):
    def construct(self):
        self.title_card("How Ansible changes a server", "check first, change only what differs")

        # 1. the control node: small at first, it grows when the work starts
        panel = RoundedRectangle(corner_radius=0.15, width=5.85, height=1.7, stroke_color=GOLD_M, stroke_width=3)
        panel.set_fill(dark(GOLD_M, 0.07), opacity=1).move_to([-3.925, 2.2, 0])
        big = RoundedRectangle(corner_radius=0.15, width=5.85, height=6.3, stroke_color=GOLD_M, stroke_width=3)
        big.set_fill(dark(GOLD_M, 0.07), opacity=1).move_to([-3.925, -0.1, 0])
        plab = T("control node", 26, GOLD_M).move_to([-3.925, 3.37, 0])
        mac = top(T("your Mac", 32).move_to(panel))
        self.beat("Ansible runs on one machine, called the control node. In this course, that is your Mac.",
                  Create(panel), Write(plab), FadeIn(mac), run_time=1.6)

        # 2. the inventory
        inv_txt = ["[web]", "web1 ansible_host=127.0.0.1 ansible_port=2201", "web2 ansible_host=127.0.0.1 ansible_port=2202",
                   "[lb]", "lb1 ansible_host=127.0.0.1 ansible_port=2203"]
        ix = -0.65
        inv_head = cl("inventory.ini", 0.75, 22, GREY_B, ix)
        inv = VGroup(*[cl(s, 0.1 - 0.52 * i, 22, BLUE_M if s.startswith("[") else WHITE, ix) for i, s in enumerate(inv_txt)])
        self.beat("First, it reads the inventory. This file lists your servers, sorts them into groups, and says how to reach each one.",
                  FadeIn(inv_head), LaggedStart(*[FadeIn(l, shift=0.1 * RIGHT) for l in inv], lag_ratio=0.15), run_time=2.2)
        hosts = [inv[1], inv[2], inv[4]]
        self.beat("The lab has three practice servers: web1 and web2 in the web group, and lb1 in the lb group. They share one address, and differ only by SSH port.",
                  Succession(AnimationGroup(Indicate(inv[0], color=BLUE_M), *[recolor(part(h, s, n), TEAL_M) for h, s, n in zip(hosts[:2], [inv_txt[1], inv_txt[2]], NAMES[:2])]),
                             AnimationGroup(Indicate(inv[3], color=BLUE_M), recolor(part(hosts[2], inv_txt[4], "lb1"), TEAL_M)),
                             Wait(0.8),
                             AnimationGroup(*[recolor(part(h, s, p), YELLOW_M) for h, s, p in zip(hosts, [inv_txt[1], inv_txt[2], inv_txt[4]], PORTS)])), run_time=7.5)

        # 3. the managed nodes come out of the inventory
        nodes = [node_box(n, p, y) for n, p, y in zip(NAMES, PORTS, NY)]
        mlab = T("managed nodes", 26, TEAL_M).move_to([NX, 3.37, 0])
        invchip = top(chip("inventory.ini", GREY_B, 20, mono=True))
        invchip.move_to([0, 2.5, 0]).align_to(np.array([TX, 0, 0]), LEFT)
        mac2 = top(T("your Mac", 26, GREY_B).move_to([0, 2.5, 0]).align_to(np.array([-1.3, 0, 0]), RIGHT))
        grow = []
        for nd, h, s, n, p in zip(nodes, hosts, [inv_txt[1], inv_txt[2], inv_txt[4]], NAMES, PORTS):
            grow.append(AnimationGroup(Create(nd[0]), TransformFromCopy(part(h, s, n), nd[1][0]),
                                       TransformFromCopy(part(h, s, p), nd[1][1])))
        self.beat("Each host becomes a managed node: a server that Ansible configures.",
                  Succession(AnimationGroup(LaggedStart(*grow, lag_ratio=0.2), FadeIn(mlab)),
                             AnimationGroup(FadeTransform(VGroup(inv_head, inv), invchip), Transform(mac, mac2))), run_time=3.0)

        # 4. SSH, agentless, ping
        lines = VGroup(*[Line([LX0, y, 0], [LX1, y, 0], stroke_width=3, color=GREY_B) for y in NY])
        sshl = VGroup(*[top(T("SSH", 20, GREY_B)).move_to([(LX0 + LX1) / 2, y + 0.25, 0]) for y in NY])
        self.beat("To work on them, Ansible logs in to each one over SSH.",
                  Succession(Transform(panel, big), AnimationGroup(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.2), FadeIn(sshl))), run_time=2.4)
        needs = VGroup(*[top(VGroup(chip("SSH", TEAL_M, 20), chip("python3", TEAL_M, 20, mono=True))).arrange(RIGHT, buff=0.2).move_to([NX, y - 0.28, 0]) for y in NY])
        agl = T("agentless", 28, TEAL_M).move_to([NX, -2.9, 0])
        self.beat("Nothing of Ansible is installed on these servers, and no Ansible process waits there. That is what agentless means. A server needs only two things: an SSH login, and Python 3.",
                  Succession(Write(agl), Wait(0.6), LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in needs], lag_ratio=0.2)), run_time=5.5)

        def packets(label, idx=(0, 1, 2), color=GOLD_M):
            ps = [top(mbox(label, color, w=1.1, h=0.5, size=20), 3).move_to([LX0 + 0.6, NY[i], 0]) for i in idx]
            return ps, AnimationGroup(*[Succession(FadeIn(p, run_time=0.2), p.animate(run_time=1.2, rate_func=smooth).move_to([LX1 - 0.6, p.get_y(), 0]),
                                                   FadeOut(p, run_time=0.3, scale=0.5)) for p in ps])

        ping = cl("$ ansible all -m ansible.builtin.ping", SLOT[0], 20, WHITE)
        _, go = packets("ping")
        pj = [jchip('"ping": "pong"', GREEN_M).move_to([(LX0 + LX1) / 2, y, 0]) for y in NY]
        pout = [cl(f"{n} | SUCCESS", s, 20, GREEN_M) for n, s in zip(NAMES, SLOT[1:4])]
        self.beat("The ping module checks both. It logs in to every server, and each one answers pong when SSH and Python work.",
                  Succession(Write(ping), go, LaggedStart(*[FadeIn(j, shift=LEFT * 0.3) for j in pj], lag_ratio=0.15),
                             LaggedStart(*[ReplacementTransform(j, o) for j, o in zip(pj, pout)], lag_ratio=0.15)), run_time=6.0)

        # 5. a task describes a result
        divider = DashedLine([TX, -0.22, 0], [-1.3, -0.22, 0], dash_length=0.08, stroke_width=1.5, color=GREY_D)

        def yblock(spec):
            return VGroup(*[cl(s, -0.6 - 0.4 * i, 20, c, TX + ind * cw(20)) for i, (s, c, ind) in enumerate(spec)])

        y_apt = [("first-playbook.yml", GREY_B, 0), ("- name: Install a few everyday tools", WHITE, 0), ("ansible.builtin.apt:", GOLD_M, 2),
                 ("name:", WHITE, 4), ("- tree", WHITE, 6), ("- htop", WHITE, 6), ("state: present", YELLOW_M, 4)]
        y_copy = [("first-playbook.yml", GREY_B, 0), ("- name: Write a login message", WHITE, 0), ("ansible.builtin.copy:", GOLD_M, 2),
                  ("dest: /etc/motd", YELLOW_M, 4), ("owner: root", WHITE, 4), ('mode: "0644"', WHITE, 4)]
        yaml = yblock(y_apt)
        cur = {"y": yaml}

        def show_yaml(spec):
            new = yblock(spec)
            a = AnimationGroup(FadeOut(cur["y"]), FadeIn(new))
            cur["y"] = new
            return a

        self.play(FadeOut(needs), FadeOut(sshl), FadeOut(agl), FadeOut(VGroup(ping, *pout), shift=0.2 * UP), run_time=0.6)
        self.beat("Your playbook lists tasks. Each task calls one module, and describes the result you want.",
                  Create(divider), LaggedStart(*[FadeIn(l, shift=0.1 * RIGHT) for l in yaml], lag_ratio=0.12), run_time=2.2)
        self.beat("Here, the apt module, and the result: tree and htop must be present.",
                  Succession(Indicate(yaml[2], color=GOLD_M), Indicate(VGroup(yaml[4], yaml[5], yaml[6]), color=YELLOW_M)), run_time=2.4)

        rows = []
        for y in NY:
            a, am = state_row("tree, htop", y - 0.05, False)
            b, bm = state_row("/etc/motd", y - 0.45, False)
            rows.append([a, am, b, bm])
        self.beat("These are fresh servers. tree and htop are missing, and the login message is not written yet.",
                  LaggedStart(*[AnimationGroup(FadeIn(r[0]), Create(r[1]), FadeIn(r[2]), Create(r[3])) for r in rows], lag_ratio=0.2), run_time=2.4)

        # 6. first run, task 1
        cmd = cl("$ ansible-playbook first-playbook.yml", SLOT[0], 20, WHITE)
        t1 = cl("TASK [Install a few everyday tools]", SLOT[1], 20, GREY_B)
        self.beat("Run the playbook. Ansible takes the first task, and does the same steps on every server.",
                  Write(cmd), FadeIn(t1), run_time=2.0)

        _, go = packets("apt")
        self.beat("It copies a small Python program, the module, to each server. By default it works on five servers at a time, so all three go at once.",
                  go, run_time=2.4)
        self.beat("The server's python3 runs the module. And the module checks the server first. Are tree and htop installed?",
                  LaggedStart(*[Circumscribe(VGroup(r[0], r[1]), color=YELLOW_M, buff=0.08) for r in rows], lag_ratio=0.1), run_time=2.2)
        oks = [top(tick(True, 0.14).move_to(r[1])) for r in rows]
        self.beat("They are not. So it installs them.",
                  *[AnimationGroup(FadeOut(r[1], scale=0.5), GrowFromCenter(o)) for r, o in zip(rows, oks)],
                  *[stroke_to(nd[0], YELLOW_M) for nd in nodes], run_time=1.2)
        for r, o in zip(rows, oks):
            r[1] = o

        def results(changed, slots, idx=(0, 1, 2), stroke=True):
            col = YELLOW_M if changed else GREEN_M
            js = [jchip('"changed": ' + ("true" if changed else "false"), col).move_to([(LX0 + LX1) / 2, NY[i], 0]) for i in idx]
            outs = [cl(("changed" if changed else "ok") + f": [{NAMES[i]}]", s, 20, col) for i, s in zip(idx, slots)]
            show = LaggedStart(*[FadeIn(j, shift=LEFT * 0.3) for j in js], lag_ratio=0.15)
            move = LaggedStart(*[ReplacementTransform(j, o) for j, o in zip(js, outs)], lag_ratio=0.15)
            back = [stroke_to(nodes[i][0], TEAL_M) for i in idx] if stroke else []
            return outs, show, move, back

        out1, show, move, back = results(True, SLOT[2:5])
        self.beat("Then the module prints a small JSON result with a changed field, and Ansible reads it back. Here, changed, in yellow.",
                  Succession(show, Wait(0.5), AnimationGroup(move, *back)), run_time=3.6)

        # 7. first run, task 2
        t2 = cl("TASK [Write a login message]", SLOT[1], 20, GREY_B)
        _, go = packets("copy")
        bt = [top(tick(True, 0.14).move_to(r[3])) for r in rows]
        out2, show, move, back = results(True, SLOT[2:5])
        self.beat("The next task writes the login message. The copy module checks the file, finds it is not right, writes it, and reports changed.",
                  Succession(AnimationGroup(FadeOut(VGroup(t1, *out1), shift=0.2 * UP), FadeIn(t2), show_yaml(y_copy)), go,
                             LaggedStart(*[Circumscribe(VGroup(r[2], r[3]), color=YELLOW_M, buff=0.08) for r in rows], lag_ratio=0.1),
                             AnimationGroup(*[AnimationGroup(FadeOut(r[3], scale=0.5), GrowFromCenter(b)) for r, b in zip(rows, bt)],
                                            *[stroke_to(nd[0], YELLOW_M) for nd in nodes]),
                             show, AnimationGroup(move, *back)), run_time=7.5)
        for r, b in zip(rows, bt):
            r[3] = b

        # 8. the recap of run 1
        rec_txt = ["lb1  : ok=9  changed=7", "web1 : ok=3  changed=2", "web2 : ok=3  changed=2"]
        rhead = cl("PLAY RECAP", SLOT[1], 22, WHITE)
        rec = VGroup(*[cl(s, SLOT[2] - 0.5 * i, 22) for i, s in enumerate(rec_txt)])
        self.beat("At the end comes the PLAY RECAP, one line per server.",
                  FadeOut(VGroup(t2, *out2), shift=0.2 * UP), Write(rhead), LaggedStart(*[FadeIn(l, shift=0.1 * RIGHT) for l in rec], lag_ratio=0.2), run_time=2.0)
        okp = [part(l, s, s.split(":")[1].split()[0]) for l, s in zip(rec, rec_txt)]
        chp = [part(l, s, s.split()[-1]) for l, s in zip(rec, rec_txt)]
        self.beat("ok counts every task that succeeded, changed or not. changed counts the tasks that changed something.",
                  Succession(AnimationGroup(*[recolor(p, GREEN_M) for p in okp]), Wait(1.2),
                             AnimationGroup(*[recolor(p, YELLOW_M) for p in chp])), run_time=4.0)
        self.beat("web1 has three ok: our two tasks, plus gathering facts, which starts every play. lb1 also ran a second play that sets up nginx, so its numbers are bigger.",
                  Succession(Indicate(rec[1], color=TEAL_M, scale_factor=1.05), Wait(1.5), Indicate(rec[0], color=TEAL_M, scale_factor=1.05)), run_time=6.0)

        # 9. second run: everything is already right
        t1b = cl("TASK [Install a few everyday tools]", SLOT[1], 20, GREY_B)
        _, go = packets("apt")
        self.beat("Now run the same playbook again, without changing anything.",
                  FadeOut(VGroup(rhead, rec), shift=0.2 * UP), Indicate(cmd, color=WHITE, scale_factor=1.04), FadeIn(t1b), show_yaml(y_apt), go, run_time=2.6)
        o1, show, move, back = results(False, SLOT[2:5], stroke=False)
        self.beat("The module checks first. tree and htop are already installed. So it does nothing, and reports ok.",
                  Succession(LaggedStart(*[Circumscribe(VGroup(r[0], r[1]), color=GREEN_M, buff=0.08) for r in rows], lag_ratio=0.1),
                             AnimationGroup(*[stroke_to(nd[0], GREEN_M) for nd in nodes]), show, move), run_time=5.0)
        t2b = cl("TASK [Write a login message]", SLOT[1], 20, GREY_B)
        _, go = packets("copy")
        o2, show, move, back = results(False, SLOT[2:5], stroke=False)
        self.beat("The same for the login message. The file already says the right thing, so: ok.",
                  Succession(AnimationGroup(FadeOut(VGroup(t1b, *o1), shift=0.2 * UP), FadeIn(t2b), show_yaml(y_copy)), go,
                             LaggedStart(*[Circumscribe(VGroup(r[2], r[3]), color=GREEN_M, buff=0.08) for r in rows], lag_ratio=0.1),
                             show, move), run_time=5.0)

        rec2_txt = ["lb1  : ok=8  changed=0", "web1 : ok=3  changed=0", "web2 : ok=3  changed=0"]
        rhead2 = cl("PLAY RECAP", SLOT[1], 22, WHITE)
        rec2 = VGroup(*[cl(s, SLOT[2] - 0.5 * i, 22) for i, s in enumerate(rec2_txt)])
        for l, s in zip(rec2, rec2_txt):
            part(l, s, s.split()[-1]).set_color(GREEN_M)
            part(l, s, s.split(":")[1].split()[0]).set_color(GREEN_M)
        self.beat("The recap says changed equals zero, on every server.",
                  FadeOut(VGroup(t2b, *o2), shift=0.2 * UP), Write(rhead2), LaggedStart(*[FadeIn(l, shift=0.1 * RIGHT) for l in rec2], lag_ratio=0.2),
                  *[stroke_to(nd[0], TEAL_M) for nd in nodes], run_time=2.2)
        self.beat("lb1 shows eight ok instead of nine, because its nginx reload runs only after a change. This time, nothing called it.",
                  Indicate(part(rec2[0], rec2_txt[0], "ok=8"), color=YELLOW_M, scale_factor=1.3), run_time=1.6)

        idem = T("idempotent: safe to repeat", 30, GREEN_M).move_to([2.95, -3.05, 0])
        self.beat("This run took about ten seconds, and changed nothing. That property is called idempotence. It is the main thing Ansible gives you over a shell script.",
                  Write(idem), run_time=2.0)

        # 10. shell and command cannot tell
        sh = cl("shell: apt-get install -y nginx", -0.75, 20, WHITE)
        stamps = VGroup(*[chip("changed", YELLOW_M, 20) for _ in range(3)]).arrange(RIGHT, buff=0.2)
        stamps.move_to([0, -1.45, 0]).align_to(np.array([TX, 0, 0]), LEFT)
        every = T("every run", 22, YELLOW_M).next_to(stamps, DOWN, buff=0.25).align_to(stamps, LEFT)
        self.beat("The shell and command modules cannot know what a command did. So they report changed every time. Treat them as a last resort.",
                  Succession(AnimationGroup(FadeOut(cur["y"]), FadeIn(sh)), LaggedStart(*[FadeIn(s, shift=0.1 * DOWN) for s in stamps], lag_ratio=0.4), FadeIn(every)), run_time=5.0)

        # 11. drift on web2
        hand = jchip("edited by hand", RED_M).move_to([(LX0 + LX1) / 2, 0.95, 0])
        bad = top(tick(False, 0.14).move_to(rows[1][3]))
        self.beat("Now someone fixes web2 by hand, and adds a line to its login message.",
                  FadeOut(VGroup(sh, stamps, every, idem, rhead2, rec2)), FadeIn(hand, shift=DOWN * 0.15), FadeIn(yblock(y_copy)),
                  FadeOut(rows[1][3], scale=0.5), GrowFromCenter(bad), stroke_to(nodes[1][0], RED_M), run_time=2.0)
        rows[1][3] = bad
        c2 = cl("--diff --limit web2", SLOT[1], 20, WHITE, TX + 2 * cw(20))
        _, go = packets("copy", idx=(1,))
        self.beat("Ansible keeps no state file. Every run checks the real server, so the next run finds the difference.",
                  Succession(AnimationGroup(Indicate(cmd, color=WHITE, scale_factor=1.04), FadeIn(c2)), go,
                             Circumscribe(VGroup(rows[1][2], rows[1][3]), color=RED_M, buff=0.08)), run_time=4.5)
        d1 = cl("TASK [Write a login message]", SLOT[2], 20, GREY_B)
        d2 = cl("-edited by hand", SLOT[3], 20, RED_M)
        d3 = cl("changed: [web2]", SLOT[4], 20, YELLOW_M)
        good = top(tick(True, 0.14).move_to(rows[1][3]))
        self.beat("It puts the file back, and shows exactly the line it removed.",
                  Succession(FadeIn(d1), AnimationGroup(FadeIn(d2), FadeOut(hand, shift=UP * 0.2)),
                             AnimationGroup(FadeOut(rows[1][3], scale=0.5), GrowFromCenter(good), stroke_to(nodes[1][0], TEAL_M), FadeIn(d3))), run_time=3.2)
        drift = T("drift: found and undone", 30, GREEN_M).move_to([2.95, -3.05, 0])
        self.beat("A difference between the code and the server is called drift. A regular Ansible run finds it, and undoes it.",
                  Write(drift), run_time=1.8)

        # 12. recap
        everything = Group(*self.mobjects)
        self.play(FadeOut(everything), run_time=0.8)
        r1 = T("check first, change only what differs", 40, YELLOW_M).move_to(UP * 0.6)
        r2 = VGroup(chip("ok: already right", GREEN_M, 26), chip("changed: fixed it", YELLOW_M, 26)).arrange(RIGHT, buff=0.6).next_to(r1, DOWN, buff=0.6)
        self.beat("So each module checks first, and changes only what differs. That is why a second run is safe, and changes nothing.",
                  Write(r1), LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in r2], lag_ratio=0.4), run_time=3.0)
        self.wait(1.0)
