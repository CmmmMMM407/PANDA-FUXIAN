# Round14 OOF Utility Calibration Launch Gate

Decision: `Round14-A-No-Go-to-B-C-current-assets`

Scope: train/val-only launch audit. No test split is read, exported, or used.

## Evidence

- Round12 status: `Diagnostic-only-No-Go-to-Round15`
- Round12 oracle gap vs best single: `0.029279`
- Round12 best learned/non-oracle delta vs best single: `0.001633`
- Round13 D4 status: `D4-No-Go-to-D5`
- Round13 best ADWA minus deterministic: `-0.003254`
- Split-safe OOF utility targets found: `0`

## Reasons

- round12_oracle_selection_space_present_but_diagnostic_only
- round12_learned_ensemble_no_go_to_round15
- round13_adwa_no_go_to_d5
- round13_best_adwa_not_above_deterministic
- missing_split_safe_oof_utility_target
- old_round9_train_or_val_utility_assets_exist_but_are_not_oof_safe

## Required Controls Present As Diagnostics

- `platt_temperature`: `true`
- `final_aux_stacking`: `true`
- `confidence_only_gate`: `true`
- `shuffled_utility`: `true`
- `reverse_utility`: `true`
- `random_utility`: `true`
- `static_aux_2p0`: `true`
- `generic_dwa`: `true`
