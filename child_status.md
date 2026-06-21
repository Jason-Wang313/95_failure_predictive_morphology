# Child Status 95

Current stage: ICLR main v5 expanded audit terminal
Last update: 2026-06-22 Asia/Shanghai
PDF: C:/Users/wangz/Downloads/95.pdf
GitHub: https://github.com/Jason-Wang313/95_failure_predictive_morphology
Submission-hardening version: v5 expanded negative evidence audit
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Evidence digest:

- Frozen plan: `docs/paper95_expanded_submission_plan_20260622.md`.
- Main rollout rows: 322,560.
- Dataset summary rows: 23,040.
- Main aggregate metric rows: 1,568.
- Hard aggregate metric rows: 196.
- Ablation rollout rows: 115,200.
- Stress-sweep raw rows: 259,200.
- Fixed-risk raw rows: 138,240.
- Negative cases: 24.
- Manuscript: 30 pages, bright boxed clickable citations, canonical PDF in Downloads only.
- PDF SHA256: `3DD7C8EE18B03A34E5DE903EB93067F7CE64396EB76E4E7D21C3E3F859B1802B`.

Hard aggregate result:

- V5 success: 0.56302 vs online system identification 0.70521.
- V5 dominant-failure accuracy: 0.69462 vs best non-v5 reference 0.62604.
- V5 safety violation: 0.11198 vs conformal shield 0.02587.
- V5 regret: 0.20755 vs online system identification 0.16782.
- V5 utility: 0.15027 vs online system identification 0.37566.

Reason:

The method now has much stronger local evidence and a real 30-page submission-style archive manuscript. The evidence still kills the ICLR-main claim: prediction improves, but adaptive/control baselines win deployment, safety, regret, utility, ablation, and scope gates.
