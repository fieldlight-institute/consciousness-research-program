"""Count whole jobs, close prerequisites, and preserve incomplete-search bounds."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'complementary-feasibility'))
from oracle import Agent,Operation,validate,solve,verify
from itertools import combinations

def validate_jobs(agents,ops,jobs,lag):
    validate(agents,ops,lag)
    if not isinstance(jobs,dict) or not 1<=len(jobs)<=8:raise ValueError('job count')
    flat=[]
    for jid,ids in jobs.items():
        if not isinstance(jid,str) or not ids or len(set(ids))!=len(ids):raise ValueError('job definition')
        flat.extend(ids)
    if len(flat)!=len(set(flat)) or set(flat)!={o.id for o in ops}:raise ValueError('jobs must partition operations')

def closure(ops,ids):
    by={o.id:o for o in ops};done=set(ids);pending=list(ids)
    while pending:
        oid=pending.pop()
        for pred in by[oid].predecessors:
            if pred not in done:done.add(pred);pending.append(pred)
    return done

def score_schedule(agents,ops,jobs,events,lag=0):
    validate_jobs(agents,ops,jobs,lag)
    ids={e['operation'] for e in events}
    if not ids<={o.id for o in ops} or len(ids)!=len(events):raise ValueError('unknown or repeated operation')
    if closure(ops,ids)!=ids:raise ValueError('missing prerequisite')
    accounting=verify(agents,[o for o in ops if o.id in ids],lag,events) if ids else dict(work_occupancy_ticks=0,travel_ticks=0,elapsed_ticks=0)
    completed=sorted(j for j,required in jobs.items() if set(required)<=ids)
    return dict(completed_jobs=completed,service=len(completed),partial_jobs=sorted(j for j,required in jobs.items() if set(required)&ids and not set(required)<=ids),accounting=accounting)

def maximize_service(agents,ops,jobs,lag=0,node_limit=100000,per_candidate_limit=None):
    validate_jobs(agents,ops,jobs,lag)
    if type(node_limit)!=int or node_limit<1:raise ValueError('node limit')
    if per_candidate_limit is not None and (type(per_candidate_limit)!=int or per_candidate_limit<1):raise ValueError('candidate limit')
    ids=sorted(jobs);unique={}
    for size in range(1,len(ids)+1):
        for chosen in combinations(ids,size):
            needed=closure(ops,{o for j in chosen for o in jobs[j]})
            credit=sum(set(required)<=needed for required in jobs.values())
            unique[tuple(sorted(needed))]=credit
    candidates=sorted(unique.items(),key=lambda x:(-x[1],x[0]));remaining=node_limit;tested=[];unresolved=[];best=[];lower=0
    for index,(needed,credit) in enumerate(candidates):
        if credit<=lower:break
        if remaining==0:
            unresolved.extend(v for _,v in candidates[index:] if v>lower);break
        allowance=min(remaining,per_candidate_limit or remaining)
        result=solve(agents,[o for o in ops if o.id in needed],lag,node_limit=allowance);remaining-=result['nodes']
        tested.append(dict(operations=list(needed),potential_service=credit,status=result['status'],nodes=result['nodes'],search_complete=result['search_complete']))
        if result['status']=='feasible':
            score=score_schedule(agents,ops,jobs,result['witness'],lag)
            assert score['service']==credit
            lower=credit;best=result['witness']
        elif result['status']=='unknown':unresolved.append(credit)
    upper=max([lower]+unresolved)
    score=score_schedule(agents,ops,jobs,best,lag)
    return dict(status='exact' if lower==upper else 'bounded',lower=lower,upper=upper,completed_jobs=score['completed_jobs'],partial_jobs=score['partial_jobs'],witness=best,accounting=score['accounting'],nodes=node_limit-remaining,candidate_closures=len(candidates),tested_candidates=tested,unresolved_service_bounds=unresolved)
