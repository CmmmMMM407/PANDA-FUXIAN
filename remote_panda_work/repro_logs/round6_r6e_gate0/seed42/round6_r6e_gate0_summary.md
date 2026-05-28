# Round 6 R6-E Gate-0 Summary

Decision: `No-Go`

| Candidate | Role | Coverage | F1 | Acc | AUC | W2C | C2W |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| branch_consensus_cov1 | primary | 0.730 | 0.956086 | 0.956098 | 0.984167 | 0 | 0 |
| max_branch_confidence_cov0.8 | primary | 0.489 | 0.956086 | 0.956098 | 0.986356 | 0 | 0 |
| fusion_confidence_cov0.8 | primary | 0.486 | 0.956086 | 0.956098 | 0.988154 | 0 | 0 |
| branch_consensus_cov0.8 | primary | 0.416 | 0.956086 | 0.956098 | 0.985701 | 0 | 0 |
| max_branch_confidence_cov0.5 | primary | 0.301 | 0.956086 | 0.956098 | 0.986039 | 0 | 0 |
| fusion_confidence_cov0.5 | primary | 0.265 | 0.956086 | 0.956098 | 0.987975 | 0 | 0 |
| branch_consensus_cov0.5 | primary | 0.254 | 0.956086 | 0.956098 | 0.985574 | 0 | 0 |
| max_branch_confidence_cov0.3 | primary | 0.167 | 0.956086 | 0.956098 | 0.987541 | 0 | 0 |
| branch_consensus_cov0.3 | primary | 0.141 | 0.956086 | 0.956098 | 0.987467 | 0 | 0 |
| fusion_confidence_cov0.3 | primary | 0.133 | 0.956086 | 0.956098 | 0.987647 | 0 | 0 |
| fusion_confidence_cov0.2 | primary | 0.101 | 0.956086 | 0.956098 | 0.987615 | 0 | 0 |
| max_branch_confidence_cov0.2 | primary | 0.098 | 0.956086 | 0.956098 | 0.987425 | 0 | 0 |
| branch_consensus_cov0.2 | primary | 0.083 | 0.956086 | 0.956098 | 0.987414 | 0 | 0 |
| max_branch_confidence_cov0.1 | primary | 0.047 | 0.956086 | 0.956098 | 0.987382 | 0 | 0 |
| shuffled_confidence_cov0.1 | shuffled_confidence_control | 0.047 | 0.956086 | 0.956098 | 0.987657 | 0 | 0 |
| fusion_confidence_cov0.1 | primary | 0.046 | 0.956086 | 0.956098 | 0.987446 | 0 | 0 |
| branch_consensus_cov0.1 | primary | 0.039 | 0.956086 | 0.956098 | 0.987372 | 0 | 0 |
| always_final | baseline | 0.000 | 0.956086 | 0.956098 | 0.987372 | 0 | 0 |
| shuffled_confidence_cov0.2 | shuffled_confidence_control | 0.098 | 0.954457 | 0.954472 | 0.985394 | 1 | 2 |
| shuffled_confidence_cov0.3 | shuffled_confidence_control | 0.167 | 0.952828 | 0.952846 | 0.984336 | 1 | 3 |
| shuffled_confidence_cov0.8 | shuffled_confidence_control | 0.489 | 0.949574 | 0.949593 | 0.981216 | 3 | 7 |
| shuffled_confidence_cov0.5 | shuffled_confidence_control | 0.301 | 0.949574 | 0.949593 | 0.980508 | 1 | 5 |
| max_branch_confidence_cov1 | primary | 0.902 | 0.949559 | 0.949593 | 0.980698 | 1 | 5 |
| always_exit_p_fusion | always_exit_control | 1.000 | 0.947956 | 0.947967 | 0.988049 | 2 | 7 |
| fusion_confidence_cov1 | primary | 1.000 | 0.947956 | 0.947967 | 0.988049 | 2 | 7 |
| random_exit_cov0.1 | random_exit_control | 0.101 | 0.946332 | 0.946341 | 0.985627 | 1 | 7 |
| random_exit_cov0.2 | random_exit_control | 0.200 | 0.943051 | 0.943089 | 0.980941 | 2 | 10 |
| random_exit_cov0.3 | random_exit_control | 0.299 | 0.941437 | 0.941463 | 0.982337 | 4 | 13 |
| shuffled_confidence_cov1 | shuffled_confidence_control | 0.902 | 0.941419 | 0.941463 | 0.980212 | 3 | 12 |
| always_exit_p_text | always_exit_control | 1.000 | 0.923576 | 0.923577 | 0.972205 | 8 | 28 |
| random_exit_cov0.5 | random_exit_control | 0.501 | 0.920241 | 0.920325 | 0.971803 | 3 | 25 |
| random_exit_cov0.8 | random_exit_control | 0.800 | 0.899069 | 0.899187 | 0.967890 | 5 | 40 |
| random_exit_cov1 | random_exit_control | 1.000 | 0.884509 | 0.884553 | 0.958086 | 6 | 50 |
| always_exit_p_image | always_exit_control | 1.000 | 0.781322 | 0.782114 | 0.885468 | 12 | 119 |

Decision reasons:
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
