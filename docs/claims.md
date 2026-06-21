# Claims

## Claim Tested

A morphology-conditioned predictor can identify the constraint family that will dominate failure before execution, then use that prediction to choose safer controllers or interventions under embodiment and environment shift.

## Supported Claims

- The v5 benchmark is expanded and reproducible: 6 morphologies, 6 tasks, 8 splits, 14 methods, 10 seeds, ablations, stress sweeps, fixed-risk budgets, paired tests, and negative cases.
- The v5 method improves the explicit diagnostic target on the hard aggregate: dominant-failure accuracy is 0.69462.
- The old v4 mechanism is improved by cost calibration, morphology conditioning, online correction, and constraint-family modeling.
- Fixed-risk and stress gates are now reported explicitly rather than hidden.

## Measured Negative Claim

The prediction advantage does not translate into a closed-loop robotics win:

- Task success: 0.56302 for v5 vs 0.70521 for online system identification.
- Safety violation: 0.11198 for v5 vs 0.02587 for conformal risk shielding.
- Planning regret: 0.20755 for v5 vs 0.16782 for online system identification.
- Robust utility: 0.15027 for v5 vs 0.37566 for online system identification.
- Best ablation: `online_adaptation_only`, not the full v5 mechanism.

## Unsupported Claims Explicitly Avoided

- No claim of ICLR-main submission readiness.
- No claim of real-robot validation.
- No claim of high-fidelity simulator validation.
- No claim that morphology-failure prediction is sufficient for robust execution.
- No claim of state-of-the-art failure prediction or control.
- No claim that the 30-page manuscript is submittable despite the terminal KILL_ARCHIVE result.
