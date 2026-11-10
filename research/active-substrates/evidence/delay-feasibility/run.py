from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'attainable-service'))
from service import Agent,Operation,maximize_service,score_schedule
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
 with p.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
def sources():return {n:sha(ROOT/n) for n in ['SPECIFICATION.md','run.py']}
def transform(w,delays):
 agents=[Agent(a['id'],a['site'],a['rates'],frozenset(a['refused'])) for a in w['agents']]
 assert set(delays)=={o['id'] for o in w['operations']}
 ops=[]
 for o in w['operations']:
  assert len(o['demands'])==1
  skill,units=o['demands'][0];extra=delays[o['id']]
  assert type(extra)==int and extra in (0,1)
  assert all(a.rates.get(skill)==1 for a in agents)
  op=Operation(o['id'],o['site'],o['release'],o['deadline'],((skill,units+extra),),tuple(o['predecessors']))
  assert all((units+extra+a.rates[skill]-1)//a.rates[skill]==units+extra for a in agents)
  ops.append(op)
 return agents,ops

def main():
 if sys.argv[1]=='freeze':
  prior={str(p.relative_to(BASE)):sha(p) for p in BASE.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
  write(ROOT/'freeze.json',dict(sources=sources(),prior=prior));print('frozen',len(prior));return
 frozen=json.loads((ROOT/'freeze.json').read_text());assert frozen['sources']==sources()
 for n,h in frozen['prior'].items():assert sha(BASE/n)==h
 w=json.loads((BASE/'reservation-replanning/evaluation/workload-18035.json').read_text())
 cases=json.loads((BASE/'execution-delay/first-results/workload-18035.json').read_text())['scenarios']
 out=ROOT/'first-results';out.mkdir(exist_ok=False);rows=[]
 for index,case in enumerate(cases):
  agents,ops=transform(w,case['delays']);bound=maximize_service(agents,ops,w['jobs'],lag=1,node_limit=100000)
  score=score_schedule(agents,ops,w['jobs'],bound['witness'],lag=1);assert score['service']==bound['lower']
  # A delayed fixed plan is an available schedule, even though it may execute
  # additional late work. Its timely complete-job count cannot exceed an upper bound.
  actual={p:r['completed'] for p,r in case['results'].items()}
  assert max(actual.values())<=bound['upper']
  row=dict(index=index,delays=case['delays'],weight=case['weight'],fixed_service=actual,bound=bound)
  write(out/f'case-{index:02}.json',row);rows.append(row)
 exact=all(r['bound']['status']=='exact' for r in rows);checks=0
 for a in rows:
  for b in rows:
   if a['bound']['status']==b['bound']['status']=='exact' and all(a['delays'][k]<=b['delays'][k] for k in a['delays']):
    assert a['bound']['lower']>=b['bound']['lower'];checks+=1
 target=next(r for r in rows if r['delays']['1-0']==1 and sum(r['delays'].values())==1)
 summary=dict(selected_seed=18035,delay_vectors=64,exact_results=sum(r['bound']['status']=='exact' for r in rows),weighted_lower=sum(r['weight']*r['bound']['lower'] for r in rows),weighted_upper=sum(r['weight']*r['bound']['upper'] for r in rows),weighted_fixed={p:sum(r['weight']*r['fixed_service'][p] for r in rows) for p in ['append','revise']},monotonic_comparisons=checks,single_delay_case=target['index'],single_delay_bound=[target['bound']['lower'],target['bound']['upper']],single_delay_fixed=target['fixed_service'],search_nodes=sum(r['bound']['nodes'] for r in rows))
 write(out/'summary.json',summary)
 for n,h in frozen['prior'].items():assert sha(BASE/n)==h
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
