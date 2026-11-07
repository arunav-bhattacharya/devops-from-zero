import json, re, sys
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
d = json.load(open(sys.argv[1]))
for L in d['lessons']:
    allsent = [x for s in L['sections'] for x in sentences(s['body'])]
    avg = sum(words(x) for x in allsent) / len(allsent)
    tot = sum(words(s['body']) for s in L['sections'])
    longest = max(allsent, key=words)
    print(L['id'], 'avg', round(avg, 1), 'sec words', tot, 'deeper', words(L['deeper']['body']), 'max', words(longest))
