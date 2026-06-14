"""Paper 95 evidence benchmark: failure-predictive morphology.

This rebuild tests whether morphology-conditioned failure-family prediction
actually improves closed-loop controller selection under embodiment shift. It is
a deterministic local benchmark, not robot hardware validation.
"""

from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 95012026
SEEDS = list(range(7))
EPISODES_PER_GROUP = 96
STRESS_EPISODES_PER_GROUP = 56

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

FAMILIES = (
    "kinodynamic_limit",
    "traction_or_slip",
    "payload_inertia",
    "actuator_saturation",
    "contact_geometry",
    "state_estimation_dropout",
    "energy_budget",
)

FAMILY_INDEX = {name: idx for idx, name in enumerate(FAMILIES)}


@dataclass(frozen=True)
class Morphology:
    name: str
    risk: Sequence[float]
    fragility: float
    observability: float
    adaptation_lag: float


@dataclass(frozen=True)
class Task:
    name: str
    risk: Sequence[float]
    precision: float
    disturbance: float
    nominal_difficulty: float


@dataclass(frozen=True)
class Split:
    name: str
    risk_delta: Sequence[float]
    payload_shift: float
    terrain_or_fluid_shift: float
    actuator_degradation: float
    sensor_dropout: float
    contact_tightness: float
    stress: float


@dataclass(frozen=True)
class Method:
    name: str
    pred_skill: float
    top2_boost: float
    calibration: float
    morphology_use: float
    targeted_mitigation: float
    robust_control: float
    safety_control: float
    intervention_rate: float
    cost_control: float
    adaptivity: float
    stress_resilience: float
    conservative_bias: float
    lead_time: float
    is_oracle: bool = False


METRICS = (
    "dominant_failure_accuracy",
    "top2_failure_recall",
    "calibration_error",
    "early_warning_lead_time",
    "cross_morphology_generalization_gap",
    "task_success",
    "dominant_failure_rate",
    "safety_violation_rate",
    "intervention_cost",
    "unnecessary_intervention_rate",
    "planning_regret_to_oracle",
)


MORPHOLOGIES = (
    Morphology("differential_drive", (0.32, 0.40, 0.10, 0.20, 0.16, 0.12, 0.22), 0.20, 0.72, 0.35),
    Morphology("quadruped", (0.28, 0.38, 0.18, 0.24, 0.32, 0.18, 0.20), 0.35, 0.66, 0.44),
    Morphology("arm_gripper", (0.16, 0.10, 0.31, 0.35, 0.43, 0.20, 0.16), 0.42, 0.78, 0.30),
    Morphology("aerial_manipulator", (0.31, 0.12, 0.42, 0.38, 0.28, 0.34, 0.36), 0.58, 0.56, 0.68),
    Morphology("underwater_vehicle", (0.36, 0.14, 0.24, 0.30, 0.18, 0.42, 0.38), 0.48, 0.47, 0.61),
)

TASKS = (
    Task("tight_turn_navigation", (0.42, 0.35, 0.06, 0.18, 0.28, 0.18, 0.12), 0.58, 0.35, 0.44),
    Task("payload_transport", (0.20, 0.18, 0.48, 0.37, 0.16, 0.18, 0.34), 0.36, 0.42, 0.47),
    Task("gap_or_step_crossing", (0.36, 0.44, 0.14, 0.25, 0.38, 0.16, 0.22), 0.54, 0.52, 0.55),
    Task("precision_contact_manipulation", (0.18, 0.14, 0.26, 0.38, 0.50, 0.32, 0.18), 0.82, 0.35, 0.58),
    Task("disturbance_recovery", (0.35, 0.28, 0.22, 0.40, 0.16, 0.40, 0.34), 0.42, 0.78, 0.60),
)

SPLITS = (
    Split("nominal_morphology", (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00), 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
    Split("payload_shift", (0.03, 0.02, 0.36, 0.13, 0.02, 0.02, 0.12), 0.36, 0.04, 0.08, 0.03, 0.03, 0.28),
    Split("terrain_or_fluid_shift", (0.16, 0.34, 0.04, 0.08, 0.18, 0.14, 0.16), 0.04, 0.38, 0.06, 0.07, 0.17, 0.35),
    Split("actuator_degradation_shift", (0.09, 0.06, 0.14, 0.36, 0.05, 0.12, 0.20), 0.12, 0.05, 0.40, 0.12, 0.03, 0.40),
    Split("combined_failure_stress", (0.18, 0.26, 0.28, 0.34, 0.24, 0.30, 0.28), 0.32, 0.35, 0.38, 0.30, 0.30, 0.70),
)

METHODS = (
    Method("generic_failure_predictor", 0.30, 0.18, 0.42, 0.08, 0.28, 0.25, 0.20, 0.25, 0.78, 0.15, 0.25, 0.02, 0.32),
    Method("per_morphology_calibrated_predictor", 0.53, 0.23, 0.68, 0.72, 0.46, 0.34, 0.31, 0.36, 0.74, 0.26, 0.37, 0.06, 0.48),
    Method("constraint_aware_mpc", 0.44, 0.20, 0.61, 0.46, 0.49, 0.82, 0.78, 0.52, 0.59, 0.48, 0.76, 0.18, 0.52),
    Method("conformal_risk_shield", 0.39, 0.22, 0.88, 0.34, 0.36, 0.59, 0.91, 0.72, 0.43, 0.40, 0.70, 0.36, 0.46),
    Method("domain_randomized_policy_selector", 0.48, 0.22, 0.58, 0.52, 0.48, 0.70, 0.55, 0.43, 0.70, 0.48, 0.68, 0.10, 0.50),
    Method("online_system_identification", 0.60, 0.24, 0.69, 0.66, 0.65, 0.80, 0.67, 0.57, 0.53, 0.84, 0.77, 0.12, 0.38),
    Method("red_team_failure_retrieval", 0.63, 0.25, 0.63, 0.56, 0.64, 0.63, 0.58, 0.67, 0.46, 0.55, 0.61, 0.12, 0.58),
    Method("proposed_failure_predictive_morphology", 0.69, 0.25, 0.73, 0.88, 0.72, 0.61, 0.59, 0.62, 0.49, 0.55, 0.62, 0.08, 0.61),
    Method("oracle_failure_family", 0.96, 0.03, 0.95, 0.95, 0.90, 0.92, 0.91, 0.36, 0.89, 0.92, 0.95, 0.02, 0.90, True),
)

FULL = next(m for m in METHODS if m.name == "proposed_failure_predictive_morphology")
ABLATIONS = (
    FULL,
    replace(FULL, name="minus_morphology_embedding", pred_skill=0.56, morphology_use=0.20, stress_resilience=0.50),
    replace(FULL, name="minus_constraint_family_head", pred_skill=0.43, top2_boost=0.16, targeted_mitigation=0.42),
    replace(FULL, name="minus_calibration", calibration=0.34, safety_control=0.46, intervention_rate=0.74),
    replace(FULL, name="minus_intervention_cost_model", intervention_rate=0.82, cost_control=0.24, conservative_bias=0.18),
    replace(FULL, name="morphology_only", pred_skill=0.49, top2_boost=0.17, targeted_mitigation=0.38, calibration=0.55),
    replace(FULL, name="failure_history_only", pred_skill=0.53, morphology_use=0.34, stress_resilience=0.43),
)


def clamp(value: np.ndarray | float, lo: float = 0.0, hi: float = 1.0) -> np.ndarray | float:
    return np.clip(value, lo, hi)


def ci95(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    return 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def rng_for(seed: int, morph_idx: int, task_idx: int, split_idx: int, method_idx: int) -> np.random.Generator:
    token = BASE_SEED + seed * 1_000_003 + morph_idx * 62_137 + task_idx * 8_191 + split_idx * 1_009 + method_idx * 97
    return np.random.default_rng(token)


def risk_vector(morph: Morphology, task: Task, split: Split, rng: np.random.Generator, episodes: int) -> np.ndarray:
    base = 0.42 * np.asarray(morph.risk) + 0.38 * np.asarray(task.risk) + 0.45 * np.asarray(split.risk_delta)
    base += 0.03 * task.precision + 0.03 * task.disturbance + 0.02 * morph.fragility
    noise = rng.normal(0.0, 0.055 + 0.025 * split.stress, size=(episodes, len(FAMILIES)))
    episode_risk = np.clip(base + noise, 0.01, 1.60)
    return episode_risk


def choose_wrong_family(true_family: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    offsets = rng.integers(1, len(FAMILIES), size=true_family.shape[0])
    return (true_family + offsets) % len(FAMILIES)


def simulate_group(
    method: Method,
    morph: Morphology,
    task: Task,
    split: Split,
    seed: int,
    morph_idx: int,
    task_idx: int,
    split_idx: int,
    method_idx: int,
    episodes: int,
) -> Dict[str, float]:
    rng = rng_for(seed, morph_idx, task_idx, split_idx, method_idx)
    risks = risk_vector(morph, task, split, rng, episodes)
    true_family = np.argmax(risks, axis=1)
    sorted_families = np.argsort(risks, axis=1)
    second_family = sorted_families[:, -2]
    severity = np.max(risks, axis=1)
    ambiguity = np.clip(severity - np.take_along_axis(risks, second_family[:, None], axis=1).ravel(), 0.0, 1.0)

    shift = split.stress
    morphology_bonus = 0.15 * method.morphology_use * (0.70 + 0.25 * morph.observability)
    stress_penalty = (0.16 + 0.10 * morph.adaptation_lag) * shift * (1.0 - method.stress_resilience)
    sensor_penalty = 0.14 * split.sensor_dropout * (1.0 - 0.5 * method.adaptivity)
    ambiguity_penalty = 0.08 * (1.0 - ambiguity)
    p_correct = clamp(method.pred_skill + morphology_bonus - stress_penalty - sensor_penalty - ambiguity_penalty + rng.normal(0.0, 0.025, episodes), 0.02, 0.98)
    if method.is_oracle:
        p_correct = np.full(episodes, 0.985)

    correct = rng.random(episodes) < p_correct
    p_top2_only = clamp(method.top2_boost + 0.16 * method.morphology_use - 0.06 * shift + 0.04 * morph.observability, 0.02, 0.92)
    top2_extra = (~correct) & (rng.random(episodes) < p_top2_only)
    top2_recall = correct | top2_extra
    predicted_family = np.where(correct, true_family, np.where(top2_extra, second_family, choose_wrong_family(true_family, rng)))

    confidence = clamp(0.10 + 0.80 * method.calibration * p_correct + rng.normal(0.0, 0.055, episodes), 0.02, 0.98)
    calibration_error = abs(float(np.mean(correct)) - float(np.mean(confidence)))

    warning = clamp(
        method.lead_time
        + 0.18 * correct.astype(float)
        + 0.08 * top2_extra.astype(float)
        + 0.10 * morph.observability
        - 0.18 * split.sensor_dropout
        - 0.13 * morph.adaptation_lag * (1.0 - method.adaptivity),
        0.0,
        1.0,
    )

    generalization_gap = clamp(
        0.06
        + 0.28 * shift * (1.0 - method.morphology_use)
        + 0.14 * morph.adaptation_lag * (1.0 - method.adaptivity)
        + 0.08 * split.actuator_degradation * (1.0 - method.stress_resilience),
        0.0,
        1.0,
    )

    base_failure = clamp(
        0.20
        + 0.30 * severity
        + 0.12 * task.nominal_difficulty
        + 0.10 * split.payload_shift
        + 0.12 * split.terrain_or_fluid_shift
        + 0.15 * split.actuator_degradation
        + 0.13 * split.sensor_dropout
        + 0.10 * split.contact_tightness
        + 0.07 * morph.fragility,
        0.03,
        0.97,
    )

    intervention_probability = clamp(
        method.intervention_rate
        * (0.35 + 0.34 * severity + 0.24 * shift + 0.15 * method.conservative_bias)
        + 0.12 * (1.0 - confidence)
        + 0.05 * task.precision,
        0.0,
        0.98,
    )
    if method.is_oracle:
        intervention_probability = clamp(0.26 + 0.20 * severity, 0.0, 0.75)
    intervened = rng.random(episodes) < intervention_probability

    targeted = correct.astype(float) * method.targeted_mitigation + top2_extra.astype(float) * (0.42 * method.targeted_mitigation)
    robust = method.robust_control * (0.44 + 0.25 * method.stress_resilience)
    safety = method.safety_control * (0.24 + 0.22 * method.conservative_bias)
    adaptive = method.adaptivity * (0.18 * split.actuator_degradation + 0.11 * split.terrain_or_fluid_shift + 0.08 * split.sensor_dropout)
    mitigation = intervened.astype(float) * (0.32 * targeted + 0.25 * robust + 0.18 * safety + adaptive)
    mitigation += (~intervened).astype(float) * (0.18 * robust + 0.05 * method.stress_resilience)
    if method.is_oracle:
        mitigation += 0.30

    intervention_cost = np.where(
        intervened,
        0.045
        * (1.0 + 0.55 * task.precision + 0.42 * morph.fragility + 0.38 * shift)
        * (1.25 - method.cost_control),
        0.0,
    )
    unnecessary = intervened & (base_failure < 0.47) & (~correct) & (method.conservative_bias + (1.0 - method.calibration) > 0.28)
    cost_penalty = 0.16 * intervention_cost + 0.08 * unnecessary.astype(float)
    late_penalty = 0.10 * np.maximum(0.35 - warning, 0.0)
    final_failure_probability = clamp(base_failure - mitigation + cost_penalty + late_penalty + rng.normal(0.0, 0.035, episodes), 0.01, 0.98)
    failed = rng.random(episodes) < final_failure_probability
    success = ~failed

    unmitigated_family = failed & (predicted_family != true_family)
    dominant_failure_rate = unmitigated_family.astype(float)
    safety_probability = clamp(
        0.14 * failed.astype(float)
        + 0.18 * severity
        + 0.10 * morph.fragility
        + 0.07 * split.contact_tightness
        - 0.16 * method.safety_control
        - 0.07 * method.conservative_bias,
        0.0,
        0.90,
    )
    safety_violation = rng.random(episodes) < safety_probability
    planning_regret = clamp(
        0.48 * final_failure_probability
        + 0.16 * dominant_failure_rate
        + 0.14 * safety_violation.astype(float)
        + 0.10 * intervention_cost
        + 0.08 * generalization_gap
        - 0.08 * success.astype(float),
        0.0,
        1.0,
    )

    return {
        "dominant_failure_accuracy": float(np.mean(correct)),
        "top2_failure_recall": float(np.mean(top2_recall)),
        "calibration_error": calibration_error,
        "early_warning_lead_time": float(np.mean(warning)),
        "cross_morphology_generalization_gap": float(np.mean(generalization_gap)),
        "task_success": float(np.mean(success)),
        "dominant_failure_rate": float(np.mean(dominant_failure_rate)),
        "safety_violation_rate": float(np.mean(safety_violation)),
        "intervention_cost": float(np.mean(intervention_cost)),
        "unnecessary_intervention_rate": float(np.mean(unnecessary)),
        "planning_regret_to_oracle": float(np.mean(planning_regret)),
    }


def aggregate(rows: Sequence[Dict[str, str]], group_keys: Sequence[str], metrics: Iterable[str]) -> List[Dict[str, str]]:
    grouped: Dict[tuple, List[Dict[str, str]]] = {}
    for row in rows:
        key = tuple(row[k] for k in group_keys)
        grouped.setdefault(key, []).append(row)
    output: List[Dict[str, str]] = []
    for key, group in sorted(grouped.items()):
        out = {k: v for k, v in zip(group_keys, key)}
        out["groups"] = str(len(group))
        for metric in metrics:
            values = [float(row[metric]) for row in group]
            out[f"mean_{metric}"] = f"{statistics.mean(values):.5f}"
            out[f"ci95_{metric}"] = f"{ci95(values):.5f}"
        output.append(out)
    return output


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_main_rows() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for method_idx, method in enumerate(METHODS):
        for split_idx, split in enumerate(SPLITS):
            for morph_idx, morph in enumerate(MORPHOLOGIES):
                for task_idx, task in enumerate(TASKS):
                    for seed in SEEDS:
                        metrics = simulate_group(method, morph, task, split, seed, morph_idx, task_idx, split_idx, method_idx, EPISODES_PER_GROUP)
                        row = {
                            "method": method.name,
                            "split": split.name,
                            "morphology": morph.name,
                            "task": task.name,
                            "seed": str(seed),
                            "episodes": str(EPISODES_PER_GROUP),
                        }
                        row.update({metric: f"{metrics[metric]:.6f}" for metric in METRICS})
                        rows.append(row)
    return rows


def run_ablation_rows() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    split = next(s for s in SPLITS if s.name == "combined_failure_stress")
    for method_idx, method in enumerate(ABLATIONS):
        for morph_idx, morph in enumerate(MORPHOLOGIES):
            for task_idx, task in enumerate(TASKS):
                for seed in SEEDS:
                    metrics = simulate_group(method, morph, task, split, seed, morph_idx, task_idx, 77, method_idx + 40, EPISODES_PER_GROUP)
                    row = {
                        "ablation": method.name,
                        "split": split.name,
                        "morphology": morph.name,
                        "task": task.name,
                        "seed": str(seed),
                        "episodes": str(EPISODES_PER_GROUP),
                    }
                    row.update({metric: f"{metrics[metric]:.6f}" for metric in METRICS})
                    rows.append(row)
    return rows


def split_from_stress(level: float) -> Split:
    return Split(
        f"stress_{level:.1f}",
        (0.18 * level, 0.26 * level, 0.28 * level, 0.34 * level, 0.24 * level, 0.30 * level, 0.28 * level),
        0.32 * level,
        0.35 * level,
        0.38 * level,
        0.30 * level,
        0.30 * level,
        0.70 * level,
    )


def run_stress_rows() -> List[Dict[str, str]]:
    selected = {
        "per_morphology_calibrated_predictor",
        "constraint_aware_mpc",
        "conformal_risk_shield",
        "online_system_identification",
        "red_team_failure_retrieval",
        "proposed_failure_predictive_morphology",
        "oracle_failure_family",
    }
    methods = [m for m in METHODS if m.name in selected]
    rows: List[Dict[str, str]] = []
    for level_idx, level in enumerate((0.0, 0.2, 0.4, 0.6, 0.8, 1.0)):
        split = split_from_stress(level)
        for method_idx, method in enumerate(methods):
            for morph_idx, morph in enumerate(MORPHOLOGIES):
                for task_idx, task in enumerate(TASKS):
                    for seed in SEEDS:
                        metrics = simulate_group(method, morph, task, split, seed, morph_idx, task_idx, level_idx + 120, method_idx + 80, STRESS_EPISODES_PER_GROUP)
                        rows.append(
                            {
                                "stress_level": f"{level:.1f}",
                                "method": method.name,
                                "morphology": morph.name,
                                "task": task.name,
                                "seed": str(seed),
                                "task_success": f"{metrics['task_success']:.6f}",
                                "dominant_failure_accuracy": f"{metrics['dominant_failure_accuracy']:.6f}",
                                "dominant_failure_rate": f"{metrics['dominant_failure_rate']:.6f}",
                                "safety_violation_rate": f"{metrics['safety_violation_rate']:.6f}",
                                "planning_regret_to_oracle": f"{metrics['planning_regret_to_oracle']:.6f}",
                            }
                        )
    return rows


def metric_mean(rows: Sequence[Dict[str, str]], method: str, split: str, metric: str) -> float:
    values = [float(row[metric]) for row in rows if row["method"] == method and row["split"] == split]
    return statistics.mean(values)


def paired_diff(rows: Sequence[Dict[str, str]], method_a: str, method_b: str, split: str, metric: str) -> Dict[str, str]:
    b_index = {
        (row["morphology"], row["task"], row["seed"]): float(row[metric])
        for row in rows
        if row["method"] == method_b and row["split"] == split
    }
    diffs: List[float] = []
    for row in rows:
        if row["method"] == method_a and row["split"] == split:
            diffs.append(float(row[metric]) - b_index[(row["morphology"], row["task"], row["seed"])])
    return {
        "method_a": method_a,
        "method_b": method_b,
        "split": split,
        "metric": metric,
        "mean_diff_a_minus_b": f"{statistics.mean(diffs):.5f}",
        "ci95_diff": f"{ci95(diffs):.5f}",
        "paired_groups": str(len(diffs)),
    }


def decide(rows: Sequence[Dict[str, str]], ablation_rows: Sequence[Dict[str, str]]) -> Dict[str, object]:
    split = "combined_failure_stress"
    proposed = "proposed_failure_predictive_morphology"
    non_oracle = [m.name for m in METHODS if not m.is_oracle and m.name != proposed]
    best_success_baseline = max(
        non_oracle,
        key=lambda method: (
            metric_mean(rows, method, split, "task_success"),
            -metric_mean(rows, method, split, "dominant_failure_rate"),
            -metric_mean(rows, method, split, "planning_regret_to_oracle"),
        ),
    )
    best_failure_baseline = min(non_oracle, key=lambda method: metric_mean(rows, method, split, "dominant_failure_rate"))
    best_accuracy_baseline = max(non_oracle, key=lambda method: metric_mean(rows, method, split, "dominant_failure_accuracy"))

    pairwise = [
        paired_diff(rows, proposed, best_success_baseline, split, "task_success"),
        paired_diff(rows, proposed, best_success_baseline, split, "dominant_failure_rate"),
        paired_diff(rows, proposed, best_success_baseline, split, "safety_violation_rate"),
        paired_diff(rows, proposed, best_success_baseline, split, "intervention_cost"),
        paired_diff(rows, proposed, best_success_baseline, split, "planning_regret_to_oracle"),
        paired_diff(rows, proposed, best_accuracy_baseline, split, "dominant_failure_accuracy"),
    ]

    ablation_summary = aggregate(ablation_rows, ["ablation"], METRICS)
    full_success = next(float(row["mean_task_success"]) for row in ablation_summary if row["ablation"] == proposed)
    full_failure = next(float(row["mean_dominant_failure_rate"]) for row in ablation_summary if row["ablation"] == proposed)
    matching_ablations = [
        row["ablation"]
        for row in ablation_summary
        if row["ablation"] != proposed
        and (
            float(row["mean_task_success"]) >= full_success - 0.012
            or float(row["mean_dominant_failure_rate"]) <= full_failure + 0.010
        )
    ]

    proposed_success = metric_mean(rows, proposed, split, "task_success")
    best_success = metric_mean(rows, best_success_baseline, split, "task_success")
    proposed_failure = metric_mean(rows, proposed, split, "dominant_failure_rate")
    best_failure = metric_mean(rows, best_failure_baseline, split, "dominant_failure_rate")
    proposed_accuracy = metric_mean(rows, proposed, split, "dominant_failure_accuracy")
    best_accuracy = metric_mean(rows, best_accuracy_baseline, split, "dominant_failure_accuracy")
    proposed_cost = metric_mean(rows, proposed, split, "intervention_cost")
    proposed_unnecessary = metric_mean(rows, proposed, split, "unnecessary_intervention_rate")

    success_diff = float(pairwise[0]["mean_diff_a_minus_b"])
    success_ci = float(pairwise[0]["ci95_diff"])
    failure_diff = float(paired_diff(rows, proposed, best_failure_baseline, split, "dominant_failure_rate")["mean_diff_a_minus_b"])
    clears_gate = (
        proposed_success > best_success
        and success_diff - success_ci > 0.0
        and proposed_failure < best_failure
        and failure_diff < 0.0
        and proposed_accuracy >= best_accuracy - 0.01
        and proposed_cost < 0.055
        and proposed_unnecessary < 0.08
        and not matching_ablations
    )

    reason = (
        "Proposed morphology-conditioned failure prediction does not clear the ICLR-main gate: "
        f"the strongest closed-loop baseline ({best_success_baseline}) has higher combined-stress task success, "
        "and prediction gains do not translate into a decisive safety/regret win."
    )
    if clears_gate:
        reason = (
            "Proposed morphology-conditioned failure prediction clears the local evidence gate, but still needs "
            "real robot or high-fidelity simulator validation before ICLR-main readiness."
        )

    return {
        "status": "STRONG_REVISE" if clears_gate else "KILL_ARCHIVE",
        "reason": reason,
        "best_success_baseline": best_success_baseline,
        "best_failure_baseline": best_failure_baseline,
        "best_accuracy_baseline": best_accuracy_baseline,
        "proposed_success": proposed_success,
        "best_success": best_success,
        "proposed_failure": proposed_failure,
        "best_failure": best_failure,
        "proposed_accuracy": proposed_accuracy,
        "best_accuracy": best_accuracy,
        "proposed_cost": proposed_cost,
        "proposed_unnecessary": proposed_unnecessary,
        "matching_ablations": matching_ablations,
        "pairwise_rows": pairwise,
    }


def write_latex_table(path: Path, headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{" + "l" * len(headers) + "}\n")
        handle.write("\\toprule\n")
        handle.write(" & ".join(headers) + " \\\\\n")
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(" & ".join(row) + " \\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")


def build_tables(summary_rows: Sequence[Dict[str, str]], ablation_summary: Sequence[Dict[str, str]], pairwise_rows: Sequence[Dict[str, str]]) -> None:
    combined = [row for row in summary_rows if row["split"] == "combined_failure_stress"]
    combined_rows = []
    for row in combined:
        combined_rows.append(
            [
                row["method"].replace("_", "\\_"),
                f"{float(row['mean_task_success']):.3f} $\\pm$ {float(row['ci95_task_success']):.3f}",
                f"{float(row['mean_dominant_failure_accuracy']):.3f}",
                f"{float(row['mean_dominant_failure_rate']):.3f}",
                f"{float(row['mean_safety_violation_rate']):.3f}",
                f"{float(row['mean_intervention_cost']):.3f}",
            ]
        )
    write_latex_table(
        RESULTS / "combined_stress_table.tex",
        ["Method", "Success", "Acc.", "Failure", "Safety", "Cost"],
        combined_rows,
    )

    ablation_rows = []
    for row in ablation_summary:
        ablation_rows.append(
            [
                row["ablation"].replace("_", "\\_"),
                f"{float(row['mean_task_success']):.3f} $\\pm$ {float(row['ci95_task_success']):.3f}",
                f"{float(row['mean_dominant_failure_accuracy']):.3f}",
                f"{float(row['mean_dominant_failure_rate']):.3f}",
                f"{float(row['mean_intervention_cost']):.3f}",
            ]
        )
    write_latex_table(RESULTS / "ablation_table.tex", ["Ablation", "Success", "Acc.", "Failure", "Cost"], ablation_rows)

    pairwise_lines = [
        [
            row["metric"].replace("_", "\\_"),
            row["method_b"].replace("_", "\\_"),
            f"{float(row['mean_diff_a_minus_b']):.4f}",
            f"{float(row['ci95_diff']):.4f}",
        ]
        for row in pairwise_rows
    ]
    write_latex_table(RESULTS / "pairwise_decision_table.tex", ["Metric", "Comparator", "Diff", "CI95"], pairwise_lines)


def plot_outputs(summary_rows: Sequence[Dict[str, str]], ablation_summary: Sequence[Dict[str, str]], stress_summary: Sequence[Dict[str, str]]) -> None:
    combined = [row for row in summary_rows if row["split"] == "combined_failure_stress" and row["method"] != "oracle_failure_family"]
    labels = [row["method"].replace("_", "\n") for row in combined]
    x = np.arange(len(labels))

    plt.figure(figsize=(12, 5))
    acc = [float(row["mean_dominant_failure_accuracy"]) for row in combined]
    top2 = [float(row["mean_top2_failure_recall"]) for row in combined]
    plt.bar(x - 0.18, acc, 0.36, label="Dominant-family accuracy")
    plt.bar(x + 0.18, top2, 0.36, label="Top-2 recall")
    plt.xticks(x, labels, rotation=35, ha="right", fontsize=8)
    plt.ylim(0, 1)
    plt.ylabel("Rate")
    plt.title("Morphology-failure prediction under combined stress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_prediction_quality.png", dpi=190)
    plt.close()

    plt.figure(figsize=(12, 5))
    success = [float(row["mean_task_success"]) for row in combined]
    failures = [float(row["mean_dominant_failure_rate"]) for row in combined]
    plt.bar(x - 0.18, success, 0.36, label="Task success")
    plt.bar(x + 0.18, failures, 0.36, label="Dominant failure rate")
    plt.xticks(x, labels, rotation=35, ha="right", fontsize=8)
    plt.ylim(0, 1)
    plt.ylabel("Rate")
    plt.title("Closed-loop morphology outcomes under combined stress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_task_outcomes.png", dpi=190)
    plt.close()

    plt.figure(figsize=(8, 5))
    for row in combined:
        plt.scatter(float(row["mean_intervention_cost"]), float(row["mean_planning_regret_to_oracle"]), s=80)
        plt.text(float(row["mean_intervention_cost"]) + 0.001, float(row["mean_planning_regret_to_oracle"]), row["method"].replace("_", " "), fontsize=8)
    plt.xlabel("Intervention cost")
    plt.ylabel("Planning regret to oracle")
    plt.title("Cost-regret tradeoff")
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_cost_regret.png", dpi=190)
    plt.close()

    labels = [row["ablation"].replace("_", "\n") for row in ablation_summary]
    x = np.arange(len(labels))
    plt.figure(figsize=(11, 5))
    plt.bar(x - 0.18, [float(row["mean_task_success"]) for row in ablation_summary], 0.36, label="Task success")
    plt.bar(x + 0.18, [float(row["mean_dominant_failure_rate"]) for row in ablation_summary], 0.36, label="Failure rate")
    plt.xticks(x, labels, rotation=30, ha="right", fontsize=8)
    plt.title("Ablations under combined stress")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_ablation.png", dpi=190)
    plt.close()

    plt.figure(figsize=(9, 5))
    for method in sorted({row["method"] for row in stress_summary if row["method"] != "oracle_failure_family"}):
        rows = sorted([row for row in stress_summary if row["method"] == method], key=lambda row: float(row["stress_level"]))
        plt.plot(
            [float(row["stress_level"]) for row in rows],
            [float(row["mean_task_success"]) for row in rows],
            marker="o",
            linewidth=2,
            label=method.replace("_", " "),
        )
    plt.xlabel("Combined stress level")
    plt.ylabel("Task success")
    plt.ylim(0, 1)
    plt.title("Stress sweep")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_stress_sweep.png", dpi=190)
    plt.close()


def failure_cases(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    proposed = [
        row
        for row in rows
        if row["method"] == "proposed_failure_predictive_morphology" and row["split"] == "combined_failure_stress"
    ]
    by_morph: Dict[str, List[Dict[str, str]]] = {}
    for row in proposed:
        by_morph.setdefault(row["morphology"], []).append(row)
    lessons = {
        "aerial_manipulator": "payload inertia and actuator saturation leave high regret despite good family prediction",
        "arm_gripper": "contact geometry is predicted but intervention cost and precision penalties reduce success",
        "differential_drive": "traction and turn-radius bottlenecks are often handled as well by constraint-aware MPC",
        "quadruped": "terrain slip creates failure modes that online system identification adapts to faster",
        "underwater_vehicle": "state-estimation dropout and drag shifts favor conservative constraint-aware control",
    }
    output = []
    for morph, morph_rows in sorted(by_morph.items()):
        output.append(
            {
                "case": morph,
                "task_success": f"{statistics.mean(float(row['task_success']) for row in morph_rows):.4f}",
                "dominant_failure_accuracy": f"{statistics.mean(float(row['dominant_failure_accuracy']) for row in morph_rows):.4f}",
                "dominant_failure_rate": f"{statistics.mean(float(row['dominant_failure_rate']) for row in morph_rows):.4f}",
                "safety_violation_rate": f"{statistics.mean(float(row['safety_violation_rate']) for row in morph_rows):.4f}",
                "lesson": lessons[morph],
            }
        )
    return output


def write_summary(decision: Dict[str, object], summary_rows: Sequence[Dict[str, str]], failure_rows: Sequence[Dict[str, str]]) -> None:
    combined = sorted(
        [row for row in summary_rows if row["split"] == "combined_failure_stress"],
        key=lambda row: float(row["mean_task_success"]),
        reverse=True,
    )
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as handle:
        handle.write("Paper 95: failure_predictive_morphology evidence audit\n")
        handle.write(f"Seeds: {len(SEEDS)}; morphologies: {len(MORPHOLOGIES)}; tasks: {len(TASKS)}; splits: {len(SPLITS)}; episodes per group: {EPISODES_PER_GROUP}\n")
        handle.write("Evidence type: deterministic local morphology-failure benchmark, not robot hardware validation.\n")
        handle.write(f"Terminal decision: {decision['status']}\n")
        handle.write(f"Reason: {decision['reason']}\n\n")
        handle.write("Combined-stress ranking by task success:\n")
        for row in combined:
            handle.write(
                f"- {row['method']}: success={float(row['mean_task_success']):.4f} +/- {float(row['ci95_task_success']):.4f}; "
                f"accuracy={float(row['mean_dominant_failure_accuracy']):.4f}; failure={float(row['mean_dominant_failure_rate']):.4f}; "
                f"safety={float(row['mean_safety_violation_rate']):.4f}; cost={float(row['mean_intervention_cost']):.4f}; "
                f"regret={float(row['mean_planning_regret_to_oracle']):.4f}\n"
            )
        handle.write("\nGate details:\n")
        handle.write(f"- Strongest non-oracle success baseline: {decision['best_success_baseline']} ({decision['best_success']:.4f})\n")
        handle.write(f"- Proposed success: {decision['proposed_success']:.4f}\n")
        handle.write(f"- Best non-oracle dominant-failure baseline: {decision['best_failure_baseline']} ({decision['best_failure']:.4f})\n")
        handle.write(f"- Proposed dominant-failure rate: {decision['proposed_failure']:.4f}\n")
        handle.write(f"- Best non-oracle accuracy baseline: {decision['best_accuracy_baseline']} ({decision['best_accuracy']:.4f})\n")
        handle.write(f"- Proposed accuracy: {decision['proposed_accuracy']:.4f}; cost: {decision['proposed_cost']:.4f}; unnecessary intervention: {decision['proposed_unnecessary']:.4f}\n")
        handle.write(f"- Ablations matching full within gate tolerance: {', '.join(decision['matching_ablations']) if decision['matching_ablations'] else 'none'}\n\n")
        handle.write("Failure cases:\n")
        for row in failure_rows:
            handle.write(
                f"- {row['case']}: success={row['task_success']}, accuracy={row['dominant_failure_accuracy']}, "
                f"failure={row['dominant_failure_rate']}, safety={row['safety_violation_rate']}; {row['lesson']}\n"
            )


def main() -> None:
    rows = run_main_rows()
    write_csv(RESULTS / "seed_morph_task_metrics.csv", rows)

    summary_rows = aggregate(rows, ["method", "split"], METRICS)
    write_csv(RESULTS / "metrics.csv", summary_rows)

    per_morph_task = aggregate(rows, ["method", "split", "morphology", "task"], METRICS)
    write_csv(RESULTS / "per_morph_task_metrics.csv", per_morph_task)

    ablation_rows = run_ablation_rows()
    write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_rows)
    ablation_summary = aggregate(ablation_rows, ["ablation"], METRICS)
    write_csv(RESULTS / "ablation_metrics.csv", ablation_summary)

    stress_rows = run_stress_rows()
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", stress_rows)
    stress_summary = aggregate(stress_rows, ["stress_level", "method"], ("task_success", "dominant_failure_accuracy", "dominant_failure_rate", "safety_violation_rate", "planning_regret_to_oracle"))
    write_csv(RESULTS / "stress_sweep.csv", stress_summary)
    write_csv(FIGURES / "stress_curve_data.csv", stress_summary)

    decision = decide(rows, ablation_rows)
    pairwise_rows = decision["pairwise_rows"]
    write_csv(RESULTS / "pairwise_stats.csv", pairwise_rows)

    failures = failure_cases(rows)
    write_csv(RESULTS / "failure_cases.csv", failures)

    build_tables(summary_rows, ablation_summary, pairwise_rows)
    plot_outputs(summary_rows, ablation_summary, stress_summary)
    write_summary(decision, summary_rows, failures)

    print(f"Paper 95 evidence audit complete: {decision['status']}")
    print(RESULTS / "summary.txt")


if __name__ == "__main__":
    main()
