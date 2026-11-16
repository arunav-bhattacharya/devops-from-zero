import json, re, sys
sys.path.insert(0, 'brief')
P = json.load(open(sys.argv[1])); lid = sys.argv[2]
L = next(x for x in P['lessons'] if x['id'] == lid)
w = lambda s: len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
tot = 0
for i, s in enumerate(L['sections']):
    tot += w(s['body']); print(i + 1, w(s['body']), s['h'])
print('sections', tot, 'opening', w(L.get('opening')), 'closing', w(L.get('closing')), 'aside', w((L.get('aside') or {}).get('body')))
from validate import sentences, words
allsent = [x for s in L['sections'] for x in sentences(s['body'])]
print('avg sentence', round(sum(words(x) for x in allsent) / len(allsent), 1))
