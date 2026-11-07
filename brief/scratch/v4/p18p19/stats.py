import json, re, sys
sys.path.insert(0, 'brief')
def words(s): return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
def strip_markup(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s or "")
    return re.sub(r"`[^`]*`", "code", s)
def sentences(s):
    s = strip_markup(s); out = []
    for line in s.split("\n"):
        line = re.sub(r"^\s*(- |\d+\. )", "", line).strip()
        if line: out += [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line) if x.strip()]
    return out
for f in sys.argv[1:]:
    d = json.load(open(f))
    for L in d['lessons']:
        tot = 0; allsent = []
        per = []
        for s in L['sections']:
            w = words(s['body']); tot += w; per.append(w); allsent += sentences(s['body'])
        avg = sum(words(x) for x in allsent) / len(allsent)
        print(L['id'], 'words', tot, 'per', per, 'avg %.1f' % avg, 'max', max(words(x) for x in allsent), 'deeper', words(L['deeper']['body']))
