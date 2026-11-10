from pathlib import Path
import hashlib,itertools,json,random,statistics,sys
from replay import replay
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'reservation-replanning/evaluation'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def sources():return {n:sha(ROOT/n) for n in ('SPECIFICATION.md','replay.py','test_replay.py','run.py')}
def run():
 if sys.argv[1]=='freeze':
  prior={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
  write(ROOT/'freeze.json',dict(sources=sources(),prior=prior));print('frozen',len(prior));return
 frozen=json.loads((ROOT/'freeze.json').read_text());assert sources()==frozen['sources']
 for n,h in frozen['prior'].items():assert sha(ROOT.parent/n)==h
 out=ROOT/'first-results';out.mkdir(exist_ok=False)
 rows=json.loads((OLD/'rows.json').read_text());by={(r['seed'],r['policy']):r for r in rows};paired=[];zero=0
 for seed in range(18000,18040):
  w=json.loads((OLD/f'workload-{seed}.json').read_text());ids=sorted(o['id'] for o in w['operations']);scenarios=[]
  totals={p:dict(completed=0.,completion_fraction=0.,late_operations=0.,work_ticks=0.,last_finish=0.) for p in ('append','revise')}
  for bits in itertools.product((0,1),repeat=len(ids)):
   weight=.25**sum(bits)*.75**(len(ids)-sum(bits));delays=dict(zip(ids,bits));results={}
   for p in totals:
    r=replay(w,by[seed,p]['events'],delays);results[p]=r
    if not any(bits):
     assert r['completed']==by[seed,p]['completed']
     assert r['events']==sorted(by[seed,p]['events'],key=lambda e:e['operation']);zero+=1
    for m in totals[p]:totals[p][m]+=weight*(len(r[m]) if m=='late_operations' else r[m])
   scenarios.append(dict(delays=delays,weight=weight,results=results))
  assert sum(s['weight'] for s in scenarios)==1
  write(out/f'workload-{seed}.json',dict(seed=seed,scenarios=scenarios,expectations=totals))
  paired.append(dict(seed=seed,policies=totals,difference=totals['revise']['completion_fraction']-totals['append']['completion_fraction']))
 diff=[r['difference'] for r in paired];rng=random.Random(74022);boots=sorted(statistics.mean(rng.choices(diff,k=40)) for _ in range(10000))
 summary=dict(workloads=40,paired_delay_vectors=2560,replayed_schedules=5120,zero_delay_exact_matches=zero,mean_difference=statistics.mean(diff),ci95=[boots[249],boots[9749]],positive=sum(d>1e-12 for d in diff),ties=sum(abs(d)<=1e-12 for d in diff),negative=sum(d< -1e-12 for d in diff),policies={p:{m:statistics.mean(r['policies'][p][m] for r in paired) for m in paired[0]['policies'][p]} for p in ('append','revise')})
 write(out/'paired.json',paired);write(out/'summary.json',summary)
 for n,h in frozen['prior'].items():assert sha(ROOT.parent/n)==h
 print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
