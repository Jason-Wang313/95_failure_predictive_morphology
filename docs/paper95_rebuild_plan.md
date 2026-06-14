# Paper 95 Rebuild Plan: Failure-Predictive Morphology

Timestamp: 2026-06-14 16:24:57 +01:00

## Starting Point

Paper 95 is currently a v3 archive. The original research bet is:

> Predict which morphology-specific constraints will dominate policy failure.

The current repo contains a generic synthetic probability scaffold, not a morphology-specific robotics benchmark. The hostile prior-work pressure is strong: model predictive control under kinodynamic constraints, adaptive/sliding-mode constrained control, red-teaming robot policies, failure-aware RL, robust task planning, and morphology-specific planning already cover much of the obvious territory. The rebuild cannot claim novelty from "predict failures" or "condition on morphology." It must show that explicit morphology-failure bottleneck prediction improves downstream policy selection/adaptation over strong constraint-aware and risk-aware baselines.

## Rebuilt Claim Under Test

The strongest defensible claim is:

> A morphology-conditioned predictor can identify the constraint family that will dominate failure before execution, enabling policy selection or intervention that reduces closed-loop failures under embodiment and environment shift.

This is a local evidence audit, not hardware validation.

## Benchmark Design

I will replace the template scaffold with a deterministic morphology-failure benchmark. Each episode samples a robot body, task, environment, and hidden bottleneck. Methods predict the dominant failure morphology/constraint and select a controller or intervention before executing.

Morphologies:

1. `differential_drive`
2. `quadruped`
3. `arm_gripper`
4. `aerial_manipulator`
5. `underwater_vehicle`

Tasks:

1. `tight_turn_navigation`
2. `payload_transport`
3. `gap_or_step_crossing`
4. `precision_contact_manipulation`
5. `disturbance_recovery`

Splits:

1. `nominal_morphology`
2. `payload_shift`
3. `terrain_or_fluid_shift`
4. `actuator_degradation_shift`
5. `combined_failure_stress`

Dominant failure families:

1. `kinodynamic_limit`
2. `traction_or_slip`
3. `payload_inertia`
4. `actuator_saturation`
5. `contact_geometry`
6. `state_estimation_dropout`
7. `energy_budget`

## Methods To Compare

Strong baselines:

1. `generic_failure_predictor`
2. `per_morphology_calibrated_predictor`
3. `constraint_aware_mpc`
4. `conformal_risk_shield`
5. `domain_randomized_policy_selector`
6. `online_system_identification`
7. `red_team_failure_retrieval`
8. `proposed_failure_predictive_morphology`
9. `oracle_failure_family`

## Metrics

Prediction metrics:

1. Dominant failure-family accuracy.
2. Top-2 failure-family recall.
3. Calibration error.
4. Early-warning lead time.
5. Cross-morphology generalization gap.

Closed-loop metrics:

1. Task success.
2. Dominant-failure rate.
3. Safety violation rate.
4. Intervention cost.
5. Unnecessary intervention rate.
6. Planning regret to oracle.

Statistics:

1. Seven deterministic seeds.
2. Per-task and per-morphology means with 95 percent confidence intervals.
3. Paired seed/task/morphology comparison against the strongest non-oracle baseline.
4. Explicit terminal decision in `results/summary.txt`.

## Ablations

The full method must beat stripped variants:

1. `full_failure_predictive_morphology`
2. `minus_morphology_embedding`
3. `minus_constraint_family_head`
4. `minus_calibration`
5. `minus_intervention_cost_model`
6. `morphology_only`
7. `failure_history_only`

If stripped variants match or beat full on closed-loop success or failure reduction, the mechanism is not supported.

## Stress Tests

Stress axes:

1. Payload mass/inertia shift.
2. Terrain or fluid drag shift.
3. Actuator degradation.
4. Sensor dropout.
5. Contact-geometry tightness.
6. Combined maximum stress.

The stress sweep must show whether morphology-failure prediction remains useful when constraint-aware MPC, conformal risk, and online system identification degrade.

## Paper Rewrite Requirements

After experiments:

1. Rewrite `paper/main.tex` as either a strong-revise evidence report or a negative evidence audit.
2. Replace template claims with measured claims only.
3. Include tables for combined stress, ablations, pairwise decision, and failure cases.
4. Include figures for prediction quality, closed-loop outcomes, cost/regret, ablations, and stress curves.
5. Update README, child status, claims, final audit, and submission-readiness docs.
6. Build only `C:/Users/wangz/Downloads/95.pdf`; do not copy anything to Desktop.
7. Commit and push to `https://github.com/Jason-Wang313/95_failure_predictive_morphology`.

## Terminal Gate

Mark `STRONG_REVISE` only if all of the following are true:

1. `proposed_failure_predictive_morphology` beats the strongest non-oracle baseline on combined-stress task success and dominant-failure reduction.
2. It also improves dominant failure-family accuracy or top-2 recall without unacceptable intervention cost or unnecessary interventions.
3. Core ablations degrade in expected directions.
4. Maximum-stress curves do not reverse in favor of constraint-aware MPC, conformal risk shielding, online system identification, or red-team retrieval.
5. The paper honestly states the evidence is local/simulated and not robot hardware validation.

Otherwise mark `KILL_ARCHIVE`. A morphology-conditioned predictor that is matched or beaten by per-morphology calibration, constraint-aware control, online system ID, or conformal shields is not ICLR-main ready.
