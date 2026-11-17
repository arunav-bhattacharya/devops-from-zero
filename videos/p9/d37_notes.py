import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bgroup_vars/web\b", "group vars web"), (r"\bgroup_vars/all\b", "group vars all"), (r"\bgroup_vars\b", "group vars"),
            (r"\bhost_vars/web2\b", "host vars web two"), (r"\bhost_vars\b", "host vars"),
            (r"\bhello_devops_greeting\b", "hello devops greeting"), (r"\bweb1\b", "web one"), (r"\bweb2\b", "web two"),
            (r"\bvars:", "vars"), (r"(?<![\w])-e\b", "dash E"), (r"\bdefaults/", "defaults folder"), (r"\bvars/", "vars folder")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def house(color=GREY_B):
    body = Rectangle(width=2.0, height=1.3, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
    roof = Polygon(body.get_corner(UL) + LEFT * 0.2, body.get_corner(UR) + RIGHT * 0.2, body.get_top() + UP * 0.8,
                   stroke_color=color, stroke_width=3).set_fill(tint(color, 0.05), 1)
    door = Rectangle(width=0.5, height=0.8, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.12), 1).align_to(body, DOWN)
    return VGroup(body, roof, door)


def note(text, color, size=22, w=None):
    t = T(text, size, color)
    r = Rectangle(width=w or t.width + 0.35, height=t.height + 0.3, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.18), 1)
    return VGroup(r, t.move_to(r))


LEVELS = [("role defaults", GREEN_M), ("group_vars/all", TEAL_M), ("group_vars/web", TEAL_M), ("host_vars/web2", TEAL_M),
          ("vars: in the play", BLUE_M), ("role vars", PURPLE_M), ("-e on the command line", GOLD_M)]


class D37Notes(VoiceScene):
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
        self.title_card("Which note wins?", "Ansible variables set in many places, and the order that picks one")

        # ---------- 1. question
        q1 = M("hello_devops_greeting", 30, YELLOW_M).move_to([0, 1.0, 0])
        q2 = T("one name, set in four files. Which value does the server get?", 32).move_to([0, -0.1, 0])
        self.beat("Here's the question. You have one setting, the greeting our little web app shows. It's set in four different files. Which one does the server actually get?",
                  FadeIn(q1), Succession(Wait(2.4), FadeIn(q2, shift=UP * 0.15)), run_time=4.6)
        self.beat("You might guess the last one written, or the first one read. Let's go back to the street to find out.",
                  Wait(0.1), run_time=0.4)
        self.play(FadeOut(VGroup(q1, q2)), run_time=0.5)

        # ---------- 2. familiar: notes on the street
        hA = house().move_to([1.7, 0.3, 0])
        hB = house().move_to([4.9, 0.3, 0])
        side = DashedLine([0.2, -0.9, 0], [6.4, -0.9, 0], dash_length=0.12, color=GREY_D)
        self.beat("Our house sitter now looks after a whole street, and the owners start leaving notes.",
                  FadeIn(hA), FadeIn(hB), Create(side), run_time=2.0)
        chk = note("checklist: heating 20 degrees", GREEN_M, 24).move_to([-3.6, 2.4, 0])
        self.beat("The printed checklist says: heating at twenty degrees. That's the author's suggestion, for any house.",
                  FadeIn(chk, shift=DOWN * 0.15), run_time=2.0)
        sideN = note("left side of the street: 19", TEAL_M, 24).move_to([3.3, -1.5, 0])
        self.beat("Then a note for this side of the street: nineteen degrees.",
                  FadeIn(sideN, shift=UP * 0.15), run_time=1.6)
        door = note("22, please", TEAL_M, 22).next_to(hB[2], UP, buff=0.08)
        self.beat("And a sticky note on one front door: twenty-two, please.",
                  FadeIn(door, scale=0.7), run_time=1.6)
        phone = note("phone call tonight: 18, we're away", GOLD_M, 24).move_to([-3.6, -2.4, 0])
        self.beat("Then the owners phone tonight. Eighteen degrees everywhere, we're away.",
                  FadeIn(phone, shift=UP * 0.15), run_time=1.8)
        qm = T("which note wins?", 30, YELLOW_M).move_to([-3.6, 0.0, 0])
        self.beat("Four notes, and they disagree. A real sitter would ring somebody and ask. Ansible never asks. It picks a winner by a fixed list, silently.",
                  FadeIn(qm), run_time=2.8)
        self.wait(0.3)

        # ---------- 3. the ladder: map every note
        X0, Y0, DY = -4.6, -2.85, 0.86
        rungs = VGroup()
        for i, (name, c) in enumerate(LEVELS):
            r = RoundedRectangle(corner_radius=0.1, width=3.2, height=0.62, stroke_color=c, stroke_width=2.5).set_fill(tint(c, 0.12), 1)
            rungs.add(VGroup(r, M(name, 22, WHITE).move_to(r)).move_to([X0, Y0 + i * DY, 0]))
        up = Arrow([-6.45, Y0 - 0.3, 0], [-6.45, Y0 + 6 * DY + 0.3, 0], buff=0, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.05)
        weak = T("weak", 22, GREY_B).next_to(rungs[0], RIGHT, buff=0.25)
        strong = T("strong", 22, GOLD_M).next_to(rungs[6], RIGHT, buff=0.25)
        self.play(FadeOut(qm), run_time=0.4)
        self.steps("Here's that list, as a ladder. Weakest at the bottom, strongest at the top.",
                   (0.6, GrowArrow(up)), (0.6, FadeIn(weak), FadeIn(strong)))
        self.steps("The printed checklist is the role's defaults, the author's suggestions. So it sits at the very bottom.",
                   (1.0, ReplacementTransform(chk, rungs[0])))
        self.steps("The note for one side of the street is a group's file in group_vars. One file for all hosts, one per group.",
                   (1.0, ReplacementTransform(sideN, rungs[2]), FadeIn(rungs[1])))
        self.steps("The sticky note on one door is host_vars, a file for one host. One host is more specific than its group, so it sits higher.",
                   (1.0, ReplacementTransform(door, rungs[3])))
        self.steps("Values written in the playbook itself beat everything in the inventory.",
                   (0.8, FadeIn(rungs[4], shift=UP * 0.1)))
        self.steps("And the phone call tonight is minus e, extra vars typed on the command line. They always win.",
                   (1.0, ReplacementTransform(phone, rungs[6])))
        self.beat("I've left one gap on purpose. Hold that thought, we'll come back to it.",
                  Wait(0.1), run_time=0.4)
        gapb = DashedVMobject(RoundedRectangle(corner_radius=0.1, width=3.2, height=0.62, stroke_color=GREY_D, stroke_width=2).move_to(rungs[5]), num_dashes=30)
        self.add(gapb)

        # ---------- 4. shrink, predict, show: the lab's real files
        w1 = house().scale(0.8).move_to([3.2, 1.6, 0])
        w2 = house().scale(0.8).move_to([5.3, 1.6, 0])
        self.play(ReplacementTransform(hA, w1), ReplacementTransform(hB, w2), FadeOut(side), run_time=0.8)
        n1 = M("web1", 26, BLUE_M).next_to(w1, DOWN, buff=0.15)
        n2 = M("web2", 26, BLUE_M).next_to(w2, DOWN, buff=0.15)
        self.beat("Now the real thing. The lab's two web servers, web1 and web2, and one variable, hello_devops_greeting.",
                  FadeIn(n1), FadeIn(n2), run_time=2.0)

        def rv(i, text, color):
            return T(text, 22, color).next_to(rungs[i], RIGHT, buff=0.3)
        self.play(FadeOut(weak), FadeOut(strong), run_time=0.3)
        d0 = rv(0, '"Hello, DevOps!"', GREEN_M)
        d2 = rv(2, '"Hello from Ansible"', TEAL_M)
        d3 = rv(3, '"Hello from web2, the canary"', TEAL_M)
        self.beat("The role's default says: Hello, DevOps!", FadeIn(d0, shift=RIGHT * 0.1), run_time=1.4)
        self.beat("The web group's file says: Hello from Ansible.", FadeIn(d2, shift=RIGHT * 0.1), run_time=1.4)
        self.beat("And web2's own file says: Hello from web2, the canary. A canary is the one server that gets a change first, so a problem shows up on one machine, not all of them.",
                  FadeIn(d3, shift=RIGHT * 0.1), run_time=2.0)
        cmd = VGroup(M("ansible web -m ansible.builtin.debug", 22, GREY_B), M("-a var=hello_devops_greeting", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.5, -2.5, 0])
        self.beat("The debug module asks each host what it sees. Before we run it: what does web1 get, and what does web2 get? Pause and guess.",
                  FadeIn(cmd, shift=UP * 0.1), run_time=2.4)
        self.wait(2.0)
        def two(a, b, color, x):
            g = VGroup(T(a, 24, color), T(b, 24, color)) if b else VGroup(T(a, 24, color))
            return g.arrange(DOWN, buff=0.12).move_to([x, -0.2, 0])
        X1, X2 = 3.2, 5.3
        a1 = two("Hello from", "Ansible", TEAL_M, X1)
        a2 = two("Hello from web2,", "the canary", TEAL_M, X2)
        self.beat("web1 isn't in host_vars, so its strongest note is the group's: Hello from Ansible.",
                  TransformFromCopy(d2, a1), run_time=1.6)
        self.beat("web2 has its own note, one rung higher, so it gets the canary text. And the role default? Beaten by both. It's a suggestion, after all.",
                  TransformFromCopy(d3, a2), Succession(Wait(3.0), Indicate(d0, color=GREEN_M, scale_factor=1.05)), run_time=4.2)
        e1 = rv(6, '"Hi from -e"', GOLD_M)
        self.beat("Now add a phone call. Run the same command with minus e, Hi from minus e.",
                  FadeIn(e1, shift=RIGHT * 0.1), run_time=1.8)
        b1 = two("Hi from -e", "", GOLD_M, X1)
        b2 = two("Hi from -e", "", GOLD_M, X2)
        self.beat("Both hosts print Hi from minus e. The canary's sticky note is still on the door. Tonight, the phone call simply wins.",
                  Transform(a1, b1), Transform(a2, b2), run_time=1.6)
        self.wait(0.3)
        self.play(FadeOut(e1), Transform(a1, two("Hello from", "Ansible", TEAL_M, X1)), Transform(a2, two("Hello from web2,", "the canary", TEAL_M, X2)), run_time=0.6)
        nm = T("variable precedence", 30, YELLOW_M).move_to([4.25, 3.1, 0])
        self.beat("This ladder has a name: variable precedence, the rule that decides which value wins when one variable is set in several places. The docs list twenty-two levels. In practice, you need these seven.",
                  FadeIn(nm, shift=DOWN * 0.1), run_time=2.6)
        self.play(FadeOut(nm), FadeOut(cmd), run_time=0.4)

        # ---------- 5. break the "most specific wins" model: role vars
        self.beat("So far, a tidy story: the more specific the note, the stronger it is. Now back to the gap I left.",
                  Indicate(gapb, color=PURPLE_M, scale_factor=1.04), run_time=2.0)
        self.play(FadeOut(gapb), FadeIn(rungs[5]), run_time=0.6)
        self.beat("Role vars, in the role's own vars folder. They sit above group_vars, and above host_vars too.",
                  Indicate(rungs[5][1], color=PURPLE_M), run_time=2.0)
        rv5 = rv(5, '"Hello from the role"', PURPLE_M)
        imag = T("imagine someone puts the greeting here", 22, GREY_B).move_to([3.0, 3.1, 0])
        self.beat("Imagine someone puts the greeting in there. What does the canary get now? Pause and guess.",
                  FadeIn(imag), FadeIn(rv5, shift=RIGHT * 0.1), run_time=2.0)
        self.wait(2.0)
        c1 = two("Hello from", "the role", PURPLE_M, X1)
        c2 = two("Hello from", "the role", PURPLE_M, X2)
        self.beat("Both hosts get the role's text. The canary's own file is ignored, and Ansible gives no warning at all.",
                  Transform(a1, c1), Transform(a2, c2), Succession(Wait(1.6), Indicate(d3, color=RED_M, scale_factor=1.04)), run_time=3.4)
        self.beat("Well... the sticky note is still on the door. Nobody reads it anymore. A forgotten override like that can hide your change for weeks.",
                  d3.animate.set_opacity(0.35), run_time=1.6)

        # ---------- 6. guardrails
        self.play(FadeOut(VGroup(w1, w2, n1, n2, a1, a2, imag)), run_time=0.5)
        g = VGroup(
            VGroup(M("defaults/", 24, GREEN_M), T("settings a user may change", 26)).arrange(RIGHT, buff=0.3),
            VGroup(M("vars/", 24, PURPLE_M), T("the role's own fixed details", 26)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([1.9, 2.2, 0])
        self.play(FadeOut(VGroup(d0, d2, d3, rv5)), run_time=0.4)
        self.beat("So here's the guardrail. The defaults folder is for every setting a user may want to change. The vars folder is only for the role's own fixed details, things nobody should override.",
                  FadeIn(g[0], shift=RIGHT * 0.1), Succession(Wait(2.6), FadeIn(g[1], shift=RIGHT * 0.1)), run_time=5.0)
        files = VGroup(*[M(f, 22, TEAL_M) for f in ("defaults/main.yml", "group_vars/all.yml", "group_vars/web.yml", "host_vars/web2.yml")]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([1.6, -0.4, 0])
        xs = tick(False, 0.2).next_to(files, RIGHT, buff=0.4)
        self.beat("And picture the same name sitting in four files. Can anyone predict the result without opening all four and climbing the ladder in their head? Nobody can.",
                  LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in files], lag_ratio=0.3), Succession(Wait(3.6), Create(xs)), run_time=5.0)
        rule = VGroup(T("Set each variable in one place,", 30, YELLOW_M), T("plus its role default.", 30, YELLOW_M)).arrange(DOWN, buff=0.15).move_to([1.9, -2.6, 0])
        self.beat("So the rule: set each variable in one place, plus its role default. And when in doubt, ask the hosts with debug.",
                  FadeIn(rule, shift=UP * 0.15), run_time=2.4)
        self.wait(0.4)
        self.play(FadeOut(VGroup(g, files, xs, rule)), run_time=0.5)

        # ---------- 7. moral, recap, quick check
        rc = VGroup(T("defaults are suggestions: weakest", 26, GREEN_M),
                    T("a host beats its group", 26, TEAL_M),
                    T("the playbook beats the inventory", 26, BLUE_M),
                    T("role vars beat them all, silently", 26, PURPLE_M),
                    T("-e always wins", 26, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([1.9, 0.3, 0])
        self.beat("Let's climb it once more. Defaults are only suggestions. A host beats its group. The playbook beats the inventory. Role vars beat them all, silently. And the phone call, minus e, always wins.",
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rc], lag_ratio=0.7), run_time=7.0)
        self.beat("The moral of the story: Ansible never asks which note you meant. So leave it only one note to read.",
                  Indicate(rc[3], color=PURPLE_M, scale_factor=1.04), run_time=2.4)
        self.wait(0.4)
        self.play(FadeOut(VGroup(rc, rungs, up)), run_time=0.6)
        qq = T("Quick check", 30, YELLOW_M).move_to([0, 2.4, 0])
        qs = VGroup(VGroup(M("defaults/main.yml", 24, GREEN_M), T("Hello", 26)).arrange(RIGHT, buff=0.4),
                    VGroup(M("group_vars/web.yml", 24, TEAL_M), T("Hi", 26)).arrange(RIGHT, buff=0.4),
                    VGroup(M("host_vars/web2.yml", 24, TEAL_M), T("Hey", 26)).arrange(RIGHT, buff=0.4)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([0, 0.9, 0])
        qt = T("What does web2 get?", 30).move_to([0, -0.6, 0])
        self.beat("A quick check. The role default says Hello. The web group says Hi. web2's own file says Hey. What does web2 get? Pause and think.",
                  FadeIn(qq), LaggedStart(*[FadeIn(x) for x in qs], lag_ratio=0.4), FadeIn(qt), run_time=4.4)
        self.wait(2.0)
        ans = T("Hey: the most specific note in the inventory wins", 30, GREEN_M).move_to([0, -1.7, 0])
        self.beat("Hey. One host is more specific than its group, and both beat the role default.",
                  FadeIn(ans, shift=UP * 0.15), run_time=2.0)
        self.wait(1.0)
