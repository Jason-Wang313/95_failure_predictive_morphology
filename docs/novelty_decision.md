# Novelty Decision

Chosen thesis: Failure-Predictive Morphology tests whether morphology-conditioned dominant-failure prediction improves controller selection under embodiment shift.

New central mechanism tested: predict the failure family most likely to dominate for a robot body and use that prediction to choose an intervention before execution.

Decision: KILL_ARCHIVE.

Reason: the v4 benchmark shows the proposed method has the best non-oracle failure-family accuracy, but it loses closed-loop task success and regret to online system identification and is contradicted by ablations. The novelty boundary is therefore not strong enough for ICLR main.
