import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\bapp\.py\b", "app dot pie"), (r"\bcosign\b", "co-sign"), (r"\bOIDC\b", "O I D C"), (r"\bSLSA\b", "salsa"), (r"\bCVE\b", "C V E")])

# caption timestamps: round to whole milliseconds first, so a cue never reads "00:01:60.000"
import fg as _fg


def _ts_ms(t):
    ms = int(round(t * 1000))
    h, r = divmod(ms, 3600000); m, r = divmod(r, 60000); s, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


_fg._ts = _ts_ms



def panel(rows, color, buff=0.28):
    fr = RoundedRectangle(corner_radius=0.12, width=rows.width + 2 * buff, height=rows.height + 2 * buff, stroke_color=color, stroke_width=2.5)
    fr.set_fill(interpolate_color(ManimColor("#000000"), ManimColor(color), 0.10), 1)
    return VGroup(fr, rows.move_to(fr))


class D63SupplyChain(VoiceScene):
    def construct(self):
        self.title_card("The software supply chain", "where it can be tampered with, and the check at each link")

        # ---------- 1. the image is mostly other people's work
        fr = RoundedRectangle(corner_radius=0.15, width=6.6, height=4.0, stroke_color=BLUE_M, stroke_width=3).move_to([0, -0.3, 0])
        flab = T("hello-devops image", 26, BLUE_M).next_to(fr, UP, buff=0.15)

        def layer(txt, h, col, w=6.0):
            r = Rectangle(width=w, height=h, stroke_color=col, stroke_width=2).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(col), 0.22), 1)
            return VGroup(r, T(txt, 24).move_to(r))
        deb = layer("87 Debian packages (base image)", 1.25, GREY_B)
        py = layer("Python", 0.62, YELLOW_M)
        pk = layer("about 10 Python packages", 0.62, TEAL_M)
        app = layer("app.py", 0.5, BLUE_M, w=1.6)
        stack = VGroup(deb, py, pk, app).arrange(UP, buff=0.12)
        app.align_to(pk, LEFT)
        stack.move_to(fr)
        self.beat("Your hello-devops image is mostly other people's work. Your own code is one file, app.py.",
                  Create(fr), FadeIn(flab), FadeIn(app, shift=DOWN * 0.15), run_time=2.2)
        self.beat("The rest is 87 Debian packages from the base image, Python itself, and about 10 Python packages, such as Flask, gunicorn and redis.",
                  LaggedStart(FadeIn(deb, shift=UP * 0.15), FadeIn(py, shift=UP * 0.15), FadeIn(pk, shift=UP * 0.15), lag_ratio=0.6), run_time=4.0)

        # ---------- 2. the chain, link by link
        names = ["Code", "Libraries", "CI build", "Registry", "Cluster"]
        xs = [-5.6, -2.8, 0.0, 2.8, 5.6]
        links = [box(n, GREY_B, w=1.95, size=26).move_to([x, 0.55, 0]) for n, x in zip(names, xs)]
        arr = [Arrow(links[i].get_right(), links[i + 1].get_left(), buff=0.1, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.4) for i in range(4)]
        self.play(FadeOut(VGroup(fr, flab, deb, py, pk, app)), run_time=0.7)
        self.beat("Everything your code passes through on its way to production is your software supply chain. Follow it from source to a running Pod.",
                  LaggedStart(*[AnimationGroup(Create(l[0]), Write(l[1])) for l in links], lag_ratio=0.3),
                  Succession(Wait(1.2), LaggedStart(*[GrowArrow(a) for a in arr], lag_ratio=0.3)), run_time=4.0)
        self.play(Succession(*[travel(a, run_time=0.45) for a in arr]), run_time=1.8)
        self.beat("A supply chain attack goes after one of these links instead of your code. It works because you trust the pieces, and run them without reading them.",
                  LaggedStart(*[Indicate(l, color=RED_M, scale_factor=1.06) for l in links], lag_ratio=0.25), run_time=3.6)

        def bad(txt, i):
            return T(txt, 22, RED_M).next_to(links[i], UP, buff=0.3)

        def good(txt, i):
            return chip(txt, GREEN_M, 22).next_to(links[i], DOWN, buff=0.35)

        def story(*lines):
            g = VGroup(*[T(t, 24, GREY_B) for t in lines]).arrange(DOWN, buff=0.16)
            return g.move_to([0, -2.6, 0])

        def focus(i):
            return [links[j][0].animate.set_stroke(RED_M if j == i else GREY_B, width=5 if j == i else 3) for j in range(5)]

        b0, g0 = bad("leaked token", 0), good("secret scan", 0)
        s0 = story("a token in a commit:", "a minute before git push, a weekend in production")
        self.beat("It starts with your own code. A leaked token caught before git push costs a minute. Found in production, it costs a weekend of rotating keys.",
                  *focus(0), FadeIn(b0, shift=DOWN * 0.1), FadeIn(s0), Succession(Wait(2.4), FadeIn(g0, shift=UP * 0.1)), run_time=4.6)

        b1, g1 = bad("xz 2024", 1), good("SBOM, scan", 1)
        s1 = story("xz 5.6.0 and 5.6.1: a backdoor in the release tarballs,", "not in the git repository where reviewers look")
        self.beat("Next, the libraries. In 2024, a contributor who had earned the maintainer's trust hid a backdoor in xz, a small compression library, in versions 5.6.0 and 5.6.1.",
                  *focus(1), FadeOut(s0), FadeIn(b1, shift=DOWN * 0.1), FadeIn(s1[0]), run_time=3.0)
        self.beat("It sat in the release tarballs, not in the git repository, where reviewers look. So you need to know exactly what you ship.",
                  FadeIn(s1[1]), Succession(Wait(2.6), FadeIn(g1, shift=UP * 0.1)), run_time=4.0)

        b2 = VGroup(T("tj-actions 2025", 22, RED_M), T("Trivy 2026", 22, RED_M)).arrange(DOWN, buff=0.1).next_to(links[2], UP, buff=0.3)
        g2 = good("pin SHAs", 2)
        s2 = story("a tag was moved to a malicious commit:", "every workflow using that tag ran the attacker's code")
        self.beat("Then the build. In March 2025, attackers moved the version tags of the tj-actions/changed-files action to a malicious commit. Workflows that used those tags printed their CI secrets into the build log.",
                  *focus(2), FadeOut(s1), FadeIn(b2[0], shift=DOWN * 0.1), FadeIn(s2), run_time=3.0)
        self.beat("In March 2026, the scanner Trivy was hit the same way: 76 of the 77 trivy-action tags were force-pushed.",
                  FadeIn(b2[1], shift=DOWN * 0.1), run_time=1.6)
        u1 = M("uses: some-org/action@v4", 24, RED_M).move_to([0, -2.6, 0])
        u2 = M("uses: some-org/action@<full 40-character SHA>", 24, GREEN_M).move_to([0, -2.6, 0])
        self.beat("A tag can be moved. A commit SHA cannot, because it is a hash of the commit's content. So the workflow pins every third-party action to its full SHA.",
                  FadeOut(s2), Succession(FadeIn(u1), Wait(2.2), AnimationGroup(ReplacementTransform(u1, u2), FadeIn(g2, shift=UP * 0.1))), run_time=5.0)

        b3, g3 = bad("tag pushed again", 3), good("sign, attest", 3)
        r1 = M("hello-devops:1.2.0" + " " * 12 + "can be pushed again", 22, RED_M)
        r2 = M("hello-devops@sha256:<64 hex>  cannot change", 22, GREEN_M)
        rr = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -2.6, 0])
        self.beat("At the registry, someone can push hello-devops:1.2.0 again, with new content. A digest cannot change. So the workflow signs the digest.",
                  *focus(3), FadeOut(u2), FadeIn(b3, shift=DOWN * 0.1), FadeIn(r1), Succession(Wait(2.6), AnimationGroup(FadeIn(r2), FadeIn(g3, shift=UP * 0.1))), run_time=4.6)

        g4 = good("verify first", 4)
        pod = Circle(radius=0.22, stroke_color=TEAL_M, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(TEAL_M), 0.25), 1)
        pod.next_to(links[4], UP, buff=0.35)
        s4 = story("signatures and attestations protect nothing", "until someone checks them")
        self.beat("The last link is the cluster, where the Pod runs. Signatures protect nothing until someone checks them. So you verify, before you run.",
                  *focus(4), FadeOut(rr), GrowFromCenter(pod), FadeIn(s4), Succession(Wait(2.8), FadeIn(g4, shift=UP * 0.1)), run_time=4.6)
        self.play(*[l[0].animate.set_stroke(GREY_B, width=3) for l in links], FadeOut(s4), run_time=0.6)
        self.wait(0.6)

        # ---------- 3. SBOM and scan
        chain = VGroup(*links, *arr, b0, b1, b2, b3, g0, g1, g2, g3, g4, pod)
        self.play(FadeOut(chain), run_time=0.8)
        img = box("hello-devops:1.2.0", BLUE_M, size=24).move_to([-4.9, 0.9, 0])
        sb_rows = VGroup(T("SBOM", 24, YELLOW_M), M("base-files   x.y.z", 20), M("libssl3      x.y.z", 20), M("python       3.14", 20),
                         M("flask        x.y.z", 20), M("gunicorn     x.y.z", 20), M("…  every package", 20, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        sbom = panel(sb_rows, YELLOW_M).move_to([-0.6, 0.6, 0])
        a_syft = edge_arrow(img, sbom, YELLOW_M)
        syl = M("syft", 22, YELLOW_M).next_to(a_syft, UP, buff=0.12)
        fmt = T("SPDX or CycloneDX", 22, YELLOW_M).next_to(sbom, DOWN, buff=0.2)
        self.beat("Now the checks. An SBOM, a software bill of materials, is the ingredient list of the image: every package and version, in a format machines can read.",
                  Create(img[0]), Write(img[1]), Succession(Wait(1.0), AnimationGroup(GrowArrow(a_syft), Create(sbom[0]),
                  LaggedStart(*[FadeIn(r, shift=DOWN * 0.08) for r in sb_rows], lag_ratio=0.2))), run_time=4.4)
        self.beat("The tool syft reads an image and writes one, in SPDX or CycloneDX format.",
                  FadeIn(syl), FadeIn(fmt), run_time=1.6)

        scan = box("Trivy or grype", RED_M, size=24).move_to([3.95, 0.6, 0])
        a_sc = edge_arrow(sbom, scan, GREY_B)
        db = box("public CVE databases", GREY_B, size=22, h=0.7).move_to([3.95, 2.45, 0])
        a_db = edge_arrow(db, scan, GREY_B)
        sev = VGroup(*[chip(t, c, 20, mono=True) for t, c in (("LOW", GREY_B), ("MEDIUM", YELLOW_M), ("HIGH", GOLD_M), ("CRITICAL", RED_M))]).arrange(RIGHT, buff=0.15)
        sev.next_to(scan, DOWN, buff=0.45)
        self.beat("A scanner such as Trivy or grype matches that list against public databases of known holes. Each hole has a CVE ID, and a severity.",
                  GrowArrow(a_sc), Create(scan[0]), Write(scan[1]), Succession(Wait(1.2), AnimationGroup(Create(db[0]), Write(db[1]), GrowArrow(a_db))),
                  Succession(Wait(3.0), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in sev], lag_ratio=0.2)), run_time=5.6)
        cfg = VGroup(M("severity: CRITICAL,HIGH", 22), M("ignore-unfixed: true", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        cfg.next_to(sev, DOWN, buff=0.4)
        fail = SurroundingRectangle(VGroup(sev[2], sev[3]), buff=0.08, color=RED_M, stroke_width=3)
        self.beat("The release workflow fails on HIGH and CRITICAL findings that already have a fixed version.",
                  Create(fail), FadeIn(cfg, shift=UP * 0.1), run_time=2.4)

        olds = VGroup(*[panel(VGroup(T("SBOM", 20, YELLOW_M), M(v, 20)).arrange(DOWN, buff=0.1), YELLOW_M, buff=0.18) for v in ("1.0.0", "1.1.0", "1.2.0")])
        olds.arrange(RIGHT, buff=0.25).move_to([-3.2, -2.55, 0])
        q = M("grype sbom:./sbom.spdx.json", 22, GREY_B).next_to(olds, RIGHT, buff=0.45)
        self.beat("Keep every SBOM. On the morning the next xz is announced, you search the files, and have your answer in minutes.",
                  LaggedStart(*[FadeIn(o, shift=UP * 0.15) for o in olds], lag_ratio=0.3), Succession(Wait(2.0), Write(q)), run_time=4.0)

        # ---------- 4. keyless signing with cosign
        self.play(FadeOut(VGroup(img, a_syft, syl, sbom, fmt, scan, a_sc, db, a_db, sev, cfg, fail, olds, q)), run_time=0.8)
        job = box("release job", BLUE_M, size=26).move_to([-4.9, 2.35, 0])
        cos = box("cosign", GOLD_M, w=1.9, size=26).move_to([-4.9, 0.05, 0])
        ful = box("Fulcio", TEAL_M, w=1.9, size=26).move_to([0.6, 2.35, 0])
        fl = T("certificate authority", 20, TEAL_M).next_to(ful, DOWN, buff=0.12)
        reg = RoundedRectangle(corner_radius=0.15, width=6.6, height=1.75, stroke_color=GREY_B, stroke_width=2).move_to([0.2, -2.35, 0])
        regl = T("registry", 22, GREY_B).move_to(reg.get_corner(UR) + np.array([-0.75, -0.35, 0]))
        dig = M("hello-devops@sha256:…", 22, BLUE_M).move_to(reg.get_top() + DOWN * 0.4)
        self.beat("Next, sign the image. A signature answers two questions: who made it, and has anyone changed it since? cosign, from the Sigstore project, signs without a stored key.",
                  Create(job[0]), Write(job[1]), Succession(Wait(2.4), AnimationGroup(Create(cos[0]), Write(cos[1]), Create(reg), FadeIn(regl), FadeIn(dig))), run_time=5.0)
        tok = chip("OIDC token: release.yml, tag v1.2.0", BLUE_M, 20).next_to(job, RIGHT, buff=0.3).shift(UP * 0.8)
        self.beat("The release job asks GitHub for an OIDC token: a short signed note that says, I am release.yml in this repository, running for tag v1.2.0.",
                  FadeIn(tok, shift=RIGHT * 0.2), run_time=1.6)
        key = chip("key pair, in memory only", GOLD_M, 20).move_to([-4.9, 1.2, 0])
        cert = chip("certificate: 10 minutes, identity release.yml", TEAL_M, 20).move_to([0.9, 0.05, 0])
        self.beat("cosign makes a fresh key pair that lives only in memory. Fulcio checks the token, and issues a certificate for that key. It is valid for 10 minutes, with the workflow identity written inside.",
                  FadeIn(key, shift=UP * 0.1),
                  Succession(Wait(1.6), AnimationGroup(Create(ful[0]), Write(ful[1]), FadeIn(fl)), tok.animate.next_to(ful, UP, buff=0.12),
                             Wait(0.4), FadeIn(cert, shift=DOWN * 0.15), cert.animate.next_to(cos, RIGHT, buff=0.2)), run_time=7.0)
        sig = chip("signature", GOLD_M, 20).move_to(reg.get_bottom() + UP * 0.5 + LEFT * 2.0)
        a_sig = Arrow(cos.get_bottom(), sig.get_top(), buff=0.12, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.12)
        self.beat("cosign signs the image digest, never a tag, and stores the signature in the registry, next to the image.",
                  Indicate(dig, color=YELLOW_M), GrowArrow(a_sig), Succession(Wait(0.8), FadeIn(sig, shift=DOWN * 0.15)), run_time=3.0)
        rek = box("Rekor", PURPLE_M, w=1.9, size=26).move_to([5.3, 2.35, 0])
        rkl = T("public log", 20, PURPLE_M).next_to(rek, DOWN, buff=0.12)
        logs = VGroup(*[Line(LEFT * 0.75, RIGHT * 0.75, stroke_width=3, color=GREY_D) for _ in range(3)]).arrange(DOWN, buff=0.16).next_to(rkl, DOWN, buff=0.22)
        entry = M("+ signing event", 20, PURPLE_M).next_to(logs, DOWN, buff=0.16)
        self.beat("The signing event also goes into Rekor, a public log that only grows. Nobody can quietly remove or rewrite an entry.",
                  Create(rek[0]), Write(rek[1]), FadeIn(rkl), FadeIn(logs), Succession(Wait(1.2), FadeIn(entry, shift=DOWN * 0.1)), run_time=3.0)

        # ---------- 5. attestations: how it was built
        prov_rows = VGroup(T("provenance", 22, GREEN_M), T("repository", 20), T("commit", 20), T("workflow file", 20), T("kind of runner", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        prov = panel(prov_rows, GREEN_M, buff=0.22).move_to([5.3, -1.75, 0])
        self.play(FadeOut(VGroup(tok, cert, key, a_sig)), run_time=0.6)
        self.beat("A signature says who signed. Provenance says how the image was built: which repository, which commit, which workflow file, and which kind of runner.",
                  Create(prov[0]), LaggedStart(*[FadeIn(r, shift=DOWN * 0.08) for r in prov_rows], lag_ratio=0.35), run_time=4.0)
        at1 = chip("provenance (SLSA)", GREEN_M, 20).move_to(reg.get_bottom() + UP * 0.5 + RIGHT * 0.15)
        at2 = chip("SBOM", YELLOW_M, 20).move_to(reg.get_bottom() + UP * 0.5 + RIGHT * 2.25)
        at = M("actions/attest", 22, GREEN_M).move_to([-0.6, 0.15, 0])
        self.beat("The workflow calls actions/attest twice: once for the SLSA provenance, and once to attach the SBOM. Both are signed, and bound to the same digest.",
                  FadeIn(at), Succession(Wait(1.6), ReplacementTransform(prov.copy(), at1), Wait(0.6), FadeIn(at2, shift=DOWN * 0.15), Indicate(dig, color=YELLOW_M)),
                  run_time=5.6)

        # ---------- 6. verify before deploy
        keep = VGroup(reg, dig, sig, at1, at2)
        self.play(FadeOut(VGroup(job, cos, ful, fl, rek, rkl, logs, entry, prov, at, regl)), keep.animate.move_to([-2.9, -2.45, 0]), run_time=1.0)
        cmd = VGroup(M("cosign verify ghcr.io/<user>/hello-devops@sha256:<digest> \\", 20),
                     M("  --certificate-identity …/release.yml@refs/tags/v1.2.0 \\", 20, YELLOW_M),
                     M("  --certificate-oidc-issuer https://token.actions.githubusercontent.com", 20, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        cmd.move_to([0, 2.75, 0])
        self.beat("GitHub's docs warn that attestations alone give no security benefit. Someone has to check them, before the deploy.",
                  Indicate(keep, color=WHITE, scale_factor=1.03), run_time=2.0)
        self.beat("cosign verify names the identity you expect: your workflow file and tag, and GitHub's token issuer.",
                  Write(cmd[0]), Succession(Wait(1.0), FadeIn(cmd[1], shift=RIGHT * 0.1), FadeIn(cmd[2], shift=RIGHT * 0.1)), run_time=3.2)
        checks = ["the signature matches the digest", "Fulcio issued the certificate", "the identity is the one you named"]
        crow = VGroup(*[VGroup(tick(True, 0.16), T(c, 24)).arrange(RIGHT, buff=0.25) for c in checks]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        crow.move_to([-2.4, 0.85, 0])
        self.beat("It checks that the signature matches the digest, that Fulcio issued the certificate, and that the identity inside is the one you named.",
                  LaggedStart(*[AnimationGroup(Create(r[0]), FadeIn(r[1], shift=RIGHT * 0.1)) for r in crow], lag_ratio=0.7), run_time=5.0)
        fake = VGroup(chip("image signed by someone else", RED_M, 22)).move_to([3.6, 0.85, 0])
        xx = tick(False, 0.3).next_to(fake, RIGHT, buff=0.25)
        self.beat("An image signed by anyone else fails.",
                  FadeIn(fake, shift=LEFT * 0.2), Succession(Wait(0.6), Create(xx)), run_time=1.8)
        gh = VGroup(M("gh attestation verify", 22, GREEN_M), VGroup(tick(True, 0.16), T("provenance", 24)).arrange(RIGHT, buff=0.2),
                    VGroup(tick(True, 0.16), T("SBOM", 24)).arrange(RIGHT, buff=0.2)).arrange(RIGHT, buff=0.45)
        gh.next_to(crow, DOWN, buff=0.4).align_to(crow, LEFT)
        clus = box("Cluster", TEAL_M, w=2.3, h=1.5, size=26).move_to([4.6, -2.45, 0])
        clus[1].move_to(clus[0].get_top() + DOWN * 0.35)
        pod2 = Circle(radius=0.24, stroke_color=TEAL_M, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(TEAL_M), 0.3), 1).move_to(clus[0].get_center() + DOWN * 0.25)
        a_dep = Arrow([0.45, -2.45, 0], clus.get_left(), buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.1)
        depl = M("deploy @sha256:…", 22, GREEN_M).next_to(a_dep, UP, buff=0.12)
        self.beat("gh attestation verify checks the provenance and the SBOM the same way. When all of it passes, deploy that exact digest, not the tag.",
                  FadeOut(VGroup(fake, xx)), FadeIn(gh[0]), Succession(Wait(1.0), AnimationGroup(Create(gh[1][0]), FadeIn(gh[1][1])), AnimationGroup(Create(gh[2][0]), FadeIn(gh[2][1])),
                  AnimationGroup(Create(clus[0]), Write(clus[1]), GrowArrow(a_dep), FadeIn(depl)), GrowFromCenter(pod2)), run_time=6.0)

        # ---------- recap
        self.beat("Each link gets its own check. And the last check is yours: verify before you run.",
                  Indicate(pod2, color=GREEN_M, scale_factor=1.3), Circumscribe(VGroup(crow, gh), color=GREEN_M), run_time=3.0)
        self.wait(1.0)
