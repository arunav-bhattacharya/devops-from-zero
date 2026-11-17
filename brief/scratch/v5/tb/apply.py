"""Shared helper: apply prose updates to one lesson in content/pN.json."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]


def apply(part, lid, upd):
    path = ROOT / f"content/p{part}.json"
    P = json.loads(path.read_text())
    L = next(x for x in P["lessons"] if x["id"] == lid)
    for k, v in upd.items():
        if k == "sections":
            assert len(v) == len(L["sections"]), "section count"
            for s, (h, body) in zip(L["sections"], v):
                s["h"], s["body"] = h, body
        elif k == "drop":
            for d in v:
                L.pop(d, None)
        elif k in ("guess", "explain_back", "task", "deeper", "aside"):
            L.setdefault(k, {}).update(v)
        elif k == "worked_say":
            assert len(v) == len(L["worked"]["steps"])
            for st, say in zip(L["worked"]["steps"], v):
                st["say"] = say
        elif k == "terms_plain":
            assert len(v) == len(L["terms"])
            for t, p in zip(L["terms"], v):
                t["plain"] = p
        elif k in ("check", "interview"):
            assert len(v) == len(L[k])
            for item, new in zip(L[k], v):
                item.update(new)
        else:
            L[k] = v
    # keep a sensible key order: opening before guess, closing after recap
    order = list(L.keys())
    for key, after in (("opening", "goal"), ("closing", "recap")):
        if key in order:
            order.remove(key)
            order.insert(order.index(after) + 1, key)
    new = {k: L[k] for k in order}
    P["lessons"][P["lessons"].index(L)] = new
    path.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")
