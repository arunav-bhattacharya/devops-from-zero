"""Day 9: Branches, merging, rebasing and remotes."""
from common import L, lab, mcq, ref, scratch_file, src, step

SECTIONS = [
    {
        "h": "Branches and tags are pointers",
        "body": (
            "Day 8 showed that a branch is a file holding one commit hash. So creating a branch writes 41 bytes, and git never copies your project to make one. "
            "The commands you need:\n\n"
            "- `git switch -c currency-first` creates a branch at the current commit and moves HEAD to it.\n"
            "- `git switch main` moves HEAD back and changes your files to match main's snapshot.\n"
            "- `git branch -v` lists the branches and the commit each one points to.\n"
            "- `git branch -d readme-fix` deletes a branch that is already merged. The commits stay; only the name goes.\n\n"
            "Uncommitted edits come along when you switch, as long as the other branch does not change the same files. "
            "If it does, git refuses to switch, so that it never overwrites your work. Commit or stash first.\n\n"
            "A tag is a pointer that never moves. Git has two kinds:\n\n"
            "- A lightweight tag is only a name for a commit: `git tag v0.1.0 0a622b0`.\n"
            "- An annotated tag is an object of its own, with a tagger, a date and a message: `git tag -a v1.0.0 -m \"First release\"`.\n\n"
            "I made one of each in the practice repo, and `git cat-file -t v1.0.0` printed `tag` for the annotated one, and `commit` for the lightweight one. "
            "Use annotated tags for releases, because they record who tagged what, and when. "
            "A plain `git push` does not send tags, so push each one by name: `git push origin v1.0.0`."
        ),
        "refs": [
            ref("Pro Git: Tagging", L["pg_tagging"], "read"),
            ref("Learn Git Branching (interactive, in the browser)", L["lgb"], "read"),
        ],
    },
    {
        "h": "Fast-forward and three-way merges",
        "body": (
            "`git merge other` brings the commits of `other` into the branch you are on. What happens depends on the shape of the history:\n\n"
            "- Fast-forward: your branch gained no commits since `other` split off from it. Git moves your branch pointer forward to `other`'s newest commit and creates nothing new.\n"
            "- Three-way merge: both branches have new commits. Git finds the merge base, the newest commit both branches contain, and compares each side with it. "
            "It combines the two sets of changes into a merge commit with two parents.\n\n"
            "When I merged a one-commit branch into main in the practice repo, git printed `Updating d6aad6e..a18a0e8` and then `Fast-forward`. "
            "The three in \"three-way\" are the merge base and the two branch tips. A change made on only one side goes in as it is. "
            "A line that both sides changed, in different ways, is a conflict.\n\n"
            "`git merge-base main currency-first` prints that shared commit, `c711550` in the practice repo. Two flags change the default:\n\n"
            "- `--no-ff` makes a merge commit even when a fast-forward was possible. The Merge pull request button on GitHub works this way (Day 23).\n"
            "- `--ff-only` refuses to merge unless a fast-forward is possible. It is a safe way to update your `main` from `origin/main`."
        ),
        "refs": [
            ref("Pro Git: Basic branching and merging", L["pg_basicmerge"], "read"),
            ref("git-merge reference", L["doc_merge"], "docs"),
        ],
    },
    {
        "h": "Merge conflicts: reading the markers",
        "body": (
            "A conflict means git found two different edits to the same lines and will not guess which one you want. "
            "The merge stops halfway, `git status` lists the file under `both modified`, and the file holds both versions between markers:\n\n"
            "- `<<<<<<< HEAD` starts your version, from the branch you are on.\n"
            "- `=======` separates the two versions.\n"
            "- `>>>>>>> currency-first` ends the version from the branch you are merging in.\n\n"
            "Edit the file until it says what it should, and delete every marker line. `git diff --check` warns about any marker you missed. "
            "Then `git add` the file to mark it resolved, and `git commit` to finish the merge. "
            "You can always back out: `git merge --abort` puts everything back the way it was before the merge.\n\n"
            "Two settings in the Files section make conflicts easier. With `merge.conflictStyle zdiff3`, git adds a block after `|||||||` that shows the lines as they were in the merge base. "
            "Seeing the original tells you what each side changed. With `rerere.enabled true` (rerere stands for reuse recorded resolution), "
            "git remembers how you resolved a conflict and reuses that resolution when the same conflict comes back.\n\n"
            "Git only checks that the text merged. It does not know if the code still works, so run the tests after you resolve a conflict."
        ),
        "refs": [
            ref("Resolving a merge conflict using the command line (GitHub Docs)", L["gh_conflict_cli"], "docs"),
            ref("GitHub Skills: Resolve merge conflicts (hands-on course)", L["skills_conflicts"], "read"),
            ref("git-rerere reference", L["doc_rerere"], "docs"),
        ],
    },
    {
        "h": "Rebase: replay your commits on a new base",
        "body": (
            "Rebase is the other way to bring your branch up to date with main. `git rebase main`, run on your feature branch, works in three steps:\n\n"
            "1. It lists the commits on your branch that main does not have.\n"
            "2. It moves your branch to main's newest commit.\n"
            "3. It applies your commits again, one at a time, on top.\n\n"
            "Each replayed commit has a new parent. The parent is part of a commit's hash, so every replayed commit is a new commit with a new ID. "
            "The old ones still exist, but no branch points to them any more. You end up with a straight line of history, as if you had started your work today.\n\n"
            "If a replayed commit conflicts, the rebase stops on that commit. You fix the file and `git add` it as in a merge, "
            "then run `git rebase --continue`, not `git commit`. `git rebase --abort` takes your branch back to where it was. "
            "Git replays the commits one at a time, so you may resolve conflicts more than once.\n\n"
            "One rule matters more than the rest: do not rebase commits that other people already have. Their copies still hold the old commits, "
            "so their history and yours no longer match, and someone has to fix it by hand. "
            "Rebasing your own branch before anyone builds on it is fine, and that is how most teams use it."
        ),
        "refs": [
            ref("Pro Git: Rebasing", L["pg_rebasing"], "read"),
            ref("Git merge vs rebase: everything you need to know (ByteByteGo)", L["bbg_rebase"], "watch"),
        ],
    },
    {
        "h": "Clean up a branch before review",
        "body": (
            "Real work produces commits like `wip`, `fix typo` and `really fix it`. Before you ask for a review, an interactive rebase turns them into a short story a reviewer can follow. "
            "The command `git rebase -i main` opens your editor with one line per commit, oldest first. You change the word at the start of a line:\n\n"
            "- `pick` keeps the commit as it is.\n"
            "- `reword` keeps it and lets you edit the message.\n"
            "- `squash` melds it into the commit above it and lets you edit the combined message.\n"
            "- `fixup` melds it into the commit above it and drops its message.\n"
            "- `drop` removes it.\n\n"
            "You can also move lines to reorder commits. Save and close the editor, and git replays the commits as you wrote them. "
            "In today's team scenario, changing `pick` to `fixup` on Ben's `wip` commit turns three commits into two. "
            "For fixes you make later there is a shortcut: commit with `git commit --fixup <commit>`, run `git rebase -i --autosquash main`, "
            "and git moves the fix under the right commit and marks it `fixup` for you.\n\n"
            "`git cherry-pick <commit>` copies one commit onto the branch you are on, as a new commit. "
            "It is the tool for a hotfix that must also land on a release branch, or for saving one good commit from a branch you are about to throw away. "
            "Add `-x` and the new commit's message records which commit it came from."
        ),
        "refs": [
            ref("Pro Git: Rewriting history", L["pg_rewriting"], "read"),
            ref("Git for professionals: tools and concepts (freeCodeCamp)", L["fcc_pro"], "watch"),
            ref("git-rebase reference", L["doc_rebase"], "docs"),
        ],
    },
    {
        "h": "Remotes: fetch, pull and push",
        "body": (
            "A remote is a name for another copy of the repository, usually on GitHub, and `git clone` calls it `origin`. "
            "Your repository also keeps remote-tracking branches such as `origin/main`. They record where the remote's branches were the last time you talked to it, "
            "and they only move when you fetch.\n\n"
            "- `git fetch` downloads new commits and moves the `origin/...` pointers. It never changes your own branches or files, so it is always safe.\n"
            "- `git pull` is a fetch followed by a merge or a rebase onto your branch's upstream, the remote branch it tracks.\n"
            "- `git push` uploads your commits and moves the branch on the remote. The first time, `git push -u origin json-logs` also sets the upstream.\n\n"
            "When you and the remote both added commits, and you have not told git what to do, `git pull` stops with `fatal: Need to specify how to reconcile divergent branches.` "
            "Choose once. I set `pull.rebase true`, which replays my unpushed commits on top of the fetched ones and keeps the history straight.\n\n"
            "After a rebase, git refuses a normal push, because the remote branch has commits yours no longer contains. "
            "A plain `git push --force` overwrites the remote branch no matter what. With `--force-with-lease`, git overwrites it only if it still points where your `origin/...` copy says. "
            "If a teammate pushed in the meantime, git rejects your push with `(stale info)`, and their commit survives. "
            "Use the lease every time. It trusts your last fetch, though, so an editor that fetches in the background can defeat it. "
            "Look at `git log origin/json-logs` before any force push.\n\n"
            "Open-source projects work with forks. A fork is your own copy of someone else's repository on GitHub. "
            "You push branches to your fork and open pull requests back to the original, which you add as a second remote, usually called `upstream`."
        ),
        "refs": [
            ref("Pro Git: Remote branches", L["pg_remote"], "read"),
            ref("git-push reference (--force-with-lease)", L["doc_push"], "docs"),
            ref("Dealing with non-fast-forward errors (GitHub Docs)", L["gh_nonff"], "docs"),
        ],
    },
    {
        "h": "Logging in to GitHub, and signing your commits",
        "body": (
            "GitHub accepts pushes over HTTPS or SSH. On Day 2, `gh auth login` set up HTTPS and told git to use gh's login, so pushing hello-devops already works. "
            "To use SSH instead, reuse your key from Day 7:\n\n"
            "1. Add the public key to your account: `gh ssh-key add ~/.ssh/id_ed25519.pub --title \"My Mac\"`, or on GitHub under Settings, SSH and GPG keys, New SSH key.\n"
            "2. Test it with `ssh -T git@github.com`. It answers `Hi USERNAME! You've successfully authenticated, but GitHub does not provide shell access.`\n"
            "3. Point the repository at the SSH address: `git remote set-url origin git@github.com:USERNAME/hello-devops.git`.\n\n"
            "Anyone can set `user.name` to anything, so the author line on a commit proves nothing. "
            "A signed commit carries a signature that only your private key can make, and Git 2.34 and later can sign with the same SSH key:\n\n"
            "1. Tell git to sign with SSH, and which key: `gpg.format ssh` and `user.signingkey`. The Files section has the commands.\n"
            "2. Set `commit.gpgsign true`, so every commit gets signed.\n"
            "3. Upload the public key again, this time as a signing key: `gh ssh-key add ~/.ssh/id_ed25519.pub --type signing`.\n\n"
            "GitHub then marks your commits Verified. The signature lives inside the commit object: `git cat-file -p HEAD` shows a `gpgsig` block, "
            "which is also why signing changes a commit's hash. Turn signing on only once the key exists. If git cannot load the key, every commit fails with `fatal: failed to write commit object`."
        ),
        "refs": [
            ref("Adding a new SSH key to your GitHub account (GitHub Docs)", L["gh_add_ssh"], "docs"),
            ref("Telling Git about your signing key (GitHub Docs)", L["gh_sig_tell"], "docs"),
            ref("About commit signature verification (GitHub Docs)", L["gh_sig_about"], "docs"),
        ],
    },
]

DIAGRAM = (
    '<svg viewBox="0 0 560 268" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Top: a three-way merge joins main and a feature branch with a merge commit M. '
    'Bottom: a rebase copies the feature commits D and E on top of main as new commits, and the old ones are left behind">'
    '<text class="ts" x="24" y="22" font-size="11" text-anchor="start">merge: a new commit with two parents</text>'
    '<rect class="bx" x="24" y="34" width="44" height="30" rx="10"/>'
    '<text class="t" x="46" y="54" font-size="13" text-anchor="middle">A</text>'
    '<line class="ln" x1="68" y1="49" x2="84" y2="49" marker-end="url(#ar)"/>'
    '<rect class="bx" x="88" y="34" width="44" height="30" rx="10"/>'
    '<text class="t" x="110" y="54" font-size="13" text-anchor="middle">B</text>'
    '<line class="ln" x1="132" y1="49" x2="148" y2="49" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="152" y="34" width="44" height="30" rx="10"/>'
    '<text class="tk" x="174" y="54" font-size="13" text-anchor="middle">C</text>'
    '<line class="ln" x1="126" y1="64" x2="154" y2="82" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="152" y="84" width="44" height="30" rx="10"/>'
    '<text class="tk" x="174" y="104" font-size="13" text-anchor="middle">D</text>'
    '<line class="ln" x1="196" y1="99" x2="212" y2="99" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="216" y="84" width="44" height="30" rx="10"/>'
    '<text class="tk" x="238" y="104" font-size="13" text-anchor="middle">E</text>'
    '<line class="ln" x1="196" y1="49" x2="276" y2="49" marker-end="url(#ar)"/>'
    '<line class="ln" x1="260" y1="90" x2="282" y2="66" marker-end="url(#ar)"/>'
    '<rect class="bxp" x="280" y="34" width="44" height="30" rx="10"/>'
    '<text class="tk" x="302" y="54" font-size="13" text-anchor="middle">M</text>'
    '<text class="ts" x="238" y="130" font-size="11" text-anchor="middle">feature</text>'
    '<text class="ts" x="302" y="80" font-size="11" text-anchor="middle">main</text>'
    '<text class="ts" x="356" y="46" font-size="11" text-anchor="start">history shows both lines</text>'
    '<text class="ts" x="356" y="64" font-size="11" text-anchor="start">safe on shared branches</text>'
    '<text class="ts" x="24" y="162" font-size="11" text-anchor="start">rebase: your commits copied on top of main, with new IDs</text>'
    '<rect class="bx" x="24" y="174" width="44" height="30" rx="10"/>'
    '<text class="t" x="46" y="194" font-size="13" text-anchor="middle">A</text>'
    '<line class="ln" x1="68" y1="189" x2="84" y2="189" marker-end="url(#ar)"/>'
    '<rect class="bx" x="88" y="174" width="44" height="30" rx="10"/>'
    '<text class="t" x="110" y="194" font-size="13" text-anchor="middle">B</text>'
    '<line class="ln" x1="132" y1="189" x2="148" y2="189" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="152" y="174" width="44" height="30" rx="10"/>'
    '<text class="tk" x="174" y="194" font-size="13" text-anchor="middle">C</text>'
    '<line class="ln" x1="196" y1="189" x2="212" y2="189" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="216" y="174" width="44" height="30" rx="10"/>'
    '<text class="tk" x="238" y="194" font-size="13" text-anchor="middle">D\'</text>'
    '<line class="ln" x1="260" y1="189" x2="276" y2="189" marker-end="url(#ar)"/>'
    '<rect class="bxo" x="280" y="174" width="44" height="30" rx="10"/>'
    '<text class="tk" x="302" y="194" font-size="13" text-anchor="middle">E\'</text>'
    '<text class="ts" x="302" y="220" font-size="11" text-anchor="middle">feature</text>'
    '<line class="lnd" x1="126" y1="204" x2="154" y2="222" marker-end="url(#ar)"/>'
    '<rect class="bx" x="152" y="224" width="44" height="30" rx="10"/>'
    '<text class="t" x="174" y="244" font-size="13" text-anchor="middle">D</text>'
    '<line class="lnd" x1="196" y1="239" x2="212" y2="239" marker-end="url(#ar)"/>'
    '<rect class="bx" x="216" y="224" width="44" height="30" rx="10"/>'
    '<text class="t" x="238" y="244" font-size="13" text-anchor="middle">E</text>'
    '<text class="ts" x="272" y="243" font-size="11" text-anchor="start">old D and E: only the reflog points here</text>'
    '<text class="ts" x="356" y="186" font-size="11" text-anchor="start">one straight line</text>'
    '<text class="ts" x="356" y="204" font-size="11" text-anchor="start">only for your own branch</text>'
    "</svg>"
)

WORKED = {
    "title": "Resolve a real conflict between two branches",
    "steps": [
        step(
            "Make a second copy of the practice repo, so today's work does not mix with Day 8's. "
            "Ana's commit on main and Ben's commit on `currency-first` both start from `c711550`, the merge base.",
            r"""
$ bash ~/code/devops-from-zero/labs/git/make-practice-repo.sh ~/code/git-merge-demo
Made a practice repo in /Users/you/code/git-merge-demo:
  8 commits: 7 on main, 1 more on the branch currency-first.
Next:  cd "/Users/you/code/git-merge-demo" && git log --oneline --graph --all
$ cd ~/code/git-merge-demo
$ git log --oneline --graph --all -4
* d6aad6e (HEAD -> main) Group thousands in prices
| * d229503 (currency-first) Show the currency before the amount
|/
* c711550 Explain how to run the calculator
* 09e16be Raise the tax rate to 25%
$ git merge-base main currency-first
c711550a5dd6a4cff3ec0eb68273f42a3d462a29
""",
        ),
        step(
            "Merge Ben's branch into main. Both commits changed the same line of `price.py`, so git cannot decide alone and stops.",
            r"""
$ git merge currency-first
Auto-merging price.py
CONFLICT (content): Merge conflict in price.py
Automatic merge failed; fix conflicts and then commit the result.
""",
        ),
        step(
            "`git status` tells you what state you are in, and how to get out of it again.",
            r"""
$ git status
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   price.py

no changes added to commit (use "git add" and/or "git commit -a")
""",
        ),
        step(
            "Look at the clash. Above `=======` is main's version (HEAD), with commas for thousands. Below it is Ben's, with the currency first.",
            r"""
$ sed -n '14,20p' price.py

def label(net):
<<<<<<< HEAD
    return f"{total(net):,.2f} {CURRENCY}"
=======
    return f"{CURRENCY} {total(net):.2f}"
>>>>>>> currency-first
""",
        ),
        step(
            "You decide the result, and here both ideas are good. Open `price.py` in your editor. "
            "Replace the five lines from `<<<<<<<` to `>>>>>>>` with one line that puts the currency first and keeps the commas. "
            "Now `git diff --check` prints nothing, so no marker is left, and the program runs.",
            r"""
$ sed -n '15,16p' price.py
def label(net):
    return f"{CURRENCY} {total(net):,.2f}"
$ git diff --check
$ python3 price.py
EUR 1,543.12
""",
        ),
        step(
            "Mark the conflict as resolved with `git add`, then commit. Git opens your editor with the message `Merge branch 'currency-first'` already written; "
            "save and close it. Your merge commit's ID will differ from this one.",
            r"""
$ git add price.py
$ git commit
[main 25ff3e9] Merge branch 'currency-first'
""",
        ),
        step(
            "The graph shows the two lines of work joined again, and the merge commit object has two `parent` lines: main's old tip and Ben's commit. "
            "Run `git branch -d currency-first` now if you like, because the branch is fully merged.",
            r"""
$ git log --oneline --graph -5
*   25ff3e9 (HEAD -> main) Merge branch 'currency-first'
|\
| * d229503 (currency-first) Show the currency before the amount
* | d6aad6e Group thousands in prices
|/
* c711550 Explain how to run the calculator
* 09e16be Raise the tax rate to 25%
$ git cat-file -p HEAD | head -3
tree d4386084c94d006452ad946a2569a35f723338de
parent d6aad6e3057b617ea767db224d5348b52ca46c3f
parent d2295036425ce18950e26087949488d2eaf547b5
""",
        ),
    ],
}

CODE = [
    {
        "lang": "bash",
        "title": "git-setup-day9.sh: settings for branches and teams (run after Day 8's git-setup.sh)",
        "src": scratch_file("git-setup-day9.sh"),
        "run": "bash git-setup-day9.sh",
    },
    {
        "lang": "bash",
        "title": "labs/git/make-team-scenario.sh: a pretend team with a shared remote (already in the course repo)",
        "src": lab("make-team-scenario.sh").rstrip("\n"),
        "run": "bash ~/code/devops-from-zero/labs/git/make-team-scenario.sh ~/code/git-team",
    },
]

COMMANDS = [
    {"cmd": "git switch -c json-logs", "what": "Create a branch at the current commit and switch to it."},
    {"cmd": "git branch -vv", "what": "List branches with their newest commit and the upstream each one tracks."},
    {"cmd": "git merge --ff-only origin/main", "what": "Bring main up to date, but only if no merge commit is needed."},
    {"cmd": "git merge --abort", "what": "Give up on a merge with conflicts and go back to how things were."},
    {"cmd": "git rebase origin/main", "what": "Replay your branch's commits on top of the newest main (your own branch only)."},
    {"cmd": "git rebase --continue", "what": "Carry on with a rebase after you fixed and staged a conflict."},
    {"cmd": "git rebase -i origin/main", "what": "Edit your branch's commits before review: reword, squash, fixup, drop or reorder."},
    {"cmd": "git cherry-pick -x <commit>", "what": "Copy one commit onto the current branch and note where it came from."},
    {"cmd": "git tag -a v1.1.0 -m \"JSON logs\"", "what": "Create an annotated tag on the current commit."},
    {"cmd": "git push origin v1.1.0", "what": "Send one tag to the remote. A plain push does not send tags."},
    {"cmd": "git fetch", "what": "Download new commits and move the origin/... pointers. Changes nothing of yours."},
    {"cmd": "git pull --rebase", "what": "Fetch, then replay your unpushed commits on top of the remote branch."},
    {"cmd": "git push -u origin json-logs", "what": "Push a new branch and remember it as the upstream."},
    {"cmd": "git push --force-with-lease", "what": "Push a rewritten branch, but refuse if the remote moved since your last fetch."},
    {"cmd": "ssh -T git@github.com", "what": "Check that GitHub accepts your SSH key; it greets you by username."},
    {"cmd": "git log --show-signature -1", "what": "Show the last commit and check its signature (needs an allowed signers file locally)."},
]

LESSON = {
    "id": "d09",
    "title": "Branches, merging, rebasing and remotes",
    "minutes": 50,
    "goal": "By the end you can branch, merge and rebase on purpose, resolve a conflict calmly, tidy a branch before review, and work with a remote, including a force push that cannot destroy a teammate's work.",
    "guess": mcq(
        "You rebase your feature branch onto the newest main. What happens to your commits?",
        [
            "They move on top of main and keep their IDs",
            "Git squashes them into a single merge commit",
            "Git writes copies of them with new IDs",
            "They are deleted, and you redo the work",
        ],
        2,
        "A commit's ID covers its parent. Rebase gives each commit a new parent, so git writes new commits and moves your branch to them; the old ones are left behind in the reflog.",
    ),
    "terms": [
        {"term": "Merge base", "plain": "The newest commit that two branches both contain. Git compares each side with it."},
        {"term": "Fast-forward", "plain": "A merge where git only moves the branch pointer forward, because that branch had no new commits."},
        {"term": "Merge commit", "plain": "A commit with two parents that joins two lines of history."},
        {"term": "Merge conflict", "plain": "Both sides changed the same lines in different ways, so git stops and asks you."},
        {"term": "Rebase", "plain": "Replaying your commits one by one on top of another commit, which creates new commits."},
        {"term": "Remote-tracking branch", "plain": "Your copy of where a remote branch was at your last fetch, such as origin/main."},
        {"term": "Upstream", "plain": "The remote branch your local branch is linked to, used by a plain git pull or git push."},
        {"term": "Force with lease", "plain": "A force push that is refused if the remote branch moved since you last fetched."},
    ],
    "sections": SECTIONS,
    "analogy": (
        "Two people write chapters of the same report in shared folders. A merge staples their pages together and adds a cover note that says \"these two drafts joined here\". "
        "A rebase is retyping your pages so they start after the latest version of the report. The words stay the same, but they are new pages, "
        "and anyone who photocopied your old pages now holds pages the report no longer has. "
        "Unlike a typist, git does the retyping in a second, which is exactly why it is so easy to rebase pages other people already copied."
    ),
    "diagram": DIAGRAM,
    "diagram_caption": "A merge adds one commit with two parents; a rebase copies your commits on top of main with new IDs.",
    "worked": WORKED,
    "code": CODE,
    "commands": COMMANDS,
    "mistake": (
        "Plain `git push --force` after a rebase silently deletes any commit a teammate pushed to that branch in the meantime. "
        "Git does not warn you, and their work is gone from the remote. "
        "Use `git push --force-with-lease`, and when it says `stale info`, fetch and look at what changed before you push again."
    ),
    "real_world": (
        "A security fix lands on `main`, and customers on the 2.3 release need it too, without the features that came after it. "
        "The release manager runs `git cherry-pick -x` with the fix's commit onto the `release-2.3` branch, CI tests it there, and the patch release ships with a tag `v2.3.5`. "
        "The `-x` note in the message lets anyone trace the copy back to the original pull request."
    ),
    "task": {
        "title": "Play Ben: rebase, a conflict and a safe force push",
        "steps": [
            "Run `make-team-scenario.sh` from the Files section. Read its last lines: you play Ben, in `~/code/git-team/ben`, and `origin.git` plays GitHub.",
            "As Ben, look at the graph, then fetch, then look again. Say in one sentence what Ana did while you were not looking.",
            "Rebase `json-logs` onto `origin/main`. When it stops on a conflict, keep both changes (Ana's log level and your JSON format), mark it resolved and continue.",
            "Push the branch. Read why git refuses, then push again with a lease.",
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
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences why a rebased branch needs a force push, and why `--force-with-lease` is the safe way to do it. Mention commit IDs and `origin/<branch>`.",
        "answer": (
            "A rebase replays my commits on a new parent, so they become new commits with new IDs. "
            "The remote branch still has the old commits, so a normal push is refused, because it would drop them. "
            "A push with `--force-with-lease` overwrites the remote branch only if it still points where my `origin/<branch>` says, which is where it was at my last fetch. "
            "If a teammate pushed after that, the push fails with stale info instead of deleting their commit."
        ),
    },
    "recap": [
        "Branches and tags are pointers; tags never move, and annotated tags record who made them.",
        "A fast-forward only moves a pointer; a three-way merge compares both tips with the merge base and adds a commit with two parents.",
        "Resolve a conflict by editing the file, deleting the markers, then `git add` and commit (or `rebase --continue`).",
        "Rebase replays your commits with new IDs: great for your own branch, never for commits others have.",
        "Fetch is always safe; pull is fetch plus merge or rebase; after a rebase, push with `--force-with-lease`.",
        "Push over HTTPS with gh or over SSH with your Day 7 key, and sign commits with that key to get the Verified badge.",
    ],
    "check": [
        mcq(
            "Your branch `fix-login` has two commits, and nobody has committed to main since you branched. You run `git switch main && git merge fix-login`. What happens?",
            [
                "Git creates a merge commit with two parents",
                "Git moves main forward to your newest commit",
                "Git asks you to resolve a conflict first",
                "Git rebases fix-login onto main",
            ],
            1,
            "Main has no commits of its own since the split, so git fast-forwards the main pointer and makes no new commit.",
        ),
        mcq(
            "Halfway through `git rebase main`, git stops with a conflict in `config.yaml`. You fix the file. What do you run next?",
            [
                "`git add config.yaml`, then `git rebase --continue`",
                "`git commit -am \"fix conflict\"`, then `git push`",
                "`git merge --abort`, then start the rebase again",
                "`git rebase --skip`, to keep your fixed version",
            ],
            0,
            "Staging the file marks the conflict resolved, and `--continue` lets the rebase create the commit and replay the rest; `--skip` would drop that commit.",
        ),
        mcq(
            "A teammate pushed to `shared-feature` ten minutes ago. You rebased your local copy without fetching and run `git push --force-with-lease`. What happens?",
            [
                "The push replaces their commit with your history",
                "Git merges their commit into yours on the server",
                "Git fetches for you and then pushes",
                "The push is rejected as stale, and their commit stays",
            ],
            3,
            "Your `origin/shared-feature` still shows the old position, which no longer matches the remote, so the lease fails and nothing is overwritten.",
        ),
    ],
    "interview": [
        {
            "q": "What is the difference between merge and rebase, and when do you use each?",
            "a": (
                "A merge joins two branches with a new commit that has both tips as parents, and it keeps every existing commit as it is. "
                "A rebase replays my commits on top of another branch, so they get new IDs and the history becomes a straight line. "
                "I rebase my own feature branch onto main before I ask for review, so the pull request shows only my changes. "
                "I merge when the commits are shared, because rewriting commits other people have breaks their copies."
            ),
        },
        {
            "q": "What does git pull actually do?",
            "a": (
                "It runs `git fetch`, which downloads new commits and moves the remote-tracking branches like `origin/main`, and then it integrates the upstream branch into mine. "
                "By default that second step is a merge, and with `pull.rebase true` it is a rebase of my unpushed commits on top. "
                "If both sides have new commits and nothing is configured, current git stops and asks me to choose. "
                "When I want to look before I integrate, I run `git fetch` alone and inspect `git log HEAD..origin/main`."
            ),
        },
        {
            "q": "Why use --force-with-lease instead of --force?",
            "a": (
                "Both overwrite a remote branch with my history, which I need after a rebase or an amend. "
                "Plain `--force` does it unconditionally, so it deletes any commit someone else pushed in the meantime. "
                "The lease version first checks that the remote branch still points where my remote-tracking branch says, and refuses otherwise. "
                "It is not perfect, because a background fetch updates that pointer, so I still look at the remote branch before I force."
            ),
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": (
            "Something is broken, and you know an older commit where it still worked. `git bisect` finds the first bad commit by binary search. "
            "It checks out the commit halfway between good and bad, you say which one it is, and it halves the range again. "
            "Ten rounds cover about a thousand commits.\n\n"
            "Try it in a fresh practice repo. The question: which commit moved the tax rate away from 20%?\n\n"
            "1. Run `git bisect start`, then `git bisect bad main` and `git bisect good 0a622b0`. Git checks out `16cc719`, about halfway, and says `2 revisions left to test after this`.\n"
            "2. You could test each commit by hand and answer `git bisect good` or `git bisect bad`. Or hand git a command that answers for you: "
            "`git bisect run grep -q \"TAX_RATE = 0.20\" price.py`.\n"
            "3. Git runs the command on three commits and prints `09e16be8b89955258da3da735bc530fb8594f563 is the first 'bad' commit`, followed by Ben's commit and its message.\n"
            "4. `git bisect reset` takes HEAD back to where you started.\n\n"
            "The command you give `bisect run` decides everything, so know its rules. Exit code 0 means good. Any code from 1 to 127 means bad, except 125. "
            "Exit 125 means \"this commit cannot be tested, skip it\", which you need when some commits do not even build. "
            "The docs show the pattern `git bisect run sh -c \"make || exit 125; ~/check_test_case.sh\"`. "
            "For hello-devops, `git bisect run pytest -q test_app.py` would work, as long as the test you care about exists in the good commit.\n\n"
            "Bisect also explains why teams care about small commits that each build and pass the tests. "
            "If one commit mixes a refactor, a feature and a config change, bisect can only point at all three at once. "
            "If every commit does one thing, the commit bisect names is usually the answer.\n\n"
            "`git bisect log` prints your answers so far. If you marked a commit wrongly, save that log to a file, delete the wrong line, and run `git bisect reset` and then `git bisect replay` on the file. "
            "The full list of options is in the [git-bisect reference](https://git-scm.com/docs/git-bisect)."
        ),
    },
    "sources": [
        src("Pro Git: Rebasing", L["pg_rebasing"]),
        src("git-push reference", L["doc_push"]),
        src("About commit signature verification (GitHub Docs)", L["gh_sig_about"]),
        src("git-bisect reference", L["doc_bisect"]),
    ],
}
