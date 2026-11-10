# Reservation withdrawal before replanning

The withdrawal boundary is implemented. It preserves departed and completed work, computes every affected reservation before applying a change, and requires authority for every affected agent. Seven tests pass; six retained demonstrations include two applied changes and four rejected changes. No caller snapshot is mutated.

This is a synthetic local state transition for a future replanning study. It does not yet choose when to cancel or construct a better schedule afterward.

## Travel makes a reservation active

A reservation records commitment, origin, departure, work start and finish explicitly. Once departure is at or before the decision time, that reservation cannot be withdrawn—even if work has not begun. The agent may already be traveling or waiting at the destination. Completed reservations remain part of the physical record.

The earlier reservation study stored work intervals and booking decisions, not explicit departure records. Its original outputs remain unchanged. A new replanning experiment must retain departure state rather than silently treat every future work start as idle capacity.

## A cancellation affects more than the requested operation

The retained example has agent a complete operation p at tick 2, then reserve q at another site followed by r farther away. Agent b reserves s, which depends on q. Requesting withdrawal of q at tick 2 affects q, r and s:

- r's route was planned from q's destination. The conservative append-only rule withdraws the remaining queue rather than silently invent a new origin.
- s depends on q's completion. Removing q must also remove s.
- Both agents are affected, so authority for agent a alone is insufficient.

If b has already departed for s at tick 1, the same request is rejected in full. Its work starts only at tick 6, but it is already committed physically. Nothing is partly removed before this conflict is discovered. In the version where b departs at tick 4, both agents can authorize the cascade at tick 2; p remains unchanged.

The queue rule is intentionally conservative. It can remove later work that could be salvaged by a new route, but that route must be an explicit replanning decision with its own feasibility check. Cancellation is not permission to rewrite the remaining schedule invisibly.

## Retained demonstrations

| Case | Outcome |
|---|---|
| Both affected agents authorize q's withdrawal | q, r and s removed; completed p preserved |
| Only the directly requested agent authorizes | Rejected; indirect agent authority missing |
| Dependent agent already traveling | Rejected; the cascade reaches departed work |
| Proposal applied at a later decision time | Rejected; a new physical-state review is required |
| Completed operation p requested for withdrawal | Rejected; completed work cannot be erased |
| Only the unstarted tail r is withdrawn | r removed; p, q and the dependent s remain |

## State and authority checks

A proposal binds the operation definitions, jobs, agent state, reservations and decision time. Application recomputes the complete affected set, rejects altered proposals and refuses changed snapshots or times. Validation checks explicit origins, travel time, queue order, release visibility and predecessor booking, as well as the existing scorer's skill, refusal, deadline and dependency rules.

The supplied authority set is a trusted simulation input. It is not authentication, human consent or a distributed authorization service. The SHA-256 fingerprint detects a changed snapshot within this local protocol; it is not a signature. Returned audit records retain before/after fingerprints and affected reservations, but this module does not provide durable transactional storage or concurrent-worker locking.

Application returns a copied reservation list. Failed requests return no partial state; successful results do not alias the caller's nested reservation data. Simultaneous multi-agent operations are outside this implementation's scope.

## Cost and next experimental use

The three-operation cascade charges three logical withdrawal units and reports three removed future work ticks. Already-departed travel is never undone. Those counters do not assign a physical duration or monetary cost to cancellation, and they do not show that the change improves service.

A replanning comparison must now specify when revision is considered, which agents delegate withdrawal, how cancellation consumes its budget, and how remaining completed work and committed travel constrain the new plan. It must compare actual whole-job service and costs against an unchanged policy, using only information available at the revision time. The offline optimizer can evaluate the outcome afterward; it cannot supply the policy with future jobs.

[Specification](SPECIFICATION.md), [implementation](lifecycle.py), [tests](test_lifecycle.py), [first demonstrations](first-results/demonstrations.json), [source freeze](first-results/freeze.json), and [verification](first-results/verification.json) retain the contract and results. All 582 earlier research artifacts remain checksum-identical. Tests cover cascade closure, indirect authority, departure timing, stale state/time, altered proposals, invalid physical state and independent result copies.

Run `python3 -m unittest -v test_lifecycle` from this directory. To reproduce the demonstrations, retain the sibling evaluator directories and run `python3 demo.py` in a fresh copy without `first-results`. Existing destinations are refused. No earlier policy experiment was rerun and no private material was used.
