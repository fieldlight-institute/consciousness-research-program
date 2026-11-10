# Composite job reservation results

Whole-job reservation completed more jobs than separate stage reservation in this bounded central-board comparison: +3.333 percentage points of offered jobs, with a paired 95% bootstrap interval of +0.833 to +6.667. It won on four of forty held-out workloads, tied on thirty-six and lost on none. The positive estimate rests on four differing pairs; it is a small result for these policies and workloads, not a general scheduling guarantee.

The useful change is concrete: do not reserve a first stage when the proposed continuation cannot finish the job. That decision can preserve capacity for a different complete job. The experiment changes admission and grouping together, so it does not isolate a pure benefit of prediction or extra information.

## Held-out outcomes

Both policies use the same two generalists, job descriptions, releases, work rates, travel model and one-tick crew-change latency. Each workload offers three sequential X-then-Y jobs. Agents append reservations to their existing queues; neither policy can cancel prior reservations or see unreleased jobs. All descriptions of a released job, including its second stage, are available to both policies.

| Mean per workload | Separate stages | Whole-job reservation |
|---|---:|---:|
| Whole jobs completed | 2.375 | 2.475 |
| Offered-job completion | 79.167% | 82.500% |
| Partial jobs left unfinished | 0.450 | 0 |
| Work occupancy ticks | 7.725 | 7.350 |
| Travel ticks | 1.775 | 1.275 |
| Candidate agent checks | 23.300 | 21.950 |

The primary completion interval uses 10,000 paired seed bootstrap resamples. Cost and partial-work means are descriptive secondary results. Avoiding partial jobs is enforced by whole-job admission in this deterministic environment; its absence is not an independent discovery. The completion and resource consequences are the outcomes of interest.

Ten pilot workloads were retained before the forty held-out workloads. Pilot completion tied in every pair. No parameter or rule changed after pilot. Forty held-out seeds were fixed in advance without a power guarantee. These are new task instances, not reruns of earlier single-skill studies, and their absolute completion rates cannot rank the earlier architectures.

## A retained schedule explains one gain

In seed 16000, both policies first reserve job 2 at site 1: agent a performs its two stages during ticks 1–3 and 3–5. At tick 1, two more jobs become visible. Job 0 requires two ticks of X and one of Y at site 0, all finished by tick 5. Job 1 requires one tick of X and two of Y at site 1, finished by tick 7.

The stage policy sends agent b from site 2 to site 0 and reserves job 0's X stage during 3–5. There is then no way for its Y stage to finish by 5. The policy also reserves job 1's first stage on agent a during 5–6, but cannot fit its two-tick second stage before 7. It finishes job 2 and leaves two partial jobs.

Whole-job reservation tentatively schedules job 0, detects that its continuation misses the deadline, and changes no queue. Agent b can instead travel to site 1 and finish both stages of job 1 during 2–3 and 3–5. The policy finishes jobs 1 and 2. It uses the same seven work ticks as stage reservation in this case but completes two jobs rather than one, with one less travel tick. This is a documented example, not a causal decomposition of all four wins. [Retained workload](evaluation/workload-16000.json) and [all policy schedules](evaluation/rows.json).

## What the offline bound adds

The separate exact evaluator proves an attainable whole-job count for every held-out workload. All forty bounds are exact. Mean attainable service is 2.775 jobs, leaving an average gap of 0.400 jobs for stage reservation and 0.300 for whole-job reservation. The comparison therefore records a modest improvement while showing that neither heuristic generally reaches the offline optimum.

The oracle has advance knowledge of the full workload and may arrange operations differently. The policies do not receive its schedules, chosen subsets or future job information. Their gap to that benchmark combines online information limits with heuristic choices; it cannot all be attributed to poor coordination. The same workload's bound applies to both because they have the same physical team and task constraints.

These counts avoid treating every individually feasible job as simultaneously attainable. They also preserve unconditional service: an improved fraction of an easier feasible set would not by itself mean that more jobs were served. No ratio with a zero or unresolved optimum is used. [Oracle bounds and witnesses](evaluation/bounds.json).

## Scope and resource accounting

This is a central reservation-board mechanism study. It does not implement decentralized negotiation, distributed races, unreliable communication or open-ended task creation. Both participants have the same skill rates; no heterogeneous/homogeneous population claim is made. The offered composite tasks are predefined.

Whole-job planning greedily chooses the earliest-finishing agent for each stage. A failed greedy proposal is not proof that the job is globally impossible; another assignment or reordering may work. Earlier reservations cannot be revised. Once a stage is committed, deterministic execution is assumed, so a complete plan cannot subsequently fail from disruption. Cancellation, interruptions and stale reservations would require a separate model.

The counters measure candidate agent checks, physical travel and work occupancy. They do not establish equal total computation or price queue scans, tentative state copies, idle gaps made unavailable by append-only booking, or communication. The lower observed number of agent checks under whole-job reservation does not establish a faster implementation. Oracle search is evaluator work, not a free coordination service given to participants.

## Verification and retention

Four multi-case tests pass: failed whole-job plans leave no partial reservations; a later unreleased job does not change the tested earlier decisions; skill refusal blocks execution; and policy witnesses validate against the earlier oracle and remain below its service upper bound. Both policies' schedules are validated for all pilot and evaluation runs, including dependencies, deadlines, travel and non-overlap.

All 519 previous research artifacts remain checksum-identical. Retained evidence includes [specification](SPECIFICATION.md), [source freeze](freeze.json), [pilot rows](pilot/rows.json), [evaluation rows](evaluation/rows.json), [summary](evaluation/summary.json), every generated workload, all policy reservations and all oracle witnesses. No first result was overwritten.

Run `python3 -m unittest -v test_policy` from this directory. To reproduce, use a fresh copy without generated freeze/pilot/evaluation destinations, preserve sibling evaluator directories, then run `python3 run.py freeze`, `python3 run.py pilot`, and `python3 run.py evaluation`. The runner refuses existing destinations and checks all preserved dependencies before and after execution.

The result earns a narrow next question: how much of the remaining attainable-service gap comes from append-only reservations that cannot be revised after new jobs arrive? That is distinct from increasing signal strength or tuning earlier learning rules. Any revision comparison must charge cancellation and preserve completed work, authorization and the information available at the decision time.
