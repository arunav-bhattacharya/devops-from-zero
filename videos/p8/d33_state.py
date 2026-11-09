import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"terraform\.tfstate", "terraform dot T F state"), (r"docker_(image|container)\.(\w+)", r"docker \1 dot \2"),
    (r"\bs3cret-123\b", "secret one two three"), (r"\bREDIS_PASSWORD\b", "redis password"), (r"\bjq\b", "J Q"),
    (r"\.tflock\b", "dot T F lock"), (r"\buse_lockfile\b", "use lock file"), (r"\s-refresh-only\b", " refresh only"),
    (r"\bIDs\b", "I Ds"), (r"\bID\b", "I D"),
])

ID_IMG = "sha256:0e52bd05..."
ID_WEB = "d8eb279cfd6e..."
ID_LEG = "b8491ec38963..."


def tint(color, a=0.12):
    return interpolate_color(ManimColor("#000000"), ManimColor(color), a)


def panel(w, h, color=GREY_B, sw=2.5, a=0.08):
    return RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, a), 1)


def code_line(text, size=20, color=WHITE):
    t = M("|" + text, size, color)
    t[0].set_opacity(0)
    return t


def lines(spec, size=20, buff=0.14):
    return VGroup(*[code_line(t, size, c) for t, c in spec]).arrange(DOWN, aligned_edge=LEFT, buff=buff)


def flash(m, color=YELLOW_M, rt=1.2):
    return ShowPassingFlash(m.copy().set_fill(opacity=0).set_stroke(color, 6), time_width=0.6, run_time=rt)


def ctr(color=TEAL_M, r=0.3):
    return Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)


def page(label, color=GOLD_M, w=0.9, h=1.1):
    body = Polygon([-w / 2, h / 2, 0], [w / 2 - 0.25, h / 2, 0], [w / 2, h / 2 - 0.25, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0],
                   stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.15), 1)
    rows = VGroup(*[Line(LEFT * (w / 2 - 0.15), RIGHT * (w / 2 - 0.2), stroke_width=2, color=color) for _ in range(3)]).arrange(DOWN, buff=0.18).move_to(body).shift(DOWN * 0.08)
    lab = M(label, 20, color).next_to(body, DOWN, buff=0.12)
    return VGroup(body, rows, lab)


class D33State(VoiceScene):
    def construct(self):
        self.title_card("Terraform state", "the map from your code to real objects")

        # ---- 1. the map: address -> real ID
        sp = panel(7.6, 3.0, GOLD_M, 2.5, 0.06).move_to([-2.65, 0.2, 0])
        stitle = M("terraform.tfstate", 24, GOLD_M).next_to(sp, UP, buff=0.18).align_to(sp, LEFT)
        self.beat("Terraform keeps a memory of what it made. It is a JSON file called terraform.tfstate.",
                  Create(sp), Write(stitle), run_time=2.4)
        AX, IX = -6.15, -2.0
        hA = T("address", 26, GREY_B).move_to([AX, 1.2, 0], aligned_edge=LEFT)
        hI = T("real ID", 26, GREY_B).move_to([IX, 1.2, 0], aligned_edge=LEFT)
        rule = Line([-6.2, 0.85, 0], [0.9, 0.85, 0], stroke_width=1.5, color=GREY_D)
        r1 = VGroup(M("docker_image.nginx", 22, BLUE_M).move_to([AX, 0.3, 0], aligned_edge=LEFT), M(ID_IMG, 22).move_to([IX, 0.3, 0], aligned_edge=LEFT))
        r2 = VGroup(M("docker_container.web", 22, BLUE_M).move_to([AX, -0.5, 0], aligned_edge=LEFT), M(ID_WEB, 22).move_to([IX, -0.5, 0], aligned_edge=LEFT))
        arrs = VGroup(*[Arrow(r[0].get_right(), r[1].get_left(), buff=0.12, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.2) for r in (r1, r2)])
        self.beat("Its main job is a map. On the left, an address from your code. On the right, the real ID of the object it points to.",
                  FadeIn(hA), FadeIn(hI), Create(rule),
                  Succession(Wait(1.2), LaggedStart(FadeIn(r1[0]), FadeIn(r2[0]), lag_ratio=0.3), Wait(1.0), LaggedStart(GrowArrow(arrs[0]), FadeIn(r1[1]), GrowArrow(arrs[1]), FadeIn(r2[1]), lag_ratio=0.3)),
                  run_time=6.0)

        dp = panel(4.3, 3.0, TEAL_M, 2.5, 0.06).move_to([4.4, 0.2, 0])
        dtitle = T("Docker", 26, TEAL_M).next_to(dp, UP, buff=0.18).align_to(dp, LEFT)
        web = ctr().move_to([4.4, 0.75, 0])
        webl = M("state-web", 20, TEAL_M).next_to(web, DOWN, buff=0.15)
        lk = DashedLine(r2[1].get_right() + RIGHT * 0.1, web.get_left() + LEFT * 0.1, dash_length=0.08, stroke_width=2, color=GOLD_M)
        self.beat("So docker_container.web is the container with this ID, over in Docker.",
                  Create(dp), FadeIn(dtitle), GrowFromCenter(web), FadeIn(webl), Succession(Wait(1.0), Create(lk)), run_time=3.0)
        self.play(travel(Line(lk.get_start(), lk.get_end()), GOLD_M, 0.8), run_time=0.9)

        others = VGroup(ctr(GREY_B, 0.26).move_to([3.35, -0.4, 0]), ctr(GREY_B, 0.26).move_to([5.45, -0.4, 0]))
        q = VGroup(*[T("?", 28, GREY_B).move_to(o) for o in others])
        oth_l = VGroup(T("teammate's?", 20, GREY_B).next_to(others[0], DOWN, buff=0.1), T("other folder's?", 20, GREY_B).next_to(others[1], DOWN, buff=0.1))
        self.beat("Why not just ask Docker which containers exist? Because Docker cannot tell which ones this folder owns.",
                  LaggedStart(*[GrowFromCenter(o) for o in others], lag_ratio=0.3), FadeIn(q), FadeIn(oth_l), run_time=3.0)
        own = T("this folder owns it", 22, GOLD_M).move_to([4.4, 1.42, 0])
        self.beat("State is the list of what this folder owns, with the ID of each.",
                  flash(SurroundingRectangle(r2, buff=0.12), GOLD_M), web.animate.set_stroke(GOLD_M, 5),
                  FadeIn(own, shift=DOWN * 0.1), others.animate.set_opacity(0.35), q.animate.set_opacity(0.35), oth_l.animate.set_opacity(0.35), run_time=2.6)
        self.play(FadeOut(VGroup(dp, dtitle, web, webl, lk, others, q, oth_l, own, hA, hI, rule, r1, r2, arrs)), run_time=0.6)

        # ---- 2. what is inside, and the secret
        js = lines([("{", WHITE), ('  "version": 4,', WHITE), ('  "terraform_version": "1.17.1",', WHITE), ('  "serial": 3,', WHITE),
                    ('  "lineage": "3a40a665-d793-...",', WHITE), ('  "resources": [ ... ]', WHITE), ("}", WHITE)], 22, 0.12)
        js.move_to(sp).align_to(sp, LEFT).shift(RIGHT * 0.45)
        cmd = M("$ jq . terraform.tfstate", 20, YELLOW_M).move_to([-2.65, -1.75, 0]).align_to(sp, LEFT)
        self.beat("Open it with jq, and you find a few top-level keys.",
                  FadeIn(cmd), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in js], lag_ratio=0.12), run_time=2.4)
        notes = [("file format", 1), ("Terraform that last wrote it", 2), ("times written", 3), ("ID from when it was created", 4), ("every attribute, of every resource", 5)]
        nt = VGroup(*[T(t, 24, GREY_B).move_to([2.0, js[i].get_y(), 0], aligned_edge=LEFT) for t, i in notes])
        self.beat("version is the file format. serial counts how many times this state was written. lineage is an ID given when the state was first created.",
                  Succession(FadeIn(nt[0], shift=LEFT * 0.1), Wait(0.5), FadeIn(nt[1], shift=LEFT * 0.1), Wait(1.4), FadeIn(nt[2], shift=LEFT * 0.1), Wait(1.6), FadeIn(nt[3], shift=LEFT * 0.1)),
                  run_time=7.0)
        self.beat("And resources holds every resource, with every attribute the provider reported.",
                  FadeIn(nt[4], shift=LEFT * 0.1), Indicate(js[5], color=GOLD_M, scale_factor=1.03), run_time=2.4)

        sec = lines([("{", WHITE), ('  "resources": [{', WHITE), ('    "type": "docker_container",', WHITE), ('    "env": ["REDIS_PASSWORD=s3cret-123"],', RED_M),
                     ("  }]", WHITE), ("}", WHITE)], 22, 0.12)
        sec.move_to(sp).align_to(sp, LEFT).shift(RIGHT * 0.45)
        self.beat("Those attributes include secrets.",
                  FadeOut(nt), FadeOut(js), FadeOut(cmd), Succession(Wait(0.5), LaggedStart(*[FadeIn(l, shift=DOWN * 0.05) for l in sec], lag_ratio=0.1)), run_time=1.6)
        var = VGroup(M('variable "redis_password"', 22, BLUE_M), M("  sensitive = true", 22, BLUE_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        hidden = VGroup(VGroup(T("plan and apply:", 24, GREY_B), M("(sensitive value)", 22)).arrange(RIGHT, buff=0.25),
                        VGroup(T("terraform output:", 24, GREY_B), M("<sensitive>", 22)).arrange(RIGHT, buff=0.25)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        top = VGroup(var, hidden).arrange(RIGHT, buff=1.2).to_edge(UP, buff=0.4)
        self.beat("In a test, a variable marked sensitive went into a container as REDIS_PASSWORD equals s3cret-123. Plan and apply printed sensitive value. terraform output printed sensitive.",
                  FadeIn(var), Succession(Wait(4.0), FadeIn(hidden[0], shift=LEFT * 0.1), Wait(1.0), FadeIn(hidden[1], shift=LEFT * 0.1)), run_time=8.0)
        plain = T("in plain text", 30, RED_M).move_to([4.2, -1.0, 0])
        pa = Arrow(plain.get_left(), sec[3].get_right(), buff=0.15, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.15)
        self.beat("But the state file held it in plain text. Anyone who can read your state can read your secrets.",
                  Indicate(sec[3], color=RED_M, scale_factor=1.04), FadeIn(plain), GrowArrow(pa), run_time=3.0)
        self.play(FadeOut(VGroup(var, hidden, sec, plain, pa)), run_time=0.6)

        rules = VGroup(VGroup(tick(False, 0.16), T("never commit it", 28)).arrange(RIGHT, buff=0.3),
                       VGroup(tick(False, 0.16), T("never edit it by hand", 28)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        cmds = VGroup(M("terraform state list", 22, YELLOW_M), M("terraform state show ADDRESS", 22, YELLOW_M), M("terraform show", 22, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rules.move_to(sp).align_to(sp, LEFT).shift(RIGHT * 0.5 + UP * 0.55)
        cmds.next_to(rules, DOWN, buff=0.45, aligned_edge=LEFT)
        pw = T("treat it like a password file", 26, GOLD_M).move_to([3.9, 0.2, 0])
        self.beat("So treat the file like a password file. Never commit it, and never edit it by hand. Read it through commands instead.",
                  FadeIn(pw), Succession(Wait(1.8), FadeIn(rules[0], shift=RIGHT * 0.1), Wait(0.6), FadeIn(rules[1], shift=RIGHT * 0.1), Wait(0.8),
                                         LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in cmds], lag_ratio=0.3)), run_time=6.6)
        self.play(FadeOut(VGroup(sp, stitle, rules, cmds, pw)), run_time=0.6)

        # ---- 3. where state lives in a team: backend and lock
        you = box("you", BLUE_M, w=2.0, h=0.7).move_to([-4.6, 1.9, 0])
        mate = box("teammate", PURPLE_M, w=2.0, h=0.7).move_to([-4.6, -1.5, 0])
        f1 = page("serial 3").next_to(you, RIGHT, buff=0.5)
        f2 = page("serial 5").next_to(mate, RIGHT, buff=0.5)
        self.beat("By default, state is a local file. That breaks as soon as a second person, or a pipeline, runs Terraform.",
                  FadeIn(you), FadeIn(f1, shift=LEFT * 0.1), Succession(Wait(2.4), AnimationGroup(FadeIn(mate), FadeIn(f2, shift=LEFT * 0.1))), run_time=5.0)
        apart = T("two copies drift apart", 26, RED_M).move_to([-2.4, 0.2, 0])
        self.beat("Two copies drift apart, and nothing stops two applies from running at once.",
                  FadeIn(apart), Indicate(f1[2], color=RED_M), Indicate(f2[2], color=RED_M), run_time=2.6)

        bucket = panel(3.2, 2.4, GOLD_M, 2.5, 0.08).move_to([3.0, 0.2, 0])
        bl = T("remote backend", 26, GOLD_M).next_to(bucket, UP, buff=0.15)
        bsub = M("S3 bucket", 20, GREY_B).next_to(bucket, DOWN, buff=0.15)
        one = page("terraform.tfstate").move_to(bucket).shift(UP * 0.15)
        pipe = box("pipeline", GREY_B, w=2.0, h=0.7).move_to([-4.6, 0.2, 0])
        la = VGroup(*[Arrow(b.get_right(), bucket.get_left() + UP * dy, buff=0.15, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.06)
                      for b, dy in ((you, 0.7), (pipe, 0), (mate, -0.7))])
        self.beat("A backend decides where state is stored. A remote backend keeps one copy that everyone uses.",
                  FadeOut(apart), Create(bucket), FadeIn(bl), FadeIn(bsub),
                  Succession(Wait(1.6), AnimationGroup(ReplacementTransform(VGroup(f1, f2), one), FadeIn(pipe), LaggedStart(*[GrowArrow(a) for a in la], lag_ratio=0.2))),
                  run_time=5.0)
        lockf = chip(".tflock", BLUE_M, 22, mono=True).next_to(bucket, RIGHT, buff=0.3)
        run1 = M("apply", 22, BLUE_M).next_to(you, UP, buff=0.15)
        self.beat("Most backends also lock it, so only one run at a time can change the state.",
                  FadeIn(run1), la[0].animate.set_color(BLUE_M), Succession(Wait(1.2), FadeIn(lockf, shift=LEFT * 0.15)), run_time=2.8)
        self.play(travel(Line(la[0].get_start(), la[0].get_end()), BLUE_M, 0.8), run_time=0.9)
        run2 = M("plan", 22, PURPLE_M).next_to(mate, DOWN, buff=0.15)
        err = M("Error: Error acquiring the state lock", 22, RED_M).move_to([0.6, -3.05, 0])
        xx = tick(False, 0.18).move_to(la[2].get_center())
        self.beat("Start an apply in one terminal, and a plan in another. The second stops with: Error acquiring the state lock.",
                  FadeIn(run2), la[2].animate.set_color(RED_M), Succession(Wait(2.6), AnimationGroup(Create(xx), FadeIn(err, shift=UP * 0.1))), run_time=5.0)
        s3 = VGroup(M("use_lockfile = true", 22, YELLOW_M), T("+ bucket versioning", 24, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        s3.move_to([0, -1.95, 0]).align_to([6.5, 0, 0], RIGHT)
        self.beat("On S3, use_lockfile set to true keeps that small .tflock file next to the state, while a run holds the lock. And bucket versioning lets you roll back a bad write.",
                  FadeIn(s3[0], shift=UP * 0.1), Indicate(lockf, color=BLUE_M), Succession(Wait(4.6), FadeIn(s3[1], shift=UP * 0.1)), run_time=7.5)
        self.play(FadeOut(VGroup(you, mate, pipe, la, bucket, bl, bsub, one, lockf, run1, run2, err, xx, s3)), run_time=0.6)

        # ---- 4. drift and refresh-only
        CX = [-4.5, 0.0, 4.5]
        cols = [panel(3.8, 2.2, c, 2.5, 0.06).move_to([x, 1.15, 0]) for c, x in zip((BLUE_M, GOLD_M, TEAL_M), CX)]
        heads = [T(t, 26, c).next_to(p, UP, buff=0.15) for t, c, p in zip(("your code", "the state", "Docker"), (BLUE_M, GOLD_M, TEAL_M), cols)]
        vals = [M('restart = "no"', 22).move_to(cols[0]), M('restart = "no"', 22).move_to(cols[1]), M("restart: no", 22).move_to(cols[2])]
        self.beat("Now drift. Drift is any difference between the real world and Terraform's state, usually from a change made by hand.",
                  *[Create(c) for c in cols], *[FadeIn(h) for h in heads], Succession(Wait(1.2), LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.3)), run_time=4.6)
        hand = M("$ docker update --restart=always state-web", 22, YELLOW_M).move_to([0, -0.55, 0])
        v2 = M("restart: always", 22, YELLOW_M).move_to(cols[2])
        self.beat("Someone runs docker update by hand, and sets restart to always.",
                  FadeIn(hand, shift=UP * 0.1), Succession(Wait(1.4), Transform(vals[2], v2)), run_time=3.0)
        pp = panel(12.6, 1.6, GREY_B, 2, 0.05).move_to([0, -2.45, 0])
        pl = M("$ terraform plan -refresh-only", 22, GREY_B).move_to(pp.get_corner(UL) + DR * 0.35, aligned_edge=UL)
        pr = M('~ restart = "no" -> "always"       (no actions)', 22, YELLOW_M).next_to(pl, DOWN, buff=0.2, aligned_edge=LEFT)
        self.beat("plan -refresh-only shows only the changes made outside Terraform. It proposes no actions.",
                  FadeOut(hand), Create(pp), FadeIn(pl), Succession(Wait(1.4), FadeIn(pr, shift=RIGHT * 0.1)), run_time=3.6)
        al = M("$ terraform apply -refresh-only", 22, GREY_B).move_to(pl, aligned_edge=LEFT)
        v1 = M('restart = "always"', 22, YELLOW_M).move_to(cols[1])
        nochange = T("no real object changes", 24, GREY_B).next_to(cols[2], DOWN, buff=0.25)
        self.beat("apply -refresh-only writes those changes into the state. It changes no real object.",
                  Transform(pl, al), FadeOut(pr), Succession(Wait(1.2), Transform(vals[1], v1)), FadeIn(nochange), run_time=3.4)
        np2 = M("$ terraform plan", 22, GREY_B).move_to(pl, aligned_edge=LEFT)
        back = M('~ restart = "always" -> "no"       Plan: 0 to add, 1 to change, 0 to destroy.', 22, GOLD_M).next_to(pl, DOWN, buff=0.2, aligned_edge=LEFT)
        fit(back, 12.0)
        self.beat("People expect that to make the change permanent. It does not. The code still says no, so the next normal plan wants to put no back.",
                  FadeOut(nochange), Transform(pl, np2), Succession(Wait(3.0), AnimationGroup(flash(cols[0], BLUE_M), Indicate(vals[0], color=BLUE_M))),
                  Succession(Wait(5.0), FadeIn(back, shift=RIGHT * 0.1)), run_time=7.0)
        wins = T("the code still wins", 26, BLUE_M).next_to(cols[0], DOWN, buff=0.25)
        self.play(FadeIn(wins, shift=UP * 0.1), run_time=0.6)
        self.beat("So after drift, you decide which side is right. If the code is right, run a normal apply, and Terraform undoes the manual change. If reality is right, change the code to match, then apply.",
                  FadeOut(VGroup(pp, pl, back)),
                  Succession(Wait(3.0), AnimationGroup(Transform(vals[2], M("restart: no", 22, WHITE).move_to(cols[2])), Transform(vals[1], M('restart = "no"', 22).move_to(cols[1]))),
                             Wait(3.0), AnimationGroup(Transform(vals[0], M('restart = "always"', 22, YELLOW_M).move_to(cols[0])), Transform(vals[1], M('restart = "always"', 22, YELLOW_M).move_to(cols[1])),
                                                       Transform(vals[2], M("restart: always", 22, YELLOW_M).move_to(cols[2])))),
                  run_time=10.0)
        self.play(FadeOut(VGroup(*cols, *heads, *vals, wins)), run_time=0.6)

        # ---- 5. moved: rename without rebuilding
        code = M('resource "docker_container" "web" {', 24).move_to([0, 2.95, 0])
        sp = panel(9.6, 1.5, GOLD_M, 2.5, 0.06).move_to([-1.75, 1.05, 0])
        stl = T("the state", 24, GOLD_M).next_to(sp, UP, buff=0.12).align_to(sp, LEFT)
        row = VGroup(M("docker_container.web", 22, BLUE_M), M(ID_WEB, 22)).arrange(RIGHT, buff=1.2).move_to(sp)
        rarr = Arrow(row[0].get_right(), row[1].get_left(), buff=0.12, stroke_width=2.5, color=GREY_B, max_tip_length_to_length_ratio=0.2)
        web = ctr().move_to([5.4, 1.05, 0])
        webl = M("state-web", 20, TEAL_M).next_to(web, DOWN, buff=0.12)
        lk = DashedLine(sp.get_right() + RIGHT * 0.05, web.get_left() + LEFT * 0.1, dash_length=0.08, stroke_width=2, color=GOLD_M)
        self.beat("Back to the map. Your code has a container resource labelled web, and the state maps that address to the real container.",
                  FadeIn(code, shift=DOWN * 0.1), Create(sp), FadeIn(stl), FadeIn(row), GrowArrow(rarr), GrowFromCenter(web), FadeIn(webl), Create(lk), run_time=4.0)
        code2 = M('resource "docker_container" "site" {', 24).move_to(code)
        code2[-7:-2].set_color(YELLOW_M)
        self.beat("Rename the label, from web to site.", Transform(code, code2), run_time=1.6)
        pp = panel(12.6, 1.9, GREY_B, 2, 0.05).move_to([0, -2.25, 0])
        pa = lines([("# docker_container.site will be created", GREEN_M), ("# docker_container.web will be destroyed", RED_M),
                    ("Plan: 1 to add, 0 to change, 1 to destroy.", WHITE)], 22, 0.14).move_to(pp).align_to(pp, LEFT).shift(RIGHT * 0.4)
        self.beat("To Terraform, you deleted one resource and wrote a new one. The plan wants to destroy the container, and build a new one, to change a name only you can see.",
                  Create(pp), Succession(Wait(1.4), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in pa], lag_ratio=0.4)),
                  Succession(Wait(4.0), web.animate.set_stroke(RED_M)), run_time=6.4)
        mv = lines([("moved {", WHITE), ("  from = docker_container.web", WHITE), ("  to   = docker_container.site", YELLOW_M), ("}", WHITE)], 22, 0.1)
        mvp = panel(mv.width + 0.6, mv.height + 0.4, YELLOW_M, 2, 0.06)
        mv.move_to(mvp)
        mvg = VGroup(mvp, mv).move_to([0, -0.95, 0])
        self.beat("A moved block fixes that. From docker_container.web, to docker_container.site.",
                  FadeOut(VGroup(pp, pa)), web.animate.set_stroke(TEAL_M), FadeIn(mvg, shift=UP * 0.1), run_time=2.2)
        self.play(mvg.animate.move_to([3.4, -0.7, 0]), run_time=0.6)
        pp2 = panel(12.6, 1.5, GREY_B, 2, 0.05).move_to([0, -2.75, 0])
        pb = lines([("# docker_container.web has moved to docker_container.site", TEAL_M), ("Plan: 0 to add, 0 to change, 0 to destroy.", WHITE)], 22, 0.14)
        pb.move_to(pp2).align_to(pp2, LEFT).shift(RIGHT * 0.4)
        row2 = M("docker_container.site", 22, BLUE_M).move_to(row[0], aligned_edge=RIGHT)
        self.beat("Now the plan says web has moved to site. Zero to add, zero to change, zero to destroy.",
                  Create(pp2), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in pb], lag_ratio=0.5), run_time=3.4)
        self.beat("Apply, and the state uses the new address. Same container, same ID.",
                  Transform(row[0], row2), Succession(Wait(1.6), AnimationGroup(Indicate(row[1], color=TEAL_M), flash(web, TEAL_M))), run_time=3.2)
        self.play(FadeOut(VGroup(code, sp, stl, row, rarr, web, webl, lk, mvg, pp2, pb)), run_time=0.6)

        # ---- 6. import: adopt what already exists
        dp = panel(3.6, 2.2, TEAL_M, 2.5, 0.06).move_to([-4.6, 1.75, 0])
        dtl = T("Docker", 26, TEAL_M).next_to(dp, UP, buff=0.15)
        leg = ctr().move_to(dp).shift(UP * 0.25)
        legl = M("state-legacy", 20, TEAL_M).next_to(leg, DOWN, buff=0.15)
        hand = T("started by hand", 22, GREY_B).next_to(legl, DOWN, buff=0.1)
        sp = panel(4.0, 2.2, GOLD_M, 2.5, 0.06).move_to([4.45, 1.75, 0])
        stl = T("the state", 26, GOLD_M).next_to(sp, UP, buff=0.15)
        unknown = T("no row for it", 24, GREY_B).move_to(sp)
        self.beat("Sometimes the real object comes first. Someone started a container by hand, called state-legacy. The state does not know it.",
                  Create(dp), FadeIn(dtl), GrowFromCenter(leg), FadeIn(legl), FadeIn(hand), Succession(Wait(3.0), AnimationGroup(Create(sp), FadeIn(stl), FadeIn(unknown))), run_time=5.6)
        im = lines([("import {", WHITE), ("  to = docker_container.legacy", BLUE_M), ('  id = "' + ID_LEG + '"', TEAL_M), ("}", WHITE)], 20, 0.1)
        imp = panel(im.width + 0.5, im.height + 0.4, YELLOW_M, 2, 0.06)
        im.move_to(imp)
        img = VGroup(imp, im).move_to([0, -0.2, 0])
        a1 = Arrow(dp.get_bottom() + RIGHT * 0.7, imp.get_left() + UP * 0.15, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        a2 = Arrow(imp.get_right() + UP * 0.15, sp.get_bottom() + LEFT * 0.7, buff=0.12, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.15)
        self.beat("An import block adopts it. It takes two arguments. to is the address it should get.",
                  Succession(AnimationGroup(FadeIn(img, shift=UP * 0.1), GrowArrow(a1), GrowArrow(a2)), Wait(1.0), Indicate(im[1], color=BLUE_M, scale_factor=1.04)), run_time=4.4)
        insp = M("docker inspect -f '{{.Id}}' state-legacy", 20, GREY_B).next_to(img, DOWN, buff=0.25)
        self.beat("id is the provider's ID for it. For a Docker container, the full ID from docker inspect. A name does not work.",
                  Indicate(im[2], color=TEAL_M, scale_factor=1.04), FadeIn(insp, shift=UP * 0.1), run_time=3.6)
        pp = panel(12.6, 1.9, GREY_B, 2, 0.05).move_to([0, -2.65, 0])
        pa = lines([("# docker_container.legacy must be replaced", GOLD_M), ("# Warning: this will destroy the imported resource", RED_M),
                    ("Plan: 1 to import, 1 to add, 0 to change, 1 to destroy.", WHITE)], 22, 0.14).move_to(pp).align_to(pp, LEFT).shift(RIGHT * 0.4)
        self.beat("You also write the matching resource block yourself, then plan. Read that plan with care. If your block differs from the real object, the plan imports it, and then replaces it.",
                  FadeOut(insp), Create(pp), Succession(Wait(4.6), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in pa], lag_ratio=0.5)),
                  Succession(Wait(7.0), leg.animate.set_stroke(RED_M)), run_time=9.0)
        pb = lines([("# docker_container.legacy will be updated in-place", TEAL_M),
                    ("Plan: 1 to import, 0 to add, 1 to change, 0 to destroy.", WHITE)], 22, 0.14).move_to(pp).align_to(pp, LEFT).shift(RIGHT * 0.4)
        self.beat("So you adjust the code until the plan imports, and destroys nothing.",
                  FadeOut(pa), leg.animate.set_stroke(TEAL_M), Succession(Wait(1.0), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in pb], lag_ratio=0.4)), run_time=3.4)
        nrow = VGroup(M("docker_container.legacy", 20, BLUE_M), M(ID_LEG, 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(sp)
        self.beat("Apply, and the state gains a row, with the container's own ID. Then delete the import block. It has nothing left to do.",
                  Succession(AnimationGroup(travel(Line(a1.get_start(), a1.get_end()), TEAL_M, 0.6)), AnimationGroup(travel(Line(a2.get_start(), a2.get_end()), TEAL_M, 0.6)),
                             AnimationGroup(FadeOut(unknown), FadeIn(nrow, shift=LEFT * 0.1))),
                  Succession(Wait(4.0), AnimationGroup(FadeOut(img), FadeOut(a1), FadeOut(a2))), run_time=6.0)
        self.play(FadeOut(VGroup(dp, dtl, leg, legl, hand, sp, stl, nrow, pp, pb)), run_time=0.6)

        # ---- recap
        rec = VGroup(
            VGroup(T("state", 30, GOLD_M), T("maps each address to a real ID, secrets included", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(T("backend", 30, BLUE_M), T("one remote copy, locked during a run", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(M("-refresh-only", 26, YELLOW_M), T("copies drift into the state; the code still wins", 26, GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(M("moved / import", 26, TEAL_M), T("rename or adopt, in a plan you can read", 26, GREY_B)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN)
        self.beat("State maps each address to a real ID, and it holds secrets, so guard it. Keep it in a locked remote backend. And moved, import and refresh-only each fix one link, in a plan you read before you apply.",
                  LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rec], lag_ratio=0.6), run_time=8.0)
        self.wait(1.0)
