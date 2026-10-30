#!/usr/bin/env python3
"""Run real Docker commands for Part 3 and save console transcripts.

Tests use unique names (v2p3-*) and ports (185xx) because other writers share
this Docker daemon. MAP turns them back into the learner-facing names and ports.
Docker prints tables padded to the widest cell, so after a rename we rebuild
those tables the way Docker's tabwriter does (min width 10, padding 3).

Usage from other scripts:
    from cap import run, show
    out = run("docker ps")             # runs it, returns raw output
    print(show(cmd, out, MAP))         # "$ cmd" + output, with names mapped
"""
import json
import pathlib
import re
import subprocess

OUT = pathlib.Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def run(cmd, cwd=None, timeout=600, env=None):
    p = subprocess.run(["bash", "-c", cmd], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=timeout, env=env)
    return p.stdout.rstrip("\n")


def mapped(s, mapping):
    for k in sorted(mapping, key=len, reverse=True):
        s = s.replace(k, mapping[k])
    return s


def _cols(header):
    """Start positions of columns in a Docker table header (2+ spaces apart)."""
    starts = [0]
    for m in re.finditer(r"\s{2,}(?=\S)", header):
        starts.append(m.end())
    return starts


def retable(block, mapping, right=()):
    """Re-render a Docker table after mapping names. `right` = column titles to right-align."""
    lines = block.split("\n")
    header = lines[0]
    starts = _cols(header)
    rows = []
    for ln in lines:
        cells = []
        for i, s in enumerate(starts):
            e = starts[i + 1] if i + 1 < len(starts) else None
            cells.append(ln[s:e].strip() if e else ln[s:].strip())
        rows.append([mapped(c, mapping) for c in cells])
    widths = [max(10, max(len(r[i]) for r in rows) + 3) for i in range(len(starts))]
    out = []
    for r in rows:
        parts = []
        for i, c in enumerate(r):
            last = i == len(r) - 1
            title = rows[0][i]
            if title in right and r is not rows[0]:
                hw = max(len(x[i]) for x in rows)
                c = c.rjust(hw)
            parts.append(c if last else c.ljust(widths[i]))
        out.append("".join(parts).rstrip())
    return "\n".join(out)


def show(cmd, output, mapping, tables=False, right=()):
    """A console block: '$ cmd' then output. tables=True re-renders a table output."""
    cmd = mapped(cmd, mapping)
    if tables and output.strip():
        output = retable(output, mapping, right)
    else:
        output = mapped(output, mapping)
    return f"$ {cmd}\n{output}" if output else f"$ {cmd}"


def save(name, data):
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))


def load(name):
    return json.loads((OUT / f"{name}.json").read_text())


if __name__ == "__main__":
    t = "CONTAINER ID   IMAGE     COMMAND                  CREATED        STATUS        PORTS                    NAMES\n8ec7c6191411   nginx     \"/docker-entrypoint.…\"   1 second ago   Up 1 second   0.0.0.0:18501->80/tcp   v2p3-web"
    print(retable(t, {"v2p3-web": "web", "18501": "8080"}))


def tty(cmd, cwd=None, cols=88, timeout=900):
    """Run a command under a fake terminal (like a Mac terminal) and return the
    final screen of BuildKit's progress display, without colour codes."""
    import shlex
    inner = f"stty cols {cols} rows 60; {cmd}"
    raw = run(f"script -qc {shlex.quote(inner)} /dev/null", cwd=cwd, timeout=timeout)
    clean = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", raw).replace("\r", "")
    i = clean.rfind("[+] Building")
    tail = clean[i:] if i >= 0 else clean
    return "\n".join(l.rstrip() for l in tail.split("\n")).strip("\n")


def ttymap(text, mapping):
    """Map names in BuildKit tty output while keeping the time column aligned."""
    out = []
    for ln in text.split("\n"):
        new = mapped(ln, mapping)
        if new != ln:
            if ln.startswith("[+] Building"):
                m = re.match(r"(.*?FINISHED)\s+(\S+)$", ln)
                if m:
                    right = mapped(m.group(2), mapping)
                    new = m.group(1).ljust(len(ln) - len(right)) + right
            else:
                m = re.match(r"(.*?)(\s+)(\d+\.\d+s)$", ln)
                if m:
                    new = mapped(m.group(1), mapping).ljust(len(ln) - len(m.group(3))) + m.group(3)
        out.append(new)
    return "\n".join(out)


def screen(raw):
    """Replay cursor moves (up, column 0, clear line) and return the final screen text."""
    lines, row, col = [[]], 0, 0
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\x1b":
            m = re.match(r"\x1b\[([0-9;?]*)([A-Za-z])", raw[i:])
            if m:
                arg, op = m.group(1), m.group(2)
                n = int(arg) if arg.isdigit() else 1
                if op == "A":
                    row = max(0, row - n)
                elif op == "B":
                    row += n
                elif op == "G":
                    col = max(0, (int(arg) if arg.isdigit() else 1) - 1)
                elif op == "K":
                    while len(lines) <= row:
                        lines.append([])
                    lines[row] = [] if arg in ("2", "") and col == 0 else lines[row][:col]
                i += len(m.group(0))
                continue
        if ch == "\n":
            row += 1
            col = 0
        elif ch == "\r":
            col = 0
        else:
            while len(lines) <= row:
                lines.append([])
            ln = lines[row]
            while len(ln) < col:
                ln.append(" ")
            if col < len(ln):
                ln[col] = ch
            else:
                ln.append(ch)
            col += 1
        while len(lines) <= row:
            lines.append([])
        i += 1
    text = "\n".join("".join(l).rstrip() for l in lines)
    return text.strip("\n")


def ttyc(cmd, cwd=None, cols=88, env=None):
    """Run a command in a fake terminal and return its final screen (for Compose)."""
    import shlex
    inner = f"stty cols {cols} rows 60; {cmd}"
    raw = run(f"script -qc {shlex.quote(inner)} /dev/null", cwd=cwd, env=env)
    return screen(raw)
