#!/usr/bin/env python3
"""Summarize Round11 UEA-PANDA D4 train/val-only ablation."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


UEA_VARIANTS = [
    "uea_entropy_alpha0p5",
    "uea_utility_only_alpha0p5",
    "uea_entropy_alpha0p25",
    "uea_utility_only_alpha0p25",
    "uea_shuffled_utility_entropy_alpha0p5",
    "uea_random_utility_entropy_alpha0p5",
    "uea_reverse_utility_entropy_alpha0p5",
    "uea_confidence_entropy_alpha0p5",
    "uea_boundary_entropy_alpha0p5",
]
PRIMARY_VARIANTS = {"uea_entropy_alpha0p5"}
REQUIRED_CONTROLS = [
    "deterministic_train_l0",
    "same_budget_noop_l0",
    "static_aux_weight_2p0_anchor_control",
    "generic_dwa",
    "generic_gradnorm",
    "generic_pcgrad",
    "generic_cagrad",
    "detached_aux_no_feature_update",
]
UTILITY_CONTROLS = {
    "uea_shuffled_utility_entropy_alpha0p5",
    "uea_random_utility_entropy_alpha0p5",
    "uea_reverse_utility_entropy_alpha0p5",
    "uea_confidence_entropy_alpha0p5",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uea-root", default="repro_logs/round11_uea_d4/seed42")
    parser.add_argument("--control-summary", default="repro_logs/round6_r6a_smoke/seed42/round6_r6a_smoke_summary.csv")
    parser.add_argument("--control-eval-root", default="repro_logs/round6_r6a_smoke/seed42/eval")
    parser.add_argument("--utility-csv", default="repro_logs/round9_cue_d2/seed42/branch_utility_train.csv")
    parser.add_argument("--output-dir", default="repro_logs/round11_uea_d4/seed42/summary")
    parser.add_argument("--dataset", default="weibo21")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--moat-delta", type=float, default=0.003)
    return parser.parse_args()


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if hasattr(value, "item"):
        return clean_json(value.item())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_json(payload), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metrics_path(root: Path, tag: str, dataset: str, seed: int) -> Path:
    return root / "eval" / tag / f"selector_variant_deterministic_train_{dataset}_seed{seed}_val_metrics.json"


def pred_path(root: Path, tag: str, dataset: str, seed: int) -> Path:
    return root / "eval" / tag / f"selector_variant_deterministic_train_{dataset}_seed{seed}_val.csv"


def control_pred_path(root: Path, tag: str, dataset: str, seed: int) -> Path:
    return root / tag / f"selector_variant_deterministic_train_{dataset}_seed{seed}_val.csv"


def flip_audit(base_csv: Path, cand_csv: Path) -> dict:
    if not base_csv.exists() or not cand_csv.exists():
        return {
            "changed_count": None,
            "wrong_to_correct": None,
            "correct_to_wrong": None,
            "flip_net": None,
        }
    base = pd.read_csv(base_csv)
    cand = pd.read_csv(cand_csv)
    merged = base[["sample_id", "y_true", "y_pred"]].merge(
        cand[["sample_id", "y_pred"]],
        on="sample_id",
        suffixes=("_base", "_cand"),
        validate="one_to_one",
    )
    y = merged["y_true"].astype(int)
    base_correct = merged["y_pred_base"].astype(int) == y
    cand_correct = merged["y_pred_cand"].astype(int) == y
    return {
        "changed_count": int((merged["y_pred_base"].astype(int) != merged["y_pred_cand"].astype(int)).sum()),
        "wrong_to_correct": int((~base_correct & cand_correct).sum()),
        "correct_to_wrong": int((base_correct & ~cand_correct).sum()),
        "flip_net": int((~base_correct & cand_correct).sum() - (base_correct & ~cand_correct).sum()),
    }


def parse_uea_meta(log_path: Path) -> dict:
    if not log_path.exists():
        return {}
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"uea_meta: (\{.*?\})", text)
    if not match:
        return {}
    raw = match.group(1)
    try:
        return json.loads(raw.replace("'", '"').replace("None", "null"))
    except json.JSONDecodeError:
        return {"raw_uea_meta": raw}


def rank_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    labels = np.asarray(y, dtype=int)
    values = np.asarray(score, dtype=float)
    pos = labels == 1
    neg = labels == 0
    if int(pos.sum()) == 0 or int(neg.sum()) == 0:
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
    n_pos = int(pos.sum())
    n_neg = int(neg.sum())
    rank_sum_pos = float(ranks[pos].sum())
    return float((rank_sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def utility_distribution(utility_csv: Path) -> dict:
    if not utility_csv.exists():
        return {"utility_csv_exists": False}
    df = pd.read_csv(utility_csv)
    q = df[["q_target_text", "q_target_image", "q_target_fusion"]].to_numpy(dtype=float)
    top = np.argmax(q, axis=1)
    entropy = -np.sum(np.clip(q, 1e-12, 1.0) * np.log(np.clip(q, 1e-12, 1.0)), axis=1) / math.log(3)
    return {
        "utility_csv_exists": True,
        "rows": int(len(df)),
        "split_values": sorted(df["split"].astype(str).unique().tolist()),
        "utility_entropy_mean": float(np.mean(entropy)),
        "top_utility_text_rate": float(np.mean(top == 0)),
        "top_utility_image_rate": float(np.mean(top == 1)),
        "top_utility_fusion_rate": float(np.mean(top == 2)),
        "mean_q_text": float(np.mean(q[:, 0])),
        "mean_q_image": float(np.mean(q[:, 1])),
        "mean_q_fusion": float(np.mean(q[:, 2])),
        "utility_entropy_has_positive_utility_auc": rank_auc(df["has_positive_utility"].astype(int).to_numpy(), entropy),
    }


def family_for_tag(tag: str) -> str:
    if tag in PRIMARY_VARIANTS:
        return "round11_uea_primary"
    if tag == "uea_boundary_entropy_alpha0p5":
        return "round10_boundary_negative_control"
    if tag in UTILITY_CONTROLS:
        return "round11_uea_control"
    if tag.startswith("uea_"):
        return "round11_uea_ablation"
    return "required_control"


def main() -> int:
    args = parse_args()
    uea_root = Path(args.uea_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    missing_controls = []
    control_summary = Path(args.control_summary)
    if control_summary.exists():
        controls_df = pd.read_csv(control_summary)
        controls = controls_df[controls_df["tag"].isin(REQUIRED_CONTROLS)].copy()
        missing_controls = sorted(set(REQUIRED_CONTROLS) - set(controls["tag"].astype(str)))
        for row in controls.to_dict("records"):
            item = dict(row)
            item["variant"] = item["tag"]
            item["family"] = "required_control"
            rows.append(item)
    else:
        missing_controls = REQUIRED_CONTROLS.copy()

    base_csv = control_pred_path(Path(args.control_eval_root), "deterministic_train_l0", args.dataset, args.seed)
    missing_uea = []
    for tag in UEA_VARIANTS:
        mpath = metrics_path(uea_root, tag, args.dataset, args.seed)
        ppath = pred_path(uea_root, tag, args.dataset, args.seed)
        if not mpath.exists() or not ppath.exists():
            missing_uea.append(tag)
            continue
        metrics = load_json(mpath)
        item = {
            "tag": tag,
            "variant": tag,
            "family": family_for_tag(tag),
            "macro_f1": metrics.get("macro_f1"),
            "accuracy": metrics.get("accuracy"),
            "auc": metrics.get("auc"),
            "brier": metrics.get("brier"),
            "ece": metrics.get("ece"),
            "high_conf_error_rate": metrics.get("high_conf_error_rate"),
        }
        item.update(flip_audit(base_csv, ppath))
        log_path = Path("logs/round11_uea_d4") / f"{args.dataset}_seed{args.seed}_{tag}_epoch5.log"
        for key, value in parse_uea_meta(log_path).items():
            item[f"train_{key}"] = value
        rows.append(item)

    out_df = pd.DataFrame(rows)
    if not out_df.empty:
        out_df = out_df.sort_values(["macro_f1", "accuracy", "auc"], ascending=False)
    out_csv = output_dir / "round11_uea_d4_summary.csv"
    out_df.to_csv(out_csv, index=False)

    uea_df = out_df[out_df["family"].astype(str).str.startswith("round11_uea", na=False)] if not out_df.empty else pd.DataFrame()
    control_df = out_df[out_df["family"] == "required_control"] if not out_df.empty else pd.DataFrame()
    reasons = []
    decision: dict[str, Any]
    if uea_df.empty:
        decision = {
            "status": "Blocked",
            "reasons": ["missing_all_uea_metrics"],
            "missing_uea_variants": missing_uea,
            "missing_controls": missing_controls,
            "test_used_for_decision": False,
        }
    else:
        best_uea = uea_df.iloc[0].to_dict()
        primary = uea_df[uea_df["tag"].isin(PRIMARY_VARIANTS)]
        primary_row = primary.iloc[0].to_dict() if not primary.empty else None
        best_control = control_df.iloc[0].to_dict() if not control_df.empty else None
        deterministic = control_df[control_df["tag"] == "deterministic_train_l0"].iloc[0].to_dict() if "deterministic_train_l0" in set(control_df.get("tag", [])) else None

        if missing_controls:
            reasons.append("missing_required_controls:" + ",".join(missing_controls))
        if missing_uea:
            reasons.append("missing_uea_variants:" + ",".join(missing_uea))

        not_above_controls = []
        for tag in REQUIRED_CONTROLS:
            row = control_df[control_df["tag"] == tag]
            if not row.empty:
                r = row.iloc[0]
                if float(best_uea["macro_f1"]) <= float(r["macro_f1"]) or float(best_uea["accuracy"]) <= float(r["accuracy"]):
                    not_above_controls.append(tag)
        if not_above_controls:
            reasons.append("best_uea_not_above_required_controls:" + ",".join(not_above_controls))

        not_above_utility_controls = []
        for tag in sorted(UTILITY_CONTROLS):
            row = uea_df[uea_df["tag"] == tag]
            if not row.empty:
                r = row.iloc[0]
                if float(best_uea["macro_f1"]) <= float(r["macro_f1"]) and best_uea["tag"] != tag:
                    not_above_utility_controls.append(tag)
        if not_above_utility_controls:
            reasons.append("best_uea_not_above_utility_controls:" + ",".join(not_above_utility_controls))

        primary_not_best = bool(primary_row and primary_row["tag"] != best_uea["tag"])
        if primary_not_best:
            reasons.append(f"primary_not_best:best={best_uea['tag']}")

        if best_uea.get("wrong_to_correct") is not None and int(best_uea.get("wrong_to_correct", 0)) <= int(best_uea.get("correct_to_wrong", 0)):
            reasons.append("best_uea_flip_not_net_positive")

        moat_fail = []
        if best_control is not None:
            if float(best_uea["macro_f1"]) < float(best_control["macro_f1"]) + float(args.moat_delta):
                moat_fail.append(f"best_control:{best_control['tag']}")
        if moat_fail:
            reasons.append("best_uea_macro_f1_moat_lt_delta:" + ",".join(moat_fail))

        if not reasons:
            status = "Go-to-D5"
        elif deterministic and float(best_uea["macro_f1"]) > float(deterministic["macro_f1"]):
            status = "Utility-Entropy-Aux-Diagnostic-only"
        else:
            status = "No-Go-for-current-UEA"

        decision = {
            "status": status,
            "candidate_id": "Round11-A",
            "candidate_name": "UEA-PANDA utility-entropy anchored auxiliary allocation",
            "best_uea_variant": best_uea["tag"],
            "best_uea_family": best_uea["family"],
            "best_uea_macro_f1": best_uea.get("macro_f1"),
            "best_uea_accuracy": best_uea.get("accuracy"),
            "best_uea_auc": best_uea.get("auc"),
            "best_uea_wrong_to_correct": best_uea.get("wrong_to_correct"),
            "best_uea_correct_to_wrong": best_uea.get("correct_to_wrong"),
            "primary_variant": None if primary_row is None else primary_row["tag"],
            "primary_macro_f1": None if primary_row is None else primary_row.get("macro_f1"),
            "primary_accuracy": None if primary_row is None else primary_row.get("accuracy"),
            "best_control_tag": None if best_control is None else best_control["tag"],
            "best_control_macro_f1": None if best_control is None else best_control.get("macro_f1"),
            "best_control_accuracy": None if best_control is None else best_control.get("accuracy"),
            "reasons": reasons,
            "missing_controls": missing_controls,
            "missing_uea_variants": missing_uea,
            "claim_scope": "D4 seed42 train/val-only smoke for current UEA per-sample branch auxiliary allocation implementation.",
            "level_reached": "D4 seed42",
            "required_level_for_primary_candidate": "D5 three-seed val only if D4 beats static aux 2.0, DWA/GradNorm/PCGrad/CAGrad, detached aux, same-budget, and utility controls.",
            "test_split_exported": False,
            "test_used_for_decision": False,
        }

    utility_meta = utility_distribution(Path(args.utility_csv))
    summary = {
        "task": "Round11-A / UEA-PANDA D4",
        "decision": decision,
        "utility_distribution": utility_meta,
        "rows": rows,
        "allowed_splits": ["train", "val"],
        "test_split_exported": False,
        "test_used_for_decision": False,
        "outputs": {
            "summary_csv": str(out_csv),
            "decision_json": str(output_dir / "round11_uea_d4_decision.json"),
            "summary_md": str(output_dir / "round11_uea_d4_summary.md"),
        },
    }
    write_json(output_dir / "round11_uea_d4_summary.json", summary)
    write_json(output_dir / "round11_uea_d4_decision.json", decision)

    lines = [
        "# Round11 UEA-PANDA D4 Summary",
        "",
        f"Decision: **{decision['status']}**",
        "",
        "Rules: train/val-only; test not exported/opened/used. UEA must beat static aux 2.0, DWA/GradNorm/PCGrad/CAGrad, detached aux, same-budget, and utility controls before D5.",
        "",
        "## Utility Target",
        "",
        f"- Train rows: `{utility_meta.get('rows')}`",
        f"- Utility entropy mean: `{utility_meta.get('utility_entropy_mean')}`",
        f"- Top utility branch rates: text `{utility_meta.get('top_utility_text_rate')}`, image `{utility_meta.get('top_utility_image_rate')}`, fusion `{utility_meta.get('top_utility_fusion_rate')}`",
        "",
        "## Ranking",
        "",
        "| Variant | Family | F1 | Acc | AUC | W2C | C2W | FlipNet |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in out_df.to_dict("records"):
        auc_text = "" if pd.isna(row.get("auc")) else f"{float(row.get('auc')):.6f}"
        w2c_text = "" if pd.isna(row.get("wrong_to_correct")) else str(int(row.get("wrong_to_correct")))
        c2w_text = "" if pd.isna(row.get("correct_to_wrong")) else str(int(row.get("correct_to_wrong")))
        flip_text = "" if pd.isna(row.get("flip_net")) else str(int(row.get("flip_net")))
        lines.append(
            f"| {row.get('tag')} | {row.get('family')} | "
            f"{float(row['macro_f1']):.6f} | {float(row['accuracy']):.6f} | "
            f"{auc_text} | {w2c_text} | {c2w_text} | {flip_text} |"
        )
    lines.extend(
        [
            "",
            "## Decision Reasons",
            "",
            *[f"- {reason}" for reason in decision.get("reasons", [])],
            "",
            "## Claim Scope",
            "",
            f"- {decision.get('claim_scope')}",
            f"- test_split_exported: `{decision.get('test_split_exported')}`",
            f"- test_used_for_decision: `{decision.get('test_used_for_decision')}`",
        ]
    )
    (output_dir / "round11_uea_d4_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Decision: {decision['status']}")
    print(f"Summary: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
