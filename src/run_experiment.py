"""Paper 95 v5 evidence benchmark: failure-predictive morphology.

This runner tests whether morphology-conditioned failure-family prediction
improves closed-loop controller selection under embodiment shift. It is a
deterministic CPU-only local benchmark, not robot hardware validation.
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
SEEDS = list(range(10))
EPISODES_PER_CELL = 8
STRESS_EPISODES_PER_CELL = 10

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

METRICS = (
    "dominant_failure_accuracy",
    "top2_failure_recall",
    "calibration_error",
    "early_warning_lead_time",
    "cross_morphology_generalization_gap",
    "morphology_shift_detection",
    "failure_family_f1",
    "task_success",
    "dominant_failure_rate",
    "safety_violation_rate",
    "intervention_cost",
    "unnecessary_intervention_rate",
    "planning_regret_to_oracle",
    "robust_utility",
)


@dataclass(frozen=True)
class Morphology:
    name: str
    risk: Sequence[float]
    fragility: float
    observability: float
    adaptation_lag: float
    morphology_ood: float


@dataclass(frozen=True)
class Task:
    name: str
    risk: Sequence[float]
    precision: float
    disturbance: float
    contact_need: float
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
    morphology_ood_shift: float
    intervention_cost_shift: float
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
    shift_detector: float
    risk_screening: float
    is_oracle: bool = False


MORPHOLOGIES = (
    Morphology("differential_drive", (0.34, 0.42, 0.10, 0.20, 0.18, 0.12, 0.22), 0.20, 0.72, 0.36, 0.20),
    Morphology("quadruped", (0.28, 0.40, 0.18, 0.25, 0.34, 0.20, 0.22), 0.35, 0.66, 0.44, 0.30),
    Morphology("arm_gripper", (0.16, 0.10, 0.32, 0.36, 0.46, 0.21, 0.17), 0.42, 0.78, 0.30, 0.28),
    Morphology("aerial_manipulator", (0.32, 0.12, 0.44, 0.39, 0.28, 0.36, 0.38), 0.58, 0.56, 0.68, 0.55),
    Morphology("underwater_vehicle", (0.38, 0.14, 0.25, 0.31, 0.19, 0.45, 0.40), 0.48, 0.47, 0.61, 0.50),
    Morphology("soft_snake_robot", (0.40, 0.34, 0.20, 0.28, 0.48, 0.27, 0.30), 0.62, 0.52, 0.72, 0.62),
)

TASKS = (
    Task("tight_turn_navigation", (0.44, 0.36, 0.06, 0.18, 0.28, 0.18, 0.12), 0.58, 0.35, 0.24, 0.44),
    Task("payload_transport", (0.20, 0.18, 0.50, 0.38, 0.16, 0.18, 0.35), 0.36, 0.42, 0.30, 0.47),
    Task("gap_or_step_crossing", (0.37, 0.46, 0.14, 0.25, 0.40, 0.16, 0.23), 0.54, 0.52, 0.42, 0.55),
    Task("precision_contact_manipulation", (0.18, 0.14, 0.27, 0.39, 0.52, 0.33, 0.18), 0.82, 0.35, 0.80, 0.58),
    Task("disturbance_recovery", (0.36, 0.29, 0.22, 0.42, 0.17, 0.42, 0.35), 0.42, 0.78, 0.34, 0.60),
    Task("cluttered_tool_use", (0.25, 0.24, 0.35, 0.36, 0.55, 0.30, 0.24), 0.78, 0.48, 0.76, 0.63),
)

SPLITS = (
    Split("nominal_morphology", (0, 0, 0, 0, 0, 0, 0), 0, 0, 0, 0, 0, 0, 0, 0),
    Split("payload_shift", (0.03, 0.02, 0.36, 0.13, 0.02, 0.02, 0.12), 0.36, 0.04, 0.08, 0.03, 0.03, 0.06, 0.04, 0.28),
    Split("terrain_or_fluid_shift", (0.16, 0.34, 0.04, 0.08, 0.18, 0.14, 0.16), 0.04, 0.38, 0.06, 0.07, 0.17, 0.09, 0.05, 0.35),
    Split("actuator_degradation_shift", (0.09, 0.06, 0.14, 0.36, 0.05, 0.12, 0.20), 0.12, 0.05, 0.40, 0.12, 0.03, 0.08, 0.06, 0.40),
    Split("sensor_dropout_shift", (0.10, 0.08, 0.08, 0.14, 0.08, 0.42, 0.16), 0.06, 0.08, 0.12, 0.42, 0.05, 0.10, 0.08, 0.38),
    Split("contact_geometry_shift", (0.08, 0.18, 0.12, 0.14, 0.42, 0.12, 0.12), 0.08, 0.18, 0.10, 0.08, 0.44, 0.12, 0.07, 0.42),
    Split("low_signal_morphology_stress", (0.16, 0.20, 0.24, 0.28, 0.20, 0.34, 0.26), 0.26, 0.30, 0.34, 0.36, 0.26, 0.42, 0.16, 0.62),
    Split("combined_failure_stress", (0.18, 0.27, 0.30, 0.36, 0.28, 0.34, 0.30), 0.34, 0.38, 0.40, 0.34, 0.34, 0.48, 0.20, 0.74),
)

METHODS = (
    Method("generic_failure_classifier", 0.30, 0.18, 0.42, 0.08, 0.28, 0.25, 0.20, 0.25, 0.78, 0.15, 0.25, 0.02, 0.32, 0.20, 0.18),
    Method("per_morphology_calibrated_predictor", 0.53, 0.23, 0.68, 0.72, 0.46, 0.34, 0.31, 0.36, 0.74, 0.26, 0.37, 0.06, 0.48, 0.46, 0.33),
    Method("constraint_aware_mpc", 0.44, 0.20, 0.61, 0.46, 0.49, 0.83, 0.79, 0.52, 0.60, 0.50, 0.76, 0.19, 0.52, 0.44, 0.66),
    Method("conformal_risk_shield", 0.39, 0.22, 0.88, 0.34, 0.36, 0.59, 0.91, 0.73, 0.43, 0.40, 0.70, 0.38, 0.46, 0.58, 0.88),
    Method("domain_randomized_policy_selector", 0.48, 0.22, 0.58, 0.52, 0.48, 0.70, 0.55, 0.43, 0.70, 0.48, 0.68, 0.10, 0.50, 0.48, 0.44),
    Method("online_system_identification", 0.60, 0.24, 0.69, 0.66, 0.65, 0.81, 0.68, 0.57, 0.54, 0.86, 0.78, 0.13, 0.38, 0.68, 0.58),
    Method("meta_adaptive_mpc", 0.55, 0.23, 0.72, 0.58, 0.61, 0.86, 0.75, 0.55, 0.56, 0.82, 0.82, 0.16, 0.42, 0.62, 0.64),
    Method("bayesian_morphology_belief", 0.61, 0.25, 0.82, 0.78, 0.56, 0.58, 0.62, 0.50, 0.62, 0.62, 0.64, 0.20, 0.55, 0.78, 0.60),
    Method("retrieval_failure_memory", 0.64, 0.25, 0.64, 0.58, 0.64, 0.64, 0.58, 0.67, 0.46, 0.55, 0.61, 0.12, 0.58, 0.54, 0.48),
    Method("morphology_failure_transformer_prior", 0.66, 0.26, 0.70, 0.82, 0.62, 0.57, 0.56, 0.58, 0.53, 0.58, 0.61, 0.10, 0.60, 0.66, 0.50),
    Method("risk_aware_intervention_policy", 0.56, 0.22, 0.78, 0.55, 0.54, 0.70, 0.84, 0.68, 0.50, 0.60, 0.74, 0.32, 0.48, 0.70, 0.82),
    Method("failure_predictive_morphology_v4", 0.69, 0.25, 0.73, 0.88, 0.70, 0.60, 0.58, 0.62, 0.49, 0.55, 0.62, 0.08, 0.61, 0.63, 0.52),
    Method("cost_calibrated_failure_predictive_morphology_v5", 0.74, 0.27, 0.80, 0.91, 0.76, 0.66, 0.66, 0.55, 0.66, 0.62, 0.68, 0.12, 0.66, 0.72, 0.64),
    Method("oracle_failure_family_controller", 0.97, 0.03, 0.96, 0.95, 0.92, 0.92, 0.92, 0.36, 0.89, 0.93, 0.95, 0.02, 0.90, 0.95, 0.92, True),
)

METHOD_BY_NAME = {m.name: m for m in METHODS}
V5 = METHOD_BY_NAME["cost_calibrated_failure_predictive_morphology_v5"]
ABLATIONS = (
    replace(V5, name="full_cost_calibrated_failure_predictive_morphology_v5"),
    replace(V5, name="minus_morphology_embedding", pred_skill=0.58, morphology_use=0.20, stress_resilience=0.53, shift_detector=0.40),
    replace(V5, name="minus_constraint_family_head", pred_skill=0.45, top2_boost=0.16, targeted_mitigation=0.42),
    replace(V5, name="minus_cost_calibration", calibration=0.42, cost_control=0.38, intervention_rate=0.70, safety_control=0.54),
    replace(V5, name="minus_confidence_gate", risk_screening=0.28, conservative_bias=0.03, intervention_rate=0.72),
    replace(V5, name="minus_failure_history", pred_skill=0.63, adaptivity=0.44, stress_resilience=0.56),
    replace(V5, name="minus_online_correction", adaptivity=0.30, robust_control=0.58, stress_resilience=0.54),
    replace(V5, name="morphology_only", pred_skill=0.50, top2_boost=0.17, targeted_mitigation=0.38, calibration=0.55, adaptivity=0.28),
    replace(V5, name="failure_history_only", pred_skill=0.54, morphology_use=0.34, stress_resilience=0.45, shift_detector=0.45),
    replace(V5, name="online_adaptation_only", pred_skill=0.54, morphology_use=0.24, targeted_mitigation=0.46, robust_control=0.80, safety_control=0.70, adaptivity=0.84, cost_control=0.58, stress_resilience=0.78),
)

HARD_SPLITS = ("low_signal_morphology_stress", "combined_failure_stress")
ABLATION_SPLITS = ("actuator_degradation_shift", "contact_geometry_shift", "low_signal_morphology_stress", "combined_failure_stress")
STRESS_METHODS = (
    "per_morphology_calibrated_predictor",
    "constraint_aware_mpc",
    "conformal_risk_shield",
    "domain_randomized_policy_selector",
    "online_system_identification",
    "meta_adaptive_mpc",
    "bayesian_morphology_belief",
    "retrieval_failure_memory",
    "morphology_failure_transformer_prior",
    "risk_aware_intervention_policy",
    "failure_predictive_morphology_v4",
    "cost_calibrated_failure_predictive_morphology_v5",
)
FIXED_RISK_METHODS = (
    "cost_calibrated_failure_predictive_morphology_v5",
    "online_system_identification",
    "meta_adaptive_mpc",
    "conformal_risk_shield",
    "constraint_aware_mpc",
    "risk_aware_intervention_policy",
)
FIXED_RISK_BUDGETS = ("0.00", "0.05", "0.10", "0.15")


def clamp(value: np.ndarray | float, lo: float = 0.0, hi: float = 1.0) -> np.ndarray | float:
    return np.clip(value, lo, hi)


def ci95(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    return 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def rng_for(*tokens: int) -> np.random.Generator:
    value = BASE_SEED
    for idx, token in enumerate(tokens):
        value += (idx + 1) * 1_000_003 * (token + 17)
    return np.random.default_rng(value % (2**32 - 1))


def macro_f1(true_family: np.ndarray, predicted_family: np.ndarray) -> float:
    scores: List[float] = []
    for family_idx in range(len(FAMILIES)):
        tp = np.sum((true_family == family_idx) & (predicted_family == family_idx))
        fp = np.sum((true_family != family_idx) & (predicted_family == family_idx))
        fn = np.sum((true_family == family_idx) & (predicted_family != family_idx))
        denom = (2 * tp + fp + fn)
        if denom > 0:
            scores.append(float(2 * tp / denom))
    return float(statistics.mean(scores)) if scores else 0.0


def scenario_arrays(morph: Morphology, task: Task, split: Split, seed: int, morph_idx: int, task_idx: int, split_idx: int, episodes: int, namespace: int) -> Dict[str, np.ndarray]:
    rng = rng_for(namespace, seed, morph_idx, task_idx, split_idx)
    base = 0.42 * np.asarray(morph.risk) + 0.38 * np.asarray(task.risk) + 0.46 * np.asarray(split.risk_delta)
    base += 0.04 * task.precision + 0.04 * task.disturbance + 0.03 * task.contact_need + 0.03 * morph.fragility
    noise = rng.normal(0.0, 0.052 + 0.030 * split.stress, size=(episodes, len(FAMILIES)))
    risks = np.clip(base + noise, 0.01, 1.80)
    severity = np.max(risks, axis=1)
    true_family = np.argmax(risks, axis=1)
    second_family = np.argsort(risks, axis=1)[:, -2]
    ambiguity = np.clip(severity - np.take_along_axis(risks, second_family[:, None], axis=1).ravel(), 0.0, 1.0)
    return {
        "risks": risks,
        "severity": severity,
        "true_family": true_family,
        "second_family": second_family,
        "ambiguity": ambiguity,
        "payload_shift": np.full(episodes, split.payload_shift),
        "terrain_or_fluid_shift": np.full(episodes, split.terrain_or_fluid_shift),
        "actuator_degradation": np.full(episodes, split.actuator_degradation),
        "sensor_dropout": np.full(episodes, split.sensor_dropout),
        "contact_tightness": np.full(episodes, split.contact_tightness),
        "morphology_ood_shift": np.full(episodes, split.morphology_ood_shift + morph.morphology_ood * split.stress),
        "intervention_cost_shift": np.full(episodes, split.intervention_cost_shift),
    }


def choose_wrong_family(true_family: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    offsets = rng.integers(1, len(FAMILIES), size=true_family.shape[0])
    return (true_family + offsets) % len(FAMILIES)


def simulate_method(method: Method, morph: Morphology, task: Task, split: Split, scenario: Dict[str, np.ndarray], seed: int, method_idx: int, namespace: int) -> Dict[str, np.ndarray | float]:
    episodes = scenario["severity"].shape[0]
    rng = rng_for(namespace, seed, method_idx, len(method.name))
    severity = scenario["severity"]
    true_family = scenario["true_family"].astype(int)
    second_family = scenario["second_family"].astype(int)
    ambiguity = scenario["ambiguity"]
    shift = split.stress

    morphology_bonus = 0.16 * method.morphology_use * (0.70 + 0.25 * morph.observability)
    ood_penalty = 0.18 * scenario["morphology_ood_shift"] * (1.0 - method.morphology_use)
    stress_penalty = (0.15 + 0.10 * morph.adaptation_lag) * shift * (1.0 - method.stress_resilience)
    sensor_penalty = 0.13 * split.sensor_dropout * (1.0 - 0.45 * method.adaptivity)
    ambiguity_penalty = 0.075 * (1.0 - ambiguity)
    p_correct = clamp(method.pred_skill + morphology_bonus - ood_penalty - stress_penalty - sensor_penalty - ambiguity_penalty + rng.normal(0.0, 0.025, episodes), 0.02, 0.98)
    if method.is_oracle:
        p_correct = np.full(episodes, 0.988)

    correct = rng.random(episodes) < p_correct
    p_top2_only = clamp(method.top2_boost + 0.15 * method.morphology_use - 0.06 * shift + 0.04 * morph.observability, 0.02, 0.93)
    top2_extra = (~correct) & (rng.random(episodes) < p_top2_only)
    top2_recall = correct | top2_extra
    predicted_family = np.where(correct, true_family, np.where(top2_extra, second_family, choose_wrong_family(true_family, rng)))

    confidence = clamp(0.10 + 0.80 * method.calibration * p_correct + rng.normal(0.0, 0.055, episodes), 0.02, 0.98)
    warning = clamp(method.lead_time + 0.17 * correct.astype(float) + 0.08 * top2_extra.astype(float) + 0.10 * morph.observability - 0.18 * split.sensor_dropout - 0.12 * morph.adaptation_lag * (1.0 - method.adaptivity), 0.0, 1.0)
    generalization_gap = clamp(0.05 + 0.30 * shift * (1.0 - method.morphology_use) + 0.16 * morph.adaptation_lag * (1.0 - method.adaptivity) + 0.10 * split.actuator_degradation * (1.0 - method.stress_resilience), 0.0, 1.0)
    shift_detection = clamp(method.shift_detector * (0.25 + 0.75 * shift + 0.35 * scenario["morphology_ood_shift"]) - 0.08 * split.sensor_dropout + rng.normal(0.0, 0.025, episodes), 0.0, 1.0)

    base_failure = clamp(
        0.19
        + 0.30 * severity
        + 0.12 * task.nominal_difficulty
        + 0.10 * split.payload_shift
        + 0.12 * split.terrain_or_fluid_shift
        + 0.15 * split.actuator_degradation
        + 0.13 * split.sensor_dropout
        + 0.11 * split.contact_tightness
        + 0.09 * split.morphology_ood_shift
        + 0.07 * morph.fragility,
        0.03,
        0.97,
    )

    uncertainty = 1.0 - confidence
    intervention_probability = clamp(
        method.intervention_rate * (0.30 + 0.36 * severity + 0.24 * shift + 0.12 * method.conservative_bias)
        + 0.12 * uncertainty
        + 0.05 * task.precision,
        0.0,
        0.98,
    )
    if method.is_oracle:
        intervention_probability = clamp(0.25 + 0.20 * severity, 0.0, 0.78)
    intervened = rng.random(episodes) < intervention_probability

    targeted = correct.astype(float) * method.targeted_mitigation + top2_extra.astype(float) * (0.40 * method.targeted_mitigation)
    robust = method.robust_control * (0.44 + 0.24 * method.stress_resilience)
    safety = method.safety_control * (0.24 + 0.22 * method.conservative_bias)
    adaptive = method.adaptivity * (0.20 * split.actuator_degradation + 0.13 * split.terrain_or_fluid_shift + 0.10 * split.sensor_dropout + 0.10 * split.morphology_ood_shift)
    mitigation = intervened.astype(float) * (0.31 * targeted + 0.24 * robust + 0.18 * safety + adaptive)
    mitigation += (~intervened).astype(float) * (0.18 * robust + 0.05 * method.stress_resilience + 0.05 * method.adaptivity)
    if method.is_oracle:
        mitigation += 0.31

    intervention_cost = np.where(
        intervened,
        0.046
        * (1.0 + 0.54 * task.precision + 0.42 * morph.fragility + 0.38 * shift + 0.50 * split.intervention_cost_shift)
        * (1.25 - method.cost_control),
        0.0,
    )
    unnecessary = intervened & (base_failure < 0.48) & (~correct) & (method.conservative_bias + (1.0 - method.calibration) > 0.28)
    cost_penalty = 0.14 * intervention_cost + 0.08 * unnecessary.astype(float)
    late_penalty = 0.10 * np.maximum(0.35 - warning, 0.0)
    over_prediction_penalty = 0.05 * intervened.astype(float) * (~correct).astype(float) * (1.0 - method.cost_control)
    final_failure_probability = clamp(base_failure - mitigation + cost_penalty + late_penalty + over_prediction_penalty + rng.normal(0.0, 0.035, episodes), 0.01, 0.98)
    failed = rng.random(episodes) < final_failure_probability
    success = ~failed

    unmitigated_family = failed & (predicted_family != true_family)
    safety_probability = clamp(
        0.12 * failed.astype(float)
        + 0.17 * severity
        + 0.10 * morph.fragility
        + 0.08 * split.contact_tightness
        - 0.16 * method.safety_control
        - 0.07 * method.conservative_bias,
        0.0,
        0.92,
    )
    safety_violation = rng.random(episodes) < safety_probability
    planning_regret = clamp(
        0.46 * final_failure_probability
        + 0.15 * unmitigated_family.astype(float)
        + 0.14 * safety_violation.astype(float)
        + 0.11 * intervention_cost
        + 0.08 * generalization_gap
        - 0.08 * success.astype(float),
        0.0,
        1.0,
    )
    risk_score = clamp(
        0.42 * safety_probability
        + 0.34 * final_failure_probability
        + 0.16 * planning_regret
        + 0.12 * uncertainty
        - 0.20 * method.risk_screening
        - 0.06 * method.calibration,
        0.0,
        1.0,
    )
    robust_utility = clamp(
        success.astype(float)
        - 1.25 * safety_violation.astype(float)
        - 0.80 * unmitigated_family.astype(float)
        - 0.70 * planning_regret
        - 0.45 * intervention_cost
        - 0.20 * unnecessary.astype(float),
        -2.0,
        1.0,
    )

    return {
        "true_family": true_family,
        "predicted_family": predicted_family,
        "severity": severity,
        "correct": correct,
        "top2_recall": top2_recall,
        "confidence": confidence,
        "warning": warning,
        "generalization_gap": generalization_gap,
        "shift_detection": shift_detection,
        "success": success,
        "dominant_failure": unmitigated_family,
        "safety_violation": safety_violation,
        "intervention_cost": intervention_cost,
        "unnecessary": unnecessary,
        "planning_regret": planning_regret,
        "risk_score": risk_score,
        "robust_utility": robust_utility,
        "metrics": {
            "dominant_failure_accuracy": float(np.mean(correct)),
            "top2_failure_recall": float(np.mean(top2_recall)),
            "calibration_error": abs(float(np.mean(correct)) - float(np.mean(confidence))),
            "early_warning_lead_time": float(np.mean(warning)),
            "cross_morphology_generalization_gap": float(np.mean(generalization_gap)),
            "morphology_shift_detection": float(np.mean(shift_detection)),
            "failure_family_f1": macro_f1(true_family, predicted_family),
            "task_success": float(np.mean(success)),
            "dominant_failure_rate": float(np.mean(unmitigated_family)),
            "safety_violation_rate": float(np.mean(safety_violation)),
            "intervention_cost": float(np.mean(intervention_cost)),
            "unnecessary_intervention_rate": float(np.mean(unnecessary)),
            "planning_regret_to_oracle": float(np.mean(planning_regret)),
            "robust_utility": float(np.mean(robust_utility)),
        },
    }


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def aggregate_group_rows(rows: Sequence[Dict[str, object]], group_keys: Sequence[str], metrics: Iterable[str]) -> List[Dict[str, object]]:
    grouped: Dict[tuple, List[Dict[str, object]]] = {}
    for row in rows:
        key = tuple(str(row[k]) for k in group_keys)
        grouped.setdefault(key, []).append(row)
    output: List[Dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        out: Dict[str, object] = {k: v for k, v in zip(group_keys, key)}
        for metric in metrics:
            out[metric] = statistics.mean(float(row[metric]) for row in group)
        output.append(out)
    return output


def metric_long(seed_rows: Sequence[Dict[str, object]], group_keys: Sequence[str]) -> List[Dict[str, object]]:
    grouped: Dict[tuple, List[Dict[str, object]]] = {}
    for row in seed_rows:
        key = tuple(str(row[k]) for k in group_keys)
        grouped.setdefault(key, []).append(row)
    output: List[Dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        base = {k: v for k, v in zip(group_keys, key)}
        for metric in METRICS:
            values = [float(row[metric]) for row in group]
            out = dict(base)
            out.update({"metric": metric, "mean": statistics.mean(values), "ci95": ci95(values), "n": len(values)})
            output.append(out)
    return output


def lookup_metric(rows: Sequence[Dict[str, object]], keys: Sequence[str]) -> Dict[tuple, Dict[str, object]]:
    return {tuple(str(row[k]) for k in keys) + (str(row["metric"]),): row for row in rows}


def paired_stats(seed_rows: Sequence[Dict[str, object]], group_key: str | None, comparisons: Sequence[str]) -> List[Dict[str, object]]:
    output: List[Dict[str, object]] = []
    baselines = [m.name for m in METHODS if not m.is_oracle and m.name != V5.name]
    if comparisons:
        baselines = list(comparisons)
    groups = sorted({str(row[group_key]) for row in seed_rows}) if group_key else [""]
    for group in groups:
        for baseline in baselines:
            for metric in METRICS:
                diffs = []
                for seed in SEEDS:
                    if group_key:
                        v5_rows = [row for row in seed_rows if str(row["method"]) == V5.name and int(row["seed"]) == seed and str(row[group_key]) == group]
                        b_rows = [row for row in seed_rows if str(row["method"]) == baseline and int(row["seed"]) == seed and str(row[group_key]) == group]
                    else:
                        v5_rows = [row for row in seed_rows if str(row["method"]) == V5.name and int(row["seed"]) == seed]
                        b_rows = [row for row in seed_rows if str(row["method"]) == baseline and int(row["seed"]) == seed]
                    if v5_rows and b_rows:
                        diffs.append(float(v5_rows[0][metric]) - float(b_rows[0][metric]))
                if diffs:
                    row: Dict[str, object] = {
                        "comparison": f"{V5.name}_minus_{baseline}",
                        "metric": metric,
                        "mean": statistics.mean(diffs),
                        "ci95": ci95(diffs),
                        "lower95": statistics.mean(diffs) - ci95(diffs),
                        "upper95": statistics.mean(diffs) + ci95(diffs),
                        "better_seeds": sum(1 for d in diffs if d > 0),
                        "n": len(diffs),
                    }
                    if group_key:
                        row[group_key] = group
                    output.append(row)
    return output


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def run_main() -> List[Dict[str, object]]:
    group_rows: List[Dict[str, object]] = []
    rollout_fields = [
        "seed",
        "morphology",
        "task",
        "split",
        "episode",
        "method",
        "true_family",
        "predicted_family",
        "severity",
        "correct",
        "top2_recall",
        "confidence",
        "warning",
        "task_success",
        "dominant_failure",
        "safety_violation",
        "intervention_cost",
        "unnecessary_intervention",
        "planning_regret_to_oracle",
        "risk_score",
        "robust_utility",
    ]
    dataset_fields = [
        "seed",
        "morphology",
        "task",
        "split",
        "episode",
        "payload_shift",
        "terrain_or_fluid_shift",
        "actuator_degradation",
        "sensor_dropout",
        "contact_tightness",
        "morphology_ood_shift",
        "intervention_cost_shift",
        "severity",
        "true_family",
    ]
    with (RESULTS / "rollouts.csv").open("w", newline="", encoding="utf-8") as rollout_handle, (RESULTS / "dataset_summary.csv").open("w", newline="", encoding="utf-8") as dataset_handle:
        rollout_writer = csv.DictWriter(rollout_handle, fieldnames=rollout_fields)
        dataset_writer = csv.DictWriter(dataset_handle, fieldnames=dataset_fields)
        rollout_writer.writeheader()
        dataset_writer.writeheader()
        for seed in SEEDS:
            for split_idx, split in enumerate(SPLITS):
                for morph_idx, morph in enumerate(MORPHOLOGIES):
                    for task_idx, task in enumerate(TASKS):
                        scenario = scenario_arrays(morph, task, split, seed, morph_idx, task_idx, split_idx, EPISODES_PER_CELL, 10)
                        for episode in range(EPISODES_PER_CELL):
                            dataset_writer.writerow(
                                {
                                    "seed": seed,
                                    "morphology": morph.name,
                                    "task": task.name,
                                    "split": split.name,
                                    "episode": episode,
                                    "payload_shift": f"{scenario['payload_shift'][episode]:.6f}",
                                    "terrain_or_fluid_shift": f"{scenario['terrain_or_fluid_shift'][episode]:.6f}",
                                    "actuator_degradation": f"{scenario['actuator_degradation'][episode]:.6f}",
                                    "sensor_dropout": f"{scenario['sensor_dropout'][episode]:.6f}",
                                    "contact_tightness": f"{scenario['contact_tightness'][episode]:.6f}",
                                    "morphology_ood_shift": f"{scenario['morphology_ood_shift'][episode]:.6f}",
                                    "intervention_cost_shift": f"{scenario['intervention_cost_shift'][episode]:.6f}",
                                    "severity": f"{scenario['severity'][episode]:.6f}",
                                    "true_family": FAMILIES[int(scenario["true_family"][episode])],
                                }
                            )
                        for method_idx, method in enumerate(METHODS):
                            result = simulate_method(method, morph, task, split, scenario, seed, method_idx, 20)
                            metrics = result["metrics"]
                            group_row: Dict[str, object] = {
                                "seed": seed,
                                "split": split.name,
                                "morphology": morph.name,
                                "task": task.name,
                                "method": method.name,
                                "episodes": EPISODES_PER_CELL,
                            }
                            group_row.update(metrics)
                            group_rows.append(group_row)
                            for episode in range(EPISODES_PER_CELL):
                                rollout_writer.writerow(
                                    {
                                        "seed": seed,
                                        "morphology": morph.name,
                                        "task": task.name,
                                        "split": split.name,
                                        "episode": episode,
                                        "method": method.name,
                                        "true_family": FAMILIES[int(result["true_family"][episode])],
                                        "predicted_family": FAMILIES[int(result["predicted_family"][episode])],
                                        "severity": f"{float(result['severity'][episode]):.6f}",
                                        "correct": int(bool(result["correct"][episode])),
                                        "top2_recall": int(bool(result["top2_recall"][episode])),
                                        "confidence": f"{float(result['confidence'][episode]):.6f}",
                                        "warning": f"{float(result['warning'][episode]):.6f}",
                                        "task_success": int(bool(result["success"][episode])),
                                        "dominant_failure": int(bool(result["dominant_failure"][episode])),
                                        "safety_violation": int(bool(result["safety_violation"][episode])),
                                        "intervention_cost": f"{float(result['intervention_cost'][episode]):.6f}",
                                        "unnecessary_intervention": int(bool(result["unnecessary"][episode])),
                                        "planning_regret_to_oracle": f"{float(result['planning_regret'][episode]):.6f}",
                                        "risk_score": f"{float(result['risk_score'][episode]):.6f}",
                                        "robust_utility": f"{float(result['robust_utility'][episode]):.6f}",
                                    }
                                )
    return group_rows


def run_ablation() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    raw_fields = ["seed", "split", "morphology", "task", "episode", "ablation"] + list(METRICS)
    with (RESULTS / "ablation_rollouts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fields)
        writer.writeheader()
        for seed in SEEDS:
            for split_name in ABLATION_SPLITS:
                split_idx = [s.name for s in SPLITS].index(split_name)
                split = SPLITS[split_idx]
                for morph_idx, morph in enumerate(MORPHOLOGIES):
                    for task_idx, task in enumerate(TASKS):
                        scenario = scenario_arrays(morph, task, split, seed, morph_idx, task_idx, split_idx, EPISODES_PER_CELL, 30)
                        for method_idx, method in enumerate(ABLATIONS):
                            result = simulate_method(method, morph, task, split, scenario, seed, method_idx, 40)
                            metrics = result["metrics"]
                            group_row = {"seed": seed, "split": split.name, "morphology": morph.name, "task": task.name, "ablation": method.name, "episodes": EPISODES_PER_CELL}
                            group_row.update(metrics)
                            rows.append(group_row)
                            for episode in range(EPISODES_PER_CELL):
                                writer.writerow(
                                    {
                                        "seed": seed,
                                        "split": split.name,
                                        "morphology": morph.name,
                                        "task": task.name,
                                        "episode": episode,
                                        "ablation": method.name,
                                        **{metric: f"{metrics[metric]:.6f}" for metric in METRICS},
                                    }
                                )
    return rows


def split_from_stress(level: float) -> Split:
    return Split(
        f"stress_{level:.1f}",
        tuple(v * level for v in (0.18, 0.27, 0.30, 0.36, 0.28, 0.34, 0.30)),
        0.34 * level,
        0.38 * level,
        0.40 * level,
        0.34 * level,
        0.34 * level,
        0.48 * level,
        0.20 * level,
        0.74 * level,
    )


def run_stress() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    methods = [METHOD_BY_NAME[name] for name in STRESS_METHODS]
    raw_fields = ["seed", "stress_level", "morphology", "task", "episode", "method"] + list(METRICS)
    with (RESULTS / "stress_sweep_raw.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fields)
        writer.writeheader()
        for level_idx, level in enumerate((0.0, 0.2, 0.4, 0.6, 0.8, 1.0)):
            split = split_from_stress(level)
            for seed in SEEDS:
                for morph_idx, morph in enumerate(MORPHOLOGIES):
                    for task_idx, task in enumerate(TASKS):
                        scenario = scenario_arrays(morph, task, split, seed, morph_idx, task_idx, level_idx, STRESS_EPISODES_PER_CELL, 50)
                        for method_idx, method in enumerate(methods):
                            result = simulate_method(method, morph, task, split, scenario, seed, method_idx, 60)
                            metrics = result["metrics"]
                            group_row = {"seed": seed, "stress_level": f"{level:.1f}", "morphology": morph.name, "task": task.name, "method": method.name, "episodes": STRESS_EPISODES_PER_CELL}
                            group_row.update(metrics)
                            rows.append(group_row)
                            for episode in range(STRESS_EPISODES_PER_CELL):
                                writer.writerow(
                                    {
                                        "seed": seed,
                                        "stress_level": f"{level:.1f}",
                                        "morphology": morph.name,
                                        "task": task.name,
                                        "episode": episode,
                                        "method": method.name,
                                        **{metric: f"{metrics[metric]:.6f}" for metric in METRICS},
                                    }
                                )
    return rows


def run_fixed_risk() -> List[Dict[str, object]]:
    raw_rows: List[Dict[str, object]] = []
    methods = [METHOD_BY_NAME[name] for name in FIXED_RISK_METHODS]
    for split_name in HARD_SPLITS:
        split_idx = [s.name for s in SPLITS].index(split_name)
        split = SPLITS[split_idx]
        for budget in FIXED_RISK_BUDGETS:
            budget_value = float(budget)
            for seed in SEEDS:
                for morph_idx, morph in enumerate(MORPHOLOGIES):
                    for task_idx, task in enumerate(TASKS):
                        scenario = scenario_arrays(morph, task, split, seed, morph_idx, task_idx, split_idx, EPISODES_PER_CELL, 70)
                        for method_idx, method in enumerate(methods):
                            result = simulate_method(method, morph, task, split, scenario, seed, method_idx, 80)
                            for episode in range(EPISODES_PER_CELL):
                                accepted = float(result["risk_score"][episode]) <= budget_value
                                raw_rows.append(
                                    {
                                        "split": split.name,
                                        "budget": budget,
                                        "method": method.name,
                                        "seed": seed,
                                        "morphology": morph.name,
                                        "task": task.name,
                                        "episode": episode,
                                        "accepted": int(accepted),
                                        "task_success": int(bool(result["success"][episode])),
                                        "safety_violation_rate": int(bool(result["safety_violation"][episode])),
                                        "planning_regret_to_oracle": f"{float(result['planning_regret'][episode]):.6f}",
                                        "robust_utility": f"{float(result['robust_utility'][episode]):.6f}",
                                        "intervention_cost": f"{float(result['intervention_cost'][episode]):.6f}",
                                    }
                                )
    write_csv(RESULTS / "fixed_risk_raw.csv", raw_rows)
    return raw_rows


def fixed_risk_seed_metrics(raw_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[tuple, List[Dict[str, object]]] = {}
    for row in raw_rows:
        key = (row["split"], row["budget"], row["method"], str(row["seed"]))
        grouped.setdefault(key, []).append(row)
    output: List[Dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        accepted = [row for row in group if int(row["accepted"]) == 1]
        coverage = len(accepted) / len(group)
        def accepted_mean(field: str) -> float:
            if not accepted:
                return 0.0
            return statistics.mean(float(row[field]) for row in accepted)
        output.append(
            {
                "split": key[0],
                "budget": key[1],
                "method": key[2],
                "seed": key[3],
                "coverage": coverage,
                "accepted_success": accepted_mean("task_success"),
                "accepted_safety_violation": accepted_mean("safety_violation_rate"),
                "accepted_regret": accepted_mean("planning_regret_to_oracle"),
                "accepted_utility": accepted_mean("robust_utility"),
                "accepted_cost": accepted_mean("intervention_cost"),
            }
        )
    return output


def fixed_risk_metric_long(seed_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    metrics = ("coverage", "accepted_success", "accepted_safety_violation", "accepted_regret", "accepted_utility", "accepted_cost")
    grouped: Dict[tuple, List[Dict[str, object]]] = {}
    for row in seed_rows:
        key = (row["split"], row["budget"], row["method"])
        grouped.setdefault(key, []).append(row)
    output: List[Dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        for metric in metrics:
            values = [float(row[metric]) for row in group]
            output.append({"split": key[0], "budget": key[1], "method": key[2], "metric": metric, "mean": statistics.mean(values), "ci95": ci95(values), "n": len(values)})
    return output


def fixed_risk_pairwise(seed_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    metrics = ("coverage", "accepted_success", "accepted_safety_violation", "accepted_regret", "accepted_utility", "accepted_cost")
    baselines = [m for m in FIXED_RISK_METHODS if m != V5.name]
    output: List[Dict[str, object]] = []
    for split in HARD_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            for baseline in baselines:
                for metric in metrics:
                    diffs = []
                    for seed in SEEDS:
                        v5_row = next(row for row in seed_rows if row["split"] == split and row["budget"] == budget and row["method"] == V5.name and int(row["seed"]) == seed)
                        b_row = next(row for row in seed_rows if row["split"] == split and row["budget"] == budget and row["method"] == baseline and int(row["seed"]) == seed)
                        diffs.append(float(v5_row[metric]) - float(b_row[metric]))
                    output.append({"split": split, "budget": budget, "comparison": f"{V5.name}_minus_{baseline}", "metric": metric, "mean": statistics.mean(diffs), "ci95": ci95(diffs), "lower95": statistics.mean(diffs) - ci95(diffs), "upper95": statistics.mean(diffs) + ci95(diffs), "n": len(diffs)})
    return output


def negative_cases(raw_path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with raw_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        candidates = [
            row
            for row in reader
            if row["method"] == V5.name
            and row["split"] in HARD_SPLITS
            and (row["task_success"] == "0" or row["safety_violation"] == "1")
        ]
    candidates = sorted(candidates, key=lambda row: (float(row["robust_utility"]), -float(row["planning_regret_to_oracle"])))[:24]
    for idx, row in enumerate(candidates, start=1):
        rows.append(
            {
                "case_id": idx,
                "seed": row["seed"],
                "morphology": row["morphology"],
                "task": row["task"],
                "split": row["split"],
                "episode": row["episode"],
                "predicted_family": row["predicted_family"],
                "true_family": row["true_family"],
                "success": row["task_success"],
                "safety_violation": row["safety_violation"],
                "regret": row["planning_regret_to_oracle"],
                "utility": row["robust_utility"],
                "failure_mode": "wrong_family" if row["predicted_family"] != row["true_family"] else "cost_or_control_failure",
            }
        )
    return rows


def decide(metrics: Sequence[Dict[str, object]], hard_metrics: Sequence[Dict[str, object]], hard_pairwise: Sequence[Dict[str, object]], ablation_metrics: Sequence[Dict[str, object]], stress_metrics: Sequence[Dict[str, object]], fixed_metrics: Sequence[Dict[str, object]]) -> Dict[str, object]:
    hard = lookup_metric(hard_metrics, ["method"])
    all_non_oracle = [m.name for m in METHODS if not m.is_oracle and m.name != V5.name]
    best_success_ref = max(all_non_oracle, key=lambda m: float(hard[(m, "task_success")]["mean"]))
    best_accuracy_ref = max(all_non_oracle, key=lambda m: float(hard[(m, "dominant_failure_accuracy")]["mean"]))
    best_utility_ref = max(all_non_oracle, key=lambda m: float(hard[(m, "robust_utility")]["mean"]))
    best_safety_ref = min(all_non_oracle, key=lambda m: float(hard[(m, "safety_violation_rate")]["mean"]))
    best_regret_ref = min(all_non_oracle, key=lambda m: float(hard[(m, "planning_regret_to_oracle")]["mean"]))
    pair_lookup = {(row["comparison"], row["metric"]): row for row in hard_pairwise}
    success_comp = pair_lookup[(f"{V5.name}_minus_{best_success_ref}", "task_success")]
    utility_comp = pair_lookup[(f"{V5.name}_minus_{best_utility_ref}", "robust_utility")]
    regret_comp = pair_lookup[(f"{V5.name}_minus_{best_regret_ref}", "planning_regret_to_oracle")]
    safety_comp = pair_lookup[(f"{V5.name}_minus_{best_safety_ref}", "safety_violation_rate")]

    abl = lookup_metric(ablation_metrics, ["ablation"])
    full = "full_cost_calibrated_failure_predictive_morphology_v5"
    best_ablation = max([a.name for a in ABLATIONS], key=lambda name: float(abl[(name, "robust_utility")]["mean"]))
    stress_lookup = lookup_metric(stress_metrics, ["stress_level", "method"])
    stress_methods = [m for m in STRESS_METHODS if m != V5.name]
    max_stress_ref = max(stress_methods, key=lambda m: float(stress_lookup[("1.0", m, "robust_utility")]["mean"]))
    fixed_lookup = lookup_metric(fixed_metrics, ["split", "budget", "method"])
    fixed_coverages = [float(fixed_lookup[(split, "0.05", V5.name, "coverage")]["mean"]) for split in HARD_SPLITS]

    gates = {
        "success_gate": float(success_comp["lower95"]) > 0.0,
        "prediction_gate": float(hard[(V5.name, "dominant_failure_accuracy")]["mean"]) >= float(hard[(best_accuracy_ref, "dominant_failure_accuracy")]["mean"]),
        "safety_gate": float(safety_comp["upper95"]) <= 0.0,
        "regret_gate": float(regret_comp["upper95"]) <= 0.0,
        "utility_gate": float(utility_comp["lower95"]) > 0.0,
        "ablation_gate": best_ablation == full,
        "stress_gate": float(stress_lookup[("1.0", V5.name, "robust_utility")]["mean"]) >= float(stress_lookup[("1.0", max_stress_ref, "robust_utility")]["mean"]),
        "fixed_risk_gate": all(cov > 0.05 for cov in fixed_coverages),
        "scope_gate": False,
    }
    terminal = "STRONG_REVISE" if all(gates.values()) else "KILL_ARCHIVE"
    return {
        "terminal": terminal,
        "best_success_reference": best_success_ref,
        "best_accuracy_reference": best_accuracy_ref,
        "best_safety_reference": best_safety_ref,
        "best_regret_reference": best_regret_ref,
        "best_utility_reference": best_utility_ref,
        "best_ablation": best_ablation,
        "max_stress_reference": max_stress_ref,
        "v5_success": float(hard[(V5.name, "task_success")]["mean"]),
        "best_success": float(hard[(best_success_ref, "task_success")]["mean"]),
        "v5_accuracy": float(hard[(V5.name, "dominant_failure_accuracy")]["mean"]),
        "best_accuracy": float(hard[(best_accuracy_ref, "dominant_failure_accuracy")]["mean"]),
        "v5_safety": float(hard[(V5.name, "safety_violation_rate")]["mean"]),
        "best_safety": float(hard[(best_safety_ref, "safety_violation_rate")]["mean"]),
        "v5_regret": float(hard[(V5.name, "planning_regret_to_oracle")]["mean"]),
        "best_regret": float(hard[(best_regret_ref, "planning_regret_to_oracle")]["mean"]),
        "v5_utility": float(hard[(V5.name, "robust_utility")]["mean"]),
        "best_utility": float(hard[(best_utility_ref, "robust_utility")]["mean"]),
        "fixed_risk_coverages": fixed_coverages,
        **gates,
    }


def plot_outputs(metrics: Sequence[Dict[str, object]], hard_metrics: Sequence[Dict[str, object]], ablation_metrics: Sequence[Dict[str, object]], stress_metrics: Sequence[Dict[str, object]], fixed_metrics: Sequence[Dict[str, object]]) -> None:
    hard = lookup_metric(hard_metrics, ["method"])
    methods = [m.name for m in METHODS if not m.is_oracle]
    labels = [m.replace("_", "\n") for m in methods]
    x = np.arange(len(methods))

    plt.figure(figsize=(14, 5))
    plt.bar(x - 0.18, [float(hard[(m, "task_success")]["mean"]) for m in methods], 0.36, label="Task success")
    plt.bar(x + 0.18, [float(hard[(m, "planning_regret_to_oracle")]["mean"]) for m in methods], 0.36, label="Regret")
    plt.xticks(x, labels, rotation=35, ha="right", fontsize=7)
    plt.ylim(0, 1)
    plt.title("Hard aggregate success and regret")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_hard_success_regret_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(14, 5))
    plt.bar(x - 0.25, [float(hard[(m, "dominant_failure_accuracy")]["mean"]) for m in methods], 0.25, label="Accuracy")
    plt.bar(x, [float(hard[(m, "top2_failure_recall")]["mean"]) for m in methods], 0.25, label="Top-2 recall")
    plt.bar(x + 0.25, [float(hard[(m, "failure_family_f1")]["mean"]) for m in methods], 0.25, label="F1")
    plt.xticks(x, labels, rotation=35, ha="right", fontsize=7)
    plt.ylim(0, 1)
    plt.title("Failure prediction metrics")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_prediction_metrics_v5.png", dpi=180)
    plt.close()

    abl = lookup_metric(ablation_metrics, ["ablation"])
    abl_names = [a.name for a in ABLATIONS]
    x = np.arange(len(abl_names))
    plt.figure(figsize=(12, 5))
    plt.bar(x - 0.18, [float(abl[(m, "task_success")]["mean"]) for m in abl_names], 0.36, label="Success")
    plt.bar(x + 0.18, [float(abl[(m, "robust_utility")]["mean"]) for m in abl_names], 0.36, label="Utility")
    plt.xticks(x, [m.replace("_", "\n") for m in abl_names], rotation=30, ha="right", fontsize=7)
    plt.title("Ablation deployment outcomes")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_ablation_v5.png", dpi=180)
    plt.close()

    stress_lookup = lookup_metric(stress_metrics, ["stress_level", "method"])
    plt.figure(figsize=(10, 5))
    for method in STRESS_METHODS:
        levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        plt.plot(levels, [float(stress_lookup[(f"{level:.1f}", method, "task_success")]["mean"]) for level in levels], marker="o", label=method.replace("_", " "))
    plt.xlabel("Stress level")
    plt.ylabel("Task success")
    plt.ylim(0, 1)
    plt.title("Stress sweep")
    plt.legend(fontsize=6, ncol=2)
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_stress_sweep_v5.png", dpi=180)
    plt.close()

    fixed_lookup = lookup_metric(fixed_metrics, ["split", "budget", "method"])
    plt.figure(figsize=(10, 5))
    budgets = [float(b) for b in FIXED_RISK_BUDGETS]
    for method in FIXED_RISK_METHODS:
        values = [statistics.mean(float(fixed_lookup[(split, f"{b:.2f}", method, "coverage")]["mean"]) for split in HARD_SPLITS) for b in budgets]
        plt.plot(budgets, values, marker="o", label=method.replace("_", " "))
    plt.xlabel("Risk budget")
    plt.ylabel("Coverage")
    plt.ylim(0, 1)
    plt.title("Fixed-risk coverage")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_fixed_risk_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    for method in methods:
        plt.scatter(float(hard[(method, "safety_violation_rate")]["mean"]), float(hard[(method, "task_success")]["mean"]), s=70)
        plt.text(float(hard[(method, "safety_violation_rate")]["mean"]) + 0.002, float(hard[(method, "task_success")]["mean"]), method.replace("_", " "), fontsize=7)
    plt.xlabel("Safety violation")
    plt.ylabel("Task success")
    plt.title("Safety-success frontier")
    plt.tight_layout()
    plt.savefig(FIGURES / "morphology_pareto_v5.png", dpi=180)
    plt.close()


def write_summary(decision: Dict[str, object], counts: Dict[str, int]) -> None:
    lines = [
        "Paper 95 failure_predictive_morphology v5 expanded audit",
        f"Terminal recommendation: {decision['terminal']}",
        "ICLR main ready: no",
        "Reason: expanded CPU-only morphology-failure audit tests whether prediction accuracy converts into closed-loop deployment gains; v5 improves over v4 and has strong prediction metrics, but it remains non-submittable if adaptive/control baselines win deployment gates.",
    ]
    for key, value in counts.items():
        lines.append(f"{key}: {value}")
    lines.extend(
        [
            "",
            "Frozen hard-aggregate gate:",
            f"best_success_reference={decision['best_success_reference']}",
            f"best_accuracy_reference={decision['best_accuracy_reference']}",
            f"best_safety_reference={decision['best_safety_reference']}",
            f"best_regret_reference={decision['best_regret_reference']}",
            f"best_utility_reference={decision['best_utility_reference']}",
            f"best_ablation={decision['best_ablation']}",
            f"max_stress_reference={decision['max_stress_reference']}",
            f"v5_success={decision['v5_success']:.5f}",
            f"best_success={decision['best_success']:.5f}",
            f"v5_accuracy={decision['v5_accuracy']:.5f}",
            f"best_accuracy={decision['best_accuracy']:.5f}",
            f"v5_safety={decision['v5_safety']:.5f}",
            f"best_safety={decision['best_safety']:.5f}",
            f"v5_regret={decision['v5_regret']:.5f}",
            f"best_regret={decision['best_regret']:.5f}",
            f"v5_utility={decision['v5_utility']:.5f}",
            f"best_utility={decision['best_utility']:.5f}",
        ]
    )
    for gate in ("success_gate", "prediction_gate", "safety_gate", "regret_gate", "utility_gate", "ablation_gate", "stress_gate", "fixed_risk_gate", "scope_gate"):
        lines.append(f"{gate}={decision[gate]}")
    for split, coverage in zip(HARD_SPLITS, decision["fixed_risk_coverages"]):
        lines.append(f"{split}: v5_coverage={coverage:.5f}")
    lines.append("terminal=" + decision["terminal"])
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    group_rows = run_main()
    raw_seed_metrics = aggregate_group_rows(group_rows, ["seed", "split", "method"], METRICS)
    write_csv(RESULTS / "raw_seed_metrics.csv", raw_seed_metrics)
    metrics = metric_long(raw_seed_metrics, ["split", "method"])
    write_csv(RESULTS / "metrics.csv", metrics)
    group_metrics = aggregate_group_rows(group_rows, ["split", "morphology", "task", "method"], METRICS)
    write_csv(RESULTS / "per_morph_task_metrics.csv", group_metrics)
    pairwise = paired_stats(raw_seed_metrics, "split", [])
    write_csv(RESULTS / "pairwise_stats.csv", pairwise)

    hard_group_rows = [row for row in group_rows if row["split"] in HARD_SPLITS]
    hard_seed = aggregate_group_rows(hard_group_rows, ["seed", "method"], METRICS)
    write_csv(RESULTS / "hard_aggregate_seed_metrics.csv", hard_seed)
    hard_metrics = metric_long(hard_seed, ["method"])
    write_csv(RESULTS / "hard_aggregate_metrics.csv", hard_metrics)
    hard_pairwise = paired_stats(hard_seed, None, [])
    write_csv(RESULTS / "hard_aggregate_pairwise_stats.csv", hard_pairwise)

    ablation_rows = run_ablation()
    ablation_seed = aggregate_group_rows(ablation_rows, ["seed", "ablation"], METRICS)
    write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_seed)
    ablation_metrics = metric_long(ablation_seed, ["ablation"])
    write_csv(RESULTS / "ablation_metrics.csv", ablation_metrics)
    write_csv(RESULTS / "ablation_metric_long.csv", ablation_metrics)

    stress_rows = run_stress()
    stress_seed = aggregate_group_rows(stress_rows, ["seed", "stress_level", "method"], METRICS)
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", stress_seed)
    stress_metrics = metric_long(stress_seed, ["stress_level", "method"])
    write_csv(RESULTS / "stress_sweep.csv", stress_metrics)
    write_csv(RESULTS / "stress_sweep_metric_long.csv", stress_metrics)

    fixed_raw = run_fixed_risk()
    fixed_seed = fixed_risk_seed_metrics(fixed_raw)
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed)
    fixed_metrics = fixed_risk_metric_long(fixed_seed)
    write_csv(RESULTS / "fixed_risk_metrics.csv", fixed_metrics)
    fixed_pair = fixed_risk_pairwise(fixed_seed)
    write_csv(RESULTS / "fixed_risk_pairwise.csv", fixed_pair)

    negatives = negative_cases(RESULTS / "rollouts.csv")
    write_csv(RESULTS / "negative_cases.csv", negatives)

    decision = decide(metrics, hard_metrics, hard_pairwise, ablation_metrics, stress_metrics, fixed_metrics)
    plot_outputs(metrics, hard_metrics, ablation_metrics, stress_metrics, fixed_metrics)
    counts = {
        "Main rollout rows": row_count(RESULTS / "rollouts.csv"),
        "Dataset summary rows": row_count(RESULTS / "dataset_summary.csv"),
        "Main seed-metric rows": len(raw_seed_metrics),
        "Main metric rows": len(metrics),
        "Main pairwise rows": len(pairwise),
        "Hard aggregate seed rows": len(hard_seed),
        "Hard aggregate metric rows": len(hard_metrics),
        "Hard aggregate pairwise rows": len(hard_pairwise),
        "Ablation rollout rows": row_count(RESULTS / "ablation_rollouts.csv"),
        "Ablation seed rows": len(ablation_seed),
        "Ablation metric rows": len(ablation_metrics),
        "Stress raw rows": row_count(RESULTS / "stress_sweep_raw.csv"),
        "Stress seed rows": len(stress_seed),
        "Stress metric rows": len(stress_metrics),
        "Fixed-risk raw rows": len(fixed_raw),
        "Fixed-risk seed rows": len(fixed_seed),
        "Fixed-risk metric rows": len(fixed_metrics),
        "Fixed-risk pairwise rows": len(fixed_pair),
        "Negative cases": len(negatives),
    }
    write_summary(decision, counts)
    print(f"Paper 95 v5 expanded audit complete: {decision['terminal']}")
    print(RESULTS / "summary.txt")


if __name__ == "__main__":
    main()
