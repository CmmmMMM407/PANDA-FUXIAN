# Round13 ADWA-PANDA D4 Summary

Decision: `D4-No-Go-to-D5`

Scope: Weibo-21 seed42 5-epoch train/val-only. No test split exported or used.

## Metrics

- `static_aux_weight_2p0_anchor_control` (control): F1 `0.939837`, Acc `0.939837`, AUC `0.981407`
- `generic_dwa` (control): F1 `0.938210`, Acc `0.938211`, AUC `0.980962`
- `detached_aux_no_feature_update` (control): F1 `0.936585`, Acc `0.936585`, AUC `0.983765`
- `deterministic_train_l0` (control): F1 `0.936585`, Acc `0.936585`, AUC `0.983765`
- `same_budget_noop_l0` (control): F1 `0.936585`, Acc `0.936585`, AUC `0.983765`
- `adwa_clip_1p0_2p5` (primary): F1 `0.933331`, Acc `0.933333`, AUC `0.980645`
- `adwa_final_guard` (primary): F1 `0.933327`, Acc `0.933333`, AUC `0.982729`
- `adwa_clip_1p5_2p5` (primary): F1 `0.930055`, Acc `0.930081`, AUC `0.983554`
- `generic_pcgrad` (control): F1 `0.928337`, Acc `0.928455`, AUC `0.980349`
- `generic_cagrad` (control): F1 `0.926655`, Acc `0.926829`, AUC `0.981618`
- `adwa_entropy_smoothed_proxy` (primary): F1 `0.918689`, Acc `0.918699`, AUC `0.978942`
- `generic_gradnorm` (control): F1 `0.907313`, Acc `0.907317`, AUC `0.967636`

## Reasons

- best_adwa_not_above_static_aux_2p0
- best_adwa_not_above_generic_dwa
- best_adwa_not_above_best_strong_control:static_aux_weight_2p0_anchor_control
