# Round 3 Branch-Boundary Residual Gate

Decision: **No-Go**

Test used for decision: `False`

Best primary: `r3b_gap_boundary_gated_residual`

{
  "family": "branch_boundary_residual",
  "macro_f1": 0.9495929628444746,
  "accuracy": 0.9495934959349593,
  "auc": 0.9871708090957165,
  "ece": 0.03021269883417539,
  "brier": 0.04045886964967621,
  "high_conf_error_rate": 0.028119507908611598,
  "weak_domain_macro_f1": 0.9394346237040352,
  "support_better_count": 1.0,
  "wrong_to_correct": 3.0,
  "correct_to_wrong": 7.0,
  "adapter_delta_abs_mean": 0.7802056670188904,
  "gate_activation_rate": 0.9008130081300812
}

Best control: `weighted_average_final_aux_logits`

{
  "family": "ordinary_combiner",
  "macro_f1": 0.9560933818804884,
  "accuracy": 0.9560975609756097,
  "auc": 0.9874986779481756,
  "ece": 0.03385390727346128,
  "brier": 0.039105365968080494,
  "high_conf_error_rate": 0.026833631484794274,
  "weak_domain_macro_f1": 0.9480286738351255,
  "support_better_count": 2.0,
  "wrong_to_correct": 3.0,
  "correct_to_wrong": 3.0,
  "adapter_delta_abs_mean": 0.4452764368297357,
  "gate_activation_rate": null
}

No-Go reasons:

- best_primary_below_original_final_score
- best_primary_not_above_best_control
- calibration_or_ordinary_combiner_matches_or_beats_primary
- flip_audit_not_net_positive
- no_low_margin_or_high_mismatch_gain
- support_metrics_insufficient