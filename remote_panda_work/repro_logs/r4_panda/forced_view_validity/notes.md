# R4 forced-view validity gate

Status: Pending review

Rules:
- Frozen reproduced PANDA checkpoints only.
- Splits exported: train/val only.
- Test split is intentionally not exported or analyzed.
- No training is performed by this script.

Outputs:
- weibo21 seed42 train: /root/autodl-tmp/panda_repro/panda/repro_logs/r4_panda/forced_view_validity_clean/r4_forced_views_summary_weibo21_seed42_train.json
- weibo21 seed42 val: /root/autodl-tmp/panda_repro/panda/repro_logs/r4_panda/forced_view_validity_clean/r4_forced_views_summary_weibo21_seed42_val.json

Preliminary gate decisions must be reviewed before any R4 training config is frozen.
