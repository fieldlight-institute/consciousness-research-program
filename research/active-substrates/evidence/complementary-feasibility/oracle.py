"""Bounded exact nonpreemptive oracle; schedules are evaluator-only."""
from dataclasses import dataclass
from itertools import permutations
from math import ceil
@dataclass(frozen=True)
class Agent:
    id:str
    site:int
    rates:dict
    refused:tuple=()
@dataclass(frozen=True)
class Operation:
    id:str
    site:int
    release:int
    deadline:int
    demands:tuple
    predecessors:tuple=()
def validate(agents,ops,lag):
    if not 1<=len(agents)<=4 or not 1<=len(ops)<=8:raise ValueError('bounded size')
    if type(lag)!=int or lag<0:raise ValueError('handoff latency')
    if len({a.id for a in agents})!=len(agents) or len({o.id for o in ops})!=len(ops):raise ValueError('duplicate ID')
    for a in agents:
        if type(a.site)!=int or any(type(v)!=int or v<0 for v in a.rates.values()):raise ValueError('agent rates/site')
    by={o.id:o for o in ops}
    for o in ops:
        if any(type(v)!=int for v in (o.site,o.release,o.deadline)) or o.release<0 or o.deadline<o.release:raise ValueError('operation time/site')
        if not o.demands or any(type(u)!=int or u<=0 for _,u in o.demands):raise ValueError('demands')
        if len(set(o.predecessors))!=len(o.predecessors) or any(p not in by or by[p].site!=o.site for p in o.predecessors):raise ValueError('predecessor')
    done=set()
    while True:
        new={o.id for o in ops if set(o.predecessors)<=done}-done
        if not new:break
        done|=new
    if len(done)!=len(ops):raise ValueError('cyclic precedence')
def capacity(agents):
    skills=sorted({k for a in agents for k in a.rates})
    return dict(potential={k:sum(a.rates.get(k,0) for a in agents) for k in skills},usable={k:sum(a.rates.get(k,0) for a in agents if k not in a.refused) for k in skills},sum_individual_max_rates=sum(max([v for k,v in a.rates.items() if k not in a.refused]+[0]) for a in agents),agents=len(agents))
def crews(agents,o):
    for ids in permutations(range(len(agents)),len(o.demands)):
        if all(agents[i].rates.get(k,0)>0 and k not in agents[i].refused for i,(k,_) in zip(ids,o.demands)):
            yield ids,max((u+agents[i].rates[k]-1)//agents[i].rates[k] for i,(k,u) in zip(ids,o.demands))
def solve(agents,ops,lag=0,node_limit=100000):
    validate(agents,ops,lag)
    if type(node_limit)!=int or node_limit<1:raise ValueError('node limit')
    options={o.id:list(crews(agents,o)) for o in ops};nodes=0;cut=False;best=None;best_time=float('inf')
    def search(done,available,positions,events):
        nonlocal nodes,cut,best,best_time
        if nodes>=node_limit:cut=True;return
        nodes+=1
        if len(done)==len(ops):
            end=max(x['finish'] for x in events)
            if end<best_time:best_time=end;best=[dict(x) for x in events]
            return
        if max(available)>=best_time:return
        for o in ops:
            if o.id in done or not set(o.predecessors)<=done.keys():continue
            for ids,duration in options[o.id]:
                crew=tuple(agents[i].id for i in ids)
                ready=max([o.release]+[done[p]['finish']+(lag if set(done[p]['crew'])!=set(crew) else 0) for p in o.predecessors])
                start=max([ready]+[available[i]+abs(positions[i]-o.site) for i in ids]);finish=start+duration
                if finish>o.deadline or finish>=best_time:continue
                e=dict(operation=o.id,crew=list(crew),start=start,finish=finish)
                av=list(available);pos=list(positions)
                for i in ids:av[i]=finish;pos[i]=o.site
                search({**done,o.id:e},av,pos,events+[e])
    search({},[0]*len(agents),[a.site for a in agents],[])
    result=dict(status='feasible' if best is not None else 'unknown' if cut else 'infeasible',search_complete=not cut,nodes=nodes,minimum_makespan=best_time if best is not None and not cut else None,witness=best)
    if best is not None:result['accounting']=verify(agents,ops,lag,best)
    return result
def verify(agents,ops,lag,events):
    validate(agents,ops,lag);aa={a.id:a for a in agents};oo={o.id:o for o in ops}
    if len(events)!=len(ops) or {e['operation'] for e in events}!=set(oo):raise ValueError('coverage')
    ee={e['operation']:e for e in events};travel=0;occupancy=0
    for e in events:
        o=oo[e['operation']];crew=e['crew']
        if len(crew)!=len(o.demands) or len(set(crew))!=len(crew) or any(i not in aa for i in crew):raise ValueError('crew')
        durations=[]
        for i,(k,u) in zip(crew,o.demands):
            a=aa[i]
            if k in a.refused or a.rates.get(k,0)<=0:raise ValueError('refusal/skill')
            durations.append((u+a.rates[k]-1)//a.rates[k])
        if any(type(e[k])!=int for k in ('start','finish')) or e['start']<o.release or e['finish']>o.deadline or e['finish']-e['start']!=max(durations):raise ValueError('time')
        for p in o.predecessors:
            required=ee[p]['finish']+(lag if set(ee[p]['crew'])!=set(crew) else 0)
            if e['start']<required:raise ValueError('precedence/handoff')
        occupancy+=len(crew)*(e['finish']-e['start'])
    for a in agents:
        t=0;site=a.site
        for e in sorted((e for e in events if a.id in e['crew']),key=lambda e:e['start']):
            distance=abs(site-oo[e['operation']].site)
            if e['start']<t+distance:raise ValueError('travel/overlap')
            travel+=distance;t=e['finish'];site=oo[e['operation']].site
    return dict(work_occupancy_ticks=occupancy,travel_ticks=travel,elapsed_ticks=max(e['finish'] for e in events))
