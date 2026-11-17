"""Book-voice rewrite of Part 1's own fields. Writer: ta. Run from the repo root."""
import json

PATH = "content/p1.json"
P = json.load(open(PATH))

P["intro"] = "Every server, container and CI runner in this course runs Linux, and you drive all of them by typing into a shell. Part 1 spends five days making that feel ordinary, in an office building where a clerk reads your notes. You learn files and folders, searching logs, chaining tools, workers and keys, and checklists that stop when something fails. You do all of it in an Ubuntu container on your Mac, on one set of fake practice files from a pretend online shop. Every output printed in the lessons is real output from those files."

P["recap"] = [
    "The shell splits and expands your line before a program runs, and `echo` shows you the result.",
    "Paths are absolute from `/` or relative from where you are, and `rm` has no undo.",
    "grep matches lines with regular expressions, find picks files by name, size or age, and every pattern goes in quotes.",
    "Every program has stdin, stdout and stderr, and redirection and pipes reconnect them.",
    "`sort | uniq -c | sort -rn | head`, awk, sed and jq turn logs and JSON into answers.",
    "Permissions are rwx for owner, group and others; root skips the checks, so borrow it rarely.",
    "SIGTERM asks and SIGKILL forces; Docker, systemd and Kubernetes send them in that order.",
    "systemd keeps services running from unit files; you drive it with `systemctl` and read the logs with `journalctl`.",
    "Child processes get a copy of exported variables, and PATH decides which program runs.",
    "Scripts start with a shebang and `set -euo pipefail`, quote `\"$var\"` and pass ShellCheck.",
]

cards = [
    ("What does the shell do to `rm *.log` before rm runs?", "It replaces `*.log` with the matching file names, so rm only ever sees names."),
    ("What is the difference between an absolute and a relative path?", "An absolute path starts at `/` and works from anywhere. A relative path starts from the folder you are in."),
    ("How do you preview what a glob will match?", "Put `echo` in front of the command, as in `echo rm *.log`."),
    ("Which grep options ignore case, count, number lines and invert the match?", "`-i`, `-c`, `-n` and `-v`."),
    ("Why does `grep 'WARN|ERROR' app.log` find nothing?", "Without `-E`, `|` is a plain character. Use `grep -E 'WARN|ERROR'`."),
    ("In a regular expression, what do `.` and `*` mean?", "`.` is any one character, and `*` is zero or more of the item before it."),
    ("What does `find . -name '*.log' -mtime +7` list?", "Files named *.log that were last changed more than 7 days ago."),
    ("What are file descriptors 0, 1 and 2?", "stdin, stdout and stderr: the in-tray, the out-tray and the complaints tray."),
    ("What does `cmd > out.txt 2>&1` do?", "It sends both normal output and error messages to out.txt."),
    ("Why must sort come before `uniq -c`?", "uniq only merges duplicate lines that are next to each other."),
    ("What do the modes 755, 644 and 600 mean?", "rwxr-xr-x, rw-r--r-- and rw-------, for owner, group and others, with r=4, w=2 and x=1."),
    ("What do exit codes 130, 143 and 137 mean?", "The process ended from Ctrl+C (SIGINT), SIGTERM or SIGKILL: 128 plus the signal number."),
    ("What does `docker stop` send to a container?", "SIGTERM first, then SIGKILL if it is still running after 10 seconds."),
    ("What is the difference between `systemctl enable` and `systemctl start`?", "enable makes it start at boot, start runs it now, and `enable --now` does both."),
    ("Can a child process change its parent's environment variables?", "No. It gets a copy, and its changes never flow back."),
    ("Where does your SSH public key go on a server?", "Into `~/.ssh/authorized_keys` of the user you log in as."),
    ("What does `set -euo pipefail` do?", "It stops on errors, treats unset variables as errors, and fails a pipe when any part fails."),
]
assert len(cards) == len(P["flashcards"])
for f, (front, back) in zip(P["flashcards"], cards):
    f["front"], f["back"] = front, back

whys = [
    "MIT's 2026 lecture on the shell from zero, with notes and exercises to match.",
    "Free notes that cover the shell, its environment, SSH and scripting in a sensible order.",
    "A real log taken apart with grep, sed, sort, uniq and awk, one pipe at a time.",
    "A gentle beginner lesson with many small exercises on files, pipes, loops and grep.",
    "A complete, friendly book from your first command to shell scripts, free as a PDF.",
    "A long course to dip into when you want to see one command used several ways.",
    "A short, clear walk through reading service logs with journalctl.",
    "Paste any script and get each bug explained, with a page for every warning.",
    "The reference for every jq filter, with examples you can run.",
    "Every grep option, and both kinds of regular expression, in one reference.",
    "Paste a long command and see which manual text explains each part.",
    "Short help pages for hundreds of commands that start with examples.",
]
assert len(whys) == len(P["resources"])
for r, w in zip(P["resources"], whys):
    r["why"] = w

Q = P["quiz"]
Q[0]["why"] = "One `..` climbs to `/work/logs`, and the second climbs to `/work`, where app.log lives."
Q[1]["why"] = "find tests every file under a folder, and `-size +1M` keeps those over 1 MB."
Q[2]["why"] = "`1200ms` and `2001` contain 200, and `-w` only matches 200 standing alone as a word."
Q[3]["why"] = "Sort first so uniq can count neighbours, then sort the counts as numbers, largest first."
Q[4]["why"] = "It points stderr (2) at /dev/null, which throws away everything written to it."
Q[5]["q"] = "`kill 4242` did not stop a process, even after a minute. What is the usual next step?"
Q[5]["why"] = "The process is ignoring SIGTERM. SIGKILL (9) cannot be caught, so it is the last resort."
Q[6]["why"] = "The others triplet is `---`, so sam has no read, write or execute rights on the folder."
Q[7]["why"] = "With pipefail the pipe fails when build.sh fails, and -e then stops the script."
Q[8]["why"] = "Change fail rate is the share of deployments that needed immediate action, and 6 of 40 is 15 percent."
Q[9]["why"] = "Each run makes a new container from the unchanged image, and `--rm` removed the old one with its changes."

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("p1 part fields written")
