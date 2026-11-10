# RI-01: addressed remote observations and recipient-local credit

Frozen before implementation and data inspection, October 21, 2026. Synthetic extension of AS-01, not a replacement for either preserved study. No external data or model calls.

Question: do addressed observations of remote demand help beyond the existing local skill-and-site claim board? Does recipient-local outcome feedback improve use of those observations? This implements addressed-message A and a local-credit mechanism needed for a future D. It does not implement an adaptive spatial substrate and must not be reported as the complete A/B/C/D comparison.

## Conditions and common environment

Use the unchanged original task generator, 24 sites, 12 agents, four skills, 3,000 ticks and original positions/costs/refusal rule. Remove agents 0–2 at tick 1800. Primary jobs are born during [1000,1500); replacement jobs during [2400,2900). Eligibility retains the previous skill-availability definition, not optimal schedule feasibility. All conditions use the same local skill-and-site claim veto and exogenous one-step exploration. Decisions and board deposits are simultaneous; arrivals rotate in fixed agent-ID order.

- `local`: local sensing and local claim board only.
- `A-fixed`: addressed remote observations; remote candidate score multiplied by fixed 0.75.
- `A-credit`: same messages, recipient-local per-sender success estimate `(3+successes)/(4+attempts)` replaces 0.75. An attempt is counted only on arrival at a remotely learned job, with success determined by that recipient's own completion. No reward, completion ledger or global state is supplied to the learner.
- `A-credit-reset`: identical to A-credit until tick 2400, then erase all per-sender estimates. Physical state, mailboxes and work in flight persist. Later outcomes of inherited trips update the new table; this is policy-memory reset, not a new organism or fully independent agent replacement.

Local candidate scores are `1/(1+distance+cost)`; remote candidates multiply by the stated weight. Highest score, earliest deadline, smallest job ID wins. Refusal is checked before commitment. Remote observations do not reveal whether a job is still uncompleted: that is learned locally on arrival. Locally visible completed jobs can be recognized as absent and removed from the mailbox; remote ones cannot. Local observations supersede mailbox reports for the same job.

## Mailboxes and information boundary

Only idle agents report directly observed, currently available jobs within the original visibility radius. At most one proposed report per sender per tick: earliest deadline, then smallest job ID. Address to one statically skill-compatible, non-refusing agent other than the sender, selected by `(tick+sender+job_id) modulo recipient_count`. This uses published capabilities, not receiver position, workload, learned quality or a central optimal assignment.

Packets contain eight scalar fields: sender, recipient, observed tick, job ID, born tick, site, skill, deadline. Delivery is next tick. Each recipient holds at most eight job-keyed entries; overwrite with latest observation, evict oldest observed tick then smallest job ID. TTL is eight ticks from observation; expire at observed+8 (exclusive). The sender can repeatedly observe/report a still-present job. No acknowledgments or outcome broadcasts. No global completion filtering of remote reports.

All messaging conditions share a cap of four packets/32 payload scalars per tick, allocated in rotating sender-ID order. Count actual transmissions, deliveries, evictions, expiry, observation scans, mailbox scans, claim comparisons, local credit updates, travel and arrivals. Common board records have five scalar fields and are counted separately. A fixed cap is equal communication opportunity, not equal realized traffic, CPU, wall time or total energy. Local condition may leave the messaging budget unused; do not inject useless traffic to make totals equal. Every condition has the same mailbox capacity; only adaptive conditions use up to 144 sender/recipient credit cells (two integer counters each). Disclose this extra state rather than call it free or memory matched.

## Evaluation and stopping

Pilot seeds 3000–3009; evaluation seeds 4000–4039, never used in previous studies. Freeze specification and code hashes before pilot. Pilot is implementation inspection, not parameter selection; any substantive change requires a named new specification and preserved old output. Run all four conditions on all 40 evaluation seeds without tuning. Primary contrast: A-fixed minus local completion fraction in the primary window. Secondary exploratory contrasts: A-credit minus A-fixed in primary window; A-credit minus A-credit-reset in replacement window. Paired seed-level bootstrap, 10,000 resamples, fixed analysis seed 73021, percentile 95% intervals; secondary intervals are not multiplicity adjusted. Report negative or null results as measured. Never infer adaptive-substrate superiority from these message-policy contrasts.

Meaningful tests must show remote reports can cause remote commitment, stale remote reports can cause failed arrivals, local refusal survives messaging, delivery/capacity/TTL boundaries, only local outcomes update credit, and credit reset changes no pre-reset trajectory. Preserve existing experiment artifacts byte-for-byte.
