# Round 4 first-principle gate summary

Dataset: `weibo21` seed `42`

Protocol:
- Input is train/val-only common frozen export.
- Test split is not exported, opened, or analyzed.
- Offline gates can only mark No-Go / Feasible-A / Feasible-B.
- Primary-Candidate requires all gates plus training-time endogenous validation.

Decisions:
- R4-A: `No-Go`; reasons: best_primary_below_original_f1_or_acc, best_primary_not_above_best_control, flip_audit_not_net_positive, no_low_margin_gain
- R4-D: `No-Go`; reasons: best_primary_below_original_f1_or_acc, best_primary_not_above_best_control, flip_audit_not_net_positive, no_low_margin_gain
- R4-C: `No-Go`; reasons: best_primary_below_original_f1_or_acc, best_primary_not_above_best_control, flip_audit_not_net_positive, no_low_margin_gain
- R4-B: `Diagnostic-only`; reasons: none

Important observation:
- Original final val Macro-F1/Acc/AUC: 0.956086 / 0.956098 / 0.987372
