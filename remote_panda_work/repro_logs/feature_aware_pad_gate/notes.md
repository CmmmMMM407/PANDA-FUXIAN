# P1-A feature-aware PAD/prototype frozen gate

Status: Pending review

Rules:
- Frozen reproduced PANDA checkpoints only.
- Splits exported: train/val only.
- Test split is intentionally not exported or analyzed.
- No training is performed by this script.
- Feature-aware source ranks use sample feature to prototype distance only; labels are not used for source selection.

Primary views:
- pad_top2_nonself
- feature_min_top2_nonself
- feature_mean_top2_nonself
- hybrid_z_top2_nonself
- hybrid_rank_top2_nonself
- pad_bottom2_nonself
- pad_shuffled_top2_nonself
- feature_min_shuffled_top2_nonself
- feature_mean_shuffled_top2_nonself
- hybrid_z_shuffled_top2_nonself
- hybrid_rank_shuffled_top2_nonself

Outputs:
- weibo21 seed42 train: /root/autodl-tmp/panda_repro/panda/repro_logs/feature_aware_pad_gate/feature_aware_pad_summary_weibo21_seed42_train.json
- weibo21 seed42 val: /root/autodl-tmp/panda_repro/panda/repro_logs/feature_aware_pad_gate/feature_aware_pad_summary_weibo21_seed42_val.json
