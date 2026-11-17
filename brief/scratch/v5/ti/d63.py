"""Fifth pass (book voice) for d63, The software supply chain. Writer: ti.
Replaces only prose fields of d63 in content/p17.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p17.json"
P = json.loads(PATH.read_text())
L = next(x for x in P["lessons"] if x["id"] == "d63")

L["goal"] = ("By the end you can explain how attackers get into the chain of other people's software behind your app, "
             "and list, scan, sign and check the hello-devops image, so you know what you ship and who built it.")

L["opening"] = """Picture a small shop that sells its own jam. You cook it in your own kitchen, but very little in each jar is really yours. The fruit comes from a farm, the sugar from a mill, and the jars and lids from a factory. One morning the radio says that someone poisoned a batch of sugar at that mill, on purpose. The phone starts ringing. Which of your jars have that sugar in them?

You never wrote it down, because the mill had always been fine. That is an easy trap to fall into. Trusting good suppliers is what lets a small shop work at all.

Last time, we watched an app closely while it ran. Watching shows what an app does. It can't show what went into it. In this lesson, we'll write the ingredient label for the hello-devops app, check it for known problems, seal it, and check the seal before we ship. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = ("Your build uses a ready-made step from another project, written as `some-org/scan-action@v4`. "
                   "An attacker steals the secret token of the person who looks after that project and adds new code. "
                   "What runs in your next build?")
L["guess"]["why"] = ("The `v4` is a tag, a name that can be moved to different code, and attackers moved the tags of "
                     "tj-actions in 2025 and trivy-action in 2026. Nobody can move a full commit SHA, the fingerprint of one exact version.")

plain = {
    "Software supply chain": "Everything your app passes through on its way to real users: other people's code, the starting image, build tools, ready-made build steps and the site that stores the result.",
    "Supply chain attack": "An attack on something you rely on, so that your own build ships the attacker's code.",
    "CVE": "A public ID for one known security hole, such as CVE-2024-3094 for the hidden way in that was planted in xz.",
    "SBOM": "Software bill of materials: a list, written for computers to read, of every piece of software and its version inside what you ship.",
    "SHA pinning": "Naming a ready-made build step by its full 40-character commit fingerprint, which always means the same code, instead of a name that can be moved.",
    "Keyless signing": "Signing with a pass that is valid for 10 minutes and names the signer, such as your release workflow, so no secret signing key is ever stored.",
    "Provenance": "A signed record of how something was built: which code store, which saved version and which set of build steps made it.",
    "SLSA": "Supply-chain Levels for Software Artifacts: build levels 0 to 3 that grade how far you can trust a build.",
}
for t in L["terms"]:
    t["plain"] = plain[t["term"]]

S = L["sections"]

S[0]["h"] = "Your image is mostly other people's work"
S[0]["body"] = """The jam shop's first job is to count what came from somewhere else. Our app, hello-devops, is the tiny web app this course builds. It answers every visit with a greeting and a count of visits so far. On Day 22 you packed it into an image: a sealed bundle of files that holds an app and everything it needs to run. Your own code in that image is one file, `app.py`. The rest is packages, bundles of ready-made code that other people wrote, each with a name and a version:
- 87 Debian packages from the `python:3.14-slim` base image, the starting image you build on.
- Python itself.
- Flask, gunicorn, redis and their dependencies: about 10 Python packages.

Debian is one kind of Linux, the free operating system on most servers. A dependency is a package that another package needs. So the jar is almost all bought fruit and sugar, with one spoon of your own recipe.

And that is only what ships. Your release workflow is a file of steps that GitHub, the site that stores your code, runs for you on a borrowed computer called a runner. Even the runner is someone else's code.

The workflow's steps use actions, ready-made steps other people wrote: the Docker actions, a scanner and a signing tool. Each one runs with your workflow's rights. So each one could read the workflow's token, a secret string that works like a key card.

That whole set is your software supply chain: every piece your code passes through between your keyboard and production, where real users reach the app. A supply chain attack goes after one of those pieces instead of your code. Like the poisoned sugar, it works because you trust the pieces and use them without opening them.

DevSecOps is how teams answer this: security checks built into the chain as automatic steps, owned by the people who ship. It rests on two ideas:
1. Shift left: run cheap checks early (left means earlier, on a timeline). A leaked token caught before it leaves your laptop costs a minute. Found in production, it costs a weekend of replacing keys.
2. Least privilege: every person, token and running app gets only the rights it needs, for as short a time as possible.

You met both already: the `permissions:` block on Day 27, and the non-root user on Day 22. What happens when one link turns bad? Three real attacks show it."""

S[1]["h"] = "Three real attacks, three different weak links"
S[1]["body"] = """None of these attacks touched the victims' own code. Each hit a different link, like poison in the sugar, the lids or the van.

The xz-utils backdoor (2024). A backdoor is a hidden way in. xz is a small compression library (code that makes files smaller) that almost every Linux system has.

Its maintainer, the volunteer who looks after it, came to trust a new contributor over time. That contributor then hid malicious code in the release tarballs of versions 5.6.0 and 5.6.1. A tarball is a packed .tar.gz file, much like a zip file. The code was not in the project's stored history, where reviewers look. It sat in extra build files inside the tarballs.

Ready-to-install versions of Linux, such as Debian, build from those tarballs. Some of them link SSH to xz's library indirectly. SSH is how people log in to a computer from far away, so on those systems the backdoor ran inside SSH. A developer, Andres Freund, was measuring speed when he saw SSH logins using too much computer power. He traced it to xz. The [GitHub advisory](https://github.com/advisories/GHSA-rxwq-x6h5-x525), a public warning, scores it 10 out of 10.

tj-actions/changed-files (March 2025). Attackers moved this popular GitHub Action's version tags to a malicious commit (a saved change of their own). For about a day, every workflow using one of those tags ran a script that printed CI secrets into the build log. CI (continuous integration) is the automatic build and test on every change. In a public repository, anyone can read that log. [GitHub's advisory](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3) says over 23,000 repositories used the action.

Trivy (March 2026). Trivy is a security scanner (a tool that checks software for known holes), the same one in your release workflow. After an earlier break-in, the attackers still had working credentials (passwords and tokens), because the key rotation (replacing every key) was not done all at once. On 19 March they published a malicious Trivy v0.69.4 and moved 76 of the 77 `trivy-action` tags by force. The bad code stole secrets, then ran the real scan, so builds looked normal. [Aqua's advisory](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23) notes that images pulled by digest were not affected. Hold on to that detail.

Each attack leaves a rule:
- A trusted maintainer can turn bad, so know exactly what you ship.
- A tag can be moved, so pin to what cannot move: commit SHAs and image digests.
- Security tools are part of the chain. After an incident, rotate every secret a bad step could read.

The second rule is the cheapest to follow, so we start there. Why can a tag move at all?"""

S[2]["h"] = "Why a tag can move and a commit SHA cannot"
S[2]["body"] = """Here is the naive way to use an action, as many examples write it: `uses: some-org/action@v4`. It reads like a fixed version, but the `v4` is a git tag. Git records your code's history as commits, saved snapshots of every file. A tag is a name that points at one commit, like a sticky note on a page. Anyone allowed to change that repository can peel the note off and stick it on another commit.

Your next run executes the new code, though nothing in your own repository changed. The worked example below does exactly this: the tag `v1` points at commit `fdc7302`, then one command later at `2df87fd`.

A commit SHA is a 40-character hash of the commit's content: its files, its parent commit, its author and its message. A hash is a fingerprint worked out from content. Change one byte and you get a different SHA, so `uses: some-org/action@<full-sha>` always means the same code. In March 2026 the attacker moved 76 `trivy-action` tags, and every old SHA still pointed at the code it always had.

**A tag can be moved by anyone who holds the key. Pin the SHA.** The scan step in the lab's `release.yml` does just that:
`uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0`

GitHub runs the SHA. The part after `#` is a comment, a note only for humans. Dependabot (Day 27), a GitHub robot that watches for new releases, updates the SHA and the comment together. The price: pinned code never changes by itself, so you need a bot to bring fixes and a person to review them.

Image tags move too. Someone can push `hello-devops:1.2.0` again with new content. A digest cannot change. It is `@sha256:` followed by 64 letters and digits, a fingerprint of the image itself. That explains the Trivy detail: images pulled by digest were not affected. It is also why the workflow signs the digest.

Pinning keeps the build steps honest. It says nothing about the 87 packages inside the image, so next we write those down."""

S[3]["h"] = "Writing the ingredient label: SBOMs and scanners"
S[3]["body"] = """The poisoned sugar was a crisis only because nobody had written down which jars held it. An SBOM (software bill of materials) is that list for software: every package and version inside an artifact, in a format machines can read. An artifact is any finished thing a build makes, such as our image. The tool `syft` reads an image and writes its SBOM in a standard format such as SPDX.

You need that list most on the morning the next xz is announced. Without SBOMs, every team pulls and inspects its images. With an SBOM stored for every release, you search the files and have the answer in minutes.

A scanner compares that list with public databases of known security holes. Each hole has a public ID called a CVE, and a severity: LOW, MEDIUM, HIGH or CRITICAL.

Trivy and grype, the two common free scanners, each download a database built from public sources, such as the US National Vulnerability Database and the security notices of Linux distributions. They match every package name and version against it. In the shop, that is checking your label against the food recall list.

Scanners have two limits:
- They cannot find a backdoor nobody has reported yet. The xz code had no CVE until the day it was found.
- They go stale. New CVEs are published against old packages every day.

So scan in CI, and scan the stored SBOMs again on a schedule. The command `grype sbom:./sbom.spdx.json` checks an old release without pulling the image from the registry, the online store for images.

Decide in advance what fails the build. My rule: fail on HIGH and CRITICAL findings that already have a fixed version, and track the rest. A finding with no fix gives you nothing to update to, so failing on it only blocks releases. The release workflow does this with `severity: CRITICAL,HIGH` and `ignore-unfixed: true`. When it fails, update first, then remove what you do not need. Only then accept a risk in a `.trivyignore` file, with a reason and a date.

Now we know what is in the jar, but not who filled it or whether anyone opened it. That is a job for a seal."""

S[4]["h"] = "A seal on the jar: who built this, and has it changed?"
S[4]["body"] = """A scan tells you what is inside. A signature answers two more questions: who made this artifact, and has anyone changed it since? It is the jar's tamper-evident seal, stamped with the factory's mark. Classic signing uses two matching keys: a private one that only the signer holds, and a public one anyone can check with. In CI, the private key is one more secret to leak.

Keyless signing removes the stored key. The tool is cosign, from the free Sigstore project.

It relies on a certificate, a signed card that ties a key to a name, issued by a certificate authority (Day 11). When the release job signs, five things happen:
1. The job asks GitHub for an OIDC token: a short signed note that says "I am release.yml in this repository, running for tag v1.2.0".
2. cosign makes a fresh key pair that lives only in memory.
3. Fulcio, Sigstore's certificate authority, checks the token and issues a certificate for that key. It is valid for 10 minutes and has the workflow identity written inside.
4. cosign signs the image digest and stores the signature in the registry, next to the image.
5. The signing event goes into Rekor, a public log that only grows. Nobody can quietly remove or rewrite an entry.

To verify, you tell `cosign verify` the identity you expect: your workflow file, your tag and GitHub's token service. Then cosign checks that the signature matches the digest, that Fulcio issued the certificate, and that the identity inside is yours. An image signed by anyone else fails.

A pass tells you where the image came from and that nobody changed it. Like a seal, it says nothing about quality: a signed image can still be full of bugs.

The [cosign README](https://github.com/sigstore/cosign/blob/main/README.md) adds two warnings. Sign the digest, never a tag, or you might sign something you did not intend. And signing as a person has a privacy cost, which Go deeper explains. The seal says who packed the jar; next, we record how it was made."""

S[5]["h"] = "The delivery note: provenance, SLSA and attestations"
S[5]["body"] = """A signature says who signed. Provenance says how the thing was built: which repository, commit, workflow file and kind of runner. In the shop, it is the delivery note naming the factory and the production line. It is a signed statement bound to the artifact's digest, so it fits only that one image.

SLSA (say "salsa") grades how far you can trust that statement. Below, a hosted build platform is a build service someone else runs, such as GitHub's, and tampering means secret changes. The build track of the [SLSA spec](https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md) has four levels:
- Build L0: no guarantees.
- Build L1: provenance exists. It catches mistakes, but anyone could have written it.
- Build L2: a hosted build platform signs the provenance. Any later edit breaks the signature, so it catches tampering after the build.
- Build L3: a hardened build platform. Builds are kept apart, and build steps cannot reach the signing key, so it catches tampering during the build.

GitHub artifact attestations, signed statements attached to an artifact, give you Build L2 in one step. The lab calls `actions/attest@v4` twice. With no SBOM input it writes SLSA provenance. With `sbom-path` it attaches the SBOM as a second signed attestation. Moving the build into a shared reusable workflow (Day 26) is GitHub's documented path to L3.

Most teams stop there, and [GitHub's own docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations) warn that generating attestations alone gives no security benefit. A person or a machine has to verify them, for example with `gh attestation verify` before a deploy. To deploy is to put a new version where users reach it.

**A seal nobody checks protects nobody. Verify before you deploy.** For a deploy by hand, run `security/verify-release.sh` from Files below. Later, the cluster (the group of machines that runs your app) can refuse unverified images, as Go deeper shows. Next, we put every piece in the order the workflow runs them."""

S[6]["h"] = "Following one release through the workflow"
S[6]["body"] = """Open `.github/workflows/release.yml` in Files below and follow one tag push through it. A tag push starts a release: you name a commit `v1.2.0` and send the name to GitHub. The file has one job, a group of steps on one runner, and each step sits where it does for a reason:
1. `permissions:` gives this job four rights: read the code, push packages, ask for an OIDC token, write attestations.
2. Build once for the runner's own platform with `load: true`. The image exists locally, and nothing is pushed yet. Step 4 pushes as it builds, so this extra build is what lets the job scan first.
3. Scan that local image with Trivy. If the scan fails, the job stops, and nothing bad reaches the registry.
4. Build and push for amd64 and arm64. This step outputs the digest.
5. Write the SBOM of the pushed digest with `anchore/sbom-action`.
6. Sign that digest with cosign.
7. Attest the provenance, then the SBOM, both bound to the same digest.

A platform here is a chip family: amd64 is in most servers, and arm64 is in Apple Silicon Macs. Every step after the push uses `${IMAGE}@${DIGEST}`, the image name joined to its fingerprint, never a tag. Every third-party action is pinned to a SHA, even the scanner attacked in March 2026.

You wrote this file on Day 27. Today adds steps 2, 3, 5, 6 and 7, and the two rights they need. Notice what it does not cover: where the workflow's secrets live, and who may change the cluster. Those are the next links to guard."""

L["aside"] = {
    "title": "If the certificate lasts ten minutes, why does a check next month still pass?",
    "body": "The certificate expired ten minutes after signing, yet a check next month still passes. The Rekor entry proves when the signature was made. That moment was inside the ten minutes, while the certificate was still valid. So cosign does not need the certificate to be valid today. It needs proof that the signing happened in time, and the public log is that proof.",
    "after": 4,
}

# analogy, mistake and real_world are woven into the opening and sections, so they go.
for k in ("analogy", "mistake", "real_world"):
    L.pop(k, None)

W = L["worked"]["steps"]
W[0]["say"] = ("First, make a throwaway repository, a fresh folder that git tracks, and play the maintainer of an action. "
               "Save one commit and tag it `v1`, the way an action publishes a release. "
               "`git rev-parse v1` prints the commit SHA that the tag points to.")
W[1]["say"] = ("Now you are the attacker, holding a stolen token. Change the code, commit it, and move the tag with `-f`, which forces the move. "
               "A workflow that says `@v1` would now run the new code, and its own file did not change at all.")
W[2]["say"] = ("The old commit is still there, and its SHA still names the old code. "
               "A workflow pinned to `fdc7302...` keeps running what you reviewed. "
               "Your hashes will differ from mine, because a SHA includes the author and the time.")
W[3]["say"] = ("Next, check a real pin. `git ls-remote` asks GitHub what a tag points to, without cloning (downloading the whole project). "
               "Release tags are often annotated, which means they are a small tag object of their own. "
               "The line ending in `^{}` is the commit underneath, and that commit's SHA is the one in the lab's workflow.")
W[4]["say"] = ("If the two ever disagree, either someone moved the tag after you pinned, or your comment is stale. "
               "In both cases the SHA is what runs. Dependabot opens a pull request, a proposed change for you to review, when a newer release appears. "
               "Review it like any other code. Delete the demo with `rm -rf /tmp/tagdemo`.")

L["diagram_caption"] = "Each link in the chain gets its own check, and the last check is yours: verify before you run."

T = L["task"]
T["steps"] = [
    "Install the tools with `brew install syft grype trivy cosign`. Homebrew (`brew`) installs command-line tools on a Mac.",
    "Build `hello-devops:1.2.0` on your laptop, as on Day 22. Write an SPDX SBOM with syft, then find the version of flask inside the JSON file it writes.",
    "Scan the image with trivy using the same gate as CI: HIGH and CRITICAL, fixed issues only, and `--exit-code 1` so a finding fails the run. Then scan the saved SBOM with grype and compare the two reports.",
    "Add the scan, SBOM, sign and attest steps to your `.github/workflows/release.yml` (the full file is in Files). Keep the job's `permissions:` block exactly as shown.",
    "Commit and push, then tag `v1.2.0` and push the tag. Follow the run with `gh run watch`.",
    "Copy `security/verify-release.sh` into your repository and run it with your GitHub user name and 1.2.0.",
    "Break it on purpose: run the script's `cosign verify` command by hand with `v1.1.0` in the identity. Read the error and explain why it fails.",
]
T["hints"] = [
    "Artifact attestations are free for public repositories. On a private personal repository the attest steps fail, so make the repository public or remove those two steps.",
    "If cosign finds no matching signatures, compare the identity letter by letter. The user name (capitals matter), the workflow file and the tag must all match the run.",
    "jq, a small tool for reading JSON, finds flask in the SBOM: `jq -r '.packages[] | select(.name==\"flask\") | .versionInfo' sbom.spdx.json`.",
]
T["done_when"] = "`security/verify-release.sh <your-github-user> 1.2.0` prints three OK lines and the digest to deploy."

L["explain_back"]["prompt"] = ("Explain in 3 to 4 sentences how your release now protects the supply chain. "
                               "Mention pinning, the SBOM, the signature and verification.")
L["explain_back"]["answer"] = ("Every third-party action in the release workflow is pinned to a full commit SHA, so a moved tag cannot change the code that runs. "
                               "Before pushing, the job scans the image and stops on serious holes that have a fix. "
                               "After pushing, it writes an SBOM of the exact digest, signs that digest with cosign without a stored key, "
                               "and attaches signed provenance that names the repository, commit and workflow. "
                               "None of that helps until someone checks it, so I verify the signature and both attestations before I deploy. "
                               "Then I deploy the digest, never the tag.")

L["recap"] = [
    "Your image is mostly other people's code, and your build runs other people's actions with your rights.",
    "xz, tj-actions and Trivy each hit a different link: a maintainer, an action's tags and a security tool.",
    "Tags can move, but commit SHAs and image digests cannot. Pin to them and let Dependabot bring updates.",
    "An SBOM lists what is inside, and a scanner checks that list against known CVEs, today and again later.",
    "Limits: a scanner cannot see an attack nobody has reported, and a signature proves who built the image, never that it is good.",
    "Nothing is protected until you verify: run cosign verify and gh attestation verify before you deploy.",
]

C = L["check"]
C[0]["q"] = "A critical CVE is announced in a Python library. What answers \"which of our released images contain it?\" fastest?"
C[0]["why"] = "SBOMs list every package and version for each release, so you can search them. Old scan logs were written before this CVE existed."
C[1]["q"] = "A teammate says: \"The image is signed, so it has no vulnerabilities.\" What does the signature actually prove?"
C[1]["why"] = "A signature proves where the image came from and that nobody changed it, never that it is good. A signed image can still contain known holes."
C[2]["q"] = ("Your workflow pins `docker/login-action` to a full SHA. Tonight someone takes over the maintainers' account and moves every tag. "
             "What runs in tomorrow's build?")
C[2]["why"] = "A SHA names one exact commit, so moving tags does not change what a pinned step runs."

I = L["interview"]
I[0]["a"] = ("It is an attack on something you depend on, such as a library, a base image or a CI action, so that your own build ships the attacker's code. "
             "The xz-utils backdoor and the tj-actions and Trivy tag hijacks are recent examples. "
             "I pin third-party actions and base images to SHAs and digests, keep workflow permissions small, and use OIDC instead of stored keys. "
             "Every release gets an SBOM, a scan, a signature and provenance, and I verify them before deploying. "
             "After an incident I rotate every secret that a compromised step could read.")
I[1]["a"] = ("An SBOM lists what is inside an artifact, so you can find vulnerable packages quickly. "
             "A signature proves who produced the artifact and that it has not changed since. "
             "Provenance records how it was built (source, commit and build workflow), and SLSA levels say how far you can trust that record. "
             "None of them proves the code is free of bugs or malice: the xz backdoor came from a trusted maintainer's own release. "
             "Together they make the path from source to running image checkable, which is what you need during an incident.")
I[2]["a"] = ("A tag is a movable pointer, so whoever controls the action's repository can point it at new code. "
             "That is what happened with tj-actions and trivy-action. "
             "A full commit SHA is a hash of the content, so it always names the same code. "
             "The cost is that you stop getting fixes automatically, so you need Dependabot or Renovate to propose updates that a person reviews. "
             "I keep the version as a comment after the SHA so people can still read it.")

L["deeper"]["body"] = """A few details first that the main text skipped. SBOMs come in two standard formats, SPDX and CycloneDX, and syft can write both at once. Provenance uses a standard format too, called in-toto. Trivy can also check Dockerfiles, Kubernetes YAML and Terraform files for risky settings (`trivy fs` in Commands). When you sign as a person instead of a workflow, your email goes into the public Rekor log, where it cannot be removed. And one gap in the lab: `actions/checkout@v7` and `actions/attest@v4` still use tags. They come from GitHub itself, and many teams accept that risk. Stricter teams pin them too, and for a release workflow I would.

Now go one level down. `trivy-action` is a composite action, an action built from other actions. It runs another action, `aquasecurity/setup-trivy`, to install the Trivy program. Your SHA pin fixes the outer code, so check what that code pulls in. Open the action's `action.yaml` file at the SHA you pinned, and you find:
- `uses: aquasecurity/setup-trivy@3fb12ec12f41e471780db15c232d5dd185dcb514 # v0.2.6`, a pin by SHA.
- A `version` input whose default is a fixed Trivy release, `v0.70.0`, not `latest`.

So the maintainers pinned their own dependency too, and Aqua's advisory lists setup-trivy 0.2.6 as the first safe version. When you adopt an action, read its action file once. If it installs `latest` of anything, set the version yourself.

SHAs come with a caveat of their own. A fork is a copy of a repository under someone else's account. GitHub's [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) says to check that a SHA comes from the action's own repository, not a fork. GitHub stores a repository and its forks together, so a commit that exists only in a fork can still be fetched through the original name. Aqua's advisory calls this an imposter commit, and the Trivy attackers used one. Let Dependabot write your pins instead of copying SHAs from a blog post.

GitHub now also documents [workflow dependency lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles). A lockfile records the exact version of every dependency. This one is `.github/workflows/actions.lock`, made by the `gh actions-lock` extension. It pins every action, including the actions your actions use. At run time it checks that each commit belongs to the right repository. It is new, so read the docs before you adopt it.

Finally, you can let the cluster do the verifying. Kyverno (Day 64) is a tool that checks every change to a Kubernetes cluster against rules you write. It has a policy type for this, ImageValidatingPolicy. You tell it:
- Which images it covers, for example `ghcr.io/<your-github-user>/*`.
- Which identity must have signed them: your release workflow and GitHub's OIDC issuer, the same values you pass to `cosign verify`.
- Optionally, which attestations must exist, such as SLSA provenance.

When a Pod (one running copy of an app in Kubernetes) arrives, Kyverno looks up the signature in the registry and checks it. An unsigned image, or one signed by another workflow, is rejected. The check needs network access to the registry and to Sigstore, and one typo in the identity blocks every deploy. So start it in Audit mode, which only reports problems, like the policies on Day 64."""

L["closing"] = """We started in a jam shop, with poisoned sugar and no record of which jars held it. Now every hello-devops release carries an ingredient label, a check against the recall list, a seal with the workflow's name on it, and a delivery note. All four are tied to one fingerprint, the digest.

Open your own `release.yml` and find every `uses:` line that ends in a tag such as `@v4`. For each one, ask who could move it tonight.

Next, we'll look at the keys themselves. Where should secrets live, who may do what, and how can rules written as code stop a bad change before it lands?"""

# keep key order tidy: opening after goal, closing after deeper
order = list(L.keys())
new = {}
for k in L:
    if k in ("opening", "closing", "aside"):
        continue
    new[k] = L[k]
    if k == "goal":
        new["opening"] = L["opening"]
    if k == "sections":
        new["aside"] = L["aside"]
    if k == "deeper":
        new["closing"] = L["closing"]
idx = P["lessons"].index(L)
P["lessons"][idx] = new
PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("d63 written")
