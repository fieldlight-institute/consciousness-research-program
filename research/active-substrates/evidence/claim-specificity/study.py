"""Separate synthetic claim-specificity mechanism study; see SPECIFICATION.md."""
import importlib.util
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent / 'simulate.py'
_spec = importlib.util.spec_from_file_location('first_as01', _BASE)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
random, N, AGENTS = base.random, base.N, base.AGENTS
task_stream, hash_json, distance, VISIBLE = base.task_stream, base.hash_json, base.distance, base.VISIBLE
CONDITIONS = ['no-veto', 'site-veto', 'skill-site-veto', 'job-veto']


def claim_blocks(records, job, condition):
    # Evaluate every record: consistent logical comparison accounting, no early exit.
    matches = []
    for r in records:
        site = r['site'] == job['site']
        skill = r['skill'] == job['skill']
        exact = r['job'] == job['id']
        matches.append({'no-veto': False, 'site-veto': site,
                        'skill-site-veto': site and skill,
                        'job-veto': site and exact}[condition])
    return any(matches)


def simulate(seed, condition, detailed=False, stream_override=None, positions=None, ticks=3000):
    assert condition in CONDITIONS
    rng = random.Random(seed+90000)
    stream = task_stream(seed) if stream_override is None else stream_override
    jobs_by_tick = {}
    for j in stream:
        jobs_by_tick.setdefault(j['born'], []).append(j)
    active = {}
    agents = [dict(id=i, site=rng.randrange(N), skill=i % 4, busy=None, arrival=0,
                   cost=1+i % 3, active=True) for i in range(AGENTS)]
    if positions is not None:
        for a, site in zip(agents, positions):
            a['site'] = site
    board = {}
    completed = set()
    eligible = set()
    completed_by_agent = [0]*AGENTS
    counters = dict(record_reads=0, record_writes=0, record_comparisons=0, board_slot_checks=0, candidate_scans=0,
                    idle_decisions=0, candidate_decisions=0, single_candidate_decisions=0,
                    vetoed_candidates=0, deferred_decisions=0, duplicate_arrivals=0, expired_arrivals=0,
                    cancelled_claims=0,
                    collisions=0, wasted_travel=0, travel=0, refusals=0, prohibited_executions=0)
    events = []
    snapshots = []
    curve = []
    primary = set()
    replacement = set()
    for t in range(ticks):
        if t == 1800:
            for a in agents[:3]:
                counters['cancelled_claims'] += int(a['busy'] is not None)
                board.pop(a['id'], None)
                a['active'] = False
                a['busy'] = None
            events.append(dict(t=t, action='remove', agents=[0, 1, 2]))
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
                counters['duplicate_arrivals' if job_id in completed else 'expired_arrivals'] += 1
                counters['wasted_travel'] += travel
            a['busy'] = None
        # Records are local to their target site; no hidden demand is exposed.
        # Expiry is the promised arrival tick, and all decisions share one snapshot.
        counters['board_slot_checks'] += AGENTS
        board = {k: r for k, r in board.items() if r['expiry'] > t}
        snapshot = list(board.values())
        deposits = []
        for a in agents:
            if not a['active'] or a['busy'] is not None:
                continue
            counters['idle_decisions'] += 1
            local_records = [r for r in snapshot if r['site'] in VISIBLE[a['site']]]
            counters['board_slot_checks'] += AGENTS
            counters['record_reads'] += len(local_records)
            choices = []
            feasible_count = 0
            for j in active.values():
                counters['candidate_scans'] += 1
                if j['id'] in completed or j['site'] not in VISIBLE[a['site']] or j['skill'] != a['skill']:
                    continue
                if a['id'] < 4 and j['skill'] == 0:
                    counters['refusals'] += 1
                    continue
                travel = distance(a['site'], j['site'])
                arrival = t+travel+a['cost']
                if arrival > j['deadline']:
                    continue
                feasible_count += 1
                counters['record_comparisons'] += len(local_records)
                blocked = claim_blocks(local_records, j, condition)
                if blocked:
                    counters['vetoed_candidates'] += 1
                    continue
                score = 1/(1+travel+a['cost'])
                choices.append((score, -j['deadline'], -j['id'], j, arrival, travel))
            counters['candidate_decisions'] += int(feasible_count > 0)
            counters['single_candidate_decisions'] += int(feasible_count == 1)
            counters['deferred_decisions'] += int(feasible_count > 0 and not choices)
            if choices:
                _, _, _, j, arrival, travel = max(choices, key=lambda x: x[:3])
                a['busy'] = (j['id'], j['site'], travel)
                a['arrival'] = arrival
                counters['travel'] += travel
                deposits.append(dict(owner=a['id'], site=j['site'], skill=j['skill'], job=j['id'], expiry=arrival))
                if detailed:
                    events.append(dict(t=t, action='claim', agent=a['id'], job=j['id'], arrival=arrival,
                                       visible_records=local_records))
            elif t % 5 == a['id'] % 5:
                # Exogenous local exploration, fixed across conditions and independent of demand truth.
                options = sorted(j for j in range(N) if distance(a['site'], j) == 1)
                if options:
                    a['site'] = options[(seed+t+a['id']) % len(options)]
                    counters['travel'] += 1
        for record in deposits:
            board[record['owner']] = record
            counters['record_writes'] += 1
        assert len(board) <= AGENTS
        if t % 100 == 0:
            curve.append(dict(t=t, completed=len(completed), eligible=len(eligible)))
            if detailed:
                snapshots.append(dict(t=t, board=list(board.values()), positions=[a['site'] for a in agents]))
    result = dict(seed=seed, condition=condition, task_hash=hash_json(stream),
                  eligible=len(eligible), completed=len(completed & eligible),
                  primary_n=len(primary), primary_done=len(primary & completed),
                  primary_rate=len(primary & completed)/max(1,len(primary)),
                  replacement_rate=len(replacement & completed)/max(1,len(replacement)),
                  agent_completions=completed_by_agent, **counters)
    # Five semantic scalar fields per record. This is storage/traffic, not CPU time.
    result['scalar_reads'] = 5*counters['record_reads']
    result['scalar_writes'] = 5*counters['record_writes']
    return result, dict(events=events, snapshots=snapshots, curve=curve)

