#!/usr/bin/env python3
"""Round14 OOF utility calibration launch gate.

This gate is intentionally conservative. It decides whether the current
train/val-only evidence and assets are enough to open a split-safe OOF utility
calibration experiment. It does not train a model, does not read test files,
and does not treat old train-only utility CSVs as OOF targets.
"""

import argparse
import csv
import glob
import json
import math
from pathlib import Path


REQUIRED_ROUND14_CONTROLS = [
    "platt_temperature",
    "final_aux_stacking",
    "confidence_only_gate",
    "shuffled_utility",
    "reverse_utility",
    "random_utility",
    "static_aux_2p0",
    "generic_dwa",
]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--round12-decision",
        default="repro_logs/round12_ensemble_val_audit/round12_decision_summary.json",
    )
    parser.add_argument(
        "--round12-results",
        default="repro_logs/round12_ensemble_val_audit/round12_ensemble_results.csv",
    )
    parser.add_argument(
        "--round13-decision",
        default="repro_logs/round13_adwa_d4/seed42/summary/round13_adwa_d4_decision_summary.json",
    )
    parser.add_argument(
        "--round13-summary",
        default="repro_logs/round13_adwa_d4/seed42/summary/round13_adwa_d4_summary.csv",
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default="repro_logs/round14_oof_launch_gate")
    parser.add_argument("--oracle-gap-threshold", type=float, default=0.02)
    return parser.parse_args()


def load_json(path):
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def safe_float(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def best_row(rows, predicate):
    candidates = [row for row in rows if predicate(row)]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            safe_float(row.get("macro_f1")) or -1.0,
            safe_float(row.get("accuracy")) or -1.0,
            safe_float(row.get("auc")) or -1.0,
        ),
    )


def scan_oof_assets(repo_root):
    root = Path(repo_root)
    patterns = [
        "repro_logs/**/*oof*",
        "repro_logs/**/*OOF*",
        "repro_logs/**/*out_of_fold*",
        "repro_logs/**/*fold*utility*",
        "repro_logs/**/*utility*fold*",
    ]
    hits = []
    for pattern in patterns:
        hits.extend(glob.glob(str(root / pattern), recursive=True))
    unique = sorted({str(Path(hit)) for hit in hits})
    classified = []
    for hit in unique:
        name = Path(hit).name.lower()
        is_round12_fold_weight = "round12_fold_weights" in name
        is_split_safe_oof_utility = (
            ("oof" in name or "out_of_fold" in name)
            and "utility" in name
            and not is_round12_fold_weight
        )
        classified.append(
            {
                "path": hit,
                "is_split_safe_oof_utility_target": bool(is_split_safe_oof_utility),
                "note": "round12_fold_weights_not_utility_target" if is_round12_fold_weight else "",
            }
        )
    return classified


def old_utility_assets(repo_root):
    root = Path(repo_root)
    paths = [
        root / "repro_logs/round9_cue_d2/seed42/branch_utility_train.csv",
        root / "repro_logs/round9_cue_d2/seed42/branch_utility_val_diagnostic.csv",
    ]
    out = []
    for path in paths:
        out.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "usable_for_round14_oof_target": False,
                "reason": (
                    "train_only_not_out_of_fold"
                    if "train" in path.name
                    else "val_diagnostic_not_allowed_for_target"
                ),
            }
        )
    return out


def available_controls(repo_root):
    root = Path(repo_root)
    controls = {}
    round9_summary = root / "repro_logs/round9_cue_d2/seed42/cue_d2_summary.json"
    round11_summary = root / "repro_logs/round11_uea_d4/seed42/summary/round11_uea_d4_summary.json"
    round12_results = root / "repro_logs/round12_ensemble_val_audit/round12_ensemble_results.csv"
    controls["platt_temperature"] = round9_summary.exists()
    controls["final_aux_stacking"] = round9_summary.exists()
    controls["confidence_only_gate"] = round9_summary.exists()
    controls["shuffled_utility"] = round9_summary.exists() or round11_summary.exists()
    controls["reverse_utility"] = round11_summary.exists()
    controls["random_utility"] = round9_summary.exists() or round11_summary.exists()
    rows = load_csv_rows(round12_results)
    names = {row.get("name") for row in rows}
    controls["static_aux_2p0"] = any(str(name).startswith("static_aux_2p0") for name in names)
    controls["generic_dwa"] = any(str(name).startswith("generic_dwa") for name in names)
    return controls


def write_markdown(path, decision):
    lines = [
        "# Round14 OOF Utility Calibration Launch Gate",
        "",
        f"Decision: `{decision['status']}`",
        "",
        "Scope: train/val-only launch audit. No test split is read, exported, or used.",
        "",
        "## Evidence",
        "",
        f"- Round12 status: `{decision['round12']['status']}`",
        f"- Round12 oracle gap vs best single: `{decision['round12']['oracle_gap_macro_f1']:.6f}`",
        f"- Round12 best learned/non-oracle delta vs best single: `{decision['round12']['learned_delta_macro_f1']:.6f}`",
        f"- Round13 D4 status: `{decision['round13']['status']}`",
        f"- Round13 best ADWA minus deterministic: `{decision['round13']['best_adwa_minus_deterministic_macro_f1']:.6f}`",
        f"- Split-safe OOF utility targets found: `{decision['oof_assets']['split_safe_oof_utility_target_count']}`",
        "",
        "## Reasons",
        "",
    ]
    lines.extend(f"- {reason}" for reason in decision["reasons"])
    lines.extend(["", "## Required Controls Present As Diagnostics", ""])
    for name, present in decision["controls"].items():
        lines.append(f"- `{name}`: `{str(present).lower()}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def json_safe(value):
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def main():
    args = parse_args()
    repo_root = Path(args.repo_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    round12_decision = load_json(args.round12_decision) or {}
    round12_rows = load_csv_rows(args.round12_results)
    best_single = round12_decision.get("best_single") or {}
    best_non_oracle = round12_decision.get("best_non_oracle_ensemble") or {}
    best_oracle = best_row(round12_rows, lambda row: row.get("kind") == "oracle_any_correct") or {}
    best_single_f1 = safe_float(best_single.get("macro_f1")) or -1.0
    learned_f1 = safe_float(best_non_oracle.get("macro_f1")) or -1.0
    oracle_f1 = safe_float(best_oracle.get("macro_f1")) or -1.0
    learned_delta = learned_f1 - best_single_f1
    oracle_gap = oracle_f1 - best_single_f1

    round13_decision = load_json(args.round13_decision) or {}
    round13_rows = load_csv_rows(args.round13_summary)
    best_adwa = best_row(round13_rows, lambda row: row.get("role") == "primary") or {}
    deterministic = best_row(round13_rows, lambda row: row.get("tag") == "deterministic_train_l0") or {}
    best_adwa_f1 = safe_float(best_adwa.get("macro_f1")) or -1.0
    deterministic_f1 = safe_float(deterministic.get("macro_f1")) or -1.0

    oof_assets = scan_oof_assets(repo_root)
    split_safe_oof_count = sum(item["is_split_safe_oof_utility_target"] for item in oof_assets)
    old_assets = old_utility_assets(repo_root)
    controls = available_controls(repo_root)

    reasons = []
    round12_oracle_space = oracle_gap >= args.oracle_gap_threshold
    if round12_oracle_space:
        reasons.append("round12_oracle_selection_space_present_but_diagnostic_only")
    else:
        reasons.append("round12_oracle_selection_space_below_threshold")
    if not str(round12_decision.get("status", "")).startswith("Go"):
        reasons.append("round12_learned_ensemble_no_go_to_round15")
    if not str(round13_decision.get("status", "")).startswith("D4-Go"):
        reasons.append("round13_adwa_no_go_to_d5")
    if best_adwa_f1 <= deterministic_f1:
        reasons.append("round13_best_adwa_not_above_deterministic")
    if split_safe_oof_count == 0:
        reasons.append("missing_split_safe_oof_utility_target")
    if any(item["exists"] for item in old_assets):
        reasons.append("old_round9_train_or_val_utility_assets_exist_but_are_not_oof_safe")

    missing_controls = [name for name in REQUIRED_ROUND14_CONTROLS if not controls.get(name)]
    if missing_controls:
        reasons.append("missing_required_round14_controls:" + ",".join(missing_controls))

    can_open_b = (
        split_safe_oof_count > 0
        and not missing_controls
        and (round12_oracle_space or str(round13_decision.get("status", "")).startswith("D4-Go"))
    )
    status = "Round14-A-Go-to-B" if can_open_b else "Round14-A-No-Go-to-B-C-current-assets"
    decision = {
        "status": status,
        "claim_scope": "Round14 OOF utility calibration launch feasibility only",
        "level_reached": "Round14-A launch gate",
        "required_level_for_method_claim": "Round14-B/C split-safe OOF target plus controls, then D5 before Round15",
        "round12": {
            "status": round12_decision.get("status"),
            "best_single": best_single,
            "best_non_oracle_ensemble": best_non_oracle,
            "best_oracle": best_oracle,
            "learned_delta_macro_f1": learned_delta,
            "oracle_gap_macro_f1": oracle_gap,
            "oracle_gap_threshold": args.oracle_gap_threshold,
        },
        "round13": {
            "status": round13_decision.get("status"),
            "best_adwa": best_adwa,
            "deterministic": deterministic,
            "best_adwa_minus_deterministic_macro_f1": best_adwa_f1 - deterministic_f1,
        },
        "oof_assets": {
            "scanned_assets": oof_assets,
            "old_non_oof_utility_assets": old_assets,
            "split_safe_oof_utility_target_count": split_safe_oof_count,
        },
        "controls": controls,
        "missing_controls": missing_controls,
        "reasons": reasons,
        "round14_b_started": False,
        "round14_c_started": False,
        "go_to_round15": False,
        "allowed_splits": ["train", "val"],
        "test_split_exported": False,
        "test_used_for_decision": False,
    }

    decision = json_safe(decision)
    (output_dir / "round14_oof_launch_gate_decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(output_dir / "round14_oof_launch_gate_summary.md", decision)
    print(json.dumps(decision, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
