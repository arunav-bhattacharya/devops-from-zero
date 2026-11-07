import json, re, sys
def words(s): return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
for f in sys.argv[1:]:
    d = json.load(open(f))
    for L in d['lessons']:
        print(L['id'], sum(words(s['body']) for s in L['sections']), [words(s['body']) for s in L['sections']])
