"""Check docs.docker.com URLs against the docker/docs source tree (sparse clone).
CLI pages come from data/cli/*.yaml; /reference/dockerfile and build-checks are
mounted from BuildKit; Compose CLI pages from docker/compose (checked by curl)."""
import json, pathlib, re, subprocess, sys
DD = pathlib.Path("/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/dockerdocs")
def exists(url):
    p = url.split("docs.docker.com", 1)[1].strip("/")
    if p.startswith("reference/cli/docker/"):
        parts = p[len("reference/cli/docker/"):].split("/")
        name = "docker_" + "_".join(parts)
        if parts[0] == "compose":
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"https://raw.githubusercontent.com/docker/compose/main/docs/reference/{name}.yaml"], capture_output=True, text=True)
            return r.stdout == "200"
        return any((DD / "data/cli" / d / f"{name}.yaml").exists() for d in ("engine", "buildx", "init", "debug"))
    if p in ("reference/dockerfile",) or p.startswith("reference/build-checks/"):
        return True  # BuildKit mount (see hugo.yaml)
    for base in ("content/manuals", "content"):
        if (DD / base / p / "_index.md").exists() or (DD / base / (p + ".md")).exists():
            return True
    # aliases in front matter
    r = subprocess.run(["grep", "-rlE", f"^\\s*-\\s*/{re.escape(p)}/?$", str(DD / "content")], capture_output=True, text=True)
    return bool(r.stdout.strip())
if __name__ == "__main__":
    if len(sys.argv) > 1:
        blob = pathlib.Path(sys.argv[1]).read_text()
        urls = sorted(set(re.findall(r"https://docs\.docker\.com[^\s\")\]]*", blob)))
    else:
        from common import L
        urls = sorted({v[1] for v in L.values() if "docs.docker.com" in v[1]})
    bad = [u for u in urls if not exists(u)]
    print(f"{len(urls)} docker docs URLs, {len(bad)} not found")
    for u in bad: print("  MISSING", u)
