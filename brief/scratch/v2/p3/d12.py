from cap import run, show, save, tty
import time
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d12"
M = {"v2p3-cow": "cow", "v2p3-bloat": "bloat", "v2p3-lean": "lean", "v2p3-one": "one", "v2p3-two": "two",
     "docker:default": "docker:desktop-linux", "mirror.gcr.io/library/": ""}
S = {}
run("docker rm -f v2p3-cow >/dev/null 2>&1")
c = "docker image inspect python:3.14-slim --format '{{.Os}}/{{.Architecture}}'"; S["osarch"] = show(c, run(c), M)
c = "docker image inspect python:3.14-slim --format '{{json .RootFS.Layers}}' | jq ."; S["layers"] = show(c, run(c), M)
c = "docker image inspect python:3.14-slim --format '{{.Id}}'"; S["id"] = show(c, run(c), M)
c = "docker history python:3.14-slim"; S["hist_py"] = show(c, run(c), M, tables=True)
# copy on write
c = "docker run -d --name v2p3-cow nginx"; S["cow_run"] = show(c, run(c), M); time.sleep(1)
c = "docker exec v2p3-cow sh -c 'echo \"# my edit\" >> /etc/nginx/nginx.conf; touch /tmp/notes.txt; rm /usr/share/nginx/html/50x.html'"; S["cow_exec"] = show(c, run(c), M)
c = "docker diff v2p3-cow"; S["cow_diff"] = show(c, run(c), M)
c = "docker ps --size --filter name=v2p3-cow --format 'table {{.Names}}\t{{.Size}}'"; S["cow_size"] = show(c, run(c), M, tables=True)
c = "docker run --rm nginx tail -1 /etc/nginx/nginx.conf"; S["cow_fresh"] = show(c, run(c), M)
run("docker rm -f v2p3-cow")
# bloat vs lean
S["bloat_build"] = "$ docker build -t bloat:1.0 bloat\n" + "\n".join(x for x in map(lambda s: s.replace("docker:default","docker:desktop-linux").replace("v2p3-",""), [tty("docker build --no-cache -t v2p3-bloat:1.0 bloat", cwd=D)]))
c = "docker history v2p3-bloat:1.0"; S["bloat_hist"] = show(c, run(c), M, tables=True)
run("docker build -q -t v2p3-lean:1.0 lean", cwd=D)
c = "docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}' | grep -E 'REPOSITORY|v2p3-bloat|v2p3-lean|^alpine:3.22'"
S["bloat_sizes"] = show(c.replace("v2p3-",""), run(c), M, tables=True)
c = "docker image ls alpine:3.22"; S["ls_alpine"] = show(c, run(c), M, tables=True)
# sharing
run("docker build -q -t v2p3-one:1.0 one", cwd=D); run("docker build -q -t v2p3-two:1.0 two", cwd=D)
c = "docker image inspect v2p3-one:1.0 --format '{{json .RootFS.Layers}}' | jq -r '.[]' | cut -c1-19"; S["one_layers"] = show(c, run(c), M)
c = "docker image inspect v2p3-two:1.0 --format '{{json .RootFS.Layers}}' | jq -r '.[]' | cut -c1-19"; S["two_layers"] = show(c, run(c), M)
c = "docker system df -v | sed -n '/^Images space usage/,/^$/p' | grep -E 'REPOSITORY|v2p3-one|v2p3-two|python  *3.14-slim'"; S["df"] = show(c, run(c), M)
save("d12", S)
for k,v in S.items(): print("==",k); print(v)
