from cap import run, show, save, load, tty, mapped
import re
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d12"
M = {"localhost:18510": "localhost:5001", "mirror.gcr.io/library/python": "docker.io/library/python", "docker:default": "docker:desktop-linux"}
S = load("d12")
c = "docker buildx build --platform linux/amd64,linux/arm64 -t localhost:18510/hello:multi --push multi"
raw = tty("docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t localhost:18510/hello:multi --push multi", cwd=D)
S["multi_build_raw"] = raw
c2 = "docker buildx imagetools inspect localhost:18510/hello:multi"; S["multi_inspect"] = show(c2, run(c2), M)
c3 = "docker buildx imagetools inspect --raw localhost:18510/hello:multi"; S["multi_raw"] = show(c3, run(c3), M)
c4 = "docker buildx imagetools inspect mirror.gcr.io/library/python:3.14-slim"; S["py_inspect"] = show(c4.replace("mirror.gcr.io/library/",""), run(c4), M)
c5 = "docker buildx imagetools inspect --raw mirror.gcr.io/library/python:3.14-slim | jq -r '.manifests[] | .platform.os + \"/\" + .platform.architecture + \" \" + (.platform.variant // \"\")'"
S["py_platforms"] = show(c5.replace("mirror.gcr.io/library/",""), run(c5), M)
c6 = "docker buildx imagetools inspect --raw mirror.gcr.io/library/python:3.14-slim | jq '.manifests[0]'"
S["py_m0"] = show(c6.replace("mirror.gcr.io/library/",""), run(c6), M)
run("docker pull -q localhost:18510/hello:multi")
c7 = "docker image ls --tree localhost:18510/hello"; S["tree"] = show(c7, run(c7), M)
save("d12", S)
print(raw); 
for k in ["multi_inspect","multi_raw","py_inspect","py_platforms","py_m0","tree"]: print("==",k); print(S[k][:3000])
