from cap import run, show, save, load, tty, ttymap
import re
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d16/app"
REAL = "cd89c30eda26ee911a4611b18680086e0ea42e6f5f8cbe653d07fa7958c9cec8"
fixbase = lambda t: re.sub(r"v2p3-pybase:3\.14-slim@sha256:([0-9a-f]+)", lambda m: "python:3.14-slim@sha256:" + REAL[:len(m.group(1)) + 5], t).replace("docker.io/library/v2p3-pybase:3.14-slim", "docker.io/library/python:3.14-slim")
M = {"v2p3-hello-devops:final": "hello-devops:1.0.0", "docker:default": "docker:desktop-linux"}
S = load("d16")
cmd = "docker build --network host --no-cache --build-arg APP_VERSION=1.0.0 -t v2p3-hello-devops:final ."
S["build_final"] = "$ docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n" + ttymap(fixbase(tty(cmd, cwd=D, cols=96)), M)
S["ls2"] = show("docker image ls --filter reference=python:3.14-slim --filter reference=hello-devops:1.0.0",
                run("docker image ls --filter reference=python:3.14-slim --filter reference=v2p3-hello-devops:final"), M, tables=True, right=("DISK USAGE", "CONTENT SIZE"))
save("d16", S); print(S["build_final"]); print(S["ls2"])
