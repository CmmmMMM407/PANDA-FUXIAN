# Round 6 R6-G Direct Gate-0 Summary

Decision: `No-Go`

Scope: direct D2/D3 soft/EMA prototype frozen probe; train/val only; no test; no training.

| Split | View | Role | F1 | Acc | AUC | CE | W2C | C2W | OverlapPAD |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | original_final | primary_baseline | 1.000000 | 1.000000 | 1.000000 | 0.000260 | 0 | 0 | 1.000 |
| train | current_pad_top2_nonself | hard_pad_control | 1.000000 | 1.000000 | 1.000000 | 0.000258 | 0 | 0 | 1.000 |
| train | current_pad_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | 1.000000 | 0.000247 | 0 | 0 | 0.000 |
| train | learned_hard_min_top2_nonself | hard_feature_control | 1.000000 | 1.000000 | 1.000000 | 0.000249 | 0 | 0 | 0.489 |
| train | learned_hard_min_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | 1.000000 | 0.000242 | 0 | 0 | 0.040 |
| train | learned_softmin_top2_nonself | primary | 1.000000 | 1.000000 | 1.000000 | 0.000250 | 0 | 0 | 0.475 |
| train | learned_softmin_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | 1.000000 | 0.000244 | 0 | 0 | 0.000 |
| train | learned_logsumexp_top2_nonself | primary | 1.000000 | 1.000000 | 1.000000 | 0.000249 | 0 | 0 | 0.451 |
| train | learned_logsumexp_bottom2_nonself | bottom_control | 1.000000 | 1.000000 | 1.000000 | 0.000244 | 0 | 0 | 0.000 |
| train | train_domain_mean_top2_nonself | primary | 1.000000 | 1.000000 | 1.000000 | 0.000255 | 0 | 0 | 0.213 |
| train | class_shuffled_domain_mean_top2_nonself | prototype_control | 1.000000 | 1.000000 | 1.000000 | 0.000262 | 0 | 0 | 0.218 |
| train | random_domain_mean_top2_nonself | prototype_control | 1.000000 | 1.000000 | 1.000000 | 0.000236 | 0 | 0 | 0.218 |
| train | shuffled_pad_top2_nonself | shuffled_control | 1.000000 | 1.000000 | 1.000000 | 0.000256 | 0 | 0 | 0.845 |
| train | random_nonself_pair_seed1 | random_control | 1.000000 | 1.000000 | 1.000000 | 0.000248 | 0 | 0 | 0.254 |
| train | random_nonself_pair_seed2 | random_control | 1.000000 | 1.000000 | 1.000000 | 0.000250 | 0 | 0 | 0.249 |
| train | random_nonself_pair_seed3 | random_control | 1.000000 | 1.000000 | 1.000000 | 0.000248 | 0 | 0 | 0.248 |
| val | random_nonself_pair_seed2 | random_control | 0.957715 | 0.957724 | 0.987530 | 0.158171 | 1 | 0 | 0.267 |
| val | shuffled_pad_top2_nonself | shuffled_control | 0.956090 | 0.956098 | 0.987784 | 0.156850 | 1 | 1 | 0.820 |
| val | original_final | primary_baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0 | 0 | 1.000 |
| val | current_pad_bottom2_nonself | bottom_control | 0.956086 | 0.956098 | 0.987668 | 0.158167 | 0 | 0 | 0.000 |
| val | learned_hard_min_top2_nonself | hard_feature_control | 0.956086 | 0.956098 | 0.987594 | 0.158318 | 0 | 0 | 0.489 |
| val | learned_softmin_top2_nonself | primary | 0.956086 | 0.956098 | 0.987636 | 0.158106 | 0 | 0 | 0.489 |
| val | learned_logsumexp_top2_nonself | primary | 0.956086 | 0.956098 | 0.987636 | 0.158077 | 0 | 0 | 0.471 |
| val | train_domain_mean_top2_nonself | primary | 0.956086 | 0.956098 | 0.987753 | 0.157737 | 0 | 0 | 0.203 |
| val | random_nonself_pair_seed1 | random_control | 0.956086 | 0.956098 | 0.987594 | 0.158443 | 1 | 1 | 0.247 |
| val | random_nonself_pair_seed3 | random_control | 0.956086 | 0.956098 | 0.987753 | 0.157322 | 0 | 0 | 0.243 |
| val | learned_hard_min_bottom2_nonself | bottom_control | 0.956081 | 0.956098 | 0.987647 | 0.158688 | 1 | 1 | 0.039 |
| val | learned_softmin_bottom2_nonself | bottom_control | 0.956081 | 0.956098 | 0.987742 | 0.158787 | 1 | 1 | 0.000 |
| val | learned_logsumexp_bottom2_nonself | bottom_control | 0.956081 | 0.956098 | 0.987742 | 0.158787 | 1 | 1 | 0.000 |
| val | random_domain_mean_top2_nonself | prototype_control | 0.956081 | 0.956098 | 0.987705 | 0.159400 | 1 | 1 | 0.189 |
| val | current_pad_top2_nonself | hard_pad_control | 0.954462 | 0.954472 | 0.987467 | 0.157783 | 0 | 1 | 1.000 |
| val | class_shuffled_domain_mean_top2_nonself | prototype_control | 0.954462 | 0.954472 | 0.987700 | 0.157487 | 0 | 1 | 0.212 |

Decision reasons:
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
