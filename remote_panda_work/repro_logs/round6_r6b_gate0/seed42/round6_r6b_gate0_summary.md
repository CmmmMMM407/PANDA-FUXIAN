# Round 6 R6-B Gate-0 Summary

Decision: `No-Go`

Rules: train/val only; no test export/open/analyze; all tuning fit on train.

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 | High-disagreement dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shuffled_confidence_evidence_gate | shuffled_confidence_control | 0.960971 | 0.960976 | 0.987530 | 0.154532 | 0.029062 | 3 | 0 | 0.007264 | 0.019250 |
| original_final | primary_baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 | 0.000000 |
| scalar_weight_final_aux | scalar_weight_control | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 | 0.000000 |
| final_only_platt | calibration_control | 0.954451 | 0.954472 | 0.987372 | 0.143413 | 0.021351 | 1 | 2 | -0.002479 | -0.006104 |
| aux_logit_mean | branch_only_control | 0.951182 | 0.951220 | 0.986568 | 0.156055 | 0.022307 | 3 | 6 | -0.007409 | -0.012505 |
| branch_only_stacking | branch_only_control | 0.949580 | 0.949593 | 0.986282 | 0.150956 | 0.027529 | 2 | 6 | -0.009606 | -0.013129 |
| r6b_confidence_evidence_gate | primary | 0.949567 | 0.949593 | 0.985912 | 0.180126 | 0.034164 | 3 | 7 | -0.009722 | -0.019184 |
| r6b_entropy_evidence_gate | primary | 0.947937 | 0.947967 | 0.985130 | 0.204887 | 0.037290 | 3 | 8 | -0.012159 | -0.025571 |
| random_confidence_evidence_gate | random_confidence_control | 0.936552 | 0.936585 | 0.986304 | 0.184760 | 0.042312 | 2 | 14 | -0.028965 | -0.071119 |
| ordinary_final_aux_stacking | ordinary_stacking_control | 0.928136 | 0.928455 | 0.926526 | 0.557259 | 0.058798 | 7 | 24 | -0.042637 | -0.096862 |

Decision reasons:
- best_primary_below_original_final
- best_primary_flip_not_net_positive
- no_positive_low_margin_or_high_disagreement_bin
- best_control_matches_or_beats_primary
- best_control_is_shuffled_confidence_control

If R6-B is No-Go, do not implement training-time branch aggregation from this evidence gate.
