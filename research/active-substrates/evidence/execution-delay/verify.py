"""Validate retained realized traces without running replay or either policy."""
from pathlib import Path
import hashlib,json,statistics
ROOT=Path(__file__).resolve().parent
old=ROOT.parent/'reservation-replanning/evaluation'
rows=json.loads((old/'rows.json').read_text());nominal={(r['seed'],r['policy']):r for r in rows}
checks=0;differences=[]
for path in sorted((ROOT/'first-results').glob('workload-*.json')):
 data=json.loads(path.read_text());seed=data['seed'];w=json.loads((old/path.name).read_text());ops={o['id']:o for o in w['operations']};total={p:0. for p in ('append','revise')}
 assert len(data['scenarios'])==64 and len({tuple(sorted(s['delays'].items())) for s in data['scenarios']})==64
 for s in data['scenarios']:
  assert s['weight']==.25**sum(s['delays'].values())*.75**(6-sum(s['delays'].values()))
  for p,r in s['results'].items():
   events={e['operation']:e for e in r['events']};original={e['operation']:e for e in nominal[seed,p]['events']}
   assert events.keys()==original.keys()
   for a in w['agents']:
    prevfinish=0;site=a['site']
    queue=sorted((e for e in r['events'] if e['crew']==[a['id']]),key=lambda e:e['depart'])
    for e in queue:
     oid=e['operation'];n=original[oid];o=ops[oid]
     assert all(e[k]==n[k] for k in ('crew','committed','origin','operation'))
     assert e['depart']>=max(prevfinish,n['depart']) and e['origin']==site
     assert e['start']>=max(n['start'],e['depart']+abs(site-o['site']))
     assert e['finish']-e['start']==n['finish']-n['start']+s['delays'][oid]
     assert all(e['start']>=events[q]['finish']+(events[q]['crew']!=e['crew']) for q in o['predecessors'])
     prevfinish=e['finish'];site=o['site']
   timely={k for k,e in events.items() if e['finish']<=ops[k]['deadline']}
   credit=sorted(j for j,ids in w['jobs'].items() if set(ids)<=timely)
   assert credit==r['completed_jobs'] and len(credit)==r['completed']
   assert r['late_operations']==sorted(set(events)-timely)
   total[p]+=s['weight']*len(credit)/len(w['jobs']);checks+=1
 for p in total:assert abs(total[p]-data['expectations'][p]['completion_fraction'])<1e-12
 differences.append(total['revise']-total['append'])
summary=json.loads((ROOT/'first-results/summary.json').read_text())
assert abs(statistics.mean(differences)-summary['mean_difference'])<1e-12
frozen=json.loads((ROOT/'freeze.json').read_text())
for n,h in frozen['prior'].items():assert hashlib.sha256((ROOT.parent/n).read_bytes()).hexdigest()==h
print(json.dumps(dict(realized_schedules_verified=checks,prior_artifacts_preserved=len(frozen['prior']),mean_reconciled=True)))
