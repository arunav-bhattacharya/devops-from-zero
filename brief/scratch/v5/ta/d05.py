"""Book-voice rewrite of d05 (Pipes, redirection and text tools). Writer: ta. Run from the repo root."""
import json

PATH = "content/p1.json"
P = json.load(open(PATH))
L = next(x for x in P["lessons"] if x["id"] == "d05")

L["opening"] = """Picture your manager stopping at your desk at nine. Traffic to the shop jumped overnight. Who is calling us, and what is failing? A short report by ten, please. You have the web server's logbook, a few hundred lines long, and the tools from last time.

grep can pick out lines, but the manager wants counts and rankings. The first idea is to copy the lines into a spreadsheet and count by hand. A second idea is quicker but worse: tidy the logbook "in place" and watch it come back empty. Both happen to smart people, because nobody has shown them how the office passes paper from one desk to the next.

Last time, we searched the logbooks with grep and find, and each search ended with one list. In this lesson, we'll connect small tools, so one tool's output becomes the next one's input, and turn raw lines into a ranked report. Before we start, make a guess, and keep it in mind."""

L["guess"]["q"] = "You want to sort a file in place, so you run `sort names.txt > names.txt`. What is in names.txt afterwards?"
L["guess"]["why"] = "The shell opens names.txt for writing, which empties it, before sort starts. So sort reads an empty file. Write to a new file and rename it instead."

L["terms"] = [
    {"term": "Stream", "plain": "A flow of bytes that a program reads or writes, such as the text it prints."},
    {"term": "stdin, stdout, stderr", "plain": "The three standard streams: input (0), normal output (1) and error messages (2)."},
    {"term": "File descriptor", "plain": "The small number a program uses for an open stream or file. 0, 1 and 2 are the standard ones."},
    {"term": "Redirection", "plain": "Sending a stream to or from a file with >, >> or <."},
    {"term": "Pipe", "plain": "The | symbol, which connects one program's stdout to the next program's stdin."},
    {"term": "Filter", "plain": "A program that reads lines, keeps or changes some of them, and writes lines, such as sort or grep."},
    {"term": "/dev/null", "plain": "A special file that throws away everything written to it."},
    {"term": "jq", "plain": "A command-line tool that picks out and reshapes JSON data, the way grep and awk work on plain text."},
]

S = L["sections"]

S[0]["h"] = "Every program has three trays: stdin, stdout and stderr"
S[0]["body"] = """Every desk in our office building has three trays. Work comes in through the in-tray. Finished pages go in the out-tray. Complaints, such as "this page is unreadable", go in a third tray, so they don't get mixed up with the good work.

Every Linux program has the same three trays. Each one is a stream, a flow of bytes, and all three are open before the program starts:

- stdin (standard input, number 0) is where it reads input. By default, that is your keyboard.
- stdout (standard output, number 1) is where it writes its results. By default, your screen.
- stderr (standard error, number 2) is where it writes error messages. Also your screen, by default.

The numbers are file descriptors: the small numbers a program uses for its open streams and files.

A program does not set up these trays itself. It gets them from the shell that started it, and in a terminal all three lead to the terminal. The program writes to 1 in the same way whether 1 leads to your screen, a file or another program. So the shell can point a tray somewhere else before the program starts, and the program needs no change. Redirection and pipes both rely on this.

Why two output trays? So results and complaints can go to different places. Run `ls app.log nosuch` and you get one error line and one result line that look alike on screen. They still travel separately, and you can send each one somewhere else.

Many tools read stdin when you give them no file. Type `wc -l` on its own and it waits. Type two lines, press Ctrl+D (which means "end of input"), and it prints `2`. If a command ever seems to hang, it may be waiting at an empty in-tray. Ctrl+D or Ctrl+C gets you out.

Next, we'll point the trays at files instead of the screen."""

S[1]["h"] = "Redirection: pointing a tray at a file"
S[1]["body"] = """Say the manager wants the results filed, not shown on a screen. Redirection connects a stream to a file instead. The shell opens the file, points the stream at it, and removes that part from the line before the program starts. In `echo hi > note.txt`, echo only receives `hi`. These are the forms you will use:

- `> file` sends stdout to a file, replacing what was in it.
- `>> file` adds stdout to the end of a file.
- `< file` feeds a file into stdin. `wc -l < app.log` prints `37` with no file name, because wc only saw a stream.
- `2> file` sends stderr to a file.
- `> file 2>&1` sends both to the same file. Read `2>&1` as "send 2 wherever 1 goes right now".
- `&> file` is a short form of the line above in bash and zsh.
- `2> /dev/null` throws error messages away. `/dev/null` is a special file that discards everything written to it, like a bin by the door.

Two mistakes here are very common. The first is the trap from the guess. A single `>` empties the file at once, before the command runs, so `sort copy.log > copy.log` leaves you with an empty file. The same goes for `sed 's/a/b/' f > f`. Write to a new file and move it into place, as in `sort f > f.new && mv f.new f`. After `set -o noclobber` the shell refuses to overwrite a file, with a message like `bash: notes.txt: cannot overwrite existing file`.

**`>` empties the file before the command starts. Never redirect into the file you are reading.**

The second mistake is about order. The shell reads redirections left to right. In `ls app.log nosuch > out.txt 2>&1`, stdout goes to the file first, then stderr follows it there. In `ls app.log nosuch 2>&1 > out.txt`, stderr is pointed at the screen, where stdout was at that moment. So the error still lands on your screen.

Use `>>` for logs you keep adding to, and `>` only for files you mean to replace.

A more useful place to send a tray is another desk. Next, we'll connect two programs directly."""

S[2]["h"] = "Pipes: a chute from one desk to the next"
S[2]["body"] = """Imagine a chute from one worker's out-tray straight into the next worker's in-tray. One worker picks out pages, the next counts them, and neither knows the other exists.

A pipe, written `|`, is that chute. It connects the stdout of one program to the stdin of the next. For `grep ERROR app.log | wc -l`, the shell creates a pipe, a small buffer that the operating system keeps in memory. It points grep's stdout at one end and wc's stdin at the other, then starts both. grep picks lines and wc counts them: `4`.

Programs that read lines, keep or change some of them, and write lines are called filters. Pipes let you chain small filters into an answer.

All the programs in a pipeline start at the same moment and pass lines along as they go. Most steps do not wait for the previous one to finish, which is why `tail -f app.log | grep ERROR` works on a log that never ends. The sort command is the exception: it has to read every line before it can print the first.

Build a pipeline one step at a time: add one step, run it, look at the output, then add the next. Cap long output with `| head` while you work. Checking each step as you go is far quicker than hunting for the broken step at the end.

Only stdout goes through a pipe. In `ls nosuch | grep x`, the error from ls skips the chute and lands on your screen, which is exactly what stderr is for.

A pipeline also has an exit code, the number a program hands back when it ends. By default it is the last program's. So `grep nosuch app.log | wc -l` prints `0`, and `echo $?` prints `0` too: grep failed, but wc succeeded. Day 7 shows how `set -o pipefail` changes that. The operators `&&` and `||` look at the last exit code to decide whether the next command runs:

- `a && b` runs b only if a succeeded.
- `a || b` runs b only if a failed.
- Together: `grep -q ERROR app.log && echo 'has errors' || echo 'clean'` prints `has errors`.

Now we have chutes. Next, we'll meet the workers who count and slice the pages that come down them."""

S[3]["h"] = "Sort, count and cut"
S[3]["body"] = """The manager's questions are counting questions: which IP address sends the most requests, or how many errors each service had. An IP address is the number that identifies a computer on a network. These filters do the counting and slicing:

- `sort` sorts lines as text, character by character, so `10` comes before `9`. Add `-n` to sort as numbers, `-r` to reverse, `-k 3` to sort by the third field, and `-t :` to split fields on colons instead of spaces.
- `uniq` removes repeated lines, but only when they sit next to each other. It remembers just the line before, which keeps it fast on huge files. That is why it nearly always comes after sort. With `-c` it puts a count in front of each line.
- `wc -l` counts lines, `-w` words and `-c` bytes.
- `cut -d ' ' -f 1` splits each line on spaces and keeps field 1. `-f 1,3` keeps fields 1 and 3.
- `tr` translates characters. `tr a-z A-Z` upper-cases text, `tr -d 'Z'` deletes every Z and `tr -s ' '` squeezes runs of spaces into one.
- `head -n 5` keeps the first five lines, so it doubles as a top-5 limiter.
- `tee file`, named after a T-shaped pipe joint, copies its input into a file and passes it on. `grep ERROR app.log | tee errors.txt | wc -l` saves the error lines and counts them.

For example, `sort -t : -k 3 -n /etc/passwd` sorts the user list by user ID, a number in the third colon-separated field.

`cut` has one catch: it treats every single space as a separator. The lab's `app.log` pads short levels, so `INFO  checkout-api` has two spaces in it. As a result, `cut -d ' ' -f 3 app.log | sort | uniq -c` reports 33 empty fields and only 4 service names. That is not the tally we were hoping for. Squeeze the spaces first with `tr -s ' '`, or use awk, which treats a run of spaces as one.

For columns with conditions and sums, there is a better worker. Next, we'll meet awk."""

S[4]["h"] = "Columns, conditions and sums with awk"
S[4]["body"] = """Picture a clerk who reads a table one row at a time, keeps only the rows you asked about, and adds up one column as they go. That clerk is awk, a small programming language for columns.

For each line, awk splits the text on runs of spaces into fields `$1`, `$2` and so on (`$0` is the whole line), then runs your program. The program has the shape `condition {action}`. With no condition, the action runs on every line. With no action, awk prints each line that meets the condition.

In the lab's `access.log`, field 1 is the client IP and field 10 the bytes sent. Field 9 is the HTTP status, the server's three-digit answer, such as 200 or 404. Most of what you will do with awk looks like one of these:

1. Print columns. `awk '{print $1, $9}' access.log` prints the client IP and the status code of each request.
2. Keep rows that meet a condition. `awk '$9 >= 500' access.log` prints only server errors. A regex works as a condition too: `awk '/^2026/ {print $2}' app.log` prints the level of each line that starts with a date.
3. Add things up. `awk '{sum += $10} END {print sum}' access.log` adds the bytes column. `END` is a condition that is true once, after the last line, so it prints `850599`.

The option `-F` changes the field separator. Access log lines put quotes around the request and the user agent (the software that sent it). So `awk -F '"' '{print $6}' access.log` splits on quotes and prints the user agent.

Always put an awk program in single quotes. Otherwise the shell reads `$1` as one of its own variables and replaces it before awk starts.

On Ubuntu, `awk` is a small version called mawk, and on the Mac it is BSD awk. These examples use only standard awk, which both understand.

awk reads and reports. Sometimes you need to change the text as it passes. Next, we'll edit a stream, and hand lines to commands that refuse to read stdin."""

S[5]["h"] = "Editing streams with sed, and xargs"
S[5]["body"] = """Before a log goes into a ticket, someone has to black out the customer references. The sed tool, short for stream editor, does that kind of edit as the text streams past. It reads a line, applies your edit, prints the result to stdout and moves on. The file it reads stays unchanged, so you redirect the output to keep it. Its most used command is substitute, `s/old/new/`:

- `sed 's/ERROR/ERR/' app.log` prints the file with the first ERROR on each line changed. Add `g` at the end to change every match on the line.
- The old part is a regex, and `-E` turns on extended regex. So `sed -E 's/req=[0-9a-f]+/req=XXXXXX/g' app.log` masks every request ID before you paste a log into a ticket.
- `sed -n '8,10p' app.log` prints only lines 8 to 10.
- `-i` edits the file in place, with no undo. sed writes a new file and renames it over the old one, so it avoids the empty-file trap of `> f`.

Mac and Linux disagree about `-i`. GNU sed on Linux takes `sed -i 's/a/b/' file`. BSD sed on the Mac needs a backup suffix right after `-i`, even an empty one: `sed -i '' 's/a/b/' file`. Each form breaks on the other system. On Linux, `sed -i ''` fails with `sed: can't read s/a/b/: No such file or directory`. The form `sed -i.bak 's/a/b/' file` works on both and keeps a backup copy.

Some commands, like `ls` and `rm`, ignore stdin and only take arguments. Their in-tray is nailed shut. For those there is xargs, which turns lines on stdin into arguments for a command. So `grep -r -l 7f3a9c logs | xargs wc -l` takes the four file names grep printed and runs `wc -l` on all of them.

By default xargs splits on spaces, so a file called `old report.tmp` becomes two arguments, `old` and `report.tmp`, and rm fails on both. For file names you do not control, use `find ... -print0 | xargs -0 ...`. It separates names with a byte that cannot appear in a file name.

Everything so far has been about lines. One very common kind of data ignores lines completely. Next, we'll read JSON."""

S[6]["h"] = "JSON with jq, and command substitution"
S[6]["body"] = """Some paperwork arrives as forms with labelled boxes instead of plain lines. JSON is that kind of data: text made of named fields and lists, inside curly and square brackets. Kubernetes, cloud tools and most web APIs (the ways programs ask other programs for data) speak JSON, and grep handles it badly. grep thinks in lines, but JSON ignores them. One object can spread over twenty lines, or a whole file can sit on one.

For JSON you use jq, which does what grep, cut and awk do for text. You give it a filter, and it applies the filter to each JSON value it reads. The lab's `pods.json` is shaped like what Kubernetes returns when you list running apps (Day 39):

- `.` prints the input, nicely indented: `jq . pods.json`.
- `.field` picks a field, and fields chain: `.items[0].metadata.name`.
- `.[]` unpacks an array (a list) into its elements. `jq '.items[].metadata.name' pods.json` prints four names, in quotes.
- `-r` (raw) prints strings without quotes, which is what you want before a pipe.
- Inside a filter, `|` works like a shell pipe, and `select(condition)` keeps only the values that match.

Together: `jq -r '.items[] | select(.status.phase != "Running") | .metadata.name' pods.json` prints the one item that is not running. The file `events.jsonl` holds one JSON object per line, and jq reads them one by one. So `jq -r '.service' events.jsonl | sort | uniq -c` counts events per service.

One last trick passes a whole answer into another line. Command substitution, written `$(command)`, runs a command first and pastes its output into your line. Then the rest of the line runs. `count=$(grep -c ERROR app.log)` stores `4` in a variable, a named value the shell remembers. Then `echo "app.log has $count errors"` uses it. In the same way, `wc -l $(grep -r -l 7f3a9c logs)` hands grep's file list to wc as arguments, a simpler cousin of xargs.

These tools work on one machine's files, one pipeline at a time. That is enough for the manager's report, and the worked example below builds it."""

L.pop("analogy", None)
L.pop("mistake", None)
L["real_world"] = "Traffic jumps, and the first questions are \"who is calling us?\" and \"what is failing?\". The first answer often comes from the worked example's pipeline, run on a load balancer log before anyone opens a dashboard. A load balancer is the server that spreads incoming requests across many copies of an app. Engineers also pipe Kubernetes JSON into jq every day, for example to list the apps that keep restarting."

W = L["worked"]["steps"]
W[0]["say"] = "Look at one line before you write a pipeline. Split on spaces, the IP is field 1, the path is field 7 and the status is field 9. A quick awk confirms the numbers."
W[1]["say"] = "Count requests per IP. Without sort, uniq only merges neighbours, so every count is 1. After sort, identical IPs sit together and `uniq -c` counts them. Note that sort orders text, so `10.0.0.2` comes first."
W[2]["say"] = "Rank by count. `sort -rn` sorts the counts as numbers, largest first, and `head -n 5` keeps the top five. One client sent 61 of the 238 requests."
W[3]["say"] = "Now the server errors, status 500 and up. Printing the status with the path keeps 500 and 504 apart. Checkout is the failing endpoint (the web address that fails)."
W[4]["say"] = "The 404s (client errors) are a separate problem. The top paths are files this shop never had, and grouping the 404s by IP shows that one client sent almost all of them. That is a scanner, a program probing for weak spots, not a broken link on the site."
W[5]["say"] = "Save the answers. The first command writes `report.txt` with `>`, and the second adds to it with `>>`. Use `>` twice by mistake and the first part is gone."

T = L["task"]
T["steps"] = [
    "Count how many requests got each status code in `access.log`, most common first.",
    "Add up the bytes sent to the client `198.51.100.23`.",
    "Find the three most common user agents by splitting each line on quotes with awk.",
    "Write `report.txt`: a heading line, the status counts, a second heading and the top 5 IPs. Use `>` for the first line and `>>` for the rest, then `cat` the file.",
    "Run `ls access.log nosuch` three ways: errors only into `err.txt`, both streams into `all.txt`, and errors thrown away.",
    "From `events.jsonl`, print the request ID and error type of every error event as plain text, one per line.",
    "From `pods.json`, list the names of the items with more than 5 restarts.",
    "Mask every request ID in `app.log` with sed and save the result as `app-masked.log`, without changing `app.log`.",
]
T["hints"] = [
    "The status is field 9 and the byte count field 10.",
    "In jq, a string like `\"\\(.request_id) \\(.error.type)\"` combines two fields.",
    "Keep `| head` on the end while you build a pipeline, and remove it when the output looks right.",
]

L["explain_back"]["answer"] = "The awk step prints the first field of each line, the client IP, and each pipe feeds that stream into the next program's stdin. Then sort puts identical IPs next to each other, which uniq needs, because it only merges neighbouring duplicates. With `-c`, uniq prints each IP once with its count. The last two steps rank the result: `sort -rn` orders the counts from highest to lowest as numbers, and `head -n 5` keeps the top five."

L["recap"] = [
    "Every program has stdin (0), stdout (1) and stderr (2), and redirection points them at files.",
    "`>` replaces, `>>` appends, `2>&1` joins errors to output, and `/dev/null` discards.",
    "A pipe joins stdout to the next stdin; build pipelines one step at a time.",
    "`sort | uniq -c | sort -rn | head` turns raw lines into a ranked count.",
    "awk handles columns, conditions and sums; sed substitutes; xargs turns lines into arguments; jq does the same jobs for JSON.",
    "These tools read one machine's files; for hundreds of servers you need a central log store (Day 55).",
]

C = L["check"]
C[0]["q"] = "A job runs `./backup.sh > backup.log`, but its error messages still appear on the screen and are missing from the log. What fixes it?"
C[0]["why"] = "Redirections run left to right, so stdout must point at the file before `2>&1` sends stderr to the same place."
C[1]["why"] = "uniq only merges identical lines that are next to each other, so the input must be sorted first."
C[2]["q"] = "A web service sends back `{\"users\":[{\"name\":\"ana\",\"active\":true},{\"name\":\"ben\",\"active\":false}]}`. Which filter prints `ben` with no quotes?"
C[2]["why"] = "`.users[]` unpacks the array, select keeps the inactive user, `.name` picks the field, and `-r` drops the quotes."

I = L["interview"]
I[0]["a"] = "Both send stdout to a file; `>` empties the file first, while `>>` appends. The shell sets them up before the command runs. That is why `sort f > f` leaves f empty. `2>&1` makes stderr go wherever stdout points at that moment, so in `cmd > log 2>&1` both end up in the log. Written the other way round, errors still reach the terminal, because redirections are processed left to right."
I[1]["a"] = "I would pull out the IP field and count it: `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -n 10`. sort has to come before uniq, because uniq only merges neighbouring duplicates. First I would look at one line to check that the IP really is field 1. A load balancer in front can change which address the log records (Day 11)."
I[2]["a"] = "When the command takes its input as arguments and ignores stdin, like `rm`, `ls` or `kill`. xargs reads lines and adds them as arguments, batching many into one call. With file names that may contain spaces, I use `find -print0 | xargs -0`, or `find -exec ... {} +`, which avoids the splitting problem."

L["deeper"]["body"] = """Plain jq works on one JSON value at a time. A total or a count per group needs all of them at once. The `-s` (slurp) option reads every value into one array first, so a single filter can see them all. All of these run on the lab's `events.jsonl`:

- `jq -s 'length' events.jsonl` prints `18`, the number of events.
- `jq -s '[.[] | select(.event == "order.created") | .amount] | add' events.jsonl` prints `86.5`, the total of the orders that went through. The square brackets collect the selected amounts into a new array, and `add` sums it.
- `jq -r -s 'group_by(.service)[] | "\\(.[0].service) \\(length)"' events.jsonl` prints one line per service with its count: checkout-api 9, orders-worker 3 and payments-api 6. The function `group_by` makes an array of arrays, one per service.
- `jq -r '[.ts, .service, .level] | @tsv' events.jsonl` turns each object into one tab-separated line, ready for sort, cut and awk.
- `jq -r 'select(.duration_ms > 1000) | "\\(.duration_ms) \\(.service) \\(.event)"' events.jsonl | sort -rn` lists the slow events, slowest first. The top line is `6012 checkout-api checkout.failed`.

The last two examples are the habit to keep: let jq turn JSON into plain lines, then use the text tools you already know. You do not need all of jq. With `select`, string templates and `@tsv` you can answer most everyday questions.

Watch out for missing fields. Not every event has `duration_ms`. For jq a missing field is `null`, and null counts as smaller than any number. So `null > 1000` is false, and those events drop out quietly. When a field may be missing, write a default with `//`: `.duration_ms // 0`.

Keep this for Day 39. When you meet `kubectl get pods -o json` there, today's filters work almost unchanged. Swap `pods.json` for the live output and the same select finds the pods that are not running."""

L["closing"] = """We started with a manager at your desk at nine, asking who is calling and what is failing. Now each question has a one-line answer, filed with `>` and `>>`. The top caller sent 61 requests, checkout is failing, and one scanner is behind almost every 404.

Before you press Enter on any line with `>`, check that the file after it is not one you are reading on the same line.

Next, we'll meet the people and keys of the building: who may open which drawer, and how to stop a worker who won't stop. The question it answers: who is allowed to do what on a Linux machine?"""

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
open(PATH, "a").write("\n")
print("d05 written")
