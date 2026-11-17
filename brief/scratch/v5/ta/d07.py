"""Book-voice rewrite of d07 (Environment, packages, SSH and shell scripts). Writer: ta. Run from the repo root."""
import json

PATH = "content/p1.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d07")

L["opening"] = """Picture a Monday in the office. For the third time this month, you check by hand that the shop's web app is answering: send a request, read the reply, try again if it is slow. A colleague says, "Write it down as a checklist, so anyone can run it. Even the robot that tests our code." It sounds like ten minutes of work.

The first checklist anyone writes has a quiet flaw. Step two fails, the list carries on, and the last line proudly says "all done". It is an easy flaw to miss, because on a good day every step works, and the list looks perfect.

Last time, we met the building's badges and keys, its workers, and the manager who keeps them running. In this lesson, we'll learn the notes each worker carries, how the clerk finds a worker, how to order new tools, and how to get a key to another building. Then we'll write a checklist that stops when a step fails. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "A script `setenv.sh` contains the line `export GREETING=hi`. You run `./setenv.sh`, then `echo $GREETING` in the same terminal. What prints?"
L["guess"]["why"] = "The script runs as a child process with its own copy of the environment, and its export dies with it. Running `source setenv.sh` runs the lines inside your shell instead."

L["terms"] = [
    {"term": "Environment variable", "plain": "A named setting that a process passes down to every program it starts, such as PATH."},
    {"term": "export", "plain": "The shell command that turns a shell variable into an environment variable."},
    {"term": "PATH", "plain": "A colon-separated list of folders the shell searches, in order, to find a command."},
    {"term": "Package manager", "plain": "A tool that downloads, installs and updates software, such as apt on Ubuntu or brew on a Mac."},
    {"term": "SSH key pair", "plain": "A private key you keep secret and a public key you give to servers, used to log in without a password."},
    {"term": "Shebang", "plain": "The first line of a script, such as #!/usr/bin/env bash, which names the program that runs it."},
    {"term": "Strict mode", "plain": "The line set -euo pipefail: stop on errors, on unset variables and on failures inside pipes."},
]

S = L["sections"]

S[0]["h"] = "Notes on every desk: variables and the environment"
S[0]["body"] = """When a supervisor in our building hires a new worker, they hand over a photocopy of the notes on their own desk, such as which printer to use. The new worker can scribble on that copy. The supervisor's notes never change.

The shell keeps notes too, called variables. Set one with `name=value` and read it with `$name`:

- After `GREETING=hi`, the command `echo $GREETING` prints `hi`.
- There are no spaces around `=`. The line `name = alice` runs a program called `name` with two arguments, and bash answers `name: command not found`.
- Values are text. Quote a value that has spaces: `name="Ada Lovelace"`.

A plain variable lives only in the current shell. But programs need settings that change from laptop to server, such as a port. An environment variable is one that the shell hands down to every program it starts. Along with its arguments, each new program receives a list of `NAME=value` pairs, called its environment. `export GREETING` turns a plain variable into an environment variable. Try it in the lab:

- Before export, `bash -c 'echo "child sees [$GREETING]"'` prints `child sees []`.
- After `export GREETING`, the same line prints `child sees [hi]`.
- Writing `GREETING=hey cmd` sets the variable for that one command only.
- `unset GREETING` removes it.

A child gets a copy of its parent's environment, and nothing the child changes ever flows back up. That is the answer to the guess. A script that runs `export` cannot change your terminal, for the same reason that `cd` inside a script cannot move you. To run a file's lines in your own shell, use `source setenv.sh`.

**Copies flow down to children, never up to parents.**

To see the whole environment, run `env` or `printenv`, and `printenv HOME` prints one value. The environment is also how one hello-devops image runs everywhere. That is the course's tiny web app, which answers every visit with a greeting and a count of visits so far. It reads `APP_VERSION`, `GREETING`, `REDIS_HOST` and `PORT` from its environment, and Docker, Compose and Kubernetes each set them.

Next, we'll look at the one note the clerk uses to find every worker."""

S[1]["h"] = "PATH: how the shell finds a command"
S[1]["body"] = """When you hand the clerk a note that says `jq`, the clerk needs to know which room the jq worker sits in. So the clerk keeps a list of rooms to check, in order, and stops at the first one with a jq inside.

That list is the `PATH` variable. The shell looks through its folders, in order, and runs the first match. Colons separate the folders. In the container, `echo $PATH` prints `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`. To see what will actually run:

- `which jq` prints the file it found: `/usr/bin/jq`.
- `type` also knows the shell's own commands. For `type cd ls jq` it says that cd is a shell builtin, ls is an alias for `ls --color=auto`, and jq is `/usr/bin/jq`.

If no folder has the program, you get `command not found` and exit code 127. To add your own folder, put it in front of the list: `export PATH="$HOME/bin:$PATH"`. The `$PATH` at the end keeps the old folders.

An export lasts until you close the terminal. To keep a setting, put the line in a startup file, which the shell reads when it starts. Which file depends on the shell. A login shell starts a session, such as an SSH login or a new Mac Terminal tab. An interactive shell is any shell you type into:

- On your Mac, zsh reads `~/.zshrc` for every interactive shell. Homebrew's setup from Day 2 lives in `~/.zprofile`, which login shells read first.
- On Linux, bash reads `~/.bashrc` for interactive shells. A login shell, such as an SSH session, reads `~/.profile`, and Ubuntu's default `~/.profile` then loads `~/.bashrc`.

After editing one, open a new terminal, or run `source ~/.zshrc` to load it into the shell you are in.

PATH finds the tools you have. Next, we'll order the ones you don't have yet."""

S[2]["h"] = "Ordering new tools: apt, dnf, apk and brew"
S[2]["body"] = """An office orders supplies from a catalogue. The supplier sends the item and everything it needs to work, and keeps a record of what you bought. Most programs need other software to run, such as libraries (shared code that many programs use). Installing all of it by hand is slow and easy to get wrong.

A package manager is that supplier. It downloads a program and everything it depends on, puts the files in the right places, remembers what it installed and updates it later. Each Linux family packs software in its own format, so each has its own manager:

- Ubuntu and Debian use apt: `apt-get update`, then `apt-get install -y jq`. On a server, put `sudo` in front.
- Fedora and Red Hat use dnf, as in `sudo dnf install jq`.
- Alpine Linux, popular for small container images, uses apk: `apk add --no-cache jq`. The `--no-cache` part keeps the package list out of the image, so the image stays small.
- Your Mac uses Homebrew: `brew install jq`.

apt installs from a local copy of the catalogue, the list of available packages. A fresh Ubuntu container starts with that list empty. So `apt-get install jq` fails with `E: Unable to locate package jq` until you run `apt-get update`. The `-y` answers yes to the confirm question, which a script cannot do.

On Ubuntu there are two commands. The newer `apt` is friendly at a terminal, with progress bars and `apt search`. The older `apt-get` keeps its output stable, which is what scripts and Dockerfiles need. Pipe `apt` into another command and it warns you itself: `WARNING: apt does not have a stable CLI interface. Use with caution in scripts.`

When a command is missing, [command-not-found.com](https://command-not-found.com) tells you which package provides it on each system.

Next, we'll get a key to another building."""

S[3]["h"] = "A key to another building: SSH"
S[3]["body"] = """Servers sit in data centres and clouds, far from any keyboard you could touch. SSH (Secure Shell) gives you a shell on such a machine over an encrypted connection, one that strangers on the network cannot read. Running `ssh ubuntu@192.168.64.5` logs you in as ubuntu on the machine at that address (Day 10 covers addresses).

Passwords work, but people guess and reuse them. Keys are safer and quicker. A key pair is two files:

- The private key, `~/.ssh/id_ed25519`, stays on your laptop. It works like a password, so never copy it anywhere else.
- The public key, `~/.ssh/id_ed25519.pub`, is safe to share. You put it on servers and in GitHub.

The public key is like a lock you are happy to hand out, and the private key is the only thing that opens it. Create a pair with `ssh-keygen -t ed25519 -C "you@example.com"`. Here `-t` picks the key type (ed25519 is the modern one that GitHub's guide uses), and `-C` adds a comment to tell keys apart.

Set a passphrase when it asks: it encrypts the private key file, so a stolen copy is useless without it. Afterwards, `ls -l ~/.ssh` shows the private key with mode `-rw-------` (600) and the public one with `-rw-r--r--` (644).

A server keeps the public keys it trusts in `~/.ssh/authorized_keys`, one per line. When you connect, your ssh signs a piece of data unique to this connection with the private key. The server checks that signature with the public key, so the private key itself never leaves your laptop.

Trust also runs the other way. The first time you connect, ssh shows the server's fingerprint, a short code that identifies it, and asks `Are you sure you want to continue connecting (yes/no/[fingerprint])?`. Saying yes stores it in `~/.ssh/known_hosts`. If that fingerprint ever changes, ssh refuses to connect, because someone may be pretending to be your server.

Four helpers make everyday SSH easier:

- The file `~/.ssh/config` gives hosts short names, so `ssh devbox` replaces a long command (see the files below).
- The ssh-agent program holds your unlocked key, so you type the passphrase once. On a Mac, `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` keeps it in your Keychain.
- `scp app.log devbox:/tmp/` copies a file over SSH.
- `rsync -av logs/ devbox:/tmp/logs/` copies a folder: `-a` copies everything inside and keeps permissions and times, and `-v` lists each file. Run it again and it sends only what changed.

Next, we'll write the work down, so the clerk can do it without you."""

S[4]["h"] = "Your first bash script: a checklist for the clerk"
S[4]["body"] = """A script is a checklist for the clerk: a text file of commands, run from top to bottom. To make one runnable:

1. The first line is a shebang, `#!/usr/bin/env bash`. When you run a file that starts with `#!`, the kernel starts the program named on that line and hands it the file. Here that program is `env`, which finds bash through PATH, wherever it is installed. Use it on your Mac too, so scripts behave the same everywhere.
2. The file needs the execute bit: `chmod +x script.sh` (Day 6).
3. You run it with a path, `./script.sh`, because your current folder is not in PATH. That is deliberate: otherwise a file called `ls` in a downloaded folder could run instead of the real one.

Scripts get their arguments as numbered variables:

- `$1`, `$2` and so on are the arguments, and `$0` is the script's own name.
- `$#` is how many arguments there are.
- `"$@"` is all of them, each kept as a separate word. Running `./args.sh deploy "eu west" 3` gives three arguments, and `eu west` stays one of them.

Quoting decides what the shell does to a value, and it causes more script bugs than anything else:

- Single quotes keep everything literal: `echo 'Hello, $name'` prints `Hello, $name`.
- Double quotes still replace variables: `echo "Hello, $name"` prints `Hello, Ada Lovelace`.
- No quotes means the shell splits the value on spaces and expands globs in it. With `file="my notes.txt"`, `ls $file` looks for two files, while `ls "$file"` works.

The same slip is far worse with rm. `rm $file` works until the value holds a space or a `*`. Then the shell splits or expands it, and the command hits the wrong files. So write `"$var"` and `"$(command)"` in double quotes unless you have a reason not to.

Your script returns an exit code too. `exit 0` ends a script with success, and `exit 1` (or any number up to 255) with failure. CI systems, the robots that test code on every change, such as GitHub Actions (Day 24), look only at that number: anything but 0 fails the step.

Real checklists also say "if this, then that" and "repeat until done". Next, we'll add both."""

S[5]["h"] = "Conditions, loops and functions"
S[5]["body"] = """A good checklist has branches: "if the door is locked, use the side door". The `if` keyword runs a command and checks its exit code. Zero runs the `then` part, and anything else skips it. In bash, `[[ ... ]]` is built-in test syntax that exits 0 when the test is true and 1 when it is false:

- `[[ -f app.log ]]` is true if the file exists, and `-d` checks for a directory.
- `[[ "$a" == "$b" ]]` compares strings, and `[[ $n -gt 9 ]]` compares numbers. Its friends are `-lt`, `-ge`, `-le`, `-eq` and `-ne`.
- `if grep -q ERROR app.log; then ... fi` works because grep returns 0 on a match.
- The older `[ ... ]`, also called `test`, works in every shell but has more quoting traps. Prefer `[[ ]]` in bash.

For repeated work, use a loop:

- `for f in logs/*.log; do echo "$f: $(grep -c ERROR "$f")"; done` prints an error count for each file.
- `while IFS= read -r line; do ...; done < app.log` reads a file line by line. `IFS=` stops read from trimming spaces at the ends, and `-r` keeps backslashes as they are.

A function is a named group of commands, a small checklist inside the big one, such as `log() { echo "healthcheck: $*" >&2; }`. Inside it, `$1` and friends are the function's own arguments, and `$*` joins them all into one string. `local` keeps a variable from leaking out of the function. The line `return 1` sets the function's exit code, which `if` and `||` can test. And `>&2` sends a message to stderr, so it never mixes with the script's real output.

It still has Monday's flaw, though: a failed step doesn't stop it. Next, we'll fix that."""

S[6]["h"] = "Safe scripts: strict mode, trap and ShellCheck"
S[6]["body"] = """Remember the checklist that said "all done" after step two failed? That is bash's default. A failed command does not stop the script, a typo in a variable name becomes an empty string, and a pipe hides failures. One line at the top fixes most of that: `set -euo pipefail`.

- `-e` exits as soon as a command fails. Commands in an `if` test or before `&&` and `||` are exempt, because there a failure is expected.
- `-u` makes an unset variable an error. Under it, `echo "deploying to $DEPLOY_DIR"` stops with `DEPLOY_DIR: unbound variable` instead of deploying to an empty path.
- `-o pipefail` makes a pipe fail when any part fails. `cat nope.txt | sort` exits 0 without it and 1 with it.

Strict mode has a cost. Because grep exits 1 when it finds nothing, under `-e` an empty search ends your script. Write `grep -q FATAL app.log || true` when no match is fine.

For a variable that must be set, `${DIR:?DIR is not set}` stops the script with that message. This guard matters most before a delete. With an empty `DIR`, the line `rm -rf "$DIR/"*` expands to every folder under `/`. The gentler form `${DELAY:-2}` uses 2 when DELAY is unset, which is how `healthcheck.sh` gets its defaults.

To clean up whatever happens, use `trap 'cleanup commands' EXIT`. It is the same `trap` that caught SIGTERM in Day 6's worker. `EXIT` is bash's name for the moment the script ends, on success or failure. So temp files made with `mktemp`, which creates a file with a unique name and prints it, always get deleted.

Run ShellCheck on every script: `shellcheck script.sh`. It is in the lab container, and on a Mac you run `brew install shellcheck`. It knows hundreds of bash traps and explains each one with a code. For an unquoted variable it reports SC2086, "Double quote to prevent globbing and word splitting." ShellCheck exits non-zero when it finds problems, so CI can run it too.

**Start every script with `set -euo pipefail`, and let ShellCheck read it before anyone runs it.**

Bash has limits. Once a script needs real data structures or grows past about a hundred lines, write it in a programming language such as Python instead. Part 4 shows how. For a short checklist like the worked example's health check, bash is the right tool."""

L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = "The last step of a deploy pipeline is often a smoke test much like `healthcheck.sh`: a quick check that the new version answers at all. It is a short strict-mode script that exits non-zero and stops the rollout when the new version does not answer. In a well-run team, engineers reach servers over SSH with keys and a shared config file, never with passwords. The same teams run ShellCheck in CI on every script in the repository."

W = L["worked"]["steps"]
W[0]["say"] = "Save `healthcheck.sh` (below) in `~/code/hello-devops` and make it executable. ShellCheck prints nothing and exits 0, which means it found nothing to warn about. `bash -n` checks the syntax without running anything."
W[1]["say"] = "With the app stopped, curl cannot connect: it prints nothing and exits 7. The script retries, then fails the way CI needs, with exit code 1. Here `RETRIES` and `DELAY` are environment variables set for this one run, so the test is quick."
W[2]["say"] = "Start the app in a second terminal with `python app.py` (in your venv from Day 2). Both checks pass and the exit code is 0. With `2> /dev/null` the log lines disappear, and `&&` runs the next step only after success."
W[3]["say"] = "Wrong usage is a different failure, so it gets its own exit code, 2, and a usage line on stderr. A caller can tell \"the app is down\" apart from \"you called me wrong\"."
W[4]["say"] = "Now break readiness, the app's answer to \"can you do real work?\". Restart the app as `REDIS_HOST=127.0.0.1 python app.py`, where no Redis runs. Then `/healthz` still answers 200, because the process is alive, but `/readyz` answers 503, so the script fails on readiness."
W[5]["say"] = "In CI, the script is one step. GitHub Actions (Day 24) runs it and fails the job on any exit code other than 0. You add no extra code for that, because the exit code is all CI looks at."

T = L["task"]
T["steps"] = [
    "On your Mac, run `ls ~/.ssh`. If there is no `id_ed25519`, create a key pair with a passphrase.",
    "Give the VM your public key: run `multipass transfer ~/.ssh/id_ed25519.pub devbox:mac.pub`, then add that file's line to `~/.ssh/authorized_keys` inside the VM.",
    "Find the VM's address with `multipass info devbox`, add a `Host devbox` entry to `~/.ssh/config`, and run `ssh devbox uptime`. Answer the fingerprint question once.",
    "Write `log-alert.sh`. It takes a log file and a threshold, counts the ERROR lines, prints the count, and exits 1 if the count reaches the threshold, otherwise 0. Use strict mode, quote every variable and check that the file exists.",
    "Make it print a usage line to stderr and exit 2 when it gets the wrong number of arguments.",
    "Run ShellCheck until it is quiet. Test the script on `app.log` with thresholds 3 and 10, printing the exit code each time.",
    "Copy the script and `app.log` to the VM with scp, and the `logs` folder with rsync. Run the rsync twice and compare the two outputs.",
    "Run the script on the VM from your Mac in one line: `ssh devbox './log-alert.sh app.log 3'; echo $?`.",
    "When you have finished Part 1, delete the VM with `multipass delete devbox`. Older Multipass versions also need `multipass purge`.",
]
T["hints"] = [
    "`[[ $# -eq 2 ]] || usage` checks the argument count in one line.",
    "`grep -c` exits 1 when the count is zero, so put `|| true` inside the `$( )` to keep strict mode from stopping the script.",
    "Inside the VM, `cat ~/mac.pub >> ~/.ssh/authorized_keys` adds the key without replacing what is there.",
]

L["explain_back"]["answer"] = "The `-e` part stops the script when a command fails, so a failed build does not go on to deploy. The `-u` part turns an unset variable into an error, so a typo like `$DEPLOY_DIRR` stops the script instead of becoming an empty path. With `-o pipefail` a pipe fails when any part fails, so `build | tee build.log` reports the build's failure instead of tee's success. Because grep returns 1 when it finds nothing, you write `grep ... || true` when no match is acceptable."

L["recap"] = [
    "Exported variables are copied to child processes, and nothing flows back to the parent.",
    "The shell finds commands through PATH; `which` and `type` show what will run, and 127 means not found.",
    "apt, dnf, apk and brew install software; scripts and Dockerfiles use `apt-get`.",
    "SSH keys: the private key stays home, the public key goes in `authorized_keys`, and `~/.ssh/config` names hosts.",
    "Scripts need a shebang, `chmod +x`, quoted `\"$var\"` and explicit exit codes; start them with `set -euo pipefail` and run ShellCheck.",
    "Bash suits short checklists; past about a hundred lines or for real data structures, use Python (Part 4).",
]

C = L["check"]
C[0]["q"] = "A script with `set -e` runs `count=$(grep -c TODO notes.md)`, and notes.md has no TODO lines. What happens?"
C[0]["why"] = "grep -c prints 0 but exits 1 when nothing matches, and set -e stops on that. Add `|| true` inside the `$( )` if zero is fine."
C[1]["why"] = "An export only lives in the shell where you ran it. A startup file sets it again in every new shell."
C[2]["why"] = "Double quotes expand the variable but stop word splitting. Single quotes would pass the text `$file` itself."

I = L["interview"]
I[0]["a"] = "It makes bash stop on the first failing command (-e), treat unset variables as errors (-u) and fail a pipeline when any part fails (-o pipefail). Together they stop a script from carrying on after a failure and reporting success. The catch is that some commands use non-zero codes for normal results. For example, grep returns 1 for no match, so you add `|| true` where that is fine. Also, `-e` has exceptions inside conditions, so treat it as a safety net and still check the important steps yourself."
I[1]["a"] = "You generate a key pair. The private key stays on your machine and the public key goes into the server's `~/.ssh/authorized_keys`. When you connect, the server sends a challenge that only the holder of the private key can sign. It checks the signature with the public key, so the private key never crosses the network. The client also checks the server's host key against `known_hosts`, which protects you from talking to an impostor."
I[2]["a"] = "Running `./script.sh` starts a new bash process, a child of your shell. The child gets a copy of the parent's environment, and an export in the child changes only that copy, which disappears when the child exits. To change your current shell you `source` the file, which runs its lines in the current process. The same rule is why `cd` inside a script does not move your terminal."

L["deeper"]["body"] = """A script that works on your laptop can still break on a server or in CI.

Start with the version. The Mac's own bash is old: macOS still ships bash 3.2 from 2007, and its default shell has been zsh since 2019. A script with `#!/usr/bin/env bash` runs under that bash 3.2 unless you installed a newer one with Homebrew. Linux servers and CI runners have bash 5. So avoid bash 4 features in scripts you share, such as associative arrays (`declare -A`) and `mapfile`. Everything in `healthcheck.sh` works in both versions.

Strict mode is also a trade-off, and some experienced engineers argue against `set -e` ([one such argument](https://jmmv.dev/2018/03/shell-readability-strict-mode.html)). Its exceptions are subtle. It does not fire inside `if` tests, on the left of `&&` or `||`, or inside a function called from such a place. A script can therefore keep running after a failure you expected to stop it. The usual answer is to keep strict mode as a safety net and still check the steps that matter explicitly, as `healthcheck.sh` does with `check /healthz || exit 1`.

When a script misbehaves, make it show its work. Run it with `bash -x script.sh`, or put `set -x` near the top. Then bash prints every command after expansion, with a `+` in front, before running it. You see the real values of variables and the real result of each glob, which is Day 3's `echo` habit, built in. Turn it off again with `set +x`.

For scripts that run in CI, send messages for humans to stderr and keep stdout for data. `healthcheck.sh` does this with its `log` function. Then `./healthcheck.sh 2> /dev/null` stays quiet, and a later step can still pipe the real output into jq or grep without the chatter getting in the way."""

L["closing"] = """We started on a Monday, with a check done by hand for the third time and a first checklist that said "all done" after a failed step. Now the check is `healthcheck.sh`: it retries, stops on the first real failure, and tells CI the truth with one number.

Open any script you have, in the lab or elsewhere, and look at its first two lines. If `set -euo pipefail` is not there, ask what happens when step two fails.

That ends Part 1. Next, we'll look at Git, the notebook where every saved page keeps a photo of the last one. The question it answers: how do you change your work freely and still get yesterday's version back?"""

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d07 written")
