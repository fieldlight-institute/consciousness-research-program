# Complementary task feasibility checker

The exact checker is implemented and tested. It decides whether a bounded set of synthetic operations can be completed under skill, refusal, travel, release, deadline, precedence and simultaneous-work constraints. Feasible results include independently checked schedules; a search limit produces an unknown result when no witness has been found. This is an offline evaluator, not a coordination policy.

The first constructed grid exposes the problem the checker was built to detect: equal aggregate per-skill rates do not imply equal productive capacity or equal deadline feasibility. It also establishes why individually feasible jobs cannot simply be added together as a feasible workload.

## First retained enumeration

Two specialists and two generalists each have aggregate potential rate 2 for X and 2 for Y. Specialists individually have one skill at rate 2; generalists each have both skills at rate 1 but can use only one at a time. Both teams start at site 0. The grid varies single, sequential and simultaneous tasks, deadlines 1–6, site 0/2 and handoff latency 0/3. Each demand requires two work units.

| Task type | Feasible for both | Specialist only | Generalist only | Neither |
|---|---:|---:|---:|---:|
| Single skill | 16 | 4 | 0 | 4 |
| Sequential X then Y | 6 | 4 | 2 | 12 |
| Simultaneous X and Y | 16 | 4 | 0 | 4 |
| Total | 38 | 12 | 2 | 20 |

All 144 team-instance searches finish; no unknown cases occur. Ninety schedules are feasible and checked. These 72 constructed instances are an exhaustive grid, not independent random observations. Handoff settings intentionally duplicate single/simultaneous cases where no transfer occurs. The counts describe this grid; they do not estimate population performance or establish a diversity advantage.

## Equal skill totals conceal different capacity regions

The specialist team can produce X at rate 2 and Y at rate 2 at the same time. The generalists can collectively produce either at rate 2, but their combined rate across both skills cannot exceed 2. Summing each skill's maximum double-counts the generalists' time. The sum of individual maximum rates is 4 for specialists and 2 for generalists.

Ignoring travel, discreteness and startup, the specialist team's attainable rate combinations fit within X≤2 and Y≤2. The generalists also obey X+Y≤2. The marginal skill maxima match while the joint capacity regions differ. No single claim of “matched capacity” captures both. Halving specialist speed would equalize the aggregate maximum but break the per-skill matching.

This is a counterexample to a proposed matching shortcut, not a valid resource-matched population comparison. A future experiment must either hold the relevant capacity region fixed or explicitly study the change in attainable capability. It cannot attribute this built-in service difference solely to better coordination.

## Handoffs can reverse the feasible team

At site 0 with a deadline of 2 and zero handoff latency, sequential X then Y is feasible for specialists: the X specialist works during 0–1, then the Y specialist during 1–2. A generalist requires two ticks per stage and cannot finish before 4.

With deadline 4 and handoff latency 3, the same sequential task is feasible for a generalist that keeps the work: X during 0–2, Y during 2–4. The specialists must change crew, so Y cannot start until 4 and completes at 5. Here the generalist's ability to retain the partial work outweighs the specialists' faster service.

The model stores completed partial work at the operation site. A changed crew incurs elapsed transfer latency without occupying an agent. This is not a measured labor cost or a realistic human handoff model. Simultaneous demands require different agents, a common start and a shared finish; faster participants remain occupied until the slowest finishes. Sequential and simultaneous complementarity therefore express different constraints and should remain separate task classes.

## Individual eligibility is not workload feasibility

The retained conflict case contains one agent and two independent one-tick jobs, each due at tick 1. Each job is feasible when tested alone. The pair is infeasible because the same agent cannot serve both during 0–1.

Filtering a future workload to tasks individually feasible for both teams will not ensure that either team can complete that workload jointly. A coordination comparison needs a joint schedule or an explicit attainable-service bound, in addition to individual eligibility. The current solver decides feasibility of completing the entire supplied set; it does not maximize a selected subset when the full set is infeasible. That distinction is the next evaluator implementation task.

## Implementation and verification

[The specification](SPECIFICATION.md) fixes timing and state semantics. [The oracle](oracle.py) enumerates precedence-compatible operation orders and eligible crew assignments, schedules each at its earliest possible time for that ordering, and retains a minimum-makespan witness when search completes. Inputs are bounded to eight operations and four agents. It supports nonpreemptive operations only and assumes advance knowledge of all demand; oracle schedules must not be exposed to decentralized agents.

The witness checker independently verifies coverage, crew identity, skill/refusal, durations, releases, deadlines, dependencies, handoffs, travel and non-overlap. It reports work occupancy, travel and elapsed completion separately. Search interruption preserves any feasible witness but withholds a minimum-makespan claim.

Seven tests pass. They cover opposite feasibility under matched skill totals, distinct simultaneous crews, travel and advance arrival, refusal, individual-versus-joint feasibility, invalid inputs and search limits, corrupted witnesses, and an independent enumeration of integer start times across 32 two-job cases. Reversing input operation order leaves feasibility unchanged in that comparison. An initial development error comparing a set with a dictionary was corrected before the retained enumeration; no first experiment output was replaced.

[First cases and witnesses](first-results/cases.json), [joint conflict](first-results/joint-conflict.json), [capacity and counts](first-results/summary.json), [source freeze](first-results/freeze.json), and [verification](first-results/verification.json) are preserved. All 499 earlier research artifacts remain checksum-identical. No previous simulation was rerun.

Run `python3 -m unittest -v test_oracle` from this directory. Run `python3 demo.py` in a fresh copy without `first-results` to reproduce the constructed grid; the demo refuses an existing destination. The first-results manifest hashes the implementation and specification used for that enumeration.

The next useful extension is an exact bound on completed whole jobs under a shared horizon, including the dependency closure of every selected job. Partial stages must not earn full composite-job credit. That bound would support reporting actual service against attainable service without assuming that individually feasible tasks can all be served. A heterogeneous/homogeneous coordination experiment remains unfinished until its resource comparison is explicit.
