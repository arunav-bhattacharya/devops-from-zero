#!/usr/bin/env python3
"""Third edition: make room for 13 new lessons (Git, hands-on AWS, Python, Ansible, service mesh, AI).

Renumbers lesson ids (dNN), part numbers, content/pN.json file names, site/art/pN.svg, and every
"Day N" / "Part N" reference in lessons, labs, the index, the build's lab-day map and the README.
Writes brief/renumber-v3.json, which the site uses once to move saved progress to the new ids.
Run once from the repo root. It refuses to run twice."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAPFILE = ROOT / "brief/renumber-v3.json"


def day_map():
    m = {}
    for old in range(1, 56):
        shift = 0 if old <= 7 else 2 if old <= 10 else 6 if old <= 29 else 8 if old <= 49 else 11 if old <= 53 else 13
        m[old] = old + shift
    return m


DAY = day_map()
PART = {0: 0, 1: 1, 2: 3, 3: 5, 4: 6, 5: 7, 6: 8, 7: 10, 8: 11, 9: 12, 10: 13, 11: 14, 12: 16, 13: 17, 14: 19}
REF = re.compile(r"\b(Days?|Parts?) (\d+)((?:(?:, | and | to | or |-)\d+)*)")


def renum_text(s):
    def fix(m):
        word, first, rest = m.group(1), m.group(2), m.group(3)
        table = DAY if word.startswith("Day") else PART

        def one(n):
            v = table.get(int(n))
            if v is None:
                raise SystemExit(f"no mapping for {word} {n} in: {s[max(0, m.start() - 60):m.end() + 20]!r}")
            return str(v).zfill(len(n)) if n.startswith("0") else str(v)
        rest = re.sub(r"\d+", lambda x: one(x.group(0)), rest)
        return f"{word} {one(first)}{rest}"
    return REF.sub(fix, s)


def lid(old):
    return f"d{DAY[int(old[1:])]:02d}"


def walk(x, key=None):
    if isinstance(x, dict):
        return {k: walk(v, k) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v, key) for v in x]
    if isinstance(x, str) and key not in ("url",):
        return renum_text(x)
    return x


def main():
    if MAPFILE.exists():
        sys.exit("already renumbered (brief/renumber-v3.json exists)")
    # 1. content files: renumber into memory first, then write, so p2 -> p3 does not clobber p3
    out = {}
    for old in PART:
        path = ROOT / f"content/p{old}.json"
        d = json.loads(path.read_text())
        d = walk(d)
        d["part"] = PART[old]
        for L in d["lessons"]:
            L["id"] = lid(L["id"])
        out[PART[old]] = d
    for old in PART:
        (ROOT / f"content/p{old}.json").unlink()
    for new, d in out.items():
        (ROOT / f"content/p{new}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    # 2. art plates
    tmp = {}
    for old, new in PART.items():
        p = ROOT / f"site/art/p{old}.svg"
        if p.exists():
            tmp[new] = p.read_text()
            p.unlink()
    for new, svg in tmp.items():
        (ROOT / f"site/art/p{new}.svg").write_text(svg)
    # 3. index: ids, part numbers and scope text ("from" keeps first-edition ids, as before)
    idx = json.loads((ROOT / "brief/index.json").read_text())
    for P in idx:
        P["part"] = PART[P["part"]]
        for L in P["lessons"]:
            L["id"] = lid(L["id"])
            L["scope"] = renum_text(L["scope"])
    (ROOT / "brief/index.json").write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n")
    # 4. labs and docs: every text file
    skip = {".terraform", ".git", "__pycache__", ".gradle", "build", "charts", ".venv"}
    files = [f for f in (ROOT / "labs").rglob("*") if f.is_file() and not skip & set(f.relative_to(ROOT).parts)]
    files += [ROOT / "README.md", ROOT / "DEPLOY.md"]
    changed = 0
    for f in files:
        try:
            t = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        n = renum_text(t)
        if n != t:
            f.write_text(n)
            changed += 1
    # 5. the build's lab-day map
    b = (ROOT / "site/build.py").read_text()
    b2 = re.sub(r'(\("(?:hello-devops|linux|hello-jvm|terraform-practice)", "[^"]*", )(\d+)\)', lambda m: f"{m.group(1)}{DAY[int(m.group(2))]})", b)
    b2 = b2.replace("for pr, pre, d in DAYS if pr == proj.name and rel.startswith(pre)), 55)", "for pr, pre, d in DAYS if pr == proj.name and rel.startswith(pre)), 68)")
    (ROOT / "site/build.py").write_text(b2)
    # 6. the map the site uses to move saved progress
    m = {f"d{o:02d}": f"d{n:02d}" for o, n in DAY.items() if o != n}
    m.update({f"p{o}": f"p{n}" for o, n in PART.items() if o != n})
    MAPFILE.write_text(json.dumps(m, indent=1) + "\n")
    print(f"renumbered 15 parts, 55 lessons; {changed} lab/doc files changed; map has {len(m)} entries")


if __name__ == "__main__":
    main()
