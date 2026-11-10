# The reversal did not exhaust physical capacity

In the retained single-overrun case for workload18035, a feasible schedule still completes **all three jobs**. The saved append-only schedule completes two; the saved revised schedule completes one. The missed work was therefore not forced by the available agents, locations, deadlines and realized durations alone.

The qualifying difference is substantial: the offline evaluator knows future jobs and delays and can choose assignments from the beginning. Its witness is not a repair available after the original agents have departed. This diagnostic identifies capacity under relaxed information and commitment constraints; it does not establish an online policy error or a deployable replacement.

## One concrete feasible schedule

Only operation `1-0` takes an extra tick. The [retained witness](first-results/case-08.json) assigns agent b to job1 and leaves agent a at site0:

| Agent | Operation | Site | Work interval | Deadline |
|---|---|---:|---|---:|
| b | 1-0 | 1 | 1–3 | 7 |
| b | 1-1 | 1 | 3–4 | 7 |
| a | 2-0 | 0 | 0–2 | 8 |
| a | 0-0 | 0 | 2–3 | 5 |
| a | 0-1 | 0 | 3–4 | 5 |
| a | 2-1 | 0 | 4–5 | 8 |

Agent b travels one site before starting. Agent a stays at site0, completing job0 between the two stages of job2. Both stages of each job keep the same agent, so no cross-agent handoff delay is incurred. Total work occupancy is8 ticks and travel is1 tick. All three jobs finish within their deadlines.

The saved revised schedule instead keeps the already committed assignment of agent a to `1-0`, then inserts job0 and postpones the job1 continuation. When `1-0` overruns, the extra travel and ordering leave the later completions late. The two plans cannot be equated merely because both have access to two agents with the same skills.

## All delay vectors for this selected workload

The diagnostic also evaluates all64 binary delay vectors already retained for this workload, with the same independent0.25 overrun probability. It uses the existing whole-job evaluator with a100,000-node limit for each vector. All64 service results are exact;25,027 search nodes were explored in total.

| Quantity | Expected whole jobs, of3 |
|---|---:|
| Offline attainable service with realized delays | 2.99097 |
| Saved append-only plan | 2.00000 |
| Saved revised plan | 1.73828 |

These are expectations for **one deliberately selected reversal workload**, not estimates across the original forty-workload population. No new confidence interval is fitted. The original delay study's population-level comparison remains unchanged. The offline result includes both future-information and freedom-to-reassign advantages; the table does not isolate their separate contributions.

## Checks and implications

The [specification](SPECIFICATION.md), runner and all preceding artifact hashes were frozen before calculation. Adding a work tick is represented as one additional demand unit only after verifying that both agents have rate1 for every demanded skill. Sites, release times, deadlines, dependencies, refusal and handoff latency remain unchanged. Every transformed duration is checked.

All64 feasible witnesses pass the existing schedule verifier and a [separate direct trace check](verify.py) of timing, travel, occupancy, dependencies and whole-job credit. The729 comparable pairs of exact results obey monotonicity: adding delays never raises attainable service. All703 previous research artifacts remain checksum-identical. Original policies and fixed-plan replays were not rerun.

This closes one interpretive gap in the adverse delay finding. Its losses cannot simply be described as inevitable consequences of longer work. Neither can the offline witness be offered as an answer the participants should have known. The next meaningful distinction is between flexibility retained before departure and repair possible after commitment. Investigating that distinction would require explicitly preserving the participants' information and physical state; this calculation does not supply it by implication.
