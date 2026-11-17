#!/usr/bin/env bash
# usage: check.sh pN lessonindex
cd /home/user/devops-from-zero
python3 brief/validate.py content/$1.json | tail -8
python3 brief/tells.py content/$1.json | tail -3
python3 brief/scratch/v5/protect.py brief/scratch/v5/orig/$1.json content/$1.json
DFZ_CHECK_ONLY=1 python3 site/build.py 2>&1 | tail -1
python3 - "$1" "$2" <<'E'
import json,re,sys
w=lambda s: len(re.findall(r"[A-Za-z0-9'`]+", s or ""))
l=json.load(open(f'content/{sys.argv[1]}.json'))['lessons'][int(sys.argv[2])]
print(l['id'],[w(s['body']) for s in l['sections']], 'total',sum(w(s['body']) for s in l['sections']),'open',w(l.get('opening')),'close',w(l.get('closing')),'deeper',w(l['deeper']['body']))
t=json.dumps(l,ensure_ascii=False); print('bold',t.count('**')//2,'dash','—' in t or '–' in t)
E
