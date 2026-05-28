# Round 6 R6-G Direct Gate-0 Summary

Decision: `No-Go`

Scope: direct D2/D3 soft/EMA prototype frozen probe; train/val only; no test; no training.

| Split | View | Role | F1 | Acc | AUC | CE | W2C | C2W | OverlapPAD |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | original_final | primary_baseline | 1.000000 | 1.000000 | nan | 0.000249 | 0 | 0 | 1.000 |
| train | current_pad_top2_nonself | hard_pad_control | 1.000000 | 1.000000 | nan | 0.000240 | 0 | 0 | 1.000 |
| train | current_pad_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | nan | 0.000256 | 0 | 0 | 0.000 |
| train | learned_hard_min_top2_nonself | hard_feature_control | 1.000000 | 1.000000 | nan | 0.000247 | 0 | 0 | 0.500 |
| train | learned_hard_min_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | nan | 0.000267 | 0 | 0 | 0.023 |
| train | learned_softmin_top2_nonself | primary | 1.000000 | 1.000000 | nan | 0.000247 | 0 | 0 | 0.492 |
| train | learned_softmin_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | nan | 0.000274 | 0 | 0 | 0.000 |
| train | learned_logsumexp_top2_nonself | primary | 1.000000 | 1.000000 | nan | 0.000244 | 0 | 0 | 0.477 |
| train | learned_logsumexp_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | nan | 0.000274 | 0 | 0 | 0.000 |
| train | train_domain_mean_top2_nonself | primary | 1.000000 | 1.000000 | nan | 0.000235 | 0 | 0 | 0.219 |
| train | class_shuffled_domain_mean_top2_nonself | prototype_control | 1.000000 | 1.000000 | nan | 0.000258 | 0 | 0 | 0.203 |
| train | random_domain_mean_top2_nonself | prototype_control | 1.000000 | 1.000000 | nan | 0.000235 | 0 | 0 | 0.477 |
| train | shuffled_pad_top2_nonself | shuffled_control | 1.000000 | 1.000000 | nan | 0.000231 | 0 | 0 | 0.633 |
| train | random_nonself_pair_seed1 | random_control | 1.000000 | 1.000000 | nan | 0.000238 | 0 | 0 | 0.234 |
| train | random_nonself_pair_seed2 | random_control | 1.000000 | 1.000000 | nan | 0.000248 | 0 | 0 | 0.266 |
| train | random_nonself_pair_seed3 | random_control | 1.000000 | 1.000000 | nan | 0.000249 | 0 | 0 | 0.250 |
| val | original_final | primary_baseline | 0.496063 | 0.984375 | nan | 0.043958 | 0 | 0 | 1.000 |
| val | current_pad_top2_nonself | hard_pad_control | 0.496063 | 0.984375 | nan | 0.042990 | 0 | 0 | 1.000 |
| val | current_pad_bottom2_nonself | bottom_control | 0.496063 | 0.984375 | nan | 0.044527 | 0 | 0 | 0.000 |
| val | learned_hard_min_top2_nonself | hard_feature_control | 0.496063 | 0.984375 | nan | 0.043866 | 0 | 0 | 0.484 |
| val | learned_hard_min_bottom2_nonself | bottom_control | 0.496063 | 0.984375 | nan | 0.045932 | 0 | 0 | 0.031 |
| val | learned_softmin_top2_nonself | primary | 0.496063 | 0.984375 | nan | 0.043923 | 0 | 0 | 0.508 |
| val | learned_softmin_bottom2_nonself | bottom_control | 0.496063 | 0.984375 | nan | 0.047332 | 0 | 0 | 0.000 |
| val | learned_logsumexp_top2_nonself | primary | 0.496063 | 0.984375 | nan | 0.043901 | 0 | 0 | 0.500 |
| val | learned_logsumexp_bottom2_nonself | bottom_control | 0.496063 | 0.984375 | nan | 0.047333 | 0 | 0 | 0.000 |
| val | train_domain_mean_top2_nonself | primary | 0.496063 | 0.984375 | nan | 0.041074 | 0 | 0 | 0.242 |
| val | class_shuffled_domain_mean_top2_nonself | prototype_control | 0.496063 | 0.984375 | nan | 0.048043 | 0 | 0 | 0.086 |
| val | random_domain_mean_top2_nonself | prototype_control | 0.496063 | 0.984375 | nan | 0.041615 | 0 | 0 | 0.422 |
| val | shuffled_pad_top2_nonself | shuffled_control | 0.496063 | 0.984375 | nan | 0.041471 | 0 | 0 | 0.719 |
| val | random_nonself_pair_seed1 | random_control | 0.496063 | 0.984375 | nan | 0.042181 | 0 | 0 | 0.250 |
| val | random_nonself_pair_seed2 | random_control | 0.496063 | 0.984375 | nan | 0.043286 | 0 | 0 | 0.258 |
| val | random_nonself_pair_seed3 | random_control | 0.496063 | 0.984375 | nan | 0.044039 | 0 | 0 | 0.273 |

Decision reasons:
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
