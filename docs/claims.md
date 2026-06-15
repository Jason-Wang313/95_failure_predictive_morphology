# Claims

## Claim Tested

A morphology-conditioned predictor can identify the constraint family that will dominate failure before execution, enabling controller selection or intervention that reduces closed-loop failures under embodiment and environment shift.

## Supported Claims

- The v4.1 rerun confirms the benchmark is reproducible and paper-specific: five morphologies, five tasks, five distribution shifts, nine methods, seven seeds, ablations, stress curves, paired comparisons, and failure cases.
- The proposed method has the best non-oracle dominant failure-family accuracy under combined stress: 0.644 vs 0.555 for online system identification.
- The proposed method reduces dominant failure rate relative to online system identification: 0.174 vs 0.191.

## Measured Negative Claim

The prediction advantage does not translate into a decisive closed-loop robotics win:

- Task success: 0.582 +/- 0.007 vs 0.618 +/- 0.008 for online system identification.
- Safety violation: 0.110 vs 0.090.
- Planning regret: 0.211 vs 0.193.
- Paired proposed-minus-online-system-ID success difference: -0.03690 +/- 0.00928.
- `minus_calibration` and `minus_intervention_cost_model` beat the full method on success in the ablation table.

## Unsupported Claims Explicitly Avoided

- No claim of ICLR-main submission readiness.
- No claim of real-robot validation.
- No claim of high-fidelity simulator validation.
- No claim that morphology-failure prediction is sufficient for robust execution.
- No claim of state-of-the-art failure prediction or control.
