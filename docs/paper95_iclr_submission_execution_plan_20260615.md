# Paper 95 ICLR-Main Submission Execution Plan

Date: 2026-06-15
Paper: `95_failure_predictive_morphology`
Repository: `https://github.com/Jason-Wang313/95_failure_predictive_morphology`

## Goal

Rebuild and audit Paper 95 under an ICLR-main submission standard, while refusing to upgrade the paper unless morphology-conditioned failure prediction improves closed-loop execution beyond online system identification, constraint-aware MPC, conformal shielding, and red-team retrieval. Better failure-family labels are not enough unless they improve what the robot does.

## Current Starting State

- The repository is on `main` at commit `d4c2ae188a9ceca7919085d9e776edf8c8a80876`.
- The existing v4 audit is terminally negative: `KILL_ARCHIVE`.
- Existing evidence reports that the proposed method improves dominant failure-family accuracy.
- Existing evidence also reports that `online_system_identification` wins the combined-stress closed-loop task-success gate and has lower regret.
- Existing evidence reports ablation contradictions: `minus_calibration` and `minus_intervention_cost_model` beat the full method on task success.
- `C:/Users/wangz/Downloads/95.pdf` exists.
- `C:/Users/wangz/Desktop/95.pdf` does not exist and must not be created.

## Execution Steps

1. Re-run `python -m py_compile src/run_experiment.py`.
2. Re-run `python src/run_experiment.py` and save the full console transcript to the batch log directory.
3. Verify that the rerun regenerates aggregate metrics, per-morphology/task metrics, seed metrics, ablations, stress sweeps, pairwise stats, failure cases, LaTeX tables, and figures.
4. Independently audit the result CSVs with pandas instead of trusting the prose summary.
5. Compare `proposed_failure_predictive_morphology` against the strongest non-oracle baselines on:
   - combined-stress task success;
   - dominant failure-family accuracy;
   - top-2 recall;
   - dominant-failure rate;
   - safety violation rate;
   - intervention cost;
   - unnecessary intervention rate;
   - planning regret;
   - maximum-stress robustness.
6. Check whether internal ablations isolate the morphology-conditioned prediction mechanism.
7. Update the paper and documentation with measured claims only.
8. Rebuild `paper/main.pdf` with `pdflatex` and copy the final artifact only to `C:/Users/wangz/Downloads/95.pdf`.
9. Scan the LaTeX log for real warnings/errors and fix recoverable typesetting problems.
10. Update the root batch ledgers after the child repo is correct.
11. Commit, push, and verify the public GitHub repository.
12. Confirm the child git tree is clean, `origin/main` matches local `HEAD`, the numbered PDF exists in Downloads, and no Desktop PDF exists.

## Submission-Readiness Gates

Paper 95 may be marked `STRONG_REVISE` only if all gates pass:

1. The proposed morphology-conditioned predictor beats the strongest non-oracle baseline on combined-stress task success.
2. It also reduces dominant-failure rate, safety violations, or planning regret without excessive intervention cost.
3. Its failure-family prediction accuracy or top-2 recall gain translates into better closed-loop execution.
4. Core ablations degrade in the expected directions and do not beat the full method on task success.
5. Maximum-stress curves do not reverse in favor of online system identification, constraint-aware MPC, conformal shielding, red-team retrieval, or domain-randomized policy selection.
6. The paper clearly labels the evidence as local simulated evidence and does not imply robot hardware validation.

If online system identification remains stronger on closed-loop task success or regret, the terminal decision remains `KILL_ARCHIVE` even if the proposed method has better failure-family accuracy.

## Expected Honest Outcome

The prior v4 evidence already suggests a likely `KILL_ARCHIVE` decision because better morphology-failure prediction does not translate into better execution. The continuation rerun must verify that result from regenerated evidence rather than preserving it by inertia.

## Deliverables

- Updated rerun log in `C:/Users/wangz/robotics_massive_pool_paper_factory/logs/`.
- Updated Paper 95 result CSVs, LaTeX tables, and figures if regenerated content changes.
- Updated child documentation and paper source with the rerun audit.
- Final numbered PDF at `C:/Users/wangz/Downloads/95.pdf` only.
- Updated root ledgers through Paper 95.
- Public GitHub repo pushed and verified clean.
