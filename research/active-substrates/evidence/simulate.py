"""AS-01 first implementation: synthetic local job coordination, no model API.

This is a deliberately bounded B/C pilot, not the complete four-condition study.
See IMPLEMENTATION.md for frozen choices and deviations before interpreting output.
"""
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
CONDITIONS = ['B', 'B-long', 'C', 'C-no-propagation', 'C-reset']


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


def simulate(seed, condition, budget=96, detailed=False):
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
            # These agents have no learned policy history. Positions and work in flight
            # are inherited as physical state; only C-reset clears medium history.
            if condition == 'C-reset':
                field = [0.]*N
                written = [-10000]*N
            events.append(dict(t=t, action='replacement', reset=condition == 'C-reset'))
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
            if job_id in active and job_id not in completed:
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
                score = 1/(1+travel+a['cost'])-.35*snapshot[j['site']]
                choices.append((score, -j['deadline'], -j['id'], j, arrival, travel))
            if choices:
                _, _, _, j, arrival, travel = max(choices, key=lambda x: x[:3])
                a['busy'] = (j['id'], j['site'], travel)
                a['arrival'] = arrival
                counters['travel'] += travel
                deposits.append(j['site'])
                if detailed:
                    events.append(dict(t=t, action='claim', agent=a['id'], job=j['id'], arrival=arrival,
                                       signal=snapshot[j['site']]))
            elif t % 5 == a['id'] % 5:
                # Exogenous local exploration, fixed across conditions and independent of demand truth.
                options = sorted(j for j in range(N) if distance(a['site'], j) == 1)
                if options:
                    a['site'] = options[(seed+t+a['id']) % len(options)]
                    counters['travel'] += 1
        for site in deposits:
            field[site] = min(1., field[site]+.5)
            written[site] = t
            counters['writes'] += 1
        if condition.startswith('B'):
            field = [x if t-written[i] < ttl else 0. for i, x in enumerate(field)]
        else:
            old = field[:]
            field = [.88*x for x in old]
            if condition != 'C-no-propagation':
                # Deterministic round-robin bounded edge updates. The full graph is 96 directed edges.
                # Symmetric edge selection and conservative updates avoid negative unstable mixing.
                edges = [(i,j) for i in range(N) for j in NEIGHBORS[i] if i < j]
                count = min(len(edges), budget//2)
                start = (t*max(1,count)) % len(edges)
                for offset in range(count):
                    i,j = edges[(start+offset) % len(edges)]
                    delta = .04*(old[j]-old[i])
                    field[i] += delta
                    field[j] -= delta
                counters['edge_updates'] += 2*count
                counters['scalar_transmissions'] += 2*count
            field = [max(0.,min(1.,x)) for x in field]
        if t % 100 == 0:
            curve.append(dict(t=t, completed=len(completed), eligible=len(eligible)))
            if detailed:
                snapshots.append(dict(t=t, field=field[:], positions=[a['site'] for a in agents]))
    result = dict(seed=seed, condition=condition, budget=budget, task_hash=hash_json(stream),
                  eligible=len(eligible), completed=len(completed & eligible),
                  primary_n=len(primary), primary_done=len(primary & completed),
                  primary_rate=len(primary & completed)/max(1,len(primary)),
                  replacement_rate=len(replacement & completed)/max(1,len(replacement)),
                  agent_completions=completed_by_agent, **counters)
    result['operations'] = sum(counters[k] for k in ['reads','writes','edge_updates'])
    result['operations_per_completion'] = result['operations']/max(1,result['completed'])
    return result, dict(events=events, snapshots=snapshots, curve=curve)


def paired_summary(rows):
    baseline = {(r['seed'],r['budget']): r for r in rows if r['condition'] == 'B'}
    results = []
    for condition in CONDITIONS:
        for budget in sorted(set(r['budget'] for r in rows)):
            group = [r for r in rows if r['condition'] == condition and r['budget'] == budget]
            if not group:
                continue
            differences = [r['primary_rate']-baseline[r['seed'],budget]['primary_rate'] for r in group]
            rng = random.Random(493)
            boots = sorted(statistics.mean(rng.choices(differences,k=len(differences))) for _ in range(5000))
            results.append(dict(condition=condition,budget=budget,n=len(group),
                mean_primary=statistics.mean(r['primary_rate'] for r in group),
                paired_difference=statistics.mean(differences),ci_low=boots[124],ci_high=boots[4874],
                mean_operations=statistics.mean(r['operations'] for r in group),
                mean_collision=statistics.mean(r['collisions'] for r in group),
                mean_replacement=statistics.mean(r['replacement_rate'] for r in group)))
    return results


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--phase',choices=['pilot','evaluation'],default='pilot')
    args = p.parse_args()
    seeds = range(10) if args.phase == 'pilot' else range(100,140)
    out = Path(__file__).parent/args.phase
    out.mkdir(exist_ok=True)
    rows = []
    manifest = dict(phase=args.phase,seeds=list(seeds),conditions=CONDITIONS,budgets=[24,96],
                    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    ticks=TICKS, specification='IMPLEMENTATION.md',
                    status='bounded B/C study; not full AS-01 confirmation')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for seed in seeds:
        for budget in [24,96]:
            for condition in CONDITIONS:
                row, detail = simulate(seed,condition,budget,detailed=(seed == seeds.start and budget == 96))
                rows.append(row)
                if seed == seeds.start and budget == 96:
                    (out/f'trace-{condition}.json').write_text(json.dumps(detail))
        print(f'{args.phase}: seed {seed} complete',flush=True)
    (out/'all-seeds.json').write_text(json.dumps(rows,indent=2))
    summary = paired_summary(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    with (out/'summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]))
        writer.writeheader();writer.writerows(summary)
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
