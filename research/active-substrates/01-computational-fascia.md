# AS-01 — Does a dynamic shared medium contribute to coordination?

Version: 0.1 · September 29, 2026  
State: specification for review; not preregistered, implemented or run

## Question

Does a persistent, locally responsive medium improve adaptation beyond an equally resourced static shared store? When does stronger coupling instead suppress useful differences or spread error?

“Computational fascia” is a design analogy. Here, field means an explicitly represented state space. It does not denote an additional physical force.

## Task and agents

Initial configuration: 12 agents on a sparse connected graph with 24 resource sites. Sites receive jobs with demand, deadline and required skill. Agents have distinct skill/cost profiles, one-job capacity and local visibility. Successful service requires reaching a site and completing a suitable job before its deadline. Competing claims consume travel/time; an evaluator may resolve collisions but may not allocate agents.

Use the same local decision rule and tie-breaking random streams across conditions. Each agent scores visible feasible jobs by remaining demand, travel/service cost and locally available congestion information. No pretrained language model or central task planner. The evaluator sees the whole environment only to score outcomes.

Use a two-dimensional layout to define travel costs. Communication neighborhoods are a separately fixed graph, shared across conditions. Initial candidate: degree-four ring with fixed seeded shortcuts; test alternative topology only as a labelled robustness analysis.

## Conditions

A. **Addressed messages:** locally connected agents send bounded observations to specified neighbors; finite mailbox history.

B. **Static shared store:** agents write and read local site records with timestamps and a fixed expiry rule; no autonomous propagation or adaptive edges.

C. **Dynamic medium:** the same local records generate a bounded scalar demand/congestion state at sites. The state propagates over the fixed graph and decays. Agents observe only their neighborhood.

D. **Adaptive medium:** C with bounded edge conductances updated from local, delayed usefulness feedback. Agents may reduce their own coupling or decline tasks without an external override.

All agents can refuse or leave in all conditions; D does not receive that right as a unique advantage. Only D adapts medium conductance in the main comparison.

Candidate update for C, specified before tuning:

`x_i(t+1) = clip((1-lambda)*x_i(t) + alpha*sum_j w_ij*(x_j(t)-x_i(t)) + u_i(t), -1, 1)`

Here `u` is a bounded local observation/deposit, not hidden global demand. Conductances are nonnegative and normalized to keep mixing stable. For D, increase or decrease a conductance using local association between received state and subsequent successful service, with fixed rate, bounds and decay toward baseline. Precisely define credit assignment before coding D; do not let global reward silently update local edges.

This diffusion model is the first computational operationalization, not a mechanical model of anatomical fascia.

## Resource matching

Equalize local observation radius, per-agent stored scalar values, numerical precision, read/write allowance, decision frequency and exogenous information. Count propagating edge updates as communication/computation; dynamic propagation is not free. Report total operations, state size and transmitted scalar values alongside performance. When exact budget matching is impossible, compare performance-versus-budget curves rather than calling unequal settings a mechanism effect.

Include B with longer static retention as a memory control. Include C with frozen D conductances to distinguish learned topology from ongoing adaptation.

## Schedule

Proposed episode: 3,000 ticks. Demand shifts at tick 1,000; remove three agents at tick 1,800. At tick 2,400, replace the remaining agents with fresh agents whose internal histories are empty. Compare persistent medium versus reset medium from identical checkpoints. These are experimental manipulations, not simulation outcomes selected after inspection.

Separate stress episodes introduce one agent depositing misleading congestion signals. Compare adaptation with and without that contributor; do not combine every intervention into the primary endpoint.

Pilot: 10 development seeds for debugging and parameter ranges, never counted as confirmation. Confirmation: 40 new paired seeds per condition at the selected budget, with further budget settings explicitly secondary. Seed is the unit of replication; individual ticks are not independent samples. This initial sample size is a feasibility choice, not a power claim.

## Endpoints and analysis

Primary contrast: C versus B, difference in fraction of eligible jobs completed by deadline during ticks 1,000–1,500 after demand shifts. Count demand that cannot be served under the available skill set separately and report its definition.

Secondary: D versus C; post-removal recovery; replacement retention; wasted travel/duplicate claims; distribution of service across agents and task types; cost per successful job. Define recovery as return to 90% of pre-intervention rolling performance for 100 consecutive ticks, with non-recovery censored at episode end.

Refusal test: a scripted subset declines a task category in every condition. Count prohibited assignments/execution (target zero), and measure feasible work remaining elsewhere. Behavioral diversity is diagnostic; diversity without task benefit is not success by definition.

Report seed-level paired differences and bootstrap intervals, all seed outcomes, and budget curves. Do not select a best run as evidence. Freeze endpoint definitions, settings and analysis code before confirmatory seeds are opened.

## Mechanism checks

- Remove propagation while retaining equal history.
- Reset stored state at replacement while holding agents and task stream fixed.
- Freeze adaptation after its initial learning interval.
- Shuffle signal timing while preserving marginal values and communication budget.
- Introduce misleading deposits and measure their persistence and reach.

A gain disappearing after state reset implicates retained state; it does not by itself implicate adaptive dynamics. C failing to beat B supports the adequacy of ordinary shared storage for this task. D losing useful variation or amplifying misleading input identifies a cost of coupling. These are publishable outcomes within this study's limits.

## Before implementation

Resolve and record: job generator and feasibility rule; local score equation; deposit encoding; D credit rule; budget accounting; parameter search bounds; compute/time ceiling. Retain all tuning trials. The task is a narrow model of coordination, not a consciousness assay or a complete AI architecture.

## Implementation record required

Commit hash; frozen specification version; condition; seed; task stream hash; parameter manifest; environment/runtime versions; event log; agent decisions; medium state snapshots; operations budget; refusal events; analysis output; deviations. Use synthetic data only. Link code and results here when they exist.
