# Final Audit

1. Chosen thesis: Failure-Predictive Morphology tests whether morphology-conditioned failure-family prediction improves controller selection under embodiment shift.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v5 expanded negative evidence audit.
4. Last update: 2026-06-22 Asia/Shanghai.
5. Evidence: deterministic CPU-only morphology-failure benchmark with 10 seeds, 6 morphologies, 6 tasks, 8 splits, 14 methods, ablations, stress sweeps, fixed-risk budgets, paired confidence intervals, and negative cases.
6. Main rollout rows: 322,560.
7. Ablation rollout rows: 115,200.
8. Stress-sweep raw rows: 259,200.
9. Fixed-risk raw rows: 138,240.
10. Strongest non-oracle deployment baseline: online_system_identification.
11. Hard aggregate evidence: online system identification reaches 0.70521 task success; v5 reaches 0.56302.
12. Prediction evidence: v5 reaches 0.69462 dominant-failure accuracy; best non-v5 reference reaches 0.62604.
13. Safety evidence: conformal risk shielding reaches 0.02587 safety violation; v5 reaches 0.11198.
14. Regret evidence: online system identification reaches 0.16782 regret; v5 reaches 0.20755.
15. Utility evidence: online system identification reaches 0.37566 robust utility; v5 reaches 0.15027.
16. Ablation failure: `online_adaptation_only` is the best ablation.
17. Gate vector: success false, prediction true, safety false, regret false, utility false, ablation false, stress true, fixed-risk true, scope false.
18. Manuscript: 30 pages, bright boxed clickable citations, 230-entry bibliography.
19. Validation: `python scripts/validate_submission_artifacts.py` passed.
20. Exact Downloads PDF path: `C:/Users/wangz/Downloads/95.pdf`.
21. PDF SHA256: `3DD7C8EE18B03A34E5DE903EB93067F7CE64396EB76E4E7D21C3E3F859B1802B`.
22. GitHub URL: https://github.com/Jason-Wang313/95_failure_predictive_morphology.
23. Confirmation: no visible Desktop PDF copy was requested or made.
24. Claim-validity status: ICLR-main claim killed; archive retained as a negative evidence report.
