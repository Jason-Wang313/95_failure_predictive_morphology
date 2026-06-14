# Child Status 95

Current stage: ICLR main gate terminal
Last update: 2026-06-14 20:19:33 +01:00
PDF: C:/Users/wangz/Downloads/95.pdf
GitHub: https://github.com/Jason-Wang313/95_failure_predictive_morphology
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Evidence digest:
- Seven seeds, five morphologies, five tasks, five splits, nine methods, ablations, stress sweep, paired confidence intervals, and failure cases.
- Strongest non-oracle combined-stress baseline: online_system_identification with task success 0.618 +/- 0.008.
- Proposed morphology predictor: task success 0.582 +/- 0.007, dominant-failure accuracy 0.644, dominant-failure rate 0.174, safety violation 0.110.
- Paired success difference vs online system identification: -0.03690 +/- 0.00928 over 175 morphology/task/seed groups.

Reason:
The proposed method predicts dominant failure families better than all non-oracle baselines, but that prediction advantage does not translate into better closed-loop execution. Online system identification has higher success and lower regret, while conformal and MPC baselines remain safer. Two ablations also beat the full method on success.
