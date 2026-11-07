#!/usr/bin/env python3
"""Human-writing pass (v3, editor p0p2) for content/p0.json and content/p2.json.

Each edit is (path, old, new). The path points at one prose string. `old` must occur
exactly once in that string and is replaced by `new` (like an exact-match edit).
If `old` is gone and `new` is already there, the edit counts as applied, so the
script can run twice. Only prose fields are touched."""
import json
import pathlib
import sys

ROOT = pathlib.Path("/home/user/devops-from-zero")

P0 = [
    # ---------------- part level ----------------
    (["intro"],
     "Part 0 is groundwork. Day 1 gives you a map of DevOps and of this 55-lesson course, so when a new tool shows up later, you already know which job it does.",
     "Two days of groundwork come before the real tools. Day 1 draws a map of DevOps and of the 55 lessons ahead. When a new tool shows up later, you will already know which job it does."),
    (["quiz", 1, "why"],
     "Argo CD watches a git repo and changes the cluster until it matches. That is how it deploys.",
     "Argo CD deploys by watching a git repo and changing the cluster until it matches."),
    (["resources", 4, "why"],
     "MIT's well-loved lecture on the shell, a good warm-up before Part 1.",
     "MIT's opening lecture on the shell, and a good warm-up before Part 1."),

    # ---------------- d01 ----------------
    (["lessons", "d01", "sections", 0, "body"],
     "Picture the older way of shipping software. One team writes the code. A separate operations team (ops) installs it on servers and keeps it running.",
     "In the older way of shipping software, one team writes the code and a separate operations team (ops) installs it on servers and keeps it running."),
    (["lessons", "d01", "sections", 0, "body"],
     "Releases become rare, big and scary, because every release is a chance for the other team to cause trouble.",
     "So releases get rare and huge, and everyone dreads them, because each one is a chance for the other team to cause trouble."),
    (["lessons", "d01", "sections", 0, "body"],
     "In a DevOps team, your work is not finished when your code is merged. It is finished when the change runs well in production and you can see that it does.",
     "In a DevOps team, merging your code is only the halfway point. You are done when the change runs well in production and you can see that it does."),
    (["lessons", "d01", "sections", 1, "body"],
     "Every change, big or small, takes the same road to your users. Engineers call this road the **pipeline**. These are its steps, in order:",
     "Every change takes the same road to your users, and engineers call that road the **pipeline**. Its steps, in order:"),
    (["lessons", "d01", "sections", 1, "body"],
     "Take a small example from this course. Tomorrow you create hello-devops,",
     "Tomorrow you create hello-devops,"),
    (["lessons", "d01", "sections", 1, "body"],
     "You learn this in two minutes on your branch, not from a user on Friday night.",
     "You find out two minutes later on your own branch, instead of from a user on Friday night."),
    (["lessons", "d01", "sections", 1, "body"],
     "Deciding what to change needs a person. Building, testing and shipping are the same every time, so hand them to a machine.",
     "Deciding what to change takes a person. Building, testing and shipping go the same way every time, so a machine should do them."),
    (["lessons", "d01", "sections", 3, "body"],
     "Tools change every few years. The ideas behind them change much more slowly. Once you know these four, each new tool makes sense faster:",
     "Tools change every few years, and the ideas behind them change much more slowly. Once you know these four, each new tool makes sense faster:"),
    (["lessons", "d01", "sections", 3, "body"],
     "The four ideas support each other. Code that lives in git can be checked by machines. Those automated checks are what make small changes safe. And a small change gives clear feedback, because when it breaks something, you know where to look. A release with 300 changes in it fails in 300 possible places.",
     "They lean on each other. Code that lives in git can be checked by machines, and those automated checks are what make small changes safe. A small change also gives clear feedback: when it breaks something, you know where to look. A release with 300 changes in it can fail in 300 places."),
    (["lessons", "d01", "sections", 4, "body"],
     "DORA's research finds the opposite: speed and stability tend to go together, and the best teams do well on both groups. Just do not turn a metric into a target. A team told to \"deploy daily\" can hit that number with tiny, pointless deploys. Use the numbers to start a conversation about where work gets stuck.",
     "DORA's research finds that speed and stability tend to go together, and the best teams do well on both groups.\n\nDo not turn a metric into a target, though. A team told to \"deploy daily\" can hit that number with tiny, pointless deploys. The numbers work better as the start of a conversation about where work gets stuck."),
    (["lessons", "d01", "sections", 5, "body"],
     "As a backend engineer, you already do part of this work. You write code that has to run somewhere. This course adds the rest: how it gets there, what it runs on, and how you know it is healthy.",
     "As a backend engineer, you already do part of this work, because the code you write has to run somewhere. The rest of this course covers how it gets there, what it runs on and how you know it is healthy."),
    (["lessons", "d01", "analogy"],
     "The picture breaks in one place: a factory builds the same car thousands of times, but every software change is new. So your tests have to grow with your code.",
     "But a factory builds the same car thousands of times, while each software change you ship is new. So your tests have to keep growing with your code."),
    (["lessons", "d01", "worked", "steps", 0, "say"],
     "PayFlow is a made-up payments team. Below is one week of their production deploy log. Each line shows when a change was committed, when it reached production, and how it went.",
     "This is one week of production deploys from a made-up payments team. Each line shows when a change was committed, when it reached production and how it went."),
    (["lessons", "d01", "worked", "steps", 6, "say"],
     "Now read the five numbers together. PayFlow deploys often and lead times are short, but one deploy in five fails.",
     "Read the five numbers together. The team deploys often and its lead times are short, but one deploy in five fails."),
    (["lessons", "d01", "real_world"],
     "At PayFlow, the made-up payments company from the worked example, one product team owns the checkout service from code to production. Their pipeline tests and deploys changes many times a day, and when checkout errors rise, the same team is on call.",
     "When checkout errors rise at a payments company that works this way, the alert goes to the team that wrote checkout. That one product team owns the service from code to production, and its pipeline tests and deploys changes many times a day."),
    (["lessons", "d01", "deeper", "body"],
     "DevOps is the broad idea: one team shares building and running software, with automation and fast feedback. It does not prescribe a job title or a tool.",
     "DevOps is the general way of working, where one team builds and runs the software with plenty of automation and fast feedback. It names no job title and no tool."),
    (["lessons", "d01", "deeper", "body"],
     "Platform engineering answers a scaling problem. When every product team builds its own pipelines and clusters, the work repeats and quality varies. So a platform team builds shared, self-service tools instead.",
     "Platform engineering shows up once a company has many product teams. Instead of each team building its own pipelines and clusters, with repeated work and uneven quality, a platform team builds shared, self-service tools."),

    (["lessons", "d01", "interview", 2, "a"],
     "In practice the titles overlap, so I look at what the role actually owns.",
     "At real companies the titles overlap, so I look at what the role actually owns."),

    # ---------------- d02 ----------------
    (["lessons", "d02", "sections", 1, "body"],
     "A note on Python. Homebrew's default Python is now newer than the one this course uses. You install `python@3.14` and type `python3.14` when you create the project's virtual environment. After that, inside the venv, plain `python` is the right one.",
     "Python needs one extra step. Homebrew's default Python is now newer than the one this course uses, so you install `python@3.14` and type `python3.14` when you create the project's virtual environment. Inside the venv, plain `python` is then the right one."),
    (["lessons", "d02", "sections", 3, "body"],
     "Terraform needs one extra detail. After HashiCorp",
     "Terraform is the odd one out. After HashiCorp"),
    (["lessons", "d02", "analogy"],
     "The comparison fails on upkeep: kitchen knives do not need updates, but your tools do, so run `brew upgrade` now and then.",
     "Unlike kitchen knives, your tools need updates, so run `brew upgrade` now and then."),
    (["lessons", "d02", "real_world"],
     "On their first day at PayFlow, a made-up payments company, new engineers run one setup script that installs the same tool versions everyone else uses. Python packages are pinned in requirements files and the JDK version is pinned in the build. So a test that passes on one laptop also passes on the others and in CI. Some teams go further with dev containers, where the whole toolbox runs inside a container.",
     "When a test passes on one laptop and fails on another, the cause is often a different tool version. So some teams hand new engineers one setup script on day one, which installs the same versions everyone else uses. Python packages are pinned in requirements files and the JDK version is pinned in the build, so CI runs the same versions too. Others go further with dev containers, where the whole toolbox runs inside a container."),
]

P2 = [
    # ---------------- part level ----------------
    (["intro"],
     "Part 2 follows one request in the order it happens. Day 8 covers names, addresses and ports. Day 9 covers the HTTP conversation and the servers in the middle, and Day 10 the rented cloud network around it all.",
     "Part 2 follows one request in the order things happen to it. Day 8 is about names, addresses and ports. Day 9 is the HTTP conversation and the servers in the middle, and Day 10 is the rented cloud network around it all."),
    (["resources", 0, "why"],
     "Julia Evans explains DNS with comics and real queries, and makes it stop feeling like magic.",
     "Julia Evans explains DNS with comics and real queries, so the moving parts are easy to picture."),

    # ---------------- d08 ----------------
    (["lessons", "d08", "sections", 0, "body"],
     "Think of it as the street address of a building.",
     "It does the job a street address does for a building."),
    (["lessons", "d08", "sections", 1, "body"],
     "How does your laptop know to send packets to the router at all? Every machine has a route table: a short list of rules that says where to send traffic for each block of addresses.",
     "Your laptop knows to send those packets to the router because of its route table. Every machine has one: a short list of rules that says where to send traffic for each block of addresses."),
    (["lessons", "d08", "sections", 1, "body"],
     "Keep this picture. On Day 10 a cloud network uses the same ideas, with an internet gateway, a NAT gateway and route tables that you write yourself.",
     "Day 10 brings the same ideas back in a cloud network, with an internet gateway, a NAT gateway and route tables that you write yourself."),
    (["lessons", "d08", "sections", 2, "body"],
     "This trips up almost everyone at first: a bigger number after the slash means a smaller network.",
     "The direction feels backwards at first: a bigger number after the slash means a smaller network."),
    (["lessons", "d08", "sections", 4, "body"],
     "`0.0.0.0` is not an address you connect to. It is a wildcard for listening. You can see the difference in the tools.",
     "`0.0.0.0` is a wildcard for listening, and you never connect to it. The tools show the difference."),
    (["lessons", "d08", "sections", 4, "body"],
     "Now the container part. A container gets its own network stack",
     "A container gets its own network stack"),
    (["lessons", "d08", "sections", 4, "body"],
     "One more Docker detail. `-p 8000:8000` publishes the port on every address of your Mac,",
     "Publishing also opens the port wider than you might expect. `-p 8000:8000` publishes the port on every address of your Mac,"),
    (["lessons", "d08", "sections", 5, "body"],
     "One gotcha: `dig` asks DNS servers directly and ignores `/etc/hosts`, while your apps and `ping` read that file first.",
     "Watch out with `dig`, though: it asks DNS servers directly and ignores `/etc/hosts`, while your apps and `ping` read that file first."),
    (["lessons", "d08", "sections", 6, "body"],
     "Learn these four, and much of network debugging becomes reading:",
     "Four errors cover most cases:"),
    (["lessons", "d08", "sections", 6, "body"],
     "A timeout makes you wait for seconds before it gives up. That difference alone tells you a lot.",
     "A timeout makes you wait for seconds before it gives up, so even the waiting is a clue."),
    (["lessons", "d08", "analogy"],
     "The picture breaks on speed and on copies. The whole thing takes milliseconds, and the phone book is copied into caches all over the world, each one possibly a little out of date.",
     "Real mail takes days, and this takes milliseconds. There is also no single phone book: copies of it sit in caches all over the world, and any of them may be a little out of date."),
    (["lessons", "d08", "worked", "steps", 0, "say"],
     "Set the scene. A Redis container called cache runs on a Docker network called shopnet. A second container, client, is your app's stand-in; it starts on Docker's default network.",
     "A Redis container called cache runs on a Docker network called shopnet. A second container, client, stands in for your app, and it starts on Docker's default network."),
    (["lessons", "d08", "real_world"],
     "PayFlow, a made-up payments company, is moving its ledger database to a new server behind the name `ledger-db.internal`. A day before, the team lowers that record's TTL from one hour to 60 seconds, so every client picks up the new address within a minute of the switch.",
     "A team is moving its ledger database to a new server behind the name `ledger-db.internal`. A day early, they lower that record's TTL from one hour to 60 seconds, so every client picks up the new address within a minute of the switch."),
    (["lessons", "d08", "deeper", "body"],
     "Two details from real life are worth knowing:",
     "Real resolvers add two complications:"),
    (["lessons", "d08", "deeper", "body"],
     "One more trap. On a Mac, the name `localhost` can resolve",
     "Last, a trap on the Mac: the name `localhost` can resolve"),

    # ---------------- d09 ----------------
    (["lessons", "d09", "sections", 1, "body"],
     "Two words describe methods. A safe method changes nothing",
     "A safe method changes nothing"),
    (["lessons", "d09", "sections", 1, "body"],
     "This matters to operators because networks fail halfway.",
     "Operators care about this because networks fail halfway."),
    (["lessons", "d09", "sections", 2, "body"],
     "Notice the last three. 502, 503 and 504 usually come from a proxy or load balancer, not from your code.",
     "The last three, 502, 503 and 504, usually come from a proxy or load balancer, not from your code."),
    (["lessons", "d09", "sections", 3, "body"],
     "`--resolve` is a good trick to know. It lets you test a new server under its real name before you change DNS,",
     "With `--resolve` you can test a new server under its real name before you change DNS,"),
    (["lessons", "d09", "sections", 4, "body"],
     "Know what TLS does not hide. The server's IP address",
     "TLS does not hide everything. The server's IP address"),
    (["lessons", "d09", "analogy"],
     "The picture breaks on scale and memory: a real receptionist remembers yesterday's visitors, while HTTP forgets each request unless a cookie reminds it.",
     "A real receptionist remembers yesterday's visitors. The server does not: it forgets each request once it has answered, unless a cookie reminds it."),
    (["lessons", "d09", "mistake"],
     "When curl fails with a certificate error, many people add `-k` (or the same switch in their HTTP library) and move on. That turns off the identity check, so you would talk to an attacker just as happily, and the setting tends to reach production.",
     "Adding `-k` to make a certificate error go away (or the same switch in your HTTP library) turns off the identity check. With it, curl talks to an attacker just as happily, and the setting tends to reach production."),
    (["lessons", "d09", "real_world"],
     "At PayFlow, a made-up payments company, every public request first reaches a layer 7 load balancer that holds the TLS certificates, renewed automatically. It routes `/api/payments` to the payments service and spreads requests over copies in two zones, using health checks to skip broken ones. The payments API requires an idempotency key on every POST,",
     "Every public request to a payments API first reaches a layer 7 load balancer, which holds the TLS certificates and renews them on its own. The balancer routes `/api/payments` to the payments service and spreads requests over copies in two zones. Health checks tell it which copies to skip. The API also requires an idempotency key on every POST,"),

    # ---------------- d10 ----------------
    (["lessons", "d10", "sections", 0, "body"],
     "Every click in a cloud console is really an API call. That one fact explains a lot of this course. Anything you can click, a program can do.",
     "Every click in a cloud console is really an API call, so anything you can click, a program can do."),
    (["lessons", "d10", "sections", 1, "body"],
     "Why the split? Because things fail at every size:",
     "The split exists because things fail at every size:"),
    (["lessons", "d10", "sections", 1, "body"],
     "One trap catches nearly every beginner. A cloud console shows one region at a time, and a server you created in another region keeps running and billing, out of sight.",
     "A cloud console shows one region at a time, and nearly every beginner gets caught by this. A server you created in another region keeps running and billing, out of sight."),
    (["lessons", "d10", "sections", 5, "body"],
     "Two rules keep you out of trouble. The first is **least privilege**:",
     "The first rule that keeps you out of trouble is **least privilege**:"),
    (["lessons", "d10", "analogy"],
     "The picture breaks on cost. A real campus charges rent whether you use it or not. The cloud charges by the hour for each thing that exists,",
     "Rent is the big difference. A real campus charges it whether you use the place or not. The cloud bills by the hour for each thing that exists,"),
    (["lessons", "d10", "mistake"],
     "Learners click around a cloud console, follow a tutorial, and forget half of what they created, often in another region.",
     "Learners follow a tutorial in a cloud console and later forget half of what they created, often in another region."),
    (["lessons", "d10", "real_world"],
     "PayFlow runs checkout in three availability zones in one region, with the load balancer in public subnets and everything else private. Its CI pipeline deploys",
     "Scaled up for production, the checkout design from the worked example runs in three availability zones in one region. The load balancer sits in public subnets and everything else is private. The CI pipeline deploys"),
    (["lessons", "d10", "real_world"],
     "and a weekly cost report by tag goes to each team.",
     "and each team gets a weekly cost report by tag."),
    (["lessons", "d10", "deeper", "body"],
     "Put Days 8, 9 and 10 together by following one request to PayFlow's checkout, hop by hop.",
     "Days 8, 9 and 10 come together when you follow one request to the checkout service from the worked example, hop by hop."),
    (["lessons", "d10", "deeper", "body"],
     "Now ask where each failure would show up:",
     "Then ask where each failure would show up:"),
    (["lessons", "d10", "deeper", "body"],
     "It is also why Parts 9 to 12 matter: metrics and traces tell you which hop is slow without guessing.",
     "Parts 9 to 12 add metrics and traces, which tell you which hop is slow without guessing."),
]


def resolve(doc, path):
    """Walk to the parent of the target string; a lesson id in the path picks that lesson."""
    node = doc
    for i, key in enumerate(path[:-1]):
        if isinstance(node, list) and isinstance(key, str):
            node = next(x for x in node if x.get("id") == key)
        else:
            node = node[key]
    return node, path[-1]


def apply(fname, edits):
    path = ROOT / "content" / fname
    doc = json.loads(path.read_text())
    done = skipped = 0
    for p, old, new in edits:
        parent, key = resolve(doc, p)
        text = parent[key]
        if not isinstance(text, str):
            sys.exit(f"{fname} {p}: not a string")
        n = text.count(old)
        if n == 1:
            parent[key] = text.replace(old, new)
            done += 1
        elif n == 0 and new in text:
            skipped += 1
        else:
            sys.exit(f"{fname} {p}: old text found {n} times\n  {old[:80]}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{fname}: {done} edits applied, {skipped} already in place")


if __name__ == "__main__":
    apply("p0.json", P0)
    apply("p2.json", P2)
