import json,sys
p,lid=sys.argv[1],sys.argv[2]
d=json.load(open(p))
L=[l for l in d['lessons'] if l['id']==lid][0]
for k,v in L.items():
    if k=='diagram': print('== diagram: (svg)'); continue
    print('==',k)
    print(json.dumps(v,indent=1,ensure_ascii=False) if not isinstance(v,str) else v)
