# 95 Failure-Predictive Morphology

Submission-hardening version: v4.1 rerun audit

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository is a negative evidence audit for the generated robotics idea:

> Predict which morphology-specific constraints will dominate policy failure.

The v4 rebuild tests the strongest defensible version of the idea: a morphology-conditioned predictor should identify the dominant failure family before execution and use that prediction to choose a safer controller or intervention under embodiment and environment shift.

The predictor does improve failure-family accuracy, but the closed-loop claim fails. Under combined failure stress, online system identification has better task success and lower regret:

The 2026-06-15 continuation rerun reproduced the same terminal decision: better morphology-failure prediction still does not translate into better execution than online system identification.

| Method | Task success | Failure accuracy | Dominant failure | Safety violation | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| online_system_identification | 0.618 +/- 0.008 | 0.555 | 0.191 | 0.090 | 0.193 |
| proposed_failure_predictive_morphology | 0.582 +/- 0.007 | 0.644 | 0.174 | 0.110 | 0.211 |

Paired comparison against online system identification over 175 morphology/task/seed groups:

- Task success diff: -0.03690 +/- 0.00928.
- Dominant failure-rate diff: -0.01667 +/- 0.00750.
- Safety-violation diff: +0.02030 +/- 0.00581.
- Intervention-cost diff: +0.00327 +/- 0.00059.
- Planning-regret diff: +0.01759 +/- 0.00248.
- Dominant failure-accuracy diff: +0.08839 +/- 0.01025.

The result is a useful negative: better morphology-failure labels are not enough when online system identification adapts the controller more effectively.

## Reproduce

```powershell
python src\run_experiment.py
```

The script writes:

- `results/metrics.csv`
- `results/per_morph_task_metrics.csv`
- `results/seed_morph_task_metrics.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep.csv`
- `results/pairwise_stats.csv`
- `results/failure_cases.csv`
- `figures/morphology_*.png`

## Rebuild Archive PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/95.pdf`

No PDF should be copied to the visible Desktop.
