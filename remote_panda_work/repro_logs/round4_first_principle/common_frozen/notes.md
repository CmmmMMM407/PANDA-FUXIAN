# Round 4 common frozen export

Status: common train/val export complete

Rules:
- Only train/val splits are accepted by the exporter.
- Test is not exported, opened, or analyzed.
- Arrays are frozen PANDA representations from deterministic neighbor selection.
- Offline gates may only produce No-Go / Feasible-A / Feasible-B.
- A paper primary must be a training-time endogenous mechanism, not a post-hoc gate.

Outputs:
- weibo21 seed42 train: /root/autodl-tmp/panda_repro/panda/repro_logs/round4_first_principle/common_frozen/round4_common_metadata_weibo21_seed42_train.csv / /root/autodl-tmp/panda_repro/panda/repro_logs/round4_first_principle/common_frozen/round4_common_features_weibo21_seed42_train.npz
- weibo21 seed42 val: /root/autodl-tmp/panda_repro/panda/repro_logs/round4_first_principle/common_frozen/round4_common_metadata_weibo21_seed42_val.csv / /root/autodl-tmp/panda_repro/panda/repro_logs/round4_first_principle/common_frozen/round4_common_features_weibo21_seed42_val.npz
