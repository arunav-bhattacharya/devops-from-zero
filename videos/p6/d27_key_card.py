import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bGITHUB_TOKEN\b", "github token"), (r"\bGHCR\b", "G H C R"), (r"\bghcr\.io\b", "G H C R dot I O"),
            (r"\bv1\.2\.0\b", "v one point two point oh"), (r"\b1\.2\.0\b", "one point two point oh"), (r"\bv4\b", "v four"),
            (r"tj-actions/changed-files", "T J actions changed files"), (r"\brelease\.yml\b", "release dot yammel"),
            (r"\bamd64\b", "A M D sixty four"), (r"\barm64\b", "arm sixty four"), (r"\bDependabot\b", "Depend a bot")])


def fix_indent(g, size):
    """Text drops leading spaces when lines are left-aligned; shift each line by its indent."""
    cw = M("x" * 20, size).width / 20
    for m in g:
        s = getattr(m, "original_text", "")
        m.shift(RIGHT * (len(s) - len(s.lstrip(" "))) * cw)
    return g


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def key(color, s=1.0):
    ring = Circle(radius=0.28, stroke_color=color, stroke_width=4)
    shaft = Line(RIGHT * 0.28, RIGHT * 1.2, stroke_width=4, color=color)
    t1 = Line(RIGHT * 0.95, RIGHT * 0.95 + DOWN * 0.22, stroke_width=4, color=color)
    t2 = Line(RIGHT * 1.15, RIGHT * 1.15 + DOWN * 0.3, stroke_width=4, color=color)
    return VGroup(ring, shaft, t1, t2).scale(s)


def door(label, color=GREY_B):
    r = Rectangle(width=1.3, height=1.9, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
    knob = Dot(radius=0.06, color=color).move_to(r.get_right() + LEFT * 0.22).set_z_index(2)
    t = T(label, 24, color).next_to(r, DOWN, buff=0.15)
    return VGroup(r, knob, t)


def commit(color=GREY_B, r=0.22):
    return Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)


class D27KeyCard(VoiceScene):
    def construct(self):
        self.title_card("A key for one shift", "shipping an image without a master key on a hook")

        # ---- 1. the question and the master key
        q = T("the release needs a key. which key?", 32, YELLOW_M).move_to([0, 2.9, 0])
        self.beat("Our pipeline is ready to ship: build the image, push it to a registry, an online store for images. That push needs a key. So which key?",
                  FadeIn(q), run_time=2.0)
        doors = VGroup(door("van"), door("office"), door("safe")).arrange(RIGHT, buff=0.9).move_to([1.6, 0.0, 0])
        hook = Line([-5.0, 1.0, 0], [-5.0, 0.6, 0], stroke_width=4, color=GREY_B)
        mk = key(GOLD_M, 1.0).rotate(-PI / 2).next_to(hook, DOWN, buff=0.0)
        mkl = T("master key", 26, GOLD_M).next_to(mk, DOWN, buff=0.25)
        self.beat("Picture the evening our kitchen starts delivering. The van is outside, and the driver needs a key. The quick fix: a copy of the master key on a hook by the back door.",
                  FadeIn(doors), Create(hook), FadeIn(mk), FadeIn(mkl), run_time=2.6)
        self.beat("It opens the van, the office and the safe. And it works, for years.",
                  LaggedStart(*[d[0].animate.set_stroke(GOLD_M) for d in doors], lag_ratio=0.3), run_time=1.6)
        st = VGroup(Circle(radius=0.2, stroke_color=RED_M, stroke_width=3), RoundedRectangle(corner_radius=0.2, width=0.8, height=0.6, stroke_color=RED_M, stroke_width=3))
        st.arrange(DOWN, buff=0.05).move_to([-3.3, -2.2, 0])
        self.beat("Nothing goes wrong for months, which is exactly why the hook feels fine. Then a stranger waiting at the door notices the key. Nobody would ever know a copy was made.",
                  FadeIn(st, shift=RIGHT * 0.3), Succession(Wait(2.6), Indicate(mk, color=RED_M)), run_time=3.6)
        self.beat("In a pipeline, the master key is a password or a long lived token, stored once and used by every job. What we really want is a key that opens one door, and expires within hours.",
                  run_time=None)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 2. GITHUB_TOKEN: a key card for one shift
        tl = Line([-5.6, -2.4, 0], [5.6, -2.4, 0], stroke_width=3, color=GREY_B)
        js = Line([-3.6, -2.25, 0], [-3.6, -2.55, 0], stroke_width=3, color=GREY_B)
        je = Line([3.0, -2.25, 0], [3.0, -2.55, 0], stroke_width=3, color=GREY_B)
        jsl = T("job starts", 24, GREY_B).next_to(js, DOWN, buff=0.12)
        jel = T("job ends", 24, GREY_B).next_to(je, DOWN, buff=0.12)
        card = RoundedRectangle(corner_radius=0.15, width=4.6, height=2.6, stroke_color=TEAL_M, stroke_width=3).set_fill(tint(TEAL_M, 0.1), 1).move_to([-0.3, 0.9, 0])
        ct = M("GITHUB_TOKEN", 28, TEAL_M).next_to(card.get_top(), DOWN, buff=0.3)
        cr = T("this repository only", 24, GREY_B).next_to(ct, DOWN, buff=0.2)
        self.beat("A good kitchen gives each cook a key card for one shift. GitHub does the same. Every job gets a token without asking: the GITHUB_TOKEN.",
                  Create(card), FadeIn(ct), run_time=2.0)
        self.beat("GitHub creates it when the job starts. It only works on the current repository.",
                  Create(tl), Create(js), FadeIn(jsl), FadeIn(cr), run_time=1.6)
        life = Line([-3.6, -1.9, 0], [3.0, -1.9, 0], stroke_width=6, color=TEAL_M)
        self.beat("And it expires when the job ends, after six hours at most on GitHub's runners. A leaked copy is useless by dinner.",
                  Create(life), Create(je), FadeIn(jel), run_time=2.0)
        perm = VGroup(M("contents: read", 24), M("packages: none", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(cr, DOWN, buff=0.3)
        self.beat("Here's the catch. Every action in the job can use this card, even if you never pass it on. So whatever the token may do, every action may do.",
                  Indicate(card, color=TEAL_M), run_time=2.2)
        self.beat("So you decide what the card opens, with the permissions key. At the top of the workflow, set a small default: contents read.",
                  FadeIn(perm[0], shift=UP * 0.1), run_time=1.8)
        self.beat("Any permission you don't list becomes none.", FadeIn(perm[1], shift=UP * 0.1), run_time=1.2)
        pw = M("packages: write", 24, GOLD_M).move_to(perm[1], aligned_edge=LEFT)
        rj = T("only in the release job", 24, GOLD_M).next_to(card, RIGHT, buff=0.3)
        self.beat("Then, only in the job that pushes the image, grant one more: packages write.",
                  Transform(perm[1], pw), FadeIn(rj), run_time=1.6)
        lp = T("least privilege: only the access the task needs", 28, YELLOW_M).move_to([0, 3.15, 0])
        self.beat("That idea has a name: least privilege. A card that opens the fridge, but not the cash drawer.",
                  FadeIn(lp), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 3. from a tag to an image
        tg = chip("git push origin v1.2.0", WHITE, 26, mono=True).move_to([-4.6, 2.6, 0])
        self.beat("Now the release itself. A tag is a fixed name for one commit. You push the tag v1.2.0, and that starts release.yml.",
                  FadeIn(tg, shift=DOWN * 0.1), run_time=1.8)
        stp = VGroup(T("1  check out the code at the tag", 26), T("2  log in to ghcr.io with the GITHUB_TOKEN", 26),
                     T("3  turn the git tag into image tags", 26), T("4  build amd64 and arm64, push both", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        stp.move_to([-1.6, 0.1, 0])
        self.beat("It checks out the code at the tag. It logs in to GitHub Container Registry, ghcr.io, with the job's own token. No password is stored anywhere.",
                  FadeIn(stp[0]), Succession(Wait(1.6), FadeIn(stp[1])), run_time=3.0)
        tags = VGroup(chip("1.2.0", GOLD_M, 24, mono=True), chip("sha-<short commit>", GOLD_M, 24, mono=True), chip("latest", GOLD_M, 24, mono=True)).arrange(DOWN, buff=0.18).move_to([4.6, 0.6, 0])
        self.beat("The metadata action turns the git tag into image tags: 1.2.0, sha plus the short commit, and latest.",
                  FadeIn(stp[2]), LaggedStart(*[FadeIn(t, shift=LEFT * 0.15) for t in tags], lag_ratio=0.3), run_time=2.4)
        self.beat("Then it builds for amd64, most servers, and arm64, like your Mac, and pushes both under one tag.",
                  FadeIn(stp[3]), run_time=1.8)
        q2 = T("you push a tag by mistake. what happens?", 28, YELLOW_M).move_to([0, -2.9, 0])
        self.beat("So far so good. Now you push a tag by mistake. Pause and guess: what happens?", FadeIn(q2), run_time=1.4)
        self.wait(2.0)
        a2 = T("it ships at once: nobody is in the way", 28, RED_M).move_to(q2)
        self.beat("It ships, at once. Nobody is in the way. No restaurant van should leave before the manager checks the order.",
                  Transform(q2, a2), run_time=1.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 4. a person says go
        jb = box("release job", PURPLE_M, w=3.0).move_to([3.4, 0.6, 0])
        gate = VGroup(Line([0, -0.6, 0], [0, 1.8, 0], stroke_width=6, color=GOLD_M), Line([-0.4, 1.8, 0], [0.4, 1.8, 0], stroke_width=6, color=GOLD_M))
        gl = M("environment: production", 24, GOLD_M).move_to([0, 2.5, 0])
        tg2 = chip("v1.2.0", WHITE, 24, mono=True).move_to([-3.8, 0.6, 0])
        self.beat("So the release job says environment: production. An environment is a named place you deploy to, with its own rules.",
                  FadeIn(tg2), FadeIn(jb), Create(gate), FadeIn(gl), run_time=2.2)
        self.play(tg2.animate.move_to([-0.9, 0.6, 0]), run_time=0.8)
        rv = VGroup(T("required reviewer", 26, GOLD_M), T("one approval lets the job go on", 24, GREY_B)).arrange(DOWN, buff=0.12).move_to([0, -1.5, 0])
        self.beat("Before the job starts, GitHub checks the environment's protection rules. A required reviewer: one approval lets the job go on.",
                  FadeIn(rv), run_time=2.0)
        ok = tick(True, 0.24).next_to(gate, UP, buff=0.1).shift(RIGHT * 0.7)
        self.beat("You click approve. Only then does the job start, and only then does it get the environment's secrets.",
                  Create(ok), tg2.animate.move_to(jb.get_left() + LEFT * 0.8), run_time=1.8)
        trap = T("trap: an environment that doesn't exist is created with no rules", 26, RED_M).move_to([0, -2.9, 0])
        self.beat("One trap. If a workflow names an environment that doesn't exist yet, GitHub creates it with no rules, and the job runs at once. Create it, and its rules, before the first tag.",
                  FadeIn(trap), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 5. borrowed code: a tag can move
        self.beat("One door is still open. Every action you call is someone else's code, running with your token.", run_time=None)
        line = Line([-5.6, 0.4, 0], [3.6, 0.4, 0], stroke_width=3, color=GREY_B)
        good = commit(GREEN_M).move_to([-2.6, 0.4, 0])
        bad = commit(RED_M).move_to([2.4, 0.4, 0])
        repo = T("the action's repository", 24, GREY_B).next_to(line, DOWN, buff=0.5).align_to(line, LEFT)
        lab = chip("v4", BLUE_M, 26, mono=True).next_to(good, UP, buff=0.4)
        use = M("uses: some-owner/some-action@v4", 24).move_to([0, 2.9, 0])
        self.beat("Say you write uses, some action, at v4. It feels like a version. Versions don't change. Right?",
                  FadeIn(use), Create(line), FadeIn(repo), GrowFromCenter(good), FadeIn(lab, shift=DOWN * 0.1), run_time=2.4)
        jar = T("a jar labelled tomato sauce", 26, GOLD_M).move_to([-2.6, -1.9, 0])
        self.beat("A tag is only a label. Whoever controls that repository can move it to different code. It's a jar labelled tomato sauce that the supplier can refill with anything.",
                  FadeIn(jar), run_time=2.4)
        self.play(GrowFromCenter(bad), run_time=0.6)
        self.beat("And it happened. In March 2025, the tags of the popular tj-actions/changed-files action were moved to a malicious commit that printed CI secrets into workflow logs.",
                  lab.animate.next_to(bad, UP, buff=0.4), run_time=2.0)
        self.beat("Same label. New code. Your workflow file never changed.", Indicate(use, color=RED_M), run_time=1.6)
        pin = VGroup(M("uses: docker/login-action@", 22, GREEN_M), M("  81c6f93d4bc991e510b342a00b419b3bb4efc5c6 # v4.7.0", 22, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([0, -2.85, 0])
        fix_indent(pin, 22)
        pl = T("a full commit SHA: 40 characters, cannot be moved", 26, GREEN_M).next_to(pin, UP, buff=0.2)
        self.beat("A full commit SHA, the 40 character ID of one commit, cannot be moved. So pin third party actions to one, and keep the version in a comment, the way the lab pins Docker's login action.",
                  FadeOut(jar), FadeIn(pl), FadeIn(pin), Indicate(good, color=GREEN_M), run_time=2.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 6. guardrails
        gt = T("Keys and pins need looking after", 34).move_to([0, 2.9, 0])
        self.beat("Two guardrails, because this is easy to get almost right.", FadeIn(gt), run_time=1.2)
        g1 = VGroup(T("pins go stale", 28, BLUE_M), T("Dependabot opens update pull requests:", 24),
                    T("weekly, only for releases 7 days old, grouped", 24)).arrange(DOWN, buff=0.15).move_to([-3.3, 0.7, 0])
        self.beat("One. Pins go stale. Dependabot, GitHub's update helper, opens pull requests to move them. The lab checks weekly, and only suggests a release once it is seven days old. The world gets a week to notice a bad one.",
                  FadeIn(g1, shift=UP * 0.1), run_time=2.0)
        g2 = VGroup(T("*** is not a lock", 28, RED_M), T("the log hides exact secret values only;", 24),
                    T("a changed copy prints in full", 24)).arrange(DOWN, buff=0.15).move_to([3.3, 0.7, 0])
        self.beat("Two. The runner hides secret values in logs as three stars, but only exact matches. A secret your script changes, say encoded in base64, prints in full. So never echo a secret, and if one leaks, rotate it.",
                  FadeIn(g2, shift=UP * 0.1), run_time=2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---- 7. moral and quick check
        mo = VGroup(T("a key card for one shift, a person at the gate,", 30),
                    T("and borrowed code locked to a commit", 30, YELLOW_M)).arrange(DOWN, buff=0.3).move_to([0, 2.3, 0])
        self.beat("So, the moral. No master key on the hook. A key card for one shift, that opens only the doors it needs. A person at the gate. And borrowed code locked to a commit you chose.",
                  FadeIn(mo[0]), Succession(Wait(3.0), FadeIn(mo[1])), run_time=4.4)
        rule = T("a tag can move; a commit SHA cannot", 28, GREY_B).next_to(mo, DOWN, buff=0.4)
        self.beat("A tag can move. A commit SHA cannot.", FadeIn(rule), run_time=1.2)
        qc = VGroup(T("Quick check", 28, GOLD_M), T("An older repository, and a workflow with no permissions key.", 26),
                    T("What can its token do?", 26)).arrange(DOWN, buff=0.22).move_to([0, -1.7, 0])
        self.beat("Quick check. An older repository has a workflow with no permissions key at all. What can its token do? Pause and think.",
                  FadeIn(qc, shift=UP * 0.1), run_time=1.6)
        self.wait(2.0)
        ans = T("Maybe read and write. Write permissions in every workflow.", 26, GREEN_M).move_to(qc[2])
        self.beat("Maybe read and write. Older repositories, and some organizations, still default to that. So write permissions in every workflow, and stop guessing.",
                  Transform(qc[2], ans), run_time=1.6)
        self.wait(1.2)
