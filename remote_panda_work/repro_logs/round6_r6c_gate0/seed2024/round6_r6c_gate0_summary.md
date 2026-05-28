# Round 6 R6-C Gate-0 Summary

Decision: `No-Go`

Rules: train/val only; no test export/open/analyze; low-margin threshold fit on train.

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original_final | primary_baseline | 0.943041 | 0.943089 | 0.985182 | 0.184023 | 0.032651 | 0 | 0 | 0.000000 |
| random_mask_h_final_control | random_mask_control | 0.941456 | 0.941463 | 0.984527 | 0.167511 | 0.026406 | 5 | 6 | -0.003074 |
| r6c_low_margin_h_di_adapter | primary | 0.939827 | 0.939837 | 0.984252 | 0.182694 | 0.036089 | 4 | 6 | -0.005487 |
| random_feature_low_margin_control | random_feature_control | 0.938210 | 0.938211 | 0.984971 | 0.167752 | 0.032364 | 6 | 9 | -0.008299 |
| same_param_global_h_final_control | same_param_control | 0.938210 | 0.938211 | 0.982845 | 0.176414 | 0.030944 | 6 | 9 | -0.008299 |
| r6c_low_margin_h_final_adapter | primary | 0.936585 | 0.936585 | 0.983215 | 0.186891 | 0.035584 | 6 | 10 | -0.010855 |
| final_only_platt | calibration_control | 0.936579 | 0.936585 | 0.985182 | 0.164027 | 0.023844 | 4 | 8 | -0.010570 |
| random_mask_h_di_control | random_mask_control | 0.936579 | 0.936585 | 0.984580 | 0.171287 | 0.030135 | 4 | 8 | -0.010570 |
| random_mask_h_collab_control | random_mask_control | 0.934958 | 0.934959 | 0.985690 | 0.162535 | 0.022115 | 5 | 10 | -0.013265 |
| same_param_global_h_di_control | same_param_control | 0.934955 | 0.934959 | 0.985394 | 0.166474 | 0.034137 | 4 | 9 | -0.013119 |
| low_margin_logit_bias_control | bias_control | 0.930081 | 0.930081 | 0.985182 | 0.184933 | 0.036540 | 5 | 13 | -0.020961 |
| r6c_low_margin_h_collab_adapter | primary | 0.928454 | 0.928455 | 0.984971 | 0.170214 | 0.034103 | 6 | 15 | -0.023715 |
| same_param_global_h_collab_control | same_param_control | 0.928451 | 0.928455 | 0.985320 | 0.165410 | 0.028393 | 2 | 11 | -0.023039 |
| final_aux_stacking_control | ordinary_stacking_control | 0.869955 | 0.871545 | 0.910904 | 0.801944 | 0.109378 | 21 | 65 | -0.127983 |

Decision reasons:
- best_primary_below_original_final
- best_primary_flip_not_net_positive
- no_positive_low_margin_delta
- best_control_matches_or_beats_primary
