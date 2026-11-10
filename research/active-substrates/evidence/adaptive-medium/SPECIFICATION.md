# AM-01 local delayed adaptation of spatial conductance

Frozen implementation extension of AS-01, October 21, 2026. Consulted the retained September29 AS-01 and October20 generative-participation sources. Original sources and prior runs remain unchanged. This implements the missing spatial adaptation mechanism, not all original controls or the generative-participation extension.

## Medium and feedback

Retain the first B/C task generator, geometry, degree-four communication ring, local congestion scoring, skill/refusal rule, exploration, removal and primary cohort. Use 96 directed transfers each tick. Each undirected ring edge has one symmetric conductance initially1, bounded [0.1,1.9]. Apply simultaneous conservative pair mixing `0.04*w*(x_j-x_i)` to the decayed field `0.88*x`. Degree four and maximum conductance give a nonnegative self-coefficient at least0.576; nonnegative inputs cannot become negative before clipping. Values remain bounded. No shortcuts or topology changes.

Each completed edge transfer also stores its positive incoming amount at each destination: `0.04*w*x_source`. This is locally received activity, not a new global-demand observation. At commitment an agent carries the four incoming amounts stored at its visible target site as an eligibility record. On arrival it applies feedback at that target only: +1 for its own successful service, −1 for its own failed arrival. For each incident edge, increment `0.02 * feedback * incoming_amount / sum(incoming_amounts)`, clipped to bounds. Zero incoming activity produces no update. This is a local delayed association; it is not a causal estimate of the edge's usefulness. No unchosen task outcomes or global completion score train the weights.

Before transfers, active learning relaxes each conductance toward1 by `0.001*(1-w)` each tick. Each executed relaxation and feedback edge update is counted. Symmetry means feedback at one endpoint changes transmission in both directions; no hidden long-range update occurs. Agents still have the same task-category refusal and departure rules; none receives unique authority to force another agent's participation.

## Conditions

- `C`: fixed conductance1, same field, receipt storage and local scoring; no adaptation.
- `D`: delayed local feedback plus baseline relaxation throughout.
- `D-frozen`: same learning as D through tick999; no weight feedback or relaxation from tick1000 onward. Existing learned topology continues to transmit.
- `D-reset`: same as D until tick2400, then clear field, receipts and weights back to baseline; resume learning.

At tick2400 every condition clears in-flight eligibility records to model fresh individual histories; physical position and already committed travel remain. Agents have no other learned internal state. D versus D-reset is therefore a retained-medium comparison with empty individual eligibility, not full social succession. Weights and field are reset jointly; this contrast does not isolate which one mattered.

The original scalar-scoring policy is deliberately retained to isolate medium changes within this extension. It still cannot reject a lone feasible candidate because of congestion. This limits the mechanism's opportunity to affect outcomes; do not silently replace the policy to obtain a gain.

## Resources and scope

Every condition has 24 field scalars, 48 symmetric conductance scalars, 96 receipt scalars and up to48 in-flight eligibility scalars (four per agent). C stores fixed weights and receipts as a controlled representation baseline. Count 96 directed transfers and96 receipt writes per tick, four eligibility reads per commitment, feedback edge updates and48 relaxation operations per learning tick separately. Shared candidate scans, decay, arithmetic instructions and interpreter cost are not fully counted; no equal total compute/energy claim. Adaptive conditions incur additional operations, explicitly reported. Scalar counts are logical fields, not serialized bytes or fixed numerical precision. No budget sweep or topology robustness claim.

Primary contrast D−C, primary cohort completion (births1000–1499). Secondary D−D-frozen primary completion; D−D-reset later cohort (births2400–2899). Forty new held-out seeds8000–8039; ten pilot seeds7000–7009. 3000 ticks. Freeze code, specification and runner before pilot; no tuning. Paired bootstrap10000 resamples, seed73023; secondary intervals exploratory/unadjusted. Record all outcomes, travel, collisions, weight changes and traces. Verify C reproduces original C at full budget, refusal is never violated, and pre-freeze/reset trajectories match.

The original AS-01 also calls for misleading deposits, timing shuffle, recovery estimates, more fully matched resource curves and fixed seeded shortcuts. Those remain unimplemented here. October20 recognition/authority factorials and yoked replay remain distinct. No consciousness or generative-participation inference follows from this narrow result.
