# Round 6 R6-B Feature Gate-0 Summary

Decision: `No-Go`

Rules: train/val only; no test export/open/analyze; frozen final head; train-only gate selection.

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 | High-disagreement dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original_equal_sum | primary_baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 | 0.000000 |
| scalar_branch_weight_control | scalar_weight_control | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 | 0.000000 |
| final_only_platt | calibration_control | 0.954451 | 0.954472 | 0.987372 | 0.143413 | 0.021351 | 1 | 2 | -0.002479 | -0.006104 |
| shuffled_confidence_feature_gate | shuffled_confidence_control | 0.952833 | 0.952846 | 0.987446 | 0.159200 | 0.028819 | 0 | 2 | -0.004803 | -0.006400 |
| r6b_entropy_feature_gate | primary | 0.951216 | 0.951220 | 0.986526 | 0.160875 | 0.031684 | 2 | 5 | -0.007083 | -0.007556 |
| r6b_branch_final_agreement_feature_gate | proxy_primary | 0.939832 | 0.939837 | 0.980349 | 0.239780 | 0.043875 | 6 | 16 | -0.023621 | -0.050147 |
| r6b_confidence_feature_gate | primary | 0.938175 | 0.938211 | 0.983078 | 0.208111 | 0.046155 | 6 | 17 | -0.026598 | -0.037923 |
| random_confidence_feature_gate | random_confidence_control | 0.930045 | 0.930081 | 0.977790 | 0.227457 | 0.040999 | 5 | 21 | -0.038587 | -0.077472 |
| ordinary_final_aux_stacking | ordinary_stacking_control | 0.928136 | 0.928455 | 0.926526 | 0.557259 | 0.058798 | 7 | 24 | -0.042637 | -0.096862 |

Decision reasons:
- best_primary_below_original_equal_sum
- best_primary_flip_not_net_positive
- no_positive_low_margin_or_high_disagreement_bin
- best_control_matches_or_beats_primary
