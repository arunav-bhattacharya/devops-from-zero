from cap import run, show, save, load
import re
M = {"localhost:18510": "localhost:5001"}
S = load("d12")
d1 = re.search(r"digest: (sha256:[0-9a-f]+)", S["v1_push"]).group(1)
run("docker rmi localhost:18510/hello:1.0 localhost:18510/hello@" + d1 + " >/dev/null 2>&1")
c = f"docker run --rm localhost:18510/hello@{d1}"; S["by_digest"] = show(c, run(c), M)
c = "docker run --rm localhost:18510/hello:1.0"; S["by_tag"] = show(c, run(c), M)
save("d12", S); print(S["by_digest"]); print(S["by_tag"])
