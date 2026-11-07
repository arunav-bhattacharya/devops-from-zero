import json, sys
ns = {"__file__": "/home/user/devops-from-zero/brief/validate.py"}
exec(open(ns["__file__"]).read().split("def mcq")[0], ns)
path = sys.argv[1]
d = json.load(open(path))
lessons = d if isinstance(d, list) else d["lessons"]
for L in lessons:
    if len(sys.argv) > 2 and L["id"] not in sys.argv[2:]:
        continue
    allsent = [x for s in L["sections"] for x in ns["sentences"](s["body"])]
    tot = sum(ns["words"](s["body"]) for s in L["sections"])
    per = [ns["words"](s["body"]) for s in L["sections"]]
    longest = max(ns["words"](x) for x in allsent)
    print(L["id"], "sections", tot, per, "avg", round(sum(ns["words"](x) for x in allsent) / len(allsent), 1),
          "max", longest, "deeper", ns["words"](L["deeper"]["body"]))
