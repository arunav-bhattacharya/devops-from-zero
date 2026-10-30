"""Day 21: Ship it: build and push images safely (first edition d12)."""
from common import T, box, cap, lab, line, link, refs, sources, svg

DIAGRAM = svg(200, "Pushing a version tag waits for approval in the production environment, then builds amd64 and arm64 images and pushes them to ghcr.io using a short-lived GITHUB_TOKEN", [
    cap(62, 30, "you push"),
    cap(190, 30, "production env"),
    cap(328, 30, "amd64 + arm64"),
    cap(484, 30, "1.0.0, sha, latest"),
    box(8, 42, 108, 44, "bxo", "Tag v1.0.0"),
    line(116, 64, 136, 64),
    box(140, 42, 100, 44, "bxp", "Approval"),
    line(240, 64, 260, 64),
    box(264, 42, 128, 44, "bxt", "Build + push"),
    line(392, 64, 412, 64),
    box(416, 42, 136, 44, "bxg", "ghcr.io"),
    box(264, 136, 128, 40, "bx", "GITHUB_TOKEN"),
    line(328, 136, 328, 90, dashed=True),
    cap(206, 161, "short-lived"),
    cap(452, 161, "packages: write"),
])

S1 = T("""
Passwords, API keys and cloud credentials must never sit in your code. GitHub stores them as secrets instead. A secret is encrypted, and a workflow gets it only when it asks for it by name, as in `${{ secrets.API_KEY }}`. Settings that are not secret, such as a region or a bucket name, are configuration variables, read as `${{ vars.AWS_REGION }}`.

Both can live at three levels:

- Repository: every workflow in the repository can read them.
- Environment: only jobs that use that environment, such as `production`, can read them.
- Organization: several repositories share them, which suits teams.

Set them in Settings, or with `gh secret set` and `gh variable set`. `gh secret set API_KEY` asks for the value, so it never lands in your shell history.

GitHub hides known secret values in logs as `***`, but don't count on it. A secret that a script changes, for example encodes in base64, no longer matches and is printed in full. So never `echo` a secret, never store a whole JSON file in one secret, and if one leaks, rotate it: create a new one and revoke the old. Two kinds of runs cannot read your secrets at all: pull requests from forks, and pull requests opened by Dependabot. Both also get a read-only token, which is what keeps a stranger's code harmless.
""")

S2 = T("""
Every job gets a token without asking: the `GITHUB_TOKEN`. GitHub creates it when the job starts, and it expires when the job ends (after 6 hours at most on GitHub-hosted runners). It only works on the current repository. Every action in the job can use it, even if you never pass it on, so whatever the token may do, every action in the job may do.

**Least privilege** means a token gets only the access its task needs. You control that with the `permissions` key:

- At the top of the workflow, set the default for every job, such as `contents: read`.
- In a job that needs more, set its own `permissions`, such as `packages: write`.
- Any permission you do not list becomes `none`, and `permissions: {}` switches everything off.

Personal repositories created since February 2023 start with a read-only token. Older repositories, and some organizations, still default to read and write. So write `permissions` in every workflow and stop guessing. Then an action in a read-only job, if it is ever compromised, cannot push a fake image or change your code.

One property surprises people. A commit or tag pushed with the `GITHUB_TOKEN` does not start new workflow runs. GitHub built it that way to prevent endless loops of workflows starting workflows. That is one reason you push the release tag yourself.
""")

S3 = T("""
When you push a tag such as `v1.0.0`, `release.yml` builds the image and pushes it to GitHub Container Registry (GHCR), at `ghcr.io/<your-github-user>/hello-devops`. That is the package you pushed by hand on Day 16. The file in Files is the full, hardened version. Its scan, SBOM, signing and attestation steps belong to Day 52; today you follow the image-push half:

1. `actions/checkout` fetches the code at the tag.
2. The QEMU and Buildx actions prepare a builder that can produce amd64 (most servers) and arm64 (your Mac) images.
3. `docker/login-action` logs in to `ghcr.io` with the job's own `GITHUB_TOKEN`. No password is stored anywhere.
4. A `run` step writes `IMAGE=ghcr.io/...` to `$GITHUB_ENV` in lower case, because registries refuse capital letters and a GitHub user name may contain them.
5. `docker/metadata-action` turns the git tag into image tags: `v1.2.0` gives `1.2.0`, `sha-` plus the short commit, and `latest`. Its `version` output, `1.2.0`, becomes the `APP_VERSION` build argument.
6. `docker/build-push-action` builds both platforms and pushes them under one multi-platform tag (Day 12).
7. The last step writes the digest and tags to the run summary.

The image is built once, from the tag, and later stages deploy that exact image by its digest. A new GHCR package is private, even when the repository is public. To pull it, make it public in its package settings, or log in with a personal access token (classic) that has the `read:packages` scope.
""")

S4 = T("""
An environment is a named deploy target, such as `staging` or `production`; Day 20 gave you a first look. The release job opts in with `environment: production`. Before that job starts, GitHub checks the environment's protection rules:

- Required reviewers: up to six people or teams. One approval lets the job go on.
- Wait timer: a delay of 1 minute up to 30 days before the job may start.
- Deployment branches and tags: for example, only tags matching `v*` may deploy.

GitHub hands over the environment's secrets only after the rules pass, so the approval also guards your credentials. A run can wait up to 30 days for its approval.

Your plan decides what you get. On the Free, Pro and Team plans, required reviewers and wait timers only work in public repositories; private repositories need GitHub Enterprise for them. And if a workflow names an environment that does not exist yet, GitHub creates it with no rules and the job runs at once. So create the environment and its rules before you push the first tag.

You work alone, so leave Prevent self-review switched off. With it on, you could never approve your own release.
""")

S5 = T("""
To deploy to a cloud such as AWS, a workflow needs credentials. The simple way is to store an access key as a secret. That key lives for months, works from anywhere, and is painful to rotate. If it leaks, an attacker can use it until someone notices.

OpenID Connect (OIDC) gets rid of the stored key. It works in five steps:

1. The job asks GitHub for a signed ID token. This needs `id-token: write` in `permissions`, which grants nothing else.
2. The token states facts: this repository, this branch or environment, this workflow.
3. The job sends the token to AWS and asks to use an IAM role.
4. AWS checks GitHub's signature and compares the facts with the role's trust policy.
5. If they match, AWS returns keys that expire after one hour by default.

You don't code any of this yourself. The `aws-actions/configure-aws-credentials` action handles steps 1, 3 and 5; you give it the role's ARN and a region. The worked example shows the workflow side, and Day 29 creates the IAM role and its trust policy for real.

`release.yml` asks for `id-token: write` too, for a different reason. cosign uses the same kind of token to sign the image without any stored key (Day 52).
""")

S6 = T("""
Every action you call is someone else's code, running with your token and your secrets. A tag such as `v4` is only a label, and whoever controls the action's repository can move it to different code. In March 2025 that really happened: the tags of the popular `tj-actions/changed-files` action were moved to a malicious commit that printed CI secrets into workflow logs ({cisa}). In March 2026 it happened again, to the tags of `aquasecurity/trivy-action`, which `release.yml` itself uses; Day 52 tells that story.

A full commit SHA cannot be moved. So pin third-party actions to one, and keep the version in a comment, as in `uses: docker/login-action@81c6f93d4bc991e510b342a00b419b3bb4efc5c6 # v4.7.0`. `git ls-remote --tags` on the action's repository lists every tag with its SHA. The lab pins every third-party action in `release.yml` and `ci.yml`, and keeps GitHub's own `actions/...` on major tags. Stricter teams pin those too. Pin in CI as well as in the release: both use the same Docker layer cache, so a bad action in CI could slip something into a release.

Pins go stale, so let Dependabot move them. The lab's `dependabot.yml` does three things:

- It checks every action weekly, including the Day 20 composite action, whose folder it must be told about.
- It suggests a new release only once that release is 7 days old.
- It groups all updates into one pull request, which your CI tests like any other.

GitHub also has a newer option, in public preview: a lockfile, `.github/workflows/actions.lock`, written by the `gh actions-lock` extension. It pins every action, including the actions your actions use. It may still change, so this course sticks with SHA pins.
""").format(cisa=link("cisa", "CISA alert"))

S7 = T("""
Most attacks on pipelines follow one pattern: untrusted code or text reaches a job that holds secrets. The trigger you choose decides a lot.

`pull_request` is the safe default. For a PR from a fork it runs the PR's own code, but with a read-only token and no secrets. A stranger's code can run, and it finds nothing worth stealing.

`pull_request_target` runs in the context of your default branch instead: your workflow file, your secrets, and a token that can write. That is safe as long as the job never runs code from the pull request. The classic mistake is to check out the PR's head commit and then run its build script or tests. Now the stranger's code runs with your secrets. GitHub's Security Lab calls this a pwn request.

GitHub is closing this hole step by step:

- `actions/checkout@v7` refuses to check out fork PR code under `pull_request_target` or `workflow_run`, unless you set `allow-unsafe-pr-checkout: true`.
- A default policy will block `pull_request_target` in public repositories that have no event policy of their own. It runs in evaluate mode now, and GitHub's docs give 2 December 2026 as the date enforcement starts.
- Runs from untrusted triggers like this one can read the default branch's cache but not write to it (Day 19).

My rule: use `pull_request` for CI. Reach for `pull_request_target` only for jobs that never touch PR code, such as adding a label.
""")

LESSON = {
    "id": "d21",
    "title": "Ship it: build and push images safely",
    "minutes": 50,
    "goal": "By the end you can publish a versioned multi-platform image to GHCR from a git tag, using a least-privilege token, an approval gate, pinned actions and Dependabot to keep the pins current.",
    "guess": {
        "q": "Your workflow uses `${{ secrets.GITHUB_TOKEN }}`. Where does that token come from?",
        "options": [
            "You create it once in Settings and paste it in as a secret",
            "GitHub creates a fresh one for each job, and it expires when the job ends",
            "It is your personal password, reused by GitHub",
            "It is shared by all your repositories and never expires",
        ],
        "answer": 1,
        "why": "GitHub makes a new GITHUB_TOKEN at the start of every job, limited to the current repository and the permissions you allow. It stops working when the job finishes.",
    },
    "terms": [
        {"term": "Secret", "plain": "An encrypted value stored in GitHub and given to a workflow only when it asks by name."},
        {"term": "Configuration variable", "plain": "A plain, non-secret setting stored in GitHub and read as vars.NAME."},
        {"term": "GITHUB_TOKEN", "plain": "A short-lived token GitHub creates for each job, limited to the current repository."},
        {"term": "Least privilege", "plain": "Giving a token or a person only the access the task needs, and nothing more."},
        {"term": "Protection rule", "plain": "A check on an environment, such as a required reviewer, that must pass before a job runs."},
        {"term": "OIDC (OpenID Connect)", "plain": "A way for a workflow to prove who it is to a cloud and get short-lived keys."},
        {"term": "SHA pinning", "plain": "Using an action by its full 40-character commit ID, which nobody can move to other code."},
        {"term": "Pwn request", "plain": "A pull_request_target workflow that runs a pull request's code with your secrets."},
    ],
    "sections": [
        {"h": "Secrets and variables", "body": S1, "refs": refs("secrets", "use_secrets", "use_variables")},
        {"h": "GITHUB_TOKEN and least privilege", "body": S2, "refs": refs("token", "token_tut")},
        {"h": "From a git tag to an image in GHCR", "body": S3, "refs": refs("publish_images", "ghcr", "metadata")},
        {"h": "Environments: a human approval gate", "body": S4, "refs": refs("envs_ref", "manage_envs")},
        {"h": "OIDC: cloud access without stored keys", "body": S5, "refs": refs("oidc", "oidc_aws", "aws_action")},
        {"h": "Pin actions, and let Dependabot move the pins", "body": S6, "refs": refs("dependabot_actions", "lockfiles", "v_checkout_sec")},
        {"h": "Pull requests from forks: pull_request or pull_request_target", "body": S7, "refs": refs("prt", "pwn", "checkout")},
    ],
    "analogy": "The GITHUB_TOKEN is like a hotel key card. The front desk makes a new card for each stay, it opens only the doors you booked, and it stops working at checkout. A long-lived cloud key is more like a copied master key: it opens many doors for years, so losing it is a disaster. OIDC is showing your passport at the desk to get a fresh card each time. The comparison falls short in one place: a key card has one guest, while every action in a job can use the token.",
    "diagram": DIAGRAM,
    "diagram_caption": "A version tag starts the release: an approval gate, then an amd64 and arm64 build pushed to GHCR with a write-scoped, short-lived token.",
    "worked": {
        "title": "Make a risky deploy workflow safe",
        "steps": [
            {
                "say": "Here is a deploy workflow like ones you may find in older repositories. Look for problems before you read on.",
                "code": T("""
                    name: deploy
                    on: push
                    permissions: write-all
                    jobs:
                      deploy:
                        runs-on: ubuntu-latest
                        steps:
                          - uses: actions/checkout@v7
                          - run: echo "Deploying ${{ github.event.head_commit.message }}"
                          - run: echo "Using key ${{ secrets.AWS_ACCESS_KEY_ID }}"
                          - run: aws s3 sync ./site s3://hello-devops-site
                            env:
                              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
                              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
                """),
                "lang": "yaml",
            },
            {
                "say": "Ask actionlint first. It finds one problem: the commit message is text anyone with push access controls, pasted straight into a script (Day 20). It says nothing about the other four, because they are valid YAML. Tools catch some problems; you catch the rest.",
                "code": T("""
                    $ actionlint
                    .github/workflows/deploy.yml:9:34: "github.event.head_commit.message" is potentially untrusted. avoid using it directly in inline scripts. instead, pass it through an environment variable. see https://docs.github.com/en/actions/reference/security/secure-use#good-practices-for-mitigating-script-injection-attacks for more details [expression]
                      |
                    9 |       - run: echo "Deploying ${{ github.event.head_commit.message }}"
                      |                                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                """),
                "lang": "console",
            },
            {
                "say": "The other four: it deploys from any branch, its token can write everything, it prints a secret, and it uses long-lived AWS keys. Fix the trigger and the default permissions first, and pass the commit message through `env`.",
                "code": T("""
                    name: deploy
                    on:
                      push:
                        branches: [main]
                    permissions:
                      contents: read
                """),
                "lang": "yaml",
            },
            {
                "say": "Give the job an environment, so it waits for approval. Then grant only the extra permission OIDC needs. `id-token: write` lets the job ask for an ID token; it gives no write access to your repository.",
                "code": T("""
                    jobs:
                      deploy:
                        runs-on: ubuntu-latest
                        environment: production
                        permissions:
                          contents: read
                          id-token: write
                """),
                "lang": "yaml",
            },
            {
                "say": "Replace the stored keys with OIDC. This third-party action receives cloud access, so pin it to a full SHA. Settings that are not secret come from variables, and the message and bucket reach the shell through `env`.",
                "code": T("""
                        steps:
                          - uses: actions/checkout@v7
                          - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
                            with:
                              role-to-assume: ${{ vars.AWS_ROLE_ARN }}
                              aws-region: eu-west-1
                          - run: echo "Deploying $MESSAGE" && aws s3 sync ./site "s3://$BUCKET"
                            env:
                              MESSAGE: ${{ github.event.head_commit.message }}
                              BUCKET: ${{ vars.SITE_BUCKET }}
                """),
                "lang": "yaml",
            },
            {
                "say": "Finish the switch. The IAM role's trust policy accepts only tokens from this repository's production environment (Day 29 builds one). Store the role and bucket as variables, delete the old key secrets here, and deactivate the keys in AWS so a leaked copy is useless.",
                "code": T("""
                    $ gh variable set AWS_ROLE_ARN --body arn:aws:iam::123456789012:role/hello-devops-deploy
                    $ gh variable set SITE_BUCKET --body hello-devops-site
                    $ gh secret delete AWS_ACCESS_KEY_ID
                    $ gh secret delete AWS_SECRET_ACCESS_KEY
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        {
            "lang": "yaml",
            "title": ".github/workflows/release.yml",
            "src": lab(".github/workflows/release.yml"),
            "run": "git tag -a v1.0.0 -m \"Release 1.0.0\" && git push origin v1.0.0 && gh run watch",
        },
        {
            "lang": "yaml",
            "title": ".github/workflows/ci.yml (final: third-party actions pinned)",
            "src": lab(".github/workflows/ci.yml"),
            "run": "actionlint && git commit -am \"Pin third-party actions in CI\" && git push",
        },
        {
            "lang": "yaml",
            "title": ".github/dependabot.yml",
            "src": lab(".github/dependabot.yml"),
            "run": "git add .github/dependabot.yml && git commit -m \"Let Dependabot update actions\" && git push",
        },
    ],
    "commands": [
        {"cmd": "export GH_USER=$(gh api user --jq .login | tr '[:upper:]' '[:lower:]')", "what": "Save your GitHub user name, in lower case, for the image commands below."},
        {"cmd": "gh api repos/{owner}/{repo}/actions/permissions/workflow", "what": "Show whether this repository's GITHUB_TOKEN defaults to read or write."},
        {"cmd": "gh secret set API_KEY", "what": "Store a repository secret; gh asks for the value, so it stays out of your shell history."},
        {"cmd": "gh variable set AWS_REGION --body eu-west-1", "what": "Store a plain variable that is not secret."},
        {"cmd": "git tag -a v1.0.0 -m \"Release 1.0.0\"", "what": "Create an annotated version tag on the current commit."},
        {"cmd": "git push origin v1.0.0", "what": "Push the tag, which starts release.yml."},
        {"cmd": "gh run watch", "what": "Follow the release run; it waits while the approval is pending."},
        {"cmd": "docker buildx imagetools inspect ghcr.io/$GH_USER/hello-devops:1.0.0", "what": "Show the digest and the platforms (amd64, arm64) behind a tag."},
        {"cmd": "docker login ghcr.io -u \"$GH_USER\"", "what": "Log in to GHCR; paste a classic token with read:packages to pull a private package."},
        {"cmd": "docker pull ghcr.io/$GH_USER/hello-devops:1.0.0", "what": "Download your released image from GHCR."},
        {"cmd": "git ls-remote --tags https://github.com/docker/login-action", "what": "List an action's tags with their commit SHAs, so you can pin by SHA."},
        {"cmd": "actionlint", "what": "Check every workflow, including untrusted values pasted into scripts."},
    ],
    "mistake": "If the push to GHCR fails with `denied` while the job has `packages: write`, the package most likely exists already and is not linked to this repository. Your manual push on Day 16 would do that. Open the package settings, add `hello-devops` under Manage Actions access with the Write role, and re-run the job.",
    "real_world": "PayLoop lets only the release workflow push images, and that workflow only runs for version tags. Production deploys wait in a protected environment until an engineer from the on-call rotation approves. No CI system there holds long-lived cloud keys. Each job gets short-lived AWS credentials through OIDC, with one role per environment. Dependabot's weekly action updates go through the same CI and review as any other change.",
    "task": {
        "title": "Release v1.0.0 to GHCR",
        "steps": [
            "On a branch, add `release.yml` and `dependabot.yml` from the Files section, and pin the two Docker actions in `ci.yml` as the final version shows. Open a PR, let CI pass, and merge it.",
            "Check your token's default with `gh api repos/{owner}/{repo}/actions/permissions/workflow`. If it says `write`, switch it to read under Settings, Actions, General, Workflow permissions.",
            "In Settings, open Environments and create `production`. Add yourself as a required reviewer, leave Prevent self-review off, and save.",
            "Under Deployment branches and tags, choose Selected branches and tags, and add a tag rule for `v*`.",
            "Update `main` locally, create the annotated tag `v1.0.0`, and push it.",
            "Follow the run. When it waits, open it in the browser, click Review deployments, then Approve and deploy.",
            "When it is green, read the digest in the run summary, and list the platforms with `docker buildx imagetools inspect`.",
            "Make the package public in its package settings (or log in to GHCR with a classic token that has `read:packages`). Then pull and run the image on your Mac with port 8000 mapped, and call `curl localhost:8000`.",
        ],
        "hints": [
            "If the job never asks for approval, check that the environment name in the workflow matches exactly.",
            "If the Trivy step stops the release, it found a HIGH or CRITICAL vulnerability that already has a fix. Its log table names the package; Day 52 explains what to do.",
            "Push tags one at a time. GitHub creates no events when you push more than three tags at once.",
        ],
        "done_when": "`curl localhost:8000` against the image you pulled from GHCR shows `\"version\": \"1.0.0\"`.",
    },
    "explain_back": {
        "prompt": "Explain how your release workflow keeps credentials safe, in 3 to 4 sentences. Mention GITHUB_TOKEN permissions, the environment and SHA pinning.",
        "answer": "The workflow gives every job a read-only GITHUB_TOKEN, and only the image job gets packages: write, so nothing else can push. That token is created for the job and expires when the job ends, so there is no long-lived password to leak. The job uses the production environment, so it waits for my approval before it runs and before any environment secrets are released. The third-party actions are pinned to full commit SHAs, so nobody can swap their code by moving a tag, and Dependabot proposes updates that go through CI.",
    },
    "recap": [
        "Secrets are encrypted and read by name. Never print them, and rotate any that leak; fork and Dependabot PRs get none.",
        "Set permissions: contents: read at the top, and grant more only in the job that needs it.",
        "A v* tag triggers release.yml, which builds amd64 and arm64 images once and pushes them to GHCR.",
        "Environments with required reviewers pause a job until a person approves it.",
        "OIDC replaces long-lived cloud keys with short-lived ones tied to your repository and environment.",
        "Pin third-party actions to full SHAs, let Dependabot move the pins, and keep PR code away from pull_request_target.",
    ],
    "check": [
        {
            "q": "A job only runs tests and then posts a comment on the PR. Which permissions fit least privilege?",
            "options": [
                "permissions: write-all",
                "contents: read and pull-requests: write",
                "contents: write and packages: write",
                "No permissions key at all",
            ],
            "answer": 1,
            "why": "The job needs to read code and write one comment. It needs nothing else.",
        },
        {
            "q": "A new teammate wants to deploy to AWS by saving an IAM user's access key as a repository secret. What do you suggest?",
            "options": [
                "Use OIDC with an IAM role and short-lived keys",
                "Put the key in the workflow file so it gets reviewed",
                "Base64 encode the key before saving it",
                "Save the key as a variable so it is easy to see",
            ],
            "answer": 0,
            "why": "With OIDC each job gets keys that expire soon, and there is no stored secret left.",
        },
        {
            "q": "Outside contributors send PRs to your public repo, and the tests need a private registry password. A teammate suggests pull_request_target with a checkout of the PR head. What is wrong with that?",
            "options": [
                "Nothing, because pull_request_target never runs on forks",
                "The tests would run on main instead of the PR",
                "It costs more runner minutes than pull_request",
                "The PR's own code would run with your secrets and a write token",
            ],
            "answer": 3,
            "why": "That is the pwn request pattern. pull_request_target gives the job your secrets, and checking out the PR head runs a stranger's code with them.",
        },
    ],
    "interview": [
        {
            "q": "Why use OIDC instead of storing cloud access keys in CI?",
            "a": "Stored keys live a long time and work from anywhere. If one leaks, an attacker has access until someone notices and rotates it. With OIDC, the workflow proves who it is with a signed token, and the cloud returns credentials that expire soon. The cloud's trust policy can limit access to one repository, branch or environment. There is no stored secret to leak or rotate, and each role can follow least privilege.",
        },
        {
            "q": "How do you protect a CI/CD pipeline from a compromised third-party action?",
            "a": "I pin every third-party action to a full commit SHA, so a moved tag cannot change the code I run. I review Dependabot's update PRs, which wait a few days after each release. I keep the GITHUB_TOKEN read-only by default and grant write access only to the job that needs it. I keep deploy credentials in environments behind approvals, and prefer OIDC over stored keys. I also use fewer actions where a short shell step will do.",
        },
        {
            "q": "What is the difference between pull_request and pull_request_target?",
            "a": "pull_request runs the pull request's own code. For forks it gets a read-only token and no secrets, so it is safe for CI. The pull_request_target trigger runs the workflow from the default branch with the repository's secrets and a write token. That is useful for labelling or commenting on fork PRs. It becomes dangerous when the job checks out and runs the PR's code, because then a stranger's code runs with those secrets. GitHub's checkout v7 refuses that by default, and a default policy will block the trigger in public repositories.",
        },
    ],
    "deeper": {
        "minutes": 13,
        "body": T("""
            The ID token that GitHub gives your job is a JSON Web Token (JWT): a small JSON document, signed by GitHub and encoded as text. Its fields are called claims. Four of them matter most:

            - `iss` (issuer) is `https://token.actions.githubusercontent.com`, so the cloud knows who signed it.
            - `aud` (audience) says who the token is for; the AWS action asks for `sts.amazonaws.com`.
            - `sub` (subject) says which workflow is calling, for example `repo:octo-org/octo-repo:environment:production`.
            - `exp` says when the token expires.

            The checking happens on the cloud side. The IAM role's trust policy decides which tokens it accepts. A strict policy checks `aud` and the exact `sub`. A loose policy, such as one that matches `repo:octo-org/*`, lets every repository owned by `octo-org` assume the role. Always pin `sub` to one repository, plus a branch or an environment.

            The `sub` value depends on the job:

            - A job with `environment: production` gets a subject ending in `environment:production`.
            - A job running on a branch gets one ending in `ref:refs/heads/main`.
            - A job started by a pull request gets one ending in `pull_request`.

            So you can give the production role only to production jobs, and a read-only role to pull request jobs.

            One recent change affects your repository. Repositories created after July 15, 2026 use an immutable subject format that includes numeric IDs, for example `repo:octo-org@123456/octo-repo@456789:ref:refs/heads/main`. This stops someone who later takes over a deleted account name from matching an old trust policy. Your hello-devops repository is new, so copy the exact format from the {oidc} when you write the trust policy on Day 29.

            Ask for `id-token: write` only in the job that needs it, not for the whole workflow. And pair OIDC with environments. Protection rules must pass before the job reaches a runner, so no token exists until a person has approved.
        """).format(oidc=link("oidc_ref", "OIDC reference")),
    },
    "sources": sources("secure_use", "token", "publish_images", "oidc_aws"),
}
