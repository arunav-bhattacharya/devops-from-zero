from cap import run, show, save
import time, re, json
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d14"
M = {"v2p3-site": "site", "v2p3-demo": "demo", "v2p3-web": "web", "v2p3-notes": "notes", "v2p3-r": "anon",
     "v2p3-tmp": "scratch", "v2p3-a": "a", "v2p3-b": "b", "v2p3-n": "pub", D: "~/code/docker-play",
     "127.0.0.1:18531": "127.0.0.1:8080", "-p 127.0.0.1:18531:80": "-p 127.0.0.1:8080:80"}
S = {}
run("docker rm -f v2p3-web v2p3-r v2p3-tmp v2p3-a v2p3-b v2p3-n >/dev/null 2>&1; docker network rm v2p3-demo >/dev/null 2>&1; docker volume rm v2p3-site v2p3-notes >/dev/null 2>&1")
# --- worked: nginx page in a volume, reached by name
c = "docker volume create v2p3-site"; S["w_vol"] = show(c, run(c), M)
c = "docker run --rm -v v2p3-site:/usr/share/nginx/html nginx ls /usr/share/nginx/html"; S["w_prepop"] = show(c, run(c + " 2>/dev/null"), M)
c = "docker run --rm -v v2p3-site:/html alpine sh -c 'echo \"<h1>Served from a volume</h1>\" > /html/index.html'"; S["w_write"] = show(c, run(c), M)
c = "docker network create v2p3-demo"; S["w_net"] = show(c, run(c), M)
c = "docker run -d --name v2p3-web --network v2p3-demo -v v2p3-site:/usr/share/nginx/html nginx"; S["w_web"] = show(c, run(c), M); time.sleep(1)
c = "docker run --rm alpine wget -qO- http://v2p3-web"; S["w_default"] = show(c, run(c), M)
c = "docker run --rm --network v2p3-demo alpine wget -qO- http://v2p3-web"; S["w_named"] = show(c, run(c), M)
c = "docker run --rm --network v2p3-demo alpine cat /etc/resolv.conf"; S["w_resolv"] = show(c, run(c), M)
c = "docker run --rm --network v2p3-demo alpine nslookup v2p3-web"; S["w_nslookup"] = show(c, run(c), M)
c = "docker rm -f v2p3-web"; S["w_rm"] = show(c, run(c), M)
c = "docker run -d --name v2p3-web --network v2p3-demo -v v2p3-site:/usr/share/nginx/html nginx"; S["w_web2"] = show(c, run(c), M); time.sleep(1)
c = "docker run --rm --network v2p3-demo alpine wget -qO- http://v2p3-web"; S["w_named2"] = show(c, run(c), M)
c = "docker network inspect v2p3-demo --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}'"; S["w_inspect"] = show(c, run(c), M)
c = "docker network inspect v2p3-demo --format '{{json .IPAM.Config}}'"; S["w_ipam"] = show(c, run(c), M)
c = "docker volume inspect v2p3-site"; S["w_volinspect"] = show(c, run(c), M)
# default bridge vs by-IP
run("docker run -d --name v2p3-a alpine sleep 600; docker run -d --name v2p3-b alpine sleep 600")
c = "docker exec v2p3-a ping -c 1 v2p3-b"; S["b_byname"] = show(c, run(c), M)
ipb = run("docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' v2p3-b")
c = "docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' v2p3-b"; S["b_ip"] = show(c, ipb, M)
c = f"docker exec v2p3-a ping -c 1 {ipb}"; S["b_byip"] = show(c, run(c), M)
c = "docker exec v2p3-a cat /etc/resolv.conf"; S["b_resolv"] = show(c, run(c), M)
c = "docker network connect v2p3-demo v2p3-a"; S["two_connect"] = show(c, run(c), M)
c = "docker exec v2p3-a ip -4 -o addr show"; S["two_ip"] = show(c, run(c), M)
c = "docker exec v2p3-a wget -qO- http://v2p3-web"; S["two_wget"] = show(c, run(c), M)
c = "docker exec v2p3-b wget -qO- -T 3 http://v2p3-web"; S["two_wget_b"] = show(c, run(c), M)
# none
c = "docker run --rm --network none alpine ip -o addr show"; S["none"] = show(c, run(c), M)
# publish vs expose
c = "docker image inspect nginx --format '{{json .Config.ExposedPorts}}'"; S["expose"] = show(c, run(c), M)
c = "docker run -d --name v2p3-n -p 127.0.0.1:18531:80 nginx"; S["pub"] = show(c, run(c), M)
c = "docker port v2p3-n"; S["port"] = show(c, run(c), M)
# volumes: notes, backup/restore
c = "docker run --rm -v v2p3-notes:/data alpine sh -c 'echo \"first note\" >> /data/notes.txt'"; S["n1"] = show(c, run(c), M)
c = "docker run --rm -v v2p3-notes:/data alpine sh -c 'echo \"second note\" >> /data/notes.txt; cat /data/notes.txt'"; S["n2"] = show(c, run(c), M)
c = "docker volume ls --filter name=v2p3-"; S["vls"] = show(c, run(c), M, tables=True)
c = f"docker run --rm -v v2p3-notes:/data -v \"{D}\":/backup alpine tar czf /backup/notes.tgz -C /data ."; S["backup"] = show(c.replace(f'"{D}"', '"$PWD"'), run(c), M)
c = f"ls -l {D}/notes.tgz"; S["backup_ls"] = show("ls -l notes.tgz", run(c), M)
c = f"docker run --rm -v v2p3-notes-copy:/data -v \"{D}\":/backup alpine sh -c 'tar xzf /backup/notes.tgz -C /data && cat /data/notes.txt'"; S["restore"] = show(c.replace(f'"{D}"', '"$PWD"'), run(c), M | {"v2p3-notes-copy": "notes-copy"})
run("docker volume rm v2p3-notes-copy")
# anonymous volume
c = "docker run -d --name v2p3-r -v /data alpine sleep 600"; S["anon_run"] = show(c, run(c), M)
c = "docker inspect -f '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}' v2p3-r"; out = run(c); S["anon_mounts"] = show(c, out, M)
anon = re.search(r"volume (\w+)", out).group(1)
c = "docker rm -f v2p3-r"; S["anon_rm"] = show(c, run(c), M)
c = f"docker volume ls --filter name={anon}"; S["anon_left"] = show("docker volume ls --filter dangling=true", run(c), M, tables=True)
run(f"docker volume rm {anon}")
# tmpfs
c = "docker run -d --name v2p3-tmp --tmpfs /scratch alpine sleep 600"; S["tmpfs_run"] = show(c, run(c), M)
c = "docker exec v2p3-tmp sh -c 'echo secret > /scratch/token; df -h /scratch'"; S["tmpfs_df"] = show(c, run(c), M)
run("docker restart -t 1 v2p3-tmp")
c = "docker restart v2p3-tmp && docker exec v2p3-tmp ls -A /scratch"; S["tmpfs_after"] = show(c, "v2p3-tmp\n" + run("docker exec v2p3-tmp ls -A /scratch"), M)
# bind mount ownership
run(f"rm -rf {D}/out; mkdir -p {D}/out")
c = f"docker run --rm -v \"{D}/out\":/out alpine touch /out/from-root.txt"; S["own1"] = show(c.replace(f'"{D}/out"', '"$PWD/out"'), run(c), M)
c = f"docker run --rm --user 10001 -v \"{D}/out\":/out alpine touch /out/from-10001.txt"; S["own2"] = show(c.replace(f'"{D}/out"', '"$PWD/out"'), run(c), M)
c = f"ls -ln {D}/out"; S["own_ls"] = show("ls -ln out", run(c), M)
save("d14", S)
for k,v in S.items(): print("==",k); print(v)
