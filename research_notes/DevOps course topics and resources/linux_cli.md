# Teaching the Linux command line to a DevOps beginner (5 lessons, ~40 min each)

Audience: an experienced Kotlin/JVM engineer with no Linux admin background, on an Apple Silicon Mac, practising for free on their own machine. Research date: October 2026.

**How things were checked (read this first)**
- **[ran locally]** means I ran the command in this research sandbox and pasted the real output: Ubuntu 24.04.5 LTS, GNU bash 5.2.21, GNU grep 3.11, GNU sed 4.9, mawk 1.3.4 (the default `awk` on Ubuntu), jq 1.7, systemd 255. Long paths are shortened. Output will match on any Ubuntu 24.04 container or VM, apart from timestamps, PIDs and sizes.
- The Missing Semester (MIT) material comes from the course's own GitHub source (`missing-semester/missing-semester`, last commit 2026-10-08), which I cloned and read. Software Carpentry material comes from `swcarpentry/shell-novice` (last commit 2026-10-08), also cloned and read. The ShellCheck, jq, explainshell, tldr, Multipass and Lima READMEs and GitHub's SSH documentation were also read from GitHub.
- WebFetch was blocked for jvns.ca, freecodecamp.org and most documentation sites. A URL marked "(search)" appeared in search results but I could not open the page, so its content comes from the search snippet only. A URL marked "(opened)" was read in full, either directly or through its GitHub source.
- YouTube: the Missing Semester video IDs come from the `video: id:` front matter in the official course repository (opened). Other video IDs appeared only inside third-party index URLs, and I mark those "verify before publishing".

**Sample data used by every lesson.** Give learners these two files on day 1, so that grep, pipes and awk all run on the same data. All the expected outputs below come from these files.

`app.log`
```
2026-10-30T09:00:01Z INFO  server started on port 8080
2026-10-30T09:00:05Z INFO  GET /health 200 3ms
2026-10-30T09:01:12Z WARN  slow query took 1200ms
2026-10-30T09:02:30Z ERROR database connection refused
2026-10-30T09:02:31Z INFO  retrying database connection
2026-10-30T09:02:35Z error timeout talking to payments-api
2026-10-30T09:03:00Z INFO  GET /orders 500 45ms
2026-10-30T09:03:10Z ERROR NullPointerException in OrderService
2026-10-30T09:04:00Z INFO  GET /health 200 2ms
```
`access.log` (nginx/Apache "combined"-style, shortened; the IPs are from the documentation ranges 192.0.2.0/24, 198.51.100.0/24 and 203.0.113.0/24)
```
203.0.113.5 - - [30/Oct/2026:09:00:01 +0000] "GET / HTTP/1.1" 200 512
198.51.100.7 - - [30/Oct/2026:09:00:02 +0000] "GET /login HTTP/1.1" 200 1024
203.0.113.5 - - [30/Oct/2026:09:00:03 +0000] "POST /login HTTP/1.1" 302 0
192.0.2.44 - - [30/Oct/2026:09:00:04 +0000] "GET /admin HTTP/1.1" 404 128
203.0.113.5 - - [30/Oct/2026:09:00:05 +0000] "GET /orders HTTP/1.1" 500 64
198.51.100.7 - - [30/Oct/2026:09:00:06 +0000] "GET /orders HTTP/1.1" 200 2048
192.0.2.44 - - [30/Oct/2026:09:00:07 +0000] "GET /wp-login.php HTTP/1.1" 404 128
203.0.113.5 - - [30/Oct/2026:09:00:08 +0000] "GET /health HTTP/1.1" 200 2
```
Field numbers in `access.log` when split on spaces: `$1` = IP, `$9` = status code, `$10` = bytes.

---

## Key question 1: What teaching order makes each concept build intuition?

### Takeaway
Both established beginner curricula start with "what is the shell and how does it read your line" and end with scripts. In between they move from files, to filters, to pipes, to loops and scripts. Three ideas unlock almost everything later, so introduce them early and keep returning to them: (1) a command line is split on spaces into a program plus a list of string arguments; (2) **the shell expands globs, variables and quotes before the program runs**; (3) every program has stdin, stdout and stderr, plus an exit code where 0 means success. Teach grep with literal strings first and add regular expressions later. Teach exit codes before scripting.

### Cited Findings
- **Software Carpentry's order** (the most widely used beginner shell lesson): 1 Introducing the shell → 2 Navigating files and directories → 3 Working with files and directories → 4 Pipes and filters → 5 Loops → 6 Shell scripts → 7 Finding things (grep, find). Learning objectives, in order: "Explain the similarities and differences between a file and a directory", "Translate an absolute path into a relative path", "Use options and arguments to change the behaviour of a shell command", "Demonstrate the use of tab completion", then delete/copy/move, then "Explain the advantage of linking commands with pipes and filters", "Redirect a command's output to a file", "Explain what usually happens if a program or pipeline isn't given any input", then loops ("Explain the difference between a variable's name and its value", "Explain why spaces and some punctuation characters shouldn't be used in file names"), then scripts, then grep/find ("Use the output of one command as the command-line argument(s) to another command", "Explain what is meant by 'text' and 'binary' files") — [SWC episodes, GitHub source (opened)](https://github.com/swcarpentry/shell-novice/tree/main/episodes); rendered lesson at [swcarpentry.github.io/shell-novice](https://swcarpentry.github.io/shell-novice/) (search; URL also in the repo's config.yaml).
- SWC targets "people who have never used the command line before" — [ecosyste.ms project listing (search)](https://awesome.ecosyste.ms/projects/github.com%2Fswcarpentry%2Fshell-novice). A workshop listing found by search (I did not identify the exact page) says that if you can already manipulate files, search with grep and find, and write simple loops and scripts, the lesson "is probably too basic" for you. That matches the scope of SWC's episode list.
- **Missing Semester's 2026 order** (lecture 1): what is the shell / terminal → why care → navigating (prompt, `date`, `echo`, arguments, quoting spaces, `man`, `--help`, `tldr`, `cd`, `pwd`, absolute vs relative paths, `.` and `..`) → what is available (`$PATH`, `which`, `ls`) → simple tools (`cat`, `sort`, `uniq`, `head`, `tail`, `grep`, `sed`, `find`, `awk`) → pipes → redirects and `tee` → `if`/`test`/`[[ ]]` → loops → `$(...)` → scripts — [MS 2026 "Course Overview + Introduction to the Shell", GitHub source (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); page [missing.csail.mit.edu/2026/course-shell](https://missing.csail.mit.edu/2026/course-shell) (search).
- Lecture 2 ("Command-line Environment") then covers: arguments and flags conventions → globbing → streams (stdin/stdout/stderr) → environment variables → return codes (`$?`, `&&`, `||`) → signals → users, files and permissions → remote machines (ssh) → multiplexers → dotfiles → aliases — [MS 2026 Command-line Environment, GitHub source (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- **Command anatomy, as MS explains it:** "The shell parses the command by splitting it by whitespace, and then runs the program indicated by the first word, supplying each subsequent word as an argument." To pass an argument containing spaces, quote it (`"My Photos"`) or escape it (`My\ Photos`) — [MS 2026 lecture 1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
- "Arguments are plain strings in shell, and it is up to the program how to interpret them... `ls -l folder/` [executes] `/bin/ls` with arguments `['-l', 'folder/']`." Flag conventions: `-a` and `--all` are equivalent; single-dash flags can be grouped (`ls -la`); order usually doesn't matter; the dashes are a convention, not a rule — [MS 2026 lecture 2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- **Help first:** "Perhaps the most important command when you're starting out is `man`... You can also usually get a short version of the help by passing `--help`". MS recommends `tldr` for example-driven help — [MS 2026 lecture 1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). tldr can be installed with `brew install tlrc` (official Rust client) or `pipx install tldr`, or used through a web client at tldr.inbrowser.app — [tldr-pages README (opened)](https://github.com/tldr-pages/tldr).
- **explainshell** "match[es] command-line arguments to their help text": it parses man pages, builds a syntax tree of the command line with bashlex, and links each argument to the matching man page text — [explainshell README (opened)](https://github.com/idank/explainshell); site [explainshell.com](http://www.explainshell.com).
- Reading `--help` output: `grep --help | head -2` prints `Usage: grep [OPTION]... PATTERNS [FILE]...` and `Search for PATTERNS in each FILE.` In this notation `[...]` means optional and `...` means "may repeat" — [ran locally].
- `man` pages open in the pager `less`. Its own help lists `h` = help, `q` = quit, `/pattern` = search forward, `n` = repeat the search — [ran locally: `less --help`].
- **Globs before grep:** "the shell will search for files... matching the pattern `*.py`... So if our folder has `main.py` and `utils.py` then the `rm` program will receive arguments `['main.py', 'utils.py']`" — [MS 2026 lecture 2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). SWC introduces wildcards in episode 3, before pipes (episode 4) and grep (episode 7) — [SWC episodes (opened)](https://github.com/swcarpentry/shell-novice/tree/main/episodes).
- **grep is regex-based, but teach it literally first.** MS: "`pattern` is actually a _regular expression_". SWC's grep sequence uses only literal words until the very end: `grep not` → `grep The` → `-w` → a quoted phrase with `-w` → `-n` → `-n -w` → `-n -w -i` → `-n -w -v` → `-r` → `--help` → finally `grep -E "^.o"` as "a taster" of regex — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md); [MS 2026 lecture 1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
- **Exit codes before scripts:** "zero means everything went well whereas nonzero means some issues were encountered... `&&` and `||`... operate on the return code of programs"; `if` and `while` also branch on return codes — [MS 2026 lecture 2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- Julia Evans wrote "What helps people get comfortable on the command line?" (2023-08-08). I could not open it; discussion threads mention a pleasant terminal app and customisation as factors — [jvns.ca post (search)](https://jvns.ca/blog/2023/08/08/what-helps-people-get-comfortable-on-the-command-line-/).

### Inferences
- **Suggested arc across the 5 lessons** (keeps the user's lesson boundaries and adds the "hooks" each lesson needs):
  1. L1: terminal vs shell → command anatomy (argv as a `List<String>`) → help (`--help`, `man`, `tldr`, explainshell) → filesystem tree and paths → create/copy/move/delete → **globs** → `PATH`/`which`/`type` (why `ls` works) → quoting names with spaces.
  2. L2: `cat`/`less`/`head`/`tail`/`tail -f` → grep with literal strings and flags → **what a regex is** (a tiny pattern language; contrast with globs from L1) → `grep -E` → `find` (quote the pattern; L1 globs come back). Show `|` once as a preview ("feed the left side's output into grep") and formalise it in L3.
  3. L3: the three streams → `|` → `>`/`>>`/`<` → `2>`/`2>&1`/`/dev/null` → **exit codes** (`$?`, `&&`, `||`, `grep -q`) → filters (`sort`, `uniq -c`, `wc`, `cut`, `tr`) → `awk` (columns) → `sed` (substitute) → `tee` → `xargs` → `jq` (the same idea for JSON).
  4. L4: users/root/`sudo` → `ls -l` anatomy → rwx → octal → `chmod`/`chown` → processes/PIDs → signals and `kill` → jobs (`&`, Ctrl-Z, `fg`/`bg`) → services (`systemctl`) → logs (`journalctl`) → resources (`df`/`du`/`free`) → ports.
  5. L5: variables vs environment variables → `export` → `PATH` again → dotfiles → package managers → SSH keys → `~/.ssh/config` → `scp`/`rsync` → scripts (which reuse everything: quoting from L1, exit codes from L3, `chmod +x` from L4).
- **The "two interpreters" frame suits a JVM engineer.** Every line passes through bash first (splitting, globs, `$vars`, quotes, redirects), then through the program's own parser (flags). Most beginner bugs come from not knowing which of the two did what. Show `echo` as the debugger: `echo rm *.log` shows what `rm` would receive.
- Teach the man page *reading* skill explicitly (SYNOPSIS brackets, `/` to search for a flag, `q` to quit), because learners will need it alone later. Pair it with explainshell for decoding one-liners copied from Stack Overflow or an AI assistant.

### Gaps
- I found no empirical study comparing teaching orders. The order above comes from two well-established curricula (SWC, MIT) plus judgement.
- I could not read Julia Evans' post, so its specific recommendations are not captured.

---

## Lesson 1: The shell and the file system — what to teach and how

### Takeaway
Start with a mental model (terminal → shell → program with arguments), then navigation (`pwd`, `ls`, `cd`, absolute vs relative paths, `~ . ..`), then file manipulation (where the safety warning "deleting is forever" belongs), then globs and `PATH`. The single most valuable habit is: "the shell rewrites your line before running it; use `echo` to see what it will run."

### Cited Findings

**Concepts in teaching order** (each with a one-line explanation; analogies are teaching suggestions, not sourced facts)
1. **Terminal vs shell vs prompt.** The terminal is "the visual interface to a shell"; the prompt (e.g. `missing:~$`) shows the machine, the current directory (`~` = home) and `$` meaning you are not root — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). *Analogy:* the terminal is the chat window; the shell is the assistant on the other side who interprets each line and runs programs for you.
2. **Which shell?** macOS has used zsh as its default login and interactive shell since Catalina (2019); bash is still installed — [The Next Web (search)](https://thenextweb.com/news/why-does-macos-catalina-use-zsh-instead-of-bash-licensing); [Apple Support Community thread (search)](https://discussions.apple.com/thread/250989957). Linux servers and Ubuntu containers use bash ([ran locally]: `bash --version` → `GNU bash, version 5.2.21`). Check with `echo $SHELL` — [MS 2026 L1 exercise 1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
3. **Command anatomy: `command [-options] [arguments]`.** The line is split on whitespace; the first word is the program; the rest are string arguments; flags begin with `-` or `--` — [MS 2026 L1 and L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). *Analogy for Kotlin devs:* `fun main(args: Array<String>)`. The shell builds `args`; the program decides what `-l` means.
4. **Getting help:** `cmd --help`, `man cmd` (navigate with `/word`, `n`, `q`), `tldr cmd`, explainshell — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); [explainshell README (opened)](https://github.com/idank/explainshell).
5. **The file system is one tree rooted at `/`.** Absolute paths start with `/`; relative paths are resolved from the current working directory; `.` = this directory, `..` = parent; `~` = home; `pwd` prints where you are; `cd` moves you; Tab completes paths — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); [SWC 02-filedir objectives (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/02-filedir.md). *Analogy:* a package hierarchy (`com.acme.orders`); an absolute path is a fully-qualified name, a relative path is resolved against your current "package".
6. **Create, copy, move, delete:** `mkdir`, `touch`, `cp`, `mv` (also renames), `rm`, `rm -r`. **"Deleting Is Forever":** "The Unix shell doesn't have a trash bin that we can recover deleted files from" — [SWC 03-create (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/03-create.md).
7. **Globs (wildcards):** `*` (zero or more of anything), `?` (exactly one character), `{a,b}` (brace expansion into several words). The shell expands them **before** the program runs — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). zsh also supports `**` for recursive matches — same source. *Analogy:* the shell does a find-and-replace on your line before pressing Enter for you.
8. **How the shell finds programs: `$PATH`.** The shell searches the `:`-separated directories in `$PATH`; `which echo` shows which file runs; `cd` is a shell builtin, not a program (`which cd` finds nothing) — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). [ran locally]: `type cd` → `cd is a shell builtin`; an unknown command gives `command not found` with exit code `127`.
9. **Names with spaces:** quote (`"My Photos"`) or escape (`My\ Photos`) — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). SWC: "It is simpler to avoid using spaces (or other special characters) in filenames" — [SWC 05-loop (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/05-loop.md).

**Misconceptions to address**
- "`rm` has an undo / goes to Trash." It doesn't — [SWC 03-create (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/03-create.md).
- "`rm *.py` passes `*.py` to rm." The shell expands it first — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- "`cd` is a program like `ls`." It's built in. MS has an exercise asking why: a child process cannot change its parent's working directory — [MS 2026 L1 exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
- "A glob that matches nothing disappears." In bash an unmatched glob is passed through literally: `echo *.nomatch` prints `*.nomatch` — [ran locally]. (zsh behaves differently; see Gaps.)
- "Spaces around `=` are fine" (`name = alice`). bash treats `name` as a program name: `name: command not found` — [ran locally]; MS explains that `foo = bar` calls program `foo` with arguments `['=', 'bar']` — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). (Preview here; it matters in L5.)

**Example commands with expected output** [ran locally]
```console
$ pwd
/home/me/lab
$ cd proj/src; pwd
/home/me/lab/proj/src
$ cd ../..; pwd
/home/me/lab
$ echo *.log                  # the shell expands the glob
access.log app.log
$ echo "*.log"                # quotes stop expansion
*.log
$ echo {dev,staging,prod}.env # brace expansion
dev.env staging.env prod.env
$ type cd
cd is a shell builtin
$ which ls
/usr/bin/ls
$ nosuchcommand; echo $?
bash: nosuchcommand: command not found
127
$ ls -l app.log
-rw-r--r-- 1 root root 481 Oct 30 04:37 app.log
```

**Hands-on exercise ideas**
- "Build this tree": give a diagram (`project/{src,logs,config}` with files) and have learners recreate it with `mkdir -p` and `touch`, then check it with `find project` (the `tree` command is not installed in the Ubuntu image) — adapted from the SWC objective "Create a directory hierarchy that matches a given diagram" — [SWC 03-create (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/03-create.md).
- Path translation drill: convert five absolute paths to relative ones from a given `pwd`, and back — [SWC 02-filedir objective (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/02-filedir.md).
- Predict-then-run with `echo`: `echo *.log`, `echo log*`, `echo ?pp.log`, `echo "*.log"` — predict the output first, then run it. The point: you can always check what the shell will pass by putting `echo` in front.
- MS exercises: "What does the `-l` flag to `ls` do? Run `ls -l /`"; "Why does `cd` have to be built into the shell?" — [MS 2026 L1 exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
- Tour `/`: `ls /`, `ls /etc`, `ls /var/log`, `cat /etc/os-release` (in the container).

**Curated resources (L1)**
- Missing Semester 2026, Lecture 1 "Course Overview + Introduction to the Shell": notes [missing.csail.mit.edu/2026/course-shell](https://missing.csail.mit.edu/2026/course-shell) (search; source opened on GitHub); video [youtube.com/watch?v=MSgoeuMqUmU](https://www.youtube.com/watch?v=MSgoeuMqUmU) (ID from the official repo's front matter).
- Software Carpentry "The Unix Shell", episodes 1–3 — [swcarpentry.github.io/shell-novice](https://swcarpentry.github.io/shell-novice/) (search; source opened).
- freeCodeCamp "The 50 Most Popular Linux & Terminal Commands – Full Course for Beginners" (~5 h; use selected chapters) — [youtube.com/watch?v=ZtqBQ68cfJc](https://www.youtube.com/watch?v=ZtqBQ68cfJc) (URL appeared in search results); article [freecodecamp.org/news/learn-the-50-most-used-linux-terminal-commands](https://www.freecodecamp.org/news/learn-the-50-most-used-linux-terminal-commands/) (search).
- "The Linux Command Line" by William Shotts — [linuxcommand.org/tlcl.php](https://www.linuxcommand.org/tlcl.php) (search). The page describes a free Creative Commons PDF ("Fifth Internet Edition"); a 2023 LinuxLinks listing says it may no longer be free — [LinuxLinks (search)](https://linuxlinks.com/excellent-no-charge-books-learn-about-linux/14). Check before linking.
- explainshell — [explainshell.com](http://www.explainshell.com) (opened via README); tldr pages — [tldr.sh](https://tldr.sh/) (opened via README).
- NetworkChuck "Linux for Hackers" EP2 covers "the Linux File System explained in 1,233 seconds" (no direct YouTube URL surfaced) — [Class Central listing (search)](https://www.classcentral.com/course/youtube-linux-for-hackers-and-everyone-free-course-for-beginners-65862).

### Inferences
- Run L1 inside the Ubuntu container from the start (see KQ4), not in macOS zsh, so that every later output matches the lesson text.
- Teach `echo` as "the shell debugger" in L1; it pays off in L3 (redirections) and L5 (quoting).
- A JVM engineer will understand the shell faster as a REPL whose "function calls" are external programs that receive `List<String>`.

### Gaps
- I did not verify the exact zsh message for an unmatched glob (by default zsh reports "no matches found" instead of passing the glob through). Verify on a Mac before writing that line.
- I found no sourced, beginner-oriented description of the Filesystem Hierarchy Standard (`/etc`, `/var/log`, `/usr/bin`, `/home`, `/tmp`) in this session. The lesson writer should cite an FHS or Ubuntu doc page.
- macOS's default APFS volume is case-insensitive while Linux file systems are case-sensitive. This is a well-known trap, but I did not find a source for it in this session.

---

## Lesson 2: Reading and searching text (cat, less, head, tail -f, grep, regex, find)

### Takeaway
Move from "look at a file" (`cat`, `less`, `head`, `tail`) to "watch a file" (`tail -f`) to "filter a file" (grep with literal strings, then flags, then regex), and finish with `find`, which searches file *names and metadata* rather than contents. The key distinction to name explicitly: **globs (shell, file names) are not regexes (grep/sed/awk, text)**. See KQ2 below for the full grep progression.

### Cited Findings

**Concepts in teaching order**
1. **`cat file`** prints a whole file; **`head`/`tail`** print the first or last lines — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). *Analogy:* `cat` dumps everything to the console, like printing a whole collection; `head`/`tail` are `.take(10)` and `.takeLast(10)`.
2. **`less file`**: a scrollable pager (`/pattern` to search, `n` for the next match, `q` to quit, `h` for help) — [ran locally: `less --help`]. Use it for big logs instead of `cat`.
3. **`tail -f`** follows a growing file; combine it with `grep --line-buffered` so matches appear immediately. `--line-buffered` exists in both GNU and BSD grep — [macOS-and-Unix book, BSD vs GNU (search; source opened on GitHub)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html).
4. **`grep PATTERN FILE`** "finds and prints lines in files that match a pattern"; the name comes from "global/regular expression/print" — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md). Flags in order: see KQ2.
5. **What a regex is:** a small pattern language for text. GNU grep's basic (BRE) and extended (ERE) syntaxes are "merely different notations for the same pattern-matching functionality"; `-E` selects ERE and `-F` matches fixed strings — [GNU grep manual, Regular Expressions (search)](https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions); see also the free book [learnbyexample: BRE/ERE Regular Expressions (search)](https://learnbyexample.github.io/learn_gnugrep_ripgrep/breere-regular-expressions.html).
6. **`find`** searches by name or metadata, recursively: `find ~/Downloads -type f -name "*.zip" -mtime +30` (zip files older than 30 days); `find ~ -type f -size +100M -exec ls -lh {} \;` (big files); `find . -name "*.py" -exec grep -l "TODO" {} \;` — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). `-exec ... {} \;` runs once per file; `{} +` batches files into one call — [ran locally].
7. **Text vs binary files:** an SWC objective is to "Explain what is meant by 'text' and 'binary' files, and why many common tools don't handle the latter well" — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md).
8. Optional modern alternatives: `ripgrep` (`rg`), "faster and more human-friendly (but less portable)", searches recursively by default; `fd` instead of `find`; `bat` instead of `cat` — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). Servers won't have them, so teach the classics first.

**Misconceptions**
- **Unquoted `find -name *.txt`.** The shell expands `*.txt` first, so `find . -name *.txt` became `find . -name numbers.txt`: "`find` did what we asked; we just asked for the wrong thing." Fix: `find . -name "*.txt"` — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md). ShellCheck flags "Unquoted find/grep patterns" — [ShellCheck README (opened)](https://github.com/koalaman/shellcheck).
- **Glob `*` ≠ regex `*`.** In a glob `*` means "anything"; in a regex `*` means "zero or more of the previous item", and `.` means "any character". [ran locally]: `printf 'a.log\nxlog\n' | grep -c '.log'` → `2` (it matched `xlog` too). Use `'\.log$'` to mean "ends in .log".
- **"`grep "ERROR|WARN"` means ERROR or WARN."** Not in basic regex: `|` is a literal character there, so it matches nothing (exit code 1). Use `grep -E "ERROR|WARN"` — [ran locally].
- **"`cat` a 2 GB log."** Use `less`, `tail -n`, or `grep` instead.

**Example commands with expected output** [ran locally]
```console
$ head -n 2 app.log
2026-10-30T09:00:01Z INFO  server started on port 8080
2026-10-30T09:00:05Z INFO  GET /health 200 3ms
$ tail -n 1 app.log
2026-10-30T09:04:00Z INFO  GET /health 200 2ms
$ tail -f live.log | grep --line-buffered ERROR     # another process appends a line
2026-10-30T09:05:00Z ERROR disk full
^C
$ find proj -name "*.kt"
proj/src/Main.kt
proj/src/Util.kt
$ find proj -type d
proj
proj/logs
proj/src
$ find proj -name "*.log" -mtime +30
proj/logs/old.log
$ find . -name "*.log" -exec grep -l ERROR {} +
./app.log
$ find . -type f -size +10M -exec ls -lh {} \;
-rw-r--r-- 1 root root 50M Oct 30 04:38 ./big.bin
```

**Hands-on exercise ideas**
- "Incident drill": using `app.log`, find (a) every error regardless of case, (b) how many there are, (c) the line numbers, (d) the line after "connection refused". Answers are in KQ2.
- Live tail: open two terminal tabs into the same container (`docker exec -it <name> bash`). In tab A run `tail -f /tmp/live.log | grep --line-buffered ERROR`; in tab B append lines with `echo "... ERROR ..." >> /tmp/live.log`.
- `find` scavenger hunt in `/etc` and `/var/log`: all `*.conf` files, files changed in the last day (`-mtime -1`), directories only, files over 1M.
- SWC "Little Women" / "Tracking a Species" style grep challenges, adapted to logs — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md).

**Curated resources (L2)**
- SWC episode 7 "Finding Things" — [GitHub source (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md); lesson home [swcarpentry.github.io/shell-novice](https://swcarpentry.github.io/shell-novice/).
- GNU grep manual, Regular Expressions chapter — [gnu.org (search)](https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions).
- learnbyexample "CLI text processing with GNU grep and ripgrep", BRE/ERE chapter — [learnbyexample.github.io (search)](https://learnbyexample.github.io/learn_gnugrep_ripgrep/breere-regular-expressions.html).
- Library Carpentry regex intro (linked from SWC for "complex searches") — [librarycarpentry.org/lc-data-intro/01-regular-expressions.html](https://librarycarpentry.org/lc-data-intro/01-regular-expressions.html) (URL taken from the SWC source; not opened).
- Missing Semester 2020 "Data Wrangling" (regex with sed on real SSH logs) — video [youtube.com/watch?v=sz_dsktIjt4](https://www.youtube.com/watch?v=sz_dsktIjt4) (ID from the official repo).
- Akamai Developer (formerly Linode) "Intro to GREP and Regular Expressions" — YouTube ID `Cr9jjBbI2hk` appeared only in a third-party index URL ([letsplayindex (search)](https://www.letsplayindex.com/video/intro-to-grep-and-regular-expressions-akamai-developer-Cr9jjBbI2hk)), so verify `https://www.youtube.com/watch?v=Cr9jjBbI2hk` before publishing.
- Corey Schafer "Linux/Mac Terminal Tutorial: The Grep Command" (2018). Only a Patreon post surfaced — [patreon.com/coreyms (search)](https://www.patreon.com/coreyms/posts/linux-mac-grep-17844354); no YouTube URL was found.
- Julia Evans' "Bite Size Command Line" zine covers grep, find, xargs, awk and sed (paid, about $10–12) — [jvns.ca announcement (search)](https://jvns.ca/blog/2018/08/05/new-zine--bite-size-command-line/); [store (search)](https://store.wizardzines.com/products/bite-size-command-line-1).

### Inferences
- Put a short "regex in 6 symbols" card in L2: `.` `*` `^` `$` `[...]` `\` (BRE), then add `+ ? {n} | ()` with `-E`. Five minutes is enough; L3's sed/awk reuse it.
- Keep `find -exec` to the `{} +` form plus a single `\;` example. Leave `xargs` to L3, where pipes are formal.

### Gaps
- No primary source surfaced comparing `tail -f` with `tail -F` (the latter follows across log rotation). This is relevant for real `/var/log` files, so the lesson writer should check `man tail`.

---

## Key question 2: How should grep be taught from zero (order, flags, small examples)?

### Takeaway
Follow SWC's proven arc (literal string → flags one at a time → recursive → `--help` → regex last), retargeted at log files. A good flag order for DevOps is: plain → `-i` → `-n` → `-c` → `-v` → `-w` → `-E` (alternation) → `-o` → `-A/-B/-C` → `-r` and `-l` → `-q` with exit codes (0 = match, 1 = no match, 2 = error). Introduce each flag with one tiny question it answers ("how many?", "which line?", "what's around it?").

### Cited Findings
- SWC's grep sequence: `grep not haiku.txt` → `grep The` → `grep -w The` → `grep -w "is not"` → `grep -n "it"` → `-n -w` → `-n -w -i` → `-n -w -v` → `grep -r Yesterday .` → `grep --help` → `grep -E "^.o"` — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md).
- SWC reproduces `grep --help`: "PATTERN is, by default, a basic regular expression (BRE)"; `-E` extended, `-F` fixed strings, `-P` Perl, `-i` ignore case, `-w` whole words, `-x` whole lines — [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md).
- MS: grep can take a directory with `-r` to search recursively — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). MS uses `grep -q "pattern" file.txt && echo "Pattern found"` to teach exit codes — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- GNU grep supports `\b` (word boundary), `\<` and `\>` (start and end of word). `-P` (PCRE) works "only if PCRE is available in the system". Backreferences "are very slow" — [GNU grep manual (search)](https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions).
- `-P` is a GNU extension; BSD grep (macOS) "supports `-E` (extended) and `-G` (basic) regex only": `grep -P '\d{3}-\d{4}'` → `grep: invalid option -- P`. The portable form is `grep -E '[0-9]{3}-[0-9]{4}'` — [macOS-and-Unix book (search; source opened)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html).
- Under `set -e`, a grep that finds nothing returns exit code 1 and can stop a script — [kindatechnical strict-mode guide (search)](https://kindatechnical.com/shell-scripting-bash/strict-mode-set-euo-pipefail.html).

**Worked progression with expected output** [ran locally, GNU grep 3.11, on `app.log` and `access.log`]
```console
# 1. Literal search — "show me the errors"
$ grep ERROR app.log
2026-10-30T09:02:30Z ERROR database connection refused
2026-10-30T09:03:10Z ERROR NullPointerException in OrderService

# 2. -i — "logs are inconsistent about case"
$ grep -i error app.log
2026-10-30T09:02:30Z ERROR database connection refused
2026-10-30T09:02:35Z error timeout talking to payments-api
2026-10-30T09:03:10Z ERROR NullPointerException in OrderService

# 3. -c — "how many?"
$ grep -c -i error app.log
3

# 4. -n — "which line, so I can open it in an editor?"
$ grep -n WARN app.log
3:2026-10-30T09:01:12Z WARN  slow query took 1200ms

# 5. -v — "hide the noise"
$ grep -v INFO app.log
2026-10-30T09:01:12Z WARN  slow query took 1200ms
2026-10-30T09:02:30Z ERROR database connection refused
2026-10-30T09:02:35Z error timeout talking to payments-api
2026-10-30T09:03:10Z ERROR NullPointerException in OrderService

# 6. -w — "200 as a whole word, not 2001 or 1200"
$ grep -w 200 access.log | wc -l
4

# 7. -E alternation — and the BRE trap
$ grep -E "ERROR|WARN" app.log
2026-10-30T09:01:12Z WARN  slow query took 1200ms
2026-10-30T09:02:30Z ERROR database connection refused
2026-10-30T09:03:10Z ERROR NullPointerException in OrderService
$ grep "ERROR|WARN" app.log; echo "exit=$?"      # basic regex: | is literal
exit=1

# 8. -o — "print only the matching part" (extract values)
$ grep -o -E "[0-9]+ms" app.log
3ms
1200ms
45ms
2ms

# 9. Context: -A (after), -B (before), -C (both)
$ grep -A1 "connection refused" app.log
2026-10-30T09:02:30Z ERROR database connection refused
2026-10-30T09:02:31Z INFO  retrying database connection
$ grep -B1 -n " 500 " app.log          # with -n, context lines use '-' instead of ':'
6-2026-10-30T09:02:35Z error timeout talking to payments-api
7:2026-10-30T09:03:00Z INFO  GET /orders 500 45ms

# 10. Regex on structure: any 5xx status in the access log
$ grep -E '" 5[0-9]{2} ' access.log
203.0.113.5 - - [30/Oct/2026:09:00:05 +0000] "GET /orders HTTP/1.1" 500 64

# 11. -r and -l — "which files mention it?"
$ grep -r -l ERROR .
./app.log

# 12. -q and exit codes — grep as a condition
$ grep -q ERROR app.log && echo found
found
$ grep nomatch app.log; echo $?
1
$ grep x missing.log; echo $?
grep: missing.log: No such file or directory
2
```

**Regex mini-curriculum to teach alongside** (ordered; each one a one-liner on the logs)
1. Literal text: `grep timeout`.
2. Anchors: `^` = start of line, `$` = end of line: `grep '^2026-10-30T09:0[0-2]'`, `grep 'ms$'`.
3. Any character `.` and escaping `\.`: `'\.php'` vs `'.php'`.
4. Character classes `[0-9]`, `[A-Z]`, negated `[^ ]`.
5. Repetition: `*` (BRE and ERE); `+`, `?`, `{n,m}` (use `-E`).
6. Alternation and groups with `-E`: `(GET|POST) /login`.
7. Word boundaries: `-w` first; `\b` later (GNU).

### Inferences
- Tell learners to **always single-quote grep patterns** (`grep -E '5[0-9]{2}'`), so that `$`, `*`, `|` and `{}` reach grep unchanged. This connects back to L1's "the shell rewrites your line first".
- Teach `-F` for searching literal strings that contain dots or brackets (IP addresses, `[error]`, version numbers). It saves a lot of escaping.
- Teach `grep -E` everywhere instead of BRE backslash forms (`\|`, `\+`). ERE syntax works the same on macOS BSD grep and GNU grep, while `-P` and `\d` do not.

### Gaps
- I didn't find an authoritative list of which GNU-only grep flags (besides `-P`) are missing from current macOS grep. Test the flag list on the learner's Mac before claiming parity.

---

## Lesson 3: Pipes, redirection and text processing

### Takeaway
Present every program as a box with one input pipe (stdin, 0) and two output pipes (stdout 1, stderr 2), plus an exit code. Then `|`, `>`, `>>`, `<`, `2>`, `2>&1` and `/dev/null` are just ways of reconnecting those pipes. The classic DevOps one-liner, `... | sort | uniq -c | sort -rn | head`, is the payoff. `awk` = columns, `sed` = substitutions, `xargs` = turn lines into arguments, `jq` = the same idea for JSON.

### Cited Findings

**Concepts in teaching order**
1. **Streams:** every program has stdin, stdout and stderr; stderr exists "for programs to report warnings and other types of issues, without that output getting parsed by the next command in the chain" — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). *Analogy:* one input port and two output ports (normal output and an error channel), like `System.in`, `System.out` and `System.err` in Java.
2. **Pipe `|`:** "takes the 'standard output'... of the program before the `|` and makes it be the standard input of the program after"; most tools read stdin when no file is given — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). All the programs in a pipeline start **at the same time** and stream data: "the shell is not first calling cat, then grep, and then uniq" — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). *Analogy:* a Kotlin `Sequence` chain (`lines.filter{}.map{}.groupingBy{}`) that processes lazily, one line at a time, with each stage a separate process.
3. **Redirects:** `>file` overwrites; `>>file` appends; `<file` reads stdin from a file — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). With `>`, "If the file exists already, it will be silently overwritten, which may lead to data loss" — [SWC 04-pipefilter (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md).
4. **stderr and `/dev/null`:** `ls /nonexistent | grep pattern` still shows the error "because stderr is not piped"; `2>/dev/null` discards it — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). `cmd > file 2>&1` sends both streams to the file, and **order matters** (see the examples) — [ran locally]; reference: [GNU bash manual, Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) (URL from the MS source; not opened).
5. **Exit codes and `&&` / `||`:** `$?` holds the last exit code; `&&` runs the next command only on success, `||` only on failure; `true` and `false` are programs — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
6. **Filters:** `sort` (sorted lines), `uniq` ("eliminates *consecutive* duplicate lines"), `head`/`tail` — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); `wc -l` (count lines), `cut -d' ' -f1` (pick a field), `tr` (translate or squeeze characters) — [ran locally].
7. **`awk`** "is built for parsing" files: `awk '{print $2}'` prints the second whitespace-separated column, and `-F,` switches to commas; awk can also filter rows and compute aggregates — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). Note: on Ubuntu 24.04 `awk` is **mawk** 1.3.4, not gawk — [ran locally].
8. **`sed`** is "a programmatic file editor": `sed -i 's/pattern/replacement/g' file`. `s/` means substitute, `/g` means all occurrences on the line, `-i` edits in place, and the pattern is a regex — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). The `-i` syntax differs on macOS (see KQ4).
9. **`tee`** writes stdin to stdout *and* to a file: `verbose cmd | tee verbose.log | grep CRITICAL` — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
10. **`xargs`** "converts lines from stdin into command arguments" (an MS exercise) — [MS 2026 L1 exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). Use `find -print0 | xargs -0` for names with spaces — [macOS-and-Unix book (search; source opened)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html); [ran locally].
11. **`jq`** is "a lightweight and flexible command-line JSON processor akin to `sed`, `awk`, `grep`, and friends for JSON data". Docs: jqlang.org; playground: play.jqlang.org — [jq README (opened)](https://github.com/jqlang/jq).
12. **Command substitution `$(cmd)`** puts a command's output into a variable or an argument. Prefer it to backticks "as it can be nested" — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).

**Misconceptions**
- **`>` vs `>>`:** `>` silently truncates — [SWC 04-pipefilter (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md). [ran locally]: `echo one > f; echo two > f; cat f` → `two`; with `>>` → `one`/`two`.
- **Redirecting into the file you're reading:** `sort -n lengths.txt > lengths.txt` "may give you incorrect results and/or delete the contents" — [SWC 04-pipefilter (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md). [ran locally]: `sort copy.log > copy.log; wc -l copy.log` → `0 copy.log` (the shell truncates the file before `sort` even starts).
- **`uniq` without `sort`** only removes *adjacent* duplicates — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); [ran locally] (see the examples).
- **`2>&1` order:** `cmd 2>&1 > file` still prints errors to the terminal; `cmd > file 2>&1` captures both — [ran locally].
- **"The pipe carries errors too."** It doesn't; only stdout goes through — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- **`xargs` and spaces in names:** `find ... | xargs ls` splits `my file.txt` into `my` and `file.txt` — [ran locally].
- **jq output keeps JSON quotes** unless you pass `-r` — [ran locally].
- **"A pipeline's exit code is the worst stage's."** By default it's the *last* stage's; see `pipefail` in L5 — [ran locally].

**Example commands with expected output** [ran locally]
```console
# Top client IPs (the classic)
$ cut -d" " -f1 access.log | sort | uniq -c | sort -rn | head -3
      4 203.0.113.5
      2 198.51.100.7
      2 192.0.2.44
$ awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3   # same result

# Why sort before uniq
$ cut -d" " -f1 access.log | uniq -c
      1 203.0.113.5
      1 198.51.100.7
      1 203.0.113.5
      ...(8 lines, all counts 1)

# Status code histogram, 5xx rows, total bytes
$ awk '{print $9}' access.log | sort | uniq -c | sort -rn
      4 200
      2 404
      1 500
      1 302
$ awk '$9 >= 500' access.log
203.0.113.5 - - [30/Oct/2026:09:00:05 +0000] "GET /orders HTTP/1.1" 500 64
$ awk '{sum += $10} END {print sum}' access.log
3906

# Counting, translating
$ wc -l app.log access.log
   9 app.log
   8 access.log
  17 total
$ echo "Hello World" | tr a-z A-Z
HELLO WORLD
$ echo "a,b,,c" | tr -s ,
a,b,c

# sed: substitute, print a range, capture groups
$ sed 's/ERROR/ERR/' app.log | grep ERR
2026-10-30T09:02:30Z ERR database connection refused
2026-10-30T09:03:10Z ERR NullPointerException in OrderService
$ sed -n '3,4p' app.log
2026-10-30T09:01:12Z WARN  slow query took 1200ms
2026-10-30T09:02:30Z ERROR database connection refused
$ sed -E 's/^([^ ]+) ([A-Z]+) .*/\2 at \1/' app.log | head -2
INFO at 2026-10-30T09:00:01Z
INFO at 2026-10-30T09:00:05Z

# Redirection and stderr
$ ls nope app.log > out.txt
ls: cannot access 'nope': No such file or directory     # stderr still on screen
$ cat out.txt
app.log
$ ls nope app.log > out.txt 2>&1; cat out.txt
ls: cannot access 'nope': No such file or directory
app.log
$ ls nope app.log 2>&1 > out.txt                        # wrong order
ls: cannot access 'nope': No such file or directory
$ ls nope 2>/dev/null; echo $?
2

# tee and xargs
$ grep ERROR app.log | tee errors.txt | wc -l
2
$ find . -name "*.tmp" | xargs rm -v
removed './a.tmp'
removed './b.tmp'
$ find . -name "*.txt" -print0 | xargs -0 ls
./errors.txt
./f.txt
./my file.txt
./out.txt

# jq on a kubectl-like JSON document
$ cat pods.json
{"items":[{"name":"api-7d9f","status":"Running","restarts":0},{"name":"worker-5c2a","status":"CrashLoopBackOff","restarts":12},{"name":"db-0","status":"Running","restarts":1}]}
$ jq -r '.items[].name' pods.json
api-7d9f
worker-5c2a
db-0
$ jq -r '.items[] | select(.status != "Running") | .name' pods.json
worker-5c2a
$ jq '.items | length' pods.json
3
$ jq -r '.items[] | "\(.name)\t\(.restarts)"' pods.json
api-7d9f	0
worker-5c2a	12
db-0	1
$ jq '.items[].name' pods.json          # without -r: JSON strings keep their quotes
"api-7d9f"
"worker-5c2a"
"db-0"
```

**Hands-on exercise ideas**
- Build the "top IPs" pipeline **one stage at a time**, running it after each `|` to see the intermediate output. This is the key habit.
- Status-code report: count 2xx/3xx/4xx/5xx; list the paths that returned 404 (`awk '$9 == 404 {print $7}'`).
- Make the "redirect into the same file" mistake on purpose, on a copy, and explain why the file ended up empty.
- Dissect MS's SSH-log pipeline (`journalctl ... | grep "Disconnected from" | sed -E ... | sort | uniq -c | sort -nk1,1 | tail -n10 | awk '{print $2}' | paste -sd,`) stage by stage — [MS 2026 L1 + exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
- MS exercise: "Use pipes to find the 5 most common file extensions in your home directory" — same source.
- jq: from a saved API response (`curl -s https://api.github.com/repos/jqlang/jq > repo.json`, if network is available), extract `.stargazers_count` and `.license.name`. Offline alternative: practise in play.jqlang.org.

**Curated resources (L3)**
- Missing Semester 2026 L2 "Command-line Environment" (streams, return codes) — [GitHub source (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); video [youtube.com/watch?v=ccBGsPedE9Q](https://www.youtube.com/watch?v=ccBGsPedE9Q) (ID from the official repo).
- Missing Semester 2020 "Data Wrangling" (sed/awk/sort/uniq on real logs) — [youtube.com/watch?v=sz_dsktIjt4](https://www.youtube.com/watch?v=sz_dsktIjt4) (ID from the official repo).
- SWC episode 4 "Pipes and Filters" — [GitHub source (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md).
- jq docs [jqlang.org](https://jqlang.org) and playground [play.jqlang.org](https://play.jqlang.org) (both linked from the jq README, opened).
- GNU bash manual: [Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) (URL from the MS source).
- Julia Evans "Bite Size Command Line" (paid zine; awk/sed/xargs pages) — [jvns.ca (search)](https://jvns.ca/blog/2018/08/05/new-zine--bite-size-command-line/).

### Inferences
- Teach `awk` only as "print column N" plus "filter rows where column N matches a condition" plus "sum a column". Teach `sed` only as `s/old/new/g` plus `-n 'X,Yp'`. That covers most DevOps one-liners; anything bigger belongs in a real language.
- `jq` fits naturally at the end of L3 because Kubernetes, cloud CLIs and HTTP APIs all output JSON. Frame it as "grep/awk for JSON".
- Introduce exit codes in L3, not L5, so that `&&`, `||` and `grep -q` feel natural before `if` and `set -e`.

### Gaps
- I didn't verify whether the default `awk` on macOS behaves identically to mawk for the examples above. They use only POSIX awk features, so they should, but this was not tested on a Mac.

---

## Lesson 4: Users, permissions, processes and services

### Takeaway
Two mental models carry this lesson: (1) **every file has an owner, a group and three rwx triplets; every process runs as a user**, and root bypasses the checks; (2) **every running thing is a process with a PID, and you talk to processes with signals**. systemd/`systemctl` is "the process manager for long-running services", and `journalctl` is "its log reader". Practical warning: **systemd does not run inside a plain Docker container**, so this lesson needs a VM (see KQ4).

### Cited Findings

**Concepts in teaching order**
1. **Users, UIDs, root, `sudo`:** `whoami` gives your name, `id -u` your numeric UID; `sudo command` runs the command as root, "which can bypass most permissions in the system"; `chown` changes the owner — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). A `$` prompt means you are not root — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). *Analogy:* root is an admin key that opens every door, which is why you only pick it up for the one door you need.
2. **`ls -l` anatomy:** `-rw-r--r--  1 alice  users  12693 Jan 11 23:05 notes.txt`: alice owns it, group `users`, the owner can read and write, everyone else can only read — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). Field by field: type (`-` file, `d` directory) | owner rwx | group rwx | others rwx | link count | owner | group | size in bytes | modification time | name.
3. **rwx and octal:** r=4, w=2, x=1, summed per triplet. [ran locally]: `chmod 640` → `-rw-r-----`; `chmod 755` → `-rwxr-xr-x`; `stat -c "%A %a %U:%G %n" deploy.sh` → `-rwxr-xr-x 755 root:root deploy.sh`.
4. **Directories are different:** `r` = list names, `x` = enter or traverse. [ran locally, as user `nobody`]: on a `drw-r--r--` directory, `cd secret` → `Permission denied` and `cat secret/a.txt` → `Permission denied`; after `chmod 711 secret`, `cat secret/a.txt` works but `ls secret` → `Permission denied`. Root could read the file throughout.
5. **`chmod`:** symbolic (`chmod u+x`, `chmod a+rx`) and numeric forms; a script needs `x` to run: `./script.sh` → permission denied, `chmod +x`, then it runs — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). [ran locally]: running a non-executable file → `Permission denied`, exit code `126`.
6. **Default permissions (umask):** [ran locally] `umask` → `0022`; new files are `-rw-r--r--` (644) and new directories `drwxr-xr-x` (755).
7. **Processes and PIDs:** `ps`, `top`/`htop`, background jobs with `&`, `jobs`, Ctrl-Z (sends SIGTSTP; resume with `fg`/`bg`), `nohup` — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). On Ubuntu, `ps`, `top` and `free` come from the `procps` package — [ran locally: `dpkg -S`].
8. **Signals:** Ctrl-C → SIGINT; Ctrl-\ → SIGQUIT; SIGTERM is "a more generic signal for asking a process to exit gracefully"; SIGKILL "cannot be captured by the process and it will always terminate it immediately. However, it can have bad side effects such as leaving orphaned children processes" — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). [ran locally]: `kill PID` sends 15 (SIGTERM); the job's exit status is then `143` (= 128 + 15); `kill -l` lists `9) SIGKILL` and `15) SIGTERM`. *Analogy:* SIGTERM is "please shut down" (shutdown hooks run, like the JVM's `Runtime.addShutdownHook`); SIGKILL is pulling the power cord.
9. **systemd services:** `systemctl status|start|stop|restart|reload|enable|disable|is-active|is-enabled|cat|daemon-reload`, `--now` ("Start or stop unit after enabling or disabling it"), `--failed`, `list-units` — [ran locally: `systemctl --help`, systemd 255]. Learn Linux TV's crash-course episode uses `systemctl` "to start, stop, restart and enable units" — [learnlinux.tv systemctl tag (search)](https://www.learnlinux.tv/tag/systemctl/).
10. **Logs with journalctl:** `-u UNIT` (one service), `-f` (follow), `-n N` (last N), `-p` (priority), `-b` (this boot), `-S/--since`, `-U/--until`, `-e` (jump to end), `--no-pager` — [ran locally: `journalctl --help`]. MS uses `journalctl -u sshd -b-1` in its log-analysis pipeline — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
11. **Disk and memory:** `df -h` (filesystem usage), `du -sh * | sort -h` (what's big), `free -h` (memory; read the `available` column) — [ran locally].
12. **Ports:** `lsof -i -P -n` lists open network sockets with their owning process — [ran locally]. `ss` (package `iproute2`) was not installed in the sandbox, so its flags were not verified here.

**Misconceptions**
- **"Just `sudo` it."** root bypasses most permission checks — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). `sudo` hides the real problem (wrong owner, wrong directory) and creates root-owned files that later break non-root tools. That second part is my inference.
- **`chmod 777` as a fix.** It hands write access to every user; the right fix is usually correct ownership (`chown`) or a narrow `chmod u+x` (inference, based on the rwx model above).
- **"x on a directory means run it."** It means "may enter/traverse" — [ran locally].
- **`kill -9` first.** SIGKILL can't be caught, so no cleanup or graceful shutdown happens and child processes can be orphaned — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- **"Ctrl-Z quit the program."** It only paused it (SIGTSTP); it's still in `jobs` — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- **"`enable` starts the service."** `enable` sets it to start at boot; `start` runs it now; `enable --now` does both — [ran locally: `systemctl --help`].
- **"`systemctl` is broken."** In a container you get `System has not been booted with systemd as init system (PID 1). Can't operate.` / `Failed to connect to bus: Host is down` — [ran locally]. Use a VM for this lesson.

**Example commands with expected output** [ran locally unless noted]
```console
$ id
uid=0(root) gid=0(root) groups=0(root)
$ echo 'echo hi' > deploy.sh; ls -l deploy.sh
-rw-r--r-- 1 root root 8 Oct 30 04:37 deploy.sh
$ ./deploy.sh; echo "exit=$?"
bash: ./deploy.sh: Permission denied
exit=126
$ chmod +x deploy.sh; ls -l deploy.sh
-rwxr-xr-x 1 root root 8 Oct 30 04:37 deploy.sh
$ chmod 640 deploy.sh; ls -l deploy.sh
-rw-r----- 1 root root 8 Oct 30 04:37 deploy.sh
$ ls -l /etc/shadow /usr/bin/passwd           # real-world permissions worth discussing
-rw-r----- 1 root shadow  1379 Oct 22 22:02 /etc/shadow
-rwsr-xr-x 1 root root   64152 May 30  2024 /usr/bin/passwd   # 's' = setuid (advanced aside)
$ sleep 300 &
[1] 25603
$ jobs
[1]+  Running                 sleep 300 &
$ ps -o pid,ppid,stat,etime,cmd -p 25603
  PID  PPID STAT     ELAPSED CMD
25603 25599 S          00:00 sleep 300
$ kill 25603; wait 25603; echo $?
[1]+  Terminated              sleep 300
143
$ df -h /
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   22G   18G  56% /
$ du -sh /usr/* 2>/dev/null | sort -h | tail -3
628M	/usr/bin
1.5G	/usr/local
2.2G	/usr/lib
$ free -h
               total        used        free      shared  buff/cache   available
Mem:            15Gi       1.9Gi        12Gi        15Mi       2.0Gi        13Gi
$ systemctl status ssh          # inside a Docker container
System has not been booted with systemd as init system (PID 1). Can't operate.
Failed to connect to bus: Host is down
```
Commands to run in the VM (flags verified against `--help` output; no live output captured):
```console
$ sudo apt install -y nginx
$ systemctl status nginx
$ sudo systemctl restart nginx
$ sudo systemctl enable --now nginx
$ systemctl --failed
$ journalctl -u nginx -n 50 --no-pager
$ journalctl -u nginx -f            # follow, Ctrl-C to stop
$ journalctl -p err -b              # errors since boot
$ sudo lsof -i -P -n | grep LISTEN  # what listens on which port
```

**Hands-on exercise ideas**
- Permission puzzles: predict `ls -l` after `chmod 640`, `chmod u+x,g-r`, `chmod 700 dir`; then verify. Try to `cd` into a directory without `x` as a normal user (`sudo -u nobody`) — this reproduces the [ran locally] experiment.
- "Fix the deploy script": give a script with mode 644 owned by root. Learners must make it runnable by their user **without** `chmod 777` or `sudo` (`sudo chown $USER deploy.sh && chmod u+x deploy.sh`).
- Signals lab: start `sleep 1000 &`, find it with `ps`/`pgrep`, stop it with SIGTERM, check `$?` = 143. Try Ctrl-Z, then `bg`/`fg`. MS's exercise uses a Python script that ignores SIGINT — [MS 2026 L2 exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
- Service lifecycle (VM): install nginx → `curl -s localhost | head -3` → `systemctl stop nginx` → curl fails → `journalctl -u nginx -n 20` → start it again → find port 80 with `lsof -i :80`.
- Disk-full triage: `df -h` → `sudo du -sh /var/* | sort -h | tail` → `sudo du -sh /var/log/* | sort -h | tail`.

**Curated resources (L4)**
- Missing Semester 2026 L2 (signals, job control, users/permissions) — [GitHub source (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); video [youtube.com/watch?v=ccBGsPedE9Q](https://www.youtube.com/watch?v=ccBGsPedE9Q); 2020 "Command-line Environment" video [youtube.com/watch?v=e8BO_dYxk5c](https://www.youtube.com/watch?v=e8BO_dYxk5c) (IDs from the official repo).
- Learn Linux TV "journalctl Basics: How to Easily Check Your Linux Logs" — [learnlinux.tv (search)](https://www.learnlinux.tv/journalctl-basics-how-to-easily-check-your-linux-logs/embed/); crash-course tags [systemctl](https://www.learnlinux.tv/tag/systemctl/) / [journalctl](https://www.learnlinux.tv/tag/journalctl/) / [linux-crash-course](https://www.learnlinux.tv/tag/linux-crash-course) (search).
- "How To Manage Linux Services with systemctl and journalctl | Sysadmin Basics" — YouTube ID `3kl62YSU9XA` appeared only in a third-party index URL ([letsplayindex (search)](https://www.letsplayindex.com/video/how-to-manage-linux-services-with-systemctl-and-journalctl-3kl62YSU9XA)). A search summary attributes a Linode video on both commands to Jay LaCroix (Learn Linux TV), but I did not confirm the channel. Verify before publishing.
- NetworkChuck "Linux for Hackers" EP4 (sudo/users), EP6 (services), EP7 (processes) — [Class Central listing (search)](https://www.classcentral.com/course/youtube-linux-for-hackers-and-everyone-free-course-for-beginners-65862); no direct YouTube URLs surfaced.
- Unix permissions reference — [Wikipedia: File-system permissions](https://en.wikipedia.org/wiki/File-system_permissions#Traditional_Unix_permissions) (URL from the MS source; not opened); [GNU coreutils chmod](https://www.gnu.org/software/coreutils/chmod) (URL from MS/tldr output).

### Inferences
- Put the systemd/journalctl half of L4 in a Multipass (or other) VM, and the permissions/process half in the same VM for continuity. Containers are fine for L1–L3.
- Teach "SIGTERM, wait, then SIGKILL" because Kubernetes and Docker stop containers the same way (graceful signal, grace period, then kill). This connects the lesson directly to later DevOps topics; check against the Kubernetes/Docker docs when writing the container lessons.
- For a JVM engineer, a demo of `kill <java pid>` running the shutdown hooks versus `kill -9` skipping them makes signals concrete.

### Gaps
- `ss -tulpn` (the modern `netstat`) could not be verified: `ss` is not installed in the sandbox and no search covered it. Verify with `ss --help` in the VM.
- `htop` is not installed by default in the Ubuntu image (sandbox: missing); `apt install htop` is needed. Not verified on a fresh VM.
- No source checked for `ps aux --sort=-%cpu` / `top` keyboard shortcuts.

---

## Lesson 5: Environment, packages, SSH and shell scripts

### Takeaway
Environment variables are "inherited settings" passed from parent to child processes (`export`); `PATH` is the most important one. Dotfiles (`~/.bashrc`, `~/.zshrc`, `~/.ssh/config`) hold configuration that persists across sessions. For SSH, teach an ed25519 key pair, `authorized_keys`, and a `~/.ssh/config` `Host` alias. For scripting, teach a template: shebang → `set -euo pipefail` → quoted variables → argument checks → functions → explicit exit codes. Run ShellCheck on every script.

### Cited Findings

**Concepts in teaching order**
1. **Shell variables:** `foo=bar` (no spaces), `$foo`. Variables are untyped strings. Single quotes are literal (`'$foo'` prints `$foo`); double quotes expand (`"$foo"` prints `bar`) — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
2. **Environment variables:** passed to child processes; `printenv` lists them; `TZ=Asia/Tokyo date` sets one for a single command; `export DEBUG=1` makes it inherited; `unset` removes it; by convention their names are ALL_CAPS — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). [ran locally]: `FOO=bar; bash -c 'echo [$FOO]'` → `[]`; after `export FOO` → `[bar]`. *Analogy:* like a Kotlin object's `val`s copied into the constructor of each child process. A child gets a copy; it can't change the parent's.
3. **`PATH`:** `export PATH="$PATH:path/to/append"` is the pattern installers use — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
4. **Dotfiles / shell config:** "For `bash`, editing your `.bashrc` or `.bash_profile` will work in most systems". Startup-file loading "can be quite complex" (MS links a guide); `~/.ssh/config` is also a dotfile — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); guide: [flowblok "Shell startup scripts" (archived)](https://web.archive.org/web/20260329133158/https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html) (URL from the MS source). Ubuntu's `/etc/skel/.profile` says: "~/.profile: executed by the command interpreter for login shells. This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login exists" — [ran locally].
5. **Package managers:** "macOS uses Homebrew, Ubuntu/Debian use `apt`, Fedora uses `dnf`, and Arch uses `pacman`" — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). Example: `sudo apt install shellcheck`, `brew install shellcheck` — [ShellCheck README (opened)](https://github.com/koalaman/shellcheck). For "which package provides command X", MS points to [command-not-found.com](https://command-not-found.com).
6. **SSH keys:** key-based auth "is both more convenient and more secure"; the private key "is effectively your password... never share its contents"; generate with `ssh-keygen -a 100 -t ed25519 -f ~/.ssh/id_ed25519`; the server checks `~/.ssh/authorized_keys`; copy the key with `ssh-copy-id -i .ssh/id_ed25519 alice@remote` — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). GitHub's docs use `ssh-keygen -t ed25519 -C "your_email@example.com"` — [GitHub Docs source (opened)](https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent.md).
7. **`~/.ssh/config`:** `Host vm` / `User alice` / `HostName 172.16.174.141` / `Port 2222` / `IdentityFile ~/.ssh/id_ed25519`; wildcards such as `Host *.mit.edu`; the file is also read by `scp` and `rsync` — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md). **Mac-specific:** GitHub's docs add `AddKeysToAgent yes` and `UseKeychain yes` (macOS keychain) and `ssh-add --apple-use-keychain ~/.ssh/id_ed25519`. If you see `Bad configuration option: usekeychain`, add `IgnoreUnknown UseKeychain` — [GitHub Docs source (opened)](https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent.md).
8. **Remote commands and file copy:** `ssh host 'cmd'`; `scp local remote:path`; `rsync` "improves upon `scp` by detecting identical files... and preventing copying them again", and supports `--partial` for resuming — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
9. **Scripts:** shebang `#!/usr/bin/env bash` + `chmod +x`; `$1..$9`, `$@` (all arguments), `$#` (count), `$0` (script name); `exit NUM`; `$?` — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).
10. **Conditionals and tests:** `if cmd; then ...; fi` branches on exit codes; `test`/`[ ]` for `-f file` and `"$var" = "string"`; `[[ ]]` is the "safer" bash built-in "with fewer odd behaviours around quoting"; `while` and `for x in a b c` loops; `$(seq 1 10)` — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md). Reference: [GNU bash manual, Conditional Expressions](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html) (URL from the MS source).
11. **Quoting rule: always quote expansions** (`"$var"`, `"$(cmd)"`). Without quotes, word splitting and pathname expansion happen — [BashPitfalls summary via search (search)](https://wiert.me/2015/12/03/bashpitfalls-common-errors-that-bash-programmers-make-gregs-wiki); [ran locally]: with `file="my file.txt"`, `ls $file` → two errors (`my`, `file.txt`), while `ls "$file"` works. Reference: [GNU bash manual, Quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html) (URL from the MS source).
12. **Strict mode `set -euo pipefail`:** `-e` exits on an error, but there are "important exceptions for conditionals and logical operators"; under `-e`, a grep with no match (exit code 1) can kill the script; `pipefail` makes a pipeline fail when any stage fails — [kindatechnical guide (search)](https://kindatechnical.com/shell-scripting-bash/strict-mode-set-euo-pipefail.html). [ran locally]: `cat nope.txt | sort` exits 0 without pipefail and 1 with it; `set -u` + an unset `$DEPLOY_DIR` → `DEPLOY_DIR: unbound variable`. A dissenting view: jmmv.dev (2018) says the needed contortions made the author stop using it; they recommend `set -eu` for POSIX sh and `set -euo pipefail` only for bash-specific scripts — [jmmv.dev (search)](https://jmmv.dev/2018/03/shell-readability-strict-mode.html).
13. **Debugging:** `set -x` traces every command (an MS exercise asks what `-x` does) — [MS 2026 L1 exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).
14. **ShellCheck:** "a GPLv3 tool that gives warnings and suggestions for bash/sh shell scripts". Its first goal is "To point out and clarify typical beginner's syntax issues that cause a shell to give cryptic error messages". You can use it on shellcheck.net, in the terminal, in VS Code (vscode-shellcheck), and in CI/pre-commit — [ShellCheck README (opened)](https://github.com/koalaman/shellcheck).

**Misconceptions (ShellCheck's own "gallery of bad code" is the best checklist)** — all from [ShellCheck README (opened)](https://github.com/koalaman/shellcheck):
- `var = 42` (spaces around `=`), `$foo=42` (`$` when assigning), `for $var in *` (`$` on a loop variable), `echo "Argument 10 is $10"` (needs `${10}`), `if $(myfunction); then` (wrapping a command in `$()`), `else if` (use `elif`), using a function before it is defined.
- Quoting: `echo $1` (unquoted), `find . -name *.ogg` (unquoted pattern), `rm "~/my file.txt"` (tilde does not expand inside quotes), `for f in "*.ogg"` (quoted glob = one literal word), `touch $@` (unquoted `$@`), `echo 'Don't forget'` (apostrophe ends the single-quoted string).
- **The `rm -rf "$DIR/"*` disaster** [ran locally, with `echo` in front so nothing was deleted]: with `DIR=""`, `echo rm -rf "$DIR/"*` expands to `rm -rf /bin /boot /dev /etc /home ...`. The guard `"${DIR:?DIR is not set}"` aborts with `DIR: DIR is not set`.
- "Script exit code = last line's" surprises: add explicit `exit 0` / `exit 1`, and note that `grep` returns 1 for "no match", which is not an error — [ran locally]; [kindatechnical (search)](https://kindatechnical.com/shell-scripting-bash/strict-mode-set-euo-pipefail.html).

**Example: a complete beginner script** [ran locally]
```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 LOGFILE [PATTERN]" >&2
  exit 2
}

[[ $# -ge 1 ]] || usage
logfile="$1"
pattern="${2:-ERROR}"          # default value if $2 is missing

if [[ ! -f "$logfile" ]]; then
  echo "error: '$logfile' not found" >&2
  exit 1
fi

count=$(grep -c -i -- "$pattern" "$logfile" || true)   # grep exits 1 on "no match"
echo "$count lines match '$pattern' in $logfile"

for level in INFO WARN ERROR; do
  n=$(grep -c -w "$level" "$logfile" || true)
  printf '%-5s %s\n' "$level" "$n"
done
```
```console
$ ./count_errors.sh; echo "exit=$?"
usage: ./count_errors.sh LOGFILE [PATTERN]
exit=2
$ ./count_errors.sh app.log
3 lines match 'ERROR' in app.log
INFO  5
WARN  1
ERROR 2
$ ./count_errors.sh nope.log; echo "exit=$?"
error: 'nope.log' not found
exit=1
$ ./count_errors.sh app.log timeout
1 lines match 'timeout' in app.log
...
```
Other [ran locally] snippets:
```console
$ echo 'single $HOME'; echo "double $HOME"
single $HOME
double /root
$ bash -c 'cat nope.txt | sort; echo "exit=$?"' 2>/dev/null
exit=0
$ bash -c 'set -o pipefail; cat nope.txt | sort; echo "exit=$?"' 2>/dev/null
exit=1
$ bash -c 'set -u; echo "dir=$DEPLOY_DIR"'
bash: line 1: DEPLOY_DIR: unbound variable
```

**Hands-on exercise ideas**
- `PATH` lab: write `~/bin/hello` (a script), try `hello` (not found), add `export PATH="$HOME/bin:$PATH"` to `~/.bashrc`, open a new shell, then run `which hello`.
- `export` lab: show that a variable set without `export` is invisible to `bash -c`.
- SSH lab (Mac ↔ VM): generate an ed25519 key on the Mac, add the public key to the VM's `~/.ssh/authorized_keys`, create a `Host devbox` entry in `~/.ssh/config`, then `ssh devbox 'uptime'`, `scp app.log devbox:/tmp/`, and `rsync -av logs/ devbox:/tmp/logs/` (run it twice to see that rsync skips unchanged files).
- Script kata: extend `count_errors.sh` to accept several files (`for f in "$@"`), to return exit code 3 if any ERROR is found (so CI could fail on it), and to pass ShellCheck cleanly.
- "Break it then lint it": hand out a script full of ShellCheck's gallery mistakes; learners fix them using shellcheck.net output.
- MS exercises: a `[ -f "$1" ]` check script; backing up a file with today's date in its name; dissecting what `set -x` shows — [MS 2026 L1 exercises (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md).

**Curated resources (L5)**
- Missing Semester 2026 L2 (environment variables, dotfiles, SSH) — [GitHub source (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); 2020 "Shell Tools and Scripting" video [youtube.com/watch?v=kgII-YWo3Zw](https://www.youtube.com/watch?v=kgII-YWo3Zw) (ID from the official repo).
- ShellCheck — [shellcheck.net](https://www.shellcheck.net) and [github.com/koalaman/shellcheck](https://github.com/koalaman/shellcheck) (opened; read the "Gallery of bad code").
- GitHub Docs "Generating a new SSH key and adding it to the ssh-agent" — [source on GitHub (opened)](https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent.md).
- man pages for [ssh-keygen](https://www.man7.org/linux/man-pages/man1/ssh-keygen.1.html), [scp](https://www.man7.org/linux/man-pages/man1/scp.1.html) and [rsync](https://www.man7.org/linux/man-pages/man1/rsync.1.html) (URLs from the MS source).
- GNU bash manual sections [Quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html), [Exit Status](https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html), [Conditional Expressions](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html) (URLs from the MS source).
- SWC episodes 5–6 (loops, scripts; "Spaces in Names") — [GitHub source (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/06-script.md).
- Strict-mode debate: [jmmv.dev](https://jmmv.dev/2018/03/shell-readability-strict-mode.html) (search).
- NetworkChuck "Linux for Hackers" EP5 (apt, dpkg, pip) — [Class Central listing (search)](https://www.classcentral.com/course/youtube-linux-for-hackers-and-everyone-free-course-for-beginners-65862).

### Inferences
- Present `set -euo pipefail` as the default for DevOps glue scripts, together with the two escape hatches learners will need on day one: `cmd || true` for "a failure here is OK" (grep with no match), and `${VAR:?message}` for required variables. Mention the jmmv critique so learners understand it is a trade-off, not magic.
- A good rule of thumb for this audience: if a script needs data structures, more than about 100 lines, or real error handling, write it in Kotlin, Python or Go instead. Google's testing blog has a 2023 post titled "Shell scripts: stay small & simple" ([search](https://testing.googleblog.com/2023/10/shell-scripts-stay-small-simple.html)); I didn't read its content.
- On the Mac, the learner's interactive shell is zsh, so config goes in `~/.zshrc`. Inside the Linux VM/container it is bash, so config goes in `~/.bashrc`. Always write scripts with `#!/usr/bin/env bash` so they run under bash everywhere.

### Gaps
- No sourced explanation of zsh startup files (`~/.zshrc` vs `~/.zprofile`) was gathered. The flowblok guide linked by MS covers both bash and zsh but I did not open it.
- apt vs apt-get, `dnf` specifics and `brew` vs `apt` naming differences were not researched beyond MS's one-line summary.
- I did not open Greg's Wiki BashPitfalls directly; it was cited only through a third-party summary.

---

## Key question 3: What are the classic beginner misconceptions and mistakes?

### Takeaway
Almost every classic mistake comes from not seeing what the shell does to a line before the program runs (quoting, globbing, splitting, expansion), or from not knowing that redirection and `rm` act immediately and can't be undone. Teach the "predict, then `echo` it, then run it" habit and the mistakes become visible.

### Cited Findings
| Mistake | What actually happens | Source |
|---|---|---|
| `rm` expecting a trash bin | Files are unlinked; recovery isn't guaranteed | [SWC 03-create (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/03-create.md) |
| `sort f > f` | File is truncated before sort reads it → empty | [SWC 04-pipefilter (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md); [ran locally] |
| `>` when `>>` was meant | Silent overwrite | [SWC 04-pipefilter (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md); [ran locally] |
| `find . -name *.txt` (unquoted) | Shell expands the glob first | [SWC 07-find (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md); [ShellCheck (opened)](https://github.com/koalaman/shellcheck) |
| Glob vs regex confusion (`*`, `.`) | `.log` as a regex matches `xlog` | [ran locally] |
| `grep "a|b"` without `-E` | `|` is literal in BRE → no match | [ran locally] |
| `uniq` without `sort` | Only adjacent duplicates are merged | [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); [ran locally] |
| `2>&1 > file` order | stderr still goes to the terminal | [ran locally] |
| Expecting errors to flow through a pipe | Only stdout is piped | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md) |
| `name = value` | Runs program `name` with arguments `=` and `value` | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); [ShellCheck (opened)](https://github.com/koalaman/shellcheck); [ran locally] |
| Unquoted `$var` holding spaces | Word splitting → wrong arguments | [ShellCheck (opened)](https://github.com/koalaman/shellcheck); [SWC 05-loop (opened)](https://github.com/swcarpentry/shell-novice/blob/main/episodes/05-loop.md); [ran locally] |
| `'$HOME'` vs `"$HOME"` | Single quotes don't expand | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); [ran locally] |
| `"~/file"` | Tilde not expanded inside quotes | [ShellCheck (opened)](https://github.com/koalaman/shellcheck) |
| `rm -rf "$DIR/"*` with empty `DIR` | Expands to everything under `/` | [ran locally, with echo]; guard with `${DIR:?}` |
| `sudo` for everything | root bypasses most checks and masks the real problem | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md) |
| `kill -9` as the first resort | No graceful cleanup; can orphan children | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md) |
| Ctrl-Z to quit | Pauses the job (SIGTSTP) | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md) |
| `set -e` + grep no-match | Script exits on grep's exit code 1 | [kindatechnical (search)](https://kindatechnical.com/shell-scripting-bash/strict-mode-set-euo-pipefail.html) |
| Pipeline exit code | Last stage only, unless `pipefail` | [ran locally] |
| GNU flags on a Mac (`sed -i`, `grep -P`, `date -d`) | Errors or different behaviour | see KQ4 |
| `xargs` with spaces in file names | Names split apart | [ran locally]; use `-print0 \| xargs -0` |

### Inferences
- Make each misconception a 2-minute "predict the output" card. Learners predict, run, and then explain the difference. This matches SWC's style of multiple-choice challenges (e.g. the "which files will be listed?" questions in episode 5).
- `chmod 777` and "curl | sudo bash" are other classic DevOps anti-patterns worth a slide, but they come from general practice rather than a source gathered here.

### Gaps
- No quantitative data on which mistakes are most frequent among beginners was found.

---

## Key question 4: Which macOS (zsh, BSD) vs Linux (bash, GNU) differences trip people up, and how do you practise real Linux on an Apple Silicon Mac for free?

### Takeaway
On the Mac the learner has zsh as the interactive shell, an old bash 3.2, and BSD versions of `sed`, `grep`, `date`, `ls`, `stat` and so on. Servers, CI runners and containers have bash 5 and GNU tools. Small flags differ (`sed -i ''`, `grep -P`, `date -d`, `stat -c`, `ls --color`). The cleanest fix for a course is to **do all exercises inside Linux**: an `ubuntu:24.04` Docker container for Lessons 1–3 and most of 5, and a lightweight Ubuntu VM (Multipass, or Lima, UTM or OrbStack) for Lesson 4 (systemd, journalctl) and the SSH part of Lesson 5.

### Cited Findings
**Shell differences**
- zsh has been the default macOS login and interactive shell since Catalina (2019); bash remains installed; you can return to it with `chsh -s /bin/bash` — [The Next Web (search)](https://thenextweb.com/news/why-does-macos-catalina-use-zsh-instead-of-bash-licensing); [Apple Support Community (search)](https://discussions.apple.com/thread/250989957); [Slashdot (search)](https://apple.slashdot.org/story/19/06/04/1645240).
- The bundled bash is 3.2 (3.2.57, from 2007); newer bash is GPLv3, which is the widely repeated explanation for why Apple didn't update it. Apple never officially confirmed this — [Apple Support Community (search)](https://discussions.apple.com/thread/250989957); [The Next Web (search)](https://thenextweb.com/news/why-does-macos-catalina-use-zsh-instead-of-bash-licensing).
- **Conflict to note:** Missing Semester 2026 says that on Linux and macOS the terminal "will usually open... bash". That is out of date for macOS — [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md) vs the sources above.
- zsh supports `**` recursive globs that bash (by default) doesn't — [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md).

**Tool differences** (primary source: the "macOS and Unix" open book, read from its GitHub source, last commit 2026-02-03 — [bsd-vs-gnu (search; opened)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html))
- **`sed -i`:** GNU `sed -i 's/a/b/' f`; BSD needs a backup suffix argument: `sed -i '' 's/a/b/' f`. If you omit it, BSD treats the script as the suffix ("hence the confusing error messages"). `-i ''` does *not* work on GNU. The portable form is `sed -i.bak 's/a/b/' f && rm f.bak` — [bsd-vs-gnu (opened)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html); [geeky-boy blog (search)](https://blog.geeky-boy.com/2020/11/using-sed-in-place-gnu-vs-bsd.html).
- **`grep -P`:** GNU only; BSD grep → `grep: invalid option -- P`; use `-E` with `[0-9]` instead of `\d` — [bsd-vs-gnu (opened)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html).
- **`date`:** GNU `date -d "2024-01-15" +%s`, `date -d "7 days ago"`; BSD `date -j -f "%Y-%m-%d" "2024-01-15" +%s`, `date -v-7d`; BSD has no natural-language dates — [bsd-vs-gnu (opened)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html).
- **`ls`:** GNU `ls --color=auto`, BSD `ls -G`; `--group-directories-first` and `--time-style` are GNU-only; `-lh` and `-lt` work on both — same source.
- **`stat`:** "almost entirely incompatible": GNU `stat -c %s` / `-c %Y`, BSD `stat -f %z` / `-f %m` — same source.
- **GNU tools on the Mac:** `brew install coreutils gnu-sed grep gawk findutils`; Homebrew installs them with a `g` prefix (`gsed`, `ggrep`, `gdate`); unprefixed versions live in `/opt/homebrew/opt/<pkg>/libexec/gnubin` on Apple Silicon. Putting that on `PATH` changes behaviour for every script — [macOS-and-Unix gnu-coreutils (search)](https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/gnu-coreutils.html). The old `brew install gnu-sed --with-default-names` option is no longer supported by current Homebrew, according to a search summary of several sed articles (e.g. [chrisshort.net (search)](https://chrisshort.net/gnu-sed-on-mac-os-x/)). I did not pin down which page says this.
- Source-quality note: the same book also claims "BSD xargs doesn't have -P" and shows `cp --progress` as a GNU option. Both contradict my understanding (macOS xargs has `-P`; GNU cp has no `--progress`), so cite that book only for the `sed`, `grep`, `date`, `ls` and `stat` items above.
- Ubuntu's default `awk` is mawk (1.3.4), not GNU awk — [ran locally].

**Practising real Linux on Apple Silicon (free, local)**
- **Docker container:** an Ubuntu image is the quickest sandbox. Important quirk: Ubuntu container images are *minimized*. `/etc/dpkg/dpkg.cfg.d/excludes` contains `path-exclude=/usr/share/man/*` ("Drop all man pages"), `man ls` prints "This system has been minimized by removing packages and content that are not required on a system that users do not log into", and an `unminimize` command is provided to restore them — [ran locally, in this Ubuntu 24.04 sandbox, which is built on the minimized Ubuntu base. I did not run the official `ubuntu:24.04` Docker image itself; confirm with `docker run --rm ubuntu:24.04 cat /etc/dpkg/dpkg.cfg.d/excludes`]. **systemd does not run as PID 1** in a container, so `systemctl` fails ("System has not been booted with systemd as init system (PID 1). Can't operate.") — [ran locally].
- **Multipass (Canonical):** "a lightweight VM manager for Linux, Windows and macOS... spin up a fresh Linux environment with a single command"; uses "QEMU or the Apple Virtualization Framework on macOS"; supports cloud-init. Install from the GitHub releases or `brew install --cask multipass` (community-maintained). Commands: `multipass launch lts`, `multipass list`, `multipass shell <name>` — [Multipass README (opened)](https://github.com/canonical/multipass); install docs [canonical.com/multipass/docs (URL from README)](https://canonical.com/multipass/docs/stable/how-to-guides/install-multipass/).
- **Lima:** "launches Linux virtual machines with automatic file sharing and port forwarding (similar to WSL2)": `brew install lima`, `limactl start`, `lima uname -a`; it can also host Docker or containerd — [Lima README (opened)](https://github.com/lima-vm/lima); [lima-vm.io](https://lima-vm.io/).
- **OrbStack:** a lightweight VM with a shared kernel, a Docker engine plus "Linux machines" (15+ distros) — [OrbStack docs, architecture (search)](https://docs.orbstack.dev/architecture); [index.html.zone summary (search)](https://index.html.zone/dev/orbstack).
- **UTM:** open source, built on Apple's Hypervisor framework, runs ARM64 Linux "at near-native speed"; some distros don't work on Apple Silicon because of page-size differences — [bell-sw.com (search)](https://bell-sw.com/blog/how-to-install-linux-on-a-mac-with-apple-silicon/); [lotas.github.io (search)](https://lotas.github.io/2021/11/01/docker-mac-m1.html).

**Recommended setup** (commands are standard; the image behaviour was verified as noted above)
```console
# Lessons 1–3 (+ L5 scripting): disposable Ubuntu container
$ docker run -it --rm --name lab -v "$PWD":/lab -w /lab ubuntu:24.04 bash
root@...:/lab# apt update && apt install -y less man-db procps jq   # base image is minimal
root@...:/lab# unminimize            # optional: restore man pages
# second terminal into the same container (for tail -f labs):
$ docker exec -it lab bash

# Lessons 4–5: a real VM with systemd and sshd
$ brew install --cask multipass
$ multipass launch lts --name devbox
$ multipass shell devbox
ubuntu@devbox:~$ systemctl status ssh
```

### Inferences
- Make "run it in Linux, not in macOS Terminal" a course-wide rule, and say why: what learners practise should match servers and CI. Teach the BSD/GNU differences as one short "when you go back to your Mac" sidebar instead of letting them surprise people mid-lesson.
- In the container learners are root (`#` prompt), which hides permission lessons. For L4 either use the Multipass VM (default user `ubuntu`, with sudo) or create a user in the container (`useradd -m dev && su - dev`).
- Docker Desktop, OrbStack, Colima/Lima and Multipass all run native arm64 Ubuntu on Apple Silicon. Pick one container runtime and one VM tool and use them for the whole course, to keep setup friction low.

### Gaps
- **Licensing/cost was not verified** for Docker Desktop (free tier conditions) or OrbStack (personal vs commercial use). The lesson writer must check both before calling them "free". Multipass, Lima and UTM are open source (Multipass and Lima READMEs opened; UTM per search).
- I didn't verify whether OrbStack's Linux machines run systemd, or whether `apt install iproute2` is needed for `ss` in the Multipass image.
- Exact behaviour of the macOS (FreeBSD-derived) grep on recent macOS versions wasn't tested on real hardware.

---

## Key question 5: Which realistic DevOps tasks make good worked examples and exercises?

### Takeaway
Use one realistic dataset (an app log, an nginx access log, a JSON API response) throughout the course, and frame each exercise as an on-call question: "what broke?", "who is hammering us?", "what's eating the disk?", "is the service up and what's it saying?", "what's listening on 8080?". Each maps to a short pipeline the learner can build one stage at a time.

### Cited Findings
| Task (on-call question) | Lesson | Commands | Evidence |
|---|---|---|---|
| Find errors in a log | 2 | `grep -i error app.log`, `grep -c`, `grep -n`, `grep -A1` | [ran locally] (outputs in KQ2) |
| Watch errors live | 2/4 | `tail -f app.log \| grep --line-buffered ERROR`; `journalctl -u nginx -f` | [ran locally]; flags from `journalctl --help` [ran locally] |
| Top client IPs | 3 | `awk '{print $1}' access.log \| sort \| uniq -c \| sort -rn \| head` | [ran locally] |
| Status-code histogram / 5xx | 3 | `awk '{print $9}' … \| sort \| uniq -c \| sort -rn`; `awk '$9>=500'`; `grep -E '" 5[0-9]{2} '` | [ran locally] |
| Bytes served | 3 | `awk '{sum+=$10} END {print sum}'` | [ran locally] |
| Top usernames in failed SSH logins | 3 | MS's `journalctl \| grep "Disconnected from" \| sed -E … \| sort \| uniq -c \| sort -nk1,1 \| tail` pipeline | [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md) |
| Which pods are unhealthy (JSON) | 3 | `jq -r '.items[] \| select(.status != "Running") \| .name'` | [ran locally] |
| Find large files | 2/4 | `find ~ -type f -size +100M -exec ls -lh {} \;`; `du -sh * \| sort -h \| tail` | [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md); [ran locally] |
| Find old logs to clean | 2 | `find /var/log -name "*.log" -mtime +30` (list first, then `-delete`) | [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md) (`-mtime +30` pattern); [ran locally] |
| Files containing a TODO/secret | 2 | `grep -r -l`, `find . -name "*.py" -exec grep -l "TODO" {} \;` | [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md) |
| Disk full | 4 | `df -h` → `du -sh /var/* \| sort -h` | [ran locally] |
| Memory pressure | 4 | `free -h` (the "available" column) | [ran locally] |
| Is the service up / why did it fail | 4 | `systemctl status X`, `systemctl --failed`, `journalctl -u X -n 50`, `journalctl -p err -b` | flags verified via `--help` [ran locally] |
| What listens on a port | 4 | `sudo lsof -i -P -n \| grep LISTEN`, `lsof -i :8080`; `ss -tlnp` (not verified) | `lsof` [ran locally] |
| Stuck process | 4 | `ps`, `kill PID` (SIGTERM), `kill -9` only if needed | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md); [ran locally] |
| Script won't run | 4 | `ls -l`, `chmod +x`, exit code 126 | [ran locally] |
| Connect and copy to a server | 5 | `ssh devbox`, `~/.ssh/config`, `scp`, `rsync -av` | [MS 2026 L2 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/command-line-environment.md) |
| CI-style log check script | 5 | `count_errors.sh` with `set -euo pipefail`, exit codes, ShellCheck | [ran locally]; [ShellCheck (opened)](https://github.com/koalaman/shellcheck) |
| Flaky test reproducer | 5 | MS's "run until it fails" loop script | [MS 2026 L1 (opened)](https://github.com/missing-semester/missing-semester/blob/master/_2026/course-shell.md) |

### Inferences
- **Capstone idea (end of L5, in the Multipass VM):** `apt install nginx` → generate traffic with `for i in $(seq 1 50); do curl -s -o /dev/null localhost/; done` plus a few 404s → report the top IPs and status codes from `/var/log/nginx/access.log` → `systemctl stop nginx`, observe the failure, read `journalctl -u nginx`, restart → wrap the report in a ShellCheck-clean script that exits non-zero if it finds any 5xx. This touches every lesson, and it leads into later course topics (containers, CI, monitoring).
- Use the documentation IP ranges (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24) in all sample logs so that no real addresses appear in the course material.
- Use a generated nginx log as the main dataset rather than a public one: it is offline, free, and has a known answer key.

### Gaps
- I found no public, permissively licensed "beginner DevOps log dataset" to recommend; generating synthetic logs (as above) is the fallback.
- The `ss` and `nginx` commands in the capstone were not executed in this sandbox (no systemd, no `ss`). Verify them once in a Multipass VM before publishing.

---

**Additional resources not tied to one lesson**
- Linux Foundation "Introduction to Linux" (LFS101x on edX): free to audit, with a paid verified certificate (price varies by listing: $199 per Linuxiac). It has passed one million enrollments — [Linuxiac (search)](https://linuxiac.com/over-1-million-enrollments-for-introduction-to-linux-training-course-on-edx/); [TechRadar review (search)](https://www.techradar.com/reviews/linux-foundation-introduction-to-linux-course). Broad and long; best as optional background reading.
- freeCodeCamp "Introduction to Linux – Full Course for Beginners" (~6 h). The YouTube ID `sWbUDq4S6Y8` appeared only in a third-party index URL ([letsplayindex (search)](https://www.letsplayindex.com/video/introduction-to-linux-full-course-for-beginners-freecodecamporg-sWbUDq4S6Y8)), so verify `https://www.youtube.com/watch?v=sWbUDq4S6Y8` before publishing. freeCodeCamp also has a ~1 h "Command Line Basics for Beginners" — [freecodecamp.org/news (search)](https://www.freecodecamp.org/news/command-line-basics-for-beginners).
- Missing Semester YouTube channel (all lectures) — [youtube.com/@MissingSemester](https://www.youtube.com/@MissingSemester) (URL from the official course source). 2020 lecture 1 video: [youtube.com/watch?v=Z56Jmr9Z34Q](https://www.youtube.com/watch?v=Z56Jmr9Z34Q).
