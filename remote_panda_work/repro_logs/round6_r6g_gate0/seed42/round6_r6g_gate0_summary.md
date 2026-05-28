# Round 6 R6-G Gate-0 Reserve Audit

Decision: `Provisional No-Go`

Decision scope: evidence-only reserve audit. This summary does not directly test
soft assignment or EMA prototype memory, so it must not be used as a permanent
No-Go for the full R6-G method family.

Reasons:
- existing_train_val_prototype_source_sensitivity_gates_failed_control_moat
- feature_or_soft_source_ranking_signal_beaten_by_shuffled_control
- pad_top2_source_view_not_cleanly_better_than_shuffled_random_bottom_controls
- no_frozen_evidence_supports_immediate_soft_ema_prototype_smoke

Evidence:
- P0-B val PAD top2 CE 0.157783 vs shuffled CE 0.156849.
- P1-A best feature candidate `feature_mean_top2_nonself` val CE 0.156865 vs shuffled CE 0.156060.
- Both source/prototype routes used train/val only and recorded test_split_exported=false.

Required revalidation before permanent exclusion:
- Run a direct train/val hard-vs-soft-vs-EMA prototype probe.
- Include random prototype, class-shuffled memory, bottom-source and random-source controls.
- Only if soft/EMA fails that direct control moat should R6-G be marked No-Go beyond this provisional reserve audit.
