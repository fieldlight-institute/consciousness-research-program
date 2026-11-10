# Claim specificity: separate mechanism study

Written before pilot or evaluation on October 21, 2026. This is a follow-up prompted by the first B/C result and code review, not a preregistered independent research program or the addressed-message A/adaptive-conductance D implementation.

## Question and contrasts

Does a local claim record help coordination when it identifies the work already claimed? The previous scalar congestion penalty could only rerank feasible jobs; an agent always chose one if any existed. It could not prevent a duplicate claim on a lone candidate. This experiment changes both representation and the permitted response, then isolates specificity within that new response. It does not attribute a difference from the original study solely to representation.

Four conditions receive the same local record schema and use the same travel/service ranking:

- `no-veto`: ignore the records when choosing; choose the best feasible job.
- `site-veto`: defer any candidate at a site with an unexpired claim.
- `skill-site-veto`: defer candidates matching a claimed site's skill.
- `job-veto`: defer only the exact claimed job.

Primary contrast: job-veto minus site-veto on completion of skill-eligible jobs born in ticks 1000–1499. Secondary contrasts: job-veto minus no-veto and job-veto minus skill-site-veto. All conditions and all differences are reported. A positive primary contrast supports specificity over broad suppression in this task; only the secondary no-veto comparison can show whether the exact claim board earns its behavioral intervention at all. No preferred positive result is required.

## Fixed environment and access

Reuse the original deterministic task generator, 24-site six-by-four physical geometry, twelve agents, four skills, service costs, observation radius two, exploration cadence, demand shift at 1000, refusal rule and removal of three agents at 1800. No learned-agent replacement is claimed; there is no intervention at 2400. Jobs arrive with probability 0.8 per tick and deadlines 12–30 ticks later. Run 3000 ticks. The primary cohort finishes before removal and has no end-of-run censoring. Whole-episode counts include late jobs and are descriptive only.

Each agent can leave one record at its destination site, containing owner, site, skill, job ID and expiry. At most twelve records exist. Agents only see records at sites inside their ordinary observation radius. There is no remote demand, hidden assignment list, central scheduler, or message transport. Records use the claimant's scheduled arrival tick as expiry; expired records are removed before decisions. Records from removed agents are removed. Busy agents cannot issue new claims. All decisions share a pre-decision snapshot, so simultaneous duplicates remain possible. If records exclude every feasible candidate, the agent follows the same idle exploration rule. Claim records do not override refusal.

## Resource accounting and limits

All conditions have the same maximum board schema (60 semantic scalar fields) and access permissions, including the ignored-record control. Each idle decision scans twelve possible board slots, reads all locally visible records once and compares every feasible candidate against every visible record. The implementation computes all site/skill/exact match predicates without early exit. Actual workload differs because behavior changes; this is not equal-runtime matching or a cap on total work.

Report board-slot checks, record reads/writes, scalar reads/writes (five per record), candidate scans, record comparisons, candidate decisions, single-candidate decisions, deferred decisions, vetoed candidates, duplicate arrivals, expired arrivals, cancelled claims and travel. Expiration and duplication are distinguished. These categories are logical operations, not hardware instructions, bytes, energy or network traffic. General environment and runtime work are excluded. Memory is bounded in record count, not fixed-width bit representation. Keeping job identifiers costs more than one scalar congestion value; no equal-memory comparison with the original B/C is claimed.

## Execution and inference

Pilot seeds 200–209; held-out seeds 1000–1039. These do not overlap the first study. No parameter sweep or adaptive edge tuning. Freeze hashes of this specification, study.py, run.py and the imported original simulate.py before pilot; require the same hashes for evaluation. Tests must pass before freezing. Preserve all rows and first-seed traces for every condition. Output directories must not already exist.

Use paired seeds as units, with 5,000 paired bootstrap resamples, fixed resampling seed 493 and percentile bounds. Report primary mean difference and interval; secondary intervals are exploratory, without multiplicity correction. Run the held-out phase only after the pilot passes denominator, task-stream, refusal, deterministic-repeat and duplicate-accounting checks. If substantive repairs are needed, document them and freeze a new version before using new held-out seeds. Neither this nor the first study supports claims about biological fascia or consciousness.
