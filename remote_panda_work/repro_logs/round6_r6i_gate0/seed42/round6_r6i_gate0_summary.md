# Round 6 R6-I Gate-0 Summary

Decision: `No-Go`

Rules: train/val only; frozen h_final; true-domain adapter must beat random-domain and same-param controls.

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 | Weak dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original_final | baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 | 0.000000 |
| final_only_platt | calibration_control | 0.954451 | 0.954472 | 0.987372 | 0.154402 | 0.043038 | 1 | 2 | -0.002479 | -0.008579 |
| shared_h_final_adapter_control | same_param_shared_control | 0.947967 | 0.947967 | 0.984791 | 0.163556 | 0.025523 | 5 | 10 | -0.011789 | 0.008436 |
| domain_bias_only_control | domain_bias_control | 0.944698 | 0.944715 | 0.986875 | 0.156295 | 0.041677 | 0 | 7 | -0.016841 | -0.008579 |
| r6i_true_domain_h_final_adapter | primary | 0.941463 | 0.941463 | 0.982041 | 0.168870 | 0.024718 | 6 | 15 | -0.021323 | -0.000325 |
| random_domain_h_final_adapter_control | random_domain_control | 0.939837 | 0.939837 | 0.980381 | 0.172006 | 0.021741 | 5 | 15 | -0.023739 | -0.000325 |

Decision reasons:
- best_primary_below_original_final
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
