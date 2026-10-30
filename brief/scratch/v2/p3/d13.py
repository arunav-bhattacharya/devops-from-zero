from cap import run, show, save, tty, ttymap
import re
REAL = "cd89c30eda26ee911a4611b18680086e0ea42e6f5f8cbe653d07fa7958c9cec8"
def fixbase(t):
    return re.sub(r"v2p3-pybase:3\.14-slim@sha256:([0-9a-f]+)", lambda m: "python:3.14-slim@sha256:" + REAL[:len(m.group(1)) + 5], t)
import time
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d13"
A = D + "/app"
PYD = "sha256:46abd81b64b5adfd51c5a7c58d3c38fa8c40feef16bae7e8b0df63719759a5bd"
M = {"docker.io/library/v2p3-pybase:3.14-slim@" + PYD: "docker.io/library/python:3.14-slim@sha256:cd89c30eda26ee911a4611b18680086e0ea42e6f5f8cbe653d07fa7958c9cec8", "v2p3-pybase:3.14-slim": "python:3.14-slim", "v2p3-hello-devops": "hello-devops", "v2p3-hello2": "hello2", "v2p3-hello": "hello", "v2p3-greeter": "greeter", "v2p3-argdemo": "argdemo", "v2p3-ctx": "ctx",
     "v2p3-shell": "shell", "v2p3-exec": "exec", "localhost:18520": "localhost:8000", "localhost:18521": "localhost:8001",
     "-p 18520:": "-p 8000:", "-p 18521:": "-p 8001:", "0.0.0.0:18520->": "0.0.0.0:8000->",
     "docker:default": "docker:desktop-linux", " --network host": ""}
S = {}
run("docker rm -f v2p3-hello v2p3-hello2 v2p3-shell v2p3-exec >/dev/null 2>&1")
run("sed -i 's#^FROM python:3.14-slim#FROM v2p3-pybase:3.14-slim#' Dockerfile", cwd=A)
cmd = "docker build --network host --no-cache --build-arg APP_VERSION=1.0.0 -t v2p3-hello-devops:1.0.0 ."
S["build1"] = "$ " + "docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n" + ttymap(fixbase(tty(cmd, cwd=A)), M)
c = "docker run -d --name v2p3-hello -p 18520:8000 v2p3-hello-devops:1.0.0"; S["run"] = show(c, run(c), M); time.sleep(3)
c = "curl -s localhost:18520"; S["curl1"] = show(c, run(c), M)
c = "curl -s localhost:18520/healthz"; S["curl2"] = show(c, run(c), M)
# cache: edit app.py
run("echo '# a comment to change the file' >> app.py", cwd=A)
cmd = "docker build --network host --build-arg APP_VERSION=1.0.0 -t v2p3-hello-devops:1.0.0 ."
S["build2"] = "$ docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n" + ttymap(fixbase(tty(cmd, cwd=A)), M)
run("sed -i '$ d' app.py", cwd=A)
c = "docker history v2p3-hello-devops:1.0.0 | head -9"; S["hist"] = show(c, run(c), M, tables=True)
c = "docker run -d --name v2p3-hello2 -p 18521:8000 -e GREETING=\"Hi from a second container\" v2p3-hello-devops:1.0.0"; S["run2"] = show(c, run(c), M); time.sleep(3)
c = "curl -s localhost:18521"; S["curl3"] = show(c, run(c), M)
c = "docker image inspect v2p3-hello-devops:1.0.0 --format '{{json .Config.Cmd}} {{.Config.WorkingDir}}'"; S["insp"] = show(c, run(c), M)
c = "docker run --rm -e GREETING=Hi v2p3-hello-devops:1.0.0 env | grep -E '^(APP_VERSION|GREETING|PYTHONUNBUFFERED)='"; S["insp_env"] = show(c, run(c), M)
c = "docker exec v2p3-hello cat /proc/1/cmdline | tr '\\0' ' '; echo"; S["pid1_exec"] = show(c, run(c), M)
c = "docker exec v2p3-hello whoami"; S["whoami"] = show(c, run(c), M)
run("docker rm -f v2p3-hello2")
# shell form
run("docker build -q -t v2p3-shell:1.0 shellform", cwd=D)
c = "docker run -d --name v2p3-shell v2p3-shell:1.0"; S["shell_run"] = show(c, run(c), M); time.sleep(3)
c = "docker exec v2p3-shell cat /proc/1/cmdline | tr '\\0' ' '; echo"; S["pid1_shell"] = show(c, run(c), M)
c = "time docker stop v2p3-shell"; S["stop_shell"] = show(c, run(c), M)
c = "time docker stop v2p3-hello"; S["stop_exec"] = show(c, run(c), M)
c = "docker ps -a --filter name=v2p3-shell --filter name=v2p3-hello --format 'table {{.Names}}\t{{.Status}}'"
S["stop_ps"] = show("docker ps -a --format 'table {{.Names}}\\t{{.Status}}'", run(c), M, tables=True)
# greeter
run("docker build -q -t v2p3-greeter:1.0 greeter", cwd=D)
for k, c in [("g1", "docker run --rm v2p3-greeter:1.0"), ("g2", "docker run --rm v2p3-greeter:1.0 Ana"),
             ("g3", "docker run --rm --entrypoint date v2p3-greeter:1.0 -u +%Y")]:
    S[k] = show(c, run(c), M)
# ARG demo
c = "docker build --progress=plain --no-cache --build-arg BUILD_NOTE=hello -t v2p3-argdemo:1.0 argdemo 2>&1 | grep 'at build time'"
S["arg_build"] = show(c, run(c, cwd=D), M)
c = "docker run --rm v2p3-argdemo:1.0"; S["arg_run"] = show(c, run(c), M)
c = "docker history v2p3-argdemo:1.0 | head -4"; S["arg_hist"] = show(c, run(c), M, tables=True)
c = "docker build --check check"; S["check"] = show(c, run(c, cwd=D), M)
c = "docker build --progress=plain -t v2p3-ctx:1.0 ctx 2>&1 | grep 'transferring context'"; S["ctx1"] = show(c, run(c, cwd=D), M)
run("echo .venv > ctx/.dockerignore", cwd=D)
c = "docker build --progress=plain -t v2p3-ctx:1.0 ctx 2>&1 | grep 'transferring context'"; S["ctx2"] = show(c, run(c, cwd=D), M)
save("d13", S)
for k,v in S.items(): print("==",k); print(v)
