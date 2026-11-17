"""Book-voice rewrite of d03 (The shell and the file system). Writer: ta. Run from the repo root."""
import json

PATH = "content/p1.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d03")

L["opening"] = """Picture your first day at a new job in a big office building. Before the ten o'clock meeting, your manager wants you to fetch one settings sheet from a drawer on the third floor and shred three old reports. There are no signs on the doors. The only way to get anything done is to write a short note and pass it to the clerk at the front desk.

Working on a server feels like that at first: no mouse, no picture of your files, only a line where you type. It is easy to assume the computer will work out what you meant. It won't. It does exactly what you wrote, and that includes shredding the wrong reports.

Last time, you stocked your laptop and opened a small Linux practice box. In this lesson, we'll learn how the clerk reads your note and how the building is laid out. Then we'll copy, move and delete files without losing the ones we need. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "A folder holds two files, `app.log` and `access.log`. You type `rm *.log` to delete them. What does the `rm` program actually receive?"
L["guess"]["why"] = "The shell turns `*.log` into the matching names before rm starts, so rm never sees the star. You can watch that step safely: `echo *.log` prints the names a command would get."

L["terms"] = [
    {"term": "Terminal", "plain": "The app with the window you type into, such as Terminal or iTerm2 on a Mac."},
    {"term": "Shell", "plain": "The program in the terminal that reads your line and runs it, such as zsh or bash."},
    {"term": "Argument", "plain": "A word after the command name. The shell splits your line on spaces to make them."},
    {"term": "Option (flag)", "plain": "An argument that starts with - or --, such as -l or --all, and changes what a command does."},
    {"term": "Working directory", "plain": "The folder you are in right now. The command pwd prints it."},
    {"term": "Absolute path", "plain": "A file's full address, starting at the top folder /, such as /var/log/app.log. It means the same from anywhere."},
    {"term": "Relative path", "plain": "A file's address counted from the folder you are in, such as logs/app.log."},
    {"term": "Glob (wildcard)", "plain": "A pattern like *.log that the shell turns into matching file names before a command runs."},
]

S = L["sections"]

S[0]["h"] = "The window, the clerk and the worker: terminal, shell and command"
S[0]["body"] = """Let's set up the building we will use for all of Part 1. You stand at a small window in the lobby. Behind it sits a clerk who reads each note you pass through. The clerk doesn't do most of the jobs. Instead, the clerk knows which worker in which room does each job, calls that worker, and passes back whatever the worker says.

People say "the command line" for all three of those things at once. They are different, and it helps to keep them apart:

- The terminal is the window. On your Mac that is the Terminal app, iTerm2 or the VS Code panel.
- The shell is the clerk: the program running inside that window. It reads the line you type and starts other programs. Your Mac uses zsh. Linux servers usually use bash, and so do the containers in this course.
- A command is the worker, and it is usually a program file on disk. `ls`, which lists files, is the file `/usr/bin/ls`. A few commands, like `cd`, are jobs the shell does itself. These are called builtins.

So when you type `ls -l` and press Enter, the terminal hands your keys to the shell. The shell finds the `ls` program by searching the folders on your PATH, which you met when you set up your laptop. It starts the program, and the terminal shows what it prints.

zsh and bash agree on almost everything in this part, and the lessons point out the few places where they differ. All the output you see comes from bash on Ubuntu, because servers, CI runners and Docker images give you that. That is why you practise inside a Linux container and not in your Mac's own shell. The Mac's tools also differ from the Linux ones in small ways, and you tend to find those differences when you are in a hurry.

Before you can pass the clerk a note, you need a building to stand in. Next, we'll start the practice one."""

S[1]["h"] = "Your practice building: a container with the lab files"
S[1]["body"] = """When you set up your laptop, you ran `docker run -it --rm ubuntu:24.04 bash` and got a throwaway Ubuntu machine. This part adds the course's practice files, so every lesson works on the same data. They are all fake: the logs and settings of a pretend online shop, laid out like a small server. A log is a file where a program writes down what it did, one line at a time.

1. Get the course files once: `git clone --depth 1 https://github.com/arunav-bhattacharya/devops-from-zero ~/code/devops-from-zero`.
2. Copy the lab to its own folder: `cp -R ~/code/devops-from-zero/labs/linux ~/code/linux-lab`.
3. In your Mac terminal, run `cd ~/code/linux-lab`.
4. Run `bash start-lab.sh`. It starts the container and installs a few extra tools, such as less, tree and jq. That takes about 20 seconds.

The first step uses git to download a copy of the course's files from GitHub. The last step runs a small script, a file of commands. Inside, the script is a single `docker run` command:

- `-it` gives you an interactive terminal.
- `--rm` deletes the container when you type `exit`.
- `-v "$PWD":/work` shows your Mac folder inside the container as `/work`.
- `-w /work` starts you in that folder.

Files in `/work` are your real Mac files, so they survive `--rm`. Anything you install or create anywhere else in the container is gone when you exit. While you learn, that is a gift: if you break something, type `exit` and start again.

Your prompt, the text the shell prints before your cursor, will look something like `root@3f2a9c1d7e4b:/work#`. It shows the user (root), the container's ID, the folder you are in, and `#`. The `#` marks the all-powerful root user, whom you meet properly in a later lesson. In this course, a line that starts with `$ ` is a command you type. Do not type the `$` itself.

You are standing at the window now. Next, we'll see exactly what the clerk does with the note you pass through."""

S[2]["h"] = "How the shell reads one line"
S[2]["body"] = """Say you write a note that reads `ls -l -h server/var/log`. Before any program starts, the clerk takes your note apart. The shell splits the line on spaces into words. The first word is the program to run. Every other word becomes an argument, a plain piece of text handed to that program.

So the shell runs `ls` with three arguments: `-l`, `-h` and `server/var/log`. The shell doesn't know what `-l` means. It only cuts the line into pieces, and the program decides what each piece means.

By habit, arguments that start with a dash are options, also called flags:

- Short options are one letter after one dash: `-l`, `-a`.
- Short options can usually be grouped: `ls -lh` means `ls -l -h`.
- Long options are words after two dashes: `--all`, `--help`. `ls -a` and `ls --all` do the same thing.
- Everything else is usually a file or folder to work on.

Nothing forces a program to follow this habit, so check the tool's help when you are unsure. The next section shows where to look.

Now watch the splitting go wrong. Because spaces split words, a file name with a space in it causes trouble. `ls my notes.txt` asks for two files, `my` and `notes.txt`, and prints two errors. The clerk did exactly what the note said.

There are two fixes. Quote the name, `ls "my notes.txt"`, or escape the space with a backslash, `ls my\\ notes.txt`. Better still, keep spaces out of the file names you create.

You now know how a line is cut into words. But how do you find out what all those little options mean? Next, we'll ask the tools themselves."""

S[3]["h"] = "Getting help: --help, man and tldr"
S[3]["body"] = """Nobody remembers every option, and experienced engineers look things up all day. The building has three places to ask:

- `ls --help` prints a short summary. Almost every Linux tool has it.
- `man ls` opens the full manual page. Press Space to page down, `/` and a word to search, `n` for the next match and `q` to quit.
- `tldr ls` shows a handful of common examples. Install it on your Mac with `brew install tlrc`.

Read the usage line first. `ls --help` begins with `Usage: ls [OPTION]... [FILE]...`. Square brackets mean optional, and three dots mean you may repeat it. So ls takes any number of options, then any number of files. Man pages call this part the SYNOPSIS.

There is one snag. The Ubuntu image is minimized, which means it was stripped down to keep it small. Inside the container, `man ls` prints a note that begins "This system has been minimized" and shows no manual. So use `--help` in the container.

`man` works on your Mac, but there it describes the Mac's own version of each tool, which can differ. For the Linux version, search the web for "man7" plus the command name.

Found a long command on the internet that you cannot read? Paste it into [explainshell](https://explainshell.com), which shows the manual text for each word.

You can read a note now, and look up any word in it. Next, we'll learn the layout of the building the notes talk about."""

S[4]["h"] = "The file system is one building, with one address for every drawer"
S[4]["body"] = """Every office building has one lobby, and every room is somewhere above it. To tell someone where a document is, you give them directions from the lobby: third floor, room 12, top drawer. Linux arranges its files the same way.

Linux keeps every file in one tree, which grows down from a single top folder. That top is the root folder, written `/`. A folder holds files and other folders, like a room with drawers. There are no drive letters: disks and USB sticks appear as folders somewhere in the tree.

The layout follows a shared standard, so settings and logs sit in the same places on every Linux server. Run `ls /` in the container to see the top level. In DevOps work you will visit these folders most:

- `/etc` holds configuration (settings), such as `/etc/passwd` (the list of users) and `/etc/nginx/` (a web server's settings).
- `/var/log` holds log files. On a server it is often the first place you look.
- `/home` holds a home folder for each normal user, such as `/home/ubuntu`. Root's home is `/root`.
- `/usr/bin` holds most programs, such as `/usr/bin/ls`.
- `/tmp` is scratch space that may be cleared at any time.

The lab's `server` folder copies this layout in miniature, so you can explore it safely.

A path is the address of a file or folder. An absolute path starts at the lobby, `/`, and means the same thing wherever you stand, such as `/work/server/var/log`. A relative path starts from the room you are standing in, which is called your working directory. So from `/work`, `server/var/log` means `/work/server/var/log`. You will type these short forms all day:

- `.` is the current folder, and `..` is the folder above it.
- `~` is your home folder: `/root` in the container, `/Users/you` on a Mac.
- `cd -` jumps back to the folder you were in before.
- `cd` with no argument takes you home.

Use `pwd` to print where you are and `ls` to list a folder. With `ls`, `-l` adds details, `-a` shows hidden files, `-h` prints sizes as K and M, and `-t` sorts newest first. A hidden file is just a file whose name starts with a dot, like `.env` or `.bashrc`. Plain `ls` skips them, because programs keep their settings in dot files and nobody wants those in every listing. The `tree` command draws a folder and everything below it.

Learn two keys early. Tab finishes a file or command name for you, which also means fewer typos. Ctrl+R searches your command history: press it, type part of an old command, and press Enter to run it again.

Knowing the addresses is half the job. Next, we'll start moving things around, and learn why the shredder deserves respect."""

S[5]["h"] = "Creating, copying, moving and deleting, with no undo"
S[5]["body"] = """Back at the front desk, your manager's list has three jobs: make a folder, copy a settings sheet into it, and shred the old reports. File work comes down to a handful of commands:

- `mkdir logs` makes a folder. `mkdir -p a/b/c` makes the whole chain and does not complain if it exists.
- `touch notes.txt` makes an empty file, or updates the time on a file that exists.
- `cp a.txt b.txt` copies a file. Folders need `-r` (recursive: the folder and everything inside it), as in `cp -r logs logs-backup`.
- `mv old new` moves or renames. Linux has no separate rename command.
- `rm file` deletes a file and `rm -r folder` deletes a folder with everything in it. `rmdir folder` deletes only an empty folder, which makes it the safe choice.

The shredder is the dangerous one. `rm` has no trash and no undo. The Trash on your Mac belongs to Finder, which only moves a file into a hidden folder. The rm command tells the system to remove the file's name from its folder, and the system can then reuse its disk space. Nothing keeps a copy.

Here is how it goes wrong. You mean to delete one folder called `old logs`, and you type `rm -r old logs`. The shell splits on the space, so rm deletes two folders, `old` and `logs`, and nothing brings them back. These habits keep that from happening to you:

1. Run `pwd`, then `ls` with the same paths first, to see what you are about to delete.
2. While you learn, add `-i`: `rm -i *.log` asks before each file.
3. Read any `rm -rf` line twice before you press Enter. The `-f` (force) part switches off every question.

**rm has no undo. Look before you delete.**

Read the error messages too, because they are short and exact. Without `-p`, `mkdir a/b/c` fails with `No such file or directory`, because `a/b` does not exist yet. Point `rm` at a folder and it refuses with `Is a directory`. Run `rmdir` on a folder with files in it and you get `Directory not empty`.

Typing three long file names to delete them is slow, and one typo picks the wrong file. Next, we'll name many files at once, and see who really does the matching."""

S[6]["h"] = "Wildcards: the shell expands them before the program starts"
S[6]["body"] = """Suppose your note says "shred every report from October". The clerk walks to the drawer, writes down the name of every October report, and hands the worker that list. The worker never hears the word "October". It only gets names.

A glob, or wildcard, is that kind of pattern for files. Before the program starts, the shell reads the folder, keeps the names that fit the pattern and puts them, sorted, in place of the pattern. You will rarely need more than these symbols:

- `*` matches any run of characters, even none. `*.log` matches `app.log` and `access.log`.
- `?` matches exactly one character. `app-2026-10-2?.log` matches the logs for the 27th, 28th and 29th.
- `[cp]` matches one character from a set. `logs/[cp]*.log` matches `checkout.log` and `payments.log`.

The program never sees the pattern, only the names. That makes `echo` a good checking tool, because echo just prints the arguments it receives, separated by spaces. Put it in front of a risky command and it prints the line the program would get. In the lab, `echo *.log` prints `access.log app.log`, and `echo rm logs/*.log` shows exactly what rm would delete.

Quotes switch globbing off: `echo "*.log"` prints `*.log`. A `*` also skips hidden files, so `*` alone never matches `.env`.

When nothing matches, bash and zsh disagree. In bash the pattern passes on unchanged, so `echo *.txt` prints `*.txt`. It is as if the clerk found no October reports and handed the worker the words "every report from October". In zsh the shell refuses to run the line and prints `no matches found: *.txt`. You will see the zsh behaviour on your Mac and the bash behaviour on every server.

That is the whole path of one note, from your fingers to the worker. In the worked example below, you walk the pretend server and tidy its logs with exactly these tools."""

L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = "Picture an engineer who gets paged at night, which means an alert has woken them because something broke. Their first minutes on the server look a lot like this lesson. They run `pwd` and `ls -lt /var/log/...` to find the newest log, and copy it aside before log rotation (the system's regular clean-up of old logs) moves it away. In reviews of deploy scripts, \"what does this glob expand to?\" is a normal question, and someone answers it with `echo`."

W = L["worked"]["steps"]
W[0]["say"] = "Start the lab with `bash start-lab.sh` in `~/code/linux-lab`. You land in `/work`, which is your Mac folder. `pwd` confirms it, and `ls` shows what is there. The `server` folder imitates the top of a Linux server."
W[1]["say"] = "Walk down the tree with a relative path. Each `cd` moves you, and `pwd` confirms where you landed. The shop's logs sit in `server/var/log/shop`, just as a real app's logs would sit in `/var/log`."
W[2]["say"] = "Climb back up with `..`, three levels at once. Then `cd -` returns to the previous folder and prints it, and `cd` alone goes home, which for root is `/root`."
W[3]["say"] = "A long listing shows sizes. The `-h` option turns bytes into K and M, so the big daily logs stand out at once. And `-a` reveals the hidden `.env` file, plus `.` and `..`. Your dates and owner columns will differ, because they come from your Mac."
W[4]["say"] = "Make an archive folder with `-p`. Before copying with a glob, put `echo` in front. It prints the command after the shell has expanded the `*`. Three files match, which is what you want, so run the real copy."
W[5]["say"] = "`mv` renames as it moves. `tree` draws the result. In the container it uses plain ASCII lines (simple keyboard characters); on your Mac it may draw nicer ones."
W[6]["say"] = "Deleting gets the same care: preview with `echo`, delete the files, then remove the empty folder with `rmdir`. Plain `rm` refuses a folder. `rm -r` removes it and everything inside, with no undo, so save it for when you are sure."

T = L["task"]
T["steps"] = [
    "Start the lab and check that you are in `/work`.",
    "Create three folders with as few commands as you can: `release/1.4.2/config`, `release/1.4.2/logs` and `release/1.4.2/bin`.",
    "Copy `server/etc/shop/config.yaml` and the hidden `.env` beside it into `release/1.4.2/config`, with one `cp` command.",
    "Copy every file in `logs` whose name starts with c or p into `release/1.4.2/logs`. Preview the glob with `echo` first.",
    "Copy `server/opt/shop/bin/start.sh` into `release/1.4.2/bin`, then rename the copy to `run.sh`.",
    "Move into `release/1.4.2/logs`. Write a relative path to `/work/server/etc/shop/config.yaml` and check it with `ls`.",
    "Back in `/work`, predict what `echo release/*/*`, `echo release/1.4.?/config/*` and `echo \"release/*\"` print. Then run them and explain any surprise.",
    "Draw your result with `tree -a release`, then delete the whole `release` folder with one command.",
]
T["hints"] = [
    "`mkdir -p` accepts several paths in one command.",
    "A `*` skips hidden files, so name `.env` on its own.",
    "From `release/1.4.2/logs`, count how many `..` steps lead back to `/work`.",
]

L["explain_back"]["answer"] = "The shell reads the line before anything runs. It replaces `*.log` with every matching file name in the current folder and splits the line into words. Then it starts `rm` and passes those names as arguments, so rm never sees the star. Putting `echo` in front prints the exact list rm would get, so I can check the glob before anything is gone for good."

L["recap"] = [
    "The terminal is the window, the shell (zsh on a Mac, bash on Linux) reads your line, and most commands are program files.",
    "The shell splits a line into a program and arguments; options start with - or --.",
    "`--help`, `man` and `tldr` tell you what a flag does; the usage line uses [ ] for optional and ... for repeatable.",
    "Paths are absolute from `/` or relative from where you are; `.`, `..`, `~` and `cd -` are shortcuts.",
    "Globs like `*`, `?` and `[abc]` are expanded by the shell before the program runs.",
    "The shell does exactly what you typed, and `rm` has no undo, so preview with `ls` or `echo` before you delete.",
]

C = L["check"]
C[0]["why"] = "Three `..` steps climb from shop to log to var to server. From `/work/server`, the path `etc/shop` lands in the right folder."
C[1]["why"] = "A `*` at the start of a glob does not match a leading dot, so hidden files stay out unless you name them."
C[2]["why"] = "The shell split the name at the space into two arguments. Quotes keep it as one word."

I = L["interview"]
I[0]["a"] = "The terminal is the program that draws the window and passes your keystrokes on. The shell is the program inside it that reads each line, expands globs and variables, and starts other programs. You can run different shells in the same terminal, such as zsh on a Mac and bash over SSH on a server. When a command behaves differently on two machines, look at the shell and the tool versions, not the terminal."
I[1]["a"] = "The shell expands `*.log` into the matching file names first, then starts `rm` with those names as arguments. It deletes each file, and there is no trash to recover them from. If nothing matches, bash passes the literal `*.log` and rm complains that it does not exist, while zsh refuses to run the line. A safe habit is to run `echo rm *.log` first and read the expansion."
I[2]["a"] = "I try `command --help` first, because most Linux tools print their usage line and options there. If man pages are installed, I open `man command` and press `/` to search for the flag. The usage line has a grammar: square brackets mean optional and three dots mean repeatable. On minimized images, such as Docker's Ubuntu image, man pages are removed, so `--help` is often the only local option."

L["deeper"]["body"] = """`cd` is built into the shell, while `ls` is a program file. The reason is a rule you will meet again on Day 7.

You can ask the shell which is which: `type cd` prints `cd is a shell builtin`, while `which ls` prints `/usr/bin/ls`. Every program the shell starts runs as a separate process, a child of the shell (Day 6 covers processes). Each process has its own working directory. A child can change its own, but it has no way to change its parent's.

Now imagine `cd` were a program. The shell would start it, it would change its own directory, and then it would exit. Your shell would not have moved at all. In the building, it is like sending a worker to the third floor and expecting the clerk to end up there. Only the shell can move the shell, so `cd` has to be a builtin. The same goes for a few other commands that change the shell's own state, such as `export` and `source`.

You will run into this rule in scripts. A script that runs `cd /var/log` does not move your terminal, and Day 7 shows that a script cannot change your terminal's variables either.

The layout of the tree has a name, by the way: the Filesystem Hierarchy Standard. The [hier(7) manual page](https://man7.org/linux/man-pages/man7/hier.7.html) describes each top-level folder, if you want the full tour.

Before you write loops over files, know that bash and zsh treat `**` differently. In bash, `*` only matches names inside one folder. In zsh, `**` also means "any number of folders". The container has no zsh, so install it first with `apt-get install -y zsh`. Then `zsh -c 'echo server/**/*.sql'` prints both backup files under `server/var/backups`. Bash can do the same after `shopt -s globstar`, but that is off by default, so scripts that must run anywhere use `find` (Day 4) instead.

When a command surprises you, ask the shell what it thinks the word means. Inside the container, `type ls` says that ls is an alias for `ls --color=auto`. An alias is a shortcut the shell expands before running, set up in a startup file. Day 7 shows where those files live."""

L["closing"] = """We started on a first day in an office building, with a note for the clerk and three reports to shred before ten. Now you know how the clerk reads that note: it splits on spaces, swaps patterns for real names, and hands the worker a plain list. You also know the building's addresses, and that its shredder keeps no copies.

Before your next delete, in the lab or anywhere else, put `echo` in front of the line and read what comes back.

Next, we'll open the documents in those drawers. The question it answers: how do you find the one line you need in a log with thousands of them?"""

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d03 written")
