# Round 6 R6-J Gate-0 Reserve Audit

Decision: `Provisional No-Go`

Decision scope: evidence-only reserve audit. This summary reuses R3/P2-D/P0-B
evidence and does not directly test a new non-self normalized or self-suppressed
differentiable source mixture.

Reasons:
- existing_r3_soft_source_router_collapsed_to_self_domain
- source_utility_residual_offline_gate_below_anchor
- pad_top2_source_view_not_cleanly_better_than_shuffled_control
- reopening_source_mixture_requires_new_protocol_not_current_smoke

Evidence:
- R3 mechanism notes report r3_effective_source_num_mean≈1.000006 and self_top1_ratio=1.0.
- P2-D best source residual F1/Acc 0.951216/0.951220 below anchor 0.956086/0.956098.
- DCA/source view PAD top2 CE 0.157783 vs shuffled CE 0.156849.

Required revalidation before permanent exclusion:
- Register a new train/val non-self normalized / self-suppressed source mixture protocol.
- Prove effective non-self source usage, bounded self weight, alpha-regret correlation, and top/bottom/random source control moat.
- Only after that direct probe fails should R6-J be marked No-Go beyond this provisional reserve audit.
