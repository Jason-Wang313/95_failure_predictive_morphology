# Hostile Reviewer Response

Paper: 95 Failure-Predictive Morphology

## Strongest Technical Threats

- Model predictive tracking control based on adaptive sliding mode constraints for unmanned underwater vehicles (2026)
- MPC-MPNet: Model-Predictive Motion Planning Networks for Fast, Near-Optimal Planning Under Kinodynamic Constraints (2021)
- Stochastic Model Predictive Control for Guided Projectiles Under Impact Area Constraints (2015)
- Multi-Parameter Predictive Model of Mobile Robot's Battery Discharge for Intelligent Mission Planning in Multi-Robot Systems (2022)
- Application of a stabilizing model predictive controller to path following for a car-like agricultural robot (2024)
- Red-Teaming Vision-Language-Action Models via Quality Diversity Prompt Generation for Robust Robot Policies (2026)
- STAR: Foundation-model-driven robust task planning and failure recovery (2025)
- Failure-Aware RL for reliable offline-to-online manipulation (2026)

## Hostile ICLR-Main Response

A hostile reviewer should reject this as an ICLR-main submission. The v4 rebuild replaces the shared template experiment with a paper-specific morphology-failure benchmark, but the central claim still fails.

The proposed method predicts dominant failure families better than all non-oracle baselines, but the closed-loop result is negative:

- Task success: 0.582 +/- 0.007 vs 0.618 +/- 0.008 for online system identification.
- Safety violation: 0.110 vs 0.090.
- Planning regret: 0.211 vs 0.193.
- Dominant-failure accuracy: 0.644 vs 0.555.

This is precisely the reviewer trap: better labels are not enough if an adaptive controller uses weaker explicit prediction but produces better execution.

## Honest Action

The paper is marked `KILL_ARCHIVE`. This avoids converting a generated robotics idea into an overstated main-conference claim.

## What Would Be Needed To Revive

- Real robot or high-fidelity benchmark experiments across multiple morphologies.
- Implemented morphology predictor, online system-identification, constrained MPC, conformal shield, and red-team retrieval baselines.
- Evidence that morphology-failure prediction improves execution, not only label accuracy.
- Manual full-paper related-work audit.
- Hardware videos or qualitative rollouts.
