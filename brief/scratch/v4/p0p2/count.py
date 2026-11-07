import json, re, sys
def words(s): return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
for f in sys.argv[1:]:
    d = json.load(open(f))
    for l in d['lessons']:
        secs = [words(s['body']) for s in l['sections']]
        print(f, l['id'], sum(secs), secs)
