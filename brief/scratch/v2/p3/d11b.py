from cap import run, show, save, load
import time
M = {"v2p3-web": "web", "v2p3-capped": "capped", "18501": "8080", "mirror.gcr.io/library/": ""}
S = load("d11")
run("docker rm -f v2p3-web v2p3-capped >/dev/null 2>&1")
run("docker run -d --name v2p3-web -p 18501:80 nginx"); time.sleep(1); run("curl -s localhost:18501 >/dev/null")
c = "docker logs --tail 1 v2p3-web"; S["logs"] = show(c, run(c), M)
run("docker rm -f v2p3-web")
c = "docker run --rm alpine ip addr"; S["ns_ip"] = show(c, run(c), M)
c = "docker run -d --name v2p3-capped -m 64m redis:8-alpine"; S["capped"] = show(c, run(c), M)
time.sleep(2)
c = "docker stats --no-stream v2p3-capped"; S["stats"] = show(c, run(c), M, tables=True)
run("docker rm -f v2p3-capped")
save("d11", S)
for k in ["logs","ns_ip","capped","stats"]: print("==",k); print(S[k])
