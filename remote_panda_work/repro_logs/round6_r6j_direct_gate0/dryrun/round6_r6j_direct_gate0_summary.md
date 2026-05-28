# Round 6 R6-J Direct Gate-0 Summary

Decision: `No-Go`

Scope: direct D2/D3 self-suppressed non-self source-mixture frozen probe; train/val only; no test; no training.

| Split | View | Role | F1 | Acc | AUC | CE | W2C | C2W | EffSrc | SelfW | CorrAlphaNegRegret |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | original_final | primary_baseline | 1.000000 | 1.000000 | nan | 0.000249 | 0 | 0 | nan | nan | nan |
| train | pad_soft_nonself_tau0p5 | primary | 1.000000 | 1.000000 | nan | 0.000243 | 0 | 0 | 7.999 | 0.000000 | 0.029838 |
| train | pad_soft_nonself_tau1p0 | primary | 1.000000 | 1.000000 | nan | 0.000243 | 0 | 0 | 8.000 | 0.000000 | 0.029903 |
| train | pad_soft_nonself_tau2p0 | primary | 1.000000 | 1.000000 | nan | 0.000243 | 0 | 0 | 8.000 | 0.000000 | 0.029934 |
| train | pad_top2_nonself_uniform | primary | 1.000000 | 1.000000 | nan | 0.000240 | 0 | 0 | 2.000 | 0.000000 | 0.027057 |
| train | uniform_nonself_control | uniform_control | 1.000000 | 1.000000 | nan | 0.000243 | 0 | 0 | 8.000 | 0.000000 | nan |
| train | self_only_control | self_control | 1.000000 | 1.000000 | nan | 0.000259 | 0 | 0 | 1.000 | 1.000000 | nan |
| train | pad_bottom2_nonself_uniform | bottom_control | 1.000000 | 1.000000 | nan | 0.000256 | 0 | 0 | 2.000 | 0.000000 | -0.063397 |
| train | shuffled_pad_top2_uniform | shuffled_control | 1.000000 | 1.000000 | nan | 0.000231 | 0 | 0 | 2.000 | 0.000000 | 0.083023 |
| train | anchor_pair_uniform_recompute | anchor_recompute_control | 1.000000 | 1.000000 | nan | 0.000248 | 0 | 0 | 2.000 | 0.500000 | 0.021260 |
| train | random_nonself_pair_seed1 | random_control | 1.000000 | 1.000000 | nan | 0.000238 | 0 | 0 | 2.000 | 0.000000 | 0.037526 |
| train | random_nonself_pair_seed2 | random_control | 1.000000 | 1.000000 | nan | 0.000248 | 0 | 0 | 2.000 | 0.000000 | -0.020101 |
| train | random_nonself_pair_seed3 | random_control | 1.000000 | 1.000000 | nan | 0.000249 | 0 | 0 | 2.000 | 0.000000 | -0.023223 |
| val | original_final | primary_baseline | 0.496063 | 0.984375 | nan | 0.043958 | 0 | 0 | nan | nan | nan |
| val | pad_soft_nonself_tau0p5 | primary | 0.496063 | 0.984375 | nan | 0.043115 | 0 | 0 | 7.999 | 0.000000 | 0.039608 |
| val | pad_soft_nonself_tau1p0 | primary | 0.496063 | 0.984375 | nan | 0.043119 | 0 | 0 | 8.000 | 0.000000 | 0.039669 |
| val | pad_soft_nonself_tau2p0 | primary | 0.496063 | 0.984375 | nan | 0.043121 | 0 | 0 | 8.000 | 0.000000 | 0.039699 |
| val | pad_top2_nonself_uniform | primary | 0.496063 | 0.984375 | nan | 0.042990 | 0 | 0 | 2.000 | 0.000000 | 0.012863 |
| val | uniform_nonself_control | uniform_control | 0.496063 | 0.984375 | nan | 0.043123 | 0 | 0 | 8.000 | 0.000000 | nan |
| val | self_only_control | self_control | 0.496063 | 0.984375 | nan | 0.045070 | 0 | 0 | 1.000 | 1.000000 | nan |
| val | pad_bottom2_nonself_uniform | bottom_control | 0.496063 | 0.984375 | nan | 0.044529 | 0 | 0 | 2.000 | 0.000000 | -0.052978 |
| val | shuffled_pad_top2_uniform | shuffled_control | 0.496063 | 0.984375 | nan | 0.041475 | 0 | 0 | 2.000 | 0.000000 | 0.076863 |
| val | anchor_pair_uniform_recompute | anchor_recompute_control | 0.496063 | 0.984375 | nan | 0.043951 | 0 | 0 | 2.000 | 0.500000 | 0.010185 |
| val | random_nonself_pair_seed1 | random_control | 0.496063 | 0.984375 | nan | 0.042180 | 0 | 0 | 2.000 | 0.000000 | 0.043105 |
| val | random_nonself_pair_seed2 | random_control | 0.496063 | 0.984375 | nan | 0.043281 | 0 | 0 | 2.000 | 0.000000 | -0.007555 |
| val | random_nonself_pair_seed3 | random_control | 0.496063 | 0.984375 | nan | 0.044042 | 0 | 0 | 2.000 | 0.000000 | -0.029985 |

Decision reasons:
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
