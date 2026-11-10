"""Synthetic, pure withdrawal transactions with explicit travel commitment."""
from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'attainable-service'))
from service import Agent,Operation,score_schedule

def fingerprint(agents,ops,jobs,events):
    state=dict(agents=[asdict(a) for a in agents],operations=[asdict(o) for o in ops],jobs=jobs,reservations=events)
    return hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()

def validate_snapshot(agents,ops,jobs,events,now,lag=1):
    if type(now)!=int or now<0:raise ValueError('invalid decision time')
    if any(len(o.demands)!=1 for o in ops):raise ValueError('single-agent operations only')
    score_schedule(agents,ops,jobs,events,lag=lag)
    by={o.id:o for o in ops};booked={e['operation']:e for e in events}
    for e in events:
        if len(e['crew'])!=1:raise ValueError('single-agent reservation only')
        if any(type(e.get(k))!=int for k in ('committed','depart','origin')):raise ValueError('explicit physical state required')
        if not by[e['operation']].release<=e['committed']<=now:raise ValueError('unreleased or future commitment')
        if not e['committed']<=e['depart']<=e['start']:raise ValueError('departure timing')
        if any(booked[p]['committed']>e['committed'] for p in by[e['operation']].predecessors):raise ValueError('unbooked predecessor at commitment')
    for a in agents:
        finish=0;site=a.site;prior_commit=0
        for e in sorted((e for e in events if e['crew']==[a.id]),key=lambda e:e['depart']):
            if e['origin']!=site or e['depart']<finish:raise ValueError('queue origin/overlap')
            if e['committed']<prior_commit:raise ValueError('queue insertion is not append-only')
            if e['start']<e['depart']+abs(site-by[e['operation']].site):raise ValueError('physical arrival')
            finish=e['finish'];site=by[e['operation']].site;prior_commit=e['committed']

def propose(agents,ops,jobs,events,requested,now,lag=1):
    validate_snapshot(agents,ops,jobs,events,now,lag)
    ids={e['operation'] for e in events};remove=set(requested)
    if not remove or not remove<=ids:raise ValueError('unknown or empty withdrawal')
    by={o.id:o for o in ops}
    changed=True
    while changed:
        before=set(remove)
        for e in events:
            if set(by[e['operation']].predecessors)&remove:remove.add(e['operation'])
        for a in agents:
            tail=False
            for e in sorted((e for e in events if e['crew']==[a.id]),key=lambda e:e['depart']):
                tail=tail or e['operation'] in remove
                if tail:remove.add(e['operation'])
        changed=before!=remove
    removed=[e for e in events if e['operation'] in remove]
    return dict(snapshot=fingerprint(agents,ops,jobs,events),now=now,lag=lag,requested=sorted(set(requested)),withdrawals=sorted(remove),affected_agents=sorted({e['crew'][0] for e in removed}),blockers=sorted(e['operation'] for e in removed if e['depart']<=now))

def apply(agents,ops,jobs,events,proposal,authorized_agents,now,lag=1):
    if proposal['now']!=now or proposal['lag']!=lag or proposal['snapshot']!=fingerprint(agents,ops,jobs,events):raise ValueError('stale proposal')
    fresh=propose(agents,ops,jobs,events,proposal['requested'],now,lag)
    if fresh!=proposal:raise ValueError('altered proposal')
    if fresh['blockers']:raise ValueError('withdrawal reaches departed work')
    if not set(fresh['affected_agents'])<=set(authorized_agents):raise ValueError('missing affected-agent authority')
    removed=[e for e in events if e['operation'] in fresh['withdrawals']]
    kept=deepcopy([e for e in events if e['operation'] not in fresh['withdrawals']])
    validate_snapshot(agents,ops,jobs,kept,now,lag)
    audit=dict(before=fresh['snapshot'],after=fingerprint(agents,ops,jobs,kept),now=now,requested=fresh['requested'],withdrawals=fresh['withdrawals'],affected_agents=fresh['affected_agents'],withdrawal_units=len(removed),removed_future_work_ticks=sum(e['finish']-e['start'] for e in removed))
    return dict(reservations=kept,audit=audit)
