"""PA-01 participant boundary authority; see SPECIFICATION.md. Fork of preserved AS-01."""
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path

TICKS = 3000
N = 24
AGENTS = 12
from participant import Participant,CONDITIONS
from medium import Medium


def hash_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def task_stream(seed):
    rng = random.Random(seed)
    jobs = []
    for t in range(TICKS):
        if rng.random() < .8:
            # Demand moves to the other half of the layout after tick 1000.
            preferred = range(12) if t < 1000 else range(12, 24)
            site = rng.choice(list(preferred)) if rng.random() < .8 else rng.randrange(N)
            jobs.append(dict(id=len(jobs), born=t, site=site, skill=rng.randrange(4), deadline=t+rng.randrange(12, 31)))
    return jobs


def distance(a, b):
    return abs(a % 6-b % 6)+abs(a//6-b//6)


NEIGHBORS = [[(i-2) % N, (i-1) % N, (i+1) % N, (i+2) % N] for i in range(N)]
VISIBLE = [[j for j in range(N) if distance(i, j) <= 2] for i in range(N)]


def simulate(seed, condition, budget=96, detailed=False, replay=None):
    assert condition in CONDITIONS and budget==96
    medium=Medium(NEIGHBORS)
    participants=[Participant() for _ in range(AGENTS)]
    coupling_trace=[]; reliability_trace=[]; boundary_reads=0; boundary_writes=0
    if condition=="Yoked":
        if replay is None or len(replay)!=TICKS//25 or any(len(row)!=AGENTS for row in replay): raise ValueError("replay shape")
    eligibility={}
    eligibility_reads=0
    rng = random.Random(seed+90000)
    stream = task_stream(seed)
    jobs_by_tick = {}
    for j in stream:
        jobs_by_tick.setdefault(j['born'], []).append(j)
    active = {}
    agents = [dict(id=i, site=rng.randrange(N), skill=i % 4, busy=None, arrival=0,
                   cost=1+i % 3, active=True) for i in range(AGENTS)]
    field = [0.] * N
    written = [-10000] * N
    completed = set()
    eligible = set()
    completed_by_agent = [0]*AGENTS
    counters = dict(reads=0, writes=0, edge_updates=0, scalar_transmissions=0,
                    collisions=0, wasted_travel=0, travel=0, refusals=0, prohibited_executions=0)
    events = []
    snapshots = []
    curve = []
    primary = set()
    replacement = set()
    ttl = 24 if condition == 'B-long' else 8
    for t in range(TICKS):
        if t == 1800:
            for a in agents[:3]:
                a['active'] = False
                a['busy'] = None
            events.append(dict(t=t, action='remove', agents=[0, 1, 2]))
        if t == 2400:
            eligibility.clear()
            for p in participants:p.reset_history()
            # These agents have no learned policy history. Positions and work in flight
            # are inherited as physical state; only C-reset clears medium history.
            if condition == 'D-reset':
                field = [0.]*N
                medium.reset()
                written = [-10000]*N
            events.append(dict(t=t, action='replacement', reset=condition == 'D-reset'))
        if t%25==0:
            estimates=[]
            for a,p in zip(agents,participants):
                if a["active"]:
                    estimates.append(p.revise(t,a["id"],condition,replay[t//25][a["id"]] if replay is not None else None))
            coupling_trace.append([p.g for p in participants])
            if detailed:reliability_trace.append(dict(t=t,estimates=estimates))
        for job in jobs_by_tick.get(t, []):
            active[job['id']] = job
            # Eligibility: an active, non-refusing agent has the required skill at arrival.
            # This is skill eligibility, not a global optimal-schedule feasibility oracle.
            feasible = any(a['active'] and a['skill'] == job['skill'] and not (a['id'] < 4 and job['skill'] == 0) for a in agents)
            if feasible:
                eligible.add(job['id'])
                if 1000 <= t < 1500:
                    primary.add(job['id'])
                if 2400 <= t < 2900:
                    replacement.add(job['id'])
        active = {k: j for k, j in active.items() if j['deadline'] >= t and k not in completed}
        # Arrivals are resolved in a fixed rotating order, not by condition-specific RNG.
        order = sorted(agents, key=lambda a: (a['id']-t) % AGENTS)
        for a in order:
            if not a['active'] or a['busy'] is None or a['arrival'] > t:
                continue
            job_id, target, travel = a['busy']
            a['site'] = target
            success=job_id in active and job_id not in completed
            participants[a['id']].arrive(success)
            if True:
                medium.feedback(target,eligibility.pop(a['id'],{}),success)
            else:
                eligibility.pop(a['id'],None)
            if success:
                job = active[job_id]
                assert a['skill'] == job['skill']
                assert not (a['id'] < 4 and job['skill'] == 0)
                completed.add(job_id)
                completed_by_agent[a['id']] += 1
                if detailed:
                    events.append(dict(t=t, action='complete', agent=a['id'], job=job_id))
            else:
                counters['collisions'] += 1
                counters['wasted_travel'] += travel
            a['busy'] = None
        # All agents read the same pre-decision snapshot. No sequential claim advantage.
        snapshot = field[:]
        deposits = []
        for a in agents:
            if not a['active'] or a['busy'] is not None:
                continue
            choices = []
            for j in active.values():
                if j['id'] in completed or j['site'] not in VISIBLE[a['site']] or j['skill'] != a['skill']:
                    continue
                if a['id'] < 4 and j['skill'] == 0:
                    counters['refusals'] += 1
                    continue
                travel = distance(a['site'], j['site'])
                arrival = t+travel+a['cost']
                if arrival > j['deadline']:
                    continue
                counters['reads'] += 1
                # Same policy in each condition: nearby demand discounted by predicted congestion.
                score = 1/(1+travel+a['cost'])-.35*participants[a['id']].g*snapshot[j['site']]
                boundary_reads+=1
                choices.append((score, -j['deadline'], -j['id'], j, arrival, travel))
            if choices:
                _, _, _, j, arrival, travel = max(choices, key=lambda x: x[:3])
                participants[a['id']].commit(snapshot[j['site']])
                eligibility[a['id']]=medium.eligibility(j['site'])
                eligibility_reads+=len(eligibility[a['id']])
                a['busy'] = (j['id'], j['site'], travel)
                a['arrival'] = arrival
                counters['travel'] += travel
                deposits.append((j['site'],participants[a['id']].g))
                if detailed:
                    events.append(dict(t=t, action='claim', agent=a['id'], job=j['id'], arrival=arrival,
                                       signal=snapshot[j['site']]))
            elif t % 5 == a['id'] % 5:
                # Exogenous local exploration, fixed across conditions and independent of demand truth.
                options = sorted(j for j in range(N) if distance(a['site'], j) == 1)
                if options:
                    a['site'] = options[(seed+t+a['id']) % len(options)]
                    counters['travel'] += 1
        for site,g in deposits:
            field[site] = min(1., field[site]+.5*g)
            boundary_writes+=1
            written[site] = t
            counters['writes'] += 1
        field=medium.step(field,True)
        counters['edge_updates']+=96
        counters['scalar_transmissions']+=96
        if t % 100 == 0:
            curve.append(dict(t=t, completed=len(completed), eligible=len(eligible)))
            if detailed:
                snapshots.append(dict(t=t, field=field[:], weights=[[i,j,w] for (i,j),w in medium.weights.items()], positions=[a['site'] for a in agents]))
    result = dict(seed=seed, condition=condition, budget=budget, task_hash=hash_json(stream),
                  eligible=len(eligible), completed=len(completed & eligible),
                  primary_n=len(primary), primary_done=len(primary & completed),
                  primary_rate=len(primary & completed)/max(1,len(primary)),
                  replacement_rate=len(replacement & completed)/max(1,len(replacement)),
                  agent_completions=completed_by_agent, **counters)
    result.update(feedback_updates=medium.feedback_updates,relaxations=medium.relaxations,receipt_writes=medium.receipt_writes,eligibility_reads=eligibility_reads,weight_min=min(medium.weights.values()),weight_max=max(medium.weights.values()),weight_mean=sum(medium.weights.values())/len(medium.weights))
    result['operations'] = sum(counters[k] for k in ['reads','writes','edge_updates'])
    result['operations_per_completion'] = result['operations']/max(1,result['completed'])
    result.update(boundary_read_multiplications=boundary_reads,boundary_deposit_multiplications=boundary_writes,agreement_records=sum(p.recorded for p in participants),window_entries_scanned=sum(p.scanned for p in participants),reserved_scan_slots=sum(p.allowance for p in participants),reliability_summaries=sum(p.summaries for p in participants),coupling_changes=sum(p.writes for p in participants),final_couplings=[p.g for p in participants])
    return result, dict(events=events, snapshots=snapshots, curve=curve, couplings=coupling_trace,reliability=reliability_trace)

