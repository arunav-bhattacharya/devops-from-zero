"""Helpers shared by the Part 1 lesson modules: real console output, lesson files, SVG pieces."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUTPUTS = json.loads((HERE / "outputs.json").read_text())
FILES = HERE / "files"


def blocks(name):
    """Split a saved transcript into [(command, output)], dropping <<SPLIT>> markers."""
    text = OUTPUTS[name]
    res = []
    for line in text.split("\n"):
        if line == "<<SPLIT>>":
            res.append(("<<SPLIT>>", ""))
            continue
        if line.startswith("$ "):
            res.append([line, []])
        elif res and res[-1][0] != "<<SPLIT>>":
            res[-1][1].append(line)
        else:
            raise ValueError(f"output before first command in {name}: {line!r}")
    return [(c, "\n".join(o)) for c, o in res]


def con(name, *picks, part=None):
    """Console text for a snippet. part=N picks the Nth <<SPLIT>> section.
    picks: command indexes (ints) within that section; default all."""
    bl = blocks(name)
    parts, cur = [], []
    for c, o in bl:
        if c == "<<SPLIT>>":
            parts.append(cur)
            cur = []
        else:
            cur.append((c, o))
    parts.append(cur)
    sel = parts[part or 0]
    if picks:
        sel = [sel[i] for i in picks]
    out = []
    for c, o in sel:
        out.append(c)
        if o:
            out.append(o)
    text = "\n".join(out)
    assert text, name
    return text


def src(name):
    return (FILES / name).read_text()


# ---------------------------------------------------------------- SVG helpers
def svg(h, label, body):
    assert 140 <= h <= 380
    return (f'<svg viewBox="0 0 560 {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            + "".join(body) + "</svg>")


def box(x, y, w, h, cls, text, sub=None):
    tcls = "t" if cls == "bx" else "tk"
    cx = x + w / 2
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>']
    if sub:
        parts.append(f'<text x="{cx:g}" y="{y + h / 2 - 3:g}" font-size="13" text-anchor="middle" class="{tcls}">{text}</text>')
        parts.append(f'<text x="{cx:g}" y="{y + h / 2 + 13:g}" font-size="11" text-anchor="middle" class="{tcls}">{sub}</text>')
    else:
        parts.append(f'<text x="{cx:g}" y="{y + h / 2 + 5:g}" font-size="13" text-anchor="middle" class="{tcls}">{text}</text>')
    return "".join(parts)


def arrow(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" class="{cls}" marker-end="url(#ar)"/>'


def line(x1, y1, x2, y2, dashed=False):
    cls = "lnd" if dashed else "ln"
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" class="{cls}"/>'


def cap(x, y, text, anchor="middle", size=11, cls="ts"):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}" class="{cls}">{text}</text>'


def row(y, h, items, x0=8, gap=None, total=544):
    """Lay out boxes left to right. items: [(label, cls, width, sub)]. Returns (svg parts, [(x, w)])."""
    widths = [w for _, _, w, _ in items]
    if gap is None:
        gap = (total - sum(widths)) / (len(items) - 1)
    parts, pos = [], []
    x = x0
    for (label, cls, w, sub) in items:
        need = 8 * max(len(label), len(sub or "") * 11 / 13) + 24
        assert w >= need - 0.1, (label, w, need)
        parts.append(box(x, y, w, h, cls, label, sub))
        pos.append((x, w))
        x += w + gap
    for (xa, wa), (xb, _) in zip(pos, pos[1:]):
        assert xb - (xa + wa) >= 12, "gap too small"
        parts.append(arrow(xa + wa + 2, y + h / 2, xb - 2, y + h / 2))
    return parts, pos


# ---------------------------------------------------------------- markup helpers
def B(*items):
    """Bulleted list."""
    return "\n".join("- " + i for i in items)


def N(*items):
    """Numbered list."""
    return "\n".join(f"{n}. {i}" for n, i in enumerate(items, 1))


def P(*paras):
    """Join paragraphs and lists with blank lines."""
    return "\n\n".join(paras)


def ref(title, url, kind):
    return {"title": title, "url": url, "kind": kind}


# Links used in several lessons (all from the research notes or this task's searches)
MS26_L1 = ref("Missing Semester 2026: Introduction to the shell (MIT)", "https://missing.csail.mit.edu/2026/course-shell/", "read")
MS26_L1_V = ref("Lecture 1: Course overview and the shell (Missing Semester, MIT)", "https://www.youtube.com/watch?v=MSgoeuMqUmU", "watch")
MS26_L2 = ref("Missing Semester 2026: Command-line environment (MIT)", "https://missing.csail.mit.edu/2026/command-line-environment/", "read")
MS26_L2_V = ref("Lecture 2: Command-line environment (Missing Semester, MIT)", "https://www.youtube.com/watch?v=ccBGsPedE9Q", "watch")
MS20_DW = ref("Missing Semester 2020: Data wrangling notes (MIT)", "https://missing.csail.mit.edu/2020/data-wrangling/", "read")
MS20_DW_V = ref("Lecture 4: Data wrangling (Missing Semester, MIT)", "https://www.youtube.com/watch?v=sz_dsktIjt4", "watch")
MS20_CLE_V = ref("Lecture 5: Command-line environment, 2020 (Missing Semester, MIT)", "https://www.youtube.com/watch?v=e8BO_dYxk5c", "watch")
MS20_ST_V = ref("Lecture 2: Shell tools and scripting (Missing Semester, MIT)", "https://www.youtube.com/watch?v=kgII-YWo3Zw", "watch")
SWC = ref("The Unix Shell (Software Carpentry)", "https://swcarpentry.github.io/shell-novice/", "read")
SWC_FIND = ref("Software Carpentry: Finding things (grep and find)", "https://github.com/swcarpentry/shell-novice/blob/main/episodes/07-find.md", "read")
SWC_PIPE = ref("Software Carpentry: Pipes and filters", "https://github.com/swcarpentry/shell-novice/blob/main/episodes/04-pipefilter.md", "read")
FCC50 = ref("The 50 most popular Linux and terminal commands (freeCodeCamp)", "https://www.youtube.com/watch?v=ZtqBQ68cfJc", "watch")
FIRESHIP_BASH = ref("Bash in 100 seconds (Fireship)", "https://www.youtube.com/watch?v=I4EWvMFj37g", "watch")
LLTV_JOURNAL = ref("journalctl basics (Learn Linux TV)", "https://www.youtube.com/watch?v=0dG3vUYt7Uk", "watch")
BASH_MANUAL = ref("GNU Bash Reference Manual", "https://www.gnu.org/software/bash/manual/bash.html", "docs")
BASH_REDIR = ref("Bash manual: Redirections", "https://www.gnu.org/software/bash/manual/html_node/Redirections.html", "docs")
BASH_SET = ref("Bash manual: The Set Builtin", "https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html", "docs")
BASH_COND = ref("Bash manual: Conditional expressions", "https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html", "docs")
BASH_EXIT = ref("Bash manual: Exit status", "https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html", "docs")
GREP_MAN = ref("GNU grep manual", "https://www.gnu.org/software/grep/manual/grep.html", "docs")
GREP_RE = ref("GNU grep manual: Regular expressions", "https://www.gnu.org/software/grep/manual/html_node/Regular-Expressions.html", "docs")
GREP_BRE = ref("GNU grep manual: Basic vs extended regular expressions", "https://www.gnu.org/software/grep/manual/html_node/Basic-vs-Extended.html", "docs")
BSD_GNU = ref("macOS and Unix: BSD vs GNU tools", "https://cloudstreet-dev.github.io/macOS-and-Unix/part6-commands/bsd-vs-gnu.html", "read")
JQ_MAN = ref("jq manual", "https://jqlang.org/manual/", "docs")
JQ_TUT = ref("jq tutorial", "https://jqlang.org/tutorial/", "read")
HIER = ref("hier(7): the Linux file system layout (man7.org)", "https://man7.org/linux/man-pages/man7/hier.7.html", "docs")
TLDR = ref("tldr pages: short, example-first help", "https://tldr.sh/", "read")
EXPLAIN = ref("explainshell: see what each part of a command does", "https://explainshell.com", "read")
DOCKER_RUN = ref("docker container run reference (Docker docs)", "https://docs.docker.com/reference/cli/docker/container/run/", "docs")
DOCKER_STOP = ref("docker container stop (Docker docs)", "https://docs.docker.com/reference/cli/docker/container/stop/", "docs")
DOCKER_BP = ref("Docker building best practices (see USER)", "https://docs.docker.com/build/building/best-practices/", "docs")
K8S_POD = ref("Pod lifecycle: termination of pods (Kubernetes docs)", "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/", "docs")
SYSTEMD_KILL = ref("systemd.kill(5): how systemd stops services (man7.org)", "https://man7.org/linux/man-pages/man5/systemd.kill.5.html", "docs")
SYSTEMCTL = ref("systemctl manual (freedesktop.org)", "https://www.freedesktop.org/software/systemd/man/latest/systemctl.html", "docs")
SYSTEMD_UNIT = ref("systemd.unit manual (freedesktop.org)", "https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html", "docs")
MULTIPASS = ref("Getting started with Multipass (Canonical docs)", "https://canonical.com/multipass/docs/latest/tutorial/getting-started/", "docs")
MULTIPASS_INSTALL = ref("Install Multipass (Canonical docs)", "https://canonical.com/multipass/docs/latest/how-to-guides/install-multipass/", "docs")
LC_PERM = ref("Learning the shell: Permissions (LinuxCommand.org)", "https://linuxcommand.org/lc3_lts0090.php", "read")
LC_REDIR = ref("Learning the shell: I/O redirection (LinuxCommand.org)", "https://linuxcommand.org/lc3_lts0070.php", "read")
LC_SHELL = ref("Learning the shell (LinuxCommand.org)", "https://linuxcommand.org/lc3_learning_the_shell.php", "read")
LC_TRAPS = ref("Writing shell scripts: errors, signals and traps (LinuxCommand.org)", "https://linuxcommand.org/lc3_wss0150.php", "read")
TLCL = ref("The Linux Command Line, free book (William Shotts)", "https://linuxcommand.org/tlcl.php", "read")
GH_SSH = ref("Generating a new SSH key and adding it to the ssh-agent (GitHub docs)", "https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent", "docs")
SSH_KEYGEN = ref("ssh-keygen(1) manual page (man7.org)", "https://www.man7.org/linux/man-pages/man1/ssh-keygen.1.html", "docs")
SHELLCHECK = ref("ShellCheck: finds bugs in shell scripts", "https://www.shellcheck.net/", "read")
SHELLCHECK_GH = ref("ShellCheck on GitHub, with its gallery of bad code", "https://github.com/koalaman/shellcheck", "docs")
COREUTILS_CHMOD = ref("GNU coreutils: chmod", "https://www.gnu.org/software/coreutils/chmod", "docs")
CMD_NOT_FOUND = ref("command-not-found.com: which package gives you a command", "https://command-not-found.com", "read")
