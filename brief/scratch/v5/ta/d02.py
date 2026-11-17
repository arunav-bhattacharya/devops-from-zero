"""Book-voice rewrite of d02 (Set up your laptop). Writer: ta. Run from the repo root."""
import json

PATH = "content/p0.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d02")

L["opening"] = """Picture moving into a bigger kitchen the night before the café's first order. The ovens are in, but the flour is still in a box in the hall, the mixer has no plug, and nobody has said which drawer holds the knives. At five in the morning you will reach for something and find nothing there.

Setting up a computer for this work feels the same. It is tempting to rush it, because installing tools feels like the dull part before the real lessons. But many strange errors in week three were planted on day two, by one skipped step.

Last time, we followed one change from the kitchen to the customer and named each step on the road. In this lesson, we'll stock the kitchen. We'll install every tool the course uses, check each one, open a small Linux practice box, and put the first copy of hello-devops online. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "You install a tool with Homebrew, an app that installs other tools, but the terminal says 'command not found'. What is the most likely cause?"
L["guess"]["why"] = "The shell, the program that runs what you type, finds programs by searching the folders listed in PATH. On Apple Silicon, Homebrew lives in /opt/homebrew, and its installer tells you how to add that folder to PATH."

L["terms"] = [
    {"term": "Homebrew", "plain": "A tool for macOS that installs other tools and apps with one command, such as `brew install jq`."},
    {"term": "PATH", "plain": "The list of folders your shell searches, in order, when you type a command name."},
    {"term": "Docker Desktop", "plain": "A Mac app that runs a small, hidden Linux computer in the background so you can run containers."},
    {"term": "Container", "plain": "A program running in its own walled-off corner of a Linux machine, started from a packed copy of its files called an image."},
    {"term": "Virtual environment (venv)", "plain": "A private folder of Python packages (add-on code) for one project, so two projects cannot clash."},
    {"term": "JDK", "plain": "The Java Development Kit: the tools you need to build and run apps written in Java or Kotlin."},
    {"term": "GitHub CLI (gh)", "plain": "A tool you type commands to, which logs you in to GitHub and creates and manages your projects there."},
    {"term": "Remote", "plain": "A saved name for another copy of your git project, such as the copy on GitHub; the usual name is origin."},
]

S = L["sections"]

S[0]["h"] = "A shopping list for the kitchen: what you install today"
S[0]["body"] = """Before a new kitchen opens, someone writes a list: what to buy, and on which day you will first need it. Today is that day for your laptop. It takes longer than other lessons, but you only do it once.

Most of these tools have no window. You use them from the terminal, an app where you type commands instead of clicking. A command is one line of text that tells the computer what to do, such as `brew --version`. Here is the list, with the day each tool first matters:

- Homebrew: the installer for almost everything else (today).
- git and the GitHub CLI (`gh`): git records your code's history, and gh works with GitHub from the terminal (today).
- Python 3.14: runs the app and its tests, and matches the course's Docker image (today).
- jq, tree, watch and htop: small helpers for JSON data, folder trees, repeating a command and watching running programs (Part 1).
- VS Code with a few extensions: a free code editor, plus add-ons that understand the kinds of files this course writes (today).
- Docker Desktop: runs containers (programs walled off inside Linux), such as your Linux practice box (today, and Part 5).
- Multipass: starts a full Ubuntu virtual machine, a whole Linux computer simulated on your Mac (Day 6).
- A JDK 21: builds the Kotlin app in the Gradle part (Day 28).
- terraform: creates servers, networks and other infrastructure from code files (Day 31).
- kubectl, kind and helm: run and manage a practice Kubernetes cluster on your laptop (Part 10).

Many of those names mean nothing yet, and that is fine: each gets its own lesson. GitHub is the website where your code will live online.

After each install, run the tool's version check, such as `git --version`. If it prints a version number, the tool works. If it prints an error, fix it before you go on. Install commands change over time, so if one fails, check the current docs linked in this lesson and follow those.

The first tool on the list installs all the others. Next, we'll install it, and meet the reason many first days go wrong."""

S[1]["h"] = "Homebrew, and why the shell can't find it at first"
S[1]["body"] = """Say you put the new flour in a cupboard by the back door. The next morning you check your usual shelves, one by one, and find no flour. It is in the kitchen. It is just not on any shelf you check.

Homebrew (the `brew` command) is a package manager for macOS. A package manager downloads a tool, puts it in the right folder, and later updates or removes it. You install Homebrew itself with one command from [brew.sh](https://brew.sh/). It asks for your password. It may also install Apple's Command Line Tools, which include git.

On Apple Silicon Macs, Homebrew lives in `/opt/homebrew` and puts its commands in `/opt/homebrew/bin`. Your shell is the program inside the terminal window that runs what you type. When you type `brew`, the shell looks in each folder on a list called your PATH, in order, and runs the first match. The PATH that macOS starts with does not include Homebrew's folder. So, like the flour, `brew` is on your Mac, but the shell cannot find it yet.

When the installer finishes, it prints "Next steps" with two or three commands that add that folder. Skip them, and every `brew` command fails with "command not found". The step is easy to miss, because the installer has just printed a wall of text that looks like success. Run exactly what it prints. The lines also save the change in `~/.zprofile`, a file each new shell reads when it starts. So open a new terminal tab, then run `brew --version`.

**When a tool is installed but "not found", check PATH first.**

Python needs one extra step. Homebrew's default Python is now newer than the one this course uses, so you install `python@3.14`. When you create the project's virtual environment later, you type `python3.14`. Inside it, plain `python` is then the right one.

With Homebrew working, the next install is the biggest one: Docker Desktop."""

S[2]["h"] = "Docker Desktop: a small Linux computer inside your Mac"
S[2]["body"] = """Some breads need a stone oven, and your kitchen only has an electric one. The fix is to put a small stone oven inside your kitchen. Docker Desktop does the same thing for your Mac.

A container is a program that runs in its own walled-off corner of a Linux machine, with its own files. It starts from an image, a packed copy of those files (Day 17 shows both). Containers are built from features of the Linux kernel, the core of the operating system. macOS has a different kernel.

So Docker Desktop runs a small Linux virtual machine (VM) in the background. A VM is a computer simulated in software: the stone oven inside your kitchen. Your `docker` commands on the Mac send requests to the Docker engine inside that VM. The engine is a daemon, a program that runs quietly in the background, and it starts and stops containers.

Install it with `brew install --cask docker-desktop`, or from [Docker's install page](https://docs.docker.com/desktop/setup/install/mac-install/). A cask is Homebrew's name for a Mac app with a window. Docker supports the current and the two previous major macOS versions, so update macOS first if yours is older. Open Docker from Applications once and accept the terms.

Then change one setting. In Settings, Advanced, turn on "Allow the default Docker socket to be used" (it asks for your password). This creates `/var/run/docker.sock`. A socket is a special file that other programs open to send requests to the Docker engine. New installs leave it off. But on Day 31, Terraform's Docker provider (the plugin that lets Terraform manage Docker) looks for it at that path.

Docker Desktop is free for personal use, education and non-commercial open source (software anyone may read, change and share). It is also free for small businesses: fewer than 250 employees and less than $10 million in yearly revenue. Larger companies need a paid plan. Learning on your own laptop counts as personal use. On a work laptop, ask your employer first.

If you can't use Docker Desktop, Colima is a free, open-source alternative that runs the same `docker` commands. OrbStack is another fast option; check its licence before you use it for work.

The big oven is in. Next come the small tools, and one of them comes from an unusual shelf."""

S[3]["h"] = "The small tools, the Kubernetes tools and a JDK"
S[3]["body"] = """Homebrew installs the rest of your tools with one short command per group. The small helpers first:

- jq: reads and filters JSON, a common text format for data. `curl ... | jq .message` pulls one field out of the answer a web app sends back.
- tree: prints a folder and everything in it as a tree.
- watch: reruns a command every two seconds, so you can watch something change.
- htop: a live, colourful list of running programs (processes), with CPU and memory use.

Then the bigger tools for later parts:

- kubectl: sends your commands to a Kubernetes cluster, the group of machines that runs your containers.
- kind: creates a small Kubernetes cluster inside Docker containers ("Kubernetes in Docker"), so you can practise without servers.
- helm: installs ready-made Kubernetes apps from packages called charts, much as brew installs tools on your Mac.
- terraform: creates infrastructure from code files.

Terraform is the odd one out. Homebrew's main collection no longer updates it, so you install it from HashiCorp's tap instead. A tap is an extra collection of Homebrew packages. HashiCorp, the company behind Terraform, keeps its tap current. `brew install hashicorp/tap/terraform` names the tap and the package together.

The Gradle part needs a JDK 21, the toolkit for building Java and Kotlin apps. If you already have one, for example through SDKMAN, keep it and check it with `java -version`. Otherwise, run `brew install openjdk@21`. Homebrew keeps versioned JDKs out of your PATH on purpose, so they cannot clash with its main `openjdk`. It calls them keg-only.

That leaves a gap. The `java` command that comes with macOS is only a launcher. It looks for JDKs in `/Library/Java/JavaVirtualMachines` and runs one from there. The install prints a `sudo ln -sfn ...` command that puts a link (a shortcut) to the new JDK in that folder. The `sudo` at its start runs it with administrator rights, so it asks for your password. Run that line, and `java -version` should print 21. If a newer JDK is also installed, macOS picks the newest; `/usr/libexec/java_home -V` lists them all.

VS Code is a cask too, and the cask also adds the `code` command to your terminal. You add extensions with `code --install-extension` and an extension ID. Each extension teaches the editor one kind of file, with colours, error checks and suggestions as you type.

Everything so far runs on macOS, and servers don't. Next, we'll set up a small piece of real Linux."""

S[4]["h"] = "Your Linux practice box, and why you need one"
S[4]["body"] = """A recipe from another country can use the same words as yours and still mean different amounts. A "cup" in one country is not quite a cup in another. Your Mac and a Linux server have the same problem with their tools.

Servers, containers and CI runners (the machines that run automated tests) run Linux with the bash shell and the GNU versions of tools like `sed` and `grep`. Your Mac runs the zsh shell and the BSD versions. The names match, but a different project wrote them, and they have small, annoying differences. For example, `sed -i 's/a/b/' notes.txt` edits a file in place on Linux. The Mac's `sed` reads the word after `-i` as the ending for a backup copy, and fails.

So Part 1 has you practise inside real Linux. The quickest way is a throwaway container running Ubuntu, a popular version of Linux. One line starts it:

`docker run -it --rm --hostname box -v "$PWD":/work -w /work ubuntu:24.04 bash`

Each part has a job:

- `-it` gives you an interactive terminal.
- `--rm` deletes the container when you exit, so every session starts clean.
- `--hostname box` gives it a short name, which shows up in the prompt.
- `-v "$PWD":/work` shares your current Mac folder into the container at `/work`.
- `-w /work` starts you in that folder.
- `ubuntu:24.04` is the image to start from, and `bash` is the program to run inside it.

Once you are inside, your prompt (the text before the cursor) says `root@box`. Three surprises are normal, and none of them means you did something wrong:

1. You are root, the all-powerful user, because a container starts as root unless you tell it otherwise.
2. The image is minimized, so tools like `less` are missing and `man` pages (the built-in manuals) are stripped out. `apt install` adds what you need.
3. Anything you install is gone after you exit, because `--rm` throws the container away. Files in `/work` survive, because they live on your Mac.

**The box is disposable. Your folder is not.**

One thing a container cannot do is run systemd, the program that starts and looks after services on a real Linux machine. Day 6 needs it, so it uses Multipass to start a small Ubuntu VM instead. Install Multipass today with `brew install --cask multipass` and check it with `multipass version`, or wait until Day 6.

Next, we'll make the first thing you will ship."""

S[5]["h"] = "Your repo, and a private shelf for Python packages"
S[5]["body"] = """The last step creates the project you ship all course. A repo, short for repository, is a project folder that git tracks. Yours starts as five files in `~/code/hello-devops`, given in full below:

- `app.py`: the web app.
- `test_app.py`: three tests for the app.
- `requirements.txt`: the Python packages the app needs to run.
- `requirements-dev.txt`: those packages plus the tools for development.
- `.gitignore`: files git should never commit.

A baker who makes rye and white bread keeps a separate starter jar for each. Share one jar, and the rye ends up in the white loaf. Python projects have the same risk, because two projects may want different versions of the same package.

So you install packages into a Python virtual environment (venv): a private folder of packages for one project. Activating it puts the venv's `bin` folder first on your PATH. Then `python` and `pip` (Python's package installer) mean the copies inside it, and this project's Flask cannot clash with another project's. You never commit the `.venv` folder, because anyone can rebuild it from the requirements files.

The tempting shortcut is `sudo pip` with no venv. Packages from different projects then fight over versions, and Homebrew's Python refuses anyway with "externally-managed-environment". Before any `pip install`, activate the venv and check that your prompt starts with `(.venv)`.

The requirements files install six packages:

- Flask: a small Python web framework, which `app.py` uses to answer web requests.
- gunicorn: a production web server that runs the app inside containers (Day 19).
- redis: lets the app keep its visit count in Redis, a small, fast database (Day 20).
- prometheus-client: publishes the app's counters on its `/metrics` page (Day 50).
- pytest: finds and runs the tests in `test_app.py`.
- ruff: a linter, which flags style problems and likely bugs (Day 25).

Then `gh repo create` makes the GitHub repo and pushes to it in one step. A flag is an extra word that changes what a command does. The flag `--source=.` means "use this folder", and `--push` sends your commits. The command also adds the new repo as a remote called origin. A remote is a saved name for the GitHub copy, so a later `git push` knows where to send your commits.

When something fails, the error message usually names the cause. Next, we'll read the common ones."""

S[6]["h"] = "When something goes wrong"
S[6]["body"] = """Even a well-stocked kitchen has mornings when the oven won't light. The fix is usually small, once you know where to look. When setup fails, it is usually one of these:

- `brew: command not found`: run the installer's "Next steps" lines, then open a new terminal tab.
- "Cannot connect to the Docker daemon": the engine only runs while Docker Desktop is open, so open it and wait until it says it is running.
- `code: command not found`: in VS Code, press Cmd+Shift+P, type "shell command" and run the install command.
- "Unable to locate a Java Runtime": run the `sudo ln -sfn` line that `brew install openjdk@21` printed.
- "externally-managed-environment" from pip: your venv is not active, so pip tried Homebrew's own Python, which refuses. Run `source .venv/bin/activate`.
- `git push` asks for a password: run `gh auth setup-git`, so git uses your gh login.
- `multipass launch` hangs on Day 6: the Multipass README says you may need to turn off the macOS firewall while it starts.

On Windows, install WSL2 (Windows Subsystem for Linux) first: run `wsl --install` in PowerShell as administrator, then restart. It gives you Ubuntu, a Linux system inside Windows. Install Docker Desktop for Windows with the WSL 2 engine, then run this course's commands inside Ubuntu.

On Linux, install Docker Engine and use your package manager for the rest. You are already in Linux, so your practice box is optional.

Once every tool answers its version check, the kitchen is ready, and the real lessons can start."""

L["aside"] = {
    "title": "Why does Terraform come from a different shelf?",
    "after": 3,
    "body": "Homebrew's main collection only accepts open-source software. In 2023 HashiCorp moved Terraform to a licence that is not open source. So Homebrew stopped updating its terraform formula, which is Homebrew's word for a package recipe. HashiCorp's own tap still carries current versions, which is why the course installs it from there.",
}

L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = "A test that passes on one laptop and fails on another often comes down to a different tool version. So some teams hand new engineers one setup script on their first day, which installs the same versions everyone else uses. Python packages are pinned (fixed to exact versions) in requirements files, and the JDK version is pinned in the build, so CI runs the same versions too. Other teams go further with dev containers, where the whole toolbox runs inside a container."

W = L["worked"]["steps"]
W[0]["say"] = "Make a throwaway folder with one file in it, then start the box from there. The first run downloads the `ubuntu:24.04` image, which takes a few seconds. Then your prompt changes: you are now root on a machine called box, in the folder /work."
W[1]["say"] = "Look around. This is real Ubuntu, you are the root user, and the file you made on your Mac is here, because `-v` shared the folder."
W[2]["say"] = "Now the minimized image shows itself. `less` is not installed at all. `man` exists, but its pages were removed to keep the image small."
W[3]["say"] = "Install what you need with apt, Ubuntu's package manager. `apt update` refreshes the list of packages, and `apt install -y` installs without asking you to confirm. The output is long; these are the last lines."
W[4]["say"] = "Write a file from inside Linux, then leave with `exit`. Back on the Mac, the new file is there, because `/work` is your Mac folder."
W[5]["say"] = "Start a new box and look for tree. It is gone. `--rm` deleted the old container, and every new one starts fresh from the image. That is the rule to remember for Part 1: the box is disposable, and your folder is not."

T = L["task"]
T["steps"] = [
    "Install Homebrew with the command from brew.sh. Run the \"Next steps\" lines it prints, open a new terminal tab, and check `brew --version`.",
    "Install git, gh, Python 3.14 and the helpers with `brew install git gh python@3.14 jq tree watch htop`. Check a few with `--version` (use `python3.14 --version`).",
    "Run `gh auth login`. Choose GitHub.com, HTTPS, yes to authenticating git, and logging in with a web browser. Confirm with `gh auth status`.",
    "Install the apps with `brew install --cask docker-desktop visual-studio-code multipass`. Open Docker once, accept the terms, turn on the default Docker socket in Settings, Advanced, then run `docker run --rm hello-world`.",
    "Add VS Code extensions with `code --install-extension`, one per kind of file: `ms-azuretools.vscode-containers` (Dockerfiles and containers), `redhat.vscode-yaml` (YAML), `hashicorp.terraform` (Terraform), `ms-kubernetes-tools.vscode-kubernetes-tools` (Kubernetes) and `ms-python.python` (Python).",
    "Install `kubectl`, `kind`, `helm` and `hashicorp/tap/terraform` with brew, and a JDK 21 (unless you already have one). Check them with `kubectl version --client`, `kind version`, `helm version`, `terraform version` and `java -version`.",
    "Open the practice box once from any folder, run `grep PRETTY /etc/os-release`, and exit.",
    "Create `~/code/hello-devops`, run `git init -b main` inside it, and save the five starter files from this lesson there.",
    "Create and activate a venv with Python 3.14, install `requirements-dev.txt`, and run the tests. Then start the app with `python app.py`, open http://localhost:8000 in your browser, reload a few times, and stop it with Ctrl+C.",
    "If git does not know your name and email yet, set them with `git config --global user.name \"Your Name\"` and `git config --global user.email you@example.com` (Day 8 explains this). Commit the five files, then publish them with `gh repo create hello-devops --public --source=. --push`. Open the repo on GitHub to see them.",
]
T["hints"] = [
    "If a version check fails right after an install, open a new terminal tab and try again.",
    "Before you commit, `git status` should not list `.venv/` or `__pycache__/`. If it does, check the name of your `.gitignore` file.",
    "If `java -version` says it cannot find a Java runtime, scroll up in the `brew install openjdk@21` output for the `sudo ln -sfn` line.",
]

L["explain_back"]["answer"] = "Servers, containers and CI runners run Linux with bash and the GNU tools, while my Mac runs zsh and BSD tools whose options differ. If I practise on Linux, what I learn works the same on a real server. The Ubuntu container starts in a second, and `--rm` throws it away when I exit, so I can break things freely and start clean next time. My files survive because the folder is shared from the Mac with `-v`."

L["recap"] = [
    "Homebrew installs your tools; run its \"Next steps\" so `brew` is on your PATH.",
    "Docker Desktop runs a small Linux VM for containers, and it is free for personal use.",
    "Install Terraform from HashiCorp's tap, and link openjdk@21 so `java -version` finds it.",
    "The ubuntu:24.04 practice box is real Linux and disposable with `--rm`, but it can't run systemd, so Day 6 adds a Multipass VM.",
    "A venv keeps the project's packages private, and `.venv` is never committed.",
    "`gh repo create hello-devops --public --source=. --push` puts your repo on GitHub.",
]

C = L["check"]
C[0]["q"] = "A teammate runs `brew install terraform`, and Homebrew says the formula is disabled. What should they run instead?"
C[0]["why"] = "Homebrew's main collection stopped updating Terraform after the 2023 licence change, so current versions come from HashiCorp's tap."
C[1]["why"] = "Each `docker run` starts a fresh container from the image, and `--rm` deleted the one where you installed jq."
C[2]["why"] = "pytest lives inside `.venv`, and each new terminal starts without the venv active. Run `source .venv/bin/activate` first."

I = L["interview"]
I[0]["a"] = "Pin versions in files that live in the repo, such as requirements files for Python packages and the Gradle wrapper for JVM builds. Install them into an isolated environment, like a venv or a container, never globally. CI uses the same files, so the pipeline builds exactly what laptops build. For command-line tools, keep a setup script or a dev container in the repo, and change versions on purpose through pull requests."
I[1]["a"] = "Containers use features of the Linux kernel to keep processes apart. macOS has a different kernel, so it cannot run Linux containers directly. Docker Desktop, Colima and similar tools start a small Linux VM and run the containers inside it. The `docker` command on the Mac only sends requests to the Docker engine in that VM."

L["deeper"]["body"] = """When you run `brew install jq`, Homebrew does four things:

1. It reads the formula, a small Ruby file that describes the package and its versions.
2. It downloads a bottle, which is a prebuilt, compressed copy of the package for your Mac.
3. It unpacks the bottle into its own folder, such as `/opt/homebrew/Cellar/jq/` plus the version.
4. It links the command into `/opt/homebrew/bin`, a folder that is on your PATH.

That is why two versions can sit side by side in the Cellar while only the linked one runs. Some formulae skip step 4 on purpose, and Homebrew calls them keg-only. Versioned formulae such as `openjdk@21` are keg-only, so they cannot clash with the main `openjdk` formula. That is why it asks you to make the `/Library/Java/JavaVirtualMachines` link yourself. Casks work differently again: they install an app into `/Applications`. A tap is an extra git repository of formulae, which is how `hashicorp/tap` works.

The "Next steps" lines from the Homebrew installer run `brew shellenv`. That command prints `export` lines for PATH and a few other variables, and `eval` runs them in your shell. One of the lines also adds the same `eval` command to the end of `~/.zprofile`, so every new terminal runs it.

Activating a venv is even simpler. The command `source .venv/bin/activate` runs a small script inside your current shell, and the script does three things:

- It sets `VIRTUAL_ENV` to the venv folder.
- It puts `.venv/bin` at the front of PATH.
- It adds `(.venv)` to your prompt.

That is why `which python` points into `.venv` after activation, and why `deactivate` can put PATH back. You can also skip activation and run `.venv/bin/python app.py` directly. The final Dockerfile on Day 22 uses the same PATH trick: it puts a venv's `bin` folder first on PATH.

The shell always runs the first match it finds on PATH. Run `which -a python3` to list every `python3` on your PATH, in the order the shell tries them. When the wrong version of a tool runs, that is the first command I would try."""

L["closing"] = """We started in a new kitchen the night before opening, with the flour in the hall and the knives in an unknown drawer. Now every tool answers its version check, the practice box opens in a second, and the first copy of hello-devops is on GitHub with three passing tests.

One habit is worth keeping from today. Before every `pip install`, look at the start of your prompt. If it does not say `(.venv)`, stop and activate the venv first.

Next, we'll step inside the practice box and learn to find our way around it. The question it answers: how do you move around a computer when there is no mouse, only a line of text?"""

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d02 written")
