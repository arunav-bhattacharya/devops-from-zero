import json,sys
d=json.load(open(sys.argv[1]))
which=sys.argv[2]
if which=='part':
    L={k:v for k,v in d.items() if k!='lessons'}
    print(json.dumps(L,indent=1,ensure_ascii=False))
else:
    L=[l for l in d['lessons'] if l['id']==which][0]
    def walk(o,pre=''):
        if isinstance(o,dict):
            for k,v in o.items(): walk(v,pre+'.'+k)
        elif isinstance(o,list):
            for i,v in enumerate(o): walk(v,pre+f'[{i}]')
        else:
            print(f'--- {pre}\n{o}')
    walk(L)
