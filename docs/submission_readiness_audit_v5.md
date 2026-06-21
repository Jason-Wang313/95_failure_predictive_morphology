# Submission Readiness Audit v5

Paper: 95 failure_predictive_morphology

Date: 2026-06-22 Asia/Shanghai

Terminal decision: KILL_ARCHIVE

## Evidence Inventory

- Main rollout rows: 322,560.
- Dataset summary rows: 23,040.
- Main seed-metric rows: 1,120.
- Main metric rows: 1,568.
- Main pairwise rows: 1,344.
- Hard aggregate seed rows: 140.
- Hard aggregate metric rows: 196.
- Hard aggregate pairwise rows: 168.
- Ablation rollout rows: 115,200.
- Ablation metric rows: 140.
- Stress raw rows: 259,200.
- Stress metric rows: 1,008.
- Fixed-risk raw rows: 138,240.
- Fixed-risk metric rows: 288.
- Negative cases: 24.

## Main Finding

V5 improves dominant-failure prediction but loses the deployment claim.

| Criterion | V5 | Best reference | Gate |
| --- | ---: | ---: | --- |
| Success | 0.56302 | 0.70521 online_system_identification | fail |
| Prediction accuracy | 0.69462 | 0.62604 non-v5 reference | pass |
| Safety violation | 0.11198 | 0.02587 conformal_risk_shield | fail |
| Regret | 0.20755 | 0.16782 online_system_identification | fail |
| Utility | 0.15027 | 0.37566 online_system_identification | fail |
| Ablation | full v5 | online_adaptation_only | fail |

## Manuscript Validation

- PDF: `C:/Users/wangz/Downloads/95.pdf`.
- Pages: 30.
- SHA256: `3DD7C8EE18B03A34E5DE903EB93067F7CE64396EB76E4E7D21C3E3F859B1802B`.
- Bright boxed clickable citations: enabled through `hyperref` border settings.
- Desktop PDF copy: absent.
- Validator: `python scripts/validate_submission_artifacts.py` passed.

## Decision

The paper should not be submitted to ICLR main. The archive is useful as a negative benchmark and as a concrete specification of what a future morphology-failure paper must beat.
