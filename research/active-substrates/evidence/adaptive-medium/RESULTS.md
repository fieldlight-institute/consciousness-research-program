# Spatial adaptation from local arrival feedback

This extension implements learning in a shared spatial medium. Conductances change through delayed feedback at the site where an agent arrives. A fixed-medium control, a frozen-learning control and a medium-reset control distinguish the mechanism from ordinary propagation and retained state.

The implementation follows the original AS-01 direction while retaining the original task and scoring policy. It does not add the October 20 recognition/authority factorial, yoked replay or generative-participation tasks. The source specifications remain unchanged.

## What was implemented

Each of 48 undirected edges has a symmetric conductance bounded between 0.1 and 1.9. The field undergoes decay and conservative mixing over the original degree-four ring. At each destination the medium stores incoming edge activity. An agent carries that local receipt pattern when it commits to a job, then applies positive or negative feedback to those incident edges after its own successful or failed arrival. Zero activity earns no credit. Learning also relaxes conductances toward the fixed baseline.

This supplies a local delayed association, not a proof of an edge's causal usefulness. As in the preceding message study, successful service depends on travel and competition as well as the received signal. Agents receive no hidden demand, unchosen-task outcomes or global reward through this update.

The fixed control uses conductance 1 throughout. D learns continuously; D-frozen stops both feedback and relaxation at tick 1000; D-reset learns normally but clears field, conductances and receipts at tick 2400. All conditions clear carried eligibility at that checkpoint while retaining physical position and work in flight. The reset changes several medium components together, so it cannot separately identify topology and field history.

## Design and checks

Ten pilot seeds 7000–7009 and forty held-out seeds 8000–8039 run four conditions for 3,000 ticks. Specification and code are frozen before pilot, with no subsequent tuning. The primary contrast is D minus fixed C in completion for jobs born 1000–1499. Secondary contrasts compare D with frozen learning in the primary window, and D with reset medium for births 2400–2899. Intervals use 10,000 paired seed bootstrap samples, analysis seed 73023; secondary intervals are exploratory and unadjusted.

Six tests pass: incident-edge-only feedback; signed and zero-activity updates; conductance bounds and conservation of mixing apart from decay; relaxation/reset; exact fixed-control reproduction of the original C implementation; and identical trajectories before freeze/reset interventions. Assertions enforce refusal, identical task/eligibility pairing,96 directed transfers per tick and 288,000 receipt writes per episode. Ninety-two earlier non-cache experiment artifacts and both original source specifications are checksum-protected.

## Interpretation limits

The original scalar-scoring policy is intentionally retained. It can rerank feasible jobs but cannot reject a lone feasible job because of congestion. Earlier audits identified that restriction as a major limit on the medium's influence. A negative result therefore concerns this medium-policy combination; it cannot rule out adaptive media with different admissible actions.

All conditions reserve the same field, conductance, receipt and carried-eligibility representation, and execute the same transfer schedule. D performs additional feedback and relaxation operations. Logical counters do not measure every instruction, total CPU or energy. The result is not an equal-total-compute comparison. The inherited `operations` field counts only reads, writes and edge updates; use the separately reported receipt, eligibility, feedback and relaxation counters rather than treating that legacy total as complete.

Agent-level authority to adjust coupling, shortcuts, misleading-signal stress, timing shuffles, resource curves and the original recovery endpoint remain outside this implementation. Fresh individual history here means only cleared carried eligibility; it is not a broad model of participant succession. The experiment establishes neither conscious recognition nor generative participation.

## Held-out results

| Condition | Primary completion | Later completion | Failed arrivals | Feedback edge updates | Relaxation operations | Final mean conductance |
|---|---:|---:|---:|---:|---:|---:|
| C | 91.609% | 89.965% | 1231.60 | 0.0 | 0 | 1.0000 |
| D | 91.553% | 90.132% | 1231.95 | 13593.8 | 144000 | 1.1426 |
| D-frozen | 91.628% | 89.964% | 1232.38 | 4780.0 | 48000 | 1.0673 |
| D-reset | 91.553% | 90.052% | 1231.55 | 13579.9 | 144000 | 1.0749 |

Values are seed means; failed arrivals and operations cover the whole episode.

| Paired contrast | Difference in percentage points | 95% interval |
|---|---:|---:|
| D minus C, primary_rate | -0.0563 | -0.1702 to +0.0442 |
| D minus D-frozen, primary_rate | -0.0753 | -0.1772 to +0.0002 |
| D minus D-reset, replacement_rate | +0.0802 | -0.0938 to +0.3078 |

The adaptive medium did not establish an improvement over fixed propagation. Continued learning did not establish an improvement over the conductances frozen at the demand shift, and retaining medium state did not establish a later-window advantage over resetting it. These are finite-sample comparisons, not equivalence tests.

Learning did occur: feedback and relaxation counters are nonzero, and retained conductance snapshots differ from the fixed control. Yet primary completion counts are identical between D and C on 33 of 40 paired seeds. The diagnostic separates a functioning internal update from an outcome benefit; an active mechanism does not necessarily change what agents accomplish. The [retained trace check](retained-trace-check.json) inspects existing outputs without rerunning a simulation.

The result closes a specific implementation gap in AS-01 while preserving the earlier research direction: this conservative congestion medium and local association rule have not earned their additional learning operations under the inherited policy. It would be misleading to describe the mere existence of adaptive conductances as successful coordination, or to tune their learning rate on these held-out seeds until an improvement appears.

## Retained evidence

[Specification](SPECIFICATION.md), [freeze manifest](freeze.json), [evaluation rows](evaluation/rows.json), [summary](evaluation/summary.json), [pilot rows](pilot/rows.json), and first-seed traces retain all phases and source hashes. The preserved original plan and October 20 extension are hashed in the manifest. Neither source was edited, and no prior result was overwritten.

For reproduction use a fresh matching copy of the source tree without generated run directories or freeze manifest. Run the tests, then `python 3 run.py freeze`, `python 3 run.py pilot`, and `python 3 run.py evaluation`. The runner refuses existing destinations. Its lineage verification uses the recorded original source locations; copy or explicitly configure those locations before freezing a reproduction elsewhere. Data are entirely synthetic.
