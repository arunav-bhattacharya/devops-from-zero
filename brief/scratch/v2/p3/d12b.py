from cap import run, show, save, load, tty, retable, mapped
import re
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d12"
DIVE = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/dl-dive/dive"
M = {"v2p3-registry": "registry", "localhost:18510": "localhost:5001", "127.0.0.1:18510": "127.0.0.1:5001",
     "v2p3-bloat": "bloat", "v2p3-lean": "lean", "v2p3-one": "one", "v2p3-two": "two",
     "mirror.gcr.io/library/registry:3": "registry:3", "docker:default": "docker:desktop-linux"}
S = load("d12")
def keepw(text):
    """Map names in BuildKit tty lines, keeping the time column aligned."""
    out = []
    for ln in text.split("\n"):
        new = mapped(ln, M)
        m = re.match(r"(.*?)(\s+)(\d+\.\d+s)$", ln)
        if m and new != ln:
            body = mapped(m.group(1), M)
            new = body.ljust(len(ln) - len(m.group(3))) + m.group(3)
        if ln.startswith("[+] Building") and new != ln:
            new = mapped(ln.replace("docker:default", ""), M).rstrip()
            new = new.ljust(len(ln) - len("docker:desktop-linux")) + "docker:desktop-linux"
        out.append(new)
    return "\n".join(out)
nocol = lambda s: re.sub(r"\x1b\[[0-9;]*m", "", s)
S["keepw_src"] = "ok"
S["bloat_build"] = "$ docker build -t bloat:1.0 bloat\n" + keepw(tty("docker build --no-cache -t v2p3-bloat:1.0 bloat", cwd=D))
c = "docker history v2p3-bloat:1.0"; S["bloat_hist"] = show(c, run(c), M, tables=True)
c = "docker image ls --filter reference=v2p3-bloat --filter reference=v2p3-lean"
S["bloat_ls"] = show(c, run(c), M, tables=True, right=("DISK USAGE", "CONTENT SIZE"))
c = "docker system df -v | grep -E '^(REPOSITORY|v2p3-one|v2p3-two|python) '"
S["df"] = show(c, run(c), M, tables=True)
c = f"CI=true {DIVE} v2p3-bloat:1.0"; S["dive_bloat"] = show("CI=true dive v2p3-bloat:1.0", nocol(run(c)), M)
c = f"CI=true {DIVE} v2p3-lean:1.0"; S["dive_lean"] = show("CI=true dive v2p3-lean:1.0", nocol(run(c)), M)
# registry: tags move, digests stay
run("docker rm -f v2p3-registry; docker rmi localhost:18510/hello:1.0 localhost:18510/hello:multi >/dev/null 2>&1")
c = "docker run -d --name v2p3-registry -p 127.0.0.1:18510:5000 mirror.gcr.io/library/registry:3"; S["reg_run"] = show(c, run(c), M)
import time; time.sleep(2)
c = "docker build -q -t localhost:18510/hello:1.0 v1"; S["v1_build"] = show(c, run(c, cwd=D), M)
c = "docker push localhost:18510/hello:1.0"; S["v1_push"] = show(c, run(c), M)
c = "docker run --rm localhost:18510/hello:1.0"; S["v1_run"] = show(c, run(c), M)
c = "docker build -q -t localhost:18510/hello:1.0 v2"; S["v2_build"] = show(c, run(c, cwd=D), M)
c = "docker push localhost:18510/hello:1.0"; S["v2_push"] = show(c, run(c), M)
d1 = re.search(r"digest: (sha256:[0-9a-f]+)", S["v1_push"]).group(1)
c = "docker rmi localhost:18510/hello:1.0"; S["rmi"] = show(c, run(c), M)
c = f"docker run --rm localhost:18510/hello@{d1}"; S["by_digest"] = show(c, run(c), M)
c = "docker run --rm localhost:18510/hello:1.0"; S["by_tag"] = show(c, run(c), M)
c = "docker images --digests localhost:18510/hello"; S["digests"] = show(c, run(c), M, tables=True)
c = "curl -s localhost:18510/v2/hello/tags/list"; S["tags_list"] = show(c, run(c), M)
save("d12", S)
for k in ["bloat_build","bloat_hist","bloat_ls","df","dive_bloat","dive_lean","reg_run","v1_build","v1_push","v1_run","v2_build","v2_push","rmi","by_digest","by_tag","digests","tags_list"]:
    print("==",k); print(S[k])
