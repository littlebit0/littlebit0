#!/usr/bin/env bash
set -euo pipefail
U=littlebit0
c=$(gh api "search/commits?q=author:$U" --jq .total_count)
i=$(gh api "search/issues?q=author:$U+type:issue" --jq .total_count)
p=$(gh api "search/issues?q=author:$U+type:pr" --jq .total_count)
python3 -I - "$c" "$i" "$p" <<'PY'
import sys
c,i,p=map(int,sys.argv[1:4])
t=open('.github/scripts/stats.template.svg',encoding='utf-8').read()
m=max(c,i,p,1)
w=lambda n:str(max(14,round(520*n/m)))
for k,v in {'{{C_FMT}}':f'{c:,}','{{I_FMT}}':f'{i:,}','{{P_FMT}}':f'{p:,}','{{I_W}}':w(i),'{{P_W}}':w(p)}.items():
    t=t.replace(k,v)
open('assets/stats.svg','w',encoding='utf-8').write(t)
PY
