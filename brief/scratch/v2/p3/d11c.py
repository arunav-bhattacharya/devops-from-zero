from cap import run, show, save, load
M = {"v2p3-life": "life"}
S = load("d11")
run("docker rm -f v2p3-life >/dev/null 2>&1")
out = []
for c in ["docker create --name v2p3-life alpine sleep 300",
          "docker inspect -f '{{.State.Status}}' v2p3-life",
          "docker start v2p3-life",
          "docker pause v2p3-life",
          "docker inspect -f '{{.State.Status}}' v2p3-life",
          "docker unpause v2p3-life",
          "time docker stop v2p3-life",
          "docker inspect -f '{{.State.Status}} {{.State.ExitCode}}' v2p3-life"]:
    out.append(show(c, run(c), M))
run("docker rm v2p3-life")
S["lifecycle"] = "\n".join(out)
save("d11", S); print(S["lifecycle"])
