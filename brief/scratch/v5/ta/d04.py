"""Book-voice rewrite of d04 (Reading and searching text). Writer: ta. Run from the repo root."""
import json

PATH = "content/p1.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d04")

L["opening"] = """Picture the phone ringing at the office front desk. A customer's order failed this morning, and they read you a reference: `7f3a9c`. Somewhere in the building, four departments each keep a logbook, a few thousand lines long, and the answer is in there. The customer is waiting on the line.

Nobody reads four logbooks from the top. You need to ask the building questions: which lines mention this reference, which of them are errors, and what happened just before the first one. The trap is that a badly worded question gets no answer at all, and silence looks exactly like good news. A result of "no errors" may only mean you asked in the wrong language.

Last time, we learned how the clerk reads a note and how every drawer in the building has an address. In this lesson, we'll open the drawers: read big files safely, search them with grep, describe text by its shape, and find files by name, size and age. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "You want every line of `app.log` that contains ERROR or WARN, so you type `grep \"ERROR|WARN\" app.log`. What does it print?"
L["guess"]["why"] = "Without `-E`, grep reads `|` as an ordinary character, and no line contains the text `ERROR|WARN`. So it prints nothing at all. `grep -E \"ERROR|WARN\"` does what you meant."

L["terms"] = [
    {"term": "Pager", "plain": "A program like less that shows a long file one screen at a time."},
    {"term": "grep", "plain": "A tool that prints the lines of its input that match a pattern."},
    {"term": "Regular expression (regex)", "plain": "A small pattern language for text, where symbols like . * ^ $ have special meanings."},
    {"term": "Anchor", "plain": "A regex symbol that matches a position: ^ is the start of a line and $ is the end."},
    {"term": "Exit code", "plain": "The number a program hands back when it ends: 0 means success, anything else means a problem."},
    {"term": "Recursive", "plain": "Going into every folder inside a folder, and every folder inside those."},
    {"term": "find", "plain": "A tool that walks through a tree of folders and lists files by name, type, size or age."},
]

S = L["sections"]

S[0]["h"] = "Looking at a file before you search it: cat, less, head and tail"
S[0]["body"] = """Every department in our building keeps a logbook at its door, and each visitor gets one line: the time, who came, and what happened. A log file is the same idea. It is a plain text file that a program adds to, one line per event. Most lines in the lab's `app.log` hold a time, a level such as INFO or ERROR, the service name, a request ID and a message. A service is one program that does one job, and a request ID is a reference number for one customer's request. Because logs come in lines, most of today's tools work line by line.

Before you read a logbook, check how thick it is. `wc -l app.log` (word count, counting lines only) prints `37 app.log`, so the file has 37 lines. The size decides which command makes sense:

- `cat app.log` prints the whole file. Fine for 37 lines, useless for a 2 GB log that scrolls past for minutes.
- `less app.log` opens a pager, a viewer that shows one screen at a time. Space goes down a page, `b` goes back, `g` jumps to the top and `G` to the end. Type `/` and a word to search, `n` for the next match, and `q` to quit.
- `head -n 3 app.log` prints the first three lines. Without `-n` you get ten.
- `tail -n 2 app.log` prints the last two lines. Logs grow at the bottom, so tail shows the newest events.

Logs also change while you read them. `tail -f app.log` (follow) keeps the file open and prints each new line as it arrives. Press Ctrl+C to stop.

Servers also rotate logs, so that one file cannot grow until the disk is full. They rename `app.log` to `app.log.1` and start a new, empty `app.log`. It is like the department starting a fresh logbook and putting the old one on a shelf. Plain `-f` keeps watching the old book and goes quiet. `tail -F` (capital F) follows the name and switches to the new file, so use it on servers.

Reading is fine for a page. For the customer's reference, you need to search. Next, we'll meet the tool that does it."""

S[1]["h"] = "Searching with grep, one question at a time"
S[1]["body"] = """Picture running a highlighter down every page of a logbook, then cutting out only the marked lines. grep does that. It answers one question: which lines contain this text? It reads its input one line at a time, checks whether the pattern appears anywhere in the line, prints the lines where it does and skips the rest.

The shape is `grep PATTERN FILE`. The first argument is what to look for, and every argument after it is a file to read. For now the pattern is a plain word, and grep matches it exactly as typed. So `grep ERROR app.log` prints the 4 lines that contain ERROR in capitals, wherever it sits in the line.

Each option changes one part of that behaviour, and each answers a question you will ask when something is broken:

- Did I miss any? Logs are messy about case, so `grep -i error app.log` ignores it. It finds 5 lines: the extra one is a WARN line that says "retrying after error".
- How many? `grep -c ERROR app.log` prints `4`. It counts lines, not words.
- Where in the file? `grep -n WARN app.log` puts the line number in front, like `6:2026-10-30T09:02:40Z WARN ...`.
- What is left without the noise? `grep -v INFO app.log` inverts the match. It shows every line without INFO, including two lines of a Java error report that have no level at all.
- Only whole words? `grep -c 200 app.log` prints `16`, because `1200ms` and `code 2001` contain 200 too. With `-w`, only 200 standing alone counts, and the answer is `14`.

Every short option also has a long name that spells out its job, and `grep --help` lists them all. For example, `-i` is `--ignore-case` and `-v` is `--invert-match`. Options combine, and their order does not matter. `grep -n -i -w error app.log` and `grep -niw error app.log` are the same command.

grep also sets an exit code, the number every program hands back when it ends. Zero means success, and anything else means a problem. There is one way to succeed and many ways to fail, so the other numbers can say which failure it was.

For grep, 0 means "found a match", 1 means "no match" and 2 means "something went wrong", such as a missing file. The shell keeps the last exit code in `$?`. So `grep -q ERROR app.log` prints nothing (`-q` is quiet), and `echo $?` then prints `0`. Day 5 and Day 7 build on this.

One matching line rarely tells the whole story, though. Next, we'll ask for the lines around it, and search many logbooks at once."""

S[2]["h"] = "Context, many files and whole folders"
S[2]["body"] = """When a visitor's line says "left angry", you want to read the lines just before it. One matching line rarely explains a failure on its own, so grep can show its neighbours:

- `-A 2` (A for after) adds 2 lines after each match. `grep -A 2 NullPointer app.log` shows the error and both lines of the error report below it.
- `-B 1` (B for before) adds 1 line before. It often shows what the app was doing just before it failed.
- `-C 1` (C for context) adds 1 line on each side. With `-n`, grep marks matches with a colon and context lines with a dash, so `15:` is a hit and `14-` is a neighbour.

grep also searches many files at once. Give it several names, or a glob like `logs/*.log`, and it puts the file name in front of each hit. With `-r` (recursive) it searches a folder and every folder inside it, like walking every room on a floor.

Across many files you often want a summary instead of every line:

- `-l` lists only the names of files that match. `grep -r -l ERROR logs` prints five file names, one of them in `logs/archive`.
- `-c` prints a count per file, such as `logs/payments.log:4`.

The `-o` option prints only the part of the line that matched. With a plain word, that is not much use. With the patterns in the next section, it turns grep into a tool that pulls values out of text.

So far every pattern has been a plain word. Next, we'll describe text by its shape instead."""

S[3]["h"] = "Regular expressions: describing text by its shape"
S[3]["body"] = """Say you want every duration in `app.log`: `2ms`, `34ms`, `1200ms`. No single word matches them all. But they share a shape: some digits, then ms. A regular expression, or regex, is a pattern that describes a shape like that. When grep reads a line, it tries the pattern at every position, and the line matches if it fits anywhere.

A plain word is already a regex in which each letter matches itself. A few symbols have special meanings, and these work in plain grep:

- `.` matches any one character. So `grep orders.db app.log` also matches `orders-db`, which may surprise you.
- `[...]` matches one character from a set. `[0-9]` is any digit, `[a-f]` any letter from a to f, and `[^ ]` anything except a space.
- `*` means "zero or more of the thing before it". `grep -o 'req=[0-9a-f]*'` happily matches `req=` with nothing after it.
- `^` anchors to the start of a line and `$` to the end. So `grep -v '^2026' app.log` prints the two lines of the error report, the only lines that do not start with a date.
- A backslash makes a symbol literal again: `orders\\.db` matches only a real dot.

Plain grep uses the original, basic dialect of regex, where `+`, `?`, `|` and braces are ordinary characters. Add `-E` for extended regular expressions, where they are special. Most people find that easier to read:

- `+` means one or more. `grep -o -E '[0-9]+ms' app.log` pulls out durations like `34ms` and `1200ms`.
- `?` means optional. `https?://` matches both http and https.
- `{4}` means exactly four times. `[0-9]{4}ms` finds requests that took 1,000 ms or more.
- `|` means or, and parentheses group: `grep -E '(GET|POST) /api/checkout' app.log`.

Now we can explain the guess from the start of this lesson. Without `-E`, `grep 'WARN|ERROR'` treats `|` as a normal character and finds nothing. With `-E` it finds 8 lines. The quiet answer was not good news. It was a question asked in the wrong dialect.

**An empty result is an answer to your pattern, not to your question. Check the pattern.**

Put every pattern in single quotes, so the shell does not treat `*`, `$`, `|` or `{}` as its own symbols first. To search for text full of dots, such as an IP address (a computer's number on a network), use `grep -F`, which switches the pattern language off.

If you have used regex in a programming language, do not bring `\\d` along. GNU grep reads `-E '\\d'` as the letter d, so `grep -c -E '\\d' app.log` prints `24`, the lines that contain a d. Write `[0-9]` instead; it works everywhere.

You may have noticed that `*` and `?` showed up last time too, with other meanings. Next, we'll keep the two languages apart."""

S[4]["h"] = "Globs and regex are two different languages"
S[4]["body"] = """Two people in the building use the same words for different things. The clerk at the front desk reads `*` as "any file name". The worker reading the logbook reads `*` as "repeat the last character". Last lesson's globs and today's regular expressions look alike, and mixing them up causes real bugs.

The shell uses globs to match file names. Tools such as grep, sed and awk use regex to match text inside files. The same symbols mean different things:

- `*` in a glob means "anything". In a regex it means "zero or more of the previous character", so the regex for anything is `.*`.
- `.` in a glob is just a dot. In a regex it is any character, so a real dot is `\\.`.
- `?` in a glob is exactly one character. In an extended regex it makes the previous thing optional.

So the glob `*.log` means "file names ending in .log", while the regex for "text ending in .log" is `\\.log$`.

One command can contain both. In `grep -E 'ERROR|WARN' logs/*.log`, the shell expands the unquoted glob into file names. It leaves the regex alone because the regex sits in single quotes, so grep receives it untouched. The quotes decide who reads what.

Sometimes your question is not about the lines inside a file, but about the files themselves. Next, we'll look for files by name, size and age."""

S[5]["h"] = "Finding files by name, size and age"
S[5]["body"] = """Where is that settings file? Which logs are big and old enough to delete? grep cannot help here, because it reads what is inside files. For this, the building has a records clerk who walks every room on every floor and checks the label on each file without opening it.

That clerk is the find command. It walks down through every folder under a starting point and tests each file it meets. It prints the path of every file that passes all the tests. Its shape is `find START TESTS`:

- `-name '*.sql'` keeps names that match a glob. `-iname` does the same but ignores case.
- `-type f` keeps only files and `-type d` only directories (folders).
- `-size +1M` keeps files over 1 MB, and `-size -10k` files under 10 kB.
- `-mtime +7` keeps files last changed more than 7 days ago, and `-mtime -1` those changed in the last day. Every file records when its content last changed (its modification time, or mtime), and `ls -l` shows it.
- `-maxdepth 2` stops two levels down. Put it straight after the start folder: it sets a rule for the whole walk, so GNU find warns if it comes later.

Tests combine with an unwritten "and": `find server -type f -size +1M` lists the four big files in the lab.

Now the classic slip. Quote the pattern after `-name`. In `/work`, the unquoted `find server -name *.log` turns into `find server -name access.log app.log` before find runs, and find fails with `paths must precede expression`. In a folder with exactly one .log file, the same mistake silently searches for that one name, which is worse.

find can also act on what it finds:

- `-exec ls -lh {} +` runs one command with all the found files in place of `{}`.
- `-exec cat {} \\;` runs the command once for each file. The `;` ends the command, and the backslash stops the shell from taking `;` as the end of its own line.
- `-delete` deletes every match. Run the same find without `-delete` first and read the list, because there is no undo.

On a Mac, always give find a start folder, as in `find . -name '*.log'`. The next section says why."""

S[6]["h"] = "What changes on a Mac"
S[6]["body"] = """Your Mac ships BSD versions of these tools, while servers and containers have GNU versions. It is like two branches of the same company with slightly different forms. Most of today's commands behave the same on both. These do not:

- The Mac's grep has no `-P` (Perl-style patterns, where `\\d` means a digit). Use `-E` with `[0-9]`, which works on both.
- The Mac's find needs a start folder. GNU find assumes the current folder, so `find -name '*.log'` works in the container and fails on the Mac. Write `find . -name '*.log'` everywhere.
- On the Mac, `wc -l` pads the number with spaces, so a script that compares its output as text can break.

The grep options from this lesson (`-i -n -c -v -w -r -l -A -B -C -o -E -F`) and tail's `-f` and `-F` exist on both, so most of what you learn carries over. The course still runs everything in the container, because that is what servers and CI runners have. If you copy a one-liner into a script for your Mac, test it on the Mac once.

With these tools you can answer the customer on the phone. The worked example below does exactly that, following reference `7f3a9c` through four services."""

L["aside"] = {
    "title": "Why is it called grep?",
    "after": 1,
    "body": "The name comes from a command in ed, one of the first Unix text editors. In ed, `g/re/p` meant: globally search for a regular expression, and print the matching lines. People typed it so often that it became a program of its own. The odd name has stuck for more than fifty years.",
}

L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = "A customer quotes a reference number, and nobody knows yet which service failed. Teams with many small services prepare for that moment: each request gets an ID where it enters, and every service writes it in its logs. The person on call pastes the ID into a search and gets the timeline from the worked example. On a few servers, that search is grep over SSH (a remote login). On hundreds, it is a central log store (Day 55), with the same questions and the same regex."

W = L["worked"]["steps"]
W[0]["say"] = "A customer reports a failed checkout at about 09:06 and quotes the reference `7f3a9c`. The services write that request ID on every log line. Start with the service you know about: checkout."
W[1]["say"] = "Checkout called payments-api, so other logs matter too. With `-r`, grep searches the whole `logs` folder and puts the file name before each hit. Four services touched this request. The order of files may differ on your machine."
W[2]["say"] = "To answer \"which files?\", use `-l`, one name per line. The find command can ask the same question, which helps when you also want to filter files by name or age first."
W[3]["say"] = "Now only the errors for this request. The regex `ERROR .*req=7f3a9c` means ERROR, then anything, then the ID. Four errors, in three services."
W[4]["say"] = "Put the story in time order. `-h` drops the file names, and `sort` (Day 5) orders the lines. ISO timestamps (dates written year first, like 2026-10-30T09:06:18Z) sort correctly as plain text, so the result is a timeline across all services."
W[5]["say"] = "Read the earliest failure with context. `-B 3` shows the three lines before payments gave up. The cause sits at the bottom of the chain: bank-gateway took more than 3 seconds, and every other error is a reaction to that."

T = L["task"]
T["steps"] = [
    "Count the lines in `access.log` and print the first one. Each line is one web request: who sent it, when, what it asked for and how the server answered. Find the status code (the server's three-digit answer, such as 200 or 404) and the path in that line.",
    "Count the requests that got a 404, a 429 and any 5xx status. Use `-E` and a character class for the 5xx case.",
    "Print the line numbers of every POST to `/api/checkout` that failed with a 5xx.",
    "One client asked for paths like `/wp-login.php` and `/.env`. Find its IP with grep, then count how many requests that IP made.",
    "Count the lines whose referrer is `http://` rather than `https://`. Then write one regex that matches both and compare the counts.",
    "Use find to list every file under `server` larger than 500 kB, with sizes.",
    "Age two files with `touch -d '20 days ago' FILE`, then find files under `server/var/log` older than 14 days.",
    "Delete only the `.part` file in `server/tmp` with find, after previewing what it matches.",
]
T["hints"] = [
    "In this log the status sits between the closing quote of the request and the byte count, so `'\" 404 '` is a precise pattern.",
    "For the scanner, search for one of its paths with `-F`, read the first field of the result, then search for that IP.",
    "find sizes use k and M, as in `-size +500k`.",
]

L["explain_back"]["answer"] = "A glob is a pattern for file names that the shell expands before a command runs, so `*.log` becomes a list of matching names. A regular expression is a pattern for text that a tool like grep applies to every line inside files. In a glob, `*` means any characters, while in a regex it means zero or more of the previous character, so the regex for anything is `.*`. Single quotes keep a regex away from the shell, so the tool receives it unchanged."

L["recap"] = [
    "Use `less`, `head` and `tail` on big files, and `tail -F` to follow a live log.",
    "grep options answer questions: `-i` any case, `-c` how many, `-n` where, `-v` the rest, `-w` whole words.",
    "`-A`, `-B` and `-C` add context; `-r` searches folders, `-l` lists files and `-o` pulls out the match.",
    "Regex symbols: `.` `*` `^` `$` `[...]`, plus `+` `?` `{n}` `|` `()` with `-E`. Quote every pattern.",
    "Globs match file names in the shell; regular expressions match text inside tools.",
    "find selects files by name, type, size and age, but grep and find only see one machine, and `-delete` has no undo.",
]

C = L["check"]
C[0]["why"] = "`$` anchors the pattern to the end of the line. `-F` would search for the text `ms$` itself."
C[1]["why"] = "Unquoted, the glob expands to the one local match before find starts, so find searches for that exact name."
C[2]["why"] = "`4[0-9]{2}` means a 4 and then exactly two digits. `-F` would look for the brackets as plain text."

I = L["interview"]
I[0]["a"] = "If the services log a request or trace ID, I search for it in all logs at once with `grep -r ID logdir`. Then I narrow it with a regex such as `ERROR .*ID`. With ISO timestamps, `grep -h ID ... | sort` gives a timeline across services. I read the earliest error with `-B` and `-A` context, because later errors are often reactions to the first one."
I[1]["a"] = "Plain grep uses basic regular expressions. There, `+`, `?`, `|` and braces are ordinary characters unless you escape them. `grep -E` uses extended regular expressions, where those symbols work directly, which is easier to read. With `-F`, grep switches patterns off and searches for the exact text, which suits IP addresses and strings full of dots. All three exist on Linux and macOS, unlike `-P`, which is GNU only."
I[2]["a"] = "First I list the candidates, for example `find /var/log -type f -name '*.log' -mtime +14 -size +100M`, with the pattern quoted. I read the list and check that no running program still writes to those files. Then I run the same command with `-delete`, or archive the files instead. Deleting a file that a process still holds open does not free the space until the process closes it. So for a live log I would rotate or empty it instead."

L["deeper"]["body"] = """Try this with two terminals: watch a log for errors as new lines arrive.

1. In the container, in `/work`, create an empty file with `touch live.log`, then run `tail -f live.log | grep --line-buffered ERROR`.
2. Open a second terminal tab on your Mac and go to `~/code/linux-lab`. It is the same folder, seen from outside the container.
3. Add a line: `echo "$(date -u +%FT%TZ) ERROR checkout-api req=ab12cd disk full" >> live.log`. It appears in the first terminal at once.
4. Add an INFO line the same way. Nothing appears, because grep drops it. Press Ctrl+C in the first terminal when you are done.

Why `--line-buffered`? When grep writes to your screen, it prints each line straight away. When its output goes into another pipe, it collects lines in a buffer and writes them in big chunks, which is faster. Put another command after grep, such as `| tee alerts.txt`, and lines can sit in that buffer for a long time. `--line-buffered` tells grep to pass each line on at once. The Mac's grep has the same option.

Then there is rotation. Busy servers do not let one log grow forever. A tool called logrotate runs each night: it renames `app.log` to `app.log.1`, starts a fresh `app.log` and compresses older copies. `tail -f` follows the open file, not the name. After the rename it keeps watching `app.log.1`. Nobody writes there any more, so it goes silent without an error. `tail -F` follows the name and retries, so it notices the new file. In the container, `tail --help` describes `-F` as "same as --follow=name --retry". On any server where you expect to watch for more than a few minutes, use `-F`.

Deleting a big log that a program still has open has a similar surprise: it does not free the disk space. The program still holds the file, so the space only returns when the program closes it or restarts. That is why log rotation tools often empty a file in place instead of deleting it, and Day 6 shows how to see which program holds which file."""

L["closing"] = """We started with a customer on the phone and a reference number lost somewhere in four logbooks. Now you can follow `7f3a9c` through every service, put its lines in time order, and point at the slow bank gateway at the bottom of the chain.

The next time a search comes back empty, run `echo $?`. A 1 means no line matched, and a 2 means grep itself failed. Then ask whether your pattern used the right dialect.

Each of today's searches ended with one list. Next, we'll connect small tools so the output of one becomes the input of the next. The question it answers: how do you go from "which lines" to "how many, from whom, and how bad"?"""

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d04 written")
