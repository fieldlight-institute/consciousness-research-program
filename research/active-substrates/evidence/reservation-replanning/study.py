from pathlib import Path
from copy import deepcopy
import sys,importlib.util
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'reservation-lifecycle'))
from lifecycle import propose,apply,validate_snapshot
from service import Agent,Operation,score_schedule,maximize_service
spec=importlib.util.spec_from_file_location('composite_reference',BASE/'composite-reservations/study.py');reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
TEAM=reference.TEAM;workload=reference.workload

def fill(agents,ops,jobs,events,t):
 by={o.id:o for o in ops};reserved={e['operation']:deepcopy(e) for e in events};av=[];pos=[];checks=0
 for a in agents:
  queue=sorted((e for e in events if e['crew']==[a.id]),key=lambda e:e['finish'])
  av.append(queue[-1]['finish'] if queue else 0);pos.append(by[queue[-1]['operation']].site if queue else a.site)
 while True:
  progress=False
  for j in sorted(jobs,key=lambda j:(min(by[k].deadline for k in jobs[j]),j)):
   missing=[k for k in jobs[j] if k not in reserved]
   if not missing:continue
   aa=av[:];pp=pos[:];rr=deepcopy(reserved);ok=True
   for oid in missing:
    o=by[oid];k,u=o.demands[0];choices=[]
    for i,a in enumerate(agents):
     checks+=1
     if k in a.refused or a.rates.get(k,0)<=0:continue
     depart=max(t,aa[i]);ready=max([t,o.release]+[rr[p]['finish']+(0 if rr[p]['crew']==[a.id] else 1) for p in o.predecessors])
     start=max(ready,depart+abs(pp[i]-o.site));finish=start+(u+a.rates[k]-1)//a.rates[k]
     if finish<=o.deadline:choices.append((finish,a.id,i,start,depart))
    if not choices:ok=False;break
    finish,_,i,start,depart=min(choices)
    rr[oid]=dict(operation=oid,crew=[agents[i].id],committed=t,origin=pp[i],depart=depart,start=start,finish=finish);aa[i]=finish;pp[i]=o.site
   if ok:av,pos,reserved=aa,pp,rr;progress=True;break
  if not progress:break
 return list(reserved.values()),checks

def simulate(ops,jobs,budget=0,agents=None):
 if budget not in (0,4):raise ValueError('budget')
 agents=TEAM if agents is None else agents;events=[];audits=[];traces=[];spent=0;checks=0;proposals=0
 by={o.id:o for o in ops};previous=set()
 for t in range(12):
  visible={j:ids for j,ids in jobs.items() if all(by[k].release<=t for k in ids)}
  if not visible:continue
  vo=[o for o in ops if any(o.id in ids for ids in visible.values())]
  baseline,n=fill(agents,vo,visible,events,t);checks+=n
  best=baseline;best_score=score_schedule(agents,vo,visible,baseline,1)['service'];best_key=None;chosen=None
  if budget and set(visible)!=previous:
   seen=set()
   for e in events:
    if e['depart']<=t:continue
    p=propose(agents,vo,visible,events,[e['operation']],t);key=tuple(p['withdrawals'])
    if key in seen:continue
    seen.add(key);proposals+=1
    if p['blockers'] or spent+len(key)>budget:continue
    withdrawn=apply(agents,vo,visible,events,p,[a.id for a in agents],t)
    candidate,n=fill(agents,vo,visible,withdrawn['reservations'],t);checks+=n
    count=score_schedule(agents,vo,visible,candidate,1)['service'];rank=(-count,len(key),key)
    if count>score_schedule(agents,vo,visible,baseline,1)['service'] and (best_key is None or rank<best_key):best=candidate;best_score=count;best_key=rank;chosen=withdrawn['audit']
  before=deepcopy(events)
  if chosen is not None:spent+=chosen['withdrawal_units'];audits.append(chosen)
  for old in before:
   if old['depart']<=t:assert old in best
  events=best;validate_snapshot(agents,vo,visible,events,t)
  traces.append(dict(t=t,before=before,after=deepcopy(events),revision=chosen,visible_jobs=sorted(visible)));previous=set(visible)
 score=score_schedule(agents,ops,jobs,events,1)
 return dict(completed=score['service'],completion_fraction=score['service']/len(jobs),partial=len(score['partial_jobs']),assignment_checks=checks,revision_proposals=proposals,revisions=len(audits),cancellation_units=spent,**score['accounting'],events=events,audits=audits,traces=traces)
