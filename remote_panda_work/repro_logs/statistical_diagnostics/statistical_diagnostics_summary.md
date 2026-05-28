# Statistical Diagnostics Summary

Paired hierarchical bootstrap resamples seeds and matched samples within seed. Positive deltas mean PANDA minus the compared baseline.

## Match Coverage

| dataset | model_a | model_b | n_model_a | n_model_b | n_matched | match_rate_vs_min |
| --- | --- | --- | --- | --- | --- | --- |
| weibo21 | PANDA | DAMMFND | 1845 | 1845 | 1845 | 1.0 |
| weibo21 | PANDA | MMDFND | 1845 | 1845 | 1845 | 1.0 |
| weibo | PANDA | DAMMFND | 4395 | 4395 | 4395 | 1.0 |
| weibo | PANDA | MMDFND | 4395 | 4395 | 4395 | 1.0 |


## Main Metric Paired Bootstrap

| dataset | model_a | model_b | metric | model_a_value | model_b_value | delta_a_minus_b | ci95_low | ci95_high | bootstrap_p_two_sided | n_matched | n_seeds | a_correct_b_wrong | a_wrong_b_correct | mcnemar_exact_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weibo21 | PANDA | DAMMFND | macro_f1 | 0.947425 | 0.943613 | 0.003812 | -0.011420 | 0.020132 | 0.660000 | 1845 | 3 | 43 | 36 | 0.499897 |
| weibo21 | PANDA | DAMMFND | accuracy | 0.947425 | 0.943631 | 0.003794 | -0.011382 | 0.020054 | 0.699000 | 1845 | 3 | 43 | 36 | 0.499897 |
| weibo21 | PANDA | DAMMFND | auc | 0.987512 | 0.983784 | 0.003728 | -0.002848 | 0.011278 | 0.349000 | 1845 | 3 | 43 | 36 | 0.499897 |
| weibo21 | PANDA | MMDFND | macro_f1 | 0.947425 | 0.926235 | 0.021190 | 0.008536 | 0.034215 | 0.000000 | 1845 | 3 | 76 | 37 | 0.000310 |
| weibo21 | PANDA | MMDFND | accuracy | 0.947425 | 0.926287 | 0.021138 | 0.008659 | 0.034146 | 0.000000 | 1845 | 3 | 76 | 37 | 0.000310 |
| weibo21 | PANDA | MMDFND | auc | 0.987512 | 0.964021 | 0.023491 | 0.013111 | 0.033530 | 0.000000 | 1845 | 3 | 76 | 37 | 0.000310 |
| weibo | PANDA | DAMMFND | macro_f1 | 0.941521 | 0.937423 | 0.004098 | -0.003875 | 0.012062 | 0.296000 | 4395 | 3 | 119 | 101 | 0.251682 |
| weibo | PANDA | DAMMFND | accuracy | 0.941524 | 0.937429 | 0.004096 | -0.003874 | 0.012059 | 0.313000 | 4395 | 3 | 119 | 101 | 0.251682 |
| weibo | PANDA | DAMMFND | auc | 0.986145 | 0.983820 | 0.002325 | -0.002161 | 0.005526 | 0.396000 | 4395 | 3 | 119 | 101 | 0.251682 |
| weibo | PANDA | MMDFND | macro_f1 | 0.941521 | 0.909421 | 0.032099 | 0.008643 | 0.052973 | 0.000000 | 4395 | 3 | 236 | 95 | 0.000000 |
| weibo | PANDA | MMDFND | accuracy | 0.941524 | 0.909443 | 0.032082 | 0.008641 | 0.052787 | 0.000000 | 4395 | 3 | 236 | 95 | 0.000000 |
| weibo | PANDA | MMDFND | auc | 0.986145 | 0.966985 | 0.019160 | 0.008416 | 0.026083 | 0.000000 | 4395 | 3 | 236 | 95 | 0.000000 |


## Reliability Metric Paired Bootstrap

| dataset | model_a | model_b | metric | model_a_value | model_b_value | delta_a_minus_b | ci95_low | ci95_high | bootstrap_p_two_sided | n_matched | n_seeds | a_correct_b_wrong | a_wrong_b_correct | mcnemar_exact_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weibo21 | PANDA | DAMMFND | ece | 0.022165 | 0.028612 | -0.006447 | -0.021186 | 0.006543 | 0.401000 | 1845 | 3 | 43 | 36 | 0.499897 |
| weibo21 | PANDA | DAMMFND | brier | 0.041818 | 0.047604 | -0.005786 | -0.020112 | 0.006994 | 0.454000 | 1845 | 3 | 43 | 36 | 0.499897 |
| weibo21 | PANDA | DAMMFND | hce_rate | 0.023306 | 0.029268 | -0.005962 | -0.019512 | 0.005420 | 0.410000 | 1845 | 3 | 43 | 36 | 0.499897 |
| weibo21 | PANDA | MMDFND | ece | 0.022165 | 0.051278 | -0.029113 | -0.039950 | -0.015623 | 0.000000 | 1845 | 3 | 76 | 37 | 0.000310 |
| weibo21 | PANDA | MMDFND | brier | 0.041818 | 0.065641 | -0.023823 | -0.033814 | -0.013839 | 0.000000 | 1845 | 3 | 76 | 37 | 0.000310 |
| weibo21 | PANDA | MMDFND | hce_rate | 0.023306 | 0.048780 | -0.025474 | -0.034688 | -0.016802 | 0.000000 | 1845 | 3 | 76 | 37 | 0.000310 |
| weibo | PANDA | DAMMFND | ece | 0.020533 | 0.029470 | -0.008937 | -0.020142 | 0.002190 | 0.132000 | 4395 | 3 | 119 | 101 | 0.251682 |
| weibo | PANDA | DAMMFND | brier | 0.044000 | 0.049037 | -0.005037 | -0.013323 | 0.001796 | 0.177000 | 4395 | 3 | 119 | 101 | 0.251682 |
| weibo | PANDA | DAMMFND | hce_rate | 0.019568 | 0.027076 | -0.007509 | -0.019113 | 0.001138 | 0.117000 | 4395 | 3 | 119 | 101 | 0.251682 |
| weibo | PANDA | MMDFND | ece | 0.020533 | 0.046290 | -0.025757 | -0.039568 | -0.014101 | 0.000000 | 4395 | 3 | 236 | 95 | 0.000000 |
| weibo | PANDA | MMDFND | brier | 0.044000 | 0.072187 | -0.028188 | -0.038436 | -0.016090 | 0.000000 | 4395 | 3 | 236 | 95 | 0.000000 |
| weibo | PANDA | MMDFND | hce_rate | 0.019568 | 0.043003 | -0.023436 | -0.036633 | -0.009101 | 0.000000 | 4395 | 3 | 236 | 95 | 0.000000 |


## Uncertainty / HCE Gate Extract

| dataset | split | score | target | pooled_auc | bootstrap_ci95_low | bootstrap_ci95_high | permutation_greater_equal_p | top25_rate | bottom25_rate | enrichment | smoothed_odds_ratio | fisher_exact_greater_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weibo | val | clip_dissimilarity | is_error | 0.508726 | 0.467564 | 0.553449 | 0.073090 |  |  |  |  |  |
| weibo | val | clip_dissimilarity | is_high_conf_error | 0.471470 | 0.406472 | 0.539816 | 0.475083 | 0.022117 | 0.030016 | 0.736842 | 0.737588 | 0.855098 |
| weibo | val | full_conflict_zscore_equal_weight | is_error | 0.746337 | 0.701809 | 0.785084 | 0.003322 |  |  |  |  |  |
| weibo | val | full_conflict_zscore_equal_weight | is_high_conf_error | 0.562269 | 0.504535 | 0.629163 | 0.049834 | 0.037915 | 0.020537 | 1.846154 | 1.847568 | 0.046975 |
| weibo | val | confidence_uncertainty | is_error | 0.858851 | 0.832866 | 0.878864 | 0.003322 |  |  |  |  |  |
| weibo | val | confidence_uncertainty | is_high_conf_error | 0.725799 | 0.689087 | 0.758610 | 0.003322 | 0.052133 | 0.000000 | 52132701421.800949 | 70.681932 | 0.000000 |
| weibo | val | random_conflict_negative_control | is_error | 0.449419 | 0.402908 | 0.502459 | 0.963455 |  |  |  |  |  |
| weibo | val | random_conflict_negative_control | is_high_conf_error | 0.427262 | 0.366622 | 0.499047 | 0.966777 | 0.022117 | 0.044234 | 0.500000 | 0.497274 | 0.991216 |
| weibo21 | val | clip_dissimilarity | is_error | 0.531447 | 0.462898 | 0.589663 | 0.172757 |  |  |  |  |  |
| weibo21 | val | clip_dissimilarity | is_high_conf_error | 0.516496 | 0.442878 | 0.611438 | 0.372093 | 0.029724 | 0.023810 | 1.248408 | 1.244334 | 0.361297 |
| weibo21 | val | full_conflict_zscore_equal_weight | is_error | 0.851451 | 0.818770 | 0.885317 | 0.003322 |  |  |  |  |  |
| weibo21 | val | full_conflict_zscore_equal_weight | is_high_conf_error | 0.777872 | 0.728369 | 0.822659 | 0.003322 | 0.071429 | 0.000000 | 71428571428.571426 | 72.147846 | 0.000000 |
| weibo21 | val | confidence_uncertainty | is_error | 0.876793 | 0.845559 | 0.907702 | 0.003322 |  |  |  |  |  |
| weibo21 | val | confidence_uncertainty | is_high_conf_error | 0.773025 | 0.739909 | 0.805636 | 0.003322 | 0.069264 | 0.000000 | 69264069264.069260 | 69.831591 | 0.000000 |
| weibo21 | val | random_conflict_negative_control | is_error | 0.460049 | 0.405615 | 0.510292 | 0.887043 |  |  |  |  |  |
| weibo21 | val | random_conflict_negative_control | is_high_conf_error | 0.457649 | 0.389126 | 0.521796 | 0.860465 | 0.008658 | 0.019481 | 0.444444 | 0.468519 | 0.954992 |
| weibo | test | clip_dissimilarity | is_error | 0.474813 | 0.434177 | 0.506580 | 0.730897 |  |  |  |  |  |
| weibo | test | clip_dissimilarity | is_high_conf_error | 0.470237 | 0.412362 | 0.525591 | 0.594684 | 0.016260 | 0.018919 | 0.859466 | 0.860465 | 0.737880 |
| weibo | test | full_conflict_zscore_equal_weight | is_error | 0.800720 | 0.772203 | 0.827700 | 0.003322 |  |  |  |  |  |
| weibo | test | full_conflict_zscore_equal_weight | is_high_conf_error | 0.573065 | 0.518914 | 0.629881 | 0.006645 | 0.025478 | 0.012739 | 2.000000 | 1.991198 | 0.020789 |
| weibo | test | confidence_uncertainty | is_error | 0.893252 | 0.869404 | 0.911475 | 0.003322 |  |  |  |  |  |
| weibo | test | confidence_uncertainty | is_high_conf_error | 0.712338 | 0.671880 | 0.761798 | 0.003322 | 0.050045 | 0.002730 | 18.333333 | 16.646584 | 0.000000 |
| weibo | test | random_conflict_negative_control | is_error | 0.523029 | 0.484903 | 0.557911 | 0.122924 |  |  |  |  |  |
| weibo | test | random_conflict_negative_control | is_high_conf_error | 0.554785 | 0.496813 | 0.621451 | 0.069767 | 0.018198 | 0.012739 | 1.428571 | 1.421651 | 0.193905 |
| weibo21 | test | clip_dissimilarity | is_error | 0.557229 | 0.496852 | 0.614434 | 0.046512 |  |  |  |  |  |
| weibo21 | test | clip_dissimilarity | is_high_conf_error | 0.568761 | 0.493144 | 0.650389 | 0.122924 | 0.027957 | 0.015054 | 1.857143 | 1.823867 | 0.128981 |
| weibo21 | test | full_conflict_zscore_equal_weight | is_error | 0.819971 | 0.778797 | 0.859669 | 0.003322 |  |  |  |  |  |
| weibo21 | test | full_conflict_zscore_equal_weight | is_high_conf_error | 0.713522 | 0.648190 | 0.772134 | 0.003322 | 0.047619 | 0.004329 | 11.000000 | 9.408627 | 0.000015 |
| weibo21 | test | confidence_uncertainty | is_error | 0.901289 | 0.878808 | 0.922548 | 0.003322 |  |  |  |  |  |
| weibo21 | test | confidence_uncertainty | is_high_conf_error | 0.786413 | 0.748389 | 0.823502 | 0.003322 | 0.062771 | 0.000000 | 62770562770.562767 | 62.946943 | 0.000000 |
| weibo21 | test | random_conflict_negative_control | is_error | 0.501103 | 0.434137 | 0.560312 | 0.534884 |  |  |  |  |  |
| weibo21 | test | random_conflict_negative_control | is_high_conf_error | 0.464845 | 0.377392 | 0.547499 | 0.787375 | 0.019481 | 0.025974 | 0.750000 | 0.754972 | 0.811110 |

