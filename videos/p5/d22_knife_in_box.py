import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bvenv\b", "venv"), (r"\b/venv\b", "slash venv"), (r"\bwhoami\b", "who am I"), (r"\bTrivy\b", "trivy"),
            (r"\bapp\.py\b", "app dot pie"), (r"\bpip\b", "pip"), (r"\bUSER 10001\b", "user ten thousand and one"),
            (r"\b10001\b", "ten thousand and one"), (r"\bARG\b", "arg"), (r"\bENV\b", "env"), (r"\bMB\b", "megabytes")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def lunchbox(color=GOLD_M, w=4.4, h=3.0):
    base = RoundedRectangle(corner_radius=0.2, width=w, height=h, stroke_color=color, stroke_width=3.5).set_fill(tint(color, 0.07), opacity=1)
    handle = Arc(radius=0.4, start_angle=0, angle=PI, stroke_color=color, stroke_width=3.5).next_to(base, UP, buff=0)
    return VGroup(base, handle)


class D22KnifeInBox(VoiceScene):
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
        self.title_card("The knife in the lunchbox", "ship only the lunch: stages, a normal user, and secrets kept out")

        # 1. the first big customer
        box_ = lunchbox(GOLD_M).move_to([2.6, -0.2, 0])
        lunch = chip("lunch", GOLD_M, 28).move_to(box_[0].get_center() + UP * 0.7)
        buyer = Circle(radius=0.3, stroke_color=WHITE, stroke_width=3).set_fill(tint(WHITE, 0.2), opacity=1).move_to([-3.6, 0.6, 0])
        bl = T("the buyer", 26, GREY_B).next_to(buyer, DOWN, buff=0.2)
        self.steps("Picture your small lunch kitchen landing its first big customer: an office that wants two hundred boxes a day. On day one, their buyer opens a box to check it.",
                   (0.8, Create(box_), FadeIn(lunch)), (2.6, Wait(2.6)), (0.6, FadeIn(buyer), FadeIn(bl)))
        knife = chip("a kitchen knife", RED_M, 26).move_to(box_[0].get_center() + LEFT * 0.95 + DOWN * 0.25)
        flour = chip("flour", GREY_B, 26).move_to(box_[0].get_center() + RIGHT * 1.25 + DOWN * 0.25)
        key = chip("the back door key", YELLOW_M, 26).move_to(box_[0].get_center() + DOWN * 1.0)
        self.steps("Next to the lunch she finds a kitchen knife, and a half-empty bag of flour. And taped under the lid is the key to your back door.",
                   (1.4, Wait(1.4)), (0.6, FadeIn(knife, scale=0.8)), (1.0, Wait(1.0)), (0.6, FadeIn(flour, scale=0.8)), (1.0, Wait(1.0)), (0.6, FadeIn(key, scale=0.8)))
        self.beat("Nobody packed those on purpose. They were lying on the counter while the lunch was made, so they went into the box. And the lunch itself tastes perfect.",
                  Wiggle(key), run_time=1.6)
        self.beat("That is the trap. An image fills up the same way, and the app inside works perfectly, so nobody looks.",
                  Indicate(lunch[1], color=GOLD_M), run_time=1.4)
        self.play(FadeOut(VGroup(buyer, bl)), run_time=0.4)

        # 2. map onto the Day 19 image
        lab = M("hello-devops:simple", 26, GOLD_M).next_to(box_, UP, buff=0.55)
        self.beat("Our hello-devops image from before has exactly these three. It was built in one stage, so everything used to build it ships with it.",
                  FadeIn(lab), run_time=1.6)
        maps = VGroup(VGroup(T("knife", 26, RED_M), T("= pip, the tool that installed the packages", 26)).arrange(RIGHT, buff=0.25),
                      VGroup(T("flour", 26, GREY_B), T("= leftovers from the build", 26)).arrange(RIGHT, buff=0.25),
                      VGroup(T("key", 26, YELLOW_M), T("= a secret token anyone can read", 26)).arrange(RIGHT, buff=0.25)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        maps.move_to([-3.2, -2.9, 0])
        fit(maps, 7.0)
        self.steps("The knife is pip, the tool that installed the app's packages. The app never needs it again, but an attacker could. The flour is whatever else the build left behind. And the key is a secret token, left where anyone who pulls the image can read it.",
                   (0.8, FadeIn(maps[0], shift=UP * 0.1)), (4.4, Wait(4.4)), (0.8, FadeIn(maps[1], shift=UP * 0.1)), (1.6, Wait(1.6)), (0.8, FadeIn(maps[2], shift=UP * 0.1)))
        self.play(FadeOut(maps), run_time=0.4)

        # 3. the wish: cook in the kitchen, ship only the lunch
        self.beat("Wouldn't it be nice to cook in the kitchen, and ship only the lunch? Leave the knife and the flour on the counter.",
                  VGroup(box_, lunch, knife, flour, key, lab).animate.scale(0.75).move_to([3.4, 0.1, 0]), run_time=1.6)
        kit = RoundedRectangle(corner_radius=0.2, width=4.6, height=3.6, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.06), opacity=1).move_to([-3.4, 0.0, 0])
        kl = VGroup(M("FROM python:3.14-slim AS build", 22, BLUE_M), T("stage 1: the kitchen", 26, BLUE_M)).arrange(DOWN, buff=0.12).next_to(kit, UP, buff=0.2)
        self.steps("That is a multi-stage build. One Dockerfile, with two FROM lines. Each FROM starts a new stage, from a clean base. The first stage is the kitchen.",
                   (2.6, Wait(2.6)), (0.8, Create(kit), FadeIn(kl)))
        venv = chip("/venv: the packages", GREEN_M, 26, mono=True).move_to(kit.get_center() + UP * 0.75)
        pipk = chip("pip", RED_M, 26, mono=True).move_to(kit.get_center() + DOWN * 0.3 + LEFT * 1.0)
        flk = chip("build leftovers", GREY_B, 24).move_to(kit.get_center() + DOWN * 1.15)
        self.steps("In the kitchen we make a virtual environment, a folder called venv that holds the app's Python packages. pip installs them into it, and then we remove pip from it.",
                   (1.6, Wait(1.6)), (0.6, FadeIn(venv)), (1.4, Wait(1.4)), (0.6, FadeIn(pipk), FadeIn(flk)), (1.2, Wait(1.2)), (0.6, pipk.animate.set_opacity(0.3)))
        newbox = lunchbox(GOLD_M, 3.3, 2.25).move_to([3.4, 0.1, 0])
        nl = VGroup(M("FROM python:3.14-slim", 22, GOLD_M), T("stage 2: the lunchbox", 26, GOLD_M)).arrange(DOWN, buff=0.12).next_to(newbox, UP, buff=0.2)
        self.steps("The second stage starts again from a fresh, empty base. It even removes the base image's own pip.",
                   (0.8, FadeOut(VGroup(box_, lunch, knife, flour, key, lab))), (0.8, Create(newbox), FadeIn(nl)))
        cp = M("COPY --from=build /venv /venv", 22, GREEN_M).move_to([0, -2.6, 0])
        arr = Arrow(kit.get_right() + UP * 0.75, newbox[0].get_left() + UP * 0.5, buff=0.15, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.1)
        v2 = venv.copy().scale(0.9).move_to(newbox[0].get_center() + UP * 0.45)
        app = chip("app.py", GOLD_M, 26, mono=True).move_to(newbox[0].get_center() + DOWN * 0.4)
        self.steps("Then it reaches back into the kitchen for exactly one thing: the venv, with every package already installed. And it adds app.py.",
                   (1.6, Wait(1.6)), (0.6, FadeIn(cp), GrowArrow(arr)), (1.0, TransformFromCopy(venv, v2)), (1.4, Wait(1.4)), (0.6, FadeIn(app)))
        only = T("only the last stage becomes the image", 28, YELLOW_M).move_to([0, -3.25, 0])
        self.beat("Only the last stage becomes the image. The kitchen, with its knife and flour, stays behind in the build cache.",
                  FadeIn(only, shift=UP * 0.1), kit.animate.set_stroke(opacity=0.4), run_time=1.6)

        # 4. predict the size; break the 'it is about size' model
        self.play(FadeOut(VGroup(only, cp)), run_time=0.4)
        self.beat("So how much smaller is the image now? Pause and guess.")
        self.wait(2.0)
        tr_a, tr_b = ValueTracker(51.8), ValueTracker(51.8)
        sz = always_redraw(lambda: T(f"{tr_a.get_value():.1f} MB", 32, GOLD_M).move_to([3.4, -2.3, 0]))
        was = T("was 51.8 MB", 26, GREY_B).move_to([3.4, -2.95, 0])
        self.steps("Barely. The content went from 51.8 megabytes to 49.6.",
                   (0.4, FadeIn(sz), FadeIn(was)), (1.6, tr_a.animate.set_value(49.6)))
        self.beat("Well, that is not much of a diet. And that's fine, because size was never the point here.", run_time=None)
        scan = VGroup(M("trivy: HIGH findings", 24, GREY_B), M("from pip:     5  ->  0", 24, GREEN_M), M("from Debian: 44  (no fix yet)", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-3.4, -2.75, 0])
        self.steps("The point is what left. A vulnerability scanner called Trivy checks every package against public lists of known bugs. Removing pip took away 5 high findings. They sat in libraries that pip carries inside itself.",
                   (1.4, Wait(1.4)), (0.6, FadeIn(scan[0])), (3.4, Wait(3.4)), (0.8, FadeIn(scan[1]), pipk.animate.set_opacity(0.1)))
        self.steps("The 44 that stayed come from the Debian base, and on the day we scanned, none of them had a fix yet. You rebuild when Debian ships one. Your numbers will differ, because new bugs are published every day.",
                   (0.8, FadeIn(scan[2])))
        sz.clear_updaters()
        self.play(FadeOut(VGroup(sz, was, scan, arr)), run_time=0.4)

        # 5. a normal user
        who = M("$ docker run --rm hello-devops:simple whoami", 22, GREY_B).move_to([0, 3.35, 0])
        root = M("root", 26, RED_M).next_to(who, DOWN, buff=0.15)
        self.steps("Next, who opens the box. The old image runs as root. Ask it who am I, and it says root.",
                   (1.0, FadeOut(VGroup(kit, kl, venv, pipk, flk)), FadeIn(who)), (1.6, Wait(1.6)), (0.6, FadeIn(root)))
        kern = box("one shared kernel", TEAL_M, w=8.0, h=0.65, size=26).move_to([0, -2.6, 0])
        self.steps("The walls of a container fence it in, but it is still root on a kernel it shares with everyone. Break out through one bug, and you arrive with root's rights.",
                   (1.4, Wait(1.4)), (0.6, FadeIn(kern, shift=UP * 0.1)), (2.4, Wait(2.4)), (0.8, Wiggle(kern)))
        user = VGroup(M("RUN useradd --uid 10001 --no-create-home appuser", 22, GREEN_M), M("USER 10001", 24, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-0.2, -1.2, 0])
        fit(user, 12.0)
        idl = M("uid=10001(appuser)", 26, GREEN_M).move_to(root)
        self.steps("Two lines in the final stage fix it. Create a normal user with the number 10001, and switch to it. Now the same question says: user 10001.",
                   (2.4, Wait(2.4)), (0.8, FadeIn(user, shift=UP * 0.1)), (1.6, Wait(1.6)), (0.6, Transform(who, M("$ docker run --rm hello-devops:1.0.0 id", 22, GREY_B).move_to(who)), Transform(root, idl)))
        r1 = T("Run as a number: 10001 is plainly not 0.", 28, YELLOW_M).move_to([0, 0.2, 0])
        self.beat("Write the number, not the name. A name means nothing until someone reads the image's user list. A number like 10001 is plainly not zero, which is root.",
                  FadeIn(r1, shift=UP * 0.1), run_time=1.6)
        self.play(FadeOut(VGroup(who, root, kern, user, r1)), run_time=0.5)

        # 6. the key under the lid: secrets
        self.play(VGroup(newbox, nl, v2, app).animate.scale(0.8).move_to([4.1, 1.3, 0]), run_time=0.6)
        arg = VGroup(M("ARG API_TOKEN", 24, YELLOW_M), M("--build-arg API_TOKEN=s3cr3t-demo-token", 22, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([-2.6, 2.2, 0])
        self.steps("Last, the key under the lid. Sometimes a build step needs a secret, like a token to download a private package. A token is a secret string that works like a password.",
                   (2.4, Wait(2.4)), (0.8, FadeIn(arg[0])))
        self.steps("The obvious way is a build argument. So we build with a fake token, s3cr3t demo token. The build finishes, and the token is not in the running container. Who can find it? Pause and guess.",
                   (1.6, Wait(1.6)), (0.8, FadeIn(arg[1])))
        self.wait(2.0)
        hist = VGroup(M("$ docker history --no-trunc leak | grep API_TOKEN", 22, GREY_B), M("API_TOKEN=s3cr3t-demo-token", 24, RED_M), M("API_TOKEN=s3cr3t-demo-token", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-2.0, 0.0, 0])
        tape = chip("key", YELLOW_M, 24).move_to(newbox[0].get_top() + DOWN * 0.3)
        self.steps("Anyone who pulls the image. docker history, the list of steps that built it, prints the token. Twice.",
                   (1.4, Wait(1.4)), (0.6, FadeIn(hist[0])), (1.6, Wait(1.6)), (0.6, FadeIn(hist[1]), FadeIn(hist[2])), (0.6, FadeIn(tape, scale=0.7)))
        leaks = T("ARG, ENV, or COPY then rm: all ship with the image", 26, RED_M).move_to([-1.2, -1.35, 0])
        self.beat("The other obvious ways leak too. ENV stores the value in the image's settings. And copying a token file, then deleting it later, leaves it in its layer. The soup jar again.",
                  FadeIn(leaks, shift=UP * 0.1), run_time=1.6)
        mount = M("RUN --mount=type=secret,id=api_token,env=API_TOKEN ...", 22, GREEN_M).move_to([-0.6, -2.25, 0])
        fit(mount, 11.5)
        zero = M("history: 0 matches for s3cr3t", 24, GREEN_M).next_to(mount, DOWN, buff=0.25)
        self.steps("The safe way is a secret mount. The secret is handed to that one RUN step while it runs, and never lands in a layer, the cache, or the history. Search the history now: zero matches.",
                   (0.8, FadeIn(mount)), (5.6, Wait(5.6)), (0.6, FadeIn(zero)), (0.6, FadeOut(tape, scale=0.5)))
        r2 = T("A secret in ARG, ENV or a deleted file ships with the image. Mount it.", 26, YELLOW_M).move_to([0, -3.4, 0])
        fit(r2, 12.4)
        self.beat("So here is the rule. A secret in ARG, ENV, or a deleted file ships with the image. Mount it instead.",
                  FadeIn(r2, shift=UP * 0.1), run_time=1.4)
        self.play(FadeOut(VGroup(arg, hist, leaks, mount, zero, r2)), run_time=0.5)

        # 7. guardrails
        g = VGroup(T("smaller bases are harder to debug: no shell to open", 26, GOLD_M),
                   T("pin the base by digest, and let a bot propose updates", 26, GOLD_M),
                   T("a token that ever went in as ARG is leaked: replace it", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-1.6, -1.0, 0])
        fit(g, 9.4)
        self.steps("A few honest costs. A smaller base, with no shell inside, is harder to debug. A base pinned to its exact fingerprint stops getting fixes by itself, so teams let a bot propose updates. And a token that ever went in as an ARG must be treated as leaked, and replaced.",
                   (0.8, FadeIn(g[0], shift=UP * 0.1)), (2.6, Wait(2.6)), (0.8, FadeIn(g[1], shift=UP * 0.1)), (3.0, Wait(3.0)), (0.8, FadeIn(g[2], shift=UP * 0.1)))
        self.play(FadeOut(g), run_time=0.5)

        # 8. moral and quick check
        hc = chip("tests itself every 30 s", TEAL_M, 24).next_to(newbox, DOWN, buff=0.3)
        u = chip("user 10001", GREEN_M, 24).next_to(hc, DOWN, buff=0.15)
        mor = VGroup(T("cook in the kitchen, ship only the lunch", 28, BLUE_M), T("open the box as a normal user", 28, GREEN_M), T("never tape the key under the lid", 28, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([-2.6, 0.6, 0])
        self.steps("So the moral of the story. Cook in the kitchen, and ship only the lunch. Open the box as a normal user. And never tape the key under the lid. Our final image also carries a health check that tests the app every thirty seconds.",
                   (0.6, FadeIn(mor[0], shift=UP * 0.1)), (1.6, Wait(1.6)), (0.6, FadeIn(mor[1], shift=UP * 0.1), FadeIn(u)), (1.4, Wait(1.4)), (0.6, FadeIn(mor[2], shift=UP * 0.1)), (2.0, Wait(2.0)), (0.6, FadeIn(hc)))
        self.play(FadeOut(mor), run_time=0.4)
        quiz = VGroup(T("Quick check: last month a token went in as ARG.", 26, YELLOW_M), T("Today you switch to a secret mount. Safe now?", 26, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([-2.4, 0.9, 0])
        self.beat("Quick check. Last month, a token went in as a build argument. Today you switch to a secret mount. Are you safe now?",
                  FadeIn(quiz, shift=UP * 0.1), run_time=1.4)
        self.wait(2.0)
        ans = VGroup(T("No. The old images still carry it.", 26, GREEN_M), T("Treat it as leaked, and replace it.", 26, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(quiz, DOWN, buff=0.4).align_to(quiz, LEFT)
        self.beat("No. Every image built last month still carries it in its history. Treat it as leaked, and replace it.", FadeIn(ans, shift=UP * 0.1), run_time=1.2)
        self.wait(1.2)
