# Round11 UEA-PANDA D4 Summary

Decision: **Utility-Entropy-Aux-Diagnostic-only**

Rules: train/val-only; test not exported/opened/used. UEA must beat static aux 2.0, DWA/GradNorm/PCGrad/CAGrad, detached aux, same-budget, and utility controls before D5.

## Utility Target

- Train rows: `4926`
- Utility entropy mean: `0.04821407631680495`
- Top utility branch rates: text `0.5032480714575721`, image `0.0`, fusion `0.49675192854242795`

## Ranking

| Variant | Family | F1 | Acc | AUC | W2C | C2W | FlipNet |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| static_aux_weight_2p0_anchor_control | required_control | 0.939837 | 0.939837 | 0.981407 | 17 | 15 | 2 |
| uea_reverse_utility_entropy_alpha0p5 | round11_uea_control | 0.939837 | 0.939837 | 0.982084 | 15 | 13 | 2 |
| generic_dwa | required_control | 0.938210 | 0.938211 | 0.980962 | 18 | 17 | 1 |
| uea_entropy_alpha0p25 | round11_uea_ablation | 0.938207 | 0.938211 | 0.983977 | 14 | 13 | 1 |
| detached_aux_no_feature_update | required_control | 0.936585 | 0.936585 | 0.983765 | 0 | 0 | 0 |
| deterministic_train_l0 | required_control | 0.936585 | 0.936585 | 0.983765 | 0 | 0 | 0 |
| same_budget_noop_l0 | required_control | 0.936585 | 0.936585 | 0.983765 | 0 | 0 | 0 |
| uea_confidence_entropy_alpha0p5 | round11_uea_control | 0.936569 | 0.936585 | 0.983247 | 18 | 18 | 0 |
| uea_random_utility_entropy_alpha0p5 | round11_uea_control | 0.934955 | 0.934959 | 0.980677 | 15 | 16 | -1 |
| uea_shuffled_utility_entropy_alpha0p5 | round11_uea_control | 0.929936 | 0.930081 | 0.978022 | 19 | 23 | -4 |
| generic_pcgrad | required_control | 0.928337 | 0.928455 | 0.980349 | 15 | 20 | -5 |
| generic_cagrad | required_control | 0.926655 | 0.926829 | 0.981618 | 14 | 20 | -6 |
| uea_boundary_entropy_alpha0p5 | round10_boundary_negative_control | 0.923574 | 0.923577 | 0.979397 | 13 | 21 | -8 |
| uea_entropy_alpha0p5 | round11_uea_primary | 0.921905 | 0.921951 | 0.981142 | 12 | 21 | -9 |
| uea_utility_only_alpha0p25 | round11_uea_ablation | 0.918697 | 0.918699 | 0.976372 | 13 | 24 | -11 |
| uea_utility_only_alpha0p5 | round11_uea_ablation | 0.918604 | 0.918699 | 0.978519 | 12 | 23 | -11 |
| generic_gradnorm | required_control | 0.907313 | 0.907317 | 0.967636 | 10 | 28 | -18 |

## Decision Reasons

- best_uea_not_above_required_controls:static_aux_weight_2p0_anchor_control
- primary_not_best:best=uea_reverse_utility_entropy_alpha0p5
- best_uea_macro_f1_moat_lt_delta:best_control:static_aux_weight_2p0_anchor_control

## Claim Scope

- D4 seed42 train/val-only smoke for current UEA per-sample branch auxiliary allocation implementation.
- test_split_exported: `False`
- test_used_for_decision: `False`
