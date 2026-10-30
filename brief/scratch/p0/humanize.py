#!/usr/bin/env python3
"""Voice pass for Part 0: rewrite prose fields in place so they read like a person wrote them.

Loads the current content/p0.json, replaces prose fields only, and writes it back.
Ids, titles, code, commands, refs, sources, answers, options and the diagrams are left alone.
Run: python3 brief/scratch/p0/humanize.py
"""
import json
import pathlib

PATH = pathlib.Path(__file__).resolve().parents[3] / "content" / "p0.json"
P = json.loads(PATH.read_text())
L = {lesson["id"]: lesson for lesson in P["lessons"]}


def put_list(target, new):
    """Replace a list of strings, keeping its length."""
    assert len(target) == len(new), (len(target), len(new), new[0][:40])
    target[:] = new


# ---------------------------------------------------------------- part level
P["intro"] = (
    "Part 0 is groundwork. Day 1 gives you a map of DevOps, so when a new tool shows up later, "
    "you already know which job it does. Day 2 sets up your Mac and creates hello-devops, "
    "the small app you ship for the rest of the course."
)

put_list(P["recap"], [
    "In DevOps, the people who build software also share the work of running it.",
    "Every change takes the same path: code, build, test, package, release, deploy, run, observe and feedback.",
    "Each tool in this course owns one part of that path.",
    "Automate what repeats, keep everything as code, ship small changes and get feedback fast.",
    "DORA's five metrics measure speed and stability together, and top teams do well on both.",
    "Homebrew installs your tools, and Docker Desktop runs a small Linux VM for containers.",
    "Your hello-devops repo lives in `~/code/hello-devops` and on GitHub, with passing tests.",
])

P["flashcards"][6]["back"] = "Each one is easy to review, test and undo. When one fails, you know which small change caused it."

P["quiz"][0]["why"] = "Small, frequent changes are easier to test and undo. When one breaks, you only have a small diff to search."
P["quiz"][1]["why"] = "Argo CD watches a git repo and changes the cluster until it matches. That is how it deploys."
P["quiz"][3]["why"] = "Those lines put `/opt/homebrew/bin` on your PATH. Open a new terminal tab after you run them."

# ---------------------------------------------------------------- d01
d = L["d01"]
d["goal"] = ("By the end you can explain what DevOps is, follow one code change from your laptop to users, "
             "and name the tool this course uses for each step.")
d["guess"]["why"] = ("DevOps is a way of working where the people who build software also share the work of running it. "
                     "One new hire can't change how a whole team works.")

S = d["sections"]
S[0]["body"] = """The older way of shipping software splits the work in two. One team writes the code. A separate operations team (ops) installs it on servers and keeps it running. When it breaks at 2 a.m., ops gets the call, but only the developers know the code. Each side blames the other, so releases become rare and scary.

**DevOps** removes that split. It is a way of working where the people who build software also share the work of running it. It has three parts:

- Culture: dev and ops share goals, on-call duty and the review after an outage.
- Practices: small changes, automated tests, automated deploys and watching the live system.
- Tools: the software that makes those practices cheap enough to do every day.

Production is the real system that your users use. In DevOps, your job doesn't end when your code reaches production. This course teaches tools, since those are what you can practice on your laptop. Keep the culture in mind anyway: a new tool on top of the old split changes very little."""

S[1]["body"] = """Every change, big or small, takes the same road to your users. Engineers call this road the **pipeline**. These are its steps, in order:

1. Code: you change code on your laptop and commit it to git.
2. Build: a machine turns the source code into something that can run.
3. Test: automated tests check that the change works and broke nothing else.
4. Package: the app and everything it needs go into one bundle, a container image.
5. Release: the package gets a version number and goes to a shared store, called a registry.
6. Deploy: the new version replaces the old one on the servers.
7. Run: the platform keeps the app alive, restarts it if it crashes and adds copies under load.
8. Observe: graphs, logs and alerts show how the app behaves for real users.
9. Feedback: what you learn shapes the next change, and the loop starts again.

CI/CD covers steps 2 to 6. Continuous integration (CI) means you merge small changes often, and a machine builds and tests each one. Continuous delivery (CD) means every change that passes is ready to release at any time. You build both on Days 9 to 12.

Deciding what to change needs a person. Building, testing and shipping are the same every time, so hand them to a machine."""

S[2]["body"] = """This course picks one main tool for each part of the pipeline. Over the next three weeks you fill in this map:

- Linux and networking (Days 3 and 4): the base that every other tool runs on.
- Docker (Days 5 to 8): packages your app into an image that runs the same everywhere.
- GitHub Actions (Days 9 to 12): builds, tests and releases your app on every push.
- Terraform (Days 13 to 15): creates infrastructure, such as networks and storage, from code.
- Kubernetes (Days 16 to 19): runs many containers across many machines and keeps them healthy.
- Argo CD (Day 20): deploys from git by making the cluster match your repo.
- Prometheus, Grafana and OpenTelemetry (Day 21): collect and show metrics, logs and traces.
- DevSecOps (Day 22): adds security checks at every step.
- Platform engineering, AI in DevOps and your capstone (Day 23): you put all the pieces together.

Infrastructure means the machines, networks and storage your app runs on. A container image is your app plus everything it needs, packed so it runs the same anywhere. You meet both properly later, so a rough idea is enough for today.

Don't try to memorize the list. When a new tool appears, in this course or at work, come back to the map and ask which step it owns."""

S[3]["body"] = """Tools change every few years, but the ideas behind them stay the same. Once you know these four, each new tool makes sense faster:

- Automate what repeats: if you do a task by hand twice, script it the third time.
- Keep everything as code: app, infrastructure, pipelines and settings live as text files in git.
- Ship small changes often: each one is easy to review, test and undo.
- Get feedback fast: tests, deploys and alerts should answer within minutes.

The ideas feed each other. Code that lives in git can be checked by machines. Those automated checks are what make small changes safe. And a small change gives clear feedback, because when it breaks something, you know where to look.

Infrastructure as code (IaC) is the second idea applied to servers and networks. You describe what you want in a file, and a tool such as Terraform creates it. You write your first one on Day 13."""

S[4]["body"] = """To measure how well a team delivers, this course uses the metrics from DORA, a long-running research program that studies software teams. Its [guide to the metrics](https://dora.dev/guides/dora-metrics/) names five measures in two groups.

Throughput shows how fast changes flow:

- Change lead time: the time from a commit to that change running in production.
- Deployment frequency: how often you deploy to production.
- Failed deployment recovery time: how long it takes to recover when a deployment fails.

Instability shows how often changes cause harm:

- Change fail rate: the share of deployments that need immediate action, such as a rollback.
- Deployment rework rate: the share of deployments that are unplanned fixes for a production problem.

Older articles talk about the "four keys" and "time to restore service". DORA now uses five metrics. It added rework rate and renamed recovery time to "failed deployment recovery time".

You might expect fast teams to break more things. DORA found that speed and stability go together, and top teams do well on all five. Just don't turn a metric into a target. A team told to "deploy daily" can hit that number with tiny, pointless deploys. Use the numbers to start a conversation about where work gets stuck."""

S[5]["body"] = """Three job titles grew out of these ideas. They overlap, and companies use them loosely, so read what a job involves before you trust its title:

- DevOps engineer: builds pipelines, infrastructure code and deploy tools with product teams.
- Site reliability engineer (SRE): keeps production reliable, using software to replace manual operations work.
- Platform engineer: builds an internal platform, a set of self-service tools so other teams ship without waiting.

The SRE role started at Google, and Google's engineers wrote [a free book about it](https://sre.google/sre-book/table-of-contents/).

Every day of this course has the same rhythm:

1. Guess an answer before you read. Even a wrong guess makes the answer easier to remember.
2. Read the short sections and study the diagram.
3. Follow the worked example.
4. Do the hands-on task on your own laptop.
5. Explain the idea back in your own words, then take the check.

All course long you ship one small app: hello-devops, a Python web app that says hello and counts visits. You create its repo tomorrow. By Day 23 it is tested, packaged, deployed to Kubernetes and watched on dashboards."""

d["analogy"] = ("A pipeline works like a modern car factory. Each station does one job, such as fitting the engine or testing the brakes. "
                "Robots do the repeatable work, and every station runs checks, so a fault is caught close to where it started. "
                "Sensors in cars already on the road report problems back to the designers, who improve the next model. "
                "The factory picture stops working in one place: a factory builds the same car thousands of times, but every software change is new. "
                "So your tests have to grow with your code.")

W = d["worked"]["steps"]
W[0]["say"] = ("PayFlow is a made-up payments team. Below is one week of their production deploy log. "
               "Each line shows when a change was committed, when it reached production, and how it went.")
W[1]["say"] = ("Start with deployment frequency, because you only have to count lines. "
               "Ten deployments in five working days is two per working day.")
W[2]["say"] = ("For change lead time, subtract the commit time from the deploy time on each line. "
               "Then sort the results and take the middle value, the median. With ten numbers, two sit in the middle, so you average them. "
               "The median stops one slow change from hiding the normal case.")
# Factual fix: the 5th and 6th of the sorted ten values are 4 and 5, so the median is 4.5 hours, not 5.
W[2]["code"] = W[2]["code"].replace("median:              (5 + 5) / 2 = 5 hours",
                                    "median:              (4 + 5) / 2 = 4.5 hours")
W[3]["say"] = ("Change fail rate counts deployments that needed immediate action. "
               "Number 4 was rolled back and number 8 needed a hotfix. That is 2 out of 10, or 20 percent.")
W[4]["say"] = ("For failed deployment recovery time, look at those two failures. Number 4 recovered in 25 minutes. "
               "Number 8 broke at 16:00, and its hotfix landed at 17:35, so 95 minutes. The average is 60 minutes.")
W[5]["say"] = ("Deployment rework rate counts unplanned fixes. Number 9 only happened because number 8 broke production. "
               "That is 1 out of 10, or 10 percent.")
W[6]["say"] = ("Now read the five numbers together. PayFlow deploys often and lead times are short, but one deploy in five fails. "
               "I'd ask two things next: what did deployments 4 and 8 have in common, and why did change 7 wait overnight?")

d["mistake"] = ("A lot of teams treat DevOps as a set of tools to install. They buy a CI server and set up Kubernetes, but keep big quarterly releases. "
                "A separate ops team still gets woken at night for code it never saw. "
                "Start with the habits (small changes, shared ownership, fast feedback), then pick tools that support them.")
d["real_world"] = ("At PayFlow, the made-up payments company from the worked example, one product team owns the checkout service from code to production. "
                   "Their pipeline tests and deploys changes many times a day. When checkout errors rise, the same team is on call. "
                   "A platform team gives every product team shared pipelines, clusters and dashboards, so nobody builds those from scratch.")

d["explain_back"]["answer"] = (
    "DevOps is a way of working where the people who build a service also help run it in production. "
    "A change travels a pipeline: code, build, test, package, release, deploy, run and observe. "
    "We automate as many of those steps as we can. Small, frequent changes keep each step safe and give fast feedback. "
    "To check progress we use DORA metrics, such as change lead time: how long a commit takes to reach production."
)

d["interview"][0]["a"] = (
    "It's a way of working where the team that builds a service also runs it. "
    "That team owns the service from commit to production, including being on call for it. "
    "In practice that means small changes, automated pipelines for build, test and deploy, infrastructure as code and good monitoring. "
    "A company can buy every DevOps tool and still not be doing DevOps if building and running stay with separate teams."
)
d["interview"][1]["a"] = (
    "I'd start with DORA's five metrics. Change lead time, deployment frequency and failed deployment recovery time show throughput. "
    "Change fail rate and deployment rework rate show instability. "
    "I'd track them for one service over time and read them together, because pushing one metric alone invites gaming. "
    "Then I'd pair the numbers with a conversation about where changes wait the longest."
)

d["deeper"]["body"] = """People often mix up DevOps, SRE and platform engineering. DevOps is the broad idea: one team shares building and running software, with automation and fast feedback. It does not prescribe a job title or a tool.

SRE is one concrete way to do it. In [the introduction to Google's SRE book](https://sre.google/sre-book/introduction/), Benjamin Treynor Sloss describes SRE as operations work done by engineers with software skills. Two ideas from that chapter matter for this course:

- The book describes a 50 percent cap on manual operations work for SREs. The rest of their time goes to engineering that removes manual work.
- 100 percent reliability is the wrong target, because users cannot tell 100 percent from 99.999 percent. The gap between the target and perfect becomes an error budget the team can spend on releases. You meet error budgets on Day 21.

Platform engineering answers a scaling problem. When every product team builds its own pipelines and clusters, the work repeats and quality varies. So a platform team builds shared, self-service tools instead. The [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) argues that an internal platform should be run like a product, with the app teams as its users. You see this on Day 23.

DORA's guide also warns about pitfalls teams hit when they adopt the metrics:

- Turning a metric into a goal, which invites people to game it.
- Trusting one metric alone, instead of several that balance each other.
- Comparing very different apps, such as a mobile app and a mainframe system.
- Using the metrics to make teams compete, instead of to improve over time.

My advice: measure one service at a time, watch the trend, and ask the team what slows their changes down."""

# ---------------------------------------------------------------- d02
d = L["d02"]
S = d["sections"]
S[0]["body"] = """Today takes longer than the other days, but you only do it once. This is what you install, and when you first need it:

- Homebrew: the installer for everything else (today).
- git and the GitHub CLI (`gh`): version control and GitHub from the terminal (today).
- Python 3.14: runs the app and its tests, and matches the course's Docker image (today).
- VS Code with four extensions: an editor that understands Dockerfiles, YAML, Terraform and Kubernetes files.
- Docker Desktop: runs containers (Day 5).
- kubectl, kind and helm: Kubernetes tools (Days 16 to 19).
- terraform: creates infrastructure from code (Day 13).
- Optional: k9s, a terminal dashboard for Kubernetes, and jq, a tool for reading JSON.

After each install, run the tool's version check. If it prints a version, the tool works. Install commands change over time, so if one fails, follow the tool's current install page, linked in this lesson."""

S[1]["body"] = """Homebrew (the `brew` command) is a package manager for macOS. A package manager downloads a tool, puts it in the right folder, and later updates or removes it. You install Homebrew itself with one command from [brew.sh](https://brew.sh/). It asks for your password, and it may also install Apple's Command Line Tools, which include git.

On Apple Silicon Macs, Homebrew lives in `/opt/homebrew`. When the installer finishes, it prints "Next steps" with two or three commands. They add Homebrew to your **PATH**: the list of folders your shell searches when you type a command.

Most people get stuck right here. If you skip those commands, every `brew` command fails with "command not found". Run exactly what the installer prints, open a new terminal tab, then run `brew --version`."""

S[2]["body"] = """Containers are a Linux feature, and macOS is not Linux. So Docker Desktop runs a small Linux virtual machine (VM) in the background. A VM is a computer simulated in software. Your `docker` commands talk to the Linux system inside it.

You install it with `brew install --cask docker-desktop`, or from [Docker's install page](https://docs.docker.com/desktop/setup/install/mac-install/). A cask is Homebrew's name for a Mac app with a window. Open Docker from Applications once and accept the terms.

Then change one setting. In Settings, Advanced, turn on "Allow the default Docker socket to be used" (it asks for your password). This creates `/var/run/docker.sock`, the file other programs use to talk to Docker. New versions leave it off, but Terraform's Docker provider on Day 13 looks for it.

Docker Desktop is free for personal use, education and non-commercial open source. It is also free for small businesses (fewer than 250 employees and less than $10 million in yearly revenue). Larger companies need a paid plan. Learning on your own laptop counts as personal use, but on a work laptop, ask your employer first.

If you can't or don't want to use Docker Desktop, two alternatives run the same `docker` commands:

- OrbStack: a fast Mac app, free for personal use and paid for commercial use.
- Colima: free and open source, started from the terminal with `colima start`."""

S[3]["body"] = """Homebrew installs the rest with one short command per tool:

- kubectl: talks to any Kubernetes cluster.
- kind: creates a small Kubernetes cluster inside Docker containers ("Kubernetes in Docker").
- helm: installs packaged Kubernetes apps, called charts.
- terraform: creates infrastructure from code files.

Terraform needs one extra step. In 2023 HashiCorp changed Terraform's licence. Homebrew's main collection then stopped updating it, so the version there is old. Install it from HashiCorp's own tap instead. A tap is an extra collection of Homebrew packages, and `brew install hashicorp/tap/terraform` names the tap and the package together.

VS Code is a cask too, and the cask also adds the `code` command to your terminal. You add extensions with `code --install-extension` and an extension ID. For Dockerfiles and Compose files, use Container Tools from Microsoft, which replaced the older Docker extension."""

S[4]["body"] = """The last part creates the project you ship all course. It starts as five files in `~/code/hello-devops`, given in full below:

- `app.py`: the Flask web app.
- `test_app.py`: three tests for pytest.
- `requirements.txt`: the packages the app needs to run.
- `requirements-dev.txt`: those packages plus pytest and ruff (a linter) for development.
- `.gitignore`: files git should never commit.

You install packages into a Python **virtual environment** (venv): a private folder of packages for one project. When you activate it, `python` and `pip` point into that folder, so this project's Flask cannot clash with another project's. You never commit the `.venv` folder, because anyone can rebuild it from the requirements files.

Then `gh repo create` makes the GitHub repo and pushes to it in one step. The flag `--source=.` means "use this folder", and `--push` sends your commits. The gh tool also adds the new repo as a remote called origin."""

S[5]["body"] = """When setup fails, it is usually one of these:

- `brew: command not found`: run the installer's "Next steps" lines, then open a new terminal tab.
- "Cannot connect to the Docker daemon": open Docker Desktop and wait until it says it is running.
- `code: command not found`: in VS Code, press Cmd+Shift+P, type "shell command" and run the install command.
- "externally-managed-environment" from pip: your venv is not active, so run `source .venv/bin/activate`.
- `git push` asks for a password: run `gh auth setup-git`, so git uses your gh login.
- `gh repo create` says the name exists: delete or rename the old repo on GitHub, or pick another name.

On Windows, install WSL2 first: run `wsl --install` in PowerShell as administrator, then restart. It gives you Ubuntu, a Linux system inside Windows. Install Docker Desktop for Windows, choose the WSL 2 engine, and turn on WSL integration. Then run this course's Linux commands inside Ubuntu.

On Linux, install Docker Engine, and use your package manager or Homebrew on Linux for the rest. Each tool's install page lists the Linux steps."""

d["analogy"] = ("Setting up your laptop is like stocking a new kitchen before you cook. "
                "Homebrew is the delivery service that brings each tool and puts it on the right shelf. "
                "PATH is the list of shelves you check when you reach for something. "
                "If a shelf isn't on the list, you can't find the tool, even though it's in the room. "
                "The comparison fails on upkeep: kitchen knives don't need updates, but your tools do, so run `brew upgrade` now and then.")

W = d["worked"]["steps"]
W[1]["say"] = ("Activate it. Activation puts `.venv/bin` at the front of your PATH, so `python` now means the venv's Python. "
               "Your prompt starts with `(.venv)` to remind you.")
W[2]["say"] = "A fresh venv holds almost nothing, just pip. From now on, only what you install shows up here."
W[4]["say"] = ("Leave with `deactivate`. A venv is disposable: you can delete it and rebuild it from a requirements file at any time, "
               "which is why `.gitignore` lists `.venv/`.")

d["mistake"] = ("Don't install Python packages outside a venv, and never with `sudo pip`. "
                "Packages from different projects then fight over versions, and Homebrew's Python refuses anyway with \"externally-managed-environment\". "
                "Before any `pip install`, activate the project's `.venv` and check that your prompt starts with `(.venv)`.")
d["real_world"] = ("On their first day at PayFlow, a made-up payments company, new engineers run one setup script. "
                   "It installs the same tool versions everyone else uses. "
                   "Python packages are pinned in requirements files, so a test that passes on one laptop also passes on the others and in CI. "
                   "Some teams go further with dev containers, where the whole toolbox runs inside a container.")

d["interview"][0]["a"] = (
    "Pin versions in files that live in the repo, such as requirements files for Python packages. "
    "Install them into an isolated environment, like a venv or a container, never globally. "
    "CI uses the same files, so the pipeline builds exactly what laptops build. "
    "For command-line tools, keep a setup script or a dev container in the repo, and change versions on purpose through pull requests."
)

d["deeper"]["body"] = """When you run `brew install jq`, Homebrew does four things:

1. It reads the formula, a small Ruby file that describes the package and its versions.
2. It downloads a bottle, which is a prebuilt, compressed copy of the package for your Mac.
3. It unpacks the bottle into its own folder, such as `/opt/homebrew/Cellar/jq/` plus the version.
4. It links the command into `/opt/homebrew/bin`, a folder that is on your PATH.

That is why two versions can sit side by side in the Cellar while only the linked one runs. Casks work differently: they install an app into `/Applications`. A tap is an extra git repository of formulae, which is how `hashicorp/tap` works.

The "Next steps" lines from the installer run `brew shellenv`. That command prints `export` lines for PATH and a few other variables, and `eval` runs them in your shell. One of the lines also appends the same `eval` command to `~/.zprofile`, so every new terminal runs it.

Activating a venv is even simpler. The command `source .venv/bin/activate` runs a small script inside your current shell, and the script does three things:

- It sets `VIRTUAL_ENV` to the venv folder.
- It puts `.venv/bin` at the front of PATH.
- It adds `(.venv)` to your prompt.

That is why `which python` points into `.venv` after activation, and why `deactivate` can put PATH back. You can also skip activation and run `.venv/bin/python app.py` directly. The Dockerfile on Day 8 uses the PATH trick instead: it puts the venv's `bin` folder first on PATH.

The shell always runs the first match it finds on PATH. The command `which -a python3` lists every `python3` on your PATH, in the order the shell tries them. When the wrong version of a tool runs, that is the first command I'd try."""

PATH.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
print("wrote", PATH)
