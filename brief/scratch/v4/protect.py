"""Compare two part files and report changes to anything that is not prose.
Usage: python3 brief/scratch/v4/protect.py ORIGINAL.json EDITED.json"""
import json, sys
PROSE_KEYS = {"intro","recap","back","why","goal","plain","body","analogy","mistake","real_world","say","h","diagram_caption",
              "steps","hints","done_when","prompt","answer","a","front","q"}
def walk(a, b, path, out):
    if type(a) != type(b):
        out.append(f"{path}: type changed"); return
    if isinstance(a, dict):
        if set(a) != set(b): out.append(f"{path}: keys {sorted(set(a)^set(b))}")
        for k in a:
            if k in b: walk(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list):
        if len(a) != len(b): out.append(f"{path}: list length {len(a)} -> {len(b)}"); return
        for i,(x,y) in enumerate(zip(a,b)): walk(x, y, f"{path}[{i}]", out)
    elif a != b:
        key = path.rsplit(".",1)[-1].split("[")[0]
        if key not in PROSE_KEYS: out.append(f"{path}: {str(a)[:60]!r} -> {str(b)[:60]!r}")
orig, new = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
out = []; walk(orig, new, "$", out)
print("\n".join(out[:40]) or "only prose fields changed"); print(len(out), "non-prose changes")
