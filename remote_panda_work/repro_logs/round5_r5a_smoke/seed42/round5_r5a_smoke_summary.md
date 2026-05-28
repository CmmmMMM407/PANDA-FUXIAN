# Round 5 R5-A Smoke Summary

Decision: `No-Go`

Rules: train/val only; test was not exported, opened, or analyzed. G0-B/G0-C and source/prompt/reliability/offline-boundary routes are superseded/excluded.

| Tag | F1 | Acc | AUC | ECE | Brier | HCE | Weak F1 | Image Conflict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aux_weight_2p0 | 0.939837 | 0.939837 | 0.981407 | 0.011093 | 0.048196 | 0.019512 | 0.922130 | 0.024675 |
| deterministic_train_l0 | 0.938175 | 0.938211 | 0.980910 | 0.032676 | 0.052929 | 0.026016 | 0.896274 | 0.106494 |
| same_budget_noop_l0 | 0.938175 | 0.938211 | 0.980910 | 0.032676 | 0.052929 | 0.026016 | 0.896274 | 0.106494 |
| aux_weight_0p0 | 0.936585 | 0.936585 | 0.983765 | 0.032488 | 0.047806 | 0.024390 | 0.903966 | 0.576623 |
| r5a_image_project_l1p0 | 0.936504 | 0.936585 | 0.982136 | 0.026180 | 0.052733 | 0.027642 | 0.913690 | 0.058442 |
| aux_weight_0p5 | 0.933333 | 0.933333 | 0.983659 | 0.025495 | 0.051455 | 0.019512 | 0.895433 | 0.072727 |
| generic_pcgrad_l1p0 | 0.928337 | 0.928455 | 0.980349 | 0.022960 | 0.055912 | 0.022764 | 0.913690 | 0.092208 |
| generic_cagrad_l1p0 | 0.926655 | 0.926829 | 0.981618 | 0.020364 | 0.056647 | 0.022764 | 0.913767 | 0.061039 |
| aux_weight_1p5 | 0.925201 | 0.925203 | 0.982062 | 0.023688 | 0.050793 | 0.019512 | 0.922269 | 0.018182 |
| random_sign_l1p0 | 0.921905 | 0.921951 | 0.982750 | 0.030140 | 0.058681 | 0.019512 | 0.895433 | 0.040260 |

Reasons:

- primary_below_deterministic_train
- primary_not_above_best_control
