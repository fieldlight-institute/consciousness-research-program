# Budgeted reservation revision results

Revising unstarted reservations increased whole-job completion by 3.333 percentage points of offered jobs in forty held-out workloads; the paired 95% bootstrap interval is +0.833 to +6.667. Revision won on four workloads, tied on 36 and lost on none. Each winning workload adopted one withdrawal and completed one additional job. The result is sparse and specific to this deterministic central reservation model.

The additional service required more planning checks, travel and work. Revision therefore earned a modest completion gain under the declared cancellation allowance; it did not reduce every resource cost. No cancellation duration, monetary charge or energy valuation was modeled.

## Held-out outcomes

| Mean per workload | Append only | Revision budget 4 |
|---|---:|---:|
| Whole jobs completed | 2.300 | 2.400 |
| Offered-job completion | 76.667% | 80.000% |
| Partial jobs remaining | 0 | 0 |
| Work occupancy ticks | 6.675 | 6.925 |
| Travel ticks | 1.225 | 1.400 |
| Candidate agent checks | 26.000 | 30.150 |
| Revision proposals | 0 | 0.850 |
| Accepted revisions | 0 | 0.100 |
| Cancellation units | 0 | 0.100 |

The primary interval uses 10,000 paired bootstrap resamples. Other means are descriptive. Ten pilot workloads preceded evaluation; they produced no accepted revisions and identical completion. No rule changed after pilot. Forty held-out pairs were fixed beforehand without a power guarantee.

Every offline service bound is exact, with mean attainable service 2.800 jobs. Append-only service is 0.500 jobs below that mean and revision is 0.400 below it. The oracle knows future demand and may reorder work globally; the remaining gap cannot be attributed entirely to poor online decisions. Neither policy receives oracle schedules or unreleased job descriptions.

The numerical primary effect happens to match the preceding whole-job-versus-stage experiment. These are different held-out workloads and a different comparison; the effects must not be added as though they came from a single factorial experiment. [Earlier reservation study](../composite-reservations/RESULTS.md).

## The revision rule

Both policies greedily reserve whole jobs using the same currently released descriptions and physical constraints. Revision is considered only when a new job arrives. It proposes withdrawing an unstarted reservation, closes the cascade through route tails and dependencies, and checks the affected agents' synthetic delegation. Any reservation with departure at or before the decision time is protected.

The planner then tries the same greedy rule on the hypothetical remaining state. It adopts at most one revision per arrival tick, only when the resulting plan completes strictly more currently known jobs than ordinary admission. Ties retain the existing commitments. Each removed reservation consumes one of four logical cancellation units. Candidate planning checks are counted even when no revision is adopted.

This is an operational intervention estimate: compare the planned service before and after a specific permitted change. Its predictions are reliable here because execution, durations and future execution of already booked stages are deterministic. Uncertain durations, failed travel, concurrent negotiations and disrupted execution would require new tests. The result should not be generalized to arbitrary recognition or learning mechanisms.

## One trace shows how completed work survives revision

In seed 18004, agent b has finished both stages of job 1 by tick 3. It has already departed for job 2's first stage at tick 3, so that stage is protected. Job 2's second stage is reserved for ticks 4–6, with departure at tick 4, and remains eligible for withdrawal.

A new job 0 arrives at tick 3 and needs two one-tick stages finished by tick 6. Revision withdraws only job 2's second-stage reservation. Agent b completes the protected first stage during 3–4, then performs job 0 during 4–5 and 5–6. Agent a travels from site 0 to site 2 and performs job 2's second stage during 5–7, within its tick 9 deadline and with the crew-change delay respected.

All three jobs finish. Completed job 1 and the already-started first stage of job 2 retain their exact records. The revision changes an unstarted commitment and reassigns its continuation; it does not erase prior work or recover travel already spent. [Workload](evaluation/workload-18004.json) and [reservation/audit traces](evaluation/rows.json).

## Physical state and authority

The new implementation records origins, departures, commitments and work intervals explicitly. Its append-only control reproduces the preserved policy's tested service, resource counters and work schedules. It does not retroactively assign physical timestamps to old experiment files.

Before every adopted revision, the lifecycle validator checks the full cascade against physical state and affected-agent authority. After replanning, every prior record with departure at or before the decision time must be unchanged. Completed and in-transit work are protected by the same rule. Snapshot fingerprints bind each withdrawal to the current state; trace audits retain both the withdrawal result and final replanned schedule.

All agents delegate revision in this synthetic comparison. This is not authenticated authority, evidence of human consent or a study of disagreements about cancellation. The cancellation allowance limits removed reservations, not evaluator computation. The policy also keeps append-only constraints within retained queues and uses no alternative-assignment search when its greedy proposal fails.

## Verification and retention

Four multi-case tests pass: baseline reproduction, a constructed useful revision with active work preserved, unreleased-job isolation, and budget/physical preservation across additional fixtures. Every pilot and held-out schedule validates against task dependencies, deadlines, skill, travel and crew-change constraints. All 100 trajectories retain before/after snapshots; the adopted withdrawals can be replay-checked without rerunning policy decisions.

All 590 earlier research artifacts remain checksum-identical. [Specification](SPECIFICATION.md), [source freeze](freeze.json), [pilot rows](pilot/rows.json), [held-out rows](evaluation/rows.json), [oracle bounds](evaluation/bounds.json), [summary](evaluation/summary.json), and [verification](verification.json) preserve the first results and their boundaries.

From this directory run `python3 -m unittest -v test_replanning`. For reproduction use a fresh copy without generated freeze/pilot/evaluation destinations and retain the sibling lifecycle, evaluator and original reservation directories. Run `python3 run.py freeze`, `python3 run.py pilot`, then `python3 run.py evaluation`. Existing destinations are refused.

This closes the bounded revision comparison. Further experimentation should be driven by a material question—such as costly or uncertain execution—not another threshold adjustment to these held-out cases. The current result establishes a small benefit of evaluating and revising specific unstarted commitments under deterministic conditions, alongside its additional resource demands.
