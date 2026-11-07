import json, re, sys
sys.path.insert(0, '/home/user/devops-from-zero/brief')
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
        secs = L['sections']
        tot = sum(words(s['body']) for s in secs)
        allsent = [x for s in secs for x in sentences(s['body'])]
        avg = sum(words(x) for x in allsent)/len(allsent)
        print(L['id'], tot, 'avg %.1f' % avg, [words(s['body']) for s in secs], 'deeper', words(L['deeper']['body']))
