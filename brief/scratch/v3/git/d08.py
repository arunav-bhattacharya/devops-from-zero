"""Day 8: How Git works: snapshots, commits and undo."""
from common import L, lab, mcq, ref, scratch_file, src, step

SECTIONS = [
    {
        "h": "Three places your work lives",
        "body": (
            "You have typed `add`, `commit` and `push` for years. They make more sense once you know that git keeps your project in three places:\n\n"
            "- The working tree: the files in your project folder, the ones your editor changes.\n"
            "- The staging area, also called the index: the exact contents of your next commit. `git add` copies a change into it.\n"
            "- The repository: the hidden `.git` folder, where every commit lives. `git commit` turns the staging area into a new commit.\n\n"
            "The staging area is the one people skip in their heads, and it is the useful one. Say you fixed a bug and renamed a variable in the same file. "
            "You can stage only the fix, commit it with a message about the bug, and commit the rename on its own. "
            "Each commit then does one thing, so it is easy to review and easy to undo.\n\n"
            "`git status` compares the three places. In today's practice repo, after an edit to `price.py` and a new file `todo.txt`, "
            "`git status --short` printed ` M price.py` and `?? todo.txt`. The first column is the staging area and the second is the working tree. "
            "So ` M` means changed but not staged, and `M ` means staged. A file marked `MM` has part of its change staged and part not, "
            "and `??` marks a file git has never tracked."
        ),
        "refs": [
            ref("Pro Git: Recording changes to the repository", L["pg_recording"], "read"),
            ref("Version control (git), MIT Missing Semester lecture 6", L["missing_video"], "watch"),
        ],
    },
    {
        "h": "A commit is a snapshot, named by its content",
        "body": (
            "Most people picture a commit as a diff: the lines you changed. Git does not store it that way. "
            "Each commit records the whole project as it was at that moment, and git works out diffs only when you ask for one.\n\n"
            "Storing every file again in every commit would waste space, so git doesn't. It keeps three kinds of objects in `.git/objects`:\n\n"
            "- A blob holds the contents of one file. Only the bytes: no file name, no date.\n"
            "- A tree is one folder. It lists names, and each name points to a blob or to another tree.\n"
            "- A commit points to one tree, the top folder of the project. It also holds its parent commit, the author, the time and the message.\n\n"
            "Each object is named by a hash of its content: a 40-character SHA-1 hash that git usually shortens to 7 characters. "
            "The same content gets the same name on every computer. `echo hello | git hash-object --stdin` prints "
            "`ce013625030ba8dba906f756967f9e9ca394464a` on your Mac and on mine. "
            "So a file that did not change is the same blob in every commit. "
            "In the practice repo, `README.md` is the blob `c1118d8` in both of the last two commits, and git stores it once.\n\n"
            "A commit's hash covers its tree, its parent, its author line and its message. Change any of them, even one letter of the message, "
            "and you get a different commit with a new hash. Remember that for Day 9, because it is why a rebase gives your commits new IDs. "
            "Git 3.0 plans to make the longer SHA-256 hashes the default for new repositories, and it has no release date yet. "
            "Nothing in this course depends on which kind you have."
        ),
        "refs": [
            ref("Pro Git: Git objects", L["pg_objects"], "read"),
            ref("MIT Missing Semester: Version control and Git (notes)", L["missing_notes"], "read"),
        ],
    },
    {
        "h": "HEAD and branches are pointers",
        "body": (
            "A branch is a small file that holds one commit hash. In the practice repo, `.git/refs/heads/main` contains "
            "`d6aad6e3057b617ea767db224d5348b52ca46c3f`, the newest commit on main. When you commit, git writes the new commit and moves that pointer to it. "
            "No files get copied. (Git can also pack these files into one, so `git rev-parse main` is the safe way to ask.)\n\n"
            "Commits point back to their parents, so history is a chain, and you can count back along it. "
            "`HEAD~1` is the parent of HEAD, and `HEAD~2` is its grandparent.\n\n"
            "HEAD answers the question \"where am I?\". Usually it points to a branch: `.git/HEAD` contains `ref: refs/heads/main`. "
            "A new commit moves main, and HEAD comes along because it points at main. "
            "You can also check out a commit directly, as in `git switch --detach 09e16be`, which git calls a detached HEAD. "
            "That is fine for looking around. A commit you make there belongs to no branch, so run `git switch -c some-name` before you leave, "
            "or it will be hard to find again.\n\n"
            "`git log --oneline --graph --all` draws the whole picture. In the practice repo it shows `(HEAD -> main)` on the newest commit "
            "and a side branch, `currency-first`, that splits off one commit earlier. Day 9 is about branches. "
            "For today, remember that they are pointers, because most undo commands work by moving one."
        ),
        "refs": [
            ref("Pro Git: Branches in a nutshell", L["pg_nutshell"], "read"),
            ref("gitdatamodel: Git's data model (official docs)", L["doc_datamodel"], "docs"),
        ],
    },
    {
        "h": "Set git up once",
        "body": (
            "Git reads settings from three levels, and the most specific one wins:\n\n"
            "- System settings apply to every user of the machine. You rarely touch them.\n"
            "- Global settings are yours, in `~/.gitconfig`. Most settings go here.\n"
            "- Local settings belong to one repository, in `.git/config`. A work email for one work repo goes here.\n\n"
            "Run `git-setup.sh` from the Files section once, with your own name and email in it. It sets:\n\n"
            "1. Your name and email. Every commit records them, and GitHub links commits to your account by the email, so use one your GitHub account has verified.\n"
            "2. `init.defaultBranch main`. Without it, `git init` still names the first branch `master`. Git 3.0 will make `main` the default.\n"
            "3. `core.editor`. Git opens it for commit messages, merges and rebases. With `code --wait`, git waits until you close the VS Code tab.\n"
            "4. Four aliases. `git st` and `git lg` alone save a lot of typing.\n\n"
            "The script only adds settings, so the lines that `gh auth login` wrote on Day 2 stay. "
            "When git behaves differently on two machines, `git config --list --show-origin` prints every setting and the file it came from. "
            "Git 2.46 added a newer spelling, `git config set user.name ...`. The older form used in this course still works."
        ),
        "refs": [
            ref("Setting your username in Git (GitHub Docs)", L["gh_username"], "docs"),
            ref("Pro Git: Git configuration", L["pg_config"], "read"),
        ],
    },
    {
        "h": "The everyday loop, up close",
        "body": (
            "Most of your day is status, add, diff, commit and log. A few details make them much more useful:\n\n"
            "- `git add -p` shows your changes one hunk at a time and asks `(1/2) Stage this hunk [y,n,q,a,d,k,K,j,J,g,/,e,p,P,?]?`. "
            "Answer `y` to stage it, `n` to skip it, `?` for help on the rest.\n"
            "- Plain `git diff` shows what you changed but have not staged. `git diff --staged` shows what the next commit will contain.\n"
            "- `git diff HEAD~1` compares your files with an older commit. `git show 09e16be` prints one commit with its diff.\n"
            "- `git log -p -- price.py` lists every change ever made to one file.\n"
            "- `git blame price.py` names the last commit that touched each line. In the practice repo, line 3 points at Ben's `09e16be`, the commit that raised the tax rate.\n\n"
            "Run `git diff --staged` before every commit. It takes two seconds and catches the debug print you forgot.\n\n"
            "A commit message is a note to whoever runs `git blame` on your line next year. Most tools assume this shape:\n\n"
            "1. A subject of about 50 characters, in the imperative: \"Raise the tax rate to 25%\", not \"raised tax\".\n"
            "2. A blank line.\n"
            "3. A body, wrapped at about 72 characters, that says why. The diff already shows what changed.\n\n"
            "When you need a body, run plain `git commit` without `-m`, and git opens your editor."
        ),
        "refs": [
            ref("Pro Git: Contributing to a project (commit guidelines)", L["pg_contrib"], "read"),
            ref("git-status reference (short format)", L["doc_status"], "docs"),
        ],
    },
    {
        "h": "Ignore files: keep junk and secrets out",
        "body": (
            "A `.gitignore` file lists files that git should act as if it cannot see. The practice repo has four patterns:\n\n"
            "- `*.log` matches any file ending in `.log`, in any folder.\n"
            "- `.env` matches a file with exactly that name, anywhere.\n"
            "- `build/` ends with a slash, so it matches folders only.\n"
            "- `__pycache__/` keeps Python's cache folders out.\n\n"
            "A few more rules cover most cases. A leading slash ties a pattern to the top of the repo, so `/config.ini` ignores only that one file. "
            "A `!` in front brings back something an earlier line ignored. A line starting with `#` is a comment, and when several lines match, the last one wins.\n\n"
            "When you can't tell why a file is ignored, ask git. `git check-ignore -v .env debug.log` printed `.gitignore:3:.env` for `.env` "
            "and `.gitignore:2:*.log` for `debug.log`: the file, the line number and the pattern that matched.\n\n"
            "The rules only apply to files git does not track yet. If you committed `.env` once, adding it to `.gitignore` changes nothing. "
            "`git rm --cached .env` stops tracking it and keeps your copy, and then you commit. "
            "If that file held a real password or token, change it, because it is still in the old commits. Day 64 covers secrets properly."
        ),
        "refs": [
            ref("gitignore: pattern format (official docs)", L["doc_gitignore"], "docs"),
            ref("Ignoring files (GitHub Docs)", L["gh_ignoring"], "docs"),
        ],
    },
    {
        "h": "The undo toolbox",
        "body": (
            "Most undo commands either move a branch pointer or copy files between the three places. "
            "Pick one by asking two questions: did I commit it, and did I push it?\n\n"
            "Not committed yet:\n\n"
            "- `git restore price.py` throws away unstaged edits to a file. Git never stored them, so look at `git diff` first.\n"
            "- `git restore --staged price.py` unstages the file and keeps your edit.\n"
            "- `git stash` shelves all uncommitted changes and leaves a clean tree. `git stash pop` brings them back, and `-u` includes new files.\n"
            "- `git clean -n` lists the untracked files that `git clean -f` would delete.\n\n"
            "Committed, not pushed:\n\n"
            "- `git commit --amend` replaces the last commit, to fix its message or add a forgotten file.\n"
            "- `git reset --soft HEAD~1` removes the last commit and keeps its changes staged. `--mixed`, the default, keeps them unstaged. `--hard` throws them away too.\n\n"
            "Already pushed, or on a shared branch:\n\n"
            "- `git revert 09e16be` adds a new commit that undoes the old one. History only grows, so nobody else's copy breaks.\n\n"
            "Amend and reset replace commits on your branch. If you already pushed the old ones, your teammates have them, and your next push is rejected. "
            "Day 9 covers when rewriting a shared branch is acceptable. When something seems lost, run `git reflog` before anything else. "
            "It lists every position HEAD has had, newest first, and a commit you reset away stays recoverable for at least 30 days by default."
        ),
        "refs": [
            ref("Pro Git: Reset demystified", L["pg_reset"], "read"),
            ref("git-reflog reference", L["doc_reflog"], "docs"),
            ref("git-restore reference", L["doc_restore"], "docs"),
        ],
    },
]

DIAGRAM = (
    '<svg viewBox="0 0 560 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="HEAD points to the branch main, main points to a commit, '
    'the commit points to a tree and to its parent commit, and the tree points to one blob per file">'
    '<rect class="bxo" x="8" y="24" width="72" height="40" rx="10"/>'
    '<text class="tk" x="44" y="49" font-size="13" text-anchor="middle">HEAD</text>'
    '<line class="ln" x1="80" y1="44" x2="100" y2="44" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="104" y="24" width="72" height="40" rx="10"/>'
    '<text class="tk" x="140" y="49" font-size="13" text-anchor="middle">main</text>'
    '<line class="ln" x1="176" y1="44" x2="196" y2="44" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="200" y="24" width="136" height="40" rx="10"/>'
    '<text class="tk" x="268" y="49" font-size="13" text-anchor="middle">commit d6aad6e</text>'
    '<line class="ln" x1="336" y1="44" x2="380" y2="44" marker-end="url(#ar)"/>'
    '<rect class="bxg" x="384" y="24" width="120" height="40" rx="10"/>'
    '<text class="tk" x="444" y="49" font-size="13" text-anchor="middle">tree 3ba153e</text>'
    '<line class="ln" x1="428" y1="64" x2="404" y2="116" marker-end="url(#ar)"/>'
    '<line class="ln" x1="462" y1="64" x2="500" y2="116" marker-end="url(#ar)"/>'
    '<rect class="bx" x="352" y="120" width="96" height="40" rx="10"/>'
    '<text class="t" x="400" y="145" font-size="13" text-anchor="middle">README.md</text>'
    '<rect class="bx" x="464" y="120" width="88" height="40" rx="10"/>'
    '<text class="t" x="508" y="145" font-size="13" text-anchor="middle">price.py</text>'
    '<line class="lnd" x1="268" y1="64" x2="268" y2="116" marker-end="url(#ar)"/>'
    '<text class="ts" x="276" y="94" font-size="11" text-anchor="start">parent</text>'
    '<rect class="bx" x="200" y="120" width="136" height="40" rx="10"/>'
    '<text class="t" x="268" y="145" font-size="13" text-anchor="middle">commit c711550</text>'
    '<text class="ts" x="92" y="88" font-size="11" text-anchor="middle">pointers you can move</text>'
    '<text class="ts" x="268" y="184" font-size="11" text-anchor="middle">the snapshot before</text>'
    '<text class="ts" x="452" y="184" font-size="11" text-anchor="middle">blobs: file contents</text>'
    "</svg>"
)

WORKED = {
    "title": "Look inside a commit, lose it, get it back",
    "steps": [
        step(
            "First run `git-setup.sh` from the Files section, so git knows your name and email. "
            "Then make the practice repo. If you cloned the course repo on Day 3, run `git -C ~/code/devops-from-zero pull` to get the new `labs/git` folder. "
            "The script fixes every name and date, so your commit IDs match the ones below.",
            r"""
$ bash ~/code/devops-from-zero/labs/git/make-practice-repo.sh
Made a practice repo in /Users/you/code/git-practice:
  8 commits: 7 on main, 1 more on the branch currency-first.
Next:  cd "/Users/you/code/git-practice" && git log --oneline --graph --all
$ cd ~/code/git-practice
""",
        ),
        step(
            "Look at the history, then follow the pointers by hand. HEAD names a branch, and the branch file holds the hash of the newest commit on it.",
            r"""
$ git log --oneline --graph --all
* d6aad6e (HEAD -> main) Group thousands in prices
| * d229503 (currency-first) Show the currency before the amount
|/
* c711550 Explain how to run the calculator
* 09e16be Raise the tax rate to 25%
* 16cc719 Add a discount function
* e47dd86 Ignore logs, local settings and build output
* 0a622b0 Add the price calculator
* d98baf0 Add a README
$ cat .git/HEAD
ref: refs/heads/main
$ cat .git/refs/heads/main
d6aad6e3057b617ea767db224d5348b52ca46c3f
""",
        ),
        step(
            "Print the commit object itself. It is a few lines of text: its tree, its parent, who made it and when (seconds since 1970, plus a time zone), and the message. "
            "The tree lists one blob per file.",
            r"""
$ git cat-file -p HEAD
tree 3ba153e4fe5c6ba0df305b135fafa8d93dc7edf0
parent c711550a5dd6a4cff3ec0eb68273f42a3d462a29
author Ana Silva <ana@example.com> 1791467100 +0200
committer Ana Silva <ana@example.com> 1791467100 +0200

Group thousands in prices
$ git cat-file -p 'HEAD^{tree}'
100644 blob 30a5edbc2d6f87052940a808cbca5e1a4c628c72	.gitignore
100644 blob c1118d8ee2a795d748677d153f46e99b3f428052	README.md
100644 blob ffd69e3613a552567710cc14ab3bbdfe65b8d3bb	price.py
""",
        ),
        step(
            "Now make a commit of your own, then the mistake: you meant to undo one commit and keep its changes (`--soft HEAD~1`), "
            "but you typed `--hard HEAD~2`. Your commit and Ana's are gone from the log. Your new commit's ID will differ from `6e176d6`, "
            "because your name and the time are part of it.",
            r"""
$ echo "Prices include VAT." >> README.md
$ git commit -am 'Say that prices include VAT'
[main 6e176d6] Say that prices include VAT
 1 file changed, 1 insertion(+)
$ git reset --hard HEAD~2
HEAD is now at c711550 Explain how to run the calculator
$ git log --oneline -2
c711550 (HEAD -> main) Explain how to run the calculator
09e16be Raise the tax rate to 25%
""",
        ),
        step(
            "The reset moved the main pointer back. It deleted nothing in `.git`. The reflog lists every move of HEAD, newest first, "
            "and the lost commit is right there one line down. `cat-file` confirms the object still exists.",
            r"""
$ git reflog -4
c711550 (HEAD -> main) HEAD@{0}: reset: moving to HEAD~2
6e176d6 HEAD@{1}: commit: Say that prices include VAT
d6aad6e HEAD@{2}: commit: Group thousands in prices
c711550 (HEAD -> main) HEAD@{3}: checkout: moving from currency-first to main
$ git cat-file -t 6e176d6
commit
""",
        ),
        step(
            "Move main back to where it was one step ago. `HEAD@{1}` means \"where HEAD was before the last move\". The quotes stop any shell from reading the braces. "
            "If you are unsure, `git branch rescue 6e176d6` is the gentler choice: it puts a name on the commit and moves nothing.",
            r"""
$ git reset --hard 'HEAD@{1}'
HEAD is now at 6e176d6 Say that prices include VAT
$ git log --oneline -3
6e176d6 (HEAD -> main) Say that prices include VAT
d6aad6e Group thousands in prices
c711550 Explain how to run the calculator
""",
        ),
        step(
            "Now the limit. An edit you never committed or staged was only in the working tree. `reset --hard` overwrote it, the reflog has no entry for it, and it is gone. "
            "Commit or stash before any `--hard`.",
            r"""
$ echo "Draft note, never committed" >> README.md
$ git reset --hard
HEAD is now at 6e176d6 Say that prices include VAT
$ git reflog -1
6e176d6 (HEAD -> main) HEAD@{0}: reset: moving to HEAD
$ grep -c 'Draft note' README.md
0
""",
        ),
    ],
}

CODE = [
    {
        "lang": "bash",
        "title": "git-setup.sh: one-time git settings (edit the name and email first)",
        "src": scratch_file("git-setup.sh"),
        "run": "bash git-setup.sh",
    },
    {
        "lang": "bash",
        "title": "labs/git/make-practice-repo.sh: the practice repo for today (already in the course repo)",
        "src": lab("make-practice-repo.sh").rstrip("\n"),
        "run": "bash ~/code/devops-from-zero/labs/git/make-practice-repo.sh ~/code/git-practice",
    },
]

COMMANDS = [
    {"cmd": "git config --list --show-origin", "what": "List every git setting and the file it comes from."},
    {"cmd": "git status --short", "what": "One line per file: first letter for the staging area, second for the working tree."},
    {"cmd": "git add -p", "what": "Stage changes one hunk at a time, answering y or n for each."},
    {"cmd": "git diff --staged", "what": "Show exactly what the next commit will contain."},
    {"cmd": "git log --oneline --graph --all", "what": "Draw the history of every branch, one line per commit."},
    {"cmd": "git show 09e16be", "what": "Print one commit: its message and its changes."},
    {"cmd": "git blame price.py", "what": "Show which commit, author and date last changed each line."},
    {"cmd": "git cat-file -p HEAD", "what": "Print a raw git object, here the current commit."},
    {"cmd": "git check-ignore -v .env", "what": "Show which .gitignore line, if any, ignores a file."},
    {"cmd": "git restore --staged price.py", "what": "Unstage a file and keep your edits."},
    {"cmd": "git commit --amend", "what": "Replace the last commit. Only before you push it."},
    {"cmd": "git reset --soft HEAD~1", "what": "Undo the last commit and keep its changes staged."},
    {"cmd": "git revert 09e16be", "what": "Add a new commit that undoes an old one. Safe on shared branches."},
    {"cmd": "git stash -u", "what": "Shelve all uncommitted changes, new files included. `git stash pop` brings them back."},
    {"cmd": "git reflog", "what": "List every place HEAD has been, to find commits that look lost."},
    {"cmd": "git clean -n", "what": "Preview which untracked files `git clean -f` would delete."},
]

LESSON = {
    "id": "d08",
    "title": "How Git works: snapshots, commits and undo",
    "minutes": 50,
    "goal": "By the end you can explain what a commit really is, find your way around a repository with status, diff, log and blame, and pick the right undo command for a mistake, including getting back a commit you thought was gone.",
    "guess": mcq(
        "You run `git reset --hard HEAD~1`, and your last commit disappears from `git log`. What happened to it?",
        [
            "Git deleted the commit and its files from disk",
            "The commit still exists; only the branch pointer moved",
            "Git moved the commit into the stash for you",
            "It was pushed to GitHub as a backup copy",
        ],
        1,
        "A reset moves the branch pointer to an older commit. The commit object stays in `.git`, and `git reflog` still lists it, so you can get it back for weeks.",
    ),
    "terms": [
        {"term": "Working tree", "plain": "The normal files in your project folder, the ones you open and edit."},
        {"term": "Staging area (index)", "plain": "The exact contents of your next commit. `git add` puts changes there."},
        {"term": "Commit", "plain": "A saved snapshot of the whole project, with an author, a message and a link to its parent."},
        {"term": "Commit hash", "plain": "A 40-character ID that git computes from a commit's content; git usually shows the first 7."},
        {"term": "Blob and tree", "plain": "A blob is one file's contents. A tree is one folder: names that point to blobs and other trees."},
        {"term": "HEAD", "plain": "Git's pointer to where you are, usually the name of the current branch."},
        {"term": "Branch", "plain": "A movable name for one commit. It moves forward each time you commit on it."},
        {"term": "Reflog", "plain": "Your repository's local record of where HEAD and each branch pointed, kept for 30 to 90 days."},
    ],
    "sections": SECTIONS,
    "analogy": (
        "Picture a photographer who takes a full photo of your desk every time you say \"commit\", and files it in an album with a label made from the picture itself. "
        "Branches are sticky notes on photos. A reset moves a sticky note to an older photo, and the newer photos stay in the album, "
        "while the reflog remembers every place the notes have been. "
        "A real photographer would print the whole desk each time. Git notices which things on the desk did not move and reuses the old print of them, "
        "so a thousand commits do not take a thousand times the space."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "HEAD points to a branch, the branch to a commit, the commit to a tree and its parent, and the tree to one blob per file.",
    "worked": WORKED,
    "code": CODE,
    "commands": COMMANDS,
    "mistake": (
        "Running `git reset --hard` or `git restore .` to \"start clean\" while uncommitted work is still in the tree. "
        "Those edits were never stored in `.git`, so the reflog cannot bring them back. "
        "Commit first, even as a `wip` commit on a branch, or `git stash -u`, and then reset. Anything committed can be recovered for weeks."
    ),
    "real_world": (
        "A fix goes out on a Friday and breaks refunds. Nobody resets `main` or force-pushes. The on-call engineer runs `git revert` on the bad commit and opens a pull request, "
        "and the revert ships within minutes, with a record of what happened. "
        "On Monday, `git blame` and the original commit message explain why the code changed, which is why reviewers object to messages like \"fix stuff\"."
    ),
    "task": {
        "title": "Undo drills in the practice repo",
        "steps": [
            "Delete the practice repo from the worked example and make a fresh one, so your history matches the lesson again.",
            "Check where each of your settings comes from with `git config --list --show-origin`. In the practice repo, try `git st` and `git lg`.",
            "Using only `git cat-file`, print `price.py` as it was in commit `0a622b0`. Note the tax rate it had then.",
            "Make two separate changes in `price.py`, such as a new word in the docstring and a second `print` line. Stage only the first with `git add -p`, look at both kinds of diff, and commit it with a subject and a body. Then commit the second change.",
            "Amend the last commit to give it a better message, then amend it again to add a new file, `CHANGELOG.md`.",
            "Turn your last two commits into one with `git reset --soft`, and commit again with one clear message.",
            "Finance says the tax rate stays at 20%. Undo Ben's commit `09e16be` without rewriting history.",
            "Start an edit to `README.md`, then shelve it with stash, check that the tree is clean, and bring the edit back. Throw it away with `git restore`.",
            "Create `build/out.txt` and `notes.txt`. Use `git check-ignore -v` to show why one is ignored and the other is not. Preview with `git clean -n`, then delete the untracked one.",
        ],
        "hints": [
            "`git cat-file -p 0a622b0` gives you a tree hash. Print that tree, and it gives you the blob hash of `price.py`.",
            "Revert only needs the commit ID. Check its result with `git show HEAD`.",
            "If anything goes wrong, `git reflog` shows where you were a minute ago.",
        ],
        "done_when": "You are done when `git log --oneline -2` shows the Revert commit on top of your one combined commit, `python3 price.py` prints `1,481.40 EUR` first, and `git status --short` prints nothing.",
    },
    "explain_back": {
        "prompt": "A teammate thinks `git reset --hard` deleted their work forever. Explain in 3 to 4 sentences what a commit is, what the reset really did, and how to get the commit back. Mention snapshots, pointers and the reflog.",
        "answer": (
            "A commit is a full snapshot of the project, stored as objects in `.git` and named by a hash of its content. "
            "A branch is only a pointer to one commit, and `git reset --hard` moved that pointer to an older commit and reset the files to match. "
            "The newer commit is still in `.git`, and `git reflog` lists it, so `git reset --hard 'HEAD@{1}'` or a new branch on its hash brings it back. "
            "The only thing the reset destroyed was uncommitted work in the working tree, because git never stored that."
        ),
    },
    "recap": [
        "Git keeps your work in three places: the working tree, the staging area and the repository.",
        "A commit is a full snapshot (a tree of blobs) plus parent, author and message, named by a hash of all of it.",
        "Branches and HEAD are pointers, and most undo commands just move them.",
        "Set your name, email, default branch and editor once, with `git config --global`.",
        "Check `git diff --staged` before you commit, and debug ignore rules with `git check-ignore -v`.",
        "Not pushed: amend or reset. Pushed: revert. Looks lost: reflog.",
    ],
    "check": [
        mcq(
            "You edit `app.py`, run `git add app.py`, then edit the same file again and run `git commit`. What does the commit contain?",
            [
                "Both edits, because commit takes the current files",
                "Nothing, because the file changed after you added it",
                "Only the first edit, the version you staged",
                "Only the second edit, because it is newer",
            ],
            2,
            "A commit is made from the staging area, which still holds the version from your `git add`; the second edit stays unstaged.",
        ),
        mcq(
            "An hour ago you pushed a commit to `main` with a wrong timeout value, and three teammates have pulled since. What is the right undo?",
            [
                "`git reset --hard HEAD~1`, then push with --force",
                "`git commit --amend`, then push again",
                "`git restore` the file, then push",
                "`git revert` the commit, then push",
            ],
            3,
            "Revert adds a new commit and leaves shared history alone, so your teammates' copies stay valid.",
        ),
        mcq(
            "A repository has a 2 MB `logo.png` that never changes, and 100 commits that each change only `app.py`. How many copies of the logo does `.git` store?",
            [
                "One, because every tree points to the same blob",
                "One hundred, one per snapshot",
                "None, because git only stores diffs",
                "Two: one in the index and one in the repository",
            ],
            0,
            "A blob is named by its content, so the unchanged logo has one name and is stored once, however many commits include it.",
        ),
    ],
    "interview": [
        {
            "q": "What is the difference between git reset, git revert and git restore?",
            "a": (
                "Restore works on files. It throws away edits in the working tree, or unstages them with `--staged`, and it never moves a branch. "
                "Reset moves the current branch to another commit. With `--soft` the changes stay staged, with `--mixed` they stay as edits, and `--hard` discards them. "
                "Revert makes a new commit that undoes an old one, so history only grows. "
                "On a shared branch I use revert, because reset rewrites history that other people already have."
            ),
        },
        {
            "q": "What is inside a git commit?",
            "a": (
                "A commit is a small object. It points to one tree, the snapshot of the top folder, and to its parent commit or commits. "
                "It also holds the author, the committer, the timestamps and the message. "
                "The tree points to blobs, which hold file contents, and to subtrees for folders. "
                "Every object is named by a hash of its content, so identical files are stored once and any change to a commit gives it a new ID. "
                "Branches and tags are just names that point at commits."
            ),
        },
        {
            "q": "How would you recover a commit after a bad reset or a deleted branch?",
            "a": (
                "I run `git reflog`, which records every position HEAD and each branch had in this clone. "
                "I find the commit from before the mistake, check it with `git show`, and then either create a branch on it or reset back to it. "
                "Unreachable entries are kept for 30 days by default, so there is plenty of time. "
                "Work that was never committed or staged is the exception, because git never stored it."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "To see that git commands are only a friendly layer over the object store, make a commit without `git commit`. "
            "Git's low-level commands, called plumbing, do each step on its own. Work in a fresh practice repo:\n\n"
            "1. `echo \"Made by hand.\" > hand.txt`, then `git hash-object -w hand.txt`. It prints `3122a5d6b298c4c04deeda6383016bc58e0c2fb3` "
            "and writes the blob into `.git/objects/31/`. The first two characters of the hash become the folder name.\n"
            "2. `git update-index --add hand.txt` puts the file into the staging area. `git status --short` now shows `A  hand.txt`.\n"
            "3. `git write-tree` turns the staging area into a tree object and prints its hash.\n"
            "4. `git commit-tree <tree> -p HEAD -m \"A commit made by hand\"` creates a commit object with that tree and the current commit as its parent. "
            "It prints the new hash, and nothing points to it yet: `git log` still shows the old commit on top.\n"
            "5. `git update-ref refs/heads/main <commit>` moves the branch. Now `git log --oneline -2` shows your hand-made commit, and `git status` is clean.\n\n"
            "That is all `git commit` does, plus writing the reflog entry and running hooks.\n\n"
            "Two more things are worth seeing while you are inside `.git`. "
            "First, git stores new objects as single compressed files, one per object, under `.git/objects`. "
            "When about 6,700 loose objects pile up, git runs `git gc --auto` and packs them into one packfile, which stores similar objects as deltas against each other. "
            "You can also run `git gc` yourself. "
            "In the practice repo, 27 loose object files turned into one `.pack` file plus its index. "
            "So git does use diffs after all, but only as a storage trick inside packfiles. Every command still sees full snapshots.\n\n"
            "Second, `git gc` also deletes unreachable objects, but only after the reflog entries that point to them expire. "
            "That takes 90 days for entries that are still reachable, and 30 days for the rest. "
            "That is the window you have to rescue a commit after a bad reset. "
            "[Pro Git's chapter on maintenance and data recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery) "
            "shows how to find a lost commit even when the reflog is gone, with `git fsck --lost-found`."
        ),
    },
    "sources": [
        src("Pro Git: Git objects", L["pg_objects"]),
        src("Pro Git: Reset demystified", L["pg_reset"]),
        src("git-reflog reference", L["doc_reflog"]),
        src("gitignore: pattern format", L["doc_gitignore"]),
    ],
}
