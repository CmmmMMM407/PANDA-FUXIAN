# P1-C Reliability / Evidential Extension Gate Notes

Status: `No-Go` for primary-method training; retained as diagnostic/calibration evidence.

This gate uses existing selector-v2 Go/No-Go, seed-recheck, and reliability diagnostics. No new training was launched. The decision is based on validation rows only; test rows are not used for method selection.

Key evidence:

- Seed42 val had one passing variant: `reliability_confidence_uncertainty_stable_source_reward_pre_epoch_l0p2`.
- Seed42 val looked promising: Macro-F1/Acc/AUC `0.941395/0.941463/0.984960` vs deterministic `0.939835/0.939837/0.981206`; ECE/Brier/HCE and weak-domain F1 also improved.
- Three-seed val recheck failed the primary gate: candidate mean Macro-F1/Acc `0.936018/0.936043` below deterministic `0.937093/0.937127`.
- Seed2024 is the decisive negative control: val Macro-F1/Acc deltas `-0.006513/-0.006504`, with support metric count 0.
- Average AUC, ECE, Brier, HCE, and weak-domain F1 improve, but these do not override the Macro-F1/Acc stability gate.

Interpretation:

Uncertainty/reliability is a strong diagnostic signal for model errors and weak-domain behavior, but the current reliability extension does not convert that signal into a stable final-boundary method. It should be reported as calibration/diagnostic analysis, not as a formal new method contribution.
