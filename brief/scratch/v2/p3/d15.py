from cap import run, show, save, ttyc, ttymap, retable
import os, time
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d15/hello-devops"
ENV = dict(os.environ, COMPOSE_PROJECT_NAME="v2p3-hello-devops")
M = {"v2p3-hello-devops": "hello-devops", "18540": "8000", "18541": "8080", D: "/Users/you/code/hello-devops"}
S = {}
def r(c): return run(c, cwd=D, env=ENV)
def sc(c): return "$ " + ttymap(c, M) + "\n" + ttymap(ttyc(c, cwd=D, env=ENV), M)
r("docker compose --profile proxy down -v --remove-orphans; rm -f .env")
S["config"] = show("docker compose config", r("docker compose config"), M)
S["up"] = sc("docker compose up -d")
time.sleep(1)
S["ps"] = show("docker compose ps", r("docker compose ps"), M, tables=True)
S["curl3"] = show("for i in 1 2 3; do curl -s localhost:18540; echo; done", r("for i in 1 2 3; do curl -s localhost:18540; echo; done"), M)
S["logs"] = show("docker compose logs web", r("docker compose logs web"), M)
S["exec"] = show("docker compose exec redis redis-cli GET visits", r("docker compose exec redis redis-cli GET visits"), M)
S["run"] = show("docker compose run --rm redis redis-cli -h redis ping", r("docker compose run --rm redis redis-cli -h redis ping"), M)
# restart policy
S["shutdown"] = show("docker compose exec redis redis-cli shutdown", r("docker compose exec redis redis-cli shutdown"), M)
time.sleep(4)
S["ps_after"] = show("docker compose ps redis", r("docker compose ps redis"), M, tables=True)
S["restarts"] = show("docker inspect -f '{{.RestartCount}}' v2p3-hello-devops-redis-1", r("docker inspect -f '{{.RestartCount}}' v2p3-hello-devops-redis-1"), M)
time.sleep(3)
S["curl_after_restart"] = show("curl -s localhost:18540", r("curl -s localhost:18540"), M)
# down / up keeps the volume
S["down"] = sc("docker compose down")
S["vol_after_down"] = show("docker volume ls --filter name=v2p3-hello-devops", r("docker volume ls --filter name=v2p3-hello-devops"), M, tables=True)
r("docker compose up -d"); time.sleep(3)
S["curl_after_down"] = show("curl -s localhost:18540", r("curl -s localhost:18540"), M)
# profiles
S["services_all"] = show("docker compose config --services", r("docker compose config --services"), M)
S["profiles"] = show("docker compose config --profiles", r("docker compose config --profiles"), M)
S["services_base"] = show("docker compose -f compose.yaml config --services", r("docker compose -f compose.yaml config --services"), M)
S["up_proxy"] = sc("docker compose --profile proxy up -d")
time.sleep(2)
S["curl_proxy"] = show("curl -s localhost:18541", r("curl -s localhost:18541"), M)
S["curl_proxy_head"] = show("curl -sI localhost:18541 | grep -i '^server'", r("curl -sI localhost:18541 | grep -i '^server'"), M)
S["ps_proxy"] = show("docker compose ps --format 'table {{.Service}}\\t{{.Status}}\\t{{.Ports}}'", r("docker compose ps --format 'table {{.Service}}\\t{{.Status}}\\t{{.Ports}}'"), M, tables=True)
S["down_noprofile"] = sc("docker compose down")
S["left"] = show("docker compose ps -a", r("docker compose ps -a"), M, tables=True)
S["down_profile"] = sc("docker compose --profile proxy down")
# .env interpolation
S["cfg_default"] = show("docker compose config | grep GREETING", r("docker compose config | grep GREETING"), M)
r("echo 'GREETING=Hi from .env' > .env")
S["cfg_env"] = show("docker compose config | grep GREETING", r("docker compose config | grep GREETING"), M)
S["cfg_shell"] = show("GREETING='Hi from my shell' docker compose config | grep GREETING", r("GREETING='Hi from my shell' docker compose config | grep GREETING"), M)
r("rm -f .env")
save("d15", S)
for k,v in S.items(): print("==",k); print(v)
