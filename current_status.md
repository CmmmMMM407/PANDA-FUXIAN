# 当前状态

最后更新：2026-05-28  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/current_status.md`

## 一句话结论

复现、baseline、诊断和 R2-R7 当前作用域方法验证已经闭环；当前没有 `Primary-Candidate`。下一步只推荐推进 R8 队列中有正向线索的方法，优先 R8-A 与 R8-B，并继续禁止 test 参与方法选择。

## 已完成

- PANDA Weibo-21 / Weibo paper-aligned 三 seed 复现完成。
- MMDFND / DAMMFND 两数据集三 seed reproduced baseline 完成。
- per-domain、reliability、uncertainty、high-confidence error、selector stability、statistical diagnostics 完成。
- CS-PANDA / CLIP 图文冲突强因果线降级；CLIP-only 信号弱，confidence-uncertainty 与 fusion/branch uncertainty 更能解释错误。
- Reliability-aware selector / uncertainty stable-source 已经经过 seed-recheck，不稳定，不能写成正式方法。
- R3、历史 R4、P0/P1、Round 2、Round 3 branch-boundary residual、Round 4 first-principle boundary rebuild、Round 5、Round 6 当前作用域均完成对应 gate 或 smoke。
- Round 7 已完成 artifact audit、R7-A/B/C/D 的 D2/D3、D3.5 gradient sanity，以及 R7-A/R7-D D4-lite。

## 关键复现数字

| Dataset | Method | Macro-F1 | Accuracy | AUC |
| --- | --- | ---: | ---: | ---: |
| Weibo-21 | PANDA | 0.9474 +/- 0.0073 | 0.9474 +/- 0.0073 | 0.9879 +/- 0.0014 |
| Weibo-21 | DAMMFND | 0.9436 +/- 0.0075 | 0.9436 +/- 0.0075 | 0.9839 +/- 0.0049 |
| Weibo-21 | MMDFND | 0.9262 +/- 0.0147 | 0.9263 +/- 0.0147 | 0.9676 +/- 0.0114 |
| Weibo | PANDA | 0.9415 +/- 0.0034 | 0.9415 +/- 0.0034 | 0.9866 +/- 0.0011 |
| Weibo | DAMMFND | 0.9374 +/- 0.0028 | 0.9374 +/- 0.0028 | 0.9856 +/- 0.0012 |
| Weibo | MMDFND | 0.9094 +/- 0.0243 | 0.9094 +/- 0.0243 | 0.9719 +/- 0.0089 |

## 当前方法判断

### R6

R6-A seed42 D4 smoke 已完成，当前训练实现 No-Go。Best primary `r6a_late_aux_ramp_0p5_to_2p0` val F1/Acc 为 `0.938184/0.938211`，低于 static control `static_aux_weight_2p0_anchor_control` 的 `0.939837/0.939837`。

R6-C 三 seed offline 复核不稳定；R6-D/G/H/J 已由旧 Blocked/Provisional 推进到当前作用域 direct/complementarity/frozen-response No-Go；R6-B/R6-E/R6-F/R6-I 当前 frozen/offline 变体也已 No-Go。R6 关闭的是当前作用域，不永久排除本质不同训练期机制。

### R7

R7-A 是唯一保留正向趋势的候选：composite risk 对 val error 有弱富集，D4-lite 中 `r7a_composite_risk_lite` F1/Acc/AUC 为 `0.732329/0.739837/0.866367`，优于 deterministic-lite、confidence-only、random risk、shuffled risk controls。限制是 D3 offline proxy 明显低于 original final，且 D3.5 显示 `risk_margin` 很像 CE/hard-sample reweighting，`risk_consistency` 与 CE 冲突。

R7-D 当前 sample aux curriculum 被 static aux 2.0 打穿；R7-B/R7-C 只有 loss-path 或 representation-path 证据，不解锁正式 D4。

这些都不能写成正式训练实现成功或失败。正式判断至少需要 D4 seed42 smoke；稳定性至少需要 D5 三 seed val。

## 下一步最高优先级

1. 冻结 R8-A / R7-A formal D4 manifest：只做 Weibo-21 seed42 train/val-only 5-epoch，强 controls 必须包括 deterministic、same-budget CE、static aux 2.0、focal loss、class-balanced CE、confidence-only risk、random risk、shuffled risk、risk-margin only、risk-consistency only、risk-margin + consistency。
2. 把 `aux_weight_2p0` 从历史 control 独立登记为 R8-B：Static/Adaptive Auxiliary-Supervision Strength。必须打过 deterministic、random/shuffled labels、same-budget、generic gradient controls，不能事后包装成 R5-A/R6-A 成功。
3. R8-C/R8-D 只在前两项未出路或资源允许时推进；R8-E 只能作为已有 primary 的 calibration/add-on。

## 不建议继续做

- 不直接启动两数据集三 seed新方法主表。
- 不用 test 选 risk、aux weight、margin threshold、teacher、memory、branch subset、lambda 或弱域定义。
- 不继续沿旧 source、prompt、prototype、offline adapter、inference selector、clean reliability selector、R5-A image projection、R6-A 当前 aux rebalancing 续参。
- 不把 R7 的 D3.5/D4-lite 写成正式 D4 结论。

## 证据位置

- Round 7：`remote_panda_work/repro_logs/round7_gate0/seed42/`、`remote_panda_work/repro_logs/round7_d35_gradient_sanity/seed42/`、`remote_panda_work/repro_logs/round7_d4_lite/seed42/`
- Round 6：`remote_panda_work/repro_logs/round6_r6a_smoke/seed42/`、`remote_panda_work/repro_logs/round6_*`
- Reproduced baselines：`remote_panda_work/repro_logs/reproduced_baseline_main_table/`
- Reliability / diagnostics：`remote_panda_work/repro_logs/panda_diagnostics/`、`remote_panda_work/repro_logs/statistical_diagnostics/`
- 完整历史文档：`docs/archive/`

## 维护规则

- 本文件只保留当前最重要状态，不写流水账。
- 详细实验过程写入 `experiment_log.md`，完整旧日志在 `docs/archive/full_snapshots_20260528/root/experiment_log.md`。
- 每次实验后同步 `current_status.md`、`todo.md`、`experiment_log.md` 和新增日志摘要到 GitHub 日志仓库。
