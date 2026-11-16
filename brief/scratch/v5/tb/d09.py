"""Book-voice rewrite of d09 (fifth edition). Run: python3 brief/scratch/v5/tb/d09.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture two colleagues, Ana and Ben, who each take a copy of the shop's price list home for the weekend. Ana groups the thousands with commas. Ben moves the currency to the front. On Monday the list goes to the printer at noon, and both of them have changed the same line.

Someone has to combine the two copies. The easy move is to keep whichever one arrived last. That is how a weekend of work quietly disappears: "last one wins" feels fair, and nobody notices what was lost.

Last time, you saw that a commit is a full snapshot and a branch is only a sticky note on one. That leaves a question open: what happens when two notes move apart?

In this lesson, we'll give work its own branch, join branches back together, and settle a real clash between Ana and Ben. Then we'll share it all through GitHub without destroying anyone's commits. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "Rebase is a Git command that moves your branch's commits so they start from the newest main. What happens to those commits?",
    "why": "A commit's ID covers its parent, and rebase gives each commit a new parent. So Git writes new commits and moves your branch to them, and the old ones are left behind in the reflog.",
}

terms_plain = [
    "The newest commit that two branches both contain; Git compares each side with it.",
    "A merge where Git only moves the branch pointer forward, because that branch had no new commits of its own.",
    "A commit with two parents that joins two lines of history.",
    "Both sides changed the same lines in different ways, so Git stops and asks you to choose.",
    "Replaying your commits one by one on top of another commit, which creates new commits.",
    "Your own record of where a branch on the shared copy was at your last fetch, such as origin/main.",
    "The branch on the shared copy that your own branch is linked to, used by a plain git pull or git push.",
    "A force push that is refused if the shared branch moved since you last fetched.",
]

s1 = """Ben wants to try showing the currency first, without touching the price list everyone else uses. So he makes a branch, a second sticky note, and his half-done work grows next to main without touching it. Last time, you saw that a branch is a file holding one commit hash. Creating one writes 41 bytes, and Git never copies your project to make it. The commands you need:

- `git switch -c currency-first` creates a branch at the current commit and moves HEAD (Git's "you are here" marker) to it.
- `git switch main` moves HEAD back and changes your files to match main's snapshot.
- `git branch -v` lists the branches and the commit each one points to.
- `git branch -d readme-fix` deletes a branch that is already merged. The commits stay; only the name goes.

What about edits you have not committed yet? They come along when you switch, because they live on your desk and in the tray. The working tree and the staging area belong to no branch. That works as long as the other branch does not change the same files. If it does, Git refuses to switch, so that it never overwrites your work. Commit or stash (shelve) your edits first.

A tag is a sticky note glued down so it never moves. So `v1.0.0` still names the same commit next year, when you need to rebuild or compare that release, the version you handed to users. Git has two kinds:

- A lightweight tag is only a name for a commit: `git tag v0.1.0 0a622b0`.
- An annotated tag is an object of its own, with a tagger, a date and a message: `git tag -a v1.0.0 -m "First release"`.

With one of each in the practice repo, `git cat-file -t v1.0.0` printed `tag` for the annotated one, and `commit` for the lightweight one. Use annotated tags for releases, because they record who tagged what, and when. A plain `git push` (which sends your commits to GitHub) does not send tags. Push each one by name: `git push origin v1.0.0`.

Branches let work drift apart. Sooner or later, it has to come back together. Next, we'll join two branches."""

s2 = """`git merge other` brings the commits of `other` into the branch you are on. What Git does depends on the shape of the history, and there are only two shapes.

In the first, your branch gained no commits since `other` split off from it. Git simply moves your sticky note forward to `other`'s newest commit and creates nothing new. That is a fast-forward. In the practice repo, merging a one-commit branch into main printed `Updating d6aad6e..a18a0e8` and then `Fast-forward`.

In the second shape, both branches have new commits, like Ana's and Ben's weekend copies. Now Git needs a third version to compare against: the merge base, the newest commit both branches contain. Git compares each side with the base and combines the two sets of changes. It saves the result as a merge commit with two parents. In the office, it staples both drafts together with a cover note that says "these two joined here".

Why does Git need that third version? Say the base has `TAX_RATE = 0.20`, main has `0.25`, and your branch still has `0.20`. Without the base, Git would see two different lines and could not tell which side changed. With it, the answer is plain: only main changed that line, so Git takes `0.25`. The three in "three-way" are the merge base and the two branch tips, each branch's newest commit. A change made on only one side goes in as it is. A line that both sides changed, in different ways, is a conflict.

`git merge-base main currency-first` prints that shared commit, `c711550` in the practice repo. Two options change the default:

- `--no-ff` makes a merge commit even when a fast-forward was possible, so the history shows where a branch's work came in. GitHub's Merge pull request button works this way. (A pull request asks teammates to review a branch before it is merged; Day 23 covers them.)
- `--ff-only` refuses to merge unless a fast-forward is possible. It is a safe way to update your `main` from `origin/main`, your record of GitHub's main. If your `main` has a stray commit of its own, Git stops instead of making a surprise merge.

Ana and Ben, though, changed the same line. Next, we'll see what Git does when it cannot decide."""

s3 = """Back to Monday morning. Ana's line groups thousands and Ben's puts the currency first, on the same line of `price.py`. Git will not guess which one you want. The merge stops halfway, and `git status` lists the file under `both modified`. The file now holds both versions between markers, lines Git adds to show where each version starts and ends:

- `<<<<<<< HEAD` starts your version, from the branch you are on.
- `=======` separates the two versions.
- `>>>>>>> currency-first` ends the version from the branch you are merging in.

The first time, it looks as if Git broke your file. It didn't. It is asking you a question.

To answer, edit the file until it says what it should, and delete every marker line. `git diff --check` warns about any marker you missed. Then `git add` the file to mark it resolved, and `git commit` to finish the merge. You can always back out: `git merge --abort` puts everything back the way it was before the merge.

Two settings in the Files section make conflicts easier:

- With `merge.conflictStyle zdiff3`, Git adds a block after `|||||||` that shows the lines as they were in the merge base. Seeing the original tells you what each side changed.
- With `rerere.enabled true`, Git remembers how you resolved a conflict. It reuses that resolution when the same conflict comes back.

Tests are small programs that check that your code still does what it should, and you will write them from Part 4 on. They matter here, because Git only checks the text.

**Git checks that the text merged, not that the code works. Run the tests after every conflict.**

A merge is one way to bring a branch up to date. Next, we'll meet the other way, which rewrites history."""

s4 = """Picture Ben's branch a week later. Main has moved on, and Ben has merged main into his branch every few days to keep up. Each merge adds a commit that says nothing about his work, and his history fills up with them. Rebase is the other way to bring a branch up to date. `git rebase main`, run on your feature branch (a branch for one new piece of work), works in three steps:

1. It lists the commits on your branch that main does not have.
2. It moves your branch to main's newest commit.
3. It applies your commits again, one at a time, on top.

In the office, a rebase retypes your pages so they start after the latest version of the report. The words stay the same, but they are new pages. Each replayed commit has a new parent. The parent is part of a commit's hash, so every replayed commit is a new commit with a new ID. The old ones still exist, but no branch points to them any more. You end up with a straight line of history, as if you had started your work today.

If a replayed commit conflicts, the rebase stops on that commit. You fix the file and `git add` it as in a merge, then run `git rebase --continue`, not `git commit`. `git rebase --abort` takes your branch back to where it was. Git replays the commits one at a time, so you may resolve conflicts more than once.

One rule matters more than the rest: do not rebase commits that other people already have. Anyone who copied your old pages now holds pages the report no longer has, so their history and yours no longer match. If a teammate then merges your rebased branch, their history holds each of your changes twice, under old and new IDs. Someone has to clean that up by hand. Unlike a typist, Git retypes in a second, which is exactly why this mistake is so easy to make.

Rebasing your own branch before anyone builds on it is fine, and that is how most teams use it. Rebase can do more than move commits, too. Next, we'll use it to tidy them."""

s5 = """Real work produces commits like `wip` (work in progress), `fix typo` and `really fix it`. Before a teammate reviews your branch, an interactive rebase turns them into a short story a reviewer can follow. The command `git rebase -i main` opens your editor with one line per commit, oldest first. You change the word at the start of a line:

- `pick` keeps the commit as it is.
- `reword` keeps it and lets you edit the message.
- `squash` melds it into the commit above it and lets you edit the combined message.
- `fixup` melds it into the commit above it and drops its message.
- `drop` removes it.

You can also move lines to reorder commits. Save and close the editor, and Git replays the commits as you wrote them. Today's task uses a pretend team on your laptop: Ana, Ben, and a shared copy that plays GitHub. There, changing `pick` to `fixup` on Ben's `wip` commit turns three commits into two.

For fixes you make later there is a shortcut. Commit with `git commit --fixup <commit>`, then run `git rebase -i --autosquash main`. Git moves the fix under the right commit and marks it `fixup` for you.

Sometimes you want one commit, not a whole branch. `git cherry-pick <commit>` copies one commit onto the branch you are on, as a new commit. Git takes the change that commit made compared with its parent, and applies the same change here. It is the tool for a hotfix (an urgent fix) that must also land on a release branch, which holds an older version you still support. It also saves one good commit from a branch you are about to throw away. Add `-x` and the new commit's message records which commit it came from.

Picture a security fix on main that customers on the older 2.3 release need too, without the newer features. The team cherry-picks it with `-x` onto `release-2.3`, tests it there, and ships it as `v2.3.5`.

So far, every branch has lived on your own laptop. Next, we'll share them."""

s6 = """Picture a second office across town with its own filing cabinet. That is GitHub. A remote is the name your repo uses for another copy of itself, like an entry in an address book. The command `git clone`, which copies a repo from GitHub to your laptop, names that entry `origin`.

Your repo also keeps notes about the other office, called remote-tracking branches, such as `origin/main`. Each one records where a branch over there was the last time you talked to it. They only move when you fetch:

- `git fetch` downloads new commits and moves the `origin/...` pointers. It never changes your own branches or files, so it is always safe.
- `git pull` is a fetch followed by a merge or a rebase onto your branch's upstream, the remote branch it is linked to.
- `git push` uploads your commits and moves the branch on the remote. The first time, `git push -u origin json-logs` also sets the upstream.

When you and the remote both added commits, and you have not told Git what to do, `git pull` stops with `fatal: Need to specify how to reconcile divergent branches.` Choose once. I prefer `pull.rebase true`, which replays your unpushed commits on top of the fetched ones and keeps the history straight.

After a rebase, Git refuses a normal push, because the remote branch has commits yours no longer contains. A plain `git push --force` overwrites the remote branch no matter what. Any commit a teammate pushed in the meantime silently disappears. With `--force-with-lease`, Git overwrites the branch only if it still points where your `origin/...` copy says. If a teammate pushed in the meantime, Git rejects your push with `(stale info)`, and their commit survives.

**A plain force push trusts you; a lease checks first. Use the lease every time.**

The lease trusts your last fetch, though, so an editor that fetches in the background can defeat it. Look at `git log origin/json-logs` before any force push.

Every push has to prove who sent it. Next, we'll set that up, and sign our commits too."""

s7 = """GitHub accepts a push only from someone it can identify, like a mail room that wants to see your staff badge. It accepts two kinds of connection: HTTPS (the encrypted web protocol, Day 11) and SSH (the secure login from Day 7). On Day 2, `gh auth login` set up HTTPS and told Git to use the login of gh, GitHub's own tool. So pushing hello-devops already works. SSH is handy on machines without gh, such as a server. To use it, reuse your key from Day 7:

1. Add the public key to your account: `gh ssh-key add ~/.ssh/id_ed25519.pub --title "My Mac"`, or on GitHub under Settings, SSH and GPG keys, New SSH key.
2. Test it with `ssh -T git@github.com`. It answers `Hi USERNAME! You've successfully authenticated, but GitHub does not provide shell access.`
3. Point the repository at the SSH address: `git remote set-url origin git@github.com:USERNAME/hello-devops.git`.

The badge proves who pushed. It says nothing about who wrote each commit. Anyone can set `user.name` to anything, so Ben could put "Ana Silva" on his commits and Git would not object. A signed commit carries a signature that only your private key can make. Anyone with the matching public key can check it. The private key is the secret half of your key pair, and the public key is the half you share. Git 2.34 and later can sign with the same SSH key:

1. Tell Git to sign with SSH, and which key: `gpg.format ssh` and `user.signingkey`. The names say gpg because Git first signed only with GPG, an older tool. The Files section has the commands.
2. Set `commit.gpgsign true`, so every commit gets signed.
3. Upload the public key again, this time as a signing key, because GitHub keeps login keys and signing keys in separate lists: `gh ssh-key add ~/.ssh/id_ed25519.pub --type signing`.

GitHub then checks each commit's signature against your signing keys and marks the commit Verified. The signature lives inside the commit object: `git cat-file -p HEAD` shows a `gpgsig` block. That is also why signing changes a commit's hash. Turn signing on only once the key exists. If Git cannot load the key, every commit fails with `fatal: failed to write commit object`.

A signature has its limit too: it proves who made a commit, not that the commit is any good. That is still a job for reviews and tests."""

sections = [
    ("Why a branch costs almost nothing, and a tag never moves", s1),
    ("Two ways to join branches: fast-forward and three-way", s2),
    ("When Git stops and asks: reading conflict markers", s3),
    ("Rebase: retype your commits on a new base", s4),
    ("Tidy a branch before anyone reviews it", s5),
    ("Sharing through a remote: fetch, pull and push", s6),
    ("Proving who you are to GitHub, and signing commits", s7),
]

closing = """We started with Ana and Ben's two copies of the price list and a noon deadline. Git joins such copies without guessing. It moves a note when it can, staples two drafts when it must, and stops to ask when both changed the same line. Rebase retypes your own pages, and a lease keeps your force push from erasing a teammate's work.

In the team task, before each push, run `git log --oneline --graph --all` and say out loud where `origin/json-logs` points.

Next, we'll leave Git and ask how computers find each other at all. When you type a web address, how does your laptop know which machine to call?"""

worked_say = [
    "Make a second copy of the practice repo, so today's work does not mix with last time's. Ana's commit on main and Ben's commit on `currency-first` both start from `c711550`, the merge base.",
    "Merge Ben's branch into main. Both commits changed the same line of `price.py`, so Git cannot decide alone, and it stops.",
    "`git status` tells you what state you are in, and how to get out of it again.",
    "Look at the clash. Above `=======` is main's version (HEAD), with commas for thousands. Below it is Ben's, with the currency first. The `sed -n '14,20p'` command prints lines 14 to 20 of the file.",
    "You decide the result, and here both ideas are good. Open `price.py` in your editor. Replace the five lines from `<<<<<<<` to `>>>>>>>` with one line that puts the currency first and keeps the commas. Now `git diff --check` prints nothing, so no marker is left, and the program runs.",
    "Mark the conflict as resolved with `git add`, then commit. Git opens your editor with the message `Merge branch 'currency-first'` already written; save and close it. Your merge commit's ID will differ from this one.",
    "The graph shows the two lines of work joined again. The merge commit object has two `parent` lines: main's old tip and Ben's commit. Run `git branch -d currency-first` now if you like, because the branch is fully merged.",
]

task = {
    "steps": [
        "Run `make-team-scenario.sh` from the Files section. Read its last lines: you play Ben, in `~/code/git-team/ben`, and a folder called `origin.git` plays GitHub.",
        "As Ben, look at the graph, then fetch, then look again. Say in one sentence what Ana did while you were not looking.",
        "Rebase `json-logs` onto `origin/main`. When it stops on a conflict, keep both changes (Ana's log level and your JSON format), mark it resolved and continue.",
        "Push the branch. Read why Git refuses, then push again with a lease.",
        "Play Ana: in `../ana`, fetch, switch to `json-logs`, add one line to `README.md`, commit and push.",
        "Back as Ben, without fetching: use an interactive rebase to fold the `wip` commit into the one before it, then push with a lease. It should fail. Explain why.",
        "Fetch, look at the graph, and bring Ana's new commit onto your rewritten branch with `git cherry-pick`. Push with a lease again.",
        "Update Ben's local `main` from `origin/main`, merge `json-logs` into it (it should be a fast-forward), and push `main`.",
        "Create an annotated tag `v1.1.0` on main and push it. In Ana's repository, pull and check that she has the tag.",
        "Ana's local `json-logs` still points at the commits from before your force push, so it shows up as a side line in her graph. Delete it there with `git branch -D json-logs`.",
    ],
    "hints": [
        "After the conflict, the `[logging]` block of `service.ini` should read `level = warning` and `format = json`.",
        "The lease compares the remote with your `origin/json-logs`, and that pointer only moves when you fetch.",
        "`git log --oneline -1 origin/json-logs` shows the one commit of Ana's that you need to cherry-pick.",
    ],
    "done_when": "You are done when `git log --oneline --graph --all` in `ana` shows main as one straight line ending in Ana's README commit, marked `tag: v1.1.0`, and `git ls-remote --tags origin` lists `v1.1.0`.",
}

explain_back = {
    "prompt": "Explain in 3 to 4 sentences why a rebased branch needs a force push, and why `--force-with-lease` is the safe way to do it. Mention commit IDs and `origin/<branch>`.",
    "answer": "A rebase replays my commits on a new parent, so they become new commits with new IDs. The remote branch still has the old commits, so a normal push is refused, because it would drop them. A push with `--force-with-lease` overwrites the remote branch only if it still points where my `origin/<branch>` says, which is where it was at my last fetch. If a teammate pushed after that, the push fails with stale info instead of deleting their commit.",
}

recap = [
    "Branches and tags are pointers; tags never move, and annotated tags record who made them.",
    "A fast-forward only moves a pointer; a three-way merge compares both tips with the merge base and adds a commit with two parents.",
    "Resolve a conflict by editing the file and deleting the markers, then `git add` and commit (or `rebase --continue`), then run the tests.",
    "Rebase replays your commits with new IDs: fine for your own branch, never for commits others have.",
    "Fetch is always safe; pull is fetch plus merge or rebase; after a rebase, push with `--force-with-lease`.",
    "The limits: Git checks only text, not working code, and a signature proves who made a commit, not that it is right.",
]

check = [
    {"q": "Your branch `fix-login` has two commits, and nobody has committed to main since you branched. You run `git switch main && git merge fix-login`. What happens?",
     "why": "Main has no commits of its own since the split, so Git fast-forwards the main pointer and makes no new commit."},
    {"q": "Halfway through `git rebase main`, Git stops with a conflict in `config.yaml`, a settings file. You fix the file. What do you run next?",
     "why": "Staging the file marks the conflict resolved, and `--continue` lets the rebase create the commit and replay the rest; `--skip` would drop that commit."},
    {"q": "A teammate pushed to `shared-feature` ten minutes ago. You rebased your local copy without fetching and run `git push --force-with-lease`. What happens?",
     "why": "Your `origin/shared-feature` still shows the old position, which no longer matches the remote, so the lease fails and nothing is overwritten."},
]

interview = [
    {"a": "A merge joins two branches with a new commit that has both tips as parents, and it keeps every existing commit as it is. A rebase replays my commits on top of another branch, so they get new IDs and the history becomes a straight line. I rebase my own feature branch onto main before I ask for review, so the pull request shows only my changes. I merge when the commits are shared, because rewriting commits other people have breaks their copies."},
    {"a": "It runs `git fetch`, which downloads new commits and moves the remote-tracking branches like `origin/main`. Then it brings the upstream branch into mine. By default that second step is a merge, and with `pull.rebase true` it is a rebase of my unpushed commits on top. If both sides have new commits and nothing is configured, current Git stops and asks me to choose. When I want to look before I integrate, I run `git fetch` alone and inspect `git log HEAD..origin/main`."},
    {"a": "Both overwrite a remote branch with my history, which I need after a rebase or an amend. Plain `--force` does it unconditionally, so it deletes any commit someone else pushed in the meantime. The lease version first checks that the remote branch still points where my remote-tracking branch says, and refuses otherwise. It is not perfect, because a background fetch updates that pointer, so I still look at the remote branch before I force."},
]

deeper = {"body": """Something is broken, and you know an older commit where it still worked. The command `git bisect` finds the first bad commit by binary search, the way you find a word in a paper dictionary. It checks out the commit halfway between good and bad, you say which one it is, and it halves the range again. Ten rounds cover about a thousand commits.

Try it in a fresh practice repo. The question: which commit moved the tax rate away from 20%?

1. Run `git bisect start`, then `git bisect bad main` and `git bisect good 0a622b0`. Git checks out `16cc719`, about halfway, and says `2 revisions left to test after this`.
2. You could test each commit by hand and answer `git bisect good` or `git bisect bad`. Or hand Git a command that answers for you: `git bisect run grep -q "TAX_RATE = 0.20" price.py`.
3. Git runs the command on three commits and prints `09e16be8b89955258da3da735bc530fb8594f563 is the first 'bad' commit`, followed by Ben's commit and its message.
4. `git bisect reset` takes HEAD back to where you started.

The command you give `bisect run` decides everything, so know its rules. Its exit code, the number every command reports when it ends, is the answer. Exit code 0 means good. Any code from 1 to 127 means bad, except 125. Exit 125 means "this commit cannot be tested, skip it", which you need when some commits do not even build. The docs show the pattern `git bisect run sh -c "make || exit 125; ~/check_test_case.sh"`. For hello-devops, `git bisect run pytest -q test_app.py` would work, as long as the test you care about exists in the good commit.

Bisect also explains why teams care about small commits that each build and pass the tests. If one commit mixes a refactor, a feature and a config change, bisect can only point at all three at once. If every commit does one thing, the commit bisect names is usually the answer.

`git bisect log` prints your answers so far. If you marked a commit wrongly, save that log to a file, delete the wrong line, and run `git bisect reset` and then `git bisect replay` on the file. The full list of options is in the [git-bisect reference](https://git-scm.com/docs/git-bisect).

Two names from today, for the curious: rerere stands for reuse recorded resolution, and GPG is GNU Privacy Guard."""}

apply(2, "d09", {
    "goal": "By the end you can branch, merge and rebase on purpose, resolve a conflict calmly, tidy a branch before review, and share work through a remote, including a force push that cannot destroy a teammate's work.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "diagram_caption": "A merge adds one commit with two parents; a rebase copies your commits on top of main with new IDs.",
    "worked_say": worked_say,
    "task": task,
    "explain_back": explain_back,
    "recap": recap,
    "closing": closing,
    "check": check,
    "interview": interview,
    "deeper": deeper,
    "aside": {"title": "What is a fork, and why is there a second upstream?", "after": 5, "body": "Open-source projects, which anyone may read and improve, work with forks. A fork is your own copy of someone else's repository on GitHub. You push branches to your fork and open pull requests back to the original. You add the original as a second remote, usually called `upstream`. Here the word is a remote's name, a different use from a branch's upstream."},
    "drop": ["analogy", "mistake", "real_world"],
})
print("d09 written")
