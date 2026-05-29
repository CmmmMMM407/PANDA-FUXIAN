# Round12 Ensemble Val Audit

Decision: `Diagnostic-only-No-Go-to-Round15`

## Key Metrics

- Strongest single: `panda_reproduced_seed42` Macro-F1 `0.954457`, Acc `0.954472`.
- Best non-oracle ensemble: `panda_dwa_equal_logit` Macro-F1 `0.956090`, Acc `0.956098`.
- Delta Macro-F1: `0.001633`.

## Decision Reasons

- Macro-F1 lift is below +0.002 and paired bootstrap lower bound does not support a positive lift

## Asset Notes

- Available safe train/val artifacts: `18`.
- Missing planned artifacts: `12`.
- DAMMFND/MMDFND train/val probability artifacts were not found in the current safe export pool.
- No test split is read or written by this script.

## Outputs

- `round12_asset_manifest.csv`
- `round12_ensemble_results.csv`
- `round12_pairwise_diversity.csv`
- `round12_fold_weights.csv`
- `round12_decision_summary.json`
