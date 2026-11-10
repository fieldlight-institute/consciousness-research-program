"""Retain first exhaustive constructed grid, with witnesses and source protection."""
from pathlib import Path
from dataclasses import asdict
from itertools import product
from collections import Counter
import hashlib,json
from oracle import Agent,Operation,solve,capacity
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
 out=ROOT/'first-results';out.mkdir(exist_ok=False)
 prior={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
 sources={n:sha(ROOT/n) for n in ('SPECIFICATION.md','oracle.py','test_oracle.py','demo.py')}
 write(out/'freeze.json',dict(sources=sources,preserved=prior))
 teams=dict(specialists=[Agent('a',0,{'X':2}),Agent('b',0,{'Y':2})],generalists=[Agent('a',0,{'X':1,'Y':1}),Agent('b',0,{'X':1,'Y':1})])
 rows=[]
 for kind,deadline,site,lag in product(('single','sequential','simultaneous'),range(1,7),(0,2),(0,3)):
  if kind=='sequential':ops=[Operation('x',site,0,deadline,(('X',2),)),Operation('y',site,0,deadline,(('Y',2),),('x',))]
  else:ops=[Operation('task',site,0,deadline,(('X',2),) if kind=='single' else (('X',2),('Y',2)))]
  results={k:solve(a,ops,lag) for k,a in teams.items()};statuses=[results[k]['status'] for k in teams]
  category='unknown' if 'unknown' in statuses else 'shared' if statuses==['feasible','feasible'] else 'specialist-only' if statuses==['feasible','infeasible'] else 'generalist-only' if statuses==['infeasible','feasible'] else 'neither'
  rows.append(dict(kind=kind,deadline=deadline,site=site,handoff_latency=lag,operations=[asdict(o) for o in ops],category=category,results=results))
 write(out/'cases.json',rows)
 a=[Agent('only',0,{'X':1})];jobs=[Operation(str(i),0,0,1,(('X',1),)) for i in range(2)]
 conflict=dict(agents=[asdict(x) for x in a],operations=[asdict(o) for o in jobs],individual=[solve(a,[o]) for o in jobs],joint=solve(a,jobs));write(out/'joint-conflict.json',conflict)
 summary=dict(instances=len(rows),categories=dict(Counter(r['category'] for r in rows)),by_type={kind:dict(Counter(r['category'] for r in rows if r['kind']==kind)) for kind in ('single','sequential','simultaneous')},teams={k:[asdict(a) for a in aa] for k,aa in teams.items()},capacity={k:capacity(a) for k,a in teams.items()},largest_search_nodes=max(v['nodes'] for r in rows for v in r['results'].values()))
 write(out/'summary.json',summary)
 for n,h in prior.items():assert sha(ROOT.parent/n)==h,n
 for n,h in sources.items():assert sha(ROOT/n)==h,n
 write(out/'verification.json',dict(prior_artifacts_unchanged=len(prior),sources=sources,all_grid_searches_complete=all(v['search_complete'] for r in rows for v in r['results'].values()),witnesses_validated=sum(v['status']=='feasible' for r in rows for v in r['results'].values()),outputs={p.name:sha(p) for p in out.iterdir() if p.is_file()}))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
