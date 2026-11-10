"""Fixed single-agent operation plans under nonnegative work overruns."""
from copy import deepcopy

def replay(workload, events, delays, lag=1):
    ops={o['id']:o for o in workload['operations']}
    agents={a['id']:a for a in workload['agents']}
    if set(delays)!=set(ops) or any(type(d)!=int or d<0 for d in delays.values()):
        raise ValueError('one nonnegative integer delay per offered operation required')
    if type(lag)!=int or lag<0: raise ValueError('invalid lag')
    booked={e['operation']:e for e in events}
    if len(booked)!=len(events) or not set(booked)<=set(ops):raise ValueError('invalid operation set')
    previous={}
    for aid in agents:
        queue=sorted((e for e in events if e['crew']==[aid]),key=lambda e:(e['depart'],e['operation']))
        prior=None
        for e in queue:
            previous[e['operation']]=prior;prior=e['operation']
    for oid,e in booked.items():
        if len(e['crew'])!=1 or e['crew'][0] not in agents:raise ValueError('single known agent required')
        if not set(ops[oid]['predecessors'])<=set(booked):raise ValueError('missing predecessor')
        if any(type(e[k])!=int for k in ('depart','start','finish','committed','origin')):raise ValueError('integer timestamps required')
        if not ops[oid]['release']<=e['committed']<=e['depart']<=e['start']<e['finish']:raise ValueError('invalid nominal timing')
        skill,units=ops[oid]['demands'][0];a=agents[e['crew'][0]]
        if len(ops[oid]['demands'])!=1 or skill in a['refused'] or a['rates'].get(skill,0)<=0:raise ValueError('invalid capability')
        if e['finish']-e['start']!=(units+a['rates'][skill]-1)//a['rates'][skill]:raise ValueError('nominal duration')
    realized={};pending=set(booked)
    while pending:
        ready=sorted(oid for oid in pending if set(ops[oid]['predecessors'])<=set(realized) and (previous[oid] is None or previous[oid] in realized))
        if not ready:raise ValueError('queue/dependency cycle')
        for oid in ready:
            e=booked[oid];o=ops[oid];prior=previous[oid];aid=e['crew'][0]
            origin=ops[prior]['site'] if prior else agents[aid]['site']
            if origin!=e['origin']:raise ValueError('nominal queue origin')
            if prior and e['depart']<booked[prior]['finish']:raise ValueError('nominal overlap')
            arrival=e['depart']+abs(origin-o['site'])
            pred_nominal=[booked[p]['finish']+(lag if booked[p]['crew']!=e['crew'] else 0) for p in o['predecessors']]
            if e['start']<max([arrival]+pred_nominal):raise ValueError('nominal physical violation')
            depart=max(e['depart'],realized[prior]['finish'] if prior else 0)
            start=max([e['start'],depart+abs(origin-o['site'])]+[realized[p]['finish']+(lag if realized[p]['crew']!=e['crew'] else 0) for p in o['predecessors']])
            actual=deepcopy(e);actual.update(depart=depart,start=start,finish=start+e['finish']-e['start']+delays[oid])
            realized[oid]=actual;pending.remove(oid)
    timely={oid for oid,e in realized.items() if e['finish']<=ops[oid]['deadline']}
    complete=[j for j,ids in workload['jobs'].items() if set(ids)<=timely]
    return dict(completed=len(complete),completion_fraction=len(complete)/len(workload['jobs']),completed_jobs=sorted(complete),late_operations=sorted(set(realized)-timely),work_ticks=sum(e['finish']-e['start'] for e in realized.values()),last_finish=max([0]+[e['finish'] for e in realized.values()]),events=[realized[k] for k in sorted(realized)])
