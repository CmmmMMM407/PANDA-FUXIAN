# Round 6 R6-C Gate-0 Summary

Decision: `Feasible-B`

Rules: train/val only; no test export/open/analyze; low-margin threshold fit on train.

| Candidate | Role | F1 | Acc | AUC | NLL | ECE | W2C | C2W | Low-margin dF1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| r6c_low_margin_h_di_adapter | primary | 0.957715 | 0.957724 | 0.988355 | 0.154031 | 0.029805 | 1 | 0 | 0.002424 |
| r6c_low_margin_h_final_adapter | primary | 0.957715 | 0.957724 | 0.987678 | 0.154306 | 0.028162 | 2 | 1 | 0.002424 |
| original_final | primary_baseline | 0.956086 | 0.956098 | 0.987372 | 0.158358 | 0.027006 | 0 | 0 | 0.000000 |
| same_param_global_h_final_control | same_param_control | 0.954462 | 0.954472 | 0.987086 | 0.145018 | 0.022542 | 1 | 2 | -0.002377 |
| same_param_global_h_di_control | same_param_control | 0.954457 | 0.954472 | 0.987901 | 0.143438 | 0.020670 | 0 | 1 | -0.002426 |
| final_only_platt | calibration_control | 0.954451 | 0.954472 | 0.987372 | 0.143413 | 0.021351 | 1 | 2 | -0.002479 |
| random_mask_h_di_control | random_mask_control | 0.954451 | 0.954472 | 0.986504 | 0.151607 | 0.025910 | 1 | 2 | -0.002479 |
| random_mask_h_collab_control | random_mask_control | 0.952828 | 0.952846 | 0.987425 | 0.143502 | 0.020376 | 1 | 3 | -0.004856 |
| low_margin_logit_bias_control | bias_control | 0.952828 | 0.952846 | 0.987372 | 0.159370 | 0.027765 | 0 | 2 | -0.004856 |
| random_mask_h_final_control | random_mask_control | 0.952828 | 0.952846 | 0.986166 | 0.151110 | 0.029485 | 0 | 2 | -0.004856 |
| random_feature_low_margin_control | random_feature_control | 0.951198 | 0.951220 | 0.987805 | 0.141271 | 0.015915 | 0 | 3 | -0.007287 |
| r6c_low_margin_h_collab_adapter | primary | 0.949580 | 0.949593 | 0.987816 | 0.143817 | 0.018537 | 0 | 4 | -0.009606 |
| same_param_global_h_collab_control | same_param_control | 0.949580 | 0.949593 | 0.987181 | 0.144781 | 0.020581 | 0 | 4 | -0.009606 |
| final_aux_stacking_control | ordinary_stacking_control | 0.929784 | 0.930081 | 0.932068 | 0.505740 | 0.062691 | 7 | 23 | -0.040117 |

Decision reasons:
