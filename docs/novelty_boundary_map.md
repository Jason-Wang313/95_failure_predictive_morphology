# Novelty Boundary Map

## Crowded Territory

- Generic failure prediction.
- Morphology-conditioned policy selection without a new execution benefit.
- Constrained model predictive control.
- Online system identification.
- Conformal risk shielding.
- Red-team retrieval for known failure modes.
- Robust task planning and failure recovery.

## Claimed Boundary Tested

The only plausible boundary was morphology-conditioned dominant-failure prediction: identify which constraint family will dominate failure for a robot body before execution, then select an intervention that reduces closed-loop failure under embodiment and environment shift.

## Falsification Result

The boundary is falsified by the v4 benchmark. The proposed method predicts failure families better than all non-oracle baselines, but online system identification has higher success and lower regret. Constraint-aware MPC and conformal risk shielding are safer.

Decision: KILL_ARCHIVE. The novelty boundary is not defensible for ICLR main unless prediction accuracy is converted into execution improvements over adaptive-control baselines.
