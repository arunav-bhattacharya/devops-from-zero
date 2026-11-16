"""Book-voice rewrite of d08 (fifth edition). Run: python3 brief/scratch/v5/tb/d08.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture a shared office folder with five files in it: `prices.docx`, `prices-final.docx`, `prices-final-2.docx`, `prices-final-REAL.docx` and `prices-ben.docx`. Your manager asks a simple question: which one did we send to the shop on Tuesday? Nobody knows. Worse, someone tidied up yesterday and deleted the one with Ana's tax fix.

Saving copies under new names feels safe, and almost everyone has done it. It works for one person and a few days. It falls apart when two people edit at once, or when you need last month's version and the names no longer mean anything.

In the last lesson, Environment, packages, SSH and shell scripts, you wrote your first scripts. Scripts change too, and one day you will want an old version back.

In this lesson, we'll open up Git, the tool that keeps every saved version of a project for you. We'll look inside a saved version, lose one on purpose, and get it back. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "Git has an undo command, `git reset --hard HEAD~1`. You run it, and your last saved version disappears from Git's history list, `git log`. What happened to it?",
    "why": "The reset only moved a name tag, the branch, back to an older saved version. The version itself is still stored in the hidden `.git` folder, and `git reflog` still lists it, so you can get it back for weeks.",
}

terms_plain = [
    "The ordinary files in your project folder, the ones you open and change.",
    "A holding area with the exact contents of your next saved version; `git add` puts changes there.",
    "A saved snapshot of the whole project, with an author, a message and a link to the snapshot before it.",
    "A 40-character ID that Git computes from a commit's contents; Git usually shows only the first 7.",
    "A blob is the contents of one file, and a tree is one folder: a list of names that point to blobs and other trees.",
    "Git's marker for where you are right now, usually the name of the branch you are on.",
    "A movable name stuck on one commit, which moves forward each time you commit on it.",
    "A record, kept only on your own computer, of every place HEAD and each branch pointed to, kept for 30 to 90 days.",
]

s1 = """Picture an office. Your desk holds the pages you are working on, and next to it sits a tray for copies of pages that are ready. Behind you stands a filing cabinet. Whenever you say "save", a clerk photographs everything in the tray and files the photo.

Git keeps your project in the same three places. A project is just a folder of files, and a folder that Git looks after is called a repository, or repo. In Git's words:

- The working tree is the desk: the ordinary files in your project folder, the ones your editor changes.
- The staging area, also called the index, is the tray: the exact contents of your next saved version. The command `git add`, typed in the terminal (the text window from Part 1), copies a change into it.
- The repository is the filing cabinet: a hidden folder, `.git`, where every saved version lives. `git commit` turns the staging area into a new saved version, called a commit.

Many people skip the tray in their heads, yet it is the useful part. Say you fixed a bug and renamed something in the same file. You can put only the fix in the tray and commit it, then commit the rename on its own. Each commit does one thing, so it is easy to review and easy to undo.

This lesson uses a practice repo, built by the worked example below. It holds price-tool, a tiny price calculator by two made-up people, Ana and Ben. Its main file, `price.py`, is a short Python program that adds tax to a price.

`git status` compares the three places and tells you what differs. After an edit to `price.py` and a new file `todo.txt`, `git status --short` printed ` M price.py` and `?? todo.txt`. The first column is the tray and the second is the desk. So ` M`, with a space first, means changed but not staged (not yet in the tray), while `M ` means staged. A file marked `MM` has part of its change in the tray and part not. A file marked `??` is one Git has never tracked, or been asked to watch.

So what exactly does one of the clerk's photos hold? Next, we'll open one."""

s2 = """Most people picture a commit as a list of the lines you changed, like red marks on an essay. Git does not store it that way. Each commit records the whole project as it was at that moment, like the clerk's full photo. Git works out the changes between two commits, called a diff, only when you ask.

You may be thinking, "A full copy every time must fill my disk." It would, so Git avoids it. It keeps three kinds of objects (stored items) in the folder `.git/objects`:

- A blob holds the contents of one file. Only the bytes (the raw data): no file name, no date.
- A tree is one folder. It lists names, and each name points to a blob or to another tree.
- A commit points to one tree, the top folder of the project. It also holds its parent commit (the one before it), the author, the time and the message.

Each object is named by a hash of its content. A hash function is a recipe that turns any bytes into a short fingerprint of fixed length. The same bytes always give the same fingerprint, and a one-letter change gives a completely different one. Git uses SHA-1 (Secure Hash Algorithm 1). It gives 40 hex characters, which are the digits 0 to 9 and the letters a to f, and Git usually shows only the first 7.

So the same content gets the same name on every computer. Try `echo hello | git hash-object --stdin`, which pipes the word hello into Git's hash function. It prints `ce013625030ba8dba906f756967f9e9ca394464a` on your Mac and on any other machine.

That naming is how Git avoids copies: a file that did not change is the same blob in every commit. When you `git add` a file, Git hashes it. If an object with that name is already in `.git/objects`, there is nothing new to store. In the practice repo, `README.md` is the blob `c1118d8` in both of the last two commits, and Git stores it once.

A commit's hash covers its tree, its parent, its author line and its message. Change any of them, even one letter of the message, and you get a different commit with a new hash. That is why a rebase, a way of rewriting history in the next lesson, gives your commits new IDs. Git 3.0 plans to make the longer SHA-256 hashes the default for new repositories, with no release date yet. Nothing in this course depends on which kind you have.

Nobody wants to remember `d6aad6e`, though. Next, we'll meet the names people actually use."""

s3 = """Which commit is the newest on the main line of work? Git keeps the answer in a tiny text file. `.git/refs/heads/main` contains `d6aad6e3057b617ea767db224d5348b52ca46c3f`, the newest commit on the branch called main.

That file is the whole branch: a sticky note with one commit's name on it. When you commit, Git writes the new commit and moves the note to it. No project files get copied. (Git can also pack these small files into one bigger file, so `git rev-parse main` is the safe way to ask.)

Commits point back to their parents, so history is a chain, and you can count back along it. `HEAD~1` is the parent of HEAD, and `HEAD~2` is its grandparent.

So what is HEAD? It answers the question "where am I?", like the "you are here" arrow on a map in a shopping centre. Usually it points to a branch: `.git/HEAD` contains `ref: refs/heads/main`. A new commit moves main, and HEAD comes along, because it points at main.

`git log --oneline --graph --all` draws the whole picture, one line per commit. In the practice repo it shows `(HEAD -> main)` on the newest commit. It also shows a side branch, `currency-first`, that splits off one commit earlier. For today, one rule is enough.

**A branch is a sticky note on a commit. Most undo commands just move the note.**

Before you make commits of your own, Git needs to know who you are. Next, we'll tell it."""

s4 = """Every commit carries a name and an email, like the signature on a form. You tell Git yours once, and it remembers. Git reads its settings from three levels, and the most specific one wins:

- System settings apply to every user of the machine. You rarely touch them.
- Global settings are yours, in the file `~/.gitconfig` (the `~` means your home folder). Most settings go here.
- Local settings belong to one repository, in `.git/config`. A work email for one work repo goes here.

Run `git-setup.sh` from the Files section once, with your own name and email in it. It is a shell script like the ones from the last lesson, and it sets four things:

1. Your name and email. Every commit records them. GitHub, the website that holds your repos online, links commits to your account by the email, so use one your GitHub account has verified.
2. `init.defaultBranch main`. Without it, `git init` (the command that starts a new repo) still names the first branch `master`, while GitHub names it `main`. Git 3.0 will make `main` the default.
3. `core.editor`, the program Git opens when it needs you to write text, such as a commit message. Without it, Git usually falls back to `vi`, a terminal editor with its own keys that puzzles nearly everyone at first. With `code --wait`, Git opens VS Code and waits until you close the tab.
4. Four aliases, which are short names for longer commands. `git st` and `git lg` alone save a lot of typing.

The script only adds settings, so the lines that `gh auth login` (GitHub's own tool) wrote on Day 2 stay. When Git behaves differently on two machines, `git config --list --show-origin` prints every setting and its file.

Git 2.46 added a newer spelling, `git config set user.name ...`. The older form used in this course still works.

Now you are ready for the loop you will repeat all day: change, look, stage, save. Next, we'll slow it down."""

s5 = """Picture two changes in `price.py`, a fix and a tidy-up, that you want in separate commits. Plain `git add price.py` puts the whole file in the tray, so both land in one commit. A few options, the dash words after a command, make the loop more precise:

- `git add -p` shows your changes one hunk (a block of changed lines) at a time and asks `(1/2) Stage this hunk [y,n,q,a,d,k,K,j,J,g,/,e,p,P,?]?`. Answer `y` to stage it, `n` to skip it, and `?` for help on the rest. The row of letters looks alarming, but you need only those three.
- Plain `git diff` shows what you changed but have not staged. `git diff --staged` shows what the next commit will contain.
- `git diff HEAD~1` compares your files with an older commit. `git show 09e16be` prints one commit with its diff.
- `git log -p -- price.py` lists every change ever made to one file. The `--` ends the options, so Git reads what follows as file names.
- `git blame price.py` names the last commit that touched each line. In the practice repo, line 3 points at Ben's `09e16be`, the commit that raised the tax rate.

Run `git diff --staged` before every commit. It takes two seconds and catches the debug print you forgot, a line you added only to watch what the program was doing.

A commit message is a note to whoever runs `git blame` on your line next year, quite possibly you. Views such as `git log --oneline` and GitHub's list of commits show only its first line, so most tools expect this shape:

1. A subject of about 50 characters, in the imperative, the form of an instruction: "Raise the tax rate to 25%", not "raised tax".
2. A blank line.
3. A body, wrapped at about 72 characters, that says why. The diff already shows what changed.

The imperative matches the messages Git writes itself, such as `Revert "Raise the tax rate to 25%"`. When you need a body, run plain `git commit` without `-m`, and Git opens your editor.

Some files, though, should never be photographed at all. Next, we'll keep them out."""

s6 = """Some papers should never go near the clerk's camera: scrap notes, and above all the key to the safe. Without an ignore file, `git add .` (add everything in this folder) sweeps them all into the tray. That means log files, where programs note what they did, and Python's cache folders. Worse, it means the `.env` file that holds your tokens, secret strings that work like passwords for programs.

A `.gitignore` file is a plain text file that lists files Git should act as if it cannot see. Each line is a pattern, a short rule that matches file names. The practice repo has four patterns:

- `*.log` matches any file ending in `.log`, in any folder. The `*` stands for any characters.
- `.env` matches a file with exactly that name, anywhere.
- `build/` ends with a slash, so it matches folders only.
- `__pycache__/` keeps Python's cache folders out.

A few more rules cover most cases. A leading slash ties a pattern to the top of the repo, so `/config.ini` ignores only that one file. A `!` in front brings back something an earlier line ignored. A `#` starts a comment, and when several lines match, the last one wins.

When you can't tell why a file is ignored, ask Git. `git check-ignore -v .env debug.log` printed `.gitignore:3:.env` for `.env` and `.gitignore:2:*.log` for `debug.log`. Each answer gives the file, the line number and the pattern that matched.

Now the trap. The rules only apply to files Git does not track yet. If you committed `.env` once, adding it to `.gitignore` changes nothing, and Git keeps saving it. `git rm --cached .env` stops tracking it and keeps your copy, and then you commit. If that file held a real password or token, change it, because it is still in the old commits. Day 64, Secrets, access and policy as code, covers secrets properly.

For every other kind of mistake, Git has a toolbox. Next, we'll open it."""

s7 = """You ran a command, and something you wanted seems to be gone. Slow down before you type anything else. Most undo commands either move a sticky note or copy files between the desk, the tray and the cabinet. Pick one by asking two questions: did I commit it, and did I push it? To push is to send your commits to a shared copy, such as the one on GitHub, where teammates pull (download) them.

Not committed yet:

- `git restore price.py` copies the staged version back over your file, which throws away unstaged edits. Git never stored them, so look at `git diff` first.
- `git restore --staged price.py` copies the last commit's version into the staging area. The file is unstaged, and your edit stays.
- `git stash` saves all uncommitted changes in special commits that sit off every branch, and leaves a clean tree. `git stash pop` brings them back, and `-u` includes new files.
- `git clean -n` lists the untracked files that `git clean -f` would delete.

Committed, not pushed:

- `git commit --amend` replaces the last commit, to fix its message or add a forgotten file. Git writes a new commit with the same parent and moves the branch to it.
- `git reset --soft HEAD~1` moves your branch back one commit and touches nothing else, so that commit's changes stay staged.
- `git reset --mixed HEAD~1`, the default, also resets the staging area, so the changes stay only in your files. With `--hard` it resets your files too, and the changes are gone.

Already pushed, or on a shared branch:

- `git revert 09e16be` adds a new commit that undoes the old one. History only grows, so nobody else's copy breaks.

Amend and reset replace commits on your branch. If you already pushed the old ones, your teammates have them. Your next push is then rejected, because the remote branch (the copy on GitHub) has commits yours no longer contains. The next lesson covers when rewriting a shared branch is acceptable.

When something seems lost, run `git reflog` before anything else. It is the clerk's logbook: it lists every position HEAD has had, newest first. A commit you reset away stays recoverable for at least 30 days by default. Remember the guess at the start? That vanished commit was in the cabinet all along.

The logbook has one blind spot: an edit that lived only on your desk has no entry, and `reset --hard` destroys it.

**Anything committed can come back. Commit or stash before any `--hard`.**

All of this works on your own copy of the repo. Other people's copies come next."""

sections = [
    ("Three places your work lives: the desk, the tray and the cabinet", s1),
    ("A commit is a full snapshot, named by its content", s2),
    ("HEAD and branches are only pointers", s3),
    ("Tell Git who you are, once", s4),
    ("The everyday loop, slowed down", s5),
    ("Keep junk and secrets out with an ignore file", s6),
    ("The undo toolbox: pick by committed and pushed", s7),
]

closing = """We started with a shared folder full of `prices-final-2.docx` files and nobody sure which one was right. Git replaces that folder with three places, a cabinet of full snapshots named by their content, and sticky notes that say where each line of work stands. Undo, most of the time, means moving a note, and the reflog remembers where every note has been.

In your own hello-devops repo from Day 2, run `git status --short` and `git log --oneline --graph --all`. Name each column and each pointer you see.

Next, we'll give Ana and Ben a second line of work each, with branches, merging, rebasing and remotes. What happens when two people change the same line?"""

worked_say = [
    "First run `git-setup.sh` from the Files section, so Git knows your name and email. Then make the practice repo. If you cloned the course repo on Day 3, run `git -C ~/code/devops-from-zero pull` to download the new `labs/git` folder (`-C` tells Git which folder to work in). The script fixes every name and date, so your commit IDs match the ones below.",
    "Look at the history, then follow the pointers by hand. HEAD names a branch, and the branch file holds the hash of the newest commit on it. `cat` prints a file, as in Part 1.",
    "Print the commit object itself. It is a few lines of text: its tree and its parent, then the author (who wrote it) and the committer (who saved it). Each has a time in seconds since 1970, plus a time zone. Last comes the message. The tree lists one blob per file.",
    "Now make a commit of your own, then the mistake. You meant to undo one commit and keep its changes (`--soft HEAD~1`), but you typed `--hard HEAD~2`. Your commit and Ana's are gone from the log. Your new commit's ID will differ from `6e176d6`, because your name and the time are part of it.",
    "The reset moved the main pointer back. It deleted nothing in `.git`. The reflog lists every move of HEAD, newest first. The lost commit is right there, one line down. `cat-file -t` prints an object's type, and it confirms the object still exists.",
    "Move main back to where it was one step ago. `HEAD@{1}` means \"where HEAD was before the last move\". The quotes stop the shell, the program that reads your commands, from treating the braces as special. If you are unsure, `git branch rescue 6e176d6` is the gentler choice: it puts a name on the commit and moves nothing.",
    "Now the limit. An edit you never committed or staged was only in the working tree. The command `reset --hard` overwrote it, and the reflog has no entry for it. The `grep -c` command counts matching lines, and it finds none. Commit or stash before any `--hard`.",
]

task = {
    "steps": [
        "Delete the practice repo from the worked example and make a fresh one, so your history matches the lesson again.",
        "Check where each of your settings comes from with `git config --list --show-origin`. In the practice repo, try the aliases `git st` and `git lg`.",
        "Using only `git cat-file`, print `price.py` as it was in commit `0a622b0`. Note the tax rate it had then.",
        "Make two separate changes in `price.py`, such as a new word in the docstring (the description at the top of the file) and a second `print` line. Stage only the first with `git add -p`, look at both kinds of diff, and commit it with a subject and a body. Then commit the second change.",
        "Amend the last commit to give it a better message, then amend it again to add a new file, `CHANGELOG.md`.",
        "Turn your last two commits into one with `git reset --soft`, and commit again with one clear message.",
        "Finance says the tax rate stays at 20%. Undo Ben's commit `09e16be` without rewriting history.",
        "Start an edit to `README.md`, then shelve it with stash, check that the tree is clean, and bring the edit back. Then throw it away with `git restore`.",
        "Create `build/out.txt` and `notes.txt`. Use `git check-ignore -v` to show why one is ignored and the other is not. Preview with `git clean -n`, then delete the untracked one.",
    ],
    "hints": [
        "`git cat-file -p 0a622b0` gives you a tree hash. Print that tree, and it gives you the blob hash of `price.py`.",
        "Revert only needs the commit ID. Check its result with `git show HEAD`.",
        "If anything goes wrong, `git reflog` shows where you were a minute ago.",
    ],
    "done_when": "You are done when `git log --oneline -2` shows the Revert commit on top of your one combined commit, `python3 price.py` prints `1,481.40 EUR` first, and `git status --short` prints nothing.",
}

explain_back = {
    "prompt": "A teammate thinks `git reset --hard` deleted their work forever. Explain in 3 to 4 sentences what a commit is, what the reset really did, and how to get the commit back. Mention snapshots, pointers and the reflog.",
    "answer": "A commit is a full snapshot of the project, stored as objects in `.git` and named by a hash of its content. A branch is only a pointer to one commit, and `git reset --hard` moved that pointer to an older commit and made the files match it. The newer commit is still in `.git`, and `git reflog` lists it, so `git reset --hard 'HEAD@{1}'` or a new branch on its hash brings it back. The only thing the reset destroyed was uncommitted work in the working tree, because Git never stored that.",
}

recap = [
    "Git keeps your work in three places: the working tree (the desk), the staging area (the tray) and the repository (the cabinet).",
    "A commit is a full snapshot (a tree of blobs) plus parent, author and message, named by a hash of all of it.",
    "Branches and HEAD are pointers, and most undo commands just move them.",
    "Set your name, email, default branch and editor once with `git config --global`, and check `git diff --staged` before you commit.",
    "Not pushed: amend or reset. Pushed: revert. Looks lost: reflog.",
    "The limit: the reflog only knows about commits, so an edit you never staged or committed is gone after `reset --hard`.",
]

check = [
    {"q": "You edit `app.py`, run `git add app.py`, then edit the same file again and run `git commit`. What does the commit contain?",
     "why": "A commit is made from the staging area, which still holds the version from your `git add`; the second edit stays unstaged."},
    {"q": "An hour ago you pushed a commit to `main` with a wrong timeout value, and three teammates have pulled it since. What is the right undo?",
     "why": "Revert adds a new commit and leaves shared history alone, so your teammates' copies stay valid."},
    {"q": "A repository has a 2 MB picture, `logo.png`, that never changes, and 100 commits that each change only `app.py`. How many copies of the logo does `.git` store?",
     "why": "A blob is named by its content, so the unchanged logo has one name and is stored once, however many commits include it."},
]

interview = [
    {"a": "Restore works on files. It throws away edits in the working tree, or unstages them with `--staged`, and it never moves a branch. Reset moves the current branch to another commit. With `--soft` the changes stay staged, with `--mixed` they stay as edits, and `--hard` discards them. Revert makes a new commit that undoes an old one, so history only grows. On a shared branch I use revert, because reset rewrites history that other people already have."},
    {"a": "A commit is a small object. It points to one tree, the snapshot of the top folder, and to its parent commit or commits. It also holds the author, the committer, the timestamps and the message. The tree points to blobs, which hold file contents, and to subtrees for folders. Every object is named by a hash of its content, so identical files are stored once and any change to a commit gives it a new ID. Branches and tags are just names that point at commits."},
    {"a": "I run `git reflog`, which records every position HEAD and each branch had in this clone. I find the commit from before the mistake, check it with `git show`, and then either create a branch on it or reset back to it. Unreachable entries are kept for 30 days by default, so there is plenty of time. Work that was never committed or staged is the exception, because Git never stored it."},
]

deeper = {"body": """Git's everyday commands are a friendly layer over the cabinet of objects. To see that for yourself, make a commit without `git commit`. Git also has low-level commands, called plumbing, and each one does a single step. Work in a fresh practice repo:

1. `echo "Made by hand." > hand.txt`, then `git hash-object -w hand.txt`. It prints `3122a5d6b298c4c04deeda6383016bc58e0c2fb3` and writes the blob into `.git/objects/31/`. The first two characters of the hash become the folder name.
2. `git update-index --add hand.txt` puts the file into the staging area. `git status --short` now shows `A  hand.txt`.
3. `git write-tree` turns the staging area into a tree object and prints its hash.
4. `git commit-tree <tree> -p HEAD -m "A commit made by hand"` creates a commit object with that tree and the current commit as its parent. It prints the new hash, and nothing points to it yet: `git log` still shows the old commit on top.
5. `git update-ref refs/heads/main <commit>` moves the branch. Now `git log --oneline -2` shows your hand-made commit, and `git status` is clean.

Those five steps are what `git commit` does for you, plus writing the reflog entry and running hooks (small scripts Git can run at set moments).

Two more things are worth seeing while you are inside `.git`. First, Git stores new objects as single compressed files, one per object, under `.git/objects`. When about 6,700 of these loose objects pile up, Git runs `git gc --auto`. It packs them into one packfile, which stores similar objects as deltas, the differences from each other. You can also run `git gc` yourself. In the practice repo, 27 loose object files turned into one `.pack` file plus its index. So Git does use diffs after all, but only as a storage trick inside packfiles. Every command still sees full snapshots.

Second, `git gc` also deletes unreachable objects, but only after the reflog entries that point to them expire. That takes 90 days for entries that are still reachable, and 30 days for the rest. That is the window you have to rescue a commit after a bad reset. [Pro Git's chapter on maintenance and data recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery) shows how to find a lost commit even when the reflog is gone, with `git fsck --lost-found`."""}

apply(2, "d08", {
    "goal": "By the end you can explain what Git saves when you commit, find your way around a project's history with status, diff, log and blame, and pick the right undo for a mistake, even getting back a commit you thought was gone.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "diagram_caption": "HEAD points to a branch, the branch to a commit, the commit to its parent and to a tree, and the tree to one blob per file.",
    "worked_say": worked_say,
    "task": task,
    "explain_back": explain_back,
    "recap": recap,
    "closing": closing,
    "check": check,
    "interview": interview,
    "deeper": deeper,
    "aside": {"title": "What if HEAD points at a commit instead of a branch?", "after": 2, "body": "You can point HEAD at a commit directly, as in `git switch --detach 09e16be`. Git calls this a detached HEAD, and it is fine for looking around. A commit you make there belongs to no branch, though: no sticky note carries its name. Git's history views start from HEAD and the branch names, so once you switch away, only the reflog (the last section) still leads to that commit. Run `git switch -c some-name` before you leave, to stick a new note on it."},
    "analogy": "Picture Git as an office with a desk, a tray and a filing cabinet. You work at the desk and put finished pages in the tray. On each commit a clerk photographs the whole tray and files the photo, labelled with a fingerprint of what is in it. Branches are sticky notes on photos, a reset only moves a note, and a logbook records every move. A real clerk would print every page again each time. Git reuses the old print of every page that did not change, so a thousand commits do not take a thousand times the space.",
    "mistake": "Running `git reset --hard` or `git restore .` to \"start clean\" while uncommitted work is still on the desk. Those edits were never stored in `.git`, so the reflog cannot bring them back. Commit first, even as a `wip` (work in progress) commit on a branch, or run `git stash -u`, and then reset. Anything committed can be recovered for weeks.",
    "real_world": "Teams name exact versions by their commit hash, because a hash means the same snapshot on every computer. Picture a fix that goes out on a Friday and breaks refunds in a team's payment app. The bug report names the bad commit by its hash. Nobody resets `main` or force-pushes, which would overwrite the shared copy on GitHub. The engineer on call runs `git revert` on that hash (it adds a new commit that undoes the bad one) and ships the revert within minutes, with a record of what happened.",
})
print("d08 written")
