# AS-01 design review: what the first result actually tested

The most consequential constraint is in the action rule, before diffusion. An agent with any feasible candidate must claim one. Congestion can change a ranking; it cannot make the agent wait. If all candidates occupy the same site, a site-level penalty subtracts the same quantity from every score and cannot change that ranking either. Extra propagation therefore has no direct action effect at most decision opportunities.

Instrumentation of the original ten pilot seeds confirms this constraint in practice. Every original output field matched the preserved pilot row exactly; instrumentation changed no decisions. These are descriptive audits of existing trajectories, not new independent evidence or counterfactual reruns under another policy.

| Original condition | Decisions with a feasible candidate | Only one candidate | All candidates at one site | Ranking changed by penalty |
|---|---:|---:|---:|---:|
| B | 34,263 | 88.13% | 90.16% | 4.10% |
| C | 34,140 | 88.81% | 90.88% | 3.24% |
| C without propagation | 34,113 | 88.76% | 90.82% | 4.05% |

For example, a lone job with a high congestion value is still chosen. Two jobs of different skills at the same site share one penalty although one claim does not necessarily interfere with the other. Diffusion also changes penalties at neighboring communication sites where the original claim does not apply. These features jointly make the original result an evaluation of a narrow encoding-and-policy combination, not a strong test of whether a persistent shared medium can coordinate agents.

## Corrections to interpretation

- The first result remains valid as reported: this C did not demonstrate an endpoint improvement over B, while adding counted propagation work. The audit does not reverse the result.
- The original `collisions` counter combined duplicate and expired arrivals. In all thirty audited pilot episodes, every such arrival was a duplicate and none was expired. The policy only schedules arrivals before deadlines; removal cancels claims rather than logging an arrival. Report duplicate/expired together for the preserved files, or use the new separate diagnostics where available.
- Refusal is enforced at selection and asserted at execution. The zero `prohibited_executions` field is never incremented, so that field alone is not an independent safety test. Likewise `refusals` counts repeated candidate encounters, not distinct decisions to refuse. The new mechanism tests explicitly check the refusing agent completes no jobs.
- Clearing a short-lived signal in a fixed-policy population does not test learned succession. There is no real replacement of learned agents at tick 2400. No conclusion about generational continuity follows from the reset condition.
- The original cost proxy omits per-site expiration/decay, filtering, sorting and other work. It cannot support a total-cost ratio or equal-resource claim. A complete budget should distinguish retained state, message payload, local comparisons, field updates and agent work; these are not automatically interchangeable units.
- Whole-episode completion has end-of-run censoring for late jobs. The primary birth cohort does not. Keep primary-cohort completion as the endpoint rather than silently comparing censored totals.
- The first manifest hashes the executable, not its accompanying specification. The new study freezes both and verifies all imported executable dependencies before and after runs.

## Implemented next test

[Claim specificity](claim-specificity/SPECIFICATION.md) isolates exact-job, skill-and-site and site-wide claims under one deferral-capable policy, with an ignored-record control. It uses separate seeds, a local visible board and explicit record expiry. This tests the proposed encoding problem without tuning propagation until positive. It exposes no remote demand and does not implement addressed-message A or adaptive D.

A and D still need their own designs. For A, define recipients, mailbox capacity, delivery/expiry and a visibility-matched local-board control. For D, specify what an edge can observe and how local delayed credit is assigned; an evaluator's global completion reward would introduce information absent from other conditions. Resource matching must include identifier-bearing records and adaptation state. Neither should be added merely to make the four labels appear complete.

The practical inference is that a medium's information must affect an action the agent can take. Adding propagation to a policy that cannot decline a duplicate is unlikely to address that coordination failure. The separate experiment determines whether this inference earns an endpoint improvement in the present environment.

## Audit reproduction

`python3 audit_policy.py --output /path/to/new-audit.json` reconstructs the diagnostic instrumentation in a temporary directory, checks every original metric against saved pilot rows, and refuses to overwrite an existing audit. [Saved diagnostics](policy-audit.json) retain every audited seed. Original code, specification, pilot and evaluation files were preserved.
