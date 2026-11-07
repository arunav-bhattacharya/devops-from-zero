#!/usr/bin/env python3
"""Human-writing pass (blog mode) on content/p1.json, lessons d03 to d07 plus part fields.

Each edit is (lesson id or "part", path to a prose field, old, new). When old is None the whole
field is replaced; otherwise old must occur exactly once in the field. Only prose fields are touched.
Run: python3 brief/scratch/v3/p1/humanize.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
PATH = ROOT / "content/p1.json"

E = []


def ed(where, path, old, new):
    E.append((where, path, old, new))


# ---------------------------------------------------------------- part level
ed("part", ("intro",), None,
   r"""Every server, container and CI runner in this course runs Linux, and you drive all of them from a shell. Part 1 spends five days making that shell feel ordinary: files, searching logs, chaining tools, processes and services, and scripts that stop when something fails. You do all of it in an Ubuntu container on your Mac, on one set of fake practice files. Every output printed in the lessons is real output from those files.""")
ed("part", ("recap", 2), None,
   r"""grep matches lines with regular expressions, find picks files by name, size or age, and every pattern goes in quotes.""")
ed("part", ("recap", 7), None,
   r"""systemd keeps services running from unit files; you drive it with `systemctl` and read the logs with `journalctl`.""")
ed("part", ("quiz", 5, "why"), None,
   r"""The process is ignoring SIGTERM. SIGKILL (9) cannot be caught, so it is the last resort.""")
ed("part", ("resources", 9, "why"), None,
   r"""Every grep option, and both kinds of regular expression, in one reference.""")

# ---------------------------------------------------------------- d03
L = "d03"
ed(L, ("goal",), None,
   r"""By the end you can use a Linux shell, read a command line, look up options, get around the file system, and copy, move and delete files safely.""")
ed(L, ("guess", "why"), r"""That is why `echo *.log` is a safe way to preview what a command will get.""",
   r"""You can watch that step safely: `echo *.log` prints the names a command would get.""")
ed(L, ("sections", 0, "body"), r"""So when you type `ls -l` and press Enter""", r"""When you type `ls -l` and press Enter""")
ed(L, ("sections", 0, "body"),
   r"""The two shells, zsh and bash, agree on almost everything in this part, and where they differ, the lesson says so. All the output you see comes from bash on Ubuntu, because that is what you meet on servers, in CI runners and inside Docker images. So you practise in Linux, not in your Mac's own shell. Small differences between the Mac's tools and the Linux ones bite exactly when you are in a hurry.""",
   r"""zsh and bash agree on almost everything in this part, and the lessons point out the few places where they differ. All the output you see comes from bash on Ubuntu, because servers, CI runners and Docker images give you that. This is why you practise inside a Linux container and not in your Mac's own shell. The Mac's tools also differ from the Linux ones in small ways, and you tend to find those differences when you are in a hurry.""")
ed(L, ("sections", 1, "body"), r"""The script runs one `docker run` command. Its parts:""",
   r"""Inside, the script is a single `docker run` command:""")
ed(L, ("sections", 1, "body"),
   r"""Anything you install or create elsewhere in the container is gone when you exit. That is a feature: you cannot break anything for long.""",
   r"""Anything you install or create anywhere else in the container is gone when you exit. While you learn, that helps: if you break something, type `exit` and start again.""")
ed(L, ("sections", 1, "body"), r"""Your prompt looks like""", r"""Your prompt will look something like""")
ed(L, ("sections", 2, "body"),
   r"""Before any program runs, the shell does some work on your line. It splits the line on spaces into words. The first word is the program to run. Every other word becomes an argument: a plain string handed to that program. Take this line: `ls -l -h server/var/log`.""",
   r"""Before any program starts, the shell takes your line apart. It splits it on spaces into words. The first word is the program to run, and every other word becomes an argument: a plain string handed to that program. Take `ls -l -h server/var/log`.""")
ed(L, ("sections", 2, "body"), r"""As a Kotlin developer you know this shape. It is""",
   r"""You know this shape from Kotlin. It is""")
ed(L, ("sections", 2, "body"), r"""This is only a habit, which is why each tool's help matters (next section).""",
   r"""Nothing forces a program to follow this habit, so check the tool's help when you are unsure (next section).""")
ed(L, ("sections", 2, "body"),
   r"""Spaces split words, so a file name with a space is a trap.""",
   r"""Because spaces split words, a file name with a space in it causes trouble.""")
ed(L, ("sections", 2, "body"), r"""Easier still: never put spaces in file names you create.""",
   r"""Better still, keep spaces out of the file names you create.""")
ed(L, ("sections", 3, "body"),
   r"""Nobody remembers every option. Experienced engineers look things up all day. You have three places to look:""",
   r"""Nobody remembers every option, and experienced engineers look things up all day. Look in one of these places:""")
ed(L, ("sections", 3, "body"), r"""Start with the usage line.""", r"""Read the usage line first.""")
ed(L, ("sections", 3, "body"),
   r"""When you meet a long command on the internet, paste it into [explainshell](https://explainshell.com). It shows which part of the manual explains each word.""",
   r"""Found a long command on the internet that you cannot read? Paste it into [explainshell](https://explainshell.com), which shows the manual text for each word.""")
ed(L, ("sections", 4, "body"), r"""These folders matter most for DevOps work:""",
   r"""In DevOps work you will visit these folders most:""")
ed(L, ("sections", 4, "body"), r"""Four short forms help:""", r"""You will type these short forms all day:""")
ed(L, ("sections", 4, "body"),
   r"""Two keys save a lot of typing. Tab completes a file or command name, so you type less and make fewer typos.""",
   r"""Learn two keys early. Tab completes a file or command name, which also means fewer typos.""")
ed(L, ("sections", 5, "body"), r"""Five commands do most of the work:""", r"""File work comes down to a handful of commands:""")
ed(L, ("sections", 5, "body"),
   r"""The file is gone the moment you press Enter, and this trips most people up once. Three habits keep you safe:""",
   r"""The file is gone the moment you press Enter, and most people learn this by losing a file they wanted. These habits keep that from happening to you:""")
ed(L, ("sections", 5, "body"),
   r"""Error messages are short and honest, so read them. Without `-p`, `mkdir a/b/c` fails with `No such file or directory`, because `a/b` does not exist yet. Given a folder, `rm` refuses with `Is a directory`. And `rmdir` on a folder with files in it says `Directory not empty`.""",
   r"""Read the error messages, because they are short and exact. Without `-p`, `mkdir a/b/c` fails with `No such file or directory`, because `a/b` does not exist yet. Point `rm` at a folder and it refuses with `Is a directory`. Run `rmdir` on a folder with files in it and you get `Directory not empty`.""")
ed(L, ("sections", 6, "body"), r"""Three symbols cover nearly every use:""", r"""You will rarely need more than these symbols:""")
ed(L, ("sections", 6, "body"),
   r"""The program never sees the pattern, only the names. That makes `echo` the best debugging tool in the shell. Put it in front""",
   r"""The program never sees the pattern, only the names, and that is what makes `echo` such a good debugging tool. Put it in front""")
ed(L, ("analogy",),
   r"""Where it breaks: a good waiter asks when an order makes no sense, but bash passes a pattern that matches nothing straight through without a word.""",
   r"""A good waiter would come back and ask if you ordered a special the kitchen does not have today. Bash never asks: a pattern that matches nothing goes to the kitchen exactly as you typed it.""")
ed(L, ("worked", "steps", 6, "say"),
   r"""Delete with the same care. Preview with `echo`, delete the files, then remove the empty folder with `rmdir`. Plain `rm` refuses a folder. `rm -r` removes it and everything inside, with no undo, so you only use it once you are sure.""",
   r"""Deleting gets the same care: preview with `echo`, delete the files, then remove the empty folder with `rmdir`. Plain `rm` refuses a folder. `rm -r` removes it and everything inside, with no undo, so save it for when you are sure.""")
ed(L, ("mistake",), None,
   r"""You delete with a glob or a path you never checked. One stray space, as in `rm -r old logs`, deletes two folders, `old` and `logs`, and nothing brings them back. Before any delete, run `pwd`, preview the line with `echo` and read it once more.""")
ed(L, ("real_world",), None,
   r"""If you get paged at night, your first minutes on the server look a lot like this lesson. You run `pwd` and `ls -lt /var/log/...` to find the newest log, and copy it aside before log rotation moves it away. In code reviews of deploy scripts, "what does this glob expand to?" is a normal question, and someone answers it with `echo`.""")
ed(L, ("explain_back", "prompt"), None,
   r"""In 3 to 4 sentences, describe what happens between pressing Enter on `rm *.log` and the files disappearing. Mention globs, arguments and why `echo` helps.""")
ed(L, ("explain_back", "answer"),
   r"""Putting `echo` in front prints the exact list rm would get, which is the safe way to check a glob before deleting anything for good.""",
   r"""Putting `echo` in front prints the exact list rm would get, so you can check the glob before anything is gone for good.""")
ed(L, ("interview", 2, "a"), r"""If man pages are installed, `man command` and then `/` to search for the flag.""",
   r"""If man pages are installed, I open `man command` and press `/` to search for the flag.""")
ed(L, ("deeper", "body"),
   r"""Why is `cd` built into the shell when `ls` is a program file? The answer explains a rule you will meet again on Day 7.

Ask the shell itself. `type cd` prints""",
   r"""`cd` is built into the shell, while `ls` is a program file. The reason is a rule you will meet again on Day 7.

You can ask the shell which is which: `type cd` prints""")
ed(L, ("deeper", "body"), r"""A child can change its own working directory, but it has no way to change its parent's.""",
   r"""A child can change its own, but it has no way to change its parent's.""")
ed(L, ("deeper", "body"),
   r"""So imagine `cd` were a program. The shell would start it, it would change its own directory, and then it would exit. Your shell would still be exactly where it was. The only way to move the shell is for the shell to do it itself, so `cd` has to be a builtin. The same is true of a few""",
   r"""Now imagine `cd` were a program. The shell would start it, it would change its own directory, and then it would exit. Your shell would not have moved at all. Only the shell can move the shell, so `cd` has to be a builtin. The same goes for a few""")
ed(L, ("deeper", "body"),
   r"""The rule "a child cannot change its parent" has a practical side. A script that runs `cd /var/log` does not move your terminal, and Day 7 shows that a script that sets a variable cannot change your terminal's variables either.""",
   r"""You will run into this rule in scripts. A script that runs `cd /var/log` does not move your terminal, and Day 7 shows that a script cannot change your terminal's variables either.""")
# factual fix: the lab container has no zsh until you install it
ed(L, ("deeper", "body"),
   r"""One more difference is worth knowing before you write loops over files. In bash, `*` only matches names inside one folder. In zsh, `**` also means "any number of folders". In the container, `zsh -c 'echo server/**/*.sql'` prints""",
   r"""Before you write loops over files, know that bash and zsh treat `**` differently. In bash, `*` only matches names inside one folder. In zsh, `**` also means "any number of folders". The container has no zsh, so install it first with `apt-get install -y zsh`. Then `zsh -c 'echo server/**/*.sql'` prints""")
ed(L, ("deeper", "body"), r"""Bash can do the same after `shopt -s globstar`, but that is off by default. So scripts""",
   r"""Bash can do the same after `shopt -s globstar`, but that is off by default, so scripts""")
ed(L, ("deeper", "body"), r"""Finally, a habit for when a command surprises you: ask the shell""",
   r"""When a command surprises you, ask the shell""")

ed(L, ("sections", 0, "body"), r"""Linux servers and containers almost always use bash.""",
   r"""Linux servers usually use bash, and so do the containers in this course.""")

# ---------------------------------------------------------------- d04
L = "d04"
ed(L, ("sections", 0, "body"),
   r"""Before you search a file, look at it. Four commands cover that, and the right one depends on the file's size:""",
   r"""Before you search a file, look at it. Check its size first: `wc -l app.log` prints `37 app.log`, so the file has 37 lines. The size decides which command makes sense:""")
ed(L, ("sections", 0, "body"),
   "\n\nFirst check how big a file is with `wc -l app.log`, which prints `37 app.log`: the file has 37 lines.", "")
ed(L, ("sections", 1, "body"),
   r"""Start with plain words; the pattern language comes later. Each option below answers one question you ask during an incident,""",
   r"""For now the patterns are plain words. Each option below answers a question you will ask during an incident,""")
ed(L, ("sections", 1, "body"), r"""The grep command also sets an exit code,""", r"""grep also sets an exit code,""")
ed(L, ("sections", 2, "body"),
   r"""A matching line rarely tells the whole story. You want the lines around it, and three options give them:""",
   r"""One matching line rarely explains a failure on its own. You want the lines around it:""")
ed(L, ("sections", 2, "body"), r"""It also searches many files at once.""", r"""grep also searches many files at once.""")
ed(L, ("sections", 2, "body"), r"""Two options pair well with `-r`:""",
   r"""Across many files you often want a summary instead of every line:""")
ed(L, ("sections", 2, "body"),
   r"""Finally, `-o` prints only the part of the line that matched, not the whole line. That turns grep into an extractor, which becomes useful once your pattern is more than a plain word.""",
   r"""The `-o` option prints only the part of the line that matched. With a plain word that is not much use, but with the patterns in the next section it turns grep into an extractor.""")
ed(L, ("sections", 3, "body"),
   r"""A plain word is already a regex: it matches itself. A handful of symbols add power, and these work in plain grep:""",
   r"""A plain word is already a regex that matches itself. Add a few special symbols and one pattern can match many strings. These work in plain grep:""")
ed(L, ("sections", 3, "body"),
   r"""Here is the classic trap. Without `-E`, `grep 'WARN|ERROR'` treats `|` as a normal character and finds nothing; with `-E` it finds 8 lines.""",
   r"""That is the trap from the question at the top of this lesson. Without `-E`, `grep 'WARN|ERROR'` treats `|` as a normal character and finds nothing. With `-E` it finds 8 lines.""")
ed(L, ("sections", 4, "body"),
   r"""the shell expands the unquoted glob into file names and leaves the quoted regex alone for grep. Quoting decides who gets each symbol: the shell or the tool.""",
   r"""the shell expands the unquoted glob into file names. It leaves the regex alone because the regex sits in single quotes, so grep receives it untouched.""")
ed(L, ("sections", 5, "body"), r"""It can also act on what it finds:""", r"""find can also act on what it finds:""")
ed(L, ("sections", 5, "body"), r"""The last section explains why.""", r"""The next section says why.""")
ed(L, ("sections", 6, "body"),
   r"""Most of today's commands behave the same on both, but three details differ:""",
   r"""Most of today's commands behave the same on both. These do not:""")
ed(L, ("sections", 6, "body"),
   r"""exist on both. That is why the course runs everything in the container: what you practise there is what servers and CI runners have. When you copy a one-liner into a script for your Mac, test it there once.""",
   r"""exist on both, so most of what you learn carries over. The course still runs everything in the container, because that is what servers and CI runners have. If you copy a one-liner into a script for your Mac, test it on the Mac once.""")
ed(L, ("analogy",), None,
   r"""Running grep is like dragging a highlighter down a printout and then cutting out only the marked lines. The find command is a filing clerk who pulls every folder that fits a description, such as "older than a week", without opening any of them. Ask a real clerk to shred that pile and they would check with you first. `find -delete` never checks.""")
ed(L, ("worked", "steps", 1, "say"), r"""One file is not the whole story.""",
   r"""Checkout called payments-api, so other logs matter too.""")
ed(L, ("mistake",), None,
   r"""You type `find . -name *.log` without quotes. It looks right, but the shell expands the glob first, and with one .log file in the folder, find silently searches for that one name. Put every pattern in single quotes: `find . -name '*.log'`, `grep -E '5[0-9]{2}'`.""")
ed(L, ("real_world",), None,
   r"""When a customer quotes a reference, nobody knows yet which service failed. Teams with many small services prepare for that: each request gets an ID where it enters, and every service logs it. On-call pastes the ID into a search and gets the timeline from the worked example. That search is grep over SSH on a few servers and a central log store on hundreds (Day 47), with the same questions and the same regex.""")
ed(L, ("explain_back", "prompt"), None,
   r"""Explain the difference between a glob and a regular expression in 3 to 4 sentences. Say who reads each one and what `*` means in each.""")
ed(L, ("deeper", "body"),
   r"""Watching a log live is a daily task, and two details make it work. Try it with two terminals.""",
   r"""Try this with two terminals: watch a log for errors as new lines arrive.""")
ed(L, ("deeper", "body"), r"""Now rotation. Busy servers""", r"""Then there is rotation. Busy servers""")
ed(L, ("deeper", "body"),
   r"""One more trap from the same family: deleting a big log that a program still has open does not free the disk space.""",
   r"""Deleting a big log that a program still has open has a similar surprise: it does not free the disk space.""")

# ---------------------------------------------------------------- d05
L = "d05"
ed(L, ("sections", 0, "body"),
   r"""Run `ls app.log nosuch` and both look the same on screen: one error line and one result line. They travel separately, though, and the rest of this lesson is about steering them.""",
   r"""Run `ls app.log nosuch` and you get one error line and one result line that look alike on screen. They still travel separately, and you can send each one somewhere else.""")
ed(L, ("sections", 1, "body"), r"""Two traps catch everyone:""", r"""Two mistakes here are very common:""")
ed(L, ("sections", 1, "body"),
   r"""1. A single `>` empties the file at once, before the command runs. `sort copy.log > copy.log` leaves you with an empty file. Type `set -o noclobber` and the shell refuses instead: `bash: notes.txt: cannot overwrite existing file`.""",
   r"""1. A single `>` empties the file at once, before the command runs, so `sort copy.log > copy.log` leaves you with an empty file. After `set -o noclobber` the shell refuses to overwrite a file, with a message like `bash: notes.txt: cannot overwrite existing file`.""")
# factual precision: sort must read all its input before it prints anything
ed(L, ("sections", 2, "body"),
   r"""No step waits for the previous one to finish, which is why `tail -f app.log | grep ERROR` works on a log that never ends.""",
   r"""Most steps do not wait for the previous one to finish, which is why `tail -f app.log | grep ERROR` works on a log that never ends. The sort command is the exception: it has to read every line before it can print the first.""")
ed(L, ("sections", 2, "body"), r"""A step you have checked is a step you will not debug later.""",
   r"""Checking each step as you go is far quicker than debugging the whole chain at the end.""")
ed(L, ("sections", 2, "body"), r"""Two operators run a command based on the last exit code:""",
   r"""The operators `&&` and `||` look at the last exit code to decide whether the next command runs:""")
ed(L, ("sections", 3, "body"), r"""These filters turn lines into numbers:""", r"""These filters do most of the counting and slicing:""")
ed(L, ("sections", 3, "body"), r"""The cut command has a sharp edge: every single space is a separator.""",
   r"""The cut command has one catch: it treats every single space as a separator.""")
ed(L, ("sections", 4, "body"), r"""Three patterns cover most DevOps work:""",
   r"""Most of what you will do with awk looks like one of these:""")
ed(L, ("sections", 5, "body"), r"""The `-i` option is where Mac and Linux part ways.""",
   r"""Mac and Linux disagree about `-i`.""")
ed(L, ("sections", 6, "body"), r"""Likewise, `wc -l $(grep -r -l 7f3a9c logs)`""", r"""In the same way, `wc -l $(grep -r -l 7f3a9c logs)`""")
ed(L, ("analogy",),
   r"""Where it breaks: on a real line a broken part travels down the belt, but here error messages leave by a side door (stderr) and never reach the next worker.""",
   r"""A real line would send a broken part down the belt with the good ones. A pipeline does not: error messages leave by a side door (stderr), and the next worker never sees them.""")
ed(L, ("worked", "steps", 4, "say"), None,
   r"""The 404s (client errors) are a separate problem. The top paths are files this shop never had, and grouping the 404s by IP shows that one client sent almost all of them. That is a scanner probing for weak spots, not a broken link on the site.""")
ed(L, ("mistake",), None,
   r"""`sort app.log > app.log` looks as if it sorts the file in place. It empties it instead, and `sed 's/a/b/' f > f` does the same: the shell clears the file before the command starts, so the data is gone. Write to a new file and move it into place, as in `sort f > f.new && mv f.new f`, or use the tool's own in-place option.""")
ed(L, ("real_world",), None,
   r"""Traffic jumps, and the first questions are "who is calling us?" and "what is failing?". The first answer often comes from the worked example's pipeline, run on a load balancer log before anyone opens a dashboard. Engineers also pipe Kubernetes JSON into jq every day, for example to list the apps that keep restarting.""")
ed(L, ("explain_back", "prompt"), None,
   r"""Walk through `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -n 5` in 3 to 4 sentences. Cover the streams, why sort comes before uniq, and what the last two steps add.""")
ed(L, ("explain_back", "answer"), None,
   r"""The awk step prints the first field of each line, the client IP, and each pipe feeds that stream into the next program's stdin. Then sort puts identical IPs next to each other, which uniq needs, because it only merges neighbouring duplicates. With `-c`, uniq prints each IP once with its count. The last two steps rank the result: `sort -rn` orders the counts from highest to lowest as numbers, and `head -n 5` keeps the top five.""")
ed(L, ("deeper", "body"),
   r"""Many questions need all of them at once: a total, a count per group, a ranking. The `-s` (slurp) option reads every value into one array first, and then the full language opens up.""",
   r"""A total or a count per group needs all of them at once. The `-s` (slurp) option reads every value into one array first, so a single filter can see them all.""")
ed(L, ("deeper", "body"),
   r"""The last two show the habit worth keeping. Let jq turn JSON into plain lines, then use the text tools you already know. You do not need to learn all of jq; `select`, string templates and `@tsv` go a long way.""",
   r"""The last two examples are the habit to keep: let jq turn JSON into plain lines, then use the text tools you already know. You do not need all of jq. With `select`, string templates and `@tsv` you can answer most everyday questions.""")
ed(L, ("deeper", "body"), r"""Missing fields are worth a note.""", r"""Watch out for missing fields.""")
ed(L, ("deeper", "body"),
   r"""A practice idea for later: when you meet `kubectl get pods -o json` on Day 31, the filters from today work almost unchanged.""",
   r"""Keep this for Day 31. When you meet `kubectl get pods -o json` there, today's filters work almost unchanged.""")

# ---------------------------------------------------------------- d06
L = "d06"
ed(L, ("sections", 0, "body"), r"""belongs to a user. Two commands tell you who you are:""",
   r"""belongs to a user. To see who you are:""")
ed(L, ("sections", 0, "body"),
   r"""It hides the real problem, such as a wrong owner or folder, and the files it creates belong to root, so your normal tools cannot change them later. When something says "Permission denied", ask why before you reach for sudo.""",
   r"""It hides the real problem, such as a wrong owner or folder. The files it creates also belong to root, so your normal user cannot change them later. When something says "Permission denied", find out why before you reach for sudo.""")
ed(L, ("sections", 0, "body"), r"""In the container you are root, so make a normal user to feel a denial:""",
   r"""In the container you are root, so to see a denial for yourself, make a normal user:""")
ed(L, ("sections", 1, "body"),
   r"""On a directory the same letters mean something else, and this trips most people up:""",
   r"""On a directory the same letters mean something else, and the meanings are not what you would guess:""")
ed(L, ("sections", 2, "body"),
   r"""Two habits from real teams. Never fix a permission problem with `chmod 777`, which lets every user change the file. And do not run containers as root.""",
   r"""Never fix a permission problem with `chmod 777`, which lets every user change the file. And avoid running containers as root.""")
ed(L, ("sections", 3, "body"), r"""These commands show processes:""", r"""To look at processes:""")
ed(L, ("sections", 4, "body"), r"""Four matter most:""", r"""These are the ones you will meet:""")
ed(L, ("sections", 4, "body"), r"""That pair is how the container world stops programs. The `docker stop` command""",
   r"""Containers get stopped with the same pair. The `docker stop` command""")
ed(L, ("sections", 5, "body"),
   r"""A service is a program that runs in the background without a terminal: a web server, a database, a queue worker.""",
   r"""A service is a program that runs in the background without a terminal, such as a web server or a queue worker.""")
ed(L, ("sections", 5, "body"),
   r"""So for services you use a small Ubuntu virtual machine made with Multipass, which the task sets up.""",
   r"""That is why the task uses a small Ubuntu virtual machine, made with Multipass, for the systemd part.""")
ed(L, ("sections", 6, "body"), r"""Five quick checks answer "is this machine healthy?":""",
   r"""When you need to know whether a machine is healthy, start with these:""")
ed(L, ("analogy",),
   r"""Where it breaks: staff cannot ignore the manager, but a program can ignore SIGTERM, and only SIGKILL cannot be ignored.""",
   r"""Real staff have to listen to the manager. A program can ignore SIGTERM completely, which is why SIGKILL exists: no process can ignore a power cut.""")
ed(L, ("worked", "steps", 2, "say"), r"""The worker PIDs change while the server never stops listening.""",
   r"""The worker PIDs change, but the server never stops listening.""")
ed(L, ("worked", "steps", 4, "say"), None,
   r"""On a real server, systemd would do all of this for you. The container cannot: first the command is missing, and after you install systemd, it refuses to work because it is not PID 1.""")
ed(L, ("mistake",), None,
   r"""Reaching for `kill -9` or `sudo` first is the wrong move. SIGKILL gives the program no chance to finish requests or close files. Using sudo hides the real cause of a permission error and leaves root-owned files behind. Send SIGTERM and wait a few seconds. For "Permission denied", read `ls -l` and fix the owner or the one missing bit.""")
ed(L, ("real_world",), None,
   r"""A rollout stops the old version of a service, and systemd and Kubernetes stop it the same way: SIGTERM, a grace period, then SIGKILL. In a payments system, code reviews check that a service handles SIGTERM by finishing the payments in flight before it exits. When a machine misbehaves, on-call starts with `systemctl status`, `journalctl -u NAME --since`, `df -h` and `ss -tlnp`.""")
ed(L, ("explain_back", "prompt"), None,
   r"""What happens when you run `docker stop` or `systemctl stop` on a program? Answer in 3 to 4 sentences, and mention SIGTERM, SIGKILL, the grace period and exit code 137.""")
ed(L, ("interview", 2, "a"), r"""I check the usual suspects:""", r"""Then I rule out the common causes:""")
ed(L, ("deeper", "body"),
   r"""Learning to read `systemctl status` pays off on every server you touch. The course container cannot run systemd, so this walk-through uses the example from the official systemctl manual, for a Bluetooth service:""",
   r"""You will read `systemctl status` on every server you touch, and it packs a lot into a few lines. The course container cannot run systemd, so this walk-through uses the Bluetooth service example from the official systemctl manual:""")
ed(L, ("deeper", "body"), r"""Two settings in your own unit file connect to today's signals.""",
   r"""Two lines in `hello-worker.service` decide how systemd uses today's signals.""")

# ---------------------------------------------------------------- d07
L = "d07"
ed(L, ("sections", 0, "body"), r"""The lab shows the difference:""", r"""Try it in the lab:""")
ed(L, ("sections", 0, "body"),
   r"""The copy only flows down. A child gets a copy of its parent's environment, and nothing the child changes ever flows back up. That is why a script that runs `export` cannot change your terminal, just as Day 3's `cd` inside a script cannot move you.""",
   r"""A child gets a copy of its parent's environment, and nothing the child changes ever flows back up. So a script that runs `export` cannot change your terminal, for the same reason that Day 3's `cd` inside a script cannot move you.""")
ed(L, ("sections", 0, "body"),
   r"""This is how one hello-devops image runs everywhere: it reads""",
   r"""The environment is also how one hello-devops image runs everywhere. It reads""")
ed(L, ("sections", 1, "body"), r"""Two commands show what will run:""", r"""To see what will actually run:""")
ed(L, ("sections", 2, "body"),
   r"""Two lookups help when something is missing. `dpkg -S /usr/bin/jq` tells you which package owns a file; here it prints `jq: /usr/bin/jq`. And [command-not-found.com](https://command-not-found.com) tells you which package provides a command on each system.""",
   r"""To find out which package a file came from, run `dpkg -S /usr/bin/jq`; here it prints `jq: /usr/bin/jq`. When a command is missing, [command-not-found.com](https://command-not-found.com) tells you which package provides it on each system.""")
ed(L, ("sections", 3, "body"), r"""Four more tools make SSH pleasant:""", r"""These make everyday SSH use much easier:""")
ed(L, ("sections", 4, "body"), r"""Three things make it runnable:""", r"""To make one runnable:""")
ed(L, ("sections", 5, "body"), r"""Loops repeat work:""", r"""For repeated work, use a loop:""")
ed(L, ("sections", 6, "body"), r"""Here is why that matters: with an empty `DIR`,""",
   r"""This guard matters most before a delete: with an empty `DIR`,""")
ed(L, ("sections", 6, "body"), r"""Finally, run ShellCheck on every script:""", r"""Run ShellCheck on every script:""")
ed(L, ("analogy",),
   r"""Where it breaks: a real child can phone home with news, while a Linux process has no way at all to edit its parent's environment.""",
   r"""Real families are not that strict: a child can phone home and read out the change. A Linux process has no such phone. It cannot touch its parent's environment at all.""")
ed(L, ("worked", "steps", 4, "say"), r"""Readiness matters too. Restart the app""", r"""Now break readiness. Restart the app""")
ed(L, ("worked", "steps", 5, "say"),
   r"""fails the job on any exit code other than 0, with no extra wiring. This is the whole point of exit codes: one number that every tool understands.""",
   r"""fails the job on any exit code other than 0. You add no extra code for that, because the exit code is all CI looks at.""")
ed(L, ("mistake",), None,
   r"""`rm $file` works until the value holds a space or a `*`. Then the shell splits or expands it, and the command hits the wrong files. Write `"$var"` every time, and let ShellCheck point out the ones you missed.""")
ed(L, ("real_world",), None,
   r"""The last step of a deploy pipeline is often a smoke test much like `healthcheck.sh`. It is a short strict-mode script that exits non-zero and stops the rollout when the new version does not answer. In a well-run team, engineers reach servers over SSH with keys and a shared config file, never with passwords. The same teams run ShellCheck in CI on every script in the repository.""")
ed(L, ("explain_back", "prompt"), None,
   r"""In 3 to 4 sentences, say what `set -euo pipefail` protects against. Give one example for each part, and one case where you need `|| true`.""")
ed(L, ("deeper", "body"),
   r"""Three details make the difference between a script that works on your laptop and one that works everywhere.

First, the Mac's own bash is old. macOS still ships""",
   r"""A script that works on your laptop can still break on a server or in CI.

Start with the version. The Mac's own bash is old: macOS still ships""")
ed(L, ("deeper", "body"), r"""Second, strict mode is a trade-off,""", r"""Strict mode is also a trade-off,""")
ed(L, ("deeper", "body"), r"""The practical answer most teams use is to keep strict mode""",
   r"""The usual answer is to keep strict mode""")
ed(L, ("deeper", "body"), r"""Third, when a script misbehaves, make it show its work.""",
   r"""When a script misbehaves, make it show its work.""")
ed(L, ("deeper", "body"), r"""A last habit for scripts that run in CI: send messages""",
   r"""For scripts that run in CI, send messages""")



# second pass
ed("d05", ("sections", 5, "body"),
   r"""The xargs tool turns lines on stdin into arguments for a command. Some commands, like `ls` and `rm`, ignore stdin and only take arguments. So""",
   r"""Some commands, like `ls` and `rm`, ignore stdin and only take arguments. For those there is xargs, which turns lines on stdin into arguments for a command. So""")
ed("d05", ("sections", 6, "body"), r"""The jq tool does for JSON what grep, cut and awk do for text.""",
   r"""For JSON you use jq, which does what grep, cut and awk do for text.""")
ed("d06", ("deeper", "body"), r"""The nginx unit file you read in the worked example uses the same setting.""",
   r"""The nginx unit file from the worked example uses the same setting.""")
ed("d07", ("sections", 0, "body"), r"""The environment is also how one hello-devops image runs everywhere. It reads""",
   r"""The environment is also how one hello-devops image runs everywhere. The app reads""")



ed("d05", ("goal",), None,
   r"""By the end you can join programs with pipes, send output and errors to files, and get answers from logs with sort, uniq, cut, awk, sed, xargs and jq.""")
ed("d06", ("goal",), None,
   r"""By the end you can read and change permissions, stop a process with the right signal, run a program as a systemd service, and check disk, memory and ports.""")
ed("d07", ("goal",), None,
   r"""By the end you can pass environment variables to programs, explain PATH, install packages, log in with SSH keys, and write a bash script that CI can trust.""")


# ---------------------------------------------------------------- apply
def get_parent(obj, path):
    for k in path[:-1]:
        obj = obj[k]
    return obj


def main():
    data = json.loads(PATH.read_text())
    lessons = {L["id"]: L for L in data["lessons"]}
    for where, path, old, new in E:
        root = data if where == "part" else lessons[where]
        parent = get_parent(root, path)
        cur = parent[path[-1]]
        assert isinstance(cur, str), (where, path)
        if old is None:
            parent[path[-1]] = new
        else:
            n = cur.count(old)
            assert n == 1, f"{where} {path}: old text found {n} times: {old[:60]!r}"
            parent[path[-1]] = cur.replace(old, new)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"applied {len(E)} edits to {PATH}")


if __name__ == "__main__":
    main()
