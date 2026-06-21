# ICLR Main Gate

Paper: 95 failure_predictive_morphology

Submission-hardening version: v5 expanded negative evidence audit

Gate verdict: KILL_ARCHIVE

Latest rerun: 2026-06-22

Evidence digest: v5 deterministic morphology-failure benchmark with 10 seeds, 6 morphologies, 6 tasks, 8 splits, 14 methods, ablations, stress sweep, fixed-risk budgets, paired confidence intervals, and negative cases.

Gate vector:

- success_gate=False
- prediction_gate=True
- safety_gate=False
- regret_gate=False
- utility_gate=False
- ablation_gate=False
- stress_gate=True
- fixed_risk_gate=True
- scope_gate=False

Fatal blockers:

- V5 loses hard-aggregate task success to online system identification: 0.56302 vs 0.70521.
- V5 loses hard-aggregate robust utility to online system identification: 0.15027 vs 0.37566.
- V5 loses hard-aggregate regret to online system identification: 0.20755 vs 0.16782.
- V5 loses safety to conformal risk shielding: 0.11198 vs 0.02587.
- The best ablation is `online_adaptation_only`.
- The evidence is local simulation rather than real robot or high-fidelity simulator validation.

The only honest main-conference-safe decision is to archive rather than overclaim.
