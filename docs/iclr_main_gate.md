# ICLR Main Gate

Paper: 95 failure_predictive_morphology

Submission-hardening version: v4

Gate verdict: KILL_ARCHIVE

Evidence digest: v4 deterministic morphology-failure benchmark, seven seeds, five morphologies, five tasks, five splits, nine methods, ablations, stress sweep, paired confidence intervals, and failure cases.

Fatal blockers:

- The proposed method loses combined-stress task success to online system identification.
- Proposed task success is 0.582 +/- 0.007 vs 0.618 +/- 0.008 for online system identification.
- Proposed safety violation is 0.110 vs 0.090.
- Proposed planning regret is 0.211 vs 0.193.
- Two ablations beat the full method on task success.
- The evidence is local simulation rather than real robot or high-fidelity simulator validation.

The only honest main-conference-safe decision is to archive rather than overclaim.
