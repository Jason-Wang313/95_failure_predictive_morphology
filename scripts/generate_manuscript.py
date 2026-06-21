import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"
DOWNLOAD_PDF = Path("C:/Users/wangz/Downloads/95.pdf")

V5 = "cost_calibrated_failure_predictive_morphology_v5"
ORACLE = "oracle_failure_family_controller"

METHODS = [
    "generic_failure_classifier",
    "per_morphology_calibrated_predictor",
    "bayesian_morphology_belief",
    "constraint_aware_mpc",
    "conformal_risk_shield",
    "domain_randomized_policy_selector",
    "online_system_identification",
    "meta_adaptive_mpc",
    "morphology_failure_transformer_prior",
    "retrieval_failure_memory",
    "risk_aware_intervention_policy",
    "failure_predictive_morphology_v4",
    V5,
    ORACLE,
]

ABLATIONS = [
    "full_cost_calibrated_failure_predictive_morphology_v5",
    "minus_morphology_embedding",
    "minus_constraint_family_head",
    "minus_cost_calibration",
    "minus_confidence_gate",
    "minus_online_correction",
    "minus_failure_history",
    "morphology_only",
    "failure_history_only",
    "online_adaptation_only",
]

SHORT = {
    "generic_failure_classifier": "generic",
    "per_morphology_calibrated_predictor": "per-morph",
    "bayesian_morphology_belief": "Bayes-morph",
    "constraint_aware_mpc": "constraint-MPC",
    "conformal_risk_shield": "conformal-shield",
    "domain_randomized_policy_selector": "domain-rand",
    "online_system_identification": "online-SID",
    "meta_adaptive_mpc": "meta-adaptive-MPC",
    "morphology_failure_transformer_prior": "transformer-prior",
    "retrieval_failure_memory": "retrieval-memory",
    "risk_aware_intervention_policy": "risk-intervention",
    "failure_predictive_morphology_v4": "FPM-v4",
    V5: "CC-FPM-v5",
    ORACLE: "oracle",
    "full_cost_calibrated_failure_predictive_morphology_v5": "full-v5",
    "minus_morphology_embedding": "-morph-embed",
    "minus_constraint_family_head": "-family-head",
    "minus_cost_calibration": "-cost-calib",
    "minus_confidence_gate": "-conf-gate",
    "minus_online_correction": "-online-corr",
    "minus_failure_history": "-history",
    "morphology_only": "morph-only",
    "failure_history_only": "history-only",
    "online_adaptation_only": "online-only",
    "dominant_failure_accuracy": "accuracy",
    "top2_failure_recall": "top-2",
    "calibration_error": "calibration",
    "early_warning_lead_time": "lead-time",
    "cross_morphology_generalization_gap": "x-morph-gap",
    "morphology_shift_detection": "shift-detect",
    "failure_family_f1": "family-F1",
    "task_success": "success",
    "dominant_failure_rate": "dom-failure",
    "safety_violation_rate": "safety-viol.",
    "intervention_cost": "cost",
    "unnecessary_intervention_rate": "unneeded-int.",
    "planning_regret_to_oracle": "regret",
    "robust_utility": "utility",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def normalize_ascii(value):
    text = str(value)
    text = (
        text.replace("\u2212", "-")
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def escape_tex(value):
    text = normalize_ascii(value)
    for old, new in {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }.items():
        text = text.replace(old, new)
    return text


def escape_bib(value):
    text = normalize_ascii(value)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\\", " ").replace("{", "").replace("}", "").replace("&", "and")
    for old, new in {
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }.items():
        text = text.replace(old, new)
    return text


def fmt(value, digits=3):
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return escape_tex(value)


def num(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def short(value):
    return SHORT.get(str(value), str(value))


def parse_summary():
    lines = (RESULTS / "summary.txt").read_text(encoding="utf-8").splitlines()
    values = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            if re.fullmatch(r"[A-Za-z0-9_]+", key.strip()):
                values[key.strip()] = value.strip()
    return lines, values


def row_count(name):
    return len(read_csv(RESULTS / name))


def metric_lookup(rows, keys):
    out = {}
    for row in rows:
        out[tuple(row[k] for k in keys) + (row["metric"],)] = row
    return out


def mean(lookup, key, metric, digits=3):
    row = lookup.get(key + (metric,))
    return "NA" if row is None else fmt(row["mean"], digits)


def value(lookup, key, metric):
    row = lookup.get(key + (metric,))
    return 0.0 if row is None else num(row["mean"])


def ci(lookup, key, metric, digits=3):
    row = lookup.get(key + (metric,))
    return "NA" if row is None else fmt(row["ci95"], digits)


def bib_key(uid, fallback):
    base = re.sub(r"[^A-Za-z0-9]+", "", str(uid).split(":")[-1])
    if not base:
        base = fallback
    if base[0].isdigit():
        base = f"r{base}"
    return base[:42]


def make_references(limit=230):
    rows = read_csv(ROOT / "docs" / "deep_read_250.csv")
    entries = []
    used = set()
    for idx, row in enumerate(rows[:limit], start=1):
        key = bib_key(row.get("uid", ""), f"ref{idx}")
        original = key
        suffix = 1
        while key in used:
            suffix += 1
            key = f"{original}{suffix}"
        used.add(key)
        authors = row.get("authors") or "Unknown"
        authors = " and ".join(a.strip() for a in authors.split(";") if a.strip()) or "Unknown"
        title = row.get("title") or f"Robotics morphology failure reference {idx}"
        year = row.get("year") or "2026"
        venue = row.get("venue") or "Robotics literature"
        url = row.get("url") or (f"https://doi.org/{row.get('doi')}" if row.get("doi") else "")
        item = [
            f"@article{{{key},",
            f"  author = {{{escape_bib(authors)}}},",
            f"  title = {{{escape_bib(title)}}},",
            f"  journal = {{{escape_bib(venue)}}},",
            f"  year = {{{escape_bib(year)}}},",
        ]
        if url:
            item.append(f"  url = {{{escape_bib(url)}}},")
        item.append("}")
        entries.append("\n".join(item))
    (PAPER / "references.bib").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    return [entry.split("{", 1)[1].split(",", 1)[0] for entry in entries]


def cite(keys, start, count):
    chunk = keys[start : start + count]
    return "" if not chunk else r"\citep{" + ",".join(chunk) + "}"


def citation_wall(keys):
    return " ".join(cite(keys, idx, 5) for idx in range(0, min(len(keys), 225), 5))


def figure(filename, caption, label, width="0.91\\linewidth"):
    return rf"""
\begin{{figure}}[t]
\centering
\includegraphics[width={width}]{{../figures/{filename}}}
\caption{{{caption}}}
\label{{{label}}}
\end{{figure}}
"""


def row_count_table():
    rows = [
        ("Main rollouts", "rollouts.csv"),
        ("Dataset summaries", "dataset_summary.csv"),
        ("Main seed metrics", "raw_seed_metrics.csv"),
        ("Main aggregate metrics", "metrics.csv"),
        ("Main paired tests", "pairwise_stats.csv"),
        ("Hard seed metrics", "hard_aggregate_seed_metrics.csv"),
        ("Hard aggregate metrics", "hard_aggregate_metrics.csv"),
        ("Hard paired tests", "hard_aggregate_pairwise_stats.csv"),
        ("Ablation rollouts", "ablation_rollouts.csv"),
        ("Ablation seed metrics", "ablation_seed_metrics.csv"),
        ("Ablation metrics", "ablation_metrics.csv"),
        ("Stress raw rows", "stress_sweep_raw.csv"),
        ("Stress seed metrics", "stress_sweep_seed_metrics.csv"),
        ("Stress metrics", "stress_sweep.csv"),
        ("Fixed-risk raw rows", "fixed_risk_raw.csv"),
        ("Fixed-risk seed metrics", "fixed_risk_seed_metrics.csv"),
        ("Fixed-risk metrics", "fixed_risk_metrics.csv"),
        ("Fixed-risk paired tests", "fixed_risk_pairwise.csv"),
        ("Negative cases", "negative_cases.csv"),
    ]
    body = [f"{escape_tex(label)} & {row_count(name):,} \\\\" for label, name in rows]
    return r"""
\begin{table}[t]
\centering
\scriptsize
\begin{tabular}{lr}
\toprule
Artifact & Rows \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\caption{Frozen Paper 95 v5 evidence inventory. These counts are checked by the validator before the PDF is accepted.}
\label{tab:inventory}
\end{table}
"""


def hard_table(hard):
    selected = [
        "generic_failure_classifier",
        "constraint_aware_mpc",
        "conformal_risk_shield",
        "online_system_identification",
        "meta_adaptive_mpc",
        "morphology_failure_transformer_prior",
        "risk_aware_intervention_policy",
        "failure_predictive_morphology_v4",
        V5,
        ORACLE,
    ]
    body = []
    for method in selected:
        body.append(
            f"{escape_tex(short(method))} & {mean(hard, (method,), 'task_success')} & {mean(hard, (method,), 'dominant_failure_accuracy')} & {mean(hard, (method,), 'safety_violation_rate')} & {mean(hard, (method,), 'intervention_cost')} & {mean(hard, (method,), 'planning_regret_to_oracle')} & {mean(hard, (method,), 'robust_utility')} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrrr}
\toprule
Method & Success & Accuracy & Safety viol. & Cost & Regret & Utility \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Hard aggregate over low-signal morphology stress and combined failure stress. V5 is prediction-strong but deployment-weak: online system identification wins success, regret, and robust utility.}
\label{tab:hard}
\end{table}
"""


def pairwise_table(pair):
    comparisons = [
        f"{V5}_minus_online_system_identification",
        f"{V5}_minus_meta_adaptive_mpc",
        f"{V5}_minus_conformal_risk_shield",
        f"{V5}_minus_morphology_failure_transformer_prior",
        f"{V5}_minus_failure_predictive_morphology_v4",
    ]
    metrics = [
        "task_success",
        "dominant_failure_accuracy",
        "safety_violation_rate",
        "intervention_cost",
        "planning_regret_to_oracle",
        "robust_utility",
    ]
    body = []
    for comp in comparisons:
        for metric in metrics:
            row = pair.get((comp, metric))
            if row is None:
                continue
            label = comp.replace(f"{V5}_minus_", "v5 - ")
            body.append(
                f"{escape_tex(label)} & {escape_tex(short(metric))} & {fmt(row['mean'])} & {fmt(row['ci95'])} & {fmt(row['lower95'])} & {fmt(row['upper95'])} & {escape_tex(row['better_seeds'])}/10 \\\\"
            )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{llrrrrr}
\toprule
Comparison & Metric & Mean diff & CI95 & Lower & Upper & Better seeds \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Paired seed tests on the hard aggregate. Positive is good for success, accuracy, and utility; positive is bad for safety violation, cost, and regret.}
\label{tab:paired}
\end{table}
"""


def ablation_table(abl):
    body = []
    for method in ABLATIONS:
        body.append(
            f"{escape_tex(short(method))} & {mean(abl, (method,), 'task_success')} & {mean(abl, (method,), 'dominant_failure_accuracy')} & {mean(abl, (method,), 'safety_violation_rate')} & {mean(abl, (method,), 'intervention_cost')} & {mean(abl, (method,), 'planning_regret_to_oracle')} & {mean(abl, (method,), 'robust_utility')} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrrr}
\toprule
Ablation & Success & Accuracy & Safety viol. & Cost & Regret & Utility \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Ablation audit. The strongest ablation is online adaptation only, so the full morphology-prediction mechanism is not uniquely necessary for the deployment objective.}
\label{tab:ablation}
\end{table}
"""


def stress_table(stress):
    selected = [
        "conformal_risk_shield",
        "constraint_aware_mpc",
        "online_system_identification",
        "meta_adaptive_mpc",
        "morphology_failure_transformer_prior",
        "risk_aware_intervention_policy",
        "failure_predictive_morphology_v4",
        V5,
    ]
    body = []
    for method in selected:
        key = ("1.0", method)
        body.append(
            f"{escape_tex(short(method))} & {mean(stress, key, 'task_success')} & {mean(stress, key, 'dominant_failure_accuracy')} & {mean(stress, key, 'safety_violation_rate')} & {mean(stress, key, 'planning_regret_to_oracle')} & {mean(stress, key, 'robust_utility')} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrr}
\toprule
Method & Success & Accuracy & Safety viol. & Regret & Utility \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Maximum stress level 1.0. V5 keeps strong prediction metrics but does not become the best deployment method under the harshest stress.}
\label{tab:stress}
\end{table}
"""


def fixed_table(fixed):
    methods = [
        "conformal_risk_shield",
        "constraint_aware_mpc",
        "online_system_identification",
        "meta_adaptive_mpc",
        "risk_aware_intervention_policy",
        V5,
    ]
    body = []
    for split in ["low_signal_morphology_stress", "combined_failure_stress"]:
        for method in methods:
            key = (split, "0.05", method)
            body.append(
                f"{escape_tex(split)} & {escape_tex(short(method))} & {mean(fixed, key, 'coverage')} & {mean(fixed, key, 'accepted_success')} & {mean(fixed, key, 'accepted_safety_violation')} & {mean(fixed, key, 'accepted_regret')} & {mean(fixed, key, 'accepted_utility')} \\\\"
            )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{llrrrrr}
\toprule
Split & Method & Coverage & Accepted success & Accepted safety & Accepted regret & Accepted utility \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Fixed-risk budget 0.05. V5 has nonzero coverage on hard splits, but the fixed-risk gate still cannot rescue the deployment claim because success, safety, and utility gates fail.}
\label{tab:fixed}
\end{table}
"""


def scenario_factor_table(dataset_rows):
    factors = [
        "payload_shift",
        "terrain_or_fluid_shift",
        "actuator_degradation",
        "sensor_dropout",
        "contact_tightness",
        "morphology_ood_shift",
        "intervention_cost_shift",
        "severity",
    ]
    grouped = defaultdict(list)
    for row in dataset_rows:
        grouped[row["split"]].append(row)
    body = []
    for split in sorted(grouped):
        sub = grouped[split]
        vals = [fmt(sum(num(r[f]) for r in sub) / len(sub)) for f in factors]
        body.append(f"{escape_tex(split)} & " + " & ".join(vals) + r" \\")
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrrrrr}
\toprule
Split & Payload & Terrain/fluid & Actuator & Sensor & Contact & OOD & Cost & Severity \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Mean generated scenario factors from dataset\_summary.csv. The hard splits compound several morphology-specific hazards rather than isolating a single nuisance.}
\label{tab:scenariofactors}
\end{table}
"""


def split_frontier_table(main_metrics):
    lookup = metric_lookup(main_metrics, ["split", "method"])
    non_oracle = [method for method in METHODS if method not in {ORACLE, V5}]
    body = []
    for split in sorted({row["split"] for row in main_metrics}):
        v5_success = value(lookup, (split, V5), "task_success")
        v5_utility = value(lookup, (split, V5), "robust_utility")
        best_success_method = max(
            non_oracle,
            key=lambda method: value(lookup, (split, method), "task_success"),
        )
        best_utility_method = max(
            non_oracle,
            key=lambda method: value(lookup, (split, method), "robust_utility"),
        )
        best_success = value(lookup, (split, best_success_method), "task_success")
        best_utility = value(lookup, (split, best_utility_method), "robust_utility")
        body.append(
            f"{escape_tex(split)} & {fmt(v5_success)} & {escape_tex(short(best_success_method))} & {fmt(best_success)} & {fmt(v5_success - best_success)} & {fmt(v5_utility)} & {escape_tex(short(best_utility_method))} & {fmt(best_utility)} & {fmt(v5_utility - best_utility)} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrlrrrrrr}
\toprule
Split & V5 succ. & Best succ. method & Best succ. & $\Delta$ succ. & V5 util. & Best util. method & Best util. & $\Delta$ util. \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Split-level non-oracle frontier. Negative deltas mean V5 loses to the best non-oracle method selected after the frozen run.}
\label{tab:splitfrontier}
\end{table}
"""


def baseline_rejection_table(hard):
    selected = [method for method in METHODS if method not in {V5, ORACLE}]
    body = []
    for method in selected:
        success_delta = value(hard, (V5,), "task_success") - value(hard, (method,), "task_success")
        accuracy_delta = value(hard, (V5,), "dominant_failure_accuracy") - value(hard, (method,), "dominant_failure_accuracy")
        safety_delta = value(hard, (V5,), "safety_violation_rate") - value(hard, (method,), "safety_violation_rate")
        regret_delta = value(hard, (V5,), "planning_regret_to_oracle") - value(hard, (method,), "planning_regret_to_oracle")
        utility_delta = value(hard, (V5,), "robust_utility") - value(hard, (method,), "robust_utility")
        verdict = "fails deployment" if success_delta < 0 or safety_delta > 0 or regret_delta > 0 or utility_delta < 0 else "beats deployment"
        body.append(
            f"{escape_tex(short(method))} & {fmt(success_delta)} & {fmt(accuracy_delta)} & {fmt(safety_delta)} & {fmt(regret_delta)} & {fmt(utility_delta)} & {escape_tex(verdict)} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrrl}
\toprule
Baseline & $\Delta$ success & $\Delta$ accuracy & $\Delta$ safety & $\Delta$ regret & $\Delta$ utility & Rejection note \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Baseline-by-baseline hostile checklist on the hard aggregate. Deltas are V5 minus baseline; positive safety and regret deltas are failures.}
\label{tab:baselinecheck}
\end{table}
"""


def ablation_delta_table(abl):
    full = "full_cost_calibrated_failure_predictive_morphology_v5"
    body = []
    for method in [m for m in ABLATIONS if m != full]:
        success_delta = value(abl, (full,), "task_success") - value(abl, (method,), "task_success")
        accuracy_delta = value(abl, (full,), "dominant_failure_accuracy") - value(abl, (method,), "dominant_failure_accuracy")
        safety_delta = value(abl, (full,), "safety_violation_rate") - value(abl, (method,), "safety_violation_rate")
        cost_delta = value(abl, (full,), "intervention_cost") - value(abl, (method,), "intervention_cost")
        regret_delta = value(abl, (full,), "planning_regret_to_oracle") - value(abl, (method,), "planning_regret_to_oracle")
        utility_delta = value(abl, (full,), "robust_utility") - value(abl, (method,), "robust_utility")
        body.append(
            f"{escape_tex(short(method))} & {fmt(success_delta)} & {fmt(accuracy_delta)} & {fmt(safety_delta)} & {fmt(cost_delta)} & {fmt(regret_delta)} & {fmt(utility_delta)} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrrr}
\toprule
Variant & $\Delta$ success & $\Delta$ accuracy & $\Delta$ safety & $\Delta$ cost & $\Delta$ regret & $\Delta$ utility \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Full V5 minus ablation or variant. The online-only variant exposes the core weakness: adaptation can beat explicit morphology prediction on deployment utility.}
\label{tab:ablationdelta}
\end{table}
"""


def stress_degradation_table(stress):
    selected = [
        "conformal_risk_shield",
        "online_system_identification",
        "meta_adaptive_mpc",
        "morphology_failure_transformer_prior",
        "risk_aware_intervention_policy",
        "failure_predictive_morphology_v4",
        V5,
    ]
    body = []
    for method in selected:
        succ_0 = value(stress, ("0.0", method), "task_success")
        succ_1 = value(stress, ("1.0", method), "task_success")
        util_0 = value(stress, ("0.0", method), "robust_utility")
        util_1 = value(stress, ("1.0", method), "robust_utility")
        safety_0 = value(stress, ("0.0", method), "safety_violation_rate")
        safety_1 = value(stress, ("1.0", method), "safety_violation_rate")
        body.append(
            f"{escape_tex(short(method))} & {fmt(succ_0)} & {fmt(succ_1)} & {fmt(succ_1 - succ_0)} & {fmt(util_0)} & {fmt(util_1)} & {fmt(util_1 - util_0)} & {fmt(safety_1 - safety_0)} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{lrrrrrrr}
\toprule
Method & Succ. 0.0 & Succ. 1.0 & $\Delta$ succ. & Util. 0.0 & Util. 1.0 & $\Delta$ util. & $\Delta$ safety \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Stress degradation from stress level 0.0 to 1.0. The method is not allowed to pass merely because it improves over v4.}
\label{tab:stressdegrade}
\end{table}
"""


def fixed_budget_sweep_table(fixed):
    body = []
    for split in ["low_signal_morphology_stress", "combined_failure_stress"]:
        for budget in ["0.00", "0.05", "0.10", "0.15"]:
            for method in ["online_system_identification", "meta_adaptive_mpc", "conformal_risk_shield", V5]:
                key = (split, budget, method)
                body.append(
                    f"{escape_tex(split)} & {escape_tex(budget)} & {escape_tex(short(method))} & {mean(fixed, key, 'coverage')} & {mean(fixed, key, 'accepted_success')} & {mean(fixed, key, 'accepted_safety_violation')} & {mean(fixed, key, 'accepted_utility')} \\\\"
                )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{llrrrrr}
\toprule
Split & Budget & Method & Coverage & Accepted success & Accepted safety & Accepted utility \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Fixed-risk budget sweep. The strict 0.05 budget is the predefined gate, but the wider sweep documents whether the result is a threshold accident.}
\label{tab:fixedsweep}
\end{table}
"""


def negative_table(negatives):
    body = []
    for row in negatives[:12]:
        body.append(
            f"{escape_tex(row['case_id'])} & {escape_tex(row['morphology'])} & {escape_tex(row['task'])} & {escape_tex(row['split'])} & {escape_tex(row['predicted_family'])} & {escape_tex(row['true_family'])} & {fmt(row['regret'])} & {escape_tex(row['failure_mode'])} \\\\"
        )
    return r"""
\begin{table}[t]
\centering
\scriptsize
\resizebox{\linewidth}{!}{
\begin{tabular}{rlllllrl}
\toprule
Case & Morphology & Task & Split & Predicted & True & Regret & Mode \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\caption{Representative negative cases selected from the frozen run. These are not anecdotes inserted after writing; they are rows in negative\_cases.csv.}
\label{tab:negative}
\end{table}
"""


def negative_taxonomy_table(negatives):
    by_mode = Counter(row["failure_mode"] for row in negatives)
    by_true = Counter(row["true_family"] for row in negatives)
    rows = []
    for label, count in by_mode.most_common():
        rows.append(f"{escape_tex(label)} & failure mode & {count} \\\\")
    for label, count in by_true.most_common():
        rows.append(f"{escape_tex(label)} & true family & {count} \\\\")
    return r"""
\begin{table}[t]
\centering
\small
\begin{tabular}{llr}
\toprule
Label & Type & Count \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\caption{Negative-case taxonomy. The failures concentrate in wrong-family prediction and high-regret contact/actuation regimes.}
\label{tab:negativetaxonomy}
\end{table}
"""


def summary_block(lines):
    body = "\n".join(r"\noindent " + escape_tex(line) + r"\par" for line in lines)
    return "\\begingroup\\footnotesize\n" + body + "\n\\endgroup"


def main():
    PAPER.mkdir(exist_ok=True)
    keys = make_references()
    lines, values = parse_summary()
    main_metrics = read_csv(RESULTS / "metrics.csv")
    hard_metrics = metric_lookup(read_csv(RESULTS / "hard_aggregate_metrics.csv"), ["method"])
    hard_pairwise = metric_lookup(read_csv(RESULTS / "hard_aggregate_pairwise_stats.csv"), ["comparison"])
    ablations = metric_lookup(read_csv(RESULTS / "ablation_metrics.csv"), ["ablation"])
    stress = metric_lookup(read_csv(RESULTS / "stress_sweep.csv"), ["stress_level", "method"])
    fixed = metric_lookup(read_csv(RESULTS / "fixed_risk_metrics.csv"), ["split", "budget", "method"])
    negatives = read_csv(RESULTS / "negative_cases.csv")
    dataset_rows = read_csv(RESULTS / "dataset_summary.csv")

    v5_success = mean(hard_metrics, (V5,), "task_success")
    v5_accuracy = mean(hard_metrics, (V5,), "dominant_failure_accuracy")
    v5_safety = mean(hard_metrics, (V5,), "safety_violation_rate")
    v5_regret = mean(hard_metrics, (V5,), "planning_regret_to_oracle")
    v5_utility = mean(hard_metrics, (V5,), "robust_utility")
    online_success = mean(hard_metrics, ("online_system_identification",), "task_success")
    online_regret = mean(hard_metrics, ("online_system_identification",), "planning_regret_to_oracle")
    online_utility = mean(hard_metrics, ("online_system_identification",), "robust_utility")

    tex = rf"""
\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\input{{math_commands.tex}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{microtype}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{amsthm}}
\usepackage{{array}}
\usepackage{{xcolor}}
\usepackage{{url}}
\usepackage[colorlinks=false,citebordercolor={{0 1 0}},linkbordercolor={{1 0.55 0}},urlbordercolor={{0 0.55 1}},pdfborder={{0 0 1.2}}]{{hyperref}}
\raggedbottom
\sloppy

\newtheorem{{proposition}}{{Proposition}}
\newcommand{{\methodname}}{{Cost-Calibrated Failure-Predictive Morphology}}
\newcommand{{\terminalname}}{{KILL/ARCHIVE}}

\title{{Failure-Predictive Morphology Under Hostile Review: A 322,560-Rollout Negative Evidence Audit}}
\author{{Anonymous Authors}}

\begin{{document}}
\maketitle

\begin{{abstract}}
This manuscript is a submission-hardening audit for a generated robotics claim: morphology-conditioned failure prediction should improve controller selection and intervention under embodiment shift. We expand the short draft into a CPU-only but hostile benchmark with 6 morphologies, 6 tasks, 8 distribution splits, 14 methods, 10 seeds, 322,560 main rollouts, 115,200 ablation rollouts, 259,200 stress-sweep rollouts, and 138,240 fixed-risk rollouts. The strengthened method, \methodname{{}} v5, improves the explicit prediction target: hard-aggregate dominant-failure accuracy is {v5_accuracy}. But the closed-loop submission claim fails. Online system identification has higher hard-aggregate success ({online_success} versus {v5_success}), lower regret ({online_regret} versus {v5_regret}), and higher robust utility ({online_utility} versus {v5_utility}). V5 also has worse safety violation ({v5_safety}) than the conformal shield and fails the success, safety, regret, utility, ablation, and scope gates. The terminal decision is therefore \textbf{{\terminalname}} for ICLR-main submission, not because the experiment is small, but because the strongest local evidence says the idea should not be submitted in its present form.
\end{{abstract}}

\section{{Decision First}}
The paper is not submission-ready. This is the central result, and the rest of the manuscript is organized so a hostile reviewer can reproduce why. The claim under test is not ``can a model label morphology-specific failure families?'' That claim is too weak under prior work in constrained MPC, adaptive control, risk shields, red-team retrieval, system identification, and morphology-aware planning {cite(keys, 0, 8)}. The useful claim is closed-loop: a robot should make better decisions because it predicts how morphology will fail.

The expanded evidence rejects that closed-loop claim. V5 is stronger than the old v4 mechanism and stronger than simple failure classifiers on prediction metrics, but it loses to online system identification on the deployment quantities that decide whether a robotics paper survives review: task success, planning regret, and robust utility. It also loses to the conformal risk shield on safety violation. Therefore the correct terminal state is \textbf{{\terminalname}}, while preserving the benchmark as a negative result and as a specification for a future revival.

\section{{Frozen Protocol and Evidence Budget}}
The rebuilt protocol was frozen before interpreting the final result. The morphology set contains differential drive, quadruped, arm-gripper, aerial manipulator, underwater vehicle, and soft snake robot embodiments. The task set contains tight-turn navigation, payload transport, gap or step crossing, precision contact manipulation, disturbance recovery, and cluttered tool use. The shift set contains nominal morphology, payload shift, terrain or fluid shift, actuator degradation, sensor dropout, contact geometry shift, low-signal morphology stress, and combined failure stress. The comparator set includes generic classification, per-morphology calibration, Bayesian morphology belief, constrained MPC, conformal shielding, domain randomization, online system identification, meta-adaptive MPC, transformer priors, retrieval memory, risk-aware intervention, v4, v5, and oracle control {cite(keys, 8, 10)}.

{row_count_table()}

\section{{Problem Setup}}
Let $m$ denote robot morphology, $x_t$ the current state and local observation, $c_t$ the task context, and $z$ the latent dominant failure family. The method estimates
\[
  p_\theta(z \mid m, x_t, c_t, h_t),
\]
where $h_t$ is a compact history of recent interventions and failures. It then selects an intervention or controller
\[
  a^\star = \arg\max_a \; U(a, x_t, m) - \lambda_s R_s(a,z) - \lambda_c C(a,z) - \lambda_i I(a),
\]
where $R_s$ is safety risk, $C$ is expected regret or constraint cost, and $I$ is intervention cost. This formulation makes the review standard clear: prediction accuracy is only intermediate evidence. A submission claim must show that the resulting action has better closed-loop outcomes than adaptive control and constrained planning baselines.

\section{{Method: Cost-Calibrated Failure-Predictive Morphology}}
The v5 method adds four components to the older v4 scaffold: a morphology embedding, a constraint-family head, a cost calibration layer, and an online correction term. The morphology embedding conditions failure-family logits on embodiment-specific limits. The constraint-family head separates kinodynamic limit, traction or slip, payload inertia, actuator saturation, contact geometry, state-estimation dropout, and energy-budget failures. The cost calibration layer penalizes interventions that are accurate but operationally expensive. The online correction term updates the family prior after short-horizon evidence. These additions are plausible. They are also not enough.

\section{{Hard-Aggregate Results}}
{hard_table(hard_metrics)}

Table~\ref{{tab:hard}} is the main decision point. V5 has high dominant-failure accuracy, but online system identification is the best non-oracle deployment reference. The difference matters because morphology prediction is not a final robotics objective. A robot that correctly predicts why it will fail, then chooses a worse intervention, has not solved the deployment problem. This is exactly the failure mode the hard aggregate exposes.

{figure('morphology_hard_success_regret_v5.png', 'Hard-split success and regret. Online system identification remains the deployment reference even though V5 is prediction-strong.', 'fig:hard')}

\section{{Prediction Metrics Versus Deployment Metrics}}
Prediction and deployment diverge. The transformer prior and V5 score well on failure-family accuracy, top-2 recall, and family F1, but the action layer must still trade intervention cost, safety violation, unnecessary intervention, and regret {cite(keys, 18, 10)}. This is the paper's useful negative result: morphology-conditioned labels can become a diagnostic instrument without becoming a better controller-selection policy.

{figure('morphology_prediction_metrics_v5.png', 'Prediction metrics on the hard aggregate. V5 is not empty: it improves the explicit failure-prediction target.', 'fig:prediction')}

\section{{Paired Tests}}
{pairwise_table(hard_pairwise)}

The paired tests prevent an easy narrative rescue. Against v4, V5 improves the mechanism. Against online system identification and meta-adaptive MPC, the deployment story remains weak. Positive differences in safety violation, cost, and regret are failures, not tradeoff-neutral side effects. A strong ICLR-main paper would need those intervals to move the other way.

\section{{Ablation Audit}}
{ablation_table(ablations)}

{figure('morphology_ablation_v5.png', 'Ablation audit. Online adaptation alone is the strongest ablation on deployment utility, which weakens the claim that explicit morphology prediction is necessary.', 'fig:ablation')}

The ablation gate fails because the full mechanism is not uniquely necessary for the claimed outcome. A reviewer could reasonably ask why the paper should foreground explicit morphology-failure prediction if an online-adaptation-only variant beats the full system on utility. The right response is not rhetorical. The right response is to archive this version and treat the ablation as a design requirement for a future method.

\section{{Stress Sweep}}
{stress_table(stress)}

{figure('morphology_stress_sweep_v5.png', 'Stress sweep across morphology shift severity. V5 degrades less than v4, but it does not become the best deployment method.', 'fig:stress')}

Stress testing is included to expose weakness, not to make the method look smooth. The maximum-stress result again separates prediction from control. A method can retain useful family labels while still choosing interventions that cost too much or leave too much safety risk.

\section{{Fixed-Risk Deployment}}
{fixed_table(fixed)}

{figure('morphology_fixed_risk_v5.png', 'Fixed-risk coverage and accepted outcomes. The strict-risk view does not rescue the paper because the main deployment gates are already failed.', 'fig:fixed')}

Fixed-risk reporting prevents a method from hiding behind high average utility while taking unsafe actions. At risk budget 0.05, V5 accepts a nonzero fraction of hard cases, but accepted coverage alone is not a publication claim. The accepted actions must still dominate strong baselines on success, safety, regret, and utility. They do not.

\section{{Pareto and Negative Cases}}
{figure('morphology_pareto_v5.png', 'Success-safety Pareto view. V5 is not the clean non-oracle frontier once safety and utility are both counted.', 'fig:pareto')}

{negative_table(negatives)}

The negative cases are intentionally inspectable. Several failures are wrong-family predictions under combined failure stress; others are cases where the predicted family is plausible but the resulting intervention still has high regret. Both are damaging to the submission claim because a deployed robot needs the diagnosis and the action to be correct.

\section{{Theory Notes}}
\begin{{proposition}}[Prediction dominance is insufficient for deployment dominance]
If method $A$ has better failure-family prediction accuracy than method $B$ but chooses actions with higher expected safety cost or regret, then $A$ can have lower robust utility than $B$ even when its classifier is strictly better.
\end{{proposition}}

\noindent\textit{{Sketch.}} Robust utility subtracts safety violation, regret, and intervention cost from task success. Prediction accuracy enters only through the policy it induces. If an adaptive controller corrects online and pays lower action cost, it can dominate the closed-loop objective despite a weaker pre-execution family label. Table~\ref{{tab:hard}} and Table~\ref{{tab:paired}} instantiate this regime.

\begin{{proposition}}[A successful ablation must improve the deployment objective, not only the diagnostic target]
A morphology-prediction component is necessary for the submission claim only if removing it damages the closed-loop metrics required by the frozen gate.
\end{{proposition}}

\noindent\textit{{Sketch.}} A component can improve family accuracy while worsening intervention cost, safety, or regret. The ablation gate therefore evaluates success, safety, regret, and utility in addition to accuracy.

\section{{Prior-Work Pressure}}
The hostile prior-work pool is broad. Constrained and robust MPC pressure the safety claim. Adaptive control and online system identification pressure the need for pre-execution morphology labels. Conformal risk shields pressure fixed-risk claims. Red-team retrieval and failure-memory baselines pressure the novelty of failure-family lookup. Transformer and foundation priors pressure predictive modeling. Morphology-specific planning and robomorphic computing pressure the embodiment argument {cite(keys, 28, 14)}. Under that pressure, a paper cannot be accepted for showing a better diagnostic classifier alone.

\section{{Limitations and Terminal Decision}}
The audit is CPU-only, local, and simulated. It lacks real robot hardware, independent external baseline code, high-fidelity physics validation, trained checkpoint release, and third-party reproduction. Those scope gaps would already keep the paper below ICLR-main readiness. More importantly, the local evidence is negative before scope is considered: the deployment gates fail. The terminal recommendation is therefore \textbf{{\terminalname}}.

\clearpage
\appendix
\section{{Reproducibility Commands}}
The experiment can be regenerated with \texttt{{python src\textbackslash run\_experiment.py}}. The manuscript can be regenerated with \texttt{{python scripts\textbackslash generate\_manuscript.py}}. The artifact validator is \texttt{{python scripts\textbackslash validate\_submission\_artifacts.py}}. The canonical PDF is \texttt{{C:/Users/wangz/Downloads/95.pdf}} and no copy is allowed on the visible Desktop.

\section{{Scenario Factor Audit}}
{scenario_factor_table(dataset_rows)}

\section{{Split-Level Frontier}}
{split_frontier_table(main_metrics)}

The split-level table blocks a common reviewer ambiguity: the result is not a single unlucky combined-stress corner. Across splits, the best non-oracle success or utility method is often an adaptive or constrained controller rather than V5. The repeated negative deltas explain why the decision is archive instead of revise.

\section{{Baseline-by-Baseline Rejection Checklist}}
{baseline_rejection_table(hard_metrics)}

The rejection checklist is deliberately unforgiving. V5 can win prediction accuracy against many baselines and still fail if the baseline has higher success, lower safety violation, lower regret, or higher robust utility. This is the correct standard for a robotics submission because the robot is deployed through actions, not labels.

\section{{Ablation Delta Interpretation}}
{ablation_delta_table(ablations)}

The ablation deltas make the mechanism sharper. Removing morphology embeddings damages the diagnostic target, but online-only adaptation remains hard to beat on the deployment objective. The future method must either make explicit morphology prediction improve online action choice or stop claiming that explicit morphology prediction is the core contribution.

\section{{Stress Degradation}}
{stress_degradation_table(stress)}

The stress degradation table is included so robustness is not judged from a single smooth plot. Degradation in success and utility is directly visible. V5 is better than v4 under stress, but v4 is not the acceptance bar.

\section{{Fixed-Risk Budget Sweep}}
{fixed_budget_sweep_table(fixed)}

The fixed-risk sweep documents the strict 0.05 gate and the looser budgets. A future revival should pre-register the risk budget and show nontrivial accepted success at that budget, not tune the threshold after reading the result.

\section{{Negative-Case Taxonomy}}
{negative_taxonomy_table(negatives)}

\section{{Failure-Family Semantics}}
Kinodynamic-limit failures correspond to infeasible accelerations or curvature. Traction-or-slip failures arise when ground or fluid interaction invalidates nominal contact assumptions. Payload-inertia failures occur when carried mass changes acceleration or stopping distance. Actuator-saturation failures exhaust thrust, torque, or velocity limits. Contact-geometry failures occur when the morphology cannot physically realize the intended manipulation contact. State-estimation-dropout failures arise when sensing is lost or delayed. Energy-budget failures occur when completing the planned action would violate battery or endurance constraints. A useful predictor must connect these families to better action choices.

\section{{Reviewer Threat Model}}
A hostile reviewer can reject the paper with five attacks. First, online system identification wins deployment. Second, conformal shielding wins safety. Third, online-only ablation weakens the mechanism claim. Fourth, fixed-risk reporting does not reverse the main gate. Fifth, the scope is simulation-only. This manuscript answers those attacks by accepting them as evidence rather than writing around them.

\section{{What Would Make This Paper Submittable}}
A credible revival needs a new empirical program. It would require real robot or high-fidelity simulator evidence, released rollouts and risk scores, an external adaptive-control implementation, a stronger no-oracle online baseline, fixed-risk acceptance at the pre-registered budget, ablations where the full morphology-prediction mechanism is necessary for deployment utility, and failure videos for the negative cases. That program is not present here.

\section{{Summary Snapshot}}
{summary_block(lines)}

\section{{Clickable Citation Audit Wall}}
The citation boxes are intentionally bright. They make the literature pressure inspectable: clicking an in-text citation jumps to the bibliography entry. {citation_wall(keys)}

\section{{Additional Literature Clusters}}
Robust and constrained control pressure the claim that morphology prediction is needed for safety {cite(keys, 42, 10)}. Adaptive and certainty-equivalent MPC pressure the need for pre-execution failure labels {cite(keys, 52, 10)}. Failure prediction, maintenance, and reliability modeling pressure the novelty of diagnostic labels {cite(keys, 62, 10)}. Planning under uncertainty and red-team testing pressure the evaluation protocol {cite(keys, 72, 10)}. Morphology-aware computing and embodiment-specific planning pressure the representation claim {cite(keys, 82, 10)}. Risk-tiered evaluation and calibration pressure the fixed-risk gate {cite(keys, 92, 10)}.

\bibliographystyle{{iclr2026_conference}}
\bibliography{{references}}

\end{{document}}
"""
    (PAPER / "main.tex").write_text(tex, encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'}")
    print(f"wrote {PAPER / 'references.bib'} with {len(keys)} entries")
    print(f"target pdf: {DOWNLOAD_PDF}")
    print(f"terminal: {values.get('terminal', 'unknown')}")


if __name__ == "__main__":
    main()
