# P2-B Boundary Adapter Smoke

Decision: **No-Go**

Test used for decision: `False`

Best primary: `adapter_final_reliability_residual`

{
  "macro_f1": 0.9098214023871668,
  "accuracy": 0.9105691056910569,
  "auc": 0.9192543627710206,
  "ece": 0.07427878447664457,
  "brier": 0.07656212420450406,
  "high_conf_error_rate": 0.06980802792321117,
  "weak_domain_macro_f1": 0.8702170507943612,
  "support_better_count": 0.0,
  "adapter_delta_abs_mean": 2.103416681289673
}

Best control: `adapter_final_aux_residual`

{
  "macro_f1": 0.9593457239634151,
  "accuracy": 0.959349593495935,
  "auc": 0.9874881015335801,
  "ece": 0.029173131493048923,
  "brier": 0.03877213430243827,
  "high_conf_error_rate": 0.026595744680851064,
  "weak_domain_macro_f1": 0.9480286738351255,
  "support_better_count": 3.0,
  "adapter_delta_abs_mean": 0.22856152057647705
}