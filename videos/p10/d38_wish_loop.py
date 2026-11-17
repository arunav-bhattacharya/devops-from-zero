import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Day 38, fifth pass (Venkat style). Restaurant manager world.
# Concept: desired state plus a loop that never stops (reconciliation).
# Colours, one per object for the whole video: wish/list = BLUE, waiters/Pods = TEAL,
# manager/controller loop = GOLD, failure = RED, prompts = YELLOW.

SAY.extend([(r"\b1\.0\.0\b", "one point oh point oh")])


def tint(c, k=0.22):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def person(color, s=1.0):
    head = Circle(radius=0.17, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    body = RoundedRectangle(corner_radius=0.16, width=0.56, height=0.42, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.35), 1)
    body.next_to(head, DOWN, buff=0.05)
    return VGroup(head, body).scale(s)


def pod(color=TEAL_M):
    return Circle(radius=0.32, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.25), opacity=1)


class Base(VoiceScene):
    def steps(self, text, *plays):
        """Speak one line while several plays run one after another."""
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

    def pause_guess(self, pos=None):
        c = chip("pause and guess", YELLOW_M, 26).move_to(pos if pos is not None else [4.6, -3.0, 0])
        n2 = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        n1 = T("1", 30, YELLOW_M).move_to(n2)
        self.play(FadeIn(c, shift=UP * 0.1), FadeIn(n2), run_time=0.4)
        self.wait(0.8)
        self.play(ReplacementTransform(n2, n1), run_time=0.2)
        self.wait(0.8)
        self.play(FadeOut(c), FadeOut(n1), run_time=0.3)


class D38WishLoop(Base):
    def construct(self):
        self.title_card("Who starts it again at 3 a.m.?", "a written wish, and a loop that never goes home")

        # ---------- 1. QUESTION + FAMILIAR: an order carried out once
        clock = T("3:00", 44, GREY_B).move_to([5.2, 2.7, 0])
        app = pod().move_to([0, 0.2, 0])
        alab = M("hello-devops", 26, TEAL_M).next_to(app, DOWN, buff=0.3)
        self.beat("Here is a question every new team asks sooner or later. Your app crashes at three in the morning. Who starts it again?",
                  FadeIn(clock), GrowFromCenter(app), FadeIn(alab), run_time=2.0)
        cmd = M("$ docker run hello-devops:1.0.0", 28).move_to([0, 2.5, 0])
        self.beat("Start with what we know. With docker run, the command that starts one container, you give an order, and Docker carries it out. Once.",
                  Write(cmd), Indicate(app, color=TEAL_M), run_time=2.2)
        x = tick(False, 0.45).move_to(app)
        self.beat("An hour later the container dies. And nothing happens, because Docker already did its job.",
                  app.animate.set_stroke(RED_M).set_fill(tint(RED_M, 0.25)), Create(x), alab.animate.set_color(RED_M), run_time=1.6)
        self.beat("docker run is a waiter who serves your dish and then goes home for the night. Drop your fork, and nobody is coming. So the point is this: an order is carried out once, and then nobody is watching.",
                  Wiggle(clock), run_time=1.6)
        self.play(FadeOut(VGroup(cmd, app, x, alab, clock)), run_time=0.6)

        # ---------- 2. PAIN + WISH: the script that keeps growing
        code = VGroup(M("every minute:", 24, GREY_B), M("  if app is not running:", 24), M("    start it", 24))
        code.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        code[1].shift(RIGHT * 0.4); code[2].shift(RIGHT * 0.8)
        crect = RoundedRectangle(corner_radius=0.12, width=6.0, height=code.height + 0.6, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1)
        card = VGroup(crect, code.move_to(crect).align_to(crect, LEFT).shift(RIGHT * 0.3)).move_to([-3.0, 1.6, 0])
        self.beat("The obvious fix? Write a little script that checks every minute. If the app is not running, start it. Three lines. Done.",
                  Create(crect), LaggedStart(*[Write(l) for l in code], lag_ratio=0.3), run_time=2.4)
        asks = ["a server died: move its work", "spread copies over 20 servers", "visitors doubled: add copies", "swap version 1 for version 2"]
        chips = VGroup(*[chip(a, RED_M, 26) for a in asks]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([3.3, 0.4, 0])
        more = VGroup(*[Line([0, 0, 0], [w, 0, 0], stroke_width=6, color=GREY_D) for w in (4.6, 3.8, 5.0, 4.2, 3.4, 4.8, 3.9)])
        more.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        self.steps("Then a server dies, and the script must move work somewhere else. Then it must spread copies, add copies when visitors double, and swap versions without a pause.",
                   (0.8, FadeIn(chips[0], shift=LEFT * 0.2)), (0.8, FadeIn(chips[1], shift=LEFT * 0.2)),
                   (0.8, FadeIn(chips[2], shift=LEFT * 0.2)), (0.8, FadeIn(chips[3], shift=LEFT * 0.2)))
        big = RoundedRectangle(corner_radius=0.12, width=6.0, height=5.4, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1).move_to([-3.0, -0.1, 0])
        more.next_to(code, DOWN, buff=0.3).align_to(code, LEFT)
        self.beat("Soon the little script is a large system of its own, and somebody has to run it and fix it. Your three lines now need a night shift.",
                  Transform(crect, big), card[1].animate.move_to([-3.0, 1.75, 0]).align_to(big, LEFT).shift(RIGHT * 0.3),
                  run_time=1.4)
        more.next_to(code, DOWN, buff=0.3).align_to(code, LEFT)
        self.play(LaggedStart(*[Create(l) for l in more], lag_ratio=0.15), run_time=1.2)
        wish = T("wouldn't it be nice to just write down what we want?", 30, YELLOW_M).move_to([0, -3.1, 0])
        self.beat("So let us say the wish out loud. Wouldn't it be nice to write down what we want, just once, and have someone keep it true?",
                  FadeIn(wish, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(VGroup(crect, code, more, chips, wish)), run_time=0.7)

        # ---------- 3. ANALOGY + MAP: the manager walking the floor
        tables = VGroup(*[RoundedRectangle(corner_radius=0.15, width=1.6, height=1.0, stroke_color=GREY_B, stroke_width=2.5).set_fill(BLACK, 1)
                          for _ in range(3)]).arrange(RIGHT, buff=1.3).move_to([1.4, 0.6, 0])
        tnum = VGroup(*[T(f"table {i + 1}", 24, GREY_B).next_to(t, DOWN, buff=0.15) for i, t in enumerate(tables)])
        waiters = VGroup(*[person(TEAL_M, 0.85).next_to(t, UP, buff=0.12) for t in tables])
        lst = VGroup(T("the list", 26, BLUE_M), T("table 1: a waiter", 24), T("table 2: a waiter", 24), T("table 3: a waiter", 24))
        lst.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        lrect = RoundedRectangle(corner_radius=0.12, width=lst.width + 0.5, height=lst.height + 0.45, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.1), 1)
        board = VGroup(lrect, lst.move_to(lrect)).move_to([-4.85, 1.4, 0])
        mgr = person(GOLD_M, 1.0).move_to([-4.85, -1.2, 0])
        mlab = T("manager", 26, GOLD_M).next_to(mgr, DOWN, buff=0.15)
        self.beat("Our restaurant has a manager who does exactly that. She holds a list of what each table should have.",
                  Create(lrect), FadeIn(lst), FadeIn(mgr, shift=UP * 0.2), FadeIn(mlab), run_time=2.0)
        self.beat("Three tables, and each one should have a waiter.",
                  LaggedStart(*[AnimationGroup(Create(t), FadeIn(n)) for t, n in zip(tables, tnum)], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(w, shift=DOWN * 0.15) for w in waiters], lag_ratio=0.2), run_time=2.0)
        path = [[-2.2, -1.4, 0], [tables[0].get_center()[0], -1.4, 0], [tables[1].get_center()[0], -1.4, 0], [tables[2].get_center()[0], -1.4, 0]]
        ticks = VGroup(*[tick(True, 0.16).next_to(lst[i + 1], RIGHT, buff=0.15) for i in range(3)])
        mlab.add_updater(lambda m: m.next_to(mgr, DOWN, buff=0.15))
        self.steps("She walks the floor. She counts what is really there. One, two, three. All good.",
                   (0.9, mgr.animate.move_to(path[1])), (0.6, Create(ticks[0])),
                   (0.7, mgr.animate.move_to(path[2])), (0.5, Create(ticks[1])),
                   (0.7, mgr.animate.move_to(path[3])), (0.5, Create(ticks[2])))
        sick = waiters[1]
        self.beat("Then the waiter at table two calls in sick.",
                  sick.animate.set_opacity(0.15), FadeOut(ticks), run_time=1.2)
        cross = tick(False, 0.14).next_to(lst[2], RIGHT, buff=0.15)
        door = T("door", 24, GREY_B).move_to([5.9, -2.6, 0])
        new = person(TEAL_M, 0.85).move_to([5.9, -1.9, 0])
        self.steps("On her next pass she reads the list, counts two, and sends for one more. Nobody told her what to do about sick waiters. A gap is just a gap.",
                   (1.2, mgr.animate.move_to(path[2])), (0.6, Create(cross)),
                   (0.5, FadeIn(door), FadeIn(new)), (1.4, new.animate.move_to(sick)), (0.4, FadeOut(sick), FadeOut(cross)))
        waiters = VGroup(waiters[0], new, waiters[2])
        mlab.clear_updaters()

        # the map, said out loud
        maps = VGroup(
            VGroup(T("the list", 26, BLUE_M), T("=", 26, GREY_B), T("desired state", 26)),
            VGroup(T("counting", 26, TEAL_M), T("=", 26, GREY_B), T("actual state", 26)),
            VGroup(T("the manager", 26, GOLD_M), T("=", 26, GREY_B), T("a controller", 26)),
        )
        for m in maps:
            m.arrange(RIGHT, buff=0.25)
        maps.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([1.6, -2.55, 0])
        self.play(FadeOut(door), mgr.animate.move_to([-4.85, -1.2, 0]), mlab.animate.move_to([-4.85, -1.95, 0]), run_time=0.8)
        self.play(VGroup(tables, tnum, waiters).animate.shift(UP * 0.9), run_time=0.6)
        self.steps("Let us map it. The list is your desired state: what you wrote down. What she counts is the actual state: what is really running. And the manager is a small program called a controller.",
                   (0.8, FadeIn(maps[0], shift=UP * 0.1), Indicate(lrect, color=BLUE_M)), (2.2, Wait(2.2)),
                   (0.8, FadeIn(maps[1], shift=UP * 0.1)), (1.6, Wait(1.6)),
                   (0.8, FadeIn(maps[2], shift=UP * 0.1), Indicate(mlab, color=GOLD_M)))
        self.wait(0.6)
        self.play(FadeOut(VGroup(tables, tnum, waiters, board, mgr, mlab, maps)), run_time=0.8)

        # ---------- 4. SHRINK: the same loop in Kubernetes
        want = VGroup(M("replicas: 3", 24, YELLOW_M), M("image: hello-devops:1.0.0", 24))
        want.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        frame_w = RoundedRectangle(corner_radius=0.15, width=want.width + 0.6, height=want.height + 0.6, stroke_color=BLUE_M, stroke_width=3)
        frame_w.set_fill(tint(BLUE_M, 0.1), opacity=1)
        desired = VGroup(frame_w, want.move_to(frame_w)).move_to([-3.9, 1.9, 0])
        dlab = T("desired state", 28, BLUE_M).next_to(desired, UP, buff=0.25)
        self.beat("Now Kubernetes. You write down one wish: run three copies of hello-devops, version 1.0.0. Kubernetes stores it as an object, a record in its database.",
                  Create(frame_w), LaggedStart(*[Write(l) for l in want], lag_ratio=0.3), FadeIn(dlab), run_time=2.4)
        node = RoundedRectangle(corner_radius=0.15, width=4.2, height=1.6, stroke_color=GREY_B, stroke_width=2).move_to([3.9, 1.9, 0])
        nlab = T("actual state", 28, TEAL_M).next_to(node, UP, buff=0.25)
        pods = VGroup(*[pod() for _ in range(3)]).arrange(RIGHT, buff=0.45).move_to(node)
        count = T("running: 3", 28, TEAL_M).next_to(node, DOWN, buff=0.3)
        self.beat("On the other side, the nodes report what is really running.",
                  Create(node), FadeIn(nlab), LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.25), FadeIn(count), run_time=1.8)

        c, R = np.array([0, -1.45, 0]), 1.25
        read = box("read", GOLD_M, w=1.8, h=0.66, size=26).move_to(on_circle(c, R, 90))
        look = box("observe", GOLD_M, w=1.8, h=0.66, size=26).move_to(on_circle(c, R, -30))
        act = box("act", GOLD_M, w=1.8, h=0.66, size=26).move_to(on_circle(c, R, 210))
        arcs = VGroup(
            CurvedArrow(on_circle(c, R, 60), on_circle(c, R, 0), angle=-np.radians(60), color=GREY_B, stroke_width=3),
            CurvedArrow(on_circle(c, R, -60), on_circle(c, R, -120), angle=-np.radians(60), color=GREY_B, stroke_width=3),
            CurvedArrow(on_circle(c, R, 180), on_circle(c, R, 120), angle=-np.radians(60), color=GREY_B, stroke_width=3),
        )
        clab = T("controller", 28, GOLD_M).move_to([-3.0, -1.45, 0])
        self.beat("And in between, the controller runs the manager's walk, forever.",
                  LaggedStart(Create(arcs), *[AnimationGroup(Create(b[0]), Write(b[1])) for b in (read, look, act)], lag_ratio=0.2), FadeIn(clab), run_time=2.4)

        def light(b, on=True):
            return b[0].animate.set_stroke(width=7 if on else 3)

        self.steps("Read the desired state. Observe the actual state. If the two differ, act to make them match. Then repeat.",
                   (0.9, light(read), Indicate(want[0], color=YELLOW_M)), (0.4, Wait(0.4)),
                   (0.9, light(read, False), light(look), Indicate(count, color=TEAL_M)), (0.4, Wait(0.4)),
                   (0.9, light(look, False), light(act)), (1.4, light(act, False), Rotate(arcs, angle=-TAU, about_point=c)))

        # ---------- 5. PREDICT, then SHOW
        gone = pods[2]
        self.beat("Now someone deletes one copy by mistake. Nobody wrote any code for this case. So what happens?",
                  gone.animate.set_stroke(RED_M).set_fill(BLACK).scale(0.6).set_opacity(0.25),
                  Transform(count, T("running: 2", 28, RED_M).move_to(count)), run_time=1.6)
        self.pause_guess()
        gap = T("3 wanted, 2 running", 28, YELLOW_M).move_to([0, 2.9, 0])
        self.beat("On its next pass, the loop reads three wanted, and counts two running.",
                  light(read), light(look), FadeIn(gap, shift=DOWN * 0.15), run_time=1.6)
        newp = pod().move_to(gone)
        self.beat("So it starts one more. Just like the manager sending for a waiter. A deleted copy is one more gap to close.",
                  light(read, False), light(look, False), light(act), FadeOut(gone), GrowFromCenter(newp),
                  Transform(count, T("running: 3", 28, TEAL_M).move_to(count)), FadeOut(gap), run_time=1.8)
        pods = VGroup(pods[0], pods[1], newp)
        self.play(light(act, False), run_time=0.4)

        # ---------- 6. BREAK the wrong model: fixing it by hand
        hand = T("you, on the node: stop this container", 26, RED_M).next_to(node, DOWN, buff=0.3)
        self.beat("Now the tempting move. You want one copy gone, so you go straight to the node and stop the container yourself. You are the boss here, right?",
                  FadeOut(count), FadeIn(hand), Indicate(pods[0], color=RED_M), run_time=2.0)
        p0 = pods[0]
        self.play(p0.animate.set_stroke(RED_M).set_fill(BLACK).scale(0.6).set_opacity(0.25), run_time=0.8)
        back = pod().move_to(p0)
        self.steps("Watch the loop. Three wanted, two running. Act.",
                   (0.7, light(read), light(look)), (0.6, light(read, False), light(look, False), light(act)),
                   (0.8, FadeOut(p0), GrowFromCenter(back)), (0.4, light(act, False)))
        pods = VGroup(back, pods[1], pods[2])
        self.beat("Well. It is back. Kubernetes is not being stubborn. It is loyal to the list, not to whoever touched the container last.",
                  Indicate(back, color=TEAL_M), run_time=1.2)
        rule = T("Change the wish, not the container.", 32, YELLOW_M).move_to(hand)
        self.beat("So the point really is this. A change made behind its back does not stick. Change the wish, not the container.",
                  FadeOut(hand), FadeIn(rule, shift=UP * 0.1), run_time=1.6)
        new5 = M("replicas: 5", 24, YELLOW_M).move_to(want[0], aligned_edge=LEFT)
        target = VGroup(*[pod() for _ in range(5)]).arrange(RIGHT, buff=0.18).scale(0.75).move_to(node)
        extra = VGroup(pod().scale(0.75).move_to(target[3]), pod().scale(0.75).move_to(target[4]))
        self.beat("Want five copies? Do not start two by hand. Edit the wish to five, and apply it.",
                  Transform(want[0], new5), FadeOut(rule), run_time=1.4)
        self.steps("The same loop sees five wanted and three running, and starts two more. You said what. Never how.",
                   (1.0, light(read), light(look), light(act)),
                   (1.4, *[pods[i].animate.move_to(target[i]).scale(0.75) for i in range(3)], LaggedStart(*[GrowFromCenter(e) for e in extra], lag_ratio=0.3)),
                   (0.4, light(read, False), light(look, False), light(act, False)))

        # ---------- 7. NAME it
        recon = T("reconciliation", 40, GOLD_M).move_to([0, -1.45, 0])
        gloss = T("bringing two lists back into agreement", 26, GREY_B).move_to([0, -3.15, 0])
        self.beat("This loop has a name. It is called reconciliation, which means bringing two lists back into agreement.",
                  FadeOut(VGroup(arcs, read, look, act, clab)), FadeIn(recon, scale=0.9), FadeIn(gloss, shift=UP * 0.1), run_time=2.0)
        spec = T("spec: your wish", 28, BLUE_M).move_to(dlab)
        status = T("status: its report", 28, TEAL_M).move_to(nlab)
        self.beat("You can see it in every object. The spec field is your wish. Kubernetes fills in the status field, its report on what is real. Controllers work to make status match spec.",
                  Transform(dlab, spec), Transform(nlab, status), run_time=2.4)
        thermo = T("like a thermostat: you set 21 degrees, never \"heat for ten minutes\"", 26, GREY_B).move_to([0, -3.15, 0])
        self.beat("The Kubernetes docs compare it to a thermostat. You set twenty one degrees, and it keeps reading the room. You never tell it to heat for ten minutes.",
                  FadeOut(gloss), FadeIn(thermo, shift=UP * 0.1), run_time=1.8)

        # ---------- 8. GUARDRAIL: the habit to take away
        self.play(FadeOut(VGroup(thermo, recon)), run_time=0.6)
        q1 = T("1. What does its spec ask for?", 30, BLUE_M)
        q2 = T("2. Which controller makes that happen?", 30, GOLD_M)
        qs = VGroup(q1, q2).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([0, -1.6, 0])
        self.beat("Most kinds of object have a controller, sometimes several. So here is a habit for the rest of this part. When you meet a new kind of object, ask two questions.",
                  FadeIn(q1, shift=UP * 0.1), run_time=1.0)
        self.beat("What does its spec ask for? And which controller makes that happen?",
                  Indicate(q1, color=BLUE_M), FadeIn(q2, shift=UP * 0.1), run_time=1.6)
        tf = VGroup(chip("Terraform, Ansible: only while they run", GREY_B, 26), chip("Kubernetes: all the time", GOLD_M, 26)).arrange(DOWN, buff=0.2).move_to([0, -2.65, 0])
        self.play(qs.animate.shift(UP * 0.9), run_time=0.5)
        self.beat("And notice the difference from Terraform and Ansible, which compare code with reality only while they run. This loop checks all the time, with nobody at the keyboard.",
                  LaggedStart(FadeIn(tf[0], shift=UP * 0.1), FadeIn(tf[1], shift=UP * 0.1), lag_ratio=0.6), run_time=2.4)

        # ---------- 9. MORAL + quick check
        self.play(FadeOut(VGroup(qs, tf, desired, dlab, node, nlab, *pods, *extra)), run_time=0.8)
        recap = VGroup(T("an order runs once", 30, GREY_B), T("a wish is kept true", 30, BLUE_M), T("by a loop that never goes home", 30, GOLD_M))
        recap.arrange(DOWN, buff=0.35).move_to([0, 1.2, 0])
        self.steps("So, the moral of the story. An order runs once, and then nobody watches. A wish is kept true, by a loop that never goes home. You write what you want. The loop works out the how.",
                   (0.8, FadeIn(recap[0], shift=UP * 0.1)), (1.6, Wait(1.6)), (0.8, FadeIn(recap[1], shift=UP * 0.1)),
                   (0.8, FadeIn(recap[2], shift=UP * 0.1)))
        check = T("Quick check: 3 wanted, 3 running. What does the loop do?", 30, YELLOW_M).move_to([0, -1.4, 0])
        self.beat("One quick check before you go. The wish says three, and the nodes report three running. What does the loop do on this pass?",
                  FadeIn(check, shift=UP * 0.1), run_time=1.4)
        self.pause_guess([0, -2.5, 0])
        ans = T("Nothing. No gap, nothing to act on. It just looks again.", 28, WHITE).move_to([0, -2.5, 0])
        self.beat("Nothing at all. There is no gap, so there is nothing to act on. It simply looks again on the next pass.",
                  FadeIn(ans, shift=UP * 0.1), run_time=1.4)
        self.wait(1.2)
