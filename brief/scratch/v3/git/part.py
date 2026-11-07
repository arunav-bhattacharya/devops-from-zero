"""Part 2 extras: intro, recap, flashcards, resources and quiz."""
from common import L, mcq

INTRO = (
    "You have used git for years as add, commit and push. This part opens it up. Day 8 shows what a commit really is and how to undo almost anything. "
    "Day 9 covers branches, merging, rebasing and working with a remote as part of a team. "
    "It comes now because every later part keeps its work in git, and from Part 6 on, every change reaches production through a pull request."
)

RECAP = [
    "A commit is a full snapshot of the project, stored as a tree of blobs and named by a hash of its content.",
    "The working tree, the staging area and the repository are three separate places; `git status` and `git diff` compare them.",
    "Branches, tags and HEAD are pointers to commits, so a branch costs almost nothing.",
    "Undo by situation: restore for edits, amend or reset for unpushed commits, revert for shared ones, reflog when something looks lost.",
    "`.gitignore` only keeps out files git does not track yet, and `git check-ignore -v` explains every match.",
    "A fast-forward only moves a pointer; a three-way merge compares both tips with the merge base and adds a commit with two parents.",
    "A conflict is git asking you to choose: edit, delete the markers, `git add`, and run the tests.",
    "Rebase replays commits with new IDs: tidy and update your own branch with it, never commits other people have.",
    "Fetch is always safe, pull is fetch plus merge or rebase, and a rewritten branch goes up with `--force-with-lease`.",
    "Push with gh's HTTPS login or your SSH key, and sign commits with that key to get GitHub's Verified badge.",
]

FLASHCARDS = [
    {"front": "What does a commit object contain?", "back": "A pointer to one tree (the snapshot), its parent commit or commits, the author and committer with dates, and the message."},
    {"front": "Does git store each commit as a diff?", "back": "No. Each commit is a full snapshot; unchanged files reuse the same blob, and diffs are worked out when you ask."},
    {"front": "What is a branch, physically?", "back": "A tiny ref that holds one commit hash and moves forward when you commit on it."},
    {"front": "What does `.git/HEAD` usually contain?", "back": "The current branch's name, such as `ref: refs/heads/main`."},
    {"front": "`git diff` vs `git diff --staged`?", "back": "`git diff` shows changes not staged yet; `--staged` shows what the next commit will contain."},
    {"front": "You pushed a bad commit to main. How do you undo it?", "back": "`git revert <commit>`: a new commit that undoes it, without rewriting shared history."},
    {"front": "`reset --soft` vs `--mixed` vs `--hard`?", "back": "All move the branch. Soft keeps the changes staged, mixed keeps them unstaged, hard throws them away."},
    {"front": "How do you get back a commit after a bad `reset --hard`?", "back": "Find it in `git reflog`, then reset to it or put a new branch on it."},
    {"front": "Why doesn't adding `.env` to `.gitignore` stop git tracking it?", "back": "Ignore rules only apply to untracked files. Run `git rm --cached .env` and commit."},
    {"front": "When is a merge a fast-forward?", "back": "When your branch has no new commits since the other one split off, so git only moves the pointer."},
    {"front": "What is the merge base?", "back": "The newest commit both branches contain. Git compares each side with it."},
    {"front": "What do you run after fixing a conflict during a rebase?", "back": "`git add` the file, then `git rebase --continue`."},
    {"front": "Why does a rebase change commit IDs?", "back": "Each replayed commit gets a new parent, and the parent is part of the hash."},
    {"front": "`squash` vs `fixup` in an interactive rebase?", "back": "Both meld a commit into the one above it; squash lets you edit the combined message, fixup drops its message."},
    {"front": "`git fetch` vs `git pull`?", "back": "Fetch downloads commits and moves the origin/... pointers only. Pull also merges or rebases your branch."},
    {"front": "What does `--force-with-lease` check before it overwrites?", "back": "That the remote branch still points where your `origin/<branch>` says. If not, the push fails as stale."},
    {"front": "Lightweight vs annotated tag?", "back": "Lightweight is only a name; annotated is an object with tagger, date and message. Use annotated for releases."},
    {"front": "Which three settings turn on SSH commit signing?", "back": "`gpg.format ssh`, `user.signingkey ~/.ssh/id_ed25519.pub` and `commit.gpgsign true`; then add the key on GitHub as a signing key."},
]

RESOURCES = [
    {"title": "Pro Git, the free book on git", "url": L["progit"], "kind": "read",
     "why": "The official book; chapters 2, 3 and 10 go deeper into everything in Days 8 and 9, internals included."},
    {"title": "Version control (git), MIT Missing Semester lecture 6", "url": L["missing_video"], "kind": "watch",
     "why": "One lecture that builds git from its data model up, the same order as Day 8."},
    {"title": "Missing Semester notes: Version control and Git", "url": L["missing_notes"], "kind": "read",
     "why": "The written version of that lecture, with exercises to try on your own repository."},
    {"title": "Learn Git Branching", "url": L["lgb"], "kind": "read",
     "why": "A browser game that draws the commit graph as you type, good for practising rebase and cherry-pick."},
    {"title": "Git for professionals: tools and concepts (freeCodeCamp)", "url": L["fcc_pro"], "kind": "watch",
     "why": "A practical course on interactive rebase, cherry-pick, the reflog and merge strategies."},
    {"title": "Git merge vs rebase: everything you need to know (ByteByteGo)", "url": L["bbg_rebase"], "kind": "watch",
     "why": "A short, visual comparison of merge, rebase and squash."},
    {"title": "gitdatamodel: Git's data model", "url": L["doc_datamodel"], "kind": "docs",
     "why": "The official description of objects, references and the index, in a few pages."},
    {"title": "Git cheat sheet (git-scm.com)", "url": L["cheatsheet"], "kind": "docs",
     "why": "The official one-page list of everyday commands, handy to keep open."},
    {"title": "GitHub Skills: Resolve merge conflicts", "url": L["skills_conflicts"], "kind": "read",
     "why": "A free hands-on course that walks you through a conflict in a real GitHub repository."},
    {"title": "About commit signature verification (GitHub Docs)", "url": L["gh_sig_about"], "kind": "docs",
     "why": "What Verified means on GitHub, and how SSH, GPG and S/MIME signatures differ."},
]

QUIZ = [
    mcq(
        "You staged `config.py`, then decide it should not go into the next commit. You want to keep your edits. Which command do you run?",
        ["`git restore config.py`", "`git restore --staged config.py`", "`git reset --hard HEAD`", "`git rm --force config.py`"],
        1,
        "`--staged` moves the file out of the staging area and leaves your edits in the working tree; plain restore would throw them away.",
    ),
    mcq(
        "Which git object stores a file's name?",
        ["The blob with its contents", "The commit that includes it", "The tree for its folder", "The reflog entry for it"],
        2,
        "A blob holds only the bytes; the tree for the folder maps each name to a blob or a subtree.",
    ),
    mcq(
        "After `git reset --hard HEAD~3`, a commit you made an hour ago is missing from `git log`. What do you run first?",
        ["`git reflog`", "`git stash pop`", "`git fetch origin`", "`git revert HEAD~3`"],
        0,
        "The reflog lists where HEAD has been, so the lost commit's hash is there and you can reset to it or branch from it.",
    ),
    mcq(
        "A teammate committed `prod.env` with a real API key and pushed it to main yesterday. What is the complete fix?",
        [
            "Add `prod.env` to `.gitignore` and push",
            "Amend the last commit and force-push it",
            "Revert the commit, and nothing else",
            "`git rm --cached`, commit, ignore it, and rotate the key",
        ],
        3,
        "Removing and ignoring the file stops future leaks, but the key is still in the old commits, so it must be replaced.",
    ),
    mcq(
        "When does `git merge feature` create a merge commit with two parents?",
        [
            "When main has no new commits since feature split off",
            "When both main and feature have new commits",
            "Only when the merge has a conflict",
            "Only when you pass `--ff-only`",
        ],
        1,
        "With new commits on both sides, git does a three-way merge and records it with a two-parent commit; otherwise it fast-forwards.",
    ),
    mcq(
        "`git pull` stops with `fatal: Need to specify how to reconcile divergent branches.` What does it mean?",
        [
            "Your SSH key is missing on GitHub",
            "The remote branch was deleted",
            "Your branch and the remote both have new commits",
            "You have uncommitted changes in the tree",
        ],
        2,
        "Both sides moved, so git needs to know whether to merge or rebase; setting `pull.rebase` answers that once.",
    ),
    mcq(
        "A security fix on main must also go to the `release-2.3` branch, without the features merged since. Which command fits?",
        ["`git cherry-pick -x <fix>`", "`git rebase main`", "`git merge main`", "`git reset --hard main`"],
        0,
        "Cherry-pick copies just that one commit onto the release branch; merge or rebase would bring every newer commit along.",
    ),
    mcq(
        "You rebased your own branch `add-metrics`, and a plain `git push` is rejected. What do you do?",
        [
            "Delete the remote branch and push again",
            "Run `git merge --abort` and try again",
            "Merge main into the branch a second time",
            "Push with `git push --force-with-lease`",
        ],
        3,
        "The rebase gave your commits new IDs; the lease replaces the remote branch only if nobody else pushed to it since your last fetch.",
    ),
    mcq(
        "Both lab scripts use `set -euo pipefail`. What does the `-e` part do?",
        [
            "Stops the script when a command fails",
            "Prints each command before it runs",
            "Exports every variable to child processes",
            "Ignores errors inside pipes",
        ],
        0,
        "`-e` exits on the first failing command; `-u` catches unset variables and `pipefail` makes a failed pipe count as a failure.",
        "Part 1",
    ),
    mcq(
        "`git push` to your GitHub repo suddenly asks for a password. Which fix from Day 2 applies?",
        [
            "Store the password with `git config user.password`",
            "Reinstall git with Homebrew",
            "Run `gh auth setup-git`, so git uses your gh login",
            "Create a new repository with `gh repo create`",
        ],
        2,
        "gh can act as git's credential helper for github.com, so git pushes with your existing gh login instead of a password.",
        "Part 0",
    ),
]
