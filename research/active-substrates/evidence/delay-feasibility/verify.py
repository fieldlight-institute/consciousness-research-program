"""Check stored witnesses directly, without search or imported solver validation."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
w=json.loads((BASE/'reservation-replanning/evaluation/workload-18035.json').read_text());ops={o['id']:o for o in w['operations']};checked=0
for path in sorted((ROOT/'first-results').glob('case-*.json')):
 row=json.loads(path.read_text());events=row['bound']['witness'];by={e['operation']:e for e in events}
 assert len(events)==len(by)
 for a in w['agents']:
  available=0;site=a['site']
  for e in sorted((e for e in events if e['crew']==[a['id']]),key=lambda e:e['start']):
   o=ops[e['operation']];skill,units=o['demands'][0]
   assert skill not in a['refused'] and a['rates'][skill]==1
   assert e['start']>=max(o['release'],available+abs(site-o['site']))
   assert e['finish']-e['start']==units+row['delays'][o['id']]
   assert e['finish']<=o['deadline']
   for pred in o['predecessors']:
    assert pred in by and e['start']>=by[pred]['finish']+(by[pred]['crew']!=e['crew'])
   available=e['finish'];site=o['site']
 assert all(len(e['crew'])==1 and e['crew'][0] in ['a','b'] for e in events)
 completed=sorted(j for j,ids in w['jobs'].items() if set(ids)<=set(by))
 assert completed==row['bound']['completed_jobs'] and len(completed)==row['bound']['lower'];checked+=1
frozen=json.loads((ROOT/'freeze.json').read_text())
for n,h in frozen['prior'].items():assert hashlib.sha256((BASE/n).read_bytes()).hexdigest()==h
print(json.dumps(dict(witnesses_verified=checked,prior_artifacts_preserved=len(frozen['prior']))))
