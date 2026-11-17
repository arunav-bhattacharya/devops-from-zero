"""Book-voice rewrite of d27 (fifth pass, writer td). Replaces prose fields only."""
from common import load, save, set_list, drop_extras

path, P, L = load(6, "d27")

L["goal"] = ("By the end you can publish a versioned multi-platform image to GHCR from a git tag, using a least-privilege token, "
             "an approval gate, pinned actions and Dependabot to keep the pins current.")

L["opening"] = """Picture the evening our kitchen starts delivering. The food is boxed, the van is outside, and the driver needs a key. The quick fix is one many small kitchens use: a copy of the master key on a hook by the back door. It opens the van, the office and the safe, and it works for years.

Nothing goes wrong for months, which is exactly why the hook feels fine. Then a stranger waiting at the door notices the key. Nobody would ever know a copy was made.

Last time, our pipeline learned conditions and outputs, but everything it built stayed on the runner and was thrown away. In this lesson, we'll ship. A version tag will build our image and publish it. It will use a key that opens one door and expires within hours, wait for a person's approval, and run outside code locked to a version we checked. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "Your workflow uses `${{ secrets.GITHUB_TOKEN }}`, a token (a temporary key) for talking to GitHub. Where does that token come from?"
L["guess"]["why"] = ("GitHub makes a new GITHUB_TOKEN at the start of every job, limited to the current repository and the permissions you allow. "
                     "It stops working when the job finishes.")

set_list(L["terms"], "plain", [
    "An encrypted value stored in GitHub and given to a workflow only when it asks by name.",
    "A plain setting that is not secret, stored in GitHub and read as vars.NAME.",
    "A short-lived key GitHub creates for each job, limited to the current repository.",
    "Giving a token or a person only the access the task needs, and nothing more.",
    "A check on an environment, such as a required reviewer, that must pass before a job runs.",
    "A way for a workflow to prove who it is to a cloud and get keys that expire soon.",
    "Using an action by its full 40-character commit ID, which nobody can move to other code.",
    "A pull_request_target workflow that runs a stranger's pull request code with your secrets.",
])

S = L["sections"]

S[0]["h"] = "Where the keys live: secrets and variables"
S[0]["body"] = """Passwords, API keys and cloud credentials must never sit in your code. An API key is a password one program uses to talk to another, and cloud credentials are the keys to your cloud account. Everyone who can read the repository would see them. And git keeps them in its history even after you delete the line (Day 8).

GitHub stores them as secrets instead, the safe in the office. A secret is encrypted, and a workflow gets it only when it asks for it by name, as in `${{ secrets.API_KEY }}`. Settings that are not secret, such as a region or a bucket name, are configuration variables, read as `${{ vars.AWS_REGION }}`. Both can live at three levels:

- Repository: every workflow in the repository can read them.
- Environment: only jobs that use that environment, such as `production`, can read them.
- Organization: several repositories share them, which suits teams.

Set them in Settings, or with `gh secret set` and `gh variable set`. `gh secret set API_KEY` asks for the value, so it never lands in your shell history, the list of commands your terminal remembers.

The runner hides secret values in logs as `***`. It knows the exact values it received for this job and replaces every exact match in the log. Don't count on it, though. A secret that a script changes, for example encodes in base64 (a way of rewriting data as plain letters and digits), no longer matches and is printed in full.

So never `echo` a secret, never store a whole JSON file in one secret, and if one leaks, rotate it: create a new one and revoke the old. Rotating is changing the locks after a key goes missing.

Two kinds of runs cannot read your secrets at all. One is a pull request from a fork, a copy of your repository under another account (Day 9). The other is a pull request opened by Dependabot, the update helper we meet later today. Both also get a read-only token, which is what keeps a stranger's code harmless. That token is the next thing to understand."""

S[1]["h"] = "A key for one shift: GITHUB_TOKEN and least privilege"
S[1]["body"] = """A good kitchen gives each cook a key card for one shift, not a copy of the master key. GitHub does the same. Every job gets a token without asking: the `GITHUB_TOKEN`.

GitHub creates it when the job starts, and it expires when the job ends (after 6 hours at most on GitHub-hosted runners). It only works on the current repository. Every action in the job can use it, even if you never pass it on. `actions/checkout`, for example, uses it by default to fetch your code. So whatever the token may do, every action in the job may do.

Least privilege means a token gets only the access its task needs, like a card that opens the fridge but not the cash drawer. You control that with the `permissions` key:

- At the top of the workflow, set the default for every job, such as `contents: read`.
- In a job that needs more, set its own `permissions`, such as `packages: write`.
- Any permission you do not list becomes `none`, and `permissions: {}` switches everything off.

Personal repositories created since February 2023 start with a read-only token. Older repositories, and some organizations, still default to read and write. So write `permissions` in every workflow and stop guessing. Then an action in a read-only job, if it is ever compromised (taken over by an attacker), cannot push a fake image or change your code.

A commit or tag pushed with the `GITHUB_TOKEN` does not start new workflow runs. GitHub built it that way to prevent endless loops of workflows starting workflows. That is one reason you push the release tag yourself, and the tag is where the release begins."""

S[2]["h"] = "From a git tag to an image in GHCR"
S[2]["body"] = """A tag is a fixed name for one commit, such as `v1.0.0`. When you push one, `release.yml` builds the image and pushes it to GitHub Container Registry (GHCR), at `ghcr.io/<your-github-user>/hello-devops`. The image is hello-devops, our tiny web app that answers every visit with a greeting and a count of visits so far. A registry is an online store for images, and this is the package you pushed by hand on Day 22.

The file in Files is the full, hardened version. Its scan and signing steps belong to Day 63, and today you follow the image-push half:

1. `actions/checkout` fetches the code at the tag.
2. QEMU, an emulator, lets this amd64 runner run arm64 build steps. Buildx then builds for amd64 (most servers) and arm64 (your Mac).
3. `docker/login-action` logs in to `ghcr.io` with the job's own `GITHUB_TOKEN`. No password is stored anywhere.
4. A `run` step writes `IMAGE=ghcr.io/...` to `$GITHUB_ENV` in lower case, because registries refuse capital letters and a GitHub user name may contain them.
5. `docker/metadata-action` turns the git tag into image tags: `v1.2.0` gives `1.2.0`, `sha-` plus the short commit, and `latest`. Its `version` output, `1.2.0`, becomes the `APP_VERSION` build argument.
6. `docker/build-push-action` builds both platforms and pushes them under one multi-platform tag (Day 18).
7. The last step writes the digest and tags to the run summary.

An emulator is a program that pretends to be another kind of processor, and Buildx is Docker's build tool. The digest, from Day 18, is the fingerprint of the image's exact contents. The image is built once, from the tag, and later stages deploy that exact image by its digest.

Two surprises wait here. A new GHCR package is private, even when the repository is public. To pull it, make it public in its package settings, or log in with a personal access token (classic) that has the `read:packages` scope. That is a long-lived key you make for your own account.

The second surprise is a push that fails with `denied` while the job has `packages: write`. The package most likely exists already and is not linked to this repository; your manual push on Day 22 would do that. Open the package settings, add `hello-devops` under Manage Actions access with the Write role, and re-run the job.

Right now, though, any `v*` tag ships at once. Next, we'll put a person in the way."""

S[3]["h"] = "A person says go: environments as an approval gate"
S[3]["body"] = """No restaurant van leaves before the manager checks the order. Without a gate, every `v*` tag you push ships at once, even one you pushed by mistake.

An environment is a named deploy target, such as `staging` or `production`; Day 26 gave you a first look. The release job opts in with `environment: production`. Before that job starts, GitHub checks the environment's protection rules:

- Required reviewers: up to six people or teams. One approval lets the job go on.
- Wait timer: a delay of 1 minute up to 30 days before the job may start.
- Deployment branches and tags: for example, only tags matching `v*` may deploy.

GitHub hands over the environment's secrets only after the rules pass, so the approval also guards your credentials. A run can wait up to 30 days for its approval.

Your plan decides what you get. On the Free, Pro and Team plans, required reviewers and wait timers only work in public repositories; private repositories need GitHub Enterprise for them.

And here is a trap. If a workflow names an environment that does not exist yet, GitHub creates it with no rules, and the job runs at once. So create the environment and its rules before you push the first tag.

Leave Prevent self-review switched off. You are the only reviewer, so with it on you could never approve your own release. GitHub is now covered. A deploy to a cloud needs a key from outside GitHub, and that is where the master key on the hook usually comes back."""

S[4]["h"] = "Cloud keys that expire on their own: OIDC"
S[4]["body"] = """To deploy to a cloud such as AWS, Amazon's cloud from Part 3, a workflow needs credentials. The simple way is to store an access key as a secret. That key lives for months, works from anywhere, and is painful to rotate. If it leaks, an attacker can use it until someone notices. It is the master key on the hook.

OpenID Connect (OIDC) gets rid of the stored key. Picture a supplier's gate that checks your ID and hands you a day pass, so you never carry a permanent key. The ID here is a signed token: a short message stamped by GitHub in a way only GitHub can make. An IAM role is a set of AWS permissions that a trusted caller may borrow. It works in five steps:

1. The job asks GitHub for a signed ID token. This needs `id-token: write` in `permissions`, which grants nothing else.
2. The token states facts: this repository, this branch or environment, this workflow.
3. The job sends the token to AWS and asks to use an IAM role.
4. AWS checks the signature with GitHub's public key, then compares the facts with the role's trust policy.
5. If they match, AWS returns keys that expire after one hour by default.

The public key is what lets anyone check GitHub's stamp, and the trust policy is the role's list of callers it accepts.

You don't code any of this yourself. The `aws-actions/configure-aws-credentials` action handles steps 1, 3 and 5. You give it the role's ARN, Amazon's full name for the role, and a region. The worked example shows the workflow side, and Day 35 creates the IAM role and its trust policy for real.

`release.yml` asks for `id-token: write` too, for a different reason. cosign, a signing tool, uses the same kind of token to sign the image without any stored key (Day 63). Our own keys are now short-lived. The code we borrow from others is the last open door."""

S[5]["h"] = "Locking down borrowed code: pins and Dependabot"
S[5]["body"] = """Every action you call is someone else's code, running with your token and your secrets. A tag such as `v4` is only a label, and whoever controls the action's repository can move it to different code. It is a jar labelled "tomato sauce" that the supplier can refill with anything.

In March 2025 that really happened. The tags of the popular `tj-actions/changed-files` action were moved to a malicious commit that printed CI secrets into workflow logs ([CISA alert](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066)). In March 2026 it happened again, to the tags of `aquasecurity/trivy-action`, which `release.yml` itself uses; Day 63 tells that story.

A full commit SHA, the 40-character ID of one commit, cannot be moved. So pin third-party actions to one, and keep the version in a comment, as in `uses: docker/login-action@81c6f93d4bc991e510b342a00b419b3bb4efc5c6 # v4.7.0`. **A tag can move, and a commit SHA cannot. Pin to the SHA.**

`git ls-remote --tags` on the action's repository lists every tag with its SHA. The lab pins every third-party action in `release.yml` and `ci.yml`, and keeps GitHub's own `actions/...` on major tags. Stricter teams pin those too. Pin in CI as well as in the release: both use the same Docker layer cache, so a bad action in CI could slip something into a release.

Pins go stale, so let Dependabot move them. Dependabot is GitHub's update helper: it opens pull requests when something you use has a newer version. The lab's `dependabot.yml` does three things:

- It checks every action weekly, including the Day 26 composite action, whose folder it must be told about.
- It suggests a new release only once that release is 7 days old.
- It groups all updates into one pull request, which your CI tests like any other.

The wait gives the world a week to notice a bad release before it reaches you. One door is left, and it opens from outside: pull requests from strangers."""

L["aside"] = {
    "title": "Doesn't GitHub have a lockfile for actions now?",
    "body": "It has a newer option, in public preview: a lockfile, `.github/workflows/actions.lock`, written by the `gh actions-lock` extension. It pins every action, including the actions your actions use. A preview feature may still change before it is final. So this course sticks with SHA pins, which work everywhere today.",
    "after": 5,
}

S[6]["h"] = "Strangers' pull requests: pull_request or pull_request_target"
S[6]["body"] = """Most attacks on pipelines follow one pattern: untrusted code or text reaches a job that holds secrets. In the kitchen, it is letting a stranger cook while the safe stands open. For pull requests from forks, the trigger you pick decides whether that can happen.

`pull_request` is the safe default. For a PR from a fork it runs the PR's own code, but with a read-only token and no secrets. A stranger's code can run, and it finds nothing worth stealing.

`pull_request_target` runs in the context of your default branch instead: your workflow file, your secrets, and a token that can write. That is safe as long as the job never runs code from the pull request. It goes wrong when the job checks out the PR's head commit and runs its build script or tests. Now the stranger's code runs with your secrets. GitHub's Security Lab calls this a pwn request ("pwn" is hacker slang for taking over).

GitHub is closing this hole step by step:

- `actions/checkout@v7` refuses to check out fork PR code under `pull_request_target` or `workflow_run`, unless you set `allow-unsafe-pr-checkout: true`.
- A default policy will block `pull_request_target` in public repositories that have no event policy of their own. It runs in evaluate mode now, and GitHub's docs give 2 December 2026 as the date enforcement starts.
- Runs from untrusted triggers like this one can read the default branch's cache but not write to it (Day 25).

My rule: use `pull_request` for CI. Reach for `pull_request_target` only for jobs that never touch PR code, such as adding a label.

That ends this part with an image in a registry, built once, approved by a person, and made with locked-down code. It has limits. Nothing runs the image yet, and the whole pipeline assumes a Python app with a Dockerfile. Apps written in Kotlin or Java must be compiled first, and that needs a build tool of its own, which Part 7 explains from the beginning."""

L["closing"] = """We started with a master key on a hook by the back door. Your release now works without one. Each job gets a key card that opens only the doors it needs and expires when the job ends. A person approves the release, cloud keys last an hour, and borrowed code is locked to a commit you chose.

Run `gh api repos/{owner}/{repo}/actions/permissions/workflow` on your own repository and check that it says `read`. Then search your workflows for third-party actions that still use a plain tag.

Next, we'll leave Python behind for a while. How does code written in Kotlin become something a computer can run, and why does that need a build tool?"""

drop_extras(L)

set_list(L["worked"]["steps"], "say", [
    "You may find deploy workflows like this one in older repositories. Look for problems before you read on.",
    "Ask actionlint first. It finds one problem: the commit message is text anyone with push access controls, pasted straight into a script (Day 26). It says nothing about the other four, because they are valid YAML, so finding those is up to you.",
    "The other four: it deploys from any branch, its token can write everything, it prints a secret, and it uses long-lived AWS keys. Fix the trigger and the default permissions first, and pass the commit message through `env`.",
    "Give the job an environment, so it waits for approval. Then grant only the extra permission OIDC needs. `id-token: write` lets the job ask for an ID token; it gives no write access to your repository.",
    "Replace the stored keys with OIDC. This third-party action receives cloud access, so pin it to a full SHA. Settings that are not secret come from variables, and the message and bucket reach the shell through `env`.",
    "Finish the switch. The IAM role's trust policy accepts only tokens from this repository's production environment (Day 35 builds one). Store the role and bucket as variables, delete the old key secrets here, and deactivate the keys in AWS, so a leaked copy is useless.",
])

L["task"]["steps"] = [
    "On a branch, add `release.yml` and `dependabot.yml` from the Files section, and pin the two Docker actions in `ci.yml` as the final version shows. Open a PR, let CI pass, and merge it.",
    "Check your token's default with `gh api repos/{owner}/{repo}/actions/permissions/workflow`. If it says `write`, switch it to read under Settings, Actions, General, Workflow permissions.",
    "In Settings, open Environments and create `production`. Add yourself as a required reviewer, leave Prevent self-review off, and save.",
    "Under Deployment branches and tags, choose Selected branches and tags, and add a tag rule for `v*`.",
    "Update `main` locally, create the annotated tag `v1.0.0`, and push it.",
    "Follow the run. When it waits, open it in the browser, click Review deployments, then Approve and deploy.",
    "When it is green, read the digest in the run summary, and list the platforms with `docker buildx imagetools inspect`.",
    "Make the package public in its package settings (or log in to GHCR with a classic token that has `read:packages`). Then pull and run the image on your Mac with port 8000 mapped, and call `curl localhost:8000`.",
]
L["task"]["hints"] = [
    "If the job never asks for approval, check that the environment name in the workflow matches exactly.",
    "If the Trivy step stops the release, it found a HIGH or CRITICAL vulnerability that already has a fix. Its log table names the package; Day 63 explains what to do.",
    "Push tags one at a time. GitHub creates no events when you push more than three tags at once.",
]
L["task"]["done_when"] = "You are done when `curl localhost:8000` against the image you pulled from GHCR shows `\"version\": \"1.0.0\"`."

L["explain_back"]["answer"] = ("The workflow gives every job a read-only GITHUB_TOKEN, and only the image job gets packages: write, so nothing else can push. "
                               "That token is created for the job and expires when the job ends, so there is no long-lived password to leak. "
                               "The job uses the production environment, so it waits for my approval before it runs and before any environment secrets are released. "
                               "The third-party actions are pinned to full commit SHAs, so nobody can swap their code by moving a tag, and Dependabot proposes updates that go through CI.")

L["recap"] = [
    "Secrets are encrypted and read by name. Never print them, and rotate any that leak; fork and Dependabot PRs get none.",
    "Set permissions: contents: read at the top, and grant more only in the job that needs it.",
    "A v* tag starts release.yml, which builds amd64 and arm64 images once and pushes them to GHCR, after a person approves.",
    "OIDC replaces long-lived cloud keys with short-lived ones tied to your repository and environment.",
    "Pin third-party actions to full SHAs, let Dependabot move the pins, and keep PR code away from pull_request_target.",
    "The limit: the image is published but runs nowhere yet, and the pipeline assumes a Python app that needs no compiling.",
]

C = L["check"]
C[0]["why"] = "The job needs to read code and write one comment. It needs nothing else."
C[1]["why"] = "With OIDC each job gets keys that expire soon, and no stored secret is left to leak."
C[2]["why"] = ("That is the pwn request pattern. pull_request_target gives the job your secrets, "
               "and checking out the PR head runs a stranger's code with them.")

I = L["interview"]
I[0]["a"] = ("Stored keys live a long time and work from anywhere. If one leaks, an attacker has access until someone notices and rotates it. "
             "With OIDC, the workflow proves who it is with a signed token, and the cloud returns credentials that expire soon. "
             "The cloud's trust policy can limit access to one repository, branch or environment. "
             "There is no stored secret to leak or rotate, and each role can follow least privilege.")
I[1]["a"] = ("Every third-party action is pinned to a full commit SHA, so a moved tag cannot change the code I run. "
             "Dependabot proposes updates only a few days after each release, and I review those PRs. "
             "The GITHUB_TOKEN stays read-only by default, with write access only in the job that needs it. "
             "Deploy credentials live in environments behind approvals, and I prefer OIDC over stored keys. "
             "Where a short shell step will do, I use that instead of another action.")
I[2]["a"] = ("pull_request runs the pull request's own code. For forks it gets a read-only token and no secrets, so it is safe for CI. "
             "The pull_request_target trigger runs the workflow from the default branch with the repository's secrets and a write token. "
             "That is useful for labelling or commenting on fork PRs. "
             "It becomes dangerous when the job checks out and runs the PR's code, because then a stranger's code runs with those secrets. "
             "GitHub's checkout v7 refuses that by default, and a default policy will block the trigger in public repositories.")

L["deeper"]["body"] = """The ID token that GitHub gives your job is a JSON Web Token (JWT): a small JSON document, signed by GitHub and encoded as text. Its fields are called claims, the facts the token states. Four of them matter most:

- `iss` (issuer) is `https://token.actions.githubusercontent.com`, so the cloud knows who signed it.
- `aud` (audience) says who the token is for; the AWS action asks for `sts.amazonaws.com`.
- `sub` (subject) says which workflow is calling, for example `repo:octo-org/octo-repo:environment:production`.
- `exp` says when the token expires.

The checking happens on the cloud side, at the supplier's gate. The IAM role's trust policy decides which tokens it accepts. A strict policy checks `aud` and the exact `sub`. A loose policy, such as one that matches `repo:octo-org/*`, lets every repository owned by `octo-org` assume the role. Always pin `sub` to one repository, plus a branch or an environment.

The `sub` value depends on the job:

- A job with `environment: production` gets a subject ending in `environment:production`.
- A job running on a branch gets one ending in `ref:refs/heads/main`.
- A job started by a pull request gets one ending in `pull_request`.

So you can give the production role only to production jobs, and a read-only role to pull request jobs.

One recent change affects your repository. Repositories created after July 15, 2026 use an immutable subject format that includes numeric IDs, for example `repo:octo-org@123456/octo-repo@456789:ref:refs/heads/main`. This stops someone who later takes over a deleted account name from matching an old trust policy. Your hello-devops repository is new, so copy the exact format from the [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) when you write the trust policy on Day 35.

Ask for `id-token: write` only in the job that needs it, not for the whole workflow. And pair OIDC with environments. Protection rules must pass before the job reaches a runner, so no token exists until a person has approved.

The image job in `release.yml` also does more than this lesson covered: a vulnerability scan, an SBOM (a list of every package inside the image), a signature and attestations. Those steps are Day 63's subject."""

save(path, P)
print("d27 written")
