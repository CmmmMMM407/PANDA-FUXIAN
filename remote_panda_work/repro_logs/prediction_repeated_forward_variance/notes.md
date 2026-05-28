# PANDA prediction-level repeated-forward variance

Created at: 2026-05-24T23:58:11+08:00
Datasets: weibo21
Seeds: 42 2024 2026
Splits: val test
Variants: panda_gumbel_reproduced deterministic_reproduced deterministic_short5 winning_control_short5
Repeats: 30
Batch size: 32

Purpose:

This is a diagnostic-only export for prediction-level y_score variance.
It compares stochastic PANDA Gumbel eval, deterministic selector eval, and
the seed-rechecked short-run winning control. Near-zero variance for
deterministic / winning-control variants is expected and must not be
presented as proof that stable-source selection passed the method gate.

Command:
/root/miniconda3/bin/python tools/export_panda_repeated_forward_variance.py --datasets weibo21 --seeds 42 2024 2026 --splits val test --variants panda_gumbel_reproduced deterministic_reproduced deterministic_short5 winning_control_short5 --repeats 30 --batch-size 32 --num-workers 0 --gpu 0 --output-dir repro_logs/prediction_repeated_forward_variance --overwrite 
