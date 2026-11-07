import json,sys
d=json.load(open(sys.argv[1]))
for L in d['lessons']:
    if L['id'] not in sys.argv[2:]: continue
    print('=====',L['id'],L['title'])
    for s in L['sections']:
        print('##',s['h']); print(s['body']); print()
    print('## worked:', L['worked']['title'])
    for st in L['worked']['steps']:
        print('-',st['say'][:300])
    print('## code titles:', [c['title'] for c in L['code']])
    print('## deeper:', L['deeper']['body'][:1500])
