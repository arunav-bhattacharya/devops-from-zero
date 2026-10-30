from cap import run, show, save
M = {"v2p3-web": "web", "v2p3-cache": "cache", "v2p3-life": "life", "v2p3-oops": "oops", "18501": "8080", "18502": "8081"}
S = {}
run("docker rm -f v2p3-web v2p3-life v2p3-oops v2p3-cache >/dev/null 2>&1")
c = "docker run -d --name v2p3-web -p 18501:80 nginx"; S["run"] = show(c, run(c), M)
import time; time.sleep(1)
c = "docker ps"; S["ps"] = show(c, run("docker ps --filter name=v2p3-web"), M, tables=True)
c = "curl -s localhost:18501 | grep title"; S["curl"] = show(c, run(c), M)
c = "docker logs v2p3-web | tail -1"; S["logs"] = show(c, run(c), M)
c = "docker exec v2p3-web cat /etc/os-release | head -2"; S["osrel"] = show(c, run(c), M)
c = "docker exec v2p3-web ls /usr/share/nginx/html"; S["ls"] = show(c, run(c), M)
c = "docker exec v2p3-web ps"; S["ps_in"] = show(c, run(c), M)
c = "docker top v2p3-web"; S["top"] = show(c, run(c), M)
c = "docker stop v2p3-web"; S["stop"] = show(c, run(c), M)
c = "docker ps -a"; S["psa"] = show(c, run("docker ps -a --filter name=v2p3-web"), M, tables=True)
c = "docker start v2p3-web"; S["start"] = show(c, run(c), M)
c = "docker rm -f v2p3-web"; S["rmf"] = show(c, run(c), M)
# lifecycle with create
c = "docker create --name v2p3-life alpine sleep 300"; S["create"] = show(c, run(c), M)
c = "docker inspect -f '{{.State.Status}}' v2p3-life"; S["st1"] = show(c, run(c), M)
run("docker start v2p3-life"); S["st2"] = show(c, run(c), M)
run("docker pause v2p3-life"); S["st3"] = show(c, run(c), M)
run("docker unpause v2p3-life"); 
t=time.time(); run("docker stop v2p3-life"); S["stoptime"] = time.time()-t
S["st4"] = show(c, run(c), M)
c = "docker inspect -f '{{.State.ExitCode}}' v2p3-life"; S["exit_life"] = show(c, run(c), M)
run("docker rm v2p3-life")
# exit codes
c = "docker run --name v2p3-oops alpine sh -c 'echo working; exit 3'"; S["oops"] = show(c, run(c), M)
c = "docker ps -a --filter name=oops"; S["oops_ps"] = show(c, run("docker ps -a --filter name=v2p3-oops"), M, tables=True)
c = "docker logs v2p3-oops"; S["oops_logs"] = show(c, run(c), M)
run("docker rm v2p3-oops")
# namespaces
c = "docker run --rm alpine ps"; S["ns_ps"] = show(c, run(c), M)
c = "docker run --rm alpine hostname"; S["ns_host"] = show(c, run(c), M)
c = "docker run --rm alpine ip -brief addr"; S["ns_ip"] = show(c, run(c), M)
c = "docker run --rm -e NAME=Ana alpine sh -c 'echo \"Hi $NAME\"'"; S["env"] = show(c, run(c), M)
c = "docker run --rm alpine uname -m"; S["uname"] = show(c, run(c), M)
c = "docker run --rm alpine cat /etc/alpine-release"; S["alprel"] = show(c, run(c), M)
c = "docker version --format '{{.Server.Os}}/{{.Server.Arch}}'"; S["ver"] = show(c, run(c), M)
save("d11", S)
for k,v in S.items(): print("==", k); print(v)
