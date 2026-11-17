"""Helpers for writer th: load a part file, patch one lesson's prose, write it back."""
import json, pathlib, re

ROOT = pathlib.Path("/home/user/devops-from-zero")


def load(part):
    return json.loads((ROOT / f"content/p{part}.json").read_text())


def save(part, d):
    (ROOT / f"content/p{part}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")


def lesson(d, lid):
    return next(L for L in d["lessons"] if L["id"] == lid)


def words(s):
    return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))


def apply(part, lid, new):
    """new: dict with prose keys. 'sections' is a list of (h, body) pairs; 'say' a list of worked texts;
    'check' a list of (q, why); 'interview' a list of (q, a); 'drop' a list of keys to delete."""
    d = load(part)
    L = lesson(d, lid)
    secs = new.pop("sections")
    assert len(secs) == len(L["sections"]), "section count changed"
    for s, (h, body) in zip(L["sections"], secs):
        s["h"], s["body"] = h, body
    for key, field, sub in (("say", "worked", None), ("check", "check", ("q", "why")),
                            ("interview", "interview", ("q", "a")), ("terms", "terms", ("plain",))):
        vals = new.pop(key)
        items = L["worked"]["steps"] if field == "worked" else L[field]
        assert len(vals) == len(items), f"{key} count changed"
        for it, v in zip(items, vals):
            if sub is None:
                it["say"] = v
            elif len(sub) == 1:
                it[sub[0]] = v
            else:
                it[sub[0]], it[sub[1]] = v
    if "guess" in new:
        L["guess"]["q"], L["guess"]["why"] = new.pop("guess")
    if "deeper" in new:
        L["deeper"]["body"] = new.pop("deeper")
    if "explain_back" in new:
        L["explain_back"]["prompt"], L["explain_back"]["answer"] = new.pop("explain_back")
    if "task" in new:
        t = new.pop("task")
        L["task"]["steps"], L["task"]["hints"], L["task"]["done_when"] = t
    for k in new.pop("drop", []):
        L.pop(k, None)
    # keep key order: insert opening right after goal, closing after recap
    for k, v in new.items():
        L[k] = v
    order = ["id", "title", "minutes", "goal", "opening", "guess", "terms", "sections", "aside", "analogy", "diagram",
             "diagram_caption", "worked", "code", "commands", "mistake", "real_world", "task", "explain_back", "recap",
             "closing", "check", "interview", "deeper", "sources"]
    rest = [k for k in L if k not in order]
    L2 = {k: L[k] for k in order + rest if k in L}
    d["lessons"][d["lessons"].index(L)] = L2
    save(part, d)
    print(lid, "sections", sum(words(b) for _, b in secs), "opening", words(L2.get("opening")),
          "closing", words(L2.get("closing")))
