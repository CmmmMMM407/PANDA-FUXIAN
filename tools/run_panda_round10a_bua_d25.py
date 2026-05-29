#!/usr/bin/env python3
"""Round10-A BUA-PANDA D2.5 offline allocator simulation.

This is a train/val-only diagnostic. It consumes existing Round9-A branch
counterfactual utility exports and checks whether BUA branch-aux allocation is
cleanly separated from uniform, confidence-only, shuffled, random, reverse, and
boundary-only controls. It never reads test artifacts and performs no training.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EPS = 1e-8
BRANCHES = ("text", "image", "fusion")
WEAK_DOMAINS = {
    "weibo21": ["灾难事故", "科技", "医药健康"],
    "weibo": ["国际", "经济", "教育"],
}
RISK_COMPONENTS = (
    "confidence_uncertainty",
    "branch_disagreement",
    "fusion_uncertainty",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="weibo21", choices=["weibo21", "weibo"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--input-dir", default="repro_logs/round9_cue_d2/seed42")
    parser.add_argument("--output-dir", default="repro_logs/round10_bua_d25/seed42")
    parser.add_argument("--alpha-max", type=float, default=0.5)
    parser.add_argument("--low-margin-quantile", type=float, default=0.25)
    parser.add_argument("--risk-quantile", type=float, default=0.75)
    parser.add_argument("--min-utility-delta", type=float, default=0.02)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean_json(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(clean_json(payload), indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_rows(scores: np.ndarray) -> np.ndarray:
    arr = np.clip(np.asarray(scores, dtype=float), 0.0, None)
    denom = arr.sum(axis=1, keepdims=True)
    out = np.divide(arr, np.clip(denom, EPS, None))
    zero = denom.reshape(-1) < EPS
    if zero.any():
        out[zero] = 1.0 / len(BRANCHES)
    return out


def entropy(q: np.ndarray, *, normalized: bool = False) -> np.ndarray:
    arr = np.clip(np.asarray(q, dtype=float), EPS, 1.0)
    value = -np.sum(arr * np.log(arr), axis=1)
    if normalized:
        value = value / math.log(arr.shape[1])
    return value


def minmax_fit(values: np.ndarray) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    return float(np.nanmin(arr)), float(np.nanmax(arr))


def minmax_apply(values: np.ndarray, lo: float, hi: float) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return np.clip((arr - lo) / max(hi - lo, EPS), 0.0, 1.0)


def rank_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    labels = np.asarray(y, dtype=int)
    values = np.asarray(score, dtype=float)
    mask = np.isfinite(values)
    labels = labels[mask]
    values = values[mask]
    pos = labels == 1
    neg = labels == 0
    n_pos = int(pos.sum())
    n_neg = int(neg.sum())
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(values) + 1, dtype=float)
    sorted_values = values[order]
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and sorted_values[end] == sorted_values[start]:
            end += 1
        if end - start > 1:
            ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    rank_sum_pos = float(ranks[pos].sum())
    return float((rank_sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def corr(a: np.ndarray, b: np.ndarray) -> float | None:
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2 or np.nanstd(x[mask]) < EPS or np.nanstd(y[mask]) < EPS:
        return None
    return float(np.corrcoef(x[mask], y[mask])[0, 1])


def safe_mean(values: np.ndarray, mask: np.ndarray | None = None) -> float | None:
    arr = np.asarray(values, dtype=float)
    if mask is not None:
        arr = arr[np.asarray(mask, dtype=bool)]
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return None
    return float(np.mean(arr))


def load_utility(input_dir: Path) -> dict[str, pd.DataFrame]:
    if any("test" in path.name.lower() for path in input_dir.glob("*")):
        raise RuntimeError(f"Round10-A refuses test artifacts in {input_dir}")
    paths = {
        "train": input_dir / "branch_utility_train.csv",
        "val_diagnostic": input_dir / "branch_utility_val_diagnostic.csv",
    }
    outputs = {}
    for split, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path)
        required = {
            "sample_id",
            "split",
            "category_name",
            "y_true",
            "y_pred",
            "final_margin_abs",
            "confidence_uncertainty",
            "branch_disagreement",
            "fusion_uncertainty",
            "p_text",
            "p_image",
            "p_fusion",
            "u_text",
            "u_image",
            "u_fusion",
            "q_target_text",
            "q_target_image",
            "q_target_fusion",
            "utility_entropy",
        }
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        outputs[split] = df
    return outputs


def add_boundary_features(
    train: pd.DataFrame,
    val: pd.DataFrame,
    *,
    low_margin_quantile: float,
    risk_quantile: float,
) -> dict:
    low_margin_threshold = float(train["final_margin_abs"].quantile(low_margin_quantile))
    margin_params = minmax_fit(-train["final_margin_abs"].to_numpy(dtype=float))
    component_params = {
        name: minmax_fit(train[name].to_numpy(dtype=float))
        for name in RISK_COMPONENTS
    }

    def apply(df: pd.DataFrame) -> None:
        risk = minmax_apply(-df["final_margin_abs"].to_numpy(dtype=float), *margin_params)
        for name in RISK_COMPONENTS:
            risk += minmax_apply(df[name].to_numpy(dtype=float), *component_params[name])
        risk = risk / (1 + len(RISK_COMPONENTS))
        df["bua_risk_score"] = risk

    apply(train)
    apply(val)
    risk_threshold = float(train["bua_risk_score"].quantile(risk_quantile))
    high_disagreement_threshold = float(train["branch_disagreement"].quantile(0.75))

    for df in (train, val):
        df["bua_low_margin"] = df["final_margin_abs"].to_numpy(dtype=float) <= low_margin_threshold
        df["bua_high_risk"] = df["bua_risk_score"].to_numpy(dtype=float) >= risk_threshold
        df["bua_high_disagreement"] = (
            df["branch_disagreement"].to_numpy(dtype=float) >= high_disagreement_threshold
        )
        df["bua_boundary_trust"] = df["bua_low_margin"] | df["bua_high_risk"]
        df["bua_final_error"] = df["y_pred"].to_numpy(dtype=int) != df["y_true"].to_numpy(dtype=int)

    return {
        "low_margin_quantile": low_margin_quantile,
        "low_margin_threshold": low_margin_threshold,
        "risk_quantile": risk_quantile,
        "risk_threshold": risk_threshold,
        "high_disagreement_threshold": high_disagreement_threshold,
        "risk_components": {
            "negative_final_margin_abs": {"min": margin_params[0], "max": margin_params[1]},
            **{name: {"min": lo, "max": hi} for name, (lo, hi) in component_params.items()},
        },
    }


def q_target(df: pd.DataFrame) -> np.ndarray:
    return normalize_rows(df[[f"q_target_{branch}" for branch in BRANCHES]].to_numpy(dtype=float))


def q_confidence(df: pd.DataFrame) -> np.ndarray:
    prob = df[[f"p_{branch}" for branch in BRANCHES]].to_numpy(dtype=float)
    return normalize_rows(np.abs(2.0 * prob - 1.0) + EPS)


def q_reverse(df: pd.DataFrame) -> np.ndarray:
    utility = df[[f"u_{branch}" for branch in BRANCHES]].to_numpy(dtype=float)
    return normalize_rows(np.maximum(-utility, 0.0) + EPS)


def random_q(rows: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.dirichlet(np.ones(len(BRANCHES)), size=rows)


def shuffled_rows(values: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return values[rng.permutation(len(values))]


def alpha_from_q(
    df: pd.DataFrame,
    q: np.ndarray,
    *,
    alpha_max: float,
    mode: str,
    boundary_override: np.ndarray | None = None,
) -> np.ndarray:
    utility_confidence = 1.0 - entropy(q, normalized=True)
    if mode == "none":
        alpha = np.zeros(len(df), dtype=float)
    elif mode == "constant":
        alpha = np.full(len(df), alpha_max, dtype=float)
    elif mode == "entropy":
        alpha = alpha_max * utility_confidence
    elif mode == "boundary":
        boundary = (
            np.asarray(boundary_override, dtype=bool)
            if boundary_override is not None
            else df["bua_boundary_trust"].to_numpy(dtype=bool)
        )
        alpha = alpha_max * boundary.astype(float)
    elif mode == "boundary_entropy":
        boundary = (
            np.asarray(boundary_override, dtype=bool)
            if boundary_override is not None
            else df["bua_boundary_trust"].to_numpy(dtype=bool)
        )
        alpha = alpha_max * boundary.astype(float) * utility_confidence
    else:
        raise ValueError(f"unknown alpha mode {mode}")
    return np.clip(alpha, 0.0, alpha_max)


def weights_from_alpha_q(alpha: np.ndarray, q: np.ndarray) -> np.ndarray:
    alpha = np.asarray(alpha, dtype=float)
    return (1.0 - alpha[:, None]) / len(BRANCHES) + alpha[:, None] * q


def evaluate_allocation(
    df: pd.DataFrame,
    *,
    split: str,
    variant: str,
    family: str,
    q: np.ndarray,
    alpha: np.ndarray,
    decision_variant: bool,
) -> dict:
    utility = df[[f"u_{branch}" for branch in BRANCHES]].to_numpy(dtype=float)
    prob = df[[f"p_{branch}" for branch in BRANCHES]].to_numpy(dtype=float)
    labels = df["y_true"].to_numpy(dtype=int)
    branch_correct = (prob >= 0.5) == labels[:, None]
    final_error = df["bua_final_error"].to_numpy(dtype=bool)
    low_margin = df["bua_low_margin"].to_numpy(dtype=bool)
    high_risk = df["bua_high_risk"].to_numpy(dtype=bool)
    boundary = df["bua_boundary_trust"].to_numpy(dtype=bool)
    high_disagreement = df["bua_high_disagreement"].to_numpy(dtype=bool)
    weak_domain = df["category_name"].isin(WEAK_DOMAINS.get(str(df["dataset_key"].iloc[0]), [])).to_numpy()
    weights = weights_from_alpha_q(alpha, q)
    weighted_utility = np.sum(weights * utility, axis=1)
    weighted_positive_utility = np.sum(weights * np.maximum(utility, 0.0), axis=1)
    weighted_correct = np.sum(weights * branch_correct.astype(float), axis=1)
    uniform = np.full_like(q, 1.0 / len(BRANCHES))
    uniform_utility = np.sum(uniform * utility, axis=1)
    oracle_utility = np.sum(q_target(df) * utility, axis=1)
    denom = np.maximum(np.abs(oracle_utility - uniform_utility), EPS)
    oracle_capture = (weighted_utility - uniform_utility) / denom
    top_weight = np.argmax(weights, axis=1)
    top_utility = np.argmax(q_target(df), axis=1)
    top_confidence = np.argmax(q_confidence(df), axis=1)
    q_ent = entropy(q, normalized=True)

    row: dict[str, Any] = {
        "split": split,
        "variant": variant,
        "family": family,
        "decision_variant": bool(decision_variant),
        "rows": int(len(df)),
        "alpha_mean": safe_mean(alpha),
        "alpha_active_rate": float((alpha > EPS).mean()),
        "alpha_final_error_auc": rank_auc(final_error.astype(int), alpha),
        "alpha_final_error_corr": corr(alpha, final_error.astype(float)),
        "q_entropy_mean": safe_mean(q_ent),
        "q_entropy_final_error_auc": rank_auc(final_error.astype(int), q_ent),
        "q_entropy_final_error_corr": corr(q_ent, final_error.astype(float)),
        "expected_utility": safe_mean(weighted_utility),
        "expected_positive_utility": safe_mean(weighted_positive_utility),
        "expected_branch_correct": safe_mean(weighted_correct),
        "oracle_capture_mean": safe_mean(oracle_capture),
        "top_weight_branch_correct_rate": safe_mean(branch_correct[np.arange(len(df)), top_weight]),
        "top_weight_matches_utility_rate": float((top_weight == top_utility).mean()),
        "top_weight_matches_confidence_rate": float((top_weight == top_confidence).mean()),
        "w_text_mean": safe_mean(weights[:, 0]),
        "w_image_mean": safe_mean(weights[:, 1]),
        "w_fusion_mean": safe_mean(weights[:, 2]),
        "top_weight_text_rate": float((top_weight == 0).mean()),
        "top_weight_image_rate": float((top_weight == 1).mean()),
        "top_weight_fusion_rate": float((top_weight == 2).mean()),
        "final_error_rate": float(final_error.mean()),
        "low_margin_rate": float(low_margin.mean()),
        "high_risk_rate": float(high_risk.mean()),
        "boundary_trust_rate": float(boundary.mean()),
        "weak_domain_rate": float(weak_domain.mean()),
    }
    masks = {
        "boundary": boundary,
        "non_boundary": ~boundary,
        "low_margin": low_margin,
        "high_risk": high_risk,
        "high_disagreement": high_disagreement,
        "weak_domain": weak_domain,
        "final_error": final_error,
        "final_correct": ~final_error,
    }
    for name, mask in masks.items():
        row[f"{name}_rows"] = int(mask.sum())
        row[f"{name}_expected_utility"] = safe_mean(weighted_utility, mask)
        row[f"{name}_expected_branch_correct"] = safe_mean(weighted_correct, mask)
        row[f"{name}_alpha_mean"] = safe_mean(alpha, mask)
    return row


def build_variants(df: pd.DataFrame, *, split: str, seed: int, alpha_max: float) -> list[dict]:
    rows = len(df)
    true_q = q_target(df)
    uniform_q = np.full((rows, len(BRANCHES)), 1.0 / len(BRANCHES), dtype=float)
    shuffled_q = shuffled_rows(true_q, seed + (101 if split == "train" else 202))
    shuffled_boundary = shuffled_rows(
        df["bua_boundary_trust"].to_numpy(dtype=bool),
        seed + (303 if split == "train" else 404),
    )
    variants = [
        {
            "variant": "bua_anchor_static_aux2p0",
            "family": "anchor",
            "q": uniform_q,
            "alpha": alpha_from_q(df, uniform_q, alpha_max=alpha_max, mode="none"),
            "decision_variant": True,
        },
        {
            "variant": "bua_boundary_gated_utility_aux",
            "family": "primary",
            "q": true_q,
            "alpha": alpha_from_q(df, true_q, alpha_max=alpha_max, mode="boundary_entropy"),
            "decision_variant": True,
        },
        {
            "variant": "bua_utility_only_aux_alloc",
            "family": "ablation",
            "q": true_q,
            "alpha": alpha_from_q(df, true_q, alpha_max=alpha_max, mode="constant"),
            "decision_variant": True,
        },
        {
            "variant": "bua_entropy_gated_utility_aux",
            "family": "ablation",
            "q": true_q,
            "alpha": alpha_from_q(df, true_q, alpha_max=alpha_max, mode="entropy"),
            "decision_variant": True,
        },
        {
            "variant": "bua_boundary_only_aux_strength",
            "family": "ablation",
            "q": uniform_q,
            "alpha": alpha_from_q(df, uniform_q, alpha_max=alpha_max, mode="boundary"),
            "decision_variant": True,
        },
        {
            "variant": "bua_shuffled_utility_control",
            "family": "control",
            "q": shuffled_q,
            "alpha": alpha_from_q(df, shuffled_q, alpha_max=alpha_max, mode="boundary_entropy"),
            "decision_variant": True,
        },
        {
            "variant": "bua_shuffled_boundary_control",
            "family": "control",
            "q": true_q,
            "alpha": alpha_from_q(
                df,
                true_q,
                alpha_max=alpha_max,
                mode="boundary_entropy",
                boundary_override=shuffled_boundary,
            ),
            "decision_variant": True,
        },
        {
            "variant": "bua_random_utility_control",
            "family": "control",
            "q": random_q(rows, seed + (505 if split == "train" else 606)),
            "alpha": None,
            "decision_variant": True,
        },
        {
            "variant": "bua_reverse_utility_control",
            "family": "control",
            "q": q_reverse(df),
            "alpha": None,
            "decision_variant": True,
        },
        {
            "variant": "bua_confidence_only_branch_allocation",
            "family": "control",
            "q": q_confidence(df),
            "alpha": None,
            "decision_variant": True,
        },
    ]
    for variant in variants:
        if variant["alpha"] is None:
            variant["alpha"] = alpha_from_q(
                df,
                variant["q"],
                alpha_max=alpha_max,
                mode="boundary_entropy",
            )
    return variants


def summarize_split(df: pd.DataFrame, split: str) -> dict:
    q = q_target(df)
    utility = df[[f"u_{branch}" for branch in BRANCHES]].to_numpy(dtype=float)
    prob = df[[f"p_{branch}" for branch in BRANCHES]].to_numpy(dtype=float)
    labels = df["y_true"].to_numpy(dtype=int)
    branch_correct = (prob >= 0.5) == labels[:, None]
    top_utility = np.argmax(q, axis=1)
    top_conf = np.argmax(q_confidence(df), axis=1)
    final_error = df["bua_final_error"].to_numpy(dtype=bool)
    boundary = df["bua_boundary_trust"].to_numpy(dtype=bool)
    return {
        "split": split,
        "rows": int(len(df)),
        "final_error_rate": float(final_error.mean()),
        "boundary_trust_rate": float(boundary.mean()),
        "boundary_error_rate": safe_mean(final_error.astype(float), boundary),
        "non_boundary_error_rate": safe_mean(final_error.astype(float), ~boundary),
        "utility_entropy_mean": safe_mean(entropy(q, normalized=True)),
        "utility_entropy_final_error_auc": rank_auc(final_error.astype(int), entropy(q, normalized=True)),
        "utility_entropy_final_error_corr": corr(entropy(q, normalized=True), final_error.astype(float)),
        "top_utility_branch_correct_rate": safe_mean(branch_correct[np.arange(len(df)), top_utility]),
        "top_utility_matches_top_confidence_rate": float((top_utility == top_conf).mean()),
        "mean_q_target": {branch: safe_mean(q[:, idx]) for idx, branch in enumerate(BRANCHES)},
        "mean_raw_utility": {branch: safe_mean(utility[:, idx]) for idx, branch in enumerate(BRANCHES)},
        "top_utility_counts": {
            branch: int((top_utility == idx).sum())
            for idx, branch in enumerate(BRANCHES)
        },
    }


def decision_from_metrics(metrics_df: pd.DataFrame, min_delta: float) -> tuple[str, list[str], dict]:
    val = metrics_df[metrics_df["split"] == "val_diagnostic"].set_index("variant")
    primary = val.loc["bua_boundary_gated_utility_aux"]
    comparisons = {}
    for control in [
        "bua_anchor_static_aux2p0",
        "bua_shuffled_utility_control",
        "bua_random_utility_control",
        "bua_reverse_utility_control",
        "bua_confidence_only_branch_allocation",
        "bua_boundary_only_aux_strength",
    ]:
        comparisons[f"delta_expected_utility_vs_{control}"] = (
            float(primary["expected_utility"]) - float(val.loc[control]["expected_utility"])
        )
    for ablation in [
        "bua_utility_only_aux_alloc",
        "bua_entropy_gated_utility_aux",
        "bua_shuffled_boundary_control",
    ]:
        comparisons[f"delta_expected_utility_vs_{ablation}"] = (
            float(primary["expected_utility"]) - float(val.loc[ablation]["expected_utility"])
        )

    blocking_controls = [
        name.replace("delta_expected_utility_vs_", "")
        for name, delta in comparisons.items()
        if name
        in {
            "delta_expected_utility_vs_bua_shuffled_utility_control",
            "delta_expected_utility_vs_bua_random_utility_control",
            "delta_expected_utility_vs_bua_reverse_utility_control",
            "delta_expected_utility_vs_bua_confidence_only_branch_allocation",
        }
        and delta <= min_delta
    ]
    boundary_not_proven = [
        name.replace("delta_expected_utility_vs_", "")
        for name, delta in comparisons.items()
        if name
        in {
            "delta_expected_utility_vs_bua_utility_only_aux_alloc",
            "delta_expected_utility_vs_bua_entropy_gated_utility_aux",
            "delta_expected_utility_vs_bua_shuffled_boundary_control",
        }
        and delta <= min_delta
    ]
    reasons: list[str] = []
    if blocking_controls:
        reasons.append("primary_not_cleanly_above_controls:" + ",".join(blocking_controls))
    if boundary_not_proven:
        reasons.append("boundary_gate_not_proven_vs:" + ",".join(boundary_not_proven))
    if float(primary["expected_utility"]) <= float(val.loc["bua_anchor_static_aux2p0"]["expected_utility"]) + min_delta:
        reasons.append("primary_not_above_static_aux_anchor")
    if float(primary["top_weight_matches_confidence_rate"]) >= 0.9:
        reasons.append("primary_degenerates_to_confidence_top_branch")

    if not reasons:
        status = "Go-to-D3.5"
        reasons.append("primary_expected_utility_cleanly_above_controls_and_boundary_gate_not_blocked")
    elif any(reason.startswith("primary_not_cleanly_above_controls") for reason in reasons):
        status = "D2.5-No-Go-for-current-BUA-allocator"
    else:
        status = "D2.5-No-Go-for-current-BUA-boundary-gate"
    return status, reasons, comparisons


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        raise RuntimeError(f"{output_dir} exists and is non-empty; pass --overwrite")
    output_dir.mkdir(parents=True, exist_ok=True)

    utility = load_utility(input_dir)
    boundary_meta = add_boundary_features(
        utility["train"],
        utility["val_diagnostic"],
        low_margin_quantile=args.low_margin_quantile,
        risk_quantile=args.risk_quantile,
    )

    metric_rows = []
    for split, df in utility.items():
        for variant in build_variants(df, split=split, seed=args.seed, alpha_max=args.alpha_max):
            metric_rows.append(
                evaluate_allocation(
                    df,
                    split=split,
                    variant=variant["variant"],
                    family=variant["family"],
                    q=variant["q"],
                    alpha=variant["alpha"],
                    decision_variant=variant["decision_variant"],
                )
            )
    metrics_df = pd.DataFrame(metric_rows)
    metrics_path = output_dir / "bua_d25_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)

    split_summary = {
        split: summarize_split(df, split)
        for split, df in utility.items()
    }
    status, reasons, comparisons = decision_from_metrics(metrics_df, args.min_utility_delta)
    summary = {
        "task": "Round10-A / BUA D2.5 offline allocator simulation",
        "status": status,
        "decision": {
            "status": status,
            "reasons": reasons,
            "go_condition": [
                "primary expected utility above shuffled/random/reverse/confidence controls",
                "primary expected utility above static aux uniform anchor",
                "boundary-gated primary not worse than utility-only, entropy-only, or shuffled-boundary controls by the configured moat",
                "primary does not degenerate to confidence-only branch allocation",
            ],
            "min_expected_utility_delta": args.min_utility_delta,
            "test_used_for_decision": False,
        },
        "dataset": args.dataset,
        "seed": int(args.seed),
        "allowed_splits": ["train", "val"],
        "test_split_exported": False,
        "test_used_for_decision": False,
        "training_allowed": False,
        "alpha_max": float(args.alpha_max),
        "boundary_meta": boundary_meta,
        "input_artifacts": {
            "branch_utility_train": {
                "path": str(input_dir / "branch_utility_train.csv"),
                "sha256": sha256(input_dir / "branch_utility_train.csv"),
            },
            "branch_utility_val_diagnostic": {
                "path": str(input_dir / "branch_utility_val_diagnostic.csv"),
                "sha256": sha256(input_dir / "branch_utility_val_diagnostic.csv"),
            },
        },
        "outputs": {
            "metrics_csv": str(metrics_path),
        },
        "split_summary": split_summary,
        "decision_comparisons": comparisons,
        "metrics": {
            row["variant"] + "::" + row["split"]: clean_json(row)
            for row in metric_rows
        },
        "claim_scope": "D2.5 offline allocator simulation only; it can open or close BUA D3.5 but cannot judge trained D4 performance.",
        "level_reached": "D2.5",
        "required_level_for_exclusion": "D2.5 closes only the current allocator gate; D3.5/D4 are required for training-time feasibility if this gate passes.",
        "status_scope": "current BUA boundary-gated utility allocator",
    }

    summary_path = output_dir / "bua_d25_summary.json"
    manifest_path = output_dir / "bua_d25_manifest.json"
    decision_path = output_dir / "bua_d25_summary.md"
    write_json(summary_path, summary)
    manifest = {
        "task": summary["task"],
        "status": status,
        "dataset": args.dataset,
        "seed": int(args.seed),
        "allowed_splits": ["train", "val"],
        "test_split_exported": False,
        "test_used_for_decision": False,
        "training_allowed": False,
        "outputs": summary["outputs"] | {
            "summary_json": str(summary_path),
            "summary_md": str(decision_path),
        },
        "command_args": vars(args),
    }
    write_json(manifest_path, manifest)

    val_metrics = metrics_df[metrics_df["split"] == "val_diagnostic"].set_index("variant")

    def fmt(name: str) -> str:
        row = val_metrics.loc[name]
        return (
            f"expected_utility={row['expected_utility']:.6f}, "
            f"expected_branch_correct={row['expected_branch_correct']:.6f}, "
            f"alpha_mean={row['alpha_mean']:.6f}"
        )

    lines = [
        "# Round10-A BUA D2.5 Decision",
        "",
        f"Decision: **{status}**",
        "",
        "Rules:",
        "- Train/val-only; test not exported, opened, or used.",
        "- D2.5 checks offline allocation signal cleanliness, not trained F1.",
        "- D3.5 opens only if utility and boundary allocation are separated from strong controls.",
        "",
        "Key val-diagnostic allocation metrics:",
        f"- primary `bua_boundary_gated_utility_aux`: {fmt('bua_boundary_gated_utility_aux')}",
        f"- anchor `bua_anchor_static_aux2p0`: {fmt('bua_anchor_static_aux2p0')}",
        f"- utility-only `bua_utility_only_aux_alloc`: {fmt('bua_utility_only_aux_alloc')}",
        f"- entropy-only `bua_entropy_gated_utility_aux`: {fmt('bua_entropy_gated_utility_aux')}",
        f"- shuffled utility `bua_shuffled_utility_control`: {fmt('bua_shuffled_utility_control')}",
        f"- random utility `bua_random_utility_control`: {fmt('bua_random_utility_control')}",
        f"- reverse utility `bua_reverse_utility_control`: {fmt('bua_reverse_utility_control')}",
        f"- confidence-only `bua_confidence_only_branch_allocation`: {fmt('bua_confidence_only_branch_allocation')}",
        "",
        "Decision comparisons:",
    ]
    for name, value in comparisons.items():
        lines.append(f"- {name}: `{value:.6f}`")
    lines.extend(["", "Reasons:"])
    lines.extend([f"- {reason}" for reason in reasons])
    lines.extend([
        "",
        "Notable diagnostics:",
        (
            f"- val boundary trust coverage: "
            f"`{split_summary['val_diagnostic']['boundary_trust_rate']:.6f}`"
        ),
        (
            f"- val utility entropy error AUC: "
            f"`{split_summary['val_diagnostic']['utility_entropy_final_error_auc']:.6f}`"
            if split_summary["val_diagnostic"]["utility_entropy_final_error_auc"] is not None
            else "- val utility entropy error AUC: `NA`"
        ),
        (
            f"- val top-utility branch correct rate: "
            f"`{split_summary['val_diagnostic']['top_utility_branch_correct_rate']:.6f}`"
        ),
        "",
        "Claim scope:",
        summary["claim_scope"],
        "",
    ])
    decision_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"summary: {summary_path}")
    print(f"decision: {decision_path}")
    print(f"metrics: {metrics_path}")
    print(f"status: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
