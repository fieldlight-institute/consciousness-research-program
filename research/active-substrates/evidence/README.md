# Runnable evidence — Active Substrates

Fieldlight Institute · November 10, 2026

This package contains the synthetic studies supporting the [implementation status](../05-implementation-status.md): source code, retained per-seed outputs, finite demonstrations, and reports. It contains generated workloads, not private participant records. The [new research extension](../06-history-maintenance-and-encoding.md) is a design record; its proposed experiments are not results in this package.

## Reproduce

Requires Python 3.9 or newer and its standard library. No account, API, external model, or downloaded dataset is required. From this directory:

```sh
python3 reproduce.py --smoke
python3 reproduce.py --full
```

Both commands run 57 unit tests and rebuild five finite demonstrations/analyses. Smoke mode compares the first retained evaluation seed in each simulation; full mode compares all 1,080 retained rows across six simulations. Comparisons include every saved row field, not just headline metrics. Each study runs in a separate process to isolate its modules.

The demonstrations run in a temporary copy of this package (allow roughly 150 MB free disk space). Original retained results are not overwritten. Python may create ordinary `__pycache__` files. Full reproduction takes several minutes depending on the machine. A failed assertion or subprocess produces a nonzero exit status.

Additional checks:

```sh
python3 reproduce.py --tests-only
python3 reproduce.py --finite-only
python3 verify_release.py
```

## What is included

| Directory | Evidence |
|---|---|
| Root, `pilot`, `evaluation` | Original medium comparison; 400 retained evaluation rows |
| `adaptive-medium` | Locally adjusted pathways; 160 rows |
| `remote-information` | Addressed reports; 160 rows |
| `participant-authority` | Recognition, coupling authority, independent-donor replay; 200 rows |
| `composite-reservations` | Whole-job reservation; 80 rows |
| `reservation-replanning` | Bounded revision; 80 rows |
| `complementary-feasibility`, `attainable-service`, `reservation-lifecycle` | Finite capacity and commitment demonstrations |
| `execution-delay`, `delay-feasibility` | Delay replay and an offline feasibility witness |
| `claim-specificity` | Supporting authority model and tests |

Read each study's report for its conditions, endpoints, and limitations. Exact reproduction establishes that the released code recreates these synthetic outputs; it does not establish the broader human or consciousness claims under investigation.

## Provenance and portability

`release-manifest.json` records original and published SHA-256 hashes for 691 copied source/result files. Private machine paths in reports and metadata were replaced with repository-relative labels. Two runners' source-location expressions were made relative to this package; simulation rules were unchanged. The manifest identifies each changed file.

Historical freeze manifests preserve the original run's hashes. They are provenance records, not checksums for this relocated release. Do not use a historical freeze to certify changed paths or the new wrapper. `verify_release.py` instead verifies the current release against `checksums.json`. The reproduction wrapper creates fresh freezes for temporary delay runs and compares resulting data with retained outputs.

The new wrapper, release documentation, checksum verifier, and verification record are release additions. They are covered by `checksums.json`; the checksum file itself is anchored by the Git commit. The original private working files remain unchanged.

## Release verification

The full command passed on November 10, 2026: 57 tests, all 1,080 simulation rows, and five finite result objects matched. See [machine-readable verification](release-verification.json). This command does not regenerate every historical pilot or bootstrap interval; those retained artifacts remain individually hashed.
