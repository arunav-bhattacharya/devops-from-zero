import json, sys
P = json.load(open(sys.argv[1])); L = next(x for x in P['lessons'] if x['id'] == sys.argv[2])
for k, v in L.items():
    if k in ('diagram',): continue
    if k == 'code':
        for c in v: print('== code', c['title'], '| run:', c.get('run')); print(c['src'][:int(sys.argv[3]) if len(sys.argv) > 3 else 800])
        continue
    if k == 'sections':
        for i, s in enumerate(v): print(f'== sec{i+1}', s['h'], '| fig' if s.get('figure') else ''); print(s['body'])
        continue
    print('==', k); print(v if isinstance(v, str) else json.dumps(v, indent=0, ensure_ascii=False))
