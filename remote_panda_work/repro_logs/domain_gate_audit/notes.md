# P1-B domain-conditioned expert gate audit

Status: Pending review

Rules:
- Frozen reproduced PANDA checkpoints only.
- Splits exported: train/val only.
- Test split is intentionally not exported or analyzed.
- No training is performed by this script.

Outputs:
- weibo21 seed42 train: /root/autodl-tmp/panda_repro/panda/repro_logs/domain_gate_audit/domain_gate_audit_summary_weibo21_seed42_train.json
- weibo21 seed42 val: /root/autodl-tmp/panda_repro/panda/repro_logs/domain_gate_audit/domain_gate_audit_summary_weibo21_seed42_val.json
