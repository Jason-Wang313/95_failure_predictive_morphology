# Final Audit

1. Chosen thesis: Failure-Predictive Morphology tests whether morphology-conditioned failure-family prediction improves controller selection under embodiment shift.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v4.
4. Last update: 2026-06-14 20:19:33 +01:00.
5. Evidence: deterministic local morphology-failure benchmark with seven seeds, five morphologies, five tasks, five splits, nine methods, ablations, stress sweeps, paired confidence intervals, and failure cases.
6. Strongest non-oracle baseline: online_system_identification.
7. Combined-stress evidence: online system identification reaches 0.618 +/- 0.008 task success; the proposed method reaches 0.582 +/- 0.007.
8. Paired task/morphology/seed result: proposed minus online system identification is -0.03690 +/- 0.00928 for success, -0.01667 +/- 0.00750 for dominant failure rate, +0.02030 +/- 0.00581 for safety violations, +0.00327 +/- 0.00059 for cost, +0.01759 +/- 0.00248 for regret, and +0.08839 +/- 0.01025 for accuracy.
9. Main failure mode: prediction accuracy improves, but online adaptation and conservative control produce better execution tradeoffs.
10. Ablation failure: `minus_calibration` and `minus_intervention_cost_model` beat full on task success.
11. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, and `docs/hostile_reviewer_response.md`.
12. Reproducibility: `python src/run_experiment.py` regenerates the CSVs, figures, LaTeX tables, and terminal decision.
13. Claim-validity status: ICLR-main claim killed; archive retained as a negative evidence report.
14. Exact Downloads PDF path: `C:/Users/wangz/Downloads/95.pdf`.
15. GitHub URL: https://github.com/Jason-Wang313/95_failure_predictive_morphology.
16. Confirmation: no visible Desktop PDF copy was requested or made.
