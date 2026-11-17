import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bcommons-lang3\b", "commons lang three"), (r"\bcommons-text\b", "commons text"), (r"\b3\.17\.0\b", "three point seventeen"),
            (r"\b3\.18\.0\b", "three point eighteen"), (r"\b1\.14\.0\b", "one point fourteen"), (r"\bdependencyInsight\b", "dependency insight"),
            (r"\bWordUtils\b", "word utils"), (r"\bNoSuchMethodError\b", "no such method error"), (r"\bcompileClasspath\b", "compile classpath"),
            (r"\bruntimeClasspath\b", "runtime classpath")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def paper(lines, color=WHITE, w=3.6, size=26, title=None):
    items = VGroup(*[T(l, size) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    if title:
        items = VGroup(T(title, size, color), items).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    r = Rectangle(width=w, height=items.height + 0.5, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
    return VGroup(r, items.move_to(r))


class D29SmallPrint(VoiceScene):
    def construct(self):
        self.title_card("Read the small print", "transitive dependencies, highest-wins, implementation and api")

        # ---- 1. the question
        decl = M('implementation("org.apache.commons:commons-lang3:3.17.0")', 24).move_to([0, 1.4, 0])
        self.beat("Your build file asks for a library, commons-lang3, at version 3.17.0. You wrote it down yourself.", FadeIn(decl), run_time=1.8)
        q = T("which version does your app run with?", 32, YELLOW_M).move_to([0, -0.4, 0])
        self.beat("So which version does your app run with? Surely the one you wrote. Hold that thought.", FadeIn(q, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(decl, q)), run_time=0.6)

        # ---- 2. the bakery and the butter
        shop = paper(["flour", "sugar", "croissant dough"], WHITE, w=3.6, title="shopping list").move_to([-4.3, 0.4, 0])
        self.beat("Picture our bakery. To save time, it buys ready-made croissant dough. Here's its shopping list.",
                  FadeIn(shop, shift=UP * 0.1), run_time=1.8)
        recall = paper(["a batch of the dairy's", "butter is unsafe"], RED_M, w=4.2, title="recall notice").move_to([3.6, 1.6, 0])
        self.beat("One morning a dairy announces a recall. A batch of its butter is unsafe.", FadeIn(recall, shift=DOWN * 0.1), run_time=1.6)
        ok = T("no butter on the list. relax.", 26, GREEN_M).next_to(shop, DOWN, buff=0.3)
        self.beat("The head baker checks the list, and relaxes. Butter isn't on it.", FadeIn(ok), run_time=1.4)
        dough = paper(["small print: made with butter", "from that very dairy"], GOLD_M, w=4.6, title="croissant dough").move_to([3.4, -1.4, 0])
        lk = edge_arrow(shop, dough, GOLD_M)
        self.beat("Then someone reads the small print on the dough. Made with butter, from that very dairy.",
                  GrowArrow(lk), FadeIn(dough, shift=UP * 0.1), Succession(Wait(1.4), Indicate(dough[1][1], color=GOLD_M)), run_time=2.6)
        self.beat("The list was honest. It just showed only what the bakery bought, and nothing about what came inside.",
                  FadeOut(ok), Indicate(shop[1][1][2], color=WHITE), run_time=2.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. map onto Gradle and build the tree
        app = mbox("app", WHITE, size=24).move_to([-5.3, 0.3, 0])
        gr = mbox("greeting", BLUE_M, size=24).move_to([-2.6, 1.7, 0])
        ct = mbox("commons-text:1.14.0", GOLD_M, size=22).move_to([1.0, 1.7, 0])
        l18 = mbox("commons-lang3:3.18.0", TEAL_M, size=22).move_to([4.5, 0.3, 0])
        l17 = mbox("commons-lang3:3.17.0", TEAL_M, size=22).move_to([0.2, -1.1, 0])
        e1, e2, e3, e4 = edge_arrow(app, gr), edge_arrow(gr, ct), edge_arrow(ct, l18), edge_arrow(app, l17)
        self.beat("Software has the same blind spot. Our lab app, hello-jvm, has two projects. app uses greeting, our own little library.",
                  FadeIn(app), GrowArrow(e1), FadeIn(gr), run_time=2.2)
        self.beat("greeting uses a library from outside, commons-text. That's the dough.", GrowArrow(e2), FadeIn(ct), run_time=1.6)
        meta = T("its metadata file lists its own dependencies", 24, GREY_B).next_to(ct, UP, buff=0.25)
        self.beat("Every published library comes with a small metadata file that lists its own dependencies. The small print. commons-text's says: I need commons-lang3, 3.18.0.",
                  FadeIn(meta), GrowArrow(e3), FadeIn(l18), run_time=2.6)
        tr = T("transitive: you get it because something you asked for needs it", 24, TEAL_M).move_to([2.3, -2.9, 0])
        self.beat("That's the butter inside the dough. A library you get because a library you asked for needs it. It's called a transitive dependency.",
                  FadeOut(meta), FadeIn(tr), run_time=2.4)
        self.beat("And app itself asks for commons-lang3 3.17.0 directly. The line we started with.",
                  GrowArrow(e4), FadeIn(l17), FadeOut(tr), run_time=1.8)
        q2 = T("one jar of commons-lang3 at run time. which one?", 28, YELLOW_M).move_to([0, -2.8, 0])
        self.beat("Two paths, two versions, and the kitchen stocks only one jar. Pause and guess. Which version runs?",
                  FadeIn(q2), Indicate(l17[1], color=TEAL_M), Indicate(l18[1], color=TEAL_M), run_time=2.0)
        self.wait(2.0)
        hw = M("commons-lang3:3.17.0 -> 3.18.0", 24, TEAL_M).move_to(l17)
        self.beat("3.18.0. Your own declaration gets no extra weight. When versions clash, Gradle's rule is simple: the highest version wins.",
                  FadeOut(q2), Transform(l17[1], hw), l17[0].animate.stretch_to_fit_width(hw.width + 0.5), run_time=2.2)
        arw = T("the arrow means: asked for one version, got another", 24, GREY_B).move_to([0.2, -2.0, 0])
        self.beat("The dependencies report shows it with an arrow: asked for 3.17.0, got 3.18.0.", FadeIn(arw), run_time=1.6)
        why = T("the bet: the newer version may be needed; old code usually runs on new", 24, GREY_B).move_to([0, -2.8, 0])
        self.beat("The bet is that the library asking for the newer version may need something only that version has, while code written for the older one usually runs on the newer too.",
                  FadeIn(why), run_time=2.4)
        mvn = T("Maven picks the declaration nearest your project instead", 24, GOLD_M).move_to([0, -3.4, 0])
        self.beat("If you know Maven, the other build tool, this surprises you. There, the declaration nearest your project wins.",
                  FadeIn(mvn), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. two classpaths: implementation, and the sauce
        self.beat("So far so good. Now let's look somewhere else: not where the app runs, but where it compiles.", run_time=None)
        rt = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.6, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.06), 1).move_to([3.3, 0.2, 0])
        cp = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.6, stroke_color=PURPLE_M, stroke_width=3).set_fill(tint(PURPLE_M, 0.06), 1).move_to([-3.3, 0.2, 0])
        rtl = M("runtimeClasspath", 24, GREEN_M).next_to(rt, UP, buff=0.15)
        cpl = M("compileClasspath", 24, PURPLE_M).next_to(cp, UP, buff=0.15)
        rti = VGroup(M("greeting", 24, BLUE_M), M("commons-text:1.14.0", 24, GOLD_M), M("commons-lang3:3.18.0", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(rt)
        self.beat("A classpath is the list of jars a program can see. app has one for running, with all three.",
                  Create(rt), FadeIn(rtl), FadeIn(rti), run_time=2.2)
        cpi = VGroup(M("greeting", 24, BLUE_M), M("commons-lang3:3.17.0", 24, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(cp)
        q3 = T("and the one for compiling?", 28, YELLOW_M).move_to([0, -2.8, 0])
        self.beat("And it has a separate one for compiling. What's on it? Pause and guess.", Create(cp), FadeIn(cpl), FadeIn(q3), run_time=1.6)
        self.wait(2.0)
        self.beat("Two surprises. commons-text is missing. And commons-lang3 is still 3.17.0 here, because each classpath is resolved on its own.",
                  FadeOut(q3), FadeIn(cpi), Succession(Wait(1.8), Indicate(cpi[1], color=TEAL_M)), run_time=3.2)
        imp = M('implementation("org.apache.commons:commons-text:1.14.0")', 22, GOLD_M).move_to([0, -2.6, 0])
        self.beat("commons-text is missing because of one word in greeting's build file: implementation.",
                  FadeIn(imp), run_time=1.6)
        self.beat("Think of a sauce you sell. The stock inside is your business, and customers never handle it. That's implementation: needed to compile and run greeting, but hidden from the projects that use it.",
                  Indicate(imp, color=GOLD_M), run_time=2.6)
        err = M("e: ... Unresolved reference 'WordUtils'.", 24, RED_M).move_to([-3.3, -3.3, 0])
        self.beat("So if app tries to import a class from commons-text, the compiler refuses: unresolved reference. The stock inside someone else's sauce isn't yours to use.",
                  FadeOut(imp), FadeIn(err), run_time=2.4)
        api = M('api("org.apache.commons:commons-text:1.14.0")', 22, BLUE_M).move_to([0, -2.6, 0])
        self.beat("Now say your label reads: serve on Brand X crackers. The crackers are part of what you promise, and customers need them too. That's api. It also puts the library on the compile classpath of every project that uses yours.",
                  FadeOut(err), FadeIn(api), run_time=3.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. guardrails
        gt = T("Reading the small print, in practice", 34).move_to([0, 2.9, 0])
        self.beat("Three habits come out of this picture.", FadeIn(gt), run_time=1.0)
        g1 = VGroup(T("default to implementation", 28, GOLD_M), T("use api only for types your public functions show", 24)).arrange(DOWN, buff=0.12).move_to([0, 1.6, 0])
        self.beat("One. Default to implementation. Use api only when a type from that library appears in your public functions. It keeps insides private, and an upgrade doesn't recompile every project that uses yours.",
                  FadeIn(g1, shift=UP * 0.1), run_time=2.0)
        g2 = VGroup(T("a recall for a version no file mentions?", 28, RED_M),
                    M("./gradlew :app:dependencyInsight --dependency commons-lang3", 22)).arrange(DOWN, buff=0.15).move_to([0, 0.0, 0])
        self.beat("Two. When a scanner reports a vulnerable version that no build file mentions, that's the butter recall. dependencyInsight shows which path brings it in. Then declare the fixed version yourself, and highest wins lifts every path to it.",
                  FadeIn(g2, shift=UP * 0.1), run_time=2.4)
        g3 = VGroup(T("compiled against 3.17.0, running on 3.18.0", 28, TEAL_M),
                    T("usually fine; a changed method fails only at run time", 24)).arrange(DOWN, buff=0.12).move_to([0, -1.7, 0])
        self.beat("Three. Compiling against 3.17.0 and running on 3.18.0 is usually harmless. But if a method you call changed, the code compiles fine, then fails at run time with NoSuchMethodError. The lesson's deeper section shows how to make the two classpaths agree.",
                  FadeIn(g3, shift=UP * 0.1), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. moral and quick check
        mo = VGroup(T("your list shows what you bought, not what came inside;", 30),
                    T("when versions meet, the highest wins", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.3, 0])
        self.beat("So, the moral. Your build file shows what you bought, not what came inside. When versions meet, the highest wins. And implementation keeps your ingredients your business.",
                  FadeIn(mo[0]), Succession(Wait(2.4), FadeIn(mo[1])), run_time=4.0)
        back = T("the version you wrote down is a request, not a promise", 26, GREY_B).next_to(mo, DOWN, buff=0.4)
        self.beat("The version you wrote at the start? A request, not a promise.", FadeIn(back), run_time=1.4)
        qc = VGroup(T("Quick check", 28, GOLD_M), T("app asks for 2.1, a library it uses asks for 2.3.", 26),
                    T("Which runs?", 26)).arrange(DOWN, buff=0.22).move_to([0, -1.6, 0])
        self.beat("Quick check, with made up numbers. app asks for version 2.1 of a library. Another library it uses asks for 2.3. Which one runs? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("2.3: the highest version wins, wherever it was asked for.", 26, GREEN_M).move_to(qc[2])
        self.beat("2.3. The highest version wins, no matter who asked for it.", Transform(qc[2], ans), run_time=1.4)
        self.wait(1.2)
