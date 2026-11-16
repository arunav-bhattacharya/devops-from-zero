#!/bin/bash
# usage: check.sh N  (part number)
cd /home/user/devops-from-zero
python3 brief/validate.py content/p$1.json | tail -8
python3 brief/tells.py content/p$1.json | tail -5
python3 brief/scratch/v5/protect.py brief/scratch/v5/orig/p$1.json content/p$1.json | tail -5
DFZ_CHECK_ONLY=1 python3 site/build.py 2>&1 | tail -2
python3 - "$1" <<'PY'
import json,re,sys
w=lambda s:len(re.findall(r"[A-Za-z0-9'`]+",s or ""))
for L in json.load(open(f'content/p{sys.argv[1]}.json'))['lessons']:
    if L.get('opening'):
        print(L['id'],'secs',[w(s['body']) for s in L['sections']],sum(w(s['body']) for s in L['sections']),'open',w(L['opening']),'close',w(L['closing']),'deeper',w(L['deeper']['body']),'aside',w((L.get('aside') or {}).get('body')))
PY
