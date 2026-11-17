import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"\bd6aad6e\b", "D 6 A A D 6 E"), (r"\b6e176d6\b", "6 E 1 7 6 D 6"), (r"\bc711550\b", "C 7 1 1 5 5 0"),
    (r"git reset --hard 'HEAD@\{1\}'", "git reset dash dash hard, head at one"), (r"HEAD@\{1\}", "head at one"),
    (r"git reset --hard HEAD~2", "git reset dash dash hard head tilde two"), (r"HEAD~2", "head tilde two"),
    (r"git reset --hard", "git reset dash dash hard"), (r"git cat-file -t", "git cat file dash T"),
    (r"\.git\b", "dot git"), (r"\bREADME\b", "read me"), (r"\breflog\b", "ref log"), (r"\bgit log\b", "git log"),
])

PHOTO, NOTE, HEADC, DESK, TRAY, CAB = GREY_B, YELLOW_M, BLUE_M, GOLD_M, TEAL_M, PURPLE_M
ROW_X = -1.0
ROWS = {"6e176d6": 2.15, "d6aad6e": 1.2, "c711550": 0.25, "09e16be": -0.7, "16cc719": -1.65}
MSG = {"6e176d6": "Say that prices include VAT", "d6aad6e": "Group thousands in prices",
       "c711550": "Explain how to run the calculator", "09e16be": "Raise the tax rate to 25%", "16cc719": "Add a discount function"}
NOTE_X, HEAD_X = 4.1, 5.9


def row(h):
    t = VGroup(M(h, 24, YELLOW_M), M(MSG[h], 24)).arrange(RIGHT, buff=0.3)
    r = RoundedRectangle(corner_radius=0.1, width=7.8, height=0.68, stroke_color=PHOTO, stroke_width=2.5).set_fill("#111111", 1)
    t.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.3)
    return VGroup(r, t).move_to(np.array([ROW_X, ROWS[h], 0]))


def sticky(text, color=NOTE):
    t = M(text, 26, BLACK)
    r = Rectangle(width=t.width + 0.5, height=0.62, stroke_width=0).set_fill(color, 1)
    fold = Polygon(r.get_corner(DR) + LEFT * 0.22, r.get_corner(DR), r.get_corner(DR) + UP * 0.22, stroke_width=0).set_fill(interpolate_color(ManimColor(color), ManimColor("#000000"), 0.35), 1)
    return VGroup(r, t.move_to(r), fold)


def place(box, color, title, sub, x, w=3.5):
    r = RoundedRectangle(corner_radius=0.15, width=w, height=2.4, stroke_color=color, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.10), 1)
    r.move_to(np.array([x, 0.3, 0]))
    t = T(title, 30, color).next_to(r, UP, buff=0.25)
    s = T(sub, 26, GREY_B).next_to(r, DOWN, buff=0.3)
    return VGroup(r, t), s


def page(color, w=0.9, h=1.15):
    p = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2.5).set_fill(BLACK, 1)
    lines = VGroup(*[Line(LEFT * w * 0.32, RIGHT * w * 0.32, stroke_width=2, color=color).shift(UP * (h * 0.28 - i * 0.2)) for i in range(4)])
    return VGroup(p, lines.move_to(p))


class D08StickyNote(VoiceScene):
    def construct(self):
        self.title_card("Where did my commit go?", "snapshots, sticky notes and the clerk's logbook")

        # ---------- 1. the folder of final files
        names = ["prices.docx", "prices-final.docx", "prices-final-2.docx", "prices-final-REAL.docx", "prices-ben.docx"]
        files = VGroup(*[VGroup(page(GREY_B, 0.42, 0.54), T(n, 28)).arrange(RIGHT, buff=0.3) for n in names])
        files.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(LEFT * 2.2 + DOWN * 0.1)
        self.beat("Picture a shared office folder, with five files in it.",
                  LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in files], lag_ratio=0.3), run_time=2.4)
        q = T("Which one went to the shop on Tuesday?", 30, YELLOW_M).move_to(UP * 2.9)
        shrug = T("?", 120, YELLOW_M).move_to(RIGHT * 4.3 + DOWN * 0.1)
        self.beat("Your manager asks a simple question. Which one did we send to the shop on Tuesday? Nobody knows.",
                  FadeIn(q, shift=DOWN * 0.1), Succession(Wait(3.2), Write(shrug)), run_time=4.6)
        self.beat("Notice how the names go. Final, then final two, then final real. File names start out honest, and end up hopeful.",
                  Succession(Indicate(files[1][1], color=GOLD_M), Indicate(files[2][1], color=GOLD_M), Indicate(files[3][1], color=GOLD_M, scale_factor=1.15)), run_time=4.4)
        self.beat("So the point really is this. A name can't remember history. We need something that does.",
                  FadeOut(VGroup(files, q, shrug)), run_time=1.4)

        # ---------- 2. desk, tray, cabinet
        desk, ds = place(None, DESK, "desk", "working tree", -4.6)
        tray, ts = place(None, TRAY, "tray", "staging area", 0)
        cab, cs = place(None, CAB, "cabinet", "repository (.git)", 4.6)
        self.beat("Git is the tool that keeps every saved version of a project for you. Picture an office again. A desk for the pages you're working on, a tray for the pages that are ready, and a filing cabinet behind you.",
                  Succession(Wait(3.0), LaggedStart(*[AnimationGroup(Create(b[0]), Write(b[1])) for b in (desk, tray, cab)], lag_ratio=0.7)), run_time=9.0)
        p1 = page(DESK).move_to(desk[0])
        self.play(FadeIn(p1, shift=UP * 0.2), run_time=0.5)
        p2 = p1.copy()
        photo = RoundedRectangle(corner_radius=0.06, width=1.3, height=1.0, stroke_color=PHOTO, stroke_width=3).set_fill("#151515", 1)
        flash = Rectangle(width=3.4, height=2.3, stroke_width=0).set_fill(WHITE, 0.6).move_to(tray[0])
        self.beat("When a page is ready, it goes in the tray. Whenever you say save, a clerk photographs everything in the tray, and files the photo in the cabinet.",
                  Succession(p2.animate(run_time=1.2).move_to(tray[0]).set_stroke(TRAY), Wait(2.4),
                             AnimationGroup(FadeIn(flash, run_time=0.15)), FadeOut(flash, run_time=0.4),
                             FadeIn(photo.move_to(tray[0]), run_time=0.3), photo.animate(run_time=1.4).move_to(cab[0])), run_time=7.0)
        self.beat("In Git's words, the desk is the working tree, the tray is the staging area, and the cabinet is the repository, a hidden folder called .git. Each photo is a commit.",
                  LaggedStart(FadeIn(ds), FadeIn(ts), FadeIn(cs), lag_ratio=0.8), Succession(Wait(6.0), Indicate(photo, color=WHITE)), run_time=7.6)
        self.beat("Let's open the cabinet.", FadeOut(VGroup(desk, tray, ds, ts, p1, p2, photo)), cab.animate.set_opacity(0), FadeOut(cs), run_time=1.2)
        self.remove(cab)

        # ---------- 3. the commits, the chain, the note
        rows = {h: row(h) for h in ROWS}
        base = ["d6aad6e", "c711550", "09e16be", "16cc719"]
        more = M("...", 26, GREY_B).move_to(np.array([ROW_X, -2.4, 0]))
        self.beat("Each photo is a full snapshot of the project. And it's named by a hash of its content, a short fingerprint like d6aad6e. Same content, same name, on every computer.",
                  LaggedStart(*[FadeIn(rows[h], shift=DOWN * 0.15) for h in base], lag_ratio=0.3), FadeIn(more),
                  Succession(Wait(4.2), Indicate(rows["d6aad6e"][1][0], color=YELLOW_M, scale_factor=1.25)), run_time=8.0)
        def par(a, b):
            ra, rb = rows[a], rows[b]
            x = ra[0].get_left()[0] - 0.35
            return Arrow(np.array([x, ra.get_center()[1], 0]), np.array([x, rb.get_center()[1], 0]), buff=0.05, stroke_width=3, color=GREY_B,
                         max_tip_length_to_length_ratio=0.25)
        pars = VGroup(par("d6aad6e", "c711550"), par("c711550", "09e16be"), par("09e16be", "16cc719"))
        plab = T("parent", 24, GREY_B).next_to(pars[0], LEFT, buff=0.15)
        self.beat("Each photo also remembers the one before it, its parent. So history is a chain, and you can walk it backwards.",
                  LaggedStart(*[GrowArrow(a) for a in pars], lag_ratio=0.4), FadeIn(plab),
                  Succession(Wait(2.6), *[travel(a, YELLOW_M, 0.5) for a in pars]), run_time=5.0)
        note = sticky("main").move_to(np.array([NOTE_X, ROWS["d6aad6e"], 0]))
        nlink = always_redraw(lambda: Arrow(note.get_left(), np.array([rows["d6aad6e"][0].get_right()[0], note.get_center()[1], 0]), buff=0.08, stroke_width=3, color=NOTE, max_tip_length_to_length_ratio=0.3))
        nl0 = nlink.copy().clear_updaters()
        self.beat("Now, which photo is the newest on the main line of work? Git keeps that answer on a sticky note. The note is called main, and it holds one name, d6aad6e. That note is the whole branch.",
                  Succession(Wait(4.0), AnimationGroup(FadeIn(note, shift=LEFT * 0.3), GrowArrow(nl0))), run_time=6.0)
        self.remove(nl0)
        self.add(nlink)
        head = chip("HEAD", HEADC, 26, mono=True).move_to(np.array([HEAD_X, ROWS["d6aad6e"], 0]))
        hlink = always_redraw(lambda: Arrow(head.get_left(), note.get_right(), buff=0.08, stroke_width=3, color=HEADC, max_tip_length_to_length_ratio=0.3))
        here = T("you are here", 24, HEADC)
        here.add_updater(lambda m: m.next_to(head, UP, buff=0.2))
        self.beat("And HEAD is the you are here arrow, like the one on a map in a shopping centre. It points at main.",
                  FadeIn(head, shift=LEFT * 0.2), FadeIn(here), run_time=1.6)
        self.add(hlink)

        # ---------- 4. a new commit: one photo, one note moves
        cmd = M("$ git commit -am 'Say that prices include VAT'", 24).move_to(UP * 3.15)
        self.beat("Let's add a line to the README, and commit it. Pause and guess. What does Git copy when you commit?",
                  Write(cmd), run_time=2.4, after=2.0)
        pg = VGroup(note, head)
        self.beat("Nothing gets copied. Git files one new photo, 6e176d6, and moves the sticky note up to it. HEAD comes along, because it points at main.",
                  Succession(Wait(1.2), FadeIn(rows["6e176d6"], shift=DOWN * 0.15), Wait(1.6),
                             pg.animate(run_time=1.4).shift(UP * (ROWS["6e176d6"] - ROWS["d6aad6e"]))), run_time=7.0)
        top = par("6e176d6", "d6aad6e")
        self.play(GrowArrow(top), run_time=0.5)
        pars.add(top)

        # ---------- 5. the mistake
        bad = M("$ git reset --hard HEAD~2", 26, RED_M).move_to(cmd)
        self.beat("Now the mistake. You meant to undo one commit, and keep its changes. But your fingers typed git reset --hard HEAD~2.",
                  FadeOut(cmd), Succession(Wait(3.4), Write(bad)), run_time=6.0)
        out = M("HEAD is now at c711550 Explain how to run the calculator", 22, GREY_B).next_to(bad, DOWN, buff=0.18)
        self.beat("Git answers, HEAD is now at c711550. The note slides back two photos.",
                  FadeIn(out), Succession(Wait(1.6), pg.animate(run_time=1.6).shift(DOWN * (ROWS["6e176d6"] - ROWS["c711550"]))), run_time=4.0)
        gone = VGroup(rows["6e176d6"], rows["d6aad6e"], pars[0], pars[3])
        self.beat("You run git log, and the top two are gone. Your commit, and Ana's.",
                  gone.animate.set_opacity(0.18), run_time=1.6)
        self.beat("This is the moment people start typing very fast, which is exactly the wrong moment to type anything. So slow down, and ask what really happened.",
                  Wiggle(bad), run_time=1.4)

        # ---------- 6. predict, then break the wrong model
        guess = T("missing from git log = deleted?", 30, YELLOW_M).move_to(DOWN * 3.2)
        self.beat("Here's the natural guess. The log is the history, so if a commit is missing from the log, it must be deleted. Pause and guess. Is it?",
                  FadeIn(guess, shift=UP * 0.1), run_time=1.6, after=2.2)
        walk = VGroup(pars[1], pars[2])
        self.beat("Let's look. git log starts at the sticky note, and walks back through the parents. It never looks forward.",
                  FadeOut(guess), Succession(Wait(1.4), Indicate(note[1], color=BLACK), *[travel(a, YELLOW_M, 0.6) for a in walk]), run_time=5.0)
        self.beat("So the two photos are still in the cabinet. The note just doesn't point at them any more.",
                  gone.animate.set_opacity(0.55), run_time=1.6)
        cf = M("$ git cat-file -t 6e176d6", 24).move_to(bad)
        cfo = M("commit", 24, GREEN_M).next_to(cf, RIGHT, buff=0.4)
        self.beat("We can even ask for one by name. git cat-file -t 6e176d6 prints its type, commit. It exists.",
                  FadeOut(out), ReplacementTransform(bad, cf), Succession(Wait(3.6), FadeIn(cfo, shift=LEFT * 0.1), Indicate(rows["6e176d6"][1][0], color=YELLOW_M)), run_time=6.0)
        self.beat("So reset deleted nothing. It moved a sticky note.",
                  Succession(pg.animate(run_time=0.6).shift(UP * 0.12), pg.animate(run_time=0.6).shift(DOWN * 0.12)), run_time=1.6)

        # ---------- 7. the clerk's logbook
        main_pic = VGroup(*rows.values(), more, pars, plab)
        lines = [("c711550 (HEAD -> main) HEAD@{0}: reset: moving to HEAD~2", WHITE),
                 ("6e176d6 HEAD@{1}: commit: Say that prices include VAT", YELLOW_M),
                 ("d6aad6e HEAD@{2}: commit: Group thousands in prices", WHITE),
                 ("c711550 (HEAD -> main) HEAD@{3}: checkout: moving from currency-first to main", WHITE)]
        rl = VGroup(*[M(s, 22, c) for s, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        fit(rl, 12.5)
        book = RoundedRectangle(corner_radius=0.15, width=rl.width + 0.5, height=rl.height + 0.8, stroke_color=CAB, stroke_width=3).set_fill("#0d0a10", 1)
        logg = VGroup(book, rl.move_to(book)).move_to(DOWN * 0.6)
        btitle = T("the clerk's logbook", 28, CAB).next_to(book, UP, buff=0.25)
        rcmd = M("$ git reflog -4", 24).move_to(cf)
        nlink.clear_updaters(); hlink.clear_updaters(); here.clear_updaters()
        self.beat("But how do you find a photo whose name you forgot? The clerk keeps a logbook. Every time HEAD moves, the logbook gets a line, newest first. That's git reflog.",
                  FadeOut(VGroup(cf, cfo)), FadeOut(nlink), FadeOut(hlink), FadeOut(VGroup(main_pic, note, head, here)),
                  Succession(Wait(3.0), AnimationGroup(Create(book), FadeIn(btitle))), Succession(Wait(6.4), Write(rcmd), LaggedStart(*[FadeIn(l, shift=DOWN * 0.08) for l in rl], lag_ratio=0.3)), run_time=10.0)
        self.beat("Read it from the top. We reset, moving to HEAD~2. Before that, we committed, Say that prices include VAT. There's our lost commit, one line down, 6e176d6.",
                  Succession(Indicate(rl[0], color=WHITE, scale_factor=1.04), Wait(2.2), Indicate(rl[1], color=YELLOW_M, scale_factor=1.06)), run_time=7.0)

        # ---------- 8. two ways back
        self.play(FadeOut(VGroup(logg, btitle)), FadeIn(VGroup(main_pic, note, head, here)), run_time=0.8)
        nlink = always_redraw(lambda: Arrow(note.get_left(), np.array([rows["d6aad6e"][0].get_right()[0], note.get_center()[1], 0]), buff=0.08, stroke_width=3, color=NOTE, max_tip_length_to_length_ratio=0.3))
        hlink = always_redraw(lambda: Arrow(head.get_left(), note.get_right(), buff=0.08, stroke_width=3, color=HEADC, max_tip_length_to_length_ratio=0.3))
        here.add_updater(lambda m: m.next_to(head, UP, buff=0.2))
        self.add(nlink, hlink)
        rescue = sticky("rescue", GREEN_M).move_to(np.array([NOTE_X + 0.3, ROWS["6e176d6"], 0]))
        rlink = Arrow(rescue.get_left(), np.array([rows["6e176d6"][0].get_right()[0], ROWS["6e176d6"], 0]), buff=0.08, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.3)
        rcmd2 = M("$ git branch rescue 6e176d6", 24, GREEN_M).move_to(rcmd)
        self.beat("Now that we know its name, there are two ways back. The gentle one: git branch rescue 6e176d6 puts a second sticky note on that photo, and moves nothing.",
                  ReplacementTransform(rcmd, rcmd2), Succession(Wait(4.4), AnimationGroup(FadeIn(rescue, shift=LEFT * 0.3), GrowArrow(rlink))), run_time=7.0)
        fix = M("$ git reset --hard 'HEAD@{1}'", 24, GREEN_M).move_to(rcmd2)
        self.beat("Or move main itself back to where it was one step ago, with git reset --hard 'HEAD@{1}'. HEAD@{1} means where HEAD was before the last move.",
                  FadeOut(VGroup(rescue, rlink)), ReplacementTransform(rcmd2, fix), run_time=2.0)
        self.remove(rescue, rlink)
        out2 = M("HEAD is now at 6e176d6 Say that prices include VAT", 22, GREY_B).next_to(fix, DOWN, buff=0.18)
        self.beat("HEAD is now at 6e176d6. The note slides back up, and both photos are on the main line again.",
                  FadeIn(out2), Succession(Wait(1.6), pg.animate(run_time=1.6).shift(UP * (ROWS["6e176d6"] - ROWS["c711550"])), gone.animate(run_time=0.6).set_opacity(1)), run_time=5.0)
        self.play(FadeOut(VGroup(fix, out2)), run_time=0.5)
        rule = T("A branch is a sticky note on a commit. Most undo commands just move the note.", 28, NOTE).move_to(UP * 3.15)
        fit(rule, 12.6)
        self.beat("So now you know why a branch is so cheap. It's a sticky note on a commit. And most undo commands just move the note.",
                  FadeIn(rule, shift=DOWN * 0.1), run_time=2.0)

        # ---------- 9. the limit: the desk
        nlink.clear_updaters(); hlink.clear_updaters(); here.clear_updaters()
        self.play(FadeOut(VGroup(main_pic, note, head, here, rule)), FadeOut(nlink), FadeOut(hlink), run_time=0.7)
        desk, ds = place(None, DESK, "desk", "working tree", -3.2, w=4.4)
        cab2, cs2 = place(None, CAB, "cabinet", "repository (.git)", 3.2)
        ph = VGroup(*[RoundedRectangle(corner_radius=0.06, width=1.0, height=0.75, stroke_color=PHOTO, stroke_width=2.5).set_fill("#151515", 1) for _ in range(3)])
        ph.arrange(RIGHT, buff=0.15).move_to(cab2[0])
        draft = chip("Draft note, never committed", DESK, 22).move_to(desk[0])
        self.beat("But every tool has a limit, and here's this one's. The logbook only knows about commits. Picture an edit that lived only on your desk.",
                  FadeIn(VGroup(desk, ds, cab2, cs2, ph)), Succession(Wait(4.8), FadeIn(draft, scale=0.8)), run_time=7.0)
        lim = VGroup(M("$ git reset --hard", 24), M("$ grep -c 'Draft note' README.md", 24), M("0", 24, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        lim.move_to(UP * 2.85)
        xd = tick(False, 0.45).move_to(draft)
        self.beat("Run git reset --hard, and the desk is wiped to match the last photo. The reflog has no entry for that draft. grep counts zero lines. It's gone.",
                  Write(lim[0]), Succession(Wait(1.8), AnimationGroup(draft.animate.set_opacity(0.25), Create(xd))),
                  Succession(Wait(5.0), FadeIn(lim[1]), Wait(0.8), FadeIn(lim[2])), run_time=8.0)
        g1 = T("commit or stash before any --hard", 30, YELLOW_M).move_to(DOWN * 2.85)
        self.beat("So, one habit before any hard reset. Commit or stash first. A commit you reset away stays recoverable for at least thirty days, by default. An edit on your desk, not even one second.",
                  FadeIn(g1, shift=UP * 0.1), Succession(Wait(5.6), Indicate(ph, color=WHITE)), Succession(Wait(9.0), Indicate(xd, color=RED_M)), run_time=10.0)
        rv = M("$ git revert 09e16be", 24, TEAL_M).move_to(lim)
        self.beat("And if you already pushed a commit, don't move a shared note at all. git revert adds a new commit that undoes the old one, so history only grows.",
                  FadeOut(lim), FadeOut(VGroup(desk, ds, draft, xd)), Succession(Wait(1.4), Write(rv)), run_time=4.0)
        extra = RoundedRectangle(corner_radius=0.06, width=1.0, height=0.75, stroke_color=TEAL_M, stroke_width=2.5).set_fill("#0b1714", 1)
        self.play(ph.animate.shift(LEFT * 0.58), run_time=0.5)
        extra.next_to(ph, RIGHT, buff=0.15)
        self.play(FadeIn(extra, shift=LEFT * 0.2), run_time=0.6)

        # ---------- 10. moral and check
        self.play(FadeOut(VGroup(cab2, cs2, ph, extra, g1, rv)), run_time=0.6)
        moral = T("Anything committed can come back.", 42)
        sub = T("Git moves notes, and writes down every move.", 30, GREY_B).next_to(moral, DOWN, buff=0.4)
        self.beat("The moral of the story. Anything committed can come back. Git rarely throws your photos away. It moves notes, and it writes down every move.",
                  Write(moral), Succession(Wait(3.0), FadeIn(sub, shift=UP * 0.1)), run_time=5.0)
        self.play(VGroup(moral, sub).animate.to_edge(UP, buff=0.8).set_opacity(0.6), run_time=0.6)
        qq = T("After git reset --hard, which one survives?", 32, YELLOW_M).move_to(UP * 0.3)
        a1 = chip("a commit from an hour ago", GREY_B, 26)
        a2 = chip("an edit you never committed", GREY_B, 26)
        opts = VGroup(a1, a2).arrange(RIGHT, buff=0.8).next_to(qq, DOWN, buff=0.6)
        self.beat("A quick check. You run git reset --hard. Which one survives? A commit you made an hour ago, or an edit you never committed? Pause and guess.",
                  FadeIn(qq), Succession(Wait(3.4), FadeIn(a1, shift=UP * 0.1), Wait(1.4), FadeIn(a2, shift=UP * 0.1)), run_time=7.0, after=2.2)
        self.beat("The commit. The reflog still lists it. The edit lived only on your desk, so it's gone.",
                  a1[0].animate.set_stroke(GREEN_M, 4), a2.animate.set_opacity(0.3), run_time=1.6)
        self.wait(1.5)
