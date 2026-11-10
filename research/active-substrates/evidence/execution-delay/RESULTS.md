# The saved revision advantage is fragile to execution delays

The earlier reservation study improved completion by 3.333 percentage points under exact durations. Replaying those same saved schedules under a fixed synthetic overrun distribution reduces the difference to **+0.162 percentage points**, with a workload-paired 95% bootstrap interval of **−0.697 to +1.174 points**. Two previously winning workloads now favor the append-only schedule in expectation. The result does not establish an advantage under this delay model.

This is a post-hoc sensitivity analysis, not a new policy trial or independent replication. Each operation independently has a 25% chance of taking one extra tick. All 64 delay vectors per workload are enumerated exactly and shared across the two schedules. Crews, queues, commitments and planned timing lower bounds remain fixed; delays propagate through physical travel, agent occupancy and prerequisites. All reserved work executes, including work that becomes late. Nothing is rerouted, cancelled or newly admitted in response to delay.

## Outcomes

| Measure | Append-only plans | Revised plans |
|---|---:|---:|
| Nominal mean whole jobs, of 3 | 2.300 | 2.400 |
| Expected whole jobs with delays | 2.07178 | 2.07664 |
| Expected offered-job completion | 69.059% | 69.221% |
| Expected late operations | 0.23525 | 0.34006 |
| Expected work occupancy, ticks | 7.825 | 8.125 |
| Expected last finish, tick | 6.80906 | 7.01133 |

Across forty workload expectations, revision has two positive differences, thirty-six ties and two negative differences. The four changed workloads are:

| Seed | Expected jobs, append | Expected jobs, revise | Difference in offered-job completion |
|---|---:|---:|---:|
| 18004 | 1.99609 | 2.18652 | +6.3477 points |
| 18026 | 1.93750 | 1.78125 | −5.2083 points |
| 18028 | 1.00000 | 1.42188 | +14.0625 points |
| 18035 | 2.00000 | 1.73828 | −8.7240 points |

The bootstrap resamples forty paired workload expectations, not the 2,560 noise vectors. Enumeration removes Monte Carlo error conditional on these workloads and this chosen distribution; it does not remove workload uncertainty or validate the chosen delay rate.

## A concrete reversal

In [seed 18035](first-results/workload-18035.json), a single extra tick on operation `1-0` leaves the append-only schedule completing jobs 1 and 2. Its revised schedule completes only job 2: the inserted job0 continuation finishes at tick6 and the displaced job1 continuation at tick8, both late. The revision had increased nominal service by filling the available schedule tightly enough that one upstream overrun removes two whole-job completions.

This demonstrates a distinction the nominal count objective cannot express: one additional promised completion can come with less tolerance for delay in existing commitments. It does not show that revision itself is harmful. Other revised schedules still gain under the same noise, and these plans never respond to observed execution. A future comparison should evaluate a rule that prices deadline slack or failure risk against nominal service, using new workloads and an explicitly causal execution model. Selecting a new rule on these forty cases would be development, not held-out validation.

## Evidence and scope

[Specification](SPECIFICATION.md) and executable hashes were frozen before this analysis. Six focused tests cover zero delay, deadline equality, travel/queue blocking, cross-agent dependency delay, slack absorption, missing stages, invalid delays and work continuing beyond the old horizon. All eighty retained zero-delay schedules reproduce their nominal timestamps and service exactly. [Independent trace verification](verify.py) checks all 5,120 realized schedules for resource occupancy, travel, prerequisites, duration and whole-job scoring without calling the replay engine or either policy.

[Summary](first-results/summary.json), [paired expectations](first-results/paired.json) and every delay vector's realized events are retained. All 653 earlier research artifacts remain checksum-identical. The previous evidence ZIP is a frozen earlier checkpoint and does not include this addition.

The original offline oracle uses nominal durations and is not a delayed attainable-service bound. No delayed optimality gap is claimed. The analysis also does not simulate adaptive execution, decentralized coordination, heterogeneous teams, real disruption probabilities or physical cancellation costs. Its supported conclusion is narrower and useful: the earlier sparse nominal gain does not establish reliable service under even this simple specified overrun process.
