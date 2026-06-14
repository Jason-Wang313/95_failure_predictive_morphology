# Submission Attack Log

Paper: 95 failure_predictive_morphology

This v4 pass applies the ICLR main-conference bar with a paper-specific morphology-failure benchmark. The result is an honest archive decision, not a workshop resubmission.

## Attack 1: Prediction accuracy may not improve closed-loop execution.

Verdict: Confirmed.

Evidence: proposed_failure_predictive_morphology has higher dominant-failure accuracy than online_system_identification, 0.644 vs 0.555, but lower task success, 0.582 vs 0.618.

Action: Kill/archive. The central claim requires execution gains, not only better labels.

## Attack 2: Online system identification may adapt better than pre-execution failure-family prediction.

Verdict: Confirmed.

Evidence: online_system_identification is the strongest non-oracle success baseline under combined stress. Paired proposed-minus-online-system-ID success difference is -0.03690 +/- 0.00928 over 175 morphology/task/seed groups.

Action: Kill/archive.

## Attack 3: The proposed method may be less safe.

Verdict: Confirmed.

Evidence: proposed safety violation is 0.110 vs 0.090 for online system identification; paired difference is +0.02030 +/- 0.00581.

Action: Do not claim safety improvement.

## Attack 4: The full mechanism may be contradicted by ablations.

Verdict: Confirmed.

Evidence: `minus_intervention_cost_model` and `minus_calibration` beat the full proposed method on task success in the ablation table.

Action: Kill/archive. Ablation contradictions are fatal for an ICLR-main mechanism claim.

## Attack 5: Constraint-aware MPC and conformal shields may remain safer.

Verdict: Confirmed.

Evidence: constraint_aware_mpc safety violation is 0.077 and conformal_risk_shield safety violation is 0.058, both lower than the proposed 0.110, although they have lower task success.

Action: State the safety tradeoff honestly.

## Attack 6: Prior work already covers constrained MPC, robust planning, failure recovery, and red-team policy testing.

Verdict: Still true.

Evidence: hostile pool includes constrained MPC variants, MPC-MPNet, robust task planning/failure recovery, red-teaming VLA policies, and failure-aware RL.

Action: Do not claim novelty from generic failure prediction or morphology conditioning alone.

## Attack 7: The evidence is local simulation only.

Verdict: Still true.

Evidence: the v4 benchmark is reproducible and paper-specific, but it is not real robot or high-fidelity simulator validation.

Action: Frame as a negative evidence audit, not a submission.

## Attack 8: No meaningful recoverable ICLR-main issue remains after the negative result.

Verdict: Terminal condition reached.

Action: Mark KILL_ARCHIVE and stop Paper 95 after public repo/PDF/report updates.
