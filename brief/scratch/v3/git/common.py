"""Shared helpers for the Part 2 (Git) build and the Day 23 rework."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
LABS = ROOT / "labs" / "git"
FILES = pathlib.Path(__file__).resolve().parent / "files"


def lab(name):
    """Return a lab file's text exactly as it is on disk."""
    return (LABS / name).read_text()


def scratch_file(name):
    return (FILES / name).read_text().rstrip("\n")


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


def src(title, url):
    return {"title": title, "url": url}


def mcq(q, options, answer, why, frm=None):
    d = {"q": q, "options": options, "answer": answer, "why": why}
    if frm:
        d["from"] = frm
    return d


def step(say, code=None, lang="console"):
    d = {"say": say}
    if code:
        d["code"] = code.strip("\n")
        d["lang"] = lang
    return d


# Links confirmed in this task (WebSearch results, the github/docs repo or git ls-remote).
L = {
    "progit": "https://git-scm.com/book/en/v2",
    "pg_recording": "https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository",
    "pg_objects": "https://git-scm.com/book/en/v2/Git-Internals-Git-Objects",
    "pg_nutshell": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell",
    "pg_config": "https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration",
    "pg_contrib": "https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project",
    "pg_reset": "https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified",
    "pg_stash": "https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning",
    "pg_tagging": "https://git-scm.com/book/en/v2/Git-Basics-Tagging",
    "pg_basicmerge": "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging",
    "pg_rebasing": "https://git-scm.com/book/en/v2/Git-Branching-Rebasing",
    "pg_rewriting": "https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History",
    "pg_remote": "https://git-scm.com/book/en/v2/Git-Branching-Remote-Branches",
    "pg_signing": "https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work",
    "pg_internals_maint": "https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery",
    "doc_reflog": "https://git-scm.com/docs/git-reflog",
    "doc_restore": "https://git-scm.com/docs/git-restore",
    "doc_gitignore": "https://git-scm.com/docs/gitignore",
    "doc_status": "https://git-scm.com/docs/git-status",
    "doc_merge": "https://git-scm.com/docs/git-merge",
    "doc_rerere": "https://git-scm.com/docs/git-rerere",
    "doc_rebase": "https://git-scm.com/docs/git-rebase",
    "doc_push": "https://git-scm.com/docs/git-push",
    "doc_bisect": "https://git-scm.com/docs/git-bisect",
    "doc_tag": "https://git-scm.com/docs/git-tag",
    "doc_datamodel": "https://git-scm.com/docs/gitdatamodel",
    "cheatsheet": "https://git-scm.com/cheat-sheet",
    "missing_notes": "https://missing.csail.mit.edu/2026/version-control/",
    "missing_video": "https://www.youtube.com/watch?v=2sjqTHE0zok",
    "fcc_pro": "https://www.youtube.com/watch?v=Uszj_k0DGsg",
    "bbg_rebase": "https://www.youtube.com/watch?v=0chZFIZLR_0",
    "lgb": "https://learngitbranching.js.org/",
    "skills_conflicts": "https://github.com/skills/resolve-merge-conflicts",
    "skills_review": "https://github.com/skills/review-pull-requests",
    "gh_username": "https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git",
    "gh_ignoring": "https://docs.github.com/en/get-started/git-basics/ignoring-files",
    "gh_remotes": "https://docs.github.com/en/get-started/git-basics/managing-remote-repositories",
    "gh_conflict_cli": "https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-using-the-command-line",
    "gh_nonff": "https://docs.github.com/en/get-started/using-git/dealing-with-non-fast-forward-errors",
    "gh_add_ssh": "https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account",
    "gh_sig_about": "https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification",
    "gh_sig_tell": "https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key",
    "gh_about_pr": "https://docs.github.com/en/pull-requests/get-started/about-pull-requests",
    "gh_create_pr": "https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request",
    "gh_review_changes": "https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request",
    "gh_helping_review": "https://docs.github.com/en/pull-requests/concepts/helping-others-review-your-changes",
    "gh_codeowners": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners",
    "gh_flow": "https://docs.github.com/en/get-started/using-github/github-flow",
    "gh_ci": "https://docs.github.com/en/actions/get-started/continuous-integration",
    "gh_cd": "https://docs.github.com/en/actions/get-started/continuous-deployment",
    "gh_releases": "https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases",
    "gh_merge_queue": "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue",
    "gh_merge_methods": "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github",
    "gh_pr_video": "https://www.youtube.com/watch?v=nCKdihvneS0",
    "google_review": "https://google.github.io/eng-practices/review/",
    "fowler_ci": "https://martinfowler.com/articles/continuousIntegration.html",
    "fowler_branching": "https://martinfowler.com/articles/branching-patterns.html",
    "tbd": "https://trunkbaseddevelopment.com/",
    "semver": "https://github.com/semver/semver/blob/master/semver.md",
    "argo_rollouts": "https://github.com/argoproj/argo-rollouts",
    "sre_book": "https://sre.google/sre-book/table-of-contents/",
}
