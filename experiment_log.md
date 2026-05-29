# 实验日志

最后整理：2026-05-29  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/experiment_log.md`

本文件现在只保留高密度索引和最新关键实验摘要。逐条长日志、命令细节和历史流水账见完整快照与 `remote_panda_work/repro_logs/`。

## 2026-05-29：Round12-R15 SOTA 冲刺与论文实验总方案制定

目标：

- 回应“继续追 SOTA”的目标切换，把后续实验从单一路线赛马改成两线并行：SOTA 冲榜线与论文方法线。
- 整合 R2-R11 的正/负证据，避免继续沿已失败的 CUE/BUA/UEA/boundary hard gate 直接续参。
- 明确最终 test 协议：三 seed val 通过并冻结最终配置前，不导出、不打开、不分析 test。

规划：

- Round12：先做 train/val-only 模型资产盘点与 ensemble 上界诊断，覆盖 PANDA、static aux 2.0、generic DWA、DAMMFND、MMDFND 的多 seed logits；用 equal-weight、convex-weight、calibration-before-ensemble、oracle disagreement 和 diversity audit 判断冲榜空间。
- Round13：优先做 `ADWA-PANDA / Anchored Dynamic Auxiliary-supervision PANDA`。核心是用 static aux 2.0 提供稳定总预算 anchor，用 clipped DWA 调 text/image/fusion auxiliary branch 相对权重，并加入 final-loss guard。
- Round14：只在 Round12/13 显示空间后启动 OOF utility calibration。它必须重做 split-safe OOF utility target，不能复用旧 train-only CUE gate 或 Round11 UEA allocation。
- Round15：只有至少一条线完成三 seed val 并冻结配置后，才允许执行最终 test；test 后禁止回头改权重、阈值、seed、aux weight 或 ensemble 成员。

关键判断：

- 最快冲指标的是多 seed / 多方法 ensemble，但必须和单模型方法线分开叙事。
- 最值得写成方法的是 ADWA-PANDA，因为它直接解释 R8-B static aux 2.0 的稳定正向趋势和 seed2026 DWA 反例。
- Utility / entropy 仍有研究价值，但只能通过 OOF target、calibration 或 ensemble feature 重构；旧 boundary hard gate 和当前 UEA 不再续参。

文档：

- 新增 `docs/PANDA_SOTA冲刺与论文实验总方案.md`。
- 更新 `current_status.md`、`todo.md`、`project_overview.md`、`session_start.md`、`docs/README.md`。

## 2026-05-29：Round 11 UEA-PANDA D4 消融闭环

目标：

- 验证 `Utility-Entropy Anchored Auxiliary PANDA` 是否能把 R8-B static aux 2.0、Round9/Round10 counterfactual branch utility、Round10 utility entropy 融合成有效训练期 per-sample branch auxiliary allocation。
- 特别检查 utility entropy 是否能替代失败的 low-margin/high-risk hard boundary trust gate。
- 继续执行 train/val-only；显式 `--model_name FTmodel --skip_final_test`，不导出、不打开、不分析 test。

操作：

- 在远端 PANDA 活代码中加入 `sample_id` 透传、UEA CLI/config 参数、per-sample branch aux allocation 逻辑。
- 新增 `tools/run_panda_round11_uea_d4.sh` 与 `tools/summarize_panda_round11_uea_d4.py`。
- 复用 Round9-A train branch utility CSV，只读取 train utility target；运行 primary、alpha 消融、utility controls、boundary negative control，并合并 static aux 2.0、DWA/GradNorm/PCGrad/CAGrad、detached aux、same-budget 等 required controls。
- 完成 `py_compile`、`bash -n`、dataloader batch `sample_id` smoke、1-epoch UEA smoke 和 seed42 5-epoch D4 全量消融。

结果：

- Round11-A 结论为 `Utility-Entropy-Aux-Diagnostic-only`，不打开 D5。
- Primary `uea_entropy_alpha0p5` F1/Acc/AUC `0.921905/0.921951/0.981142`，flip audit W2C `12`、C2W `21`，低于 static aux 2.0 `0.939837/0.939837/0.981407` 和 generic DWA `0.938210/0.938211/0.980962`。
- Best real UEA ablation `uea_entropy_alpha0p25` 为 `0.938207/0.938211/0.983977`，接近 DWA 但仍低于 static aux 2.0。
- `uea_reverse_utility_entropy_alpha0p5` 达到 `0.939837/0.939837/0.982084`，与 static aux 2.0 并列最高；这击穿了当前 utility directionality claim。
- `uea_boundary_entropy_alpha0p5` 只有 `0.923574/0.923577/0.979397`，继续证明 Round10 low-margin/high-risk boundary gate 不是可复用抓手。

结论：

- 当前 UEA 不是 `Primary-Candidate`，也不值得三 seed D5。
- 重要规律 1：static aux / auxiliary supervision strength 仍是最稳定的有希望线，但它更像训练动力学观察，不是已经可投稿的 PANDA-specific 方法。
- 重要规律 2：utility signal 的训练期使用仍有启发，但当前 per-sample branch allocation 的方向性没有被证明；reverse utility 追平 best control，说明收益可能来自扰动/正则化或预算分配形状。
- 重要规律 3：utility entropy 比 boundary risk 更值得作为 soft calibration 变量继续研究；但下一版必须重做 utility target / reliability 泛化机制，不能沿当前 UEA 直接续参。

证据目录：

- `remote_panda_work/repro_logs/round11_uea_d4/seed42/summary/`
- `remote_panda_work/logs/round11_uea_d4/`
- `remote_panda_work/code_snapshots/round11_uea_patch_after/`

## 2026-05-29：Round 10 BUA-PANDA D2.5 offline allocator 闭环

目标：

- 验证 `Boundary-gated Utility-Anchored Auxiliary PANDA` 是否能把 Round9-A 的 counterfactual branch utility 从 inference gate 降级为 training-time branch auxiliary supervision allocator。
- 检查 boundary trust gate 是否提供增量价值，而不是削弱 utility 或退化为 confidence / boundary heuristic。
- 继续执行 train/val-only；不训练 PANDA，不导出、不打开、不分析 test。

操作：

- 新增 `tools/run_panda_round10a_bua_d25.py`。
- 复用远端 Round9-A 已生成的 `branch_utility_train.csv` 与 `branch_utility_val_diagnostic.csv`，构造 `q_i,b = normalize(relu(u_i,b)+epsilon)`。
- 用 train 分布确定 low-margin / risk thresholds，构造 `boundary_trust_i = 1[low_margin_i or high_boundary_risk_i]` 与 `alpha_i = clip(boundary_trust_i * utility_confidence_i, 0, 0.5)`。
- 比较 primary `bua_boundary_gated_utility_aux` 与 static uniform anchor、utility-only、entropy-only、boundary-only、shuffled utility、shuffled boundary、random utility、reverse utility、confidence-only branch allocation。
- 安全同步仅保留 summary、manifest、metrics 和 md decision；不保存 checkpoint、权重、原始数据、branch utility 长表或 test artifact。

结果：

- Round10-A D2.5 结论为 `D2.5-No-Go-for-current-BUA-boundary-gate`。
- Primary `bua_boundary_gated_utility_aux` expected utility `0.773082`，明显高于 static anchor `0.503536`、shuffled utility `0.539701`、random utility `0.508881`、reverse utility `0.468324`、confidence-only allocation `0.505511`。
- 但 primary 低于 utility-only `0.911898` 和 entropy-only `0.816022`；decision reason 为 `boundary_gate_not_proven_vs:bua_utility_only_aux_alloc,bua_entropy_gated_utility_aux`。
- Val utility entropy 对 final error 的 AUC 为 `0.936162`，top-utility branch correct rate 为 `0.939837`，top-utility 与 top-confidence match rate 仅 `0.380488`。

结论：

- 当前 BUA boundary-gated allocator 不进入 D3.5/D4/D5。
- 重要规律 1：counterfactual utility 作为 branch aux allocation 的离线信号是干净的，能打过 shuffled/random/reverse/confidence controls。
- 重要规律 2：当前 boundary trust gate 不是有效开关，反而压低 utility-only / entropy-only allocation 的收益；后续若重开，不应继续沿 `low-margin or high-risk` 的 hard boundary gate 续参。
- 重要规律 3：utility entropy 比 boundary risk 更像“何时信 utility”的变量；这提示下一版机制应考虑 soft reliability / entropy calibration / train-time coupling，而不是把 R7/R8 risk 直接作为 trust gate。

证据目录：

- `remote_panda_work/repro_logs/round10_bua_d25/seed42/`

## 2026-05-29：Round 9 CUE-PANDA 与 DGL-Aux fallback 闭环

目标：

- 验证 `Counterfactual Utility-aligned Evidence PANDA` 是否能用 train-only branch utility 学到比 confidence/stacking/calibration 更干净的 evidence gate。
- 若 CUE D2 不成立，验证 DGL-style branch-local gradient decoupling / aux-final conflict drop 是否能超过 static aux 2.0、DWA、GradNorm、PCGrad/CAGrad、detached aux 和 same-budget controls。
- 继续执行 train/val-only；D5 前不导出、不打开、不分析 test。

操作：

- Round9-A：基于现有 PANDA checkpoint 与 Round6-R6B branch features，构造 leave-one-branch-out counterfactual utility：`u_branch = CE(y_minus_branch,y)-CE(y_full,y)`；训练 CUE gate，并比较 original equal-sum、global weights、confidence-only、uncertainty/disagreement、random/shuffled utility、same-param MLP、final+aux stacking、Platt/temperature controls。
- Round9-C：在远端 `main.py` / `model/PANDA.py` 增加 `dgl_branch_pcgrad` 与 `dgl_branch_conflict_drop` 两种 `r5a_grad_mode`，运行 4 个 seed42 D4 variants：PCGrad aux1.0/2.0 与 conflict-drop aux1.0/2.0。
- 安全同步仅保留 summary、decision、manifest、metrics、flip audit、stdout log 和代码快照；不保存 checkpoint、权重、原始数据、branch utility 长表或 val prediction 长表。

结果：

- Round9-A D2 `No-Go-for-current-CUE-D2`：`cue_gate` F1/Acc/AUC `0.921800/0.921951/0.980069`，低于 `confidence_only_gate` `0.930045/0.930081/0.983659`、`same_param_mlp_classifier` `0.936542/0.936585/0.949355`，也低于 `final_aux_stacking` / `platt_temperature` `0.954451/0.954472`。原始 equal-sum 为 `0.956086/0.956098/0.987372`。
- CUE flip audit 为 W2C `8`、C2W `29`，不是净正收益。
- Oracle val utility gate diagnostic F1/Acc/AUC `0.973959/0.973984/0.998773`，说明 counterfactual utility 有强上界信号，但当前 train-only CUE gate 学不到可泛化版本。
- Round9-C D4 `No-Go-for-current-DGL-Aux`：best DGL `round9c_dgl_branch_conflict_drop_aux1p0` F1/Acc/AUC `0.933299/0.933333/0.981650`，低于 `static_aux_weight_2p0_anchor_control` `0.939837/0.939837/0.981407`、`generic_dwa` `0.938210/0.938211/0.980962`、deterministic/same-budget/detached `0.936585/0.936585/0.983765`。
- Best DGL flip audit W2C `15`、C2W `17`；4 个 DGL variants 的 flip net 均为负。

结论：

- Round9 当前作用域闭环，仍无 `Primary-Candidate`，不进入 D5。
- 重要规律 1：utility 不是没有信息，而是“oracle 有信号、train-only gate 泛化失败”。后续若再做 CUE，必须从 utility target 的稳定性、跨 split 校准、正负 utility 归因偏差或 train-time representation coupling 上重新设计，而不是继续调当前 gate。
- 重要规律 2：DGL-style branch-local gradient surgery 没有解决 aux-final 冲突；简单 static aux 2.0 仍是更强控制。这进一步支持 R8-B 的观察：当前有效信号更像辅助监督强度/训练动力学，而不是已经形成 PANDA-specific 新机制。

证据目录：

- `remote_panda_work/repro_logs/round9_cue_d2/seed42/`
- `remote_panda_work/repro_logs/round9c_dgl_aux_d4/seed42/summary/`
- `remote_panda_work/logs/round9c_dgl_aux_d4/`
- `remote_panda_work/code_snapshots/round9c_dgl_aux_patch/`

## 2026-05-29：Round 8 完整闭环与 R8-B D5

目标：

- 接续 R8 队列，把有正向线索的方法推进到当前可验证层级。
- 对所有正式训练继续执行 train/val-only，不导出、不打开、不分析 test。

操作：

- R8-A：运行 formal D4 seed42 5-epoch，显式 `--model_name FTmodel`，强 controls 覆盖 same-budget CE、static aux 2.0、focal/class-balanced、confidence/random/shuffled risk、risk-margin/consistency。
- R8-B：独立登记 static aux 2.0；补跑 `generic_gradnorm`、`generic_dwa` controls；随后运行 D5 seeds 2024/2026，与 seed42 合并成三 seed val 复核。
- R8-C：修正 D3.5 决策理由命名，把“梯度不一致非零”与“完全无梯度”区分开，重跑并同步 summary。
- R8-D：修正同类未来 reason 命名；当前结果不需重跑。
- 安全同步仅保留 manifest、summary、decision、metrics、notes、telemetry 和必要 stdout log；排除 checkpoint、权重、原始数据、大 `.npz` 和逐样本 val/prediction 长表。

结果：

- R8-A formal D4 `No-Go`：best primary `r8a_composite_risk_primary` F1/Acc/AUC `0.926767/0.926829/0.978847`，低于 best strong control `shuffled_risk_control` `0.938207/0.938211/0.980836`。
- R8-B seed42 D4 `Feasible-A`：static aux 2.0 F1/Acc/AUC `0.939837/0.939837/0.981407`，打过 deterministic、random/shuffled label、same-budget、PCGrad/CAGrad/GradNorm/DWA controls。
- R8-B D5 降级为 `D5-Feasible-B-not-stable-enough`：static aux 2.0 三 seed 均高于 deterministic，平均 Macro-F1 delta `+0.004856`；但 seed2026 被 `generic_dwa` 打穿，static aux F1/Acc `0.911679/0.912195`，DWA `0.926826/0.926829`。
- R8-C D3.5 `No-Go`：primary 只在 `1/5` batch 产生非零 final-boundary 梯度，且 low-margin 梯度富集不高于 controls。
- R8-D D3.5 `No-Go`：aux-logit endogenous signal 能到 final boundary，但 high-mismatch 梯度富集没有打过 controls。

结论：

- Round 8 当前作用域全部闭环，仍无 `Primary-Candidate`。
- 重要规律：static aux 2.0 对 deterministic 有跨 seed 正向趋势，但 DWA seed2026 反例说明它更像“辅助监督训练动力学”而不是足够干净的 PANDA-specific 方法贡献。
- R8-A 的 shuffled-risk control 打穿 primary，提示 risk-aware 线的提升主要来自扰动/正则化 artifact。

证据目录：

- `remote_panda_work/repro_logs/round8_r8a_formal_d4/seed42/`
- `remote_panda_work/repro_logs/round8_r8b_static_aux_candidate/seed42/`
- `remote_panda_work/repro_logs/round8_r8b_d5_seed_recheck/summary/`
- `remote_panda_work/repro_logs/round8_r8c_d35_gradient_sanity/seed42/`
- `remote_panda_work/repro_logs/round8_r8d_d35_branch_aux_endogenous_sanity/seed42/`

## 2026-05-28：文档整理与日志同步

目标：

- 精简本地项目文档，合并重复入口，归档历史长文。
- 保留信息保真：先完整快照，再压缩根目录文档。
- 把整理后的实验日志同步到 GitHub 仓库 `CmmmMMM407/PANDA-FUXIAN`。

操作：

- 将整理前根目录 Markdown/JSON/DOCX 原样备份到 `docs/archive/full_snapshots_20260528/root/`。
- 将历史方案文档移动到 `docs/archive/method_rounds/`。
- 将投稿规划、路线和阅读笔记移动到 `docs/archive/planning_and_submission/`。
- 将候选登记表移动到 `docs/archive/registries/`。
- 将 Word 文档移动到 `docs/archive/word_docs/`。
- 将 `project_overview.md`、`current_status.md`、`todo.md`、`experiment_log.md` 重写为入口型短文档。
- 筛选公开安全的 summary、manifest、metrics、notes 和必要 stdout log；排除 checkpoint、权重、原始数据、大 `.npz`、压缩包、DOCX 和含样本正文/图片字段的预测长表。
- 同步到 GitHub 提交 `d94253b`，并确认远端 HEAD 指向该提交。

结果：

- 根目录保留当前入口、报告、manifest 和工具目录。
- 完整旧文档未删除，已进入快照和归档区。
- 敏感信息扫描未发现真实 SSH 连接串或密码落盘；GitHub 同步仓库未跟踪 checkpoint、权重、原始数据、大 `.npz`、压缩包、DOCX 或含样本正文的预测长表。

## 2026-05-28：Round 7 D3.5 与 D4-lite

目标：

- 回应“D2/D3 检验偏浅”的问题，把 Round 7 补到梯度可达性和短训趋势层级。
- 保持 train/val-only，不导出、不打开、不分析 test。

操作：

- 新增并运行 `tools/run_panda_round7_d35_gradient_sanity.py`。
- 新增并运行 `tools/run_panda_round7_d4_lite.py`。
- 证据目录：
  - `remote_panda_work/repro_logs/round7_d35_gradient_sanity/seed42/`
  - `remote_panda_work/repro_logs/round7_d4_lite/seed42/`

结果：

- R7-A `risk_margin` 可触达 final classifier / `h_final`，但与 CE 高度同向；`risk_consistency` 与 CE 冲突。
- R7-B agreement-KD 可触达 final boundary，但 teacher/partition 在 D2/D3 不干净。
- R7-C contrastive path 可触达 `h_final`，但 hard-region 与 all-sample/random controls 不分离。
- R7-D sample-level aux 只走 branch path，不直接触达 final classifier / `h_final`。
- R7-A D4-lite `r7a_composite_risk_lite` F1/Acc/AUC `0.732329/0.739837/0.866367`，优于 deterministic-lite、confidence-only、random risk、shuffled risk controls，标为 `D4-lite Feasible-B trend`。
- R7-D sample aux curriculum 被 static aux 2.0 打穿，标为 `Not-worth-full-D4 for current lite setup`。

结论：

- Round 7 不再停留在浅层 D2/D3，但 D3.5/D4-lite 仍不能替代正式 D4。
- 若继续方法线，优先只考虑 R7-A formal D4，并预注册 static aux 2.0、focal/class-balanced、confidence/random/shuffled risk 等强 controls。

## 2026-05-28：Round 7 D2/D3 Gate-0

目标：

- 完成 Round 7 artifact audit 与 R7-A/B/C/D 的 train/val-only D2/D3 核心机制实验。

结果：

- Artifact audit `PASS`：train/val rows `4926/615`，final logits / branch logits / branch features / margin / domain / uncertainty 等关键字段可用。
- R7-A D2 `Feasible-B`：composite risk val error AUC `0.828231`，best simple control AUC `0.811665`；D3 offline proxy No-Go，F1/Acc `0.918404/0.918699` 低于 original final `0.956086/0.956098`。
- R7-B D2/D3 No-Go for current partition / teacher construction。
- R7-C D2/D3 No-Go for current hard-region memory / frozen memory proxy。
- R7-D D2/D3 No-Go for current branch reliability / aux-weight proxy。

结论：

- 当前没有候选解锁正式 D4。
- R7-A 是唯一值得保留的正向诊断信号，但必须通过训练期 formal D4 才能判断是否有实际价值。

## 2026-05-28：R6 补实验闭环

目标：

- 补完 R6-A、R6-C、R6-D、R6-G、R6-H、R6-J 的误杀风险验证。

结果：

- R6-A D4 seed42 smoke No-Go：best primary `r6a_late_aux_ramp_0p5_to_2p0` F1/Acc `0.938184/0.938211`，低于 static control `static_aux_weight_2p0_anchor_control` 的 `0.939837/0.939837`。
- R6-C seed42 弱正但三 seed offline 复核不稳定，seed2024 负、seed2026 被 calibration/global control 打穿。
- R6-D cross-architecture complementarity No-Go。
- R6-G soft/EMA prototype direct probe No-Go。
- R6-H prompt-response frozen probe No-Go。
- R6-J non-self source mixture direct probe No-Go。

结论：

- Round 6 当前作用域闭环，无 `Primary-Candidate`。
- R5-A 与 R6-A 两轮 smoke 都被 aux/static control 打穿，说明 auxiliary supervision 强度是重要训练动力学线索，但目前不足以构成 PANDA-specific 方法贡献。

## 2026-05-27：验证深度复审

目标：

- 重新审查旧创新候选是否被浅层证据误杀。

结论：

- `D0/D1` 不能判 No-Go。
- `D2/D3` 只否定当前 probe/offline/frozen/proxy 变体。
- `D3.5/D4-lite` 只能提供梯度可达和短训趋势。
- `D4` 才能判当前训练实现 No-Go。
- `D5` 才能支撑稳定性或 Primary-Candidate。

该规则已同步到当前 TODO 和状态文档。

## 2026-05-21 至 2026-05-26：历史索引

完整细节见快照；高层索引如下：

- 2026-05-21：PANDA 官方代码、环境、数据、权重、sanity gate 与 Weibo-21 / Weibo 三 seed 复现启动。
- 2026-05-22：PANDA 复现阶段报告完成。
- 2026-05-23：MMDFND / DAMMFND baseline、per-domain/error/reliability 诊断、CS-PANDA gate 设计与执行。
- 2026-05-24：selector control paths、selector v2 Go/No-Go、seed-recheck、prediction-level repeated-forward variance。
- 2026-05-25：R3/R4 方法线、PRCV 同档方法论文规划与反审。
- 2026-05-26：Round 2/3/4/5 gate、R5-A smoke、远端源码审计、云算力数据盘清理。

## 日志同步规则

同步到 GitHub 的日志应包含：

- `*.md`
- `*summary*.json/csv/md`
- `*manifest*.json`
- `*metrics.json`
- 必要 stdout `*.log`

默认排除：

- checkpoint、权重、原始数据集、`.npz`、压缩包。
- `*predictions*.csv`、`*extended_predictions*`、`*matched_inputs*`、`*high_confidence_errors*`、`*features*` 等可能包含样本正文或大规模逐样本内容的长表。
- 服务器密码、token、私钥、完整 SSH 连接串。
