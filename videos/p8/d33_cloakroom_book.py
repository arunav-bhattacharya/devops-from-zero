import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bterraform\.tfstate\b", "terraform dot T F state"), (r"\btfstate\b", "T F state"), (r"\bstate rm\b", "state R M"),
            (r"\bd8eb279c\b", "D 8 E B 2 7 9 C"), (r"\bs3cret-123\b", "secret one two three")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(w, h, color, k=0.08, sw=2.5):
    return RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=sw).set_fill(tint(color, k), opacity=1)


def coat(color=GREEN_M, s=1.0):
    hook = Arc(radius=0.12, start_angle=PI, angle=-PI, stroke_color=GREY_B, stroke_width=3)
    body = Polygon([-0.3, -0.15, 0], [0.3, -0.15, 0], [0.42, -1.0, 0], [-0.42, -1.0, 0], stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), opacity=1)
    return VGroup(hook.move_to([0, -0.05, 0]), body).scale(s)


def cont(name, cid, color=GREEN_M):
    r = RoundedRectangle(corner_radius=0.1, width=2.6, height=0.95, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.22), opacity=1)
    t = VGroup(M(name, 22), M(cid, 22, GREY_B)).arrange(DOWN, buff=0.1).move_to(r)
    return VGroup(r, t)


class D33CloakroomBook(VoiceScene):
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

    def guess(self, where):
        c = chip("pause and guess", YELLOW_M, 24).move_to(where)
        n = T("2", 30, YELLOW_M).next_to(c, RIGHT, buff=0.3)
        self.play(FadeIn(c), FadeIn(n), run_time=0.3)
        self.wait(0.85)
        self.play(Transform(n, T("1", 30, YELLOW_M).move_to(n)), run_time=0.15)
        self.wait(0.85)
        self.play(FadeOut(c), FadeOut(n), run_time=0.3)

    def construct(self):
        self.title_card("The coats are fine. Where is the book?", "Terraform's state, and why it matters")

        # 1. the cloakroom  [FAMILIAR, QUESTION]
        coats = VGroup(*[coat(c) for c in (GREEN_M, TEAL_M, GREEN_M, TEAL_M)]).arrange(RIGHT, buff=0.6).move_to([2.6, 0.6, 0])
        tickets = VGroup(*[T(str(n), 26, GREY_B).next_to(c, DOWN, buff=0.2) for n, c in zip((38, 39, 40, 41), coats)])
        book = panel(3.0, 2.4, GOLD_M, 0.12, 3).move_to([-3.6, 0.4, 0])
        bl = T("the book", 26, GOLD_M).next_to(book, UP, buff=0.2)
        lines = VGroup(*[M(f"{n} -> hook {h}", 22, GOLD_M) for n, h in ((38, 3), (39, 7), (40, 2), (41, 5))]).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(book)
        self.beat("You are looking after the coats at a friend's wedding. Each coat goes on a hook, and you write the ticket number next to the hook in a small book.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in coats], lag_ratio=0.25), FadeIn(tickets),
                  Succession(Wait(2.4), AnimationGroup(Create(book), FadeIn(bl), FadeIn(lines))), run_time=4.4)
        punch = Circle(radius=1.0, stroke_width=0).set_fill(RED_M, opacity=0.5).move_to(book)
        self.beat("Halfway through the evening, the book falls into a bowl of punch.",
                  FadeIn(punch, scale=0.4), lines.animate.set_opacity(0.1), run_time=2.0)
        t41 = chip("ticket 41", YELLOW_M, 26).move_to([2.6, 2.75, 0])
        self.beat("The coats are all still there, safe on their hooks. Then a guest hands you ticket 41. Which coat is hers? No idea.",
                  Indicate(coats, color=GREEN_M, scale_factor=1.03), Succession(Wait(1.8), FadeIn(t41, shift=DOWN * 0.1)), run_time=3.2)
        self.play(FadeOut(VGroup(coats, tickets, book, bl, lines, punch, t41)), run_time=0.6)

        # 2. Terraform's three pictures  [MAP]
        W, H, Y = 4.0, 2.6, 0.75
        cp = panel(W, H, BLUE_M).move_to([-4.45, Y, 0])
        sp = panel(W, H, GOLD_M).move_to([0, Y, 0])
        wp = panel(W, H, GREEN_M).move_to([4.45, Y, 0])
        cl = T("your code", 28, BLUE_M).next_to(cp, UP, buff=0.18)
        sl = T("the state: the book", 28, GOLD_M).next_to(sp, UP, buff=0.18)
        wl = T("the real world: the coats", 28, GREEN_M).next_to(wp, UP, buff=0.18)
        fit(wl, 4.2)
        code = VGroup(M('resource "docker_container"', 22), M('         "web" {', 22), M('  name = "state-web"', 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to(cp)
        fit(code, 3.6)
        rec = VGroup(M("docker_container.web", 22, GOLD_M), M("id d8eb279c...", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(sp)
        c1 = cont("state-web", "d8eb279c...").move_to(wp)
        self.beat("Terraform has the same three things. Your code says what you want. The real world is the containers Docker is running: those are the coats.",
                  Create(cp), FadeIn(cl), FadeIn(code), Create(wp), FadeIn(wl), Succession(Wait(2.8), GrowFromCenter(c1)), run_time=4.4)
        self.beat("And in between is the book: the state, a file called terraform.tfstate.", Create(sp), FadeIn(sl), run_time=2.0)
        self.steps("Its main job is one line per object. This address, docker_container.web, is the container with ID d8eb279c. Ticket, and hook.",
                   (1.0, Wait(1.0)), (0.8, FadeIn(rec[0])), (1.8, Wait(1.8)), (0.8, TransformFromCopy(c1[1][1], rec[1])))
        pathp = ArcBetweenPoints(sp.get_bottom() + RIGHT * 0.8 + DOWN * 0.08, wp.get_bottom() + LEFT * 0.8 + DOWN * 0.08, angle=np.radians(50))
        ask = CurvedArrow(pathp.get_start(), pathp.get_end(), angle=np.radians(50), color=GOLD_M, stroke_width=3)
        self.steps("Every plan begins with a refresh. Terraform asks the provider, the plugin that talks to Docker, about every object in the book. Is d8eb279c still there? Then it compares the book with your code.",
                   (1.4, Wait(1.4)), (0.7, Create(ask)), (0.9, travel(pathp, GOLD_M, 0.9)), (1.8, Wait(1.8)), (0.6, Indicate(c1, color=GREEN_M)),
                   (1.0, Indicate(code, color=BLUE_M, scale_factor=1.03)))

        # 3. why not just ask Docker?  [QUESTION, BREAK]
        q = T("why not just ask Docker what exists?", 30, YELLOW_M).move_to([0, -1.3, 0])
        self.beat("Which raises the question you are probably already thinking. Docker can list every container. Why does Terraform need a book at all?",
                  FadeIn(q), run_time=2.4)
        others = VGroup(cont("hello-web", "a teammate's?", TEAL_M), cont("site-dev", "another folder's?", TEAL_M))
        for o in others:
            fit(o, 2.9)
        others.arrange(RIGHT, buff=0.3).move_to([1.6, -2.65, 0])
        self.beat("Because Docker cannot tell which containers this folder owns. Some might be a teammate's. Some might belong to another Terraform folder. Only the book says which coats are ours.",
                  FadeOut(q), LaggedStart(*[FadeIn(o, shift=UP * 0.1) for o in others], lag_ratio=0.5), Succession(Wait(3.4), Indicate(rec, color=GOLD_M)), run_time=4.6)
        self.play(FadeOut(others), run_time=0.4)

        # 4. predict: the book is gone  [PREDICT, PAUSE, SHOW]
        q2 = T("delete terraform.tfstate. What does the next apply do?", 28, YELLOW_M).move_to([0, -1.3, 0])
        self.beat("So let's drop the book in the punch. You delete terraform.tfstate by mistake. The container keeps running. What does the next apply try to do?",
                  FadeIn(q2), rec.animate.set_opacity(0.1), run_time=2.8)
        self.guess([0, -2.1, 0])
        cr = M("+ docker_container.web   create", 24, GREEN_M).move_to([-2.2, -2.3, 0])
        fail = T("Docker: the name state-web is taken", 26, RED_M).move_to([-2.2, -3.0, 0])
        self.steps("It tries to create everything again, as if new. The code asks for a container, and the book knows of none. With Docker that fails, because the name is already taken.",
                   (0.6, FadeOut(q2)), (0.9, FadeIn(cr)), (2.4, Wait(2.4)), (0.8, FadeIn(fail)))
        two = T("in a cloud: two of everything", 26, RED_M).move_to([3.6, -2.65, 0])
        self.beat("In a cloud, where names don't clash, you can end up with two of everything. The coats were never the problem. The book was.",
                  FadeIn(two), run_time=2.6)
        self.play(FadeOut(VGroup(cr, fail, two)), rec.animate.set_opacity(1), run_time=0.6)

        # 5. a harmless rename?  [PREDICT, BREAK]
        code2 = VGroup(M('resource "docker_container"', 22), M('         "site" {', 22), M('  name = "state-web"', 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        fit(code2, 3.6).move_to(code)
        self.beat("Now a smaller slip. You rename the resource label from web to site, because site reads better. In git it looks harmless. Same container, same name.",
                  Transform(code, code2), run_time=2.8)
        q3 = T("what does the plan say?", 28, YELLOW_M).move_to([0, -1.3, 0])
        self.beat("What does the plan say?", FadeIn(q3), run_time=1.0)
        self.guess([0, -2.1, 0])
        pl = VGroup(M("+ docker_container.site  will be created", 22, GREEN_M), M("- docker_container.web   will be destroyed", 22, RED_M),
                    M("Plan: 1 to add, 0 to change, 1 to destroy.", 22, WHITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([0, -2.4, 0])
        self.steps("Terraform reads it differently. The book has a line for web, and the code has no web any more, so web will be destroyed. The code has a site, and the book has none, so site will be created.",
                   (0.5, FadeOut(q3)), (1.8, Wait(1.8)), (0.8, FadeIn(pl[1]), Indicate(rec[0], color=RED_M)), (2.4, Wait(2.4)), (0.8, FadeIn(pl[0])), (0.6, FadeIn(pl[2])))
        self.beat("That is the cloakroom attendant who sees a new ticket number, throws the coat in the bin, and buys an identical one. The real container would be rebuilt, data and all, to change a name only you can see.",
                  Indicate(c1, color=RED_M), run_time=3.4)

        # 6. the fix: a moved block  [NAME]
        mv = VGroup(M("moved {", 22, YELLOW_M), M("  from = docker_container.web", 22, YELLOW_M), M("  to   = docker_container.site", 22, YELLOW_M), M("}", 22, YELLOW_M))
        mv.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        mvp = panel(mv.width + 0.5, mv.height + 0.4, YELLOW_M, 0.08).move_to([-3.6, -2.35, 0])
        mv.move_to(mvp)
        self.beat("The fix is one block in your code: a moved block. From docker_container.web, to docker_container.site. It tells Terraform the object only changed its address.",
                  FadeOut(pl), Create(mvp), FadeIn(mv), run_time=3.2)
        res = VGroup(M("docker_container.web has moved to", 22, GREEN_M), M("docker_container.site", 22, GREEN_M), M("Plan: 0 to add, 0 to change, 0 to destroy.", 22, WHITE))
        res.arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([2.6, -2.35, 0])
        fit(res, 6.4).move_to([2.9, -2.35, 0])
        rec2 = VGroup(M("docker_container.site", 22, GOLD_M), M("id d8eb279c...", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(sp)
        self.steps("Plan again. docker_container.web has moved to docker_container.site. Zero to add, zero to destroy. Apply, and the book gets the new address, with the same ID.",
                   (1.6, FadeIn(res[:2])), (1.4, FadeIn(res[2])), (1.6, Wait(1.6)), (1.0, Transform(rec[0], rec2[0])), (0.6, Indicate(rec[1], color=GREY_B)))
        rule = T("A rename in code is a destroy to Terraform. Add a moved block.", 28, YELLOW_M).move_to([0, -0.9, 0])
        fit(rule, 12.4)
        self.beat("So the rule is short. A rename in code is a destroy to Terraform. Add a moved block, and check the plan for has moved to.",
                  FadeIn(rule, shift=UP * 0.1), run_time=2.8)
        self.play(FadeOut(VGroup(rule, mvp, mv, res, ask)), run_time=0.5)

        # 7. guardrails: the book holds everything  [GUARDRAIL]
        sec = M("REDIS_PASSWORD=s3cret-123", 22, RED_M).next_to(rec, DOWN, buff=0.2).align_to(rec, LEFT)
        self.beat("One place where the cloakroom picture stops short. A cloakroom book notes a ticket and a hook. Terraform's state copies every detail of each object, secrets included.",
                  FadeIn(sec), run_time=3.0)
        g = VGroup(T("a sensitive value is hidden in plan output, but plain text in the state", 26, RED_M),
                   T("never commit it to git, never edit it by hand", 26, GOLD_M),
                   T("read it with terraform state list and state show", 26, GOLD_M),
                   T("in a team: one locked remote backend", 26, GOLD_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.2, 0])
        fit(g, 12.4)
        self.beat("In a test, a variable marked sensitive printed as sensitive value in the plan. The state file held it in plain text. Anyone who can read your state can read your secrets.",
                  FadeIn(g[0]), run_time=3.2)
        self.beat("So treat the book like a password file. Never commit it to git, and never edit it by hand. Read it through commands, terraform state list and terraform state show.",
                  FadeIn(g[1]), Succession(Wait(2.0), FadeIn(g[2])), run_time=3.4)
        self.beat("And in a team, keep one copy on a remote backend that locks it, so only one run at a time can write in the book.",
                  FadeIn(g[3]), run_time=2.6)
        self.play(FadeOut(g), FadeOut(sec), run_time=0.5)

        # 8. moral and check  [MORAL, RECAP]
        mor = T("the coats are easy to see. The book is what tells you whose they are.", 26, WHITE).move_to([0, -1.6, 0])
        fit(mor, 12.4)
        self.beat("The moral of the story. The containers are easy to see, so they feel like what matters. But the state is what tells Terraform which ones are its own. Lose the book, and it builds again. Rename without telling it, and it rebuilds.",
                  FadeIn(mor), Indicate(sp, color=GOLD_M, scale_factor=1.02), run_time=5.0)
        self.play(FadeOut(mor), run_time=0.4)
        chk = VGroup(T("quick check: terraform state rm docker_container.site,", 26, YELLOW_M), T("then terraform apply. The container still runs. What happens?", 26, YELLOW_M)).arrange(DOWN, buff=0.12).move_to([0, -1.6, 0])
        fit(chk, 12.4)
        self.beat("A quick check. You run terraform state rm on the site container, then apply. The container is still running. What happens?",
                  FadeIn(chk), rec.animate.set_opacity(0.1), run_time=2.8)
        self.guess([0, -2.7, 0])
        ans = T("apply tries to create it, and Docker refuses the taken name", 26, GREEN_M).move_to([0, -2.75, 0])
        fit(ans, 12.4)
        self.beat("state rm only crossed the line out of the book. The code still asks for the container, so apply tries to create it, and Docker refuses the duplicate name.",
                  FadeIn(ans), run_time=3.0)
        self.wait(1.0)
