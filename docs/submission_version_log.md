# Submission Version Log

## v1 - Generated Draft

- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening

- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Recompiled canonical PDF at `C:/Users/wangz/Downloads/95.pdf`.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive

- Applied the stricter ICLR-main-conference standard.
- Re-read local paper, docs, experiments, prior-work artifacts, PDF state, and repo state.
- Determined that missing real-robot/high-fidelity evidence, template-generated experiments, and unresolved novelty threats were not recoverable from local artifacts.
- Recompiled the canonical PDF with `Submission-hardening version: v3`.
- Terminal decision: KILL_ARCHIVE.

## v4 - Paper-Specific Evidence Audit

- Added a concrete Paper 95 rebuild plan before experiments.
- Replaced the generic probability scaffold with a deterministic morphology-failure benchmark.
- Tested five morphologies, five tasks, five splits, nine methods, seven seeds, ablations, stress sweeps, paired comparisons, and failure cases.
- Generated paper-specific figures and LaTeX tables.
- Found that better morphology-failure prediction does not beat online system identification on closed-loop success or regret.
- Terminal decision remains: KILL_ARCHIVE.

## v4.1 - 2026-06-15 Rerun Audit

- Re-ran `python -m py_compile src\run_experiment.py` and the full `python src\run_experiment.py`.
- Confirmed online system identification remains the strongest non-oracle combined-stress success baseline.
- Confirmed proposed-minus-online-system-ID task-success difference is `-0.03690 +/- 0.00928`.
- Confirmed the proposed method improves accuracy by `+0.08839 +/- 0.01025` but has worse safety violation and regret.
- Confirmed `minus_calibration` and `minus_intervention_cost_model` beat the full method on task success.
- Updated child docs and paper source to keep the v4 KILL_ARCHIVE decision evidence-bound.

## v5 - 2026-06-22 Expanded Negative Evidence Audit

- Froze `docs/paper95_expanded_submission_plan_20260622.md` before interpreting the expanded results.
- Replaced the v4.1 experiment with a 10-seed, 6-morphology, 6-task, 8-split, 14-method protocol.
- Generated 322,560 main rollout rows, 115,200 ablation rollout rows, 259,200 stress-sweep raw rows, and 138,240 fixed-risk raw rows.
- Added fixed-risk budgets, hard-aggregate paired tests, negative cases, and v5 figures.
- Rebuilt the manuscript into a 30-page ICLR-style archive with bright boxed clickable citations and 230 bibliography entries.
- Validated `C:/Users/wangz/Downloads/95.pdf` with SHA256 `3DD7C8EE18B03A34E5DE903EB93067F7CE64396EB76E4E7D21C3E3F859B1802B`.
- Terminal decision remains: KILL_ARCHIVE.
