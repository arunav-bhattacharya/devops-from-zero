import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\.github/workflows/", "dot github slash workflows"), (r"\.github/workflow/", "dot github slash workflow"),
            (r"\bpytest\b", "pie test"), (r"requirements-dev\.txt", "requirements dev dot T X T"),
            (r"actions/checkout", "actions slash checkout"), (r"\bubuntu-latest\b", "ubuntu latest"),
            (r"\btimeout-minutes\b", "timeout minutes"), (r"\bci\.yml\b", "C I dot yammel")])


def fix_indent(g, size):
    """Text drops leading spaces when lines are left-aligned; shift each line by its indent."""
    cw = M("x" * 20, size).width / 20
    for m in g:
        s = getattr(m, "original_text", "")
        m.shift(RIGHT * (len(s) - len(s.lstrip(" "))) * cw)
    return g


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color, s=1.0):
    body = RoundedRectangle(corner_radius=0.22, width=0.86, height=0.62, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1)
    head = Circle(radius=0.21, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), 1).next_to(body, UP, buff=0.06)
    return VGroup(body, head).scale(s)


def pot(color=GREY_B, s=1.0):
    body = RoundedRectangle(corner_radius=0.14, width=1.0, height=0.7, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.12), 1)
    rim = Line(LEFT * 0.62, RIGHT * 0.62, stroke_width=5, color=color).move_to(body.get_top())
    return VGroup(body, rim).scale(s)


def ticket(lines, color=GOLD_M, w=2.6, size=24):
    txt = VGroup(*[T(l, size) for l in lines]).arrange(DOWN, buff=0.1)
    r = Rectangle(width=w, height=txt.height + 0.4, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), 1)
    return VGroup(r, txt.move_to(r))


def pair(kitchen, tech, color, pos):
    a = T(kitchen, 24, GREY_B)
    b = T(tech, 26, color)
    return VGroup(a, b).arrange(DOWN, buff=0.08).move_to(pos)


class D24FreshStation(VoiceScene):
    def construct(self):
        self.title_card("Who tastes the soup when you push?", "events, workflows, runners and steps")

        # ---- 1. the question
        lap = box("your laptop", GREY_B, w=2.8, h=0.9).move_to([-4.3, 0.3, 0])
        gh = box("GitHub", WHITE, w=2.8, h=0.9).move_to([1.0, 0.3, 0])
        pa = edge_arrow(lap, gh)
        pl = M("git push", 24).next_to(pa, UP, buff=0.15)
        tk = tick(True, 0.3).next_to(gh, RIGHT, buff=0.5)
        self.beat("You push your code to GitHub, and a minute later, a green tick appears next to your commit.",
                  FadeIn(lap), FadeIn(gh), GrowArrow(pa), FadeIn(pl), Succession(Wait(1.4), Create(tk)), run_time=2.6)
        q1 = T("where did the tests run?", 30, YELLOW_M).move_to([0, -1.5, 0])
        q2 = T("how did it know a test failed?", 30, YELLOW_M).next_to(q1, DOWN, buff=0.3)
        self.beat("So where did your tests actually run? Not on your laptop. And how did a machine you have never seen know whether a test failed?",
                  FadeIn(q1, shift=UP * 0.1), Succession(Wait(2.2), FadeIn(q2, shift=UP * 0.1)), run_time=3.6)
        self.beat("Hold on to both questions. First, a small cafe.", FadeOut(VGroup(lap, gh, pa, pl, tk, q1, q2)), run_time=1.0)

        # ---- 2. the cafe owner
        owner = person(TEAL_M).move_to([-5.0, -0.2, 0])
        ol = T("owner", 26, TEAL_M).next_to(owner, DOWN, buff=0.2)
        pots = VGroup(*[pot() for _ in range(4)]).arrange(RIGHT, buff=0.6).move_to([0.8, -0.2, 0])
        day = T("quiet Tuesday", 30, GREY_B).move_to([0, 2.7, 0])
        self.beat("The owner tastes every pot of soup herself, before it goes out. On a quiet Tuesday, that works.",
                  FadeIn(owner), FadeIn(ol), FadeIn(day), LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in pots], lag_ratio=0.2), run_time=2.0)
        ticks = VGroup(*[tick(True, 0.2).next_to(p, UP, buff=0.25) for p in pots])
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.25), run_time=1.4)
        queue = VGroup(*[person(GREY_B, 0.7) for _ in range(5)]).arrange(RIGHT, buff=0.25).move_to([3.4, -2.6, 0])
        sat = T("busy Saturday", 30, GOLD_M).move_to(day)
        self.beat("On a busy Saturday, with a queue at the door, she skips one taste. Just this once.",
                  Transform(day, sat), FadeOut(ticks), LaggedStart(*[FadeIn(p, shift=LEFT * 0.3) for p in queue], lag_ratio=0.15), run_time=2.0)
        ticks2 = VGroup(*[tick(True, 0.2).next_to(pots[i], UP, buff=0.25) for i in (0, 1, 3)])
        self.play(LaggedStart(*[Create(t) for t in ticks2], lag_ratio=0.25), run_time=1.0)
        salt = T("no salt", 26, RED_M).next_to(pots[2], UP, buff=0.25)
        self.beat("That is the pot with no salt.", pots[2][0].animate.set_stroke(RED_M), FadeIn(salt), run_time=1.0)
        self.beat("Nobody would call her lazy. Her tongue is fine. Her Saturday is the problem.", Indicate(owner, color=TEAL_M), run_time=1.6)
        rule = T("a check that lives in a busy person's memory gets skipped on the busy day", 26, YELLOW_M).move_to([0, 2.0, 0])
        self.beat("A check that lives in a busy person's memory gets skipped exactly when it matters most. Testing on your own laptop has the same weakness.",
                  FadeIn(rule), run_time=2.0)
        self.beat("What we want is a taster who has no Saturdays.", run_time=None)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. the kitchen chain, mapped
        hdr = T("one push, step by step", 30, GREY_B).move_to([0, 3.15, 0])
        self.beat("So let's hire one. Picture a restaurant kitchen, and follow one order through it, step by step.", FadeIn(hdr), run_time=1.2)
        rail = Line([-6.4, 2.35, 0], [-2.4, 2.35, 0], stroke_width=4, color=GREY_B)
        tk1 = ticket(["push: this commit,", "this branch"], GOLD_M, w=3.2).next_to(rail, DOWN, buff=0.1)
        tk1.shift(LEFT * 3)
        p1 = pair("a ticket on the rail", "an event", GOLD_M, [-4.4, -0.1, 0])
        self.beat("You push. GitHub records an event: a push of this commit, to this branch. That's an order ticket landing on the rail.",
                  Create(rail), tk1.animate.shift(RIGHT * 3), FadeIn(p1), run_time=2.4)
        folder = VGroup(M(".github/workflows/", 24, BLUE_M), M("ci.yml   on: push", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        fbox = SurroundingRectangle(folder, color=BLUE_M, buff=0.2, corner_radius=0.1).set_fill(tint(BLUE_M, 0.1), 1)
        wf = VGroup(fbox, folder).move_to([0.0, 1.95, 0])
        p2 = pair("what the ticket says", "a workflow", BLUE_M, [0.0, 0.75, 0])
        self.beat("GitHub opens the folder .github/workflows/ in the commit you pushed, and starts a run of every workflow that listens for push.",
                  FadeIn(wf, shift=LEFT * 0.2), FadeIn(p2), run_time=2.4)
        self.beat("A workflow is just a text file that says what to run, and when. It is what's written on the ticket.",
                  Indicate(folder[1], color=BLUE_M), run_time=1.4)
        st = RoundedRectangle(corner_radius=0.12, width=3.8, height=3.0, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.06), 1).move_to([4.3, 0.95, 0])
        stl = T("fresh virtual machine", 24, GREEN_M).next_to(st, UP, buff=0.12)
        p3 = pair("a clean, empty station", "the runner", GREEN_M, [4.3, -1.25, 0])
        self.beat("For each job, GitHub starts a brand new virtual machine, a computer simulated in software. It is called the runner.",
                  Create(st), FadeIn(stl), FadeIn(p3), run_time=2.2)
        empty = T("tools, but none of your files", 24, GREY_B).move_to(st)
        self.beat("It comes with Linux and common tools, but none of your files. A clean, empty station.", FadeIn(empty), run_time=1.6)
        steps = VGroup(*[M(s, 22) for s in ["1  checkout", "2  set up Python", "3  install", "4  pytest -q"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(st)
        p4 = pair("the cook follows the ticket", "steps, in order", WHITE, [0.0, -1.25, 0])
        self.beat("A program on that machine runs the job's steps, one at a time, in order. The cook follows the ticket, line by line.",
                  FadeOut(empty), LaggedStart(*[FadeIn(s, shift=RIGHT * 0.15) for s in steps], lag_ratio=0.35), FadeIn(p4), run_time=2.6)
        res = tick(True, 0.28).move_to([-0.2, -2.6, 0])
        resl = T("tick or cross on the commit", 26, GREEN_M).next_to(res, RIGHT, buff=0.3)
        self.beat("The result, a green tick or a red cross, lands on the commit. Then GitHub deletes the machine. The station is wiped for the next order.",
                  Create(res), FadeIn(resl), Succession(Wait(2.4), AnimationGroup(FadeOut(steps), st.animate.set_stroke(opacity=0.35))), run_time=3.6)
        self.beat("So your laptop takes no part, and no file survives from one job to the next. Your first question, answered.",
                  Indicate(stl, color=GREEN_M), run_time=1.6)
        st2 = st.copy().set_stroke(opacity=1).scale(0.55).move_to([5.0, -2.55, 0])
        st.set_stroke(opacity=1)
        two = T("two jobs: two stations at once", 24, GREEN_M).next_to(st2, LEFT, buff=0.3)
        self.beat("And two jobs get two stations, side by side, at the same time. Like two cooks with two tickets.",
                  FadeOut(VGroup(res, resl)), FadeIn(st2), FadeIn(two), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. the empty station breaks the obvious job
        y1 = VGroup(M("runs-on: ubuntu-latest", 24), M("steps:", 24),
                    M("  - run: pip install -r requirements-dev.txt", 24, GOLD_M),
                    M("  - run: pytest -q", 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([-0.6, 1.5, 0])
        fix_indent(y1, 24)
        self.beat("Now let's write the job the obvious way. Install the packages the tests need, then run the tests. Exactly what you type on your laptop.",
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in y1], lag_ratio=0.25), run_time=2.6)
        gq = T("green or red?", 30, YELLOW_M).move_to([0, -1.0, 0])
        self.beat("Pause and guess. Green, or red?", FadeIn(gq), run_time=1.0)
        self.wait(2.0)
        x1 = tick(False, 0.22).next_to(y1[2], RIGHT, buff=0.3)
        why = T("requirements-dev.txt does not exist on that machine", 26, RED_M).move_to([0, -1.0, 0])
        self.beat("Red, at the very first step. requirements-dev.txt does not exist on that machine. On your laptop it was right there.",
                  FadeOut(gq), Create(x1), FadeIn(why), run_time=1.8)
        self.beat("Of course. We gave the cook a spotless station, and no ingredients.", Indicate(why, color=RED_M), run_time=1.4)
        y2 = VGroup(M("runs-on: ubuntu-latest", 24), M("steps:", 24),
                    M("  - uses: actions/checkout@v7", 24, TEAL_M),
                    M("  - uses: actions/setup-python@v7", 24, TEAL_M),
                    M('    with:', 24, TEAL_M), M('      python-version: "3.14"', 24, TEAL_M),
                    M("  - run: pip install -r requirements-dev.txt", 24, GOLD_M),
                    M("  - run: pytest -q", 24, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([-0.6, 1.1, 0])
        fix_indent(y2, 24)
        self.beat("So nearly every job begins with actions/checkout, which copies your repository onto the machine. Fetch the ingredients first.",
                  FadeOut(x1), FadeOut(why), Transform(y1[0], y2[0]), Transform(y1[1], y2[1]), Transform(y1[2], y2[6]), Transform(y1[3], y2[7]),
                  FadeIn(y2[2], shift=RIGHT * 0.1), run_time=2.4)
        self.beat("Then setup-python puts Python 3.14 on the station.", FadeIn(VGroup(y2[3], y2[4], y2[5]), shift=RIGHT * 0.1), run_time=1.4)
        kinds = VGroup(chip("run: your own shell command", GOLD_M, 24), chip("uses: a published action", TEAL_M, 24)).arrange(RIGHT, buff=0.5).move_to([0, -2.7, 0])
        self.beat("Notice there are two kinds of step. run executes your own shell commands. uses calls an action: ready made code that someone published, at a version after the at sign.",
                  LaggedStart(FadeIn(kinds[0]), FadeIn(kinds[1]), lag_ratio=0.6), run_time=3.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. how does it know? the exit code
        q3 = T("how did it know a test failed?", 30, YELLOW_M).move_to([0, 3.0, 0])
        self.beat("Now the second question. How does a machine that never read your tests know that one failed?", FadeIn(q3), run_time=1.6)
        cmd = M("$ pytest -q", 28).move_to([-4.2, 1.4, 0])
        code = VGroup(T("exit code", 26, GREY_B), M("0", 40, GREEN_M)).arrange(DOWN, buff=0.15).move_to([-4.2, -0.3, 0])
        self.beat("Every command ends with a number, its exit code. Zero means success. Anything else means trouble.",
                  FadeIn(cmd), FadeIn(code), run_time=1.8)
        one = M("1", 40, RED_M).move_to(code[1])
        self.beat("pytest exits with 1 when a test fails.", Transform(code[1], one), run_time=1.2)
        chain = VGroup(box("step", RED_M, w=1.8), box("job", RED_M, w=1.8), box("run", RED_M, w=1.8)).arrange(RIGHT, buff=0.9).move_to([2.2, -0.3, 0])
        for b in chain:
            b[0].set_stroke(GREY_B); b[1].set_color(GREY_B)
        arrs = VGroup(edge_arrow(code, chain[0]), edge_arrow(chain[0], chain[1]), edge_arrow(chain[1], chain[2]))
        self.play(FadeIn(chain), FadeIn(arrs), run_time=0.8)
        self.beat("A non zero exit code fails the step. The job stops there and is marked failed, and so is the run.",
                  LaggedStart(*[AnimationGroup(b[0].animate.set_stroke(RED_M), b[1].animate.set_color(RED_M)) for b in chain], lag_ratio=0.5), run_time=2.6)
        cross = tick(False, 0.3).next_to(chain[2], DOWN, buff=0.4)
        self.play(Create(cross), run_time=0.6)
        self.beat("So the machine doesn't read your test output at all. It reads one number. Most of CI rests on that habit: tools exit with a non zero code when something is wrong.",
                  Indicate(code[1], color=RED_M), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. guardrails
        gt = T("A clean station has rules of its own", 34).move_to([0, 3.0, 0])
        self.beat("A clean station is a fine taster, as long as you respect three rules.", FadeIn(gt), run_time=1.2)
        g1 = ticket(["never attach a self-hosted runner", "to a public repository"], RED_M, w=6.2, size=26).move_to([-3.3, 1.2, 0])
        self.beat("One. A self-hosted runner is a machine you run yourself. Never attach one to a public repository. Anyone can open a pull request, and a stranger's code could run on your machine, and leave things behind for your next job. A dirty station nobody cleaned.",
                  FadeIn(g1, shift=UP * 0.15), run_time=1.6)
        g2 = ticket(["set timeout-minutes much lower", "than the 360 minute maximum"], GOLD_M, w=6.2, size=26).move_to([3.3, 1.2, 0])
        self.beat("Two. A job may run for at most 6 hours. Set timeout-minutes much lower, or a hung job waits the full 360 minutes.",
                  FadeIn(g2, shift=UP * 0.15), run_time=1.6)
        g3 = ticket(["the station forgets everything:", "every run installs again from nothing"], GREEN_M, w=6.8, size=26).move_to([0, -1.4, 0])
        self.beat("Three. The wiped station forgets everything, so every run downloads and installs the same packages again. Day 25 adds a cache that remembers.",
                  FadeIn(g3, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. moral and quick check
        mo = VGroup(T("a push is a ticket; a workflow says what to cook;", 30),
                    T("a fresh runner cooks it; one exit code says how it went", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        self.beat("So here's the whole story. A push is a ticket. A workflow says what to cook. A fresh runner cooks it, step by step. And one exit code says how it went.",
                  FadeIn(mo[0]), Succession(Wait(2.4), FadeIn(mo[1])), run_time=4.4)
        self.beat("A taster with no Saturdays.", run_time=None)
        qc = VGroup(T("Quick check", 28, GOLD_M), M(".github/workflow/ci.yml", 26, BLUE_M),
                    T("You push. What do you see in the Actions tab?", 26)).arrange(DOWN, buff=0.25).move_to([0, -1.2, 0])
        self.beat("Quick check. You save your file as .github/workflow/ci.yml, with no s, and push. What do you see? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("Nothing at all: no run, no error. GitHub never looks there.", 26, GREEN_M).move_to(qc[2])
        self.beat("Nothing at all. No run, no error, no warning, because GitHub never looks in that folder. If no run appears after a push, check that path first.",
                  Transform(qc[2], ans), run_time=1.6)
        self.wait(1.2)
