#!/bin/bash
# usage: check.sh dNN
cd /home/user/devops-from-zero
python3 brief/scratch/v5/tf/apply.py $1 && python3 brief/validate.py content/p10.json
python3 brief/tells.py content/p10.json | tail -5
python3 brief/scratch/v5/protect.py brief/scratch/v5/orig/p10.json content/p10.json
DFZ_CHECK_ONLY=1 python3 site/build.py 2>&1 | tail -1
python3 - $1 <<'PY'
import json,re,sys
src=open('brief/validate.py').read().split('def mcq')[0].replace('__file__','"brief/validate.py"')
exec(src)
d=json.load(open('content/p10.json'));L=[l for l in d['lessons'] if l['id']==sys.argv[1]][0]
ss=[x for s in L['sections'] for x in sentences(s['body'])]
print('sections',[words(s['body']) for s in L['sections']],'total',sum(words(s['body']) for s in L['sections']))
print('opening',words(L.get('opening')),'closing',words(L.get('closing')),'deeper',words(L['deeper']['body']))
print('avg sentence',round(sum(words(x) for x in ss)/len(ss),1),'max',max(words(x) for x in ss))
PY
