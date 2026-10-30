"""Console examples for Part 1. capture.py runs them; build_p1.py embeds the saved output.
Each value: {"group": lab-copy name, "steps": [commands or step dicts]}. See capture.run_snippet."""

import pathlib

SNIPPETS = {}
FILES = pathlib.Path(__file__).resolve().parent / "files"


def heredoc(name, dest=None):
    """A shell command that writes files/<name> to dest (default: same name)."""
    return f"cat > {dest or name} <<'END'\n" + (FILES / name).read_text() + "END"


def S(name, steps, group=None, **kw):
    SNIPPETS[name] = dict(steps=steps, group=group or name.split(".")[0], **kw)


# ============================================================ Day 3
S("d03.w1", ["pwd", "ls", "ls server"])
S("d03.w2", ["cd server/var/log", "pwd", "ls", "cd shop", "pwd", "cd ../../..", "pwd", "cd -", "cd", "pwd", "cd /work"])
S("d03.w3", ["ls -lh server/var/log/shop", "ls -a server/etc/shop"])
S("d03.w4", ["mkdir -p playground/archive/2026-10",
             "echo cp server/var/log/shop/app-2026-*.log playground/archive/2026-10/",
             "cp server/var/log/shop/app-2026-*.log playground/archive/2026-10/",
             "ls playground/archive/2026-10"])
S("d03.w5", ["mv playground/archive/2026-10/app-2026-10-29.log playground/latest.log",
             "tree playground"])
S("d03.w6", ["echo rm playground/archive/2026-10/*.log",
             "rm playground/archive/2026-10/*.log",
             "rmdir playground/archive/2026-10",
             "rm playground",
             "rm -r playground",
             "ls"])
# inline facts for the sections
S("d03.glob", ["echo *.log", "echo \"*.log\"", "echo logs/*.log", "echo logs/[cp]*.log",
               "ls server/var/log/shop/app-2026-10-2?.log", "echo *.txt", "echo ~"], group="d03x")
S("d03.zsh", [{"cmd": "apt-get install -y -qq zsh > /dev/null 2>&1", "hide": True, "timeout": 120},
              "zsh -c 'echo *.txt'", "zsh -c 'echo server/**/*.sql'"], group="d03x")
S("d03.errors", ["ls nosuch", "mkdir a/b/c", "mkdir -p a/b/c", "rmdir a", "rm a", "touch \"my notes.txt\"",
                 "ls my notes.txt", "ls \"my notes.txt\"", "ls my\\ notes.txt", "rm -r a \"my notes.txt\""], group="d03x")
S("d03.help", ["ls --help | head -n 4", "man ls", "type cd", "which ls", "ls /", "ls -l app.log", "ls -l --block-size=1 app.log"], group="d03x")
S("d03.shell", ["echo $0", "ps -p $$", "ls -la server/home/dev"], group="d03x")

# ============================================================ Day 4
S("d04.view", ["wc -l app.log", "head -n 3 app.log", "tail -n 2 app.log"], group="d04x")
S("d04.ladder1", ["grep ERROR app.log", "grep -i error app.log", "grep -c ERROR app.log", "grep -c -i error app.log",
                  "grep -n WARN app.log"], group="d04x")
S("d04.ladder2", ["grep -v INFO app.log", "grep -c 200 app.log", "grep -c -w 200 app.log", "grep 200 app.log | grep -v ' 200 '"], group="d04x")
S("d04.ladder3", ["grep -A 2 NullPointer app.log", "grep -B 1 -A 2 'connection refused' app.log", "grep -n -C 1 ' 504 ' app.log"], group="d04x")
S("d04.ladder4", ["grep -r -l ERROR logs", "grep -r -c ERROR logs", "grep -o 'req=[0-9a-f]*' app.log | head -n 3"], group="d04x")
S("d04.exit", ["grep -q ERROR app.log", "echo $?", "grep -q FATAL app.log", "echo $?", "grep ERROR nosuch.log", "echo $?",
               "grep -q ERROR app.log && echo 'found errors'"], group="d04x")
S("d04.regex1", ["grep -v '^2026' app.log", "grep -c 'ms$' app.log", "grep -c 'orders.db' app.log", "grep 'orders.db' app.log | head -n 1",
                 "grep -c -F 'orders.db' app.log"], group="d04x")
S("d04.regex2", ["grep -E ' 50[0-9] ' app.log", "grep -o -E '[0-9]+ms' app.log | head -n 4", "grep -o -E 'req=[0-9a-f]{6}' app.log | head -n 2",
                 "grep -c 'WARN|ERROR' app.log", "grep -c -E 'WARN|ERROR' app.log", "grep -c 'https://' access.log", "grep -c -E 'https?://' access.log"], group="d04x")
S("d04.regex3", ["grep -c -E '\\d' app.log", "grep -c d app.log", "grep -o -E 'req=[0-9a-f]+' app.log | head -n 2", "grep -c -P '\\d{4}ms' app.log", "grep -c -E '[0-9]{4}ms' app.log",
                 "grep -E '(GET|POST) /api/checkout' app.log | head -n 2", "grep -c -E '\" 5[0-9]{2} ' access.log"], group="d04x")
S("d04.find1", ["find logs", "find server -name '*.sql'", "find server -name *.log", "find server -iname 'NOTES*'",
                "find server -maxdepth 2 -type d"], group="d04x")
S("d04.find2", ["find server -type f -size +1M", "find server -type f -size +1M -exec ls -lh {} +",
                "find server -type f -name '*.lock' -exec cat {} \\;"], group="d04x")
S("d04.find3", ["touch -d '10 days ago' server/var/log/shop/app-2026-10-27.log server/var/log/shop/app-2026-10-28.log",
                "find server/var/log -name '*.log' -mtime +7",
                "find server/var/log -name '*.log' -mtime -1 | sort",
                "find server/tmp -name '*.part'", "find server/tmp -name '*.part' -delete", "ls server/tmp"], group="d04f")
S("d04.w", ["grep 7f3a9c logs/checkout.log",
            "grep -r 7f3a9c logs",
            "grep -r -l 7f3a9c logs",
            "grep -r -E 'ERROR .*req=7f3a9c' logs",
            "grep -r -h 7f3a9c logs | sort",
            "find logs -name '*.log' -exec grep -l 7f3a9c {} +",
            "grep -B 3 'charge failed' logs/payments.log"], group="d04w")
S("d04.tailf", [{"cmd": "touch live.log; (sleep 1; echo '2026-10-30T09:30:00Z ERROR checkout-api req=ab12cd disk full' >> live.log; sleep 1; echo '2026-10-30T09:30:02Z INFO  checkout-api req=ab12ce GET /healthz 200 2ms' >> live.log) & disown", "hide": True},
                {"cmd": "tail -f live.log | grep --line-buffered ERROR", "keys": [(3, "\x03", "^C")]}], group="d04x")
S("d04.patterns", [{"cmd": "printf 'ERROR\\nTimeout|timeout\\nrefused\\n[0-9]{4}ms\\n' > alert-patterns.txt", "hide": True},
                   "grep -c -E -f alert-patterns.txt app.log", "grep -n -E -f alert-patterns.txt app.log"], group="d04x")

# ============================================================ Day 5
S("d05.streams", ["ls app.log nosuch", "ls app.log nosuch > out.txt", "cat out.txt", "ls app.log nosuch 2> err.txt", "cat err.txt",
                  "ls app.log nosuch > all.txt 2>&1", "cat all.txt", "ls app.log nosuch 2>&1 > out.txt", "ls app.log nosuch &> all.txt",
                  "ls app.log nosuch 2> /dev/null"], group="d05x")
S("d05.redir", ["echo one > notes.txt", "echo two > notes.txt", "cat notes.txt", "echo three >> notes.txt", "cat notes.txt",
                "wc -l app.log", "wc -l < app.log", "cp access.log copy.log", "sort copy.log > copy.log", "wc -l copy.log",
                "set -o noclobber", "echo four > notes.txt"], group="d05x")
S("d05.stdin", [{"cmd": "wc -l", "keys": [(0.5, "first line\n", "first line\n"), (0.3, "second line\n", "second line\n"), (0.3, "\x04", "")]},
                "grep nosuch app.log | wc -l", "echo $?", "ls nosuch | grep x", "true", "echo $?", "false", "echo $?",
                "grep -q ERROR app.log && echo 'has errors' || echo 'clean'"], group="d05x")
S("d05.tools1", ["cut -d ' ' -f 1 access.log | head -n 3", "cut -d ' ' -f 3 app.log | sort | uniq -c", "head -n 6 app.log | tr -s ' ' | cut -d ' ' -f 3",
                 "head -n 1 app.log | tr a-z A-Z", "head -n 1 app.log | tr -d 'Z'", "sort -t : -k 3 -n /etc/passwd | head -n 4 | cut -d : -f 1,3"], group="d05x")
S("d05.tools2", ["cut -d ' ' -f 1 access.log | head -n 6", "cut -d ' ' -f 1 access.log | head -n 6 | uniq -c",
                 "cut -d ' ' -f 1 access.log | head -n 6 | sort | uniq -c", "cut -d ' ' -f 1 access.log | sort | uniq | wc -l",
                 "grep ERROR app.log | tee errors.txt | wc -l", "wc -l errors.txt"], group="d05x")
S("d05.awk", ["awk '{print $1, $9}' access.log | head -n 3", "awk '/^2026/ {print $2}' app.log | sort | uniq -c",
              "awk -F '\"' '{print $6}' access.log | sort | uniq -c | sort -rn | head -n 3",
              "awk '$9 >= 500' access.log | wc -l", "awk '$9 >= 500 {print $1, $7, $9}' access.log | head -n 3",
              "awk '{sum += $10} END {print sum}' access.log", "awk '$1 == \"203.0.113.7\" {n++; bytes += $10} END {print n, bytes}' access.log"], group="d05x")
S("d05.sed", ["sed 's/ERROR/ERR/' app.log | grep ERR | head -n 2", "sed -n '8,10p' app.log",
              "sed -E 's/req=[0-9a-f]+/req=XXXXXX/g' app.log | head -n 4",
              "cp app.log app-copy.log", "sed -i 's/checkout-api/checkout/' app-copy.log", "head -n 1 app-copy.log",
              "sed -i '' 's/a/b/' app-copy.log"], group="d05x")
S("d05.xargs", ["grep -r -l 7f3a9c logs | xargs wc -l", "find server -name '*.sql' | xargs ls -lh",
                "echo app.log access.log | xargs -n 1 wc -l",
                "touch 'old report.tmp'", "find . -maxdepth 1 -name '*.tmp' | xargs rm",
                "find . -maxdepth 1 -name '*.tmp' -print0 | xargs -0 rm -v"], group="d05x")
S("d05.jq1", ["jq . pods.json | head -n 12", "jq '.items | length' pods.json", "jq '.items[].metadata.name' pods.json",
              "jq -r '.items[].metadata.name' pods.json",
              "jq -r '.items[] | select(.status.phase != \"Running\") | .metadata.name' pods.json",
              "jq -r '.items[] | select(.status.containerStatuses[0].restartCount > 5) | .metadata.name' pods.json"], group="d05x")
S("d05.jq2", ["head -n 1 events.jsonl", "head -n 1 events.jsonl | jq .", "jq -r '.service' events.jsonl | sort | uniq -c",
              "jq -c 'select(.level == \"error\") | {service, request_id, type: .error.type}' events.jsonl",
              "jq -r 'select(.request_id == \"7f3a9c\") | \"\\(.ts) \\(.service) \\(.event)\"' events.jsonl"], group="d05x")
S("d05.subst", ["count=$(grep -c ERROR app.log)", "echo \"app.log has $count errors\"", "echo \"Report for $(date -u +%F)\"",
                "wc -l $(grep -r -l 7f3a9c logs)"], group="d05x")
S("d05.w1", ["head -n 1 access.log", "head -n 1 access.log | awk '{print $1, $7, $9}'", "awk '{print $1}' access.log | head -n 4"], group="d05w")
S("d05.w2", ["awk '{print $1}' access.log | uniq -c | head -n 4", "awk '{print $1}' access.log | sort | uniq -c"], group="d05w")
S("d05.w3", ["awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -n 5"], group="d05w")
S("d05.w4", ["awk '$9 >= 500 {print $9, $7}' access.log | sort | uniq -c | sort -rn",
             "awk '$9 == 404 {print $7}' access.log | sort | uniq -c | sort -rn | head -n 5",
             "awk '$9 == 404 {print $1}' access.log | sort | uniq -c | sort -rn"], group="d05w")
S("d05.w5", ["awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -n 5 > report.txt",
             "awk '$9 >= 500 {print $9, $7}' access.log | sort | uniq -c | sort -rn >> report.txt",
             "wc -l report.txt"], group="d05w")

# ============================================================ Day 6
WORKER = heredoc("worker.sh")
S("d06.users", ["whoami", "id", "grep -E '^(root|www-data|nobody):' /etc/passwd", "useradd -m -s /bin/bash dev", "id dev",
                "su - dev -c 'whoami; pwd'", "su - dev -c 'cat /etc/shadow'", "ls -l /etc/shadow", "su - dev -c 'touch /etc/test'"], group="d06x")
S("d06.perm", [{"cmd": "cd /tmp", "hide": True}, "printf 'echo deploying version 1.4.1\\n' > deploy.sh", "ls -l deploy.sh", "./deploy.sh", "echo $?",
               "chmod u+x deploy.sh", "ls -l deploy.sh", "./deploy.sh", "chmod 640 deploy.sh", "ls -l deploy.sh", "chmod 755 deploy.sh",
               "stat -c '%A %a %U:%G %n' deploy.sh", "chmod go-rx deploy.sh", "stat -c '%A %a %n' deploy.sh",
               "umask", "touch new.txt", "mkdir newdir", "ls -ld new.txt newdir"], group="d06x")
S("d06.dirs", [{"cmd": "useradd -m -s /bin/bash dev; cd /tmp", "hide": True}, "mkdir vault", "echo 'api-key=fake-0000' > vault/key.txt",
               "chmod 700 vault", "ls -ld vault", "su dev -c 'ls /tmp/vault'", "su dev -c 'cat /tmp/vault/key.txt'",
               "chmod 711 vault", "su dev -c 'ls /tmp/vault'", "su dev -c 'cat /tmp/vault/key.txt'",
               "chown dev:dev vault/key.txt", "ls -l vault/key.txt"], group="d06x")
S("d06.ps", ["ps aux", "sleep 300 &", "ps -o pid,ppid,stat,cmd", "pgrep -a sleep", "jobs", "kill %1", "jobs", "ps -o pid,ppid,stat,cmd"], group="d06x")
S("d06.jobs", [{"cmd": "sleep 300", "keys": [(1, "\x1a", "^Z")]}, "jobs", "bg", "jobs",
               {"cmd": "fg", "keys": [(1, "\x03", "^C")]}, "echo $?",
               "sleep 300 &", "kill -9 %1", "jobs", "sleep 300 &", "kill %1", "wait %1", "echo $?"], group="d06x")
S("d06.nohup", ["nohup sleep 1", "ls", "kill -l | head -n 3"], group="d06x", cwd="/tmp")
S("d06.worker", [{"cmd": "cd /tmp", "hide": True}, {"cmd": WORKER, "hide": True}, "chmod +x worker.sh",
                 "./worker.sh > worker.log &", "sleep 5", "kill $!", "wait $!", "echo $?", "cat worker.log",
                 "./worker.sh > worker.log &", "sleep 3", "kill -9 $!", "wait $!", "echo $?", "cat worker.log"], group="d06x")
S("d06.top", ["top -b -n 1 | head -n 12", "uptime", "free -h", "df -h /", "du -sh server/*", "du -sh server/var/* | sort -h", "nproc"], group="d06x")
NGINX = {"cmd": "apt-get install -y -qq nginx > /dev/null 2>&1; sed -i '/listen \\[::\\]/d' /etc/nginx/sites-enabled/default", "hide": True, "timeout": 180}
S("d06.w", [NGINX, "nginx", "ps -o user,pid,ppid,cmd -C nginx", "---",
            "ss -tlnp", "lsof -iTCP -sTCP:LISTEN -n -P", "curl -sI localhost | head -n 1", "---",
            "cat /run/nginx.pid", "kill -HUP $(cat /run/nginx.pid)", "sleep 1", "ps -o user,pid,ppid,cmd -C nginx", "---",
            "kill $(cat /run/nginx.pid)", "sleep 1", "pgrep nginx", "echo $?", "curl -s localhost", "echo $?", "---",
            "systemctl status nginx",
            {"cmd": "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq systemd > /dev/null 2>&1", "hide": True, "timeout": 240},
            "systemctl status nginx", "---", "head -n 3 /usr/lib/systemd/system/nginx.service",
            "grep -E '^(\\[|Exec|Wanted)' /usr/lib/systemd/system/nginx.service"], group="d06w")
UNIT = heredoc("hello-worker.service")
S("d06.unit", [{"cmd": "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq systemd > /dev/null 2>&1; useradd -m ubuntu; cd /tmp", "hide": True, "timeout": 240},
               {"cmd": WORKER, "hide": True}, {"cmd": UNIT, "hide": True},
               {"cmd": "install -m 755 worker.sh /usr/local/bin/worker.sh && cp hello-worker.service /etc/systemd/system/", "hide": True},
               "systemd-analyze verify /etc/systemd/system/hello-worker.service", "echo $?",
               "systemctl --root=/ enable hello-worker.service", "systemctl --root=/ is-enabled hello-worker.service",
               "bash -n /usr/local/bin/worker.sh", "shellcheck /usr/local/bin/worker.sh", "echo $?"], group="d06u")

# ============================================================ Day 7
S("d07.env", ["echo $HOME", "printenv HOME", "GREETING=hi", "echo $GREETING", "bash -c 'echo \"child sees [$GREETING]\"'",
              "export GREETING", "bash -c 'echo \"child sees [$GREETING]\"'", "GREETING=hey bash -c 'echo \"one command sees [$GREETING]\"'",
              "echo $GREETING", "bash -c 'export COLOR=blue; echo \"child set [$COLOR]\"'", "echo \"parent sees [$COLOR]\"",
              "unset GREETING", "echo \"[$GREETING]\"", "name = alice"], group="d07x")
S("d07.path", ["echo $PATH", "which ls jq", "type cd ls jq", "nosuchcmd", "echo $?", "mkdir -p ~/bin",
               "printf '#!/usr/bin/env bash\\necho \"hello from my own command\"\\n' > ~/bin/hello", "chmod +x ~/bin/hello", "hello",
               "export PATH=\"$HOME/bin:$PATH\"", "hello", "which hello", "ls -a ~"], group="d07x")
S("d07.quotes", ["name=\"Ada Lovelace\"", "echo 'Hello, $name'", "echo \"Hello, $name\"", "file=\"my notes.txt\"", "touch \"$file\"",
                 "ls $file", "ls \"$file\"", "echo \"Today is $(date -u +%A)\""], group="d07x")
S("d07.apt", [{"cmd": "apt-get update -qq", "timeout": 120}, "apt search jq 2>&1 | head -n 4", "apt-cache policy jq | head -n 3",
              "dpkg -S /usr/bin/jq", "apt-get install -y figlet 2>&1 | tail -n 3", "figlet hi"], group="d07x")
S("d07.args", [{"cmd": "printf '#!/usr/bin/env bash\\necho \"script name: $0\"\\necho \"first arg:   $1\"\\necho \"arg count:   $#\"\\nfor arg in \"$@\"; do\\n  echo \"- $arg\"\\ndone\\n' > args.sh", "hide": True},
               "cat args.sh", "chmod +x args.sh", "./args.sh deploy \"eu west\" 3", "./args.sh"], group="d07x")
S("d07.flow", ["for f in logs/*.log; do echo \"$f: $(grep -c ERROR \"$f\")\"; done",
               "n=0; while IFS= read -r line; do n=$((n + 1)); done < app.log; echo \"$n lines\"",
               "if [[ -f app.log ]]; then echo 'app.log exists'; else echo 'no app.log'; fi",
               "[[ -d logs ]] && echo 'logs is a folder'", "test -f nosuch.log; echo $?", "[[ 10 -gt 9 ]] && echo 'numbers compare as numbers'",
               "[[ \"abc\" == a* ]] && echo 'starts with a'"], group="d07x")
S("d07.strict", ["bash -c 'cat nope.txt | sort; echo \"exit=$?\"'", "bash -c 'set -o pipefail; cat nope.txt | sort; echo \"exit=$?\"'",
                 "bash -c 'set -u; echo \"deploying to $DEPLOY_DIR\"'", "bash -c 'set -e; grep -q FATAL app.log; echo \"never printed\"'",
                 "echo $?", "bash -c 'set -e; grep -q FATAL app.log || true; echo \"still running\"'",
                 "DIR=\"\"; echo rm -rf \"$DIR/\"*", "bash -c 'echo rm -rf \"${DIR:?DIR is not set}/\"'"], group="d07x")
S("d07.trap", [{"cmd": heredoc("trapdemo.sh"), "hide": True}, "bash trapdemo.sh", "echo $?"], group="d07x")
S("d07.lint", [{"cmd": heredoc("bad.sh"), "hide": True}, "cat bad.sh", "shellcheck bad.sh", "echo $?"], group="d07x")
S("d07.keygen", [{"cmd": "apt-get install -y -qq openssh-client > /dev/null 2>&1", "hide": True, "timeout": 120},
                 "ssh-keygen -t ed25519 -C \"you@example.com\" -f ~/.ssh/id_ed25519 -N \"\"",
                 "ls -l ~/.ssh", "cut -c 1-60 ~/.ssh/id_ed25519.pub"], group="d07x")
SSHD_SETUP = ("docker network create v2p1-net >/dev/null 2>&1; docker rm -f v2p1-devbox >/dev/null 2>&1; "
              "docker run -d --name v2p1-devbox --hostname devbox --network v2p1-net --network-alias devbox v2p1-lab:24.04 "
              "bash -c 'apt-get install -y -qq openssh-server rsync >/dev/null 2>&1; useradd -m -s /bin/bash ubuntu; "
              "mkdir -p /home/ubuntu/.ssh /run/sshd; touch /home/ubuntu/.ssh/authorized_keys; chown -R ubuntu:ubuntu /home/ubuntu/.ssh; "
              "chmod 700 /home/ubuntu/.ssh; touch /ready; exec /usr/sbin/sshd -D'; "
              "until docker exec v2p1-devbox test -f /ready; do sleep 1; done; sleep 2")
S("d07.ssh", [{"cmd": "apt-get install -y -qq openssh-client rsync > /dev/null 2>&1; mkdir -p /keys", "hide": True, "timeout": 120},
              {"cmd": "ssh-keygen -q -t ed25519 -C you@example.com -f ~/.ssh/id_ed25519 -N '' && cp ~/.ssh/id_ed25519.pub /keys/", "hide": True},
              {"host": "docker cp v2p1-cap-d07-ssh:/keys/id_ed25519.pub /tmp/claude-0/v2p1-key.pub && docker cp /tmp/claude-0/v2p1-key.pub v2p1-devbox:/home/ubuntu/.ssh/authorized_keys && docker exec v2p1-devbox chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys && rm -f /tmp/claude-0/v2p1-key.pub"},
              {"cmd": "ssh ubuntu@devbox 'whoami; hostname'", "keys": [(3, "yes\n", "yes")]},
              "ssh ubuntu@devbox 'whoami; hostname'", "---",
              {"cmd": "printf 'Host devbox\\n    HostName devbox\\n    User ubuntu\\n    IdentityFile ~/.ssh/id_ed25519\\n' > ~/.ssh/config", "hide": True},
              "ssh devbox uptime", "scp app.log devbox:/tmp/", "ssh devbox 'ls -l /tmp/app.log'", "---",
              "rsync -av logs/ devbox:/tmp/logs/", "rsync -av logs/ devbox:/tmp/logs/"],
  group="d07s", docker=["--network", "v2p1-net"], host_before=[SSHD_SETUP],
  host_after=["docker rm -f v2p1-devbox >/dev/null 2>&1; docker network rm v2p1-net >/dev/null 2>&1"])
HELLO_UP = "docker rm -f v2p1-hello >/dev/null 2>&1; docker run -d --name v2p1-hello hello-devops:1.0.0 >/dev/null; sleep 4"
HELLO_REDIS = "docker rm -f v2p1-hello >/dev/null 2>&1; docker run -d --name v2p1-hello -e REDIS_HOST=127.0.0.1 hello-devops:1.0.0 >/dev/null; sleep 4"
HELLO_DOWN = "docker rm -f v2p1-hello >/dev/null 2>&1"
S("d07.w1", [{"cmd": heredoc("healthcheck.sh"), "hide": True}, "chmod +x healthcheck.sh", "shellcheck healthcheck.sh", "echo $?",
             "bash -n healthcheck.sh && echo 'syntax OK'"], group="d07w")
S("d07.w2", [{"cmd": heredoc("healthcheck.sh"), "hide": True}, {"cmd": "chmod +x healthcheck.sh", "hide": True},
             "curl -s localhost:8000/healthz", "echo $?", "RETRIES=3 DELAY=1 ./healthcheck.sh", "echo $?"], group="d07w")
S("d07.w3", [{"cmd": heredoc("healthcheck.sh"), "hide": True}, {"cmd": "chmod +x healthcheck.sh", "hide": True},
             "curl -s localhost:8000/healthz", "./healthcheck.sh", "echo $?", "./healthcheck.sh 2> /dev/null && echo 'smoke test passed: carry on with the deploy'", "---",
             "./healthcheck.sh http://localhost:8000 extra", "echo $?"],
  group="d07w", docker=["--network", "container:v2p1-hello"], host_before=[HELLO_UP], host_after=[HELLO_DOWN])
S("d07.w4", [{"cmd": heredoc("healthcheck.sh"), "hide": True}, {"cmd": "chmod +x healthcheck.sh", "hide": True},
             "curl -s localhost:8000/readyz", "RETRIES=3 DELAY=1 ./healthcheck.sh", "echo $?"],
  group="d07w", docker=["--network", "container:v2p1-hello"], host_before=[HELLO_REDIS], host_after=[HELLO_DOWN])

S("d04.tailhelp", ["tail --help | grep -E -- '^ +-(f|F)'"], group="d04x")
S("d05.deep", ["jq -s 'length' events.jsonl", "jq -s '[.[] | select(.event == \"order.created\") | .amount] | add' events.jsonl",
               "jq -r -s 'group_by(.service)[] | \"\\(.[0].service) \\(length)\"' events.jsonl",
               "jq -r '[.ts, .service, .level] | @tsv' events.jsonl | head -n 3",
               "jq -r 'select(.duration_ms > 1000) | \"\\(.duration_ms) \\(.service) \\(.event)\"' events.jsonl | sort -rn"], group="d05x")
S("d07.profile", ["grep -n -A 3 'BASH_VERSION' /etc/skel/.profile"], group="d07x")
