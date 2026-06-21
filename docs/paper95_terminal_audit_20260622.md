# Paper 95 Terminal Audit - 2026-06-22

Terminal: KILL_ARCHIVE

ICLR-main readiness: no

## Completed

- Frozen expanded plan before execution.
- Full v5 CPU-only benchmark run completed.
- 30-page manuscript generated from CSV artifacts.
- Canonical PDF copied to `C:/Users/wangz/Downloads/95.pdf`.
- No PDF copied to the visible Desktop.
- Artifact validator passed.
- Representative PDF pages rendered and visually inspected.

## Final PDF

- Path: `C:/Users/wangz/Downloads/95.pdf`
- Pages: 30
- SHA256: `3DD7C8EE18B03A34E5DE903EB93067F7CE64396EB76E4E7D21C3E3F859B1802B`

## Gate Result

- success_gate=False
- prediction_gate=True
- safety_gate=False
- regret_gate=False
- utility_gate=False
- ablation_gate=False
- stress_gate=True
- fixed_risk_gate=True
- scope_gate=False

## Reason

The method predicts morphology-specific failure families better than strong non-v5 references, but online system identification and adaptive/control baselines remain stronger on task success, regret, and robust utility. Conformal shielding remains stronger on safety. The full mechanism also loses the ablation gate to online adaptation alone.
