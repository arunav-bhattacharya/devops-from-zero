import json, re, sys
sys.path.insert(0, '/home/user/devops-from-zero/brief')
def words(s): return len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
for path, ids in (('content/p10.json', ['d43','d44','d45','d46']), ('content/p11.json', ['d47','d48'])):
    d = json.load(open(path))
    for L in d['lessons']:
        if L['id'] in ids:
            per = [words(s['body']) for s in L['sections']]
            print(L['id'], sum(per), per)
