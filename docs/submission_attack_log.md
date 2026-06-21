# Submission Attack Log

Paper: 95 failure_predictive_morphology

This v5 pass applies the ICLR main-conference bar with an expanded paper-specific morphology-failure benchmark. The result is an honest archive decision, not a workshop resubmission.

## Attack 1: Prediction accuracy may not improve closed-loop execution.

Verdict: Confirmed.

Evidence: cost_calibrated_failure_predictive_morphology_v5 has higher dominant-failure accuracy than online_system_identification, 0.695 vs 0.558, but lower task success, 0.563 vs 0.705.

Action: Kill/archive. The central claim requires execution gains, not only better labels.

## Attack 2: Online system identification may adapt better than pre-execution failure-family prediction.

Verdict: Confirmed.

Evidence: online_system_identification is the strongest non-oracle success and utility baseline on the hard aggregate: success 0.705, regret 0.168, utility 0.376. V5 reaches success 0.563, regret 0.208, utility 0.150.

Action: Kill/archive.

## Attack 3: The proposed method may be less safe.

Verdict: Confirmed.

Evidence: v5 safety violation is 0.112, while conformal_risk_shield reaches 0.026.

Action: Do not claim safety improvement.

## Attack 4: The full mechanism may be contradicted by ablations.

Verdict: Confirmed.

Evidence: `online_adaptation_only` is the best ablation, beating the full v5 mechanism on the deployment objective.

Action: Kill/archive. Ablation contradictions are fatal for an ICLR-main mechanism claim.

## Attack 5: Constraint-aware MPC and conformal shields may remain safer.

Verdict: Confirmed.

Evidence: constraint_aware_mpc safety violation is 0.051 and conformal_risk_shield safety violation is 0.026, both lower than v5's 0.112.

Action: State the safety tradeoff honestly.

## Attack 6: Prior work already covers constrained MPC, robust planning, failure recovery, and red-team policy testing.

Verdict: Still true.

Evidence: hostile pool includes constrained MPC variants, MPC-MPNet, robust task planning/failure recovery, red-teaming VLA policies, and failure-aware RL.

Action: Do not claim novelty from generic failure prediction or morphology conditioning alone.

## Attack 7: The evidence is local simulation only.

Verdict: Still true.

Evidence: the v5 benchmark is reproducible and paper-specific, but it is not real robot or high-fidelity simulator validation.

Action: Frame as a negative evidence audit, not a submission.

## Attack 8: No meaningful recoverable ICLR-main issue remains after the negative result.

Verdict: Terminal condition reached.

Action: Mark KILL_ARCHIVE and stop Paper 95 after public repo/PDF/report updates.

## v5 Expanded Gate Round 9

Attack: The 2026-06-22 expanded run might show that prediction accuracy now translates into better execution.

Verdict: Failed. V5 reaches hard success `0.56302`, while `online_system_identification` reaches `0.70521`.

Action: Keep KILL_ARCHIVE.

## v5 Expanded Gate Round 10

Attack: Lower dominant-failure rate might compensate for lower task success.

Verdict: Failed for ICLR main. V5 improves failure-family accuracy, but safety violation rises to `0.11198`, regret rises to `0.20755`, and robust utility falls to `0.15027`.

Action: Preserve the diagnostic signal, not submission readiness.

## v5 Expanded Gate Round 11

Attack: Ablations might validate the full morphology-conditioned intervention policy.

Verdict: Failed. `online_adaptation_only` is the best ablation.

Action: Keep the negative audit and archive.
