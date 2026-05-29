# Round10-A BUA D2.5 Decision

Decision: **D2.5-No-Go-for-current-BUA-boundary-gate**

Rules:
- Train/val-only; test not exported, opened, or used.
- D2.5 checks offline allocation signal cleanliness, not trained F1.
- D3.5 opens only if utility and boundary allocation are separated from strong controls.

Key val-diagnostic allocation metrics:
- primary `bua_boundary_gated_utility_aux`: expected_utility=0.773082, expected_branch_correct=0.914225, alpha_mean=0.296044
- anchor `bua_anchor_static_aux2p0`: expected_utility=0.503536, expected_branch_correct=0.884553, alpha_mean=0.000000
- utility-only `bua_utility_only_aux_alloc`: expected_utility=0.911898, expected_branch_correct=0.914391, alpha_mean=0.500000
- entropy-only `bua_entropy_gated_utility_aux`: expected_utility=0.816022, expected_branch_correct=0.914225, alpha_mean=0.425707
- shuffled utility `bua_shuffled_utility_control`: expected_utility=0.539701, expected_branch_correct=0.906754, alpha_mean=0.307109
- random utility `bua_random_utility_control`: expected_utility=0.508881, expected_branch_correct=0.886354, alpha_mean=0.083745
- reverse utility `bua_reverse_utility_control`: expected_utility=0.468324, expected_branch_correct=0.876749, alpha_mean=0.067310
- confidence-only `bua_confidence_only_branch_allocation`: expected_utility=0.505511, expected_branch_correct=0.886108, alpha_mean=0.013132

Decision comparisons:
- delta_expected_utility_vs_bua_anchor_static_aux2p0: `0.269546`
- delta_expected_utility_vs_bua_shuffled_utility_control: `0.233381`
- delta_expected_utility_vs_bua_random_utility_control: `0.264201`
- delta_expected_utility_vs_bua_reverse_utility_control: `0.304758`
- delta_expected_utility_vs_bua_confidence_only_branch_allocation: `0.267571`
- delta_expected_utility_vs_bua_boundary_only_aux_strength: `0.269546`
- delta_expected_utility_vs_bua_utility_only_aux_alloc: `-0.138817`
- delta_expected_utility_vs_bua_entropy_gated_utility_aux: `-0.042940`
- delta_expected_utility_vs_bua_shuffled_boundary_control: `0.051165`

Reasons:
- boundary_gate_not_proven_vs:bua_utility_only_aux_alloc,bua_entropy_gated_utility_aux

Notable diagnostics:
- val boundary trust coverage: `0.730081`
- val utility entropy error AUC: `0.936162`
- val top-utility branch correct rate: `0.939837`

Claim scope:
D2.5 offline allocator simulation only; it can open or close BUA D3.5 but cannot judge trained D4 performance.
