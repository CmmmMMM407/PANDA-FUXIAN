# Round 6 R6-C Gate-0 Summary

Decision: `No-Go`

Rules: train/val only; no test export/open/analyze; low-margin threshold fit on train.

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| final_only_platt | calibration_control | 0.947964 | 0.947967 | 0.984188 | 0.160843 | 0.018805 | 8 | 4 | 0.009259 |
| same_param_global_h_collab_control | same_param_control | 0.947964 | 0.947967 | 0.983956 | 0.161941 | 0.018812 | 8 | 4 | 0.009259 |
| random_mask_h_di_control | random_mask_control | 0.946336 | 0.946341 | 0.983987 | 0.165666 | 0.027408 | 8 | 5 | 0.006650 |
| random_mask_h_collab_control | random_mask_control | 0.946336 | 0.946341 | 0.983681 | 0.162060 | 0.018683 | 8 | 5 | 0.006650 |
| same_param_global_h_di_control | same_param_control | 0.944712 | 0.944715 | 0.984527 | 0.162187 | 0.022823 | 7 | 5 | 0.004191 |
| r6c_low_margin_h_di_adapter | primary | 0.944708 | 0.944715 | 0.981491 | 0.178887 | 0.035084 | 8 | 6 | 0.004036 |
| random_mask_h_final_control | random_mask_control | 0.943084 | 0.943089 | 0.983268 | 0.168585 | 0.019190 | 7 | 6 | 0.001577 |
| same_param_global_h_final_control | same_param_control | 0.943084 | 0.943089 | 0.982485 | 0.171579 | 0.028978 | 7 | 6 | 0.001577 |
| r6c_low_margin_h_final_adapter | primary | 0.943084 | 0.943089 | 0.980338 | 0.182569 | 0.025810 | 7 | 6 | 0.001577 |
| low_margin_logit_bias_control | bias_control | 0.943068 | 0.943089 | 0.984188 | 0.175488 | 0.023781 | 10 | 9 | 0.001077 |
| original_final | primary_baseline | 0.941456 | 0.941463 | 0.984188 | 0.179868 | 0.023883 | 0 | 0 | 0.000000 |
| random_feature_low_margin_control | random_feature_control | 0.941429 | 0.941463 | 0.984104 | 0.165099 | 0.014574 | 11 | 11 | -0.001749 |
| r6c_low_margin_h_collab_adapter | primary | 0.939797 | 0.939837 | 0.984421 | 0.162687 | 0.025857 | 11 | 12 | -0.004405 |
| final_aux_stacking_control | ordinary_stacking_control | 0.855441 | 0.858537 | 0.865288 | 1.453618 | 0.132253 | 23 | 74 | -0.160221 |

Decision reasons:
- best_control_matches_or_beats_primary
- best_control_is_calibration_control
