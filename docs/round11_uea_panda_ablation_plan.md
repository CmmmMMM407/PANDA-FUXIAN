# Round11 UEA-PANDA 消融计划

最后更新：2026-05-29

## 核心假设

`UEA-PANDA / Utility-Entropy Anchored Auxiliary PANDA` 把已有三条线降级融合为训练期辅助监督分配机制：

- R8-B static aux 2.0：提供同预算辅助监督 anchor，不写成主方法成功。
- Round9/Round10 counterfactual utility：只作为 train-time branch auxiliary allocation target，不再做 inference gate。
- Round10 utility entropy：作为 soft reliability/calibration，替代失败的 low-margin/high-risk hard boundary gate。

核心公式：

```text
q_i,b = normalize(relu(u_i,b) + eps)
alpha_i = alpha_max * (1 - H(q_i) / log 3)
w_i,b = base_aux_weight * ((1 - alpha_i) / 3 + alpha_i * q_i,b)
L_aux = mean_i sum_b w_i,b * BCE(branch_b(x_i), y_i)
```

其中 `utility_only` 消融令 `alpha_i = alpha_max`，`entropy` 消融使用上式，`boundary_entropy` 只作为 Round10 negative control。

## 第一轮验证

Round11-A 只跑 Weibo-21 seed42 D4 smoke，5 epoch，train/val-only。所有 PANDA 命令显式：

```text
--model_name FTmodel --skip_final_test
```

Primary:

- `uea_entropy_alpha0p5`

Ablation:

- `uea_utility_only_alpha0p5`
- `uea_entropy_alpha0p25`
- `uea_utility_only_alpha0p25`

New controls:

- `uea_shuffled_utility_entropy_alpha0p5`
- `uea_random_utility_entropy_alpha0p5`
- `uea_reverse_utility_entropy_alpha0p5`
- `uea_confidence_entropy_alpha0p5`
- `uea_boundary_entropy_alpha0p5`

Reused strong controls:

- `deterministic_train_l0`
- `same_budget_noop_l0`
- `static_aux_weight_2p0_anchor_control`
- `generic_dwa`
- `generic_gradnorm`
- `generic_pcgrad`
- `generic_cagrad`
- `detached_aux_no_feature_update`

## Go / No-Go

`Go-to-D5` requires seed42 best UEA to beat static aux 2.0, DWA/GradNorm/PCGrad/CAGrad, detached aux, same-budget, and shuffled/random/reverse/confidence utility controls on Macro-F1 and Accuracy, with W2C > C2W versus deterministic.

If UEA only beats deterministic/static but loses to DWA or utility controls, the result is diagnostic only. If shuffled/random/reverse utility controls match or beat UEA, the utility allocation claim is closed for the current implementation.

## Claim Boundary

Round11-A can only judge the current UEA training implementation at seed42 D4-smoke level. It cannot justify test evaluation, two-dataset main tables, or `Primary-Candidate`. D5 three-seed val opens only after Round11-A passes the moat.
