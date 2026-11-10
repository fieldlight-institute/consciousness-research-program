# Delayed feasibility in the retained reversal case

Post-hoc diagnostic of workload18035 only, selected because the retained fixed-plan delay study identified a single-overrun reversal there. Do not present it as an independent sample or general population estimate.

Use all64 binary delay vectors and their retained0.25-per-operation weights from execution-delay/first-results/workload-18035.json. Transform each single-skill operation demand from units to units+delay. This transformation is allowed only because both agents have rate1 for each demanded skill; validate that precondition and every resulting duration. Preserve sites, releases, deadlines, dependencies, refusal and handoff lag1. Do not expose delayed future information to a policy or rerun either policy.

For each vector run the existing whole-job service maximizer with100000 search nodes. Retain exact/bounded status, feasible witness and lower/upper service. Validate every witness against the transformed operations. Unknown remains unknown. Report weighted attainable lower/upper service, alongside the already retained fixed-plan outcomes. No new bootstrap or comparison across all40 workloads.

The offline evaluator knows all future jobs and delays and is free to choose assignments and order from the beginning. This is an information-and-commitment relaxation, not a replacement policy with equal information. A gap establishes available capacity under that relaxation, not that the online policy should have known how to achieve it. Examine the specific vector with only1-0 delayed to distinguish physical impossibility from plan fragility.

Check that attainable bounds do not improve as delays increase whenever the compared results are exact. Preserve all earlier artifacts and the first outputs. Freeze specification, runner and source checksums before computation.
