from cap import run, show, save, tty, ttymap
import time, os
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d16"
DIVE = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/dl-dive/dive"
M = {"v2p3-hello-devops:simple": "hello-devops:simple", "v2p3-hello-devops:final": "hello-devops:1.0.0", "v2p3-web": "web",
     "v2p3-nosock": "nosock", "v2p3-leak": "leak", "v2p3-safe": "safe", "-p 18560:": "-p 8000:", "0.0.0.0:18560->": "0.0.0.0:8000->",
     "localhost:18560": "localhost:8000"}
S = {}
run("docker rm -f v2p3-web v2p3-nosock >/dev/null 2>&1")
for k, c in [("who_simple", "docker run --rm v2p3-hello-devops:simple whoami"), ("who_final", "docker run --rm v2p3-hello-devops:final id"),
             ("pip_gone", "docker run --rm v2p3-hello-devops:final pip --version"),
             ("pip_gone2", "docker run --rm v2p3-hello-devops:final python -m pip --version"),
             ("hist", "docker history v2p3-hello-devops:final | head -15")]:
    S[k] = show(c, run(c), M, tables=(k == "hist"))
S["ls"] = show("docker image ls --filter reference=python:3.14-slim --filter reference=hello-devops",
               run("docker image ls --filter reference=python:3.14-slim --filter reference=v2p3-hello-devops:final --filter reference=v2p3-hello-devops:simple"), M, tables=True, right=("DISK USAGE", "CONTENT SIZE"))
S["pyc_base"] = show("docker run --rm python:3.14-slim sh -c 'find /usr/local/lib/python3.14 -name \"*.pyc\" | wc -l'", run("docker run --rm python:3.14-slim sh -c 'find /usr/local/lib/python3.14 -name \"*.pyc\" | wc -l'"), M)
S["pyc_final"] = show("docker run --rm v2p3-hello-devops:final sh -c 'find /usr/local/lib/python3.14 -name \"*.pyc\" | wc -l'", run("docker run --rm v2p3-hello-devops:final sh -c 'find /usr/local/lib/python3.14 -name \"*.pyc\" | wc -l'"), M)
# control socket
c = "docker run -d --name v2p3-nosock v2p3-hello-devops:final gunicorn --bind 0.0.0.0:8000 app:app"
S["nosock_run"] = show(c, run(c), M); time.sleep(4)
S["nosock_logs"] = show("docker logs v2p3-nosock", run("docker logs v2p3-nosock"), M)
S["nosock_ps"] = show("docker ps -a --filter name=v2p3-nosock --format '{{.Status}}'", run("docker ps -a --filter name=v2p3-nosock --format '{{.Status}}'"), M)
run("docker rm -f v2p3-nosock")
# health
c = "docker run -d --name v2p3-web -p 18560:8000 v2p3-hello-devops:final"; S["h_run"] = show(c, run(c), M)
time.sleep(2)
S["h_ps1"] = show("docker ps --format 'table {{.Names}}\\t{{.Status}}'", run("docker ps --filter name=v2p3-web --format 'table {{.Names}}\\t{{.Status}}'"), M, tables=True)
for _ in range(40):
    if "healthy" in run("docker inspect -f '{{.State.Health.Status}}' v2p3-web") and "starting" not in run("docker inspect -f '{{.State.Health.Status}}' v2p3-web"):
        break
    time.sleep(2)
S["h_ps2"] = show("docker ps --format 'table {{.Names}}\\t{{.Status}}'", run("docker ps --filter name=v2p3-web --format 'table {{.Names}}\\t{{.Status}}'"), M, tables=True)
S["h_inspect"] = show("docker inspect -f '{{json .State.Health}}' v2p3-web | jq '{Status, FailingStreak, last: .Log[-1]}'", run("docker inspect -f '{{json .State.Health}}' v2p3-web | jq '{Status, FailingStreak, last: .Log[-1]}'"), M)
S["h_curl"] = show("curl -s localhost:18560", run("curl -s localhost:18560"), M)
S["h_top"] = show("docker exec v2p3-web ps -o user,pid,cmd", run("docker exec v2p3-web ps -o user,pid,cmd"), M)
run("docker rm -f v2p3-web")
# dive
S["dive_final"] = show("CI=true dive hello-devops:1.0.0", run(f"CI=true {DIVE} v2p3-hello-devops:final | sed 's/\\x1b\\[[0-9;]*m//g'"), M)
# secrets
c = "docker build -q --build-arg API_TOKEN=s3cr3t-demo-token -t v2p3-leak leak"; S["leak_build"] = show(c, run(c, cwd=D), M)
c = "docker history --no-trunc --format '{{.CreatedBy}}' v2p3-leak | grep -o 'API_TOKEN=[^ ]*'"; S["leak_hist"] = show(c, run(c), M)
env = dict(os.environ, API_TOKEN="s3cr3t-demo-token")
c = "docker build --progress=plain --secret id=api_token,env=API_TOKEN -t v2p3-safe safe 2>&1 | grep 'downloaded'"
S["safe_build"] = show("API_TOKEN=s3cr3t-demo-token " + c.replace(" 2>&1 | grep 'downloaded'", "") , run(c, cwd=D, env=env), M)
c = "docker history --no-trunc --format '{{.CreatedBy}}' v2p3-safe | grep -c s3cr3t"; S["safe_hist"] = show(c, run(c), M)
save("d16", S)
for k,v in S.items(): print("==",k); print(v)
