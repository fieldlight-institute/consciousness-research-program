# PA-01: participant recognition and authority

Locally informed adjustment did not establish an advantage over replayed adjustment from an independent synthetic donor. The primary difference is −0.1327 percentage points, with a paired 95% interval of −0.3729 to +0.1252. An exploratory comparison favors the clock-driven adjustment policy over the locally informed policy; that interval is unadjusted and requires independent confirmation.

The implemented distinction is consequential permission: participants can revise the strength of their own connection to a shared adaptive medium. The reliability estimate is operational, derived only from local task arrivals. No result here measures conscious recognition or tests the broader philosophical account.

## Held-out comparison

Forty matched recipient seeds, five conditions each, plus forty independent donor runs. Ten earlier pilot seeds and ten donors are retained separately. All conditions keep the same AM-01 spatial adaptation.

| Condition | Primary completion | Total completions | Travel | Failed arrivals | Boundary changes |
|---|---:|---:|---:|---:|---:|
| No estimate use / fixed boundary | 91.454% | 2171.57 | 9231.02 | 1232.95 | 0.0 |
| Estimate / fixed boundary | 91.454% | 2171.57 | 9231.02 | 1232.95 | 0.0 |
| Clock-driven adjustment | 91.689% | 2172.10 | 9232.90 | 1238.03 | 1268.0 |
| Locally informed adjustment | 91.440% | 2173.12 | 9240.38 | 1232.22 | 457.0 |
| Independent-donor replay | 91.573% | 2174.32 | 9236.02 | 1228.12 | 447.6 |

| Paired contrast | Difference (percentage points) | 95% interval |
|---|---:|---:|
| Informed − donor replay (primary) | -0.1327 | -0.3729 to +0.1252 |
| Recognition × authority interaction (exploratory) | -0.2481 | -0.4630 to -0.0485 |
| Informed − fixed boundary (exploratory) | -0.0132 | -0.2148 to +0.1811 |

The estimate-only and no-estimate fixed conditions are exactly identical, as the implementation requires. Consequently the factorial interaction equals informed adjustment minus clock-driven adjustment. This identity is a design property, not independent evidence that recognition is inert in general. The clock comparator is one prespecified alternative, not an optimized policy or a control matched on the number or distribution of changes.

## What participants can change

Each participant starts with boundary coupling1. A change scales both its congestion read and its own claim deposit; shared edge learning continues separately. Every25 ticks, informed participants take a bounded step toward a target based on the last32 observed signal/outcome agreements. The estimate uses the raw field at commitment and only that participant’s eventual arrival. No hidden task outcomes enter it. Clock-driven participants use a fixed triangular schedule. Replay participants use the same agent ID’s schedule from another task realization; recipient outcomes cannot revise that schedule.

The chosen estimate measures whether a thresholded congestion signal predicts arrival failure. It does not estimate the outcome of a coupling intervention. This distinction is the central design finding: usable information about a relationship and authority to revise that relationship do not by themselves provide a good revision rule. Reading more strongly and depositing more strongly are changed together here, so their effects cannot be isolated. The negative exploratory interaction gives a concrete reason to examine this rule before adding more sophisticated recognition claims.

The independent-donor comparison also has a limit: it tests transfer of a learned schedule across task realizations, not identical information with its causal contingency surgically removed. Shared demand-shift/removal timing remains aligned; local outcomes differ. A null primary result is not equivalence or proof that histories are irrelevant. Time-shuffled estimates, stress exposure, explicit revision-latency analysis and broader generative-participation tasks remain unfinished.

## Costs and planning

Every condition reserves the same32-slot local scan allowance and computes the same summary/comparator candidates at each active checkpoint. In conditions without recognition access the estimate is inaccessible instrumentation. Actual scan entries and arrival counts can differ because behavior changes. Donor generation incurs an additional full simulation per pair; it is not free online coordination. Shared-medium operations, boundary multiplications and local computation must be reported separately, not collapsed into the legacy operation total.

| Condition | Recorded arrivals | Window entries scanned | Reserved scan slots | Summary evaluations | Read multiplications | Deposit multiplications |
|---|---:|---:|---:|---:|---:|---:|
| R0A0 | 3401.5 | 34919.5 | 41472.0 | 1296.0 | 3857.6 | 3409.2 |
| R1A0 | 3401.5 | 34919.5 | 41472.0 | 1296.0 | 3857.6 | 3409.2 |
| R0A1 | 3407.0 | 34924.0 | 41472.0 | 1296.0 | 3868.6 | 3414.8 |
| R1A1 | 3402.2 | 34920.0 | 41472.0 | 1296.0 | 3860.7 | 3410.1 |
| Yoked | 3399.3 | 34915.4 | 41472.0 | 1296.0 | 3861.0 | 3407.1 |

Capacity adds384 agreement bits,12 boundary scalars and up to12 pending signal values to AM-01. Python object sizes, allocation, replay retrieval and interpreter overhead are not priced. Each episode still executes288,000 directed spatial transfers and144,000 shared-weight relaxations. This is a matched scheduled allowance comparison, not equal total CPU or energy.

Pilot paired standard deviation was0.008109 in rate units. The frozen normal-approximation rule for a0.005 rate difference requested21 pairs; the prespecified floor selected40, below the200 cap. Ten pilot pairs cannot guarantee power. Evaluation uses40 distinct seeds with10,000 paired bootstrap resamples; the three intervals are not multiplicity-adjusted. No parameter or sample-size rule changed after pilot.

## Evidence and checks

Five multi-case tests pass: bounded local observation history/uncertainty, authority and update direction, history-independent clock/replay controls, exact original AM-01 reproduction when the boundary is fixed, and the factorial negative control plus refusal/replay/accounting checks. Every held-out replay trajectory matches its donor exactly. Original refusal remains intact; there is no new departure or abstention action. All165 prior experiment artifacts and the original October20 specification are checksum-preserved.

All recipient completion events are retained, allowing later recovery analysis without agent reruns. First recipient and donor detailed traces, every donor coupling schedule, all rows, source hashes and sample-size decision are saved. The first experiment states remain unchanged.

[Specification](SPECIFICATION.md) · [Source freeze](freeze.json) · [Sample-size decision](sample-size.json) · [Evaluation rows](evaluation/rows.json) · [Donor rows](evaluation/donors.json) · [Summary](evaluation/summary.json) · [Verification](verification.json)

Reproduction uses a fresh copy without generated destinations: `python3 -m unittest -v test_participant`, then `python3 run.py freeze`, `python3 run.py pilot`, `python3 run.py size`, and `python3 run.py evaluation`. The runner refuses existing destinations and validates the original source path from its manifest. This completes the bounded factorial and independent-donor comparison; it does not complete Extension A or the full Active Substrates program.
