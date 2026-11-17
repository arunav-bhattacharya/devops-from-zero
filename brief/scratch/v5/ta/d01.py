"""Book-voice rewrite of d01 (The DevOps map). Writer: ta. Run from the repo root."""
import json

PATH = "content/p0.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d01")

L["opening"] = """Picture yourself baking bread in your home kitchen. The neighbors love it, and one day the café down the street asks for forty loaves every morning, starting Monday. Baking one good loaf was never the hard part. The hard part is forty good loaves, on time, every single morning, while you keep improving the recipe and nobody gets a burnt one.

Software has the same problem. Most people picture programmers writing code, and they assume the work ends when the code is written. That is an easy belief to hold, because writing code is the part you can see. But a program helps nobody until it runs for real people, every day, and keeps running after each change.

This is the first lesson, so we start with no tools at all, only a map. In this lesson, we'll follow one change from the kitchen to the customer, name each step on the way, and see which part of the course teaches it. Before we start, make a guess, and keep it in mind."""

L["guess"]["why"] = "DevOps is a way of working where the people who build software also share the work of running it. One new hire cannot change how a whole team works."

L["terms"] = [
    {"term": "DevOps", "plain": "A way of working where the people who build software also share the job of running it."},
    {"term": "Production", "plain": "The real, live system that your users use."},
    {"term": "Pipeline", "plain": "A fixed series of steps, run by machines, that carries a change from a developer's computer to real users."},
    {"term": "Continuous integration (CI)", "plain": "Adding small changes to the shared code often, with a machine that builds and tests each one."},
    {"term": "Continuous delivery (CD)", "plain": "Keeping every change that passes the tests ready to release to users at any time."},
    {"term": "Infrastructure as code (IaC)", "plain": "Describing the computers, networks and storage an app needs in text files, so a tool can create them for you."},
    {"term": "Observability", "plain": "Being able to see what a running system is doing from the outside, through numbers, written records and the path of each request."},
    {"term": "DORA metrics", "plain": "Five measures from the DORA research program that show how fast and how safely a team delivers software."},
]

S = L["sections"]

S[0]["h"] = "What DevOps is: one team instead of two"
S[0]["body"] = """Let's grow the bakery a little. You bake, and your cousin drives the loaves to the café. One Friday the café calls at seven: the bread is flat. Your cousin can't fix it, because only you know the recipe. You blame the hot van, your cousin blames the dough, and the café still has no bread.

Software companies were long split the same way. One team, the developers, wrote the code, the instructions that tell a computer what to do. A second team, operations, ran that code on servers. A server is a computer that stays on day and night and answers other computers over a network.

When the app broke at 2 a.m., operations got the call, but only the developers understood the code. Each side blamed the other. So both made releases rare. A release is one batch of changes handed to users, and rare releases grew huge and dreaded.

DevOps removes that wall. It is a way of working where the people who build software also share the work of running it. In the bakery, you and your cousin share one goal, good bread at seven, and you take turns answering the early call. You make small recipe changes, taste every batch and watch the café shelf. Then you buy the timer and the mixer that make those habits cheap enough to keep. Software teams name those three layers culture, practices and tools. Taking turns to be the person called when something breaks is known as on-call duty.

The real, live system that your users use is called production. In a DevOps team, finishing your code is only the halfway point. You are done when the change runs well in production and you can see that it does.

This course teaches mostly tools, because you can practise those alone on a laptop. Keep the culture in mind anyway. A team that installs Kubernetes (a popular tool for running apps on many machines) but keeps the wall ends up with the same wall, plus Kubernetes.

Next, we'll follow one change along the road that this one team now owns."""

S[1]["h"] = "Following one change from the kitchen to the customer"
S[1]["body"] = """Say you decide to use less sugar. Before the café sees that change, you write it on the recipe card, bake a test batch and taste it. You bag the loaves, the van takes them to the café, and you watch who buys a second one. Skip the tasting to save ten minutes, and you learn on Friday, from an unhappy owner, that the bread tastes of nothing. The mistake was made on Tuesday, far from where you paid for it.

Software takes the same road, called the pipeline. Its steps, in order:

1. Code: you change code on your laptop and commit it to git, a tool that saves snapshots of your files. Each snapshot is a commit.
2. Build: a machine turns the source code (the text you wrote) into something that can run.
3. Test: automated tests, small programs that check your program, make sure the change works and broke nothing else.
4. Package: the app and everything it needs go into one bundle, a container image, so it runs the same on any machine.
5. Release: the package gets a version number and goes to a shared store, called a registry.
6. Deploy: the new version replaces the old one on the servers.
7. Run: software on the servers keeps the app alive, restarts it if it crashes and starts extra copies when traffic grows.
8. Observe: graphs, logs and alerts show how the app behaves. A log is a written record of what the app did, and an alert is a message that calls a person.
9. Feedback: what you learn shapes the next change, and the loop starts again.

In the bakery, the recipe card is the code, the tasting is the test, the bag is the package and the van is the deploy.

Now the same mistake in software. Tomorrow you create hello-devops, a tiny web app that answers every visit with a greeting and a count of visits so far. Say you change its default greeting from "Hello, DevOps!" to "Hi there" and push, which sends your commits to a shared copy online. The test step fails at once, because one test still expects the old greeting. You find out two minutes later on your own branch, instead of from a user on Friday night. A branch is your own line of work, kept apart from everyone else's. Each step of the pipeline catches a different kind of mistake, as close as possible to where it was made.

The name CI/CD covers steps 2 to 6. Continuous integration (CI) means you add small changes to the shared code often, and a machine builds and tests each one. Continuous delivery (CD) means every change that passes is ready to release at any time. You build both in Part 6.

Deciding what to change takes a person. Building, testing and shipping do not. **When a step goes the same way every time, give it to a machine.**

Next, we'll put the course's parts along the road."""

S[2]["h"] = "Where each part of this course sits on the road"
S[2]["body"] = """Twenty stops on one road are easier to remember than twenty tool names. The course has 68 lessons in 20 parts, and each part owns one piece of the pipeline. Two words come up below. A service is a program that does a job for other programs. A request is a message asking a service for something.

- Part 0, Start here (Days 1 and 2): this map, and your laptop setup.
- Part 1, The Linux command line (Days 3 to 7): typing commands to Linux, the system most servers run, from files to SSH (logging in to other machines) and scripts.
- Part 2, Git (Days 8 and 9): how Git stores your work, how to undo mistakes, and branches.
- Part 3, Networking and the cloud (Days 10 to 14): how computers find each other and talk safely, then cloud basics and AWS (Amazon's rented computers) by hand.
- Part 4, Python scripts (Days 15 and 16): small automation scripts that read logs and ask other programs for data.
- Part 5, Docker (Days 17 to 22): package the app into an image that runs the same everywhere. A running image is a container.
- Part 6, CI/CD with GitHub Actions (Days 23 to 27): test, build and publish on every push.
- Part 7, Builds with Gradle (Days 28 to 30): build, test and package an app written in Kotlin (another programming language), fast, in CI.
- Part 8, Terraform (Days 31 to 35): create infrastructure (the machines, networks and storage an app runs on) from code files.
- Part 9, Ansible (Days 36 and 37): set up the servers you created, the same way every time.
- Part 10, Kubernetes (Days 38 to 46): run many containers across a cluster, a group of machines, and keep them healthy.
- Part 11, GitOps with Argo CD (Days 47 and 48): deploy by making the cluster match what Git says.
- Part 12, Prometheus (Days 49 to 52): collect metrics (numbers measured over time) and alert when something is wrong.
- Part 13, Grafana (Days 53 and 54): dashboards (screens of live graphs), plus alerts and logs in the same tool.
- Part 14, Logs and traces (Days 55 to 57): search all logs in one place, and follow one request across services.
- Part 15, Service mesh (Days 58 to 60): tools that manage the calls between services, and when you need none.
- Part 16, Dynatrace (Days 61 and 62): a commercial platform that covers much of Parts 12 to 14 in one product.
- Part 17, DevSecOps (Days 63 and 64): security checks at every step, from dependencies (code your app borrows) to the cluster.
- Part 18, AI in DevOps (Days 65 and 66): use AI assistants and agents, check their work, and keep them safe.
- Part 19, Platform engineering and your capstone (Days 67 and 68): internal platforms, then one final project that touches every part.

Read it as layers. Linux and networking sit underneath everything, because every server, container and CI runner (the machine that runs your checks) runs Linux and talks over a network. Each tool above them takes one stretch of the road. DevSecOps checks every step, and Python and AI assistants help along all of it.

Do not try to memorize the list. When a new tool appears, come back here and ask which step it owns. The ideas under all these tools come next."""

S[3]["h"] = "Four ideas that sit under every tool"
S[3]["body"] = """Back to the bakery. The café says today's bread is dry. That same day, you changed the flour, the oven setting and the baking time. Which change made it dry? You can't tell, so you undo all three, or guess.

Tools change every few years, and the ideas behind them change much more slowly. Once you know these four, each new tool makes sense faster:

- Automate what repeats: if you do a task by hand twice, script it the third time. A script is a small file of commands that a computer runs in order.
- Keep everything as code: app, infrastructure, pipelines and settings live as text files in Git.
- Ship small changes often: each one is easy to review, test and undo.
- Get feedback fast: tests, deploys and alerts should answer within minutes.

The ideas lean on each other. Code that lives in Git can be checked by machines, and those automated checks are what make small changes safe. A small change also gives clear feedback: when it breaks something, you know where to look. A release with 300 changes in it can fail in 300 places.

**Change one thing at a time, and you will know what broke.**

Infrastructure as code (IaC) is the second idea applied to servers and networks. You describe what you want in a text file, and a tool such as Terraform creates it. You write your first one on Day 31.

But how does a team know it is getting better at all this? Next, we'll measure it."""

S[4]["h"] = "Measuring how a team delivers: the DORA metrics"
S[4]["body"] = """The bakery now supplies five cafés. Are you getting faster, or does it only feel that way? You can't tell without counting.

Software teams count too. This course uses the metrics from DORA, a long-running research program that studies software teams. A metric is a number you measure again and again. DORA's [guide to the metrics](https://dora.dev/guides/dora-metrics/) names five measures in two groups.

Throughput shows how fast changes flow:

- Change lead time: the time from a commit to that change running in production.
- Deployment frequency: how often you deploy to production.
- Failed deployment recovery time: how long it takes to recover when a deployment fails.

Instability shows how often changes cause harm:

- Change fail rate: the share of deployments that need immediate action, such as a rollback (putting the previous version back).
- Deployment rework rate: the share of deployments that are unplanned fixes for a problem in production.

You might expect fast teams to break more things. DORA's research finds that speed and stability tend to go together, and the best teams do well on both groups. Small changes are one reason: each one is quick to ship and easy to undo.

Do not turn a metric into a target, though. A team told to "deploy daily" can hit that number with tiny, pointless deploys. Picture a van that leaves twelve times a day with one bread roll. The numbers work better as the start of a conversation about where work gets stuck.

Numbers don't say who does which job. Next, we'll meet the titles that grew out of these ideas."""

S[5]["h"] = "Three roles you will see in job ads"
S[5]["body"] = """Now the bakery has ten branches, and three kinds of helper appear. One builds the ovens and delivery routes. One makes sure every branch opens on time, and when an oven fails twice, fixes the cause. One builds a central kitchen with ready-made tools, so a new branch opens without inventing its own.

Software grew the same three jobs. They overlap, and companies use the titles loosely, so read what a job involves before you trust its title:

- DevOps engineer: builds pipelines, infrastructure code and deploy tools, usually with product teams (the teams that build what customers use).
- Site reliability engineer (SRE): keeps production reliable, and writes software to replace manual operations work.
- Platform engineer: builds an internal platform, a set of self-service tools so other teams ship without waiting for anyone.

The SRE role started at Google, and Google's engineers wrote [a free book about it](https://sre.google/sre-book/table-of-contents/). Platform engineering is newer. It answers a growth problem: when twenty product teams each build their own pipelines and clusters, the work repeats and the quality varies. That is the central kitchen. Day 67 comes back to it.

You need none of these titles to start. If you have ever wondered how a phone app gets a new version overnight, you have asked the question all three answer. Before we follow that question, here is how each lesson is built."""

S[6]["h"] = "How each lesson in this course works"
S[6]["body"] = """Nobody learns to bake from recipes alone, so every lesson mixes reading with doing. Each one takes 40 to 50 minutes, and you can split it over two sittings. Every lesson has the same shape:

1. Guess an answer before you read. Even a wrong guess makes the answer easier to remember.
2. Read the words you will meet, then the short sections, then study the diagram.
3. Follow the worked example, which shows real commands (lines you type to tell the computer what to do) and their real output.
4. Do the hands-on task on your own laptop. It is similar to the example, but not the same.
5. Explain the idea back in your own words, then take the three check questions.

Two optional extras follow: an interview corner and a "go deeper" box for days with more time. Each part ends with flashcards and a short quiz. A few quiz questions come from earlier parts on purpose, because mixing old and new topics helps you remember both.

All course long you ship one small app: hello-devops, written in Python, a programming language known for being easy to read. You create its repo tomorrow. A repo, short for repository, is a project folder that Git tracks. By the capstone, the final project, it is tested, packaged, deployed to Kubernetes by Argo CD and watched on dashboards.

Part 7 adds a second small app, hello-jvm, written in Kotlin, so you see the same ideas with a different kind of app.

Everything runs on your Mac and costs nothing. From Day 2 you practise Linux in a throwaway container running Ubuntu, a popular version of Linux. Throwaway means you can break it and start a fresh one. From Day 6 you also use a small Ubuntu virtual machine, a whole computer simulated in software. The steps that use a real cloud account are on Days 13, 14 and 35. They are optional: you can follow Days 13 and 14 with a local stand-in for AWS instead, and every cloud step ends with a cleanup.

Tomorrow, the map turns into tools on your laptop."""



L["real_world"] = "Picture an online payments company that works this way. When more customers than usual see errors at checkout (the page where they pay), the alert goes to the team that wrote checkout. That one product team owns the service from code to production, and its pipeline tests and deploys changes many times a day. A platform team gives every product team shared pipelines, clusters and dashboards, so nobody builds those from scratch."

W = L["worked"]["steps"]
W[0]["say"] = "Here is one week of production deploys from a made-up payments team. A deploy is one new version going live. Each line shows when a change was committed (saved in Git), when it reached production and how it went."
W[1]["say"] = "Start with deployment frequency, because you only have to count lines. Ten deployments in five working days is two per working day."
W[2]["say"] = "For change lead time, subtract the commit time from the deploy time on each line. Then sort the results and take the middle value, called the median. With ten numbers, two sit in the middle, so you average those two. The median stops one slow change from hiding the normal case."
W[3]["say"] = "Change fail rate counts deployments that needed immediate action. Number 4 was rolled back, which means the old version was put back. Number 8 needed a hotfix, an urgent fix shipped outside the normal plan. That is 2 out of 10, or 20 percent."
W[4]["say"] = "For failed deployment recovery time, look at those two failures. Number 4 recovered in 25 minutes. Number 8 broke at 16:00, and its hotfix landed at 17:35, so that took 95 minutes. The average of the two is 60 minutes."
W[5]["say"] = "Deployment rework rate counts unplanned fixes. Number 9 only happened because number 8 broke production. That is 1 out of 10, or 10 percent."
W[6]["say"] = "Now read the five numbers together. The team deploys often and its lead times are short, but one deploy in five fails. I would ask two things next: what did deployments 4 and 8 have in common, and why did change 7 wait overnight?"

L["task"]["steps"] = [
    "Pick one piece of software you know from the inside: something from your job, a side project, or an app a friend builds. If you have none, use the bakery from today's lesson.",
    "On paper, write every step a change takes from the first edit to real users, in order.",
    "Mark each step as manual (a person does it) or automated (a machine does it).",
    "Next to each step, write the tool used, if you know it, and the matching step name from today's map.",
    "Next to each step, write which part of this course covers it.",
    "Estimate the five DORA metrics for it. Rough guesses are fine.",
    "Circle the one step you would automate first, and write one sentence on why.",
]
L["task"]["hints"] = [
    "To estimate lead time, think of the last change: when was it first saved, and when did users get it?",
    "Waiting counts too: a change that waits two days for someone to review it adds two days of lead time.",
]
L["task"]["done_when"] = "You are done when you have one page with every step marked manual or automated, a tool and a course part for each, and a guess for all five DORA metrics."

L["explain_back"]["prompt"] = "Explain DevOps to a friend who has never worked in software, in 3 to 4 sentences. Mention shared ownership, the pipeline and one DORA metric."
L["explain_back"]["answer"] = "DevOps is a way of working where the people who build a piece of software also help run it for real users. A change travels a pipeline: code, build, test, package, release, deploy, run and observe, and the team lets machines do as many of those steps as it can. Small, frequent changes keep each step safe and show quickly when something is wrong. To see whether it is working, teams use DORA metrics, such as change lead time: how long a saved change takes to reach users."

L["recap"] = [
    "DevOps means the people who build software also share running it, through culture, practices and tools.",
    "A change flows through code, build, test, package, release, deploy, run, observe and feedback.",
    "The course has 20 parts, and each owns a piece of that road, with Linux and networking underneath.",
    "Four ideas drive it all: automate repeats, keep everything as code, ship small changes, get feedback fast.",
    "DORA's five metrics measure throughput and instability, but a metric turned into a target gets gamed.",
    "DevOps engineer, SRE and platform engineer overlap, so read the job, not the title.",
]

C = L["check"]
C[0]["why"] = "Running the checks on every push gives feedback within minutes, which a weekly run by hand cannot."
C[1]["q"] = "A team creates its cloud network and database (where its data is stored) by clicking buttons on a website. Which part of this course turns that into code?"
C[1]["why"] = "Terraform creates infrastructure, such as networks and databases, from text files."
C[2]["why"] = "Six out of forty deployments needed immediate action, and 6 divided by 40 is 15 percent."

I = L["interview"]
I[0]["a"] = "It is a way of working where the team that builds a service also runs it. That team owns the service from commit to production, including being on call for it. In practice that means small changes, automated pipelines for build, test and deploy, infrastructure as code and good monitoring. A company can buy every DevOps tool and still not be doing DevOps if building and running stay with separate teams."
I[1]["a"] = "I would start with DORA's five metrics. Change lead time, deployment frequency and failed deployment recovery time show throughput. Change fail rate and deployment rework rate show instability. I would track them for one service over time and read them together, because pushing one metric alone invites gaming. Then I would pair the numbers with a conversation about where changes wait the longest."
I[2]["a"] = "DevOps is the broad idea: one team shares building and running software, with automation and fast feedback. SRE is one concrete way to do the running part, started at Google. There, engineers with software skills do operations work and use error budgets (an agreed amount of failure) to balance speed and reliability. Platform engineering builds shared, self-service tools, such as pipelines and clusters, so product teams do not each build their own. At real companies the titles overlap, so I look at what the role actually owns."

L["deeper"]["body"] = """People often mix up DevOps, SRE and platform engineering. DevOps is the general way of working, where one team builds and runs the software with plenty of automation and fast feedback. It names no job title and no tool.

SRE is one concrete way to do it. In the opening part of [Google's SRE book](https://sre.google/sre-book/part-I-introduction/), Ben Treynor Sloss describes SRE as operations work done by engineers with software skills. Two ideas from the book matter for this course:

- The book describes a 50 percent cap on manual operations work for SREs. The rest of their time goes to engineering that removes manual work.
- 100 percent reliability is the wrong target, because users cannot tell 100 percent from 99.999 percent. The gap between the target and perfect becomes an error budget the team can spend on releases. You meet error budgets on Day 49.

The second idea surprises most people at first. In the bakery, it would mean accepting that a rare loaf comes out a little pale. Chasing that last loaf would cost so much care that you would never dare to try a new recipe.

Platform engineering shows up once a company has many product teams. Instead of each team building its own pipelines and clusters, with repeated work and uneven quality, a platform team builds shared, self-service tools. The CNCF (Cloud Native Computing Foundation) is a non-profit group that looks after Kubernetes and many other tools in this course. Its [platforms white paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) argues that an internal platform should be run like a product, with the app teams as its users. You see this on Day 67.

DORA stands for DevOps Research and Assessment. Older articles talk about its "four keys" and "time to restore service". DORA's current guide lists the five metrics from this lesson, with rework rate as the newest. The guide also warns about pitfalls teams hit when they adopt the metrics:

- Turning a metric into a goal, which invites people to game it.
- Trusting one metric alone, instead of several that balance each other.
- Comparing very different apps, such as a mobile app and a mainframe system (a large, older kind of business computer).
- Using the metrics to make teams compete, instead of to improve over time.

My advice: measure one service at a time, watch the trend, and ask the team what slows their changes down. If you work on a team and want to try it on real history, count deploys and failures from your team's last month of release notes. It takes about ten minutes and usually starts a good discussion."""

L["closing"] = """We started in a home kitchen, with a café that wanted forty good loaves every morning. The baking was never the hard part. The road was: recipe, test batch, tasting, packing, the van, a full basket and a close eye on customers. Software takes the same road, and DevOps is one team owning all of it.

The next time an app on your phone updates, ask which steps that change passed through, and which of them a person did by hand.

Next, we'll set up your laptop with the tools for that road, open a Linux practice box and push a first, tested copy of hello-devops. The question it answers: what does the kitchen need before the first loaf?"""

L.pop("analogy", None)
L.pop("mistake", None)
L["aside"] = {"title": "Where do these parts sit on the site?", "after": 2, "body": """On the site, the twenty parts sit in seven groups, in the same order. Foundations (Days 1 to 16) covers the shell, Git, networks and the cloud, and Python. Build and ship (Days 17 to 30) covers Docker, GitHub Actions and Gradle. Infrastructure as code (Days 31 to 37) is Terraform and Ansible, and Run on Kubernetes (Days 38 to 48) is Kubernetes and Argo CD. Observability (Days 49 to 57) covers metrics, dashboards, logs and traces, and Operate at scale (Days 58 to 62) covers service mesh and Dynatrace. The last group is Security, AI and the capstone (Days 63 to 68)."""}

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d01 written")
