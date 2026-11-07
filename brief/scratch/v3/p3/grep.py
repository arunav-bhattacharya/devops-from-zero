import json,re,sys
d=json.load(open(sys.argv[1]))
pat=re.compile(sys.argv[2],re.I)
def walk(o,path):
    if isinstance(o,str):
        for m in pat.finditer(o):
            print(path, '::', o[max(0,m.start()-60):m.end()+50].replace('\n',' / '))
    elif isinstance(o,list):
        for i,x in enumerate(o): walk(x,f'{path}[{i}]')
    elif isinstance(o,dict):
        for k,v in o.items():
            if k in ('diagram','code','commands','src','url','refs','sources'): continue
            walk(v,f'{path}.{k}')
walk(d,'')
