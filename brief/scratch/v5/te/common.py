"""Helper for te's fifth-pass rewrites: replace one lesson's prose fields and write the part file back."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]


def apply(part, lid, new):
    path = ROOT / "content" / f"p{part}.json"
    P = json.loads(path.read_text())
    L = next(x for x in P["lessons"] if x["id"] == lid)
    for key in ("goal", "opening", "closing", "diagram_caption", "recap"):
        if key in new:
            L[key] = new[key]
    if "guess" in new:
        L["guess"]["q"], L["guess"]["why"] = new["guess"]
    if "terms" in new:
        assert len(new["terms"]) == len(L["terms"])
        for t, plain in zip(L["terms"], new["terms"]):
            t["plain"] = plain
    if "sections" in new:
        assert len(new["sections"]) == len(L["sections"])
        for s, (h, body) in zip(L["sections"], new["sections"]):
            s["h"], s["body"] = h, body.strip()
    if "worked" in new:
        assert len(new["worked"]) == len(L["worked"]["steps"])
        for st, say in zip(L["worked"]["steps"], new["worked"]):
            st["say"] = say
    if "task" in new:
        t = new["task"]
        L["task"]["steps"], L["task"]["hints"], L["task"]["done_when"] = t["steps"], t["hints"], t["done_when"]
    if "explain_back" in new:
        L["explain_back"]["prompt"], L["explain_back"]["answer"] = new["explain_back"]
    if "check" in new:
        assert len(new["check"]) == len(L["check"])
        for q, (qq, why) in zip(L["check"], new["check"]):
            q["q"], q["why"] = qq, why
    if "interview" in new:
        assert len(new["interview"]) == len(L["interview"])
        for q, (qq, a) in zip(L["interview"], new["interview"]):
            q["q"], q["a"] = qq, a
    if "deeper" in new:
        L["deeper"]["body"] = new["deeper"].strip()
    if "aside" in new:
        L["aside"] = new["aside"]
    for k in new.get("drop", []):
        L.pop(k, None)
    for k, v in new.get("keep", {}).items():
        L[k] = v
    # keep a stable key order: put opening right after goal, closing after recap
    order = list(L.keys())
    def move(k, after):
        if k in order and after in order:
            order.remove(k)
            order.insert(order.index(after) + 1, k)
    move("opening", "goal")
    move("closing", "recap")
    move("aside", "sections")
    P["lessons"][P["lessons"].index(L)] = {k: L[k] for k in order}
    path.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")
    print("wrote", path, lid)
