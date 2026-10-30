"""Shared helpers for Part 4 (CI/CD with GitHub Actions), second edition.

Every docs.github.com URL below was checked against a sparse clone of
github/docs (commit 6cbe641, 29 Oct 2026) with checkurl.py. Other links come
from the research notes, from WebSearch results in this task, or from
repositories checked with `git ls-remote`.
"""
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs/hello-devops"
FILES = pathlib.Path(__file__).resolve().parent / "files"


class Txt(str):
    """A str whose format() fills only the named {placeholders} it is given,
    so workflow text such as ${{ github.sha }} or bash -e {0} stays as it is."""

    def format(self, **kw):
        out = str(self)
        for k, v in kw.items():
            out = out.replace("{" + k + "}", v)
        return out


def T(s):
    """Dedent and strip a triple-quoted block."""
    return Txt(textwrap.dedent(s).strip("\n").rstrip())


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def scratch(name):
    return (FILES / name).read_text().rstrip("\n")


# ---------------------------------------------------------------- svg helpers
def svg(h, label, parts):
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{label}">' + "".join(parts) + "</svg>")


def box(x, y, w, h, cls, text):
    assert w >= 8 * len(text) + 24, f"box too narrow for {text!r}"
    assert x >= 8 and x + w <= 552, f"box {text!r} leaves the viewBox"
    tcls = "t" if cls == "bx" else "tk"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>'
            f'<text x="{x + w / 2:g}" y="{y + h / 2 + 5:g}" class="{tcls}" font-size="13" '
            f'text-anchor="middle">{text}</text>')


def cap(x, y, text):
    return f'<text x="{x}" y="{y}" class="ts" font-size="11" text-anchor="middle">{text}</text>'


def line(x1, y1, x2, y2, dashed=False, arrow=True):
    cls = "lnd" if dashed else "ln"
    m = ' marker-end="url(#ar)"' if arrow else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"{m}/>'


# ---------------------------------------------------------------- links
GH = "https://docs.github.com/en/"
GA = GH + "actions/"
R = {
    # git, pull requests, CI/CD ideas
    "about_git": ("About Git", GH + "get-started/using-git/about-git", "docs"),
    "progit": ("Pro Git, the free book on git", "https://git-scm.com/book/en/v2", "read"),
    "progit_rebase": ("Pro Git: Rebasing", "https://git-scm.com/book/en/v2/Git-Branching-Rebasing", "read"),
    "conflict_cli": ("Resolving a merge conflict using the command line", GH + "pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-using-the-command-line", "docs"),
    "skill_conflicts": ("GitHub Skills: Resolve merge conflicts (hands-on course)", "https://github.com/skills/resolve-merge-conflicts", "read"),
    "about_prs": ("About pull requests", GH + "pull-requests/get-started/about-pull-requests", "docs"),
    "review_qs": ("Reviewing pull requests quickstart", GH + "pull-requests/get-started/reviewing-pull-requests-quickstart", "docs"),
    "v_gh_pr": ("How to create a pull request in 4 minutes (GitHub, GitHub for Beginners)", "https://www.youtube.com/watch?v=nCKdihvneS0", "watch"),
    "gh_flow": ("GitHub flow", GH + "get-started/using-github/github-flow", "docs"),
    "tbd": ("Trunk Based Development (trunkbaseddevelopment.com)", "https://trunkbaseddevelopment.com/", "read"),
    "fowler_branching": ("Patterns for Managing Source Code Branches (Martin Fowler)", "https://martinfowler.com/articles/branching-patterns.html", "read"),
    "fowler_ci": ("Continuous Integration (Martin Fowler)", "https://martinfowler.com/articles/continuousIntegration.html", "read"),
    "merge_methods": ("About merge methods on GitHub", GH + "repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github", "docs"),
    "merge_queue": ("Managing a merge queue", GH + "repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue", "docs"),
    "ci": ("About continuous integration", GA + "get-started/continuous-integration", "docs"),
    "cd": ("About continuous deployment", GA + "get-started/continuous-deployment", "docs"),
    "rollouts": ("Argo Rollouts: blue/green and canary for Kubernetes", "https://github.com/argoproj/argo-rollouts", "read"),
    "sre": ("Google's SRE book (see the release engineering chapter)", "https://sre.google/sre-book/table-of-contents/", "read"),
    "semver": ("Semantic Versioning 2.0.0 specification", "https://github.com/semver/semver/blob/master/semver.md", "read"),
    "releases": ("About releases", GH + "repositories/releasing-projects-on-github/about-releases", "docs"),
    # first workflow
    "understand": ("Understanding GitHub Actions", GA + "get-started/understand-github-actions", "docs"),
    "quickstart": ("GitHub Actions quickstart", GA + "get-started/quickstart", "docs"),
    "skill_hello": ("GitHub Skills: Hello GitHub Actions (hands-on course)", "https://github.com/skills/hello-github-actions", "read"),
    "v_gh_actions": ("How to use GitHub Actions (GitHub, GitHub for Beginners)", "https://www.youtube.com/watch?v=BQrohJ3PT7I", "watch"),
    "syntax": ("Workflow syntax for GitHub Actions", GA + "reference/workflows-and-actions/workflow-syntax", "docs"),
    "events": ("Events that trigger workflows", GA + "reference/workflows-and-actions/events-that-trigger-workflows", "docs"),
    "hosted": ("GitHub-hosted runners", GA + "concepts/runners/github-hosted-runners", "docs"),
    "runners_ref": ("GitHub-hosted runners reference (labels and specs)", GA + "reference/runners/github-hosted-runners", "docs"),
    "selfhosted": ("Self-hosted runners", GA + "concepts/runners/self-hosted-runners", "docs"),
    "find_actions": ("Finding and customizing actions", GA + "how-tos/write-workflows/choose-what-workflows-do/find-and-customize-actions", "docs"),
    "v_nana": ("GitHub Actions tutorial: basic concepts and a CI/CD pipeline with Docker (TechWorld with Nana, 2020)", "https://www.youtube.com/watch?v=R8_veQiYBjI", "watch"),
    "variables": ("Variables reference (default environment variables)", GA + "reference/workflows-and-actions/variables", "docs"),
    "logs": ("Using workflow run logs", GA + "how-tos/monitor-workflows/use-workflow-run-logs", "docs"),
    "debug": ("Enabling debug logging", GA + "how-tos/monitor-workflows/enable-debug-logging", "docs"),
    "billing": ("GitHub Actions billing", GH + "billing/concepts/product-billing/github-actions", "docs"),
    "limits": ("Actions limits", GA + "reference/limits", "docs"),
    # real CI pipeline
    "use_jobs": ("Using jobs in a workflow (needs)", GA + "how-tos/write-workflows/choose-what-workflows-do/use-jobs", "docs"),
    "python": ("Building and testing Python", GA + "tutorials/build-and-test-code/python", "docs"),
    "artifacts": ("Workflow artifacts", GA + "concepts/workflows-and-actions/workflow-artifacts", "docs"),
    "upload_artifact": ("actions/upload-artifact README", "https://github.com/actions/upload-artifact", "read"),
    "caching": ("Dependency caching", GA + "concepts/workflows-and-actions/dependency-caching", "docs"),
    "caching_ref": ("Dependency caching reference (keys, scope, eviction)", GA + "reference/workflows-and-actions/dependency-caching", "docs"),
    "setup_python": ("actions/setup-python README", "https://github.com/actions/setup-python", "read"),
    "matrix": ("Running variations of jobs in a workflow (matrix)", GA + "how-tos/write-workflows/choose-what-workflows-do/run-job-variations", "docs"),
    "build_push": ("docker/build-push-action README", "https://github.com/docker/build-push-action", "read"),
    "docker_gha_cache": ("Docker docs: cache management with GitHub Actions (source)", "https://github.com/docker/docs/blob/main/content/manuals/build/ci/github-actions/cache.md", "read"),
    "rulesets": ("About rulesets", GH + "repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets", "docs"),
    "rulesets_create": ("Creating rulesets for a repository", GH + "repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository", "docs"),
    "req_checks": ("Troubleshooting required status checks", GH + "pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks", "docs"),
    "concurrency": ("Control the concurrency of workflows and jobs", GA + "how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency", "docs"),
    "skip_runs": ("Skipping workflow runs", GA + "how-tos/manage-workflow-runs/skip-workflow-runs", "docs"),
    "actionlint": ("actionlint: a linter for workflow files", "https://github.com/rhysd/actionlint", "read"),
    "act": ("act: run your GitHub Actions locally", "https://github.com/nektos/act", "read"),
    "v_kk2": ("GitHub Actions tutorial: advanced concepts, part 2 (KodeKloud)", "https://www.youtube.com/watch?v=TKj0KyX8m8o", "watch"),
    # workflow logic
    "contexts": ("Contexts reference", GA + "reference/workflows-and-actions/contexts", "docs"),
    "expressions": ("Expressions reference (operators, functions, status checks)", GA + "reference/workflows-and-actions/expressions", "docs"),
    "conditions": ("Using conditions to control job execution", GA + "how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions", "docs"),
    "pass_outputs": ("Passing information between jobs", GA + "how-tos/write-workflows/choose-what-workflows-do/pass-job-outputs", "docs"),
    "workflow_commands": ("Workflow commands (GITHUB_OUTPUT, GITHUB_ENV, job summaries)", GA + "reference/workflows-and-actions/workflow-commands", "docs"),
    "manual_run": ("Manually running a workflow", GA + "how-tos/manage-workflow-runs/manually-run-a-workflow", "docs"),
    "reuse": ("Reusing workflow configurations", GA + "concepts/workflows-and-actions/reusing-workflow-configurations", "docs"),
    "reuse_ref": ("Reusable workflows reference (limits)", GA + "reference/workflows-and-actions/reusing-workflow-configurations", "docs"),
    "reuse_howto": ("Reuse workflows", GA + "how-tos/reuse-automations/reuse-workflows", "docs"),
    "composite": ("Creating a composite action", GA + "tutorials/create-actions/create-a-composite-action", "docs"),
    "metadata_syntax": ("Metadata syntax for actions (action.yml)", GA + "reference/workflows-and-actions/metadata-syntax", "docs"),
    "skill_reusable": ("GitHub Skills: Reusable workflows (hands-on course)", "https://github.com/skills/reusable-workflows", "read"),
    "v_composite": ("Ultimate guide to GitHub composite actions (CoderDave)", "https://www.youtube.com/watch?v=w8ZALhqoHgs", "watch"),
    "envs": ("Deployment environments", GA + "concepts/workflows-and-actions/deployment-environments", "docs"),
    "envs_ref": ("Deployments and environments reference", GA + "reference/workflows-and-actions/deployments-and-environments", "docs"),
    "manage_envs": ("Managing environments for deployment", GA + "how-tos/deploy/configure-and-manage-deployments/manage-environments", "docs"),
    "script_injection": ("Script injections", GA + "concepts/security/script-injections", "docs"),
    # shipping safely
    "secrets": ("About secrets", GA + "concepts/security/secrets", "docs"),
    "use_secrets": ("Using secrets in GitHub Actions", GA + "how-tos/write-workflows/choose-what-workflows-do/use-secrets", "docs"),
    "use_variables": ("Store information in variables", GA + "how-tos/write-workflows/choose-what-workflows-do/use-variables", "docs"),
    "token": ("GITHUB_TOKEN", GA + "concepts/security/github_token", "docs"),
    "token_tut": ("Use GITHUB_TOKEN for authentication in workflows", GA + "tutorials/authenticate-with-github_token", "docs"),
    "publish_images": ("Publishing Docker images", GA + "tutorials/publish-packages/publish-docker-images", "docs"),
    "ghcr": ("Working with the Container registry", GH + "packages/working-with-a-github-packages-registry/working-with-the-container-registry", "docs"),
    "pkg_visibility": ("Configuring a package's access control and visibility", GH + "packages/learn-github-packages/configuring-a-packages-access-control-and-visibility", "docs"),
    "metadata": ("docker/metadata-action README", "https://github.com/docker/metadata-action", "read"),
    "oidc": ("OpenID Connect", GA + "concepts/security/openid-connect", "docs"),
    "oidc_aws": ("Configuring OpenID Connect in Amazon Web Services", GA + "how-tos/secure-your-work/security-harden-deployments/oidc-in-aws", "docs"),
    "oidc_ref": ("OpenID Connect reference", GA + "reference/security/oidc", "docs"),
    "aws_action": ("aws-actions/configure-aws-credentials README", "https://github.com/aws-actions/configure-aws-credentials", "read"),
    "secure_use": ("Secure use reference", GA + "reference/security/secure-use", "docs"),
    "prt": ("Securely using pull_request_target", GA + "reference/security/securely-using-pull_request_target", "docs"),
    "pwn": ("Preventing pwn requests (GitHub Security Lab)", "https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/", "read"),
    "checkout": ("actions/checkout README (what changed in v6 and v7)", "https://github.com/actions/checkout", "read"),
    "lockfiles": ("Workflow dependency lockfiles (public preview)", GA + "concepts/security/workflow-dependency-lockfiles", "docs"),
    "dependabot_actions": ("Keeping your actions up to date with Dependabot", GH + "code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions", "docs"),
    "dependabot_opts": ("Dependabot options reference", GH + "code-security/reference/supply-chain-security/dependabot-options-reference", "docs"),
    "cisa": ("CISA alert: tj-actions/changed-files supply chain compromise (CVE-2025-30066)", "https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066", "read"),
    "v_checkout_sec": ("Keeping your GitHub Actions and workflows secure (GitHub Checkout)", "https://www.youtube.com/watch?v=Jn0kfAuJI2o", "watch"),
    "actions_docs": ("GitHub Actions documentation", GH + "actions", "docs"),
}


def refs(*keys):
    return [{"title": R[k][0], "url": R[k][1], "kind": R[k][2]} for k in keys]


def sources(*keys):
    return [{"title": R[k][0], "url": R[k][1]} for k in keys]


def link(k, text=None):
    """Inline markup link to a registered URL."""
    return f"[{text or R[k][0]}]({R[k][1]})"
