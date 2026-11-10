from pathlib import Path
import sys,random
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'attainable-service'))
from service import Agent,Operation,score_schedule,maximize_service
TEAM=[Agent('a',0,{'X':1,'Y':1}),Agent('b',2,{'X':1,'Y':1})]
def workload(seed):
 rng=random.Random(seed);ops=[];jobs={}
 for j in range(3):
  release=rng.randrange(4);site=rng.randrange(3);deadline=rng.randrange(5,10);ids=[]
  for stage,k in enumerate(('X','Y')):
   oid=f'{j}-{stage}';ops.append(Operation(oid,site,release,deadline,((k,rng.randrange(1,3)),),tuple(ids)));ids.append(oid)
  jobs[str(j)]=ids
 return ops,jobs

def place(o,t,agents,available,positions,reserved):
 choices=[];checks=0;k,u=o.demands[0]
 for i,a in enumerate(agents):
  checks+=1
  if k in a.refused or a.rates.get(k,0)<=0:continue
  ready=max([t,o.release]+[reserved[p]['finish']+(0 if reserved[p]['crew']==[a.id] else 1) for p in o.predecessors])
  arrival=max(t,available[i])+abs(positions[i]-o.site)
  start=max(ready,arrival);finish=start+(u+a.rates[k]-1)//a.rates[k]
  if finish<=o.deadline:choices.append((finish,a.id,i,start))
 if not choices:return None,checks
 finish,_,i,start=min(choices)
 e=dict(operation=o.id,crew=[agents[i].id],start=start,finish=finish)
 available[i]=finish;positions[i]=o.site;reserved[o.id]=e
 return e,checks

def simulate(ops,jobs,policy,agents=None):
 if policy not in ('stage','whole'):raise ValueError('policy')
 agents=TEAM if agents is None else agents
 available=[0]*len(agents);positions=[a.site for a in agents];reserved={};decisions=[];checks=0;rejections=0
 by={o.id:o for o in ops}
 for t in range(12):
  # Only released job descriptions enter the policy's view.
  visible={j:ids for j,ids in jobs.items() if all(by[k].release<=t for k in ids)}
  while True:
   progress=False
   if policy=='stage':
    candidates=sorted((by[k] for ids in visible.values() for k in ids if k not in reserved and set(by[k].predecessors)<=reserved.keys()),key=lambda o:(o.deadline,len(o.predecessors),o.id))
    for o in candidates:
     e,n=place(o,t,agents,available,positions,reserved);checks+=n
     if e is not None:decisions.append(dict(t=t,operations=[o.id]));progress=True;break
     rejections+=1
   else:
    candidates=sorted((j for j,ids in visible.items() if not any(k in reserved for k in ids)),key=lambda j:(min(by[k].deadline for k in visible[j]),j))
    for j in candidates:
     av=available[:];pos=positions[:];rr=dict(reserved);success=True
     for oid in visible[j]:
      e,n=place(by[oid],t,agents,av,pos,rr);checks+=n
      if e is None:success=False;break
     if success:
      available,positions,reserved=av,pos,rr;decisions.append(dict(t=t,operations=visible[j][:]));progress=True;break
     rejections+=1
   if not progress:break
 events=list(reserved.values());score=score_schedule(agents,ops,jobs,events,lag=1)
 return dict(completed=score['service'],completion_fraction=score['service']/len(jobs),partial=len(score['partial_jobs']),assignment_checks=checks,rejected_proposals=rejections,**score['accounting'],events=events,decisions=decisions)
