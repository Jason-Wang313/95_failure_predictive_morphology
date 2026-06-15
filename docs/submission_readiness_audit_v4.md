# Submission Readiness Audit v4.1

Date: 2026-06-15

Paper: 95 Failure-Predictive Morphology

Terminal decision: KILL_ARCHIVE

## Commands Run

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
```

Both commands completed. The full experiment output was redirected to `logs/95_failure_predictive_morphology_continuation_rerun_20260615.log`.

## Evidence Coverage

- Aggregate metrics: 45 rows.
- Per-morphology/task metrics: 1,125 rows.
- Seed/morphology/task metrics: 7,875 rows.
- Pairwise gate rows: 6 rows.
- Ablation aggregate metrics: 7 rows.
- Ablation seed metrics: 1,225 rows.
- Stress sweep aggregates: 42 rows.
- Stress sweep seed metrics: 7,350 rows.
- Failure cases: 5 rows.
- Seeds: 0, 1, 2, 3, 4, 5, 6.
- Morphologies: `differential_drive`, `quadruped`, `arm_gripper`, `aerial_manipulator`, `underwater_vehicle`.
- Tasks: `tight_turn_navigation`, `payload_transport`, `gap_or_step_crossing`, `precision_contact_manipulation`, `disturbance_recovery`.
- Splits: `nominal_morphology`, `payload_shift`, `terrain_or_fluid_shift`, `actuator_degradation_shift`, `combined_failure_stress`.
- Methods: `generic_failure_predictor`, `per_morphology_calibrated_predictor`, `constraint_aware_mpc`, `conformal_risk_shield`, `domain_randomized_policy_selector`, `online_system_identification`, `red_team_failure_retrieval`, `proposed_failure_predictive_morphology`, `oracle_failure_family`.

## Main Gate

On combined failure stress, `proposed_failure_predictive_morphology` reaches task success `0.58155 +/- 0.00749`, dominant failure-family accuracy `0.64387`, dominant-failure rate `0.17440`, safety violation `0.11024`, intervention cost `0.03149`, and planning regret `0.21059`.

The strongest non-oracle closed-loop baseline is `online_system_identification`, which reaches task success `0.61845 +/- 0.00750`, dominant failure-family accuracy `0.55548`, dominant-failure rate `0.19107`, safety violation `0.08994`, intervention cost `0.02822`, and planning regret `0.19300`.

The paired proposed-minus-online-system-ID differences over 175 morphology/task/seed groups are:

- Task success: `-0.03690 +/- 0.00928`.
- Dominant-failure rate: `-0.01667 +/- 0.00750`.
- Safety violation: `+0.02030 +/- 0.00581`.
- Intervention cost: `+0.00327 +/- 0.00059`.
- Planning regret: `+0.01759 +/- 0.00248`.
- Dominant failure-family accuracy: `+0.08839 +/- 0.01025`.

## Contradictory Evidence

- The proposed method improves explicit failure-family prediction but loses the closed-loop task-success gate.
- The proposed method has higher safety violation and higher planning regret than online system identification.
- `minus_calibration` reaches task success `0.60482`, above the full method's ablation success `0.58042`.
- `minus_intervention_cost_model` reaches task success `0.61887`, also above the full method.
- At maximum stress, online system identification remains ahead on task success: `0.61112` versus proposed `0.57816`.
- The evidence remains local/simulated and lacks robot hardware or accepted high-fidelity morphology/control validation.

## Readiness Judgment

The paper is reproducible as a negative evidence audit. The proposed method has a real prediction-quality signal, but the paper is not submission-ready for ICLR main because the prediction signal does not translate into better execution than online system identification.

## Terminal Action

Keep `KILL_ARCHIVE`. Do not submit this paper to ICLR main in the current form.
