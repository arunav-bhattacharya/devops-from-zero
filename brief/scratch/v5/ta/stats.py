import json, re, sys
def words(s): return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
def strip(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s or ""); return re.sub(r"`[^`]*`", "code", s)
def sents(s):
    out = []
    for line in strip(s).split("\n"):
        line = re.sub(r"^\s*(- |\d+\. )", "", line).strip()
        if line: out += [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line) if x.strip()]
    return out
P = json.load(open(sys.argv[1]))
for L in P["lessons"]:
    if len(sys.argv) > 2 and L["id"] not in sys.argv[2:]: continue
    ss = [x for s in L["sections"] for x in sents(s["body"])]
    print(L["id"], "sections", [words(s["body"]) for s in L["sections"]], "total", sum(words(s["body"]) for s in L["sections"]),
          "avg %.1f" % (sum(map(words, ss)) / len(ss)), "opening", words(L.get("opening", "")), "closing", words(L.get("closing", "")),
          "bold", json.dumps(L).count("**") // 2)
