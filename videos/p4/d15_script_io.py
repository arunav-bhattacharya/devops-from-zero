import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\blogsum\.py\b", "log sum dot pie"), (r"\blogsum\b", "log sum"), (r"\bLOGSUM_MAX_ERROR_RATE\b", "log sum max error rate"),
            (r"--max-error-rate\b", "max error rate"), (r"--format json\b", "format jay-son"), (r"\bargparse\b", "arg parse"),
            (r"\bsys\.argv\b", "sys dot arg V"), (r"\bjq\b", "J Q"), (r"\bsystemd\b", "system D"), (r"\b5xx\b", "five hundreds"),
            (r"\bnope\.log\b", "nope dot log"), (r"\bexcept Exception: pass\b", "except exception, pass")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def port(label, color, w=2.6, h=0.62, size=24):
    r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.2), opacity=1)
    return VGroup(r, T(label, size).move_to(r))


class D15ScriptIo(VoiceScene):
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
        self.title_card("What a script takes in, and what it hands back", "arguments, environment and files in; stdout, stderr and an exit code out")

        # 0. the problem: CI reads one number
        ci = box("CI job", GREY_B, w=2.2, h=0.8, size=26).move_to([-3.2, 0.6, 0])
        sc = mbox("logsum.py", WHITE, size=26, w=2.6, h=0.8).move_to([2.0, 0.6, 0])
        ca = edge_arrow(ci, sc)
        self.beat("A CI job runs your script on every push. It cannot read the messages your script prints.",
                  FadeIn(ci), GrowArrow(ca), FadeIn(sc), run_time=2.0)
        num = M("1", 40, RED_M).next_to(sc, DOWN, buff=0.5)
        back = CurvedArrow(sc.get_bottom() + DOWN * 0.1 + LEFT * 0.5, ci.get_bottom() + DOWN * 0.1, angle=-PI / 3, color=RED_M, stroke_width=3)
        who = T("CI, systemd, cron, Kubernetes probes", 24, GREY_B).move_to([0, 2.6, 0])
        self.steps("It looks at one number, the exit code. So do systemd, cron, and Kubernetes probes. They decide success or failure from the exit code alone.",
                   (0.8, FadeIn(num, scale=0.6)), (1.0, Create(back)), (0.6, ci[0].animate.set_stroke(RED_M)), (1.4, Wait(1.4)), (0.8, FadeIn(who)))
        self.play(FadeOut(VGroup(ci, ca, num, back, who)), run_time=0.5)

        # 1. the box: three ins, three outs
        core_r = RoundedRectangle(corner_radius=0.15, width=2.9, height=2.6, stroke_color=WHITE, stroke_width=3).set_fill(BLACK, opacity=1).move_to([0, 0.2, 0])
        core_t = VGroup(M("logsum.py", 26), M("main(argv) -> int", 20, GREY_B)).arrange(DOWN, buff=0.2).move_to(core_r.get_center() + UP * 0.45)
        lim = M("limit 1.0%", 22, YELLOW_M).move_to(core_r.get_center() + DOWN * 0.6)
        self.beat("So picture the script as a box. Things come in on the left, and results leave on the right.",
                  Transform(sc, VGroup(core_r, core_t)), run_time=1.6)
        core = sc
        Ys = (1.9, 0.2, -1.5)
        ins = VGroup(port("arguments", BLUE_M), port("environment", TEAL_M), port("file", GOLD_M)).move_to([-4.75, 0, 0])
        for p, y in zip(ins, Ys):
            p.move_to([-4.75, y, 0])
        outs = VGroup(port("stdout", WHITE), port("stderr", RED_M), port("exit code", YELLOW_M))
        for p, y in zip(outs, Ys):
            p.move_to([4.75, y, 0])
        ia = VGroup(*[Arrow(p.get_right(), core_r.get_left() + UP * (y - 0.2) * 0.45, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12) for p, y in zip(ins, Ys)])
        oa = VGroup(*[Arrow(core_r.get_right() + UP * (y - 0.2) * 0.45, p.get_left(), buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.12) for p, y in zip(outs, Ys)])
        self.beat("Inputs come from three places: arguments, environment variables, and files.",
                  LaggedStart(*[AnimationGroup(FadeIn(p, shift=RIGHT * 0.15), GrowArrow(a)) for p, a in zip(ins, ia)], lag_ratio=0.35), run_time=2.6)
        self.beat("And results leave on three separate channels: stdout, stderr, and the exit code.",
                  LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(p, shift=RIGHT * 0.15)) for p, a in zip(outs, oa)], lag_ratio=0.35), run_time=2.6)

        # 2. inputs in detail
        d_arg = M("--max-error-rate 5", 20, BLUE_M).next_to(ins[0], DOWN, buff=0.15)
        d_env = M("LOGSUM_MAX_ERROR_RATE=5", 20, TEAL_M).next_to(ins[1], DOWN, buff=0.15)
        d_fil = M("access.log", 20, GOLD_M).next_to(ins[2], DOWN, buff=0.15)
        self.beat("argparse turns the words of the command line into named values. Like the limit, max error rate.",
                  FadeIn(d_arg, shift=DOWN * 0.1), run_time=1.8)
        self.beat("The same setting can also come from an environment variable.",
                  FadeIn(d_env, shift=DOWN * 0.1), run_time=1.4)
        lad = VGroup(chip("flag", BLUE_M, 24), T(">", 28), chip("variable", TEAL_M, 24), T(">", 28), chip("built-in 1.0", GREY_B, 24)).arrange(RIGHT, buff=0.3)
        lad.move_to([0, -2.95, 0])
        self.steps("So which one wins? argparse uses a default only when the flag is missing. So a flag beats the variable, and the variable beats the built-in 1.0.",
                   (0.6, FadeIn(lad[0]), FadeIn(lad[2]), FadeIn(lad[4])), (2.2, Wait(2.2)), (0.6, FadeIn(lad[1]), Indicate(lad[0], color=BLUE_M)),
                   (0.8, Wait(0.8)), (0.6, FadeIn(lad[3]), Indicate(lad[2], color=TEAL_M)))
        self.play(FadeOut(lad), FadeOut(d_arg), FadeOut(d_env), run_time=0.5)
        self.beat("The file is the access log, with 238 requests in it.",
                  FadeIn(d_fil, shift=DOWN * 0.1), travel(ia[2], GOLD_M, 1.0), run_time=1.6)

        # 3. run 1: above the limit
        cmd = M("$ uv run scripts/logsum.py access access.log", 22, GREY_B).move_to([0, 3.3, 0])
        self.beat("Run it with no limit given. The default is 1 percent.",
                  FadeIn(cmd), FadeIn(lim), Indicate(lim, color=YELLOW_M), run_time=1.8)
        rep = M("238 requests ... 5xx 11 ... error rate 4.6%", 20, WHITE).move_to([0, -2.6, 0])
        err = M("logsum: ERROR error rate 4.6% is above the limit of 1.0%", 20, RED_M).move_to([0, -3.15, 0])
        fit(err, 12.8)
        self.steps("It counts 11 server errors out of 238 requests. That is 4.6 percent.",
                   (1.0, travel(ia[2], GOLD_M, 1.0)), (0.8, Indicate(core_r, color=WHITE, scale_factor=1.03)))
        self.steps("The report goes to stdout, the only stream a pipe passes on.",
                   (0.8, travel(oa[0], WHITE, 0.8)), (0.8, FadeIn(rep, shift=UP * 0.1)))
        self.steps("The reason it failed goes to stderr, in one line for people.",
                   (0.8, travel(oa[1], RED_M, 0.8)), (0.8, FadeIn(err, shift=UP * 0.1)))
        ec = M("1", 36, RED_M).next_to(outs[2], DOWN, buff=0.15)
        self.steps("And 4.6 is above the 1 percent limit, so the exit code is 1. The CI job turns red. You wrote no extra code for that.",
                   (0.8, travel(oa[2], YELLOW_M, 0.8)), (0.8, FadeIn(ec, scale=0.6)), (1.4, Wait(1.4)), (0.8, Indicate(ec, color=RED_M)))

        # 4. run 2: pass, json, pipe
        cmd2 = M("$ uv run scripts/logsum.py access access.log --max-error-rate 5", 22, GREY_B).move_to(cmd)
        fit(cmd2, 12.8)
        ec0 = M("0", 36, GREEN_M).move_to(ec)
        lim5 = M("limit 5%", 22, YELLOW_M).move_to(lim)
        self.steps("Raise the limit to 5 with the flag, and the same log passes. Exit code 0.",
                   (0.8, Transform(cmd, cmd2), FadeOut(err), FadeOut(rep)), (0.6, travel(ia[0], BLUE_M, 0.6)), (0.6, Transform(lim, lim5)),
                   (0.8, travel(oa[2], YELLOW_M, 0.8)), (0.6, Transform(ec, ec0)))
        jq = mbox("jq", GREEN_M, size=26, w=1.2, h=0.62).next_to(outs[0], UP, buff=0.35)
        jqa = Arrow(outs[0].get_top(), jq.get_bottom(), buff=0.06, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.3)
        js = M('{"2xx":181,"3xx":16,"4xx":30,"5xx":11}', 20, GREEN_M).move_to([0, -2.6, 0])
        self.steps("With format json, stdout holds only JSON, because every message went to stderr. So you can pipe it into jq, with no cleanup.",
                   (1.2, FadeIn(jq), GrowArrow(jqa)), (0.8, travel(oa[0], WHITE, 0.8)), (0.6, travel(jqa, GREEN_M, 0.6)), (0.8, FadeIn(js, shift=UP * 0.1)))
        self.play(FadeOut(VGroup(jq, jqa, js)), run_time=0.5)

        # 5. the contract: 0, 1, 2
        con = VGroup(
            VGroup(M("0", 30, GREEN_M), T("all good", 24)).arrange(RIGHT, buff=0.35),
            VGroup(M("1", 30, RED_M), T("the check found a problem", 24)).arrange(RIGHT, buff=0.35),
            VGroup(M("2", 30, GOLD_M), T("the script could not do its job", 24)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([0, -2.75, 0])
        self.beat("Every script in the lab keeps one contract. Zero means all good. One means the check found a problem. Two means the script could not do its job.",
                  LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in con], lag_ratio=0.6), run_time=4.4)
        cmd3 = M("$ uv run scripts/logsum.py access nope.log", 22, GREY_B).move_to(cmd)
        e2 = M("2", 36, GOLD_M).move_to(ec)
        nf = M("logsum: ERROR no such file: nope.log", 22, RED_M).move_to([0, 2.7, 0])
        self.steps("Give it a file that is not there. The script catches FileNotFoundError by name, prints one clear line, and returns 2.",
                   (0.8, Transform(cmd, cmd3), Transform(d_fil, M("nope.log", 20, RED_M).move_to(d_fil))), (1.6, Wait(1.6)),
                   (0.8, travel(oa[1], RED_M, 0.8)), (0.6, FadeIn(nf)), (0.6, travel(oa[2], YELLOW_M, 0.6)), (0.6, Transform(ec, e2), Indicate(con[2], color=GOLD_M)))
        self.beat("Now a caller can tell the error rate is too high apart from the log file is missing.",
                  Indicate(con[1], color=RED_M), Succession(Wait(1.6), Indicate(con[2], color=GOLD_M)), run_time=3.0)

        # 6. the mistake
        self.play(FadeOut(VGroup(con, nf)), run_time=0.5)
        bad = M("except Exception: pass", 26, RED_M).move_to(core_r.get_center() + DOWN * 0.6)
        self.beat("Here is the mistake to avoid. Wrap the whole script in except Exception, pass.",
                  FadeOut(lim), FadeIn(bad), run_time=1.6)
        fit(bad, 2.6)
        e0 = M("0", 36, GREEN_M).move_to(ec)
        grn = T("CI goes green, and nothing was checked", 26, RED_M).move_to([0, -2.75, 0])
        self.steps("Now a crash becomes a silent success. The script exits 0, CI goes green, and nothing was checked.",
                   (0.8, Wiggle(core_r)), (0.8, travel(oa[2], YELLOW_M, 0.8)), (0.6, Transform(ec, e0)), (1.0, Wait(1.0)), (0.8, FadeIn(grn, shift=UP * 0.1)))
        fix = T("catch what you expect, by name; let the rest crash", 26, GREEN_M).move_to([0, -3.35, 0])
        self.beat("Catch the errors you expect, by name. Say on stderr what went wrong, return a non-zero code, and let everything else crash with its traceback.",
                  FadeIn(fix, shift=UP * 0.1), run_time=2.0)

        # 7. recap
        self.play(FadeOut(VGroup(grn, fix, bad, cmd)), run_time=0.5)
        rc = T("report on stdout, reasons on stderr, the verdict in the exit code", 26, WHITE).move_to([0, -2.8, 0])
        fit(rc, 12.6)
        self.beat("So: the report goes to stdout, the reasons go to stderr, and the verdict is the exit code. That number is the whole interface for CI.",
                  FadeIn(rc, shift=UP * 0.1), *[Indicate(o, color=WHITE, scale_factor=1.06) for o in outs], run_time=3.6)
        self.wait(1.2)
