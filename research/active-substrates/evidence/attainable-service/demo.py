"""Freeze and retain bounded service demonstrations without overwriting prior evidence."""
from pathlib import Path
from dataclasses import asdict
from itertools import product,combinations
from collections import Counter
import hashlib,json
from service import Agent,Operation,maximize_service,score_schedule
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,data):
 with path.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
def singles(durations,deadline):
 ops=[Operation(str(i),0,0,deadline,(('X',d),)) for i,d in enumerate(durations)]
 return ops,{str(i):[str(i)] for i in range(len(ops))}
def main():
 out=ROOT/'first-results';out.mkdir(exist_ok=False)
 prior={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
 sources={n:sha(ROOT/n) for n in ('SPECIFICATION.md','service.py','test_service.py','demo.py')};dependency=ROOT.parent/'complementary-feasibility/oracle.py'
 write(out/'freeze.json',dict(sources=sources,dependency={str(dependency.resolve()):sha(dependency)},preserved=prior))
 a=[Agent('a',0,{'X':1,'Y':1})];cases=[]
 def retain(name,ops,jobs,**kwargs):
  result=maximize_service(a,ops,jobs,**kwargs)
  assert score_schedule(a,ops,jobs,result['witness'])['service']==result['lower']
  cases.append(dict(name=name,agents=[asdict(x) for x in a],operations=[asdict(x) for x in ops],jobs=jobs,limits=kwargs,result=result))
 ops,jobs=singles([1,1],1);retain('individually feasible but competing',ops,jobs)
 ops=[Operation('x',0,0,1,(('X',1),)),Operation('y',0,0,1,(('Y',1),),('x',))];retain('partial composite earns no completion',ops,{'whole':['x','y']})
 ops=[Operation('x',0,0,2,(('X',1),)),Operation('y',0,0,2,(('Y',1),),('x',))];retain('prerequisite finishes another whole job',ops,{'first':['x'],'second':['y']})
 ops=[Operation('a1',0,0,2,(('X',1),)),Operation('a2',0,0,2,(('Z',1),)),Operation('b',0,0,2,(('Y',1),),('a1',))];retain('prerequisite remains a partial job',ops,{'A':['a1','a2'],'B':['b']})
 ops,jobs=singles([1,1],2);retain('global search exhausted',ops,jobs,node_limit=1);retain('positive witness unresolved optimum',ops,jobs,node_limit=10,per_candidate_limit=2)
 write(out/'demonstrations.json',cases)
 grid=[]
 for durations in product(range(1,4),repeat=3):
  for deadline in range(1,7):
   ops,jobs=singles(durations,deadline);result=maximize_service(a,ops,jobs)
   independent=max([0]+[len(c) for n in range(1,4) for c in combinations(durations,n) if sum(c)<=deadline])
   assert result['lower']==result['upper']==independent
   grid.append(dict(durations=durations,deadline=deadline,independent_optimum=independent,result=result))
 write(out/'grid.json',grid)
 summary=dict(instances=len(grid),counts_by_optimum=dict(Counter(x['independent_optimum'] for x in grid)),maximum_nodes=max(x['result']['nodes'] for x in grid),demonstrations=[dict(name=c['name'],status=c['result']['status'],lower=c['result']['lower'],upper=c['result']['upper']) for c in cases])
 write(out/'summary.json',summary)
 for n,h in prior.items():assert sha(ROOT.parent/n)==h,n
 for n,h in sources.items():assert sha(ROOT/n)==h,n
 write(out/'verification.json',dict(prior_artifacts_unchanged=len(prior),independent_grid_matches=len(grid),demonstration_witnesses_checked=len(cases),dependency_sha256=sha(dependency),sources=sources,outputs={p.name:sha(p) for p in out.iterdir() if p.is_file()}))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
