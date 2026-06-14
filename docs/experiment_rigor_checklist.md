# Experiment Rigor Checklist

## Completed In v4

- [x] Concrete pre-execution rebuild plan.
- [x] Hostile prior-work pressure from the shared robotics literature pool.
- [x] Paper-specific morphology-failure benchmark.
- [x] Five morphologies: differential drive, quadruped, arm gripper, aerial manipulator, and underwater vehicle.
- [x] Five tasks: tight-turn navigation, payload transport, gap/step crossing, precision contact manipulation, and disturbance recovery.
- [x] Five splits: nominal morphology, payload shift, terrain/fluid shift, actuator degradation shift, and combined failure stress.
- [x] Seven dominant failure families.
- [x] Nine methods including per-morphology calibration, constraint-aware MPC, conformal risk shielding, domain randomization, online system identification, red-team retrieval, proposed morphology prediction, and oracle.
- [x] Seven deterministic seeds.
- [x] Per-morphology/per-task/per-seed metrics.
- [x] 95 percent confidence intervals.
- [x] Paired morphology/task/seed comparison against the strongest non-oracle baseline.
- [x] Ablations for morphology embedding, constraint-family head, calibration, intervention cost model, morphology-only, and failure-history-only.
- [x] Stress sweep across payload, terrain/fluid, actuator degradation, sensor dropout, contact tightness, and combined maximum stress.
- [x] Failure-case analysis.
- [x] Numeric hygiene audit: no NaN or Inf values in generated CSVs.
- [x] Paper-specific figures and LaTeX tables.

## Still Missing For ICLR Main

- [ ] Real robot validation.
- [ ] High-fidelity simulator benchmark.
- [ ] Trained model checkpoints.
- [ ] Integrated external baseline codebases.
- [ ] Manual full-paper related-work synthesis beyond the local hostile pool.
- [ ] Hardware videos or qualitative rollouts.

Decision: KILL_ARCHIVE. The local benchmark is rigorous enough to falsify the generated claim, not enough to revive it as an ICLR-main submission.
