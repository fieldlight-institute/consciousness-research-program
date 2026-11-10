# Exact attainable service for whole jobs

The evaluator now computes the maximum number of whole jobs that can be completed under the earlier feasibility model. It closes every selected job over its prerequisites, checks the resulting schedule, and credits no partial composite job. When search is incomplete it returns lower and upper bounds rather than inventing an optimum.

This supplies the missing distinction between individually eligible tasks and a jointly attainable workload. It is an offline evaluator for small synthetic instances, not a decentralized policy, a general scheduling service or a completed population-comparison experiment.

## Retained demonstrations

| Case | Proven service interval | Meaning |
|---|---:|---|
| Two one-tick jobs, one agent, both due at tick 1 | 1–1 | Both jobs are individually feasible, but only one can finish. |
| Two sequential one-tick stages due at tick 1 | 0–0 | Finishing the first stage does not finish the composite job. |
| Completing a selected job also finishes its prerequisite job | 2–2 | Both whole jobs earn credit; prerequisite work is not hidden. |
| A prerequisite completes only part of another job | 1–1 | The selected job earns credit; the other remains partial. |
| Global search stops before a witness | 0–2 | No positive lower bound was established; two jobs remain possible. |
| One job is witnessed while the two-job candidate remains unresolved | 1–2 | A useful schedule is known, but optimality is not. |

The same code checks 162 constructed workloads: three independent jobs with durations 1–3 and a common deadline of 1–6. Every result agrees with an independent calculation that enumerates subsets whose total duration fits the deadline. The optimum is zero in 9 cases, one in 54, two in 67 and three in 32. The largest search uses 16 oracle nodes. These counts describe this constructed grid, not a statistical performance estimate.

## Dependencies and credit

Jobs partition the operation IDs, so one operation cannot be claimed by two jobs. A job may depend on operations belonging to another job. Selecting it expands the scheduled set to include all transitive predecessors. The evaluator then counts every job whose complete operation set is present, including any prerequisite job that finishes as a consequence.

For example, job A consists of stages a1 and a2; job B requires a1 but not a2. If a2 requires an unavailable skill, B can still be feasible after a1. Its witness contains a1 and B, credits B once, and records A as partial. Conversely, if A consists only of a1, the same witness completes both jobs. These cases prevent both undercounting completed prerequisites and overcounting partial work.

The separate `score_schedule` function checks the actual completed operation set, refuses missing dependencies, and validates deadlines, crew, refusal, travel, non-overlap and durations through the preserved oracle. It returns completed and partial job IDs plus travel, work occupancy and elapsed time. Full-job count is the objective; jobs are not weighted by importance or number of stages.

## What exact and bounded mean

The optimizer enumerates job subsets and deduplicates their prerequisite closures. It considers closures in descending order of whole-job credit. A feasible witness establishes a lower bound. A closure is excluded only when feasibility search proves it impossible. Unknown higher-value candidates retain their possible service as an upper bound.

A single node allowance is shared across feasibility calls. An optional per-candidate allowance lets a hard case remain unresolved while easier cases supply a witness. Search diagnostics retain each tested closure, its potential service, status and nodes; closures below an established bound need not be tested.

An exact service count does not imply that the returned schedule is fastest among all equally productive subsets. The inherited oracle may also find a feasible schedule before proving its minimum duration; that witness still proves the associated service is possible. Service optimality and schedule timing optimality are different claims.

The finite model assumes nonpreemptive work, stored partial artifacts, fixed skills and advance knowledge of demand. Removing irrelevant partial work cannot improve skills or release a new resource in this model. If a future task allows partial work to transform capabilities, the closure argument must be revisited. Bounds are limited to eight operations, eight jobs and four agents.

## How to use the bound in the next experiment

Keep the number of arriving jobs, the number actually completed and the offline attainable-service bound separate. Completing one of two arriving jobs can be full attainable service in the one-agent conflict case. It is still one job served, not two. A relative measure should not hide that absolute loss of capability.

An unresolved bound must remain an interval. A policy's independently validated schedule can strengthen its lower bound. If the proven attainable count is zero, a service-to-optimum ratio is undefined; do not turn it into a successful score of one. A normalized comparison also cannot repair unequal team capacities: one team may serve its entire smaller opportunity set while another serves more jobs in absolute terms.

The evaluator sees future demand solely to establish an offline bound. Passing its schedules, chosen subsets or future task information into a decentralized policy would change the experiment. Travel and work occupancy remain separate quantities; search nodes measure evaluator effort, not the team's coordination cost.

## Verification and reproduction

Seven tests pass, covering competition, partial credit, automatic prerequisite credit, partially completed prerequisite jobs, incomplete-search bounds, partition and witness rejection, and the independent 162-case optimum calculation. The first demonstration preserves all cases, witnesses, source hashes and the earlier oracle dependency. No earlier experiment was rerun or overwritten.

[Specification](SPECIFICATION.md), [implementation](service.py), [tests](test_service.py), [demonstrations](first-results/demonstrations.json), [full grid](first-results/grid.json), [summary](first-results/summary.json), and [verification](first-results/verification.json) retain the evidence. The source freeze also preserves all preceding research artifacts.

From this directory run `python3 -m unittest -v test_service`. Reproduce with `python3 demo.py` in a fresh copy without `first-results`, retaining the sibling `complementary-feasibility/oracle.py`. The demonstration refuses an existing destination.

The evaluator is ready for a bounded policy comparison. The next experimental design must specify the offered workload, population resources, admissible observations and coordination costs before testing a performance claim. Marginal skill matching alone remains insufficient, as the earlier feasibility counterexamples establish.
