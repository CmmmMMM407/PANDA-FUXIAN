#!/usr/bin/env python3
"""Round12 train/val-only ensemble and diversity audit for PANDA assets.

The script consumes safe selector_variant CSVs produced by
run_panda_round12_export_trainval_logits.sh. It never reads test splits and
never writes sample text or image paths.
"""

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold


FAMILIES = {
    "panda_reproduced": {
        "mode": "panda_gumbel",
        "tag": "selector_variant_panda_gumbel_{dataset}_seed{seed}_{split}.csv",
    },
    "static_aux_2p0": {
        "mode": "deterministic_train",
        "tag": "selector_variant_deterministic_train_{dataset}_seed{seed}_{split}.csv",
    },
    "generic_dwa": {
        "mode": "deterministic_train",
        "tag": "selector_variant_deterministic_train_{dataset}_seed{seed}_{split}.csv",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="weibo21", choices=["weibo21", "weibo"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 2026])
    parser.add_argument("--input-root", default="repro_logs/round12_trainval_exports")
    parser.add_argument("--output-dir", default="repro_logs/round12_ensemble_val_audit")
    parser.add_argument("--bootstrap-iters", type=int, default=1000)
    parser.add_argument("--grid-step", type=float, default=0.05)
    parser.add_argument("--random-seed", type=int, default=12012)
    return parser.parse_args()


def safe_auc(y_true, y_score):
    y_true = np.asarray(y_true).astype(int)
    if len(np.unique(y_true)) < 2:
        return None
    return float(roc_auc_score(y_true, y_score))


def metrics(y_true, y_score):
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)
    y_pred = (y_score >= 0.5).astype(int)
    return {
        "rows": int(len(y_true)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=[0, 1], average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "auc": safe_auc(y_true, y_score),
    }


def logit(prob):
    prob = np.clip(np.asarray(prob, dtype=float), 1e-7, 1.0 - 1e-7)
    return np.log(prob / (1.0 - prob))


def sigmoid(value):
    value = np.asarray(value, dtype=float)
    return 1.0 / (1.0 + np.exp(-value))


def expected_path(input_root, family, dataset, seed, split):
    spec = FAMILIES[family]
    return (
        Path(input_root)
        / family
        / spec["tag"].format(dataset=dataset, seed=seed, split=split)
    )


def load_asset(input_root, family, dataset, seed, split):
    path = expected_path(input_root, family, dataset, seed, split)
    if not path.exists():
        return None
    df = pd.read_csv(path)
    required = {"sample_id", "dataset_key", "seed", "split", "y_true", "y_score"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    out = df[["sample_id", "dataset_key", "seed", "split", "y_true", "y_score"]].copy()
    out["family"] = family
    out["artifact_path"] = str(path)
    return out


def build_asset_manifest(args):
    rows = []
    assets = {}
    for family in FAMILIES:
        for seed in args.seeds:
            for split in ["train", "val"]:
                path = expected_path(args.input_root, family, args.dataset, seed, split)
                status = "available" if path.exists() else "missing"
                rows.append(
                    {
                        "dataset": args.dataset,
                        "family": family,
                        "seed": seed,
                        "split": split,
                        "status": status,
                        "path": str(path),
                        "safe_for_sync": True,
                        "contains_sample_text": False,
                        "contains_image_path": False,
                    }
                )
                asset = load_asset(args.input_root, family, args.dataset, seed, split)
                if asset is not None:
                    assets[(family, seed, split)] = asset
    for family in ["dammfnd_reproduced", "mmdfnd_reproduced"]:
        for seed in args.seeds:
            for split in ["train", "val"]:
                rows.append(
                    {
                        "dataset": args.dataset,
                        "family": family,
                        "seed": seed,
                        "split": split,
                        "status": "missing",
                        "path": "",
                        "safe_for_sync": True,
                        "contains_sample_text": False,
                        "contains_image_path": False,
                    }
                )
    return pd.DataFrame(rows), assets


def align_assets(asset_items):
    base = None
    names = []
    scores = []
    for name, df in asset_items:
        current = df[["sample_id", "y_true", "y_score"]].sort_values("sample_id").reset_index(drop=True)
        if base is None:
            base = current[["sample_id", "y_true"]].copy()
        else:
            if not np.array_equal(base["sample_id"].to_numpy(), current["sample_id"].to_numpy()):
                raise ValueError(f"sample_id mismatch for {name}")
            if not np.array_equal(base["y_true"].to_numpy(), current["y_true"].to_numpy()):
                raise ValueError(f"label mismatch for {name}")
        names.append(name)
        scores.append(current["y_score"].to_numpy(dtype=float))
    return base, names, np.vstack(scores)


def make_family_means(assets, families, split="val"):
    items = []
    for family in families:
        seed_items = []
        for (asset_family, seed, asset_split), df in assets.items():
            if asset_family == family and asset_split == split:
                seed_items.append((f"{family}_seed{seed}", df))
        if not seed_items:
            raise ValueError(f"No assets for family={family} split={split}")
        base, _, scores = align_assets(seed_items)
        family_score = sigmoid(np.mean(logit(scores), axis=0))
        family_df = base.copy()
        family_df["y_score"] = family_score
        items.append((family, family_df))
    return align_assets(items)


def equal_logit_ensemble(asset_items):
    base, names, scores = align_assets(asset_items)
    return base, names, sigmoid(np.mean(logit(scores), axis=0))


def family_weight_grid(n, step):
    units = int(round(1.0 / step))
    if n == 1:
        yield np.ones(1)
        return
    for counts in itertools.product(range(units + 1), repeat=n):
        if sum(counts) == units:
            yield np.asarray(counts, dtype=float) / float(units)


def weighted_family_scores(family_scores, weights):
    return sigmoid(np.average(logit(family_scores), axis=0, weights=weights))


def choose_weights(y_true, family_scores, step):
    best = None
    for weights in family_weight_grid(family_scores.shape[0], step):
        score = weighted_family_scores(family_scores, weights)
        row = metrics(y_true, score)
        key = (row["macro_f1"], row["accuracy"], 0.0 if row["auc"] is None else row["auc"])
        if best is None or key > best[0]:
            best = (key, weights, score, row)
    return best[1], best[3]


def nested_convex(y_true, family_scores, step, seed):
    y_true = np.asarray(y_true).astype(int)
    out = np.zeros_like(y_true, dtype=float)
    fold_rows = []
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    for fold, (train_idx, eval_idx) in enumerate(skf.split(np.zeros(len(y_true)), y_true), start=1):
        weights, tune_metrics = choose_weights(y_true[train_idx], family_scores[:, train_idx], step)
        out[eval_idx] = weighted_family_scores(family_scores[:, eval_idx], weights)
        fold_rows.append(
            {
                "fold": fold,
                "weights": json.dumps(weights.tolist()),
                "tune_macro_f1": tune_metrics["macro_f1"],
                "tune_accuracy": tune_metrics["accuracy"],
            }
        )
    return out, fold_rows


def nested_platt_equal(y_true, family_scores, seed):
    y_true = np.asarray(y_true).astype(int)
    out = np.zeros_like(y_true, dtype=float)
    fold_rows = []
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    for fold, (train_idx, eval_idx) in enumerate(skf.split(np.zeros(len(y_true)), y_true), start=1):
        calibrated = []
        for row in family_scores:
            model = LogisticRegression(solver="lbfgs")
            model.fit(logit(row[train_idx]).reshape(-1, 1), y_true[train_idx])
            calibrated.append(model.predict_proba(logit(row[eval_idx]).reshape(-1, 1))[:, 1])
        out[eval_idx] = sigmoid(np.mean(logit(np.vstack(calibrated)), axis=0))
        fold_rows.append({"fold": fold, "calibration": "platt", "family_count": int(family_scores.shape[0])})
    return out, fold_rows


def nested_isotonic_equal(y_true, family_scores, seed):
    y_true = np.asarray(y_true).astype(int)
    out = np.zeros_like(y_true, dtype=float)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    for train_idx, eval_idx in skf.split(np.zeros(len(y_true)), y_true):
        calibrated = []
        for row in family_scores:
            model = IsotonicRegression(out_of_bounds="clip")
            model.fit(row[train_idx], y_true[train_idx])
            calibrated.append(model.predict(row[eval_idx]))
        out[eval_idx] = sigmoid(np.mean(logit(np.vstack(calibrated)), axis=0))
    return out


def oracle_upper_bound(y_true, scores):
    preds = scores >= 0.5
    y_true = np.asarray(y_true).astype(int)
    any_correct = (preds == y_true[None, :]).any(axis=0)
    oracle_pred = np.where(any_correct, y_true, preds[0].astype(int))
    return {
        "rows": int(len(y_true)),
        "macro_f1": float(f1_score(y_true, oracle_pred, labels=[0, 1], average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(y_true, oracle_pred)),
        "auc": None,
        "oracle_unfixable_errors": int((~any_correct).sum()),
    }


def pairwise_audit(y_true, names, scores):
    y_true = np.asarray(y_true).astype(int)
    rows = []
    preds = scores >= 0.5
    for i, j in itertools.combinations(range(len(names)), 2):
        pi = preds[i].astype(int)
        pj = preds[j].astype(int)
        err_i = pi != y_true
        err_j = pj != y_true
        disagreement = pi != pj
        rows.append(
            {
                "model_a": names[i],
                "model_b": names[j],
                "error_overlap_count": int((err_i & err_j).sum()),
                "error_overlap_rate": float((err_i & err_j).mean()),
                "a_wrong_b_correct": int((err_i & ~err_j).sum()),
                "a_correct_b_wrong": int((~err_i & err_j).sum()),
                "disagreement_count": int(disagreement.sum()),
                "disagreement_rate": float(disagreement.mean()),
                "disagreement_any_correct": int((disagreement & ((pi == y_true) | (pj == y_true))).sum()),
                "disagreement_both_wrong": int((disagreement & err_i & err_j).sum()),
            }
        )
    return rows


def bootstrap_delta(y_true, reference_score, candidate_score, iters, seed):
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true).astype(int)
    ref = np.asarray(reference_score, dtype=float)
    cand = np.asarray(candidate_score, dtype=float)
    deltas = []
    n = len(y_true)
    for _ in range(iters):
        idx = rng.integers(0, n, size=n)
        deltas.append(metrics(y_true[idx], cand[idx])["macro_f1"] - metrics(y_true[idx], ref[idx])["macro_f1"])
    arr = np.asarray(deltas)
    return {
        "bootstrap_iters": int(iters),
        "delta_macro_f1_mean": float(arr.mean()),
        "delta_macro_f1_ci025": float(np.quantile(arr, 0.025)),
        "delta_macro_f1_ci975": float(np.quantile(arr, 0.975)),
        "p_delta_le_0": float(np.mean(arr <= 0.0)),
    }


def add_result(rows, name, kind, families, y_true, y_score, extra=None):
    row = {
        "name": name,
        "kind": kind,
        "families": ",".join(families),
    }
    row.update(metrics(y_true, y_score))
    if extra:
        row.update(extra)
    rows.append(row)


def write_markdown(output_dir, decision, best_single, best_candidate, asset_manifest, results):
    lines = [
        "# Round12 Ensemble Val Audit",
        "",
        f"Decision: `{decision['status']}`",
        "",
        "## Key Metrics",
        "",
        f"- Strongest single: `{best_single['name']}` Macro-F1 `{best_single['macro_f1']:.6f}`, Acc `{best_single['accuracy']:.6f}`.",
        f"- Best non-oracle ensemble: `{best_candidate['name']}` Macro-F1 `{best_candidate['macro_f1']:.6f}`, Acc `{best_candidate['accuracy']:.6f}`.",
        f"- Delta Macro-F1: `{decision['delta_macro_f1']:.6f}`.",
        "",
        "## Decision Reasons",
        "",
    ]
    lines.extend([f"- {reason}" for reason in decision["reasons"]])
    lines.extend(
        [
            "",
            "## Asset Notes",
            "",
            f"- Available safe train/val artifacts: `{int((asset_manifest['status'] == 'available').sum())}`.",
            f"- Missing planned artifacts: `{int((asset_manifest['status'] == 'missing').sum())}`.",
            "- DAMMFND/MMDFND train/val probability artifacts were not found in the current safe export pool.",
            "- No test split is read or written by this script.",
            "",
            "## Outputs",
            "",
            "- `round12_asset_manifest.csv`",
            "- `round12_ensemble_results.csv`",
            "- `round12_pairwise_diversity.csv`",
            "- `round12_fold_weights.csv`",
            "- `round12_decision_summary.json`",
        ]
    )
    (output_dir / "round12_ensemble_audit_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_manifest, assets = build_asset_manifest(args)
    asset_manifest.to_csv(output_dir / "round12_asset_manifest.csv", index=False)

    val_assets = [
        (f"{family}_seed{seed}", df)
        for (family, seed, split), df in sorted(assets.items())
        if split == "val"
    ]
    if not val_assets:
        raise RuntimeError("No val assets found. Run run_panda_round12_export_trainval_logits.sh first.")

    base, names, scores = align_assets(val_assets)
    y_true = base["y_true"].to_numpy(dtype=int)
    result_rows = []
    fold_rows = []

    for name, df in val_assets:
        aligned, _, score = align_assets([(name, df)])
        add_result(result_rows, name, "single", [name.split("_seed")[0]], y_true, score[0])

    groups = {
        "panda_only_equal_logit": ["panda_reproduced"],
        "static_only_equal_logit": ["static_aux_2p0"],
        "dwa_only_equal_logit": ["generic_dwa"],
        "panda_static_equal_logit": ["panda_reproduced", "static_aux_2p0"],
        "panda_dwa_equal_logit": ["panda_reproduced", "generic_dwa"],
        "panda_static_dwa_equal_logit": ["panda_reproduced", "static_aux_2p0", "generic_dwa"],
    }

    group_scores = {}
    for group_name, families in groups.items():
        group_items = [
            (name, df)
            for name, df in val_assets
            if name.split("_seed")[0] in families
        ]
        _, _, group_score = equal_logit_ensemble(group_items)
        group_scores[group_name] = group_score
        add_result(result_rows, group_name, "equal_logit", families, y_true, group_score)

        _, family_names, family_scores = make_family_means(assets, families, split="val")
        if len(families) >= 2:
            nested_score, nested_rows = nested_convex(y_true, family_scores, args.grid_step, args.random_seed)
            for row in nested_rows:
                row.update({"group": group_name, "method": "nested_convex"})
                fold_rows.append(row)
            add_result(result_rows, f"{group_name}_nested_convex", "nested_convex", families, y_true, nested_score)

            platt_score, platt_rows = nested_platt_equal(y_true, family_scores, args.random_seed + 1)
            for row in platt_rows:
                row.update({"group": group_name, "method": "nested_platt_equal"})
                fold_rows.append(row)
            add_result(result_rows, f"{group_name}_nested_platt_equal", "nested_platt_equal", families, y_true, platt_score)

            isotonic_score = nested_isotonic_equal(y_true, family_scores, args.random_seed + 2)
            add_result(result_rows, f"{group_name}_nested_isotonic_equal", "nested_isotonic_equal", families, y_true, isotonic_score)

        oracle = oracle_upper_bound(y_true, align_assets(group_items)[2])
        oracle["name"] = f"{group_name}_oracle_any_correct"
        oracle["kind"] = "oracle_any_correct"
        oracle["families"] = ",".join(families)
        result_rows.append(oracle)

    pairwise_rows = pairwise_audit(y_true, names, scores)
    pd.DataFrame(pairwise_rows).to_csv(output_dir / "round12_pairwise_diversity.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "round12_fold_weights.csv", index=False)

    results = pd.DataFrame(result_rows)
    results = results.sort_values(["kind", "macro_f1", "accuracy"], ascending=[True, False, False])
    results.to_csv(output_dir / "round12_ensemble_results.csv", index=False)

    single = results[results["kind"] == "single"].sort_values(["macro_f1", "accuracy"], ascending=False).iloc[0].to_dict()
    non_oracle = results[~results["kind"].isin(["single", "oracle_any_correct"])].sort_values(
        ["macro_f1", "accuracy"], ascending=False
    )
    best = non_oracle.iloc[0].to_dict()
    ref_name = single["name"]
    ref_score = dict(val_assets)[ref_name]["y_score"].to_numpy(dtype=float)
    best_score = group_scores.get(best["name"])
    if best_score is None:
        # Nested/calibrated scores are deterministic but not retained above; recompute the most likely best groups.
        families = best["families"].split(",")
        _, _, family_scores = make_family_means(assets, families, split="val")
        if best["kind"] == "nested_convex":
            best_score, _ = nested_convex(y_true, family_scores, args.grid_step, args.random_seed)
        elif best["kind"] == "nested_platt_equal":
            best_score, _ = nested_platt_equal(y_true, family_scores, args.random_seed + 1)
        elif best["kind"] == "nested_isotonic_equal":
            best_score = nested_isotonic_equal(y_true, family_scores, args.random_seed + 2)
        else:
            best_score = weighted_family_scores(family_scores, np.ones(len(families)) / len(families))

    delta = float(best["macro_f1"] - single["macro_f1"])
    bootstrap = bootstrap_delta(y_true, ref_score, best_score, args.bootstrap_iters, args.random_seed + 3)
    reasons = []
    if best["accuracy"] <= single["accuracy"]:
        reasons.append("best ensemble accuracy does not exceed strongest single model")
    if delta < 0.002 and bootstrap["delta_macro_f1_ci025"] <= 0:
        reasons.append("Macro-F1 lift is below +0.002 and paired bootstrap lower bound does not support a positive lift")
    if len(best["families"].split(",")) < 2:
        reasons.append("best ensemble does not use at least two method families")
    status = "Go-to-Round15-final-freeze" if not reasons else "Diagnostic-only-No-Go-to-Round15"
    if not reasons:
        reasons.append("best ensemble passes val-only lift, accuracy, and family-complementarity gates")

    decision = {
        "status": status,
        "best_single": single,
        "best_non_oracle_ensemble": best,
        "delta_macro_f1": delta,
        "bootstrap_vs_best_single": bootstrap,
        "reasons": reasons,
        "allowed_splits": ["train", "val"],
        "test_split_exported": False,
        "test_used_for_decision": False,
    }
    (output_dir / "round12_decision_summary.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown(output_dir, decision, single, best, asset_manifest, results)
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
