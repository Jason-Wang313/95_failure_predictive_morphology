# Paper 95 Terminal Audit

Date: 2026-06-15

Paper: `95_failure_predictive_morphology`

Decision: `KILL_ARCHIVE`

## Reproduction

- `python -m py_compile src\run_experiment.py`: passed.
- `python src\run_experiment.py`: passed; log at `logs/95_failure_predictive_morphology_continuation_rerun_20260615.log`.
- PDF target: `C:/Users/wangz/Downloads/95.pdf`.
- Visible Desktop copy: not allowed.

## Evidence Files

- `results/metrics.csv`: 45 rows.
- `results/per_morph_task_metrics.csv`: 1,125 rows.
- `results/seed_morph_task_metrics.csv`: 7,875 rows.
- `results/pairwise_stats.csv`: 6 rows.
- `results/ablation_metrics.csv`: 7 rows.
- `results/ablation_seed_metrics.csv`: 1,225 rows.
- `results/stress_sweep.csv`: 42 rows.
- `results/stress_sweep_seed_metrics.csv`: 7,350 rows.
- `results/failure_cases.csv`: 5 rows.
- `results/combined_stress_table.tex`: regenerated.
- `results/ablation_table.tex`: regenerated.
- `results/pairwise_decision_table.tex`: regenerated.

## Key Results

Combined failure stress:

- `online_system_identification`: success `0.61845 +/- 0.00750`, accuracy `0.55548`, dominant-failure rate `0.19107`, safety violation `0.08994`, regret `0.19300`.
- `proposed_failure_predictive_morphology`: success `0.58155 +/- 0.00749`, accuracy `0.64387`, dominant-failure rate `0.17440`, safety violation `0.11024`, regret `0.21059`.
- `red_team_failure_retrieval`: success `0.57893`, accuracy `0.53929`, dominant-failure rate `0.21911`, safety violation `0.11196`, regret `0.22715`.
- Paired success difference versus `online_system_identification`: `-0.03690 +/- 0.00928`.
- Paired dominant-failure-rate difference: `-0.01667 +/- 0.00750`.
- Paired safety-violation difference: `+0.02030 +/- 0.00581`.
- Paired regret difference: `+0.01759 +/- 0.00248`.
- Paired accuracy difference: `+0.08839 +/- 0.01025`.

Ablation:

- Full proposed method: success `0.58042`, accuracy `0.64899`, dominant-failure rate `0.16940`, safety violation `0.11393`, regret `0.21114`.
- `minus_calibration`: success `0.60482`, accuracy `0.64815`, dominant-failure rate `0.16696`, regret `0.19959`.
- `minus_intervention_cost_model`: success `0.61887`, accuracy `0.64226`, dominant-failure rate `0.16542`, regret `0.18947`.

Maximum stress:

- `online_system_identification`: success `0.61112`, accuracy `0.55735`, dominant-failure rate `0.19510`, safety violation `0.09235`, regret `0.19563`.
- `proposed_failure_predictive_morphology`: success `0.57816`, accuracy `0.64735`, dominant-failure rate `0.17347`, safety violation `0.11143`, regret `0.21257`.

## Terminal Reason

The rerun verifies the v4 negative decision. The proposed method predicts failure families better and reduces dominant-failure rate, but online system identification has higher task success, lower safety violation, and lower regret. Ablations also contradict the full intervention policy. The only honest ICLR-main decision is `KILL_ARCHIVE`.

## PDF Verification

- Build command: two-pass `pdflatex -interaction=nonstopmode -halt-on-error main.tex`.
- Canonical PDF: `C:/Users/wangz/Downloads/95.pdf`.
- PDF SHA256: `9953181DCEA08C2AAC3575329F8E9982B8E99E23E30494987F11D33AB39A8585`.
- PDF size: 544,472 bytes.
- LaTeX log scan: no document warnings/errors requiring action after the second pass.
- Desktop copy: absent.
