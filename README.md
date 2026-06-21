# 95 Failure-Predictive Morphology

Submission-hardening version: v5 expanded negative evidence audit.

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository is a hostile-review audit for the generated robotics idea:

> Predict which morphology-specific constraints will dominate policy failure, then use that prediction to select safer controllers or interventions.

The expanded v5 protocol tests the strongest local CPU-only version of the claim with 6 morphologies, 6 tasks, 8 distribution splits, 14 methods, 10 seeds, 322,560 main rollouts, 115,200 ablation rollouts, 259,200 stress-sweep rollouts, and 138,240 fixed-risk rollouts.

The result is negative. The v5 method improves the explicit prediction target, but the closed-loop robotics claim fails against adaptive/control baselines.

| Method | Hard success | Failure accuracy | Safety violation | Regret | Robust utility |
| --- | ---: | ---: | ---: | ---: | ---: |
| online_system_identification | 0.705 | 0.558 | 0.083 | 0.168 | 0.376 |
| cost_calibrated_failure_predictive_morphology_v5 | 0.563 | 0.695 | 0.112 | 0.208 | 0.150 |
| conformal_risk_shield | 0.530 | 0.262 | 0.026 | 0.280 | 0.008 |

Gate outcome:

- success_gate=False
- prediction_gate=True
- safety_gate=False
- regret_gate=False
- utility_gate=False
- ablation_gate=False
- stress_gate=True
- fixed_risk_gate=True
- scope_gate=False

The useful negative: better morphology-failure labels are not enough when online system identification and adaptive control produce better execution tradeoffs.

## Reproduce

```powershell
python src\run_experiment.py
python scripts\generate_manuscript.py
python scripts\validate_submission_artifacts.py
```

Canonical local PDF: `C:/Users/wangz/Downloads/95.pdf`

Final validated PDF:

- Pages: 30
- SHA256: `3DD7C8EE18B03A34E5DE903EB93067F7CE64396EB76E4E7D21C3E3F859B1802B`
- Desktop copy: forbidden and absent.
