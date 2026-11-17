"""Book-voice rewrite of Part 2's own fields. Run after d08.py and d09.py."""
import json, pathlib
path = pathlib.Path(__file__).resolve().parents[4] / "content/p2.json"
P = json.loads(path.read_text())

P["intro"] = ("Git is the tool that keeps every saved version of a project, so nothing you commit is ever really lost. "
              "Day 8 opens a commit to see what Git actually saves, and shows how to undo almost any mistake. "
              "Day 9 covers branches, merging, rebasing and sharing work with a team through GitHub. "
              "It comes now because every later part keeps its work in Git, and from Part 6 on, every change reaches users through a pull request.")
P["recap"] = [
    "A commit is a full snapshot of the project, stored as a tree of blobs and named by a hash of its content.",
    "The working tree, the staging area and the repository are three separate places; `git status` and `git diff` compare them.",
    "Branches, tags and HEAD are pointers to commits, so a branch costs almost nothing.",
    "Undo by situation: restore for edits, amend or reset for unpushed commits, revert for shared ones, reflog when something looks lost.",
    "`.gitignore` only keeps out files Git does not track yet, and `git check-ignore -v` explains every match.",
    "A fast-forward only moves a pointer; a three-way merge compares both tips with the merge base and adds a commit with two parents.",
    "A conflict is Git asking you to choose: edit the file, delete the markers, `git add` it, and run the tests.",
    "Rebase replays commits with new IDs: use it to tidy and update your own branch, never on commits other people have.",
    "Fetch is always safe, pull is fetch plus merge or rebase, and a rewritten branch goes up with `--force-with-lease`.",
    "Push with gh's HTTPS login or your SSH key, and sign commits with that key to get GitHub's Verified badge.",
]
cards = [
    ("What is inside a commit?", "A pointer to one tree (the snapshot), its parent commit or commits, the author and committer with dates, and the message."),
    ("Does Git store each commit as a list of changes?", "No. Each commit is a full snapshot. Unchanged files reuse the same blob, and Git works out the changes only when you ask."),
    ("What is a branch, on disk?", "A tiny file that holds one commit hash and moves forward when you commit on it."),
    ("What does `.git/HEAD` usually contain?", "The current branch's name, such as `ref: refs/heads/main`."),
    ("`git diff` or `git diff --staged`: which shows what?", "`git diff` shows changes not staged yet; `--staged` shows what the next commit will contain."),
    ("You pushed a bad commit to main. How do you undo it?", "`git revert <commit>`: a new commit that undoes it, without rewriting shared history."),
    ("`reset --soft`, `--mixed` and `--hard`: how do they differ?", "All three move the branch. Soft keeps the changes staged, mixed keeps them unstaged, and hard throws them away."),
    ("How do you get back a commit after a bad `reset --hard`?", "Find it in `git reflog`, then reset to it or put a new branch on it."),
    ("Why doesn't adding `.env` to `.gitignore` stop Git tracking it?", "Ignore rules only apply to untracked files. Run `git rm --cached .env` and commit."),
    ("When is a merge a fast-forward?", "When your branch has no new commits since the other one split off, so Git only moves the pointer."),
    ("What is the merge base?", "The newest commit both branches contain. Git compares each side with it."),
    ("What do you run after fixing a conflict during a rebase?", "`git add` the file, then `git rebase --continue`."),
    ("Why does a rebase change commit IDs?", "Each replayed commit gets a new parent, and the parent is part of the hash."),
    ("`squash` or `fixup` in an interactive rebase: what is the difference?", "Both meld a commit into the one above it; squash lets you edit the combined message, fixup drops its message."),
    ("`git fetch` or `git pull`: what does each do?", "Fetch downloads commits and moves only the origin/... pointers. Pull also merges or rebases your branch."),
    ("What does `--force-with-lease` check before it overwrites?", "That the remote branch still points where your `origin/<branch>` says. If not, the push fails as stale."),
    ("Lightweight or annotated tag: what is the difference?", "A lightweight tag is only a name; an annotated tag is an object with tagger, date and message. Use annotated tags for releases."),
    ("Which three settings turn on SSH commit signing?", "`gpg.format ssh`, `user.signingkey ~/.ssh/id_ed25519.pub` and `commit.gpgsign true`; then add the key on GitHub as a signing key."),
]
assert len(cards) == len(P["flashcards"])
for f, (a, b) in zip(P["flashcards"], cards):
    f["front"], f["back"] = a, b
quiz = [
    ("You staged `config.py`, then decide it should not go into the next commit. You want to keep your edits. Which command do you run?",
     "`--staged` takes the file out of the staging area and leaves your edits in the working tree; plain restore would throw them away."),
    ("Which Git object stores a file's name?",
     "A blob holds only the bytes; the tree for the folder links each name to a blob or a subtree."),
    ("After `git reset --hard HEAD~3`, a commit you made an hour ago is missing from `git log`. What do you run first?",
     "The reflog lists where HEAD has been, so the lost commit's hash is there, and you can reset to it or branch from it."),
    ("A teammate committed `prod.env`, a file with a real API key (a password for a program), and pushed it to main yesterday. What is the complete fix?",
     "Removing and ignoring the file stops future leaks, but the key is still in the old commits, so it must be replaced."),
    ("When does `git merge feature` create a merge commit with two parents?",
     "With new commits on both sides, Git does a three-way merge and records it with a two-parent commit; otherwise it fast-forwards."),
    ("`git pull` stops with `fatal: Need to specify how to reconcile divergent branches.` What does it mean?",
     "Both sides moved, so Git needs to know whether to merge or rebase; setting `pull.rebase` answers that once."),
    ("A security fix on main must also go to the `release-2.3` branch, without the features merged since. Which command fits?",
     "Cherry-pick copies just that one commit onto the release branch; merge or rebase would bring every newer commit along."),
    ("You rebased your own branch `add-metrics`, and a plain `git push` is rejected. What do you do?",
     "The rebase gave your commits new IDs; the lease replaces the remote branch only if nobody else pushed to it since your last fetch."),
    ("Both lab scripts start with `set -euo pipefail`. What does the `-e` part do?",
     "`-e` exits on the first failing command; `-u` catches unset variables, and `pipefail` makes a failed pipe count as a failure."),
    ("`git push` to your GitHub repo suddenly asks for a password. Which fix from Day 2 applies?",
     "gh can hand your GitHub login to Git, so Git pushes with your existing gh login instead of a password."),
]
assert len(quiz) == len(P["quiz"])
for q, (a, b) in zip(P["quiz"], quiz):
    q["q"], q["why"] = a, b
res = [
    "The official book on Git, free to read; chapters 2, 3 and 10 go deeper into everything in Days 8 and 9.",
    "One lecture that builds Git up from how it stores data, in the same order as Day 8.",
    "The written version of that lecture, with exercises to try on your own repository.",
    "A browser game that draws the commit graph as you type, good for practising rebase and cherry-pick.",
    "A practical video course on interactive rebase, cherry-pick, the reflog and the ways to merge.",
    "A short, visual comparison of merge, rebase and squash.",
    "The official description of Git's objects, pointers and staging area, in a few pages.",
    "The official one-page list of everyday commands, handy to keep open while you work.",
    "A free hands-on course that walks you through a conflict in a real GitHub repository.",
    "What Verified means on GitHub, and how the different kinds of signatures compare.",
]
assert len(res) == len(P["resources"])
for r, w in zip(P["resources"], res):
    r["why"] = w
path.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")
print("p2 part fields written")
