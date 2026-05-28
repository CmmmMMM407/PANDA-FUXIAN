# Round 6 R6-F Gate-0 Summary

Decision: `No-Go`

Rules: train/val only; frozen final head; same-sample view drops only; no cross-sample modality replacement.

Val drop-delta error AUC: `0.537856`

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 | High-disagreement dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mean_rescaled_drop | primary | 0.956086 | 0.956098 | 0.987425 | 0.158684 | 0.028814 | 0 | 0 | 0.000000 | 0.000000 |
| original_full_view | baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 | 0.000000 |
| drop_image_rescaled | diagnostic_primary | 0.949559 | 0.949593 | 0.985912 | 0.229818 | 0.040498 | 4 | 8 | -0.009785 | -0.031958 |
| control_shuffled_mask_drop_disagreeing_branch_high_disagreement | shuffled_mask_control | 0.938211 | 0.938211 | 0.976594 | 0.266503 | 0.042238 | 5 | 16 | -0.026110 | -0.021896 |
| control_shuffled_mask_drop_disagreeing_branch_low_margin | shuffled_mask_control | 0.938210 | 0.938211 | 0.982782 | 0.213182 | 0.041014 | 5 | 16 | -0.026067 | -0.043014 |
| drop_fusion | diagnostic_primary | 0.933322 | 0.933333 | 0.979989 | 0.180437 | 0.023237 | 7 | 21 | -0.033148 | -0.043833 |
| r6f_drop_disagreeing_branch_high_disagreement | primary | 0.928440 | 0.928455 | 0.979207 | 0.274381 | 0.053168 | 6 | 23 | -0.040300 | -0.043833 |
| r6f_drop_disagreeing_branch_low_margin | primary | 0.926817 | 0.926829 | 0.976499 | 0.285084 | 0.051860 | 6 | 24 | -0.042707 | -0.043833 |
| control_shuffled_mask_drop_low_conf_branch_low_margin | shuffled_mask_control | 0.917017 | 0.917073 | 0.972522 | 0.315116 | 0.066098 | 6 | 30 | -0.057935 | -0.083217 |
| drop_image | diagnostic_primary | 0.916848 | 0.917073 | 0.985584 | 0.266544 | 0.056743 | 9 | 33 | -0.056947 | -0.100161 |
| control_shuffled_mask_drop_low_conf_branch_high_disagreement | shuffled_mask_control | 0.912167 | 0.912195 | 0.973168 | 0.327120 | 0.069631 | 5 | 32 | -0.064890 | -0.097226 |
| r6f_drop_low_conf_branch_high_disagreement | primary | 0.905635 | 0.905691 | 0.974744 | 0.340466 | 0.078564 | 10 | 41 | -0.074727 | -0.109200 |
| r6f_drop_low_conf_branch_low_margin | primary | 0.904000 | 0.904065 | 0.971306 | 0.351169 | 0.078235 | 10 | 42 | -0.077195 | -0.109200 |
| control_random_branch_drop_all | random_branch_control | 0.889346 | 0.889431 | 0.946674 | 0.407516 | 0.080232 | 12 | 53 | -0.098935 | -0.179586 |
| control_random_branch_drop_disagreeing_branch_low_margin | random_branch_control | 0.877893 | 0.878049 | 0.953189 | 0.456253 | 0.091268 | 9 | 57 | -0.116232 | -0.181808 |
| control_random_branch_drop_low_conf_branch_low_margin | random_branch_control | 0.872961 | 0.873171 | 0.953157 | 0.425170 | 0.086877 | 11 | 62 | -0.123775 | -0.180593 |
| control_random_branch_drop_low_conf_branch_high_disagreement | random_branch_control | 0.864949 | 0.865041 | 0.949561 | 0.447426 | 0.092941 | 8 | 64 | -0.134975 | -0.184680 |
| drop_text_rescaled | diagnostic_primary | 0.858052 | 0.860163 | 0.983067 | 0.513926 | 0.082156 | 13 | 72 | -0.143598 | -0.258600 |
| control_random_branch_drop_disagreeing_branch_high_disagreement | random_branch_control | 0.855131 | 0.855285 | 0.940412 | 0.510496 | 0.106679 | 7 | 69 | -0.149820 | -0.259484 |
| drop_fusion_rescaled | diagnostic_primary | 0.789393 | 0.798374 | 0.980264 | 0.624666 | 0.141753 | 10 | 107 | -0.274269 | -0.375431 |
| drop_text | diagnostic_primary | 0.389751 | 0.523577 | 0.983099 | 1.538700 | 0.405128 | 16 | 282 | -0.605195 | -0.523508 |

Decision reasons:
- best_primary_flip_not_net_positive
- no_positive_low_margin_or_high_disagreement_bin
- drop_delta_error_auc_below_0p65
