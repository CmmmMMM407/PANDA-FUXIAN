# 当前状态

最后更新：2026-05-29  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/current_status.md`

## 一句话结论

复现、baseline、诊断和 R2-R11 当前作用域方法验证已经闭环；当前仍没有 `Primary-Candidate`。下一阶段切换为 Round12-R15 SOTA 冲刺与论文实验总方案：先用 train/val-only ensemble 上界诊断判断冲榜空间，再以 `ADWA-PANDA / Anchored Dynamic Auxiliary-supervision PANDA` 追单模型方法，最后只在必要时重构 OOF utility calibration。继续禁止 test 参与方法选择。

## 已完成

- PANDA Weibo-21 / Weibo paper-aligned 三 seed 复现完成。
- MMDFND / DAMMFND 两数据集三 seed reproduced baseline 完成。
- per-domain、reliability、uncertainty、high-confidence error、selector stability、statistical diagnostics 完成。
- CS-PANDA / CLIP 图文冲突强因果线降级；CLIP-only 信号弱，confidence-uncertainty 与 fusion/branch uncertainty 更能解释错误。
- Reliability-aware selector / uncertainty stable-source 已经经过 seed-recheck，不稳定，不能写成正式方法。
- R3、历史 R4、P0/P1、Round 2、Round 3 branch-boundary residual、Round 4 first-principle boundary rebuild、Round 5、Round 6 当前作用域均完成对应 gate 或 smoke。
- Round 7 已完成 artifact audit、R7-A/B/C/D 的 D2/D3、D3.5 gradient sanity，以及 R7-A/R7-D D4-lite。
- Round 8 已完成 R8-A formal D4、R8-B D4/D5、R8-C D3.5、R8-D D3.5；当前无可进入 test 或论文主表的新方法。
- Round 9 已完成 CUE D2 counterfactual utility probe 与 DGL-Aux D4 fallback。CUE 当前 frozen gate 不成立，DGL-Aux 当前 gradient decoupling 不成立；不打开 D5。
- Round 10 已完成 BUA D2.5 offline allocator simulation。Utility allocation 打过 shuffled/random/reverse/confidence controls，但 boundary-gated primary 被 utility-only 和 entropy-only ablations 反超；当前 BUA 不打开 D3.5/D4/D5。
- Round 11 已完成 UEA-PANDA D4 seed42 train/val-only 消融。Primary UEA 不成立；milder entropy alpha0.25 只接近 DWA，reverse-utility control 与 static aux 2.0 并列最高；当前 UEA 不打开 D5。
- Round 12-R15 后续总方案已制定，详见 `docs/PANDA_SOTA冲刺与论文实验总方案.md`。核心是把 SOTA 冲榜线和论文方法线分开：ensemble/calibration 先测上界，ADWA-PANDA 作为优先单模型方法，OOF utility calibration 作为有条件重启线。

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

### R8

R8-A / Boundary-Risk Aware Training 已完成 seed42 formal D4，结论 `No-Go`。Best primary `r8a_composite_risk_primary` F1/Acc/AUC 为 `0.926767/0.926829/0.978847`，低于 best strong control `shuffled_risk_control` 的 `0.938207/0.938211/0.980836`。关键启发是 shuffled risk control 反而最强，说明当前 risk-aware 训练增益更像扰动/正则化 artifact，而不是干净的风险信号。

R8-B / Static Auxiliary-Supervision Strength 已完成 seed42 D4 和三 seed D5。Seed42 D4 `Feasible-A`：static aux 2.0 F1/Acc/AUC `0.939837/0.939837/0.981407`，打过 deterministic、random/shuffled label、same-budget、PCGrad/CAGrad/GradNorm/DWA controls。D5 结论降为 `D5-Feasible-B-not-stable-enough`：三 seed static aux 2.0 均高于 deterministic，平均 Macro-F1 delta `+0.004856`，但 seed2026 被 `generic_dwa` 打穿，static aux `0.911679/0.912195` 低于 DWA `0.926826/0.926829`。这条线可作为训练动力学观察，不可作为 Primary-Candidate。

R8-C / low-margin margin regularizer 已完成 D3.5，结论 `D3.5-No-Go-for-current-regularizer`。Primary 只有 `1/5` batch 对 `h_final/final_classifier` 产生非零梯度，且 low-margin 梯度富集没有高于 controls；不打开 D4。

R8-D / branch aux-logit endogenous signal 已完成 D3.5，结论 `D3.5-No-Go-for-current-aux-logit-signal`。Signal 能触达 final boundary，但 high-mismatch 梯度富集没有打过 branch-drop / shuffled / random controls；不打开 D4。

R8-E 不启动，因为 R8-A/C/D 未过线，R8-B D5 未升 `Primary-Candidate`，没有可挂载的 second-stage primary。

### Round9

Round9-A / CUE-PANDA 已完成 seed42 train/val-only D2 frozen/offline counterfactual utility probe，结论 `No-Go-for-current-CUE-D2`。`cue_gate` F1/Acc/AUC 为 `0.921800/0.921951/0.980069`，低于 `confidence_only_gate` `0.930045/0.930081/0.983659` 和 `same_param_mlp_classifier` `0.936542/0.936585/0.949355`；`final_aux_stacking` 与 `platt_temperature` 为 `0.954451/0.954472`，也强于 CUE。CUE flip audit W2C `8`、C2W `29`，说明当前 train-only utility gate 会把更多原本正确样本翻错。

关键启发：oracle val utility gate diagnostic 达到 F1/Acc/AUC `0.973959/0.973984/0.998773`，说明 counterfactual utility 在验证集上确实有上界信号；但从 train-only utility target 学到的 gate 泛化失败。当前问题不是“utility 完全没信息”，而是“utility 监督构造/泛化路径不干净”，不能进入 CUE D3.5/D4。

Round9-C / DGL-Aux fallback 已完成 seed42 train/val-only D4 smoke，结论 `No-Go-for-current-DGL-Aux`。Best DGL `round9c_dgl_branch_conflict_drop_aux1p0` F1/Acc/AUC `0.933299/0.933333/0.981650`，低于 static aux 2.0、DWA、deterministic/same-budget/detached controls；flip audit W2C `15`、C2W `17`。当前 branch-local PCGrad/conflict-drop 没有把 aux-final 冲突转成有效收益，反而弱于简单 static aux 2.0。

### Round10

Round10-A / BUA-PANDA 已完成 seed42 train/val-only D2.5 offline allocator simulation，结论 `D2.5-No-Go-for-current-BUA-boundary-gate`。Primary `bua_boundary_gated_utility_aux` expected utility 为 `0.773082`，高于 static anchor `0.503536`、shuffled utility `0.539701`、random utility `0.508881`、reverse utility `0.468324`、confidence-only allocation `0.505511`，说明 counterfactual utility 作为 aux allocation 信号仍然干净。

但 primary 低于 `bua_utility_only_aux_alloc` 的 `0.911898` 和 `bua_entropy_gated_utility_aux` 的 `0.816022`；decision reason 为 `boundary_gate_not_proven_vs:bua_utility_only_aux_alloc,bua_entropy_gated_utility_aux`。当前结论是：utility 可作为训练期分支辅助监督分配信号继续研究，但 BUA 当前的 boundary trust gate 会削弱 utility 信号，不能打开 D3.5/D4/D5。

### Round11

Round11-A / UEA-PANDA 已完成 seed42 train/val-only D4 消融，结论 `Utility-Entropy-Aux-Diagnostic-only`。Primary `uea_entropy_alpha0p5` F1/Acc/AUC 为 `0.921905/0.921951/0.981142`，明显低于 static aux 2.0 `0.939837/0.939837/0.981407`、generic DWA `0.938210/0.938211/0.980962`，flip audit 为 W2C `12`、C2W `21`。

Best real UEA ablation 是更温和的 `uea_entropy_alpha0p25`，F1/Acc/AUC `0.938207/0.938211/0.983977`，接近 DWA 但仍低于 static aux 2.0。更关键的负证据是 `uea_reverse_utility_entropy_alpha0p5` 达到 `0.939837/0.939837/0.982084`，与 static aux 2.0 并列最高；这说明当前 per-sample utility allocation 的方向性没有被证明，训练收益更可能来自辅助监督强度/扰动正则化，而不是 utility 指向本身。

`uea_boundary_entropy_alpha0p5` 只有 `0.923574/0.923577/0.979397`，继续支持 Round10 结论：low-margin/high-risk boundary gate 不能作为 hard trust gate 续参。当前 UEA 不打开 D5；可保留的论文启发是“utility entropy / soft reliability calibration / train-time coupling 值得研究，但当前实现不是候选方法”。

## 下一步最高优先级

1. 启动 Round12 train/val-only 模型资产盘点与 ensemble 上界诊断；只导出 train/val logits，不导出 test。
2. 同步启动 Round13 ADWA-PANDA 设计：static aux 2.0 作为总预算 anchor，DWA 只调 text/image/fusion auxiliary branches 的相对权重，并加入 clip/final-loss guard。
3. 只有 Round12 显示明显可学习融合空间，或 Round13 有正趋势，才启动 Round14 OOF utility calibration；不再沿旧 CUE/BUA/UEA 直接续参。
4. Round15 只在至少一条线三 seed val 通过并冻结配置后启动，最终 test 只允许在冻结后打开一次。

## 不建议继续做

- 不直接启动两数据集三 seed新方法主表。
- 不用 test 选 risk、aux weight、margin threshold、teacher、memory、branch subset、lambda 或弱域定义。
- 不继续沿旧 source、prompt、prototype、offline adapter、inference selector、clean reliability selector、R5-A image projection、R6-A 当前 aux rebalancing 续参。
- 不把 R7 的 D3.5/D4-lite 写成正式 D4 结论。
- 不把 R8-B seed42 D4 `Feasible-A` 写成 `Primary-Candidate`；D5 已经显示稳定性不足。
- 不把 Round10 BUA D2.5 的 utility-only 正信号写成 BUA 成功；当前 boundary-gated BUA 已被 utility-only/entropy-only ablations 反超。
- 不把 Round11 的 `uea_entropy_alpha0p25` 接近 DWA 写成方法成功；reverse-utility control 追平 best control，当前 utility directionality claim 不成立。
- 不把冲榜 ensemble 和单模型方法混成一个贡献；ensemble 可以冲指标，ADWA/OOF utility 才能承担方法叙事。

## 证据位置

- Round 7：`remote_panda_work/repro_logs/round7_gate0/seed42/`、`remote_panda_work/repro_logs/round7_d35_gradient_sanity/seed42/`、`remote_panda_work/repro_logs/round7_d4_lite/seed42/`
- Round 8：`remote_panda_work/repro_logs/round8_r8a_formal_d4/seed42/`、`remote_panda_work/repro_logs/round8_r8b_static_aux_candidate/seed42/`、`remote_panda_work/repro_logs/round8_r8b_d5_seed_recheck/summary/`、`remote_panda_work/repro_logs/round8_r8c_d35_gradient_sanity/seed42/`、`remote_panda_work/repro_logs/round8_r8d_d35_branch_aux_endogenous_sanity/seed42/`
- Round 9：`remote_panda_work/repro_logs/round9_cue_d2/seed42/`、`remote_panda_work/repro_logs/round9c_dgl_aux_d4/seed42/summary/`、`remote_panda_work/logs/round9c_dgl_aux_d4/`、`remote_panda_work/code_snapshots/round9c_dgl_aux_patch/`
- Round 10：`remote_panda_work/repro_logs/round10_bua_d25/seed42/`
- Round 11：`remote_panda_work/repro_logs/round11_uea_d4/seed42/summary/`、`remote_panda_work/logs/round11_uea_d4/`、`remote_panda_work/code_snapshots/round11_uea_patch_after/`
- Round 12-R15 planning：`docs/PANDA_SOTA冲刺与论文实验总方案.md`
- Round 6：`remote_panda_work/repro_logs/round6_r6a_smoke/seed42/`、`remote_panda_work/repro_logs/round6_*`
- Reproduced baselines：`remote_panda_work/repro_logs/reproduced_baseline_main_table/`
- Reliability / diagnostics：`remote_panda_work/repro_logs/panda_diagnostics/`、`remote_panda_work/repro_logs/statistical_diagnostics/`
- 完整历史文档：`docs/archive/`

## 维护规则

- 本文件只保留当前最重要状态，不写流水账。
- 详细实验过程写入 `experiment_log.md`，完整旧日志在 `docs/archive/full_snapshots_20260528/root/experiment_log.md`。
- 每次实验后同步 `current_status.md`、`todo.md`、`experiment_log.md` 和新增日志摘要到 GitHub 日志仓库。
