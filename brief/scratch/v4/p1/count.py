import json, re, sys
sys.path.insert(0, 'brief')
def words(s): return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
d = json.load(open(sys.argv[1]))
for L in d['lessons']:
    secs = [words(s['body']) for s in L['sections']]
    print(L['id'], sum(secs), secs)
