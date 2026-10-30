#!/usr/bin/env python3
"""Build content/p0.json (Part 0: Start here, lessons d01 and d02).

Run: python3 brief/scratch/p0/build_p0.py
The d02 starter files are read from labs/hello-devops so they always match the lab.
"""
import json
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[3]
LAB = ROOT / "labs" / "hello-devops"
OUT = ROOT / "content" / "p0.json"


def T(s):
    """Dedent a triple-quoted block and trim blank lines at both ends."""
    return textwrap.dedent(s).strip("\n")


def lab(name):
    return (LAB / name).read_text()


# ---------------------------------------------------------------- links
L = {
    "aws_devops": {"title": "What is DevOps? (AWS)", "url": "https://aws.amazon.com/devops/what-is-devops/", "kind": "read"},
    "nana_devops": {"title": "What is DevOps? REALLY understand it (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=0yWAtQ6wYNM", "kind": "watch"},
    "fowler_ci": {"title": "Continuous Integration (Martin Fowler)", "url": "https://martinfowler.com/articles/continuousIntegration.html", "kind": "read"},
    "fowler_delivery": {"title": "Software Delivery Guide (Martin Fowler)", "url": "https://martinfowler.com/delivery.html", "kind": "read"},
    "fowler_freq": {"title": "Frequency Reduces Difficulty (Martin Fowler)", "url": "https://martinfowler.com/bliki/FrequencyReducesDifficulty.html", "kind": "read"},
    "dora_small": {"title": "Working in small batches (DORA)", "url": "https://dora.dev/capabilities/working-in-small-batches/", "kind": "read"},
    "dora_metrics": {"title": "DORA's software delivery performance metrics", "url": "https://dora.dev/guides/dora-metrics/", "kind": "docs"},
    "dora_history": {"title": "A history of DORA's software delivery metrics", "url": "https://dora.dev/insights/dora-metrics-history/", "kind": "read"},
    "sre_intro": {"title": "Site Reliability Engineering, Introduction (Google SRE book)", "url": "https://sre.google/sre-book/introduction/", "kind": "read"},
    "cncf_platforms": {"title": "CNCF Platforms White Paper", "url": "https://tag-app-delivery.cncf.io/whitepapers/platforms/", "kind": "read"},
    "brew": {"title": "Homebrew", "url": "https://brew.sh/", "kind": "docs"},
    "brew_install": {"title": "Homebrew installation docs", "url": "https://docs.brew.sh/Installation", "kind": "docs"},
    "docker_mac": {"title": "Install Docker Desktop on Mac", "url": "https://docs.docker.com/desktop/setup/install/mac-install/", "kind": "docs"},
    "docker_license": {"title": "Docker Desktop license agreement", "url": "https://docs.docker.com/subscription-billing/desktop-license/", "kind": "docs"},
    "orbstack": {"title": "OrbStack", "url": "https://orbstack.dev/", "kind": "docs"},
    "tf_install": {"title": "Install Terraform (HashiCorp)", "url": "https://developer.hashicorp.com/terraform/install", "kind": "docs"},
    "kubectl_mac": {"title": "Install and set up kubectl on macOS", "url": "https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/", "kind": "docs"},
    "kind_quick": {"title": "kind quick start", "url": "https://kind.sigs.k8s.io/docs/user/quick-start/", "kind": "docs"},
    "py_venv": {"title": "Virtual environments and packages (Python tutorial)", "url": "https://docs.python.org/3/tutorial/venv.html", "kind": "docs"},
    "gh_repo_create": {"title": "gh repo create (GitHub CLI manual)", "url": "https://cli.github.com/manual/gh_repo_create", "kind": "docs"},
    "wsl": {"title": "Install WSL (Microsoft Learn)", "url": "https://learn.microsoft.com/en-us/windows/wsl/install", "kind": "docs"},
    "vscode_mac": {"title": "Visual Studio Code on macOS", "url": "https://code.visualstudio.com/docs/setup/mac", "kind": "docs"},
}


def refs(*keys):
    return [L[k] for k in keys]


def src(*keys):
    return [{"title": L[k]["title"], "url": L[k]["url"]} for k in keys]


# ---------------------------------------------------------------- d01
D01_SVG = (
    '<svg viewBox="0 0 560 276" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="A change flows from Git through GitHub Actions, Docker and Argo CD to Kubernetes and users, '
    'while Terraform creates the infrastructure and Prometheus watches and feeds back to the next change">'
    # row 1
    '<rect x="28" y="16" width="160" height="52" rx="10" class="bx"/>'
    '<text x="108" y="38" font-size="13" text-anchor="middle" class="t">Code</text>'
    '<text x="108" y="56" font-size="11" text-anchor="middle" class="ts">Git</text>'
    '<rect x="208" y="16" width="160" height="52" rx="10" class="bxo"/>'
    '<text x="288" y="38" font-size="13" text-anchor="middle" class="tk">Build and test</text>'
    '<text x="288" y="56" font-size="11" text-anchor="middle" class="tk">GitHub Actions</text>'
    '<rect x="388" y="16" width="160" height="52" rx="10" class="bxt"/>'
    '<text x="468" y="38" font-size="13" text-anchor="middle" class="tk">Package</text>'
    '<text x="468" y="56" font-size="11" text-anchor="middle" class="tk">Docker</text>'
    # row 2
    '<rect x="388" y="112" width="160" height="52" rx="10" class="bxp"/>'
    '<text x="468" y="134" font-size="13" text-anchor="middle" class="tk">Deploy</text>'
    '<text x="468" y="152" font-size="11" text-anchor="middle" class="tk">Argo CD</text>'
    '<rect x="208" y="112" width="160" height="52" rx="10" class="bxg"/>'
    '<text x="288" y="134" font-size="13" text-anchor="middle" class="tk">Run</text>'
    '<text x="288" y="152" font-size="11" text-anchor="middle" class="tk">Kubernetes</text>'
    '<text x="108" y="142" font-size="13" text-anchor="middle" class="t">Users</text>'
    # row 3
    '<rect x="208" y="208" width="160" height="52" rx="10" class="bx"/>'
    '<text x="288" y="230" font-size="13" text-anchor="middle" class="t">Infrastructure</text>'
    '<text x="288" y="248" font-size="11" text-anchor="middle" class="ts">Terraform</text>'
    '<rect x="28" y="208" width="160" height="52" rx="10" class="bxo"/>'
    '<text x="108" y="230" font-size="13" text-anchor="middle" class="tk">Observe</text>'
    '<text x="108" y="248" font-size="11" text-anchor="middle" class="tk">Prometheus</text>'
    # arrows
    '<line x1="188" y1="42" x2="206" y2="42" class="ln" marker-end="url(#ar)"/>'
    '<line x1="368" y1="42" x2="386" y2="42" class="ln" marker-end="url(#ar)"/>'
    '<line x1="468" y1="68" x2="468" y2="110" class="ln" marker-end="url(#ar)"/>'
    '<line x1="388" y1="138" x2="370" y2="138" class="ln" marker-end="url(#ar)"/>'
    '<line x1="208" y1="138" x2="140" y2="138" class="ln" marker-end="url(#ar)"/>'
    '<line x1="288" y1="208" x2="288" y2="166" class="ln" marker-end="url(#ar)"/>'
    '<text x="298" y="191" font-size="11" text-anchor="start" class="ts">creates</text>'
    '<line x1="240" y1="164" x2="178" y2="206" class="lnd" marker-end="url(#ar)"/>'
    # feedback loop back to Code
    '<line x1="28" y1="234" x2="14" y2="234" class="lnd"/>'
    '<line x1="14" y1="234" x2="14" y2="42" class="lnd"/>'
    '<line x1="14" y1="42" x2="26" y2="42" class="lnd" marker-end="url(#ar)"/>'
    '<text x="22" y="100" font-size="11" text-anchor="start" class="ts">feedback</text>'
    '</svg>'
)

d01 = {
    "id": "d01",
    "title": "The DevOps map",
    "minutes": 35,
    "goal": "By the end you can explain what DevOps is, trace one code change from your laptop to users, and name the tool this course uses for each step.",
    "guess": {
        "q": "A company hires one 'DevOps engineer' and changes nothing else. Has it adopted DevOps?",
        "options": [
            "Yes, because DevOps is a job title",
            "Yes, if that person buys the right tools",
            "No, DevOps is how teams share running software",
            "No, DevOps only applies to cloud companies",
        ],
        "answer": 2,
        "why": "DevOps is first a way of working: the people who build software also share the work of running it. One new hire cannot change how a whole team works.",
    },
    "terms": [
        {"term": "DevOps", "plain": "A way of working where the people who build software also share the job of running it."},
        {"term": "Production", "plain": "The real, live system that your users use."},
        {"term": "Pipeline", "plain": "The automated series of steps that takes a code change from a commit to production."},
        {"term": "Continuous integration (CI)", "plain": "Merging small changes into the main branch often, with an automatic build and test for each one."},
        {"term": "Continuous delivery (CD)", "plain": "Keeping every change that passes the tests ready to release at any time."},
        {"term": "Infrastructure as code (IaC)", "plain": "Describing servers, networks and storage in text files that a tool can create for you."},
        {"term": "DORA metrics", "plain": "Five measures from the DORA research program that show how fast and how safely a team delivers software."},
    ],
    "sections": [
        {
            "h": "What DevOps is",
            "body": T("""
                Picture an older way of shipping software. One team writes the code. A separate operations team (ops) installs it on servers and keeps it running. When it breaks at 2 a.m., ops gets the call, but only the developers know the code. Each side blames the other, so releases become rare and scary.

                **DevOps** is the fix for that split. It is a way of working where the people who build software also share the work of running it. It has three parts:

                - Culture: dev and ops share goals, on-call duty and the review after an outage.
                - Practices: small changes, automated tests, automated deploys and watching the live system.
                - Tools: the software that makes those practices cheap enough to do every day.

                Production means the real system that your users use. In DevOps, your job continues after your code reaches production. This course teaches tools, but keep the culture in mind. A tool without the habits around it changes very little.
            """),
            "refs": refs("aws_devops", "nana_devops"),
        },
        {
            "h": "The path of one change",
            "body": T("""
                Every change takes the same road to your users. Engineers call this road the **pipeline**. Here are its steps, in order:

                1. Code: you change code on your laptop and commit it to git.
                2. Build: a machine turns the source code into something that can run.
                3. Test: automated tests check that the change works and broke nothing else.
                4. Package: the app and everything it needs go into one bundle, a container image.
                5. Release: the package gets a version number and goes to a shared store, called a registry.
                6. Deploy: the new version replaces the old one on the servers.
                7. Run: the platform keeps the app alive, restarts it if it crashes and adds copies under load.
                8. Observe: graphs, logs and alerts show how the app behaves for real users.
                9. Feedback: what you learn shapes the next change, and the loop starts again.

                Steps 2 to 6 are where CI/CD lives. Continuous integration (CI) means you merge small changes often, and a machine builds and tests each one. Continuous delivery (CD) means every change that passes is ready to release at any time. You build both on Days 9 to 12.

                A person decides what to change. Machines should do the repeatable work of building, testing and shipping it.
            """),
            "refs": refs("fowler_ci"),
        },
        {
            "h": "Where each tool sits",
            "body": T("""
                This course gives each part of the pipeline one main tool. Here is the map you fill in over the next three weeks:

                - Linux and networking (Days 3 and 4): the base that every other tool runs on.
                - Docker (Days 5 to 8): packages your app into an image that runs the same everywhere.
                - GitHub Actions (Days 9 to 12): builds, tests and releases your app on every push.
                - Terraform (Days 13 to 15): creates infrastructure, such as networks and storage, from code.
                - Kubernetes (Days 16 to 19): runs many containers across many machines and keeps them healthy.
                - Argo CD (Day 20): deploys from git by making the cluster match your repo.
                - Prometheus, Grafana and OpenTelemetry (Day 21): collect and show metrics, logs and traces.
                - DevSecOps (Day 22): adds security checks at every step.
                - Platform engineering, AI in DevOps and your capstone (Day 23): tie it all together.

                Infrastructure means the machines, networks and storage your app runs on. A container image is your app plus everything it needs, packed so it runs the same anywhere. You meet both properly later, so a rough idea is enough today.

                You do not need to remember this list. When a new tool appears, come back to this map and ask one question: which step does it own?
            """),
            "refs": refs("fowler_delivery"),
        },
        {
            "h": "Four ideas behind every tool",
            "body": T("""
                Tools change every few years. The ideas behind them stay the same. Learn these four, and each new tool makes sense faster:

                - Automate what repeats: if you do a task by hand twice, script it the third time.
                - Keep everything as code: app, infrastructure, pipelines and settings live as text files in git.
                - Ship small changes often: each one is easy to review, test and undo.
                - Get feedback fast: tests, deploys and alerts should answer within minutes.

                Each idea makes the others easier. Code in git can be checked by machines. Automated checks make small changes safe. Small changes give clear feedback, because when one breaks something, you know where to look.

                Infrastructure as code (IaC) is the second idea applied to servers and networks. You describe what you want in a file, and a tool such as Terraform creates it. Watch for these four ideas in every lesson.
            """),
            "refs": refs("dora_small", "fowler_freq"),
        },
        {
            "h": "Measuring delivery: the DORA metrics",
            "body": T("""
                How do you know if a team delivers well? DORA is a long-running research program that studies how software teams deliver. Its [guide to the metrics](https://dora.dev/guides/dora-metrics/) names five measures in two groups.

                Throughput shows how fast changes flow:

                - Change lead time: the time from a commit to that change running in production.
                - Deployment frequency: how often you deploy to production.
                - Failed deployment recovery time: how long it takes to recover when a deployment fails.

                Instability shows how often changes cause harm:

                - Change fail rate: the share of deployments that need immediate action, such as a rollback.
                - Deployment rework rate: the share of deployments that are unplanned fixes for a production problem.

                Older articles talk about the "four keys" and "time to restore service". Today DORA uses five metrics. It added rework rate and now calls recovery time "failed deployment recovery time".

                The key finding is that speed and stability go together. Top teams do well on all five. One warning: do not turn a metric into a target. A team told to "deploy daily" can game it with tiny, pointless deploys. Use the numbers to start a conversation about where work gets stuck.
            """),
            "refs": refs("dora_metrics", "dora_history"),
        },
        {
            "h": "Roles, and how this course works",
            "body": T("""
                Three job titles grew out of these ideas. They overlap, and companies use them loosely:

                - DevOps engineer: builds pipelines, infrastructure code and deploy tools with product teams.
                - Site reliability engineer (SRE): keeps production reliable, using software to replace manual operations work.
                - Platform engineer: builds an internal platform, a set of self-service tools so other teams ship without waiting.

                The SRE role started at Google, and Google wrote a free book about it. Each day of this course follows the same rhythm:

                1. Guess an answer before you read. A guess, even a wrong one, makes the answer easier to remember.
                2. Read the short sections and study the diagram.
                3. Follow the worked example.
                4. Do the hands-on task on your own laptop.
                5. Explain the idea back in your own words, then take the check.

                You ship one small app all course: hello-devops, a Python web app that says hello and counts visits. Tomorrow you create its repo. By Day 23 it is tested, packaged, deployed to Kubernetes and watched on dashboards.
            """),
            "refs": refs("sre_intro", "cncf_platforms"),
        },
    ],
    "analogy": T("""
        The pipeline is like a modern car factory. Each station does one job: one fits the engine, one paints, one tests the brakes. Robots do the repeatable work, and checks happen at every station, so a fault is caught close to where it started. Sensors in cars already on the road report problems back to the designers, who improve the next model. The analogy breaks because a factory builds the same car thousands of times, while every software change is new, so your tests must grow with your code.
    """),
    "diagram": D01_SVG,
    "diagram_caption": "One change flows from Git to users. Terraform creates what it runs on, and what you observe feeds the next change.",
    "worked": {
        "title": "Compute the DORA metrics for one week",
        "steps": [
            {
                "say": "Meet PayFlow, a made-up payments team. This is their production deploy log for one week. Each line shows when a change was committed, when it reached production, and what happened.",
                "code": T("""
                    #   committed   deployed    result
                    1   Mon 09:00   Mon 11:00   ok
                    2   Mon 13:00   Mon 16:00   ok
                    3   Tue 10:00   Tue 13:00   ok
                    4   Tue 14:00   Tue 18:00   failed, rolled back after 25 min
                    5   Wed 09:00   Wed 14:00   ok
                    6   Wed 10:00   Wed 15:00   ok
                    7   Wed 15:00   Thu 09:00   ok
                    8   Thu 10:00   Thu 16:00   failed, needed a hotfix
                    9   Thu 16:30   Thu 17:35   ok (unplanned hotfix for #8)
                    10  Fri 08:00   Fri 14:00   ok
                """),
                "lang": "text",
            },
            {
                "say": "Deployment frequency is the easiest: count the lines. Ten deployments in five working days is two per working day.",
            },
            {
                "say": "Change lead time: subtract the commit time from the deploy time for each line. Then sort the numbers and take the middle one (the median), so one slow change does not hide the normal case.",
                "code": T("""
                    lead times in hours: 2, 3, 3, 4, 5, 5, 18, 6, 1, 6
                    sorted:              1, 2, 3, 3, 4, 5, 5, 6, 6, 18
                    median:              (5 + 5) / 2 = 5 hours
                """),
                "lang": "text",
            },
            {
                "say": "Change fail rate: deployments 4 and 8 needed immediate action, a rollback and a hotfix. That is 2 out of 10, so 20 percent.",
            },
            {
                "say": "Failed deployment recovery time: deployment 4 recovered in 25 minutes. Deployment 8 broke at 16:00 and the hotfix landed at 17:35, so 95 minutes. The average is 60 minutes.",
            },
            {
                "say": "Deployment rework rate: deployment 9 was unplanned and only happened because of a production problem. That is 1 out of 10, so 10 percent.",
            },
            {
                "say": "Now read the five numbers together. PayFlow deploys often with short lead times, but one deploy in five fails. The next questions are what deployments 4 and 8 had in common, and why change 7 waited overnight.",
            },
        ],
    },
    "code": [],
    "commands": [],
    "mistake": T("""
        The most common mistake is treating DevOps as a set of tools to install. A team buys a CI server and sets up Kubernetes, but keeps big quarterly releases and a separate ops team that gets paged for code it never saw. Start with the habits (small changes, shared ownership, fast feedback), then pick tools that support them.
    """),
    "real_world": T("""
        At a payments company like PayFlow, one product team owns its checkout service from code to production. The pipeline tests and deploys their changes many times a day, and the same team is on call when checkout errors rise. A platform team gives every product team the shared pipelines, clusters and dashboards, so nobody builds them from scratch.
    """),
    "task": {
        "title": "Map your own delivery path",
        "steps": [
            "Pick one service you worked on at your current or last job, or a side project.",
            "On paper, write every step a change takes from your commit to real users, in order.",
            "Mark each step as manual (a person does it) or automated (a machine does it).",
            "Next to each step, write the tool used, if any, and the matching step name from today's map.",
            "Estimate the five DORA metrics for that service. Rough guesses are fine.",
            "Circle the one step you would automate first, and write one sentence on why.",
        ],
        "hints": [
            "To estimate lead time, think of your last change: when was it committed, and when did users get it?",
            "Waiting counts too: a change that waits two days for review adds two days of lead time.",
        ],
        "done_when": "You are done when you have one page with every step marked manual or automated, a tool for each, and a guess for all five DORA metrics.",
    },
    "explain_back": {
        "prompt": "Explain DevOps to a backend friend in 3 to 4 sentences. Mention shared ownership, the pipeline and one DORA metric.",
        "answer": T("""
            DevOps is a way of working where the people who build a service also help run it in production. A change travels a pipeline: code, build, test, package, release, deploy, run and observe, and we automate as many steps as we can. Small, frequent changes keep each step safe and give fast feedback. We check our progress with DORA metrics, such as change lead time: how long a commit takes to reach production.
        """),
    },
    "recap": [
        "DevOps is culture, practices and tools that let the people who build software also share running it.",
        "A change flows through code, build, test, package, release, deploy, run, observe and feedback.",
        "Each step gets a tool: Git, GitHub Actions, Docker, Terraform, Kubernetes, Argo CD, Prometheus and Grafana.",
        "Four ideas drive it all: automate repeats, everything as code, small changes, fast feedback.",
        "DORA's five metrics measure throughput and instability, and top teams do well on both.",
    ],
    "check": [
        {
            "q": "Your team has a script that builds the app and runs the tests, but someone runs it by hand once a week. What is the best next step?",
            "options": ["Keep the script in git", "Run it on every push", "Write more unit tests", "Hire a release manager"],
            "answer": 1,
            "why": "Running the checks on every push gives fast feedback, which a weekly manual run cannot.",
        },
        {
            "q": "A team creates its cloud network and database by clicking in a web console. Which tool from this course turns that into code?",
            "options": ["Docker", "Argo CD", "Terraform", "Prometheus"],
            "answer": 2,
            "why": "Terraform creates infrastructure, such as networks and databases, from code files.",
        },
        {
            "q": "A team deployed 40 times last month. Six of those deployments broke something and were rolled back at once. What is their change fail rate?",
            "options": ["5 percent", "20 percent", "40 percent", "15 percent"],
            "answer": 3,
            "why": "Six out of forty deployments needed immediate action, and 6 divided by 40 is 15 percent.",
        },
    ],
    "interview": [
        {
            "q": "What is DevOps, in your own words?",
            "a": "DevOps is a way of working that joins building software and running it. The same team owns a service from commit to production, including being on call for it. In practice that means small changes, automated build, test and deploy pipelines, infrastructure as code and good monitoring. Tools support it, but the core is shared ownership and fast feedback.",
        },
        {
            "q": "How would you measure whether a team's software delivery is improving?",
            "a": "I would start with DORA's five metrics. Change lead time, deployment frequency and failed deployment recovery time show throughput, and change fail rate and deployment rework rate show instability. I would track them for one service over time and read them together, because pushing one metric alone invites gaming. Then I would pair the numbers with a conversation about where changes wait the longest.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": T("""
            DevOps, SRE and platform engineering often get mixed up. Here is how they relate, using their own sources.

            DevOps is the broad idea: one team shares building and running software, with automation and fast feedback. It does not prescribe a job title or a tool.

            SRE is one concrete way to do it. In [the introduction to Google's SRE book](https://sre.google/sre-book/introduction/), Benjamin Treynor Sloss describes SRE as operations work done by engineers with software skills. Two ideas from that chapter matter for this course:

            - The book describes a 50 percent cap on manual operations work for SREs. The rest of their time goes to engineering that removes manual work.
            - 100 percent reliability is the wrong target, because users cannot tell 100 percent from 99.999 percent. The gap between the target and perfect becomes an error budget the team can spend on releases. You meet error budgets on Day 21.

            Platform engineering answers a scaling problem. When every product team builds its own pipelines and clusters, the work repeats and quality varies. A platform team builds shared, self-service tools instead. The [CNCF platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) argues that an internal platform should be run like a product, with the app teams as its users. You see this on Day 23.

            Finally, DORA's guide warns about common pitfalls when teams adopt the metrics:

            - Turning a metric into a goal, which invites people to game it.
            - Trusting one metric alone, instead of several that balance each other.
            - Comparing very different apps, such as a mobile app and a mainframe system.
            - Using the metrics to make teams compete, instead of to improve over time.

            A good habit is to measure one service at a time, watch the trend, and ask what slows changes down. The numbers point to questions. People find the answers.
        """),
    },
    "sources": src("dora_metrics", "sre_intro", "cncf_platforms", "aws_devops"),
}

# ---------------------------------------------------------------- d02
D02_SVG = (
    '<svg viewBox="0 0 560 236" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="From the terminal, git and gh talk to GitHub, docker and kind talk to the Linux VM in Docker Desktop, '
    'and kubectl and helm talk to the kind cluster that runs inside that VM">'
    '<rect x="8" y="96" width="112" height="44" rx="10" class="bx"/>'
    '<text x="64" y="114" font-size="13" text-anchor="middle" class="t">Terminal</text>'
    '<text x="64" y="131" font-size="11" text-anchor="middle" class="ts">zsh</text>'
    # middle column: tools
    '<rect x="160" y="16" width="152" height="44" rx="10" class="bxo"/>'
    '<text x="236" y="43" font-size="13" text-anchor="middle" class="tk">git, gh</text>'
    '<rect x="160" y="96" width="152" height="44" rx="10" class="bxt"/>'
    '<text x="236" y="123" font-size="13" text-anchor="middle" class="tk">docker, kind</text>'
    '<rect x="160" y="176" width="152" height="44" rx="10" class="bxp"/>'
    '<text x="236" y="203" font-size="13" text-anchor="middle" class="tk">kubectl, helm</text>'
    # right column: what they talk to
    '<rect x="352" y="16" width="196" height="44" rx="10" class="bx"/>'
    '<text x="450" y="34" font-size="13" text-anchor="middle" class="t">GitHub</text>'
    '<text x="450" y="51" font-size="11" text-anchor="middle" class="ts">hello-devops repo</text>'
    '<rect x="352" y="96" width="196" height="44" rx="10" class="bx"/>'
    '<text x="450" y="114" font-size="13" text-anchor="middle" class="t">Linux VM</text>'
    '<text x="450" y="131" font-size="11" text-anchor="middle" class="ts">Docker Desktop</text>'
    '<rect x="352" y="176" width="196" height="44" rx="10" class="bx"/>'
    '<text x="450" y="194" font-size="13" text-anchor="middle" class="t">kind cluster</text>'
    '<text x="450" y="211" font-size="11" text-anchor="middle" class="ts">nodes are containers</text>'
    # arrows
    '<line x1="120" y1="108" x2="158" y2="46" class="ln" marker-end="url(#ar)"/>'
    '<line x1="120" y1="118" x2="158" y2="118" class="ln" marker-end="url(#ar)"/>'
    '<line x1="120" y1="128" x2="158" y2="190" class="ln" marker-end="url(#ar)"/>'
    '<line x1="312" y1="38" x2="350" y2="38" class="ln" marker-end="url(#ar)"/>'
    '<line x1="312" y1="118" x2="350" y2="118" class="ln" marker-end="url(#ar)"/>'
    '<line x1="312" y1="198" x2="350" y2="198" class="ln" marker-end="url(#ar)"/>'
    '<line x1="450" y1="140" x2="450" y2="174" class="lnd" marker-end="url(#ar)"/>'
    '<text x="458" y="161" font-size="11" text-anchor="start" class="ts">runs</text>'
    '</svg>'
)

d02 = {
    "id": "d02",
    "title": "Set up your laptop",
    "minutes": 45,
    "goal": "By the end you can install and check every tool this course uses, and push a tested hello-devops repo to your GitHub account.",
    "guess": {
        "q": "You install a tool with Homebrew, but the terminal says 'command not found'. What is the most likely cause?",
        "options": [
            "The download was corrupted",
            "The tool needs a Mac restart",
            "PATH does not include Homebrew's folder",
            "The tool only works on Intel Macs",
        ],
        "answer": 2,
        "why": "The shell finds programs by searching the folders listed in PATH. On Apple Silicon, Homebrew lives in /opt/homebrew, and its installer tells you how to add that folder to PATH.",
    },
    "terms": [
        {"term": "Homebrew", "plain": "A package manager for macOS that installs command-line tools and apps with one command, such as `brew install jq`."},
        {"term": "PATH", "plain": "The list of folders your shell searches, in order, when you type a command name."},
        {"term": "Docker Desktop", "plain": "A Mac app that runs a small Linux machine in the background so you can run containers."},
        {"term": "Virtual environment (venv)", "plain": "A private folder of Python packages for one project, so projects cannot clash."},
        {"term": "GitHub CLI (gh)", "plain": "A command-line tool for GitHub that logs you in, creates repos and opens pull requests."},
        {"term": "Remote", "plain": "A named link from your local git repo to a copy on a server; the usual name is origin."},
    ],
    "sections": [
        {
            "h": "What you install today, and why",
            "body": T("""
                Today is setup day. It takes longer than other days, but you only do it once. Here is what you install, and when you first need it:

                - Homebrew: the installer for everything else (today).
                - git and the GitHub CLI (`gh`): version control and GitHub from the terminal (today).
                - Python 3.14: runs the app and its tests, and matches the course's Docker image (today).
                - VS Code with four extensions: an editor that understands Dockerfiles, YAML, Terraform and Kubernetes files.
                - Docker Desktop: runs containers (Day 5).
                - kubectl, kind and helm: Kubernetes tools (Days 16 to 19).
                - terraform: creates infrastructure from code (Day 13).
                - Optional: k9s, a terminal dashboard for Kubernetes, and jq, a tool for reading JSON.

                Every install ends with a version check. If the check prints a version, the tool works. Install commands change over time, so if one fails, check that tool's current install page, linked in this lesson.
            """),
            "refs": refs("brew", "docker_mac"),
        },
        {
            "h": "Homebrew and your PATH",
            "body": T("""
                Homebrew (the `brew` command) is a package manager for macOS. A package manager downloads a tool, puts it in the right folder, and later updates or removes it. You install Homebrew with one command from [brew.sh](https://brew.sh/). It asks for your password, and it may install Apple's Command Line Tools, which include git.

                On Apple Silicon Macs, Homebrew lives in `/opt/homebrew`. At the end, the installer prints "Next steps" with two or three commands. They add Homebrew to your **PATH**: the list of folders your shell searches when you type a command.

                This step trips up most people. If you skip it, every `brew` command fails with "command not found". Run exactly what the installer prints, open a new terminal tab, then run `brew --version`.
            """),
            "refs": refs("brew", "brew_install"),
        },
        {
            "h": "Docker Desktop, and its licence",
            "body": T("""
                Containers are a Linux feature, and macOS is not Linux. So Docker Desktop runs a small Linux virtual machine (VM) in the background. A VM is a computer simulated in software. Your `docker` commands talk to the Linux system inside it.

                You install it with `brew install --cask docker-desktop`, or from [Docker's install page](https://docs.docker.com/desktop/setup/install/mac-install/). A cask is Homebrew's name for a Mac app with a window. Open Docker from Applications once and accept the terms.

                Then change one setting: in Settings, Advanced, turn on "Allow the default Docker socket to be used". It creates `/var/run/docker.sock`, the file other programs use to talk to Docker. New versions leave it off, and Terraform's Docker provider on Day 13 looks for it.

                The licence: Docker Desktop is free for personal use, education and non-commercial open source. It is also free for small businesses (fewer than 250 employees and less than $10 million in yearly revenue). Larger companies need a paid plan. Learning on your own laptop counts as personal use. On a work laptop, ask your employer first.

                Two alternatives run the same `docker` commands:

                - OrbStack: a fast Mac app, free for personal use and paid for commercial use.
                - Colima: free and open source, started from the terminal with `colima start`.
            """),
            "refs": refs("docker_mac", "docker_license", "orbstack"),
        },
        {
            "h": "The command-line tools",
            "body": T("""
                Homebrew installs the rest, one short command each. Each tool has one job:

                - kubectl: talks to any Kubernetes cluster.
                - kind: creates a small Kubernetes cluster inside Docker containers ("Kubernetes in Docker").
                - helm: installs packaged Kubernetes apps, called charts.
                - terraform: creates infrastructure from code files.

                Terraform needs one extra detail. In 2023 HashiCorp changed Terraform's licence. Homebrew's main collection then stopped updating it, so it is stuck at an old version there. Install it from HashiCorp's own tap instead. A tap is an extra collection of Homebrew packages, and `brew install hashicorp/tap/terraform` names the tap and the package together.

                VS Code comes as a cask too, and the cask also adds the `code` command to your terminal. You add extensions with `code --install-extension` and an extension ID. Container Tools, from Microsoft, replaced the older Docker extension and helps with Dockerfiles and Compose files.
            """),
            "refs": refs("tf_install", "kubectl_mac", "kind_quick"),
        },
        {
            "h": "Your repo and a Python virtual environment",
            "body": T("""
                The last part creates the project you ship all course. You put five starter files in `~/code/hello-devops`. They are given in full below:

                - `app.py`: the Flask web app.
                - `test_app.py`: three tests for pytest.
                - `requirements.txt`: the packages the app needs to run.
                - `requirements-dev.txt`: those packages plus pytest and ruff (a linter) for development.
                - `.gitignore`: files git should never commit.

                You install packages into a Python **virtual environment** (venv): a private folder of packages for one project. When you activate it, `python` and `pip` point into that folder. So this project's Flask cannot clash with another project's. The `.venv` folder is never committed, because anyone can rebuild it from the requirements files.

                Finally, `gh repo create` makes the GitHub repo and pushes in one step. `--source=.` means "use this folder", and `--push` sends your commits. The new repo is added as a remote called origin.
            """),
            "refs": refs("py_venv", "gh_repo_create"),
        },
        {
            "h": "When something goes wrong",
            "body": T("""
                Most setup problems are one of these:

                - `brew: command not found`: run the installer's "Next steps" lines, then open a new terminal tab.
                - "Cannot connect to the Docker daemon": open Docker Desktop and wait until it says it is running.
                - `code: command not found`: in VS Code, press Cmd+Shift+P, type "shell command" and run the install command.
                - "externally-managed-environment" from pip: your venv is not active, so run `source .venv/bin/activate`.
                - `git push` asks for a password: run `gh auth setup-git`, so git uses your gh login.
                - `gh repo create` says the name exists: delete or rename the old repo on GitHub, or pick another name.

                On Windows, install WSL2 first: run `wsl --install` in PowerShell as administrator, then restart. It gives you Ubuntu, a Linux system inside Windows. Install Docker Desktop for Windows, choose the WSL 2 engine, and turn on WSL integration. Then run this course's Linux commands inside Ubuntu.

                On Linux, install Docker Engine, and use your package manager or Homebrew on Linux for the rest. Each tool's install page lists the Linux steps.
            """),
            "refs": refs("wsl", "vscode_mac"),
        },
    ],
    "analogy": T("""
        Setting up your laptop is like stocking a new kitchen before you cook. Homebrew is the delivery service that brings each tool and puts it on the right shelf. PATH is the list of shelves you check when you reach for something. If a shelf is not on the list, you cannot find the tool, even though it is in the room. The analogy breaks because kitchen knives do not need updates, while your tools do, so run `brew upgrade` now and then.
    """),
    "diagram": D02_SVG,
    "diagram_caption": "Homebrew installs the tools. Each tool talks to a different place: GitHub, Docker's Linux VM, or the kind cluster inside it.",
    "worked": {
        "title": "See what a virtual environment changes",
        "steps": [
            {
                "say": "Make a throwaway folder and create a venv in it. `python3.14 -m venv .venv` runs Python's built-in venv module, which builds a private Python setup in the `.venv` folder.",
                "code": T("""
                    $ mkdir -p ~/code/venv-demo && cd ~/code/venv-demo
                    $ python3.14 -m venv .venv
                """),
                "lang": "console",
            },
            {
                "say": "Activate it. Activation puts `.venv/bin` at the front of your PATH, so `python` now means the venv's Python. Your prompt starts with `(.venv)` as a reminder.",
                "code": T("""
                    $ source .venv/bin/activate
                    (.venv) $ which python
                    /Users/you/code/venv-demo/.venv/bin/python
                    (.venv) $ python --version
                    Python 3.14.10
                """),
                "lang": "console",
            },
            {
                "say": "A new venv holds almost nothing. That is the point: only what you install is there.",
                "code": T("""
                    (.venv) $ python -m pip list
                    Package Version
                    ------- -------
                    pip     26.2.2
                """),
                "lang": "console",
            },
            {
                "say": "Install a package. Flask and the packages it depends on land inside `.venv`, not in Homebrew's Python, so other projects never see them.",
                "code": T("""
                    (.venv) $ python -m pip install -q flask
                    (.venv) $ python -m pip list
                    Package      Version
                    ------------ -------
                    blinker      1.9.0
                    click        8.5.0
                    Flask        3.1.3
                    itsdangerous 2.2.0
                    Jinja2       3.1.6
                    MarkupSafe   3.0.4
                    pip          26.2.2
                    Werkzeug     3.1.9
                """),
                "lang": "console",
            },
            {
                "say": "Leave with `deactivate`. A venv is disposable: you can delete it and rebuild it from a requirements file at any time. That is why `.gitignore` lists `.venv/`.",
                "code": T("""
                    (.venv) $ deactivate
                    $ rm -rf ~/code/venv-demo
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        {"lang": "python", "title": "app.py", "src": lab("app.py"), "run": "python app.py"},
        {"lang": "python", "title": "test_app.py", "src": lab("test_app.py"), "run": "pytest -q"},
        {"lang": "text", "title": "requirements.txt", "src": lab("requirements.txt"), "run": "pip install -r requirements.txt"},
        {"lang": "text", "title": "requirements-dev.txt", "src": lab("requirements-dev.txt"), "run": "pip install -r requirements-dev.txt"},
        {"lang": "text", "title": ".gitignore", "src": lab(".gitignore"), "run": "git status --short"},
    ],
    "commands": [
        {"cmd": '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', "what": "Install Homebrew (Mac). Then run the 'Next steps' lines it prints."},
        {"cmd": "brew install git gh python@3.14", "what": "Install git, the GitHub CLI and Python 3.14."},
        {"cmd": "brew install --cask docker-desktop visual-studio-code", "what": "Install the Docker Desktop and VS Code apps (Mac)."},
        {"cmd": "brew install kubectl kind helm hashicorp/tap/terraform", "what": "Install the Kubernetes tools, and Terraform from HashiCorp's tap."},
        {"cmd": "code --install-extension hashicorp.terraform", "what": "Add a VS Code extension by its ID. Repeat for each extension."},
        {"cmd": "gh auth login", "what": "Log in to GitHub from the terminal through your browser."},
        {"cmd": "python3.14 -m venv .venv && source .venv/bin/activate", "what": "Create a virtual environment in this folder and turn it on."},
        {"cmd": "pip install -r requirements-dev.txt", "what": "Install the app's packages and the dev tools into the active venv."},
        {"cmd": "pytest -q", "what": "Run the tests and print a short summary."},
        {"cmd": "gh repo create hello-devops --public --source=. --push", "what": "Create the GitHub repo from this folder, add it as origin, and push."},
        {"cmd": "docker run --rm hello-world", "what": "Check that Docker can download and run a container. Day 5 explains it."},
        {"cmd": "brew upgrade", "what": "Update everything Homebrew installed."},
    ],
    "mistake": T("""
        The classic mistake is installing Python packages outside a venv, or with `sudo pip`. Packages from different projects then fight over versions, and Homebrew's Python refuses with "externally-managed-environment". Always activate the project's `.venv` first, and check that your prompt starts with `(.venv)`.
    """),
    "real_world": T("""
        At PayFlow, new engineers run one setup script on their first day, and it installs the same tool versions everyone else uses. Python packages are pinned in requirements files, so a test that passes on one laptop also passes on others and in CI. Some teams go further and use dev containers, where the whole toolbox runs inside a container.
    """),
    "task": {
        "title": "Install your toolbox and ship hello-devops",
        "steps": [
            "Install Homebrew with the command from brew.sh. Run the \"Next steps\" lines it prints, open a new terminal tab, and check `brew --version`.",
            "Install git, the GitHub CLI and Python with `brew install git gh python@3.14`. Check each one with its `--version` flag (use `python3.14 --version`).",
            "Run `gh auth login`. Choose GitHub.com, HTTPS, yes to authenticating git, and logging in with a web browser. Confirm with `gh auth status`.",
            "Install the apps with `brew install --cask docker-desktop visual-studio-code`. Open Docker once, accept the terms, and turn on the default Docker socket in Settings, Advanced. Check `docker version`.",
            "Add four VS Code extensions with `code --install-extension`: `ms-azuretools.vscode-containers`, `redhat.vscode-yaml`, `hashicorp.terraform` and `ms-kubernetes-tools.vscode-kubernetes-tools`.",
            "Install `kubectl`, `kind`, `helm` and `hashicorp/tap/terraform` with brew. Check them with `kubectl version --client`, `kind version`, `helm version` and `terraform version`. Optional: `brew install k9s jq`.",
            "Create `~/code/hello-devops`, run `git init -b main` inside it, and save the five starter files from this lesson there.",
            "Create and activate a venv with Python 3.14, install `requirements-dev.txt`, and run the tests. All three should pass.",
            "Start the app with `python app.py` and open http://localhost:8000 in your browser. Reload a few times and watch `visits` grow. Stop it with Ctrl+C.",
            "Commit the five files, then publish them with `gh repo create hello-devops --public --source=. --push`. Open the repo on GitHub to see them.",
        ],
        "hints": [
            "If a version check fails right after an install, open a new terminal tab and try again.",
            "Before you commit, `git status` should not list `.venv/` or `__pycache__/`; if it does, check the name of your `.gitignore` file.",
            "If pip says \"externally-managed-environment\", your venv is not active in this terminal.",
        ],
        "done_when": "You are done when `pytest -q` shows 3 passed and your hello-devops repo with its five files is on GitHub.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences why the project uses a virtual environment. Mention what activation changes and why `.venv` is not committed.",
        "answer": T("""
            A virtual environment is a private folder of Python packages for one project, so its versions cannot clash with other projects. Activating it puts the venv's `bin` folder first in PATH, so `python` and `pip` use that folder. We do not commit `.venv`, because it is large, tied to one machine and easy to rebuild. Anyone can recreate it from `requirements-dev.txt` with one pip command.
        """),
    },
    "recap": [
        "Homebrew installs your tools; run its \"Next steps\" so `brew` is on your PATH.",
        "Docker Desktop runs a small Linux VM for containers, and it is free for personal use.",
        "Install Terraform from HashiCorp's tap: `brew install hashicorp/tap/terraform`.",
        "Every tool has a version check, and a printed version means it works.",
        "A venv keeps the project's packages private, and `.venv` is never committed.",
        "`gh repo create hello-devops --public --source=. --push` puts your repo on GitHub.",
    ],
    "check": [
        {
            "q": "A teammate runs `brew install terraform` and Homebrew says the formula is disabled. What should they run instead?",
            "options": [
                "`brew install terraform --force`",
                "`brew install hashicorp/tap/terraform`",
                "`pip install terraform`",
                "`sudo brew install terraform`",
            ],
            "answer": 1,
            "why": "Homebrew's main collection stopped updating Terraform after the 2023 licence change, so current versions come from HashiCorp's tap.",
        },
        {
            "q": "You open a new terminal, go to `~/code/hello-devops`, and `pytest` says 'command not found'. It worked yesterday. What is wrong?",
            "options": [
                "Your test files were deleted overnight",
                "pytest only runs while Docker is open",
                "This new terminal has no active venv",
                "Your GitHub login token has expired",
            ],
            "answer": 2,
            "why": "pytest lives inside `.venv`, and each new terminal starts without the venv active, so run `source .venv/bin/activate` first.",
        },
        {
            "q": "`git status` lists `.venv/` as a new folder to add. What is the best fix?",
            "options": [
                "Commit it so teammates get the packages",
                "Delete the venv after each session",
                "Move the venv into your home folder",
                "Add `.venv/` to `.gitignore`",
            ],
            "answer": 3,
            "why": "The venv is large and machine-specific; ignore it and let others rebuild it from the requirements files.",
        },
    ],
    "interview": [
        {
            "q": "How do you make sure every developer and CI use the same tool and package versions?",
            "a": "Pin versions in files that live in the repo, such as requirements files for Python packages. Install them into an isolated environment, like a venv or a container, never globally. Use the same files in CI, so the pipeline builds exactly what laptops build. For command-line tools, keep a setup script or a dev container in the repo, and change versions on purpose through pull requests.",
        },
        {
            "q": "Why do container tools on a Mac need a virtual machine?",
            "a": "Containers use features of the Linux kernel to isolate processes. macOS has a different kernel, so it cannot run Linux containers directly. Docker Desktop, OrbStack and Colima each start a small Linux VM and run the containers inside it. The `docker` command on the Mac only sends requests to the Docker engine in that VM.",
        },
    ],
    "deeper": {
        "minutes": 10,
        "body": T("""
            Two commands from today can feel like magic. Here is what they really do.

            When you run `brew install jq`, Homebrew does four things:

            1. It reads the formula, a small Ruby file that describes the package and its versions.
            2. It downloads a bottle, which is a prebuilt, compressed copy of the package for your Mac.
            3. It unpacks the bottle into its own folder, such as `/opt/homebrew/Cellar/jq/` plus the version.
            4. It links the command into `/opt/homebrew/bin`, a folder that is on your PATH.

            So two versions can sit side by side in the Cellar, and only the linked one runs. Casks work differently: they install an app into `/Applications`. A tap is an extra git repository of formulae, which is how `hashicorp/tap` works.

            The "Next steps" lines from the installer run `brew shellenv`. That command prints `export` lines for PATH and a few other variables, and `eval` runs them in your shell. The installer also adds the line to `~/.zprofile`, so every new terminal runs it.

            Activating a venv is simpler than it looks. `source .venv/bin/activate` runs a small script inside your current shell. It does three things:

            - It sets `VIRTUAL_ENV` to the venv folder.
            - It puts `.venv/bin` at the front of PATH.
            - It adds `(.venv)` to your prompt.

            Nothing else changes. That is why `which python` points into `.venv` after activation, and `deactivate` puts PATH back. You can also skip activation and run `.venv/bin/python app.py` directly. The Dockerfile on Day 8 uses the PATH trick instead: it puts the venv's `bin` folder first on PATH.

            PATH order matters everywhere. The shell runs the first match it finds, and `which -a python3` lists every `python3` on your PATH in the order the shell tries them. When the wrong version of a tool runs, this is the first command to try.
        """),
    },
    "sources": src("brew", "docker_mac", "tf_install", "gh_repo_create"),
}

# ---------------------------------------------------------------- part
part = {
    "part": 0,
    "title": "Start here",
    "intro": T("""
        Part 0 gives you the map and the tools. Day 1 shows where every tool in this course fits, so each later lesson has a place to land. Day 2 sets up your Mac and creates the hello-devops project you ship all course.
    """),
    "lessons": [d01, d02],
    "recap": [
        "DevOps is a way of working where the people who build software also share running it.",
        "A change travels code, build, test, package, release, deploy, run, observe and feedback.",
        "Each tool in this course owns one part of that path.",
        "Automate what repeats, keep everything as code, ship small changes and get feedback fast.",
        "DORA's five metrics measure delivery speed and stability together.",
        "Homebrew installs your tools, and Docker Desktop runs a small Linux VM for containers.",
        "Your hello-devops repo lives in `~/code/hello-devops` and on GitHub, with passing tests.",
    ],
    "flashcards": [
        {"front": "What three things does DevOps combine?", "back": "Culture, practices and tools, so the people who build software also share running it."},
        {"front": "List the steps a change passes through on its way to users.", "back": "Code, build, test, package, release, deploy, run, observe, feedback."},
        {"front": "Which tool packages the app, and which runs it across many machines?", "back": "Docker packages it into an image. Kubernetes runs the containers across machines."},
        {"front": "What does Argo CD do?", "back": "It watches a git repo and makes the cluster match what the repo says."},
        {"front": "Which DORA metrics measure throughput?", "back": "Change lead time, deployment frequency and failed deployment recovery time."},
        {"front": "Which DORA metrics measure instability?", "back": "Change fail rate and deployment rework rate."},
        {"front": "Why do small, frequent changes lower risk?", "back": "Each one is easy to review, test and undo, and a failure points to a small change."},
        {"front": "Where do you install Terraform from with Homebrew, and why?", "back": "From HashiCorp's tap (`hashicorp/tap/terraform`), because Homebrew's main collection stopped updating it after the 2023 licence change."},
        {"front": "What does activating a Python venv change?", "back": "It puts `.venv/bin` first on PATH, so `python` and `pip` use the project's private packages."},
        {"front": "What does `gh repo create hello-devops --public --source=. --push` do?", "back": "Creates the GitHub repo from this folder, adds it as the origin remote, and pushes your commits."},
    ],
    "quiz": [
        {
            "q": "A team ships one huge release every three months, and each one breaks something. Which idea from Day 1 helps most?",
            "options": ["Add a manual approval step", "Ship smaller changes more often", "Hire a separate ops team", "Release only on Fridays"],
            "answer": 1,
            "why": "Small, frequent changes are easier to test and undo, and a failure points straight at a small diff.",
        },
        {
            "q": "Which tool in this course keeps a Kubernetes cluster in sync with what is in git?",
            "options": ["Argo CD", "Terraform", "Docker", "Grafana"],
            "answer": 0,
            "why": "Argo CD watches a git repo and makes the cluster match it, which is how it deploys.",
        },
        {
            "q": "A team made 20 deployments last week. Four of them needed a rollback right away. What is the change fail rate?",
            "options": ["4 percent", "5 percent", "20 percent", "80 percent"],
            "answer": 2,
            "why": "Four out of twenty deployments needed immediate action, and 4 divided by 20 is 20 percent.",
        },
        {
            "q": "Right after installing Homebrew, `brew --version` says 'command not found'. What do you do?",
            "options": [
                "Reinstall Homebrew using sudo",
                "Restart Docker Desktop first",
                "Install the tool with pip instead",
                "Run the installer's 'Next steps' lines",
            ],
            "answer": 3,
            "why": "Those lines add `/opt/homebrew/bin` to your PATH; then open a new terminal tab.",
        },
        {
            "q": "You clone hello-devops onto a new laptop. What must you do before `pytest` works?",
            "options": [
                "Copy the old .venv folder across",
                "Make a venv, install requirements-dev.txt",
                "Run `gh repo create` once again",
                "Install Flask for all users with sudo",
            ],
            "answer": 1,
            "why": "The venv is not in git, so you rebuild it on each machine from the requirements file.",
        },
        {
            "q": "Which of these should never be committed to the hello-devops repo?",
            "options": ["requirements.txt", "test_app.py", ".gitignore", ".venv/"],
            "answer": 3,
            "why": "The venv is large and machine-specific, so `.gitignore` keeps it out of git.",
        },
    ],
}

OUT.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {OUT}")
