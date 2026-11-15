import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcommons-lang3\b", "commons lang three"), (r"\bcommons-text\b", "commons text"), (r"\b3\.17\.0\b", "three point seventeen"),
            (r"\b3\.18\.0\b", "three point eighteen"), (r"\b1\.14\.0\b", "one point fourteen"), (r"\bWordUtils\b", "word utils"),
            (r"\bclasspaths?\b", lambda m: "class path" + ("s" if m.group(0).endswith("s") else "")), (r"\bapi\b", "A P I")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def dep(name, ver=None, color=WHITE, w=2.3):
    lines = VGroup(M(name, 20))
    if ver:
        lines.add(M(ver, 20, GREY_B))
    lines.arrange(DOWN, buff=0.1)
    r = RoundedRectangle(corner_radius=0.1, width=w, height=lines.height + 0.3, stroke_color=color, stroke_width=2.5).set_fill(tint(color), 1)
    return VGroup(r, lines.move_to(r))


def link_arrow(a, b, color=GREY_B):
    return Arrow(a.get_bottom(), b.get_top(), buff=0.08, stroke_width=2.5, color=color, max_tip_length_to_length_ratio=0.15)


class D29Dependencies(VoiceScene):
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
        self.title_card("Which version, on which classpath?", "transitive dependencies, highest-wins, implementation and api")

        # ---- 1. the tree
        app = dep("app", None, BLUE_M, w=1.8).move_to([-2.7, 2.65, 0])
        gr = dep("greeting", None, TEAL_M, w=2.1).move_to([-4.6, 1.25, 0])
        l17 = dep("commons-lang3", "3.17.0", GOLD_M).move_to([-0.85, 1.25, 0])
        ct = dep("commons-text", "1.14.0", PURPLE_M).move_to([-4.6, -0.45, 0])
        l18 = dep("commons-lang3", "3.18.0", GOLD_M).move_to([-4.6, -2.25, 0])
        e_ag, e_al = link_arrow(app, gr), link_arrow(app, l17)
        e_gc, e_cl = link_arrow(gr, ct), link_arrow(ct, l18)
        self.beat("hello-jvm now has two projects. app is the web service, and it uses the library greeting.",
                  FadeIn(app), GrowArrow(e_ag), FadeIn(gr), run_time=2.0)
        self.beat("Now try an experiment. app asks for a library directly: commons-lang3, version 3.17.0.",
                  GrowArrow(e_al), FadeIn(l17, shift=DOWN * 0.1), run_time=1.8)
        impl = M("implementation", 20, GREY_B).next_to(e_gc, RIGHT, buff=0.15)
        self.beat("And greeting uses commons-text inside. It declares it as implementation.",
                  GrowArrow(e_gc), FadeIn(ct, shift=DOWN * 0.1), FadeIn(impl), run_time=2.0)
        meta = T("its metadata file lists its own dependencies", 22, GREY_B).move_to([-0.7, -1.35, 0])
        self.steps("But libraries have dependencies of their own. The metadata file of commons-text lists commons-lang3, version 3.18.0. So that comes along too.",
                   (1.6, Indicate(ct, color=PURPLE_M)), (1.0, FadeIn(meta)), (1.2, GrowArrow(e_cl), FadeIn(l18, shift=DOWN * 0.1)))
        tr = T("transitive", 24, GOLD_M).next_to(l18, RIGHT, buff=0.3)
        self.beat("These are transitive dependencies. In a real service, they often outnumber the ones you declared.",
                  FadeOut(meta), FadeIn(tr), run_time=1.8)

        # ---- 2. conflict: highest wins
        q = T("two paths, two versions of one library. Which one?", 26, YELLOW_M).move_to([0, -3.35, 0])
        self.beat("Now two paths ask for different versions of the same library. Which one does app get?",
                  FadeOut(tr), Indicate(l17, color=YELLOW_M), Indicate(l18, color=YELLOW_M), FadeIn(q), run_time=2.4)
        win = T("highest version wins", 30, GOLD_M).move_to([3.6, 2.65, 0])
        cross = CurvedArrow(l17.get_bottom() + DOWN * 0.05, l18.get_right() + RIGHT * 0.08, angle=-0.6, color=GOLD_M, stroke_width=3)
        self.steps("Gradle settles this with one rule. The highest version wins. Your own declaration gets no extra weight.",
                   (1.6, FadeIn(win, shift=DOWN * 0.1)), (1.4, Create(cross)), (1.0, l17.animate.set_opacity(0.35)))
        bet = VGroup(T("newer: may need something only it has", 22, GREY_B),
                     T("older code: usually runs on the newer", 22, GREY_B)).arrange(DOWN, buff=0.15).next_to(win, DOWN, buff=0.35)
        self.beat("The bet: the library that asks for the newer version may need something only it has. Code written for the older one usually runs on the newer too.",
                  FadeIn(bet[0]), Succession(Wait(2.6), FadeIn(bet[1])), run_time=4.2)
        mav = T("Maven: the nearest declaration wins", 22, RED_M).next_to(bet, DOWN, buff=0.35)
        self.beat("This surprises people who know Maven. There, the declaration nearest your project wins.",
                  FadeIn(mav, shift=UP * 0.1), run_time=1.8)
        rep = M("\\--- org.apache.commons:commons-lang3:3.17.0 -> 3.18.0", 20, GOLD_M).move_to([0, -3.35, 0])
        self.beat("The dependencies report shows it with an arrow. 3.17.0 was asked for, and 3.18.0 was chosen.",
                  FadeOut(q), FadeIn(rep, shift=UP * 0.1), FadeOut(bet), FadeOut(mav), run_time=2.0)

        # ---- 3. two classpaths
        CPX = (2.4, 5.25)
        cols = VGroup()
        for x, name, c in ((CPX[0], "compile", BLUE_M), (CPX[1], "runtime", TEAL_M)):
            r = RoundedRectangle(corner_radius=0.12, width=2.65, height=3.75, stroke_color=c, stroke_width=2.5).set_fill(BLACK, 1).move_to([x, 0.15, 0])
            lab = VGroup(T(name, 24, c), T("classpath", 22, c)).arrange(DOWN, buff=0.06).next_to(r, UP, buff=0.12)
            cols.add(VGroup(r, lab))
        self.beat("But which classpath? A classpath is the list of jars the compiler, or the JVM, can see. app has one for compiling, and one for running.",
                  FadeOut(win), FadeOut(rep), LaggedStart(*[FadeIn(c) for c in cols], lag_ratio=0.4), run_time=3.0)
        SLOTS = [1.35, 0.35, -0.85]

        def slot(i, col):
            return np.array([CPX[col], SLOTS[i], 0])

        rg, rt, rl = gr.copy(), ct.copy(), l18.copy()
        self.steps("The runtime classpath gets everything the program needs to run. greeting, commons-text, and one copy of commons-lang3: 3.18.0.",
                   (1.6, Wait(1.6)),
                   (2.4, LaggedStart(rg.animate.move_to(slot(0, 1)), rt.animate.move_to(slot(1, 1)), rl.animate.move_to(slot(2, 1)), lag_ratio=0.35)))
        cg, cl = gr.copy(), l17.copy().set_opacity(1)
        blocked = ct.copy()
        self.steps("The compile classpath is different. greeting is there. But commons-text is not, because greeting declared it as implementation.",
                   (1.6, Wait(1.6)), (1.0, cg.animate.move_to(slot(0, 0))),
                   (1.4, blocked.animate.move_to(slot(1, 0) + LEFT * 0.4)), (0.8, blocked.animate.move_to(slot(1, 0) + LEFT * 2.2).set_opacity(0)),
                   (0.6, Indicate(impl, color=RED_M)))
        self.remove(blocked)
        own = T("each classpath is resolved on its own", 24, YELLOW_M).move_to([0, -3.35, 0])
        self.steps("Without commons-text, nothing here asks for 3.18.0. So the compile classpath keeps 3.17.0. Each classpath is resolved on its own.",
                   (1.6, Wait(1.6)), (1.4, cl.animate.move_to(slot(2, 0))), (1.0, FadeIn(own, shift=UP * 0.1)))
        err = M("Unresolved reference 'WordUtils'.", 20, RED_M).move_to([0, -3.35, 0])
        self.beat("So app cannot use commons-text itself. Import a class from it, and the compiler says unresolved reference.",
                  FadeOut(own), FadeIn(err, shift=UP * 0.1), Wiggle(cols[0][0]), run_time=2.4)

        # ---- 4. api
        api = M("api", 20, YELLOW_M).move_to(impl, aligned_edge=LEFT)
        self.beat("Change that one line from implementation to api.",
                  FadeOut(err), Transform(impl, api), run_time=1.4)
        ct2 = ct.copy()
        self.steps("Now commons-text joins app's compile classpath too. And it brings 3.18.0 along, so the highest wins here as well.",
                   (1.4, ct2.animate.move_to(slot(1, 0))), (1.2, Wait(1.2)),
                   (1.2, Transform(cl, l18.copy().move_to(slot(2, 0)))))
        rule = VGroup(T("api: only when a type from that library", 24, YELLOW_M),
                      T("appears in your public functions", 24, YELLOW_M)).arrange(DOWN, buff=0.12).move_to([0, -3.25, 0])
        self.beat("Use api only when a type from that library appears in your public functions. Then every caller needs it to compile.",
                  FadeIn(rule, shift=UP * 0.1), run_time=2.4)
        back = M("implementation", 20, GREY_B).move_to(impl, aligned_edge=LEFT)
        self.steps("Otherwise, make implementation your default. It keeps a library's insides private.",
                   (1.2, FadeOut(rule), Transform(impl, back)),
                   (1.4, ct2.animate.move_to(slot(1, 0) + LEFT * 2.2).set_opacity(0),
                    Transform(cl, l17.copy().set_opacity(1).move_to(slot(2, 0)))))
        self.remove(ct2)
        fast = T("upgrade it, and app does not recompile", 26, GREEN_M).move_to([0, -3.3, 0])
        self.beat("It also saves build time. When you upgrade an implementation dependency, the projects that use yours do not recompile.",
                  Indicate(ct, color=GREEN_M), FadeIn(fast, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- recap
        rc = VGroup(T("transitive dependencies come along with every library", 30, PURPLE_M),
                    T("when two versions meet, the highest wins", 30, GOLD_M),
                    T("implementation: hidden from callers when they compile", 30, BLUE_M),
                    T("api: part of your public face", 30, YELLOW_M)).arrange(DOWN, buff=0.4)
        self.beat("Every library brings its own dependencies. When two versions meet, the highest wins. And each classpath is resolved on its own: implementation stays hidden when callers compile, api does not.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rc], lag_ratio=0.5), run_time=5.5)
        self.wait(1.0)
