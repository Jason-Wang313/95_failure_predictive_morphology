# Paper 95 Expanded Submission-Readiness Plan

Date frozen: 2026-06-22

Paper: `95_failure_predictive_morphology`

Target venue posture: ICLR-main hostile-review audit. The goal is not to make the result look pretty. The goal is to test whether morphology-conditioned failure prediction survives strong baselines, stress, ablations, fixed-risk deployment, and reviewer attack.

## Core Question

Can a robot predict which morphology-specific constraint family will dominate failure early enough to select a controller or intervention that improves closed-loop success, safety, regret, and utility under embodiment and environment shift?

The v4.1 audit found that prediction accuracy improved, but online system identification still won the closed-loop gate. The v5 audit must test a stronger version without relaxing the standard.

## Method Under Audit

`cost_calibrated_failure_predictive_morphology_v5`

The v5 method may use:

- Morphology descriptors.
- Task-conditioned constraint-family logits.
- Early-warning lead-time estimates.
- Intervention cost calibration.
- Risk-aware controller selection.
- Confidence-gated abstention.
- Failure-history correction.

The method is not allowed to win by silently discarding safety, regret, intervention burden, fixed-risk coverage, or strong adaptive baselines.

## CPU/RAM-Light Expanded Protocol

Main evaluation:

- Seeds: 10.
- Morphologies: 6.
- Tasks: 6.
- Splits: 8.
- Methods: 14.
- Episodes per cell: 8.
- Expected main rollout rows: 322,560.
- Expected seed-metric rows: 4,032.
- Expected aggregate metric rows: 1,568.
- Expected paired rows: at least 1,344.

Morphologies:

- differential_drive
- quadruped
- arm_gripper
- aerial_manipulator
- underwater_vehicle
- soft_snake_robot

Tasks:

- tight_turn_navigation
- payload_transport
- gap_or_step_crossing
- precision_contact_manipulation
- disturbance_recovery
- cluttered_tool_use

Splits:

- nominal_morphology
- payload_shift
- terrain_or_fluid_shift
- actuator_degradation_shift
- sensor_dropout_shift
- contact_geometry_shift
- low_signal_morphology_stress
- combined_failure_stress

Methods:

- generic_failure_classifier
- per_morphology_calibrated_predictor
- constraint_aware_mpc
- conformal_risk_shield
- domain_randomized_policy_selector
- online_system_identification
- meta_adaptive_mpc
- bayesian_morphology_belief
- retrieval_failure_memory
- morphology_failure_transformer_prior
- risk_aware_intervention_policy
- failure_predictive_morphology_v4
- cost_calibrated_failure_predictive_morphology_v5
- oracle_failure_family_controller

## Metrics

Prediction metrics:

- dominant_failure_accuracy
- top2_failure_recall
- calibration_error
- early_warning_lead_time
- cross_morphology_generalization_gap
- morphology_shift_detection
- failure_family_f1

Deployment metrics:

- task_success
- dominant_failure_rate
- safety_violation_rate
- intervention_cost
- unnecessary_intervention_rate
- planning_regret_to_oracle
- recovery_success
- robust_utility

Risk metrics:

- abstention_rate
- accepted_success
- accepted_safety_violation
- accepted_regret
- fixed-risk coverage

## Ablations

Run 10 ablations/variants on the hard splits:

- full_cost_calibrated_failure_predictive_morphology_v5
- minus_morphology_embedding
- minus_constraint_family_head
- minus_cost_calibration
- minus_confidence_gate
- minus_failure_history
- minus_online_correction
- morphology_only
- failure_history_only
- online_adaptation_only

Expected ablation rollout rows: 115,200.

## Stress Sweep

Run a six-level stress sweep over payload, terrain/fluid, actuator degradation, sensor dropout, contact tightness, morphology OOD shift, and intervention cost.

Expected stress raw rows: 259,200.

Stress gate:

- V5 must not be dominated by online_system_identification, meta_adaptive_mpc, conformal_risk_shield, or constraint_aware_mpc at maximum stress.
- If prediction accuracy remains high but utility degrades, report the negative mechanism honestly.

## Fixed-Risk Deployment

Budgets:

- 0.00
- 0.05
- 0.10
- 0.15

Hard splits:

- low_signal_morphology_stress
- combined_failure_stress

Methods:

- cost_calibrated_failure_predictive_morphology_v5
- online_system_identification
- meta_adaptive_mpc
- conformal_risk_shield
- constraint_aware_mpc
- risk_aware_intervention_policy

Expected fixed-risk raw rows: 138,240.

Fixed-risk gate:

- At budget 0.05, V5 must have nonzero useful coverage.
- Accepted success must not trail the strongest accepted baseline.
- If coverage collapses or accepted utility is poor, mark the gate failed.

## Required Gates

V5 can only be `STRONG_REVISE` if all of these pass:

- `success_gate`: V5 beats the best non-oracle hard-split success baseline by a practical margin or a paired positive lower bound.
- `prediction_gate`: V5 is best or statistically tied-best on dominant-failure accuracy and top-2 recall.
- `safety_gate`: V5 does not increase safety violations relative to the strongest safe baseline.
- `regret_gate`: V5 does not increase regret relative to online/adaptive control baselines.
- `utility_gate`: V5 is on the hard robust-utility frontier.
- `ablation_gate`: the full method is necessary; stripped variants cannot match or beat it on the deployment objective.
- `stress_gate`: V5 survives maximum stress without being dominated.
- `fixed_risk_gate`: V5 has useful coverage and accepted performance at budget 0.05.
- `scope_gate`: evidence is not overclaimed as real robot or high-fidelity validation.

If any critical deployment gate fails, the terminal state must be `KILL_ARCHIVE` unless the evidence supports only a clearly bounded `STRONG_REVISE`.

## Manuscript Requirements

- 25+ page ICLR-style PDF.
- Bright boxed clickable citations routed to the bibliography.
- 120+ bibliography entries from `docs/deep_read_250.csv`.
- Formal problem setup for morphology-conditioned failure-family prediction.
- Theory notes showing why prediction accuracy alone is insufficient for closed-loop improvement.
- Tables for row counts, hard aggregate, paired tests, ablations, stress, fixed risk, split frontiers, baseline rejection, and negative cases.
- Honest limitations: local deterministic benchmark, no real robot, no high-fidelity simulator, no learned checkpoint release, no independent reproduction.

## Artifact Requirements

- Numbered PDF only at `C:/Users/wangz/Downloads/95.pdf`.
- No visible Desktop PDF.
- `scripts/generate_manuscript.py`.
- `scripts/validate_submission_artifacts.py`.
- Updated README/status/checklist/audit docs.
- Public GitHub repo pushed and verified.
- Root ledgers updated only after Paper 95 repo validation and push.

## Frozen Decision Rule

Report all predefined results honestly. Do not optimize for pretty results. Optimize for a result that survives hostile review.

If V5 improves prediction but online/adaptive/control baselines remain better for success, safety, regret, robust utility, fixed-risk coverage, or ablation necessity, the correct terminal decision is `KILL_ARCHIVE`.
