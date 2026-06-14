# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

## Why It Fails

The strongest defensible claim was that morphology-conditioned prediction should identify the dominant failure family early enough to improve closed-loop controller selection under embodiment shift. The benchmark does not support that claim.

The proposed method predicts failure families better than online system identification, but the stronger closed-loop baseline still wins:

- online_system_identification task success: 0.618 +/- 0.008.
- proposed_failure_predictive_morphology task success: 0.582 +/- 0.007.
- Paired proposed-minus-online-system-ID success difference: -0.03690 +/- 0.00928.
- Proposed safety violations are higher: 0.110 vs 0.090.
- Proposed planning regret is higher: 0.211 vs 0.193.
- Two ablations beat the full method on task success.

## Honest Terminal Action

Archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

## Revival Condition

The idea would need a substantially new empirical project:

- Real robot or high-fidelity simulator evidence across multiple morphologies.
- Implemented morphology-conditioned predictors and external adaptive-control baselines.
- A mechanism that turns failure-family prediction into better closed-loop success, safety, and regret than online system identification and constraint-aware MPC.
- Manual related-work synthesis and qualitative rollouts.
- A new terminal gate showing the full method beats ablations and strong baselines under maximum stress.
