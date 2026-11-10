# Active Substrates first executable comparison

Frozen before the first run on October 21, 2026. This implementation develops the primary static-store versus dynamic-medium question in AS-01. It is a bounded B/C study, not completion of the full September 29 specification. The original specification and October 20 extension remain unchanged.

## Task and policy

Twelve agents occupy a six-by-four layout with 24 sites. Skills cycle through four types; service costs cycle through one to three ticks. Agents can see jobs within Manhattan distance two. Each tick produces a job with probability 0.8, a uniformly selected skill and deadline 12–30 ticks away. Eighty percent of demand falls in the first half of sites before tick 1000 and the second half thereafter. An agent selects a feasible matching job by `1/(1+travel+service) - 0.35*congestion`, with earliest deadline and job ID breaking ties. Idle agents explore one neighboring site at a fixed five-tick cadence. Agents never receive remote hidden-job information.

Claims are selected from one pre-decision snapshot and resolved in a condition-independent rotating arrival order. Agents do not read an omniscient assignment list. Successful arrival completes a job; a duplicate or expired claim wastes its travel. A scripted refusal excludes skill-zero jobs for agents 0–3. Three agents leave at tick 1800. No evaluator assigns work.

The primary outcome is the completion fraction for skill-eligible jobs born in ticks 1000–1499, completed by their deadlines. Skill eligibility means an available agent has the skill and does not refuse it; it does not assert joint schedulability. The last eligible primary deadline falls before the removal intervention.

## Medium and controls

All conditions receive the same local claim deposits, +0.5 bounded at one, and use the same scoring rule. B retains local congestion values for eight ticks since the last deposit; B-long retains them for 24. C applies 0.12 decay and conservative pairwise mixing at rate 0.04 on a fixed degree-four ring over sites. Communication and physical geometry are deliberately distinct. C-no-propagation retains decay but removes mixing. C-reset clears field state at tick 2400. The field is a congestion signal; demand remains directly observed local job data.

Budgets allow 24 or 96 directed edge operations per tick. All actual edge updates and transmitted scalars are counted, along with reads, writes and travel. B and C do not have equal total compute: the result is a performance/cost comparison, not a resource-matched causal claim. Each stores 24 field scalars and 24 timestamps, with common task/agent state. No tuning sweep is planned.

Ten pilot seeds (0–9) check implementation. Forty held-out evaluation seeds (100–139) follow only after checks pass. The evaluation is confirmation of this frozen implementation, not preregistration or confirmation of all AS-01. Use paired differences with seed as unit and 5,000 bootstrap resamples. Primary budget is 96; 24 is a secondary cost comparison. Report all outcomes, including harms and nulls.

## Scope differences from the retained study

Addressed-message A, adaptive-conductance D, fixed learned conductances, misleading deposits, timing shuffle and recovery-time estimation are not implemented in this first executable. The graph uses a degree-four ring without shortcuts. Agents have no learned internal histories; the tick-2400 replacement therefore tests medium reset with a fixed policy, not learned-agent succession. The generative-participation extensions require distinct implementations and remain pending.

Detailed decisions and field snapshots are retained for the first seed of each phase at the primary budget; aggregate outcomes are retained for every seed. Task streams are deterministic and hashed. Code hashes and settings are saved in each run manifest. No model API, human participant, private transcript or physical tissue is involved.

## Interpretation

A C advantage over B would justify further matched-budget work, not establish biological fascia or consciousness. C losing to B would show that this diffusion/decay mechanism, encoding and policy do not earn their extra work on this task. C versus C-no-propagation distinguishes mixing from decay within this implementation. B-long tests whether a longer ordinary retention window can account for an apparent benefit. Results cannot be generalized to every dynamic medium.
