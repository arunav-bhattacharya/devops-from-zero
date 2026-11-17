"""Shared helpers for tc's fifth-pass lesson scripts."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]


def load(part, lid):
    path = ROOT / f"content/p{part}.json"
    P = json.loads(path.read_text())
    O = json.loads((ROOT / f"brief/scratch/v5/orig/p{part}.json").read_text())
    L = next(x for x in P["lessons"] if x["id"] == lid)
    OL = next(x for x in O["lessons"] if x["id"] == lid)
    return path, P, L, OL


def apply(L, new):
    """Set prose fields from a dict. Keys: goal, opening, closing, aside, guess_q, guess_why,
    terms (term -> plain), sections (list of (h, body)), drop (list), and any top-level prose key."""
    for k, v in new.items():
        if k == "guess_q":
            L["guess"]["q"] = v
        elif k == "guess_why":
            L["guess"]["why"] = v
        elif k == "terms":
            for t in L["terms"]:
                t["plain"] = v[t["term"]]
        elif k == "sections":
            assert len(v) == len(L["sections"])
            for s, (h, body) in zip(L["sections"], v):
                s["h"], s["body"] = h, body
        elif k == "worked":
            assert len(v) == len(L["worked"]["steps"])
            for st, say in zip(L["worked"]["steps"], v):
                st["say"] = say
        elif k == "task":
            L["task"].update(v)
        elif k == "explain_back":
            L["explain_back"].update(v)
        elif k == "check":
            assert len(v) == len(L["check"])
            for q, (qq, why) in zip(L["check"], v):
                q["q"], q["why"] = qq, why
        elif k == "interview":
            assert len(v) == len(L["interview"])
            for q, (qq, a) in zip(L["interview"], v):
                q["q"], q["a"] = qq, a
        elif k == "deeper":
            L["deeper"]["body"] = v
        elif k == "drop":
            for d in v:
                L.pop(d, None)
        else:
            L[k] = v


def save(path, P, L, OL):
    new = {}
    for k in OL:
        if k in L:
            new[k] = L[k]
        if k == "goal" and "opening" in L:
            new["opening"] = L["opening"]
    for k in L:
        if k not in new and k not in ("aside", "closing"):
            new[k] = L[k]
    if "aside" in L:
        new["aside"] = L["aside"]
    if "closing" in L:
        new["closing"] = L["closing"]
    P["lessons"][P["lessons"].index(L)] = new
    path.write_text(json.dumps(P, ensure_ascii=False, indent=1) + "\n")
    print(new["id"], "written")
