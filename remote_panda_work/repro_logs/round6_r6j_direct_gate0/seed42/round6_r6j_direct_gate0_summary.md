# Round 6 R6-J Direct Gate-0 Summary

Decision: `No-Go`

Scope: direct D2/D3 self-suppressed non-self source-mixture frozen probe; train/val only; no test; no training.

| Split | View | Role | F1 | Acc | AUC | CE | W2C | C2W | EffSrc | SelfW | CorrAlphaNegRegret |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | original_final | primary_baseline | 1.000000 | 1.000000 | 1.000000 | 0.000260 | 0 | 0 | nan | nan | nan |
| train | pad_soft_nonself_tau0p5 | primary | 1.000000 | 1.000000 | 1.000000 | 0.000247 | 0 | 0 | 7.999 | 0.000000 | -0.049264 |
| train | pad_soft_nonself_tau1p0 | primary | 1.000000 | 1.000000 | 1.000000 | 0.000247 | 0 | 0 | 8.000 | 0.000000 | -0.049243 |
| train | pad_soft_nonself_tau2p0 | primary | 1.000000 | 1.000000 | 1.000000 | 0.000247 | 0 | 0 | 8.000 | 0.000000 | -0.049232 |
| train | pad_top2_nonself_uniform | primary | 1.000000 | 1.000000 | 1.000000 | 0.000258 | 0 | 0 | 2.000 | 0.000000 | -0.044166 |
| train | uniform_nonself_control | uniform_control | 1.000000 | 1.000000 | 1.000000 | 0.000247 | 0 | 0 | 8.000 | 0.000000 | nan |
| train | self_only_control | self_control | 1.000000 | 1.000000 | 1.000000 | 0.000261 | 0 | 0 | 1.000 | 1.000000 | nan |
| train | pad_bottom2_nonself_uniform | bottom_control | 1.000000 | 1.000000 | 1.000000 | 0.000247 | 0 | 0 | 2.000 | 0.000000 | 0.004201 |
| train | shuffled_pad_top2_uniform | shuffled_control | 1.000000 | 1.000000 | 1.000000 | 0.000256 | 0 | 0 | 2.000 | 0.000000 | -0.034654 |
| train | anchor_pair_uniform_recompute | anchor_recompute_control | 1.000000 | 1.000000 | 1.000000 | 0.000260 | 0 | 0 | 2.000 | 0.500000 | -0.035778 |
| train | random_nonself_pair_seed1 | random_control | 1.000000 | 1.000000 | 1.000000 | 0.000248 | 0 | 0 | 2.000 | 0.000000 | -0.002075 |
| train | random_nonself_pair_seed2 | random_control | 1.000000 | 1.000000 | 1.000000 | 0.000250 | 0 | 0 | 2.000 | 0.000000 | -0.008890 |
| train | random_nonself_pair_seed3 | random_control | 1.000000 | 1.000000 | 1.000000 | 0.000248 | 0 | 0 | 2.000 | 0.000000 | 0.001076 |
| val | random_nonself_pair_seed2 | random_control | 0.957715 | 0.957724 | 0.987530 | 0.158172 | 1 | 0 | 2.000 | 0.000000 | -0.003108 |
| val | shuffled_pad_top2_uniform | shuffled_control | 0.956090 | 0.956098 | 0.987784 | 0.156850 | 1 | 1 | 2.000 | 0.000000 | 0.022863 |
| val | original_final | primary_baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0 | 0 | nan | nan | nan |
| val | pad_soft_nonself_tau0p5 | primary | 0.956086 | 0.956098 | 0.987636 | 0.157973 | 0 | 0 | 7.999 | 0.000000 | 0.018818 |
| val | pad_soft_nonself_tau1p0 | primary | 0.956086 | 0.956098 | 0.987647 | 0.157977 | 0 | 0 | 8.000 | 0.000000 | 0.018817 |
| val | pad_soft_nonself_tau2p0 | primary | 0.956086 | 0.956098 | 0.987647 | 0.157978 | 0 | 0 | 8.000 | 0.000000 | 0.018817 |
| val | uniform_nonself_control | uniform_control | 0.956086 | 0.956098 | 0.987647 | 0.157980 | 0 | 0 | 8.000 | 0.000000 | nan |
| val | self_only_control | self_control | 0.956086 | 0.956098 | 0.987478 | 0.158469 | 0 | 0 | 1.000 | 1.000000 | nan |
| val | pad_bottom2_nonself_uniform | bottom_control | 0.956086 | 0.956098 | 0.987668 | 0.158167 | 0 | 0 | 2.000 | 0.000000 | -0.004035 |
| val | anchor_pair_uniform_recompute | anchor_recompute_control | 0.956086 | 0.956098 | 0.987377 | 0.158352 | 0 | 0 | 2.000 | 0.500000 | -0.003179 |
| val | random_nonself_pair_seed1 | random_control | 0.956086 | 0.956098 | 0.987615 | 0.158438 | 1 | 1 | 2.000 | 0.000000 | -0.006711 |
| val | random_nonself_pair_seed3 | random_control | 0.956086 | 0.956098 | 0.987753 | 0.157321 | 0 | 0 | 2.000 | 0.000000 | 0.012500 |
| val | pad_top2_nonself_uniform | primary | 0.954462 | 0.954472 | 0.987467 | 0.157782 | 0 | 1 | 2.000 | 0.000000 | 0.005979 |

Decision reasons:
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
