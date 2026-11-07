import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# Real objects from the course's practice repo (labs/git/make-practice-repo.sh), checked with git cat-file.
COMMIT_C, TREE_C, BLOB_C, PTR_C = BLUE_M, GREEN_M, TEAL_M, GOLD_M


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def late(a, b=1.0, f=smooth):
    """Rate function that waits until fraction a of the animation, then runs f until fraction b."""
    return lambda t: f(float(np.clip((t - a) / (b - a), 0, 1)))


def obj_box(rows, color, msg=None, size=20, pad=0.25, w=None):
    """A git object: outlined box with monospace rows (text, colour) and an optional message line."""
    g = VGroup(*[M(t, size, c) for t, c in rows])
    if msg:
        g.add(T(msg, 22))
    g.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    r = RoundedRectangle(corner_radius=0.12, width=w or g.width + 2 * pad, height=g.height + 2 * pad, stroke_color=color, stroke_width=3)
    r.set_fill(tint(color, 0.12), 1)
    g.move_to(r)
    return VGroup(r, g)


def fchip(name, color=GREY_B, w=2.5):
    t = M(name, 22)
    r = RoundedRectangle(corner_radius=0.08, width=w, height=0.56, stroke_color=color, stroke_width=2.5).set_fill(tint(color, 0.16), 1)
    return VGroup(r, t.move_to(r))


def cdot(color=COMMIT_C, r=0.32):
    return Circle(radius=r, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)


def harrow(a, b, color=GREY_B, sw=3):
    return Arrow(a, b, buff=0, stroke_width=sw, color=color, max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=10)


def tag(text, color=PTR_C):
    return chip(text, color, size=24, mono=True)


class D08GitStore(VoiceScene):
    def construct(self):
        self.title_card("How Git stores your work", "three places, snapshots, and pointers")

        # ---------- 1. three places
        xs = [-4.7, 0.0, 4.7]
        names = ["working tree", "staging area", "repository"]
        subs = ["your project folder", "the index: your next commit", "the hidden .git folder"]
        cols = [GREY_B, YELLOW_M, COMMIT_C]
        frames = VGroup(*[RoundedRectangle(corner_radius=0.15, width=3.0, height=3.3, stroke_color=c, stroke_width=3).move_to([x, -0.25, 0])
                          for x, c in zip(xs, cols)])
        heads = VGroup(*[T(n, 32, c).next_to(f, UP, buff=0.3) for n, c, f in zip(names, cols, frames)])
        subl = VGroup(*[T(s, 24, GREY_B).next_to(f, DOWN, buff=0.25) for s, f in zip(subs, frames)])
        self.beat("Git keeps your project in three places.",
                  LaggedStart(*[AnimationGroup(Create(f), Write(h)) for f, h in zip(frames, heads)], lag_ratio=0.3), run_time=2.2)

        rows_y = [0.55, -0.25, -1.05]
        files = [".gitignore", "README.md", "price.py"]
        wt = VGroup(*[fchip(n).move_to([xs[0], y, 0]) for n, y in zip(files, rows_y)])
        self.beat("The working tree is the files in your project folder, the ones your editor changes.",
                  LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in wt], lag_ratio=0.25), FadeIn(subl[0]), run_time=2.0)

        st = VGroup(*[fchip(n, GREY_D).move_to([xs[1], y, 0]) for n, y in zip(files, rows_y)])
        self.beat("The staging area, also called the index, holds the exact contents of your next commit.",
                  LaggedStart(*[TransformFromCopy(a, b) for a, b in zip(wt, st)], lag_ratio=0.2), FadeIn(subl[1]), run_time=2.2)

        rx = 3.95
        old = VGroup(cdot(r=0.22).move_to([rx, rows_y[0], 0]), cdot(r=0.22).move_to([rx, rows_y[1], 0]))
        old_l = VGroup(*[M(h, 20, GREY_B).next_to(d, RIGHT, buff=0.22) for h, d in zip(["c711550", "d6aad6e"], old)])
        old_a = harrow(old[1].get_top(), old[0].get_bottom())
        self.beat("The repository is the hidden .git folder, where every commit lives.",
                  LaggedStart(GrowFromCenter(old[0]), GrowFromCenter(old[1]), lag_ratio=0.3), GrowArrow(old_a), FadeIn(old_l), FadeIn(subl[2]), run_time=2.0)

        edited = fchip("price.py", YELLOW_M).move_to(wt[2])
        self.beat("Say you change the price file in your editor. Only the working tree changes.",
                  Transform(wt[2], edited), run_time=1.2)
        self.play(Circumscribe(wt[2], color=YELLOW_M, buff=0.08), run_time=0.8)

        a_add = harrow([xs[0] + 1.6, rows_y[2], 0], [xs[1] - 1.6, rows_y[2], 0], YELLOW_M)
        l_add = M("git add", 20, YELLOW_M).next_to(a_add, UP, buff=0.12)
        staged = fchip("price.py", YELLOW_M).move_to(st[2])
        self.beat("git add copies that change into the staging area.",
                  GrowArrow(a_add), FadeIn(l_add), FadeOut(st[2], rate_func=late(0.3, 0.6)),
                  TransformFromCopy(wt[2], staged, rate_func=late(0.3)), run_time=1.8)
        st = VGroup(st[0], st[1], staged)

        new = cdot(YELLOW_M, r=0.22).move_to([rx, rows_y[2], 0])
        ghosts = VGroup(*[c.copy() for c in st])
        new_a = harrow(new.get_top(), old[1].get_bottom())
        a_com = harrow([xs[1] + 1.6, rows_y[2], 0], [xs[2] - 1.6, rows_y[2], 0], COMMIT_C)
        l_com = M("git commit", 20, COMMIT_C).next_to(a_com, UP, buff=0.12)
        new_l = T("new commit", 22, YELLOW_M).next_to(new, RIGHT, buff=0.22)
        self.beat("git commit turns the whole staging area into a new commit in the repository.",
                  GrowArrow(a_com), FadeIn(l_com),
                  Succession(Wait(0.6), AnimationGroup(*[g.animate.move_to(new).scale(0.12).set_opacity(0) for g in ghosts], run_time=1.2), GrowFromCenter(new)),
                  Succession(Wait(1.8), AnimationGroup(GrowArrow(new_a), FadeIn(new_l))), run_time=2.8)
        self.remove(*ghosts)
        self.play(FadeOut(VGroup(frames, heads, subl, wt, st, old, old_l, old_a, new, new_a, new_l, a_add, l_add, a_com, l_com)), run_time=0.8)
        self.remove(*self.mobjects)

        # ---------- 2. a commit is a snapshot of objects named by hashes
        diff = VGroup(M("price.py", 22, GREY_B), M("- TAX_RATE = 0.20", 26, RED_M), M("+ TAX_RATE = 0.25", 26, GREEN_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        dbox = SurroundingRectangle(diff, buff=0.35, corner_radius=0.12, stroke_color=GREY_B, stroke_width=2.5)
        dg = VGroup(dbox, diff).move_to(UP * 0.3)
        dlab = T("a diff: the lines you changed", 28, GREY_B).next_to(dg, UP, buff=0.35)
        self.beat("Most people picture a commit as a diff: the lines you changed. Git does not store it that way.",
                  Create(dbox), Write(diff), FadeIn(dlab), run_time=2.0)
        self.play(Create(tick(False, 0.9).move_to(dg)), run_time=0.7)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        # right side: commit d6aad6e, its tree and its blobs
        RX, LX = 3.7, -3.7
        c1 = obj_box([("commit d6aad6e", YELLOW_M), ("tree   3ba153e", WHITE), ("parent c711550", WHITE), ("author Ana Silva 1791467100", GREY_B)],
                     COMMIT_C, msg="Group thousands in prices").move_to([RX, 2.5, 0])
        t1 = obj_box([("tree 3ba153e", YELLOW_M), (".gitignore", WHITE), ("README.md", WHITE), ("price.py", WHITE)], TREE_C).move_to([RX, -0.05, 0])
        b_ig = obj_box([("blob 30a5edb", YELLOW_M)], BLOB_C).move_to([0, 0.5, 0])
        b_rm = obj_box([("blob c1118d8", YELLOW_M)], BLOB_C).move_to([0, -0.45, 0])
        b_p1 = obj_box([("blob ffd69e3", YELLOW_M)], BLOB_C).move_to([RX, -2.45, 0])
        ent = t1[1]

        def entry_arrow(tree, i, blob, side):
            p = ent_point(tree, i, side)
            q = blob[0].get_right() if side < 0 else blob[0].get_left()
            return harrow(p, [q[0] + (0.08 if side < 0 else -0.08), q[1], 0], GREY_B, sw=2.5)

        def ent_point(tree, i, side):
            row = tree[1][i]
            x = tree[0].get_left()[0] if side < 0 else tree[0].get_right()[0]
            return np.array([x + (-0.05 if side < 0 else 0.05), row.get_center()[1], 0])

        r_ig = entry_arrow(t1, 1, b_ig, -1)
        r_rm = entry_arrow(t1, 2, b_rm, -1)
        r_p1 = harrow(t1[0].get_bottom() + DOWN * 0.05, b_p1[0].get_top() + UP * 0.08, GREY_B, sw=2.5)
        c_t1 = harrow(c1[0].get_bottom() + DOWN * 0.05, t1[0].get_top() + UP * 0.08, GREY_B, sw=2.5)
        right = VGroup(c1, t1, b_ig, b_rm, b_p1)
        self.beat("Each commit records the whole project, as it was at that moment. Git works out a diff only when you ask for one.",
                  LaggedStart(FadeIn(c1, shift=DOWN * 0.2), GrowArrow(c_t1), FadeIn(t1, shift=DOWN * 0.2),
                              AnimationGroup(GrowArrow(r_ig), GrowArrow(r_rm), GrowArrow(r_p1)),
                              AnimationGroup(FadeIn(b_ig), FadeIn(b_rm), FadeIn(b_p1)), lag_ratio=0.35), run_time=3.6)

        legend = VGroup(T("blob: one file's contents", 26, BLOB_C), T("tree: one folder", 26, TREE_C), T("commit: a tree, a parent,", 26, COMMIT_C),
                        T("an author, a message", 26, COMMIT_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([-4.0, 0.6, 0])
        legend[3].shift(RIGHT * 1.15)
        self.beat("Git keeps three kinds of objects. A blob holds the contents of one file. Only the bytes: no file name, no date.",
                  FadeIn(legend[0], shift=RIGHT * 0.15), *[Circumscribe(b, color=BLOB_C, buff=0.06) for b in (b_ig, b_rm, b_p1)], run_time=2.4)
        self.beat("A tree is one folder. It lists names, and each name points to a blob, or to another tree.",
                  FadeIn(legend[1], shift=RIGHT * 0.15), Circumscribe(t1, color=TREE_C, buff=0.06), run_time=2.4)
        self.beat("A commit points to one tree, the top folder of the project. It also holds its parent commit, the author, the time and the message.",
                  FadeIn(legend[2:], shift=RIGHT * 0.15), Circumscribe(c1, color=COMMIT_C, buff=0.06), run_time=2.6)

        # the hash
        hello = chip("hello", WHITE, 26, mono=True)
        sha = box("SHA-1", GREY_B, w=1.6, h=0.62, size=26)
        hx = M("ce013625030ba8dba906f756967f9e9ca394464a", 22, YELLOW_M)
        hrow = VGroup(hello, sha, hx).arrange(RIGHT, buff=0.75).move_to(DOWN * 3.4)
        h_a1, h_a2 = harrow(hello.get_right() + RIGHT * 0.1, sha.get_left() + LEFT * 0.1), harrow(sha.get_right() + RIGHT * 0.1, hx.get_left() + LEFT * 0.1)
        self.beat("Every object is named by a hash of its content. A hash turns any bytes into a short, fixed-length fingerprint.",
                  FadeOut(legend), FadeIn(hello), GrowArrow(h_a1), FadeIn(sha), Succession(Wait(1.0), AnimationGroup(GrowArrow(h_a2), Write(hx))), run_time=3.0)
        first7 = Line(hx[:7].get_corner(DL) + DOWN * 0.1, hx[:7].get_corner(DR) + DOWN * 0.1, stroke_color=YELLOW_M, stroke_width=4)
        self.beat("Git uses SHA-1, which gives forty hex characters, and it usually shows only the first seven.",
                  Create(first7), hx[7:].animate.set_opacity(0.4), run_time=1.6)
        same = VGroup(T("same content, same name,", 26, GREY_B), T("on every computer", 26, GREY_B)).arrange(DOWN, buff=0.15).move_to([-3.7, -2.0, 0])
        self.beat("The same content gets the same name on every computer. Hash the word hello on your machine or on mine, and you get exactly this.",
                  FadeIn(same, shift=UP * 0.1), Indicate(hx[:7], color=YELLOW_M, scale_factor=1.15), run_time=2.0)
        self.play(FadeOut(VGroup(hrow, h_a1, h_a2, first7, same)), run_time=0.6)

        # left side: the commit before, sharing blobs
        c0 = obj_box([("commit c711550", YELLOW_M), ("tree   a1ce7e7", WHITE), ("parent 09e16be", WHITE), ("author Ana Silva 1791374700", GREY_B)],
                     COMMIT_C, msg="Explain how to run the calculator").move_to([LX, 2.5, 0])
        t0 = obj_box([("tree a1ce7e7", YELLOW_M), (".gitignore", WHITE), ("README.md", WHITE), ("price.py", WHITE)], TREE_C).move_to([LX, -0.05, 0])
        b_p0 = obj_box([("blob e7edc93", YELLOW_M)], BLOB_C).move_to([LX, -2.45, 0])
        l_ig, l_rm = entry_arrow(t0, 1, b_ig, 1), entry_arrow(t0, 2, b_rm, 1)
        l_p0 = harrow(t0[0].get_bottom() + DOWN * 0.05, b_p0[0].get_top() + UP * 0.08, GREY_B, sw=2.5)
        c_t0 = harrow(c0[0].get_bottom() + DOWN * 0.05, t0[0].get_top() + UP * 0.08, GREY_B, sw=2.5)
        par = harrow(c1[0].get_left() + LEFT * 0.08, c0[0].get_right() + RIGHT * 0.08, COMMIT_C)
        par_l = T("parent", 24, COMMIT_C).next_to(par, UP, buff=0.12)
        self.beat("So a file that did not change is the same blob in every commit. Here is the commit just before this one.",
                  LaggedStart(AnimationGroup(GrowArrow(par), FadeIn(par_l)), FadeIn(c0, shift=RIGHT * 0.2), GrowArrow(c_t0), FadeIn(t0, shift=DOWN * 0.2),
                              AnimationGroup(GrowArrow(l_ig), GrowArrow(l_rm), GrowArrow(l_p0)), FadeIn(b_p0), lag_ratio=0.3), run_time=3.4)
        self.beat("Both trees point to the same README blob. Git stores it once.",
                  l_rm.animate.set_color(YELLOW_M), r_rm.animate.set_color(YELLOW_M), Circumscribe(b_rm, color=YELLOW_M, buff=0.06), run_time=1.8)
        self.beat("The price file did change, so each commit points to its own blob for it.",
                  l_p0.animate.set_color(BLOB_C), r_p1.animate.set_color(BLOB_C), Circumscribe(b_p0, color=BLOB_C, buff=0.06), Circumscribe(b_p1, color=BLOB_C, buff=0.06), run_time=1.8)

        h_old, m_old = c1[1][0], c1[1][4]
        h_new = M("commit 91d8050", 20, RED_M).move_to(h_old, aligned_edge=LEFT)
        m_new = T("Group thousands in price", 22, RED_M).move_to(m_old, aligned_edge=LEFT)
        self.beat("A commit's hash covers its tree, its parent, its author line and its message. Change even one letter of the message, and you get a different commit, with a new hash.",
                  Indicate(VGroup(c1[1][1:4]), color=YELLOW_M, scale_factor=1.04), Succession(Wait(3.6), AnimationGroup(Transform(m_old, m_new), Transform(h_old, h_new))), run_time=5.6)
        self.beat("Remember that for Day 9. It is why a rebase gives your commits new IDs.",
                  Indicate(h_old, color=RED_M, scale_factor=1.15), run_time=1.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

        # ---------- 3. branches and HEAD are pointers
        Y = 0.3
        hashes = ["16cc719", "09e16be", "c711550", "d6aad6e"]
        hx_ = [-3.6, -1.8, 0.0, 1.8]
        dots = VGroup(*[cdot().move_to([x, Y, 0]) for x in hx_])
        labs = VGroup(*[M(h, 20, GREY_B).next_to(d, DOWN, buff=0.18) for h, d in zip(hashes, dots)])
        more = M("...", 26, GREY_B).move_to([-5.1, Y, 0])
        links = VGroup(*[harrow(dots[i + 1].get_left() + LEFT * 0.06, dots[i].get_right() + RIGHT * 0.06) for i in range(3)],
                       harrow(dots[0].get_left() + LEFT * 0.06, more.get_right() + RIGHT * 0.15))
        side = cdot().move_to([1.8, -1.3, 0])
        side_l = M("d229503", 20, GREY_B).next_to(side, DOWN, buff=0.18)
        side_a = edge_arrow(side, dots[2])
        self.beat("Commits point back to their parents, so history is a chain. You can follow it back, one parent at a time.",
                  LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15), FadeIn(labs), FadeIn(more),
                  LaggedStart(*[GrowArrow(a) for a in reversed(links[:3])], GrowArrow(links[3]), lag_ratio=0.2),
                  GrowFromCenter(side), FadeIn(side_l), GrowArrow(side_a), run_time=3.0)
        self.play(*[Indicate(dots[i], color=YELLOW_M, scale_factor=1.25, rate_func=late(0.22 * (3 - i), 0.22 * (3 - i) + 0.34, there_and_back)) for i in range(4)], run_time=2.0)

        def tag_at(t, x, y):
            return t.move_to([x, y, 0])

        main_t = tag_at(tag("main"), 1.8, 1.35)
        main_a = harrow(main_t.get_bottom() + DOWN * 0.04, dots[3].get_top() + UP * 0.06, PTR_C)
        mfile = obj_box([(".git/refs/heads/main", GREY_B), ("d6aad6e3057b617ea767db224d5348b52ca46c3f", PTR_C)], PTR_C).move_to([2.55, -3.05, 0])
        cf_t = tag_at(tag("currency-first"), 4.3, -1.35)
        cf_a = harrow(cf_t.get_left() + LEFT * 0.04, side.get_right() + RIGHT * 0.06, PTR_C)
        self.beat("A branch is a small file that holds one commit hash. main points to the newest commit on main.",
                  FadeIn(main_t, shift=DOWN * 0.15), GrowArrow(main_a), Succession(Wait(1.2), FadeIn(mfile, shift=UP * 0.15)), run_time=2.6)
        self.beat("And currency-first is another branch, pointing at the commit on its side branch.",
                  FadeIn(cf_t, shift=LEFT * 0.15), GrowArrow(cf_a), run_time=1.4)

        head_t = tag_at(tag("HEAD", WHITE), 1.8, 2.3)
        head_a = harrow(head_t.get_bottom() + DOWN * 0.04, main_t.get_top() + UP * 0.06, WHITE)
        hfile = obj_box([(".git/HEAD", GREY_B), ("ref: refs/heads/main", WHITE)], WHITE).move_to([-4.3, -3.05, 0])
        self.beat("HEAD answers the question: where am I? Usually it points to a branch, not to a commit.",
                  FadeIn(head_t, shift=DOWN * 0.15), GrowArrow(head_a), Succession(Wait(1.4), FadeIn(hfile, shift=UP * 0.15)), run_time=2.6)

        cmd = M("$ git commit -am 'Say that prices include VAT'", 26).move_to(UP * 3.35)
        nd = cdot(YELLOW_M).move_to([3.6, Y, 0])
        nd_l = M("6e176d6", 20, YELLOW_M).next_to(nd, DOWN, buff=0.18)
        nd_a = harrow(nd.get_left() + LEFT * 0.06, dots[3].get_right() + RIGHT * 0.06)
        self.beat("Now make a commit. Git writes a new commit object, and its parent is the commit main points to.",
                  Write(cmd), Succession(Wait(1.6), AnimationGroup(GrowFromCenter(nd), FadeIn(nd_l), GrowArrow(nd_a))), run_time=3.0)

        main_a2 = harrow(main_t.get_bottom() + DOWN * 0.04 + RIGHT * 1.8, nd.get_top() + UP * 0.06, PTR_C)
        mval = mfile[1][1]
        mval_new = M("6e176d6...", 20, PTR_C).move_to(mval, aligned_edge=LEFT)
        self.beat("Then it moves main forward to the new commit. HEAD comes along, because it points at main. No files get copied.",
                  VGroup(main_t, head_t, head_a).animate.shift(RIGHT * 1.8), Transform(main_a, main_a2),
                  Transform(mval, mval_new, rate_func=late(0.4)), run_time=2.4)
        self.beat("So git commit moves one pointer: the branch that HEAD points to. currency-first did not move at all.",
                  Indicate(main_t, color=PTR_C, scale_factor=1.15), Indicate(cf_t, color=GREY_B, scale_factor=1.08, rate_func=late(0.5, 1.0, there_and_back)), run_time=2.6)

        cmd2 = M("$ git reset --hard HEAD~2", 26).move_to(UP * 3.35)
        main_a3 = harrow(main_t.get_bottom() + DOWN * 0.04 + LEFT * 3.6, dots[2].get_top() + UP * 0.06, PTR_C)
        mval_back = M("c711550a5dd6a4cff3ec0eb68273f42a3d462a29", 20, PTR_C).move_to(mval, aligned_edge=LEFT)
        still = T("still in .git", 26, GREY_B).move_to([2.7, 1.35, 0])
        self.beat("Most undo commands work the same way. A hard reset two commits back moves main to an older commit, and resets your files to match.",
                  Transform(cmd, cmd2), VGroup(main_t, head_t, head_a).animate.shift(LEFT * 3.6), Transform(main_a, main_a3),
                  Transform(mval, mval_back, rate_func=late(0.4)), run_time=2.4)
        self.beat("The newer commits are not deleted. They are still in .git, and the reflog can lead you back to them.",
                  VGroup(dots[3], nd, links[2], nd_a).animate.set_opacity(0.35), VGroup(labs[3], nd_l).animate.set_opacity(0.5), FadeIn(still, shift=UP * 0.1), run_time=2.0)

        recap = T("a commit = a full snapshot, named by its hash.   branches and HEAD = pointers.", 28, YELLOW_M).move_to(UP * 3.35)
        fit(recap, 13.2)
        self.beat("A commit is a full snapshot, named by a hash of its content. Branches and HEAD are pointers, and git commit moves the branch HEAD points to.",
                  FadeOut(cmd), Write(recap), run_time=3.0)
        self.wait(1.2)
