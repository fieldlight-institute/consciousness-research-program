from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
import json,hashlib
from lifecycle import propose,apply
from test_lifecycle import fixture
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
 out=ROOT/'first-results';out.mkdir(exist_ok=False)
 sources={n:sha(ROOT/n) for n in ('SPECIFICATION.md','lifecycle.py','test_lifecycle.py','demo.py')}
 prior={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
 write(out/'freeze.json',dict(sources=sources,preserved=prior))
 rows=[]
 for name,early,requested,authority,apply_time in [('authorized cascade',False,['q'],['a','b'],2),('missing indirect authority',False,['q'],['a'],2),('downstream already traveling',True,['q'],['a','b'],2),('stale decision time',False,['q'],['a','b'],3),('completed operation protected',False,['p'],['a','b'],2),('unrelated tail withdrawal',False,['r'],['a'],2)]:
  a,o,j,e=fixture(early);before=deepcopy(e);proposal=propose(a,o,j,e,requested,2)
  row=dict(name=name,agents=[asdict(x) for x in a],operations=[asdict(x) for x in o],jobs=j,before=e,proposal=proposal,authorized_agents=authority,apply_time=apply_time)
  try:row['result']=apply(a,o,j,e,proposal,authority,apply_time);row['status']='applied'
  except ValueError as error:row['status']='rejected';row['reason']=str(error)
  assert e==before;rows.append(row)
 write(out/'demonstrations.json',rows)
 for n,h in prior.items():assert sha(ROOT.parent/n)==h,n
 for n,h in sources.items():assert sha(ROOT/n)==h,n
 summary=dict(cases=len(rows),applied=sum(x['status']=='applied' for x in rows),rejected=sum(x['status']=='rejected' for x in rows),caller_snapshots_unchanged=True,prior_artifacts_unchanged=len(prior),sources=sources)
 write(out/'verification.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
