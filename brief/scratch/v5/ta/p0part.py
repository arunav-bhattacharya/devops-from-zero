"""Book-voice rewrite of Part 0's own fields. Writer: ta. Run from the repo root."""
import json

PATH = "content/p0.json"
P = json.load(open(PATH))

P["intro"] = "Before any real tool, you need a map and a stocked kitchen. Day 1 follows one change from a developer's laptop to real users, names each step, and shows which of the 68 lessons teaches it. When a new tool shows up later, you will already know which job it does. Day 2 sets up your Mac, a Linux practice box, and hello-devops, the small app you ship for the rest of the course."

P["recap"] = [
    "In DevOps, the people who build software also share the work of running it.",
    "Every change takes the same road: code, build, test, package, release, deploy, run, observe and feedback.",
    "The 20 parts of this course each own a piece of that road, with Linux and networking underneath.",
    "Automate what repeats, keep everything as code, ship small changes and get feedback fast.",
    "DORA's five metrics measure speed and stability together, and the best teams do well on both.",
    "Homebrew installs your tools, and Docker Desktop runs a small Linux VM for containers.",
    "You practise Linux in a disposable ubuntu:24.04 container, and in a Multipass VM from Day 6.",
    "Your hello-devops repo lives in `~/code/hello-devops` and on GitHub, with passing tests.",
]

F = P["flashcards"]
cards = [
    ("What three things does DevOps combine?", "Culture, practices and tools, so the people who build software also share running it."),
    ("Name the steps a change passes through on its way to users.", "Code, build, test, package, release, deploy, run, observe, feedback."),
    ("Which tool packages the app, and which runs it across many machines?", "Docker packs it into an image. Kubernetes runs the containers across many machines."),
    ("What does Argo CD do?", "It watches a git repo and changes the cluster until it matches what the repo says."),
    ("Which DORA metrics measure throughput, meaning how fast changes flow?", "Change lead time, deployment frequency and failed deployment recovery time."),
    ("Which DORA metrics measure instability, meaning how often changes cause harm?", "Change fail rate and deployment rework rate."),
    ("Why do small, frequent changes lower risk?", "Each one is easy to review, test and undo. When one fails, you know which small change caused it."),
    ("Where do you install Terraform from with Homebrew, and why?", "From HashiCorp's tap (`hashicorp/tap/terraform`), because Homebrew's main collection stopped updating it after the 2023 licence change."),
    ("What do `--rm` and `-v \"$PWD\":/work` do in the practice box command?", "`--rm` deletes the container when you exit. `-v` shares your current Mac folder into it at /work."),
    ("Why does Day 6 use a Multipass VM instead of the container?", "A plain container cannot run systemd, the program that starts and looks after services, which Day 6 teaches."),
    ("What does activating a Python venv change?", "It puts `.venv/bin` first on PATH, so `python` and `pip` use the project's private packages."),
    ("What does `gh repo create hello-devops --public --source=. --push` do?", "It creates the GitHub repo from this folder, adds it as the origin remote, and pushes your commits."),
]
assert len(cards) == len(F)
for f, (front, back) in zip(F, cards):
    f["front"], f["back"] = front, back

whys = [
    "A friendly, visual explanation of what DevOps is and how it compares to SRE.",
    "The official definitions of the five delivery metrics, from the research team itself.",
    "Google's free book on running live systems; read the first part to see where SRE came from.",
    "A short paper, written for no single company, on why companies build internal platforms.",
    "MIT's opening lecture on the shell, and a good warm-up before Part 1.",
    "Explains environment variables, PATH and the settings files your shell reads, which is what makes today's setup work.",
    "What the Homebrew installer needs, and what its 'Next steps' lines really do.",
    "Docker's own install guide for Apple Silicon Macs, with the system requirements.",
    "The Python tutorial chapter on venvs and requirements files, short and clear.",
    "The commands for starting, entering and deleting the Ubuntu VM you use on Day 6.",
]
assert len(whys) == len(P["resources"])
for r, w in zip(P["resources"], whys):
    r["why"] = w

Q = P["quiz"]
Q[0]["q"] = "A team ships one huge release every three months, and each one breaks something. Which idea from Day 1 helps most?"
Q[0]["why"] = "Small, frequent changes are easier to test and undo. When one breaks, there is only a small change to search."
Q[1]["q"] = "Which part of this course teaches the tool that keeps a Kubernetes cluster matching what is in git?"
Q[1]["why"] = "Argo CD deploys by watching a git repo and changing the cluster until it matches."
Q[2]["why"] = "Four out of twenty deployments needed immediate action, and 4 divided by 20 is 20 percent."
Q[3]["why"] = "Those lines put `/opt/homebrew/bin` on your PATH. Open a new terminal tab after you run them."
Q[4]["q"] = "You try `systemctl status ssh` in the ubuntu:24.04 practice box, and it fails. What is the fix?"
Q[4]["why"] = "A plain container does not start systemd as its first program, so systemctl cannot work there. A full VM does start it."
Q[5]["why"] = "The venv is large and built for one machine, so `.gitignore` keeps it out of git. Anyone can rebuild it from the requirements files."

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("p0 part fields written")
