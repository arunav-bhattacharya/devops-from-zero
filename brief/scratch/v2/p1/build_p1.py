#!/usr/bin/env python3
"""Build content/p1.json (Part 1, second edition) from the lesson modules l03..l07.

Run order:  python3 make_lab.py   (writes labs/linux)
            python3 capture.py    (runs every console example in Docker, writes outputs.json)
            python3 build_p1.py   (writes content/p1.json)
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[3]

import l03, l04, l05, l06, l07  # noqa: E402,E401

PART = {
    "part": 1,
    "title": "The Linux command line",
    "intro": "Every server, container and CI runner in this course runs Linux, and you drive all of them from a shell. Part 1 takes five days to make that shell feel normal: files, searching logs, chaining tools, processes and services, and scripts that fail safely. Every example runs on the same fake practice files in an Ubuntu container on your Mac, and every output shown is real.",
    "lessons": [l03.LESSON, l04.LESSON, l05.LESSON, l06.LESSON, l07.LESSON],
    "recap": [
        "The shell splits and expands your line before a program runs, and `echo` shows you the result.",
        "Paths are absolute from `/` or relative from where you are, and `rm` has no undo.",
        "grep finds lines, regular expressions describe text, and find finds files; quote every pattern.",
        "Every program has stdin, stdout and stderr, and redirection and pipes reconnect them.",
        "`sort | uniq -c | sort -rn | head`, awk, sed and jq turn logs and JSON into answers.",
        "Permissions are rwx for owner, group and others; root skips the checks, so borrow it rarely.",
        "SIGTERM asks and SIGKILL forces; Docker, systemd and Kubernetes send them in that order.",
        "systemd runs services from unit files; `systemctl` controls them and `journalctl` reads their logs.",
        "Child processes get a copy of exported variables, and PATH decides which program runs.",
        "Scripts start with a shebang and `set -euo pipefail`, quote `\"$var\"` and pass ShellCheck.",
    ],
    "flashcards": [
        {"front": "What does the shell do to `rm *.log` before rm runs?", "back": "It replaces `*.log` with the matching file names, so rm only ever sees names."},
        {"front": "What is the difference between an absolute and a relative path?", "back": "An absolute path starts at `/` and works from anywhere; a relative path starts from the current folder."},
        {"front": "How do you preview what a glob will match?", "back": "Put `echo` in front of the command, as in `echo rm *.log`."},
        {"front": "Which grep options ignore case, count, number lines and invert the match?", "back": "`-i`, `-c`, `-n` and `-v`."},
        {"front": "Why does `grep 'WARN|ERROR' app.log` find nothing?", "back": "Without `-E`, `|` is a plain character. Use `grep -E 'WARN|ERROR'`."},
        {"front": "In a regular expression, what do `.` and `*` mean?", "back": "`.` is any one character; `*` is zero or more of the item before it."},
        {"front": "What does `find . -name '*.log' -mtime +7` list?", "back": "Files named *.log that were last changed more than 7 days ago."},
        {"front": "What are file descriptors 0, 1 and 2?", "back": "stdin, stdout and stderr."},
        {"front": "What does `cmd > out.txt 2>&1` do?", "back": "It sends both normal output and error messages to out.txt."},
        {"front": "Why must sort come before `uniq -c`?", "back": "uniq only merges duplicate lines that are next to each other."},
        {"front": "What do the modes 755, 644 and 600 mean?", "back": "rwxr-xr-x, rw-r--r-- and rw-------: owner, group and others, with r=4, w=2, x=1."},
        {"front": "What do exit codes 130, 143 and 137 mean?", "back": "The process ended from Ctrl+C (SIGINT), SIGTERM or SIGKILL: 128 plus the signal number."},
        {"front": "What does `docker stop` send to a container?", "back": "SIGTERM first, then SIGKILL if it is still running after 10 seconds."},
        {"front": "What is the difference between `systemctl enable` and `systemctl start`?", "back": "enable makes it start at boot, start runs it now, and `enable --now` does both."},
        {"front": "Can a child process change its parent's environment variables?", "back": "No. It gets a copy, and its changes never flow back."},
        {"front": "Where does your SSH public key go on a server?", "back": "Into `~/.ssh/authorized_keys` of the user you log in as."},
        {"front": "What does `set -euo pipefail` do?", "back": "Exit on errors, treat unset variables as errors, and fail a pipe when any part fails."},
    ],
    "resources": [
        {"title": "Lecture 1: Course overview and the shell (Missing Semester, MIT)", "url": "https://www.youtube.com/watch?v=MSgoeuMqUmU", "kind": "watch",
         "why": "MIT's 2026 lecture on the shell from zero, with notes and exercises to match."},
        {"title": "Missing Semester 2026 lecture notes (MIT)", "url": "https://missing.csail.mit.edu/2026/", "kind": "read",
         "why": "Free notes that cover the shell, its environment, SSH and scripting in a sensible order."},
        {"title": "Lecture 4: Data wrangling (Missing Semester, MIT)", "url": "https://www.youtube.com/watch?v=sz_dsktIjt4", "kind": "watch",
         "why": "A real log taken apart with grep, sed, sort, uniq and awk, one pipe at a time."},
        {"title": "The Unix Shell (Software Carpentry)", "url": "https://swcarpentry.github.io/shell-novice/", "kind": "read",
         "why": "A gentle beginner lesson with many small exercises on files, pipes, loops and grep."},
        {"title": "The Linux Command Line, free book (William Shotts)", "url": "https://linuxcommand.org/tlcl.php", "kind": "read",
         "why": "A complete, friendly book from your first command to shell scripts, free as a PDF."},
        {"title": "The 50 most popular Linux and terminal commands (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=ZtqBQ68cfJc", "kind": "watch",
         "why": "A long course to dip into when you want to see one command used several ways."},
        {"title": "journalctl basics (Learn Linux TV)", "url": "https://www.youtube.com/watch?v=0dG3vUYt7Uk", "kind": "watch",
         "why": "A short, clear walk through reading service logs with journalctl."},
        {"title": "ShellCheck", "url": "https://www.shellcheck.net/", "kind": "docs",
         "why": "Paste any script and get each bug explained, with a wiki page per warning."},
        {"title": "jq manual", "url": "https://jqlang.org/manual/", "kind": "docs",
         "why": "The reference for every jq filter, with runnable examples."},
        {"title": "GNU grep manual", "url": "https://www.gnu.org/software/grep/manual/grep.html", "kind": "docs",
         "why": "The full story on grep options and both kinds of regular expressions."},
        {"title": "explainshell", "url": "https://explainshell.com", "kind": "read",
         "why": "Paste a long command and see which manual text explains each part."},
        {"title": "tldr pages", "url": "https://tldr.sh/", "kind": "read",
         "why": "Short, example-first help pages for hundreds of commands."},
    ],
    "quiz": [
        {"q": "You are in `/work/logs/archive`. Which path reaches `/work/app.log`?",
         "options": ["`../app.log`", "`../../app.log`", "`/app.log`", "`~/app.log`"],
         "answer": 1,
         "why": "One `..` climbs to `/work/logs` and the second to `/work`, where app.log lives."},
        {"q": "Which command lists the files under `server` that are larger than 1 MB?",
         "options": ["`find server -type f -size +1M`", "`grep -r -size +1M server`", "`ls -lh server | grep M`", "`du -sh server -min 1M`"],
         "answer": 0,
         "why": "find tests every file under a folder, and `-size +1M` keeps those over 1 MB."},
        {"q": "`grep -c 200 app.log` prints 16, but `grep -c -w 200 app.log` prints 14. Why the difference?",
         "options": ["`-w` skips the first and last lines", "`-w` ignores lines in upper case",
                     "Two lines contain 200 inside a longer word", "`-c` counts words, not lines"],
         "answer": 2,
         "why": "`1200ms` and `2001` contain 200, and `-w` only matches 200 standing alone as a word."},
        {"q": "Which pipeline counts requests per status code (field 9), most common first?",
         "options": ["`awk '{print $9}' access.log | uniq -c | sort -rn`", "`sort -k 9 access.log | uniq -c | sort -rn | head`",
                     "`cut -d ' ' -f 9 access.log | sort -rn | uniq`", "`awk '{print $9}' access.log | sort | uniq -c | sort -rn`"],
         "answer": 3,
         "why": "Sort first so uniq can count neighbours, then sort the counts as numbers in reverse."},
        {"q": "What does `2> /dev/null` do at the end of a command?",
         "options": ["Throws away the error messages", "Throws away the normal output",
                     "Saves errors into a file called null", "Stops the command on its first error"],
         "answer": 0,
         "why": "It points stderr (2) at /dev/null, which discards everything written to it."},
        {"q": "`kill 4242` did not stop a process, even after a minute. What is the usual next step?",
         "options": ["`sudo kill 4242`", "`kill -9 4242`", "`kill -HUP 4242`", "Reboot the machine"],
         "answer": 1,
         "why": "The process is ignoring SIGTERM, so SIGKILL (9), which cannot be caught, is the last resort."},
        {"q": "`ls -ld reports` shows `drwxr-x---`, owned by `app:ops`. User sam is not in ops. What can sam do?",
         "options": ["Nothing: no listing and no entry", "List the names but not enter it",
                     "Enter it and read files by name", "Create new files inside it"],
         "answer": 0,
         "why": "The others triplet is `---`, so sam has no read, write or execute rights on the folder."},
        {"q": "A deploy script runs `./build.sh | tee build.log` and then deploys. It deploys even when the build fails. Which line at the top stops it?",
         "options": ["`set -u`", "`set -eo pipefail`", "`trap 'rm -f build.log' EXIT`", "`chmod +x build.sh`"],
         "answer": 1,
         "why": "With pipefail the pipe fails when build.sh fails, and -e then stops the script."},
        {"q": "A team made 40 deployments last month, and 6 of them needed a hotfix or a rollback. Which DORA metric is 15 percent?",
         "options": ["Deployment frequency", "Change lead time", "Change fail rate", "Failed deployment recovery time"],
         "answer": 2,
         "why": "Change fail rate is the share of deployments that needed immediate action: 6 of 40 is 15 percent.",
         "from": "Part 0"},
        {"q": "You installed tree inside `docker run -it --rm ubuntu:24.04 bash`, typed exit, and ran the same command again. Why is tree missing now?",
         "options": ["tree only works on a Mac", "apt needs sudo inside a container",
                     "The image updated itself overnight", "`--rm` deleted the container; each run starts clean"],
         "answer": 3,
         "why": "Each run makes a new container from the unchanged image, and `--rm` removed the old one with its changes.",
         "from": "Part 0"},
    ],
}


def main():
    out = ROOT / "content/p1.json"
    out.write_text(json.dumps(PART, indent=1, ensure_ascii=False) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
