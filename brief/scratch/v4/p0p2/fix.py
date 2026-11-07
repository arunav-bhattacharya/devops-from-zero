"""First-principles review fixes for Days 1, 2 (content/p0.json) and Days 8, 9 (content/p2.json).
Each edit is an exact old -> new replacement inside one prose field. Re-runnable: an edit whose
new text is already present is skipped. Run from the repo root: python3 brief/scratch/v4/p0p2/fix.py"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]

# (part file, lesson id, path to the field inside the lesson, old, new)
EDITS = [
    # ---------------- Day 1 ----------------
    ("p0", "d01", ("sections", 0, "body"),
     "- Culture: dev and ops share goals, on-call duty and the review after an outage.",
     "- Culture: dev and ops share goals, on-call duty (being the person called when it breaks) and the review after an outage."),
    ("p0", "d01", ("sections", 1, "body"),
     "4. Package: the app and everything it needs go into one bundle, a container image.",
     "4. Package: the app and everything it needs go into one bundle, a container image, so it runs the same on any machine."),
    ("p0", "d01", ("sections", 1, "body"),
     "7. Run: the platform keeps the app alive, restarts it if it crashes and adds copies under load.",
     "7. Run: software on the servers keeps the app alive, restarts it if it crashes and starts extra copies when traffic grows."),
    ("p0", "d01", ("sections", 2, "body"),
     "processes, SSH and scripts.",
     "processes, SSH (logging in to other machines) and scripts."),
    ("p0", "d01", ("sections", 2, "body"),
     "(Days 10 to 14): addresses, DNS, HTTP, TLS, cloud basics, then AWS by hand.",
     "(Days 10 to 14): addresses, DNS (names to addresses), HTTP and TLS (web requests, encrypted), cloud basics, then AWS (Amazon's cloud) by hand."),
    ("p0", "d01", ("sections", 2, "body"),
     "(Days 31 to 35): create infrastructure from code files.",
     "(Days 31 to 35): create infrastructure (the machines, networks and storage an app runs on) from code files."),
    ("p0", "d01", ("sections", 2, "body"),
     "run many containers across many machines and keep them healthy.",
     "run many containers across a cluster, a group of machines, and keep them healthy."),
    ("p0", "d01", ("sections", 2, "body"),
     "(Days 58 to 60): Envoy, Istio, Linkerd and Cilium, and when you need none of them.",
     "(Days 58 to 60): tools that manage the calls between services (Envoy, Istio, Linkerd, Cilium), and when you need none."),
    ("p0", "d01", ("sections", 2, "body"),
     "Linux and networking sit underneath everything, because every server, container and CI runner you touch runs Linux and talks over a network.",
     "Linux and networking sit underneath everything. Every server, container and CI runner (the machine that runs your automated checks) runs Linux and talks over a network."),
    # The two definitions now sit where the words first appear (Part 8 bullet, pipeline step 4).
    ("p0", "d01", ("sections", 2, "body"),
     "\n\nInfrastructure means the machines, networks and storage your app runs on. A container image is your app plus everything it needs, packed so it runs the same anywhere. You meet both properly later, so a rough idea is enough today.",
     ""),
    ("p0", "d01", ("sections", 4, "body"),
     "To measure how well a team delivers, this course uses the metrics from DORA, a long-running research program that studies software teams.",
     "A team that says it ships faster now needs a way to show it. This course uses the metrics from DORA (DevOps Research and Assessment), a long-running research program that studies software teams."),
    ("p0", "d01", ("sections", 4, "body"),
     "immediate action, such as a rollback.",
     "immediate action, such as a rollback (putting the previous version back)."),
    ("p0", "d01", ("sections", 4, "body"),
     "and the best teams do well on both groups.",
     "and the best teams do well on both groups. Small changes are one reason: each one is quick to ship and easy to undo."),
    ("p0", "d01", ("sections", 6, "body"),
     "You practise Linux in a throwaway Ubuntu container from Day 2, and in a small Ubuntu virtual machine from Day 6.",
     "You practise Linux in a throwaway container running Ubuntu, a popular version of Linux, from Day 2. From Day 6 you also use a small Ubuntu virtual machine, a whole computer simulated in software."),
    ("p0", "d01", ("worked", "steps", 3, "say"),
     "Number 4 was rolled back and number 8 needed a hotfix.",
     "Number 4 was rolled back, and number 8 needed a hotfix, an urgent fix shipped outside the normal plan."),
    ("p0", "d01", ("sections", 6, "body"),
     "They are optional, you can follow Days 13 and 14",
     "They are optional: you can follow Days 13 and 14"),

    # ---------------- Day 2 ----------------
    ("p0", "d02", ("sections", 0, "body"),
     "- git and the GitHub CLI (`gh`): version control and GitHub from the terminal (today).",
     "- git and the GitHub CLI (`gh`): git records your code's history, and gh works with GitHub from the terminal (today)."),
    ("p0", "d02", ("sections", 0, "body"),
     "- VS Code with a few extensions: an editor that understands Dockerfiles, YAML, Terraform and Kubernetes files.",
     "- VS Code with a few extensions: a free code editor, plus add-ons that check Dockerfiles, YAML, Terraform, Kubernetes and Python files (today)."),
    ("p0", "d02", ("sections", 0, "body"),
     "- Docker Desktop: runs containers, including your Linux practice box (today, and Part 5).",
     "- Docker Desktop: runs containers (programs walled off inside Linux), such as your Linux practice box (today, and Part 5)."),
    ("p0", "d02", ("sections", 0, "body"),
     "- Multipass: a tool that starts a full Ubuntu virtual machine (Day 6).",
     "- Multipass: starts a full Ubuntu virtual machine, a whole Linux computer simulated on your Mac (Day 6)."),
    ("p0", "d02", ("sections", 0, "body"),
     "- terraform: creates infrastructure from code (Day 31).",
     "- terraform: creates servers, networks and other infrastructure from code files (Day 31)."),
    ("p0", "d02", ("sections", 0, "body"),
     "- kubectl, kind and helm: Kubernetes tools (Part 10).",
     "- kubectl, kind and helm: run and manage a practice Kubernetes cluster on your laptop (Part 10)."),
    ("p0", "d02", ("sections", 1, "body"),
     "On Apple Silicon Macs, Homebrew lives in `/opt/homebrew`. When the installer finishes, it prints \"Next steps\" with two or three commands. They add Homebrew to your **PATH**: the list of folders your shell searches when you type a command.\n\nMost people get stuck right here. If you skip those commands, every `brew` command fails with \"command not found\". Run exactly what the installer prints, open a new terminal tab, then run `brew --version`.",
     "On Apple Silicon Macs, Homebrew lives in `/opt/homebrew` and puts its commands in `/opt/homebrew/bin`. Your shell is the program in the terminal window that runs what you type. When you type `brew`, it looks in each folder on your **PATH**, in order, and runs the first match. The PATH that macOS starts with does not include that folder, so the shell cannot find `brew` yet.\n\nWhen the installer finishes, it prints \"Next steps\" with two or three commands that add that folder. Most people get stuck right here: skip them, and every `brew` command fails with \"command not found\". Run exactly what the installer prints. The lines also save the change in `~/.zprofile`, a file each new shell reads when it starts, so open a new terminal tab, then run `brew --version`."),
    ("p0", "d02", ("sections", 2, "body"),
     "Containers are a Linux feature, and macOS is not Linux. So Docker Desktop runs a small Linux virtual machine (VM) in the background. A VM is a computer simulated in software. Your `docker` commands on the Mac talk to the Docker engine inside that VM.",
     "A container is a program that runs in its own walled-off corner of a Linux machine, with its own files. It starts from an image, a packed copy of those files (Day 17 shows both). Containers are built from features of the Linux kernel, the core of the operating system, and macOS has a different kernel. So Docker Desktop runs a small Linux virtual machine (VM) in the background. A VM is a computer simulated in software. Your `docker` commands on the Mac send requests to the Docker engine inside that VM: a background program, or daemon, that starts and stops containers."),
    ("p0", "d02", ("sections", 2, "body"),
     "This creates `/var/run/docker.sock`, the file other programs use to talk to Docker. New installs leave it off, but Terraform's Docker provider on Day 31 looks for it.",
     "This creates `/var/run/docker.sock`, a socket: a special file that other programs open to send requests to the Docker engine. New installs leave it off, but Terraform's Docker provider (the plugin that lets Terraform manage Docker) on Day 31 looks for it at that path."),
    ("p0", "d02", ("sections", 3, "body"),
     "- kubectl: talks to any Kubernetes cluster.\n- kind: creates a small Kubernetes cluster inside Docker containers (\"Kubernetes in Docker\").\n- helm: installs packaged Kubernetes apps, called charts.",
     "- kubectl: sends your commands to a Kubernetes cluster, the group of machines that runs your containers.\n- kind: creates a small Kubernetes cluster inside Docker containers (\"Kubernetes in Docker\"), so you can practise without servers.\n- helm: installs ready-made Kubernetes apps from packages called charts, much as brew installs tools on your Mac."),
    ("p0", "d02", ("sections", 3, "body"),
     "Terraform is the odd one out. After HashiCorp changed Terraform's licence in 2023, Homebrew's main collection stopped updating it. So install it from HashiCorp's own tap: an extra collection of Homebrew packages.",
     "Terraform is the odd one out. Homebrew's main collection only accepts open-source software. In 2023 HashiCorp, the company behind Terraform, moved it to a licence that is not open source. So Homebrew stopped updating its terraform formula (Homebrew's word for a package recipe). Install it from HashiCorp's own tap instead: an extra collection of Homebrew packages, which HashiCorp keeps current."),
    ("p0", "d02", ("sections", 3, "body"),
     "Homebrew keeps versioned JDKs out of your PATH on purpose (it calls them keg-only), so macOS cannot find this one yet. The install prints a `sudo ln -sfn ...` command that links it into `/Library/Java/JavaVirtualMachines`. Run that line, then `java -version` should print 21.",
     "Homebrew keeps versioned JDKs out of your PATH on purpose (it calls them keg-only), so they cannot clash with its main `openjdk`. The `java` command that comes with macOS is only a launcher. It looks for JDKs in `/Library/Java/JavaVirtualMachines` and runs one from there. The install prints a `sudo ln -sfn ...` command that puts a link (a shortcut) to the new JDK in that folder. Run that line, then `java -version` should print 21."),
    ("p0", "d02", ("sections", 3, "body"),
     "You add extensions with `code --install-extension` and an extension ID.",
     "You add extensions with `code --install-extension` and an extension ID. Each extension teaches the editor one kind of file, with colours, error checks and suggestions as you type."),
    ("p0", "d02", ("sections", 4, "body"),
     "Servers, containers and CI runners run Linux with the bash shell and the GNU versions of tools like `sed` and `grep`. Your Mac runs zsh and the BSD versions, which differ in small, annoying ways. A flag that works on your Mac can fail on a server.",
     "Servers, containers and CI runners (the machines that run automated tests) run Linux with the bash shell and the GNU versions of tools like `sed` and `grep`. Your Mac runs zsh and the BSD versions: the same names, written by a different project, with small, annoying differences. For example, `sed -i 's/a/b/' notes.txt` edits a file in place on Linux. The Mac's `sed` reads the word after `-i` as the ending for a backup copy, and fails."),
    ("p0", "d02", ("sections", 4, "body"),
     "Each flag has a job:",
     "Each part has a job:"),
    ("p0", "d02", ("sections", 4, "body"),
     "- `-w /work` starts you in that folder.",
     "- `-w /work` starts you in that folder.\n- `ubuntu:24.04` is the image to start from, and `bash` is the program to run inside it."),
    ("p0", "d02", ("sections", 5, "body"),
     "- `app.py`: the Flask web app.\n- `test_app.py`: three tests for pytest.\n- `requirements.txt`: the packages the app needs to run.\n- `requirements-dev.txt`: those packages plus pytest and ruff (a linter) for development.\n- `.gitignore`: files git should never commit.\n\nYou install packages into a Python virtual environment (venv): a private folder of packages for one project. When you activate it, `python` and `pip` point into that folder, so this project's Flask cannot clash with another project's. You never commit the `.venv` folder, because anyone can rebuild it from the requirements files.",
     "- `app.py`: the web app.\n- `test_app.py`: three tests for the app.\n- `requirements.txt`: the Python packages the app needs to run.\n- `requirements-dev.txt`: those packages plus the tools for development.\n- `.gitignore`: files git should never commit.\n\nYou install packages into a Python virtual environment (venv): a private folder of packages for one project. Activating it puts the venv's `bin` folder first on your PATH, so `python` and `pip` now mean the copies inside it. This project's Flask then cannot clash with another project's. You never commit the `.venv` folder, because anyone can rebuild it from the requirements files.\n\nThe requirements files install six packages:\n\n- Flask: a small Python web framework, which `app.py` uses to answer web requests.\n- gunicorn: a production web server that runs the app inside containers (Day 19).\n- redis: lets the app keep its visit count in Redis, a small, fast database (Day 20).\n- prometheus-client: publishes the app's counters on its `/metrics` page (Day 50).\n- pytest: finds and runs the tests in `test_app.py`.\n- ruff: a linter, which flags style problems and likely bugs (Day 25)."),
    ("p0", "d02", ("sections", 5, "body"),
     "gh also adds the new repo as a remote called origin.",
     "The command also adds the new repo as a remote called origin: a saved name for the GitHub copy, so a later `git push` knows where to send your commits."),
    ("p0", "d02", ("sections", 6, "body"),
     "- \"Cannot connect to the Docker daemon\": open Docker Desktop and wait until it says it is running.",
     "- \"Cannot connect to the Docker daemon\": the engine only runs while Docker Desktop is open, so open it and wait until it says it is running."),
    ("p0", "d02", ("sections", 6, "body"),
     "- \"externally-managed-environment\" from pip: your venv is not active, so run `source .venv/bin/activate`.",
     "- \"externally-managed-environment\" from pip: your venv is not active, so pip tried Homebrew's own Python, which refuses. Run `source .venv/bin/activate`."),
    ("p0", "d02", ("sections", 6, "body"),
     "On Windows, install WSL2 first:",
     "On Windows, install WSL2 (Windows Subsystem for Linux) first:"),
    ("p0", "d02", ("task", "steps", 4),
     "Add VS Code extensions with `code --install-extension`: `ms-azuretools.vscode-containers`, `redhat.vscode-yaml`, `hashicorp.terraform`, `ms-kubernetes-tools.vscode-kubernetes-tools` and `ms-python.python`.",
     "Add VS Code extensions with `code --install-extension`, one per kind of file: `ms-azuretools.vscode-containers` (Dockerfiles and containers), `redhat.vscode-yaml` (YAML), `hashicorp.terraform` (Terraform), `ms-kubernetes-tools.vscode-kubernetes-tools` (Kubernetes) and `ms-python.python` (Python)."),

    # ---------------- Day 8 ----------------
    ("p2", "d08", ("sections", 1, "body"),
     "Each object is named by a hash of its content: a 40-character SHA-1 hash that git usually shortens to 7 characters. The same content gets the same name on every computer.",
     "Each object is named by a hash of its content. A hash function turns any bytes into a short, fixed-length fingerprint. Git uses SHA-1 (Secure Hash Algorithm 1), which gives 40 hex characters, and usually shows only the first 7. The same content gets the same name on every computer."),
    ("p2", "d08", ("sections", 1, "body"),
     "So a file that did not change is the same blob in every commit.",
     "So a file that did not change is the same blob in every commit. When you `git add` a file, git hashes it, and if an object with that name is already in `.git/objects`, there is nothing new to store."),
    ("p2", "d08", ("sections", 2, "body"),
     "A commit you make there belongs to no branch, so run `git switch -c some-name` before you leave, or it will be hard to find again.",
     "A commit you make there belongs to no branch. Git's history views start from HEAD and the branch names, so once you switch away, only the reflog (last section) still leads to it. Run `git switch -c some-name` before you leave."),
    ("p2", "d08", ("sections", 3, "body"),
     "Without it, `git init` still names the first branch `master`.",
     "Without it, `git init` still names the first branch `master`, while GitHub names it `main`."),
    ("p2", "d08", ("sections", 3, "body"),
     "Git opens it for commit messages, merges and rebases. With `code --wait`",
     "Git opens it for commit messages, merges and rebases. Without it, git usually falls back to `vi`, a terminal editor with its own keys. With `code --wait`"),
    ("p2", "d08", ("sections", 4, "body"),
     "- `git add -p` shows your changes one hunk at a time and asks",
     "- `git add -p` shows your changes one hunk (a block of changed lines) at a time and asks"),
    ("p2", "d08", ("sections", 4, "body"),
     "- `git log -p -- price.py` lists every change ever made to one file.",
     "- `git log -p -- price.py` lists every change ever made to one file. The `--` ends the options, so git reads what follows as file names."),
    ("p2", "d08", ("sections", 4, "body"),
     "on your line next year. Most tools assume this shape:",
     "on your line next year. Views such as `git log --oneline` and GitHub's commit list show only its first line, so most tools assume this shape:"),
    ("p2", "d08", ("sections", 4, "body"),
     "When you need a body, run plain `git commit` without `-m`, and git opens your editor.",
     "The imperative matches the messages git writes itself, such as `Revert \"Raise the tax rate to 25%\"`. When you need a body, run plain `git commit` without `-m`, and git opens your editor."),
    ("p2", "d08", ("sections", 5, "body"),
     "A `.gitignore` file lists files that git should act as if it cannot see.",
     "Without an ignore file, `git add .` sweeps up log files, Python's cache folders and the `.env` file that holds your tokens. A `.gitignore` file lists files that git should act as if it cannot see."),
    ("p2", "d08", ("sections", 6, "body"),
     "- `git restore price.py` throws away unstaged edits to a file. Git never stored them, so look at `git diff` first.\n- `git restore --staged price.py` unstages the file and keeps your edit.\n- `git stash` shelves all uncommitted changes and leaves a clean tree.",
     "- `git restore price.py` copies the staged version back over your file, which throws away unstaged edits. Git never stored them, so look at `git diff` first.\n- `git restore --staged price.py` copies the last commit's version into the staging area. The file is unstaged, and your edit stays.\n- `git stash` saves all uncommitted changes in special commits that sit off every branch, and leaves a clean tree."),
    ("p2", "d08", ("sections", 6, "body"),
     "- `git commit --amend` replaces the last commit, to fix its message or add a forgotten file.\n- `git reset --soft HEAD~1` removes the last commit and keeps its changes staged. `--mixed`, the default, keeps them unstaged. `--hard` throws them away too.",
     "- `git commit --amend` replaces the last commit, to fix its message or add a forgotten file. Git writes a new commit with the same parent and moves the branch to it.\n- `git reset --soft HEAD~1` moves your branch back one commit and touches nothing else, so that commit's changes stay staged.\n- `git reset --mixed HEAD~1`, the default, also resets the staging area, so the changes stay only in your files. With `--hard` it resets your files too, and the changes are gone."),
    ("p2", "d08", ("sections", 6, "body"),
     "your teammates have them, and your next push is rejected.",
     "your teammates have them, and your next push is rejected, because the remote branch has commits yours no longer contains."),

    # ---------------- Day 9 ----------------
    ("p2", "d09", ("sections", 0, "body"),
     "Day 8 showed that a branch is a file holding one commit hash.",
     "You branch so a half-done change can live next to main without touching it. Day 8 showed that a branch is a file holding one commit hash."),
    ("p2", "d09", ("sections", 0, "body"),
     "Uncommitted edits come along when you switch, as long as the other branch does not change the same files.",
     "Uncommitted edits come along when you switch, because they live in your working tree and staging area, which belong to no branch. That works as long as the other branch does not change the same files."),
    ("p2", "d09", ("sections", 0, "body"),
     "A tag is a pointer that never moves. Git has two kinds:",
     "A tag is a pointer that never moves, so `v1.0.0` still names the same commit next year, when you need to rebuild or compare that release. Git has two kinds:"),
    ("p2", "d09", ("sections", 1, "body"),
     "A change made on only one side goes in as it is.",
     "A change made on only one side goes in as it is. Say the base has `TAX_RATE = 0.20`, main has `0.25`, and your branch still has `0.20`. Only main changed that line, so git takes `0.25`. Without the base, git would see two different lines and could not tell which side changed."),
    ("p2", "d09", ("sections", 1, "body"),
     "makes a merge commit even when a fast-forward was possible.",
     "makes a merge commit even when a fast-forward was possible, so the history shows where a branch's work came in."),
    ("p2", "d09", ("sections", 1, "body"),
     "It is a safe way to update your `main` from `origin/main`.",
     "It is a safe way to update your `main` from `origin/main`: if your `main` has a stray commit of its own, git stops instead of making a surprise merge."),
    ("p2", "d09", ("sections", 3, "body"),
     "Rebase is the other way to bring your branch up to date with main.",
     "Merging main into your branch every few days works, but each merge adds a commit that says nothing about your work, and the history fills with them. Rebase is the other way to bring your branch up to date with main."),
    ("p2", "d09", ("sections", 3, "body"),
     "Their copies still hold the old commits, so their history and yours no longer match, and someone has to fix it by hand.",
     "Their copies still hold the old commits, so their history and yours no longer match. If a teammate then merges your rebased branch, their history holds each of your changes twice, under old and new IDs. Someone has to clean that up by hand."),
    ("p2", "d09", ("sections", 4, "body"),
     "copies one commit onto the branch you are on, as a new commit. It is the tool for a hotfix that must also land on a release branch, or for saving one good commit from a branch you are about to throw away.",
     "copies one commit onto the branch you are on, as a new commit. Git takes the change that commit made compared with its parent, and applies the same change here. It is the tool for a hotfix (an urgent fix) that must also land on a release branch, which holds an older version you still support. It also saves one good commit from a branch you are about to throw away."),
    ("p2", "d09", ("sections", 5, "body"),
     "which you add as a second remote, usually called `upstream`.",
     "which you add as a second remote, usually called `upstream`. Here the word is a remote's name, a different use from a branch's upstream above."),
    ("p2", "d09", ("sections", 6, "body"),
     "GitHub accepts pushes over HTTPS or SSH. On Day 2, `gh auth login` set up HTTPS and told git to use gh's login, so pushing hello-devops already works. To use SSH instead, reuse your key from Day 7:",
     "GitHub accepts pushes over HTTPS (the encrypted web protocol, Day 11) or SSH (Day 7). On Day 2, `gh auth login` set up HTTPS and told git to use gh's login, so pushing hello-devops already works. SSH is handy on machines without gh, such as a server. To use it, reuse your key from Day 7:"),
    ("p2", "d09", ("sections", 6, "body"),
     "A signed commit carries a signature that only your private key can make, and Git 2.34 and later can sign with the same SSH key:",
     "A signed commit carries a signature that only your private key can make, and anyone with the matching public key can check it. Git 2.34 and later can sign with the same SSH key:"),
    ("p2", "d09", ("sections", 6, "body"),
     "`gpg.format ssh` and `user.signingkey`. The Files section has the commands.",
     "`gpg.format ssh` and `user.signingkey`. The names say gpg because git first signed only with GPG (GNU Privacy Guard), an older tool. The Files section has the commands."),
    ("p2", "d09", ("sections", 6, "body"),
     "3. Upload the public key again, this time as a signing key:",
     "3. Upload the public key again, this time as a signing key, because GitHub keeps login keys and signing keys in separate lists:"),
    ("p2", "d09", ("sections", 6, "body"),
     "GitHub then marks your commits Verified.",
     "GitHub then checks each commit's signature against your signing keys and marks the commit Verified."),
]


def get(obj, path):
    for p in path[:-1]:
        obj = obj[p]
    return obj, path[-1]


def main():
    docs = {}
    applied = skipped = 0
    for part, lid, path, old, new in EDITS:
        if part not in docs:
            f = ROOT / "content" / f"{part}.json"
            docs[part] = (f, json.loads(f.read_text()))
        lesson = next(L for L in docs[part][1]["lessons"] if L["id"] == lid)
        parent, key = get(lesson, path)
        text = parent[key]
        if (new and new in text) or (not new and old not in text):
            skipped += 1
            continue
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{lid} {path}: old text found {n} times: {old[:70]!r}")
        parent[key] = text.replace(old, new)
        applied += 1
    for f, d in docs.values():
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(f"{applied} edits applied, {skipped} already present")


if __name__ == "__main__":
    main()
