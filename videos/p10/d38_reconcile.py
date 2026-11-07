import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *


def pod(color=TEAL_M):
    c = Circle(radius=0.32, stroke_color=color, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.25), opacity=1)
    return c


class D38Reconcile(VoiceScene):
    def construct(self):
        self.title_card("Kubernetes runs on a loop", "desired state, actual state, and the gap between them")

        # 1. docker run: an order, carried out once
        cmd = M("docker run hello-devops:1.0.0", 30).to_edge(UP, buff=0.9)
        one = pod().move_to(DOWN * 0.3)
        self.beat("With docker run, you give an order, and Docker carries it out once.",
                  Write(cmd), GrowFromCenter(one), run_time=1.8)
        x = tick(False, 0.45).move_to(one)
        self.beat("If that container crashes at three in the morning, nothing starts it again. The order was already done.",
                  one.animate.set_stroke(RED_M).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(RED_M), 0.25)), Create(x), run_time=1.6)
        self.play(FadeOut(VGroup(cmd, one, x)), run_time=0.6)

        # 2. desired state, written down and stored
        want = VGroup(M("kind: Deployment", 21), M("replicas: 3", 21, YELLOW_M), M("image: hello-devops:1.0.0", 21))
        want.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        frame_w = RoundedRectangle(corner_radius=0.15, width=want.width + 0.7, height=want.height + 0.7, stroke_color=BLUE_M, stroke_width=3)
        frame_w.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(BLUE_M), 0.10), opacity=1)
        desired = VGroup(frame_w, want.move_to(frame_w)).move_to(LEFT * 4.55 + UP * 0.4)
        dlab = T("desired state", 28, BLUE_M).next_to(desired, UP, buff=0.3)
        self.beat("Kubernetes works the other way round. You describe the end state you want.",
                  Create(frame_w), LaggedStart(*[Write(l) for l in want], lag_ratio=0.3), FadeIn(dlab), run_time=2.2)
        db = mbox("etcd", GREY_B, size=22).next_to(desired, DOWN, buff=0.5)
        self.beat("Kubernetes stores that description as an object, a record in its database. Run three copies of hello-devops.",
                  GrowFromCenter(db), Indicate(want[1], color=YELLOW_M), run_time=1.6)

        # 3. actual state: what is really running on the nodes
        node = RoundedRectangle(corner_radius=0.15, width=3.4, height=2.0, stroke_color=GREY_B, stroke_width=2).move_to(RIGHT * 4.55 + UP * 0.4)
        nlab = T("actual state", 28, TEAL_M).next_to(node, UP, buff=0.3)
        pods = VGroup(*[pod() for _ in range(3)]).arrange(RIGHT, buff=0.45).move_to(node)
        count = T("running: 3", 26, TEAL_M).next_to(node, DOWN, buff=0.35)
        self.beat("On the other side is the actual state: what is really running, as the nodes report it.",
                  Create(node), FadeIn(nlab), LaggedStart(*[GrowFromCenter(p) for p in pods], lag_ratio=0.25), FadeIn(count), run_time=2.0)

        # 4. the controller loop between them
        c, R = DOWN * 0.15, 1.15
        read = box("read", BLUE_M, w=1.6, h=0.62, size=24).move_to(on_circle(c, R, 90))
        look = box("observe", TEAL_M, w=1.6, h=0.62, size=24).move_to(on_circle(c, R, -30))
        act = box("act", GOLD_M, w=1.6, h=0.62, size=24).move_to(on_circle(c, R, 210))
        arcs = VGroup(
            CurvedArrow(on_circle(c, R, 62), on_circle(c, R, -2), angle=-np.radians(64), color=GREY_B, stroke_width=3),
            CurvedArrow(on_circle(c, R, -58), on_circle(c, R, -122), angle=-np.radians(64), color=GREY_B, stroke_width=3),
            CurvedArrow(on_circle(c, R, 182), on_circle(c, R, 118), angle=-np.radians(64), color=GREY_B, stroke_width=3),
        )
        clab = T("controller", 26, GREY_B).move_to(c + DOWN * 2.05)
        self.beat("Between them sits a small program called a controller. It runs the same loop, forever.",
                  LaggedStart(Create(arcs), *[AnimationGroup(Create(b[0]), Write(b[1])) for b in (read, look, act)], lag_ratio=0.2), FadeIn(clab), run_time=2.4)
        loop = VGroup(arcs, read, look, act)

        def light(b, on=True):
            return b[0].animate.set_stroke(width=6 if on else 3)

        self.beat("Read the desired state.", light(read), Indicate(want[1], color=YELLOW_M), run_time=1.0)
        self.beat("Observe the actual state.", light(read, False), light(look), Indicate(count, color=TEAL_M), run_time=1.0)
        self.beat("If the two differ, act to make them match. Then repeat.", light(look, False), light(act), run_time=1.0)
        self.play(light(act, False), Rotate(arcs, angle=-TAU, about_point=c), run_time=1.6)

        # 5. someone deletes a copy: the loop closes the gap
        gone = pods[2]
        self.beat("Say someone deletes one copy by mistake.",
                  gone.animate.set_stroke(RED_M).set_fill(BLACK).scale(0.6).set_opacity(0.2),
                  Transform(count, T("running: 2", 26, RED_M).move_to(count)), run_time=1.4)
        gap = T("3 wanted, 2 running", 26, YELLOW_M).move_to(UP * 3.0)
        self.beat("On its next pass, the loop reads three wanted, and counts two running.",
                  light(read), light(look), FadeIn(gap, shift=DOWN * 0.15), run_time=1.6)
        new = pod().move_to(gone)
        self.beat("So it starts one more. Nobody wrote a script for that case.",
                  light(read, False), light(look, False), light(act), FadeOut(gone), GrowFromCenter(new),
                  Transform(count, T("running: 3", 26, TEAL_M).move_to(count)), FadeOut(gap), run_time=1.8)
        pods = VGroup(pods[0], pods[1], new)
        self.play(light(act, False), run_time=0.4)

        # 6. you change the wish: the same loop does the work
        self.beat("Now you change your wish. Three copies becomes five.",
                  Transform(want[1], M("replicas: 5", 21, YELLOW_M).move_to(want[1], aligned_edge=LEFT)), run_time=1.2)
        more = VGroup(pod(), pod())
        target = VGroup(*[pod() for _ in range(5)]).arrange(RIGHT, buff=0.18).scale(0.8).move_to(node)
        self.beat("The loop sees five wanted and three running, and acts again.",
                  light(read), light(look), light(act), run_time=1.0)
        more[0].move_to(target[3]).scale(0.8); more[1].move_to(target[4]).scale(0.8)
        self.beat("Two more copies start. You never said how. You only said what.",
                  *[pods[i].animate.move_to(target[i]).scale(0.8) for i in range(3)],
                  LaggedStart(GrowFromCenter(more[0]), GrowFromCenter(more[1]), lag_ratio=0.3),
                  Transform(count, T("running: 5", 26, TEAL_M).move_to(count)), run_time=1.8)
        self.play(light(read, False), light(look, False), light(act, False), run_time=0.4)

        # 7. thermostat
        thermo = T("like a thermostat: you set 21 degrees, it keeps checking the room", 26, GREY_B).to_edge(DOWN, buff=0.35)
        self.beat("The Kubernetes docs compare it to a thermostat. You set twenty-one degrees, and it keeps reading the room. You never tell it to heat for ten minutes.",
                  FadeIn(thermo, shift=UP * 0.15), Rotate(arcs, angle=-TAU, about_point=c), run_time=3.0)

        # 8. recap
        spec = T("desired state = spec", 28, BLUE_M).move_to(dlab)
        status = T("actual state = status", 28, TEAL_M).move_to(nlab)
        self.beat("In every object you write, spec is your wish, and status is Kubernetes' report. Controllers work, all the time, to make status match spec.",
                  FadeOut(thermo), Transform(dlab, spec), Transform(nlab, status), run_time=2.4)
        self.wait(1.0)
