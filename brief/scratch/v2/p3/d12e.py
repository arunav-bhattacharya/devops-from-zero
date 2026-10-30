from cap import run, show, save, load
import time, json
D = "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/v2p3/d12"
M = {"localhost:18510": "localhost:5001"}
S = load("d12")
run("docker rm -fv v2p3-registry >/dev/null 2>&1")
run("docker run -d --rm --name v2p3-registry -p 127.0.0.1:18510:5000 mirror.gcr.io/library/registry:3"); time.sleep(2)
run("docker buildx build --platform linux/amd64,linux/arm64 -t localhost:18510/hello:multi --push multi", cwd=D)
A = "Accept: application/vnd.oci.image.index.v1+json"
c = f"curl -s -H '{A}' localhost:18510/v2/hello/manifests/multi | jq -r '.manifests[] | .platform.architecture + \"  \" + .digest'"
S["api_index"] = show(c, run(c), M)
dig = run(f"curl -s -H '{A}' localhost:18510/v2/hello/manifests/multi | jq -r '.manifests[] | select(.platform.architecture==\"arm64\") | .digest'")
c = f"curl -s -H 'Accept: application/vnd.oci.image.manifest.v1+json' localhost:18510/v2/hello/manifests/{dig} | jq '{{config: .config.digest, layers: [.layers[].digest]}}'"
S["api_manifest"] = show(c.replace(dig, dig[:19] + "..."), run(c), M)
S["api_manifest_cmd_full"] = c
cfg = json.loads(run(c))["config"]
c = f"curl -s localhost:18510/v2/hello/blobs/{cfg} | jq '{{architecture, os, cmd: .config.Cmd, layers: .rootfs.diff_ids | length}}'"
S["api_config"] = show(c.replace(cfg, cfg[:19] + "..."), run(c), M)
run("docker rm -f v2p3-registry")
save("d12", S)
for k in ["api_index","api_manifest","api_config"]: print("==",k); print(S[k])
