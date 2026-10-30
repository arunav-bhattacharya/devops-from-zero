#!/usr/bin/env python3
"""Run every console example of Part 1 for real and save the transcripts.

Each snippet runs in a fresh `docker run -it --rm ... ubuntu:24.04 bash` session (the image
v2p1-lab:24.04 is ubuntu:24.04 plus the packages start-lab.sh installs), with a fresh copy of
labs/linux mounted at /work, typed through a pseudo-terminal like a person would.

Usage: python3 capture.py [snippet-prefix ...]     (default: all)
Writes outputs.json next to this file. build_p1.py reads it.
"""
import fcntl
import json
import os
import pathlib
import pty
import re
import select
import shutil
import struct
import subprocess
import sys
import termios
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = ROOT / "labs/linux"
WORK = pathlib.Path(os.environ.get("CAPWORK", "/tmp/claude-0/-home-user/5a31be1b-d2d7-5096-8c55-314d3e3b0058/scratchpad/capwork"))
OUT = HERE / "outputs.json"
IMAGE = "v2p1-lab:24.04"
TOKEN = "__P1PROMPT__"
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07|\x1b[()][AB0-2]|\x1b[=>]")


class Session:
    def __init__(self, argv, cols=80, rows=40):
        pid, fd = pty.fork()
        if pid == 0:
            fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
            os.execvp(argv[0], argv)
        self.pid, self.fd = pid, fd

    def read_until(self, token, timeout):
        buf = ""
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.fd], [], [], 0.1)
            if r:
                try:
                    data = os.read(self.fd, 65536).decode("utf-8", "replace")
                except OSError:
                    break
                if not data:
                    break
                buf += data
                if token and token in buf:
                    return buf, True
        return buf, False

    def send(self, s):
        os.write(self.fd, s.encode())

    def close(self):
        try:
            self.send("exit\n")
            time.sleep(0.3)
            os.close(self.fd)
        except OSError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass


def clean(text):
    text = ANSI.sub("", text).replace("\r\n", "\n").replace("\r", "")
    return "\n".join(line.rstrip() for line in text.split("\n"))


def run_snippet(name, spec, workdir):
    """spec: {"steps": [...], "docker": [...extra args], "image": str, "cwd": "/work"}
    A step is a string (a command) or a dict:
      {"cmd": str, "hide": bool, "timeout": s, "wait": s, "keys": [(delay, key, shown)]}"""
    for hc in spec.get("host_before", []):
        subprocess.run(hc, shell=True, capture_output=True)
    cname = "v2p1-cap-" + re.sub(r"[^a-z0-9]", "-", name.lower())
    subprocess.run(["docker", "rm", "-f", cname], capture_output=True)
    argv = ["docker", "run", "-it", "--rm", "--name", cname, "-v", f"{workdir}:/work", "-w", spec.get("cwd", "/work")]
    argv += spec.get("docker", []) + [spec.get("image", IMAGE), "bash"]
    s = Session(argv)
    s.read_until(spec.get("ready", "# "), 30)
    time.sleep(0.3)
    s.send("set +o emacs +o vi; stty -echo; PS2=''; PS1='__P1''PROMPT__'\n")
    s.read_until(TOKEN, 10)
    out = []
    for step in spec["steps"]:
        if step == "---":
            out.append("<<SPLIT>>")
            continue
        if isinstance(step, str):
            step = {"cmd": step}
        if "host" in step:
            subprocess.run(step["host"], shell=True, capture_output=True)
            continue
        cmd = step["cmd"]
        s.send(cmd + "\n")
        pre = ""
        for delay, key, show in step.get("keys", []):
            got, _ = s.read_until(None, delay)
            pre += got + show
            s.send(key)
        buf, ok = s.read_until(TOKEN, step.get("timeout", 60))
        if not ok:
            print(f"  ! timeout in {name}: {cmd}", file=sys.stderr)
        body = clean(pre + buf.split(TOKEN)[0])
        shown = ""
        if step.get("hide"):
            continue
        shown_cmd = step.get("show", cmd)
        block = "$ " + shown_cmd.replace("\n", "\n> ") if shown_cmd else ""
        text = (shown + body) if shown else body
        if text.startswith("\n") and shown == "":
            text = text[1:]
        parts = [block] if block else []
        if text.strip("\n"):
            parts.append(text.rstrip("\n"))
        out.append("\n".join(parts))
    s.close()
    subprocess.run(["docker", "rm", "-f", cname], capture_output=True)
    for hc in spec.get("host_after", []):
        subprocess.run(hc, shell=True, capture_output=True)
    return "\n".join(x for x in out if x)


def fresh_copy(group):
    d = WORK / group
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(LAB, d, symlinks=True)
    return d


from snippets import SNIPPETS  # noqa: E402  (name -> spec, ordered; spec["group"] shares a lab copy)


def main():
    wanted = sys.argv[1:]
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    groups = {}
    for name, spec in SNIPPETS.items():
        if wanted and not any(name.startswith(w) for w in wanted):
            continue
        g = spec.get("group", name)
        if g not in groups:
            groups[g] = fresh_copy(g)
        print("running", name, file=sys.stderr)
        data[name] = run_snippet(name, spec, groups[g])
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    for d in groups.values():
        shutil.rmtree(d, ignore_errors=True)
    for name in data:
        if wanted and not any(name.startswith(w) for w in wanted):
            continue
        print(f"===== {name}\n{data[name]}\n")


if __name__ == "__main__":
    main()
