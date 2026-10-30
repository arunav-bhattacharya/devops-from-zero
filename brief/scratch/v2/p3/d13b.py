from cap import run, save, load, tty, ttymap
import re
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d13/app"
REAL = "cd89c30eda26ee911a4611b18680086e0ea42e6f5f8cbe653d07fa7958c9cec8"
fixbase = lambda t: re.sub(r"v2p3-pybase:3\.14-slim@sha256:([0-9a-f]+)", lambda m: "python:3.14-slim@sha256:" + REAL[:len(m.group(1)) + 5], t)
M = {"v2p3-pybase:3.14-slim": "python:3.14-slim", "v2p3-hello-devops": "hello-devops", "docker:default": "docker:desktop-linux"}
S = load("d13")
cmd = "docker build --network host --build-arg APP_VERSION=1.0.0 -t v2p3-hello-devops:1.0.0 ."
tty(cmd, cwd=D)  # make sure the clean app.py is built
run("echo '# edited to test the build cache' >> app.py", cwd=D)
S["build2"] = "$ docker build --build-arg APP_VERSION=1.0.0 -t hello-devops:1.0.0 .\n" + ttymap(fixbase(tty(cmd, cwd=D)), M)
run("sed -i '$ d' app.py", cwd=D)
save("d13", S); print(S["build2"])
