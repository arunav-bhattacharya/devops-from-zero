"""Book-voice rewrite of d06 (Users, permissions, processes and services). Writer: ta. Run from the repo root."""
import json

PATH = "content/p1.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d06")

L["opening"] = """Picture Friday afternoon in the office building. Your new script for the shop's nightly job won't start: the screen says "Permission denied". Down the hall, an old worker program is still running and won't stop. Everyone wants to go home.

Two shortcuts are right there. Borrow the building manager's master key for everything, and stop arguing with the door. Call security and have the old worker dragged out mid-task. Both get you home on time, and both leave a mess for Monday: files only the manager can change, and half-finished work nobody can explain. They feel safe because they work at once.

Last time, we connected small tools with pipes and turned a log into a report. In this lesson, we'll meet the people and keys of the building. We'll read and fix permissions, stop running programs politely, hand them to the manager who keeps them running, and check a machine's health. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "`sleep 300` is a command that just waits for 300 seconds. While it runs in your terminal, you press Ctrl+Z. What happened to it?"
L["guess"]["why"] = "Ctrl+Z sends a signal called SIGTSTP, which pauses the process. `jobs` still lists it as Stopped, and `fg` or `bg` brings it back."

L["terms"] = [
    {"term": "User and group", "plain": "A user is an account that permissions are checked against. A group is a named set of users."},
    {"term": "root", "plain": "The superuser, with user ID 0, which skips almost every permission check."},
    {"term": "Permission bits", "plain": "Read (r), write (w) and execute (x) rights, set separately for the owner, the group and everyone else."},
    {"term": "Process", "plain": "A running program. Each one has an ID number called a PID."},
    {"term": "PID", "plain": "Process ID: the number the system gives each running process."},
    {"term": "Signal", "plain": "A short message the system delivers to a process, such as SIGTERM (please stop) or SIGKILL (stop now)."},
    {"term": "Service", "plain": "A program that runs in the background, started and watched by a manager such as systemd."},
    {"term": "Unit file", "plain": "A small text file that tells systemd how to run a service."},
]

S = L["sections"]

S[0]["h"] = "Badges and the master key: users, groups and root"
S[0]["body"] = """In our office building, everyone wears a badge, and every drawer belongs to someone. Linux works the same way. It is built for many users on one machine, and every file and every process belongs to a user. Without that, a bug in the web server could read every password on the machine. Each process carries the ID of the user it runs as. When it opens a file, the kernel, the core of the operating system, compares that user with the file's owner and permissions. To see who you are:

- `whoami` prints your user name.
- `id` prints your user ID (UID), your main group and every group you are in. In the container it prints `uid=0(root) gid=0(root) groups=0(root)`.

A group is a named set of users, so one rule can cover a whole team. Users are listed in `/etc/passwd`, one per line. Programs get their own users too. On Ubuntu the web server nginx runs as `www-data`, so a bug in nginx can only reach what www-data may touch.

The superuser is called root and has UID 0. Root is the building manager with the master key: the kernel skips almost every permission check for root. That is why your container prompt ends with `#`: you are root. A normal user's prompt ends with `$`.

On a real server you log in as a normal user and borrow the master key for one command with `sudo`, as in `sudo apt install nginx`. The sudo command checks that you are allowed (on Ubuntu, by being in the `sudo` group). It usually asks for your own password, then runs that one command as root.

That is the first Friday shortcut, and it is a trap. Do not put sudo in front of everything. It hides the real cause, such as a wrong owner, and leaves files behind that only root can change.

In the container you are root, so to see a denial for yourself, make a normal user: `useradd -m -s /bin/bash dev` (`-m` makes a home folder and `-s` picks the shell). Then `su - dev -c 'cat /etc/shadow'` runs one command as dev. `/etc/shadow` holds the password hashes (scrambled passwords), so only root may read it, and dev gets `cat: /etc/shadow: Permission denied`.

Badges say who you are. The sign on each drawer says what you may do with it. Next, we'll read that sign."""

S[1]["h"] = "Reading the sign on each drawer: ls -l, column by column"
S[1]["body"] = """Run `ls -l deploy.sh` and you get a line like `-rw-r--r-- 1 root root 29 Oct 30 05:10 deploy.sh`. It looks like noise at first, but it is a sign with seven parts. From left to right:

1. `-` is the type: `-` for a file, `d` for a directory, `l` for a link.
2. `rw-` is what the owner may do.
3. `r--` is what the group may do.
4. `r--` is what everyone else (others) may do.
5. `1` is the number of links to the file. You can ignore it for now.
6. `root root` are the owner and the group.
7. `29` is the size in bytes, and then come the last change time and the name.

Each permission triplet has three slots: `r` is read, `w` is write and `x` is execute (run). A dash means "not allowed".

For each check the kernel picks exactly one triplet. It uses the owner's if you own the file, else the group's if you are in its group, else the one for others. The first that fits decides, even if a later one allows more.

On a directory, the same letters mean something else:

- `r` lets you list the names inside.
- `w` lets you create, rename and delete entries inside.
- `x` lets you enter the directory and reach the files in it.

So a directory with `x` but no `r` works like a room with no list on the door: you can fetch a file only if you know its name. To test it, make a folder `/tmp/vault` with a file `key.txt` in it and run `chmod 711 /tmp/vault`, which gives `drwx--x--x`. User dev then gets `Permission denied` from `ls /tmp/vault`. Yet `cat /tmp/vault/key.txt` works, because dev knows the exact name.

Now you can read the sign. Next, we'll change it, and fix Friday's "Permission denied" the right way."""

S[2]["h"] = "Changing permissions: chmod, chown and umask"
S[2]["body"] = """The chmod command changes permissions, and you can write them in two ways. The symbolic form says who, then plus or minus, then what. Here `u` is the owner (user), `g` the group, `o` others and `a` all:

- `chmod u+x deploy.sh` lets the owner run it.
- `chmod go-rx deploy.sh` takes read and execute away from group and others.

The octal form gives each triplet one digit. A triplet is three yes-or-no bits, and three bits hold a number from 0 to 7, which is one octal (base 8) digit. So r = 4, w = 2 and x = 1, and you add the rights you want:

- `755` is `rwxr-xr-x`: everyone can run it and only the owner can change it. Normal for scripts and folders.
- `644` is `rw-r--r--`: everyone can read and only the owner writes. Normal for files.
- `600` is `rw-------`: the owner only. Use it for private keys and secrets.

To change the owner and group, use `chown dev:dev key.txt`, which needs root.

New files do not start with random rights either. A setting called the umask removes rights from every new file and folder. Programs usually ask for 666 for a new file and 777 for a new folder. The usual umask, `0022`, removes write for group and others, so new files come out as 644 and new folders as 755.

That explains Friday's script. A fresh file is 644, with no execute bit for anyone. Running `./deploy.sh` (the `./` means "in this folder", because the shell only looks for commands in PATH) prints `Permission denied` with exit code 126. The fix is one missing bit: `chmod u+x deploy.sh`.

**Fix the one bit that is missing. Never reach for `chmod 777`.** That mode lets every user on the machine change the file.

Drawers and keys cover files. But who is actually doing the work in the building? Next, we'll meet the workers."""

S[3]["h"] = "Workers on shift: processes, PIDs and jobs"
S[3]["body"] = """A job description in a drawer does nothing until someone is hired to do it. A program is like that description: a file on disk. A process is one running copy of it, a worker on shift. Run `sleep 300` in two terminals and you get two processes from one file.

The kernel gives each process a number, its process ID, or PID. Each one carries its own state: the user it runs as, its working directory (Day 3) and its open streams (Day 5). Every process also has a parent, the process that started it. The parent's PID is called the PPID. Your shell is the parent of every command you type. To look at processes:

- `ps aux` lists every process with its user, PID, CPU and memory use, and command. The letters `aux` are an old option style with no dash: `a` and `x` together include every process, and `u` adds the user, CPU and memory columns.
- `ps -o pid,ppid,stat,cmd` lists your own processes with the columns you choose.
- `pgrep -a sleep` finds processes by name and prints their PIDs.
- `top` shows a live view, busiest first; `q` quits. `htop` is a friendlier version.

In a fresh container, `ps aux` shows just two processes: `bash` with PID 1 and the `ps` command itself. PID 1 is the first process. In a container it is whatever you started. On a normal Linux machine it is systemd, which starts everything else.

A command you type runs in the foreground, and the shell waits for it. Add `&` to run it in the background and get your prompt back. The shell calls these jobs:

- `sleep 300 &` prints a job number and the PID, like `[1] 15`. Afterwards, `$!` holds that PID.
- `jobs` lists your jobs. `fg` brings one back to the foreground, and `bg` lets a paused one carry on in the background.
- Ctrl+Z pauses the foreground job. It does not end it. That was the answer to the guess.
- `nohup cmd &` keeps a command alive after you close the terminal. A closing terminal sends the hang-up signal, and nohup makes the command ignore it. Output goes to `nohup.out`.

A worker in the background is not listening to your keyboard. So how do you tell it to go home? Next, we'll slip it a note."""

S[4]["h"] = "Signals: asking a process to stop, and forcing it"
S[4]["body"] = """There are two ways to end a worker's shift. You can knock and say "please finish what you are doing and go home". Or you can call security and have them carried out mid-sentence. The first leaves tidy desks. The second leaves half-filed papers everywhere.

A signal is a short message the kernel delivers to a process. The terminal sends one when you press Ctrl+C, and the `kill` command sends one from another shell. Despite its name, kill can send any signal. A program can catch most signals and decide what to do. If it does not, the default for the four below is to end the process. These are the ones you will meet:

- SIGINT (signal 2) is what Ctrl+C sends: "the user wants you to stop".
- SIGTERM (15) is the polite knock, and `kill PID` sends it by default. A well-behaved program finishes its work, closes its connections and exits.
- SIGKILL (9) is security. It ends the process at once and cannot be caught, so no cleanup runs. Send it with `kill -9 PID`.
- SIGHUP (1) once meant "your terminal hung up". Many servers, nginx included, treat it as "reload your configuration".

The exit code tells you how a process ended. When a signal kills it, the code is 128 plus the signal number. So 130 means Ctrl+C, 143 means SIGTERM and 137 means SIGKILL. You will meet 137 again when Docker or Kubernetes kills a container that used too much memory.

The lesson's `worker.sh` catches SIGTERM with `trap`, a shell command that says what to run when a signal arrives. After a plain `kill`, its log ends with `worker: stopped cleanly after job 3`, and it exits with 0. After `kill -9`, the log just stops mid-job and the exit code is 137.

Containers get stopped with the same pair. The `docker stop` command sends SIGTERM, waits 10 seconds, then sends SIGKILL. Kubernetes does the same with a 30 second default.

**Knock with SIGTERM first. Keep `kill -9` for a process that ignores the knock.**

Stopping a worker by hand is fine for one machine on one afternoon. But who starts the workers again after a power cut at 3 a.m.? Next, we'll meet the building's facilities manager."""

S[5]["h"] = "Services with systemd: the manager who opens the building"
S[5]["body"] = """Every morning, someone unlocks the building, switches on the lights and makes sure each department has its staff. When a worker walks out, that person calls in a replacement. On a Linux server, that someone is systemd.

A service is a program that runs in the background without a terminal, such as a web server or a queue worker. Running it with `nohup` keeps it alive after you log out. But nothing starts it again after a reboot, or after a crash at 3 a.m.

systemd does that job on almost every Linux server. As PID 1, it starts services at boot, can restart them when they crash and collects their logs. It describes each service in a unit file. That is a short text file in INI format: sections in square brackets, then `key=value` lines. The nginx package ships one at `/usr/lib/systemd/system/nginx.service`, with three sections:

- `[Unit]` has a description and says what must start first.
- `[Service]` has `ExecStart`, the command to run, and how to stop and reload it.
- `[Install]` has `WantedBy=multi-user.target`. A target is a named stage of booting, and multi-user.target is the normal running server, so this means "start at boot".

You control services with systemctl:

- `systemctl status nginx` shows whether it runs, its main PID and its last log lines.
- `sudo systemctl start nginx` starts it, and `stop` and `restart` do what they say.
- `sudo systemctl enable nginx` makes it start at boot, but does not start it now. `enable --now` does both.
- `sudo systemctl daemon-reload` makes systemd read unit files again after you change one. It does not notice edits on its own.

systemd connects each service's stdout and stderr to its journal, so every line the program prints becomes a log entry. The journalctl command reads that journal. Add `-u nginx` for one service, `-f` to follow new lines like `tail -f`, `-n 50` for the last 50, and `--since '10 min ago'` to limit by time.

In a plain container systemd does not run, because PID 1 is your own shell, and the worked example shows the errors you get. That is why the task uses a small Ubuntu virtual machine, made with Multipass, for the systemd part.

The manager keeps the workers running. The last question is whether the building itself is healthy. Next, we'll check the storeroom, the desks and the doors."""

S[6]["h"] = "Disk, memory, load and ports: a quick health check"
S[6]["body"] = """A building inspector checks a few things first: is the storeroom full, are there enough desks, is anyone queueing at the door? A machine has the same quick checks. The last two look at ports, the numbered doors that programs listen behind (Day 10 explains them properly).

- `df -h` shows each disk's size, used space and free space. A full disk breaks logs, databases and deploys.
- `du -sh server/*` (disk usage, one total per folder) shows how much space each folder uses. Add `| sort -h` to sort sizes like 60K and 2.9M correctly.
- `free -h` shows memory. Read the `available` column, because Linux borrows spare memory as a disk cache and gives it back when needed.
- `uptime` shows how long the machine has run and three load averages over 1, 5 and 15 minutes. The load is the average number of processes running or waiting for a CPU, so compare it with the CPU count from `nproc`.
- `ss -tlnp` lists the TCP ports that something listens on, and which process owns each one. The letters stand for TCP, listening, numeric and process.
- `lsof -i :80` asks the same question about one port. lsof means list open files: Linux treats a network connection as an open file, with a file descriptor.

On your Mac, `df`, `du`, `uptime` and `lsof` exist, but `free` and `ss` do not. There, `lsof -iTCP -sTCP:LISTEN -n -P` lists listening ports.

These checks tell you what is wrong on one machine, right now. They don't remember last night, and they don't watch a hundred servers at once. Later parts add that. First, the worked example puts today's tools together on a real web server in the container."""

L["aside"] = {
    "title": "Why is running a container as root risky?",
    "after": 2,
    "body": "Root inside a container is UID 0, the same number as root on the host machine that runs the container. The container's walls usually keep it in its corner. But if an attacker finds a way through those walls, they arrive with the master key already in hand. Running the app as a normal user means an escape starts with almost no power. Part 5 shows how to set that user in a Dockerfile.",
}

L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = "A rollout replaces the old version of a service, and systemd and Kubernetes stop the old one the same way: SIGTERM, a grace period, then SIGKILL. In a payments system, code reviews check that a service handles SIGTERM by finishing the payments in flight before it exits. When a machine misbehaves, the person on call starts with `systemctl status`, `journalctl -u NAME --since`, `df -h` and `ss -tlnp`."

W = L["worked"]["steps"]
W[0]["say"] = "Install nginx quietly and start it by hand, since the container has no systemd. Then list its processes. One master runs as root, which a normal server requires for opening port 80. It starts four workers (one per CPU here) as the `www-data` user, so the code that answers strangers cannot touch root's files. The PPID column shows that the workers are the master's children."
W[1]["say"] = "Who listens on port 80? `ss -tlnp` names nginx and the master's PID, and `lsof` agrees. A request with curl, a command-line tool that fetches web pages, gets `200 OK`. On your machine you may also see a line for `[::]:80`, the IPv6 version of the same port."
W[2]["say"] = "Send SIGHUP to the master, which nginx treats as \"reload\". The master keeps its PID, starts new workers with the new settings and lets the old ones finish. The worker PIDs change, but the server never stops listening."
W[3]["say"] = "Now stop it politely with SIGTERM. `pgrep` finds nothing and exits 1, and curl exits 7, which means it could not connect at all."
W[4]["say"] = "On a real server, systemd would do all of this for you. The container cannot. First the command is missing, and after you install systemd, it refuses to work because it is not PID 1."
W[5]["say"] = "The unit file still arrives with the nginx package, so you can read it. Its `ExecStart` line is how systemd starts nginx, and `ExecReload` sends the reload. The `WantedBy` line makes `enable` start it at boot. The task does the same with your own service in a VM."

T = L["task"]
T["steps"] = [
    "Install Multipass on your Mac with the installer from [canonical.com/multipass/install](https://canonical.com/multipass/install) (it needs macOS 14 or later). Then run `multipass launch 24.04 --name devbox` and `multipass shell devbox`.",
    "In the VM, run `whoami`, `id` and `ps -p 1 -o pid,cmd`. Note your user, your groups, and what PID 1 is this time.",
    "From your Mac, copy this lesson's two files into the VM's home folder with `multipass transfer worker.sh hello-worker.service devbox:.`.",
    "In the VM, install the script so systemd can run it: put it in `/usr/local/bin` with mode 755, owned by root. That folder is the usual place for programs you add by hand. With root as the owner, the service's normal user can run the script but not change it. Copy the unit file into `/etc/systemd/system/` and make systemd read it.",
    "Start the service and check it with `systemctl status hello-worker`. Find its main PID and that PID's parent.",
    "Follow its log with `journalctl -u hello-worker -f`. In a second Mac terminal, open another shell into the VM and stop the service. Find the two lines from the trap in the log.",
    "Enable the service, reboot the VM with `sudo reboot`, wait a minute, open a shell again and check that it started on its own.",
    "Check the VM's health: disk space, memory, load average and listening ports. Keep the VM for Day 7.",
]
T["hints"] = [
    "`sudo install -m 755 worker.sh /usr/local/bin/worker.sh` copies the file and sets its mode in one step.",
    "After you add or change a unit file, systemd needs `sudo systemctl daemon-reload` before it sees the change.",
    "`ps -o ppid= -p PID` prints only the parent's PID.",
]

L["explain_back"]["answer"] = "Both first send SIGTERM, a polite request that the program can catch to finish its work and exit. Then they wait a grace period: 10 seconds by default for docker stop. If the program is still running after that, they send SIGKILL, which cannot be caught and ends it at once. A process ended that way exits with 137, which is 128 plus signal 9, a sign that it ignored or mishandled SIGTERM."

L["recap"] = [
    "Every file has an owner, a group and rwx bits for owner, group and others; root (UID 0) skips the checks.",
    "Octal adds r=4, w=2 and x=1: 755 for scripts and folders, 644 for files, 600 for secrets.",
    "On a directory, `x` means you may enter it and `r` means you may list it.",
    "Processes have PIDs and parents; `&`, `jobs`, `fg`, `bg` and Ctrl+Z manage jobs.",
    "SIGTERM asks and SIGKILL forces; exit codes 130, 143 and 137 tell you which signal ended a process.",
    "systemd runs services from unit files, but `systemctl` and `df` only see one machine; watching many comes in later parts.",
]

C = L["check"]
C[0]["why"] = "Dana is not the owner but is in the group, so the group triplet decides, and it is `r--`."
C[1]["why"] = "systemd sent SIGTERM, waited out its stop timeout, then had to force the stop. A program that handles SIGTERM exits long before that."
C[2]["why"] = "Only the owner's execute bit is missing. sudo and 777 give away far more than the problem needs."

I = L["interview"]
I[0]["a"] = "SIGTERM asks a process to stop, and the process can catch it to finish its work and exit cleanly. SIGKILL cannot be caught and ends the process immediately, with no cleanup. Docker and Kubernetes send SIGTERM first, wait a grace period (10 seconds for docker stop, 30 by default for a pod), then send SIGKILL. An app that handles SIGTERM can finish its requests during a rollout instead of dropping them."
I[1]["a"] = "Each digit covers one of owner, group and others, adding read 4, write 2 and execute 1. So 755 is rwxr-xr-x, typical for scripts and folders, and 644 is rw-r--r--, typical for plain files. On a directory, x means you may enter it and reach the files inside by name, and r means you may list its contents. With x but no r, people can open a file only if they know its exact name."
I[2]["a"] = "I start with `systemctl status NAME`, which shows the state, the last exit code and the latest log lines. Then `journalctl -u NAME --since '1 hour ago'` gives the full story, or `-f` while I restart it. Then I rule out the common causes: `df -h` for a full disk, `free -h` for memory and `ss -tlnp` for a port that another program already holds. If someone edited the unit file, I make sure `daemon-reload` ran."

L["deeper"]["body"] = """You will read `systemctl status` on every server you touch, and it packs a lot into a few lines. The course container cannot run systemd, so this walk-through uses the Bluetooth service example from the official systemctl manual:

- `● bluetooth.service - Bluetooth service` is the unit name and its description. The dot shows the state at a glance: a green dot for active, a white circle for inactive, a red cross for failed.
- `Loaded: loaded (/usr/lib/systemd/system/bluetooth.service; enabled; preset: enabled)` gives the unit file's path and says the service is enabled, so it starts at boot.
- `Active: active (running) since Wed 2017-01-04 13:54:04 EST; 1 weeks 0 days ago` is the current state and how long it has been in it. A crashed service shows `failed` here, often with an exit code.
- `Main PID: 930 (bluetoothd)` is the process systemd watches. When it exits, systemd decides whether to restart it.
- `Tasks: 1`, `Memory: 648.0K` and `CPU: 435ms` are what the service uses right now.
- `CGroup: /system.slice/bluetooth.service` lists every process in the service's control group, a kernel feature that keeps a service's processes together.

After a blank line come the last log lines, in the same format as journalctl: date and time, host name, process name with its PID in brackets, then the message. For example: `Jan 12 10:46:45 example.com bluetoothd[8900]: Not enough free handles to register service`.

Two lines in `hello-worker.service` decide how systemd uses today's signals. `Restart=on-failure` makes systemd start the worker again if it crashes or is killed, but not after a clean stop. Try it in the VM: find the main PID and send it `kill -9`. Then run `systemctl status hello-worker` again. The Main PID has changed, because systemd started a fresh copy.

`KillMode=mixed` controls what `systemctl stop` does. By default systemd sends SIGTERM to every process in the control group at once, including the `sleep` inside the worker's loop. With `mixed`, only the main process gets SIGTERM, so the worker can finish its current job and exit cleanly. Any process still around afterwards gets SIGKILL. The nginx unit file from the worked example uses the same setting."""

L["closing"] = """We started on a Friday afternoon, with a script that said "Permission denied" and a worker that would not leave. Neither needed the master key or security. The script was missing one execute bit, and the worker deserved a polite SIGTERM and a few seconds to finish.

The next time you are about to type `sudo` or `kill -9`, stop and read `ls -l` or the process's log first, and name the real cause.

Next, we'll read the notes pinned to each worker's desk, get a key to another building, and write a checklist for the clerk. The question it answers: how do you turn a good afternoon at the terminal into a script that runs the same way every time?"""

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d06 written")
