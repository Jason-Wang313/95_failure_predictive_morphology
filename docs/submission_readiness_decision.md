# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

## Why It Fails

The strongest defensible claim is that morphology-conditioned prediction should identify the dominant failure family early enough to improve closed-loop controller selection under embodiment shift. The expanded v5 benchmark does not support that claim.

The proposed v5 method predicts failure families well, but the stronger closed-loop baseline still wins:

- online_system_identification hard success: 0.70521.
- cost_calibrated_failure_predictive_morphology_v5 hard success: 0.56302.
- V5 dominant-failure accuracy: 0.69462.
- V5 safety violation: 0.11198 vs 0.02587 for conformal risk shielding.
- V5 planning regret: 0.20755 vs 0.16782 for online system identification.
- V5 robust utility: 0.15027 vs 0.37566 for online system identification.
- `online_adaptation_only` is the best ablation.

## Honest Terminal Action

Archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

## Revival Condition

The idea would need a substantially new empirical project:

- Real robot or high-fidelity simulator evidence across multiple morphologies.
- Implemented morphology-conditioned predictors and external adaptive-control baselines.
- A mechanism that turns failure-family prediction into better closed-loop success, safety, regret, and utility than online system identification and constraint-aware MPC.
- Manual related-work synthesis and qualitative rollouts.
- A new terminal gate showing the full method beats ablations and strong baselines under maximum stress and fixed-risk budgets.
