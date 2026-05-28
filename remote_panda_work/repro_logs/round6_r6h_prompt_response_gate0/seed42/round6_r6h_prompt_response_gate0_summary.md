# Round 6 R6-H Prompt Response Gate-0 Summary

Decision: `No-Go`

Scope: frozen prompt-response probe; prompt tensors passed through BERT/text path without editing PANDA.py; train/val only; no training; no test.

| Split | View | Role | F1 | Acc | AUC | NLL | W2C | C2W | AbsDiff | JSD |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | random_prompt_text_fusion | control | 0.950108 | 0.950264 | 0.999515 | 0.120145 | 0 | 245 | 0.077531 | 0.033942 |
| train | shuffled_prompt_text_fusion | control | 0.999797 | 0.999797 | 1.000000 | 0.001781 | 0 | 1 | 0.001210 | 0.000408 |
| train | content_baseline | primary_baseline | 1.000000 | 1.000000 | 1.000000 | 0.000260 | 0 | 0 | 0.000000 | 0.000000 |
| train | prompt_text_fusion | primary | 1.000000 | 1.000000 | 1.000000 | 0.001016 | 0 | 0 | 0.000789 | 0.000184 |
| train | prompt_text_only | control | 1.000000 | 1.000000 | 1.000000 | 0.001016 | 0 | 0 | 0.000789 | 0.000184 |
| val | random_prompt_text_fusion | control | 0.816766 | 0.821138 | 0.937610 | 0.490616 | 7 | 90 | 0.173982 | 0.077452 |
| val | prompt_text_fusion | primary | 0.936454 | 0.936585 | 0.985161 | 0.190771 | 4 | 16 | 0.038104 | 0.008464 |
| val | prompt_text_only | control | 0.936454 | 0.936585 | 0.985161 | 0.190771 | 4 | 16 | 0.038104 | 0.008464 |
| val | shuffled_prompt_text_fusion | control | 0.949473 | 0.949593 | 0.990090 | 0.153774 | 20 | 24 | 0.090436 | 0.039788 |
| val | content_baseline | primary_baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0 | 0 | 0.000000 | 0.000000 |

Decision reasons:
- best_primary_below_content_baseline
- best_primary_flip_not_net_positive
- best_control_matches_or_beats_primary
