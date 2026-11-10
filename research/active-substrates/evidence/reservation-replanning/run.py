from pathlib import Path
from dataclasses import asdict
import json,hashlib,sys,statistics,random
from study import workload,simulate,TEAM,maximize_service
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def sources():return {n:sha(ROOT/n) for n in ('SPECIFICATION.md','study.py','test_replanning.py','run.py')}
def main():
 phase=sys.argv[1];assert phase in ('freeze','pilot','evaluation')
 if phase=='freeze':
  prior={str(p.relative_to(ROOT.parent)):sha(p) for p in ROOT.parent.rglob('*') if p.is_file() and ROOT not in p.parents and '__pycache__' not in p.parts}
  write(ROOT/'freeze.json',dict(sources=sources(),preserved=prior));print('frozen',len(prior));return
 frozen=json.loads((ROOT/'freeze.json').read_text());assert sources()==frozen['sources']
 def verify():
  for n,h in frozen['preserved'].items():assert sha(ROOT.parent/n)==h,n
 verify();out=ROOT/phase;out.mkdir(exist_ok=False);seeds=range(17000,17010) if phase=='pilot' else range(18000,18040);rows=[];bounds=[]
 for seed in seeds:
  ops,jobs=workload(seed);bound=maximize_service(TEAM,ops,jobs,lag=1);bounds.append(dict(seed=seed,**bound))
  write(out/f'workload-{seed}.json',dict(agents=[asdict(a) for a in TEAM],operations=[asdict(o) for o in ops],jobs=jobs))
  for policy,budget in [('append',0),('revise',4)]:
   r=simulate(ops,jobs,budget);assert r['completed']<=bound['upper'];assert r['cancellation_units']<=budget;rows.append(dict(seed=seed,policy=policy,**r))
 write(out/'rows.json',rows);write(out/'bounds.json',bounds)
 by={(r['seed'],r['policy']):r for r in rows};diff=[by[s,'revise']['completion_fraction']-by[s,'append']['completion_fraction'] for s in seeds];rng=random.Random(73023)
 boots=sorted(statistics.mean(rng.choices(diff,k=len(diff))) for _ in range(10000))
 metrics=['completed','completion_fraction','partial','assignment_checks','revision_proposals','revisions','cancellation_units','work_occupancy_ticks','travel_ticks']
 summary=dict(paired_seeds=len(seeds),primary=dict(mean=statistics.mean(diff),ci95=[boots[249],boots[9749]]),policies={p:{m:statistics.mean(r[m] for r in rows if r['policy']==p) for m in metrics} for p in ('append','revise')},exact_oracles=sum(b['status']=='exact' for b in bounds),oracle_lower_mean=statistics.mean(b['lower'] for b in bounds),oracle_upper_mean=statistics.mean(b['upper'] for b in bounds),revision_wins=sum(d>0 for d in diff),ties=sum(d==0 for d in diff),revision_losses=sum(d<0 for d in diff),source_hashes=sources())
 write(out/'summary.json',summary);verify();print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
