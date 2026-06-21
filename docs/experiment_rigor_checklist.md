# Experiment Rigor Checklist

## Completed In v5

- [x] Concrete pre-execution expanded plan.
- [x] Hostile prior-work pressure from the shared robotics literature pool.
- [x] Paper-specific morphology-failure benchmark.
- [x] Six morphologies: differential drive, quadruped, arm gripper, aerial manipulator, underwater vehicle, and soft snake robot.
- [x] Six tasks: tight-turn navigation, payload transport, gap/step crossing, precision contact manipulation, disturbance recovery, and cluttered tool use.
- [x] Eight splits: nominal morphology, payload shift, terrain/fluid shift, actuator degradation shift, sensor dropout shift, contact geometry shift, low-signal morphology stress, and combined failure stress.
- [x] Fourteen methods including constrained MPC, conformal shielding, domain randomization, online system identification, meta-adaptive MPC, transformer prior, retrieval memory, risk-aware intervention, v4, v5, and oracle.
- [x] Ten deterministic seeds.
- [x] 322,560 main rollout rows.
- [x] 115,200 ablation rollout rows.
- [x] 259,200 stress-sweep raw rows.
- [x] 138,240 fixed-risk raw rows.
- [x] Per-split, hard-aggregate, paired, ablation, stress, fixed-risk, and negative-case metrics.
- [x] 95 percent confidence intervals.
- [x] Fixed-risk budgets 0.00, 0.05, 0.10, and 0.15.
- [x] Paper-specific v5 figures.
- [x] 30-page archive manuscript with bright boxed clickable citations.
- [x] Artifact validator.

## Still Missing For ICLR Main

- [ ] Real robot validation.
- [ ] High-fidelity simulator benchmark.
- [ ] Trained model checkpoints.
- [ ] Integrated external baseline codebases.
- [ ] Independent third-party reproduction.
- [ ] Hardware videos or qualitative rollouts.

Decision: KILL_ARCHIVE after v5. The local benchmark is rigorous enough to falsify the generated claim, not enough to revive it as an ICLR-main submission.
