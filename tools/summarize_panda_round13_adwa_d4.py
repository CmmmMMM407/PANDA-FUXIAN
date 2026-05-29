#!/usr/bin/env python3
"""Summarize Round13 ADWA-PANDA D4 seed42 train/val-only smoke."""

import argparse
import json
import math
from pathlib import Path

import pandas as pd


PRIMARY_TAGS = {
    "adwa_clip_1p5_2p5",
    "adwa_clip_1p0_2p5",
    "adwa_final_guard",
    "adwa_entropy_smoothed_proxy",
}
REQUIRED_CONTROLS = {
    "deterministic_train_l0",
    "static_aux_weight_2p0_anchor_control",
    "generic_dwa",
    "generic_gradnorm",
    "generic_pcgrad",
    "generic_cagrad",
    "detached_aux_no_feature_update",
    "same_budget_noop_l0",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="repro_logs/round13_adwa_d4/seed42")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--dataset", default="weibo21")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_metrics(root: Path, tag: str, dataset: str, seed: int):
    path = root / "eval" / tag / f"selector_variant_deterministic_train_{dataset}_seed{seed}_val_metrics.json"
    if not path.exists():
        return None, str(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["tag"] = tag
    payload["metrics_path"] = str(path)
    payload["role"] = "primary" if tag in PRIMARY_TAGS else "control"
    return payload, str(path)


def safe_num(value, default=-1.0):
    if value is None:
        return default
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    return value if math.isfinite(value) else default


def pick_best(rows):
    return max(rows, key=lambda row: (safe_num(row.get("macro_f1")), safe_num(row.get("accuracy")), safe_num(row.get("auc"))))


def build_decision(rows, missing):
    primary_rows = [row for row in rows if row["tag"] in PRIMARY_TAGS]
    control_rows = [row for row in rows if row["tag"] in REQUIRED_CONTROLS]
    reasons = []
    if missing:
        reasons.append("missing_variant_metrics:" + ",".join(missing))
    if not primary_rows:
        reasons.append("missing_primary_adwa_metrics")
    if not control_rows:
        reasons.append("missing_control_metrics")
    if reasons:
        return {
            "status": "Blocked",
            "reasons": reasons,
            "go_to_d5": False,
            "test_split_exported": False,
            "test_used_for_decision": False,
        }
    best_primary = pick_best(primary_rows)
    best_control = pick_best(control_rows)
    static = next((row for row in rows if row["tag"] == "static_aux_weight_2p0_anchor_control"), None)
    dwa = next((row for row in rows if row["tag"] == "generic_dwa"), None)
    if static is None:
        reasons.append("missing_static_aux_2p0_control")
    if dwa is None:
        reasons.append("missing_generic_dwa_control")
    if static is not None and safe_num(best_primary.get("macro_f1")) <= safe_num(static.get("macro_f1")):
        reasons.append("best_adwa_not_above_static_aux_2p0")
    if dwa is not None and safe_num(best_primary.get("macro_f1")) <= safe_num(dwa.get("macro_f1")):
        reasons.append("best_adwa_not_above_generic_dwa")
    if safe_num(best_primary.get("macro_f1")) <= safe_num(best_control.get("macro_f1")):
        reasons.append("best_adwa_not_above_best_strong_control:" + best_control["tag"])
    status = "D4-Go-to-D5" if not reasons else "D4-No-Go-to-D5"
    return {
        "status": status,
        "claim_scope": "ADWA-PANDA seed42 5-epoch train/val-only D4 smoke",
        "level_reached": "D4",
        "required_level_for_stability": "D5 three-seed val",
        "best_primary": best_primary,
        "best_control": best_control,
        "static_aux_2p0": static,
        "generic_dwa": dwa,
        "reasons": reasons,
        "go_to_d5": not reasons,
        "allowed_splits": ["train", "val"],
        "test_split_exported": False,
        "test_used_for_decision": False,
    }


def write_markdown(path: Path, decision: dict, rows: list[dict], missing: list[str]):
    lines = [
        "# Round13 ADWA-PANDA D4 Summary",
        "",
        f"Decision: `{decision['status']}`",
        "",
        "Scope: Weibo-21 seed42 5-epoch train/val-only. No test split exported or used.",
        "",
        "## Metrics",
        "",
    ]
    for row in sorted(rows, key=lambda item: safe_num(item.get("macro_f1")), reverse=True):
        lines.append(
            f"- `{row['tag']}` ({row['role']}): F1 `{safe_num(row.get('macro_f1')):.6f}`, "
            f"Acc `{safe_num(row.get('accuracy')):.6f}`, AUC `{safe_num(row.get('auc')):.6f}`"
        )
    if missing:
        lines.extend(["", "## Missing", ""])
        lines.extend(f"- `{tag}`" for tag in missing)
    if decision.get("reasons"):
        lines.extend(["", "## Reasons", ""])
        lines.extend(f"- {reason}" for reason in decision["reasons"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    root = Path(args.root)
    output_dir = Path(args.output_dir) if args.output_dir else root / "summary"
    output_dir.mkdir(parents=True, exist_ok=True)
    tags = sorted(PRIMARY_TAGS | REQUIRED_CONTROLS)
    rows = []
    missing = []
    for tag in tags:
        payload, path = load_metrics(root, tag, args.dataset, args.seed)
        if payload is None:
            missing.append(tag)
        else:
            rows.append(payload)
    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "round13_adwa_d4_summary.csv", index=False)
    decision = build_decision(rows, missing)
    (output_dir / "round13_adwa_d4_decision_summary.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    write_markdown(output_dir / "round13_adwa_d4_summary.md", decision, rows, missing)
    print(json.dumps(decision, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
